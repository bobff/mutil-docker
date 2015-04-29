from __future__ import absolute_import

import os

from celery import Celery

from django.conf import settings
from celery.schedules import crontab
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mutil_docker.settings')

app = Celery('mutil_docker')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.update(
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
    BROKER_URL='django://',
    CELERYBEAT_SCHEDULE = {
	    # Executes every Monday morning at 7:30 A.M
	    'stop_container': {
	        'task': 'dockers.tasks.stop_container',
	        'schedule': crontab(minute=0, hour='*/2'),#crontab(), #  # execute every two hours
	        'args': (),
	    },
	    'delete_container': {
	        'task': 'dockers.tasks.delete_container',
	        'schedule': crontab(minute=0, hour='*/2'),  # execute every two hours
	        'args': (),
	    },
	},
	CELERY_TIMEZONE = 'PRC',
)




# see: http://celery.readthedocs.org/en/latest/userguide/periodic-tasks.html#crontab-schedules
# CELERY_TIMEZONE = 'UTC'



