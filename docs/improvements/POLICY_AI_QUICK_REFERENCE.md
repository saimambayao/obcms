# Policy AI Enhancement - Quick Reference Guide

**Quick Start Guide for Using Enhanced AI Features in Policy Recommendations**

---

## Installation & Setup

### 1. Ensure Dependencies Installed
```bash
cd src
pip install -r requirements/development.txt
```

### 2. Configure Environment Variables
```bash
# .env file
GOOGLE_API_KEY=your_google_api_key_here
REDIS_URL=redis://localhost:6379/0
```

### 3. Start Required Services
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery Worker
cd src
celery -A obc_management worker -l info

# Terminal 3: Django Dev Server
cd src
./manage.py runserver
```

---

## Quick Usage Examples

### Evidence Gathering

```python
from recommendations.policies.ai_services import get_evidence_gatherer

# Initialize
gatherer = get_evidence_gatherer()

# Gather evidence
evidence = gatherer.gather_evidence(
    policy_topic="Healthcare access for coastal communities",
    modules=['assessments', 'communities', 'projects'],
    limit_per_module=10,
    similarity_threshold=0.5
)

# Synthesize evidence
synthesis = gatherer.synthesize_evidence(evidence, "Healthcare access")

# Results
print(f"Total Citations: {evidence['total_citations']}")
print(f"Evidence Strength: {synthesis['strength_of_evidence']}")
print(f"Confidence: {synthesis['confidence_score']:.0%}")
```

---

### Policy Generation

```python
from recommendations.policies.ai_services import get_policy_generator

# Initialize
generator = get_policy_generator()

# Generate comprehensive policy
policy = generator.generate_policy_recommendation(
    issue="Healthcare access for coastal communities",
    evidence=evidence,  # From above
    category='social_development',
    scope='regional'
)

# Results
print(f"Title: {policy['title']}")
print(f"Cost: ₱{policy['estimated_cost']:,.2f}")
print(f"Citations: {len(policy['citations'])}")
```

---

### Impact Simulation

```python
from recommendations.policies.ai_services import get_impact_simulator

# Initialize
simulator = get_impact_simulator()

# Simulate impact
results = simulator.simulate_impact(
    policy_data=policy,  # From above or UUID
    scenarios=['best_case', 'realistic', 'worst_case'],
    use_cache=True
)

# Display results
for scenario, data in results['scenarios'].items():
    print(f"\n{scenario.upper()}:")
    print(f"  Beneficiaries: {data['beneficiaries_reached']:,}")
    print(f"  Cost/Person: ₱{data['cost_per_beneficiary']:,.2f}")
    print(f"  Timeline: {data['timeline_months']} months")
    print(f"  Success: {data['success_probability']:.0%}")
```

---

### Compliance Checking

```python
from recommendations.policies.ai_services import get_compliance_checker

# Initialize
checker = get_compliance_checker()

# Check compliance
result = checker.check_compliance(
    policy_text=policy_full_text,
    policy_title=policy['title'],
    category='social_development'
)

# Results
print(f"Compliant: {result['compliant']}")
print(f"Score: {result['compliance_score']:.0%}")
print(f"Risk: {result['risk_level']}")
print(f"Laws: {', '.join(result['relevant_laws'][:3])}")
```

---

## Async Task Processing

### Generate Policy (Background)

```python
from recommendations.policy_tracking.tasks import generate_policy_from_assessments

# Trigger task
task = generate_policy_from_assessments.delay(
    issue="Healthcare access",
    assessment_ids=[1, 2, 3],
    category='social_development',
    scope='regional'
)

# Check status
print(f"Task ID: {task.id}")
print(f"Status: {task.status}")

# Get result (blocks until complete)
result = task.get(timeout=120)
print(f"Generated: {result['policy_title']}")

# Retrieve from cache
from django.core.cache import cache
policy_data = cache.get(result['cache_key'])
```

### Simulate Impact (Background)

```python
from recommendations.policy_tracking.tasks import simulate_policy_impact

# Trigger task
task = simulate_policy_impact.delay(
    policy_id='uuid-here',
    scenarios=['realistic', 'best_case']
)

# Results cached automatically
# View in admin or dashboard
```

### Batch Simulation (Scheduled)

```python
from recommendations.policy_tracking.tasks import simulate_all_active_policies

# Run manually
task = simulate_all_active_policies.delay()

# Or schedule with celery-beat
# Runs nightly at 2 AM by default
```

---

## UI Integration

### Evidence Dashboard Widget

```django
{# In your template #}
{% load static %}

{# Get evidence and synthesis from view context #}
{% include "recommendations/policy_tracking/widgets/evidence_dashboard.html" with evidence=evidence evidence_synthesis=synthesis %}
```

### Impact Simulation Widget

```django
{# In your template #}
{% include "recommendations/policy_tracking/widgets/impact_simulation.html" with simulation=simulation_results %}
```

---

## Common Workflows

### Workflow 1: MANA Assessment → Policy

```python
# 1. User completes MANA assessment
# 2. System identifies policy need

# 3. Gather evidence
evidence = gatherer.gather_evidence(
    policy_topic="Education access in remote areas",
    modules=['assessments', 'communities']
)

# 4. Generate policy
policy = generator.generate_policy_recommendation(
    issue="Education access in remote areas",
    evidence=evidence
)

# 5. Simulate impact
simulation = simulator.simulate_impact(policy)

# 6. Check compliance
compliance = checker.check_compliance(
    policy_text=policy_text,
    category='education'
)

# 7. Present to user for review
```

### Workflow 2: Policy Refinement

```python
# 1. Get stakeholder feedback
feedback = "Please add more detail on budget allocation"

# 2. Refine policy
refined = generator.refine_policy(
    policy_data=current_policy,
    feedback=feedback,
    focus_areas=['budget', 'implementation']
)

# 3. Re-check compliance
compliance = checker.check_compliance(refined_text)

# 4. Update policy in database
```

### Workflow 3: Policy Comparison

```python
# Compare multiple policy options
results = simulator.compare_policies(
    policy_ids=['uuid-1', 'uuid-2', 'uuid-3'],
    scenario='realistic'
)

# View ranking
for rank in results['ranking']:
    print(f"{rank['policy_title']}: {rank['score']:.2f}")
```

---

## Troubleshooting

### Issue: AI Generation Fails

```python
# Check API key
from django.conf import settings
print(f"API Key configured: {bool(settings.GOOGLE_API_KEY)}")

# Test Gemini connection
from ai_assistant.services import GeminiService
gemini = GeminiService()
response = gemini.generate_text("Test prompt", use_cache=False)
print(f"Success: {response['success']}")
```

### Issue: No Evidence Found

```python
# Check vector indices
from ai_assistant.services import get_similarity_search_service
search = get_similarity_search_service()
stats = search.get_index_stats()
print(f"Indices: {stats}")

# If empty, rebuild indices
# (Refer to ai_assistant documentation)
```

### Issue: Celery Tasks Not Processing

```bash
# Check Celery status
celery -A obc_management inspect active

# Check Redis connection
redis-cli ping

# View Celery logs
celery -A obc_management worker -l debug
```

---

## API Cost Monitoring

```python
# Track API usage
from django.core.cache import cache

# Get monthly stats (if implemented)
monthly_cost = cache.get('ai_monthly_cost', 0.0)
print(f"Monthly API Cost: ${monthly_cost:.2f}")

# Per-request tracking
response = gemini.generate_text(prompt)
print(f"Tokens: {response['tokens_used']}")
print(f"Cost: ${response['cost']:.6f}")
```

---

## Performance Tips

### 1. Use Caching Effectively
```python
# Enable caching for evidence synthesis
synthesis = gatherer.synthesize_evidence(
    evidence, topic
)  # Cached for 1 hour

# Enable caching for impact simulation
simulation = simulator.simulate_impact(
    policy_id,
    use_cache=True  # Cached for 24 hours
)
```

### 2. Async for Slow Operations
```python
# Don't wait for policy generation
task = generate_policy_from_assessments.delay(...)

# Show loading indicator to user
# Poll task status via AJAX
# Display result when ready
```

### 3. Batch Processing
```python
# Generate multiple policies overnight
for assessment in assessments:
    generate_policy_from_assessments.delay(
        issue=assessment.primary_need,
        assessment_ids=[assessment.id]
    )
```

---

## Best Practices

### 1. Evidence Quality
- Gather from at least 3 modules for strong evidence
- Use similarity threshold 0.5+ for relevance
- Review AI synthesis for accuracy

### 2. Policy Generation
- Provide clear, specific issue descriptions
- Include relevant evidence context
- Review and refine AI-generated policies

### 3. Impact Simulation
- Run multiple scenarios for comparison
- Validate AI estimates with real data
- Update assumptions based on outcomes

### 4. Compliance Checking
- Run checks before policy submission
- Address all high-severity conflicts
- Keep legal framework updated

---

## Quick Commands

```bash
# Run tests
pytest src/recommendations/policies/tests/test_ai_services.py -v

# Generate test policy
python manage.py shell
>>> from recommendations.policies.ai_services import get_policy_generator
>>> generator = get_policy_generator()
>>> policy = generator.generate_quick_policy("Test issue", "standard")

# Clear cache
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()

# Rebuild vector indices
python manage.py rebuild_vector_indices  # If command exists

# View Celery tasks
celery -A obc_management inspect active
celery -A obc_management inspect scheduled
```

---

## Support & Resources

- **Full Documentation:** `docs/improvements/POLICY_AI_ENHANCEMENT.md`
- **Test Examples:** `src/recommendations/policies/tests/test_ai_services.py`
- **AI Services Code:** `src/recommendations/policies/ai_services/`
- **UI Templates:** `src/templates/recommendations/policy_tracking/widgets/`

**For Issues:**
- Check logs: `src/logs/`
- Review error traces in Celery output
- Verify API key and Redis connectivity
- Ensure vector indices are populated

---

## Version Information

- **Implementation Date:** October 6, 2025
- **AI Model:** Google Gemini 1.5 Pro
- **Python:** 3.12+
- **Django:** 5.x
- **Celery:** 5.x
- **Redis:** Required for caching and Celery

---

**End of Quick Reference**
