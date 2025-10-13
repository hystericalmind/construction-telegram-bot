import os
import webbrowser


def help_download_credentials():
    """Помощь в скачивании credentials.json"""

    print("📋 ИНСТРУКЦИЯ ПО СКАЧИВАНИЮ credentials.json")
    print("=" * 50)

    print("1. 📍 Перейдите в Google Cloud Console:")
    print("   https://console.cloud.google.com/")
    print()

    print("2. 🔍 Выберите ваш проект: 'Construction Telegram Bot'")
    print()

    print("3. 👤 Перейдите в раздел:")
    print("   'IAM и администрирование' → 'Сервисные аккаунты'")
    print()

    print("4. 🎯 Найдите сервисный аккаунт: 'construction-bot'")
    print()

    print("5. 🔑 Создайте ключ:")
    print("   - Нажмите на сервисный аккаунт")
    print("   - Вкладка 'Ключи'")
    print("   - 'Добавить ключ' → 'Создать новый ключ'")
    print("   - Формат: JSON")
    print("   - 'Создать'")
    print()

    print("6. 💾 Файл автоматически скачается")
    print("   - Переименуйте его в 'credentials.json'")
    print("   - Переместите в папку с проектом")
    print()

    print("7. 📁 Текущая папка проекта:")
    print(f"   {os.getcwd()}")
    print()

    # Покажем текущие файлы в папке
    print("📋 Файлы в текущей папке:")
    print("-" * 30)
    files = os.listdir()
    for file in files:
        if file.endswith('.json') or file.endswith('.py') or file == '.env':
            print(f"   {file}")
    print("-" * 30)

    # Предложим открыть ссылку
    choice = input("Открыть Google Cloud Console в браузере? (y/n): ")
    if choice.lower() == 'y':
        webbrowser.open('https://console.cloud.google.com/iam-admin/serviceaccounts')

    print("\n🎯 После скачивания запустите: python setup_tables.py")


if __name__ == "__main__":
    help_download_credentials()