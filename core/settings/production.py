# settings/production.py
import os
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    
    "trucktrack-frontend.vercel.app",
    "www.trucktrack-frontend.vercel.app",
    # 'yourdomain.com',
    # 'www.yourdomain.com',
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


# Database - PostgreSQL for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'truck'),
        'USER': os.environ.get('DB_USER', 'trucker'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'trucker_123'),
        'HOST': os.environ.get('DB_HOST', '0.0.0.0'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# CELERY for production
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://redis:6379')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://redis:6379')

# Channel layer configuration (Redis is used)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [os.environ.get('REDIS_URL', 'redis://redis:6379')],
        },
    },
}

# CORS SETTINGS for production
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "https://trucktrack-frontend.vercel.app/",
    "https://www.trucktrack-frontend.vercel.app/",
    "https://trucktrack.publicvm.com",
    "https://www.trucktrack.publicvm.com",
]



# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'



# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/django.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}