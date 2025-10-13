# RBAC HTMX Quick Fix Guide

**🚨 Critical Issues - Fix Immediately**

## Issue #1: Full Page Reload (BLOCKING)

**File:** `src/templates/common/user_approvals.html` lines 84-88

**❌ Current (WRONG):**
```html
<div hx-trigger="refresh-page from:body"
     hx-get="{% url 'common:user_approvals' %}"
     hx-target="body"
     hx-swap="innerHTML">
```

**✅ Fixed:**
```html
<!-- Remove the hx-trigger wrapper entirely -->
<div id="pending-users-section" class="bg-white rounded-xl...">
```

---

## Issue #2: No Metrics Updates (BLOCKING)

**Problem:** Metrics don't update when users are approved/roles assigned

**Backend Fix:** `src/common/views.py` - `user_approval_action`

```python
from django.template.loader import render_to_string
import json

@login_required
@require_POST
def user_approval_action(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    action = request.POST.get('action')

    if action == 'approve':
        user.is_active = True
        user.approved_by = request.user
        user.approved_at = timezone.now()
        user.save()

        # ✅ Get updated counts
        pending_count = User.objects.filter(is_active=False).count()

        # ✅ Render metrics fragment
        metrics_html = render_to_string(
            'common/partials/approval_metrics.html',
            {'pending_count': pending_count}
        )

        # ✅ Return with OOB swap
        response = HttpResponse(f'''
            <div id="approval-metrics" hx-swap-oob="innerHTML">
                {metrics_html}
            </div>
        ''')

        response['HX-Trigger'] = json.dumps({
            'showMessage': {
                'type': 'success',
                'message': f'Approved {user.get_full_name()}'
            }
        })

        return response
```

**Frontend Fix:** Wrap metrics

```html
<!-- user_approvals.html -->
<div id="approval-metrics">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
        <div class="bg-white rounded-xl...">
            <!-- Pending count stat card -->
            <p class="mt-2 text-3xl font-bold">{{ pending_count }}</p>
        </div>
        <!-- ... other metrics -->
    </div>
</div>
```

---

## Issue #3: Modal Opens Before Content Loads

**File:** `src/templates/common/rbac/dashboard.html` line 254

**❌ Current (WRONG):**
```html
<button onclick="openRbacModal()"
        hx-get="{% url 'common:rbac_user_permissions' user.id %}">
```

**✅ Fixed:**
```html
<button hx-get="{% url 'common:rbac_user_permissions' user.id %}"
        hx-target="#rbac-modal-content"
        hx-swap="innerHTML show:#rbac-modal:top"
        hx-on::before-request="openRbacModal()">
```

**Add loading state in modal:**
```html
<div id="rbac-modal-content">
    <div class="htmx-indicator p-12 text-center">
        <i class="fas fa-spinner fa-spin text-4xl mb-4"></i>
        <p>Loading...</p>
    </div>
</div>
```

---

## Issue #4: Tab System Loads Hidden Content

**File:** `src/templates/common/user_approvals.html` line 260

**❌ Current (WRONG):**
```html
<div hx-trigger="load once">
```

**✅ Fixed:**
```html
<div hx-trigger="revealed once">
```

**Update JavaScript:**
```javascript
function showTab(tabName) {
    // ... existing code ...

    if (contentElement) {
        contentElement.classList.remove('hidden');
        htmx.trigger(contentElement, 'revealed'); // ✅ Add this
    }
}
```

---

## Issue #5: Missing Error Handling

**Add to all templates with HTMX:**

```html
<!-- Global error toast -->
<div id="htmx-error-toast" class="hidden fixed top-4 right-4 z-50">
    <div class="bg-red-100 border-l-4 border-red-500 p-4 rounded-lg">
        <i class="fas fa-exclamation-triangle mr-2"></i>
        <span id="htmx-error-message"></span>
    </div>
</div>

<script>
document.body.addEventListener('htmx:responseError', function(evt) {
    const toast = document.getElementById('htmx-error-toast');
    const msg = document.getElementById('htmx-error-message');

    msg.textContent = evt.detail.xhr.responseText || 'An error occurred';
    toast.classList.remove('hidden');

    setTimeout(() => toast.classList.add('hidden'), 5000);
});
</script>
```

---

## Issue #6: Missing Disabled States

**Add to ALL interactive elements:**

```html
<!-- Search -->
<input hx-get="..."
       hx-disabled-elt="this"
       hx-indicator=".spinner">

<!-- Buttons -->
<button hx-post="..."
        hx-disabled-elt="this"
        hx-indicator="#loading">

<!-- Selects -->
<select hx-get="..."
        hx-disabled-elt="this"
        hx-indicator=".filter-spinner">
```

---

## Checklist - Fix Priority

### 🔴 CRITICAL (Fix Today)
- [ ] Remove full page reload (`user_approvals.html` line 84-88)
- [ ] Add OOB swaps for metrics updates (backend + frontend)
- [ ] Fix modal lifecycle (open after content loads)

### 🟡 HIGH (Fix This Week)
- [ ] Change `hx-trigger="load once"` to `revealed once`
- [ ] Add global error handler
- [ ] Add `hx-disabled-elt` to all interactive elements

### 🟢 MEDIUM (Fix Next Sprint)
- [ ] Preserve checkbox state after swaps
- [ ] Add ARIA live regions
- [ ] Implement focus management

---

## Testing Commands

```bash
# After fixes, test:
cd src

# 1. Test user approval flow
python manage.py runserver
# Navigate to /user-approvals/
# Click approve - should NOT reload page
# Metrics should update instantly

# 2. Test RBAC modal
# Navigate to /user-approvals/ → Permissions & Roles tab
# Click "Permissions" on any user
# Modal should show loading spinner first
# Content should appear without flicker

# 3. Test tab lazy loading
# Navigate to /user-approvals/
# Switch to "Permissions & Roles" tab
# Check Network tab - should load ONLY when tab clicked

# 4. Test error handling
# Temporarily break backend endpoint
# Should show error toast, not blank screen
```

---

## Before/After Behavior

### ❌ BEFORE (Current)
1. User clicks "Approve" → **Full page reloads** → Metrics unchanged
2. User clicks "Permissions" → **Empty modal flashes** → Content loads
3. Page loads → **All tabs load immediately** → Wasted bandwidth
4. HTMX fails → **Blank screen** → No feedback

### ✅ AFTER (Fixed)
1. User clicks "Approve" → **Row disappears smoothly** → Metrics update instantly
2. User clicks "Permissions" → **Spinner shows** → Content swaps in
3. Page loads → **Only visible tab loads** → Efficient loading
4. HTMX fails → **Error toast shows** → Clear feedback

---

## Files to Update

### Templates
1. `src/templates/common/user_approvals.html`
2. `src/templates/common/rbac/dashboard.html`
3. `src/templates/common/rbac/partials/user_permissions_modal.html`
4. `src/templates/common/rbac/partials/role_assignment_form.html`
5. `src/templates/common/rbac/partials/bulk_assign_modal.html`

### Views
6. `src/common/views.py` - `user_approval_action`
7. `src/common/views/rbac_management.py` - Multiple endpoints

### New Files Needed
8. `src/templates/common/partials/approval_metrics.html` (OOB fragment)
9. `src/templates/components/error_toast.html` (Error handler)

---

**Read full analysis:** `docs/improvements/RBAC_FRONTEND_HTMX_REVIEW.md`
