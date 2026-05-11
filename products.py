"""Модуль с информацией о страховых продуктах"""
from typing import Dict, List, Optional

PRODUCTS_INFO = {
    'osago': {
        'name': 'ОСАГО',
        'description': 'Обязательное страхование автогражданской ответственности. Защищает от финансовых потерь при ДТП.',
        'full_description': '''ОСАГО (Обязательное страхование автогражданской ответственности) — это обязательный вид страхования для всех владельцев транспортных средств.

Что покрывает:
• Ущерб, причиненный третьим лицам в результате ДТП
• Вред здоровью и жизни пострадавших
• Повреждение имущества других участников дорожного движения

Что НЕ покрывает:
• Ущерб вашему автомобилю
• Ущерб, причиненный умышленно
• Ущерб при управлении в нетрезвом виде

Основные условия:
• Минимальная сумма выплаты: 400 000 руб. (имущество), 500 000 руб. (жизнь и здоровье)
• Срок действия: 1 год
• Франшиза: отсутствует''',
        'coverage': ['Ущерб третьим лицам', 'Вред здоровью', 'Повреждение имущества'],
        'not_covered': ['Ущерб вашему автомобилю', 'Умышленный ущерб', 'Управление в нетрезвом виде'],
        'franchise': 'Отсутствует'
    },
    'kasko': {
        'name': 'Каско',
        'description': 'Добровольное страхование автомобиля от ущерба, хищения и угона. Полная защита вашего транспортного средства.',
        'full_description': '''Каско — добровольное страхование автомобиля от различных рисков.

Что покрывает:
• Ущерб от ДТП (включая ваш автомобиль)
• Угон и хищение
• Повреждения от стихийных бедствий
• Повреждения от противоправных действий третьих лиц
• Пожар, взрыв

Что НЕ покрывает:
• Естественный износ
• Ущерб при управлении в нетрезвом виде
• Ущерб при отсутствии водительского удостоверения

Основные условия:
• Сумма страхования: по стоимости автомобиля
• Срок действия: 1 год
• Франшиза: от 0% до 15% (влияет на стоимость)''',
        'coverage': ['Ущерб от ДТП', 'Угон и хищение', 'Стихийные бедствия', 'Пожар'],
        'not_covered': ['Естественный износ', 'Управление в нетрезвом виде'],
        'franchise': '0-15%'
    },
    'property': {
        'name': 'Страхование жилья',
        'description': 'Защита вашего дома или квартиры от пожара, затопления, кражи и других рисков.',
        'full_description': '''Страхование жилья — защита вашей недвижимости от различных рисков.

Что покрывает:
• Пожар, взрыв
• Затопление
• Кража со взломом
• Стихийные бедствия
• Повреждения от падения деревьев, летательных аппаратов

Что НЕ покрывает:
• Естественный износ
• Умышленные действия
• Военные действия

Основные условия:
• Сумма страхования: по стоимости имущества
• Срок действия: 1 год
• Франшиза: от 0% до 5%''',
        'coverage': ['Пожар', 'Затопление', 'Кража', 'Стихийные бедствия'],
        'not_covered': ['Естественный износ', 'Умышленные действия'],
        'franchise': '0-5%'
    },
    'travel': {
        'name': 'Страхование путешественников',
        'description': 'Медицинская страховка для поездок за границу. Обязательна для получения визы во многие страны.',
        'full_description': '''Страхование путешественников — защита вашего здоровья во время поездок.

Что покрывает:
• Медицинские расходы за границей
• Эвакуация и репатриация
• Экстренная стоматология
• Поисково-спасательные работы
• Отмена поездки (опционально)

Что НЕ покрывает:
• Хронические заболевания (без декларирования)
• Экстремальные виды спорта (без доплаты)
• Алкогольное опьянение

Основные условия:
• Сумма покрытия: от 30 000 до 100 000 USD
• Срок действия: по длительности поездки
• Франшиза: обычно отсутствует''',
        'coverage': ['Медицинские расходы', 'Эвакуация', 'Стоматология', 'Поисково-спасательные работы'],
        'not_covered': ['Хронические заболевания', 'Экстремальный спорт'],
        'franchise': 'Отсутствует'
    },
    'health': {
        'name': 'Страхование здоровья',
        'description': 'Добровольное медицинское страхование для защиты вашего здоровья и здоровья вашей семьи.',
        'full_description': '''Страхование здоровья — комплексная защита вашего здоровья.

Что покрывает:
• Амбулаторное лечение
• Стационарное лечение
• Стоматология (опционально)
• Экстренная помощь
• Профилактические осмотры

Что НЕ покрывает:
• Заболевания, существовавшие до начала страхования (без декларирования)
• Косметические процедуры
• Нетрадиционная медицина

Основные условия:
• Сумма покрытия: от 100 000 до 5 000 000 руб.
• Срок действия: 1 год
• Франшиза: от 0% до 10%''',
        'coverage': ['Амбулаторное лечение', 'Стационар', 'Стоматология', 'Профилактика'],
        'not_covered': ['Косметические процедуры', 'Нетрадиционная медицина'],
        'franchise': '0-10%'
    }
}


def get_product_info(product_key: str) -> Optional[Dict]:
    """Получить информацию о продукте"""
    return PRODUCTS_INFO.get(product_key)


def get_all_products() -> Dict:
    """Получить все продукты"""
    return PRODUCTS_INFO


def calculate_price(product_type: str, data: Dict) -> float:
    """Расчет стоимости полиса"""
    base_prices = {
        'osago': 5000,
        'kasko': 50000,
        'property': 10000,
        'travel': 2000,
        'health': 30000
    }
    
    base_price = base_prices.get(product_type, 10000)
    
    if product_type == 'osago':
        # Для ОСАГО учитываем мощность
        power = data.get('power', 100)
        if power < 100:
            multiplier = 0.8
        elif power <= 150:
            multiplier = 1.0
        else:
            multiplier = 1.5
        return base_price * multiplier
    
    elif product_type == 'kasko':
        # Для Каско учитываем стоимость автомобиля
        car_value = data.get('car_value', 1000000)
        multiplier = car_value / 1000000
        return base_price * multiplier
    
    elif product_type == 'property':
        # Для недвижимости учитываем площадь
        area = data.get('area', 50)
        multiplier = area / 50
        return base_price * multiplier
    
    elif product_type == 'travel':
        # Для путешествий учитываем длительность
        days = data.get('days', 7)
        return base_price * (days / 7)
    
    elif product_type == 'health':
        # Для здоровья учитываем возраст
        age = data.get('age', 30)
        if age < 30:
            multiplier = 0.8
        elif age <= 50:
            multiplier = 1.0
        else:
            multiplier = 1.3
        return base_price * multiplier
    
    return base_price


def recommend_products(survey_data: Dict) -> List[Dict]:
    """
    Рекомендация продуктов на основе опроса
    Возвращает 1-3 наиболее подходящих продукта
    """
    recommendations = []
    
    insurance_type = survey_data.get('insurance_type')
    priority = survey_data.get('priority', 'optimal')
    
    if insurance_type == 'auto':
        sub_type = survey_data.get('auto_subtype', 'osago')
        if sub_type == 'osago':
            recommendations.append({
                'key': 'osago',
                'name': 'ОСАГО Базовый',
                'price': calculate_price('osago', survey_data),
                'description': 'Стандартное обязательное страхование'
            })
            if priority == 'maximum':
                recommendations.append({
                    'key': 'osago',
                    'name': 'ОСАГО Расширенный',
                    'price': calculate_price('osago', survey_data) * 1.2,
                    'description': 'С дополнительными опциями'
                })
        else:
            recommendations.append({
                'key': 'kasko',
                'name': 'Каско Стандарт',
                'price': calculate_price('kasko', survey_data),
                'description': 'Полная защита вашего автомобиля'
            })
            if priority == 'maximum':
                recommendations.append({
                    'key': 'kasko',
                    'name': 'Каско Премиум',
                    'price': calculate_price('kasko', survey_data) * 1.3,
                    'description': 'Максимальное покрытие без франшизы'
                })
    
    elif insurance_type == 'property':
        recommendations.append({
            'key': 'property',
            'name': 'Страхование жилья Базовое',
            'price': calculate_price('property', survey_data),
            'description': 'Защита от основных рисков'
        })
        if priority == 'maximum':
            recommendations.append({
                'key': 'property',
                'name': 'Страхование жилья Расширенное',
                'price': calculate_price('property', survey_data) * 1.25,
                'description': 'Расширенное покрытие всех рисков'
            })
    
    elif insurance_type == 'travel':
        recommendations.append({
            'key': 'travel',
            'name': 'Страхование путешественников',
            'price': calculate_price('travel', survey_data),
            'description': 'Медицинская страховка для поездок'
        })
    
    elif insurance_type == 'health':
        recommendations.append({
            'key': 'health',
            'name': 'Страхование здоровья Стандарт',
            'price': calculate_price('health', survey_data),
            'description': 'Базовое медицинское страхование'
        })
        if priority == 'maximum':
            recommendations.append({
                'key': 'health',
                'name': 'Страхование здоровья Премиум',
                'price': calculate_price('health', survey_data) * 1.4,
                'description': 'Расширенное медицинское покрытие'
            })
    
    # Сортируем по приоритету пользователя
    if priority == 'minimum':
        recommendations.sort(key=lambda x: x['price'])
    elif priority == 'maximum':
        recommendations.sort(key=lambda x: x['price'], reverse=True)
    
    return recommendations[:3]  # Возвращаем максимум 3 варианта
