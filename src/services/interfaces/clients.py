from abc import ABC, abstractmethod

from pyrogram import Client
from pyrogram.types import SentCode

from utils import generate_str


class Clients(ABC):
	@abstractmethod
	async def create(self, client: Client, phone_number: str, code_info: SentCode, sms_code: str) -> str:
		pass
	
	@abstractmethod
	async def check_uniqueness(self, api_id: int, api_hash: str, phone_number: str) -> bool:
		pass
	
	@abstractmethod
	async def request_sms_code(self, api_id: int, api_hash: str, phone_number: str) -> tuple[Client, SentCode]:
		pass
	
	@abstractmethod
	def get(self, user_id: int) -> Client|None:
		pass
	
	@abstractmethod
	def give(self, name: str, session_string: str):
		pass