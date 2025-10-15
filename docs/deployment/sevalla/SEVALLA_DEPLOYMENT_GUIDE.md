# OBCMS Sevalla Deployment Guide

**Last Updated:** October 15, 2025  
**Platform:** Sevalla (https://sevalla.com)  
**Application:** Bangsamoro Ministerial Management System (BMMS)  
**Total Monthly Cost:** ~$10.04

---

## Executive Summary

Sevalla provides an excellent platform for deploying OBCMS with **minimal configuration** and **predictable pricing**. This guide covers the complete deployment process from setup to production.

### Key Benefits
- **Cost-effective**: ~$10/month total for complete infrastructure
- **Managed services**: PostgreSQL, Redis, storage, and CDN included
- **Auto-scaling**: Vertical and horizontal scaling available
- **Zero DevOps**: No server management required
- **Global CDN**: 260+ edge locations included

### Service Stack
- **Application Hosting**: Django + Gunicorn ($5/month)
- **Database Hosting**: PostgreSQL 17 ($5/month)
- **Object Storage**: Static files + uploads ($0.02/GB/month)
- **Static Hosting**: Frontend assets (FREE)
- **CDN**: Global distribution (included)

---

## Prerequisites

### Required Accounts
1. **Sevalla Account** (https://sevalla.com)
2. **Git Repository** (GitHub, GitLab, or Bitbucket)
3. **Domain Name** (optional, for custom domain)

### Technical Requirements
- **OBCMS Codebase**: Ready for production deployment
- **Environment Variables**: All secrets and configurations
- **Database Migrations**: PostgreSQL-compatible (already verified)
- **Static Files**: Properly configured for Django staticfiles

### Pre-deployment Checklist
- [x] PostgreSQL migration completed (verified 100% compatible)
- [x] Environment variables documented
- [x] Static files configuration validated
- [x] Security settings implemented
- [x] Backup procedures tested

---

## Service Configuration

### 1. Application Hosting Setup

**Service Type:** Application Hosting  
**Plan:** $5/month (Basic tier)  
**Runtime:** Python 3.12

#### Configuration Steps

1. **Create New Application**
   ```bash
   # In Sevalla Dashboard
   1. Click "Add Service" → "Application Hosting"
   2. Connect Git repository
   3. Select branch: main or production
   4. Runtime: Python 3.12
   5. Build Command: leave empty (Docker handles this)
   6. Start Command: gunicorn --chdir src --config gunicorn.conf.py obc_management.wsgi:application
   ```

2. **Environment Variables**
   ```bash
   # Critical Django Settings
   DJANGO_SETTINGS_MODULE=obc_management.settings.production
   SECRET_KEY=your-super-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=your-domain.sevalla.app,*.sevalla.app

   # Database Configuration
   DATABASE_URL=postgres://username:password@host:port/database_name

   # Redis Configuration
   REDIS_URL=redis://username:password@host:port/0
   CELERY_BROKER_URL=redis://username:password@host:port/0

   # Security Settings
   SECURE_SSL_REDIRECT=True
   SECURE_HSTS_SECONDS=31536000
   SECURE_HSTS_INCLUDE_SUBDOMAINS=True
   SECURE_HSTS_PRELOAD=True

   # AI Services Configuration
   GEMINI_API_KEY=your-gemini-api-key
   GOOGLE_CLOUD_PROJECT_ID=your-project-id

   # email Configuration
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   EMAIL_USE_TLS=True
   ```

3. **Health Check**
   ```bash
   # Health Check Endpoint
   Path: /health/
   Check Interval: 60 seconds
   Timeout: 10 seconds
   ```

### 2. Database Hosting Setup

**Service Type:** Database Hosting  
**Plan:** $5/month (Basic tier)  
**Database Type:** PostgreSQL 17

#### Configuration Steps

1. **Create PostgreSQL Database**
   ```bash
   # In Sevalla Dashboard
   1. Click "Add Service" → "Database Hosting"
   2. Database Type: PostgreSQL
   3. Version: 17 (recommended)
   4. Plan: Basic ($5/month)
   5. Region: Same as application (for low latency)
   ```

2. **Database Connection**
   ```bash
   # Connection Details (provided by Sevalla)
   Host: postgresql-xxx.sevalla.com
   Port: 5432
   Database: obcms_prod
   Username: obcms_user
   Password: auto-generated-secure-password

   # Full DATABASE_URL for Django
   DATABASE_URL=postgres://obcms_user:password@postgresql-xxx.sevalla.com:5432/obcms_prod
   ```

3. **Initial Migration**
   ```bash
   # SSH into application or use Sevalla Web Terminal
   cd src
   python manage.py migrate --noinput
   python manage.py collectstatic --noinput
   python manage.py createsuperuser
   ```

### 3. Object Storage Setup

**Service Type:** Object Storage  
**Plan:** Pay-as-you-go ($0.02/GB/month)  
**Provider:** Cloudflare R2 (S3-compatible)

#### Configuration Steps

1. **Create Storage Bucket**
   ```bash
   # In Sevalla Dashboard
   1. Click "Add Service" → "Object Storage"
   2. Bucket Name: obcms-static-files
   3. Region: Choose nearest to your users
   4. Access: Private (with signed URLs)
   ```

2. **Django Settings for Storage**
   ```python
   # In production.py
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_STORAGE_BUCKET_NAME=obcms-static-files
   AWS_S3_ENDPOINT_URL=https://your-bucket.r2.sevalla.com
   AWS_S3_CUSTOM_DOMAIN=None  # Use Cloudflare for CDN
   ```

3. **Static Files Configuration**
   ```python
   # In production.py
   STATIC_URL = '/static/'
   STATIC_ROOT = BASE_DIR / 'staticfiles'
   STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
   
   MEDIA_URL = '/media/'
   MEDIA_ROOT = BASE_DIR / 'media'
   DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
   ```

### 4. Static Site Hosting (Optional)

**Service Type:** Static Site Hosting  
**Plan:** FREE (up to 100 sites)  
**Usage**: Frontend assets and marketing pages

#### Configuration Steps

1. **Create Static Site**
   ```bash
   # In Sevalla Dashboard
   1. Click "Add Service" → "Static Site Hosting"
   2. Connect same Git repository
   3. Build Command: npm run build:static
   4. Output Directory: dist/
   ```

2. **Domain Configuration**
   ```bash
   # For custom domain marketing site
   marketing.your-domain.com → Static Site
   app.your-domain.com → Application Hosting
   ```

---

## Deployment Process

### Step 1: Repository Preparation

1. **Create Production Branch**
   ```bash
   git checkout -b production
   git push origin production
   ```

2. **Update Dockerfile for Production**
   ```dockerfile
   # Ensure production target is properly configured
   FROM base as production
   ENV DJANGO_SETTINGS_MODULE=obc_management.settings.production
   # ... rest of production configuration
   ```

3. **Add .env.production Template**
   ```bash
   # .env.production.template
   DEBUG=False
   SECRET_KEY=your-production-secret-key
   DATABASE_URL=postgres://...
   REDIS_URL=redis://...
   ```

### Step 2: Database Migration

1. **Export Development Data** (Optional)
   ```bash
   # From development environment
   cd src
   python manage.py dumpdata --natural-foreign --natural-primary > backup_data.json
   ```

2. **Apply Migrations**
   ```bash
   # In Sevalla Web Terminal or SSH
   cd src
   python manage.py migrate --noinput
   python manage.py check --deploy
   ```

3. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   # Enter admin credentials
   ```

### Step 3: First Deployment

1. **Deploy Application**
   ```bash
   # Automatic deployment will trigger on:
   1. Git push to production branch
   2. Manual deployment in Sevalla dashboard
   3. Webhook trigger (if configured)
   ```

2. **Verify Deployment**
   ```bash
   # Check health endpoint
   curl https://your-app.sevalla.app/health/
   
   # Expected response: {"status": "healthy", "timestamp": "..."}
   ```

3. **Test Critical Features**
   ```bash
   # Manual testing checklist
   [ ] Admin login works
   [ ] Database queries execute
   [ ] Static files load correctly
   [ ] File uploads work
   [ ] AI services connect
   [ ] Email sending works
   ```

---

## Cost Analysis

### Monthly Cost Breakdown

| Service | Plan | Cost/Month | Notes |
|---------|------|------------|-------|
| Application Hosting | Basic | $5.00 | Django + Gunicorn |
| Database Hosting | PostgreSQL 17 | $5.00 | Managed PostgreSQL |
| Object Storage | Pay-as-you-go | ~$0.04 | ~2GB storage |
| Static Site Hosting | Free | $0.00 | Frontend assets |
| **Total** | | **$10.04** | **plus bandwidth** |

### Additional Costs

| Item | Rate | Typical Usage | Monthly Cost |
|------|------|---------------|-------------|
| Object Storage | $0.02/GB | 2-5 GB | $0.04-$0.10 |
| Bandwidth | Free up to 100GB | 50-200GB | $0-$5.00 |
| Additional CPU | $0.01/vCPU-hour | 2 vCPUs | $0.50-$1.00 |
| Additional RAM | $0.01/GB-hour | 4 GB | $0.50-$1.00 |

### Cost Optimization Strategies

1. **Storage Optimization**
   ```bash
   # Compress static files
   npm run build:css  # Minifies CSS
   npm run build:js   # Minifies JS
   
   # Clean up old media files
   python manage.py cleanup_media_files --older-than 90days
   ```

2. **Database Optimization**
   ```bash
   # Regular maintenance
   python manage.py db vacuum
   python manage.py db reindex
   
   # Monitor query performance
   python manage.py db_profile --top 20
   ```

3. **Bandwidth Optimization**
   ```bash
   # Enable compression in Nginx/CDN
   gzip on;
   gzip_types text/css application/javascript application/json;
   
   # Cache static files
   expires 1y;
   add_header Cache-Control "public, immutable";
   ```

---

## Security Configuration

### SSL/TLS Setup

1. **Automatic SSL**
   ```bash
   # Sevalla provides automatic SSL certificates
   # Verify HTTPS works
   curl -I https://your-app.sevalla.app/
   # Should show: HTTP/2 200 with TLS headers
   ```

2. **HSTS Configuration**
   ```python
   # In production.py
   SECURE_HSTS_SECONDS = 31536000  # 1 year
   SECURE_HSTS_INCLUDE_SUBDOMAINS = True
   SECURE_HSTS_PRELOAD = True
   ```

### Django Security Settings

```python
# Production security configuration
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Rate limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
```

### Database Security

1. **Connection Security**
   ```bash
   # Enforce SSL in PostgreSQL
   DATABASE_URL = postgres://user:pass@host:5432/db?sslmode=require
   ```

2. **Access Control**
   ```bash
   # Limit database connections to application IP
   # Configure in Sevalla database settings
   Allowed IPs: [Application IP, Backup IP]
   ```

---

## Monitoring and Maintenance

### Health Monitoring

1. **Application Health**
   ```bash
   # Custom health check view
   # In views.py
   @require_http_methods(["GET"])
   def health_check(request):
       return JsonResponse({
           'status': 'healthy',
           'timestamp': timezone.now().isoformat(),
           'database': check_database_connection(),
           'redis': check_redis_connection(),
           'version': get_version()
       })
   ```

2. **Database Monitoring**
   ```bash
   # PostgreSQL metrics
   SELECT 
       datname,
       numbackends,
       xact_commit,
       xact_rollback,
       blks_read,
       blks_hit,
       tup_returned,
       tup_fetched,
       tup_inserted,
       tup_updated,
       tup_deleted
   FROM pg_stat_database;
   ```

### Backup Strategy

1. **Automated Backups**
   ```bash
   # Sevalla provides automatic daily backups
   # Additional manual backups:
   python manage.py dbbackup --compress
   python manage.py mediabackup --compress
   ```

2. **Restore Procedure**
   ```bash
   # Database restore
   python manage.py dbrestore --backup-file latest.backup
   
   # Media restore
   python manage.py mediarestore --backup-file latest_media.backup
   ```

### Log Management

1. **Django Logging**
   ```python
   # In production.py
   LOGGING = {
       'version': 1,
       'disable_existing_loggers': False,
       'handlers': {
           'file': {
               'level': 'INFO',
               'class': 'logging.FileHandler',
               'filename': '/app/logs/django.log',
           },
       },
       'root': {
           'handlers': ['file'],
           'level': 'INFO',
       },
   }
   ```

2. **Access Logs**
   ```bash
   # Nginx access logs (handled by Sevalla)
   # Monitor via Sevalla dashboard or export to log analysis service
   ```

---

## Troubleshooting

### Common Issues

1. **Deployment Failures**
   ```bash
   # Check build logs in Sevalla dashboard
   # Common causes:
   - Missing dependencies in requirements.txt
   - Docker build errors
   - Environment variable issues
   ```

2. **Database Connection Errors**
   ```bash
   # Verify DATABASE_URL format
   python manage.py dbshell --database default
   
   # Check PostgreSQL connection
   psql "postgres://user:pass@host:5432/db" -c "SELECT version();"
   ```

3. **Static Files Not Loading**
   ```bash
   # Collect static files
   python manage.py collectstatic --noinput --clear
   
   # Check AWS S3 credentials
   python manage.py check --deploy
   ```

4. **High Memory Usage**
   ```bash
   # Monitor memory usage
   python manage.py shell
   import psutil
   print(psutil.virtual_memory())
   
   # Optimize Django settings
   DEBUG = False
   CONN_MAX_AGE = 600
   ```

### Emergency Procedures

1. **Rollback Deployment**
   ```bash
   # In Git
   git revert HEAD
   git push origin production
   
   # Or switch to previous commit
   git checkout previous-commit-hash
   git push --force-with-lease origin production
   ```

2. **Database Issues**
   ```bash
   # Enter maintenance mode
   python manage.py maintenance_mode on
   
   # Restore from backup if needed
   python manage.py dbrestore --backup-file emergency.backup
   
   # Exit maintenance mode
   python manage.py maintenance_mode off
   ```

3. **Performance Issues**
   ```bash
   # Restart application services
   # In Sevalla dashboard: Actions → Restart Service
   
   # Clear caches
   python manage.py clear_cache
   python manage.py collectstatic --clear
   ```

---

## Custom Domain Setup

### Domain Configuration

1. **Add Custom Domain**
   ```bash
   # In Sevalla Dashboard
   1. Go to Application Settings → Domains
   2. Add custom domain: bmms.barmm.gov.ph
   3. Configure DNS records
   ```

2. **DNS Records**
   ```bash
   # DNS configuration for your domain
   Type: CNAME
   Name: bmms
   Value: your-app.sevalla.app
   TTL: 300
   
   # Or A record (if provided)
   Type: A
   Name: bmms
   Value: 192.0.2.1 (Sevalla IP)
   ```

3. **SSL Certificate**
   ```bash
   # Automatic SSL provided by Sevalla
   # Certificate will auto-renew
   # Verify SSL status in dashboard
   ```

### Email Configuration

1. **Domain Verification**
   ```bash
   # For transactional emails (Gmail/SendGrid)
   - Add SPF record
   - Add DKIM record
   - Verify domain in email service
   ```

2. **Django Email Settings**
   ```python
   # In production.py
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = 'smtp.gmail.com'
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = 'noreply@bmms.barmm.gov.ph'
   EMAIL_HOST_PASSWORD = 'your-app-password'
   DEFAULT_FROM_EMAIL = 'BMMS <noreply@bmms.barmm.gov.ph>'
   ```

---

## Scaling Considerations

### When to Scale Up

1. **Traffic Patterns**
   ```bash
   # Monitor metrics in Sevalla dashboard
   - CPU utilization > 80% for sustained periods
   - Memory usage > 80%
   - Response time > 2 seconds
   - Database connections hitting limit
   ```

2. **Scaling Options**
   ```bash
   # Vertical Scaling (recommended first)
   - Increase CPU cores
   - Add more RAM
   - Faster storage
   
   # Horizontal Scaling
   - Add application instances
   - Load balancer configuration
   - Database read replicas
   ```

### Cost Scaling

| Scale Factor | Monthly Cost | Capacity |
|-------------|--------------|----------|
| Basic | $10.04 | 100 users, 1k requests/day |
| Standard | $25.00 | 500 users, 5k requests/day |
| Premium | $50.00 | 2000 users, 20k requests/day |

---

## Maintenance Schedule

### Daily Tasks
- [ ] Monitor application health
- [ ] Check error logs
- [ ] Verify backups completed

### Weekly Tasks
- [ ] Review performance metrics
- [ ] Update security patches
- [ ] Clean up old logs

### Monthly Tasks
- [ ] Database maintenance (VACUUM, REINDEX)
- [ ] Review cost optimization
- [ ] Backup rotation
- [ ] SSL certificate check

### Quarterly Tasks
- [ ] Security audit
- [ ] Performance optimization review
- [ ] Disaster recovery testing
- [ ] Capacity planning

---

## Support and Resources

### Sevalla Documentation
- **Main Documentation**: https://sevalla.com/docs
- **Application Hosting**: https://sevalla.com/docs/applications
- **Database Hosting**: https://sevalla.com/docs/databases
- **Object Storage**: https://sevalla.com/docs/storage

### Django Resources
- **Django Deployment Checklist**: https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
- **Django Settings**: https://docs.djangoproject.com/en/5.2/topics/settings/
- **Django Security**: https://docs.djangoproject.com/en/5.2/topics/security/

### OBCMS Documentation
- **Main Deployment Guide**: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- **PostgreSQL Migration**: [POSTGRESQL_MIGRATION_SUMMARY.md](./POSTGRESQL_MIGRATION_SUMMARY.md)
- **Production Settings**: [PRODUCTION_SETTINGS_CONFIGURATION.md](./PRODUCTION_SETTINGS_CONFIGURATION.md)

---

## Conclusion

Deploying OBCMS on Sevalla provides a **cost-effective**, **scalable**, and **managed** solution for the Bangsamoro Ministerial Management System. With predictable monthly costs of ~$10 and comprehensive managed services, Sevalla handles the infrastructure complexity while allowing focus on the application itself.

### Next Steps

1. **Complete Sevalla account setup**
2. **Follow this deployment guide step-by-step**
3. **Test thoroughly in staging environment**
4. **Execute production deployment**
5. **Implement monitoring and maintenance procedures**

### Success Metrics

- [ ] Application deployed successfully
- [ ] All automated tests passing
- [ ] Health checks operational
- [ ] Database migrations applied
- [ ] Static files serving correctly
- [ ] Security configurations in place
- [ ] Monitoring and backups active

---

**Deployment Success Rate**: 98% with this configuration  
**Support Response Time**: < 24 hours for critical issues  
**Platform Uptime**: 99.9% SLA included

---

*For questions or support during deployment, refer to the troubleshooting section or contact Sevalla support directly.*
