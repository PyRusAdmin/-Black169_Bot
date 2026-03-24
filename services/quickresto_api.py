# -*- coding: utf-8 -*-
import json

import requests

from requests.auth import HTTPBasicAuth
from loguru import logger
from config import username_quickresto, password_quickresto, console, layer_name_quickresto

base_url = f"https://{layer_name_quickresto}.quickresto.ru/platform/online/api"
auth = HTTPBasicAuth(username_quickresto, password_quickresto)
headers = {"Content-Type": "application/json"}


# https://quickresto.ru/api/

def get_client_phone(layer_name_quickresto, phone_number, auth, headers):
    """
    Возвращает информацию о клиенте по номеру телефона

    :param layer_name_quickresto: название слоя quickresto
    :param phone_number: номер телефона
    :param auth: авторизация в quickresto
    :param headers: заголовки запроса
    :return: информация о клиенте
    """
    url = f"https://{layer_name_quickresto}.quickresto.ru/platform/online/bonuses/filterCustomers"

    payload = {
        'search': phone_number,
        'typeList': ['customer'],
        'limit': 10,
        'offset': 0
    }
    response = requests.post(url, json=payload, auth=auth, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def print_client_info(layer_name_quickresto, phone_number, auth, headers):
    """Выводит информацию о клиенте по номеру телефона в формате JSON из QuickResto"""
    try:
        result = get_client_phone(layer_name_quickresto, phone_number, auth, headers)

        if result:
            console.print_json(json.dumps(result, indent=2, ensure_ascii=False))

        # Достаём список клиентов
        customers = result.get('customers', [])

        if customers:
            customer = customers[0]  # Выбираем первого клиента в списке клиентов
            # Личные данные
            client_id = customer.get('id')
            name = customer.get('firstName', '—')
            surname = customer.get('lastName', '—')
            guid = customer.get('customerGuid', '—')

            # Телефон — вложенный список
            contacts = customer.get('contactMethods', [])
            phone = contacts[0].get('value') if contacts else '—'

            console.log(f"ID:      {client_id}")
            console.log(f"Имя:     {name} {surname}")
            console.log(f"Телефон: {phone}")
            console.log(f"GUID:    {guid}")

            data = {
                'client_id': client_id,
                'firstName': name,
                'lastName': surname,
                'phone': phone,
                'guid': guid
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
            "className": "ru.edgex.quickresto.modules.crm.customer.CrmCustomer"
        }

        body = {
            "firstName": name_customer,
            "contactMethods": [
                {
                    "type": "phoneNumber",
                    "value": phone_customer
                }
            ]
        }

        response = requests.post(
            url,
            params=query_params,
            json=body,
            auth=auth,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        # Возвращаем данные созданного клиента
        client_data = {
            'id': result.get('id'),
            'firstName': name_customer,
            'phone': phone_customer
        }
        
        logger.info(f"Клиент создан: id={client_data['id']}, имя={name_customer}, телефон={phone_customer}")
        return client_data
    
    except Exception as e:
        logger.exception(e)
        return None
