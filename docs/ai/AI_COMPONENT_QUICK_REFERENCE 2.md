# OBCMS AI Components - Quick Reference

**Last Updated:** October 6, 2025
**Version:** 1.0

---

## 🚀 Quick Start

### 1. Display AI Insights

```django
{% include "components/ai_insight_card.html" with
   insight_id="my-analysis"
   title="AI Analysis"
   data=ai_data
   color="emerald" %}
```

### 2. Add AI Action Button

```django
{% include "components/ai_action_button.html" with
   action_id="run-analysis"
   action_url="{% url 'my_module:ai_analyze' object.id %}"
   button_text="Run AI Analysis"
   icon="fa-brain" %}
```

### 3. Show Operation Status

```django
{% include "components/ai_status_indicator.html" with
   operation_id=task_id
   status="processing"
   progress=45 %}
```

### 4. Display Results

```django
{% include "components/ai_results_panel.html" with
   results_id="results-1"
   results=ai_results
   show_export=True %}
```

---

## 📋 Component Cheat Sheet

### AI Insight Card

**Required:**
- `insight_id` - Unique ID
- `data` - Insight data dict

**Optional:**
- `title` - Card title (default: "AI Analysis")
- `icon` - FontAwesome icon (default: "fa-brain")
- `color` - emerald|blue|purple|teal (default: "emerald")
- `api_endpoint` - URL for HTMX loading
- `loading` - Show loading state (default: False)
- `compact` - Compact layout (default: False)
- `show_confidence` - Show confidence score (default: True)
- `show_actions` - Show action buttons (default: True)

**Data Structure:**
```python
{
    'summary': 'Text summary',
    'confidence': 0.92,  # 0-1 float
    'sentiment': 'positive',  # positive|negative|neutral|mixed
    'key_points': ['Point 1', 'Point 2'],
    'recommendations': ['Action 1', 'Action 2'],
    'metrics': {'label': 'Count', 'value': 42, 'icon': 'fa-chart'},
    'error': False,
    'error_message': ''
}
```

---

### AI Action Button

**Required:**
- `action_id` - Unique ID
- `action_url` - POST endpoint URL

**Optional:**
- `button_text` - Button label (default: "Run AI Analysis")
- `icon` - FontAwesome icon (default: "fa-brain")
- `color` - emerald|blue|purple|teal (default: "emerald")
- `size` - sm|md|lg (default: "md")
- `variant` - primary|secondary|outline (default: "primary")
- `loading_text` - Loading message (default: "Processing...")
- `success_text` - Success message (default: "Complete")
- `target` - HTMX target element ID
- `swap` - HTMX swap strategy (default: "innerHTML")
- `confirm` - Confirmation message (optional)
- `disabled` - Disable button (default: False)
- `full_width` - Full width button (default: False)

**Variants:**
- `primary` - Gradient background (default)
- `secondary` - White with border
- `outline` - Transparent with border

---

### AI Status Indicator

**Required:**
- `operation_id` - Unique ID
- `status` - queued|processing|complete|error|cancelled

**Optional:**
- `title` - Operation title (default: "AI Operation")
- `progress` - 0-100 percentage (default: 0)
- `eta` - Seconds remaining (optional)
- `message` - Status message (optional)
- `cancellable` - Show cancel button (default: True)
- `compact` - Compact layout (default: False)
- `auto_refresh` - Auto-refresh via HTMX (default: False)
- `refresh_url` - Status polling URL
- `refresh_interval` - Polling interval in ms (default: 2000)

**Status Colors:**
- `queued` - Blue
- `processing` - Emerald (with spinner)
- `complete` - Green
- `error` - Red
- `cancelled` - Gray

---

### AI Results Panel

**Required:**
- `results_id` - Unique ID
- `results` - Results data dict

**Optional:**
- `title` - Panel title (default: "AI Analysis Results")
- `icon` - FontAwesome icon (default: "fa-chart-line")
- `color` - emerald|blue|purple|teal (default: "blue")
- `format` - text|markdown|json|table (default: "text")
- `show_export` - Show export buttons (default: True)
- `show_copy` - Show copy button (default: True)
- `show_metadata` - Show metadata footer (default: True)
- `collapsible` - Collapsible panel (default: False)

**Results Structure:**
```python
{
    'content': 'Main content (text/markdown)',
    'format': 'text',
    'metadata': {
        'model': 'claude-sonnet-4',
        'timestamp': '2025-10-06 14:30:00',
        'tokens': 1250,
        'processing_time': 3.5,
        'confidence': 0.92
    },
    'structured_data': {
        # For JSON: any dict
        # For table: {'headers': [...], 'rows': [[...], [...]]}
    },
    'highlights': ['Key point 1', 'Key point 2'],
    'citations': ['Source 1', 'Source 2']
}
```

---

## 🎨 Icon Reference

### AI Icons
- `fa-brain` - General AI (primary)
- `fa-robot` - AI assistant
- `fa-sparkles` - AI enhancement
- `fa-lightbulb` - Insights
- `fa-magic` - AI-powered

### Status Icons
- `fa-check-circle` - Success
- `fa-exclamation-circle` - Error
- `fa-clock` - Queued
- `fa-cog fa-spin` - Processing
- `fa-ban` - Cancelled

### Module Icons
- `fa-map-marked-alt` - MANA
- `fa-users` - Communities
- `fa-handshake` - Coordination
- `fa-file-contract` - Policy
- `fa-project-diagram` - Projects

---

## 🎨 Color Palette

### AI Colors
- `emerald-600` - Primary AI, success
- `blue-600` - Information, data
- `purple-600` - Advanced ML
- `teal-600` - Processing
- `amber-500` - Insights, warnings

### Status Colors
- `emerald-600` - Success
- `red-600` - Error
- `blue-600` - Processing
- `amber-600` - Warning
- `gray-600` - Inactive

---

## 🔔 JavaScript Functions

### Notifications
```javascript
showAINotification('Message', 'success');  // Green
showAINotification('Message', 'error');    // Red
showAINotification('Message', 'warning');  // Amber
showAINotification('Message', 'info');     // Blue
```

### Status Updates
```javascript
updateAIProgress('operation-id', 75, 'Processing...');
updateETA('operation-id', 30);  // 30 seconds
updateStage('operation-id', 'Extracting themes...');
```

### Operations
```javascript
cancelAIOperation('operation-id');
retryAIOperation('operation-id');
refreshAIInsights('insight-id');
```

### Results
```javascript
exportResults('results-id', 'pdf');
exportResults('results-id', 'docx');
exportResults('results-id', 'json');
exportResults('results-id', 'csv');
copyResults('results-id');
```

---

## 🔗 Backend Integration

### Simple View

```python
from django.shortcuts import render
from my_module.ai_services import MyAnalyzer

def ai_analyze(request, object_id):
    obj = MyModel.objects.get(id=object_id)

    # Run AI
    analyzer = MyAnalyzer()
    results = analyzer.analyze(obj.data)

    # Return component
    if request.headers.get('HX-Request'):
        return render(request, 'components/ai_insight_card.html', {
            'insight_id': f'analysis-{object_id}',
            'data': results
        })

    return JsonResponse(results)
```

### Long-Running Task

```python
from celery import shared_task
from my_module.models import AIOperation

@shared_task(bind=True)
def run_analysis(self, object_id):
    operation = AIOperation.objects.create(
        object_id=object_id,
        status='processing',
        task_id=self.request.id
    )

    try:
        # Run AI
        analyzer = MyAnalyzer()
        results = analyzer.analyze(object_id)

        # Complete
        operation.status = 'complete'
        operation.results = results
        operation.save()

    except Exception as e:
        operation.status = 'error'
        operation.error_message = str(e)
        operation.save()
        raise
```

### Status Endpoint

```python
def ai_status(request, task_id):
    operation = AIOperation.objects.get(task_id=task_id)

    return render(request, 'components/ai_status_indicator.html', {
        'operation_id': task_id,
        'status': operation.status,
        'progress': operation.progress,
        'message': operation.message,
        'eta': operation.eta
    })
```

---

## 📱 Responsive Patterns

### Grid Layouts
```django
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {% include "components/ai_insight_card.html" ... %}
</div>
```

### Text Sizes
```html
<h3 class="text-base md:text-lg lg:text-xl">
```

### Touch Targets
```html
<button class="min-h-[48px] py-2.5 px-4">
```

---

## ♿ Accessibility

### ARIA Labels
```html
<button aria-label="Run AI analysis">
    <i class="fas fa-brain"></i>
</button>
```

### Live Regions
```html
<div role="status" aria-live="polite">
    Processing...
</div>
```

### Screen Reader Only
```html
<span class="sr-only">Loading</span>
```

---

## 🧪 Testing Snippets

### Component Render Test
```python
def test_ai_insight_card(self):
    response = self.client.get('/my-view/')
    self.assertContains(response, 'ai-insight-')
    self.assertContains(response, 'AI Analysis')
```

### HTMX Request Test
```python
def test_ai_action_htmx(self):
    response = self.client.post(
        '/ai/analyze/1/',
        HTTP_HX_REQUEST='true'
    )
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'ai-insight-card')
```

---

## 📚 Documentation Links

- **Full Documentation:** `/docs/ai/AI_UNIFIED_COMPONENT_SYSTEM.md`
- **Implementation Summary:** `/AI_INTERFACE_UNIFICATION_COMPLETE.md`
- **Component Source:** `/src/templates/components/ai_*.html`

---

## 🎯 Common Patterns

### Pattern 1: Simple AI Button + Results
```django
{% include "components/ai_action_button.html" with
   action_id="analyze"
   action_url="{% url 'module:ai_analyze' pk %}"
   target="#results" %}

<div id="results"></div>
```

### Pattern 2: Status Polling
```django
{% include "components/ai_status_indicator.html" with
   operation_id=task_id
   status="processing"
   auto_refresh=True
   refresh_url="{% url 'module:ai_status' task_id %}" %}
```

### Pattern 3: Results with Export
```django
{% include "components/ai_results_panel.html" with
   results_id="analysis"
   results=data
   show_export=True
   collapsible=True %}
```

---

## 💡 Pro Tips

1. **Always use unique IDs** - Prevents conflicts with multiple components
2. **Use HTMX targets** - For seamless updates without page refresh
3. **Show loading states** - User feedback during AI processing
4. **Handle errors gracefully** - Provide retry options
5. **Display confidence** - Transparency builds trust
6. **Mobile-first** - Test on small screens
7. **Accessibility matters** - Use ARIA labels and keyboard nav

---

**Quick Reference v1.0 - October 2025**
