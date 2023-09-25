from abc import ABC, abstractmethod

from ..mysql.models import QueuePosition


class Queue(ABC):
    @abstractmethod
    def create(self, user_id: int):
        pass
    
    @abstractmethod
    def get(self) -> QueuePosition|None:
        pass
    
    @abstractmethod
    def get_count(self) -> int:
        pass