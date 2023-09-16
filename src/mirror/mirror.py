import asyncio
from dataclasses import dataclass
import os
import random
import string
import time
from aiogram import Bot
from anyio import sleep
from pyrogram import Client
from pyrogram.types import Message, Photo

from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram.types.input_file import FSInputFile

from config import MirrorConfig
import services
from utils import generate_str

from .pyr_aio_converter import MirrorCallback, PyrogramAiogramConverter
from .session import ReplyType, Session

from aiogram.filters.callback_data import CallbackData


class SessionInfo:
    def __init__(self, user_id: int):
        self.session_id: str = generate_str(10)
        self.user_id: int = user_id
        self.last_time: float = time.time()

        self.c2u_messages: dict[int, int] = {}
        

# def update_last_time(fn):
#     def f(self, *args, **kwargs):
#         fn(self, *args, **kwargs)
#     return f

class Mirror:
    def __init__(self, bot: Bot, clients_service: services.interfaces.Clients, config: MirrorConfig):
        self.bot: Bot = bot
        self.clients_service: services.interfaces.Clients = clients_service
        self.config: MirrorConfig = config

        self.timeout_limit: float = 30

        self.sessions: dict[Session, SessionInfo] = {}

        asyncio.create_task(self.wait_session_timeouts())
        asyncio.create_task(self.collect_session_replyes())

    async def U2S_press_button(self, user_id: int, callback_data: str) -> bool:
        callback_data: MirrorCallback = MirrorCallback.unpack(callback_data)
        session, info = await self.get_current_session(user_id)

        if (session is not None) and (info.session_id == callback_data.session_id):
            self.clear_session_timeout(session)
            await session.press_button(callback_data.message_id, callback_data.data)
            return True
        
        return False

    async def U2S_send_message(self, user_id: int, text: str):
        session, info = await self.get_current_session(user_id)

        if session is None:
            session = await self.new_session(user_id)
        else:
            self.clear_session_timeout(session)

        await session.send_message(text)

    async def S2U_send_message(self, reply: Message, session: Session, info: SessionInfo):
        self.clear_session_timeout(session)

        if reply.photo is not None:
            kwargs, file_name = await PyrogramAiogramConverter.convert_photo_message(reply, info.session_id)
            message = await self.bot.send_photo(info.user_id, **kwargs)
            os.remove(file_name)

        elif reply.document is not None:
            kwargs, file_name = await PyrogramAiogramConverter.convert_document_message(reply, info.session_id)
            message = await self.bot.send_document(info.user_id, **kwargs)
            os.remove(file_name)

        elif reply.location is not None:
            kwargs = await PyrogramAiogramConverter.convert_location_message(reply, info.session_id)
            message = await self.bot.send_location(info.user_id, **kwargs)

        elif reply.text is not None:
            kwargs = await PyrogramAiogramConverter.convert_text_reply(reply, info.session_id)
            message = await self.bot.send_message(info.user_id, disable_web_page_preview=False, **kwargs)

        info.c2u_messages[reply.id] = message.message_id

    async def S2U_edit_message(self, reply: Message, session: Session, info: SessionInfo):
        self.clear_session_timeout(session)

        if reply.text is not None:
            kwargs = await PyrogramAiogramConverter.convert_text_reply(reply, info.session_id)
            message_id = info.c2u_messages[reply.id]
            message = await self.bot.edit_message_text(chat_id=info.user_id, message_id=message_id, **kwargs)
            info.c2u_messages[reply.id] = message.message_id

    async def S2U_delete_message(self, reply: Message, session: Session, info: SessionInfo):
        self.clear_session_timeout(session)
        pass
        # await self.bot.send_message(user_id, "ПРОИЗОШЛО УДАЛЕНИЕ СООБЩЕНИЯ")

    async def new_session(self, user_id: int) -> Session|None:
        client = self.clients_service.get(user_id)

        if client is None:
            return None
    
        session = Session(client, self.config.bot_link)
        self.sessions[session] = SessionInfo(user_id)
        await session.start()
        return session
    
    async def get_current_session(self, user_id: int) -> tuple[Session, SessionInfo]:
        for session, info in self.sessions.items():
            if info.user_id == user_id:
                return session, info
        
        return None, None
    
    async def wait_session_timeouts(self):
        while True:
            for session in list(self.sessions):
                info = self.sessions[session]

                if time.time() - info.last_time >  self.timeout_limit:
        
                    client_string = await session.stop()
                    self.clients_service.give(session.client.name, client_string)

                    del self.sessions[session]
            
            await sleep(0.1)

    async def collect_session_replyes(self):
        while True:
            for session in list(self.sessions):
                info = self.sessions[session]

                if len(session.collected_replyes) > 0:

                    for reply_type, reply in session.collected_replyes:

                        match reply_type:
                            case ReplyType.message:
                                await self.S2U_send_message(reply, session, info)
                            case ReplyType.edit_message:
                                await self.S2U_edit_message(reply, session, info)
                            case ReplyType.delete_message:
                                await self.S2U_delete_message(reply, session, info)

                    session.collected_replyes.clear()
            
            await sleep(0.1) 

    def clear_session_timeout(self, session: Session):
        info = self.sessions[session]
        info.last_time = time.time()
        self.sessions[session] = info

    
#     async def send_messages_group(self, chat_id: int, messages: list[Message]):
#         photo_messages = []

#         for message in messages:

#             if (message.photo is not None):
#                 photo_messages.append(message)
        
#             else:
#                 if len(photo_messages) > 0:
#                     await self.send_media_group(chat_id, photo_messages)

#                 if message.text is not None:
#                     await self.bot.send_message(chat_id, message.text.html, disable_web_page_preview=True)
        
#     async def send_media_group(self, chat_id, messages: list[Message]):
#         file_names = []

#         for message in messages:
#             file_name = f"files/{message.photo.file_id}"
#             await message.download(file_name)
#             file_names.append(file_name)
        
#         media = [InputMediaPhoto(media=FSInputFile(file_name)) for file_name in file_names]
#         await self.bot.send_media_group(chat_id, media)

#         for file_name in file_names:
#             os.remove(file_name)
