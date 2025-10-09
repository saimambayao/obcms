# Unified Work Hierarchy System - Evaluation & Refactoring Plan

**Date:** 2025-10-05
**Status:** ✅ APPROVED - FULL IMPLEMENTATION IN PROGRESS
**Complexity:** HIGH
**Priority:** STRATEGIC ENHANCEMENT
**Phase:** Phase 1 - Model Creation (Week 1)
**Implementation Start:** 2025-10-05

---

## Executive Summary

This document evaluates the feasibility and architecture for refactoring OBCMS into a **Unified Hierarchical Work Management System** where Projects, Sub-projects, Activities, Sub-activities, Tasks, and Subtasks are managed through a single, cohesive model with flexible hierarchical relationships and calendar integration.

**Key Finding:** ✅ **FEASIBLE AND APPROVED** - Implementation in progress with phased migration approach

**Decision:** Full implementation approved - proceeding with all 5 phases

---

## Table of Contents

1. [Current Architecture Analysis](#1-current-architecture-analysis)
2. [Research Findings](#2-research-findings)
3. [Proposed Unified Architecture](#3-proposed-unified-architecture)
4. [Implementation Approaches](#4-implementation-approaches)
5. [Recommended Solution](#5-recommended-solution)
6. [Migration Strategy](#6-migration-strategy)
7. [Risks & Mitigation](#7-risks--mitigation)
8. [Decision Framework](#8-decision-framework)
9. [Implementation Estimates](#9-implementation-estimates)
10. [Conclusion & Next Steps](#10-conclusion--next-steps)

---

## 1. Current Architecture Analysis

### 1.1 Current State Overview

OBCMS currently has **3 separate systems** for work management:

#### A. **StaffTask Model** (`common.models.StaffTask`)
- **Purpose:** Task management with domain-specific relationships
- **Location:** `src/common/models.py` (lines 628-1446)
- **Key Features:**
  - Extensive domain relationships (30+ ForeignKey fields)
  - Status tracking (not_started, in_progress, at_risk, completed)
  - Priority levels (low, medium, high, critical)
  - Board position for Kanban view
  - Recurrence support via `RecurringEventPattern`
  - Task context field (standalone, project, activity, project_activity)
  - Workflow integration (`linked_workflow`, `linked_ppa`)

#### B. **ProjectWorkflow Model** (`project_central.models.ProjectWorkflow`)
- **Purpose:** Project lifecycle management
- **Location:** `src/project_central/models.py` (lines 17-369)
- **Key Features:**
  - Workflow stages (9 stages from need_identification to completion)
  - Priority levels (low, medium, high, urgent, critical)
  - Linked to MANA Need and Monitoring PPA
  - Stage history tracking (JSON field)
  - Budget tracking
  - Project activities relationship (`project_activities`)

#### C. **Event Model** (`coordination.models.Event`)
- **Purpose:** Activity/event management
- **Location:** `src/coordination/models.py` (lines 1583+)
- **Key Features:**
  - 15 event types (meeting, consultation, workshop, etc.)
  - Status tracking (draft, planned, scheduled, confirmed, etc.)
  - Calendar integration (start/end dates, times)
  - Community and organization relationships
  - Assessment linkage

### 1.2 Current Integration Points

**Existing Integration (Phase 1 - Implemented):**
- `StaffTask.task_context` field distinguishes task types
- `StaffTask.linked_workflow` connects tasks to projects
- `StaffTask.linked_event` connects tasks to activities
- `ProjectWorkflow.project_activities` relationship to Events

**Current Limitations:**
1. ❌ **No hierarchical relationships** within same type (no sub-projects, no sub-tasks)
2. ❌ **Three separate models** require different forms and logic
3. ❌ **Inconsistent fields** across models (status, priority, dates)
4. ❌ **Complex relationships** harder to query and maintain
5. ❌ **Limited flexibility** in work breakdown structure

### 1.3 Current Database Fields Comparison

| Field Category | StaffTask | ProjectWorkflow | Event |
|---------------|-----------|-----------------|-------|
| **Identity** | id, title, description | id (via Need title) | id, title, description |
| **Status** | 4 statuses | current_stage (9 stages) | 9 statuses |
| **Priority** | 4 levels | 5 levels | 4 levels |
| **Dates** | start_date, due_date, completed_at | initiated_date, target_completion, actual_completion | start_date, end_date, start_time, end_time |
| **Progress** | progress (0-100) | overall_progress (0-100) | ❌ None |
| **Assignees** | assignees (M2M), teams (M2M) | project_lead, mao_focal_person | organizer, attendees |
| **Relationships** | 30+ domain FKs | primary_need, ppa | community, organizations |
| **Calendar** | ✅ Via linked_event | ❌ No direct calendar | ✅ Native calendar |
| **Recurrence** | ✅ RecurringEventPattern | ❌ None | ✅ RecurringEventPattern |
| **Hierarchy** | ❌ None | ❌ None (except via relationships) | ❌ None |

---

## 2. Research Findings

### 2.1 Work Breakdown Structure (WBS) Standards

**Industry Standard Hierarchy:**
1. **Level 1:** Project goal (ultimate deliverable)
2. **Level 2:** Major categories of deliverables
3. **Level 3:** Smaller groups of deliverables or individual deliverables
4. **Level 4:** Work packages (individual tasks)

**Key Findings:**
- Most projects use **2-4 levels** of hierarchy
- WBS is recognized as one of the **7 main project management techniques** (Forbes, 2024)
- Tasks should be deliverable-focused, not activity-focused

### 2.2 Django Hierarchical Model Patterns

#### Pattern 1: **Self-Referential Foreign Key (Adjacency List)**
```python
parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE)
```
- ✅ **Pros:** Simple, flexible, easy to implement
- ❌ **Cons:** Slow tree queries, complex recursive lookups
- **Best for:** Shallow hierarchies (<3 levels)

#### Pattern 2: **MPTT (Modified Preorder Tree Traversal)** ⭐ CHOSEN
```python
from mptt.models import MPTTModel, TreeForeignKey

class WorkItem(MPTTModel):
    parent = TreeForeignKey('self', null=True, on_delete=models.CASCADE)
```
- ✅ **Pros:** Fast queries, efficient tree operations
- ❌ **Cons:** Every save triggers tree rebalancing, concurrent writes cause deadlocks
- **Best for:** Read-heavy hierarchies with infrequent updates
- **Package:** `django-mptt` (actively maintained)
- **Status:** ✅ **SELECTED FOR IMPLEMENTATION**

#### Pattern 3: **Polymorphic + MPTT (django-polymorphic-tree)**
```python
from polymorphic_tree.models import PolymorphicMPTTModel

class WorkItem(PolymorphicMPTTModel):
    # Different types: Project, Activity, Task
    pass
```
- ✅ **Pros:** Type-specific fields, inheritance, efficient queries
- ❌ **Cons:** Complex migrations, harder to maintain, overhead
- **Best for:** True polymorphic trees with different node types
- **Package:** `django-polymorphic-tree`
- **Status:** ❌ **NOT SELECTED** (too complex for current needs)

#### Pattern 4: **Closure Table**
- Separate table storing all ancestor-descendant relationships
- ✅ **Pros:** Extremely fast queries, flexible
- ❌ **Cons:** Complex to implement, storage overhead
- **Best for:** Very deep/complex hierarchies
- **Status:** ❌ **NOT SELECTED** (MPTT sufficient)

### 2.3 Real-World Task Management Schemas

**Common Database Components (2024 Best Practices):**
1. **Unified Work Items Table** with type field
2. **Self-referential hierarchy** (parent_id)
3. **Status and priority** fields
4. **Date/time tracking** (start, end, due, completed)
5. **Assignment tables** (users, teams)
6. **Comments/attachments** tables
7. **Time tracking** tables

**Key Insight:** Most modern task management systems use a **single unified table** with a type discriminator field rather than separate tables for each work item type.

---

## 3. Proposed Unified Architecture

### 3.1 Core Design Principles

1. **Single Source of Truth:** One model (`WorkItem`) for all work types
2. **Flexible Hierarchy:** Self-referential tree supporting unlimited depth
3. **Type-Specific Behavior:** Type field determines validation and UI
4. **Calendar Integration:** All work items are calendar-compatible
5. **Backward Compatibility:** Preserve existing relationships during migration
6. **Progressive Enhancement:** Migrate in phases without breaking existing features

### 3.2 Unified WorkItem Model Architecture

**Core Model:** `common.work_item_model.WorkItem`
**Implementation:** Complete (see `src/common/work_item_model.py`)

**Key Components:**

#### A. Work Type Hierarchy
```
WORK_TYPE_PROJECT          → Top-level projects
WORK_TYPE_SUB_PROJECT      → Nested projects
WORK_TYPE_ACTIVITY         → Activities within projects
WORK_TYPE_SUB_ACTIVITY     → Nested activities
WORK_TYPE_TASK             → Individual tasks
WORK_TYPE_SUBTASK          → Task breakdowns
```

#### B. Hierarchical Rules
```python
ALLOWED_CHILD_TYPES = {
    'project': ['sub_project', 'activity', 'task'],
    'sub_project': ['sub_project', 'activity', 'task'],  # Recursive nesting
    'activity': ['sub_activity', 'task'],
    'sub_activity': ['sub_activity', 'task'],  # Recursive nesting
    'task': ['subtask'],
    'subtask': [],  # Leaf nodes
}
```

#### C. Example Hierarchies

```
Project A: MANA Assessment Rollout
├── Sub-Project A1: Region IX Implementation
│   ├── Activity A1.1: Provincial Training Workshop (Zamboanga del Sur)
│   │   ├── Task: Prepare training materials
│   │   ├── Task: Send invitations to LGUs
│   │   └── Subtask: Book venue
│   └── Activity A1.2: Field Assessment (Pagadian City)
│       └── Task: Conduct household surveys
├── Activity A2: Stakeholder Consultation
│   ├── Sub-Activity A2.1: Community Leader Engagement
│   │   └── Task: Interview barangay captains
│   └── Task: Document findings
└── Task: Submit final MANA report to BARMM
    ├── Subtask: Draft executive summary
    ├── Subtask: Compile assessment data
    └── Subtask: Review and finalize
```

### 3.3 Key Architectural Features

#### A. **Type-Specific Data (JSON Fields)**
```python
# Project-specific
project_data = {
    'workflow_stage': 'implementation',
    'estimated_budget': 500000.00,
    'budget_approved': True,
    'stage_history': [...]
}

# Activity-specific
activity_data = {
    'event_type': 'workshop',
    'location': 'Zamboanga City',
    'attendees_count': 50,
    'objectives': '...'
}

# Task-specific
task_data = {
    'domain': 'mana',
    'task_category': 'assessment',
    'deliverable_type': 'survey_data',
    'estimated_hours': 8.5
}
```

#### B. **Related Items (Non-Hierarchical)**
```python
# Tasks can be related to multiple activities/projects
task.related_items.add(activity1, activity2, project1)

# Activities can be grouped as related
activity1.related_items.add(activity2, activity3)  # Related activities

# Projects can be grouped
project1.related_items.add(project2)  # Related projects
```

#### C. **Calendar Integration**
- All work items have calendar fields (start_date, due_date, times)
- `is_calendar_visible` flag controls display
- Type-specific colors (Projects: Blue, Activities: Green, Tasks: Orange)
- Recurrence support via existing `RecurringEventPattern`

#### D. **Progress Tracking**
```python
# Auto-calculate from children
project.auto_calculate_progress = True
project.progress  # Automatically calculated from child completion

# Manual progress
task.auto_calculate_progress = False
task.progress = 75  # Manually set
```

---

## 4. Implementation Approaches

### Approach A: **Big Bang Migration** ❌ NOT RECOMMENDED
- Migrate all at once
- High risk, complex rollback
- System downtime required
- **Status:** REJECTED

### Approach B: **Phased Migration with Dual-Write** ✅ RECOMMENDED
1. Create new `WorkItem` model
2. Dual-write: Save to both old and new models
3. Migrate data in background
4. Switch reads to new model
5. Deprecate old models
- **Status:** ✅ **SELECTED AND IN PROGRESS**

### Approach C: **Proxy Models (Temporary)** ⚙️ ALTERNATIVE
- Use Django proxy models to provide unified interface
- Keep separate tables initially
- Migrate gradually
- **Status:** Will be used in Phase 4 for backward compatibility

---

## 5. Recommended Solution

### 5.1 Hybrid Approach: **MPTT + JSON Fields + Phased Migration**

**Why This Approach:**
1. ✅ **MPTT** for efficient tree queries (django-mptt is battle-tested)
2. ✅ **JSON fields** for type-specific data (flexible, no schema changes)
3. ✅ **Generic FK** preserves existing domain relationships
4. ✅ **Phased migration** reduces risk
5. ✅ **Backward compatible** during transition

### 5.2 Package Dependencies

```python
# requirements/base.txt
django-mptt>=0.16.0  # Tree support ✅ INSTALLED
django-cors-headers>=4.6.0  # Existing
djangorestframework>=3.15.2  # Existing
```

**Status:** ✅ All dependencies installed

---

## 6. Migration Strategy

### Phase 1: **Model Creation & Setup** (CURRENT PHASE)

**Duration:** 2-3 weeks
**Status:** 🔄 IN PROGRESS

**Tasks:**
- [x] Install django-mptt
- [x] Add 'mptt' to INSTALLED_APPS
- [x] Create WorkItem model (`common/work_item_model.py`)
- [ ] Create Django migrations
- [ ] Create admin interface
- [ ] Create unified forms
- [ ] Add backward-compatible properties

**Deliverables:**
- WorkItem model ready for testing
- Admin interface functional
- Initial migrations created

### Phase 2: **Data Migration**

**Duration:** 1 week
**Status:** ⏳ PENDING

**Tasks:**
1. ✅ Create migration management commands
2. ✅ Migrate StaffTask → WorkItem (type='task')
3. ✅ Migrate ProjectWorkflow → WorkItem (type='project')
4. ✅ Migrate Event → WorkItem (type='activity')
5. ✅ Migrate hierarchical relationships
6. ✅ Verify data integrity

**Management Commands:**
```bash
# Dry-run first
python manage.py migrate_tasks_to_workitems --dry-run
python manage.py migrate_projects_to_workitems --dry-run
python manage.py migrate_events_to_workitems --dry-run

# Execute
python manage.py migrate_tasks_to_workitems --execute
python manage.py migrate_projects_to_workitems --execute
python manage.py migrate_events_to_workitems --execute
```

### Phase 3: **UI Refactoring**

**Duration:** 2-3 weeks
**Status:** ⏳ PENDING

**Tasks:**
1. ✅ Create unified WorkItem CRUD views
2. ✅ Update calendar to use WorkItem
3. ✅ Implement hierarchical tree UI (HTMX)
4. ✅ Add drag-and-drop for hierarchy
5. ✅ Update dashboards

**UI Components:**
- Hierarchical tree view with expand/collapse
- Unified work item modal (type-specific fields)
- Calendar integration (all work types)
- Kanban board (hierarchical grouping)

### Phase 4: **Switch Reads & Cleanup**

**Duration:** 1 week
**Status:** ⏳ PENDING

**Tasks:**
1. ✅ Switch all queries to WorkItem
2. ✅ Create proxy models for old interfaces
3. ✅ Deprecate old models (keep for rollback)
4. ✅ Archive old tables (don't drop immediately)

**Proxy Models (Backward Compatibility):**
```python
class StaffTaskProxy(WorkItem):
    """Proxy model for backward compatibility with StaffTask queries."""
    class Meta:
        proxy = True

    objects = WorkItemManager(work_type=WorkItem.WORK_TYPE_TASK)
```

### Phase 5: **Enhancement & Optimization**

**Duration:** Ongoing
**Status:** ⏳ PENDING

**Tasks:**
1. ✅ Add advanced tree operations (move, copy, bulk actions)
2. ✅ Implement work item templates
3. ✅ Add Gantt chart view
4. ✅ Optimize MPTT queries
5. ✅ Performance monitoring

---

## 7. Risks & Mitigation

### Risk 1: **MPTT Concurrent Write Deadlocks**
- **Likelihood:** Medium
- **Impact:** High
- **Mitigation:**
  - Use database-level locking for tree operations
  - Implement retry logic
  - Batch operations during off-peak hours
  - Monitor deadlock frequency
- **Status:** Mitigation strategies documented

### Risk 2: **Data Migration Complexity**
- **Likelihood:** High
- **Impact:** High
- **Mitigation:**
  - Extensive testing on staging
  - Dry-run migrations with validation
  - Rollback plan ready
  - Keep old data for 6 months
  - Database backups before each phase
- **Status:** ✅ Dry-run testing planned for Phase 2

### Risk 3: **Performance Degradation**
- **Likelihood:** Low
- **Impact:** Medium
- **Mitigation:**
  - Proper indexing on work_type, status, dates
  - Caching for tree queries
  - Denormalized fields (e.g., root_project_id)
  - Database query monitoring
  - Load testing before production
- **Status:** Indexes defined in model

### Risk 4: **Complex Form Validation**
- **Likelihood:** Medium
- **Impact:** Medium
- **Mitigation:**
  - Type-specific form classes
  - JavaScript validation
  - Clear error messages
  - User training
- **Status:** Planned for Phase 1

### Risk 5: **Backward Compatibility Breaking**
- **Likelihood:** Medium
- **Impact:** High
- **Mitigation:**
  - Dual-write during transition
  - Proxy models for old interfaces
  - Comprehensive test coverage
  - Gradual deprecation (not immediate removal)
- **Status:** Proxy models planned for Phase 4

---

## 8. Decision Framework

### 8.1 Decision History

**Decision Date:** 2025-10-05
**Decision:** ✅ **APPROVED - FULL IMPLEMENTATION**

**Decision Makers:**
- Technical Lead: [Approved]
- Product Owner: [Approved]
- Stakeholder: [Approved]

**Rationale:**
1. ✅ Need for complex work hierarchies confirmed
2. ✅ Development resources allocated (6-8 weeks)
3. ✅ Unified work management is strategic priority
4. ✅ Technical feasibility validated
5. ✅ Risk mitigation strategies acceptable

### 8.2 Alternative Options Considered

**Option A: Add Hierarchy to Existing Models**
```python
# Add to StaffTask
parent_task = TreeForeignKey('self', null=True, ...)
work_type = models.CharField(choices=[('task', 'Task'), ('subtask', 'Subtask')])
```
- **Status:** REJECTED (doesn't address core issues)

**Option B: Enhanced Integration (Keep Separate Models)**
```python
# Just improve the linking between existing models
# Add better queries, unified views, but keep 3 models
```
- **Status:** REJECTED (maintains technical debt)

**Option C: Do Nothing**
- **Status:** REJECTED (doesn't meet strategic goals)

---

## 9. Implementation Estimates

### 9.1 Development Effort

| Phase | Tasks | Complexity | Estimated Duration | Status |
|-------|-------|------------|-------------------|--------|
| Phase 1: Model Creation | Model, migrations, admin | HIGH | 2-3 weeks | 🔄 IN PROGRESS |
| Phase 2: Data Migration | Scripts, validation, testing | HIGH | 1 week | ⏳ PENDING |
| Phase 3: UI Refactoring | Forms, views, templates | MEDIUM | 2-3 weeks | ⏳ PENDING |
| Phase 4: Switchover | Query updates, cleanup | MEDIUM | 1 week | ⏳ PENDING |
| Phase 5: Enhancement | Advanced features | LOW | Ongoing | ⏳ PENDING |
| **TOTAL** | | | **6-8 weeks** | |

### 9.2 Testing Requirements

- ✅ **Unit Tests:** Model methods, validation, tree operations
- ✅ **Integration Tests:** Migration scripts, dual-write
- ✅ **UI Tests:** Forms, hierarchy display
- ✅ **Performance Tests:** Tree queries, large datasets
- ✅ **User Acceptance Testing:** Real workflows

**Test Coverage Goal:** 95%+ for WorkItem model

---

## 10. Conclusion & Next Steps

### ✅ **DECISION: APPROVED - IMPLEMENTATION IN PROGRESS**

**Current Status:** Phase 1 - Model Creation (Week 1)

**Completed (Phase 1 - Week 1, Day 1):**
- [x] Research and evaluation
- [x] Architecture design
- [x] Stakeholder approval obtained
- [x] django-mptt installed (`pip install django-mptt>=0.16.0`)
- [x] Added 'mptt' to INSTALLED_APPS
- [x] WorkItem model created (`src/common/work_item_model.py`)
- [x] WorkItem imported into common.models
- [x] UNIFIED_WORK_HIERARCHY_EVALUATION.md completed

**In Progress:**
- [ ] Create initial migration for WorkItem (fixing MPTT field references)

**Next Immediate Steps:**
1. [ ] Create initial migration for WorkItem
2. [ ] Create admin interface with MPTTModelAdmin
3. [ ] Create unified WorkItemForm with dynamic fields
4. [ ] Test model in Django shell
5. [ ] Begin Phase 2 planning (migration commands)

### Implementation Timeline

```
Week 1-2:  Phase 1 - Model Creation & Setup (CURRENT)
Week 3:    Phase 2 - Data Migration
Week 4-6:  Phase 3 - UI Refactoring
Week 7:    Phase 4 - Switchover & Cleanup
Week 8+:   Phase 5 - Enhancements (ongoing)
```

**Target Go-Live:** 6-8 weeks from start (Week 1 began 2025-10-05)

---

## Appendix A: Technical References

### Research Sources
1. **Django MPTT Documentation:** https://django-mptt.readthedocs.io/
2. **Django Polymorphic Tree:** https://github.com/django-polymorphic/django-polymorphic-tree
3. **WBS Best Practices:** Asana, Atlassian, ProjectManager.com (2024)
4. **Task Management Schemas:** Stack Overflow, Medium (Database Design Patterns)

### Related Documentation
- **[WORK_ITEM_IMPLEMENTATION_EXAMPLES.md](./WORK_ITEM_IMPLEMENTATION_EXAMPLES.md)** - Code examples
- **[QUICK_DECISION_GUIDE.md](./QUICK_DECISION_GUIDE.md)** - Executive summary
- **[CALENDAR_INTEGRATION_PLAN.md](./CALENDAR_INTEGRATION_PLAN.md)** - Calendar integration details
- **[README.md](./README.md)** - Documentation index

---

**Document Status:** ✅ COMPLETE - APPROVED FOR IMPLEMENTATION
**Last Updated:** 2025-10-05
**Next Review:** After Phase 1 completion
**Owner:** Technical Architecture Team
**Implementation Lead:** [In Progress]
