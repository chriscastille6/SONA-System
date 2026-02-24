"""
Django settings for Research Participant Recruitment System.
"""
import os
from pathlib import Path
from decouple import config, Csv, Config, RepositoryEnv
import dj_database_url

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from project root so it's used regardless of CWD (e.g. systemd/gunicorn)
_env_file = BASE_DIR / ".env"
if _env_file.exists():
    _config = Config(RepositoryEnv(str(_env_file)))
else:
    _config = config

# Security
DEBUG = _config('DEBUG', default=False, cast=bool)
_SECRET_KEY = _config('SECRET_KEY', default=None)
if not DEBUG and not _SECRET_KEY:
    raise RuntimeError('SECRET_KEY must be set in environment (e.g. .env) for production.')
SECRET_KEY = _SECRET_KEY or 'django-insecure-change-me-in-production'
ALLOWED_HOSTS = _config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# Railway.app deployment support
RAILWAY_ENVIRONMENT = _config('RAILWAY_ENVIRONMENT', default=None)
if RAILWAY_ENVIRONMENT:
    ALLOWED_HOSTS.append('.railway.app')
    # Trust Railway's proxy headers
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Render.com deployment support
RENDER_ENVIRONMENT = _config('RENDER', default=None)
if RENDER_ENVIRONMENT:
    ALLOWED_HOSTS.append('.onrender.com')
    # Trust Render's proxy headers
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# AI Review Feature Gating
AI_REVIEW_ENABLED = _config('AI_REVIEW_ENABLED', default='True', cast=bool)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'django_filters',
    'corsheaders',
    'django_celery_beat',
    'django_celery_results',
    'django_htmx',
    
    # Local apps
    'apps.accounts',
    'apps.courses',
    'apps.prescreening',
    'apps.studies',
    'apps.credits',
    'apps.reporting',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
                'config.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=_config('DATABASE_URL', default='postgresql://postgres:postgres@localhost:5432/recruitment_db'),
        conn_max_age=600
    )
}

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
USE_I18N = True
USE_TZ = True

# URL Prefix (for deployment behind /hsirb/ path)
# Only set if explicitly configured (for campus server deployment)
FORCE_SCRIPT_NAME = _config('FORCE_SCRIPT_NAME', default=None)

# Static files (CSS, JavaScript, Images)
# Auto-detect if we're on campus server and adjust URLs
if 'bayoupal.nicholls.edu' in ALLOWED_HOSTS:
    STATIC_URL = '/hsirb/static/'
    MEDIA_URL = '/hsirb/media/'
else:
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_ROOT = BASE_DIR / 'media'

# AI IRB Review Configuration
# Provider: 'openai' | 'anthropic' | 'ollama' | 'gemini'
IRB_AI_PROVIDER = _config('IRB_AI_PROVIDER', default='openai')
ANTHROPIC_API_KEY = _config('ANTHROPIC_API_KEY', default='')
OPENAI_API_KEY = _config('OPENAI_API_KEY', default='')
GEMINI_API_KEY = _config('GEMINI_API_KEY', default='')
# For provider='ollama': base URL of Ollama server (e.g. http://localhost:11434 or http://bayoupal:11434)
IRB_AI_OLLAMA_BASE_URL = _config('IRB_AI_OLLAMA_BASE_URL', default='http://localhost:11434')
# For provider='gemini': seconds to wait between agent calls (Free Tier: Flash 10 RPM, Pro 2 RPM)
IRB_AI_GEMINI_RATE_LIMIT_DELAY = _config('IRB_AI_GEMINI_RATE_LIMIT_DELAY', default='6', cast=int)
# Model: provider-specific model IDs (e.g. gpt-4o, claude-3-5-sonnet, gemini-2.5-flash)
IRB_AI_MODEL = _config('IRB_AI_MODEL', default='gpt-4o')
IRB_REVIEW_STORAGE = 'media/irb_reviews/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email Configuration
EMAIL_BACKEND = _config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = _config('EMAIL_HOST', default='')
EMAIL_PORT = _config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = _config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = _config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = _config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = _config('DEFAULT_FROM_EMAIL', default='noreply@university.edu')

# Celery Configuration
CELERY_BROKER_URL = _config('CELERY_BROKER_URL', default='django://')
CELERY_RESULT_BACKEND = _config('CELERY_RESULT_BACKEND', default='django-db')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# CORS Settings
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = _config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000', cast=Csv())

# Site Configuration
SITE_NAME = _config('SITE_NAME', default='Participant Recruitment and Management System')
SITE_URL = _config('SITE_URL', default='http://localhost:8000')
INSTITUTION_NAME = _config('INSTITUTION_NAME', default='Nicholls State University')

# Participant Information & Consent document (full doc at /studies/participant-information/)
# Used on the assessment platform "Your Rights and Options" page → "Read full participant information document"
PLATFORM_NAME = _config('PLATFORM_NAME', default=None)  # Defaults to SITE_NAME in view
IRB_PROTOCOL_NUMBER = _config('IRB_PROTOCOL_NUMBER', default='To be assigned')
PLATFORM_SUPPORT_EMAIL = _config('PLATFORM_SUPPORT_EMAIL', default='Christopher Castille (christopher.castille@nicholls.edu)')
PARTICIPANT_INFO_PI_NAME = _config('PARTICIPANT_INFO_PI_NAME', default='Christopher Castille')
PARTICIPANT_INFO_PI_EMAIL = _config('PARTICIPANT_INFO_PI_EMAIL', default='christopher.castille@nicholls.edu')
PARTICIPANT_INFO_PI_PHONE = _config('PARTICIPANT_INFO_PI_PHONE', default='')
IRB_OFFICE_NAME = _config('IRB_OFFICE_NAME', default='Dr. Alaina Daigle, Chair of the Committee, 168 Ayo Hall')
IRB_OFFICE_PHONE = _config('IRB_OFFICE_PHONE', default='985-448-4697')
IRB_OFFICE_EMAIL = _config('IRB_OFFICE_EMAIL', default='alania.daigle@nicholls.edu')

# Research exports: system-specific salt for anonymized participant IDs (prevents cross-database linkage)
PARTICIPANT_EXPORT_SALT = _config('PARTICIPANT_EXPORT_SALT', default=None)

# Policy Settings
CANCELLATION_WINDOW_HOURS = _config('CANCELLATION_WINDOW_HOURS', default=2, cast=int)
MAX_WEEKLY_SIGNUPS = _config('MAX_WEEKLY_SIGNUPS', default=3, cast=int)
NO_SHOW_LIMIT = _config('NO_SHOW_LIMIT', default=2, cast=int)
REMINDER_HOURS_BEFORE = _config('REMINDER_HOURS_BEFORE', default='24,2', cast=Csv(cast=int))

# CSRF Settings
CSRF_TRUSTED_ORIGINS = _config('CSRF_TRUSTED_ORIGINS', default='http://localhost:8000', cast=Csv())
CSRF_COOKIE_HTTPONLY = True
CSRF_USE_SESSIONS = False

# Security Settings (Production)
if not DEBUG:
    SECURE_SSL_REDIRECT = _config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE = _config('SESSION_COOKIE_SECURE', default=True, cast=bool)
    CSRF_COOKIE_SECURE = _config('CSRF_COOKIE_SECURE', default=True, cast=bool)
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # Cache control headers to prevent stale content
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Trust proxy headers for campus server deployment
    if 'bayoupal.nicholls.edu' in ALLOWED_HOSTS:
        SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

# Create logs directory
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# Login/Logout URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'




