# Event vs WorkItem Activity: Decision Guide

**Status:** Active Guide
**Last Updated:** 2025-10-05
**Applies To:** OBCMS Coordination & Project Management Modules

---

## Overview

OBCMS offers two complementary systems for tracking activities:

1. **Event Model** (Coordination Module) - Full-featured coordination meetings with participant management
2. **WorkItem Activity** (Project Management Portal) - Simple project activities with task integration

Both systems are **fully supported** and serve different use cases. This guide helps you choose the right tool for your needs.

---

## Quick Decision Matrix

| Use Case | Recommended Tool | Why |
|----------|-----------------|-----|
| Quarterly Coordination Meeting | **Event** | Participant tracking, formal documentation, attendance management |
| Multi-stakeholder coordination meeting | **Event** | Organization management, participant roles, detailed outcomes |
| Partnership signing ceremony | **Event** | Multiple organizations, formal documentation, attendance required |
| Project kickoff meeting | **Event** | Participant tracking, formal agenda, multiple organizations |
| Simple project activity (e.g., "Submit report") | **WorkItem Activity** | Quick scheduling, task integration, no participant tracking needed |
| Internal team meeting (informal) | **WorkItem Activity** | Lightweight, fast to create, integrates with tasks |
| Deadline/milestone | **WorkItem Activity** | No participants needed, just a scheduled action |
| Community consultation | **Event** | Participant tracking, feedback collection, stakeholder engagement |

---

## Event Model (Coordination Module)

### When to Use Event

Use **Event** when you need:

- **Participant Management**: Track who's attending, their roles, and response status
- **Organization Coordination**: Multiple organizations, partnerships, or stakeholders
- **Formal Documentation**: Agendas, minutes, outcomes, decisions, action items
- **Attendance Tracking**: Know who attended, satisfaction ratings, feedback
- **Recurring Meetings**: Quarterly coordination meetings, regular stakeholder engagements
- **Virtual Meeting Support**: Platform links, meeting IDs, passcodes
- **Budget/Cost Tracking**: Budget allocated, actual costs, logistics expenses
- **Follow-up Actions**: Track action items assigned during meetings

### Event Features

✅ **Participant Management**
- Track participant names, organizations, roles
- Response status (Confirmed, Tentative, Declined, No Response)
- Satisfaction ratings and feedback

✅ **Organization Integration**
- Link to multiple organizations
- Partnership coordination
- Stakeholder engagement tracking

✅ **Comprehensive Documentation**
- Event objectives and description
- Detailed agenda
- Meeting minutes
- Outcomes and decisions made
- Key discussions
- Lessons learned

✅ **Logistics Management**
- Venue details and address
- Virtual meeting platform (Zoom, Teams, Meet)
- Virtual meeting links, IDs, passcodes
- Budget allocated and actual costs
- Materials needed
- Expected vs actual participants

✅ **Action Item Tracking**
- Action items assigned during event
- Assigned to specific people
- Due dates and priorities
- Status tracking (Pending, In Progress, Completed)
- Overdue indicators

✅ **Recurrence Support**
- Recurring meetings (weekly, monthly, quarterly)
- Parent-instance relationships
- Quarterly coordination meeting tracking
- Fiscal year and quarter designation

✅ **Project Integration** (Optional)
- Link events to projects
- Auto-generate preparation/follow-up tasks
- Activity type designation (Planning, Coordination, Review, etc.)

### Event Workflow Example

**Scenario: Quarterly MAO Coordination Meeting**

1. **Create Event**
   - Title: "Q1 FY2025 MAO Coordination Meeting"
   - Event Type: Quarterly Coordination Meeting
   - Mark as "Quarterly Coordination"
   - Set Quarter: Q1, Fiscal Year: 2025

2. **Schedule & Venue**
   - Start Date: March 15, 2025
   - Duration: 3 hours
   - Venue: OOBC Main Conference Hall
   - Virtual Platform: Zoom (hybrid meeting)

3. **Participant Management**
   - Add MAO focal persons
   - Add OOBC staff
   - Add partner organization representatives
   - Track response status

4. **Documentation**
   - Upload pre-meeting reports
   - Create detailed agenda
   - Capture meeting minutes
   - Document decisions made
   - Record key discussions

5. **Action Items**
   - Assign follow-up actions
   - Set due dates
   - Track completion

6. **Outcomes**
   - Document meeting outcomes
   - Collect participant feedback
   - Record satisfaction ratings
   - Capture lessons learned

---

## WorkItem Activity (Project Management Portal)

### When to Use WorkItem Activity

Use **WorkItem Activity** when you need:

- **Simple Scheduling**: Just a date/time for an activity, no complex logistics
- **Task Integration**: Activity is part of a project workflow with tasks
- **No Participant Tracking**: You don't need to track who's attending
- **Quick Creation**: Fast to create, minimal fields
- **Lightweight Documentation**: Brief description is sufficient
- **Project Milestones**: Deadlines, deliverables, checkpoints
- **Internal Activities**: Team activities without external stakeholders

### WorkItem Activity Features

✅ **Simple Scheduling**
- Start date and time
- Due date
- Duration (optional)
- Status (Draft, Scheduled, In Progress, Completed)

✅ **Task Integration**
- Create linked tasks automatically
- Quick action to add tasks
- Task board integration
- Task status tracking

✅ **Project Integration**
- Linked to project workflow
- Part of project timeline
- Activity type (Planning, Implementation, Review, etc.)
- Project status updates

✅ **Lightweight Documentation**
- Title and description
- Notes field
- Deliverable tracking
- File attachments

✅ **Team Assignment**
- Assign to staff members
- Multiple assignees supported
- Priority levels

### WorkItem Activity Workflow Example

**Scenario: Submit Monthly Community Report**

1. **Create WorkItem Activity**
   - Title: "Submit March 2025 Community Report"
   - Type: Activity
   - Related Project: "Community Outreach Q1 2025"
   - Activity Type: Reporting

2. **Schedule**
   - Start Date: March 25, 2025
   - Due Date: March 31, 2025
   - Status: Scheduled

3. **Quick Tasks** (Auto-generated)
   - "Collect community data" (Due: March 27)
   - "Draft report" (Due: March 29)
   - "Review and finalize" (Due: March 30)
   - "Submit to supervisor" (Due: March 31)

4. **Track Progress**
   - Update task statuses on task board
   - Mark activity complete when all tasks done
   - Upload final report as attachment

---

## Feature Comparison Table

| Feature | Event | WorkItem Activity |
|---------|-------|-------------------|
| **Participant Tracking** | ✅ Full participant management | ❌ No participant tracking |
| **Organization Management** | ✅ Multiple organizations, partnerships | ❌ Not applicable |
| **Response Status** | ✅ Confirmed, Tentative, Declined, No Response | ❌ Not applicable |
| **Satisfaction Ratings** | ✅ Participant feedback & ratings | ❌ Not applicable |
| **Virtual Meeting Details** | ✅ Platform, links, IDs, passcodes | ❌ Not applicable |
| **Budget Tracking** | ✅ Budget allocated, actual costs | ❌ Not applicable |
| **Logistics Management** | ✅ Venue, address, materials needed | ❌ Not applicable |
| **Meeting Minutes** | ✅ Comprehensive minutes, decisions, discussions | ❌ Simple notes field |
| **Action Items** | ✅ Dedicated action item model with tracking | ❌ Use task system instead |
| **Recurring Meetings** | ✅ Full recurrence support | ❌ Not supported |
| **Quarterly Coordination** | ✅ Fiscal year, quarter designation | ❌ Not applicable |
| **Task Integration** | ✅ Optional project activity integration | ✅ Native task integration |
| **Quick Creation** | ⚠️ Many fields, more detailed | ✅ Fast, minimal fields |
| **Project Timeline** | ⚠️ Optional project link | ✅ Always part of project |
| **Calendar Display** | ✅ Full calendar integration | ✅ Basic calendar integration |
| **Document Attachments** | ✅ Event documents with types | ✅ File attachments |
| **Community Linking** | ✅ Link to OBC community | ✅ Indirect via project |
| **Stakeholder Engagement** | ✅ Link to stakeholder engagements | ❌ Not applicable |

---

## Migration Considerations

### Can I Switch Between Systems?

**Event → WorkItem Activity**
- ❌ **Not recommended** - You'll lose participant tracking, organization links, and detailed documentation
- ✅ **Alternative**: Keep Event, add WorkItem Activities for follow-up tasks

**WorkItem Activity → Event**
- ✅ **Possible** - If you discover you need participant tracking, create a new Event and link it
- ✅ **Use Case**: Started as simple activity, evolved into formal meeting

### Best Practice: Use Both

For complex coordination workflows:

1. **Create Event** for the main coordination meeting
   - Participant tracking
   - Formal documentation
   - Outcomes and decisions

2. **Create WorkItem Activities** for preparation/follow-up
   - "Prepare agenda" (before meeting)
   - "Collect pre-meeting reports" (before meeting)
   - "Distribute meeting minutes" (after meeting)
   - "Implement action items" (after meeting)

3. **Link Event to Project** (Optional)
   - Check "This is a project-specific activity"
   - Select related project
   - Auto-generate preparation/follow-up tasks

---

## System Architecture Notes

### Event Model Location
- **App**: `coordination` (Django app)
- **Model**: `Event`
- **Admin**: `/admin/coordination/event/`
- **Templates**: `src/templates/coordination/`
- **URLs**: `common:coordination_event_*`

### WorkItem Model Location
- **App**: `common` (Django app)
- **Model**: `WorkItem`
- **Admin**: `/admin/common/workitem/`
- **Templates**: `src/templates/common/work_items/`
- **URLs**: `common:work_item_*`

### Data Model Relationships

**Event can link to:**
- Organizations (many-to-many)
- OBC Communities (many-to-many)
- Stakeholder Engagements (foreign key)
- MANA Assessments (foreign key)
- Projects (foreign key, optional)
- Parent Events (foreign key, for recurrence)

**WorkItem Activity links to:**
- Projects (foreign key, required)
- Assigned Staff (many-to-many)
- Related Tasks (reverse relationship)

---

## Frequently Asked Questions

### Q: Should I use Event for all meetings?

**A:** No. Use Event for **coordination meetings** where you need to track participants, organizations, and formal outcomes. For quick internal team check-ins or informal discussions, use WorkItem Activity or don't track them at all.

### Q: Can I track tasks with Events?

**A:** Yes, but indirectly:
1. Enable "This is a project-specific activity" on the Event
2. Check "Auto-create preparation and follow-up tasks"
3. Tasks will be created as WorkItems linked to the Event's project

Alternatively, use the built-in **Action Item** model for meeting action items.

### Q: Can WorkItem Activities have participants?

**A:** No. WorkItem Activities are designed for simple scheduling and task integration. If you need participant tracking, use Event instead.

### Q: What about recurring activities that aren't meetings?

**A:** For recurring non-meeting activities (e.g., "Monthly report submission"), create individual WorkItem Activities or use Django's built-in periodic task scheduling (Celery). Events are specifically designed for recurring **meetings** with participants.

### Q: Can I see both Events and WorkItem Activities on the calendar?

**A:** Yes! The OOBC Calendar (`/oobc-management/calendar/`) displays both:
- Events from the Coordination module
- WorkItem Activities from Project Management Portal
- Staff Tasks
- Personal calendar events

### Q: Which system integrates better with projects?

**A:** Both integrate with projects:
- **Event**: Optional project link, auto-generates tasks
- **WorkItem Activity**: Always part of a project, native task integration

For project-centric workflows, **WorkItem Activity** is more natural. For coordination workflows that *involve* projects, **Event** is better.

---

## Migration from Legacy Systems

### If you have existing calendar events

**Coordination meetings (participants tracked externally)**
→ Migrate to **Event** model

**Project activities (simple scheduling)**
→ Migrate to **WorkItem Activity**

**Recurring internal meetings**
→ Evaluate case-by-case:
- Formal, documented meetings → **Event**
- Quick check-ins, stand-ups → **WorkItem Activity**

---

## Conclusion

Both Event and WorkItem Activity are **fully supported, production-ready systems**. The choice depends on your use case:

- **Need participant tracking?** → Use **Event**
- **Need simple project scheduling?** → Use **WorkItem Activity**
- **Complex coordination workflow?** → Use **both** (Event for meetings, WorkItem Activities for tasks)

When in doubt, ask yourself: **"Do I need to track who's attending?"**
- **Yes** → Event
- **No** → WorkItem Activity

---

## Related Documentation

- [Event Model Documentation](../development/README.md#coordination-module)
- [WorkItem Model Documentation](../development/README.md#project-central)
- [OOBC Calendar Guide](../development/README.md#calendar-integration)
- [Project-Activity-Task Integration](../improvements/PROJECT_ACTIVITY_TASK_INTEGRATION_COMPLETE.md)

---

**Document Version:** 1.0
**Maintained By:** OBCMS Development Team
**Questions?** Contact the coordination team or file an issue in the project repository.
