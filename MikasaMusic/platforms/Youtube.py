import asyncio
import base64
import os
import re
import subprocess
import time
from typing import Union
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch, Playlist
from MikasaMusic.utils.formatters import time_to_seconds
import aiohttp
from MikasaMusic import LOGGER

DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
COOKIE_FILE = "/tmp/mikasa_youtube_cookies.txt"
INVIDIOUS_INSTANCES = [
    "https://yt.chocolatemoo53.com",
    "https://inv.nadeko.net",
]
_TRACK_CACHE = {}
_TRACK_CACHE_TTL = 60
_AUDIO_CACHE = {}
_AUDIO_CACHE_TTL = 45
TRACK_LOOKUP_TIMEOUT = 18
DOWNLOAD_TIMEOUT = 90
DOWNLOAD_ATTEMPT_TIMEOUT = DOWNLOAD_TIMEOUT / 2
YTDLP_HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "Chrome/124.0 Safari/537.36"
    ),
}


def _yt_dlp_network_options():
    return {
        "retries": 2,
        "fragment_retries": 2,
        "socket_timeout": 10,
        "http_headers": YTDLP_HTTP_HEADERS,
        "extractor_args": {
            "youtube": {"player_client": ["android", "web"]},
        },
    }


def _prepare_cookie_file():
    encoded = os.environ.get("YOUTUBE_COOKIES_B64")
    if not encoded:
        return None
    try:
        cookie_data = base64.b64decode(encoded, validate=True)
        with open(COOKIE_FILE, "wb") as cookie_file:
            cookie_file.write(cookie_data)
        return COOKIE_FILE
    except Exception as error:
        LOGGER(__name__).warning(
            f"Ignoring invalid YOUTUBE_COOKIES_B64; continuing without cookies: {error}"
        )
        return None


async def _download_with_ytdlp(link: str, video: bool = False) -> str:
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    options = {
        "format": "bestvideo+bestaudio/best" if video else "bestaudio/best",
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": True,
    }
    options.update(_yt_dlp_network_options())
    cookie_file = _prepare_cookie_file()
    if cookie_file:
        options["cookiefile"] = cookie_file
    if video:
        options["merge_output_format"] = "mp4"
    else:
        options["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]

    def fetch():
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(link, download=True)
            return ydl.prepare_filename(info)

    output = await asyncio.to_thread(fetch)
    if not video:
        output = os.path.splitext(output)[0] + ".mp3"
    elif not output.endswith(".mp4"):
        output = os.path.splitext(output)[0] + ".mp4"
    return output if os.path.exists(output) else None


async def download_song(link: str) -> str:
    try:
        downloaded = await asyncio.wait_for(
            _download_with_invidious(link), timeout=DOWNLOAD_ATTEMPT_TIMEOUT
        )
        if downloaded:
            return downloaded
    except Exception as e:
        LOGGER(__name__).warning(f"Invidious audio failed, trying yt-dlp: {e}")
    try:
        downloaded = await asyncio.wait_for(
            _download_with_ytdlp(link, video=False), timeout=DOWNLOAD_ATTEMPT_TIMEOUT
        )
        if downloaded:
            return downloaded
    except Exception as e:
        LOGGER(__name__).error(f"Audio download failed: {e}")
    return None


async def download_video(link: str) -> str:
    try:
        return await asyncio.wait_for(
            _download_with_ytdlp(link, video=True), timeout=DOWNLOAD_TIMEOUT
        )
    except Exception as e:
        LOGGER(__name__).error(f"Video download failed: {e}")
        return None


async def _extract_track(link: str):
    """Resolve a YouTube URL or search phrase through yt-dlp."""
    query = link.strip()
    if not re.match(r"https?://", query):
        query = f"ytsearch1:{query}"
    options = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "skip_download": True,
    }
    options.update(_yt_dlp_network_options())
    cookie_file = _prepare_cookie_file()
    if cookie_file:
        options["cookiefile"] = cookie_file

    def fetch():
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(query, download=False)
            if info and info.get("_type") == "playlist":
                return next((entry for entry in (info.get("entries") or []) if entry), None)
            return info

    try:
        # Use native YouTube extraction first. Invidious search/video responses
        # are intermittently unavailable from Render and can return stale data.
        info = await asyncio.wait_for(
            asyncio.to_thread(fetch), timeout=TRACK_LOOKUP_TIMEOUT * 0.65
        )
        if info and info.get("id"):
            return info
        raise RuntimeError("yt-dlp returned no track")
    except Exception as error:
        LOGGER(__name__).warning(f"yt-dlp metadata failed, trying Invidious: {error}")
        try:
            return await asyncio.wait_for(
                _invidious_track(link), timeout=TRACK_LOOKUP_TIMEOUT * 0.35
            )
        except Exception as fallback_error:
            LOGGER(__name__).error(
                f"Track details lookup failed after timeout: {fallback_error}"
            )
            raise RuntimeError("Track details could not be fetched in time") from fallback_error


async def _invidious_json(path):
    def request_json(instance):
        import requests
        response = requests.get(instance + path, timeout=(4, 8))
        response.raise_for_status()
        return response.json(), instance

    tasks = [asyncio.create_task(asyncio.to_thread(request_json, instance)) for instance in INVIDIOUS_INSTANCES]
    errors = []
    try:
        for task in asyncio.as_completed(tasks):
            try:
                return await task
            except Exception as error:
                errors.append(error)
    finally:
        pending_tasks = [task for task in tasks if not task.done()]
        for task in pending_tasks:
            task.cancel()
        if pending_tasks:
            await asyncio.gather(*pending_tasks, return_exceptions=True)
    raise RuntimeError(f"All Invidious instances failed: {errors[-1] if errors else 'unknown error'}")


async def _invidious_track(link: str):
    cache_key = link.strip()
    cached = _TRACK_CACHE.get(cache_key)
    if cached and time.monotonic() - cached[0] < _TRACK_CACHE_TTL:
        return cached[1]
    video_match = re.search(r"(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{6,})", link)
    if video_match:
        info, _ = await _invidious_json(f"/api/v1/videos/{video_match.group(1)}?local=1")
        _TRACK_CACHE[cache_key] = (time.monotonic(), info)
        return info
    from urllib.parse import quote
    results, _ = await _invidious_json(
        f"/api/v1/search?q={quote(link)}&type=video"
    )
    if not results:
        raise ValueError("No YouTube result found")
    result = results[0]
    info = {
        "id": result["videoId"],
        "title": result.get("title"),
        "duration": result.get("lengthSeconds"),
        "thumbnail": (result.get("videoThumbnails") or [{}])[0].get("url"),
        "webpage_url": f"https://www.youtube.com/watch?v={result['videoId']}",
    }
    _TRACK_CACHE[cache_key] = (time.monotonic(), info)
    return info


def _select_audio_format(info):
    audio = [
        item for item in info.get("adaptiveFormats", [])
        if item.get("type", "").startswith("audio/") and item.get("url")
    ]
    if not audio:
        return None
    audio.sort(
        key=lambda item: (
            0 if int(item.get("bitrate", 0) or 0) <= 80000 else 1,
            abs(int(item.get("bitrate", 0) or 0) - 64000),
        )
    )
    return audio[0]


async def _invidious_audio_url(link: str) -> str:
    info = await _invidious_track(link)
    selected = _select_audio_format(info)
    return selected.get("url") if selected else None


async def _download_with_invidious(link: str) -> str:
    try:
        info = await asyncio.wait_for(
            _invidious_track(link), timeout=TRACK_LOOKUP_TIMEOUT / 2
        )
        selected = _select_audio_format(info)
        if not selected:
            return None
        # Prefer a small, stable audio stream on Render's free instance.
        # High-bitrate streams make the initial download slow and can starve playback.
        audio_url = selected["url"]
        output_dir = os.path.join(os.getcwd(), "downloads")
        os.makedirs(output_dir, exist_ok=True)
        video_id = info["videoId"] if info.get("videoId") else info["id"]
        source = os.path.join(output_dir, f"{video_id}.m4a")
        target = os.path.join(output_dir, f"{video_id}.mp3")

        def fetch_audio():
            import requests
            with requests.get(audio_url, stream=True, timeout=(10, 20)) as response:
                response.raise_for_status()
                with open(source, "wb") as output:
                    for chunk in response.iter_content(1024 * 64):
                        if chunk:
                            output.write(chunk)

        await asyncio.wait_for(asyncio.to_thread(fetch_audio), timeout=90)
        await asyncio.wait_for(
            asyncio.to_thread(
                subprocess.run,
                ["ffmpeg", "-y", "-loglevel", "error", "-i", source, "-vn", "-codec:a", "libmp3lame", "-b:a", "96k", "-ar", "48000", target],
                check=True,
            ),
            timeout=30,
        )
        return target if os.path.exists(target) and os.path.getsize(target) else None
    except Exception as error:
        LOGGER(__name__).error(f"Invidious audio fallback failed: {error}")
        return None


def _format_duration(seconds):
    if not seconds:
        return None
    seconds = int(seconds)
    return f"{seconds // 60}:{seconds % 60:02d}"


def _track_details(info):
    if not info or not info.get("id"):
        raise ValueError("No YouTube result found")
    return {
        "title": info.get("title") or "Unknown title",
        "link": info.get("webpage_url") or f"https://www.youtube.com/watch?v={info['id']}",
        "vidid": info["id"],
        "duration_min": _format_duration(info.get("duration")),
        "thumb": info.get("thumbnail") or "",
    }


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        return text[entity.offset: entity.offset + entity.length]
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        info = await _extract_track(link)
        details = _track_details(info)
        duration_sec = int(info.get("duration") or 0)
        return details["title"], details["duration_min"], duration_sec, details["thumb"], details["vidid"]

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["title"]

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["duration"]

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["thumbnails"][0]["url"].split("?")[0]

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            downloaded_file = await download_video(link)
            if downloaded_file:
                return 1, downloaded_file
            else:
                return 0, "Video download failed"
        except Exception as e:
            return 0, f"Video download error: {e}"

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            plist = await Playlist.get(link)
        except:
            return []

        videos = plist.get("videos") or []
        ids = []
        for data in videos[:limit]:
            if not data:
                continue
            vid = data.get("id")
            if not vid:
                continue
            ids.append(vid)
        return ids

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        info = await _extract_track(link)
        track_details = _track_details(info)
        return track_details, track_details["vidid"]

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        ytdl_opts = {"quiet": True}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    if "dash" not in str(format["format"]).lower():
                        formats_available.append(
                            {
                                "format": format["format"],
                                "filesize": format.get("filesize"),
                                "format_id": format["format_id"],
                                "ext": format["ext"],
                                "format_note": format["format_note"],
                                "yturl": link,
                            }
                        )
                except:
                    continue
        return formats_available, link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            link = self.base + link

        try:
            if video:
                downloaded_file = await download_video(link)
            else:
                downloaded_file = await download_song(link)

            if downloaded_file:
                return downloaded_file, True
            else:
                return None, False
        except Exception:
            return None, False

    async def stream_url(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        cached = _AUDIO_CACHE.get(link)
        if cached and time.monotonic() - cached[0] < _AUDIO_CACHE_TTL:
            return cached[1]
        # Do not pass Invidious' proxied videoplayback URLs to PyTgCalls.
        # Those URLs frequently return a valid-looking response but PyTgCalls
        # rejects them with "No audio source found". Resolve a native YouTube
        # audio URL with yt-dlp instead; Invidious remains available for metadata.

        def resolve_with_ytdlp():
            options = {
                "format": "bestaudio/best",
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "skip_download": True,
            }
            options.update(_yt_dlp_network_options())
            cookie_file = _prepare_cookie_file()
            if cookie_file:
                options["cookiefile"] = cookie_file
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(link, download=False)
                return info.get("url")

        try:
            audio_url = await asyncio.wait_for(asyncio.to_thread(resolve_with_ytdlp), timeout=12)
            if audio_url:
                _AUDIO_CACHE[link] = (time.monotonic(), audio_url)
                return audio_url
        except Exception as error:
            LOGGER(__name__).warning(f"yt-dlp direct audio failed: {error}")
        return None
