import asyncio
import datetime
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from anyio import sleep
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


logging.basicConfig(level=logging.ERROR)


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

    # repository.settings.create('extra_charge', 'extra_charge', {"extra_charge": 0.1})
    # repository.settings.create('request_cost', 'request_cost', {"request_cost": 0.1})
    # repository.settings.create('commissio_output_USDT', 'commission_input_usdt', {"commissio_output_USDT": 0.01})
    # repository.settings.create('admin_wallet_BNB', 'admin_wallet_bnb', {"admin_wallet_BNB": '0x82fc376cc654b0f101e3f31bb6f310474d79a4a5'})
    # repository.settings.create('admin_wallet_DEL', 'admin_wallet_del', {"admin_wallet_DEL": 'd01st7rwmxx2jc0zq0r7vdmducsgaxhnf99xr4skp'})
    # repository.settings.create('admin_wallet_TON', 'admin_wallet_ton', {"admin_wallet_TON": 'UQAd1eAW_v7HcfXEc4EOiPzzzAF95TVbz6fNyvo5nE9SaEXV'})
    # repository.settings.create('admin_wallet_TRX', 'admin_wallet_trx', {"admin_wallet_TRX": 'TVeiCR3gJviMjDKD3BcLYZqxEyXgTqHuft'})
    # repository.settings.create('admin_wallet_USDT', 'admin_wallet_usdt', {"admin_wallet_USDT": 'TVeiCR3gJviMjDKD3BcLYZqxEyXgTqHuft'})
    # repository.settings.create('min_balance_BNB', 'min_balance_bnb', {"min_balance_BNB": 0.01})
    # repository.settings.create('min_balance_TRX', 'min_balance_trx', {"min_balance_TRX": 0.01})
    # repository.settings.create('min_balance_TON', 'min_balance_ton', {"min_balance_TON": 0.01})
    # repository.settings.create('min_balance_DEL', 'min_balance_del', {"min_balance_DEL": 0.01})
    # repository.settings.create('refferal_reward_lvl_1', 'refferal_reward_lvl_1',  {"refferal_reward_lvl_1": 0.12})
    # repository.settings.create('refferal_reward_lvl_2', 'refferal_reward_lvl_2',  {"refferal_reward_lvl_2": 0.01})
    # repository.settings.create('min_output_USDT', 'refferal_reward_lvl_2',  {"min_output_USDT": 0.01})
    # repository.settings.create('max_output_USDT', 'refferal_reward_lvl_2',  {"max_output_USDT": 0.01})
    # repository.settings.create('commission_output_USDT', 'commission_output_USDT',  {"commission_output_USDT": 0.05})


async def update_clients(repository: Repository):
    while True:
        now = datetime.datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0)

        if now == midnight:
            repository.clients.update_values()
        else:
            await sleep(1)


async def main():
    config = Config()
    bot = Bot(config.bot.token, parse_mode='HTML')

    engine = mysql.get_engine(config.mysql)
    repository = Repository(engine, config)

    repository.clients.clear()

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

    asyncio.create_task(update_clients(repository))
    await dp.start_polling(dp['bot'])


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("ебать!")
