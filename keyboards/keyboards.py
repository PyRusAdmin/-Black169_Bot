from aiogram.utils.keyboard import ReplyKeyboardBuilder


def contact_keyboard():
    """
    Клавиатура для отправки номера телефона пользователя
    """
    builder = ReplyKeyboardBuilder()
    builder.button(
        text="📱 Отправить номер телефона (нажмите сюда)",
        request_contact=True,  # Запрос контакта
        style="danger",  # Кнопка красного цвета
    )
    builder.adjust(1)  # Кнопка на всю ширину
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True  # Скрыть после использования
    )
