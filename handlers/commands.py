import logging
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from utils.message_template import MessageTemplate

router = Router()


@router.message(Command('start'))
async def start(message: Message, state: FSMContext):
    text, reply_markup = MessageTemplate.from_json('commands/start').render()
    await message.answer(text=text, reply_markup=reply_markup)

    text, reply_markup = MessageTemplate.from_json('commands/menu').render()
    await message.answer(text=text, reply_markup=reply_markup)


@router.message(Command('help'))
async def help(message: Message, state: FSMContext):
    pass


@router.message(Command('menu'))
async def menu(message: Message, state: FSMContext):
    text, reply_markup = MessageTemplate.from_json('commands/menu').render()
    await message.answer(text=text, reply_markup=reply_markup)


@router.message(Command("account"))
async def account(message: Message, state: FSMContext):

    # Исправить
    # Получение данных
    first_name = message.from_user.first_name
    balance = "300 руб"
    referral_count = "5"
    referral_link = "<i>реферальная ссылка</i>"
    
    text, reply_markup = MessageTemplate.from_json('account/account').render(
        first_name=first_name,
        balance=balance,
        referral_count=referral_count,
        referral_link=referral_link
    )

    await message.answer(text=text, reply_markup=reply_markup)


@router.message(Command('admin'))
async def admin(message: Message, state: FSMContext):
    pass