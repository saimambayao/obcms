# Phase 2B Budget Execution - User Journey Guide

**Date:** October 13, 2025
**Module:** Budget Execution (Parliament Bill No. 325 Section 78)

## Overview

This guide shows the complete user journey through the Budget Execution module, from initial dashboard access to final payment recording.

## User Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      BUDGET EXECUTION DASHBOARD                  │
│                   /budget/execution/                             │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Approved   │  │   Allotted   │  │  Obligated   │         │
│  │   ₱100M      │  │   ₱75M       │  │   ₱50M       │         │
│  │   (Amber)    │  │   (Blue)     │  │  (Purple)    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          Quarterly Execution Chart (Chart.js)            │  │
│  │  Q1 ▂▂▂▂  Q2 ▅▅▅▅  Q3 ▇▇▇▇  Q4 ████                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  [Release Allotment] [Record Obligation] [Record Payment]      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ├──────────────┬──────────────┬──────────────┐
                              ▼              ▼              ▼              ▼
                    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
                    │  ALLOTMENTS  │ │ OBLIGATIONS  │ │DISBURSEMENTS │
                    │     VIEW     │ │     VIEW     │ │     VIEW     │
                    └──────────────┘ └──────────────┘ └──────────────┘
```

## Journey 1: Release Quarterly Allotment

### Step 1: Access Dashboard
**URL:** `/budget/execution/`
**Role:** Budget Officer or Finance Director

**What User Sees:**
```
┌─────────────────────────────────────────┐
│  Budget Execution Dashboard             │
│                                          │
│  ┌────────┐ ┌────────┐ ┌────────┐      │
│  │Approved│ │Allotted│ │Obligate│      │
│  │ ₱100M  │ │ ₱75M   │ │ ₱50M   │      │
│  └────────┘ └────────┘ └────────┘      │
│                                          │
│  Quick Actions:                          │
│  [Release Allotment] ← Click here       │
└─────────────────────────────────────────┘
```

### Step 2: Release Allotment Form
**URL:** `/budget/execution/allotments/release/`

**Form Fields:**
```
┌─────────────────────────────────────────────────┐
│  Release Quarterly Allotment                    │
│                                                  │
│  Program Budget: [Select Program ▼]             │
│  ┌─────────────────────────────────────────┐   │
│  │ Budget Info (auto-loads via HTMX):      │   │
│  │ Approved: ₱25M                           │   │
│  │ Already Allotted: ₱15M                   │   │
│  │ Remaining: ₱10M                          │   │
│  └─────────────────────────────────────────┘   │
│                                                  │
│  Quarter: [Q1 ▼]                                │
│  Amount: [0.00 ________________]                │
│  Release Date: [2025-10-13 ___]                 │
│  Allotment Order #: [AO-2025-001 ________]     │
│  Notes: [________________________]              │
│                                                  │
│  [Cancel] [Release Allotment]                   │
└─────────────────────────────────────────────────┘
```

**Validation:**
- ✅ Program budget must have approved amount
- ✅ Quarter must not have existing allotment
- ✅ Amount must not exceed remaining budget
- ✅ All required fields filled

### Step 3: View Allotment Details
**URL:** `/budget/execution/allotments/<uuid>/`

**Success View:**
```
┌─────────────────────────────────────────────────┐
│  Allotment Q1 - Community Development Program   │
│  Status: [Released]                              │
│                                                  │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │
│  │ Total  │ │Obligate│ │Remainin│ │Utilizat│   │
│  │ ₱10M   │ │ ₱2M    │ │ ₱8M    │ │  20%   │   │
│  └────────┘ └────────┘ └────────┘ └────────┘   │
│                                                  │
│  Obligations:                                    │
│  ┌──────────────────────────────────────────┐  │
│  │ No obligations yet                       │  │
│  │ [Create Obligation] ← Next step          │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## Journey 2: Create Obligation

### Step 1: Access Obligation Form
**URL:** `/budget/execution/obligations/create/`
**Role:** Finance Staff or Budget Officer

**Form:**
```
┌─────────────────────────────────────────────────┐
│  Record Obligation                               │
│                                                  │
│  Allotment: [Select Allotment ▼]                │
│  ┌─────────────────────────────────────────┐   │
│  │ Allotment Info (auto-loads via HTMX):   │   │
│  │ Total: ₱10M                              │   │
│  │ Obligated: ₱2M                           │   │
│  │ Available: ₱8M                           │   │
│  └─────────────────────────────────────────┘   │
│                                                  │
│  Description: [Purchase Order #12345      ]     │
│  Amount: [0.00 ________________]                │
│  Obligation Date: [2025-10-13 ___]             │
│  Document Reference: [PO-2025-001 ______]      │
│  Monitoring Entry: [Optional ▼]                 │
│  Notes: [________________________]              │
│                                                  │
│  [Cancel] [Record Obligation]                   │
└─────────────────────────────────────────────────┘
```

**Validation:**
- ✅ Allotment must be released or partially utilized
- ✅ Amount must not exceed available balance
- ✅ Description required
- ✅ Document reference recommended

### Step 2: View Obligation Details
**URL:** `/budget/execution/obligations/<uuid>/`

**Success View:**
```
┌─────────────────────────────────────────────────┐
│  Obligation: Purchase Order #12345               │
│  Status: [Committed]                             │
│                                                  │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │
│  │ Total  │ │Disbursed│ │Remainin│ │ Payment│   │
│  │ ₱5M    │ │ ₱0     │ │ ₱5M    │ │   0    │   │
│  └────────┘ └────────┘ └────────┘ └────────┘   │
│                                                  │
│  Quick Actions:                                  │
│  [Record Payment] ← Next step                    │
│                                                  │
│  Disbursements:                                  │
│  ┌──────────────────────────────────────────┐  │
│  │ No disbursements yet                     │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## Journey 3: Record Disbursement (Payment)

### Step 1: Access Payment Form
**URL:** `/budget/execution/disbursements/record/`
**Role:** Finance Staff, Budget Officer, or Disbursement Officer

**Form:**
```
┌─────────────────────────────────────────────────┐
│  Record Payment (Disbursement)                   │
│                                                  │
│  Obligation: [Select Obligation ▼]              │
│  ┌─────────────────────────────────────────┐   │
│  │ Obligation Info (auto-loads via HTMX):  │   │
│  │ Total: ₱5M                               │   │
│  │ Disbursed: ₱0                            │   │
│  │ Available: ₱5M                           │   │
│  └─────────────────────────────────────────┘   │
│                                                  │
│  Amount: [0.00 ________________]                │
│  Payment Date: [2025-10-13 ___]                 │
│  Payee: [ABC Construction Co. ___________]      │
│  Payment Method: [Bank Transfer ▼]              │
│  Check Number: [Optional ___________]           │
│  Voucher Number: [DV-2025-001 ________]         │
│  Notes: [________________________]              │
│                                                  │
│  [Cancel] [Record Payment]                      │
└─────────────────────────────────────────────────┘
```

**Validation:**
- ✅ Obligation must be committed or partially disbursed
- ✅ Amount must not exceed available balance
- ✅ Payee required
- ✅ Payment method required
- ✅ Voucher number recommended

### Step 2: View Payment Details
**URL:** `/budget/execution/disbursements/<uuid>/`

**Success View:**
```
┌─────────────────────────────────────────────────┐
│  Payment to ABC Construction Co.                 │
│  Status: [Completed]                             │
│                                                  │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │
│  │ Amount │ │ Method │ │Reference│ │  Line  │   │
│  │ ₱5M    │ │  Bank  │ │DV-2025-│ │ Items  │   │
│  │        │ │Transfer│ │  001   │ │   0    │   │
│  └────────┘ └────────┘ └────────┘ └────────┘   │
│                                                  │
│  Related Obligation:                             │
│  ┌──────────────────────────────────────────┐  │
│  │ PO #12345 - ₱5M                          │  │
│  │ Status: Fully Disbursed ✅               │  │
│  │ [View Obligation]                        │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  Payment Information:                            │
│  Payee: ABC Construction Co.                     │
│  Date: October 13, 2025                          │
│  Program: Community Development                  │
│  Quarter: Q1                                     │
└─────────────────────────────────────────────────┘
```

## Journey 4: Monitor Budget Execution

### Dashboard Real-Time Widgets

**Recent Transactions (Auto-refreshes every 30s):**
```
┌───────────────────────────────────────┐
│  Recent Transactions                  │
│                                        │
│  ⚡ Payment to ABC Construction        │
│     ₱5M • Oct 13, 2025                │
│                                        │
│  📝 Obligation: PO #12345             │
│     ₱5M • Oct 13, 2025                │
│                                        │
│  💰 Q1 Allotment Released             │
│     ₱10M • Oct 13, 2025               │
└───────────────────────────────────────┘
```

**Pending Approvals (Auto-refreshes every 30s):**
```
┌───────────────────────────────────────┐
│  Pending Approvals                [3] │
│                                        │
│  ⏳ Q2 Allotment - Education Program  │
│     ₱8M • Awaiting approval           │
│     [Approve] [Reject]                │
│                                        │
│  ⏳ Q3 Allotment - Health Services    │
│     ₱6M • Awaiting approval           │
│     [Approve] [Reject]                │
└───────────────────────────────────────┘
```

**Budget Alerts (Auto-refreshes every 60s):**
```
┌───────────────────────────────────────┐
│  Budget Alerts                    [2] │
│                                        │
│  ⚠️  Q1 Community Dev - 95% utilized  │
│     Only ₱500K remaining              │
│                                        │
│  ⚠️  Q2 Education - 87% utilized      │
│     Only ₱1.2M remaining              │
└───────────────────────────────────────┘
```

## User Roles & Permissions

### Finance Director
**Highest Access Level**
```
✅ View all financial reports
✅ Approve allotments
✅ Release allotments
✅ Create obligations
✅ Record disbursements
✅ Override budget constraints (with justification)
```

### Budget Officer
**Standard Access Level**
```
✅ View financial reports
✅ Release allotments
✅ Create obligations
✅ Record disbursements
❌ Approve allotments
❌ Override constraints
```

### Finance Staff
**Basic Access Level**
```
✅ View financial reports
❌ Release allotments
✅ Create obligations
✅ Record disbursements
❌ Approve allotments
❌ Override constraints
```

### Disbursement Officer
**Limited Access Level**
```
✅ View disbursement records
❌ Release allotments
❌ Create obligations
✅ Record disbursements only
❌ Approve allotments
❌ Override constraints
```

## Navigation Flow

### Primary Navigation
```
Dashboard → Allotments → Obligations → Disbursements
    ↓           ↓            ↓             ↓
 [Release]   [Create]     [Record]      [View]
    ↓           ↓            ↓             ↓
 Detail      Detail       Detail        Detail
```

### Quick Actions
Every detail page provides quick actions:
```
Allotment Detail:
├─ Create Obligation
├─ View Program Budget
└─ Back to List

Obligation Detail:
├─ Record Payment
├─ View Allotment
├─ Edit Obligation
└─ Back to List

Disbursement Detail:
├─ View Obligation
├─ View Allotment
└─ Back to List
```

## Mobile Experience

All views are fully responsive:

**Mobile Dashboard (320px+):**
```
┌────────────────┐
│ Budget Exec    │
│                │
│  ┌──────────┐ │
│  │ Approved │ │
│  │  ₱100M   │ │
│  └──────────┘ │
│                │
│  ┌──────────┐ │
│  │ Allotted │ │
│  │  ₱75M    │ │
│  └──────────┘ │
│                │
│ [Release]      │
│ [Obligate]     │
│ [Pay]          │
└────────────────┘
```

**Touch Targets:**
All buttons and links are **minimum 48px** for easy tapping (WCAG 2.1 AA compliance).

## Keyboard Navigation

Full keyboard support:
```
Tab       → Navigate between fields
Enter     → Submit forms
Esc       → Cancel/close modals
Arrow Up  → Navigate table rows
Arrow Down→ Navigate table rows
```

## Success Messages

After each operation, users see clear feedback:

**Allotment Released:**
```
┌───────────────────────────────────────┐
│ ✅ Success!                           │
│ Allotment released successfully:      │
│ Q1 for Community Development (₱10M)   │
└───────────────────────────────────────┘
```

**Obligation Created:**
```
┌───────────────────────────────────────┐
│ ✅ Success!                           │
│ Obligation recorded successfully:     │
│ Purchase Order #12345 (₱5M)           │
└───────────────────────────────────────┘
```

**Payment Recorded:**
```
┌───────────────────────────────────────┐
│ ✅ Success!                           │
│ Disbursement recorded successfully:   │
│ ABC Construction Co. (₱5M)            │
└───────────────────────────────────────┘
```

## Error Handling

Clear error messages guide users:

**Insufficient Balance:**
```
┌───────────────────────────────────────┐
│ ❌ Error                              │
│ Total obligations (₱12M) would exceed │
│ allotment (₱10M).                     │
│ Available: ₱8M                        │
└───────────────────────────────────────┘
```

**Duplicate Allotment:**
```
┌───────────────────────────────────────┐
│ ❌ Error                              │
│ Allotment for Community Dev Q1        │
│ already exists. Cannot create         │
│ duplicate allotment.                  │
└───────────────────────────────────────┘
```

## Summary

The Budget Execution module provides a complete, user-friendly workflow with:

✅ **Clear Navigation** - Logical flow from allotment to payment
✅ **Real-Time Feedback** - HTMX widgets, instant validation
✅ **Role-Based Access** - Appropriate permissions per role
✅ **Mobile-Friendly** - Responsive design, large touch targets
✅ **Accessibility** - WCAG 2.1 AA compliant
✅ **Error Prevention** - Triple-layer validation
✅ **Success Feedback** - Clear confirmation messages

**Users can confidently manage their budget execution with minimal training.**

---
**Date:** October 13, 2025
**Status:** Production-Ready ✅
**Documentation:** Complete User Journey Guide
