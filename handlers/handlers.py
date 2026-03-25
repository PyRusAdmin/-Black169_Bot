# -*- coding: utf-8 -*-
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery
from aiogram.types import Message
from loguru import logger

from keyboards.inline import main_menu_keyboard
from keyboards.keyboards import contact_keyboard
from services.database import write_to_db_start_person, is_user_registered
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
    write_to_db_start_person(data)  # Записываем данные в базу данных (пользователь который запустил бота)

    """
    Проверяем был ли уже зарегистрирован пользователь. Проверка происходит по таблице registered_persons. Проверяем по 
    id_telegram, так как он полностью уникальный в Telegram.
    """

    if is_user_registered(id_telegram):
        # Пользователь уже зарегистрирован — показываем главное меню
        logger.info(f"Пользователь {id_telegram} уже зарегистрирован, показываем главное меню")
        await message.answer(
            text=t("main-menu"),
            reply_markup=main_menu_keyboard(),
        )
        return

    logger.info(f"Отправка приветственного сообщения пользователю {message.from_user.id}")
    await message.answer(
        text=t("greet-message"),
        reply_markup=contact_keyboard()
    )


@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки "В главное меню"
    """
    logger.info(f"Получена команда /start от пользователя {callback.message.from_user.id}")

    id_telegram = callback.message.from_user.id
    first_name_telegram = callback.message.from_user.first_name
    last_name_telegram = callback.message.from_user.last_name
    username_telegram = callback.message.from_user.username

    data = {
        "id_telegram": id_telegram,
        "last_name_telegram": last_name_telegram,
        "first_name_telegram": first_name_telegram,
        "username_telegram": username_telegram
    }
    write_to_db_start_person(data)  # Записываем данные в базу данных (пользователь который запустил бота)

    """
    Проверяем был ли уже зарегистрирован пользователь. Проверка происходит по таблице registered_persons. Проверяем по 
    id_telegram, так как он полностью уникальный в Telegram.
    """

    if is_user_registered(id_telegram):
        # Пользователь уже зарегистрирован — показываем главное меню
        logger.info(f"Пользователь {id_telegram} уже зарегистрирован, показываем главное меню")
        await callback.message.answer(
            text=t("main-menu"),
            reply_markup=main_menu_keyboard(),
        )
        return

    logger.info(f"Отправка приветственного сообщения пользователю {callback.message.from_user.id}")
    await callback.message.answer(
        text=t("greet-message"),
        reply_markup=contact_keyboard()
    )
