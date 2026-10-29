from MikasaMusic.utils.inline.buttons import styled_button
# Copyright (c) 2025 MIKASA MUSIC <MIKASA MUSIC>
# Location: Supaul, Bihar
#
# All rights reserved.
#
# This code is the intellectual property of MIKASA MUSIC.
# You are not allowed to copy, modify, redistribute, or use this
# code for commercial or personal projects without explicit permission.
#
# Allowed:
# - Forking for personal learning
# - Submitting improvements via pull requests
#
# Not Allowed:
# - Claiming this code as your own
# - Re-uploading without credit or permission
# - Selling or using commercially
#
# Contact for permissions:
# Email: YOUR_EMAIL@example.com


from typing import Union

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def queue_markup(
    _,
    DURATION,
    CPLAY,
    videoid,
    played: Union[bool, int] = None,
    dur: Union[bool, int] = None,
):
    not_dur = [
        [
            styled_button(
                text=_["QU_B_1"],
                callback_data=f"GetQueued {CPLAY}|{videoid}",
            ),
            styled_button(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
            ),
        ]
    ]
    dur = [
        [
            styled_button(
                text=_["QU_B_2"].format(played, dur),
                callback_data="GetTimer",
            )
        ],
        [
            styled_button(
                text=_["QU_B_1"],
                callback_data=f"GetQueued {CPLAY}|{videoid}",
            ),
            styled_button(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
            ),
        ],
    ]
    upl = InlineKeyboardMarkup(not_dur if DURATION == "Unknown" else dur)
    return upl


def queue_back_markup(_, CPLAY):
    upl = InlineKeyboardMarkup(
        [
            [
                styled_button(
                    text=_["BACK_BUTTON"],
                    callback_data=f"queue_back_timer {CPLAY}",
                ),
                styled_button(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                ),
            ]
        ]
    )
    return upl


def aq_markup(_, chat_id):
    buttons = [
        [
            styled_button(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
            ),
        ],
    ]
    return buttons


# ©️ Copyright Reserved - @MIKASA MUSIC  MIKASA MUSIC

# ===========================================
# ©️ 2025 MIKASA MUSIC (aka @MIKASA MUSIC)
# 🔗 GitHub : https://github.com/YOUR_GITHUB_USERNAME/MikasaMusic
# 📢 Telegram Channel : https://t.me/YOUR_SUPPORT_CHANNEL
# ===========================================


# ❤️ Love From MIKASA MUSIC 
