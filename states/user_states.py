from aiogram.fsm.state import State, StatesGroup


class BroadcastState(StatesGroup):
    """Состояния для рассылки сообщений"""
    waiting_for_message_text = State()  # Ожидание текста сообщения
    waiting_for_photo = State()  # Ожидание фото
    waiting_for_video = State()  # Ожидание видео


class DeleteUserState(StatesGroup):
    """Состояния для удаления пользователя"""
    waiting_for_user_id = State()  # Ожидание ID пользователя


class ConsentState(StatesGroup):
    """Состояния для получения согласия на обработку персональных данных"""
    waiting_for_consent = State()  # Ожидание согласия пользователя
    waiting_to_phone_user = State()  # Ожидаем телефон от пользователя


class EventState(StatesGroup):
    """Состояния для создания мероприятий"""
    waiting_for_title = State()  # Ожидание названия мероприятия
    waiting_for_description = State()  # Ожидание описания мероприятия
    waiting_for_date = State()  # Ожидание даты и времени мероприятия
    waiting_for_photo = State()  # Ожидание фото мероприятия (необязательно)
    waiting_for_reminder_3days = State()  # Ожидание текста напоминания за 3 дня
    waiting_for_reminder_1day = State()  # Ожидание текста напоминания за 1 день
    waiting_for_reminder_event_day = (
        State()
    )  # Ожидание текста напоминания в день мероприятия
    waiting_for_confirmation = State()  # Ожидание подтверждения создания


class SearchUserState(StatesGroup):
    """Состояния для поиска пользователя"""
    waiting_for_phone_number = State()  # Ожидание номера телефона


class AdminManagementState(StatesGroup):
    """Состояния для управления администраторами"""
    waiting_for_admin_id = State()  # Ожидание ID нового администратора
