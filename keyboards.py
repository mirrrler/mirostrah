"""Модуль для создания клавиатур бота"""
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu_keyboard():
    """Главное меню"""
    keyboard = [
        ['📋 Подобрать страховой продукт'],
        ['ℹ️ Узнать о продуктах'],
        ['📝 Оформить заявку'],
        ['🆘 Помощь / Связаться с оператором']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_products_menu_keyboard():
    """Меню выбора продуктов для информации"""
    keyboard = [
        ['🚗 ОСАГО', '🚙 Каско'],
        ['🏠 Страхование жилья'],
        ['✈️ Страхование путешественников', '❤️ Страхование здоровья'],
        ['⬅️ Назад в главное меню']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_product_detail_keyboard(product_key: str):
    """Клавиатура для детальной информации о продукте"""
    keyboard = [
        ['🔎 Подробнее'],
        ['✅ Подобрать этот продукт'],
        ['⬅️ Назад']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_insurance_type_keyboard():
    """Выбор типа страхования"""
    keyboard = [
        ['🚗 Авто', '🏠 Недвижимость'],
        ['✈️ Путешествие', '❤️ Здоровье'],
        ['⬅️ Назад']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_auto_subtype_keyboard():
    """Выбор подтипа автострахования"""
    keyboard = [
        ['ОСАГО', 'Каско'],
        ['🤔 В чем разница?'],
        ['⬅️ Назад']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_priority_keyboard():
    """Выбор приоритета при подборе"""
    keyboard = [
        ['Максимальное покрытие'],
        ['Оптимальное соотношение цены и качества'],
        ['Минимальная стоимость'],
        ['⬅️ Назад']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_power_keyboard():
    """Быстрый выбор мощности автомобиля"""
    keyboard = [
        ['Менее 100 л.с.', '100-150 л.с.'],
        ['Более 150 л.с.'],
        ['⬅️ Назад']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_product_recommendation_keyboard(recommendations: list):
    """Клавиатура для выбора рекомендованного продукта"""
    buttons = []
    for i, rec in enumerate(recommendations):
        buttons.append([f'✅ Выбрать вариант {i+1}: {rec["name"]}'])
    buttons.append(['🔍 Сравнить все варианты'])
    buttons.append(['🔄 Подобрать заново'])
    buttons.append(['⬅️ Назад'])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def get_contact_method_keyboard():
    """Выбор способа связи"""
    keyboard = [
        ['Телефонный звонок', 'Email'],
        ['Мессенджер'],
        ['⬅️ Назад']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_phone_keyboard():
    """Кнопка для отправки номера телефона"""
    keyboard = [[KeyboardButton('📱 Отправить номер', request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


def get_confirmation_keyboard():
    """Подтверждение начала оформления"""
    keyboard = [
        ['Да, начать'],
        ['❌ Отмена']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_final_confirmation_keyboard():
    """Финальное подтверждение заявки"""
    keyboard = [
        ['✅ Всё верно, отправить заявку'],
        ['✏️ Исправить данные'],
        ['❌ Отменить заявку']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_application_completed_keyboard():
    """Клавиатура после оформления заявки"""
    keyboard = [
        ['🔄 Оформить еще один полис'],
        ['📞 Связаться с менеджером сейчас'],
        ['ℹ️ Главное меню']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_always_available_keyboard():
    """Критические кнопки, доступные почти всегда"""
    keyboard = [
        ['🆘 Помощь', '👨‍💼 Оператор'],
        ['⬅️ Назад', '❌ Отмена'],
        ['ℹ️ Главное меню']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# === НОВЫЕ КЛАВИАТУРЫ ===

def get_car_brand_keyboard():
    """Выбор марки автомобиля"""
    keyboard = [
        ['Toyota', 'Volkswagen'],
        ['Kia', 'Hyundai'],
        ['BMW', 'Mercedes'],
        ['Lada', 'Renault'],
        ['Другая марка'],
        ['⬅️ Назад']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_car_year_keyboard():
    """Выбор года выпуска автомобиля"""
    keyboard = [
        ['2020-2024', '2015-2019'],
        ['2010-2014', '2005-2009'],
        ['До 2005'],
        ['⬅️ Назад']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_housing_type_keyboard():
    """Выбор типа жилья"""
    keyboard = [
        ['🏢 Квартира', '🏠 Дом'],
        ['🏘️ Таунхаус', '🏗️ Другое'],
        ['⬅️ Назад']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_country_keyboard():
    """Выбор страны для путешествия"""
    keyboard = [
        ['🇪🇺 Шенген', '🇹🇷 Турция'],
        ['🇪🇬 Египет', '🇹🇭 Таиланд'],
        ['🇦🇪 ОАЭ', '🌍 Другая'],
        ['⬅️ Назад']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_age_keyboard():
    """Выбор возраста"""
    keyboard = [
        ['18-30 лет', '31-45 лет'],
        ['46-60 лет', 'Старше 60'],
        ['⬅️ Назад']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_budget_keyboard():
    """Выбор бюджета"""
    keyboard = [
        ['До 5 000 ₽', '5 000 - 15 000 ₽'],
        ['15 000 - 50 000 ₽', 'Более 50 000 ₽'],
        ['Бюджет не важен'],
        ['⬅️ Назад']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_skip_keyboard():
    """Клавиатура с возможностью пропустить шаг"""
    keyboard = [
        ['Пропустить'],
        ['⬅️ Назад']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

