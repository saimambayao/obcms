"""
Cost Tracker - Track and report AI API costs.

This module provides:
- Real-time cost tracking
- Daily/monthly cost reports
- Budget alerts
- Cost optimization suggestions
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from django.core.cache import cache
from django.db.models import Sum
from django.utils import timezone

logger = logging.getLogger(__name__)


class CostTracker:
    """
    Track and manage AI API costs.

    Features:
    - Real-time cost accumulation
    - Daily/monthly aggregation
    - Budget monitoring
    - Cost optimization insights
    """

    # Gemini Pro pricing (per 1K tokens)
    GEMINI_PRO_INPUT_COST = Decimal('0.00025')
    GEMINI_PRO_OUTPUT_COST = Decimal('0.00075')

    # Cache keys
    CACHE_KEY_DAILY_COST = "ai_cost:daily:{date}"
    CACHE_KEY_MONTHLY_COST = "ai_cost:monthly:{year}_{month}"

    def __init__(self):
        """Initialize cost tracker."""
        self.logger = logging.getLogger(__name__)

    def track_operation(
        self,
        operation_type: str,
        tokens_used: int,
        model: str = 'gemini-1.5-pro',
        user_id: Optional[int] = None,
        module: str = 'general'
    ) -> Decimal:
        """
        Track cost of an AI operation.

        Args:
            operation_type: Type of operation (e.g., 'chat', 'analysis')
            tokens_used: Total tokens used
            model: AI model used
            user_id: Optional user ID
            module: OBCMS module (e.g., 'mana', 'coordination')

        Returns:
            Decimal: Cost of operation
        """
        # Calculate cost based on model
        cost = self._calculate_cost(tokens_used, model)

        # Update daily cache
        self._update_daily_cost(cost)

        # Update monthly cache
        self._update_monthly_cost(cost)

        # Log to database (done in service layer)
        self.logger.info(
            f"AI Cost: ${cost:.6f} | Operation: {operation_type} | "
            f"Tokens: {tokens_used} | Model: {model} | Module: {module}"
        )

        return cost

    def _calculate_cost(self, tokens_used: int, model: str) -> Decimal:
        """Calculate cost based on token usage and model."""
        # Assume 60/40 split input/output
        input_tokens = int(tokens_used * 0.6)
        output_tokens = int(tokens_used * 0.4)

        if 'gemini' in model.lower():
            input_cost = (input_tokens / 1000) * self.GEMINI_PRO_INPUT_COST
            output_cost = (output_tokens / 1000) * self.GEMINI_PRO_OUTPUT_COST
            return input_cost + output_cost
        else:
            # Default fallback
            return Decimal('0.001') * tokens_used

    def _update_daily_cost(self, cost: Decimal):
        """Update daily cost in cache."""
        today = timezone.now().date()
        cache_key = self.CACHE_KEY_DAILY_COST.format(date=today)

        current_cost = cache.get(cache_key, Decimal('0'))
        new_cost = current_cost + cost

        # Store for 48 hours
        cache.set(cache_key, new_cost, 60 * 60 * 48)

    def _update_monthly_cost(self, cost: Decimal):
        """Update monthly cost in cache."""
        now = timezone.now()
        cache_key = self.CACHE_KEY_MONTHLY_COST.format(
            year=now.year,
            month=now.month
        )

        current_cost = cache.get(cache_key, Decimal('0'))
        new_cost = current_cost + cost

        # Store for 60 days
        cache.set(cache_key, new_cost, 60 * 60 * 24 * 60)

    def get_daily_cost(self, date: Optional[datetime] = None) -> Decimal:
        """Get total cost for a specific day."""
        if date is None:
            date = timezone.now().date()

        cache_key = self.CACHE_KEY_DAILY_COST.format(date=date)
        return cache.get(cache_key, Decimal('0'))

    def get_monthly_cost(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> Decimal:
        """Get total cost for a specific month."""
        now = timezone.now()
        year = year or now.year
        month = month or now.month

        cache_key = self.CACHE_KEY_MONTHLY_COST.format(
            year=year,
            month=month
        )
        return cache.get(cache_key, Decimal('0'))

    def get_cost_breakdown(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Decimal]:
        """
        Get cost breakdown by module/operation type.

        Note: This requires querying AIOperation model.
        Returns cached daily costs for now.
        """
        breakdown = {}
        current_date = start_date.date()
        end = end_date.date()

        while current_date <= end:
            daily_cost = self.get_daily_cost(current_date)
            breakdown[str(current_date)] = daily_cost
            current_date += timedelta(days=1)

        return breakdown

    def check_budget_alert(
        self,
        daily_budget: Decimal,
        monthly_budget: Decimal
    ) -> Dict[str, any]:
        """
        Check if costs exceed budget thresholds.

        Args:
            daily_budget: Daily budget limit
            monthly_budget: Monthly budget limit

        Returns:
            Dict with alert information
        """
        daily_cost = self.get_daily_cost()
        monthly_cost = self.get_monthly_cost()

        alerts = []

        # Daily budget check
        daily_usage_pct = (daily_cost / daily_budget * 100) if daily_budget > 0 else 0
        if daily_usage_pct >= 90:
            alerts.append({
                'type': 'daily',
                'severity': 'critical',
                'message': f'Daily budget at {daily_usage_pct:.1f}% (${daily_cost:.2f}/${daily_budget:.2f})'
            })
        elif daily_usage_pct >= 75:
            alerts.append({
                'type': 'daily',
                'severity': 'warning',
                'message': f'Daily budget at {daily_usage_pct:.1f}% (${daily_cost:.2f}/${daily_budget:.2f})'
            })

        # Monthly budget check
        monthly_usage_pct = (monthly_cost / monthly_budget * 100) if monthly_budget > 0 else 0
        if monthly_usage_pct >= 90:
            alerts.append({
                'type': 'monthly',
                'severity': 'critical',
                'message': f'Monthly budget at {monthly_usage_pct:.1f}% (${monthly_cost:.2f}/${monthly_budget:.2f})'
            })
        elif monthly_usage_pct >= 75:
            alerts.append({
                'type': 'monthly',
                'severity': 'warning',
                'message': f'Monthly budget at {monthly_usage_pct:.1f}% (${monthly_cost:.2f}/${monthly_budget:.2f})'
            })

        return {
            'has_alerts': len(alerts) > 0,
            'alerts': alerts,
            'daily_cost': float(daily_cost),
            'monthly_cost': float(monthly_cost),
            'daily_usage_pct': float(daily_usage_pct),
            'monthly_usage_pct': float(monthly_usage_pct),
        }

    def get_optimization_suggestions(self) -> List[str]:
        """Get cost optimization suggestions."""
        suggestions = [
            "Enable response caching to reduce duplicate API calls (target: 80%+ cache hit rate)",
            "Use shorter prompts where possible to reduce token usage",
            "Consider using gemini-1.5-flash for simple queries (lower cost)",
            "Batch similar operations to optimize API usage",
            "Review and remove unnecessary cultural context for non-sensitive operations",
            "Set appropriate cache TTLs (24h for analysis, 7d for static content)",
        ]

        # Calculate current daily cost
        daily_cost = self.get_daily_cost()

        if daily_cost > Decimal('10'):
            suggestions.insert(0, "⚠️ URGENT: Daily cost exceeds $10. Review high-cost operations immediately.")
        elif daily_cost > Decimal('5'):
            suggestions.insert(0, "⚠️ WARNING: Daily cost exceeds $5. Consider optimization.")

        return suggestions


class DailyCostReport:
    """Generate daily cost reports."""

    def __init__(self, date: Optional[datetime] = None):
        """
        Initialize daily cost report.

        Args:
            date: Date for report (default: today)
        """
        self.date = date or timezone.now()
        self.cost_tracker = CostTracker()

    def generate(self) -> Dict[str, any]:
        """
        Generate comprehensive daily cost report.

        Returns:
            Dict with report data
        """
        daily_cost = self.cost_tracker.get_daily_cost(self.date.date())

        # Get last 7 days for trend
        last_7_days = []
        for i in range(7):
            day = self.date.date() - timedelta(days=i)
            cost = self.cost_tracker.get_daily_cost(day)
            last_7_days.append({
                'date': str(day),
                'cost': float(cost)
            })

        last_7_days.reverse()

        # Calculate average
        avg_cost = sum(d['cost'] for d in last_7_days) / 7

        return {
            'date': str(self.date.date()),
            'total_cost': float(daily_cost),
            'average_daily_cost_7d': float(avg_cost),
            'trend': 'increasing' if daily_cost > Decimal(str(avg_cost)) else 'decreasing',
            'last_7_days': last_7_days,
            'optimization_suggestions': self.cost_tracker.get_optimization_suggestions(),
            'generated_at': timezone.now().isoformat(),
        }

    def format_report(self) -> str:
        """Format report as readable text."""
        report = self.generate()

        text = f"""
AI COST DAILY REPORT - {report['date']}
{'=' * 50}

SUMMARY:
- Daily Cost: ${report['total_cost']:.2f}
- 7-Day Average: ${report['average_daily_cost_7d']:.2f}
- Trend: {report['trend'].upper()}

LAST 7 DAYS:
"""
        for day in report['last_7_days']:
            text += f"  {day['date']}: ${day['cost']:.2f}\n"

        text += f"\nOPTIMIZATION SUGGESTIONS:\n"
        for i, suggestion in enumerate(report['optimization_suggestions'], 1):
            text += f"  {i}. {suggestion}\n"

        text += f"\n{'=' * 50}\n"
        text += f"Generated at: {report['generated_at']}\n"

        return text
