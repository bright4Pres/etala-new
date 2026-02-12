import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lims_portal.settings')

app = Celery('lims_portal')

# Load configuration from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Define periodic tasks
app.conf.beat_schedule = {}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
