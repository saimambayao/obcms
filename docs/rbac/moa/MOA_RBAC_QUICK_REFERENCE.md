# MOA RBAC Quick Reference Guide

**For Developers** | **Last Updated:** 2025-10-08

---

## Quick Access Decision Matrix

**"Can this MOA user do X?"**

| Action | OBC Communities | MOA Organization | MOA PPAs | Other MOA PPAs | MANA | Work Items |
|--------|----------------|------------------|----------|----------------|------|------------|
| **View** | ✅ YES | ✅ YES (own only) | ✅ YES (own only) | ❌ NO | ❌ NO | ✅ YES (own only) |
| **Create** | ❌ NO | ❌ NO | ✅ YES | ❌ NO | ❌ NO | ✅ YES (for own PPAs) |
| **Edit** | ❌ NO | ✅ YES (own only) | ✅ YES (own only) | ❌ NO | ❌ NO | ✅ YES (own only) |
| **Delete** | ❌ NO | ❌ NO | ✅ YES (own only) | ❌ NO | ❌ NO | ✅ YES (own only) |

---

## Code Snippets Cheat Sheet

### 1. Check if User is MOA Staff

```python
# In view
if request.user.is_moa_staff:
    # MOA-specific logic

# In model
user.is_moa_staff  # Returns True for bmoa, lgu, nga user types
```

### 2. Check if User Owns Organization

```python
# In view
if request.user.owns_moa_organization(org_id):
    # User can edit this organization

# In template
{% user_can_edit_organization organization as can_edit %}
{% if can_edit %}
    <a href="...">Edit</a>
{% endif %}
```

### 3. Check if User Owns PPA

```python
# In view
if request.user.owns_moa_ppa(ppa_id):
    # User can edit this PPA

# In template
{% user_can_edit_ppa ppa as can_edit %}
{% if can_edit %}
    <a href="...">Edit</a>
{% endif %}
```

### 4. Protect View (View-Only)

```python
from common.permissions.decorators import moa_view_only

@moa_view_only('OBC Communities')
def community_list(request):
    # MOA users can only GET
    ...
```

### 5. Protect View (Edit Own Organization)

```python
from common.permissions.decorators import moa_can_edit_organization

@moa_can_edit_organization
def organization_update(request, pk):
    # MOA users can only edit their own MOA
    ...
```

### 6. Protect View (Edit Own PPA)

```python
from common.permissions.decorators import moa_can_edit_ppa

@moa_can_edit_ppa
def ppa_update(request, pk):
    # MOA users can only edit their own PPAs
    ...
```

### 7. Block MOA Access Completely

```python
from common.permissions.decorators import moa_no_access

@moa_no_access('MANA Assessments')
def assessment_list(request):
    # MOA users get 403 Forbidden
    ...
```

### 8. Auto-Filter QuerySet (Class-Based View)

```python
from common.permissions.mixins import MOAFilteredQuerySetMixin

class PPAListView(MOAFilteredQuerySetMixin, ListView):
    model = MonitoringEntry
    moa_filter_field = 'implementing_moa'
    # QuerySet auto-filtered to user's MOA
```

### 9. Restrict Organization Access (Class-Based View)

```python
from common.permissions.mixins import MOAOrganizationAccessMixin

class OrganizationUpdateView(MOAOrganizationAccessMixin, UpdateView):
    model = Organization
    # Object retrieval checks ownership
```

### 10. Restrict PPA Access (Class-Based View)

```python
from common.permissions.mixins import MOAPPAAccessMixin

class PPAUpdateView(MOAPPAAccessMixin, UpdateView):
    model = MonitoringEntry
    # Object retrieval checks ownership
```

---

## Common Patterns

### Pattern 1: List View with Auto-Filtering

**Use Case:** Show MOA users only their own PPAs

```python
from django.views.generic import ListView
from common.permissions.mixins import MOAFilteredQuerySetMixin
from monitoring.models import MonitoringEntry

class MyPPAListView(MOAFilteredQuerySetMixin, ListView):
    model = MonitoringEntry
    template_name = 'monitoring/my_ppa_list.html'
    context_object_name = 'ppas'
    moa_filter_field = 'implementing_moa'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        # Additional filtering
        return qs.filter(category='moa_ppa').order_by('-updated_at')
```

**Template:** `my_ppa_list.html`
```django
{% for ppa in ppas %}
    <div class="ppa-card">
        <h3>{{ ppa.title }}</h3>
        <a href="{% url 'monitoring:ppa_detail' ppa.id %}">View</a>

        {% user_can_edit_ppa ppa as can_edit %}
        {% if can_edit %}
            <a href="{% url 'monitoring:ppa_update' ppa.id %}">Edit</a>
        {% endif %}
    </div>
{% endfor %}
```

### Pattern 2: Update View with Ownership Check

**Use Case:** MOA user can edit own organization

```python
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from common.permissions.mixins import MOAOrganizationAccessMixin
from coordination.models import Organization
from coordination.forms import OrganizationForm

class OrganizationUpdateView(MOAOrganizationAccessMixin, UpdateView):
    model = Organization
    form_class = OrganizationForm
    template_name = 'coordination/organization_form.html'

    def get_success_url(self):
        return reverse_lazy('coordination:organization_detail', args=[self.object.pk])
```

### Pattern 3: Create View for MOA PPAs

**Use Case:** MOA user creates a new PPA

```python
from django.views.generic import CreateView
from django.urls import reverse_lazy
from monitoring.models import MonitoringEntry
from monitoring.forms import PPAForm

class PPACreateView(CreateView):
    model = MonitoringEntry
    form_class = PPAForm
    template_name = 'monitoring/ppa_form.html'

    def form_valid(self, form):
        # Auto-assign implementing_moa to user's MOA
        if self.request.user.is_moa_staff:
            form.instance.implementing_moa = self.request.user.moa_organization

        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('monitoring:ppa_detail', args=[self.object.pk])
```

### Pattern 4: Function-Based View with Decorator

**Use Case:** View-only access to communities

```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from common.permissions.decorators import moa_view_only
from communities.models import OBCCommunity

@login_required
@moa_view_only('OBC Communities')
def community_list(request):
    """List all OBC communities (view-only for MOA)."""
    communities = OBCCommunity.objects.filter(is_active=True)

    return render(request, 'communities/community_list.html', {
        'communities': communities,
        'is_readonly': request.user.is_moa_staff,
    })
```

**Template:** `community_list.html`
```django
{% if not is_readonly %}
    <a href="{% url 'communities:community_create' %}" class="btn btn-primary">
        Create Community
    </a>
{% else %}
    <p class="text-muted">
        <i class="fas fa-info-circle"></i>
        MOA users have view-only access to OBC communities.
    </p>
{% endif %}
```

### Pattern 5: Conditional Navigation Menu

**Use Case:** Show different menus for OOBC vs MOA users

```django
<!-- base.html -->
<nav class="sidebar">
    {% if user.is_oobc_staff %}
        <!-- Full navigation for OOBC -->
        <a href="{% url 'mana:assessment_list' %}">MANA</a>
        <a href="{% url 'monitoring:ppa_list' %}">All PPAs</a>
        <a href="{% url 'coordination:organization_list' %}">All Organizations</a>

    {% elif user.is_moa_staff %}
        <!-- Limited navigation for MOA -->
        <a href="{% url 'communities:community_list' %}">
            <i class="fas fa-users"></i> OBC Communities (View Only)
        </a>
        <a href="{% url 'monitoring:my_ppa_list' %}">
            <i class="fas fa-project-diagram"></i> My PPAs
        </a>
        <a href="{% url 'coordination:my_organization' %}">
            <i class="fas fa-building"></i> My Organization
        </a>

        {% if not user.moa_organization %}
        <div class="alert alert-warning">
            <i class="fas fa-exclamation-triangle"></i>
            Your account is not linked to an MOA. Contact admin.
        </div>
        {% endif %}
    {% endif %}
</nav>
```

---

## Template Tags Reference

### Load Tags

```django
{% load moa_permissions %}
```

### Available Tags

| Tag | Usage | Returns |
|-----|-------|---------|
| `user_can_edit_organization` | `{% user_can_edit_organization org as can_edit %}` | Boolean |
| `user_can_edit_ppa` | `{% user_can_edit_ppa ppa as can_edit %}` | Boolean |
| `user_can_view_ppa` | `{% user_can_view_ppa ppa as can_view %}` | Boolean |
| `user_can_delete_ppa` | `{% user_can_delete_ppa ppa as can_delete %}` | Boolean |
| `user_can_create_ppa` | `{% user_can_create_ppa as can_create %}` | Boolean |
| `user_can_view_community` | `{% user_can_view_community comm as can_view %}` | Boolean |
| `user_can_access_mana` | `{% user_can_access_mana as can_access %}` | Boolean |

### Example Usage

```django
{% load moa_permissions %}

{% user_can_edit_ppa ppa as can_edit %}
{% user_can_delete_ppa ppa as can_delete %}

<div class="ppa-actions">
    {% if can_edit %}
        <a href="{% url 'monitoring:ppa_update' ppa.id %}" class="btn btn-primary">
            <i class="fas fa-edit"></i> Edit
        </a>
    {% endif %}

    {% if can_delete %}
        <a href="{% url 'monitoring:ppa_delete' ppa.id %}" class="btn btn-danger">
            <i class="fas fa-trash"></i> Delete
        </a>
    {% endif %}

    {% if not can_edit %}
        <p class="text-muted">
            <i class="fas fa-lock"></i>
            You can only edit PPAs implemented by {{ user.moa_organization }}.
        </p>
    {% endif %}
</div>
```

---

## Error Handling

### Permission Denied (403)

When a permission check fails, Django raises `PermissionDenied`:

```python
from django.core.exceptions import PermissionDenied

# In decorator
if request.user.is_moa_staff and not allowed:
    raise PermissionDenied(
        "You can only edit your own MOA organization. "
        f"This organization belongs to {org.name}."
    )
```

**Custom 403 Template:** `src/templates/403.html`

```django
{% extends 'common/base.html' %}

{% block content %}
<div class="error-page">
    <h1>403 - Permission Denied</h1>
    <p>{{ exception }}</p>

    {% if user.is_moa_staff %}
        <div class="help-box">
            <h3>MOA User Access Limitations:</h3>
            <ul>
                <li>You can only edit your own MOA's data</li>
                <li>You have view-only access to OBC communities</li>
                <li>MANA assessments are restricted to OOBC staff</li>
            </ul>
            <p>Contact support: <a href="mailto:support@oobc.gov.ph">support@oobc.gov.ph</a></p>
        </div>
    {% endif %}

    <a href="{% url 'common:dashboard' %}" class="btn btn-primary">
        <i class="fas fa-home"></i> Return to Dashboard
    </a>
</div>
{% endblock %}
```

---

## Testing Checklist

### Unit Tests

```python
# Test permission decorator
def test_moa_view_only_blocks_post(self):
    """MOA users cannot POST to view-only endpoints."""
    @moa_view_only('Test')
    def view(request):
        return "OK"

    request = self.factory.post('/test/')
    request.user = self.moa_user

    with self.assertRaises(PermissionDenied):
        view(request)

# Test ownership check
def test_moa_cannot_edit_other_ppa(self):
    """MOA user cannot edit another MOA's PPA."""
    other_ppa = MonitoringEntry.objects.create(
        implementing_moa=self.other_moa
    )

    self.assertFalse(
        self.moa_user.owns_moa_ppa(other_ppa.id)
    )
```

### Integration Tests

```python
# Test complete workflow
def test_moa_can_create_and_edit_ppa(self):
    """MOA user can create and edit own PPA."""
    self.client.login(username='moa_user', password='pass')

    # Create PPA
    response = self.client.post('/monitoring/ppa/create/', {
        'title': 'Health Program',
        'category': 'moa_ppa',
        'implementing_moa': self.moa.id,
    })
    self.assertEqual(response.status_code, 302)  # Redirect

    # Edit PPA
    ppa = MonitoringEntry.objects.last()
    response = self.client.post(f'/monitoring/ppa/{ppa.id}/update/', {
        'title': 'Updated Health Program',
    })
    self.assertEqual(response.status_code, 302)
```

---

## Common Pitfalls

### ❌ Pitfall 1: Forgetting to Filter QuerySet

**Bad:**
```python
# MOA users can see ALL PPAs
class PPAListView(ListView):
    model = MonitoringEntry
```

**Good:**
```python
# Auto-filtered to user's MOA
class PPAListView(MOAFilteredQuerySetMixin, ListView):
    model = MonitoringEntry
    moa_filter_field = 'implementing_moa'
```

### ❌ Pitfall 2: Only Checking Permissions in Template

**Bad:**
```django
<!-- Only hide button, but URL is still accessible -->
{% if user.is_oobc_staff %}
    <a href="{% url 'mana:assessment_create' %}">Create Assessment</a>
{% endif %}
```

**Good:**
```python
# Also protect the view
@moa_no_access('MANA Assessments')
def assessment_create(request):
    ...
```

### ❌ Pitfall 3: Not Validating Ownership in Forms

**Bad:**
```python
# User can manipulate implementing_moa field
class PPAUpdateView(UpdateView):
    model = MonitoringEntry
    fields = ['title', 'implementing_moa']  # DANGEROUS
```

**Good:**
```python
# Validate and enforce ownership
class PPAUpdateView(MOAPPAAccessMixin, UpdateView):
    model = MonitoringEntry
    fields = ['title', 'status']  # Exclude implementing_moa
```

---

## Performance Tips

### 1. Use select_related for Foreign Keys

```python
# Avoid N+1 queries
User.objects.select_related('moa_organization').filter(...)

# In QuerySet
qs = MonitoringEntry.objects.select_related('implementing_moa')
```

### 2. Add Database Indexes

```python
# In migration
class Migration(migrations.Migration):
    operations = [
        migrations.AddIndex(
            model_name='user',
            index=models.Index(
                fields=['user_type', 'moa_organization'],
                name='user_type_moa_idx'
            ),
        ),
    ]
```

### 3. Cache Permission Checks

```python
# Cache user's MOA organization in session
if not hasattr(request, '_moa_organization_cache'):
    request._moa_organization_cache = request.user.moa_organization

# Use cached value
if request._moa_organization_cache == ppa.implementing_moa:
    ...
```

---

## Security Best Practices

### ✅ DO:
- Always validate ownership at multiple layers (view, model, template)
- Use Django's built-in `PermissionDenied` exception
- Log all MOA user actions for audit trail
- Provide clear error messages explaining access restrictions
- Test all permission scenarios thoroughly

### ❌ DON'T:
- Rely only on template-level hiding
- Allow MOA users to edit `user_type` or `moa_organization`
- Expose sensitive OOBC data in API responses
- Skip input validation in forms
- Forget to check permissions in API endpoints

---

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| MOA user sees "Permission Denied" | Check if `moa_organization` is set correctly |
| MOA user can't edit own PPA | Verify `implementing_moa` matches `user.moa_organization` |
| MOA user sees other MOAs' PPAs | Apply `MOAFilteredQuerySetMixin` to view |
| Template shows edit button but URL is blocked | Check decorator is applied to view |
| Tests failing with PermissionDenied | Ensure test user has `moa_organization` set |

---

## Additional Resources

- **Full Design Doc:** [MOA_RBAC_DESIGN.md](MOA_RBAC_DESIGN.md)
- **Implementation Status:** [MOA_RBAC_IMPLEMENTATION_STATUS.md](MOA_RBAC_IMPLEMENTATION_STATUS.md)
- **User Guide:** Appendix C in design document
- **Django Permissions Docs:** https://docs.djangoproject.com/en/4.2/topics/auth/default/

---

**Questions?** Contact: dev@oobc.gov.ph
