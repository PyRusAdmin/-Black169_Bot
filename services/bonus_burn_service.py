# -*- coding: utf-8 -*-
from loguru import logger

from config import bot
from services.database import get_bonus_burning_users


async def send_bonus_burn_warning(days_until_burn: int = 7) -> dict:
    """
    Отправка уведомлений о сгорании бонусов

    :param days_until_burn: через сколько дней сгорят бонусы (7, 3, 1)
    :return: Статистика отправок
    """
    logger.info(f"Запуск проверки бонусов, сгорающих через {days_until_burn} дн....")

    burning_users = get_bonus_burning_users(days_until_burn)

    if not burning_users:
        logger.info(f"Нет пользователей с бонусами, сгорающими через {days_until_burn} дн.")
        return {"total": 0, "success": 0, "failed": 0}

    logger.info(f"Найдено пользователей с горящими бонусами: {len(burning_users)}")

    total = len(burning_users)
    success = 0
    failed = 0

    # Тексты уведомлений для разных периодов
    if days_until_burn == 7:
        warning_text = "через 7 дней"
        emoji = "⚠️"
    elif days_until_burn == 3:
        warning_text = "через 3 дня"
        emoji = "🔥"
    elif days_until_burn == 1:
        warning_text = "завтра"
        emoji = "❗"
    else:
        warning_text = f"через {days_until_burn} дн."
        emoji = "⏰"

    for user in burning_users:
        try:
            id_telegram = user.get("id_telegram")
            first_name = user.get("first_name", "Пользователь")
            bot_bonus_amount = user.get("bot_bonus_amount", "0")  # Бонусы, начисленные ботом
            burn_date = user.get("burn_date")

            # Форматируем дату сгорания
            if burn_date:
                burn_date_str = burn_date.strftime("%d.%m.%Y")
            else:
                burn_date_str = "скоро"

            # Отправляем уведомление пользователю
            try:
                await bot.send_message(
                    chat_id=id_telegram,
                    text=(
                        f"{emoji} <b>Ваши бонусы скоро сгорят!</b>\n\n"
                        f"Уважаемый(ая) {first_name}, напоминаем, что {warning_text} "
                        f"сгорят бонусы, начисленные нашим ботом.\n\n"
                        f"💰 Сумма бонусов: <b>{bot_bonus_amount} бонусов</b>\n"
                        f"📅 Дата сгорания: <b>{burn_date_str}</b>\n\n"
                        f"Успейте использовать бонусы до этой даты!\n\n"
                        f"Ждём Вас в The Black 169! 🖤"
                    ),
                )
                logger.success(
                    f"Уведомление отправлено пользователю {id_telegram} (сгорание через {days_until_burn} дн.)"
                )
                success += 1
            except Exception as e:
                if "bot was blocked" in str(e).lower():
                    logger.warning(f"Пользователь {id_telegram} заблокировал бота")
                else:
                    logger.error(f"Не удалось отправить уведомление {id_telegram}: {e}")
                failed += 1

        except Exception as e:
            logger.exception(f"Ошибка обработки пользователя {user.get('id_telegram')}: {e}")
            failed += 1

    logger.info(
        f"Проверка горящих бонусов ({days_until_burn} дн.) завершена. "
        f"Всего: {total}, Успешно: {success}, Ошибок: {failed}"
    )

    return {"total": total, "success": success, "failed": failed}


async def check_all_burningBonuses() -> dict:
    """
    Проверка всех уровней сгорания бонусов (7, 3, 1 день)

    :return: Общая статистика
    """
    logger.info("Запуск полной проверки сгорания бонусов...")

    total_stats = {
        "7_days": {"total": 0, "success": 0, "failed": 0},
        "3_days": {"total": 0, "success": 0, "failed": 0},
        "1_day": {"total": 0, "success": 0, "failed": 0},
    }

    # Проверяем каждый уровень
    total_stats["7_days"] = await send_bonus_burn_warning(7)
    total_stats["3_days"] = await send_bonus_burn_warning(3)
    total_stats["1_day"] = await send_bonus_burn_warning(1)

    # Общая статистика
    overall = {
        "total": sum(s["total"] for s in total_stats.values()),
        "success": sum(s["success"] for s in total_stats.values()),
        "failed": sum(s["failed"] for s in total_stats.values()),
    }

    logger.info(
        f"Полная проверка сгорания бонусов завершена. "
        f"Всего уведомлений: {overall['total']}, Успешно: {overall['success']}, Ошибок: {overall['failed']}"
    )

    return overall
