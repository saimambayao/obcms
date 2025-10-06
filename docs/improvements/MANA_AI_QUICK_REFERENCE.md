# MANA AI Intelligence - Quick Reference Guide

## Usage Cheat Sheet

### Import AI Services

```python
from mana.ai_services.response_analyzer import ResponseAnalyzer
from mana.ai_services.theme_extractor import ThemeExtractor
from mana.ai_services.needs_extractor import NeedsExtractor
from mana.ai_services.report_generator import AssessmentReportGenerator
from mana.ai_services.cultural_validator import BangsomoroCulturalValidator
```

### Analyze Workshop Responses

```python
# Initialize analyzer
analyzer = ResponseAnalyzer()

# Analyze single question
question = "What are the health needs in your community?"
responses = ["Need clinic", "No doctor", "Medicine expensive"]

analysis = analyzer.analyze_question_responses(question, responses)
# Returns: {summary, key_points, sentiment, action_items, confidence}

# Aggregate full workshop
insights = analyzer.aggregate_workshop_insights(workshop_id=123)
# Returns: {status, workshop_title, total_responses, question_analyses, overall_summary}
```

### Extract Themes

```python
# Initialize extractor
extractor = ThemeExtractor()

# Extract themes
themes = extractor.extract_themes(
    responses=['Need healthcare', 'Education poor', ...],
    num_themes=5,
    context='Barangay Balangasan Workshop'
)
# Returns: [{theme, frequency, example_quotes, sub_themes, priority, category}]

# Track theme evolution
evolution = extractor.track_theme_evolution(
    community_id=456,
    lookback_months=12
)
# Returns: {status, timeline, evolution_analysis}
```

### Extract & Rank Needs

```python
# Initialize extractor
needs_extractor = NeedsExtractor()

# Extract needs
needs = needs_extractor.extract_needs(
    workshop_responses=['Need health clinic', ...],
    context='Barangay Balangasan'
)
# Returns: {health: {priority, needs, urgency, beneficiaries, category_score}}

# Rank needs
ranked = needs_extractor.rank_needs_by_priority(needs)
# Returns: [{category, priority, needs, composite_score, beneficiaries}, ...]

# Generate priority matrix
matrix = needs_extractor.generate_needs_prioritization_matrix(needs)
# Returns: {quick_wins, strategic_projects, fill_ins, hard_slogs}
```

### Generate Reports

```python
# Initialize generator
generator = AssessmentReportGenerator()

# Executive summary (500-700 words)
summary = generator.generate_executive_summary(
    workshop_id=123,
    max_words=700
)
# Returns: Professional summary text

# Full report
report = generator.generate_full_report(workshop_id=123)
# Returns: {metadata, sections, appendices}

# Comparison report
comparison = generator.generate_comparison_report(
    community_ids=[1, 2, 3],
    title='Regional Needs Comparison'
)
# Returns: {title, communities_analyzed, community_data, comparative_analysis}
```

### Validate Cultural Appropriateness

```python
# Initialize validator
validator = BangsomoroCulturalValidator()

# Validate report content
validation = validator.validate_report_content(report_text)
# Returns: {appropriate, score, issues, suggestions, strengths}

# Validate needs list
needs_validation = validator.validate_needs_list(
    needs=['Build clinic', 'Support tribal leaders']  # 'tribal' will be flagged
)
# Returns: {valid, flagged_needs, score, flagged_count}

# Get suggestions
suggestions = validator.suggest_culturally_appropriate_phrasing(
    original_text='The tribal community needs support',
    context='Community needs assessment'
)
# Returns: {suggestions: [{phrasing, rationale}]}

# Generate compliance report
compliance = validator.generate_cultural_compliance_report(validation)
# Returns: Formatted text report
```

### Background Tasks

```python
from mana.tasks import (
    analyze_workshop_responses,
    generate_assessment_report,
    validate_report_cultural_compliance
)

# Trigger async analysis
task = analyze_workshop_responses.delay(workshop_id=123)

# Trigger async report generation
task = generate_assessment_report.delay(
    workshop_id=123,
    report_type='executive'  # or 'full'
)

# Trigger async validation
task = validate_report_cultural_compliance.delay(
    report_text='...',
    report_id='report_123'
)
```

### Cache Management

```python
from django.core.cache import cache

# Get cached analysis
cache_key = f'mana_workshop_analysis_{workshop_id}'
analysis = cache.get(cache_key)

# Clear specific cache
cache.delete(cache_key)

# Clear all MANA AI cache
cache.delete_pattern('mana_*')
```

### HTMX Endpoints

```html
<!-- Trigger analysis -->
<button hx-post="{% url 'mana:trigger_workshop_analysis' workshop.id %}"
        hx-target="#analysis-container">
    Analyze Workshop
</button>

<!-- Check status (with polling) -->
<div hx-get="{% url 'mana:analysis_status' workshop.id %}"
     hx-trigger="every 2s"
     hx-swap="outerHTML">
    Loading...
</div>

<!-- Generate report -->
<button hx-post="{% url 'mana:generate_report' workshop.id %}"
        hx-target="#report-preview">
    Generate Report
</button>

<!-- Validate content -->
<form hx-post="{% url 'mana:validate_content' %}"
      hx-target="#validation-result">
    <textarea name="content">...</textarea>
    <button type="submit">Validate</button>
</form>
```

### Template Usage

```django
{% load static %}

<!-- Include AI analysis widget -->
{% include 'mana/widgets/ai_analysis.html' with ai_insights=insights %}

<!-- Include themes display -->
{% include 'mana/widgets/themes_display.html' with themes=themes %}

<!-- Include needs display -->
{% include 'mana/widgets/needs_display.html' with ranked_needs=ranked_needs %}
```

## Need Categories Reference

| Category | Keywords | Icon | Color |
|----------|----------|------|-------|
| Health | health, clinic, hospital, medicine, doctor | fa-heartbeat | #dc2626 |
| Education | school, education, teacher, madrasah | fa-graduation-cap | #2563eb |
| Infrastructure | road, bridge, building, facility | fa-road | #7c3aed |
| Livelihood | job, income, business, farming | fa-briefcase | #059669 |
| Water | water, well, sanitation, toilet | fa-tint | #0891b2 |
| Electricity | electricity, power, light, solar | fa-bolt | #f59e0b |
| Governance | governance, leader, council, services | fa-landmark | #6366f1 |
| Culture | culture, mosque, islamic, halal | fa-mosque | #10b981 |
| Peace & Security | peace, security, safety, protection | fa-shield-alt | #8b5cf6 |
| Social Services | social, welfare, assistance, aid | fa-hands-helping | #ec4899 |

## Priority Levels

- **CRITICAL** - Immediate action required, affects health/safety
- **HIGH** - Significant impact, should be addressed soon
- **MEDIUM** - Important but not urgent
- **LOW** - Nice to have, long-term improvement

## Cultural Validation Score Guide

- **0.90-1.00** - Excellent (fully appropriate)
- **0.75-0.89** - Good (minor improvements suggested)
- **0.60-0.74** - Acceptable (some issues to address)
- **0.00-0.59** - Needs revision (critical issues found)

## Prohibited Terms

❌ **Avoid:**
- tribal
- primitive
- backward
- uncivilized
- minority group
- savage

✅ **Use instead:**
- community-based / traditional
- developing / emerging
- underserved / marginalized
- traditional / indigenous
- Bangsamoro community / OBC community
- respectful descriptive terms

## API Response Times (Approximate)

| Operation | Time | Cache Duration |
|-----------|------|----------------|
| Response Analysis | 5-15s | 24 hours |
| Theme Extraction | 10-20s | 7 days |
| Needs Extraction | 8-15s | 3 days |
| Report Generation | 30-60s | 30 days |
| Cultural Validation | 5-10s | 30 days |

## Error Handling

```python
try:
    analysis = analyzer.aggregate_workshop_insights(workshop_id)

    if analysis.get('status') == 'error':
        # Handle error
        logger.error(f"Analysis failed: {analysis.get('message')}")

    elif analysis.get('status') == 'no_data':
        # No responses available
        messages.info(request, 'No workshop responses to analyze yet')

    else:
        # Success
        display_analysis(analysis)

except Exception as e:
    logger.exception('Unexpected error during analysis')
    messages.error(request, 'Analysis failed. Please try again.')
```

## Logging

```python
import logging
logger = logging.getLogger(__name__)

# AI services log at INFO level
logger.info('Starting analysis for workshop 123')

# Errors logged with full traceback
logger.exception('Error during theme extraction')
```

## Testing

```bash
# Run all AI service tests
pytest src/mana/tests/test_ai_services.py -v

# Run specific test class
pytest src/mana/tests/test_ai_services.py::TestResponseAnalyzer -v

# Run with coverage
pytest src/mana/tests/test_ai_services.py --cov=mana.ai_services
```

## Common Issues & Solutions

### Issue: Analysis not appearing

**Check:**
1. Cache: `cache.get(f'mana_workshop_analysis_{workshop_id}')`
2. Task status: Check Celery worker logs
3. Responses exist: `workshop.structured_responses.filter(status='submitted').count()`

**Solution:**
```python
# Force re-analysis
cache.delete(f'mana_workshop_analysis_{workshop_id}')
analyze_workshop_responses.delay(workshop_id)
```

### Issue: Low cultural validation score

**Check:**
1. Prohibited terms: `validator._quick_scan_for_issues(text)`
2. Review issues: `validation['issues']`
3. Apply suggestions: `validation['suggestions']`

**Solution:**
```python
# Get suggestions
suggestions = validator.suggest_culturally_appropriate_phrasing(
    original_text='problematic text',
    context='report section'
)

# Apply changes and re-validate
```

### Issue: Report generation timeout

**Possible causes:**
- Too many responses (>500)
- API rate limiting
- Network issues

**Solution:**
```python
# Increase timeout
@shared_task(soft_time_limit=300, time_limit=360)
def generate_assessment_report(...):
    ...

# Or reduce scope
report = generator.generate_executive_summary(workshop_id)  # Faster
```

## Best Practices

1. **Always validate** reports before publication
2. **Cache aggressively** - API calls are expensive
3. **Use background tasks** for anything >5 seconds
4. **Provide loading indicators** for async operations
5. **Log everything** for debugging
6. **Test with mock data** before production
7. **Monitor API usage** to avoid rate limits
8. **Review AI outputs** - don't trust blindly
9. **Gather user feedback** on quality
10. **Update cultural guidelines** based on community input

---

**Quick Help:** For issues, check logs in `src/logs/` or contact AI engineering team.
