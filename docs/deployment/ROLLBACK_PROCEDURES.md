# OBCMS Deployment Rollback Procedures

**Date:** October 2, 2025
**Status:** Production-Ready Rollback Guide
**Target:** Staging and Production Environments

---

## Purpose

This document provides step-by-step procedures for rolling back OBCMS deployments in case of critical failures, bugs, or issues discovered after deployment to staging or production.

**Critical Principle:** Always have a rollback plan before deploying.

---

## Table of Contents

1. [When to Rollback](#when-to-rollback)
2. [Rollback Decision Matrix](#rollback-decision-matrix)
3. [Pre-Rollback Checklist](#pre-rollback-checklist)
4. [Rollback Procedures](#rollback-procedures)
5. [Post-Rollback Actions](#post-rollback-actions)
6. [Database Rollback](#database-rollback)
7. [Prevention Strategies](#prevention-strategies)

---

## When to Rollback

### Critical Issues (Immediate Rollback Required)

**Roll back immediately if:**
- ✅ Application fails to start or crashes repeatedly
- ✅ Database connection failures preventing all operations
- ✅ Critical security vulnerability introduced
- ✅ Data corruption or loss detected
- ✅ Authentication system broken (users cannot login)
- ✅ Payment/financial system failures (if applicable)
- ✅ Complete loss of core functionality

### High Priority Issues (Rollback Recommended)

**Consider rollback within 1-2 hours if:**
- Major features broken affecting >50% of users
- Performance degradation >50% (pages taking 5x longer)
- Database query errors affecting critical operations
- Admin panel inaccessible
- Email notifications completely broken
- Calendar/scheduling system failures

### Medium Priority Issues (Monitor, Fix Forward)

**Typically fix forward rather than rollback:**
- Minor UI bugs not affecting functionality
- Non-critical features broken affecting <10% of users
- Performance degradation <30%
- Minor visual/styling issues
- Non-blocking error messages

---

## Rollback Decision Matrix

| Issue Severity | User Impact | Data Risk | Decision | Timeline |
|----------------|-------------|-----------|----------|----------|
| **Critical** | >80% users | High | **ROLLBACK** | Immediate (< 15 min) |
| **High** | 50-80% users | Medium | **ROLLBACK** | 1-2 hours |
| **Medium** | 10-50% users | Low | Fix Forward | 4-8 hours |
| **Low** | <10% users | None | Fix Forward | Next release |

---

## Pre-Rollback Checklist

Before initiating rollback, complete these steps:

### 1. Assessment (5-10 minutes)

- [ ] **Verify issue is deployment-related** (not external service failure)
- [ ] **Document the issue:** Error messages, affected endpoints, user reports
- [ ] **Check monitoring:** Error rate, response times, database load
- [ ] **Identify deployment time:** When was the deployment made?
- [ ] **Determine blast radius:** How many users/features affected?

### 2. Communication (2-5 minutes)

- [ ] **Notify stakeholders:** Management, dev team, support team
- [ ] **Post status update:** "Investigating deployment issue, rollback may be required"
- [ ] **Set user expectations:** Maintenance notice if needed

### 3. Backup Current State (5 minutes)

- [ ] **Database snapshot:** Create backup before rollback
- [ ] **Log export:** Download recent error logs
- [ ] **Configuration backup:** Save current environment variables

**Critical:** Never rollback without a current backup!

---

## Rollback Procedures

### Option 1: Docker/Coolify Rollback (Recommended)

**Duration:** 5-10 minutes
**Risk:** Low
**Works for:** Code changes, configuration updates

#### For Coolify Deployments

1. **Access Coolify Dashboard**
   ```bash
   # Navigate to: https://coolify.yourdomain.com
   # Go to: Applications → OBCMS → Deployments
   ```

2. **Identify Previous Stable Version**
   - Look for last successful deployment before current one
   - Note the commit hash or deployment ID
   - Example: `2273691` (commit from Oct 1)

3. **Redeploy Previous Version**
   ```
   Click on previous deployment → Click "Redeploy"
   ```

4. **Monitor Deployment**
   - Watch logs for successful startup
   - Check health endpoint: `curl https://yourdomain.com/health/`
   - Verify application loads

5. **Verify Rollback Success**
   ```bash
   # Test critical endpoints
   curl -I https://yourdomain.com/
   curl https://yourdomain.com/ready/
   curl -I https://yourdomain.com/admin/
   ```

**Total Time:** ~10 minutes

#### For Docker Compose Deployments

1. **SSH into Server**
   ```bash
   ssh user@staging-server
   cd /opt/obcms
   ```

2. **Check Docker Image Tags**
   ```bash
   docker images | grep obcms
   # Look for previous tag, e.g., obcms:2025-10-01
   ```

3. **Update docker-compose.prod.yml**
   ```yaml
   services:
     web:
       image: obcms:2025-10-01  # Change to previous stable tag
   ```

4. **Redeploy**
   ```bash
   docker-compose -f docker-compose.prod.yml pull
   docker-compose -f docker-compose.prod.yml up -d
   ```

5. **Verify**
   ```bash
   docker-compose -f docker-compose.prod.yml logs -f web
   curl http://localhost:8000/health/
   ```

**Total Time:** ~10-15 minutes

---

### Option 2: Git-Based Rollback

**Duration:** 10-15 minutes
**Risk:** Medium
**Works for:** Code changes only

1. **Identify Previous Stable Commit**
   ```bash
   git log --oneline -n 10
   # Find last known good commit, e.g., 2273691
   ```

2. **Create Rollback Branch**
   ```bash
   git checkout -b rollback-emergency-$(date +%Y%m%d-%H%M)
   git reset --hard 2273691  # Last stable commit
   git push origin rollback-emergency-$(date +%Y%m%d-%H%M) --force
   ```

3. **Deploy Rollback Branch**
   - **Coolify:** Change deployment branch to `rollback-emergency-*`
   - **Manual:** Re-run deployment pipeline

4. **Verify Deployment**
   ```bash
   curl https://yourdomain.com/health/
   ```

**Total Time:** ~15 minutes

---

### Option 3: Database Rollback (Use with Extreme Caution)

**Duration:** 30-60 minutes
**Risk:** HIGH - Potential data loss
**Use only when:** Database changes caused critical failures

⚠️ **WARNING:** Database rollbacks can cause permanent data loss. Only use if:
- Current database state is completely broken
- No forward fix is possible
- Acceptable to lose data created after deployment

#### Steps

1. **Stop Application** (prevent further writes)
   ```bash
   docker-compose -f docker-compose.prod.yml stop web celery
   ```

2. **Verify Backup Exists**
   ```bash
   ls -lh /opt/backups/obcms_prod/
   # Find backup from before deployment
   ```

3. **Create Snapshot of Current Database** (just in case)
   ```bash
   docker-compose -f docker-compose.prod.yml exec db \
     pg_dump -U obcms_user obcms_prod | \
     gzip > /opt/backups/obcms_prod/before_rollback_$(date +%Y%m%d_%H%M%S).sql.gz
   ```

4. **Restore Previous Database**
   ```bash
   # Drop current database
   docker-compose -f docker-compose.prod.yml exec db \
     psql -U obcms_user -d postgres -c "DROP DATABASE obcms_prod;"

   # Recreate database
   docker-compose -f docker-compose.prod.yml exec db \
     psql -U obcms_user -d postgres -c "CREATE DATABASE obcms_prod;"

   # Restore backup
   gunzip < /opt/backups/obcms_prod/obcms_prod_20251001_020000.sql.gz | \
     docker-compose -f docker-compose.prod.yml exec -T db \
     psql -U obcms_user obcms_prod
   ```

5. **Restart Application**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

6. **Verify Data**
   ```bash
   docker-compose -f docker-compose.prod.yml exec db \
     psql -U obcms_user obcms_prod -c "SELECT COUNT(*) FROM auth_user;"
   ```

**Total Time:** ~45-60 minutes
**Data Loss:** All data created between backup and rollback will be lost

---

## Post-Rollback Actions

After successful rollback, complete these critical steps:

### Immediate (Within 30 minutes)

1. **Verify System Stability**
   - [ ] Test critical user workflows (login, dashboard, MANA)
   - [ ] Check error rates in logs
   - [ ] Monitor response times
   - [ ] Verify database queries working

2. **Communicate Status**
   - [ ] Update stakeholders: "Rollback complete, system stable"
   - [ ] Post user notification: "Issue resolved, service restored"
   - [ ] Document in incident report

3. **Enable Monitoring Alerts**
   - [ ] Set up enhanced monitoring for next 24 hours
   - [ ] Watch for recurring issues
   - [ ] Monitor user reports

### Short-term (Within 24 hours)

4. **Root Cause Analysis**
   - [ ] Identify what went wrong
   - [ ] Document failure mode
   - [ ] Determine why it wasn't caught in testing
   - [ ] Create ticket for proper fix

5. **Update Deployment Process**
   - [ ] Add tests to prevent recurrence
   - [ ] Update staging checklist
   - [ ] Enhance monitoring/alerts
   - [ ] Review deployment approval process

6. **Plan Forward Fix**
   - [ ] Create fix in separate branch
   - [ ] Add comprehensive tests
   - [ ] Test in staging environment
   - [ ] Schedule deployment with extra caution

---

## Database Migration Rollback

Specific procedures for rolling back database migrations:

### Forward Migration Failed Mid-Migration

**Scenario:** Migration started but failed partway through

**Resolution:**
```bash
# Option 1: Fake the migration (if no schema changes)
python manage.py migrate app_name migration_name --fake

# Option 2: Manual rollback (if schema changes)
# Connect to database
psql -U obcms_user obcms_prod

# Manually revert schema changes (have SQL ready beforehand!)
```

### Migration Completed but Causes Issues

**Scenario:** Migration succeeded but breaks application

**Resolution:**
```bash
# Rollback to previous migration
python manage.py migrate app_name previous_migration_name

# Example:
python manage.py migrate common 0015_migrate_monitoring_task_assignments
```

### Irreversible Migration

**Scenario:** Migration marked as irreversible (data transformations)

**Resolution:**
1. Database restore from backup (see Option 3 above)
2. OR manually write reverse migration
3. OR fix forward with new migration

---

## Prevention Strategies

**Prevent rollbacks by:**

### 1. Comprehensive Testing
- [ ] Full test suite passes (99%+)
- [ ] Integration tests cover critical workflows
- [ ] Performance tests show no regressions
- [ ] Security scans show no new vulnerabilities

### 2. Staging Validation
- [ ] Deploy to staging first (always!)
- [ ] Run staging rehearsal checklist
- [ ] UAT with actual users (5-7 days minimum)
- [ ] Load testing with realistic data volumes

### 3. Gradual Rollout
- [ ] Deploy during low-traffic windows
- [ ] Use feature flags for new features
- [ ] Canary deployments (10% users first)
- [ ] Monitor closely for first 2 hours

### 4. Backup Strategy
- [ ] Automated daily database backups
- [ ] Verify backups can be restored
- [ ] Keep 7 days of backups minimum
- [ ] Document restore procedures

### 5. Monitoring & Alerts
- [ ] Error rate monitoring
- [ ] Response time tracking
- [ ] Database query performance
- [ ] Resource utilization (CPU, memory)

---

## Emergency Contacts

**During Rollback:**

| Role | Contact | Responsibility |
|------|---------|----------------|
| **DevOps Lead** | tech-lead@obcms.gov.ph | Execute rollback |
| **Database Admin** | dba@obcms.gov.ph | Database operations |
| **Tech Manager** | tech-mgr@obcms.gov.ph | Decision authority |
| **OOBC Director** | director@oobc.barmm.gov.ph | Stakeholder communication |

**Escalation:**
1. First 15 min: DevOps Lead decides
2. After 15 min: Tech Manager approval
3. Database rollback: Requires DBA + Tech Manager approval

---

## Rollback Checklist

Print this and keep accessible during deployments:

```
PRE-ROLLBACK:
[ ] Issue verified and documented
[ ] Stakeholders notified
[ ] Current database backup created
[ ] Logs exported
[ ] Rollback decision approved

ROLLBACK EXECUTION:
[ ] Previous stable version identified
[ ] Deployment reverted (Docker/Git)
[ ] Application restarted
[ ] Health endpoints verified
[ ] Critical workflows tested

POST-ROLLBACK:
[ ] System stability confirmed
[ ] Users notified
[ ] Incident report started
[ ] Root cause analysis scheduled
[ ] Forward fix planned

SIGN-OFF:
Executed by: ___________________
Date/Time: ____________________
Verified by: ___________________
```

---

## Rollback Test Procedures

**Test rollback procedures quarterly:**

```bash
# 1. Deploy to test environment
# 2. Simulate failure
# 3. Execute rollback
# 4. Verify restoration
# 5. Document findings
# 6. Update procedures
```

**Next Test:** January 2026

---

## Related Documents

- [Staging Rehearsal Checklist](../testing/staging_rehearsal_checklist.md)
- [Production Deployment Guide](./production-deployment-issues-resolution.md)
- [Backup & Recovery Procedures](./backup_recovery.md) (TODO)
- [Incident Response Plan](../security/incident_response.md) (TODO)

---

**Last Updated:** October 2, 2025
**Next Review:** January 2026
**Owner:** DevOps Team / OOBC Technical Lead
