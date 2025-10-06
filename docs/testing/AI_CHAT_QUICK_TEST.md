# AI Chat Panel - Quick Testing Guide

## 🚀 Immediate Testing Steps

### 1. Visual Verification (30 seconds)

**Open any OBCMS page with the AI chat widget:**

1. **Locate the toggle button** (bottom-right corner, emerald gradient circle)
2. **Click the button**
3. **Verify panel appears** above the button

**Expected Result:**
- ✅ Panel slides up from button with smooth animation
- ✅ Panel is fully visible (white card with "AI Assistant" header)
- ✅ Button icon changes to X
- ✅ Panel positioned correctly (doesn't overflow viewport)

**If panel is invisible:**
- Proceed to Debug Mode (Section 2)

---

### 2. Debug Mode (Console Testing)

**Open browser DevTools (F12 or Cmd+Option+I on Mac):**

#### Enable Visual Debug Mode
```javascript
// In console, run:
window.enableAIChatDebug();
```

**What happens:**
- Panel shows with **RED border** when closed
- Panel shows with **GREEN border** when open
- Background turns yellow-tinted to confirm visibility

**Verification:**
- Can you see the red border around the panel area?
  - ✅ YES → Panel is rendered, positioning is correct
  - ❌ NO → Panel is off-screen or clipped (see Section 3)

#### Check Panel Position
```javascript
// In console, run:
window.debugAIChat();
```

**Expected Output:**
```javascript
=== AI Chat Debug Info ===
Chat open: true/false
Panel position: {
    top: ~312,      // Should be positive number
    bottom: ~812,   // Should be < viewport height
    left: ~1512,    // Depends on viewport width
    right: ~1920,   // Depends on viewport width
    height: 500,    // Or less if viewport is small
    width: 384
}
Computed styles: {
    position: "fixed",
    bottom: "88px",
    right: "24px",
    opacity: "0" or "1",
    visibility: "hidden" or "visible",
    transform: "matrix(...)",
    zIndex: "9999"
}
Visibility check: {
    inViewportVertically: true,     // Must be true
    inViewportHorizontally: true,   // Must be true
    hasOpenClass: true/false,
    ariaHidden: "true" or "false"
}
```

**Red Flags (Problems):**
- ❌ `inViewportVertically: false` → Panel is off-screen vertically
- ❌ `inViewportHorizontally: false` → Panel is off-screen horizontally
- ❌ `visibility: "hidden"` when open → CSS conflict
- ❌ `bottom: "auto"` or `right: "auto"` → Positioning not applied

---

### 3. Positioning Validation

**Desktop (≥640px width):**

**Check with DevTools Elements tab:**
1. Inspect `#ai-chat-panel` element
2. Look for inline styles:
   ```css
   style="bottom: 88px; right: 24px; height: min(500px, calc(100vh - 140px)); max-height: calc(100vh - 140px); visibility: hidden;"
   ```
3. When open, check computed styles:
   - `position: fixed` ✅
   - `bottom: 88px` ✅
   - `right: 24px` ✅
   - `visibility: visible` (when `.chat-open` class is present) ✅

**Mobile (<640px width):**

**Check with DevTools mobile emulation:**
1. Open DevTools → Toggle device toolbar (Cmd+Shift+M)
2. Select iPhone or Android device
3. Click toggle button
4. Verify panel appears as **full-width bottom sheet**:
   - `bottom: 0` ✅
   - `left: 0` ✅
   - `right: 0` ✅
   - `width: 100%` ✅
   - `height: 80vh` ✅

---

### 4. Animation Verification

**Test smooth transitions:**

1. **Open animation:**
   - Panel fades in (opacity 0 → 1) over 300ms
   - Panel scales up (95% → 100%) over 300ms
   - Transform origin: bottom-right (panel grows from button corner)

2. **Close animation:**
   - Reverses smoothly
   - Button icon changes back to comments icon

**Check with DevTools Performance:**
1. Start recording (Cmd+E)
2. Click toggle button
3. Stop recording after animation
4. Check FPS: Should be 60fps with no dropped frames

---

### 5. Common Issues & Fixes

#### Issue 1: Panel is invisible (opacity issue)

**Symptom:** Button works, but panel never appears

**Debug:**
```javascript
const panel = document.getElementById('ai-chat-panel');
console.log('Opacity:', getComputedStyle(panel).opacity);
console.log('Visibility:', getComputedStyle(panel).visibility);
console.log('Has chat-open class:', panel.classList.contains('chat-open'));
```

**Fix:**
```javascript
// Force panel visibility (temporary):
panel.style.opacity = '1';
panel.style.visibility = 'visible';
panel.classList.add('chat-open');
```

#### Issue 2: Panel is off-screen (positioning issue)

**Symptom:** Panel exists but is outside viewport

**Debug:**
```javascript
const panel = document.getElementById('ai-chat-panel');
const rect = panel.getBoundingClientRect();
console.log('Panel top:', rect.top, '(should be > 0)');
console.log('Panel bottom:', rect.bottom, '(should be < viewport height)');
console.log('Viewport height:', window.innerHeight);
```

**Fix:**
```javascript
// Manual positioning override (temporary):
panel.style.bottom = '88px';
panel.style.right = '24px';
panel.style.position = 'fixed';
```

#### Issue 3: Transform scaling issue

**Symptom:** Panel appears but is tiny or scaled incorrectly

**Debug:**
```javascript
const panel = document.getElementById('ai-chat-panel');
console.log('Transform:', getComputedStyle(panel).transform);
// Should be: "matrix(1, 0, 0, 1, 0, 0)" when open (scale 1)
// Should be: "matrix(0.95, 0, 0, 0.95, ...)" when closed (scale 0.95)
```

**Fix:**
```javascript
// Force scale to 1 (temporary):
panel.style.transform = 'scale(1)';
```

#### Issue 4: Z-index conflict

**Symptom:** Panel appears behind other elements (calendar, modals)

**Debug:**
```javascript
const panel = document.getElementById('ai-chat-panel');
console.log('Z-index:', getComputedStyle(panel).zIndex);
// Should be: "9999"
```

**Fix:**
```javascript
// Increase z-index (temporary):
panel.style.zIndex = '99999';
```

---

### 6. Automated Test Script

**Copy-paste this into console for instant diagnosis:**

```javascript
(function testAIChatPanel() {
    console.log('🧪 AI Chat Panel Test Suite');
    console.log('================================\n');

    const widget = document.getElementById('ai-chat-widget');
    const panel = document.getElementById('ai-chat-panel');
    const button = document.getElementById('ai-chat-toggle-btn');

    // Test 1: Elements exist
    console.log('✅ Test 1: Element Existence');
    console.log('Widget exists:', !!widget);
    console.log('Panel exists:', !!panel);
    console.log('Button exists:', !!button);
    console.log('');

    // Test 2: Initial positioning
    console.log('✅ Test 2: Panel Positioning (Closed State)');
    const closedRect = panel.getBoundingClientRect();
    const closedStyle = getComputedStyle(panel);
    console.log('Position:', closedStyle.position);
    console.log('Bottom:', closedStyle.bottom);
    console.log('Right:', closedStyle.right);
    console.log('Opacity:', closedStyle.opacity);
    console.log('Visibility:', closedStyle.visibility);
    console.log('');

    // Test 3: Toggle function exists
    console.log('✅ Test 3: Toggle Function');
    console.log('toggleAIChat exists:', typeof window.toggleAIChat === 'function');
    console.log('');

    // Test 4: Open panel and check
    console.log('✅ Test 4: Opening Panel...');
    window.toggleAIChat();

    setTimeout(() => {
        const openRect = panel.getBoundingClientRect();
        const openStyle = getComputedStyle(panel);

        console.log('Panel opened:', panel.classList.contains('chat-open'));
        console.log('Opacity:', openStyle.opacity, '(should be 1)');
        console.log('Visibility:', openStyle.visibility, '(should be visible)');
        console.log('Transform:', openStyle.transform);
        console.log('');

        console.log('✅ Test 5: Viewport Visibility');
        const inViewportY = openRect.top >= 0 && openRect.bottom <= window.innerHeight;
        const inViewportX = openRect.left >= 0 && openRect.right <= window.innerWidth;
        console.log('In viewport (vertical):', inViewportY);
        console.log('In viewport (horizontal):', inViewportX);
        console.log('Panel rect:', {
            top: Math.round(openRect.top),
            bottom: Math.round(openRect.bottom),
            left: Math.round(openRect.left),
            right: Math.round(openRect.right),
            width: Math.round(openRect.width),
            height: Math.round(openRect.height)
        });
        console.log('');

        console.log('✅ Test 6: Accessibility');
        console.log('ARIA hidden:', panel.getAttribute('aria-hidden'), '(should be "false" when open)');
        console.log('Button aria-expanded:', button.getAttribute('aria-expanded'));
        console.log('Panel role:', panel.getAttribute('role'));
        console.log('');

        // Test 7: Close panel
        console.log('✅ Test 7: Closing Panel...');
        window.toggleAIChat();

        setTimeout(() => {
            const closedAgainRect = panel.getBoundingClientRect();
            const closedAgainStyle = getComputedStyle(panel);

            console.log('Panel closed:', !panel.classList.contains('chat-open'));
            console.log('Opacity:', closedAgainStyle.opacity, '(should be 0)');
            console.log('Visibility:', closedAgainStyle.visibility, '(should be hidden)');
            console.log('');

            // Final summary
            console.log('================================');
            console.log('📊 Test Summary');
            console.log('================================');

            const allTestsPassed =
                !!widget && !!panel && !!button && // Elements exist
                closedStyle.position === 'fixed' && // Fixed positioning
                openStyle.opacity === '1' && // Opens to opacity 1
                openStyle.visibility === 'visible' && // Becomes visible
                inViewportY && inViewportX && // In viewport
                closedAgainStyle.opacity === '0'; // Closes to opacity 0

            if (allTestsPassed) {
                console.log('✅ ALL TESTS PASSED');
                console.log('AI Chat Panel is working correctly!');
            } else {
                console.log('❌ SOME TESTS FAILED');
                console.log('Review the output above for details.');
                console.log('Run window.debugAIChat() for more info.');
            }
        }, 350);
    }, 350);
})();
```

**Expected Output:**
```
🧪 AI Chat Panel Test Suite
================================

✅ Test 1: Element Existence
Widget exists: true
Panel exists: true
Button exists: true

✅ Test 2: Panel Positioning (Closed State)
Position: fixed
Bottom: 88px
Right: 24px
Opacity: 0
Visibility: hidden

✅ Test 3: Toggle Function
toggleAIChat exists: true

✅ Test 4: Opening Panel...
Panel opened: true
Opacity: 1 (should be 1)
Visibility: visible (should be visible)
Transform: matrix(1, 0, 0, 1, 0, 0)

✅ Test 5: Viewport Visibility
In viewport (vertical): true
In viewport (horizontal): true
Panel rect: {
    top: 312,
    bottom: 812,
    left: 1512,
    right: 1896,
    width: 384,
    height: 500
}

✅ Test 6: Accessibility
ARIA hidden: false (should be "false" when open)
Button aria-expanded: true
Panel role: dialog

✅ Test 7: Closing Panel...
Panel closed: true
Opacity: 0 (should be 0)
Visibility: hidden (should be hidden)

================================
📊 Test Summary
================================
✅ ALL TESTS PASSED
AI Chat Panel is working correctly!
```

---

### 7. Mobile Testing

**Test on actual mobile devices:**

**iOS Safari:**
1. Open OBCMS on iPhone
2. Tap AI chat button (bottom-right)
3. Verify full-width bottom sheet appears
4. Tap backdrop to close
5. Check for smooth slide-up/down animation

**Android Chrome:**
1. Repeat above steps
2. Check for any rendering issues
3. Verify touch targets are at least 44px

**Responsive Testing (DevTools):**
1. Open DevTools → Device Toolbar (Cmd+Shift+M)
2. Test these viewports:
   - iPhone SE (375px) - Small mobile
   - iPhone 14 Pro (393px) - Standard mobile
   - iPad (768px) - Tablet portrait
   - iPad Pro (1024px) - Tablet landscape
   - Desktop (1920px) - Large desktop

---

### 8. Accessibility Testing

**Keyboard Navigation:**
1. Tab to AI chat button
2. Press Enter or Space → Panel opens
3. Tab again → Focus moves to close button in panel
4. Press Escape → Panel closes
5. Focus returns to toggle button

**Screen Reader Testing:**
1. Enable VoiceOver (Mac) or NVDA (Windows)
2. Navigate to AI chat button
3. Activate button → Hear "AI chat opened"
4. Navigate panel content
5. Close panel → Hear "AI chat closed"

**ARIA Attributes:**
- `role="dialog"` on panel
- `aria-labelledby="ai-chat-title"` points to header
- `aria-hidden="true/false"` toggles correctly
- `aria-expanded="true/false"` on button

---

## ✅ Success Criteria

**The fix is successful if:**

- [ ] Panel is visible when toggle button is clicked (desktop)
- [ ] Panel positioned correctly above button (88px bottom, 24px right)
- [ ] Panel appears as full-width bottom sheet on mobile
- [ ] Animations are smooth (60fps, 300ms duration)
- [ ] Toggle button icon changes (comments ↔ X)
- [ ] Escape key closes panel
- [ ] Focus management works (to close button, back to toggle)
- [ ] Screen reader announces state changes
- [ ] Debug mode shows colored borders (red → green when open)
- [ ] All automated tests pass (run script from Section 6)

---

## 🐛 If Tests Fail

**Run these commands to gather debug info:**

```javascript
// Quick diagnosis:
window.debugAIChat();

// Enable visual debug mode:
window.enableAIChatDebug();

// Force panel visible (emergency override):
const panel = document.getElementById('ai-chat-panel');
panel.style.opacity = '1';
panel.style.visibility = 'visible';
panel.style.position = 'fixed';
panel.style.bottom = '88px';
panel.style.right = '24px';
panel.style.zIndex = '99999';
panel.classList.add('chat-open');
```

**Then report these details:**
1. Browser & version
2. Viewport size (width x height)
3. Console output from `window.debugAIChat()`
4. Screenshot of DevTools Elements tab showing `#ai-chat-panel`
5. Screenshot of DevTools Computed styles for panel

---

**Last Updated:** 2025-10-06
**Testing Status:** READY FOR VERIFICATION
