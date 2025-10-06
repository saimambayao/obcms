"""
Risk Analysis Service for PPAs

Identifies and analyzes project risks using ML and AI:
- Budget risks
- Timeline risks
- Implementation risks
- External risks
- Risk mitigation recommendations

Combines quantitative analysis with AI-powered insights.
"""

import json
import logging
from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional

from django.db.models import Q
from django.utils import timezone

from ai_assistant.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


class RiskAnalyzer:
    """
    Analyze and identify project risks using ML and AI.

    Features:
    - Multi-dimensional risk scoring
    - Risk categorization
    - Mitigation recommendations
    - Portfolio risk analysis
    """

    # Risk severity thresholds
    CRITICAL_RISK_SCORE = 0.8
    HIGH_RISK_SCORE = 0.6
    MEDIUM_RISK_SCORE = 0.4

    def __init__(self):
        """Initialize risk analyzer with AI service."""
        self.gemini = GeminiService(temperature=0.4)
        logger.info("RiskAnalyzer initialized")

    def analyze_ppa_risks(self, ppa_id: int) -> Dict:
        """
        Comprehensive risk analysis for a single PPA.

        Args:
            ppa_id: PPA ID to analyze

        Returns:
            Dictionary containing:
            - overall_risk_score: Aggregate risk score (0-1)
            - risk_level: CRITICAL/HIGH/MEDIUM/LOW
            - risk_categories: Breakdown by category
            - identified_risks: List of specific risks
            - mitigation_recommendations: AI-generated recommendations
        """
        from monitoring.models import MonitoringEntry

        try:
            ppa = MonitoringEntry.objects.with_funding_totals().get(id=ppa_id)
        except MonitoringEntry.DoesNotExist:
            return {'error': f'PPA {ppa_id} not found'}

        # Analyze different risk dimensions
        budget_risk = self._analyze_budget_risk(ppa)
        timeline_risk = self._analyze_timeline_risk(ppa)
        implementation_risk = self._analyze_implementation_risk(ppa)
        external_risk = self._analyze_external_risk(ppa)

        # Calculate overall risk score (weighted average)
        overall_risk_score = (
            budget_risk['score'] * 0.3 +
            timeline_risk['score'] * 0.3 +
            implementation_risk['score'] * 0.25 +
            external_risk['score'] * 0.15
        )

        # Determine risk level
        risk_level = self._get_risk_level(overall_risk_score)

        # Collect all identified risks
        identified_risks = (
            budget_risk['risks'] +
            timeline_risk['risks'] +
            implementation_risk['risks'] +
            external_risk['risks']
        )

        # Sort risks by severity
        identified_risks = self._prioritize_risks(identified_risks)

        # AI-generated mitigation recommendations
        mitigation_recommendations = self._generate_mitigation_recommendations(
            ppa, identified_risks
        )

        analysis = {
            'ppa_id': ppa.id,
            'ppa_name': ppa.title,
            'overall_risk_score': round(overall_risk_score, 2),
            'risk_level': risk_level,
            'risk_categories': {
                'budget': {
                    'score': round(budget_risk['score'], 2),
                    'level': self._get_risk_level(budget_risk['score']),
                    'description': budget_risk['description']
                },
                'timeline': {
                    'score': round(timeline_risk['score'], 2),
                    'level': self._get_risk_level(timeline_risk['score']),
                    'description': timeline_risk['description']
                },
                'implementation': {
                    'score': round(implementation_risk['score'], 2),
                    'level': self._get_risk_level(implementation_risk['score']),
                    'description': implementation_risk['description']
                },
                'external': {
                    'score': round(external_risk['score'], 2),
                    'level': self._get_risk_level(external_risk['score']),
                    'description': external_risk['description']
                }
            },
            'identified_risks': identified_risks[:10],  # Top 10
            'mitigation_recommendations': mitigation_recommendations,
            'analysis_date': date.today().isoformat(),
        }

        logger.info(
            f"Risk analysis for PPA {ppa_id}: {risk_level} "
            f"(score: {overall_risk_score:.2f})"
        )

        return analysis

    def analyze_portfolio_risks(self, ministry: Optional[str] = None) -> Dict:
        """
        Analyze risks across entire PPA portfolio.

        Args:
            ministry: Filter by ministry (optional)

        Returns:
            Portfolio-wide risk summary
        """
        from monitoring.models import MonitoringEntry

        # Get active PPAs
        ppas = MonitoringEntry.objects.filter(
            status__in=['planning', 'ongoing']
        )

        if ministry:
            ppas = ppas.filter(
                Q(lead_organization__name__icontains=ministry) |
                Q(implementing_moa__name__icontains=ministry)
            )

        ppas = ppas.with_funding_totals()

        # Analyze each PPA
        high_risk_ppas = []
        risk_scores = []

        for ppa in ppas:
            try:
                analysis = self.analyze_ppa_risks(ppa.id)
                risk_scores.append(analysis['overall_risk_score'])

                if analysis['risk_level'] in ['CRITICAL', 'HIGH']:
                    high_risk_ppas.append({
                        'ppa_id': ppa.id,
                        'ppa_name': ppa.title,
                        'risk_level': analysis['risk_level'],
                        'risk_score': analysis['overall_risk_score'],
                        'top_risks': analysis['identified_risks'][:3]
                    })

            except Exception as e:
                logger.error(f"Error analyzing PPA {ppa.id}: {e}")

        # Calculate portfolio metrics
        if risk_scores:
            avg_risk_score = sum(risk_scores) / len(risk_scores)
            max_risk_score = max(risk_scores)
        else:
            avg_risk_score = 0
            max_risk_score = 0

        # Sort high-risk PPAs by score
        high_risk_ppas.sort(key=lambda x: x['risk_score'], reverse=True)

        portfolio_analysis = {
            'total_ppas_analyzed': len(risk_scores),
            'average_risk_score': round(avg_risk_score, 2),
            'max_risk_score': round(max_risk_score, 2),
            'high_risk_count': len(high_risk_ppas),
            'high_risk_ppas': high_risk_ppas[:10],  # Top 10
            'risk_distribution': {
                'critical': sum(1 for s in risk_scores if s >= self.CRITICAL_RISK_SCORE),
                'high': sum(
                    1 for s in risk_scores
                    if self.HIGH_RISK_SCORE <= s < self.CRITICAL_RISK_SCORE
                ),
                'medium': sum(
                    1 for s in risk_scores
                    if self.MEDIUM_RISK_SCORE <= s < self.HIGH_RISK_SCORE
                ),
                'low': sum(1 for s in risk_scores if s < self.MEDIUM_RISK_SCORE),
            },
            'ministry': ministry or 'All Ministries',
            'analysis_date': date.today().isoformat(),
        }

        logger.info(
            f"Portfolio risk analysis: {len(high_risk_ppas)} high-risk PPAs identified"
        )

        return portfolio_analysis

    def _analyze_budget_risk(self, ppa) -> Dict:
        """Analyze budget-related risks."""
        risks = []
        risk_score = 0.0

        budget_allocation = float(ppa.budget_allocation or 0)
        current_spending = float(ppa.total_disbursements_sum or 0)

        if budget_allocation == 0:
            return {
                'score': 0.5,
                'description': 'No budget allocation',
                'risks': [{'type': 'budget', 'severity': 'MEDIUM', 'description': 'No budget allocated'}]
            }

        # Calculate utilization
        utilization = current_spending / budget_allocation if budget_allocation > 0 else 0

        # Risk: High utilization early in project
        if ppa.start_date and ppa.target_completion:
            timeline_progress = self._calculate_timeline_progress(ppa)

            if utilization > timeline_progress + 0.25:
                risk_score += 0.4
                risks.append({
                    'type': 'budget',
                    'severity': 'HIGH',
                    'description': f'Budget {utilization:.0%} spent but only {timeline_progress:.0%} through timeline'
                })

        # Risk: Very high utilization
        if utilization > 0.9:
            risk_score += 0.3
            risks.append({
                'type': 'budget',
                'severity': 'HIGH',
                'description': f'Budget {utilization:.0%} utilized - potential overrun risk'
            })

        # Risk: Large budget with low disbursement
        if budget_allocation > 1000000 and utilization < 0.2:
            risk_score += 0.2
            risks.append({
                'type': 'budget',
                'severity': 'MEDIUM',
                'description': 'Large budget with low disbursement rate'
            })

        description = f"Budget utilization at {utilization:.0%}"

        return {
            'score': min(risk_score, 1.0),
            'description': description,
            'risks': risks
        }

    def _analyze_timeline_risk(self, ppa) -> Dict:
        """Analyze timeline-related risks."""
        risks = []
        risk_score = 0.0

        if not ppa.start_date or not ppa.target_completion:
            return {
                'score': 0.3,
                'description': 'Missing timeline data',
                'risks': [{'type': 'timeline', 'severity': 'LOW', 'description': 'No clear timeline defined'}]
            }

        # Calculate timeline metrics
        total_days = (ppa.target_completion - ppa.start_date).days
        elapsed_days = (date.today() - ppa.start_date).days
        remaining_days = (ppa.target_completion - date.today()).days

        timeline_progress = elapsed_days / total_days if total_days > 0 else 0

        # Risk: Past target completion date
        if remaining_days < 0:
            risk_score += 0.5
            risks.append({
                'type': 'timeline',
                'severity': 'CRITICAL',
                'description': f'Project {abs(remaining_days)} days overdue'
            })

        # Risk: Close to deadline with low progress
        elif remaining_days < 30:
            actual_progress = self._get_actual_progress(ppa)
            if actual_progress < 0.8:
                risk_score += 0.4
                risks.append({
                    'type': 'timeline',
                    'severity': 'HIGH',
                    'description': f'Only {remaining_days} days remaining, {actual_progress:.0%} complete'
                })

        # Risk: Slow progress
        if timeline_progress > 0.5:
            actual_progress = self._get_actual_progress(ppa)
            if actual_progress < timeline_progress - 0.2:
                risk_score += 0.3
                risks.append({
                    'type': 'timeline',
                    'severity': 'MEDIUM',
                    'description': f'Behind schedule: {actual_progress:.0%} complete vs {timeline_progress:.0%} expected'
                })

        description = f"{remaining_days} days remaining to target completion"

        return {
            'score': min(risk_score, 1.0),
            'description': description,
            'risks': risks
        }

    def _analyze_implementation_risk(self, ppa) -> Dict:
        """Analyze implementation-related risks."""
        risks = []
        risk_score = 0.0

        # Risk: On hold status
        if ppa.status == 'on_hold':
            risk_score += 0.6
            risks.append({
                'type': 'implementation',
                'severity': 'CRITICAL',
                'description': 'Project currently on hold'
            })

        # Risk: Planning status for too long
        if ppa.status == 'planning' and ppa.start_date:
            planning_days = (date.today() - ppa.start_date).days
            if planning_days > 90:
                risk_score += 0.4
                risks.append({
                    'type': 'implementation',
                    'severity': 'HIGH',
                    'description': f'In planning phase for {planning_days} days'
                })

        # Risk: No recent updates (if update tracking exists)
        # This would require update/activity tracking
        # Placeholder for future enhancement

        # Risk: Complex sector
        complex_sectors = ['infrastructure', 'environment']
        if hasattr(ppa, 'sector') and ppa.sector in complex_sectors:
            risk_score += 0.1
            risks.append({
                'type': 'implementation',
                'severity': 'LOW',
                'description': f'Complex sector ({ppa.get_sector_display()}) may face technical challenges'
            })

        description = f"Current status: {ppa.get_status_display() if hasattr(ppa, 'get_status_display') else ppa.status}"

        return {
            'score': min(risk_score, 1.0),
            'description': description,
            'risks': risks
        }

    def _analyze_external_risk(self, ppa) -> Dict:
        """Analyze external risks (funding, stakeholders, etc.)."""
        risks = []
        risk_score = 0.0

        # Risk: Donor-funded projects (dependency on external funding)
        if hasattr(ppa, 'funding_source') and ppa.funding_source == 'donor':
            risk_score += 0.2
            risks.append({
                'type': 'external',
                'severity': 'MEDIUM',
                'description': 'Dependent on external donor funding'
            })

        # Risk: Multiple implementing organizations (coordination complexity)
        if hasattr(ppa, 'supporting_organizations'):
            supporting_count = ppa.supporting_organizations.count()
            if supporting_count > 3:
                risk_score += 0.15
                risks.append({
                    'type': 'external',
                    'severity': 'LOW',
                    'description': f'Coordination complexity with {supporting_count} supporting organizations'
                })

        # Risk: Multi-community coverage (wider scope)
        if hasattr(ppa, 'communities'):
            community_count = ppa.communities.count()
            if community_count > 5:
                risk_score += 0.1
                risks.append({
                    'type': 'external',
                    'severity': 'LOW',
                    'description': f'Wide coverage across {community_count} communities'
                })

        description = "External environment assessment"

        return {
            'score': min(risk_score, 1.0),
            'description': description,
            'risks': risks
        }

    def _calculate_timeline_progress(self, ppa) -> float:
        """Calculate timeline progress (0.0 to 1.0)."""
        if not ppa.start_date or not ppa.target_completion:
            return 0.0

        total_days = (ppa.target_completion - ppa.start_date).days
        if total_days <= 0:
            return 0.0

        elapsed_days = (date.today() - ppa.start_date).days

        return min(max(elapsed_days / total_days, 0.0), 1.0)

    def _get_actual_progress(self, ppa) -> float:
        """Get actual project progress (0.0 to 1.0)."""
        # Try milestones
        milestones = getattr(ppa, 'milestones', None)
        if milestones and milestones.exists():
            total = milestones.count()
            completed = milestones.filter(status='completed').count()
            if total > 0:
                return completed / total

        # Fallback to status
        status_progress = {
            'completed': 1.0,
            'ongoing': 0.5,
            'planning': 0.1,
            'on_hold': 0.0
        }

        return status_progress.get(ppa.status, 0.0)

    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to level."""
        if risk_score >= self.CRITICAL_RISK_SCORE:
            return 'CRITICAL'
        elif risk_score >= self.HIGH_RISK_SCORE:
            return 'HIGH'
        elif risk_score >= self.MEDIUM_RISK_SCORE:
            return 'MEDIUM'
        return 'LOW'

    def _prioritize_risks(self, risks: List[Dict]) -> List[Dict]:
        """Sort risks by severity."""
        severity_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}

        return sorted(
            risks,
            key=lambda r: severity_order.get(r['severity'], 0),
            reverse=True
        )

    def _generate_mitigation_recommendations(
        self, ppa, identified_risks: List[Dict]
    ) -> List[str]:
        """
        Generate AI-powered mitigation recommendations.

        Returns:
            List of recommendation strings
        """
        if not identified_risks:
            return ["No significant risks identified - continue current approach"]

        # Format risks for AI
        risks_text = '\n'.join(
            f"- [{r['severity']}] {r['description']}"
            for r in identified_risks[:5]
        )

        prompt = f"""
Provide mitigation recommendations for this government project:

**Project:** {ppa.title}
**Status:** {ppa.status}

**Identified Risks:**
{risks_text}

Generate 5 specific, actionable mitigation recommendations.
Focus on practical steps to reduce these risks.
Each recommendation should be one concise sentence.

Return ONLY valid JSON array (no markdown):
["Recommendation 1", "Recommendation 2", ...]
"""

        try:
            response = self.gemini.generate_text(
                prompt,
                use_cache=True,
                cache_ttl=3600,
                include_cultural_context=False
            )

            if response['success']:
                text = response['text'].strip()
                if text.startswith('```'):
                    text = text.split('```')[1]
                    if text.startswith('json'):
                        text = text[4:]
                    text = text.strip()

                recommendations = json.loads(text)
                if isinstance(recommendations, list):
                    return recommendations[:5]

        except Exception as e:
            logger.warning(f"AI mitigation recommendations failed: {e}")

        # Fallback recommendations based on risk types
        return self._generate_fallback_mitigations(identified_risks)

    def _generate_fallback_mitigations(self, risks: List[Dict]) -> List[str]:
        """Generate fallback mitigation recommendations."""
        recommendations = []

        # Address top risks
        for risk in risks[:3]:
            if risk['type'] == 'budget':
                recommendations.append("Conduct urgent budget review and implement tighter spending controls")
            elif risk['type'] == 'timeline':
                recommendations.append("Accelerate critical path activities and remove bottlenecks")
            elif risk['type'] == 'implementation':
                recommendations.append("Provide additional technical support to implementing team")
            elif risk['type'] == 'external':
                recommendations.append("Strengthen stakeholder coordination and communication")

        # Generic recommendations
        if len(recommendations) < 5:
            recommendations.extend([
                "Increase monitoring frequency to weekly status updates",
                "Escalate critical issues to executive leadership",
                "Develop contingency plans for high-risk areas"
            ])

        return recommendations[:5]
