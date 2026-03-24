# -*- coding: utf-8 -*-
import json

import requests

from requests.auth import HTTPBasicAuth

from config import username_quickresto, password_quickresto

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
    result = get_client_phone(layer_name_quickresto, phone_number, auth, headers)

    if result:
        print(json.dumps(result, indent=2, ensure_ascii=False))

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

        print(f"ID:      {client_id}")
        print(f"Имя:     {name} {surname}")
        print(f"Телефон: {phone}")
        print(f"GUID:    {guid}")

        data = {
            'client_id': client_id,
            'name': name,
            'surname': surname,
            'phone': phone,
            'guid': guid
        }

        return data

    else:
        print("Клиент не найден")
