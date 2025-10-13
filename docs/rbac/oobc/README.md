# OOBC RBAC Documentation

**Purpose:** Role-Based Access Control for OOBC (Office for Other Bangsamoro Communities) staff and executives.

---

## Quick Links

### Primary Documentation
- **[OOBC RBAC Master Reference](OOBC_RBAC_MASTER_REFERENCE.md)** ⭐ **START HERE** - Complete RBAC system guide for OOBC users

---

## OOBC Role Hierarchy

### 1. OOBC Executive Director
- **Full System Access** - All features and modules
- **Strategic Decision-Making** - MANA, Recommendations, Planning & Budgeting
- **System Administration** - RBAC Management, User Approvals

### 2. OOBC Deputy Executive Director
- **Full System Access** - All features and modules (same as Executive Director)
- **Strategic Decision-Making** - MANA, Recommendations, Planning & Budgeting
- **System Administration** - RBAC Management, User Approvals

### 3. OOBC Staff
- **Operational Access** - M&E, Coordination, OBC Data
- **Field Operations** - Field coordinators, M&E officers, program officers
- **Restricted** - No access to strategic planning modules

---

## What's Included

### ✅ OOBC Staff Can Access:
1. **OBC Data** - View, create, edit OBC community records
2. **Coordination** - Manage organizations, partnerships, events
3. **M&E (Monitoring & Evaluation)** - Track PPAs, initiatives, work items
4. **OOBC Management** - Staff profiles, work items, calendar

### ❌ OOBC Staff CANNOT Access:
1. **MANA** - Strategic needs assessment (executives only)
2. **Recommendations** - Policy recommendations (executives only)
3. **Planning & Budgeting** - Strategic planning tools (executives only)
4. **Project Management** - Advanced portfolio management (executives only)
5. **User Approvals** - Account approval system (executives only)
6. **RBAC Management** - Role/permission administration (executives only)

---

## Implementation Status

**Status:** ✅ FULLY OPERATIONAL
**Version:** 2.0
**Last Updated:** October 13, 2025

### Completed Features:
- [x] Three-tier role hierarchy (Executive Director, Deputy Director, Staff)
- [x] Feature-based access control (7 features defined)
- [x] Navigation filtering based on permissions
- [x] View-level protection with decorators
- [x] Template-level filtering
- [x] Database-level role assignments

---

## Technical Implementation

### Key Files:
1. `src/common/rbac_models.py` - Role, Feature, Permission models
2. `src/common/services/rbac_service.py` - Permission checking service
3. `src/common/mixins/rbac_mixins.py` - View mixins for protection
4. `src/common/decorators/rbac_decorators.py` - View decorators
5. `src/common/templatetags/rbac_tags.py` - Template tags
6. `src/templates/common/navbar.html` - Navigation with feature checks

### Migration Files:
- `0040_add_oobc_staff_rbac_restrictions.py` - Initial RBAC setup
- `0045_add_monitoring_access_feature.py` - M&E feature creation
- `0046_grant_monitoring_to_oobc_staff.py` - Grant M&E to staff

---

## Quick Start

### For Developers:

**Check user's feature access:**
```python
from common.services.rbac_service import RBACService

# Check if user can access MANA
can_access = RBACService.has_feature_access(user, 'mana_access')
```

**Protect a view:**
```python
from common.decorators.rbac_decorators import require_feature_access

@require_feature_access('mana_access')
@login_required
def my_view(request):
    # Only users with mana_access can access
    ...
```

**Template usage:**
```django
{% load rbac_tags %}

{% has_feature_access user 'mana_access' as can_access_mana %}
{% if can_access_mana %}
    <a href="{% url 'mana:home' %}">MANA</a>
{% endif %}
```

### For System Administrators:

**Assign OOBC Staff role:**
```python
from django.contrib.auth import get_user_model
from common.rbac_models import Role, UserRole

User = get_user_model()
oobc_staff_role = Role.objects.get(slug='oobc-staff')

user = User.objects.get(username='staff.test')
UserRole.objects.get_or_create(
    user=user,
    role=oobc_staff_role,
    defaults={'is_active': True}
)
```

---

## Troubleshooting

### Common Issues:

**Issue:** OOBC Staff user sees 403 on M&E module
**Solution:**
1. Verify user has `oobc-staff` role assigned
2. Check role has `monitoring_access` permission
3. Verify migration 0046 was applied

**Issue:** Executive cannot access MANA
**Solution:**
1. Verify user_type is `oobc_executive_director` or `oobc_deputy_executive_director`
2. Check executive role assignment
3. Verify role has `mana_access` permission

---

## Related Documentation

- **[MOA RBAC System](../moa/README.md)** - RBAC for Ministry/Office/Agency users
- **[RBAC Backend](../backend/)** - Backend implementation details
- **[RBAC Frontend](../frontend/)** - Frontend implementation details
- **[RBAC Architecture](../RBAC_ARCHITECTURE_REVIEW.md)** - System architecture overview

---

## Support

For questions or issues:
1. Review the **[Master Reference Guide](OOBC_RBAC_MASTER_REFERENCE.md)**
2. Check the **[Main RBAC README](../README.md)**
3. Contact: OBCMS Development Team

---

**System Status:** ✅ **PRODUCTION READY**
