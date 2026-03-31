# -*- coding: utf-8 -*-
"""
Тесты для приветственных бонусов и колеса подарков
"""
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from services.bonus import random_bonus
from services.database import (
    activate_promo_code,
    add_consent,
    create_promo_code,
    get_promo_code,
    has_consent,
    has_user_spun_today,
    write_spin_result,
)


class TestWelcomeBonus:
    """Тесты для приветственных бонусов (1000 ₽)"""

    @pytest.fixture
    def mock_user_data(self):
        """Фикстура с данными пользователя"""
        return {
            "id_telegram": 123456789,
            "id_quickresto": 98765,
            "phone_telegram": "79999999999",
            "first_name": "Иван",
            "last_name": "Иванов",
        }

    def test_add_consent_exists(self):
        """Тест: функция add_consent существует"""
        assert callable(add_consent)

    @patch("services.database.Consents")
    @patch("services.database.db")
    def test_has_consent_true(self, mock_db, mock_consents, mock_user_data):
        """Тест: проверка наличия согласия — согласие есть"""
        mock_db.is_closed.return_value = False
        mock_consents.get_or_none.return_value = MagicMock()

        result = has_consent(mock_user_data["id_telegram"])

        assert result is True
        mock_consents.get_or_none.assert_called_once()

    @patch("services.database.Consents")
    @patch("services.database.db")
    def test_has_consent_false(self, mock_db, mock_consents, mock_user_data):
        """Тест: проверка наличия согласия — согласия нет"""
        mock_db.is_closed.return_value = False
        mock_consents.get_or_none.return_value = None

        result = has_consent(mock_user_data["id_telegram"])

        assert result is False


class TestGiftWheel:
    """Тесты для колеса подарков"""

    def test_random_bonus_possible_values(self):
        """Тест: случайный бонус возвращает допустимые значения"""
        possible_values = ["Коктейль на выбор", "Кальян на выбор", "Бонус в рублях (1000)", "Попробуйте завтра"]

        # Запускаем 100 раз для проверки всех возможных значений
        results = set()
        for _ in range(100):
            result = random_bonus()
            results.add(result)

        # Все полученные значения должны быть из допустимых
        assert results.issubset(set(possible_values))

    def test_random_bonus_not_always_winner(self):
        """Тест: случайный бонус не всегда возвращает выигрыш"""
        # Запускаем 100 раз
        results = [random_bonus() for _ in range(100)]

        # Должен быть хотя бы один проигрыш
        losers = [r for r in results if r == "Попробуйте завтра"]
        assert len(losers) > 0, "Все результаты — выигрыши, что маловероятно"

    @patch("services.database.GiftWheelSpins")
    @patch("services.database.db")
    def test_write_spin_result_winner(self, mock_db, mock_spins):
        """Тест: запись результата розыгрыша — победитель"""
        mock_db.is_closed.return_value = False
        mock_db.connect = MagicMock()
        mock_db.close = MagicMock()

        data = {
            "id_telegram": 123456789,
            "id_quickresto": 98765,
            "bonus_name": "Бонус в рублях (1000)",
            "is_winner": True,
        }

        result = write_spin_result(data)

        assert result is not None

    @patch("services.database.GiftWheelSpins")
    @patch("services.database.db")
    def test_write_spin_result_loser(self, mock_db, mock_spins):
        """Тест: запись результата розыгрыша — не победитель"""
        mock_db.is_closed.return_value = False

        data = {
            "id_telegram": 123456789,
            "id_quickresto": 98765,
            "bonus_name": "Попробуйте завтра",
            "is_winner": False,
        }

        result = write_spin_result(data)

        assert result is not None

    @patch("services.database.GiftWheelSpins")
    @patch("services.database.db")
    def test_has_user_spun_today_false(self, mock_db, mock_spins):
        """Тест: пользователь не участвовал сегодня — False"""
        mock_db.is_closed.return_value = False
        mock_spins.get_or_none.return_value = None

        result = has_user_spun_today(123456789)

        assert result is False


class TestPromoCodes:
    """Тесты для промокодов"""

    @pytest.fixture
    def mock_promo_data(self):
        """Фикстура с данными промокода"""
        return {
            "code": "TEST2026",
            "bonus_amount": 500.00,
            "description": "Тестовый промокод",
        }

    @patch("services.database.PromoCodes")
    @patch("services.database.db")
    def test_create_promo_code_success(self, mock_db, mock_promo_codes, mock_promo_data):
        """Тест: создание промокода — успешно"""
        mock_db.is_closed.return_value = False
        mock_db.connect = MagicMock()
        mock_db.close = MagicMock()

        result = create_promo_code(
            mock_promo_data["code"], mock_promo_data["bonus_amount"], mock_promo_data["description"]
        )

        assert result is True

    @patch("services.database.PromoCodes")
    @patch("services.database.db")
    def test_get_promo_code_found(self, mock_db, mock_promo_codes, mock_promo_data):
        """Тест: получение промокода — найден"""
        mock_db.is_closed.return_value = False

        mock_promo = MagicMock()
        mock_promo.code = mock_promo_data["code"]
        mock_promo.bonus_amount = mock_promo_data["bonus_amount"]
        mock_promo.is_active = True

        mock_promo_codes.get_or_none.return_value = mock_promo

        result = get_promo_code(mock_promo_data["code"])

        assert result is not None
        assert result["code"] == mock_promo_data["code"]
        assert result["bonus_amount"] == mock_promo_data["bonus_amount"]

    @patch("services.database.PromoCodes")
    @patch("services.database.db")
    def test_get_promo_code_not_found(self, mock_db, mock_promo_codes):
        """Тест: получение промокода — не найден"""
        mock_db.is_closed.return_value = False
        mock_promo_codes.get_or_none.return_value = None

        result = get_promo_code("NONEXISTENT")

        assert result is None

    @patch("services.database.PromoCodes")
    @patch("services.database.db")
    def test_activate_promo_code_success(self, mock_db, mock_promo_codes):
        """Тест: активация промокода — успешно"""
        mock_db.is_closed.return_value = False
        mock_db.connect = MagicMock()
        mock_db.close = MagicMock()

        mock_promo = MagicMock()
        mock_promo_codes.get_or_none.return_value = mock_promo

        mock_update = MagicMock()
        mock_update.execute.return_value = 1
        mock_promo_codes.update.return_value = mock_update
        mock_update.where.return_value = mock_update

        result = activate_promo_code("TEST2026", 123456789)

        assert result is True

    @patch("services.database.PromoCodes")
    @patch("services.database.db")
    def test_activate_promo_code_already_used(self, mock_db, mock_promo_codes):
        """Тест: активация промокода — уже использован"""
        mock_db.is_closed.return_value = False
        mock_promo_codes.get_or_none.return_value = None  # Уже использован или не активен

        result = activate_promo_code("USED2026", 123456789)

        assert result is False

        assert result is False
