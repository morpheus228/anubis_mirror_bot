from .mysql import *
from .interfaces import *


class Repository:
	def __init__(self, engine):
		self.referrals: Referrals = ReferralsMYSQL(engine)
		self.clients: Clients = ClientsMYSQL(engine)
		self.users: Users = UsersMYSQL(engine)

