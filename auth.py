from config import ADMIN_ID
import gsheets_manager as gsheets


def is_admin(user_id):
    """Проверяет, является ли пользователь администратором"""
    return str(user_id) == str(ADMIN_ID)


def is_user_allowed(user_id, username):
    """Проверяет, есть ли пользователь в списке разрешенных"""
    # Временно разрешаем всем для тестирования
    # Раскомментируйте следующую строку для включения проверки:
    return True

    # Если это администратор - всегда разрешаем
    if is_admin(user_id):
        return True

    # Если таблица users пустая или недоступна, временно разрешаем всем
    users = gsheets.get_all_users()
    if not users:
        print("⚠️  Таблица users пустая, временно разрешаем доступ")
        return True

    # Проверяем по user_id (надежнее) или по username
    for user in users:
        if (str(user_id) == str(user.get('user_id', '')) or
                username == user.get('username', '') or
                username == user.get('full_name', '')):
            return user.get('status') == 'active'

    return False


def add_user_to_sheet(user_id, username, full_name=None):
    """Добавляет пользователя в список разрешенных"""
    new_user = {
        'user_id': str(user_id) if user_id else '',
        'username': username,
        'full_name': full_name or username,
        'status': 'active'
    }
    return gsheets.append_user(new_user)


def remove_user_from_sheet(username):
    """Удаляет пользователя из списка разрешенных"""
    return gsheets.remove_user(username)


def rename_user(user_identifier, new_name):
    """Переименовывает пользователя"""
    return gsheets.rename_user(user_identifier, new_name)