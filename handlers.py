"""Модуль с обработчиками команд и сообщений"""
from telegram import Update
from telegram.ext import ContextTypes
from database import async_session, User, Application, UserState
from sqlalchemy import select
from states import UserStateEnum
from keyboards import *
from products import get_product_info, recommend_products, calculate_price
import json
import random
from datetime import datetime


async def save_user_state(telegram_id: int, state: str, context: dict = None):
    """Сохранение состояния пользователя"""
    from database import serialize_json
    async with async_session() as session:
        result = await session.execute(
            select(UserState).where(UserState.telegram_id == telegram_id)
        )
        user_state = result.scalar_one_or_none()
        
        if user_state:
            user_state.state = state
            user_state.context = serialize_json(context or {})
            user_state.updated_at = datetime.utcnow()
        else:
            user_state = UserState(
                telegram_id=telegram_id,
                state=state,
                context=serialize_json(context or {})
            )
            session.add(user_state)
        
        await session.commit()


async def get_user_state(telegram_id: int) -> tuple:
    """Получение состояния пользователя"""
    from database import deserialize_json
    async with async_session() as session:
        result = await session.execute(
            select(UserState).where(UserState.telegram_id == telegram_id)
        )
        user_state = result.scalar_one_or_none()
        if user_state:
            return user_state.state, deserialize_json(user_state.context)
        return UserStateEnum.MAIN_MENU, {}


async def save_or_update_user(update: Update):
    """Сохранение или обновление пользователя в БД"""
    async with async_session() as session:
        user = update.effective_user
        result = await session.execute(
            select(User).where(User.telegram_id == user.id)
        )
        db_user = result.scalar_one_or_none()
        
        if db_user:
            db_user.username = user.username
            db_user.first_name = user.first_name
            db_user.last_name = user.last_name
        else:
            db_user = User(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            session.add(db_user)
        
        await session.commit()
        return db_user


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await save_or_update_user(update)
    await save_user_state(update.effective_user.id, UserStateEnum.MAIN_MENU)
    
    welcome_text = (
        "Здравствуйте! Я МироСтрах бот, ваш помощник в мире страхования. "
        "Я помогу вам подобрать подходящий страховой продукт и оформить полис. "
        "Чем могу помочь?"
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_menu_keyboard()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = (
        "📋 Доступные команды:\n\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать эту справку\n\n"
        "Основные функции:\n"
        "• Подбор страхового продукта через опрос\n"
        "• Информация о страховых продуктах\n"
        "• Оформление заявки на полис\n"
        "• Связь с оператором\n\n"
        "Используйте кнопки меню для навигации."
    )
    await update.message.reply_text(help_text)


async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка главного меню"""
    text = update.message.text
    
    if text == "📋 Подобрать страховой продукт":
        await save_user_state(update.effective_user.id, UserStateEnum.SURVEY_START)
        await update.message.reply_text(
            "Давайте подберем для вас идеальный вариант. Что вы хотите застраховать?",
            reply_markup=get_insurance_type_keyboard()
        )
    
    elif text == "ℹ️ Узнать о продуктах":
        await save_user_state(update.effective_user.id, UserStateEnum.PRODUCT_INFO)
        await update.message.reply_text(
            "Выберите интересующий вас тип страхования, чтобы узнать о нем подробнее.",
            reply_markup=get_products_menu_keyboard()
        )
    
    elif text == "📝 Оформить заявку":
        await save_user_state(update.effective_user.id, UserStateEnum.APPLICATION_START)
        await update.message.reply_text(
            "Для оформления заявки сначала нужно подобрать продукт. "
            "Давайте начнем с выбора типа страхования.",
            reply_markup=get_insurance_type_keyboard()
        )
    
    elif text == "🆘 Помощь / Связаться с оператором":
        await help_command(update, context)
        await update.message.reply_text(
            "Для связи с оператором нажмите кнопку '👨‍💼 Оператор'",
            reply_markup=get_always_available_keyboard()
        )


async def handle_product_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка меню информации о продуктах"""
    text = update.message.text
    product_map = {
        "🚗 ОСАГО": "osago",
        "🚙 Каско": "kasko",
        "🏠 Страхование жилья": "property",
        "✈️ Страхование путешественников": "travel",
        "❤️ Страхование здоровья": "health"
    }
    
    if text in product_map:
        product_key = product_map[text]
        product = get_product_info(product_key)
        
        if product:
            await save_user_state(
                update.effective_user.id,
                UserStateEnum.PRODUCT_SELECTION,
                {"product_key": product_key}
            )
            await update.message.reply_text(
                f"**{product['name']}**\n\n{product['description']}",
                reply_markup=get_product_detail_keyboard(product_key),
                parse_mode='Markdown'
            )
    
    elif text == "⬅️ Назад в главное меню":
        await save_user_state(update.effective_user.id, UserStateEnum.MAIN_MENU)
        await update.message.reply_text(
            "Вы вернулись в главное меню.",
            reply_markup=get_main_menu_keyboard()
        )


async def handle_product_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка детальной информации о продукте"""
    text = update.message.text
    state, ctx = await get_user_state(update.effective_user.id)
    product_key = ctx.get("product_key")
    
    if text == "🔎 Подробнее":
        product = get_product_info(product_key)
        if product:
            await update.message.reply_text(
                product['full_description'],
                reply_markup=get_product_detail_keyboard(product_key)
            )
    
    elif text == "✅ Подобрать этот продукт":
        await save_user_state(
            update.effective_user.id,
            UserStateEnum.SURVEY_START,
            {"selected_product": product_key}
        )
        await update.message.reply_text(
            "Отлично! Давайте подберем для вас оптимальный вариант. "
            "Что для вас наиболее важно при выборе страховки?",
            reply_markup=get_priority_keyboard()
        )
    
    elif text == "⬅️ Назад":
        await save_user_state(update.effective_user.id, UserStateEnum.PRODUCT_INFO)
        await update.message.reply_text(
            "Выберите интересующий вас тип страхования.",
            reply_markup=get_products_menu_keyboard()
        )


async def handle_survey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка опроса для подбора продукта"""
    text = update.message.text
    state, ctx = await get_user_state(update.effective_user.id)
    
    if state == UserStateEnum.SURVEY_START or state == UserStateEnum.SURVEY_INSURANCE_TYPE:
        insurance_map = {
            "🚗 Авто": "auto",
            "🏠 Недвижимость": "property",
            "✈️ Путешествие": "travel",
            "❤️ Здоровье": "health"
        }
        
        if text in insurance_map:
            ctx["insurance_type"] = insurance_map[text]
            if insurance_map[text] == "auto":
                await save_user_state(
                    update.effective_user.id,
                    UserStateEnum.SURVEY_AUTO_SUBTYPE,
                    ctx
                )
                await update.message.reply_text(
                    "Вам нужно оформить полис ОСАГО (обязательный) или Каско (добровольный)?",
                    reply_markup=get_auto_subtype_keyboard()
                )
            else:
                await save_user_state(
                    update.effective_user.id,
                    UserStateEnum.SURVEY_PRIORITY,
                    ctx
                )
                await update.message.reply_text(
                    "Что для вас наиболее важно при выборе страховки?",
                    reply_markup=get_priority_keyboard()
                )
        
        elif text == "⬅️ Назад":
            await save_user_state(update.effective_user.id, UserStateEnum.MAIN_MENU)
            await update.message.reply_text(
                "Вы вернулись в главное меню.",
                reply_markup=get_main_menu_keyboard()
            )
    
    elif state == UserStateEnum.SURVEY_AUTO_SUBTYPE:
        if text == "ОСАГО":
            ctx["auto_subtype"] = "osago"
            await save_user_state(
                update.effective_user.id,
                UserStateEnum.SURVEY_PRIORITY,
                ctx
            )
            await update.message.reply_text(
                "Что для вас наиболее важно при выборе страховки?",
                reply_markup=get_priority_keyboard()
            )
        elif text == "Каско":
            ctx["auto_subtype"] = "kasko"
            await save_user_state(
                update.effective_user.id,
                UserStateEnum.SURVEY_PRIORITY,
                ctx
            )
            await update.message.reply_text(
                "Что для вас наиболее важно при выборе страховки?",
                reply_markup=get_priority_keyboard()
            )
        elif text == "🤔 В чем разница?":
            await update.message.reply_text(
                "**ОСАГО** - обязательное страхование, покрывает ущерб третьим лицам.\n\n"
                "**Каско** - добровольное страхование, покрывает ущерб вашему автомобилю, "
                "угон, хищение и другие риски.",
                parse_mode='Markdown',
                reply_markup=get_auto_subtype_keyboard()
            )
        elif text == "⬅️ Назад":
            await save_user_state(
                update.effective_user.id,
                UserStateEnum.SURVEY_INSURANCE_TYPE,
                ctx
            )
            await update.message.reply_text(
                "Что вы хотите застраховать?",
                reply_markup=get_insurance_type_keyboard()
            )
    
    elif state == UserStateEnum.SURVEY_PRIORITY:
        priority_map = {
            "Максимальное покрытие": "maximum",
            "Оптимальное соотношение цены и качества": "optimal",
            "Минимальная стоимость": "minimum"
        }
        
        if text in priority_map:
            ctx["priority"] = priority_map[text]
            
            # Для авто — запрашиваем марку
            if ctx.get("insurance_type") == "auto":
                await save_user_state(
                    update.effective_user.id,
                    UserStateEnum.SURVEY_CAR_BRAND,
                    ctx
                )
                await update.message.reply_text(
                    "Укажите марку вашего автомобиля:",
                    reply_markup=get_car_brand_keyboard()
                )
            # Для недвижимости — тип жилья
            elif ctx.get("insurance_type") == "property":
                await save_user_state(
                    update.effective_user.id,
                    UserStateEnum.SURVEY_ADDRESS,
                    ctx
                )
                await update.message.reply_text(
                    "Какой тип жилья вы хотите застраховать?",
                    reply_markup=get_housing_type_keyboard()
                )
            # Для путешествий — страна
            elif ctx.get("insurance_type") == "travel":
                await save_user_state(
                    update.effective_user.id,
                    UserStateEnum.SURVEY_TRAVEL_COUNTRY,
                    ctx
                )
                await update.message.reply_text(
                    "В какую страну планируете поездку?",
                    reply_markup=get_country_keyboard()
                )
            # Для здоровья — возраст
            elif ctx.get("insurance_type") == "health":
                await save_user_state(
                    update.effective_user.id,
                    UserStateEnum.SURVEY_AGE,
                    ctx
                )
                await update.message.reply_text(
                    "Укажите ваш возраст:",
                    reply_markup=get_age_keyboard()
                )
            else:
                await show_survey_results(update, context, ctx)
        
        elif text == "⬅️ Назад":
            if ctx.get("auto_subtype"):
                await save_user_state(
                    update.effective_user.id,
                    UserStateEnum.SURVEY_AUTO_SUBTYPE,
                    ctx
                )
                await update.message.reply_text(
                    "Вам нужно оформить полис ОСАГО или Каско?",
                    reply_markup=get_auto_subtype_keyboard()
                )
            else:
                await save_user_state(
                    update.effective_user.id,
                    UserStateEnum.SURVEY_INSURANCE_TYPE,
                    ctx
                )
                await update.message.reply_text(
                    "Что вы хотите застраховать?",
                    reply_markup=get_insurance_type_keyboard()
                )
    
    # === СБОР ДАННЫХ АВТО ===
    elif state == UserStateEnum.SURVEY_CAR_BRAND:
        if text == "⬅️ Назад":
            await save_user_state(update.effective_user.id, UserStateEnum.SURVEY_PRIORITY, ctx)
            await update.message.reply_text(
                "Что для вас наиболее важно при выборе страховки?",
                reply_markup=get_priority_keyboard()
            )
        else:
            ctx["car_brand"] = text
            await save_user_state(update.effective_user.id, UserStateEnum.SURVEY_CAR_YEAR, ctx)
            await update.message.reply_text(
                "Укажите год выпуска автомобиля:",
                reply_markup=get_car_year_keyboard()
            )
    
    elif state == UserStateEnum.SURVEY_CAR_YEAR:
        if text == "⬅️ Назад":
            await save_user_state(update.effective_user.id, UserStateEnum.SURVEY_CAR_BRAND, ctx)
            await update.message.reply_text(
                "Укажите марку вашего автомобиля:",
                reply_markup=get_car_brand_keyboard()
            )
        else:
            # Парсим год
            if "2020-2024" in text:
                ctx["car_year"] = 2022
            elif "2015-2019" in text:
                ctx["car_year"] = 2017
            elif "2010-2014" in text:
                ctx["car_year"] = 2012
            elif "2005-2009" in text:
                ctx["car_year"] = 2007
            elif "До 2005" in text:
                ctx["car_year"] = 2000
            else:
                ctx["car_year"] = text
            
            await save_user_state(update.effective_user.id, UserStateEnum.SURVEY_CAR_VIN, ctx)
            await update.message.reply_text(
                "Введите VIN-номер автомобиля (17 символов) или нажмите 'Пропустить':",
                reply_markup=get_skip_keyboard()
            )
    
    elif state == UserStateEnum.SURVEY_CAR_VIN:
        if text == "⬅️ Назад":
            await save_user_state(update.effective_user.id, UserStateEnum.SURVEY_CAR_YEAR, ctx)
            await update.message.reply_text(
                "Укажите год выпуска автомобиля:",
                reply_markup=get_car_year_keyboard()
            )
        elif text == "Пропустить":
            ctx["car_vin"] = None
            await save_user_state(update.effective_user.id, UserStateEnum.SURVEY_DATA_COLLECTION, ctx)
            await update.message.reply_text(
                "Укажите мощность вашего автомобиля в л.с.:",
                reply_markup=get_power_keyboard()
            )
        else:
            ctx["car_vin"] = text.upper()
            await save_user_state(update.effective_user.id, UserStateEnum.SURVEY_DATA_COLLECTION, ctx)
            await update.message.reply_text(
                "Укажите мощность вашего автомобиля в л.с.:",
                reply_markup=get_power_keyboard()
            )
    
    # === СБОР ДАННЫХ НЕДВИЖИМОСТИ ===
    elif state == UserStateEnum.SURVEY_ADDRESS:
        housing_types = {
            "🏢 Квартира": "apartment",
            "🏠 Дом": "house",
            "🏘️ Таунхаус": "townhouse",
            "🏗️ Другое": "other"
        }
        if text == "⬅️ Назад":
            await save_user_state(update.effective_user.id, UserStateEnum.SURVEY_PRIORITY, ctx)
            await update.message.reply_text(
                "Что для вас наиболее важно при выборе страховки?",
                reply_markup=get_priority_keyboard()
            )
        elif text in housing_types:
            ctx["housing_type"] = housing_types[text]
            await save_user_state(update.effective_user.id, UserStateEnum.SURVEY_AREA, ctx)
            await update.message.reply_text(
                "Укажите площадь жилья в кв.м (например: 50):",
                reply_markup=get_skip_keyboard()
            )
    
    elif state == UserStateEnum.SURVEY_AREA:
        if text == "⬅️ Назад":
            await save_user_state(update.effective_user.id, UserStateEnum.SURVEY_ADDRESS, ctx)
            await update.message.reply_text(
                "Какой тип жилья вы хотите застраховать?",
                reply_markup=get_housing_type_keyboard()
            )
        elif text == "Пропустить":
            ctx["area"] = 50
            await show_survey_results(update, context, ctx)
        else:
            try:
                ctx["area"] = int(''.join(filter(str.isdigit, text)))
            except:
                ctx["area"] = 50
            await show_survey_results(update, context, ctx)
    
    # === СБОР ДАННЫХ ПУТЕШЕСТВИЙ ===
    elif state == UserStateEnum.SURVEY_TRAVEL_COUNTRY:
        countries = {
            "🇪🇺 Шенген": "schengen",
            "🇹🇷 Турция": "turkey",
            "🇪🇬 Египет": "egypt",
            "🇹🇭 Таиланд": "thailand",
            "🇦🇪 ОАЭ": "uae",
            "🌍 Другая": "other"
        }
        if text == "⬅️ Назад":
            await save_user_state(update.effective_user.id, UserStateEnum.SURVEY_PRIORITY, ctx)
            await update.message.reply_text(
                "Что для вас наиболее важно при выборе страховки?",
                reply_markup=get_priority_keyboard()
            )
        elif text in countries:
            ctx["travel_country"] = countries[text]
            await save_user_state(update.effective_user.id, UserStateEnum.SURVEY_TRAVEL_DATES, ctx)
            await update.message.reply_text(
                "На сколько дней планируется поездка? Введите число:",
                reply_markup=get_skip_keyboard()
            )
    
    elif state == UserStateEnum.SURVEY_TRAVEL_DATES:
        if text == "⬅️ Назад":
            await save_user_state(update.effective_user.id, UserStateEnum.SURVEY_TRAVEL_COUNTRY, ctx)
            await update.message.reply_text(
                "В какую страну планируете поездку?",
                reply_markup=get_country_keyboard()
            )
        elif text == "Пропустить":
            ctx["travel_days"] = 7
            await show_survey_results(update, context, ctx)
        else:
            try:
                ctx["travel_days"] = int(''.join(filter(str.isdigit, text)))
            except:
                ctx["travel_days"] = 7
            await show_survey_results(update, context, ctx)
    
    # === СБОР ДАННЫХ ЗДОРОВЬЯ ===
    elif state == UserStateEnum.SURVEY_AGE:
        age_map = {
            "18-30 лет": 25,
            "31-45 лет": 38,
            "46-60 лет": 53,
            "Старше 60": 65
        }
        if text == "⬅️ Назад":
            await save_user_state(update.effective_user.id, UserStateEnum.SURVEY_PRIORITY, ctx)
            await update.message.reply_text(
                "Что для вас наиболее важно при выборе страховки?",
                reply_markup=get_priority_keyboard()
            )
        elif text in age_map:
            ctx["age"] = age_map[text]
            await show_survey_results(update, context, ctx)
        else:
            try:
                ctx["age"] = int(''.join(filter(str.isdigit, text)))
            except:
                ctx["age"] = 30
            await show_survey_results(update, context, ctx)
    
    elif state == UserStateEnum.SURVEY_DATA_COLLECTION:
        # Обработка мощности для авто
        if "л.с." in text or "лс" in text.lower():
            if "Менее 100" in text:
                ctx["power"] = 90
            elif "100-150" in text:
                ctx["power"] = 125
            elif "Более 150" in text:
                ctx["power"] = 200
            else:
                try:
                    ctx["power"] = int(''.join(filter(str.isdigit, text)))
                except:
                    await update.message.reply_text(
                        "Пожалуйста, укажите мощность числом или выберите из вариантов.",
                        reply_markup=get_power_keyboard()
                    )
                    return
            
            await show_survey_results(update, context, ctx)
        
        elif text == "⬅️ Назад":
            await save_user_state(update.effective_user.id, UserStateEnum.SURVEY_CAR_VIN, ctx)
            await update.message.reply_text(
                "Введите VIN-номер автомобиля или нажмите 'Пропустить':",
                reply_markup=get_skip_keyboard()
            )



async def show_survey_results(update: Update, context: ContextTypes.DEFAULT_TYPE, survey_data: dict):
    """Показ результатов подбора"""
    recommendations = recommend_products(survey_data)
    
    if not recommendations:
        await update.message.reply_text(
            "К сожалению, не удалось подобрать подходящие варианты. "
            "Попробуйте изменить параметры поиска.",
            reply_markup=get_main_menu_keyboard()
        )
        await save_user_state(update.effective_user.id, UserStateEnum.MAIN_MENU)
        return
    
    await save_user_state(
        update.effective_user.id,
        UserStateEnum.SURVEY_RESULTS,
        {"recommendations": recommendations, "survey_data": survey_data}
    )
    
    result_text = "Исходя из ваших ответов, вот лучшие варианты для вас:\n\n"
    
    for i, rec in enumerate(recommendations, 1):
        result_text += f"**Вариант {i}: {rec['name']}**\n"
        result_text += f"{rec['description']}\n"
        result_text += f"Предварительная стоимость: {rec['price']:,.0f} руб.\n\n"
    
    await update.message.reply_text(
        result_text,
        parse_mode='Markdown',
        reply_markup=get_product_recommendation_keyboard(recommendations)
    )


async def handle_survey_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка результатов подбора"""
    text = update.message.text
    state, ctx = await get_user_state(update.effective_user.id)
    recommendations = ctx.get("recommendations", [])
    
    if text.startswith("✅ Выбрать вариант"):
        # Извлекаем номер варианта
        try:
            variant_num = int(text.split(":")[0].split()[-1]) - 1
            selected_rec = recommendations[variant_num]
            ctx["selected_recommendation"] = selected_rec
            await save_user_state(
                update.effective_user.id,
                UserStateEnum.APPLICATION_START,
                ctx
            )
            await start_application(update, context, selected_rec)
        except:
            await update.message.reply_text(
                "Произошла ошибка. Попробуйте выбрать вариант еще раз."
            )
    
    elif text == "🔍 Сравнить все варианты":
        comparison_text = "**Сравнение вариантов:**\n\n"
        for i, rec in enumerate(recommendations, 1):
            comparison_text += f"**{rec['name']}**\n"
            comparison_text += f"Стоимость: {rec['price']:,.0f} руб.\n"
            comparison_text += f"Описание: {rec['description']}\n\n"
        
        await update.message.reply_text(
            comparison_text,
            parse_mode='Markdown',
            reply_markup=get_product_recommendation_keyboard(recommendations)
        )
    
    elif text == "🔄 Подобрать заново":
        await save_user_state(update.effective_user.id, UserStateEnum.SURVEY_START)
        await update.message.reply_text(
            "Давайте подберем для вас идеальный вариант. Что вы хотите застраховать?",
            reply_markup=get_insurance_type_keyboard()
        )
    
    elif text == "⬅️ Назад":
        await save_user_state(update.effective_user.id, UserStateEnum.MAIN_MENU)
        await update.message.reply_text(
            "Вы вернулись в главное меню.",
            reply_markup=get_main_menu_keyboard()
        )


async def start_application(update: Update, context: ContextTypes.DEFAULT_TYPE, product: dict = None):
    """Начало оформления заявки"""
    state, ctx = await get_user_state(update.effective_user.id)
    
    if not product:
        product = ctx.get("selected_recommendation")
    
    if not product:
        await update.message.reply_text(
            "Для оформления заявки нужно сначала подобрать продукт.",
            reply_markup=get_main_menu_keyboard()
        )
        await save_user_state(update.effective_user.id, UserStateEnum.MAIN_MENU)
        return
    
    ctx["application_product"] = product
    await save_user_state(
        update.effective_user.id,
        UserStateEnum.APPLICATION_START,
        ctx
    )
    
    await update.message.reply_text(
        f"Вы выбрали **{product['name']}**. "
        "Для оформления заявки мне потребуется 5-7 минут. Начнем?",
        parse_mode='Markdown',
        reply_markup=get_confirmation_keyboard()
    )


async def handle_application(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка процесса оформления заявки"""
    text = update.message.text
    state, ctx = await get_user_state(update.effective_user.id)
    
    if state == UserStateEnum.APPLICATION_START:
        if text == "Да, начать":
            await save_user_state(
                update.effective_user.id,
                UserStateEnum.APPLICATION_FIO,
                ctx
            )
            await update.message.reply_text(
                "Пожалуйста, укажите ваше ФИО (полностью):",
                reply_markup=get_always_available_keyboard()
            )
        elif text == "❌ Отмена":
            await save_user_state(update.effective_user.id, UserStateEnum.MAIN_MENU)
            await update.message.reply_text(
                "Оформление заявки отменено.",
                reply_markup=get_main_menu_keyboard()
            )
    
    elif state == UserStateEnum.APPLICATION_FIO:
        if text in ["⬅️ Назад", "❌ Отмена", "ℹ️ Главное меню"]:
            await handle_navigation(update, context, text)
            return
        
        ctx["application_fio"] = text
        await save_user_state(
            update.effective_user.id,
            UserStateEnum.APPLICATION_PHONE,
            ctx
        )
        await update.message.reply_text(
            "Укажите ваш номер телефона или нажмите кнопку для автоматической отправки:",
            reply_markup=get_phone_keyboard()
        )
    
    elif state == UserStateEnum.APPLICATION_PHONE:
        if text in ["⬅️ Назад", "❌ Отмена", "ℹ️ Главное меню"]:
            await handle_navigation(update, context, text)
            return
        
        # Проверяем, есть ли контакт в сообщении
        if update.message.contact:
            ctx["application_phone"] = update.message.contact.phone_number
        else:
            ctx["application_phone"] = text
        
        await save_user_state(
            update.effective_user.id,
            UserStateEnum.APPLICATION_EMAIL,
            ctx
        )
        await update.message.reply_text(
            "Укажите ваш email адрес:",
            reply_markup=get_always_available_keyboard()
        )
    
    elif state == UserStateEnum.APPLICATION_EMAIL:
        if text in ["⬅️ Назад", "❌ Отмена", "ℹ️ Главное меню"]:
            await handle_navigation(update, context, text)
            return
        
        ctx["application_email"] = text
        await save_user_state(
            update.effective_user.id,
            UserStateEnum.APPLICATION_CONTACT_METHOD,
            ctx
        )
        await update.message.reply_text(
            "Выберите предпочтительный способ связи для менеджера:",
            reply_markup=get_contact_method_keyboard()
        )
    
    elif state == UserStateEnum.APPLICATION_CONTACT_METHOD:
        if text in ["⬅️ Назад", "❌ Отмена", "ℹ️ Главное меню"]:
            await handle_navigation(update, context, text)
            return
        
        contact_methods = {
            "Телефонный звонок": "phone",
            "Email": "email",
            "Мессенджер": "messenger"
        }
        
        if text in contact_methods:
            ctx["application_contact_method"] = contact_methods[text]
            await save_user_state(
                update.effective_user.id,
                UserStateEnum.APPLICATION_CONFIRMATION,
                ctx
            )
            await show_application_summary(update, context, ctx)
        else:
            await update.message.reply_text(
                "Пожалуйста, выберите способ связи из предложенных вариантов.",
                reply_markup=get_contact_method_keyboard()
            )
    
    elif state == UserStateEnum.APPLICATION_CONFIRMATION:
        if text == "✅ Всё верно, отправить заявку":
            await complete_application(update, context, ctx)
        elif text == "✏️ Исправить данные":
            await save_user_state(
                update.effective_user.id,
                UserStateEnum.APPLICATION_FIO,
                ctx
            )
            await update.message.reply_text(
                "Начнем заново. Укажите ваше ФИО:",
                reply_markup=get_always_available_keyboard()
            )
        elif text == "❌ Отменить заявку":
            await save_user_state(update.effective_user.id, UserStateEnum.MAIN_MENU)
            await update.message.reply_text(
                "Заявка отменена.",
                reply_markup=get_main_menu_keyboard()
            )
        elif text in ["⬅️ Назад", "ℹ️ Главное меню"]:
            await handle_navigation(update, context, text)


async def show_application_summary(update: Update, context: ContextTypes.DEFAULT_TYPE, ctx: dict):
    """Показ сводки заявки для подтверждения"""
    product = ctx.get("application_product", {})
    summary = (
        "**Проверьте правильность данных:**\n\n"
        f"**Продукт:** {product.get('name', 'Не указан')}\n"
        f"**ФИО:** {ctx.get('application_fio', 'Не указано')}\n"
        f"**Телефон:** {ctx.get('application_phone', 'Не указан')}\n"
        f"**Email:** {ctx.get('application_email', 'Не указан')}\n"
        f"**Способ связи:** {ctx.get('application_contact_method', 'Не указан')}\n"
        f"**Предварительная стоимость:** {product.get('price', 0):,.0f} руб.\n"
    )
    
    await update.message.reply_text(
        summary,
        parse_mode='Markdown',
        reply_markup=get_final_confirmation_keyboard()
    )


async def complete_application(update: Update, context: ContextTypes.DEFAULT_TYPE, ctx: dict):
    """Завершение оформления заявки"""
    from database import serialize_json
    from notifications import notify_application_created
    product = ctx.get("application_product", {})
    
    # Сохранение заявки в БД
    async with async_session() as session:
        application = Application(
            user_id=update.effective_user.id,
            telegram_id=update.effective_user.id,
            product_type=product.get('key', 'unknown'),
            product_name=product.get('name', 'Unknown'),
            data=serialize_json(ctx),
            status='pending',
            calculated_price=product.get('price', 0),
            contact_method=ctx.get('application_contact_method', 'unknown')
        )
        session.add(application)
        await session.commit()
        application_id = application.id
    
    # Отправка уведомлений в CRM и Email (заглушки с логированием)
    await notify_application_created(application_id, {
        "product_name": product.get('name'),
        "product_type": product.get('key'),
        "price": product.get('price'),
        "fio": ctx.get('application_fio'),
        "phone": ctx.get('application_phone'),
        "email": ctx.get('application_email'),
        "contact_method": ctx.get('application_contact_method')
    })
    
    await save_user_state(
        update.effective_user.id,
        UserStateEnum.APPLICATION_COMPLETED,
        {"application_id": application_id}
    )
    
    contact_method_text = {
        "phone": "телефонному звонку",
        "email": "email",
        "messenger": "мессенджеру"
    }.get(ctx.get('application_contact_method', ''), "указанному способу")
    
    completion_text = (
        f"Отлично! Ваша заявка на \"{product.get('name', '')}\" успешно создана и передана менеджеру 🎉\n\n"
        f"В течение 15 минут с вами свяжутся по {contact_method_text} "
        f"для подтверждения деталей и завершения оформления.\n\n"
        f"**Номер вашей заявки:** #{application_id}"
    )
    
    await update.message.reply_text(
        completion_text,
        parse_mode='Markdown',
        reply_markup=get_application_completed_keyboard()
    )


async def handle_operator_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка запроса на оператора"""
    await save_user_state(update.effective_user.id, UserStateEnum.OPERATOR_REQUEST)
    
    operator_text = (
        "Вы запросили связь с оператором. "
        "Ваш запрос зарегистрирован и будет обработан в ближайшее время.\n\n"
        "Вы можете вернуться в главное меню или продолжить работу с ботом."
    )
    
    await update.message.reply_text(
        operator_text,
        reply_markup=get_main_menu_keyboard()
    )


async def handle_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Обработка навигационных команд"""
    if text == "⬅️ Назад":
        # Простая логика возврата на шаг назад
        state, ctx = await get_user_state(update.effective_user.id)
        # В реальности здесь должна быть более сложная логика
        await save_user_state(update.effective_user.id, UserStateEnum.MAIN_MENU)
        await update.message.reply_text(
            "Вы вернулись в главное меню.",
            reply_markup=get_main_menu_keyboard()
        )
    
    elif text == "❌ Отмена":
        await save_user_state(update.effective_user.id, UserStateEnum.MAIN_MENU)
        await update.message.reply_text(
            "Операция отменена. Вы вернулись в главное меню.",
            reply_markup=get_main_menu_keyboard()
        )
    
    elif text == "ℹ️ Главное меню":
        await save_user_state(update.effective_user.id, UserStateEnum.MAIN_MENU)
        await update.message.reply_text(
            "Вы вернулись в главное меню.",
            reply_markup=get_main_menu_keyboard()
        )
    
    elif text == "🆘 Помощь":
        await help_command(update, context)
    
    elif text == "👨‍💼 Оператор":
        await handle_operator_request(update, context)
