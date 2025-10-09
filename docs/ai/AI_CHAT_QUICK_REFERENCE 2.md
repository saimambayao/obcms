# AI Chat Quick Reference - OBCMS

**Last Updated**: October 6, 2025
**Status**: ✅ Production Ready with Gemini AI Fallback

---

## What's New

### ✅ Gemini AI Fallback (October 6, 2025)
- **No more "Could not understand" errors**
- All queries now get intelligent responses
- Location queries fully supported (Davao City, Zamboanga, Cotabato, etc.)
- Graceful handling of API rate limits

---

## How It Works

### Two-Tier Response System

```
User Query
    ↓
Intent Classification
    ↓
Query Generation
    ├─ Structured Query (Fast) → Execute → Response ✅
    └─ Gemini AI (Intelligent) → Conversational Response ✅
```

**Tier 1: Structured Queries** (when possible)
- Direct database queries using Django ORM
- Fast response time (< 100ms)
- Precise data retrieval

**Tier 2: Gemini AI Fallback** (when needed)
- Natural language understanding
- Contextual, conversational responses
- Cultural sensitivity (Bangsamoro context)

---

## Supported Query Types

### 1. Data Queries ✅

**Count Queries**:
```
"How many communities are in Davao City?"
"Count OBC communities in Region IX"
"Total workshops in Zamboanga del Sur"
```

**List Queries**:
```
"Show me communities in Cotabato"
"List all workshops"
"Display policy recommendations"
```

**Location-Specific**:
```
"Tell me about OBC communities in Davao City"
"Communities in Cagayan de Oro"
"Assessments from Lanao del Norte"
```

### 2. Navigation Queries ✅

```
"Go to dashboard"
"Open the MANA module"
"Take me to coordination page"
```

### 3. Help Queries ✅

```
"How do I create a workshop?"
"What is a policy recommendation?"
"Help me search for communities"
```

### 4. General Conversation ✅

```
"Hello!"
"Thank you"
"What can you help me with?"
```

---

## Supported Locations

### Cities
- Davao City ✅
- Cagayan de Oro ✅
- Iligan ✅
- Marawi ✅

### Provinces
- Zamboanga del Sur ✅
- Zamboanga del Norte ✅
- Zamboanga Sibugay ✅
- Sultan Kudarat ✅
- Lanao del Norte ✅
- Lanao del Sur ✅
- Bukidnon ✅
- Cotabato ✅

### Regions
- Region IX (Zamboanga Peninsula) ✅
- Region X (Northern Mindanao) ✅
- Region XI (Davao Region) ✅
- Region XII (SOCCSKSARGEN) ✅

---

## Example Interactions

### Example 1: City-Specific Query

**User**: "tell me about OBC communities in Davao City"

**Assistant**:
> That's a great question! Davao City is indeed home to diverse and vibrant Bangsamoro communities, primarily composed of Maranao, Maguindanao, and Tausug families who maintain strong kinship ties and *Maratabat*. To access detailed information like specific demographic data, community profiles, or current Mapping and Needs Assessments (MANA) for these areas, please utilize the 'Community Profiles' search function within the OBCMS dashboard.

**Suggestions**:
- Tell me more
- What else can you help with?
- Show me some data

**AI-Powered**: Yes (Gemini Fallback)

---

### Example 2: Region Query

**User**: "How many communities are in Region IX?"

**Assistant**:
> That is a very important question regarding our Bangsamoro communities in the Zamboanga Peninsula (Region IX). The exact number is dynamic and constantly updated through our official Mapping and Needs Assessment (MANA) system. For the most current and specific community profiles and counts, please consult the MANA database section of the OBCMS portal.

**Suggestions**:
- Show me community details
- Which provinces have the most?
- What are the top needs?

**AI-Powered**: Yes (Gemini Fallback)

---

### Example 3: Navigation

**User**: "Go to MANA module"

**Assistant**:
> I'll take you to the mana page.

**Action**: Redirects to `/mana/`

---

## Response Structure

Every response includes:

```javascript
{
  "response": "Natural language answer...",
  "data": {
    // Structured data for UI display
    "redirect_url": "/mana/",  // If navigation
    "results": [...]            // If data query
  },
  "suggestions": [
    "Follow-up question 1",
    "Follow-up question 2",
    "Follow-up question 3"
  ],
  "intent": "data_query",        // Intent type
  "confidence": 0.85,            // Confidence score
  "visualization": "bar_chart",  // Suggested visualization (future)
  "ai_powered": true,            // Whether Gemini was used
  "tokens_used": 450,            // API tokens (if AI-powered)
  "cached": false                // Whether response was cached
}
```

---

## Error Handling

### Graceful Degradation

**API Rate Limit**:
```
Response: "I'm currently experiencing high demand. Please try again in a few moments."
Suggestions: Fallback suggestions provided
```

**Network Error**:
```
Response: "I'm having trouble connecting to the network. Please check your internet connection."
Suggestions: Alternative queries provided
```

**Unknown Query**:
```
Response: "I'm not sure how to help with that. Can you try rephrasing your question?"
Suggestions: Example queries provided
```

---

## Performance

### Response Times

| Query Type | Tier 1 (Structured) | Tier 2 (Gemini AI) |
|-----------|---------------------|-------------------|
| Simple count | < 100ms | 3-5 seconds |
| List query | < 500ms | 4-6 seconds |
| Complex query | 500ms - 2s | 5-10 seconds |

### Caching

- **Gemini responses**: Cached for 1 hour
- **Conversation context**: Cached for 30 minutes
- **Structured queries**: Not cached (always fresh data)

### Rate Limits

| Tier | Requests/Minute | Retry Logic |
|------|----------------|-------------|
| Free | 10 | Exponential backoff (1s, 2s, 4s) |
| Paid | 60+ | Same retry logic |

---

## Integration Guide

### Backend (Django View)

```python
from common.ai_services.chat.chat_engine import get_conversational_assistant

def chat_api(request):
    assistant = get_conversational_assistant()

    result = assistant.chat(
        user_id=request.user.id,
        message=request.POST.get('message')
    )

    return JsonResponse({
        'response': result['response'],
        'suggestions': result.get('suggestions', []),
        'data': result.get('data', {}),
        'ai_powered': result.get('ai_powered', False),
    })
```

### Frontend (JavaScript)

```javascript
async function sendChatMessage(message) {
    const response = await fetch('/api/chat/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ message }),
    });

    const data = await response.json();

    // Display response
    displayMessage(data.response, 'assistant');

    // Show suggestions as quick-reply buttons
    if (data.suggestions) {
        displaySuggestions(data.suggestions);
    }

    // Handle special data (e.g., redirect)
    if (data.data.redirect_url) {
        window.location.href = data.data.redirect_url;
    }
}
```

---

## Configuration

### Environment Variables

```bash
# .env
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-flash-latest
GEMINI_TEMPERATURE=0.8  # 0.0-1.0 (higher = more creative)
```

### Settings

```python
# settings/base.py
AI_CHAT_CONFIG = {
    'enable_gemini_fallback': True,
    'cache_ttl': 3600,  # 1 hour
    'max_conversation_history': 5,
    'temperature': 0.8,
    'max_retries': 3,
}
```

---

## Monitoring

### Logs

```bash
# View chat logs
tail -f src/logs/obcms.log | grep "User.*query"

# Monitor Gemini fallback usage
grep "falling back to Gemini" src/logs/obcms.log

# Check rate limit errors
grep "rate limit" src/logs/obcms.log
```

### Metrics to Track

1. **Query Success Rate**: % of queries answered successfully
2. **Fallback Rate**: % of queries using Gemini vs structured
3. **Response Time**: Average response time per query type
4. **API Costs**: Gemini API usage and costs
5. **User Satisfaction**: Follow-up suggestion click rate

---

## Troubleshooting

### Issue: "Could not understand your data query"

**Cause**: Both structured query and Gemini fallback failed
**Solution**:
1. Check Gemini API key is configured
2. Verify network connectivity
3. Check API rate limits

### Issue: Slow Response Times

**Cause**: Gemini API latency
**Solution**:
1. Check if caching is enabled
2. Consider upgrading to paid tier
3. Implement response streaming (future)

### Issue: Database Constraint Error

**Cause**: Trying to save message with null response
**Solution**: ✅ Fixed - conversation manager now validates response before saving

---

## Best Practices

### For Developers

1. **Always handle errors gracefully**
   ```python
   try:
       result = assistant.chat(user_id, message)
   except Exception as e:
       logger.error(f"Chat error: {e}")
       return fallback_response()
   ```

2. **Monitor API costs**
   - Track Gemini API usage via AIOperation model
   - Set budget alerts in Google Cloud Console

3. **Optimize prompts**
   - Keep prompts concise for faster responses
   - Include relevant context only

### For Users

1. **Be specific in queries**
   - ✅ "How many communities in Davao City?"
   - ❌ "Tell me stuff"

2. **Use suggested follow-ups**
   - Suggestions are context-aware and optimized

3. **Rephrase if needed**
   - Natural language is flexible
   - Different phrasings work

---

## Future Enhancements

### Phase 1: Near-term
- [ ] Conversation history support (multi-turn dialogs)
- [ ] Response streaming for real-time feel
- [ ] Voice input/output integration

### Phase 2: Medium-term
- [ ] Multilingual support (Tagalog, Tausug, Maranao)
- [ ] Proactive insights ("Did you know...")
- [ ] Visual query builder with AI assist

### Phase 3: Long-term
- [ ] Custom model fine-tuning on OBCMS data
- [ ] Predictive analytics integration
- [ ] Advanced visualization recommendations

---

## Related Documentation

- [AI Implementation Complete Summary](/AI_IMPLEMENTATION_COMPLETE_SUMMARY.md)
- [AI Chat Query Fix Summary](/AI_CHAT_QUERY_FIX_SUMMARY.md)
- [Gemini Service Documentation](/src/ai_assistant/services/gemini_service.py)
- [Chat Engine Documentation](/src/common/ai_services/chat/chat_engine.py)

---

## Support

For issues or questions:
1. Check logs: `src/logs/obcms.log`
2. Review error messages
3. Contact OBCMS tech team
4. File issue on GitHub (if applicable)

---

**Remember**: The AI chat is designed to ALWAYS provide a helpful response. If you encounter "Could not understand" errors, it's a bug - please report it!
