from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from config import OWNER_IDS
from keyboards.keyboards import consent_keyboard, main_menu_keyboard, main_menu_keyboard_admin
from keyboards.keyboards import contact_keyboard
from services.database import add_consent, has_consent, is_user_registered, write_to_db_start_person
from services.i18n import t
from utils.logger import logger

router = Router(name=__name__)

"""
Обработчик команды /start (общая команда для всех пользователей). В зависимости от того, является ли пользователь 
владельцем бота, он получает разные клавиатуры.
"""


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Этот обработчик получает сообщения с командой '/start'
    """
    logger.info(f"Получена команда /start от пользователя {message.from_user.id}")

    # Проверяем, является ли пользователь владельцем бота. ID пользователя должен быть в списке OWNER_IDS в файле .env
    if message.from_user.id in OWNER_IDS:
        logger.info(f"Пользователь {message.from_user.id} является владельцем бота")
        await message.answer(
            text=t("main-menu"),
            reply_markup=main_menu_keyboard_admin(),
        )
        return

    # Записываем данные в базу данных (пользователь который запустил бота)
    write_to_db_start_person(
        {
            "id_telegram": message.from_user.id,
            "last_name_telegram": message.from_user.last_name,
            "first_name_telegram": message.from_user.first_name,
            "username_telegram": message.from_user.username,
        }
    )

    # Проверяем, давал ли пользователь согласие на обработку персональных данных
    if has_consent(message.from_user.id):
        logger.info(
            f"Пользователь {message.from_user.id} уже дал согласие на обработку персональных данных"
        )

        # Проверяем, был ли уже зарегистрирован пользователь
        if is_user_registered(message.from_user.id):
            # Пользователь уже зарегистрирован — показываем главное меню
            logger.info(
                f"Пользователь {message.from_user.id} уже зарегистрирован, показываем главное меню"
            )
            await message.answer(
                text=t("main-menu"),
                reply_markup=main_menu_keyboard(),
            )
            return

        # Пользователь дал согласие, но ещё не зарегистрирован — просим номер телефона
        logger.info(
            f"Отправка запроса номера телефона пользователю {message.from_user.id}"
        )
        await message.answer(text=t("greet-message"), reply_markup=contact_keyboard())
        return

    # Пользователь не давал согласие — запрашиваем его
    logger.info(
        f"Запрос согласия на обработку персональных данных у пользователя {message.from_user.id}"
    )
    await message.answer(
        text=t("consent-title"),
        reply_markup=consent_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "consent_given")
async def consent_given_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки «Даю согласие на обработку персональных данных»
    """
    logger.info(
        f"Пользователь {callback.from_user.id} дал согласие на обработку персональных данных"
    )

    id_telegram = callback.from_user.id

    # Добавляем согласие в базу данных
    add_consent(id_telegram)

    await callback.message.answer(
        text=t("consent-given"), reply_markup=contact_keyboard(), parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "consent_declined")
async def consent_declined_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки «Не даю согласие»
    """
    logger.info(
        f"Пользователь {callback.from_user.id} отказался от обработки персональных данных"
    )

    await callback.message.answer(text=t("consent-declined"), parse_mode="HTML")
    await callback.answer()


"""Кнопка возврата в главное меню для обычных пользователей"""


@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu_handler(callback: CallbackQuery) -> None:
    """
    Обработчик кнопки "В главное меню"
    """
    logger.info(f"Пользователь {callback.from_user.id} нажал 'В главное меню'")

    id_telegram = callback.from_user.id
    first_name_telegram = callback.from_user.first_name
    last_name_telegram = callback.from_user.last_name
    username_telegram = callback.from_user.username

    # Проверяем, является ли пользователь владельцем бота. ID пользователя должен быть в списке OWNER_IDS в файле .env
    if id_telegram in OWNER_IDS:
        logger.info(f"Пользователь {id_telegram} является владельцем бота")
        try:
            await callback.message.edit_text(
                text=t("main-menu"),
                reply_markup=main_menu_keyboard_admin(),
            )
        except Exception:
            await callback.message.answer(
                text=t("main-menu"),
                reply_markup=main_menu_keyboard_admin(),
            )
        await callback.answer()
        return

    data = {
        "id_telegram": id_telegram,
        "last_name_telegram": last_name_telegram,
        "first_name_telegram": first_name_telegram,
        "username_telegram": username_telegram,
    }
    write_to_db_start_person(
        data
    )  # Записываем данные в базу данных (пользователь который запустил бота)

    # Проверяем, давал ли пользователь согласие на обработку персональных данных
    if has_consent(id_telegram):
        # Проверяем, был ли уже зарегистрирован пользователь
        if is_user_registered(id_telegram):
            # Пользователь уже зарегистрирован — показываем главное меню
            logger.info(
                f"Пользователь {id_telegram} уже зарегистрирован, показываем главное меню"
            )
            # Пробуем отредактировать сообщение, а если не получится (документ) — отправляем новое
            try:
                await callback.message.edit_text(
                    text=t("main-menu"),
                    reply_markup=main_menu_keyboard(),
                )
            except Exception:
                await callback.message.answer(
                    text=t("main-menu"),
                    reply_markup=main_menu_keyboard(),
                )
            await callback.answer()
            return

        # Пользователь дал согласие, но ещё не зарегистрирован — просим номер телефона
        logger.info(
            f"Отправка запроса номера телефона пользователю {callback.from_user.id}"
        )
        try:
            await callback.message.edit_text(
                text=t("greet-message"),
                reply_markup=contact_keyboard(),
            )
        except Exception:
            await callback.message.answer(
                text=t("greet-message"),
                reply_markup=contact_keyboard(),
            )
        await callback.answer()
        return

    # Пользователь не давал согласие — запрашиваем его
    logger.info(
        f"Запрос согласия на обработку персональных данных у пользователя {callback.from_user.id}"
    )
    try:
        await callback.message.edit_text(
            text=t("consent-title"),
            reply_markup=consent_keyboard(),
            parse_mode="HTML",
        )
    except Exception:
        await callback.message.answer(
            text=t("consent-title"),
            reply_markup=consent_keyboard(),
            parse_mode="HTML",
        )
    await callback.answer()
