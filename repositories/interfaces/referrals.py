from abc import ABC, abstractmethod

from ..mysql.models import Referral


class Referrals(ABC):
	@abstractmethod
	def get_by_child_id(self, child_id: int) -> Referral:
		pass
	
	@abstractmethod
	def create(self, child_id: int, parent_id: int):
		pass

	@abstractmethod
	def get_refferal_ids(self, parent_id: int) -> list[int]:
		pass
