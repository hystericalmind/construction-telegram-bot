import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', 0))

SERVICE_ACCOUNT_FILE = 'credentials.json'
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
MAIN_SPREADSHEET_ID = os.getenv('MAIN_SPREADSHEET_ID')

USERS_SHEET_NAME = 'users'
PROJECTS_SHEET_NAME = 'projects'

# Обновленные столбцы согласно новому формату
DEFAULT_COLUMNS = ['Дата', 'Монтажник', 'Объект', 'Вид работ', 'Объем', 'Примечания']

# Новые состояния для авто-добавления данных
PENDING_APPROVAL = 'pending_approval'