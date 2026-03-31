from aiogram.utils.keyboard import ReplyKeyboardBuilder


def contact_keyboard():
    """
    Клавиатура для отправки номера телефона пользователя
    """
    builder = ReplyKeyboardBuilder()
    builder.button(text="📱 Отправить номер телефона", request_contact=True)
    return builder.as_markup(resize_keyboard=True)
