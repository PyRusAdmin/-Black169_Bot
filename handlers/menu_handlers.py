# -*- coding: utf-8 -*-
from aiogram import F, Router
from aiogram.types import CallbackQuery
from utils.logger import logger

from config import layer_name_quickresto
from keyboards.inline import back_to_main_menu_keyboard, twist_keyboard
from services.bonus import random_bonus
from services.database import (
    get_user_bonus, get_user_info, has_user_spun_today, write_spin_result, write_to_db_registered_person,
    update_bonus_accrual_date
)
from services.i18n import t
from services.quickresto_api import print_full_client_info, update_customer_bonus, auth, headers

router = Router(name=__name__)


@router.callback_query(F.data == "my_bonuses")
async def my_bonuses_handler(callback: CallbackQuery) -> None:
    """Обработчик кнопки 'Мои бонусы'"""
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
        "phone_telegram": phone_telegram
    }

    write_to_db_registered_person(data)

    # Получаем бонусы из БД
    user_info = get_user_info(callback.from_user.id)
    user_bonus = user_info.get("user_bonus") if user_info else None

    await callback.message.answer(
        text=f"💰 Ваши бонусы: <b>{user_bonus}</b>\n\nИспользуйте их при следующем посещении!",
        reply_markup=back_to_main_menu_keyboard()
    )

    await callback.answer()


@router.callback_query(F.data == "pick_up_gift")
async def pick_up_gift_handler(callback: CallbackQuery) -> None:
    """Обработчик кнопки 'Забрать подарок'"""
    logger.info(f"Пользователь {callback.from_user.id} нажал 'Забрать подарок'")
    await callback.message.answer(
        text=t("menu-pick-up-gift"),
        reply_markup=back_to_main_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "bonuses_will_soon_burn_out")
async def bonuses_will_soon_burn_out_handler(callback: CallbackQuery) -> None:
    """Обработчик кнопки 'Бонусы скоро сгорят'"""
    logger.info(f"Пользователь {callback.from_user.id} нажал 'Бонусы скоро сгорят'")
    await callback.message.answer(
        text=t("menu-bonuses-will-soon-burn-out"),
        reply_markup=back_to_main_menu_keyboard()
    )
    await callback.answer()


"""Колесо подарков, которое выдается пользователю рандомно. Шанс выпадения 5 процентов"""


@router.callback_query(F.data == "gift_wheel")
async def gift_wheel_handler(callback: CallbackQuery) -> None:
    """Обработчик кнопки 'Колесо подарков'"""
    logger.info(f"Пользователь {callback.from_user.id} нажал 'Колесо подарков'")
    await callback.message.answer(
        text=t("menu-gift-wheel"),
        reply_markup=twist_keyboard()
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
            reply_markup=back_to_main_menu_keyboard()
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
    is_winner = bonus != 'Попробуйте завтра'

    # Записываем результат в базу данных
    write_spin_result({
        "id_telegram": id_telegram,
        "id_quickresto": id_quickresto,
        "bonus_name": bonus,
        "is_winner": is_winner
    })

    if bonus == 'Коктейль на выбор':
        await callback.message.answer(
            text=t("cocktail-winning-message"),
            reply_markup=back_to_main_menu_keyboard()
        )
        return
    elif bonus == 'Кальян на выбор':
        await callback.message.answer(
            text=t("hookah-winning-message"),
            reply_markup=back_to_main_menu_keyboard()
        )
        return
    elif bonus == 'Бонус в рублях (1000)':
        await callback.message.answer(
            text=t("bonus-winning-message"),
            reply_markup=back_to_main_menu_keyboard()
        )
        # Добавляем бонус клиенту, если выпал денежный бонус
        update_customer_bonus(
            layer_name_quickresto=layer_name_quickresto,  # Название слоя QuickResto
            customer_id=id_quickresto,  # ID клиента в QuickResto
            amount=1000.00,  # Сумма бонуса в рублях
            customer_phone=phone_telegram,  # Телефон клиента в QuickResto
            auth=auth,
            headers=headers
        )

        # Обновляем дату начисления бонусов (для отслеживания сгорания)
        update_bonus_accrual_date(id_telegram)

        return
    elif bonus == 'Попробуйте завтра':
        await callback.message.answer(
            text=t("try-tomorrow-winning-message"),
            reply_markup=back_to_main_menu_keyboard()
        )
        return


"""Акции и мероприятия"""


@router.callback_query(F.data == "promotions")
async def promotions_handler(callback: CallbackQuery) -> None:
    """Обработчик кнопки 'Акции'"""
    logger.info(f"Пользователь {callback.from_user.id} нажал 'Акции'")
    await callback.message.answer(
        text=t("menu-promotions"),
        reply_markup=back_to_main_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "events")
async def events_handler(callback: CallbackQuery) -> None:
    """Обработчик кнопки 'Мероприятия'"""
    logger.info(f"Пользователь {callback.from_user.id} нажал 'Мероприятия'")
    await callback.message.answer(
        text=t("menu-events"),
        reply_markup=back_to_main_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "back_today")
async def back_today_handler(callback: CallbackQuery) -> None:
    """Обработчик кнопки 'Вернуться сегодня'"""
    logger.info(f"Пользователь {callback.from_user.id} нажал 'Вернуться сегодня'")
    await callback.message.answer(
        text=t("menu-back-today"),
        reply_markup=back_to_main_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "contacts")
async def contacts_handler(callback: CallbackQuery) -> None:
    """Обработчик кнопки '📍 Контакты'"""
    logger.info(f"Пользователь {callback.from_user.id} нажал '📍 Контакты'")
    await callback.message.answer(
        text=t("menu-contacts"),
        reply_markup=back_to_main_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "about_institution")
async def about_institution_handler(callback: CallbackQuery) -> None:
    """Обработчик кнопки 'ℹ️ О заведении'"""
    logger.info(f"Пользователь {callback.from_user.id} нажал 'ℹ️ О заведении'")
    await callback.message.answer(
        text=t("menu-about-institution"),
        reply_markup=back_to_main_menu_keyboard()
    )
    await callback.answer()
