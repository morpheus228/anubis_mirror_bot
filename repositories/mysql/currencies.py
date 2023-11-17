from abc import ABC, abstractmethod
import asyncio

import httpx

from repositories.mysql.models import Currency


class CurrenciesAPI:
    def __init__(self):
        self.url = "https://api-v2.coinmarketrate.com/api/cryptocurrency/one/"

    async def to_usdt(self, currency: Currency, value: float) -> float:
        async with httpx.AsyncClient() as client:
            response = await client.get(self.url + self.get_str_currency(currency))
            return value * response.json()['data']['stat']['price']
        
    async def from_usdt(self, value: float, currency: Currency) -> float:
        async with httpx.AsyncClient() as client:
            response = await client.get(self.url + self.get_str_currency(currency))
            print(response.json()['data']['stat']['price'])
            return value / response.json()['data']['stat']['price']

    @staticmethod
    def get_str_currency(currency: Currency) -> str:
        print(currency)
        if currency == Currency.BNB: return 'bnb'
        elif currency == Currency.TRX: return 'tron'
        elif currency == Currency.TON: return "toncoin"
        elif currency == Currency.DEL: return "decimal"
        return 'ooo'
