"""
Performance Forecasting Service

Forecasts PPA outcomes using time series analysis and AI:
- Completion date predictions
- Budget utilization forecasts
- Success probability estimation
- Risk factor identification

Uses historical progress data and AI-powered factor analysis.
"""

import json
import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from django.db.models import Avg, Q
from django.utils import timezone

from ai_assistant.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


class PerformanceForecaster:
    """
    Forecast PPA outcomes using time series and AI.

    Features:
    - Completion date prediction
    - Budget utilization forecast
    - Success probability estimation
    - AI-powered factor analysis
    """

    # Confidence thresholds
    HIGH_CONFIDENCE = 0.8
    MEDIUM_CONFIDENCE = 0.6

    def __init__(self):
        """Initialize forecaster with AI service."""
        self.gemini = GeminiService(temperature=0.3)
        logger.info("PerformanceForecaster initialized")

    def forecast_completion_date(self, ppa_id: int) -> Dict:
        """
        Predict actual completion date based on current progress.

        Args:
            ppa_id: PPA ID to forecast

        Returns:
            Dictionary containing:
            - predicted_completion: Predicted completion date
            - planned_completion: Original target date
            - delay_days: Expected delay in days (0 if on time)
            - confidence: Confidence level (0-1)
            - factors: List of factors affecting timeline
            - velocity: Current progress velocity
        """
        from monitoring.models import MonitoringEntry

        try:
            ppa = MonitoringEntry.objects.get(id=ppa_id)
        except MonitoringEntry.DoesNotExist:
            return {'error': f'PPA {ppa_id} not found'}

        # Check if we have enough data to forecast
        if not ppa.start_date or not ppa.target_completion:
            return {
                'error': 'Insufficient data: PPA missing start date or target completion date'
            }

        # Calculate current progress
        actual_progress = self._get_actual_progress(ppa)

        # Calculate historical progress rate (velocity)
        velocity = self._calculate_velocity(ppa, actual_progress)

        # Predict completion date
        if velocity > 0 and actual_progress < 1.0:
            # Days needed to complete remaining work
            remaining_progress = 1.0 - actual_progress
            days_to_complete = remaining_progress / velocity

            predicted_completion = date.today() + timedelta(days=days_to_complete)
        elif actual_progress >= 1.0:
            # Already complete
            predicted_completion = date.today()
        else:
            # Cannot predict (no progress)
            predicted_completion = None

        # Calculate delay
        if predicted_completion and ppa.target_completion:
            delay_days = (predicted_completion - ppa.target_completion).days
        else:
            delay_days = None

        # Calculate confidence
        confidence = self._calculate_forecast_confidence(ppa, actual_progress, velocity)

        # AI-powered factor analysis
        factors = self._analyze_timeline_factors(ppa, actual_progress, velocity, delay_days)

        forecast = {
            'ppa_id': ppa.id,
            'ppa_name': ppa.title,
            'predicted_completion': predicted_completion.isoformat() if predicted_completion else None,
            'planned_completion': ppa.target_completion.isoformat(),
            'delay_days': max(0, delay_days) if delay_days else 0,
            'is_on_time': delay_days is not None and delay_days <= 0,
            'current_progress': round(actual_progress, 3),
            'velocity': round(velocity, 5),  # Progress per day
            'confidence': round(confidence, 2),
            'confidence_level': self._get_confidence_level(confidence),
            'factors': factors,
            'forecast_date': date.today().isoformat(),
        }

        logger.info(
            f"Forecasted completion for PPA {ppa_id}: "
            f"{predicted_completion} (delay: {delay_days} days)"
        )

        return forecast

    def forecast_budget_utilization(self, ppa_id: int) -> Dict:
        """
        Forecast final budget utilization at project completion.

        Args:
            ppa_id: PPA ID to forecast

        Returns:
            Dictionary containing:
            - predicted_total_spending: Predicted final spending
            - budget_allocation: Original budget
            - variance: Expected over/under spending
            - variance_percent: Variance as percentage
            - confidence: Confidence level
            - spending_trend: Current spending pattern
        """
        from monitoring.models import MonitoringEntry

        try:
            ppa = MonitoringEntry.objects.with_funding_totals().get(id=ppa_id)
        except MonitoringEntry.DoesNotExist:
            return {'error': f'PPA {ppa_id} not found'}

        if not ppa.budget_allocation or ppa.budget_allocation == 0:
            return {'error': 'PPA has no budget allocation'}

        # Get current metrics
        current_spending = float(ppa.total_disbursements_sum or 0)
        budget_allocation = float(ppa.budget_allocation)
        actual_progress = self._get_actual_progress(ppa)

        # Calculate spending rate
        if actual_progress > 0:
            spending_rate = current_spending / actual_progress
        else:
            spending_rate = 0

        # Forecast final spending
        if actual_progress < 1.0 and spending_rate > 0:
            predicted_total_spending = spending_rate * 1.0  # 100% complete
        else:
            predicted_total_spending = current_spending

        # Calculate variance
        variance = predicted_total_spending - budget_allocation
        variance_percent = (variance / budget_allocation * 100) if budget_allocation > 0 else 0

        # Determine spending trend
        spending_trend = self._analyze_spending_trend(
            current_spending, budget_allocation, actual_progress
        )

        # Calculate confidence
        confidence = self._calculate_budget_forecast_confidence(
            ppa, actual_progress, current_spending
        )

        forecast = {
            'ppa_id': ppa.id,
            'ppa_name': ppa.title,
            'predicted_total_spending': round(predicted_total_spending, 2),
            'budget_allocation': budget_allocation,
            'current_spending': current_spending,
            'variance': round(variance, 2),
            'variance_percent': round(variance_percent, 2),
            'is_within_budget': variance <= 0,
            'current_progress': round(actual_progress, 3),
            'spending_rate': round(spending_rate, 2),
            'spending_trend': spending_trend,
            'confidence': round(confidence, 2),
            'confidence_level': self._get_confidence_level(confidence),
            'forecast_date': date.today().isoformat(),
        }

        logger.info(
            f"Forecasted budget for PPA {ppa_id}: "
            f"₱{predicted_total_spending:,.2f} (variance: {variance_percent:.1f}%)"
        )

        return forecast

    def estimate_success_probability(self, ppa_id: int) -> Dict:
        """
        Estimate probability of successful project completion.

        Args:
            ppa_id: PPA ID to analyze

        Returns:
            Dictionary containing:
            - success_probability: Overall success probability (0-1)
            - risk_factors: List of identified risks
            - success_factors: Positive indicators
            - overall_assessment: AI-generated assessment
        """
        from monitoring.models import MonitoringEntry

        try:
            ppa = MonitoringEntry.objects.with_funding_totals().get(id=ppa_id)
        except MonitoringEntry.DoesNotExist:
            return {'error': f'PPA {ppa_id} not found'}

        # Get forecasts
        timeline_forecast = self.forecast_completion_date(ppa_id)
        budget_forecast = self.forecast_budget_utilization(ppa_id)

        # Calculate component scores
        timeline_score = self._score_timeline_health(timeline_forecast)
        budget_score = self._score_budget_health(budget_forecast)
        status_score = self._score_status_health(ppa)

        # Overall probability (weighted average)
        success_probability = (
            timeline_score * 0.4 +
            budget_score * 0.4 +
            status_score * 0.2
        )

        # Identify factors
        risk_factors = self._identify_risk_factors(ppa, timeline_forecast, budget_forecast)
        success_factors = self._identify_success_factors(ppa, timeline_forecast, budget_forecast)

        # AI assessment
        assessment = self._generate_success_assessment(
            ppa, success_probability, risk_factors, success_factors
        )

        result = {
            'ppa_id': ppa.id,
            'ppa_name': ppa.title,
            'success_probability': round(success_probability, 2),
            'success_rating': self._get_success_rating(success_probability),
            'timeline_score': round(timeline_score, 2),
            'budget_score': round(budget_score, 2),
            'status_score': round(status_score, 2),
            'risk_factors': risk_factors,
            'success_factors': success_factors,
            'overall_assessment': assessment,
            'forecast_date': date.today().isoformat(),
        }

        logger.info(
            f"Success probability for PPA {ppa_id}: {success_probability:.0%}"
        )

        return result

    def _get_actual_progress(self, ppa) -> float:
        """
        Get actual project progress (0.0 to 1.0).

        Uses milestones if available, otherwise estimates from status.
        """
        # Try milestones first
        milestones = getattr(ppa, 'milestones', None)
        if milestones and milestones.exists():
            total = milestones.count()
            completed = milestones.filter(status='completed').count()
            if total > 0:
                return completed / total

        # Fallback to status-based estimate
        if ppa.status == 'completed':
            return 1.0
        elif ppa.status == 'ongoing':
            # Estimate based on timeline
            if ppa.start_date and ppa.target_completion:
                total_days = (ppa.target_completion - ppa.start_date).days
                elapsed_days = (date.today() - ppa.start_date).days
                if total_days > 0:
                    return min(max(elapsed_days / total_days, 0.0), 0.9)  # Cap at 90%
            return 0.5  # Default midpoint
        elif ppa.status == 'planning':
            return 0.1

        return 0.0

    def _calculate_velocity(self, ppa, actual_progress: float) -> float:
        """
        Calculate progress velocity (progress per day).

        Returns:
            Progress per day (e.g., 0.01 = 1% per day)
        """
        if not ppa.start_date:
            return 0.0

        days_elapsed = (date.today() - ppa.start_date).days

        if days_elapsed > 0:
            return actual_progress / days_elapsed

        return 0.0

    def _calculate_forecast_confidence(
        self, ppa, actual_progress: float, velocity: float
    ) -> float:
        """
        Calculate confidence in the forecast (0.0 to 1.0).

        Higher confidence when:
        - More progress has been made
        - Consistent velocity
        - Clear start/end dates
        """
        confidence = 0.5  # Base confidence

        # More progress = higher confidence
        if actual_progress > 0.7:
            confidence += 0.3
        elif actual_progress > 0.4:
            confidence += 0.2
        elif actual_progress > 0.2:
            confidence += 0.1

        # Positive velocity increases confidence
        if velocity > 0:
            confidence += 0.1

        # Clear dates increase confidence
        if ppa.start_date and ppa.target_completion:
            confidence += 0.1

        return min(confidence, 1.0)

    def _calculate_budget_forecast_confidence(
        self, ppa, actual_progress: float, current_spending: float
    ) -> float:
        """Calculate confidence in budget forecast."""
        confidence = 0.5

        # More progress = better forecast
        if actual_progress > 0.6:
            confidence += 0.3
        elif actual_progress > 0.3:
            confidence += 0.2

        # Some spending has occurred
        if current_spending > 0:
            confidence += 0.2

        return min(confidence, 1.0)

    def _get_confidence_level(self, confidence: float) -> str:
        """Convert confidence score to level."""
        if confidence >= self.HIGH_CONFIDENCE:
            return 'HIGH'
        elif confidence >= self.MEDIUM_CONFIDENCE:
            return 'MEDIUM'
        return 'LOW'

    def _analyze_timeline_factors(
        self, ppa, actual_progress: float, velocity: float, delay_days: Optional[int]
    ) -> List[str]:
        """
        Analyze factors affecting timeline using AI.

        Returns:
            List of factor descriptions
        """
        prompt = f"""
Analyze timeline factors for this government project:

- Project: {ppa.title}
- Current Progress: {actual_progress:.0%}
- Progress Velocity: {velocity:.3f} per day
- Predicted Delay: {delay_days or 0} days
- Status: {ppa.status}

Identify 3-4 key factors affecting the timeline (positive or negative).
Be specific and concise (one sentence each).

Return ONLY valid JSON array (no markdown):
["Factor 1", "Factor 2", ...]
"""

        try:
            response = self.gemini.generate_text(
                prompt,
                use_cache=True,
                cache_ttl=3600,  # 1 hour
                include_cultural_context=False
            )

            if response['success']:
                text = response['text'].strip()
                if text.startswith('```'):
                    text = text.split('```')[1]
                    if text.startswith('json'):
                        text = text[4:]
                    text = text.strip()

                factors = json.loads(text)
                if isinstance(factors, list):
                    return factors[:4]

        except Exception as e:
            logger.warning(f"AI factor analysis failed: {e}")

        # Fallback factors
        factors = []
        if delay_days and delay_days > 0:
            factors.append(f"Current trajectory indicates {delay_days}-day delay")
        if velocity < 0.01:
            factors.append("Low progress velocity suggests implementation challenges")
        if actual_progress > 0.5:
            factors.append("Project past midpoint with measurable progress")

        return factors or ["Insufficient data for detailed factor analysis"]

    def _analyze_spending_trend(
        self, current_spending: float, budget: float, progress: float
    ) -> str:
        """Analyze spending trend pattern."""
        if progress == 0:
            return "No progress yet"

        spending_ratio = current_spending / budget if budget > 0 else 0

        if spending_ratio > progress + 0.15:
            return "Accelerating (spending faster than progress)"
        elif spending_ratio < progress - 0.15:
            return "Decelerating (spending slower than progress)"
        else:
            return "Steady (aligned with progress)"

    def _score_timeline_health(self, timeline_forecast: Dict) -> float:
        """Score timeline health (0-1)."""
        if 'error' in timeline_forecast:
            return 0.5

        delay_days = timeline_forecast.get('delay_days', 0)

        if delay_days <= 0:
            return 1.0  # On time or early
        elif delay_days <= 7:
            return 0.8  # Slight delay
        elif delay_days <= 14:
            return 0.6  # Moderate delay
        elif delay_days <= 30:
            return 0.4  # Significant delay
        else:
            return 0.2  # Critical delay

    def _score_budget_health(self, budget_forecast: Dict) -> float:
        """Score budget health (0-1)."""
        if 'error' in budget_forecast:
            return 0.5

        variance_percent = budget_forecast.get('variance_percent', 0)

        if variance_percent <= 0:
            return 1.0  # Under budget
        elif variance_percent <= 5:
            return 0.9  # Slight overrun
        elif variance_percent <= 10:
            return 0.7  # Moderate overrun
        elif variance_percent <= 20:
            return 0.5  # Significant overrun
        else:
            return 0.3  # Critical overrun

    def _score_status_health(self, ppa) -> float:
        """Score based on current status."""
        status_scores = {
            'completed': 1.0,
            'ongoing': 0.7,
            'planning': 0.5,
            'on_hold': 0.2,
        }
        return status_scores.get(ppa.status, 0.5)

    def _identify_risk_factors(self, ppa, timeline_forecast, budget_forecast) -> List[str]:
        """Identify risk factors threatening success."""
        risks = []

        # Timeline risks
        if timeline_forecast.get('delay_days', 0) > 14:
            risks.append(f"Significant timeline delay ({timeline_forecast['delay_days']} days)")

        # Budget risks
        if budget_forecast.get('variance_percent', 0) > 10:
            risks.append(f"Budget overrun risk ({budget_forecast['variance_percent']:.1f}%)")

        # Status risks
        if ppa.status == 'on_hold':
            risks.append("Project currently on hold")

        # Low confidence
        if timeline_forecast.get('confidence', 1) < 0.5:
            risks.append("Low forecast confidence due to limited progress data")

        return risks or ["No significant risks identified"]

    def _identify_success_factors(self, ppa, timeline_forecast, budget_forecast) -> List[str]:
        """Identify positive success factors."""
        factors = []

        # Timeline success
        if timeline_forecast.get('is_on_time'):
            factors.append("Project on track for timely completion")

        # Budget success
        if budget_forecast.get('is_within_budget'):
            factors.append("Budget utilization within planned allocation")

        # Progress
        if timeline_forecast.get('current_progress', 0) > 0.6:
            factors.append("Strong progress momentum (>60% complete)")

        # Velocity
        if timeline_forecast.get('velocity', 0) > 0.01:
            factors.append("Positive progress velocity")

        return factors or ["Project in early stages"]

    def _generate_success_assessment(
        self, ppa, success_probability: float, risk_factors: List, success_factors: List
    ) -> str:
        """Generate AI-powered success assessment."""
        return (
            f"Project has a {success_probability:.0%} probability of successful completion. "
            f"{'Strong indicators include: ' + ', '.join(success_factors[:2]) + '.' if success_factors else ''} "
            f"{'Key risks: ' + ', '.join(risk_factors[:2]) + '.' if risk_factors else ''}"
        )

    def _get_success_rating(self, probability: float) -> str:
        """Convert probability to rating."""
        if probability >= 0.8:
            return 'EXCELLENT'
        elif probability >= 0.65:
            return 'GOOD'
        elif probability >= 0.5:
            return 'FAIR'
        else:
            return 'AT RISK'
