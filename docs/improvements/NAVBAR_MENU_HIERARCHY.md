# OBCMS Navbar Menu Hierarchy

**Visual Reference for RBAC Design**

---

## Menu Structure Tree

```
🏛️ OBCMS Navbar
│
├── 🏠 Dashboard (Logo)
│   └── URL: common:dashboard
│   └── Permission: Authenticated only
│
├── 👤 User Profile Menu (Right Corner)
│   ├── 👤 Profile → common:profile
│   ├── 🔧 Admin Panel → /admin/ (staff only)
│   └── 🚪 Logout → common:logout
│
└── 📋 Main Navigation
    │
    ├── 🔒 RESTRICTED MENU (MANA Participants/Facilitators Only)
    │   ├── Condition: perms.mana.can_access_regional_mana
    │   ├── 🏴 Provincial OBC → communities:communities_manage_provincial
    │   ├── 🗺️ Regional MANA → mana:mana_regional_overview
    │   └── 👨‍🏫 Facilitator Dashboard → mana:mana_manage_assessments
    │       └── Condition: perms.mana.can_facilitate_workshop
    │
    └── 📋 STANDARD MENU (OOBC Staff & MOA Users)
        │
        ├── 🏢 MOA Profile (MOA Focal Users Only)
        │   └── Condition: is_moa_focal_user_filter
        │   └── URL: Dynamic → /coordination/organizations/{moa_id}/
        │
        ├── 👥 OBC Data (Dropdown)
        │   ├── Permission: All authenticated
        │   ├── 📍 Barangay OBCs → communities:communities_manage
        │   ├── 🏙️ Municipal OBCs → communities:communities_manage_municipal
        │   ├── 🏴 Provincial OBCs → communities:communities_manage_provincial
        │   └── 🗺️ Geographic Data → mana:mana_geographic_data
        │       └── Condition: can_access_geographic_data (OOBC staff + superuser)
        │
        ├── 🗺️ MANA (Dropdown)
        │   ├── Permission: can_access_mana_filter (OOBC staff + superuser)
        │   ├── 🌏 Regional MANA → mana:mana_regional_overview
        │   ├── 🗺️ Provincial MANA → mana:mana_provincial_overview
        │   ├── 📖 Desk Review → mana:mana_desk_review
        │   ├── 📋 Survey → mana:mana_survey_module
        │   └── 💬 Key Informant Interview → mana:mana_kii
        │
        ├── 🤝 Coordination (Dropdown)
        │   ├── Permission: NOT is_moa_focal_user (OOBC staff only)
        │   ├── 👥 Mapped Partners → coordination:organizations
        │   ├── 📄 Partnership Agreements → coordination:partnerships
        │   └── 📅 Coordination Activities → coordination:events
        │
        ├── ⚖️ Recommendations (Dropdown)
        │   ├── Permission: can_access_policies (OOBC + MOA staff)
        │   ├── ⚖️ Policies → policies:manage
        │   ├── 📊 Systematic Programs → policies:programs
        │   └── 🔔 Services → policies:services
        │
        ├── 📊 M&E (Dropdown)
        │   ├── Permission: All authenticated
        │   ├── 📄 MOA PPAs → monitoring:moa_ppas
        │   ├── 💚 OOBC Initiatives → monitoring:oobc_initiatives
        │   │   └── Condition: can_access_oobc_initiatives (OOBC staff + superuser)
        │   ├── 📝 OBC Requests → monitoring:obc_requests
        │   └── 📈 M&E Analytics → project_central:me_analytics_dashboard
        │       └── Condition: can_access_me_analytics (OOBC staff + superuser)
        │
        └── 🧰 OOBC Management (Dropdown)
            ├── Permission: can_access_oobc_management (OOBC staff + superuser)
            ├── 👨‍💼 Staff Management → common:staff_management
            ├── ✅ Work Items → common:work_item_list
            ├── 📝 Planning & Budgeting → common:planning_budgeting
            ├── 📅 Calendar Management → common:oobc_calendar
            ├── 📊 Project Management Portal → project_central:portfolio_dashboard
            └── ✓ User Approvals → common:user_approvals
                └── Condition: Complex position check (Executive Dir, DMO, etc.)
```

---

## Permission Matrix

### User Type vs Menu Access

| Menu Item | Admin | OOBC Executive | OOBC Staff | MOA Staff | MANA Participant | Community Leader |
|-----------|:-----:|:--------------:|:----------:|:---------:|:----------------:|:----------------:|
| **Dashboard** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **OBC Data** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| └ Geographic Data | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **MANA** | ✅ | ✅ | ✅ | ❌ | ✅* | ❌ |
| **Coordination** | ✅ | ✅ | ✅ | ❌** | ❌ | ❌ |
| **MOA Profile** | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **Recommendations** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **M&E** | ✅ | ✅ | ✅ | ✅*** | ✅*** | ✅*** |
| └ OOBC Initiatives | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| └ M&E Analytics | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **OOBC Management** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| └ User Approvals | ✅ | ✅ | ✅**** | ❌ | ❌ | ❌ |

**Legend:**
- ✅ Full Access
- ✅* Limited view (via Django permissions)
- ✅** See MOA Profile instead
- ✅*** Only see MOA PPAs and OBC Requests
- ✅**** Only specific positions
- ❌ No Access

---

## Permission Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Authentication                       │
│                   is_authenticated = True                    │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │   Check User Type   │
                    └─────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
    ┌─────────────┐  ┌──────────────┐  ┌─────────────┐
    │ OOBC Staff  │  │  MOA Staff   │  │    Other    │
    │ (Staff/Exec)│  │ (BMOA/LGU/   │  │ (Community, │
    │             │  │     NGA)     │  │  Researcher)│
    └─────────────┘  └──────────────┘  └─────────────┘
           │                 │                  │
           ▼                 ▼                  ▼
    ┌─────────────┐  ┌──────────────┐  ┌─────────────┐
    │ Full Menu   │  │   Limited    │  │  Restricted │
    │ - MANA      │  │   Menu       │  │    Menu     │
    │ - Coord     │  │ - MOA Profile│  │ - Provincial│
    │ - OOBC Mgt  │  │ - OBC Data   │  │   OBC Only  │
    │ - M&E Full  │  │ - Recomm     │  │ - Regional  │
    │             │  │ - M&E Partial│  │   MANA      │
    └─────────────┘  └──────────────┘  └─────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  Check Approval     │
                    │  is_approved = ?    │
                    └─────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
            ┌───────────────┐   ┌──────────────┐
            │   Approved    │   │ Not Approved │
            │  Show Menus   │   │ Redirect to  │
            │               │   │ Approval Page│
            └───────────────┘   └──────────────┘
```

---

## Django Permission Groups (Current MANA Only)

```
mana.WorkshopParticipantAccount
│
├── can_access_regional_mana
│   └── Used by: Restricted menu visibility
│
├── can_view_provincial_obc
│   └── Used by: (Not currently in navbar)
│
└── can_facilitate_workshop
    └── Used by: Facilitator Dashboard menu item
```

---

## Custom Template Filter Dependencies

```
moa_rbac.py Template Tags
│
├── is_moa_focal_user_filter(user)
│   ├── Checks: is_moa_staff + is_approved + moa_organization
│   └── Used by: MOA Profile menu visibility
│
├── can_access_mana_filter(user)
│   ├── Checks: is_superuser OR is_oobc_staff
│   └── Used by: MANA dropdown visibility
│
├── can_access_geographic_data(user)
│   ├── Checks: is_superuser OR is_oobc_staff
│   └── Used by: Geographic Data submenu item
│
├── can_access_oobc_initiatives(user)
│   ├── Checks: is_superuser OR is_oobc_staff
│   └── Used by: OOBC Initiatives submenu item
│
├── can_access_me_analytics(user)
│   ├── Checks: is_superuser OR is_oobc_staff
│   └── Used by: M&E Analytics submenu item
│
├── can_access_oobc_management(user)
│   ├── Checks: is_superuser OR is_oobc_staff
│   └── Used by: OOBC Management dropdown visibility
│
├── can_access_policies(user)
│   ├── Checks: is_superuser OR is_oobc_staff OR is_moa_staff
│   └── Used by: Recommendations dropdown visibility
│
├── get_coordination_label(user)
│   ├── Returns: "MOA Profile" if MOA staff, else "Coordination"
│   └── Used by: Dynamic menu label
│
└── get_coordination_url(user)
    ├── Returns: Dynamic URL based on user type
    └── Used by: Dynamic menu link
```

---

## User Model Permission Methods

```
User Model (common.models.User)
│
├── @property is_oobc_staff
│   └── Returns: user_type in ["oobc_staff", "oobc_executive"]
│
├── @property is_moa_staff
│   └── Returns: user_type in ["bmoa", "lgu", "nga"]
│
├── owns_moa_organization(organization)
│   └── Returns: True if user's moa_organization matches
│
├── can_edit_ppa(ppa)
│   ├── Superuser/OOBC staff: Always True
│   └── MOA staff: True if ppa.implementing_moa == user.moa_organization
│
├── can_view_ppa(ppa)
│   ├── Superuser/OOBC staff: Always True
│   └── MOA staff: True if ppa.implementing_moa == user.moa_organization
│
├── can_delete_ppa(ppa)
│   ├── Superuser/OOBC Executive: Always True
│   ├── OOBC Staff: True if NOT GAAB-funded
│   └── MOA staff: True if NOT GAAB-funded AND owns PPA
│
└── can_edit_work_item(work_item)
    ├── Superuser/OOBC staff: Always True
    └── MOA staff: True if work_item.related_ppa belongs to user's MOA
```

---

## BMMS Enhancement Roadmap

### 1. Replace User Type Checks with Role-Based Permissions

**Before:**
```python
if user.is_oobc_staff:
    # Show menu
```

**After:**
```python
if user.has_perm('bmms.access_oobc_management'):
    # Show menu
```

### 2. Add Organization Context to All Checks

**Before:**
```python
ppas = PPA.objects.all()
```

**After:**
```python
ppas = PPA.objects.filter(implementing_moa=request.user.organization)
```

### 3. Implement Module Toggles

**New Model:**
```python
class OrganizationModuleConfig:
    organization = ForeignKey(Organization)
    module_name = CharField(choices=MODULE_CHOICES)
    is_enabled = BooleanField(default=True)
```

**Usage:**
```python
if user.organization.module_enabled('mana'):
    # Show MANA menu
```

---

## File Reference Quick Links

| File | Purpose |
|------|---------|
| `/src/templates/common/navbar.html` | Main navbar template |
| `/src/common/templatetags/moa_rbac.py` | Permission template tags |
| `/src/common/models.py` | User model & permission methods |
| `/src/mana/models.py` | MANA Django permissions |

---

## Next Steps

1. ✅ **Analysis Complete** - This document
2. ⏭️ **Design RBAC System** - Create permission groups & roles
3. ⏭️ **Implement Organization Context** - Add middleware & managers
4. ⏭️ **Update Navbar** - Replace type checks with role checks
5. ⏭️ **Add Module Toggles** - Create OrganizationModuleConfig
6. ⏭️ **Test & Validate** - Comprehensive permission testing

---

**Document Status:** Complete ✅
**Last Updated:** 2025-10-13
**Related Docs:**
- [NAVBAR_RBAC_ANALYSIS.md](./NAVBAR_RBAC_ANALYSIS.md) - Detailed analysis
- [BMMS Transition Plan](../plans/bmms/TRANSITION_PLAN.md) - Overall BMMS strategy
