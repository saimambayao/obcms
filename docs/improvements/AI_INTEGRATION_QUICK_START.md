# AI Integration Quick Start Guide

**For developers implementing AI backend endpoints**

---

## 5-Minute Setup

### 1. Add AI URLs to Your Module

**File:** `src/{your_module}/urls.py`

```python
from django.urls import path
from . import ai_views

urlpatterns = [
    # ... existing URLs ...

    # AI Endpoints (GET - returns HTML fragments)
    path('object/<int:pk>/ai/feature-name/',
         ai_views.ai_feature_name,
         name='ai_feature_name'),

    # AI Report Generation (POST - returns HTML fragment)
    path('object/<int:pk>/ai/generate-report/',
         ai_views.ai_generate_report,
         name='ai_generate_report'),
]
```

---

### 2. Create AI Views File

**File:** `src/{your_module}/ai_views.py`

```python
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import YourModel

@login_required
def ai_feature_name(request, pk):
    """
    AI-powered feature analysis.
    Returns HTML fragment with analysis results.
    """
    obj = get_object_or_404(YourModel, pk=pk)

    # TODO: Replace with real AI service call
    # from ai_assistant.services import analyze_feature
    # result = analyze_feature(obj)

    # Placeholder data
    context = {
        'object': obj,
        'ai_result': 'Placeholder AI result',
        'confidence': 0.85,
    }

    return render(request, f'{your_module}/partials/ai_feature_name.html', context)


@login_required
def ai_generate_report(request, pk):
    """
    Generate AI report for object.
    Returns HTML fragment with download link or error.
    """
    if request.method != 'POST':
        return HttpResponse('Method not allowed', status=405)

    obj = get_object_or_404(YourModel, pk=pk)

    # TODO: Replace with real AI service call
    # from ai_assistant.services import generate_report
    # report_url = generate_report(obj)

    context = {
        'success': True,
        'message': 'Report generated successfully!',
        'download_url': '#',  # TODO: Real URL
    }

    return render(request, f'{your_module}/partials/ai_report_result.html', context)
```

---

### 3. Create Partial Templates

**Directory:** `src/templates/{your_module}/partials/`

**File:** `ai_feature_name.html`

```html
<div class="space-y-3">
    <div class="flex items-center justify-between">
        <span class="text-sm font-medium text-gray-700">Confidence</span>
        <span class="text-lg font-bold text-emerald-600">{{ confidence|floatformat:0 }}%</span>
    </div>

    <div class="w-full bg-gray-200 rounded-full h-2">
        <div class="bg-emerald-500 h-2 rounded-full" style="width: {{ confidence|multiply:100 }}%"></div>
    </div>

    <div class="mt-4">
        <p class="text-sm text-gray-700">{{ ai_result }}</p>
    </div>
</div>
```

**File:** `ai_report_result.html`

```html
{% if success %}
<div class="bg-emerald-50 border border-emerald-200 rounded-lg p-3">
    <div class="flex items-start gap-2">
        <i class="fas fa-check-circle text-emerald-600 mt-0.5"></i>
        <div class="flex-1">
            <p class="text-sm font-medium text-emerald-900">{{ message }}</p>
            {% if download_url %}
            <a href="{{ download_url }}"
               class="inline-flex items-center gap-1 mt-2 text-xs text-emerald-700 hover:text-emerald-900">
                <i class="fas fa-download"></i>
                <span>Download Report</span>
            </a>
            {% endif %}
        </div>
    </div>
</div>
{% else %}
<div class="bg-red-50 border border-red-200 rounded-lg p-3">
    <div class="flex items-start gap-2">
        <i class="fas fa-exclamation-circle text-red-600 mt-0.5"></i>
        <div class="flex-1">
            <p class="text-sm font-medium text-red-900">{{ message }}</p>
        </div>
    </div>
</div>
{% endif %}
```

---

### 4. Add AI Section to Detail Page

**File:** `src/templates/{your_module}/object_detail.html`

**At the bottom of your detail page (before `{% endblock %}`):**

```django
{% comment %}AI Insights Section{% endcomment %}
{% include "{your_module}/ai_insights_section.html" with object=your_object %}
```

---

### 5. Test It

1. Navigate to object detail page
2. Verify AI section loads at bottom
3. Check loading spinners appear
4. Click "Generate Report" button
5. Verify placeholder responses display

---

## Module-Specific Templates Available

### Communities Module
```django
{% include "communities/ai_insights_section.html" with community=community %}
```

**Features:**
- Similar Communities
- Needs Classification
- Data Quality Score
- Quick Insights

---

### MANA Module
```django
{% extends 'mana/mana_assessment_detail.html' %}
{% comment %}or use ai_insights_section.html{% endcomment %}
```

**Features:**
- Response Analysis
- Theme Extraction
- Cultural Validation
- Similar Assessments

---

### Coordination Module
```django
{% include "coordination/ai_insights_section.html" with organization=organization %}
```

**Features:**
- Stakeholder Matching
- Partnership Predictions
- Meeting Intelligence
- Resource Optimization

---

### Policy Module
```django
{% include "recommendations/policy_tracking/ai_insights_section.html" with policy=policy %}
```

**Features:**
- Evidence Gathering
- Policy Suggestions
- Impact Simulation
- Compliance Check

---

### Project Central (M&E) Module
```django
{% include "project_central/ai_insights_section.html" with project=project %}
```

**Features:**
- Anomaly Detection
- Performance Forecasting
- Risk Analysis
- Resource Optimization

---

## Common AI Chat Integration

**Already integrated in `base.html`!**

Just create this endpoint:

**File:** `src/common/urls.py`

```python
from django.urls import path
from .views import chat

urlpatterns = [
    # ... existing URLs ...
    path('ai/chat/', chat.ai_chat, name='ai_chat'),
]
```

**File:** `src/common/views/chat.py`

```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

@login_required
def ai_chat(request):
    if request.method != 'POST':
        return HttpResponse('Method not allowed', status=405)

    message = request.POST.get('message', '').strip()

    # TODO: Integrate with AI service
    response = f"You asked: '{message}'. AI coming soon!"

    context = {
        'message': message,
        'response': response,
        'timestamp': 'Just now'
    }

    return render(request, 'common/partials/chat_message.html', context)
```

**File:** `src/templates/common/partials/chat_message.html`

```html
<!-- User message -->
<div class="flex justify-end">
    <div class="bg-blue-100 rounded-lg p-3 max-w-[80%]">
        <p class="text-sm text-gray-900">{{ message }}</p>
        <p class="text-xs text-gray-500 mt-1">{{ timestamp }}</p>
    </div>
</div>

<!-- AI response -->
<div class="bg-emerald-50 border border-emerald-200 rounded-lg p-3">
    <div class="flex items-start gap-2">
        <i class="fas fa-robot text-emerald-600 mt-0.5"></i>
        <div class="flex-1">
            <p class="text-sm text-gray-700">{{ response }}</p>
            <p class="text-xs text-gray-500 mt-1">{{ timestamp }}</p>
        </div>
    </div>
</div>
```

---

## Error Handling Template

**Create this for all modules:**

**File:** `src/templates/{your_module}/partials/ai_error.html`

```html
<div class="bg-red-50 border border-red-200 rounded-lg p-3">
    <div class="flex items-start gap-2">
        <i class="fas fa-exclamation-triangle text-red-600 mt-0.5"></i>
        <div class="flex-1">
            <p class="text-sm font-medium text-red-900">{{ error_title|default:"AI Service Error" }}</p>
            <p class="text-xs text-red-700 mt-1">{{ error_message|default:"Please try again later or contact support." }}</p>
        </div>
    </div>
</div>
```

**Use in views:**

```python
try:
    result = ai_service.process(obj)
    return render(request, 'partials/success.html', {'result': result})
except Exception as e:
    return render(request, 'partials/ai_error.html', {
        'error_title': 'Analysis Failed',
        'error_message': 'Unable to analyze data. Please try again later.'
    })
```

---

## HTMX Patterns Reference

### Load on Page Load
```html
<div hx-get="{% url 'module:endpoint' object.id %}"
     hx-trigger="load"
     hx-swap="innerHTML">
    Loading...
</div>
```

### Button Click (POST)
```html
<button hx-post="{% url 'module:endpoint' object.id %}"
        hx-target="#result"
        hx-swap="innerHTML"
        hx-indicator="#spinner">
    Generate Report
    <i id="spinner" class="fas fa-spinner fa-spin htmx-indicator"></i>
</button>
<div id="result"></div>
```

### Form Submission
```html
<form hx-post="{% url 'module:endpoint' %}"
      hx-target="#result"
      hx-swap="innerHTML">
    {% csrf_token %}
    <input type="text" name="field">
    <button type="submit">Submit</button>
</form>
```

---

## Testing Checklist

- [ ] URL route added to urls.py
- [ ] View function created in ai_views.py
- [ ] Partial templates created
- [ ] AI section included in detail page
- [ ] Page loads without errors
- [ ] HTMX requests trigger correctly
- [ ] Loading spinners show
- [ ] Responses render properly
- [ ] Error states display correctly

---

## Next: Integrate Real AI Services

1. Import AI service: `from ai_assistant.services import your_service`
2. Replace placeholder data with real AI calls
3. Add error handling and caching
4. Test with real data
5. Deploy module by module

---

## Need Help?

- **Full Documentation:** `/docs/improvements/AI_TEMPLATE_INTEGRATION_SUMMARY.md`
- **UI Standards:** `/docs/ui/OBCMS_UI_COMPONENTS_STANDARDS.md`
- **HTMX Docs:** https://htmx.org/docs/

---

**Status:** ✅ Ready to implement! Start with placeholder data, test, then integrate real AI services.
