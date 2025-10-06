"""
Resource Optimizer Service

AI-powered optimization of resource allocation across partnerships and projects.
"""

import json
from typing import Dict, List, Optional
from decimal import Decimal
from collections import defaultdict

from django.db.models import Sum, Avg, Count, Q, F
from django.utils import timezone

from ai_assistant.services import GeminiService
from coordination.models import Partnership, Organization
from communities.models import BarangayOBC


class ResourceOptimizer:
    """Optimize resource allocation using AI analysis"""

    def __init__(self):
        self.gemini = GeminiService()

    def optimize_budget_allocation(
        self,
        total_budget: Decimal,
        communities: List[int],
        priority_weights: Optional[Dict] = None
    ) -> Dict:
        """
        Optimize budget allocation across multiple communities

        Args:
            total_budget: Total available budget
            communities: List of BarangayOBC IDs
            priority_weights: Optional weights for criteria
                {
                    'population': 0.3,
                    'needs_severity': 0.4,
                    'accessibility': 0.2,
                    'prior_investment': 0.1
                }

        Returns:
            {
                'allocations': [
                    {
                        'community_id': 123,
                        'community_name': '...',
                        'allocated_budget': 5000000,
                        'percentage': 25.0,
                        'rationale': '...'
                    },
                    ...
                ],
                'optimization_criteria': {...},
                'recommendations': [...]
            }
        """
        # Default weights
        if not priority_weights:
            priority_weights = {
                'population': 0.3,
                'needs_severity': 0.3,
                'accessibility': 0.2,
                'prior_investment': 0.2
            }

        # Get community data
        community_data = []
        for comm_id in communities:
            try:
                community = BarangayOBC.objects.select_related(
                    'municipality__province__region'
                ).get(id=comm_id)

                # Calculate community score
                score = self._calculate_community_priority(
                    community,
                    priority_weights
                )

                community_data.append({
                    'id': comm_id,
                    'name': community.name,
                    'province': community.municipality.province.name,
                    'population': community.total_population,
                    'score': score,
                    'community': community
                })
            except BarangayOBC.DoesNotExist:
                continue

        # Calculate total score
        total_score = sum(c['score'] for c in community_data)

        # Allocate budget proportionally
        allocations = []
        for data in community_data:
            percentage = (data['score'] / total_score * 100) if total_score > 0 else 0
            allocated = total_budget * Decimal(str(data['score'] / total_score)) if total_score > 0 else 0

            allocations.append({
                'community_id': data['id'],
                'community_name': data['name'],
                'province': data['province'],
                'population': data['population'],
                'allocated_budget': float(allocated),
                'percentage': round(percentage, 1),
                'priority_score': round(data['score'], 2),
                'rationale': self._generate_allocation_rationale(
                    data['community'],
                    percentage,
                    priority_weights
                )
            })

        # Sort by allocation (descending)
        allocations.sort(key=lambda x: x['allocated_budget'], reverse=True)

        return {
            'total_budget': float(total_budget),
            'allocations': allocations,
            'optimization_criteria': priority_weights,
            'recommendations': self._generate_allocation_recommendations(allocations)
        }

    def _calculate_community_priority(
        self,
        community: BarangayOBC,
        weights: Dict
    ) -> float:
        """Calculate community priority score"""
        score = 0.0

        # Population factor (normalized to 0-1)
        # Assume max population of 50,000
        pop_factor = min(community.total_population / 50000, 1.0)
        score += pop_factor * weights.get('population', 0.3)

        # Needs severity (placeholder - would integrate with MANA data)
        # For now, use inverse of prior investment as proxy
        needs_factor = 0.5  # Default medium severity
        score += needs_factor * weights.get('needs_severity', 0.3)

        # Accessibility (inverse of remoteness)
        # Use province-level proxy for now
        accessibility_factor = 0.7  # Default moderate accessibility
        score += accessibility_factor * weights.get('accessibility', 0.2)

        # Prior investment (inverse factor - prioritize underserved)
        # Check partnerships involving this community
        from coordination.models import Partnership
        prior_partnerships = Partnership.objects.filter(
            communities=community,
            status__in=['active', 'completed']
        ).count()

        # Inverse factor: more prior investment = lower priority
        prior_factor = max(0, 1.0 - (prior_partnerships * 0.1))
        score += prior_factor * weights.get('prior_investment', 0.2)

        return score

    def _generate_allocation_rationale(
        self,
        community: BarangayOBC,
        percentage: float,
        weights: Dict
    ) -> str:
        """Generate human-readable allocation rationale"""
        factors = []

        # Population
        if weights.get('population', 0) > 0.2:
            if community.total_population > 20000:
                factors.append('large population')
            elif community.total_population > 10000:
                factors.append('moderate population')

        # Prior investment
        from coordination.models import Partnership
        prior_count = Partnership.objects.filter(
            communities=community,
            status__in=['active', 'completed']
        ).count()

        if prior_count == 0:
            factors.append('currently underserved')
        elif prior_count < 3:
            factors.append('limited prior investment')

        # Location
        factors.append(f'located in {community.municipality.province.name}')

        return f"{percentage:.1f}% allocation based on: " + ", ".join(factors) + "."

    def _generate_allocation_recommendations(self, allocations: List[Dict]) -> List[str]:
        """Generate recommendations for budget allocation"""
        recommendations = []

        # Check for imbalanced allocation
        top_allocation = allocations[0]['percentage'] if allocations else 0
        if top_allocation > 40:
            recommendations.append(
                f"Consider more balanced distribution - top allocation is {top_allocation:.1f}%"
            )

        # Check for very small allocations
        small_allocations = [a for a in allocations if a['percentage'] < 5]
        if small_allocations:
            recommendations.append(
                f"{len(small_allocations)} communities have <5% allocation - "
                f"consider minimum threshold or grouping"
            )

        # Geographic diversity
        provinces = set(a['province'] for a in allocations)
        if len(provinces) < len(allocations) / 2:
            recommendations.append(
                "Consider geographic diversity in allocation"
            )

        if not recommendations:
            recommendations.append("Budget allocation is well-balanced")

        return recommendations

    def recommend_partnerships_for_budget(
        self,
        community_id: int,
        budget: Decimal,
        project_type: str
    ) -> List[Dict]:
        """
        Recommend optimal partnerships given a budget constraint

        Returns:
            List of recommended partnership configurations
        """
        try:
            community = BarangayOBC.objects.get(id=community_id)
        except BarangayOBC.DoesNotExist:
            return []

        # Get relevant stakeholders
        stakeholders = Organization.objects.filter(
            is_active=True,
            partnership_status='active'
        )

        # Filter by budget capacity
        stakeholders = stakeholders.filter(
            Q(annual_budget__gte=budget * Decimal('0.1')) |
            Q(annual_budget__isnull=True)
        )

        recommendations = []

        # Single partner scenarios
        for org in stakeholders[:10]:  # Limit to top 10
            config = {
                'type': 'single_partner',
                'partners': [{'id': str(org.id), 'name': org.name}],
                'estimated_coverage': self._estimate_coverage(org, budget),
                'pros': [f"Simpler coordination with {org.name}"],
                'cons': ['Single point of failure', 'Limited expertise diversity'],
                'budget_distribution': {str(org.id): float(budget)}
            }
            recommendations.append(config)

        # Multi-partner scenarios (if budget > 5M)
        if budget > Decimal('5000000'):
            # Find complementary pairs
            for i, org1 in enumerate(stakeholders[:5]):
                for org2 in stakeholders[i+1:i+3]:
                    if self._are_complementary(org1, org2):
                        budget_split = {
                            str(org1.id): float(budget * Decimal('0.6')),
                            str(org2.id): float(budget * Decimal('0.4'))
                        }
                        config = {
                            'type': 'partnership',
                            'partners': [
                                {'id': str(org1.id), 'name': org1.name},
                                {'id': str(org2.id), 'name': org2.name}
                            ],
                            'estimated_coverage': 'Enhanced coverage with complementary expertise',
                            'pros': [
                                'Diverse expertise',
                                'Shared resources and risk',
                                'Broader network'
                            ],
                            'cons': ['More complex coordination', 'Potential for delays'],
                            'budget_distribution': budget_split
                        }
                        recommendations.append(config)

        return recommendations[:5]  # Return top 5

    def _estimate_coverage(self, org: Organization, budget: Decimal) -> str:
        """Estimate service coverage based on organization and budget"""
        if org.staff_count and budget:
            # Simple heuristic: budget per staff member
            per_capita = budget / Decimal(str(org.staff_count))
            if per_capita > Decimal('500000'):
                return 'High capacity - extensive coverage expected'
            elif per_capita > Decimal('200000'):
                return 'Moderate capacity - adequate coverage'
            else:
                return 'Limited capacity - focused intervention'

        return 'Coverage to be determined'

    def _are_complementary(self, org1: Organization, org2: Organization) -> bool:
        """Check if two organizations have complementary expertise"""
        if not org1.areas_of_expertise or not org2.areas_of_expertise:
            return False

        expertise1 = set(org1.areas_of_expertise.lower().split(','))
        expertise2 = set(org2.areas_of_expertise.lower().split(','))

        # Complementary if they have different primary expertise
        overlap = expertise1.intersection(expertise2)
        return len(overlap) < len(expertise1) / 2 and len(overlap) < len(expertise2) / 2

    def analyze_resource_utilization(self, organization_id: str) -> Dict:
        """
        Analyze organization's resource utilization across partnerships

        Returns:
            {
                'total_committed_budget': 1000000,
                'active_partnerships': 5,
                'budget_per_partnership': 200000,
                'utilization_rate': 0.75,
                'capacity_status': 'optimal/overextended/underutilized',
                'recommendations': [...]
            }
        """
        try:
            org = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            return {'error': 'Organization not found'}

        # Get active partnerships
        active_partnerships = Partnership.objects.filter(
            organizations=org,
            status='active'
        )

        total_committed = active_partnerships.aggregate(
            total=Sum('partner_contribution')
        )['total'] or Decimal('0')

        partnership_count = active_partnerships.count()

        # Calculate metrics
        avg_per_partnership = (
            total_committed / partnership_count
            if partnership_count > 0 else Decimal('0')
        )

        # Utilization rate (committed vs. annual budget)
        utilization_rate = 0.0
        if org.annual_budget and org.annual_budget > 0:
            utilization_rate = float(total_committed / org.annual_budget)

        # Determine capacity status
        if utilization_rate > 0.9:
            capacity_status = 'overextended'
        elif utilization_rate > 0.6:
            capacity_status = 'optimal'
        else:
            capacity_status = 'underutilized'

        # Generate recommendations
        recommendations = []
        if capacity_status == 'overextended':
            recommendations.append('Reduce new commitments or increase budget allocation')
            recommendations.append('Consider delegating some partnerships')
        elif capacity_status == 'underutilized':
            recommendations.append('Capacity available for additional partnerships')
            recommendations.append('Consider expanding program reach')
        else:
            recommendations.append('Resource utilization is at optimal level')

        return {
            'organization': org.name,
            'total_committed_budget': float(total_committed),
            'active_partnerships': partnership_count,
            'budget_per_partnership': float(avg_per_partnership),
            'utilization_rate': round(utilization_rate, 2),
            'capacity_status': capacity_status,
            'annual_budget': float(org.annual_budget) if org.annual_budget else 0,
            'recommendations': recommendations
        }

    def suggest_reallocation(
        self,
        partnership_id: str,
        performance_score: float
    ) -> Dict:
        """
        Suggest budget reallocation based on partnership performance

        Args:
            partnership_id: Partnership UUID
            performance_score: Performance score (0-1)

        Returns:
            Reallocation recommendation
        """
        try:
            partnership = Partnership.objects.get(id=partnership_id)
        except Partnership.DoesNotExist:
            return {'error': 'Partnership not found'}

        current_budget = partnership.total_budget or Decimal('0')

        # Determine reallocation
        if performance_score >= 0.8:
            # High performance - suggest increase
            suggested_budget = current_budget * Decimal('1.2')
            recommendation = 'increase'
            rationale = 'Excellent performance warrants additional investment'
        elif performance_score >= 0.6:
            # Good performance - maintain
            suggested_budget = current_budget
            recommendation = 'maintain'
            rationale = 'Good performance - continue current allocation'
        elif performance_score >= 0.4:
            # Fair performance - reduce
            suggested_budget = current_budget * Decimal('0.8')
            recommendation = 'reduce'
            rationale = 'Fair performance - consider reducing allocation'
        else:
            # Poor performance - significant reduction
            suggested_budget = current_budget * Decimal('0.5')
            recommendation = 'significant_reduction'
            rationale = 'Poor performance requires intervention or reallocation'

        return {
            'partnership': partnership.title,
            'current_budget': float(current_budget),
            'suggested_budget': float(suggested_budget),
            'change_amount': float(suggested_budget - current_budget),
            'change_percentage': float((suggested_budget - current_budget) / current_budget * 100) if current_budget > 0 else 0,
            'recommendation': recommendation,
            'rationale': rationale,
            'performance_score': performance_score
        }
