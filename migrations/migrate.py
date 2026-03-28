# -*- coding: utf-8 -*-
"""
Скрипт для миграции базы данных
Добавляет поля для отслеживания бонусов, начисленных ботом
"""

import sqlite3
from loguru import logger

DB_PATH = "database.db"


def migrate_database():
    """Выполнение миграции базы данных"""
    logger.info("Начало миграции базы данных...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Проверяем, существует ли уже поле bonus_accrued_at
        cursor.execute("PRAGMA table_info(registered_persons)")
        columns = [col[1] for col in cursor.fetchall()]

        # Добавляем поле bonus_accrued_at если его нет
        if "bonus_accrued_at" not in columns:
            logger.info("Добавление поля bonus_accrued_at...")
            cursor.execute("""
                ALTER TABLE registered_persons 
                ADD COLUMN bonus_accrued_at DATETIME NULL
            """)
            logger.success("Поле bonus_accrued_at успешно добавлено")
        else:
            logger.info("Поле bonus_accrued_at уже существует")

        # Добавляем поле bot_bonus_amount если его нет
        if "bot_bonus_amount" not in columns:
            logger.info("Добавление поля bot_bonus_amount...")
            cursor.execute("""
                ALTER TABLE registered_persons 
                ADD COLUMN bot_bonus_amount DECIMAL(10, 2) NULL
            """)
            logger.success("Поле bot_bonus_amount успешно добавлено")
        else:
            logger.info("Поле bot_bonus_amount уже существует")

        conn.commit()
        logger.success("Миграция базы данных успешно завершена!")

    except Exception as e:
        logger.exception(f"Ошибка при выполнении миграции: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    migrate_database()
