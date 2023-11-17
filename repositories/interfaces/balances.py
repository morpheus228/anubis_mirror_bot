from abc import ABC, abstractmethod

from ..mysql.models import Balance


class Balances(ABC):
    @abstractmethod
    def create(self, user_id: int, value: float = 0) -> float:
        pass

    @abstractmethod
    def get(self, user_id: int) -> Balance:
        pass

    @abstractmethod
    def update(self, user_id: int, value: float) -> float:
        pass

    @abstractmethod
    def add(self, user_id: int, value: float):
        pass

    @abstractmethod
    def subtract(self, user_id: int, value: float):
        pass