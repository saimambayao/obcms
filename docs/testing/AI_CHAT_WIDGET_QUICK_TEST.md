# AI Chat Widget - Quick Testing Guide

**File:** `/src/templates/components/ai_chat_widget.html`
**Test Duration:** 5 minutes
**Last Updated:** 2025-10-06

## Quick Visual Test (30 seconds)

1. **Load any OBCMS page**
   - Dashboard, Community List, etc.

2. **Look for floating chat button**
   - ✅ Should see emerald circular button in bottom-right corner
   - ✅ Button should have subtle pulse animation

3. **Click the chat button**
   - ✅ Panel should appear instantly above the button
   - ✅ Panel should be fully visible (white card with green header)
   - ✅ Should see "AI Assistant" with Beta badge

4. **Click the X button or chat button again**
   - ✅ Panel should close smoothly
   - ✅ Button icon should switch back to comments icon

**If panel doesn't appear:** Continue to debug section below.

## Debug Mode Test (2 minutes)

### Enable Debug Mode

Open browser console (F12) and run:

```javascript
window.enableAIChatDebug()
```

**Expected:**
- ✅ Console message: "Debug mode enabled - panel will show with colored borders"
- ✅ Panel should now show with **RED BORDER** (closed state)
- ✅ Panel should be visible even when closed (yellow background)

### Test Panel Toggle

Click chat button:
- ✅ Border should turn **GREEN** (open state)
- ✅ Background should turn white
- ✅ Content should be readable

Click chat button again:
- ✅ Border should turn **RED** again (closed state)

### Get Detailed Debug Info

```javascript
window.debugAIChat()
```

**Expected Console Output:**
```
=== AI Chat Debug Info ===
Chat open: false/true
Panel classes: "ai-chat-panel ... [chat-open]"
Panel position: {
    top: <number>,
    bottom: <number>,
    left: <number>,
    right: <number>,
    height: <number>,
    width: <number>
}
Computed styles: {
    position: "fixed",
    bottom: "88px",
    right: "24px",
    visibility: "visible" or "hidden",
    ...
}
Visibility check: {
    inViewportVertically: true,   ← Must be TRUE when open
    inViewportHorizontally: true, ← Must be TRUE when open
    hasOpenClass: true/false,
    ariaHidden: "true" or "false"
}
```

### Disable Debug Mode

```javascript
window.disableAIChatDebug()
```

## Mobile Test (1 minute)

### Resize Browser to Mobile Width

1. **Open DevTools** (F12)
2. **Enable device toolbar** (Ctrl+Shift+M or Cmd+Shift+M)
3. **Select iPhone or Android device**

### Test Mobile Bottom Sheet

Click chat button:
- ✅ Panel should slide up from bottom (full width)
- ✅ Should cover ~80% of screen height
- ✅ Dark backdrop should appear behind panel
- ✅ Rounded top corners only

Click backdrop:
- ✅ Panel should close
- ✅ Backdrop should fade out

## Common Issues & Fixes

### Issue 1: Panel Not Visible When Open

**Symptoms:**
- Button icon changes to X
- Console shows "Chat open: true"
- But no panel visible

**Fix:**
```javascript
// Run in console:
window.debugAIChat()

// Look for:
// - visibility: "hidden" while chat is open ← Problem
// - inViewportVertically: false ← Panel off-screen

// Force visibility:
document.getElementById('ai-chat-panel').style.visibility = 'visible'
```

### Issue 2: Panel Outside Viewport

**Symptoms:**
- Console shows: "Panel outside viewport vertically"
- `rect.bottom > window.innerHeight`

**Fix:**
- This should auto-fix with `validatePanelPosition()`
- If not, check console for warning messages
- Panel height should auto-adjust

### Issue 3: Debug Mode Not Working

**Symptoms:**
- `window.enableAIChatDebug()` does nothing

**Fix:**
```javascript
// Manually add debug class:
document.getElementById('ai-chat-widget').classList.add('debug-chat')

// Verify:
document.getElementById('ai-chat-widget').classList.contains('debug-chat')
// Should return: true
```

### Issue 4: Panel Overlaps Other Elements

**Symptoms:**
- Panel appears behind navbar or modals

**Fix:**
```javascript
// Check z-index:
getComputedStyle(document.getElementById('ai-chat-panel')).zIndex
// Should be: "9999"

// If lower, force higher:
document.getElementById('ai-chat-panel').style.zIndex = '10000'
```

## Viewport Size Test Matrix

| Viewport Size | Expected Panel Size | Position | Status |
|--------------|---------------------|----------|---------|
| 1920x1080 (Full HD) | 384x488px | bottom: 88px, right: 24px | ✅ Tested |
| 1366x768 (Laptop) | 384x488px | bottom: 88px, right: 24px | ✅ Tested |
| 1024x768 (Tablet) | 384x488px | bottom: 88px, right: 24px | ✅ Tested |
| 768x1024 (Tablet Portrait) | 384x884px | bottom: 88px, right: 24px | ✅ Tested |
| 375x667 (iPhone) | 100%x80vh | bottom: 0, full width | ✅ Tested |
| 360x640 (Android) | 100%x80vh | bottom: 0, full width | ✅ Tested |

## Console Commands Reference

### Essential Commands

```javascript
// Enable visual debugging
window.enableAIChatDebug()

// Get detailed position info
window.debugAIChat()

// Disable visual debugging
window.disableAIChatDebug()

// Force open chat (bypass button)
window.toggleAIChat()
```

### Advanced Inspection

```javascript
// Get panel element
const panel = document.getElementById('ai-chat-panel')

// Check current position
panel.getBoundingClientRect()

// Check computed styles
getComputedStyle(panel)

// Check all classes
panel.className

// Check if chat is open
panel.classList.contains('chat-open')

// Check visibility
getComputedStyle(panel).visibility

// Check opacity
getComputedStyle(panel).opacity
```

## Expected Console Logs (Normal Operation)

### On Page Load
```
✅ AI Chat Widget initialized (fixed positioning)
Initial panel state: {
    width: 384,
    height: 500,
    computedPosition: "fixed",
    computedBottom: "88px",
    computedRight: "24px",
    computedVisibility: "hidden",
    computedOpacity: "0"
}
```

### On Chat Open
```
AI Chat Panel Position: {
    top: 200-500,
    bottom: 500-900,
    left: 1400-1800,
    right: 1800-2200,
    height: 400-500,
    width: 384,
    viewportHeight: 1080,
    viewportWidth: 1920,
    isVisible: true,    ← Must be TRUE
    isOpen: true        ← Must be TRUE
}
```

### On Resize (if open)
```
AI Chat Panel Position: { ... }
```

### No Error Messages Expected
If you see:
- ❌ "Panel outside viewport" - Auto-adjusts, expected on extreme viewports
- ❌ "Panel too wide" - Auto-adjusts, expected on narrow screens
- ❌ "Forcing visibility" - Safeguard triggered, panel should still work

## Pass/Fail Criteria

### PASS Criteria ✅

1. Panel appears instantly on button click
2. Panel is fully visible (no cutoff)
3. Panel closes smoothly
4. Mobile bottom sheet works
5. Debug mode shows panel with colored borders
6. Console logs show `isVisible: true` when open
7. No JavaScript errors in console
8. Accessibility (Esc key closes, focus management works)

### FAIL Criteria ❌

1. Panel never appears when button clicked
2. Panel appears off-screen (invisible)
3. JavaScript errors in console
4. Panel doesn't close
5. Mobile bottom sheet doesn't work
6. Debug mode doesn't show panel

## Reporting Issues

If tests fail, capture:

1. **Screenshot** of the issue
2. **Console output** (`window.debugAIChat()`)
3. **Browser & version** (Chrome 120, Firefox 121, etc.)
4. **Viewport size** (from DevTools or `window.innerWidth` x `window.innerHeight`)
5. **Steps to reproduce**

## Quick Fix Summary

| Problem | Quick Fix Command |
|---------|------------------|
| Panel invisible | `document.getElementById('ai-chat-panel').style.visibility = 'visible'` |
| Panel off-screen | Resize browser, panel auto-adjusts |
| Debug not working | `document.getElementById('ai-chat-widget').classList.add('debug-chat')` |
| Z-index issue | `document.getElementById('ai-chat-panel').style.zIndex = '10000'` |
| Chat won't open | `window.toggleAIChat()` in console |

## Test Complete

If all quick tests pass:
- ✅ **AI Chat Widget is working correctly**
- ✅ **Positioning fix is successful**
- ✅ **Production-ready**

Time to complete: **5 minutes**
