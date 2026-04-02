import random

from services.database import get_user_info, update_bonus_accrual_date
from services.quickresto_api import update_customer_bonus, print_full_client_info

"""
Формирование системы выдачи бонусов пользователю бота

cocktail - коктейль на выбор
hookah - кальян на выбор
bonus - бонус в рублях (1000)
try_tomorrow - попробуйте завтра
"""


def random_bonus():
    """Функция для выбора бонуса пользователю бота"""

    bonuses = [
        "Попробуйте завтра",
        "Попробуйте завтра",
        "Попробуйте завтра",
        "Попробуйте завтра",
        "Попробуйте завтра",
        "Коктейль на выбор",
        "Попробуйте завтра",
        "Попробуйте завтра",
        "Попробуйте завтра",
        "Попробуйте завтра",
        "Попробуйте завтра",
        "Кальян на выбор",
        "Попробуйте завтра",
        "Попробуйте завтра",
        "Попробуйте завтра",
        "Попробуйте завтра",
        "Попробуйте завтра",
        "Бонус в рублях (1000)",  # ← добавлена запятая
        "Попробуйте завтра",
        "Попробуйте завтра",
    ]
    return random.choice(bonuses)


def generate_promo_code():
    """
    Генерирует промокод в формате BLACK169-XXXXXXXXXXXXXXX

    :return: Сгенерированный промокод
    """
    prefix = "BLACK169-"
    return prefix + str(random.randint(100000000000000, 999999999999999))


def receives_information_about_user_and_accrues_bonuses(id_telegram: int, bonus_amount: float):
    """
    Функция получает информацию о пользователе из базы данных зарегистрированных пользователей, находит пользователя по
    ID Telegram, извлекает ID пользователя в QuickResto и номер телефона, затем использует API QuickResto для начисления
    бонусов.

    :param id_telegram: ID пользователя в Telegram
    :param bonus_amount: Количество бонусов
    """

    # Получаем информацию о пользователе
    user_info = get_user_info(id_telegram)
    # Начисляем например 3000 бонусов пользователю по ID пользователя в QuickResto и номеру телефона
    update_customer_bonus(
        customer_id=user_info.get("id_quickresto"),  # ID пользователя в QuickResto
        amount=bonus_amount,  # Количество бонусов
        customer_phone=user_info.get("phone_telegram"),  # Телефон пользователя в Telegram
    )


def updates_bonuses_in_the_database(id_telegram):
    """
    Функция обновляет базу данных пользователя с информацией о бонусах пользователя
    :param id_telegram: ID пользователя в Telegram
    :return:
    """
    # Получаем информацию о пользователе
    user_info = get_user_info(id_telegram)
    full_data = print_full_client_info(user_info.get("id_quickresto"))
    update_bonus_accrual_date(id_telegram=id_telegram, bonus_amount=full_data.get("bonus_ledger"))
