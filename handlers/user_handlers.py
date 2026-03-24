# -*- coding: utf-8 -*-
from aiogram import F, Router
from aiogram.types import Message
from loguru import logger

from services.database import write_to_db_registered_person
from services.i18n import t

router = Router(name=__name__)


@router.message(F.contact)
async def message_handler(message: Message) -> None:
    """
    Обработчик сообщений
    """
    id_telegram = message.from_user.id
    name_telegram = message.from_user.first_name
    first_name_telegram = message.from_user.last_name
    username_telegram = message.from_user.username
    phone_telegram = message.contact.phone_number
    logger.info(f"Пользователь отправил контакт: {phone_telegram}")

    data = {
        "id_telegram": id_telegram,
        "name_telegram": name_telegram,
        "first_name_telegram": first_name_telegram,
        "username_telegram": username_telegram,
        "phone_telegram": phone_telegram
    }

    write_to_db_registered_person(data)

    await message.answer(
        text=t("registered-message"),
    )
