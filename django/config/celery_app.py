from __future__ import absolute_import, unicode_literals

import os

from celery import Celery



# set the default Django settings module for the 'celery' program.

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
BASE_REDIS_URL = f"redis://{os.environ.get('REDIS_HOST','localhost')}:{os.environ.get('REDIS_PORT',6379)}/0"#os.environ.get('REDIS_URL', 'redis://')
TIME_ZONE=os.environ.get('TIME_ZONE', 'Europe/Kiev')
app = Celery('config')


# Using a string here means the worker doesn't have to serialize

# the configuration object to child processes.

# - namespace='CELERY' means all celery-related configuration keys

#   should have a `CELERY_` prefix.

app.config_from_object('django.conf:settings', namespace='CELERY')


# Load task modules from all registered Django app configs.

app.autodiscover_tasks()
app.conf.broker_url = BASE_REDIS_URL
app.conf.timezone = TIME_ZONE

@app.task(bind=True)
def debug_task(self):

    print('Request: {0!r}'.format(self.request))
