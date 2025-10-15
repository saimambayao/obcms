# OBCMS Sevalla Environment Configuration

**Last Updated:** October 15, 2025  
**Purpose:** Complete environment variable configuration for Sevalla deployment  
**Application:** Bangsamoro Ministerial Management System (BMMS)

---

## Environment Variables Overview

This document provides the complete configuration for deploying OBCMS on Sevalla, including all necessary environment variables and security settings.

---

## Core Django Settings

### Required Variables

```bash
# Django Configuration
DJANGO_SETTINGS_MODULE=obc_management.settings.production
SECRET_KEY=your-super-secret-key-generate-new-for-production
DEBUG=False
ALLOWED_HOSTS=your-domain.sevalla.app,*.sevalla.app,bmms.barmm.gov.ph

# Application Information
SITE_NAME=BMMS - Bangsamoro Ministerial Management System
SITE_URL=https://bmms.barmm.gov.ph
ADMIN_EMAIL=admin@bmms.barmm.gov.ph
```

### Security Settings

```bash
# HTTPS and Security
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
X_FRAME_OPTIONS=DENY

# Session Configuration
SESSION_COOKIE_AGE=86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST=True
SESSION_COOKIE_HTTPONLY=True
CSRF_COOKIE_HTTPONLY=True
```

---

## Database Configuration

### PostgreSQL Connection

```bash
# Database Connection (provided by Sevalla)
DATABASE_URL=postgres://obcms_user:secure-password@postgresql-xxx.sevalla.com:5432/obcms_prod

# Alternative detailed configuration
DB_NAME=obcms_prod
DB_USER=obcms_user
DB_PASSWORD=secure-auto-generated-password
DB_HOST=postgresql-xxx.sevalla.com
DB_PORT=5432
DB_SSLMODE=require

# Database Optimization
CONN_MAX_AGE=600
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
```

### Database Connection Pooling

```python
# In production.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
        'OPTIONS': {
            'sslmode': 'require',
        },
        'CONN_MAX_AGE': int(os.getenv('CONN_MAX_AGE', 600)),
    }
}
```

---

## Redis Configuration

### Connection Settings

```bash
# Redis Connection (provided by Sevalla)
REDIS_URL=redis://obcms_user:redis-password@redis-xxx.sevalla.com:6379/0

# Alternative detailed configuration
REDIS_HOST=redis-xxx.sevalla.com
REDIS_PORT=6379
REDIS_PASSWORD=redis-secure-password
REDIS_DB=0
REDIS_CONNECTION_POOL_MAX_CONNECTIONS=50
```

### Celery Configuration

```bash
# Celery Settings
CELERY_BROKER_URL=redis://obcms_user:redis-password@redis-xxx.sevalla.com:6379/0
CELERY_RESULT_BACKEND=redis://obcms_user:redis-password@redis-xxx.sevalla.com:6379/0
CELERY_ACCEPT_CONTENT=json
CELERY_TASK_SERIALIZER=json
CELERY_RESULT_SERIALIZER=json
CELERY_TIMEZONE=Asia/Manila
CELERY_BEAT_SCHEDULE_ENABLED=True
```

---

## Static Files and Media Storage

### Object Storage (Cloudflare R2)

```bash
# S3-Compatible Storage Configuration
AWS_ACCESS_KEY_ID=your-r2-access-key
AWS_SECRET_ACCESS_KEY=your-r2-secret-key
AWS_STORAGE_BUCKET_NAME=obcms-static-files
AWS_S3_ENDPOINT_URL=https://your-bucket.r2.sevalla.com
AWS_S3_CUSTOM_DOMAIN=
AWS_S3_REGION_NAME=auto
AWS_S3_FILE_OVERWRITE=False
AWS_DEFAULT_ACL=private

# Django Storage Settings
STATIC_URL=/static/
STATIC_ROOT=/app/src/staticfiles
MEDIA_URL=/media/
MEDIA_ROOT=/app/src/media

# Storage Backends
STATICFILES_STORAGE=storages.backends.s3boto3.S3Boto3Storage
DEFAULT_FILE_STORAGE=storages.backends.s3boto3.S3Boto3Storage
```

### Alternative: Local Storage (Development/Testing)

```bash
# For development environments only
USE_S3=False
STATIC_URL=/static/
STATIC_ROOT=/app/src/staticfiles
MEDIA_URL=/media/
MEDIA_ROOT=/app/src/media
STATICFILES_STORAGE=DjangoManifestStaticFilesStorage
DEFAULT_FILE_STORAGE=django.core.files.storage.FileSystemStorage
```

---

## Email Configuration

 Gmail/Google Workspace Setup

```bash
# Email Backend Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@bmms.barmm.gov.ph
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=BMMS <noreply@bmms.barmm.gov.ph>
SERVER_EMAIL=admin@bmms.barmm.gov.ph

# Email Settings
EMAIL_SUBJECT_PREFIX="[BMMS] "
EMAIL_TIMEOUT=30
EMAIL_USE_SSL=False
```

### Alternative: SendGrid

```bash
# SendGrid Configuration
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SENDGRID_API_KEY
DEFAULT_FROM_EMAIL=BMMS <noreply@bmms.barmm.gov.ph
```

---

## AI Services Configuration

### Google Gemini API

```bash
# Google AI Configuration
GEMINI_API_KEY=your-gemini-api-key-assignment
GOOGLE_CLOUD_PROJECT_ID=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account",...}

# AI Model Configuration
GEMINI_MODEL=gemini-1.5-pro
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=2048

# Vector Store Configuration
VECTOR_STORE_TYPE=faiss
VECTOR_STORE_DIMENSION=768
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Search Configuration

```bash
# Similarity Search Settings
SIMILARITY_THRESHOLD=0.7
MAX_SEARCH_RESULTS=10
SEARCH_TIMEOUT=30
ENABLE_SEMANTIC_SEARCH=True
ENABLE_FULLTEXT_SEARCH=True
```

---

## Logging Configuration

### Application Logging

```bash
# Logging Settings
LOG_LEVEL=INFO
LOG_DIR=/app/logs
LOG_FILE=django.log
LOG_MAX_SIZE=50MB
LOG_BACKUP_COUNT=5

# Django Logging
DJANGO_LOG_LEVEL=INFO
REQUEST_LOGGING=True
SECURE_LOGGING=True
```

### Log Rotation

```python
# In production.py
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
        'file': {
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.getenv('LOG_DIR', '/app/logs'), os.getenv('LOG_FILE', 'django.log')),
            'maxBytes': (50 * 1024 * 1024),  # 50MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'obc_management': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

---

## Performance and Caching

### Cache Configuration

```bash
# Redis Cache Configuration
CACHE_URL=redis://obcms_user:redis-password@redis-xxx.sevalla.com:6379/1
CACHE_TTL=3600
CACHE_KEY_PREFIX=obcms
CACHE_VERSION=1

# Session Cache
SESSION_CACHE_ALIAS=default
SESSION_ENGINE=django.contrib.sessions.backends.cache
```

### Performance Optimization

```bash
# Django Performance
USE_TZ=True
TIME_ZONE=Asia/Manila
LANGUAGE_CODE=en-us
USE_I18N=True
USE_L10N=True

# Connection Settings
CONN_MAX_AGE=600
DATA_UPLOAD_MAX_MEMORY_SIZE=5242880  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE=5242880  # 5MB

# Security Headers
SECURE_REFERRER_POLICY=same-origin
SECURE_CROSS_ORIGIN_OPENER_POLICY=same-origin
```

---

## Security and Monitoring

### Rate Limiting

```bash
# Rate Limiting Configuration
RATELIMIT_ENABLE=True
RATELIMIT_USE_CACHE=default
RATELIMIT_KEY_PREFIX=rl:obcms

# Rate Limits (requests per minute)
RATELIMIT_VIEWS_LOGIN=5/m
RATELIMIT_VIEWS_REGISTER=3/m
RATELIMIT_VIEWS_API=100/m
RATELIMIT_GLOBAL=1000/m
```

### Monitoring and Health

```bash
# Health Check Configuration
HEALTH_CHECK_ENABLED=True
HEALTH_CHECK_TOKEN=your-health-check-token
HEALTH_CHECK_INTERVAL=60

# Monitoring Settings
MONITORING_ENABLED=True
SENTRY_DSN=your-sentry-dsn  # Optional
ERROR_TRACKING_ENABLED=True
```

---

## BMMS-Specific Settings

### Organization Configuration

```bash
# BMMS Organization Settings
BMMS_ORGANIZATION_NAME=Office of the Chief Minister
BMMS_ORGANIZATION_TYPE=central
BMMS_ORGANIZATION_CODE=OCM
BMMS_ORGANIZATION_LEVEL=national

# Multi-tenant Settings
ENABLE_MULTI_TENANT=True
TENANT_MODEL=common.models.Organization
TENANT_QUERY_FIELD=organization
```

### Geographic Configuration

```bash
# Geographic Settings
DEFAULT_REGION=BARMM
DEFAULT_TIMEZONE=Asia/Manila
GEOCODING_SERVICE=google
GEOCODING_API_KEY=your-geocoding-api-key

# Philippines Administrative Division
COUNTRY_CODE=PH
COUNTRY_NAME=Philippines
ADMIN_LEVEL_1=Region
ADMIN_LEVEL_2=Province
ADMIN_LEVEL_3=Municipality
ADMIN_LEVEL_4=Barangay
```

### Features Configuration

```bash
# Feature Flags
ENABLE_AI_FEATURES=True
ENABLE_QUERY_EXPANSION=True
ENABLE_SEMANTIC_SEARCH=True
ENABLE_ANALYTICS=True
ENABLE_REPORTING=True
ENABLE_MOBILE_ACCESS=True

# Budgeting Module
ENABLE_BUDGET_MODULE=True
BUDGET_CURRENCY=PHP
BUDGET_FISCAL_YEAR_START=01
BUDGET_FISCAL_YEAR_END=12
```

---

## Development and Testing

### Staging Environment

```bash
# Staging Configuration (for testing)
DJANGO_SETTINGS_MODULE=obc_management.settings.staging
DEBUG=True
ALLOWED_HOSTS=staging-bmms.sevalla.app
DATABASE_URL=postgres://user:pass@host:5432/obcms_staging
REDIS_URL=redis://user:pass@host:6379/1
```

### Testing Configuration

```bash
# Test Environment
DJANGO_SETTINGS_MODULE=obc_management.settings.testing
DEBUG=True
DATABASE_URL=postgres://user:pass@host:5432/obcms_test
REDIS_URL=redis://user:pass@host:6379/2
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

---

## Production Deployment Templates

### .env.production Template

```bash
# ==========================================
# OBCMS Production Environment Configuration
# ==========================================

# Django Core Settings
DJANGO_SETTINGS_MODULE=obc_management.settings.production
SECRET_KEY=GENERATE_NEW_SMURFP31_SECRET_KEY_HERE
DEBUG=False
ALLOWED_HOSTS=your-domain.sevalla.app,*.sevalla.app,bmms.barmm.gov.ph

# Database Configuration
DATABASE_URL=postgres://obcms_user:PASSWORD@postgresql-xxx.sevalla.com:5432/obcms_prod
CONN_MAX_AGE=600

# Redis Configuration
REDIS_URL=redis://obcms_user:PASSWORD@redis-xxx.sevalla.com:6379/0
CELERY_BROKER_URL=redis://obcms_user:PASSWORD@redis-xxx.sevalla.com:6379/0

# Storage Configuration
AWS_ACCESS_KEY_ID=YOUR_R2_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=YOUR_R2_SECRET_KEY
AWS_STORAGE_BUCKET_NAME=obcms-static-files
AWS_S3_ENDPOINT_URL=https://your-bucket.r2.sevalla.com

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@bmms.barmm.gov.ph
EMAIL_HOST_PASSWORD=YOUR_GMAIL_APP_PASSWORD

# AI Services Configuration
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GOOGLE_CLOUD_PROJECT_ID=YOUR_GCP_PROJECT_ID

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# BMMS Configuration
BMMS_ORGANIZATION_NAME=Office of the Chief Minister
ENABLE_MULTI_TENANT=True
ENABLE_AI_FEATURES=True

# Logging
LOG_LEVEL=INFO
DJANGO_LOG_LEVEL=INFO
```

### .env.staging Template

```bash
# ==========================================
# OBCMS Staging Environment Configuration
# ==========================================

# Django Core Settings
DJANGO_SETTINGS_MODULE=obc_management.settings.staging
SECRET_KEY=staging-secret-key-for-testing-only
DEBUG=True
ALLOWED_HOSTS=staging-bmms.sevalla.app

# Database Configuration
DATABASE_URL=postgres://obcms_user:PASSWORD@postgresql-staging-xxx.sevalla.com:5432/obcms_staging
CONN_MAX_AGE=60

# Redis Configuration
REDIS_URL=redis://obcms_user:PASSWORD@redis-staging-xxx.sevalla.com:6379/1

# Storage Configuration (Local for staging)
USE_S3=False
STATIC_URL=/static/
MEDIA_URL=/media/

# Email Configuration (Console backend for testing)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# AI Services Configuration (Use test keys)
GEMINI_API_KEY=TEST_GEMINI_API_KEY
GOOGLE_CLOUD_PROJECT_ID=obcms-test

# Security Settings (Relaxed for staging)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# Logging
LOG_LEVEL=DEBUG
DJANGO_LOG_LEVEL=DEBUG
```

---

## Security Best Practices

### Secret Generation

```bash
# Generate new Django SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Generate secure passwords
openssl rand -base64 32
```

### Environment Variable Security

```bash
# Encrypt sensitive values when possible
# Use Sevalla's built-in secret management
# Rotate keys regularly (every 90 days)
# Audit access logs for secret usage
```

### Access Control

```bash
# limit access to Sevalla dashboard
# Use MFA for all accounts
# Regular security audits
# Monitor for unauthorized access
```

---

## Validation Commands

### Django Deployment Check

```bash
# Run comprehensive deployment check
python manage.py check --deploy

# Expected output: System check identified no issues (0 silenced)
```

### Database Connection Test

```bash
# Test database connection
python manage.py dbshell --database default
# Should connect successfully to PostgreSQL

# Test migrations
python manage.py showmigrations
# Should show all migrations as [X] applied
```

### Cache and Redis Test

```bash
# Test Redis connection
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value', 60)
>>> cache.get('test')
'value'  # Should return the test value
```

### Email Configuration Test

```bash
# Test email configuration
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test Subject', 'Test Message', 'from@example.com', ['to@example.com'])
# Should return 1 if successful
```

### Storage Test

```bash
# Test file upload to storage
python manage.py shell
>>> from django.core.files.base import ContentFile
>>> from django.core.files.storage import default_storage
>>> default_storage.save('test.txt', ContentFile(b'test content'))
'test.txt'  # Should return filename if successful
```

---

## Common Issues and Solutions

### Database Connection Issues

```bash
# Symptom: OperationalError: could not connect to server
# Solution: Check DATABASE_URL format and network connectivity

# Verify connection string format
psql "postgres://user:pass@host:5432/db" -c "SELECT 1;"
```

### Static Files Not Loading

```bash
# Symptom: CSS/JS files return 404
# Solution: Check AWS credentials and bucket permissions

# Debug storage configuration
python manage.py shell
>>> from django.contrib.staticfiles.storage import staticfiles_storage
>>> staticfiles_storage.exists('css/output.css')
True  # Should return True
```

### Email Issues

```bash
# Symptom: SMTPAuthenticationError
# Solution: Use app-specific password for Gmail

# Test SMTP connection
python manage.py shell
>>> import smtplib
>>> server = smtplib.SMTP('smtp.gmail.com', 587)
>>> server.starttls()
>>> server.login('email@gmail.com', 'app-password')
```

---

## Maintenance and Updates

### Regular Tasks

```bash
# Weekly: Check for security updates
pip list --outdated

# Monthly: Rotate secrets
# Update API keys, passwords, and tokens

# Quarterly: Review permissions
# Audit user access and API key usage
```

### Backup Procedures

```bash
# Environment variable backup
# Store secure backup in vault or encrypted storage

# Database backups (handled by Sevalla automatically)
# Additional manual backup if needed
python manage.py dumpdata --natural-foreign --natural-primary > backup.json
```

---

## Support and Documentation

### Quick Reference

- **Django Settings**: https://docs.djangoproject.com/en/5.2/topics/settings/
- **PostgreSQL on Sevalla**: https://sevalla.com/docs/databases/postgresql
- **Object Storage**: https://sevalla.com/docs/storage
- **Security Best Practices**: https://sevalla.com/docs/security

### Troubleshooting

1. **Check application logs** in Sevalla dashboard
2. **Verify environment variables** are properly formatted
3. **Test connections** individually before deployment
4. **Monitor resource usage** for performance issues

---

This configuration provides a complete, secure, and optimized setup for deploying OBCMS on Sevalla. Regular monitoring and maintenance will ensure continued reliable operation.
