"""
Communities & MANA Query Templates for OBCMS Chat System

Comprehensive templates covering:
- Communities: Count, list, filter, aggregate queries (30 templates)
- MANA: Workshop, assessment, needs queries (30 templates)

Total: 60+ query templates for natural language queries.

Performance target: <50ms query matching and generation
"""

import logging
from common.ai_services.chat.query_templates.base import QueryTemplate, get_template_registry

logger = logging.getLogger(__name__)


# ============================================================================
# COMMUNITIES QUERY TEMPLATES (30 templates)
# ============================================================================


def register_communities_templates():
    """Register all Communities query templates (30 templates)."""
    registry = get_template_registry()

    templates = [
        # COUNT QUERIES (10 templates)
        QueryTemplate(
            id="count_all_communities",
            category="communities",
            pattern=r"(?:how many|count|total|number of).*(?:obc )?communit(?:y|ies)",
            description="Count total OBC communities",
            query_template="OBCCommunity.objects.all().count()",
            required_entities=[],
            examples=["how many communities", "count all communities"],
            tags=["count", "total"],
            priority=7,
        ),
        QueryTemplate(
            id="count_communities_by_location",
            category="communities",
            pattern=r"(?:how many|count).*communit(?:y|ies).*(?:in|at|from)\s+",
            description="Count communities in a specific location",
            query_template="OBCCommunity.objects.filter({location_filter}).count()",
            required_entities=["location"],
            examples=["how many communities in Region IX", "count communities from Zamboanga"],
            tags=["count", "location"],
            priority=10,
        ),
        QueryTemplate(
            id="count_communities_by_ethnicity",
            category="communities",
            pattern=r"(?:how many|count).*(?:maranao|tausug|maguindanaon|sama|badjao|iranun|yakan).*communit",
            description="Count communities by ethnolinguistic group",
            query_template="OBCCommunity.objects.filter(primary_ethnolinguistic_group__icontains='{ethnolinguistic_group}').count()",
            required_entities=["ethnolinguistic_group"],
            examples=["how many maranao communities", "count tausug communities"],
            tags=["count", "ethnicity"],
            priority=9,
        ),
        QueryTemplate(
            id="count_communities_by_livelihood",
            category="communities",
            pattern=r"(?:how many|count).*(?:fishing|farming|agricultural|trade).*communit",
            description="Count communities by livelihood",
            query_template="OBCCommunity.objects.filter(primary_livelihoods__icontains='{livelihood}').count()",
            required_entities=["livelihood"],
            examples=["how many fishing communities", "count farming communities"],
            tags=["count", "livelihood"],
            priority=8,
        ),
        QueryTemplate(
            id="count_communities_high_population",
            category="communities",
            pattern=r"(?:how many|count).*communit(?:y|ies).*(?:with|having|over|above)\s+\d+",
            description="Count communities with population above threshold",
            query_template="OBCCommunity.objects.filter(estimated_obc_population__gt={threshold}).count()",
            required_entities=[],
            examples=["how many communities with over 1000 people"],
            tags=["count", "population"],
            priority=7,
        ),
        QueryTemplate(
            id="count_communities_by_service_access",
            category="communities",
            pattern=r"(?:how many|count).*communit(?:y|ies).*(?:poor|fair|good|excellent).*(?:access|education|healthcare)",
            description="Count communities by service access level",
            query_template="OBCCommunity.objects.filter(access_{service}='{access_level}').count()",
            required_entities=["service", "access_level"],
            examples=["how many communities with poor education access"],
            tags=["count", "service", "access"],
            priority=8,
        ),
        QueryTemplate(
            id="count_communities_by_proximity_barmm",
            category="communities",
            pattern=r"(?:how many|count).*communit(?:y|ies).*(?:adjacent|near|distant).*barmm",
            description="Count communities by proximity to BARMM",
            query_template="OBCCommunity.objects.filter(proximity_to_barmm='{proximity}').count()",
            required_entities=["proximity"],
            examples=["how many communities adjacent to BARMM"],
            tags=["count", "proximity", "barmm"],
            priority=8,
        ),
        QueryTemplate(
            id="count_communities_by_region_specific",
            category="communities",
            pattern=r"(?:how many|count).*communit(?:y|ies).*region\s+(?:ix|9|x|10|xi|11|xii|12)",
            description="Count communities in specific region",
            query_template="OBCCommunity.objects.filter({location_filter}).count()",
            required_entities=["location"],
            examples=["how many communities in Region IX", "count communities Region 12"],
            tags=["count", "region"],
            priority=10,
        ),
        QueryTemplate(
            id="count_communities_by_province_specific",
            category="communities",
            pattern=r"(?:how many|count).*communit(?:y|ies).*(?:zamboanga|bukidnon|davao|sarangani|sultan kudarat)",
            description="Count communities in specific province",
            query_template="OBCCommunity.objects.filter({location_filter}).count()",
            required_entities=["location"],
            examples=["how many communities in Zamboanga", "count Bukidnon communities"],
            tags=["count", "province"],
            priority=10,
        ),
        QueryTemplate(
            id="count_communities_vulnerable",
            category="communities",
            pattern=r"(?:how many|count).*(?:vulnerable|underserved|marginalized).*communit",
            description="Count vulnerable or underserved communities",
            query_template="OBCCommunity.objects.filter(Q(access_healthcare='poor') | Q(access_education='poor') | Q(access_clean_water='poor')).count()",
            required_entities=[],
            examples=["how many vulnerable communities", "count underserved communities"],
            tags=["count", "vulnerable"],
            priority=7,
        ),

        # LIST QUERIES (10 templates)
        QueryTemplate(
            id="list_all_communities",
            category="communities",
            pattern=r"(?:list|show|display).*(?:all |the )?communit(?:y|ies)",
            description="List all OBC communities",
            query_template="OBCCommunity.objects.all()[:20]",
            required_entities=[],
            examples=["list all communities", "show communities"],
            tags=["list", "all"],
            priority=6,
        ),
        QueryTemplate(
            id="list_communities_by_location",
            category="communities",
            pattern=r"(?:list|show|display).*communit(?:y|ies).*(?:in|at|from)\s+",
            description="List communities in specific location",
            query_template="OBCCommunity.objects.filter({location_filter})[:20]",
            required_entities=["location"],
            examples=["list communities in Region IX", "show communities from Zamboanga"],
            tags=["list", "location"],
            priority=9,
        ),
        QueryTemplate(
            id="list_communities_by_ethnicity",
            category="communities",
            pattern=r"(?:list|show|display).*(?:maranao|tausug|maguindanaon|sama|badjao|iranun|yakan).*communit",
            description="List communities by ethnolinguistic group",
            query_template="OBCCommunity.objects.filter(primary_ethnolinguistic_group__icontains='{ethnolinguistic_group}')[:20]",
            required_entities=["ethnolinguistic_group"],
            examples=["list maranao communities", "show tausug communities"],
            tags=["list", "ethnicity"],
            priority=8,
        ),
        QueryTemplate(
            id="list_communities_by_livelihood",
            category="communities",
            pattern=r"(?:list|show|display).*(?:fishing|farming|agricultural|trade).*communit",
            description="List communities by livelihood",
            query_template="OBCCommunity.objects.filter(primary_livelihoods__icontains='{livelihood}')[:20]",
            required_entities=["livelihood"],
            examples=["list fishing communities", "show farming communities"],
            tags=["list", "livelihood"],
            priority=8,
        ),
        QueryTemplate(
            id="list_communities_poor_access",
            category="communities",
            pattern=r"(?:list|show|display).*communit(?:y|ies).*poor.*(?:access|education|healthcare|water)",
            description="List communities with poor service access",
            query_template="OBCCommunity.objects.filter(access_{service}='poor')[:20]",
            required_entities=[],
            examples=["list communities with poor education access"],
            tags=["list", "service", "access", "poor"],
            priority=7,
        ),
        QueryTemplate(
            id="list_recent_communities",
            category="communities",
            pattern=r"(?:list|show|display).*recent.*communit",
            description="List recently added communities",
            query_template="OBCCommunity.objects.order_by('-created_at')[:20]",
            required_entities=[],
            examples=["show recent communities", "list recently added communities"],
            tags=["list", "recent"],
            priority=7,
        ),
        QueryTemplate(
            id="list_largest_communities",
            category="communities",
            pattern=r"(?:list|show|display).*(?:largest|biggest).*communit",
            description="List communities by population (largest first)",
            query_template="OBCCommunity.objects.filter(estimated_obc_population__isnull=False).order_by('-estimated_obc_population')[:20]",
            required_entities=[],
            examples=["show largest communities", "list biggest communities"],
            tags=["list", "population", "largest"],
            priority=7,
        ),
        QueryTemplate(
            id="list_communities_ethnicity_location",
            category="communities",
            pattern=r"(?:maranao|tausug|maguindanaon|sama|badjao|iranun|yakan).*communit.*(?:in|at|from)\s+",
            description="List communities by ethnicity and location",
            query_template="OBCCommunity.objects.filter({location_filter}, primary_ethnolinguistic_group__icontains='{ethnolinguistic_group}')[:20]",
            required_entities=["ethnolinguistic_group", "location"],
            examples=["maranao communities in Region IX"],
            tags=["list", "ethnicity", "location"],
            priority=10,
        ),
        QueryTemplate(
            id="list_communities_livelihood_location",
            category="communities",
            pattern=r"(?:fishing|farming|agricultural|trade).*communit.*(?:in|at|from)\s+",
            description="List communities by livelihood and location",
            query_template="OBCCommunity.objects.filter({location_filter}, primary_livelihoods__icontains='{livelihood}')[:20]",
            required_entities=["livelihood", "location"],
            examples=["fishing communities in Zamboanga"],
            tags=["list", "livelihood", "location"],
            priority=9,
        ),
        QueryTemplate(
            id="list_communities_needing_support",
            category="communities",
            pattern=r"(?:list|show|display).*communit(?:y|ies).*(?:need|requiring).*(?:support|assistance|help)",
            description="List communities needing support",
            query_template="OBCCommunity.objects.exclude(priority_needs='')[:20]",
            required_entities=[],
            examples=["show communities needing support", "list communities requiring assistance"],
            tags=["list", "needs", "support"],
            priority=7,
        ),

        # AGGREGATE QUERIES (10 templates)
        QueryTemplate(
            id="total_obc_population",
            category="communities",
            pattern=r"(?:total|what.s).*(?:obc )?population",
            description="Calculate total OBC population",
            query_template="OBCCommunity.objects.aggregate(total=Sum('estimated_obc_population'))['total']",
            required_entities=[],
            examples=["total obc population", "what's the total population"],
            tags=["aggregate", "population", "total"],
            priority=8,
        ),
        QueryTemplate(
            id="average_community_population",
            category="communities",
            pattern=r"average.*(?:community )?population",
            description="Calculate average population per community",
            query_template="OBCCommunity.objects.aggregate(avg=Avg('estimated_obc_population'))['avg']",
            required_entities=[],
            examples=["average community population", "mean population per community"],
            tags=["aggregate", "population", "average"],
            priority=7,
        ),
        QueryTemplate(
            id="top_ethnolinguistic_groups",
            category="communities",
            pattern=r"(?:top|most common|major).*(?:ethnic|ethnolinguistic).*groups",
            description="Show most common ethnolinguistic groups",
            query_template="OBCCommunity.objects.values('primary_ethnolinguistic_group').annotate(count=Count('id')).order_by('-count')[:10]",
            required_entities=[],
            examples=["top ethnic groups", "most common ethnolinguistic groups"],
            tags=["aggregate", "ethnicity", "top"],
            priority=7,
        ),
        QueryTemplate(
            id="top_livelihoods",
            category="communities",
            pattern=r"(?:top|most common|major).*livelihoods",
            description="Show most common livelihoods",
            query_template="OBCCommunity.objects.values('primary_livelihoods').annotate(count=Count('id')).order_by('-count')[:10]",
            required_entities=[],
            examples=["top livelihoods", "most common livelihoods"],
            tags=["aggregate", "livelihood", "top"],
            priority=7,
        ),
        QueryTemplate(
            id="total_households",
            category="communities",
            pattern=r"total.*households",
            description="Calculate total households across communities",
            query_template="OBCCommunity.objects.aggregate(total=Sum('households'))['total']",
            required_entities=[],
            examples=["total households", "how many households"],
            tags=["aggregate", "households", "total"],
            priority=7,
        ),
        QueryTemplate(
            id="population_by_region",
            category="communities",
            pattern=r"population.*by region",
            description="Show population distribution by region",
            query_template="OBCCommunity.objects.values('barangay__municipality__province__region__name').annotate(total_population=Sum('estimated_obc_population')).order_by('-total_population')",
            required_entities=[],
            examples=["population by region", "regional population breakdown"],
            tags=["aggregate", "population", "region"],
            priority=8,
        ),
        QueryTemplate(
            id="communities_by_province",
            category="communities",
            pattern=r"communit(?:y|ies).*by province",
            description="Show community count by province",
            query_template="OBCCommunity.objects.values('barangay__municipality__province__name').annotate(count=Count('id')).order_by('-count')",
            required_entities=[],
            examples=["communities by province", "provincial community breakdown"],
            tags=["aggregate", "province", "count"],
            priority=7,
        ),
        QueryTemplate(
            id="service_access_statistics",
            category="communities",
            pattern=r"(?:service )?access.*(?:statistics|breakdown)",
            description="Show service access level distribution",
            query_template="OBCCommunity.objects.values('access_{service}').annotate(count=Count('id')).order_by('-count')",
            required_entities=[],
            examples=["education access statistics", "healthcare access breakdown"],
            tags=["aggregate", "service", "access"],
            priority=7,
        ),
        QueryTemplate(
            id="total_vulnerable_populations",
            category="communities",
            pattern=r"total.*(?:pwd|children|women|seniors|farmers|fisherfolk)",
            description="Calculate total vulnerable populations",
            query_template="OBCCommunity.objects.aggregate(total=Sum('{sector}_count'))['total']",
            required_entities=[],
            examples=["total pwd count", "how many farmers"],
            tags=["aggregate", "vulnerable", "sectors"],
            priority=7,
        ),
        QueryTemplate(
            id="settlement_type_distribution",
            category="communities",
            pattern=r"settlement.*(?:type|distribution|breakdown)",
            description="Show settlement type distribution",
            query_template="OBCCommunity.objects.values('settlement_type').annotate(count=Count('id')).order_by('-count')",
            required_entities=[],
            examples=["settlement type distribution", "settlement breakdown"],
            tags=["aggregate", "settlement"],
            priority=6,
        ),
    ]

    try:
        registry.register_many(templates)
        logger.info(f"Registered {len(templates)} Communities templates")
    except Exception as e:
        logger.error(f"Failed to register Communities templates: {e}")


# ============================================================================
# MANA QUERY TEMPLATES (30 templates)
# ============================================================================


def register_mana_templates():
    """Register all MANA/Workshop/Assessment query templates (30 templates)."""
    registry = get_template_registry()

    templates = [
        # WORKSHOP QUERIES (15 templates)
        QueryTemplate(
            id="count_all_workshops",
            category="mana",
            pattern=r"(?:how many|count|total).*(?:mana )?(?:workshops?|assessments?)",
            description="Count total MANA workshops/assessments",
            query_template="Assessment.objects.all().count()",
            required_entities=[],
            examples=["how many workshops", "count all assessments"],
            tags=["count", "workshops"],
            priority=7,
        ),
        QueryTemplate(
            id="count_workshops_by_location",
            category="mana",
            pattern=r"(?:how many|count).*(?:workshops?|assessments?).*(?:in|at|from)\s+",
            description="Count workshops in specific location",
            query_template="Assessment.objects.filter({location_filter}).count()",
            required_entities=["location"],
            examples=["how many workshops in Region IX", "count assessments from Zamboanga"],
            tags=["count", "workshops", "location"],
            priority=10,
        ),
        QueryTemplate(
            id="list_recent_workshops",
            category="mana",
            pattern=r"(?:recent|latest).*(?:workshops?|assessments?)",
            description="Show recent MANA workshops",
            query_template="Assessment.objects.order_by('-actual_start_date')[:10]",
            required_entities=[],
            examples=["recent workshops", "latest assessments"],
            tags=["list", "workshops", "recent"],
            priority=9,
        ),
        QueryTemplate(
            id="list_upcoming_workshops",
            category="mana",
            pattern=r"(?:upcoming|planned|scheduled).*(?:workshops?|assessments?)",
            description="Show upcoming/planned workshops",
            query_template="Assessment.objects.filter(status__in=['planning', 'preparation']).order_by('planned_start_date')[:10]",
            required_entities=[],
            examples=["upcoming workshops", "planned assessments"],
            tags=["list", "workshops", "upcoming"],
            priority=9,
        ),
        QueryTemplate(
            id="list_workshops_by_status",
            category="mana",
            pattern=r"(?:planning|preparation|completed|ongoing|cancelled).*(?:workshops?|assessments?)",
            description="List workshops by status",
            query_template="Assessment.objects.filter(status='{status}')[:20]",
            required_entities=["status"],
            examples=["completed workshops", "ongoing assessments"],
            tags=["list", "workshops", "status"],
            priority=8,
        ),
        QueryTemplate(
            id="list_all_workshops",
            category="mana",
            pattern=r"(?:list|show|display).*(?:all )?(?:workshops?|assessments?)",
            description="List all MANA workshops",
            query_template="Assessment.objects.all()[:20]",
            required_entities=[],
            examples=["list all workshops", "show assessments"],
            tags=["list", "workshops"],
            priority=6,
        ),
        QueryTemplate(
            id="list_workshops_by_location",
            category="mana",
            pattern=r"(?:list|show|display).*(?:workshops?|assessments?).*(?:in|at|from)\s+",
            description="List workshops in specific location",
            query_template="Assessment.objects.filter({location_filter})[:20]",
            required_entities=["location"],
            examples=["list workshops in Region IX", "show assessments from Zamboanga"],
            tags=["list", "workshops", "location"],
            priority=9,
        ),
        QueryTemplate(
            id="count_completed_workshops",
            category="mana",
            pattern=r"(?:how many|count).*completed.*(?:workshops?|assessments?)",
            description="Count completed workshops",
            query_template="Assessment.objects.filter(status='completed').count()",
            required_entities=[],
            examples=["how many completed workshops", "count completed assessments"],
            tags=["count", "workshops", "completed"],
            priority=8,
        ),
        QueryTemplate(
            id="count_ongoing_workshops",
            category="mana",
            pattern=r"(?:how many|count).*(?:ongoing|active|in progress).*(?:workshops?|assessments?)",
            description="Count ongoing workshops",
            query_template="Assessment.objects.filter(status='data_collection').count()",
            required_entities=[],
            examples=["how many ongoing workshops", "count active assessments"],
            tags=["count", "workshops", "ongoing"],
            priority=8,
        ),
        QueryTemplate(
            id="list_workshops_this_year",
            category="mana",
            pattern=r"(?:workshops?|assessments?).*this year",
            description="List workshops conducted this year",
            query_template="Assessment.objects.filter(actual_start_date__year={current_year})[:20]",
            required_entities=[],
            examples=["workshops this year", "assessments in 2025"],
            tags=["list", "workshops", "year"],
            priority=7,
        ),
        QueryTemplate(
            id="list_workshops_by_priority",
            category="mana",
            pattern=r"(?:high|critical|medium|low).*priority.*(?:workshops?|assessments?)",
            description="List workshops by priority level",
            query_template="Assessment.objects.filter(priority='{priority}')[:20]",
            required_entities=["priority"],
            examples=["high priority workshops", "critical assessments"],
            tags=["list", "workshops", "priority"],
            priority=8,
        ),
        QueryTemplate(
            id="count_workshops_by_methodology",
            category="mana",
            pattern=r"(?:how many|count).*(?:survey|workshop|kii|fgd|participatory).*(?:workshops?|assessments?)",
            description="Count workshops by methodology",
            query_template="Assessment.objects.filter(primary_methodology='{methodology}').count()",
            required_entities=["methodology"],
            examples=["how many survey workshops", "count FGD assessments"],
            tags=["count", "workshops", "methodology"],
            priority=7,
        ),
        QueryTemplate(
            id="list_workshops_by_assessor",
            category="mana",
            pattern=r"(?:workshops?|assessments?).*(?:led by|by|conducted by)\s+",
            description="List workshops by lead assessor",
            query_template="Assessment.objects.filter(lead_assessor__username__icontains='{assessor}')[:20]",
            required_entities=["assessor"],
            examples=["workshops led by Juan", "assessments by Maria"],
            tags=["list", "workshops", "assessor"],
            priority=7,
        ),
        QueryTemplate(
            id="workshops_by_date_range",
            category="mana",
            pattern=r"(?:workshops?|assessments?).*(?:from|between).*(?:to|and)\s+",
            description="List workshops within date range",
            query_template="Assessment.objects.filter(actual_start_date__range=['{date_start}', '{date_end}'])[:20]",
            required_entities=["date_range"],
            examples=["workshops from Jan to March", "assessments between 2024-01-01 and 2024-12-31"],
            tags=["list", "workshops", "date"],
            priority=8,
        ),
        QueryTemplate(
            id="workshop_statistics_by_region",
            category="mana",
            pattern=r"(?:show |display |list )?(?:workshops?|assessments?).*by region",
            description="Show workshop count by region",
            query_template="Assessment.objects.values('region__name').annotate(count=Count('id')).order_by('-count')",
            required_entities=[],
            examples=["workshops by region", "show workshops by region", "regional assessment breakdown"],
            tags=["aggregate", "workshops", "region"],
            priority=7,
        ),

        # NEEDS/ASSESSMENT QUERIES (15 templates)
        QueryTemplate(
            id="list_all_assessments",
            category="mana",
            pattern=r"(?:list|show|display).*(?:all )?assessments?",
            description="List all needs assessments",
            query_template="Assessment.objects.all()[:20]",
            required_entities=[],
            examples=["list all assessments", "show assessments"],
            tags=["list", "assessments"],
            priority=6,
        ),
        QueryTemplate(
            id="assessments_by_location",
            category="mana",
            pattern=r"assessments?.*(?:in|at|from)\s+",
            description="List assessments in specific location",
            query_template="Assessment.objects.filter({location_filter})[:20]",
            required_entities=["location"],
            examples=["assessments in Region IX", "assessments from Zamboanga"],
            tags=["list", "assessments", "location"],
            priority=9,
        ),
        QueryTemplate(
            id="assessments_by_date",
            category="mana",
            pattern=r"assessments?.*(?:from|after|since)\s+",
            description="List assessments after a date",
            query_template="Assessment.objects.filter(actual_start_date__gte='{date}')[:20]",
            required_entities=[],
            examples=["assessments from 2024", "assessments since January"],
            tags=["list", "assessments", "date"],
            priority=7,
        ),
        QueryTemplate(
            id="assessment_findings",
            category="mana",
            pattern=r"(?:show|display|list).*(?:assessment )?findings",
            description="Show assessment findings",
            query_template="Assessment.objects.exclude(key_findings='')[:20]",
            required_entities=[],
            examples=["show assessment findings", "list findings"],
            tags=["list", "assessments", "findings"],
            priority=7,
        ),
        QueryTemplate(
            id="needs_identified",
            category="mana",
            pattern=r"(?:identified |priority )?needs",
            description="Show identified needs from assessments",
            query_template="Assessment.objects.exclude(recommendations='')[:20]",
            required_entities=[],
            examples=["show identified needs", "priority needs"],
            tags=["list", "needs"],
            priority=7,
        ),
        QueryTemplate(
            id="top_needs",
            category="mana",
            pattern=r"(?:top|most common|major).*needs",
            description="Show most common needs",
            query_template="Assessment.objects.exclude(recommendations='').values('recommendations')[:10]",
            required_entities=[],
            examples=["top needs", "most common needs"],
            tags=["aggregate", "needs", "top"],
            priority=7,
        ),
        QueryTemplate(
            id="needs_by_category",
            category="mana",
            pattern=r"needs.*by category",
            description="Show needs by assessment category",
            query_template="Assessment.objects.values('category__name').annotate(count=Count('id')).order_by('-count')",
            required_entities=[],
            examples=["needs by category", "category breakdown"],
            tags=["aggregate", "needs", "category"],
            priority=7,
        ),
        QueryTemplate(
            id="needs_by_location",
            category="mana",
            pattern=r"needs.*(?:in|at|from)\s+",
            description="Show needs in specific location",
            query_template="Assessment.objects.filter({location_filter}).exclude(recommendations='')[:20]",
            required_entities=["location"],
            examples=["needs in Region IX", "needs from Zamboanga"],
            tags=["list", "needs", "location"],
            priority=8,
        ),
        QueryTemplate(
            id="urgent_needs",
            category="mana",
            pattern=r"(?:show |display |list )?(?:urgent|critical|high priority).*needs",
            description="Show urgent/critical needs",
            query_template="Assessment.objects.filter(priority__in=['high', 'critical']).exclude(recommendations='')[:20]",
            required_entities=[],
            examples=["urgent needs", "show urgent needs", "critical needs"],
            tags=["list", "needs", "urgent"],
            priority=8,
        ),
        QueryTemplate(
            id="needs_analysis_summary",
            category="mana",
            pattern=r"needs.*(?:analysis|summary|overview)",
            description="Show needs analysis summary",
            query_template="Assessment.objects.aggregate(total=Count('id'), completed=Count('id', filter=Q(status='completed')))",
            required_entities=[],
            examples=["needs analysis", "needs summary"],
            tags=["aggregate", "needs", "summary"],
            priority=6,
        ),
        QueryTemplate(
            id="assessment_recommendations",
            category="mana",
            pattern=r"(?:assessment )?recommendations",
            description="Show recommendations from assessments",
            query_template="Assessment.objects.exclude(recommendations='')[:20]",
            required_entities=[],
            examples=["show recommendations", "assessment recommendations"],
            tags=["list", "recommendations"],
            priority=7,
        ),
        QueryTemplate(
            id="count_assessments_by_category",
            category="mana",
            pattern=r"(?:how many|count).*(?:needs assessment|baseline study|impact assessment).*assessments?",
            description="Count assessments by category",
            query_template="Assessment.objects.filter(category__name__icontains='{category}').count()",
            required_entities=["category"],
            examples=["how many needs assessment assessments", "count baseline study assessments"],
            tags=["count", "assessments", "category"],
            priority=8,
        ),
        QueryTemplate(
            id="assessments_high_impact",
            category="mana",
            pattern=r"high impact.*assessments?",
            description="Show high impact assessments",
            query_template="Assessment.objects.filter(impact_level__in=['high', 'critical'])[:20]",
            required_entities=[],
            examples=["high impact assessments", "critical impact assessments"],
            tags=["list", "assessments", "impact"],
            priority=7,
        ),
        QueryTemplate(
            id="assessment_coverage_by_province",
            category="mana",
            pattern=r"assessments?.*by province",
            description="Show assessment count by province",
            query_template="Assessment.objects.values('province__name').annotate(count=Count('id')).order_by('-count')",
            required_entities=[],
            examples=["assessments by province", "provincial assessment coverage"],
            tags=["aggregate", "assessments", "province"],
            priority=7,
        ),
        QueryTemplate(
            id="assessment_completion_rate",
            category="mana",
            pattern=r"(?:assessment )?completion.*(?:rate|statistics)",
            description="Show assessment completion statistics",
            query_template="Assessment.objects.aggregate(total=Count('id'), completed=Count('id', filter=Q(status='completed')))",
            required_entities=[],
            examples=["assessment completion rate", "completion statistics"],
            tags=["aggregate", "assessments", "completion"],
            priority=7,
        ),
    ]

    try:
        registry.register_many(templates)
        logger.info(f"Registered {len(templates)} MANA templates")
    except Exception as e:
        logger.error(f"Failed to register MANA templates: {e}")


# ============================================================================
# AUTO-REGISTRATION
# ============================================================================


def register_all_communities_mana_templates():
    """
    Register all Communities and MANA query templates (60 templates).

    Called automatically when module is imported.
    """
    try:
        register_communities_templates()
        register_mana_templates()

        registry = get_template_registry()
        stats = registry.get_stats()

        logger.info(
            f"Communities & MANA templates registered: "
            f"{stats['total_templates']} total templates"
        )
        logger.info(f"Categories: {list(stats['categories'].keys())}")

    except Exception as e:
        logger.error(f"Failed to register Communities & MANA templates: {e}")


# Auto-register templates when module is imported
register_all_communities_mana_templates()
