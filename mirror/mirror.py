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
from .session import AbruptSession, ReplyType, Session

from aiogram.filters.callback_data import CallbackData


class NoAvailableClientError(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "No Available Client Error"


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
        callback_data.data = callback_data.data.replace("^^^", ":")
        session, info = await self.get_current_session(user_id)

        if (session is not None) and (info.session_id == callback_data.session_id):
            self.clear_session_timeout(session)
            await session.press_button(callback_data.message_id, callback_data.data)
            return True
        
        return False

    async def U2S_send_message(self, user_id: int, text: str):
        session, info = await self.get_current_session(user_id)

        if session is not None:
            await self.close_session(session, info)

        session = await self.new_session(user_id)

        if session is None:
            raise NoAvailableClientError()
        
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

        try:  
            message_id = info.c2u_messages.pop(reply.id)
            await self.bot.delete_message(chat_id=info.user_id, message_id=message_id)
        except KeyError:
            pass

    async def new_session(self, user_id: int) -> Session|None:
        client = self.clients_service.get(user_id)

        if client is None:
            return None
    
        session = Session(client, self.config.bot_link)
        self.sessions[session] = SessionInfo(user_id)
        await session.start()
        return session
    
    async def close_session(self, session: Session, info: SessionInfo):
        await session.stop()
        requests_balance, client_string = await self.get_requests_balance(session.client)
        self.clients_service.give(session.client.name, client_string, requests_balance)
        del self.sessions[session]
    
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
                    await self.close_session(session, info)

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

    async def get_requests_balance(self, client: Client) -> tuple[int, str]:
        abrupt_session = AbruptSession(client, self.config.bot_link)
        await abrupt_session.start()
        await abrupt_session.send_message("/account")
        account_message = (await abrupt_session.get_answer(1))[0][1]

        requests_balance = self.parse_account_message(account_message.text)
        client_string = await abrupt_session.stop()

        return requests_balance, client_string

    def parse_account_message(self, message: str):
        for phrase in message.split("\n"):
            if phrase.__contains__("Лимит запросов в сутки"):
                was, total = phrase.strip().split(":")[1].strip().split("/")
                return int(total) - int(was)
            
        raise Exception("Ошибка в парсинге сообщения с остатками")
        
