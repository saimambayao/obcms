# RBAC (Role-Based Access Control) Documentation Index

Complete documentation for the OBCMS RBAC system implementation.

## 📚 **Quick Navigation**

### **System Overview**
- **[Complete System Overview](RBAC_COMPLETE_SYSTEM_OVERVIEW.md)** 🎯 - Visual diagrams, feature matrix, and complete architecture

### **User-Specific RBAC Documentation**
- **[OOBC Staff & Executive RBAC](oobc/README.md)** ⭐ - Complete RBAC guide for OOBC users (Staff, Deputy Director, Executive Director)
- **[MOA Focal Person RBAC](moa/README.md)** ⭐ - Complete RBAC guide for 44 MOA focal persons

### **Getting Started**
- [RBAC Quick Reference](implementation/RBAC_QUICK_REFERENCE.md) - Quick access to all RBAC features
- [OOBC Staff Implementation Summary](implementation/OOBC_STAFF_RBAC_IMPLEMENTATION_SUMMARY.md) - OOBC Staff restrictions and access levels

### **Architecture**
- [RBAC Architecture Review](architecture/RBAC_ARCHITECTURE_REVIEW.md) - Comprehensive technical review (9.4/10 rating)
- [Architecture Review Summary](architecture/RBAC_ARCHITECTURE_REVIEW_SUMMARY.md) - Executive summary

### **Backend Implementation**
- [Backend Implementation Complete](backend/RBAC_BACKEND_IMPLEMENTATION_COMPLETE.md) - All 16 views implementation report
- [Backend Views Quick Reference](backend/RBAC_BACKEND_QUICK_REFERENCE.md) - Code examples and usage
- [Admin Interface Implementation](backend/RBAC_DJANGO_ADMIN_IMPLEMENTATION.md) - Django admin integration
- [Admin Quick Reference](backend/RBAC_ADMIN_QUICK_REFERENCE.md) - Admin usage guide

### **Frontend Implementation**
- [Frontend Implementation Complete](frontend/RBAC_FRONTEND_IMPLEMENTATION_COMPLETE.md) - UI implementation report
- [Frontend Visual Guide](frontend/RBAC_FRONTEND_VISUAL_GUIDE.md) - Screenshots and UI patterns
- [HTMX Critical Fixes Complete](frontend/RBAC_HTMX_CRITICAL_FIXES_COMPLETE.md) - Fixed instant UI issues
- [User Approvals Access Level UI](frontend/USER_APPROVALS_ACCESS_LEVEL_UI_UPDATE.md) - Access matrix UI
- [Navbar RBAC Analysis](frontend/NAVBAR_RBAC_ANALYSIS.md) - Navigation protection

### **Performance Optimization**
- [Performance Optimization Complete](performance/RBAC_PERFORMANCE_OPTIMIZATION_COMPLETE.md) - Cache, rate limiting, N+1 fixes
- [Performance Visual Metrics](performance/RBAC_PERFORMANCE_VISUAL_METRICS.md) - Before/after metrics
- [Performance Summary](performance/RBAC_PERFORMANCE_SUMMARY.md) - Executive summary

### **Implementation Phases**
- [Phase 1: Foundation Complete](implementation/PHASE1_RBAC_FOUNDATION_COMPLETE.md) - Core RBAC models and services
- [Phase 2: View Protection Complete](implementation/PHASE2_RBAC_VIEW_PROTECTION_COMPLETE.md) - Decorator implementation
- [Phase 3: Template Tags Summary](implementation/PHASE3_RBAC_TEMPLATE_TAGS_SUMMARY.md) - Template-level protection

### **Multi-Tenant (MOA) Documentation** _(Legacy - See User-Specific sections above)_
- [MOA-Specific RBAC Docs](moa-specific/) - Legacy MOA documentation (migrated to `moa/` directory)

---

## 🎯 **System Overview**

### What is RBAC?
Role-Based Access Control (RBAC) is a security framework that restricts system access based on user roles. In OBCMS:

- **Features** → Groups of related permissions (e.g., "MANA Access", "Monitoring Access")
- **Permissions** → Specific actions (e.g., "view", "edit", "delete")
- **Roles** → Collections of permissions (e.g., "OOBC Staff", "MOA Staff", "Executive Director")
- **Users** → Assigned one or more roles

### User Types & Access Levels

#### **OOBC Users (Office Staff & Executives)**

**✅ OOBC Staff CAN Access:**
- OBC Data (Communities Management)
- Coordination & Events
- M&E (Monitoring & Evaluation)
- OOBC Management (Calendar, Work Items, Staff Profiles)

**❌ Executive-Only Modules:**
- MANA Assessments
- Policy Recommendations
- Planning & Budgeting
- Project Management Portal
- User Approvals
- RBAC Management

**📚 Full Documentation:** [OOBC RBAC Guide](oobc/README.md)

#### **MOA Users (Ministry/Office/Agency Focal Persons)**

**✅ MOA Staff CAN Access:**
- Their Own Organization Profile (full CRUD)
- Their Own MOA PPAs (create, manage)
- Their Own Work Items (manage tasks)
- OBC Data (view-only)
- M&E Module (filtered to own MOA)

**❌ MOA Staff CANNOT Access:**
- Other MOAs' data (complete isolation)
- MANA Assessments
- Policy Recommendations
- Strategic planning modules

**📚 Full Documentation:** [MOA RBAC Guide](moa/README.md)

---

## 📊 **Implementation Status**

| Component | Status | Files |
|-----------|--------|-------|
| **Data Models** | ✅ Complete | `src/common/rbac_models.py` |
| **Service Layer** | ✅ Complete | `src/common/services/rbac_service.py` |
| **View Decorators** | ✅ Complete | `src/common/decorators/rbac.py` |
| **Template Tags** | ✅ Complete | `src/common/templatetags/rbac_tags.py` |
| **Admin Interface** | ✅ Complete | `src/common/admin/rbac_admin.py` |
| **Backend Views** | ✅ Complete | `src/common/views/rbac_management.py` (16 views) |
| **Frontend UI** | ✅ Complete | `src/templates/common/rbac/` |
| **HTMX Fixes** | ✅ Complete | OOB swaps, modal lifecycle, error handling |
| **Performance** | ✅ Complete | Cache invalidation, rate limiting, N+1 fixes |
| **OOBC RBAC** | ✅ Complete | 3 roles, 7 features, full navigation filtering |
| **MOA RBAC** | ✅ Complete | 44 MOA accounts, data isolation, monitoring access |

---

## 🚀 **Quick Start Guide**

### 1. Run Migrations
```bash
cd src/
python manage.py migrate common
```

### 2. Assign Roles to Users
```python
from django.contrib.auth import get_user_model
from common.rbac_models import Role, UserRole

User = get_user_model()

# Get roles
staff_role = Role.objects.get(slug='oobc-staff')
executive_role = Role.objects.get(slug='oobc-executive-director')

# Assign to staff
for user in User.objects.filter(position='Staff'):
    UserRole.objects.get_or_create(user=user, role=staff_role)

# Assign to executive
executive = User.objects.get(position='Executive Director')
UserRole.objects.get_or_create(user=executive, role=executive_role)
```

### 3. Protect Views
```python
from common.decorators.rbac import require_feature_access

@require_feature_access('mana_access')
def mana_dashboard(request):
    return render(request, 'mana/dashboard.html')
```

### 4. Use in Templates
```django
{% load rbac_tags %}

{% has_feature_access request user 'mana_access' as can_access_mana %}
{% if can_access_mana %}
    <a href="{% url 'mana:dashboard' %}">MANA Dashboard</a>
{% endif %}
```

---

## 📈 **Performance Metrics**

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Database queries (10 roles) | 11 | 4 | **64% reduction** |
| First page load | 800ms | 150ms | **81% faster** |
| Cached page load | 800ms (stale) | 20ms | **97% faster** |
| Cache hit rate | 0% (broken) | 90-98% | **∞% better** |

---

## 🔒 **Security Features**

- ✅ **Organization-based data isolation** (MOA A cannot see MOA B)
- ✅ **Rate limiting** on sensitive endpoints
- ✅ **Audit logging** for all RBAC operations
- ✅ **Cache invalidation** after role/permission changes
- ✅ **Multi-layer protection** (auth → decorator → org context → model validation)
- ✅ **Fail-secure defaults** (users without roles have NO access)

---

## 🧪 **Testing**

### Run Unit Tests
```bash
cd src/
python manage.py test common.tests.test_rbac_decorators
python manage.py test common.tests.test_rbac_templatetags
python manage.py test common.tests.test_oobc_staff_rbac
```

### Browser Testing Checklist
- [ ] OOBC Staff: Verify NO access to 5 restricted modules
- [ ] Executive: Verify FULL access to all modules
- [ ] Navbar visibility based on role
- [ ] User approvals access matrix displays correctly
- [ ] HTMX instant UI updates work (no full page reloads)
- [ ] Modal lifecycle (loading spinner, no flicker)
- [ ] Error toasts show for failed operations

---

## 📞 **Support**

For questions or issues:
1. Check [RBAC Quick Reference](implementation/RBAC_QUICK_REFERENCE.md) first
2. Review relevant section documentation above
3. Check code comments in `src/common/rbac_models.py`
4. Contact development team

---

**Last Updated:** October 13, 2025
**Version:** 2.0.0
**Status:** ✅ Production-Ready (OOBC & MOA RBAC Complete)
