"""Основной файл Telegram бота МироСтрах"""
import asyncio
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from config import BOT_TOKEN
from database import init_db
from handlers import (
    start_command,
    help_command,
    handle_main_menu,
    handle_product_info,
    handle_product_detail,
    handle_survey,
    handle_survey_results,
    handle_application,
    handle_navigation,
    handle_operator_request,
    get_user_state
)
from states import UserStateEnum

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главный обработчик сообщений"""
    if not update.message or not update.message.text:
        return
    
    text = update.message.text
    text_lower = text.lower()
    state, _ = await get_user_state(update.effective_user.id)
    
    # Текстовые команды-синонимы
    if text_lower in ["начать", "старт"]:
        await start_command(update, context)
        return
    
    # Обработка критических команд
    if text in ["🆘 Помощь", "/help"] or text_lower == "помощь":
        await help_command(update, context)
        return
    
    # Триггеры для оператора (расширенный список)
    operator_triggers = [
        "👨‍💼 Оператор", "Хочу поговорить с человеком", "Оператор",
        "Мне не подходит", "Сложный вопрос", "Ошибка в полисе",
        "Хочу оператора", "Позовите человека"
    ]
    if text in operator_triggers or any(trigger.lower() in text_lower for trigger in ["оператор", "человек", "не подходит", "сложный вопрос", "ошибка в полисе"]):
        await handle_operator_request(update, context)
        return
    
    # Навигация (с текстовыми синонимами)
    if text in ["⬅️ Назад", "❌ Отмена", "ℹ️ Главное меню"]:
        await handle_navigation(update, context, text)
        return
    
    if text_lower in ["назад", "вернуться", "обратно"]:
        await handle_navigation(update, context, "⬅️ Назад")
        return
    
    if text_lower in ["меню", "главное меню", "домой"]:
        await handle_navigation(update, context, "ℹ️ Главное меню")
        return
    
    # Обработка по состояниям
    if state == UserStateEnum.MAIN_MENU:
        await handle_main_menu(update, context)
    
    elif state == UserStateEnum.PRODUCT_INFO:
        await handle_product_info(update, context)
    
    elif state == UserStateEnum.PRODUCT_SELECTION:
        await handle_product_detail(update, context)
    
    elif state in [
        UserStateEnum.SURVEY_START,
        UserStateEnum.SURVEY_INSURANCE_TYPE,
        UserStateEnum.SURVEY_AUTO_SUBTYPE,
        UserStateEnum.SURVEY_PRIORITY,
        UserStateEnum.SURVEY_DATA_COLLECTION,
        # Новые состояния сбора данных объекта
        UserStateEnum.SURVEY_CAR_BRAND,
        UserStateEnum.SURVEY_CAR_YEAR,
        UserStateEnum.SURVEY_CAR_VIN,
        UserStateEnum.SURVEY_ADDRESS,
        UserStateEnum.SURVEY_AREA,
        UserStateEnum.SURVEY_TRAVEL_COUNTRY,
        UserStateEnum.SURVEY_TRAVEL_DATES,
        UserStateEnum.SURVEY_AGE
    ]:
        await handle_survey(update, context)
    
    elif state == UserStateEnum.SURVEY_RESULTS:
        await handle_survey_results(update, context)
    
    elif state in [
        UserStateEnum.APPLICATION_START,
        UserStateEnum.APPLICATION_FIO,
        UserStateEnum.APPLICATION_PHONE,
        UserStateEnum.APPLICATION_EMAIL,
        UserStateEnum.APPLICATION_CONTACT_METHOD,
        UserStateEnum.APPLICATION_CONFIRMATION
    ]:
        await handle_application(update, context)
    
    elif state == UserStateEnum.APPLICATION_COMPLETED:
        if text == "🔄 Оформить еще один полис":
            await handle_main_menu(update, context)
        elif text == "📞 Связаться с менеджером сейчас":
            await handle_operator_request(update, context)
        elif text == "ℹ️ Главное меню":
            await handle_navigation(update, context, text)
        else:
            await handle_main_menu(update, context)
    
    else:
        # Если состояние неизвестно, возвращаем в главное меню
        await handle_main_menu(update, context)


async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик контактов (номер телефона)"""
    from handlers import save_user_state, handle_application
    from keyboards import get_always_available_keyboard
    
    state, ctx = await get_user_state(update.effective_user.id)
    
    if state == UserStateEnum.APPLICATION_PHONE and update.message.contact:
        ctx["application_phone"] = update.message.contact.phone_number
        await save_user_state(
            update.effective_user.id,
            UserStateEnum.APPLICATION_EMAIL,
            ctx
        )
        await update.message.reply_text(
            "Спасибо! Теперь укажите ваш email адрес:",
            reply_markup=get_always_available_keyboard()
        )


def main():
    """Главная функция запуска бота"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен! Проверьте файл ..env")
        return
    
    # Создание приложения
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Обработчик контактов
    application.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    
    # Обработчик всех текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # Инициализация БД
    async def post_init(app: Application):
        await init_db()
        logger.info("База данных инициализирована")
    
    application.post_init = post_init
    
    # Запуск бота
    logger.info("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
