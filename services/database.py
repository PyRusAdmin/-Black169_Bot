# -*- coding: utf-8 -*-
from datetime import datetime
from peewee import *  # https://docs.peewee-orm.com/en/latest/index.html
from loguru import logger

db = SqliteDatabase("database.db")

"""Запись в базу данных о пользователях, которые зарегистрировались в боте, передав свой номер телефона"""


class RegisteredPersons(Model):
    """База данных для хранения данных о пользователях Telegram"""

    id_telegram = IntegerField(unique=True)  # id пользователя в Telegram
    last_name_telegram = CharField(null=True)  # фамилия пользователя в Telegram
    first_name_telegram = CharField(null=True)  # имя пользователя в Telegram
    username_telegram = CharField(null=True)  # username пользователя в Telegram
    phone_telegram = CharField(null=True)  # номер телефона пользователя в Telegram
    updated_at = DateTimeField(default=datetime.now)  # дата и время обновления

    class Meta:
        database = db  # база данных
        table_name = "registered_persons"  # название таблицы


def write_to_db_registered_person(data):
    """Запись данных о пользователе в базу данных"""
    id_telegram = data.get("id_telegram")
    last_name_telegram = data.get("last_name_telegram")
    first_name_telegram = data.get("first_name_telegram")
    username_telegram = data.get("username_telegram")
    phone_telegram = data.get("phone_telegram")
    try:
        person, created = RegisteredPersons.get_or_create(id_telegram=id_telegram, defaults={
            "last_name_telegram": last_name_telegram,
            "first_name_telegram": first_name_telegram,
            "username_telegram": username_telegram,
            "phone_telegram": phone_telegram,
        })
        if not created:
            person.last_name_telegram = last_name_telegram
            person.first_name_telegram = first_name_telegram
            person.username_telegram = username_telegram
            person.phone_telegram = phone_telegram
            person.updated_at = datetime.now()
        person.save()
    except Exception as e:
        logger.exception(e)


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


"""Всегда в конце, что бы создавать таблицы в базе данных"""


def create_tables():
    """Создание таблицы в базе данных"""
    db.create_tables([RegisteredPersons, StartPersons])
