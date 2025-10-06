# OBCMS AI Quick Start Guide
## Get Started with AI Integration in 30 Minutes

**Document Version:** 1.0
**Date:** October 2025
**Audience:** Django Developers

---

## Overview

This guide helps you **quickly integrate AI capabilities** into OBCMS modules. For comprehensive strategy, see [AI_STRATEGY_COMPREHENSIVE.md](AI_STRATEGY_COMPREHENSIVE.md).

---

## Prerequisites

1. **API Keys** (choose one or both):
   - **Claude (Recommended)**: Get API key from https://console.anthropic.com
   - **Gemini (Alternative)**: Get API key from https://makersuite.google.com

2. **Environment Setup**:
   ```bash
   # Install AI dependencies
   pip install anthropic google-generativeai openai faiss-cpu

   # Add to .env
   ANTHROPIC_API_KEY=sk-ant-...
   GOOGLE_API_KEY=...
   OPENAI_API_KEY=...  # For embeddings
   ```

---

## 5-Minute AI Integration

### Step 1: Setup AI Service (Existing)

OBCMS already has an AI service layer in `src/ai_assistant/`. You can extend it:

```python
# src/ai_assistant/services/quick_ai.py
import anthropic
from django.conf import settings
from django.core.cache import cache

class QuickAI:
    """Simple AI service for rapid integration."""

    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=settings.ANTHROPIC_API_KEY
        )

    def analyze_text(self, text: str, task: str) -> str:
        """Analyze text with AI."""

        # Check cache first (save API costs)
        cache_key = f"ai_{hash(text + task)}"
        if cached := cache.get(cache_key):
            return cached

        # Call Claude
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"{task}\n\nText to analyze:\n{text}"
            }]
        )

        result = message.content[0].text

        # Cache for 1 hour
        cache.set(cache_key, result, 3600)

        return result

# Usage in any view:
from ai_assistant.services.quick_ai import QuickAI

ai = QuickAI()
summary = ai.analyze_text(
    text=assessment.description,
    task="Summarize this assessment in 2-3 sentences"
)
```

### Step 2: Add AI to Your View

```python
# Example: Add AI summary to MANA assessment view
# src/mana/views.py

from ai_assistant.services.quick_ai import QuickAI

def assessment_detail(request, assessment_id):
    assessment = Assessment.objects.get(id=assessment_id)

    # Add AI summary (fast, cached)
    ai = QuickAI()
    ai_summary = ai.analyze_text(
        text=assessment.description,
        task="Extract 3 key needs from this MANA assessment"
    )

    context = {
        'assessment': assessment,
        'ai_summary': ai_summary,  # Pass to template
    }
    return render(request, 'mana/assessment_detail.html', context)
```

### Step 3: Display in Template

```html
<!-- src/templates/mana/assessment_detail.html -->

<!-- AI Summary Section -->
<div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
    <div class="flex items-center mb-2">
        <i class="fas fa-robot text-blue-600 mr-2"></i>
        <h3 class="text-lg font-semibold text-blue-900">AI-Powered Summary</h3>
        <span class="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
            Claude Sonnet 4
        </span>
    </div>
    <div class="text-gray-700">
        {{ ai_summary }}
    </div>
</div>
```

**That's it!** You now have AI-powered summaries in your module.

---

## Common AI Tasks

### 1. Text Summarization

```python
from ai_assistant.services.quick_ai import QuickAI

ai = QuickAI()

# Summarize long text
summary = ai.analyze_text(
    text=long_document,
    task="Create a 3-sentence executive summary"
)

# Extract key points
key_points = ai.analyze_text(
    text=workshop_responses,
    task="Extract the top 5 key themes as bullet points"
)
```

### 2. Classification

```python
# Classify community needs
needs = ai.analyze_text(
    text=community_description,
    task="""Classify the primary needs into these categories:
    - Health
    - Education
    - Infrastructure
    - Livelihood
    - Social Services

    Return ONLY the category name."""
)
```

### 3. Data Validation

```python
# Validate data quality
validation = ai.analyze_text(
    text=f"Population: {pop}, Households: {households}",
    task="""Check if this data is logically consistent.
    If population is 500 but households is 200, that's suspicious.
    Return: VALID or INVALID with brief reason."""
)
```

### 4. Question Answering

```python
# Answer questions about data
answer = ai.analyze_text(
    text=assessment_data,
    task=f"Question: {user_question}\n\nAnswer based on the data above."
)
```

---

## Advanced: Cultural Context

For Bangsamoro-specific content, always include cultural context:

```python
from ai_assistant.cultural_context import BangsomoroCulturalContext

cultural_context = BangsomoroCulturalContext()

def culturally_aware_analysis(text: str) -> str:
    """Analyze text with Bangsamoro cultural sensitivity."""

    ai = QuickAI()

    prompt = f"""{cultural_context.get_base_context()}

Task: Analyze the following community assessment and provide recommendations
that respect Bangsamoro cultural values, Islamic principles, and traditional governance.

Assessment:
{text}

Provide:
1. Key findings
2. Culturally appropriate recommendations
3. Stakeholder engagement suggestions (include traditional leaders)
"""

    return ai.analyze_text(text=prompt, task="Analyze with cultural sensitivity")
```

---

## Async Processing (For Heavy Tasks)

For long-running AI operations, use Celery:

```python
# src/ai_assistant/tasks.py
from celery import shared_task
from ai_assistant.services.quick_ai import QuickAI

@shared_task
def generate_report_async(assessment_id: int):
    """Generate AI report in background."""

    assessment = Assessment.objects.get(id=assessment_id)
    ai = QuickAI()

    report = ai.analyze_text(
        text=assessment.get_full_data(),
        task="""Generate a comprehensive MANA report with:
        1. Executive Summary
        2. Key Findings
        3. Priority Needs
        4. Recommendations
        5. Next Steps"""
    )

    # Save report
    assessment.ai_report = report
    assessment.save()

    return report

# In your view:
from ai_assistant.tasks import generate_report_async

def generate_report(request, assessment_id):
    # Trigger background task
    task = generate_report_async.delay(assessment_id)

    return JsonResponse({
        "status": "processing",
        "task_id": str(task.id),
        "message": "Report generation started. Check back in 2 minutes."
    })
```

---

## Cost Optimization: Caching

**Always cache AI responses** to save costs:

```python
from django.core.cache import cache
import hashlib

def cached_ai_call(text: str, task: str) -> str:
    """Call AI with caching."""

    # Generate cache key
    cache_key = f"ai_{hashlib.md5((text + task).encode()).hexdigest()}"

    # Check cache
    if cached := cache.get(cache_key):
        logger.info(f"Cache HIT: {cache_key}")
        return cached

    # Call AI
    ai = QuickAI()
    result = ai.analyze_text(text, task)

    # Cache for 24 hours
    cache.set(cache_key, result, 86400)

    return result
```

**Cache Strategy:**
- **24 hours**: Analysis results (assessments, summaries)
- **7 days**: Generated reports
- **30 days**: Classifications and validations
- **Never expire**: Embeddings (until content changes)

---

## Vector Search (Semantic Search)

For intelligent search across your data:

```python
# src/ai_assistant/services/vector_search.py
import faiss
import numpy as np
from openai import OpenAI

class VectorSearch:
    """Simple vector search for semantic queries."""

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.index = None
        self.metadata = {}

    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for text."""
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return np.array(response.data[0].embedding)

    def index_records(self, records: list):
        """Index records for search."""
        embeddings = []
        for record in records:
            embedding = self.embed_text(record['text'])
            embeddings.append(embedding)
            self.metadata[len(embeddings)-1] = record

        # Create FAISS index
        embeddings = np.array(embeddings).astype('float32')
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)

    def search(self, query: str, k: int = 5) -> list:
        """Search for similar records."""
        query_embedding = self.embed_text(query).reshape(1, -1).astype('float32')
        distances, indices = self.index.search(query_embedding, k)

        results = []
        for idx, distance in zip(indices[0], distances[0]):
            results.append({
                "record": self.metadata[idx],
                "similarity": 1 / (1 + distance)
            })

        return results

# Usage:
vector_search = VectorSearch()

# Index communities
communities = Community.objects.all()
vector_search.index_records([
    {"id": c.id, "text": f"{c.name} {c.needs_summary}"}
    for c in communities
])

# Search
results = vector_search.search("Tausug communities with health needs")
# Returns: Top 5 most relevant communities
```

---

## Module-Specific Quick Wins

### MANA Module: Auto-Summarize Responses

```python
# src/mana/views.py
from ai_assistant.services.quick_ai import QuickAI

def workshop_summary(request, workshop_id):
    workshop = Workshop.objects.get(id=workshop_id)
    responses = workshop.responses.all()

    # Aggregate responses
    all_text = "\n".join([r.answer for r in responses])

    # AI summary
    ai = QuickAI()
    summary = ai.analyze_text(
        text=all_text,
        task="""Analyze these workshop responses:
        1. Extract top 5 themes (with frequency)
        2. Identify priority needs
        3. Suggest interventions

        Format as markdown."""
    )

    return render(request, 'mana/workshop_summary.html', {
        'workshop': workshop,
        'ai_summary': summary
    })
```

### Communities Module: Validate Data

```python
# src/communities/forms.py
from ai_assistant.services.quick_ai import QuickAI

class CommunityForm(forms.ModelForm):
    def clean(self):
        data = super().clean()

        # AI validation
        ai = QuickAI()
        validation = ai.analyze_text(
            text=f"""
            Population: {data.get('population')}
            Households: {data.get('households')}
            Families: {data.get('families')}
            """,
            task="""Check if these numbers are logically consistent.
            Return: OK if valid, ERROR: [reason] if invalid."""
        )

        if "ERROR" in validation:
            raise forms.ValidationError(validation)

        return data
```

### Coordination Module: Match Stakeholders

```python
# src/coordination/views.py
from ai_assistant.services.quick_ai import QuickAI

def find_partners(request, community_id):
    community = Community.objects.get(id=community_id)
    ngos = NGO.objects.all()

    # Build context
    ngo_list = "\n".join([
        f"- {ngo.name}: {ngo.expertise} (Region: {ngo.region})"
        for ngo in ngos
    ])

    ai = QuickAI()
    recommendations = ai.analyze_text(
        text=f"""
        Community Needs: {community.needs_summary}
        Community Location: {community.region}

        Available NGOs:
        {ngo_list}
        """,
        task="""Recommend the top 3 best-fit NGOs for this community.
        Consider: expertise match, geographic proximity, past success.
        Format: NGO name | Match reason | Confidence (High/Medium/Low)"""
    )

    return render(request, 'coordination/partner_recommendations.html', {
        'community': community,
        'ai_recommendations': recommendations
    })
```

---

## Error Handling

Always handle AI errors gracefully:

```python
from ai_assistant.services.quick_ai import QuickAI
import logging

logger = logging.getLogger(__name__)

def safe_ai_call(text: str, task: str) -> str:
    """Call AI with error handling."""

    try:
        ai = QuickAI()
        result = ai.analyze_text(text, task)
        return result

    except Exception as e:
        logger.error(f"AI call failed: {str(e)}")

        # Fallback: Return safe default
        return "AI analysis unavailable. Please try again later."

# In views:
ai_summary = safe_ai_call(assessment.text, "Summarize this")
# Will never crash your view!
```

---

## Testing AI Features

```python
# src/ai_assistant/tests/test_quick_ai.py
from django.test import TestCase
from ai_assistant.services.quick_ai import QuickAI

class QuickAITests(TestCase):

    def test_summarization(self):
        """Test AI summarization."""
        ai = QuickAI()

        text = "Long assessment text here..."
        summary = ai.analyze_text(text, "Summarize in one sentence")

        # Check response
        self.assertIsNotNone(summary)
        self.assertGreater(len(summary), 0)
        self.assertLess(len(summary), len(text))  # Summary is shorter

    def test_caching(self):
        """Test that identical requests are cached."""
        from django.core.cache import cache

        ai = QuickAI()
        text = "Test text"
        task = "Summarize"

        # First call (not cached)
        result1 = ai.analyze_text(text, task)

        # Second call (should be cached)
        result2 = ai.analyze_text(text, task)

        # Results should be identical (from cache)
        self.assertEqual(result1, result2)
```

---

## Monitoring & Debugging

Track AI usage and costs:

```python
# src/ai_assistant/middleware.py
from django.utils import timezone
import logging

logger = logging.getLogger('ai_usage')

def log_ai_usage(user, operation, tokens_used, cost):
    """Log AI usage for monitoring."""

    logger.info(f"""
    AI Usage:
    - User: {user.username}
    - Operation: {operation}
    - Tokens: {tokens_used}
    - Cost: ${cost:.4f}
    - Timestamp: {timezone.now()}
    """)

    # Save to database
    AIUsageLog.objects.create(
        user=user,
        operation=operation,
        tokens_used=tokens_used,
        cost=cost
    )

# In your AI service:
class QuickAI:
    def analyze_text(self, text, task):
        # ... AI call ...

        # Log usage
        log_ai_usage(
            user=request.user,
            operation="analyze_text",
            tokens_used=len(text.split()) + len(result.split()),
            cost=0.002  # Estimate
        )

        return result
```

---

## Production Checklist

Before deploying AI features:

- [ ] **API Keys**: Stored in environment variables (not code)
- [ ] **Caching**: Enabled (Redis) with appropriate TTLs
- [ ] **Error Handling**: All AI calls wrapped in try/except
- [ ] **Rate Limiting**: Implement request throttling if needed
- [ ] **Monitoring**: Log all AI usage and costs
- [ ] **Fallbacks**: Provide non-AI alternatives when AI fails
- [ ] **Cultural Validation**: Apply Bangsamoro context for sensitive content
- [ ] **User Communication**: Label all AI-generated content clearly
- [ ] **Cost Alerts**: Set up budget monitoring (>$100/month trigger alert)

---

## Cost Estimates

**Claude Sonnet 4 Pricing:**
- Input: $3 per 1M tokens
- Output: $15 per 1M tokens

**Example Monthly Costs:**

| Use Case | Daily Calls | Avg Tokens | Monthly Cost |
|----------|-------------|------------|--------------|
| Assessment Summaries | 50 | 500 in, 200 out | $13.50 |
| Data Validation | 100 | 200 in, 50 out | $7.50 |
| Report Generation | 20 | 2000 in, 1000 out | $24.00 |
| **Total** | **170** | - | **$45.00** |

**With 80% cache hit rate:** $9/month

---

## Next Steps

1. **Try the 5-Minute Integration** above
2. **Read the full strategy**: [AI_STRATEGY_COMPREHENSIVE.md](AI_STRATEGY_COMPREHENSIVE.md)
3. **Explore existing AI code**: `src/ai_assistant/`
4. **Join AI discussions**: Ask in #ai-integration Slack channel

---

## Resources

- [Anthropic Claude Docs](https://docs.anthropic.com)
- [OBCMS AI Strategy](AI_STRATEGY_COMPREHENSIVE.md)
- [Cultural Context Framework](../../src/ai_assistant/cultural_context.py)
- [Example AI Views](../../src/ai_assistant/views.py)

---

**Questions?** Contact the AI Engineering Team or consult the comprehensive strategy document.

**Happy AI Coding!** 🤖
