# Views Migration Status - Visual Overview

```
                VIEWS MIGRATION TO WORKITEM
                ============================

┌─────────────────────────────────────────────────────────────────────┐
│                         MIGRATION PROGRESS                          │
│                                                                     │
│  ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  15% │
│                                                                     │
│  Fully Migrated: 1 file  |  Partial: 2 files  |  Not Done: 3 files│
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      LEGACY MODEL USAGE MAP                         │
└─────────────────────────────────────────────────────────────────────┘

  FILE: src/common/views.py                           STATUS: ❌ CRITICAL
  ├─ StaffTask: ███████ (6 refs)
  ├─ Event:     █████████████ (13 refs)
  └─ Total:     ███████████████████ (19 refs)
     Functions: home_view, coordination_dashboard, oobc_calendar,
                oobc_calendar_api, get_user_metrics

  FILE: src/coordination/views.py                     STATUS: ⚠️ PARTIAL  
  ├─ StaffTask: ░ (0 refs)
  ├─ Event:     ██████████████████████████████ (30+ refs)
  └─ Total:     ██████████████████████████████ (30+ refs)
     Functions: create_recurring_event, edit_event_instance,
                coordination_events, event_quick_update_htmx,
                delete_event, attendance tracking (4 functions)

  FILE: src/project_central/views.py                  STATUS: ⚠️ PARTIAL
  ├─ StaffTask:      ░ (0 refs)
  ├─ Event:          ░ (1 ref)
  ├─ ProjectWorkflow: ███████████████ (15+ refs)
  └─ Total:          ████████████████ (16+ refs)
     Has WorkItem integration (5 queries)
     7 deprecated functions still active

  FILE: src/mana/views.py                             STATUS: ❌ HIGH
  ├─ StaffTask: ███ (3 refs)
  ├─ Event:     ██ (2 refs)
  └─ Total:     █████ (5 refs)
     Functions: assessment_detail, assessment_tasks_board

  FILE: src/project_central/views_enhanced_dashboard.py  STATUS: 🟢 LOW
  ├─ ProjectWorkflow: █ (1 ref)
  └─ Total:           █ (1 ref)
     Quick fix needed

┌─────────────────────────────────────────────────────────────────────┐
│                      WORKITEM ADOPTION STATUS                       │
└─────────────────────────────────────────────────────────────────────┘

  ✅ FULLY MIGRATED
  └─ src/common/views/work_items.py
     └─ 100% WorkItem-based CRUD operations

  ⚠️ PARTIAL MIGRATION
  ├─ src/common/views/management.py
  │  └─ Has WorkItem imports + 3 deprecated stubs
  └─ src/project_central/views.py
     └─ 5 WorkItem queries + 15+ ProjectWorkflow refs (mixed)

  ❌ NOT MIGRATED
  ├─ src/common/views.py (19 refs)
  ├─ src/coordination/views.py (30+ refs)
  └─ src/mana/views.py (5 refs)

┌─────────────────────────────────────────────────────────────────────┐
│                     MIGRATION PRIORITY MATRIX                       │
└─────────────────────────────────────────────────────────────────────┘

  🔴 CRITICAL (Do First)
  ┌────────────────────────────────────────────────────────────────┐
  │ 1. src/common/views.py (2277 lines)                           │
  │    • 19 legacy references                                      │
  │    • Core system: Dashboard, Calendar, Metrics                 │
  │    • Affects entire OBCMS                                      │
  │    • Functions: 6 major views                                  │
  └────────────────────────────────────────────────────────────────┘

  🔴 HIGH PRIORITY
  ┌────────────────────────────────────────────────────────────────┐
  │ 2. src/mana/views.py                                          │
  │    • 5 legacy references                                       │
  │    • Assessment functionality                                  │
  │    • Functions: 2 major views                                  │
  └────────────────────────────────────────────────────────────────┘

  🟡 MEDIUM-HIGH
  ┌────────────────────────────────────────────────────────────────┐
  │ 3. src/coordination/views.py                                  │
  │    • 30+ Event references                                      │
  │    • Event forms, attendance tracking                          │
  │    • Functions: 9+ event-related views                         │
  └────────────────────────────────────────────────────────────────┘

  🟡 MEDIUM
  ┌────────────────────────────────────────────────────────────────┐
  │ 4. src/project_central/views.py                               │
  │    • 16+ ProjectWorkflow references                            │
  │    • Already has WorkItem integration started                  │
  │    • 7 deprecated functions to remove                          │
  └────────────────────────────────────────────────────────────────┘

  🟢 LOW
  ┌────────────────────────────────────────────────────────────────┐
  │ 5. src/project_central/views_enhanced_dashboard.py           │
  │    • 1 ProjectWorkflow reference                               │
  │    • Simple query replacement                                  │
  └────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        DEPRECATED VIEWS                             │
└─────────────────────────────────────────────────────────────────────┘

  📂 src/common/views/management.py
  ├─ staff_task_create() (Line 1062)
  ├─ staff_task_modal_create() (Line 1104)
  └─ staff_task_board() (Line 1301)

  📂 src/project_central/views.py
  ├─ create_workflow_from_ppa() (Line 594)
  ├─ project_workflow_detail() (Line 648)
  ├─ project_list_view() (Line 741)
  ├─ create_project_workflow() (Line 759)
  ├─ edit_project_workflow() (Line 769)
  ├─ advance_project_stage() (Line 807)
  └─ generate_workflow_tasks() (Line 1580)

  ⚠️ WARNING: These functions still contain ACTIVE CODE
              despite deprecation markers

┌─────────────────────────────────────────────────────────────────────┐
│                     MIGRATION ROADMAP                               │
└─────────────────────────────────────────────────────────────────────┘

  PHASE 1: CORE SYSTEM ⏱️ Priority: CRITICAL
  ────────────────────────────────────────────────────────
  Target Files:
    • src/common/views.py (19 refs)
    • src/mana/views.py (5 refs)
  
  Tasks:
    ✓ Replace StaffTask → WorkItem(work_type='task')
    ✓ Replace Event → WorkItem(work_type='activity')
    ✓ Update calendar API serialization
    ✓ Migrate dashboard metrics
    ✓ Update assessment views
  
  Impact: Dashboard, Calendar, Metrics, Assessments
  Estimated Lines: 300+ lines to modify

  PHASE 2: DOMAIN MODULES ⏱️ Priority: HIGH
  ────────────────────────────────────────────────────────
  Target Files:
    • src/coordination/views.py (30+ refs)
    • src/project_central/views.py (complete migration)
  
  Tasks:
    ✓ Replace EventForm → WorkItemForm
    ✓ Migrate event attendance to WorkItem
    ✓ Update recurring event logic
    ✓ Remove ProjectWorkflow queries
    ✓ Delete 7 deprecated functions
  
  Impact: Coordination, Project Tracking
  Estimated Lines: 500+ lines to modify

  PHASE 3: CLEANUP ⏱️ Priority: MEDIUM
  ────────────────────────────────────────────────────────
  Target: All deprecated code
  
  Tasks:
    ✓ Remove 10 deprecated functions
    ✓ Clean up legacy imports
    ✓ Update URL routing
    ✓ Remove @deprecated decorators
    ✓ Update tests
  
  Impact: Code quality, maintainability
  Estimated Lines: 200+ lines removed

┌─────────────────────────────────────────────────────────────────────┐
│                          KEY STATISTICS                             │
└─────────────────────────────────────────────────────────────────────┘

  Total View Files Scanned:          32
  Files with Legacy References:       5
  Files Using WorkItem:               3
  
  Legacy References by Model:
    • StaffTask:        9 locations
    • Event:           35+ locations
    • ProjectWorkflow: 15+ locations
    • TOTAL:           59+ references
  
  Deprecated Functions:              10
  
  Migration Status:
    • Fully Migrated:   5% (1 file)
    • Partial:         30% (2 files)
    • Not Migrated:    65% (3 files)
  
  Code Volume:
    • Lines to modify: ~1000+
    • Lines to delete:  ~200+
    • Functions affected: 25+

┌─────────────────────────────────────────────────────────────────────┐
│                       IMMEDIATE ACTIONS                             │
└─────────────────────────────────────────────────────────────────────┘

  1️⃣ START HERE: src/common/views.py
     Line 1952: Migrate StaffTask queries
     Line 2086: Migrate calendar API
     Line 115:  Migrate Event queries
     Impact: ENTIRE SYSTEM

  2️⃣ THEN: src/mana/views.py
     Line 411: Migrate assessment detail
     Line 549: Migrate assessment tasks board
     Impact: MANA MODULE

  3️⃣ NEXT: src/coordination/views.py
     Line 516: Replace EventForm
     Line 691: Migrate coordination events
     Impact: COORDINATION MODULE

  4️⃣ FINISH: Complete project_central migration
     Remove 7 deprecated functions
     Clean up legacy imports
     Impact: PROJECT CENTRAL

┌─────────────────────────────────────────────────────────────────────┐
│                         QUICK WINS                                  │
└─────────────────────────────────────────────────────────────────────┘

  🎯 Easy Fixes (< 30 min each):
  1. src/project_central/views_enhanced_dashboard.py (1 line)
  2. Delete deprecated stubs in management.py (3 functions)
  3. Remove @deprecated decorators (7 functions)

  🎯 Medium Effort (2-4 hours):
  1. src/mana/views.py (5 references, 2 functions)
  2. Complete WorkItem migration in project_central/views.py

  🎯 Major Effort (1-2 days):
  1. src/common/views.py (19 references, 6 functions)
  2. src/coordination/views.py (30+ references, 9+ functions)

═══════════════════════════════════════════════════════════════════════

                      🎯 NEXT STEP: BEGIN PHASE 1
                   Migrate src/common/views.py first

═══════════════════════════════════════════════════════════════════════

Report Generated: October 5, 2025
Status: COMPREHENSIVE AUDIT COMPLETE
Full Details: VIEWS_AUDIT_COMPREHENSIVE.md
Quick Reference: VIEWS_AUDIT_SUMMARY.md
