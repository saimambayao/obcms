# OBCMS Sevalla Deployment Documentation

**Last Updated:** October 15, 2025  
**Platform:** Sevalla (https://sevalla.com)  
**Application:** Bangsamoro Ministerial Management System (BMMS)  
**Total Monthly Cost:** ~$10.04

---

## 🚀 Complete Sevalla Deployment Guide

This directory contains everything you need to deploy OBCMS on Sevalla platform.

### 📋 Quick Start

1. **[Deployment Guide](./SEVALLA_DEPLOYMENT_GUIDE.md)** ⭐ - Complete step-by-step deployment
2. **[Environment Configuration](./SEVALLA_ENVIRONMENT_CONFIG.md)** - Environment variables setup
3. **[Settings Configuration](./SEVALLA_SETTINGS_CONFIG.md)** - Django settings for Sevalla
4. **[Cost Analysis](./SEVALLA_COST_ANALYSIS.md)** - Cost breakdown and optimization
5. **[Troubleshooting](./SEVALLA_TROUBLESHOOTING.md)** - Support and maintenance guide

---

## 📁 File Structure

```
docs/deployment/sevalla/
├── README.md                           # This file - Overview and quick start
├── SEVALLA_DEPLOYMENT_GUIDE.md          # ⭐ Main deployment guide
├── SEVALLA_ENVIRONMENT_CONFIG.md        # Environment variables template
├── SEVALLA_SETTINGS_CONFIG.md           # Django settings configuration
├── SEVALLA_COST_ANALYSIS.md             # Cost breakdown and optimization
├── SEVALLA_TROUBLESHOOTING.md          # Troubleshooting and maintenance
├── .env.production.template             # Environment variables template (copy to project root)
├── docker-compose.sevalla.yml           # Local testing configuration
├── issues/                              # Known issues and resolutions
│   └── CRASHED_STATUS_WITH_HEALTHY_CONTAINER.md  # ⚠️ Current investigation
└── scripts/                             # Deployment and monitoring scripts
    ├── sevalla-deploy.sh               # ⚡ Deployment automation script
    ├── sevalla-health-check.sh         # 🏥 Health monitoring script
    ├── validate-sevalla-settings.py    # Settings validation script
    └── cleanup-sevalla-backups.sh      # Backup cleanup script
```

---

## 🎯 Deployment Path

### Phase 1: Preparation (5-15 minutes)

1. **Configure Environment Variables**
   ```bash
   # Copy template to project root
   cp docs/deployment/sevalla/.env.production.template .env.production
   
   # Fill in your Sevalla credentials
   # See SEVALLA_ENVIRONMENT_CONFIG.md for details
   ```

2. **Update Django Settings**
   ```bash
   # Create Sevalla-specific settings file
   cp src/obc_management/settings/production.py src/obc_management/settings/sevalla.py
   
   # Apply configuration from SEVALLA_SETTINGS_CONFIG.md
   ```

3. **Test Locally (Optional)**
   ```bash
   # Test with Sevalla-style configuration locally
   docker-compose -f docs/deployment/sevalla/docker-compose.sevalla.yml up -d
   ```

### Phase 2: Sevalla Setup (10-20 minutes)

1. **Create Sevalla Account**
   - Sign up at https://sevalla.com
   - Choose Application Hosting ($5/month)
   - Choose Database Hosting - PostgreSQL 17 ($5/month)
   - Choose Object Storage for static files

2. **Configure Sevalla Services**
   - Application: Connect Git repository
   - Database: PostgreSQL 17 with credentials
   - Storage: Cloudflare R2 bucket setup
   - Custom domain (optional)

### Phase 3: Environment Variables (5-10 minutes)

1. **Database Configuration**
   ```bash
   # Get from Sevalla dashboard
   DB_NAME=obcms_prod
   DB_USER=obcms_user
   DB_PASSWORD=your-sevalla-db-password
   DB_HOST=postgresql-xxx.sevalla.com
   DATABASE_URL=postgres://obcms_user:password@host:5432/obcms_prod
   ```

2. **Storage Configuration**
   ```bash
   # Get from Sevalla dashboard  
   AWS_ACCESS_KEY_ID=your-r2-access-key
   AWS_SECRET_ACCESS_KEY=your-r2-secret-key
   AWS_STORAGE_BUCKET_NAME=obcms-static-files
   AWS_S3_ENDPOINT_URL=https://your-bucket.r2.sevalla.com
   ```

3. **Security Configuration**
   ```bash
   # Generate new secure key
   SECRET_KEY=your-new-secure-django-secret-key
   ALLOWED_HOSTS=your-domain.sevalla.app,*.sevalla.app
   ```

### Phase 4: Deployment (5-10 minutes)

1. **Push to Production**
   ```bash
   git add .
   git commit -m "Configure for Sevalla deployment"
   git push origin production
   ```

2. **Monitor Deployment**
   - Check Sevalla dashboard for build status
   - Verify health endpoint: `https://your-domain.sevalla.app/health/`
   - Test admin panel: `https://your-domain.sevalla.app/admin/`

---

## 🛠️ Deployment Scripts

### Automated Deployment

```bash
# Run complete deployment setup
./docs/deployment/sevalla/scripts/sevalla-deploy.sh production

# Generate secure secrets
./docs/deployment/sevalla/scripts/sevalla-deploy.sh --generate-secrets

# Quick deployment (skip tests)
./docs/deployment/sevalla/scripts/sevalla-deploy.sh production --skip-tests
```

### Health Monitoring

```bash
# Health check your deployed application
./docs/deployment/sevalla/scripts/sevalla-health-check.sh production bmms.barmm.gov.ph

# Continuous monitoring
./docs/deployment/sevalla/scripts/sevalla-health-check.sh production --monitor
```

### Validation

```bash
# Validate Django settings
python src/obc_management/settings/scripts/validate_sevalla_settings.py

# Django deployment check
python src/manage.py check --deploy --settings=obc_management.settings.sevalla
```

---

## 💰 Cost Summary

| Service | Monthly Cost | Annual Cost | Description |
|---------|-------------|-------------|-------------|
| **Application Hosting** | $5.00 | $60.00 | Django + Gunicorn |
| **Database Hosting** | $5.00 | $60.00 | PostgreSQL 17 |
| **Object Storage** | $0.04 | $0.48 | ~2GB storage |
| **Static Site Hosting** | $0.00 | $0.00 | FREE |
| **CDN** | $0.00 | $0.00 | Included |
| **SSL Certificates** | $0.00 | $0.00 | Auto-renewed |
| **Total** | **$10.04** | **$120.48** | **Complete infrastructure** |

### Cost Comparison

| Platform | Monthly Cost | Annual Cost | Savings |
|----------|-------------|-------------|---------|
| **Sevalla** | $10.04 | $120.48 | **85-90%** |
| AWS | $50-80 | $600-960 | +$480-840 |
| Google Cloud | $45-70 | $540-840 | +$420-720 |
| DigitalOcean | $25-40 | $300-480 | +$180-360 |

---

## 🔧 Configuration Files

### Environment Variables Template

Copy `.env.production.template` to your project root:
```bash
cp docs/deployment/sevalla/.env.production.template .env.production
```

**Required Variables to Configure:**
- `SECRET_KEY` - Generate new secure key
- `DATABASE_URL` - From Sevalla database service
- `REDIS_URL` - From Sevalla Redis service  
- `AWS_ACCESS_KEY_ID` - From Sevalla storage service
- `AWS_SECRET_ACCESS_KEY` - From Sevalla storage service
- `ALLOWED_HOSTS` - Your Sevalla domain(s)

### Docker Configuration

For local testing with Sevalla-style services:
```bash
# Start local test environment
docker-compose -f docs/deployment/sevalla/docker-compose.sevalla.yml up -d

# Check containers
docker-compose -f docs/deployment/sevalla/docker-compose.sevalla.yml ps

# View logs
docker-compose -f docs/deployment/sevalla/docker-compose.sevalla.yml logs -f web
```

### Django Settings

Apply Sevalla-specific configuration:
1. Create `src/obc_management/settings/sevalla.py`
2. Copy configuration from `SEVALLA_SETTINGS_CONFIG.md`
3. Update Dockerfile to use Sevalla settings

---

## 🏗️ Architecture Overview

### Sevalla Services

```
┌─────────────────────────────────────────────────────────────┐
│                    Sevalla Platform                        │
├─────────────────────────────────────────────────────────────┤
│  Application Hosting (Django + Gunicorn)                    │
│  ├─ Auto-deploys on git push                               │
│  ├─ 25 data center locations                                │
│  ├─ Auto-scaling                                            │
│  └─ Health monitoring                                      │
├─────────────────────────────────────────────────────────────┤
│  Database Hosting (PostgreSQL 17)                           │
│  ├─ Managed PostgreSQL                                      │
│  ├─ Automatic daily backups                                 │
│  ├─ Connection pooling                                      │
│  └─ Vertical scaling                                        │
├─────────────────────────────────────────────────────────────┤
│  Object Storage (Cloudflare R2)                             │
│  ├─ S3-compatible API                                       │
│  ├─ 6 storage locations                                    │
│  ├─ No ingress/egress fees                                 │
│  └─ Global CDN included                                    │
├─────────────────────────────────────────────────────────────┤
│  Static Site Hosting                                         │
│  ├─ Free tier                                              │
│  ├─ 260+ edge locations                                    │
│  ├─ Auto-deploys                                           │
│  └─ 100GB free bandwidth                                   │
└─────────────────────────────────────────────────────────────┘
```

### OBCMS Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    OBCMS Application                        │
├─────────────────────────────────────────────────────────────┤
│  Django 5.2 + DRF                                           │
│  ├─ Multi-tenant architecture (44 MOAs)                    │
│  ├─ PostgreSQL database                                     │
│  ├─ Redis caching                                            │
│  ├─ Celery background tasks                                 │
│  ├─ AI services (Google Gemini)                            │
│  └─ Static files (Tailwind CSS)                             │
├─────────────────────────────────────────────────────────────┤
│  BMMS Modules                                               │
│  ├─ Organization Management                                 │
│  ├─ Planning & Budgeting                                    │
│  ├─ Monitoring & Evaluation                                 │
│  ├─ Reports & Analytics                                     │
│  └─ AI Assistant                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚨 Support and Troubleshooting

### Known Issues

⚠️ **[ACTIVE ISSUE: Container Marked "Crashed" Despite Healthy State](./issues/CRASHED_STATUS_WITH_HEALTHY_CONTAINER.md)**
- **Status:** Under Investigation
- **Symptoms:** Application runs successfully but Sevalla shows "Crashed" status and returns 503 errors
- **Current Hypothesis:** Kubernetes readiness probe misconfiguration
- **See full documentation** for timeline, evidence, and recommended actions

### Quick Issues Resolution

| Issue | Solution |
|-------|----------|
| **Deployment fails** | Check build logs, verify environment variables |
| **Database connection** | Verify DATABASE_URL format and credentials |
| **Static files not loading** | Check AWS credentials and bucket permissions |
| **Performance issues** | Check resource usage, optimize queries |
| **Security errors** | Verify SSL configuration and security headers |
| **Crashed status** | See [known issue documentation](./issues/CRASHED_STATUS_WITH_HEALTHY_CONTAINER.md) |

### Health Checks

```bash
# Application health
curl https://your-domain.sevalla.app/health/

# Database connectivity
curl https://your-domain.sevalla.app/health/ | jq '.checks.database'

# Overall status
curl https://your-domain.sevalla.app/health/ | jq '.status'
```

### Monitoring

- **Sevalla Dashboard**: Real-time metrics and logs
- **Health Endpoint**: `/health/` for automated monitoring
- **Django Admin**: Application administration
- **Error Logs**: Comprehensive error tracking

---

## 📚 Additional Documentation

### Must-Read Documents

1. **[SEVALLA_DEPLOYMENT_GUIDE.md](./SEVALLA_DEPLOYMENT_GUIDE.md)** ⭐
   - Complete step-by-step deployment process
   - Service configuration details
   - Security best practices

2. **[SEVALLA_ENVIRONMENT_CONFIG.md](./SEVALLA_ENVIRONMENT_CONFIG.md)**
   - All environment variables documented
   - Configuration templates
   - Security considerations

3. **[SEVALLA_SETTINGS_CONFIG.md](./SEVALLA_SETTINGS_CONFIG.md)**
   - Django settings for Sevalla
   - Multi-environment support
   - Performance optimization

4. **[SEVALLA_TROUBLESHOOTING.md](./SEVALLA_TROUBLESHOOTING.md)**
   - Common issues and solutions
   - Maintenance procedures
   - Emergency response

### Known Issues Documentation

1. **[Container Marked Crashed Despite Healthy State](./issues/CRASHED_STATUS_WITH_HEALTHY_CONTAINER.md)** ⚠️
   - Comprehensive investigation of "Crashed" status paradox
   - Timeline of troubleshooting steps
   - Root cause analysis and recommended fixes
   - Status: Under active investigation

### Reference Documentation

- **[PostgreSQL Migration Summary](../POSTGRESQL_MIGRATION_SUMMARY.md)** - Database migration guide
- **[Production Settings Configuration](../PRODUCTION_SETTINGS_CONFIGURATION.md)** - General production settings
- **[Docker Deployment Guide](../docker-guide.md)** - Container deployment

---

## ✅ Deployment Checklist

### Pre-Deployment

- [ ] Create Sevalla account and select services
- [ ] Configure Git repository integration
- [ ] Set up database hosting (PostgreSQL 17)
- [ ] Configure object storage (R2 bucket)
- [ ] Prepare environment variables
- [ ] Create Django settings for Sevalla

### Deployment

- [ ] Push code to production branch
- [ ] Configure environment variables in Sevalla
- [ ] Monitor build process
- [ ] Verify deployment health
- [ ] Test critical functionality

### Post-Deployment

- [ ] Run database migrations
- [ ] Create admin user
- [ ] Configure email services
- [ ] Set up monitoring and alerts
- [ ] Document deployment details

---

## 🎯 Success Metrics

### Expected Results

- **Deployment Time**: 15-30 minutes
- **Total Cost**: $10.04/month (85-90% savings)
- **Performance**: < 2 second response times
- **Uptime**: 99.9% (Sevalla SLA)
- **Scalability**: Automatic vertical/horizontal scaling

### Validation Checklist

- [ ] Application responds on HTTPS
- [ ] Health check endpoint working
- [ ] Database connected and migrated
- [ ] Static files loading correctly
- [ ] Admin panel accessible
- [ ] Email services working
- [ ] AI services connected
- [ ] Monitoring active

---

**Ready to deploy!** 🚀

Start with the [Deployment Guide](./SEVALLA_DEPLOYMENT_GUIDE.md) and follow the step-by-step process.

---

*For questions or support, refer to the troubleshooting guide or contact the development team.*
