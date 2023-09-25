from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from services import Service
from services.interfaces.refferals import RefferalInfo
from services.interfaces.stats import Stats

from utils.message_template import MessageTemplate

router = Router()


@router.message(Command('start'))
async def start(message: Message, state: FSMContext, service: Service):
    service.refferals.process_start_message(message)
    
    text, reply_markup = MessageTemplate.from_json('commands/start').render()
    await message.answer(text=text, reply_markup=reply_markup)

    text, reply_markup = MessageTemplate.from_json('commands/menu').render()
    await message.answer(text=text, reply_markup=reply_markup)


@router.message(Command('help'))
async def help(message: Message, state: FSMContext):
    pass


@router.message(F.text.in_({'/menu', 'ℹ️ Показать меню'}))
async def menu(message: Message, state: FSMContext):
    text, reply_markup = MessageTemplate.from_json('commands/menu').render()
    await message.answer(text=text, reply_markup=reply_markup)


@router.message(Command("account"))
async def account(message: Message, state: FSMContext, service: Service):
    refferal_info: RefferalInfo = service.refferals.get_info(message.from_user.id)

    # Исправить
    balance = "300 руб"
    
    text, reply_markup = MessageTemplate.from_json('account/account').render(
        first_name = message.from_user.first_name,
        balance = balance,
        referral_count = refferal_info.count,
        referral_link = refferal_info.link
    )

    await message.answer(text=text, reply_markup=reply_markup)


@router.message(Command('admin'))
async def admin(message: Message, state: FSMContext, stats: Stats):
    stat = stats.get()
    text, reply_markup = MessageTemplate.from_json('commands/admin').render(stat=stat)
    await message.answer(text=text, reply_markup=reply_markup)


@router.callback_query(F.data == 'search')
async def search(call: CallbackQuery, state: FSMContext):
    text, reply_markup = MessageTemplate.from_json('commands/search').render()
    await call.message.edit_text(text=text, reply_markup=reply_markup, disable_web_page_preview=True)