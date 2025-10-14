#!/usr/bin/env python3
"""Тестовый скрипт для проверки методов gsheets_manager"""

import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(__file__))

try:
    import gsheets_manager as gsheets

    print("✅ Модуль gsheets_manager загружен успешно")

    # Проверяем наличие методов
    methods_to_check = [
        'get_project_report',
        'get_all_workers_in_project',
        'get_worker_detailed_report',
        'get_all_projects',
        'add_work_record'
    ]

    for method in methods_to_check:
        if hasattr(gsheets, method):
            print(f"✅ Метод {method} найден")
        else:
            print(f"❌ Метод {method} НЕ найден")

    # Проверяем список проектов
    projects = gsheets.get_all_projects()
    print(f"📊 Найдено проектов: {len(projects)}")
    for project in projects:
        print(f"  - {project.get('name', 'N/A')}")

except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback

    traceback.print_exc()