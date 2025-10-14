# BMMS Embedded Architecture - Quick Reference Card

**Print this for your desk!**

---

## 🔴 CRITICAL: Pre-Implementation Required

**⚠️ STOP: Complete Phase -1 reconciliation BEFORE using this guide**

### Must Fix Before Implementation (2 hours)

1. **🔴 Fix Organization Import** (5 min)
   ```python
   # Line 44 in common/middleware/organization_context.py
   # CHANGE: from coordination.models import Organization
   # TO:     from organizations.models import Organization
   ```

2. **🔴 Add BMMS_MODE Configuration** (15 min)
   ```bash
   # Add to .env:
   BMMS_MODE=obcms
   DEFAULT_ORGANIZATION_CODE=OOBC

   # Create: src/obc_management/settings/bmms_config.py
   ```

3. **🟡 Audit ENABLE_MULTI_TENANT** (30 min)
   ```python
   # Line 638 in base.py: Currently defaults to True
   # MUST CHANGE to mode-dependent default
   ```

4. **🔴 Resolve Middleware Conflict** (1 hour)
   ```
   Existing:  OrganizationContextMiddleware (line 133)
   Planned:   OBCMSOrganizationMiddleware + OrganizationMiddleware
   Decision:  Choose refactor existing vs replace
   ```

**See:** [RECONCILIATION_PLAN.md](./RECONCILIATION_PLAN.md) for detailed fixes

**Once Phase -1 is complete, proceed with this guide. ✅**

---

## 🎯 Core Principle

**One Codebase, Two Modes, Zero Code Changes to Switch**

```
.env.obcms  →  OBCMS Mode (Single-tenant OOBC)
.env.bmms   →  BMMS Mode (Multi-tenant 44 MOAs)
```

---

## 🔧 Configuration (settings/base.py)

```python
# Mode selection
BMMS_MODE = env.str('BMMS_MODE', default='obcms')  # or 'bmms'
DEFAULT_ORGANIZATION_CODE = 'OOBC'

# Auto-adjusts based on mode
ENABLE_MULTI_TENANT = (BMMS_MODE == 'bmms')
ALLOW_ORGANIZATION_SWITCHING = (BMMS_MODE == 'bmms')
```

---

## 📁 Model Pattern

### ❌ Before (Single-tenant)
```python
class OBCCommunity(models.Model):
    name = models.CharField(max_length=255)
    # No organization field
```

### ✅ After (BMMS-ready)
```python
from organizations.models import OrganizationScopedModel

class OBCCommunity(OrganizationScopedModel):
    name = models.CharField(max_length=255)
    # organization field inherited
    # objects = auto-filtered manager
    # all_objects = unfiltered manager
```

---

## 🎨 View Pattern

### ❌ Before
```python
@login_required
def community_list(request):
    communities = OBCCommunity.objects.all()
    return render(request, 'list.html', {'communities': communities})
```

### ✅ After
```python
from common.decorators.organization import require_organization

@login_required
@require_organization  # NEW
def community_list(request):
    # Auto-filtered to request.organization
    communities = OBCCommunity.objects.all()
    return render(request, 'list.html', {
        'communities': communities,
        'organization': request.organization,  # NEW
    })
```

---

## 🔄 Three-Step Migration

```bash
# Step 1: Add nullable field
python manage.py makemigrations app_name
python manage.py migrate app_name

# Step 2: Populate field
python manage.py populate_organization_field --app app_name

# Step 3: Make required
python manage.py makemigrations app_name
python manage.py migrate app_name
```

---

## 🌐 URL Patterns

### OBCMS Mode
```
/communities/              → Community list
/mana/assessments/         → Assessment list
```

### BMMS Mode
```
/moa/OOBC/communities/     → OOBC communities
/moa/MOH/mana/assessments/ → MOH assessments
```

---

## 🧪 Testing

```bash
# OBCMS mode
BMMS_MODE=obcms pytest

# BMMS mode
BMMS_MODE=bmms pytest

# Specific test
pytest src/communities/tests/test_organization_scoping.py
```

---

## 🔍 Debugging

### Check current mode
```python
from obc_management.settings.bmms_config import *
is_obcms_mode()  # True or False
is_bmms_mode()   # True or False
```

### Check organization context
```python
from organizations.models.scoped import get_current_organization
org = get_current_organization()
print(org.code if org else "No org")
```

### Bypass organization filter
```python
# Auto-filtered (normal)
communities = OBCCommunity.objects.all()

# Unfiltered (admin/OCM)
all_communities = OBCCommunity.all_objects.all()
```

---

## 🚨 Common Errors

### "Organization context required"
**Fix:** Check middleware ordering
```python
MIDDLEWARE = [
    # ...
    "organizations.middleware.obcms_middleware.OBCMSOrganizationMiddleware",  # FIRST
    "organizations.middleware.OrganizationMiddleware",  # SECOND
]
```

### "Organization field cannot be null"
**Fix:** Run Step 2 before Step 3
```bash
python manage.py populate_organization_field --app app_name
```

### Queries return no results
**Fix:** Check organization context
```python
from organizations.models.scoped import set_current_organization
from organizations.utils import get_default_organization
set_current_organization(get_default_organization())
```

---

## ⚡ Management Commands

```bash
# Ensure OOBC org exists
python manage.py ensure_default_organization

# Populate organization field
python manage.py populate_organization_field [--app APP] [--model MODEL]

# Dry run
python manage.py populate_organization_field --dry-run
```

---

## 📊 Validation Checklist

- [ ] Default OOBC organization exists
- [ ] All models have organization field
- [ ] All records have organization assigned (no NULL)
- [ ] Auto-filtering works (Model.objects.all())
- [ ] Views have @require_organization decorator
- [ ] Templates access {{ organization }}
- [ ] Tests pass in OBCMS mode
- [ ] Tests pass in BMMS mode
- [ ] URLs work in both modes

---

## 🎓 Key Files

```
src/
├── obc_management/settings/
│   └── bmms_config.py                 # Mode utilities
├── organizations/
│   ├── middleware/obcms_middleware.py # OBCMS auto-inject
│   ├── models/scoped.py               # Base class
│   └── utils/__init__.py              # Utilities
└── common/decorators/
    └── organization.py                # View decorators
```

---

## 🔐 Security Rules

1. **Organization Isolation:** Each MOA sees ONLY their data
2. **Auto-Filtering:** Enforced at database level (manager)
3. **View Validation:** @require_organization checks access
4. **OCM Exception:** Read-only access to all orgs
5. **Superuser Exception:** Full access to all orgs

---

## 💡 Pro Tips

1. **Use all_objects sparingly** - only for admin/OCM views
2. **Test both modes** - add fixtures for obcms_mode and bmms_mode
3. **Check organization context** - always verify request.organization exists
4. **Use thread-local cleanup** - middleware handles this automatically
5. **Backup before migrating** - three-step process is safe but backup anyway

---

## 📚 Documentation Links

- **Full Implementation Plan:** [BMMS_EMBEDDED_ARCHITECTURE_IMPLEMENTATION.md](./BMMS_EMBEDDED_ARCHITECTURE_IMPLEMENTATION.md)
- **Implementation Summary:** [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)
- **Architecture Diagrams:** [ARCHITECTURE_DIAGRAMS.md](./ARCHITECTURE_DIAGRAMS.md)
- **BMMS Transition Plan:** [../TRANSITION_PLAN.md](../TRANSITION_PLAN.md)

---

## 🚀 Quick Start

```bash
# 1. Create feature branch
git checkout -b feature/bmms-embedded-architecture

# 2. Backup database
cp src/db.sqlite3 src/db.sqlite3.backup

# 3. Start with Phase 1
# See IMPLEMENTATION_SUMMARY.md for phase details

# 4. Test continuously
pytest --cov=src

# 5. Validate
python manage.py check --deploy
```

---

**Version:** 1.1
**Updated:** 2025-10-14 (Post-Audit)
**Status:** ⚠️ REQUIRES PHASE -1 RECONCILIATION BEFORE IMPLEMENTATION

---

## ☎️ Need Help?

1. Check [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) for detailed steps
2. Review [ARCHITECTURE_DIAGRAMS.md](./ARCHITECTURE_DIAGRAMS.md) for visual explanations
3. See [BMMS_EMBEDDED_ARCHITECTURE_IMPLEMENTATION.md](./BMMS_EMBEDDED_ARCHITECTURE_IMPLEMENTATION.md) for complete specifications
4. Refer to [CLAUDE.md](../../../CLAUDE.md) for project guidelines
