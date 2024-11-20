"""
Django settings for IRIS project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import pymysql
import os
from . import config

pymysql.install_as_MySQLdb()

FIELD_ENCRYPTION_KEY = config.field_encryption_key

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

OPENAI_API_KEY = config.open_api_key
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.secret_key

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
ALLOWED_HOSTS = []
LOGIN_URL = '/mainApp/'
LOGIN_REDIRECT_URL = '/mainApp/ruleOTP'
LOGOUT_REDIRECT_URL = '/mainApp/'
AUTH_USER_MODEL = 'mainApp.CustomUser'
EMAIL_HOST_USER = config.email_host_user
EMAIL_HOST_PASSWORD = config.email_host_password
EMAIL_HOST = config.cus_host
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
ALLOWED_HOSTS = []
EMAIL_PORT = config.email_port



# Application definition

GET_USERS = config.get_users
GET_USER_OBJECTS = config.get_user_objects
OBJECT_GET_LOCATIONS = config.object_get_locations
API_SHARE = config.api_share
CUS_USERNAME = config.cus_username
CUS_PASSWORD = config.cus_password
CUS_HOST = 'email-smtp.us-east-1.amazonaws.com'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'encrypted_model_fields',
    'chatterbot.ext.django_chatterbot',
    'mainApp',
    'rest_framework',
    'IRIS',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication'
    )
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_session_timeout.middleware.SessionTimeoutMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = True
SESSSION_COOCKIE_SECURE = True

SESSION_EXPIRE_SECONDS = 1800
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_TIMEOUT_REDIRECT = '/mainApp/'

ROOT_URLCONF = 'IRIS.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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


WSGI_APPLICATION = 'IRIS.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


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

DATABASES = config.database

CHATTERBOT =  {
    'name': 'ChatterBot',
    'logic_adapters': [
        {  'import_path': 'chatterbot.logic.BestMatch' },
        {  'import_path': 'chatterbot.logic.TimeLogicAdapter' },
        {  'import_path': 'chatterbot.logic.MathematicalEvaluation' },
    ],
    'storage_adapters' : [
        
    ]
}
    
    
    

SESSION_EXPIRE_AT_BROWSER_CLOSE = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'statics/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'statics'),  # Update this path to point to your static folder
]
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'