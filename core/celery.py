import os
from celery import Celery
from django.conf import settings

# Initialize Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')

# create a Celery instance
app = Celery('core')

# initialize Celery with Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically load tasks.py files from all Django apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)