"""Centralized Telegram inline-button styling.

Telegram Bot API 9.4 supports primary/success/danger button styles. The
runtime currently may use an older Pyrofork serializer, so the helper passes
style only when the installed client accepts it and otherwise falls back to a
normal button without breaking the bot.
"""

import inspect

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
    return InlineKeyboardButton(text=text, *positional, **kwargs)
