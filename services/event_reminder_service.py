"""
Сервис автоматических рассылок напоминаний о мероприятиях

Проверяет мероприятия и отправляет напоминания:
- За 3 дня до мероприятия
- За 1 день до мероприятия
- В день мероприятия
"""
import asyncio

from config import OWNER_IDS, bot
from services.database import (
    get_all_user_ids, get_events_for_reminder, update_reminder_sent,
)
from utils.logger import logger


async def send_event_reminders(days_until: int, reminder_type: str) -> dict:
    """
    Отправка напоминаний о мероприятиях

    :param days_until: За сколько дней до мероприятия (3, 1, 0)
    :param reminder_type: Тип напоминания для обновления статуса (3days, 1day, event_day)
    :return: Статистика отправленных сообщений
    """
    logger.info(f"Начало рассылки напоминаний за {days_until} дн.")

    # Получаем мероприятия для напоминания
    events = get_events_for_reminder(days_until)

    if not events:
        logger.info(f"Нет мероприятий для напоминания за {days_until} дн.")
        return {"sent": 0, "failed": 0}

    # Получаем всех пользователей (исключая администраторов)
    user_ids = get_all_user_ids()
    user_ids = [uid for uid in user_ids if uid not in OWNER_IDS]

    total_sent = 0
    total_failed = 0

    for event in events:
        reminder_text = event.get("reminder_text")
        if not reminder_text:
            logger.warning(f"Мероприятие {event['id']} не имеет текста напоминания")
            continue

        # Формируем сообщение
        event_date = event["event_date"].strftime("%d.%m.%Y %H:%M")
        message = f"{reminder_text}\n\n📅 Дата: {event_date}"

        for user_id in user_ids:
            try:
                # Если есть фото, отправляем с фото
                if event.get("photo_id"):
                    await bot.send_photo(
                        chat_id=user_id,
                        photo=event["photo_id"],
                        caption=message,
                        parse_mode="HTML",
                    )
                else:
                    await bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode="HTML",
                    )
                total_sent += 1

                # Небольшая задержка для избежания лимитов Telegram
                await asyncio.sleep(0.05)

            except Exception as e:
                if "bot was blocked" in str(e).lower():
                    logger.warning(f"Пользователь {user_id} заблокировал бота")
                else:
                    logger.error(
                        f"Ошибка при отправке напоминания пользователю {user_id}: {e}"
                    )
                total_failed += 1

        # Обновляем статус отправленного напоминания
        update_reminder_sent(event["id"], reminder_type)
        logger.info(
            f"Отправлено напоминание за {days_until} дн. для мероприятия {event['id']}"
        )

    logger.info(
        f"Рассылка напоминаний завершена: отправлено {total_sent}, ошибок {total_failed}"
    )
    return {"sent": total_sent, "failed": total_failed}


async def check_and_send_reminders():
    """
    Проверка и отправка всех типов напоминаний
    Вызывается планировщиком каждый день в 00:00
    """
    logger.info("Проверка напоминаний о мероприятиях")

    try:
        # Напоминание за 3 дня
        result_3days = await send_event_reminders(days_until=3, reminder_type="3days")

        # Напоминание за 1 день
        result_1day = await send_event_reminders(days_until=1, reminder_type="1day")

        # Напоминание в день мероприятия
        result_event_day = await send_event_reminders(
            days_until=0, reminder_type="event_day"
        )

        logger.info(
            f"Итоги рассылки напоминаний:\n"
            f"  За 3 дня: отправлено {result_3days['sent']}, ошибок {result_3days['failed']}\n"
            f"  За 1 день: отправлено {result_1day['sent']}, ошибок {result_1day['failed']}\n"
            f"  В день мероприятия: отправлено {result_event_day['sent']}, ошибок {result_event_day['failed']}"
        )

    except Exception as e:
        logger.exception(f"Ошибка при проверке напоминаний: {e}")
        logger.exception(f"Ошибка при проверке напоминаний: {e}")
