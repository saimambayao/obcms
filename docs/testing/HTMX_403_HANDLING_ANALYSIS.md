# HTMX 403 Handling Analysis Report

**Date:** 2025-10-13
**System:** OBCMS (Office for Other Bangsamoro Communities Management System)
**Focus:** HTMX-based endpoints and 403 Forbidden error handling

---

## Executive Summary

This analysis examines all HTMX-powered endpoints in OBCMS to verify proper 403 (Forbidden) error handling. The system has **78 template files** containing HTMX directives, with critical endpoints in:

1. **User Approvals** (OOBC Staff & MOA Staff)
2. **RBAC Management** (Role & Permission Assignment)
3. **Staff Management** (Profile & Task Management)
4. **Work Items** (Project Management)

### Key Findings

✅ **STRENGTHS:**
- Global error handling via `htmx:responseError` event listener in `base.html` and `error_toast.html`
- RBAC management views return proper HTTP 403 with helpful error messages
- MOA approval views include permission checks with 403 responses
- Toast notification system for user feedback on errors

⚠️ **GAPS IDENTIFIED:**
- Some 403 responses lack `HX-Trigger` headers with structured error messages
- Inconsistent error message formats (some use plain text, others use JSON)
- Missing client-side 403-specific handling (generic error handler catches all errors)
- No automated refresh or retry mechanisms after permission restoration

---

## HTMX Endpoint Inventory

### 1. User Approvals System

#### **Endpoint:** User Approval Action
- **URL:** `/oobc-management/user-approvals/<int:user_id>/action/`
- **View:** `common.views.management.user_approval_action`
- **HTMX Pattern:** `hx-post` with `hx-swap="delete"`
- **Permission Check:** `_can_approve_users(request.user)`

**403 Handling Status:** ⚠️ **PARTIAL**

```python
# Current Implementation (Line 3772-3773)
if not _can_approve_users(request.user):
    return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)
```

**Issues:**
- Returns JSON response but HTMX expects HTML or triggers
- No `HX-Trigger` header for toast notification
- Client receives generic error handler response

**Recommendation:**
```python
if not _can_approve_users(request.user):
    response = HttpResponse(
        '<div class="alert alert-error">You do not have permission to approve users.</div>',
        status=403
    )
    response['HX-Trigger'] = json.dumps({
        'showMessage': {
            'type': 'error',
            'message': 'You do not have permission to approve users.'
        }
    })
    return response
```

#### **Template Location:** `templates/common/user_approvals.html`
- Lines 363-387: Approve/Reject buttons with HTMX
- `hx-post="{% url 'common:user_approval_action' user.id %}"`
- `hx-target="#user-row-{{ user.id }}"`
- `hx-swap="delete swap:300ms"`

---

### 2. MOA Staff Approval System

#### **Endpoint:** MOA Approval List (Stage 1 - Focal)
- **URL:** `/oobc-management/moa-approvals/<int:user_id>/endorse/`
- **View:** `common.views.approval.approve_moa_user_stage_one`
- **Permission Check:** `is_moa_focal_approver(request.user)`

**403 Handling Status:** ✅ **GOOD**

```python
# Current Implementation (Lines 189-193)
if not is_moa_focal_approver(request.user):
    return HttpResponse(
        status=403,
        content="You do not have permission to endorse users for OOBC approval.",
    )
```

**Issues:**
- Plain text response (not HTML)
- No `HX-Trigger` header for user feedback

**Enhancement Needed:**
```python
if not is_moa_focal_approver(request.user):
    response = HttpResponse(
        '<div class="alert alert-error">You do not have permission to endorse users.</div>',
        status=403
    )
    response['HX-Trigger'] = json.dumps({
        'showMessage': {
            'type': 'error',
            'message': 'You do not have permission to endorse users for OOBC approval.'
        }
    })
    return response
```

#### **Endpoint:** MOA Approval (Stage 2 - Final)
- **URL:** `/oobc-management/moa-approvals/<int:user_id>/approve/`
- **View:** `common.views.approval.approve_moa_user`
- **Permission Check:** `can_approve_moa_users(request.user)`

**403 Handling Status:** ✅ **GOOD**

```python
# Current Implementation (Lines 291-295)
if not can_approve_moa_users(request.user):
    return HttpResponse(
        status=403,
        content="You do not have permission to approve users."
    )
```

**Same Issues & Recommendations as Stage 1**

#### **Endpoint:** MOA Rejection
- **URL:** `/oobc-management/moa-approvals/<int:user_id>/reject/`
- **View:** `common.views.approval.reject_moa_user`
- **Permission Check:** `can_approve_moa_users(request.user)` OR `is_moa_focal_approver(request.user)`

**403 Handling Status:** ✅ **GOOD**

```python
# Current Implementation (Lines 401-404)
if not (is_final_approver or is_focal_approver):
    return HttpResponse(
        status=403,
        content="You do not have permission to reject users."
    )
```

**Same Issues & Recommendations**

#### **Template Location:** `templates/common/approval/moa_approval_list_partial.html`
- HTMX lazy loading: `hx-get="{% url 'common:moa_approval_list' %}"`
- `hx-trigger="revealed once"`

---

### 3. RBAC Management System

#### **Endpoint:** RBAC Dashboard
- **URL:** `/rbac/`
- **View:** `common.views.rbac_management.rbac_dashboard`
- **Permission Check:** `@require_permission('oobc_management.manage_user_permissions')`

**403 Handling Status:** ✅ **EXCELLENT**

The `@require_permission` decorator handles 403 responses properly:
- Returns structured error response
- Includes `HX-Trigger` header with error message
- Logs unauthorized access attempts

#### **Endpoint:** User Permissions List (HTMX)
- **URL:** `/rbac/users/list/`
- **View:** `common.views.rbac_management.rbac_users_list`
- **Permission Check:** `@require_permission('oobc_management.manage_user_permissions')`

**403 Handling Status:** ✅ **EXCELLENT**

#### **Endpoint:** User Permissions Detail (Modal)
- **URL:** `/rbac/user/<int:user_id>/permissions/`
- **View:** `common.views.rbac_management.user_permissions_detail`
- **Permission Check:** `@require_permission('oobc_management.manage_user_permissions')`

**403 Handling Status:** ✅ **EXCELLENT**

#### **Endpoint:** Role Assignment (HTMX POST)
- **URL:** `/rbac/user/<int:user_id>/roles/assign/`
- **View:** `common.views.rbac_management.user_role_assign`
- **Permission Check:** `@require_permission('oobc_management.assign_user_roles')`

**403 Handling Status:** ✅ **EXCELLENT**

**Template Locations:**
- `templates/common/rbac/dashboard.html` (Lines 92-97, 113-118, 142-147)
- `templates/common/rbac/partials/users_grid.html`
- `templates/common/rbac/partials/user_permissions_modal.html`

**HTMX Patterns Found:**
- Search with auto-trigger: `hx-get="{% url 'common:rbac_users_list' %}" hx-trigger="keyup changed delay:500ms"`
- Filter with change trigger: `hx-get="{% url 'common:rbac_users_list' %}" hx-trigger="change"`
- Modal loading: `hx-get="{% url 'common:rbac_user_permissions' user.id %}" hx-target="#rbac-modal-content"`

---

### 4. Work Items Management

**Endpoints:** Multiple work item HTMX endpoints detected in 43 templates

**Template Locations:**
- `templates/work_items/partials/sidebar_*.html`
- `templates/work_items/partials/tree_*.html`
- `templates/work_items/_work_item_*.html`

**403 Handling Status:** ⚠️ **NEEDS REVIEW**

Work item views not reviewed in this analysis. Recommend separate audit for work item permission checks.

---

## Global Error Handling Infrastructure

### 1. Error Toast Component
**File:** `templates/components/error_toast.html`

**Features:**
- Global `htmx:responseError` listener (Line 53)
- Parses JSON error messages
- Displays user-friendly toast notifications
- Auto-dismisses after 5 seconds

```javascript
document.body.addEventListener('htmx:responseError', function(evt) {
    const errorToast = document.getElementById('htmx-error-toast');
    const errorMessage = document.getElementById('htmx-error-message');

    let message = 'An error occurred. Please try again.';

    try {
        const response = evt.detail.xhr.responseText;
        if (response) {
            const data = JSON.parse(response);
            message = data.error || data.message || message;
        }
    } catch (e) {
        message = evt.detail.xhr.responseText || message;
    }

    errorMessage.textContent = message;
    errorToast.classList.remove('hidden');

    setTimeout(() => {
        errorToast.classList.add('hidden');
    }, 5000);
});
```

**Issues:**
- Generic error message for all HTTP errors (doesn't distinguish 403 from 500)
- No specific handling for permission-related errors
- No visual distinction between error types

### 2. Base Template Error Handler
**File:** `templates/base.html` (Line 824)

```javascript
document.body.addEventListener('htmx:responseError', function(event) {
    console.error('HTMX Error:', event.detail);
    showToast({
        message: 'An error occurred. Please try again or contact support.',
        level: 'error'
    });
});
```

**Also handles:**
- `htmx:sendError` - Network errors
- `htmx:timeout` - Request timeouts

**Issues:**
- Generic error message doesn't indicate permission issue
- No specific action for 403 errors (e.g., redirect to login or show permission request form)

---

## Permission Check Patterns Analysis

### Pattern 1: Manual Check with 403 Response
```python
if not has_permission(user):
    return HttpResponse(status=403, content="Error message")
```

**Used in:**
- `approve_moa_user_stage_one`
- `approve_moa_user`
- `reject_moa_user`
- `user_approval_action`

**Issues:**
- Plain text responses (not HTML-friendly)
- No structured error format
- Missing `HX-Trigger` headers

### Pattern 2: Decorator-based Permission Check
```python
@require_permission('permission.codename')
def view_function(request):
    # View logic
```

**Used in:**
- All RBAC management views
- Most staff management views

**Strengths:**
- Consistent 403 handling
- Centralized error response logic
- Proper `HX-Trigger` headers

### Pattern 3: Manual Check with JsonResponse
```python
if not has_permission(user):
    return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)
```

**Used in:**
- `user_approval_action`

**Issues:**
- HTMX expects HTML or triggers, not JSON
- Client-side HTMX doesn't process JSON error responses properly

---

## Client-Side 403 Handling Analysis

### Current Implementation

**No specific 403 handling detected**. All HTTP errors trigger the same `htmx:responseError` handler.

### Recommended Implementation

Add specific 403 handler before the generic error handler:

```javascript
// Add to base.html or error_toast.html
document.body.addEventListener('htmx:responseError', function(evt) {
    const xhr = evt.detail.xhr;

    // Handle 403 Forbidden specifically
    if (xhr.status === 403) {
        const errorToast = document.getElementById('htmx-error-toast');
        const errorMessage = document.getElementById('htmx-error-message');

        let message = 'You do not have permission to perform this action.';

        // Try to parse structured error
        try {
            const data = JSON.parse(xhr.responseText);
            message = data.error || data.message || message;
        } catch (e) {
            message = xhr.responseText || message;
        }

        errorMessage.innerHTML = `
            <strong>Permission Denied:</strong> ${message}
            <br><small>If you believe this is an error, please contact your administrator.</small>
        `;
        errorToast.classList.remove('hidden');

        // Log for debugging
        console.warn('403 Forbidden:', evt.detail);

        return; // Prevent generic handler
    }

    // Generic error handling...
});
```

---

## HTMX Endpoint Summary Table

| Endpoint | URL Pattern | Permission Check | 403 Response Format | HX-Trigger | Status |
|----------|-------------|------------------|---------------------|------------|--------|
| User Approval Action | `/user-approvals/<id>/action/` | Manual check | JSON | ❌ No | ⚠️ Partial |
| MOA Focal Endorsement | `/moa-approvals/<id>/endorse/` | Manual check | Plain text | ❌ No | ⚠️ Partial |
| MOA Final Approval | `/moa-approvals/<id>/approve/` | Manual check | Plain text | ❌ No | ⚠️ Partial |
| MOA Rejection | `/moa-approvals/<id>/reject/` | Manual check | Plain text | ❌ No | ⚠️ Partial |
| RBAC Dashboard | `/rbac/` | Decorator | Structured HTML | ✅ Yes | ✅ Good |
| RBAC Users List | `/rbac/users/list/` | Decorator | Structured HTML | ✅ Yes | ✅ Good |
| RBAC User Permissions | `/rbac/user/<id>/permissions/` | Decorator | Structured HTML | ✅ Yes | ✅ Good |
| RBAC Role Assign | `/rbac/user/<id>/roles/assign/` | Decorator | Structured HTML | ✅ Yes | ✅ Good |
| RBAC Role Remove | `/rbac/user/<id>/roles/<role_id>/remove/` | Decorator | Structured HTML | ✅ Yes | ✅ Good |
| RBAC Feature Toggle | `/rbac/user/<id>/features/<feature_id>/toggle/` | Decorator | Structured HTML | ✅ Yes | ✅ Good |
| RBAC Permission Grant | `/rbac/user/<id>/permissions/grant/` | Decorator | Structured HTML | ✅ Yes | ✅ Good |
| RBAC Permission Remove | `/rbac/user/<id>/permissions/<perm_id>/remove/` | Decorator | Structured HTML | ✅ Yes | ✅ Good |
| RBAC Bulk Assign | `/rbac/bulk/assign/` | Decorator | Structured HTML | ✅ Yes | ✅ Good |
| RBAC Bulk Remove | `/rbac/bulk/remove/` | Decorator | Structured HTML | ✅ Yes | ✅ Good |

**Legend:**
- ✅ Good: Proper 403 handling with HX-Trigger
- ⚠️ Partial: Permission check exists but response format needs improvement
- ❌ Poor: Missing permission check or improper response

---

## Critical Issues & Recommendations

### Issue 1: Inconsistent 403 Response Formats

**Problem:** Some views return JSON, others plain text, others HTML. HTMX clients expect consistent format.

**Solution:** Standardize all HTMX 403 responses to:
```python
def htmx_403_response(message, request=None):
    """Standard 403 response for HTMX requests."""
    response = HttpResponse(
        f'<div class="alert alert-error" role="alert">{message}</div>',
        status=403
    )
    response['HX-Trigger'] = json.dumps({
        'showMessage': {
            'type': 'error',
            'message': message
        }
    })
    return response
```

**Apply to:**
- `user_approval_action` (Line 3773)
- `approve_moa_user_stage_one` (Lines 189-193)
- `approve_moa_user` (Lines 291-295)
- `reject_moa_user` (Lines 401-404)

### Issue 2: Missing Client-Side 403 Handler

**Problem:** Generic error handler doesn't provide specific guidance for permission errors.

**Solution:** Add 403-specific handler to `error_toast.html`:
```javascript
document.body.addEventListener('htmx:responseError', function(evt) {
    const xhr = evt.detail.xhr;

    if (xhr.status === 403) {
        showPermissionError(xhr);
        return;
    }

    // Generic error handling...
});

function showPermissionError(xhr) {
    const errorToast = document.getElementById('htmx-error-toast');
    const errorMessage = document.getElementById('htmx-error-message');

    let message = 'You do not have permission to perform this action.';

    try {
        const data = JSON.parse(xhr.responseText);
        message = data.error || data.message || message;
    } catch (e) {
        // HTML or plain text response
        const div = document.createElement('div');
        div.innerHTML = xhr.responseText;
        message = div.textContent || message;
    }

    errorMessage.innerHTML = `
        <div class="font-semibold">Permission Denied</div>
        <div class="mt-1">${message}</div>
        <div class="mt-2 text-xs opacity-75">
            Contact your administrator if you believe this is an error.
        </div>
    `;

    errorToast.classList.remove('hidden');

    // Auto-hide after 8 seconds (longer for permission errors)
    setTimeout(() => {
        errorToast.classList.add('hidden');
    }, 8000);
}
```

### Issue 3: No Permission Check Bypass Mechanism

**Problem:** HTMX views that bypass permission checks (e.g., decorators commented out) are security vulnerabilities.

**Solution:** Implement automated permission check verification:
```python
# Add to settings/base.py
HTMX_ENFORCE_PERMISSIONS = True

# Add to middleware
class HTMXPermissionEnforcementMiddleware:
    """Ensure all HTMX endpoints have permission checks."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.headers.get('HX-Request'):
            # Log HTMX requests without @require_permission decorator
            view_func = request.resolver_match.func
            if not hasattr(view_func, '_permission_required'):
                logger.warning(
                    f"HTMX endpoint without permission check: {request.path}"
                )

        return self.get_response(request)
```

### Issue 4: Work Items Permission Audit Needed

**Problem:** 43 work item templates contain HTMX but views not audited.

**Solution:** Conduct separate audit of:
- `work_items/views.py`
- All work item HTMX endpoints
- Verify permission checks on create, update, delete operations

---

## Testing Recommendations

### 1. Manual Testing Checklist

For each HTMX endpoint:

```
□ Test as unauthorized user (no permissions)
  - Verify 403 response returned
  - Verify toast notification displays
  - Verify error message is user-friendly

□ Test as partially authorized user (some permissions)
  - Verify correct permission is checked
  - Verify 403 for missing specific permission

□ Test as fully authorized user
  - Verify operation succeeds
  - Verify success feedback displayed

□ Test network error handling
  - Disconnect network
  - Verify timeout handling
  - Verify retry mechanism (if any)
```

### 2. Automated Test Template

```python
from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

class HTMXPermissionTest:
    """Base class for HTMX 403 testing."""

    def test_htmx_403_response(self):
        """Verify HTMX endpoint returns proper 403."""
        client = Client()

        # Create user without permission
        user = User.objects.create_user(
            username='testuser',
            password='password123'
        )
        client.force_login(user)

        # Make HTMX request
        response = client.post(
            self.endpoint_url,
            HTTP_HX_REQUEST='true'
        )

        # Assertions
        self.assertEqual(response.status_code, 403)
        self.assertIn('HX-Trigger', response.headers)

        # Verify error message structure
        trigger_data = json.loads(response.headers['HX-Trigger'])
        self.assertIn('showMessage', trigger_data)
        self.assertEqual(trigger_data['showMessage']['type'], 'error')
        self.assertIsNotNone(trigger_data['showMessage']['message'])
```

### 3. Security Test Scenarios

```python
def test_permission_bypass_attempts():
    """Test that permission checks cannot be bypassed."""

    scenarios = [
        # Try to bypass permission check with header manipulation
        {'HX-Request': 'false', 'expected': 403},

        # Try to bypass with CSRF token manipulation
        {'csrfmiddlewaretoken': 'invalid', 'expected': 403},

        # Try to access endpoint directly (not via HTMX)
        {'direct_access': True, 'expected': 302},  # Should redirect
    ]

    for scenario in scenarios:
        response = client.post(endpoint_url, **scenario)
        assert response.status_code == scenario['expected']
```

---

## Implementation Priority

### Phase 1: Critical Fixes (HIGH PRIORITY)

1. **Standardize 403 responses in approval views**
   - Update `user_approval_action`
   - Update MOA approval views (3 endpoints)
   - Add `HX-Trigger` headers to all

2. **Add 403-specific client handler**
   - Update `error_toast.html`
   - Add permission-specific error UI

3. **Fix JSON response in `user_approval_action`**
   - Replace JsonResponse with HttpResponse
   - Add proper HX-Trigger header

**Estimated Effort:** 4 hours

### Phase 2: Enhancement (MEDIUM PRIORITY)

1. **Create standardized helper function**
   - Add `htmx_403_response()` to utils
   - Update all views to use helper

2. **Add permission enforcement middleware**
   - Log HTMX endpoints without permission checks
   - Alert on potential security gaps

3. **Work items permission audit**
   - Review all work item views
   - Add missing permission checks

**Estimated Effort:** 8 hours

### Phase 3: Testing (LOW PRIORITY)

1. **Create automated test suite**
   - Test all HTMX endpoints for 403 handling
   - Add security bypass tests

2. **Manual testing protocol**
   - Test with different user roles
   - Verify error messages
   - Test edge cases

**Estimated Effort:** 12 hours

---

## Appendix A: HTMX Templates Reference

Complete list of templates with HTMX directives:

### User Approvals (2 templates)
- `templates/common/user_approvals.html`
- `templates/common/approval/moa_approval_list_partial.html`

### RBAC Management (7 templates)
- `templates/common/rbac/dashboard.html`
- `templates/common/rbac/partials/user_permissions_modal.html`
- `templates/common/rbac/partials/users_grid.html`
- `templates/common/rbac/partials/permission_grant_form.html`
- `templates/common/rbac/partials/bulk_assign_modal.html`
- `templates/common/rbac/partials/feature_toggle_matrix.html`
- `templates/common/rbac/partials/role_assignment_form.html`

### Work Items (43 templates)
- `templates/work_items/work_item_*.html` (12 files)
- `templates/work_items/partials/*.html` (31 files)

### Other Modules (26 templates)
- Budget preparation/execution (7 files)
- Coordination/events (5 files)
- MANA assessments (4 files)
- Communities management (4 files)
- Monitoring (4 files)
- Project Central (2 files)

**Total: 78 templates with HTMX directives**

---

## Appendix B: Decorator Implementation

The `@require_permission` decorator used in RBAC views:

```python
# From common/decorators/rbac.py
def require_permission(permission_string):
    """
    Decorator to require a specific permission for a view.

    For HTMX requests, returns proper 403 with HX-Trigger header.
    For normal requests, redirects to permission denied page.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())

            if not RBACService.has_permission(request.user, permission_string):
                # Log unauthorized attempt
                log_unauthorized_access(
                    request,
                    permission_string,
                    f"User {request.user.username} attempted to access {request.path}"
                )

                # HTMX response
                if request.headers.get('HX-Request'):
                    response = HttpResponse(
                        '<div class="alert alert-error">Permission denied: You do not have access to this resource.</div>',
                        status=403
                    )
                    response['HX-Trigger'] = json.dumps({
                        'showMessage': {
                            'type': 'error',
                            'message': f'Permission denied: {permission_string}'
                        }
                    })
                    return response

                # Normal response
                return render(request, 'errors/403.html', status=403)

            return view_func(request, *args, **kwargs)

        # Mark function as having permission check
        wrapper._permission_required = permission_string
        return wrapper
    return decorator
```

**This decorator should be the standard for all HTMX endpoints.**

---

## Conclusion

The OBCMS system has a **solid foundation** for HTMX 403 error handling through the RBAC management views and global error handlers. However, **critical gaps exist** in the approval workflow views that need immediate attention.

### Summary of Findings

✅ **Strengths:**
- RBAC views use proper decorator pattern
- Global error toast infrastructure exists
- Permission checks are in place (not bypassed)

⚠️ **Critical Issues:**
- Inconsistent 403 response formats (JSON, plain text, HTML)
- Missing `HX-Trigger` headers in approval views
- No 403-specific client-side handling
- Generic error messages don't indicate permission issues

🔧 **Required Actions:**
1. Standardize all 403 responses to use `HX-Trigger` headers
2. Add 403-specific error handler to error_toast.html
3. Update approval views to return proper HTMX responses
4. Conduct work items permission audit

**Completion of Phase 1 fixes will bring the system to production-ready state for HTMX 403 handling.**
