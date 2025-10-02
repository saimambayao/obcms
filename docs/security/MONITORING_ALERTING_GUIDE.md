# OBCMS Monitoring & Alerting Guide

**Version:** 1.0
**Date:** January 2025
**Status:** Implementation Guide

---

## Overview

This guide provides step-by-step instructions for setting up security monitoring and real-time alerting for OBCMS.

---

## Phase 1: Local Monitoring (Development)

### 1.1 Django Admin Monitoring

**Security Logs Dashboard:**

Access via Django admin panel:

```
http://localhost:8000/admin/

# Audit Logs
/admin/auditlog/logentry/

# Failed Login Attempts
/admin/axes/accessattempt/

# Users
/admin/common/user/
```

**Key Metrics to Monitor:**
- Recent audit log entries (last 24 hours)
- Failed login attempts by IP
- Locked out users
- New user registrations

### 1.2 Log File Monitoring

**View Real-Time Logs:**

```bash
cd src

# All logs
tail -f logs/django.log

# Security events only
tail -f logs/django.log | grep "security\|axes\|auditlog"

# Failed logins
tail -f logs/django.log | grep "Failed login"

# Unauthorized access
tail -f logs/django.log | grep "Unauthorized access"

# Data exports
tail -f logs/django.log | grep "Data export"
```

**Log Analysis Commands:**

```bash
# Top 10 IPs with failed logins
grep "Failed login" logs/django.log | \
  grep -oP 'IP: \K[0-9.]+' | \
  sort | uniq -c | sort -rn | head -10

# Count security events by type
grep -E "Failed login|Unauthorized|Permission denied|Data export" logs/django.log | \
  awk -F'|' '{print $2}' | sort | uniq -c

# Recent admin actions
grep "Admin action" logs/django.log | tail -20
```

### 1.3 Django Management Commands

**Axes Commands:**

```bash
cd src

# List all failed attempts
python manage.py axes_list_attempts

# Reset specific user lockout
python manage.py axes_reset_username <username>

# Reset specific IP lockout
python manage.py axes_reset_ip <ip_address>

# Reset all lockouts
python manage.py axes_reset
```

---

## Phase 2: Centralized Logging (Graylog)

### 2.1 Graylog Setup (Docker)

**Deploy Graylog with Docker Compose:**

Create `docker-compose.graylog.yml`:

```yaml
version: '3'
services:
  mongodb:
    image: mongo:6.0
    volumes:
      - mongo_data:/data/db
    networks:
      - graylog

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.17.15
    environment:
      - http.host=0.0.0.0
      - transport.host=localhost
      - network.host=0.0.0.0
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      - discovery.type=single-node
    volumes:
      - es_data:/usr/share/elasticsearch/data
    networks:
      - graylog

  graylog:
    image: graylog/graylog:5.2
    environment:
      # Generate password_secret: pwgen -N 1 -s 96
      - GRAYLOG_PASSWORD_SECRET=<your-secret-96-chars>
      # Generate root password hash: echo -n "yourpassword" | sha256sum | cut -d' ' -f1
      - GRAYLOG_ROOT_PASSWORD_SHA2=<your-sha256-hash>
      - GRAYLOG_HTTP_EXTERNAL_URI=http://localhost:9000/
    entrypoint: /usr/bin/tini -- wait-for-it elasticsearch:9200 --  /docker-entrypoint.sh
    networks:
      - graylog
    restart: always
    depends_on:
      - mongodb
      - elasticsearch
    ports:
      # Graylog web interface
      - 9000:9000
      # Syslog TCP
      - 1514:1514
      # Syslog UDP
      - 1514:1514/udp
      # GELF TCP
      - 12201:12201
      # GELF UDP
      - 12201:12201/udp

volumes:
  mongo_data:
    driver: local
  es_data:
    driver: local

networks:
  graylog:
    driver: bridge
```

**Start Graylog:**

```bash
docker-compose -f docker-compose.graylog.yml up -d

# Wait for services to start (2-3 minutes)
docker-compose -f docker-compose.graylog.yml logs -f graylog
```

**Access Graylog:**

```
URL: http://localhost:9000
Username: admin
Password: <your-password>
```

### 2.2 Configure Django to Send Logs to Graylog

**Install Python GELF Handler:**

```bash
pip install graypy
```

**Update Django Settings:**

Add to `src/obc_management/settings/production.py`:

```python
import graypy

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "graylog": {
            "level": "INFO",
            "class": "graypy.GELFUDPHandler",
            "host": env("GRAYLOG_HOST", default="localhost"),
            "port": 12201,
            "facility": "obcms",
        },
    },
    "root": {
        "handlers": ["console", "graylog"],
        "level": "INFO",
    },
    "loggers": {
        "django.security": {
            "handlers": ["console", "graylog"],
            "level": "WARNING",
            "propagate": False,
        },
        "axes": {
            "handlers": ["console", "graylog"],
            "level": "WARNING",
            "propagate": False,
        },
        "auditlog": {
            "handlers": ["console", "graylog"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
```

**Environment Variables:**

```env
# .env.production
GRAYLOG_HOST=graylog  # Or IP address of Graylog server
```

### 2.3 Create Graylog Inputs

**In Graylog Web Interface:**

1. Go to **System → Inputs**
2. Select **GELF UDP** from dropdown
3. Click **Launch new input**
4. Configure:
   - **Title:** OBCMS Application Logs
   - **Port:** 12201 (default)
   - **Bind address:** 0.0.0.0
5. Click **Save**

**Verify Logs:**

1. Go to **Search**
2. Search query: `facility:obcms`
3. You should see Django logs streaming in

### 2.4 Create Security Dashboards

**Dashboard 1: Failed Logins**

**Widgets:**
1. **Count of Failed Logins (Last 24h)**
   - Query: `message:"Failed login"`
   - Visualization: Single Number

2. **Failed Logins Over Time**
   - Query: `message:"Failed login"`
   - Visualization: Line Chart

3. **Top 10 IPs with Failed Logins**
   - Query: `message:"Failed login"`
   - Field: `source` (extract IP from message)
   - Visualization: Pie Chart

**Dashboard 2: Audit Trail**

**Widgets:**
1. **Recent Administrative Actions**
   - Query: `message:"Admin action"`
   - Visualization: Message List
   - Limit: 50

2. **Data Exports**
   - Query: `message:"Data export"`
   - Visualization: Line Chart

3. **User Changes**
   - Query: `logger_name:auditlog`
   - Visualization: Table

---

## Phase 3: Real-Time Alerting

### 3.1 Email Alerts (Graylog)

**Configure SMTP in Graylog:**

1. Go to **System → Configurations → Email**
2. Configure SMTP settings:
   ```
   SMTP Host: smtp.gmail.com
   SMTP Port: 587
   Use TLS: Yes
   Username: noreply@oobc.gov.ph
   Password: <app-password>
   From Email: noreply@oobc.gov.ph
   ```
3. Click **Save**
4. Send test email to verify

**Create Alert: Excessive Failed Logins:**

1. Go to **Alerts → Event Definitions**
2. Click **Create Event Definition**
3. Configure:
   - **Title:** Excessive Failed Login Attempts
   - **Description:** Alert when >10 failed logins in 5 minutes
   - **Condition Type:** Filter & Aggregation
   - **Search Query:** `message:"Failed login"`
   - **Search within:** 5 minutes
   - **Execute search every:** 1 minute
   - **Aggregation:** Count
   - **Threshold:** >= 10
4. **Notifications:**
   - Create Email Notification
   - Recipients: security@oobc.gov.ph
   - Subject: `[OBCMS ALERT] Excessive Failed Logins Detected`
   - Body template:
     ```
     OBCMS Security Alert

     Event: ${event.message}
     Timestamp: ${event.timestamp}
     Count: ${event.fields.count}

     Action Required: Investigate potential brute force attack

     View details: ${event_definition_url}
     ```
5. Click **Create**

**Create Alert: Data Export Spike:**

Similar configuration with:
- Query: `message:"Data export"`
- Threshold: >= 20 exports in 1 hour

### 3.2 Slack Alerts (Alternative)

**Install Graylog Slack Plugin:**

1. Download plugin from Graylog Marketplace
2. Place in Graylog plugins directory
3. Restart Graylog

**Configure Slack Webhook:**

1. In Slack, create Incoming Webhook
2. Copy Webhook URL
3. In Graylog:
   - Go to **Alerts → Notifications**
   - Create **Slack Notification**
   - Paste Webhook URL
   - Channel: `#security-alerts`

### 3.3 PagerDuty Integration (Production)

**For 24/7 On-Call:**

1. Create PagerDuty service
2. Get Integration Key
3. In Graylog:
   - Install PagerDuty plugin
   - Configure with Integration Key
4. Create alert with PagerDuty notification for:
   - System down (health check failures)
   - Critical security events

---

## Phase 4: Advanced Monitoring

### 4.1 Prometheus + Grafana (Optional)

**For Infrastructure Metrics:**

Deploy with Docker Compose:

```yaml
# docker-compose.monitoring.yml
version: '3'
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - 9090:9090

  grafana:
    image: grafana/grafana:latest
    ports:
      - 3000:3000
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  prometheus_data:
  grafana_data:
```

**Django Prometheus Metrics:**

```bash
pip install django-prometheus
```

Add to settings:

```python
INSTALLED_APPS = [
    'django_prometheus',
    # ... other apps
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... other middleware
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]
```

Metrics endpoint: `http://localhost:8000/metrics`

### 4.2 Sentry (Error Tracking)

**For Application Errors:**

```bash
pip install sentry-sdk
```

Configure in settings:

```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=env("SENTRY_DSN"),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,  # 10% of transactions
    profiles_sample_rate=0.1,
    environment=env("ENVIRONMENT", default="development"),
)
```

---

## Monitoring Checklist

### Daily Checks
- [ ] Review failed login attempts (should be < 50/day)
- [ ] Check for locked out legitimate users
- [ ] Review audit log for unusual activities
- [ ] Verify backup completion

### Weekly Checks
- [ ] Review security dashboard metrics
- [ ] Check for outdated dependencies (`bash scripts/security_scan.sh`)
- [ ] Review alert rules effectiveness
- [ ] Update security documentation

### Monthly Checks
- [ ] Review all security alerts triggered
- [ ] Analyze trends in security events
- [ ] Update incident response procedures
- [ ] Conduct security training

---

## Alert Response Procedures

### Alert: Excessive Failed Logins

**Immediate Actions:**
1. Check `/admin/axes/accessattempt/` for source IPs
2. Determine if legitimate user or attack
3. If attack:
   - Block IP at firewall level
   - Increase rate limiting if needed
4. If legitimate:
   - Contact user
   - Reset lockout: `python manage.py axes_reset_username <username>`

**Investigation:**
1. Review logs for patterns
2. Check if credentials compromised
3. Force password reset if needed

### Alert: Data Export Spike

**Immediate Actions:**
1. Check audit logs for user performing exports
2. Verify if authorized activity
3. If unauthorized:
   - Lock user account immediately
   - Revoke JWT tokens
   - Review exported data

**Investigation:**
1. Determine scope of data accessed
2. Contact legal team if personal data involved
3. Follow data breach procedures if needed

### Alert: System Health Check Failed

**Immediate Actions:**
1. Check application status: `curl http://localhost:8000/health/`
2. Check database connectivity
3. Check Redis connectivity
4. Review error logs

**Escalation:**
- If down > 5 minutes: Page on-call engineer
- If critical data loss risk: Escalate to management

---

## Metrics to Track

### Security Metrics

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Failed Login Rate | < 5% of logins | > 10% |
| Account Lockouts | < 10/day | > 50/day |
| Data Exports | < 100/day | > 500/day |
| API Error Rate | < 1% | > 5% |
| Unauthorized Access Attempts | < 20/day | > 100/day |

### Performance Metrics

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Average Response Time | < 500ms | > 2s |
| Database Query Time (p95) | < 100ms | > 500ms |
| API Availability | > 99.9% | < 99% |
| Celery Queue Depth | < 100 | > 1000 |

---

## Monitoring Dashboard Examples

### Dashboard 1: Security Overview

```
┌─────────────────────────────────────────────────────────────┐
│ OBCMS Security Dashboard - Last 24 Hours                     │
├─────────────────────────────────────────────────────────────┤
│ Failed Logins    │ Locked Accounts │ Data Exports │ Alerts  │
│       47         │        3        │      23      │    1    │
├─────────────────────────────────────────────────────────────┤
│ Failed Logins by Hour (Line Chart)                          │
│ ▁▂▃▅▇█▆▄▃▂▁▁▁▂▃▄▅▆▇█▆▅▄▃                                    │
├─────────────────────────────────────────────────────────────┤
│ Top 5 IPs with Failed Logins                                │
│ 192.168.1.100  (15 attempts)                                │
│ 203.122.45.67  (12 attempts)                                │
│ 10.0.0.50      (8 attempts)                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### Graylog Not Receiving Logs

1. **Check connectivity:**
   ```bash
   telnet localhost 12201
   ```

2. **Verify GELF handler:**
   ```python
   import graypy
   handler = graypy.GELFUDPHandler('localhost', 12201)
   ```

3. **Check Graylog input status:**
   - System → Inputs
   - Verify input is running

### Alerts Not Firing

1. **Test search query manually** in Graylog Search
2. **Check threshold values** (too high?)
3. **Verify SMTP configuration**
4. **Check notification settings**

---

## Next Steps

1. **This Week:**
   - [ ] Set up local log monitoring
   - [ ] Test Django admin dashboards
   - [ ] Configure Axes lockout alerts

2. **Month 1:**
   - [ ] Deploy Graylog
   - [ ] Configure log shipping
   - [ ] Create security dashboards
   - [ ] Set up email alerts

3. **Month 2:**
   - [ ] Implement Prometheus + Grafana
   - [ ] Add Sentry error tracking
   - [ ] Configure PagerDuty for 24/7
   - [ ] Train team on monitoring

---

**Document Version:** 1.0
**Last Updated:** January 2025
**Next Review:** March 2025

---
