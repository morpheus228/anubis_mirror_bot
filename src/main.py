import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from middlewares.user_availability import UserAvailabilityMiddleware

# from mirror.client_base import ClientsBase
from mirror.mirror import Mirror

from config import Config

from handlers.commands import router as command_router
from handlers.account import router as account_router
from handlers.refferals import router as refferals_router
from handlers.search import router as search_router
from handlers.requests import router as requests_router
from handlers.clients import router as clients_router

from repositories import mysql, Repository

from services import Service


logging.basicConfig(level=logging.INFO)


def register_routers(dp: Dispatcher):
    dp.include_router(command_router)
    dp.include_router(account_router)
    dp.include_router(refferals_router)
    dp.include_router(search_router)
    dp.include_router(clients_router)
    dp.include_router(requests_router)


def register_middlewares(dp: Dispatcher):
    dp.update.outer_middleware(UserAvailabilityMiddleware(dp['repository'].users))


async def register_default_commands(dp: Dispatcher):
    command_list = []
    for key in dp['commands']:
        command_list.append(BotCommand(command=key[1:], description=dp['commands'][key]))

    await dp['bot'].set_my_commands(command_list)


async def main():
    config = Config()
    bot = Bot(config.bot.token, parse_mode='HTML')

    engine = mysql.get_engine(config.mysql)
    repository = Repository(engine)
    service = Service(repository)

    dp = Dispatcher(storage=MemoryStorage())
    
    dp['config'] = config
    dp['dp'] = dp
    dp['bot'] = bot
    dp['service'] = service
    dp['repository'] = repository
    dp['mirror'] = Mirror(dp['bot'], service.clients, dp['config'].mirror)

    dp['commands'] = {"/help": "Помощь",
                      "/menu": "Меню",
                      "/account": "Аккаунт",
                      "/admin": "Админ"}
    
    await register_default_commands(dp)
    
    register_routers(dp)
    register_middlewares(dp)

    await dp.start_polling(dp['bot'])


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")
