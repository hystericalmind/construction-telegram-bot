import sys
import os

# Добавляем путь к проекту
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

# Импортируем и запускаем бота
from main import main

# Функция для запуска на PythonAnywhere
application = None

def run_bot():
    try:
        print("🤖 Запускаем бота на PythonAnywhere...")
        main()
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")

# Для запуска в отдельном потоке
if __name__ == "__main__":
    run_bot()