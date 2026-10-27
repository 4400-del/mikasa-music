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


import aiohttp

BASE = "https://batbin.me/"


async def post(url: str, *args, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, *args, **kwargs) as resp:
            try:
                data = await resp.json()
            except Exception:
                data = await resp.text()
        return data


async def NandBin(text):
    resp = await post(f"{BASE}api/v2/paste", data=text)
    if not resp["success"]:
        return
    link = BASE + resp["message"]
    return link


# ©️ Copyright Reserved - @MIKASA MUSIC  MIKASA MUSIC

# ===========================================
# ©️ 2025 MIKASA MUSIC (aka @MIKASA MUSIC)
# 🔗 GitHub : https://github.com/YOUR_GITHUB_USERNAME/MikasaMusic
# 📢 Telegram Channel : https://t.me/YOUR_SUPPORT_CHANNEL
# ===========================================


# ❤️ Love From MIKASA MUSIC 
