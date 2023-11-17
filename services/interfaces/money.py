from abc import ABC, abstractmethod
from aiogram.types import Message

from repositories.mysql.models import Wallet


class Money(ABC):
	payment_messages: dict[int, Message] = {}
	
	@abstractmethod
	def get_user_balance(self, user_id: int) -> float|None:
		pass

	@abstractmethod
	async def get_user_wallet(self, user_id: int, currency: str) -> Wallet:
		pass

	@abstractmethod
	async def check_wallet(self, wallet_id: int):
		pass

	@abstractmethod
	def check_money_availability(self, user_id: int) -> bool:
		pass

	@abstractmethod
	def pay_request(self, user_id: int, count: int) -> bool:
		pass

	@abstractmethod
	async def make_withdraw(self, user_id: int, count: int, address: str) -> bool:
		pass