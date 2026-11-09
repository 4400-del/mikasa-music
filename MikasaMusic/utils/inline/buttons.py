"""Centralized Telegram inline-button styling.

Telegram Bot API 9.4 supports primary/success/danger button styles. The
runtime currently may use an older Pyrofork serializer, so the helper passes
style only when the installed client accepts it and otherwise falls back to a
normal button without breaking the bot.
"""

import inspect
import aiohttp
import config

from pyrogram.types import InlineKeyboardButton


_STYLE_SUPPORT = "style" in inspect.signature(InlineKeyboardButton).parameters
_DANGER_WORDS = ("close", "back", "cancel", "stop", "delete", "remove", "ban", "danger", "off", "reject")
_SUCCESS_WORDS = ("add", "start", "play", "resume", "support", "subscribe", "enable", "yes", "confirm", "next", "join")


def _pick_style(text, callback_data=None):
    value = f"{text or ''} {callback_data or ''}".lower()
    if any(word in value for word in _DANGER_WORDS):
        return "danger"
    if any(word in value for word in _SUCCESS_WORDS):
        return "success"
    return "primary"


def styled_button(*args, style=None, **kwargs):
    """Build a button with a deterministic style and backwards compatibility."""
    if args:
        text = args[0]
        positional = args[1:]
    else:
        text = kwargs.pop("text")
        positional = ()

    style = style or _pick_style(text, kwargs.get("callback_data"))
    if _STYLE_SUPPORT:
        return InlineKeyboardButton(text=text, *positional, style=style, **kwargs)
    button = InlineKeyboardButton(text=text, *positional, **kwargs)
    # Pyrofork currently drops Bot API 9.4's style field. Keep it on the
    # object so the HTTP markup patcher can apply the real style afterwards.
    button._mikasa_style = style
    return button


def _button_payload(button):
    data = {"text": button.text}
    style = getattr(button, "_mikasa_style", None)
    if style:
        data["style"] = style
    for key in (
        "callback_data", "url", "switch_inline_query",
        "switch_inline_query_current_chat",
    ):
        value = getattr(button, key, None)
        if value is not None:
            data[key] = value.decode() if isinstance(value, bytes) else value
            break
    return data


async def apply_button_styles(chat_id, message_id, markup):
    """Apply Bot API 9.4 styles after Pyrofork sends the message."""
    if not markup or not config.BOT_TOKEN:
        return False
    rows = getattr(markup, "inline_keyboard", markup)
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reply_markup": {
            "inline_keyboard": [[_button_payload(button) for button in row] for row in rows]
        },
    }
    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/editMessageReplyMarkup"
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as response:
                return response.status == 200
    except Exception:
        return False
