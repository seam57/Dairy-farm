import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# .env ফাইল লোড করা
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# নিরাপত্তা: Render-এ পরিবেশ চলক থেকে সিক্রেট কি নেওয়া
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-default-key-change-this')

# Render-এ DEBUG False রাখা নিরাপদ
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['livestock-pro.onrender.com', '127.0.0.1', 'localhost']

# Add dynamic host for Render
RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL')
if RENDER_EXTERNAL_URL:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_URL)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'whitenoise.runserver_nostatic',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # অবশ্যই SecurityMiddleware এর নিচে থাকবে
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'livestock_project.urls'

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

WSGI_APPLICATION = 'livestock_project.wsgi.application'

# Database configuration for Render (PostgreSQL)
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- স্ট্যাটিক ফাইল কনফিগারেশন ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# এটি খুব গুরুত্বপূর্ণ: যদি আপনার প্রজেক্টে 'static' ফোল্ডারটি না থাকে, তবে এরর দিবে। 
# তাই চেক করে নিচ্ছি ফোল্ডারটি আছে কি না।
STATICFILES_DIRS = []
if os.path.exists(os.path.join(BASE_DIR, "static")):
    STATICFILES_DIRS.append(os.path.join(BASE_DIR, "static"))

# স্ট্যাটিক ফাইল স্টোরেজ (WhiteNoise)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_REDIRECT_URL = 'farmer_dashboard'