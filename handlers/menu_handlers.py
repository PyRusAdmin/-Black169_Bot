# -*- coding: utf-8 -*-
from aiogram import F, Router
from aiogram.types import CallbackQuery
from loguru import logger

from keyboards.inline import back_to_main_menu_keyboard, twist_keyboard
from services.database import get_user_bonus
from services.i18n import t

router = Router(name=__name__)


@router.callback_query(F.data == "my_bonuses")
async def my_bonuses_handler(callback: CallbackQuery) -> None:
    """Обработчик кнопки 'Мои бонусы'"""
    logger.info(f"Пользователь {callback.from_user.id} нажал 'Мои бонусы'")

    # Получаем баланс бонусов пользователя
    bonus = get_user_bonus(callback.from_user.id)

    if bonus:
        await callback.message.answer(
            text=f"💰 Ваши бонусы: <b>{bonus}</b>\n\nИспользуйте их при следующем посещении!",
            reply_markup=back_to_main_menu_keyboard()
        )
    else:
        await callback.message.answer(
            text="❌ Информация о бонусах не найдена. Пожалуйста, зарегистрируйтесь.",
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
    """Обработчик кнопки 'Крутить'"""
    logger.info(f"Пользователь {callback.from_user.id} нажал 'Крутить'")
    await callback.message.answer(
        text=t("winning-message"),
        reply_markup=back_to_main_menu_keyboard()
    )
    await callback.answer()


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
    """Обработчик кнопки 'Контакты'"""
    logger.info(f"Пользователь {callback.from_user.id} нажал 'Контакты'")
    await callback.message.answer(
        text=t("menu-contacts"),
        reply_markup=back_to_main_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "about_institution")
async def about_institution_handler(callback: CallbackQuery) -> None:
    """Обработчик кнопки 'О заведении'"""
    logger.info(f"Пользователь {callback.from_user.id} нажал 'О заведении'")
    await callback.message.answer(
        text=t("menu-about-institution"),
        reply_markup=back_to_main_menu_keyboard()
    )
    await callback.answer()
