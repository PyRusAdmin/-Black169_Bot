# The Black 169 — Telegram Bot

Телеграм-бот для кальянной The Black 169. Позволяет гостям регистрироваться, отслеживать бонусы, участвовать в акциях и
получать подарки. Интегрирован с системой лояльности QuickResto через API.

## 🚀 Возможности

### Для пользователей:

- 📱 Регистрация по номеру телефона
- 💰 Просмотр бонусного баланса
- 🎁 Участие в акции «Колесо подарков» (1 раз в день)
- 🎉 Информация об акциях и мероприятиях
- 📍 Контакты заведения
- ℹ️ Информация о заведении

### Для администратора:

- 🔧 Админ-панель с inline-кнопками
- 🏆 Список победителей «Колеса подарков»
- 👥 Список пользователей
- 📨 Рассылка сообщений (в разработке)
- 📊 Статистика пользователей (в разработке)

## 📋 Структура проекта

```
├── config.py              # Конфигурация (токен, OWNER_ID, QuickResto, прокси)
├── main.py                # Точка входа
├── handlers/
│   ├── handlers.py        # Обработчик /start и возврат в меню
│   ├── user_handlers.py   # Обработчик контактов и регистрация
│   ├── menu_handlers.py   # Обработчики главного меню (callback query)
│   └── admin_handlers.py  # Админ-панель (callback query)
├── services/
│   ├── database.py        # Модели и функции для работы с БД
│   ├── i18n.py            # Локализация (Fluent)
│   ├── quickresto_api.py  # Интеграция с QuickResto API
│   └── bonus.py           # Сервис бонусов (random_bonus)
├── keyboards/
│   ├── keyboards.py       # Reply-клавиатуры (отправка контакта)
│   └── inline.py          # Inline-клавиатуры (меню, навигация)
├── filters/
│   └── admin_filter.py    # Фильтр администратора (заготовка)
├── states/
│   ├── user_states.py     # FSM состояния пользователя
│   └── order_states.py    # FSM состояния заказа
├── locales/
│   └── ru.ftl             # Переводы (Fluent)
├── log/
│   └── log.log            # Файл логов
├── .env.example           # Шаблон переменных окружения
├── .env                   # Переменные окружения (не в git)
├── requirements.txt       # Зависимости Python
└── database.db            # SQLite база данных
```

## ⚙️ Установка

### 1. Клонируйте репозиторий

```bash
git clone <repository-url>
cd Quickresto_Telegram_bot
```

### 2. Создайте виртуальное окружение

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Настройте переменные окружения

Скопируйте `.env.example` в `.env` и заполните своими данными:

```bash
cp .env.example .env
```

### 5. Настройте `.env`

```env
# Токен бота (получить у @BotFather)
BOT_TOKEN=your_bot_token_here

# ID владельца бота (ваш Telegram ID, узнать у @userinfobot)
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

## 🏃 Запуск

```bash
python main.py
```

## 🎮 Использование

### Обычный пользователь:

1. Отправьте `/start` боту
2. Нажмите «📱 Отправить номер телефона»
3. Подтвердите отправку контакта
4. Используйте меню с inline-кнопками:
    - 💰 Мои бонусы
    - 🎁 Забрать подарок
    - 🔥 Бонусы скоро сгорят
    - 🎡 Колесо подарков
    - 🎉 Акции
    - 📅 Мероприятия
    - 🔥 Вернуться сегодня
    - 📍 Контакты
    - ℹ️ О заведении

### Администратор:

1. Отправьте `/start` боту (с аккаунта OWNER_ID)
2. Автоматически откроется админ-панель
3. Используйте inline-кнопки:
    - Список победителей «Колеса подарков»
    - Список пользователей
    - Рассылка сообщений
    - Статистика пользователей

## 🗄️ База данных

### Таблицы:

#### `start_persons`

Пользователи, запустившие бота:

- `id_telegram` — ID в Telegram
- `last_name_telegram` — Фамилия
- `first_name_telegram` — Имя
- `username_telegram` — Username
- `updated_at` — Дата обновления

#### `registered_persons`

Зарегистрированные пользователи (с номером телефона):

- `id_telegram` — ID в Telegram
- `id_quickresto` — ID в QuickResto
- `phone_telegram` — Номер телефона
- `last_name` — Фамилия (QuickResto)
- `first_name` — Имя (QuickResto)
- `patronymic_name` — Отчество (QuickResto)
- `birthday_user` — Дата рождения
- `user_bonus` — Бонусный баланс
- `date_of_visit` — Дата последнего посещения
- `updated_at` — Дата обновления

#### `gift_wheel_spins`

История розыгрышей «Колесо подарков»:

- `id_telegram` — ID пользователя
- `id_quickresto` — ID в QuickResto
- `bonus_name` — Название бонуса
- `is_winner` — Победитель (True/False)
- `spun_at` — Дата розыгрыша

## 🔌 QuickResto API

Бот интегрирован с QuickResto API для:

- Поиска клиента по номеру телефона
- Создания нового клиента
- Получения информации о клиенте (баланс, имя, дата рождения)
- Синхронизации данных с базой

## 📝 Локализация

Проект использует Fluent для локализации. Файл переводов: `locales/ru.ftl`

Для добавления нового текста:

1. Добавьте ключ в `locales/ru.ftl`
2. Используйте функцию `t()` в коде:
   ```python
   from services.i18n import t
   await message.answer(text=t("your-key"))
   ```

## 🛠️ Разработка

### Добавление новой inline-кнопки:

1. Создайте клавиатуру в `keyboards/inline.py`:
   ```python
   def your_keyboard():
       return InlineKeyboardMarkup(
           inline_keyboard=[
               [InlineKeyboardButton(text="Кнопка", callback_data="your_callback")],
           ]
       )
   ```

2. Добавьте обработчик в `handlers/menu_handlers.py`:
   ```python
   @router.callback_query(F.data == "your_callback")
   async def your_handler(callback: CallbackQuery):
       await callback.message.answer(text="Ответ")
       await callback.answer()
   ```

### Добавление новой команды администратора:

1. Добавьте кнопку в `admin_menu_keyboard()`
2. Создайте обработчик в `admin_handlers.py`
3. Используйте `is_admin()` для проверки прав

## 📊 Статус проекта

Выполнено: **51%** (77 из 150 задач)

- ✅ Базовая настройка: 100%
- ✅ База данных: 85%
- ✅ Обработчики: 100%
- ✅ Клавиатуры: 100%
- ✅ Локализация: 100%
- 🔄 Админ-панель: 40%
- 🔄 Интеграция с QuickResto: 64%

## 📋 TODO

См. файл [ToDo.md](ToDo.md) для полного списка задач.

## 📄 Лицензия

Проект создан для внутреннего использования The Black 169.

## 📞 Контакты

- Telegram: [@your_bot](https://t.me/your_bot)
- Адрес: Океанский проспект 169
- Телефон: +7 (914) 791-19-11
