"""Модуль для работы с базой данных"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from datetime import datetime
from config import DATABASE_URL
import json

Base = declarative_base()


class User(Base):
    """Модель пользователя"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    phone = Column(String(50))
    email = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)


class Application(Base):
    """Модель заявки на оформление полиса"""
    __tablename__ = 'applications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    telegram_id = Column(Integer, nullable=False)
    product_type = Column(String(100), nullable=False)
    product_name = Column(String(255), nullable=False)
    data = Column(Text)  # Все собранные данные в формате JSON (хранится как текст)
    status = Column(String(50), default='pending')  # pending, processed, completed
    calculated_price = Column(Float)
    contact_method = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


class UserState(Base):
    """Модель для хранения состояния пользователя в диалоге"""
    __tablename__ = 'user_states'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    state = Column(String(100))
    context = Column(Text)  # Дополнительные данные состояния (хранится как JSON текст)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Создание движка и сессии
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Инициализация базы данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session():
    """Получение сессии базы данных"""
    async with async_session() as session:
        yield session


def serialize_json(data):
    """Сериализация данных в JSON строку"""
    if data is None:
        return None
    return json.dumps(data, ensure_ascii=False)


def deserialize_json(data):
    """Десериализация JSON строки в словарь"""
    if data is None:
        return {}
    if isinstance(data, str):
        try:
            return json.loads(data)
        except:
            return {}
    return data
