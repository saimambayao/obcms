# AI URL Configuration Summary

**Date:** 2025-10-06
**Status:** Complete - All AI endpoints configured
**Migration Phase:** URL Infrastructure Setup

## Overview

This document provides a comprehensive summary of all AI endpoints configured across the OBCMS system. The URL configuration enables frontend widgets and HTMX components to access AI-powered features through RESTful endpoints.

---

## URL Configuration by Module

### 1. Communities Module

**File:** `src/communities/urls.py`
**Namespace:** `communities`
**Base URL:** `/communities/`

#### AI Endpoints

| Endpoint | View Function | Purpose | Status |
|----------|--------------|---------|--------|
| `ai/similar/<int:pk>/` | `ai_similar_communities` | Find similar communities using AI matching | ⚠️ View Missing |
| `ai/classify-needs/<int:pk>/` | `ai_classify_needs` | Classify community needs using AI | ⚠️ View Missing |
| `ai/generate-report/<int:pk>/` | `ai_generate_report` | Generate community profile reports | ⚠️ View Missing |
| `ai/validate-data/<int:pk>/` | `ai_validate_data` | Validate community data quality | ⚠️ View Missing |

#### AI Services Available

- `CommunityDataValidator` - Data validation service (implemented)
- `CommunityNeedsClassifier` - Needs classification service (implemented)
- `CommunityMatcher` - Similarity matching service (implemented)

#### Example Usage

```html
<!-- Find similar communities -->
<button
    hx-get="{% url 'communities:ai-similar' community.id %}"
    hx-target="#similar-communities"
    class="btn-primary">
    Find Similar Communities
</button>

<!-- Classify needs -->
<div
    hx-get="{% url 'communities:ai-classify-needs' community.id %}"
    hx-trigger="load">
    Loading needs classification...
</div>
```

---

### 2. MANA Module (Mapping & Needs Assessment)

**File:** `src/mana/urls.py`
**Namespace:** `mana`
**Base URL:** `/mana/workshops/`

#### AI Endpoints

| Endpoint | View Function | Purpose | Status |
|----------|--------------|---------|--------|
| `workshop/<int:workshop_id>/ai-analysis/` | `workshop_ai_analysis` | Display AI analysis dashboard | ✅ Implemented |
| `workshop/<int:workshop_id>/analyze/` | `trigger_workshop_analysis` | Trigger async AI analysis | ✅ Implemented |
| `workshop/<int:workshop_id>/analysis/status/` | `analysis_status` | Check analysis status (polling) | ✅ Implemented |
| `workshop/<int:workshop_id>/generate-report/` | `generate_report` | Generate assessment report | ✅ Implemented |
| `workshop/<int:workshop_id>/report/status/` | `report_status` | Check report generation status | ✅ Implemented |
| `workshop/<int:workshop_id>/themes/` | `theme_analysis` | Display theme analysis | ✅ Implemented |
| `workshop/<int:workshop_id>/needs/` | `needs_analysis` | Display needs analysis | ✅ Implemented |
| `workshop/<int:workshop_id>/export-analysis/` | `export_analysis_json` | Export analysis as JSON | ✅ Implemented |
| `validate-content/` | `validate_content` | Validate cultural appropriateness | ✅ Implemented |

#### AI Services Available

- `ResponseAnalyzer` - Analyzes workshop responses (implemented)
- `ThemeExtractor` - Extracts themes from responses (implemented)
- `NeedsExtractor` - Identifies and ranks needs (implemented)
- `AssessmentReportGenerator` - Generates comprehensive reports (implemented)
- `BangsomoroCulturalValidator` - Cultural sensitivity validation (implemented)

#### Example Usage

```html
<!-- Trigger AI analysis -->
<button
    hx-post="{% url 'mana:trigger_workshop_analysis' workshop.id %}"
    hx-target="#analysis-results"
    hx-swap="outerHTML"
    class="btn-primary">
    Analyze Workshop Responses
</button>

<!-- Poll for status -->
<div
    id="analysis-status"
    hx-get="{% url 'mana:analysis_status' workshop.id %}"
    hx-trigger="every 2s"
    hx-swap="outerHTML">
    Loading...
</div>
```

---

### 3. Coordination Module

**File:** `src/coordination/urls.py` (NEW)
**Namespace:** `coordination`
**Base URL:** `/coordination/`

#### AI Endpoints

| Endpoint | View Function | Purpose | Status |
|----------|--------------|---------|--------|
| `ai/match-stakeholders/<int:pk>/` | `ai_match_stakeholders` | Match stakeholders for partnerships | ⚠️ View Missing |
| `ai/predict-partnerships/<int:pk>/` | `ai_predict_partnerships` | Predict partnership success | ⚠️ View Missing |
| `ai/meeting-intelligence/<int:pk>/` | `ai_meeting_intelligence` | Meeting notes AI analysis | ⚠️ View Missing |
| `ai/optimize-resources/<int:pk>/` | `ai_optimize_resources` | Optimize resource allocation | ⚠️ View Missing |

#### AI Services Available

- `StakeholderMatcher` - Match stakeholders based on capabilities (implemented)
- `PartnershipPredictor` - Predict partnership viability (implemented)
- `MeetingIntelligence` - Analyze meeting notes and extract action items (implemented)
- `ResourceOptimizer` - Optimize resource allocation across projects (implemented)

#### Example Usage

```html
<!-- Match stakeholders -->
<button
    hx-get="{% url 'coordination:ai-match-stakeholders' organization.id %}"
    hx-target="#stakeholder-matches"
    class="btn-ai">
    <i class="fas fa-brain"></i> Find Compatible Partners
</button>

<!-- Meeting intelligence -->
<div
    hx-post="{% url 'coordination:ai-meeting-intelligence' meeting.id %}"
    hx-include="#meeting-notes"
    hx-target="#action-items">
    <button class="btn-secondary">Extract Action Items</button>
</div>
```

---

### 4. Policy Module (Recommendations)

**File:** `src/recommendations/policies/urls.py` (NEW)
**Namespace:** `policies`
**Base URL:** `/policies/`

#### AI Endpoints

| Endpoint | View Function | Purpose | Status |
|----------|--------------|---------|--------|
| `ai/gather-evidence/<int:pk>/` | `ai_gather_evidence` | Gather evidence for policy | ⚠️ View Missing |
| `ai/generate-policy/<int:pk>/` | `ai_generate_policy` | Generate policy draft | ⚠️ View Missing |
| `ai/simulate-impact/<int:pk>/` | `ai_simulate_impact` | Simulate policy impact | ⚠️ View Missing |
| `ai/check-compliance/<int:pk>/` | `ai_check_compliance` | Check legal compliance | ⚠️ View Missing |

#### AI Services Available

- `EvidenceGatherer` - Gather evidence from MANA and community data (implemented)
- `PolicyGenerator` - Generate policy drafts with AI assistance (implemented)
- `ImpactSimulator` - Simulate policy impacts on communities (implemented)
- `ComplianceChecker` - Check policy compliance with BARMM laws (implemented)

#### Example Usage

```html
<!-- Gather evidence -->
<button
    hx-post="{% url 'policies:ai-gather-evidence' policy.id %}"
    hx-target="#evidence-panel"
    class="btn-ai">
    Gather Supporting Evidence
</button>

<!-- Simulate impact -->
<div
    hx-get="{% url 'policies:ai-simulate-impact' policy.id %}"
    hx-trigger="revealed"
    hx-swap="innerHTML">
    <div class="spinner">Simulating impact...</div>
</div>
```

---

### 5. Project Central (Project Management Portal)

**File:** `src/project_central/urls.py`
**Namespace:** `project_central`
**Base URL:** `/project-management/`

#### AI Endpoints

| Endpoint | View Function | Purpose | Status |
|----------|--------------|---------|--------|
| `ai/detect-anomalies/<uuid:pk>/` | `ai_detect_anomalies` | Detect budget/schedule anomalies | ⚠️ View Missing |
| `ai/forecast-performance/<uuid:pk>/` | `ai_forecast_performance` | Forecast project performance | ⚠️ View Missing |
| `ai/analyze-risks/<uuid:pk>/` | `ai_analyze_risks` | Analyze project risks | ⚠️ View Missing |
| `ai/generate-report/<uuid:pk>/` | `ai_generate_report` | Generate project reports | ⚠️ View Missing |

#### AI Services Available

- `AnomalyDetector` - Detect anomalies in project data (implemented)
- `PerformanceForecaster` - Forecast EVM performance (implemented)
- `RiskAnalyzer` - Analyze project risks and dependencies (implemented)
- `ReportGenerator` - Generate comprehensive project reports (implemented)

#### Example Usage

```html
<!-- Detect anomalies -->
<button
    hx-get="{% url 'project_central:ai-detect-anomalies' project.id %}"
    hx-target="#anomaly-alerts"
    class="btn-warning">
    <i class="fas fa-exclamation-triangle"></i> Check for Anomalies
</button>

<!-- Forecast performance -->
<div
    id="performance-forecast"
    hx-get="{% url 'project_central:ai-forecast-performance' project.id %}"
    hx-trigger="load delay:1s">
    Loading forecast...
</div>
```

---

### 6. Common Module (Cross-cutting AI Features)

**File:** `src/common/urls.py`
**Namespace:** `common`
**Base URL:** `/`

#### AI Endpoints

| Endpoint | View Function | Purpose | Status |
|----------|--------------|---------|--------|
| `chat/message/` | `chat_message` | Send message to AI assistant | ✅ Implemented |
| `chat/history/` | `chat_history` | Retrieve chat history | ✅ Implemented |
| `chat/clear/` | `clear_chat_history` | Clear chat history | ✅ Implemented |
| `chat/stats/` | `chat_stats` | Chat usage statistics | ✅ Implemented |
| `chat/capabilities/` | `chat_capabilities` | Get AI capabilities | ✅ Implemented |
| `chat/suggestion/` | `chat_suggestion` | Get contextual suggestions | ✅ Implemented |
| `search/` | `unified_search_view` | Unified AI-powered search | ✅ Implemented |
| `search/autocomplete/` | `search_autocomplete` | Search autocomplete | ✅ Implemented |
| `search/stats/` | `search_stats` | Search analytics | ✅ Implemented |
| `search/reindex/<str:module>/` | `reindex_module` | Reindex module for search | ✅ Implemented |

#### AI Services Available

- `UnifiedSearchService` - Intelligent cross-module search (implemented)
- `QueryParser` - Parse natural language queries (implemented)
- `ResultRanker` - Rank search results by relevance (implemented)
- `SearchAnalytics` - Track and analyze search patterns (implemented)

---

## URL Namespace Structure

### Complete URL Mapping

```
http://localhost:8000/
│
├── communities/
│   └── ai/
│       ├── similar/<pk>/
│       ├── classify-needs/<pk>/
│       ├── generate-report/<pk>/
│       └── validate-data/<pk>/
│
├── coordination/
│   └── ai/
│       ├── match-stakeholders/<pk>/
│       ├── predict-partnerships/<pk>/
│       ├── meeting-intelligence/<pk>/
│       └── optimize-resources/<pk>/
│
├── policies/
│   └── ai/
│       ├── gather-evidence/<pk>/
│       ├── generate-policy/<pk>/
│       ├── simulate-impact/<pk>/
│       └── check-compliance/<pk>/
│
├── mana/workshops/
│   └── workshop/<workshop_id>/
│       ├── ai-analysis/
│       ├── analyze/
│       ├── analysis/status/
│       ├── generate-report/
│       ├── report/status/
│       ├── themes/
│       ├── needs/
│       └── export-analysis/
│
├── project-management/
│   └── ai/
│       ├── detect-anomalies/<uuid>/
│       ├── forecast-performance/<uuid>/
│       ├── analyze-risks/<uuid>/
│       └── generate-report/<uuid>/
│
└── (common - root level)
    ├── chat/
    │   ├── message/
    │   ├── history/
    │   ├── clear/
    │   ├── stats/
    │   ├── capabilities/
    │   └── suggestion/
    └── search/
        ├── (root)
        ├── autocomplete/
        ├── stats/
        └── reindex/<module>/
```

---

## Implementation Status Summary

### ✅ Fully Implemented (100%)

**MANA Module:**
- 9/9 AI endpoints implemented
- All view functions exist
- All AI services integrated
- HTMX patterns established
- Celery async tasks configured

**Common Module:**
- 10/10 AI endpoints implemented
- Chat assistant fully functional
- Unified search operational
- Analytics tracking active

### ⚠️ Services Implemented, Views Pending (80%)

**Communities Module:**
- 0/4 view functions implemented
- 3/3 AI services implemented
- URL routing configured
- **Action Required:** Implement view functions

**Coordination Module:**
- 0/4 view functions implemented
- 4/4 AI services implemented
- URL routing configured
- **Action Required:** Implement view functions

**Policy Module:**
- 0/4 view functions implemented
- 4/4 AI services implemented
- URL routing configured
- **Action Required:** Implement view functions

**Project Central Module:**
- 0/4 view functions implemented
- 4/4 AI services implemented
- URL routing configured
- **Action Required:** Implement view functions

---

## Next Steps: View Implementation

### Priority Order

1. **CRITICAL: Communities Module** (core data source)
2. **HIGH: Project Central Module** (budget monitoring)
3. **MEDIUM: Policy Module** (evidence-based recommendations)
4. **MEDIUM: Coordination Module** (stakeholder management)

### View Implementation Template

Each view should follow this pattern (based on MANA's successful implementation):

```python
@login_required
@require_http_methods(["GET", "POST"])
def ai_example_view(request, pk):
    """
    HTMX endpoint: AI-powered feature

    GET: Display results if cached
    POST: Trigger async processing
    """
    from .ai_services import ExampleService
    from .tasks import process_example_task

    item = get_object_or_404(Model, pk=pk)

    if request.method == "POST":
        # Trigger async task
        task = process_example_task.delay(pk)

        return HttpResponse(
            f"""
            <div id="status" hx-get="{reverse('app:status', args=[pk])}"
                 hx-trigger="every 2s" hx-swap="outerHTML">
                <div class="spinner">Processing...</div>
            </div>
            """,
            headers={"HX-Trigger": json.dumps({"task-started": {"id": pk}})}
        )

    # GET: Return cached results
    cache_key = f"ai_example_{pk}"
    result = cache.get(cache_key)

    if result:
        return render(request, "app/widgets/result.html", {
            "item": item,
            "result": result
        })

    return HttpResponse("<div>No results yet. Click 'Analyze' to start.</div>")
```

---

## HTMX Integration Patterns

### 1. Trigger + Poll Pattern (Async Operations)

```html
<!-- Step 1: Trigger button -->
<button
    hx-post="{% url 'app:ai-trigger' item.id %}"
    hx-target="#results"
    hx-swap="outerHTML">
    Start AI Analysis
</button>

<!-- Step 2: Status polling (returned by trigger) -->
<div id="results"
     hx-get="{% url 'app:ai-status' item.id %}"
     hx-trigger="every 2s"
     hx-swap="outerHTML">
    <div class="spinner">Analyzing...</div>
</div>

<!-- Step 3: Final results (returned by status when complete) -->
<div id="results">
    <h3>Analysis Complete</h3>
    <!-- Results display -->
</div>
```

### 2. Instant Display Pattern (Cached Results)

```html
<!-- Load immediately on page load -->
<div hx-get="{% url 'app:ai-display' item.id %}"
     hx-trigger="load"
     hx-swap="innerHTML">
    Loading...
</div>

<!-- Load on user reveal (scroll into view) -->
<div hx-get="{% url 'app:ai-widget' item.id %}"
     hx-trigger="revealed"
     hx-swap="innerHTML">
    <!-- Placeholder -->
</div>
```

### 3. Form Submission Pattern

```html
<form hx-post="{% url 'app:ai-analyze' %}"
      hx-target="#results"
      hx-swap="innerHTML">
    <textarea name="content">{{ item.content }}</textarea>
    <button type="submit">Analyze Content</button>
</form>

<div id="results">
    <!-- Results appear here -->
</div>
```

---

## Testing AI Endpoints

### Manual Testing Checklist

```bash
# 1. Start development server
cd src
python manage.py runserver

# 2. Test each endpoint (example)
curl -X GET http://localhost:8000/communities/ai/similar/1/ \
     -H "Cookie: sessionid=YOUR_SESSION_ID"

# 3. Check for proper responses
# - 200 OK for successful requests
# - 404 if view not implemented
# - 401 if not authenticated
# - 500 if server error

# 4. Test HTMX headers
curl -X POST http://localhost:8000/mana/workshop/1/analyze/ \
     -H "HX-Request: true" \
     -H "Cookie: sessionid=YOUR_SESSION_ID"
```

### Automated URL Testing

```python
# Run URL validation
cd src
python manage.py test --pattern="test_urls*.py"

# Check all URLs are accessible
python scripts/verify_urls.py
```

---

## Performance Considerations

### Caching Strategy

All AI operations cache results to avoid redundant API calls:

```python
# Cache key pattern
cache_key = f"{module}_{operation}_{object_id}"

# Cache duration
CACHE_TIMEOUT = 3600  # 1 hour for AI results

# Example
cache.set(f"mana_analysis_{workshop_id}", results, timeout=3600)
```

### Async Processing

Long-running AI operations use Celery:

```python
# Task definition
@shared_task(bind=True)
def analyze_workshop_responses(self, workshop_id):
    # Process in background
    results = ResponseAnalyzer().analyze(workshop_id)
    cache.set(f"mana_analysis_{workshop_id}", results, timeout=3600)
    return results

# Task invocation
task = analyze_workshop_responses.delay(workshop_id)
```

---

## Security Considerations

### Authentication

All AI endpoints require authentication:

```python
@login_required
def ai_view(request, pk):
    # Only authenticated users can access
    pass
```

### Permission Checks

Some endpoints require specific permissions:

```python
from django.contrib.auth.decorators import permission_required

@login_required
@permission_required('app.can_use_ai_features')
def ai_sensitive_view(request, pk):
    pass
```

### Rate Limiting

Implement rate limiting for AI endpoints to prevent abuse:

```python
from django.core.cache import cache

def rate_limit_check(user_id, endpoint):
    key = f"rate_limit_{endpoint}_{user_id}"
    count = cache.get(key, 0)

    if count >= 10:  # 10 requests per hour
        return False

    cache.set(key, count + 1, timeout=3600)
    return True
```

---

## Related Documentation

- **[AI Implementation Summary](AI_IMPLEMENTATION_COMPLETE_SUMMARY.md)** - Overall AI integration
- **[Communities AI Guide](../improvements/COMMUNITIES_AI_IMPLEMENTATION_COMPLETE.md)** - Communities module
- **[MANA AI Guide](../improvements/MANA_AI_INTELLIGENCE_IMPLEMENTATION.md)** - MANA module
- **[Coordination AI Guide](../improvements/COORDINATION_AI_IMPLEMENTATION.md)** - Coordination module
- **[Policy AI Guide](../improvements/POLICY_AI_IMPLEMENTATION_SUMMARY.md)** - Policy module
- **[Project Central AI Setup](../improvements/PROJECT_CENTRAL_AI_SETUP.md)** - Project management
- **[Unified Search Guide](../improvements/UNIFIED_SEARCH_IMPLEMENTATION.md)** - Search features

---

## Maintenance

### Adding New AI Endpoints

1. **Define URL pattern** in appropriate `urls.py`
2. **Implement view function** following MANA pattern
3. **Create AI service** in `ai_services/` directory
4. **Add Celery task** if async processing needed
5. **Create widget template** for HTMX response
6. **Update this document** with new endpoint

### Deprecating Endpoints

1. **Add deprecation warning** to view docstring
2. **Update documentation** with migration path
3. **Log deprecation warnings** in production
4. **Remove after 2 release cycles**

---

**Last Updated:** 2025-10-06
**Document Owner:** AI Integration Team
**Review Cycle:** After each module implementation
