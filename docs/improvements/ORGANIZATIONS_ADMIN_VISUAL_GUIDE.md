# Organizations Admin Visual Guide

**Visual reference for admin interface appearance and behavior**

---

## Organization List View

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║ Django Administration                                      [admin] [Log out]   ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Home › Organizations › Organizations                                           ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                 ║
║ Organizations                                       [+ Add organization]       ║
║                                                                                 ║
║ ┌─────────────────────────────────────────────────────────────────────────┐  ║
║ │ 🔍 Search organizations: [____________________________] [Search]        │  ║
║ └─────────────────────────────────────────────────────────────────────────┘  ║
║                                                                                 ║
║ Actions: [Activate selected organizations ▼] [Go]         44 organizations    ║
║                                                                                 ║
║ ┌──┬────────┬──────────────────────┬────────────┬────────┬────────┬─────────┐ ║
║ │☐ │ Code   │ Name                 │ Type       │ Status │ Pilot  │ Modules │ ║
║ ├──┼────────┼──────────────────────┼────────────┼────────┼────────┼─────────┤ ║
║ │☐ │ OOBC   │ Office for Other     │ 🏢 Office  │ Active │   -    │ MANA    │ ║
║ │  │        │ Bangsamoro...        │            │        │        │ Plan    │ ║
║ │  │        │                      │            │        │        │ Budget  │ ║
║ │  │        │                      │            │        │        │ M&E     │ ║
║ │  │        │                      │            │        │        │ Coord   │ ║
║ │  │        │                      │            │        │        │ Policy  │ ║
║ ├──┼────────┼──────────────────────┼────────────┼────────┼────────┼─────────┤ ║
║ │☐ │ MOH    │ Ministry of Health   │ 🏛️ Ministry│ Active │ 🚀 PILOT│ All 6  │ ║
║ │🟡│        │                      │            │        │        │ enabled │ ║
║ ├──┼────────┼──────────────────────┼────────────┼────────┼────────┼─────────┤ ║
║ │☐ │ MOLE   │ Ministry of Labor    │ 🏛️ Ministry│ Active │ 🚀 PILOT│ All 6  │ ║
║ │🟡│        │ and Employment       │            │        │        │ enabled │ ║
║ ├──┼────────┼──────────────────────┼────────────┼────────┼────────┼─────────┤ ║
║ │☐ │ MAFAR  │ Ministry of Agri...  │ 🏛️ Ministry│ Active │ 🚀 PILOT│ All 6  │ ║
║ │🟡│        │                      │            │        │        │ enabled │ ║
║ ├──┼────────┼──────────────────────┼────────────┼────────┼────────┼─────────┤ ║
║ │☐ │ MBHTE  │ Ministry of Basic... │ 🏛️ Ministry│Inactive│   -    │ None    │ ║
║ │  │        │                      │            │        │        │         │ ║
║ └──┴────────┴──────────────────────┴────────────┴────────┴────────┴─────────┘ ║
║                                                                                 ║
║ 1-5 of 44                                        [< 1 2 3 4 5 6 7 8 9 >]      ║
║                                                                                 ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Filters                                                                         ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ By type                                                                         ║
║   ○ All                                                                         ║
║   ○ Ministry (16)                                                              ║
║   ○ Office (10)                                                                ║
║   ○ Agency (8)                                                                 ║
║   ○ Special (7)                                                                ║
║   ○ Commission (3)                                                             ║
║                                                                                 ║
║ By active status                                                               ║
║   ○ All                                                                         ║
║   ● Active (4)                                                                 ║
║   ○ Inactive (40)                                                              ║
║                                                                                 ║
║ By pilot status                                                                ║
║   ○ All                                                                         ║
║   ○ Yes (3)                                                                    ║
║   ○ No (41)                                                                    ║
║                                                                                 ║
║ By modules                                                                     ║
║   ☐ Enable MANA                                                               ║
║   ☐ Enable Planning                                                           ║
║   ☐ Enable Budgeting                                                          ║
║   ☐ Enable M&E                                                                ║
║   ☐ Enable Coordination                                                       ║
║   ☐ Enable Policies                                                           ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**Legend:**
- 🟡 = Pilot MOA highlighting (gold background)
- Active = Green badge
- Inactive = Gray badge
- 🚀 PILOT = Gold badge
- Module badges = Colored (Blue, Purple, Green, Orange, Pink, Cyan)

---

## Organization Detail View

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║ Django Administration                                      [admin] [Log out]   ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Home › Organizations › Organizations › OOBC                                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                 ║
║ Change Organization                                                            ║
║                                                                                 ║
║ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ║
║ ┃ IDENTIFICATION                                                             ┃ ║
║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
║                                                                                 ║
║ Code:    [OOBC______] (read-only)                                             ║
║          Unique organization code                                              ║
║                                                                                 ║
║ Name:    [Office for Other Bangsamoro Communities___________________]         ║
║          Full organization name                                                ║
║                                                                                 ║
║ Acronym: [OOBC___]                                                             ║
║          Alternative acronym                                                   ║
║                                                                                 ║
║ Type:    [Office ▼]                                                            ║
║          Ministry / Office / Agency / Special / Commission                     ║
║                                                                                 ║
║ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ║
║ ┃ MODULE ACTIVATION                                                          ┃ ║
║ ┃ Enable or disable specific BMMS modules for this organization             ┃ ║
║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
║                                                                                 ║
║ ☑ Enable MANA           ☑ Enable Planning      ☑ Enable Budgeting            ║
║ ☑ Enable M&E            ☑ Enable Coordination  ☑ Enable Policies             ║
║                                                                                 ║
║ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ║
║ ┃ ► GEOGRAPHIC COVERAGE                                            (collapsed)┃ ║
║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
║                                                                                 ║
║ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ║
║ ┃ LEADERSHIP                                                                 ┃ ║
║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
║                                                                                 ║
║ Head Official:        [Atty. John Doe_________________________]               ║
║ Head Title:           [Executive Director____________________]               ║
║ Primary Focal Person: [admin                             ▼] 🔍               ║
║                                                                                 ║
║ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ║
║ ┃ ► CONTACT INFORMATION                                        (collapsed)   ┃ ║
║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
║                                                                                 ║
║ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ║
║ ┃ STATUS & ONBOARDING                                                        ┃ ║
║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
║                                                                                 ║
║ ☑ Active  (read-only)                                                          ║
║ ☐ Pilot                                                                        ║
║                                                                                 ║
║ Onboarding Date: [2024-01-15] 📅    Go-Live Date: [2024-02-01] 📅            ║
║                                                                                 ║
║ ┌─────────────────────────────────────────────────────────────────┐          ║
║ │ Membership Details:                                             │          ║
║ │                                                                 │          ║
║ │ Total Members: 12                                              │          ║
║ │ Active Members: 8                                              │          ║
║ │ Administrators: 2                                              │          ║
║ └─────────────────────────────────────────────────────────────────┘          ║
║                                                                                 ║
║ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ║
║ ┃ ORGANIZATION MEMBERSHIPS                                                   ┃ ║
║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
║                                                                                 ║
║ ┌──────────────┬─────────┬─────────┬────────┬─────────────────┬────────────┐ ║
║ │ User         │ Role    │ Primary │ Active │ Position        │ Department │ ║
║ ├──────────────┼─────────┼─────────┼────────┼─────────────────┼────────────┤ ║
║ │ admin     ▼  │ Admin▼  │   ☑    │   ☑   │ Director        │ Admin      │ ║
║ ├──────────────┼─────────┼─────────┼────────┼─────────────────┼────────────┤ ║
║ │ oobc_staff1▼ │ Staff▼  │   ☐    │   ☑   │ Planning Officer│ Planning   │ ║
║ ├──────────────┼─────────┼─────────┼────────┼─────────────────┼────────────┤ ║
║ │ oobc_staff2▼ │ Staff▼  │   ☐    │   ☑   │ Budget Officer  │ Finance    │ ║
║ └──────────────┴─────────┴─────────┴────────┴─────────────────┴────────────┘ ║
║                                                                                 ║
║ [+ Add another Organization Membership]                                        ║
║                                                                                 ║
║ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ║
║ ┃ ► AUDIT INFORMATION                                          (collapsed)   ┃ ║
║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
║                                                                                 ║
║                                                                                 ║
║                              [Save and continue editing]  [Save]  [Delete]    ║
║                                                                                 ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## Organization Membership List View

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║ Django Administration                                      [admin] [Log out]   ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Home › Organizations › Organization memberships                                ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                 ║
║ Organization Memberships                  [+ Add organization membership]     ║
║                                                                                 ║
║ ┌─────────────────────────────────────────────────────────────────────────┐  ║
║ │ 🔍 Search memberships: [_________________________] [Search]             │  ║
║ └─────────────────────────────────────────────────────────────────────────┘  ║
║                                                                                 ║
║ Actions: [Activate selected memberships ▼] [Go]               18 memberships  ║
║                                                                                 ║
║ ┌──┬─────────────┬──────────────────────┬──────────┬─────────┬──────────────┐ ║
║ │☐ │ User        │ Organization         │ Role     │ Primary │ Permissions  │ ║
║ ├──┼─────────────┼──────────────────────┼──────────┼─────────┼──────────────┤ ║
║ │☐ │ admin       │ OOBC 🏢              │ ADMIN    │   ⭐    │ 👥 📋 💰 📊 │ ║
║ │  │ (John Doe)  │ Office for Other...  │          │         │              │ ║
║ ├──┼─────────────┼──────────────────────┼──────────┼─────────┼──────────────┤ ║
║ │☐ │ moh_admin   │ MOH 🏛️               │ ADMIN    │   ⭐    │ 👥 📋 💰 📊 │ ║
║ │  │ (Jane Smith)│ Ministry of Health   │          │         │              │ ║
║ ├──┼─────────────┼──────────────────────┼──────────┼─────────┼──────────────┤ ║
║ │☐ │ moh_staff1  │ MOH 🏛️               │ STAFF    │    -    │ 📊          │ ║
║ │  │ (Bob Wilson)│ Ministry of Health   │          │         │              │ ║
║ ├──┼─────────────┼──────────────────────┼──────────┼─────────┼──────────────┤ ║
║ │☐ │ mole_admin  │ MOLE 🏛️              │ ADMIN    │   ⭐    │ 👥 📋 💰 📊 │ ║
║ │  │ (Alice Lee) │ Ministry of Labor... │          │         │              │ ║
║ ├──┼─────────────┼──────────────────────┼──────────┼─────────┼──────────────┤ ║
║ │☐ │ guest_user  │ OOBC 🏢              │ VIEWER   │    -    │ -            │ ║
║ │  │             │ Office for Other...  │          │         │              │ ║
║ └──┴─────────────┴──────────────────────┴──────────┴─────────┴──────────────┘ ║
║                                                                                 ║
║ 1-5 of 18                                            [< 1 2 3 4 >]            ║
║                                                                                 ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Filters                                                                         ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ By organization                                                                ║
║   ○ All                                                                         ║
║   ○ OOBC (5)                                                                   ║
║   ○ MOH (6)                                                                    ║
║   ○ MOLE (4)                                                                   ║
║   ○ MAFAR (3)                                                                  ║
║                                                                                 ║
║ By role                                                                        ║
║   ○ All                                                                         ║
║   ○ Admin (4)                                                                  ║
║   ○ Manager (3)                                                                ║
║   ○ Staff (9)                                                                  ║
║   ○ Viewer (2)                                                                 ║
║                                                                                 ║
║ By primary                                                                     ║
║   ○ All                                                                         ║
║   ○ Yes (4)                                                                    ║
║   ○ No (14)                                                                    ║
║                                                                                 ║
║ By active status                                                               ║
║   ● All                                                                         ║
║   ○ Active (15)                                                                ║
║   ○ Inactive (3)                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**Legend:**
- ADMIN = Red badge
- MANAGER = Orange badge
- STAFF = Blue badge
- VIEWER = Gray badge
- ⭐ = Primary organization indicator (green)
- 👥 = Can manage users
- 📋 = Can approve plans
- 💰 = Can approve budgets
- 📊 = Can view reports

---

## Badge Color Reference

### Status Badges

```
┌──────────────────────────────────────────┐
│ ACTIVE                                   │  🟢 Green (#10b981)
│ Background: Green                        │
│ Text: White                              │
│ Shape: Rounded pill                      │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│ INACTIVE                                 │  ⚫ Gray (#6b7280)
│ Background: Gray                         │
│ Text: White                              │
│ Shape: Rounded pill                      │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│ 🚀 PILOT                                 │  🟡 Gold (#f59e0b)
│ Background: Gold                         │
│ Text: White                              │
│ Shape: Rounded pill                      │
│ Icon: Rocket emoji                       │
└──────────────────────────────────────────┘
```

### Module Badges

```
┌──────┐ ┌──────────┐ ┌─────────┐ ┌──────┐ ┌──────┐ ┌────────┐
│ MANA │ │ Planning │ │ Budget  │ │ M&E  │ │ Coord│ │ Policy │
│ Blue │ │  Purple  │ │  Green  │ │Orange│ │ Pink │ │  Cyan  │
└──────┘ └──────────┘ └─────────┘ └──────┘ └──────┘ └────────┘
#3b82f6   #8b5cf6      #10b981     #f59e0b  #ec4899   #06b6d4
```

### Role Badges

```
┌───────────┐ ┌──────────┐ ┌────────┐ ┌─────────┐
│   ADMIN   │ │ MANAGER  │ │ STAFF  │ │ VIEWER  │
│    Red    │ │  Orange  │ │  Blue  │ │  Gray   │
└───────────┘ └──────────┘ └────────┘ └─────────┘
  #ef4444      #f59e0b      #3b82f6    #6b7280
```

---

## Pilot MOA Row Highlighting

```
Normal Organization Row:
┌────────────────────────────────────────────────┐
│ □ MBHTE  Ministry of Basic...  Ministry  ...  │
│   Background: White (#ffffff)                  │
└────────────────────────────────────────────────┘

Pilot Organization Row:
┌────────────────────────────────────────────────┐
│ □ MOH    Ministry of Health    Ministry  ...  │  🟡 Gold Background
│   Background: Light Gold (#fffbeb)            │
│   Border-left: 4px Orange (#f59e0b)           │
└────────────────────────────────────────────────┘

Pilot Organization Row (Hover):
┌────────────────────────────────────────────────┐
│ □ MOH    Ministry of Health    Ministry  ...  │  🟡 Lighter Gold
│   Background: Lighter Gold (#fef3c7)          │
│   Border-left: 4px Orange (#f59e0b)           │
└────────────────────────────────────────────────┘
```

---

## Permission Icons Reference

```
┌──────────────────────────────────────────────┐
│ Permission                  Icon             │
├──────────────────────────────────────────────┤
│ Can Manage Users            👥               │
│ Can Approve Plans           📋               │
│ Can Approve Budgets         💰               │
│ Can View Reports            📊               │
│ None (View Only)            -                │
└──────────────────────────────────────────────┘
```

**Display Example:**
```
User with all permissions:  👥 📋 💰 📊
User with some permissions: 📋 📊
User with no permissions:   -
```

---

## Action Dropdown Visual

```
┌─────────────────────────────────────────────────────────┐
│ Actions: [Select an action to perform... ▼] [Go]       │
└─────────────────────────────────────────────────────────┘
                ▼
┌─────────────────────────────────────────────────────────┐
│ ✅ Activate selected organizations                      │
│ ❌ Deactivate selected organizations                    │
│ 🚀 Mark as pilot organizations                          │
│ 🔓 Enable all modules                                   │
│ 🔒 Disable all modules                                  │
└─────────────────────────────────────────────────────────┘
```

---

## Filter Panel Visual

```
╔══════════════════════════════════════════╗
║ Filters                                  ║
╠══════════════════════════════════════════╣
║ By type                                  ║
║   ○ All                                  ║
║   ● Ministry (16)                        ║ ← Selected
║   ○ Office (10)                          ║
║   ○ Agency (8)                           ║
║   ○ Special (7)                          ║
║   ○ Commission (3)                       ║
║                                          ║
║ [Clear filter] [Apply]                   ║
╠══════════════════════════════════════════╣
║ By active status                         ║
║   ○ All                                  ║
║   ● Active (4)                           ║ ← Selected
║   ○ Inactive (40)                        ║
║                                          ║
║ [Clear filter] [Apply]                   ║
╠══════════════════════════════════════════╣
║ By pilot status                          ║
║   ○ All                                  ║
║   ○ Yes (3)                              ║
║   ● No (41)                              ║ ← Selected
╚══════════════════════════════════════════╝
```

---

## Inline Editor Visual

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ORGANIZATION MEMBERSHIPS                                           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┌───┬─────────────┬──────┬─────────┬────────┬─────────┬──────────┐
│ # │ User        │ Role │ Primary │ Active │ Position│ Dept     │
├───┼─────────────┼──────┼─────────┼────────┼─────────┼──────────┤
│ 1 │ admin    ▼  │Admin▼│   ☑    │   ☑   │Director │Admin     │
│   │ 🔍 Search   │      │         │        │         │          │
├───┼─────────────┼──────┼─────────┼────────┼─────────┼──────────┤
│ 2 │ oobc_staff1▼│Staff▼│   ☐    │   ☑   │Officer  │Planning  │
│   │             │      │         │        │         │          │
├───┼─────────────┼──────┼─────────┼────────┼─────────┼──────────┤
│ 3 │ oobc_staff2▼│Staff▼│   ☐    │   ☑   │Officer  │Finance   │
│   │             │      │         │        │         │          │
└───┴─────────────┴──────┴─────────┴────────┴─────────┴──────────┘

[+ Add another Organization Membership]
```

---

## Autocomplete Search Visual

```
Primary Focal Person: [ad________________________] 🔍
                       ▼
                    ┌────────────────────────────────┐
                    │ admin (John Doe)               │ ← Highlighted
                    │ admin_assistant (Jane Smith)   │
                    │ oobc_admin (Bob Wilson)        │
                    └────────────────────────────────┘
                      ↑ Dropdown appears as you type
```

---

## Success Message Visual

```
┌─────────────────────────────────────────────────────────┐
│ ✅ Success                                              │
│ Successfully activated 3 organization(s).               │
│                                                [✕ Close] │
└─────────────────────────────────────────────────────────┘
```

## Warning Message Visual

```
┌─────────────────────────────────────────────────────────┐
│ ⚠️ Warning                                              │
│ Cannot deactivate OOBC (Office for Other Bangsamoro    │
│ Communities). This organization must remain active.     │
│                                                [✕ Close] │
└─────────────────────────────────────────────────────────┘
```

---

## Responsive Design (Mobile)

```
┌─────────────────────────────────┐
│ Organizations            [Menu] │
├─────────────────────────────────┤
│                                 │
│ [+ Add]                         │
│                                 │
│ [Search: ________________]      │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ OOBC                        │ │
│ │ Office for Other Bang...    │ │
│ │ 🏢 Office | Active          │ │
│ │ Modules: All 6 enabled      │ │
│ └─────────────────────────────┘ │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ MOH 🚀                      │ │
│ │ Ministry of Health          │ │
│ │ 🏛️ Ministry | Active        │ │
│ │ Modules: All 6 enabled      │ │
│ └─────────────────────────────┘ │
│                                 │
│ [Load More]                     │
└─────────────────────────────────┘
```

---

**End of Visual Guide**

This guide provides ASCII mockups of the admin interface appearance.
For actual implementation, refer to:
- `src/organizations/admin.py` - Admin code
- `src/static/admin/css/organizations_admin.css` - Styling
- `docs/improvements/ORGANIZATIONS_ADMIN_INTERFACE.md` - Full documentation
