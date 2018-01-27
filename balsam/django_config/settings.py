"""
Django settings for argobalsam project.

Generated by 'django-admin startproject' using Django 1.9.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import sys
import logging
from balsam.django_config import serverinfo, sqlite_client
from balsam.user_settings import *

logger = logging.getLogger(__name__)

# ---------------
# DATABASE SETUP
# ---------------
def resolve_db_path(path=None):
    if path:
        assert os.path.exists(path)
    elif os.environ.get('BALSAM_DB_PATH'):
        path = os.environ['BALSAM_DB_PATH']
        assert os.path.exists(path)
    else:
        path = default_db_path
    return path

def configure_db_backend(db_path):
    ENGINES = {
        'sqlite3' : 'django.db.backends.sqlite3',
    }
    NAMES = {
        'sqlite3' : 'db.sqlite3',
    }
    OPTIONS = {
        'sqlite3' : {'timeout' : 5000},
    }

    info = serverinfo.ServerInfo(db_path)
    db_type = info['db_type']
    user = info.get('user', '')
    password = info.get('password', '')
    db_name = os.path.join(db_path, NAMES[db_type])

    db = dict(ENGINE=ENGINES[db_type], NAME=db_name,
              OPTIONS=OPTIONS[db_type], USER=user, PASSWORD=password)

    DATABASES = {'default':db}
    return DATABASES

CONCURRENCY_ENABLED = True
BALSAM_PATH = resolve_db_path()
DATABASES = configure_db_backend(BALSAM_PATH)

# -----------------------
# SQLITE CLIENT SETUP
# ------------------------
is_server = os.environ.get('IS_BALSAM_SERVER')=='True'
using_sqlite = DATABASES['default']['ENGINE'].endswith('sqlite3')
SAVE_CLIENT = None

if using_sqlite and not is_server:
    SAVE_CLIENT = sqlite_client.Client(serverinfo.ServerInfo(BALSAM_PATH))
    if SAVE_CLIENT.serverAddr is None:
        logger.debug("SQLite client: writing straight to disk")
        SAVE_CLIENT = None
    else:
        logger.debug(f"SQL client: save() via {client.serverAddr}")

# --------------------
# SUBDIRECTORY SETUP
# --------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGGING_DIRECTORY = os.path.join(BALSAM_PATH , 'log') 
DATA_PATH = os.path.join(BALSAM_PATH ,'data')
BALSAM_WORK_DIRECTORY = os.path.join(DATA_PATH,'balsamjobs') # where to store local job data used for submission
ARGO_WORK_DIRECTORY = os.path.join(DATA_PATH,'argojobs')

for d in [
      BALSAM_PATH ,
      DATA_PATH,
      LOGGING_DIRECTORY,
      BALSAM_WORK_DIRECTORY,
      ARGO_WORK_DIRECTORY
]:
    if not os.path.exists(d):
        os.makedirs(d)

# ----------------
# LOGGING SETUP
# ----------------
HANDLER_FILE = os.path.join(LOGGING_DIRECTORY, LOG_FILENAME)
LOGGING = {
   'version': 1,
   'disable_existing_loggers': False,
   'formatters': {
      'standard': {
      'format' : '%(asctime)s|%(process)d|%(levelname)8s|%(name)s:%(lineno)s] %(message)s',
      'datefmt' : "%d-%b-%Y %H:%M:%S"
      },
   },
   'handlers': {
      'console': {
         'class':'logging.StreamHandler',
         'formatter': 'standard',
          'level' : 'DEBUG'
      },
      'default': {
         'level':LOG_HANDLER_LEVEL,
         'class':'logging.handlers.RotatingFileHandler',
         'filename': HANDLER_FILE,
         'maxBytes': LOG_FILE_SIZE_LIMIT,
         'backupCount': LOG_BACKUP_COUNT,
         'formatter': 'standard',
      }
   },
   'loggers': {
      'django':{
         'handlers': ['default'],
         'level': 'DEBUG',
         'propagate': True,
      },
      'balsam': {
         'handlers': ['default'],
         'level': 'DEBUG',
          'propagate': True,
      },
   }
}

def log_uncaught_exceptions(exctype, value, tb,logger=logger):
   logger.error(f"Uncaught Exception {exctype}: {value}",exc_info=(exctype,value,tb))
   logger = logging.getLogger('console')
   logger.error(f"Uncaught Exception {exctype}: {value}",exc_info=(exctype,value,tb))
sys.excepthook = log_uncaught_exceptions


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=gyp#o9ac0@w3&-^@a)j&f#_n-o=k%z2=g5u@z5+klmh_*hebj'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'balsam.service.apps.BalsamCoreConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'balsam.django_config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'balsam.django_config.wsgi.application'





# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
