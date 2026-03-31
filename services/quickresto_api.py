# -*- coding: utf-8 -*-
import json

import requests
from requests.auth import HTTPBasicAuth

from config import console, layer_name_quickresto, password_quickresto, username_quickresto
from utils.logger import logger

base_url = f"https://{layer_name_quickresto}.quickresto.ru/platform/online/api"
auth = HTTPBasicAuth(username_quickresto, password_quickresto)
headers = {"Content-Type": "application/json"}

# https://quickresto.ru/api/

"""Ищет клиента по номеру телефона в QuickResto"""


def get_customer_by_phone(layer_name_quickresto, phone_number, auth, headers):
    """
    Возвращает информацию о клиенте по номеру телефона

    :param layer_name_quickresto: название слоя quickresto
    :param phone_number: номер телефона
    :param auth: авторизация в quickresto
    :param headers: заголовки запроса
    :return: информация о клиенте
    """
    url = f"https://{layer_name_quickresto}.quickresto.ru/platform/online/bonuses/filterCustomers"

    payload = {"search": phone_number, "typeList": ["customer"], "limit": 10, "offset": 0}
    response = requests.post(url, json=payload, auth=auth, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def print_client_info(layer_name_quickresto, phone_number, auth, headers):
    """Выводит информацию о клиенте по номеру телефона в формате JSON из QuickResto"""
    try:
        result = get_customer_by_phone(layer_name_quickresto, phone_number, auth, headers)

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

            data = {"client_id": client_id, "firstName": name, "lastName": surname, "phone": phone, "guid": guid}

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

        body = {"firstName": name_customer, "contactMethods": [{"type": "phoneNumber", "value": phone_customer}]}

        response = requests.post(url, params=query_params, json=body, auth=auth, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()

        # Возвращаем данные созданного клиента
        client_data = {"id": result.get("id"), "firstName": name_customer, "phone": phone_customer}

        logger.info(f"Клиент создан: id={client_data['id']}, имя={name_customer}, телефон={phone_customer}")
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
        response = requests.get(url, params=query_params, auth=auth, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        logger.exception(f"❌ Ошибка при чтении клиента {client_id}: {e}")
        return None


def print_full_client_info(client_id):
    """Выводит полную информацию о клиенте по ID в QuickResto"""
    result = get_full_client_info(client_id=client_id, base_url=base_url, auth=auth, headers=headers)

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


def update_customer_bonus(
    layer_name_quickresto: str, customer_id: int, amount: float, customer_phone: str, auth, headers
):
    """
    Редактирование бонусных балов для клиента. Для изменения бонусных балов, требуется ID клиента в QuickResto и номер
    телефона клиента, котрый в базе данных QuickResto. Для получения ID клиента и номера телефона клиента,
    требуется можно использовать метод get_customer_by_phone.

    :param layer_name_quickresto: название слоя QuickResto
    :param customer_id: идентификатор клиента в QuickResto
    :param amount: количество бонусных балов для клиента в QuickResto
    :param customer_phone: номер телефона клиента в QuickResto
    :param auth: аутентификация
    :param headers: заголовки
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
            "accountType": {"accountGuid": "bonus_account_type-1"},  # ← из данных клиента
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
