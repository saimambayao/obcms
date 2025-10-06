"""
Coordination Module Query Templates for OBCMS Chat System

55+ comprehensive templates for partnerships, organizations, meetings,
stakeholder engagement, activities, resources, and collaboration analytics.

Enhanced from 30 → 55+ templates following communities.py architecture pattern.
"""

from typing import Any, Dict
from .base import QueryTemplate, build_location_filter, build_status_filter, build_date_range_filter


# =============================================================================
# PARTNERSHIP QUERIES (10 templates)
# =============================================================================

def _partnerships_in_location(entities: Dict[str, Any]) -> str:
    """Partnerships filtered by location."""
    location_filter = build_location_filter(entities, "")
    if location_filter:
        return f"Partnership.objects.filter({location_filter}).count()"
    return "Partnership.objects.count()"


def _active_partnerships(entities: Dict[str, Any]) -> str:
    """Active partnerships."""
    return "Partnership.objects.filter(status='active').count()"


def _partnerships_with_org(entities: Dict[str, Any]) -> str:
    """Partnerships with specific organization."""
    org = entities.get('organization', '')
    return f"Partnership.objects.filter(Q(lead_organization__name__icontains='{org}') | Q(partner_organizations__name__icontains='{org}')).distinct().count()"


def _partnership_count(entities: Dict[str, Any]) -> str:
    """Total partnership count."""
    return "Partnership.objects.count()"


def _partnerships_by_type(entities: Dict[str, Any]) -> str:
    """Partnerships by type."""
    ptype = entities.get('type', '')
    return f"Partnership.objects.filter(partnership_type__icontains='{ptype}').count()"


def _recent_partnerships(entities: Dict[str, Any]) -> str:
    """Recently created partnerships."""
    return "Partnership.objects.order_by('-created_at')[:10].values('id', 'title', 'status', 'created_at')"


def _partnerships_by_status(entities: Dict[str, Any]) -> str:
    """Partnerships filtered by status."""
    status_filter = build_status_filter(entities)
    if status_filter:
        return f"Partnership.objects.filter({status_filter}).count()"
    return "Partnership.objects.count()"


def _list_partnerships(entities: Dict[str, Any]) -> str:
    """List all partnerships."""
    return "Partnership.objects.values('id', 'title', 'partnership_type', 'status')[:20]"


def _partnerships_by_sector(entities: Dict[str, Any]) -> str:
    """Partnerships in specific sector."""
    sector = entities.get('sector', '')
    return f"Partnership.objects.filter(focus_sectors__icontains='{sector}').count()"


def _partnership_details(entities: Dict[str, Any]) -> str:
    """Details of specific partnership."""
    pid = entities.get('id', '')
    return f"Partnership.objects.filter(id='{pid}').values('title', 'partnership_type', 'status', 'description')[:1]"


# ========== ORGANIZATION QUERIES (10 templates) ==========

def _orgs_in_sector(entities: Dict[str, Any]) -> str:
    """Organizations in specific sector."""
    sector = entities.get('sector', '')
    return f"Organization.objects.filter(sector__icontains='{sector}').count()"


def _active_stakeholders(entities: Dict[str, Any]) -> str:
    """Active stakeholder organizations."""
    return "Organization.objects.filter(is_active=True).count()"


def _ngos_in_location(entities: Dict[str, Any]) -> str:
    """NGOs in specific location."""
    location_filter = build_location_filter(entities, "")
    return f"Organization.objects.filter(organization_type='ngo', {location_filter}).count()"


def _org_count(entities: Dict[str, Any]) -> str:
    """Total organization count."""
    return "Organization.objects.count()"


def _list_organizations(entities: Dict[str, Any]) -> str:
    """List all organizations."""
    return "Organization.objects.values('id', 'name', 'organization_type', 'sector')[:20]"


def _orgs_by_type(entities: Dict[str, Any]) -> str:
    """Organizations by type."""
    otype = entities.get('type', '')
    return f"Organization.objects.filter(organization_type__icontains='{otype}').count()"


def _government_agencies(entities: Dict[str, Any]) -> str:
    """Government agency organizations."""
    return "Organization.objects.filter(organization_type='government').count()"


def _org_details(entities: Dict[str, Any]) -> str:
    """Details of specific organization."""
    oid = entities.get('id', '')
    return f"Organization.objects.filter(id='{oid}').values('name', 'organization_type', 'sector', 'contact_person')[:1]"


def _orgs_in_location(entities: Dict[str, Any]) -> str:
    """Organizations in location."""
    location_filter = build_location_filter(entities, "")
    if location_filter:
        return f"Organization.objects.filter({location_filter}).count()"
    return "Organization.objects.count()"


def _search_organizations(entities: Dict[str, Any]) -> str:
    """Search organizations by name."""
    name = entities.get('name', '')
    return f"Organization.objects.filter(name__icontains='{name}').values('id', 'name', 'organization_type')[:10]"


# ========== MEETING/ENGAGEMENT QUERIES (10 templates) ==========

def _recent_meetings(entities: Dict[str, Any]) -> str:
    """Recently scheduled meetings."""
    return "StakeholderEngagement.objects.filter(engagement_type__category='meeting').order_by('-scheduled_date')[:10].values('id', 'title', 'scheduled_date', 'status')"


def _meetings_with_org(entities: Dict[str, Any]) -> str:
    """Meetings with specific organization."""
    org = entities.get('organization', '')
    return f"StakeholderEngagement.objects.filter(participating_organizations__name__icontains='{org}').count()"


def _meeting_schedule(entities: Dict[str, Any]) -> str:
    """Upcoming meeting schedule."""
    return "StakeholderEngagement.objects.filter(engagement_type__category='meeting', status='scheduled', scheduled_date__gte=timezone.now()).order_by('scheduled_date')[:10].values('title', 'scheduled_date', 'location')"


def _completed_meetings(entities: Dict[str, Any]) -> str:
    """Completed meetings."""
    return "StakeholderEngagement.objects.filter(engagement_type__category='meeting', status='completed').count()"


def _meetings_in_location(entities: Dict[str, Any]) -> str:
    """Meetings in specific location."""
    location = entities.get('location', '')
    return f"StakeholderEngagement.objects.filter(engagement_type__category='meeting', location__icontains='{location}').count()"


def _meeting_count(entities: Dict[str, Any]) -> str:
    """Total meeting count."""
    return "StakeholderEngagement.objects.filter(engagement_type__category='meeting').count()"


def _planned_meetings(entities: Dict[str, Any]) -> str:
    """Planned meetings."""
    return "StakeholderEngagement.objects.filter(engagement_type__category='meeting', status='planned').count()"


def _meeting_details(entities: Dict[str, Any]) -> str:
    """Details of specific meeting."""
    mid = entities.get('id', '')
    return f"StakeholderEngagement.objects.filter(id='{mid}').values('title', 'scheduled_date', 'location', 'agenda', 'status')[:1]"


def _meetings_by_date_range(entities: Dict[str, Any]) -> str:
    """Meetings in date range."""
    date_filter = build_date_range_filter(entities, "scheduled_date")
    if date_filter:
        return f"StakeholderEngagement.objects.filter(engagement_type__category='meeting', {date_filter}).count()"
    return "StakeholderEngagement.objects.filter(engagement_type__category='meeting').count()"


def _todays_meetings(entities: Dict[str, Any]) -> str:
    """Meetings scheduled for today."""
    return "StakeholderEngagement.objects.filter(engagement_type__category='meeting', scheduled_date=timezone.now().date()).values('title', 'scheduled_time', 'location')[:10]"


# =============================================================================
# ACTIVITY TRACKING QUERIES (5 templates)
# =============================================================================

def _coordination_activities(entities: Dict[str, Any]) -> str:
    """List coordination activities."""
    return "StakeholderEngagement.objects.exclude(engagement_type__category='meeting').values('id', 'title', 'engagement_type__name', 'status', 'scheduled_date')[:20]"


def _activities_by_type(entities: Dict[str, Any]) -> str:
    """Activities by engagement type."""
    eng_type = entities.get('type', '')
    return f"StakeholderEngagement.objects.filter(engagement_type__name__icontains='{eng_type}').count()"


def _activities_timeline(entities: Dict[str, Any]) -> str:
    """Activity timeline for date range."""
    date_filter = build_date_range_filter(entities, "scheduled_date")
    if date_filter:
        return f"StakeholderEngagement.objects.filter({date_filter}).order_by('scheduled_date').values('title', 'scheduled_date', 'status')[:30]"
    return "StakeholderEngagement.objects.order_by('scheduled_date').values('title', 'scheduled_date', 'status')[:30]"


def _activities_by_org(entities: Dict[str, Any]) -> str:
    """Activities by organization."""
    org = entities.get('organization', '')
    return f"StakeholderEngagement.objects.filter(participating_organizations__name__icontains='{org}').values('title', 'engagement_type__name', 'scheduled_date')[:20]"


def _activities_count(entities: Dict[str, Any]) -> str:
    """Total activity count."""
    return "StakeholderEngagement.objects.count()"


# =============================================================================
# RESOURCE COORDINATION QUERIES (5 templates)
# =============================================================================

def _shared_resources(entities: Dict[str, Any]) -> str:
    """List shared resources in partnerships."""
    return "Partnership.objects.exclude(resources_shared='').values('title', 'resources_shared', 'lead_organization__name')[:20]"


def _resources_by_partnership(entities: Dict[str, Any]) -> str:
    """Resources for specific partnership."""
    pid = entities.get('id', '')
    return f"Partnership.objects.filter(id='{pid}').values('title', 'resources_shared', 'resource_contributions')[:1]"


def _resource_allocation(entities: Dict[str, Any]) -> str:
    """Resource allocation across partnerships."""
    return "Partnership.objects.exclude(resource_contributions='').values('title', 'lead_organization__name', 'resource_contributions').order_by('-created_at')[:15]"


def _partnerships_with_resources(entities: Dict[str, Any]) -> str:
    """Partnerships with resource sharing."""
    return "Partnership.objects.exclude(resources_shared='').count()"


def _resource_types(entities: Dict[str, Any]) -> str:
    """Types of resources shared."""
    return "Partnership.objects.exclude(resources_shared='').values('resources_shared')[:30]"


# =============================================================================
# MOA/MOU MANAGEMENT QUERIES (5 templates)
# =============================================================================

def _active_moas(entities: Dict[str, Any]) -> str:
    """Active MOAs/MOUs."""
    return "Partnership.objects.filter(status='active', partnership_type__icontains='moa').count()"


def _moa_expiring_soon(entities: Dict[str, Any]) -> str:
    """MOAs expiring within 90 days."""
    return "Partnership.objects.filter(status='active', end_date__lte=timezone.now().date() + timedelta(days=90), end_date__gte=timezone.now().date()).values('title', 'lead_organization__name', 'end_date')[:15]"


def _moa_by_agency(entities: Dict[str, Any]) -> str:
    """MOAs with specific agency."""
    org = entities.get('organization', '')
    return f"Partnership.objects.filter(Q(partnership_type__icontains='moa') | Q(partnership_type__icontains='mou'), Q(lead_organization__name__icontains='{org}') | Q(partner_organizations__name__icontains='{org}')).distinct().values('title', 'partnership_type', 'status', 'start_date')[:20]"


def _moa_renewals(entities: Dict[str, Any]) -> str:
    """MOAs pending renewal."""
    return "Partnership.objects.filter(status='pending_renewal').values('title', 'lead_organization__name', 'end_date').order_by('end_date')[:10]"


def _moa_list(entities: Dict[str, Any]) -> str:
    """List all MOAs/MOUs."""
    return "Partnership.objects.filter(Q(partnership_type__icontains='moa') | Q(partnership_type__icontains='mou')).values('id', 'title', 'partnership_type', 'status', 'start_date', 'end_date')[:25]"


# =============================================================================
# COLLABORATION ANALYTICS QUERIES (5 templates)
# =============================================================================

def _partnership_effectiveness(entities: Dict[str, Any]) -> str:
    """Partnership effectiveness metrics."""
    return "Partnership.objects.filter(status='active').values('title', 'lead_organization__name', 'deliverables', 'impact_assessment').order_by('-created_at')[:15]"


def _engagement_metrics(entities: Dict[str, Any]) -> str:
    """Stakeholder engagement metrics."""
    return "StakeholderEngagement.objects.aggregate(total=Count('id'), completed=Count('id', filter=Q(status='completed')), scheduled=Count('id', filter=Q(status='scheduled')))"


def _organization_activity_level(entities: Dict[str, Any]) -> str:
    """Activity level by organization."""
    return "Organization.objects.annotate(activity_count=Count('stakeholder_engagements')).filter(activity_count__gt=0).order_by('-activity_count').values('name', 'organization_type', 'activity_count')[:20]"


def _partnership_by_sector_stats(entities: Dict[str, Any]) -> str:
    """Partnership distribution by sector."""
    return "Partnership.objects.values('focus_sectors').annotate(count=Count('id')).order_by('-count')[:15]"


def _collaboration_trends(entities: Dict[str, Any]) -> str:
    """Collaboration trends over time."""
    date_filter = build_date_range_filter(entities, "created_at")
    if date_filter:
        return f"Partnership.objects.filter({date_filter}).values('created_at__year', 'created_at__month').annotate(count=Count('id')).order_by('created_at__year', 'created_at__month')"
    return "Partnership.objects.values('created_at__year', 'created_at__month').annotate(count=Count('id')).order_by('created_at__year', 'created_at__month')[:12]"


# =============================================================================
# ENGAGEMENT HISTORY QUERIES (5 templates)
# =============================================================================

def _org_engagement_history(entities: Dict[str, Any]) -> str:
    """Engagement history for organization."""
    org = entities.get('organization', '')
    return f"StakeholderEngagement.objects.filter(participating_organizations__name__icontains='{org}').order_by('-scheduled_date').values('title', 'engagement_type__name', 'scheduled_date', 'status')[:15]"


def _partnership_history(entities: Dict[str, Any]) -> str:
    """Historical partnerships."""
    return "Partnership.objects.filter(status='completed').order_by('-end_date').values('title', 'lead_organization__name', 'start_date', 'end_date', 'impact_assessment')[:20]"


def _recent_engagements(entities: Dict[str, Any]) -> str:
    """Recent stakeholder engagements."""
    return "StakeholderEngagement.objects.order_by('-created_at')[:15].values('title', 'engagement_type__name', 'scheduled_date', 'status')"


def _engagement_outcomes(entities: Dict[str, Any]) -> str:
    """Outcomes from engagements."""
    return "StakeholderEngagement.objects.filter(status='completed').exclude(outcomes='').values('title', 'scheduled_date', 'outcomes')[:20]"


def _partnership_milestones(entities: Dict[str, Any]) -> str:
    """Partnership milestones achieved."""
    return "Partnership.objects.exclude(deliverables='').values('title', 'lead_organization__name', 'deliverables', 'status').order_by('-updated_at')[:15]"


# =============================================================================
# TEMPLATE DEFINITIONS (55 templates total)
# =============================================================================

COORDINATION_TEMPLATES = [
    # Partnership templates
    QueryTemplate(
        pattern=r"partnerships?\s+in\s+(?P<location>.+)",
        category="coordination",
        intent="data_query",
        query_builder=_partnerships_in_location,
        description="Count partnerships in location",
        example_queries=["Partnerships in Region IX", "How many partnerships in Zamboanga del Sur?"],
        required_entities=["location"],
        priority=70,
    ),
    QueryTemplate(
        pattern=r"(active|ongoing)\s+partnerships?",
        category="coordination",
        intent="data_query",
        query_builder=_active_partnerships,
        description="Count active partnerships",
        example_queries=["Active partnerships", "Show me ongoing partnerships"],
        priority=60,
    ),
    QueryTemplate(
        pattern=r"partnerships?\s+with\s+(?P<organization>.+)",
        category="coordination",
        intent="data_query",
        query_builder=_partnerships_with_org,
        description="Partnerships with specific organization",
        example_queries=["Partnerships with BARMM", "How many partnerships with DSWD?"],
        required_entities=["organization"],
        priority=70,
    ),
    QueryTemplate(
        pattern=r"(how\s+many|total|count)\s+partnerships?",
        category="coordination",
        intent="data_query",
        query_builder=_partnership_count,
        description="Total partnership count",
        example_queries=["How many partnerships?", "Total partnerships", "Count partnerships"],
        priority=50,
    ),
    QueryTemplate(
        pattern=r"(?P<type>\w+)\s+partnerships?",
        category="coordination",
        intent="data_query",
        query_builder=_partnerships_by_type,
        description="Partnerships by type",
        example_queries=["Technical partnerships", "Funding partnerships"],
        required_entities=["type"],
        priority=40,
    ),
    QueryTemplate(
        pattern=r"recent\s+partnerships?",
        category="coordination",
        intent="data_query",
        query_builder=_recent_partnerships,
        description="Recently created partnerships",
        example_queries=["Recent partnerships", "Show me recent partnerships"],
        priority=60,
    ),
    QueryTemplate(
        pattern=r"(list|show)\s+(all\s+)?partnerships?",
        category="coordination",
        intent="data_query",
        query_builder=_list_partnerships,
        description="List all partnerships",
        example_queries=["List all partnerships", "Show partnerships"],
        priority=55,
    ),
    QueryTemplate(
        pattern=r"partnerships?\s+in\s+(?P<sector>.+)\s+sector",
        category="coordination",
        intent="data_query",
        query_builder=_partnerships_by_sector,
        description="Partnerships in sector",
        example_queries=["Partnerships in education sector", "Health sector partnerships"],
        required_entities=["sector"],
        priority=65,
    ),
    QueryTemplate(
        pattern=r"partnership\s+(?P<id>[\w-]+)",
        category="coordination",
        intent="data_query",
        query_builder=_partnership_details,
        description="Partnership details",
        example_queries=["Partnership abc-123", "Show me partnership details"],
        required_entities=["id"],
        priority=80,
    ),
    QueryTemplate(
        pattern=r"(?P<status>active|completed|pending)\s+partnerships?",
        category="coordination",
        intent="data_query",
        query_builder=_partnerships_by_status,
        description="Partnerships by status",
        example_queries=["Completed partnerships", "Pending partnerships"],
        required_entities=["status"],
        priority=60,
    ),

    # Organization templates
    QueryTemplate(
        pattern=r"organizations?\s+in\s+(?P<sector>.+)\s+sector",
        category="coordination",
        intent="data_query",
        query_builder=_orgs_in_sector,
        description="Organizations in sector",
        example_queries=["Organizations in health sector", "Education sector organizations"],
        required_entities=["sector"],
        priority=70,
    ),
    QueryTemplate(
        pattern=r"(active\s+)?(stakeholders?|organizations?)",
        category="coordination",
        intent="data_query",
        query_builder=_active_stakeholders,
        description="Active stakeholder organizations",
        example_queries=["Active stakeholders", "Show me active organizations"],
        priority=55,
    ),
    QueryTemplate(
        pattern=r"ngos?\s+in\s+(?P<location>.+)",
        category="coordination",
        intent="data_query",
        query_builder=_ngos_in_location,
        description="NGOs in location",
        example_queries=["NGOs in Region IX", "How many NGOs in Zamboanga?"],
        required_entities=["location"],
        priority=70,
    ),
    QueryTemplate(
        pattern=r"(how\s+many|total|count)\s+organizations?",
        category="coordination",
        intent="data_query",
        query_builder=_org_count,
        description="Total organization count",
        example_queries=["How many organizations?", "Total organizations"],
        priority=50,
    ),
    QueryTemplate(
        pattern=r"(list|show)\s+(all\s+)?organizations?",
        category="coordination",
        intent="data_query",
        query_builder=_list_organizations,
        description="List all organizations",
        example_queries=["List all organizations", "Show organizations"],
        priority=55,
    ),
    QueryTemplate(
        pattern=r"(?P<type>ngo|government|private|academic)\s+organizations?",
        category="coordination",
        intent="data_query",
        query_builder=_orgs_by_type,
        description="Organizations by type",
        example_queries=["NGO organizations", "Government organizations"],
        required_entities=["type"],
        priority=65,
    ),
    QueryTemplate(
        pattern=r"government\s+agencies",
        category="coordination",
        intent="data_query",
        query_builder=_government_agencies,
        description="Government agency count",
        example_queries=["Government agencies", "How many government agencies?"],
        priority=60,
    ),
    QueryTemplate(
        pattern=r"organization\s+(?P<id>[\w-]+)",
        category="coordination",
        intent="data_query",
        query_builder=_org_details,
        description="Organization details",
        example_queries=["Organization abc-123", "Show me organization details"],
        required_entities=["id"],
        priority=80,
    ),
    QueryTemplate(
        pattern=r"organizations?\s+in\s+(?P<location>.+)",
        category="coordination",
        intent="data_query",
        query_builder=_orgs_in_location,
        description="Organizations in location",
        example_queries=["Organizations in Region IX", "Organizations in Zamboanga"],
        required_entities=["location"],
        priority=70,
    ),
    QueryTemplate(
        pattern=r"(find|search)\s+organization\s+(?P<name>.+)",
        category="coordination",
        intent="data_query",
        query_builder=_search_organizations,
        description="Search organizations by name",
        example_queries=["Find organization DSWD", "Search organization Red Cross"],
        required_entities=["name"],
        priority=75,
    ),

    # Meeting/Engagement templates
    QueryTemplate(
        pattern=r"recent\s+meetings?",
        category="coordination",
        intent="data_query",
        query_builder=_recent_meetings,
        description="Recent meetings",
        example_queries=["Recent meetings", "Show me recent meetings"],
        priority=60,
    ),
    QueryTemplate(
        pattern=r"meetings?\s+with\s+(?P<organization>.+)",
        category="coordination",
        intent="data_query",
        query_builder=_meetings_with_org,
        description="Meetings with organization",
        example_queries=["Meetings with BARMM", "How many meetings with DSWD?"],
        required_entities=["organization"],
        priority=70,
    ),
    QueryTemplate(
        pattern=r"meeting\s+schedule",
        category="coordination",
        intent="data_query",
        query_builder=_meeting_schedule,
        description="Upcoming meeting schedule",
        example_queries=["Meeting schedule", "Show me meeting schedule"],
        priority=60,
    ),
    QueryTemplate(
        pattern=r"completed\s+meetings?",
        category="coordination",
        intent="data_query",
        query_builder=_completed_meetings,
        description="Completed meetings count",
        example_queries=["Completed meetings", "How many completed meetings?"],
        priority=55,
    ),
    QueryTemplate(
        pattern=r"meetings?\s+in\s+(?P<location>.+)",
        category="coordination",
        intent="data_query",
        query_builder=_meetings_in_location,
        description="Meetings in location",
        example_queries=["Meetings in Region IX", "How many meetings in Zamboanga?"],
        required_entities=["location"],
        priority=70,
    ),
    QueryTemplate(
        pattern=r"(how\s+many|total|count)\s+meetings?",
        category="coordination",
        intent="data_query",
        query_builder=_meeting_count,
        description="Total meeting count",
        example_queries=["How many meetings?", "Total meetings"],
        priority=50,
    ),
    QueryTemplate(
        pattern=r"planned\s+meetings?",
        category="coordination",
        intent="data_query",
        query_builder=_planned_meetings,
        description="Planned meetings count",
        example_queries=["Planned meetings", "How many planned meetings?"],
        priority=55,
    ),
    QueryTemplate(
        pattern=r"meeting\s+(?P<id>[\w-]+)",
        category="coordination",
        intent="data_query",
        query_builder=_meeting_details,
        description="Meeting details",
        example_queries=["Meeting abc-123", "Show me meeting details"],
        required_entities=["id"],
        priority=80,
    ),
    QueryTemplate(
        pattern=r"meetings?\s+from\s+(?P<date_start>[\d-]+)\s+to\s+(?P<date_end>[\d-]+)",
        category="coordination",
        intent="data_query",
        query_builder=_meetings_by_date_range,
        description="Meetings in date range",
        example_queries=["Meetings from 2025-01-01 to 2025-12-31"],
        required_entities=["date_start", "date_end"],
        priority=75,
    ),
    QueryTemplate(
        pattern=r"(today'?s?|today)\s+meetings?",
        category="coordination",
        intent="data_query",
        query_builder=_todays_meetings,
        description="Today's meetings",
        example_queries=["Today's meetings", "Meetings today"],
        priority=70,
    ),

    # =========================================================================
    # ACTIVITY TRACKING TEMPLATES (5 templates)
    # =========================================================================
    QueryTemplate(
        pattern=r"coordination\s+activities",
        category="coordination",
        intent="data_query",
        query_builder=_coordination_activities,
        description="List coordination activities (non-meeting)",
        example_queries=["Coordination activities", "Show coordination activities"],
        priority=60,
    ),
    QueryTemplate(
        pattern=r"(?P<type>workshop|training|consultation|assessment)\s+activities",
        category="coordination",
        intent="data_query",
        query_builder=_activities_by_type,
        description="Activities by engagement type",
        example_queries=["Workshop activities", "Training activities", "Consultation activities"],
        required_entities=["type"],
        priority=65,
    ),
    QueryTemplate(
        pattern=r"activit(y|ies)\s+timeline",
        category="coordination",
        intent="data_query",
        query_builder=_activities_timeline,
        description="Activity timeline for date range",
        example_queries=["Activity timeline", "Show activity timeline"],
        optional_entities=["date_start", "date_end"],
        priority=60,
    ),
    QueryTemplate(
        pattern=r"activities\s+(with|by)\s+(?P<organization>.+)",
        category="coordination",
        intent="data_query",
        query_builder=_activities_by_org,
        description="Activities by organization",
        example_queries=["Activities with DSWD", "Activities by BARMM"],
        required_entities=["organization"],
        priority=70,
    ),
    QueryTemplate(
        pattern=r"(how\s+many|total|count)\s+activities",
        category="coordination",
        intent="data_query",
        query_builder=_activities_count,
        description="Total activity count",
        example_queries=["How many activities?", "Total activities", "Count activities"],
        priority=50,
    ),

    # =========================================================================
    # RESOURCE COORDINATION TEMPLATES (5 templates)
    # =========================================================================
    QueryTemplate(
        pattern=r"shared\s+resources",
        category="coordination",
        intent="data_query",
        query_builder=_shared_resources,
        description="List shared resources in partnerships",
        example_queries=["Shared resources", "Show shared resources", "Resources being shared"],
        priority=60,
    ),
    QueryTemplate(
        pattern=r"resources\s+(for|in)\s+partnership\s+(?P<id>[\w-]+)",
        category="coordination",
        intent="data_query",
        query_builder=_resources_by_partnership,
        description="Resources for specific partnership",
        example_queries=["Resources for partnership abc-123", "Resources in partnership xyz"],
        required_entities=["id"],
        priority=75,
    ),
    QueryTemplate(
        pattern=r"resource\s+allocation",
        category="coordination",
        intent="data_query",
        query_builder=_resource_allocation,
        description="Resource allocation across partnerships",
        example_queries=["Resource allocation", "Show resource allocation"],
        priority=65,
    ),
    QueryTemplate(
        pattern=r"partnerships?\s+with\s+resources?",
        category="coordination",
        intent="data_query",
        query_builder=_partnerships_with_resources,
        description="Count partnerships with resource sharing",
        example_queries=["Partnerships with resources", "How many partnerships with resource sharing?"],
        priority=60,
    ),
    QueryTemplate(
        pattern=r"(types?\s+of\s+)?resources?\s+shared",
        category="coordination",
        intent="data_query",
        query_builder=_resource_types,
        description="Types of resources being shared",
        example_queries=["Types of resources shared", "Resource types", "What resources are shared?"],
        priority=55,
    ),

    # =========================================================================
    # MOA/MOU MANAGEMENT TEMPLATES (5 templates)
    # =========================================================================
    QueryTemplate(
        pattern=r"(active\s+)?(moas?|mous?|memorandum)",
        category="coordination",
        intent="data_query",
        query_builder=_active_moas,
        description="Active MOAs/MOUs count",
        example_queries=["Active MOAs", "MOUs", "Memorandum of agreements"],
        priority=70,
    ),
    QueryTemplate(
        pattern=r"(moas?|mous?)\s+(expiring|renewal|renew)",
        category="coordination",
        intent="data_query",
        query_builder=_moa_expiring_soon,
        description="MOAs expiring within 90 days",
        example_queries=["MOAs expiring", "MOUs needing renewal", "MOA renewal"],
        priority=75,
    ),
    QueryTemplate(
        pattern=r"(moas?|mous?)\s+with\s+(?P<organization>.+)",
        category="coordination",
        intent="data_query",
        query_builder=_moa_by_agency,
        description="MOAs with specific agency",
        example_queries=["MOAs with DSWD", "MOUs with BARMM", "Memorandum with OPAPP"],
        required_entities=["organization"],
        priority=75,
    ),
    QueryTemplate(
        pattern=r"(moas?|mous?)\s+pending\s+renewal",
        category="coordination",
        intent="data_query",
        query_builder=_moa_renewals,
        description="MOAs pending renewal",
        example_queries=["MOAs pending renewal", "MOUs needing renewal"],
        priority=70,
    ),
    QueryTemplate(
        pattern=r"(list|show)\s+(all\s+)?(moas?|mous?)",
        category="coordination",
        intent="data_query",
        query_builder=_moa_list,
        description="List all MOAs/MOUs",
        example_queries=["List all MOAs", "Show MOUs", "All memorandums"],
        priority=65,
    ),

    # =========================================================================
    # COLLABORATION ANALYTICS TEMPLATES (5 templates)
    # =========================================================================
    QueryTemplate(
        pattern=r"partnership\s+effectiveness",
        category="coordination",
        intent="data_query",
        query_builder=_partnership_effectiveness,
        description="Partnership effectiveness metrics",
        example_queries=["Partnership effectiveness", "How effective are partnerships?"],
        priority=65,
    ),
    QueryTemplate(
        pattern=r"engagement\s+metrics",
        category="coordination",
        intent="data_query",
        query_builder=_engagement_metrics,
        description="Stakeholder engagement metrics",
        example_queries=["Engagement metrics", "Show engagement statistics"],
        priority=60,
    ),
    QueryTemplate(
        pattern=r"(organization|agency)\s+activity\s+level",
        category="coordination",
        intent="data_query",
        query_builder=_organization_activity_level,
        description="Activity level by organization",
        example_queries=["Organization activity level", "Agency activity level", "Most active organizations"],
        priority=65,
    ),
    QueryTemplate(
        pattern=r"partnerships?\s+by\s+sector",
        category="coordination",
        intent="data_query",
        query_builder=_partnership_by_sector_stats,
        description="Partnership distribution by sector",
        example_queries=["Partnerships by sector", "Sector distribution"],
        priority=60,
    ),
    QueryTemplate(
        pattern=r"collaboration\s+trends",
        category="coordination",
        intent="data_query",
        query_builder=_collaboration_trends,
        description="Collaboration trends over time",
        example_queries=["Collaboration trends", "Partnership trends", "Show collaboration trends"],
        optional_entities=["date_start", "date_end"],
        priority=65,
    ),

    # =========================================================================
    # ENGAGEMENT HISTORY TEMPLATES (5 templates)
    # =========================================================================
    QueryTemplate(
        pattern=r"engagement\s+history\s+(for|of)\s+(?P<organization>.+)",
        category="coordination",
        intent="data_query",
        query_builder=_org_engagement_history,
        description="Engagement history for organization",
        example_queries=["Engagement history for DSWD", "Engagement history of BARMM"],
        required_entities=["organization"],
        priority=70,
    ),
    QueryTemplate(
        pattern=r"(historical|past|completed)\s+partnerships?",
        category="coordination",
        intent="data_query",
        query_builder=_partnership_history,
        description="Historical partnerships",
        example_queries=["Historical partnerships", "Past partnerships", "Completed partnerships"],
        priority=60,
    ),
    QueryTemplate(
        pattern=r"recent\s+engagements?",
        category="coordination",
        intent="data_query",
        query_builder=_recent_engagements,
        description="Recent stakeholder engagements",
        example_queries=["Recent engagements", "Latest engagements", "Show recent engagements"],
        priority=60,
    ),
    QueryTemplate(
        pattern=r"engagement\s+outcomes",
        category="coordination",
        intent="data_query",
        query_builder=_engagement_outcomes,
        description="Outcomes from completed engagements",
        example_queries=["Engagement outcomes", "Show engagement outcomes", "What were the outcomes?"],
        priority=65,
    ),
    QueryTemplate(
        pattern=r"partnership\s+milestones",
        category="coordination",
        intent="data_query",
        query_builder=_partnership_milestones,
        description="Partnership milestones achieved",
        example_queries=["Partnership milestones", "Show milestones", "Deliverables achieved"],
        priority=65,
    ),
]

# Total: 30 (original) + 25 (new) = 55 templates
