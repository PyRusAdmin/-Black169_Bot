from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove

from handlers.menu_handlers import updates_bonuses_in_the_database
from keyboards.keyboards import main_menu_keyboard
from services.database import write_to_db_registered_person
from services.i18n import t
from services.quickresto_api import (
    create_client, print_client_info, print_full_client_info, update_customer_bonus,
)
from utils.logger import logger

router = Router(name=__name__)


@router.message(F.contact)
async def message_handler(message: Message) -> None:
    """
    Принимает контакт пользователя (отправленный номер телефона) и проверяет его в базе QuickResto
    """
    try:
        logger.info(f"Пользователь отправил контакт: {message.contact.phone_number}")

        phone_telegram = message.contact.phone_number.replace("+", "")
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
                logger.success(f"Клиент создан в QuickResto: id={created_client.get("id")}")

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

                # Сначала удаляем реплай-клавиатуру
                await message.answer(
                    text=t("registration-completed"),
                    reply_markup=ReplyKeyboardRemove(remove_keyboard=True),
                )
                # Затем показываем главное меню
                await message.answer(
                    text=t("main-menu"),
                    reply_markup=main_menu_keyboard(),
                )
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

            # Сначала удаляем реплай-клавиатуру
            await message.answer(
                text=t("registration-completed"),
                reply_markup=ReplyKeyboardRemove(remove_keyboard=True),
            )
            # Затем показываем главное меню
            await message.answer(
                text=t("main-menu"),
                reply_markup=main_menu_keyboard(),
            )
        else:
            logger.warning(
                f"Пользователь не найден в базе QuickResto: {phone_telegram}"
            )
            await message.answer(text=t("user-not-found"))

    except Exception as e:
        logger.exception(e)
