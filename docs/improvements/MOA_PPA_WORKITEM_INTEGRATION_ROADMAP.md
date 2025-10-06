# MOA PPA WorkItem Integration: Implementation Roadmap

**Document Type**: Implementation Roadmap
**Date**: 2025-10-05
**Last Updated**: 2025-10-06
**Status**: DRAFT - Action Plan
**Priority**: CRITICAL for M&E Module Enhancement

**Note**: This document uses correct BARMM agency nomenclature:
- **MFBM**: Ministry of Finance and Budget Management (budget formulation, execution, fiscal policy)
- **BPDA**: Bangsamoro Planning and Development Authority (planning, development coordination, BDP alignment)
- **BICTO**: Bangsamoro ICT Office (ICT infrastructure, OBCMS platform, e-governance)

---

## Executive Summary

### The Challenge

**Current State**:
- **MonitoringEntry (PPAs)**: Single-level M&E tracking with budget/approval workflow but NO hierarchical decomposition
- **WorkItem**: Hierarchical execution tracking (projects → activities → tasks) but NO budget or approval integration

**The Gap**: PPAs cannot be broken down into manageable work items, limiting execution visibility and budget control.

### The Solution

**HYBRID INTEGRATION**: Combine MonitoringEntry's budget/approval authority with WorkItem's hierarchical execution tracking.

**Key Insight**: MonitoringEntry remains "source of truth" for budget and approvals, while WorkItem provides WBS execution tracking.

### Expected Outcomes

**After Integration**:
1. ✅ PPAs decompose into hierarchical work structures (Planning → Execution → Completion)
2. ✅ Budget allocated at activity/task level with automatic rollup to PPA
3. ✅ Progress automatically calculated from work item completion
4. ✅ Approval workflow triggers WorkItem project activation
5. ✅ Real-time budget variance tracking (allocated vs. actual expenditure)
6. ✅ Calendar integration for all PPA activities and tasks

**Alignment Score**: 85/100 (from current 40/100)

---

## Phase 1: Foundation - Database Schema & Models

**PRIORITY: CRITICAL | COMPLEXITY: Moderate | DURATION: 2-3 weeks**

### Deliverables

1. **Migration 0018: Add WorkItem Integration to MonitoringEntry**
   - `execution_project` (OneToOne to WorkItem)
   - `budget_distribution_policy` (manual/equal/weighted)
   - `enable_workitem_tracking` (boolean flag)
   - `auto_sync_progress` and `auto_sync_status` (sync flags)

2. **Migration 0021: Add Budget & Explicit FKs to WorkItem**
   - `related_ppa` (FK to MonitoringEntry)
   - `related_assessment`, `related_policy`, `related_community` (explicit FKs)
   - `allocated_budget`, `actual_expenditure`, `budget_notes` (budget tracking)

3. **Model Methods**
   - `MonitoringEntry.sync_progress_from_workitem()`
   - `MonitoringEntry.sync_status_from_workitem()`
   - `MonitoringEntry.get_budget_allocation_tree()`
   - `WorkItem.get_ppa_source()`
   - `WorkItem.get_allocated_budget_rollup()`
   - `WorkItem.get_expenditure_rollup()`
   - `WorkItem.get_budget_variance()`

### Implementation Steps

```bash
# 1. Create migration files
cd src
python manage.py makemigrations monitoring --name add_workitem_integration
python manage.py makemigrations common --name workitem_budget_and_explicit_fks

# 2. Review migrations
python manage.py sqlmigrate monitoring 0018
python manage.py sqlmigrate common 0021

# 3. Apply to local development database
python manage.py migrate

# 4. Run model tests
pytest src/monitoring/tests/test_ppa_workitem_integration.py -v
pytest src/common/tests/test_workitem_budget_tracking.py -v
```

### Testing Checklist

- [ ] MonitoringEntry.execution_project bidirectional linkage works
- [ ] WorkItem.related_ppa only accepts work_type='project'
- [ ] Budget allocation validation prevents exceeding parent budget
- [ ] Progress sync correctly maps WorkItem status to PPA status
- [ ] Budget rollup sums all descendants correctly
- [ ] Database indexes created for performance

### Success Criteria

- All migrations apply cleanly (no errors)
- 90% test coverage for new model methods
- Zero performance regression on existing PPA queries
- Documentation updated in model docstrings

---

## Phase 2: Service Layer & Business Logic

**PRIORITY: CRITICAL | COMPLEXITY: Complex | DURATION: 2-3 weeks**
**DEPENDENCIES**: Phase 1 complete

### Deliverables

1. **WorkItemGenerationService** (`src/monitoring/services/workitem_generation.py`)
   - `create_project_from_ppa()` - Basic project creation
   - `generate_default_structure_program()` - Program-level WBS template
   - `generate_default_structure_activity()` - Activity-level WBS template

2. **BudgetDistributionService** (`src/monitoring/services/budget_distribution.py`)
   - `distribute_budget_equally()` - Equal split across children
   - `distribute_budget_weighted()` - Weighted allocation
   - `distribute_budget_manual()` - Manual specification
   - `get_allocation_tree()` - Hierarchical budget breakdown
   - `lock_budget_allocations()` - Freeze after approval

3. **PPAApprovalService** (enhance existing `src/project_central/services/approval_service.py`)
   - Integrate WorkItem activation into approval workflow
   - `approve_technical_review()` → auto-create execution project
   - `approve_budget_review()` → lock budget allocations
   - `enact_budget()` → activate WorkItem project

### Implementation Steps

```bash
# 1. Create service modules
mkdir -p src/monitoring/services
touch src/monitoring/services/__init__.py
touch src/monitoring/services/workitem_generation.py
touch src/monitoring/services/budget_distribution.py

# 2. Implement services (see architecture doc for code)

# 3. Run service layer tests
pytest src/monitoring/tests/test_budget_distribution_service.py -v
pytest src/monitoring/tests/test_workitem_generation_service.py -v

# 4. Integration tests
pytest src/monitoring/tests/test_ppa_approval_workflow_integration.py -v
```

### Testing Scenarios

**Scenario 1: Auto-Generation from PPA**
```python
ppa = MonitoringEntry.objects.get(title="Livelihood Training")
project = WorkItemGenerationService.generate_default_structure_activity(ppa, user)

# Verify:
# - 3 activities created (Preparation, Execution, Completion)
# - Budget distributed (15%, 75%, 10%)
# - Total allocated = PPA budget
```

**Scenario 2: Budget Distribution**
```python
BudgetDistributionService.distribute_budget_equally(ppa)

# Verify:
# - All children have equal budget
# - Rollup sum = PPA budget
# - No child exceeds parent budget
```

**Scenario 3: Approval Workflow Integration**
```python
PPAApprovalService.approve_technical_review(ppa, user)

# Verify:
# - WorkItem project auto-created
# - ppa.execution_project is set
# - ppa.enable_workitem_tracking = True
```

### Success Criteria

- All service methods pass unit tests
- Integration tests cover full approval → activation workflow
- Budget distribution validates correctly (no over-allocation)
- Performance: Budget rollup < 100ms for 100-item hierarchy

---

## Phase 3: API & Frontend Integration

**PRIORITY: HIGH | COMPLEXITY: Moderate | DURATION: 3-4 weeks**
**DEPENDENCIES**: Phase 2 complete

### Deliverables

1. **REST API Endpoints** (`src/monitoring/api_views.py`)
   ```
   POST /api/monitoring-entries/{id}/enable_workitem_tracking/
   GET  /api/monitoring-entries/{id}/budget_allocation_tree/
   POST /api/monitoring-entries/{id}/distribute_budget/
   POST /api/monitoring-entries/{id}/sync_from_workitem/
   ```

2. **PPA Detail Page Enhancement** (`src/templates/monitoring/detail.html`)
   - "Enable Execution Tracking" button
   - Budget allocation tree visualization
   - WorkItem progress overview (total/completed/in-progress tasks)
   - Budget variance indicators

3. **Budget Distribution UI** (`src/templates/monitoring/partials/budget_allocation_form.html`)
   - Visual tree with drag-drop budget allocation
   - Equal/Weighted/Manual distribution modes
   - Real-time validation (prevent over-allocation)

### UI Mockup Requirements

**PPA Detail Page - Execution Tracking Section**:
```
┌──────────────────────────────────────────────────────────────┐
│ Execution Tracking                        [View Full Project]│
├──────────────────────────────────────────────────────────────┤
│ Budget Allocation                                            │
│ Total PPA Budget:        ₱5,000,000.00                       │
│ Allocated to Activities: ₱4,500,000.00 (90%)                 │
│ Unallocated:             ₱500,000.00 (10%)                   │
│ ██████████████████████░░░ 90%                                │
│                                                              │
│ Hierarchical Breakdown:                                      │
│ ├─ Preparation          ₱750,000.00 (15%) [Edit]            │
│ │  ├─ Venue Booking     ₱300,000.00                          │
│ │  └─ Invitations       ₱450,000.00                          │
│ ├─ Execution            ₱3,750,000.00 (75%) [Edit]           │
│ │  └─ Training Sessions ₱3,750,000.00                        │
│ └─ Completion           ₱500,000.00 (10%) [Edit]             │
│    └─ M&E Report        ₱500,000.00                          │
├──────────────────────────────────────────────────────────────┤
│ Progress Overview                                            │
│ [42 Total] [18 Completed] [15 In Progress] [9 Not Started]  │
└──────────────────────────────────────────────────────────────┘
```

### Implementation Steps

```bash
# 1. Create API views
# Edit src/monitoring/api_views.py (add custom actions to viewset)

# 2. Create serializers
# Edit src/monitoring/serializers.py (add budget tree serializer)

# 3. Update PPA detail template
# Edit src/templates/monitoring/detail.html

# 4. Create budget allocation partial
touch src/templates/monitoring/partials/budget_tree_node.html
touch src/templates/monitoring/partials/budget_allocation_form.html

# 5. Add HTMX interactions
# Create src/static/monitoring/js/budget_allocation.js

# 6. Test API endpoints
pytest src/monitoring/tests/test_api_views.py -v

# 7. Manual UI testing
python manage.py runserver
# Navigate to /monitoring/entry/{uuid}/
```

### Testing Checklist

- [ ] API endpoint returns correct budget tree JSON
- [ ] "Enable Execution Tracking" button creates WorkItem project
- [ ] Budget allocation tree renders correctly
- [ ] Drag-drop budget distribution updates allocations
- [ ] Real-time validation prevents over-allocation
- [ ] HTMX updates work without full page reload
- [ ] Mobile responsiveness (test on tablet/phone)

### Success Criteria

- API response time < 200ms for budget allocation tree
- UI updates instantly (no full page reload)
- Accessibility: WCAG 2.1 AA compliance
- Cross-browser compatibility (Chrome, Firefox, Safari)

---

## Phase 4: Approval Workflow Integration & Automation

**PRIORITY: MEDIUM | COMPLEXITY: Moderate | DURATION: 1-2 weeks**
**DEPENDENCIES**: Phases 1-3 complete

### Deliverables

1. **Celery Tasks** (`src/monitoring/tasks.py`)
   - `auto_sync_ppa_progress.delay()` - Nightly sync of PPA progress from WorkItem
   - `detect_budget_variances.delay()` - Alert on over-budget work items

2. **Django Signals** (`src/monitoring/signals.py`)
   - `workitem_status_changed` → sync to PPA status
   - `workitem_completed` → recalculate PPA progress
   - `budget_allocation_exceeded` → create Alert

3. **Alert Integration** (use existing `project_central.models.Alert`)
   - Alert Type: `workitem_budget_variance`
   - Alert Type: `workitem_execution_blocked`

### Implementation Steps

```bash
# 1. Create Celery tasks
# Edit src/monitoring/tasks.py

# 2. Create signals
touch src/monitoring/signals.py

# 3. Connect signals
# Edit src/monitoring/apps.py (ready() method)

# 4. Schedule periodic tasks
# Edit src/obc_management/settings/base.py (CELERY_BEAT_SCHEDULE)

# 5. Test automation
pytest src/monitoring/tests/test_automation.py -v
```

### Automation Rules

**Rule 1: Nightly Progress Sync**
```
Every night at 2:00 AM:
  For each PPA with enable_workitem_tracking=True:
    - Calculate progress from WorkItem hierarchy
    - Update MonitoringEntry.progress
    - Create audit log entry
```

**Rule 2: Budget Variance Alerts**
```
On WorkItem.actual_expenditure update:
  If actual_expenditure > allocated_budget:
    - Create Alert (severity: high)
    - Notify PPA manager
    - Flag work item in dashboard
```

**Rule 3: Status Sync**
```
On WorkItem.status change:
  If related_ppa and auto_sync_status=True:
    - Map WorkItem status to PPA status
    - Update MonitoringEntry.status
    - Log status change
```

### Success Criteria

- Celery tasks run without errors
- Progress sync accuracy: 100% match with manual calculation
- Alert creation within 5 minutes of variance detection
- No performance impact on interactive requests

---

## Phase 5: Documentation & Training

**PRIORITY: MEDIUM | COMPLEXITY: Simple | DURATION: 1 week**
**DEPENDENCIES**: Phases 1-4 complete

### Deliverables

1. **User Guide** (`docs/user-guide/ppa-execution-tracking.md`)
   - How to enable execution tracking
   - How to distribute budgets
   - How to monitor progress
   - Troubleshooting common issues

2. **API Documentation** (`docs/api/monitoring-workitem-integration.md`)
   - Endpoint specifications
   - Request/response examples
   - Authentication requirements

3. **Video Tutorials** (Optional)
   - 5-minute overview: "PPA Execution Tracking"
   - 10-minute deep dive: "Budget Distribution Strategies"

4. **Training Session for OOBC Staff**
   - Live demo of integration features
   - Q&A session
   - Hands-on practice with test PPAs

### Success Criteria

- Documentation covers all user-facing features
- API docs include working code examples
- Training session feedback: 80%+ satisfaction
- Zero support tickets related to missing documentation

---

## Deployment Strategy

### Staging Deployment (Week 8)

**Pre-Deployment**:
- [ ] Run full test suite (100% pass rate)
- [ ] Database backup created
- [ ] Migration plan reviewed

**Deployment Steps**:
```bash
# 1. Database backup
pg_dump obcms_staging > backup_$(date +%Y%m%d).sql

# 2. Apply migrations
python manage.py migrate --database=staging

# 3. Run smoke tests
pytest src/monitoring/tests/test_smoke.py --database=staging

# 4. Verify UI
# Manual testing on staging.obcms.gov.ph
```

**Post-Deployment**:
- [ ] UAT with OOBC staff (1 week)
- [ ] Performance monitoring (slow query log)
- [ ] Bug triage and fixes

### Production Deployment (Week 10)

**Pre-Deployment**:
- [ ] All UAT issues resolved
- [ ] Load testing completed (100+ concurrent users)
- [ ] Rollback plan documented

**Deployment Window**: Sunday 2:00 AM - 6:00 AM (low traffic)

**Deployment Steps**:
```bash
# 1. Enable maintenance mode
python manage.py maintenance_mode on

# 2. Database backup
pg_dump obcms_prod > backup_prod_$(date +%Y%m%d_%H%M%S).sql

# 3. Apply migrations
python manage.py migrate

# 4. Restart services
sudo systemctl restart gunicorn
sudo systemctl restart celery
sudo systemctl restart celery-beat

# 5. Smoke tests
curl -I https://obcms.gov.ph/health/

# 6. Disable maintenance mode
python manage.py maintenance_mode off
```

**Post-Deployment**:
- [ ] Monitor logs (first 24 hours)
- [ ] Check Celery task execution
- [ ] Verify API response times
- [ ] User feedback collection

---

## Risk Mitigation

### Risk 1: Data Sync Failures

**Mitigation**:
- Implement idempotent sync methods
- Add database transaction wrappers
- Create manual sync UI as fallback

**Rollback Plan**: Disable auto-sync flags, revert to manual PPA updates

### Risk 2: Performance Degradation

**Mitigation**:
- Database indexes on FK fields
- Caching layer for budget rollup calculations
- Async Celery tasks for heavy computations

**Monitoring**: Set up alerts for queries > 1 second

### Risk 3: User Confusion

**Mitigation**:
- Progressive feature rollout (opt-in initially)
- Comprehensive training
- In-app tooltips and help text

**Support Plan**: Dedicated Slack channel for Q&A during first 2 weeks

### Risk 4: Budget Allocation Errors

**Mitigation**:
- Extensive validation in model clean() methods
- Audit trail for all budget changes
- "Undo" capability for budget distributions

**Safety Net**: Keep MonitoringEntry.budget_allocation as source of truth (never modified by WorkItem)

---

## Success Metrics

### Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response Time | < 200ms | New Relic APM |
| Budget Rollup Calculation | < 100ms | Django Debug Toolbar |
| Database Query Count | < 10 per request | Django Debug Toolbar |
| Celery Task Success Rate | > 99% | Flower monitoring |
| Test Coverage | > 90% | pytest-cov |

### User Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| PPAs with Execution Tracking Enabled | > 50% within 3 months | Admin dashboard |
| User Satisfaction | > 80% | Post-deployment survey |
| Support Tickets | < 10 per month | Helpdesk tracking |
| Feature Adoption Rate | > 60% active users | Google Analytics |

### Business Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Budget Variance Visibility | 100% of tracked PPAs | Reporting dashboard |
| Execution Progress Accuracy | > 95% | Manual audit sample |
| On-Time PPA Completion Rate | Increase by 15% | Historical comparison |

---

## Timeline Summary

| Phase | Duration | Start | End |
|-------|----------|-------|-----|
| Phase 1: Database Schema | 2-3 weeks | Week 1 | Week 3 |
| Phase 2: Service Layer | 2-3 weeks | Week 3 | Week 6 |
| Phase 3: API & Frontend | 3-4 weeks | Week 6 | Week 10 |
| Phase 4: Automation | 1-2 weeks | Week 8 | Week 10 |
| Phase 5: Documentation | 1 week | Week 9 | Week 10 |
| **Staging Deployment** | - | Week 8 | - |
| **UAT & Bug Fixes** | 1 week | Week 9 | Week 10 |
| **Production Deployment** | - | Week 10 | - |

**Total Duration**: 10 weeks (2.5 months)

---

## Next Steps

### Immediate Actions (This Week)

1. **Stakeholder Review** (2-3 days)
   - Share architecture doc with BICTO leadership (ICT platform oversight)
   - Coordinate with MFBM (budget workflow requirements)
   - Present to OOBC technical team
   - Gather feedback and adjust plan

2. **Technical Prep** (2 days)
   - Set up development branch: `feature/ppa-workitem-integration`
   - Create GitHub project board for task tracking
   - Assign developers to phases

3. **Kick-off Meeting** (1 day)
   - Review roadmap with full team
   - Clarify roles and responsibilities
   - Establish communication channels (Slack, weekly stand-ups)

### Week 1 Deliverables

- [ ] Migration 0018 created and tested locally
- [ ] Migration 0021 created and tested locally
- [ ] Model method implementations (50% complete)
- [ ] Unit test suite started (30% coverage)

---

## Appendix: Reference Documents

**Primary Architecture**:
- [MOA PPA WorkItem Integration Architecture](./MOA_PPA_WORKITEM_INTEGRATION_ARCHITECTURE.md)

**Supporting Research**:
- [WorkItem Architectural Assessment](./WORKITEM_ARCHITECTURAL_ASSESSMENT.md)
- [OBCMS Unified PM Research](./obcms_unified_pm_research.md)

**Code References**:
- MonitoringEntry Model: `/src/monitoring/models.py`
- WorkItem Model: `/src/common/work_item_model.py`
- Budget Approval Stages: `/src/project_central/models.py`

---

**Document Maintained By**: BICTO System Architect (OBCMS Platform)
**Review Cycle**: Weekly during implementation, monthly post-deployment
**Last Updated**: 2025-10-06
