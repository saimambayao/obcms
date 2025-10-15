# OBCMS Sevalla Configuration Guide

**Date**: October 16, 2025
**Status**: ✅ **CONFIGURATION READY**
**Security**: 🔒 **SECRETS MANAGED LOCALLY**

---

## 🎯 **SECURITY FIRST APPROACH**

**✅ SECURE CONFIGURATION**: All real credentials are stored locally in `.env.production.local` (NOT committed to Git).

**📋 FILES IN GIT:**
- ✅ `.env.production.template` - Template with placeholders
- ✅ This configuration guide - No real secrets
- ❌ `.env.production.local` - Contains real credentials (NOT in Git)

---

## 🚀 **SEVALLA DEPLOYMENT SETUP**

### **Step 1: Get Your Sevalla Credentials**

From your Sevalla dashboard, you'll need:

#### **Database Credentials**
```bash
# Format from Sevalla:
DATABASE_URL=postgres://username:password@host:port/database_name

# Extract for configuration:
DB_NAME=your-database-name
DB_USER=your-username
DB_PASSWORD=your-password
DB_HOST=postgresql-xxx.sevalla.com
```

#### **Redis Credentials**
```bash
# Format from Sevalla:
REDIS_URL=redis://:password@host:port/0

# Extract for configuration:
REDIS_HOST=redis-xxx.sevalla.com
REDIS_PASSWORD=your-redis-password
```

#### **Object Storage (R2) Credentials**
```bash
# Format from Sevalla:
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_ENDPOINT_URL=https://xxx.r2.cloudflarestorage.com
```

#### **Domain Information**
```bash
# Your Sevalla domain:
ALLOWED_HOSTS=your-app-name.sevalla.app
CSRF_TRUSTED_ORIGINS=https://your-app-name.sevalla.app
```

### **Step 2: Configure Local Environment**

1. **Copy template to local file:**
   ```bash
   cp .env.production.template .env.production.local
   ```

2. **Edit `.env.production.local`** with your real Sevalla credentials

3. **Never commit `.env.production.local`** to Git

### **Step 3: Add Environment Variables to Sevalla Dashboard**

Copy these variables from your `.env.production.local` file:

```bash
# Core Django Settings
DJANGO_SETTINGS_MODULE=obc_management.settings.production
SECRET_KEY=your-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=your-app-name.sevalla.app,localhost,127.0.0.1,10.96.*.*
CSRF_TRUSTED_ORIGINS=https://your-app-name.sevalla.app

# Application Information
SITE_NAME=BMMS - Bangsamoro Ministerial Management System
SITE_URL=https://your-app-name.sevalla.app
ADMIN_EMAIL=admin@bmms.barmm.gov.ph

# Database Configuration (from Sevalla)
DATABASE_URL=postgres://user:pass@host:port/dbname
DB_NAME=your-database-name
DB_USER=your-username
DB_PASSWORD=your-password
DB_HOST=postgresql-xxx.sevalla.com
DB_PORT=5432

# Redis Configuration (from Sevalla)
REDIS_URL=redis://:password@host:port/0
REDIS_HOST=redis-xxx.sevalla.com
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_DB=0

# Celery Configuration
CELERY_BROKER_URL=${REDIS_URL}
CELERY_RESULT_BACKEND=${REDIS_URL}
CELERY_ACCEPT_CONTENT=json
CELERY_TASK_SERIALIZER=json
CELERY_RESULT_SERIALIZER=json
CELERY_TIMEZONE=Asia/Manila
CELERY_BEAT_SCHEDULE_ENABLED=True

# Storage Configuration (from Sevalla)
USE_S3=True
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=obcms-static-files
AWS_S3_ENDPOINT_URL=https://xxx.r2.cloudflarestorage.com
AWS_S3_REGION_NAME=auto
AWS_S3_FILE_OVERWRITE=False
AWS_DEFAULT_ACL=private

# Django Storage Settings
STATIC_URL=/static/
STATIC_ROOT=/app/src/staticfiles
MEDIA_URL=/media/
MEDIA_ROOT=/app/src/media
STATICFILES_STORAGE=storages.backends.s3boto3.S3Boto3Storage
DEFAULT_FILE_STORAGE=storages.backends.s3boto3.S3Boto3Storage

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
X_FRAME_OPTIONS=DENY

# Email Configuration (Basic Setup)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=localhost
EMAIL_PORT=25
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=OBCMS <noreply@your-app-name.sevalla.app>
SERVER_EMAIL=admin@bmms.barmm.gov.ph
EMAIL_SUBJECT_PREFIX="[BMMS]"

# BMMS Configuration
BMMS_ORGANIZATION_NAME=Office of the Chief Minister
BMMS_ORGANIZATION_TYPE=central
BMMS_ORGANIZATION_CODE=OCM
BMMS_ORGANIZATION_LEVEL=national
ENABLE_MULTI_TENANT=True
TENANT_MODEL=common.models.Organization
TENANT_QUERY_FIELD=organization

# Geographic Configuration
DEFAULT_REGION=BARMM
DEFAULT_TIMEZONE=Asia/Manila
TIME_ZONE=Asia/Manila
LANGUAGE_CODE=en-us
USE_I18N=True
USE_L10N=True
USE_TZ=True

# Philippines Administrative Division
COUNTRY_CODE=PH
COUNTRY_NAME=Philippines
ADMIN_LEVEL_1=Region
ADMIN_LEVEL_2=Province
ADMIN_LEVEL_3=Municipality
ADMIN_LEVEL_4=Barangay

# Performance Settings
CONN_MAX_AGE=600
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
REDIS_CONNECTION_POOL_MAX_CONNECTIONS=50
CACHE_TTL=3600
CACHE_KEY_PREFIX=obcms
CACHE_VERSION=1

# Feature Flags
ENABLE_AI_FEATURES=True
ENABLE_QUERY_EXPANSION=True
ENABLE_SEMANTIC_SEARCH=True
ENABLE_ANALYTICS=True
ENABLE_REPORTING=True
ENABLE_MOBILE_ACCESS=True
ENABLE_BUDGET_MODULE=True
BUDGET_CURRENCY=PHP
BUDGET_FISCAL_YEAR_START=01
BUDGET_FISCAL_YEAR_END=12

# Deployment Control
ENVIRONMENT=production
BUILD_NUMBER=1
RUN_MIGRATES=false

# Rate Limiting
RATELIMIT_ENABLE=True
RATELIMIT_USE_CACHE=default
RATELIMIT_KEY_PREFIX=rl:obcms
RATELIMIT_VIEWS_LOGIN=5/m
RATELIMIT_VIEWS_REGISTER=3/m
RATELIMIT_VIEWS_API=100/m
RATELIMIT_GLOBAL=1000/m

# Monitoring
HEALTH_CHECK_ENABLED=True
HEALTH_CHECK_TOKEN=generate-secure-token
HEALTH_CHECK_INTERVAL=60
MONITORING_ENABLED=True
ERROR_TRACKING_ENABLED=True
LOG_LEVEL=INFO
DJANGO_LOG_LEVEL=INFO
REQUEST_LOGGING=True
SECURE_LOGGING=True

# Backup Configuration
BACKUP_ENABLED=True
BACKUP_SCHEDULE=daily
BACKUP_RETENTION_DAYS=30
BACKUP_ENCRYPTION=True
```

---

## 🔐 **SECURITY BEST PRACTICES**

### ✅ **DO:**
- Store secrets in local `.env.production.local` file
- Use different secrets for production vs development
- Rotate secrets regularly (every 90 days)
- Use strong, unique passwords
- Monitor access logs

### ❌ **DON'T:**
- Commit `.env.production.local` to Git
- Share credentials via email or chat
- Use the same secrets across environments
- Hard-code secrets in code
- Store secrets in public documentation

### 📁 **FILE SECURITY STATUS**

| File | Contains Secrets | In Git | Safe |
|------|------------------|--------|------|
| `.env.production.template` | ❌ No placeholders | ✅ Yes | ✅ Safe |
| `.env.production.local` | ✅ Real credentials | ❌ No | ✅ Safe |
| This guide | ❌ No real secrets | ✅ Yes | ✅ Safe |

---

## 🛠️ **DEPLOYMENT STEPS**

### **Step 1: Configure Environment Variables**
1. **Get credentials** from Sevalla dashboard
2. **Update `.env.production.local`** with real values
3. **Copy variables** to Sevalla environment settings

### **Step 2: Deploy Application**
1. **Push code** to production branch
2. **Sevalla auto-deploys** from repository
3. **Monitor deployment** logs

### **Step 3: Post-Deployment Setup**
1. **Verify health check**: `https://your-app.sevalla.app/health/`
2. **Run database migrations**
3. **Create admin user**
4. **Collect static files**
5. **Test functionality**

---

## 🔧 **TOOLS AND HELPERS**

### **Generate Secure Secrets**
```bash
# Django SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Random passwords
openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
```

### **Validate Configuration**
```bash
# Test Django configuration
python manage.py check --deploy

# Test database connection
python manage.py dbshell --command="SELECT 1;"

# Test Redis connection
python manage.py shell -c "from django.core.cache import cache; cache.set('test', 'value', 60); print(cache.get('test'))"
```

---

## 📞 **SUPPORT AND RESOURCES**

### **Quick Links**
- **Application**: https://your-app-name.sevalla.app
- **Health Check**: https://your-app-name.sevalla.app/health/
- **Admin Panel**: https://your-app-name.sevalla.app/admin/
- **Sevalla Dashboard**: https://dashboard.sevalla.com

### **Documentation**
- [CLAUDE.md](CLAUDE.md) - Project guidelines
- [SEVALLA_DEPLOYMENT_COMPLETE_GUIDE.md](SEVALLA_DEPLOYMENT_COMPLETE_GUIDE.md) - Technical details
- [Dockerfile](Dockerfile) - Container configuration

### **Troubleshooting**
1. **Static Files 404**: Run `collectstatic` command
2. **Database Issues**: Verify connection string format
3. **Redis Connection**: Check password and host
4. **Permission Errors**: Verify storage bucket permissions

---

## 🎉 **CONCLUSION**

**✅ SECURE CONFIGURATION COMPLETE**

Your OBCMS application is configured with:

- **✅ Secure secret management** (local file, not in Git)
- **✅ Production-ready Django settings**
- **✅ Comprehensive environment template**
- **✅ Security best practices applied**
- **✅ Complete deployment documentation**

**Next Steps:**
1. **Get your Sevalla credentials** from dashboard
2. **Configure local `.env.production.local`** file
3. **Add environment variables** to Sevalla dashboard
4. **Deploy and test** your application

**Security Confidence**: 10/10 🔒

---

*This guide contains no real secrets and is safe to commit to version control.*