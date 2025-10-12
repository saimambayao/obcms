# Organization Middleware Quick Reference

**Quick Access Guide for Developers**

---

## Request Attributes

Every authenticated request has these attributes:

```python
request.organization          # Organization instance or None
request.is_ocm_user          # Boolean: True if OCM user
request.can_switch_org       # Boolean: True if can switch organizations
```

---

## Common Patterns

### View Pattern

```python
def my_view(request):
    # Get organization (may be None)
    org = request.organization

    if not org:
        return render(request, 'error/no_org.html')

    # Filter by organization
    data = MyModel.objects.filter(moa_organization=org)

    return render(request, 'template.html', {
        'organization': org,
        'data': data,
    })
```

### API View Pattern

```python
from rest_framework import viewsets

class MyViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        org = self.request.organization

        if not org:
            return MyModel.objects.none()

        # OCM sees all
        if self.request.is_ocm_user:
            return MyModel.objects.all()

        # Others filtered
        return MyModel.objects.filter(moa_organization=org)
```

### Form Pattern

```python
from django import forms

class MyForm(forms.ModelForm):
    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.organization = organization

        # Limit choices to organization
        if organization:
            self.fields['related_field'].queryset = (
                RelatedModel.objects.filter(
                    moa_organization=organization
                )
            )
```

---

## Decorators

```python
from common.middleware.organization import (
    requires_organization,
    requires_organization_access
)

# Require organization context
@requires_organization
def my_view(request):
    # request.organization guaranteed to exist
    pass

# Require verified access
@requires_organization_access
def sensitive_view(request):
    # User access to organization verified
    pass
```

---

## Template Usage

```html
<!-- Check if organization exists -->
{% if request.organization %}
    <h1>{{ request.organization.name }}</h1>
    <p>Code: {{ request.organization.acronym }}</p>
{% endif %}

<!-- Show organization switcher for authorized users -->
{% if request.can_switch_org %}
    <a href="{% url 'organization_switch' %}">
        Switch Organization
    </a>
{% endif %}

<!-- Show OCM badge -->
{% if request.is_ocm_user %}
    <span class="badge badge-info">OCM - Read Only</span>
{% endif %}
```

---

## Thread-Local Storage

```python
from common.middleware.organization import (
    get_current_organization,
    set_current_organization,
    clear_current_organization
)

# In model managers
class MyManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        org = get_current_organization()

        if org:
            return qs.filter(moa_organization=org)

        return qs

# In utility functions
def process_data():
    org = get_current_organization()
    if org:
        # Process for specific organization
        pass
```

---

## URL Patterns

```python
# Organization-scoped URLs
urlpatterns = [
    # Format: /moa/<ORG_CODE>/...
    path('moa/<str:org_code>/dashboard/', views.dashboard),
    path('moa/<str:org_code>/planning/ppas/', views.ppa_list),
    path('moa/<str:org_code>/budget/', views.budget_home),
]
```

---

## Access Control Checks

```python
from common.middleware.organization import user_can_access_organization

# Manual access check
if not user_can_access_organization(request.user, organization):
    raise PermissionDenied("No access to this organization")

# Check if OCM user
from common.middleware.organization import is_ocm_user

if is_ocm_user(request.user):
    # Read-only access
    # Don't allow modifications
    pass
```

---

## Common Errors and Solutions

### Error: `request.organization` is None

**Solution:**
```python
# Always check if organization exists
org = request.organization
if not org:
    # Handle gracefully
    return render(request, 'error/no_org.html')
```

### Error: 403 Forbidden

**Solution:**
```python
# User doesn't have access to organization
# Check user's role and organization assignment
# Verify URL pattern matches organization acronym
```

### Error: Cross-organization data visible

**Solution:**
```python
# Ensure QuerySet is filtered by organization
data = MyModel.objects.filter(
    moa_organization=request.organization
)
```

---

## Security Reminders

⚠️ **ALWAYS filter QuerySets by organization**
⚠️ **NEVER trust organization from URL - use request.organization**
⚠️ **CHECK organization exists before using**
⚠️ **LOG security events (access denied, etc.)**
⚠️ **MOA staff CANNOT access other organizations**

---

## Testing

```python
from django.test import TestCase

class MyViewTest(TestCase):
    def test_organization_filtering(self):
        # Create organizations
        org_a = Organization.objects.create(acronym='org-a')
        org_b = Organization.objects.create(acronym='org-b')

        # Create user for org_a
        user = User.objects.create_user('test')
        user.moa_organization = org_a
        user.is_moa_staff = True
        user.save()

        self.client.force_login(user)

        # Should access org_a data
        response = self.client.get('/moa/org-a/data/')
        self.assertEqual(response.status_code, 200)

        # Should NOT access org_b data
        response = self.client.get('/moa/org-b/data/')
        self.assertEqual(response.status_code, 403)
```

---

## Role Quick Reference

| Role | Can View All | Can Modify | Can Switch |
|------|-------------|-----------|-----------|
| Superuser | ✅ Yes | ✅ Yes | ✅ Yes |
| OCM User | ✅ Yes | ❌ No | ✅ Yes |
| OOBC Staff | ✅ Yes | ✅ Yes | ✅ Yes |
| MOA Staff | ❌ No | ✅ Own Only | ❌ No |

---

## Useful Links

- [Full Implementation Guide](./ORGANIZATION_MIDDLEWARE_IMPLEMENTATION.md)
- [Security Considerations](./ORGANIZATION_MIDDLEWARE_SECURITY.md)
- [BMMS Transition Plan](../plans/bmms/TRANSITION_PLAN.md)

---

**Last Updated:** 2025-10-13
