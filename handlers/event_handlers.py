import uuid
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import OWNER_IDS
from keyboards.keyboards import (
    admin_menu_keyboard, back_to_events_menu_keyboard, event_action_keyboard, event_confirm_keyboard,
    events_menu_keyboard
)
from services.database import is_admin_in_db
from services.events_json import create_event_json, delete_event_json, get_all_events_json, update_event_json
from services.i18n import t
from states.user_states import EventState
from utils.logger import logger

router = Router(name=__name__)


async def verifies_the_user_for_admin(callback):
    """
    Проверяет пользователя на права администратора (OWNER_IDS из .env + из БД)

    :param callback: CallbackQuery
    :return: True если администратор, False если нет
    """
    if callback.from_user.id in OWNER_IDS or is_admin_in_db(callback.from_user.id):
        return True
    await callback.answer(t("no-admin-permission"), show_alert=True)
    return False


@router.callback_query(F.data == "events_menu")
async def events_menu_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки 'Мероприятия' в админ-панели
    """
    logger.info(f"Администратор {callback.from_user.id} запросил меню мероприятий")

    # Проверяет пользователя на права администратора
    if not await verifies_the_user_for_admin(callback):
        return

    await callback.message.edit_text(
        text=t("events-menu-title"), reply_markup=events_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "event_create")
async def event_create_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик кнопки 'Создать мероприятие'
    """
    logger.info(f"Администратор {callback.from_user.id} начал создание мероприятия")

    # Проверяет пользователя на права администратора
    if not await verifies_the_user_for_admin(callback):
        return

    await state.set_state(EventState.waiting_for_title)
    await callback.message.edit_text(
        text=t("event-create-title"), reply_markup=back_to_events_menu_keyboard()
    )
    await callback.answer()


@router.message(EventState.waiting_for_title, F.text)
async def event_title_handler(message: Message, state: FSMContext) -> None:
    """
    Получение названия мероприятия
    """
    logger.info(f"Администратор {message.from_user.id} ввёл название мероприятия")

    title = message.text.strip()
    if len(title) < 3:
        await message.answer(
            text="❌ Название должно быть не менее 3 символов.\n\nВведите название ещё раз:"
        )
        return

    await state.update_data(title=title)
    await state.set_state(EventState.waiting_for_description)
    await message.answer(
        text=t("event-create-description"), reply_markup=back_to_events_menu_keyboard()
    )


@router.message(EventState.waiting_for_description, F.text)
async def event_description_handler(message: Message, state: FSMContext) -> None:
    """
    Получение описания мероприятия
    """
    logger.info(f"Администратор {message.from_user.id} ввёл описание мероприятия")

    description = message.text.strip()
    if len(description) < 10:
        await message.answer(
            text="❌ Описание должно быть не менее 10 символов.\n\nВведите описание ещё раз:"
        )
        return

    await state.update_data(description=description)
    await state.set_state(EventState.waiting_for_date)
    await message.answer(
        text=t("event-create-date"), reply_markup=back_to_events_menu_keyboard()
    )


@router.message(EventState.waiting_for_date, F.text)
async def event_date_handler(message: Message, state: FSMContext) -> None:
    """
    Получение даты и времени мероприятия
    """
    logger.info(f"Администратор {message.from_user.id} ввёл дату мероприятия")

    date_text = message.text.strip()

    # Проверяем формат даты (ДД.ММ.ГГГГ ЧЧ:ММ)
    try:
        event_date = datetime.strptime(date_text, "%d.%m.%Y %H:%M")
    except ValueError:
        await message.answer(
            text="❌ Неверный формат даты.\n\nИспользуйте формат: ДД.ММ.ГГГГ ЧЧ:ММ\n\nПример: 15.04.2026 22:00"
        )
        return

    # Проверяем, что дата не в прошлом
    if event_date < datetime.now():
        await message.answer(
            text="❌ Дата мероприятия не может быть в прошлом.\n\nВведите корректную дату:"
        )
        return

    await state.update_data(event_date=event_date, event_date_str=date_text)
    await state.set_state(EventState.waiting_for_photo)
    await message.answer(
        text=t("event-create-photo"), reply_markup=back_to_events_menu_keyboard()
    )


@router.message(EventState.waiting_for_photo, F.photo)
async def event_photo_handler(message: Message, state: FSMContext) -> None:
    """
    Получение фото мероприятия
    """
    logger.info(f"Администратор {message.from_user.id} отправил фото мероприятия")

    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    await state.set_state(EventState.waiting_for_reminder_3days)
    await message.answer(
        text=t("event-create-reminder-3days"),
        reply_markup=back_to_events_menu_keyboard(),
    )


@router.message(EventState.waiting_for_photo, F.text)
async def event_skip_photo_handler(message: Message, state: FSMContext) -> None:
    """
    Пропуск загрузки фото
    """
    logger.info(f"Администратор {message.from_user.id} пропустил загрузку фото")

    if message.text.strip() == "-":
        await state.update_data(photo_id=None)
        await state.set_state(EventState.waiting_for_reminder_3days)
        await message.answer(
            text=t("event-create-reminder-3days"),
            reply_markup=back_to_events_menu_keyboard(),
        )
    else:
        await message.answer(text="❌ Отправьте фото или введите '-' для пропуска:")


@router.message(EventState.waiting_for_reminder_3days, F.text)
async def event_reminder_3days_handler(message: Message, state: FSMContext) -> None:
    """
    Получение текста напоминания за 3 дня
    """
    logger.info(f"Администратор {message.from_user.id} ввёл напоминание за 3 дня")

    if message.text.strip() == "-":
        await state.update_data(reminder_text_3days=None)
    else:
        await state.update_data(reminder_text_3days=message.text.strip())

    await state.set_state(EventState.waiting_for_reminder_1day)
    await message.answer(
        text=t("event-create-reminder-1day"),
        reply_markup=back_to_events_menu_keyboard(),
    )


@router.message(EventState.waiting_for_reminder_1day, F.text)
async def event_reminder_1day_handler(message: Message, state: FSMContext) -> None:
    """
    Получение текста напоминания за 1 день
    """
    logger.info(f"Администратор {message.from_user.id} ввёл напоминание за 1 день")

    if message.text.strip() == "-":
        await state.update_data(reminder_text_1day=None)
    else:
        await state.update_data(reminder_text_1day=message.text.strip())

    await state.set_state(EventState.waiting_for_reminder_event_day)
    await message.answer(
        text=t("event-create-reminder-event-day"),
        reply_markup=back_to_events_menu_keyboard(),
    )


@router.message(EventState.waiting_for_reminder_event_day, F.text)
async def event_reminder_event_day_handler(message: Message, state: FSMContext) -> None:
    """
    Получение текста напоминания в день мероприятия
    """
    logger.info(
        f"Администратор {message.from_user.id} ввёл напоминание в день мероприятия"
    )

    if message.text.strip() == "-":
        await state.update_data(reminder_text_event_day=None)
    else:
        await state.update_data(reminder_text_event_day=message.text.strip())

    await send_confirmation(message, state)


async def send_confirmation(message: Message, state: FSMContext) -> None:
    """
    Отправка подтверждения создания мероприятия
    """
    data = await state.get_data()
    title = data.get("title")
    description = data.get("description")
    date = data.get("event_date_str")

    logger.info(
        f"Данные для подтверждения: title={title}, description={description}, date={date}"
    )
    logger.info(f"Все данные состояния: {data}")

    await state.set_state(EventState.waiting_for_confirmation)
    await message.answer(
        text=t("event-create-confirm", title=title, description=description, date=date),
        reply_markup=event_confirm_keyboard(),
    )


@router.callback_query(F.data == "event_confirm_yes")
async def event_confirm_yes_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Подтверждение создания мероприятия
    """
    logger.info(
        f"Администратор {callback.from_user.id} подтвердил создание мероприятия"
    )

    data = await state.get_data()
    title = data.get("title")
    description = data.get("description")
    event_date = data.get("event_date")
    photo_id = data.get("photo_id")
    reminder_text_3days = data.get("reminder_text_3days")
    reminder_text_1day = data.get("reminder_text_1day")
    reminder_text_event_day = data.get("reminder_text_event_day")

    # Генерируем уникальный ID для мероприятия
    event_id = str(uuid.uuid4())

    # Создаём мероприятие в JSON
    try:
        create_event_json(
            event_id=event_id,
            title=title,
            description=description,
            event_date=event_date,
            created_by=callback.from_user.id,
            photo_id=photo_id,
            reminder_text_3days=reminder_text_3days,
            reminder_text_1day=reminder_text_1day,
            reminder_text_event_day=reminder_text_event_day,
        )

        # Показываем информацию о напоминаниях
        reminders_info = []
        if reminder_text_3days:
            reminders_info.append("• За 3 дня: ✅")
        if reminder_text_1day:
            reminders_info.append("• За 1 день: ✅")
        if reminder_text_event_day:
            reminders_info.append("• В день мероприятия: ✅")

        reminders_text = (
            "\n".join(reminders_info)
            if reminders_info
            else "❌ Напоминания не настроены"
        )

        await callback.message.answer(
            text=f"{t('event-create-success', title=title, date=data.get('event_date_str'))}\n\n🔔 <b>Напоминания:</b>\n{reminders_text}",
            reply_markup=admin_menu_keyboard(),
            parse_mode="HTML",
        )
    except Exception as e:
        logger.exception(f"Ошибка при создании мероприятия: {e}")
        await callback.message.answer(
            text="❌ Ошибка при создании мероприятия. Попробуйте ещё раз.",
            reply_markup=admin_menu_keyboard(),
        )

    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "event_confirm_no")
async def event_confirm_no_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Отмена создания мероприятия
    """
    logger.info(f"Администратор {callback.from_user.id} отменил создание мероприятия")

    await state.clear()
    await callback.message.answer(
        text="❌ Создание мероприятия отменено.",
        reply_markup=admin_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "event_list")
async def event_list_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки 'Список мероприятий'
    """
    logger.info(f"Администратор {callback.from_user.id} запросил список мероприятий")

    # Проверяет пользователя на права администратора
    if not await verifies_the_user_for_admin(callback):
        return

    events = get_all_events_json()

    if not events:
        await callback.message.answer(
            text=t("event-list-empty"), reply_markup=back_to_events_menu_keyboard()
        )
        await callback.answer()
        return

    # Показываем статистику
    active_count = len([e for e in events if e.get("is_active", False)])
    inactive_count = len(events) - active_count

    await callback.message.answer(
        text=t(
            "event-list-title",
            total=len(events),
            active=active_count,
            inactive=inactive_count,
        ),
        reply_markup=back_to_events_menu_keyboard(),
    )

    # Показываем каждое мероприятие
    for event in events:
        status = "✅ Активно" if event.get("is_active", False) else "⏸️ Неактивно"
        event_date = datetime.fromisoformat(event["event_date"])
        date_str = event_date.strftime("%d.%m.%Y %H:%M")

        text = t(
            "event-info",
            title=event["title"],
            description=event["description"],
            date=date_str,
            status=status,
        )

        # Если есть фото, отправляем с фото
        if event.get("photo_id"):
            await callback.message.answer_photo(
                photo=event["photo_id"],
                caption=text,
                reply_markup=event_action_keyboard(event["id"]),
            )
        else:
            await callback.message.answer(
                text=text, reply_markup=event_action_keyboard(event["id"])
            )

    await callback.answer()


@router.callback_query(F.data.startswith("event_activate_"))
async def event_activate_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки 'Активировать мероприятие'
    """
    event_id = callback.data.split("_", 2)[-1]
    logger.info(
        f"Администратор {callback.from_user.id} активировал мероприятие {event_id}"
    )

    # Проверяет пользователя на права администратора
    if not await verifies_the_user_for_admin(callback):
        return

    result = update_event_json(event_id, is_active=True)

    if result:
        await callback.answer(t("event-activated", id=event_id), show_alert=True)
    else:
        await callback.answer("❌ Ошибка при активации мероприятия", show_alert=True)


@router.callback_query(F.data.startswith("event_deactivate_"))
async def event_deactivate_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки 'Деактивировать мероприятие'
    """
    event_id = callback.data.split("_", 2)[-1]
    logger.info(
        f"Администратор {callback.from_user.id} деактивировал мероприятие {event_id}"
    )

    # Проверяет пользователя на права администратора
    if not await verifies_the_user_for_admin(callback):
        return

    result = update_event_json(event_id, is_active=False)

    if result:
        await callback.answer(t("event-deactivated", id=event_id), show_alert=True)
    else:
        await callback.answer("❌ Ошибка при деактивации мероприятия", show_alert=True)


@router.callback_query(F.data == "event_delete")
async def event_delete_menu_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик кнопки 'Удалить мероприятие'
    """
    logger.info(f"Администратор {callback.from_user.id} запросил удаление мероприятия")

    # Проверяет пользователя на права администратора
    if not await verifies_the_user_for_admin(callback):
        return

    await state.set_state(EventState.waiting_for_date)  # Временное состояние
    await callback.message.answer(
        text=t("event-delete-title"), reply_markup=back_to_events_menu_keyboard()
    )
    await callback.answer()


@router.message(F.text, StateFilter(EventState.waiting_for_date))
async def event_delete_handler(message: Message, state: FSMContext) -> None:
    """
    Удаление мероприятия по ID
    """
    logger.info(f"Администратор {message.from_user.id} удаляет мероприятие")

    event_id = message.text.strip()

    result = delete_event_json(event_id)

    if result:
        await message.answer(
            text=t("event-delete-success", id=event_id),
            reply_markup=admin_menu_keyboard(),
        )
    else:
        await message.answer(
            text=t("event-delete-not-found", id=event_id),
            reply_markup=back_to_events_menu_keyboard(),
        )

    await state.clear()


@router.callback_query(F.data.startswith("event_delete_"))
async def event_delete_direct_handler(callback: CallbackQuery) -> None:
    """
    Удаление мероприятия напрямую из списка
    """
    event_id = callback.data.split("_", 2)[-1]
    logger.info(f"Администратор {callback.from_user.id} удаляет мероприятие {event_id}")

    # Проверяет пользователя на права администратора
    if not await verifies_the_user_for_admin(callback):
        return

    result = delete_event_json(event_id)

    if result:
        await callback.answer(f"✅ Мероприятие {event_id} удалено", show_alert=True)
        # Редактируем сообщение, убирая клавиатуру
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
    else:
        await callback.answer("❌ Ошибка при удалении мероприятия", show_alert=True)


@router.callback_query(F.data == "events_back")
async def events_back_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик кнопки 'В меню мероприятий'
    """
    logger.info(f"Администратор {callback.from_user.id} вернулся в меню мероприятий")

    # Проверяет пользователя на права администратора
    if not await verifies_the_user_for_admin(callback):
        return

    # Очищаем состояние FSM
    await state.clear()

    # Пробуем отредактировать сообщение
    try:
        await callback.message.edit_text(
            text=t("events-menu-title"), reply_markup=events_menu_keyboard()
        )
    except Exception:
        await callback.message.answer(
            text=t("events-menu-title"), reply_markup=events_menu_keyboard()
        )

    await callback.answer()
