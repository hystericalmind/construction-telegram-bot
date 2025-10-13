import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройки из config.py
SERVICE_ACCOUNT_FILE = 'credentials.json'
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
MAIN_SPREADSHEET_ID = os.getenv('MAIN_SPREADSHEET_ID')
USERS_SHEET_NAME = 'users'
PROJECTS_SHEET_NAME = 'projects'


def setup_tables():
    """Автоматическая настройка таблиц"""
    print("🔄 Настраиваю Google таблицы...")

    try:
        # Проверяем существование файла credentials
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            print("❌ Файл credentials.json не найден!")
            print("💡 Скачайте его из Google Cloud Console")
            return False

        # Проверяем наличие ID таблицы
        if not MAIN_SPREADSHEET_ID or MAIN_SPREADSHEET_ID == 'your_main_google_sheet_id':
            print("❌ MAIN_SPREADSHEET_ID не настроен в .env файле!")
            print("💡 Откройте .env и замените your_main_google_sheet_id на реальный ID")
            return False

        # Авторизация
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)

        # Открываем основную таблицу
        spreadsheet = client.open_by_key(MAIN_SPREADSHEET_ID)
        print("✅ Подключение к таблице установлено")

        # Создаем или проверяем лист users
        try:
            users_sheet = spreadsheet.worksheet(USERS_SHEET_NAME)
            print("✅ Лист 'users' уже существует")
        except:
            users_sheet = spreadsheet.add_worksheet(title=USERS_SHEET_NAME, rows=100, cols=4)
            users_sheet.update('A1:D1', [['user_id', 'username', 'full_name', 'status']])
            print("✅ Лист 'users' создан")

        # Создаем или проверяем лист projects
        try:
            projects_sheet = spreadsheet.worksheet(PROJECTS_SHEET_NAME)
            print("✅ Лист 'projects' уже существует")
        except:
            projects_sheet = spreadsheet.add_worksheet(title=PROJECTS_SHEET_NAME, rows=100, cols=6)
            projects_sheet.update('A1:F1', [['name', 'spreadsheet_id', 'url', 'admin', 'status', 'columns']])
            print("✅ Лист 'projects' создан")

        print("🎉 Настройка таблиц завершена!")
        return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\n💡 Возможные причины:")
        print("1. Нет доступа к интернету")
        print("2. Неправильный MAIN_SPREADSHEET_ID")
        print("3. Сервисный аккаунт не имеет доступа к таблице")
        print("4. Не включены Google Sheets API в Google Cloud Console")
        return False


if __name__ == "__main__":
    setup_tables()