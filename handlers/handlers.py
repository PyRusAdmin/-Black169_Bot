# -*- coding: utf-8 -*-

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import dp
from keyboards.keyboards import contact_keyboard
from services.database import write_to_db_start_person
from services.i18n import t

router = Router(name=__name__)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Этот обработчик получает сообщения с командой '/start'
    """
    id_telegram = message.from_user.id
    first_name_telegram = message.from_user.first_name
    last_name_telegram = message.from_user.last_name
    username_telegram = message.from_user.username

    data = {
        "id_telegram": id_telegram,
        "last_name_telegram": last_name_telegram,
        "first_name_telegram": first_name_telegram,
        "username_telegram": username_telegram
    }
    write_to_db_start_person(data)

    await message.answer(
        text=t("greet-message"),
        reply_markup=contact_keyboard()
    )
