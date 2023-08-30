import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery 
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext

from utils.message_template import MessageTemplate

router = Router()


@router.callback_query(Text("account"))
async def account(call: CallbackQuery, state: FSMContext):

    # Исправить
    # Получение данных
    first_name = call.from_user.first_name
    balance = "300 руб"
    referral_count = "5"
    referral_link = "<i>реферальная ссылка</i>"
    
    text, reply_markup = MessageTemplate.from_json('account/account').render(
        first_name=first_name,
        balance=balance,
        referral_count=referral_count,
        referral_link=referral_link
    )

    await call.message.edit_text(text=text, reply_markup=reply_markup)


@router.callback_query(Text("pay_balance"))
async def currency(call: CallbackQuery, state: FSMContext):
    text, reply_markup = MessageTemplate.from_json('account/currency').render()
    await call.message.edit_text(text=text, reply_markup=reply_markup)


@router.callback_query(Text("usdt"))
async def ustd_network(call: CallbackQuery, state: FSMContext):
    text, reply_markup = MessageTemplate.from_json('account/ustd_network').render()
    await call.message.edit_text(text=text, reply_markup=reply_markup)


@router.callback_query(F.data.in_({'bep20', 'trc20', 'rub'}))
async def wallet(call: CallbackQuery, state: FSMContext):
    text, reply_markup = MessageTemplate.from_json('account/wallet').render()
    await call.message.edit_text(text=text, reply_markup=reply_markup)


@router.callback_query(Text("check_balance"))
async def check_balance(call: CallbackQuery, state: FSMContext):
    text, reply_markup = MessageTemplate.from_json('account/check_balance').render()
    await call.message.edit_text(text=text, reply_markup=reply_markup)

