# BMMS Phase 8 Full Rollout Deployment Guide

**Status:** ✅ Ready for Production Deployment
**Target:** 44 MOAs, 700-1100 concurrent users
**Last Updated:** 2025-10-14

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Infrastructure Components](#infrastructure-components)
4. [Pre-Deployment Checklist](#pre-deployment-checklist)
5. [Deployment Steps](#deployment-steps)
6. [Post-Deployment Verification](#post-deployment-verification)
7. [Monitoring & Alerts](#monitoring--alerts)
8. [Troubleshooting](#troubleshooting)
9. [Rollback Procedures](#rollback-procedures)

---

## Overview

This guide covers the deployment of BMMS Phase 8 scaled infrastructure designed to support full rollout to all 44 Bangsamoro Ministries, Offices, and Agencies (MOAs) with 700-1100 concurrent users.

### **Infrastructure Architecture**

```
                          ┌─────────────┐
                          │   Nginx LB  │ (Load Balancer)
                          └──────┬──────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
           ┌────▼────┐     ┌────▼────┐     ┌────▼────┐
           │  Web 1  │     │  Web 2  │ ... │  Web 4  │ (4 Django App Servers)
           └────┬────┘     └────┬────┘     └────┬────┘
                │                │                │
                └────────────────┼────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
              ┌─────▼─────┐            ┌─────▼─────┐
              │ PgBouncer │            │   Redis   │
              │  (Pool)   │            │  Cluster  │
              └─────┬─────┘            │  (M+2R+3S)│
                    │                  └───────────┘
         ┌──────────┼──────────┐
         │          │          │
    ┌────▼───┐ ┌───▼────┐ ┌───▼────┐
    │ DB     │ │ DB     │ │ DB     │
    │Primary │ │Replica1│ │Replica2│
    └────────┘ └────────┘ └────────┘

    M = Master, R = Replica, S = Sentinel
```

### **Key Features**

- ✅ **4 Django application servers** (horizontal scaling)
- ✅ **Nginx load balancer** (least_conn algorithm)
- ✅ **PostgreSQL primary + 2 read replicas** (high availability)
- ✅ **PgBouncer connection pooling** (500 connections)
- ✅ **Redis cluster** (master + 2 replicas + 3 sentinels for automatic failover)
- ✅ **Prometheus + Grafana monitoring** (real-time metrics)
- ✅ **Multiple Celery workers** (background tasks)

---

## Prerequisites

### **System Requirements**

Calculate exact requirements using capacity planning tool:
```bash
python scripts/capacity_planning.py --moas 44 --users 1000
```

**Minimum Hardware (based on capacity planning):**
- **CPU:** 64+ cores total (4 servers × 8 cores + DB + cache)
- **RAM:** 96+ GB total
- **Storage:** 500 GB (database + media + logs + backups)
- **Network:** 1 Gbps bandwidth

### **Software Requirements**

- Docker 24.0+
- Docker Compose 2.20+
- SSL certificates (Let's Encrypt or commercial)
- Domain name configured (DNS A/AAAA records)

### **Environment Variables**

Create `.env.production` file (see `.env.example`):

```bash
# Critical Production Variables
SECRET_KEY=<generate-using-python-c-import-secrets-secrets.token-urlsafe-50>
ALLOWED_HOSTS=obcms.barmm.gov.ph,www.obcms.barmm.gov.ph
CSRF_TRUSTED_ORIGINS=https://obcms.barmm.gov.ph,https://www.obcms.barmm.gov.ph

# Database
POSTGRES_DB=obcms_prod
POSTGRES_USER=obcms_user
POSTGRES_PASSWORD=<generate-strong-password>

# Email (Production SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.barmm.gov.ph
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=obcms@barmm.gov.ph
EMAIL_HOST_PASSWORD=<smtp-password>
DEFAULT_FROM_EMAIL=OBCMS <noreply@barmm.gov.ph>

# Application
BASE_URL=https://obcms.barmm.gov.ph
GUNICORN_WORKERS=17
GUNICORN_THREADS=2

# Monitoring (Grafana)
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=<generate-strong-password>
```

---

## Infrastructure Components

### **1. Nginx Load Balancer**

**File:** `config/nginx/load_balancer.conf`

- **Algorithm:** `least_conn` (route to least busy server)
- **Backends:** web1, web2, web3, web4 (4 Django servers)
- **Features:**
  - SSL/TLS termination
  - Rate limiting (100 req/min per IP)
  - Static file serving
  - Health checks on `/health/` endpoint

**Configuration:**
- Edit `config/nginx/load_balancer.conf` to adjust server pool
- Place SSL certificates in `ssl/cert.pem` and `ssl/key.pem`

### **2. PgBouncer Connection Pooling**

**Files:**
- `config/pgbouncer/pgbouncer.ini`
- `config/pgbouncer/userlist.txt`

- **Max Client Connections:** 1000
- **Pool Size:** 50 per database
- **Mode:** `transaction` (connection returns to pool after transaction)

**Setup:**
1. Generate password hash:
   ```bash
   echo -n "yourpasswordobcms_user" | md5sum
   ```
2. Update `userlist.txt` with MD5 hash: `"obcms_user" "md5HASHHERE"`

### **3. Redis Cluster**

**Files:**
- `config/redis/master.conf` (8GB memory, AOF+RDB persistence)
- `config/redis/replica.conf` (2 replicas)
- `config/redis/sentinel.conf` (3 sentinels for automatic failover)

- **Memory:** 8GB per instance (master + 2 replicas = 24GB total)
- **Persistence:** AOF (every second) + RDB snapshots
- **Failover:** Automatic (Redis Sentinel with quorum=2)

**Sentinel Monitoring:**
```bash
# Check sentinel status
docker-compose exec redis-sentinel1 redis-cli -p 26379 sentinel masters
docker-compose exec redis-sentinel1 redis-cli -p 26379 sentinel replicas bmms-master
```

### **4. PostgreSQL with Replicas**

- **Primary Database:** `db` (500 max connections, 4GB shared_buffers)
- **Read Replica 1:** `db-replica1` (read-only queries)
- **Read Replica 2:** `db-replica2` (read-only queries)

**Performance Tuning:**
- `max_connections=500`
- `shared_buffers=4GB`
- `work_mem=16MB`
- `maintenance_work_mem=512MB`

### **5. Monitoring Stack**

- **Prometheus:** Metrics collection (http://localhost:9090)
- **Grafana:** Dashboards (http://localhost:3000)
- **Exporters:**
  - `node-exporter` (system metrics: CPU, memory, disk)
  - `postgres-exporter` (database metrics)
  - `redis-exporter` (cache metrics)

**Grafana Login:**
- Username: `${GRAFANA_ADMIN_USER}` (default: admin)
- Password: `${GRAFANA_ADMIN_PASSWORD}` (set in `.env`)

---

## Pre-Deployment Checklist

### **⚠️ CRITICAL: Complete ALL items before deployment**

```
Infrastructure:
[ ] Run capacity planning: python scripts/capacity_planning.py
[ ] Provision servers (4 app + 1 DB + 1 cache minimum)
[ ] Configure DNS A records (obcms.barmm.gov.ph → load balancer IP)
[ ] Obtain SSL certificates (Let's Encrypt or commercial)
[ ] Place certificates in ssl/cert.pem and ssl/key.pem

Configuration:
[ ] Create .env.production with all required variables
[ ] Generate strong SECRET_KEY (50+ characters)
[ ] Configure ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS
[ ] Update PgBouncer userlist.txt with MD5 password hashes
[ ] Configure production email settings (SMTP)
[ ] Set Grafana admin password

Security:
[ ] Review nginx rate limits (config/nginx/load_balancer.conf)
[ ] Enable Redis authentication (uncomment requirepass in redis configs)
[ ] Restrict Grafana access (set strong password)
[ ] Configure firewall rules (allow only 80/443)
[ ] Disable unnecessary services

Backup:
[ ] Set up automated database backups (see backups/ directory)
[ ] Configure off-site backup storage
[ ] Test backup restoration procedure
[ ] Document backup retention policy (30 days)

Testing:
[ ] Test docker-compose build: docker-compose -f docker-compose.prod.yml build
[ ] Validate .env file: python scripts/validate_env.py
[ ] Run security check: python manage.py check --deploy
[ ] Load test with Locust (1000 concurrent users)
```

---

## Deployment Steps

### **Step 1: Clone Repository and Setup**

```bash
# Clone repository
git clone https://github.com/your-org/obcms.git
cd obcms

# Checkout production branch
git checkout main

# Create production environment file
cp .env.example .env.production
vim .env.production  # Edit with production values
```

### **Step 2: Build Docker Images**

```bash
# Build all services
docker-compose -f docker-compose.prod.yml build

# Verify images
docker images | grep obcms
```

### **Step 3: Initialize Database**

```bash
# Start database services only
docker-compose -f docker-compose.prod.yml up -d db pgbouncer

# Wait for database to be ready
docker-compose -f docker-compose.prod.yml logs -f db

# Run migrations
docker-compose -f docker-compose.prod.yml run --rm migrate

# Verify migrations
docker-compose -f docker-compose.prod.yml exec db psql -U obcms_user -d obcms_prod -c "\d"
```

### **Step 4: Deploy Full Stack**

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Monitor startup
docker-compose -f docker-compose.prod.yml logs -f

# Verify all services are healthy
docker-compose -f docker-compose.prod.yml ps
```

**Expected Output:**
```
NAME                    STATUS          PORTS
obcms-db-1              Up (healthy)    5432/tcp
obcms-db-replica1-1     Up (healthy)    5432/tcp
obcms-db-replica2-1     Up (healthy)    5432/tcp
obcms-pgbouncer-1       Up (healthy)    6432/tcp
obcms-redis-master-1    Up (healthy)    6379/tcp
obcms-redis-replica1-1  Up (healthy)    6379/tcp
obcms-redis-replica2-1  Up (healthy)    6379/tcp
obcms-web1-1            Up (healthy)    8000/tcp
obcms-web2-1            Up (healthy)    8000/tcp
obcms-web3-1            Up (healthy)    8000/tcp
obcms-web4-1            Up (healthy)    8000/tcp
obcms-nginx-1           Up              80/tcp, 443/tcp
obcms-prometheus-1      Up              9090/tcp
obcms-grafana-1         Up              3000/tcp
```

### **Step 5: Create Superuser**

```bash
# Create admin user
docker-compose -f docker-compose.prod.yml exec web1 sh -c "cd src && python manage.py createsuperuser"
```

### **Step 6: Load Initial Data (Optional)**

```bash
# Load MOA organizations
docker-compose -f docker-compose.prod.yml exec web1 sh -c "cd src && python manage.py load_pilot_moas"

# Load geographic data
docker-compose -f docker-compose.prod.yml exec web1 sh -c "cd src && python manage.py load_geographic_data"
```

---

## Post-Deployment Verification

### **1. Health Check Verification**

```bash
# Test health endpoints
curl https://obcms.barmm.gov.ph/health/
# Expected: {"status": "healthy", "service": "obcms", "version": "1.0.0"}

curl https://obcms.barmm.gov.ph/ready/
# Expected: {"status": "ready", "checks": {"database": true, "cache": true}, ...}
```

### **2. Load Balancer Verification**

```bash
# Check all backends are reachable
for i in {1..10}; do
  curl -I https://obcms.barmm.gov.ph/ | grep "Server:"
done
# Should see requests distributed across web1, web2, web3, web4
```

### **3. Database Verification**

```bash
# Check PostgreSQL connections
docker-compose -f docker-compose.prod.yml exec db psql -U obcms_user -d obcms_prod -c "SELECT count(*) FROM pg_stat_activity;"

# Check PgBouncer stats
docker-compose -f docker-compose.prod.yml exec pgbouncer psql -h localhost -p 6432 -U obcms_user pgbouncer -c "SHOW POOLS;"
```

### **4. Redis Verification**

```bash
# Check Redis master
docker-compose -f docker-compose.prod.yml exec redis-master redis-cli ping
# Expected: PONG

# Check replication status
docker-compose -f docker-compose.prod.yml exec redis-master redis-cli info replication
# Should show 2 connected slaves

# Check sentinel status
docker-compose -f docker-compose.prod.yml exec redis-sentinel1 redis-cli -p 26379 sentinel masters
```

### **5. Monitoring Verification**

```bash
# Access Prometheus
open http://localhost:9090
# Check Targets: Status → Targets (all should be UP)

# Access Grafana
open http://localhost:3000
# Login with ${GRAFANA_ADMIN_USER} / ${GRAFANA_ADMIN_PASSWORD}
# Verify datasource: Configuration → Data Sources → Prometheus (should be green)
```

### **6. Performance Verification**

```bash
# Run capacity planning check
python scripts/capacity_planning.py --moas 44 --users 1000

# Load test (requires Locust)
locust -f tests/load_test.py --host=https://obcms.barmm.gov.ph --users=1000 --spawn-rate=50
```

---

## Monitoring & Alerts

### **Key Metrics to Monitor**

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Response Time (Dashboard) | <3s | >5s |
| Error Rate | <1% | >5% |
| CPU Usage (per server) | <70% | >85% |
| Memory Usage | <85% | >90% |
| Database Connections | <400 | >450 |
| Redis Memory | <7GB | >7.5GB |
| Disk Usage | <80% | >90% |

### **Grafana Dashboards**

**Pre-configured dashboards:**
1. **BMMS Overview** - High-level system health
2. **Application Performance** - Django response times, error rates
3. **Database Performance** - PostgreSQL queries, connections, replication lag
4. **Cache Performance** - Redis hit rate, memory usage
5. **Infrastructure** - CPU, memory, disk, network

**Access:** http://localhost:3000 → Dashboards → Browse → BMMS Phase 8

### **Alert Setup (Optional)**

Edit `config/prometheus/alert_rules.yml`:
```yaml
groups:
  - name: bmms_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(django_http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
```

---

## Troubleshooting

### **Issue: Web servers won't start**

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs web1

# Common causes:
# - SECRET_KEY not set in .env
# - Database migration not complete
# - Missing environment variables

# Solution:
docker-compose -f docker-compose.prod.yml run --rm migrate
docker-compose -f docker-compose.prod.yml restart web1 web2 web3 web4
```

### **Issue: PgBouncer connection errors**

```bash
# Check PgBouncer logs
docker-compose -f docker-compose.prod.yml logs pgbouncer

# Verify userlist.txt hash
docker-compose -f docker-compose.prod.yml exec pgbouncer cat /etc/pgbouncer/userlist.txt

# Regenerate MD5 hash
echo -n "passwordusername" | md5sum
```

### **Issue: Redis failover not working**

```bash
# Check sentinel logs
docker-compose -f docker-compose.prod.yml logs redis-sentinel1

# Verify quorum
docker-compose -f docker-compose.prod.yml exec redis-sentinel1 \
  redis-cli -p 26379 sentinel ckquorum bmms-master

# Manual failover (if needed)
docker-compose -f docker-compose.prod.yml exec redis-sentinel1 \
  redis-cli -p 26379 sentinel failover bmms-master
```

### **Issue: High database connections**

```bash
# Check active connections
docker-compose -f docker-compose.prod.yml exec db \
  psql -U obcms_user -d obcms_prod -c \
  "SELECT count(*), state FROM pg_stat_activity GROUP BY state;"

# Increase pool size (if needed)
# Edit config/pgbouncer/pgbouncer.ini: default_pool_size = 75
docker-compose -f docker-compose.prod.yml restart pgbouncer
```

---

## Rollback Procedures

### **Emergency Rollback**

```bash
# Stop all services
docker-compose -f docker-compose.prod.yml down

# Restore database from backup
docker-compose -f docker-compose.prod.yml up -d db
docker-compose -f docker-compose.prod.yml exec -T db \
  psql -U obcms_user -d obcms_prod < backups/obcms_prod_YYYYMMDD_HHMMSS.sql

# Checkout previous version
git checkout <previous-commit-hash>

# Rebuild and redeploy
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### **Gradual Rollback (per server)**

```bash
# Stop one server at a time
docker-compose -f docker-compose.prod.yml stop web4
# Monitor load on remaining servers
# If stable, stop next server
docker-compose -f docker-compose.prod.yml stop web3
# Continue as needed
```

---

## Support & Documentation

- **Deployment Issues:** See `docs/deployment/TROUBLESHOOTING.md`
- **Capacity Planning:** `scripts/capacity_planning.py --help`
- **Monitoring Setup:** `docs/monitoring/PROMETHEUS_GRAFANA_SETUP.md`
- **Security Hardening:** `docs/security/PRODUCTION_SECURITY.md`

**Emergency Contact:**
- Technical Lead: [tech-lead@barmm.gov.ph](mailto:tech-lead@barmm.gov.ph)
- Infrastructure Team: [infra@barmm.gov.ph](mailto:infra@barmm.gov.ph)
- On-Call: +63-XXX-XXX-XXXX

---

**Deployment Checklist Sign-Off:**

- [ ] Deployment Lead: _________________ Date: _______
- [ ] Technical Reviewer: _________________ Date: _______
- [ ] Security Reviewer: _________________ Date: _______
- [ ] Project Manager Approval: _________________ Date: _______

**Last Deployment:** YYYY-MM-DD HH:MM UTC
**Next Review:** 30 days post-deployment
