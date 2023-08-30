import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery 
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext

from utils.message_template import MessageTemplate

router = Router()


@router.callback_query(Text("search"))
async def search(call: CallbackQuery, state: FSMContext):
    text, reply_markup = MessageTemplate.from_json('search/search').render()
    await call.message.edit_text(text=text, reply_markup=reply_markup)

