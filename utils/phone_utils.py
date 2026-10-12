import re


def normalize_phone_number(phone: str) -> str:
    """
    Нормализация номера телефона к единому виду.

    Приводит номер к формату: 79999999999 (11 цифр, начиная с 7)

    :param phone: Исходный номер телефона
    :return: Нормализованный номер телефона
    """
    if not phone or phone.strip() in ["", "—", "-", "None", "null"]:
        return ""

    # Удаляем все не цифровые символы
    digits = re.sub(r"\D", "", phone)

    # Если номер начинается с 8 и имеет 11 цифр, заменяем на 7
    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]

    # Если номер начинается с 7 и имеет 11 цифр — оставляем как есть
    if len(digits) == 11 and digits.startswith("7"):
        return digits

    # Если номер начинается с 7 и имеет 12 цифр (например, 79991234567), оставляем
    if len(digits) == 11:
        return digits

    # Если номер короче или длиннее — возвращаем как есть (для логирования)
    return digits


def is_valid_phone(phone: str) -> bool:
    """
    Проверка валидности номера телефона.

    :param phone: Номер телефона для проверки
    :return: True если номер валидный, False если нет
    """
    normalized = normalize_phone_number(phone)
    return len(normalized) == 11 and normalized.startswith("7")
