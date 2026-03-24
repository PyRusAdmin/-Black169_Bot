# -*- coding: utf-8 -*-
from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove
from loguru import logger

from config import layer_name_quickresto
from keyboards.inline import main_menu_keyboard
from services.database import write_to_db_registered_person
from services.i18n import t
from services.quickresto_api import print_client_info, auth, headers, create_client, base_url

router = Router(name=__name__)


@router.message(F.contact)
async def message_handler(message: Message) -> None:
    """
    Обработчик сообщений
    """
    try:
        id_telegram = message.from_user.id  # получаем id пользователя
        name_telegram = message.from_user.first_name  # получаем имя пользователя
        first_name_telegram = message.from_user.last_name  # получаем фамилию пользователя
        username_telegram = message.from_user.username  # получаем username пользователя
        phone_telegram = message.contact.phone_number  # получаем контакт пользователя
        logger.info(f"Пользователь отправил контакт: {phone_telegram}")

        phone_telegram = phone_telegram.replace("+", "")
        logger.info(f"Проверяем контакт: {phone_telegram} в базе QuickResto")
        # проверяем контакт в базе QuickResto
        data_customer = print_client_info(
            layer_name_quickresto=layer_name_quickresto,
            phone_number=phone_telegram,
            auth=auth,
            headers=headers
        )

        if data_customer is None:
            logger.warning(f"Пользователь не найден а базе QuickResto: {phone_telegram}")
            create_client(
                name_customer=name_telegram,
                phone_customer=phone_telegram,
                base_url=base_url,
                auth=auth,
                headers=headers
            )

        phone_quickresto = data_customer.get("phone")
        if phone_telegram == phone_quickresto:
            logger.success(f"Пользователь найден а базе QuickResto: {phone_telegram}")

            data = {
                "id_telegram": id_telegram,
                "id_quickresto": data_customer.get("client_id"),
                "last_name": data_customer.get("lastName"),
                "first_name": data_customer.get("firstName"),
                "phone_telegram": phone_telegram
            }

            write_to_db_registered_person(data)  # записываем данные в базу данных

            # Сначала удаляем реплай-клавиатуру
            await message.answer(
                text=t("registration-completed"),
                reply_markup=ReplyKeyboardRemove(remove_keyboard=True),
            )
            # Затем показываем главное меню
            await message.answer(
                text=t("main-menu"),
                reply_markup=main_menu_keyboard(),
            )
    except Exception as e:
        logger.exception(e)
