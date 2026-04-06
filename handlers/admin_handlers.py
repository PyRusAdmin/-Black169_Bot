import asyncio

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from config import OWNER_IDS, bot
from keyboards.keyboards import (
    admin_menu_keyboard, admins_menu_keyboard, back_to_admin_menu_keyboard, back_to_admins_menu_keyboard,
    broadcast_confirm_keyboard, broadcast_type_keyboard,
)
from services.database import (
    RegisteredPersons, add_admin as db_add_admin, delete_registered_person, delete_start_person, get_all_admins,
    get_all_user_ids, get_all_winners, get_broadcast_stats, get_client_levels_stats, get_registered_persons,
    get_registered_persons_count, get_start_persons, get_start_persons_count, is_admin_in_db, is_owner_in_db,
    log_marketing_message, remove_admin as db_remove_admin,
)
from services.excel_service import (
    write_registered_users_to_excel, write_users_to_excel, write_winners_to_excel,
)
from services.i18n import t
from services.quickresto_api import delete_customer, print_client_info
from states.user_states import (
    AdminManagementState, BroadcastState, DeleteUserState, SearchUserState,
)
from utils.logger import logger

router = Router(name=__name__)

"""Для администратора и владельца боте не будет никаких команд, только инлайн кнопки"""


def is_admin(user_id: int) -> bool:
    """
    Проверка прав администратора (OWNER_IDS из .env + из БД)

    :param user_id: ID пользователя в Telegram
    :return: True если администратор, False если нет
    """
    if user_id in OWNER_IDS:
        return True
    return is_admin_in_db(user_id)


def is_owner(user_id: int) -> bool:
    """
    Проверка прав владельца

    :param user_id: ID пользователя в Telegram
    :return: True если владелец, False если нет
    """
    if user_id in OWNER_IDS:
        return True
    return is_owner_in_db(user_id)


@router.callback_query(F.data == "admin_menu")
async def admin_menu_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки 'В меню администратора'
    """
    logger.info(f"Администратор {callback.from_user.id} запросил меню администратора")
    await callback.message.answer(
        text=t("main-menu-admin"), reply_markup=admin_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "winners")
async def winners_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки '🏆 Список победителей «Колеса подарков»'
    """
    logger.info(f"Администратор {callback.from_user.id} запросил список победителей")

    if not is_admin(callback.from_user.id):
        await callback.answer(t("no-admin-permission"), show_alert=True)
        return

    result = get_all_winners()  # получаем список победителей
    buffer = write_winners_to_excel(result)  # формируем Excel-файл

    await callback.message.answer_document(
        document=BufferedInputFile(
            buffer.read(), filename="Победители_Колеса_подарков.xlsx"
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
        await callback.answer(t("no-admin-permission"), show_alert=True)
        return

    result = get_start_persons()  # получаем список пользователей
    buffer = write_users_to_excel(result)  # формируем Excel-файл

    await callback.message.answer_document(
        document=BufferedInputFile(
            buffer.read(), filename="Пользователи_запускавшие_телеграмм_бота.xlsx"
        ),
        caption="📊 Список пользователей бота",
    )
    await callback.answer()


@router.callback_query(F.data == "registered_users")
async def registered_users_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки 'Зарегистрированные пользователи' (кто отправил номер телефона)
    """
    logger.info(
        f"Администратор {callback.from_user.id} запросил список зарегистрированных пользователей"
    )

    if not is_admin(callback.from_user.id):
        await callback.answer(t("no-admin-permission"), show_alert=True)
        return

    result = (
        get_registered_persons()
    )  # получаем список зарегистрированных пользователей

    if not result:
        await callback.message.answer(
            text=t("delete-no-registered-users"),
            reply_markup=back_to_admin_menu_keyboard(),
        )
        await callback.answer()
        return

    buffer = write_registered_users_to_excel(result)  # формируем Excel-файл

    await callback.message.answer_document(
        document=BufferedInputFile(
            buffer.read(), filename="Зарегистрированные_пользователи.xlsx"
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
        await callback.answer(t("no-admin-permission"), show_alert=True)
        return

    await callback.message.answer(
        text=t("broadcast-title"), reply_markup=broadcast_type_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "broadcast_text")
async def broadcast_text_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик выбора типа рассылки — текст
    """
    logger.info(f"Администратор {callback.from_user.id} выбрал рассылку текстом")

    if not is_admin(callback.from_user.id):
        await callback.answer(t("no-admin-permission"), show_alert=True)
        return

    await state.set_state(BroadcastState.waiting_for_message_text)
    await callback.message.answer(text=t("broadcast-text-title"))
    await callback.answer()


@router.callback_query(F.data == "broadcast_photo")
async def broadcast_photo_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик выбора типа рассылки — фото
    """
    logger.info(f"Администратор {callback.from_user.id} выбрал рассылку фото")

    if not is_admin(callback.from_user.id):
        await callback.answer(t("no-admin-permission"), show_alert=True)
        return

    await state.set_state(BroadcastState.waiting_for_photo)
    await callback.message.answer(text=t("broadcast-photo-title"))
    await callback.answer()


@router.callback_query(F.data == "broadcast_video")
async def broadcast_video_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик выбора типа рассылки — видео
    """
    logger.info(f"Администратор {callback.from_user.id} выбрал рассылку видео")

    if not is_admin(callback.from_user.id):
        await callback.answer(t("no-admin-permission"), show_alert=True)
        return

    await state.set_state(BroadcastState.waiting_for_video)
    await callback.message.answer(text=t("broadcast-video-title"))
    await callback.answer()


@router.callback_query(F.data == "broadcast_cancel")
async def broadcast_cancel_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик отмены рассылки
    """
    logger.info(f"Администратор {callback.from_user.id} отменил рассылку")

    if not is_admin(callback.from_user.id):
        await callback.answer(t("no-admin-permission"), show_alert=True)
        return

    await state.clear()
    await callback.message.answer(
        text=t("broadcast-cancelled"), reply_markup=back_to_admin_menu_keyboard()
    )
    await callback.answer()


@router.message(Command("cancel"))
async def broadcast_cancel_command_handler(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды /cancel для отмены рассылки или поиска
    """
    logger.info(f"Пользователь {message.from_user.id} отправил /cancel")

    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активной операции для отмены.")
        return

    await state.clear()
    await message.answer(
        text="❌ Операция отменена.", reply_markup=back_to_admin_menu_keyboard()
    )


@router.message(BroadcastState.waiting_for_message_text, F.text)
async def broadcast_receive_text(message: Message, state: FSMContext) -> None:
    """
    Получение текста сообщения для рассылки
    """
    logger.info(f"Пользователь {message.from_user.id} отправил текст для рассылки")

    text = message.text
    await state.update_data(message_text=text, message_type="text")

    await message.answer(
        text=t("broadcast-confirm-title", text=text, count=len(get_all_user_ids())),
        reply_markup=broadcast_confirm_keyboard(),
    )


@router.message(BroadcastState.waiting_for_photo, F.photo)
async def broadcast_receive_photo(message: Message, state: FSMContext) -> None:
    """
    Получение фото для рассылки
    """
    logger.info(f"Пользователь {message.from_user.id} отправил фото для рассылки")

    photo_id = message.photo[-1].file_id
    caption = message.caption or ""
    await state.update_data(photo_id=photo_id, caption=caption, message_type="photo")

    await message.answer(
        text=t(
            "broadcast-photo-confirm-title",
            caption=caption if caption else "без подписи",
            count=len(get_all_user_ids()),
        ),
        reply_markup=broadcast_confirm_keyboard(),
    )


@router.message(BroadcastState.waiting_for_video, F.video)
async def broadcast_receive_video(message: Message, state: FSMContext) -> None:
    """
    Получение видео для рассылки
    """
    logger.info(f"Пользователь {message.from_user.id} отправил видео для рассылки")

    video_id = message.video.file_id
    caption = message.caption or ""
    await state.update_data(video_id=video_id, caption=caption, message_type="video")

    await message.answer(
        text=t(
            "broadcast-video-confirm-title",
            caption=caption if caption else "без подписи",
            count=len(get_all_user_ids()),
        ),
        reply_markup=broadcast_confirm_keyboard(),
    )


@router.callback_query(F.data == "broadcast_confirm_send")
async def broadcast_confirm_send_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Подтверждение и отправка рассылки
    """
    logger.info(f"Администратор {callback.from_user.id} подтвердил отправку рассылки")

    if not is_admin(callback.from_user.id):
        await callback.answer(t("no-admin-permission"), show_alert=True)
        return

    data = await state.get_data()
    message_type = data.get("message_type")
    user_ids = get_all_user_ids()

    # Исключаем администраторов из рассылки (бот не может отправлять сообщения другим ботам)
    user_ids = [uid for uid in user_ids if uid not in OWNER_IDS]

    total_sent = 0
    total_blocked = 0

    await callback.message.answer(text=t("broadcast-start", count=len(user_ids)))

    for user_id in user_ids:
        try:
            if message_type == "text":
                await bot.send_message(chat_id=user_id, text=data.get("message_text"))
            elif message_type == "photo":
                await bot.send_photo(
                    chat_id=user_id,
                    photo=data.get("photo_id"),
                    caption=data.get("caption"),
                )
            elif message_type == "video":
                await bot.send_video(
                    chat_id=user_id,
                    video=data.get("video_id"),
                    caption=data.get("caption"),
                )

            log_marketing_message(
                id_telegram=user_id,
                message_text=data.get("message_text", data.get("caption", "")),
                message_type=message_type,
            )
            total_sent += 1

        except Exception as e:
            if "bot was blocked" in str(e).lower():
                total_blocked += 1
                log_marketing_message(
                    id_telegram=user_id, message_text="Blocked", message_type="blocked"
                )
            logger.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

        # Небольшая задержка для избежания лимитов Telegram
        await asyncio.sleep(0.05)

    await state.clear()

    await callback.message.answer(
        text=t(
            "broadcast-completed",
            total=len(user_ids),
            sent=total_sent,
            blocked=total_blocked,
            failed=len(user_ids) - total_sent - total_blocked,
        ),
        reply_markup=back_to_admin_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "stats")
async def stats_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки '📊 Статистика пользователей'
    """
    logger.info(f"Администратор {callback.from_user.id} запросил статистику")

    if not is_admin(callback.from_user.id):
        await callback.answer(t("no-admin-permission"), show_alert=True)
        return

    # Получаем статистику
    total_users = get_start_persons_count()  # Пользователи, запустившие бота
    registered_users = get_registered_persons_count()  # Привязавшие номер телефона
    broadcast_stats = get_broadcast_stats()  # Статистика по рассылкам
    client_levels_stats = get_client_levels_stats()  # Статистика по уровням в БД

    # Получаем статистику по всем клиентам QuickResto из JSON
    quickresto_stats = get_quickresto_clients_stats()

    # Формируем текст статистики по уровням в БД
    levels_text = ""
    for level in ["Black", "Gold", "Silver", "Bronze"]:
        level_data = client_levels_stats["levels"].get(level, {})
        count = level_data.get("count", 0)
        percent = level_data.get("percent", 0)
        emoji = {"Black": "💎", "Gold": "🥇", "Silver": "🥈", "Bronze": "🥉"}.get(
            level, "📊"
        )
        levels_text += f"{emoji} <b>{level}</b>: {count} чел. ({percent}%)\n"

    # Формируем текст статистики по QuickResto
    qr_levels_text = ""
    qr_level_dist = quickresto_stats.get("level_distribution", {})
    qr_total = quickresto_stats.get("total", 0)
    for level in ["Black", "Gold", "Silver", "Bronze"]:
        count = qr_level_dist.get(level, 0)
        percent = round(count / qr_total * 100, 1) if qr_total > 0 else 0
        emoji = {"Black": "💎", "Gold": "🥇", "Silver": "🥈", "Bronze": "🥉"}.get(
            level, "📊"
        )
        qr_levels_text += f"{emoji} <b>{level}</b>: {count} чел. ({percent}%)\n"

    await callback.message.answer(
        text=(
            f"📊 <b>Статистика пользователей</b>\n\n"
            f"👥 Пользователей запустили бота: <b>{total_users}</b>\n"
            f"✅ Зарегистрировали номер: <b>{registered_users}</b>\n\n"
            f"📈 <b>Уровни клиентов (в боте):</b>\n"
            f"{levels_text}\n"
            f"📭 Без уровня: {client_levels_stats['no_level']} чел.\n\n"
            f"🏪 <b>Вся база QuickResto ({qr_total} клиентов):</b>\n"
            f"{qr_levels_text}\n"
            f"📨 <b>Рассылки:</b>\n"
            f"Всего сообщений: {broadcast_stats['total_messages']}\n"
            f"• Текстом: {broadcast_stats['text_count']}\n"
            f"• С фото: {broadcast_stats['photo_count']}\n"
            f"• С видео: {broadcast_stats['video_count']}\n"
            f"📖 Прочитано: {broadcast_stats['unique_users']}\n"
            f"🚫 Заблокировано: {broadcast_stats['blocked_count']}"
        ),
        reply_markup=back_to_admin_menu_keyboard(),
    )
    await callback.answer()


def get_quickresto_clients_stats() -> dict:
    """
    Получение статистики по всем клиентам QuickResto из JSON файла.

    :return: Статистика по уровням клиентов
    """
    import json
    from pathlib import Path

    json_path = Path("data/clients_levels.json")

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            clients_data = json.load(f)

        total = len(clients_data)
        level_distribution = {}

        for client in clients_data:
            level = client.get("level", "Unknown")
            level_distribution[level] = level_distribution.get(level, 0) + 1

        return {
            "total": total,
            "level_distribution": level_distribution,
        }

    except FileNotFoundError:
        logger.warning("Файл clients_levels.json не найден")
        return {"total": 0, "level_distribution": {}}
    except Exception as e:
        logger.exception(f"Ошибка при чтении статистики QuickResto: {e}")
        return {"total": 0, "level_distribution": {}}


"""Анализ и синхронизация клиентов"""


@router.callback_query(F.data == "analyze_clients")
async def analyze_clients_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки 'Анализ и синхронизация клиентов'
    Запускает полный цикл анализа, нормализации телефонов, сохранения в JSON и синхронизации с БД.
    """
    logger.info(
        f"Администратор {callback.from_user.id} запустил анализ и синхронизацию клиентов"
    )

    if not is_admin(callback.from_user.id):
        await callback.answer(t("no-admin-permission"), show_alert=True)
        return

    await callback.answer("⏳ Запуск анализа клиентов...")

    try:
        from services.quickresto_api import analyze_and_sync_clients

        # Запускаем анализ и синхронизацию
        result = analyze_and_sync_clients()

        # Формируем отчет
        level_dist = result.get("level_distribution", {})
        db_stats = result.get("db_sync_stats", {})

        report = (
            f"✅ <b>Анализ и синхронизация клиентов завершены!</b>\n\n"
            f"📊 <b>Результаты:</b>\n"
            f"• Всего клиентов: {result.get('total_clients', 0)}\n"
            f"• JSON обновлен: {'✅' if result.get('json_saved') else '❌'}\n\n"
            f"📈 <b>Распределение по уровням:</b>\n"
        )

        emojis = {"Black": "💎", "Gold": "🥇", "Silver": "🥈", "Bronze": "🥉"}
        for level in ["Black", "Gold", "Silver", "Bronze"]:
            count = level_dist.get(level, 0)
            emoji = emojis.get(level, "📊")
            report += f"{emoji} {level}: {count} чел.\n"

        report += (
            f"\n🔄 <b>Синхронизация с БД:</b>\n"
            f"• Обновлено: {db_stats.get('updated', 0)}\n"
            f"• Не найдено: {db_stats.get('not_found', 0)}\n"
            f"• Ошибок: {db_stats.get('errors', 0)}\n\n"
            f"🕒 <b>Время выполнения:</b> {result.get('timestamp', '—')}"
        )

        await callback.message.answer(
            text=report,
            reply_markup=back_to_admin_menu_keyboard(),
        )

    except Exception as e:
        logger.exception(f"Ошибка при анализе клиентов: {e}")
        await callback.message.answer(
            text=f"❌ <b>Ошибка при анализе клиентов:</b>\n\n{str(e)}",
            reply_markup=back_to_admin_menu_keyboard(),
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
        await callback.answer(t("no-admin-permission"), show_alert=True)
        return

    await state.set_state(DeleteUserState.waiting_for_user_id)

    await callback.message.answer(
        text=t("delete-user-enter-id"), reply_markup=back_to_admin_menu_keyboard()
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
    delete_customer(customer_id=int(id_user))

    # Удаляем из базы данных registered_persons
    if id_telegram:
        delete_registered_person(id_telegram)
        # Удаляем из базы данных start_persons
        delete_start_person(id_telegram)

    await message.answer(
        text=t(
            "delete-user-success",
            user_id=id_user,
            status="удалён" if id_telegram else "не найден",
        ),
        reply_markup=back_to_admin_menu_keyboard(),
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
        await callback.answer(t("no-admin-permission"), show_alert=True)
        return

    # Очищаем состояние FSM если есть активная рассылка
    await state.clear()

    # Пробуем отредактировать сообщение, а если не получится (документ) — отправляем новое
    try:
        await callback.message.edit_text(
            text=t("admin-panel"), reply_markup=admin_menu_keyboard()
        )
    except Exception:
        await callback.message.answer(
            text=t("admin-panel"), reply_markup=admin_menu_keyboard()
        )
    await callback.answer()


@router.callback_query(F.data == "search_user")
async def search_user_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик кнопки '🔍 Поиск пользователя по номеру телефона'
    """
    logger.info(
        f"Администратор {callback.from_user.id} запросил поиск пользователя по номеру телефона"
    )

    if not is_admin(callback.from_user.id):
        await callback.answer(t("no-admin-permission"), show_alert=True)
        return

    # Очищаем состояние FSM если есть активная рассылка
    await state.clear()
    await state.set_state(SearchUserState.waiting_for_phone_number)

    await callback.message.answer(
        text=t("search-user-enter-phone-number"),
        reply_markup=back_to_admin_menu_keyboard(),
    )
    await callback.answer()


@router.message(F.text, StateFilter(SearchUserState.waiting_for_phone_number))
async def search_user_phone_number_handler(message: Message, state: FSMContext) -> None:
    """
    Обработчик ввода номера телефона пользователя
    """
    phone_number = message.text.strip()

    logger.info(
        f"Администратор {message.from_user.id} ввел номер телефона: {phone_number}"
    )

    # Проверяем формат номера (должен быть 79999999999)
    if (
            not phone_number.isdigit()
            or len(phone_number) != 11
            or not phone_number.startswith("7")
    ):
        await message.answer(
            text=(
                "❌ <b>Неверный формат номера</b>\n\n"
                "Номер должен быть в формате <code>79999999999</code> (11 цифр, начиная с 7).\n\n"
                "Попробуйте снова или отправьте /cancel для отмены."
            ),
            reply_markup=back_to_admin_menu_keyboard(),
        )
        return

    try:
        # Получаем информацию о клиенте
        data = print_client_info(phone_number)

        if data:
            # Формируем красивое сообщение
            first_name = data.get("firstName", "Не указано")
            last_name = data.get("lastName", "Не указано")
            client_id = data.get("client_id", "Не указано")
            phone = data.get("phone", phone_number)

            # Пробуем найти Telegram ID в базе
            from services.database import RegisteredPersons

            user = RegisteredPersons.get_or_none(
                RegisteredPersons.id_quickresto == client_id
            )
            telegram_id = user.id_telegram if user else "Не привязан"

            await message.answer(
                text=(
                    "✅ <b>Пользователь найден!</b>\n\n"
                    "👤 <b>Информация о клиенте:</b>\n"
                    f"• Имя: <b>{first_name} {last_name}</b>\n"
                    f"• Телефон: <code>{phone}</code>\n"
                    f"• ID в QuickResto: <code>{client_id}</code>\n"
                    f"• ID в Telegram: <code>{telegram_id}</code>\n\n"
                ),
                reply_markup=back_to_admin_menu_keyboard(),
            )
        else:
            await message.answer(
                text=t("search-user-not-found", phone=phone_number),
                reply_markup=back_to_admin_menu_keyboard(),
            )

    except Exception as e:
        logger.exception(f"Ошибка при поиске пользователя: {e}")
        await message.answer(
            text=(
                "⚠️ <b>Ошибка поиска</b>\n\n"
                "Не удалось получить информацию о клиенте.\n\n"
                "Проверьте правильность номера телефона и попробуйте снова."
            ),
            reply_markup=back_to_admin_menu_keyboard(),
        )

    # Очищаем состояние FSM
    await state.clear()


"""Управление администраторами"""


@router.callback_query(F.data == "admins_menu")
async def admins_menu_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки 'Управление администраторами'
    Только для владельцев
    """
    logger.info(
        f"Администратор {callback.from_user.id} запросил меню управления администраторами"
    )

    if not is_owner(callback.from_user.id):
        await callback.answer(
            "❌ Только владелец может управлять администраторами", show_alert=True
        )
        return

    admins = get_all_admins()

    admins_text = ""
    if admins:
        for admin in admins:
            role_emoji = "👑" if admin["role"] == "owner" else "🔧"
            name = admin["full_name"] or "Без имени"
            username = f"@{admin['username']}" if admin["username"] else "нет username"
            admins_text += f"{role_emoji} <b>{name}</b> ({username})\n   ID: <code>{admin['id_telegram']}</code>\n\n"
    else:
        admins_text = "Администраторов нет.\n\n"

    await callback.message.answer(
        text=(
            f"👥 <b>Управление администраторами</b>\n\n"
            f"📋 <b>Текущие администраторы:</b>\n{admins_text}"
            f"Выберите действие:"
        ),
        reply_markup=admins_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin_add")
async def admin_add_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик кнопки 'Добавить администратора'
    Только для владельцев
    """
    logger.info(f"Владелец {callback.from_user.id} начал добавление администратора")

    if not is_owner(callback.from_user.id):
        await callback.answer(
            "❌ Только владелец может добавлять администраторов", show_alert=True
        )
        return

    await state.set_state(AdminManagementState.waiting_for_admin_id)

    await callback.message.answer(
        text=(
            "➕ <b>Добавление администратора</b>\n\n"
            "Отправьте Telegram ID пользователя, которого хотите сделать администратором.\n\n"
            "📱 Формат: <code>123456789</code>\n\n"
            "❌ Для отмены отправьте /cancel"
        ),
        reply_markup=back_to_admins_menu_keyboard(),
    )
    await callback.answer()


async def admin_add_id_handler(message: Message, state: FSMContext) -> None:
    """
    Обработчик ввода ID нового администратора (вызывается из admin_action_handler)
    """
    if not is_owner(message.from_user.id):
        await message.answer("❌ Только владелец может добавлять администраторов")
        await state.clear()
        return

    admin_id_text = message.text.strip()

    # Проверяем что это число
    if not admin_id_text.isdigit():
        await message.answer(
            text="❌ ID должен быть числом. Попробуйте снова или отправьте /cancel",
            reply_markup=back_to_admins_menu_keyboard(),
        )
        return

    admin_id = int(admin_id_text)

    # Нельзя добавить самого себя
    if admin_id == message.from_user.id:
        await message.answer(
            text="❌ Вы уже являетесь владельцем. Нельзя добавить самого себя.",
            reply_markup=back_to_admins_menu_keyboard(),
        )
        await state.clear()
        return

    # Проверяем что пользователь запускал бота
    from services.database import StartPersons

    user_in_db = StartPersons.get_or_none(StartPersons.id_telegram == admin_id)
    username = user_in_db.username_telegram if user_in_db else None
    full_name = None
    if user_in_db:
        full_name = f"{user_in_db.first_name_telegram or ''} {user_in_db.last_name_telegram or ''}".strip()

    # Добавляем администратора
    result = db_add_admin(
        id_telegram=admin_id,
        added_by=message.from_user.id,
        username=username,
        full_name=full_name or "Администратор",
        role="admin",
    )

    if result["success"]:
        await message.answer(
            text=(
                f"✅ <b>Администратор добавлен!</b>\n\n"
                f"👤 ID: <code>{admin_id}</code>\n"
                f"📛 Имя: {full_name or 'Неизвестно'}\n"
                f"📱 Username: @{username or 'нет'}\n\n"
                f"Теперь этот пользователь имеет доступ к админ-панели."
            ),
            reply_markup=admins_menu_keyboard(),
        )
    else:
        await message.answer(
            text=f"❌ {result['message']}",
            reply_markup=admins_menu_keyboard(),
        )

    await state.clear()


@router.callback_query(F.data == "admin_list")
async def admin_list_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки 'Список администраторов'
    """
    logger.info(
        f"Администратор {callback.from_user.id} запросил список администраторов"
    )

    if not is_admin(callback.from_user.id):
        await callback.answer(t("no-admin-permission"), show_alert=True)
        return

    admins = get_all_admins()

    if not admins:
        await callback.message.answer(
            text="📋 <b>Список администраторов</b>\n\nАдминистраторов нет.",
            reply_markup=back_to_admins_menu_keyboard(),
        )
        await callback.answer()
        return

    report = "📋 <b>Список администраторов</b>\n\n"

    for admin in admins:
        role_emoji = "👑" if admin["role"] == "owner" else "🔧"
        role_name = "Владелец" if admin["role"] == "owner" else "Администратор"
        name = admin["full_name"] or "Без имени"
        username = f"@{admin['username']}" if admin["username"] else "нет username"
        added_at = (
            admin["added_at"].strftime("%d.%m.%Y %H:%M") if admin["added_at"] else "—"
        )

        report += (
            f"{role_emoji} <b>{name}</b>\n"
            f"   Роль: {role_name}\n"
            f"   ID: <code>{admin['id_telegram']}</code>\n"
            f"   Username: {username}\n"
            f"   Добавлен: {added_at}\n\n"
        )

    await callback.message.answer(
        text=report,
        reply_markup=back_to_admins_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin_remove")
async def admin_remove_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик кнопки 'Удалить администратора'
    Только для владельцев
    """
    logger.info(f"Владелец {callback.from_user.id} начал удаление администратора")

    if not is_owner(callback.from_user.id):
        await callback.answer(
            "❌ Только владелец может удалять администраторов", show_alert=True
        )
        return

    # Показываем список администраторов для удаления
    admins = get_all_admins()

    # Фильтруем только админов (не владельцев), которых можно удалить
    removable_admins = [a for a in admins if a["role"] != "owner"]

    if not removable_admins:
        await callback.message.answer(
            text="🗑️ <b>Удаление администратора</b>\n\nНет администраторов для удаления.",
            reply_markup=back_to_admins_menu_keyboard(),
        )
        await callback.answer()
        return

    admins_list = ""
    for admin in removable_admins:
        name = admin["full_name"] or "Без имени"
        admins_list += f"• <code>{admin['id_telegram']}</code> — {name}\n"

    await callback.message.answer(
        text=(
            f"🗑️ <b>Удаление администратора</b>\n\n"
            f"Текущие администраторы:\n{admins_list}\n"
            f"Отправьте ID администратора для удаления.\n\n"
            f"❌ Для отмены отправьте /cancel"
        ),
        reply_markup=back_to_admins_menu_keyboard(),
    )

    # Используем то же состояние, но с другим флагом в state данных
    await state.set_state(AdminManagementState.waiting_for_admin_id)
    await state.update_data(action="remove")
    await callback.answer()


# Переопределяем обработчик для удаления (через data action)
@router.message(F.text, StateFilter(AdminManagementState.waiting_for_admin_id))
async def admin_action_handler(message: Message, state: FSMContext) -> None:
    """
    Универсальный обработчик ввода ID (добавление или удаление)
    """
    data = await state.get_data()
    action = data.get("action", "add")

    if action == "remove":
        await admin_remove_id_handler(message, state)
    else:
        await admin_add_id_handler(message, state)


async def admin_remove_id_handler(message: Message, state: FSMContext) -> None:
    """
    Обработчик ввода ID администратора для удаления
    """
    if not is_owner(message.from_user.id):
        await message.answer("❌ Только владелец может удалять администраторов")
        await state.clear()
        return

    admin_id_text = message.text.strip()

    if not admin_id_text.isdigit():
        await message.answer(
            text="❌ ID должен быть числом. Попробуйте снова или отправьте /cancel",
            reply_markup=back_to_admins_menu_keyboard(),
        )
        return

    admin_id = int(admin_id_text)

    # Нельзя удалить самого себя
    if admin_id == message.from_user.id:
        await message.answer(
            text="❌ Нельзя удалить самого себя.",
            reply_markup=admins_menu_keyboard(),
        )
        await state.clear()
        return

    result = db_remove_admin(admin_id)

    if result:
        await message.answer(
            text=f"✅ Администратор <code>{admin_id}</code> удалён.",
            reply_markup=admins_menu_keyboard(),
        )
    else:
        await message.answer(
            text=f"❌ Администратор <code>{admin_id}</code> не найден или является владельцем.",
            reply_markup=admins_menu_keyboard(),
        )

    await state.clear()
