import httpx
from sqlalchemy.orm import Session

from repositories.mysql.models import Wallet

from ..interfaces import Transactions


class TransactionsAPI(Transactions):
    def __init__(self):
        self.url = 'http://185.250.44.26:6662/'
    
    async def get_wallet_balance(self, wallet: Wallet, amount: float = 0.0001) -> float:
        async with httpx.AsyncClient() as client:
            url = self.url + f"monitoring/{wallet.currency}/{wallet.address}/{amount}"
            response = await client.get(url)
            return float(response.json())
    
    async def create_wallet(self, type: str) -> str:
        async with httpx.AsyncClient() as client:
            url = self.url + f"create/{type}"
            response = await client.get(url)
            return response.text
        
    async def make_transaction(self, type: str, address_from: str, address_to: str, amount: float) -> tuple[bool, float]:
        async with httpx.AsyncClient() as client:
            url = self.url + f"transfer/{type}/{address_from}/{address_to}/{amount}"
            response = await client.get(url)
            return response.json()['status'], response.json()['fee'] 
