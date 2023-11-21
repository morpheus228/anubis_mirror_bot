from abc import ABC, abstractmethod

from ..mysql.models import Setting


class Settings(ABC):
    @abstractmethod
    def get(self, name: str) -> float|int|str:
        pass
    
    @abstractmethod
    def create(self, setting: Setting) -> Setting:
        pass