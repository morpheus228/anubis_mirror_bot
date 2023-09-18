from abc import ABC, abstractmethod
from dataclasses import dataclass

from aiogram.types import Message


@dataclass
class RefferalInfo:
	link: str
	count: int
	total_earned: int
	available_for_withdrawal: float


class Refferals(ABC):
	@abstractmethod
	def get_info(self, user_id: int) -> RefferalInfo:
		pass
	
	@abstractmethod
	def process_start_message(self, message: Message):
		pass