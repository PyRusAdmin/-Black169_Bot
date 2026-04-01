# 📚 Документация системы уровней клиентов QuickResto Bot

## Содержание

1. [Обзор системы](#обзор-системы)
2. [Уровни клиентов](#уровни-клиентов)
3. [Установка и настройка](#установка-и-настройка)
4. [Миграция данных](#миграция-данных)
5. [Использование](#использование)
6. [API и функции](#api-и-функции)
7. [Структура базы данных](#структура-базы-данных)
8. [Примеры кода](#примеры-кода)
9. [Устранение проблем](#устранение-проблем)

---

## Обзор системы

Система уровней клиентов интегрирована с Telegram-ботом QuickResto и позволяет:

- ✅ Автоматически определять уровень клиента на основе накопительной суммы
- ✅ Синхронизировать данные с QuickResto API
- ✅ Отображать уровень и прогресс в личном кабинете пользователя
- ✅ Получать детальную статистику по уровням в админ-панели
- ✅ Нормализовать телефонные номера к единому формату

**Архитектура системы:**

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  QuickResto API │ ──▶ │  Telegram Bot    │ ──▶ │  SQLite Database│
│  (клиенты)      │     │  (анализ)        │     │  (уровни)       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  JSON File       │
                        │  (кэширование)   │
                        └──────────────────┘
```

---

## Уровни клиентов

Система использует 4 уровня, основанных на **накопительной сумме** (accumulationBalance) из QuickResto:

| Иконка | Уровень    | Мин. сумма (₽) | Описание                                             |
|--------|------------|----------------|------------------------------------------------------|
| 💎     | **Black**  | от 60 000      | Привилегированный уровень, максимальные преимущества |
| 🥇     | **Gold**   | от 30 000      | Золотой уровень, повышенные бонусы                   |
| 🥈     | **Silver** | от 10 000      | Серебряный уровень, стандартные бонусы               |
| 🥉     | **Bronze** | от 0           | Базовый уровень, начальные преимущества              |

### Алгоритм определения уровня

```python
LEVELS = [
    {"name": "Black", "min_amount": 60000},
    {"name": "Gold", "min_amount": 30000},
    {"name": "Silver", "min_amount": 10000},
    {"name": "Bronze", "min_amount": 0},
]


def get_level(accumulation: float) -> str:
    for level in LEVELS:
        if accumulation >= level["min_amount"]:
            return level["name"]
    return "Bronze"
```

---

## Установка и настройка

### Требования

- Python 3.9+
- SQLite (встроен в Python)
- Библиотеки из `requirements.txt`

### Настройка

1. **Убедитесь, что все зависимости установлены:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Проверьте наличие файла `.env`:**
   ```env
   BOT_TOKEN=your_bot_token
   OWNER_ID=your_admin_id
   LAYER_NAME_QUICKRESTO=your_layer
   USERNAME_QUICKRESTO=your_username
   PASSWORD_QUICKRESTO=your_password
   ```

3. **Запустите миграцию данных:**
   ```bash
   python migrate_clients_to_db.py
   ```

---

## Миграция данных

### Скрипт миграции

**Файл:** `migrate_clients_to_db.py`

**Назначение:** Перенос данных о клиентах из `data/clients_levels.json` в базу данных SQLite.

**Использование:**

```bash
python migrate_clients_to_db.py
```

**Что делает:**

1. Загружает данные из JSON файла
2. Нормализует телефонные номера (формат: `79999999999`)
3. Ищет пользователей в БД по телефону или ID QuickResto
4. Обновляет поля `client_level` и `accumulation_amount`

**Пример вывода:**

```
🚀 Запуск миграции данных из clients_levels.json в БД...
📁 Загружено клиентов из JSON: 7389

============================================================
📊 ОТЧЕТ О МИГРАЦИИ ДАННЫХ
============================================================
📁 Всего клиентов в JSON: 7389
✅ Обновлено в БД: 4
❌ Не найдено в БД: 7385
⚠️  Ошибок: 0
============================================================
📈 Процент успешных: 0.1%
============================================================

✅ Миграция успешно завершена!
```

> **Важно:** В БД обновляются только те клиенты, которые зарегистрированы в боте (отправили номер телефона через
`/start`).

---

## Использование

### Для администратора

#### 1. Просмотр статистики

В админ-панели нажмите **"📊 Статистика пользователей"**.

**Отображаемая информация:**

- Количество пользователей, запустивших бота
- Количество зарегистрированных пользователей
- Уровни клиентов (в боте)
- Уровни всех клиентов QuickResto
- Статистика по рассылкам

**Пример:**

```
📊 Статистика пользователей

👥 Пользователей запустили бота: 6
✅ Зарегистрировали номер: 4

📈 Уровни клиентов (в боте):
💎 Black: 0 чел. (0.0%)
🥇 Gold: 0 чел. (0.0%)
🥈 Silver: 0 чел. (0.0%)
🥉 Bronze: 4 чел. (100.0%)
📭 Без уровня: 0 чел.

🏪 Вся база QuickResto (7389 клиентов):
💎 Black: 185 чел. (2.5%)
🥇 Gold: 237 чел. (3.2%)
🥈 Silver: 838 чел. (11.3%)
🥉 Bronze: 6129 чел. (83.0%)

📨 Рассылки:
Всего сообщений: 14
• Текстом: 11
• С фото: 3
• С видео: 0
📖 Прочитано: 5
🚫 Заблокировано: 0
```

#### 2. Синхронизация с QuickResto

В админ-панели нажмите **"🔄 Анализ и синхронизация клиентов"**.

**Процесс:**

1. Загрузка всех клиентов из QuickResto API
2. Нормализация телефонных номеров
3. Определение уровней по накопительной сумме
4. Сохранение в `data/clients_levels.json`
5. Синхронизация с базой данных

**Результат:**

```
✅ Анализ и синхронизация клиентов завершены!

📊 Результаты:
• Всего клиентов: 7389
• JSON обновлен: ✅

📈 Распределение по уровням:
💎 Black: 185 чел.
🥇 Gold: 237 чел.
🥈 Silver: 838 чел.
🥉 Bronze: 6129 чел.

🔄 Синхронизация с БД:
• Обновлено: 4
• Не найдено: 7385
• Ошибок: 0

🕒 Время выполнения: 2026-04-02T00:00:33
```

### Для пользователя

#### Просмотр уровня и бонусов

В главном меню нажмите **"💰 Мои бонусы"**.

**Отображаемая информация:**

- Текущий баланс бонусов
- Текущий уровень с описанием
- Прогресс до следующего уровня

**Пример:**

```
💰 Ваши бонусы: 1500

🥇 Gold — золотой уровень (от 30 000 ₽)
📈 До уровня Black осталось 30000 ₽

Используйте их при следующем посещении!
```

---

## API и функции

### Основные модули

#### `utils/phone_utils.py`

Утилиты для работы с телефонными номерами.

**Функции:**

```python
def normalize_phone_number(phone: str) -> str:
    """
    Нормализация номера телефона к формату 79999999999.
    
    :param phone: Исходный номер
    :return: Нормализованный номер
    
    Примеры:
    '+7 924 111-14-44' → '79241111444'
    '89241111444' → '79241111444'
    '—' → ''
    """


def format_phone_display(phone: str) -> str:
    """
    Форматирование для отображения: +7 (999) 123-45-67.
    
    :param phone: Нормализованный номер
    :return: Отформатированный номер
    """


def is_valid_phone(phone: str) -> bool:
    """
    Проверка валидности номера.
    
    :param phone: Номер для проверки
    :return: True если номер валидный
    """
```

#### `services/client_levels.py`

Сервис управления уровнями клиентов.

**Функции:**

```python
def get_level(accumulation: float) -> str:
    """Определение уровня по накопительной сумме."""


def get_level_description(level: str) -> str:
    """Получение описания уровня с эмодзи."""


def get_next_level_info(current_level: str, current_accumulation: float) -> dict:
    """
    Информация о следующем уровне.
    
    :return: {
        "has_next": bool,
        "next_level": str,
        "amount_needed": float,
        "message": str
    }
    """


def save_clients_to_json(clients_data: list, filepath: str) -> bool:
    """Сохранение данных о клиентах в JSON."""


def load_clients_from_json(filepath: str) -> list:
    """Загрузка данных о клиентах из JSON."""


def normalize_clients_phone_numbers(clients_data: list) -> list:
    """Нормализация телефонов в данных о клиентах."""


def sync_clients_with_database(clients_data: list) -> dict:
    """
    Синхронизация данных с БД.
    
    :return: {
        "total": int,
        "updated": int,
        "not_found": int,
        "errors": int
    }
    """


def analyze_and_save_clients(clients_from_api: list) -> dict:
    """
    Полный цикл анализа и сохранения.
    
    :return: {
        "total_clients": int,
        "json_saved": bool,
        "db_sync_stats": dict,
        "level_distribution": dict,
        "timestamp": str
    }
    """
```

#### `services/database.py`

Работа с базой данных.

**Функции:**

```python
def get_client_levels_stats() -> dict:
    """
    Статистика по уровням клиентов в БД.
    
    :return: {
        "total": int,
        "levels": {
            "Black": {"count": int, "percent": float},
            "Gold": {"count": int, "percent": float},
            "Silver": {"count": int, "percent": float},
            "Bronze": {"count": int, "percent": float}
        },
        "no_level": int
    }
    """


def update_client_level(id_telegram: int, client_level: str,
                        accumulation_amount: float = None) -> bool:
    """
    Обновление уровня клиента в БД.
    
    :param id_telegram: ID пользователя в Telegram
    :param client_level: Уровень (Black/Gold/Silver/Bronze)
    :param accumulation_amount: Накопительная сумма
    :return: True если успешно
    """
```

#### `services/quickresto_api.py`

Интеграция с QuickResto API.

**Функции:**

```python
def analyze_clients() -> list:
    """
    Анализ всех клиентов QuickResto.
    
    :return: Список клиентов с уровнями
    """


def analyze_and_sync_clients() -> dict:
    """
    Полный цикл анализа и синхронизации.
    
    :return: Статистика обработки
    """
```

---

## Структура базы данных

### Таблица `registered_persons`

| Поле                      | Тип         | Описание                                 |
|---------------------------|-------------|------------------------------------------|
| `id_telegram`             | INTEGER     | ID пользователя в Telegram (PRIMARY KEY) |
| `id_quickresto`           | INTEGER     | ID пользователя в QuickResto             |
| `phone_telegram`          | TEXT        | Нормализованный номер телефона           |
| `last_name`               | TEXT        | Фамилия                                  |
| `first_name`              | TEXT        | Имя                                      |
| `patronymic_name`         | TEXT        | Отчество                                 |
| `birthday_user`           | TEXT        | Дата рождения                            |
| `user_bonus`              | TEXT        | Бонусы                                   |
| `date_of_visit`           | DATETIME    | Дата последнего посещения                |
| `updated_at`              | DATETIME    | Дата обновления                          |
| `bonus_accrued_at`        | DATETIME    | Дата начисления бонусов ботом            |
| `bot_bonus_amount`        | DECIMAL     | Сумма бонусов от бота                    |
| **`client_level`**        | **TEXT**    | **Уровень клиента**                      |
| **`accumulation_amount`** | **DECIMAL** | **Накопительная сумма**                  |

### SQL-запросы для миграции

```sql
-- Добавление новых полей (если миграция не сработала)
ALTER TABLE registered_persons ADD COLUMN client_level TEXT;
ALTER TABLE registered_persons ADD COLUMN accumulation_amount REAL;

-- Просмотр статистики по уровням
SELECT 
    client_level,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM registered_persons), 2) as percent
FROM registered_persons
WHERE client_level IS NOT NULL
GROUP BY client_level;

-- Поиск пользователя по телефону
SELECT * FROM registered_persons 
WHERE phone_telegram = '79241111444';
```

---

## Примеры кода

### Пример 1: Проверка уровня пользователя

```python
from services.client_levels import get_level, get_level_description

accumulation = 75000  # Накопительная сумма
level = get_level(accumulation)  # "Black"
description = get_level_description(level)  # "💎 Black — привилегированный уровень"

print(f"Уровень: {level}")
print(f"Описание: {description}")
```

### Пример 2: Информация о следующем уровне

```python
from services.client_levels import get_next_level_info

info = get_next_level_info("Gold", 35000)

if info["has_next"]:
    print(f"Следующий уровень: {info['next_level']}")
    print(f"Нужно накопить: {info['amount_needed']} ₽")
    print(f"Сообщение: {info['message']}")
else:
    print("🏆 Вы достигли максимального уровня!")
```

### Пример 3: Статистика по уровням из БД

```python
from services.database import get_client_levels_stats

stats = get_client_levels_stats()

print(f"Всего зарегистрировано: {stats['total']}")
print("\nРаспределение по уровням:")

for level, data in stats['levels'].items():
    emoji = {"Black": "💎", "Gold": "🥇", "Silver": "🥈", "Bronze": "🥉"}[level]
    print(f"{emoji} {level}: {data['count']} чел. ({data['percent']}%)")

print(f"Без уровня: {stats['no_level']} чел.")
```

### Пример 4: Статистика из QuickResto JSON

```python
import json

with open("data/clients_levels.json", "r", encoding="utf-8") as f:
    clients = json.load(f)

total = len(clients)
levels = {}

for client in clients:
    level = client.get("level", "Unknown")
    levels[level] = levels.get(level, 0) + 1

print(f"Всего клиентов QuickResto: {total}")
print("\nРаспределение:")

for level in ["Black", "Gold", "Silver", "Bronze"]:
    count = levels.get(level, 0)
    percent = round(count / total * 100, 1)
    print(f"  {level}: {count} чел. ({percent}%)")
```

### Пример 5: Обновление уровня пользователя

```python
from services.database import update_client_level

id_telegram = 123456789
new_level = "Gold"
new_accumulation = 45000.0

success = update_client_level(id_telegram, new_level, new_accumulation)

if success:
    print(f"✅ Уровень пользователя {id_telegram} обновлён на {new_level}")
else:
    print(f"❌ Не удалось обновить уровень")
```

---

## Устранение проблем

### Проблема 1: Миграция не обновляет клиентов

**Симптомы:**

```
✅ Обновлено в БД: 0
❌ Не найдено в БД: 7389
```

**Причина:** В базе данных нет зарегистрированных пользователей.

**Решение:**

1. Проверьте количество зарегистрированных пользователей:
   ```python
   from services.database import get_registered_persons_count
   print(get_registered_persons_count())
   ```
2. Если 0 — пользователи ещё не регистрировались в боте
3. Попросите пользователей отправить номер телефона через `/start`

### Проблема 2: Ошибка при чтении JSON

**Симптомы:**

```
FileNotFoundError: [Errno 2] No such file or directory: 'data/clients_levels.json'
```

**Причина:** Файл `clients_levels.json` отсутствует.

**Решение:**

1. Запустите синхронизацию через админ-панель
2. Или выполните скрипт напрямую:
   ```bash
   python services/quickresto_api.py
   ```

### Проблема 3: Не отображается уровень пользователя

**Симптомы:** Пользователь видит только бонусы, без уровня.

**Причина:** Поля `client_level` и `accumulation_amount` не заполнены.

**Решение:**

1. Запустите миграцию:
   ```bash
   python migrate_clients_to_db.py
   ```
2. Или синхронизируйте через админ-панель

### Проблема 4: Ошибка импорта модулей

**Симптомы:**

```
ModuleNotFoundError: No module named 'utils'
```

**Причина:** Отсутствуют файлы `__init__.py`.

**Решение:**

```bash
# Создайте файлы __init__.py
touch utils/__init__.py
touch services/__init__.py
```

### Проблема 5: Неверный формат телефона

**Симптомы:** Телефоны не нормализуются, клиенты не находятся.

**Причина:** В JSON телефоны в разных форматах.

**Решение:**
Функция `normalize_phone_number()` автоматически обрабатывает форматы:

- `+7 924 111-14-44` ✓
- `89241111444` ✓
- `+79241111444` ✓
- `8 924 111 14 44` ✓
- `9841466936` → останется как есть (не российский формат)

---

## Приложения

### A. Структура проекта

```
Quickresto_Telegram_bot/
├── data/
│   ├── clients_levels.json      # Данные о клиентах
│   └── database.db              # SQLite база данных
├── doc/
│   ├── Doc.md                   # Эта документация
│   ├── MIGRATION_GUIDE.md       # Руководство по миграции
│   └── client_levels_system.md  # Описание системы уровней
├── handlers/
│   ├── admin_handlers.py        # Админ-панель
│   └── menu_handlers.py         # Пользовательское меню
├── services/
│   ├── client_levels.py         # Сервис уровней
│   ├── database.py              # Работа с БД
│   └── quickresto_api.py        # QuickResto API
├── utils/
│   ├── phone_utils.py           # Утилиты телефонов
│   └── logger.py                # Логирование
├── keyboards/
│   └── inline.py                # Клавиатуры
├── migrate_clients_to_db.py     # Скрипт миграции
└── tests/
    └── test_client_levels.py    # Тесты
```

### B. Команды для администратора

| Команда                              | Описание                        |
|--------------------------------------|---------------------------------|
| `/start`                             | Запуск бота                     |
| `/cancel`                            | Отмена текущей операции         |
| `📊 Статистика пользователей`        | Просмотр полной статистики      |
| `🔄 Анализ и синхронизация клиентов` | Обновление данных из QuickResto |

### C. Полезные SQL-запросы

```sql
-- Все пользователи с уровнями
SELECT 
    id_telegram,
    first_name,
    phone_telegram,
    client_level,
    accumulation_amount
FROM registered_persons
WHERE client_level IS NOT NULL
ORDER BY accumulation_amount DESC;

-- Топ-10 клиентов по накопительной сумме
SELECT 
    first_name,
    phone_telegram,
    client_level,
    accumulation_amount
FROM registered_persons
ORDER BY accumulation_amount DESC
LIMIT 10;

-- Количество пользователей по уровням
SELECT 
    COALESCE(client_level, 'Без уровня') as level,
    COUNT(*) as count
FROM registered_persons
GROUP BY client_level;

-- Поиск по телефону
SELECT * FROM registered_persons 
WHERE phone_telegram LIKE '%79241111444%';
```

---

## Контакты и поддержка

При возникновении проблем:

1. Проверьте логи бота
2. Убедитесь, что все зависимости установлены
3. Проверьте подключение к QuickResto API
4. Убедитесь, что файл `.env` настроен корректно

**Версия документации:** 1.0  
**Дата обновления:** 2 апреля 2026 г.
