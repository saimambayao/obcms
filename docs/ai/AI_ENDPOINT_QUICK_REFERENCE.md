# AI Endpoint Quick Reference

**Quick lookup guide for all AI endpoints in OBCMS**

---

## Communities Module

**Base URL:** `/communities/`
**Namespace:** `communities`

| Endpoint | Method | View | Purpose |
|----------|--------|------|---------|
| `ai/similar/<pk>/` | GET | `ai_similar_communities` | Find similar communities |
| `ai/classify-needs/<pk>/` | POST | `ai_classify_needs` | Classify community needs |
| `ai/generate-report/<pk>/` | POST | `ai_generate_report` | Generate profile report |
| `ai/validate-data/<pk>/` | POST | `ai_validate_data` | Validate data quality |

**Template Usage:**
```django
{% url 'communities:ai-similar' community.id %}
{% url 'communities:ai-classify-needs' community.id %}
{% url 'communities:ai-generate-report' community.id %}
{% url 'communities:ai-validate-data' community.id %}
```

---

## MANA Module

**Base URL:** `/mana/workshops/`
**Namespace:** `mana`

| Endpoint | Method | View | Purpose |
|----------|--------|------|---------|
| `workshop/<id>/ai-analysis/` | GET | `workshop_ai_analysis` | Display analysis dashboard |
| `workshop/<id>/analyze/` | POST | `trigger_workshop_analysis` | Trigger analysis |
| `workshop/<id>/analysis/status/` | GET | `analysis_status` | Poll for status |
| `workshop/<id>/generate-report/` | POST | `generate_report` | Generate report |
| `workshop/<id>/report/status/` | GET | `report_status` | Poll report status |
| `workshop/<id>/themes/` | GET | `theme_analysis` | Display themes |
| `workshop/<id>/needs/` | GET | `needs_analysis` | Display needs |
| `workshop/<id>/export-analysis/` | GET | `export_analysis_json` | Export as JSON |
| `validate-content/` | POST | `validate_content` | Cultural validation |

**Template Usage:**
```django
{% url 'mana:workshop_ai_analysis' workshop.id %}
{% url 'mana:trigger_workshop_analysis' workshop.id %}
{% url 'mana:analysis_status' workshop.id %}
```

---

## Coordination Module

**Base URL:** `/coordination/`
**Namespace:** `coordination`

| Endpoint | Method | View | Purpose |
|----------|--------|------|---------|
| `ai/match-stakeholders/<pk>/` | GET | `ai_match_stakeholders` | Match partners |
| `ai/predict-partnerships/<pk>/` | POST | `ai_predict_partnerships` | Predict success |
| `ai/meeting-intelligence/<pk>/` | POST | `ai_meeting_intelligence` | Analyze meeting |
| `ai/optimize-resources/<pk>/` | POST | `ai_optimize_resources` | Optimize allocation |

**Template Usage:**
```django
{% url 'coordination:ai-match-stakeholders' organization.id %}
{% url 'coordination:ai-predict-partnerships' organization.id %}
{% url 'coordination:ai-meeting-intelligence' meeting.id %}
{% url 'coordination:ai-optimize-resources' organization.id %}
```

---

## Policy Module

**Base URL:** `/policies/`
**Namespace:** `policies`

| Endpoint | Method | View | Purpose |
|----------|--------|------|---------|
| `ai/gather-evidence/<pk>/` | POST | `ai_gather_evidence` | Gather evidence |
| `ai/generate-policy/<pk>/` | POST | `ai_generate_policy` | Generate draft |
| `ai/simulate-impact/<pk>/` | POST | `ai_simulate_impact` | Simulate impact |
| `ai/check-compliance/<pk>/` | POST | `ai_check_compliance` | Check compliance |

**Template Usage:**
```django
{% url 'policies:ai-gather-evidence' policy.id %}
{% url 'policies:ai-generate-policy' policy.id %}
{% url 'policies:ai-simulate-impact' policy.id %}
{% url 'policies:ai-check-compliance' policy.id %}
```

---

## Project Central Module

**Base URL:** `/project-management/`
**Namespace:** `project_central`

| Endpoint | Method | View | Purpose |
|----------|--------|------|---------|
| `ai/detect-anomalies/<uuid>/` | GET | `ai_detect_anomalies` | Detect anomalies |
| `ai/forecast-performance/<uuid>/` | GET | `ai_forecast_performance` | Forecast EVM |
| `ai/analyze-risks/<uuid>/` | POST | `ai_analyze_risks` | Analyze risks |
| `ai/generate-report/<uuid>/` | POST | `ai_generate_report` | Generate report |

**Template Usage:**
```django
{% url 'project_central:ai-detect-anomalies' project.id %}
{% url 'project_central:ai-forecast-performance' project.id %}
{% url 'project_central:ai-analyze-risks' project.id %}
{% url 'project_central:ai-generate-report' project.id %}
```

---

## Common Module (Chat)

**Base URL:** `/` (root)
**Namespace:** `common`

| Endpoint | Method | View | Purpose |
|----------|--------|------|---------|
| `chat/message/` | POST | `chat_message` | Send message |
| `chat/history/` | GET | `chat_history` | Get history |
| `chat/clear/` | POST | `clear_chat_history` | Clear history |
| `chat/stats/` | GET | `chat_stats` | Usage stats |
| `chat/capabilities/` | GET | `chat_capabilities` | Get capabilities |
| `chat/suggestion/` | GET | `chat_suggestion` | Get suggestions |

**Template Usage:**
```django
{% url 'common:chat_message' %}
{% url 'common:chat_history' %}
{% url 'common:chat_clear' %}
```

---

## Common Module (Search)

**Base URL:** `/` (root)
**Namespace:** `common`

| Endpoint | Method | View | Purpose |
|----------|--------|------|---------|
| `search/` | GET | `unified_search_view` | Unified search |
| `search/autocomplete/` | GET | `search_autocomplete` | Autocomplete |
| `search/stats/` | GET | `search_stats` | Search stats |
| `search/reindex/<module>/` | POST | `reindex_module` | Reindex module |

**Template Usage:**
```django
{% url 'common:unified_search' %}
{% url 'common:search_autocomplete' %}
{% url 'common:search_stats' %}
{% url 'common:reindex_module' module='communities' %}
```

---

## HTMX Patterns

### Trigger + Poll (Async)

```html
<button hx-post="{% url 'app:ai-trigger' item.id %}"
        hx-target="#results">
    Analyze
</button>

<div id="results">
    <!-- Polling div returned by trigger -->
    <div hx-get="{% url 'app:ai-status' item.id %}"
         hx-trigger="every 2s"
         hx-swap="outerHTML">
        Loading...
    </div>
</div>
```

### Instant Display

```html
<div hx-get="{% url 'app:ai-widget' item.id %}"
     hx-trigger="load"
     hx-swap="innerHTML">
    Loading...
</div>
```

### On User Action

```html
<button hx-get="{% url 'app:ai-feature' item.id %}"
        hx-target="#panel"
        class="btn-ai">
    <i class="fas fa-brain"></i> AI Feature
</button>
```

---

## Status Legend

- ✅ **Implemented** - View exists, tested, working
- ⚠️ **View Needed** - URL configured, service exists, view pending
- 🔧 **In Progress** - Currently being implemented
- 📋 **Planned** - Future implementation

---

**Quick Tip:** Use browser DevTools Network tab with filter "hx" to debug HTMX requests to AI endpoints.
