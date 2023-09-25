import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services import Service

from utils.message_template import MessageTemplate

router = Router()


class States(StatesGroup):
    api_id = State()
    api_hash = State()
    phone_number = State()
    sms_code = State()


@router.callback_query(F.data == "add_client")
async def request_api_id(call: CallbackQuery, state: FSMContext):
    text, reply_markup = MessageTemplate.from_json('clients/api_id').render()
    await call.message.edit_text(text=text, reply_markup=reply_markup)
    await state.set_state(States.api_id)


@router.message(States.api_id)
async def take_api_id(message: Message, state: FSMContext):
    await state.update_data(api_id=message.text)
    await request_api_hash(message, state)


async def request_api_hash(message: Message, state: FSMContext):
    text, reply_markup = MessageTemplate.from_json('clients/api_hash').render()
    await message.answer(text=text, reply_markup=reply_markup)
    await state.set_state(States.api_hash)


@router.message(States.api_hash)
async def take_api_hash(message: Message, state: FSMContext):
    await state.update_data(api_hash=message.text)
    await request_phone_number(message, state)


async def request_phone_number(message: Message, state: FSMContext):
    text, reply_markup = MessageTemplate.from_json('clients/phone_number').render()
    await message.answer(text=text, reply_markup=reply_markup)
    await state.set_state(States.phone_number)


@router.message(States.phone_number)
async def take_phone_number(message: Message, state: FSMContext, service: Service):
    await state.update_data(phone_number=message.text)
    await request_sms_code(message, state, service)


async def request_sms_code(message: Message, state: FSMContext, service: Service):
    data = await state.get_data()

    if not await service.clients.check_uniqueness(data['api_id'], data['api_hash'], data['phone_number']):
        text, reply_markup = MessageTemplate.from_json('clients/not_unique').render()
        await message.answer(text=text, reply_markup=reply_markup)
        await state.clear(); return
    
    try:
        client, code_info = await service.clients.request_sms_code(data['api_id'], data['api_hash'], data['phone_number'])
        await state.update_data(client=client, code_info=code_info)
        text, reply_markup = MessageTemplate.from_json('clients/sms_code').render()
        await message.answer(text=text, reply_markup=reply_markup)
        await state.set_state(States.sms_code)
        
    except Exception as err:
        await message.answer(f"Произошла ошибка: {err}")
        await state.clear()


@router.message(States.sms_code)
async def take_sms_code(message: Message, state: FSMContext, service: Service):
    sms_code = message.text.replace("-", "")
    data = await state.get_data()

    try:
        client_name = await service.clients.create(
            client=data['client'], phone_number=data['phone_number'], 
            code_info=data['code_info'], sms_code=sms_code)
        
        text, reply_markup = MessageTemplate.from_json('clients/success').render(client_name=client_name)
        await message.answer(text=text, reply_markup=reply_markup)
        await state.clear()
        
        
    except Exception as err:
        await message.answer(f"Произошла ошибка: {err}")
        await state.clear()
