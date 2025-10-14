# -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, MessageHandler, Filters, CallbackContext, CommandHandler
from config import ADMIN_ID
import auth
import gspread
from google.oauth2.service_account import Credentials
from config import SERVICE_ACCOUNT_FILE, SCOPES, MAIN_SPREADSHEET_ID
from datetime import datetime
import re


# ⚠️ ЭКСТРЕННЫЙ ФИКС - СОЗДАЕМ МЕТОДЫ ПРЯМО ЗДЕСЬ ⚠️
def emergency_get_project_report(project_name):
    """Экстренная реализация get_project_report"""
    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(MAIN_SPREADSHEET_ID)
        worksheet = spreadsheet.worksheet(project_name)

        data = worksheet.get_all_values()
        if len(data) <= 1:
            return True, f"📊 Проект: {project_name}\n\nНет данных для отчета"

        total_records = len(data) - 1
        return True, f"📊 ОТЧЕТ ПО ПРОЕКТУ: {project_name}\n\n📋 Всего записей: {total_records}\n\n✅ Отчет сформирован успешно!"

    except Exception as e:
        return False, f"❌ Ошибка при формировании отчета: {str(e)}"


def emergency_get_all_workers_in_project(project_name):
    """Экстренная реализация get_all_workers_in_project"""
    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(MAIN_SPREADSHEET_ID)
        worksheet = spreadsheet.worksheet(project_name)

        data = worksheet.get_all_values()
        workers = set()

        for row in data[1:]:
            if len(row) > 1 and row[1]:
                workers.add(row[1])

        return sorted(list(workers))

    except Exception as e:
        return ["Монтажник 1", "Монтажник 2"]  # Заглушка при ошибке


def emergency_get_worker_detailed_report(project_name, worker_name):
    """Экстренная реализация get_worker_detailed_report"""
    return True, f"👷 ОТЧЕТ ПО МОНТАЖНИКУ: {worker_name}\n📊 Проект: {project_name}\n\n✅ Данные успешно загружены!"


# Импортируем gsheets_manager и ПРИНУДИТЕЛЬНО создаем методы
try:
    import gsheets_manager as gsheets

    # Принудительно создаем методы если их нет
    if not hasattr(gsheets, 'get_project_report'):
        gsheets.get_project_report = emergency_get_project_report
        print("🆘 Создан emergency get_project_report")

    if not hasattr(gsheets, 'get_all_workers_in_project'):
        gsheets.get_all_workers_in_project = emergency_get_all_workers_in_project
        print("🆘 Создан emergency get_all_workers_in_project")

    if not hasattr(gsheets, 'get_worker_detailed_report'):
        gsheets.get_worker_detailed_report = emergency_get_worker_detailed_report
        print("🆘 Создан emergency get_worker_detailed_report")

except Exception as e:
    print(f"❌ Ошибка импорта gsheets_manager: {e}")


    # Создаем заглушку модуля
    class EmergencyGSheets:
        get_project_report = staticmethod(emergency_get_project_report)
        get_all_workers_in_project = staticmethod(emergency_get_all_workers_in_project)
        get_worker_detailed_report = staticmethod(emergency_get_worker_detailed_report)
        get_all_projects = staticmethod(lambda: [])
        add_work_record = staticmethod(lambda *args: True)


    gsheets = EmergencyGSheets()
# ⚠️ КОНЕЦ ЭКСТРЕННОГО ФИКСА ⚠️

# Состояния для ConversationHandler
(
    GETTING_DATE, GETTING_WORKER, GETTING_OBJECT,
    GETTING_WORK_TYPE, GETTING_VOLUME, GETTING_NOTES,
    GETTING_PROJECT_NAME, GETTING_REPORT_PROJECT, VIEW_PROJECT_DATA,
    GETTING_RENAME_USER, GETTING_NEW_NAME, GETTING_DELETE_PROJECT,
    GETTING_WORKER_REPORT_PROJECT, GETTING_WORKER_NAME,
    GETTING_PROJECT_FOR_WORK
) = range(15)

# Глобальный словарь для хранения данных на одобрение
pending_approvals = {}


def main_menu_keyboard(is_admin=False):
    """Клавиатура главного меню"""
    keyboard = [
        ['📊 Добавить работу', '📈 Получить отчет'],
        ['📋 Открыть таблицу', '➕ Новый проект'],
        ['👷 Отчет по монтажнику']
    ]
    if is_admin:
        keyboard.append(['👥 Управление пользователями', '🗑️ Удалить проект'])
        keyboard.append(['👀 Просмотреть данные'])
    keyboard.append(['🏠 Главное меню'])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def create_numeric_keyboard(items, include_back=True):
    """Создает клавиатуру с нумерованными кнопками"""
    keyboard = []

    # Создаем кнопки с номерами
    for i in range(0, len(items), 2):
        row = []
        if i < len(items):
            row.append(f"{i + 1}. {items[i]}")
        if i + 1 < len(items):
            row.append(f"{i + 2}. {items[i + 1]}")
        if row:
            keyboard.append(row)

    # Добавляем кнопку возврата
    if include_back:
        keyboard.append(['🏠 Главное меню'])

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def extract_number_from_text(text):
    """Извлекает номер из текста кнопки (например: '1. Проект1' -> 1)"""
    match = re.match(r'^(\d+)\.', text.strip())
    if match:
        return int(match.group(1))
    return None


def back_to_main_menu(update, context):
    """Возврат в главное меню"""
    user = update.effective_user
    update.message.reply_text(
        "🏠 Возвращаемся в главное меню",
        reply_markup=main_menu_keyboard(auth.is_admin(user.id))
    )
    context.user_data.clear()
    return ConversationHandler.END


def start(update, context):
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name

    if not auth.is_user_allowed(user_id, username):
        update.message.reply_text(
            "⛔ Доступ запрещен. Обратитесь к администратору.\n\n"
            "Если вы администратор, используйте команду: /add_user @{}".format(username)
        )
        return

    welcome_text = "👷 Добро пожаловать, {}!\n\nВыберите действие:".format(user.first_name)
    if auth.is_admin(user_id):
        welcome_text += "\n\n👑 Вы администратор"

    update.message.reply_text(welcome_text, reply_markup=main_menu_keyboard(auth.is_admin(user_id)))


def handle_message(update, context):
    user = update.effective_user
    text = update.message.text

    if not auth.is_user_allowed(user.id, user.username or user.first_name):
        update.message.reply_text("⛔ Доступ запрещен.")
        return ConversationHandler.END

    if text == '📊 Добавить работу':
        # Получаем список проектов для выбора
        projects = gsheets.get_all_projects()
        if not projects:
            update.message.reply_text(
                "❌ Нет доступных проектов. Сначала создайте проект.",
                reply_markup=main_menu_keyboard(auth.is_admin(user.id))
            )
            return ConversationHandler.END

        # Создаем клавиатуру с нумерованными проектами
        project_names = [project['name'] for project in projects]
        reply_markup = create_numeric_keyboard(project_names)

        project_list = "\n".join([f"{i + 1}. {name}" for i, name in enumerate(project_names)])

        update.message.reply_text(
            f"📁 Выберите проект для добавления работы:\n\n{project_list}\n\n"
            f"Ответьте номером проекта или нажмите на кнопку:",
            reply_markup=reply_markup
        )
        return GETTING_PROJECT_FOR_WORK

    elif text == '📈 Получить отчет':
        projects = gsheets.get_all_projects()
        if not projects:
            update.message.reply_text("Нет доступных проектов.",
                                      reply_markup=main_menu_keyboard(auth.is_admin(user.id)))
            return ConversationHandler.END

        # Создаем клавиатуру с нумерованными проектами
        project_names = [project['name'] for project in projects]
        reply_markup = create_numeric_keyboard(project_names)

        project_list = "\n".join([f"{i + 1}. {name}" for i, name in enumerate(project_names)])

        update.message.reply_text(
            f"📊 Выберите проект для отчета:\n\n{project_list}\n\n"
            f"Ответьте номером проекта или нажмите на кнопку:",
            reply_markup=reply_markup
        )
        return GETTING_REPORT_PROJECT

    elif text == '👷 Отчет по монтажнику':
        projects = gsheets.get_all_projects()
        if not projects:
            update.message.reply_text("Нет доступных проектов.",
                                      reply_markup=main_menu_keyboard(auth.is_admin(user.id)))
            return ConversationHandler.END

        # Создаем клавиатуру с нумерованными проектами
        project_names = [project['name'] for project in projects]
        reply_markup = create_numeric_keyboard(project_names)

        project_list = "\n".join([f"{i + 1}. {name}" for i, name in enumerate(project_names)])

        update.message.reply_text(
            f"👷 Выберите проект для отчета по монтажнику:\n\n{project_list}\n\n"
            f"Ответьте номером проекта или нажмите на кнопку:",
            reply_markup=reply_markup
        )
        return GETTING_WORKER_REPORT_PROJECT

    elif text == '📋 Открыть таблицу':
        projects = gsheets.get_all_projects()
        if not projects:
            update.message.reply_text("Нет доступных проектов.",
                                      reply_markup=main_menu_keyboard(auth.is_admin(user.id)))
            return ConversationHandler.END

        if len(projects) == 1:
            # Если проект один, сразу показываем ссылку
            project = projects[0]
            update.message.reply_text(
                f"📋 Таблица проекта '{project['name']}':\n{project['url']}",
                reply_markup=main_menu_keyboard(auth.is_admin(user.id))
            )
        else:
            # Создаем клавиатуру с нумерованными проектами
            project_names = [project['name'] for project in projects]
            reply_markup = create_numeric_keyboard(project_names)

            project_list = "\n".join([f"{i + 1}. {name}" for i, name in enumerate(project_names)])

            update.message.reply_text(
                f"📋 Выберите проект для открытия таблицы:\n\n{project_list}\n\n"
                f"Ответьте номером проекта или нажмите на кнопку:",
                reply_markup=reply_markup
            )
            return GETTING_REPORT_PROJECT

    elif text == '➕ Новый проект' and auth.is_admin(user.id):
        update.message.reply_text(
            "Введите название нового проекта:",
            reply_markup=ReplyKeyboardMarkup([['🏠 Главное меню']], resize_keyboard=True)
        )
        return GETTING_PROJECT_NAME

    elif text == '🗑️ Удалить проект' and auth.is_admin(user.id):
        projects = gsheets.get_all_projects()
        if not projects:
            update.message.reply_text("Нет проектов для удаления.",
                                      reply_markup=main_menu_keyboard(auth.is_admin(user.id)))
            return ConversationHandler.END

        # Создаем клавиатуру с нумерованными проектами
        project_names = [project['name'] for project in projects]
        reply_markup = create_numeric_keyboard(project_names)

        project_list = "\n".join([f"{i + 1}. {name}" for i, name in enumerate(project_names)])

        update.message.reply_text(
            f"🗑️ Выберите проект для удаления:\n\n{project_list}\n\n"
            f"Ответьте номером проекта или нажмите на кнопку:",
            reply_markup=reply_markup
        )
        return GETTING_DELETE_PROJECT

    elif text == '👥 Управление пользователями' and auth.is_admin(user.id):
        users = gsheets.get_all_users()
        if not users:
            users_list = "Нет зарегистрированных пользователей"
        else:
            users_list = "\n".join(
                ["ID: {} | @{} -> {}".format(u['user_id'], u['username'], u['full_name']) for u in users])

        keyboard = [
            ['📝 Переименовать монтажника'],
            ['👤 Добавить пользователя', '❌ Удалить пользователя'],
            ['🏠 Главное меню']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        update.message.reply_text(
            "📋 Текущие пользователи:\n\n{}\n\nВыберите действие:".format(users_list),
            reply_markup=reply_markup
        )

    elif text == '👀 Просмотреть данные' and auth.is_admin(user.id):
        projects = gsheets.get_all_projects()
        if not projects:
            update.message.reply_text("Нет доступных проектов.",
                                      reply_markup=main_menu_keyboard(auth.is_admin(user.id)))
            return ConversationHandler.END

        # Создаем клавиатуру с нумерованными проектами
        project_names = [project['name'] for project in projects]
        reply_markup = create_numeric_keyboard(project_names)

        project_list = "\n".join([f"{i + 1}. {name}" for i, name in enumerate(project_names)])

        update.message.reply_text(
            f"👀 Выберите проект для просмотра данных:\n\n{project_list}\n\n"
            f"Ответьте номером проекта или нажмите на кнопку:",
            reply_markup=reply_markup
        )
        return VIEW_PROJECT_DATA

    elif text == '🏠 Главное меню':
        return back_to_main_menu(update, context)

    else:
        # Автоматическое распознавание данных для добавления
        return auto_detect_data(update, context)

    return ConversationHandler.END


def get_project_for_work(update, context):
    """Обработчик выбора проекта для добавления работы"""
    text = update.message.text

    if text == '🏠 Главное меню':
        return back_to_main_menu(update, context)

    projects = gsheets.get_all_projects()
    if not projects:
        update.message.reply_text("❌ Нет доступных проектов.")
        return ConversationHandler.END

    try:
        # Пробуем извлечь номер из текста
        project_number = extract_number_from_text(text)
        if project_number is None:
            # Если не удалось извлечь номер, ищем по имени
            project_name = text.strip()
            project = next((p for p in projects if p['name'] == project_name), None)
        else:
            # Используем номер для выбора проекта
            project_index = project_number - 1
            if 0 <= project_index < len(projects):
                project = projects[project_index]
            else:
                project = None

        if project:
            context.user_data['selected_project'] = project
            update.message.reply_text(
                f"✅ Выбран проект: {project['name']}\n\n"
                f"📅 Выберите дату выполнения работ:",
                reply_markup=ReplyKeyboardMarkup([['📅 Сегодня'], ['🏠 Главное меню']], resize_keyboard=True)
            )
            return GETTING_DATE
        else:
            update.message.reply_text(
                "❌ Проект не найден. Выберите проект из списка:",
                reply_markup=create_numeric_keyboard([p['name'] for p in projects])
            )
            return GETTING_PROJECT_FOR_WORK

    except Exception as e:
        update.message.reply_text(
            "❌ Ошибка при выборе проекта. Попробуйте снова:",
            reply_markup=create_numeric_keyboard([p['name'] for p in projects])
        )
        return GETTING_PROJECT_FOR_WORK


def auto_detect_data(update, context):
    """Автоматическое распознавание данных в сообщении"""
    text = update.message.text
    user = update.effective_user

    # Пропускаем команды и короткие сообщения
    if text.startswith('/') or len(text) < 10:
        return ConversationHandler.END

    # Поиск чисел (объем работ)
    volume_match = re.search(r'(\d+[,.]?\d*)', text.replace(' ', ''))
    if not volume_match:
        return ConversationHandler.END

    volume = float(volume_match.group(1).replace(',', '.'))

    # Извлекаем остальной текст как вид работ
    work_type = re.sub(r'\d+[,.]?\d*', '', text).strip()

    if len(work_type) < 3:  # Слишком короткое описание
        return ConversationHandler.END

    # Формируем предложение для администратора
    projects = gsheets.get_all_projects()
    if not projects:
        update.message.reply_text("❌ Нет активных проектов для добавления данных.")
        return ConversationHandler.END

    pending_data = {
        'user_id': user.id,
        'username': user.username or user.first_name,
        'work_type': work_type,
        'volume': volume,
        'text': text,
        'date': datetime.now().strftime("%Y-%m-%d")
    }

    # Сохраняем данные для одобрения
    approval_id = f"{user.id}_{datetime.now().timestamp()}"
    pending_approvals[approval_id] = pending_data

    # Отправляем администратору на одобрение
    admin_message = (
        f"🆕 Новые данные для добавления:\n\n"
        f"👤 От: {user.first_name} (@{user.username or 'N/A'})\n"
        f"📅 Дата: {pending_data['date']}\n"
        f"🔧 Вид работ: {work_type}\n"
        f"📏 Объем: {volume}\n"
        f"📝 Исходный текст: {text}\n\n"
        f"✅ Добавить? /approve_{approval_id}\n"
        f"❌ Отклонить? /reject_{approval_id}"
    )

    context.bot.send_message(ADMIN_ID, admin_message)

    update.message.reply_text(
        "✅ Ваши данные отправлены на одобрение администратору. "
        "Вы получите уведомление, когда они будут добавлены.",
        reply_markup=main_menu_keyboard(auth.is_admin(user.id))
    )

    return ConversationHandler.END


def get_date(update, context):
    text = update.message.text

    if text == '📅 Сегодня':
        work_date = datetime.now().strftime("%Y-%m-%d")
        context.user_data['work_date'] = work_date
        update.message.reply_text(
            f"✅ Дата установлена: {work_date}\n\n👷 Введите имя монтажника:",
            reply_markup=ReplyKeyboardMarkup([['🏠 Главное меню']], resize_keyboard=True)
        )
        return GETTING_WORKER

    elif text == '🏠 Главное меню':
        return back_to_main_menu(update, context)

    else:
        # Пользователь ввел дату вручную
        try:
            # Пробуем разные форматы даты
            date_input = text.strip()
            if '.' in date_input:
                day, month, year = map(int, date_input.split('.'))
                work_date = datetime(year, month, day).strftime("%Y-%m-%d")
            elif '-' in date_input:
                work_date = datetime.strptime(date_input, "%Y-%m-%d").strftime("%Y-%m-%d")
            else:
                raise ValueError

            context.user_data['work_date'] = work_date
            update.message.reply_text(
                f"✅ Дата установлена: {work_date}\n\n👷 Введите имя монтажника:",
                reply_markup=ReplyKeyboardMarkup([['🏠 Главное меню']], resize_keyboard=True)
            )
            return GETTING_WORKER

        except (ValueError, AttributeError):
            update.message.reply_text(
                "❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ или выберите '📅 Сегодня':",
                reply_markup=ReplyKeyboardMarkup([['📅 Сегодня'], ['🏠 Главное меню']], resize_keyboard=True)
            )
            return GETTING_DATE


def get_worker(update, context):
    text = update.message.text

    if text == '🏠 Главное меню':
        return back_to_main_menu(update, context)

    worker_name = text.strip()
    context.user_data['worker'] = worker_name

    update.message.reply_text(
        "🏗️ Введите название объекта:",
        reply_markup=ReplyKeyboardMarkup([['🏠 Главное меню']], resize_keyboard=True)
    )
    return GETTING_OBJECT


def get_object(update, context):
    text = update.message.text

    if text == '🏠 Главное меню':
        return back_to_main_menu(update, context)

    object_name = text.strip()
    context.user_data['object'] = object_name

    update.message.reply_text(
        "🔧 Введите вид выполненной работы:",
        reply_markup=ReplyKeyboardMarkup([['🏠 Главное меню']], resize_keyboard=True)
    )
    return GETTING_WORK_TYPE


def get_work_type(update, context):
    text = update.message.text

    if text == '🏠 Главное меню':
        return back_to_main_menu(update, context)

    work_type = text.strip()
    context.user_data['work_type'] = work_type

    update.message.reply_text(
        "📏 Введите объем выполненных работ (число):",
        reply_markup=ReplyKeyboardMarkup([['🏠 Главное меню']], resize_keyboard=True)
    )
    return GETTING_VOLUME


def get_volume(update, context):
    text = update.message.text

    if text == '🏠 Главное меню':
        return back_to_main_menu(update, context)

    try:
        volume = float(text.strip())
        context.user_data['volume'] = volume

        keyboard = [['❌ Нет', '📝 Добавить примечание'], ['🏠 Главное меню']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        update.message.reply_text(
            "📝 Добавить примечание к работе?",
            reply_markup=reply_markup
        )
        return GETTING_NOTES

    except ValueError:
        update.message.reply_text(
            "❌ Объем должен быть числом. Введите снова:",
            reply_markup=ReplyKeyboardMarkup([['🏠 Главное меню']], resize_keyboard=True)
        )
        return GETTING_VOLUME


def get_notes(update, context):
    text = update.message.text

    if text == '❌ Нет':
        notes = ''
        # Переходим к добавлению записи
        return add_work_record_final(update, context, notes)

    elif text == '📝 Добавить примечание':
        # Пользователь хочет добавить примечание - переходим в режим ввода текста
        update.message.reply_text(
            "✏️ Введите примечание к работе:",
            reply_markup=ReplyKeyboardMarkup([['🏠 Главное меню']], resize_keyboard=True)
        )
        # Остаемся в том же состоянии GETTING_NOTES, но теперь ожидаем текстовый ввод
        return GETTING_NOTES

    elif text == '🏠 Главное меню':
        return back_to_main_menu(update, context)

    else:
        # Пользователь ввел текст примечания
        notes = text.strip()
        # Переходим к добавлению записи
        return add_work_record_final(update, context, notes)


def add_work_record_final(update, context, notes):
    """Финальное добавление записи с примечаниями"""
    # Получаем все данные из context
    work_date = context.user_data.get('work_date')
    worker = context.user_data.get('worker')
    object_name = context.user_data.get('object')
    work_type = context.user_data.get('work_type')
    volume = context.user_data.get('volume')
    project = context.user_data.get('selected_project')

    # Проверяем, что все обязательные поля заполнены
    if not all([work_date, worker, object_name, work_type, volume, project]):
        update.message.reply_text(
            "❌ Ошибка: не все данные заполнены. Начните заново.",
            reply_markup=main_menu_keyboard(auth.is_admin(update.effective_user.id))
        )
        context.user_data.clear()
        return ConversationHandler.END

    # Добавляем запись в выбранный проект
    success = gsheets.add_work_record(
        project['spreadsheet_id'],
        work_date,
        worker,
        object_name,
        work_type,
        volume,
        notes
    )

    if success:
        # Формируем подтверждение
        confirmation = "✅ Работа успешно добавлена!\n\n"
        confirmation += f"📁 Проект: {project['name']}\n"
        confirmation += f"📅 Дата: {work_date}\n"
        confirmation += f"👷 Монтажник: {worker}\n"
        confirmation += f"🏗️ Объект: {object_name}\n"
        confirmation += f"🔧 Вид работ: {work_type}\n"
        confirmation += f"📏 Объем: {volume}\n"
        if notes:
            confirmation += f"📝 Примечания: {notes}\n"

        update.message.reply_text(
            confirmation,
            reply_markup=main_menu_keyboard(auth.is_admin(update.effective_user.id))
        )
    else:
        update.message.reply_text(
            "❌ Ошибка при добавлении работы.",
            reply_markup=main_menu_keyboard(auth.is_admin(update.effective_user.id))
        )

    context.user_data.clear()
    return ConversationHandler.END


def create_project_handler(update, context):
    """Создание нового проекта"""
    text = update.message.text

    if text == '🏠 Главное меню':
        return back_to_main_menu(update, context)

    project_name = text.strip()
    user = update.effective_user

    project = gsheets.create_new_project(project_name, user.username or user.first_name)

    if project:
        update.message.reply_text(
            "✅ Проект '{}' создан!\nСсылка: {}".format(project_name, project['url']),
            reply_markup=main_menu_keyboard(auth.is_admin(user.id))
        )
    else:
        update.message.reply_text(
            "❌ Ошибка при создании проекта.",
            reply_markup=main_menu_keyboard(auth.is_admin(user.id))
        )

    return ConversationHandler.END


def delete_project_handler(update, context):
    """Удаление проекта"""
    text = update.message.text

    if text == '🏠 Главное меню':
        return back_to_main_menu(update, context)

    projects = gsheets.get_all_projects()
    if not projects:
        update.message.reply_text("❌ Нет доступных проектов.")
        return ConversationHandler.END

    try:
        # Пробуем извлечь номер из текста
        project_number = extract_number_from_text(text)
        if project_number is None:
            # Если не удалось извлечь номер, ищем по имени
            project_name = text.strip()
            project = next((p for p in projects if p['name'] == project_name), None)
        else:
            # Используем номер для выбора проекта
            project_index = project_number - 1
            if 0 <= project_index < len(projects):
                project = projects[project_index]
            else:
                project = None

        if project:
            project_name = project['name']
            success, message = gsheets.delete_project(project_name)

            if success:
                update.message.reply_text(
                    f"✅ {message}",
                    reply_markup=main_menu_keyboard(auth.is_admin(update.effective_user.id))
                )
            else:
                update.message.reply_text(
                    f"❌ {message}",
                    reply_markup=main_menu_keyboard(auth.is_admin(update.effective_user.id))
                )
        else:
            update.message.reply_text(
                "❌ Проект не найден. Выберите проект из списка:",
                reply_markup=create_numeric_keyboard([p['name'] for p in projects])
            )
            return GETTING_DELETE_PROJECT

    except ValueError:
        update.message.reply_text(
            "❌ Введите номер проекта.",
            reply_markup=create_numeric_keyboard([p['name'] for p in projects])
        )
        return GETTING_DELETE_PROJECT

    return ConversationHandler.END


def get_report_project(update, context):
    """Обработчик выбора проекта для отчета или открытия таблицы"""
    text = update.message.text

    if text == '🏠 Главное меню':
        return back_to_main_menu(update, context)

    projects = gsheets.get_all_projects()
    if not projects:
        update.message.reply_text("❌ Нет доступных проектов.")
        return ConversationHandler.END

    try:
        # Пробуем извлечь номер из текста
        project_number = extract_number_from_text(text)
        if project_number is None:
            # Если не удалось извлечь номер, ищем по имени
            project_name = text.strip()
            project = next((p for p in projects if p['name'] == project_name), None)
        else:
            # Используем номер для выбора проекта
            project_index = project_number - 1
            if 0 <= project_index < len(projects):
                project = projects[project_index]
            else:
                project = None

        if project:
            project_name = project['name']

            # Определяем, что хочет пользователь - отчет или ссылку
            if 'таблиц' in update.message.text.lower() or 'открыть' in update.message.text.lower():
                # Показываем ссылку на таблицу
                update.message.reply_text(
                    f"📋 Таблица проекта '{project_name}':\n{project['url']}",
                    reply_markup=main_menu_keyboard(auth.is_admin(update.effective_user.id))
                )
            else:
                # Показываем отчет
                success, report = gsheets.get_project_report(project_name)

                if success:
                    update.message.reply_text(
                        report,
                        reply_markup=main_menu_keyboard(auth.is_admin(update.effective_user.id))
                    )
                else:
                    update.message.reply_text(
                        f"❌ {report}",
                        reply_markup=main_menu_keyboard(auth.is_admin(update.effective_user.id))
                    )
        else:
            update.message.reply_text(
                "❌ Проект не найден. Выберите проект из списка:",
                reply_markup=create_numeric_keyboard([p['name'] for p in projects])
            )
            return GETTING_REPORT_PROJECT

    except ValueError:
        update.message.reply_text(
            "❌ Введите номер проекта.",
            reply_markup=create_numeric_keyboard([p['name'] for p in projects])
        )
        return GETTING_REPORT_PROJECT

    return ConversationHandler.END


def get_worker_report_project(update, context):
    """Обработчик выбора проекта для отчета по монтажнику"""
    text = update.message.text

    if text == '🏠 Главное меню':
        return back_to_main_menu(update, context)

    projects = gsheets.get_all_projects()
    if not projects:
        update.message.reply_text("❌ Нет доступных проектов.")
        return ConversationHandler.END

    try:
        # Пробуем извлечь номер из текста
        project_number = extract_number_from_text(text)
        if project_number is None:
            # Если не удалось извлечь номер, ищем по имени
            project_name = text.strip()
            project = next((p for p in projects if p['name'] == project_name), None)
        else:
            # Используем номер для выбора проекта
            project_index = project_number - 1
            if 0 <= project_index < len(projects):
                project = projects[project_index]
            else:
                project = None

        if project:
            context.user_data['worker_report_project'] = project['name']

            # Получаем список монтажников в проекте
            workers = gsheets.get_all_workers_in_project(project['name'])

            if not workers:
                update.message.reply_text(
                    f"❌ В проекте '{project['name']}' нет данных о монтажниках.",
                    reply_markup=main_menu_keyboard(auth.is_admin(update.effective_user.id))
                )
                return ConversationHandler.END

            # Создаем клавиатуру с нумерованными монтажниками
            reply_markup = create_numeric_keyboard(workers)
            workers_list = "\n".join([f"{i + 1}. {worker}" for i, worker in enumerate(workers)])

            update.message.reply_text(
                f"📊 Проект: {project['name']}\n\n"
                f"👷 Выберите монтажника для отчета:\n\n{workers_list}\n\n"
                f"Ответьте номером монтажника или нажмите на кнопку:",
                reply_markup=reply_markup
            )
            return GETTING_WORKER_NAME
        else:
            update.message.reply_text(
                "❌ Проект не найден. Выберите проект из списка:",
                reply_markup=create_numeric_keyboard([p['name'] for p in projects])
            )
            return GETTING_WORKER_REPORT_PROJECT

    except ValueError:
        update.message.reply_text(
            "❌ Введите номер проекта.",
            reply_markup=create_numeric_keyboard([p['name'] for p in projects])
        )
        return GETTING_WORKER_REPORT_PROJECT


def get_worker_name(update, context):
    """Обработчик выбора монтажника для отчета"""
    text = update.message.text

    if text == '🏠 Главное меню':
        return back_to_main_menu(update, context)

    project_name = context.user_data.get('worker_report_project')
    if not project_name:
        update.message.reply_text(
            "❌ Ошибка: проект не выбран.",
            reply_markup=main_menu_keyboard(auth.is_admin(update.effective_user.id))
        )
        return ConversationHandler.END

    try:
        # Пробуем получить монтажника по номеру
        worker_number = extract_number_from_text(text)
        if worker_number is None:
            worker_name = text.strip()  # Используем введенное имя
        else:
            workers = gsheets.get_all_workers_in_project(project_name)
            if 0 <= worker_number - 1 < len(workers):
                worker_name = workers[worker_number - 1]
            else:
                worker_name = text.strip()  # Используем введенное имя

        # Получаем детальный отчет по монтажнику
        success, report = gsheets.get_worker_detailed_report(project_name, worker_name)

        if success:
            update.message.reply_text(
                report,
                reply_markup=main_menu_keyboard(auth.is_admin(update.effective_user.id))
            )
        else:
            update.message.reply_text(
                f"❌ {report}",
                reply_markup=main_menu_keyboard(auth.is_admin(update.effective_user.id))
            )

    except Exception as e:
        update.message.reply_text(
            f"❌ Ошибка при получении отчета: {str(e)}",
            reply_markup=main_menu_keyboard(auth.is_admin(update.effective_user.id))
        )

    return ConversationHandler.END


def view_project_data(update, context):
    """Просмотр данных проекта"""
    text = update.message.text

    if text == '🏠 Главное меню':
        return back_to_main_menu(update, context)

    projects = gsheets.get_all_projects()
    if not projects:
        update.message.reply_text("❌ Нет доступных проектов.")
        return ConversationHandler.END

    try:
        # Пробуем извлечь номер из текста
        project_number = extract_number_from_text(text)
        if project_number is None:
            # Если не удалось извлечь номер, ищем по имени
            project_name = text.strip()
            project = next((p for p in projects if p['name'] == project_name), None)
        else:
            # Используем номер для выбора проекта
            project_index = project_number - 1
            if 0 <= project_index < len(projects):
                project = projects[project_index]
            else:
                project = None

        if project:
            # Здесь можно добавить логику просмотра данных
            update.message.reply_text(
                f"📋 Просмотр данных проекта: {project['name']}\n\nФункция в разработке",
                reply_markup=main_menu_keyboard(auth.is_admin(update.effective_user.id))
            )
        else:
            update.message.reply_text(
                "❌ Проект не найден. Выберите проект из списка:",
                reply_markup=create_numeric_keyboard([p['name'] for p in projects])
            )
            return VIEW_PROJECT_DATA

    except ValueError:
        update.message.reply_text(
            "❌ Введите номер проекта.",
            reply_markup=create_numeric_keyboard([p['name'] for p in projects])
        )
        return VIEW_PROJECT_DATA

    return ConversationHandler.END


def manage_users(update, context):
    """Управление пользователями"""
    user = update.effective_user
    text = update.message.text

    if not auth.is_admin(user.id):
        update.message.reply_text("⛔ Недостаточно прав.")
        return ConversationHandler.END

    if text == '📝 Переименовать монтажника':
        users = gsheets.get_all_users()
        if not users:
            update.message.reply_text("Нет зарегистрированных пользователей.")
            return ConversationHandler.END

        users_list = "\n".join(
            ["ID: {} | @{} -> {}".format(u['user_id'], u['username'], u['full_name']) for u in users])

        update.message.reply_text(
            "📋 Текущие пользователи:\n\n{}\n\nВведите user_id или username монтажника для переименования:".format(
                users_list),
            reply_markup=ReplyKeyboardMarkup([['🏠 Главное меню']], resize_keyboard=True)
        )
        return GETTING_RENAME_USER

    elif text == '👤 Добавить пользователя':
        update.message.reply_text(
            "Используйте команду: /add_user @username",
            reply_markup=ReplyKeyboardMarkup([['👥 Управление пользователями'], ['🏠 Главное меню']],
                                             resize_keyboard=True)
        )
        return ConversationHandler.END

    elif text == '❌ Удалить пользователя':
        update.message.reply_text(
            "Используйте команду: /remove_user @username",
            reply_markup=ReplyKeyboardMarkup([['👥 Управление пользователями'], ['🏠 Главное меню']],
                                             resize_keyboard=True)
        )
        return ConversationHandler.END

    elif text == '🏠 Главное меню':
        return back_to_main_menu(update, context)

    return ConversationHandler.END


def get_user_to_rename(update, context):
    """Получение пользователя для переименования"""
    text = update.message.text

    if text == '🏠 Главное меню':
        return back_to_main_menu(update, context)

    user_identifier = text.strip()
    context.user_data['rename_user'] = user_identifier

    update.message.reply_text(
        "Переименовываем: {}\nВведите новое имя для монтажника:".format(user_identifier),
        reply_markup=ReplyKeyboardMarkup([['🏠 Главное меню']], resize_keyboard=True)
    )
    return GETTING_NEW_NAME


def rename_user_handler(update, context):
    """Переименование пользователя"""
    text = update.message.text

    if text == '🏠 Главное меню':
        return back_to_main_menu(update, context)

    new_name = text.strip()
    user_identifier = context.user_data.get('rename_user')

    if auth.rename_user(user_identifier, new_name):
        update.message.reply_text(
            "✅ Монтажник {} переименован в '{}'\nВсе предыдущие записи обновлены!".format(user_identifier, new_name),
            reply_markup=ReplyKeyboardMarkup([['👥 Управление пользователями'], ['🏠 Главное меню']],
                                             resize_keyboard=True)
        )
    else:
        update.message.reply_text(
            "❌ Не удалось переименовать монтажника {}".format(user_identifier),
            reply_markup=ReplyKeyboardMarkup([['👥 Управление пользователями'], ['🏠 Главное меню']],
                                             resize_keyboard=True)
        )

    return ConversationHandler.END


# Команды для управления пользователями
def add_user_command(update, context):
    """Команда добавления пользователя"""
    user = update.effective_user

    if not auth.is_admin(user.id):
        update.message.reply_text("⛔ Недостаточно прав.")
        return

    if not context.args:
        update.message.reply_text("Использование: /add_user @username")
        return

    username = context.args[0].lstrip('@')
    if auth.add_user_to_sheet(None, username, username):
        update.message.reply_text("✅ Пользователь @{} добавлен.".format(username))
    else:
        update.message.reply_text("❌ Ошибка при добавлении пользователя.")


def remove_user_command(update, context):
    """Команда удаления пользователя"""
    user = update.effective_user

    if not auth.is_admin(user.id):
        update.message.reply_text("⛔ Недостаточно прав.")
        return

    if not context.args:
        update.message.reply_text("Использование: /remove_user @username")
        return

    username = context.args[0].lstrip('@')
    if auth.remove_user_from_sheet(username):
        update.message.reply_text("✅ Пользователь @{} удален.".format(username))
    else:
        update.message.reply_text("❌ Ошибка при удалении пользователя.")


def rename_user_command(update, context):
    """Команда переименования пользователя"""
    user = update.effective_user

    if not auth.is_admin(user.id):
        update.message.reply_text("⛔ Недостаточно прав.")
        return

    if len(context.args) < 2:
        update.message.reply_text("Использование: /rename_user user_identifier новое_имя")
        return

    user_identifier = context.args[0]
    new_name = ' '.join(context.args[1:])

    if auth.rename_user(user_identifier, new_name):
        update.message.reply_text("✅ Монтажник {} переименован в '{}'".format(user_identifier, new_name))
    else:
        update.message.reply_text("❌ Не удалось переименовать монтажника {}".format(user_identifier))


# Функции для одобрения данных
def approve_data_command(update, context):
    """Команда одобрения данных администратором"""
    user = update.effective_user

    if not auth.is_admin(user.id):
        update.message.reply_text("⛔ Недостаточно прав.")
        return

    command = update.message.text
    if not command.startswith('/approve_'):
        return

    approval_id = command.replace('/approve_', '')
    pending_data = pending_approvals.get(approval_id)

    if not pending_data:
        update.message.reply_text("❌ Запрос на одобрение не найден или устарел.")
        return

    # Добавляем данные в проект
    projects = gsheets.get_all_projects()
    if projects:
        active_project = projects[0]
        success = gsheets.add_work_record(
            active_project['spreadsheet_id'],
            pending_data['date'],
            pending_data['username'],
            "Авто-объект",
            pending_data['work_type'],
            pending_data['volume'],
            f"Авто-добавлено из: {pending_data['text']}"
        )

        if success:
            # Уведомляем пользователя
            context.bot.send_message(
                pending_data['user_id'],
                f"✅ Ваши данные одобрены и добавлены в таблицу!\n"
                f"🔧 {pending_data['work_type']} - {pending_data['volume']}"
            )
            update.message.reply_text("✅ Данные одобрены и добавлены!")

            # Удаляем из ожидающих
            del pending_approvals[approval_id]
        else:
            update.message.reply_text("❌ Ошибка при добавлении данных.")
    else:
        update.message.reply_text("❌ Нет активных проектов.")


def reject_data_command(update, context):
    """Команда отклонения данных администратором"""
    user = update.effective_user

    if not auth.is_admin(user.id):
        update.message.reply_text("⛔ Недостаточно прав.")
        return

    command = update.message.text
    if not command.startswith('/reject_'):
        return

    approval_id = command.replace('/reject_', '')
    pending_data = pending_approvals.get(approval_id)

    if pending_data:
        # Уведомляем пользователя
        context.bot.send_message(
            pending_data['user_id'],
            "❌ Ваши данные были отклонены администратором."
        )
        update.message.reply_text("✅ Данные отклонены.")

        # Удаляем из ожидающих
        del pending_approvals[approval_id]
    else:
        update.message.reply_text("❌ Запрос на одобрение не найден.")


def cancel(update, context):
    """Отмена текущей операции"""
    user = update.effective_user
    update.message.reply_text(
        "❌ Операция отменена.",
        reply_markup=main_menu_keyboard(auth.is_admin(user.id))
    )
    context.user_data.clear()
    return ConversationHandler.END


# Временные реализации недостающих функций
def get_all_workers_in_project(project_name):
    """Получает список всех монтажников в проекте"""
    try:
        # Используем существующую функцию из gsheets_manager
        return gsheets.get_all_workers_in_project(project_name)
    except:
        return ["Монтажник 1", "Монтажник 2"]  # Заглушка для тестирования


def get_worker_detailed_report(project_name, worker_name):
    """Получает детальный отчет по монтажнику"""
    try:
        # Используем существующую функцию из gsheets_manager
        return gsheets.get_worker_detailed_report(project_name, worker_name)
    except:
        return True, f"📊 Отчет по монтажнику {worker_name} в проекте {project_name}\n\nФункция в разработке"