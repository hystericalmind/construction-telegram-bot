import gspread
from google.oauth2.service_account import Credentials
from config import SERVICE_ACCOUNT_FILE, SCOPES, MAIN_SPREADSHEET_ID


def cleanup_drive():
    """Очищает старые таблицы сервисного аккаунта"""
    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)

        # Получаем все таблицы
        spreadsheets = client.list_spreadsheet_files()

        print(f"📊 Найдено таблиц: {len(spreadsheets)}")

        # Удаляем старые (кроме основной)
        for spreadsheet in spreadsheets:
            if spreadsheet['id'] != MAIN_SPREADSHEET_ID:
                try:
                    client.del_spreadsheet(spreadsheet['id'])
                    print(f"🗑️ Удалена: {spreadsheet['name']}")
                except:
                    continue

    except Exception as e:
        print(f"❌ Ошибка очистки: {e}")


if __name__ == "__main__":
    cleanup_drive()