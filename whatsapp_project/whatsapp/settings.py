"""
Django settings for whatsapp project.

Generated by 'django-admin startproject' using Django 5.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/


This file contains the settings for configuring the Django web application, including database configurations, installed apps, middleware, templates, logging, authentication, and more.

Settings include:

- `BASE_DIR`: The base directory for the project, used for referencing paths.
- `SECRET_KEY`: A secret key for cryptographic signing. This should be kept secret and secure in production.
- `DEBUG`: A flag indicating whether the app is in development or production. Should be `False` in production.
- `ALLOWED_HOSTS`: A list of strings representing the host/domain names that this Django site can serve.
- `INSTALLED_APPS`: A list of strings representing the installed applications in the project, such as Django's built-in apps and custom apps.
- `MIDDLEWARE`: A list of middleware components that are used by Django to process requests and responses.
- `ROOT_URLCONF`: The URL configuration for the project, specifying where to find URL patterns.
- `TEMPLATES`: A list of settings for template rendering, including the backend and template directories.
- `DATABASES`: The configuration for the project's database, including the engine and location of the database file.
- `LOGIN_URL` and `LOGOUT_REDIRECT_URL`: URLs for user login and logout.
- `LOGGING`: Configuration for logging, including file handler and logging level.
- `AUTH_PASSWORD_VALIDATORS`: A list of password validation rules to enforce password complexity.
- `AUTHENTICATION_BACKENDS`: Specifies the authentication backend(s) for logging in users.
- `LANGUAGE_CODE`: The language code for the project (en-us for English).
- `TIME_ZONE`: The time zone used for the project (UTC by default).
- `USE_I18N`: Flag for enabling internationalization.
- `USE_TZ`: Flag for enabling time zone awareness.
- `STATIC_URL` and `STATICFILES_DIRS`: Configuration for serving static files.
- `AUTH_USER_MODEL`: A custom user model for the application, located in the `messaging` app.
- `STATIC_ROOT`: The directory to collect static files when running `collectstatic` in production (only used when `DEBUG=False`).
- `DEFAULT_AUTO_FIELD`: The default primary key field type (set to `BigAutoField` for large auto-incrementing fields).

Notes:
- This file contains sensitive information such as the `SECRET_KEY`, which should be kept secure.
- In production, `DEBUG` should be set to `False`, and proper security settings should be applied.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-97k4@$jx+^f#m@yti)(2^tjwmaph!_5@i_4(-=@2k13%#_5*%o'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'messaging',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'whatsapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "messaging", "templates", "messaging")],
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

WSGI_APPLICATION = 'whatsapp.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
LOGIN_URL = '/login/'
LOGOUT_REDIRECT_URL = 'login'

import os

# Make sure the logs directory exists
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'app.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
        'django': {  # Django logger
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'your_app_name': {  # Your application logger
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}




# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # Default backend
)

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

AUTH_USER_MODEL = 'messaging.User'

if DEBUG:
    STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
