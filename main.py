import logging
import os
import sys
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from config import BOT_TOKEN
import handlers

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def error_handler(update, context):
    """Обработчик ошибок"""
    logger.error(f'Ошибка при обработке update {update}: {context.error}', exc_info=context.error)


def setup_handlers(application):
    """Настройка всех обработчиков"""

    # Обработчики команд
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("add_user", handlers.add_user_command))
    application.add_handler(CommandHandler("remove_user", handlers.remove_user_command))
    application.add_handler(CommandHandler("rename_user", handlers.rename_user_command))
    application.add_handler(CommandHandler("cancel", handlers.cancel))

    # Обработчики для одобрения данных
    application.add_handler(MessageHandler(
        filters.Regex(r'^/approve_[\w\.]+$'),
        handlers.approve_data_command
    ))
    application.add_handler(MessageHandler(
        filters.Regex(r'^/reject_[\w\.]+$'),
        handlers.reject_data_command
    ))

    # Основной ConversationHandler для добавления работ
    add_work_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex('^(📊 Добавить работу)$'), handlers.handle_message)
        ],
        states={
            handlers.GETTING_PROJECT_FOR_WORK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_project_for_work)
            ],
            handlers.GETTING_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_date)
            ],
            handlers.GETTING_WORKER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_worker)
            ],
            handlers.GETTING_OBJECT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_object)
            ],
            handlers.GETTING_WORK_TYPE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_work_type)
            ],
            handlers.GETTING_VOLUME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_volume)
            ],
            handlers.GETTING_NOTES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_notes)
            ],
        },
        fallbacks=[
            CommandHandler("cancel", handlers.cancel),
            MessageHandler(filters.Regex('^(🏠 Главное меню)$'), handlers.back_to_main_menu)
        ]
    )

    # ConversationHandler для управления проектами
    project_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex('^(➕ Новый проект|📈 Получить отчет|👀 Просмотреть данные|🗑️ Удалить проект)$'),
                           handlers.handle_message)
        ],
        states={
            handlers.GETTING_PROJECT_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.create_project_handler)
            ],
            handlers.GETTING_REPORT_PROJECT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_report_project)
            ],
            handlers.VIEW_PROJECT_DATA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.view_project_data)
            ],
            handlers.GETTING_DELETE_PROJECT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.delete_project_handler)
            ],
        },
        fallbacks=[
            CommandHandler("cancel", handlers.cancel),
            MessageHandler(filters.Regex('^(🏠 Главное меню)$'), handlers.back_to_main_menu)
        ]
    )

    # ConversationHandler для отчетов по монтажникам
    worker_report_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex('^(👷 Отчет по монтажнику)$'), handlers.handle_message)
        ],
        states={
            handlers.GETTING_WORKER_REPORT_PROJECT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_worker_report_project)
            ],
            handlers.GETTING_WORKER_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_worker_name)
            ],
        },
        fallbacks=[
            CommandHandler("cancel", handlers.cancel),
            MessageHandler(filters.Regex('^(🏠 Главное меню)$'), handlers.back_to_main_menu)
        ]
    )

    # ConversationHandler для управления пользователями
    users_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex('^(👥 Управление пользователями)$'), handlers.handle_message)
        ],
        states={
            handlers.GETTING_RENAME_USER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_user_to_rename)
            ],
            handlers.GETTING_NEW_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.rename_user_handler)
            ],
        },
        fallbacks=[
            CommandHandler("cancel", handlers.cancel),
            MessageHandler(filters.Regex('^(🏠 Главное меню)$'), handlers.back_to_main_menu)
        ]
    )

    # Добавляем все ConversationHandler
    application.add_handler(add_work_conv_handler)
    application.add_handler(project_conv_handler)
    application.add_handler(worker_report_conv_handler)
    application.add_handler(users_conv_handler)

    # Обработчики для кнопок управления пользователями
    application.add_handler(MessageHandler(
        filters.Regex('^(📝 Переименовать монтажника|👤 Добавить пользователя|❌ Удалить пользователя)$'),
        handlers.manage_users
    ))

    # Обработчик для кнопки "Открыть таблицу"
    application.add_handler(MessageHandler(
        filters.Regex('^(📋 Открыть таблицу)$'),
        handlers.handle_message
    ))

    # Обработчик для кнопки "Главное меню"
    application.add_handler(MessageHandler(
        filters.Regex('^(🏠 Главное меню)$'),
        handlers.back_to_main_menu
    ))

    # Обработчик обычных текстовых сообщений (главное меню и авто-распознавание)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handlers.handle_message
    ))

    # Обработчик ошибок
    application.add_error_handler(error_handler)


def main():
    """Основная функция запуска бота"""
    try:
        # Проверяем наличие токена
        if not BOT_TOKEN or BOT_TOKEN == 'your_telegram_bot_token_here':
            print("❌ BOT_TOKEN не настроен в .env файле!")
            print("💡 Откройте .env и замените your_telegram_bot_token_here на реальный токен")
            return

        # Создаем application (новая версия python-telegram-bot)
        application = Application.builder().token(BOT_TOKEN).build()

        # Настраиваем обработчики
        setup_handlers(application)

        # Запускаем бота
        print("🤖 Бот запускается на PythonAnywhere...")
        print("✅ Бот успешно запущен!")
        print("📱 Бот работает в режиме polling")

        # Запускаем polling
        application.run_polling()

    except Exception as e:
        logger.error(f"Критическая ошибка при запуске бота: {e}")
        print(f"❌ Критическая ошибка: {e}")


if __name__ == "__main__":
    main()