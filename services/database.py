# -*- coding: utf-8 -*-
from datetime import datetime
from peewee import *  # https://docs.peewee-orm.com/en/latest/index.html
from peewee import fn
from utils.logger import logger

db = SqliteDatabase("database.db")
"""
Запись в базу данных о пользователях, которые зарегистрировались в боте, передав свой номер телефона. Часть данных 
о пользователях будет браться из QuickResto https://quickresto.ru/api/ и записываться в базу данных database.db
"""


class RegisteredPersons(Model):
    """База данных для хранения данных о пользователях Telegram и QuickResto"""

    id_telegram = IntegerField(unique=True)  # ✅ id пользователя в Telegram
    id_quickresto = IntegerField(null=True)  # ✅ id пользователя в QuickResto
    phone_telegram = CharField(null=True)  # ✅ Номер телефона пользователя в Telegram
    last_name = CharField(null=True)  # ✅ Фамилия пользователя QuickResto
    first_name = CharField(null=True)  # ✅ Имя пользователя QuickResto
    patronymic_name = CharField(null=True)  # ✅ Отчество пользователя QuickResto
    birthday_user = CharField(null=True)  # ✅ День рождения пользователя QuickResto
    user_bonus = CharField(null=True)  # ✅ Бонус пользователя QuickResto
    date_of_visit = DateTimeField(default=datetime.now)  # Дата и время последнего посещения QuickResto
    updated_at = DateTimeField(default=datetime.now)  # Дата обновления данных
    bonus_accrued_at = DateTimeField(null=True)  # ✅ Дата начисления бонусов ботом (для отслеживания сгорания)
    bot_bonus_amount = DecimalField(null=True, max_digits=10, decimal_places=2)  # ✅ Сумма бонусов, начисленных ботом

    class Meta:
        database = db  # база данных
        table_name = "registered_persons"  # название таблицы


def delete_registered_person(id_telegram: int) -> bool:
    """
    Удаление пользователя из базы данных registered_persons

    :param id_telegram: ID пользователя в Telegram
    :return: True если удалён, False если не найден
    """
    try:
        if db.is_closed():
            db.connect()

        query = RegisteredPersons.delete().where(RegisteredPersons.id_telegram == id_telegram)
        result = query.execute()

        if result > 0:
            logger.info(f"Пользователь {id_telegram} удалён из registered_persons")
            return True
        else:
            logger.warning(f"Пользователь {id_telegram} не найден в registered_persons")
            return False
    except Exception as e:
        logger.exception(f"Ошибка при удалении пользователя {id_telegram}: {e}")
        return False
    finally:
        if not db.is_closed():
            db.close()


def delete_start_person(id_telegram: int) -> bool:
    """
    Удаление пользователя из базы данных start_persons

    :param id_telegram: ID пользователя в Telegram
    :return: True если удалён, False если не найден
    """
    try:
        if db.is_closed():
            db.connect()

        query = StartPersons.delete().where(StartPersons.id_telegram == id_telegram)
        result = query.execute()

        if result > 0:
            logger.info(f"Пользователь {id_telegram} удалён из start_persons")
            return True
        else:
            logger.warning(f"Пользователь {id_telegram} не найден в start_persons")
            return False
    except Exception as e:
        logger.exception(f"Ошибка при удалении пользователя {id_telegram}: {e}")
        return False
    finally:
        if not db.is_closed():
            db.close()


def write_to_db_registered_person(data):
    """Запись данных о пользователе Telegram в базу данных, а так же из QuickResto"""
    id_telegram = data.get("id_telegram")  # идентификатор пользователя в Telegram
    id_quickresto = data.get("id_quickresto")  # идентификатор пользователя в QuickResto
    last_name = data.get("last_name")  # фамилия пользователя QuickResto
    first_name = data.get("first_name")  # имя пользователя QuickResto
    patronymic_name = data.get("patronymic_name")  # отчество пользователя QuickResto
    user_bonus = data.get("user_bonus")  # бонус пользователя QuickResto
    birthday_user = data.get("birthday_user")  # день рождения пользователя QuickResto
    phone_telegram = data.get("phone_telegram")  # номер телефона пользователя в Telegram
    try:
        if db.is_closed():
            db.connect()
        person, created = RegisteredPersons.get_or_create(id_telegram=id_telegram, defaults={
            "id_quickresto": id_quickresto,  # идентификатор пользователя в QuickResto
            "last_name": last_name,  # фамилия пользователя QuickResto
            "first_name": first_name,  # имя пользователя QuickResto
            "patronymic_name": patronymic_name,  # отчество пользователя QuickResto
            "user_bonus": user_bonus,  # бонус пользователя QuickResto
            "birthday_user": birthday_user,  # день рождения пользователя QuickResto
            "phone_telegram": phone_telegram,  # номер телефона пользователя в Telegram
        })
        if not created:
            person.id_quickresto = id_quickresto  # идентификатор пользователя в QuickResto
            person.last_name = last_name  # фамилия пользователя QuickResto
            person.first_name = first_name  # имя пользователя QuickResto
            person.patronymic_name = patronymic_name  # отчество пользователя QuickResto
            person.user_bonus = user_bonus  # бонус пользователя QuickResto
            person.birthday_user = birthday_user  # день рождения пользователя QuickResto
            person.phone_telegram = phone_telegram  # номер телефона пользователя в Telegram
            person.updated_at = datetime.now()  # дата и время обновления данных о пользователе
        person.save()
    except Exception as e:
        logger.exception(e)
    finally:
        if not db.is_closed():
            db.close()


"""Запись в базу данных пользователей, которые запустили Telegram бота"""


class StartPersons(Model):
    """База данных для хранения данных о пользователях Telegram"""

    id_telegram = IntegerField(unique=True)  # id пользователя в Telegram
    last_name_telegram = CharField(null=True)  # фамилия пользователя в Telegram
    first_name_telegram = CharField(null=True)  # имя пользователя в Telegram
    username_telegram = CharField(null=True)  # username пользователя в Telegram
    updated_at = DateTimeField(default=datetime.now)  # дата и время обновления

    class Meta:
        database = db  # база данных
        table_name = "start_persons"  # название таблицы


def write_to_db_start_person(data):
    """
    Запись данных о пользователе в базу данных, которые запустили Telegram бота через команду /start или вернулись в
    начальное меню
    """
    id_telegram = data.get("id_telegram")
    last_name_telegram = data.get("last_name_telegram")
    first_name_telegram = data.get("first_name_telegram")
    username_telegram = data.get("username_telegram")

    try:
        if db.is_closed():
            db.connect()
        person, created = StartPersons.get_or_create(id_telegram=id_telegram, defaults={
            "last_name_telegram": last_name_telegram,
            "first_name_telegram": first_name_telegram,
            "username_telegram": username_telegram,
        })
        if not created:
            person.last_name_telegram = last_name_telegram
            person.first_name_telegram = first_name_telegram
            person.username_telegram = username_telegram
            person.updated_at = datetime.now()
        person.save()
    except Exception as e:
        logger.exception(e)
    finally:
        if not db.is_closed():
            db.close()


def is_user_registered(id_telegram: int) -> bool:
    """
    Проверка, зарегистрирован ли пользователь (есть ли в таблице registered_persons)

    :param id_telegram: ID пользователя в Telegram
    :return: True если зарегистрирован, False если нет
    """
    try:
        if db.is_closed():
            db.connect()
        exists = RegisteredPersons.get_or_none(RegisteredPersons.id_telegram == id_telegram)
        return exists is not None
    except Exception as e:
        logger.exception(f"Ошибка при проверке регистрации пользователя {id_telegram}: {e}")
        return False
    finally:
        if not db.is_closed():
            db.close()


def get_user_info(id_telegram: int) -> dict | None:
    """
    Получение полной информации о пользователе из таблицы registered_persons

    :param id_telegram: ID пользователя в Telegram
    :return: Словарь с данными пользователя или None если пользователь не найден
    """
    try:
        if db.is_closed():
            db.connect()
        user = RegisteredPersons.get_or_none(RegisteredPersons.id_telegram == id_telegram)
        if user:
            return {
                "id_telegram": user.id_telegram,
                "id_quickresto": user.id_quickresto,
                "phone_telegram": user.phone_telegram,
                "last_name": user.last_name,
                "first_name": user.first_name,
                "patronymic_name": user.patronymic_name,
                "birthday_user": user.birthday_user,
                "user_bonus": user.user_bonus,
                "date_of_visit": user.date_of_visit,
                "updated_at": user.updated_at
            }
        return None
    except Exception as e:
        logger.exception(f"Ошибка при получении данных пользователя {id_telegram}: {e}")
        return None
    finally:
        if not db.is_closed():
            db.close()


def get_user_bonus(id_telegram: int):
    """
    Получение баланса бонусов пользователя

    :param id_telegram: ID пользователя в Telegram
    :return: Баланс бонусов или None если пользователь не найден
    """
    try:
        if db.is_closed():
            db.connect()
        user = RegisteredPersons.get_or_none(RegisteredPersons.id_telegram == id_telegram)
        if user:
            return user.id_quickresto, user.phone_telegram
        return None
    except Exception as e:
        logger.exception(f"Ошибка при получении бонусов пользователя {id_telegram}: {e}")
        return None
    finally:
        if not db.is_closed():
            db.close()


def get_user_by_phone(phone_telegram: str) -> dict | None:
    """
    Получение информации о пользователе по номеру телефона

    :param phone_telegram: Номер телефона пользователя
    :return: Словарь с данными пользователя или None если пользователь не найден
    """
    try:
        if db.is_closed():
            db.connect()
        user = RegisteredPersons.get_or_none(RegisteredPersons.phone_telegram == phone_telegram)
        if user:
            return {
                "id_telegram": user.id_telegram,
                "id_quickresto": user.id_quickresto,
                "phone_telegram": user.phone_telegram,
                "last_name": user.last_name,
                "first_name": user.first_name,
                "patronymic_name": user.patronymic_name,
                "birthday_user": user.birthday_user,
                "user_bonus": user.user_bonus,
                "date_of_visit": user.date_of_visit,
                "updated_at": user.updated_at
            }
        return None
    except Exception as e:
        logger.exception(f"Ошибка при получении данных пользователя по телефону {phone_telegram}: {e}")
        return None
    finally:
        if not db.is_closed():
            db.close()


"""
Таблица для учёта розыгрышей в 'Колесе подарков'
Фиксирует попытки участия, выигрыши и статус (победитель/не победитель)
"""


class GiftWheelSpins(Model):
    """База данных для хранения истории розыгрышей 'Колесо подарков'"""

    id_telegram = IntegerField()  # ID пользователя в Telegram
    id_quickresto = IntegerField(null=True)  # ID пользователя в QuickResto
    bonus_name = CharField()  # Название выигранного бонуса
    is_winner = BooleanField(default=False)  # True если выиграл, False если 'Попробуйте завтра'
    spun_at = DateTimeField(default=datetime.now)  # Дата и время розыгрыша

    class Meta:
        database = db
        table_name = "gift_wheel_spins"
        indexes = (
            (('id_telegram', 'spun_at'), False),  # Индекс для быстрого поиска по дате
        )


def write_spin_result(data):
    """
    Запись результата розыгрыша 'Колесо подарков' в базу данных

    :param data: Словарь с данными: id_telegram, id_quickresto, bonus_name, is_winner
    """
    id_telegram = data.get("id_telegram")
    id_quickresto = data.get("id_quickresto")
    bonus_name = data.get("bonus_name")
    is_winner = data.get("is_winner", False)

    try:
        if db.is_closed():
            db.connect()
        spin = GiftWheelSpins.create(
            id_telegram=id_telegram,
            id_quickresto=id_quickresto,
            bonus_name=bonus_name,
            is_winner=is_winner,
            spun_at=datetime.now()
        )
        logger.info(
            f"Записан результат розыгрыша: пользователь {id_telegram}, бонус '{bonus_name}', победитель: {is_winner}")
        return spin
    except Exception as e:
        logger.exception(f"Ошибка при записи результата розыгрыша: {e}")
        return None
    finally:
        if not db.is_closed():
            db.close()


def has_user_spun_today(id_telegram: int) -> bool:
    """
    Проверка, участвовал ли пользователь в 'Колесе подарков' сегодня

    :param id_telegram: ID пользователя в Telegram
    :return: True если участвовал сегодня, False если нет
    """
    try:
        if db.is_closed():
            db.connect()

        # Получаем начало текущего дня (00:00:00)
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Ищем записи за сегодня
        spin = GiftWheelSpins.get_or_none(
            (GiftWheelSpins.id_telegram == id_telegram) &
            (GiftWheelSpins.spun_at >= today_start)
        )
        return spin is not None
    except Exception as e:
        logger.exception(f"Ошибка при проверке участия пользователя {id_telegram} в розыгрыше: {e}")
        return False
    finally:
        if not db.is_closed():
            db.close()


def get_user_spin_history(id_telegram: int, limit: int = 10) -> list:
    """
    Получение истории розыгрышей пользователя

    :param id_telegram: ID пользователя в Telegram
    :param limit: Количество последних записей
    :return: Список словарей с историей розыгрышей
    """
    try:
        if db.is_closed():
            db.connect()

        spins = (GiftWheelSpins
                 .select()
                 .where(GiftWheelSpins.id_telegram == id_telegram)
                 .order_by(GiftWheelSpins.spun_at.desc())
                 .limit(limit))

        history = []
        for spin in spins:
            history.append({
                "id_telegram": spin.id_telegram,
                "bonus_name": spin.bonus_name,
                "is_winner": spin.is_winner,
                "spun_at": spin.spun_at
            })
        return history
    except Exception as e:
        logger.exception(f"Ошибка при получении истории розыгрышей пользователя {id_telegram}: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()


def get_all_winners() -> list:
    """
    Получение всех победителей розыгрышей (для админ-панели)

    :return: Список словарей с данными победителей
    """
    try:
        if db.is_closed():
            db.connect()

        winners = (GiftWheelSpins
                   .select()
                   .where(GiftWheelSpins.is_winner == True)
                   .order_by(GiftWheelSpins.spun_at.desc()))

        result = []
        for winner in winners:
            result.append({
                "id_telegram": winner.id_telegram,
                "id_quickresto": winner.id_quickresto,
                "bonus_name": winner.bonus_name,
                "spun_at": winner.spun_at
            })
        return result
    except Exception as e:
        logger.exception(f"Ошибка при получении списка победителей: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()


"""Получение пользователей которые запустили бота командой /start"""


def get_start_persons() -> list:
    """
    Получение пользователей которые запустили бота командой /start

    :return: Список словарей с данными пользователей
    """
    try:
        if db.is_closed():
            db.connect()

        start_persons = (
            StartPersons.select().order_by(
                StartPersons.updated_at.desc()
            )
        )

        result = []  # список словарей с данными пользователей
        for start_person in start_persons:
            result.append({
                "id_telegram": start_person.id_telegram,  # id пользователя в Telegram
                "first_name": start_person.first_name_telegram,  # имя пользователя в Telegram
                "last_name": start_person.last_name_telegram,  # фамилия пользователя в Telegram
                "username": start_person.username_telegram,  # username пользователя в Telegram
                "updated_at": start_person.updated_at  # дата и время обновления
            })
        return result
    except Exception as e:
        logger.exception(f"Ошибка при получении списка пользователей: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()


def get_registered_persons() -> list:
    """
    Получение зарегистрированных пользователей (кто отправил номер телефона)

    :return: Список словарей с данными зарегистрированных пользователей
    """
    try:
        if db.is_closed():
            db.connect()

        registered_persons = (
            RegisteredPersons.select().order_by(
                RegisteredPersons.updated_at.desc()
            )
        )

        result = []  # список словарей с данными пользователей
        for person in registered_persons:
            result.append({
                "id_telegram": person.id_telegram,  # ID пользователя в Telegram
                "id_quickresto": person.id_quickresto,  # ID пользователя в QuickResto
                "phone_telegram": person.phone_telegram,  # Номер телефона
                "last_name": person.last_name,  # Фамилия (QuickResto)
                "first_name": person.first_name,  # Имя (QuickResto)
                "patronymic_name": person.patronymic_name,  # Отчество (QuickResto)
                "birthday_user": person.birthday_user,  # Дата рождения
                "user_bonus": person.user_bonus,  # Бонусы
                "date_of_visit": person.date_of_visit,  # Дата последнего визита
                "updated_at": person.updated_at  # Дата обновления
            })
        return result
    except Exception as e:
        logger.exception(f"Ошибка при получении списка зарегистрированных пользователей: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()


"""Всегда в конце, что бы создавать таблицы в базе данных"""


def create_tables():
    """Создание таблицы в базе данных"""
    db.create_tables([RegisteredPersons, StartPersons, GiftWheelSpins, MarketingMessages, PromoCodes])


"""Таблица для учёта маркетинговых рассылок"""


class MarketingMessages(Model):
    """Таблица для отслеживания эффективности рассылок"""

    id_telegram = IntegerField()  # ID пользователя в Telegram
    message_text = TextField()  # Текст сообщения
    message_type = CharField()  # Тип: text, photo, video
    sent_at = DateTimeField(default=datetime.now)  # Дата отправки
    is_blocked = BooleanField(default=False)  # True если пользователь заблокировал бота
    is_read = BooleanField(default=False)  # True если пользователь прочитал сообщение

    class Meta:
        database = db
        table_name = "marketing_messages"
        indexes = (
            (('id_telegram', 'sent_at'), False),  # Индекс для быстрого поиска
        )


def log_marketing_message(id_telegram: int, message_text: str, message_type: str = "text") -> None:
    """
    Логирование отправки маркетингового сообщения

    :param id_telegram: ID пользователя в Telegram
    :param message_text: Текст сообщения
    :param message_type: Тип сообщения (text, photo, video)
    """
    try:
        if db.is_closed():
            db.connect()
        MarketingMessages.create(
            id_telegram=id_telegram,
            message_text=message_text[:500],  # Ограничиваем длину текста
            message_type=message_type,
            sent_at=datetime.now()
        )
    except Exception as e:
        logger.exception(f"Ошибка при логировании рассылки: {e}")
    finally:
        if not db.is_closed():
            db.close()


def update_message_status(id_telegram: int, is_blocked: bool = False, is_read: bool = False) -> None:
    """
    Обновление статуса сообщения (заблокировано/прочитано)

    :param id_telegram: ID пользователя в Telegram
    :param is_blocked: True если пользователь заблокировал бота
    :param is_read: True если пользователь прочитал сообщение
    """
    try:
        if db.is_closed():
            db.connect()
        # Обновляем последнее сообщение для этого пользователя
        query = (MarketingMessages
                 .update(is_blocked=is_blocked, is_read=is_read)
                 .where(MarketingMessages.id_telegram == id_telegram)
                 .order_by(MarketingMessages.sent_at.desc())
                 .limit(1))
        query.execute()
    except Exception as e:
        logger.exception(f"Ошибка при обновлении статуса сообщения: {e}")
    finally:
        if not db.is_closed():
            db.close()


def get_all_user_ids() -> list:
    """
    Получение всех ID пользователей, которые запускали бота

    :return: Список ID пользователей
    """
    try:
        if db.is_closed():
            db.connect()

        user_ids = (StartPersons
                    .select(StartPersons.id_telegram)
                    .order_by(StartPersons.updated_at.desc()))

        return [user.id_telegram for user in user_ids]
    except Exception as e:
        logger.exception(f"Ошибка при получении списка пользователей: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()


def get_start_persons_count() -> int:
    """
    Получение количества пользователей, которые запускали бота

    :return: Количество пользователей
    """
    try:
        if db.is_closed():
            db.connect()

        count = StartPersons.select().count()
        return count
    except Exception as e:
        logger.exception(f"Ошибка при получении количества пользователей: {e}")
        return 0
    finally:
        if not db.is_closed():
            db.close()


def get_registered_persons_count() -> int:
    """
    Получение количества пользователей, которые привязали номер телефона

    :return: Количество пользователей
    """
    try:
        if db.is_closed():
            db.connect()

        count = RegisteredPersons.select().count()
        return count
    except Exception as e:
        logger.exception(f"Ошибка при получении количества зарегистрированных пользователей: {e}")
        return 0
    finally:
        if not db.is_closed():
            db.close()


def get_broadcast_stats() -> dict:
    """
    Получение статистики по рассылкам

    :return: Словарь со статистикой
    """
    try:
        if db.is_closed():
            db.connect()

        # Общее количество сообщений
        total_messages = MarketingMessages.select().count()

        # Количество по типам
        text_count = MarketingMessages.select().where(MarketingMessages.message_type == "text").count()
        photo_count = MarketingMessages.select().where(MarketingMessages.message_type == "photo").count()
        video_count = MarketingMessages.select().where(MarketingMessages.message_type == "video").count()
        blocked_count = MarketingMessages.select().where(MarketingMessages.is_blocked == True).count()

        # Уникальные пользователи, получившие рассылки
        unique_users = MarketingMessages.select(fn.COUNT(fn.DISTINCT(MarketingMessages.id_telegram))).scalar()

        return {
            "total_messages": total_messages,
            "text_count": text_count,
            "photo_count": photo_count,
            "video_count": video_count,
            "blocked_count": blocked_count,
            "unique_users": unique_users
        }
    except Exception as e:
        logger.exception(f"Ошибка при получении статистики рассылок: {e}")
        return {
            "total_messages": 0,
            "text_count": 0,
            "photo_count": 0,
            "video_count": 0,
            "blocked_count": 0,
            "unique_users": 0
        }
    finally:
        if not db.is_closed():
            db.close()


def get_birthday_users_today() -> list:
    """
    Получение пользователей, у которых сегодня день рождения

    :return: Список словарей с данными именинников
    """
    try:
        if db.is_closed():
            db.connect()

        today = datetime.now().strftime("%d.%m")  # Сегодняшняя дата в формате DD.MM

        # Получаем всех зарегистрированных пользователей
        registered_persons = RegisteredPersons.select()

        result = []  # список словарей с данными именинников
        for person in registered_persons:
            if person.birthday_user:
                # Формат даты в QuickResto: YYYY-MM-DD или DD.MM.YYYY
                birthday = person.birthday_user
                if len(birthday) == 10:
                    # Преобразуем в DD.MM
                    if '-' in birthday:
                        birthday_formatted = f"{birthday[8:10]}.{birthday[5:7]}"
                    elif '.' in birthday:
                        birthday_formatted = birthday[:5]
                    else:
                        continue

                    if birthday_formatted == today:
                        result.append({
                            "id_telegram": person.id_telegram,
                            "id_quickresto": person.id_quickresto,
                            "phone_telegram": person.phone_telegram,
                            "first_name": person.first_name,
                            "last_name": person.last_name,
                            "birthday_user": person.birthday_user
                        })

        return result
    except Exception as e:
        logger.exception(f"Ошибка при получении именинников: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()


def get_birthday_users_count() -> int:
    """
    Получение количества пользователей, у которых сегодня день рождения

    :return: Количество именинников
    """
    try:
        if db.is_closed():
            db.connect()

        today = datetime.now().strftime("%d.%m")
        registered_persons = RegisteredPersons.select()

        count = 0
        for person in registered_persons:
            if person.birthday_user:
                birthday = person.birthday_user
                if len(birthday) == 10:
                    if '-' in birthday:
                        birthday_formatted = f"{birthday[8:10]}.{birthday[5:7]}"
                    elif '.' in birthday:
                        birthday_formatted = birthday[:5]
                    else:
                        continue

                    if birthday_formatted == today:
                        count += 1

        return count
    except Exception as e:
        logger.exception(f"Ошибка при подсчёте именинников: {e}")
        return 0
    finally:
        if not db.is_closed():
            db.close()


def get_bonus_burning_users(days_until_burn: int = 7) -> list:
    """
    Получение пользователей, у которых бонусы, начисленные ботом, сгорят через указанное количество дней

    :param days_until_burn: через сколько дней сгорят бонусы (7, 3, 1)
    :return: Список словарей с данными пользователей
    """
    try:
        if db.is_closed():
            db.connect()

        # Бонусы, начисленные ботом, действуют 3 месяца (90 дней)
        # Находим пользователей, у которых дата начисления + (90 - days_until_burn) дней = сегодня
        from datetime import timedelta

        # Дата начисления должна быть: сегодня - (90 - days_until_burn) дней
        target_accrual_date = (datetime.now() - timedelta(days=90 - days_until_burn)).date()

        # Получаем только тех пользователей, у которых есть дата начисления бонусов ботом
        registered_persons = RegisteredPersons.select().where(
            RegisteredPersons.bonus_accrued_at.is_null(False)
        )

        result = []
        for person in registered_persons:
            if person.bonus_accrued_at:
                accrual_date = person.bonus_accrued_at.date()
                if accrual_date == target_accrual_date:
                    # Бонусы сгорят через days_until_burn дней
                    burn_date = person.bonus_accrued_at + timedelta(days=90)
                    result.append({
                        "id_telegram": person.id_telegram,
                        "id_quickresto": person.id_quickresto,
                        "phone_telegram": person.phone_telegram,
                        "first_name": person.first_name,
                        "last_name": person.last_name,
                        "user_bonus": person.user_bonus,
                        "bot_bonus_amount": person.bot_bonus_amount,  # Сумма бонусов, начисленных ботом
                        "bonus_accrued_at": person.bonus_accrued_at,
                        "burn_date": burn_date
                    })

        return result
    except Exception as e:
        logger.exception(f"Ошибка при получении пользователей с горящими бонусами бота: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()


def update_bonus_accrual_date(id_telegram: int, accrued_at: datetime = None, bonus_amount: float = None) -> bool:
    """
    Обновление даты начисления бонусов ботом для пользователя

    :param id_telegram: ID пользователя в Telegram
    :param accrued_at: Дата начисления (по умолчанию - сейчас)
    :param bonus_amount: Сумма начисленных бонусов (для отслеживания)
    :return: True если обновлено, False если нет
    """
    try:
        if db.is_closed():
            db.connect()

        if accrued_at is None:
            accrued_at = datetime.now()

        # Если передана сумма бонуса, обновляем и её
        if bonus_amount is not None:
            query = (RegisteredPersons
                     .update(bonus_accrued_at=accrued_at, bot_bonus_amount=bonus_amount)
                     .where(RegisteredPersons.id_telegram == id_telegram))
        else:
            query = (RegisteredPersons
                     .update(bonus_accrued_at=accrued_at)
                     .where(RegisteredPersons.id_telegram == id_telegram))

        result = query.execute()

        if result > 0:
            logger.info(f"Дата начисления бонусов ботом обновлена для пользователя {id_telegram}")
            return True
        return False
    except Exception as e:
        logger.exception(f"Ошибка при обновлении даты начисления бонусов ботом: {e}")
        return False
    finally:
        if not db.is_closed():
            db.close()


"""Таблица для учёта промокодов"""


class PromoCodes(Model):
    """Таблица для хранения промокодов"""

    code = CharField(unique=True)  # Уникальный код промокода
    bonus_amount = DecimalField(max_digits=10, decimal_places=2)  # Сумма бонусов
    description = TextField(null=True)  # Описание промокода
    is_active = BooleanField(default=True)  # Активен ли промокод
    created_at = DateTimeField(default=datetime.now)  # Дата создания
    used_by = IntegerField(null=True)  # ID пользователя в Telegram, который использовал
    used_at = DateTimeField(null=True)  # Дата использования

    class Meta:
        database = db
        table_name = "promo_codes"
        indexes = (
            (('code',), True),  # Уникальный индекс на код
        )


def create_promo_code(code: str, bonus_amount: float, description: str = None) -> bool:
    """
    Создание нового промокода

    :param code: Уникальный код промокода
    :param bonus_amount: Сумма бонусов
    :param description: Описание промокода
    :return: True если создан, False если ошибка
    """
    try:
        if db.is_closed():
            db.connect()

        PromoCodes.create(
            code=code,
            bonus_amount=bonus_amount,
            description=description,
            is_active=True
        )
        logger.info(f"Создан промокод: {code} на сумму {bonus_amount}")
        return True
    except Exception as e:
        logger.exception(f"Ошибка при создании промокода {code}: {e}")
        return False
    finally:
        if not db.is_closed():
            db.close()


def get_promo_code(code: str) -> dict | None:
    """
    Получение информации о промокоде по коду

    :param code: Код промокода
    :return: Словарь с данными промокода или None если не найден
    """
    try:
        if db.is_closed():
            db.connect()

        promo = PromoCodes.get_or_none(PromoCodes.code == code)
        if promo:
            return {
                "code": promo.code,
                "bonus_amount": promo.bonus_amount,
                "description": promo.description,
                "is_active": promo.is_active,
                "created_at": promo.created_at,
                "used_by": promo.used_by,
                "used_at": promo.used_at
            }
        return None
    except Exception as e:
        logger.exception(f"Ошибка при получении промокода {code}: {e}")
        return None
    finally:
        if not db.is_closed():
            db.close()


def activate_promo_code(code: str, id_telegram: int) -> bool:
    """
    Активация промокода пользователем

    :param code: Код промокода
    :param id_telegram: ID пользователя в Telegram
    :return: True если активирован, False если ошибка или уже использован
    """
    try:
        if db.is_closed():
            db.connect()

        # Проверяем, существует ли промокод и активен ли он
        promo = PromoCodes.get_or_none(
            (PromoCodes.code == code) &
            (PromoCodes.is_active == True) &
            (PromoCodes.used_by.is_null())
        )

        if not promo:
            return False

        # Помечаем как использованный
        query = (PromoCodes
                 .update(
                     used_by=id_telegram,
                     used_at=datetime.now(),
                     is_active=False
                 )
                 .where(PromoCodes.code == code))

        result = query.execute()

        if result > 0:
            logger.info(f"Промокод {code} активирован пользователем {id_telegram}")
            return True
        return False
    except Exception as e:
        logger.exception(f"Ошибка при активации промокода {code}: {e}")
        return False
    finally:
        if not db.is_closed():
            db.close()


def get_all_promo_codes() -> list:
    """
    Получение всех промокодов

    :return: Список словарей с данными промокодов
    """
    try:
        if db.is_closed():
            db.connect()

        promo_codes = PromoCodes.select().order_by(PromoCodes.created_at.desc())

        result = []
        for promo in promo_codes:
            result.append({
                "code": promo.code,
                "bonus_amount": promo.bonus_amount,
                "description": promo.description,
                "is_active": promo.is_active,
                "created_at": promo.created_at,
                "used_by": promo.used_by,
                "used_at": promo.used_at
            })
        return result
    except Exception as e:
        logger.exception(f"Ошибка при получении списка промокодов: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()


def delete_promo_code(code: str) -> bool:
    """
    Удаление промокода

    :param code: Код промокода
    :return: True если удалён, False если не найден
    """
    try:
        if db.is_closed():
            db.connect()

        query = PromoCodes.delete().where(PromoCodes.code == code)
        result = query.execute()

        if result > 0:
            logger.info(f"Промокод {code} удалён")
            return True
        logger.warning(f"Промокод {code} не найден")
        return False
    except Exception as e:
        logger.exception(f"Ошибка при удалении промокода {code}: {e}")
        return False
    finally:
        if not db.is_closed():
            db.close()


def get_active_promo_codes_count() -> int:
    """
    Получение количества активных промокодов

    :return: Количество активных промокодов
    """
    try:
        if db.is_closed():
            db.connect()

        count = PromoCodes.select().where(PromoCodes.is_active == True).count()
        return count
    except Exception as e:
        logger.exception(f"Ошибка при подсчёте активных промокодов: {e}")
        return 0
    finally:
        if not db.is_closed():
            db.close()


def get_used_promo_codes_count() -> int:
    """
    Получение количества использованных промокодов

    :return: Количество использованных промокодов
    """
    try:
        if db.is_closed():
            db.connect()

        count = PromoCodes.select().where(PromoCodes.used_by.is_null(False)).count()
        return count
    finally:
        if not db.is_closed():
            db.close()
