# OBCMS AI Deployment Runbook

**Quick Reference Guide for Production Deployment**

---

## 🚀 Quick Deployment (30 Minutes)

### Prerequisites Checklist
- [ ] Python 3.12+ installed
- [ ] PostgreSQL 14+ running
- [ ] Redis 6+ running
- [ ] Domain with SSL configured
- [ ] Google Gemini API key (from https://ai.google.dev/)

### Step 1: Clone & Setup (5 min)
```bash
# Clone repository
git clone https://github.com/tech-bangsamoro/obcms.git
cd obcms

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements/base.txt
```

### Step 2: Environment Configuration (5 min)
```bash
# Copy template
cp .env.example .env

# Generate SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Edit .env with required values
nano .env
```

**Required .env Variables:**
```bash
# Django Core
SECRET_KEY=<generated-50-char-key>
DEBUG=0
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Database
DATABASE_URL=postgres://user:pass@localhost:5432/obcms_prod

# Redis & Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

# Google Gemini AI
GOOGLE_API_KEY=<your-gemini-api-key>

# Email (Production SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=<app-password>
```

### Step 3: Database Setup (5 min)
```bash
cd src

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### Step 4: AI System Initialization (5 min)
```bash
# Health check
python manage.py ai_health_check

# Index initial data
python manage.py index_communities

# Test AI service
python manage.py shell -c "
from ai_assistant.services import GeminiService
service = GeminiService()
result = service.generate_text('Hello')
print('✓ AI service working' if result['success'] else '✗ AI service failed')
"
```

### Step 5: Start Services (10 min)
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery Worker
cd src
celery -A obc_management worker -l info

# Terminal 3: Celery Beat
cd src
celery -A obc_management beat -l info

# Terminal 4: Gunicorn
gunicorn obc_management.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 120
```

### Step 6: Verification
```bash
# Run verification script
./scripts/verify_ai.sh

# Access admin panel
# https://yourdomain.com/admin/
# Navigate to: AI Assistant → AI Operations
```

---

## 🔒 Security Checklist (Critical)

### Before Going Live
- [ ] `DEBUG=0` in .env
- [ ] `SECRET_KEY` is 50+ characters (generated)
- [ ] `GOOGLE_API_KEY` set in .env (not in code)
- [ ] `ALLOWED_HOSTS` configured with production domains
- [ ] `CSRF_TRUSTED_ORIGINS` includes https:// scheme
- [ ] SSL/TLS certificates installed (Let's Encrypt)
- [ ] HTTPS redirect active (`SECURE_SSL_REDIRECT=1`)
- [ ] Rate limiting active (default DRF throttling)
- [ ] Dangerous query blocking verified (Chat AI)
- [ ] All security headers configured

### Security Verification
```bash
# Django deployment check
cd src
python manage.py check --deploy

# Expected: System check identified no issues (0 silenced).
```

---

## 🛠️ Infrastructure Setup

### Redis Installation
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis
sudo systemctl enable redis

# Verify
redis-cli ping  # Should return: PONG
```

### PostgreSQL Setup
```bash
# Create database
sudo -u postgres psql

postgres=# CREATE DATABASE obcms_prod ENCODING 'UTF8';
postgres=# CREATE USER obcms_user WITH PASSWORD 'secure-password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE obcms_prod TO obcms_user;
postgres=# \q

# Update .env
DATABASE_URL=postgres://obcms_user:secure-password@localhost:5432/obcms_prod
```

### Nginx Configuration
```nginx
# /etc/nginx/sites-available/obcms
server {
    listen 80;
    server_name obcms.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name obcms.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/obcms.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/obcms.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /static/ {
        alias /path/to/obcms/src/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /path/to/obcms/src/media/;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/obcms /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot --nginx -d obcms.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### Supervisor (Process Management)
```ini
# /etc/supervisor/conf.d/obcms.conf
[program:obcms_web]
command=/path/to/venv/bin/gunicorn obc_management.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120
directory=/path/to/obcms/src
user=www-data
autostart=true
autorestart=true
stdout_logfile=/var/log/obcms/web.log
stderr_logfile=/var/log/obcms/web_err.log

[program:obcms_celery_worker]
command=/path/to/venv/bin/celery -A obc_management worker -l info
directory=/path/to/obcms/src
user=www-data
autostart=true
autorestart=true
stdout_logfile=/var/log/obcms/celery_worker.log
stderr_logfile=/var/log/obcms/celery_worker_err.log

[program:obcms_celery_beat]
command=/path/to/venv/bin/celery -A obc_management beat -l info
directory=/path/to/obcms/src
user=www-data
autostart=true
autorestart=true
stdout_logfile=/var/log/obcms/celery_beat.log
stderr_logfile=/var/log/obcms/celery_beat_err.log
```

```bash
# Load configuration
sudo supervisorctl reread
sudo supervisorctl update

# Start all services
sudo supervisorctl start all

# Check status
sudo supervisorctl status
```

---

## 📊 Monitoring & Cost Management

### Cost Tracking Commands
```bash
# Get daily/monthly costs
cd src
python manage.py shell

>>> from ai_assistant.utils import CostTracker
>>> tracker = CostTracker()
>>> print(f"Today: ${tracker.get_daily_cost():.2f}")
>>> print(f"Month: ${tracker.get_monthly_cost():.2f}")
>>> exit()
```

### Budget Alerts
```python
# In Django shell
from ai_assistant.utils import CostTracker
from decimal import Decimal

tracker = CostTracker()
alerts = tracker.check_budget_alert(
    daily_budget=Decimal('10.00'),
    monthly_budget=Decimal('100.00')
)

if alerts['has_alerts']:
    for alert in alerts['alerts']:
        print(f"{alert['severity'].upper()}: {alert['message']}")
```

### View AI Operations (Admin Panel)
```
URL: https://yourdomain.com/admin/ai_assistant/aioperation/

Filters:
- Operation type (chat, analysis, document_generation)
- Module (MANA, Coordination, Communities, etc.)
- Success/failure
- Cached vs. fresh
- Date range
```

### Daily Cost Report
```bash
cd src
python manage.py shell

>>> from ai_assistant.utils import DailyCostReport
>>> report = DailyCostReport()
>>> print(report.format_report())
```

---

## 🔍 Health Checks & Verification

### AI System Health Check
```bash
cd src
python manage.py ai_health_check

# Expected output:
# ========================================
# AI INFRASTRUCTURE HEALTH CHECK
# ========================================
# 1. Checking Google API Key...
#    ✓ API Key configured
# 2. Checking Gemini Service...
#    ✓ Gemini API connection successful
# 3. Checking Cache (Redis)...
#    ✓ Cache operational
# 4. Checking AI Models...
#    ✓ All models accessible
# ========================================
# ✓ ALL CHECKS PASSED
# ========================================
```

### Service Status Checks
```bash
# Redis
redis-cli ping  # Should return: PONG

# Celery workers
celery -A obc_management inspect active

# Celery beat
ps aux | grep "celery beat"

# Gunicorn
ps aux | grep gunicorn

# Nginx
sudo systemctl status nginx
```

### Django Deployment Check
```bash
cd src
python manage.py check --deploy

# Should show: System check identified no issues (0 silenced).
```

---

## 🚨 Troubleshooting

### Issue: "GOOGLE_API_KEY not found"
**Solution:**
```bash
# Check .env file
cat .env | grep GOOGLE_API_KEY

# Should show: GOOGLE_API_KEY=your_key_here

# Restart Django server after updating .env
sudo supervisorctl restart obcms_web
```

### Issue: "Redis connection failed"
**Solution:**
```bash
# Check Redis status
sudo systemctl status redis

# Start Redis if not running
sudo systemctl start redis

# Verify connectivity
redis-cli ping
```

### Issue: "Celery tasks not running"
**Solution:**
```bash
# Check Celery worker status
sudo supervisorctl status obcms_celery_worker

# Restart worker
sudo supervisorctl restart obcms_celery_worker

# Check logs
tail -f /var/log/obcms/celery_worker.log
```

### Issue: "403 CSRF error on forms"
**Solution:**
```bash
# Verify CSRF_TRUSTED_ORIGINS in .env
cat .env | grep CSRF_TRUSTED_ORIGINS

# MUST include https:// scheme
# ✓ CORRECT: CSRF_TRUSTED_ORIGINS=https://yourdomain.com
# ✗ WRONG:   CSRF_TRUSTED_ORIGINS=yourdomain.com

# Update .env and restart
sudo supervisorctl restart obcms_web
```

### Issue: AI operations failing
**Solution:**
```bash
# Run verbose health check
cd src
python manage.py ai_health_check --verbose

# Check AI logs
tail -f logs/ai_assistant.log

# Test Gemini API manually
python << 'EOF'
import google.generativeai as genai
import os
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-exp')
response = model.generate_content("Hello")
print(response.text)
EOF
```

---

## 📈 Performance Tuning

### Gunicorn Workers
```bash
# Calculate optimal workers: (2 × CPU cores) + 1
python3 -c "import multiprocessing; print((2 * multiprocessing.cpu_count()) + 1)"

# Update .env
GUNICORN_WORKERS=9  # For 4-core server

# Restart
sudo supervisorctl restart obcms_web
```

### Cache Optimization
```python
# In settings/production.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'TIMEOUT': 3600,  # 1 hour default
    }
}

# AI-specific cache TTLs
AI_CACHE_TTL = {
    'gemini_response': 86400,    # 24 hours
    'embeddings': 604800,        # 7 days
    'search_results': 3600,      # 1 hour
}
```

### Database Connection Pooling
```python
# In .env
DATABASE_URL=postgres://user:pass@localhost:5432/obcms_prod?pool_size=20

# In settings/production.py
DATABASES['default']['CONN_MAX_AGE'] = 600  # 10 minutes
DATABASES['default']['CONN_HEALTH_CHECKS'] = True
```

---

## 🔄 Update & Maintenance

### Update Deployment
```bash
# 1. Pull latest code
cd /path/to/obcms
git pull origin main

# 2. Activate venv
source venv/bin/activate

# 3. Install new dependencies
pip install -r requirements/base.txt

# 4. Apply migrations
cd src
python manage.py migrate

# 5. Collect static files
python manage.py collectstatic --noinput

# 6. Restart services
sudo supervisorctl restart all
```

### Database Backup
```bash
# Automated backup script
./scripts/db_backup.sh

# Manual backup
pg_dump obcms_prod > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Reindex Vector Store
```bash
cd src

# Rebuild all indices
python manage.py rebuild_vector_index

# Or individual indices
python manage.py index_communities
python manage.py index_policies
```

---

## 📋 Post-Deployment Checklist

- [ ] All services running (Gunicorn, Celery, Redis, Nginx)
- [ ] HTTPS working with valid SSL certificate
- [ ] AI health check passing
- [ ] Admin panel accessible
- [ ] Test user can login
- [ ] Chat AI responding correctly
- [ ] Cost tracking operational
- [ ] Logs writing to files
- [ ] Security headers present (check browser dev tools)
- [ ] Rate limiting active (test with rapid requests)
- [ ] Celery scheduled tasks running
- [ ] Database backups configured

### Final Verification
```bash
# Run full verification suite
./scripts/verify_ai.sh

# Expected: All checks pass
```

---

## 📞 Support Resources

**Documentation:**
- Full deployment guide: `docs/deployment/AI_DEPLOYMENT_GUIDE.md`
- Security assessment: `AI_PRODUCTION_READINESS_ASSESSMENT.md`
- UAT guide: `docs/testing/AI_USER_ACCEPTANCE_TESTING.md`

**Scripts:**
- Automated deployment: `./scripts/deploy_ai.sh`
- Verification: `./scripts/verify_ai.sh`
- Security check: `./scripts/verify_security.sh`

**Management Commands:**
```bash
python manage.py ai_health_check        # System health
python manage.py index_communities      # Index data
python manage.py rebuild_vector_index   # Rebuild indices
```

**Monitoring:**
- AI Operations: `/admin/ai_assistant/aioperation/`
- Logs: `src/logs/ai_assistant.log`
- Cost reports: `CostTracker().get_daily_cost()`

---

**Deployment Complete** ✅
**For issues, refer to troubleshooting section or deployment guide**
