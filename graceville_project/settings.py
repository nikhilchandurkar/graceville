"""
Django settings for graceville_project project.
Grace Ville - Luxury Private Villa & Nature Sanctuary.
"""

import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env if present
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-xnoqfbwn&_##acq65sg4a)2+5!b6g%po2&j0z4mywmttyp+c#o')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

raw_allowed_hosts = os.environ.get('ALLOWED_HOSTS', '*')
ALLOWED_HOSTS = [h.strip() for h in raw_allowed_hosts.split(',') if h.strip()]
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ['*']

# CSRF Trusted Origins for Vercel and custom domains
raw_csrf = os.environ.get('CSRF_TRUSTED_ORIGINS', 'https://*.vercel.app,http://localhost:8000,http://127.0.0.1:8000')
CSRF_TRUSTED_ORIGINS = [c.strip() for c in raw_csrf.split(',') if c.strip()]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'villa.apps.VillaConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise for production static file serving
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'graceville_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'villa.context_processors.whatsapp_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'graceville_project.wsgi.application'

# Database Configuration
# Supports:
# 1. External PostgreSQL via DATABASE_URL (e.g. Neon.tech, Supabase, Vercel Postgres)
# 2. Vercel Serverless SQLite with automatic copy to /tmp/db.sqlite3
# 3. Local SQLite for development
database_url = os.environ.get('DATABASE_URL')
if database_url:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(default=database_url, conn_max_age=600, ssl_require=True)
    }
else:
    IS_VERCEL = bool(os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'))
    if IS_VERCEL:
        tmp_db = Path('/tmp/db.sqlite3')
        local_db = BASE_DIR / 'db.sqlite3'
        if not tmp_db.exists() and local_db.exists():
            try:
                shutil.copyfile(local_db, tmp_db)
                os.chmod(tmp_db, 0o666)
            except Exception:
                pass
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': str(tmp_db),
            }
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images, Webfonts, Videos)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email / SMTP Configuration
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False').lower() in ('true', '1', 'yes')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'Grace Ville <reservations@graceville.in>')

# Notification Receiver Emails (Supports comma-separated emails, e.g. xyz@gmail.com,owner@graceville.in)
NOTIFICATION_RECEIVER_EMAIL = os.environ.get('NOTIFICATION_RECEIVER_EMAIL', '')

# WhatsApp Host / Concierge Phone (International format without '+' sign)
WHATSAPP_PHONE = os.environ.get('WHATSAPP_PHONE', '917768956163')
OWNER_PHONE = os.environ.get('OWNER_PHONE', '919699825732')
