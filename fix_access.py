import gspread
from google.oauth2.service_account import Credentials
from config import SERVICE_ACCOUNT_FILE, SCOPES, MAIN_SPREADSHEET_ID, USERS_SHEET_NAME, ADMIN_ID


def fix_access():
    """Добавляет текущего пользователя в таблицу"""
    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)

        spreadsheet = client.open_by_key(MAIN_SPREADSHEET_ID)
        users_sheet = spreadsheet.worksheet(USERS_SHEET_NAME)

        # Добавляем администратора
        users_sheet.append_row([str(ADMIN_ID), 'admin', 'Администратор', 'active'])
        print("✅ Доступ исправлен! Перезапустите бота.")

    except Exception as e:
        print("❌ Ошибка: {}".format(e))


if __name__ == "__main__":
    fix_access()