# Gemini Chat Service Enhancement Guide

## Overview

The enhanced GeminiService provides optimized chat functionality for the OBCMS AI chat widget, offering natural conversational responses with deep OBCMS domain knowledge.

**Location:** `/src/ai_assistant/services/gemini_service.py`

**Status:** ✅ Enhanced for Chat (January 2025)

---

## Key Features

### 1. **Chat-Optimized Temperature**
- Default: `0.7` for general tasks
- Chat-specific: `0.8` for more natural conversational responses
- Configurable per use case

### 2. **OBCMS Domain Knowledge**
The chat assistant understands all OBCMS modules:

- **Communities Module**: OBC profiles, demographics, geographic distribution
- **MANA**: Needs assessments, priority identification, regional data
- **Coordination**: Partnerships, workshops, MOAs, resource allocation
- **Policy Recommendations**: Evidence-based proposals, impact tracking
- **Project Central**: PPAs, budget tracking, performance metrics

### 3. **Bangsamoro Cultural Context**
Automatically integrates cultural sensitivity:
- Islamic principles and Shariah compatibility
- Traditional governance structures (Datu, Sultan)
- Ethnolinguistic diversity awareness
- Historical sensitivity and trauma-informed approaches

### 4. **User-Friendly Error Handling**
Converts technical errors to helpful messages:
- API key issues → "Contact system administrator"
- Rate limits → "Try again in a few moments"
- Timeouts → "Try a simpler question"
- Network errors → "Check internet connection"

### 5. **Smart Response Caching**
- 1-hour cache for chat responses (faster than general 24-hour cache)
- Reduces API costs for common questions
- Maintains conversation quality

---

## Usage

### Basic Chat Message

```python
from ai_assistant.services.gemini_service import GeminiService

# Initialize with chat-optimized temperature
service = GeminiService(temperature=0.8)

# Send chat message
result = service.chat_with_ai(
    user_message="How many communities are in Region IX?",
    context="User viewing Communities dashboard"
)

# Access response
if result["success"]:
    print(result["message"])
    # "Based on the latest data, there are 47 Bangsamoro communities in Region IX..."

    print(result["suggestions"])
    # ["Show me details about these communities", "Which provinces have the most?", ...]

    print(f"Cost: ${result['cost']:.6f}")
    print(f"Tokens: {result['tokens_used']}")
else:
    print(f"Error: {result['message']}")
```

### With Conversation History

```python
# Include previous exchanges for context-aware responses
conversation_history = [
    {"role": "user", "content": "How many communities are there?"},
    {"role": "assistant", "content": "There are 150 OBC communities total."},
    {"role": "user", "content": "What about Region IX?"},
]

result = service.chat_with_ai(
    user_message="What about Region IX?",
    conversation_history=conversation_history
)

# AI understands context from previous exchanges
print(result["message"])
# "In Region IX specifically, there are 47 Bangsamoro communities..."
```

### With Additional Context

```python
# Provide page-specific context
result = service.chat_with_ai(
    user_message="What are the priority needs?",
    context="User viewing MANA Assessment #123 for Barangay Poblacion"
)

# AI tailors response to specific assessment
```

---

## Response Structure

### Success Response

```python
{
    "success": True,
    "message": "Natural language response here...",
    "tokens_used": 150,
    "cost": 0.000045,  # USD
    "response_time": 0.8,  # seconds
    "suggestions": [
        "Follow-up question 1",
        "Follow-up question 2",
        "Follow-up question 3"
    ],
    "cached": False
}
```

### Error Response

```python
{
    "success": False,
    "message": "User-friendly error message",
    "tokens_used": 0,
    "cost": 0.0,
    "response_time": 0.1,
    "suggestions": [
        "How many communities are in Region IX?",
        "Show me recent MANA assessments",
        "What can you help me with?"
    ],
    "cached": False
}
```

---

## OBCMS System Context

The chat assistant provides detailed context about OBCMS capabilities:

### Communities Module
- OBC profiles and demographics
- Geographic data for Regions IX, X, XI, XII
- Ethnolinguistic group information
- Provincial and municipal distribution

### MANA (Mapping and Needs Assessment)
- Community needs across sectors
- Priority needs (Health, Education, Infrastructure, Livelihood)
- Assessment status tracking
- Regional and community-level data

### Coordination Module
- Multi-stakeholder partnerships
- Workshops and capacity building
- Partnership agreements (MOAs)
- Resource coordination

### Policy Recommendations
- Evidence-based proposals
- Policy tracking and implementation
- Impact assessments
- Cultural compliance validation

### Project Management
- Programs, Projects, Activities (PPAs)
- Budget allocation and tracking
- Timeline and milestone monitoring
- Performance metrics

---

## Pricing and Cost Management

### Gemini Flash Pricing (2025)
- **Input tokens**: $0.30 per 1M tokens
- **Output tokens**: $2.50 per 1M tokens

### Typical Chat Costs

| Interaction Type | Tokens | Cost (USD) |
|------------------|--------|------------|
| Simple question | 100-200 | $0.00003-0.00006 |
| Complex query with history | 300-500 | $0.00009-0.00015 |
| Multi-turn conversation | 500-1000 | $0.00015-0.00030 |

### Cost Optimization

1. **Response caching** (1-hour TTL) reduces repeat query costs to $0
2. **Conversation history limit** (last 5 exchanges) prevents token bloat
3. **Smart prompting** keeps system context concise
4. **Fallback suggestions** reduce follow-up query costs

**Estimated monthly cost for 1000 users:**
- Average: 10 queries/user/day
- 300,000 queries/month
- Estimated cost: **$9-15/month** (with caching)

---

## Error Handling

### API Key Errors
```
"I'm having trouble connecting to the AI service.
Please contact your system administrator."
```

### Rate Limit Errors
```
"I'm currently experiencing high demand.
Please try again in a few moments."
```

### Timeout Errors
```
"The request took too long to process.
Please try a simpler question or try again later."
```

### Network Errors
```
"I'm having trouble connecting to the network.
Please check your internet connection and try again."
```

### Content Policy Errors
```
"I couldn't process that request due to content guidelines.
Please try rephrasing your question."
```

---

## Integration with Chat Widget

### In ConversationalAssistant

```python
# src/common/ai_services/chat/chat_engine.py

from ai_assistant.services.gemini_service import GeminiService

class ConversationalAssistant:
    def __init__(self):
        # Initialize with chat-optimized temperature
        self.gemini = GeminiService(temperature=0.8)

    def chat(self, user_id: int, message: str):
        # Get conversation history
        context = self.conversation_manager.get_context(user_id)

        # Use enhanced chat method
        result = self.gemini.chat_with_ai(
            user_message=message,
            context=f"User role: {user.role}, Current page: {page}",
            conversation_history=context.get("history", [])
        )

        return result
```

### In Chat View

```python
# src/common/views/chat.py

from ai_assistant.services.gemini_service import GeminiService

@login_required
def chat_message(request):
    message = request.POST.get('message')

    # Direct usage (alternative to ConversationalAssistant)
    service = GeminiService(temperature=0.8)
    result = service.chat_with_ai(user_message=message)

    if result["success"]:
        return render(request, 'common/chat/message_pair.html', {
            'user_message': message,
            'assistant_response': result['message'],
            'suggestions': result['suggestions'],
        })
    else:
        return HttpResponse(
            f'<div class="text-red-500">{result["message"]}</div>',
            status=500
        )
```

---

## Configuration

### Environment Variables

```env
# Required
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional (defaults shown)
GEMINI_MODEL=gemini-flash-latest
GEMINI_TEMPERATURE=0.8
GEMINI_MAX_RETRIES=3
```

### Django Settings

```python
# src/obc_management/settings/base.py

# Google Gemini API
GOOGLE_API_KEY = env('GOOGLE_API_KEY', default='')

# Chat widget settings
CHAT_ENABLED = bool(GOOGLE_API_KEY)
CHAT_CACHE_TTL = 3600  # 1 hour
CHAT_MAX_HISTORY = 5  # Last 5 exchanges
```

---

## Testing

### Unit Tests

```bash
# Run Gemini chat tests
cd src
pytest ai_assistant/tests/test_gemini_chat.py -v

# Run specific test class
pytest ai_assistant/tests/test_gemini_chat.py::TestChatWithAI -v

# Run with coverage
pytest ai_assistant/tests/test_gemini_chat.py --cov=ai_assistant.services.gemini_service
```

### Integration Test

```python
from ai_assistant.services.gemini_service import GeminiService

# Real API test (requires valid API key)
service = GeminiService(temperature=0.8)

result = service.chat_with_ai(
    user_message="How many communities are in OBCMS?",
    context="Testing chat functionality"
)

assert result["success"]
print(f"Response: {result['message']}")
print(f"Suggestions: {result['suggestions']}")
print(f"Cost: ${result['cost']:.6f}")
```

---

## Best Practices

### 1. **Temperature Selection**
- **0.3-0.5**: Factual queries, data extraction
- **0.7-0.8**: Conversational chat (recommended)
- **0.9-1.0**: Creative content, brainstorming

### 2. **Conversation History Management**
- Limit to last 5 exchanges to prevent token bloat
- Clear history periodically (user preference)
- Store full history in database for analytics

### 3. **Context Provision**
- Include current page/module in context
- Provide user role for personalized responses
- Add relevant IDs (e.g., "Viewing Assessment #123")

### 4. **Error Recovery**
- Always provide fallback suggestions
- Log errors for debugging
- Display user-friendly messages
- Offer alternative actions

### 5. **Cost Monitoring**
- Log all API calls with token counts
- Monitor daily/monthly costs
- Set budget alerts in Google Cloud
- Review cache hit rates

### 6. **Cultural Sensitivity**
- Let AI auto-include Bangsamoro context
- Review responses for appropriateness
- Test with diverse scenarios
- Gather user feedback

---

## Troubleshooting

### Issue: "API key not found"
**Solution:** Set `GOOGLE_API_KEY` in environment variables or `.env` file

### Issue: High API costs
**Solutions:**
1. Check cache hit rate (`cached: True` in responses)
2. Reduce conversation history limit
3. Implement request rate limiting
4. Review prompt efficiency

### Issue: Slow responses
**Solutions:**
1. Check `response_time` in results
2. Verify network connectivity
3. Consider using streaming for long responses
4. Implement timeout handling

### Issue: Poor response quality
**Solutions:**
1. Adjust temperature (try 0.7-0.9 range)
2. Provide more specific context
3. Include conversation history
4. Review system prompt clarity

---

## Monitoring and Analytics

### Key Metrics to Track

```python
from ai_assistant.models import AIOperation

# Query metrics
stats = AIOperation.objects.filter(
    operation_type='chat_message'
).aggregate(
    total_calls=Count('id'),
    avg_tokens=Avg('tokens_used'),
    total_cost=Sum('cost'),
    avg_response_time=Avg('response_time'),
    cache_hit_rate=Avg(
        Case(When(cached=True, then=1), default=0, output_field=FloatField())
    )
)

print(f"Total chat calls: {stats['total_calls']}")
print(f"Average tokens: {stats['avg_tokens']:.0f}")
print(f"Total cost: ${stats['total_cost']:.2f}")
print(f"Cache hit rate: {stats['cache_hit_rate']:.1%}")
```

### Set Budget Alerts

```python
# Check daily costs
from datetime import date
from decimal import Decimal

daily_cost = AIOperation.objects.filter(
    operation_type='chat_message',
    created_at__date=date.today()
).aggregate(total=Sum('cost'))['total'] or Decimal('0')

DAILY_BUDGET = Decimal('0.50')  # $0.50/day

if daily_cost >= DAILY_BUDGET:
    # Send alert to admin
    logger.warning(f"Daily AI budget exceeded: ${daily_cost:.2f}")
```

---

## Future Enhancements

### Phase 1: Streaming Responses ✅ (Already available)
- Use `generate_stream()` for real-time responses
- Better UX for long answers

### Phase 2: Multi-modal Chat (Planned)
- Image analysis (chart uploads)
- Document parsing (PDF reports)
- Map interactions

### Phase 3: Advanced Context (Planned)
- User preference learning
- Proactive suggestions
- Cross-session memory

### Phase 4: Voice Interface (Future)
- Speech-to-text input
- Text-to-speech output
- Multilingual support

---

## Related Documentation

- **[GeminiService Base Documentation](gemini_service.py)** - Core service implementation
- **[Bangsamoro Cultural Context](../ai_assistant/cultural_context.py)** - Cultural guidelines
- **[Chat Engine Architecture](CONVERSATIONAL_AI_IMPLEMENTATION.md)** - Full chat system
- **[AI Implementation Summary](AI_IMPLEMENTATION_COMPLETE_SUMMARY.md)** - Overall AI features

---

## Support

For issues or questions:

1. **Check logs:** `/src/logs/` for detailed error traces
2. **Review tests:** `/src/ai_assistant/tests/test_gemini_chat.py`
3. **Contact:** OBCMS AI Engineering Team

**Last Updated:** January 2025
**Version:** 1.0 (Chat Enhancement)
