import asyncio
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from repositories.repository import Repository
from services.interfaces.refferals import RefferalInfo
from services.service import Service
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup

from utils.message_template import MessageTemplate
from utils.number_input import number_validation

router = Router()


class States(StatesGroup):
    withdraw_amount = State()
    withdraw_address = State()


class WalletCallback(CallbackData, prefix="check_balance"):
    wallet_id: int


@router.callback_query(F.data == "withdraw_money")
async def amount(call: CallbackQuery, state: FSMContext, service: Service):
    min_output_USDT = service.settings.get('min_output_USDT')
    balance = service.money.get_user_balance(call.from_user.id)

    text, reply_markup = MessageTemplate.from_json('withdraw_money/amount').render(
        min_output = min_output_USDT,
        max_output = balance
    )

    await call.message.edit_text(text=text, reply_markup=reply_markup)
    await state.set_state(States.withdraw_amount)


@router.message(States.withdraw_amount)
async def address(message: Message, state: FSMContext, service: Service):
    min_output_USDT = service.settings.get('min_output_USDT')
    balance = service.money.get_user_balance(message.from_user.id)

    amount = number_validation(message.text)

    if (amount is None) or (amount < min_output_USDT) or (amount > balance):
        text, reply_markup = MessageTemplate.from_json('withdraw_money/amount_error').render(
            min_output = min_output_USDT,
            max_output = balance
        )
        await message.answer(text=text, reply_markup=reply_markup)

    else:
        await state.update_data(amount=amount)
        text, reply_markup = MessageTemplate.from_json('withdraw_money/address').render(
            min_output = min_output_USDT,
            max_output = balance
        )

        await message.answer(text=text, reply_markup=reply_markup)
        await state.set_state(States.withdraw_address)


@router.message(States.withdraw_address)
async def withdraw(message: Message, state: FSMContext, service: Service):
    await state.update_data(address=message.text)
    data =  await state.get_data()

    commision = service.settings.get('commission_output_USDT')

    text, reply_markup = MessageTemplate.from_json('withdraw_money/withdraw').render(
        address = data['address'],
        price = data['amount'],
        price_with_commision = round(data['amount']-commision, 2),
        commision = commision
    )

    await message.answer(text=text, reply_markup=reply_markup)
    await state.set_state()


@router.callback_query(F.data == "avoid_withdraw")
async def avoid_withdraw(call: CallbackQuery, state: FSMContext, service: Service):
    await call.message.delete()
    

@router.callback_query(F.data == "confirm_withdraw")
async def confirm_withdraw(call: CallbackQuery, state: FSMContext, service: Service):
    min_output_USDT = service.settings.get('min_output_USDT')

    balance = service.money.get_user_balance(call.from_user.id)
    data = await state.get_data()

    if (data['amount'] < min_output_USDT) or (data['amount'] > balance):
        text, reply_markup = MessageTemplate.from_json('withdraw_money/amount_error').render(
            min_output = min_output_USDT,
            max_output = balance
        )
    
    else:
        text, reply_markup = MessageTemplate.from_json('withdraw_money/withdraw_success').render()
        await service.money.make_withdraw(call.from_user.id, data['amount'], data['address'])
        await call.message.edit_text(text=text, reply_markup=reply_markup)
        await state.clear()
