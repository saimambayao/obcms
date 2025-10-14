# BMMS Administrator Training Guide

**Target Audience:** System Administrators in BARMM Ministries, Offices, and Agencies (MOAs)
**Document Version:** 1.0
**Last Updated:** 2025-10-14

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Role Overview](#2-role-overview)
3. [Getting Started](#3-getting-started)
4. [User Management](#4-user-management)
5. [Role Assignments](#5-role-assignments)
6. [Organization Settings](#6-organization-settings)
7. [Module Enablement](#7-module-enablement)
8. [Approval Workflows Configuration](#8-approval-workflows-configuration)
9. [Security and Access Controls](#9-security-and-access-controls)
10. [Audit Logs Review](#10-audit-logs-review)
11. [Troubleshooting](#11-troubleshooting)
12. [Best Practices](#12-best-practices)

---

## 1. Introduction

### 1.1 Purpose of This Guide

This comprehensive guide empowers BMMS Administrators to effectively manage their organization's BMMS instance. From user management to security configuration, this guide provides step-by-step instructions for all administrative responsibilities.

### 1.2 About BMMS Administration

BMMS (Bangsamoro Ministerial Management System) is a multi-tenant platform serving 44 MOAs. As an Administrator, you manage:
- User accounts and access for your MOA only
- Organization-specific settings and configurations
- Module activation and permissions
- Security policies and access controls
- Audit logs and compliance monitoring

**Important:** You manage ONLY your organization's instance. You cannot access or modify other MOAs' data or settings.

### 1.3 Prerequisites

Before using this guide, ensure you have:
- Active BMMS account with Administrator role
- Understanding of your organization's structure
- Knowledge of your organization's approval workflows
- Familiarity with basic security concepts
- Contact information for technical support

### 1.4 Administrator Responsibilities

**Account Management:**
- Create, edit, and deactivate user accounts
- Reset passwords and unlock accounts
- Manage user profiles and contact information

**Access Control:**
- Assign roles and permissions
- Configure approval workflows
- Manage data access levels
- Enforce security policies

**System Configuration:**
- Enable/disable modules
- Configure organization settings
- Customize approval thresholds
- Set notification preferences

**Monitoring and Compliance:**
- Review audit logs
- Monitor system usage
- Investigate security incidents
- Ensure compliance with policies

**Support:**
- Assist users with access issues
- Troubleshoot technical problems
- Coordinate with BMMS technical support
- Train new users

---

## 2. Role Overview

### 2.1 Administrator Role in BMMS

As a BMMS Administrator, you have elevated permissions within your organization:

**What You Can Do:**
- ✅ Manage all user accounts in your MOA
- ✅ Assign and revoke roles
- ✅ Configure organization settings
- ✅ Enable/disable modules
- ✅ Configure approval workflows
- ✅ View audit logs
- ✅ Access all data within your MOA
- ✅ Generate administrative reports
- ✅ Configure security settings

**What You Cannot Do:**
- ❌ Access other MOAs' data or settings
- ❌ Modify system-wide configurations (BMMS platform level)
- ❌ Approve budgets or plans (requires specific officer roles)
- ❌ Delete audit logs
- ❌ Bypass approval workflows

### 2.2 Types of Administrators

**Organization Administrator (Your Role):**
- Manages single MOA instance
- Full control within organization
- Cannot access other MOAs

**Super Administrator (BMMS Team):**
- Manages entire BMMS platform
- Cross-MOA access and configuration
- Technical infrastructure management
- Not covered in this guide

### 2.3 Administrator vs. Officer Roles

**Key Difference:**

**Administrator:**
- Focuses on system management
- Enables others to do their work
- Configures settings and access
- Does not typically create content (plans, budgets, etc.)

**Officer Roles (Planning, Budget, M&E):**
- Focus on content creation and management
- Use modules for daily work
- Create plans, budgets, monitoring entries, etc.
- Work within configured system

**Note:** You can have both Administrator role AND one or more Officer roles (e.g., Administrator + Planning Officer). This is common in smaller MOAs.

### 2.4 Daily Workflow Overview

A typical day for an Administrator involves:

1. **Morning Review** (15-30 minutes)
   - Check new user requests
   - Review security alerts
   - Verify system status
   - Check pending approvals (if also an officer)

2. **User Account Management** (Variable)
   - Process new account requests
   - Reset forgotten passwords
   - Update user information
   - Deactivate departed staff accounts

3. **Configuration Tasks** (As needed)
   - Enable modules for new initiatives
   - Update approval workflows
   - Adjust notification settings
   - Configure new features

4. **Monitoring and Compliance** (30-60 minutes weekly)
   - Review audit logs
   - Check for security anomalies
   - Generate usage reports
   - Verify compliance

5. **Support and Training** (Variable)
   - Respond to user queries
   - Troubleshoot access issues
   - Conduct user orientation
   - Coordinate with BMMS support

---

## 3. Getting Started

### 3.1 Accessing Admin Panel

**Step 1:** Log in to BMMS
- Navigate to your organization's BMMS URL
- Enter administrator credentials
- Complete two-factor authentication (if enabled)

**Step 2:** Navigate to Admin Panel
- Click your profile icon (top right)
- Select "Administration" from dropdown
- Admin Panel loads

[SCREENSHOT: Access admin panel]

**Alternative Access:**
- From any page, click "Admin" in main navigation (visible only to Administrators)

### 3.2 Admin Panel Dashboard

The Admin Panel dashboard provides:

**Overview Cards:**
- Total Users (active/inactive)
- Active Modules
- Recent Logins (last 24 hours)
- Pending User Requests
- Security Alerts

**Quick Actions:**
- Create User Account
- Assign Role
- View Audit Log
- Generate Report
- Configure Settings

**System Health:**
- Server status
- Database status
- Storage usage
- Performance metrics

**Recent Activity:**
- Latest user logins
- Recent account changes
- Configuration updates
- Security events

[SCREENSHOT: Admin dashboard with labeled sections]

### 3.3 Navigation Overview

**Admin Panel Menu:**
- **Dashboard:** Overview and quick actions
- **Users:** User account management
- **Roles:** Role assignment and permissions
- **Organization:** Organization settings
- **Modules:** Enable/disable modules
- **Workflows:** Approval workflow configuration
- **Security:** Security settings and policies
- **Audit Logs:** Activity logging and review
- **Reports:** Administrative reports
- **Settings:** System preferences

**Breadcrumb Navigation:**
- Shows current location in admin panel
- Click to navigate back
- Always visible at top

---

## 4. User Management

### 4.1 Understanding User Accounts

**User Account Components:**

**Profile Information:**
- Full name
- Email address (used for login)
- Phone number
- Position/Title
- Department/Division

**Account Status:**
- Active: Can log in and access system
- Inactive: Temporarily disabled, can be reactivated
- Locked: Temporarily locked due to security (e.g., too many failed login attempts)
- Deactivated: Permanently disabled, cannot reactivate (used for departed staff)

**Authentication:**
- Username: Email address
- Password: Encrypted, not visible to Administrator
- Two-Factor Authentication (optional, recommended)

**Roles and Permissions:**
- One or more roles assigned (Planning Officer, Budget Officer, etc.)
- Permissions derived from roles
- Access level determined by roles

### 4.2 Creating User Accounts

**Step 1:** Navigate to Users
- Go to Admin Panel → Users
- Click "Create User Account"

[SCREENSHOT: Create user button]

**Step 2:** Enter User Information

**Required Fields:**

**First Name:**
```
Example: Juan
```

**Last Name:**
```
Example: Dela Cruz
```

**Email Address:**
```
Example: juan.delacruz@moa.barmm.gov.ph
```
- Must be unique (no duplicate emails)
- Will be used as username
- Must be valid and accessible by user

**Phone Number:**
```
Example: +63 917 123 4567
```
- Format: +63 followed by 10 digits
- Used for SMS notifications (if enabled)

**Position/Title:**
```
Example: Budget Officer II
```

**Department/Division:**
```
Example: Finance Division
```
- Select from dropdown (or add new if not listed)

[SCREENSHOT: Create user form]

**Optional Fields:**

**Employee ID:**
- Your organization's employee identifier
- Useful for HR integration

**Location:**
- Primary office location
- Relevant for multi-location MOAs

**Manager:**
- Select user's supervisor
- Used for approval routing

**Notes:**
- Additional context
- Internal notes not visible to user

**Step 3:** Set Initial Password

**Password Options:**

**Option 1: System-Generated Password (Recommended)**
- Click "Generate Secure Password"
- System creates strong, random password
- Copy password securely
- Share with user through secure channel (not email)

**Option 2: Custom Password**
- Enter password manually
- Must meet security requirements:
  - Minimum 8 characters
  - At least 1 uppercase letter
  - At least 1 lowercase letter
  - At least 1 number
  - At least 1 special character (!@#$%^&*)

**Password Security:**
- ☑ Require password change on first login (Recommended)
- ☐ Allow user to skip password change (Not recommended)

**Step 4:** Assign Initial Roles

Select one or more roles:
- ☐ Planning Officer
- ☐ Budget Officer
- ☐ M&E Officer
- ☐ Administrator
- ☐ Viewer (Read-only access)
- ☐ Other (custom roles if configured)

**Note:** You can assign roles now or later. Many administrators prefer to create account first, then assign roles after user orientation.

[SCREENSHOT: Role selection checkboxes]

**Step 5:** Configure Account Settings

**Account Status:**
- ○ Active (user can log in immediately)
- ○ Inactive (account created but not yet enabled)

**Email Notifications:**
- ☑ Send account creation email (includes login instructions)
- ☑ Send temporary password (if not requiring immediate change)

**Two-Factor Authentication:**
- ○ Required (user must set up 2FA before first login)
- ○ Optional (user can enable 2FA later)
- ○ Disabled (2FA not available for this user)

**Step 6:** Review and Create

- Review all entered information
- Click "Create User Account"
- Confirmation message displayed
- User receives email notification (if enabled)

**Account Created Successfully:**
```
USER ACCOUNT CREATED
====================

Name: Juan Dela Cruz
Email: juan.delacruz@moa.barmm.gov.ph
Status: Active
Roles: Budget Officer
Temporary Password: [Generated password]

The user has been sent an email with login instructions.
Temporary password must be changed on first login.

Next Steps:
- Share temporary password with user securely
- Provide user orientation
- Assign to specific budgets/projects (if applicable)
```

[SCREENSHOT: Account creation confirmation]

### 4.3 Editing User Accounts

**Step 1:** Find User
- Go to Admin Panel → Users
- Use search or filter to find user

**Search Options:**
- By name
- By email
- By role
- By department
- By status (active/inactive)

[SCREENSHOT: User search/filter]

**Step 2:** Open User Profile
- Click on user's name
- User profile page loads
- View current information and settings

**Step 3:** Edit Information

Click "Edit User" button

**Editable Fields:**
- Name (first, last, middle)
- Email (with caution - this is the username)
- Phone number
- Position/Title
- Department/Division
- Manager
- Employee ID
- Notes

**Note:** Changing email address requires user to log in with new email. Notify user before changing.

**Step 4:** Update Roles

- Click "Manage Roles" tab
- Add or remove roles
- Changes take effect immediately
- User may need to log out and back in to see new permissions

[SCREENSHOT: Edit user form]

**Step 5:** Modify Account Settings

**Account Status:**
- Active → Inactive (temporary disable)
- Inactive → Active (re-enable)
- Active → Deactivated (permanent disable for departed staff)

**Security Settings:**
- Require password change
- Unlock account (if locked due to failed login attempts)
- Enable/disable 2FA requirement

**Notification Preferences:**
- Enable/disable email notifications
- Enable/disable SMS notifications
- Configure notification frequency

**Step 6:** Save Changes

- Click "Save Changes"
- User receives notification of profile update (if email enabled)
- Changes logged in audit trail

### 4.4 Resetting Passwords

**Scenario 1: User Forgot Password**

**User-Initiated Reset (Preferred):**
1. User clicks "Forgot Password" on login page
2. Enters email address
3. Receives password reset link
4. Creates new password
5. Logs in with new password

**Administrator-Assisted Reset:**
If user cannot access email or self-reset fails:

**Step 1:** Locate user account
- Admin Panel → Users → Search for user

**Step 2:** Reset password
- Click "Reset Password" button
- Choose method:
  - **Option A:** Send reset link to user's email
  - **Option B:** Generate temporary password and share securely

**Step 3:** Generate temporary password
- Click "Generate Temporary Password"
- System creates secure password
- Copy password securely
- Share with user (phone call, in-person, secure messaging)

**Step 4:** Require password change
- ☑ User must change password on next login
- This ensures only user knows final password

[SCREENSHOT: Password reset interface]

---

**Scenario 2: Account Locked (Too Many Failed Login Attempts)**

**Step 1:** Identify locked account
- User reports cannot log in
- Check Admin Panel → Users → Locked Accounts
- Or search for specific user

**Step 2:** Investigate
- Review audit log for failed login attempts
- Verify user identity (ensure it's legitimate user, not unauthorized access attempt)
- Check for suspicious activity

**Step 3:** Unlock account
- Click "Unlock Account"
- Confirm identity verification completed
- Account immediately unlocked

**Step 4:** Notify user
- Inform user account is unlocked
- Remind user of correct password
- If user forgot password, also perform password reset

**Step 5:** Document
- Add note to user account: "Account unlocked on [date] after user verification"
- Monitor for repeated lockouts (may indicate security issue)

---

**Scenario 3: Suspected Compromised Account**

**If you suspect a user account has been compromised:**

**Step 1:** Immediate action
- Immediately deactivate account (Admin Panel → Users → [User] → Deactivate)
- This prevents further unauthorized access

**Step 2:** Investigate
- Review audit logs for suspicious activity
- Check login locations and IP addresses
- Identify what data was accessed
- Determine scope of compromise

**Step 3:** Notify
- Contact user immediately
- Inform BMMS security team (security@bmms.barmm.gov.ph)
- Notify MOA leadership if sensitive data accessed

**Step 4:** Remediate
- Force password reset
- Revoke active sessions
- Enable 2FA requirement
- Review and adjust permissions if needed

**Step 5:** Reactivate
- After security measures in place, reactivate account
- Monitor closely for continued suspicious activity
- Document incident for compliance

[SCREENSHOT: Security incident workflow diagram]

### 4.5 Deactivating User Accounts

**When to Deactivate:**
- Employee leaves organization (resignation, retirement, termination)
- Long-term absence (extended leave)
- Role change (no longer needs BMMS access)

**Important Distinction:**

**Inactive vs. Deactivated:**

**Inactive:**
- Temporary status
- Can be reactivated by Administrator
- Use for: Leave of absence, temporary role change

**Deactivated:**
- Permanent status
- Cannot be reactivated (would need to create new account)
- Use for: Departed employees, permanent role change

**Deactivation Process:**

**Step 1:** Verify need to deactivate
- Confirm with HR or supervisor
- Ensure user has truly left or no longer needs access

**Step 2:** Backup user's work (if needed)
- Export reports created by user
- Transfer ownership of ongoing projects
- Archive important documents

**Step 3:** Deactivate account
- Admin Panel → Users → [User]
- Click "Deactivate Account"
- Confirm deactivation

**Step 4:** Transfer responsibilities
- Reassign user's pending tasks
- Update approval workflows if user was approver
- Notify team members of transition

**Step 5:** Document
- Add note to account: "Deactivated on [date]. Reason: [resignation/etc.]"
- Retain account for audit purposes (do NOT delete)

**Confirmation:**
```
ACCOUNT DEACTIVATED
===================

User: Juan Dela Cruz
Email: juan.delacruz@moa.barmm.gov.ph
Deactivation Date: October 14, 2025
Reason: Employee resigned

Actions Taken:
- User cannot log in
- Active sessions terminated
- Email notifications stopped
- Roles revoked
- Pending tasks reassigned to: Maria Santos

Account retained for audit purposes.
Do NOT delete account.
```

[SCREENSHOT: Deactivate account confirmation]

**What Happens When Account Deactivated:**
- User cannot log in
- All active sessions terminated immediately
- User removed from approval workflows
- Email notifications stopped
- Data created by user remains (plans, budgets, reports, etc.)
- Audit trail preserved
- Account visible to Administrators but marked "Deactivated"

**Note:** NEVER delete user accounts. Deactivation preserves data integrity and audit trail.

---

## 5. Role Assignments

### 5.1 Understanding BMMS Roles

**Core Roles:**

**Planning Officer:**
- Creates and manages strategic plans
- Defines objectives and key results
- Tracks implementation progress
- Generates planning reports

**Budget Officer:**
- Creates budget proposals
- Manages allocations
- Tracks obligations and disbursements
- Ensures Bill No. 325 compliance

**M&E Officer:**
- Conducts monitoring visits
- Manages performance indicators
- Designs and conducts evaluations
- Generates M&E reports

**Administrator:**
- Manages user accounts
- Configures system settings
- Reviews audit logs
- Provides user support

**Viewer (Read-Only):**
- Can view data but not create/edit
- Suitable for: Senior management, auditors, external reviewers

**Custom Roles:**
- Organization-specific roles
- Defined by MOA based on needs
- Examples: Data Entry Clerk, Project Coordinator, Finance Reviewer

### 5.2 Role Permissions Matrix

**What Each Role Can Do:**

| Action | Viewer | Planning | Budget | M&E | Admin |
|--------|--------|----------|--------|-----|-------|
| View strategic plans | ✅ | ✅ | ✅ | ✅ | ✅ |
| Create strategic plans | ❌ | ✅ | ❌ | ❌ | ❌ |
| Edit strategic plans | ❌ | ✅ | ❌ | ❌ | ❌ |
| View budgets | ✅ | ✅ | ✅ | ✅ | ✅ |
| Create budgets | ❌ | ❌ | ✅ | ❌ | ❌ |
| Approve budgets | ❌ | ❌ | Depends* | ❌ | ❌ |
| View M&E data | ✅ | ✅ | ✅ | ✅ | ✅ |
| Create monitoring entries | ❌ | ❌ | ❌ | ✅ | ❌ |
| Manage users | ❌ | ❌ | ❌ | ❌ | ✅ |
| View audit logs | ❌ | ❌ | ❌ | ❌ | ✅ |
| Configure settings | ❌ | ❌ | ❌ | ❌ | ✅ |

*Depends on approval workflow configuration

**Multiple Roles:**
- Users can have multiple roles simultaneously
- Permissions are cumulative (union of all roles)
- Example: Administrator + Planning Officer can manage users AND create plans

[SCREENSHOT: Permissions comparison table]

### 5.3 Assigning Roles to Users

**Step 1:** Navigate to user account
- Admin Panel → Users → [Select User]
- Click "Manage Roles" tab

**Step 2:** View current roles
- List of currently assigned roles
- Permission summary

**Step 3:** Add role
- Click "Add Role"
- Select role from dropdown:
  - Planning Officer
  - Budget Officer
  - M&E Officer
  - Administrator
  - Viewer
  - Custom roles (if configured)

**Step 4:** Configure role settings (if applicable)

For some roles, additional settings:

**Budget Officer Settings:**
- Approval Authority Level: Level 1, 2, 3, or 4
  - Based on Bill No. 325 thresholds
  - Determines which budgets user can approve
- Budget Categories: Which categories user can manage (PS, MOOE, CO, FE)

**Planning Officer Settings:**
- Planning Scope: Organization-wide, specific departments, specific projects
- Approval Authority: Can approve plans up to certain complexity level

**M&E Officer Settings:**
- Geographic Coverage: Which regions/provinces user monitors
- Evaluation Types: Which evaluations user can conduct

[SCREENSHOT: Assign role with settings]

**Step 5:** Set effective dates (optional)

**Start Date:**
- When role assignment begins
- Default: Immediately

**End Date:**
- When role assignment expires
- Useful for temporary assignments
- Default: No expiration

**Example Temporary Assignment:**
```
Role: Budget Officer
User: Maria Santos
Start Date: January 1, 2025
End Date: March 31, 2025
Reason: Temporary coverage for Juan Dela Cruz (on leave)

On April 1, 2025, role will automatically expire and user will
revert to previous roles.
```

**Step 6:** Save role assignment
- Click "Assign Role"
- User receives notification (if email enabled)
- Changes take effect immediately
- User may need to log out and back in

**Confirmation:**
```
ROLE ASSIGNED
=============

User: Maria Santos
New Role: Budget Officer
Effective: Immediately
Expiration: None

User has been notified via email.
User will see Budget Officer permissions when they next log in.
```

### 5.4 Removing Roles from Users

**Step 1:** Navigate to user account
- Admin Panel → Users → [Select User]
- Click "Manage Roles" tab

**Step 2:** Identify role to remove
- View list of assigned roles
- Click "Remove" next to role

**Step 3:** Confirm removal
- System prompts for confirmation
- Warning displayed if user has active work in that role

**Warning Example:**
```
WARNING: Pending Work
=====================

User: Juan Dela Cruz
Role to Remove: Budget Officer

This user has:
- 3 draft budget proposals
- 5 pending obligations to record
- 2 quarterly reports due next week

Removing Budget Officer role will:
- Prevent user from editing draft proposals
- Prevent user from recording obligations
- Prevent user from submitting reports

Recommendation: Either complete pending work first OR reassign
work to another Budget Officer.

Proceed with role removal?
[Cancel] [Reassign Work] [Remove Anyway]
```

**Step 4:** Handle pending work

**Option A: Reassign work**
- Click "Reassign Work"
- Select another user with Budget Officer role
- Work transferred to selected user

**Option B: Complete work first**
- Click "Cancel"
- Contact user to complete pending work
- Remove role after work completed

**Option C: Remove anyway**
- Click "Remove Anyway"
- Role removed immediately
- Pending work remains but user cannot access
- Another Budget Officer must complete work

**Step 5:** Document reason
- Add note explaining why role removed
- Example: "Role removed - user transferred to Planning Division"

**Step 6:** Notify user
- User receives email notification
- Explain what they can no longer access
- Provide next steps if applicable

[SCREENSHOT: Remove role confirmation]

### 5.5 Creating Custom Roles

**When to Create Custom Roles:**
- Standard roles don't fit your organization's needs
- Specialized positions with unique permission requirements
- Need for more granular access control

**Examples:**
- Data Entry Clerk: Can enter data but not approve
- Finance Reviewer: Can view budgets and add comments but not edit
- Project Coordinator: Can view all modules but only edit specific projects

**Creating Custom Role:**

**Step 1:** Navigate to Roles
- Admin Panel → Roles
- Click "Create Custom Role"

**Step 2:** Define role basics

**Role Name:**
```
Example: "Project Coordinator"
```
- Descriptive and clear
- Unique within organization

**Description:**
```
Example: "Coordinates implementation of specific projects. Can view
all data related to assigned projects and update progress, but cannot
create new plans or budgets."
```

**Role Category:**
- Management
- Implementation
- Support
- Other

[SCREENSHOT: Create custom role form]

**Step 3:** Set permissions

**Module Access:**
- ☑ Planning Module
  - ☑ View plans
  - ☑ Update progress
  - ☐ Create plans
  - ☐ Approve plans
- ☑ Budgeting Module
  - ☑ View budgets
  - ☐ Create budgets
  - ☐ Approve budgets
- ☑ M&E Module
  - ☑ View M&E data
  - ☑ Create monitoring entries
  - ☐ Design evaluations

**Data Scope:**
- ○ Organization-wide: Access all data in organization
- ● Project-specific: Access only assigned projects
- ○ Department-specific: Access only assigned departments

**Actions Allowed:**
- ☑ View
- ☑ Edit (own data)
- ☑ Comment
- ☐ Delete
- ☐ Approve
- ☐ Export

[SCREENSHOT: Permission builder interface]

**Step 4:** Save custom role
- Click "Create Role"
- Role becomes available for assignment
- Document role purpose and use cases

**Step 5:** Assign custom role to users
- Go to Users → [Select User] → Manage Roles
- Select custom role
- Configure role-specific settings if applicable

---

## 6. Organization Settings

### 6.1 Viewing Organization Profile

**Step 1:** Navigate to organization settings
- Admin Panel → Organization
- View organization profile

**Organization Information:**

**Basic Details:**
- Organization Name: [Your MOA name]
- Organization Type: Ministry / Office / Agency
- Parent Organization: BARMM Government
- Establishment Date
- Official Website
- Contact Email
- Contact Phone

**Address:**
- Main Office Address
- City/Municipality
- Province
- Region
- Postal Code

**Leadership:**
- Head of Organization (Minister, Director, etc.)
- Deputy Head
- Chief of Staff
- Other key positions

[SCREENSHOT: Organization profile view]

### 6.2 Editing Organization Settings

**Step 1:** Click "Edit Settings"

**Editable Settings:**

**1. Fiscal Year Configuration**

**Fiscal Year Start:**
- ○ January 1 (Calendar year)
- ● April 1 (Most BARMM MOAs)
- ○ July 1
- ○ Other (specify)

**Current Fiscal Year:** FY 2025
**Next Fiscal Year:** FY 2026

**2. Work Week Configuration**

**Work Days:**
- ☑ Monday
- ☑ Tuesday
- ☑ Wednesday
- ☑ Thursday
- ☑ Friday
- ☐ Saturday
- ☐ Sunday

**Work Hours:**
- Start: 8:00 AM
- End: 5:00 PM
- Lunch Break: 12:00 PM - 1:00 PM

**3. Holiday Calendar**

**National Holidays:** (Auto-populated by BMMS)
- New Year's Day
- Eid al-Fitr
- Eid al-Adha
- Independence Day
- Christmas Day
- Etc.

**Organization-Specific Holidays:**
- Add custom holidays
- Example: Founding anniversary, special non-working days

[SCREENSHOT: Holiday calendar configuration]

**4. Notification Settings**

**Email Notifications:**
- ☑ Enabled for all users
- Notification From Name: BMMS - [Your MOA]
- Notification From Email: noreply@bmms.barmm.gov.ph
- Reply-To Email: admin@yourmoa.barmm.gov.ph

**Notification Frequency:**
- ○ Real-time (immediate)
- ● Daily digest (9:00 AM)
- ○ Weekly digest (Monday 9:00 AM)

**SMS Notifications:** (If enabled)
- ☑ Enabled for critical alerts only
- SMS Sender ID: BMMS-[MOA]

**5. Data Retention Settings**

**Audit Logs:**
- Retention Period: 5 years (Bill No. 325 requirement)
- Cannot be changed

**Completed Projects:**
- Retention Period: 7 years
- After period, data archived (not deleted)

**User Accounts (Deactivated):**
- Retention Period: Indefinite
- Never delete deactivated accounts (audit trail)

**Step 2:** Save settings
- Click "Save Settings"
- Changes take effect immediately
- Some settings may require system restart (BMMS team notified)

[SCREENSHOT: Organization settings form]

### 6.3 Branding and Customization

**Logo and Images:**

**Organization Logo:**
- Upload: PNG or JPG, maximum 500 KB
- Recommended size: 200 x 200 pixels
- Displayed in: Header, login page, reports

**Cover Photo:**
- Upload: JPG, maximum 2 MB
- Recommended size: 1920 x 400 pixels
- Displayed in: Dashboard header

**Favicon:**
- Upload: ICO or PNG, 32 x 32 pixels
- Displayed in: Browser tab

[SCREENSHOT: Logo upload interface]

**Color Scheme:**

**Primary Color:**
- Default: BARMM Blue (#003F87)
- Can customize to match MOA branding
- Used for: Buttons, links, headers

**Secondary Color:**
- Default: BARMM Green (#008551)
- Used for: Accents, highlights

**Preview:**
- Live preview of color changes
- Ensure sufficient contrast for accessibility

**Note:** Customization is optional. Default BARMM branding meets all requirements.

---

## 7. Module Enablement

### 7.1 Understanding BMMS Modules

**Core Modules:**

**Planning Module:**
- Strategic planning
- Objectives and key results
- Annual work plans
- Progress tracking

**Budgeting Module:**
- Budget proposals
- Allocation management
- Obligation and disbursement tracking
- Bill No. 325 compliance

**M&E Module:**
- Monitoring visits
- Performance indicators
- Evaluations
- Data collection

**Coordination Module:**
- Inter-MOA collaboration
- Shared projects
- Communication tools

**Additional Modules:**

**Communities Module:** (Primarily for OOBC)
- Bangsamoro community management
- Beneficiary database
- Geographic information

**MANA Module:** (OOBC-specific)
- Municipal affairs coordination

**Policies Module:**
- Policy management
- Document repository
- Version control

### 7.2 Enabling/Disabling Modules

**Step 1:** Navigate to modules
- Admin Panel → Modules
- View list of available modules

**Module Status:**
- ✅ Enabled: Module active and accessible to users
- ⏹️ Disabled: Module not accessible (even if user has role)
- 🔒 Locked: Required module, cannot disable

[SCREENSHOT: Modules list]

**Step 2:** Enable module

Click "Enable" next to module:

**Planning Module:**
```
Enable Planning Module?

This will:
- Make Planning Module accessible to Planning Officers
- Enable strategic plan creation
- Enable OKR tracking
- Integrate with Budget and M&E Modules

Required roles: Planning Officer (will be available for assignment)

Cost: Included in base BMMS subscription

[Cancel] [Enable Module]
```

**Step 3:** Configure module settings

After enabling, configure:

**Planning Module Settings:**
- Default planning period: 1 year / 3 years / 5 years
- Approval required for plans: Yes / No
- Approval workflow: Select from configured workflows
- Notifications: Enable/disable specific notifications

**Budgeting Module Settings:**
- Bill No. 325 compliance: Enabled (cannot disable)
- Approval thresholds: Use default or customize
- Approval workflow: Configure levels and approvers
- Budget categories: Enable/disable specific categories (PS, MOOE, CO, FE)

**M&E Module Settings:**
- Monitoring frequency: Default monthly (can be adjusted per activity)
- Indicator tracking: Real-time or batch updates
- Evaluation types: Baseline, Midline, Endline, Impact
- Data collection: Online, offline, or both

[SCREENSHOT: Module configuration]

**Step 4:** Activate module
- Click "Activate Module"
- Module immediately available
- Users with relevant roles notified

**Step 5:** Train users
- Conduct module orientation
- Provide user guides
- Assign super users (power users who can help others)

### 7.3 Module Dependencies

**Some modules depend on others:**

**Budgeting Module:**
- Recommended: Planning Module (for budget-plan alignment)
- Not required, but integration provides significant value

**M&E Module:**
- Recommended: Planning Module (for indicator-objective linkage)
- Not required, but integration enhances performance management

**Coordination Module:**
- Independent, no dependencies

**When disabling modules:**
```
WARNING: Module Dependencies
=============================

You are attempting to disable: Planning Module

Other modules depend on Planning Module:
- Budgeting Module (budget-plan links)
- M&E Module (indicator-objective links)

Disabling Planning Module will:
- Break existing links to budgets and indicators
- Prevent new links from being created
- Not delete existing plans (data preserved)

Recommendation: Keep Planning Module enabled if Budget or M&E
Modules are active.

Proceed with disabling?
[Cancel] [Disable Anyway]
```

### 7.4 Module Access Control

**Per-Module Access:**

Even if module is enabled, users need:
1. Module enabled organization-wide (Administrator does this)
2. Appropriate role assigned (Administrator assigns roles)
3. Specific permissions within role (configured in role settings)

**Example:**

**Scenario:** User cannot access Planning Module

**Troubleshooting:**
1. Check if Planning Module enabled for organization
   - Admin Panel → Modules → Planning Module → Status
   - If disabled, enable it
2. Check if user has Planning Officer role
   - Admin Panel → Users → [User] → Manage Roles
   - If not assigned, assign Planning Officer role
3. Check if role has Planning Module permissions
   - Admin Panel → Roles → Planning Officer → Permissions
   - Verify "Planning Module Access" is checked

**All three must be true for user to access module.**

[SCREENSHOT: Access troubleshooting flowchart]

---

## 8. Approval Workflows Configuration

### 8.1 Understanding Approval Workflows

**What are Approval Workflows:**
- Structured processes for reviewing and approving documents
- Examples: Budget proposals, strategic plans, evaluations
- Define: Who approves, in what order, under what conditions

**Components:**
- **Trigger:** What initiates workflow (e.g., budget proposal submitted)
- **Steps:** Sequence of approval levels
- **Approvers:** Who approves at each level
- **Conditions:** Rules determining routing (e.g., amount thresholds)
- **Actions:** What happens at each step (approve, reject, request changes)
- **Notifications:** Who gets notified when

### 8.2 Budget Approval Workflow

**Bill No. 325 Requirements:**

Parliament Bill No. 325 mandates specific approval levels based on budget amount:

**Level 1:** Up to PHP 500,000
- Approver: Department Head
- Timeline: 3 working days

**Level 2:** PHP 500,001 - PHP 2,000,000
- Approver: Finance Officer
- Timeline: 5 working days

**Level 3:** PHP 2,000,001 - PHP 10,000,000
- Approver: Ministry Head / Executive
- Timeline: 7 working days

**Level 4:** Above PHP 10,000,000
- Approver: Ministry of Finance (MOF)
- Timeline: 15 working days

**Configuring Budget Approval Workflow:**

**Step 1:** Navigate to workflows
- Admin Panel → Workflows
- Select "Budget Approval Workflow"

[SCREENSHOT: Workflow configuration page]

**Step 2:** Define approval levels

**Level 1 Configuration:**
- Threshold: PHP 0 - PHP 500,000
- Approver Role: Department Head
- Specific Approvers: Select users with Department Head designation
  - Option: Primary approver + Backup (for absences)
- Timeline: 3 working days
- Auto-escalate if not approved: Yes (to supervisor)
- Notifications:
  - ☑ Email to approver when submission received
  - ☑ Reminder email if not approved within 2 days
  - ☑ Escalation notification if deadline exceeded

**Level 2 Configuration:**
- Threshold: PHP 500,001 - PHP 2,000,000
- Approver Role: Finance Officer
- Specific Approvers: [Select from list]
- Primary: Maria Santos
- Backup: Juan Dela Cruz
- Timeline: 5 working days
- Auto-escalate: Yes

**Level 3 Configuration:**
- Threshold: PHP 2,000,001 - PHP 10,000,000
- Approver Role: Ministry Head
- Specific Approvers: [Minister or Executive Director]
- Primary: [Minister Name]
- Backup: [Deputy Minister Name]
- Timeline: 7 working days
- Auto-escalate: Yes

**Level 4 Configuration:**
- Threshold: Above PHP 10,000,000
- Approver: Ministry of Finance (External to organization)
- MOF Submission Process: Automated via BMMS
- Timeline: 15 working days
- Auto-escalate: No (MOF has own process)

[SCREENSHOT: Approval level configuration]

**Step 3:** Configure workflow logic

**Sequential vs. Parallel:**
- ● Sequential: Each level must approve before next level (Standard for budgets)
- ○ Parallel: Multiple approvers at same level, all must approve
- ○ Parallel (Any): Multiple approvers at same level, any one can approve

**Rejection Handling:**
- When approver rejects:
  - ○ Return to submitter for revision
  - ● Return to submitter and require resubmission from beginning
  - ○ Allow submitter to resubmit to same level

**Revision Handling:**
- When approver requests changes:
  - ● Unlock document for editing
  - ○ Keep document locked, allow comments only

**Timeout Handling:**
- If approver doesn't respond within timeline:
  - ● Auto-escalate to supervisor
  - ○ Send reminder but don't escalate
  - ○ Auto-approve (NOT recommended for budgets)

**Step 4:** Test workflow
- Click "Test Workflow"
- Create sample budget proposal
- Submit and track through approval levels
- Verify notifications sent correctly
- Confirm approvers can approve/reject
- Fix any issues

**Step 5:** Activate workflow
- Click "Activate Workflow"
- Workflow applied to all future budget submissions
- Existing pending budgets: Apply new workflow or continue with old?
  - ● Apply new workflow to all pending
  - ○ Continue old workflow for existing, new workflow for future

[SCREENSHOT: Workflow testing interface]

### 8.3 Planning Approval Workflow

**Strategic Plan Approval:**

**Step 1:** Navigate to Planning Approval Workflow
- Admin Panel → Workflows → Planning Approval

**Step 2:** Determine if approval required

**Option A: No Approval Required**
- Strategic plans immediately active upon submission
- Use for: Smaller MOAs, high trust environment
- Risk: Less oversight

**Option B: Simple Approval (Recommended)**
- One-level approval by designated reviewer
- Use for: Most MOAs
- Balance of speed and oversight

**Option C: Multi-Level Approval**
- Multiple approval levels (like budget)
- Use for: Large MOAs, high-stakes planning
- More rigorous but slower

**Step 3:** Configure approval (if required)

**Simple Approval Configuration:**

**Approver:**
- Role: Planning Manager / Deputy Minister / Chief of Staff
- Specific Approver: [Select user]
- Backup Approver: [Select user]

**Timeline:**
- 5 working days

**Approval Criteria:**
- ☑ Alignment with BARMM priorities
- ☑ Feasibility and realism
- ☑ Resource availability
- ☑ Stakeholder consultation completed

**Actions:**
- Approve: Plan becomes active
- Request Changes: Return to Planning Officer with comments
- Reject: Plan archived, Planning Officer must start over

**Step 4:** Save and activate
- Click "Save and Activate"
- Workflow applied to new strategic plan submissions

[SCREENSHOT: Planning approval configuration]

### 8.4 Custom Approval Workflows

**Creating workflow for other processes:**

**Examples:**
- Evaluation report approval
- Data collection tool approval
- Realignment request approval
- Procurement request approval (if BMMS used for procurement)

**Step 1:** Create new workflow
- Admin Panel → Workflows → Create Custom Workflow

**Step 2:** Define workflow basics

**Workflow Name:**
```
Example: "Evaluation Report Approval"
```

**Workflow Description:**
```
Example: "Approval process for evaluation reports before
dissemination to stakeholders. Ensures quality and accuracy of findings."
```

**Trigger:**
- When: Evaluation report submitted
- By: M&E Officer
- In: M&E Module

**Step 3:** Define workflow steps

**Step 1: Technical Review**
- Approver: Senior M&E Officer
- Criteria: Data quality, methodology soundness, analysis rigor
- Timeline: 3 working days
- Actions: Approve, Request Revision, Reject

**Step 2: Management Review**
- Approver: Department Head or Ministry Leadership
- Criteria: Findings alignment with expectations, recommendations feasibility
- Timeline: 5 working days
- Actions: Approve, Request Revision, Reject

**Step 3: Final Clearance**
- Approver: Minister or designated authority
- Criteria: Political sensitivity, dissemination approval
- Timeline: 3 working days
- Actions: Approve for Dissemination, Hold, Reject

**Step 4:** Configure notifications

**When submitted:**
- Notify: Technical reviewer
- Message: "New evaluation report submitted for your review"

**When approved at each level:**
- Notify: Next level approver
- Message: "Evaluation report approved by [previous approver], now pending your review"

**When fully approved:**
- Notify: M&E Officer, Program Manager, Stakeholders
- Message: "Evaluation report approved for dissemination"

**When revision requested:**
- Notify: M&E Officer
- Message: "Revisions requested on evaluation report by [approver]"

**Step 5:** Activate custom workflow
- Test with sample document
- Activate when satisfied
- Train users on new workflow

[SCREENSHOT: Custom workflow builder]

---

## 9. Security and Access Controls

### 9.1 Security Settings

**Password Policies:**

**Step 1:** Navigate to security settings
- Admin Panel → Security → Password Policy

**Step 2:** Configure password requirements

**Minimum Length:**
- 8 characters (default, minimum)
- 12 characters (recommended for high security)
- 16 characters (maximum security)

**Complexity Requirements:**
- ☑ At least 1 uppercase letter
- ☑ At least 1 lowercase letter
- ☑ At least 1 number
- ☑ At least 1 special character (!@#$%^&*)
- ☐ No repeating characters (e.g., "aaa")
- ☐ No sequential characters (e.g., "abc", "123")

**Password Expiration:**
- ● Never expire (not recommended)
- ○ Expire every 90 days (recommended)
- ○ Expire every 180 days
- ○ Custom: [days]

**Password Reuse:**
- Prevent reuse of last [5] passwords

**Password Reset:**
- Users can reset: ● Anytime ○ Only with admin approval
- Reset link validity: 24 hours

[SCREENSHOT: Password policy configuration]

**Step 3:** Configure account lockout policy

**Failed Login Attempts:**
- Lock account after [5] failed attempts
- Lockout duration:
  - ○ 15 minutes (auto-unlock)
  - ○ 30 minutes
  - ● Until admin unlocks (recommended for security)

**Lockout Notifications:**
- ☑ Email user when account locked
- ☑ Email admin when account locked
- ☑ Log security event

**Step 4:** Save password policy
- Click "Save Policy"
- Policy applies to all users immediately
- Existing users required to update passwords at next login if they don't meet new requirements

### 9.2 Two-Factor Authentication (2FA)

**Enabling 2FA:**

**Step 1:** Navigate to 2FA settings
- Admin Panel → Security → Two-Factor Authentication

**Step 2:** Configure 2FA policy

**2FA Requirement:**
- ○ Optional (users can enable if they want)
- ● Required for Administrators (recommended)
- ○ Required for all users (maximum security)

**2FA Methods:**
- ☑ Authenticator App (Google Authenticator, Microsoft Authenticator)
  - Most secure, recommended
- ☑ SMS Code
  - Convenient but less secure
- ☐ Email Code
  - Least secure, not recommended

**2FA Backup Codes:**
- ☑ Generate backup codes for users
- Number of codes: 10
- One-time use only
- Users can download/print for safekeeping

**2FA Enforcement Timeline:**
- Effective date: [Date]
- Grace period: 30 days
- After grace period, users without 2FA cannot log in

[SCREENSHOT: 2FA configuration]

**Step 3:** Activate 2FA
- Click "Activate 2FA Policy"
- All users (or specified roles) notified
- Instructions provided

**User 2FA Setup Process:**

1. User logs in (after policy activated)
2. System prompts: "2FA Required - Set Up Now"
3. User chooses 2FA method (Authenticator App recommended)
4. For Authenticator App:
   - User scans QR code with authenticator app
   - Enters 6-digit code to verify
   - System generates backup codes
   - User saves backup codes securely
5. Future logins:
   - Enter username/password as usual
   - Enter 6-digit code from authenticator app
   - Login successful

**Administrator 2FA Management:**

**Viewing 2FA Status:**
- Admin Panel → Users → [User] → Security Tab
- Shows: 2FA enabled/disabled, method used, last verified

**Resetting User 2FA:**
If user loses access to 2FA method:
- Verify user identity thoroughly
- Admin Panel → Users → [User] → Security → "Reset 2FA"
- 2FA disabled for that user
- User must set up 2FA again at next login

**Bypassing 2FA (Emergency):**
- Only for critical situations (user locked out, urgent access needed)
- Generate temporary 2FA bypass code
- Valid for 24 hours only
- Strongly discouraged, log in audit trail

[SCREENSHOT: User 2FA status]

### 9.3 IP Whitelisting (Optional)

**Restricting Access by IP Address:**

**When to Use:**
- High-security environments
- Prevent access from unauthorized locations
- Ensure access only from office network

**Step 1:** Navigate to IP whitelisting
- Admin Panel → Security → IP Whitelisting

**Step 2:** Enable IP whitelisting
- ☐ Disabled (allow access from any IP)
- ☑ Enabled (restrict to whitelisted IPs)

**Warning:**
```
⚠️ WARNING: IP Whitelisting
===========================

Enabling IP whitelisting will block access from IP addresses not
on the whitelist. This includes:
- Remote access (e.g., from home)
- Mobile access
- Access during travel

Ensure:
1. Your office IP is whitelisted before enabling
2. Key staff can access from whitelisted locations
3. Backup access method exists (e.g., VPN)

Enabling without proper configuration may lock out all users,
including administrators.

Proceed with caution.
```

**Step 3:** Add IP addresses to whitelist

**Whitelist Format:**

**Single IP:**
```
192.168.1.100
```

**IP Range:**
```
192.168.1.1 - 192.168.1.254
```

**CIDR Notation:**
```
192.168.1.0/24
```

**Example Whitelist:**
```
Office Network: 192.168.1.0/24
Minister's Residence: 203.177.XX.XX
VPN Gateway: 10.0.0.1
```

**Step 4:** Test before activating
- Add your current IP to whitelist
- Click "Test Configuration"
- Verify you can still access after enabling

**Step 5:** Activate whitelisting
- Click "Activate IP Whitelisting"
- Only whitelisted IPs can access BMMS
- Non-whitelisted IPs see: "Access Denied - Unauthorized IP"

[SCREENSHOT: IP whitelist configuration]

### 9.4 Session Management

**Session Security Settings:**

**Step 1:** Navigate to session settings
- Admin Panel → Security → Session Management

**Step 2:** Configure session timeouts

**Idle Timeout:**
- Log out user after [30] minutes of inactivity
- Warning shown 5 minutes before logout
- User can extend session

**Maximum Session Duration:**
- Force logout after [8] hours regardless of activity
- Recommended for security
- User must log in again

**Concurrent Sessions:**
- ○ Allow unlimited concurrent sessions (not recommended)
- ● Limit to [3] concurrent sessions per user
- ○ Only one session per user (most secure)

**Behavior when limit exceeded:**
- ○ Block new login (force user to log out existing sessions)
- ● Terminate oldest session (allow new login)

**Step 3:** Configure session security

**Secure Session Cookies:**
- ☑ HTTPS only (cookies only sent over secure connection)
- ☑ HttpOnly (prevent JavaScript access to cookies)
- ☑ SameSite (prevent CSRF attacks)

**Session Hijacking Prevention:**
- ☑ Bind session to IP address (session invalid if IP changes)
  - May cause issues for users on mobile networks
- ☑ Bind session to user agent (session invalid if browser changes)
- ☑ Regenerate session ID on login

**Step 4:** Save session settings
- Click "Save Settings"
- Settings apply to all new sessions
- Existing sessions remain valid until timeout

[SCREENSHOT: Session management configuration]

### 9.5 Data Access Controls

**Organization Data Isolation:**

**BMMS Multi-Tenant Architecture:**
- Each MOA has separate data space
- MOA A cannot access MOA B's data
- Enforced at database level
- Cannot be disabled

**Within-Organization Access:**

**Data Scope by Role:**

**Organization-Wide Access:**
- Administrator: Sees all data in organization
- Viewer: Sees all data (read-only)

**Departmental Access:**
- Users can be restricted to specific departments
- Example: Planning Officer in Education Department sees only Education Department plans

**Project-Based Access:**
- Users can be restricted to specific projects
- Example: M&E Officer monitoring only Health Projects

**Configuring Data Scope:**

**Step 1:** Edit user account
- Admin Panel → Users → [User] → Edit

**Step 2:** Set data scope

**Data Access:**
- ● Organization-wide (all data)
- ○ Department-specific: [Select departments]
- ○ Project-specific: [Select projects]
- ○ Custom: [Define custom scope]

**Example: Department-Specific Access**
```
User: Juan Dela Cruz
Role: Planning Officer
Data Scope: Department-specific
Departments: Education Department, Youth Affairs Department

Result: User can only view/edit plans, budgets, and M&E data
for Education and Youth Affairs. Other departments' data is invisible.
```

**Step 3:** Save data scope
- Changes take effect immediately
- User sees only data within scope

[SCREENSHOT: Data scope configuration]

---

## 10. Audit Logs Review

### 10.1 Understanding Audit Logs

**What are Audit Logs:**
- Comprehensive record of all system activities
- Who did what, when, where, and how
- Immutable (cannot be edited or deleted)
- Retained for 5 years (Bill No. 325 requirement)

**What is Logged:**
- User logins and logouts
- Account creation, modification, deactivation
- Role assignments and changes
- Data creation, editing, deletion
- Configuration changes
- Security events (failed logins, lockouts, etc.)
- Report generation
- File uploads and downloads

**What is NOT Logged:**
- User passwords (encrypted, never logged)
- Page views (too voluminous, no value)
- Background system processes

### 10.2 Accessing Audit Logs

**Step 1:** Navigate to audit logs
- Admin Panel → Audit Logs

**Step 2:** View log entries

**Log Entry Format:**
```
Timestamp: 2025-10-14 09:15:32
User: Juan Dela Cruz (juan.delacruz@moa.barmm.gov.ph)
IP Address: 192.168.1.105
Action: Budget Proposal Created
Details: Budget proposal "Ministry of Education FY 2025" created
Amount: PHP 50,000,000
Module: Budgeting
Session ID: sess_xyz123
```

[SCREENSHOT: Audit log entries]

### 10.3 Searching and Filtering Audit Logs

**Search Parameters:**

**By User:**
- Select specific user
- View all activities by that user

**By Action:**
- Login/Logout
- Create/Edit/Delete
- Approve/Reject
- Configuration Change
- Security Event

**By Module:**
- Planning
- Budgeting
- M&E
- Administration
- Security

**By Date Range:**
- Today
- Last 7 days
- Last 30 days
- Last 90 days
- Custom date range

**By IP Address:**
- Useful for tracking activity from specific location
- Identify unauthorized access attempts from unknown IPs

**Search Examples:**

**Example 1: All actions by specific user**
```
Filter:
- User: Maria Santos
- Date Range: October 1-14, 2025

Result: 47 log entries showing all Maria's activities
- 15 logins
- 12 budget proposals created
- 8 budget proposals edited
- 7 obligations recorded
- 5 reports generated
```

**Example 2: All failed login attempts**
```
Filter:
- Action: Failed Login
- Date Range: Last 30 days

Result: 23 failed login attempts
- 18 by known users (forgot password)
- 5 by unknown email (potential unauthorized access attempts)
```

**Example 3: All administrative changes**
```
Filter:
- Module: Administration
- Action: Configuration Change
- Date Range: Last 90 days

Result: 8 configuration changes
- 3 user account creations
- 2 role assignments
- 1 workflow configuration update
- 1 module enablement
- 1 security setting change
```

[SCREENSHOT: Audit log search interface]

### 10.4 Analyzing Audit Logs for Security

**Security Monitoring:**

**Daily Review:**
- Check for failed login attempts
- Review unusual access patterns
- Verify no unauthorized configuration changes

**Weekly Review:**
- Analyze user activity patterns
- Identify inactive accounts
- Review role assignments

**Monthly Review:**
- Comprehensive security assessment
- Generate security report
- Share findings with leadership

**Red Flags to Watch For:**

**1. Multiple Failed Logins:**
```
Warning: Multiple Failed Login Attempts
========================================

User: maria.santos@moa.barmm.gov.ph
Failed Attempts: 8 in last hour
IP Address: 203.177.XX.XX
Location: Unknown (not typical user location)

Action: Account automatically locked. Investigate before unlocking.
```

**2. Access from Unusual Location:**
```
Alert: Unusual Access Location
===============================

User: Juan Dela Cruz
Typical Location: Cotabato City (IP range: 192.168.1.x)
Current Access: Manila (IP: 203.177.XX.XX)

Action: Verify with user. Ensure authorized access.
```

**3. Unusual Activity Pattern:**
```
Alert: Unusual Activity Pattern
================================

User: Budget Officer Account
Typical Activity: 8:00 AM - 5:00 PM, weekdays
Current Activity: 2:00 AM, Sunday

Action: Verify if authorized (possibly user working late) or
potential compromised account.
```

**4. Bulk Data Export:**
```
Alert: Large Data Export
========================

User: Planning Officer
Action: Exported 1,500 beneficiary records
Time: 11:45 PM

Action: Verify purpose of export. Ensure compliance with data
privacy policies.
```

[SCREENSHOT: Security alerts dashboard]

**Investigating Security Incidents:**

**Step 1:** Identify incident from audit logs

**Step 2:** Gather details
- Who: User involved
- What: Action performed
- When: Timestamp
- Where: IP address, location
- Why: Purpose (if documented)

**Step 3:** Verify with user
- Contact user immediately
- Confirm if action was authorized
- If not authorized, assume compromise

**Step 4:** Take action
- Deactivate account if compromised
- Force password reset
- Review data accessed
- Notify affected parties if data breach

**Step 5:** Document incident
- Create incident report
- Log in security incident register
- Share with leadership
- Notify BMMS security team if system-wide issue

**Step 6:** Implement preventive measures
- Strengthen security settings
- Additional user training
- Policy updates
- Technical controls

### 10.5 Exporting Audit Logs

**For compliance, audit, or reporting purposes:**

**Step 1:** Configure export
- Admin Panel → Audit Logs → Export

**Step 2:** Select parameters
- Date range
- Filters (user, action, module)
- Format: CSV / Excel / PDF

**Step 3:** Export
- Click "Export Audit Logs"
- File generated and downloaded

**Example Export (CSV):**
```
Timestamp,User,Email,IP Address,Action,Module,Details
2025-10-14 09:15:32,Juan Dela Cruz,juan@moa.gov.ph,192.168.1.105,Budget Created,Budgeting,"Budget: FY2025, Amount: PHP50M"
2025-10-14 09:20:15,Maria Santos,maria@moa.gov.ph,192.168.1.110,Plan Updated,Planning,"Plan: Strategic Plan 2025, Status: Approved"
...
```

**Use Cases:**
- Annual audit compliance
- Security incident investigation
- Performance review (user activity analysis)
- Compliance reporting to OCM or oversight bodies

[SCREENSHOT: Export audit logs interface]

---

## 11. Troubleshooting

### 11.1 Common Administrative Issues

**Issue 1: User Cannot Log In**

**Symptoms:**
- User enters correct email and password
- Error: "Invalid credentials" or "Account not found"

**Troubleshooting:**

**Step 1:** Verify account exists
- Admin Panel → Users → Search for user
- If not found, create account

**Step 2:** Check account status
- Status: Active / Inactive / Locked / Deactivated?
- If Inactive: Activate account
- If Locked: Unlock account
- If Deactivated: Cannot be reactivated (need to create new account)

**Step 3:** Verify email address
- Is email correct?
- Common mistake: Typos in email
- Update email if incorrect

**Step 4:** Reset password
- Generate temporary password
- Share with user securely
- Require password change on next login

**Step 5:** Check IP whitelisting (if enabled)
- Is user accessing from whitelisted IP?
- If not, add user's IP to whitelist or disable IP whitelisting

---

**Issue 2: User Has Role But Cannot Access Module**

**Symptoms:**
- User assigned Budget Officer role
- Cannot see Budgeting Module

**Troubleshooting:**

**Step 1:** Verify module enabled
- Admin Panel → Modules → Check if Budgeting Module enabled
- If disabled, enable module

**Step 2:** Verify role assignment
- Admin Panel → Users → [User] → Manage Roles
- Check if Budget Officer role actually assigned
- Assign if missing

**Step 3:** Check role permissions
- Admin Panel → Roles → Budget Officer → Permissions
- Verify "Budgeting Module Access" is checked
- Update permissions if needed

**Step 4:** Force session refresh
- Ask user to log out completely
- Close all browser tabs
- Clear browser cache
- Log back in
- Check if module now visible

---

**Issue 3: Approval Workflow Not Working**

**Symptoms:**
- User submits budget proposal
- Approver not notified
- Proposal stuck in "Pending" status

**Troubleshooting:**

**Step 1:** Verify workflow configured
- Admin Panel → Workflows → Budget Approval
- Check if workflow exists and is active
- If not configured, configure workflow

**Step 2:** Check approver assignment
- Review workflow approval levels
- Verify approvers assigned to each level
- Ensure approvers have required roles

**Step 3:** Verify email notifications enabled
- Admin Panel → Organization → Notification Settings
- Check if email notifications enabled
- Test email delivery

**Step 4:** Check approver account status
- Admin Panel → Users → [Approver]
- Verify account active
- Verify email address correct

**Step 5:** Manual notification (workaround)
- Contact approver directly
- Provide link to pending approval
- While investigating root cause

---

**Issue 4: Audit Logs Missing or Incomplete**

**Symptoms:**
- Expected activities not appearing in audit logs
- Date gaps in logs

**Troubleshooting:**

**Step 1:** Verify date range
- Ensure search date range includes expected activities
- Try expanding date range

**Step 2:** Check filters
- Remove all filters
- Search again
- Filters may be excluding expected entries

**Step 3:** Contact BMMS support
- If logs truly missing, this is system-level issue
- Provide details: date range, missing activities
- BMMS team will investigate database

**Note:** Audit logs cannot be edited or deleted by users (including Administrators). If logs are missing, it's a technical issue requiring BMMS support.

---

**Issue 5: Organization Settings Not Saving**

**Symptoms:**
- Administrator changes settings
- Clicks "Save"
- Settings revert to previous values

**Troubleshooting:**

**Step 1:** Check for validation errors
- Look for error messages on form
- Ensure all required fields completed
- Ensure values within valid ranges

**Step 2:** Check browser compatibility
- Use supported browser (Chrome, Firefox, Edge)
- Update browser to latest version
- Disable browser extensions temporarily

**Step 3:** Check internet connection
- Ensure stable connection
- Try refreshing page
- Re-enter changes and save

**Step 4:** Check administrator permissions
- Verify you have Administrator role
- Verify not using restricted Admin account (if such exists)

**Step 5:** Contact BMMS support
- If issue persists, may be technical problem
- Provide screenshot of settings being changed
- Support team will investigate

### 11.2 Getting Help

**Support Resources:**

**1. Administrator Help Center:**
- Access: Admin Panel → Help
- Comprehensive admin guides
- Video tutorials
- FAQs

**2. BMMS Technical Support:**
- Email: admin-support@bmms.barmm.gov.ph
- Phone: [Support Number]
- Hours: Monday-Friday, 8:00 AM - 5:00 PM
- 24/7 emergency hotline for critical issues

**3. Administrator Community:**
- BMMS Administrators Network
- Monthly virtual meetups
- Share solutions and best practices
- Access peer support

**4. Training Resources:**
- Quarterly administrator training sessions
- Recorded webinars
- User guide library
- Release notes and updates

**When Contacting Support:**

Provide:
- Your name, organization, role
- Description of issue
- Steps to reproduce
- Screenshots or screen recording
- User accounts affected (if applicable)
- Urgency level (Low, Medium, High, Critical)

**Urgency Levels:**

**Critical:**
- System down, no one can access
- Security breach
- Data loss
- Response time: Within 1 hour

**High:**
- Major functionality not working
- Multiple users affected
- Compliance risk
- Response time: Within 4 hours

**Medium:**
- Single user or feature affected
- Workaround available
- Response time: Within 24 hours

**Low:**
- Minor issue
- Enhancement request
- General question
- Response time: Within 48 hours

---

## 12. Best Practices

### 12.1 User Management Best Practices

**1. Create Accounts Promptly**
- New staff should have accounts on Day 1
- Enables immediate productivity
- Prevents workarounds (account sharing)

**2. Use Strong Password Policies**
- Enforce complexity requirements
- Require regular password changes (90 days)
- Prevent password reuse

**3. Implement 2FA**
- Require 2FA for all Administrators (minimum)
- Encourage 2FA for all users
- Significantly improves security

**4. Apply Principle of Least Privilege**
- Assign only roles users need
- Don't make everyone an Administrator
- Review permissions regularly

**5. Deactivate Promptly**
- Deactivate accounts same day employee leaves
- Don't wait for HR processing
- Security risk to delay

**6. Never Share Accounts**
- Each person must have own account
- Sharing accounts violates audit trail
- Makes accountability impossible

**7. Regular Account Reviews**
- Quarterly review of all accounts
- Verify users still need access
- Deactivate unused accounts

### 12.2 Security Best Practices

**1. Regular Security Audits**
- Monthly review of audit logs
- Quarterly security assessment
- Annual penetration testing (coordinate with BMMS team)

**2. Stay Updated**
- Keep BMMS updated (BMMS team handles this)
- Update your knowledge (attend training, read release notes)
- Update security policies as threats evolve

**3. Educate Users**
- Conduct security awareness training
- Teach password hygiene
- Warn about phishing
- Promote 2FA adoption

**4. Monitor Continuously**
- Daily review of critical security events
- Real-time alerts for suspicious activity
- Proactive threat detection

**5. Incident Response Plan**
- Have plan before incident occurs
- Know who to contact
- Know what actions to take
- Practice incident response

**6. Backup Access**
- Ensure multiple Administrators
- Document access procedures
- Test backup access methods
- Prevent single point of failure

### 12.3 Configuration Best Practices

**1. Document Everything**
- Document all configuration changes
- Maintain configuration register
- Include rationale for changes
- Enables knowledge transfer

**2. Test Before Deploying**
- Test workflows before activating
- Test settings in sandbox if available
- Involve key users in testing
- Prevents disruptions

**3. Change Management**
- Communicate changes to users in advance
- Provide training on new features
- Monitor adoption
- Gather feedback

**4. Version Control**
- Keep track of configuration versions
- Document when changes made
- Enable rollback if needed
- Especially important for workflows

**5. Standardize**
- Use consistent naming conventions
- Apply uniform settings across departments
- Document standards
- Makes system easier to manage

### 12.4 Workflow Management Best Practices

**1. Keep Workflows Simple**
- Fewer steps = faster approvals
- Only required approvers
- Avoid bottlenecks

**2. Define Clear Criteria**
- Approval criteria should be explicit
- Approvers know what to look for
- Reduces subjective decisions
- Speeds approvals

**3. Set Realistic Timelines**
- Timelines should be achievable
- Account for approver workload
- Build in buffer time
- Monitor actual vs. planned timelines

**4. Enable Delegations**
- Allow approvers to delegate when away
- Prevents workflow stalls
- Maintain backup approvers

**5. Monitor Workflow Performance**
- Track approval times
- Identify bottlenecks
- Optimize workflows based on data
- Continuous improvement

### 12.5 Audit and Compliance Best Practices

**1. Regular Log Reviews**
- Daily: Critical security events
- Weekly: User activity summary
- Monthly: Comprehensive audit log review
- Make it a habit

**2. Automated Alerts**
- Configure alerts for critical events
- Failed logins, unusual access, bulk exports
- Real-time notification
- Faster response

**3. Compliance Reporting**
- Generate compliance reports regularly
- Share with leadership
- Demonstrate accountability
- Identify compliance gaps

**4. Retention Compliance**
- Respect retention policies
- Don't delete logs prematurely
- Archive properly
- Meet legal requirements

**5. Third-Party Audits**
- Welcome external audits
- Facilitate auditor access
- Learn from audit findings
- Demonstrate transparency

---

## Appendix A: Administrator Checklist

**Daily Tasks:**
- ☐ Review security alerts
- ☐ Process new account requests
- ☐ Reset forgotten passwords
- ☐ Unlock accounts if needed

**Weekly Tasks:**
- ☐ Review audit logs
- ☐ Check system health
- ☐ Update user roles as needed
- ☐ Respond to support requests

**Monthly Tasks:**
- ☐ Comprehensive security audit
- ☐ Review all user accounts
- ☐ Generate usage reports
- ☐ Update documentation

**Quarterly Tasks:**
- ☐ Full security assessment
- ☐ Review and update workflows
- ☐ Compliance reporting
- ☐ User training sessions

**Annual Tasks:**
- ☐ Comprehensive system review
- ☐ Update security policies
- ☐ Budget planning for BMMS
- ☐ Strategic planning for system improvements

---

## Appendix B: Glossary

**2FA:** Two-Factor Authentication - Additional security layer beyond password

**BARMM:** Bangsamoro Autonomous Region in Muslim Mindanao

**BMMS:** Bangsamoro Ministerial Management System

**Bill No. 325:** Parliament legislation establishing BARMM budget framework

**Deactivated Account:** Permanently disabled account (cannot reactivate)

**Inactive Account:** Temporarily disabled account (can reactivate)

**MOA:** Ministry, Office, or Agency within BARMM government

**Multi-Tenant:** Architecture where each organization has isolated data space

**OCM:** Office of the Chief Minister

**Role:** Set of permissions granted to user

**Workflow:** Structured approval process

---

## Appendix C: Quick Reference Card

**Create User:**
Admin Panel → Users → Create User Account

**Reset Password:**
Admin Panel → Users → [User] → Reset Password

**Assign Role:**
Admin Panel → Users → [User] → Manage Roles → Add Role

**Enable Module:**
Admin Panel → Modules → [Module] → Enable

**Configure Workflow:**
Admin Panel → Workflows → [Workflow] → Configure

**View Audit Logs:**
Admin Panel → Audit Logs

**Security Settings:**
Admin Panel → Security

**Get Help:**
Admin Panel → Help or contact admin-support@bmms.barmm.gov.ph

---

**End of Administrator Training Guide**

For additional assistance, contact BMMS Admin Support or refer to the Administrator Help Center in BMMS.

**Remember:** As an Administrator, you are the guardian of your organization's BMMS instance. Your diligence in user management, security, and compliance ensures BMMS serves your MOA effectively and securely.
