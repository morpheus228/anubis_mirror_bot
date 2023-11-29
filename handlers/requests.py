from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from mirror.mirror import Mirror, NoAvailableClientError



router = Router()


@router.message(F.text.regexp(r'^((\+7|7|8)+([0-9]){10})$') |
                F.text.regexp(r'\d{2}:\d{2}:\d{6,7}:\d*') |
                F.text.regexp(r'[A-HJ-NPR-Z0-9]{17}') |
                F.text.regexp(r'^https:\/\/www\.instagram\.com\/') |
                F.text.regexp(r'[-\w.]+@([A-z0-9][-A-z0-9]+\.)+[A-z]{2,4}$') |
                F.text.regexp(r'^[АВЕКМНОРСТУХ]\d{3}(?<!000)[АВЕКМНОРСТУХ]{2}\d{2,3}$') |
                F.text.regexp(r'^[АВЕКМНОРСТУХ]{2}\d{3}(?<!000)\d{2,3}$') |
                F.text.regexp(r'^[АВЕКМНОРСТУХ]{2}\d{4}(?<!0000)\d{2,3}$') |
                F.text.regexp(r'^\d{4}(?<!0000)[АВЕКМНОРСТУХ]{2}\d{2,3}$') |
                F.text.regexp(r'^[АВЕКМНОРСТУХ]{2}\d{3}(?<!000)[АВЕКМНОРСТУХ]\d{2,3}$') |
                F.text.regexp(r'^Т[АВЕКМНОРСТУХ]{2}\d{3}(?<!000)\d{2,3}$') |
                F.text.regexp(r'^@') |
                F.text.regexp(r'^#') |
                F.text.regexp(r'^https:\/\/www\.instagram\.com\/') |
                F.text.regexp(r'^https:\/\/vk\.com\/') |
                F.text.regexp(r'^https:\/\/facebook\.com\/') |
                F.text.regexp(r'^[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+$') |
                F.text.regexp(r'^[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+\s\d{2}\.\d{2}\.\d{4}$'))
@router.message(F.text != None)
async def reg_message_request(message: Message, state: FSMContext, mirror: Mirror, service):
    await mirror.U2S_send_message(message.from_user.id, message.text)


@router.message(Command("pas", "company", "inn", "snils", "adr"))
async def reg_message_request(message: Message, state: FSMContext, mirror: Mirror):
    await mirror.U2S_send_message(message.from_user.id, message.text)


@router.callback_query(F.data.contains("mirror"))
async def callback_answer(call: CallbackQuery, mirror: Mirror):
    if not await mirror.U2S_press_button(call.from_user.id, call.data):
        call.message.edit_text(call.message.text)


@router.message(F.photo != None)
async def photo_answer(message: Message, mirror: Mirror, bot: Bot):
    file = await bot.get_file(message.photo[-1].file_id)
    path = f"files/photos/{file.file_id}"
    await bot.download_file(file.file_path, path)
   
    await mirror.U2S_send_message(message.from_user.id, message.text, photo=path)