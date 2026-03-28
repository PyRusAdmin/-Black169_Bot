# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

"""Клавиатура для обычного пользователя"""


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
                InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main_menu"),
            ],
        ]
    )


def twist_keyboard():
    """Клавиатура для вращения и возврата в главное меню"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎰 Крутить 🎰", callback_data="twist"),
            ],
            [
                InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main_menu"),
            ],

        ]
    )


"""Клавиатура для администратора бота"""

"""
По желанию. Стиль кнопки. 
Должно быть: 
«опасность» (красный) - danger,  
«успех» (зелёный) - success,
«первичный» (синий) - primary. 

Если его опускают, то используется специфический для приложения стиль.
"""


def main_menu_keyboard_admin():
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
            # Администратор
            [
                InlineKeyboardButton(
                    text="⚙️ В меню администратора",
                    callback_data="admin_menu",
                    style="success",
                ),
            ],
        ]
    )


def admin_menu_keyboard():
    """Клавиатура для администратора бота"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🏆 Список победителей «Колеса подарков»", callback_data="winners"),
            ],
            [
                InlineKeyboardButton(text="👥 Список пользователей", callback_data="users"),
                InlineKeyboardButton(text="✅ Зарегистрированные", callback_data="registered_users"),
            ],
            [
                InlineKeyboardButton(text="📨 Рассылка сообщений", callback_data="broadcast"),
            ],
            [
                InlineKeyboardButton(text="📊 Статистика пользователей", callback_data="stats"),
            ],
            [
                InlineKeyboardButton(text="🗑️ Удалить пользователя", callback_data="delete_user"),
            ],
        ]
    )


def back_to_admin_menu_keyboard():
    """Клавиатура для возврата в меню администратора"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔧 В меню администратора", callback_data="admin_back"),
            ],
        ]
    )


def broadcast_type_keyboard():
    """Клавиатура выбора типа сообщения для рассылки"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📝 Текст", callback_data="broadcast_text"),
            ],
            [
                InlineKeyboardButton(text="🖼️ Фото", callback_data="broadcast_photo"),
            ],
            [
                InlineKeyboardButton(text="🎥 Видео", callback_data="broadcast_video"),
            ],
            [
                InlineKeyboardButton(text="❌ Отмена", callback_data="broadcast_cancel"),
            ],
        ]
    )


def broadcast_confirm_keyboard():
    """Клавиатура подтверждения отправки рассылки"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Отправить", callback_data="broadcast_confirm_send"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="broadcast_cancel"),
            ],
        ]
    )
