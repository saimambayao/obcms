# AI Chat Widget - Visual Testing Guide

**Purpose:** Visual reference for expected UI states and behaviors
**Component:** AI Chat Widget (HTMX Integration)
**For:** QA Engineers, Designers, Developers

---

## Visual States Reference

### State 1: Initial Load (Closed)

**Expected Appearance:**
```
┌─────────────────────────────────────┐
│                                     │
│         (Page Content)              │
│                                     │
│                                     │
│                                     │
│                                 ┌──┐│
│                                 │💬││  ← Toggle Button
│                                 └──┘│  (Blue-Teal Gradient)
└─────────────────────────────────────┘
```

**CSS State:**
- Button: `position: fixed; bottom: 24px; right: 24px`
- Button: `width: 64px; height: 64px` (desktop)
- Button: `width: 56px; height: 56px` (mobile)
- Icon: `fa-comments` (💬)
- Panel: `opacity: 0; visibility: hidden; pointer-events: none`

**How to Verify:**
1. Load any page in OBCMS
2. Look for button in bottom-right corner
3. Panel should NOT be visible
4. Console: `debugAIChat()` → Chat open: false

---

### State 2: Panel Open (Desktop)

**Expected Appearance:**
```
┌─────────────────────────────────────────────────────┐
│                                                     │
│         (Page Content)                              │
│                                   ┌─────────────┐   │
│                                   │ 🤖 AI Asst. │   │ ← Header (Emerald Gradient)
│                                   │─────────────│   │
│                                   │ Hello! I'm  │   │
│                                   │ your AI...  │   │ ← Welcome Message
│                                   │             │   │
│                                   │ [Chip][Chip]│   │ ← Query Chips
│                                   │             │   │
│                                   │─────────────│   │
│                                   │ Type... [>] │   │ ← Input Area
│                                   └─────────────┘   │
│                                                 ┌──┐│
│                                                 │✕ ││ ← Toggle Button (X icon)
│                                                 └──┘│
└─────────────────────────────────────────────────────┘
```

**Dimensions (Desktop):**
- Panel: `400px width × 500px height`
- Position: `bottom: 100px; right: 24px`
- Border radius: `12px` (all corners)
- Shadow: Large (`shadow-2xl`)

**How to Verify:**
1. Click toggle button
2. Panel slides up from bottom-right (300ms animation)
3. Panel is 400px × 500px
4. Icon changes to X (✕)
5. Button has blue ring glow
6. Console: `debugAIChat()` → Chat open: true

---

### State 3: Panel Open (Mobile)

**Expected Appearance:**
```
┌─────────────────────────────────────┐
│ ████████████████████████████████████│ ← Backdrop (semi-transparent)
│ ████████████████████████████████████│
│ ████┌──────────────────────────┐████│
│ ████│ 🤖 AI Assistant         │████│ ← Header
│ ████│──────────────────────────│████│
│ ████│ Hello! I'm your AI...   │████│
│ ████│                          │████│
│ ████│ [Chip] [Chip] [Chip]    │████│
│ ████│                          │████│ ← 80vh height
│ ████│                          │████│
│ ████│                          │████│
│ ████│──────────────────────────│████│
│ ████│ Type your message... [>]│████│ ← Input
└─────└──────────────────────────┘─────┘
                                    ┌──┐
                                    │✕ │ ← Button
                                    └──┘
```

**Dimensions (Mobile <640px):**
- Panel: `100% width × 80vh height`
- Position: `bottom: 0; left: 0; right: 0`
- Border radius: `16px 16px 0 0` (top corners only)
- Backdrop: Visible, blurred background

**How to Verify:**
1. Open DevTools, enable device emulation (iPhone 14 Pro)
2. Click toggle button
3. Panel slides up from bottom (full width)
4. Backdrop appears behind panel
5. Panel height is 80% of viewport
6. Top corners are rounded, bottom corners are square

---

### State 4: User Message (Optimistic UI)

**Expected Appearance:**
```
┌────────────────────────────────────┐
│ 🤖 AI Assistant              [✕]  │
│────────────────────────────────────│
│                                    │
│ 🤖  Hello! I'm your AI assistant.  │
│                                    │
│                    ┌──────────────┐│
│                    │How many comm.││ ← User Message
│                    │Just now      ││ (Blue Gradient, Right-aligned)
│                    └──────────────┘│
│                                    │
│ 🤖  ⚫⚫⚫                           │ ← Loading Dots
│                                    │
│────────────────────────────────────│
│ Type your message...            [>]│
└────────────────────────────────────┘
```

**Timing:**
1. User types "How many communities?"
2. User presses Enter or clicks Send
3. **Instant (<50ms):** User message appears (blue bubble, right-aligned)
4. **Instant:** Loading indicator shows (animated dots)
5. **~400ms later:** AI response appears

**CSS Classes:**
- User message: `.ai-message-user`
- Background: `bg-gradient-to-br from-blue-500 to-blue-600`
- Text: `text-white`
- Alignment: `justify-end` (flex)
- Timestamp: `Just now` (opacity 75%)

**How to Verify:**
1. Type message in input
2. Press Enter
3. User message appears IMMEDIATELY (before server response)
4. Loading dots animate
5. Network tab shows XHR request in progress

---

### State 5: AI Response with Suggestions

**Expected Appearance:**
```
┌────────────────────────────────────────┐
│ 🤖 AI Assistant                  [✕]  │
│────────────────────────────────────────│
│                      ┌────────────────┐│
│                      │How many comm?  ││ ← User Message
│                      │Just now        ││
│                      └────────────────┘│
│                                        │
│ 🤖 ┌──────────────────────────────────┐│
│    │There are 1,247 communities in   ││ ← AI Response
│    │the OBCMS database.               ││ (White with Emerald Border)
│    │                                  ││
│    │──────────────────────────────────││
│    │💡 You might also ask:            ││ ← Suggestions Section
│    │                                  ││
│    │ ▸ Show me communities in IX      ││ ← Suggestion 1
│    │ ▸ List assessments this month    ││ ← Suggestion 2
│    │ ▸ What's the total population?   ││ ← Suggestion 3
│    │                                  ││
│    │Just now                          ││
│    └──────────────────────────────────┘│
│────────────────────────────────────────│
│ Type your message...                [>]│
└────────────────────────────────────────┘
```

**Elements:**
1. **AI Response Bubble:**
   - Background: `bg-white`
   - Border: `border border-emerald-100`
   - Icon: Robot emoji or `fa-robot`
   - Text: `text-gray-700`

2. **Suggestions:**
   - Separator: `border-t border-gray-100`
   - Label: "💡 You might also ask:"
   - Buttons: Emerald background (`bg-emerald-50`)
   - Hover: Darker emerald (`hover:bg-emerald-100`)
   - Icon: Arrow right (▸)

**How to Verify:**
1. Send message that returns suggestions
2. Check for border separator above suggestions
3. Verify suggestion buttons are clickable
4. Click suggestion → Input populates → Form submits

---

### State 6: Error State with Helpful Suggestions

**Expected Appearance:**
```
┌────────────────────────────────────────┐
│ 🤖 AI Assistant                  [✕]  │
│────────────────────────────────────────│
│                      ┌────────────────┐│
│                      │asdfasdf        ││ ← User Message (Gibberish)
│                      │Just now        ││
│                      └────────────────┘│
│                                        │
│ 🤖 ┌──────────────────────────────────┐│
│    │I couldn't understand that.       ││ ← Error Message
│    │                                  ││
│    │┌────────────────────────────────┐││ ← Amber Error Box
│    ││💡 Try these instead:           │││
│    ││                                │││
│    ││ 👥 "How many communities in IX?"│││ ← Example 1
│    ││                                │││
│    ││ 📋 "Show me MANA assessments"  │││ ← Example 2
│    ││                                │││
│    ││ 🤝 "List coordination activities│││ ← Example 3
│    ││                                │││
│    ││ ❓ "What can you help me with?" │││ ← Example 4
│    │└────────────────────────────────┘││
│    │Just now                          ││
│    └──────────────────────────────────┘│
│────────────────────────────────────────│
│ Type your message...                [>]│
└────────────────────────────────────────┘
```

**Error Box Styling:**
- Background: `bg-amber-50`
- Border: `border border-amber-200`
- Text: `text-amber-900` (label), `text-gray-700` (examples)
- Icons: Colored (emerald, blue, purple, blue)
- Hover: `hover:bg-amber-100`

**How to Verify:**
1. Send gibberish: "asdfasdfasdf"
2. Error response received
3. Amber box appears with 4 example queries
4. Each example is clickable
5. Click example → Input populates → Form submits

---

### State 7: Loading State

**Expected Appearance:**
```
┌────────────────────────────────────────┐
│ 🤖 AI Assistant                  [✕]  │
│────────────────────────────────────────│
│     ╔═══════════════════════════════╗  │
│     ║                               ║  │ ← Loading Overlay
│     ║         ⚪ (spinning)          ║  │   (Covers entire panel)
│     ║                               ║  │
│     ║   Searching communities...    ║  │ ← Context-aware message
│     ║   Processing your query       ║  │
│     ║                               ║  │
│     ╚═══════════════════════════════╝  │
│────────────────────────────────────────│
│ Type your message...                [>]│
└────────────────────────────────────────┘
```

**Loading Messages by Query Type:**
- "communities" → "Searching communities..."
- "assessment", "MANA" → "Analyzing assessments..."
- "coordination", "activity" → "Finding activities..."
- "policy" → "Searching policies..."
- "project", "PPA" → "Locating projects..."
- Default → "Thinking..."

**Overlay Properties:**
- Background: `bg-white/80` (80% opacity)
- Backdrop filter: `backdrop-blur-sm`
- Z-index: `z-10` (above messages, below header)
- Spinner: Emerald color with border animation

**How to Verify:**
1. Send message
2. Loading overlay appears immediately
3. Spinner rotates smoothly
4. Message is context-specific
5. Overlay disappears when response arrives
6. Submit button disabled during loading

---

### State 8: Network Error

**Expected Appearance:**
```
┌────────────────────────────────────────┐
│ 🤖 AI Assistant                  [✕]  │
│────────────────────────────────────────│
│                      ┌────────────────┐│
│                      │Test message    ││ ← User Message
│                      │Just now        ││
│                      └────────────────┘│
│                                        │
│ ⚠️ ┌──────────────────────────────────┐│
│    │Sorry, I encountered an error.    ││ ← Error Message
│    │Please try again.                 ││ (Red Background)
│    │Just now                          ││
│    └──────────────────────────────────┘│
│────────────────────────────────────────│
│ Type your message...                [>]│
└────────────────────────────────────────┘
```

**Error Message Styling:**
- Class: `.ai-message-error`
- Background: `bg-red-50`
- Border: `border border-red-200`
- Text: `text-red-700`
- Icon: `fa-exclamation-triangle` (red)

**How to Verify:**
1. Open DevTools → Network tab
2. Enable "Offline" mode
3. Send message
4. Error message appears with red styling
5. Submit button re-enabled
6. User can type and retry

---

### State 9: Intent Badge (Debug Info)

**Expected Appearance:**
```
┌────────────────────────────────────────┐
│ 🤖 ┌──────────────────────────────────┐│
│    │There are 1,247 communities...    ││
│    │                                  ││
│    │──────────────────────────────────││
│    │🏷️ Community_Info    [85%]        ││ ← Intent Badge
│    │                                  ││
│    │Just now                          ││
│    └──────────────────────────────────┘│
└────────────────────────────────────────┘
```

**Badge Properties:**
- Icon: `fa-tag`
- Intent text: Capitalized (e.g., "Community_Info")
- Confidence: Emerald badge (`bg-emerald-50 text-emerald-600`)
- Separator: `border-t border-gray-100`

**How to Verify:**
1. Send message
2. Check if response includes intent
3. Verify badge appears at bottom of response
4. Confidence shown as percentage

---

### State 10: Welcome Message with Query Chips

**Expected Appearance:**
```
┌────────────────────────────────────────┐
│ 🤖 AI Assistant                  [✕]  │
│────────────────────────────────────────│
│ 🤖 ┌──────────────────────────────────┐│
│    │Hello! I'm your AI assistant. I   ││
│    │can help you with:                ││
│    │                                  ││
│    │ ✅ Finding community data        ││
│    │ ✅ Analyzing assessments         ││
│    │ ✅ Generating reports            ││
│    │ ✅ Answering questions           ││
│    │                                  ││
│    │──────────────────────────────────││
│    │⚡ Try these quick queries:       ││
│    │                                  ││
│    │ [👥 Communities] [📋 Assessments]││ ← Query Chips
│    │ [🤝 Activities]  [❓ Help]       ││
│    │                                  ││
│    └──────────────────────────────────┘│
│────────────────────────────────────────│
│ Type your message...                [>]│
└────────────────────────────────────────┘
```

**Query Chip Styling:**
1. **Communities Chip:**
   - Background: `bg-gradient-to-r from-emerald-50 to-teal-50`
   - Hover: `from-emerald-100 to-teal-100`
   - Text: `text-emerald-700`
   - Border: `border-emerald-200`
   - Icon: 👥 `fa-users`

2. **Assessments Chip:**
   - Background: `from-blue-50 to-indigo-50`
   - Hover: `from-blue-100 to-indigo-100`
   - Text: `text-blue-700`
   - Border: `border-blue-200`
   - Icon: 📋 `fa-clipboard-check`

3. **Activities Chip:**
   - Background: `from-purple-50 to-pink-50`
   - Hover: `from-purple-100 to-pink-100`
   - Text: `text-purple-700`
   - Border: `border-purple-200`
   - Icon: 🤝 `fa-handshake`

4. **Help Chip:**
   - Background: `from-amber-50 to-orange-50`
   - Hover: `from-amber-100 to-orange-100`
   - Text: `text-amber-700`
   - Border: `border-amber-200`
   - Icon: ❓ `fa-question-circle`

**How to Verify:**
1. Open chat when no messages exist
2. Welcome message appears
3. 4 query chips visible
4. Each chip has gradient background
5. Hover effect works (darker gradient)
6. Click chip → Input populates → Form submits

---

## Color Palette Reference

### Primary Colors

**Emerald (Primary):**
- `emerald-50`: `#ecfdf5` (Lightest - chip backgrounds)
- `emerald-100`: `#d1fae5` (Light - borders)
- `emerald-500`: `#10b981` (Medium - icons)
- `emerald-600`: `#059669` (Dark - focus rings)

**Blue (User Messages):**
- `blue-50`: `#eff6ff` (Lightest)
- `blue-500`: `#3b82f6` (Medium - user message gradient start)
- `blue-600`: `#2563eb` (Dark - user message gradient end)
- `blue-700`: `#1d4ed8` (Darker - chip text)

**Teal (Accents):**
- `teal-50`: `#f0fdfa` (Lightest)
- `teal-500`: `#14b8a6` (Medium)
- `teal-600`: `#0d9488` (Dark - gradient end)

### Status Colors

**Red (Errors):**
- `red-50`: `#fef2f2` (Background)
- `red-200`: `#fecaca` (Border)
- `red-500`: `#ef4444` (Icon)
- `red-700`: `#b91c1c` (Text)

**Amber (Warnings/Help):**
- `amber-50`: `#fffbeb` (Background)
- `amber-200`: `#fde68a` (Border)
- `amber-700`: `#b45309` (Text)

**Gray (UI Elements):**
- `gray-50`: `#f9fafb` (Chat background)
- `gray-100`: `#f3f4f6` (Borders)
- `gray-200`: `#e5e7eb` (Input borders)
- `gray-600`: `#4b5563` (Icons)
- `gray-700`: `#374151` (Text)

---

## Animation Reference

### 1. Panel Open/Close Animation

**Open (300ms):**
```css
@keyframes slideUpFadeIn {
    from {
        opacity: 0;
        transform: translateY(10px) scale(0.95);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}
```

**Close (200ms):**
```css
/* Reverse of slideUpFadeIn */
opacity: 0;
transform: scale(0.95);
transition: all 0.2s ease-in;
```

**How to Verify:**
1. Click toggle button
2. Panel slides up smoothly (300ms)
3. Panel scales from 95% to 100%
4. Opacity fades from 0 to 1

### 2. Message Fade-In

**Animation (400ms):**
```css
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(5px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
```

**Applied to:**
- `.animate-fade-in` class
- User messages
- AI responses
- Error messages

### 3. Button Pulse (Idle State)

**Animation (2s, infinite):**
```css
@keyframes pulse-ring {
    0%, 100% {
        opacity: 0;
        transform: scale(1);
    }
    50% {
        opacity: 0.3;
        transform: scale(1.15);
    }
}
```

**Applied to:**
- Toggle button when closed
- Creates pulsing ring effect

### 4. Loading Spinner

**Animation (1s, infinite):**
```css
.animate-spin {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}
```

**Applied to:**
- Loading overlay spinner
- Smooth rotation

### 5. Smooth Scroll

**JavaScript:**
```javascript
chatMessages.scrollTo({
    top: chatMessages.scrollHeight,
    behavior: 'smooth'
});
```

**Timing:**
- Duration: ~100-200ms
- Easing: CSS `scroll-behavior: smooth`

---

## Responsive Breakpoints

### Mobile (<640px)

**Changes:**
- Panel: Full width, 80vh height, bottom sheet style
- Button: 56px × 56px (WCAG compliant)
- Backdrop: Visible
- Border radius: Top corners only (`1rem 1rem 0 0`)

### Tablet (640px - 1023px)

**Changes:**
- Panel: Desktop layout (400px × 500px)
- Button: 64px × 64px
- Backdrop: Hidden
- Border radius: All corners (`12px`)

### Desktop (≥1024px)

**Changes:**
- Panel: Desktop layout (400px × 500px)
- Button: 64px × 64px
- Backdrop: Hidden
- Position: `bottom: 100px; right: 24px`

---

## Testing Checklist (Visual QA)

### Toggle Button
- [ ] Visible in bottom-right corner
- [ ] Correct size (64px desktop, 56px mobile)
- [ ] Gradient background (blue to teal)
- [ ] Icon changes (comments ↔ times)
- [ ] Pulse animation when closed
- [ ] Ring glow when open

### Panel (Desktop)
- [ ] 400px × 500px dimensions
- [ ] Position: bottom 100px, right 24px
- [ ] Rounded corners (12px all)
- [ ] Smooth open animation (300ms)
- [ ] No backdrop visible
- [ ] Within viewport bounds

### Panel (Mobile)
- [ ] Full width (100vw)
- [ ] 80vh height
- [ ] Bottom sheet style
- [ ] Rounded top corners only
- [ ] Backdrop visible and blurred
- [ ] Slides up from bottom

### Messages
- [ ] User: Blue gradient, right-aligned
- [ ] AI: White with emerald border, left-aligned
- [ ] Timestamps: "Just now" text
- [ ] Smooth fade-in animation
- [ ] Auto-scroll to bottom

### Query Chips
- [ ] 4 chips in welcome message
- [ ] Gradient backgrounds (emerald, blue, purple, amber)
- [ ] Icons visible
- [ ] Hover effect works
- [ ] Click populates input

### Suggestions
- [ ] Border separator visible
- [ ] "You might also ask:" label
- [ ] Emerald background
- [ ] Arrow icon (▸)
- [ ] Clickable

### Error State
- [ ] Red styling (bg-red-50)
- [ ] Exclamation icon
- [ ] Error message clear
- [ ] Amber suggestion box (if applicable)
- [ ] Submit button re-enabled

### Loading State
- [ ] Overlay covers panel
- [ ] Backdrop blur effect
- [ ] Spinner rotates smoothly
- [ ] Context-aware message
- [ ] Submit button disabled

### Accessibility
- [ ] Focus indicators visible
- [ ] Escape key closes
- [ ] Screen reader announcements
- [ ] Keyboard navigation works
- [ ] ARIA attributes correct

---

## Screenshot Checklist

**Required Screenshots:**

1. ✅ `initial-load.png` - Chat button visible, panel hidden
2. ✅ `panel-open-desktop.png` - Desktop layout (400×500px)
3. ✅ `panel-open-mobile.png` - Mobile bottom sheet with backdrop
4. ✅ `user-message.png` - Blue gradient user message
5. ✅ `ai-response.png` - White AI response with emerald border
6. ✅ `suggestions.png` - Follow-up suggestions visible
7. ✅ `error-state.png` - Amber error box with examples
8. ✅ `loading-state.png` - Loading overlay with spinner
9. ✅ `welcome-message.png` - Welcome with query chips
10. ✅ `network-error.png` - Red error message
11. ✅ `focus-state.png` - Keyboard focus indicators
12. ✅ `mobile-landscape.png` - Mobile landscape orientation

---

## Common Visual Issues

### Issue 1: Panel Not Visible

**Symptom:** Panel doesn't appear when opened

**Check:**
1. Console: `debugAIChat()` → Check `opacity`, `visibility`
2. Inspect: Look for `chat-open` class
3. Console: `forceShowAIChat()` → Emergency override

**Fix:**
- Ensure `chat-open` class is added
- Check z-index conflicts
- Verify position: fixed (not absolute)

### Issue 2: Panel Off-Screen

**Symptom:** Panel appears outside viewport

**Check:**
1. Console: `checkPanelVisibility()`
2. Console: `validatePanelPosition()` → Should auto-adjust

**Fix:**
- Panel auto-adjusts via `validatePanelPosition()`
- Check viewport size vs panel size
- Ensure media queries work

### Issue 3: Animations Janky

**Symptom:** Choppy animations, not smooth

**Check:**
1. Performance tab → Check frame rate
2. Look for layout thrashing
3. Check for unnecessary repaints

**Fix:**
- Ensure hardware acceleration (transform, opacity)
- Avoid animating width/height
- Use `will-change` sparingly

### Issue 4: Messages Not Scrolling

**Symptom:** New messages don't auto-scroll to bottom

**Check:**
1. Console: `chatMessages.scrollTop` → Should match `scrollHeight`
2. Check `overflow-y: auto` on messages container

**Fix:**
- Ensure `scrollTo()` is called after message added
- Use `behavior: 'smooth'` for smooth scroll
- Check for CSS `overflow` conflicts

### Issue 5: Chips Not Clickable

**Symptom:** Query chips don't respond to clicks

**Check:**
1. Console: Check event delegation setup
2. Inspect: Verify `data-query` attributes
3. Console: `sendQuery('test')` → Should work

**Fix:**
- Ensure event delegation initialized
- Check for z-index/pointer-events issues
- Verify `sendQuery()` function exists

---

## Debug Commands Quick Reference

```javascript
// Visual debugging
debugAIChat()                    // Log panel state
checkPanelVisibility()           // Check position & visibility
enableAIChatDebug()              // Show colored borders (red=closed, green=open)
forceShowAIChat()                // Emergency visibility override

// Functionality testing
simulateMessage('Test')          // Send test message
sendQuery('Test query')          // Simulate chip click
clearChatMessages()              // Clear all messages
testKeyboardNav()                // Test keyboard navigation

// Run tests
runAllTests()                    // Run all automated tests
generateTestReport()             // Generate markdown report
```

---

**Visual Guide Version:** 1.0
**Last Updated:** 2025-10-06
**For:** QA Engineers, Designers, Developers
**Next Review:** After first deployment
