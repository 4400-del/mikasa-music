import pyrogram
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus, ParseMode
from pyrogram.types import InlineKeyboardMarkup

import config
from ..logging import LOGGER


class Nand(Client):
    def __init__(self):
        LOGGER(__name__).info(f"Starting bot...")
        super().__init__(
            name="MikasaMusic",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            parse_mode=ParseMode.HTML,
            max_concurrent_transmissions=7,
        )

    @staticmethod
    async def _apply_styles(message, markup):
        if not message or not markup:
            return
        rows = getattr(markup, "inline_keyboard", markup)
        if not any(getattr(button, "_mikasa_style", None) for row in rows for button in row):
            return
        from MikasaMusic.utils.inline.buttons import apply_button_styles
        await apply_button_styles(message.chat.id, message.id, markup)

    async def send_message(self, *args, **kwargs):
        markup = kwargs.get("reply_markup")
        message = await super().send_message(*args, **kwargs)
        await self._apply_styles(message, markup)
        return message

    async def send_photo(self, *args, **kwargs):
        markup = kwargs.get("reply_markup")
        message = await super().send_photo(*args, **kwargs)
        await self._apply_styles(message, markup)
        return message

    async def send_audio(self, *args, **kwargs):
        markup = kwargs.get("reply_markup")
        message = await super().send_audio(*args, **kwargs)
        await self._apply_styles(message, markup)
        return message

    async def send_video(self, *args, **kwargs):
        markup = kwargs.get("reply_markup")
        message = await super().send_video(*args, **kwargs)
        await self._apply_styles(message, markup)
        return message

    async def edit_message_text(self, *args, **kwargs):
        markup = kwargs.get("reply_markup")
        message = await super().edit_message_text(*args, **kwargs)
        await self._apply_styles(message, markup)
        return message

    async def edit_message_caption(self, *args, **kwargs):
        markup = kwargs.get("reply_markup")
        message = await super().edit_message_caption(*args, **kwargs)
        await self._apply_styles(message, markup)
        return message

    async def edit_message_reply_markup(self, *args, **kwargs):
        markup = kwargs.get("reply_markup")
        message = await super().edit_message_reply_markup(*args, **kwargs)
        await self._apply_styles(message, markup)
        return message

    async def start(self):
        await super().start()
        get_me = await self.get_me()
        self.username = get_me.username
        self.id = get_me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.mention = self.me.mention

        from MikasaMusic.utils.inline.buttons import styled_button
        button = InlineKeyboardMarkup(
            [
                [
                    styled_button(
                        text="Add Me To Your Group",
                        url=f"https://t.me/{self.username}?startgroup=true",
                        style="primary",
                    )
                ]
            ]
        )

        if config.LOG_GROUP_ID:
            try:
                await self.send_photo(
                    config.LOG_GROUP_ID,
                    photo=config.START_IMG_URL,
                    caption=f"<b>🎵 Bot Started Successfully</b>\n\n"
                            f"<b>Name:</b> {self.name}\n"
                            f"<b>Username:</b> @{self.username}\n"
                            f"<b>ID:</b> <code>{self.id}</code>\n\n"
                            f"<i>Bot is now online and ready to serve!</i>",
                    reply_markup=button,
                )
            except pyrogram.errors.ChatWriteForbidden:
                LOGGER(__name__).error("Bot cannot write to the log group")
                try:
                    await self.send_message(
                        config.LOG_GROUP_ID,
                        f"<b>🎵 Bot Started Successfully</b>\n\n"
                        f"<b>Name:</b> {self.name}\n"
                        f"<b>Username:</b> @{self.username}\n"
                        f"<b>ID:</b> <code>{self.id}</code>\n\n"
                        f"<i>Bot is now online and ready to serve!</i>",
                        reply_markup=button,
                    )
                except Exception as e:
                    LOGGER(__name__).error(f"Failed to send message in log group: {e}")
            except Exception as e:
                LOGGER(__name__).error(f"Error while sending to log group: {e}")
        else:
            LOGGER(__name__).warning("LOG_GROUP_ID is not set")

        if config.LOG_GROUP_ID:
            try:
                chat_member_info = await self.get_chat_member(
                    config.LOG_GROUP_ID, self.id
                )
                if chat_member_info.status != ChatMemberStatus.ADMINISTRATOR:
                    LOGGER(__name__).error("Please promote Bot as Admin in Logger Group")
            except Exception as e:
                LOGGER(__name__).error(f"Error checking bot status: {e}")

        LOGGER(__name__).info(f"Music Bot Started as {self.name}")

    async def stop(self):
        await super().stop()
