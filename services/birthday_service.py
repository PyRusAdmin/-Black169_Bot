from loguru import logger

from config import bot
from services.database import get_birthday_users_today, update_bonus_accrual_date
from services.quickresto_api import update_customer_bonus


async def send_birthday_bonus() -> dict:
    """
    Автоматическое начисление 1500 бонусов пользователям в день рождения

    :return: Статистика начислений
    """
    logger.info("Запуск проверки дней рождения...")

    birthday_users = get_birthday_users_today()

    if not birthday_users:
        logger.info("Сегодня именинников нет")
        return {"total": 0, "success": 0, "failed": 0}

    logger.info(f"Найдено именинников: {len(birthday_users)}")

    total = len(birthday_users)
    success = 0
    failed = 0

    for user in birthday_users:
        try:
            id_telegram = user.get("id_telegram")
            id_quickresto = user.get("id_quickresto")
            phone = user.get("phone_telegram")
            first_name = user.get("first_name", "Пользователь")
            last_name = user.get("last_name", "")

            # Начисляем бонусы через QuickResto
            result = update_customer_bonus(
                customer_id=id_quickresto,  # ID пользователя в QuickResto
                amount=1500.00,  # 1500 бонусов
                customer_phone=phone,  # Телефон пользователя
            )

            if result:
                logger.success(
                    f"Начислено 1500 бонусов имениннику {first_name} {last_name} (ID: {id_telegram})"
                )
                success += 1

                # Обновляем дату начисления бонусов (для отслеживания сгорания)
                update_bonus_accrual_date(id_telegram, bonus_amount=1500.00)

                # Отправляем поздравление пользователю
                try:
                    await bot.send_message(
                        chat_id=id_telegram,
                        text=(
                            f"🎂 <b>С Днём рождения, {first_name}!</b>\n\n"
                            f"Команда The Black 169 поздравляет Вас с праздником! 🎉\n\n"
                            f"🎁 Мы начислили Вам <b>1500 бонусов</b> на счёт.\n"
                            f"Используйте их при следующем визите!\n\n"
                            f"Ждём Вас в гости! 🖤"
                        ),
                    )
                    logger.info(f"Поздравление отправлено пользователю {id_telegram}")
                except Exception as e:
                    logger.warning(
                        f"Не удалось отправить поздравление {id_telegram}: {e}"
                    )
            else:
                logger.error(f"Ошибка начисления бонусов {id_telegram}")
                failed += 1

        except Exception as e:
            logger.exception(
                f"Ошибка обработки именинника {user.get('id_telegram')}: {e}"
            )
            failed += 1

    logger.info(
        f"Проверка дней рождения завершена. "
        f"Всего: {total}, Успешно: {success}, Ошибок: {failed}"
    )

    return {"total": total, "success": success, "failed": failed}
