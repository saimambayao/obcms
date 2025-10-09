# OBCMS Docker Deployment Guide

**Last Updated:** October 9, 2025
**PostgreSQL Migration:** Complete ✅
**Production Ready:** Yes ✅

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Deployment Options](#deployment-options)
5. [Production Deployment](#production-deployment)
6. [Database Management](#database-management)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Overview

OBCMS uses Docker for containerized deployment with the following services:

| Service | Image | Purpose | Port |
|---------|-------|---------|------|
| **db** | postgres:17-alpine | PostgreSQL database | 5432 |
| **redis** | redis:7-alpine | Cache & Celery broker | 6379 |
| **web** | obcms:production | Django application (Gunicorn) | 8000 |
| **celery** | obcms:production | Background task worker | - |
| **celery-beat** | obcms:production | Scheduled task scheduler | - |
| **nginx** | nginx:alpine | Reverse proxy (optional) | 80, 443 |

**Architecture:**
```
Client → Nginx → Gunicorn (web) → PostgreSQL (db)
                                  ↘ Redis (redis)
                                      ↓
                                  Celery (worker) ← Celery Beat (scheduler)
```

---

## Prerequisites

### System Requirements

**Minimum (Development/Staging):**
- 2 CPU cores
- 4 GB RAM
- 20 GB disk space
- Docker 20.10+
- Docker Compose 2.0+

**Recommended (Production):**
- 4 CPU cores
- 8 GB RAM
- 50 GB disk space (including backups)
- Docker 24.0+
- Docker Compose 2.20+

### Software Requirements

1. **Docker & Docker Compose**
   ```bash
   # Install Docker (Ubuntu/Debian)
   curl -fsSL https://get.docker.com | sh

   # Install Docker Compose
   sudo apt-get install docker-compose-plugin

   # Verify installation
   docker --version
   docker compose version
   ```

2. **Git** (for deployment)
   ```bash
   sudo apt-get install git
   ```

3. **Optional: Certbot** (for SSL certificates)
   ```bash
   sudo apt-get install certbot
   ```

---

## Quick Start

### Development Environment

```bash
# 1. Clone repository
git clone https://github.com/your-org/obcms.git
cd obcms

# 2. Start development stack
docker-compose up -d

# 3. Access application
open http://localhost:8000

# 4. View logs
docker-compose logs -f web
```

**Default Credentials:**
- Admin URL: http://localhost:8000/admin/
- Username: `admin` (create with `docker-compose exec web python src/manage.py createsuperuser`)

---

## Deployment Options

### Option 1: Docker Compose (Recommended for VPS)

**Best For:** VPS deployments (DigitalOcean, AWS EC2, Linode)

**Advantages:**
- ✅ Full control over configuration
- ✅ Easy to customize
- ✅ Works on any Docker-compatible host
- ✅ Supports custom SSL certificates

**Deployment Steps:** See [Production Deployment](#production-deployment)

---

### Option 2: Coolify (Recommended for Ease of Use)

**Best For:** Quick deployments, automatic SSL, built-in monitoring

**Advantages:**
- ✅ Automatic SSL with Let's Encrypt
- ✅ Built-in monitoring dashboard
- ✅ Zero-downtime deployments
- ✅ GitHub/GitLab integration
- ✅ One-click rollbacks

**Deployment Steps:**

1. **Install Coolify** (on your server)
   ```bash
   curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
   ```

2. **Access Coolify Dashboard**
   - Navigate to `http://your-server-ip:3000`
   - Complete initial setup

3. **Create New Project**
   - Click "New Project"
   - Select "Docker Compose"
   - Paste `docker-compose.prod.yml` contents

4. **Configure Environment**
   - Copy variables from `.env.production.template`
   - Set all required values (SECRET_KEY, passwords, domains)

5. **Deploy**
   - Click "Deploy"
   - Coolify handles SSL, reverse proxy, and monitoring automatically

**Reference:** [Coolify Deployment Checklist](deployment-coolify.md)

---

### Option 3: Kubernetes (Enterprise)

**Best For:** Large-scale deployments, multi-region, high availability

**Advantages:**
- ✅ Auto-scaling
- ✅ Self-healing
- ✅ Load balancing
- ✅ Rolling updates

**Status:** Kubernetes manifests available on request

---

## Production Deployment

### Step 1: Prepare Server

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt-get install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

---

### Step 2: Clone Repository

```bash
# Clone OBCMS
git clone https://github.com/your-org/obcms.git
cd obcms

# Checkout production branch (or main)
git checkout production
```

---

### Step 3: Configure Environment

```bash
# Copy production template
cp .env.production.template .env.production

# Edit configuration
nano .env.production
```

**CRITICAL Configuration Items:**

1. **SECRET_KEY** (MUST CHANGE)
   ```bash
   # Generate a new secret key
   python3 -c "from secrets import token_urlsafe; print(token_urlsafe(50))"

   # Or use Django's utility
   docker run --rm python:3.12-slim python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **DEBUG** (MUST be 0)
   ```env
   DEBUG=0
   ```

3. **ALLOWED_HOSTS** (Your domain)
   ```env
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

4. **CSRF_TRUSTED_ORIGINS** (HTTPS URLs)
   ```env
   CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

5. **POSTGRES_PASSWORD** (Strong password)
   ```env
   POSTGRES_PASSWORD=$(openssl rand -base64 32)
   ```

6. **Email Configuration** (SMTP)
   ```env
   EMAIL_HOST=smtp.yourdomain.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=1
   EMAIL_HOST_USER=noreply@yourdomain.com
   EMAIL_HOST_PASSWORD=your-email-password
   ```

**Configuration Checklist:**
- [ ] SECRET_KEY changed from template
- [ ] DEBUG=0
- [ ] ALLOWED_HOSTS set to your domain(s)
- [ ] CSRF_TRUSTED_ORIGINS set with https://
- [ ] POSTGRES_PASSWORD changed to secure password
- [ ] Email SMTP configured
- [ ] Security headers enabled

---

### Step 4: Deploy with Deployment Script

```bash
# Make deployment script executable
chmod +x scripts/deploy-production.sh

# Run deployment
./scripts/deploy-production.sh
```

**What the script does:**
1. ✅ Validates environment configuration
2. ✅ Stops existing containers
3. ✅ Builds fresh production images
4. ✅ Starts database and Redis
5. ✅ Runs database migrations
6. ✅ Starts all services
7. ✅ Runs health checks
8. ✅ Displays deployment summary

**Expected Output:**
```
================================
OBCMS Production Deployment
================================

⚙ Validating environment configuration...
✓ Environment configuration validated

⚙ Stopping existing containers...
✓ Containers stopped

⚙ Building production images...
✓ Images built successfully

⚙ Starting database and redis...
✓ Database and redis started

⚙ Running database migrations...
✓ Migrations complete

⚙ Starting all services...
✓ All services started

================================
✓ Deployment Complete!
================================
```

---

### Step 5: Create Superuser

```bash
# Create admin user
docker-compose -f docker-compose.prod.yml exec web python src/manage.py createsuperuser

# Follow prompts to set username, email, password
```

---

### Step 6: Configure Reverse Proxy (If Using Nginx)

**Option A: Use Included Nginx Service**

The `docker-compose.prod.yml` includes an optional Nginx service. To use it:

1. **Generate SSL Certificates**
   ```bash
   # Using Certbot (Let's Encrypt)
   sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

   # Certificates will be in /etc/letsencrypt/live/yourdomain.com/
   ```

2. **Copy Certificates to Project**
   ```bash
   mkdir -p ssl
   sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/
   sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/
   sudo chown $USER:$USER ssl/*.pem
   ```

3. **Update nginx.conf**
   ```bash
   # Edit nginx.conf to set your server_name
   nano nginx.conf

   # Change: server_name _;
   # To: server_name yourdomain.com www.yourdomain.com;
   ```

4. **Restart Nginx**
   ```bash
   docker-compose -f docker-compose.prod.yml restart nginx
   ```

**Option B: Use External Nginx**

If you already have Nginx running on your host:

```nginx
# /etc/nginx/sites-available/obcms.conf

upstream obcms {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    client_max_body_size 50M;

    location /static/ {
        alias /path/to/obcms/staticfiles/;
    }

    location /media/ {
        alias /path/to/obcms/media/;
    }

    location / {
        proxy_pass http://obcms;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
}
```

---

### Step 7: Verify Deployment

```bash
# 1. Check service status
docker-compose -f docker-compose.prod.yml ps

# Expected: All services "Up" and "healthy"

# 2. Check logs for errors
docker-compose -f docker-compose.prod.yml logs web | grep -i error

# 3. Test health endpoint
curl https://yourdomain.com/health/

# Expected: "healthy"

# 4. Test admin login
open https://yourdomain.com/admin/
```

---

## Database Management

### Backups

**Automated Daily Backups:**

```bash
# Create cron job for daily backups
crontab -e

# Add this line (runs daily at 2 AM):
0 2 * * * /path/to/obcms/scripts/backup-database.sh
```

**Manual Backup:**

```bash
# Create backup
./scripts/backup-database.sh

# Backups saved to: backups/postgres/obcms_backup_YYYYMMDD_HHMMSS.sql.gz
```

**Backup to Remote Storage (Recommended):**

```bash
# Example: Upload to S3 after backup
./scripts/backup-database.sh
aws s3 cp backups/postgres/obcms_backup_$(date +%Y%m%d)_*.sql.gz \
    s3://your-bucket/obcms-backups/
```

---

### Restore from Backup

```bash
# Restore from backup file
./scripts/restore-database.sh backups/postgres/obcms_backup_20251009_120000.sql.gz

# Confirm when prompted
```

**⚠️ WARNING:** Restore will replace the current database!

---

### Database Shell Access

```bash
# PostgreSQL shell
docker-compose -f docker-compose.prod.yml exec db psql -U obcms_user -d obcms_prod

# Common queries:
# \dt               - List tables
# \d+ tablename     - Describe table
# SELECT COUNT(*) FROM auth_user;  - Count users
# \q                - Quit
```

---

## Monitoring & Maintenance

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f web

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 web

# Since timestamp
docker-compose -f docker-compose.prod.yml logs --since 2025-10-09T10:00:00 web
```

---

### Service Management

```bash
# Restart specific service
docker-compose -f docker-compose.prod.yml restart web

# Restart all services
docker-compose -f docker-compose.prod.yml restart

# Stop all services
docker-compose -f docker-compose.prod.yml stop

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Remove all containers (data persists in volumes)
docker-compose -f docker-compose.prod.yml down
```

---

### Update Deployment

```bash
# 1. Pull latest code
git pull origin production

# 2. Rebuild and redeploy
./scripts/deploy-production.sh

# 3. Verify deployment
docker-compose -f docker-compose.prod.yml ps
```

---

### Database Migrations

```bash
# Run pending migrations
docker-compose -f docker-compose.prod.yml exec web python src/manage.py migrate

# Check migration status
docker-compose -f docker-compose.prod.yml exec web python src/manage.py showmigrations

# Create new migrations (after model changes)
docker-compose -f docker-compose.prod.yml exec web python src/manage.py makemigrations
```

---

### Django Shell Access

```bash
# Open Django shell
docker-compose -f docker-compose.prod.yml exec web python src/manage.py shell

# Common tasks:
# from django.contrib.auth import get_user_model
# User = get_user_model()
# User.objects.count()  # Count users
```

---

## Troubleshooting

### Service Won't Start

**Check logs:**
```bash
docker-compose -f docker-compose.prod.yml logs <service-name>
```

**Common Issues:**

1. **Database connection refused**
   - Check if database is healthy: `docker-compose -f docker-compose.prod.yml ps db`
   - Verify DATABASE_URL in .env.production

2. **Migration errors**
   - Check migration status: `docker-compose -f docker-compose.prod.yml exec web python src/manage.py showmigrations`
   - Run migrations manually: `docker-compose -f docker-compose.prod.yml exec web python src/manage.py migrate`

3. **Permission denied errors**
   - Check volume ownership: `docker-compose -f docker-compose.prod.yml exec web ls -la /app`
   - Rebuild with: `docker-compose -f docker-compose.prod.yml build --no-cache`

---

### 502 Bad Gateway (Nginx)

**Possible Causes:**

1. **Web service not running**
   ```bash
   docker-compose -f docker-compose.prod.yml ps web
   docker-compose -f docker-compose.prod.yml logs web
   ```

2. **Gunicorn timeout**
   - Increase timeout in `gunicorn.conf.py`
   - Check for long-running database queries

3. **Out of memory**
   - Check system resources: `free -h`
   - Reduce Gunicorn workers in .env.production

---

### Database Performance Issues

**Check Connection Pool:**
```bash
docker-compose -f docker-compose.prod.yml exec db psql -U obcms_user -d obcms_prod -c \
    "SELECT count(*) FROM pg_stat_activity WHERE datname='obcms_prod';"
```

**Check Slow Queries:**
```bash
docker-compose -f docker-compose.prod.yml exec db psql -U obcms_user -d obcms_prod -c \
    "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"
```

---

### Disk Space Issues

**Check Volume Usage:**
```bash
docker system df
docker volume ls
du -sh /var/lib/docker/volumes/*
```

**Clean Up:**
```bash
# Remove unused images
docker image prune -a

# Remove unused volumes (⚠️ CAUTION: May delete data)
docker volume prune

# Clean build cache
docker builder prune
```

---

## Security Checklist

Before deploying to production:

- [ ] SECRET_KEY changed from template (50+ characters)
- [ ] DEBUG=0 in .env.production
- [ ] ALLOWED_HOSTS configured with actual domain(s)
- [ ] CSRF_TRUSTED_ORIGINS configured with https:// URLs
- [ ] All passwords changed from defaults
- [ ] SSL certificates configured (HTTPS)
- [ ] Security headers enabled (HSTS, CSP, etc.)
- [ ] Firewall configured (allow only 80, 443, 22)
- [ ] SSH key authentication (disable password login)
- [ ] Regular backups automated
- [ ] Monitoring and alerting set up
- [ ] Database access restricted (not exposed publicly)

---

## Additional Resources

- **[PostgreSQL Migration Report](POSTGRESQL_MIGRATION_REPORT_20251009.md)** - Migration details
- **[Coolify Deployment](deployment-coolify.md)** - Coolify-specific guide
- **[Staging Environment](../env/staging-complete.md)** - Staging setup
- **[Production Settings](../../src/obc_management/settings/production.py)** - Django production config

---

## Support

**Issues:** https://github.com/your-org/obcms/issues
**Documentation:** https://docs.obcms.gov.ph
**Contact:** support@obcms.gov.ph

---

**End of Docker Deployment Guide**
