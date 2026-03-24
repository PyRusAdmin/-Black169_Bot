# -*- coding: utf-8 -*-
from datetime import datetime
from peewee import *  # https://docs.peewee-orm.com/en/latest/index.html
from loguru import logger

db = SqliteDatabase("database.db")


class Person(Model):
    """База данных для хранения данных о пользователях Telegram"""

    id_telegram = IntegerField(unique=True)  # id пользователя в Telegram
    last_name_telegram = CharField(null=True)  # фамилия пользователя в Telegram
    first_name_telegram = CharField(null=True)  # имя пользователя в Telegram
    username_telegram = CharField(null=True)  # username пользователя в Telegram
    phone_telegram = CharField(null=True)  # номер телефона пользователя в Telegram
    updated_at = DateTimeField(default=datetime.now)  # дата и время обновления

    class Meta:
        database = db  # база данных
        table_name = "person"  # название таблицы


def create_tables():
    """Создание таблицы в базе данных"""
    db.create_tables([Person])


def write_to_db_person(id_telegram, last_name_telegram, first_name_telegram, username_telegram, phone_telegram):
    """Запись данных о пользователе в базу данных"""
    try:
        person, created = Person.get_or_create(id_telegram=id_telegram, defaults={
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
