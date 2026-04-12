import os
from pathlib import Path
from dotenv import load_dotenv # .env ফাইল লোড করার জন্য

# এনভায়রনমেন্ট ভেরিয়েবল লোড করা হচ্ছে
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# নিরাপত্তা: সিক্রেট কি কখনোই হার্ডকোড করবেন না, তবে আপাতত এটিই থাকলো
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-638@4z14i^*=3jpe%bq3@_)a$1i!#-q$w9kg_%5@7p098p1ax$')

# Render-এ ডেপ্লয় করলে DEBUG অবশ্যই False করা উচিত, তবে টেস্টিং এর জন্য True রাখা হলো
DEBUG = True

# Render-এ ডেপ্লয় করার জন্য '*' অথবা আপনার ডোমেইন নাম দিতে হবে
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'whitenoise.runserver_nostatic', # স্ট্যাটিক ফাইল হ্যান্ডেল করার জন্য
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # এটি যোগ করা হয়েছে স্ট্যাটিক ফাইলের জন্য
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

# ডেটাবেস কনফিগারেশন
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
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

# --- স্ট্যাটিক ফাইল কনফিগারেশন (WhiteNoise এর জন্য) ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
# Render এই ফোল্ডার থেকেই সব CSS/JS লোড করবে
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# স্ট্যাটিক ফাইল কম্প্রেস করার জন্য (WhiteNoise)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- মিডিয়া ফাইল কনফিগারেশন ---
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- লগইন ও রিডাইরেক্ট পাথ ---
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_REDIRECT_URL = 'farmer_dashboard'