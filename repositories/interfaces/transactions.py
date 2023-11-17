from abc import ABC, abstractmethod

from ..mysql.models import Balance, Wallet


class Transactions(ABC):
    @abstractmethod
    async def get_wallet_balance(self, wallet: Wallet, amount: float = 0.0001) -> float:
        pass
    
    @abstractmethod
    async def create_wallet(self, type: str) -> str:
        pass
        
    @abstractmethod
    async def make_transaction(self, type: str, address_from: str, address_to: str, amount: float) -> bool:
        pass