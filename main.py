import asyncio
import logging
import sys

from config import bot, dp
from handlers.admin_handlers import router as admin_handlers
from handlers.event_handlers import router as event_handlers
from handlers.handlers import router as handlers
from handlers.menu_handlers import router as menu_handlers
from handlers.user_handlers import router as user_handlers
from services.birthday_service import send_birthday_bonus
from services.bonus_burn_service import check_all_burningBonuses
from services.database import create_tables
from utils.logger import logger


async def birthday_scheduler():
    """
    Планировщик для ежедневной проверки дней рождения
    Запускается каждый день в 00:00
    """
    logger.info("Планировщик дней рождения запущен")

    while True:
        try:
            # Ждём до 00:00 следующего дня
            now = asyncio.get_event_loop().time()
            next_midnight = 86400 - (now % 86400)  # Секунд до полуночи

            logger.info(f"Следующая проверка дней рождения через {next_midnight:.0f} секунд")
            await asyncio.sleep(next_midnight)

            # Запускаем проверку дней рождения
            await send_birthday_bonus()

        except Exception as e:
            logger.exception(f"Ошибка в планировщике дней рождения: {e}")
            await asyncio.sleep(3600)  # Ждём час при ошибке


async def bonus_burn_scheduler():
    """
    Планировщик для ежедневной проверки сгорания бонусов
    Запускается каждый день в 00:00 (после проверки дней рождения)
    """
    logger.info("Планировщик сгорания бонусов запущен")

    while True:
        try:
            # Ждём до 00:00 следующего дня
            now = asyncio.get_event_loop().time()
            next_midnight = 86400 - (now % 86400)  # Секунд до полуночи

            logger.info(f"Следующая проверка сгорания бонусов через {next_midnight:.0f} секунд")
            await asyncio.sleep(next_midnight)

            # Запускаем проверку сгорания бонусов (7, 3, 1 день)
            await check_all_burningBonuses()

        except Exception as e:
            logger.exception(f"Ошибка в планировщике сгорания бонусов: {e}")
            await asyncio.sleep(3600)  # Ждём час при ошибке


async def main() -> None:
    """
    Точка входа в приложение
    """
    logger.info("Запуск приложения")

    create_tables()  # Создание таблицы в базе данных

    dp.include_router(handlers)  # Общие хендлеры
    dp.include_router(user_handlers)  # Хендлеры для пользователей
    dp.include_router(menu_handlers)  # Хендлеры главного меню
    dp.include_router(admin_handlers)  # Хендлеры для администраторов
    dp.include_router(event_handlers)  # Хендлеры мероприятий

    # Запускаем планировщики в фоновом режиме
    scheduler_tasks = [asyncio.create_task(birthday_scheduler()), asyncio.create_task(bonus_burn_scheduler())]

    try:
        # Запуск polling
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки (Ctrl+C)")
    finally:
        # Корректное завершение планировщиков
        for task in scheduler_tasks:
            task.cancel()
        await asyncio.gather(*scheduler_tasks, return_exceptions=True)
        logger.info("Приложение корректно завершено")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
