from abc import ABC, abstractmethod
from aiogram import types

from ..mysql.models import User


class Users(ABC):
	@abstractmethod
	def create(self, user: types.User) -> User:
		pass
	
	@abstractmethod
	def get_by_id(self, user_id: int) -> User|None:
		pass
	
	@abstractmethod
	def get(self) -> list[User|None]:
		pass

	@abstractmethod
	def clear(self):
		pass