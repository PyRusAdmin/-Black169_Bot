# -*- coding: utf-8 -*-
import asyncio
import logging
import sys

from config import dp, bot
from handlers.admin_handlers import router as admin_handlers
from handlers.handlers import router as handlers
from handlers.menu_handlers import router as menu_handlers
from handlers.user_handlers import router as user_handlers
from services.database import create_tables
from services.birthday_service import send_birthday_bonus
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

    # Запускаем планировщик дней рождения в фоновом режиме
    asyncio.create_task(birthday_scheduler())

    # И распределение событий на забегах
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
