# Calendar Compact Layout Testing Guide

**Quick Start:** Hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R) after deployment

## Visual Inspection Checklist

### 1. Event Height Test
**Expected:** Events should be ~28-32px tall (about 2 lines of text height)

**How to Test:**
1. Navigate to calendar page
2. Right-click on any event → Inspect
3. Check computed height in DevTools
4. **PASS**: Height is 22-32px
5. **FAIL**: Height is > 35px

**What to Look For:**
```
✅ GOOD: Event is single-line height with minimal padding
❌ BAD: Event takes 40-50px (thick rectangular blocks)
```

### 2. Inline Layout Test
**Expected:** All content (title, badges, time) should be on ONE line

**How to Test:**
1. Find an event with badges (recurring, project, etc.)
2. Observe layout
3. **PASS**: All elements are side-by-side (horizontal)
4. **FAIL**: Badges stack below title (vertical)

**What to Look For:**
```
✅ GOOD: [Icon] Title [Badge] [Badge] [Time]
❌ BAD: [Icon] Title
        [Badge]
        [Badge]
        [Time]
```

### 3. Text Readability Test
**Expected:** Dark text on light backgrounds, good contrast

**How to Test:**
1. View events in different categories (project, activity, task)
2. Check text is easily readable
3. **PASS**: Text has 4.5:1 contrast ratio
4. **FAIL**: Text is washed out or hard to read

**Color Combinations:**
- Project (Blue): Dark blue text on light blue background ✅
- Activity (Emerald): Dark green text on light green background ✅
- Task (Purple): Dark purple text on light purple background ✅

### 4. Badge Compactness Test
**Expected:** Badges should be small pills (~8-9px font, minimal padding)

**How to Test:**
1. Find events with multiple badges
2. Check badge size
3. **PASS**: Badges are compact, don't dominate event
4. **FAIL**: Badges are larger than event title

**What to Look For:**
```
✅ GOOD: Small badges (font-size: 8-9px, padding: 1px 4px)
❌ BAD: Large badges (font-size: 10-12px, padding: 4px 8px)
```

### 5. Hover State Test
**Expected:** Subtle shadow increase, NO vertical movement

**How to Test:**
1. Hover over event
2. Observe shadow changes
3. **PASS**: Shadow intensifies, event stays in place
4. **FAIL**: Event jumps up 2px (old transform behavior)

**What to Look For:**
```
✅ GOOD: Shadow increases, no movement
❌ BAD: Event "lifts up" on hover (transform: translateY(-2px))
```

### 6. Multiple Events Test
**Expected:** Can see 5-10+ events per day without scrolling (month view)

**How to Test:**
1. Navigate to month view
2. Find day with multiple events
3. Count visible events
4. **PASS**: Can see 6+ events comfortably
5. **FAIL**: Only 2-3 events visible, rest hidden

**Density Check:**
```
✅ GOOD: 8-10 events visible per day cell
❌ BAD: Only 2-3 events visible, "+5 more" link
```

### 7. Mobile Responsive Test
**Expected:** Events remain compact on mobile (< 768px)

**How to Test:**
1. Open DevTools → Toggle device toolbar
2. Select iPhone/Android device
3. Check event height and readability
4. **PASS**: Events are 20-28px tall, text readable
5. **FAIL**: Events are too small or overlap

**Mobile Metrics:**
- Event height: 20-28px
- Font size: 11px
- Badge font: 8px
- Padding: 2px 4px

### 8. Long Title Test
**Expected:** Long titles truncate with ellipsis (...)

**How to Test:**
1. Find/create event with very long title
2. Check if title wraps or truncates
3. **PASS**: Title truncates with "..." and tooltip shows full text
4. **FAIL**: Title wraps to multiple lines, breaks layout

**What to Look For:**
```
✅ GOOD: "Very long event title that g..." [tooltip on hover]
❌ BAD: "Very long event title that goes
         on and on and on..."
```

## Browser Testing Matrix

### Desktop Browsers
| Browser | Version | Status | Notes |
|---------|---------|--------|-------|
| Chrome | Latest | ✅ | Primary development browser |
| Firefox | Latest | ✅ | Test flexbox rendering |
| Safari | Latest | ✅ | Test on macOS |
| Edge | Latest | ✅ | Chromium-based, should match Chrome |

### Mobile Browsers
| Browser | Device | Status | Notes |
|---------|--------|--------|-------|
| Safari iOS | iPhone | ✅ | Test on iOS 15+ |
| Chrome Android | Pixel/Samsung | ✅ | Test on Android 10+ |
| Firefox Mobile | Android | ✅ | Alternative rendering engine |

## Common Issues & Fixes

### Issue 1: Events Still Too Tall
**Symptom:** Events are 40-50px tall after fix
**Diagnosis:** CSS not loaded or cache issue
**Fix:**
```bash
# Hard refresh browser
Ctrl+Shift+R (Windows)
Cmd+Shift+R (Mac)

# Or clear cache completely
Chrome: Settings → Privacy → Clear browsing data → Cached images and files
```

### Issue 2: Vertical Stacking Persists
**Symptom:** Badges still stack below title
**Diagnosis:** Old CSS still cached or missing flex properties
**Fix:**
1. Inspect element in DevTools
2. Check if `display: flex` is applied to `.fc-event-title-container`
3. If not, clear cache and hard refresh

### Issue 3: Text Unreadable
**Symptom:** Text too light or wrong color
**Diagnosis:** Color override conflict
**Fix:**
1. Check for custom CSS overriding event colors
2. Verify `calendar-enhanced.css` loads AFTER other CSS
3. Increase specificity if needed (add `!important`)

### Issue 4: Events Too Small on Mobile
**Symptom:** Text too small to read on phone
**Diagnosis:** Mobile breakpoint not applied
**Fix:**
1. Check if viewport meta tag exists in `<head>`
2. Verify media query triggers at 768px
3. Test actual device vs. DevTools emulation

## Performance Testing

### Page Load Test
**Expected:** Calendar renders in < 2 seconds

**How to Test:**
1. Open DevTools → Network tab
2. Reload page
3. Check `calendar-enhanced.css` load time
4. **PASS**: < 100ms load time
5. **FAIL**: > 500ms load time

### Interaction Test
**Expected:** Hover/click responds in < 100ms

**How to Test:**
1. Open DevTools → Performance tab
2. Record interaction
3. Hover over events, click events
4. Check frame rate (should be 60fps)
5. **PASS**: Smooth 60fps, no jank
6. **FAIL**: Frame drops, sluggish

## Accessibility Testing

### Keyboard Navigation Test
1. Tab through calendar
2. Focus on events (should show focus outline)
3. Press Enter to open event
4. **PASS**: Can navigate and activate with keyboard
5. **FAIL**: Focus invisible or keyboard doesn't work

### Screen Reader Test
1. Enable screen reader (VoiceOver, NVDA, JAWS)
2. Navigate to calendar
3. Focus on events
4. **PASS**: Screen reader announces event details
5. **FAIL**: Screen reader silent or confusing

### Color Contrast Test
1. Use DevTools → Lighthouse
2. Run accessibility audit
3. Check for contrast errors
4. **PASS**: No contrast errors (4.5:1 minimum)
5. **FAIL**: Contrast warnings/errors

## Regression Testing

### Features to Verify Still Work
- ✅ Event click opens modal
- ✅ Drag and drop to reschedule
- ✅ Create new event
- ✅ Edit event
- ✅ Delete event
- ✅ Filter by category
- ✅ Switch between month/week/day views
- ✅ Navigate between months
- ✅ Today button returns to current date
- ✅ Export to iCal/CSV
- ✅ Print calendar

## Sign-Off Checklist

Before marking as complete, verify:
- [ ] All visual tests pass
- [ ] Tested on Chrome, Firefox, Safari
- [ ] Tested on mobile device (iOS or Android)
- [ ] Events are 22-32px tall
- [ ] Inline layout (no vertical stacking)
- [ ] Text is readable (4.5:1 contrast)
- [ ] Badges are compact (8-9px font)
- [ ] Hover works without transform jump
- [ ] Long titles truncate with ellipsis
- [ ] 6+ events visible per day (month view)
- [ ] Mobile responsive works (< 768px)
- [ ] Keyboard navigation intact
- [ ] Screen reader announces events
- [ ] No regression in functionality
- [ ] Performance is smooth (60fps)

## Quick DevTools Verification

Open browser console and run:
```javascript
// Check event height
const event = document.querySelector('.fc-event');
const height = event ? window.getComputedStyle(event).height : 'No events found';
console.log('Event height:', height); // Should be ~22-32px

// Check padding
const padding = event ? window.getComputedStyle(event).padding : 'No events found';
console.log('Event padding:', padding); // Should be "2px 6px"

// Check display mode
const display = event ? window.getComputedStyle(event).display : 'No events found';
console.log('Event display:', display); // Should be "flex"

// Check title container
const titleContainer = document.querySelector('.fc-event-title-container');
const titleDisplay = titleContainer ? window.getComputedStyle(titleContainer).display : 'Not found';
console.log('Title container display:', titleDisplay); // Should be "flex"
```

Expected output:
```
Event height: 28px
Event padding: 2px 6px
Event display: flex
Title container display: flex
```

## Rollback Procedure

If critical issues found:

1. **Immediate Rollback:**
```bash
cd src/static/common/css
git checkout HEAD~1 calendar-enhanced.css
```

2. **Restore from backup:**
```bash
# If you made a backup before changes
cp calendar-enhanced.css.backup calendar-enhanced.css
```

3. **Hard refresh all browsers**

4. **Report issue** with:
   - Browser/version
   - Screenshot
   - Console errors
   - Steps to reproduce

---

**Testing Completed By:** ___________________
**Date:** ___________________
**Result:** ✅ PASS / ❌ FAIL (with notes)
**Notes:** ___________________
