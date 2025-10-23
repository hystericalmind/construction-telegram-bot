import logging
import os
import sys
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def start(update, context):
    update.message.reply_text('🚀 Бот запущен на Railway! Используйте /help для списка команд.')

def help_command(update, context):
    update.message.reply_text('📋 Доступные команды: /start, /help')

def main():
    # Получаем токен из переменных окружения
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не настроен!")
        return

    try:
        # Создаем application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        
        logger.info("🤖 Бот запускается на Railway...")
        
        # Запускаем бота
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    main()
