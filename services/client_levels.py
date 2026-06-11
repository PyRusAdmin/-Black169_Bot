import json
from datetime import datetime

from utils.logger import logger
from utils.phone_utils import normalize_phone_number

"""
Сервис для управления уровнями клиентов.

Уровни определяются на основе накопительной суммы (accumulationBalance) из QuickResto:
- Black: от 60 000 ₽
- Gold: от 30 000 ₽
- Silver: от 10 000 ₽
- Bronze: от 0 ₽
"""

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


def get_level_privileges(level: str) -> list:
    """
    Получение списка привилегий для уровня из базы данных.

    :param level: Название уровня (Bronze, Silver, Gold, Black)
    :return: Список привилегий
    """
    from services.database import get_client_level_info

    level_info = get_client_level_info(level)

    if level_info and level_info.get("privileges"):
        try:
            return json.loads(level_info["privileges"])
        except json.JSONDecodeError:
            return [level_info["privileges"]]

    # Привилегии по умолчанию, если БД недоступна
    default_privileges = {
        "Bronze": [
            "Доступ к базовой программе лояльности",
            "Накопление бонусов с каждого заказа",
        ],
        "Silver": [
            "Все привилегии Bronze уровня",
            "Повышенный кэшбэк бонусами (1.2x)",
            "Приоритетное бронирование столов",
        ],
        "Gold": [
            "Все привилегии Silver уровня",
            "Максимальный кэшбэк бонусами (1.5x)",
            "Персональный менеджер",
            "Скидка 10% на все услуги",
        ],
        "Black": [
            "Все привилегии Gold уровня",
            "Эксклюзивный кэшбэк бонусами (2.0x)",
            "Персональный консьерж 24/7",
            "Скидка 15% на все услуги",
        ],
    }
    return default_privileges.get(level, [])


def get_level_full_info(level: str) -> dict:
    """
    Получение полной информации об уровне из БД.

    :param level: Название уровня
    :return: Полная информация об уровне
    """
    from services.database import get_client_level_info

    level_info = get_client_level_info(level)

    if level_info:
        level_info["privileges_list"] = get_level_privileges(level)
        return level_info

    # Информация по умолчанию
    return {
        "level_name": level,
        "min_accumulation": {
            "Bronze": 0,
            "Silver": 10000,
            "Gold": 30000,
            "Black": 60000,
        }.get(level, 0),
        "emoji": {"Bronze": "🥉", "Silver": "🥈", "Gold": "🥇", "Black": "💎"}.get(
            level, "📊"
        ),
        "privileges_list": get_level_privileges(level),
    }


def get_all_levels_with_privileges() -> list:
    """
    Получение всех уровней с привилегиями.

    :return: Список уровней с полной информацией
    """
    from services.database import get_all_client_levels

    levels = get_all_client_levels()

    if levels:
        for level in levels:
            level["privileges_list"] = json.loads(level.get("privileges", "[]"))
        return levels

    # Возвращаем значения по умолчанию
    return [
        {
            "level_name": "Bronze",
            "min_accumulation": 0,
            "emoji": "🥉",
            "description": "Базовый уровень",
            "privileges_list": get_level_privileges("Bronze"),
            "discount_percent": 0,
            "bonus_multiplier": 1.0,
        },
        {
            "level_name": "Silver",
            "min_accumulation": 10000,
            "emoji": "🥈",
            "description": "Серебряный уровень",
            "privileges_list": get_level_privileges("Silver"),
            "discount_percent": 5,
            "bonus_multiplier": 1.2,
        },
        {
            "level_name": "Gold",
            "min_accumulation": 30000,
            "emoji": "🥇",
            "description": "Золотой уровень",
            "privileges_list": get_level_privileges("Gold"),
            "discount_percent": 10,
            "bonus_multiplier": 1.5,
        },
        {
            "level_name": "Black",
            "min_accumulation": 60000,
            "emoji": "💎",
            "description": "Black уровень",
            "privileges_list": get_level_privileges("Black"),
            "discount_percent": 15,
            "bonus_multiplier": 2.0,
        },
    ]


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


def save_clients_to_json(
        clients_data: list, filepath: str = "data/clients_levels.json"
) -> bool:
    """
    Сохранение данных о клиентах в JSON файл.

    :param clients_data: Список данных о клиентах
    :param filepath: Путь к файлу
    :return: True если успешно, False если нет
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(clients_data, f, ensure_ascii=False, indent=2)
        logger.info(
            f"Данные о клиентах сохранены в {filepath} ({len(clients_data)} клиентов)"
        )
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

    logger.info(
        f"Нормализовано телефонных номеров: {normalized_count} из {len(clients_data)}"
    )
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
                user = RegisteredPersons.get_or_none(
                    RegisteredPersons.phone_telegram == phone
                )

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
                logger.warning(
                    f"Ошибка при синхронизации клиента {client.get('id')}: {e}"
                )
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
    sorted_clients = sorted(
        normalized_clients, key=lambda x: x.get("accumulation", 0), reverse=True
    )

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
