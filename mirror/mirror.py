import asyncio
from dataclasses import dataclass
import os
import random
import string
import time
from aiogram import Bot
from anyio import sleep
from pyrogram import Client
from pyrogram.types import Message

from collections import deque as Queue

from config import MirrorConfig
import services
import repositories
from utils import generate_str

from .pyr_aio_converter import MirrorCallback, PyrogramAiogramConverter
from .session import AbruptSession, ReplyType, Session


class NoAvailableClientError(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "No Available Client Error"


class SessionInfo:
    def __init__(self, user_id: int, requests_balance: int):
        self.session_id: str = generate_str(10)
        self.user_id: int = user_id
        self.is_available: bool = True
        self.last_time: float = time.time()
        self.start_requests_balance: int = requests_balance

        self.c2u_messages: dict[int, int] = {}


@dataclass
class QueuePosition:
    user_id: int
    event: asyncio.Event
    client: Client = None
        

class Mirror:
    def __init__(self, bot: Bot, 
                 clients_service: services.interfaces.Clients,
                 money_service: services.interfaces.Money,
                 config: MirrorConfig):
        
        self.bot: Bot = bot
        self.clients_service: services.interfaces.Clients = clients_service
        self.money_service: services.interfaces.Money = money_service
        self.config: MirrorConfig = config

        self.timeout_limit: float = 30

        self.sessions: dict[Session, SessionInfo] = {}
        self.queue: list[QueuePosition] = list()

        asyncio.create_task(self.wait_session_timeouts())
        asyncio.create_task(self.distribute_clients())
        asyncio.create_task(self.collect_session_replyes())

    async def U2S_press_button(self, user_id: int, callback_data: str) -> bool:
        callback_data: MirrorCallback = MirrorCallback.unpack(callback_data)
        callback_data.data = callback_data.data.replace("^^^", ":")
        session, info = await self.get_current_session(user_id)

        if (session is not None) and (info.session_id == callback_data.session_id):
            self.clear_session_timeout(session)
            
            try:
                await session.press_button(callback_data.message_id, callback_data.data)
                
            except Exception as err:
                print(f"Ошибка: {str(err)}")
                return False

            return True
        
        return False

    async def U2S_send_message(self, user_id: int, text: str, photo: str = None):
        # проверяем баланс на кошельке пользователя
        if not self.money_service.check_money_availability(user_id):
            await self.bot.send_message(user_id, "У вас недостаточно денег на балансе.")
            return
        
        session, info = await self.get_current_session(user_id)
        if session is not None:
            # если сессия locked (уже есть запросы по ней), то говорим клиенту об этом
            if not info.is_available:
                print('Сессия не доступна')
                await self.bot.send_message(user_id, "<b>Подождите. У вас уже есть запросы в обработке.</b>")
                return
            
            # если сессия не locked (уже есть запросы по ней), то обновляем ее и отправляем запрос
            print('Перезапускаем сессию')
            message = await self.bot.send_message(user_id, "<b>Ожидайте, ваш запрос обрабатывается...</b>")
            session = await self.refresh_session(session, info)

            if session is not None:
                await message.delete()
                await session.send_message(text, photo)
                
            return

        # проверяем наличие челика в очереди, если да - шлем нахуй
        if self.check_user_id_in_queue(user_id):
            await self.bot.send_message(user_id, "<b>Подождите. У вас уже есть запросы в обработке.</b>")
            return

        # если нет - ставим в очередь
        print('Ставим запрос в очередь.')
        message = await self.bot.send_message(user_id, "<b>Ожидайте, ваш запрос обрабатывается...</b>")
        queue_position = QueuePosition(user_id=user_id, event=asyncio.Event())
        self.queue.append(queue_position)
        await queue_position.event.wait()
        session, info = await self.get_current_session(user_id)
        await message.delete()
        await session.send_message(text, photo)
        return

           
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

    async def refresh_session(self, session: Session, info: SessionInfo) -> Session:
        # останавливаем и удаляем сессию
        self.sessions[session].is_available = False
        print("Делаем сессию недоступной")
        
        try:
            await session.stop()
        except Exception:
            return

        # платим по счетам
        print("Определяем сколько пользователь потратил")
        requests_balance, client_string = await self.get_requests_balance(session.client)
        if requests_balance != -1:
            spent_requests = info.start_requests_balance - requests_balance
            self.money_service.pay_request(info.user_id, spent_requests)

        # создаем новую сессию
        print("Создаем новую сессию и удаляем старую")
        session.client.session_string = client_string
        new_session = Session(session.client, self.config.bot_link)
        self.sessions[new_session] = SessionInfo(info.user_id, requests_balance)
        del self.sessions[session]
        await new_session.start()

        return new_session 


    async def pay_request(self, session: SessionInfo, info: SessionInfo) -> str:
        requests_balance, client_string = await self.get_requests_balance(session.client)
        if requests_balance != -1:
            spent_requests = info.start_requests_balance - requests_balance
            self.money_service.pay_request(info.user_id, spent_requests)
        
        return client_string

    # async def new_session(self, user_id: int) -> Session:
    #     await self.close_current_session(user_id)
    #     queue_position = QueuePosition(user_id=user_id, event=asyncio.Event())
    #     self.queue.append(queue_position)
    #     await queue_position.event.wait()
    #     return await self.create_session(queue_position.client, user_id)

    async def create_session(self, client: Client, user_id: int) -> Session:
        session = Session(client, self.config.bot_link)
        requests_balance, _ = await self.get_requests_balance(session.client)
        await session.start()
        self.sessions[session] = SessionInfo(user_id, requests_balance)
        return session 
    
    async def close_current_session(self, user_id: int):
        session, info = await self.get_current_session(user_id)
        if session is not None:
            await self.close_session(session, info)

    async def close_session(self, session: Session, info: SessionInfo):
        await session.stop()
        del self.sessions[session]

        requests_balance, client_string = await self.get_requests_balance(session.client)
        spent_requests = info.start_requests_balance - requests_balance
        self.money_service.pay_request(info.user_id, spent_requests)

        self.clients_service.give(session.client.name, client_string, requests_balance)

    async def get_current_session(self, user_id: int) -> tuple[Session, SessionInfo]:
        for session, info in self.sessions.items():
            if info.user_id == user_id:
                return session, info
        
        return None, None

    def check_user_id_in_queue(self, user_id: int) -> bool:
        for queue_position in self.queue:

            if queue_position.user_id == user_id:
                return True
        
        return False
    
    async def distribute_clients(self):
        while True:
            if len(self.queue) == 0:
                await sleep(0.5)
                continue

            queue_position: QueuePosition = self.queue[0]

            while True:
                client = self.clients_service.get(queue_position.user_id)
                
                if client is not None:
                    queue_position.client = client
                    await self.create_session(queue_position.client, queue_position.user_id)
                    queue_position.event.set()
                    self.queue = self.queue[1:]
                    break

                await sleep(0.1)
        
    
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

        try:
            requests_balance = self.parse_account_message(account_message.text)
        except:
            requests_balance = -1

        client_string = await abrupt_session.stop()
        return requests_balance, client_string

    def parse_account_message(self, message: str):
        for phrase in message.split("\n"):
            if phrase.__contains__("Лимит запросов в сутки"):
                was, total = phrase.strip().split(":")[1].strip().split("/")
                return int(total) - int(was)
            
        raise Exception("Ошибка в парсинге сообщения с остатками")
        
