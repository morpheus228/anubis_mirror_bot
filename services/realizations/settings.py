import repositories
from repositories.mysql.models import Setting

from ..interfaces import Settings



class SettingsService(Settings):
	def __init__(self, repository: repositories.Settings):
		self.repository: repositories.Settings = repository

	def get(self) -> Setting:
		return self.repository.get()
	