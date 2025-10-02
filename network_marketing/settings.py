import os
from pathlib import Path
import dj_database_url 
from dotenv import load_dotenv
import os
load_dotenv()
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'your-secret-key-change-this-in-production'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'widget_tweaks'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
]

ROOT_URLCONF = 'network_marketing.urls'

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

WSGI_APPLICATION = 'network_marketing.wsgi.application'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "Ayurvedics",
        "USER": "postgres",
        "PASSWORD": "Gouse@1725",
        "HOST": "localhost",
        "PORT": "5432",
    }
}


AUTH_USER_MODEL = 'core.CustomUser'

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "core/static"]
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = 'your-email@example.com'
EMAIL_HOST = 'smtp.example.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'abdulgouse757@gmail.com'
EMAIL_HOST_PASSWORD = 'fzyr cmyg dckz yivs'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# settings.py
OWNER_UPI_ID = "gouse1725@ibl"  # Replace with your actual UPI ID
OWNER_MOBILE_NO = "+919491309768"  # Replace with actual mobile number
OWNER_EMAIL = "abdulgouse757@gmail.com"  # Replace with actual email


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'abdulgouse757@gmail.com'
EMAIL_HOST_PASSWORD = 'fzyr cmyg dckz yivs'
DEFAULT_FROM_EMAIL = 'abdulgouse757@gmail.com'


MSG91_AUTH_KEY = os.getenv("MSG91_AUTH_KEY")
MSG91_SENDER_ID = os.getenv("MSG91_SENDER_ID")


# PayU Configuration
# ...existing code...
PAYU_MERCHANT_KEY = config(
    "PAYU_MERCHANT_KEY", default="gtKFFx"
)  # Test key for MID 8854378
PAYU_MERCHANT_SALT = config(
    "PAYU_MERCHANT_SALT", default="4R38IvwiV57FwVpsgOvTXBdLE4tHUXFW"
)  # <-- Correct test salt
PAYU_BASE_URL = config(
    "PAYU_BASE_URL", default="https://test.payu.in/_payment"
)  # Test environment
# ...existing code...
PAYU_SUCCESS_URL = config("PAYU_SUCCESS_URL", default="https://network-marketing-7llt.onrender.com/checkout/success/")
PAYU_FAILURE_URL = config("PAYU_FAILURE_URL", default="https://network-marketing-7llt.onrender.com/checkout/failure/")


CONTACT_EMAIL = "abdulgouse757@gmail.com"  # Replace with actual email
OWNER_EMAIL = "abdulgouse757@gmail.com"  # Replace with actual owner email
OWNER_MOBILE_NO = "9491309768"  # Replace with actual owner mobile number
