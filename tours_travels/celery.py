"""
Celery configuration for tours_travels project
"""

import os
import ssl
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tours_travels.settings')

app = Celery('tours_travels')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure SSL for Upstash Redis
app.conf.update(
    broker_use_ssl={
        'ssl_cert_reqs': ssl.CERT_REQUIRED,
        'ssl_ca_certs': None,
        'ssl_certfile': None,
        'ssl_keyfile': None,
    },
    redis_backend_use_ssl={
        'ssl_cert_reqs': ssl.CERT_REQUIRED,
        'ssl_ca_certs': None,
        'ssl_certfile': None,
        'ssl_keyfile': None,
    },
    # Task configuration
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task routing
    task_routes={
        'email_marketing.tasks.*': {'queue': 'email_marketing'},
    },
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Result backend configuration
    result_expires=3600,  # 1 hour
    result_backend_transport_options={
        'master_name': 'mymaster',
    },
)

@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery configuration"""
    print(f'Request: {self.request!r}')
    return 'Celery is working!'
