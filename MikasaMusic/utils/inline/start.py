# Copyright (c) 2025 MIKASA MUSIC <MIKASA MUSIC>

from pyrogram.types import InlineKeyboardMarkup
import config
from MikasaMusic import app
from .buttons import styled_button


def start_panel(_):
    return [
        [
            styled_button(text=_["S_B_1"], url=f"https://t.me/{app.username}?startgroup=true", style="success"),
            styled_button(text=_["S_B_2"], url=config.SUPPORT_GROUP, style="primary"),
        ],
        [
            styled_button(text=_["S_B_5"], user_id=config.OWNER_ID, style="success"),
            styled_button(text=_["S_B_4"], callback_data="help_page_1", style="success"),
        ],
    ]


def private_panel(_):
    return [
        [
            styled_button(text=_["S_B_3"], url=f"https://t.me/{app.username}?startgroup=true", style="success"),
        ],
        [
            styled_button(text=_["S_B_2"], url=config.SUPPORT_GROUP, style="primary"),
            styled_button(text=_["S_B_6"], url=config.SUPPORT_CHANNEL, style="primary"),
        ],
        [
            styled_button(text=_["S_H_4"], url=config.DONATE, style="danger"),
            styled_button(text=_["S_B_5"], user_id=config.OWNER_ID, style="danger"),
        ],
        [
            styled_button(text=_["S_B_4"], callback_data="help_page_1", style="primary"),
        ],
        [
            styled_button(text="🛠 ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ", callback_data="admin_panel", style="danger"),
        ],
    ]


def about_panel(_):
    return [
        [
            styled_button(text=_["S_B_6"], url=config.SUPPORT_CHANNEL, style="primary"),
            styled_button(text=_["S_B_2"], url=config.SUPPORT_GROUP, style="primary"),
        ],
        [
            styled_button(text=_["BACK_BUTTON"], callback_data="settingsback_helper", style="danger"),
        ],
    ]


def owner_panel(_):
    return [
        [
            styled_button(text=_["S_H_1"], url=config.INSTAGRAM, style="primary"),
            styled_button(text=_["S_H_2"], url=config.YOUTUBE, style="primary"),
        ],
        [
            styled_button(text=_["S_H_3"], url=config.GITHUB, style="success"),
            styled_button(text=_["S_H_4"], url=config.DONATE, style="success"),
        ],
        [
            styled_button(text=_["BACK_BUTTON"], callback_data="settingsback_helper", style="danger"),
        ],
    ]
