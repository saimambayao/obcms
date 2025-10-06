# AI Chat Widget Positioning Debug Guide

## 🔍 Overview

This guide helps developers diagnose and fix positioning issues with the AI Chat Widget in OBCMS. The widget should appear in the bottom-right corner of the viewport, with the chat panel opening upward from the toggle button.

---

## 📐 Expected Positioning Behavior

### Desktop (> 640px)
```
┌─────────────────────────────────────────┐
│                                         │
│  VIEWPORT                               │
│                                         │
│                          ┌──────────┐   │
│                          │ AI Chat  │   │
│                          │  Panel   │   │
│                          │          │   │
│                          │          │   │
│                          └──────────┘   │
│                                ▲         │
│                                │         │
│                             [Button]  ← Fixed: bottom-right
└─────────────────────────────────────────┘
   Bottom: 24px (1.5rem)
   Right: 24px (1.5rem)
```

### Mobile (< 640px)
```
┌─────────────────────────────────────────┐
│                                         │
│  VIEWPORT                               │
│                                         │
│┌───────────────────────────────────────┐│
││                                       ││
││        AI Chat Panel                  ││
││        (80vh height)                  ││
││        (Full width)                   ││
││                                       ││
│└───────────────────────────────────────┘│
│                                         │
│                              [Button]   │
└─────────────────────────────────────────┘
   Panel: Fixed to bottom, full-width
   Button: bottom: 16px, right: 16px
```

---

## 🐛 Common Issues & Solutions

### Issue 1: Panel Not Visible (Above Viewport)

**Symptoms:**
- Panel opens but can't be seen
- Console shows negative `top` value
- Panel positioned above screen

**Diagnosis:**
```javascript
// Run in console
const panel = document.getElementById('ai-chat-panel');
const rect = panel.getBoundingClientRect();
console.log('Panel top:', rect.top); // Negative = above viewport
```

**Root Causes:**
1. ❌ Panel uses `position: absolute` with `bottom: full`
2. ❌ Parent container has incorrect positioning
3. ❌ CSS `bottom` calculation is wrong

**Solution:**
```css
/* CORRECT - Panel opens upward from button */
#ai-chat-panel {
    position: absolute;
    bottom: calc(100% + 8px); /* 100% of button height + gap */
    right: 0;
    max-height: calc(100vh - 120px);
}

/* INCORRECT - Don't use these */
#ai-chat-panel {
    position: absolute;
    bottom: 100%; /* ❌ No gap, might clip */
    top: auto; /* ❌ Don't set top */
}
```

**Quick Fix Command:**
```javascript
// Force panel to correct position
document.getElementById('ai-chat-panel').style.cssText = `
    position: absolute !important;
    bottom: calc(100% + 8px) !important;
    right: 0 !important;
    max-height: calc(100vh - 120px) !important;
`;
```

---

### Issue 2: Widget Container Not Fixed

**Symptoms:**
- Widget scrolls with page content
- Widget not visible in bottom-right corner
- Position changes on scroll

**Diagnosis:**
```javascript
// Check widget container position
const widget = document.getElementById('ai-chat-widget');
const style = window.getComputedStyle(widget);
console.log('Widget position:', style.position); // Should be "fixed"
console.log('Widget bottom:', style.bottom); // Should be "24px" or "1.5rem"
console.log('Widget right:', style.right); // Should be "24px" or "1.5rem"
```

**Solution:**
```css
/* CORRECT - Widget stays fixed in viewport */
#ai-chat-widget {
    position: fixed;
    bottom: 1.5rem; /* 24px */
    right: 1.5rem; /* 24px */
    z-index: 9999;
}

/* INCORRECT */
#ai-chat-widget {
    position: absolute; /* ❌ Scrolls with page */
    bottom: 6rem; /* ❌ Too high */
}
```

---

### Issue 3: Panel Height Calculation Wrong

**Symptoms:**
- Panel extends beyond viewport
- Bottom of panel not visible
- Panel too tall on mobile

**Diagnosis:**
```javascript
// Check panel height vs viewport
const panel = document.getElementById('ai-chat-panel');
const rect = panel.getBoundingClientRect();
const viewport = window.innerHeight;
console.log('Panel height:', rect.height);
console.log('Viewport height:', viewport);
console.log('Panel fits?', rect.height < viewport - 120); // Should be true
```

**Solution:**
```css
/* CORRECT - Panel respects viewport */
#ai-chat-panel {
    height: min(500px, calc(100vh - 120px));
    /* Desktop: 500px max, always 120px gap */
    /* Mobile: 80vh for better experience */
}

@media (max-width: 640px) {
    #ai-chat-panel {
        height: 80vh !important; /* Fixed 80% of viewport */
    }
}
```

---

### Issue 4: Z-Index Conflicts

**Symptoms:**
- Panel appears behind other elements
- Widget hidden by navigation or modals

**Diagnosis:**
```javascript
// Check z-index hierarchy
const widget = document.getElementById('ai-chat-widget');
const panel = document.getElementById('ai-chat-panel');
console.log('Widget z-index:', window.getComputedStyle(widget).zIndex);
console.log('Panel z-index:', window.getComputedStyle(panel).zIndex);

// Check for conflicting elements
document.querySelectorAll('[style*="z-index"]').forEach(el => {
    const z = window.getComputedStyle(el).zIndex;
    if (parseInt(z) > 9999) {
        console.warn('Higher z-index found:', el, z);
    }
});
```

**Solution:**
```css
/* Z-Index Hierarchy */
#ai-chat-widget {
    z-index: 9999; /* Widget container */
}

#ai-chat-panel {
    z-index: inherit; /* Inherits from widget */
}

#ai-chat-backdrop {
    z-index: -1; /* Behind panel, relative to widget */
}

/* Common OBCMS z-indexes */
/* Navbar: 50 */
/* Modals: 1000-2000 */
/* Toasts: 50 (top-6 right-6) */
/* AI Chat: 9999 (highest) */
```

---

### Issue 5: Mobile Panel Not Full Width

**Symptoms:**
- Panel doesn't fill width on mobile
- Gap on left/right sides on small screens

**Solution:**
```css
@media (max-width: 640px) {
    #ai-chat-panel {
        position: fixed !important; /* Override absolute */
        bottom: 0 !important;
        right: 0 !important;
        left: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
        height: 80vh !important;
        margin: 0 !important;
        border-radius: 1rem 1rem 0 0 !important; /* Top corners only */
    }
}
```

---

## 🛠️ Debugging Tools

### 1. Console Position Debugger

**Copy-paste this into browser console:**

```javascript
// AI Chat Position Debugger
// Paste in browser console to diagnose positioning issues

(function() {
    console.log('🔍 AI CHAT POSITION DEBUGGER');
    console.log('================================');

    const widget = document.getElementById('ai-chat-widget');
    const button = document.getElementById('ai-chat-toggle-btn');
    const panel = document.getElementById('ai-chat-panel');

    if (!widget || !button || !panel) {
        console.error('❌ Elements not found:', {
            widget: !!widget,
            button: !!button,
            panel: !!panel
        });
        return;
    }

    // 1. Widget Container Analysis
    const widgetRect = widget.getBoundingClientRect();
    const widgetStyle = window.getComputedStyle(widget);
    console.log('\n1️⃣ WIDGET CONTAINER:');
    console.log('   Position:', widgetStyle.position, widgetStyle.position === 'fixed' ? '✅' : '❌ Should be fixed');
    console.log('   Bottom:', widgetStyle.bottom);
    console.log('   Right:', widgetStyle.right);
    console.log('   Z-Index:', widgetStyle.zIndex);
    console.log('   Bounds:', {
        top: Math.round(widgetRect.top),
        bottom: Math.round(widgetRect.bottom),
        left: Math.round(widgetRect.left),
        right: Math.round(widgetRect.right)
    });

    // 2. Toggle Button Analysis
    const buttonRect = button.getBoundingClientRect();
    console.log('\n2️⃣ TOGGLE BUTTON:');
    console.log('   Size:', Math.round(buttonRect.width) + 'x' + Math.round(buttonRect.height));
    console.log('   Position:', {
        top: Math.round(buttonRect.top),
        left: Math.round(buttonRect.left)
    });

    // 3. Chat Panel Analysis
    const panelRect = panel.getBoundingClientRect();
    const panelStyle = window.getComputedStyle(panel);
    console.log('\n3️⃣ CHAT PANEL:');
    console.log('   Position:', panelStyle.position);
    console.log('   Top:', panelStyle.top);
    console.log('   Bottom:', panelStyle.bottom);
    console.log('   Right:', panelStyle.right);
    console.log('   Width:', panelStyle.width);
    console.log('   Height:', panelStyle.height);
    console.log('   Max-Height:', panelStyle.maxHeight);
    console.log('   Opacity:', panelStyle.opacity, panelStyle.opacity === '1' ? '✅' : '❌');
    console.log('   Transform:', panelStyle.transform);
    console.log('   Z-Index:', panelStyle.zIndex);
    console.log('   Bounds:', {
        top: Math.round(panelRect.top),
        bottom: Math.round(panelRect.bottom),
        left: Math.round(panelRect.left),
        right: Math.round(panelRect.right),
        width: Math.round(panelRect.width),
        height: Math.round(panelRect.height)
    });

    // 4. Viewport Info
    console.log('\n4️⃣ VIEWPORT:');
    console.log('   Width:', window.innerWidth);
    console.log('   Height:', window.innerHeight);
    console.log('   Device:', window.innerWidth < 640 ? 'Mobile' : 'Desktop');

    // 5. Visibility Check
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;
    const isVisible =
        panelRect.top >= 0 &&
        panelRect.bottom <= viewportHeight &&
        panelRect.left >= 0 &&
        panelRect.right <= viewportWidth;

    console.log('\n5️⃣ VISIBILITY CHECK:');
    console.log('   Is Visible:', isVisible ? '✅ YES' : '❌ NO');

    if (!isVisible) {
        const reasons = [];
        if (panelRect.top < 0) reasons.push('Panel TOP is above viewport (top: ' + Math.round(panelRect.top) + 'px)');
        if (panelRect.bottom > viewportHeight) reasons.push('Panel BOTTOM is below viewport (bottom: ' + Math.round(panelRect.bottom) + 'px, viewport: ' + viewportHeight + 'px)');
        if (panelRect.left < 0) reasons.push('Panel LEFT is outside viewport (left: ' + Math.round(panelRect.left) + 'px)');
        if (panelRect.right > viewportWidth) reasons.push('Panel RIGHT is outside viewport (right: ' + Math.round(panelRect.right) + 'px, viewport: ' + viewportWidth + 'px)');

        console.log('   Reasons:');
        reasons.forEach(r => console.log('   ❌', r));
    }

    // 6. Recommendations
    console.log('\n6️⃣ RECOMMENDATIONS:');

    if (panelRect.top < 0) {
        console.warn('   ⚠️ Panel is ABOVE viewport');
        console.log('   💡 Fix: Adjust bottom positioning');
        console.log('   💡 Run: document.getElementById("ai-chat-panel").style.bottom = "calc(100% + 8px)"');
    }

    if (panelRect.bottom > viewportHeight) {
        console.warn('   ⚠️ Panel is BELOW viewport or TOO TALL');
        console.log('   💡 Fix: Reduce max-height');
        console.log('   💡 Run: document.getElementById("ai-chat-panel").style.maxHeight = "calc(100vh - 120px)"');
    }

    if (panelStyle.opacity === '0') {
        console.warn('   ⚠️ Panel opacity is 0');
        console.log('   💡 Fix: Add "chat-open" class');
        console.log('   💡 Run: document.getElementById("ai-chat-panel").classList.add("chat-open")');
    }

    if (widgetStyle.position !== 'fixed') {
        console.warn('   ⚠️ Widget is not fixed position');
        console.log('   💡 Fix: Change widget to position: fixed');
        console.log('   💡 Run: document.getElementById("ai-chat-widget").style.position = "fixed"');
    }

    if (panelStyle.position === 'absolute' && window.innerWidth < 640) {
        console.warn('   ⚠️ Panel should be fixed on mobile');
        console.log('   💡 Fix: Change panel to position: fixed on mobile');
    }

    if (isVisible) {
        console.log('   ✅ Panel is correctly positioned!');
    }

    console.log('\n================================');
    console.log('✅ Diagnostic complete');
    console.log('\nNeed visual overlay? Run: addVisualDebug()');
})();
```

---

### 2. Visual Overlay Debugger

**Add red border to see exact panel position:**

```javascript
// Add visual debugging overlay
function addVisualDebug() {
    // Remove existing overlay
    const existing = document.getElementById('chat-debug-overlay');
    if (existing) existing.remove();

    const panel = document.getElementById('ai-chat-panel');
    const button = document.getElementById('ai-chat-toggle-btn');
    const widget = document.getElementById('ai-chat-widget');

    const panelRect = panel.getBoundingClientRect();
    const buttonRect = button.getBoundingClientRect();
    const widgetRect = widget.getBoundingClientRect();

    // Panel overlay
    const panelOverlay = document.createElement('div');
    panelOverlay.id = 'chat-debug-overlay';
    panelOverlay.style.cssText = `
        position: fixed;
        top: ${panelRect.top}px;
        left: ${panelRect.left}px;
        width: ${panelRect.width}px;
        height: ${panelRect.height}px;
        border: 5px dashed red;
        background: rgba(255, 0, 0, 0.1);
        pointer-events: none;
        z-index: 99999;
    `;

    const panelLabel = document.createElement('div');
    panelLabel.style.cssText = `
        position: absolute;
        top: -35px;
        left: 0;
        background: red;
        color: white;
        padding: 5px 10px;
        font-size: 12px;
        font-weight: bold;
        white-space: nowrap;
    `;
    panelLabel.textContent = `Panel: ${Math.round(panelRect.top)}px from top | ${Math.round(panelRect.height)}px tall`;
    panelOverlay.appendChild(panelLabel);

    // Button overlay
    const buttonOverlay = document.createElement('div');
    buttonOverlay.style.cssText = `
        position: fixed;
        top: ${buttonRect.top}px;
        left: ${buttonRect.left}px;
        width: ${buttonRect.width}px;
        height: ${buttonRect.height}px;
        border: 3px dashed blue;
        background: rgba(0, 0, 255, 0.1);
        pointer-events: none;
        z-index: 99999;
    `;

    const buttonLabel = document.createElement('div');
    buttonLabel.style.cssText = `
        position: absolute;
        bottom: -25px;
        right: 0;
        background: blue;
        color: white;
        padding: 3px 8px;
        font-size: 11px;
        font-weight: bold;
        white-space: nowrap;
    `;
    buttonLabel.textContent = `Button`;
    buttonOverlay.appendChild(buttonLabel);

    // Widget container overlay
    const widgetOverlay = document.createElement('div');
    widgetOverlay.style.cssText = `
        position: fixed;
        top: ${widgetRect.top}px;
        left: ${widgetRect.left}px;
        width: ${widgetRect.width}px;
        height: ${widgetRect.height}px;
        border: 3px dashed green;
        background: rgba(0, 255, 0, 0.05);
        pointer-events: none;
        z-index: 99998;
    `;

    const widgetLabel = document.createElement('div');
    widgetLabel.style.cssText = `
        position: absolute;
        top: -25px;
        left: 0;
        background: green;
        color: white;
        padding: 3px 8px;
        font-size: 11px;
        font-weight: bold;
        white-space: nowrap;
    `;
    widgetLabel.textContent = `Widget Container`;
    widgetOverlay.appendChild(widgetLabel);

    // Viewport guide
    const viewportGuide = document.createElement('div');
    viewportGuide.style.cssText = `
        position: fixed;
        top: 10px;
        left: 10px;
        background: black;
        color: white;
        padding: 10px;
        font-size: 12px;
        font-family: monospace;
        z-index: 99999;
        border-radius: 5px;
    `;
    viewportGuide.innerHTML = `
        <strong>🔍 Debug Overlay Active</strong><br>
        Viewport: ${window.innerWidth} x ${window.innerHeight}<br>
        Panel visible: ${panelRect.top >= 0 && panelRect.bottom <= window.innerHeight ? '✅' : '❌'}<br>
        <small>Overlay will auto-remove in 10s</small>
    `;

    document.body.appendChild(widgetOverlay);
    document.body.appendChild(buttonOverlay);
    document.body.appendChild(panelOverlay);
    document.body.appendChild(viewportGuide);

    console.log('✅ Visual debug overlay added (10s duration)');
    console.log('   🟢 Green = Widget container');
    console.log('   🔵 Blue = Toggle button');
    console.log('   🔴 Red = Chat panel');

    setTimeout(() => {
        widgetOverlay.remove();
        buttonOverlay.remove();
        panelOverlay.remove();
        viewportGuide.remove();
        console.log('✅ Visual debug overlay removed');
    }, 10000);
}

// Run it
addVisualDebug();
```

---

### 3. Quick Fix Commands

**Copy-paste these to fix common issues:**

#### Fix 1: Force Panel Visibility
```javascript
// QUICK FIX: Make panel visible
const panel = document.getElementById('ai-chat-panel');
panel.style.cssText = `
    position: absolute !important;
    bottom: calc(100% + 8px) !important;
    right: 0 !important;
    max-height: calc(100vh - 120px) !important;
    opacity: 1 !important;
    pointer-events: auto !important;
    transform: scale(1) !important;
    border: 3px solid green !important;
`;
panel.classList.add('chat-open');
console.log('✅ Panel forced visible (green border = debug mode)');
```

#### Fix 2: Reset Widget Position
```javascript
// QUICK FIX: Reset widget to correct position
const widget = document.getElementById('ai-chat-widget');
widget.style.cssText = `
    position: fixed !important;
    bottom: 1.5rem !important;
    right: 1.5rem !important;
    z-index: 9999 !important;
`;
console.log('✅ Widget position reset to bottom-right');
```

#### Fix 3: Fix Mobile Layout
```javascript
// QUICK FIX: Force mobile layout
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
    console.log('✅ Mobile layout applied');
}
```

#### Fix 4: Complete Reset
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
        position: absolute;
        bottom: calc(100% + 8px);
        right: 0;
        width: 24rem;
        max-width: calc(100vw - 2rem);
        height: min(500px, calc(100vh - 120px));
    `;
    panel.classList.remove('chat-open');

    // Reset button
    button.classList.remove('chat-active');
    button.setAttribute('aria-expanded', 'false');

    console.log('✅ Complete reset to default positioning');
})();
```

---

## 🧪 Testing Checklist

### Desktop Testing
- [ ] Widget appears in bottom-right corner
- [ ] Panel opens upward from button
- [ ] Panel doesn't exceed viewport height
- [ ] Panel stays within viewport bounds
- [ ] Smooth open/close animations
- [ ] No visual glitches on resize

### Mobile Testing
- [ ] Widget appears in bottom-right (with smaller margin)
- [ ] Panel is full-width
- [ ] Panel is 80vh height
- [ ] Panel rounded top corners only
- [ ] Backdrop appears behind panel
- [ ] Touch interactions work smoothly

### Browser DevTools Inspection

1. **Open DevTools** (F12 or Cmd+Opt+I)

2. **Select AI Chat Widget:**
   ```
   Elements → Find: #ai-chat-widget
   ```

3. **Check Computed Styles:**
   ```
   Widget should have:
   - position: fixed
   - bottom: 24px (or 1.5rem)
   - right: 24px (or 1.5rem)
   - z-index: 9999
   ```

4. **Select AI Chat Panel:**
   ```
   Elements → Find: #ai-chat-panel
   ```

5. **Check Computed Styles:**
   ```
   Panel should have:
   - position: absolute
   - bottom: calc(100% + 8px) [or similar]
   - right: 0px
   - max-height: calc(100vh - 120px)
   ```

6. **Trigger State Change:**
   ```
   Console → toggleAIChat()
   ```

7. **Verify Class Toggle:**
   ```
   Panel should gain: .chat-open
   - opacity: 1
   - pointer-events: auto
   - transform: scale(1)
   ```

---

## 📊 Visual Comparison

### ✅ CORRECT Positioning

**Desktop:**
```
Panel visible within viewport:
- Top edge visible (not cut off)
- Bottom aligned above button
- Right edge aligned with button
- Height respects max-height
```

**Mobile:**
```
Panel full-width:
- Left edge: 0
- Right edge: 0
- Bottom edge: 0
- Height: 80vh
```

### ❌ INCORRECT Positioning

**Desktop:**
```
Panel above viewport:
- Top edge negative Y
- Can't see panel content
- Only button visible
```

**Desktop:**
```
Panel too tall:
- Bottom extends beyond button
- Scrollbar appears on page
- Top cut off
```

**Mobile:**
```
Panel not full-width:
- Gaps on left/right
- Smaller than expected
- Doesn't touch edges
```

---

## 🔄 Troubleshooting Flowchart

```
START: Panel not visible?
    ↓
Is widget position: fixed?
    NO → Set widget to position: fixed, bottom: 1.5rem, right: 1.5rem
    YES ↓

Is panel.getBoundingClientRect().top < 0?
    YES → Panel above viewport
          → Fix: panel.style.bottom = "calc(100% + 8px)"
    NO ↓

Is panel.getBoundingClientRect().bottom > window.innerHeight?
    YES → Panel too tall
          → Fix: panel.style.maxHeight = "calc(100vh - 120px)"
    NO ↓

Is panel opacity = 0?
    YES → Panel invisible (not opened)
          → Fix: panel.classList.add('chat-open')
    NO ↓

Is panel z-index < 9999?
    YES → Panel behind other elements
          → Fix: widget.style.zIndex = "9999"
    NO ↓

✅ PANEL SHOULD BE VISIBLE
   Run visual debug to confirm: addVisualDebug()
```

---

## 🎯 Best Practices

### DO ✅
- Use `position: fixed` for widget container
- Use `position: absolute` for panel (relative to widget)
- Calculate panel height with `calc(100vh - 120px)`
- Test on multiple screen sizes
- Use visual debug overlay for verification
- Check console for positioning errors

### DON'T ❌
- Don't use `top` property on panel (use `bottom` only)
- Don't hardcode panel height (use `calc()` or `min()`)
- Don't forget mobile styles (@media max-width: 640px)
- Don't set widget to `position: absolute`
- Don't ignore z-index hierarchy

---

## 📝 Implementation Notes

### Current Implementation
- **File:** `/src/templates/components/ai_chat_widget.html`
- **Widget ID:** `ai-chat-widget`
- **Panel ID:** `ai-chat-panel`
- **Button ID:** `ai-chat-toggle-btn`
- **Open State Class:** `chat-open`

### CSS Architecture
```css
/* Widget Container - Fixed to viewport */
#ai-chat-widget {
    position: fixed;
    bottom: 1.5rem; /* 24px */
    right: 1.5rem;
    z-index: 9999;
}

/* Panel - Relative to widget, opens upward */
#ai-chat-panel {
    position: absolute;
    bottom: calc(100% + 8px); /* Full button height + gap */
    right: 0;
    max-height: calc(100vh - 120px); /* Viewport - margins */
}

/* Open State - Visible and interactive */
.ai-chat-panel.chat-open {
    opacity: 1;
    pointer-events: auto;
    transform: scale(1);
}

/* Mobile Override - Full screen panel */
@media (max-width: 640px) {
    #ai-chat-panel {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        width: 100% !important;
        height: 80vh !important;
    }
}
```

---

## 🆘 Support

If issues persist after trying all fixes:

1. **Run Full Diagnostic:**
   ```javascript
   // Copy-paste the console debugger from section "1. Console Position Debugger"
   ```

2. **Add Visual Overlay:**
   ```javascript
   addVisualDebug();
   ```

3. **Check Browser Console:**
   - Look for JavaScript errors
   - Check network tab for CSS loading issues
   - Verify HTMX is loaded

4. **Document the Issue:**
   - Screenshot of DevTools Elements panel
   - Screenshot of Console diagnostic output
   - Screenshot with visual debug overlay
   - Browser and screen size details

5. **Contact Team:**
   - Share diagnostic screenshots
   - Provide browser/device info
   - Include steps to reproduce

---

## 📚 Related Documentation

- [OBCMS UI Components & Standards](./OBCMS_UI_COMPONENTS_STANDARDS.md)
- [AI Chat Widget Implementation](../../src/templates/components/ai_chat_widget.html)
- [Instant UI Improvements Plan](../improvements/instant_ui_improvements_plan.md)

---

**Last Updated:** 2025-10-06
**Status:** ✅ Complete
**Maintainer:** OBCMS Development Team
