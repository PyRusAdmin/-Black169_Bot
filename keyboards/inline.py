# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard():
    """Клавиатура главного меню после авторизации"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            # Бонусы и подарки
            [
                InlineKeyboardButton(text="💰 Мои бонусы", callback_data="my_bonuses"),
                InlineKeyboardButton(text="🎁 Забрать подарок", callback_data="pick_up_gift"),
            ],
            [
                InlineKeyboardButton(text="🔥 Бонусы скоро сгорят", callback_data="bonuses_will_soon_burn_out"),
                InlineKeyboardButton(text="🎡 Колесо подарков", callback_data="gift_wheel"),
            ],
            # Акции и мероприятия
            [
                InlineKeyboardButton(text="🎉 Акции", callback_data="promotions"),
                InlineKeyboardButton(text="📅 Мероприятия", callback_data="events"),
            ],
            # Маркетинг
            [
                InlineKeyboardButton(text="🔥 Вернуться сегодня", callback_data="back_today"),
            ],
            # Информация
            [
                InlineKeyboardButton(text="📍 Контакты", callback_data="contacts"),
                InlineKeyboardButton(text="ℹ️ О заведении", callback_data="about_institution"),
            ],
        ]
    )


def back_to_main_menu_keyboard():
    """Клавиатура для возврата в главное меню"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="В главное меню", callback_data="back_to_main_menu"),
            ],
        ]
    )


def twist_keyboard():
    """Клавиатура для вращения и возврата в главное меню"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Крутить 🎰", callback_data="twist"),
            ],
            [
                InlineKeyboardButton(text="В главное меню", callback_data="back_to_main_menu"),
            ],

        ]
    )
