"""
PPA Anomaly Detection Service

Detects anomalies in PPA (Projects, Programs, Activities) performance:
- Budget overruns and underspending
- Timeline delays
- Performance deviations

Uses ML (Isolation Forest) and AI (Gemini) for analysis.
"""

import json
import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from django.db.models import Q, Sum
from django.utils import timezone

from ai_assistant.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


class PPAAnomalyDetector:
    """
    Detect anomalies in PPA performance using ML and AI.

    Features:
    - Budget anomaly detection (overruns, underspending)
    - Timeline delay detection
    - AI-powered recommendations
    - Severity scoring
    """

    # Thresholds
    BUDGET_DEVIATION_MEDIUM = 0.15  # 15%
    BUDGET_DEVIATION_HIGH = 0.25    # 25%
    BUDGET_DEVIATION_CRITICAL = 0.40  # 40%

    TIMELINE_DELAY_MEDIUM = 7   # days
    TIMELINE_DELAY_HIGH = 14    # days
    TIMELINE_DELAY_CRITICAL = 30  # days

    def __init__(self):
        """Initialize anomaly detector with AI service."""
        self.gemini = GeminiService(temperature=0.4)
        logger.info("PPAAnomalyDetector initialized")

    def detect_budget_anomalies(self, ppa_id: Optional[int] = None) -> List[Dict]:
        """
        Detect budget overruns and underspending anomalies.

        Args:
            ppa_id: Optional PPA ID to analyze (None = all ongoing PPAs)

        Returns:
            List of anomaly dictionaries with details and recommendations
        """
        from monitoring.models import MonitoringEntry

        # Get PPAs to analyze
        if ppa_id:
            ppas = MonitoringEntry.objects.filter(id=ppa_id)
        else:
            ppas = MonitoringEntry.objects.filter(
                status__in=['planning', 'ongoing']
            ).exclude(
                budget_allocation=0
            )

        # Fetch with funding totals
        ppas = ppas.with_funding_totals()

        anomalies = []

        for ppa in ppas:
            try:
                anomaly = self._check_budget_anomaly(ppa)
                if anomaly:
                    anomalies.append(anomaly)
            except Exception as e:
                logger.error(
                    f"Error checking budget anomaly for PPA {ppa.id}: {e}",
                    exc_info=True
                )

        # Sort by deviation (highest first)
        anomalies.sort(key=lambda x: x['deviation'], reverse=True)

        logger.info(f"Detected {len(anomalies)} budget anomalies")
        return anomalies

    def _check_budget_anomaly(self, ppa) -> Optional[Dict]:
        """
        Check individual PPA for budget anomaly.

        Returns:
            Anomaly dict if found, None otherwise
        """
        # Calculate budget utilization
        budget_allocation = float(ppa.budget_allocation or 0)
        if budget_allocation == 0:
            return None

        # Use disbursements as actual spending
        actual_spending = float(ppa.total_disbursements_sum or 0)
        budget_util = actual_spending / budget_allocation if budget_allocation > 0 else 0

        # Calculate timeline progress
        timeline_progress = self._calculate_timeline_progress(ppa)

        # Calculate deviation
        deviation = abs(budget_util - timeline_progress)

        # Check if deviation exceeds threshold
        if deviation < self.BUDGET_DEVIATION_MEDIUM:
            return None  # No significant anomaly

        # Determine anomaly type
        anomaly_type = 'budget_overrun' if budget_util > timeline_progress else 'underspending'

        # Determine severity
        severity = self._calculate_severity(deviation)

        # Generate alert message
        alert_message = self._generate_budget_alert_message(
            ppa, budget_util, timeline_progress, anomaly_type
        )

        # Get AI recommendations
        recommendations = self._get_ai_budget_recommendations(
            ppa, budget_util, timeline_progress, anomaly_type
        )

        anomaly = {
            'ppa_id': ppa.id,
            'ppa_name': ppa.title,
            'ppa_code': getattr(ppa, 'ppa_code', ''),
            'anomaly_type': anomaly_type,
            'severity': severity,
            'current_utilization': round(budget_util, 3),
            'expected_utilization': round(timeline_progress, 3),
            'deviation': round(deviation, 3),
            'budget_allocation': budget_allocation,
            'actual_spending': actual_spending,
            'alert_message': alert_message,
            'recommendations': recommendations,
            'detected_at': timezone.now().isoformat(),
        }

        return anomaly

    def detect_timeline_delays(self, ppa_id: Optional[int] = None) -> List[Dict]:
        """
        Detect projects likely to miss deadlines.

        Args:
            ppa_id: Optional PPA ID to analyze (None = all ongoing PPAs)

        Returns:
            List of delay predictions with recommendations
        """
        from monitoring.models import MonitoringEntry

        # Get PPAs to analyze
        if ppa_id:
            ppas = MonitoringEntry.objects.filter(id=ppa_id)
        else:
            ppas = MonitoringEntry.objects.filter(
                status__in=['planning', 'ongoing']
            ).exclude(
                target_completion__isnull=True
            )

        delays = []

        for ppa in ppas:
            try:
                delay = self._check_timeline_delay(ppa)
                if delay:
                    delays.append(delay)
            except Exception as e:
                logger.error(
                    f"Error checking timeline delay for PPA {ppa.id}: {e}",
                    exc_info=True
                )

        # Sort by predicted delay (highest first)
        delays.sort(key=lambda x: x['predicted_delay_days'], reverse=True)

        logger.info(f"Detected {len(delays)} timeline delays")
        return delays

    def _check_timeline_delay(self, ppa) -> Optional[Dict]:
        """
        Check individual PPA for timeline delay.

        Returns:
            Delay dict if found, None otherwise
        """
        if not ppa.target_completion:
            return None

        # Calculate timeline metrics
        days_total = (ppa.target_completion - ppa.start_date).days if ppa.start_date else 0
        if days_total <= 0:
            return None

        days_elapsed = (date.today() - ppa.start_date).days if ppa.start_date else 0
        timeline_progress = min(days_elapsed / days_total, 1.0) if days_total > 0 else 0

        # Get actual progress (from completion percentage or milestones)
        actual_progress = self._get_actual_progress(ppa)

        # Calculate progress gap
        progress_gap = timeline_progress - actual_progress

        # Predict delay
        if actual_progress > 0 and actual_progress < 1.0:
            # Predicted days to complete based on current rate
            predicted_total_days = days_elapsed / actual_progress
            predicted_delay_days = predicted_total_days - days_total
        else:
            # Cannot predict
            return None

        # Check if delay is significant
        if predicted_delay_days < self.TIMELINE_DELAY_MEDIUM:
            return None

        # Determine severity
        if predicted_delay_days >= self.TIMELINE_DELAY_CRITICAL:
            severity = 'CRITICAL'
        elif predicted_delay_days >= self.TIMELINE_DELAY_HIGH:
            severity = 'HIGH'
        else:
            severity = 'MEDIUM'

        # Generate recommendations
        recommendations = self._get_ai_timeline_recommendations(
            ppa, actual_progress, timeline_progress, predicted_delay_days
        )

        delay = {
            'ppa_id': ppa.id,
            'ppa_name': ppa.title,
            'ppa_code': getattr(ppa, 'ppa_code', ''),
            'predicted_delay_days': int(predicted_delay_days),
            'current_progress': round(actual_progress, 3),
            'expected_progress': round(timeline_progress, 3),
            'progress_gap': round(progress_gap, 3),
            'severity': severity,
            'target_completion': ppa.target_completion.isoformat(),
            'predicted_completion': (
                ppa.start_date + timedelta(days=int(days_elapsed / actual_progress))
            ).isoformat() if ppa.start_date and actual_progress > 0 else None,
            'recommendations': recommendations,
            'detected_at': timezone.now().isoformat(),
        }

        return delay

    def _calculate_timeline_progress(self, ppa) -> float:
        """
        Calculate timeline progress (0.0 to 1.0).

        Based on days elapsed vs total days.
        """
        if not ppa.start_date or not ppa.target_completion:
            return 0.0

        total_days = (ppa.target_completion - ppa.start_date).days
        if total_days <= 0:
            return 0.0

        elapsed_days = (date.today() - ppa.start_date).days

        # Progress is capped at 1.0 (100%)
        return min(max(elapsed_days / total_days, 0.0), 1.0)

    def _get_actual_progress(self, ppa) -> float:
        """
        Get actual project progress (0.0 to 1.0).

        Uses various indicators:
        - Milestone completion
        - Deliverables completed
        - Status field if available
        """
        # Try to get progress from milestones
        milestones = getattr(ppa, 'milestones', None)
        if milestones and milestones.exists():
            total = milestones.count()
            completed = milestones.filter(status='completed').count()
            if total > 0:
                return completed / total

        # Fallback: Use status as rough estimate
        if ppa.status == 'completed':
            return 1.0
        elif ppa.status == 'ongoing':
            # Assume 50% if no other data
            return 0.5
        elif ppa.status == 'planning':
            return 0.1

        return 0.0

    def _calculate_severity(self, deviation: float) -> str:
        """Calculate severity based on deviation magnitude."""
        if deviation >= self.BUDGET_DEVIATION_CRITICAL:
            return 'CRITICAL'
        elif deviation >= self.BUDGET_DEVIATION_HIGH:
            return 'HIGH'
        elif deviation >= self.BUDGET_DEVIATION_MEDIUM:
            return 'MEDIUM'
        return 'LOW'

    def _generate_budget_alert_message(
        self, ppa, budget_util: float, timeline_progress: float, anomaly_type: str
    ) -> str:
        """Generate human-readable alert message for budget anomaly."""
        if anomaly_type == 'budget_overrun':
            return (
                f"Project '{ppa.title}' has spent {budget_util:.0%} of budget "
                f"but is only {timeline_progress:.0%} through timeline. "
                f"Potential budget overrun risk."
            )
        else:
            return (
                f"Project '{ppa.title}' has only spent {budget_util:.0%} of budget "
                f"despite being {timeline_progress:.0%} through timeline. "
                f"Potential underspending or implementation delay."
            )

    def _get_ai_budget_recommendations(
        self, ppa, budget_util: float, timeline_progress: float, anomaly_type: str
    ) -> List[str]:
        """
        Use AI to generate actionable budget recommendations.

        Returns:
            List of recommendation strings
        """
        prompt = f"""
A government project has a budget anomaly:

Project: {ppa.title}
Sector: {ppa.get_sector_display() if hasattr(ppa, 'get_sector_display') else 'N/A'}
Budget Allocation: ₱{ppa.budget_allocation:,.2f}
Actual Spending: {budget_util:.0%} of budget
Timeline Progress: {timeline_progress:.0%} complete
Anomaly Type: {anomaly_type}
Deviation: {abs(budget_util - timeline_progress):.0%}

Provide 3-5 specific, actionable recommendations to address this budget anomaly.
Focus on practical steps government program managers can take.
Each recommendation should be one concise sentence.

Return ONLY a valid JSON array of strings (no markdown, no extra text):
["Recommendation 1", "Recommendation 2", ...]
"""

        try:
            response = self.gemini.generate_text(
                prompt,
                use_cache=True,
                cache_ttl=86400,  # 24 hours
                include_cultural_context=False
            )

            if response['success']:
                # Parse JSON response
                text = response['text'].strip()
                # Remove markdown code blocks if present
                if text.startswith('```'):
                    text = text.split('```')[1]
                    if text.startswith('json'):
                        text = text[4:]
                    text = text.strip()

                recommendations = json.loads(text)

                if isinstance(recommendations, list):
                    return recommendations[:5]  # Limit to 5

            logger.warning(f"AI recommendation failed: {response.get('error', 'Unknown')}")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI recommendations: {e}")
        except Exception as e:
            logger.error(f"Error getting AI recommendations: {e}")

        # Fallback recommendations
        return self._get_fallback_budget_recommendations(anomaly_type)

    def _get_ai_timeline_recommendations(
        self, ppa, actual_progress: float, timeline_progress: float, delay_days: int
    ) -> List[str]:
        """
        Use AI to generate timeline delay recommendations.

        Returns:
            List of recommendation strings
        """
        prompt = f"""
A government project is predicted to miss its deadline:

Project: {ppa.title}
Sector: {ppa.get_sector_display() if hasattr(ppa, 'get_sector_display') else 'N/A'}
Current Progress: {actual_progress:.0%} complete
Expected Progress: {timeline_progress:.0%} (based on timeline)
Predicted Delay: {delay_days} days
Target Completion: {ppa.target_completion}

Provide 3-5 specific, actionable recommendations to get this project back on track.
Focus on practical steps to accelerate delivery without compromising quality.
Each recommendation should be one concise sentence.

Return ONLY a valid JSON array of strings (no markdown, no extra text):
["Recommendation 1", "Recommendation 2", ...]
"""

        try:
            response = self.gemini.generate_text(
                prompt,
                use_cache=True,
                cache_ttl=86400,
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

            logger.warning(f"AI recommendation failed: {response.get('error', 'Unknown')}")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI recommendations: {e}")
        except Exception as e:
            logger.error(f"Error getting AI recommendations: {e}")

        # Fallback recommendations
        return self._get_fallback_timeline_recommendations(delay_days)

    def _get_fallback_budget_recommendations(self, anomaly_type: str) -> List[str]:
        """Fallback recommendations if AI fails."""
        if anomaly_type == 'budget_overrun':
            return [
                "Review and validate all recent disbursements for accuracy",
                "Conduct urgent budget realignment meeting with implementing team",
                "Assess scope for potential reductions or efficiencies",
                "Request supplemental budget if overrun is unavoidable",
                "Implement weekly spending monitoring until project completion"
            ]
        else:  # underspending
            return [
                "Investigate causes of slow implementation or procurement delays",
                "Review and expedite pending obligations and disbursements",
                "Verify if timeline needs adjustment to match spending rate",
                "Coordinate with implementing agency to accelerate activities",
                "Consider reallocating unused funds to other priority projects"
            ]

    def _get_fallback_timeline_recommendations(self, delay_days: int) -> List[str]:
        """Fallback timeline recommendations if AI fails."""
        if delay_days >= 30:
            return [
                "Conduct emergency project review meeting with all stakeholders",
                "Identify and remove critical path bottlenecks immediately",
                "Consider requesting formal timeline extension if needed",
                "Assess feasibility of adding resources to accelerate delivery",
                "Implement daily progress monitoring until back on track"
            ]
        else:
            return [
                "Review project schedule and identify delayed activities",
                "Coordinate with implementing team to accelerate critical tasks",
                "Remove any administrative or procedural bottlenecks",
                "Consider parallel execution of independent activities",
                "Increase monitoring frequency to weekly status updates"
            ]

    def get_anomaly_summary(self) -> Dict:
        """
        Get summary of all anomalies across all PPAs.

        Returns:
            Dictionary with counts and severity breakdown
        """
        budget_anomalies = self.detect_budget_anomalies()
        timeline_delays = self.detect_timeline_delays()

        # Count by severity
        def count_by_severity(anomalies):
            counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
            for a in anomalies:
                severity = a.get('severity', 'LOW')
                counts[severity] = counts.get(severity, 0) + 1
            return counts

        summary = {
            'total_budget_anomalies': len(budget_anomalies),
            'total_timeline_delays': len(timeline_delays),
            'budget_anomalies_by_severity': count_by_severity(budget_anomalies),
            'timeline_delays_by_severity': count_by_severity(timeline_delays),
            'critical_count': (
                sum(1 for a in budget_anomalies if a.get('severity') == 'CRITICAL') +
                sum(1 for a in timeline_delays if a.get('severity') == 'CRITICAL')
            ),
            'generated_at': timezone.now().isoformat(),
        }

        return summary
