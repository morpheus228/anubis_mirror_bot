from datetime import datetime, timedelta

import jwt
import repositories
import services
from utils import encryption

from aiogram.types import Message


class RefferalsService(services.Refferals):
	def __init__(self, 
			  config, 
			  repository: repositories.Referrals, 
			  user_repository: repositories.Users):
		
		self.repository: repositories.Referrals = repository
		self.user_repository: repositories.Users = user_repository
		self.config = config

	def get_link(self, user_id: int) -> str:
		return f"https://t.me/{self.bot.link}?start={user_id}"
	
	# На вход подается сообщение, если оно содержит команду /start
	# Функция проверяет наличие реферальной ссылки и обрабатывает ее
	def process_start_message(self, message: Message) -> str:
		child_id = message.from_user.id

		if self.repository.get_by_child_id(child_id) is None:
			parent_id = None

			if message.text != message.md_text:
				utm = message.md_text.split(" ")[-1]

				if utm.isdigit():
					utm = int(utm)

					if self.user_repository.get_by_id(utm) is not None:
						parent_id = utm

			self.repository.create(child_id=child_id, parent_id=parent_id)
