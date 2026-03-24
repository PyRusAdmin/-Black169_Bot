# -*- coding: utf-8 -*-
import os

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# Токен бота можно получить с помощью https://t.me/BotFather
TOKEN: str = os.getenv("BOT_TOKEN")
logger.info(f"Bot token: {TOKEN}")
