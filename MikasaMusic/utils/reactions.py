"""Best-effort animated reactions for incoming bot commands."""

import aiohttp
import config


async def react_to_message(chat_id, message_id, emoji="✨"):
    """Add a big/animated emoji reaction when Telegram permits it."""
    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/setMessageReaction"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reaction": [{"type": "emoji", "emoji": emoji}],
        "is_big": True,
    }
    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as response:
                return response.status == 200
    except Exception:
        return False
