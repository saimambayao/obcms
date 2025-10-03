# OBCMS Incident Response Playbook

**Document Version:** 1.0
**Date:** October 3, 2025
**Status:** ACTIVE
**Classification:** Internal Use - Security Team Only

---

## Executive Summary

This playbook provides standardized procedures for responding to security incidents affecting the Other Bangsamoro Communities Management System (OBCMS). All security team members must be familiar with these procedures.

**⚠️ CRITICAL**: For P0 (Critical) incidents, immediately contact the Security Lead and OOBC Director.

---

## 1. Incident Classification

### Severity Levels

| Priority | Severity | Response Time | Definition | Examples |
|----------|----------|---------------|------------|----------|
| **P0** | 🚨 CRITICAL | **15 minutes** | Active data breach, system compromise | Database dump, ransomware, root access, mass data exfiltration |
| **P1** | ❌ HIGH | **1 hour** | Critical vulnerability, imminent threat | Unpatched critical CVE, active DDoS, zero-day exploit |
| **P2** | ⚠️ MEDIUM | **4 hours** | Security policy violation, suspicious activity | Brute force attack, unauthorized access attempt, privilege escalation |
| **P3** | ℹ️ LOW | **24 hours** | Low severity security concern | Outdated dependency, misconfiguration, failed audit |

---

## 2. Emergency Contact Information

### Internal Team

| Role | Name | Email | Phone | Availability |
|------|------|-------|-------|--------------|
| **Security Lead** | [TBD] | security@oobc.gov.ph | [TBD] | 24/7 On-Call |
| **IT Manager** | [TBD] | it@oobc.gov.ph | [TBD] | Business Hours |
| **OOBC Director** | [TBD] | director@oobc.gov.ph | [TBD] | Business Hours |
| **Database Administrator** | [TBD] | dba@oobc.gov.ph | [TBD] | On-Call |
| **Legal Counsel** | [TBD] | legal@oobc.gov.ph | [TBD] | Business Hours |

### External Resources

| Service | Contact | Purpose |
|---------|---------|---------|
| **National Privacy Commission (NPC)** | complaints@privacy.gov.ph | Data breach notification (72 hours) |
| **DICT Cybersecurity** | cybersecurity@dict.gov.ph | Government system incidents |
| **PNP Anti-Cybercrime Group** | acg@pnp.gov.ph | Criminal investigations |
| **Cloudflare Support** | support@cloudflare.com | WAF/DDoS mitigation |
| **Hosting Provider** | [TBD] | Infrastructure support |

---

## 3. Incident Response Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                  INCIDENT RESPONSE PHASES                    │
├─────────────────────────────────────────────────────────────┤
│  1. DETECTION (Immediate)                                    │
│     ├─ Automated alerts (Slack, email)                       │
│     ├─ Security monitoring (Graylog)                         │
│     ├─ User reports                                          │
│     └─ External notification                                 │
├─────────────────────────────────────────────────────────────┤
│  2. TRIAGE (Within 15 minutes for P0/P1)                     │
│     ├─ Classify severity (P0/P1/P2/P3)                       │
│     ├─ Assemble response team                                │
│     ├─ Create incident ticket (Jira/GitHub)                  │
│     └─ Establish communication channel                       │
├─────────────────────────────────────────────────────────────┤
│  3. CONTAINMENT (Within 1 hour for P0/P1)                    │
│     ├─ Isolate compromised systems                           │
│     ├─ Block malicious IPs (Cloudflare WAF)                  │
│     ├─ Revoke compromised credentials                        │
│     ├─ Enable aggressive rate limiting                       │
│     └─ Preserve evidence (logs, snapshots)                   │
├─────────────────────────────────────────────────────────────┤
│  4. ERADICATION                                              │
│     ├─ Identify root cause                                   │
│     ├─ Remove malware/backdoors                              │
│     ├─ Patch vulnerabilities                                 │
│     ├─ Reset compromised accounts                            │
│     └─ Strengthen defenses                                   │
├─────────────────────────────────────────────────────────────┤
│  5. RECOVERY                                                 │
│     ├─ Restore from clean backups (if needed)                │
│     ├─ Rebuild compromised systems                           │
│     ├─ Verify system integrity                               │
│     ├─ Gradual service restoration                           │
│     └─ Monitor for re-infection                              │
├─────────────────────────────────────────────────────────────┤
│  6. POST-INCIDENT REVIEW (Within 7 days)                     │
│     ├─ Document timeline                                     │
│     ├─ Identify improvements                                 │
│     ├─ Update runbooks                                       │
│     ├─ Security training (if needed)                         │
│     └─ Communicate lessons learned                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Incident Scenarios & Response Procedures

### Scenario 1: Data Breach (P0 - CRITICAL)

**Definition:** Unauthorized access to sensitive data (PII, OBC community data, assessment data)

**Immediate Actions (0-15 minutes):**
1. **Confirm breach scope:**
   ```bash
   # Check audit logs
   cd /var/log/obcms
   grep -i "unauthorized" django.log | tail -100

   # Check database access logs
   psql -U obcms_admin -c "SELECT * FROM auditlog_logentry WHERE timestamp > NOW() - INTERVAL '1 hour';"
   ```

2. **Revoke compromised credentials:**
   ```bash
   # Django management command
   cd src
   ./manage.py shell
   >>> from common.models import User
   >>> user = User.objects.get(username='compromised_user')
   >>> user.is_active = False
   >>> user.save()
   ```

3. **Block attacker IP (Cloudflare):**
   - Login to Cloudflare Dashboard
   - Security → Tools → IP Access Rules
   - Add IP to blocklist

4. **Preserve evidence:**
   ```bash
   # Copy logs to secure location
   sudo cp -r /var/log/obcms /backup/incident_$(date +%Y%m%d_%H%M%S)/
   sudo cp /var/lib/postgresql/data/pg_log/* /backup/incident_$(date +%Y%m%d_%H%M%S)/
   ```

**Containment (15-60 minutes):**
5. **Enable emergency mode (read-only):**
   ```python
   # src/obc_management/settings/production.py
   EMERGENCY_READ_ONLY_MODE = True
   ```

6. **Rotate all API keys and secrets:**
   ```bash
   # Generate new SECRET_KEY
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

   # Update .env file
   nano /opt/obcms/.env
   # Restart services
   docker-compose restart
   ```

7. **Notify affected users (if PII exposed):**
   - See "Data Breach Notification" section below

**Eradication:**
8. Identify and patch vulnerability
9. Remove backdoors/malware
10. Force password reset for all users

**Recovery:**
11. Restore from last known good backup
12. Verify data integrity
13. Gradual service restoration

**Reporting:**
14. **CRITICAL: Notify NPC within 72 hours** (Data Privacy Act requirement)
15. Document timeline and lessons learned

---

### Scenario 2: Brute Force Attack (P2 - MEDIUM)

**Definition:** Multiple failed login attempts from same IP (10+ in 5 minutes)

**Automated Response:**
- Django Axes automatically locks account after 5 failed attempts
- Slack/email alert sent automatically

**Manual Response (if persistent):**
1. **Check attack details:**
   ```bash
   # View failed login attempts
   cd src
   ./manage.py shell
   >>> from axes.models import AccessAttempt
   >>> attempts = AccessAttempt.objects.filter(
   ...     attempt_time__gte=timezone.now() - timedelta(hours=1)
   ... ).values('ip_address', 'username').annotate(count=Count('id')).order_by('-count')
   >>> print(attempts)
   ```

2. **Block attacker IP:**
   - Add to Cloudflare blocklist
   - Or use Fail2Ban to auto-block

3. **Review targeted accounts:**
   - Check if specific high-value accounts targeted
   - Notify account owners
   - Consider forcing MFA enrollment

4. **Monitor for 24 hours:**
   - Watch for IP changes
   - Check for distributed attack (multiple IPs)

---

### Scenario 3: DDoS Attack (P1 - HIGH)

**Definition:** Service degradation due to excessive traffic

**Immediate Actions:**
1. **Verify attack:**
   ```bash
   # Check server load
   top
   htop

   # Check network traffic
   netstat -an | wc -l
   tcpdump -i eth0 -c 100
   ```

2. **Enable Cloudflare "I'm Under Attack" mode:**
   - Cloudflare Dashboard → Security → "Under Attack Mode"
   - Shows interstitial to visitors (blocks bots)

3. **Enable aggressive rate limiting:**
   ```python
   # Temporary setting
   REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {
       "anon": "10/hour",      # Drastically reduced
       "user": "100/hour",
       "burst": "20/minute",
   }
   ```

4. **Scale infrastructure (if needed):**
   ```bash
   # Increase container replicas
   docker-compose up --scale web=3 -d
   ```

5. **Contact hosting provider:**
   - Request DDoS mitigation at network level

---

### Scenario 4: Ransomware (P0 - CRITICAL)

**Definition:** Files encrypted, ransom demanded

**⚠️ DO NOT PAY RANSOM - Government policy**

**Immediate Actions:**
1. **Isolate infected system:**
   ```bash
   # Shut down network interfaces
   sudo ifconfig eth0 down

   # Or shutdown system completely
   sudo shutdown -h now
   ```

2. **Identify ransomware strain:**
   - Take screenshot of ransom note
   - Save a copy of encrypted file
   - Search ID Ransomware database

3. **Assess backup status:**
   ```bash
   # Check last backup
   ls -lht /backup/ | head -10

   # Verify backup integrity
   pg_restore --list /backup/latest.dump | wc -l
   ```

4. **Notify authorities:**
   - PNP Anti-Cybercrime Group
   - NBI Cybercrime Division

5. **Restore from backup:**
   - Use backup from before infection
   - Verify decryption tools available (nomoreransom.org)

6. **Rebuild infrastructure:**
   - Clean reinstall of OS
   - Restore data from verified clean backup
   - Change all passwords and keys

---

### Scenario 5: SQL Injection Attack (P1 - HIGH)

**Definition:** Malicious SQL queries executed via input fields

**Detection:**
```bash
# Check for SQL injection patterns in logs
grep -i "union.*select" /var/log/obcms/django.log
grep -i "drop.*table" /var/log/obcms/django.log
grep -i "exec.*sp_" /var/log/obcms/django.log
```

**Response:**
1. **Identify injection point:**
   - Review recent code changes
   - Check raw SQL queries in views
   - Review user input fields

2. **Block malicious requests:**
   ```python
   # Add WAF rule (Cloudflare)
   # Block requests with SQL patterns
   ```

3. **Verify database integrity:**
   ```sql
   -- Check for unexpected tables
   SELECT tablename FROM pg_tables WHERE schemaname = 'public';

   -- Check for suspicious stored procedures
   SELECT proname FROM pg_proc WHERE pronamespace = 'public'::regnamespace;

   -- Audit recent database changes
   SELECT * FROM auditlog_logentry WHERE timestamp > NOW() - INTERVAL '1 hour';
   ```

4. **Patch vulnerability:**
   - Fix raw SQL queries to use ORM
   - Add input validation
   - Deploy hotfix immediately

5. **Restore from backup (if data modified):**
   ```bash
   pg_restore -U obcms_admin -d obcms_prod /backup/latest.dump
   ```

---

## 5. Data Breach Notification Procedures

### Philippine Data Privacy Act (RA 10173) Requirements

**Timeline:**
- **Within 72 hours** of breach discovery → Notify National Privacy Commission (NPC)
- **Without undue delay** → Notify affected individuals (if high risk)

**NPC Notification Process:**
1. Email: complaints@privacy.gov.ph
2. Include:
   - Nature of breach
   - Data categories affected
   - Approximate number of data subjects
   - Likely consequences
   - Measures taken/proposed

**Template:**
```
Subject: Data Breach Notification - OOBC OBCMS System

Date: [Breach Discovery Date]
From: [Data Protection Officer]
To: complaints@privacy.gov.ph

Dear National Privacy Commission,

This is to notify you of a personal data breach affecting the Other Bangsamoro
Communities Management System (OBCMS) operated by the Office for Other
Bangsamoro Communities (OOBC).

1. Nature of Breach:
   [Description: unauthorized access, ransomware, data exfiltration, etc.]

2. Date/Time of Breach:
   Discovered: [Date/Time]
   Estimated Occurrence: [Date/Time]

3. Data Categories Affected:
   - Personal data: [Yes/No - specify: names, addresses, etc.]
   - Sensitive personal data: [Yes/No - specify: religion, ethnicity, etc.]
   - Government-issued IDs: [Yes/No - specify types]

4. Number of Data Subjects Affected:
   Approximately [X] individuals

5. Likely Consequences:
   [Identity theft, discrimination, privacy violation, etc.]

6. Measures Taken:
   - [Immediate containment actions]
   - [Security enhancements]
   - [User notification plan]

7. Contact Person:
   Name: [DPO Name]
   Email: [Email]
   Phone: [Phone]

Sincerely,
[Data Protection Officer]
Office for Other Bangsamoro Communities
```

---

## 6. Post-Incident Review Template

**Incident ID:** INC-[YYYY]-[NNNN]
**Date:** [Date]
**Severity:** [P0/P1/P2/P3]
**Duration:** [Total incident duration]

### Timeline

| Time | Event | Action Taken |
|------|-------|--------------|
| HH:MM | [Detection event] | [Response] |
| HH:MM | [Escalation] | [Team assembled] |
| HH:MM | [Containment] | [Systems isolated] |
| HH:MM | [Resolution] | [Service restored] |

### Root Cause Analysis

**What happened:**
[Technical description]

**Why it happened:**
[Root cause - technical, process, or human]

**Why wasn't it prevented:**
[Gap in defenses]

### Lessons Learned

**What went well:**
- [Positive aspects of response]

**What could be improved:**
- [Areas for improvement]

**Action Items:**
| Action | Owner | Due Date | Priority |
|--------|-------|----------|----------|
| [Action 1] | [Name] | [Date] | [P0/P1/P2/P3] |

---

## 7. Useful Commands & Scripts

### Quick Response Commands

```bash
# View recent failed logins
cd /opt/obcms/src
./manage.py shell
>>> from axes.models import AccessAttempt
>>> AccessAttempt.objects.filter(attempt_time__gte=timezone.now() - timedelta(hours=1)).values('ip_address', 'username').annotate(count=Count('id')).order_by('-count')

# Block IP in Django
>>> from common.models import BlockedIP
>>> BlockedIP.objects.create(ip_address='1.2.3.4', reason='Brute force attack', blocked_until=timezone.now() + timedelta(days=7))

# Force logout all users
>>> from django.contrib.sessions.models import Session
>>> Session.objects.all().delete()

# Disable user account
>>> from common.models import User
>>> user = User.objects.get(username='suspicious_user')
>>> user.is_active = False
>>> user.save()

# View audit logs
>>> from auditlog.models import LogEntry
>>> LogEntry.objects.filter(timestamp__gte=timezone.now() - timedelta(hours=1)).values('actor', 'action', 'object_repr')[:20]
```

### Database Forensics

```sql
-- Check for suspicious database users
SELECT usename, usecreatedb, usesuper, valuntil
FROM pg_user;

-- Check active connections
SELECT pid, usename, application_name, client_addr, backend_start, state
FROM pg_stat_activity
WHERE state = 'active';

-- Check for large data exports
SELECT query, calls, total_time, rows
FROM pg_stat_statements
ORDER BY rows DESC
LIMIT 20;
```

---

## 8. Training & Drills

### Required Training

**All Security Team Members:**
- Complete this playbook training (annually)
- Tabletop exercise (bi-annually)
- Incident simulation drill (annually)

### Incident Response Drill Schedule

| Quarter | Scenario | Participants |
|---------|----------|--------------|
| Q1 | Data Breach (P0) | All security team |
| Q2 | DDoS Attack (P1) | IT team + hosting provider |
| Q3 | Ransomware (P0) | All security team + legal |
| Q4 | Brute Force (P2) | Security team only |

---

## 9. Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | October 3, 2025 | Security Team | Initial playbook |

**Next Review Date:** April 3, 2026 (6 months)

**Distribution:** Security Team, IT Team, OOBC Leadership

**Classification:** Internal Use - Security Team Only

---

**END OF PLAYBOOK**

*For questions or clarifications, contact: security@oobc.gov.ph*
