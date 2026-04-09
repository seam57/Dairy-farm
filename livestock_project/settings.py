import os
from pathlib import Path

# ১. আগে BASE_DIR ডিফাইন করা হয়েছে
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-638@4z14i^*=3jpe%bq3@_)a$1i!#-q$w9kg_%5@7p098p1ax$'

DEBUG = True

ALLOWED_HOSTS = []

# ২. অ্যাপস কনফিগারেশন
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
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

ROOT_URLCONF = 'livestock_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'livestock_project.wsgi.application'

# ৩. ডাটাবেস
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ৪. পাসওয়ার্ড ভ্যালিডেশন
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# ৫. ভাষা ও সময়
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ৬. স্ট্যাটিক ফাইল কনফিগারেশন (সঠিকভাবে সাজানো)
STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / "accounts" / "static",
]

# প্রোডাকশনের জন্য কালেক্ট স্ট্যাটিক (ঐচ্ছিক)
STATIC_ROOT = BASE_DIR / "staticfiles"

# ৭. মিডিয়া ফাইল (ছবি আপলোডের জন্য)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ৮. লগইন/লগআউট রিডাইরেক্ট
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_REDIRECT_URL = 'farmer_dashboard'