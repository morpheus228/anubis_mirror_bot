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

    refferal_reward_lvl_1 = service.settings.get('refferal_reward_lvl_1')
    refferal_reward_lvl_2 = service.settings.get('refferal_reward_lvl_2')
    
    kwargs = {
        "refferal_link": refferal_info.link,
        "total_earned": refferal_info.total_earned,
        "available_for_withdrawal": refferal_info.available_for_withdrawal,
        "refferals_count": refferal_info.count,

        "referral_reward_lvl_1": refferal_reward_lvl_1 * 100,
        "referral_reward_lvl_2": refferal_reward_lvl_2 * 100,
        "referral_reward": 5
    }

    text, reply_markup = MessageTemplate.from_json('refferals/refferals').render(**kwargs)
    await call.message.edit_text(text=text, reply_markup=reply_markup)
