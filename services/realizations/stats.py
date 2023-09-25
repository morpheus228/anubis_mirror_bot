import repositories
from ..interfaces import Stats, Stat


class StatsServece(Stats):
	def __init__(self,
			     user_repository: repositories.Users,
			     client_repository: repositories.Clients,
			     mirror):
	
		self.user_repository: repositories.Users = user_repository
		self.client_repository: repositories.Clients = client_repository
		self.mirror = mirror

	def get(self) -> Stat:
		users = self.user_repository.get()
		clients = self.client_repository.get()

		return Stat(
            users_count = len(users),
			clients_count = len(clients),
			busy_clients_count = len(list(filter(lambda x: x.is_used_by == None, clients))),
			request_count = sum([client.requests_balance for client in clients]),
			queue_size = len(self.mirror.queue)
		)