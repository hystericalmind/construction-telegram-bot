#!/usr/bin/env python3
import os
import sys
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def setup_environment():
    """Настройка окружения для Railway"""
    # Создаем credentials.json если есть переменная GOOGLE_CREDENTIALS
    google_creds = os.getenv('GOOGLE_CREDENTIALS')
    if google_creds and not os.path.exists('credentials.json'):
        try:
            with open('credentials.json', 'w') as f:
                f.write(google_creds)
            print("✅ credentials.json создан из переменных окружения")
        except Exception as e:
            print(f"❌ Ошибка создания credentials.json: {e}")
    
    # Проверяем обязательные переменные
    required_vars = ['BOT_TOKEN', 'ADMIN_ID', 'MAIN_SPREADSHEET_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Отсутствуют переменные: {', '.join(missing_vars)}")
        return False
    
    print("✅ Окружение настроено правильно")
    return True

def main():
    print("🚀 Запуск бота на Railway...")
    
    if not setup_environment():
        print("❌ Не удалось настроить окружение")
        return
    
    try:
        from main import main as bot_main
        bot_main()
    except KeyboardInterrupt:
        print("⏹️ Бот остановлен")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
