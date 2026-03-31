from aiogram.fsm.state import State, StatesGroup


class BroadcastState(StatesGroup):
    """Состояния для рассылки сообщений"""

    waiting_for_message_type = State()  # Ожидание типа сообщения (текст/фото/видео)
    waiting_for_message_text = State()  # Ожидание текста сообщения
    waiting_for_photo = State()  # Ожидание фото
    waiting_for_video = State()  # Ожидание видео
    waiting_for_confirmation = State()  # Ожидание подтверждения отправки


class DeleteUserState(StatesGroup):
    """Состояния для удаления пользователя"""

    waiting_for_user_id = State()  # Ожидание ID пользователя


class PromoCodeState(StatesGroup):
    """Состояния для создания промокодов"""

    waiting_for_bonus_amount = State()  # Ожидание суммы бонуса
    waiting_for_description = State()  # Ожидание описания промокода
    waiting_for_quantity = State()  # Ожидание количества промокодов


class ConsentState(StatesGroup):
    """Состояния для получения согласия на обработку персональных данных"""

    waiting_for_consent = State()  # Ожидание согласия пользователя


class EventState(StatesGroup):
    """Состояния для создания мероприятий"""

    waiting_for_title = State()  # Ожидание названия мероприятия
    waiting_for_description = State()  # Ожидание описания мероприятия
    waiting_for_date = State()  # Ожидание даты и времени мероприятия
    waiting_for_photo = State()  # Ожидание фото мероприятия (необязательно)
    waiting_for_confirmation = State()  # Ожидание подтверждения создания
