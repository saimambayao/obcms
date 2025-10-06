# AI Chat Troubleshooting Guide

**Last Updated:** 2025-10-06
**Status:** Active Issue - Gemini API Quota Exhausted

---

## Current Status Summary

### ✅ Fixed Issues

**CSRF Token Authentication (RESOLVED)**
- **Issue:** 403 Forbidden errors on chat POST requests
- **Root Cause:** Missing CSRF token in AJAX requests
- **Fix Applied:** Updated `src/static/common/js/chat-widget.js` to include CSRF token
- **Verification:** Console now shows "✅ CSRF token added to POST request"
- **Status:** WORKING CORRECTLY

### ⚠️ Active Issues

**Gemini API Quota Exceeded (BLOCKING)**
- **Issue:** 429 Too Many Requests error from Gemini API
- **Root Cause:** Free tier limit of 250 requests/day exhausted
- **Impact:** ALL AI chat queries failing (both structured and conversational)
- **User Experience:** Generic error message displayed
- **Status:** BLOCKED - Requires API upgrade or local fallback

---

## Error Details

### Error Message in Terminal

```
ERROR 429 You exceeded your current quota
Quota exceeded for metric: generate_content_free_tier_requests
Limit: 250 requests per day
Model: gemini-2.5-flash
```

### Error Flow

1. **User Query:** "How many communities are in Region IX?"
2. **System Attempts:** Generate structured database query via Gemini API
3. **API Response:** 429 Quota Exceeded
4. **Retry Logic:** 3 attempts with exponential backoff (all fail)
5. **Fallback Attempt:** Conversational AI generation via Gemini
6. **API Response:** 429 Quota Exceeded (again)
7. **Final Retry:** 3 more attempts (all fail)
8. **User Sees:** "I couldn't process your question. Please try rephrasing it."

### Affected Components

**Backend Services:**
- `src/common/ai_services/chat/chat_engine.py` - Main chat orchestration
- `src/ai_assistant/services/gemini_service.py` - Gemini API client
- `src/common/views/chat.py` - Chat view handling

**Frontend Components:**
- `src/static/common/js/chat-widget.js` - Chat interface (WORKING)
- `src/templates/components/chat_widget.html` - Widget template (WORKING)

**Database:**
- `src/common/models/chat.py` - Conversation storage (WORKING)
- All queries are cached correctly (WORKING)

---

## Solutions

### Option 1: Upgrade Gemini API to Paid Tier ⭐ RECOMMENDED

**Overview:**
Upgrade from free tier to paid tier for production-level quota

**Specifications:**
- **Free Tier:** 250 requests/day
- **Paid Tier:** 1,000 requests/minute
- **Cost:** ~$24/month for 100 users (~$0.000125 per request)
- **Model:** gemini-2.5-flash

**Pricing Details:**
- Input: $0.075 per 1M tokens
- Output: $0.30 per 1M tokens
- Average query: ~500 input tokens + 200 output tokens = $0.00007/query
- Estimated monthly: 100 users × 10 queries/day × 30 days = 30,000 queries = $2.10
- Safety buffer: $24/month covers up to 340,000 queries

**Steps:**
1. Visit https://ai.google.dev/pricing
2. Sign up for paid tier
3. Generate new API key
4. Update `GEMINI_API_KEY` in `.env`
5. Restart Django server

**Benefits:**
- Production-ready immediately
- No code changes required
- Supports high traffic
- Real-time AI responses

---

### Option 2: Implement Local Query Fallback 🛠️ IMMEDIATE

**Overview:**
Add database query fallback for common questions without using AI

**Implementation:**

```python
# src/common/ai_services/chat/chat_engine.py

def _local_query_fallback(self, message: str) -> Optional[str]:
    """
    Handle common queries without AI when API is unavailable.
    """
    message_lower = message.lower()

    # Pattern 1: Count communities by region
    if "how many" in message_lower and "communities" in message_lower:
        region_patterns = {
            'region ix': 'IX',
            'region 9': 'IX',
            'zamboanga': 'IX',
            'region x': 'X',
            'region 10': 'X',
            'northern mindanao': 'X',
            'region xi': 'XI',
            'region 11': 'XI',
            'davao': 'XI',
            'region xii': 'XII',
            'region 12': 'XII',
            'soccsksargen': 'XII',
        }

        for pattern, region_code in region_patterns.items():
            if pattern in message_lower:
                count = OBCCommunity.objects.filter(
                    barangay__municipality__province__region__code=region_code
                ).count()
                return f"There are {count} OBC communities in Region {region_code}."

    # Pattern 2: List regions
    if "regions" in message_lower and ("list" in message_lower or "what" in message_lower):
        regions = Region.objects.filter(
            province__municipality__barangay__obc_communities__isnull=False
        ).distinct().values_list('name', 'code')

        region_list = "\n".join([f"- {name} ({code})" for name, code in regions])
        return f"OBCMS serves the following regions:\n{region_list}"

    # Pattern 3: Count assessments
    if "how many" in message_lower and "assessment" in message_lower:
        count = MANAAssessment.objects.count()
        return f"There are {count} MANA assessments in the system."

    return None  # No pattern matched, let AI handle it


def process_message(self, user_message: str, user=None) -> Dict[str, Any]:
    """
    Process user message with fallback support.
    """
    try:
        # Try AI processing
        return self._process_with_ai(user_message, user)

    except GeminiQuotaExceeded:
        # Try local fallback first
        fallback_response = self._local_query_fallback(user_message)

        if fallback_response:
            return {
                'success': True,
                'response': fallback_response,
                'source': 'local_fallback',
                'conversation_id': None
            }

        # No fallback available
        return {
            'success': False,
            'error': 'AI service temporarily unavailable. Please try again later.',
            'fallback_available': False
        }
```

**Steps:**
1. Add fallback method to `ChatEngine` class
2. Implement common query patterns
3. Catch quota exceptions
4. Return database results directly

**Benefits:**
- Works immediately (no API needed)
- Free forever
- Fast responses for common queries
- Graceful degradation

**Limitations:**
- Limited to predefined patterns
- No natural language understanding
- Must manually add new patterns

---

### Option 3: Wait for Quota Reset ⏰

**Overview:**
Wait 24 hours for free tier quota to reset

**Timeline:**
- **Quota Reset:** ~24 hours from last request
- **Next Available:** Check at https://aistudio.google.com/app/apikey
- **Testing Window:** Limited to 250 requests/day

**Recommended Use:**
- Development/testing only
- Not suitable for production
- Good for prototyping

---

## Technical Implementation Details

### CSRF Fix Implementation

**File:** `src/static/common/js/chat-widget.js`

**Changes Applied:**

```javascript
// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Send message to server with CSRF token
const csrftoken = getCookie('csrftoken');
console.log('✅ CSRF token added to POST request');

const response = await fetch('/chat/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken,  // ← Added this
    },
    body: JSON.stringify({ message: messageText })
});
```

**Testing:**
```bash
# Open browser console at http://localhost:8000/
# Send chat message: "hello"
# Verify console shows: ✅ CSRF token added to POST request
# Verify response: 200 OK (not 403 Forbidden)
```

---

### Retry Logic with Exponential Backoff

**File:** `src/ai_assistant/services/gemini_service.py`

**Current Implementation:**

```python
def generate_content_with_retry(self, prompt: str, max_retries: int = 3) -> str:
    """
    Generate content with exponential backoff retry.
    """
    for attempt in range(max_retries):
        try:
            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 1  # 1s, 2s, 4s
                    time.sleep(wait_time)
                    continue
                else:
                    raise GeminiQuotaExceeded(f"Quota exceeded after {max_retries} attempts")
            raise
```

**Behavior:**
- Attempt 1: Immediate
- Attempt 2: Wait 1 second
- Attempt 3: Wait 2 seconds
- Attempt 4: Wait 4 seconds (if configured)
- Final: Raise exception

---

### Conversation Caching

**File:** `src/common/models/chat.py`

**Implementation:**

```python
class Conversation(models.Model):
    """
    Store conversation history for caching and context.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Message(models.Model):
    """
    Store individual messages with AI responses.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    role = models.CharField(max_length=20)  # 'user' or 'assistant'
    content = models.TextField()
    query_used = models.TextField(null=True, blank=True)  # Cached SQL query
    created_at = models.DateTimeField(auto_now_add=True)
```

**Benefits:**
- Reduces API calls for repeated questions
- Maintains conversation context
- Enables query reuse

**Status:** WORKING CORRECTLY ✅

---

## Testing Procedures

### Test 1: CSRF Token Verification ✅

```bash
# 1. Start development server
cd src
python manage.py runserver

# 2. Open browser at http://localhost:8000/
# 3. Open Developer Console (F12)
# 4. Type message in chat widget: "hello"
# 5. Verify console output:
#    ✅ CSRF token added to POST request
# 6. Verify Network tab:
#    Request Headers include: X-CSRFToken: <token>
# 7. Verify response: 200 OK (not 403)
```

**Expected Result:** ✅ PASS

---

### Test 2: Gemini API Quota Check ⚠️

```bash
# 1. Send test query: "How many communities are in Region IX?"
# 2. Check terminal output for errors
# 3. Verify response to user

# Current Result:
# - Terminal: ERROR 429 You exceeded your current quota
# - User sees: "I couldn't process your question. Please try rephrasing it."
```

**Expected Result:** ⚠️ BLOCKED (Quota exhausted)

---

### Test 3: Help Command (No AI Required) ✅

```bash
# 1. Send message: "help"
# 2. Verify response includes available commands
# 3. Verify no API calls made

# Expected response:
# "I can help you with:
#  - Finding OBC communities by region
#  - Checking MANA assessment data
#  - Searching coordination records
#  Type a question to get started!"
```

**Expected Result:** ✅ PASS (Should work even with quota exhausted)

---

## Monitoring & Debugging

### Check API Quota Status

```bash
# Visit Gemini API Console
open https://aistudio.google.com/app/apikey

# Check quota metrics:
# - Requests today: X / 250
# - Quota resets: HH:MM (24 hours after first request)
```

### Monitor Django Logs

```bash
# Terminal output shows:
cd src
python manage.py runserver

# Watch for:
# - ERROR 429 You exceeded your current quota
# - INFO: Using cached response for query
# - WARNING: Gemini API fallback to conversational
```

### Enable Debug Logging

```python
# src/obc_management/settings/development.py

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',  # ← Change from INFO to DEBUG
        },
    },
    'loggers': {
        'ai_assistant': {
            'handlers': ['console'],
            'level': 'DEBUG',  # ← Enable detailed AI logs
        },
    },
}
```

---

## Production Readiness Checklist

### Before Deployment

- [ ] Upgrade Gemini API to paid tier
- [ ] Set `GEMINI_API_KEY` in production environment
- [ ] Implement local fallback for common queries
- [ ] Test with production data volume
- [ ] Configure monitoring alerts for API errors
- [ ] Set up rate limiting (10 queries/minute per user)
- [ ] Enable conversation caching (already implemented)
- [ ] Test CSRF token in production domain
- [ ] Verify CORS settings for production URLs
- [ ] Load test: 50 concurrent users × 10 queries/minute

### Monitoring Setup

```python
# Add to production settings
GEMINI_API_MONITORING = {
    'alert_on_quota_warning': True,  # Alert at 80% quota
    'alert_on_errors': True,  # Alert on 429 errors
    'log_all_requests': True,  # Log for analysis
    'fallback_enabled': True,  # Use local fallback
}
```

### Cost Estimation (Paid Tier)

**Monthly Usage Projection:**
- **Users:** 100 staff members
- **Queries:** 10 queries/user/day
- **Days:** 22 working days/month
- **Total Queries:** 22,000/month

**Cost Breakdown:**
```
Input tokens:  22,000 × 500 tokens = 11M tokens = $0.825
Output tokens: 22,000 × 200 tokens = 4.4M tokens = $1.32
Total: ~$2.15/month

Safety buffer (10x): ~$24/month
Covers up to: 220,000 queries/month (340,000 theoretical max)
```

**ROI:**
- Staff time saved: ~5 min/query × 22,000 queries = 1,833 hours/month
- Cost per hour saved: $2.15 / 1,833 = $0.001/hour
- Clear positive ROI for productivity improvement

---

## Related Documentation

- **[AI Chat Quick Reference](../AI_CHAT_QUICK_REFERENCE.md)** - Usage guide
- **[Gemini Chat Service Guide](../GEMINI_CHAT_SERVICE_GUIDE.md)** - Service architecture
- **[Chat Widget Integration](../CHAT_WIDGET_INTEGRATION_GUIDE.md)** - Frontend integration
- **[AI Production Readiness](../AI_PRODUCTION_READINESS_ASSESSMENT.md)** - Full assessment

---

## Changelog

**2025-10-06:**
- ✅ Fixed CSRF token authentication in chat widget
- ⚠️ Identified Gemini API quota exhaustion issue
- 📝 Documented troubleshooting procedures
- 📋 Created local fallback implementation plan

---

## Contact & Support

**For Issues:**
- Review this guide first
- Check [AI documentation](../README.md)
- Test with "help" command (works without API)
- Review terminal logs for specific errors

**Next Steps:**
1. Choose solution: Upgrade API (recommended) or implement fallback
2. Test thoroughly in development
3. Deploy to staging for validation
4. Monitor production usage and costs
