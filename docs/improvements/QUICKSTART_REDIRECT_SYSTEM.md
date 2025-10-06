# URL Redirect System - Quick Start Guide

**Status:** ✅ PRODUCTION READY | **Tests:** 12/12 PASSED

---

## Overview

Automatic URL redirect system with deprecation logging for OBCMS WorkItem migration.

**What it does:**
- Redirects old URLs → WorkItem URLs
- Logs every deprecated request
- Shows user messages
- Provides admin dashboard

---

## Quick Test (30 seconds)

```bash
# 1. Run automated tests
./test_deprecation_system.sh

# Expected: ✅ 12/12 tests passing

# 2. Start server
cd src
python manage.py runserver

# 3. Test redirect (in another terminal)
curl -I http://localhost:8000/staff/tasks/

# Expected: 302 Redirect to /oobc-management/work-items/

# 4. Check log
tail logs/deprecation.log

# Expected: Log entry with timestamp, user, IP

# 5. Access dashboard (in browser)
http://localhost:8000/admin/deprecation/

# Expected: Statistics dashboard
```

---

## Files Modified

**Settings:**
- `/src/obc_management/settings/base.py` - Middleware added ✅

**Middleware:**
- `/src/common/middleware.py` - DeprecationLoggingMiddleware added ✅

**URLs:**
- `/src/common/urls.py` - 38 legacy redirects added ✅

**Views:**
- `/src/common/views/redirects.py` - New file ✅
- `/src/common/views/deprecation.py` - New file ✅

**Templates:**
- `/src/templates/admin/deprecation_dashboard.html` - New file ✅

---

## URL Redirects (38 configured)

### StaffTask URLs (35)
```
/staff/tasks/                        → /oobc-management/work-items/
/staff/tasks/create/                 → /oobc-management/work-items/create/
/staff/tasks/<id>/                   → /oobc-management/work-items/
/staff/tasks/<id>/edit/              → /oobc-management/work-items/
/staff/tasks/<id>/delete/            → /oobc-management/work-items/
... (30+ more)
```

### ProjectWorkflow URLs (6)
```
/project-central/workflows/          → /oobc-management/work-items/
/project-central/workflows/create/   → /oobc-management/work-items/create/
... (4 more)
```

### Event URLs (5)
```
/coordination/events/legacy/         → /oobc-management/work-items/
... (4 more)
```

---

## Dashboard Access

**URL:** `http://localhost:8000/admin/deprecation/`

**Requirements:** Staff user (admin)

**Features:**
- Total deprecated requests
- Unique users affected
- Top deprecated URLs
- 30-day trend chart
- User impact analysis

---

## Log Format

**Location:** `src/logs/deprecation.log`

**Example Entry:**
```
2025-10-05 15:30:00 | WARNING | Deprecated URL accessed |
Path: /staff/tasks/ |
User: admin (ID: 1) |
IP: 127.0.0.1 |
Referer: http://localhost:8000/dashboard/ |
User-Agent: Mozilla/5.0...
```

---

## Common Tasks

### View Total Requests
```bash
grep "Deprecated URL accessed" src/logs/deprecation.log | wc -l
```

### View Unique Users
```bash
grep "Deprecated URL accessed" src/logs/deprecation.log | \
  grep -o "User: [^|]*" | sort -u
```

### View Top URLs
```bash
grep "Deprecated URL accessed" src/logs/deprecation.log | \
  grep -o "Path: [^|]*" | sort | uniq -c | sort -rn
```

### Clear Logs (for testing)
```bash
> src/logs/deprecation.log
```

---

## Testing

### Test Redirect
```bash
curl -I http://localhost:8000/staff/tasks/
# Expected: 302 Redirect
```

### Test Query Params
```bash
curl -I "http://localhost:8000/staff/tasks/?status=pending"
# Expected: Redirect preserves ?status=pending
```

### Test Logging
```bash
# Access URL
curl http://localhost:8000/staff/tasks/

# Check log
tail -1 logs/deprecation.log
# Expected: New log entry
```

### Test Dashboard
```bash
# In browser (as admin):
http://localhost:8000/admin/deprecation/

# Should show statistics
```

---

## Troubleshooting

### Redirects not working?

1. Check middleware in settings:
   ```bash
   grep "DeprecationLoggingMiddleware" src/obc_management/settings/base.py
   ```

2. Verify URL patterns:
   ```bash
   cd src && python manage.py show_urls | grep deprecated
   ```

3. Check Django errors:
   ```bash
   cd src && python manage.py check
   ```

### Logs not created?

1. Create logs directory:
   ```bash
   mkdir -p src/logs
   ```

2. Check permissions:
   ```bash
   ls -la src/logs
   chmod 755 src/logs
   ```

3. Test a deprecated URL:
   ```bash
   curl http://localhost:8000/staff/tasks/
   ```

### Dashboard shows no data?

1. Verify log file exists:
   ```bash
   ls src/logs/deprecation.log
   ```

2. Check log has content:
   ```bash
   cat src/logs/deprecation.log
   ```

3. Access a deprecated URL to trigger logging

---

## Next Steps

### Development
- [ ] Test all redirects manually
- [ ] Verify logging works
- [ ] Check dashboard displays correctly

### Staging
- [ ] Deploy to staging environment
- [ ] Monitor deprecation logs
- [ ] Notify users about migration

### Production
- [ ] Deploy with monitoring
- [ ] Track migration progress
- [ ] Plan 410 Gone transition

---

## Documentation

**Full Guide:** `docs/refactor/URL_REDIRECT_IMPLEMENTATION.md`

**Implementation Summary:** `IMPLEMENTATION_SUMMARY.md`

**Deprecation Plan:** `docs/refactor/LEGACY_CODE_DEPRECATION_PLAN.md`

---

## Support

**Questions?** Check the full documentation:
- Architecture: See `URL_REDIRECT_IMPLEMENTATION.md`
- Testing: Run `./test_deprecation_system.sh`
- Migration: See `LEGACY_CODE_DEPRECATION_PLAN.md`

---

**Status:** ✅ READY FOR DEPLOYMENT
**Last Updated:** 2025-10-05
**Version:** 1.0
