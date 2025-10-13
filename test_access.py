import gspread
from google.oauth2.service_account import Credentials
from config import SERVICE_ACCOUNT_FILE, SCOPES, MAIN_SPREADSHEET_ID


def test_access():
    """Проверяет доступ к таблице"""
    try:
        print("🔍 Проверка доступа к Google таблице...")

        # Авторизация
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)

        # Пытаемся открыть таблицу
        spreadsheet = client.open_by_key(MAIN_SPREADSHEET_ID)
        print("✅ Таблица найдена!")

        # Пытаемся прочитать данные
        worksheet = spreadsheet.sheet1
        data = worksheet.get_all_values()
        print(f"✅ Данные прочитаны! Записей: {len(data)}")

        # Пытаемся записать данные
        worksheet.update('A1', [['Тест', 'Доступ', 'Работает']])
        print("✅ Запись данных успешна!")

        print("🎉 Все проверки пройдены! Доступ настроен правильно!")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\n💡 Возможные решения:")
        print("1. Проверьте MAIN_SPREADSHEET_ID в .env файле")
        print("2. Убедитесь, что дали доступ сервисному аккаунту")
        print("3. Проверьте email сервисного аккаунта в credentials.json")


if __name__ == "__main__":
    test_access()