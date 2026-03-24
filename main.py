# -*- coding: utf-8 -*-
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, F, Router

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from loguru import logger

from config import TOKEN
from keyboards.keyboards import contact_keyboard
from services.database import create_tables, write_to_db_person

router = Router(name=__name__)

dp = Dispatcher()
dp.include_router(router)

logger.add("log/log.log")

greet_message = (
    "Добро пожаловать в The Black 169 🖤\n\n"
    "В этом боте вы сможете:\n"
    "🔹 проверять бонусы\n"
    "🎁 узнать акции\n"
    "🎀 получать подарки\n"
    "📅 следить за мероприятиями\n\n"
    "Отправьте свой номер телефона, чтобы начать 📱\n"
)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Этот обработчик получает сообщения с командой '/start'
    """
    id_telegram = message.from_user.id
    name_telegram = message.from_user.first_name
    first_name_telegram = message.from_user.last_name
    username_telegram = message.from_user.username
    phone_telegram = ""

    write_to_db_person(
        id_telegram=id_telegram,
        last_name_telegram=name_telegram,
        first_name_telegram=first_name_telegram,
        username_telegram=username_telegram,
        phone_telegram=phone_telegram
    )

    await message.answer(
        text=greet_message,
        reply_markup=contact_keyboard()
    )


@router.message(F.contact)
async def message_handler(message: Message) -> None:
    """
    Обработчик сообщений
    """
    id_telegram = message.from_user.id
    name_telegram = message.from_user.first_name
    first_name_telegram = message.from_user.last_name
    username_telegram = message.from_user.username
    phone_telegram = message.contact.phone_number
    logger.info(f"Пользователь отправил контакт: {phone_telegram}")

    write_to_db_person(
        id_telegram=id_telegram,
        last_name_telegram=name_telegram,
        first_name_telegram=first_name_telegram,
        username_telegram=username_telegram,
        phone_telegram=phone_telegram
    )


async def main() -> None:
    create_tables()  # Создание таблицы в базе данных

    # Initialize Bot Instance with default properties that will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # И распределение событий на забегах
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
