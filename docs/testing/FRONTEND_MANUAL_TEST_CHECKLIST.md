# AI Chat Widget - Manual Testing Checklist

**Purpose:** Step-by-step manual testing guide for QA engineers and developers
**Component:** AI Chat Widget (HTMX Integration)
**Location:** `/src/templates/components/ai_chat_widget.html`

---

## Prerequisites

- [ ] Local development server running (`cd src && ./manage.py runserver`)
- [ ] Logged in as an authenticated user
- [ ] Browser DevTools open (Console + Network tabs)
- [ ] No JavaScript errors in console
- [ ] OBCMS loaded successfully

---

## Test Session Setup

### 1. Environment Verification

```bash
# Start development server
cd src
python manage.py runserver

# Open browser
open http://localhost:8000/

# Login with test credentials
# Navigate to any page with chat widget
```

### 2. Browser DevTools Setup

**Chrome/Edge/Firefox:**
- Press `F12` or `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)
- Open Console tab
- Open Network tab
- Filter Network by "XHR" or "Fetch"

**Console Commands to Run:**
```javascript
// Check if widget is loaded
console.log('Widget exists:', !!document.getElementById('ai-chat-widget'));

// Check initial state
debugAIChat();
```

---

## Category 1: Widget Visibility & Positioning

### Test 1.1: Widget Appears on Page Load

**Steps:**
1. Load any page in OBCMS
2. Look for chat button in bottom-right corner

**Expected:**
- [ ] Chat button visible at bottom-right
- [ ] Button has gradient blue-to-teal background
- [ ] Button shows comment icon (💬)
- [ ] Panel is hidden (not visible)

**Screenshot:** `test-1.1-initial-load.png`

---

### Test 1.2: Toggle Button Click Opens Panel

**Steps:**
1. Click chat toggle button

**Expected:**
- [ ] Panel appears smoothly (300ms animation)
- [ ] Panel positioned at `bottom: 100px, right: 24px`
- [ ] Panel is 400px wide, 500px tall (desktop)
- [ ] Icon changes from comment to X (✕)
- [ ] Button has ring around it (blue glow)

**Console Check:**
```javascript
debugAIChat();
// Should show: Chat open: true, hasOpenClass: true
```

**Screenshot:** `test-1.2-panel-open.png`

---

### Test 1.3: Panel Stays Within Viewport

**Steps:**
1. Open chat panel
2. Resize browser window to very small width/height
3. Check panel position

**Expected:**
- [ ] Panel adjusts to fit viewport
- [ ] Panel never goes off-screen
- [ ] Panel reduces height if needed
- [ ] Panel adjusts width if needed

**Console Check:**
```javascript
const panel = document.getElementById('ai-chat-panel');
const rect = panel.getBoundingClientRect();
console.log('Visible:', rect.top >= 0 && rect.bottom <= window.innerHeight);
```

**Screenshot:** `test-1.3-viewport-bounds.png`

---

### Test 1.4: Mobile Bottom Sheet (Mobile Only)

**Steps:**
1. Open browser DevTools
2. Enable device emulation (iPhone 14 Pro)
3. Reload page
4. Click chat toggle button

**Expected:**
- [ ] Panel appears as full-width bottom sheet
- [ ] Panel is 80vh tall
- [ ] Panel has rounded top corners only
- [ ] Backdrop appears behind panel
- [ ] Button is 56px x 56px (mobile size)

**Screenshot:** `test-1.4-mobile-bottom-sheet.png`

---

### Test 1.5: Close Panel

**Steps:**
1. Open chat panel
2. Click X button in panel header

**Expected:**
- [ ] Panel closes smoothly (200ms animation)
- [ ] Icon changes back to comment (💬)
- [ ] Button ring disappears
- [ ] Focus returns to toggle button

**Screenshot:** `test-1.5-panel-closed.png`

---

### Test 1.6: Escape Key Closes Panel

**Steps:**
1. Open chat panel
2. Press `Escape` key

**Expected:**
- [ ] Panel closes
- [ ] Focus returns to toggle button

---

### Test 1.7: Backdrop Click Closes (Mobile Only)

**Steps:**
1. Enable mobile emulation
2. Open chat panel
3. Click backdrop (dark area outside panel)

**Expected:**
- [ ] Panel closes
- [ ] Backdrop fades out

---

## Category 2: HTMX Form Submission

### Test 2.1: Form Has Correct HTMX Attributes

**Steps:**
1. Open chat panel
2. Right-click form, inspect element

**Expected:**
- [ ] `hx-post="/common/chat/message/"` attribute
- [ ] `hx-target="#ai-chat-messages"` attribute
- [ ] `hx-swap="beforeend scroll:bottom"` attribute
- [ ] `hx-indicator="#ai-chat-loading"` attribute
- [ ] CSRF token present

**Console Check:**
```javascript
const form = document.getElementById('ai-chat-form');
console.log('hx-post:', form.getAttribute('hx-post'));
console.log('hx-target:', form.getAttribute('hx-target'));
console.log('hx-swap:', form.getAttribute('hx-swap'));
```

---

### Test 2.2: Form Submit on Enter Key

**Steps:**
1. Open chat panel
2. Type "Hello" in input field
3. Press `Enter` key

**Expected:**
- [ ] Form submits via HTMX (no page reload)
- [ ] User message appears immediately
- [ ] Loading indicator shows
- [ ] AI response appears after processing
- [ ] Input field clears
- [ ] Input field refocuses

**Network Tab:**
- [ ] XHR request to `/common/chat/message/`
- [ ] POST method
- [ ] Form data includes `message=Hello`
- [ ] Response is HTML snippet

**Screenshot:** `test-2.2-enter-submit.png`

---

### Test 2.3: Form Submit on Button Click

**Steps:**
1. Open chat panel
2. Type "How many communities?" in input
3. Click send button (paper plane icon)

**Expected:**
- [ ] Same behavior as Enter key submit
- [ ] Form submits via HTMX
- [ ] No page reload

**Screenshot:** `test-2.3-button-submit.png`

---

### Test 2.4: Empty Message Validation

**Steps:**
1. Open chat panel
2. Leave input empty
3. Click send button

**Expected:**
- [ ] Form does NOT submit
- [ ] Submit button remains disabled (should be disabled when input is empty)
- [ ] No network request

---

### Test 2.5: CSRF Token Included

**Steps:**
1. Open chat panel
2. Type message
3. Submit form
4. Check Network tab request payload

**Expected:**
- [ ] `csrfmiddlewaretoken` in form data
- [ ] Token matches Django session token

**Network Tab Check:**
- Request Payload should include:
  ```
  csrfmiddlewaretoken: [token]
  message: [user message]
  ```

---

## Category 3: Optimistic UI Updates

### Test 3.1: User Message Appears Immediately

**Steps:**
1. Open chat panel
2. Type "Test message"
3. Submit form
4. Observe timing

**Expected:**
- [ ] User message appears BEFORE server response (<50ms)
- [ ] Message has blue gradient background
- [ ] Message is right-aligned
- [ ] Message shows "Just now" timestamp
- [ ] Message text is NOT HTML-escaped visually (but is safe from XSS)

**Screenshot:** `test-3.1-optimistic-user-message.png`

---

### Test 3.2: Loading Indicator Shows

**Steps:**
1. Submit a message
2. Observe loading overlay

**Expected:**
- [ ] Loading overlay appears immediately
- [ ] Spinner animation visible
- [ ] Loading text shows (e.g., "Thinking...")
- [ ] Submit button disabled during loading

**Screenshot:** `test-3.2-loading-indicator.png`

---

### Test 3.3: Chat Auto-Scrolls to Bottom

**Steps:**
1. Send 10 messages to fill chat
2. Observe scroll behavior

**Expected:**
- [ ] Chat automatically scrolls to show latest message
- [ ] Scroll is smooth (not instant jump)
- [ ] Latest message always visible

---

### Test 3.4: XSS Prevention (HTML Escape)

**Steps:**
1. Type message: `<script>alert('XSS')</script>`
2. Submit message

**Expected:**
- [ ] Message displays as plain text (HTML tags visible)
- [ ] NO alert popup appears
- [ ] Script NOT executed

**Console Check:**
```javascript
// Should NOT see alert
// Message should show: <script>alert('XSS')</script>
```

**Screenshot:** `test-3.4-xss-prevention.png`

---

## Category 4: AI Response Rendering

### Test 4.1: AI Response Appends to Chat

**Steps:**
1. Send message: "How many communities?"
2. Wait for response

**Expected:**
- [ ] AI response appears below user message
- [ ] Response has white background with emerald border
- [ ] Robot icon visible (🤖)
- [ ] Response is left-aligned
- [ ] "Just now" timestamp shown

**Screenshot:** `test-4.1-ai-response.png`

---

### Test 4.2: Line Breaks Render Correctly

**Steps:**
1. Send message that returns multi-line response
2. Observe text formatting

**Expected:**
- [ ] Line breaks preserved
- [ ] Text wraps at word boundaries
- [ ] Long URLs break correctly

---

### Test 4.3: Follow-up Suggestions Render

**Steps:**
1. Send message that returns suggestions
2. Observe suggestions section

**Expected:**
- [ ] Suggestions appear below response
- [ ] Border separator visible
- [ ] "You might also ask:" label shown
- [ ] Each suggestion is a clickable button
- [ ] Emerald styling on suggestions

**Screenshot:** `test-4.3-suggestions.png`

---

### Test 4.4: Error State with Suggestions

**Steps:**
1. Send gibberish message: "asdfasdfasdf"
2. Observe error handling

**Expected:**
- [ ] Error message shown in amber box
- [ ] "Try these instead:" label
- [ ] 4 example queries shown
- [ ] Each query is clickable

**Screenshot:** `test-4.4-error-suggestions.png`

---

### Test 4.5: Intent Badge Display

**Steps:**
1. Send message: "Show communities"
2. Check for intent badge

**Expected:**
- [ ] Intent badge visible (e.g., "Community_Info")
- [ ] Confidence percentage shown
- [ ] Emerald badge styling

**Screenshot:** `test-4.5-intent-badge.png`

---

## Category 5: Clickable Query Chips

### Test 5.1: Welcome Message Query Chips

**Steps:**
1. Open chat panel (first time, no messages)
2. Observe welcome message

**Expected:**
- [ ] 4 query chips visible:
  - Communities (emerald/teal gradient)
  - Assessments (blue/indigo gradient)
  - Activities (purple/pink gradient)
  - Help (amber/orange gradient)
- [ ] Each chip has icon
- [ ] Hover effect works

**Screenshot:** `test-5.1-query-chips.png`

---

### Test 5.2: Click Query Chip Submits

**Steps:**
1. Click "Communities" chip
2. Observe behavior

**Expected:**
- [ ] Input field populates with query
- [ ] Form submits automatically (HTMX)
- [ ] User message appears
- [ ] AI response received

**Network Tab:**
- [ ] XHR request with chip query

**Screenshot:** `test-5.2-chip-submit.png`

---

### Test 5.3: Suggestion Buttons Click

**Steps:**
1. Get a response with suggestions
2. Click a suggestion button

**Expected:**
- [ ] Input populates with suggestion
- [ ] Form submits
- [ ] New message pair created

---

### Test 5.4: Error Suggestion Buttons Click

**Steps:**
1. Trigger error state
2. Click an error suggestion

**Expected:**
- [ ] Input populates
- [ ] Form submits
- [ ] Valid response received

---

### Test 5.5: Multiple Rapid Clicks

**Steps:**
1. Click query chip rapidly 5 times

**Expected:**
- [ ] Only ONE request sent
- [ ] Submit button disabled during request
- [ ] No duplicate messages

---

## Category 6: Loading States

### Test 6.1: Loading Overlay Appearance

**Steps:**
1. Send message
2. Observe loading state

**Expected:**
- [ ] Overlay covers entire panel
- [ ] Backdrop blur effect
- [ ] Spinner animation smooth
- [ ] Loading text visible

**Screenshot:** `test-6.1-loading-overlay.png`

---

### Test 6.2: Dynamic Loading Messages

**Steps:**
1. Send "communities" → Check loading text
2. Send "assessments" → Check loading text
3. Send "help" → Check loading text

**Expected:**
- [ ] "Searching communities..." for community queries
- [ ] "Analyzing assessments..." for MANA queries
- [ ] "Preparing help..." for help queries
- [ ] "Thinking..." for generic queries

**Console Check:**
```javascript
// After each submit, check:
document.getElementById('ai-chat-loading-text').textContent
```

---

### Test 6.3: Loading Overlay Hides After Response

**Steps:**
1. Send message
2. Wait for response

**Expected:**
- [ ] Loading overlay shows during request
- [ ] Loading overlay hides when response arrives
- [ ] Submit button re-enabled

---

## Category 7: Error Handling

### Test 7.1: Network Error (Offline)

**Steps:**
1. Open DevTools → Network tab
2. Enable "Offline" mode
3. Send message

**Expected:**
- [ ] Error message displays in chat
- [ ] Red styling on error
- [ ] "Sorry, I encountered an error. Please try again."
- [ ] Submit button re-enabled
- [ ] User can retry

**Screenshot:** `test-7.1-network-error.png`

---

### Test 7.2: Server Error (500)

**Steps:**
1. Temporarily break backend (or simulate)
2. Send message

**Expected:**
- [ ] Error message in chat
- [ ] User can retry
- [ ] Form remains functional

---

### Test 7.3: Validation Error (400)

**Steps:**
1. Submit empty message (if validation allows)
2. Observe error handling

**Expected:**
- [ ] Error message shown
- [ ] User can correct and resubmit

---

### Test 7.4: Error Recovery

**Steps:**
1. Trigger error (offline mode)
2. Observe error message
3. Go back online
4. Send new message

**Expected:**
- [ ] New message works correctly
- [ ] Error doesn't persist
- [ ] Chat remains functional

---

## Category 8: Accessibility

### Test 8.1: Keyboard Navigation

**Steps:**
1. Close chat panel
2. Press `Tab` repeatedly
3. Press `Enter` on toggle button
4. Press `Tab` inside panel

**Expected:**
- [ ] Can reach toggle button via Tab
- [ ] Enter key opens chat
- [ ] Can Tab to close button
- [ ] Can Tab to input field
- [ ] Can Tab to send button
- [ ] Focus indicators visible

**Screenshot:** `test-8.1-keyboard-nav.png`

---

### Test 8.2: Screen Reader Announcements

**Steps:**
1. Enable VoiceOver (Mac) or NVDA (Windows)
2. Open chat panel
3. Send message

**Expected:**
- [ ] "AI chat opened" announced
- [ ] "New message received" announced
- [ ] "AI chat closed" announced

**Testing Tools:**
- macOS: VoiceOver (`Cmd+F5`)
- Windows: NVDA (free download)
- Screen reader should announce all state changes

---

### Test 8.3: ARIA Attributes

**Steps:**
1. Open chat panel
2. Inspect elements

**Expected:**
- [ ] Panel has `role="dialog"`
- [ ] Panel has `aria-labelledby="ai-chat-title"`
- [ ] Panel has `aria-hidden="false"` when open
- [ ] Toggle button has `aria-expanded="true"` when open
- [ ] Messages container has `role="log"`
- [ ] Messages container has `aria-live="polite"`

**Console Check:**
```javascript
const panel = document.getElementById('ai-chat-panel');
console.log('role:', panel.getAttribute('role')); // "dialog"
console.log('aria-labelledby:', panel.getAttribute('aria-labelledby')); // "ai-chat-title"
console.log('aria-hidden:', panel.getAttribute('aria-hidden')); // "false" when open
```

---

### Test 8.4: Focus Management

**Steps:**
1. Open chat panel
2. Check focus position

**Expected:**
- [ ] Close button receives focus when panel opens
- [ ] Focus returns to toggle button when panel closes

---

### Test 8.5: Escape Key Closes

**Steps:**
1. Open chat panel
2. Press `Escape` key

**Expected:**
- [ ] Panel closes
- [ ] Focus returns to toggle button

---

### Test 8.6: Focus Indicators

**Steps:**
1. Tab through all interactive elements
2. Observe focus styles

**Expected:**
- [ ] All buttons show focus outline (green)
- [ ] Input field shows focus ring (emerald)
- [ ] Focus indicators meet WCAG contrast requirements

---

## Category 9: Mobile Responsiveness

### Test 9.1: Mobile Layout (iPhone)

**Steps:**
1. Open DevTools
2. Select iPhone 14 Pro preset
3. Reload page
4. Open chat

**Expected:**
- [ ] Full-width bottom sheet
- [ ] 80vh height
- [ ] Rounded top corners only
- [ ] Backdrop visible
- [ ] Button 56px x 56px

**Screenshot:** `test-9.1-iphone.png`

---

### Test 9.2: Tablet Layout (iPad)

**Steps:**
1. Select iPad Pro 12.9" preset
2. Reload page
3. Open chat

**Expected:**
- [ ] Desktop layout (fixed 400x500px panel)
- [ ] No backdrop

**Screenshot:** `test-9.2-ipad.png`

---

### Test 9.3: Landscape Orientation (Mobile)

**Steps:**
1. Select iPhone 14 Pro
2. Rotate to landscape
3. Open chat

**Expected:**
- [ ] Panel adjusts to landscape
- [ ] Still usable (not cut off)

**Screenshot:** `test-9.3-landscape.png`

---

### Test 9.4: Very Small Screen (iPhone SE)

**Steps:**
1. Select iPhone SE preset (375x667)
2. Open chat

**Expected:**
- [ ] Bottom sheet still works
- [ ] All controls accessible
- [ ] Text readable

**Screenshot:** `test-9.4-small-screen.png`

---

### Test 9.5: Touch Targets (Mobile)

**Steps:**
1. Enable mobile emulation
2. Check all button sizes

**Expected:**
- [ ] All buttons ≥44px (WCAG minimum)
- [ ] Toggle button: 56px
- [ ] Send button: ≥44px
- [ ] Chip buttons: ≥44px

**Console Check:**
```javascript
const toggleBtn = document.getElementById('ai-chat-toggle-btn');
const rect = toggleBtn.getBoundingClientRect();
console.log('Button size:', rect.width, 'x', rect.height); // Should be ≥44x44
```

---

### Test 9.6: Query Chips Wrap on Narrow Screens

**Steps:**
1. Select very narrow width (320px)
2. Open chat

**Expected:**
- [ ] Query chips wrap to multiple lines
- [ ] All chips visible
- [ ] No horizontal overflow

---

## Category 10: JavaScript Functions

### Test 10.1: Debug Functions Work

**Steps:**
1. Open console
2. Run debug commands

**Expected:**
```javascript
// Should work without errors
debugAIChat(); // Logs debug info
enableAIChatDebug(); // Shows colored borders
disableAIChatDebug(); // Removes borders
forceShowAIChat(); // Emergency override
```

**Console Output:**
```
=== AI Chat Debug Info ===
Chat open: false
Panel classes: ai-chat-panel
Panel position: {...}
Computed styles: {...}
```

---

### Test 10.2: sendQuery() Function

**Steps:**
1. Open console
2. Run: `sendQuery("How many communities?")`

**Expected:**
- [ ] Input populates with query
- [ ] Form submits automatically
- [ ] HTMX request sent

---

### Test 10.3: escapeHtml() Prevents XSS

**Steps:**
1. Send: `<img src=x onerror=alert('XSS')>`

**Expected:**
- [ ] No alert
- [ ] HTML shown as text

---

### Test 10.4: Position Validation

**Steps:**
1. Resize window to very small
2. Open chat
3. Check console

**Expected:**
- [ ] Console logs position validation
- [ ] Panel adjusts if off-screen
- [ ] No errors

---

## Category 11: Performance

### Test 11.1: Initial Render Speed

**Steps:**
1. Reload page
2. Open Performance tab
3. Click toggle button
4. Stop recording

**Expected:**
- [ ] Panel opens in <100ms
- [ ] Smooth 60fps animation
- [ ] No layout shifts

---

### Test 11.2: HTMX Request Time

**Steps:**
1. Open Network tab
2. Send message
3. Measure request time

**Expected:**
- [ ] Request completes in <1000ms
- [ ] Response renders immediately

---

### Test 11.3: Smooth Scrolling

**Steps:**
1. Send 20 messages
2. Observe scroll behavior

**Expected:**
- [ ] Smooth scroll to bottom
- [ ] No janky animations
- [ ] 60fps maintained

---

### Test 11.4: Memory Leaks

**Steps:**
1. Open/close chat 50 times
2. Check Memory tab

**Expected:**
- [ ] Memory usage stable
- [ ] No memory leaks
- [ ] Event listeners cleaned up

---

## Test Results Summary

**Tester Name:** _______________
**Date:** _______________
**Environment:** _______________

| Category | Tests Passed | Tests Failed | Notes |
|----------|--------------|--------------|-------|
| 1. Visibility & Positioning | __ / 7 | __ | |
| 2. HTMX Form Submission | __ / 5 | __ | |
| 3. Optimistic UI Updates | __ / 4 | __ | |
| 4. AI Response Rendering | __ / 5 | __ | |
| 5. Clickable Query Chips | __ / 5 | __ | |
| 6. Loading States | __ / 3 | __ | |
| 7. Error Handling | __ / 4 | __ | |
| 8. Accessibility | __ / 6 | __ | |
| 9. Mobile Responsiveness | __ / 6 | __ | |
| 10. JavaScript Functions | __ / 4 | __ | |
| 11. Performance | __ / 4 | __ | |

**Total:** __ / 53

---

## Issues Found

| # | Category | Severity | Description | Screenshot |
|---|----------|----------|-------------|------------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

---

## Browser-Specific Notes

**Chrome:**
- [ ] All tests pass

**Firefox:**
- [ ] All tests pass
- [ ] Known issues: _______________

**Safari:**
- [ ] All tests pass
- [ ] Known issues: _______________

**Edge:**
- [ ] All tests pass
- [ ] Known issues: _______________

---

## Sign-Off

**QA Engineer:** _______________
**Date:** _______________
**Status:** ☐ Approved ☐ Rejected ☐ Needs Review

**Deployment Recommendation:** ☐ Ready ☐ Not Ready ☐ Conditional

**Comments:**
_______________________________________________
_______________________________________________
_______________________________________________
