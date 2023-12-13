from aiogram import BaseMiddleware
from aiogram.types import Update, User
import repositories
from repositories.mysql.models import Currency
from repositories.repository import Repository


class UserAvailabilityMiddleware(BaseMiddleware):
    def __init__(self, repository: Repository):
        self.repository: Repository = repository

    async def __call__(self, handler, update: Update, data: dict):
        user: User = update.event.from_user
        
        if not self.repository.users.get_by_id(user.id):
           self.repository.users.create(user)
           self.repository.balances.create(user.id, 1.5)

           self.repository.wallets.create(user.id, Currency.DEL, await self.repository.transaction.create_wallet('DEL'))
           self.repository.wallets.create(user.id, Currency.TON, await self.repository.transaction.create_wallet('TON'))
           self.repository.wallets.create(user.id, Currency.TRX, await self.repository.transaction.create_wallet('USDTTRC20'))
           self.repository.wallets.create(user.id, Currency.BNB, await self.repository.transaction.create_wallet('USDTBEP20'))
            
        await handler(update, data)