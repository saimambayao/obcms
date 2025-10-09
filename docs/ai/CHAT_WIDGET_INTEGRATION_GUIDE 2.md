# Chat Widget Integration Guide - Using Enhanced Gemini Service

## Quick Integration Steps

### Step 1: Update Chat View

**File:** `/src/common/views/chat.py`

Replace the existing chat message handler with this optimized version:

```python
"""
Chat Views for Conversational AI Assistant
"""

import json
import logging
from typing import Optional

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from ai_assistant.services.gemini_service import GeminiService
from common.models import ChatMessage

logger = logging.getLogger(__name__)


# Initialize chat-optimized Gemini service (singleton)
_chat_service = None

def get_chat_service() -> GeminiService:
    """Get singleton chat service instance."""
    global _chat_service
    if _chat_service is None:
        _chat_service = GeminiService(temperature=0.8)  # Chat-optimized
        logger.info("Chat service initialized with temperature=0.8")
    return _chat_service


@login_required
@require_http_methods(['POST'])
def chat_message(request):
    """
    Handle incoming chat message from user.

    Uses enhanced GeminiService with OBCMS context and cultural sensitivity.
    """
    message = request.POST.get('message', '').strip()

    if not message:
        return HttpResponse(
            '<div class="text-red-500 text-sm">Please enter a message</div>',
            status=400,
        )

    try:
        # Get chat service
        service = get_chat_service()

        # Get conversation history (last 5 exchanges)
        recent_messages = ChatMessage.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]

        conversation_history = []
        for msg in reversed(list(recent_messages)):
            conversation_history.append({
                "role": "user",
                "content": msg.user_message
            })
            conversation_history.append({
                "role": "assistant",
                "content": msg.assistant_response
            })

        # Get current page context
        referer = request.META.get('HTTP_REFERER', '')
        context_info = f"User role: {request.user.get_role_display()}"
        if 'communities' in referer:
            context_info += ", Viewing: Communities module"
        elif 'mana' in referer:
            context_info += ", Viewing: MANA module"
        elif 'coordination' in referer:
            context_info += ", Viewing: Coordination module"
        elif 'policies' in referer:
            context_info += ", Viewing: Policy Recommendations"
        elif 'project-central' in referer:
            context_info += ", Viewing: Project Central"

        # Use enhanced chat_with_ai() method
        result = service.chat_with_ai(
            user_message=message,
            context=context_info,
            conversation_history=conversation_history
        )

        if result["success"]:
            # Save to database
            chat_msg = ChatMessage.objects.create(
                user=request.user,
                user_message=message,
                assistant_response=result['message'],
                intent='chat',  # Can be enhanced with intent detection
                topic='general',
                metadata={
                    'tokens_used': result['tokens_used'],
                    'cost': str(result['cost']),
                    'response_time': result['response_time'],
                    'cached': result['cached'],
                    'suggestions': result['suggestions']
                }
            )

            # Log metrics
            logger.info(
                f"Chat success - User: {request.user.id}, "
                f"Tokens: {result['tokens_used']}, "
                f"Cost: ${result['cost']:.6f}, "
                f"Cached: {result['cached']}"
            )

            # Render response
            context = {
                'user_message': message,
                'assistant_response': result['message'],
                'suggestions': json.dumps(result['suggestions']),
                'chat_id': chat_msg.id,
                'cached': result['cached'],
            }

            return render(request, 'common/chat/message_pair.html', context)

        else:
            # Error - still save to track failures
            ChatMessage.objects.create(
                user=request.user,
                user_message=message,
                assistant_response=result['message'],
                intent='error',
                topic='error',
                metadata={'error': True}
            )

            logger.warning(
                f"Chat error - User: {request.user.id}, "
                f"Error: {result['message']}"
            )

            context = {
                'user_message': message,
                'assistant_response': result['message'],
                'suggestions': json.dumps(result['suggestions']),
                'is_error': True,
            }

            return render(request, 'common/chat/message_pair.html', context)

    except Exception as e:
        logger.error(f"Chat exception: {str(e)}", exc_info=True)
        return HttpResponse(
            f'<div class="text-red-500 text-sm">'
            f'An unexpected error occurred. Please try again.'
            f'</div>',
            status=500,
        )
```

---

### Step 2: Update Chat Template

**File:** `/src/templates/common/chat/message_pair.html`

Enhance to show suggestions and cached indicator:

```django
{# Chat message pair with suggestions #}
<div class="space-y-4">
    {# User message #}
    <div class="flex justify-end">
        <div class="bg-blue-500 text-white rounded-lg px-4 py-2 max-w-lg">
            <p class="text-sm">{{ user_message }}</p>
        </div>
    </div>

    {# Assistant response #}
    <div class="flex justify-start">
        <div class="bg-gray-100 rounded-lg px-4 py-2 max-w-lg {% if is_error %}border-l-4 border-red-500{% endif %}">
            <p class="text-sm text-gray-800">{{ assistant_response }}</p>

            {# Cached indicator (optional) #}
            {% if cached %}
            <div class="mt-2 text-xs text-gray-500 flex items-center gap-1">
                <i class="fas fa-bolt text-yellow-500"></i>
                <span>Instant response (cached)</span>
            </div>
            {% endif %}
        </div>
    </div>

    {# Suggestions as clickable buttons #}
    {% if suggestions and suggestions != '[]' %}
    <div class="flex flex-wrap gap-2 px-4">
        <span class="text-xs text-gray-500">Try asking:</span>
        <script>
            // Parse suggestions JSON
            const suggestions = {{ suggestions|safe }};

            // Create suggestion buttons
            suggestions.forEach(suggestion => {
                const btn = document.createElement('button');
                btn.className = 'text-xs bg-white border border-gray-300 rounded-full px-3 py-1 hover:bg-gray-50 transition-colors';
                btn.textContent = suggestion;
                btn.onclick = () => {
                    // Send suggestion as new message
                    document.querySelector('#chat-input').value = suggestion;
                    document.querySelector('#chat-form').dispatchEvent(new Event('submit'));
                };
                document.currentScript.parentElement.appendChild(btn);
            });
        </script>
    </div>
    {% endif %}
</div>
```

---

### Step 3: Add Cost Monitoring Dashboard

**File:** `/src/common/views/chat.py` (add this view)

```python
@login_required
@require_http_methods(['GET'])
def chat_analytics(request):
    """
    Chat analytics dashboard (admin only).

    Shows usage stats, costs, and performance metrics.
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'Admin access required'}, status=403)

    from django.db.models import Count, Sum, Avg
    from django.utils import timezone
    from datetime import timedelta

    # Get date range
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Today's stats
    today_stats = ChatMessage.objects.filter(
        created_at__date=today
    ).aggregate(
        total=Count('id'),
        avg_tokens=Avg('metadata__tokens_used'),
        total_cost=Sum('metadata__cost'),
    )

    # Weekly stats
    weekly_stats = ChatMessage.objects.filter(
        created_at__date__gte=week_ago
    ).aggregate(
        total=Count('id'),
        total_cost=Sum('metadata__cost'),
    )

    # Monthly stats
    monthly_stats = ChatMessage.objects.filter(
        created_at__date__gte=month_ago
    ).aggregate(
        total=Count('id'),
        total_cost=Sum('metadata__cost'),
    )

    # Cache hit rate
    cached_count = ChatMessage.objects.filter(
        created_at__date__gte=week_ago,
        metadata__cached=True
    ).count()
    total_count = weekly_stats['total'] or 1
    cache_hit_rate = (cached_count / total_count) * 100

    # Top users
    top_users = ChatMessage.objects.filter(
        created_at__date__gte=week_ago
    ).values('user__username').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    return JsonResponse({
        'today': {
            'total_messages': today_stats['total'] or 0,
            'avg_tokens': int(today_stats['avg_tokens'] or 0),
            'total_cost': float(today_stats['total_cost'] or 0),
        },
        'weekly': {
            'total_messages': weekly_stats['total'] or 0,
            'total_cost': float(weekly_stats['total_cost'] or 0),
            'cache_hit_rate': f"{cache_hit_rate:.1f}%",
        },
        'monthly': {
            'total_messages': monthly_stats['total'] or 0,
            'total_cost': float(monthly_stats['total_cost'] or 0),
            'projected_cost': float((monthly_stats['total_cost'] or 0) / 30 * 30),
        },
        'top_users': list(top_users),
    })
```

**Add URL:**
```python
# src/common/urls.py
path('chat/analytics/', views.chat_analytics, name='chat_analytics'),
```

---

### Step 4: Environment Configuration

**File:** `.env`

Add or update:

```env
# Google Gemini API for Chat
GOOGLE_API_KEY=your_actual_gemini_api_key_here

# Optional: Chat-specific settings
CHAT_ENABLED=True
CHAT_MAX_HISTORY=5
CHAT_CACHE_TTL=3600
```

**File:** `src/obc_management/settings/base.py`

Add settings:

```python
# Google Gemini AI
GOOGLE_API_KEY = env('GOOGLE_API_KEY', default='')

# Chat widget configuration
CHAT_ENABLED = bool(GOOGLE_API_KEY)
CHAT_MAX_HISTORY = env.int('CHAT_MAX_HISTORY', default=5)
CHAT_CACHE_TTL = env.int('CHAT_CACHE_TTL', default=3600)  # 1 hour
```

---

### Step 5: Test Integration

**Test manually:**

```bash
# 1. Start server
cd src
./manage.py runserver

# 2. Open chat widget in browser
# 3. Try these test messages:

# Simple query
"How many communities are in Region IX?"

# Follow-up (tests conversation history)
"What about Region X?"

# Module-specific
"Show me recent MANA assessments"

# Help
"What can you help me with?"

# Error (to test error handling)
"" (empty message)
```

**Monitor logs:**

```bash
# In another terminal
tail -f src/logs/obcms.log | grep -i chat
```

**Check analytics (if admin):**

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/chat/analytics/
```

---

## Expected Results

### Successful Response

**User:** "How many communities are in Region IX?"

**AI Response:**
```
Based on the latest data, there are 47 Bangsamoro communities
in Region IX (Zamboanga Peninsula). These communities are spread
across multiple provinces and municipalities in the region.
```

**Suggestions:**
- "Show me details about these communities"
- "Which provinces have the most communities?"
- "What are the priority needs in Region IX?"

**Metrics:**
- Tokens: ~150
- Cost: $0.000045
- Response time: 0.8s
- Cached: No (first query)

### With Conversation History

**User:** "What about Region X?"

**AI Response:**
```
In Region X (Northern Mindanao), there are 35 Bangsamoro communities.
This is fewer than Region IX, but these communities also have important
needs across education, health, and livelihood sectors.
```

**Suggestions:**
- "Compare all regions"
- "Show me the breakdown by province"
- "What are the main needs in Region X?"

**Metrics:**
- Tokens: ~180 (includes history)
- Cost: $0.000054
- Response time: 0.9s
- Cached: No

### Cached Response

**User:** "How many communities are in Region IX?" (asked again)

**AI Response:** (same as first time)

**Metrics:**
- Tokens: 0 (cached)
- Cost: $0.00 (cached)
- Response time: 0.05s
- Cached: **Yes** ⚡

---

## Monitoring Checklist

After integration, monitor these metrics:

- [ ] **Response Time**: Average < 2 seconds
- [ ] **Cache Hit Rate**: > 60% after first week
- [ ] **Daily Cost**: < $0.50 for 100 users
- [ ] **Error Rate**: < 5%
- [ ] **User Satisfaction**: Collect feedback (thumbs up/down)

---

## Troubleshooting

### Issue: "API key not found"
**Fix:** Set `GOOGLE_API_KEY` in `.env` file

### Issue: Slow responses
**Fix:**
1. Check internet connection
2. Review `response_time` in logs
3. Consider regional API endpoints

### Issue: High costs
**Fix:**
1. Check `cache_hit_rate` in analytics
2. Verify `CHAT_CACHE_TTL=3600` is set
3. Review conversation history limit

### Issue: Poor responses
**Fix:**
1. Verify temperature is 0.8 (not too low)
2. Check system context is being included
3. Review conversation history quality

---

## Performance Benchmarks

**Target Metrics:**

| Metric | Target | Acceptable | Poor |
|--------|--------|------------|------|
| Response Time | < 1s | 1-2s | > 2s |
| Cache Hit Rate | > 70% | 50-70% | < 50% |
| Daily Cost (100 users) | < $0.30 | $0.30-0.50 | > $0.50 |
| Error Rate | < 2% | 2-5% | > 5% |

---

## Next Steps

1. **Deploy to staging** with real API key
2. **User acceptance testing** with OOBC staff
3. **Monitor costs** for first week
4. **Collect feedback** and iterate
5. **Add advanced features**:
   - Voice input
   - Document search integration
   - Proactive suggestions
   - Multi-language support

---

## Related Documentation

- **[GEMINI_CHAT_SERVICE_GUIDE.md](GEMINI_CHAT_SERVICE_GUIDE.md)** - Full service documentation
- **[GEMINI_CHAT_QUICK_REFERENCE.md](GEMINI_CHAT_QUICK_REFERENCE.md)** - Developer quick reference
- **[CONVERSATIONAL_AI_IMPLEMENTATION.md](../improvements/CONVERSATIONAL_AI_IMPLEMENTATION.md)** - Chat architecture

---

**Last Updated:** January 2025
**Status:** Ready for Integration
