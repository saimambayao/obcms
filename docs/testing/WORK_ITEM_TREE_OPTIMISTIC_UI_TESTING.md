# Work Item Tree Optimistic UI - Testing Guide

**Date:** 2025-10-06
**Component:** Work Items Hierarchical Tree View
**Implementation:** Optimistic UI with Instant Loading Indicators

---

## Quick Test Checklist

### Basic Functionality

```
□ Navigate to Work Items list (/oobc-management/work-items/)
□ Verify page loads without errors
□ Check console for initialization message:
  "✅ Work Items tree navigation initialized with optimistic UI updates (< 50ms instant feedback)"
□ Confirm at least one parent item with children exists
```

---

## Test Cases

### Test 1: Instant Visual Feedback

**Objective:** Verify chevron rotates and skeleton appears instantly (< 50ms)

**Steps:**
1. Navigate to Work Items list
2. Find a parent item with children (shows count badge)
3. Click the expand button (chevron-right icon)
4. **OBSERVE:**
   - Chevron should rotate to down position **INSTANTLY**
   - Skeleton row should appear below parent **INSTANTLY**
   - Spinner should replace chevron icon **INSTANTLY**

**Expected Result:**
- All visual changes happen within ~20ms (feels instant)
- No delay between click and visual feedback

**Pass Criteria:**
- ✅ Chevron rotates immediately
- ✅ Skeleton row visible immediately
- ✅ Spinner shows immediately

---

### Test 2: Loading State

**Objective:** Verify loading indicators work during HTMX request

**Steps:**
1. Navigate to Work Items list
2. Click expand button on parent item
3. **OBSERVE during request:**
   - Spinner icon visible (replaces chevron)
   - Skeleton row visible with pulsing animation
   - Button is disabled (cannot click again)

**Expected Result:**
- Loading state visible throughout request
- No double-click possible

**Pass Criteria:**
- ✅ Spinner visible during request
- ✅ Skeleton row pulsing
- ✅ Button disabled (no double-click)

---

### Test 3: Successful Completion

**Objective:** Verify smooth transition from loading to loaded state

**Steps:**
1. Click expand button on parent item
2. Wait for children to load
3. **OBSERVE:**
   - Skeleton row should fade out smoothly (200ms)
   - Real child rows should appear with smooth transition (300ms)
   - Chevron should remain in down position
   - Button should be re-enabled

**Expected Result:**
- Smooth transition from skeleton to real content
- No flicker or layout shift

**Pass Criteria:**
- ✅ Skeleton fades out smoothly
- ✅ Children appear smoothly
- ✅ No visual glitches
- ✅ Button re-enabled

---

### Test 4: Collapse After Expand

**Objective:** Verify collapse still works after optimistic expansion

**Steps:**
1. Expand a parent item (wait for children to load)
2. Click the same expand button again (now showing chevron-down)
3. **OBSERVE:**
   - Children should hide immediately
   - Chevron should rotate to right position
   - No HTMX request (children already loaded)

**Expected Result:**
- Instant collapse (no loading state)
- Smooth transition

**Pass Criteria:**
- ✅ Chevron rotates to right immediately
- ✅ Children hide smoothly
- ✅ No HTMX request made

---

### Test 5: Re-expand (No HTMX Request)

**Objective:** Verify second expansion uses cached children

**Steps:**
1. Expand a parent item (wait for children to load)
2. Collapse the item
3. Expand the item again
4. **OBSERVE:**
   - No spinner shown (children already loaded)
   - No skeleton row shown
   - Children appear immediately
   - Chevron rotates to down

**Expected Result:**
- Instant expand (no loading state)
- Uses cached children

**Pass Criteria:**
- ✅ No spinner or skeleton
- ✅ Children appear instantly
- ✅ No HTMX request in Network tab

---

### Test 6: Error Handling (Simulated)

**Objective:** Verify graceful error handling

**Steps:**
1. Open browser DevTools > Network tab
2. Set network throttling to "Offline"
3. Click expand button on parent item
4. **OBSERVE:**
   - Chevron rotates down immediately
   - Skeleton row appears
   - After timeout, optimistic UI should revert
   - Chevron rotates back to right
   - Skeleton row disappears
   - Error logged to console

**Expected Result:**
- Optimistic UI reverted on error
- User can retry

**Pass Criteria:**
- ✅ Optimistic UI shows initially
- ✅ Optimistic UI reverts on error
- ✅ Chevron back to right position
- ✅ Skeleton row hidden
- ✅ Button re-enabled for retry

---

### Test 7: Multiple Rapid Clicks

**Objective:** Verify button disabled state prevents double-clicks

**Steps:**
1. Find a parent item with children
2. Click expand button rapidly 5 times in succession
3. **OBSERVE:**
   - Only one HTMX request made
   - Button disabled after first click
   - No visual glitches

**Expected Result:**
- Only one expansion occurs
- Button disabled prevents duplicate requests

**Pass Criteria:**
- ✅ Only one HTMX request in Network tab
- ✅ Button disabled after first click
- ✅ No duplicate children loaded

---

### Test 8: Expand All Button

**Objective:** Verify Expand All still works with optimistic UI

**Steps:**
1. Navigate to Work Items list
2. Click "Expand All" button
3. **OBSERVE:**
   - All parent items show loading states
   - Items load sequentially (100ms delay between each)
   - Expand All icon spins during operation
   - All children visible after completion

**Expected Result:**
- All items expand successfully
- No errors in console

**Pass Criteria:**
- ✅ All parents expand
- ✅ Sequential loading works
- ✅ No console errors

---

### Test 9: Collapse All Button

**Objective:** Verify Collapse All still works

**Steps:**
1. Expand at least 2 parent items
2. Click "Collapse All" button
3. **OBSERVE:**
   - All expanded items collapse immediately
   - Chevrons rotate to right
   - Collapse All icon spins briefly

**Expected Result:**
- All items collapse instantly
- No HTMX requests (uses cached state)

**Pass Criteria:**
- ✅ All items collapse
- ✅ Instant collapse (no loading)
- ✅ No console errors

---

### Test 10: Nested Children

**Objective:** Verify optimistic UI works for nested hierarchies

**Steps:**
1. Expand a parent item with children
2. Expand a child item (that has its own children)
3. **OBSERVE:**
   - Both levels show optimistic UI correctly
   - Skeleton rows appear at correct indentation
   - No visual conflicts

**Expected Result:**
- Nested expansions work correctly
- Skeleton rows properly indented

**Pass Criteria:**
- ✅ Parent expands with optimistic UI
- ✅ Child expands with optimistic UI
- ✅ Indentation correct
- ✅ No visual conflicts

---

## Performance Testing

### Visual Feedback Timing

**Measure with DevTools Performance Tab:**

1. Open Chrome DevTools > Performance tab
2. Click "Record"
3. Click expand button
4. Stop recording after children load
5. **MEASURE:**
   - Time from click to chevron rotation
   - Time from click to skeleton row display
   - Time from click to spinner display

**Expected Timings:**
- Click to chevron rotation: < 20ms
- Click to skeleton row: < 20ms
- Click to spinner: < 20ms
- **Total perceived latency: < 50ms**

**Pass Criteria:**
- ✅ All visual changes within 50ms
- ✅ No janky frames (all 60fps)

---

### Network Simulation

**Test with Different Network Speeds:**

1. **Fast 3G (100ms latency):**
   - Skeleton visible for ~100-200ms
   - Smooth transition to content

2. **Slow 3G (300ms latency):**
   - Skeleton visible for ~300-400ms
   - Still smooth transition

3. **Offline (timeout):**
   - Optimistic UI reverts after timeout
   - Error logged to console

**Pass Criteria:**
- ✅ Works correctly on all network speeds
- ✅ Graceful degradation on timeout

---

## Accessibility Testing

### Keyboard Navigation

**Steps:**
1. Tab to expand button
2. Press Space or Enter
3. **VERIFY:**
   - Expansion works via keyboard
   - Loading state announced
   - Focus maintained on button

**Pass Criteria:**
- ✅ Space/Enter trigger expansion
- ✅ Focus management correct
- ✅ No keyboard traps

---

### Screen Reader Testing

**Test with VoiceOver (macOS) or NVDA (Windows):**

1. Navigate to expand button with screen reader
2. Activate button
3. **LISTEN FOR:**
   - "Expand/Collapse, button"
   - "Busy" state during loading
   - "Expanded" state after loading

**Pass Criteria:**
- ✅ Button labeled correctly
- ✅ Loading state announced
- ✅ Expanded state announced

---

### Color Contrast

**Verify Skeleton Rows:**
- Background: `bg-gray-200` (#E5E7EB)
- Text contrast: N/A (no text in skeleton)
- Visual distinction: Clear pulsing animation

**Pass Criteria:**
- ✅ Skeleton clearly visible
- ✅ Pulsing animation not too fast/slow
- ✅ Doesn't rely on color alone

---

## Browser Compatibility

### Desktop Browsers

**Chrome/Edge:**
- [ ] Optimistic UI works
- [ ] Animations smooth (60fps)
- [ ] HTMX requests successful

**Firefox:**
- [ ] Optimistic UI works
- [ ] Animations smooth (60fps)
- [ ] HTMX requests successful

**Safari:**
- [ ] Optimistic UI works
- [ ] Animations smooth (60fps)
- [ ] HTMX requests successful

---

### Mobile Browsers

**iOS Safari:**
- [ ] Optimistic UI works on touch
- [ ] Animations smooth
- [ ] No touch delay
- [ ] Skeleton rows visible

**Chrome Mobile (Android):**
- [ ] Optimistic UI works on touch
- [ ] Animations smooth
- [ ] No touch delay
- [ ] Skeleton rows visible

---

## Debugging Tips

### Console Logs

Look for these console messages:

**Success:**
```
✅ Work Items tree navigation initialized with optimistic UI updates (< 50ms instant feedback)
```

**Errors:**
```
❌ HTMX Swap Error: [details]
❌ HTMX Target Error: [details]
Failed to load children for item: [itemId]
Server error loading children for item: [itemId]
```

---

### Network Tab

**Check for:**
- HTMX requests to `/oobc-management/work-items/{id}/tree-partial/`
- 200 OK responses
- Response time < 500ms
- No duplicate requests for same item

---

### Elements Tab

**Inspect During Loading:**
- Button should have `disabled` attribute
- Skeleton row should have `style="display: block;"`
- Loading indicator should have `.htmx-indicator` class visible

**After Loading:**
- Skeleton row should have `style="display: none;"`
- Loading indicator hidden
- Button re-enabled

---

## Common Issues & Solutions

### Issue 1: Skeleton Row Not Showing

**Symptom:** Chevron rotates but no skeleton appears

**Check:**
- Skeleton row exists in HTML?
- `showSkeletonRow()` function called?
- CSS `display: none` overriding inline style?

**Solution:**
- Verify skeleton row template rendered
- Check `htmx:beforeRequest` event firing

---

### Issue 2: Chevron Doesn't Rotate

**Symptom:** No visual feedback on click

**Check:**
- `rotateChevronDown()` function called?
- Chevron has `.toggle-icon` class?
- JavaScript errors in console?

**Solution:**
- Verify event listener attached
- Check icon classes correct

---

### Issue 3: Button Not Disabled

**Symptom:** Can click button multiple times

**Check:**
- `hx-disabled-elt="this"` attribute present?
- HTMX version supports this attribute?

**Solution:**
- Add `hx-disabled-elt="this"` to button
- Update HTMX if needed

---

### Issue 4: Error State Not Reverting

**Symptom:** Skeleton stays visible after error

**Check:**
- `htmx:sendError` event listener attached?
- `hideSkeletonRow()` called?

**Solution:**
- Verify error event listeners present
- Check error handler logic

---

## Automated Testing

### Playwright Test Example

```javascript
test('Work Item Tree Optimistic UI', async ({ page }) => {
  await page.goto('/oobc-management/work-items/');

  // Find expand button
  const expandBtn = page.locator('[data-item-id]').first();

  // Click and measure feedback time
  const startTime = Date.now();
  await expandBtn.click();

  // Verify skeleton visible immediately
  const skeletonVisible = await page.locator('.skeleton-row').isVisible();
  const feedbackTime = Date.now() - startTime;

  expect(skeletonVisible).toBe(true);
  expect(feedbackTime).toBeLessThan(100); // < 100ms acceptable in automation

  // Wait for children to load
  await page.waitForSelector('[data-work-item-id]', { state: 'visible' });

  // Verify skeleton hidden
  const skeletonHidden = await page.locator('.skeleton-row').isHidden();
  expect(skeletonHidden).toBe(true);
});
```

---

## Test Data Requirements

### Minimum Test Data

**Required:**
- At least 3 parent work items
- Each parent should have 2-5 children
- At least 1 parent with nested children (grandchildren)

**Create Test Data:**
```bash
# Run Django management command
cd src
python manage.py create_test_work_items
```

**Or create manually:**
1. Project 1
   - Activity 1.1
   - Activity 1.2
     - Task 1.2.1
     - Task 1.2.2
2. Project 2
   - Activity 2.1
   - Activity 2.2

---

## Regression Testing

### Before Each Release

**Run these critical tests:**
1. ✅ Test 1: Instant Visual Feedback
2. ✅ Test 2: Loading State
3. ✅ Test 3: Successful Completion
4. ✅ Test 6: Error Handling
5. ✅ Test 7: Multiple Rapid Clicks

**Estimated Time:** 10 minutes

---

## Sign-Off Checklist

**Before marking as COMPLETE:**

- [ ] All 10 functional tests pass
- [ ] Performance metrics meet targets (< 50ms feedback)
- [ ] Accessibility tests pass (keyboard, screen reader)
- [ ] Works in Chrome, Firefox, Safari
- [ ] Mobile testing complete (iOS Safari, Chrome Mobile)
- [ ] No console errors
- [ ] Network simulation tests pass
- [ ] Regression tests pass

**Tested By:** ___________________________

**Date:** ___________________________

**Status:** ___________________________

---

## Resources

**Documentation:**
- [Implementation Guide](docs/improvements/UI/WORK_ITEM_TREE_OPTIMISTIC_UI_IMPLEMENTATION.md)
- [HTMX Documentation](https://htmx.org/docs/)
- [OBCMS UI Standards](docs/ui/OBCMS_UI_COMPONENTS_STANDARDS.md)

**Related Issues:**
- [Instant UI Improvements Plan](docs/improvements/instant_ui_improvements_plan.md)

**Code Files:**
- `src/templates/work_items/_work_item_tree_row.html`
- `src/templates/work_items/work_item_list.html`
- `src/common/views/work_items.py` (backend endpoint)
