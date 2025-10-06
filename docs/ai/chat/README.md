# AI Chat Documentation

**Directory:** `docs/ai/chat/`
**Purpose:** Troubleshooting, status tracking, and operational guides for the AI Chat system

---

## Quick Links

- **[STATUS.md](STATUS.md)** ⭐ Check here first for current system status
- **[TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md)** 🔧 Detailed solutions for common issues

---

## Current Status

**Last Updated:** 2025-10-06 15:35

| Component | Status |
|-----------|--------|
| Chat UI | ✅ WORKING |
| CSRF Auth | ✅ FIXED |
| Gemini API | ⚠️ QUOTA EXCEEDED |
| Data Queries | ❌ BLOCKED |

**Critical Issue:** Gemini API quota exhausted (250/day free tier limit)

**See:** [STATUS.md](STATUS.md) for full details

---

## Common Issues & Solutions

### Issue 1: 403 Forbidden Error ✅ FIXED
**Symptom:** Chat POST requests return 403 Forbidden
**Solution:** CSRF token now properly included in requests
**Status:** RESOLVED

### Issue 2: 429 Quota Exceeded ⚠️ ACTIVE
**Symptom:** "I couldn't process your question" error message
**Root Cause:** Gemini API free tier limit (250 req/day) exhausted
**Solutions:**
1. Upgrade to paid tier (~$24/month) ← RECOMMENDED
2. Implement local database fallback (free, limited)
3. Wait 24 hours for quota reset (testing only)

**See:** [TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md#option-1-upgrade-gemini-api-to-paid-tier-recommended)

---

## Testing Quick Start

### Test CSRF Token (Should Pass)
```bash
# 1. Start server
cd src && python manage.py runserver

# 2. Open http://localhost:8000/
# 3. Open browser console (F12)
# 4. Send chat message: "hello"
# 5. Verify: "✅ CSRF token added to POST request"
```

### Test Data Query (Currently Blocked)
```bash
# Send: "How many communities are in Region IX?"
# Expected: "There are X communities in Region IX."
# Current: "I couldn't process your question." (429 error)
```

### Test Help Command (Should Pass)
```bash
# Send: "help"
# Expected: List of available commands
# Status: WORKING (no API needed)
```

---

## Implementation Details

### Architecture
```
User → Chat Widget (JS)
         ↓ POST /chat/
      Chat View (Django)
         ↓
      Chat Engine
         ↓
      Gemini API ← QUOTA EXHAUSTED HERE
         ↓
      Response → User
```

### Key Files
- **Frontend:** `src/static/common/js/chat-widget.js`
- **Backend:** `src/common/views/chat.py`
- **AI Engine:** `src/common/ai_services/chat/chat_engine.py`
- **Gemini Service:** `src/ai_assistant/services/gemini_service.py`
- **Models:** `src/common/models/chat.py`

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] Upgrade Gemini API to paid tier
- [ ] Set `GEMINI_API_KEY` in production `.env`
- [ ] Test all query types
- [ ] Verify CSRF token in production domain
- [ ] Enable monitoring and alerts
- [ ] Load test (50 concurrent users)
- [ ] Document rollback procedure

### Cost Estimation
- **Users:** 100 staff
- **Queries:** 10/user/day × 22 days = 22,000/month
- **Cost:** ~$2.15/month (actual usage)
- **Budget:** $24/month (10x safety buffer)

**See:** [TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md#production-readiness-checklist)

---

## Support & Escalation

### Step 1: Check Status
Read [STATUS.md](STATUS.md) for current system state

### Step 2: Review Troubleshooting
Read [TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md) for solutions

### Step 3: Test Components
- CSRF token: Should work ✅
- Help command: Should work ✅
- Data queries: Blocked by quota ⚠️

### Step 4: Decision Required
Choose upgrade path (paid API vs local fallback)

---

## Recent Changes

**2025-10-06:**
- ✅ Fixed CSRF token authentication
- ⚠️ Identified Gemini API quota exhaustion
- 📝 Created comprehensive troubleshooting guide
- 📋 Documented local fallback implementation plan

---

## Related Documentation

### In This Directory
- [STATUS.md](STATUS.md) - Current system status
- [TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md) - Detailed troubleshooting

### Parent Directory (`docs/ai/`)
- [AI_CHAT_QUICK_REFERENCE.md](../AI_CHAT_QUICK_REFERENCE.md) - User guide
- [GEMINI_CHAT_SERVICE_GUIDE.md](../GEMINI_CHAT_SERVICE_GUIDE.md) - Technical architecture
- [CHAT_WIDGET_INTEGRATION_GUIDE.md](../CHAT_WIDGET_INTEGRATION_GUIDE.md) - Frontend integration
- [AI_PRODUCTION_READINESS_ASSESSMENT.md](../AI_PRODUCTION_READINESS_ASSESSMENT.md) - Full assessment

### Root Documentation
- [Main AI README](../README.md) - AI system overview
- [CLAUDE.md](../../../CLAUDE.md) - Development guidelines

---

## Quick Command Reference

```bash
# Start development server
cd src && python manage.py runserver

# Check API quota (browser)
open https://aistudio.google.com/app/apikey

# View logs
cd src && tail -f logs/django.log

# Test chat endpoint
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <token>" \
  -d '{"message": "help"}'

# Enable debug logging
# Edit: src/obc_management/settings/development.py
# Set: LOGGING['loggers']['ai_assistant']['level'] = 'DEBUG'
```

---

**For current status and blocking issues, see [STATUS.md](STATUS.md)**
