# Calendar Overflow - Quick Reference Card

**One-Page Implementation Guide**
**Date:** 2025-10-06

---

## 🚀 Quick Setup (5 Minutes)

### 1. Add to Calendar Config (Line 210)
```javascript
var calendar = new FullCalendar.Calendar(calendarEl, {
    dayMaxEvents: 3,          // Show max 3 events + link
    moreLinkClick: 'popover', // Google Calendar pattern
    // ... rest of config
});
```

### 2. Add CSS (End of calendar-enhanced.css)
```css
/* "+N more" Link */
.fc-daygrid-more-link {
    display: inline-flex !important;
    align-items: center !important;
    gap: 4px !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #3B82F6 !important;
    padding: 3px 8px !important;
    margin: 1px 2px !important;
    background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%) !important;
    border: 1px solid #BFDBFE !important;
    border-radius: 6px !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
    transition: all 0.15s ease !important;
    cursor: pointer !important;
}

.fc-daygrid-more-link:hover {
    transform: translateY(-1px) !important;
    background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%) !important;
    box-shadow: 0 3px 5px rgba(59, 130, 246, 0.15) !important;
    color: #1D4ED8 !important;
}

/* Popover */
.fc-popover {
    box-shadow: 0 20px 25px rgba(0, 0, 0, 0.15) !important;
    border-radius: 12px !important;
    border: 1px solid #E5E7EB !important;
    animation: popoverFadeIn 0.2s ease-out !important;
    max-width: 400px !important;
    z-index: 9999 !important;
}

.fc-popover-header {
    background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 10px 14px !important;
    border-radius: 12px 12px 0 0 !important;
}

.fc-popover-body {
    background: white !important;
    padding: 8px !important;
    max-height: 400px !important;
    overflow-y: auto !important;
    border-radius: 0 0 12px 12px !important;
}

@keyframes popoverFadeIn {
    from { opacity: 0; transform: translateY(-8px) scale(0.95); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}
```

### 3. Test
```python
# Create 15 test events
python src/manage.py shell
from common.models import WorkItem
from django.utils import timezone

base_date = timezone.now().date()
for i in range(15):
    WorkItem.objects.create(
        title=f"Test Event {i+1}",
        work_type='task',
        start_date=base_date,
        created_by_id=1
    )
```

✅ **Done!** Reload calendar, see "+12 more" link.

---

## 📊 Configuration Options

| Setting | Options | Recommendation |
|---------|---------|----------------|
| `dayMaxEvents` | `true`, `2`, `3`, `4`, etc. | Use `3` for optimal balance |
| `moreLinkClick` | `'popover'`, `'week'`, `'day'`, `function` | Use `'popover'` (Google Calendar) |
| Mobile limit | Dynamic | `2` for < 768px |
| Tablet limit | Dynamic | `3` for 768-1023px |
| Desktop limit | Dynamic | `4` for 1024px+ |

---

## 🎨 Design Specs

### "+N more" Link
- **Font:** 11px, weight 600
- **Color:** #3B82F6 (blue-600)
- **Background:** Gradient #EFF6FF → #DBEAFE
- **Padding:** 3px 8px
- **Border:** 1px #BFDBFE
- **Radius:** 6px
- **Hover:** Lift 1px, darker gradient

### Popover
- **Max Width:** 400px (desktop), 100vw-32px (mobile)
- **Max Height:** 400px (desktop), 300px (mobile)
- **Header:** Gradient #3B82F6 → #2563EB
- **Body:** White, scrollable
- **Radius:** 12px
- **Shadow:** 0 20px 25px rgba(0,0,0,0.15)

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Tab` | Focus "+N more" link |
| `Enter` / `Space` | Open popover |
| `Tab` (in popover) | Navigate events |
| `Escape` | Close popover |

---

## 📱 Responsive Breakpoints

```javascript
// Desktop (1024px+): 4 events
// Tablet (768-1023px): 3 events
// Mobile (< 768px): 2 events

var isMobile = window.innerWidth < 768;
var isTablet = window.innerWidth >= 768 && window.innerWidth < 1024;

calendar.setOption('dayMaxEvents',
    isMobile ? 2 : isTablet ? 3 : 4
);
```

---

## ✅ Testing Checklist

### Desktop
- [ ] See 3-4 events visible
- [ ] "+N more" link appears when > limit
- [ ] Click link → Popover opens
- [ ] Events clickable in popover
- [ ] Close button works
- [ ] Click outside closes
- [ ] Escape closes

### Mobile (375px)
- [ ] See 2 events max
- [ ] Popover centered, full-width
- [ ] Touch-friendly tap targets
- [ ] Smooth scrolling

### Accessibility
- [ ] Tab to "+N more" link
- [ ] Focus ring visible (blue)
- [ ] Enter opens popover
- [ ] Screen reader announces count
- [ ] High contrast mode works

---

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| Link not showing | Check `dayMaxEvents: 3` is set |
| Popover not styled | Verify CSS loaded, check DevTools |
| Popover behind elements | Add `z-index: 9999 !important` |
| Events not clickable | Check `eventClick` handler exists |
| Mobile too large | Check responsive CSS applied |

---

## 📂 Files Modified

1. **`/src/templates/common/oobc_calendar.html`** (Line 210)
   - Add `dayMaxEvents: 3`
   - Add `moreLinkClick: 'popover'`

2. **`/src/static/common/css/calendar-enhanced.css`** (End of file)
   - Add "+N more" link styles
   - Add popover styles
   - Add responsive styles

---

## 🎯 Success Criteria

✅ Calendar shows max 3-4 events/day
✅ "+N more" appears on overflow
✅ Popover matches OBCMS design
✅ Mobile responsive (2 events)
✅ Keyboard accessible
✅ WCAG 2.1 AA compliant

---

## 📚 Full Documentation

- **Strategy:** `/docs/improvements/UI/CALENDAR_EVENT_OVERFLOW_STRATEGY.md`
- **Code:** `/docs/improvements/UI/CALENDAR_OVERFLOW_IMPLEMENTATION_CODE.md`
- **UX Flow:** `/docs/improvements/UI/CALENDAR_OVERFLOW_UX_FLOW.md`
- **Quick Reference:** This document

---

## 🚢 Deployment Command

```bash
git add src/templates/common/oobc_calendar.html
git add src/static/common/css/calendar-enhanced.css
git commit -m "Add calendar event overflow handling

- Implement dayMaxEvents: 3 (Google Calendar pattern)
- Add custom '+N more' link styling
- Create popover with OBCMS design
- Responsive: mobile(2), tablet(3), desktop(4)
- WCAG 2.1 AA accessibility compliant

Fixes: Calendar overflow with 10+ events per day"
git push origin main
```

---

**IMPLEMENTATION TIME: 5-10 MINUTES**
**EXPECTED IMPACT: CRITICAL UX IMPROVEMENT**

---

**END OF QUICK REFERENCE**
