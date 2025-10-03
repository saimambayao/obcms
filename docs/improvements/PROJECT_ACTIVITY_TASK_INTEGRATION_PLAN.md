# Project-Activity-Task Integration Plan

**Status**: APPROVED FOR IMPLEMENTATION
**Priority**: HIGH
**Complexity**: Moderate (mostly UI enhancements)
**Created**: 2025-10-03

## Executive Summary

This plan integrates OBCMS's three core management systems—**Projects** (PPAs/Workflows), **Activities/Events** (meetings, consultations), and **Tasks** (staff assignments)—into a unified project management framework.

**Key Finding**: 85-90% of required infrastructure already exists. Integration requires primarily UI enhancements and 2-3 new database fields.

## Architecture Overview

### Current Relationships (ALREADY IMPLEMENTED)

```
ProjectWorkflow
    ↓ (OneToOne)
MonitoringEntry (PPA)
    ↑ (FK: linked_ppa)
StaffTask ← (FK: linked_workflow) ─ ProjectWorkflow
    ↓ (FK: linked_event)
Event
```

**StaffTask already supports**:
- `linked_workflow` → ProjectWorkflow
- `linked_ppa` → MonitoringEntry (PPA)
- `linked_event` → Event
- `task_context` field for categorization

**Event currently has**:
- All scheduling/coordination metadata
- Resource booking, recurrence, notifications
- ❌ **Missing**: `related_project` → ProjectWorkflow

### Proposed Enhancement (3 NEW FIELDS)

```python
# Add to Event model
class Event(models.Model):
    # ... existing 40+ fields ...

    # NEW FIELDS
    related_project = models.ForeignKey(
        "project_central.ProjectWorkflow",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="project_activities"
    )

    is_project_activity = models.BooleanField(default=False)

    project_activity_type = models.CharField(
        max_length=30,
        choices=[
            ("project_kickoff", "Project Kickoff"),
            ("milestone_review", "Milestone Review"),
            ("stakeholder_consultation", "Stakeholder Consultation"),
            ("technical_review", "Technical Review"),
            ("progress_review", "Progress Review"),
            ("closeout", "Project Closeout"),
        ],
        blank=True
    )
```

```python
# Add to StaffTask model (enhance existing)
class StaffTask(models.Model):
    # ... existing 100+ fields including linked_event, linked_workflow ...

    # ENHANCE EXISTING FIELD
    task_context = models.CharField(
        max_length=20,
        choices=[
            ("standalone", "Standalone Task"),
            ("project", "Project Task"),
            ("activity", "Activity/Event Task"),
            ("project_activity", "Project Activity Task"),  # BOTH
        ],
        default="standalone"
    )
```

## Relationship Model

### Flexible Graph (RECOMMENDED)

Tasks can be:
1. **Standalone**: No project/activity (e.g., "Review emails")
2. **Project-only**: `linked_workflow` set (e.g., "Draft budget proposal")
3. **Activity-only**: `linked_event` set (e.g., "Prepare meeting agenda")
4. **Project-Activity**: BOTH set (e.g., "Prepare materials for project kickoff")

Activities can be:
1. **Standalone**: Generic office events (e.g., "All-staff meeting")
2. **Project-related**: `related_project` set (e.g., "Water project technical review")

Projects aggregate:
- Direct workflow tasks (`linked_workflow`)
- PPA tasks (`linked_ppa`)
- Activity tasks (via `Event.related_project` → tasks with `linked_event`)

## Implementation Phases

### Phase 1: Database Schema (PRIORITY: CRITICAL)

**Effort**: 2-3 hours
**Complexity**: Simple
**Risk**: Minimal (backward compatible)

**Tasks**:
1. Create migration adding `Event.related_project`, `Event.is_project_activity`, `Event.project_activity_type`
2. Create migration enhancing `StaffTask.task_context` choices
3. Add composite indexes:
   ```python
   models.Index(fields=['related_project', 'start_date'])
   models.Index(fields=['is_project_activity', 'status'])
   models.Index(fields=['task_context', 'status'])
   ```
4. Run migrations in development
5. Test backward compatibility

**Deliverables**:
- ✅ `coordination/migrations/XXXX_add_project_fields.py`
- ✅ `common/migrations/XXXX_enhance_task_context.py`
- ✅ Migration applied without errors
- ✅ Existing data preserved

**Verification**:
```bash
cd src
python manage.py makemigrations
python manage.py migrate
python manage.py check
```

---

### Phase 2: Model Logic & Properties (PRIORITY: CRITICAL)

**Effort**: 4-6 hours
**Complexity**: Moderate
**Prerequisites**: Phase 1 complete

**Tasks**:
1. Add `ProjectWorkflow.all_project_tasks` property:
   ```python
   @property
   def all_project_tasks(self):
       """Aggregate tasks from workflow + PPA + activities."""
       workflow_tasks = self.tasks.all()
       ppa_tasks = StaffTask.objects.filter(linked_ppa=self.ppa) if self.ppa else []
       activity_ids = self.project_activities.values_list('id', flat=True)
       activity_tasks = StaffTask.objects.filter(linked_event__id__in=activity_ids)
       return (workflow_tasks | ppa_tasks | activity_tasks).distinct()
   ```

2. Add `ProjectWorkflow.get_upcoming_activities()` method
3. Add `Event.save()` override for auto-task generation (if `auto_generate_tasks=True`)
4. Update `StaffTask.clean()` validation (warnings only, not errors)
5. Write unit tests for new relationships

**Deliverables**:
- ✅ `project_central/models.py` updated
- ✅ `coordination/models.py` updated
- ✅ `common/models.py` enhanced
- ✅ `tests/test_project_integration.py` created
- ✅ All tests passing

**Verification**:
```python
project = ProjectWorkflow.objects.get(pk='...')
assert project.all_project_tasks.count() > 0
assert project.project_activities.count() >= 0
```

---

### Phase 3: Project Dashboard UI (PRIORITY: HIGH)

**Effort**: 6-8 hours
**Complexity**: Moderate
**Prerequisites**: Phase 2 complete

**Tasks**:
1. Update `project_central/views.py` to include activities in context:
   ```python
   def workflow_detail_view(request, workflow_id):
       workflow = ProjectWorkflow.objects.prefetch_related(
           'project_activities',
           'all_project_tasks__assignees'
       ).get(pk=workflow_id)

       context = {
           'workflow': workflow,
           'activities': workflow.project_activities.all(),
           'tasks': workflow.all_project_tasks,
           'upcoming_activities': workflow.get_upcoming_activities(),
       }
       return render(request, 'project_central/workflow_detail.html', context)
   ```

2. Create activity list component in `templates/project_central/workflow_detail.html`:
   ```html
   <div class="project-activities">
       <h3>Upcoming Activities</h3>
       {% for activity in upcoming_activities %}
           <div class="activity-card">
               <h4>{{ activity.title }}</h4>
               <p>{{ activity.start_date }} | {{ activity.venue }}</p>
               <span class="badge">{{ activity.get_project_activity_type_display }}</span>
               <a href="{% url 'coordination:event_detail' activity.id %}">View Details</a>
           </div>
       {% endfor %}
       <button id="add-activity-btn">+ Add Activity</button>
   </div>
   ```

3. Add task filter (All / Activity-related / Direct):
   ```javascript
   function filterProjectTasks(filterType) {
       // 'all', 'activity', 'direct'
       const tasks = document.querySelectorAll('.task-card');
       tasks.forEach(task => {
           const context = task.dataset.taskContext;
           if (filterType === 'all' ||
               (filterType === 'activity' && context.includes('activity')) ||
               (filterType === 'direct' && context === 'project')) {
               task.style.display = 'block';
           } else {
               task.style.display = 'none';
           }
       });
   }
   ```

4. Add "+ Add Activity" quick action (opens event form with `related_project` pre-filled)

**Deliverables**:
- ✅ Enhanced project dashboard template
- ✅ Activity list component
- ✅ Task filtering JavaScript
- ✅ Quick action buttons

---

### Phase 4: Event Form Enhancement (PRIORITY: HIGH)

**Effort**: 4-5 hours
**Complexity**: Simple
**Prerequisites**: Phase 1 complete

**Tasks**:
1. Update `coordination/forms.py`:
   ```python
   class EventForm(forms.ModelForm):
       class Meta:
           model = Event
           fields = [
               'title', 'event_type', 'description',
               'start_date', 'start_time', 'venue',
               # NEW FIELDS
               'is_project_activity',
               'related_project',
               'project_activity_type',
               'auto_generate_tasks',
               # ... existing fields
           ]
   ```

2. Update `templates/coordination/event_form.html` with conditional project fields:
   ```html
   <div class="form-section">
       <label>
           <input type="checkbox" name="is_project_activity" id="is_project_activity">
           This is a project-specific activity
       </label>

       <div id="project-fields" class="hidden">
           <label>Related Project:</label>
           <select name="related_project">
               {% for project in active_projects %}
                   <option value="{{ project.id }}">{{ project.primary_need.title }}</option>
               {% endfor %}
           </select>

           <label>Activity Type:</label>
           <select name="project_activity_type">
               <option value="project_kickoff">Project Kickoff</option>
               <option value="milestone_review">Milestone Review</option>
               <!-- ... other types -->
           </select>

           <label>
               <input type="checkbox" name="auto_generate_tasks">
               Auto-create preparation and follow-up tasks
           </label>
       </div>
   </div>

   <script>
       document.getElementById('is_project_activity').addEventListener('change', function() {
           document.getElementById('project-fields').classList.toggle('hidden', !this.checked);
       });
   </script>
   ```

3. Update `coordination/views.py` to handle auto-task generation:
   ```python
   def event_create_view(request):
       if request.method == 'POST':
           form = EventForm(request.POST)
           if form.is_valid():
               event = form.save(commit=False)
               event.created_by = request.user
               event.save()

               # Auto-generate tasks if requested
               if form.cleaned_data.get('auto_generate_tasks'):
                   create_event_preparation_tasks(event)

               return redirect('coordination:event_detail', pk=event.id)
   ```

**Deliverables**:
- ✅ Enhanced event creation form
- ✅ Project field visibility toggle
- ✅ Auto-task generation logic

---

### Phase 5: Kanban & Calendar UI (PRIORITY: MEDIUM)

**Effort**: 5-6 hours
**Complexity**: Moderate
**Prerequisites**: Phase 2 complete

**Tasks**:

**A. Kanban Board Enhancements**:

1. Add task context badges to `templates/components/task_card.html`:
   ```html
   {% if task.task_context == 'project_activity' %}
       <span class="badge badge-purple">
           <i class="fas fa-project-diagram"></i> Project Activity
       </span>
   {% elif task.task_context == 'project' %}
       <span class="badge badge-blue">Project</span>
   {% elif task.task_context == 'activity' %}
       <span class="badge badge-emerald">Activity</span>
   {% endif %}

   {% if task.linked_workflow %}
       <div class="text-xs text-gray-600">
           <i class="fas fa-folder"></i>
           <a href="{{ task.linked_workflow.get_absolute_url }}">
               {{ task.linked_workflow.primary_need.title|truncatewords:5 }}
           </a>
       </div>
   {% endif %}

   {% if task.linked_event %}
       <div class="text-xs text-gray-600">
           <i class="fas fa-calendar"></i>
           <a href="{% url 'coordination:event_detail' task.linked_event.id %}">
               {{ task.linked_event.title }}
           </a>
       </div>
   {% endif %}
   ```

2. Add "Group by Project" filter to kanban view

**B. Calendar Enhancements**:

1. Update `common/services/calendar.py` to include project context:
   ```python
   def build_calendar_payload(filter_modules=None):
       events = []

       # Include Events with project context
       for event in Event.objects.select_related('related_project'):
           events.append({
               'id': f'event-{event.id}',
               'title': event.title,
               'start': event.start_datetime.isoformat(),
               'backgroundColor': '#10b981',
               'extendedProps': {
                   'type': 'event',
                   'is_project_activity': event.is_project_activity,
                   'project': {
                       'id': str(event.related_project.id) if event.related_project else None,
                       'name': event.related_project.primary_need.title if event.related_project else None
                   } if event.related_project else None
               }
           })

       # Include Tasks with project/activity context
       for task in StaffTask.objects.select_related('linked_workflow', 'linked_event'):
           events.append({
               'id': f'task-{task.id}',
               'title': task.title,
               'start': task.due_date.isoformat(),
               'backgroundColor': '#3b82f6' if task.task_context == 'project' else '#6366f1',
               'extendedProps': {
                   'type': 'task',
                   'task_context': task.task_context,
                   'project': {
                       'id': str(task.linked_workflow.id) if task.linked_workflow else None,
                       'name': task.linked_workflow.primary_need.title if task.linked_workflow else None
                   } if task.linked_workflow else None,
                   'event': {
                       'id': str(task.linked_event.id) if task.linked_event else None,
                       'name': task.linked_event.title if task.linked_event else None
                   } if task.linked_event else None
               }
           })

       return events
   ```

2. Add project badges to calendar events in JavaScript:
   ```javascript
   eventDidMount: function(info) {
       const props = info.event.extendedProps;
       if (props.project && props.project.id) {
           const badge = document.createElement('div');
           badge.className = 'calendar-project-badge';
           badge.innerHTML = `<i class="fas fa-project-diagram"></i> ${props.project.name}`;
           info.el.appendChild(badge);
       }
   }
   ```

**Deliverables**:
- ✅ Task cards show project/activity context
- ✅ Kanban supports "Group by Project" filter
- ✅ Calendar events display project badges
- ✅ Calendar tooltips show project context

---

### Phase 6: Workflow Automation (PRIORITY: LOW)

**Effort**: 6-8 hours
**Complexity**: Complex
**Prerequisites**: Phases 1-5 complete

**Tasks**:
1. Create task templates for common activity types:
   - `event_preparation_template` (send invitations, prepare materials, book venue)
   - `event_followup_template` (document minutes, distribute action items)

2. Implement auto-task generation on event creation:
   ```python
   def create_event_preparation_tasks(event):
       """Auto-create prep and follow-up tasks for project activities."""
       if not event.auto_generate_tasks:
           return

       # Preparation tasks (due before event)
       prep_tasks = [
           {
               'title': f'Prepare agenda for {event.title}',
               'activity_task_type': 'pre_event_prep',
               'due_date': event.start_date - timedelta(days=2),
           },
           {
               'title': f'Send invitations for {event.title}',
               'activity_task_type': 'pre_event_prep',
               'due_date': event.start_date - timedelta(days=3),
           },
           {
               'title': f'Book venue for {event.title}',
               'activity_task_type': 'logistics',
               'due_date': event.start_date - timedelta(days=5),
           },
       ]

       # Follow-up tasks (due after event)
       followup_tasks = [
           {
               'title': f'Document minutes for {event.title}',
               'activity_task_type': 'post_event_followup',
               'due_date': event.start_date + timedelta(days=1),
           },
           {
               'title': f'Distribute action items from {event.title}',
               'activity_task_type': 'post_event_followup',
               'due_date': event.start_date + timedelta(days=2),
           },
       ]

       for task_data in prep_tasks + followup_tasks:
           StaffTask.objects.create(
               title=task_data['title'],
               linked_event=event,
               linked_workflow=event.related_project if event.is_project_activity else None,
               task_context='project_activity' if event.related_project else 'activity',
               activity_task_type=task_data['activity_task_type'],
               due_date=task_data['due_date'],
               priority='medium',
               auto_generated=True,
               created_by=event.created_by,
           )
   ```

3. Add signal handlers for workflow stage progression
4. Implement notifications for project activity updates

**Deliverables**:
- ✅ Event task templates created
- ✅ Auto-task generation functional
- ✅ Signal handlers registered
- ✅ Notifications implemented

---

### Phase 7: Project Calendar View (PRIORITY: LOW)

**Effort**: 4-5 hours
**Complexity**: Simple
**Prerequisites**: Phases 1-5 complete

**Tasks**:
1. Create `/project-central/workflows/<workflow_id>/calendar/` endpoint
2. Render FullCalendar with project-specific events + tasks
3. Color-code by type (milestone/event/task)
4. Add event click handler to open detail modal

**Template**:
```html
<div id="project-calendar"></div>

<script>
var calendar = new FullCalendar.Calendar(document.getElementById('project-calendar'), {
    initialView: 'dayGridMonth',
    events: '/api/projects/{{ workflow.id }}/calendar-events/',
    eventDidMount: function(info) {
        const type = info.event.extendedProps.type;
        if (type === 'milestone') {
            info.el.style.borderLeft = '4px solid gold';
        } else if (type === 'task') {
            info.el.style.borderLeft = '4px solid #3b82f6';
        }
    },
    eventClick: function(info) {
        openDetailModal(info.event);
    }
});
calendar.render();
</script>
```

**Deliverables**:
- ✅ Project calendar view created
- ✅ Events filtered by project
- ✅ Visual differentiation by type
- ✅ Click-to-detail functionality

---

## Query Patterns

### Get all tasks for a project

```python
project = ProjectWorkflow.objects.get(pk='abc-123')

# Use property (recommended)
all_tasks = project.all_project_tasks

# Manual (for custom filtering)
workflow_tasks = project.tasks.all()
ppa_tasks = StaffTask.objects.filter(linked_ppa=project.ppa) if project.ppa else []
activity_ids = project.project_activities.values_list('id', flat=True)
activity_tasks = StaffTask.objects.filter(linked_event__id__in=activity_ids)
all_tasks = (workflow_tasks | ppa_tasks | activity_tasks).distinct()
```

### Get activities for a project by stage

```python
from coordination.models import Event

implementation_activities = Event.objects.filter(
    related_project_id=project_id,
    workflow_stage='implementation',
    is_project_activity=True
)
```

### Get user's tasks grouped by context

```python
user = request.user

tasks_by_context = {
    'standalone': StaffTask.objects.filter(assignees=user, task_context='standalone'),
    'project': StaffTask.objects.filter(assignees=user, task_context='project'),
    'activity': StaffTask.objects.filter(assignees=user, task_context='activity'),
    'project_activity': StaffTask.objects.filter(assignees=user, task_context='project_activity'),
}
```

### Performance optimization

```python
# Optimized project dashboard query (avoid N+1)
project = ProjectWorkflow.objects.select_related(
    'primary_need',
    'ppa',
    'project_lead'
).prefetch_related(
    'project_activities__participants',
    'tasks__assignees',
    'ppa__workflow_tasks'
).get(pk=project_id)
```

## Performance Considerations

### Indexes

All necessary indexes added in Phase 1:
```python
# Event indexes
models.Index(fields=['related_project', 'start_date'])
models.Index(fields=['is_project_activity', 'status'])

# StaffTask indexes
models.Index(fields=['linked_workflow', 'status', 'due_date'])
models.Index(fields=['task_context', 'status'])
```

### Query Optimization

- Use `select_related()` for foreign keys
- Use `prefetch_related()` for M2M and reverse FKs
- Consider caching `all_project_tasks` count for large projects:
  ```python
  class ProjectWorkflow(models.Model):
      cached_task_count = models.PositiveIntegerField(default=0)

      def update_cached_counts(self):
          self.cached_task_count = self.all_project_tasks.count()
          self.save(update_fields=['cached_task_count'])
  ```

### Database Considerations

- Composite indexes support common query patterns
- All new fields are nullable (no performance impact on existing data)
- Use `.distinct()` when combining QuerySets

## Testing Requirements

### Unit Tests

**File**: `tests/test_project_integration.py`

```python
class ProjectActivityIntegrationTest(TestCase):
    def test_create_project_activity(self):
        """Verify event can be linked to project."""
        event = Event.objects.create(
            title='Kickoff',
            related_project=self.project,
            is_project_activity=True
        )
        self.assertEqual(self.project.project_activities.count(), 1)

    def test_all_project_tasks_aggregation(self):
        """Verify tasks aggregate from multiple sources."""
        # Create workflow task, PPA task, activity task
        # Assert all appear in project.all_project_tasks
```

### Integration Tests

```python
def test_auto_task_generation(self):
    """Verify event creation generates tasks."""
    event = Event.objects.create(
        title='Meeting',
        auto_generate_tasks=True,
        related_project=self.project
    )
    tasks = StaffTask.objects.filter(linked_event=event)
    self.assertGreater(tasks.count(), 0)
```

### Performance Tests

```python
@override_settings(DEBUG=True)
def test_dashboard_query_count(self):
    """Ensure dashboard uses < 10 queries."""
    connection.queries_log.clear()
    project = ProjectWorkflow.objects.prefetch_related(...).get(pk=self.project.id)
    all_tasks = project.all_project_tasks
    self.assertLess(len(connection.queries), 10)
```

## Rollback Plan

All changes are backward compatible:

1. **Phase 1**: If migration fails, simply revert migration
2. **Phases 2-7**: Can disable features by:
   - Hiding UI components (CSS `display: none`)
   - Skipping auto-task generation (`auto_generate_tasks=False` default)
   - Using existing views (no forced changes)

**Data Safety**:
- All new fields are nullable (no data loss)
- Existing relationships preserved (SET_NULL on delete)
- No breaking changes to existing code

## Success Criteria

### Phase 1-3 (Critical)
- ✅ Event model has `related_project` field
- ✅ StaffTask has enhanced `task_context` field
- ✅ Migrations applied successfully
- ✅ Project dashboard shows activities
- ✅ Task filters functional

### Phase 4-5 (High Priority)
- ✅ Event form supports project linkage
- ✅ Kanban shows task context badges
- ✅ Calendar displays project context

### Phase 6-7 (Optional Enhancements)
- ✅ Auto-task generation functional
- ✅ Project calendar view created

## Timeline Estimate

| Phase | Effort | Risk | Dependencies |
|-------|--------|------|--------------|
| Phase 1: Schema | 2-3 hours | Low | None |
| Phase 2: Logic | 4-6 hours | Low | Phase 1 |
| Phase 3: Dashboard | 6-8 hours | Medium | Phase 2 |
| Phase 4: Forms | 4-5 hours | Low | Phase 1 |
| Phase 5: Kanban/Calendar | 5-6 hours | Medium | Phase 2 |
| Phase 6: Automation | 6-8 hours | High | Phases 1-5 |
| Phase 7: Calendar View | 4-5 hours | Low | Phases 1-5 |

**Total**: 31-41 hours

**Critical Path**: Phases 1 → 2 → 3 (12-17 hours for core functionality)

## Next Steps

1. ✅ **Review this plan** with stakeholders
2. ⏳ **Phase 1**: Create database migrations (START HERE)
3. ⏳ **Phase 2**: Implement model logic and properties
4. ⏳ **Phase 3**: Build enhanced project dashboard
5. ⏳ **Phases 4-7**: Incremental UI improvements

## References

- **Architecture Analysis**: Generated by architect agents (2025-10-03)
- **Task System Documentation**: `TASK_MANAGEMENT_COMPLETE_SUMMARY.md`
- **Calendar System**: `common/services/calendar.py`
- **Project Workflow**: `project_central/models.py`
- **OBCMS UI Standards**: `docs/ui/OBCMS_UI_COMPONENTS_STANDARDS.md`
