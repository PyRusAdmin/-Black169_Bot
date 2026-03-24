# -*- coding: utf-8 -*-
import asyncio
import logging
import sys

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from loguru import logger

from handlers.admin_handlers import router as admin_handlers
from handlers.user_handlers import router as user_handlers
from handlers.handlers import router as handlers

from config import TOKEN, dp
from services.database import create_tables

logger.add("log/log.log")


async def main() -> None:
    create_tables()  # Создание таблицы в базе данных

    dp.include_router(handlers)  # Общие хендлеры
    dp.include_router(user_handlers)  # Хендлеры для пользователей
    dp.include_router(admin_handlers)  # Хендлеры для администраторов

    # Initialize Bot Instance with default properties that will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # И распределение событий на забегах
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
