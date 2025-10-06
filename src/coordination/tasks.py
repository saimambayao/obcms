"""
Celery Tasks for Coordination AI Services

Background tasks for AI-powered stakeholder matching, partnership analysis,
and meeting intelligence.
"""

from celery import shared_task
from django.core.cache import cache
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(name='coordination.analyze_meeting')
def analyze_meeting(meeting_id: str):
    """
    Background task: Analyze meeting and create tasks

    Args:
        meeting_id: UUID of StakeholderEngagement

    Returns:
        dict with summary and tasks created
    """
    from coordination.ai_services.meeting_intelligence import MeetingIntelligence

    try:
        service = MeetingIntelligence()

        # Generate summary
        summary = service.summarize_meeting(meeting_id)

        # Auto-create tasks from action items
        tasks = service.auto_create_tasks(meeting_id)

        # Cache results for 7 days
        cache.set(f'meeting_summary_{meeting_id}', summary, timeout=86400 * 7)

        logger.info(f"Meeting {meeting_id} analyzed: {len(tasks)} tasks created")

        return {
            'meeting_id': meeting_id,
            'summary': summary,
            'tasks_created': len(tasks),
            'task_ids': [str(task.id) for task in tasks]
        }

    except Exception as e:
        logger.error(f"Error analyzing meeting {meeting_id}: {str(e)}")
        return {'error': str(e), 'meeting_id': meeting_id}


@shared_task(name='coordination.match_stakeholders_for_communities')
def match_stakeholders_for_communities():
    """
    Nightly task: Pre-compute stakeholder matches for all active communities

    This task runs nightly to pre-compute and cache stakeholder matches,
    ensuring instant results when users access the matching feature.
    """
    from communities.models import BarangayOBC
    from coordination.ai_services.stakeholder_matcher import StakeholderMatcher

    matcher = StakeholderMatcher()

    # Get active communities
    communities = BarangayOBC.objects.filter(
        is_active=True
    ).select_related('municipality__province__region')

    # Need categories to match
    need_categories = [
        'Health',
        'Education',
        'Livelihood',
        'Infrastructure',
        'Agriculture',
        'Water and Sanitation',
        'Social Services'
    ]

    results = {
        'communities_processed': 0,
        'matches_generated': 0,
        'errors': []
    }

    for community in communities:
        try:
            for need in need_categories:
                matches = matcher.find_matching_stakeholders(
                    community.id,
                    need,
                    top_k=10,
                    min_score=0.6
                )

                # Cache results for 24 hours
                cache_key = f"stakeholder_matches_{community.id}_{need}"
                cache.set(cache_key, matches, timeout=86400)

                results['matches_generated'] += len(matches)

            results['communities_processed'] += 1

        except Exception as e:
            logger.error(f"Error matching stakeholders for community {community.id}: {str(e)}")
            results['errors'].append({
                'community_id': community.id,
                'error': str(e)
            })

    logger.info(f"Stakeholder matching complete: {results['communities_processed']} communities, "
                f"{results['matches_generated']} matches")

    return results


@shared_task(name='coordination.analyze_partnership_portfolio')
def analyze_partnership_portfolio(organization_id: str):
    """
    Background task: Analyze organization's partnership portfolio

    Args:
        organization_id: UUID of Organization

    Returns:
        Portfolio analysis results
    """
    from coordination.ai_services.partnership_predictor import PartnershipPredictor

    try:
        predictor = PartnershipPredictor()
        analysis = predictor.analyze_partnership_portfolio(organization_id)

        # Cache results for 7 days
        cache.set(f'portfolio_analysis_{organization_id}', analysis, timeout=86400 * 7)

        logger.info(f"Portfolio analyzed for organization {organization_id}")

        return analysis

    except Exception as e:
        logger.error(f"Error analyzing portfolio for {organization_id}: {str(e)}")
        return {'error': str(e), 'organization_id': organization_id}


@shared_task(name='coordination.predict_partnership_success')
def predict_partnership_success(stakeholder_id: str, community_id: int, project_type: str):
    """
    Background task: Predict partnership success

    Args:
        stakeholder_id: Organization UUID
        community_id: Community ID
        project_type: Type of project

    Returns:
        Success prediction
    """
    from coordination.ai_services.partnership_predictor import PartnershipPredictor

    try:
        predictor = PartnershipPredictor()
        prediction = predictor.predict_success(
            stakeholder_id,
            community_id,
            project_type
        )

        # Cache results for 7 days
        cache_key = f"partnership_prediction_{stakeholder_id}_{community_id}_{project_type}"
        cache.set(cache_key, prediction, timeout=86400 * 7)

        logger.info(f"Partnership prediction for {stakeholder_id} + {community_id}: "
                   f"{prediction.get('success_probability', 0):.2f}")

        return prediction

    except Exception as e:
        logger.error(f"Error predicting partnership success: {str(e)}")
        return {'error': str(e)}


@shared_task(name='coordination.optimize_budget_allocation')
def optimize_budget_allocation(total_budget: float, community_ids: list):
    """
    Background task: Optimize budget allocation across communities

    Args:
        total_budget: Total available budget
        community_ids: List of community IDs

    Returns:
        Optimized allocation plan
    """
    from decimal import Decimal
    from coordination.ai_services.resource_optimizer import ResourceOptimizer

    try:
        optimizer = ResourceOptimizer()
        allocation = optimizer.optimize_budget_allocation(
            Decimal(str(total_budget)),
            community_ids
        )

        # Cache results for 3 days
        cache_key = f"budget_allocation_{hash(tuple(community_ids))}"
        cache.set(cache_key, allocation, timeout=86400 * 3)

        logger.info(f"Budget allocation optimized: {len(community_ids)} communities, "
                   f"₱{total_budget:,.2f} total")

        return allocation

    except Exception as e:
        logger.error(f"Error optimizing budget allocation: {str(e)}")
        return {'error': str(e)}


@shared_task(name='coordination.generate_meeting_reports')
def generate_meeting_reports(start_date: str, end_date: str):
    """
    Background task: Generate meeting reports for a date range

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        Report generation results
    """
    from datetime import datetime
    from coordination.models import StakeholderEngagement
    from coordination.ai_services.meeting_intelligence import MeetingIntelligence

    try:
        service = MeetingIntelligence()

        # Get meetings in date range
        meetings = StakeholderEngagement.objects.filter(
            planned_date__range=[start_date, end_date],
            status='completed'
        )

        reports = []
        for meeting in meetings:
            try:
                report = service.generate_meeting_report(str(meeting.id))
                reports.append({
                    'meeting_id': str(meeting.id),
                    'meeting_title': meeting.title,
                    'report': report
                })
            except Exception as e:
                logger.error(f"Error generating report for meeting {meeting.id}: {str(e)}")

        logger.info(f"Generated {len(reports)} meeting reports for {start_date} to {end_date}")

        return {
            'reports_generated': len(reports),
            'reports': reports
        }

    except Exception as e:
        logger.error(f"Error generating meeting reports: {str(e)}")
        return {'error': str(e)}


@shared_task(name='coordination.update_resource_utilization')
def update_resource_utilization():
    """
    Daily task: Update resource utilization metrics for all active organizations
    """
    from coordination.models import Organization
    from coordination.ai_services.resource_optimizer import ResourceOptimizer

    optimizer = ResourceOptimizer()

    # Get active organizations with partnerships
    organizations = Organization.objects.filter(
        is_active=True,
        partnerships__isnull=False
    ).distinct()

    results = {
        'organizations_processed': 0,
        'high_utilization': [],
        'low_utilization': [],
        'errors': []
    }

    for org in organizations:
        try:
            analysis = optimizer.analyze_resource_utilization(str(org.id))

            # Cache results
            cache.set(
                f'resource_utilization_{org.id}',
                analysis,
                timeout=86400
            )

            # Track utilization levels
            if analysis['capacity_status'] == 'overextended':
                results['high_utilization'].append(org.name)
            elif analysis['capacity_status'] == 'underutilized':
                results['low_utilization'].append(org.name)

            results['organizations_processed'] += 1

        except Exception as e:
            logger.error(f"Error analyzing resource utilization for {org.id}: {str(e)}")
            results['errors'].append({
                'organization_id': str(org.id),
                'error': str(e)
            })

    logger.info(f"Resource utilization updated for {results['organizations_processed']} organizations")

    return results


@shared_task(name='coordination.send_partnership_alerts')
def send_partnership_alerts():
    """
    Daily task: Send alerts for partnerships requiring attention
    """
    from datetime import timedelta
    from coordination.models import Partnership
    from django.core.mail import send_mail
    from django.contrib.auth import get_user_model

    User = get_user_model()

    # Get partnerships requiring attention
    today = timezone.now().date()
    warning_date = today + timedelta(days=30)

    # Partnerships expiring soon
    expiring_soon = Partnership.objects.filter(
        status='active',
        end_date__lte=warning_date,
        end_date__gte=today
    ).select_related('focal_person', 'lead_organization')

    # Partnerships with overdue milestones
    from coordination.models import PartnershipMilestone
    overdue_milestones = PartnershipMilestone.objects.filter(
        status__in=['planned', 'in_progress'],
        due_date__lt=today
    ).select_related('partnership__focal_person')

    alerts_sent = 0

    # Alert for expiring partnerships
    for partnership in expiring_soon:
        if partnership.focal_person and partnership.focal_person.email:
            days_until_expiry = (partnership.end_date - today).days
            send_mail(
                subject=f'Partnership Expiring Soon: {partnership.title}',
                message=f"""
Dear {partnership.focal_person.get_full_name()},

The partnership "{partnership.title}" will expire in {days_until_expiry} days on {partnership.end_date}.

Please review and take necessary action for renewal or closure.

Partnership Details:
- Lead Organization: {partnership.lead_organization.name}
- Start Date: {partnership.start_date}
- End Date: {partnership.end_date}

View partnership: http://yourdomain.com/coordination/partnerships/{partnership.id}/

Best regards,
OBCMS System
                """,
                from_email='noreply@oobc.gov.ph',
                recipient_list=[partnership.focal_person.email],
                fail_silently=True
            )
            alerts_sent += 1

    # Alert for overdue milestones (grouped by partnership)
    milestone_alerts = {}
    for milestone in overdue_milestones:
        partnership = milestone.partnership
        if partnership.focal_person:
            if partnership.id not in milestone_alerts:
                milestone_alerts[partnership.id] = {
                    'partnership': partnership,
                    'milestones': []
                }
            milestone_alerts[partnership.id]['milestones'].append(milestone)

    for data in milestone_alerts.values():
        partnership = data['partnership']
        milestones = data['milestones']

        if partnership.focal_person and partnership.focal_person.email:
            milestone_list = '\n'.join([
                f"- {m.title} (Due: {m.due_date})"
                for m in milestones
            ])

            send_mail(
                subject=f'Overdue Milestones: {partnership.title}',
                message=f"""
Dear {partnership.focal_person.get_full_name()},

The following milestones for "{partnership.title}" are overdue:

{milestone_list}

Please review and update the status or adjust timelines.

View partnership: http://yourdomain.com/coordination/partnerships/{partnership.id}/

Best regards,
OBCMS System
                """,
                from_email='noreply@oobc.gov.ph',
                recipient_list=[partnership.focal_person.email],
                fail_silently=True
            )
            alerts_sent += 1

    logger.info(f"Sent {alerts_sent} partnership alerts")

    return {
        'alerts_sent': alerts_sent,
        'expiring_partnerships': expiring_soon.count(),
        'overdue_milestones': overdue_milestones.count()
    }
