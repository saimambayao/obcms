# OBCMS Deployment Quickstart

**Production-Ready Docker Deployment** ✅
**PostgreSQL Migration Complete** ✅

---

## One-Command Deployment

```bash
# 1. Clone and configure
git clone https://github.com/your-org/obcms.git && cd obcms
cp .env.production.template .env.production
nano .env.production  # Edit configuration

# 2. Deploy
./scripts/deploy-production.sh

# 3. Create admin user
docker-compose -f docker-compose.prod.yml exec web python src/manage.py createsuperuser
```

**Done!** Access your deployment at `http://your-server-ip:8000`

---

## Essential Configuration (`.env.production`)

**MUST CHANGE:**
```env
SECRET_KEY=<generate-with-django-command>
DEBUG=0
ALLOWED_HOSTS=yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
POSTGRES_PASSWORD=<strong-password>
```

**Generate SECRET_KEY:**
```bash
docker run --rm python:3.12-slim python -c \
    "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Common Commands

### Deployment
```bash
# Deploy/Update
./scripts/deploy-production.sh

# View logs
docker-compose -f docker-compose.prod.yml logs -f web

# Restart
docker-compose -f docker-compose.prod.yml restart web

# Stop
docker-compose -f docker-compose.prod.yml down
```

### Database
```bash
# Backup
./scripts/backup-database.sh

# Restore
./scripts/restore-database.sh backups/postgres/backup.sql.gz

# Shell
docker-compose -f docker-compose.prod.yml exec db psql -U obcms_user -d obcms_prod
```

### Management
```bash
# Django shell
docker-compose -f docker-compose.prod.yml exec web python src/manage.py shell

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python src/manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec web python src/manage.py createsuperuser
```

---

## Architecture

```
Client → Nginx (port 80/443) → Gunicorn (port 8000) → PostgreSQL
                                                      ↘ Redis
                                                          ↓
                                                      Celery Worker
                                                          ↑
                                                      Celery Beat
```

---

## Services

| Service | Purpose | Health Check |
|---------|---------|--------------|
| **db** | PostgreSQL 17 | `pg_isready` |
| **redis** | Cache & Celery | `redis-cli ping` |
| **web** | Django (Gunicorn) | `curl localhost:8000/health/` |
| **celery** | Background tasks | Running |
| **celery-beat** | Scheduled tasks | Running |
| **nginx** | Reverse proxy (optional) | `wget localhost/health/` |

---

## Troubleshooting

**Service won't start:**
```bash
docker-compose -f docker-compose.prod.yml logs <service-name>
docker-compose -f docker-compose.prod.yml ps
```

**Database connection error:**
```bash
# Check database health
docker-compose -f docker-compose.prod.yml exec db pg_isready -U obcms_user

# Check environment
docker-compose -f docker-compose.prod.yml exec web env | grep DATABASE
```

**502 Bad Gateway:**
```bash
# Check web service
docker-compose -f docker-compose.prod.yml logs web | tail -50
docker-compose -f docker-compose.prod.yml restart web
```

---

## Deployment Checklist

**Before Production:**
- [ ] `SECRET_KEY` changed (50+ characters)
- [ ] `DEBUG=0` set
- [ ] `ALLOWED_HOSTS` configured
- [ ] `CSRF_TRUSTED_ORIGINS` with https://
- [ ] Postgres password changed
- [ ] Email SMTP configured
- [ ] SSL certificates installed
- [ ] Automated backups configured
- [ ] Firewall configured (ports 80, 443, 22)
- [ ] Monitoring set up

---

## Resources

- **[Full Deployment Guide](docs/deployment/DOCKER_DEPLOYMENT_GUIDE.md)**
- **[PostgreSQL Migration Report](docs/deployment/POSTGRESQL_MIGRATION_REPORT_20251009.md)**
- **[Coolify Deployment](docs/deployment/deployment-coolify.md)**

---

**Questions?** See [docs/deployment/](docs/deployment/) or create an issue.
