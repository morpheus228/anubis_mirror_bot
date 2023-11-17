import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from middlewares.user_availability import UserAvailabilityMiddleware
from sqlalchemy.orm import Session

# from mirror.client_base import ClientsBase
from mirror.mirror import Mirror

from config import Config

from handlers.commands import router as command_router
from handlers.account import router as account_router
from handlers.refferals import router as refferals_router
from handlers.requests import router as requests_router
from handlers.clients import router as clients_router
from handlers.withdraw_money import router as withdraw_router

from repositories import mysql, Repository
from repositories.mysql.models import Setting, User

from services import Service
from services.realizations.stats import StatsServece


logging.basicConfig(level=logging.INFO)


def register_routers(dp: Dispatcher):
    dp.include_router(command_router)
    dp.include_router(account_router)
    dp.include_router(withdraw_router)
    dp.include_router(refferals_router)
    dp.include_router(clients_router)
    dp.include_router(requests_router)


def register_middlewares(dp: Dispatcher):
    dp.update.outer_middleware(UserAvailabilityMiddleware(dp['repository']))


async def register_default_commands(dp: Dispatcher):
    command_list = []
    for key in dp['commands']:
        command_list.append(BotCommand(command=key[1:], description=dp['commands'][key]))

    await dp['bot'].set_my_commands(command_list)


def on_startup(repository: Repository):
    pass
    # from repositories.mysql.models import Base
    # Base.metadata.drop_all(repository.engine)
    # Base.metadata.create_all(repository.engine)

    # repository.clients.clear()
    # repository.users.clear()

    # repository.users.create(User(id=1))
    # repository.balances.create(1)

    # repository.users.create(User(id=2))
    # repository.balances.create(2)

    # repository.settings.create(Setting(
    #     id = 1,

    #     extra_charge = 0.1,
    #     request_cost = 0.1,

    #     commissio_output_USDT = 0.01,

    #     admin_wallet_BNB = 'dfdfdf',
    #     admin_wallet_DEL = 'dfdfdf',
    #     admin_wallet_TON = 'dfdfdf',
    #     admin_wallet_TRX = 'dfdfdf',
    #     admin_wallet_USDT = 'dfdfdf',

    #     min_balance_BNB = 0.01,
    #     min_balance_TRX = 0.01,
    #     min_balance_TON = 0.01,
    #     min_balance_DEL = 0.01,

    #     refferal_reward_lvl_1 = 0.12,
    #     refferal_reward_lvl_2 = 0.01,

    #     min_output_USDT = 0.01,
    #     max_output_USDT = 1000
    # ))


async def main():
    config = Config()
    bot = Bot(config.bot.token, parse_mode='HTML')

    engine = mysql.get_engine(config.mysql)
    repository = Repository(engine)

    service = Service(repository, config)
    mirror = Mirror(bot, service.clients, service.money, config.mirror)
    stats = StatsServece(repository.users, repository.clients, mirror)

    dp = Dispatcher(storage=MemoryStorage())
    
    dp['config'] = config
    dp['dp'] = dp
    dp['bot'] = bot
    dp['service'] = service
    dp['mirror'] = mirror
    dp['stats'] = stats
    dp['repository'] = repository

    dp['commands'] = {"/help": "Помощь",
                      "/menu": "Меню",
                      "/account": "Аккаунт"}
    
    on_startup(repository)

    await register_default_commands(dp)
    
    register_routers(dp)
    register_middlewares(dp)

    await dp.start_polling(dp['bot'])


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")
