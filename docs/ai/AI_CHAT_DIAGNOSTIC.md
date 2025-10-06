# AI Chat Widget Diagnostic Guide

**Issue:** AI chat button not opening the chat panel
**Status:** Investigating

---

## Quick Diagnostic (Paste in Browser Console)

Open the page, press **F12** to open Developer Tools, go to **Console** tab, and paste:

```javascript
// AI Chat Widget Diagnostic
console.log('=== AI CHAT DIAGNOSTIC ===');

// 1. Check if function exists
console.log('1. toggleAIChat function:', typeof window.toggleAIChat);

// 2. Check if elements exist
console.log('2. Chat panel:', document.getElementById('ai-chat-panel'));
console.log('3. Chat button:', document.getElementById('ai-chat-toggle-btn'));
console.log('4. Chat icon:', document.getElementById('ai-chat-icon'));
console.log('5. Chat messages:', document.getElementById('ai-chat-messages'));

// 3. Check panel classes
const panel = document.getElementById('ai-chat-panel');
if (panel) {
    console.log('6. Panel classes:', panel.className);
    console.log('7. Panel computed display:', window.getComputedStyle(panel).display);
    console.log('8. Panel computed opacity:', window.getComputedStyle(panel).opacity);
}

// 4. Try to manually toggle
console.log('9. Attempting manual toggle...');
try {
    if (typeof window.toggleAIChat === 'function') {
        window.toggleAIChat();
        console.log('✅ Toggle executed successfully');
    } else {
        console.error('❌ toggleAIChat function not found');
    }
} catch (error) {
    console.error('❌ Error during toggle:', error);
}

// 5. Check for initialization message
console.log('10. Look for "✅ AI Chat Widget initialized" in console above');

console.log('=== END DIAGNOSTIC ===');
```

---

## Expected Results

### ✅ If Working Correctly:

```
=== AI CHAT DIAGNOSTIC ===
1. toggleAIChat function: function
2. Chat panel: <div id="ai-chat-panel" ...>
3. Chat button: <button id="ai-chat-toggle-btn" ...>
4. Chat icon: <i id="ai-chat-icon" ...>
5. Chat messages: <div id="ai-chat-messages" ...>
6. Panel classes: ai-chat-panel opacity-0 pointer-events-none ...
7. Panel computed display: flex
8. Panel computed opacity: 0
9. Attempting manual toggle...
✅ Toggle executed successfully
10. Look for "✅ AI Chat Widget initialized" in console above
=== END DIAGNOSTIC ===
```

After running the diagnostic, the chat panel should be visible (opacity changed from 0 to 1).

---

## Common Issues & Solutions

### Issue 1: `toggleAIChat function: undefined`

**Problem:** JavaScript didn't execute

**Solutions:**
```bash
# Check for JavaScript errors
# Look in Console for red error messages

# Possible causes:
# - User not authenticated (widget only shows for logged-in users)
# - JavaScript error earlier in page blocking execution
# - Component file not included in base.html
```

**Fix:**
1. Ensure you're logged in
2. Clear browser cache (Cmd+Shift+R / Ctrl+Shift+F5)
3. Check base.html includes component: `{% include 'components/ai_chat_widget.html' %}`

---

### Issue 2: Elements return `null`

**Problem:** HTML not rendering

**Solutions:**
```bash
# Check if user is authenticated
# The widget is wrapped in: {% if user.is_authenticated %}
```

**Fix:**
1. Log in to OBCMS
2. Refresh the page
3. Run diagnostic again

---

### Issue 3: Function exists but toggle doesn't work

**Problem:** CSS classes or animation issue

**Manual toggle test:**
```javascript
// Force open with direct class manipulation
const panel = document.getElementById('ai-chat-panel');
panel.classList.add('chat-open');
panel.style.opacity = '1';
panel.style.pointerEvents = 'auto';
panel.style.transform = 'scale(1)';

// Check if it appears
console.log('Panel visible?', window.getComputedStyle(panel).opacity === '1');
```

---

### Issue 4: Chat opens but immediately closes

**Problem:** Event propagation or duplicate toggles

**Check:**
```javascript
// Add debugging to toggle function
const originalToggle = window.toggleAIChat;
window.toggleAIChat = function() {
    console.log('🔧 toggleAIChat called');
    console.trace(); // Shows who called the function
    originalToggle();
};
```

---

## Manual Testing Steps

### Step 1: Verify Authentication

```python
# In Django shell or template:
{{ user.is_authenticated }}  # Should be True
{{ user.username }}          # Should show username
```

### Step 2: Check Component Inclusion

```bash
# Check base.html line 464:
cd src/templates
grep -n "ai_chat_widget" base.html

# Should show:
# 464:    {% include 'components/ai_chat_widget.html' %}
```

### Step 3: Verify Component File

```bash
# Check if component exists:
ls -la src/templates/components/ai_chat_widget.html

# Should show:
# -rw-r--r--  ... 15155 Oct  6 14:11 ai_chat_widget.html
```

### Step 4: Check Browser DevTools

1. Open page (F12)
2. Go to **Elements** tab
3. Press **Cmd+F** (Ctrl+F) and search for: `ai-chat-widget`
4. Should find: `<div id="ai-chat-widget" class="fixed bottom-6 right-6 z-[9999]">`

If not found → User not authenticated or component not included

---

## Quick Fix: Force Initialization

If the diagnostic shows the function doesn't exist, try forcing initialization:

```javascript
// Paste this in console to manually load the component
const script = document.createElement('script');
script.src = '/static/js/ai-chat-widget.js'; // If you extract to separate file
document.body.appendChild(script);
```

Or reload the component:

```javascript
// Force reload by triggering a full page refresh
location.reload(true);
```

---

## Advanced Debugging

### Enable Verbose Logging

Add this at the top of the component's `<script>` section (line 250):

```javascript
(function() {
    'use strict';

    // ADD THIS LINE:
    const DEBUG = true;

    // Then wrap console.logs:
    const log = DEBUG ? console.log.bind(console, '[AI Chat]') : () => {};

    log('Initializing...');

    // ... rest of code
})();
```

### Check for HTMX Conflicts

```javascript
// Check if HTMX is loaded
console.log('HTMX loaded:', typeof htmx !== 'undefined');

// Check if HTMX is interfering with onclick
const button = document.getElementById('ai-chat-toggle-btn');
console.log('Button onclick:', button.onclick);
console.log('Button attributes:', button.getAttribute('onclick'));
```

---

## Rollback Plan

If the new component isn't working, temporarily revert:

```bash
# Restore old inline version in base.html
# Replace line 464 with the old inline code
# (backup should be in git history)

git diff src/templates/base.html
git checkout HEAD~1 -- src/templates/base.html
```

---

## Next Steps Based on Diagnostic Results

### If diagnostic shows everything working:
→ Try clicking the button manually
→ Check if CSS is hiding it (z-index issue)
→ Check for click event blocking (other overlays)

### If diagnostic shows function undefined:
→ Check authentication status
→ Check for JavaScript errors in console
→ Verify component file is included

### If diagnostic shows elements are null:
→ User not logged in
→ Component not rendering
→ Check template syntax errors

---

## Contact Information

If issue persists after diagnostic:
1. Copy all console output
2. Take screenshot of Elements tab (showing or not showing widget)
3. Note browser version
4. Note user authentication status

---

**Created:** October 6, 2025
**Status:** Diagnostic tool ready
**Next:** Run diagnostic in browser console
