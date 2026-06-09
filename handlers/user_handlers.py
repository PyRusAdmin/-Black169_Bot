from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from handlers.menu_handlers import updates_bonuses_in_the_database
from keyboards.keyboards import main_menu_keyboard
from services.database import write_to_db_registered_person
from services.i18n import t
from services.quickresto_api import (
    create_client,
    print_client_info,
    print_full_client_info,
    update_customer_bonus,
)
from states.user_states import ConsentState
from utils.logger import logger
from utils.phone_utils import normalize_phone_number, is_valid_phone

router = Router(name=__name__)


@router.message(ConsentState.waiting_to_phone_user)
async def message_handler(message: Message, state: FSMContext) -> None:
    """
    Принимает контакт пользователя (отправленный номер телефона) и проверяет его в базе QuickResto
    """
    try:
        if message.contact:
            raw_phone = message.contact.phone_number
        elif message.text:
            raw_phone = message.text.strip()
        else:
            await message.answer(
                "Пожалуйста, введите ваш номер телефона в формате 79999999999."
            )
            return

        phone_telegram = normalize_phone_number(raw_phone)

        if not is_valid_phone(phone_telegram):
            await message.answer(
                "Некорректный формат номера телефона. Пожалуйста, введите номер в формате 79999999999."
            )
            return
        logger.info(f"Пользователь отправил контакт: {phone_telegram}")
        logger.info(f"Проверяем контакт: {phone_telegram} в базе QuickResto")

        # Проверяем контакт в базе QuickResto
        data_customer = print_client_info(phone_number=phone_telegram)

        # Если клиент не найден — создаём нового и присваиваем ему 1000 бонусных балов
        if data_customer is None:
            logger.info(f"Клиент не найден, создаём нового: {phone_telegram}")

            created_client = create_client(
                name_customer=message.from_user.first_name,  # имя клиента
                phone_customer=phone_telegram,  # номер телефона клиента
            )

            if created_client:
                logger.success(
                    f"Клиент создан в QuickResto: id={created_client.get('id')}"
                )

                data = {
                    "id_telegram": message.from_user.id,
                    "id_quickresto": created_client.get("id"),
                    "last_name": message.from_user.last_name,
                    "first_name": message.from_user.first_name,
                    "phone_telegram": phone_telegram,
                }

                write_to_db_registered_person(data)

                # Добавляем бонус клиенту, если пользователя нет в базе QuickResto
                update_customer_bonus(
                    customer_id=created_client.get("id"),  # ID клиента в QuickResto
                    amount=1000.00,  # Сумма бонуса в рублях
                    customer_phone=phone_telegram,  # Телефон клиента в QuickResto
                )

                # Обновляем базу данных с бонусами
                updates_bonuses_in_the_database(id_telegram=message.from_user.id)

                # Объединяем сообщение о регистрации с главным меню
                await message.answer(
                    text=t("registration-completed") + "\n\n" + t("main-menu"),
                    reply_markup=main_menu_keyboard(),
                )
                await state.clear()
            else:
                logger.error("Не удалось создать клиента в QuickResto")
                await message.answer(text=t("user-not-found"))
            return

        # Клиент найден в базе QuickResto
        phone_quickresto = data_customer.get("phone")
        if phone_telegram == phone_quickresto:
            logger.success(f"Пользователь найден в базе QuickResto: {phone_telegram}")

            """
            Если пользователь найден в базе QuickResto, то записываем его в базу данных. Так как QuickResto не
            выдает полную информацию о пользователе по номеру телефона, то запрашиваем его данные из базы
            QuickResto по его ID
            """
            id_quickresto = data_customer.get("client_id")

            full_data = print_full_client_info(client_id=id_quickresto)

            data = {
                "id_telegram": message.from_user.id,
                "id_quickresto": full_data.get("id"),
                "last_name": full_data.get("last_name"),
                "first_name": full_data.get("first_name"),
                "patronymic_name": full_data.get("middle_name"),
                "birthday_user": full_data.get("date_of_birth"),
                "user_bonus": full_data.get("bonus_ledger"),
                "phone_telegram": phone_telegram,
            }

            write_to_db_registered_person(data)

            # Объединяем сообщение о регистрации с главным меню
            await message.answer(
                text=t("registration-completed") + "\n\n" + t("main-menu"),
                reply_markup=main_menu_keyboard(),
            )
            await state.clear()
        else:
            logger.warning(
                f"Пользователь не найден в базе QuickResto: {phone_telegram}"
            )
            await message.answer(text=t("user-not-found"))

    except Exception as e:
        logger.exception(e)
