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

from pyrogram.types import InlineKeyboardButton


def setting_markup(_):
    buttons = [
        [
            styled_button(text=_["ST_B_1"], callback_data="AU"),
            styled_button(text=_["ST_B_3"], callback_data="LG"),
        ],
        [
            styled_button(text=_["ST_B_2"], callback_data="PM"),
        ],
        [
            styled_button(text=_["ST_B_4"], callback_data="VM"),
        ],
        [
            styled_button(text=_["CLOSE_BUTTON"], callback_data="close"),
        ],
    ]
    return buttons


def vote_mode_markup(_, current, mode: Union[bool, str] = None):
    buttons = [
        [
            styled_button(text="Vᴏᴛɪɴɢ ᴍᴏᴅᴇ ➜", callback_data="VOTEANSWER"),
            styled_button(
                text=_["ST_B_5"] if mode == True else _["ST_B_6"],
                callback_data="VOMODECHANGE",
            ),
        ],
        [
            styled_button(text="-2", callback_data="FERRARIUDTI M"),
            styled_button(
                text=f"ᴄᴜʀʀᴇɴᴛ : {current}",
                callback_data="ANSWERVOMODE",
            ),
            styled_button(text="+2", callback_data="FERRARIUDTI A"),
        ],
        [
            styled_button(
                text=_["BACK_BUTTON"],
                callback_data="settings_helper",
            ),
            styled_button(text=_["CLOSE_BUTTON"], callback_data="close"),
        ],
    ]
    return buttons


def auth_users_markup(_, status: Union[bool, str] = None):
    buttons = [
        [
            styled_button(text=_["ST_B_7"], callback_data="AUTHANSWER"),
            styled_button(
                text=_["ST_B_8"] if status == True else _["ST_B_9"],
                callback_data="AUTH",
            ),
        ],
        [
            styled_button(text=_["ST_B_1"], callback_data="AUTHLIST"),
        ],
        [
            styled_button(
                text=_["BACK_BUTTON"],
                callback_data="settings_helper",
            ),
            styled_button(text=_["CLOSE_BUTTON"], callback_data="close"),
        ],
    ]
    return buttons


def playmode_users_markup(
    _,
    Direct: Union[bool, str] = None,
    Group: Union[bool, str] = None,
    Playtype: Union[bool, str] = None,
):
    buttons = [
        [
            styled_button(text=_["ST_B_10"], callback_data="SEARCHANSWER"),
            styled_button(
                text=_["ST_B_11"] if Direct == True else _["ST_B_12"],
                callback_data="MODECHANGE",
            ),
        ],
        [
            styled_button(text=_["ST_B_13"], callback_data="AUTHANSWER"),
            styled_button(
                text=_["ST_B_8"] if Group == True else _["ST_B_9"],
                callback_data="CHANNELMODECHANGE",
            ),
        ],
        [
            styled_button(text=_["ST_B_14"], callback_data="PLAYTYPEANSWER"),
            styled_button(
                text=_["ST_B_8"] if Playtype == True else _["ST_B_9"],
                callback_data="PLAYTYPECHANGE",
            ),
        ],
        [
            styled_button(
                text=_["BACK_BUTTON"],
                callback_data="settings_helper",
            ),
            styled_button(text=_["CLOSE_BUTTON"], callback_data="close"),
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
