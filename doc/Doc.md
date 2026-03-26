# The Black 169 — Telegram Bot

Телеграм-бот для кальянной The Black 169. Позволяет гостям регистрироваться, отслеживать бонусы, участвовать в акциях и
получать подарки. Интегрирован с системой лояльности QuickResto через API.

## Возможности

### Для пользователей:

- Регистрация пользователей по номеру телефона
- Приветственные бонусы (1000 ₽)
- Автоматическое создание клиентов в QuickResto
- Интеграция с QuickResto API (поиск, создание клиентов, получение бонусов)
- Главное меню с inline-кнопками
- Просмотр бонусов, акций, мероприятий
- Получение подарков (промокоды)
- 🎡 Колесо подарков (ежедневный розыгрыш, шанс 5%)
- Акция «Вернуться сегодня»
- Отслеживание сгорания бонусов (7, 3, 1 день)
- Поздравления с днём рождения (1500 бонусов)
- FSM для управления состояниями

### Для администраторов:

- Админ-панель для управления
- 📊 Статистика пользователей
- 📨 Рассылка сообщений (текст, фото, видео)
- 👥 Выгрузка пользователей в Excel
- 🏆 Выгрузка победителей «Колеса подарков» в Excel

## Структура проекта

```
├── config.py              # Конфигурация (токен, bot, dispatcher, proxy, QuickResto)
├── main.py                # Точка входа
├── handlers/
│   ├── handlers.py        # Общие обработчики (/start, echo)
│   ├── user_handlers.py   # Обработчики пользователей (контакты, регистрация)
│   ├── menu_handlers.py   # Обработчики главного меню (callbacks)
│   └── admin_handlers.py  # Обработчики администраторов
├── services/
│   ├── database.py        # Модели и функции для работы с БД
│   ├── i18n.py            # Локализация (Fluent)
│   ├── quickresto_api.py  # Интеграция с QuickResto API
│   ├── bonus.py           # Генерация случайных бонусов
│   └── excel_service.py   # Экспорт данных в Excel
├── keyboards/
│   ├── keyboards.py       # Reply-клавиатуры (кнопка отправки контакта)
│   └── inline.py          # Inline-клавиатуры (меню, админ-панель)
├── filters/
│   └── admin_filter.py    # Фильтр администратора
├── states/
│   ├── order_states.py    # FSM-состояния для заказов
│   └── user_states.py     # FSM-состояния для пользователей (рассылка)
├── utils/                 # Утилиты
├── locales/
│   └── ru.ftl             # Переводы (Fluent)
├── doc/
│   ├── Doc.md             # Документация
│   └── Тз.md              # Техническое задание
├── log/
│   └── log.log            # Логи
├── .env.example           # Шаблон .env
├── .gitignore             # Игнорируемые файлы
├── ToDo.md                # Список задач (не коммитить)
├── requirements.txt       # Зависимости Python
└── database.db            # SQLite база данных
```

## Конфигурация (.env)

```env
# Токен бота (получить у @BotFather)
BOT_TOKEN=your_token_here

# ID владельца бота (ваш Telegram ID)
OWNER_ID=123456789

# QuickResto API
LAYER_NAME_QUICKRESTO=your_layer
USERNAME_QUICKRESTO=your_username
PASSWORD_QUICKRESTO=your_password

# Прокси (SOCKS5)
USER_PROXY=proxy_user
PASSWORD_PROXY=proxy_password
IP_PROXY=127.0.0.1
PORT_PROXY=1080
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
| id_quickresto   | INTEGER  | ID клиента в QuickResto    |
| phone_telegram  | TEXT     | Номер телефона             |
| last_name       | TEXT     | Фамилия (QuickResto)       |
| first_name      | TEXT     | Имя (QuickResto)           |
| patronymic_name | TEXT     | Отчество (QuickResto)      |
| birthday_user   | TEXT     | Дата рождения              |
| user_bonus      | TEXT     | Бонусы                     |
| date_of_visit   | DATETIME | Последнее посещение        |
| updated_at      | DATETIME | Дата обновления            |

### Таблица `gift_wheel_spins`

История розыгрышей «Колеса подарков».

| Поле          | Тип      | Описание                    |
|---------------|----------|-----------------------------|
| id_telegram   | INTEGER  | ID пользователя в Telegram  |
| id_quickresto | INTEGER  | ID клиента в QuickResto     |
| bonus_name    | TEXT     | Название выигранного бонуса |
| is_winner     | BOOLEAN  | True если победитель        |
| spun_at       | DATETIME | Дата и время розыгрыша      |

### Таблица `marketing_messages`

Логирование маркетинговых рассылок.

| Поле         | Тип      | Описание                            |
|--------------|----------|-------------------------------------|
| id_telegram  | INTEGER  | ID пользователя в Telegram          |
| message_text | TEXT     | Текст сообщения                     |
| message_type | TEXT     | Тип: text, photo, video, blocked    |
| sent_at      | DATETIME | Дата отправки                       |
| is_blocked   | BOOLEAN  | True если пользователь заблокировал |
| is_read      | BOOLEAN  | True если прочитал                  |

## Архитектура обработчиков

```
dp (Dispatcher)
├── handlers        # Общие (/start, echo)
├── user_handlers   # Пользователи (контакты, регистрация)
├── menu_handlers   # Главное меню (callbacks)
└── admin_handlers  # Администраторы
```

### Обработчики меню (пользователь)

| Callback                     | Описание            |
|------------------------------|---------------------|
| `my_bonuses`                 | Мои бонусы          |
| `pick_up_gift`               | Забрать подарок     |
| `bonuses_will_soon_burn_out` | Бонусы скоро сгорят |
| `gift_wheel`                 | Колесо подарков     |
| `twist`                      | Крутить колесо      |
| `promotions`                 | Акции               |
| `events`                     | Мероприятия         |
| `back_today`                 | Вернуться сегодня   |
| `contacts`                   | Контакты            |
| `about_institution`          | О заведении         |
| `back_to_main_menu`          | В главное меню      |

### Обработчики админ-панели

| Callback                 | Описание                     |
|--------------------------|------------------------------|
| `winners`                | Список победителей (Excel)   |
| `users`                  | Список пользователей (Excel) |
| `broadcast`              | Рассылка сообщений           |
| `broadcast_text`         | Рассылка текстом             |
| `broadcast_photo`        | Рассылка фото                |
| `broadcast_video`        | Рассылка видео               |
| `broadcast_confirm_send` | Подтверждение рассылки       |
| `broadcast_cancel`       | Отмена рассылки              |
| `stats`                  | Статистика пользователей     |
| `admin_back`             | В меню администратора        |

## QuickResto API

### Функции (`services/quickresto_api.py`)

| Функция                    | Описание                             |
|----------------------------|--------------------------------------|
| `get_customer_by_phone()`  | Поиск клиента по номеру телефона     |
| `print_client_info()`      | Получение информации о клиенте       |
| `create_client()`          | Создание нового клиента в QuickResto |
| `get_full_client_info()`   | Полная информация по ID клиента      |
| `print_full_client_info()` | Вывод полной информации о клиенте    |

## Клавиатуры

### Reply-клавиатуры (`keyboards/keyboards.py`)

- `contact_keyboard()` — кнопка отправки номера телефона

### Inline-клавиатуры (`keyboards/inline.py`)

#### Пользовательские:

- `main_menu_keyboard()` — главное меню после авторизации
- `back_to_main_menu_keyboard()` — возврат в главное меню
- `twist_keyboard()` — колесо подарков (крутить + возврат)

#### Администраторские:

- `admin_menu_keyboard()` — меню администратора
- `back_to_admin_menu_keyboard()` — возврат в меню администратора
- `broadcast_type_keyboard()` — выбор типа рассылки
- `broadcast_confirm_keyboard()` — подтверждение рассылки

## Запуск

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Запуск бота

```bash
python main.py
```

### Требования (`requirements.txt`)

```
aiogram>=3.0.0
peewee>=3.17.0
python-dotenv>=1.0.0
loguru>=0.7.0
fluent-runtime>=0.3.0
requests>=2.31.0
openpyxl>=3.1.0
rich>=13.0.0
```

## Логирование

- `log/log.log` — файл
- stdout — консоль

Используется библиотека `loguru`. Уровни: INFO, SUCCESS, WARNING, ERROR.

## Локализация

Fluent-формат в `locales/ru.ftl`.

Пример использования в коде:

```python
from services.i18n import t

text = t("greet-message")  # Получение строки по ключу
```

## Админ-панель

### Статистика пользователей

- Количество пользователей, запустивших бота (`start_persons`)
- Количество привязавших номер телефона (`registered_persons`)
- Статистика по рассылкам (всего, текстовых, с фото, с видео)
- Количество заблокировавших бота

### Рассылка сообщений

1. Выбор типа сообщения (текст / фото / видео)
2. Отправка контента боту
3. Подтверждение рассылки
4. Отправка всем пользователям из `start_persons`
5. Статистика: отправлено / заблокировано / не доставлено
6. Логирование в `marketing_messages`

### Выгрузка данных

- **Пользователи** — Excel-файл со всеми пользователями (ID, имя, фамилия, username, дата)
- **Победители** — Excel-файл с победителями «Колеса подарков» (ID, приз, дата)

## FSM состояния

### BroadcastState (рассылка)

- `waiting_for_message_type` — ожидание выбора типа сообщения
- `waiting_for_message_text` — ожидание текста
- `waiting_for_photo` — ожидание фото
- `waiting_for_video` — ожидание видео
- `waiting_for_confirmation` — ожидание подтверждения

## Команды бота

| Команда   | Описание        |
|-----------|-----------------|
| `/start`  | Запуск бота     |
| `/cancel` | Отмена рассылки |

## Нагрузка

Бот рассчитан на:

- 7000+ пользователей
- Массовые рассылки
- Высокую активность клиентов

## Безопасность

- Проверка прав администратора по `OWNER_ID`
- SOCKS5 прокси для обхода блокировок
- Файлы Excel формируются в памяти (не сохраняются на диск)
