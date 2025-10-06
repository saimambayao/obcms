# Quick Debug Steps: Modal Delete Button Not Working

## TL;DR - The Fix

**Add one line to `src/templates/common/oobc_calendar.html` at line 369:**

```javascript
.then(function(html) {
    modalContent.innerHTML = html;

    // ✅ ADD THIS LINE:
    if (window.htmx) { htmx.process(modalContent); }

    attachModalHandlers();
})
```

**Why:** HTMX doesn't automatically scan dynamically loaded content. The `hx-delete` attribute on the button is never activated.

---

## Debug in Browser DevTools (5 Minutes)

### Open Console and Run These Commands:

#### 1. Check HTMX Loaded
```javascript
console.log('HTMX:', !!window.htmx, window.htmx?.version);
// Expected: HTMX: true "1.9.12"
```

#### 2. Open Modal, Then Check Button
```javascript
var btn = document.querySelector('[hx-delete]');
console.log('Button found:', !!btn);
console.log('Button HTML:', btn?.outerHTML);
// Expected: Button found: false ❌ (This is the problem!)
```

#### 3. After Adding htmx.process(), Verify
```javascript
var btn = document.querySelector('[hx-delete]');
console.log('Button found:', !!btn);
// Expected: Button found: true ✅
```

#### 4. Test Delete Request Manually
```javascript
// Replace UUID with actual work item ID
fetch('/work-items/YOUR-UUID-HERE/delete/', {
    method: 'DELETE',
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
})
.then(r => {
    console.log('Status:', r.status);
    console.log('HX-Trigger:', r.headers.get('HX-Trigger'));
});
// Expected: Status: 200, HX-Trigger: {"workItemDeleted":{...}}
```

---

## Event Listeners Affecting Modal

### 1. Modal Backdrop (Line 428-432) ✅ NOT BLOCKING
```javascript
modal.addEventListener('click', function(e) {
    if (e.target === modal) { closeModal(); }  // Only closes if clicking backdrop
});
```
**Safe:** Only triggers on backdrop click, not button clicks.

### 2. HTMX Focus Management ✅ NOT BLOCKING
**File:** `src/static/common/js/htmx-focus-management.js` (Line 145)
```javascript
document.body.addEventListener('click', function(event) {
    const modalLink = event.target.closest('[data-modal-link]');
    // ...no preventDefault() or stopPropagation()
});
```
**Safe:** Doesn't prevent default or stop propagation.

### 3. Calendar Event Click (Line 254-266) ✅ NOT BLOCKING
```javascript
eventClick: function(info) {
    info.jsEvent.preventDefault();  // Only prevents default on calendar events
    openModal(modalUrl);
},
```
**Safe:** Only affects calendar event clicks, not modal buttons.

---

## CSS/Layout Issues Check

### Run in DevTools Console:
```javascript
var btn = document.querySelector('[hx-delete]');
if (btn) {
    var styles = window.getComputedStyle(btn);
    console.log('Display:', styles.display);
    console.log('Visibility:', styles.visibility);
    console.log('Pointer events:', styles.pointerEvents);
    console.log('Z-index:', styles.zIndex);
    console.log('Position:', styles.position);
}
```

**Expected:**
- Display: `inline-flex` ✅
- Visibility: `visible` ✅
- Pointer events: `auto` ✅
- Z-index: `auto` or `1` ✅
- Position: `static` or `relative` ✅

**If NOT Expected:**
- Check for overlay elements blocking clicks
- Inspect parent containers for `pointer-events: none`
- Look for absolute/fixed positioned elements covering button

---

## Complete Fix with Logging

**Replace lines 367-371 in `oobc_calendar.html`:**

```javascript
.then(function(html) {
    modalContent.innerHTML = html;

    console.log('📄 Modal content loaded');

    // Process HTMX attributes
    if (window.htmx) {
        console.log('⚙️  Processing HTMX attributes...');
        htmx.process(modalContent);

        // Verify button is now active
        var deleteBtn = modalContent.querySelector('[hx-delete]');
        console.log('✅ Delete button found:', !!deleteBtn);
        console.log('🔗 Delete URL:', deleteBtn?.getAttribute('hx-delete'));
    } else {
        console.error('❌ HTMX not loaded!');
    }

    attachModalHandlers();
})
```

---

## Monitor HTMX Events (Add to Console)

```javascript
// Run BEFORE opening modal
document.body.addEventListener('htmx:beforeRequest', function(e) {
    console.log('🚀 HTMX Request:', e.detail.requestConfig.verb, e.detail.requestConfig.path);
});

document.body.addEventListener('htmx:afterRequest', function(e) {
    console.log('✅ HTMX Response:', e.detail.xhr.status);
    console.log('📨 HX-Trigger:', e.detail.xhr.getResponseHeader('HX-Trigger'));
});

document.body.addEventListener('htmx:responseError', function(e) {
    console.error('❌ HTMX Error:', e.detail.xhr.status, e.detail.xhr.statusText);
});

document.body.addEventListener('workItemDeleted', function(e) {
    console.log('🗑️  Work item deleted:', e.detail);
});
```

---

## Expected Console Output After Fix

```
📄 Modal content loaded
⚙️  Processing HTMX attributes...
✅ Delete button found: true
🔗 Delete URL: /work-items/abc123-def456/delete/

[User clicks delete button]

🚀 HTMX Request: DELETE /work-items/abc123-def456/delete/
✅ HTMX Response: 200
📨 HX-Trigger: {"workItemDeleted":{...},"showToast":{...}}
🔔 Dispatching event: workItemDeleted {...}
🗑️  Work item deleted: {id: "abc123-def456", title: "Example Task", type: "Task"}
✅ Removed event from calendar: work-item-abc123-def456
✅ Task "Example Task" deleted successfully
```

---

## If htmx.process() Doesn't Work

**Fallback: Manual Event Listener**

Replace `attachModalHandlers()` function (lines 382-425):

```javascript
function attachModalHandlers() {
    // Close button
    var closeBtn = modalContent.querySelector('[data-close-modal]');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeModal);
    }

    // Delete button - MANUAL HANDLER
    var deleteBtn = modalContent.querySelector('[hx-delete]');
    if (deleteBtn) {
        console.log('✅ Attaching manual delete handler');

        deleteBtn.addEventListener('click', function(e) {
            e.preventDefault();

            var deleteUrl = deleteBtn.getAttribute('hx-delete');
            var confirmMsg = deleteBtn.getAttribute('hx-confirm');

            if (confirmMsg && !confirm(confirmMsg)) {
                return;
            }

            console.log('🗑️  Sending DELETE request:', deleteUrl);

            fetch(deleteUrl, {
                method: 'DELETE',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(function(response) {
                var triggerHeader = response.headers.get('HX-Trigger');

                if (response.ok && triggerHeader) {
                    // Dispatch events manually
                    var triggers = JSON.parse(triggerHeader);
                    Object.keys(triggers).forEach(function(name) {
                        document.body.dispatchEvent(new CustomEvent(name, {
                            detail: triggers[name]
                        }));
                    });
                }

                closeModal();
            })
            .catch(function(error) {
                console.error('❌ Delete failed:', error);
                alert('Failed to delete. Please try again.');
            });
        });
    } else {
        console.error('❌ Delete button NOT found');
    }
}
```

---

## Verification Checklist

After applying fix:

- [ ] Modal opens (click calendar event)
- [ ] Delete button is visible
- [ ] Console shows: "✅ Delete button found: true"
- [ ] Click delete button
- [ ] Browser confirmation appears
- [ ] Console shows: "🚀 HTMX Request: DELETE..."
- [ ] Console shows: "📨 HX-Trigger: {..."
- [ ] Console shows: "🗑️ Work item deleted:..."
- [ ] Event disappears from calendar
- [ ] Modal closes
- [ ] Toast notification appears

---

## Common Issues

### Issue: "Button found: false"
**Cause:** HTMX not processing dynamic content
**Fix:** Add `htmx.process(modalContent)`

### Issue: "HTMX: false"
**Cause:** HTMX script not loaded
**Fix:** Check `src/static/vendor/htmx/htmx.min.js` exists
**Fallback:** CDN should load automatically (see base.html line 654)

### Issue: "Status: 403"
**Cause:** Permission denied
**Fix:** Check user permissions in Django admin

### Issue: "Status: 404"
**Cause:** Wrong delete URL
**Fix:** Verify URL in button: `deleteBtn.getAttribute('hx-delete')`

### Issue: Button clicks but nothing happens
**Cause:** HTMX listener not attached
**Fix:** Check console for HTMX events (add listeners from section above)

---

## Files Modified

**1. Primary Fix:**
- `src/templates/common/oobc_calendar.html` (Line 369)
- Add: `if (window.htmx) { htmx.process(modalContent); }`

**2. Optional Fallback:**
- `src/templates/common/oobc_calendar.html` (Lines 382-425)
- Replace: `attachModalHandlers()` function

---

## Time to Fix: 2 Minutes

1. Open `src/templates/common/oobc_calendar.html`
2. Find line 369: `modalContent.innerHTML = html;`
3. Add below it: `if (window.htmx) { htmx.process(modalContent); }`
4. Save file
5. Hard refresh browser (Cmd+Shift+R or Ctrl+Shift+F5)
6. Test delete button

**Done!** 🎉
