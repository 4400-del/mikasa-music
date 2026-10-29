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


from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def stats_buttons(_, status):
    not_sudo = [
        styled_button(
            text=_["SA_B_1"],
            callback_data="TopOverall",
        )
    ]
    sudo = [
        styled_button(
            text=_["SA_B_2"],
            callback_data="bot_stats_sudo",
        ),
        styled_button(
            text=_["SA_B_3"],
            callback_data="TopOverall",
        ),
    ]
    upl = InlineKeyboardMarkup(
        [
            sudo if status else not_sudo,
            [
                styled_button(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                ),
            ],
        ]
    )
    return upl


def back_stats_buttons(_):
    upl = InlineKeyboardMarkup(
        [
            [
                styled_button(
                    text=_["BACK_BUTTON"],
                    callback_data="stats_back",
                ),
                styled_button(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                ),
            ],
        ]
    )
    return upl


# ©️ Copyright Reserved - @MIKASA MUSIC  MIKASA MUSIC

# ===========================================
# ©️ 2025 MIKASA MUSIC (aka @MIKASA MUSIC)
# 🔗 GitHub : https://github.com/YOUR_GITHUB_USERNAME/MikasaMusic
# 📢 Telegram Channel : https://t.me/YOUR_SUPPORT_CHANNEL
# ===========================================


# ❤️ Love From MIKASA MUSIC 
