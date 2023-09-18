import repositories
import services
from services.interfaces.refferals import RefferalInfo

from ..interfaces import Refferals

from aiogram.types import Message


class RefferalsService(Refferals):
	def __init__(self, 
			  config, 
			  repository: repositories.Referrals, 
			  user_repository: repositories.Users):
		
		self.repository: repositories.Referrals = repository
		self.user_repository: repositories.Users = user_repository
		self.config = config


	def get_info(self, user_id: int) -> RefferalInfo:
		refferal_ids_lvl_1 = self.repository.get_refferal_ids(user_id)

		refferal_ids_lvl_2 = []
		for refferal_id in refferal_ids_lvl_1:
			refferal_ids_lvl_2 += self.repository.get_refferal_ids(refferal_id)

		return RefferalInfo(
			link = f"https://t.me/{self.config.bot.link}?start={user_id}",
			count = len(refferal_ids_lvl_1) + len(refferal_ids_lvl_2),
			total_earned = 15,
			available_for_withdrawal = 300
		)
	
	def process_start_message(self, message: Message):
		child_id = message.from_user.id
		
		if self.repository.get_by_child_id(child_id) is None:
			parent_id = self.parse_message_text(message)

			if (parent_id is not None) and (parent_id != child_id): 
				self.repository.create(child_id=child_id, parent_id=parent_id)
				# добавляем оплату за реферал
			else:
				self.repository.create(child_id=child_id, parent_id=None)

	def parse_message_text(self, message: Message) -> int|None:
		if message.md_text == "/start":
			return None
		
		utm = message.md_text.split(" ")[-1]

		if not utm.isdigit():
			return None
		
		if self.user_repository.get_by_id(int(utm)) is None:
			return None

		return int(utm)