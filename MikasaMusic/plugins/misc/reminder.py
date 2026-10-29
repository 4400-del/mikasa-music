"""Periodic music reminders for served chats.

This module only uses the bot client and the existing served-chat registry. It
never reads or changes assistant string sessions.
"""

import asyncio
import random

from pyrogram.errors import FloodWait

from MikasaMusic import app
from MikasaMusic.utils.database import get_served_chats


REMINDER_INTERVAL = 3 * 60 * 60
REMINDER_MESSAGES = (
    "🎶 <b>ᴍᴜsɪᴄ ʙʀᴇᴀᴋ</b>\n\nᴛɪʀᴇᴅ ᴏғ ʙᴏʀɪɴɢ sɪʟᴇɴᴄᴇ? ᴘʟᴀʏ ᴀ sᴏɴɢ ᴀɴᴅ ᴇɴᴊᴏʏ ᴛʜᴇ ᴠɪʙᴇ ✨",
    "🎧 <b>ᴠɪʙᴇ ᴄʜᴇᴄᴋ</b>\n\nᴘɪᴄᴋ ᴀ ᴛʀᴀᴄᴋ, ᴊᴏɪɴ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ, ᴀɴᴅ ʟᴇᴛ ᴛʜᴇ ᴍᴜsɪᴄ ᴘʟᴀʏ 🎵",
    "✨ <b>ᴋᴇᴇᴘ ᴛʜᴇ ᴄʜᴀᴛ ᴀʟɪᴠᴇ</b>\n\nᴜsᴇ /play ᴡɪᴛʜ ᴀ sᴏɴɢ ɴᴀᴍᴇ ᴏʀ ʏᴏᴜᴛᴜʙᴇ ʟɪɴᴋ ᴀɴᴅ ᴇɴᴊᴏʏ ᴛʜᴇ ɢʀᴏᴏᴠᴇ 🎶",
)


async def _reminder_loop():
    await asyncio.sleep(REMINDER_INTERVAL)
    while True:
        try:
            message = random.choice(REMINDER_MESSAGES)
            for chat in await get_served_chats():
                try:
                    await app.send_message(int(chat["chat_id"]), message)
                    await asyncio.sleep(0.2)
                except FloodWait as wait:
                    await asyncio.sleep(wait.value)
                except Exception:
                    continue
        except Exception:
            pass
        await asyncio.sleep(REMINDER_INTERVAL)


asyncio.create_task(_reminder_loop())
