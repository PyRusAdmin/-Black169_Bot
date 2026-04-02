import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from utils.logger import logger

EVENTS_DIR = Path(__file__).parent.parent / "data" / "events"


def ensure_events_dir() -> None:
    """
    Убедиться, что директория для мероприятий существует
    """
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)


def get_event_file_path(event_id: str) -> Path:
    """
    Получить путь к файлу мероприятия
    """
    return EVENTS_DIR / f"{event_id}.json"


def create_event_json(
    event_id: str,
    title: str,
    description: str,
    event_date: datetime,
    created_by: int,
    photo_id: str | None = None,
    reminder_text_3days: str | None = None,
    reminder_text_1day: str | None = None,
    reminder_text_event_day: str | None = None,
) -> dict[str, Any]:
    """
    Создать мероприятие в JSON файле

    :param event_id: Уникальный ID мероприятия
    :param title: Название мероприятия
    :param description: Описание мероприятия
    :param event_date: Дата и время мероприятия
    :param created_by: ID администратора, создавшего мероприятие
    :param photo_id: ID фото мероприятия
    :param reminder_text_3days: Текст напоминания за 3 дня
    :param reminder_text_1day: Текст напоминания за 1 день
    :param reminder_text_event_day: Текст напоминания в день мероприятия
    :return: Словарь с данными мероприятия
    """
    ensure_events_dir()

    event_data = {
        "id": event_id,
        "title": title,
        "description": description,
        "event_date": event_date.isoformat(),
        "created_by": created_by,
        "created_at": datetime.now().isoformat(),
        "photo_id": photo_id,
        "reminder_text_3days": reminder_text_3days,
        "reminder_text_1day": reminder_text_1day,
        "reminder_text_event_day": reminder_text_event_day,
        "is_active": True,
        "notified_3days": False,
        "notified_1day": False,
        "notified_event_day": False,
    }

    file_path = get_event_file_path(event_id)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(event_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Мероприятие {event_id} создано в {file_path}")
        return event_data
    except Exception as e:
        logger.exception(f"Ошибка при создании мероприятия {event_id}: {e}")
        raise


def get_event_json(event_id: str) -> dict[str, Any] | None:
    """
    Получить данные мероприятия из JSON файла

    :param event_id: ID мероприятия
    :return: Словарь с данными мероприятия или None
    """
    file_path = get_event_file_path(event_id)

    if not file_path.exists():
        logger.warning(f"Файл мероприятия {event_id} не найден")
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.exception(f"Ошибка при чтении мероприятия {event_id}: {e}")
        return None


def get_all_events_json() -> list[dict[str, Any]]:
    """
    Получить все мероприятия из JSON файлов

    :return: Список словарей с данными мероприятий
    """
    ensure_events_dir()

    events = []
    for file_path in EVENTS_DIR.glob("*.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                event_data = json.load(f)
                events.append(event_data)
        except Exception as e:
            logger.exception(f"Ошибка при чтении файла {file_path}: {e}")

    # Сортируем по дате мероприятия
    events.sort(key=lambda x: x.get("event_date", ""), reverse=False)
    return events


def get_active_events_json() -> list[dict[str, Any]]:
    """
    Получить только активные мероприятия

    :return: Список активных мероприятий
    """
    all_events = get_all_events_json()
    return [event for event in all_events if event.get("is_active", False)]


def get_upcoming_events_json() -> list[dict[str, Any]]:
    """
    Получить предстоящие мероприятия (активные и дата в будущем)

    :return: Список предстоящих мероприятий
    """
    active_events = get_active_events_json()
    now = datetime.now()

    upcoming = []
    for event in active_events:
        try:
            event_date = datetime.fromisoformat(event["event_date"])
            if event_date > now:
                upcoming.append(event)
        except Exception as e:
            logger.exception(
                f"Ошибка при обработке даты мероприятия {event.get('id')}: {e}"
            )

    return upcoming


def update_event_json(event_id: str, **kwargs) -> bool:
    """
    Обновить данные мероприятия

    :param event_id: ID мероприятия
    :param kwargs: Поля для обновления
    :return: True если успешно, False если ошибка
    """
    event_data = get_event_json(event_id)
    if not event_data:
        return False

    event_data.update(kwargs)
    file_path = get_event_file_path(event_id)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(event_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Мероприятие {event_id} обновлено")
        return True
    except Exception as e:
        logger.exception(f"Ошибка при обновлении мероприятия {event_id}: {e}")
        return False


def delete_event_json(event_id: str) -> bool:
    """
    Удалить мероприятие (физически удалить файл)

    :param event_id: ID мероприятия
    :return: True если успешно, False если ошибка
    """
    file_path = get_event_file_path(event_id)

    if not file_path.exists():
        logger.warning(f"Файл мероприятия {event_id} не найден")
        return False

    try:
        os.remove(file_path)
        logger.info(f"Мероприятие {event_id} удалено")
        return True
    except Exception as e:
        logger.exception(f"Ошибка при удалении мероприятия {event_id}: {e}")
        return False


def deactivate_event_json(event_id: str) -> bool:
    """
    Деактивировать мероприятие (установить is_active = False)

    :param event_id: ID мероприятия
    :return: True если успешно, False если ошибка
    """
    return update_event_json(event_id, is_active=False)
