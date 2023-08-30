import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery 
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext

from utils.message_template import MessageTemplate

from aiogram.fsm.state import State, StatesGroup


router = Router()


class States(StatesGroup):
    wallet = State()
    count = State()


@router.callback_query(Text("refferals"))
async def refferals(call: CallbackQuery, state: FSMContext):
    text, reply_markup = MessageTemplate.from_json('refferals/refferals').render()
    await call.message.edit_text(text=text, reply_markup=reply_markup)


@router.callback_query(Text("withdrawal"))
async def currency(call: CallbackQuery, state: FSMContext):
    text, reply_markup = MessageTemplate.from_json('refferals/currency').render()
    await call.message.edit_text(text=text, reply_markup=reply_markup)


@router.callback_query(Text("rub_refferals"))
async def request_wallet(call: CallbackQuery, state: FSMContext):
    text, reply_markup = MessageTemplate.from_json('refferals/wallet').render()
    await call.message.edit_text(text=text, reply_markup=reply_markup)
    await state.set_state(States.wallet)


@router.message(States.wallet)
async def take_wallet(message: CallbackQuery, state: FSMContext):
    await request_count(message, state)


async def request_count(message: CallbackQuery, state: FSMContext):
    # Исправить
    min, max = "100", "10000"

    text, reply_markup = MessageTemplate.from_json('refferals/count').render(
        min = min,
        max = max
    )
    
    await message.answer(text=text, reply_markup=reply_markup)
    await state.set_state(States.count)


@router.message(States.count)
async def take_count(message: CallbackQuery, state: FSMContext):

    text, reply_markup = MessageTemplate.from_json('refferals/success').render()
    await message.answer(text=text, reply_markup=reply_markup)
    await state.clear()
