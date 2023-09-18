from abc import ABC, abstractmethod

from repositories.mysql.models import Setting


class Settings(ABC):
    @abstractmethod
    def get(self) -> Setting:
        pass