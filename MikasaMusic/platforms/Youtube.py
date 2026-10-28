import asyncio
import base64
import os
import re
import subprocess
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


def _prepare_cookie_file():
    encoded = os.environ.get("YOUTUBE_COOKIES_B64")
    if not encoded:
        return None
    try:
        with open(COOKIE_FILE, "wb") as cookie_file:
            cookie_file.write(base64.b64decode(encoded))
        return COOKIE_FILE
    except Exception as error:
        LOGGER(__name__).error(f"Could not prepare YouTube cookies: {error}")
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
        downloaded = await _download_with_invidious(link)
        if downloaded:
            return downloaded
    except Exception as e:
        LOGGER(__name__).warning(f"Invidious audio failed, trying yt-dlp: {e}")
    try:
        downloaded = await _download_with_ytdlp(link, video=False)
        if downloaded:
            return downloaded
    except Exception as e:
        LOGGER(__name__).error(f"Audio download failed: {e}")
    return None


async def download_video(link: str) -> str:
    try:
        return await _download_with_ytdlp(link, video=True)
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
        return await _invidious_track(link)
    except Exception as error:
        LOGGER(__name__).warning(f"Invidious metadata failed, trying yt-dlp: {error}")
        return await asyncio.to_thread(fetch)


async def _invidious_json(path):
    def request_json():
        import requests
        last_error = None
        for instance in INVIDIOUS_INSTANCES:
            try:
                response = requests.get(instance + path, timeout=20)
                response.raise_for_status()
                return response.json(), instance
            except Exception as error:
                last_error = error
        raise RuntimeError(f"All Invidious instances failed: {last_error}")

    return await asyncio.to_thread(request_json)


async def _invidious_track(link: str):
    video_match = re.search(r"(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{6,})", link)
    if video_match:
        info, _ = await _invidious_json(f"/api/v1/videos/{video_match.group(1)}?local=1")
        return info
    from urllib.parse import quote
    results, _ = await _invidious_json(
        f"/api/v1/search?q={quote(link)}&type=video"
    )
    if not results:
        raise ValueError("No YouTube result found")
    result = results[0]
    return {
        "id": result["videoId"],
        "title": result.get("title"),
        "duration": result.get("lengthSeconds"),
        "thumbnail": (result.get("videoThumbnails") or [{}])[0].get("url"),
        "webpage_url": f"https://www.youtube.com/watch?v={result['videoId']}",
    }


async def _download_with_invidious(link: str) -> str:
    try:
        info = await _invidious_track(link)
        audio = [
            item for item in info.get("adaptiveFormats", [])
            if item.get("type", "").startswith("audio/") and item.get("url")
        ]
        if not audio:
            return None
        # Prefer a small, stable audio stream on Render's free instance.
        # High-bitrate streams make the initial download slow and can starve playback.
        audio.sort(
            key=lambda item: (
                0 if int(item.get("bitrate", 0) or 0) <= 80000 else 1,
                abs(int(item.get("bitrate", 0) or 0) - 64000),
            )
        )
        # The Invidious URL is already proxied. Passing it directly to
        # PyTgCalls avoids waiting for the complete MP3 download first.
        return audio[0]["url"]
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
