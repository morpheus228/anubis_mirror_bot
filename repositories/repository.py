from .mysql import *
from .interfaces import *


class Repository:
	def __init__(self, engine):
		self.engine = engine
		
		self.referrals: Referrals = ReferralsMYSQL(engine)
		self.clients: Clients = ClientsMYSQL(engine)
		self.users: Users = UsersMYSQL(engine)
		self.settings: Settings = SettingsMYSQL(engine)
		self.balances: Balances = BalancesMYSQL(engine)
		self.wallets: Wallets = WalletsMYSQL(engine)
		self.transaction: Transactions = TransactionsAPI()
		self.currencies: CurrenciesAPI = CurrenciesAPI()
		self.pays: PaysMYSQL = PaysMYSQL(engine)

