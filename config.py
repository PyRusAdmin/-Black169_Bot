# -*- coding: utf-8 -*-
import os

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
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

"""Считывание данных прокси из файла .env"""
USER_PROXY = os.getenv('USER_PROXY')
PASSWORD_PROXY = os.getenv('PASSWORD_PROXY')
PORT_PROXY = os.getenv('PORT_PROXY')
IP_PROXY = os.getenv('IP_PROXY')

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Используем SOCKS5 прокси через URL
session = AiohttpSession(proxy=f"socks5://{USER_PROXY}:{PASSWORD_PROXY}@{IP_PROXY}:{PORT_PROXY}")

# Initialize Bot Instance with default properties that will be passed to all API calls
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    session=session
)
