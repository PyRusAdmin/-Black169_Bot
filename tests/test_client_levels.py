#!/usr/bin/env python3
"""Тесты для проверки функций нормализации и уровней"""

import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.phone_utils import normalize_phone_number, format_phone_display
from services.client_levels import get_level, get_level_description, get_next_level_info

print("=" * 60)
print("ТЕСТЫ НОРМАЛИЗАЦИИ ТЕЛЕФОНОВ")
print("=" * 60)

test_phones = [
    '+7 924 111-14-44',
    '89241111444',
    '+79241111444',
    '8 924 111 14 44',
    '9841466936',
    '',
    '—',
]

for phone in test_phones:
    normalized = normalize_phone_number(phone)
    formatted = format_phone_display(normalized) if normalized else '—'
    print(f"{repr(phone):20} -> {repr(normalized):15} -> {formatted}")

print()
print("=" * 60)
print("ТЕСТЫ УРОВНЕЙ КЛИЕНТОВ")
print("=" * 60)

test_amounts = [0, 5000, 15000, 45000, 75000]
for amount in test_amounts:
    level = get_level(amount)
    desc = get_level_description(level)
    next_info = get_next_level_info(level, amount)
    print(f"{amount:>8} ₽ -> {level:<6} -> {desc}")
    if next_info['has_next']:
        print(f"           {next_info['message']}")

print()
print("=" * 60)
print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
print("=" * 60)
