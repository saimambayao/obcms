# Calendar Event Overflow - Ready-to-Use Code

**Quick Implementation Guide**
**Date:** 2025-10-06

---

## Step 1: Update FullCalendar Configuration

**File:** `/src/templates/common/oobc_calendar.html`
**Location:** Line 210 (calendar initialization)

### Add These Lines to Calendar Config:

```javascript
var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',

    // === ADD OVERFLOW CONFIGURATION HERE ===
    dayMaxEvents: 3,  // Show max 3 events + "+N more" link
    moreLinkClick: 'popover',  // Google Calendar pattern

    // === CUSTOMIZE "+N MORE" LINK ===
    moreLinkContent: function(args) {
        return {
            html: '<div class="fc-more-link-content"><i class="fas fa-plus-circle mr-1"></i><span>' + args.num + ' more</span></div>'
        };
    },

    // === ADD ACCESSIBILITY LABELS ===
    moreLinkDidMount: function(args) {
        // Add custom class
        args.el.classList.add('obcms-more-link');

        // Enhanced ARIA label
        var dateStr = args.date.toLocaleDateString('en-US', {
            month: 'long',
            day: 'numeric'
        });
        args.el.setAttribute('aria-label', 'Show ' + args.num + ' more events for ' + dateStr);
    },

    // === EXISTING CONFIGURATION (KEEP THESE) ===
    headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,listWeek'
    },
    height: 'auto',
    // ... rest of existing config
});
```

---

## Step 2: Add CSS Styling

**File:** `/src/static/common/css/calendar-enhanced.css`
**Location:** Append at end of file (after line 445)

### Copy-Paste This CSS:

```css
/* ============================================
   EVENT OVERFLOW HANDLING
   ============================================ */

/* "+N more" Link Base Styling */
.fc-daygrid-more-link {
    /* Override FullCalendar defaults */
    display: inline-flex !important;
    align-items: center !important;
    gap: 4px !important;

    /* OBCMS Design System */
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #3B82F6 !important;

    /* Compact Spacing */
    padding: 3px 8px !important;
    margin: 1px 2px !important;

    /* Modern Card Look */
    background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%) !important;
    border: 1px solid #BFDBFE !important;
    border-radius: 6px !important;

    /* Subtle Shadow */
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;

    /* Smooth Transitions */
    transition: all 0.15s ease !important;
    cursor: pointer !important;
}

/* Hover State - Lift Effect */
.fc-daygrid-more-link:hover {
    transform: translateY(-1px) !important;
    background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%) !important;
    box-shadow: 0 3px 5px rgba(59, 130, 246, 0.15),
                0 2px 3px rgba(59, 130, 246, 0.1) !important;
    color: #1D4ED8 !important;
}

/* Active State */
.fc-daygrid-more-link:active {
    transform: translateY(0) !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1) !important;
}

/* Custom Icon Styling */
.fc-more-link-content {
    display: flex;
    align-items: center;
    gap: 3px;
}

.fc-more-link-content i {
    font-size: 10px;
    opacity: 0.8;
}

/* ============================================
   EVENT POPOVER STYLING
   ============================================ */

/* Popover Container */
.fc-popover {
    /* Modern Shadow */
    box-shadow: 0 20px 25px rgba(0, 0, 0, 0.15),
                0 10px 10px rgba(0, 0, 0, 0.1),
                0 0 0 1px rgba(0, 0, 0, 0.05) !important;

    /* Rounded Corners */
    border-radius: 12px !important;
    border: 1px solid #E5E7EB !important;

    /* Smooth Animation */
    animation: popoverFadeIn 0.2s ease-out !important;

    /* Max Width for Readability */
    max-width: 400px !important;

    /* Ensure z-index above everything */
    z-index: 9999 !important;
}

/* Popover Header */
.fc-popover-header {
    /* OBCMS Gradient */
    background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
    color: white !important;

    /* Typography */
    font-weight: 600 !important;
    font-size: 13px !important;

    /* Padding */
    padding: 10px 14px !important;

    /* Top Rounded Corners */
    border-radius: 12px 12px 0 0 !important;
}

/* Popover Title */
.fc-popover-title {
    color: white !important;
    font-weight: 600 !important;
}

/* Close Button */
.fc-popover-close {
    color: white !important;
    opacity: 0.9 !important;
    cursor: pointer !important;
    transition: opacity 0.2s ease !important;
    font-size: 16px !important;
}

.fc-popover-close:hover {
    opacity: 1 !important;
}

/* Popover Body */
.fc-popover-body {
    /* Clean Background */
    background: white !important;

    /* Padding */
    padding: 8px !important;

    /* Max Height with Scroll */
    max-height: 400px !important;
    overflow-y: auto !important;

    /* Bottom Rounded Corners */
    border-radius: 0 0 12px 12px !important;
}

/* Scrollbar Styling for Popover */
.fc-popover-body::-webkit-scrollbar {
    width: 6px;
}

.fc-popover-body::-webkit-scrollbar-track {
    background: #F3F4F6;
    border-radius: 0 0 12px 0;
}

.fc-popover-body::-webkit-scrollbar-thumb {
    background: #D1D5DB;
    border-radius: 3px;
}

.fc-popover-body::-webkit-scrollbar-thumb:hover {
    background: #9CA3AF;
}

/* Events Inside Popover - Maintain Compact Style */
.fc-popover .fc-event {
    /* Keep compact spacing */
    margin-bottom: 3px !important;
    padding: 4px 6px !important;
    font-size: 12px !important;
    max-height: none !important; /* Allow natural height in popover */
}

/* Last event in popover - no margin */
.fc-popover .fc-event:last-child {
    margin-bottom: 0 !important;
}

/* Popover Fade-In Animation */
@keyframes popoverFadeIn {
    from {
        opacity: 0;
        transform: translateY(-8px) scale(0.95);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

/* ============================================
   RESPONSIVE ADJUSTMENTS
   ============================================ */

/* Mobile: Smaller Popover */
@media (max-width: 768px) {
    .fc-popover {
        max-width: calc(100vw - 32px) !important;
        position: fixed !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
    }

    .fc-popover-body {
        max-height: 300px !important;
    }

    .fc-daygrid-more-link {
        font-size: 10px !important;
        padding: 2px 6px !important;
    }
}

/* Tablet: Medium Popover */
@media (min-width: 769px) and (max-width: 1024px) {
    .fc-popover {
        max-width: 360px !important;
    }
}

/* ============================================
   ACCESSIBILITY ENHANCEMENTS
   ============================================ */

/* Keyboard Focus for "+N more" Link */
.fc-daygrid-more-link:focus-visible {
    outline: 3px solid #3B82F6 !important;
    outline-offset: 2px !important;
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2) !important;
}

/* High Contrast Mode */
@media (prefers-contrast: high) {
    .fc-daygrid-more-link {
        border-width: 2px !important;
        font-weight: 700 !important;
    }
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
    .fc-daygrid-more-link,
    .fc-popover {
        animation: none !important;
        transition: none !important;
    }
}

/* ============================================
   PRINT STYLES
   ============================================ */

@media print {
    /* Hide "+N more" links in print */
    .fc-daygrid-more-link {
        display: none !important;
    }

    /* Show all events when printing */
    .fc-event {
        page-break-inside: avoid !important;
    }
}
```

---

## Step 3: Responsive Breakpoints (Optional Enhancement)

**Add to calendar JavaScript (after calendar initialization):**

```javascript
// Responsive event limit based on screen size
function updateEventLimit() {
    var width = window.innerWidth;
    var newLimit = width < 768 ? 2 : width < 1024 ? 3 : 4;
    calendar.setOption('dayMaxEvents', newLimit);
}

// Set initial limit
updateEventLimit();

// Update on resize (debounced)
var resizeTimer;
window.addEventListener('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(updateEventLimit, 250);
});
```

---

## Step 4: Testing Checklist

### Create Test Data (Django Shell):

```python
# Run in terminal
python src/manage.py shell

# Create 15 events on same day
from common.models import WorkItem
from django.utils import timezone
from datetime import timedelta

base_date = timezone.now().date()
for i in range(15):
    WorkItem.objects.create(
        title=f"Test Event {i+1}",
        work_type='task',
        start_date=base_date,
        created_by_id=1  # Use your user ID
    )
```

### Verify Functionality:

1. **Desktop View (1440px):**
   - ✅ See 3 events visible
   - ✅ See "+12 more" link
   - ✅ Click link → Popover opens
   - ✅ Events are clickable in popover
   - ✅ Close button works
   - ✅ Click outside closes popover
   - ✅ Press Escape closes popover

2. **Tablet View (768px):**
   - ✅ See 3 events visible
   - ✅ "+N more" link smaller

3. **Mobile View (375px):**
   - ✅ See 2 events visible
   - ✅ Popover centered on screen
   - ✅ Popover fits screen width

4. **Accessibility:**
   - ✅ Tab to "+N more" link
   - ✅ Enter opens popover
   - ✅ Screen reader announces count
   - ✅ High contrast mode visible

---

## Step 5: Production Deployment

### Before Deploying:

```bash
# 1. Test with real data (100+ events)
# 2. Test all browsers (Chrome, Firefox, Safari, Edge)
# 3. Test all devices (Desktop, Tablet, Mobile)
# 4. Run accessibility audit (Lighthouse, axe DevTools)
```

### Deploy:

```bash
# 1. Commit changes
git add src/templates/common/oobc_calendar.html
git add src/static/common/css/calendar-enhanced.css
git commit -m "Add calendar event overflow handling

- Implement dayMaxEvents: 3 (Google Calendar pattern)
- Add custom '+N more' link styling
- Create popover with OBCMS design system
- Add responsive breakpoints (mobile: 2, tablet: 3, desktop: 4)
- Ensure WCAG 2.1 AA accessibility compliance

Fixes: Calendar overflow with 10+ events per day
Ref: docs/improvements/UI/CALENDAR_EVENT_OVERFLOW_STRATEGY.md"

# 2. Push to staging
git push origin staging

# 3. Test in staging
# 4. Push to production
git push origin main
```

---

## Troubleshooting

### Issue: "+N more" link not showing
**Solution:** Check `dayMaxEvents` configuration is set correctly

### Issue: Popover not styled
**Solution:** Verify CSS file is loaded, check browser DevTools

### Issue: Popover appears behind other elements
**Solution:** Add `z-index: 9999 !important;` to `.fc-popover`

### Issue: Events in popover not clickable
**Solution:** Ensure `eventClick` handler is still working (existing code)

### Issue: Mobile popover too large
**Solution:** Check responsive CSS is applied (`@media (max-width: 768px)`)

---

## Quick Reference

### Configuration Summary:

| Setting | Value | Purpose |
|---------|-------|---------|
| `dayMaxEvents` | `3` | Show max 3 events + link |
| `moreLinkClick` | `'popover'` | Google Calendar pattern |
| Mobile limit | `2` | Smaller screens show less |
| Tablet limit | `3` | Medium screens |
| Desktop limit | `4` | Large screens show more |

### Key Files Modified:

1. `/src/templates/common/oobc_calendar.html` (Lines 210-220)
2. `/src/static/common/css/calendar-enhanced.css` (Lines 446-700)

### Estimated Implementation Time:

- ✅ Copy-paste code: 5 minutes
- ✅ Test functionality: 10 minutes
- ✅ Create test data: 5 minutes
- ✅ Total: 20 minutes

---

## Success Criteria

✅ Calendar shows max 3-4 events per day
✅ "+N more" link appears when overflow
✅ Popover opens with all events
✅ Popover matches OBCMS design system
✅ Mobile responsive (2 events on small screens)
✅ Keyboard accessible (Tab, Enter, Escape)
✅ Screen reader announces event counts
✅ WCAG 2.1 AA compliant

---

**END OF IMPLEMENTATION GUIDE**
