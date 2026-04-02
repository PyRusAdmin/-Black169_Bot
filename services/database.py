import json
from datetime import datetime

# https://docs.peewee-orm.com/en/latest/index.html
from peewee import (
    BooleanField,
    CharField,
    DateTimeField,
    DecimalField,
    IntegerField,
    Model,
    SqliteDatabase,
    TextField,
    fn,
)

from utils.logger import logger

db = SqliteDatabase("data/database.db")

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
    date_of_visit = DateTimeField(
        default=datetime.now
    )  # Дата и время последнего посещения QuickResto
    updated_at = DateTimeField(default=datetime.now)  # Дата обновления данных
    bonus_accrued_at = DateTimeField(
        null=True
    )  # ✅ Дата начисления бонусов ботом (для отслеживания сгорания)
    bot_bonus_amount = DecimalField(
        null=True, max_digits=10, decimal_places=2
    )  # ✅ Сумма бонусов, начисленных ботом
    client_level = CharField(
        null=True
    )  # ✅ Уровень клиента (Bronze, Silver, Gold, Black)
    accumulation_amount = DecimalField(
        null=True, max_digits=12, decimal_places=2
    )  # ✅ Накопительная сумма для уровня
    gift_bonus_claimed = BooleanField(
        default=False
    )  # ✅ Получил ли пользователь подарочные бонусы 3000
    gift_bonus_claimed_at = DateTimeField(
        null=True
    )  # ✅ Дата получения подарочных бонусов

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

        query = RegisteredPersons.delete().where(
            RegisteredPersons.id_telegram == id_telegram
        )
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
    phone_telegram = data.get(
        "phone_telegram"
    )  # номер телефона пользователя в Telegram
    client_level = data.get("client_level")  # уровень клиента
    accumulation_amount = data.get("accumulation_amount")  # накопительная сумма

    try:
        if db.is_closed():
            db.connect()
        person, created = RegisteredPersons.get_or_create(
            id_telegram=id_telegram,
            defaults={
                "id_quickresto": id_quickresto,  # идентификатор пользователя в QuickResto
                "last_name": last_name,  # фамилия пользователя QuickResto
                "first_name": first_name,  # имя пользователя QuickResto
                "patronymic_name": patronymic_name,  # отчество пользователя QuickResto
                "user_bonus": user_bonus,  # бонус пользователя QuickResto
                "birthday_user": birthday_user,  # день рождения пользователя QuickResto
                "phone_telegram": phone_telegram,  # номер телефона пользователя в Telegram
                "client_level": client_level,  # уровень клиента
                "accumulation_amount": accumulation_amount,  # накопительная сумма
            },
        )
        if not created:
            person.id_quickresto = (
                id_quickresto  # идентификатор пользователя в QuickResto
            )
            person.last_name = last_name  # фамилия пользователя QuickResto
            person.first_name = first_name  # имя пользователя QuickResto
            person.patronymic_name = patronymic_name  # отчество пользователя QuickResto
            person.user_bonus = user_bonus  # бонус пользователя QuickResto
            person.birthday_user = (
                birthday_user  # день рождения пользователя QuickResto
            )
            person.phone_telegram = (
                phone_telegram  # номер телефона пользователя в Telegram
            )
            person.client_level = client_level  # уровень клиента
            person.accumulation_amount = accumulation_amount  # накопительная сумма
            person.updated_at = (
                datetime.now()
            )  # дата и время обновления данных о пользователе
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
        person, created = StartPersons.get_or_create(
            id_telegram=id_telegram,
            defaults={
                "last_name_telegram": last_name_telegram,
                "first_name_telegram": first_name_telegram,
                "username_telegram": username_telegram,
            },
        )
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
        exists = RegisteredPersons.get_or_none(
            RegisteredPersons.id_telegram == id_telegram
        )
        return exists is not None
    except Exception as e:
        logger.exception(
            f"Ошибка при проверке регистрации пользователя {id_telegram}: {e}"
        )
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
        user = RegisteredPersons.get_or_none(
            RegisteredPersons.id_telegram == id_telegram
        )
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
                "updated_at": user.updated_at,
                "client_level": user.client_level,
                "accumulation_amount": user.accumulation_amount,
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
        user = RegisteredPersons.get_or_none(
            RegisteredPersons.id_telegram == id_telegram
        )
        if user:
            return user.id_quickresto, user.phone_telegram
        return None
    except Exception as e:
        logger.exception(
            f"Ошибка при получении бонусов пользователя {id_telegram}: {e}"
        )
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
        user = RegisteredPersons.get_or_none(
            RegisteredPersons.phone_telegram == phone_telegram
        )
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
                "updated_at": user.updated_at,
            }
        return None
    except Exception as e:
        logger.exception(
            f"Ошибка при получении данных пользователя по телефону {phone_telegram}: {e}"
        )
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
    is_winner = BooleanField(
        default=False
    )  # True если выиграл, False если 'Попробуйте завтра'
    spun_at = DateTimeField(default=datetime.now)  # Дата и время розыгрыша

    class Meta:
        database = db
        table_name = "gift_wheel_spins"
        indexes = (
            (("id_telegram", "spun_at"), False),
        )  # Индекс для быстрого поиска по дате


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
            spun_at=datetime.now(),
        )
        logger.info(
            f"Записан результат розыгрыша: пользователь {id_telegram}, бонус '{bonus_name}', победитель: {is_winner}"
        )
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
            (GiftWheelSpins.id_telegram == id_telegram)
            & (GiftWheelSpins.spun_at >= today_start)
        )
        return spin is not None
    except Exception as e:
        logger.exception(
            f"Ошибка при проверке участия пользователя {id_telegram} в розыгрыше: {e}"
        )
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

        spins = (
            GiftWheelSpins.select()
            .where(GiftWheelSpins.id_telegram == id_telegram)
            .order_by(GiftWheelSpins.spun_at.desc())
            .limit(limit)
        )

        history = []
        for spin in spins:
            history.append(
                {
                    "id_telegram": spin.id_telegram,
                    "bonus_name": spin.bonus_name,
                    "is_winner": spin.is_winner,
                    "spun_at": spin.spun_at,
                }
            )
        return history
    except Exception as e:
        logger.exception(
            f"Ошибка при получении истории розыгрышей пользователя {id_telegram}: {e}"
        )
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

        winners = (
            GiftWheelSpins.select()
            .where(GiftWheelSpins.is_winner)
            .order_by(GiftWheelSpins.spun_at.desc())
        )

        result = []
        for winner in winners:
            result.append(
                {
                    "id_telegram": winner.id_telegram,
                    "id_quickresto": winner.id_quickresto,
                    "bonus_name": winner.bonus_name,
                    "spun_at": winner.spun_at,
                }
            )
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

        start_persons = StartPersons.select().order_by(StartPersons.updated_at.desc())

        result = []  # список словарей с данными пользователей
        for start_person in start_persons:
            result.append(
                {
                    "id_telegram": start_person.id_telegram,  # id пользователя в Telegram
                    "first_name": start_person.first_name_telegram,  # имя пользователя в Telegram
                    "last_name": start_person.last_name_telegram,  # фамилия пользователя в Telegram
                    "username": start_person.username_telegram,  # username пользователя в Telegram
                    "updated_at": start_person.updated_at,  # дата и время обновления
                }
            )
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

        registered_persons = RegisteredPersons.select().order_by(
            RegisteredPersons.updated_at.desc()
        )

        result = []  # список словарей с данными пользователей
        for person in registered_persons:
            result.append(
                {
                    "id_telegram": person.id_telegram,  # ID пользователя в Telegram
                    "id_quickresto": person.id_quickresto,  # ID пользователя в QuickResto
                    "phone_telegram": person.phone_telegram,  # Номер телефона
                    "last_name": person.last_name,  # Фамилия (QuickResto)
                    "first_name": person.first_name,  # Имя (QuickResto)
                    "patronymic_name": person.patronymic_name,  # Отчество (QuickResto)
                    "birthday_user": person.birthday_user,  # Дата рождения
                    "user_bonus": person.user_bonus,  # Бонусы
                    "date_of_visit": person.date_of_visit,  # Дата последнего визита
                    "updated_at": person.updated_at,  # Дата обновления
                    "client_level": person.client_level,  # Уровень клиента
                    "accumulation_amount": person.accumulation_amount,  # Накопительная сумма
                }
            )
        return result
    except Exception as e:
        logger.exception(
            f"Ошибка при получении списка зарегистрированных пользователей: {e}"
        )
        return []
    finally:
        if not db.is_closed():
            db.close()


def get_client_levels_stats() -> dict:
    """
    Получение статистики по уровням клиентов

    :return: Словарь со статистикой по уровням
    """
    try:
        if db.is_closed():
            db.connect()

        # Общее количество зарегистрированных клиентов
        total = RegisteredPersons.select().count()

        # Количество по уровням
        levels = {}
        for level in ["Black", "Gold", "Silver", "Bronze"]:
            count = (
                RegisteredPersons.select()
                .where(RegisteredPersons.client_level == level)
                .count()
            )
            levels[level] = {
                "count": count,
                "percent": round(count / total * 100, 1) if total > 0 else 0,
            }

        # Клиенты без определенного уровня
        no_level = (
            RegisteredPersons.select()
            .where(
                (RegisteredPersons.client_level.is_null())
                | (RegisteredPersons.client_level == "")
            )
            .count()
        )

        return {
            "total": total,
            "levels": levels,
            "no_level": no_level,
        }
    except Exception as e:
        logger.exception(f"Ошибка при получении статистики по уровням клиентов: {e}")
        return {
            "total": 0,
            "levels": {
                "Black": {"count": 0, "percent": 0},
                "Gold": {"count": 0, "percent": 0},
                "Silver": {"count": 0, "percent": 0},
                "Bronze": {"count": 0, "percent": 0},
            },
            "no_level": 0,
        }
    finally:
        if not db.is_closed():
            db.close()


def update_client_level(
    id_telegram: int, client_level: str, accumulation_amount: float = None
) -> bool:
    """
    Обновление уровня клиента в базе данных

    :param id_telegram: ID пользователя в Telegram
    :param client_level: Уровень клиента (Bronze, Silver, Gold, Black)
    :param accumulation_amount: Накопительная сумма
    :return: True если успешно, False если нет
    """
    try:
        if db.is_closed():
            db.connect()

        query = RegisteredPersons.update(
            client_level=client_level,
            accumulation_amount=accumulation_amount,
            updated_at=datetime.now(),
        ).where(RegisteredPersons.id_telegram == id_telegram)
        result = query.execute()

        if result > 0:
            logger.info(f"Уровень клиента {id_telegram} обновлен на {client_level}")
            return True
        else:
            logger.warning(f"Клиент {id_telegram} не найден для обновления уровня")
            return False
    except Exception as e:
        logger.exception(f"Ошибка при обновлении уровня клиента {id_telegram}: {e}")
        return False
    finally:
        if not db.is_closed():
            db.close()


"""Всегда в конце, что бы создавать таблицы в базе данных"""


class ClientLevels(Model):
    """Справочник уровней клиентов с привилегиями и критериями"""

    level_name = CharField(unique=True)  # Название уровня (Bronze, Silver, Gold, Black)
    min_accumulation = DecimalField(
        max_digits=12, decimal_places=2
    )  # Мин. накопительная сумма
    emoji = CharField()  # Эмодзи уровня
    description = TextField()  # Описание уровня
    privileges = TextField()  # Привилегии уровня (JSON или текст)
    discount_percent = IntegerField(default=0)  # Процент скидки
    bonus_multiplier = DecimalField(
        max_digits=3, decimal_places=2, default=1.0
    )  # Множитель бонусов
    priority_service = BooleanField(default=False)  # Приоритетное обслуживание
    personal_manager = BooleanField(default=False)  # Персональный менеджер
    birthday_bonus = DecimalField(
        max_digits=10, decimal_places=2, default=0
    )  # Бонус на день рождения
    free_event_access = BooleanField(default=False)  # Бесплатный доступ на мероприятия
    created_at = DateTimeField(default=datetime.now)  # Дата создания записи
    updated_at = DateTimeField(default=datetime.now)  # Дата обновления записи

    class Meta:
        database = db
        table_name = "client_levels"
        indexes = ((("level_name",), True),)  # Уникальный индекс по названию


def get_client_level_info(level_name: str) -> dict | None:
    """
    Получение информации об уровне клиента.

    :param level_name: Название уровня (Bronze, Silver, Gold, Black)
    :return: Словарь с информацией об уровне или None
    """
    try:
        if db.is_closed():
            db.connect()

        level = ClientLevels.get_or_none(ClientLevels.level_name == level_name)

        if level:
            return {
                "level_name": level.level_name,
                "min_accumulation": float(level.min_accumulation),
                "emoji": level.emoji,
                "description": level.description,
                "privileges": level.privileges,
                "discount_percent": level.discount_percent,
                "bonus_multiplier": float(level.bonus_multiplier),
                "priority_service": level.priority_service,
                "personal_manager": level.personal_manager,
                "birthday_bonus": float(level.birthday_bonus),
                "free_event_access": level.free_event_access,
            }
        return None
    except Exception as e:
        logger.exception(f"Ошибка при получении информации об уровне {level_name}: {e}")
        return None
    finally:
        if not db.is_closed():
            db.close()


def get_all_client_levels() -> list:
    """
    Получение всех уровней клиентов.

    :return: Список словарей с информацией об уровнях
    """
    try:
        if db.is_closed():
            db.connect()

        levels = ClientLevels.select().order_by(ClientLevels.min_accumulation.desc())

        result = []
        for level in levels:
            result.append(
                {
                    "level_name": level.level_name,
                    "min_accumulation": float(level.min_accumulation),
                    "emoji": level.emoji,
                    "description": level.description,
                    "privileges": level.privileges,
                    "discount_percent": level.discount_percent,
                    "bonus_multiplier": float(level.bonus_multiplier),
                    "priority_service": level.priority_service,
                    "personal_manager": level.personal_manager,
                    "birthday_bonus": float(level.birthday_bonus),
                    "free_event_access": level.free_event_access,
                }
            )
        return result
    except Exception as e:
        logger.exception(f"Ошибка при получении всех уровней: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()


def initialize_client_levels():
    """
    Инициализация справочника уровней клиентов значениями по умолчанию.

    :return: True если успешно, False если нет
    """
    levels_data = [
        {
            "level_name": "Bronze",
            "min_accumulation": 0,
            "emoji": "🥉",
            "description": "Базовый уровень — начните своё путешествие с нами!",
            "privileges": json.dumps(
                [
                    "Доступ к базовой программе лояльности",
                    "Накопление бонусов с каждого заказа",
                    "Приглашения на открытые мероприятия",
                    "Персональные предложения в день рождения",
                ]
            ),
            "discount_percent": 0,
            "bonus_multiplier": 1.0,
            "priority_service": False,
            "personal_manager": False,
            "birthday_bonus": 500,
            "free_event_access": False,
        },
        {
            "level_name": "Silver",
            "min_accumulation": 10000,
            "emoji": "🥈",
            "description": "Серебряный уровень — больше преимуществ для постоянных гостей!",
            "privileges": json.dumps(
                [
                    "Все привилегии Bronze уровня",
                    "Повышенный кэшбэк бонусами (1.2x)",
                    "Приоритетное бронирование столов",
                    "Скидка 5% на банкетные услуги",
                    "Приглашения на закрытые мероприятия",
                    "Комплимент от заведения при посещении",
                ]
            ),
            "discount_percent": 5,
            "bonus_multiplier": 1.2,
            "priority_service": False,
            "personal_manager": False,
            "birthday_bonus": 1000,
            "free_event_access": False,
        },
        {
            "level_name": "Gold",
            "min_accumulation": 30000,
            "emoji": "🥇",
            "description": "Золотой уровень — элитное обслуживание для избранных!",
            "privileges": json.dumps(
                [
                    "Все привилегии Silver уровня",
                    "Максимальный кэшбэк бонусами (1.5x)",
                    "Персональный менеджер",
                    "Скидка 10% на все услуги",
                    "Бесплатный доступ на платные мероприятия",
                    "Приоритетное обслуживание",
                    "Подарок на день рождения",
                    "Возможность бронирования VIP-зон",
                ]
            ),
            "discount_percent": 10,
            "bonus_multiplier": 1.5,
            "priority_service": True,
            "personal_manager": False,
            "birthday_bonus": 2000,
            "free_event_access": True,
        },
        {
            "level_name": "Black",
            "min_accumulation": 60000,
            "emoji": "💎",
            "description": "Black уровень — максимальные привилегии для наших VIP-гостей!",
            "privileges": json.dumps(
                [
                    "Все привилегии Gold уровня",
                    "Эксклюзивный кэшбэк бонусами (2.0x)",
                    "Персональный консьерж 24/7",
                    "Скидка 15% на все услуги",
                    "Бесплатное посещение всех мероприятий",
                    "Доступ в закрытый Black-клуб",
                    "Индивидуальное меню по предпочтениям",
                    "Бесплатная парковка",
                    "Возможность организации частных мероприятий",
                    "Приоритет при бронировании любых дат",
                ]
            ),
            "discount_percent": 15,
            "bonus_multiplier": 2.0,
            "priority_service": True,
            "personal_manager": True,
            "birthday_bonus": 5000,
            "free_event_access": True,
        },
    ]

    try:
        if db.is_closed():
            db.connect()

        # Создаём таблицу если не существует
        db.create_tables([ClientLevels], safe=True)
        logger.info("Таблица client_levels создана или уже существует")

        for level_data in levels_data:
            level, created = ClientLevels.get_or_create(
                level_name=level_data["level_name"], defaults=level_data
            )

            if not created:
                # Обновляем существующую запись
                for key, value in level_data.items():
                    if key != "level_name":
                        setattr(level, key, value)
                level.updated_at = datetime.now()
                level.save()
            else:
                logger.info(f"Создан уровень {level_data['level_name']}")

        logger.info("Справочник уровней клиентов инициализирован")
        return True

    except Exception as e:
        logger.exception(f"Ошибка при инициализации уровней: {e}")
        return False
    finally:
        if not db.is_closed():
            db.close()


def initialize_owners(owner_ids: list[int]) -> None:
    """
    Инициализация владельцев из .env в таблицу Admins.
    Вызывается при запуске, чтобы владельцы из конфига всегда были в БД.

    :param owner_ids: Список ID владельцев из .env
    """
    if not owner_ids:
        logger.info("OWNER_IDS не задан в .env, пропускаем инициализацию владельцев")
        return

    try:
        if db.is_closed():
            db.connect()

        for owner_id in owner_ids:
            admin, created = Admins.get_or_create(
                id_telegram=owner_id,
                defaults={
                    "role": "owner",
                    "is_active": True,
                    "full_name": "Владелец",
                },
            )

            if not created:
                # Убеждаемся что роль owner и активен
                if admin.role != "owner" or not admin.is_active:
                    admin.role = "owner"
                    admin.is_active = True
                    admin.save()
                    logger.info(f"Обновлён владелец {owner_id}")
            else:
                logger.info(f"Создан владелец {owner_id}")

        logger.info(f"Владельцы инициализированы: {owner_ids}")

    except Exception as e:
        logger.exception(f"Ошибка при инициализации владельцев: {e}")
    finally:
        if not db.is_closed():
            db.close()


"""Таблица для управления администраторами бота"""


class Admins(Model):
    """Таблица администраторов бота (дополнительные к OWNER_IDS из .env)"""

    id_telegram = IntegerField(unique=True)  # ID пользователя в Telegram
    username = CharField(null=True)  # Username в Telegram
    full_name = CharField(null=True)  # Имя и фамилия
    role = CharField(default="admin")  # Роль: owner, admin
    added_by = IntegerField(null=True)  # ID владельца, который добавил
    added_at = DateTimeField(default=datetime.now)  # Дата добавления
    is_active = BooleanField(default=True)  # Активен ли администратор

    class Meta:
        database = db
        table_name = "admins"
        indexes = ((("id_telegram",), True),)


def add_admin(
    id_telegram: int,
    added_by: int,
    username: str = None,
    full_name: str = None,
    role: str = "admin",
) -> dict:
    """
    Добавление администратора

    :param id_telegram: ID пользователя в Telegram
    :param added_by: ID владельца, который добавляет
    :param username: Username в Telegram
    :param full_name: Имя и фамилия
    :param role: Роль (admin)
    :return: Словарь с результатом
    """
    try:
        if db.is_closed():
            db.connect()

        # Проверяем, не является ли уже администратором
        existing = Admins.get_or_none(Admins.id_telegram == id_telegram)
        if existing:
            if existing.is_active:
                return {"success": False, "message": "Уже является администратором"}
            else:
                # Реактивируем
                existing.is_active = True
                existing.role = role
                existing.added_by = added_by
                existing.added_at = datetime.now()
                existing.username = username
                existing.full_name = full_name
                existing.save()
                logger.info(f"Администратор {id_telegram} реактивирован")
                return {
                    "success": True,
                    "message": "Администратор реактивирован",
                    "action": "reactivated",
                }

        Admins.create(
            id_telegram=id_telegram,
            username=username,
            full_name=full_name,
            role=role,
            added_by=added_by,
            is_active=True,
        )
        logger.info(f"Добавлен администратор: {id_telegram} ({full_name})")
        return {"success": True, "message": "Администратор добавлен", "action": "added"}

    except Exception as e:
        logger.exception(f"Ошибка при добавлении администратора {id_telegram}: {e}")
        return {"success": False, "message": f"Ошибка: {e}"}
    finally:
        if not db.is_closed():
            db.close()


def remove_admin(id_telegram: int) -> bool:
    """
    Удаление (деактивация) администратора

    :param id_telegram: ID пользователя в Telegram
    :return: True если удалён, False если не найден
    """
    try:
        if db.is_closed():
            db.connect()

        query = Admins.update(is_active=False).where(
            (Admins.id_telegram == id_telegram) & (Admins.role != "owner")
        )
        result = query.execute()

        if result > 0:
            logger.info(f"Администратор {id_telegram} деактивирован")
            return True
        logger.warning(f"Администратор {id_telegram} не найден или является владельцем")
        return False

    except Exception as e:
        logger.exception(f"Ошибка при удалении администратора {id_telegram}: {e}")
        return False
    finally:
        if not db.is_closed():
            db.close()


def is_admin_in_db(id_telegram: int) -> bool:
    """
    Проверка, является ли пользователь администратором в БД

    :param id_telegram: ID пользователя в Telegram
    :return: True если администратор
    """
    try:
        if db.is_closed():
            db.connect()

        admin = Admins.get_or_none(
            (Admins.id_telegram == id_telegram) & Admins.is_active
        )
        return admin is not None

    except Exception as e:
        logger.exception(f"Ошибка при проверке администратора {id_telegram}: {e}")
        return False
    finally:
        if not db.is_closed():
            db.close()


def is_owner_in_db(id_telegram: int) -> bool:
    """
    Проверка, является ли пользователь владельцем в БД

    :param id_telegram: ID пользователя в Telegram
    :return: True если владелец
    """
    try:
        if db.is_closed():
            db.connect()

        admin = Admins.get_or_none(
            (Admins.id_telegram == id_telegram)
            & Admins.is_active
            & (Admins.role == "owner")
        )
        return admin is not None

    except Exception as e:
        logger.exception(f"Ошибка при проверке владельца {id_telegram}: {e}")
        return False
    finally:
        if not db.is_closed():
            db.close()


def get_all_admins() -> list:
    """
    Получение списка всех активных администраторов

    :return: Список словарей с данными администраторов
    """
    try:
        if db.is_closed():
            db.connect()

        admins = (
            Admins.select()
            .where(Admins.is_active)
            .order_by(Admins.role.desc(), Admins.added_at.asc())
        )

        result = []
        for admin in admins:
            result.append(
                {
                    "id_telegram": admin.id_telegram,
                    "username": admin.username,
                    "full_name": admin.full_name,
                    "role": admin.role,
                    "added_by": admin.added_by,
                    "added_at": admin.added_at,
                    "is_active": admin.is_active,
                }
            )
        return result

    except Exception as e:
        logger.exception(f"Ошибка при получении списка администраторов: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()


def get_admin_role(id_telegram: int) -> str | None:
    """
    Получение роли пользователя

    :param id_telegram: ID пользователя в Telegram
    :return: Роль (owner, admin) или None если не администратор
    """
    try:
        if db.is_closed():
            db.connect()

        admin = Admins.get_or_none(
            (Admins.id_telegram == id_telegram) & Admins.is_active
        )
        return admin.role if admin else None

    except Exception as e:
        logger.exception(f"Ошибка при получении роли {id_telegram}: {e}")
        return None
    finally:
        if not db.is_closed():
            db.close()


def get_admins_count() -> int:
    """
    Получение количества активных администраторов

    :return: Количество администраторов
    """
    try:
        if db.is_closed():
            db.connect()

        count = Admins.select().where(Admins.is_active).count()
        return count

    except Exception as e:
        logger.exception(f"Ошибка при подсчёте администраторов: {e}")
        return 0
    finally:
        if not db.is_closed():
            db.close()


def create_tables():
    """Создание таблицы в базе данных"""
    db.create_tables(
        [
            RegisteredPersons,
            StartPersons,
            GiftWheelSpins,
            MarketingMessages,
            PromoCodes,
            Consents,
            Events,
            ClientLevels,
            Admins,
        ]
    )

    # Миграция: добавляем новые поля в существующую таблицу RegisteredPersons
    try:
        if db.is_closed():
            db.connect()

        # Проверяем и добавляем поле client_level если его нет
        cursor = db.execute_sql("PRAGMA table_info(registered_persons)")
        columns = [row[1] for row in cursor.fetchall()]

        if "client_level" not in columns:
            db.execute_sql(
                "ALTER TABLE registered_persons ADD COLUMN client_level TEXT"
            )
            logger.info("Добавлено поле client_level в таблицу registered_persons")

        if "accumulation_amount" not in columns:
            db.execute_sql(
                "ALTER TABLE registered_persons ADD COLUMN accumulation_amount REAL"
            )
            logger.info(
                "Добавлено поле accumulation_amount в таблицу registered_persons"
            )

        # Проверяем существование таблицы client_levels
        cursor = db.execute_sql(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='client_levels'"
        )
        if not cursor.fetchone():
            logger.info("Таблица client_levels будет создана")

    except Exception as e:
        logger.exception(f"Ошибка при миграции таблицы registered_persons: {e}")
    finally:
        if not db.is_closed():
            db.close()


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
        indexes = ((("id_telegram", "sent_at"), False),)  # Индекс для быстрого поиска


def log_marketing_message(
    id_telegram: int, message_text: str, message_type: str = "text"
) -> None:
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
            sent_at=datetime.now(),
        )
    except Exception as e:
        logger.exception(f"Ошибка при логировании рассылки: {e}")
    finally:
        if not db.is_closed():
            db.close()


def update_message_status(
    id_telegram: int, is_blocked: bool = False, is_read: bool = False
) -> None:
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
        query = (
            MarketingMessages.update(is_blocked=is_blocked, is_read=is_read)
            .where(MarketingMessages.id_telegram == id_telegram)
            .order_by(MarketingMessages.sent_at.desc())
            .limit(1)
        )
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

        user_ids = StartPersons.select(StartPersons.id_telegram).order_by(
            StartPersons.updated_at.desc()
        )

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
        logger.exception(
            f"Ошибка при получении количества зарегистрированных пользователей: {e}"
        )
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
        text_count = (
            MarketingMessages.select()
            .where(MarketingMessages.message_type == "text")
            .count()
        )
        photo_count = (
            MarketingMessages.select()
            .where(MarketingMessages.message_type == "photo")
            .count()
        )
        video_count = (
            MarketingMessages.select()
            .where(MarketingMessages.message_type == "video")
            .count()
        )
        blocked_count = (
            MarketingMessages.select().where(MarketingMessages.is_blocked).count()
        )

        # Уникальные пользователи, получившие рассылки
        unique_users = MarketingMessages.select(
            fn.COUNT(fn.DISTINCT(MarketingMessages.id_telegram))
        ).scalar()

        return {
            "total_messages": total_messages,
            "text_count": text_count,
            "photo_count": photo_count,
            "video_count": video_count,
            "blocked_count": blocked_count,
            "unique_users": unique_users,
        }
    except Exception as e:
        logger.exception(f"Ошибка при получении статистики рассылок: {e}")
        return {
            "total_messages": 0,
            "text_count": 0,
            "photo_count": 0,
            "video_count": 0,
            "blocked_count": 0,
            "unique_users": 0,
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
                    if "-" in birthday:
                        birthday_formatted = f"{birthday[8:10]}.{birthday[5:7]}"
                    elif "." in birthday:
                        birthday_formatted = birthday[:5]
                    else:
                        continue

                    if birthday_formatted == today:
                        result.append(
                            {
                                "id_telegram": person.id_telegram,
                                "id_quickresto": person.id_quickresto,
                                "phone_telegram": person.phone_telegram,
                                "first_name": person.first_name,
                                "last_name": person.last_name,
                                "birthday_user": person.birthday_user,
                            }
                        )

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
                    if "-" in birthday:
                        birthday_formatted = f"{birthday[8:10]}.{birthday[5:7]}"
                    elif "." in birthday:
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
        target_accrual_date = (
            datetime.now() - timedelta(days=90 - days_until_burn)
        ).date()

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
                    result.append(
                        {
                            "id_telegram": person.id_telegram,
                            "id_quickresto": person.id_quickresto,
                            "phone_telegram": person.phone_telegram,
                            "first_name": person.first_name,
                            "last_name": person.last_name,
                            "user_bonus": person.user_bonus,
                            "bot_bonus_amount": person.bot_bonus_amount,  # Сумма бонусов, начисленных ботом
                            "bonus_accrued_at": person.bonus_accrued_at,
                            "burn_date": burn_date,
                        }
                    )

        return result
    except Exception as e:
        logger.exception(
            f"Ошибка при получении пользователей с горящими бонусами бота: {e}"
        )
        return []
    finally:
        if not db.is_closed():
            db.close()


def update_bonus_accrual_date(
    id_telegram: int, accrued_at: datetime = None, bonus_amount: float = None
) -> bool:
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
            query = RegisteredPersons.update(
                bonus_accrued_at=accrued_at, bot_bonus_amount=bonus_amount
            ).where(RegisteredPersons.id_telegram == id_telegram)
        else:
            query = RegisteredPersons.update(bonus_accrued_at=accrued_at).where(
                RegisteredPersons.id_telegram == id_telegram
            )

        result = query.execute()

        if result > 0:
            logger.info(
                f"Дата начисления бонусов ботом обновлена для пользователя {id_telegram}"
            )
            return True
        return False
    except Exception as e:
        logger.exception(f"Ошибка при обновлении даты начисления бонусов ботом: {e}")
        return False
    finally:
        if not db.is_closed():
            db.close()


def get_user_burning_bonus_info(id_telegram: int) -> dict | None:
    """
    Получение информации о сгорающих бонусах конкретного пользователя

    :param id_telegram: ID пользователя в Telegram
    :return: Словарь с информацией о сгорающих бонусах или None
    """
    try:
        if db.is_closed():
            db.connect()

        from datetime import timedelta

        user = RegisteredPersons.get_or_none(
            RegisteredPersons.id_telegram == id_telegram
        )

        if not user or not user.bonus_accrued_at or not user.bot_bonus_amount:
            return None

        # Бонусы сгорают через 90 дней (3 месяца) с момента начисления
        burn_date = user.bonus_accrued_at + timedelta(days=90)
        days_until_burn = (burn_date.date() - datetime.now().date()).days

        # Если бонусы уже сгорели, возвращаем None
        if days_until_burn < 0:
            return None

        return {
            "bot_bonus_amount": user.bot_bonus_amount,
            "bonus_accrued_at": user.bonus_accrued_at,
            "burn_date": burn_date,
            "days_until_burn": days_until_burn,
        }
    except Exception as e:
        logger.exception(
            f"Ошибка при получении информации о сгорающих бонусах пользователя {id_telegram}: {e}"
        )
        return None
    finally:
        if not db.is_closed():
            db.close()


def has_user_claimed_gift_bonus(id_telegram: int) -> bool:
    """
    Проверка, получил ли пользователь подарочные бонусы 3000

    :param id_telegram: ID пользователя в Telegram
    :return: True если получил, False если нет
    """
    try:
        if db.is_closed():
            db.connect()

        user = RegisteredPersons.get_or_none(
            RegisteredPersons.id_telegram == id_telegram
        )

        if not user:
            return False

        return user.gift_bonus_claimed
    except Exception as e:
        logger.exception(
            f"Ошибка при проверке получения подарочных бонусов пользователем {id_telegram}: {e}"
        )
        return False
    finally:
        if not db.is_closed():
            db.close()


def mark_gift_bonus_claimed(id_telegram: int) -> bool:
    """
    Отметить, что пользователь получил подарочные бонусы 3000

    :param id_telegram: ID пользователя в Telegram
    :return: True если успешно, False если ошибка
    """
    try:
        if db.is_closed():
            db.connect()

        query = RegisteredPersons.update(
            gift_bonus_claimed=True, gift_bonus_claimed_at=datetime.now()
        ).where(RegisteredPersons.id_telegram == id_telegram)

        result = query.execute()

        if result > 0:
            logger.info(f"Пользователь {id_telegram} получил подарочные бонусы 3000")
            return True
        return False
    except Exception as e:
        logger.exception(
            f"Ошибка при отметке получения подарочных бонусов пользователем {id_telegram}: {e}"
        )
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
        indexes = ((("code",), True),)  # Уникальный индекс на код


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
            is_active=True,
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
                "used_at": promo.used_at,
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
            (PromoCodes.code == code)
            & PromoCodes.is_active
            & PromoCodes.used_by.is_null()
        )

        if not promo:
            return False

        # Помечаем как использованный
        query = PromoCodes.update(
            used_by=id_telegram, used_at=datetime.now(), is_active=False
        ).where(PromoCodes.code == code)

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
            result.append(
                {
                    "code": promo.code,
                    "bonus_amount": promo.bonus_amount,
                    "description": promo.description,
                    "is_active": promo.is_active,
                    "created_at": promo.created_at,
                    "used_by": promo.used_by,
                    "used_at": promo.used_at,
                }
            )
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

        count = PromoCodes.select().where(PromoCodes.is_active).count()
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


"""Таблица для учёта согласий на обработку персональных данных"""


class Consents(Model):
    """Таблица для хранения согласий пользователей на обработку персональных данных"""

    id_telegram = IntegerField(unique=True)  # ID пользователя в Telegram
    is_consent = BooleanField(default=True)  # Флаг согласия
    consented_at = DateTimeField(default=datetime.now)  # Дата получения согласия
    ip_address = CharField(null=True)  # IP-адрес (если доступен)
    user_agent = TextField(null=True)  # User agent (если доступен)

    class Meta:
        database = db
        table_name = "consents"
        indexes = ((("id_telegram",), True),)  # Уникальный индекс на ID пользователя


def add_consent(
    id_telegram: int, ip_address: str = None, user_agent: str = None
) -> bool:
    """
    Добавление согласия на обработку персональных данных

    :param id_telegram: ID пользователя в Telegram
    :param ip_address: IP-адрес пользователя (если доступен)
    :param user_agent: User agent (если доступен)
    :return: True если добавлено, False если ошибка
    """
    try:
        if db.is_closed():
            db.connect()

        Consents.create(
            id_telegram=id_telegram,
            is_consent=True,
            consented_at=datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        logger.info(
            f"Пользователь {id_telegram} дал согласие на обработку персональных данных"
        )
        return True
    except Exception as e:
        logger.exception(
            f"Ошибка при добавлении согласия пользователя {id_telegram}: {e}"
        )
        return False
    finally:
        if not db.is_closed():
            db.close()


def has_consent(id_telegram: int) -> bool:
    """
    Проверка наличия согласия на обработку персональных данных

    :param id_telegram: ID пользователя в Telegram
    :return: True если согласие есть, False если нет
    """
    try:
        if db.is_closed():
            db.connect()

        consent = Consents.get_or_none(
            (Consents.id_telegram == id_telegram) & Consents.is_consent
        )
        return consent is not None
    except Exception as e:
        logger.exception(
            f"Ошибка при проверке согласия пользователя {id_telegram}: {e}"
        )
        return False
    finally:
        if not db.is_closed():
            db.close()


def get_consent_info(id_telegram: int) -> dict | None:
    """
    Получение информации о согласии пользователя

    :param id_telegram: ID пользователя в Telegram
    :return: Словарь с данными согласия или None если не найдено
    """
    try:
        if db.is_closed():
            db.connect()

        consent = Consents.get_or_none(Consents.id_telegram == id_telegram)
        if consent:
            return {
                "id_telegram": consent.id_telegram,
                "is_consent": consent.is_consent,
                "consented_at": consent.consented_at,
                "ip_address": consent.ip_address,
                "user_agent": consent.user_agent,
            }
        return None
    except Exception as e:
        logger.exception(
            f"Ошибка при получении информации о согласии {id_telegram}: {e}"
        )
        return None
    finally:
        if not db.is_closed():
            db.close()


def revoke_consent(id_telegram: int) -> bool:
    """
    Отзыв согласия на обработку персональных данных

    :param id_telegram: ID пользователя в Telegram
    :return: True если отозвано, False если ошибка
    """
    try:
        if db.is_closed():
            db.connect()

        query = Consents.update(is_consent=False).where(
            Consents.id_telegram == id_telegram
        )

        result = query.execute()

        if result > 0:
            logger.info(
                f"Пользователь {id_telegram} отозвал согласие на обработку персональных данных"
            )
            return True
        return False
    except Exception as e:
        logger.exception(f"Ошибка при отзыве согласия пользователя {id_telegram}: {e}")
        return False
    finally:
        if not db.is_closed():
            db.close()


def get_consents_count() -> int:
    """
    Получение количества пользователей, давших согласие

    :return: Количество пользователей с согласием
    """
    try:
        if db.is_closed():
            db.connect()

        count = Consents.select().where(Consents.is_consent).count()
        return count
    except Exception as e:
        logger.exception(f"Ошибка при подсчёте согласий: {e}")
        return 0
    finally:
        if not db.is_closed():
            db.close()


"""Таблица для учёта мероприятий"""


class Events(Model):
    """Таблица для хранения мероприятий"""

    title = CharField()  # Название мероприятия
    description = TextField()  # Описание мероприятия
    event_date = DateTimeField()  # Дата и время мероприятия
    photo_id = CharField(null=True)  # ID фото мероприятия (если есть)
    is_active = BooleanField(default=True)  # Активно ли мероприятие
    created_at = DateTimeField(default=datetime.now)  # Дата создания
    created_by = IntegerField()  # ID администратора, создавшего мероприятие

    # Поля для автоматических напоминаний
    reminder_text_3days = TextField(null=True)  # Текст напоминания за 3 дня
    reminder_text_1day = TextField(null=True)  # Текст напоминания за 1 день
    reminder_text_event_day = TextField(
        null=True
    )  # Текст напоминания в день мероприятия
    reminder_3days_sent = BooleanField(
        default=False
    )  # Отправлено ли напоминание за 3 дня
    reminder_1day_sent = BooleanField(
        default=False
    )  # Отправлено ли напоминание за 1 день
    reminder_event_day_sent = BooleanField(
        default=False
    )  # Отправлено ли напоминание в день мероприятия

    class Meta:
        database = db
        table_name = "events"
        indexes = (
            (("event_date",), False),  # Индекс для быстрого поиска по дате
            (("is_active",), False),  # Индекс для фильтрации активных
        )


def create_event(
    title: str,
    description: str,
    event_date: datetime,
    created_by: int,
    photo_id: str = None,
    reminder_text_3days: str = None,
    reminder_text_1day: str = None,
    reminder_text_event_day: str = None,
) -> bool:
    """
    Создание нового мероприятия

    :param title: Название мероприятия
    :param description: Описание мероприятия
    :param event_date: Дата и время мероприятия
    :param created_by: ID администратора, создавшего мероприятие
    :param photo_id: ID фото мероприятия (если есть)
    :param reminder_text_3days: Текст напоминания за 3 дня
    :param reminder_text_1day: Текст напоминания за 1 день
    :param reminder_text_event_day: Текст напоминания в день мероприятия
    :return: True если создано, False если ошибка
    """
    try:
        if db.is_closed():
            db.connect()

        Events.create(
            title=title,
            description=description,
            event_date=event_date,
            created_by=created_by,
            photo_id=photo_id,
            is_active=False,  # Создаем неактивным, чтобы администратор мог активировать вручную
            reminder_text_3days=reminder_text_3days,
            reminder_text_1day=reminder_text_1day,
            reminder_text_event_day=reminder_text_event_day,
        )
        logger.info(f"Создано мероприятие: {title} на {event_date}")
        return True
    except Exception as e:
        logger.exception(f"Ошибка при создании мероприятия {title}: {e}")
        return False
    finally:
        if not db.is_closed():
            db.close()


def get_event(event_id: int) -> dict | None:
    """
    Получение информации о мероприятии по ID

    :param event_id: ID мероприятия
    :return: Словарь с данными мероприятия или None если не найдено
    """
    try:
        if db.is_closed():
            db.connect()

        event = Events.get_or_none(Events.id == event_id)
        if event:
            return {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "event_date": event.event_date,
                "photo_id": event.photo_id,
                "is_active": event.is_active,
                "created_at": event.created_at,
                "created_by": event.created_by,
            }
        return None
    except Exception as e:
        logger.exception(f"Ошибка при получении мероприятия {event_id}: {e}")
        return None
    finally:
        if not db.is_closed():
            db.close()


def get_all_events(active_only: bool = False) -> list:
    """
    Получение всех мероприятий

    :param active_only: True если только активные
    :return: Список словарей с данными мероприятий
    """
    try:
        if db.is_closed():
            db.connect()

        query = Events.select()
        if active_only:
            query = query.where(Events.is_active)
        query = query.order_by(Events.event_date.desc())

        events = query.execute()

        result = []
        for event in events:
            result.append(
                {
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "event_date": event.event_date,
                    "photo_id": event.photo_id,
                    "is_active": event.is_active,
                    "created_at": event.created_at,
                    "created_by": event.created_by,
                }
            )
        return result
    except Exception as e:
        logger.exception(f"Ошибка при получении списка мероприятий: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()


def delete_event(event_id: int) -> bool:
    """
    Удаление мероприятия

    :param event_id: ID мероприятия
    :return: True если удалено, False если не найдено
    """
    try:
        if db.is_closed():
            db.connect()

        query = Events.delete().where(Events.id == event_id)
        result = query.execute()

        if result > 0:
            logger.info(f"Мероприятие {event_id} удалено")
            return True
        logger.warning(f"Мероприятие {event_id} не найдено")
        return False
    except Exception as e:
        logger.exception(f"Ошибка при удалении мероприятия {event_id}: {e}")
        return False
    finally:
        if not db.is_closed():
            db.close()


def update_reminder_sent(event_id: int, reminder_type: str) -> bool:
    """
    Обновление статуса отправленного напоминания

    :param event_id: ID мероприятия
    :param reminder_type: Тип напоминания (3days, 1day, event_day)
    :return: True если обновлено, False если ошибка
    """
    try:
        if db.is_closed():
            db.connect()

        field_name = f"reminder_{reminder_type}_sent"
        query = Events.update(**{field_name: True}).where(Events.id == event_id)
        result = query.execute()

        if result > 0:
            logger.info(
                f"Обновлён статус напоминания {reminder_type} для мероприятия {event_id}"
            )
            return True
        return False
    except Exception as e:
        logger.exception(f"Ошибка при обновлении статуса напоминания: {e}")
        return False
    finally:
        if not db.is_closed():
            db.close()


def get_events_for_reminder(days_until: int) -> list:
    """
    Получение мероприятий, для которых нужно отправить напоминание

    :param days_until: За сколько дней до мероприятия (3, 1, 0)
    :return: Список мероприятий
    """
    try:
        if db.is_closed():
            db.connect()

        from datetime import date, timedelta

        today = date.now()
        target_date = today + timedelta(days=days_until)

        # Определяем поле для проверки отправки
        if days_until == 3:
            sent_field = Events.reminder_3days_sent
            text_field = Events.reminder_text_3days
        elif days_until == 1:
            sent_field = Events.reminder_1day_sent
            text_field = Events.reminder_text_1day
        else:  # days_until == 0
            sent_field = Events.reminder_event_day_sent
            text_field = Events.reminder_text_event_day

        # Получаем мероприятия, где:
        # - мероприятие активное
        # - напоминание ещё не отправлено
        # - есть текст напоминания
        # - дата мероприятия через days_until дней
        events = (
            Events.select()
            .where(
                Events.is_active
                & (not sent_field)
                & (text_field.is_null(False))
                & (fn.DATE(Events.event_date) == target_date)
            )
            .order_by(Events.event_date.asc())
        )

        result = []
        for event in events:
            result.append(
                {
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "event_date": event.event_date,
                    "photo_id": event.photo_id,
                    "reminder_text": getattr(
                        event,
                        (
                            f"reminder_text_{days_until}days"
                            if days_until > 0
                            else "reminder_text_event_day"
                        ),
                    ),
                }
            )
        return result
    except Exception as e:
        logger.exception(f"Ошибка при получении мероприятий для напоминания: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()


def update_event_status(event_id: int, is_active: bool) -> bool:
    """
    Обновление статуса мероприятия

    :param event_id: ID мероприятия
    :param is_active: Новый статус
    :return: True если обновлено, False если ошибка
    """
    try:
        if db.is_closed():
            db.connect()

        query = Events.update(is_active=is_active).where(Events.id == event_id)
        result = query.execute()

        if result > 0:
            logger.info(f"Мероприятие {event_id} обновлено, статус: {is_active}")
            return True
        return False
    except Exception as e:
        logger.exception(f"Ошибка при обновлении статуса мероприятия {event_id}: {e}")
        return False
    finally:
        if not db.is_closed():
            db.close()


def get_upcoming_events(days: int = 7) -> list:
    """
    Получение предстоящих мероприятий (в течение указанного количества дней)

    :param days: Количество дней
    :return: Список словарей с данными мероприятий
    """
    try:
        if db.is_closed():
            db.connect()

        from datetime import timedelta

        now = datetime.now()
        future_date = now + timedelta(days=days)

        events = (
            Events.select()
            .where(
                Events.is_active
                & (Events.event_date >= now)
                & (Events.event_date <= future_date)
            )
            .order_by(Events.event_date.asc())
        )

        result = []
        for event in events:
            result.append(
                {
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "event_date": event.event_date,
                    "photo_id": event.photo_id,
                    "is_active": event.is_active,
                    "created_at": event.created_at,
                    "created_by": event.created_by,
                }
            )
        return result
    except Exception as e:
        logger.exception(f"Ошибка при получении предстоящих мероприятий: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()


def get_events_count() -> dict:
    """
    Получение статистики по мероприятиям

    :return: Словарь со статистикой
    """
    try:
        if db.is_closed():
            db.connect()

        total = Events.select().count()
        active = Events.select().where(Events.is_active).count()
        inactive = Events.select().where(not Events.is_active).count()

        return {"total": total, "active": active, "inactive": inactive}
    except Exception as e:
        logger.exception(f"Ошибка при получении статистики мероприятий: {e}")
        return {"total": 0, "active": 0, "inactive": 0}
    finally:
        if not db.is_closed():
            db.close()
