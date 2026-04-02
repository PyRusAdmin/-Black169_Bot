from aiogram import F, Router
from aiogram.types import CallbackQuery

from keyboards.keyboards import back_to_main_menu_keyboard, twist_keyboard
from services.bonus import random_bonus, generate_promo_code
# Формируем сообщение с уровнем клиента
from services.client_levels import get_level_description, get_next_level_info
from services.database import (
    get_user_bonus, has_user_spun_today, update_bonus_accrual_date, write_spin_result, write_to_db_registered_person,
)
# Формируем сообщение с информацией о бонусах пользователя
from services.database import get_user_burning_bonus_info
from services.database import (
    has_user_claimed_gift_bonus, mark_gift_bonus_claimed, get_user_info,
)
from services.i18n import t
from services.quickresto_api import (
    print_full_client_info, update_customer_bonus,
)
from utils.logger import logger

router = Router(name=__name__)


@router.callback_query(F.data == "my_bonuses")
async def my_bonuses_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки '💰 Мои бонусы'
    :param callback: CallbackQuery
    """
    logger.info(f"Пользователь {callback.from_user.id} нажал 'Мои бонусы'")

    # Получаем баланс бонусов пользователя
    id_quickresto, phone_telegram = get_user_bonus(callback.from_user.id)
    data = print_full_client_info(client_id=id_quickresto)

    data = {
        "id_telegram": callback.from_user.id,
        "id_quickresto": data.get("id"),
        "last_name": data.get("last_name"),
        "first_name": data.get("first_name"),
        "patronymic_name": data.get("middle_name"),
        "birthday_user": data.get("date_of_birth"),
        "user_bonus": data.get("bonus_ledger"),
        "phone_telegram": phone_telegram,
        "client_level": data.get("level"),  # Уровень клиента
        "accumulation_amount": data.get("accumulation_balance", {}).get(
            "ledger", 0
        ),  # Накопительная сумма
    }

    write_to_db_registered_person(data)

    # Получаем бонусы из БД
    user_info = get_user_info(callback.from_user.id)
    user_bonus = user_info.get("user_bonus") if user_info else None
    client_level = user_info.get("client_level") if user_info else None
    accumulation_amount = user_info.get("accumulation_amount") if user_info else None

    level_text = ""
    if client_level:
        level_text = f"{get_level_description(client_level)}\n\n"

        # Информация о следующем уровне
        if accumulation_amount:
            next_level_info = get_next_level_info(client_level, accumulation_amount)
            if next_level_info["has_next"]:
                level_text += f"📈 {next_level_info['message']}\n"
            else:
                level_text += f"🏆 {next_level_info['message']}\n"

    await callback.message.answer(
        text=(
            f"<b>Ваш ID: {id_quickresto}</b>\n"
            f"💰 <b>Ваши бонусы: {user_bonus}</b>\n\n"
            f"{level_text}"
            f"Используйте их при следующем посещении!"
        ),
        reply_markup=back_to_main_menu_keyboard(),
    )

    await callback.answer()


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


@router.callback_query(F.data == "pick_up_gift")
async def pick_up_gift_handler(callback: CallbackQuery) -> None:
    """Обработчик кнопки 'Забрать подарок'"""
    logger.info(f"Пользователь {callback.from_user.id} нажал 'Забрать подарок'")
    # Проверяем, получал ли пользователь подарок ранее
    is_claimed = has_user_claimed_gift_bonus(callback.from_user.id)
    logger.info(is_claimed)

    if is_claimed == False:
        promo_code = generate_promo_code()
        logger.info(f"Сгенерирован промокод: {promo_code} для пользователя {callback.from_user.id}")

        # Получает информацию о пользователе и начисляет бонусы
        receives_information_about_user_and_accrues_bonuses(id_telegram=callback.from_user.id, bonus_amount=3000.00)

        # Отмечаем, что пользователь получил подарок
        mark_gift_bonus_claimed(id_telegram=callback.from_user.id, promo_code=promo_code)
        # Обновляем дату начисления бонусов (для отслеживания сгорания)
        update_bonus_accrual_date(callback.from_user.id, bonus_amount=3000.00)

        await callback.message.answer(
            text=(
                "🎁 <b>Поздравляем!</b>\n\n"
                "Вам начислено <b>3000 бонусов</b>!\n\n"
                f"Ваш промокод: <code>{promo_code}</code>\n"
                f"Для получения бонусов, покажите промокод администратору\n\n"
                "Используйте их при следующем посещении The Black 169.\n\n"
                "Спасибо, что вы с нами! 🖤"
            ),
            reply_markup=back_to_main_menu_keyboard(),
        )
        await callback.answer()

    elif is_claimed == True:
        await callback.message.edit_text(
            text=(
                "❌ <b>Вы уже получили подарочные бонусы</b>\n\n"
                "Подарочные бонусы можно получить только один раз.\n\n"
                "Спасибо, что вы с нами! 🖤"
            ),
            reply_markup=back_to_main_menu_keyboard(),
        )
        await callback.answer()
        return


@router.callback_query(F.data == "bonuses_will_soon_burn_out")
async def bonuses_will_soon_burn_out_handler(callback: CallbackQuery) -> None:
    """Обработчик кнопки 'Бонусы скоро сгорят'"""
    logger.info(f"Пользователь {callback.from_user.id} нажал 'Бонусы скоро сгорят'")

    # Получаем информацию о сгорающих бонусах
    burning_info = get_user_burning_bonus_info(callback.from_user.id)

    if burning_info:
        # Сумма бонусов, начисленных ботом
        bot_bonus_amount = burning_info.get("bot_bonus_amount")
        burn_date = burning_info.get("burn_date")
        days_until_burn = burning_info.get("days_until_burn")

        burn_date_str = burn_date.strftime("%d.%m.%Y")

        if days_until_burn <= 1:
            warning_emoji = "❗"
            warning_text = "завтра" if days_until_burn == 1 else "сегодня"
        elif days_until_burn <= 3:
            warning_emoji = "🔥"
            warning_text = f"через {days_until_burn} дня"
        elif days_until_burn <= 7:
            warning_emoji = "⚠️"
            warning_text = f"через {days_until_burn} дней"
        else:
            warning_emoji = "⏰"
            warning_text = f"через {days_until_burn} дней"

        message_text = (
            f"{warning_emoji} <b>Бонусы скоро сгорят!</b>\n\n"
            f"Напоминаем, что {warning_text} сгорят бонусы, начисленные нашим ботом.\n\n"
            f"💰 Сумма бонусов: <b>{bot_bonus_amount} бонусов</b>\n"
            f"📅 Дата сгорания: <b>{burn_date_str}</b>\n\n"
            f"Успейте использовать бонусы до этой даты!\n\n"
            f"Ждём Вас в The Black 169! 🖤"
        )
    else:
        message_text = (
            "✅ <b>У вас нет бонусов, которые скоро сгорят</b>\n\n"
            "Все ваши бонусы в безопасности! 🖤"
        )

    await callback.message.answer(
        text=message_text, reply_markup=back_to_main_menu_keyboard()
    )
    await callback.answer()


"""Колесо подарков, которое выдается пользователю рандомно. Шанс выпадения 5 процентов"""


@router.callback_query(F.data == "gift_wheel")
async def gift_wheel_handler(callback: CallbackQuery) -> None:
    """Обработчик кнопки 'Колесо подарков'"""
    logger.info(f"Пользователь {callback.from_user.id} нажал 'Колесо подарков'")
    await callback.message.answer(
        text=t("menu-gift-wheel"), reply_markup=twist_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "twist")
async def twist_handler(callback: CallbackQuery) -> None:
    """Обработчик кнопки 'Крутить'. Шанс выпадения бонуса 5 процентов"""
    logger.info(f"Пользователь {callback.from_user.id} нажал 'Крутить'")

    id_telegram = callback.from_user.id

    # Проверяем, участвовал ли пользователь сегодня
    if has_user_spun_today(id_telegram):
        await callback.message.answer(
            text=(
                "⛔️ Вы уже участвовали в розыгрыше сегодня.\n\n"
                "Приходите завтра — у вас будет новая попытка выиграть подарок! 🍀"
            ),
            reply_markup=back_to_main_menu_keyboard(),
        )
        await callback.answer()
        return

    # Получаем ID пользователя в QuickResto
    user_info = get_user_info(id_telegram)
    id_quickresto = user_info.get("id_quickresto") if user_info else None
    phone_telegram = user_info.get("phone_telegram") if user_info else None

    bonus = random_bonus()  # получаем случайный бонус из списка бонусов
    logger.info(f"Пользователь {id_telegram} выиграл бонус {bonus}")

    # Определяем, является ли пользователь победителем
    is_winner = bonus != "Попробуйте завтра"

    # Записываем результат в базу данных
    write_spin_result(
        {
            "id_telegram": id_telegram,
            "id_quickresto": id_quickresto,
            "bonus_name": bonus,
            "is_winner": is_winner,
        },
    )

    if bonus == "Коктейль на выбор":
        await callback.message.answer(
            text=t("cocktail-winning-message"),
            reply_markup=back_to_main_menu_keyboard(),
        )
        return
    if bonus == "Кальян на выбор":
        await callback.message.answer(
            text=t("hookah-winning-message"), reply_markup=back_to_main_menu_keyboard()
        )
        return
    if bonus == "Бонус в рублях (1000)":
        await callback.message.answer(
            text=t("bonus-winning-message"), reply_markup=back_to_main_menu_keyboard()
        )
        # Добавляем бонус клиенту, если выпал денежный бонус
        update_customer_bonus(
            customer_id=id_quickresto,  # ID клиента в QuickResto
            amount=1000.00,  # Сумма бонуса в рублях
            customer_phone=phone_telegram,  # Телефон клиента в QuickResto
        )

        # Обновляем дату начисления бонусов (для отслеживания сгорания)
        update_bonus_accrual_date(id_telegram, bonus_amount=1000.00)

        return
    if bonus == "Попробуйте завтра":
        await callback.message.answer(
            text=t("try-tomorrow-winning-message"),
            reply_markup=back_to_main_menu_keyboard(),
        )
        return


@router.callback_query(F.data == "promotions")
async def promotions_handler(callback: CallbackQuery) -> None:
    """Обработчик кнопки 'Акции'"""
    logger.info(f"Пользователь {callback.from_user.id} нажал 'Акции'")
    await callback.message.answer(
        text=t("menu-promotions"), reply_markup=back_to_main_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "events")
async def events_handler(callback: CallbackQuery) -> None:
    """Обработчик кнопки 'Мероприятия'"""
    logger.info(f"Пользователь {callback.from_user.id} нажал 'Мероприятия'")
    await callback.message.answer(
        text=t("menu-events"), reply_markup=back_to_main_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "back_today")
async def back_today_handler(callback: CallbackQuery) -> None:
    """Обработчик кнопки 'Вернуться сегодня'"""
    logger.info(f"Пользователь {callback.from_user.id} нажал 'Вернуться сегодня'")
    await callback.message.answer(
        text=t("menu-back-today"), reply_markup=back_to_main_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "contacts")
async def contacts_handler(callback: CallbackQuery) -> None:
    """Обработчик кнопки '📍 Контакты'"""
    logger.info(f"Пользователь {callback.from_user.id} нажал '📍 Контакты'")
    await callback.message.answer(
        text=t("menu-contacts"), reply_markup=back_to_main_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "about_institution")
async def about_institution_handler(callback: CallbackQuery) -> None:
    """Обработчик кнопки 'ℹ️ О заведении'"""
    logger.info(f"Пользователь {callback.from_user.id} нажал 'ℹ️ О заведении'")
    await callback.message.answer(
        text=t("menu-about-institution"), reply_markup=back_to_main_menu_keyboard()
    )
    await callback.answer()
