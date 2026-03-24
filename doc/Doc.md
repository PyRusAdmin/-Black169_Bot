# The Black 169 — Telegram Bot

Телеграм-бот для ресторана The Black 169. Позволяет гостям регистрироваться, отслеживать бонусы и получать информацию об
акциях и мероприятиях. Интегрирован с системой лояльности QuickResto через API.

## Возможности

- Регистрация пользователей по номеру телефона
- Интеграция с QuickResto API
- Проверка клиентов по базе QuickResto
- Отслеживание активности пользователей
- FSM для управления состояниями
- Поддержка SOCKS5 прокси
- Админ-панель для управления

## Структура проекта

```
├── config.py              # Конфигурация (токен, bot, dispatcher, proxy)
├── main.py                # Точка входа
├── handlers/
│   ├── handlers.py        # Общие обработчики (/start, echo)
│   ├── user_handlers.py  # Обработчики пользователей (контакты)
│   └── admin_handlers.py # Обработчики администраторов
├── services/
│   ├── database.py       # Модели и функции для работы с БД
│   ├── i18n.py          # Локализация
│   └── quickresto_api.py # Интеграция с QuickResto API
├── keyboards/
│   └── keyboards.py     # Клавиатуры
├── locales/
│   └── ru.ftl           # Переводы (Fluent)
├── doc/
│   └── Doc.md           # Документация
├── log/
│   └── log.log          # Логи
└── database.db          # SQLite база данных
```

## Конфигурация (.env)

```env
BOT_TOKEN=your_token_here
LAYER_NAME_QUICKRESTO=your_layer
USERNAME_QUICKRESTO=your_username
PASSWORD_QUICKRESTO=your_password
USER_PROXY=proxy_user
PASSWORD_PROXY=proxy_password
IP_PROXY=proxy_ip
PORT_PROXY=proxy_port
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

## Архитектура обработчиков

```
dp (Dispatcher)
├── handlers        # Общие (/start, echo)
├── user_handlers   # Пользователи (контакты)
└── admin_handlers  # Администраторы
```

## Запуск

```bash
pip install aiogram peewee python-dotenv loguru fluent-runtime
python main.py
```

## Логирование

- `log/log.log` — файл
- stdout — консоль

## Локализация

Fluent-формат в `locales/ru.ftl`.
