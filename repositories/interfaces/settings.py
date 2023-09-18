from abc import ABC, abstractmethod

from ..mysql.models import Setting


class Settings(ABC):
    @abstractmethod
    def get(self) -> Setting:
        pass
    
    @abstractmethod
    def create(self, setting: Setting) -> Setting:
        pass