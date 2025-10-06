# Query Template System Deployment Checklist

**Status:** Ready for Deployment
**Target Environment:** Staging → Production
**Est. Deployment Time:** 30 minutes
**Est. Validation Time:** 2 hours

---

## Pre-Deployment Checklist

### System Validation

- [ ] **All 559 templates registered successfully**
  ```bash
  cd src
  ./manage.py validate_query_templates
  # Expected: ✅ 559 templates registered across 18 categories
  ```

- [ ] **All 220+ tests passing (98%+ pass rate)**
  ```bash
  python -m pytest common/tests/test_*templates.py -v
  # Expected: 220+ passed in ~15 seconds
  ```

- [ ] **Performance benchmarks met (<10ms matching)**
  ```bash
  ./manage.py benchmark_query_system
  # Expected: Average match time < 10ms
  ```

- [ ] **Entity extraction working (8 resolvers)**
  ```bash
  python -m pytest common/tests/test_entity_extractor.py -v
  # Expected: All entity resolver tests passing
  ```

- [ ] **Django ORM queries validated**
  ```bash
  # Test queries in Django shell
  ./manage.py shell
  >>> from common.ai_services.chat.query_templates import get_template_registry
  >>> registry = get_template_registry()
  >>> # Test sample queries
  ```

- [ ] **Cache configuration verified**
  ```bash
  # Check Redis connection
  redis-cli PING
  # Expected: PONG
  ```

- [ ] **Error handling tested**
  - Missing templates (fallback behavior)
  - Invalid queries (error messages)
  - Database errors (graceful degradation)
  - Timeout scenarios (retry logic)

### Database Preparation

- [ ] **All models exist**
  - Communities (OBCCommunity, Ethnicity, etc.)
  - MANA (Assessment, Need, Workshop, etc.)
  - Coordination (Partnership, Stakeholder, Engagement, etc.)
  - Projects (MonitoringEntry, Activity, etc.)
  - Policies (PolicyRecommendation, Evidence, etc.)

- [ ] **Database indexes created**
  ```sql
  -- Critical indexes for performance
  CREATE INDEX idx_community_status ON communities_obccommunity(status);
  CREATE INDEX idx_assessment_status ON mana_assessment(status);
  CREATE INDEX idx_partnership_status ON coordination_partnership(status);
  CREATE INDEX idx_ppa_status ON project_central_monitoringentry(status);
  CREATE INDEX idx_policy_status ON policies_policyrecommendation(status);
  CREATE INDEX idx_need_linked_ppa ON mana_need(linked_ppa_id);
  ```

- [ ] **Sample data loaded (for testing)**
  ```bash
  # Load fixtures if needed
  ./manage.py loaddata test_data.json
  ```

- [ ] **Database migrations applied**
  ```bash
  ./manage.py migrate
  # Expected: No unapplied migrations
  ```

- [ ] **Connection pooling configured**
  ```python
  # settings/production.py
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.postgresql',
          'CONN_MAX_AGE': 600,  # 10 minutes
          # ... other settings
      }
  }
  ```

### Infrastructure

- [ ] **Redis cache configured**
  ```bash
  # Test Redis connection
  redis-cli
  > SET test "value"
  > GET test
  # Expected: "value"
  ```

- [ ] **Django settings optimized**
  ```python
  # settings/production.py
  CACHES = {
      'default': {
          'BACKEND': 'django_redis.cache.RedisCache',
          'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
          'OPTIONS': {
              'CLIENT_CLASS': 'django_redis.client.DefaultClient',
              'MAX_ENTRIES': 10000,
          }
      }
  }
  ```

- [ ] **Application servers scaled**
  - Minimum 2 instances for high availability
  - Load balancer configured
  - Health checks enabled

- [ ] **Monitoring configured**
  - Application performance monitoring (APM)
  - Error tracking (Sentry, etc.)
  - Query performance logging
  - User activity tracking

- [ ] **Logging enabled**
  ```python
  # settings/production.py
  LOGGING = {
      'version': 1,
      'disable_existing_loggers': False,
      'handlers': {
          'file': {
              'level': 'INFO',
              'class': 'logging.FileHandler',
              'filename': '/var/log/obcms/query_templates.log',
          },
      },
      'loggers': {
          'common.ai_services.chat.query_templates': {
              'handlers': ['file'],
              'level': 'INFO',
              'propagate': True,
          },
      },
  }
  ```

---

## Deployment Steps

### Step 1: Backup Current System

- [ ] **Backup database**
  ```bash
  cd /path/to/obcms
  ./manage.py dumpdata > backup_pre_template_expansion_$(date +%Y%m%d).json
  ```

- [ ] **Backup code**
  ```bash
  git tag pre-template-expansion-$(date +%Y%m%d)
  git push origin pre-template-expansion-$(date +%Y%m%d)
  ```

- [ ] **Document current system state**
  - Number of templates: 151 (baseline)
  - Test pass rate: 96%
  - Average query time: (record current performance)
  - Active users: (record current metrics)

### Step 2: Deploy New Template Files

- [ ] **Pull latest code**
  ```bash
  git fetch origin
  git checkout main
  git pull origin main
  ```

- [ ] **Verify template files**
  ```bash
  ls -la src/common/ai_services/chat/query_templates/

  # Expected new files:
  # temporal.py
  # cross_domain.py
  # analytics.py
  # comparison.py
  # infrastructure.py
  # livelihood.py
  # stakeholders.py
  # budget.py
  ```

- [ ] **Install dependencies (if any)**
  ```bash
  pip install -r requirements/production.txt
  ```

### Step 3: Run Migrations (if any)

- [ ] **Check for new migrations**
  ```bash
  cd src
  ./manage.py makemigrations --dry-run
  # Expected: No new migrations (templates don't require DB changes)
  ```

- [ ] **Apply migrations**
  ```bash
  ./manage.py migrate
  # Expected: "No migrations to apply" (or apply if any exist)
  ```

### Step 4: Restart Application Servers

- [ ] **Restart Django application**
  ```bash
  # Option 1: Systemd
  sudo systemctl restart obcms-web

  # Option 2: Gunicorn
  sudo systemctl restart gunicorn-obcms

  # Option 3: Docker
  docker-compose restart web

  # Option 4: Manual (if using manage.py runserver)
  # Kill current process and restart
  ```

- [ ] **Verify server started successfully**
  ```bash
  # Check process status
  sudo systemctl status obcms-web

  # Check logs
  tail -f /var/log/obcms/django.log

  # Test health endpoint
  curl http://localhost:8000/health/
  # Expected: {"status": "ok"}
  ```

### Step 5: Clear Cache

- [ ] **Clear Redis cache**
  ```bash
  redis-cli FLUSHALL
  # OR clear specific cache namespace
  redis-cli --scan --pattern "obcms:*" | xargs redis-cli DEL
  ```

- [ ] **Clear Django cache**
  ```bash
  cd src
  ./manage.py shell
  >>> from django.core.cache import cache
  >>> cache.clear()
  >>> exit()
  ```

### Step 6: Run Validation

- [ ] **Validate template registration**
  ```bash
  cd src
  ./manage.py validate_query_templates

  # Expected output:
  # ✅ 559 templates registered
  # ✅ 18 categories available
  # ✅ All templates have examples
  # ✅ All templates have descriptions
  # ✅ No duplicate IDs
  # ✅ Pattern compilation successful
  ```

- [ ] **Run comprehensive tests**
  ```bash
  python -m pytest common/tests/test_*templates.py -v

  # Expected:
  # 220+ passed in ~15 seconds
  # 98%+ pass rate
  ```

### Step 7: Run Smoke Tests

- [ ] **Test top 20 user queries**
  ```bash
  cd src
  ./manage.py test_chat_queries

  # Queries tested:
  # 1. "How many communities?"
  # 2. "Show me all provinces"
  # 3. "Needs without PPAs"
  # 4. "Assessment trends"
  # 5. "Region IX vs Region X"
  # 6. "Budget ceiling utilization"
  # 7. "Communities with assessments"
  # 8. "Infrastructure gaps"
  # 9. "Livelihood opportunities"
  # 10. "High influence stakeholders"
  # ... (10 more)

  # Expected: All 20 queries return results
  ```

- [ ] **Manual testing**
  - Navigate to chat interface
  - Test 5 queries from each category
  - Verify results are accurate
  - Check response times

### Step 8: Monitor Error Logs

- [ ] **Monitor Django logs**
  ```bash
  tail -f /var/log/obcms/django.log

  # Watch for:
  # - Template matching errors
  # - Query execution errors
  # - Performance issues
  ```

- [ ] **Monitor application logs**
  ```bash
  tail -f /var/log/obcms/gunicorn.log

  # Watch for:
  # - Server errors (500)
  # - Timeout issues
  # - Memory problems
  ```

- [ ] **Monitor Nginx logs**
  ```bash
  tail -f /var/log/nginx/obcms.error.log

  # Watch for:
  # - Gateway timeouts
  # - Connection errors
  # - Rate limiting issues
  ```

---

## Post-Deployment Verification

### Functional Testing (30 minutes)

- [ ] **Test 20 sample queries across all domains**
  1. Communities: "How many OBC communities?"
  2. Geographic: "Show me the list of provinces"
  3. MANA: "Show pending assessments"
  4. Coordination: "Active partnerships"
  5. Projects: "PPAs by DSWD"
  6. Policies: "Approved policy recommendations"
  7. Cross-Domain: "Needs without PPAs" ⭐
  8. Temporal: "Assessment trends over time" ⭐
  9. Analytics: "Statistical summary" ⭐
  10. Comparison: "Region IX vs Region X" ⭐
  11. Staff: "My pending tasks"
  12. Needs: "Unmet infrastructure needs"
  13. Infrastructure: "Communities with poor water access"
  14. Livelihood: "Fishing communities"
  15. Stakeholders: "High influence religious leaders"
  16. Budget: "Budget ceiling violations"
  17. General: "Help with queries"
  18. Multi-entity: "Critical infrastructure needs in Region IX"
  19. Temporal range: "Assessments last 30 days"
  20. Complex: "Complete flow: Needs to Policies to PPAs"

- [ ] **Verify correct template matching**
  - Check logs for matched template IDs
  - Verify highest priority templates selected
  - Confirm entity extraction working

- [ ] **Check query results accuracy**
  - Compare results with database records
  - Verify counts match expected values
  - Check list results are complete

- [ ] **Validate entity extraction**
  - Location entities (regions, provinces, etc.)
  - Date entities (ranges, fiscal years, etc.)
  - Sector entities (education, health, etc.)
  - Priority entities (critical, high, etc.)

- [ ] **Test edge cases**
  - Ambiguous queries (multiple matches)
  - Typos and misspellings
  - Incomplete queries
  - Very long queries
  - Special characters

### Performance Testing (15 minutes)

- [ ] **Run benchmark command**
  ```bash
  cd src
  ./manage.py benchmark_query_system

  # Expected results:
  # Average match time: <10ms
  # 95th percentile: <15ms
  # 99th percentile: <20ms
  ```

- [ ] **Verify database query performance**
  ```bash
  # Enable query logging
  # Check slow query log
  # Target: <500ms for complex queries
  ```

- [ ] **Monitor memory usage**
  ```bash
  # Check application memory
  ps aux | grep gunicorn

  # Expected: Stable memory usage (no leaks)
  # Target: <500MB per worker
  ```

- [ ] **Test concurrent requests**
  ```bash
  # Use Apache Bench or similar
  ab -n 1000 -c 50 http://localhost:8000/chat/

  # Expected: All requests successful
  # Target: >95% success rate
  ```

### User Acceptance Testing (2 hours)

- [ ] **Staff members test real-world queries**
  - OOBC staff: 5 people × 10 queries each
  - Domain experts: MANA, Coordination, Projects
  - End users: Field workers, managers

- [ ] **Collect feedback on accuracy**
  - Are results correct?
  - Are results complete?
  - Are results relevant?
  - Are results understandable?

- [ ] **Note any missing query types**
  - Document queries that don't match any template
  - Prioritize new templates for next iteration
  - Estimate effort for implementation

- [ ] **Document edge cases**
  - Unexpected query formats
  - Ambiguous queries
  - Multi-domain queries
  - Natural language variations

- [ ] **Verify user satisfaction**
  - Survey: 1-10 rating on usefulness
  - Survey: 1-10 rating on accuracy
  - Survey: 1-10 rating on speed
  - Target: >8 average rating

### Monitoring (First 24 Hours)

- [ ] **Monitor error rates (target: <1%)**
  ```bash
  # Check error logs every 2 hours
  # Track error types and frequencies
  # Alert if error rate exceeds 1%
  ```

- [ ] **Track query volume and patterns**
  ```bash
  # Log all queries
  # Analyze popular vs unused templates
  # Identify missing query types
  ```

- [ ] **Check performance metrics**
  - Match time: Target <10ms average
  - Query time: Target <500ms for complex queries
  - Response time: Target <1 second total
  - Uptime: Target >99.9%

- [ ] **Review user feedback**
  - Collect feedback via in-app survey
  - Monitor support tickets
  - Track user satisfaction ratings
  - Address issues within 24 hours

- [ ] **Address any issues immediately**
  - Critical issues: Fix within 1 hour
  - High priority: Fix within 4 hours
  - Medium priority: Fix within 24 hours
  - Low priority: Schedule for next sprint

---

## Rollback Plan

### When to Rollback

**Trigger rollback if:**
- Template matching error rate >5%
- Query execution error rate >2%
- Performance degradation >20% (match time or query time)
- Memory leak detected (>20% increase)
- User-reported critical bugs (data loss, security issues)
- System instability (crashes, timeouts)

### Rollback Procedure

#### Step 1: Revert to Previous Code Version

- [ ] **Revert code changes**
  ```bash
  git log --oneline -10
  # Find commit hash before template expansion

  git revert <commit_hash>
  # OR
  git reset --hard <commit_hash>

  git push origin main --force
  ```

#### Step 2: Restore Database Backup (if needed)

- [ ] **Restore database**
  ```bash
  cd src
  ./manage.py loaddata backup_pre_template_expansion_YYYYMMDD.json

  # Verify restoration
  ./manage.py shell
  >>> from common.ai_services.chat.query_templates import get_template_registry
  >>> registry = get_template_registry()
  >>> len(registry.templates)
  # Expected: 151 (baseline)
  ```

#### Step 3: Restart Application Servers

- [ ] **Restart servers**
  ```bash
  sudo systemctl restart obcms-web
  # OR
  sudo systemctl restart gunicorn-obcms
  # OR
  docker-compose restart web
  ```

#### Step 4: Clear Cache

- [ ] **Clear all caches**
  ```bash
  redis-cli FLUSHALL

  cd src
  ./manage.py shell
  >>> from django.core.cache import cache
  >>> cache.clear()
  ```

#### Step 5: Verify System Restored

- [ ] **Run validation**
  ```bash
  cd src
  ./manage.py validate_query_templates
  # Expected: 151 templates (baseline)
  ```

- [ ] **Test critical queries**
  - Test 10 most common queries
  - Verify all return correct results
  - Check performance is acceptable

#### Step 6: Notify Users

- [ ] **Communication**
  - Send system alert: "System temporarily reverted"
  - Explain: "Issues being investigated"
  - Provide: "Expected resolution time"
  - Offer: "Support contact for urgent needs"

#### Step 7: Post-Mortem

- [ ] **Investigate root cause**
  - Review error logs
  - Analyze performance metrics
  - Identify what went wrong
  - Document lessons learned

- [ ] **Plan fix**
  - Develop solution
  - Test thoroughly in staging
  - Schedule re-deployment
  - Communicate timeline to stakeholders

---

## Success Criteria

### Deployment Successful If:

✅ **All 559 templates registered** (no errors)
✅ **98%+ test pass rate** (220+ tests passing)
✅ **<10ms average match time** (performance maintained)
✅ **<1% error rate** (queries executing correctly)
✅ **>8 user satisfaction rating** (feedback positive)
✅ **No critical bugs** (system stable)
✅ **No performance degradation** (speed maintained or improved)
✅ **Zero data loss** (all data intact)

### Deployment Failed If:

❌ Template registration errors (>5% failure)
❌ Test pass rate <95%
❌ Average match time >20ms
❌ Error rate >2%
❌ User satisfaction <7
❌ Critical bugs reported
❌ Performance degradation >20%
❌ Data loss or corruption

---

## Contact Information

### Escalation Path

**Level 1: Development Team**
- Primary Contact: Development Lead
- Response Time: <1 hour (business hours)
- Scope: Template issues, query errors, performance problems

**Level 2: System Administrator**
- Primary Contact: DevOps Lead
- Response Time: <30 minutes (24/7)
- Scope: Server issues, database problems, infrastructure failures

**Level 3: Technical Director**
- Primary Contact: CTO/Technical Director
- Response Time: <15 minutes (critical issues only)
- Scope: Critical system failures, security incidents, data loss

### Support Channels

- **Slack:** #obcms-support
- **Email:** support@obcms.gov.ph
- **Phone:** +63 XXX XXX XXXX (24/7 hotline)
- **Ticketing:** https://support.obcms.gov.ph

---

## Post-Deployment Tasks

### Week 1

- [ ] Daily error log review
- [ ] Daily performance monitoring
- [ ] Collect user feedback (survey)
- [ ] Address critical issues
- [ ] Document lessons learned

### Week 2-4

- [ ] Weekly error log review
- [ ] Weekly performance analysis
- [ ] Analyze query usage patterns
- [ ] Identify popular templates
- [ ] Plan template optimizations

### Month 2-3

- [ ] Monthly template audit
- [ ] User satisfaction survey
- [ ] Gap analysis (missing queries)
- [ ] Plan next template expansion
- [ ] Update documentation

---

**Checklist Version:** 1.0
**Last Updated:** 2025-10-06
**Next Review:** 2025-11-06
**Owner:** Development Team

---

**END OF CHECKLIST**
