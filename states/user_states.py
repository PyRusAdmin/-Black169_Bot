# -*- coding: utf-8 -*-
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
