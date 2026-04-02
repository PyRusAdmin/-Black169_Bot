import json

import requests
from requests.auth import HTTPBasicAuth
from collections import Counter
from config import (
    console,
    layer_name_quickresto,
    password_quickresto,
    username_quickresto,
)
from utils.logger import logger
import time

base_url = f"https://{layer_name_quickresto}.quickresto.ru/platform/online/api"
auth = HTTPBasicAuth(username_quickresto, password_quickresto)
headers = {"Content-Type": "application/json"}

# https://quickresto.ru/api/

"""Ищет клиента по номеру телефона в QuickResto"""


def get_customer_by_phone(layer_name_quickresto, phone_number, auth, headers):
    """
    Возвращает информацию о клиенте по номеру телефона

    :param layer_name_quickresto: название слоя QuickResto
    :param phone_number: номер телефона
    :param auth: авторизация в QuickResto
    :param headers: заголовки запроса
    :return: информация о клиенте
    """
    url = f"https://{layer_name_quickresto}.quickresto.ru/platform/online/bonuses/filterCustomers"

    payload = {
        "search": phone_number,
        "typeList": ["customer"],
        "limit": 10,
        "offset": 0,
    }
    response = requests.post(url, json=payload, auth=auth, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def print_client_info(layer_name_quickresto, phone_number, auth, headers):
    """Выводит информацию о клиенте по номеру телефона в формате JSON из QuickResto"""
    try:
        result = get_customer_by_phone(
            layer_name_quickresto, phone_number, auth, headers
        )

        if result:
            console.print_json(json.dumps(result, indent=2, ensure_ascii=False))

        # Достаём список клиентов
        customers = result.get("customers", [])

        if customers:
            customer = customers[0]  # Выбираем первого клиента в списке клиентов
            # Личные данные
            client_id = customer.get("id")
            name = customer.get("firstName", "—")
            surname = customer.get("lastName", "—")
            guid = customer.get("customerGuid", "—")

            # Телефон — вложенный список
            contacts = customer.get("contactMethods", [])
            phone = contacts[0].get("value") if contacts else "—"

            console.log(f"ID:      {client_id}")
            console.log(f"Имя:     {name} {surname}")
            console.log(f"Телефон: {phone}")
            console.log(f"GUID:    {guid}")

            data = {
                "client_id": client_id,
                "firstName": name,
                "lastName": surname,
                "phone": phone,
                "guid": guid,
            }

            return data

        else:
            logger.warning("Клиент не найден")
            return None
    except Exception as e:
        logger.exception(f"Ошибка: {e}")


"""Создает клиента в QuickResto"""


def create_client(name_customer, phone_customer, base_url, auth, headers):
    """Создание нового клиента в QuickResto"""
    try:
        url = f"{base_url}/create"

        query_params = {
            "moduleName": "crm.customer",
            "className": "ru.edgex.quickresto.modules.crm.customer.CrmCustomer",
        }

        body = {
            "firstName": name_customer,
            "contactMethods": [{"type": "phoneNumber", "value": phone_customer}],
        }

        response = requests.post(
            url, params=query_params, json=body, auth=auth, headers=headers, timeout=30
        )
        response.raise_for_status()
        result = response.json()

        # Возвращаем данные созданного клиента
        client_data = {
            "id": result.get("id"),
            "firstName": name_customer,
            "phone": phone_customer,
        }

        logger.info(
            f"Клиент создан: id={client_data['id']}, имя={name_customer}, телефон={phone_customer}"
        )
        return client_data

    except Exception as e:
        logger.exception(e)
        return None


"""Получаем информацию о клиенте по ID в QuickResto"""


def get_full_client_info(client_id, base_url, auth, headers):
    """
    Возвращает полную информацию об одном конкретном пользователе (клиенте)

    :param client_id: ID клиента
    :param base_url: базовый URL
    :param auth: аутентификация
    :param headers: заголовки
    :return: полную информацию об одном конкретном пользователе (клиенте)
    """
    url = f"{base_url}/read"

    query_params = {
        "moduleName": "crm.customer",
        "className": "ru.edgex.quickresto.modules.crm.customer.CrmCustomer",
        "objectId": client_id,  # ← objectId идёт в params, не в body
    }

    try:
        response = requests.get(
            url, params=query_params, auth=auth, headers=headers, timeout=30
        )
        response.raise_for_status()
        return response.json()

    except Exception as e:
        logger.exception(f"❌ Ошибка при чтении клиента {client_id}: {e}")
        return None


def print_full_client_info(client_id):
    """Выводит полную информацию о клиенте по ID в QuickResto"""
    result = get_full_client_info(
        client_id=client_id, base_url=base_url, auth=auth, headers=headers
    )

    if not result:
        logger.error("Клиент не найден")
        return

    if result:
        console.print_json(json.dumps(result, indent=2, ensure_ascii=False))

    # Личные данные
    id_client = result.get("id")
    first_name = result.get("firstName", "—")
    middle_name = result.get("middleName", "—")
    last_name = result.get("lastName", "—")
    date_of_birth = result.get("dateOfBirth", "—")
    create_time = result.get("createTime", "—")

    # Телефон
    contacts = result.get("contactMethods", [])
    phone_number = contacts[0].get("value") if contacts else "—"

    # Бонусный счёт
    accounts = result.get("accounts", [])
    if accounts:
        account_balance = accounts[0].get("accountBalance", {})
        bonus_ledger = account_balance.get("ledger", 0)  # общий
        bonus_available = account_balance.get("available", 0)  # доступно
    else:
        bonus_ledger = bonus_available = 0

    # Накопительный баланс
    accumulation = result.get("accumulationBalance", {})
    accum_ledger = accumulation.get("ledger", 0)

    logger.info(f"ID:              {id_client}")
    logger.info(f"Имя:             {first_name} {middle_name} {last_name}")
    logger.info(f"Дата рождения:   {date_of_birth}")
    logger.info(f"Телефон:         {phone_number}")
    logger.info(f"Создан:          {create_time}")
    logger.info(f"Бонусы (всего):  {bonus_ledger}")
    logger.info(f"Бонусы (доступно): {bonus_available}")
    logger.info(f"Накопительный:   {accum_ledger}")

    data = {
        "id": id_client,
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "date_of_birth": date_of_birth,
        "phone_number": phone_number,
        "create_time": create_time,
        "bonus_ledger": bonus_ledger,
        "bonus_available": bonus_available,
        "accum_ledger": accum_ledger,
    }
    return data


"""Назначение клиенту бонусов в QuickResto"""


def update_customer_bonus(customer_id: int, amount: float, customer_phone: str):
    """
    Редактирование бонусных балов для клиента. Для изменения бонусных балов, требуется ID клиента в QuickResto и номер
    телефона клиента, который в базе данных QuickResto. Для получения ID клиента и номера телефона клиента,
    требуется можно использовать метод get_customer_by_phone.

    :param customer_id: идентификатор клиента в QuickResto
    :param amount: количество бонусных балов для клиента в QuickResto
    :param customer_phone: номер телефона клиента в QuickResto
    :return: результат выполнения запроса в формате JSON
    """
    try:
        logger.info(f"Редактирование бонусных балов для клиента {customer_id}")
        url = f"https://{layer_name_quickresto}.quickresto.ru/platform/online/bonuses/creditHold"
        body = {
            "customerToken": {
                "type": "phone",  # ← тип токена: телефон
                "entry": "manual",  # ← способ ввода: вручную
                "key": customer_phone,  # ← сам номер телефона
            },
            "accountType": {
                "accountGuid": "bonus_account_type-1"
            },  # ← из данных клиента
            "amount": amount,
        }
        response = requests.post(url, json=body, auth=auth, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        logger.exception(e)


"""Удаление клиента из QuickResto"""


def delete_customer(customer_id: int, base_url, auth, headers):
    """
    Удаление клиента по ID

    :param customer_id: ID клиента
    :param base_url: базовый URL
    :param auth: аутентификация
    :param headers: заголовки
    """
    try:
        logger.info(f"Удаление клиента {customer_id}")

        url = f"{base_url}/remove"

        query_params = {
            "moduleName": "crm.customer",
            "className": "ru.edgex.quickresto.modules.crm.customer.CrmCustomer",
        }

        body = {"id": customer_id}  # ← id в теле, не в params

        response = requests.post(  # ← POST, не DELETE
            url, params=query_params, json=body, auth=auth, headers=headers, timeout=30
        )
        response.raise_for_status()
        return response.json()

    except Exception as e:
        logger.exception(e)


"""Определение клиентов по уровню бонусов в QuickResto"""

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


BASE_URL = f"https://{layer_name_quickresto}.quickresto.ru/platform/online/api"


def get_all_clients_full() -> list:
    """Загружает полные данные всех клиентов через /api/read"""

    # Шаг 1 — получаем только ID через /api/list
    all_ids = []
    limit, offset = 500, 0

    logger.info("Загружаю список ID клиентов...")
    while True:
        response = requests.get(
            f"{BASE_URL}/list",
            params={
                "moduleName": "crm.customer",
                "className": "ru.edgex.quickresto.modules.crm.customer.CrmCustomer",
            },
            json={"limit": limit, "offset": offset},
            auth=auth,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        batch = response.json()
        if not batch:
            break
        all_ids.extend([c["id"] for c in batch if c.get("id")])
        offset += limit
        if len(batch) < limit:
            break

    logger.info(f"Найдено ID: {len(all_ids)}")

    # Шаг 2 — для каждого ID запрашиваем полные данные
    full_clients = []
    errors = 0

    for i, client_id in enumerate(all_ids):
        try:
            response = requests.get(
                f"{BASE_URL}/read",
                params={
                    "moduleName": "crm.customer",
                    "className": "ru.edgex.quickresto.modules.crm.customer.CrmCustomer",
                    "objectId": client_id,
                },
                auth=auth,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            full_clients.append(response.json())

            # Прогресс каждые 100 клиентов
            if (i + 1) % 100 == 0:
                logger.info(f"Обработано: {i + 1}/{len(all_ids)}")

            # Пауза чтобы не перегружать сервер
            time.sleep(0.1)

        except Exception as e:
            logger.warning(f"Ошибка для ID {client_id}: {e}")
            errors += 1
            continue

    logger.info(f"Готово. Загружено: {len(full_clients)}, ошибок: {errors}")
    return full_clients


def get_all_clients() -> list:
    all_clients = []
    limit = 500
    offset = 0

    logger.info("Начинаю загрузку клиентов...")

    while True:
        response = requests.get(
            f"{BASE_URL}/list",
            params={
                "moduleName": "crm.customer",
                "className": "ru.edgex.quickresto.modules.crm.customer.CrmCustomer",
            },
            json={"limit": limit, "offset": offset},
            auth=auth,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        batch = response.json()

        if not batch:
            break

        all_clients.extend(batch)
        logger.info(f"Загружено: {len(all_clients)}...")
        offset += limit

        if len(batch) < limit:
            break

    return all_clients


# ── Обработка ─────────────────────────────────────────────────────────────────


def analyze_clients():
    """
    Анализ всех клиентов QuickResto с определением уровней.

    :return: Список данных о клиентах с уровнями
    """
    clients = get_all_clients_full()
    logger.info(f"Всего клиентов: {len(clients)}")

    result = []

    for client in clients:
        # Личные данные
        client_id = client.get("id")
        first_name = client.get("firstName", "—")
        last_name = client.get("lastName", "—")

        # Телефон
        contacts = client.get("contactMethods", [])
        phone = contacts[0].get("value") if contacts else "—"

        # Накопительный баланс — основа для уровня
        accumulation = client.get("accumulationBalance", {})
        accum_amount = (
            accumulation.get("ledger", 0) if isinstance(accumulation, dict) else 0
        )

        # Бонусный счёт
        accounts = client.get("accounts", [])
        bonus = (
            accounts[0].get("accountBalance", {}).get("ledger", 0) if accounts else 0
        )

        # Уровень
        level = get_level(accum_amount)

        result.append(
            {
                "id": client_id,
                "name": f"{first_name} {last_name}".strip(),
                "phone": phone,
                "accumulation": accum_amount,
                "bonus": bonus,
                "level": level,
            }
        )

    # Сортируем по накопленной сумме — лучшие клиенты вверху
    result.sort(key=lambda x: x["accumulation"], reverse=True)

    logger.info(f"Проанализировано клиентов: {len(result)}")
    return result


def analyze_and_sync_clients():
    """
    Полный цикл анализа, нормализации, сохранения в JSON и синхронизации с БД.

    :return: Статистика обработки
    """
    from services.client_levels import (
        analyze_and_save_clients,
        normalize_clients_phone_numbers,
    )

    # Получаем данные из API
    clients_data = analyze_clients()

    # Нормализуем телефоны, сохраняем в JSON и синхронизируем с БД
    result = analyze_and_save_clients(clients_data)

    return result


# ── Вывод ─────────────────────────────────────────────────────────────────────


def print_report(data: list):
    print("\n" + "=" * 75)
    print(
        f"{'ID':<7} | {'Имя':<25} | {'Телефон':<15} | {'Накоп.':<10} | {'Бонусы':<8} | Уровень"
    )
    print("-" * 75)

    for c in data:
        print(
            f"{c['id']:<7} | "
            f"{c['name']:<25} | "
            f"{c['phone']:<15} | "
            f"{c['accumulation']:<10.1f} | "
            f"{c['bonus']:<8.1f} | "
            f"{c['level']}"
        )

    # Статистика по уровням
    level_counts = Counter(c["level"] for c in data)
    print("\n" + "=" * 75)
    print("📊 Распределение по уровням:")
    for level in ["Black", "Gold", "Silver", "Bronze"]:
        count = level_counts.get(level, 0)
        percent = count / len(data) * 100 if data else 0
        print(f"  {level:<8}: {count:>5} клиентов ({percent:.1f}%)")
    print("=" * 75)


if __name__ == "__main__":
    data = analyze_clients()
    print_report(data)

    # Сохраняем в JSON для дальнейшей работы
    with open("data/clients_levels.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info("Результат сохранён в data/clients_levels.json")

    # Синхронизируем с базой данных
    logger.info("Начинаю синхронизацию с базой данных...")
    sync_result = analyze_and_sync_clients()
    logger.info(f"Синхронизация завершена: {sync_result}")
