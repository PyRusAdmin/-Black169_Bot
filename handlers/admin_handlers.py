# -*- coding: utf-8 -*-
import asyncio

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, BufferedInputFile, Message
from loguru import logger

from config import OWNER_IDS, bot
from keyboards.inline import (
    admin_menu_keyboard, back_to_admin_menu_keyboard, broadcast_type_keyboard, broadcast_confirm_keyboard,
)
from services.database import (
    get_start_persons, get_all_winners, get_all_user_ids, log_marketing_message, get_start_persons_count,
    get_registered_persons_count, get_broadcast_stats, delete_registered_person, delete_start_person,
    RegisteredPersons, get_registered_persons,
)
from services.excel_service import write_users_to_excel, write_winners_to_excel, write_registered_users_to_excel
from services.i18n import t
from services.quickresto_api import delete_customer, base_url, auth, headers
from states.user_states import BroadcastState, DeleteUserState

router = Router(name=__name__)

"""Для администратора и владельца боте не будет никаких команд, только инлайн кнопки"""


def is_admin(user_id: int) -> bool:
    """
    Проверка прав администратора

    :param user_id: ID пользователя в Telegram
    :return: True если администратор, False если нет
    """
    return user_id in OWNER_IDS


@router.callback_query(F.data == "admin_menu")
async def admin_menu_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки 'В меню администратора'
    """
    logger.info(f"Администратор {callback.from_user.id} запросил меню администратора")
    await callback.message.answer(
        text=t("main-menu-admin"),
        reply_markup=admin_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "winners")
async def winners_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки '🏆 Список победителей «Колеса подарков»'
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


@router.callback_query(F.data == "registered_users")
async def registered_users_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки 'Зарегистрированные пользователи' (кто отправил номер телефона)
    """
    logger.info(f"Администратор {callback.from_user.id} запросил список зарегистрированных пользователей")

    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав для доступа к этой информации", show_alert=True)
        return

    result = get_registered_persons()  # получаем список зарегистрированных пользователей

    if not result:
        await callback.message.answer(
            text="❌ Нет зарегистрированных пользователей\n\n"
                 "Никто ещё не отправил номер телефона.",
            reply_markup=back_to_admin_menu_keyboard()
        )
        await callback.answer()
        return

    buffer = write_registered_users_to_excel(result)  # формируем Excel-файл

    await callback.message.answer_document(
        document=BufferedInputFile(
            buffer.read(),
            filename="Зарегистрированные_пользователи.xlsx"
        ),
        caption=f"✅ Зарегистрированные пользователи ({len(result)} чел.)\n\n"
                f"Полная информация из QuickResto",
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
            "Выберите тип сообщения для рассылки:\n\n"
            "📝 <b>Текст</b> — отправка текстового сообщения\n"
            "🖼️ <b>Фото</b> — отправка фото с подписью\n"
            "🎥 <b>Видео</b> — отправка видео с подписью\n\n"
            "Сообщение будет отправлено всем пользователям, которые запускали бота."
        ),
        reply_markup=broadcast_type_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "broadcast_text")
async def broadcast_text_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик выбора типа рассылки — текст
    """
    logger.info(f"Администратор {callback.from_user.id} выбрал рассылку текстом")

    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав для доступа к этой информации", show_alert=True)
        return

    await state.set_state(BroadcastState.waiting_for_message_text)
    await callback.message.answer(
        text=(
            "📝 <b>Отправка текстового сообщения</b>\n\n"
            "Отправьте текст сообщения для рассылки.\n\n"
            "❌ Для отмены отправьте /cancel"
        )
    )
    await callback.answer()


@router.callback_query(F.data == "broadcast_photo")
async def broadcast_photo_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик выбора типа рассылки — фото
    """
    logger.info(f"Администратор {callback.from_user.id} выбрал рассылку фото")

    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав для доступа к этой информации", show_alert=True)
        return

    await state.set_state(BroadcastState.waiting_for_photo)
    await callback.message.answer(
        text=(
            "🖼️ <b>Отправка фото</b>\n\n"
            "Отправьте фото для рассылки.\n\n"
            "❌ Для отмены отправьте /cancel"
        )
    )
    await callback.answer()


@router.callback_query(F.data == "broadcast_video")
async def broadcast_video_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик выбора типа рассылки — видео
    """
    logger.info(f"Администратор {callback.from_user.id} выбрал рассылку видео")

    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав для доступа к этой информации", show_alert=True)
        return

    await state.set_state(BroadcastState.waiting_for_video)
    await callback.message.answer(
        text=(
            "🎥 <b>Отправка видео</b>\n\n"
            "Отправьте видео для рассылки.\n\n"
            "❌ Для отмены отправьте /cancel"
        )
    )
    await callback.answer()


@router.callback_query(F.data == "broadcast_cancel")
async def broadcast_cancel_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик отмены рассылки
    """
    logger.info(f"Администратор {callback.from_user.id} отменил рассылку")

    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав для доступа к этой информации", show_alert=True)
        return

    await state.clear()
    await callback.message.answer(
        text="❌ Рассылка отменена.",
        reply_markup=back_to_admin_menu_keyboard()
    )
    await callback.answer()


@router.message(Command("cancel"))
async def broadcast_cancel_command_handler(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды /cancel для отмены рассылки
    """
    logger.info(f"Пользователь {message.from_user.id} отправил /cancel")

    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активной рассылки для отмены.")
        return

    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для доступа к этой информации")
        return

    await state.clear()
    await message.answer(
        text="❌ Рассылка отменена.",
        reply_markup=back_to_admin_menu_keyboard()
    )


@router.message(BroadcastState.waiting_for_message_text, F.text)
async def broadcast_receive_text(message: Message, state: FSMContext) -> None:
    """
    Получение текста сообщения для рассылки
    """
    logger.info(f"Пользователь {message.from_user.id} отправил текст для рассылки")

    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для доступа к этой информации")
        return

    text = message.text
    await state.update_data(message_text=text, message_type="text")

    await message.answer(
        text=(
            "📨 <b>Подтверждение рассылки</b>\n\n"
            f"Текст сообщения:\n{text}\n\n"
            f"Количество получателей: {len(get_all_user_ids())}\n\n"
            "Вы уверены, что хотите отправить рассылку?"
        ),
        reply_markup=broadcast_confirm_keyboard()
    )


@router.message(BroadcastState.waiting_for_photo, F.photo)
async def broadcast_receive_photo(message: Message, state: FSMContext) -> None:
    """
    Получение фото для рассылки
    """
    logger.info(f"Пользователь {message.from_user.id} отправил фото для рассылки")

    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для доступа к этой информации")
        return

    photo_id = message.photo[-1].file_id
    caption = message.caption or ""
    await state.update_data(photo_id=photo_id, caption=caption, message_type="photo")

    await message.answer(
        text=(
            "📨 <b>Подтверждение рассылки</b>\n\n"
            f"Фото отправлено.\n"
            f"Подпись: {caption if caption else 'без подписи'}\n\n"
            f"Количество получателей: {len(get_all_user_ids())}\n\n"
            "Вы уверены, что хотите отправить рассылку?"
        ),
        reply_markup=broadcast_confirm_keyboard()
    )


@router.message(BroadcastState.waiting_for_video, F.video)
async def broadcast_receive_video(message: Message, state: FSMContext) -> None:
    """
    Получение видео для рассылки
    """
    logger.info(f"Пользователь {message.from_user.id} отправил видео для рассылки")

    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для доступа к этой информации")
        return

    video_id = message.video.file_id
    caption = message.caption or ""
    await state.update_data(video_id=video_id, caption=caption, message_type="video")

    await message.answer(
        text=(
            "📨 <b>Подтверждение рассылки</b>\n\n"
            f"Видео отправлено.\n"
            f"Подпись: {caption if caption else 'без подписи'}\n\n"
            f"Количество получателей: {len(get_all_user_ids())}\n\n"
            "Вы уверены, что хотите отправить рассылку?"
        ),
        reply_markup=broadcast_confirm_keyboard()
    )


@router.callback_query(F.data == "broadcast_confirm_send")
async def broadcast_confirm_send_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Подтверждение и отправка рассылки
    """
    logger.info(f"Администратор {callback.from_user.id} подтвердил отправку рассылки")

    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав для доступа к этой информации", show_alert=True)
        return

    data = await state.get_data()
    message_type = data.get("message_type")
    user_ids = get_all_user_ids()

    # Исключаем администраторов из рассылки (бот не может отправлять сообщения другим ботам)
    user_ids = [uid for uid in user_ids if uid not in OWNER_IDS]

    total_sent = 0
    total_blocked = 0

    await callback.message.answer(
        text=f"📨 <b>Начало рассылки...</b>\n\n"
             f"Всего получателей: {len(user_ids)}"
    )

    for user_id in user_ids:
        try:
            if message_type == "text":
                await bot.send_message(
                    chat_id=user_id,
                    text=data.get("message_text")
                )
            elif message_type == "photo":
                await bot.send_photo(
                    chat_id=user_id,
                    photo=data.get("photo_id"),
                    caption=data.get("caption")
                )
            elif message_type == "video":
                await bot.send_video(
                    chat_id=user_id,
                    video=data.get("video_id"),
                    caption=data.get("caption")
                )

            log_marketing_message(
                id_telegram=user_id,
                message_text=data.get("message_text", data.get("caption", "")),
                message_type=message_type
            )
            total_sent += 1

        except Exception as e:
            if "bot was blocked" in str(e).lower():
                total_blocked += 1
                log_marketing_message(
                    id_telegram=user_id,
                    message_text="Blocked",
                    message_type="blocked"
                )
            logger.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

        # Небольшая задержка для избежания лимитов Telegram
        await asyncio.sleep(0.05)

    await state.clear()

    await callback.message.answer(
        text=(
            f"✅ <b>Рассылка завершена!</b>\n\n"
            f"📊 <b>Статистика:</b>\n"
            f"• Всего получателей: {len(user_ids)}\n"
            f"• Успешно отправлено: {total_sent}\n"
            f"• Заблокировали бота: {total_blocked}\n"
            f"• Не доставлено: {len(user_ids) - total_sent - total_blocked}"
        ),
        reply_markup=back_to_admin_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "stats")
async def stats_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки '📊 Статистика пользователей'
    """
    logger.info(f"Администратор {callback.from_user.id} запросил статистику")

    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав для доступа к этой информации", show_alert=True)
        return

    # Получаем статистику
    total_users = get_start_persons_count()  # Пользователи, запустившие бота
    registered_users = get_registered_persons_count()  # Привязавшие номер телефона
    broadcast_stats = get_broadcast_stats()  # Статистика по рассылкам

    await callback.message.answer(
        text=(
            "📊 <b>Статистика пользователей</b>\n\n"
            f"👥 <b>Пользователи:</b>\n"
            f"• Запустили бота: <b>{total_users}</b>\n"
            f"• Привязали номер телефона: <b>{registered_users}</b>\n\n"
            f"📨 <b>Рассылки:</b>\n"
            f"• Всего отправлено сообщений: <b>{broadcast_stats['total_messages']}</b>\n"
            f"  └ Текстовых: {broadcast_stats['text_count']}\n"
            f"  └ С фото: {broadcast_stats['photo_count']}\n"
            f"  └ С видео: {broadcast_stats['video_count']}\n"
            f"• Уникальных получателей: <b>{broadcast_stats['unique_users']}</b>\n"
            f"• Заблокировали бота: <b>{broadcast_stats['blocked_count']}</b>\n\n"
            f"ℹ️ <i>Данные актуальны на текущий момент</i>"
        ),
        reply_markup=back_to_admin_menu_keyboard()
    )
    await callback.answer()


"""Удаление клиента из QuickResto"""


@router.callback_query(F.data == "delete_user")
async def delete_user_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик кнопки 'Удалить клиента'
    """
    logger.info(f"Администратор {callback.from_user.id} запросил удаление клиента")
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав для доступа к данной информации", show_alert=True)
        return

    await state.set_state(DeleteUserState.waiting_for_user_id)

    await callback.message.answer(
        text="Введите ID клиента QuickResto:",
        reply_markup=back_to_admin_menu_keyboard()
    )
    await callback.answer()


@router.message(F.text, StateFilter(DeleteUserState.waiting_for_user_id))
async def delete_user_id_handler(message: Message, state: FSMContext) -> None:
    """
    Обработчик ввода ID клиента QuickResto
    """
    id_user = message.text

    logger.info(f"Администратор {message.from_user.id} ввел ID клиента QuickResto: {id_user}")

    # Получаем ID пользователя в Telegram по ID QuickResto
    user = RegisteredPersons.get_or_none(RegisteredPersons.id_quickresto == int(id_user))
    id_telegram = user.id_telegram if user else None

    # Удаляем клиента QuickResto
    delete_customer(
        customer_id=int(id_user),
        base_url=base_url,
        auth=auth,
        headers=headers
    )

    # Удаляем из базы данных registered_persons
    if id_telegram:
        delete_registered_person(id_telegram)
        # Удаляем из базы данных start_persons
        delete_start_person(id_telegram)

    await message.answer(
        text=f"✅ Клиент QuickResto с ID <b>{id_user}</b> успешно удален\n\n"
             f"Из базы данных бота: {'удалён' if id_telegram else 'не найден'}",
        reply_markup=back_to_admin_menu_keyboard()
    )
    await state.clear()

"""Меню администратора"""


@router.callback_query(F.data == "admin_back")
async def admin_back_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик кнопки 'В админ-панель'
    """
    logger.info(f"Администратор {callback.from_user.id} вернулся в админ-панель")

    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав для доступа к этой информации", show_alert=True)
        return

    # Очищаем состояние FSM если есть активная рассылка
    await state.clear()

    await callback.message.edit_text(
        text=(
            "🔧 <b>Админ-панель</b>\n\n"
            "Выберите раздел для управления ботом:"
        ),
        reply_markup=admin_menu_keyboard()
    )
    await callback.answer()
