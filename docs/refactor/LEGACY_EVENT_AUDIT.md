# Legacy Event Model Audit & Deprecation Analysis

**Date:** 2025-10-05
**Status:** AUDIT COMPLETE - AWAITING DECISION
**Context:** WorkItem system (work_type='activity') is intended to replace Event model

---

## Executive Summary

The coordination app contains an extensive **Event model** (3660 lines total in models.py) with rich features for managing coordination meetings, consultations, workshops, and other activities. The new **WorkItem model** (work_type='activity') was designed to replace this, but **critical feature gaps exist** that prevent full migration.

**Recommendation:** **DO NOT DEPRECATE Event model yet.** Complete feature parity first.

---

## 1. Inventory: Event-Related Files

### A. Models (src/coordination/models.py)

**Event Model (Lines 1583-2373)**
- **Size:** ~790 lines of model definition
- **Purpose:** Comprehensive event/activity management
- **Fields:** 50+ fields covering scheduling, logistics, participants, documentation, feedback

**Related Models:**
- **EventParticipant (Lines 2374-2540):** Participant tracking with roles, RSVP, invitations
- **EventDocument (Lines 2855-2920):** Event-related documents (agenda, minutes, photos, recordings)
- **EventAttendance (Lines 3614-3680):** QR code check-in, attendance tracking

**Total Lines:** ~1,150 lines of Event-specific models

### B. Views (src/coordination/views.py)

**Event Views Identified:**
1. `event_create` (Line 515) - Create single event
2. `event_create_recurring` (Line 719) - Create recurring event series
3. `event_edit_instance` (Line 784) - Edit single recurrence instance
4. `coordination_event_modal` (Line 905) - Modal detail view
5. `coordination_event_delete` (Line 964) - Delete event
6. `event_attendance_tracker` (Line 1203) - Attendance tracking UI
7. `event_attendance_count` (Line 1221) - Real-time attendance count
8. `event_participant_list` (Line 1280) - Participant list view
9. `event_check_in` (Line 1338) - QR code check-in

**Helper Functions:**
- `_combine_event_datetime` (Line 49) - Datetime combination logic
- `_serialize_coordination_event` (Line 56) - Event serialization

**Total:** 9 views + 2 helper functions (~400-500 lines)

### C. Forms (src/coordination/forms.py)

**EventForm (Lines 252-360)**
- **Size:** ~108 lines
- **Fields:** 40+ form fields
- **Features:**
  - Auto-task generation checkbox
  - Project activity integration
  - Virtual meeting fields
  - Participant management
  - Budget tracking
  - Feedback/evaluation

**Total:** ~108 lines

### D. Templates (src/templates/coordination/)

**Event Templates:**
1. `event_form.html` - Comprehensive event creation form (305 lines)
   - 6 major sections (Basic Info, Project Activity, Schedule, Team, Content, Follow-up)
   - Project activity integration with conditional visibility
   - Rich form with venue, virtual meeting, participant tracking

2. `event_recurring_form.html` - Recurring event creation
3. `event_edit_instance.html` - Edit single recurrence instance
4. `event_attendance_tracker.html` - Attendance tracking UI
5. `coordination_events.html` - Event list/calendar view

**Total:** 5 templates (~1000+ lines)

### E. URL Patterns (src/common/urls.py)

**Event Endpoints (Lines 237-278):**
```python
coordination/events/add/                        # Create event
coordination/events/recurring/add/              # Create recurring series
coordination/events/<uuid>/edit-instance/       # Edit instance
coordination/events/<uuid>/modal/               # Modal view
coordination/events/<uuid>/delete/              # Delete
coordination/events/<uuid>/attendance/          # Attendance tracker
coordination/events/<uuid>/attendance/count/    # Attendance count API
coordination/events/<uuid>/attendance/participants/  # Participant list
coordination/events/<uuid>/check-in/            # QR check-in
coordination/events/                            # List view
```

**Additional Event URLs (Lines 464-481):**
```python
coordination/events/<uuid>/qr-code/             # Generate QR code
coordination/events/<uuid>/qr-scan/             # Scan QR code
coordination/events/<uuid>/attendance-report/   # Attendance report
```

**Total:** 13 URL patterns

### F. Signals (src/coordination/signals.py)

**Event Signal Handlers:**
1. `handle_event_creation` (Line 18) - Post-save event creation logging
2. `handle_event_update` (Line 51) - Pre-save event update detection
   - Status changes
   - Project linkage changes
   - Date rescheduling

**Project Workflow Integration:**
3. `handle_workflow_stage_change` (Line 130) - Auto-creates Event for milestone reviews

**Total:** 3 signal handlers (~180 lines)

### G. Tests

**Event Test Coverage:**
- `src/coordination/tests/test_views.py::test_create_event` (Line 562)
- `src/coordination/tests/test_quarterly_reports.py::test_report_creation_links_event_and_mao` (Line 57)

**Total:** 2+ test functions

---

## 2. Feature Completeness Analysis: WorkItem Activity vs Event

### ✅ **FEATURE PARITY ACHIEVED**

| Feature | Event Model | WorkItem Activity | Status |
|---------|-------------|-------------------|--------|
| **Basic Info** | ✅ | ✅ | **PARITY** |
| Title | `title` (CharField) | `title` (CharField) | ✅ |
| Description | `description` (TextField) | `description` (TextField) | ✅ |
| Status | 9 statuses | 6 statuses | ⚠️ Different but sufficient |
| Priority | 4 levels | 5 levels | ✅ |
| **Scheduling** | ✅ | ✅ | **PARITY** |
| Start date | `start_date` | `start_date` | ✅ |
| End date | `end_date` | `due_date` | ✅ (renamed) |
| Start time | `start_time` | `start_time` | ✅ |
| End time | `end_time` | `end_time` | ✅ |
| Duration | `duration_hours` | Calculated | ⚠️ Can be calculated |
| **Calendar** | ✅ | ✅ | **PARITY** |
| Calendar visibility | Implicit (always visible) | `is_calendar_visible` | ✅ Better |
| Calendar color | - | `calendar_color` | ✅ Better |
| Recurrence | `is_recurring`, `recurrence_pattern` | `is_recurring`, `recurrence_pattern` | ✅ |
| **Assignment** | ✅ | ✅ | **PARITY** |
| Organizer | `organizer` (ForeignKey) | `created_by` (ForeignKey) | ✅ |
| Assignees | `co_organizers`, `facilitators` | `assignees` (ManyToMany) | ✅ Better |
| Teams | - | `teams` (ManyToMany) | ✅ Better |
| **Progress** | ✅ | ✅ | **PARITY** |
| Status tracking | `status` field | `status` + `progress` % | ✅ Better |
| Completion | `completed_at` implied | `completed_at` explicit | ✅ |

### ⚠️ **PARTIAL PARITY (Stored in JSON)**

| Feature | Event Model | WorkItem Activity | Gap Analysis |
|---------|-------------|-------------------|--------------|
| **Event Type** | ✅ | ⚠️ | **Stored in `activity_data` JSON** |
| Event type | 15 choices (meeting, consultation, workshop, etc.) | `activity_data.event_type` | ✅ Property exists |
| **Location** | ✅ | ⚠️ | **Can be stored in `activity_data` JSON** |
| Venue | `venue` (CharField) | `activity_data.venue` | ⚠️ Not implemented yet |
| Address | `address` (TextField) | `activity_data.address` | ⚠️ Not implemented yet |
| Coordinates | `coordinates` (JSONField) | `activity_data.coordinates` | ⚠️ Not implemented yet |
| **Virtual Meeting** | ✅ | ⚠️ | **Can be stored in `activity_data` JSON** |
| Is virtual | `is_virtual` (BooleanField) | `activity_data.is_virtual` | ⚠️ Not implemented yet |
| Platform | `virtual_platform` | `activity_data.virtual_platform` | ⚠️ Not implemented yet |
| Link | `virtual_link` (URLField) | `activity_data.virtual_link` | ⚠️ Not implemented yet |
| Meeting ID | `virtual_meeting_id` | `activity_data.virtual_meeting_id` | ⚠️ Not implemented yet |
| Passcode | `virtual_passcode` | `activity_data.virtual_passcode` | ⚠️ Not implemented yet |

### ❌ **MISSING FEATURES (Critical Gaps)**

| Feature Category | Event Model | WorkItem Activity | Migration Path |
|------------------|-------------|-------------------|----------------|
| **Participants** | ✅ | ❌ | **BLOCKING** |
| Expected participants | `expected_participants` (int) | `activity_data.expected_participants` | ⚠️ JSON only |
| Actual participants | `actual_participants` (int) | `activity_data.actual_participants` | ⚠️ JSON only |
| Target audience | `target_audience` (TextField) | `activity_data.target_audience` | ⚠️ JSON only |
| **Participant Management** | ✅ | ❌ | **CRITICAL GAP** |
| EventParticipant model | 165+ lines (roles, RSVP, invitations) | **NONE** | ❌ No replacement |
| Participant roles | 8 role choices | **NONE** | ❌ Missing |
| RSVP tracking | 4 statuses (going/maybe/declined) | **NONE** | ❌ Missing |
| Invitation status | 5 statuses (sent/delivered/opened) | **NONE** | ❌ Missing |
| **Attendance Tracking** | ✅ | ❌ | **CRITICAL GAP** |
| EventAttendance model | QR code check-in | **NONE** | ❌ No replacement |
| Check-in methods | manual/qr_code/nfc | **NONE** | ❌ Missing |
| Check-in timestamp | `checked_in_at` | **NONE** | ❌ Missing |
| Check-out timestamp | `checked_out_at` | **NONE** | ❌ Missing |
| **Content & Documentation** | ✅ | ⚠️ | **Partial** |
| Agenda | `agenda` (TextField) | `activity_data.agenda` | ⚠️ JSON only |
| Materials needed | `materials_needed` (TextField) | `activity_data.materials_needed` | ⚠️ JSON only |
| Minutes | `minutes` (TextField) | `activity_data.minutes` | ⚠️ JSON only |
| Outcomes | `outcomes` (TextField) | `activity_data.outcomes` | ⚠️ JSON only |
| Decisions made | `decisions_made` (TextField) | `activity_data.decisions_made` | ⚠️ JSON only |
| Key discussions | `key_discussions` (TextField) | `activity_data.key_discussions` | ⚠️ JSON only |
| **Document Management** | ✅ | ❌ | **CRITICAL GAP** |
| EventDocument model | 11 document types (agenda, minutes, photos, recordings) | **NONE** | ❌ No replacement |
| Document uploads | File storage | **NONE** | ❌ Missing |
| **Budget** | ✅ | ⚠️ | **Can use project_data** |
| Budget allocated | `budget_allocated` (Decimal) | `project_data.budget` | ⚠️ Different field |
| Actual cost | `actual_cost` (Decimal) | `activity_data.actual_cost` | ⚠️ JSON only |
| **Feedback & Evaluation** | ✅ | ⚠️ | **JSON only** |
| Feedback summary | `feedback_summary` (TextField) | `activity_data.feedback_summary` | ⚠️ JSON only |
| Satisfaction rating | 1-5 stars | `activity_data.satisfaction_rating` | ⚠️ JSON only |
| Lessons learned | `lessons_learned` (TextField) | `activity_data.lessons_learned` | ⚠️ JSON only |
| **Follow-up** | ✅ | ⚠️ | **JSON only** |
| Follow-up required | `follow_up_required` (bool) | `activity_data.follow_up_required` | ⚠️ JSON only |
| Follow-up date | `follow_up_date` (DateField) | `activity_data.follow_up_date` | ⚠️ JSON only |
| Follow-up notes | `follow_up_notes` (TextField) | `activity_data.follow_up_notes` | ⚠️ JSON only |
| **Quarterly Coordination** | ✅ | ❌ | **CRITICAL GAP** |
| Is quarterly coordination | `is_quarterly_coordination` (bool) | **NONE** | ❌ Missing |
| Quarter | Q1/Q2/Q3/Q4 choices | **NONE** | ❌ Missing |
| Fiscal year | `fiscal_year` (int) | **NONE** | ❌ Missing |
| Pre-meeting reports due | `pre_meeting_reports_due` (DateField) | **NONE** | ❌ Missing |
| **Project Activity** | ✅ | ⚠️ | **Can use related_object** |
| Related project | `related_project` (ForeignKey) | `related_object` (GenericForeignKey) | ⚠️ Less specific |
| Is project activity | `is_project_activity` (bool) | `activity_data.is_project_activity` | ⚠️ JSON only |
| Activity type | 6 choices (kickoff, milestone review, etc.) | `activity_data.project_activity_type` | ⚠️ JSON only |

---

## 3. Calendar Integration Analysis

### Current State

**Event Calendar Integration:**
- Events included in `oobc_calendar_feed_json` (Line 562, src/common/views/management.py)
- Events included in `oobc_calendar_feed_ics` (Line 611, src/common/views/management.py)
- Events appear in unified calendar via `build_calendar_payload()`

**WorkItem Calendar Integration:**
- WorkItems have dedicated `work_items_calendar_feed` (src/common/views/calendar.py)
- WorkItems have `work_item_calendar_feed` (src/common/views/work_items.py)
- WorkItems include Activities (work_type='activity')

### Migration Impact

**If Event is deprecated:**
1. ✅ WorkItem Activities can replace Event in calendar feed
2. ⚠️ Need to migrate `build_calendar_payload()` to use WorkItem Activities
3. ⚠️ Calendar templates need update to recognize Activity type
4. ❌ **BLOCKER:** Attendance tracking features will be lost (QR check-in, participant lists)

**URL Redirect Strategy:**
```python
# Old Event URLs
/coordination/events/<uuid>/modal/              → /oobc-management/work-items/<uuid>/modal/
/coordination/events/<uuid>/attendance/         → ??? (No WorkItem equivalent)
/coordination/events/<uuid>/check-in/           → ??? (No WorkItem equivalent)
```

---

## 4. Usage Frequency Analysis

**Event Usage Indicators:**

1. **Template References:**
   - `src/templates/common/dashboard.html` (Line 429): Shows event count
   - `src/templates/common/navbar.html` (Lines 147, 448): Navigation links
   - `src/templates/common/partials/staff_task_modal.html` (Line 51): Linked event display
   - `src/templates/common/tasks/event_tasks.html` (Lines 13, 42): Event task management

2. **StaffTask Integration:**
   - StaffTask has `linked_event` ForeignKey to Event model
   - Event tasks view at `/oobc-management/staff/tasks/event/<uuid>/`
   - Event creation auto-generates tasks (via `_auto_generate_tasks` flag)

3. **Project Workflow Integration:**
   - Workflow stage changes auto-create Event instances (signals.py Line 153)
   - Milestone reviews automatically generate Events
   - Project activities link to Events

**Conclusion:** Event model is **HEAVILY INTEGRATED** throughout the system.

---

## 5. Gap Resolution Recommendations

### Option A: Complete Feature Parity (Recommended)

**Add to WorkItem Activity:**

1. **Participant Management (Critical)**
   - Create `WorkItemParticipant` model (similar to EventParticipant)
   - Fields: participant type, role, RSVP status, invitation status
   - Link to WorkItem via ForeignKey

2. **Attendance Tracking (Critical)**
   - Create `WorkItemAttendance` model (similar to EventAttendance)
   - QR code check-in functionality
   - Check-in/check-out timestamps
   - Attendance reports

3. **Document Management (Critical)**
   - Create `WorkItemDocument` model (similar to EventDocument)
   - Support for agendas, minutes, photos, recordings
   - File upload and storage

4. **Quarterly Coordination Support (Important)**
   - Add `activity_data` fields:
     - `is_quarterly_coordination`
     - `quarter` (Q1/Q2/Q3/Q4)
     - `fiscal_year`
     - `pre_meeting_reports_due`

5. **Activity-Specific Form (Important)**
   - Create `WorkItemActivityForm` with all Event features
   - Conditional field visibility (venue vs virtual)
   - Participant management UI
   - Document upload UI

6. **Enhanced activity_data Schema (Medium Priority)**
   - Standardize JSON schema for activity-specific fields
   - Add validation for required fields
   - Create helper properties for common fields

**Estimated Effort:** HIGH (New models, forms, views, templates)
**Timeline:** Should be planned carefully with testing

### Option B: Keep Event Permanently

**Reasoning:**
- Event model is **specialized** for coordination activities
- Participant/attendance tracking is **domain-specific** to events
- Document management is **event-specific** (agendas, minutes, recordings)
- Quarterly coordination is **unique** to OCM meetings
- WorkItem Activities are **different use case** (generic project activities)

**Recommendation:** Treat Event and WorkItem as **complementary**, not duplicative.

**Use Cases:**
- **Event model:** Coordination meetings, consultations, workshops with participants/attendance
- **WorkItem Activity:** Generic project activities, milestones, deliverables without participant tracking

**Benefits:**
- No migration risk
- Preserve specialized functionality
- Simpler than adding complexity to WorkItem
- Clear separation of concerns

---

## 6. Analysis Summary

### Files FULLY REPLACED by WorkItem Activity

**NONE**

Every Event-related file has unique features not yet in WorkItem:
- Participant management
- Attendance tracking
- Document uploads
- Quarterly coordination specifics

### Files with UNIQUE FEATURES (Not in WorkItem)

**ALL EVENT FILES:**
1. **Models:** EventParticipant, EventAttendance, EventDocument
2. **Views:** Attendance tracker, check-in, participant list
3. **Forms:** EventForm with participant/venue/virtual meeting fields
4. **Templates:** Attendance tracker, check-in UI, participant management
5. **Signals:** Event-specific automation

### Files STILL REQUIRED

**ALL EVENT FILES** are required until feature parity is achieved.

---

## 7. Deprecation Plan

### Phase 1: Analysis Complete ✅

- [x] Inventory all Event-related files
- [x] Compare Event vs WorkItem Activity features
- [x] Identify critical gaps
- [x] Assess calendar integration
- [x] Analyze usage patterns

### Phase 2: Feature Parity Implementation (NOT STARTED)

**Prerequisites:**
- [ ] Create `WorkItemParticipant` model
- [ ] Create `WorkItemAttendance` model
- [ ] Create `WorkItemDocument` model
- [ ] Add quarterly coordination fields to `activity_data`
- [ ] Create `WorkItemActivityForm` with full Event features
- [ ] Build participant management UI
- [ ] Build attendance tracking UI (QR check-in)
- [ ] Build document upload UI
- [ ] Migrate calendar feeds to use WorkItem Activities
- [ ] Update calendar templates
- [ ] Create URL redirects

**Estimated Lines of Code:** ~2000+ lines

### Phase 3: Data Migration (BLOCKED)

**Cannot start until Phase 2 is complete.**

Migration script requirements:
- Migrate Event → WorkItem (work_type='activity')
- Migrate EventParticipant → WorkItemParticipant
- Migrate EventAttendance → WorkItemAttendance
- Migrate EventDocument → WorkItemDocument
- Update related_object GenericForeignKey references
- Update StaffTask.linked_event references

### Phase 4: Deprecation (BLOCKED)

**Cannot start until Phase 3 is complete.**

1. Add deprecation warnings to Event model
2. Update documentation to recommend WorkItem Activity
3. Update admin interface to show deprecation notice
4. Set removal target date (e.g., 6 months)

### Phase 5: Removal (BLOCKED)

**Cannot start until Phase 4 grace period expires.**

1. Delete Event model
2. Delete EventParticipant model
3. Delete EventAttendance model
4. Delete EventDocument model
5. Delete Event views
6. Delete Event forms
7. Delete Event templates
8. Delete Event URLs
9. Delete Event signals
10. Update tests

---

## 8. Final Recommendation

### ⚠️ **DO NOT DEPRECATE EVENT MODEL**

**Reasoning:**

1. **Critical Feature Gaps:** WorkItem Activity lacks participant management, attendance tracking, document uploads, and quarterly coordination support.

2. **High Migration Risk:** Event is deeply integrated (StaffTask, ProjectWorkflow, calendar, dashboard). Migration requires touching 50+ files.

3. **Domain Specificity:** Event model is highly specialized for coordination activities. Adding all these features to WorkItem would create bloat.

4. **Complementary Use Cases:**
   - **Event:** Coordination meetings with participants, attendance, documents
   - **WorkItem Activity:** Generic project activities, milestones, deliverables

5. **User Impact:** Losing attendance tracking, participant management, and quarterly coordination would significantly harm OCM coordination workflow.

### Alternative Approach: **Keep Both Models**

**Event Model:** Specialized coordination activities with participants/attendance
**WorkItem Activity:** Generic project activities without participant tracking

**Benefits:**
- Zero migration risk
- Preserve specialized functionality
- Clear separation of concerns
- Simpler codebase (no feature bloat in WorkItem)

**Trade-offs:**
- Two models for similar concepts
- Need to maintain both codebases
- Slightly more complex calendar integration

---

## 9. Next Steps

**If proceeding with deprecation (NOT RECOMMENDED):**
1. Implement Phase 2 (Feature Parity) - estimated 2000+ lines of code
2. Create comprehensive migration script
3. Test thoroughly with production data backup
4. Plan rollback strategy

**If keeping Event model (RECOMMENDED):**
1. Document Event vs WorkItem Activity use cases clearly
2. Update CLAUDE.md to specify when to use each
3. Consider renaming WorkItem Activity to avoid confusion
4. Add cross-references in admin interface
5. Update developer documentation

---

## Appendix A: Event Field Inventory

**Event Model Fields (50+ total):**

**Identity & Type:**
- id (UUID)
- title (CharField)
- event_type (15 choices)
- description (TextField)
- objectives (TextField)

**Relationships:**
- community (ForeignKey)
- organizations (ManyToMany)
- related_engagement (ForeignKey)
- related_assessment (ForeignKey)
- related_project (ForeignKey)

**Status & Priority:**
- status (9 choices)
- priority (4 levels)

**Schedule:**
- start_date (DateField)
- end_date (DateField)
- start_time (TimeField)
- end_time (TimeField)
- duration_hours (DecimalField)

**Location:**
- venue (CharField)
- address (TextField)
- coordinates (JSONField)

**Virtual Meeting:**
- is_virtual (BooleanField)
- virtual_platform (CharField)
- virtual_link (URLField)
- virtual_meeting_id (CharField)
- virtual_passcode (CharField)

**Team:**
- organizer (ForeignKey)
- co_organizers (ManyToMany)
- facilitators (ManyToMany)

**Participants:**
- expected_participants (int)
- actual_participants (int)
- target_audience (TextField)

**Content:**
- agenda (TextField)
- materials_needed (TextField)
- minutes (TextField)
- outcomes (TextField)
- decisions_made (TextField)
- key_discussions (TextField)

**Budget:**
- budget_allocated (Decimal)
- actual_cost (Decimal)

**Feedback:**
- feedback_summary (TextField)
- satisfaction_rating (1-5 stars)
- lessons_learned (TextField)

**Follow-up:**
- follow_up_required (bool)
- follow_up_date (DateField)
- follow_up_notes (TextField)

**Recurrence:**
- is_recurring (bool)
- recurrence_pattern (ForeignKey)
- recurrence_parent (ForeignKey)
- is_recurrence_exception (bool)

**Quarterly Coordination:**
- is_quarterly_coordination (bool)
- quarter (Q1/Q2/Q3/Q4)
- fiscal_year (int)
- pre_meeting_reports_due (DateField)

**Project Activity:**
- is_project_activity (bool)
- project_activity_type (6 choices)

**Metadata:**
- created_by (ForeignKey)
- created_at (DateTime)
- updated_at (DateTime)

---

## Appendix B: Related Models

**EventParticipant Model:**
- event (ForeignKey)
- participant_type (6 choices)
- role (8 choices)
- user (ForeignKey, optional)
- name (CharField)
- email (EmailField)
- phone (CharField)
- organization (CharField)
- designation (CharField)
- rsvp_status (4 choices)
- invitation_status (5 choices)
- invitation_sent_at (DateTime)
- rsvp_received_at (DateTime)
- attended (bool)
- check_in_time (DateTime)
- check_out_time (DateTime)
- notes (TextField)

**EventDocument Model:**
- event (ForeignKey)
- document_type (11 choices)
- title (CharField)
- description (TextField)
- file (FileField)
- uploaded_by (ForeignKey)
- uploaded_at (DateTime)
- is_public (bool)
- notes (TextField)

**EventAttendance Model:**
- event (ForeignKey)
- participant (ForeignKey EventParticipant)
- checked_in_at (DateTime)
- check_in_method (3 choices: manual/qr_code/nfc)
- checked_out_at (DateTime)
- notes (TextField)

---

**END OF AUDIT**
