# OBCMS Sevalla Troubleshooting and Maintenance Guide

**Last Updated:** October 15, 2025  
**Platform:** Sevalla (https://sevalla.com)  
**Application:** Bangsamoro Ministerial Management System (BMMS)  
**Purpose**: Essential reference for production support and maintenance

---

## Emergency Contacts and Resources

### Immediate Support Channels

| Issue Type | Contact Method | Response Time |
|------------|----------------|---------------|
| **Sevalla Platform Issues** | Sevalla Support Dashboard | < 2 hours |
| **Critical Application Errors** | Internal Dev Team | < 1 hour |
| **Database Issues** | Sevalla Database Support | < 2 hours |
| **Security Incidents** | Security Team Immediately | < 30 minutes |

### Documentation and References

- **Sevalla Documentation**: https://sevalla.com/docs
- **OBCMS Deployment Guide**: [SEVALLA_DEPLOYMENT_GUIDE.md](./SEVALLA_DEPLOYMENT_GUIDE.md)
- **Environment Configuration**: [SEVALLA_ENVIRONMENT_CONFIG.md](./SEVALLA_ENVIRONMENT_CONFIG.md)
- **Django Troubleshooting**: https://docs.djangoproject.com/en/5.2/faq/
- **PostgreSQL Issues**: https://www.postgresql.org/docs/current/

---

## Quick Diagnosis Checklist

### First Response (First 5 minutes)

```bash
# 1. Check Application Status
curl -I https://your-app.sevalla.app/health/
# Expected: HTTP/2 200

# 2. Check Sevalla Dashboard
- Application status: Running/Stopped/Error
- Recent deployments: Success/Failure
- Resource usage: CPU, Memory, Disk space
- Error logs: Recent entries

# 3. Database Connection Test
python manage.py dbshell --database default
# Expected: Successful connection

# 4. Redis Connection Test
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value', 60)
>>> cache.get('test')
'value'
```

### Priority Assessment

| Severity | Response | Resolution Time | Examples |
|----------|----------|-----------------|----------|
| **Critical** | Immediate | < 1 hour | Complete outage, data loss, security breach |
| **High** | < 30 minutes | < 4 hours | Major features down, significant performance issues |
| **Medium** | < 2 hours | < 24 hours | Partial functionality, minor performance issues |
| **Low** | < 8 hours | < 72 hours | UI issues, minor bugs, improvements |

---

## Common Issues and Solutions

### 1. Deployment Failures

#### Symptom: Application won't start after deployment

**Quick Check:**
```bash
# Check build logs in Sevalla dashboard
# Look for:
- Missing dependencies
- Docker build errors
- Environment variable issues
- Start command failures
```

**Common Solutions:**

1. **Missing Dependencies**
   ```bash
   # Update requirements.txt
   pip freeze > requirements.txt
   
   # Ensure critical packages are pinned:
   Django>=5.2.0,<5.3.0
   djangorestframework>=3.14.0
   psycopg[binary]>=3.2.0
   gunicorn>=20.1.0
   ```

2. **Environment Variable Issues**
   ```bash
   # Verify all required variables are set
   python manage.py check --deploy
   # Look for SECURITY WARNING messages
   ```

3. **Docker Build Issues**
   ```bash
   # Check Dockerfile target
   # Ensure production target is used
   FROM base as production
   ```

#### Symptom: "Application Error" page displayed

**Diagnosis:**
```bash
# Check application logs
# In Sevalla dashboard: Logs → Application

# Check specific error patterns:
- ImportError: Missing modules
- ModuleNotFoundError
- SyntaxError in Python code
- Configuration errors
```

**Solution:**
```bash
# 1. Roll back to previous working commit
git revert HEAD
git push origin production

# 2. If rollback fails, switch to known good commit
git checkout previous-working-commit
git push --force-with-lease origin production

# 3. Debug locally
git pull origin production
python manage.py runserver
# Reproduce error locally
```

### 2. Database Connection Issues

#### Symptom: OperationalError: could not connect to server

**Quick Test:**
```bash
# Test direct PostgreSQL connection
psql "postgres://user:pass@host:5432/db" -c "SELECT version();"

# In Django:
python manage.py dbshell --database default
```

**Common Causes and Solutions:**

1. **Incorrect DATABASE_URL**
   ```bash
   # Verify format
   DATABASE_URL=postgres://username:password@host:port/database
   
   # Check for special characters in password
   # URL encode if necessary
   ```

2. **Database Service Unavailable**
   ```bash
   # Check Sevalla dashboard
   # Database service status
   # Recent maintenance notifications
   
   # Contact Sevalla support if service appears down
   ```

3. **SSL/TLS Issues**
   ```bash
   # Ensure SSL mode is correct
   DATABASE_URL=postgres://user:pass@host:5432/db?sslmode=require
   
   # Test without SSL (temporary, for debugging only)
   DATABASE_URL=postgres://user:pass@host:5432/db?sslmode=disable
   ```

#### Symptom: Connection timeout errors

**Diagnosis:**
```bash
# Check connection limits
SELECT 
    max_connections,
    current_setting('max_connections')::int - 
    (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as available;
```

**Solutions:**
```bash
# 1. Optimize connection pooling
CONN_MAX_AGE=600  # Reuse connections

# 2. Reduce concurrent connections
# Check Django settings for excessive connection usage

# 3. Use connection pooling
# Configure in DATABASES setting options
```

### 3. Static Files and Media Issues

#### Symptom: CSS/JS files return 404

**Quick Check:**
```bash
# Test static file URL
curl -I https://your-app.sevalla.app/static/css/output.css
# Expected: HTTP/2 200

# Check Django collectstatic
python manage.py collectstatic --noinput --clear
```

**Common Solutions:**

1. **Storage Configuration Issues**
   ```bash
   # Verify AWS credentials
   python manage.py shell
   >>> from storages.backends.s3boto3 import S3Boto3Storage
   >>> storage = S3Boto3Storage()
   >>> storage.exists('static/css/output.css')
   True  # Should return True
   ```

2. **Bucket Permissions**
   ```bash
   # Check bucket policy in Sevalla dashboard
   # Ensure read access is allowed
   # Test with curl from browser
   ```

3. **URL Configuration**
   ```bash
   # Verify STATIC_URL in Django settings
   STATIC_URL='/static/'
   
   # Check nginx/static file serving
   # Should be configured by Sevalla automatically
   ```

#### Symptom: File uploads failing

**Diagnosis:**
```bash
# Test file upload manually
python manage.py shell
>>> from django.core.files.base import ContentFile
>>> from django.core.files.storage import default_storage
>>> default_storage.save('test.txt', ContentFile(b'test'))
'test.txt'  # Should return filename
```

**Solutions:**
```bash
# 1. Check storage permissions
# Ensure bucket has write permissions

# 2. Verify file size limits
DATA_UPLOAD_MAX_MEMORY_SIZE=5242880  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE=5242880  # 5MB

# 3. Check content type restrictions
# Add allowed file types if necessary
```

### 4. Performance Issues

#### Symptom: Slow page load times (> 5 seconds)

**Quick Diagnosis:**
```bash
# Check application performance
curl -w "@curl-format.txt" -o /dev/null -s https://your-app.sevalla.app/

# curl-format.txt:
#      time_namelookup:  %{time_namelookup}\n
#         time_connect:  %{time_connect}\n
#      time_appconnect:  %{time_appconnect}\n
#     time_pretransfer:  %{time_pretransfer}\n
#        time_redirect:  %{time_redirect}\n
#   time_starttransfer:  %{time_starttransfer}\n
#                      ----------\n
#           time_total:  %{time_total}\n
```

**Performance Optimization:**

1. **Database Query Optimization**
   ```bash
   # Enable Django Debug Toolbar for testing
   pip install django-debug-toolbar
   
   # Add to INSTALLED_APPS in development
   'debug_toolbar',
   
   # Check query count and timing
   # Target: < 50 queries per page, < 200ms total
   ```

2. **Caching Implementation**
   ```bash
   # Enable Redis caching
   CACHE_URL=redis://user:pass@host:6379/1
   
   # Cache frequently accessed data
   from django.core.cache import cache
   cache.set('key', data, timeout=3600)
   ```

3. **Static File Optimization**
   ```bash
   # Minify CSS/JS
   npm run build:css
   npm run build:js
   
   # Enable compression
   pip install django-compressor
   ```

#### Symptom: High CPU/memory usage

**Diagnosis:**
```bash
# Check resource usage in Sevalla dashboard
# Look for:
- CPU utilization > 80%
- Memory usage > 85%
- Disk space > 90%

# Check Django processes
python manage.py shell
>>> import psutil
>>> psutil.cpu_percent()
>>> psutil.virtual_memory().percent
```

**Solutions:**
```bash
# 1. Optimize queries
# Use select_related and prefetch_related
# Add database indexes
# Avoid N+1 queries

# 2. Implement caching
# Cache expensive operations
# Use view decorators for caching

# 3. Scale resources
# Upgrade to higher-tier plan
# Add CPU/RAM resources
```

### 5. Email Issues

#### Symptom: Emails not being sent

**Quick Test:**
```bash
# Test email configuration
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test Subject', 'Test Message', 'from@example.com', ['to@example.com'])
# Expected return: 1
```

**Common Solutions:**

1. **Gmail/Google Workspace Issues**
   ```bash
   # Use app-specific password, not regular password
   # Enable 2-factor authentication
   # Enable "Less secure app access" or use App Passwords
   
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=noreply@bmms.barmm.gov.ph
   EMAIL_HOST_PASSWORD=your-app-specific-password
   ```

2. **SMTP Authentication Issues**
   ```bash
   # Test SMTP connection manually
   python manage.py shell
   >>> import smtplib
   >>> server = smtplib.SMTP('smtp.gmail.com', 587)
   >>> server.starttls()
   >>> server.login('email@gmail.com', 'app-password')
   >>> server.quit()
   ```

3. **Rate Limiting**
   ```bash
   # Gmail limits: 500 emails/day
   # Use SendGrid for higher volumes
   # Implement email queuing with Celery
   ```

---

## Security Issues

### 1. SSL Certificate Issues

#### Symptom: HTTPS not working or certificate errors

**Diagnosis:**
```bash
# Check SSL configuration
curl -I https://your-app.sevalla.app/
# Should show: HTTP/2 200 with proper headers

# Check certificate details
openssl s_client -connect your-app.sevalla.app:443 -servername your-app.sevalla.app
```

**Solutions:**
```bash
# SSL is managed by Sevalla automatically
# If issues persist:
# 1. Check domain configuration
# 2. Verify DNS settings
# 3. Contact Sevalla support

# Ensure Django settings enforce HTTPS
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 2. Authentication Issues

#### Symptom: Users unable to login or CSRF errors

**Diagnosis:**
```bash
# Check secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# Should be unique and secure

# Check debug settings
DEBUG=False  # Must be False in production
```

**Solutions:**
```bash
# 1. Generate new SECRET_KEY
SECRET_KEY=your-new-secure-secret-key-here

# 2. Ensure ALLOWED_HOSTS is correct
ALLOWED_HOSTS=your-domain.sevalla.app,*.sevalla.app

# 3. Clear user sessions if needed
python manage.py shell
>>> from django.contrib.sessions.models import Session
>>> Session.objects.all().delete()
```

---

## Backup and Recovery

### Database Backup Issues

#### Symptom: Backup failures or corruption

**Manual Backup Procedure:**
```bash
# Create manual backup
python manage.py dbbackup --compress

# Verify backup
python manage.py dbbackup --list

# Test restore (on test database)
python manage.py dbrestore --backup-file backup-file.dump --database=test
```

**Complete Backup Strategy:**
```bash
# Automated backups (Sevalla handles this)
# Additional manual backups:
python manage.py dbbackup --compress --clean
python manage.py mediabackup --compress --clean

# Export data as JSON (additional backup)
python manage.py dumpdata --natural-foreign --natural-primary > backup.json
```

### Disaster Recovery

#### Complete System Recovery

```bash
# 1. Fresh deployment
# Deploy working code to new Sevalla application

# 2. Database restoration
python manage.py migrate --fake-initial
python manage.py dbrestore --backup-file latest-backup

# 3. Static files restoration
python manage.py collectstatic --noinput

# 4. Create superuser
python manage.py createsuperuser

# 5. Verify application
python manage.py check --deploy
curl https://your-app.sevalla.app/health/
```

---

## Monitoring and Alerting

### Health Check Implementation

```python
# views.py
import json
from django.http import JsonResponse
from django.core.cache import cache
from django.db import connection
from django.utils import timezone

def health_check(request):
    """Comprehensive health check endpoint"""
    
    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Redis/cache check
    try:
        cache.set('health_check', 'ok', 10)
        cache_status = "healthy" if cache.get('health_check') == 'ok' else "unhealthy"
    except Exception as e:
        cache_status = f"unhealthy: {str(e)}"
    
    # Overall status
    status = "healthy" if db_status == "healthy" and cache_status == "healthy" else "unhealthy"
    
    return JsonResponse({
        'status': status,
        'timestamp': timezone.now().isoformat(),
        'database': db_status,
        'cache': cache_status,
        'version': '1.0.0'
    })
```

### Alert Configuration

```bash
# Set up monitoring in Sevalla dashboard:

# Resource alerts:
- CPU > 80% for 5 minutes
- Memory > 85% for 5 minutes
- Disk > 90% capacity
- Response time > 5 seconds

# Application alerts:
- 5xx error rate > 5%
- Health check failures
- Database connection failures

# Security alerts:
- Failed login attempts > 10/hour
- Unusual traffic patterns
- SSL certificate expiry (30 days)
```

---

## Maintenance Procedures

### Daily Maintenance

```bash
# Check application health
curl https://your-app.sevalla.app/health/

# Review error logs (last 24 hours)
# In Sevalla dashboard: Logs → Application

# Monitor resource usage
# Look for trends in CPU, memory, storage
```

### Weekly Maintenance

```bash
# Database maintenance
python manage.py db vacuum  # Clean up
python manage.py db reindex  # Optimize indexes

# Clear old logs
find /app/logs -name "*.log" -mtime +7 -delete

# Check for security updates
pip list --outdated
```

### Monthly Maintenance

```bash
# Update dependencies (test first)
pip install --upgrade django
pip install --upgrade djangorestframework

# Test updates in staging
# Deploy to production only after testing

# Review and rotate secrets
# Update API keys if needed
# Change database passwords

# Performance review
# Analyze slow queries
# Optimize frequently used views
```

---

## Performance Tuning

### Database Optimization

```sql
-- Find slow queries
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Identify missing indexes
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY n_distinct DESC;
```

### Django Optimization

```python
# settings.py - Production optimization

# Connection pooling
CONN_MAX_AGE = 600
DATABASE_POOL_SIZE = 20

# Caching configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Email queuing
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
CELERY_EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
```

---

## Escalation Procedures

### Level 1: Developer Response (1 hour)

1. **Acknowledge Issue**: Log in monitoring system
2. **Initial Triage**: Determine severity and impact
3. **Quick Fix**: Implement temporary solution if possible
4. **Documentation**: Log all actions and observations

### Level 2: Senior Developer/DevOps (4 hours)

1. **Root Cause Analysis**: Investigate underlying cause
2. **Permanent Fix**: Implement proper solution
3. **Testing**: Verify fix resolves issue without side effects
4. **Monitoring**: Additional monitoring to prevent recurrence

### Level 3: Management/Architecture (24 hours)

1. **Strategic Review**: Assess systemic issues
2. **Architecture Changes**: Consider fundamental improvements
3. **Process Changes**: Update deployment/maintenance procedures
4. **Communication**: Stakeholder updates and post-mortem

---

## Post-Mortem Template

### Incident Report

```markdown
# Incident Report: [Brief Description]

## Summary
- **Time**: Start/End duration
- **Impact**: Users affected, functionality lost
- **Severity**: Critical/High/Medium/Low
- **Root Cause**: Primary cause of failure

## Timeline
- [Time]: Initial detection
- [Time]: Response initiated
- [Time]: Temporary fix implemented
- [Time]: Permanent fix deployed
- [Time]: Service restored

## Root Cause Analysis
- Primary cause:
- Contributing factors:
- Timeline of events:

## Resolution
- Immediate actions taken:
- Permanent fix implemented:
- Testing performed:

## Impact Assessment
- Users affected:
- Data loss:
- Financial impact:
- Reputation impact:

## Prevention Measures
- Monitoring improvements:
- Process changes:
- Technical changes:
- Training needed:
```

---

## Frequently Asked Questions

### Q: How do I rollback a deployment?

```bash
# Option 1: Using Git
git revert HEAD
git push origin production

# Option 2: Using Sevalla dashboard
1. Go to Deployments tab
2. Find previous successful deployment
3. Click "Redeploy"

# Option 3: Emergency rollback
git checkout previous-working-commit
git push --force-with-lease origin production
```

### Q: Why is my application showing 500 errors?

```bash
# 1. Check application logs
# 2. Verify environment variables
# 3. Test database connection
# 4. Check static file serving
# 5. Run Django checks: python manage.py check --deploy
```

### Q: How do I debug database issues?

```bash
# 1. Test direct connection
psql "postgres://user:pass@host:5432/db" -c "SELECT version();"

# 2. Check database logs
# 3. Verify migrations are up to date
python manage.py showmigrations

# 4. Check connection limits
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';
```

### Q: What should I do if I can't access the admin panel?

```bash
# 1. Check superuser exists
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.filter(is_superuser=True).exists()

# 2. Create new superuser if needed
python manage.py createsuperuser

# 3. Check ALLOWED_HOSTS setting
# 4. Verify SECRET_KEY is correct
```

---

## Contact Information

### Internal Support
- **Lead Developer**: [Name, Email, Phone]
- **DevOps Engineer**: [Name, Email, Phone]
- **Database Administrator**: [Name, Email, Phone]

### External Support
- **Sevalla Support**: dashboard.sevalla.com/support
- **Django Community**: https://forum.djangoproject.com/
- **PostgreSQL Community**: https://www.postgresql.org/community/

---

This troubleshooting guide should be used as the primary reference for managing OBCMS on Sevalla. Regular updates and maintenance of this document will ensure continued effective support for the production system.
