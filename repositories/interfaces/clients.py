from abc import ABC, abstractmethod

from ..mysql.models import Client

import pyrogram


class Clients(ABC):
	@abstractmethod
	def get_by_info(self, api_id: int, api_hash: str, phone_number: str) -> Client|None:
		pass

	@abstractmethod
	def get_by_name(self, name: str) -> Client|None:
		pass
	
	@abstractmethod
	def create(self, client: pyrogram.client.Client, phone_number: str, session_string: str) -> Client:
		pass
	
	@abstractmethod
	def get_available(self) -> Client:
		pass

	@abstractmethod
	def update_by_name(self, name: str, **kwargs) -> Client:
		pass

	@abstractmethod
	def clear(self):
		pass

	@abstractmethod
	def get(self) -> list[Client]:
		pass
