# -*- coding: utf-8 -*-
from aiogram import F, Router
from aiogram.types import CallbackQuery, BufferedInputFile
from loguru import logger
from config import OWNER_ID
from keyboards.inline import admin_menu_keyboard, back_to_admin_menu_keyboard
from services.database import get_start_persons, get_all_winners
from services.excel_service import write_users_to_excel, write_winners_to_excel

router = Router(name=__name__)

"""Для администратора и владельца боте не будет никаких команд, только инлайн кнопки"""


def is_admin(user_id: int) -> bool:
    """
    Проверка прав администратора

    :param user_id: ID пользователя в Telegram
    :return: True если администратор, False если нет
    """
    return user_id == OWNER_ID


@router.callback_query(F.data == "winners")
async def winners_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки 'Список победителей «Колеса подарков»'
    """
    logger.info(f"Администратор {callback.from_user.id} запросил список победителей")

    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав для доступа к этой информации", show_alert=True)
        return

    result = get_all_winners()  # получаем список победителей
    buffer = write_winners_to_excel(result)  # формируем Excel-файл

    await callback.message.answer_document(
        document=BufferedInputFile(
            buffer.read(),
            filename="Победители_Колеса_подарков.xlsx"
        ),
        caption="🏆 Список победителей «Колеса подарков»",
    )
    await callback.answer()


@router.callback_query(F.data == "users")
async def users_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки '👥 Список пользователей'
    """
    logger.info(f"Администратор {callback.from_user.id} запросил список пользователей")

    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав для доступа к этой информации", show_alert=True)
        return

    result = get_start_persons()  # получаем список пользователей
    buffer = write_users_to_excel(result)  # формируем Excel-файл

    await callback.message.answer_document(
        document=BufferedInputFile(
            buffer.read(),
            filename="Пользователи_запускавшие_телеграмм_бота.xlsx"
        ),
        caption="📊 Список пользователей бота",
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
        reply_markup=back_to_admin_menu_keyboard()
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
        reply_markup=back_to_admin_menu_keyboard()
    )
    await callback.answer()


"""Меню администратора"""


@router.callback_query(F.data == "admin_back")
async def admin_back_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки 'В админ-панель'
    """
    logger.info(f"Администратор {callback.from_user.id} вернулся в админ-панель")

    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав для доступа к этой информации", show_alert=True)
        return

    await callback.message.edit_message_text(
        text=(
            "🔧 <b>Админ-панель</b>\n\n"
            "Выберите раздел для управления ботом:"
        ),
        reply_markup=admin_menu_keyboard()
    )
    await callback.answer()
