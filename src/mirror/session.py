import asyncio
from enum import Enum
import random
import string


from anyio import sleep
from pyrogram import Client, filters
from pyrogram.types import Message


class ReplyType(Enum):
    message = 0
    edit_message = 1
    delete_message = 2


class Session:
    def __init__(self, client: Client, chat_id: str) -> None:
        self.client: Client = client
        self.chat_id: str = chat_id
        self.collected_replyes: list = []

    async def start(self):
        await self.client.start()
        self.apply_handlers()

    async def stop(self) -> str:
        session_string = await self.client.export_session_string()
        await self.client.stop()
        return session_string
    
    def apply_handlers(self):
        self.client.on_message(filters.chat(self.chat_id))(self.message_handle)
        self.client.on_edited_message(filters.chat(self.chat_id))(self.edit_message_handle)
        self.client.on_deleted_messages(filters.chat(self.chat_id))(self.delete_message_handle)

    async def message_handle(self, client: Client, message: Message):
        self.collected_replyes.append([ReplyType.message, message])

    async def edit_message_handle(self, client: Client, message: Message):
        self.collected_replyes.append([ReplyType.edit_message, message])

    async def delete_message_handle(self, client: Client, messages: list[Message]):
        print("УДАЛЕНО!!!")
        for message in messages:
            self.collected_replyes.append([ReplyType.delete_message, message])

    async def send_message(self, text: str):
        await self.client.send_message(self.chat_id, text)

    async def press_button(self, message_id: str, callback_data: str):
        await self.client.request_callback_answer(self.chat_id, message_id, callback_data)