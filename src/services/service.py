from repositories import Repository

from .realizations import *
from .interfaces import *


class Service:
	def __init__(self, repository: Repository):
		# self.refferals: Refferals = RefferalsService()
		self.clients: Clients = ClientsService(repository.clients)