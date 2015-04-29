"""
Django settings for mutil_docker project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

#ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dockers',
    'api',
    'network',
    'djcelery',
    'kombu.transport.django',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django.middleware.cache.CacheMiddleware',
)

ROOT_URLCONF = 'mutil_docker.urls'

WSGI_APPLICATION = 'mutil_docker.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',# Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'mutil_docker',    # Or path to database file if using sqlite3.
        'USER': 'root',       # Not used with sqlite3.
        'PASSWORD': 'root',       # Not used with sqlite3.
        'HOST': '127.0.0.1',  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'PRC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TEMPLATE_CONTEXT_PROCESSORS=(
    "django.core.context_processors.request",
    "django.contrib.auth.context_processors.auth",
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_PATH = './site_media'
STATIC_ROOT = STATIC_PATH + '/static'

CERTIFICATE_PATH = '/home/bobfu/.docker'

API_SECRET_KEY = '#$%^&*(I%%&^*(%^&(*POkjhgty6789uoiJHGT^%&*IOKJHGTt'
API_USER = 'apiuser'
API_PWD  = 'apipwd'
API_TIME_OUT = 9999

DOCKER_HUB_HOST = '10.0.0.100'
DOCKER_HUB_PORT = 5000

DOCKER_IMAGE_ROOT_PWD = 'dockerrootpwd'

DOCKER_DEFAULT_USER = 'duser'
DOCKER_DEFAULT_PWD = '123123'

BROKER_URL = 'django://'

SESSION_EXPIRE_AT_BROWSER_CLOSE=False