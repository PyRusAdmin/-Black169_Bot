# -*- coding: utf-8 -*-
"""
Конфигурация pytest и общие фикстуры
"""
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture(scope="session")
def test_config():
    """Конфигурация для тестов"""
    return {
        "test_user_id": 123456789,
        "test_quickresto_id": 98765,
        "test_phone": "79999999999",
        "test_bonus_amount": 1000.00,
    }


@pytest.fixture
def mock_bot():
    """Mock бота для тестов"""
    bot = MagicMock()
    bot.send_message = MagicMock()
    bot.send_photo = MagicMock()
    bot.send_video = MagicMock()
    bot.answer_callback_query = MagicMock()
    return bot


@pytest.fixture
def mock_callback_query():
    """Mock callback query для тестов"""
    callback = MagicMock()
    callback.from_user.id = 123456789
    callback.from_user.first_name = "Иван"
    callback.from_user.last_name = "Иванов"
    callback.message = MagicMock()
    callback.answer = MagicMock()
    return callback


@pytest.fixture
def mock_message():
    """Mock сообщения для тестов"""
    message = MagicMock()
    message.from_user.id = 123456789
    message.from_user.first_name = "Иван"
    message.from_user.last_name = "Иванов"
    message.text = "Тестовое сообщение"
    message.answer = MagicMock()
    return message


@pytest.fixture(autouse=True)
def mock_db(monkeypatch):
    """Автоматический mock базы данных для всех тестов"""
    mock = MagicMock()
    mock.is_closed.return_value = False
    mock.connect = MagicMock()
    mock.close = MagicMock()

    with patch("services.database.db", mock):
        yield mock


@pytest.fixture
def sample_user():
    """Пример данных пользователя"""
    return {
        "id_telegram": 123456789,
        "id_quickresto": 98765,
        "phone_telegram": "79999999999",
        "first_name": "Иван",
        "last_name": "Иванов",
        "patronymic_name": "Иванович",
        "birthday_user": "15.01.1990",
        "user_bonus": "1500",
    }


@pytest.fixture
def sample_event():
    """Пример данных мероприятия"""
    from datetime import datetime, timedelta

    return {
        "title": "DJ-вечеринка",
        "description": "Музыка, танцы, кальяны",
        "event_date": datetime.now() + timedelta(days=3),
        "photo_id": "AgACAgIAAxkBAAIB",
        "reminder_text_3days": "Не забудьте! Через 3 дня вечеринка!",
        "reminder_text_1day": "Завтра вечеринка! Ждём вас!",
        "reminder_text_event_day": "Сегодня вечеринка! До встречи!",
    }
