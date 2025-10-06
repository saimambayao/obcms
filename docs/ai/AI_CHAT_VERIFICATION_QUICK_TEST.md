# AI Chat - Quick Verification Test

## Issue
You're seeing "AI Chat Coming Soon" because your browser cached the old version.

## Solution

### Step 1: Hard Refresh Browser
**Mac:** `Cmd + Shift + R`
**Windows:** `Ctrl + Shift + F5`

### Step 2: Verify Chat Form Appeared

After refreshing, click the green chat button. You should see:

**❌ OLD VERSION (Cached):**
```
┌─────────────────────────────┐
│ AI Assistant           Beta │
├─────────────────────────────┤
│ Hello! I'm your AI...       │
│                             │
├─────────────────────────────┤
│   🔧 AI Chat Coming Soon    │
│   Backend integration...    │
└─────────────────────────────┘
```

**✅ NEW VERSION (After Refresh):**
```
┌─────────────────────────────┐
│ AI Assistant           Beta │
├─────────────────────────────┤
│ Hello! I'm your AI...       │
│                             │
├─────────────────────────────┤
│ [Type your message...] [>]  │  ← INPUT FORM
└─────────────────────────────┘
```

### Step 3: Test AI Chat

**Type a test message:**
```
How many communities are in Region IX?
```

**Expected Behavior:**
1. Your message appears immediately (blue bubble, right side)
2. Loading spinner shows "Thinking..."
3. AI response appears (white bubble with emerald border, left side)
4. Response includes data + follow-up suggestions

**Example Expected Response:**
```
Based on the latest data in OBCMS, there are 47 Bangsamoro
communities identified in Region IX (Zamboanga Peninsula).
These communities are distributed across 3 provinces.

SUGGESTIONS:
- Show me the provincial distribution
- Which municipalities have the most communities?
- Tell me about the assessment status
```

### Step 4: Verify Backend Integration

**Open Browser Console (F12)** and check for:

✅ **Success indicators:**
```
✅ AI Chat Widget initialized (fixed positioning)
Initial panel state: {...}
```

✅ **No errors** (no red text)

❌ **If you see errors:**
- `401 Unauthorized` → Not logged in
- `500 Internal Server Error` → Check GOOGLE_API_KEY
- `404 Not Found` → URL routing issue

---

## What Was Implemented

### Backend (Already Complete ✅)
1. **Chat View** (`/src/common/views/chat.py`)
   - Handles POST requests
   - Integrates with Gemini AI
   - Returns HTMX-compatible HTML

2. **URL Route** (`/src/common/urls.py` line 731)
   - Endpoint: `/chat/message/`
   - Name: `common:chat_message`

3. **AI Service** (`/src/ai_assistant/services/gemini_service.py`)
   - New `chat_with_ai()` method
   - OBCMS domain knowledge
   - Cultural context integration

4. **Response Template** (`/src/templates/common/chat/message_pair.html`)
   - AI message bubble
   - Intent classification display
   - Timestamp

### Frontend (Already Complete ✅)
1. **Chat Widget** (`/src/templates/components/ai_chat_widget.html`)
   - HTMX form enabled (lines 96-119)
   - Removed "Coming Soon" placeholder
   - Optimistic UI updates
   - Error handling

2. **HTMX Integration**
   - Form submits to `{% url 'common:chat_message' %}`
   - Auto-scrolls to latest message
   - Loading state during AI response

---

## Quick Django Check

**If form doesn't appear after refresh**, run this in terminal:

```bash
cd src

# Check if chat URLs are registered
python manage.py show_urls | grep chat

# Expected output:
# /chat/message/    common:chat_message
# /chat/history/    common:chat_history
# /chat/clear/      common:chat_clear
# /chat/stats/      common:chat_stats
```

If URLs don't show up:
```bash
# Restart Django server
python manage.py runserver
```

---

## Test Checklist

- [ ] Hard refreshed browser (`Cmd+Shift+R` or `Ctrl+Shift+F5`)
- [ ] Chat button opens panel
- [ ] See **input form** (not "Coming Soon")
- [ ] Can type message
- [ ] Message sends (blue bubble appears)
- [ ] Loading spinner shows
- [ ] AI response appears (white bubble)
- [ ] Response is relevant to question
- [ ] No errors in console

---

## Troubleshooting

### Issue: Still seeing "Coming Soon"
**Solution:** Clear all browser data
1. Chrome: `Ctrl+Shift+Delete` or `Cmd+Shift+Delete`
2. Check "Cached images and files"
3. Click "Clear data"
4. Close and reopen browser
5. Navigate to OBCMS again

### Issue: Form appears but sends error
**Check Console (F12) for:**

**Error: `API key not found`**
```bash
# Add to src/.env
GOOGLE_API_KEY=your_actual_api_key_here
```

**Error: `Module not found: ai_services`**
```bash
# Restart Django server
cd src
python manage.py runserver
```

**Error: `401 Unauthorized`**
→ You're not logged in. Log in to OBCMS first.

### Issue: Blank response or loading forever
**Check:**
1. Is GOOGLE_API_KEY valid?
2. Is Gemini API accessible from your network?
3. Check Django console for errors

---

## Expected Performance

| Metric | Expected |
|--------|----------|
| UI response (user message) | Instant (<50ms) |
| AI response time | 1-3 seconds |
| Token usage | 100-300 tokens |
| Cost per query | $0.00003-0.0001 |

---

## Next Steps After Verification

### ✅ If Everything Works
1. Test with various questions (see `/docs/testing/AI_CHAT_SAMPLE_QUESTIONS.md`)
2. Share with team for user acceptance testing
3. Monitor API usage and costs

### ❌ If Issues Persist
1. Run full diagnostic: `/EMERGENCY_AI_CHAT_DIAGNOSTIC.md`
2. Check logs: `src/logs/django.log`
3. Share error messages/console output

---

**Status:** All code implemented ✅
**Action Required:** Hard refresh browser to load new chat form
**ETA:** Working chat in <1 minute after refresh
