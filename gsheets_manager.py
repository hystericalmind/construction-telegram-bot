import gspread
from google.oauth2.service_account import Credentials
from config import SERVICE_ACCOUNT_FILE, SCOPES, MAIN_SPREADSHEET_ID, USERS_SHEET_NAME, PROJECTS_SHEET_NAME, DEFAULT_COLUMNS

_client = None

def get_client():
    global _client
    if _client is None:
        try:
            creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            _client = gspread.authorize(creds)
        except Exception as e:
            print("❌ Ошибка авторизации Google API: " + str(e))
    return _client

def get_sheet(sheet_name):
    try:
        client = get_client()
        if not client:
            return None
        spreadsheet = client.open_by_key(MAIN_SPREADSHEET_ID)
        return spreadsheet.worksheet(sheet_name)
    except Exception as e:
        print("❌ Ошибка получения листа " + sheet_name + ": " + str(e))
        return None

def get_all_users():
    sheet = get_sheet(USERS_SHEET_NAME)
    if not sheet:
        return []
    try:
        return sheet.get_all_records()
    except:
        return []

def append_user(user_data):
    sheet = get_sheet(USERS_SHEET_NAME)
    if not sheet:
        return False
    try:
        sheet.append_row([
            user_data['user_id'],
            user_data['username'],
            user_data['full_name'],
            user_data['status']
        ])
        return True
    except:
        return False

def remove_user(username):
    sheet = get_sheet(USERS_SHEET_NAME)
    if not sheet:
        return False
    try:
        cell = sheet.find(username, in_column=2)
        if cell:
            sheet.update_cell(cell.row, 4, 'inactive')
            return True
        return False
    except:
        return False

def rename_user(user_identifier, new_name):
    sheet = get_sheet(USERS_SHEET_NAME)
    if not sheet:
        return False
    try:
        cell = None
        try:
            cell = sheet.find(user_identifier, in_column=1)
        except:
            pass

        if not cell:
            cell = sheet.find(user_identifier, in_column=2)

        if cell:
            sheet.update_cell(cell.row, 3, new_name)
            return True
        return False
    except:
        return False

def get_all_projects():
    """Получает список всех проектов"""
    sheet = get_sheet(PROJECTS_SHEET_NAME)
    if not sheet:
        return []
    try:
        return sheet.get_all_records()
    except:
        return []

def create_new_project(project_name, admin_username):
    try:
        client = get_client()
        if not client:
            return None

        # Открываем основную таблицу
        spreadsheet = client.open_by_key(MAIN_SPREADSHEET_ID)

        # Проверяем, нет ли уже листа с таким именем
        try:
            existing_worksheet = spreadsheet.worksheet(project_name)
            print("❌ Лист с именем '" + project_name + "' уже существует")
            return None
        except gspread.WorksheetNotFound:
            pass

        # Создаем новый лист
        try:
            worksheet = spreadsheet.add_worksheet(title=project_name, rows=1000, cols=20)
        except Exception as e:
            print("❌ Ошибка создания листа: " + str(e))
            return None

        # Устанавливаем стандартные столбцы
        worksheet.update('A1', [DEFAULT_COLUMNS])

        # Добавляем фильтр
        try:
            worksheet.set_basic_filter()
        except:
            pass

        # Обновляем запись в projects sheet
        projects_sheet = get_sheet(PROJECTS_SHEET_NAME)
        if projects_sheet:
            worksheet_id = worksheet.id
            projects_sheet.append_row([
                project_name,
                MAIN_SPREADSHEET_ID,
                "https://docs.google.com/spreadsheets/d/" + MAIN_SPREADSHEET_ID + "/edit#gid=" + str(worksheet_id),
                admin_username,
                'active',
                ','.join(DEFAULT_COLUMNS)
            ])

        print("✅ Проект '" + project_name + "' создан как лист в основной таблице")
        return {
            'name': project_name,
            'spreadsheet_id': MAIN_SPREADSHEET_ID,
            'url': "https://docs.google.com/spreadsheets/d/" + MAIN_SPREADSHEET_ID + "/edit#gid=" + str(worksheet.id)
        }

    except Exception as e:
        print("❌ Ошибка создания проекта: " + str(e))
        return None

def delete_project(project_name):
    """Удаление проекта"""
    try:
        client = get_client()
        if not client:
            return False, "Нет доступа к API"

        spreadsheet = client.open_by_key(MAIN_SPREADSHEET_ID)

        try:
            worksheet = spreadsheet.worksheet(project_name)
            spreadsheet.del_worksheet(worksheet)
        except gspread.WorksheetNotFound:
            return False, "Проект '" + project_name + "' не найден"

        # Удаляем запись из листа projects
        projects_sheet = get_sheet(PROJECTS_SHEET_NAME)
        if projects_sheet:
            cell = projects_sheet.find(project_name, in_column=1)
            if cell:
                projects_sheet.delete_rows(cell.row)
                return True, "Проект '" + project_name + "' успешно удален"
            else:
                return False, "Не удалось найти запись проекта"
        else:
            return False, "Лист projects не найден"

    except Exception as e:
        return False, "Ошибка при удалении проекта: " + str(e)

def add_work_record(project_id, date, worker, object_name, work_type, volume, notes):
    try:
        client = get_client()
        if not client:
            return False

        spreadsheet = client.open_by_key(project_id)

        # Находим проект по имени
        projects = get_all_projects()
        project_name = None
        for project in projects:
            if project['spreadsheet_id'] == project_id:
                project_name = project['name']
                break

        if not project_name:
            print("❌ Проект не найден")
            return False

        # Открываем лист проекта
        try:
            worksheet = spreadsheet.worksheet(project_name)
            worksheet.append_row([date, worker, object_name, work_type, volume, notes])
            return True
        except Exception as e:
            print("❌ Ошибка доступа к листу проекта: " + str(e))
            return False

    except Exception as e:
        print("❌ Ошибка добавления записи: " + str(e))
        return False

def setup_tables():
    try:
        client = get_client()
        if not client:
            return False

        spreadsheet = client.open_by_key(MAIN_SPREADSHEET_ID)

        # Создаем лист users если не существует
        try:
            spreadsheet.worksheet(USERS_SHEET_NAME)
        except:
            users_sheet = spreadsheet.add_worksheet(title=USERS_SHEET_NAME, rows=100, cols=4)
            users_sheet.update('A1:D1', [['user_id', 'username', 'full_name', 'status']])

        # Создаем лист projects если не существует
        try:
            spreadsheet.worksheet(PROJECTS_SHEET_NAME)
        except:
            projects_sheet = spreadsheet.add_worksheet(title=PROJECTS_SHEET_NAME, rows=100, cols=6)
            projects_sheet.update('A1:F1', [['name', 'spreadsheet_id', 'url', 'admin', 'status', 'columns']])

        return True

    except Exception as e:
        print("❌ Ошибка настройки таблиц: " + str(e))
        return False
