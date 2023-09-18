from config import Config
from repositories import Repository

from .realizations import *
from .interfaces import *


class Service:
	def __init__(self, repository: Repository, config: Config):
		self.refferals: Refferals = RefferalsService(config, repository.referrals, repository.users)
		self.clients: Clients = ClientsService(repository.clients)
		self.settings: Settings = SettingsService(repository.settings)
