# Calendar Cache Flow Diagram

## Current Broken Flow (Why Deleted Items Persist)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          USER DELETES WORK ITEM                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  1. HTMX DELETE Request                                                 │
│     DELETE /oobc-management/work-items/{uuid}/delete/                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  2. Django Server (work_item_delete view)                               │
│     ┌─────────────────────────────────────────────────────────────┐    │
│     │ ✅ Delete work item from database                           │    │
│     └─────────────────────────────────────────────────────────────┘    │
│     ┌─────────────────────────────────────────────────────────────┐    │
│     │ ❌ Cache invalidation (BROKEN)                              │    │
│     │                                                             │    │
│     │   Tries to delete:                                          │    │
│     │   calendar_feed:1:None:None:2025-10-01:2025-10-31           │    │
│     │                                                             │    │
│     │   But actual cached key is:                                 │    │
│     │   calendar_feed:1:None:None:2025-09-28:2025-11-08           │    │
│     │                                                             │    │
│     │   ❌ MISMATCH! Cache not invalidated!                       │    │
│     └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  3. Server Response                                                     │
│     HTTP 200 OK                                                         │
│     HX-Trigger: {"workItemDeleted": {"id": "...", "title": "..."}}     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  4. JavaScript Event Listener (oobc_calendar.html:584)                  │
│     ┌─────────────────────────────────────────────────────────────┐    │
│     │ Tries to find event by ID                                   │    │
│     │   - work-item-{uuid}                                        │    │
│     │   - coordination-event-{uuid}                               │    │
│     │   - staff-task-{uuid}                                       │    │
│     │                                                             │    │
│     │ If found:                                                   │    │
│     │   ✅ calendarEvent.remove() - Instant UI update             │    │
│     │                                                             │    │
│     │ If NOT found (ID mismatch):                                 │    │
│     │   ⚠️  calendar.refetchEvents() - Full refresh               │    │
│     └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  5. FullCalendar Refetch (if event not found by ID)                     │
│     GET /oobc-management/calendar/work-items/feed/?start=...&end=...    │
│                                                                         │
│     ┌─────────────────────────────────────────────────────────────┐    │
│     │ ❌ Browser checks local cache first (no cache headers)      │    │
│     │    Returns stale cached response                            │    │
│     └─────────────────────────────────────────────────────────────┘    │
│                                                                         │
│     If browser cache miss:                                              │
│     ┌─────────────────────────────────────────────────────────────┐    │
│     │ Request reaches Django server                               │    │
│     │ ❌ Django returns CACHED response (cache not invalidated)   │    │
│     │    Deleted item still in cached data!                       │    │
│     └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  6. RESULT: Deleted item reappears in calendar ❌                       │
│                                                                         │
│     User sees:                                                          │
│     - Item removed briefly (if ID matched)                              │
│     - Item restored after refetch (stale cache)                         │
│                                                                         │
│     OR                                                                  │
│                                                                         │
│     - Item never removed (ID didn't match)                              │
│     - Full refresh shows deleted item (stale cache)                     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Fixed Flow (Instant Removal, No Persistence)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          USER DELETES WORK ITEM                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  1. HTMX DELETE Request                                                 │
│     DELETE /oobc-management/work-items/{uuid}/delete/                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  2. Django Server (work_item_delete view)                               │
│     ┌─────────────────────────────────────────────────────────────┐    │
│     │ ✅ Delete work item from database                           │    │
│     └─────────────────────────────────────────────────────────────┘    │
│     ┌─────────────────────────────────────────────────────────────┐    │
│     │ ✅ Cache invalidation (FIXED - Version-based)               │    │
│     │                                                             │    │
│     │   Increment version:                                        │    │
│     │   calendar_feed_version:1 = 5 → 6                           │    │
│     │                                                             │    │
│     │   ALL cached entries with v5 are now invalid!               │    │
│     │   Next request will use v6 (cache miss, fresh data)         │    │
│     │                                                             │    │
│     │   ✅ O(1) operation, guaranteed invalidation                │    │
│     └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  3. Server Response                                                     │
│     HTTP 200 OK                                                         │
│     Cache-Control: no-store, max-age=0  ⬅️ NEW                         │
│     HX-Trigger: {"workItemDeleted": {"id": "...", "title": "..."}}     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  4. JavaScript Event Listener (oobc_calendar.html:584)                  │
│     ┌─────────────────────────────────────────────────────────────┐    │
│     │ ✅ Find event by raw UUID (standardized ID format)          │    │
│     │    calendarEvent.remove()                                   │    │
│     │    → Instant UI update, item disappears immediately         │    │
│     └─────────────────────────────────────────────────────────────┘    │
│     ┌─────────────────────────────────────────────────────────────┐    │
│     │ ✅ Trigger background refetch (for sync)                    │    │
│     │    calendar.refetchEvents()                                 │    │
│     └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  5. FullCalendar Refetch (background sync)                              │
│     GET /oobc-management/calendar/work-items/feed/?start=...&end=...    │
│         &_=1728234567890  ⬅️ NEW: Cache-busting timestamp               │
│                                                                         │
│     Headers:                                                            │
│       Cache-Control: no-cache  ⬅️ NEW                                   │
│       Pragma: no-cache         ⬅️ NEW                                   │
│                                                                         │
│     ┌─────────────────────────────────────────────────────────────┐    │
│     │ ✅ Browser bypasses local cache (cache headers respected)   │    │
│     │    Request reaches Django server                            │    │
│     └─────────────────────────────────────────────────────────────┘    │
│                                                                         │
│     ┌─────────────────────────────────────────────────────────────┐    │
│     │ ✅ Django cache miss (version incremented v5 → v6)          │    │
│     │    Query database (fresh data)                              │    │
│     │    Deleted item NOT in results                              │    │
│     │    Cache response with new version (v6)                     │    │
│     └─────────────────────────────────────────────────────────────┘    │
│                                                                         │
│     Response Headers:                                                   │
│       Cache-Control: no-store, max-age=0  ⬅️ NEW (@never_cache)        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  6. RESULT: Deleted item gone forever ✅                                │
│                                                                         │
│     User sees:                                                          │
│     - ✅ Item removed INSTANTLY (optimistic UI update)                  │
│     - ✅ Background refetch confirms deletion (fresh data)              │
│     - ✅ Page refresh shows item still gone (no cache)                  │
│     - ✅ Navigate away and back - item still gone (cache invalidated)   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Cache Key Mismatch Visualization

### Problem: Date Range Mismatch

```
FullCalendar's 6-Week View (What's Actually Requested):
┌──────────────────────────────────────────────────────────────────┐
│  September 2025                 October 2025                     │
│  Su Mo Tu We Th Fr Sa           Su Mo Tu We Th Fr Sa             │
│           1  2  3  4  5  6                1  2  3  4             │
│   7  8  9 10 11 12 13  ──────▶  5  6  7  8  9 10 11             │
│  14 15 16 17 18 19 20           12 13 14 15 16 17 18             │
│  21 22 23 24 25 26 27           19 20 21 22 23 24 25             │
│ [28][29][30]                    26 27 28 29 30 31                │
│                                                                  │
│  ▲────────────────────────────────────────────────────▲          │
│  start: 2025-09-28                   end: 2025-11-08  │          │
│                                                                  │
│  Cache Key Generated:                                            │
│  calendar_feed:1:None:None:2025-09-28:2025-11-08                 │
└──────────────────────────────────────────────────────────────────┘


Cache Invalidation Attempts (What's Being Deleted):
┌──────────────────────────────────────────────────────────────────┐
│  October 2025 (Month boundaries only)                            │
│  Su Mo Tu We Th Fr Sa                                            │
│              1  2  3  4                                          │
│   5  6  7  8  9 10 11                                            │
│  12 13 14 15 16 17 18                                            │
│  19 20 21 22 23 24 25                                            │
│  26 27 28 29 30 31                                               │
│                                                                  │
│  ▲─────────────────────▲                                         │
│  start: 2025-10-01     end: 2025-10-31                           │
│                                                                  │
│  Cache Key Being Deleted:                                        │
│  calendar_feed:1:None:None:2025-10-01:2025-10-31                 │
│                                                                  │
│  ❌ DOES NOT MATCH ACTUAL CACHE KEY!                             │
│  ❌ Cache remains active, deleted item persists                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Version-Based Cache Invalidation (Solution)

```
Traditional Approach (BROKEN):
┌─────────────────────────────────────────────────────────────────┐
│  Must delete EVERY possible cache key:                          │
│                                                                 │
│  calendar_feed:1:None:None:2025-09-28:2025-11-08  ❌ Miss      │
│  calendar_feed:1:None:None:2025-10-01:2025-10-31  ❌ Miss      │
│  calendar_feed:1:project:None:2025-09-28:2025-11-08  ❌ Miss   │
│  calendar_feed:1:None:in_progress:2025-09-28:2025-11-08  ❌    │
│  calendar_feed:1:task:completed:2025-10-01:2025-10-31  ❌      │
│  ... hundreds more possible combinations ...                   │
│                                                                 │
│  Result: Impossible to delete ALL keys (don't know exact dates)│
└─────────────────────────────────────────────────────────────────┘


Version-Based Approach (FIXED):
┌─────────────────────────────────────────────────────────────────┐
│  Single operation invalidates ALL cache entries:                │
│                                                                 │
│  1. Increment version counter:                                  │
│     calendar_feed_version:1 = 5 → 6                             │
│                                                                 │
│  2. All cache keys now use new version:                         │
│     calendar_feed:v6:1:None:None:2025-09-28:2025-11-08          │
│     calendar_feed:v6:1:None:None:2025-10-01:2025-10-31          │
│     calendar_feed:v6:1:project:None:2025-09-28:2025-11-08       │
│     ... all new requests use v6 ...                             │
│                                                                 │
│  3. Old cache entries (v5) are orphaned, never accessed again:  │
│     calendar_feed:v5:1:None:None:2025-09-28:2025-11-08  💀      │
│     calendar_feed:v5:1:project:None:2025-09-28:2025-11-08  💀   │
│                                                                 │
│  Result: ✅ ALL caches invalidated in O(1) time                 │
│  Bonus: ✅ Works with ANY date range, filter combination        │
└─────────────────────────────────────────────────────────────────┘
```

---

## HTTP Cache Headers (Browser-Level Caching)

```
WITHOUT @never_cache (BROKEN):
┌─────────────────────────────────────────────────────────────────┐
│  HTTP Response Headers:                                         │
│                                                                 │
│  HTTP/1.1 200 OK                                                │
│  Content-Type: application/json                                 │
│  Content-Length: 12345                                          │
│  (no cache headers)                                             │
│                                                                 │
│  Browser behavior:                                              │
│  ❌ Caches response in memory/disk                              │
│  ❌ Subsequent requests served from cache (no network request)  │
│  ❌ Even after server cache invalidated, browser serves stale   │
└─────────────────────────────────────────────────────────────────┘


WITH @never_cache (FIXED):
┌─────────────────────────────────────────────────────────────────┐
│  HTTP Response Headers:                                         │
│                                                                 │
│  HTTP/1.1 200 OK                                                │
│  Content-Type: application/json                                 │
│  Cache-Control: max-age=0, no-cache, no-store, must-revalidate │
│  Pragma: no-cache                                               │
│  Expires: 0                                                     │
│  Content-Length: 12345                                          │
│                                                                 │
│  Browser behavior:                                              │
│  ✅ Does NOT cache response                                     │
│  ✅ Every request goes to server (fresh data)                   │
│  ✅ No stale cache issues                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Three-Layer Cache Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 1: Browser Cache                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Fetch Cache (Browser Memory/Disk)                        │  │
│  │ - Caches GET requests by default                         │  │
│  │ - Controlled by HTTP headers (Cache-Control, Pragma)     │  │
│  │ - Fixed by: @never_cache decorator + fetch headers       │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 2: Django Cache                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Server-Side Cache (Redis/LocMem)                         │  │
│  │ - Caches query results for 5 minutes                     │  │
│  │ - Keyed by: user_id + filters + date_range               │  │
│  │ - Fixed by: Version-based invalidation                   │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 3: FullCalendar                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Client-Side Event Cache (JavaScript Memory)              │  │
│  │ - Stores events in memory after fetch                    │  │
│  │ - Updated by: event.remove() or refetchEvents()          │  │
│  │ - Fixed by: Optimistic UI update on deletion             │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE (Source of Truth)                 │
│  PostgreSQL / SQLite - WorkItem table                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Timing Diagram: Delete Operation

```
Time: 0ms
│  User clicks "Delete" button
│
Time: 50ms
│  HTMX sends DELETE request to server
│
Time: 150ms
│  Server processes deletion:
│    - Delete from database (50ms)
│    - Increment cache version (1ms)
│    - Build response (10ms)
│
Time: 200ms
│  Server returns HX-Trigger response
│
Time: 210ms
│  JavaScript receives response
│  Optimistic UI update:
│    - Find event by ID (5ms)
│    - Remove from calendar (5ms)
│    ✅ USER SEES ITEM DISAPPEAR (instant feedback)
│
Time: 220ms
│  JavaScript triggers background refetch
│  Fetch request sent to server
│
Time: 320ms
│  Server processes calendar feed request:
│    - Check cache (version v6, no match) - cache miss (10ms)
│    - Query database (80ms)
│    - Serialize to JSON (20ms)
│    - Cache response with v6 (5ms)
│
Time: 350ms
│  FullCalendar receives fresh data
│  Renders calendar (deleted item NOT in data)
│  ✅ Confirmation: UI stays updated
│
TOTAL TIME: 350ms from click to confirmation
USER EXPERIENCE: Item disappears at 210ms (instant)
```

---

**Diagram Version:** 1.0
**Created:** 2025-10-06
**Purpose:** Visualize calendar cache flow and mismatch issues
