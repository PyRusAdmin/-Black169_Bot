#!/usr/bin/env python3
"""Тест инициализации таблицы уровней клиентов"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.database import initialize_client_levels, get_all_client_levels, get_client_level_info

print("=" * 60)
print("ТЕСТ: Инициализация таблицы уровней клиентов")
print("=" * 60)

# Инициализация уровней
print("\n1. Инициализация уровней...")
result = initialize_client_levels()
print(f"   Результат: {'✅ Успешно' if result else '❌ Ошибка'}")

# Получение всех уровней
print("\n2. Все уровни из БД:")
levels = get_all_client_levels()

for level in levels:
    print(f"\n   {level['emoji']} {level['level_name']}:")
    print(f"      Мин. сумма: {level['min_accumulation']:,.0f} ₽")
    print(f"      Скидка: {level['discount_percent']}%")
    print(f"      Множитель бонусов: {level['bonus_multiplier']}x")
    print(f"      Бонус на ДР: {level['birthday_bonus']} бонусов")
    print(f"      Приоритетное обслуживание: {'✅' if level['priority_service'] else '❌'}")
    print(f"      Персональный менеджер: {'✅' if level['personal_manager'] else '❌'}")
    print(f"      Бесплатные мероприятия: {'✅' if level['free_event_access'] else '❌'}")
    
    # Привилегии
    import json
    privileges = json.loads(level.get('privileges', '[]'))
    if privileges:
        print(f"      Привилегии ({len(privileges)}):")
        for priv in privileges[:3]:  # Показываем первые 3
            print(f"        • {priv}")
        if len(privileges) > 3:
            print(f"        ... и ещё {len(privileges) - 3}")

# Тест получения информации об отдельном уровне
print("\n3. Тест получения информации об уровне Gold:")
gold_info = get_client_level_info("Gold")
if gold_info:
    print(f"   ✅ Получено: {gold_info['level_name']}")
    print(f"      Описание: {gold_info['description']}")
else:
    print("   ❌ Не удалось получить информацию")

print("\n" + "=" * 60)
print("ТЕСТ ЗАВЕРШЕН УСПЕШНО!")
print("=" * 60)
