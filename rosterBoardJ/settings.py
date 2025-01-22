"""
Django settings for rosterBoardJ project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os, sentry_sdk, dj_database_url
from pathlib import Path
from decouple import Config, Csv, RepositoryEnv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

if (os.path.isdir(os.getcwd()+"/config")):
    config = Config(RepositoryEnv(os.getcwd()+"/config/settings.ini"))
else:
    from decouple import config

LOGIN_REDIRECT_URL = '/'

# SECURITY WARNING: don't run with debug turned on in production!
SECRET_KEY = config("SECRET_KEY")
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('APP_DEBUG') == 'true'

ALLOW_REGISTRATION = config('ALLOW_REGISTRATION') == 'true'

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# Application definition

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'colorfield',
    'fontawesomefree',
    'whitenoise',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'django_select2',
    'crispy_forms',
    'crispy_bootstrap5',
    'roster.apps.RosterConfig'
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

CRISPY_TEMPLATE_PACK = "bootstrap5"

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'rosterBoardJ.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'rosterboardJ.context_processors.get_domain',
            ],
        },
    },
]

WSGI_APPLICATION = 'rosterBoardJ.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.parse(
        url=config('DATABASE_URL'),
        conn_max_age=600,
    )
}

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv())

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": config('CHANNEL_LAYERS_REDIS_URLS', cast=Csv()),
        },
    },
}


USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

