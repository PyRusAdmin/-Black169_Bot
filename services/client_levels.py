"""
Сервис для управления уровнями клиентов.

Уровни определяются на основе накопительной суммы (accumulationBalance) из QuickResto:
- Black: от 60 000 ₽
- Gold: от 30 000 ₽
- Silver: от 10 000 ₽
- Bronze: от 0 ₽
"""

import json
from datetime import datetime

from utils.logger import logger
from utils.phone_utils import normalize_phone_number

# Конфигурация уровней клиентов
LEVELS = [
    {"name": "Black", "min_amount": 60000},
    {"name": "Gold", "min_amount": 30000},
    {"name": "Silver", "min_amount": 10000},
    {"name": "Bronze", "min_amount": 0},
]


def get_level(accumulation: float) -> str:
    """
    Определение уровня клиента по накопительной сумме.
    
    :param accumulation: Накопительная сумма клиента
    :return: Название уровня (Black, Gold, Silver, Bronze)
    """
    for level in LEVELS:
        if accumulation >= level["min_amount"]:
            return level["name"]
    return "Bronze"


def get_level_description(level: str) -> str:
    """
    Получение описания уровня клиента.
    
    :param level: Название уровня
    :return: Описание уровня с условиями
    """
    descriptions = {
        "Black": "💎 Black — привилегированный уровень (от 60 000 ₽)",
        "Gold": "🥇 Gold — золотой уровень (от 30 000 ₽)",
        "Silver": "🥈 Silver — серебряный уровень (от 10 000 ₽)",
        "Bronze": "🥉 Bronze — базовый уровень",
    }
    return descriptions.get(level, f"📊 {level}")


def get_next_level_info(current_level: str, current_accumulation: float) -> dict:
    """
    Получение информации о следующем уровне.
    
    :param current_level: Текущий уровень
    :param current_accumulation: Текущая накопительная сумма
    :return: Информация о следующем уровне
    """
    level_order = ["Bronze", "Silver", "Gold", "Black"]

    try:
        current_index = level_order.index(current_level)
    except ValueError:
        current_index = 0

    if current_index >= len(level_order) - 1:
        return {
            "has_next": False,
            "next_level": None,
            "amount_needed": 0,
            "message": "Вы достигли максимального уровня!",
        }

    next_level_name = level_order[current_index + 1]
    next_level = next((lvl for lvl in LEVELS if lvl["name"] == next_level_name), None)

    if not next_level:
        return {
            "has_next": False,
            "next_level": None,
            "amount_needed": 0,
            "message": "Вы достигли максимального уровня!",
        }

    amount_needed = next_level["min_amount"] - current_accumulation

    return {
        "has_next": True,
        "next_level": next_level_name,
        "amount_needed": max(0, amount_needed),
        "message": f"До уровня {next_level_name} осталось {max(0, amount_needed):.0f} ₽",
    }


def save_clients_to_json(clients_data: list, filepath: str = "data/clients_levels.json") -> bool:
    """
    Сохранение данных о клиентах в JSON файл.
    
    :param clients_data: Список данных о клиентах
    :param filepath: Путь к файлу
    :return: True если успешно, False если нет
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(clients_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Данные о клиентах сохранены в {filepath} ({len(clients_data)} клиентов)")
        return True
    except Exception as e:
        logger.exception(f"Ошибка при сохранении данных о клиентах в JSON: {e}")
        return False


def load_clients_from_json(filepath: str = "data/clients_levels.json") -> list:
    """
    Загрузка данных о клиентах из JSON файла.
    
    :param filepath: Путь к файлу
    :return: Список данных о клиентах
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"Загружено данных о клиентах из JSON: {len(data)}")
        return data
    except FileNotFoundError:
        logger.warning(f"Файл {filepath} не найден")
        return []
    except Exception as e:
        logger.exception(f"Ошибка при загрузке данных о клиентах из JSON: {e}")
        return []


def normalize_clients_phone_numbers(clients_data: list) -> list:
    """
    Нормализация телефонных номеров в данных о клиентах.
    
    :param clients_data: Список данных о клиентах
    :return: Обновленный список с нормализованными номерами
    """
    updated_clients = []
    normalized_count = 0

    for client in clients_data:
        original_phone = client.get("phone", "")
        normalized_phone = normalize_phone_number(original_phone)

        if original_phone != normalized_phone:
            normalized_count += 1
            logger.debug(f"Нормализован номер: {original_phone} -> {normalized_phone}")

        client["phone"] = normalized_phone
        updated_clients.append(client)

    logger.info(f"Нормализовано телефонных номеров: {normalized_count} из {len(clients_data)}")
    return updated_clients


def sync_clients_with_database(clients_data: list) -> dict:
    """
    Синхронизация данных о клиентах с базой данных.
    
    :param clients_data: Список данных о клиентах
    :return: Статистика синхронизации
    """
    from services.database import RegisteredPersons, update_client_level, db

    stats = {
        "total": len(clients_data),
        "updated": 0,
        "not_found": 0,
        "errors": 0,
    }

    try:
        if db.is_closed():
            db.connect()

        for client in clients_data:
            try:
                phone = client.get("phone")
                if not phone:
                    stats["not_found"] += 1
                    continue

                # Ищем пользователя по телефону в базе данных
                user = RegisteredPersons.get_or_none(RegisteredPersons.phone_telegram == phone)

                if user:
                    # Обновляем уровень клиента
                    update_client_level(
                        id_telegram=user.id_telegram,
                        client_level=client.get("level"),
                        accumulation_amount=client.get("accumulation"),
                    )
                    stats["updated"] += 1
                else:
                    # Пробуем найти по ID QuickResto
                    user = RegisteredPersons.get_or_none(
                        RegisteredPersons.id_quickresto == client.get("id")
                    )

                    if user:
                        update_client_level(
                            id_telegram=user.id_telegram,
                            client_level=client.get("level"),
                            accumulation_amount=client.get("accumulation"),
                        )
                        stats["updated"] += 1
                    else:
                        stats["not_found"] += 1

            except Exception as e:
                logger.warning(f"Ошибка при синхронизации клиента {client.get('id')}: {e}")
                stats["errors"] += 1

        logger.info(
            f"Синхронизация завершена: всего={stats['total']}, "
            f"обновлено={stats['updated']}, не найдено={stats['not_found']}, "
            f"ошибок={stats['errors']}"
        )

    except Exception as e:
        logger.exception(f"Ошибка при синхронизации клиентов с БД: {e}")
        stats["errors"] += len(clients_data)
    finally:
        if not db.is_closed():
            db.close()

    return stats


def analyze_and_save_clients(clients_from_api: list) -> dict:
    """
    Полный цикл анализа, нормализации и сохранения данных о клиентах.
    
    :param clients_from_api: Данные о клиентах из QuickResto API
    :return: Статистика обработки
    """
    logger.info(f"Начало анализа клиентов. Всего получено: {len(clients_from_api)}")

    # Шаг 1: Нормализация телефонных номеров
    normalized_clients = normalize_clients_phone_numbers(clients_from_api)

    # Шаг 2: Сортировка по накопительной сумме (лучшие клиенты вверху)
    sorted_clients = sorted(normalized_clients, key=lambda x: x.get("accumulation", 0), reverse=True)

    # Шаг 3: Сохранение в JSON
    json_saved = save_clients_to_json(sorted_clients)

    # Шаг 4: Синхронизация с базой данных
    db_stats = sync_clients_with_database(sorted_clients)

    # Шаг 5: Подсчет статистики по уровням
    level_counts = {}
    for client in sorted_clients:
        level = client.get("level", "Unknown")
        level_counts[level] = level_counts.get(level, 0) + 1

    result = {
        "total_clients": len(sorted_clients),
        "json_saved": json_saved,
        "db_sync_stats": db_stats,
        "level_distribution": level_counts,
        "timestamp": datetime.now().isoformat(),
    }

    logger.info(f"Анализ завершен: {result}")
    return result
