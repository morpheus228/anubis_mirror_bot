import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from mirror.pyr_aio_converter import MirrorCallback

from mirror.mirror import Mirror
# from client.mirror import Mirror
# from client.end_conditions import MessageLambda

from utils.message_template import MessageTemplate

router = Router()


@router.message(F.text != None)
async def reg_message_request(message: Message, state: FSMContext, mirror: Mirror):
    await mirror.U2S_send_message(message.from_user.id, message.text)


# @router.message(Command("pas", "company", "inn", "snils", "adr"))
# async def reg_message_request(message: Message, state: FSMContext, mirror: Mirror):
#     await mirror.U2S_send_message(message.from_user.id, message.text)


@router.callback_query(F.data.contains("mirror"))
async def callback_answer(call: CallbackQuery, mirror: Mirror):
    if not await mirror.U2S_press_button(call.from_user.id, call.data):
        call.message.edit_text(call.message.text)