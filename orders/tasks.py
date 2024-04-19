
from celery import shared_task
from django.core.mail import send_mail
import logging


# Получаем экземпляр логгера Django, который был настроен в settings.py
logger = logging.getLogger('django')



@shared_task
def send_email_task(subject, message, email_from, recipient_list):
    logger.info('Отправка письма...')
    send_mail(subject, message, email_from, recipient_list)
    logger.info('Письмо отправлено.')