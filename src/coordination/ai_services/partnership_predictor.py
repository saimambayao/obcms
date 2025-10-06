"""
Partnership Predictor Service

Predict partnership success using historical data and AI-powered analysis.
"""

import json
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime, timedelta

from django.db.models import Q, Avg, Count, F
from django.utils import timezone
from django.core.cache import cache

from ai_assistant.services import GeminiService
from coordination.models import (
    Partnership,
    Organization,
    PartnershipMilestone
)
from communities.models import BarangayOBC


class PartnershipPredictor:
    """Predict partnership success using historical data and ML"""

    def __init__(self):
        self.gemini = GeminiService()

    def predict_success(
        self,
        stakeholder_id: str,
        community_id: int,
        project_type: str,
        budget: Optional[Decimal] = None
    ) -> Dict:
        """
        Predict likelihood of partnership success

        Args:
            stakeholder_id: Organization UUID
            community_id: Community ID (BarangayOBC)
            project_type: Type of project/intervention
            budget: Proposed budget (optional)

        Returns:
            {
                'success_probability': 0.78,
                'confidence_level': 'high',
                'risk_factors': ['Geographic distance', 'Limited capacity'],
                'success_factors': ['Sector expertise', 'Past experience'],
                'recommendations': ['Pair with local NGO', 'Provide capacity building'],
                'historical_context': {...}
            }
        """
        # Extract features
        features = self._extract_features(stakeholder_id, community_id, project_type, budget)

        # Build prediction prompt
        prompt = self._build_prediction_prompt(features)

        # Get AI prediction
        try:
            response = self.gemini.generate_text(prompt, temperature=0.3)
            prediction = json.loads(response)

            # Add historical context
            prediction['historical_context'] = {
                'past_projects': features['past_projects_count'],
                'success_rate': features['success_rate'],
                'similar_projects': features['similar_projects_count']
            }

            return prediction

        except Exception as e:
            # Fallback to rule-based prediction
            return self._fallback_prediction(features)

    def _extract_features(
        self,
        stakeholder_id: str,
        community_id: int,
        project_type: str,
        budget: Optional[Decimal]
    ) -> Dict:
        """Extract features for prediction"""
        try:
            stakeholder = Organization.objects.get(id=stakeholder_id)
            community = BarangayOBC.objects.select_related(
                'municipality__province__region'
            ).get(id=community_id)
        except (Organization.DoesNotExist, BarangayOBC.DoesNotExist):
            return {}

        # Historical partnerships
        past_partnerships = Partnership.objects.filter(
            organizations=stakeholder
        )

        total_projects = past_partnerships.count()
        completed_projects = past_partnerships.filter(status='completed').count()
        success_rate = (completed_projects / total_projects * 100) if total_projects > 0 else 0

        # Similar projects
        similar_projects = past_partnerships.filter(
            objectives__icontains=project_type
        ).count()

        # Geographic match
        geographic_match = False
        if stakeholder.geographic_coverage:
            coverage = stakeholder.geographic_coverage.lower()
            geographic_match = (
                community.municipality.province.name.lower() in coverage or
                community.municipality.province.region.name.lower() in coverage
            )

        # Sector alignment
        sector_match = False
        if stakeholder.areas_of_expertise:
            sector_match = project_type.lower() in stakeholder.areas_of_expertise.lower()

        # Budget adequacy
        budget_adequate = True
        if budget and stakeholder.annual_budget:
            budget_adequate = stakeholder.annual_budget >= budget * Decimal('0.2')

        # Staff capacity
        staff_adequate = stakeholder.staff_count and stakeholder.staff_count >= 10

        # Recent activity
        recent_partnerships = past_partnerships.filter(
            created_at__gte=timezone.now() - timedelta(days=365)
        ).count()

        return {
            'stakeholder_name': stakeholder.name,
            'stakeholder_type': stakeholder.get_organization_type_display(),
            'sectors': stakeholder.areas_of_expertise or 'Not specified',
            'coverage': stakeholder.geographic_coverage or 'Not specified',
            'budget': float(stakeholder.annual_budget) if stakeholder.annual_budget else 0,
            'staff_count': stakeholder.staff_count or 0,
            'past_projects_count': total_projects,
            'completed_projects_count': completed_projects,
            'success_rate': round(success_rate, 1),
            'similar_projects_count': similar_projects,
            'recent_activity': recent_partnerships,
            'community_name': community.name,
            'province': community.municipality.province.name,
            'region': community.municipality.province.region.name,
            'population': community.total_population,
            'project_type': project_type,
            'proposed_budget': float(budget) if budget else 0,
            'geographic_match': geographic_match,
            'sector_match': sector_match,
            'budget_adequate': budget_adequate,
            'staff_adequate': staff_adequate,
        }

    def _build_prediction_prompt(self, features: Dict) -> str:
        """Build prompt for AI prediction"""
        return f"""
Predict partnership success based on these factors:

Stakeholder: {features.get('stakeholder_name')}
- Type: {features.get('stakeholder_type')}
- Sectors: {features.get('sectors')}
- Coverage: {features.get('coverage')}
- Annual Budget: ₱{features.get('budget'):,.2f}
- Staff Count: {features.get('staff_count')}
- Past Projects: {features.get('past_projects_count')}
- Success Rate: {features.get('success_rate')}%
- Similar Projects: {features.get('similar_projects_count')}
- Recent Activity: {features.get('recent_activity')} projects in past year

Community: {features.get('community_name')}
- Province: {features.get('province')}
- Region: {features.get('region')}
- Population: {features.get('population'):,}

Project Details:
- Type: {features.get('project_type')}
- Proposed Budget: ₱{features.get('proposed_budget'):,.2f}

Alignment Factors:
- Geographic Match: {'Yes' if features.get('geographic_match') else 'No'}
- Sector Match: {'Yes' if features.get('sector_match') else 'No'}
- Budget Adequate: {'Yes' if features.get('budget_adequate') else 'No'}
- Staff Adequate: {'Yes' if features.get('staff_adequate') else 'No'}

Provide a comprehensive partnership success prediction with:
1. Success probability (0.0-1.0 scale)
2. Confidence level (low/medium/high)
3. Risk factors (list of potential challenges)
4. Success factors (list of positive indicators)
5. Specific recommendations (actionable steps to improve success)

Return as JSON with keys: success_probability, confidence_level, risk_factors, success_factors, recommendations
"""

    def _fallback_prediction(self, features: Dict) -> Dict:
        """Rule-based fallback prediction"""
        # Calculate simple score
        score = 0.5  # Base score

        # Adjust based on features
        if features.get('success_rate', 0) >= 80:
            score += 0.2
        elif features.get('success_rate', 0) >= 60:
            score += 0.1

        if features.get('geographic_match'):
            score += 0.1

        if features.get('sector_match'):
            score += 0.1

        if features.get('budget_adequate'):
            score += 0.05

        if features.get('staff_adequate'):
            score += 0.05

        if features.get('similar_projects_count', 0) > 0:
            score += 0.05

        # Determine confidence
        data_points = sum([
            features.get('past_projects_count', 0) > 0,
            features.get('geographic_match', False),
            features.get('sector_match', False),
            bool(features.get('budget')),
            bool(features.get('staff_count'))
        ])

        if data_points >= 4:
            confidence = 'high'
        elif data_points >= 2:
            confidence = 'medium'
        else:
            confidence = 'low'

        # Identify risk factors
        risk_factors = []
        if not features.get('geographic_match'):
            risk_factors.append('Geographic distance from target area')
        if features.get('success_rate', 0) < 60:
            risk_factors.append('Limited track record')
        if not features.get('budget_adequate'):
            risk_factors.append('Budget constraints')
        if not features.get('staff_adequate'):
            risk_factors.append('Limited staffing capacity')

        # Identify success factors
        success_factors = []
        if features.get('sector_match'):
            success_factors.append('Strong sector expertise')
        if features.get('success_rate', 0) >= 70:
            success_factors.append('Proven track record')
        if features.get('geographic_match'):
            success_factors.append('Geographic presence in target area')
        if features.get('similar_projects_count', 0) > 0:
            success_factors.append('Experience with similar projects')

        # Generate recommendations
        recommendations = []
        if not features.get('geographic_match'):
            recommendations.append('Partner with local organization for geographic coverage')
        if not features.get('sector_match'):
            recommendations.append('Engage technical expert for sector-specific guidance')
        if risk_factors:
            recommendations.append('Conduct thorough risk assessment and mitigation planning')

        return {
            'success_probability': min(score, 1.0),
            'confidence_level': confidence,
            'risk_factors': risk_factors or ['No significant risks identified'],
            'success_factors': success_factors or ['General organizational capacity'],
            'recommendations': recommendations or ['Proceed with standard partnership protocols'],
            'historical_context': {
                'past_projects': features.get('past_projects_count', 0),
                'success_rate': features.get('success_rate', 0),
                'similar_projects': features.get('similar_projects_count', 0)
            }
        }

    def analyze_partnership_portfolio(self, organization_id: str) -> Dict:
        """
        Analyze organization's partnership portfolio

        Returns insights on partnership patterns, success rates, and recommendations
        """
        try:
            org = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            return {'error': 'Organization not found'}

        # Get all partnerships
        partnerships = Partnership.objects.filter(organizations=org)

        # Calculate metrics
        total = partnerships.count()
        active = partnerships.filter(status='active').count()
        completed = partnerships.filter(status='completed').count()
        success_rate = (completed / total * 100) if total > 0 else 0

        # Milestone completion rate
        milestones = PartnershipMilestone.objects.filter(
            partnership__organizations=org
        )
        total_milestones = milestones.count()
        completed_milestones = milestones.filter(status='completed').count()
        milestone_completion_rate = (
            completed_milestones / total_milestones * 100
        ) if total_milestones > 0 else 0

        # Average duration
        completed_partnerships = partnerships.filter(
            status='completed',
            start_date__isnull=False,
            end_date__isnull=False
        )
        avg_duration_days = 0
        if completed_partnerships.exists():
            durations = [
                (p.end_date - p.start_date).days
                for p in completed_partnerships
            ]
            avg_duration_days = sum(durations) / len(durations)

        return {
            'organization': org.name,
            'total_partnerships': total,
            'active_partnerships': active,
            'completed_partnerships': completed,
            'success_rate': round(success_rate, 1),
            'milestone_completion_rate': round(milestone_completion_rate, 1),
            'average_duration_days': round(avg_duration_days),
            'partnership_types': list(
                partnerships.values('partnership_type').annotate(
                    count=Count('id')
                ).order_by('-count')
            ),
            'recommendations': self._generate_portfolio_recommendations(
                success_rate,
                milestone_completion_rate,
                active
            )
        }

    def _generate_portfolio_recommendations(
        self,
        success_rate: float,
        milestone_rate: float,
        active_count: int
    ) -> List[str]:
        """Generate recommendations based on portfolio analysis"""
        recommendations = []

        if success_rate < 60:
            recommendations.append(
                'Focus on improving partnership completion rates through better project planning'
            )

        if milestone_rate < 70:
            recommendations.append(
                'Strengthen milestone tracking and accountability mechanisms'
            )

        if active_count > 10:
            recommendations.append(
                'Consider partnership portfolio management to avoid overextension'
            )

        if success_rate >= 80 and milestone_rate >= 80:
            recommendations.append(
                'Excellent track record - consider taking on more complex partnerships'
            )

        return recommendations or ['Continue with current partnership approach']
