from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Указываем дефолтные настройки Django для файла 'celery.py'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'herbdonbass.settings')

app = Celery('herbdonbass')

# Пространство имен 'CELERY' означает, что все конфигурационные ключи должны быть указаны с этим префиксом.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Загрузка задач из всех зарегистрированных приложений Django.
app.autodiscover_tasks()
