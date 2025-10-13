# RBAC HTMX Flow Diagrams

## Current Implementation (BROKEN) ❌

### User Approval Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     USER CLICKS "APPROVE"                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  HTMX: hx-post="/user-approval/123/"                        │
│        hx-target="#user-row-123"                             │
│        hx-swap="delete swap:300ms"                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend: user_approval_action(request, 123)                │
│    - Sets user.is_active = True                             │
│    - Returns HTTP 200 (empty response)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  ✅ Row disappears (CORRECT)                                 │
│  ❌ Metrics unchanged (WRONG - shows old count)              │
│  ❌ Parent container triggers full page reload (WRONG)       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  💥 ENTIRE PAGE RELOADS                                      │
│     hx-trigger="refresh-page from:body"                      │
│     hx-target="body" hx-swap="innerHTML"                     │
└─────────────────────────────────────────────────────────────┘
```

**Problem:** Full page reload defeats HTMX purpose!

---

## Fixed Implementation ✅

### User Approval Flow (Corrected)

```
┌─────────────────────────────────────────────────────────────┐
│                     USER CLICKS "APPROVE"                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  HTMX: hx-post="/user-approval/123/"                        │
│        hx-target="#user-row-123"                             │
│        hx-swap="delete swap:300ms"                           │
│        hx-indicator="#approve-loading"                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend: user_approval_action(request, 123)                │
│    - Sets user.is_active = True                             │
│    - Renders metrics fragment                               │
│    - Returns HTML with OOB swap                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Response HTML:                                              │
│  ```                                                         │
│  <div id="approval-metrics" hx-swap-oob="innerHTML">        │
│    <div>Pending: 5</div>  ← Updated count                   │
│  </div>                                                      │
│  ```                                                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  ✅ Row disappears smoothly (300ms animation)                │
│  ✅ Metrics update instantly (OOB swap)                      │
│  ✅ Success toast shows                                      │
│  ✅ NO page reload                                           │
└─────────────────────────────────────────────────────────────┘
```

**Result:** Instant UI with all regions updated!

---

## Modal Interaction Flow

### Current (BROKEN) ❌

```
┌─────────────────────────────────────────────────────────────┐
│         USER CLICKS "PERMISSIONS" BUTTON                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  JavaScript: onclick="openRbacModal()"                       │
│    → Modal opens IMMEDIATELY (empty)                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  💥 USER SEES EMPTY MODAL (flicker)                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  HTMX: hx-get="/rbac/user/123/permissions/"                 │
│    → Request sent AFTER modal opened                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend returns HTML → Swaps into #rbac-modal-content       │
└─────────────────────────────────────────────────────────────┘
```

**Problem:** Modal opens before content loads - poor UX!

---

### Fixed (CORRECT) ✅

```
┌─────────────────────────────────────────────────────────────┐
│         USER CLICKS "PERMISSIONS" BUTTON                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  HTMX: hx-on::before-request="openRbacModal()"              │
│    → Modal opens with loading spinner                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  ✅ USER SEES LOADING SPINNER                                │
│     <i class="fas fa-spinner fa-spin"></i>                   │
│     "Loading permissions..."                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  HTMX: hx-get="/rbac/user/123/permissions/"                 │
│        hx-swap="innerHTML show:#rbac-modal:top"              │
│    → Request sent, content loading                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend returns HTML → Swaps into modal                     │
│  ✅ Smooth transition from spinner to content                │
└─────────────────────────────────────────────────────────────┘
```

**Result:** Smooth loading experience!

---

## Role Assignment with Multi-Region Update

### Current (INCOMPLETE) ⚠️

```
┌─────────────────────────────────────────────────────────────┐
│              USER ASSIGNS ROLE IN MODAL                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  HTMX: hx-post="/rbac/user/123/assign-role/"                │
│        hx-target="#rbac-modal-content"                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend: Creates UserRole, returns updated modal HTML       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  ✅ Modal content updates (shows new role)                   │
│  ❌ Main user list UNCHANGED (stale)                         │
│  ❌ Metrics UNCHANGED (stale)                                │
└─────────────────────────────────────────────────────────────┘
```

**Problem:** Only modal updates - rest of UI is stale!

---

### Fixed with OOB Swaps ✅

```
┌─────────────────────────────────────────────────────────────┐
│              USER ASSIGNS ROLE IN MODAL                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  HTMX: hx-post="/rbac/user/123/assign-role/"                │
│        hx-target="#rbac-modal-content"                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend Response:                                           │
│  ```html                                                     │
│  <div id="rbac-modal-content">                              │
│    <!-- Updated modal content -->                            │
│  </div>                                                      │
│                                                              │
│  <!-- OOB Swap #1: User Row -->                             │
│  <tr id="user-row-123" hx-swap-oob="outerHTML">             │
│    <td>John Doe</td>                                         │
│    <td>Admin, Editor ← NEW ROLE</td>                        │
│  </tr>                                                       │
│                                                              │
│  <!-- OOB Swap #2: Metrics -->                              │
│  <div id="rbac-metrics" hx-swap-oob="innerHTML">            │
│    <div>Active Roles: 15 ← UPDATED</div>                    │
│  </div>                                                      │
│  ```                                                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  ✅ Modal content updates                                    │
│  ✅ Main user list updates (shows new role badge)           │
│  ✅ Metrics update (active roles count increments)          │
│  ✅ Success toast displays                                   │
│  ✅ ALL IN ONE REQUEST - No page reload                     │
└─────────────────────────────────────────────────────────────┘
```

**Result:** Entire UI updates instantly from single response!

---

## Tab Lazy Loading

### Current (INEFFICIENT) ⚠️

```
┌─────────────────────────────────────────────────────────────┐
│                    PAGE LOADS                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Tab 1 (Approvals) - VISIBLE                                 │
│  Tab 2 (RBAC) - HIDDEN (display:none)                       │
│    <div hx-trigger="load once">  ← FIRES EVEN WHEN HIDDEN   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  💥 HTMX loads hidden tab content                            │
│     - Wastes bandwidth                                       │
│     - User may never see this tab                           │
└─────────────────────────────────────────────────────────────┘
```

---

### Fixed with `revealed` Trigger ✅

```
┌─────────────────────────────────────────────────────────────┐
│                    PAGE LOADS                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Tab 1 (Approvals) - VISIBLE                                 │
│  Tab 2 (RBAC) - HIDDEN                                       │
│    <div hx-trigger="revealed once">  ← WAITS                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  ✅ No request sent (tab is hidden)                          │
└─────────────────────────────────────────────────────────────┘
                              │
                (USER CLICKS TAB 2)
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  JavaScript: showTab('permissions')                          │
│    → tab-pane.classList.remove('hidden')                     │
│    → htmx.trigger(tab-pane, 'revealed')                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  ✅ NOW HTMX fires request                                   │
│     (only when user actually views the tab)                  │
└─────────────────────────────────────────────────────────────┘
```

**Result:** Efficient lazy loading - content loads only when needed!

---

## Error Handling Flow

### Current (BROKEN) ❌

```
┌─────────────────────────────────────────────────────────────┐
│              HTMX REQUEST FAILS (500 error)                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  💥 BLANK SCREEN or unchanged UI                             │
│     - No error message                                       │
│     - User confused                                          │
│     - Button still clickable                                │
└─────────────────────────────────────────────────────────────┘
```

---

### Fixed with Error Handlers ✅

```
┌─────────────────────────────────────────────────────────────┐
│              HTMX REQUEST FAILS (500 error)                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Event: htmx:responseError fires                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  JavaScript Handler:                                         │
│    document.body.addEventListener('htmx:responseError', ...) │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  ✅ Error Toast Shows:                                       │
│     ┌───────────────────────────────────────────┐          │
│     │ ⚠️ Error                                  │          │
│     │ Failed to assign role. Please try again. │          │
│     └───────────────────────────────────────────┘          │
│                                                              │
│  ✅ Button re-enabled                                        │
│  ✅ User can retry                                           │
└─────────────────────────────────────────────────────────────┘
```

**Result:** Clear error feedback, recoverable state!

---

## Key Takeaways

### ❌ Anti-Patterns Found
1. **Full page reload** with `hx-target="body"`
2. **Modal opened in onclick** before HTMX request
3. **No OOB swaps** for multi-region updates
4. **`hx-trigger="load"`** on hidden elements
5. **No error handlers** for failed requests

### ✅ Correct Patterns
1. **Target specific elements** (`#user-row-123`, `#metrics`)
2. **Open modal via HTMX events** (`hx-on::before-request`)
3. **Use OOB swaps** (`hx-swap-oob="innerHTML"`)
4. **Use `revealed` trigger** for lazy loading
5. **Global error handler** (`htmx:responseError`)

### 🎯 Implementation Priority
1. **CRITICAL:** Fix full page reload (1 hour)
2. **CRITICAL:** Add OOB swaps (2 hours)
3. **HIGH:** Fix modal lifecycle (1 hour)
4. **HIGH:** Add error handling (1 hour)
5. **MEDIUM:** Fix lazy loading (30 min)

**Total estimated effort for critical fixes: 5-6 hours**

---

**See also:**
- [Full Review](./RBAC_FRONTEND_HTMX_REVIEW.md) - Detailed analysis
- [Quick Fix Guide](./RBAC_HTMX_QUICK_FIX_GUIDE.md) - Code examples
- [Summary](./RBAC_REVIEW_SUMMARY.md) - Executive overview
