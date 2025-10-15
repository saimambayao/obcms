# OBCMS/BMMS Production Deployment Guide

**System**: Office for Other Bangsamoro Communities Management System (OBCMS)
**Transition**: Bangsamoro Ministerial Management System (BMMS)
**Target**: 44 BARMM Ministries, Offices, and Agencies (MOAs)

## 📋 Overview

This guide provides step-by-step instructions for deploying the OBCMS/BMMS system to production, including environment setup, database migration to PostgreSQL, and production configuration.

## 🚀 Prerequisites

### System Requirements
- **Python**: 3.10+ (3.13+ recommended)
- **Memory**: 4GB+ RAM minimum
- **Storage**: 20GB+ free disk space
- **Network**: Stable internet connection
- **OS**: Linux (Ubuntu 20.04+), macOS, Windows 10+

### Software Requirements
- **PostgreSQL**: 13+ (recommended for production)
- **Redis**: 6.0+ (for caching and background tasks)
- **Nginx**: 1.18+ (for reverse proxy)
- **Docker**: 20.10+ (optional, for containerization)
- **SSL Certificate**: For HTTPS security

## 🔧 Phase 1: Environment Setup

### 1.1 Clone Repository
```bash
git clone <repository-url>
cd obcms/src
```

### 1.2 Create Virtual Environment
```bash
python3 -m venv ../venv
source ../venv/bin/activate
```

### 1.3 Run Production Setup Script
```bash
chmod +x setup_production_environment.sh
./setup_production_environment.sh
```

This script will:
- ✅ Verify Python version
- ✅ Install production dependencies
- ✅ Create necessary directories
- ✅ Set up environment configuration
- ✅ Generate secure SECRET_KEY
- ✅ Create admin user
- ✅ Configure BMMS multi-tenant settings
- ✅ Test AI services integration

### 1.4 Review Environment Configuration
```bash
# Edit .env file with your production values
nano ../.env
```

Critical settings to update:
- `SECRET_KEY`: Generate new secure key
- `ALLOWED_HOSTS`: Add your production domains
- `CSRF_TRUSTED_ORIGINS`: Add HTTPS origins
- `DATABASE_URL`: Configure PostgreSQL (see Phase 2)
- `GOOGLE_API_KEY`: Add for AI services (optional)
- `BMMS_MODE`: Set to 'bmms' for multi-tenant

## 🗄️ Phase 2: Database Setup

### 2.1 Install PostgreSQL

#### Option A: PostgreSQL Local Installation
```bash
# macOS
brew install postgresql postgresql-contrib

# Ubuntu
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL
brew services start postgresql  # macOS
sudo systemctl start postgresql  # Ubuntu
```

#### Option B: Docker PostgreSQL (Recommended)
```bash
docker run --name postgres-obcms \
  -e POSTGRES_PASSWORD=secure_password \
  -e POSTGRES_DB=obcms_prod \
  -e POSTGRES_USER=obcms_user \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  -d postgres:15-alpine
```

### 2.2 Run PostgreSQL Setup Script
```bash
chmod +x setup_postgresql.sh
./setup_postgresql.sh
```

This script will:
- ✅ Check PostgreSQL installation
- ✅ Start PostgreSQL service
- ✅ Create database and user
- ✅ Configure permissions
- ✅ Update .env with PostgreSQL settings

### 2.3 Manual PostgreSQL Setup (Alternative)
If setup script doesn't work, follow these manual steps:

```bash
# Start PostgreSQL service
sudo systemctl start postgresql

# Switch to postgres user
sudo -u postgres psql

# Create database
CREATE DATABASE obcms_prod;
CREATE USER obcms_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE obcms_prod TO obcms_user;
\q

# Test connection
psql -h localhost -U obcms_user -d obcms_prod
```

### 2.4 Update Database Configuration
Edit `.env` file:
```bash
DATABASE_URL=postgres://obcms_user:secure_password@localhost:5432/obcms_prod
POSTGRES_DB=obcms_prod
POSTGRES_USER=obcms_user
POSTGRES_PASSWORD=secure_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

## 🔄 Phase 3: Database Migration

### 3.1 Export SQLite Data
```bash
python migrate_to_postgresql.py --export-only
```

This will:
- ✅ Export all data from SQLite
- ✅ Create `postgres_export/` directory
- ✅ Save data as JSON files
- ✅ Maintain data integrity

### 3.2 Import to PostgreSQL
```bash
python migrate_to_postgresql.py --import-only
```

This will:
- ✅ Create PostgreSQL database structure
- ✅ Import all data from JSON files
- ✅ Maintain relationships and constraints
- ✅ Optimize PostgreSQL indexes

### 3.3 Full Migration (All-in-One)
```bash
python migrate_to_postgresql.py
```

This will perform the complete migration including export, import, and validation.

### 3.4 Validate Migration
```bash
python migrate_to_postgresql.py --validate-only
```

## 🚀 Phase 4: Production Deployment

### 4.1 Install Production Dependencies
```bash
pip install -r requirements/production.txt
```

### 4.2 Run Django Production Checks
```bash
python manage.py check --deploy
```

### 4.3 Collect Static Files
```bash
python manage.py collectstatic --no-input
```

### 4.4 Start Production Server
```bash
./start_production.sh
```

### 4.5 Docker Deployment (Optional)
```bash
# Build and start with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down
```

## 🔧 Phase 5: Configuration

### 5.1 Nginx Reverse Proxy
Create `/etc/nginx/sites-available/obcms.conf`:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";

    # Location Blocks
    location /static/ {
        alias /path/to/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /path/to/mediafiles/;
        expires 1y;
        add_header Cache-Control "public, max-age=31536000";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

### 5.2 SSL Certificate Setup
Let's Encrypt (Recommended):
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo crontab -e "0 12 * * * /usr/bin/certbot renew --quiet"
```

## 🔍 Phase 6: Verification

### 6.1 System Health Check
```bash
# Django system checks
python manage.py check --deploy

# Database connectivity
python manage.py dbshell -c "SELECT COUNT(*) FROM auth_user;"

# Cache connectivity
python manage.py shell -c "from django.core.cache import cache; cache.set('health', 'ok', 60); print(cache.get('health'))"
```

### 6.2 BMMS Configuration Check
```bash
python manage.py shell -c "
from django.conf import settings
print('BMMS Mode:', settings.BMMS_MODE)
print('Multi-tenant:', settings.RBAC_SETTINGS['ENABLE_MULTI_TENANT'])
print('Organization Switching:', settings.RBAC_SETTINGS['ALLOW_ORGANIZATION_SWITCHING'])
"
```

### 6.3 AI Services Check
```bash
python manage.py shell -c "
from django.conf import settings
print('AI Enabled:', getattr(settings, 'AI_ENABLED', False))
print('Google API Key:', 'Configured' if settings.GOOGLE_API_KEY else 'Not configured')
"
```

### 6.4 Security Verification
```bash
# Test authentication
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123456"}'

# Check security headers
curl -I https://your-domain.com/ | grep -E "(Strict-Transport-Security|Content-Security-Policy)"
```

## 📊 Phase 7: Monitoring

### 7.1 Application Monitoring
```bash
# View application logs
tail -f src/logs/django.log

# View security audit logs
tail -f src/logs/rbac_security.log
```

### 7.2 Database Monitoring
```bash
# Check database connections
psql -h localhost -U obcms_user -d obcms_prod -c "SELECT count(*) FROM pg_stat_activity;"

# Monitor slow queries
psql -h localhost -U obcms_user -d obcms_prod -c "SELECT * FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;"
```

### 7.3 Performance Monitoring
```bash
# Check Gunicorn worker status
systemctl status gunicorn

# Monitor resource usage
htop
```

## 🚨 Phase 8: Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check PostgreSQL status
pg_isready -h localhost -p 5432

# Check database permissions
psql -lqt | grep obcms_prod

# Test connection manually
psql -h localhost -U obcms_user -d obcms_prod
```

#### Migration Issues
```bash
# Check migration status
python manage.py showmigrations

# Force migration re-run
python manage.py migrate --fake

# Check for data conflicts
python migrate_to_postgresql.py --validate-only
```

#### Performance Issues
```bash
# Check memory usage
free -h

# Check disk space
df -h

# Check process list
ps aux | grep gunicorn
```

#### SSL Certificate Issues
```bash
# Check certificate expiration
openssl x509 -in /path/to/cert.pem -text -noout | grep "Not After"

# Test SSL configuration
openssl s_client -connect your-domain.com:443 -servername your-domain.com
```

## 📈 Phase 9: Scaling

### 9.1 Horizontal Scaling
- **Load Balancer**: Nginx or HAProxy
- **Web Servers**: Multiple Gunicorn instances
- **Database**: Read replicas for heavy queries
- **Cache**: Redis cluster for distributed caching

### 9.2 Database Optimization
- **Connection Pooling**: Configure connection limits
- **Indexing**: Optimize slow queries
- **Vacuum**: Regular database maintenance
- **Monitoring**: Query performance analysis

### 9.3 Caching Strategy
- **Redis Cluster**: Distributed caching
- **CDN**: Static file distribution
- **Browser Caching**: Optimize static assets
- **Application Caching**: Database query results

## 🎯 Phase 10: BMMS Deployment

### 10.1 Multi-Tenant Configuration
```python
# Enable BMMS mode in .env
BMMS_MODE=bmms
ENABLE_MULTI_TENANT=1
ALLOW_ORGANIZATION_SWITCHING=1
```

### 10.2 Organization Setup
```bash
python manage.py shell -c "
from organizations.models import Organization
from common.models import User

# Create pilot organizations
pilot_orgs = [
    ('MOH', 'Ministry of Health', 'ministry'),
    ('MOLE', 'Ministry of Labor and Employment', 'ministry'),
    ('MAFAR', 'Ministry of Agriculture, Fisheries and Agrarian Reform', 'ministry'),
]

for code, name, org_type in pilot_orgs:
    org, created = Organization.objects.get_or_create(
        code=code,
        defaults={
            'name': name,
            'org_type': org_type,
            'is_pilot': True,
        }
    )
    print(f"Organization {code}: {'created' if created else 'existing'}")
"
```

### 10.3 User Organization Assignment
```bash
python manage.py shell -c "
from organizations.models import Organization, OrganizationMembership
from common.models import User

# Get organizations
orgs = Organization.objects.filter(is_pilot=True)
admin_user = User.objects.get(username='admin')

# Assign admin to pilot organizations
for org in orgs:
    membership, created = OrganizationMembership.objects.get_or_create(
        user=admin_user,
        organization=org,
        defaults={
            'role': 'admin',
            'is_primary': org == orgs.first(),
        }
    )
    print(f"Admin membership: {org.code} - {'created' if created else 'existing'}")
"
```

## ✅ Success Criteria

The deployment is successful when:

- [x] **Production Environment**: All dependencies installed and configured
- [x] **Database Migration**: Data successfully migrated to PostgreSQL
- [x] **Web Server**: Gunicorn running with production configuration
- [x] **Static Files**: Collected and properly configured
- [x] **Security**: HTTPS, CSRF protection, and security headers active
- [x] **BMMS Features**: Multi-tenant isolation working
- [x] **AI Services**: Configuration ready (API key setup)
- [x] **Health Checks**: All system health checks passing
- [x] **Performance**: Response times under target thresholds

## 📞 Support

### Documentation
- **API Documentation**: `/api/docs/`
- **User Guide**: `/docs/user-guide/`
- **Admin Guide**: `/docs/admin-guide/`
- **Technical Documentation**: `/docs/technical/`

### Contact
- **System Administrator**: admin@obcms.gov.ph
- **Technical Support**: support@obcms.gov.ph
- **Security Team**: security@obcms.gov.ph

---

**Deployment Guide Version**: 1.0
**Last Updated**: October 15, 2025
**System Version**: OBCMS/BMMS v1.0
**Status**: Production Ready

This guide ensures a smooth, secure, and scalable production deployment of the OBCMS/BMMS system for serving all 44 BARMM Ministries, Offices, and Agencies.