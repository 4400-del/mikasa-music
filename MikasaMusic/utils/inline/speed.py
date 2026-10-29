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


def speed_markup(_, chat_id):
    upl = InlineKeyboardMarkup(
        [
            [
                styled_button(
                    text="🕒 0.5x",
                    callback_data=f"SpeedUP {chat_id}|0.5",
                ),
                styled_button(
                    text="🕓 0.75x",
                    callback_data=f"SpeedUP {chat_id}|0.75",
                ),
            ],
            [
                styled_button(
                    text=_["P_B_4"],
                    callback_data=f"SpeedUP {chat_id}|1.0",
                ),
            ],
            [
                styled_button(
                    text="🕤 1.5x",
                    callback_data=f"SpeedUP {chat_id}|1.5",
                ),
                styled_button(
                    text="🕛 2.0x",
                    callback_data=f"SpeedUP {chat_id}|2.0",
                ),
            ],
            [
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
