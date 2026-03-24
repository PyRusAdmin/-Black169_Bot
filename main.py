import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import TOKEN
from keyboards.keyboards import contact_keyboard

dp = Dispatcher()

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
    await message.answer(
        text=greet_message,
        reply_markup=contact_keyboard()
    )


async def main() -> None:
    # Initialize Bot Instance with default properties that will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # И распределение событий на забегах
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
