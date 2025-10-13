import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Проверка .env файла:")
print("=" * 40)

bot_token = os.getenv('BOT_TOKEN')
admin_id = os.getenv('ADMIN_ID')
spreadsheet_id = os.getenv('MAIN_SPREADSHEET_ID')

print(f"BOT_TOKEN: {bot_token}")
print(f"ADMIN_ID: {admin_id}")
print(f"MAIN_SPREADSHEET_ID: {spreadsheet_id}")

print("\n" + "=" * 40)

if spreadsheet_id and spreadsheet_id != 'your_main_google_sheet_id':
    print("✅ MAIN_SPREADSHEET_ID настроен правильно!")
else:
    print("❌ MAIN_SPREADSHEET_ID не настроен!")
    print("💡 Замените 'your_main_google_sheet_id' на реальный ID таблицы")

if bot_token and bot_token != 'your_telegram_bot_token_here':
    print("✅ BOT_TOKEN настроен!")
else:
    print("❌ BOT_TOKEN не настроен!")

if admin_id and admin_id != 'your_telegram_user_id':
    print("✅ ADMIN_ID настроен!")
else:
    print("❌ ADMIN_ID не настроен!")