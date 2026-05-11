"""Конфигурация бота"""
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@mirostrah.ru')
CRM_WEBHOOK_URL = os.getenv('CRM_WEBHOOK_URL', '')

# База данных
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///mirostrah_bot.db')
