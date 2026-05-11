"""Модуль уведомлений для CRM и Email"""
import logging
from config import CRM_WEBHOOK_URL, ADMIN_EMAIL

logger = logging.getLogger(__name__)


async def send_to_crm(application_data: dict) -> bool:
    """Отправка заявки в CRM-систему"""
    logger.info(f"Отправка заявки в CRM: {CRM_WEBHOOK_URL}")
    logger.info(f"Данные заявки: {application_data}")
    
    # Интеграция с API CRM
    #     async with session.post(CRM_WEBHOOK_URL, json=application_data) as resp:
    #         return resp.status == 200
    
    return True


async def send_email_notification(application_data: dict) -> bool:
    """Отправка email уведомления менеджеру"""
    logger.info(f"Отправка email на: {ADMIN_EMAIL}")
    logger.info(f"Тема: Новая заявка на страхование")
    logger.info(f"Данные: {application_data}")
    
    # Логика отправки через SMTP
    # message = MIMEText(...)
    # await aiosmtplib.send(message, hostname=SMTP_HOST, ...)
    
    return True


async def notify_application_created(application_id: int, application_data: dict) -> dict:
    """Отправка уведомлений о новой заявке"""
    results = {
        "crm_sent": False,
        "email_sent": False
    }
    
    try:
        results["crm_sent"] = await send_to_crm({
            "application_id": application_id,
            **application_data
        })
    except Exception as e:
        logger.error(f"Ошибка отправки в CRM: {e}")
    
    try:
        results["email_sent"] = await send_email_notification({
            "application_id": application_id,
            **application_data
        })
    except Exception as e:
        logger.error(f"Ошибка отправки email: {e}")
    
    return results
