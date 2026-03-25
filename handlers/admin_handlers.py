# -*- coding: utf-8 -*-
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from loguru import logger

from config import OWNER_ID
from keyboards.inline import admin_menu_keyboard

router = Router(name=__name__)


def is_admin(user_id: int) -> bool:
    """
    Проверка прав администратора

    :param user_id: ID пользователя в Telegram
    :return: True если администратор, False если нет
    """
    return user_id == OWNER_ID


@router.message(Command("admin"))
async def admin_command_handler(message: Message) -> None:
    """
    Обработчик команды /admin — открытие админ-панели
    """
    logger.info(f"Пользователь {message.from_user.id} запросил админ-панель")

    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для доступа к админ-панели")
        return

    await message.answer(
        text=(
            "🔧 <b>Админ-панель</b>\n\n"
            "Выберите раздел для управления ботом:"
        ),
        reply_markup=admin_menu_keyboard()
    )


@router.callback_query(F.data == "winners")
async def winners_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки 'Список победителей «Колеса подарков»'
    """
    logger.info(f"Администратор {callback.from_user.id} запросил список победителей")

    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав для доступа к этой информации", show_alert=True)
        return

    await callback.message.answer(
        text=(
            "🏆 <b>Список победителей «Колеса подарков»</b>\n\n"
            "🚧 Раздел в разработке...\n\n"
            "Здесь будет отображаться список всех победителей:\n"
            "• Telegram ID\n"
            "• Имя\n"
            "• Выигранный приз\n"
            "• Дата выигрыша"
        ),
        reply_markup=admin_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "users")
async def users_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки 'Список пользователей'
    """
    logger.info(f"Администратор {callback.from_user.id} запросил список пользователей")

    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав для доступа к этой информации", show_alert=True)
        return

    await callback.message.answer(
        text=(
            "👥 <b>Список пользователей</b>\n\n"
            "🚧 Раздел в разработке...\n\n"
            "Здесь будет отображаться список всех пользователей:\n"
            "• Telegram ID\n"
            "• Имя\n"
            "• Номер телефона\n"
            "• Дата регистрации\n"
            "• Бонусный баланс"
        ),
        reply_markup=admin_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "broadcast")
async def broadcast_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки 'Рассылка сообщений'
    """
    logger.info(f"Администратор {callback.from_user.id} запросил рассылку")

    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав для доступа к этой информации", show_alert=True)
        return

    await callback.message.answer(
        text=(
            "📨 <b>Рассылка сообщений</b>\n\n"
            "🚧 Раздел в разработке...\n\n"
            "Функционал рассылки будет включать:\n"
            "• Отправка текста\n"
            "• Отправка фото\n"
            "• Отправка видео\n"
            "• Добавление кнопок\n"
            "• Сегментация аудитории"
        ),
        reply_markup=admin_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "stats")
async def stats_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки 'Статистика пользователей'
    """
    logger.info(f"Администратор {callback.from_user.id} запросил статистику")

    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав для доступа к этой информации", show_alert=True)
        return

    await callback.message.answer(
        text=(
            "📊 <b>Статистика пользователей</b>\n\n"
            "🚧 Раздел в разработке...\n\n"
            "Здесь будет отображаться статистика:\n"
            "• Количество пользователей бота\n"
            "• Количество привязанных номеров\n"
            "• Начислено/списано/сгорело бонусов\n"
            "• Эффективность рассылок\n"
            "• Возврат клиентов"
        ),
        reply_markup=admin_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_back")
async def admin_back_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки 'В админ-панель'
    """
    logger.info(f"Администратор {callback.from_user.id} вернулся в админ-панель")

    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав для доступа к этой информации", show_alert=True)
        return

    await callback.message.edit_text(
        text=(
            "🔧 <b>Админ-панель</b>\n\n"
            "Выберите раздел для управления ботом:"
        ),
        reply_markup=admin_menu_keyboard()
    )
    await callback.answer()
