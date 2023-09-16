from pyrogram.types import Message
from pyrogram import types as pyrogram_types
from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, Location
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.types.input_file import FSInputFile


class MirrorCallback(CallbackData, prefix="mirror"):
    data: str
    session_id: str
    message_id: int


class PyrogramAiogramConverter:
    @classmethod
    async def convert_text_reply(cls, message: Message, session_id: str) -> dict:
        kwargs = {"text":  message.text.html}

        if message.reply_markup is not None:
            if type(message.reply_markup) == pyrogram_types.InlineKeyboardMarkup:
                kwargs['reply_markup'] = cls.convert_inline_keyboard(message.reply_markup.inline_keyboard, message.id, session_id)

        return kwargs
    
    @classmethod
    async def convert_document_message(cls, message: Message, session_id: str) -> tuple[dict, str]:
        file_name = f"files/documents/{message.document.file_name}"
        await message.download(file_name)

        kwargs = {"document":  FSInputFile(file_name)}

        if message.caption is not None:
            kwargs['caption'] = message.caption.html

        if message.reply_markup is not None:
            if type(message.reply_markup) == pyrogram_types.InlineKeyboardMarkup:
                kwargs['reply_markup'] = cls.convert_inline_keyboard(message.reply_markup.inline_keyboard, message.id, session_id)

        return kwargs, file_name
    
    @classmethod
    async def convert_photo_message(cls, message: Message, session_id: str) -> tuple[dict, str]:
        file_name = f"files/photos/{message.photo.file_unique_id}"
        await message.download(file_name)

        kwargs = {"photo":  FSInputFile(file_name)}

        if message.caption is not None:
            kwargs['caption'] = message.caption.html

        if message.reply_markup is not None:
            if type(message.reply_markup) == pyrogram_types.InlineKeyboardMarkup:
                kwargs['reply_markup'] = cls.convert_inline_keyboard(message.reply_markup.inline_keyboard, message.id, session_id)

        return kwargs, file_name
    
    @classmethod
    async def convert_location_message(cls, message: Message, session_id: str) -> tuple[dict, str]:
        kwargs = {"longitude": message.location.longitude, 
                  "latitude": message.location.latitude}

        if message.reply_markup is not None:
            if type(message.reply_markup) == pyrogram_types.InlineKeyboardMarkup:
                kwargs['reply_markup'] = cls.convert_inline_keyboard(message.reply_markup.inline_keyboard, message.id, session_id)

        return kwargs

    @classmethod        
    def convert_inline_keyboard(cls, keyboard, message_id, session_id):
        reply_markup = []

        for row in keyboard:
            row_keys = []

            for key in row:
                print(key.text)
                print(key.callback_data)
                if key.callback_data is None:
                    row_keys.append(InlineKeyboardButton(text=key.text, url=key.url))

                else:
                    if cls.filter_callback_data(key.callback_data):
                        data = MirrorCallback(data=key.callback_data, session_id=session_id, message_id=message_id).pack()
                        row_keys.append(InlineKeyboardButton(text=key.text, url=key.url, callback_data=data))

            if len(row_keys) > 0:
                reply_markup.append(row_keys)
        
        if len(reply_markup) > 0:
            return InlineKeyboardBuilder(reply_markup).as_markup()
        else:
            return None
    
    @staticmethod
    def filter_callback_data(callback_data: str) -> bool:
        for string in [
            "PREMIUM", "REP", "DELETEFULL", "COMMENT"
        ]:
            if callback_data.__contains__(string):
                return False
            
        return True