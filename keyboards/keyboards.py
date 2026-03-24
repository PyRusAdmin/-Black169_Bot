# -*- coding: utf-8 -*-
from aiogram.types import KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def contact_keyboard():
    """Клавиатура для отправления номера телефона пользователя"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Отправить номер телефона", request_contact=True))
    return builder.as_markup(resize_keyboard=True)


def main_menu_keyboard():
    """Клавиатура главного меню, которое будет только после того, как пользователь отправит свой номер телефона"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💰 Мои бонусы",
                    callback_data="my_bonuses",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎁 Забрать подарок",
                    callback_data="pick_up_gift",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔥 Бонусы скоро сгорят",
                    callback_data="bonuses_will_soon_burn_out",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎉 Акции",
                    callback_data="promotions",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📅 Мероприятия",
                    callback_data="events",
                )
            ],

            [
                InlineKeyboardButton(
                    text="📍 Контакты",
                    callback_data="contacts",
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ О заведении",
                    callback_data="about_institution",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔥 Вернуться сегодня",
                    callback_data="back_today",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎡 Колесо подарков",
                    callback_data="gift_wheel",
                )
            ],
        ]
    )
