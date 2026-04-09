from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
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
        resize_keyboard=True, one_time_keyboard=True  # Скрыть после использования
    )


def new_section_keyboard():
    """Клавиатура специальных предложений"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎁 Забрать подарок", callback_data="pick_up_gift"

                ),
                InlineKeyboardButton(
                    text="🔥 Бонусы скоро сгорят",
                    callback_data="bonuses_will_soon_burn_out",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔥 Вернуться сегодня", callback_data="back_today"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🏠 В главное меню",
                    callback_data="back_to_main_menu",
                    style="danger",
                ),
            ],
        ]
    )


"""Клавиатура для обычного пользователя"""


def main_menu_keyboard():
    """Клавиатура главного меню после авторизации"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            # Бонусы и подарки
            [
                InlineKeyboardButton(text="💰 Мои бонусы", callback_data="my_bonuses"),
                InlineKeyboardButton(text="🎡 Колесо подарков", callback_data="gift_wheel"),
            ],
            # Акции и мероприятия
            [
                InlineKeyboardButton(text="🎉 Акции", callback_data="promotions"),
                InlineKeyboardButton(text="📅 Мероприятия", callback_data="events"),
            ],
            # Специальные предложения
            [
                InlineKeyboardButton(text="💫 Специальные предложения", callback_data="special_offers"),
            ],
            # Информация
            [
                InlineKeyboardButton(text="📍 Контакты", callback_data="contacts"),
                InlineKeyboardButton(
                    text="ℹ️ О заведении", callback_data="about_institution"
                ),
            ],
        ]
    )


def contacts_keyboard():
    """Клавиатура для контактов"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📞 Позвонить", url="tel:+79147911911"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🏠 В главное меню",
                    callback_data="back_to_main_menu",
                    style="danger",
                ),
            ],
        ]
    )


def back_to_main_menu_keyboard():
    """Клавиатура для возврата в главное меню"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏠 В главное меню",
                    callback_data="back_to_main_menu",
                    style="danger",
                ),
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
                InlineKeyboardButton(
                    text="🏠 В главное меню",
                    callback_data="back_to_main_menu",
                    style="danger",
                ),
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
                InlineKeyboardButton(text="🎡 Колесо подарков", callback_data="gift_wheel"),
            ],
            # Акции и мероприятия
            [
                InlineKeyboardButton(text="🎉 Акции", callback_data="promotions"),
                InlineKeyboardButton(text="📅 Мероприятия", callback_data="events"),
            ],
            # Специальные предложения
            [
                InlineKeyboardButton(text="💫 Специальные предложения", callback_data="special_offers"),
            ],
            # Информация
            [
                InlineKeyboardButton(text="📍 Контакты", callback_data="contacts"),
                InlineKeyboardButton(
                    text="ℹ️ О заведении", callback_data="about_institution"
                ),
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
                InlineKeyboardButton(
                    text="🏆 Список победителей «Колеса подарков»",
                    callback_data="winners",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👥 Список пользователей", callback_data="users"
                ),
                InlineKeyboardButton(
                    text="✅ Зарегистрированные", callback_data="registered_users"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📨 Рассылка сообщений", callback_data="broadcast"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📊 Статистика пользователей", callback_data="stats"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Анализ и синхронизация клиентов",
                    callback_data="analyze_clients",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🗑️ Удалить пользователя", callback_data="delete_user"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔍 Поиск пользователя по номеру телефона",
                    callback_data="search_user",
                ),
            ],
            [
                InlineKeyboardButton(text="🎁 Промокоды", callback_data="promo_menu"),
            ],
            [
                InlineKeyboardButton(
                    text="📅 Мероприятия", callback_data="events_menu"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👥 Управление администраторами", callback_data="admins_menu"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🏠 В главное меню",
                    callback_data="back_to_main_menu",
                    style="danger",
                ),
            ],
        ]
    )


def back_to_admin_menu_keyboard():
    """Клавиатура для возврата в меню администратора"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔧 В меню администратора", callback_data="admin_back", style="danger"
                ),
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
                InlineKeyboardButton(
                    text="❌ Отмена", callback_data="broadcast_cancel", style="danger"
                ),
            ],
        ]
    )


def broadcast_confirm_keyboard():
    """Клавиатура подтверждения отправки рассылки"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Отправить", callback_data="broadcast_confirm_send", style="success"
                ),
                InlineKeyboardButton(
                    text="❌ Отмена", callback_data="broadcast_cancel", style="danger"
                ),
            ],
        ]
    )


def promo_codes_menu_keyboard():
    """Клавиатура управления промокодами для админ-панели"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Создать промокод", callback_data="promo_create"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📋 Список промокодов", callback_data="promo_list"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🗑️ Удалить промокод", callback_data="promo_delete"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔧 В меню администратора", callback_data="admin_back", style="danger"
                ),
            ],
        ]
    )


def back_to_promo_menu_keyboard():
    """Клавиатура возврата в меню промокодов"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙 В меню промокодов", callback_data="promo_menu", style="danger"
                ),
            ],
        ]
    )


def consent_keyboard():
    """Клавиатура для получения согласия на обработку персональных данных"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Даю согласие на обработку персональных данных",
                    callback_data="consent_given",
                    style="success",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="❌ Не даю согласие",
                    callback_data="consent_declined",
                    style="danger",
                ),
            ],
        ]
    )


def events_menu_keyboard():
    """Клавиатура управления мероприятиями для админ-панели"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Создать мероприятие", callback_data="event_create"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📋 Список мероприятий", callback_data="event_list"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🗑️ Удалить мероприятие", callback_data="event_delete"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔧 В меню администратора", callback_data="admin_back", style="danger"
                ),
            ],
        ]
    )


def back_to_events_menu_keyboard():
    """Клавиатура возврата в меню мероприятий"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙 В меню мероприятий", callback_data="events_menu", style="danger"
                ),
            ],
        ]
    )


def event_action_keyboard(event_id: int):
    """Клавиатура действий с мероприятием"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Активировать", callback_data=f"event_activate_{event_id}"
                ),
                InlineKeyboardButton(
                    text="⏸️ Деактивировать",
                    callback_data=f"event_deactivate_{event_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🗑️ Удалить", callback_data=f"event_delete_{event_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔙 В список мероприятий", callback_data="event_list", style="secondary"
                ),
            ],
        ]
    )


def event_confirm_keyboard():
    """Клавиатура подтверждения создания мероприятия"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да, создать", callback_data="event_confirm_yes"
                ),
                InlineKeyboardButton(
                    text="❌ Нет, отмена", callback_data="event_confirm_no"
                ),
            ],
        ]
    )


def admins_menu_keyboard():
    """Клавиатура управления администраторами"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Добавить администратора", callback_data="admin_add"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📋 Список администраторов", callback_data="admin_list"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🗑️ Удалить администратора", callback_data="admin_remove"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔧 В меню администратора", callback_data="admin_back"
                ),
            ],
        ]
    )


def back_to_admins_menu_keyboard():
    """Клавиатура возврата в меню администраторов"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙 В управление администраторами", callback_data="admins_menu"
                ),
            ],
        ]
    )
