"""
Production settings for Novustell Travel
Uses NeonDB PostgreSQL for production
"""

from .settings import *
import os
import dj_database_url

# Production-specific settings
DEBUG = False

# Production database - NeonDB PostgreSQL
DATABASES = {
    'default': dj_database_url.parse(
        os.getenv('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Production email backend - Mailtrap HTTP API
# NOTE: Using Mailtrap HTTP API instead of SMTP for better reliability
MAILTRAP_API_TOKEN = os.getenv('MAILTRAP_API_TOKEN', 'd766975d57a7ef1acf2f750a36247a37')

# Email addresses configuration
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'api')  # Keep for compatibility
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD','d766975d57a7ef1acf2f750a36247a37')  # Keep for compatibility
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'Novustell Travel <info@novustelltravel.com>')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'info@novustelltravel.com')
JOBS_EMAIL = os.getenv('JOBS_EMAIL', 'careers@novustelltravel.com')
NEWSLETTER_EMAIL = os.getenv('NEWSLETTER_EMAIL', 'news@novustelltravel.com')

# Production allowed hosts
ALLOWED_HOSTS = [
    'novustelltravel.onrender.com',
    'www.novustelltravel.com',
    'novustelltravel.com',
    '.onrender.com',
    os.getenv('RENDER_EXTERNAL_HOSTNAME', ''),
]

# Remove empty strings from ALLOWED_HOSTS
ALLOWED_HOSTS = [host for host in ALLOWED_HOSTS if host]

# Production static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Production media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Production logging
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
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/tmp/novustell.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'users': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'adminside': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Production cache - Redis (if available) or Database cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Production session configuration
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Production security settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Production Uploadcare settings
UPLOADCARE = {
    'pub_key': os.getenv('UPLOADCARE_PUBLIC_KEY'),
    'secret': os.getenv('UPLOADCARE_SECRET_KEY'),
}

# Production site URL
SITE_URL = os.getenv('SITE_URL', 'https://www.novustelltravel.com')

# Production WhatsApp settings
WHATSAPP_PHONE = os.getenv('WHATSAPP_PHONE', '+254701363551')
WHATSAPP_MESSAGE_TEMPLATE = 'Hello! I have a question about my booking: {booking_reference}'

# Production performance settings
USE_TZ = True
TIME_ZONE = 'Africa/Nairobi'

# Production internationalization
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True

# Production file upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB

# Production CORS settings
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://novustelltravel.onrender.com",
    "https://www.novustelltravel.com",
    "https://novustelltravel.com",
]
CORS_ALLOW_CREDENTIALS = True

# Production CSP settings
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com")
CSP_IMG_SRC = ("'self'", "data:", "https:", "https://ucarecdn.com")
CSP_FONT_SRC = ("'self'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com")
CSP_CONNECT_SRC = ("'self'", "https://api.uploadcare.com")

# Production error reporting
ADMINS = [
    ('Admin', os.getenv('ADMIN_EMAIL', 'info@novustelltravel.com')),
]
MANAGERS = ADMINS

# Production database connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 600
DATABASES['default']['OPTIONS'] = {
    'sslmode': 'require',
}

# Production middleware order (security first)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Production static files with WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = False

# Production compression
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Production template settings
TEMPLATES[0]['OPTIONS']['debug'] = False

# Production email error reporting
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_SUBJECT_PREFIX = '[Novustell Travel] '

# Production health check
HEALTH_CHECK_URL = '/health/'

# Production monitoring
SENTRY_DSN = os.getenv('SENTRY_DSN')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    
    sentry_logging = LoggingIntegration(
        level=logging.INFO,
        event_level=logging.ERROR
    )
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), sentry_logging],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment='production',
    )

print("🚀 Production settings loaded")
print(f"🌐 Site URL: {SITE_URL}")
print(f"📧 Mailtrap API Token: {MAILTRAP_API_TOKEN[:8]}...")
print(f"🔒 SSL redirect: {SECURE_SSL_REDIRECT}")
print(f"📊 Debug mode: {DEBUG}")
