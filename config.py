# -*- coding: utf-8 -*-
import os

from aiogram import Dispatcher
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# Токен бота можно получить с помощью https://t.me/BotFather
TOKEN: str = os.getenv("BOT_TOKEN")
logger.info(f"Bot token: {TOKEN}")

"""QuickResto API"""

layer_name_quickresto: str = os.getenv("LAYER_NAME_QUICKRESTO")  # Извлекаем значение из .env файла
username_quickresto: str = os.getenv("USERNAME_QUICKRESTO")  # Извлекаем значение из .env файла
password_quickresto: str = os.getenv("PASSWORD_QUICKRESTO")  # Извлекаем значение из .env файла

dp = Dispatcher()
