"""
Django settings for runcrunch project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import dj_database_url

if 'sferg' in os.path.expanduser('~'):
  import __docs__.__secrets__

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = 'sferg' in os.path.expanduser('~')

ALLOWED_HOSTS = [
  'runcrunch.fly.dev',
  'www.run-crunch.com'
]
if DEBUG:
  ALLOWED_HOSTS.extend([
    'localhost',
    '.ngrok.io'
  ])
CSRF_TRUSTED_ORIGINS = ['https://*.run-crunch.com']
DOMAIN = 'https://www.run-crunch.com'

# Application definition

INSTALLED_APPS = [
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.messages',
  'whitenoise.runserver_nostatic',
  'django.contrib.staticfiles',

  'app',
  'api',
  
  'django.contrib.admin',
  'django.contrib.auth',
  'storages',
]

MIDDLEWARE = [
  'django.middleware.security.SecurityMiddleware',
  'whitenoise.middleware.WhiteNoiseMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.common.CommonMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  'django.middleware.clickjacking.XFrameOptionsMiddleware',
  'app.middleware.athleteMiddleware',
]

ROOT_URLCONF = 'runcrunch.urls'

TEMPLATES = [
  {
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [ os.path.join(BASE_DIR, 'templates') ],
    'APP_DIRS': False,
    'OPTIONS': {
      'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
        "django.template.context_processors.request"
      ],
    },
  },
]

WSGI_APPLICATION = 'runcrunch.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
  'default': dj_database_url.config(conn_max_age=600, ssl_require=False)
}
DATABASES['default']['NAME'] = 'postgres'

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTHENTICATION_BACKENDS = [
  'django.contrib.auth.backends.ModelBackend',
]

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = False

X_FRAME_OPTIONS = 'SAMEORIGIN'
STATICFILES_FINDERS =  [
  'django.contrib.staticfiles.finders.FileSystemFinder',
  'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
AWS_STORAGE_BUCKET_NAME = 'runcrunch-static'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
  os.path.join(BASE_DIR, 'staticBase'),
  ('css', os.path.join(BASE_DIR, 'staticBase', 'css')),
  ('img', os.path.join(BASE_DIR, 'staticBase', 'img')),
]
if DEBUG:
  STATIC_URL = '/staticBase/'
  STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
  WHITENOISE_MANIFEST_STRICT = False
  STATIC_URL = f'https://{AWS_STORAGE_BUCKET_NAME}/'
  STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
else:
  STATIC_URL = f'https://{AWS_STORAGE_BUCKET_NAME}/'
  STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

LOGIN_REDIRECT_URL = '/dashboard'
LOGIN_URL = '/user/login'
LOGOUT_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = (
  'django.contrib.auth.backends.ModelBackend',
)

SITE_ID = 4
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# SMPT CONFIG
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'runcrunch.contact@gmail.com'
EMAIL_HOST_PASSWORD = os.environ['GMAIL_PW']

IMPORTER_SERVICE_FUNCTION_NAME = 'runcrunch-importer'
HEATMAP_SERVICE_FUNCTION_NAME = 'heatmap-generator'

# API Credentials
STRAVA_CLIENT_ID = os.environ['STRAVA_CLIENT_ID']
STRAVA_CLIENT_SECRET = os.environ['STRAVA_CLIENT_SECRET']
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_REGION_NAME = 'us-east-1'
AWS_POLYLINE_BUCKET_NAME = 'runcrunch-polyline'
AWS_HEATMAP_BUCKET_NAME = 'runcrunch-heatmap'
MAPBOX_TOKEN = os.environ['MAPBOX_TOKEN']
