from pyrogram.types import InlineKeyboardMarkup
from .buttons import styled_button


def admin_panel_markup():
    return InlineKeyboardMarkup([
        [
            styled_button(text="📢 ᴜsᴇʀ ʙʀᴏᴀᴅᴄᴀsᴛ", callback_data="admin_broadcast_user", style="primary"),
            styled_button(text="👥 ɢʀᴏᴜᴘ ʙʀᴏᴀᴅᴄᴀsᴛ", callback_data="admin_broadcast_chat", style="primary"),
        ],
        [
            styled_button(text="🌐 ᴀʟʟ ᴜsᴇʀs + ɢʀᴏᴜᴘs", callback_data="admin_broadcast_all", style="success"),
            styled_button(text="📊 ʙᴏᴛ sᴛᴀᴛs", callback_data="admin_broadcast_stats", style="success"),
        ],
        [
            styled_button(text="⏱ ʀᴇᴍɪɴᴅᴇʀ sᴇᴛᴛɪɴɢs", callback_data="admin_reminder_info", style="danger"),
        ],
        [
            styled_button(text="✖ ᴄʟᴏsᴇ", callback_data="close", style="danger"),
        ],
    ])


def admin_back_markup():
    return InlineKeyboardMarkup([
        [styled_button(text="🔙 ʙᴀᴄᴋ ᴛᴏ ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ", callback_data="admin_panel", style="primary")],
        [styled_button(text="✖ ᴄʟᴏsᴇ", callback_data="close", style="danger")],
    ])
