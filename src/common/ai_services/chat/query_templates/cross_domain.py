"""
Cross-Domain Query Templates for OBCMS Chat System

40 templates for cross-module relationship queries including:
- Communities + MANA (15 templates)
- MANA + Coordination (10 templates)
- Needs → Policies → Projects Pipeline (15 templates)
"""

from typing import Any, Dict
from common.ai_services.chat.query_templates.base import QueryTemplate


# =============================================================================
# COMMUNITIES + MANA QUERIES (15 templates)
# =============================================================================

CROSS_DOMAIN_COMMUNITIES_MANA_TEMPLATES = [
    QueryTemplate(
        id='communities_with_assessments',
        category='cross_domain',
        pattern=r'\bcommunities\s+(with|having)\s+(active\s+)?assessments?',
        query_template='OBCCommunity.objects.filter(assessments__isnull=False).distinct().select_related("barangay__municipality__province__region")',
        required_entities=[],
        optional_entities=['status'],
        examples=[
            'Communities with active assessments',
            'Communities having assessments',
            'Show communities with assessments',
            'Which communities have assessments?'
        ],
        priority=8,
        description='Communities with assessments',
        tags=['cross_domain', 'communities', 'mana', 'assessments']
    ),
    QueryTemplate(
        id='communities_without_assessments',
        category='cross_domain',
        pattern=r'\bcommunities\s+(without|never assessed|no assessment)',
        query_template='OBCCommunity.objects.filter(assessments__isnull=True).select_related("barangay__municipality__province__region")',
        required_entities=[],
        optional_entities=['location'],
        examples=[
            'Communities without assessments',
            'Communities never assessed',
            'No assessment communities',
            'Which communities lack assessments?'
        ],
        priority=8,
        description='Communities without any assessments',
        tags=['cross_domain', 'communities', 'mana', 'gaps']
    ),
    QueryTemplate(
        id='communities_recent_assessment',
        category='cross_domain',
        pattern=r'\bcommunities\s+assessed\s+(in|within)\s+(last|past)?\s*(\d+)?\s*(months?|years?)',
        query_template='OBCCommunity.objects.filter(assessments__created_at__gte=timezone.now() - timedelta({period}={value})).distinct().select_related("barangay")',
        required_entities=['time_period'],
        optional_entities=[],
        examples=[
            'Communities assessed in last 12 months',
            'Communities assessed within past year',
            'Recent assessments by community',
            'Communities assessed last 6 months'
        ],
        priority=8,
        description='Communities assessed in timeframe',
        tags=['cross_domain', 'communities', 'mana', 'recent']
    ),
    QueryTemplate(
        id='assessment_coverage_by_ethnicity',
        category='cross_domain',
        pattern=r'\bassessment coverage\s+by\s+(ethnicity|ethnic group)',
        query_template='OBCCommunity.objects.values("primary_ethnolinguistic_group").annotate(total_communities=Count("id"), assessed_communities=Count("id", filter=Q(assessments__isnull=False)), coverage_rate=100.0 * Count("id", filter=Q(assessments__isnull=False)) / Count("id")).order_by("-coverage_rate")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Assessment coverage by ethnic group',
            'Coverage by ethnicity',
            'Which ethnic groups are assessed?',
            'Assessment penetration by ethnicity'
        ],
        priority=7,
        description='Assessment coverage by ethnic group',
        tags=['cross_domain', 'communities', 'mana', 'ethnicity']
    ),
    QueryTemplate(
        id='needs_per_community',
        category='cross_domain',
        pattern=r'\b(average|mean)\s+needs\s+(per|identified in)\s+communit',
        query_template='OBCCommunity.objects.annotate(needs_count=Count("assessments__identified_needs")).aggregate(avg_needs=Avg("needs_count"))',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Average needs identified per community',
            'Mean needs per community',
            'Needs per community average',
            'How many needs per community?'
        ],
        priority=7,
        description='Average needs per community',
        tags=['cross_domain', 'communities', 'mana', 'needs']
    ),
    QueryTemplate(
        id='communities_by_needs_count',
        category='cross_domain',
        pattern=r'\bcommunities\s+(with|by)\s+most\s+(identified\s+)?needs',
        query_template='OBCCommunity.objects.annotate(needs_count=Count("assessments__identified_needs")).filter(needs_count__gt=0).order_by("-needs_count").select_related("barangay__municipality__province")[:20]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Communities with most identified needs',
            'Communities by needs count',
            'Top communities by needs',
            'Most needs identified'
        ],
        priority=7,
        description='Communities ranked by needs count',
        tags=['cross_domain', 'communities', 'mana', 'ranking']
    ),
    QueryTemplate(
        id='communities_with_unmet_needs',
        category='cross_domain',
        pattern=r'\bcommunities\s+with\s+unmet\s+needs',
        query_template='OBCCommunity.objects.filter(assessments__identified_needs__status__in=["identified", "validated"]).distinct().select_related("barangay__municipality")',
        required_entities=[],
        optional_entities=['location'],
        examples=[
            'Communities with unmet needs',
            'Unaddressed needs by community',
            'Communities needing support',
            'Show communities with open needs'
        ],
        priority=8,
        description='Communities with unaddressed needs',
        tags=['cross_domain', 'communities', 'mana', 'unmet']
    ),
    QueryTemplate(
        id='assessment_to_needs_pipeline',
        category='cross_domain',
        pattern=r'\b(assessment to needs|assessments?\s+to\s+needs)\s+(pipeline|flow)',
        query_template='Assessment.objects.annotate(needs_count=Count("identified_needs")).values("status", "needs_count").order_by("-needs_count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Assessment to needs pipeline',
            'Assessments to needs identified',
            'Assessment needs flow',
            'Track assessment to needs conversion'
        ],
        priority=7,
        description='Assessments and their identified needs',
        tags=['cross_domain', 'mana', 'pipeline']
    ),
    QueryTemplate(
        id='communities_multiple_assessments',
        category='cross_domain',
        pattern=r'\bcommunities\s+with\s+(multiple|2\+|\d+\+)\s+assessments',
        query_template='OBCCommunity.objects.annotate(assessment_count=Count("assessments")).filter(assessment_count__gte={min_count}).order_by("-assessment_count").select_related("barangay")',
        required_entities=[],
        optional_entities=['number'],
        examples=[
            'Communities with 2+ assessments',
            'Communities with multiple assessments',
            'Multiple assessments per community',
            'Communities assessed more than once'
        ],
        priority=7,
        description='Communities with multiple assessments',
        tags=['cross_domain', 'communities', 'mana', 'multiple']
    ),
    QueryTemplate(
        id='community_assessment_history',
        category='cross_domain',
        pattern=r'\b(assessment history|full assessment)\s+(by|for)\s+community',
        query_template='Assessment.objects.select_related("community", "lead_organization").filter(community_id={community_id}).order_by("-created_at")',
        required_entities=['community_id'],
        optional_entities=[],
        examples=[
            'Full assessment history by community',
            'Assessment history for community',
            'Show all assessments for this community',
            'Community assessment timeline'
        ],
        priority=7,
        description='Complete assessment history for community',
        tags=['cross_domain', 'communities', 'mana', 'history']
    ),
    QueryTemplate(
        id='communities_by_assessment_status',
        category='cross_domain',
        pattern=r'\bcommunities\s+by\s+assessment\s+status',
        query_template='OBCCommunity.objects.filter(assessments__isnull=False).values("assessments__status").annotate(community_count=Count("id", distinct=True)).order_by("-community_count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Communities by assessment status',
            'Group communities by assessment phase',
            'Assessment status distribution',
            'Communities in each assessment stage'
        ],
        priority=7,
        description='Communities grouped by assessment status',
        tags=['cross_domain', 'communities', 'mana', 'status']
    ),
    QueryTemplate(
        id='assessment_geographic_coverage',
        category='cross_domain',
        pattern=r'\bassessment\s+(coverage|geographic coverage)\s+by\s+(province|region)',
        query_template='OBCCommunity.objects.values("barangay__municipality__province__{level}__name").annotate(total_communities=Count("id"), assessed_communities=Count("id", filter=Q(assessments__isnull=False)), coverage_pct=100.0 * Count("id", filter=Q(assessments__isnull=False)) / Count("id")).order_by("-coverage_pct")',
        required_entities=['location_level'],
        optional_entities=[],
        examples=[
            'Assessment coverage by province',
            'Geographic coverage by region',
            'Assessment penetration by province',
            'Coverage map by location'
        ],
        priority=7,
        description='Assessment coverage by geographic area',
        tags=['cross_domain', 'communities', 'mana', 'coverage']
    ),
    QueryTemplate(
        id='communities_priority_needs',
        category='cross_domain',
        pattern=r'\bcommunities\s+with\s+(critical|high priority|priority)\s+needs',
        query_template='OBCCommunity.objects.filter(assessments__identified_needs__priority__in=["high", "critical"]).distinct().annotate(priority_needs_count=Count("assessments__identified_needs", filter=Q(assessments__identified_needs__priority__in=["high", "critical"]))).order_by("-priority_needs_count").select_related("barangay")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Communities with critical needs',
            'High priority needs by community',
            'Priority needs communities',
            'Communities needing urgent support'
        ],
        priority=8,
        description='Communities with high-priority needs',
        tags=['cross_domain', 'communities', 'mana', 'priority']
    ),
    QueryTemplate(
        id='assessment_participation_rate',
        category='cross_domain',
        pattern=r'\b(community participation|participation rate)\s+in\s+assessments?',
        query_template='Assessment.objects.values("community__name").annotate(participant_count=Count("participants")).order_by("-participant_count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Community participation in assessments',
            'Participation rate by assessment',
            'Engagement in assessments',
            'Community involvement tracking'
        ],
        priority=7,
        description='Community participation in assessments',
        tags=['cross_domain', 'communities', 'mana', 'participation']
    ),
    QueryTemplate(
        id='communities_assessment_gap',
        category='cross_domain',
        pattern=r'\b(time since|gap|last assessment)\s+(last assessment|by community)',
        query_template='OBCCommunity.objects.annotate(last_assessment=Max("assessments__created_at"), days_since=timezone.now() - Max("assessments__created_at")).filter(last_assessment__isnull=False).order_by("-days_since").select_related("barangay")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Time since last assessment',
            'Assessment gap by community',
            'Days since last assessment',
            'Communities needing reassessment'
        ],
        priority=7,
        description='Time since last assessment per community',
        tags=['cross_domain', 'communities', 'mana', 'gap']
    ),
]


# =============================================================================
# MANA + COORDINATION QUERIES (10 templates)
# =============================================================================

CROSS_DOMAIN_MANA_COORDINATION_TEMPLATES = [
    QueryTemplate(
        id='partnerships_supporting_assessments',
        category='cross_domain',
        pattern=r'\bpartnerships?\s+(supporting|linked to|for)\s+assessments?',
        query_template='Partnership.objects.filter(related_assessments__isnull=False).distinct().prefetch_related("partners", "related_assessments")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Partnerships supporting assessments',
            'Partnerships linked to assessments',
            'Assessment partnerships',
            'Which partnerships support assessments?'
        ],
        priority=7,
        description='Partnerships supporting assessments',
        tags=['cross_domain', 'mana', 'coordination', 'partnerships']
    ),
    QueryTemplate(
        id='stakeholder_engagement_in_workshops',
        category='cross_domain',
        pattern=r'\bstakeholders?\s+(in|participating in)\s+(mana\s+)?(workshops?|assessments?)',
        query_template='StakeholderOrganization.objects.filter(engagements__related_assessment__isnull=False).distinct().annotate(workshop_count=Count("engagements", filter=Q(engagements__engagement_type="workshop"))).order_by("-workshop_count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Stakeholders in MANA workshops',
            'Stakeholders participating in assessments',
            'Workshop participants',
            'Who attends MANA workshops?'
        ],
        priority=7,
        description='Stakeholders engaged in MANA activities',
        tags=['cross_domain', 'mana', 'coordination', 'stakeholders']
    ),
    QueryTemplate(
        id='moa_assessment_leadership',
        category='cross_domain',
        pattern=r'\b(moa|ministry|agency)\s+(leading|conducting)\s+assessments?',
        query_template='StakeholderOrganization.objects.filter(organization_type__in=["government", "moa"]).annotate(assessment_count=Count("led_assessments")).filter(assessment_count__gt=0).order_by("-assessment_count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'MOAs leading assessments',
            'Ministries conducting assessments',
            'Agencies leading MANA',
            'Government assessment leadership'
        ],
        priority=7,
        description='MOAs leading assessments',
        tags=['cross_domain', 'mana', 'coordination', 'moa']
    ),
    QueryTemplate(
        id='coordination_to_assessment',
        category='cross_domain',
        pattern=r'\b(engagements?\s+to\s+assessments?|coordination to assessment)',
        query_template='StakeholderEngagement.objects.filter(related_assessment__isnull=False).values("engagement_type").annotate(assessment_count=Count("related_assessment", distinct=True)).order_by("-assessment_count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Engagements to assessments',
            'Coordination to assessment flow',
            'Meetings leading to assessments',
            'Engagement assessment linkage'
        ],
        priority=7,
        description='Engagements linked to assessments',
        tags=['cross_domain', 'mana', 'coordination', 'pipeline']
    ),
    QueryTemplate(
        id='assessment_stakeholder_count',
        category='cross_domain',
        pattern=r'\b(stakeholder\s+)?(participation|count)\s+(by|in)\s+assessment',
        query_template='Assessment.objects.annotate(stakeholder_count=Count("participating_organizations")).order_by("-stakeholder_count").select_related("lead_organization")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Stakeholder participation by assessment',
            'Count stakeholders per assessment',
            'Assessment participation levels',
            'How many stakeholders per assessment?'
        ],
        priority=7,
        description='Stakeholder count per assessment',
        tags=['cross_domain', 'mana', 'coordination', 'count']
    ),
    QueryTemplate(
        id='multi_stakeholder_assessments',
        category='cross_domain',
        pattern=r'\bassessments?\s+with\s+(3\+|\d+\+|multiple)\s+(stakeholders?|organizations?)',
        query_template='Assessment.objects.annotate(org_count=Count("participating_organizations")).filter(org_count__gte={min_count}).order_by("-org_count").prefetch_related("participating_organizations")',
        required_entities=[],
        optional_entities=['number'],
        examples=[
            'Assessments with 3+ organizations',
            'Multi-stakeholder assessments',
            'Assessments with multiple partners',
            'Collaborative assessments'
        ],
        priority=7,
        description='Assessments with multiple stakeholders',
        tags=['cross_domain', 'mana', 'coordination', 'multi']
    ),
    QueryTemplate(
        id='assessment_facilitators',
        category='cross_domain',
        pattern=r'\b(staff|facilitators?)\s+(facilitating|leading)\s+assessments?',
        query_template='User.objects.filter(facilitated_assessments__isnull=False).annotate(assessment_count=Count("facilitated_assessments")).filter(assessment_count__gt=0).order_by("-assessment_count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Staff facilitating assessments',
            'Assessment facilitators',
            'Who leads assessments?',
            'Staff assessment workload'
        ],
        priority=7,
        description='Staff members facilitating assessments',
        tags=['cross_domain', 'mana', 'coordination', 'staff']
    ),
    QueryTemplate(
        id='engagement_assessment_linkage',
        category='cross_domain',
        pattern=r'\b(engagements?\s+linked|related engagements?)\s+to\s+assessments?',
        query_template='StakeholderEngagement.objects.filter(related_assessment__isnull=False).select_related("related_assessment", "lead_organization").order_by("-engagement_date")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Engagements linked to assessments',
            'Related engagements to assessments',
            'Show engagement-assessment links',
            'Coordination supporting assessments'
        ],
        priority=7,
        description='Engagements linked to assessments',
        tags=['cross_domain', 'mana', 'coordination', 'linkage']
    ),
    QueryTemplate(
        id='partnership_assessment_support',
        category='cross_domain',
        pattern=r'\bpartnerships?\s+supporting\s+mana',
        query_template='Partnership.objects.filter(focus_areas__icontains="mana").prefetch_related("partners").annotate(assessment_count=Count("related_assessments")).order_by("-assessment_count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Partnerships supporting MANA',
            'MANA partnerships',
            'Partnerships for assessments',
            'Collaborative MANA support'
        ],
        priority=7,
        description='Partnerships supporting MANA activities',
        tags=['cross_domain', 'mana', 'coordination', 'support']
    ),
    QueryTemplate(
        id='stakeholder_assessment_coverage',
        category='cross_domain',
        pattern=r'\bstakeholder\s+coverage\s+across\s+assessments?',
        query_template='StakeholderOrganization.objects.annotate(assessment_count=Count("participated_assessments")).filter(assessment_count__gt=0).order_by("-assessment_count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Stakeholder coverage across assessments',
            'Stakeholder assessment participation',
            'Which stakeholders are most involved?',
            'Assessment engagement by stakeholder'
        ],
        priority=7,
        description='Stakeholder participation across assessments',
        tags=['cross_domain', 'mana', 'coordination', 'coverage']
    ),
]


# =============================================================================
# NEEDS → POLICIES → PROJECTS PIPELINE (15 templates) - CRITICAL
# =============================================================================

CROSS_DOMAIN_PIPELINE_TEMPLATES = [
    QueryTemplate(
        id='needs_to_ppas_pipeline',
        category='cross_domain',
        pattern=r'\b(needs?\s+to\s+(ppas?|projects?)(\s+addressing\s+them)?|needs?\s+(pipeline|flow))',
        query_template='Need.objects.annotate(ppa_count=Count("addressing_ppas")).values("sector", "ppa_count").order_by("-ppa_count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Needs to PPAs pipeline',
            'Needs to projects addressing them',
            'Needs flow to PPAs',
            'Track needs to implementation'
        ],
        priority=9,
        description='Needs and PPAs addressing them',
        tags=['cross_domain', 'pipeline', 'needs', 'ppas', 'critical']
    ),
    QueryTemplate(
        id='needs_without_ppas',
        category='cross_domain',
        pattern=r'\b(needs?\s+without|unaddressed\s+needs?|needs?\s+lacking)\s*(ppas?|projects?|implementation)?',
        query_template='Need.objects.filter(addressing_ppas__isnull=True, status__in=["identified", "validated"]).select_related("assessment__community").order_by("-priority", "-created_at")',
        required_entities=[],
        optional_entities=['sector', 'priority'],
        examples=[
            'Needs without PPAs',
            'Unaddressed needs',
            'Needs lacking implementation',
            'Which needs have no projects?'
        ],
        priority=9,
        description='Unaddressed needs without PPAs',
        tags=['cross_domain', 'pipeline', 'needs', 'gaps', 'critical']
    ),
    QueryTemplate(
        id='needs_with_budget',
        category='cross_domain',
        pattern=r'\bneeds?\s+with\s+(budget|funding)\s+(allocated|assigned)',
        query_template='Need.objects.filter(addressing_ppas__actual_budget__gt=0).distinct().annotate(total_budget=Sum("addressing_ppas__actual_budget")).order_by("-total_budget").select_related("assessment")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Needs with budget allocated',
            'Funded needs',
            'Needs with funding assigned',
            'Which needs have budget?'
        ],
        priority=8,
        description='Needs with budget allocation',
        tags=['cross_domain', 'pipeline', 'needs', 'budget']
    ),
    QueryTemplate(
        id='policies_implementing_needs',
        category='cross_domain',
        pattern=r'\b(policies?|recommendations?)\s+(addressing|implementing)\s+needs?',
        query_template='PolicyRecommendation.objects.filter(related_needs__isnull=False).distinct().prefetch_related("related_needs").annotate(needs_count=Count("related_needs")).order_by("-needs_count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Policies addressing needs',
            'Recommendations implementing needs',
            'Policies for identified needs',
            'Policy-needs linkage'
        ],
        priority=8,
        description='Policies addressing identified needs',
        tags=['cross_domain', 'pipeline', 'policies', 'needs']
    ),
    QueryTemplate(
        id='ppas_addressing_needs',
        category='cross_domain',
        pattern=r'\bppas?\s+(addressing|implementing|for)\s+needs?',
        query_template='MonitoringEntry.objects.filter(addresses_needs__isnull=False).distinct().prefetch_related("addresses_needs").annotate(needs_count=Count("addresses_needs")).order_by("-needs_count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'PPAs addressing needs',
            'Projects implementing needs',
            'PPAs for identified needs',
            'Implementation of needs'
        ],
        priority=8,
        description='PPAs addressing identified needs',
        tags=['cross_domain', 'pipeline', 'ppas', 'needs']
    ),
    QueryTemplate(
        id='needs_policy_ppa_flow',
        category='cross_domain',
        pattern=r'\b(complete flow|needs?\s+to\s+policies?\s+to\s+ppas?|full pipeline)',
        query_template='Need.objects.annotate(policy_count=Count("related_policies"), ppa_count=Count("addressing_ppas")).values("sector").annotate(needs_total=Count("id"), needs_with_policy=Count("id", filter=Q(policy_count__gt=0)), needs_with_ppa=Count("id", filter=Q(ppa_count__gt=0)))',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Complete flow: Needs to Policies to PPAs',
            'Full pipeline tracking',
            'Needs policy PPA flow',
            'Track complete implementation chain'
        ],
        priority=9,
        description='Complete needs-policies-PPAs pipeline',
        tags=['cross_domain', 'pipeline', 'needs', 'policies', 'ppas', 'critical']
    ),
    QueryTemplate(
        id='unfunded_needs_analysis',
        category='cross_domain',
        pattern=r'\b(unfunded|high.?priority.*without|critical.*no)\s+(budget|funding|ppas?)',
        query_template='Need.objects.filter(priority__in=["high", "critical"], addressing_ppas__isnull=True).select_related("assessment__community").order_by("-priority", "sector")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'High-priority needs without funding',
            'Critical needs lacking PPAs',
            'Unfunded priority needs',
            'High priority gaps'
        ],
        priority=9,
        description='High-priority unfunded needs',
        tags=['cross_domain', 'pipeline', 'needs', 'gaps', 'critical']
    ),
    QueryTemplate(
        id='needs_coverage_by_sector',
        category='cross_domain',
        pattern=r'\bneeds?\s+(coverage|addressed|met)\s+(vs|versus)?\s*(unmet)?\s+by\s+sector',
        query_template='Need.objects.values("sector").annotate(total_needs=Count("id"), addressed_needs=Count("id", filter=Q(addressing_ppas__isnull=False)), unmet_needs=Count("id", filter=Q(addressing_ppas__isnull=True)), coverage_rate=100.0 * Count("id", filter=Q(addressing_ppas__isnull=False)) / Count("id")).order_by("-coverage_rate")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Needs addressed vs unmet by sector',
            'Needs coverage by sector',
            'Sector-wise needs status',
            'Implementation rate by sector'
        ],
        priority=8,
        description='Needs coverage by sector',
        tags=['cross_domain', 'pipeline', 'needs', 'sector', 'coverage']
    ),
    QueryTemplate(
        id='policy_to_ppa_conversion_rate',
        category='cross_domain',
        pattern=r'\bpolic(y|ies)\s+implementation\s+rate',
        query_template='PolicyRecommendation.objects.values("status").annotate(total=Count("id"), with_ppas=Count("id", filter=Q(implementing_ppas__isnull=False))).annotate(implementation_rate=100.0 * F("with_ppas") / F("total"))',
        required_entities=[],
        optional_entities=[],
        examples=[
            '% of policies with implementing PPAs',
            'Policy implementation rate',
            'How many policies are implemented?',
            'Policy to action conversion'
        ],
        priority=8,
        description='Policy implementation rate based on implementing PPAs',
        tags=['cross_domain', 'pipeline', 'policies', 'rate']
    ),
    QueryTemplate(
        id='needs_with_multiple_ppas',
        category='cross_domain',
        pattern=r'\bneeds?\s+(addressed by|with)\s+multiple\s+ppas?',
        query_template='Need.objects.annotate(ppa_count=Count("addressing_ppas")).filter(ppa_count__gte=2).order_by("-ppa_count").select_related("assessment")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Needs addressed by multiple PPAs',
            'Needs with multiple projects',
            'Multi-PPA needs',
            'Comprehensive need addressing'
        ],
        priority=7,
        description='Needs with multiple PPAs',
        tags=['cross_domain', 'pipeline', 'needs', 'multiple']
    ),
    QueryTemplate(
        id='ppas_by_needs_addressed',
        category='cross_domain',
        pattern=r'\bppas?\s+(ranked by|by)\s+needs?\s+addressed',
        query_template='MonitoringEntry.objects.annotate(needs_count=Count("addresses_needs")).filter(needs_count__gt=0).order_by("-needs_count").select_related("implementing_moa")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'PPAs ranked by needs addressed count',
            'Projects by needs addressed',
            'Most impactful PPAs',
            'PPAs addressing most needs'
        ],
        priority=7,
        description='PPAs ranked by needs addressed',
        tags=['cross_domain', 'pipeline', 'ppas', 'ranking']
    ),
    QueryTemplate(
        id='needs_budget_allocation',
        category='cross_domain',
        pattern=r'\bbudget\s+allocated\s+to\s+needs?\s+by\s+sector',
        query_template='Need.objects.filter(addressing_ppas__actual_budget__gt=0).values("sector").annotate(total_budget=Sum("addressing_ppas__actual_budget"), needs_count=Count("id", distinct=True)).order_by("-total_budget")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Budget allocated to needs by sector',
            'Funding by sector for needs',
            'Sector budget allocation',
            'How much budget per sector?'
        ],
        priority=8,
        description='Budget allocation to needs by sector',
        tags=['cross_domain', 'pipeline', 'needs', 'budget', 'sector']
    ),
    QueryTemplate(
        id='evidence_based_budgeting',
        category='cross_domain',
        pattern=r'\b(evidence.?based|assessment to budget|needs to funding)\s+(budgeting|flow)',
        query_template='Assessment.objects.annotate(needs_count=Count("identified_needs"), funded_needs=Count("identified_needs", filter=Q(identified_needs__addressing_ppas__actual_budget__gt=0))).aggregate(total_needs=Sum("needs_count"), total_funded=Sum("funded_needs"), funding_rate=100.0 * Sum("funded_needs") / Sum("needs_count"))',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Assessment to needs to budget flow',
            'Evidence-based budgeting',
            'Needs to funding conversion',
            'Data-driven budget allocation'
        ],
        priority=8,
        description='Evidence-based budgeting flow',
        tags=['cross_domain', 'pipeline', 'budget', 'evidence']
    ),
    QueryTemplate(
        id='needs_implementation_gap',
        category='cross_domain',
        pattern=r'\b(time from need|gap|lag)\s+(identification to|to)\s+(ppa|implementation)',
        query_template='Need.objects.filter(addressing_ppas__isnull=False).annotate(gap_days=(Min("addressing_ppas__start_date") - F("created_at")).days).order_by("-gap_days")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Time from need identification to PPA start',
            'Gap between need and implementation',
            'Implementation lag analysis',
            'How long from need to action?'
        ],
        priority=7,
        description='Time gap from need to implementation',
        tags=['cross_domain', 'pipeline', 'needs', 'gap']
    ),
    QueryTemplate(
        id='cross_sector_needs_analysis',
        category='cross_domain',
        pattern=r'\b(cross.?sector|multi.?sector|needs?\s+spanning)\s+needs?',
        query_template='Need.objects.filter(addressing_ppas__isnull=False).annotate(ppa_sectors=ArrayAgg("addressing_ppas__sector", distinct=True), sector_count=Count("addressing_ppas__sector", distinct=True)).filter(sector_count__gte=2).order_by("-sector_count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Needs spanning multiple sectors',
            'Cross-sector needs analysis',
            'Multi-sector needs',
            'Needs requiring coordination'
        ],
        priority=7,
        description='Needs addressed by multiple sectors',
        tags=['cross_domain', 'pipeline', 'needs', 'cross_sector']
    ),
]


# =============================================================================
# COMBINE ALL CROSS-DOMAIN TEMPLATES
# =============================================================================

CROSS_DOMAIN_TEMPLATES = (
    CROSS_DOMAIN_COMMUNITIES_MANA_TEMPLATES +
    CROSS_DOMAIN_MANA_COORDINATION_TEMPLATES +
    CROSS_DOMAIN_PIPELINE_TEMPLATES
)

# Total: 15 + 10 + 15 = 40 cross-domain query templates
