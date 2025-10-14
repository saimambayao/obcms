# BMMS Pilot Staging Server Setup

This guide provisions the BMMS pilot staging environment used in Phase 7 onboarding. It
mirrors production while isolating pilot data for MOH, MOLE, and MAFAR.

## Prerequisites
- Ubuntu 22.04 LTS host (4 vCPU, 8 GB RAM, 80 GB SSD)
- Docker and Docker Compose installed
- Access to the BMMS container registry and GitHub repository
- DNS control for `staging.bmms.gov.ph`

## 1. Clone Repository and Load Environment
```bash
sudo mkdir -p /opt/bmms && sudo chown $USER /opt/bmms
cd /opt/bmms
git clone https://github.com/oobcms/obcms.git .
cp .env.staging.example .env
./scripts/validate_env.py .env --profile staging
```

Update `.env` with production-like secrets and staging-specific URLs.

## 2. Build and Launch Services
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Services started:
- `web`: Django + Gunicorn (`DEBUG=0`)
- `worker`: Celery workers for background jobs
- `beat`: Celery beat scheduler
- `redis`: cache and task broker (db 1 & 2 for pilot)
- `postgres`: staging database

## 3. Apply Database Migrations
```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
```

## 4. Provision Pilot Data
```bash
docker compose exec web python manage.py generate_pilot_data --users 5 --programs 3 --year 2025
```

## 5. Smoke Tests
- Load `https://staging.bmms.gov.ph/login/` and verify TLS
- Authenticate using a generated pilot account
- Confirm planning, budgeting, and coordination dashboards render under 200 ms

## 6. Monitoring and Logging
- Application logs stream to stdout (captured by Docker)
- Configure Sentry/New Relic via `.env` if available
- Rotate logs weekly using systemd or platform tooling

## 7. Backup Automation
Schedule `scripts/backup_pilot_db.sh` daily via cron and upload archives to secure
storage. Verify restore path quarterly with `scripts/restore_pilot_db.sh`.

## 8. Access Control
- Restrict SSH to BMMS DevOps IP range
- Enforce MFA on registry and hosting provider
- Rotate staging secrets every 90 days

The pilot staging server is now ready for user training, UAT, and analytics collection.
