# -*- coding: utf-8 -*-
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from loguru import logger

from keyboards.keyboards import contact_keyboard
from services.database import write_to_db_start_person
from services.i18n import t

router = Router(name=__name__)


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Этот обработчик получает сообщения с командой '/start'
    """
    logger.info(f"Получена команда /start от пользователя {message.from_user.id}")

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

    logger.info(f"Отправка приветственного сообщения пользователю {message.from_user.id}")
    await message.answer(
        text=t("greet-message"),
        reply_markup=contact_keyboard()
    )


@router.message(F.text)
async def echo_handler(message: Message) -> None:
    """
    Обработчик всех сообщений для отладки
    """
    logger.info(f"Получено сообщение от {message.from_user.id}: {message.text or message.content_type}")
