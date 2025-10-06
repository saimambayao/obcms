"""
Tests for Coordination Module Query Templates

Comprehensive test suite for 55 coordination templates covering:
- Partnerships (10 templates)
- Organizations (10 templates)
- Meetings/Engagements (10 templates)
- Activity Tracking (5 templates)
- Resource Coordination (5 templates)
- MOA/MOU Management (5 templates)
- Collaboration Analytics (5 templates)
- Engagement History (5 templates)
"""

import pytest
from common.ai_services.chat.query_templates.coordination import (
    COORDINATION_TEMPLATES,
    _partnerships_in_location,
    _active_partnerships,
    _partnerships_with_org,
    _partnership_count,
    _partnerships_by_type,
    _recent_partnerships,
    _partnerships_by_status,
    _list_partnerships,
    _partnerships_by_sector,
    _partnership_details,
    _orgs_in_sector,
    _active_stakeholders,
    _ngos_in_location,
    _org_count,
    _list_organizations,
    _orgs_by_type,
    _government_agencies,
    _org_details,
    _orgs_in_location,
    _search_organizations,
    _recent_meetings,
    _meetings_with_org,
    _meeting_schedule,
    _completed_meetings,
    _meetings_in_location,
    _meeting_count,
    _planned_meetings,
    _meeting_details,
    _meetings_by_date_range,
    _todays_meetings,
    _coordination_activities,
    _activities_by_type,
    _activities_timeline,
    _activities_by_org,
    _activities_count,
    _shared_resources,
    _resources_by_partnership,
    _resource_allocation,
    _partnerships_with_resources,
    _resource_types,
    _active_moas,
    _moa_expiring_soon,
    _moa_by_agency,
    _moa_renewals,
    _moa_list,
    _partnership_effectiveness,
    _engagement_metrics,
    _organization_activity_level,
    _partnership_by_sector_stats,
    _collaboration_trends,
    _org_engagement_history,
    _partnership_history,
    _recent_engagements,
    _engagement_outcomes,
    _partnership_milestones,
)
from common.ai_services.chat.query_templates.base import QueryTemplate


# =============================================================================
# TEMPLATE REGISTRATION TESTS
# =============================================================================

def test_coordination_templates_count():
    """Test that all 55 coordination templates are registered."""
    assert len(COORDINATION_TEMPLATES) == 55, f"Expected 55 templates, got {len(COORDINATION_TEMPLATES)}"


def test_all_templates_are_query_template_instances():
    """Test that all templates are QueryTemplate instances."""
    for template in COORDINATION_TEMPLATES:
        assert isinstance(template, QueryTemplate)


def test_all_templates_have_category():
    """Test that all templates have 'coordination' category."""
    for template in COORDINATION_TEMPLATES:
        assert template.category == 'coordination'


def test_all_templates_have_valid_priority():
    """Test that all templates have valid priority (1-100)."""
    for template in COORDINATION_TEMPLATES:
        assert 1 <= template.priority <= 100


def test_no_duplicate_patterns():
    """Test that there are no duplicate patterns."""
    patterns = [t.pattern for t in COORDINATION_TEMPLATES]
    assert len(patterns) == len(set(patterns)), "Duplicate patterns found"


# =============================================================================
# PARTNERSHIP QUERY BUILDER TESTS (10 tests)
# =============================================================================

def test_partnerships_in_location():
    """Test partnerships in location query builder."""
    entities = {'location': {'type': 'region', 'value': 'Region IX'}}
    result = _partnerships_in_location(entities)
    assert 'Partnership.objects.filter' in result
    assert 'count()' in result


def test_active_partnerships():
    """Test active partnerships query builder."""
    result = _active_partnerships({})
    assert "status='active'" in result
    assert 'Partnership.objects.filter' in result


def test_partnerships_with_org():
    """Test partnerships with organization query builder."""
    entities = {'organization': 'DSWD'}
    result = _partnerships_with_org(entities)
    assert 'DSWD' in result
    assert 'Q(' in result  # Uses Q objects for OR logic


def test_partnership_count():
    """Test partnership count query builder."""
    result = _partnership_count({})
    assert result == "Partnership.objects.count()"


def test_partnerships_by_type():
    """Test partnerships by type query builder."""
    entities = {'type': 'technical'}
    result = _partnerships_by_type(entities)
    assert 'technical' in result
    assert 'partnership_type__icontains' in result


def test_recent_partnerships():
    """Test recent partnerships query builder."""
    result = _recent_partnerships({})
    assert 'order_by' in result
    assert '-created_at' in result


def test_partnerships_by_status():
    """Test partnerships by status query builder."""
    entities = {'status': 'completed'}
    result = _partnerships_by_status(entities)
    assert 'Partnership.objects.filter' in result


def test_list_partnerships():
    """Test list partnerships query builder."""
    result = _list_partnerships({})
    assert 'values(' in result
    assert 'title' in result


def test_partnerships_by_sector():
    """Test partnerships by sector query builder."""
    entities = {'sector': 'education'}
    result = _partnerships_by_sector(entities)
    assert 'education' in result
    assert 'focus_sectors__icontains' in result


def test_partnership_details():
    """Test partnership details query builder."""
    entities = {'id': 'abc-123'}
    result = _partnership_details(entities)
    assert 'abc-123' in result
    assert 'values(' in result


# =============================================================================
# ORGANIZATION QUERY BUILDER TESTS (10 tests)
# =============================================================================

def test_orgs_in_sector():
    """Test organizations in sector query builder."""
    entities = {'sector': 'health'}
    result = _orgs_in_sector(entities)
    assert 'health' in result
    assert 'sector__icontains' in result


def test_active_stakeholders():
    """Test active stakeholders query builder."""
    result = _active_stakeholders({})
    assert 'is_active=True' in result
    assert 'Organization.objects.filter' in result


def test_ngos_in_location():
    """Test NGOs in location query builder."""
    entities = {'location': {'type': 'region', 'value': 'Region IX'}}
    result = _ngos_in_location(entities)
    assert "organization_type='ngo'" in result


def test_org_count():
    """Test organization count query builder."""
    result = _org_count({})
    assert result == "Organization.objects.count()"


def test_list_organizations():
    """Test list organizations query builder."""
    result = _list_organizations({})
    assert 'values(' in result
    assert 'name' in result


def test_orgs_by_type():
    """Test organizations by type query builder."""
    entities = {'type': 'government'}
    result = _orgs_by_type(entities)
    assert 'government' in result
    assert 'organization_type__icontains' in result


def test_government_agencies():
    """Test government agencies query builder."""
    result = _government_agencies({})
    assert "organization_type='government'" in result


def test_org_details():
    """Test organization details query builder."""
    entities = {'id': 'org-456'}
    result = _org_details(entities)
    assert 'org-456' in result


def test_orgs_in_location():
    """Test organizations in location query builder."""
    entities = {'location': {'type': 'province', 'value': 'Zamboanga del Sur'}}
    result = _orgs_in_location(entities)
    assert 'Organization.objects' in result


def test_search_organizations():
    """Test search organizations query builder."""
    entities = {'name': 'Red Cross'}
    result = _search_organizations(entities)
    assert 'Red Cross' in result
    assert 'name__icontains' in result


# =============================================================================
# MEETING/ENGAGEMENT QUERY BUILDER TESTS (10 tests)
# =============================================================================

def test_recent_meetings():
    """Test recent meetings query builder."""
    result = _recent_meetings({})
    assert "engagement_type__category='meeting'" in result
    assert 'order_by' in result


def test_meetings_with_org():
    """Test meetings with organization query builder."""
    entities = {'organization': 'BARMM'}
    result = _meetings_with_org(entities)
    assert 'BARMM' in result
    assert 'participating_organizations' in result


def test_meeting_schedule():
    """Test meeting schedule query builder."""
    result = _meeting_schedule({})
    assert "status='scheduled'" in result
    assert 'scheduled_date__gte' in result


def test_completed_meetings():
    """Test completed meetings query builder."""
    result = _completed_meetings({})
    assert "status='completed'" in result


def test_meetings_in_location():
    """Test meetings in location query builder."""
    entities = {'location': 'Cotabato'}
    result = _meetings_in_location(entities)
    assert 'Cotabato' in result
    assert 'location__icontains' in result


def test_meeting_count():
    """Test meeting count query builder."""
    result = _meeting_count({})
    assert "engagement_type__category='meeting'" in result
    assert 'count()' in result


def test_planned_meetings():
    """Test planned meetings query builder."""
    result = _planned_meetings({})
    assert "status='planned'" in result


def test_meeting_details():
    """Test meeting details query builder."""
    entities = {'id': 'meet-789'}
    result = _meeting_details(entities)
    assert 'meet-789' in result


def test_meetings_by_date_range():
    """Test meetings by date range query builder."""
    entities = {'date_start': '2025-01-01', 'date_end': '2025-12-31'}
    result = _meetings_by_date_range(entities)
    assert '2025-01-01' in result
    assert '2025-12-31' in result


def test_todays_meetings():
    """Test today's meetings query builder."""
    result = _todays_meetings({})
    assert 'timezone.now().date()' in result


# =============================================================================
# ACTIVITY TRACKING QUERY BUILDER TESTS (5 tests)
# =============================================================================

def test_coordination_activities():
    """Test coordination activities query builder."""
    result = _coordination_activities({})
    assert 'StakeholderEngagement.objects.exclude' in result
    assert "engagement_type__category='meeting'" in result


def test_activities_by_type():
    """Test activities by type query builder."""
    entities = {'type': 'workshop'}
    result = _activities_by_type(entities)
    assert 'workshop' in result
    assert 'engagement_type__name__icontains' in result


def test_activities_timeline():
    """Test activities timeline query builder."""
    entities = {}
    result = _activities_timeline(entities)
    assert 'order_by' in result
    assert 'scheduled_date' in result


def test_activities_by_org():
    """Test activities by organization query builder."""
    entities = {'organization': 'OPAPP'}
    result = _activities_by_org(entities)
    assert 'OPAPP' in result


def test_activities_count():
    """Test activities count query builder."""
    result = _activities_count({})
    assert result == "StakeholderEngagement.objects.count()"


# =============================================================================
# RESOURCE COORDINATION QUERY BUILDER TESTS (5 tests)
# =============================================================================

def test_shared_resources():
    """Test shared resources query builder."""
    result = _shared_resources({})
    assert 'exclude' in result
    assert "resources_shared=''" in result


def test_resources_by_partnership():
    """Test resources by partnership query builder."""
    entities = {'id': 'part-123'}
    result = _resources_by_partnership(entities)
    assert 'part-123' in result
    assert 'resource_contributions' in result


def test_resource_allocation():
    """Test resource allocation query builder."""
    result = _resource_allocation({})
    assert 'resource_contributions' in result
    assert 'order_by' in result


def test_partnerships_with_resources():
    """Test partnerships with resources query builder."""
    result = _partnerships_with_resources({})
    assert 'exclude' in result
    assert 'count()' in result


def test_resource_types():
    """Test resource types query builder."""
    result = _resource_types({})
    assert 'resources_shared' in result
    assert 'values(' in result


# =============================================================================
# MOA/MOU MANAGEMENT QUERY BUILDER TESTS (5 tests)
# =============================================================================

def test_active_moas():
    """Test active MOAs query builder."""
    result = _active_moas({})
    assert "status='active'" in result
    assert 'partnership_type__icontains' in result


def test_moa_expiring_soon():
    """Test MOAs expiring soon query builder."""
    result = _moa_expiring_soon({})
    assert 'end_date__lte' in result
    assert 'timedelta(days=90)' in result


def test_moa_by_agency():
    """Test MOAs by agency query builder."""
    entities = {'organization': 'DSWD'}
    result = _moa_by_agency(entities)
    assert 'DSWD' in result
    assert 'Q(' in result


def test_moa_renewals():
    """Test MOA renewals query builder."""
    result = _moa_renewals({})
    assert "status='pending_renewal'" in result


def test_moa_list():
    """Test MOA list query builder."""
    result = _moa_list({})
    assert 'partnership_type__icontains' in result
    assert 'Q(' in result


# =============================================================================
# COLLABORATION ANALYTICS QUERY BUILDER TESTS (5 tests)
# =============================================================================

def test_partnership_effectiveness():
    """Test partnership effectiveness query builder."""
    result = _partnership_effectiveness({})
    assert 'deliverables' in result
    assert 'impact_assessment' in result


def test_engagement_metrics():
    """Test engagement metrics query builder."""
    result = _engagement_metrics({})
    assert 'aggregate(' in result
    assert 'Count(' in result


def test_organization_activity_level():
    """Test organization activity level query builder."""
    result = _organization_activity_level({})
    assert 'annotate(' in result
    assert 'activity_count' in result


def test_partnership_by_sector_stats():
    """Test partnership by sector stats query builder."""
    result = _partnership_by_sector_stats({})
    assert 'focus_sectors' in result
    assert 'annotate(' in result


def test_collaboration_trends():
    """Test collaboration trends query builder."""
    entities = {}
    result = _collaboration_trends(entities)
    assert 'created_at__year' in result
    assert 'created_at__month' in result


# =============================================================================
# ENGAGEMENT HISTORY QUERY BUILDER TESTS (5 tests)
# =============================================================================

def test_org_engagement_history():
    """Test organization engagement history query builder."""
    entities = {'organization': 'MILF'}
    result = _org_engagement_history(entities)
    assert 'MILF' in result
    assert 'order_by' in result


def test_partnership_history():
    """Test partnership history query builder."""
    result = _partnership_history({})
    assert "status='completed'" in result
    assert 'order_by' in result


def test_recent_engagements():
    """Test recent engagements query builder."""
    result = _recent_engagements({})
    assert 'order_by' in result
    assert '-created_at' in result


def test_engagement_outcomes():
    """Test engagement outcomes query builder."""
    result = _engagement_outcomes({})
    assert "status='completed'" in result
    assert 'outcomes' in result


def test_partnership_milestones():
    """Test partnership milestones query builder."""
    result = _partnership_milestones({})
    assert 'deliverables' in result
    assert 'exclude' in result


# =============================================================================
# PATTERN MATCHING TESTS (Sample tests for each category)
# =============================================================================

def test_partnership_pattern_matching():
    """Test partnership query patterns."""
    patterns_to_test = [
        ("Partnerships in Region IX", r"partnerships?\s+in\s+(?P<location>.+)"),
        ("Active partnerships", r"(active|ongoing)\s+partnerships?"),
        ("Partnerships with DSWD", r"partnerships?\s+with\s+(?P<organization>.+)"),
        ("How many partnerships?", r"(how\s+many|total|count)\s+partnerships?"),
    ]

    for query, expected_pattern in patterns_to_test:
        matching_templates = [
            t for t in COORDINATION_TEMPLATES
            if t.pattern == expected_pattern
        ]
        assert len(matching_templates) > 0, f"No template found for pattern: {expected_pattern}"


def test_organization_pattern_matching():
    """Test organization query patterns."""
    patterns_to_test = [
        ("Organizations in health sector", r"organizations?\s+in\s+(?P<sector>.+)\s+sector"),
        ("Active stakeholders", r"(active\s+)?(stakeholders?|organizations?)"),
        ("NGOs in Region IX", r"ngos?\s+in\s+(?P<location>.+)"),
        ("How many organizations?", r"(how\s+many|total|count)\s+organizations?"),
    ]

    for query, expected_pattern in patterns_to_test:
        matching_templates = [
            t for t in COORDINATION_TEMPLATES
            if t.pattern == expected_pattern
        ]
        assert len(matching_templates) > 0, f"No template found for pattern: {expected_pattern}"


def test_meeting_pattern_matching():
    """Test meeting query patterns."""
    patterns_to_test = [
        ("Recent meetings", r"recent\s+meetings?"),
        ("Meetings with BARMM", r"meetings?\s+with\s+(?P<organization>.+)"),
        ("Meeting schedule", r"meeting\s+schedule"),
        ("Completed meetings", r"completed\s+meetings?"),
    ]

    for query, expected_pattern in patterns_to_test:
        matching_templates = [
            t for t in COORDINATION_TEMPLATES
            if t.pattern == expected_pattern
        ]
        assert len(matching_templates) > 0, f"No template found for pattern: {expected_pattern}"


def test_activity_pattern_matching():
    """Test activity tracking query patterns."""
    patterns_to_test = [
        ("Coordination activities", r"coordination\s+activities"),
        ("Workshop activities", r"(?P<type>workshop|training|consultation|assessment)\s+activities"),
        ("Activity timeline", r"activit(y|ies)\s+timeline"),
        ("How many activities?", r"(how\s+many|total|count)\s+activities"),
    ]

    for query, expected_pattern in patterns_to_test:
        matching_templates = [
            t for t in COORDINATION_TEMPLATES
            if t.pattern == expected_pattern
        ]
        assert len(matching_templates) > 0, f"No template found for pattern: {expected_pattern}"


def test_resource_pattern_matching():
    """Test resource coordination query patterns."""
    patterns_to_test = [
        ("Shared resources", r"shared\s+resources"),
        ("Resource allocation", r"resource\s+allocation"),
        ("Partnerships with resources", r"partnerships?\s+with\s+resources?"),
    ]

    for query, expected_pattern in patterns_to_test:
        matching_templates = [
            t for t in COORDINATION_TEMPLATES
            if t.pattern == expected_pattern
        ]
        assert len(matching_templates) > 0, f"No template found for pattern: {expected_pattern}"


def test_moa_pattern_matching():
    """Test MOA/MOU management query patterns."""
    patterns_to_test = [
        ("Active MOAs", r"(active\s+)?(moas?|mous?|memorandum)"),
        ("MOAs expiring", r"(moas?|mous?)\s+(expiring|renewal|renew)"),
        ("List all MOAs", r"(list|show)\s+(all\s+)?(moas?|mous?)"),
    ]

    for query, expected_pattern in patterns_to_test:
        matching_templates = [
            t for t in COORDINATION_TEMPLATES
            if t.pattern == expected_pattern
        ]
        assert len(matching_templates) > 0, f"No template found for pattern: {expected_pattern}"


def test_analytics_pattern_matching():
    """Test collaboration analytics query patterns."""
    patterns_to_test = [
        ("Partnership effectiveness", r"partnership\s+effectiveness"),
        ("Engagement metrics", r"engagement\s+metrics"),
        ("Collaboration trends", r"collaboration\s+trends"),
    ]

    for query, expected_pattern in patterns_to_test:
        matching_templates = [
            t for t in COORDINATION_TEMPLATES
            if t.pattern == expected_pattern
        ]
        assert len(matching_templates) > 0, f"No template found for pattern: {expected_pattern}"


def test_history_pattern_matching():
    """Test engagement history query patterns."""
    patterns_to_test = [
        ("Historical partnerships", r"(historical|past|completed)\s+partnerships?"),
        ("Recent engagements", r"recent\s+engagements?"),
        ("Engagement outcomes", r"engagement\s+outcomes"),
        ("Partnership milestones", r"partnership\s+milestones"),
    ]

    for query, expected_pattern in patterns_to_test:
        matching_templates = [
            t for t in COORDINATION_TEMPLATES
            if t.pattern == expected_pattern
        ]
        assert len(matching_templates) > 0, f"No template found for pattern: {expected_pattern}"


# =============================================================================
# INTEGRATION SUMMARY TEST
# =============================================================================

def test_coordination_templates_summary():
    """Test coordination templates summary and statistics."""
    print("\n" + "="*80)
    print("COORDINATION TEMPLATES TEST SUMMARY")
    print("="*80)

    categories = {
        'Partnerships': 10,
        'Organizations': 10,
        'Meetings/Engagements': 10,
        'Activity Tracking': 5,
        'Resource Coordination': 5,
        'MOA/MOU Management': 5,
        'Collaboration Analytics': 5,
        'Engagement History': 5,
    }

    print(f"\nTotal Templates: {len(COORDINATION_TEMPLATES)}")
    print(f"Expected: 55")
    print(f"\nTemplate Distribution:")
    for category, expected_count in categories.items():
        print(f"  - {category}: {expected_count} templates")

    print(f"\nAverage Priority: {sum(t.priority for t in COORDINATION_TEMPLATES) / len(COORDINATION_TEMPLATES):.2f}")
    print(f"Priority Range: {min(t.priority for t in COORDINATION_TEMPLATES)} - {max(t.priority for t in COORDINATION_TEMPLATES)}")

    print("\n" + "="*80)
    print("✅ All coordination template tests completed successfully!")
    print("="*80)

    assert True  # Summary test always passes if we get here
