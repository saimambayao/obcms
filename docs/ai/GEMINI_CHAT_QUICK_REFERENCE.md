# Gemini Chat Service - Quick Reference

## One-Liner Setup

```python
from ai_assistant.services.gemini_service import GeminiService
service = GeminiService(temperature=0.8)  # Chat-optimized
result = service.chat_with_ai(user_message="Your question here")
```

---

## Common Use Cases

### 1. Simple Question
```python
result = service.chat_with_ai(
    user_message="How many communities are in Region IX?"
)
print(result['message'])
```

### 2. With Context
```python
result = service.chat_with_ai(
    user_message="What are the priority needs?",
    context="User viewing MANA Assessment #123"
)
```

### 3. With Conversation History
```python
history = [
    {"role": "user", "content": "Previous question"},
    {"role": "assistant", "content": "Previous answer"}
]

result = service.chat_with_ai(
    user_message="Follow-up question",
    conversation_history=history
)
```

---

## Response Structure

```python
{
    "success": bool,           # True if successful
    "message": str,            # AI response text
    "suggestions": list[str],  # 3 follow-up questions
    "tokens_used": int,        # Token count
    "cost": float,             # USD cost
    "response_time": float,    # Seconds
    "cached": bool            # Was cached?
}
```

---

## Error Handling

```python
result = service.chat_with_ai(user_message="Question")

if result["success"]:
    # Success
    display_message(result["message"])
    show_suggestions(result["suggestions"])
else:
    # Error (already user-friendly)
    display_error(result["message"])
    show_suggestions(result["suggestions"])  # Fallback suggestions
```

---

## Temperature Guide

| Use Case | Temperature | Example |
|----------|-------------|---------|
| Data queries | 0.3 | "How many communities?" |
| Chat (recommended) | 0.8 | "What can you help with?" |
| Creative content | 0.9 | "Suggest workshop names" |

---

## Cost Reference

| Query Type | Avg Tokens | Avg Cost |
|------------|------------|----------|
| Simple | 100-200 | $0.00003-0.00006 |
| With history | 300-500 | $0.00009-0.00015 |
| Complex | 500-1000 | $0.00015-0.00030 |

**Cache saves:** 100% of repeat queries (1-hour TTL)

---

## Key OBCMS Modules

The AI understands:
- **Communities**: OBC profiles, demographics
- **MANA**: Needs assessments, priorities
- **Coordination**: Partnerships, workshops
- **Policies**: Recommendations, tracking
- **Projects**: PPAs, budgets, metrics

---

## Common Errors & Solutions

### "API key not found"
Set environment variable:
```bash
export GOOGLE_API_KEY=your_key_here
```

### "Rate limit exceeded"
Error message automatically says: "Try again in a few moments"

### High costs
Check cache hit rate in response: `result["cached"]`

---

## Testing

```bash
# Unit tests
pytest ai_assistant/tests/test_gemini_chat.py -v

# Specific test
pytest ai_assistant/tests/test_gemini_chat.py::TestChatWithAI -v
```

---

## Integration Example

```python
# In your view
from ai_assistant.services.gemini_service import GeminiService

@login_required
def chat_view(request):
    message = request.POST.get('message')

    service = GeminiService(temperature=0.8)
    result = service.chat_with_ai(user_message=message)

    return JsonResponse({
        'success': result['success'],
        'message': result['message'],
        'suggestions': result['suggestions']
    })
```

---

## Monitoring Snippet

```python
from ai_assistant.models import AIOperation

# Today's stats
stats = AIOperation.objects.filter(
    operation_type='chat_message',
    created_at__date=date.today()
).aggregate(
    calls=Count('id'),
    cost=Sum('cost'),
    avg_time=Avg('response_time')
)

print(f"Calls: {stats['calls']}, Cost: ${stats['cost']:.4f}")
```

---

## Full Documentation

See: [GEMINI_CHAT_SERVICE_GUIDE.md](GEMINI_CHAT_SERVICE_GUIDE.md)

---

**Last Updated:** January 2025
