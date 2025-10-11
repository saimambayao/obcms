# Production Deployment Guide
# Integrated Project Management System - OBCMS

**Version:** 1.0
**Date:** October 1, 2025
**Status:** Production Ready (Backend Complete)

---

## Pre-Deployment Checklist

### System Requirements

- [ ] **Server:** Ubuntu 22.04 LTS or similar (2+ CPU, 4GB+ RAM, 50GB+ storage)
- [ ] **Database:** PostgreSQL 14+ (recommended) or MySQL 8+
- [ ] **Cache/Queue:** Redis 6+
- [ ] **Python:** Python 3.12
- [ ] **Web Server:** Nginx
- [ ] **Application Server:** Gunicorn
- [ ] **Process Manager:** Supervisor or systemd
- [ ] **SSL Certificate:** For HTTPS (Let's Encrypt recommended)

### Software Dependencies

```bash
# System packages (Ubuntu)
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv python3-pip postgresql postgresql-contrib redis-server nginx supervisor git

# Python packages
pip install -r requirements/production.txt
```

### Environment Variables

Create `/opt/obcms/.env` file:

```env
# Django Core
SECRET_KEY=<generate-50+-character-random-key>
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DATABASE_URL=postgres://obcms_user:strong_password@localhost:5432/obcms_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=<app-specific-password>

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Static & Media
STATIC_ROOT=/opt/obcms/static/
MEDIA_ROOT=/opt/obcms/media/

# Sentry (Optional but recommended)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

---

## Step 1: Server Setup

### 1.1 Create Application User

```bash
sudo useradd -r -s /bin/bash -d /opt/obcms -m obcms
sudo su - obcms
```

### 1.2 Clone Repository

```bash
cd /opt/obcms
git clone https://github.com/your-org/obcms.git code
cd code
```

### 1.3 Create Virtual Environment

```bash
python3.12 -m venv /opt/obcms/venv
source /opt/obcms/venv/bin/activate
pip install --upgrade pip
pip install -r requirements/production.txt
```

---

## Step 2: Database Setup

### 2.1 Create PostgreSQL Database

```bash
sudo -u postgres psql

CREATE DATABASE obcms_db;
CREATE USER obcms_user WITH PASSWORD 'strong_password_here';
ALTER ROLE obcms_user SET client_encoding TO 'utf8';
ALTER ROLE obcms_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE obcms_user SET timezone TO 'Asia/Manila';
GRANT ALL PRIVILEGES ON DATABASE obcms_db TO obcms_user;
\q
```

### 2.2 Run Migrations

```bash
cd /opt/obcms/code/src
../venv/bin/python manage.py migrate
```

### 2.3 Create Superuser

```bash
../venv/bin/python manage.py createsuperuser
```

### 2.4 Collect Static Files

```bash
../venv/bin/python manage.py collectstatic --noinput
```

---

## Step 3: Redis Setup

### 3.1 Configure Redis

```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 3.2 Test Redis Connection

```bash
redis-cli ping
# Should return: PONG
```

---

## Step 4: Gunicorn Setup

### 4.1 Create Gunicorn Socket File

Create `/etc/systemd/system/gunicorn_obcms.socket`:

```ini
[Unit]
Description=gunicorn socket for OBCMS

[Socket]
ListenStream=/run/gunicorn_obcms.sock

[Install]
WantedBy=sockets.target
```

### 4.2 Create Gunicorn Service File

Create `/etc/systemd/system/gunicorn_obcms.service`:

```ini
[Unit]
Description=gunicorn daemon for OBCMS
Requires=gunicorn_obcms.socket
After=network.target

[Service]
Type=notify
User=obcms
Group=www-data
RuntimeDirectory=gunicorn
WorkingDirectory=/opt/obcms/code/src
Environment="PATH=/opt/obcms/venv/bin"
ExecStart=/opt/obcms/venv/bin/gunicorn \
          --workers 4 \
          --worker-class=sync \
          --max-requests 1000 \
          --max-requests-jitter 50 \
          --timeout 60 \
          --bind unix:/run/gunicorn_obcms.sock \
          --access-logfile /opt/obcms/logs/gunicorn_access.log \
          --error-logfile /opt/obcms/logs/gunicorn_error.log \
          obc_management.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 4.3 Start Gunicorn

```bash
sudo systemctl daemon-reload
sudo systemctl enable gunicorn_obcms.socket
sudo systemctl start gunicorn_obcms.socket
sudo systemctl status gunicorn_obcms.socket
```

---

## Step 5: Celery Setup

### 5.1 Create Celery Worker Service

Create `/etc/systemd/system/celery_obcms.service`:

```ini
[Unit]
Description=Celery Worker for OBCMS
After=network.target

[Service]
Type=forking
User=obcms
Group=obcms
EnvironmentFile=/opt/obcms/.env
WorkingDirectory=/opt/obcms/code/src
ExecStart=/opt/obcms/venv/bin/celery -A obc_management worker \
          --loglevel=info \
          --logfile=/opt/obcms/logs/celery_worker.log \
          --pidfile=/opt/obcms/run/celery_worker.pid
Restart=always

[Install]
WantedBy=multi-user.target
```

### 5.2 Create Celery Beat Service

Create `/etc/systemd/system/celerybeat_obcms.service`:

```ini
[Unit]
Description=Celery Beat for OBCMS
After=network.target

[Service]
Type=simple
User=obcms
Group=obcms
EnvironmentFile=/opt/obcms/.env
WorkingDirectory=/opt/obcms/code/src
ExecStart=/opt/obcms/venv/bin/celery -A obc_management beat \
          --loglevel=info \
          --logfile=/opt/obcms/logs/celery_beat.log \
          --pidfile=/opt/obcms/run/celery_beat.pid
Restart=always

[Install]
WantedBy=multi-user.target
```

### 5.3 Start Celery Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable celery_obcms celerybeat_obcms
sudo systemctl start celery_obcms celerybeat_obcms
sudo systemctl status celery_obcms celerybeat_obcms
```

---

## Step 6: Nginx Setup

### 6.1 Create Nginx Configuration

Create `/etc/nginx/sites-available/obcms`:

```nginx
upstream obcms_app {
    server unix:/run/gunicorn_obcms.sock fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers "EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH";

    client_max_body_size 100M;

    access_log /opt/obcms/logs/nginx_access.log;
    error_log /opt/obcms/logs/nginx_error.log;

    location /static/ {
        alias /opt/obcms/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /opt/obcms/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://obcms_app;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 6.2 Enable Site and Restart Nginx

```bash
sudo ln -s /etc/nginx/sites-available/obcms /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6.3 Setup SSL with Let's Encrypt

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

---

## Step 7: Monitoring & Logging

### 7.1 Setup Sentry (Error Tracking)

```bash
pip install sentry-sdk

# Add to settings/production.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=env('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False,
)
```

### 7.2 Setup Log Rotation

Create `/etc/logrotate.d/obcms`:

```
/opt/obcms/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 obcms obcms
    sharedscripts
    postrotate
        systemctl reload gunicorn_obcms
    endscript
}
```

### 7.3 Create Log Directories

```bash
sudo mkdir -p /opt/obcms/logs /opt/obcms/run
sudo chown -R obcms:obcms /opt/obcms/logs /opt/obcms/run
```

---

## Step 8: Backups

### 8.1 Database Backup Script

Create `/opt/obcms/scripts/backup_db.sh`:

```bash
#!/bin/bash
BACKUP_DIR=/opt/obcms/backups
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

pg_dump obcms_db | gzip > $BACKUP_DIR/obcms_db_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "obcms_db_*.sql.gz" -mtime +30 -delete
```

### 8.2 Setup Cron for Daily Backups

```bash
sudo crontab -e

# Add:
0 2 * * * /opt/obcms/scripts/backup_db.sh
```

---

## Step 9: Security Hardening

### 9.1 Firewall Configuration

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 9.2 Fail2ban Setup

```bash
sudo apt-get install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 9.3 Security Headers

Already configured in settings/production.py:
- SECURE_SSL_REDIRECT
- SECURE_HSTS_SECONDS
- SESSION_COOKIE_SECURE
- CSRF_COOKIE_SECURE

---

## Step 10: Post-Deployment Verification

### 10.1 Health Checks

```bash
# Check all services
sudo systemctl status gunicorn_obcms
sudo systemctl status celery_obcms
sudo systemctl status celerybeat_obcms
sudo systemctl status nginx
sudo systemctl status redis-server
sudo systemctl status postgresql

# Check logs
tail -f /opt/obcms/logs/gunicorn_error.log
tail -f /opt/obcms/logs/celery_worker.log
tail -f /opt/obcms/logs/nginx_error.log
```

### 10.2 Test Endpoints

```bash
# Homepage
curl -I https://your-domain.com/

# Admin
curl -I https://your-domain.com/admin/

# API
curl -I https://your-domain.com/api/

# Static files
curl -I https://your-domain.com/static/admin/css/base.css
```

### 10.3 Test Celery Tasks

```bash
cd /opt/obcms/code/src
../venv/bin/python manage.py shell

from project_central.tasks import generate_daily_alerts_task
result = generate_daily_alerts_task.delay()
print(result.get())
```

---

## Troubleshooting

### Issue: Gunicorn Won't Start

**Check logs:**
```bash
sudo journalctl -u gunicorn_obcms -n 50
```

**Common fixes:**
- Check socket file permissions
- Verify Python path in service file
- Check database connectivity

### Issue: Celery Tasks Not Running

**Check:**
```bash
sudo systemctl status celery_obcms
tail -f /opt/obcms/logs/celery_worker.log
```

**Common fixes:**
- Verify Redis is running
- Check CELERY_BROKER_URL in settings
- Restart celery services

### Issue: Static Files Not Loading

**Fix:**
```bash
cd /opt/obcms/code/src
../venv/bin/python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

---

## Maintenance

### Updating the Application

```bash
sudo su - obcms
cd /opt/obcms/code
git pull origin main
source /opt/obcms/venv/bin/activate
pip install -r requirements/production.txt
cd src
../venv/bin/python manage.py migrate
../venv/bin/python manage.py collectstatic --noinput
sudo systemctl restart gunicorn_obcms
sudo systemctl restart celery_obcms
sudo systemctl restart celerybeat_obcms
```

### Monitoring Disk Space

```bash
df -h
du -sh /opt/obcms/*
```

### Database Maintenance

```bash
# Vacuum database
sudo -u postgres psql obcms_db -c "VACUUM ANALYZE;"

# Check database size
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('obcms_db'));"
```

#### Coordination Partner Organization Location Upgrade

- Run `./manage.py migrate` inside `src/` to apply the new geographic columns on `coordination.Organization`.
- Execute `./manage.py backfill_organization_locations --dry-run` to preview inferred headquarters matches, then re-run without `--dry-run` when you are ready to persist updates.
- To reprocess a specific record after manual corrections, call `./manage.py backfill_organization_locations --organization <uuid>`.

---

## Production Checklist

- [ ] All services running (Gunicorn, Celery, Nginx, PostgreSQL, Redis)
- [ ] SSL certificate installed and auto-renewal configured
- [ ] Database backups automated
- [ ] Log rotation configured
- [ ] Firewall enabled
- [ ] Sentry error tracking configured
- [ ] Email notifications working
- [ ] Static files served correctly
- [ ] Admin interface accessible
- [ ] Celery tasks executing on schedule
- [ ] Monitoring dashboard set up
- [ ] Documentation accessible to team

---

**Deployment Guide Version:** 1.0
**Last Updated:** October 1, 2025
**Contact:** DevOps Team - devops@oobc.gov.ph
