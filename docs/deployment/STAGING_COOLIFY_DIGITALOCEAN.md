# Staging Deployment on DigitalOcean via Coolify

**Priority:** HIGH  
**Complexity:** Moderate  
**Dependencies:** docs/deployment/deployment-coolify.md, docs/env/staging-complete.md  
**Prerequisites:** Coolify installed, Docker engine available, repository access, DNS control

---

## 1. Purpose & Scope

This guide explains what a staging environment is and how to operate one for OBCMS using Coolify on DigitalOcean. It covers infrastructure design, provisioning steps, environment configuration, deployment workflow, and ongoing operations tailored to a DigitalOcean droplet (or Droplet + managed services) running Coolify.

---

## 2. Staging Environment Fundamentals

- **Definition:** Staging is a production-like environment used to validate features, migrations, and performance against production datasets and configuration without risking end users. It mirrors production topology, security posture, and integrations while isolating test traffic.
- **Goals:** Catch regressions before release, rehearse deployments, test infrastructure changes, and validate backups/restore processes.
- **Scope in OBCMS:** Django application, PostgreSQL, Redis, Celery workers, scheduled jobs, static/media storage, email/SMS integrations, third-party APIs, and AI assistants. All secrets must be unique to staging.
- **Promotion Workflow:** Changes move dev ➜ staging ➜ production only after staging passes automation (pytest, lint, smoke tests), manual QA, and operations sign-off.

---

## 3. Reference Architecture (DigitalOcean + Coolify)

| Component | Recommendation | Notes |
| --- | --- | --- |
| Compute | DigitalOcean Droplet (4GB RAM, 2 vCPU) hosting Coolify | Use latest Ubuntu LTS, enable monitoring, tag `obcms-staging`. |
| Docker Orchestrator | Coolify (self-hosted) | Installed via Docker compose on the droplet. Handles Git deployments, services, jobs. |
| Database | DigitalOcean Managed PostgreSQL (cluster or single node) | Improves durability, automated backups. Alternatively run Postgres inside Coolify service if budget constrained. |
| Cache/Broker | DigitalOcean Managed Redis (or Coolify Redis service) | Required for Celery and caching. |
| Storage | Spaces (S3-compatible) for media or Coolify volume | For static files rely on collectstatic, media requires persistence. |
| Networking | DigitalOcean VPC + Cloud Firewall | Restrict inbound to SSH (22), HTTP/HTTPS (80/443) through proxy. Deny direct database/redis public access. |
| DNS | DigitalOcean DNS | Create `staging.obcms.yourdomain` A record to droplet IP. |
| SSL | Let's Encrypt issued through Coolify / Traefik | Auto-renew; ensure firewall allows :80/:443. |

---

## 4. Provisioning Checklist (DigitalOcean)

1. **Create Project:** Organize staging resources in a DigitalOcean project named `OBCMS Staging`.
2. **Droplet Setup:**
   - Choose latest Ubuntu LTS image.
   - Select VPC networking and enable backups.
   - Add SSH keys for administrators.
   - Tag droplet (`coolify`, `staging`).
3. **Firewall Rules:**
   - Allow inbound: TCP 22 (admin IPs), 80/443 (Any) for HTTP(S).
   - Deny all outbound? Keep default (allow). Ensure DB/Redis accessible via private network.
4. **Managed Services:**
   - Provision Managed PostgreSQL (single node with automated backups). Record connection string and CA cert.
   - Provision Managed Redis (TLS preferred). Enable eviction policy `noeviction`.
5. **Object Storage (optional):**
   - Create DigitalOcean Spaces bucket `obcms-staging-media`. Generate key pair.
6. **DNS:**
   - Create `staging.obcms.example` A record to droplet public IP.
7. **Secrets Management:**
   - Generate staging-specific secrets (SECRET_KEY, DB password, Redis password, email credentials, AI tokens) and store in password manager.

---

## 5. Install Coolify on the Droplet

> DigitalOcean's console and `doctl` CLI can run these commands. Execute as a privileged user on the droplet.

```bash
# Update system and install dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git docker.io docker-compose-plugin

# Create Coolify directory
sudo mkdir -p /opt/coolify && sudo chown $USER:$USER /opt/coolify
cd /opt/coolify

# Fetch latest Coolify installer
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash

# After install, Coolify UI available at https://<droplet-ip>:8080 (configure firewall accordingly)
```

**Post-install actions:**
- Set up admin account via Coolify onboarding wizard.
- Enforce HTTPS for the Coolify dashboard (custom domain or Cloudflare tunnel) to secure secret management.
- Configure daily backup of the Coolify database (PostgreSQL container) using provided scripts or DigitalOcean snapshots.

---

## 6. Configure Staging Services in Coolify

Follow along with [deployment/deployment-coolify.md](deployment-coolify.md) for base concepts; the key staging-specific decisions are outlined below.

### 6.1 Add Managed Services

1. **PostgreSQL Service:**
   - In Coolify, add external database using DigitalOcean connection string.
   - Set environment variables: `DATABASE_URL`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `PGSSLMODE=require`.
2. **Redis Service:**
   - Add external Redis using `rediss://` (TLS) URL.
   - Inject `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`.
3. **Media Storage:**
   - If using Spaces, configure `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_REGION_NAME`, `AWS_S3_ENDPOINT_URL=https://<region>.digitaloceanspaces.com`.

### 6.2 Create the Staging Application

1. Link repository branch dedicated to staging (e.g., `staging` or protected release branch).
2. Select **Buildpack ➜ Python** and set build env `BP_PYTHON_VERSION=3.12.x`.
3. Define environment variables:
   - `DJANGO_SETTINGS_MODULE=obc_management.settings.production`
   - `SECRET_KEY=<staging secret>`
   - `DEBUG=0`
   - `ALLOWED_HOSTS=staging.obcms.example`
   - `CSRF_TRUSTED_ORIGINS=https://staging.obcms.example`
   - `DATABASE_URL`, `REDIS_URL`, `CELERY_*`, email credentials, AI tokens, `SITE_NAME=OBCMS Staging`.
4. Configure commands:
   - **Pre-deploy:** `python src/manage.py migrate && python src/manage.py collectstatic --noinput`
   - **Start:** `gunicorn obc_management.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120`
5. Attach persistent volume `/workspace/media` if not using Spaces.
6. Deploy once to initialize; monitor logs for migrations and static compilation.

### 6.3 Celery Worker and Beat

- Create a separate Coolify application using same repository.
- Environment variables: clone from web app (ensure same `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`).
- Start commands:
  - Worker: `celery -A obc_management.celery_app worker --loglevel=info`
  - Beat: `celery -A obc_management.celery_app beat --loglevel=info`
- Use Coolify Jobs if you prefer scheduled triggers instead of persistent beat service.

---

## 7. Deploying OBCMS to Staging

1. **Source Control Workflow:** Merge development branch into staging branch after code review and automated test success.
2. **Initiate Deployment:** Coolify auto-deploy on push or manual redeploy via UI. Ensure `pytest --ds=obc_management.settings` ran prior to merging.
3. **Health Verification:**
   - Use Coolify logs to confirm app start.
   - Hit `/health/` endpoint via HTTPS.
   - Run `docker-compose -f docker-compose.prod.yml exec web python src/manage.py check --deploy` using Coolify console (if CLI accessible).
4. **Smoke Tests:** Validate login, CRUD for key modules, Celery background tasks (send test email or queue job).
5. **Data Seeding:** Load anonymized fixtures or sanitized production snapshot using backup/restore process.

---

## 8. Staging Operations Playbook

### 8.1 Configuration Management
- Maintain `.env.staging` locally to sync with Coolify env variables.
- Track secrets in password manager; rotate quarterly or after personnel changes.
- Mirror feature flags and toggles from production, defaulting to safe values.

### 8.2 Data Lifecycle
- Restore sanitized production data weekly to emulate real usage.
- Run `./scripts/backup-database.sh` (configured for staging) before large migrations.
- Store backups in DigitalOcean Spaces or another offsite location with lifecycle policies.

### 8.3 Monitoring & Alerts
- Enable Coolify metrics; forward logs to DigitalOcean Monitoring or third-party tools.
- Configure Django logging to send warnings/errors to email or Slack using staging credentials.
- Set up health-check monitors (UptimeRobot, BetterStack) targeting `https://staging.obcms.example/health/`.

### 8.4 Security Controls
- Enforce MFA on DigitalOcean accounts.
- Limit SSH to operator IPs via Cloud Firewall.
- Use DigitalOcean VPC so managed Postgres/Redis are private.
- Apply HTTPS redirects and HSTS (`SECURE_HSTS_SECONDS`) after confirming TLS.
- Audit access logs monthly.

### 8.5 Release Readiness Criteria
- Automated tests (pytest, flake8, coverage) green.
- Manual QA checklist signed off (UI regression, accessibility, HTMX flows).
- Database migrations applied without errors.
- Background tasks processed queue successfully (no stuck Celery jobs).
- Monitoring dashboards show nominal resource usage.
- Backup & restore drill executed within acceptable recovery window.

---

## 9. Promotion from Staging to Production

1. **Change Control:** Document staged changes, database migrations, and feature toggles.
2. **Rollback Plan:** Prepare `restore-database.sh` and container rollback steps; ensure latest backups available.
3. **Production Secrets:** Maintain separate `.env.production`; never reuse staging credentials.
4. **Deployment Runbook:** Use `scripts/deploy-production.sh` after merging staging branch into production/release branch.
5. **Post-Deployment Validation:** Re-run smoke tests, confirm monitoring, rotate operations logs.

---

## 10. Troubleshooting Reference

| Symptom | Likely Cause | Mitigation |
| --- | --- | --- |
| Deployment fails at migrations | Staging DB schema drift | Run `python src/manage.py showmigrations`, align branch, reapply migrations after backup. |
| App healthy but static assets missing | `collectstatic` failed or Spaces misconfigured | Check Coolify pre-deploy logs, verify AWS keys and bucket permissions. |
| Celery worker exits | Redis credentials mismatch or firewall block | Confirm `CELERY_BROKER_URL`, ensure Redis reachable via VPC. |
| TLS errors accessing staging | Missing certificate or DNS mismatch | Re-issue Let's Encrypt via Coolify, confirm DNS to droplet, update `ALLOWED_HOSTS`. |
| High latency | Droplet undersized or missing database indexes | Review Coolify metrics, consider larger Droplet or enabling DO managed DB performance insights. |

---

## 11. Related Resources

- docs/deployment/deployment-coolify.md — Base Coolify deployment workflow.
- docs/deployment/DOCKER_DEPLOYMENT_GUIDE.md — Production Docker compose reference.
- docs/env/staging-complete.md — Checklist for staging configuration.
- docs/env/production.md — Production environment parity checklist.
- docs/deployment/DATABASE_BACKUP_GUIDE.md — Backup strategy and automation scripts.

