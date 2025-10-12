# RBAC Admin Quick Reference

**Quick guide for staff managing RBAC through Django admin**

---

## Access Points

```
/admin/common/feature/          → Manage features (modules, menu items)
/admin/common/permission/       → Manage permissions (view, create, edit, etc.)
/admin/common/role/            → Manage roles (OOBC Admin, MOA Staff, etc.)
/admin/common/rolepermission/  → Manage role-permission assignments
/admin/common/userrole/        → Assign roles to users
/admin/common/userpermission/  → Grant direct permissions to users
```

---

## Common Tasks

### Create a New Feature

1. Go to `/admin/common/feature/`
2. Click "Add Feature"
3. Fill in:
   - **Feature Key**: Unique identifier (e.g., `communities.barangay_obc`)
   - **Name**: Display name (e.g., "Barangay OBC Management")
   - **Module**: App name (e.g., `communities`)
   - **Category**: Optional grouping (e.g., `navigation`)
   - **Parent**: For hierarchical menus (optional)
   - **Icon**: CSS class (e.g., `fa-users`)
   - **URL Pattern**: Route (e.g., `/communities/barangay/`)
   - **Sort Order**: Display order (lower = first)
4. Save

### Create Permissions for a Feature

1. Go to `/admin/common/permission/`
2. Click "Add Permission"
3. Fill in:
   - **Feature**: Select the feature
   - **Codename**: Action (e.g., `view`, `create`, `edit`, `delete`)
   - **Name**: Display name (e.g., "Can view barangay data")
   - **Permission Type**: Choose from dropdown (view, create, edit, delete, approve, export)
4. Save

**Standard Permissions Pattern:**
- `view` → View/Read access
- `create` → Add new items
- `edit` → Update existing items
- `delete` → Remove items
- `approve` → Authorize submissions
- `export` → Export data

### Create a Role

1. Go to `/admin/common/role/`
2. Click "Add Role"
3. Fill in:
   - **Name**: Role name (e.g., "OOBC Admin", "MOA Manager")
   - **Slug**: URL-friendly name (e.g., `oobc-admin`)
   - **Scope**: System-wide, Organization-specific, or Module-specific
   - **Level**: 1=Viewer, 2=Staff, 3=Manager, 4=Admin, 5=Super Admin
   - **Organization**: For org-specific roles (optional)
   - **Parent Role**: For permission inheritance (optional)
4. **Add Permissions** (Inline):
   - Click "Add another Role Permission"
   - Select Permission
   - Grant or Deny
   - Set conditions (JSON, optional)
   - Set expiration (optional)
5. Save

**Tips:**
- Use parent roles to inherit permissions
- Mark as "System Role" to prevent deletion
- Organization-scoped roles require organization selection

### Assign Role to User

1. Go to `/admin/common/userrole/`
2. Click "Add User Role"
3. Fill in:
   - **User**: Search and select user (raw ID field - enter user ID)
   - **Role**: Select role
   - **Organization**: Required for org-scoped roles
   - **Expires At**: Optional expiration date
4. Save

**Auto-filled:**
- `assigned_by` → Current admin user
- `assigned_at` → Current timestamp

### Grant Direct Permission

1. Go to `/admin/common/userpermission/`
2. Click "Add User Permission"
3. Fill in:
   - **User**: Search and select user (raw ID field)
   - **Permission**: Select permission
   - **Organization**: For org-scoped permissions (optional)
   - **Grant/Deny**: Choose action
   - **Reason**: REQUIRED - explain why (audit trail)
   - **Expires At**: Optional expiration date
4. Save

**Use Cases:**
- Emergency access grants
- One-off permissions
- Override role permissions (deny)
- Temporary elevated access

---

## Admin Features

### Clickable Count Links

**Feature Admin:**
- **Sub-features** → Click to see child features

**Permission Admin:**
- **Roles** → Click to see roles using this permission

**Role Admin:**
- **Users** → Click to see users with this role
- **Permissions** → Click to see role permissions

### Filter Options

**Feature:**
- Category, Module, Active, Parent, Organization

**Permission:**
- Type, Active, Feature Category, Feature Module

**Role:**
- Scope, Level, Active, System Role, Organization

**UserRole:**
- Active, Role, Organization, Assigned Date, Expiration

**UserPermission:**
- Grant/Deny, Active, Feature, Organization, Assigned Date, Expiration

### Search

**Feature:** Name, Feature Key, Description, Module, Category

**Permission:** Name, Codename, Description, Feature Name, Feature Key

**Role:** Name, Slug, Description

**UserRole:** User (username, name, email), Role Name

**UserPermission:** User (username, name, email), Permission Name/Codename, Reason

---

## Security Features

### System Role Protection

**Cannot delete system roles:**
- Individual delete → ValidationError
- Bulk delete → Excludes system roles + warning message

**How to identify:**
- "System Role" column = Yes
- Checkbox in admin form

### Auto-Population

**Automatically set by system:**
- `created_by` → Who created the role
- `assigned_by` → Who assigned the user role
- `granted_by` → Who granted the permission

**You don't need to fill these!**

### Validation Rules

**UserRole:**
- Org-scoped roles MUST have organization
- System roles CANNOT have organization
- Expiration must be in future

**UserPermission:**
- Reason field REQUIRED (for audit)
- Expiration must be in future

**Role:**
- Cannot be own parent (prevents circular refs)
- System roles cannot be org-scoped

---

## Common Workflows

### Setting Up OOBC Admin Role

1. **Create Features** (if not exist):
   - Dashboard, Communities, MANA, Coordination, etc.
2. **Create Permissions** for each feature:
   - view, create, edit, delete, approve, export
3. **Create Role**:
   - Name: "OOBC Admin"
   - Scope: System-wide
   - Level: 4 (Admin)
   - System Role: Yes
4. **Add Permissions** (inline):
   - Select all permissions
   - Grant: Yes
   - Active: Yes
5. **Assign to Users**:
   - Go to UserRole
   - Add user + OOBC Admin role
   - No organization (system-wide)

### Setting Up MOA Staff Role

1. **Create Role**:
   - Name: "MOA Staff"
   - Scope: Organization-specific
   - Level: 2 (Staff)
   - Organization: Select MOA
2. **Add Permissions** (inline):
   - Own MOA data: view, create, edit
   - Communities: view only
   - MANA: no access
3. **Assign to Users**:
   - Go to UserRole
   - Add user + MOA Staff role
   - Organization: Same MOA

### Granting Emergency Access

1. **Go to UserPermission**
2. **Add User Permission**:
   - User: Select user
   - Permission: Select what they need
   - Grant: Yes
   - Reason: "Emergency access for budget approval deadline"
   - Expires At: Set to 24 hours from now
3. **Save**

**Note:** Direct permissions override role permissions

---

## Troubleshooting

### "An admin for model 'User' has to be registered"

**Cause:** Autocomplete fields referencing User model before registration
**Solution:** Already fixed - we use raw_id_fields for User

### Cannot Delete System Role

**Cause:** System roles are protected
**Solution:** Either:
1. Uncheck "System Role" first, then delete (if safe)
2. Leave as-is (system roles should not be deleted)

### Role Without Permissions Shows "0 permissions"

**Check:**
1. Are permissions granted and active?
2. Is role active?
3. Check RolePermission inline in Role edit page

### User Role Not Working

**Check:**
1. Is UserRole active?
2. Is Role active?
3. Is UserRole expired?
4. Does org-scoped role have correct organization?
5. Are role permissions granted (not denied)?

---

## Best Practices

### Naming Conventions

**Features:**
- Key: `app.feature_name` (e.g., `communities.barangay_obc`)
- Name: Human-readable (e.g., "Barangay OBC Management")

**Permissions:**
- Codename: action (e.g., `view`, `create`, `edit`)
- Name: Full description (e.g., "Can view barangay data")

**Roles:**
- Name: Clear title (e.g., "OOBC Admin", "MOA Manager")
- Slug: lowercase-with-dashes (e.g., `oobc-admin`)

### Permission Granularity

**Too Broad:**
- ❌ `app.all` → Can do everything
- ❌ `manage` → Too vague

**Just Right:**
- ✅ `view`, `create`, `edit`, `delete` → Clear actions
- ✅ `approve`, `export` → Specific operations

### Role Hierarchy

Use parent roles for inheritance:

```
OOBC Admin (parent=None)
  ├── OOBC Manager (parent=OOBC Admin)
  │   ├── OOBC Staff (parent=OOBC Manager)
  │   └── OOBC Viewer (parent=OOBC Manager)
  └── OCM Analyst (parent=OOBC Admin) [read-only]
```

**Benefits:**
- Managers inherit admin permissions
- Easy to maintain
- Consistent access levels

### Audit Trail

**Always provide reason for:**
- Direct user permissions
- Permission denials
- Temporary access grants

**Example Reasons:**
- "Emergency budget approval access"
- "Temporary MOA focal assignment"
- "Override for system integration testing"
- "Denied per security policy"

---

## Next Steps

**After Admin Setup:**
1. Seed default features (navbar items)
2. Seed default permissions (CRUD operations)
3. Create standard roles (OOBC Admin, MOA Staff, etc.)
4. Assign roles to users
5. Test permission enforcement in views
6. Update templates with permission checks

**See:**
- Full Documentation: `docs/improvements/RBAC_DJANGO_ADMIN_IMPLEMENTATION.md`
- RBAC Design: `docs/improvements/MOA_RBAC_DESIGN.md`
- Navbar Analysis: `docs/improvements/NAVBAR_RBAC_ANALYSIS.md`
