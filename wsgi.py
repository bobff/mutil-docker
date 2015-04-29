import os, sys

if not os.path.dirname(__file__) in sys.path[:1]:
    sys.path.insert(0, os.path.dirname(__file__))
os.environ['DJANGO_SETTINGS_MODULE'] = 'mutil_docker.settings'

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
