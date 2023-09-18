from aiogram import Router, F
from aiogram.types import CallbackQuery 
from aiogram.fsm.context import FSMContext
from services.interfaces.refferals import RefferalInfo
from services.service import Service

from utils.message_template import MessageTemplate

router = Router()


@router.callback_query(F.data == "account")
async def account(call: CallbackQuery, state: FSMContext, service: Service):
    refferal_info: RefferalInfo = service.refferals.get_info(call.from_user.id)

    # Исправить
    balance = "300 руб"
    
    text, reply_markup = MessageTemplate.from_json('account/account').render(
        first_name = call.from_user.first_name,
        balance = balance,
        referral_count = refferal_info.count,
        referral_link = refferal_info.link
    )

    await call.message.edit_text(text=text, reply_markup=reply_markup)


@router.callback_query(F.data == "pay_balance")
async def currency(call: CallbackQuery, state: FSMContext):
    text, reply_markup = MessageTemplate.from_json('account/currency').render()
    await call.message.edit_text(text=text, reply_markup=reply_markup)


@router.callback_query(F.data == "usdt")
async def ustd_network(call: CallbackQuery, state: FSMContext):
    text, reply_markup = MessageTemplate.from_json('account/ustd_network').render()
    await call.message.edit_text(text=text, reply_markup=reply_markup)


@router.callback_query(F.data.in_({'bep20', 'trc20', 'rub'}))
async def wallet(call: CallbackQuery, state: FSMContext):
    text, reply_markup = MessageTemplate.from_json('account/wallet').render()
    await call.message.edit_text(text=text, reply_markup=reply_markup)


@router.callback_query(F.data == "check_balance")
async def check_balance(call: CallbackQuery, state: FSMContext):
    text, reply_markup = MessageTemplate.from_json('account/check_balance').render()
    await call.message.edit_text(text=text, reply_markup=reply_markup)

