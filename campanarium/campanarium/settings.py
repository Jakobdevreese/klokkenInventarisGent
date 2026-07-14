"""
Django settings for the campanarium project (Ghent bell & carillon inventory).

Security-sensitive settings (secret key, debug, hosts, database credentials) are
read from environment variables so nothing secret is committed. Local defaults
keep development frictionless; set the env vars on the server for the beta test.
"""

import os
from pathlib import Path

from django.contrib.messages import constants as messages

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# --- Security --------------------------------------------------------------
# Override all three via environment variables in any real deployment.
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-=%3=og#w9vrg*dvyu0g41_s097i@a=n2ffi2ln13b%rf8px6&b',
)
DEBUG = os.environ.get('DEBUG', 'True').lower() not in ('false', '0', 'no', '')
# Comma-separated list, e.g. ALLOWED_HOSTS="klokken.example.be,192.168.0.10".
ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if h.strip()]
# Needed for HTTPS POST (forms) once served behind a TLS reverse proxy, e.g.
# CSRF_TRUSTED_ORIGINS="https://klokkeninventaris.sonataduo.com".
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()]


# --- Applications ----------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',        # GeoDjango: PointField on Tower
    'inventory',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'campanarium.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,  # loads inventory/templates/
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

WSGI_APPLICATION = 'campanarium.wsgi.application'


# --- Database (PostgreSQL + PostGIS) ---------------------------------------
# Credentials come from the environment. One-time server setup:
#   CREATE DATABASE campanarium;
#   \c campanarium
#   CREATE EXTENSION postgis;
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('DB_NAME', 'campanarium'),
        'USER': os.environ.get('DB_USER', 'campanarium'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}


# --- Authentication --------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# --- Internationalisation --------------------------------------------------
# Dutch (Belgium) so dates/months render in the site's language.
LANGUAGE_CODE = 'nl-be'
TIME_ZONE = 'Europe/Brussels'
USE_I18N = True
USE_TZ = True


# --- Static & media --------------------------------------------------------
# App-level static (inventory/static/) is found automatically; no STATICFILES_DIRS
# needed. STATIC_ROOT is only the collectstatic target for production.
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- Messages --------------------------------------------------------------
# Map Django's ERROR level to Bootstrap's "danger" so alert-{{ tag }} styles match.
MESSAGE_TAGS = {messages.ERROR: 'danger'}
