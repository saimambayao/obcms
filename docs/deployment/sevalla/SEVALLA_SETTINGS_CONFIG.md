# OBCMS Sevalla Settings Configuration

**Last Updated:** October 15, 2025  
**Purpose:** Django settings configuration for Sevalla deployment  
**Application:** Bangsamoro Ministerial Management System (BMMS)

---

## Overview

This document provides the complete Django settings configuration required for deploying OBCMS on Sevalla platform. The settings are organized to work optimally with Sevalla's managed services.

---

## Production Settings Structure

### Settings Files Hierarchy

```
src/obc_management/settings/
├── __init__.py              # Settings loader
├── base.py                  # Common settings
├── production.py            # Production settings (general)
├── sevalla.py               # Sevalla-specific settings
├── staging.py               # Staging settings
└── development.py           # Development settings
```

---

## Sevalla-Specific Settings

### Create Sevalla Production Settings

Create `src/obc_management/settings/sevalla.py`:

```python
"""
Sevalla Production Settings for OBCMS

Optimized for Sevalla platform with managed PostgreSQL, Redis, and Object Storage.
"""

import os
from .production import *  # noqa: F401,F403

# ==========================================
# DJANGO CORE CONFIGURATION
# ==========================================

# Sevalla Settings Module Override
DJANGO_SETTINGS_MODULE = 'obc_management.settings.sevalla'

# Application Identification
SITE_URL = env.str('SITE_URL', default='https://your-domain.sevalla.app')
SITE_NAME = env.str('SITE_NAME', default='BMMS - Bangsamoro Ministerial Management System')

# ==========================================
# SEVALLA DATABASE CONFIGURATION
# ==========================================

# PostgreSQL 17 with Connection Pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env.str('DB_NAME', default='obcms_prod'),
        'USER': env.str('DB_USER', default='obcms_user'),
        'PASSWORD': env.str('DB_PASSWORD'),
        'HOST': env.str('DB_HOST', default='localhost'),
        'PORT': env.int('DB_PORT', default=5432),
        'OPTIONS': {
            'sslmode': 'require',  # Enforce SSL for Sevalla
            'connect_timeout': 30,
        },
        'CONN_MAX_AGE': env.int('CONN_MAX_AGE', default=600),  # 10 minutes
        'CONN_HEALTH_CHECKS': True,
        'ATOMIC_REQUESTS': True,  # Transaction safety
    }
}

# ==========================================
# SEVALLA REDIS CONFIGURATION
# ==========================================

# Redis for Caching and Sessions
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env.str('REDIS_URL', default='redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'retry_on_timeout': True,
                'socket_connect_timeout': 30,
                'socket_timeout': 30,
                'max_connections': 50,
            }
        },
        'KEY_PREFIX': env.str('CACHE_KEY_PREFIX', default='obcms_sevalla'),
        'TIMEOUT': env.int('CACHE_TTL', default=3600),  # 1 hour
    }
}

# Session Backend using Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# ==========================================
# SEVALLA STORAGE CONFIGURATION
# ==========================================

# Sevalla Object Storage (Cloudflare R2)
USE_S3 = env.bool('USE_S3', default=True)

if USE_S3:
    # AWS S3-Compatible Storage Configuration
    AWS_ACCESS_KEY_ID = env.str('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env.str('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env.str('AWS_STORAGE_BUCKET_NAME', default='obcms-static-files')
    AWS_S3_ENDPOINT_URL = env.str('AWS_S3_ENDPOINT_URL')
    AWS_S3_CUSTOM_DOMAIN = None  # Let Sevalla handle CDN
    AWS_S3_REGION_NAME = env.str('AWS_S3_REGION_NAME', default='auto')
    
    # Security Settings
    AWS_DEFAULT_ACL = None
    AWS_S3_FILE_OVERWRITE = False
    
    # Django Storages Configuration
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    
else:
    # Local/Alternative Storage (for testing)
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Static and Media File Configuration
STATIC_URL = env.str('STATIC_URL', default='/static/')
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = env.str('MEDIA_URL', default='/media/')
MEDIA_ROOT = BASE_DIR / 'media'

# ==========================================
# SEVALLA SECURITY CONFIGURATION
# ==========================================

# Enhanced Security for Production
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
SECURE_HSTS_PRELOAD = env.bool('SECURE_HSTS_PRELOAD', default=True)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# Cookie Security
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=True)
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=True)
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SAMESITE = 'Strict'

# ==========================================
# SEVALLA CELERY CONFIGURATION
# ==========================================

# Celery for Sevalla Platform
CELERY_BROKER_URL = env.str('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env.str('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')

# Worker Configuration
CELERY_WORKER_CONCURRENCY = env.int('CELERY_WORKER_CONCURRENCY', default=4)
CELERY_WORKER_MAX_TASKS_PER_CHILD = env.int('CELERY_WORKER_MAX_TASKS_PER_CHILD', default=1000)
CELERY_WORKER_PREFETCH_MULTIPLIER = env.int('CELERY_WORKER_PREFETCH_MULTIPLIER', default=4)

# Task Configuration
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = env.str('CELERY_TIMEZONE', default='Asia/Manila')
CELERY_ENABLE_utc = True

# Task Timeouts
CELERY_TASK_TIME_LIMIT = env.int('CELERY_TASK_TIME_LIMIT', default=300)  # 5 minutes
CELERY_TASK_SOFT_TIME_LIMIT = env.int('CELERY_TASK_SOFT_TIME_LIMIT', default=240)  # 4 minutes
CELERY_TASK_RESULT_EXPIRES = 3600  # 1 hour

# Beat Configuration
CELERY_BEAT_SCHEDULE_ENABLED = env.bool('CELERY_BEAT_SCHEDULE_ENABLED', default=True)
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# ==========================================
# SEVALLA EMAIL CONFIGURATION
# ==========================================

# Production Email Backend
EMAIL_BACKEND = env.str('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = env.str('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL', default=False)
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env.str('DEFAULT_FROM_EMAIL', default='BMMS <noreply@bmms.barmm.gov.ph>')
SERVER_EMAIL = env.str('SERVER_EMAIL', default='admin@bmms.barmm.gov.ph')

# ==========================================
# SEVALLA AI SERVICES CONFIGURATION
# ==========================================

# Google Gemini AI Configuration
GEMINI_API_KEY = env.str('GEMINI_API_KEY')
GEMINI_MODEL = env.str('GEMINI_MODEL', default='gemini-1.5-pro')
GEMINI_TEMPERATURE = env.float('GEMINI_TEMPERATURE', default=0.7)
GEMINI_MAX_TOKENS = env.int('GEMINI_MAX_TOKENS', default=2048)

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT_ID = env.str('GOOGLE_CLOUD_PROJECT_ID')

# Vector Store Configuration
VECTOR_STORE_TYPE = env.str('VECTOR_STORE_TYPE', default='faiss')
VECTOR_STORE_DIMENSION = env.int('VECTOR_STORE_DIMENSION', default=768)
EMBEDDING_MODEL = env.str('EMBEDDING_MODEL', default='sentence-transformers/all-MiniLM-L6-v2')

# Search Configuration
SIMILARITY_THRESHOLD = env.float('SIMILARITY_THRESHOLD', default=0.7)
MAX_SEARCH_RESULTS = env.int('MAX_SEARCH_RESULTS', default=10)
SEARCH_TIMEOUT = env.int('SEARCH_TIMEOUT', default=30)

# ==========================================
# SEVALLA BMMS CONFIGURATION
# ==========================================

# Organization Settings
BMMS_ORGANIZATION_NAME = env.str('BMMS_ORGANIZATION_NAME', default='Office of the Chief Minister')
BMMS_ORGANIZATION_TYPE = env.str('BMMS_ORGANIZATION_TYPE', default='central')
BMMS_ORGANIZATION_CODE = env.str('BMMS_ORGANIZATION_CODE', default='OCM')
BMMS_ORGANIZATION_LEVEL = env.str('BMMS_ORGANIZATION_LEVEL', default='national')

# Multi-tenant Settings
ENABLE_MULTI_TENANT = env.bool('ENABLE_MULTI_TENANT', default=True)
TENANT_MODEL = 'common.models.Organization'
TENANT_QUERY_FIELD = 'organization'

# Geographic Settings
DEFAULT_REGION = env.str('DEFAULT_REGION', default='BARMM')
DEFAULT_TIMEZONE = env.str('DEFAULT_TIMEZONE', default='Asia/Manila')
GEOCODING_SERVICE = env.str('GEOCODING_SERVICE', default='google')
GEOCODING_API_KEY = env.str('GEOCODING_API_KEY')

# Philippines Administrative Division
COUNTRY_CODE = 'PH'
COUNTRY_NAME = 'Philippines'
ADMIN_LEVEL_1 = 'Region'
ADMIN_LEVEL_2 = 'Province'
ADMIN_LEVEL_3 = 'Municipality'
ADMIN_LEVEL_4 = 'Barangay'

# ==========================================
# SEVALLA FEATURE FLAGS
# ==========================================

# Enable/Disable Features
ENABLE_AI_FEATURES = env.bool('ENABLE_AI_FEATURES', default=True)
ENABLE_QUERY_EXPANSION = env.bool('ENABLE_QUERY_EXPANSION', default=True)
ENABLE_SEMANTIC_SEARCH = env.bool('ENABLE_SEMANTIC_SEARCH', default=True)
ENABLE_ANALYTICS = env.bool('ENABLE_ANALYTICS', default=True)
ENABLE_REPORTING = env.bool('ENABLE_REPORTING', default=True)
ENABLE_MOBILE_ACCESS = env.bool('ENABLE_MOBILE_ACCESS', default=True)

# Budgeting Module
ENABLE_BUDGET_MODULE = env.bool('ENABLE_BUDGET_MODULE', default=True)
BUDGET_CURRENCY = env.str('BUDGET_CURRENCY', default='PHP')
BUDGET_FISCAL_YEAR_START = env.int('BUDGET_FISCAL_YEAR_START', default=1)
BUDGET_FISCAL_YEAR_END = env.int('BUDGET_FISCAL_YEAR_END', default=12)

# ==========================================
# SEVALLA LOGGING CONFIGURATION
# ==========================================

# Production Logging
LOG_LEVEL = env.str('LOG_LEVEL', default='INFO')
DJANGO_LOG_LEVEL = env.str('DJANGO_LOG_LEVEL', default='INFO')
REQUEST_LOGGING = env.bool('REQUEST_LOGGING', default=True)

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
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 50 * 1024 * 1024,  # 50MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': DJANGO_LOG_LEVEL,
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': DJANGO_LOG_LEVEL,
            'propagate': False,
        },
        'obc_management': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}

# ==========================================
# SEVALLA RATE LIMITING
# ==========================================

# Rate Limiting Configuration
RATELIMIT_ENABLE = env.bool('RATELIMIT_ENABLE', default=True)
RATELIMIT_USE_CACHE = 'default'
RATELIMIT_KEY_PREFIX = env.str('RATELIMIT_KEY_PREFIX', default='rl:obcms_sevalla')

# Rate Limits (requests per minute)
RATELIMIT_VIEWS_LOGIN = env.str('RATELIMIT_VIEWS_LOGIN', default='5/m')
RATELIMIT_VIEWS_REGISTER = env.str('RATELIMIT_VIEWS_REGISTER', default='3/m')
RATELIMIT_VIEWS_API = env.str('RATELIMIT_VIEWS_API', default='100/m')
RATELIMIT_GLOBAL = env.str('RATELIMIT_GLOBAL', default='1000/m')

# ==========================================
# SEVALLA PERFORMANCE CONFIGURATION
# ==========================================

# Connection Settings
CONN_MAX_AGE = env.int('CONN_MAX_AGE', default=600)
DATA_UPLOAD_MAX_MEMORY_SIZE = env.int('DATA_UPLOAD_MAX_MEMORY_SIZE', default=5242880)  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = env.int('FILE_UPLOAD_MAX_MEMORY_SIZE', default=5242880)  # 5MB

# Performance Optimization
USE_TZ = True
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True

# ==========================================
# SEVALLA DEPLOYMENT CONTROL
# ==========================================

# Migration Control
RUN_MIGRATIONS = env.bool('RUN_MIGRATIONS', default=True)

# Build and Deployment
ENVIRONMENT = 'sevalla'
BUILD_NUMBER = env.str('BUILD_NUMBER', default='1')

# ==========================================
# SEVALLA MONITORING
# ==========================================

# Health Check Configuration
HEALTH_CHECK_ENABLED = env.bool('HEALTH_CHECK_ENABLED', default=True)
HEALTH_CHECK_TOKEN = env.str('HEALTH_CHECK_TOKEN', default='your-secure-health-check-token')
HEALTH_CHECK_INTERVAL = env.int('HEALTH_CHECK_INTERVAL', default=60)

# Monitoring Settings
MONITORING_ENABLED = env.bool('MONITORING_ENABLED', default=True)
SENTRY_DSN = env.str('SENTRY_DSN', default='')  # Optional
ERROR_TRACKING_ENABLED = env.bool('ERROR_TRACKING_ENABLED', default=True)
```

---

## Environment-Specific Settings

### Staging Settings (sevalla_staging.py)

```python
"""
Sevalla Staging Settings

Uses Sevalla production settings with development-friendly overrides.
"""

from .sevalla import *  # noqa: F401,F403

# Enable Debugging for Staging
DEBUG = True
TEMPLATE_DEBUG = True

# Use Console Email Backend for Testing
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Use Local Storage for Testing
USE_S3 = False
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Test AI Services
GEMINI_API_KEY = env.str('GEMINI_API_KEY', default='test-key')
GOOGLE_CLOUD_PROJECT_ID = env.str('GOOGLE_CLOUD_PROJECT_ID', default='obcms-test')

 allow Local Testing
ALLOWED_HOSTS = ['*']
CORS_ALLOW_ALL_ORIGINS = True

# Reduced Logging for Development
LOG_LEVEL = 'DEBUG'
DJANGO_LOG_LEVEL = 'DEBUG'

# Performance Settings for Development
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
```

---

## Settings Updates Checklist

### 1. Create Sevalla Settings File
```bash
# Create sevalla.py settings file
cp src/obc_management/settings/production.py src/obc_management/settings/sevalla.py
```

### 2. Update Settings Loader
Update `src/obc_management/settings/__init__.py`:

```python
"""
Django settings loader for OBCMS.

This module automatically selects the appropriate settings module based on
environment variables and deployment platform.
"""

import os

# Default settings
DJANGO_SETTINGS_MODULE = 'obc_management.settings.development'

# Production environments
if os.getenv('DJANGO_SETTINGS_MODULE'):
    DJANGO_SETTINGS_MODULE = os.getenv('DJANGO_SETTINGS_MODULE')
elif os.getenv('ENVIRONMENT') == 'production':
    DJANGO_SETTINGS_MODULE = 'obc_management.settings.production'
elif os.getenv('ENVIRONMENT') == 'sevalla':
    DJANGO_SETTINGS_MODULE = 'obc_management.settings.sevalla'
elif os.getenv('ENVIRONMENT') == 'staging':
    DJANGO_SETTINGS_MODULE = 'obc_management.settings.staging'
elif os.getenv('ENVIRONMENT') == 'sevalla_staging':
    DJANGO_SETTINGS_MODULE = 'obc_management.settings.sevalla_staging'
```

### 3. Update Dockerfile Settings Module
Update ENV variable in Dockerfile:

```dockerfile
# Set environment variables for Sevalla deployment
ENV DJANGO_SETTINGS_MODULE=obc_management.settings.sevalla
```

---

## Configuration Validation

### Django Management Command
```bash
# Validate Sevalla configuration
python manage.py check --deploy --settings=obc_management.settings.sevalla

# Test database connection
python manage.py dbshell --settings=obc_management.settings.sevalla

# Test cache connection
python manage.py shell --settings=obc_management.settings.sevalla
>>> from django.core.cache import cache
>>> cache.set('test', 'value', 60)
>>> cache.get('test')
'value'
```

### Settings Validation Script
```python
# scripts/validate_sevalla_settings.py
import os
import sys
import django
from django.conf import settings

def validate_sevalla_settings():
    """Validate Sevalla-specific settings"""
    
    required_settings = [
        'DB_NAME',
        'DB_USER', 
        'DB_PASSWORD',
        'DB_HOST',
        'REDIS_URL',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_STORAGE_BUCKET_NAME',
        'AWS_S3_ENDPOINT_URL',
        'SECRET_KEY',
        'ALLOWED_HOSTS',
    ]
    
    missing_settings = []
    
    for setting in required_settings:
        if not getattr(settings, setting, None):
            missing_settings.append(setting)
    
    if missing_settings:
        print(f"❌ Missing required settings: {', '.join(missing_settings)}")
        return False
    
    print("✅ All required Sevalla settings are configured")
    return True

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.sevalla')
    django.setup()
    
    if validate_sevalla_settings():
        sys.exit(0)
    else:
        sys.exit(1)
```

---

## Security Configuration

### Production Security Checklist

```bash
# Check security settings
python manage.py check --deploy --settings=obc_management.settings.sevalla

# Expected output:
# System check identified no issues (0 silenced)
```

### Environment Variable Security

1. **Never commit secrets to version control**
2. **Use Sevalla's environment variable management**
3. **Rotate secrets regularly**
4. **Use strong, unique values for:**
   - SECRET_KEY
   - Database passwords
   - Redis passwords
   - AWS credentials
   - Health check tokens

---

## Performance Optimization

### Database Optimization

```python
# Connection pooling configured in settings
DATABASES['default']['CONN_MAX_AGE'] = 600
DATABASES['default']['CONN_HEALTH_CHECKS'] = True

# Query optimization
DATABASES['default']['OPTIONS']['connect_timeout'] = 30
DATABASES['default']['ATOMIC_REQUESTS'] = True
```

### Caching Strategy

```python
# Multi-level caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env.str('REDIS_URL'),
        'TIMEOUT': 3600,
    }
}

# Session cache
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
```

### Static File Optimization

```python
# S3 storage with CDN
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Compression and caching
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

---

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check DATABASE_URL format
   echo $DATABASE_URL
   # Should be: postgres://user:pass@host:port/db
   ```

2. **Static Files Not Loading**
   ```bash
   # Check AWS credentials
   python manage.py shell
   >>> from storages.backends.s3boto3 import S3Boto3Storage
   >>> storage = S3Boto3Storage()
   >>> storage.exists('static/css/output.css')
   ```

3. **Caching Issues**
   ```bash
   # Test Redis connection
   python manage.py shell
   >>> from django.core.cache import cache
   >>> cache.set('test', 'value', 60)
   >>> cache.get('test')
   ```

### Debug Commands

```bash
# Test specific settings module
python manage.py shell --settings=obc_management.settings.sevalla

# Check all settings
python manage.py shell --settings=obc_management.settings.sevalla
>>> from django.conf import settings
>>> settings.DATABASES
>>> settings.CACHES
>>> settings.STATICFILES_STORAGE
```

---

This configuration provides a complete, production-ready Django setup optimized for Sevalla's infrastructure with proper security, performance, and scalability considerations.
