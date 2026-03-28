# -*- coding: utf-8 -*-
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from loguru import logger

from config import OWNER_IDS
from keyboards.inline import main_menu_keyboard, admin_menu_keyboard, main_menu_keyboard_admin
from keyboards.keyboards import contact_keyboard
from services.database import write_to_db_start_person, is_user_registered
from services.i18n import t

router = Router(name=__name__)

"""
Обработчик команды /start (общая команда для всех пользователей). В зависимости от того, является ли пользователь 
владельцем бота, он получает разные клавиатуры.
"""


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

    # Проверяем, является ли пользователь владельцем бота. ID пользователя должен быть в списке OWNER_IDS в файле .env
    if id_telegram in OWNER_IDS:
        logger.info(f"Пользователь {id_telegram} является владельцем бота")
        await message.answer(
            text=t("main-menu"),
            reply_markup=main_menu_keyboard_admin(),
        )
        return

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
        # Скрываем reply-клавиатуру и показываем inline-меню одним сообщением
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


"""Кнопка возврата в главное меню для обычных пользователей"""


@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки "В главное меню"
    """
    logger.info(f"Пользователь {callback.from_user.id} нажал 'В главное меню'")

    id_telegram = callback.from_user.id
    first_name_telegram = callback.from_user.first_name
    last_name_telegram = callback.from_user.last_name
    username_telegram = callback.from_user.username

    if id_telegram in OWNER_IDS:
        logger.info(f"Пользователь {id_telegram} является владельцем бота")
        await callback.message.edit_text(
            text=t("main-menu"),
            reply_markup=admin_menu_keyboard(),
        )
        await callback.answer()
        return

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
        await callback.message.edit_text(
            text=t("main-menu"),
            reply_markup=main_menu_keyboard(),
        )
        await callback.answer()
        return

    logger.info(f"Отправка приветственного сообщения пользователю {callback.from_user.id}")
    # Скрываем reply-клавиатуру и показываем приветственное сообщение
    await callback.message.edit_text(
        text=t("greet-message"),
        reply_markup=contact_keyboard(),
    )
    await callback.answer()
