from aiogram import Router, F
from aiogram.types import CallbackQuery 
from aiogram.fsm.context import FSMContext
from config import Config
from services import Service

from utils.message_template import MessageTemplate

from aiogram.fsm.state import State, StatesGroup


router = Router()


class States(StatesGroup):
    wallet = State()
    count = State()


@router.callback_query(F.data == "refferals")
async def refferals(call: CallbackQuery, state: FSMContext, config: Config, service: Service):
    refferal_info = service.refferals.get_info(call.from_user.id)
    settings = service.settings.get()
    
    kwargs = {
        "refferal_link": refferal_info.link,
        "total_earned": refferal_info.total_earned,
        "available_for_withdrawal": refferal_info.available_for_withdrawal,
        "refferals_count": refferal_info.count,

        "referral_reward_lvl_1": settings.refferal_reward_lvl_1 * 100,
        "referral_reward_lvl_2": settings.refferal_reward_lvl_2 * 100,
        "referral_reward": 5
    }

    text, reply_markup = MessageTemplate.from_json('refferals/refferals').render(**kwargs)
    await call.message.edit_text(text=text, reply_markup=reply_markup)


@router.callback_query(F.data == "withdrawal")
async def currency(call: CallbackQuery, state: FSMContext):
    text, reply_markup = MessageTemplate.from_json('refferals/currency').render()
    await call.message.edit_text(text=text, reply_markup=reply_markup)


@router.callback_query(F.data == "rub_refferals")
async def request_wallet(call: CallbackQuery, state: FSMContext):
    text, reply_markup = MessageTemplate.from_json('refferals/wallet').render()
    await call.message.edit_text(text=text, reply_markup=reply_markup)
    await state.set_state(States.wallet)


@router.message(States.wallet)
async def take_wallet(message: CallbackQuery, state: FSMContext, service: Service):
    await request_count(message, state, service)


async def request_count(message: CallbackQuery, state: FSMContext, service: Service):
    settings = service.settings.get()

    text, reply_markup = MessageTemplate.from_json('refferals/count').render(
        min = settings.min_output,
        max = settings.max_output
    )
    
    await message.answer(text=text, reply_markup=reply_markup)
    await state.set_state(States.count)


@router.message(States.count)
async def take_count(message: CallbackQuery, state: FSMContext, service: Service):
    settings = service.settings.get()

    if (message.text.isdigit()) and (float(message.text) <= settings.max_output) and (float(message.text) >= settings.min_output):
        text, reply_markup = MessageTemplate.from_json('refferals/success').render()
        await message.answer(text=text, reply_markup=reply_markup)
        await state.clear()

    else:
        await message.answer(text="Введеное значение не соответсвует допустимому.")
        await state.clear()
