"""
Django settings for hilichurlian_database_project project.

Generated by 'django-admin startproject' using Django 3.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/
# Settings for deployment
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'o46_3cpp947uxj-0mkoru)&7dugehc^-brm_204+t^r3*l*ia^')
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'not-secret')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
DEBUG = (os.environ.get('DJANGO_DEBUG', 'False') == 'True')

if DEBUG:
	ALLOWED_HOSTS = []
else:
	ALLOWED_HOSTS = ['hilichurlian-database.herokuapp.com']


# Application definition

INSTALLED_APPS = [
	'hilichurlian_database.apps.HilichurlianDatabaseConfig',
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
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
]

ROOT_URLCONF = 'hilichurlian_database_project.urls'

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

WSGI_APPLICATION = 'hilichurlian_database_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

IS_LOCAL = (os.environ.get('LOCAL_WORK', 'False') == 'True')

DATABASES = { 'default': {} }

if IS_LOCAL:
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.postgresql',
			'NAME': os.environ.get('POSTGRES_DB_NAME', 'mydatabase'),
			'USER': os.environ.get('POSTGRES_USER', 'mysuperuser'),
			'PASSWORD': os.environ.get('POSTGRES_PASS', 'mypassword'),
			'HOST': os.environ.get('POSTGRES_HOST', '127.0.0.1'),
			'PORT': os.environ.get('POSTGRES_POST', '5432'),
		}
	}
else:
	DATABASES['default'] = dj_database_url.config(conn_max_age=600)


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)