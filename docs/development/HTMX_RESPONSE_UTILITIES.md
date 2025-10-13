# HTMX Response Utilities

**Status:** ✅ Implemented
**File:** `src/common/utils/htmx_responses.py`
**Purpose:** Standardized HTMX error and success response handling

## Overview

This module provides consistent response patterns for HTMX endpoints across OBCMS, ensuring:
- Uniform error handling with toast notifications
- Minimal response payloads (HTMX handles UI updates)
- Consistent HX-Trigger header formatting
- Better user experience with instant feedback

## Problem Solved

**Before:** Inconsistent 403 handling across HTMX endpoints
- Some returned JSON responses
- Some returned plain text
- Some didn't use HX-Trigger headers
- Inconsistent toast notification triggering

**After:** Standardized response utilities
- All HTMX errors use consistent format
- Automatic toast notification triggering
- Clean, reusable helper functions
- Type hints and comprehensive documentation

## Core Functions

### 1. `htmx_403_response()`

**Purpose:** Handle permission denied errors in HTMX endpoints

**Signature:**
```python
def htmx_403_response(
    message: Optional[str] = None,
    trigger_toast: bool = True
) -> HttpResponse
```

**Features:**
- Returns HTTP 403 status
- Adds HX-Trigger header for error toast
- Returns minimal HTML content (empty string)
- Works with existing `error_toast.html` component

**Default Message:**
```
"You do not have permission to perform this action."
```

**Usage Examples:**

```python
from common.utils.htmx_responses import htmx_403_response

# Basic usage with default message
if not has_permission(request.user):
    return htmx_403_response()

# With custom message
if not can_approve_users(request.user):
    return htmx_403_response(
        message="Only coordinators can approve user registrations."
    )

# Without toast notification (silent)
if not is_owner(request.user, obj):
    return htmx_403_response(
        message="Access denied",
        trigger_toast=False
    )
```

### 2. `htmx_error_response()`

**Purpose:** Generic error response for various HTTP status codes

**Signature:**
```python
def htmx_error_response(
    message: str,
    status: int = 400,
    trigger_toast: bool = True
) -> HttpResponse
```

**Usage Examples:**

```python
from common.utils.htmx_responses import htmx_error_response

# 400 Bad Request
if not form.is_valid():
    return htmx_error_response(
        message="Invalid form data. Please check your inputs.",
        status=400
    )

# 404 Not Found
if not obj:
    return htmx_error_response(
        message="Resource not found.",
        status=404
    )

# 500 Server Error
return htmx_error_response(
    message="An unexpected error occurred. Please try again.",
    status=500
)
```

### 3. `htmx_success_response()`

**Purpose:** Standardized success response with toast and additional triggers

**Signature:**
```python
def htmx_success_response(
    message: str,
    additional_triggers: Optional[dict] = None
) -> HttpResponse
```

**Usage Examples:**

```python
from common.utils.htmx_responses import htmx_success_response

# Basic success
return htmx_success_response(
    message="User approved successfully"
)

# With additional triggers for UI updates
return htmx_success_response(
    message="User endorsed to OOBC",
    additional_triggers={
        "user-endorsed": {"id": user_id},
        "refresh-list": True
    }
)
```

## Implementation Examples

### Approval Views Implementation

**File:** `src/common/views/approval.py`

#### Example 1: Stage One Approval Permission Check

**Before:**
```python
@login_required
def approve_moa_user_stage_one(request, user_id):
    if not is_moa_focal_approver(request.user):
        return HttpResponse(
            status=403,
            content="You do not have permission to endorse users for OOBC approval.",
        )
```

**After:**
```python
from ..utils.htmx_responses import htmx_403_response

@login_required
def approve_moa_user_stage_one(request, user_id):
    if not is_moa_focal_approver(request.user):
        return htmx_403_response(
            message="You do not have permission to endorse users for OOBC approval."
        )
```

**Benefits:**
- Automatic HX-Trigger header
- Toast notification triggered
- Cleaner, more readable code
- Consistent error format

#### Example 2: Organization-Level Permission Check

**Before:**
```python
if (
    not request.user.moa_organization
    or request.user.moa_organization_id != user_to_endorse.moa_organization_id
):
    return HttpResponse(
        status=403,
        content="You can only endorse users from your assigned organization.",
    )
```

**After:**
```python
if (
    not request.user.moa_organization
    or request.user.moa_organization_id != user_to_endorse.moa_organization_id
):
    return htmx_403_response(
        message="You can only endorse users from your assigned organization."
    )
```

#### Example 3: Final Approval Permission Check

**Before:**
```python
@login_required
def approve_moa_user(request, user_id):
    if not can_approve_moa_users(request.user):
        return HttpResponse(
            status=403,
            content="You do not have permission to approve users."
        )
```

**After:**
```python
@login_required
def approve_moa_user(request, user_id):
    if not can_approve_moa_users(request.user):
        return htmx_403_response(
            message="You do not have permission to approve users."
        )
```

#### Example 4: Rejection Permission Check

**Before:**
```python
@login_required
def reject_moa_user(request, user_id):
    is_final_approver = can_approve_moa_users(request.user)
    is_focal_approver = is_moa_focal_approver(request.user)
    if not (is_final_approver or is_focal_approver):
        return HttpResponse(
            status=403,
            content="You do not have permission to reject users."
        )
```

**After:**
```python
@login_required
def reject_moa_user(request, user_id):
    is_final_approver = can_approve_moa_users(request.user)
    is_focal_approver = is_moa_focal_approver(request.user)
    if not (is_final_approver or is_focal_approver):
        return htmx_403_response(
            message="You do not have permission to reject users."
        )
```

#### Example 5: Organization-Level Rejection Check

**Before:**
```python
if (
    is_focal_approver
    and not is_final_approver
    and (
        not request.user.moa_organization
        or request.user.moa_organization_id != user_to_reject.moa_organization_id
    )
):
    return HttpResponse(
        status=403,
        content="You can only reject registrations from your organization.",
    )
```

**After:**
```python
if (
    is_focal_approver
    and not is_final_approver
    and (
        not request.user.moa_organization
        or request.user.moa_organization_id != user_to_reject.moa_organization_id
    )
):
    return htmx_403_response(
        message="You can only reject registrations from your organization."
    )
```

## Integration with Existing Components

### Toast System Integration

The helper functions integrate seamlessly with the existing toast system:

**Component:** `src/templates/components/error_toast.html`
**Handler:** `src/templates/base.html` (lines 807-821)

**Event Flow:**
1. Helper function returns 403 with `HX-Trigger: {"show-toast": "message"}`
2. HTMX processes the response and triggers the `show-toast` event
3. Global event listener in `base.html` catches the event
4. Toast notification displays to user with error styling

**Event Listener (base.html):**
```javascript
document.body.addEventListener('show-toast', function (event) {
    const payload = event?.detail ?? event?.value;
    showToast(payload);
    // ... event handling
}, true);
```

## Import Patterns

### Single Function Import
```python
from common.utils.htmx_responses import htmx_403_response

# Use in view
return htmx_403_response(message="Permission denied")
```

### Multiple Function Import
```python
from common.utils.htmx_responses import (
    htmx_403_response,
    htmx_error_response,
    htmx_success_response,
)

# Use based on context
if not has_permission:
    return htmx_403_response(message="No permission")
if not obj:
    return htmx_error_response(message="Not found", status=404)
# ... success case
return htmx_success_response(message="Action completed")
```

### Module Import
```python
from common.utils import htmx_responses

# Use with module prefix
return htmx_responses.htmx_403_response(message="Access denied")
```

## File Locations

### Utility Module
**Path:** `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/common/utils/htmx_responses.py`

**Structure:**
```
src/common/utils/
├── __init__.py
├── deprecation.py
├── htmx_responses.py  # ← New utility module
├── moa_permissions.py
└── permissions.py
```

### Updated Views
**Path:** `/Users/saidamenmambayao/Library/Mobile Documents/com~apple~CloudDocs/BTA/OOBC/obcms/src/common/views/approval.py`

**Changes:**
- Added import: `from ..utils.htmx_responses import htmx_403_response`
- Replaced 6 instances of `HttpResponse(status=403, ...)` with `htmx_403_response(...)`

## Response Format Details

### 403 Response Structure

**HTTP Response:**
```http
HTTP/1.1 403 Forbidden
HX-Trigger: {"show-toast": "You do not have permission to perform this action."}
Content-Length: 0

```

**Key Features:**
- Status: 403 (Forbidden)
- Header: HX-Trigger with JSON-encoded toast event
- Body: Empty string (minimal payload)

### Success Response Structure

**HTTP Response:**
```http
HTTP/1.1 200 OK
HX-Trigger: {"show-toast": "Action completed", "refresh-list": true}
Content-Length: 0

```

## Testing the Implementation

### Manual Test Steps

1. **Test 403 Response:**
   ```bash
   # As non-approver user, attempt to approve
   curl -X POST \
     -H "HX-Request: true" \
     -H "Cookie: sessionid=..." \
     http://localhost:8000/common/approve-moa-user/123/
   ```

   **Expected:**
   - Status: 403
   - HX-Trigger header present
   - Toast message displays in UI

2. **Test Custom Message:**
   ```python
   # In Django shell
   from common.utils.htmx_responses import htmx_403_response

   response = htmx_403_response(
       message="Custom error message"
   )

   print(response.status_code)  # 403
   print(response.headers)       # Has HX-Trigger
   ```

3. **Test Without Toast:**
   ```python
   response = htmx_403_response(
       message="Silent error",
       trigger_toast=False
   )

   # HX-Trigger header should not be present
   assert 'HX-Trigger' not in response.headers
   ```

## Future Enhancements

### Potential Additions

1. **HTMX Redirect Response:**
   ```python
   def htmx_redirect_response(
       url: str,
       message: Optional[str] = None
   ) -> HttpResponse
   ```

2. **HTMX Refresh Response:**
   ```python
   def htmx_refresh_response(
       target: str,
       message: Optional[str] = None
   ) -> HttpResponse
   ```

3. **HTMX Validation Error Response:**
   ```python
   def htmx_validation_error_response(
       errors: dict,
       form_selector: str
   ) -> HttpResponse
   ```

### Migration Checklist

To migrate other views to use these utilities:

- [ ] Search for `HttpResponse(status=403`
- [ ] Replace with `htmx_403_response(message=...)`
- [ ] Search for `HttpResponse(status=400`
- [ ] Replace with `htmx_error_response(message=..., status=400)`
- [ ] Search for `JsonResponse({"error": ...}, status=403)`
- [ ] Replace with `htmx_403_response(message=...)`
- [ ] Add import: `from common.utils.htmx_responses import ...`

## Benefits Summary

### Code Quality
- **Consistency:** All HTMX errors follow same pattern
- **Maintainability:** Single source of truth for error responses
- **Readability:** Clear, self-documenting function names
- **Type Safety:** Type hints for better IDE support

### User Experience
- **Instant Feedback:** Toast notifications appear immediately
- **Clear Messages:** Standardized error message formatting
- **Accessibility:** Works with existing WCAG-compliant toast system
- **Mobile-Friendly:** Toast positioning optimized for all devices

### Developer Experience
- **Easy to Use:** Simple import and one-line usage
- **Well Documented:** Comprehensive docstrings and examples
- **Discoverable:** Clear naming convention
- **Extensible:** Easy to add new response types

## Related Documentation

- [Instant UI Improvements Plan](../improvements/instant_ui_improvements_plan.md)
- [OBCMS UI Standards](../ui/OBCMS_UI_STANDARDS_MASTER.md)
- [Toast Component](../../src/templates/components/error_toast.html)
- [Base Template](../../src/templates/base.html)

---

**Last Updated:** 2025-10-13
**Author:** Claude Code
**Status:** Production Ready
