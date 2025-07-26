"""
Development settings for Novustell Travel
Uses SQLite for local development
"""

from .settings import *
import os

# Development-specific settings
DEBUG = True

# Development database - SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_development.sqlite3',
    }
}

# Development email backend - Console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Development allowed hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Development static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles_dev'

# Development media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media_dev'

# Development logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'development.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'users': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'adminside': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# Development cache - Dummy cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Development session configuration
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Development security settings
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Development Uploadcare settings
UPLOADCARE = {
    'pub_key': os.getenv('UPLOADCARE_PUBLIC_KEY', 'demopublickey'),
    'secret': os.getenv('UPLOADCARE_SECRET_KEY', 'demosecretkey'),
}

# Development email settings
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025  # For development email server
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = 'noreply@localhost'
ADMIN_EMAIL = 'admin@localhost'

# Development site URL
SITE_URL = 'http://localhost:8000'

# Development WhatsApp settings
WHATSAPP_PHONE = '+254701363551'
WHATSAPP_MESSAGE_TEMPLATE = 'Hello! I have a question about my booking: {booking_reference}'

# Development debug toolbar (if installed)
if 'debug_toolbar' in INSTALLED_APPS:
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1', 'localhost']
    
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
        'SHOW_COLLAPSED': True,
    }

# Development performance settings
USE_TZ = True
TIME_ZONE = 'Africa/Nairobi'

# Development internationalization
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True

# Development file upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Development CORS settings (if needed)
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Development CSP settings (relaxed for development)
CSP_DEFAULT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'")
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'", "https:")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https:")
CSP_IMG_SRC = ("'self'", "data:", "https:")

print("🔧 Development settings loaded")
print(f"📁 Database: {DATABASES['default']['NAME']}")
print(f"📧 Email backend: {EMAIL_BACKEND}")
print(f"🌐 Site URL: {SITE_URL}")
print(f"📊 Debug mode: {DEBUG}")
