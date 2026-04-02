# -*- coding: utf-8 -*-
"""
Тесты для интеграции с QuickResto API
"""
from unittest.mock import MagicMock, patch

import pytest

from services.quickresto_api import (
    create_client,
    delete_customer,
    get_customer_by_phone,
    print_full_client_info,
    update_customer_bonus,
)


class TestQuickRestoAPI:
    """Тесты для QuickResto API"""

    @pytest.fixture
    def mock_auth(self):
        """Фикстура для mock авторизации"""
        return ("test_user", "test_pass")

    @pytest.fixture
    def mock_headers(self):
        """Фикстура для mock заголовков"""
        return {"Content-Type": "application/json"}

    @pytest.fixture
    def mock_response(self):
        """Фикстура для mock ответа"""
        return {
            "id": 12345,
            "last_name": "Иванов",
            "first_name": "Иван",
            "middle_name": "Иванович",
            "phone": "79999999999",
            "bonus_ledger": "1500",
            "date_of_birth": "1990-01-15",
        }

    @patch("services.quickresto_api.requests.get")
    def test_get_customer_by_phone_found(
        self, mock_get, mock_auth, mock_headers, mock_response
    ):
        """Тест: поиск клиента по телефону — клиент найден"""
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = {"customers": [mock_response]}
        mock_get.return_value = mock_response_obj

        result = get_customer_by_phone(
            "79999999999", "https://api.quickresto.ru", mock_auth, mock_headers
        )

        assert result is not None
        assert result["id"] == 12345
        assert result["last_name"] == "Иванов"
        mock_get.assert_called_once()

    @patch("services.quickresto_api.requests.get")
    def test_get_customer_by_phone_not_found(self, mock_get, mock_auth, mock_headers):
        """Тест: поиск клиента по телефону — клиент не найден"""
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = {"customers": []}
        mock_get.return_value = mock_response_obj

        result = get_customer_by_phone(
            "79999999999", "https://api.quickresto.ru", mock_auth, mock_headers
        )

        assert result is None
        mock_get.assert_called_once()

    @patch("services.quickresto_api.requests.get")
    def test_get_customer_by_phone_error(self, mock_get, mock_auth, mock_headers):
        """Тест: поиск клиента по телефону — ошибка API"""
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 500
        mock_get.return_value = mock_response_obj

        result = get_customer_by_phone(
            "79999999999", "https://api.quickresto.ru", mock_auth, mock_headers
        )

        assert result is None
        mock_get.assert_called_once()

    @patch("services.quickresto_api.requests.post")
    def test_create_client_success(self, mock_post, mock_auth, mock_headers):
        """Тест: создание клиента — успешно"""
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = {"id": 12345}
        mock_post.return_value = mock_response_obj

        client_data = {
            "last_name": "Петров",
            "first_name": "Петр",
            "middle_name": "Петрович",
            "phone": "79998887766",
            "birthday": "1995-05-20",
        }

        result = create_client(
            client_data, "https://api.quickresto.ru", mock_auth, mock_headers
        )

        assert result is not None
        assert result["id"] == 12345
        mock_post.assert_called_once()

    @patch("services.quickresto_api.requests.post")
    def test_create_client_error(self, mock_post, mock_auth, mock_headers):
        """Тест: создание клиента — ошибка"""
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 400
        mock_post.return_value = mock_response_obj

        client_data = {
            "last_name": "Петров",
            "first_name": "Петр",
            "phone": "79998887766",
        }

        result = create_client(
            client_data, "https://api.quickresto.ru", mock_auth, mock_headers
        )

        assert result is None
        mock_post.assert_called_once()

    @patch("services.quickresto_api.requests.put")
    def test_update_customer_bonus_success(self, mock_put, mock_auth, mock_headers):
        """Тест: начисление бонусов — успешно"""
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = {"success": True}
        mock_put.return_value = mock_response_obj

        result = update_customer_bonus(
            customer_id=12345,
            amount=1000.00,
            customer_phone="79999999999",
            base_url="https://api.quickresto.ru",
            auth=mock_auth,
            headers=mock_headers,
        )

        assert result is True
        mock_put.assert_called_once()

    @patch("services.quickresto_api.requests.put")
    def test_update_customer_bonus_error(self, mock_put, mock_auth, mock_headers):
        """Тест: начисление бонусов — ошибка"""
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 500
        mock_put.return_value = mock_response_obj

        result = update_customer_bonus(
            customer_id=12345,
            amount=1000.00,
            customer_phone="79999999999",
        )

        assert result is False
        mock_put.assert_called_once()

    @patch("services.quickresto_api.requests.delete")
    def test_delete_customer_success(self, mock_delete, mock_auth, mock_headers):
        """Тест: удаление клиента — успешно"""
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 200
        mock_delete.return_value = mock_response_obj

        result = delete_customer(
            12345, "https://api.quickresto.ru", mock_auth, mock_headers
        )

        assert result is True
        mock_delete.assert_called_once()

    @patch("services.quickresto_api.requests.delete")
    def test_delete_customer_error(self, mock_delete, mock_auth, mock_headers):
        """Тест: удаление клиента — ошибка"""
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 404
        mock_delete.return_value = mock_response_obj

        result = delete_customer(
            12345, "https://api.quickresto.ru", mock_auth, mock_headers
        )

        assert result is False
        mock_delete.assert_called_once()

    @patch("services.quickresto_api.requests.get")
    def test_print_full_client_info(
        self, mock_get, mock_auth, mock_headers, mock_response
    ):
        """Тест: получение полной информации о клиенте"""
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_response
        mock_get.return_value = mock_response_obj

        result = print_full_client_info(
            12345, "https://api.quickresto.ru", mock_auth, mock_headers
        )

        assert result is not None
        assert result["id"] == 12345
        assert result["bonus_ledger"] == "1500"
        mock_get.assert_called_once()
        assert result["bonus_ledger"] == "1500"
        mock_get.assert_called_once()
