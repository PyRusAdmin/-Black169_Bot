# -*- coding: utf-8 -*-
from aiogram import F, Router
from aiogram.types import Message
from loguru import logger
import asyncio
from config import layer_name_quickresto
from keyboards.keyboards import main_menu_keyboard
from services.database import write_to_db_registered_person
from services.i18n import t
from services.quickresto_api import print_client_info, auth, headers

router = Router(name=__name__)


@router.message(F.contact)
async def message_handler(message: Message) -> None:
    """
    Обработчик сообщений
    """
    id_telegram = message.from_user.id  # получаем id пользователя
    name_telegram = message.from_user.first_name  # получаем имя пользователя
    first_name_telegram = message.from_user.last_name  # получаем фамилию пользователя
    username_telegram = message.from_user.username  # получаем username пользователя
    phone_telegram = message.contact.phone_number  # получаем контакт пользователя
    logger.info(f"Пользователь отправил контакт: {phone_telegram}")

    phone_telegram = phone_telegram.replace("+", "")
    logger.info(f"Проверяем контакт: {phone_telegram} в базе QuickResto")

    data_customer = print_client_info(
        layer_name_quickresto=layer_name_quickresto,
        phone_number=phone_telegram,
        auth=auth,
        headers=headers
    )

    phone_quickresto = data_customer.get("phone")
    if phone_telegram == phone_quickresto:
        logger.info(f"Пользователь найден а базе QuickResto: {phone_telegram}")

        data = {
            "id_telegram": id_telegram,
            "name_telegram": name_telegram,
            "first_name_telegram": first_name_telegram,
            "username_telegram": username_telegram,
            "phone_telegram": phone_telegram
        }

        write_to_db_registered_person(data)

        sent = await message.answer(
            text=t("registered-message"),
            disable_notification=True
        )
        await asyncio.sleep(5)  # Ждём 5 секунд
        # Удаляем сообщение
        await sent.delete()

        await message.answer(
            text=t("main-menu"),
            reply_markup=main_menu_keyboard(),
        )

    else:
        logger.info(f"Пользователь не найден а базе QuickResto: {phone_telegram}")
