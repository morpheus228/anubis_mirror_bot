from abc import ABC, abstractmethod
from aiogram import types

from ..mysql.models import User


class Users(ABC):
	@abstractmethod
	def create(self, user: types.User) -> User:
		pass