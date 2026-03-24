# The Black 169 — Telegram Bot

Телеграм-бот для ресторана The Black 169. Позволяет гостям регистрироваться, отслеживать бонусы и получать информацию об
акциях и мероприятиях. Интегрирован с системой лояльности QuickResto.

## Возможности

- Регистрация пользователей по номеру телефона
- Интеграция с QuickResto API
- Отслеживание активности пользователей
- Админ-панель для управления

## Структура проекта

```
├── config.py              # Конфигурация (токен, dispatcher)
├── main.py                # Точка входа
├── handlers/
│   ├── handlers.py        # Общие обработчики
│   ├── user_handlers.py   # Обработчики пользователей
│   └── admin_handlers.py  # Обработчики администраторов
├── services/
│   ├── database.py        # Модели и функции для работы с БД
│   └── i18n.py            # Локализация
├── locales/
│   └── ru.ftl            # Переводы (Fluent)
├── doc/
│   └── Doc.md             # Документация
├── log/
│   └── log.log            # Логи
└── database.db            # SQLite база данных
```

## База данных

### Таблица `start_persons`

Пользователи, запустившие бота командой `/start`.

| Поле                | Тип      | Описание                   |
|---------------------|----------|----------------------------|
| id_telegram         | INTEGER  | Уникальный ID пользователя |
| last_name_telegram  | TEXT     | Фамилия (Telegram)         |
| first_name_telegram | TEXT     | Имя (Telegram)             |
| username_telegram   | TEXT     | Username (Telegram)        |
| updated_at          | DATETIME | Дата обновления            |

### Таблица `registered_persons`

Пользователи, отправившие номер телефона. Данные из Telegram и QuickResto.

| Поле            | Тип      | Описание                   |
|-----------------|----------|----------------------------|
| id_telegram     | INTEGER  | Уникальный ID пользователя |
| phone_telegram  | TEXT     | Номер телефона             |
| last_name       | TEXT     | Фамилия (QuickResto)       |
| first_name      | TEXT     | Имя (QuickResto)           |
| patronymic_name | TEXT     | Отчество (QuickResto)      |
| birthday_user   | TEXT     | Дата рождения              |
| user_bonus      | TEXT     | Бонусы                     |
| date_of_visit   | DATETIME | Последнее посещение        |
| updated_at      | DATETIME | Дата обновления            |

## Запуск

1. Зависимости:

```bash
pip install aiogram peewee python-dotenv loguru fluent-runtime
```

2. Файл `.env`:

```
BOT_TOKEN=your_token_here
```

3. Запуск:

```bash
python main.py
```

## Архитектура обработчиков

```
dp (Dispatcher)
├── handlers        # Общие
├── user_handlers   # Пользователи
└── admin_handlers  # Администраторы
```

## Логирование

- `log/log.log` — файл
- stdout — консоль

## Локализация

Fluent-формат в `locales/ru.ftl`.
