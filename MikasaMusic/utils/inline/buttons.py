"""Small UI helpers for consistently styled Telegram inline buttons.

Telegram Bot API 9.4 added the ``style`` field with primary/success/danger
values. Older Pyrogram/Pyrofork releases do not serialize that field yet, so
this helper gracefully falls back to a normal button until the runtime is
upgraded.
"""

import inspect

from pyrogram.types import InlineKeyboardButton


_STYLE_SUPPORT = "style" in inspect.signature(InlineKeyboardButton).parameters


def styled_button(text, *, style=None, **kwargs):
    """Build an inline button and pass ``style`` only when the client supports it."""
    if style and _STYLE_SUPPORT:
        kwargs["style"] = style
    return InlineKeyboardButton(text=text, **kwargs)
