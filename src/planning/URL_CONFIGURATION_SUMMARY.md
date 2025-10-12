# Planning Module URL Configuration

**File:** `src/planning/urls.py`  
**Status:** ✅ Complete  
**Date:** 2025-10-13

## Overview

Comprehensive RESTful URL configuration for the Planning module implementing clean URL patterns for strategic planning and annual work plan management.

## Configuration Details

### App Namespace
- **app_name:** `planning`
- **Total URLs:** 19 endpoints
- **Import:** Views from `planning.views` (to be implemented)

## URL Pattern Structure

### 1. Dashboard (1 URL)
```python
path("", views.planning_dashboard, name="dashboard")
```
- **URL:** `/planning/`
- **Reverse:** `planning:dashboard`

### 2. Strategic Plans (5 URLs)
```python
path("strategic/", views.strategic_plan_list, name="strategic_list")
path("strategic/create/", views.strategic_plan_create, name="strategic_create")
path("strategic/<int:pk>/", views.strategic_plan_detail, name="strategic_detail")
path("strategic/<int:pk>/edit/", views.strategic_plan_edit, name="strategic_edit")
path("strategic/<int:pk>/delete/", views.strategic_plan_delete, name="strategic_delete")
```
- **List:** `/planning/strategic/` → `planning:strategic_list`
- **Create:** `/planning/strategic/create/` → `planning:strategic_create`
- **Detail:** `/planning/strategic/123/` → `planning:strategic_detail`
- **Edit:** `/planning/strategic/123/edit/` → `planning:strategic_edit`
- **Delete:** `/planning/strategic/123/delete/` → `planning:strategic_delete`

### 3. Strategic Goals (4 URLs)
```python
path("goals/create/<int:plan_id>/", views.goal_create, name="goal_create")
path("goals/<int:pk>/edit/", views.goal_edit, name="goal_edit")
path("goals/<int:pk>/progress/", views.goal_update_progress, name="goal_update_progress")
path("goals/<int:pk>/delete/", views.goal_delete, name="goal_delete")
```
- **Create:** `/planning/goals/create/123/` → `planning:goal_create`
- **Edit:** `/planning/goals/456/edit/` → `planning:goal_edit`
- **Update Progress:** `/planning/goals/456/progress/` → `planning:goal_update_progress`
- **Delete:** `/planning/goals/456/delete/` → `planning:goal_delete`

### 4. Annual Work Plans (5 URLs)
```python
path("annual/", views.annual_plan_list, name="annual_list")
path("annual/create/", views.annual_plan_create, name="annual_create")
path("annual/<int:pk>/", views.annual_plan_detail, name="annual_detail")
path("annual/<int:pk>/edit/", views.annual_plan_edit, name="annual_edit")
path("annual/<int:pk>/delete/", views.annual_plan_delete, name="annual_delete")
```
- **List:** `/planning/annual/` → `planning:annual_list`
- **Create:** `/planning/annual/create/` → `planning:annual_create`
- **Detail:** `/planning/annual/2024/` → `planning:annual_detail`
- **Edit:** `/planning/annual/2024/edit/` → `planning:annual_edit`
- **Delete:** `/planning/annual/2024/delete/` → `planning:annual_delete`

### 5. Work Plan Objectives (4 URLs)
```python
path("objectives/create/<int:plan_id>/", views.objective_create, name="objective_create")
path("objectives/<int:pk>/edit/", views.objective_edit, name="objective_edit")
path("objectives/<int:pk>/progress/", views.objective_update_progress, name="objective_update_progress")
path("objectives/<int:pk>/delete/", views.objective_delete, name="objective_delete")
```
- **Create:** `/planning/objectives/create/2024/` → `planning:objective_create`
- **Edit:** `/planning/objectives/789/edit/` → `planning:objective_edit`
- **Update Progress:** `/planning/objectives/789/progress/` → `planning:objective_update_progress`
- **Delete:** `/planning/objectives/789/delete/` → `planning:objective_delete`

## RESTful Design Principles

### ✅ Conventions Followed
1. **Resource-based URLs:** `/strategic/`, `/annual/`, `/goals/`, `/objectives/`
2. **HTTP method simulation:** `/create/`, `/edit/`, `/delete/` suffixes
3. **Hierarchical structure:** Goals and objectives linked to plans via `plan_id`
4. **Consistent naming:** `list`, `create`, `detail`, `edit`, `delete` patterns
5. **Primary key routing:** `<int:pk>` for resource identification
6. **Nested resources:** Create actions use parent `plan_id`

### URL Naming Patterns
- **Lists:** `{resource}_list` (e.g., `strategic_list`)
- **Create:** `{resource}_create` (e.g., `strategic_create`)
- **Detail:** `{resource}_detail` (e.g., `strategic_detail`)
- **Edit:** `{resource}_edit` (e.g., `strategic_edit`)
- **Delete:** `{resource}_delete` (e.g., `strategic_delete`)
- **Custom Actions:** `{resource}_update_progress` (e.g., `goal_update_progress`)

## Template Usage Examples

### In Django Templates
```django
{# Dashboard #}
<a href="{% url 'planning:dashboard' %}">Planning Dashboard</a>

{# Strategic Plans #}
<a href="{% url 'planning:strategic_list' %}">All Strategic Plans</a>
<a href="{% url 'planning:strategic_create' %}">New Strategic Plan</a>
<a href="{% url 'planning:strategic_detail' plan.pk %}">View Plan</a>
<a href="{% url 'planning:strategic_edit' plan.pk %}">Edit Plan</a>

{# Goals (linked to plan) #}
<a href="{% url 'planning:goal_create' plan.pk %}">Add Goal to Plan</a>
<a href="{% url 'planning:goal_edit' goal.pk %}">Edit Goal</a>
<a href="{% url 'planning:goal_update_progress' goal.pk %}">Update Progress</a>

{# Annual Plans #}
<a href="{% url 'planning:annual_list' %}">Annual Work Plans</a>
<a href="{% url 'planning:annual_detail' annual.pk %}">View Annual Plan</a>

{# Objectives (linked to annual plan) #}
<a href="{% url 'planning:objective_create' annual.pk %}">Add Objective</a>
<a href="{% url 'planning:objective_update_progress' obj.pk %}">Update Progress</a>
```

### In Python Views
```python
from django.urls import reverse

# Dashboard
dashboard_url = reverse('planning:dashboard')

# Strategic Plans
list_url = reverse('planning:strategic_list')
create_url = reverse('planning:strategic_create')
detail_url = reverse('planning:strategic_detail', kwargs={'pk': 123})
edit_url = reverse('planning:strategic_edit', args=[123])

# Goals (with plan context)
goal_create_url = reverse('planning:goal_create', kwargs={'plan_id': 123})
goal_progress_url = reverse('planning:goal_update_progress', kwargs={'pk': 456})

# Annual Plans
annual_list_url = reverse('planning:annual_list')
annual_detail_url = reverse('planning:annual_detail', kwargs={'pk': 2024})

# Objectives (with plan context)
obj_create_url = reverse('planning:objective_create', kwargs={'plan_id': 2024})
```

## Integration Points

### Main Project URLs
Add to `src/obc_management/urls.py`:
```python
urlpatterns = [
    # ... other patterns ...
    path('planning/', include('planning.urls')),
]
```

### Middleware Compatibility
- ✅ Compatible with URL refactoring middleware
- ✅ Supports namespace-based routing
- ✅ Clean separation from other app URLs

## Next Steps

### 1. View Implementation
All 19 view functions need to be implemented in `src/planning/views.py`:
- `planning_dashboard`
- Strategic Plan views (5)
- Goal views (4)
- Annual Plan views (5)
- Objective views (4)

### 2. Template Creation
Create templates in `src/templates/planning/`:
- Dashboard template
- List templates for strategic plans and annual plans
- Detail templates with HTMX partials
- Form templates for create/edit operations

### 3. Form Integration
Link with existing forms in `src/planning/forms.py`:
- `StrategicPlanForm`
- `StrategicGoalForm`
- `AnnualWorkPlanForm`
- `WorkPlanObjectiveForm`

### 4. HTMX Enhancement
Implement instant UI updates for:
- Progress updates (goals and objectives)
- Delete confirmations
- Form autosave
- Dynamic content loading

## Validation Status

✅ **Syntax:** Valid Python/Django syntax  
✅ **Structure:** RESTful conventions followed  
✅ **Naming:** Consistent naming patterns  
✅ **Namespace:** Properly configured as `planning`  
✅ **Documentation:** Comprehensive docstring included  
✅ **Standards:** Follows OBCMS URL refactoring guidelines  

## Phase 0 URL Refactoring Compliance

- ✅ Clean namespace separation (`planning:`)
- ✅ RESTful URL patterns
- ✅ No legacy URL patterns
- ✅ Follows project URL standards
- ✅ Ready for future middleware integration
- ✅ Compatible with HTMX instant UI patterns

---

**Next Task:** Implement view functions in `src/planning/views.py`
