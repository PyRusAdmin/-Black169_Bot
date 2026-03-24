# -*- coding: utf-8 -*-
from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove
from loguru import logger

from config import layer_name_quickresto
from keyboards.inline import main_menu_keyboard
from services.database import write_to_db_registered_person
from services.i18n import t
from services.quickresto_api import print_client_info, create_client, auth, headers, base_url

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
        phone_telegram = message.contact.phone_number  # получаем контакт пользователя
        logger.info(f"Пользователь отправил контакт: {phone_telegram}")

        phone_telegram = phone_telegram.replace("+", "")
        logger.info(f"Проверяем контакт: {phone_telegram} в базе QuickResto")

        # Проверяем контакт в базе QuickResto
        data_customer = print_client_info(
            layer_name_quickresto=layer_name_quickresto,
            phone_number=phone_telegram,
            auth=auth,
            headers=headers
        )

        # Если клиент не найден — создаём нового
        if data_customer is None:
            logger.info(f"Клиент не найден, создаём нового: {phone_telegram}")

            created_client = create_client(
                name_customer=name_telegram,
                phone_customer=phone_telegram,
                base_url=base_url,
                auth=auth,
                headers=headers
            )

            if created_client:
                client_id = created_client.get('id')
                logger.success(f"Клиент создан в QuickResto: id={client_id}")

                data = {
                    "id_telegram": id_telegram,
                    "id_quickresto": client_id,
                    "last_name": first_name_telegram,
                    "first_name": name_telegram,
                    "phone_telegram": phone_telegram
                }

                write_to_db_registered_person(data)

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
            else:
                logger.error("Не удалось создать клиента в QuickResto")
                await message.answer(text=t("user-not-found"))
            return

        # Клиент найден
        phone_quickresto = data_customer.get("phone")
        if phone_telegram == phone_quickresto:
            logger.success(f"Пользователь найден в базе QuickResto: {phone_telegram}")

            data = {
                "id_telegram": id_telegram,
                "id_quickresto": data_customer.get("client_id"),
                "last_name": data_customer.get("lastName"),
                "first_name": data_customer.get("firstName"),
                "phone_telegram": phone_telegram
            }

            write_to_db_registered_person(data)

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
        else:
            logger.warning(f"Пользователь не найден в базе QuickResto: {phone_telegram}")
            await message.answer(text=t("user-not-found"))

    except Exception as e:
        logger.exception(e)
