import asyncio
import logging
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

router = Router()


class States(StatesGroup):
    amount = State()


class WalletCallback(CallbackData, prefix="check_balance"):
    wallet_id: int


@router.callback_query(F.data == "account")
async def account(call: CallbackQuery, state: FSMContext, service: Service):
    refferal_info: RefferalInfo = service.refferals.get_info(call.from_user.id)
    balance: float = service.money.get_user_balance(call.from_user.id)
    
    text, reply_markup = MessageTemplate.from_json('account/account').render(
        first_name = call.from_user.first_name,
        balance = str(round(balance, 2)) + "$",
        referral_count = refferal_info.count,
        referral_link = refferal_info.link
    )

    await call.message.edit_text(text=text, reply_markup=reply_markup)


@router.callback_query(F.data == "pay_balance")
async def currency(call: CallbackQuery, state: FSMContext):
    text, reply_markup = MessageTemplate.from_json('account/currency').render()
    await call.message.edit_text(text=text, reply_markup=reply_markup)


@router.callback_query(F.data.in_({'BNB', 'TRX', 'TON', 'DEL'}))
async def amount(call: CallbackQuery, state: FSMContext, service: Service):
    wallet = await service.money.get_user_wallet(call.from_user.id, call.data)
    payment_message = service.money.payment_messages.get(wallet.id, None)

    if payment_message is not None:
        message = await call.message.edit_text(text=payment_message.text, reply_markup=payment_message.reply_markup)
        await payment_message.delete()
        service.money.payment_messages[wallet.id] = message
    
    else:
        await state.update_data(currency=call.data)
        text, reply_markup = MessageTemplate.from_json('account/amount').render()
        await call.message.edit_text(text=text, reply_markup=reply_markup)
        await state.set_state(States.amount)


@router.message(States.amount)
async def wallet_(message: Message, state: FSMContext, service: Service, repository: Repository):
    if not message.text.isdigit():
        text, reply_markup = MessageTemplate.from_json('account/invalid_amount').render()
        await message.answer(text=text, reply_markup=reply_markup)

    else:
        data = await state.get_data()
        wallet = await service.money.get_user_wallet(message.from_user.id, data['currency'])
        logging.info(f"Начальный баланс кошелька ({wallet.id}) = {wallet.balance}")

        if data['currency'] == "BNB": wallet_type = "USDTBEP20"
        elif data['currency'] == "TRX": wallet_type = "USDTTRC20"
        else: wallet_type = data['currency']

        amount = round(await repository.currencies.from_usdt(int(message.text), wallet.currency), 2)
        
        text, reply_markup = MessageTemplate.from_json('account/wallet').render(
            wallet_address=wallet.address,
            amount=round(amount, 2),
            currency=data['currency'],
            type=wallet_type
        )

        await state.update_data(amount=round(amount, 2))
        await state.update_data(wallet_type=wallet_type)

        callback_data = WalletCallback(wallet_id=wallet.id).pack()
        reply_markup = InlineKeyboardBuilder([[InlineKeyboardButton(text="Проверить баланс", callback_data=callback_data)]]).as_markup()

        message = await message.answer(text=text, reply_markup=reply_markup)
        service.money.payment_messages[wallet.id] = message



@router.callback_query(F.data.contains("check_balance"))
async def check_balance(call: CallbackQuery, state: FSMContext, service: Service):
    text = call.message.html_text.replace("ожидание", "ожидает потверждения")
    text = text.replace("⚠ После отправĸи валюты на уĸазанный адрес нажмите ĸнопĸу «Проверить транзаĸцию»", "")
    await call.message.edit_text(text)

    wallet_id = WalletCallback.unpack(call.data).wallet_id
    data = await state.get_data()
    asyncio.create_task(service.money.check_wallet(wallet_id, data['amount'], data['wallet_type']))
    await state.clear()
