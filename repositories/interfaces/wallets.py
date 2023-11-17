from abc import ABC, abstractmethod

from ..mysql.models import Wallet, Currency


class Wallets(ABC):
    @abstractmethod
    def create(self, user_id: int, type: Currency, address: str, balance: float = 0) -> float:
        pass

    @abstractmethod
    def get_by_user(self, user_id: int, currency: Currency) -> Wallet:
        pass

    @abstractmethod
    def get_by_id(self, wallet_id: int) -> Wallet:
        pass

    @abstractmethod
    def update(self, wallet_id: int, balance: float) -> Wallet:
        pass