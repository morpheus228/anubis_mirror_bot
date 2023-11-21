import httpx
from sqlalchemy.orm import Session
from config import Config

from repositories.mysql.models import Currency, Wallet

from ..interfaces import Transactions


class TransactionsAPI(Transactions):
    def __init__(self, config: Config):
        self.config: Config = config
        self.url = 'http://185.250.44.26:6662/'
    
    async def get_wallet_balance(self, wallet: Wallet, amount: float = 0.0001) -> float:
        async with httpx.AsyncClient() as client:

            if wallet.currency == Currency.BNB: wallet_type = "USDTBEP20"
            elif wallet.currency == Currency.TRX: wallet_type = "USDTTRC20"
            else: wallet_type = wallet.currency._name_

            url = self.url + f"monitoring/{wallet_type}/{wallet.address}/{amount}"
            response = await client.get(url)
            return float(response.json()['balance'])
    
    async def create_wallet(self, type: str) -> str:
        async with httpx.AsyncClient() as client:
            url = self.url + f"create/{type}"
            response = await client.get(url)
            return response.text
        
    async def make_transaction(self, currency: Currency, address_from: str, address_to: str, amount: float) -> tuple[bool, float]:
        async with httpx.AsyncClient() as client:

            if currency == Currency.BNB: wallet_type = "USDTBEP20"
            elif currency == Currency.TRX: wallet_type = "USDTTRC20"
            elif currency == Currency.USDT: wallet_type = "USDTBEP20"
            else: wallet_type = currency._name_

            url = self.url + f"transfer/{wallet_type}/{address_from}/{address_to}/{amount}/{self.config.bot.transfers_password}"
            response = await client.get(url)

            if response.status_code == 200:
                return response.json()['status'], response.json()['fee'] 
