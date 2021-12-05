import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'data_extraction.settings.prod')

app = Celery('data_extraction')
app.config_from_object('django.conf:settings')

# Load task modules from all rejistered Django app configs.
app.autodiscover_tasks()