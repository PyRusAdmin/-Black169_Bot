# -*- coding: utf-8 -*-
"""
Тесты для сервисов: дни рождения, сгорание бонусов, мероприятия
"""
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from services.database import (
    Events,
    create_event,
    get_birthday_users_today,
    get_bonus_burning_users,
    get_events_for_reminder,
    update_bonus_accrual_date,
    update_reminder_sent,
)


class TestBirthdayService:
    """Тесты для сервиса дней рождения"""

    @pytest.fixture
    def mock_birthday_user(self):
        """Фикстура с данными именинника"""
        return {
            "id_telegram": 123456789,
            "id_quickresto": 98765,
            "phone_telegram": "79999999999",
            "first_name": "Иван",
            "last_name": "Иванов",
            "birthday_user": datetime.now().strftime("%d.%m"),
        }

    @patch("services.database.RegisteredPersons")
    @patch("services.database.db")
    def test_get_birthday_users_today(self, mock_db, mock_registered, mock_birthday_user):
        """Тест: получение именинников сегодня"""
        today = datetime.now()

        mock_db.is_closed.return_value = False

        # Mock пользователя с сегодняшним ДР
        mock_person = MagicMock()
        mock_person.id_telegram = mock_birthday_user["id_telegram"]
        mock_person.birthday_user = today.strftime("%d.%m.%Y")
        mock_person.first_name = mock_birthday_user["first_name"]
        mock_person.last_name = mock_birthday_user["last_name"]

        mock_registered.select.return_value = [mock_person]

        result = get_birthday_users_today()

        # Проверяем, что функция вернула список
        assert isinstance(result, list)

    @patch("services.database.RegisteredPersons")
    @patch("services.database.db")
    def test_get_birthday_users_today_none(self, mock_db, mock_registered):
        """Тест: именинников сегодня нет"""
        mock_db.is_closed.return_value = False

        mock_person = MagicMock()
        mock_person.birthday_user = "15.05"  # Другая дата

        mock_registered.select.return_value = [mock_person]

        result = get_birthday_users_today()

        assert len(result) == 0


class TestBonusBurnService:
    """Тесты для сервиса сгорания бонусов"""

    @pytest.fixture
    def mock_burning_user(self):
        """Фикстура с данными пользователя с горящими бонусами"""
        return {
            "id_telegram": 123456789,
            "id_quickresto": 98765,
            "first_name": "Иван",
            "last_name": "Иванов",
            "user_bonus": "1500",
            "bot_bonus_amount": 1000.00,
        }

    @patch("services.database.RegisteredPersons")
    @patch("services.database.db")
    def test_get_bonus_burning_users_7_days(self, mock_db, mock_registered, mock_burning_user):
        """Тест: получение пользователей с горящими бонусами (за 7 дней)"""
        # Дата начисления бонусов: 90 - 7 = 83 дня назад
        accrual_date = datetime.now() - timedelta(days=83)

        mock_db.is_closed.return_value = False

        mock_person = MagicMock()
        mock_person.id_telegram = mock_burning_user["id_telegram"]
        mock_person.bonus_accrued_at = accrual_date
        mock_person.bot_bonus_amount = mock_burning_user["bot_bonus_amount"]
        mock_person.user_bonus = mock_burning_user["user_bonus"]

        mock_registered.select.return_value = [mock_person]

        result = get_bonus_burning_users(days_until_burn=7)

        # Проверяем, что функция вернула список
        assert isinstance(result, list)

    @patch("services.database.RegisteredPersons")
    @patch("services.database.db")
    def test_update_bonus_accrual_date_success(self, mock_db, mock_registered):
        """Тест: обновление даты начисления бонусов"""
        mock_db.is_closed.return_value = False
        mock_db.connect = MagicMock()
        mock_db.close = MagicMock()

        mock_update = MagicMock()
        mock_update.execute.return_value = 1
        mock_registered.update.return_value = mock_update
        mock_update.where.return_value = mock_update

        result = update_bonus_accrual_date(123456789, bonus_amount=1000.00)

        assert result is True


class TestEventReminderService:
    """Тесты для сервиса напоминаний о мероприятиях"""

    @pytest.fixture
    def mock_event(self):
        """Фикстура с данными мероприятия"""
        return {
            "id": 1,
            "title": "DJ-вечеринка",
            "description": "Музыка, танцы",
            "event_date": datetime.now() + timedelta(days=3),
            "reminder_text_3days": "Не забудьте! Через 3 дня вечеринка!",
        }

    @patch("services.database.fn")
    @patch("services.database.Events")
    @patch("services.database.db")
    def test_get_events_for_reminder_3days(self, mock_db, mock_events, mock_fn, mock_event):
        """Тест: получение мероприятий для напоминания за 3 дня"""
        mock_db.is_closed.return_value = False

        mock_event_obj = MagicMock()
        mock_event_obj.id = mock_event["id"]
        mock_event_obj.title = mock_event["title"]
        mock_event_obj.reminder_text_3days = mock_event["reminder_text_3days"]
        mock_event_obj.reminder_3days_sent = False
        mock_event_obj.is_active = True

        mock_select = MagicMock()
        mock_select.where.return_value = mock_select
        mock_select.order_by.return_value = [mock_event_obj]
        mock_events.select.return_value = mock_select

        result = get_events_for_reminder(days_until=3)

        # Проверяем, что функция вернула список
        assert isinstance(result, list)

    @patch("services.database.Events")
    @patch("services.database.db")
    def test_update_reminder_sent_success(self, mock_db, mock_events):
        """Тест: обновление статуса отправленного напоминания"""
        mock_db.is_closed.return_value = False
        mock_db.connect = MagicMock()
        mock_db.close = MagicMock()

        mock_update = MagicMock()
        mock_update.execute.return_value = 1
        mock_events.update.return_value = mock_update
        mock_update.where.return_value = mock_update

        result = update_reminder_sent(event_id=1, reminder_type="3days")

        assert result is True


class TestDatabaseIntegration:
    """Интеграционные тесты для базы данных"""

    def test_create_tables_exists(self):
        """Тест: таблица events существует"""
        # Проверяем, что модель определена
        assert Events is not None
        assert Events._meta.table_name == "events"

    def test_event_model_fields(self):
        """Тест: модель Events имеет все необходимые поля"""
        fields = Events._meta.fields
        field_names = list(fields.keys())

        required_fields = [
            "title",
            "description",
            "event_date",
            "photo_id",
            "is_active",
            "created_at",
            "created_by",
            "reminder_text_3days",
            "reminder_text_1day",
            "reminder_text_event_day",
            "reminder_3days_sent",
            "reminder_1day_sent",
            "reminder_event_day_sent",
        ]

        for field in required_fields:
            assert field in field_names, f"Поле {field} отсутствует в модели Events"
        for field in required_fields:
            assert field in field_names, f"Поле {field} отсутствует в модели Events"
