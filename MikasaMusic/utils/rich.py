"""Optional Telegram Rich Message sender with a normal-message fallback.

Pyrofork does not expose every new Bot API type yet, so this module talks to
sendRichMessage directly and lets callers keep the existing Pyrogram path when
Telegram rejects an unsupported rich payload or an older client/API gateway.
"""

import aiohttp
import config


def _button_to_dict(button):
    data = {"text": button.text}
    if getattr(button, "url", None):
        data["url"] = button.url
    elif getattr(button, "callback_data", None):
        data["callback_data"] = button.callback_data
    elif getattr(button, "user_id", None):
        data["url"] = f"tg://user?id={button.user_id}"
    else:
        return None
    return data


def _markup_to_dict(markup):
    if markup is None:
        return None
    rows = []
    for row in getattr(markup, "inline_keyboard", []) or []:
        converted = [_button_to_dict(button) for button in row]
        converted = [button for button in converted if button]
        if converted:
            rows.append(converted)
    return {"inline_keyboard": rows} if rows else None


async def send_rich_message(chat_id, html, reply_markup=None, reply_to_message_id=None):
    """Send a Rich HTML card and return the Bot API response, or None on failure."""
    payload = {
        "chat_id": chat_id,
        "rich_message": {"html": html},
    }
    markup = _markup_to_dict(reply_markup)
    if markup:
        payload["reply_markup"] = markup
    if reply_to_message_id:
        payload["reply_parameters"] = {"message_id": reply_to_message_id}

    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendRichMessage"
    timeout = aiohttp.ClientTimeout(total=12)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    return None
                body = await response.json()
                return body if body.get("ok") else None
    except Exception:
        return None


def start_rich_html(caption, image_url=None):
    """Wrap the existing styled copy in a structured, client-friendly card."""
    media = f'<img src="{image_url}"/>' if image_url else ""
    return (
        f"{media}<h2>🎶 Mɪᴋᴀsᴀ Mᴜsɪᴄ</h2>"
        f"<blockquote>{caption}</blockquote>"
        "<hr/><p>🎧 <b>Fast, smooth music for Telegram voice chats.</b></p>"
    )
