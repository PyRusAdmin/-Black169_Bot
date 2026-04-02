#!/usr/bin/env python3
"""
Скрипт для переноса данных из clients_levels.json в базу данных.

Использование:
    python migrate_clients_to_db.py
"""
import json
import sys
from pathlib import Path

from services.database import RegisteredPersons, db
from utils.phone_utils import normalize_phone_number
from utils.logger import logger

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent))


def migrate_clients_to_db(json_filepath: str = "data/clients_levels.json") -> dict:
    """
    Перенос данных о клиентах из JSON файла в базу данных.
    
    :param json_filepath: Путь к JSON файлу
    :return: Статистика миграции
    """
    stats = {
        "total": 0,
        "updated": 0,
        "not_found": 0,
        "errors": 0,
    }

    # Загружаем данные из JSON
    try:
        with open(json_filepath, "r", encoding="utf-8") as f:
            clients_data = json.load(f)
        logger.info(f"Загружено клиентов из JSON: {len(clients_data)}")
    except FileNotFoundError:
        logger.error(f"Файл {json_filepath} не найден")
        return stats
    except Exception as e:
        logger.exception(f"Ошибка при загрузке JSON: {e}")
        return stats

    stats["total"] = len(clients_data)

    try:
        if db.is_closed():
            db.connect()

        for i, client in enumerate(clients_data, 1):
            try:
                # Нормализуем телефон
                phone = normalize_phone_number(client.get("phone", ""))
                client_id = client.get("id")
                level = client.get("level")
                accumulation = client.get("accumulation", 0)

                if not phone:
                    logger.warning(f"Клиент {client_id} не имеет телефона, пропускаем")
                    stats["not_found"] += 1
                    continue

                # Ищем пользователя по телефону в БД
                user = RegisteredPersons.get_or_none(RegisteredPersons.phone_telegram == phone)

                if not user and client_id:
                    # Пробуем найти по ID QuickResto
                    user = RegisteredPersons.get_or_none(RegisteredPersons.id_quickresto == client_id)

                if user:
                    # Обновляем данные пользователя
                    user.client_level = level
                    user.accumulation_amount = accumulation
                    user.phone_telegram = phone  # Обновляем нормализованный телефон
                    user.save()

                    stats["updated"] += 1

                    if i % 100 == 0:
                        logger.info(f"Обработано: {i}/{len(clients_data)}")
                else:
                    stats["not_found"] += 1

            except Exception as e:
                logger.warning(f"Ошибка при обработке клиента {client.get('id')}: {e}")
                stats["errors"] += 1

        logger.info(
            f"Миграция завершена: всего={stats['total']}, "
            f"обновлено={stats['updated']}, не найдено={stats['not_found']}, "
            f"ошибок={stats['errors']}"
        )

    except Exception as e:
        logger.exception(f"Ошибка при миграции данных: {e}")
        stats["errors"] += len(clients_data)
    finally:
        if not db.is_closed():
            db.close()

    return stats


def print_report(stats: dict):
    """Вывод отчета о миграции"""
    print("\n" + "=" * 60)
    print("📊 ОТЧЕТ О МИГРАЦИИ ДАННЫХ")
    print("=" * 60)
    print(f"📁 Всего клиентов в JSON: {stats['total']}")
    print(f"✅ Обновлено в БД: {stats['updated']}")
    print(f"❌ Не найдено в БД: {stats['not_found']}")
    print(f"⚠️  Ошибок: {stats['errors']}")
    print("=" * 60)

    if stats['total'] > 0:
        percent = stats['updated'] / stats['total'] * 100
        print(f"📈 Процент успешных: {percent:.1f}%")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    print("🚀 Запуск миграции данных из clients_levels.json в БД...")
    result = migrate_clients_to_db()
    print_report(result)

    if result['updated'] > 0:
        print("✅ Миграция успешно завершена!")
    else:
        print("⚠️  Миграция завершена, но данные не были обновлены.")
        print("   Проверьте, есть ли зарегистрированные пользователи в БД.")
