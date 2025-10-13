import gspread
from google.oauth2.service_account import Credentials
from config import SERVICE_ACCOUNT_FILE, SCOPES, MAIN_SPREADSHEET_ID, USERS_SHEET_NAME, ADMIN_ID  # Исправлен импорт
import os
from dotenv import load_dotenv

load_dotenv()


def setup_initial_user():
    """Добавляет администратора в таблицу users при первом запуске"""
    try:
        # Авторизация
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)

        # Открываем основную таблицу
        spreadsheet = client.open_by_key(MAIN_SPREADSHEET_ID)

        # Получаем лист users
        try:
            users_sheet = spreadsheet.worksheet(USERS_SHEET_NAME)
        except:
            print("❌ Лист users не найден")
            return False

        # Проверяем, есть ли уже пользователи
        users = users_sheet.get_all_records()
        if users:
            print("✅ В таблице уже есть пользователи")
            return True

        # Добавляем администратора
        users_sheet.append_row([
            str(ADMIN_ID),
            'admin',
            'Администратор',
            'active'
        ])

        print("✅ Администратор добавлен в таблицу users")
        return True

    except Exception as e:
        print("❌ Ошибка при добавлении администратора: {}".format(e))
        return False


def check_env_file():
    """Проверяет .env файл"""
    required_vars = ['BOT_TOKEN', 'ADMIN_ID', 'MAIN_SPREADSHEET_ID']
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print("❌ В .env файле отсутствуют переменные: {}".format(', '.join(missing_vars)))
        return False

    print("✅ .env файл настроен правильно")
    return True


def check_credentials():
    """Проверяет файл credentials.json"""
    if not os.path.exists(SERVICE_ACCOUNT_FILE):  # Используем переменную из config
        print("❌ Файл {} не найден".format(SERVICE_ACCOUNT_FILE))
        return False

    try:
        with open(SERVICE_ACCOUNT_FILE, 'r') as f:
            content = f.read()
            if '"client_email"' not in content:
                print("❌ Неверный формат {}".format(SERVICE_ACCOUNT_FILE))
                return False
    except:
        print("❌ Не удалось прочитать {}".format(SERVICE_ACCOUNT_FILE))
        return False

    print("✅ Файл {} найден и валиден".format(SERVICE_ACCOUNT_FILE))
    return True


if __name__ == "__main__":
    print("🔧 Настройка бота...")
    print("-" * 50)

    # Проверяем настройки
    if not check_env_file():
        exit(1)

    if not check_credentials():
        exit(1)

    # Добавляем администратора
    if setup_initial_user():
        print("\n🎉 Настройка завершена успешно!")
        print("🤖 Теперь запустите бота: python main.py")
    else:
        print("\n⚠️  Возникли проблемы с настройкой")
        print("💡 Вы можете добавить пользователя вручную командой: /add_user @username")