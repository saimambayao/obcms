# RBAC Template Tags - Quick Reference

**Quick reference for OBCMS permission-based template rendering**

---

## Load Tags

```django
{% load rbac_tags %}
```

---

## Permission Checks

### Check Specific Permission

```django
{% has_permission user 'communities.view_obc_community' org as can_view %}
{% if can_view %}
    <!-- Content here -->
{% endif %}
```

**Use when:** Checking create/edit/delete permissions

### Check Feature Access

```django
{% has_feature_access user 'communities.barangay_obc' org as can_access %}
{% if can_access %}
    <!-- Content here -->
{% endif %}
```

**Use when:** Checking module/navbar access

---

## Filters (One-Liners)

### Feature Access Filter

```django
{% if user|can_access_feature:'mana.regional_overview' %}
    <a href="...">Regional MANA</a>
{% endif %}
```

### Permission Filter

```django
{% if user|can_perform_action:'communities.create_obc' %}
    <button>Add Community</button>
{% endif %}
```

---

## Get Features

### Get All Accessible Features

```django
{% get_accessible_features user as features %}
{% for feature in features %}
    <a href="{{ feature.url_pattern }}">
        <i class="fas {{ feature.icon }}"></i> {{ feature.name }}
    </a>
{% endfor %}
```

### Get Sub-Features

```django
{% get_accessible_features user parent=feature as sub_features %}
{% for sub in sub_features %}
    <a href="{{ sub.url_pattern }}">{{ sub.name }}</a>
{% endfor %}
```

### Check for Sub-Features

```django
{% if feature|has_sub_features %}
    <!-- Render dropdown -->
{% endif %}
```

---

## RBAC Action Button

### Basic Button

```django
{% include 'components/rbac_action_button.html' with
   user=request.user
   permission_code='communities.create_obc'
   button_text='Add Community'
%}
```

### Link Button with Icon

```django
{% include 'components/rbac_action_button.html' with
   user=request.user
   permission_code='communities.view_obc'
   button_text='View Community'
   button_type='link'
   button_url='/communities/123/'
   icon_class='fa-eye'
%}
```

### Delete Button (Custom Style)

```django
{% include 'components/rbac_action_button.html' with
   user=request.user
   permission_code='communities.delete_obc'
   button_text='Delete'
   button_class='btn-danger btn-sm'
   icon_class='fa-trash'
   onclick='confirmDelete(123)'
%}
```

### Submit Button with Organization

```django
{% include 'components/rbac_action_button.html' with
   user=request.user
   permission_code='budget.approve_budget'
   organization=moa_org
   button_text='Approve Budget'
   button_type='submit'
   button_class='btn-success'
%}
```

---

## Context & Organizations

### Get Permission Context

```django
{% get_permission_context request as perm_context %}

<div>
    Organization: {{ perm_context.current_organization.name }}
    Can Switch: {{ perm_context.can_switch_organization }}
    OOBC Staff: {{ perm_context.is_oobc_staff }}
    MOA Staff: {{ perm_context.is_moa_staff }}
    OCM User: {{ perm_context.is_ocm_user }}
</div>
```

### Get User Organizations

```django
{% get_user_organizations user as orgs %}
{% for org in orgs %}
    <option value="{{ org.id }}">{{ org.name }}</option>
{% endfor %}
```

---

## Utility Tags

### Feature URL

```django
<a href="{% feature_url feature %}">{{ feature.name }}</a>
```

### Feature Icon

```django
<i class="fas {% feature_icon feature %}"></i>
```

---

## Button Component Parameters

| Parameter | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `user` | ✅ | User | - | User to check permissions for |
| `permission_code` | ✅ | string | - | Permission code (e.g., 'communities.create_obc') |
| `button_text` | ✅ | string | - | Text to display on button |
| `organization` | ❌ | Organization | request.organization | Organization context |
| `button_url` | ❌ | string | '#' | URL for link-type buttons |
| `button_class` | ❌ | string | (Tailwind default) | CSS classes for styling |
| `button_type` | ❌ | string | 'button' | Type: 'button', 'submit', 'link' |
| `button_id` | ❌ | string | - | HTML id attribute |
| `icon_class` | ❌ | string | - | Icon class (e.g., 'fa-plus') |
| `onclick` | ❌ | string | - | JavaScript onclick handler |
| `disabled` | ❌ | boolean | False | Whether button is disabled |

---

## Common Permission Codes

### Communities
- `communities.view_obc_community`
- `communities.create_obc`
- `communities.edit_obc`
- `communities.delete_obc`

### MANA
- `mana.view_assessment`
- `mana.create_assessment`
- `mana.edit_assessment`
- `mana.delete_assessment`

### Coordination
- `coordination.view_organization`
- `coordination.edit_organization`
- `coordination.delete_organization`

### Budget
- `budget.view_budget`
- `budget.create_budget`
- `budget.approve_budget`

---

## Common Feature Keys

### Navigation Features
- `communities.barangay_obc`
- `communities.municipal_obc`
- `communities.provincial_obc`
- `mana.regional_overview`
- `mana.provincial_overview`
- `coordination.organizations`
- `coordination.partnerships`
- `coordination.events`

---

## Quick Patterns

### Permission-Gated Section

```django
{% has_feature_access user 'module.feature' as can_access %}
{% if can_access %}
    <section class="feature-section">
        <!-- Feature content -->
    </section>
{% endif %}
```

### Dynamic Feature Grid

```django
{% get_accessible_features user as features %}
<div class="grid">
    {% for feature in features %}
        {% if feature.module == 'communities' %}
            <div class="card">
                <a href="{% feature_url feature %}">
                    <i class="fas {% feature_icon feature %}"></i>
                    <h3>{{ feature.name }}</h3>
                </a>
            </div>
        {% endif %}
    {% endfor %}
</div>
```

### Organization-Scoped Actions

```django
{% for org in organizations %}
    <div class="org-card">
        <h3>{{ org.name }}</h3>

        {% has_permission user 'coordination.edit_organization' org as can_edit %}
        {% if can_edit %}
            {% include 'components/rbac_action_button.html' with
               user=user
               permission_code='coordination.edit_organization'
               organization=org
               button_text='Edit'
               button_class='btn-primary btn-sm'
            %}
        {% endif %}
    </div>
{% endfor %}
```

---

## Tips

💡 **Use `has_permission` for action permissions** (create, edit, delete)

💡 **Use `has_feature_access` for feature visibility** (modules, navbar items)

💡 **Use filters for simple checks** (one-liner conditionals)

💡 **Use RBAC button component for consistency** (reusable, styled)

💡 **Pass organization explicitly when needed** (for multi-tenant checks)

💡 **Check `has_sub_features` before rendering dropdowns**

---

## Migration from moa_rbac

### Before (moa_rbac)

```django
{% load moa_rbac %}

{% if user|can_access_mana_filter %}
    <a href="{% url 'mana:mana_home' %}">MANA</a>
{% endif %}

{% if user|can_edit_communities %}
    <button>Edit</button>
{% endif %}
```

### After (rbac_tags)

```django
{% load rbac_tags %}

{% if user|can_access_feature:'mana.regional_overview' %}
    <a href="{% url 'mana:mana_home' %}">MANA</a>
{% endif %}

{% include 'components/rbac_action_button.html' with
   user=user
   permission_code='communities.edit_obc'
   button_text='Edit'
%}
```

---

**See Also:**
- [Full Documentation](PHASE_3_RBAC_TEMPLATE_TAGS_COMPLETE.md)
- [RBACService API](../../src/common/services/rbac_service.py)
- [RBAC Models](../../src/common/rbac_models.py)
