# AI Chat Widget - Quick Testing Guide

**For:** Developers & QA Engineers
**Duration:** 5 minutes
**Purpose:** Verify chat widget works correctly

---

## 🚀 Quick Start (30 seconds)

### 1. Open Browser Console

**Chrome/Edge/Firefox:**
- Press `F12` or `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)

### 2. Load Test Helpers

```javascript
// Copy and paste this URL into browser:
// Then copy the entire contents of the file and paste into console

// Or manually copy from: /docs/testing/browser_test_helpers.js
```

### 3. Run All Tests

```javascript
runAllTests()
```

**Expected Output:**
```
🚀 Running All AI Chat Widget Tests...

=== TEST: Chat Toggle & Visibility ===
✅ Widget element exists
✅ Panel element exists
✅ Toggle button exists
✅ Panel initially hidden
✅ Panel opens with chat-open class
✅ Panel aria-hidden set to false
✅ Button aria-expanded set to true
✅ Icon changed to X (times)
✅ Desktop: Panel bottom position ~100px (actual: 100px)
✅ Desktop: Panel right position ~24px (actual: 24px)
✅ Desktop: Panel width ~400px (actual: 400px)
✅ Panel visibility set to visible
✅ Panel opacity is 1
✅ Panel closes (chat-open class removed)
✅ Panel aria-hidden set to true
✅ Icon changed back to comments

📊 Result: 15/15 tests passed

... (other categories) ...

🏆 OVERALL: 53/53 tests passed (100%)

🎉 EXCELLENT! Widget is production-ready!
```

---

## ✅ Quick Verification (2 minutes)

### Test 1: Toggle Chat (15 seconds)

1. Look for chat button in bottom-right corner (💬)
2. Click button → Panel opens smoothly
3. Icon changes to X (✕)
4. Click X → Panel closes
5. Icon changes back to comment (💬)

**Pass Criteria:** ✅ Smooth animations, no errors

---

### Test 2: Send Message (30 seconds)

1. Open chat
2. Type: "How many communities?"
3. Press Enter
4. User message appears immediately (blue bubble)
5. Loading indicator shows
6. AI response appears (white bubble with robot icon)

**Pass Criteria:** ✅ Instant user message, AI response within 1 second

---

### Test 3: Click Query Chip (15 seconds)

1. Open chat (if no messages, you'll see welcome)
2. Click any query chip (e.g., "Communities")
3. Input field populates
4. Form submits automatically
5. Response appears

**Pass Criteria:** ✅ One-click interaction, smooth flow

---

### Test 4: Test Error Handling (30 seconds)

1. Open browser DevTools → Network tab
2. Enable "Offline" mode
3. Open chat
4. Type message and send
5. Error message appears in red

**Pass Criteria:** ✅ Error shown, submit button re-enabled

---

### Test 5: Mobile Layout (30 seconds)

1. Open DevTools
2. Enable device emulation (iPhone 14 Pro)
3. Reload page
4. Open chat
5. Panel appears as full-width bottom sheet
6. Backdrop visible

**Pass Criteria:** ✅ Full-width panel, backdrop visible, 80vh height

---

### Test 6: Keyboard Navigation (30 seconds)

1. Close chat if open
2. Press Tab until toggle button focused
3. Press Enter → Chat opens
4. Press Escape → Chat closes
5. Focus returns to toggle button

**Pass Criteria:** ✅ Full keyboard control, focus management works

---

## 🐛 Common Issues & Fixes

### Issue: Panel not visible

**Symptom:** Click button but panel doesn't appear

**Debug:**
```javascript
debugAIChat()
// Check: Chat open: true, hasOpenClass: true, visibility: visible
```

**Fix:**
```javascript
forceShowAIChat() // Emergency override
```

---

### Issue: HTMX not working

**Symptom:** Form submits but nothing happens

**Debug:**
1. Check Network tab → XHR requests
2. Look for `/common/chat/message/` POST request
3. Check response (should be HTML)

**Fix:**
- Verify CSRF token present
- Check Django view is working
- Ensure HTMX library loaded

---

### Issue: Messages not appearing

**Symptom:** Response received but not shown in chat

**Debug:**
```javascript
// Check if messages appended
document.querySelectorAll('.ai-message-bot').length
document.querySelectorAll('.ai-message-user').length
```

**Fix:**
- Check HTMX swap target (`#ai-chat-messages`)
- Verify template renders correctly
- Check for JavaScript errors in console

---

### Issue: Mobile layout broken

**Symptom:** Panel not full-width on mobile

**Debug:**
```javascript
// Check viewport
console.log(`Viewport: ${window.innerWidth}x${window.innerHeight}`);

// Check panel dimensions
const panel = document.getElementById('ai-chat-panel');
const rect = panel.getBoundingClientRect();
console.log(`Panel: ${rect.width}x${rect.height}`);
```

**Fix:**
- Ensure media query works (`@media (max-width: 640px)`)
- Check for CSS conflicts
- Verify mobile-specific styles applied

---

### Issue: Animations choppy

**Symptom:** Jerky animations, not smooth

**Debug:**
1. Open Performance tab
2. Record panel open/close
3. Check frame rate (should be 60fps)

**Fix:**
- Ensure hardware acceleration (GPU rendering)
- Use `transform` and `opacity` (avoid `width`/`height`)
- Check for layout thrashing

---

## 📊 Test Results Interpretation

### 100% Pass (53/53 tests)
✅ **Production Ready** - Deploy immediately

### 95%+ Pass (50-52/53 tests)
⚠️ **Minor Issues** - Review failing tests, likely non-critical

### 80-94% Pass (42-49/53 tests)
⚠️ **Needs Attention** - Fix failing tests before deployment

### <80% Pass (<42/53 tests)
❌ **Not Ready** - Critical issues, investigate thoroughly

---

## 🔍 Detailed Testing

### For Comprehensive Testing:

1. **Manual Checklist** (30 minutes)
   - Open: `/docs/testing/FRONTEND_MANUAL_TEST_CHECKLIST.md`
   - Follow step-by-step instructions
   - Mark results in checklist

2. **Visual Testing** (15 minutes)
   - Open: `/docs/testing/AI_CHAT_VISUAL_TEST_GUIDE.md`
   - Compare screenshots
   - Verify visual states

3. **Full Test Report** (Reference)
   - Open: `/docs/testing/FRONTEND_TEST_RESULTS.md`
   - Comprehensive analysis
   - Browser compatibility matrix

---

## 📝 Test Report Generation

### Generate Markdown Report

```javascript
generateTestReport()
```

**Output:**
```
📄 Generating Test Report...

=== MARKDOWN REPORT ===
# AI Chat Widget Test Report

**Date:** 2025-10-06T...
**Browser:** Mozilla/5.0...
**Viewport:** 1920x1080

## Test Results

| Category | Passed | Total | Success Rate |
|----------|--------|-------|--------------|
| ✅ chatToggle | 15 | 15 | 100.0% |
| ✅ htmxSubmission | 5 | 5 | 100.0% |
| ✅ optimisticUI | 7 | 7 | 100.0% |
...

**Overall:** 53/53 (100%)

## Recommendations

✅ **Production Ready** - Widget meets all quality standards.

✅ Report copied to clipboard!
```

**Paste into:** Documentation file or GitHub issue

---

## 🎯 Critical Test Points

### Must-Pass Tests:

1. ✅ **HTMX Form Submission**
   - Form submits without page reload
   - CSRF token included
   - Response appends to chat

2. ✅ **Optimistic UI**
   - User message appears instantly (<50ms)
   - XSS prevention (HTML escaped)
   - Auto-scroll to bottom

3. ✅ **Accessibility**
   - WCAG 2.1 AA compliant
   - Keyboard navigation works
   - Screen reader compatible

4. ✅ **Error Handling**
   - Network errors caught
   - User-friendly error messages
   - Form recovers gracefully

5. ✅ **Mobile Responsive**
   - Full-width bottom sheet
   - Touch targets ≥44px
   - Backdrop visible

---

## 🚨 Emergency Debug Commands

### If widget completely broken:

```javascript
// 1. Force show panel (emergency override)
forceShowAIChat()

// 2. Enable debug mode (shows borders)
enableAIChatDebug()

// 3. Check panel visibility
checkPanelVisibility()

// 4. Send test message
simulateMessage('Test emergency message')

// 5. Clear all messages
clearChatMessages()

// 6. Full debug info
debugAIChat()
```

---

## 📋 Pre-Deployment Checklist

Before deploying to production:

- [ ] All 53 tests pass (`runAllTests()`)
- [ ] No JavaScript errors in console
- [ ] HTMX requests work (check Network tab)
- [ ] Tested on Chrome, Firefox, Safari, Edge
- [ ] Tested on mobile (iPhone, Android)
- [ ] Keyboard navigation works
- [ ] Error handling verified (offline mode)
- [ ] Accessibility verified (screen reader)
- [ ] Performance metrics met (Lighthouse >90)

---

## 🔗 Documentation Links

### Test Documentation:
1. **Test Results** → `/docs/testing/FRONTEND_TEST_RESULTS.md`
2. **Manual Checklist** → `/docs/testing/FRONTEND_MANUAL_TEST_CHECKLIST.md`
3. **Visual Guide** → `/docs/testing/AI_CHAT_VISUAL_TEST_GUIDE.md`
4. **Test Summary** → `/docs/testing/AI_CHAT_WIDGET_TESTING_SUMMARY.md`
5. **This Guide** → `/docs/testing/QUICK_TEST_GUIDE.md`

### Code Files:
1. **Widget Template** → `/src/templates/components/ai_chat_widget.html`
2. **Backend View** → `/src/common/views/chat.py`
3. **Response Template** → `/src/templates/common/chat/message_pair.html`
4. **Test Scripts** → `/docs/testing/browser_test_helpers.js`

---

## 💡 Tips

### For QA Engineers:
- Use automated tests first (`runAllTests()`)
- Follow manual checklist for comprehensive testing
- Take screenshots of each visual state
- Test on real devices (not just emulators)

### For Developers:
- Run tests after every change
- Use debug commands for troubleshooting
- Check console for errors
- Verify HTMX events in Network tab

### For Designers:
- Use visual guide for UI verification
- Check color palette reference
- Verify animation timings
- Test on multiple screen sizes

---

**Quick Test Guide Version:** 1.0
**Last Updated:** 2025-10-06
**Estimated Time:** 5-30 minutes (depending on depth)
