#!/usr/bin/env python3
import os
import sys
import logging
from main import main

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_pythonanywhere.log'),
        logging.StreamHandler()
    ]
)

if __name__ == "__main__":
    print("🚀 Запуск бота на PythonAnywhere...")
    try:
        main()
    except KeyboardInterrupt:
        print("⏹️ Бот остановлен")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")