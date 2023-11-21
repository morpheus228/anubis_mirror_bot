import repositories
from repositories.mysql.models import Setting

from ..interfaces import Settings



class SettingsService(Settings):
	def __init__(self, repository: repositories.Settings):
		self.repository: repositories.Settings = repository

	def get(self, name: str) -> float|int|str:
		return self.repository.get(name=name).value[name]
	