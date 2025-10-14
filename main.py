import logging
import os
import sys
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from config import BOT_TOKEN
import handlers

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def error_handler(update, context):
    """Обработчик ошибок"""
    logger.error(f'Ошибка при обработке update {update}: {context.error}', exc_info=context.error)

def setup_handlers(dispatcher):
    """Настройка всех обработчиков"""

    # Обработчики команд
    dispatcher.add_handler(CommandHandler("start", handlers.start))
    dispatcher.add_handler(CommandHandler("add_user", handlers.add_user_command))
    dispatcher.add_handler(CommandHandler("remove_user", handlers.remove_user_command))
    dispatcher.add_handler(CommandHandler("rename_user", handlers.rename_user_command))
    dispatcher.add_handler(CommandHandler("cancel", handlers.cancel))

    # Обработчики для одобрения данных
    dispatcher.add_handler(MessageHandler(
        Filters.regex(r'^/approve_[\w\.]+$'),
        handlers.approve_data_command
    ))
    dispatcher.add_handler(MessageHandler(
        Filters.regex(r'^/reject_[\w\.]+$'),
        handlers.reject_data_command
    ))

    # Основной ConversationHandler для добавления работ
    add_work_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('^(📊 Добавить работу)$'), handlers.handle_message)
        ],
        states={
            handlers.GETTING_PROJECT_FOR_WORK: [
                MessageHandler(Filters.text & ~Filters.command, handlers.get_project_for_work)
            ],
            handlers.GETTING_DATE: [
                MessageHandler(Filters.text & ~Filters.command, handlers.get_date)
            ],
            handlers.GETTING_WORKER: [
                MessageHandler(Filters.text & ~Filters.command, handlers.get_worker)
            ],
            handlers.GETTING_OBJECT: [
                MessageHandler(Filters.text & ~Filters.command, handlers.get_object)
            ],
            handlers.GETTING_WORK_TYPE: [
                MessageHandler(Filters.text & ~Filters.command, handlers.get_work_type)
            ],
            handlers.GETTING_VOLUME: [
                MessageHandler(Filters.text & ~Filters.command, handlers.get_volume)
            ],
            handlers.GETTING_NOTES: [
                MessageHandler(Filters.text & ~Filters.command, handlers.get_notes)
            ],
        },
        fallbacks=[
            CommandHandler("cancel", handlers.cancel),
            MessageHandler(Filters.regex('^(🏠 Главное меню)$'), handlers.back_to_main_menu)
        ]
    )

    # ConversationHandler для управления проектами
    project_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('^(➕ Новый проект|📈 Получить отчет|👀 Просмотреть данные|🗑️ Удалить проект)$'),
                           handlers.handle_message)
        ],
        states={
            handlers.GETTING_PROJECT_NAME: [
                MessageHandler(Filters.text & ~Filters.command, handlers.create_project_handler)
            ],
            handlers.GETTING_REPORT_PROJECT: [
                MessageHandler(Filters.text & ~Filters.command, handlers.get_report_project)
            ],
            handlers.VIEW_PROJECT_DATA: [
                MessageHandler(Filters.text & ~Filters.command, handlers.view_project_data)
            ],
            handlers.GETTING_DELETE_PROJECT: [
                MessageHandler(Filters.text & ~Filters.command, handlers.delete_project_handler)
            ],
        },
        fallbacks=[
            CommandHandler("cancel", handlers.cancel),
            MessageHandler(Filters.regex('^(🏠 Главное меню)$'), handlers.back_to_main_menu)
        ]
    )

    # ConversationHandler для отчетов по монтажникам
    worker_report_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('^(👷 Отчет по монтажнику)$'), handlers.handle_message)
        ],
        states={
            handlers.GETTING_WORKER_REPORT_PROJECT: [
                MessageHandler(Filters.text & ~Filters.command, handlers.get_worker_report_project)
            ],
            handlers.GETTING_WORKER_NAME: [
                MessageHandler(Filters.text & ~Filters.command, handlers.get_worker_name)
            ],
        },
        fallbacks=[
            CommandHandler("cancel", handlers.cancel),
            MessageHandler(Filters.regex('^(🏠 Главное меню)$'), handlers.back_to_main_menu)
        ]
    )

    # ConversationHandler для управления пользователями
    users_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('^(👥 Управление пользователями)$'), handlers.handle_message)
        ],
        states={
            handlers.GETTING_RENAME_USER: [
                MessageHandler(Filters.text & ~Filters.command, handlers.get_user_to_rename)
            ],
            handlers.GETTING_NEW_NAME: [
                MessageHandler(Filters.text & ~Filters.command, handlers.rename_user_handler)
            ],
        },
        fallbacks=[
            CommandHandler("cancel", handlers.cancel),
            MessageHandler(Filters.regex('^(🏠 Главное меню)$'), handlers.back_to_main_menu)
        ]
    )

    # Добавляем все ConversationHandler
    dispatcher.add_handler(add_work_conv_handler)
    dispatcher.add_handler(project_conv_handler)
    dispatcher.add_handler(worker_report_conv_handler)
    dispatcher.add_handler(users_conv_handler)

    # Обработчики для кнопок управления пользователями
    dispatcher.add_handler(MessageHandler(
        Filters.regex('^(📝 Переименовать монтажника|👤 Добавить пользователя|❌ Удалить пользователя)$'),
        handlers.manage_users
    ))

    # Обработчик для кнопки "Открыть таблицу"
    dispatcher.add_handler(MessageHandler(
        Filters.regex('^(📋 Открыть таблицу)$'),
        handlers.handle_message
    ))

    # Обработчик для кнопки "Главное меню"
    dispatcher.add_handler(MessageHandler(
        Filters.regex('^(🏠 Главное меню)$'),
        handlers.back_to_main_menu
    ))

    # Обработчик обычных текстовых сообщений (главное меню и авто-распознавание)
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command,
        handlers.handle_message
    ))

    # Обработчик ошибок
    dispatcher.add_error_handler(error_handler)

def main():
    """Основная функция запуска бота"""
    try:
        # Проверяем наличие токена
        if not BOT_TOKEN or BOT_TOKEN == 'your_telegram_bot_token_here':
            print("❌ BOT_TOKEN не настроен в .env файле!")
            print("💡 Откройте .env и замените your_telegram_bot_token_here на реальный токен")
            return

        # Создаем updater и dispatcher (старая версия API)
        updater = Updater(BOT_TOKEN, use_context=True)
        dispatcher = updater.dispatcher

        # Настраиваем обработчики
        setup_handlers(dispatcher)

        # Запускаем бота
        print("🤖 Бот запускается на Railway...")
        print("✅ Бот успешно запущен!")
        print("📱 Бот работает в режиме polling")
        
        # Запускаем polling (старая версия API)
        updater.start_polling()
        
        # Бесконечный цикл
        updater.idle()

    except Exception as e:
        logger.error(f"Критическая ошибка при запуске бота: {e}")
        print(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main()
