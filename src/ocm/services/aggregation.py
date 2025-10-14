"""
OCM Aggregation Service

Service for aggregating data across all MOAs for OCM dashboard.
Provides caching, query optimization, and consolidated views.
"""
import logging
from datetime import datetime
from decimal import Decimal

from django.core.cache import cache
from django.db.models import Count, Q, Sum
from django.utils import timezone

logger = logging.getLogger(__name__)

# Cache TTL: 15 minutes
CACHE_TTL = 900


class OCMAggregationService:
    """
    Service class for aggregating data across all MOAs.
    
    Features:
    - Organization statistics
    - Budget aggregation
    - Planning status
    - Coordination metrics
    - Performance analytics
    - 15-minute caching
    """
    
    @staticmethod
    def get_organization_count():
        """
        Get count of active organizations (MOAs).
        
        Excludes OOBC and OCM from count.
        Cached for 15 minutes.
        
        Returns:
            int: Number of active MOAs
        """
        cache_key = 'ocm:org_count'
        count = cache.get(cache_key)
        
        if count is None:
            try:
                from organizations.models import Organization
                
                count = Organization.objects.filter(
                    is_active=True
                ).exclude(
                    code__in=['OOBC', 'OCM']
                ).count()
                
                cache.set(cache_key, count, CACHE_TTL)
                logger.debug(f"Cached organization count: {count}")
            except Exception as e:
                logger.error(f"Error getting organization count: {e}")
                count = 0
        
        return count
    
    @staticmethod
    def get_all_organizations():
        """
        Get all active organizations.
        
        Returns:
            list: List of dicts with code, name, org_type
        """
        cache_key = 'ocm:all_orgs'
        orgs = cache.get(cache_key)
        
        if orgs is None:
            try:
                from organizations.models import Organization
                
                orgs = list(Organization.objects.filter(
                    is_active=True
                ).exclude(
                    code__in=['OOBC', 'OCM']
                ).values('code', 'name', 'org_type').order_by('name'))
                
                cache.set(cache_key, orgs, CACHE_TTL)
                logger.debug(f"Cached {len(orgs)} organizations")
            except Exception as e:
                logger.error(f"Error getting organizations: {e}")
                orgs = []
        
        return orgs
    
    @staticmethod
    def get_government_stats():
        """
        Get high-level government statistics.
        
        Returns:
            dict: Government-wide statistics including:
                - moa_count: Number of active MOAs
                - total_budget: Total budget across all MOAs
                - total_plans: Total strategic/annual plans
                - total_partnerships: Total inter-MOA partnerships
        """
        cache_key = 'ocm:gov_stats'
        stats = cache.get(cache_key)
        
        if stats is None:
            try:
                from organizations.models import Organization
                
                moa_count = Organization.objects.filter(
                    is_active=True
                ).exclude(
                    code__in=['OOBC', 'OCM']
                ).count()
                
                # Get budget data
                total_budget = OCMAggregationService._get_total_budget()
                
                # Get planning data
                total_plans = OCMAggregationService._get_total_plans()
                
                # Get coordination data
                total_partnerships = OCMAggregationService._get_total_partnerships()
                
                stats = {
                    'moa_count': moa_count,
                    'total_budget': total_budget,
                    'total_plans': total_plans,
                    'total_partnerships': total_partnerships,
                }
                
                cache.set(cache_key, stats, CACHE_TTL)
                logger.debug(f"Cached government stats: {stats}")
            except Exception as e:
                logger.error(f"Error getting government stats: {e}")
                stats = {
                    'moa_count': 0,
                    'total_budget': Decimal('0'),
                    'total_plans': 0,
                    'total_partnerships': 0,
                }
        
        return stats
    
    @staticmethod
    def _get_total_budget():
        """Get total budget across all MOAs"""
        try:
            from budget_preparation.models import BudgetProposal
            
            result = BudgetProposal.objects.filter(
                status='approved'
            ).aggregate(
                total=Sum('total_amount')
            )
            
            return result.get('total') or Decimal('0')
        except Exception as e:
            logger.warning(f"Error getting total budget: {e}")
            return Decimal('0')
    
    @staticmethod
    def _get_total_plans():
        """Get total strategic and annual plans"""
        try:
            from planning.models import StrategicPlan, AnnualWorkPlan
            
            strategic_count = StrategicPlan.objects.filter(is_active=True).count()
            annual_count = AnnualWorkPlan.objects.filter(is_active=True).count()
            
            return strategic_count + annual_count
        except Exception as e:
            logger.warning(f"Error getting total plans: {e}")
            return 0
    
    @staticmethod
    def _get_total_partnerships():
        """Get total inter-MOA partnerships"""
        try:
            from coordination.models import InterMOAPartnership
            
            return InterMOAPartnership.objects.filter(is_active=True).count()
        except Exception as e:
            logger.warning(f"Error getting total partnerships: {e}")
            return 0
    
    @staticmethod
    def get_consolidated_budget(fiscal_year=None):
        """
        Get consolidated budget across all MOAs.
        
        Args:
            fiscal_year (int, optional): Filter by fiscal year
        
        Returns:
            list: List of dicts with organization budget data
        """
        cache_key = f'ocm:budget:consolidated:{fiscal_year or "all"}'
        data = cache.get(cache_key)
        
        if data is None:
            try:
                from budget_preparation.models import BudgetProposal
                from budget_execution.models import BudgetAllotment, Disbursement
                
                queryset = BudgetProposal.objects.select_related('organization')
                
                if fiscal_year:
                    queryset = queryset.filter(fiscal_year=fiscal_year)
                
                # Aggregate by organization
                budget_data = queryset.values(
                    'organization__name',
                    'organization__code'
                ).annotate(
                    total_proposed=Sum('total_amount'),
                    total_approved=Sum('total_amount', filter=Q(status='approved'))
                )
                
                data = []
                for item in budget_data:
                    org_code = item['organization__code']
                    
                    # Get allocated amount
                    allocated = BudgetAllotment.objects.filter(
                        organization__code=org_code
                    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
                    
                    # Get disbursed amount
                    disbursed = Disbursement.objects.filter(
                        allotment__organization__code=org_code
                    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
                    
                    # Calculate utilization rate
                    utilization_rate = 0
                    if allocated > 0:
                        utilization_rate = float((disbursed / allocated) * 100)
                    
                    data.append({
                        'organization': item['organization__name'],
                        'organization_code': org_code,
                        'proposed': item['total_proposed'] or Decimal('0'),
                        'approved': item['total_approved'] or Decimal('0'),
                        'allocated': allocated,
                        'disbursed': disbursed,
                        'utilization_rate': round(utilization_rate, 2)
                    })
                
                cache.set(cache_key, data, CACHE_TTL)
                logger.debug(f"Cached consolidated budget: {len(data)} organizations")
            except Exception as e:
                logger.error(f"Error getting consolidated budget: {e}")
                data = []
        
        return data
    
    @staticmethod
    def get_budget_summary(fiscal_year=None):
        """
        Get budget summary statistics.
        
        Args:
            fiscal_year (int, optional): Filter by fiscal year
        
        Returns:
            dict: Budget summary with total_proposed, total_approved, approval_rate
        """
        cache_key = f'ocm:budget:summary:{fiscal_year or "all"}'
        summary = cache.get(cache_key)
        
        if summary is None:
            try:
                from budget_preparation.models import BudgetProposal
                
                queryset = BudgetProposal.objects.all()
                
                if fiscal_year:
                    queryset = queryset.filter(fiscal_year=fiscal_year)
                
                result = queryset.aggregate(
                    total_proposed=Sum('total_amount'),
                    total_approved=Sum('total_amount', filter=Q(status='approved'))
                )
                
                total_proposed = result.get('total_proposed') or Decimal('0')
                total_approved = result.get('total_approved') or Decimal('0')
                
                approval_rate = 0
                if total_proposed > 0:
                    approval_rate = float((total_approved / total_proposed) * 100)
                
                summary = {
                    'total_proposed': total_proposed,
                    'total_approved': total_approved,
                    'approval_rate': round(approval_rate, 2)
                }
                
                cache.set(cache_key, summary, CACHE_TTL)
                logger.debug(f"Cached budget summary: {summary}")
            except Exception as e:
                logger.error(f"Error getting budget summary: {e}")
                summary = {
                    'total_proposed': Decimal('0'),
                    'total_approved': Decimal('0'),
                    'approval_rate': 0
                }
        
        return summary
    
    @staticmethod
    def get_strategic_planning_status():
        """
        Get strategic planning status across all MOAs.
        
        Returns:
            dict: Planning status with counts by organization
        """
        cache_key = 'ocm:planning:status'
        data = cache.get(cache_key)
        
        if data is None:
            try:
                from planning.models import StrategicPlan, AnnualWorkPlan
                from organizations.models import Organization
                
                orgs = Organization.objects.filter(
                    is_active=True
                ).exclude(code__in=['OOBC', 'OCM'])
                
                planning_data = []
                for org in orgs:
                    strategic_count = StrategicPlan.objects.filter(
                        organization=org,
                        is_active=True
                    ).count()
                    
                    annual_count = AnnualWorkPlan.objects.filter(
                        organization=org,
                        is_active=True
                    ).count()
                    
                    planning_data.append({
                        'organization': org.name,
                        'organization_code': org.code,
                        'active_strategic_plans': strategic_count,
                        'active_annual_plans': annual_count,
                        'has_planning': strategic_count > 0 or annual_count > 0
                    })
                
                data = {
                    'by_organization': planning_data,
                    'total_strategic': sum(p['active_strategic_plans'] for p in planning_data),
                    'total_annual': sum(p['active_annual_plans'] for p in planning_data),
                }
                
                cache.set(cache_key, data, CACHE_TTL)
                logger.debug(f"Cached planning status: {len(planning_data)} organizations")
            except Exception as e:
                logger.error(f"Error getting planning status: {e}")
                data = {'by_organization': [], 'total_strategic': 0, 'total_annual': 0}
        
        return data
    
    @staticmethod
    def get_planning_summary():
        """Get planning summary statistics"""
        cache_key = 'ocm:planning:summary'
        summary = cache.get(cache_key)
        
        if summary is None:
            try:
                from planning.models import StrategicPlan, AnnualWorkPlan
                from organizations.models import Organization
                
                total_strategic = StrategicPlan.objects.filter(is_active=True).count()
                total_annual = AnnualWorkPlan.objects.filter(is_active=True).count()
                
                moas_with_plans = Organization.objects.filter(
                    is_active=True,
                    strategicplan__is_active=True
                ).distinct().count()
                
                summary = {
                    'total_plans': total_strategic + total_annual,
                    'active_plans': total_strategic + total_annual,
                    'moas_with_plans': moas_with_plans
                }
                
                cache.set(cache_key, summary, CACHE_TTL)
            except Exception as e:
                logger.error(f"Error getting planning summary: {e}")
                summary = {'total_plans': 0, 'active_plans': 0, 'moas_with_plans': 0}
        
        return summary
    
    @staticmethod
    def get_inter_moa_partnerships():
        """
        Get inter-MOA partnerships.
        
        Returns:
            list: List of partnership dicts
        """
        cache_key = 'ocm:coord:partnerships'
        data = cache.get(cache_key)
        
        if data is None:
            try:
                from coordination.models import InterMOAPartnership
                
                partnerships = InterMOAPartnership.objects.select_related(
                    'lead_moa'
                ).prefetch_related(
                    'participating_moas'
                ).filter(is_active=True)
                
                data = []
                for p in partnerships:
                    participating = [m.code for m in p.participating_moas.all()]
                    
                    data.append({
                        'id': p.id,
                        'title': p.title,
                        'type': p.partnership_type,
                        'lead_moa': p.lead_moa.code if p.lead_moa else None,
                        'participating_moas': participating,
                        'status': p.status,
                        'progress': getattr(p, 'progress_percentage', 0)
                    })
                
                cache.set(cache_key, data, CACHE_TTL)
                logger.debug(f"Cached {len(data)} partnerships")
            except Exception as e:
                logger.error(f"Error getting partnerships: {e}")
                data = []
        
        return data
    
    @staticmethod
    def get_coordination_summary():
        """Get coordination summary statistics"""
        cache_key = 'ocm:coord:summary'
        summary = cache.get(cache_key)
        
        if summary is None:
            try:
                from coordination.models import InterMOAPartnership
                from django.db.models import Count
                
                total = InterMOAPartnership.objects.filter(is_active=True).count()
                active = InterMOAPartnership.objects.filter(
                    is_active=True,
                    status='active'
                ).count()
                
                # Get most collaborative MOAs
                from organizations.models import Organization
                
                most_collaborative = Organization.objects.filter(
                    is_active=True
                ).annotate(
                    partnership_count=Count('led_partnerships') + Count('partnerships')
                ).order_by('-partnership_count')[:5]
                
                collab_list = [
                    {'code': org.code, 'name': org.name, 'count': org.partnership_count}
                    for org in most_collaborative
                ]
                
                summary = {
                    'total_partnerships': total,
                    'active_partnerships': active,
                    'most_collaborative_moas': collab_list
                }
                
                cache.set(cache_key, summary, CACHE_TTL)
            except Exception as e:
                logger.error(f"Error getting coordination summary: {e}")
                summary = {
                    'total_partnerships': 0,
                    'active_partnerships': 0,
                    'most_collaborative_moas': []
                }
        
        return summary
    
    @staticmethod
    def get_performance_metrics():
        """
        Get government-wide performance metrics.
        
        Returns:
            dict: Performance metrics including approval rates, completion rates
        """
        cache_key = 'ocm:performance:metrics'
        metrics = cache.get(cache_key)
        
        if metrics is None:
            try:
                budget_approval = OCMAggregationService._calculate_budget_approval_rate()
                planning_completion = OCMAggregationService._calculate_planning_completion()
                partnership_success = OCMAggregationService._calculate_partnership_success()
                
                # Calculate overall score (weighted average)
                overall_score = (
                    budget_approval * 0.4 +
                    planning_completion * 0.3 +
                    partnership_success * 0.3
                )
                
                metrics = {
                    'budget_approval_rate': round(budget_approval, 2),
                    'planning_completion': round(planning_completion, 2),
                    'partnership_success': round(partnership_success, 2),
                    'overall_score': round(overall_score, 2)
                }
                
                cache.set(cache_key, metrics, CACHE_TTL)
            except Exception as e:
                logger.error(f"Error getting performance metrics: {e}")
                metrics = {
                    'budget_approval_rate': 0,
                    'planning_completion': 0,
                    'partnership_success': 0,
                    'overall_score': 0
                }
        
        return metrics
    
    @staticmethod
    def _calculate_budget_approval_rate(fiscal_year=None):
        """Calculate budget approval rate percentage"""
        try:
            from budget_preparation.models import BudgetProposal
            
            queryset = BudgetProposal.objects.all()
            if fiscal_year:
                queryset = queryset.filter(fiscal_year=fiscal_year)
            
            total = queryset.count()
            if total == 0:
                return 0
            
            approved = queryset.filter(status='approved').count()
            return (approved / total) * 100
        except Exception as e:
            logger.error(f"Error calculating budget approval rate: {e}")
            return 0
    
    @staticmethod
    def _calculate_planning_completion():
        """Calculate planning completion rate"""
        try:
            from planning.models import StrategicPlan
            from organizations.models import Organization
            
            total_moas = Organization.objects.filter(
                is_active=True
            ).exclude(code__in=['OOBC', 'OCM']).count()
            
            if total_moas == 0:
                return 0
            
            moas_with_plans = Organization.objects.filter(
                is_active=True,
                strategicplan__is_active=True
            ).distinct().count()
            
            return (moas_with_plans / total_moas) * 100
        except Exception as e:
            logger.error(f"Error calculating planning completion: {e}")
            return 0
    
    @staticmethod
    def _calculate_partnership_success():
        """Calculate partnership success rate"""
        try:
            from coordination.models import InterMOAPartnership
            
            total = InterMOAPartnership.objects.filter(is_active=True).count()
            if total == 0:
                return 0
            
            successful = InterMOAPartnership.objects.filter(
                is_active=True,
                status__in=['active', 'completed']
            ).count()
            
            return (successful / total) * 100
        except Exception as e:
            logger.error(f"Error calculating partnership success: {e}")
            return 0
    
    @staticmethod
    def clear_cache():
        """
        Clear all OCM cache keys.
        
        Call this when data is updated to refresh aggregations.
        """
        try:
            from django.core.cache import cache
            
            # List of all cache key patterns
            patterns = [
                'ocm:org_count',
                'ocm:all_orgs',
                'ocm:gov_stats',
                'ocm:budget:consolidated:*',
                'ocm:budget:summary:*',
                'ocm:planning:status',
                'ocm:planning:summary',
                'ocm:coord:partnerships',
                'ocm:coord:summary',
                'ocm:performance:metrics',
            ]
            
            # Django cache doesn't support pattern deletion, so we delete known keys
            cache.delete_many([
                'ocm:org_count',
                'ocm:all_orgs',
                'ocm:gov_stats',
                'ocm:budget:consolidated:all',
                'ocm:budget:summary:all',
                'ocm:planning:status',
                'ocm:planning:summary',
                'ocm:coord:partnerships',
                'ocm:coord:summary',
                'ocm:performance:metrics',
            ])
            
            logger.info("Cleared all OCM cache keys")
        except Exception as e:
            logger.error(f"Error clearing OCM cache: {e}")
