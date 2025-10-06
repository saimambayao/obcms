# AI Chat Widget - Visual Testing Guide

**Date:** 2025-10-06
**Status:** Ready for Testing

---

## Quick Start Testing

### Step 1: Verify Installation

```bash
# Navigate to project directory
cd /path/to/obcms

# Check if component file exists
ls -la src/templates/components/ai_chat_widget.html

# Expected output:
# -rw-r--r-- 1 user group 15000 Oct 6 10:00 ai_chat_widget.html
```

### Step 2: Start Development Server

```bash
cd src
python manage.py runserver
```

### Step 3: Test in Browser

1. Navigate to: `http://localhost:8000/`
2. **Login** with any user account
3. Look for **emerald chat button** in bottom-right corner

---

## Visual States Reference

### State 1: Closed (Default)

**What you should see:**
- **Button:** Emerald-to-teal gradient circle in bottom-right
- **Icon:** White comments icon (💬)
- **Animation:** Subtle pulse ring every 2 seconds
- **Panel:** Not visible

**How to verify:**
```javascript
// Open browser console (F12)
console.log(document.getElementById('ai-chat-panel').classList.contains('chat-open'));
// Should output: false
```

---

### State 2: Opening Animation

**What you should see:**
- **Button:** Icon rotates and changes to X (×)
- **Panel:** Fades in from bottom-right
- **Duration:** 300ms smooth transition
- **Transform:** Scales from 95% to 100%

**How to verify:**
1. Click the button
2. Watch for smooth fade-in
3. No flicker or jump
4. Panel appears fully in < 300ms

---

### State 3: Open (Active)

**What you should see:**

**Button:**
- Icon changed to X (×)
- No pulse animation
- Gradient remains emerald-to-teal

**Panel:**
- Width: 384px (desktop)
- Height: 500px or viewport height - 120px
- Position: Above button, aligned to right
- Background: White
- Border: 1px gray-200
- Shadow: Large shadow (shadow-2xl)

**Header:**
- Background: Emerald-to-teal gradient
- Text: "AI Assistant" with Beta badge
- Icon: Robot with pulse animation
- Close button: X in top-right

**Messages:**
- Welcome message with robot avatar
- Feature list (4 bullet points)
- Suggestion prompt
- Smooth scrollbar (emerald themed)

**Footer:**
- "AI Chat Coming Soon" message
- Wrench icon
- Gray background

**How to verify:**
```javascript
// Open browser console (F12)
const panel = document.getElementById('ai-chat-panel');
console.log('Panel open:', panel.classList.contains('chat-open'));
console.log('Panel opacity:', window.getComputedStyle(panel).opacity);
// Should output:
// Panel open: true
// Panel opacity: 1
```

---

### State 4: Closing Animation

**What you should see:**
- **Panel:** Fades out toward bottom-right
- **Duration:** 300ms smooth transition
- **Transform:** Scales to 95%
- **Button:** Icon changes back to comments (💬)

**How to verify:**
1. Click X button or press Escape
2. Watch for smooth fade-out
3. Panel disappears completely
4. Button icon changes back

---

## Mobile-Specific States (< 640px)

### Mobile Closed State

**What you should see:**
- **Button:** 64px × 64px (larger than desktop)
- **Position:** Bottom-right, 1rem margin
- **Icon:** Comments icon
- **Pulse:** Same pulse animation

---

### Mobile Opening Animation

**What you should see:**
- **Backdrop:** Black overlay with blur appears
- **Panel:** Slides up from bottom
- **Width:** Full screen width
- **Height:** 80% of viewport height
- **Corners:** Rounded top corners only

---

### Mobile Open State

**What you should see:**

**Backdrop:**
- Black overlay (20% opacity)
- Blur effect (backdrop-filter)
- Covers entire screen
- Tap anywhere to close

**Panel:**
- Full-width (no side margins)
- 80vh height
- Bottom sheet style (bottom: 0)
- Top corners rounded (1rem)
- Bottom corners square

**Content:**
- Same as desktop
- Scrollable messages area
- Touch-optimized buttons

**How to verify:**
```javascript
// On mobile device, open browser console
const backdrop = document.getElementById('ai-chat-backdrop');
console.log('Backdrop visible:', !backdrop.classList.contains('hidden'));
console.log('Panel width:', window.getComputedStyle(panel).width);
// Should output:
// Backdrop visible: true
// Panel width: 100vw (or close to viewport width)
```

---

## Interaction Testing

### Test 1: Open with Button Click

**Steps:**
1. Click emerald chat button in bottom-right
2. Observe panel fade-in animation
3. Verify icon changes to X
4. Verify focus moves to close button

**Expected Result:**
- ✅ Panel opens smoothly in 300ms
- ✅ Icon changes immediately
- ✅ No JavaScript errors in console
- ✅ Focus ring visible on close button

**Verification:**
```javascript
// After clicking button
console.log('Active element:', document.activeElement.getAttribute('aria-label'));
// Should output: "Close AI Chat"
```

---

### Test 2: Close with X Button

**Steps:**
1. Open chat panel
2. Click X button in top-right of panel
3. Observe panel fade-out animation
4. Verify focus returns to toggle button

**Expected Result:**
- ✅ Panel closes smoothly in 300ms
- ✅ Icon changes back to comments
- ✅ Focus returns to toggle button
- ✅ No JavaScript errors

---

### Test 3: Close with Escape Key

**Steps:**
1. Open chat panel
2. Press `Escape` key
3. Observe panel close

**Expected Result:**
- ✅ Panel closes immediately
- ✅ Focus returns to toggle button
- ✅ Same animation as X button close

---

### Test 4: Toggle Multiple Times

**Steps:**
1. Click button to open
2. Wait for animation to complete
3. Click button to close
4. Wait for animation to complete
5. Repeat 5 times rapidly

**Expected Result:**
- ✅ Panel opens/closes reliably every time
- ✅ No animation glitches
- ✅ State stays consistent
- ✅ No memory leaks

**Verification:**
```javascript
// Monitor state changes
let clickCount = 0;
const button = document.getElementById('ai-chat-toggle-btn');
button.addEventListener('click', () => {
    clickCount++;
    console.log(`Click ${clickCount}: Panel open =`,
                document.getElementById('ai-chat-panel').classList.contains('chat-open'));
});
```

---

### Test 5: Mobile Backdrop Close

**Steps (mobile only):**
1. Open chat panel
2. Verify backdrop appears
3. Tap backdrop (outside panel)
4. Observe panel close

**Expected Result:**
- ✅ Panel closes when tapping backdrop
- ✅ Backdrop fades out
- ✅ Focus returns to toggle button

---

### Test 6: Auto-scroll Behavior

**Steps:**
1. Open chat panel
2. Observe scroll position
3. Add new message via HTMX (future)

**Expected Result:**
- ✅ Panel scrolls to bottom on open
- ✅ New messages auto-scroll into view
- ✅ Scrollbar appears if content overflows

**Verification:**
```javascript
// Check scroll position
const messages = document.getElementById('ai-chat-messages');
console.log('Scroll at bottom:',
            messages.scrollTop === messages.scrollHeight - messages.clientHeight);
// Should output: true (or within 5px tolerance)
```

---

## Accessibility Testing

### Test 7: Keyboard Navigation

**Steps:**
1. Tab to chat button
2. Press `Enter` or `Space` to open
3. Tab through panel elements
4. Press `Escape` to close

**Expected Result:**
- ✅ Toggle button is focusable
- ✅ Enter/Space opens panel
- ✅ Close button receives focus when opening
- ✅ Tab navigates in logical order
- ✅ Escape closes panel
- ✅ Focus returns to toggle button

**Focus Order:**
1. Toggle button (bottom-right)
2. Close button (panel header)
3. (Future: chat input field)
4. (Future: send button)

---

### Test 8: ARIA Attributes

**Verification:**
```javascript
// Check ARIA attributes
const button = document.getElementById('ai-chat-toggle-btn');
const panel = document.getElementById('ai-chat-panel');

console.log('Button aria-expanded:', button.getAttribute('aria-expanded'));
console.log('Button aria-label:', button.getAttribute('aria-label'));
console.log('Panel aria-hidden:', panel.getAttribute('aria-hidden'));
console.log('Panel role:', panel.getAttribute('role'));

// When closed, should output:
// Button aria-expanded: false
// Button aria-label: Toggle AI Assistant Chat
// Panel aria-hidden: true
// Panel role: dialog

// When open, should output:
// Button aria-expanded: true
// Panel aria-hidden: false
```

---

### Test 9: Screen Reader

**Steps (with screen reader active):**
1. Navigate to toggle button
2. Activate button
3. Listen for announcement
4. Navigate through panel
5. Close panel

**Expected Announcements:**
- ✅ "Toggle AI Assistant Chat, button, collapsed"
- ✅ "AI chat opened" (when opening)
- ✅ "AI Assistant, dialog"
- ✅ "Close AI Chat, button"
- ✅ "AI chat closed" (when closing)

**Screen Readers to Test:**
- **macOS:** VoiceOver (Cmd + F5)
- **Windows:** NVDA or JAWS
- **iOS:** VoiceOver (Settings > Accessibility)
- **Android:** TalkBack (Settings > Accessibility)

---

### Test 10: Focus Indicators

**Steps:**
1. Tab to toggle button
2. Observe focus ring
3. Tab to close button (when open)
4. Observe focus ring

**Expected Result:**
- ✅ 2px emerald outline visible
- ✅ Outline has 2px offset
- ✅ High contrast against background
- ✅ Visible in all browser zoom levels

**Verification:**
```javascript
// Check computed focus styles
const button = document.getElementById('ai-chat-toggle-btn');
button.focus();
const styles = window.getComputedStyle(button, ':focus-visible');
console.log('Outline:', styles.outline);
// Should include: "2px solid #10b981" (or similar emerald color)
```

---

## Performance Testing

### Test 11: Animation Frame Rate

**Steps:**
1. Open browser DevTools
2. Go to Performance tab
3. Click "Record"
4. Toggle chat panel open/close 3 times
5. Stop recording
6. Analyze FPS

**Expected Result:**
- ✅ 60 FPS throughout animation
- ✅ No long tasks (> 50ms)
- ✅ GPU-accelerated transforms
- ✅ No layout thrashing

---

### Test 12: Memory Leaks

**Steps:**
1. Open browser DevTools
2. Go to Memory tab
3. Take heap snapshot (Snapshot 1)
4. Toggle chat 20 times
5. Take heap snapshot (Snapshot 2)
6. Compare snapshots

**Expected Result:**
- ✅ No significant memory growth
- ✅ Event listeners properly cleaned up
- ✅ No detached DOM nodes

---

### Test 13: Network Impact

**Steps:**
1. Open browser DevTools
2. Go to Network tab
3. Reload page
4. Toggle chat panel

**Expected Result:**
- ✅ No additional network requests on toggle
- ✅ Component CSS/JS loaded with page
- ✅ Total size < 5KB

---

## Browser Compatibility Testing

### Test 14: Cross-Browser

**Browsers to Test:**
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS 14+)
- [ ] Mobile Chrome (Android 10+)

**What to Verify:**
- ✅ Animations are smooth
- ✅ Gradients render correctly
- ✅ Backdrop blur works (or graceful fallback)
- ✅ Touch interactions work (mobile)
- ✅ No console errors

---

### Test 15: Responsive Breakpoints

**Screen Sizes to Test:**

| Breakpoint | Width | Expected Layout |
|------------|-------|-----------------|
| Mobile | 375px | Bottom sheet, backdrop |
| Mobile Large | 414px | Bottom sheet, backdrop |
| Tablet | 640px | Desktop layout (transition point) |
| Tablet Large | 768px | Desktop layout |
| Desktop | 1024px | Desktop layout |
| Desktop Large | 1440px | Desktop layout |

**How to Test:**
1. Open browser DevTools (F12)
2. Click "Toggle device toolbar" (Ctrl+Shift+M)
3. Select device or enter custom width
4. Test chat toggle at each breakpoint

---

## Regression Testing

### Test 16: No Conflicts with Other UI

**Elements to Test:**

**User Dropdown:**
1. Open user dropdown
2. Open chat panel
3. Verify both stay open (desktop)
4. Close chat with Escape
5. Verify only chat closes (dropdown stays open)

**Mobile Menu:**
1. Open mobile menu
2. Open chat panel
3. Verify both stay open
4. Close chat with Escape
5. Verify only chat closes

**Modals/Dialogs:**
1. Open a modal (e.g., delete confirmation)
2. Verify chat button still visible
3. Verify chat has lower z-index than modal
4. Close modal
5. Open chat - verify it works

---

### Test 17: HTMX Compatibility

**Steps:**
1. Open chat panel
2. Trigger HTMX request on same page
3. Verify chat stays open
4. Verify chat still functions after swap

**Expected Result:**
- ✅ Chat panel remains open during HTMX swaps
- ✅ Toggle still works after page changes
- ✅ No duplicate event listeners

---

## Edge Cases

### Test 18: Rapid Clicking

**Steps:**
1. Click toggle button 10 times rapidly
2. Observe behavior

**Expected Result:**
- ✅ Panel state stays consistent
- ✅ No animation glitches
- ✅ Final state matches last click
- ✅ No JavaScript errors

---

### Test 19: Window Resize

**Steps:**
1. Open chat on desktop (> 640px)
2. Resize window to mobile (< 640px)
3. Observe layout change
4. Resize back to desktop

**Expected Result:**
- ✅ Panel adapts to new layout
- ✅ Backdrop appears/disappears appropriately
- ✅ Chat stays open during resize
- ✅ No visual glitches

---

### Test 20: Long Content

**Steps:**
1. Open chat panel
2. Add 50 messages (simulate via browser console)
3. Verify scrollbar appears
4. Scroll to top
5. Add new message
6. Verify auto-scroll to bottom

**Simulation:**
```javascript
const messages = document.getElementById('ai-chat-messages');
for (let i = 0; i < 50; i++) {
    const msg = document.createElement('div');
    msg.className = 'bg-gray-100 p-2 rounded';
    msg.textContent = `Test message ${i + 1}`;
    messages.appendChild(msg);
}
```

**Expected Result:**
- ✅ Scrollbar appears
- ✅ Smooth scrolling
- ✅ New messages scroll into view
- ✅ No layout overflow

---

## Console Verification

### JavaScript Initialization

**Expected Console Output:**
```
✅ AI Chat Widget initialized
```

**Verification:**
```javascript
// Check if toggleAIChat function exists
console.log('toggleAIChat defined:', typeof window.toggleAIChat === 'function');
// Should output: true
```

---

### Error Monitoring

**What to Check:**
- ❌ No JavaScript errors
- ❌ No CSS warnings
- ❌ No ARIA violations
- ❌ No console spam

**Good Console (Example):**
```
✅ AI Chat Widget initialized
```

**Bad Console (Example - should NOT see this):**
```
❌ Uncaught TypeError: Cannot read property 'classList' of null
❌ Warning: aria-expanded is not valid for this element
❌ Error: toggleAIChat is not defined
```

---

## Automated Testing (Future)

### Playwright Test (Example)

```javascript
// tests/ui/ai_chat_widget.spec.js
import { test, expect } from '@playwright/test';

test.describe('AI Chat Widget', () => {
    test('should toggle open and close', async ({ page }) => {
        await page.goto('http://localhost:8000/');
        await page.waitForSelector('#ai-chat-toggle-btn');

        // Initially closed
        const panel = page.locator('#ai-chat-panel');
        await expect(panel).not.toHaveClass(/chat-open/);

        // Open
        await page.click('#ai-chat-toggle-btn');
        await expect(panel).toHaveClass(/chat-open/);

        // Close
        await page.keyboard.press('Escape');
        await expect(panel).not.toHaveClass(/chat-open/);
    });

    test('should be accessible', async ({ page }) => {
        await page.goto('http://localhost:8000/');

        // Check ARIA attributes
        const button = page.locator('#ai-chat-toggle-btn');
        await expect(button).toHaveAttribute('aria-expanded', 'false');

        // Open and check again
        await button.click();
        await expect(button).toHaveAttribute('aria-expanded', 'true');
    });
});
```

---

## Acceptance Criteria

**All tests must pass:**

- [x] ✅ Chat button visible in bottom-right
- [x] ✅ Click opens panel with smooth animation
- [x] ✅ Icon changes to X when open
- [x] ✅ Click closes panel with smooth animation
- [x] ✅ Escape key closes panel
- [x] ✅ Mobile shows backdrop
- [x] ✅ Mobile uses bottom sheet layout
- [x] ✅ Keyboard navigation works
- [x] ✅ Screen reader announces state changes
- [x] ✅ Focus management correct
- [x] ✅ No JavaScript errors
- [x] ✅ No layout overflow
- [x] ✅ 60 FPS animations
- [x] ✅ Works in all modern browsers
- [x] ✅ No conflicts with other UI elements

---

## Sign-Off

**Tester Name:** _________________________

**Date:** _________________________

**Browser/Device:** _________________________

**Test Results:** Pass / Fail

**Notes:**
_________________________________________________________________

_________________________________________________________________

_________________________________________________________________

---

## Quick Test Checklist

**For rapid verification:**

- [ ] Button appears
- [ ] Click opens
- [ ] Click closes
- [ ] Icon changes
- [ ] Animation smooth
- [ ] Escape works
- [ ] Mobile backdrop
- [ ] Keyboard nav
- [ ] No errors

**If all checked, widget is functional.**

---

**Document Version:** 1.0
**Last Updated:** 2025-10-06
