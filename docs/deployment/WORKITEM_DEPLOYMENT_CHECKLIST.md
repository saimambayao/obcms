# MOA PPA WorkItem Integration - Production Deployment Checklist

**System**: OBCMS (Office for Other Bangsamoro Communities Management System)
**Feature**: MOA PPA WorkItem Integration (8 Phases Complete)
**Target Environment**: Production
**Deployment Date**: TBD
**Prepared By**: BICTO Development Team
**Last Updated**: October 6, 2025

---

## 📋 Pre-Deployment Checklist

### 1. Code & Database Preparation

**Migrations** (Priority: CRITICAL)
- [ ] Backup production database
  ```bash
  # PostgreSQL
  pg_dump obcms_prod > backups/obcms_backup_$(date +%Y%m%d_%H%M%S).sql

  # SQLite (if applicable)
  cp db.sqlite3 backups/db_backup_$(date +%Y%m%d_%H%M%S).sqlite3
  ```

- [ ] Review all migration files (2 new migrations)
  - [ ] `monitoring/0018_add_workitem_integration.py` - Adds 5 WorkItem fields to MonitoringEntry
  - [ ] `common/0023_workitem_explicit_fks.py` - Adds explicit FK fields to WorkItem

- [ ] Test migrations on staging database
  ```bash
  cd src
  python manage.py migrate monitoring 0018 --database=staging
  python manage.py migrate common 0023 --database=staging
  ```

- [ ] Verify no data loss after staging migration
  ```bash
  # Compare record counts before/after
  python manage.py shell
  >>> from monitoring.models import MonitoringEntry
  >>> MonitoringEntry.objects.count()  # Should match pre-migration count
  ```

**Code Quality** (Priority: HIGH)
- [ ] All Python files pass syntax validation
  ```bash
  python3 -m py_compile src/**/*.py
  ```

- [ ] Run full test suite (target: >95% pass rate)
  ```bash
  cd src
  pytest -v --cov=monitoring --cov=common --cov-report=html
  ```

- [ ] Review test coverage report
  ```bash
  open htmlcov/index.html  # macOS
  xdg-open htmlcov/index.html  # Linux
  ```

- [ ] Run Django system checks
  ```bash
  python manage.py check --deploy
  ```

**Environment Configuration** (Priority: CRITICAL)
- [ ] Update `.env` file with production settings
  ```env
  # Database
  DATABASE_URL=postgres://user:pass@host:5432/obcms_prod

  # Redis (for Celery)
  REDIS_URL=redis://redis:6379/0
  CELERY_BROKER_URL=redis://redis:6379/0

  # Email (for notifications)
  EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
  EMAIL_HOST=smtp.gmail.com
  EMAIL_PORT=587
  EMAIL_USE_TLS=True
  EMAIL_HOST_USER=noreply@oobc.gov.ph
  EMAIL_HOST_PASSWORD=***********
  DEFAULT_FROM_EMAIL=noreply@oobc.gov.ph

  # MFBM Analyst Emails (for approval reminders)
  MFBM_ANALYST_EMAILS=analyst1@mfbm.gov.ph,analyst2@mfbm.gov.ph

  # WorkItem Cleanup (default: dry-run)
  WORKITEM_CLEANUP_DRY_RUN=True  # Set to False to enable deletion

  # Security
  SECRET_KEY=***********  # Generate new for production
  DEBUG=False
  ALLOWED_HOSTS=obcms.gov.ph,www.obcms.gov.ph
  CSRF_TRUSTED_ORIGINS=https://obcms.gov.ph,https://www.obcms.gov.ph
  ```

- [ ] Verify all required environment variables are set
  ```bash
  python manage.py shell
  >>> from django.conf import settings
  >>> assert settings.SECRET_KEY != 'your-secret-key-here'
  >>> assert settings.DEBUG == False
  >>> assert 'obcms.gov.ph' in settings.ALLOWED_HOSTS
  ```

**Dependencies** (Priority: HIGH)
- [ ] Verify all Python packages installed
  ```bash
  pip install -r requirements/base.txt
  pip freeze > requirements_deployed.txt  # For audit trail
  ```

- [ ] Verify `openpyxl>=3.1.0` installed (required for reports)
- [ ] Verify `django-auditlog>=3.0.0` installed (required for compliance)
- [ ] Verify `celery>=5.0.0` installed (required for automation)
- [ ] Verify `redis>=4.0.0` installed (required for Celery broker)

---

## 2. Service Configuration

**Celery Workers** (Priority: CRITICAL)
- [ ] Configure Celery worker service
  ```bash
  # systemd service file: /etc/systemd/system/celery-worker.service
  [Unit]
  Description=OBCMS Celery Worker
  After=network.target

  [Service]
  Type=forking
  User=obcms
  Group=obcms
  WorkingDirectory=/opt/obcms/src
  Environment="PATH=/opt/obcms/venv/bin"
  ExecStart=/opt/obcms/venv/bin/celery -A obc_management worker \
            --loglevel=info \
            --logfile=/var/log/celery/worker.log \
            --pidfile=/var/run/celery/worker.pid
  ExecStop=/bin/kill -s TERM $MAINPID

  [Install]
  WantedBy=multi-user.target
  ```

- [ ] Configure Celery beat scheduler service
  ```bash
  # systemd service file: /etc/systemd/system/celery-beat.service
  [Unit]
  Description=OBCMS Celery Beat Scheduler
  After=network.target

  [Service]
  Type=simple
  User=obcms
  Group=obcms
  WorkingDirectory=/opt/obcms/src
  Environment="PATH=/opt/obcms/venv/bin"
  ExecStart=/opt/obcms/venv/bin/celery -A obc_management beat \
            --loglevel=info \
            --logfile=/var/log/celery/beat.log \
            --pidfile=/var/run/celery/beat.pid \
            --schedule=/var/run/celery/celerybeat-schedule

  [Install]
  WantedBy=multi-user.target
  ```

- [ ] Create Celery log directories
  ```bash
  sudo mkdir -p /var/log/celery /var/run/celery
  sudo chown obcms:obcms /var/log/celery /var/run/celery
  ```

- [ ] Enable and start Celery services
  ```bash
  sudo systemctl daemon-reload
  sudo systemctl enable celery-worker celery-beat
  sudo systemctl start celery-worker celery-beat
  sudo systemctl status celery-worker celery-beat
  ```

**Redis Server** (Priority: CRITICAL)
- [ ] Verify Redis is running
  ```bash
  redis-cli ping  # Should return "PONG"
  ```

- [ ] Configure Redis persistence (for scheduled tasks)
  ```bash
  # /etc/redis/redis.conf
  appendonly yes
  appendfsync everysec
  ```

- [ ] Test Redis connection from Django
  ```bash
  python manage.py shell
  >>> import redis
  >>> r = redis.from_url('redis://localhost:6379/0')
  >>> r.ping()  # Should return True
  ```

**Web Server** (Priority: CRITICAL)
- [ ] Collect static files
  ```bash
  python manage.py collectstatic --noinput
  ```

- [ ] Configure Gunicorn workers (if using Gunicorn)
  ```bash
  # Recommended: (2 x CPU cores) + 1 workers
  gunicorn obc_management.wsgi:application \
    --workers 5 \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile /var/log/gunicorn/access.log \
    --error-logfile /var/log/gunicorn/error.log
  ```

- [ ] Restart web server
  ```bash
  sudo systemctl restart gunicorn  # or uwsgi, etc.
  ```

---

## 3. Database Migration Execution

**Pre-Migration Validation** (Priority: CRITICAL)
- [ ] Confirm production database backup exists
  ```bash
  ls -lh backups/obcms_backup_*.sql
  ```

- [ ] Test rollback procedure on staging
  ```bash
  # Staging test: Apply migrations, then rollback
  python manage.py migrate monitoring 0018 --database=staging
  python manage.py migrate monitoring 0017 --database=staging  # Rollback
  ```

- [ ] Verify database connection in production
  ```bash
  python manage.py dbshell
  \dt  # List tables (PostgreSQL)
  .tables  # List tables (SQLite)
  \q  # Quit
  ```

**Migration Execution** (Priority: CRITICAL)
- [ ] Put application in maintenance mode
  ```bash
  touch /opt/obcms/maintenance.flag
  # Or set MAINTENANCE_MODE=True in .env
  ```

- [ ] Apply MonitoringEntry migration
  ```bash
  cd src
  python manage.py migrate monitoring 0018
  ```

  **Expected Output:**
  ```
  Running migrations:
    Applying monitoring.0018_add_workitem_integration... OK
  ```

- [ ] Apply WorkItem migration
  ```bash
  python manage.py migrate common 0023
  ```

  **Expected Output:**
  ```
  Running migrations:
    Applying common.0023_workitem_explicit_fks... OK
  ```

- [ ] Verify migrations applied successfully
  ```bash
  python manage.py showmigrations monitoring common
  ```

  **Expected Output:**
  ```
  monitoring
   [X] 0017_add_model_validation_constraints
   [X] 0018_add_workitem_integration  # ← Should be checked

  common
   [X] 0022_eventproxy_projectworkflowproxy_stafftaskproxy
   [X] 0023_workitem_explicit_fks  # ← Should be checked
  ```

- [ ] Verify new fields exist in database
  ```bash
  python manage.py dbshell
  \d+ monitoring_monitoringentry;  # Check for execution_project, enable_workitem_tracking, etc.
  \d+ common_workitem;  # Check for related_assessment, related_policy, etc.
  ```

- [ ] Remove maintenance mode
  ```bash
  rm /opt/obcms/maintenance.flag
  # Or set MAINTENANCE_MODE=False in .env
  ```

**Post-Migration Validation** (Priority: CRITICAL)
- [ ] Verify record counts unchanged
  ```bash
  python manage.py shell
  >>> from monitoring.models import MonitoringEntry
  >>> from common.models import WorkItem
  >>> MonitoringEntry.objects.count()  # Should match pre-migration count
  >>> WorkItem.objects.count()  # Should match pre-migration count
  ```

- [ ] Test creating a PPA with WorkItem tracking
  ```bash
  python manage.py shell
  >>> from monitoring.models import MonitoringEntry
  >>> ppa = MonitoringEntry.objects.first()
  >>> ppa.enable_workitem_tracking = True
  >>> ppa.save()
  >>> print("✓ WorkItem fields working")
  ```

- [ ] Verify audit logging active
  ```bash
  python manage.py shell
  >>> from auditlog.models import LogEntry
  >>> LogEntry.objects.filter(content_type__model='monitoringentry').exists()  # Should be True
  ```

---

## 4. Feature Activation & Testing

**Signal Handlers** (Priority: HIGH)
- [ ] Verify signal handlers registered
  ```bash
  python manage.py shell
  >>> import monitoring.signals  # Should import without errors
  >>> print("✓ Signal handlers loaded")
  ```

- [ ] Test approval workflow automation
  ```bash
  # Create test PPA
  >>> from monitoring.models import MonitoringEntry
  >>> ppa = MonitoringEntry.objects.create(
  ...     title="Test PPA - Delete After",
  ...     category="moa_ppa",
  ...     enable_workitem_tracking=True,
  ...     budget_distribution_policy='activity'
  ... )

  # Trigger auto-creation
  >>> ppa.approval_status = 'technical_review'
  >>> ppa.save()

  # Verify execution project created
  >>> assert ppa.execution_project is not None
  >>> print(f"✓ Auto-created: {ppa.execution_project.title}")

  # Clean up
  >>> ppa.delete()
  ```

**API Endpoints** (Priority: HIGH)
- [ ] Test API authentication
  ```bash
  curl -X POST https://obcms.gov.ph/api/token/ \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"***"}'
  ```

- [ ] Test enable WorkItem tracking endpoint
  ```bash
  curl -X POST https://obcms.gov.ph/api/monitoring/entries/{id}/enable-workitem-tracking/ \
    -H "Authorization: Bearer {token}" \
    -H "Content-Type: application/json" \
    -d '{"structure_template":"activity"}'
  ```

- [ ] Test budget allocation tree endpoint
  ```bash
  curl https://obcms.gov.ph/api/monitoring/entries/{id}/budget-allocation-tree/ \
    -H "Authorization: Bearer {token}"
  ```

- [ ] Verify API response time <200ms
  ```bash
  curl -w "@curl-format.txt" -o /dev/null -s \
    https://obcms.gov.ph/api/monitoring/entries/{id}/budget-allocation-tree/

  # curl-format.txt content:
  # time_total: %{time_total}s
  ```

**Celery Tasks** (Priority: HIGH)
- [ ] Test auto_sync_ppa_progress task
  ```bash
  python manage.py shell
  >>> from monitoring.tasks import auto_sync_ppa_progress
  >>> result = auto_sync_ppa_progress()
  >>> print(result)  # Should show sync summary
  ```

- [ ] Test detect_budget_variances task
  ```bash
  >>> from monitoring.tasks import detect_budget_variances
  >>> result = detect_budget_variances()
  >>> print(result)  # Should show variance detection summary
  ```

- [ ] Test send_approval_deadline_reminders task
  ```bash
  >>> from monitoring.tasks import send_approval_deadline_reminders
  >>> result = send_approval_deadline_reminders()
  >>> print(result)  # Should show reminder summary
  ```

- [ ] Verify Celery Beat schedule
  ```bash
  celery -A obc_management inspect scheduled
  ```

**UI Components** (Priority: HIGH)
- [ ] Test Work Items tab renders
  - Navigate to PPA detail page
  - Click "Work Items" tab
  - Verify tree view displays
  - Verify budget summary cards display

- [ ] Test budget distribution modal
  - Click "Distribute Budget" button
  - Select distribution method
  - Verify preview updates
  - Submit distribution

- [ ] Test progress updates reflect in UI
  - Update WorkItem progress
  - Verify PPA progress updates automatically
  - Check calendar displays updated progress

**Reports** (Priority: HIGH)
- [ ] Test MFBM Budget Execution Report
  - Navigate to `/monitoring/reports/`
  - Select fiscal year
  - Click "Download MFBM Report"
  - Verify Excel file downloads
  - Open and verify format

- [ ] Test BPDA Development Report
  - Select fiscal year and sector
  - Click "Download BPDA Report"
  - Verify Excel file downloads
  - Verify BDP alignment scores calculated

- [ ] Test COA Variance Report
  - Select fiscal year
  - Click "Download COA Report"
  - Verify 3-sheet Excel file
  - Verify audit trail populated

---

## 5. Performance Validation

**Database Performance** (Priority: HIGH)
- [ ] Verify budget allocation tree query <100ms
  ```bash
  python manage.py shell
  >>> from django.db import connection
  >>> from django.test.utils import override_settings
  >>> with override_settings(DEBUG=True):
  ...     ppa = MonitoringEntry.objects.first()
  ...     tree = ppa.get_budget_allocation_tree()
  ...     print(f"Queries: {len(connection.queries)}")  # Should be <10
  ```

- [ ] Run performance tests
  ```bash
  pytest tests/test_performance_workitem.py -v
  ```

- [ ] Verify no N+1 query issues
  ```bash
  # Enable query logging in Django toolbar
  # Check for repeated queries in budget tree generation
  ```

**API Performance** (Priority: HIGH)
- [ ] Benchmark all 4 API endpoints
  ```bash
  # Should all be <200ms
  ab -n 100 -c 10 https://obcms.gov.ph/api/monitoring/entries/{id}/budget-allocation-tree/
  ```

- [ ] Verify Celery task performance
  ```bash
  # auto_sync_ppa_progress should complete in <5 minutes for 1000 PPAs
  # detect_budget_variances should complete in <2 minutes for 1000 PPAs
  ```

**Memory & Resource Usage** (Priority: MEDIUM)
- [ ] Monitor server memory during task execution
  ```bash
  htop  # Monitor during Celery task execution
  ```

- [ ] Verify no memory leaks in long-running tasks
  ```bash
  # Run tasks multiple times, check memory doesn't grow
  for i in {1..10}; do
    python manage.py shell -c "from monitoring.tasks import auto_sync_ppa_progress; auto_sync_ppa_progress()"
    sleep 60
  done
  ```

---

## 6. Security Hardening

**Django Security** (Priority: CRITICAL)
- [ ] Verify `SECRET_KEY` is production-safe (50+ characters, random)
  ```bash
  python manage.py shell
  >>> from django.conf import settings
  >>> assert len(settings.SECRET_KEY) >= 50
  >>> assert settings.SECRET_KEY != 'your-secret-key-here'
  ```

- [ ] Verify `DEBUG=False` in production
  ```bash
  >>> assert settings.DEBUG == False
  ```

- [ ] Verify `ALLOWED_HOSTS` configured
  ```bash
  >>> assert 'obcms.gov.ph' in settings.ALLOWED_HOSTS
  >>> assert '*' not in settings.ALLOWED_HOSTS  # Wildcard not allowed
  ```

- [ ] Verify HTTPS enforced
  ```bash
  >>> assert settings.SECURE_SSL_REDIRECT == True
  >>> assert settings.SESSION_COOKIE_SECURE == True
  >>> assert settings.CSRF_COOKIE_SECURE == True
  ```

**API Security** (Priority: HIGH)
- [ ] Verify JWT token expiration configured
  ```bash
  >>> from datetime import timedelta
  >>> assert settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] == timedelta(hours=1)
  ```

- [ ] Test API authentication required
  ```bash
  curl https://obcms.gov.ph/api/monitoring/entries/ \
    # Should return 401 Unauthorized without token
  ```

- [ ] Verify rate limiting active (if configured)
  ```bash
  # Make 100 requests rapidly, should be throttled
  ```

**Audit Trail** (Priority: HIGH)
- [ ] Verify django-auditlog captures all changes
  ```bash
  python manage.py shell
  >>> from monitoring.models import MonitoringEntry
  >>> from auditlog.models import LogEntry
  >>> ppa = MonitoringEntry.objects.first()
  >>> ppa.budget_allocation = 1000000
  >>> ppa.save()
  >>> assert LogEntry.objects.filter(object_id=ppa.id).exists()
  ```

- [ ] Verify sensitive fields excluded from audit (if any)
- [ ] Configure audit log retention (recommend: 2 years minimum)

---

## 7. Monitoring & Logging

**Application Logging** (Priority: HIGH)
- [ ] Verify log files created
  ```bash
  ls -lh /var/log/obcms/
  ls -lh /var/log/celery/
  ```

- [ ] Configure log rotation
  ```bash
  # /etc/logrotate.d/obcms
  /var/log/obcms/*.log {
      daily
      rotate 30
      compress
      delaycompress
      notifempty
      create 0640 obcms obcms
      sharedscripts
  }
  ```

- [ ] Test log aggregation (if using ELK/Graylog)
  ```bash
  # Verify logs appear in centralized system
  ```

**Celery Monitoring** (Priority: HIGH)
- [ ] Set up Flower (Celery monitoring tool)
  ```bash
  celery -A obc_management flower --port=5555
  # Access at: http://localhost:5555
  ```

- [ ] Configure Celery event snapshots
  ```bash
  celery -A obc_management events
  ```

- [ ] Set up alerts for failed tasks
  ```bash
  # Configure Sentry/Datadog for Celery error tracking
  ```

**Performance Monitoring** (Priority: MEDIUM)
- [ ] Set up Prometheus metrics (optional)
  ```python
  # django-prometheus integration
  pip install django-prometheus
  ```

- [ ] Configure Grafana dashboards (optional)
  - WorkItem creation rate
  - Budget distribution performance
  - API response times
  - Celery task execution times

**Health Checks** (Priority: HIGH)
- [ ] Configure `/health/` endpoint monitoring
  ```bash
  curl https://obcms.gov.ph/health/
  # Should return 200 OK with system status
  ```

- [ ] Set up uptime monitoring (e.g., UptimeRobot, Pingdom)
- [ ] Configure alerting for downtime (email, SMS)

---

## 8. User Training & Documentation

**Training Sessions** (Priority: HIGH)
- [ ] Conduct MOA staff training (use `docs/training/WORKITEM_TRAINING_PRESENTATION.md`)
  - Target: All MOA program managers
  - Duration: 2 hours
  - Hands-on exercises included

- [ ] Conduct MFBM analyst training
  - Target: Budget analysts
  - Focus: Budget reports, variance analysis
  - Duration: 1.5 hours

- [ ] Conduct BPDA planner training
  - Target: Planning officers
  - Focus: Development reports, BDP alignment
  - Duration: 1.5 hours

**Documentation Deployment** (Priority: HIGH)
- [ ] Upload all user guides to internal knowledge base
  - `MOA_WORKITEM_TRACKING_GUIDE.md`
  - `MFBM_BUDGET_REPORTS_GUIDE.md`
  - `BPDA_DEVELOPMENT_REPORTS_GUIDE.md`

- [ ] Create printable quick reference cards (PDF)
- [ ] Set up documentation search (Algolia/MeiliSearch)
- [ ] Add help links in UI (contextual help)

**Support Preparation** (Priority: HIGH)
- [ ] Create support ticket categories for WorkItem issues
- [ ] Prepare FAQ document (common issues + solutions)
- [ ] Set up dedicated support email (workitem-support@oobc.gov.ph)
- [ ] Train helpdesk staff on common troubleshooting

---

## 9. Rollback Preparation

**Rollback Procedures** (Priority: CRITICAL)
- [ ] Document rollback steps
  ```bash
  # 1. Restore database from backup
  psql obcms_prod < backups/obcms_backup_YYYYMMDD_HHMMSS.sql

  # 2. Revert migrations
  python manage.py migrate monitoring 0017
  python manage.py migrate common 0022

  # 3. Revert code deployment
  git checkout <previous-commit-hash>

  # 4. Restart services
  sudo systemctl restart gunicorn celery-worker celery-beat
  ```

- [ ] Test rollback procedure on staging
- [ ] Verify data integrity after rollback test
- [ ] Document rollback decision criteria
  - Critical bug affecting >50% of users
  - Data corruption detected
  - Performance degradation >50%
  - Security vulnerability discovered

**Rollback Testing** (Priority: HIGH)
- [ ] Simulate rollback on staging environment
  ```bash
  # Apply migrations, then rollback
  python manage.py migrate monitoring 0018 --database=staging
  python manage.py migrate monitoring 0017 --database=staging

  # Verify no data loss
  ```

- [ ] Verify application works after rollback
- [ ] Document time required for rollback (estimate: 30-60 minutes)

---

## 10. Post-Deployment Validation

**Immediate Verification** (Priority: CRITICAL)
- [ ] Verify application accessible
  ```bash
  curl -I https://obcms.gov.ph/
  # Should return 200 OK
  ```

- [ ] Test user login (admin and regular user)
- [ ] Verify all modules accessible
  - Communities
  - MANA (Mapping & Needs Assessment)
  - Coordination
  - Monitoring (PPAs)
  - Project Central

- [ ] Test creating new PPA with WorkItem tracking
  - Enable WorkItem tracking
  - Generate execution project
  - Add work items
  - Distribute budget
  - Verify sync

**24-Hour Monitoring** (Priority: CRITICAL)
- [ ] Monitor error logs continuously
  ```bash
  tail -f /var/log/obcms/error.log
  tail -f /var/log/celery/*.log
  ```

- [ ] Monitor Celery task execution
  ```bash
  # Check auto_sync_ppa_progress runs at 2:00 AM
  # Check detect_budget_variances runs every 6 hours
  # Check send_approval_deadline_reminders runs at 8:00 AM
  ```

- [ ] Monitor server resources (CPU, memory, disk)
  ```bash
  htop
  df -h
  ```

- [ ] Check for any user-reported issues
- [ ] Verify all scheduled tasks execute successfully

**7-Day Follow-Up** (Priority: HIGH)
- [ ] Review Celery task success rate (target: >99%)
  ```bash
  # Check Flower dashboard for failed tasks
  ```

- [ ] Review API response times (target: <200ms)
- [ ] Analyze user adoption metrics
  - Number of PPAs with WorkItem tracking enabled
  - Number of work items created
  - Budget distribution operations performed

- [ ] Gather user feedback
  - Conduct user survey (MOA, MFBM, BPDA)
  - Address top 3 issues/requests

- [ ] Review and address any bugs/issues reported
- [ ] Plan optimization based on usage patterns

---

## 11. Documentation & Knowledge Transfer

**Technical Documentation** (Priority: HIGH)
- [ ] Update system architecture diagrams
- [ ] Document all configuration changes
- [ ] Update deployment runbook
- [ ] Create troubleshooting playbook

**Knowledge Transfer** (Priority: MEDIUM)
- [ ] Conduct handover session with BICTO team
- [ ] Document lessons learned
- [ ] Update internal wiki
- [ ] Archive deployment notes

---

## 📊 Deployment Success Criteria

**Must-Have (Deployment Blocker if Failed)**
- ✅ All migrations apply successfully without errors
- ✅ Zero data loss (record counts match pre-deployment)
- ✅ All 4 API endpoints functional (<200ms response time)
- ✅ Celery workers and beat scheduler running
- ✅ Auto-sync and variance detection tasks executing
- ✅ All 3 government reports generate successfully
- ✅ Signal handlers triggering correctly
- ✅ Audit logging capturing all changes
- ✅ No critical errors in logs (24 hours)

**Should-Have (Address within 48 hours)**
- ✅ All UI components render correctly
- ✅ User training sessions completed
- ✅ Documentation deployed and accessible
- ✅ Performance tests pass (>95%)
- ✅ Support team trained and ready

**Nice-to-Have (Address within 7 days)**
- ✅ Monitoring dashboards configured
- ✅ User feedback collected
- ✅ Minor UI/UX improvements identified
- ✅ Future enhancements documented

---

## 🚨 Emergency Contacts

**Technical Escalation**
- **BICTO Director**: director@bicto.gov.ph
- **Lead Developer**: dev-lead@bicto.gov.ph
- **Database Administrator**: dba@bicto.gov.ph
- **DevOps Engineer**: devops@bicto.gov.ph

**Stakeholder Notification**
- **MFBM Director**: director@mfbm.gov.ph
- **BPDA Director**: director@bpda.gov.ph
- **OOBC Chief**: chief@oobc.gov.ph

**Rollback Authority**
- Decision requires approval from: BICTO Director + OOBC Chief
- Expected decision time: 30 minutes
- Rollback execution time: 30-60 minutes

---

## 📝 Sign-Off

**Pre-Deployment Approval**
- [ ] Technical Lead: _________________ Date: _______
- [ ] BICTO Director: _________________ Date: _______
- [ ] OOBC Chief: _________________ Date: _______

**Post-Deployment Confirmation**
- [ ] Deployment Successful: _______ Date: _______ Time: _______
- [ ] 24-Hour Monitoring Complete: _______ Date: _______
- [ ] 7-Day Review Complete: _______ Date: _______
- [ ] Production Sign-Off: _________________ Date: _______

---

**Document Version**: 1.0
**Last Updated**: October 6, 2025
**Next Review**: After Deployment + 7 Days
