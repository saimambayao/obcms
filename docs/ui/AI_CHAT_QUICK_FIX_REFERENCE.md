# AI Chat Widget - Quick Fix Reference Card

## 🚀 Quick Start

**Problem:** AI chat panel not visible when opened?

**Solution:** Copy-paste one of these commands into browser console:

```javascript
// 1. Run diagnostic first
// Copy from: docs/testing/ai_chat_console_debugger.js

// 2. Add visual overlay
// Copy from: docs/testing/ai_chat_visual_debugger.js
addVisualDebug()

// 3. Apply quick fix
applyQuickFix()
```

---

## 🔧 Quick Fix Commands

### Fix 1: Force Panel Visible (Most Common)

```javascript
// QUICK FIX: Make panel visible immediately
const panel = document.getElementById('ai-chat-panel');
panel.style.cssText = `
    position: fixed !important;
    bottom: 88px !important;
    right: 24px !important;
    max-height: calc(100vh - 140px) !important;
    opacity: 1 !important;
    visibility: visible !important;
    pointer-events: auto !important;
    transform: scale(1) !important;
    border: 3px solid green !important;
`;
panel.classList.add('chat-open');
console.log('✅ Panel forced visible (green border = debug mode)');
```

**When to use:**
- Panel opens but you can't see it
- Panel is above or below viewport
- Panel has opacity/visibility issues

---

### Fix 2: Reset Widget Position

```javascript
// QUICK FIX: Reset widget to bottom-right corner
const widget = document.getElementById('ai-chat-widget');
widget.style.cssText = `
    position: fixed !important;
    bottom: 1.5rem !important;
    right: 1.5rem !important;
    z-index: 9999 !important;
`;
console.log('✅ Widget position reset to bottom-right');
```

**When to use:**
- Widget not in bottom-right corner
- Widget scrolls with page content
- Widget not visible at all

---

### Fix 3: Force Mobile Layout

```javascript
// QUICK FIX: Apply mobile full-width layout
if (window.innerWidth < 640) {
    const panel = document.getElementById('ai-chat-panel');
    panel.style.cssText = `
        position: fixed !important;
        bottom: 0 !important;
        right: 0 !important;
        left: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
        height: 80vh !important;
        margin: 0 !important;
        border-radius: 1rem 1rem 0 0 !important;
    `;
    console.log('✅ Mobile layout forced');
}
```

**When to use:**
- On mobile, panel not full-width
- Panel has gaps on left/right on small screens

---

### Fix 4: Complete Reset

```javascript
// QUICK FIX: Complete reset to default state
(function() {
    const widget = document.getElementById('ai-chat-widget');
    const panel = document.getElementById('ai-chat-panel');
    const button = document.getElementById('ai-chat-toggle-btn');

    // Reset widget
    widget.style.cssText = `
        position: fixed;
        bottom: 1.5rem;
        right: 1.5rem;
        z-index: 9999;
    `;

    // Reset panel
    panel.style.cssText = `
        position: fixed;
        bottom: 88px;
        right: 24px;
        max-height: calc(100vh - 140px);
    `;
    panel.classList.remove('chat-open');

    // Reset button
    button.classList.remove('chat-active');
    button.setAttribute('aria-expanded', 'false');

    console.log('✅ Complete reset to default positioning');
})();
```

**When to use:**
- Multiple issues present
- After testing different fixes
- Before reporting a bug

---

### Fix 5: Fix Z-Index Issues

```javascript
// QUICK FIX: Ensure chat is on top of all elements
const widget = document.getElementById('ai-chat-widget');
const panel = document.getElementById('ai-chat-panel');

widget.style.zIndex = '99999';
panel.style.zIndex = '99999';

console.log('✅ Z-index boosted to 99999');
```

**When to use:**
- Panel appears behind other elements
- Navigation or modals covering chat

---

## 🐛 Debug Commands

### Enable Visual Debug Mode

```javascript
// Show panel with colored borders
// Red = closed, Green = open
document.getElementById('ai-chat-widget').classList.add('debug-chat');
console.log('✅ Debug mode ON');

// Disable debug mode
document.getElementById('ai-chat-widget').classList.remove('debug-chat');
console.log('✅ Debug mode OFF');
```

---

### Check Panel Position

```javascript
// Quick position check
const panel = document.getElementById('ai-chat-panel');
const rect = panel.getBoundingClientRect();
console.log('Panel Position:', {
    top: Math.round(rect.top),
    bottom: Math.round(rect.bottom),
    left: Math.round(rect.left),
    right: Math.round(rect.right),
    inViewport: rect.top >= 0 && rect.bottom <= window.innerHeight
});
```

---

### Toggle Chat (Manual)

```javascript
// Open/close chat manually
toggleAIChat();

// Force open
document.getElementById('ai-chat-panel').classList.add('chat-open');

// Force close
document.getElementById('ai-chat-panel').classList.remove('chat-open');
```

---

## 📊 Common Issues & Solutions

### Issue: Panel Above Viewport

**Symptom:** Panel opens but you can't see it

**Quick Check:**
```javascript
const panel = document.getElementById('ai-chat-panel');
const rect = panel.getBoundingClientRect();
console.log('Top:', rect.top); // Negative = above viewport
```

**Fix:**
```javascript
panel.style.bottom = '88px';
panel.style.top = 'auto';
```

---

### Issue: Panel Too Tall

**Symptom:** Panel extends beyond viewport

**Quick Check:**
```javascript
const panel = document.getElementById('ai-chat-panel');
const rect = panel.getBoundingClientRect();
console.log('Height:', rect.height, 'Viewport:', window.innerHeight);
console.log('Too tall?', rect.height > window.innerHeight - 140);
```

**Fix:**
```javascript
panel.style.maxHeight = 'calc(100vh - 140px)';
panel.style.height = 'min(500px, calc(100vh - 140px))';
```

---

### Issue: Widget Scrolls with Page

**Symptom:** Chat widget moves when scrolling

**Quick Check:**
```javascript
const widget = document.getElementById('ai-chat-widget');
console.log('Position:', getComputedStyle(widget).position);
// Should be "fixed"
```

**Fix:**
```javascript
widget.style.position = 'fixed';
widget.style.bottom = '1.5rem';
widget.style.right = '1.5rem';
```

---

### Issue: Panel Invisible (Opacity)

**Symptom:** Panel opens but is invisible

**Quick Check:**
```javascript
const panel = document.getElementById('ai-chat-panel');
const style = getComputedStyle(panel);
console.log('Opacity:', style.opacity);
console.log('Visibility:', style.visibility);
console.log('Has chat-open class?', panel.classList.contains('chat-open'));
```

**Fix:**
```javascript
panel.style.opacity = '1';
panel.style.visibility = 'visible';
panel.classList.add('chat-open');
```

---

## 🔍 Load Full Debuggers

### Console Debugger (Full Diagnostic)

```javascript
// Load and run full diagnostic
// Copy entire content from: docs/testing/ai_chat_console_debugger.js
// Then paste in console

// Or download and run:
fetch('/static/docs/testing/ai_chat_console_debugger.js')
    .then(r => r.text())
    .then(eval);
```

### Visual Overlay Debugger

```javascript
// Load visual debugger
// Copy entire content from: docs/testing/ai_chat_visual_debugger.js
// Then paste in console

// Or download and run:
fetch('/static/docs/testing/ai_chat_visual_debugger.js')
    .then(r => r.text())
    .then(eval)
    .then(() => addVisualDebug());
```

---

## 📐 Expected Positioning Values

### Desktop (≥ 640px)

```css
/* Widget Container */
#ai-chat-widget {
    position: fixed;        /* ✅ Required */
    bottom: 1.5rem;         /* 24px */
    right: 1.5rem;          /* 24px */
    z-index: 9999;
}

/* Chat Panel */
#ai-chat-panel {
    position: fixed;        /* ✅ Fixed positioning */
    bottom: 88px;           /* Button height + gap */
    right: 24px;
    max-height: calc(100vh - 140px);
}

/* Open State */
#ai-chat-panel.chat-open {
    opacity: 1;
    visibility: visible;
    pointer-events: auto;
    transform: scale(1);
}
```

### Mobile (< 640px)

```css
/* Widget Container */
#ai-chat-widget {
    position: fixed;
    bottom: 1rem;           /* 16px on mobile */
    right: 1rem;            /* 16px on mobile */
    z-index: 9999;
}

/* Chat Panel - Full Width */
#ai-chat-panel {
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    right: 0 !important;
    width: 100% !important;
    height: 80vh !important;
    border-radius: 1rem 1rem 0 0 !important;
}
```

---

## 🎯 Testing Checklist

### Desktop
- [ ] Widget in bottom-right (24px from edges)
- [ ] Panel opens upward from button
- [ ] Panel doesn't exceed viewport height
- [ ] Panel visible within viewport
- [ ] Smooth animations
- [ ] Z-index correct (no overlapping)

### Mobile
- [ ] Widget in bottom-right (16px from edges)
- [ ] Panel full-width
- [ ] Panel 80vh height
- [ ] Panel rounded top corners only
- [ ] Backdrop appears
- [ ] Touch interactions work

---

## 🆘 If All Fixes Fail

1. **Check Browser Console:**
   - Look for JavaScript errors
   - Check if HTMX is loaded
   - Verify CSS files loaded

2. **Check Template:**
   ```bash
   # Ensure template is included
   grep -r "ai_chat_widget.html" src/templates/base.html
   ```

3. **Check Static Files:**
   ```bash
   # Restart server after static changes
   python manage.py collectstatic --noinput
   python manage.py runserver
   ```

4. **Report Issue:**
   - Browser + version
   - Screen size
   - Console debugger output (copy-paste)
   - Visual overlay screenshot
   - Steps to reproduce

---

## 📚 Related Documentation

- **Full Debug Guide:** [AI_CHAT_POSITIONING_DEBUG_GUIDE.md](./AI_CHAT_POSITIONING_DEBUG_GUIDE.md)
- **Console Debugger:** [ai_chat_console_debugger.js](../testing/ai_chat_console_debugger.js)
- **Visual Debugger:** [ai_chat_visual_debugger.js](../testing/ai_chat_visual_debugger.js)
- **Widget Template:** [ai_chat_widget.html](../../src/templates/components/ai_chat_widget.html)

---

**Last Updated:** 2025-10-06
**Quick Start:** Run visual debugger → `addVisualDebug()` → Apply appropriate fix
