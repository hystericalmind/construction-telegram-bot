def create_env_file():
    """Создает .env файл с шаблоном"""
    env_content = """# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here

# Admin User ID (get from @userinfobot)
ADMIN_ID=your_telegram_user_id

# Google Sheets Main Spreadsheet ID
MAIN_SPREADSHEET_ID=your_main_google_sheet_id

# Дополнительные настройки (опционально)
# DEBUG=True
# DATABASE_URL=sqlite:///database.db
"""

    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ Файл .env успешно создан!")
        print("📝 Заполните его своими данными перед запуском бота")
    except Exception as e:
        print(f"❌ Ошибка при создании файла: {e}")


if __name__ == "__main__":
    create_env_file()