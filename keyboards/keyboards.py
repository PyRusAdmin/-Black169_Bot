# -*- coding: utf-8 -*-
from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def contact_keyboard():
    """Клавиатура для отправления номера телефона пользователя"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Отправить номер телефона", request_contact=True))
    return builder.as_markup(resize_keyboard=True)
