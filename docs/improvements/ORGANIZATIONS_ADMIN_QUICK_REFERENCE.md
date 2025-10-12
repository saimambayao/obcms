# Organizations Admin Quick Reference

**Quick access guide for common admin operations**

---

## Quick Actions

### Create New Organization (MOA)

1. **Navigate:** Admin → Organizations → Organizations → Add
2. **Required Fields:**
   - Code (unique, 2-6 letters)
   - Name (full organization name)
   - Type (ministry/office/agency/special/commission)
3. **Recommended:**
   - Enable desired modules
   - Set active status
   - Add primary focal person
4. **Save**

### Add User to Organization

1. **Navigate:** Admin → Organizations → Organizations → [Select Org]
2. **Scroll to:** Organization Memberships section
3. **Click:** "Add another Organization Membership"
4. **Fill:**
   - User (autocomplete search)
   - Role (admin/manager/staff/viewer)
   - Check "Is primary" if default org
   - Position and department (optional)
5. **Save**

### Change User's Primary Organization

1. **Navigate:** Admin → Organization Memberships
2. **Search:** User's username
3. **Select:** Membership to make primary
4. **Action:** "Set as primary organization" → Go

### Bulk Activate Multiple Organizations

1. **Navigate:** Admin → Organizations → Organizations
2. **Select:** Organizations to activate (checkboxes)
3. **Action:** "Activate selected organizations" → Go

### Mark Organizations as Pilot

1. **Navigate:** Admin → Organizations → Organizations
2. **Select:** Organizations (e.g., MOH, MOLE, MAFAR)
3. **Action:** "Mark as pilot organizations" → Go

### Grant Administrator Access

1. **Navigate:** Admin → Organization Memberships
2. **Filter:** By organization and role
3. **Select:** Memberships to promote
4. **Action:** "Grant administrator role" → Go

---

## Search Tips

### Find Organization

**By Code:**
```
Search box: OOBC
```

**By Name:**
```
Search box: Ministry of Health
```

**By Type:**
```
Filter: Type → Ministry
```

### Find User Memberships

**By Username:**
```
Search box: admin
```

**By Email:**
```
Search box: admin@oobc.gov.ph
```

**By Organization:**
```
Filter: Organization → OOBC
```

---

## Bulk Operations

### Activate Multiple Organizations
```
Select orgs → Action: "Activate selected organizations" → Go
```

### Enable All Modules
```
Select orgs → Action: "Enable all modules" → Go
```

### Promote Multiple Users
```
Select memberships → Action: "Grant administrator role" → Go
```

### Deactivate Memberships
```
Select memberships → Action: "Deactivate selected memberships" → Go
```

---

## Visual Indicators

### Status Badges

| Color | Meaning |
|-------|---------|
| 🟢 Green | Active |
| ⚫ Gray | Inactive |
| 🟡 Gold | Pilot MOA |

### Module Badges

| Badge | Module |
|-------|--------|
| 🔵 Blue | MANA |
| 🟣 Purple | Planning |
| 🟢 Green | Budgeting |
| 🟠 Orange | M&E |
| 🩷 Pink | Coordination |
| 🔷 Cyan | Policies |

### Role Badges

| Color | Role |
|-------|------|
| 🔴 Red | Admin |
| 🟠 Orange | Manager |
| 🔵 Blue | Staff |
| ⚫ Gray | Viewer |

### Permission Icons

| Icon | Permission |
|------|------------|
| 👥 | Manage Users |
| 📋 | Approve Plans |
| 💰 | Approve Budgets |
| 📊 | View Reports |

---

## Security Notes

### OOBC Protection

⚠️ **OOBC cannot be:**
- Deleted
- Deactivated
- Code changed

✅ **Reason:** OOBC is the foundation organization and must always be active.

### Superuser Access

✅ **Only superusers** can access Organizations admin

🔐 **Future:** Organization admins will manage their own org

---

## Common Workflows

### Onboard New MOA

1. Create organization
2. Enable modules
3. Mark as pilot (if applicable)
4. Activate organization
5. Add admin user membership
6. Add staff memberships
7. Set onboarding/go-live dates

### Offboard Organization

1. Deactivate all memberships
2. Disable all modules
3. Deactivate organization
4. Document reason in notes

### User Role Change

1. Find membership
2. Edit membership
3. Change role
4. Update permissions
5. Save

### Transfer User Primary Org

1. Find all user memberships
2. Select new primary membership
3. Action: "Set as primary" → Go

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl/Cmd + S` | Save |
| `Ctrl/Cmd + K` | Focus search |
| `Alt + S` | Save and add another |
| `Alt + C` | Save and continue |

---

## Filters Cheat Sheet

### Organization Filters

- **Type:** Ministry, Office, Agency, Special, Commission
- **Status:** Active, Inactive
- **Pilot:** Yes, No
- **Modules:** By each module flag
- **Date:** Onboarding date range

### Membership Filters

- **Role:** Admin, Manager, Staff, Viewer
- **Primary:** Yes, No
- **Status:** Active, Inactive
- **Organization:** All 44 MOAs
- **Permissions:** By each permission flag
- **Date:** Joined date range

---

## Troubleshooting Quick Fixes

### CSS Not Loading
```bash
python manage.py collectstatic --noinput
# Clear browser cache
```

### Autocomplete Not Working
- Check search_fields defined
- Verify permissions

### Cannot Delete Organization
- Check if memberships exist
- Check OOBC protection

### Cannot Set Primary
- Select only ONE membership
- Ensure user has membership

---

## Contact & Support

**Documentation:** `docs/improvements/ORGANIZATIONS_ADMIN_INTERFACE.md`
**Task Breakdown:** `docs/plans/bmms/tasks/phase1_foundation_organizations.txt`
**BMMS Plan:** `docs/plans/bmms/TRANSITION_PLAN.md`

---

**Last Updated:** 2025-10-13
**Version:** 1.0
**Phase:** BMMS Phase 1 - Foundation
