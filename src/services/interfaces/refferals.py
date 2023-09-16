from abc import ABC, abstractmethod


class Refferals(ABC):
	@abstractmethod
	def get_link(self, user_id: int) -> str:
		pass
	
	@abstractmethod
	def process_link(bot_id: int) -> str:
		pass