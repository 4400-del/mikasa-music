import asyncio
import base64
import os
import re
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
        return await _download_with_ytdlp(link, video=False)
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

    return await asyncio.to_thread(fetch)


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
