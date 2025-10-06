"""
M&E Report Generator Service

Auto-generates comprehensive M&E reports for PPAs:
- Quarterly reports
- Monthly reports
- Annual reports
- Custom period reports

Uses AI (Gemini) to create professional narrative summaries.
"""

import json
import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone

from ai_assistant.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


class MEReportGenerator:
    """
    Auto-generate M&E reports for PPAs using AI.

    Features:
    - Quarterly/monthly/annual reports
    - Executive summaries
    - Performance analysis
    - Budget analysis
    - AI-generated narratives
    """

    def __init__(self):
        """Initialize report generator with AI service."""
        self.gemini = GeminiService(temperature=0.5)
        logger.info("MEReportGenerator initialized")

    def generate_quarterly_report(
        self,
        quarter: str,
        year: int,
        ministry: Optional[str] = None
    ) -> Dict:
        """
        Generate comprehensive quarterly M&E report.

        Args:
            quarter: 'Q1', 'Q2', 'Q3', 'Q4'
            year: Fiscal year (e.g., 2025)
            ministry: Filter by ministry/organization (optional)

        Returns:
            Dictionary containing:
            - executive_summary: AI-generated summary
            - performance_overview: Metrics and analysis
            - budget_analysis: Financial performance
            - key_achievements: Top performing projects
            - challenges: Issues identified
            - recommendations: Action items
            - statistics: Aggregate data
        """
        logger.info(f"Generating quarterly report for {quarter} {year}")

        # Get date range for quarter
        start_date, end_date = self._get_quarter_dates(quarter, year)

        # Get PPAs for period
        ppas = self._get_ppas_for_period(start_date, end_date, ministry)

        # Calculate statistics
        stats = self._calculate_quarterly_statistics(ppas, start_date, end_date)

        # Get top performers and underperformers
        top_projects = self._get_top_projects(ppas, limit=5)
        underperforming = self._get_underperforming_projects(ppas, limit=5)

        # Identify challenges
        challenges = self._identify_challenges(ppas, stats)

        # Generate AI narrative sections
        executive_summary = self._generate_executive_summary(
            quarter, year, stats, top_projects, challenges
        )

        performance_overview = self._generate_performance_overview(
            stats, top_projects, underperforming
        )

        budget_analysis = self._generate_budget_analysis(stats)

        recommendations = self._generate_recommendations(
            stats, challenges, underperforming
        )

        report = {
            'report_type': 'quarterly',
            'period': f'{quarter} {year}',
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'ministry': ministry or 'All Ministries',
            'executive_summary': executive_summary,
            'performance_overview': performance_overview,
            'budget_analysis': budget_analysis,
            'key_achievements': [
                {
                    'ppa_name': p.title,
                    'achievement': self._get_achievement_description(p)
                }
                for p in top_projects
            ],
            'challenges': challenges,
            'recommendations': recommendations,
            'statistics': stats,
            'generated_at': timezone.now().isoformat(),
        }

        logger.info(f"Quarterly report generated successfully for {quarter} {year}")
        return report

    def generate_monthly_report(
        self,
        year: int,
        month: int,
        ministry: Optional[str] = None
    ) -> Dict:
        """
        Generate monthly M&E report.

        Args:
            year: Year (e.g., 2025)
            month: Month (1-12)
            ministry: Filter by ministry (optional)

        Returns:
            Monthly report dictionary
        """
        logger.info(f"Generating monthly report for {year}-{month:02d}")

        # Get date range
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        # Get PPAs
        ppas = self._get_ppas_for_period(start_date, end_date, ministry)

        # Calculate statistics
        stats = self._calculate_monthly_statistics(ppas, start_date, end_date)

        # Generate AI summary
        month_name = start_date.strftime('%B')
        summary = self._generate_monthly_summary(month_name, year, stats)

        report = {
            'report_type': 'monthly',
            'period': f'{month_name} {year}',
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'ministry': ministry or 'All Ministries',
            'summary': summary,
            'statistics': stats,
            'generated_at': timezone.now().isoformat(),
        }

        logger.info(f"Monthly report generated for {year}-{month:02d}")
        return report

    def generate_ppa_status_report(self, ppa_id: int) -> str:
        """
        Generate individual PPA status report.

        Args:
            ppa_id: PPA ID

        Returns:
            Markdown-formatted status report
        """
        from monitoring.models import MonitoringEntry

        try:
            ppa = MonitoringEntry.objects.with_funding_totals().get(id=ppa_id)
        except MonitoringEntry.DoesNotExist:
            return f"Error: PPA {ppa_id} not found"

        # Calculate metrics
        timeline_progress = self._calculate_timeline_progress_percent(ppa)
        budget_util = self._calculate_budget_utilization_percent(ppa)

        prompt = f"""
Generate a professional status report for this government project:

**Project Details:**
- Title: {ppa.title}
- Sector: {ppa.get_sector_display() if hasattr(ppa, 'get_sector_display') else 'N/A'}
- Status: {ppa.get_status_display() if hasattr(ppa, 'get_status_display') else ppa.status}
- Budget: ₱{ppa.budget_allocation:,.2f}
- Start Date: {ppa.start_date}
- Target Completion: {ppa.target_completion}

**Performance Metrics:**
- Timeline Progress: {timeline_progress}%
- Budget Utilization: {budget_util}%
- Disbursements: ₱{ppa.total_disbursements_sum or 0:,.2f}

Create a concise status report (200-250 words) with:
1. Current Status (1 paragraph)
2. Key Accomplishments (2-3 bullet points)
3. Challenges (if any, 1-2 bullet points)
4. Next Steps (2-3 bullet points)

Use professional government report style. Return plain text (no JSON).
"""

        try:
            response = self.gemini.generate_text(
                prompt,
                use_cache=False,
                include_cultural_context=False
            )

            if response['success']:
                return response['text']
            else:
                logger.error(f"AI report generation failed: {response.get('error')}")
                return self._generate_fallback_ppa_report(ppa, timeline_progress, budget_util)

        except Exception as e:
            logger.error(f"Error generating PPA report: {e}")
            return self._generate_fallback_ppa_report(ppa, timeline_progress, budget_util)

    def _get_quarter_dates(self, quarter: str, year: int):
        """Get start and end dates for a quarter."""
        quarters = {
            'Q1': (date(year, 1, 1), date(year, 3, 31)),
            'Q2': (date(year, 4, 1), date(year, 6, 30)),
            'Q3': (date(year, 7, 1), date(year, 9, 30)),
            'Q4': (date(year, 10, 1), date(year, 12, 31)),
        }
        return quarters.get(quarter.upper(), quarters['Q1'])

    def _get_ppas_for_period(self, start_date, end_date, ministry=None):
        """Get PPAs active during the period."""
        from monitoring.models import MonitoringEntry

        # PPAs that were active during the period
        ppas = MonitoringEntry.objects.filter(
            Q(start_date__lte=end_date) &
            (Q(target_completion__gte=start_date) | Q(target_completion__isnull=True))
        )

        if ministry:
            ppas = ppas.filter(
                Q(lead_organization__name__icontains=ministry) |
                Q(implementing_moa__name__icontains=ministry)
            )

        return ppas.with_funding_totals()

    def _calculate_quarterly_statistics(self, ppas, start_date, end_date) -> Dict:
        """Calculate aggregate statistics for quarterly report."""
        total_ppas = ppas.count()

        # Status breakdown
        status_counts = {
            'planning': ppas.filter(status='planning').count(),
            'ongoing': ppas.filter(status='ongoing').count(),
            'completed': ppas.filter(status='completed').count(),
            'on_hold': ppas.filter(status='on_hold').count(),
        }

        # Financial metrics
        total_budget = ppas.aggregate(
            total=Sum('budget_allocation')
        )['total'] or Decimal('0')

        total_disbursed = ppas.aggregate(
            total=Sum('total_disbursements_sum')
        )['total'] or Decimal('0')

        # Calculate average budget utilization
        ppas_with_budget = ppas.exclude(budget_allocation=0)
        if ppas_with_budget.exists():
            avg_utilization = sum(
                (float(p.total_disbursements_sum or 0) / float(p.budget_allocation) * 100)
                for p in ppas_with_budget
            ) / ppas_with_budget.count()
        else:
            avg_utilization = 0

        # Sector breakdown
        sector_counts = {}
        for ppa in ppas:
            sector = getattr(ppa, 'sector', 'unknown')
            sector_counts[sector] = sector_counts.get(sector, 0) + 1

        stats = {
            'total_ppas': total_ppas,
            'status_breakdown': status_counts,
            'total_budget': float(total_budget),
            'total_disbursed': float(total_disbursed),
            'disbursement_rate': (
                float(total_disbursed / total_budget * 100)
                if total_budget > 0 else 0
            ),
            'average_budget_utilization': round(avg_utilization, 2),
            'sector_breakdown': sector_counts,
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
        }

        return stats

    def _calculate_monthly_statistics(self, ppas, start_date, end_date) -> Dict:
        """Calculate statistics for monthly report."""
        # Similar to quarterly but more focused on monthly changes
        return self._calculate_quarterly_statistics(ppas, start_date, end_date)

    def _get_top_projects(self, ppas, limit=5):
        """Get top performing projects based on progress and budget utilization."""
        # Score based on: timeline adherence + budget utilization balance
        scored_ppas = []

        for ppa in ppas:
            if not ppa.budget_allocation or ppa.budget_allocation == 0:
                continue

            timeline_progress = self._calculate_timeline_progress_percent(ppa) / 100
            budget_util = self._calculate_budget_utilization_percent(ppa) / 100

            # Ideal: budget utilization ≈ timeline progress
            alignment_score = 1 - abs(budget_util - timeline_progress)

            # Overall score (higher timeline progress is better)
            score = (timeline_progress * 0.6) + (alignment_score * 0.4)

            scored_ppas.append((ppa, score))

        # Sort by score (descending)
        scored_ppas.sort(key=lambda x: x[1], reverse=True)

        return [ppa for ppa, score in scored_ppas[:limit]]

    def _get_underperforming_projects(self, ppas, limit=5):
        """Get underperforming projects."""
        scored_ppas = []

        for ppa in ppas:
            if not ppa.budget_allocation or ppa.budget_allocation == 0:
                continue

            timeline_progress = self._calculate_timeline_progress_percent(ppa) / 100
            budget_util = self._calculate_budget_utilization_percent(ppa) / 100

            # Low timeline progress OR high budget/timeline deviation
            deviation = abs(budget_util - timeline_progress)

            # Lower is worse
            score = timeline_progress - (deviation * 0.5)

            scored_ppas.append((ppa, score))

        # Sort by score (ascending = worst first)
        scored_ppas.sort(key=lambda x: x[1])

        return [ppa for ppa, score in scored_ppas[:limit]]

    def _identify_challenges(self, ppas, stats) -> List[str]:
        """Identify key challenges from the data."""
        challenges = []

        # Low disbursement rate
        if stats['disbursement_rate'] < 50:
            challenges.append(
                f"Low disbursement rate ({stats['disbursement_rate']:.1f}%) "
                "indicating potential implementation delays"
            )

        # High on_hold count
        on_hold = stats['status_breakdown'].get('on_hold', 0)
        if on_hold > 0:
            challenges.append(
                f"{on_hold} project(s) currently on hold requiring resolution"
            )

        # Budget utilization
        if stats['average_budget_utilization'] > 85:
            challenges.append(
                "High budget utilization may indicate potential overruns in some projects"
            )
        elif stats['average_budget_utilization'] < 40:
            challenges.append(
                "Low budget utilization suggests slow implementation or procurement issues"
            )

        return challenges

    def _calculate_timeline_progress_percent(self, ppa) -> float:
        """Calculate timeline progress as percentage."""
        if not ppa.start_date or not ppa.target_completion:
            return 0.0

        total_days = (ppa.target_completion - ppa.start_date).days
        if total_days <= 0:
            return 0.0

        elapsed_days = (date.today() - ppa.start_date).days

        return min(max(elapsed_days / total_days * 100, 0.0), 100.0)

    def _calculate_budget_utilization_percent(self, ppa) -> float:
        """Calculate budget utilization as percentage."""
        if not ppa.budget_allocation or ppa.budget_allocation == 0:
            return 0.0

        disbursed = float(ppa.total_disbursements_sum or 0)
        allocated = float(ppa.budget_allocation)

        return min((disbursed / allocated) * 100, 100.0)

    def _get_achievement_description(self, ppa) -> str:
        """Get achievement description for a project."""
        timeline_progress = self._calculate_timeline_progress_percent(ppa)
        budget_util = self._calculate_budget_utilization_percent(ppa)

        return (
            f"{timeline_progress:.0f}% complete, {budget_util:.0f}% budget utilized - "
            f"on track with balanced progress"
        )

    def _generate_executive_summary(
        self, quarter, year, stats, top_projects, challenges
    ) -> str:
        """Generate AI-powered executive summary."""
        prompt = f"""
Generate a professional executive summary for a quarterly M&E report:

**Period:** {quarter} {year}

**Key Statistics:**
- Total PPAs: {stats['total_ppas']}
- Ongoing: {stats['status_breakdown']['ongoing']}
- Completed this quarter: {stats['status_breakdown']['completed']}
- Total Budget: ₱{stats['total_budget']:,.2f}
- Disbursement Rate: {stats['disbursement_rate']:.1f}%

**Top Performing Projects:**
{', '.join(p.title for p in top_projects[:3])}

**Key Challenges:**
{chr(10).join(f'- {c}' for c in challenges)}

Write a 200-250 word executive summary for government stakeholders.
Focus on: overall performance, key achievements, challenges, and outlook.
Professional government report style.
Return plain text only.
"""

        try:
            response = self.gemini.generate_text(
                prompt,
                use_cache=True,
                cache_ttl=86400,
                include_cultural_context=False
            )

            if response['success']:
                return response['text']

        except Exception as e:
            logger.error(f"Error generating executive summary: {e}")

        # Fallback
        return self._generate_fallback_executive_summary(quarter, year, stats)

    def _generate_performance_overview(self, stats, top_projects, underperforming) -> str:
        """Generate performance overview section."""
        return f"""
**Overall Performance Metrics:**
- Total PPAs monitored: {stats['total_ppas']}
- Average budget utilization: {stats['average_budget_utilization']:.1f}%
- Disbursement rate: {stats['disbursement_rate']:.1f}%

**Status Distribution:**
- Planning: {stats['status_breakdown']['planning']}
- Ongoing: {stats['status_breakdown']['ongoing']}
- Completed: {stats['status_breakdown']['completed']}
- On Hold: {stats['status_breakdown']['on_hold']}

**Top Performing Projects:** {', '.join(p.title for p in top_projects[:3])}

**Projects Requiring Attention:** {', '.join(p.title for p in underperforming[:3])}
"""

    def _generate_budget_analysis(self, stats) -> str:
        """Generate budget analysis section."""
        return f"""
**Budget Overview:**
- Total Budget Allocation: ₱{stats['total_budget']:,.2f}
- Total Disbursed: ₱{stats['total_disbursed']:,.2f}
- Disbursement Rate: {stats['disbursement_rate']:.1f}%
- Average Project Budget Utilization: {stats['average_budget_utilization']:.1f}%

**Analysis:**
The disbursement rate of {stats['disbursement_rate']:.1f}% indicates {"strong" if stats['disbursement_rate'] > 70 else "moderate" if stats['disbursement_rate'] > 50 else "weak"} financial implementation during the period.
"""

    def _generate_recommendations(self, stats, challenges, underperforming) -> List[str]:
        """Generate AI-powered recommendations."""
        prompt = f"""
Based on this M&E data, provide 5 specific recommendations for improving project performance:

**Statistics:**
- Disbursement Rate: {stats['disbursement_rate']:.1f}%
- Average Budget Utilization: {stats['average_budget_utilization']:.1f}%

**Challenges:**
{chr(10).join(f'- {c}' for c in challenges)}

**Underperforming Projects:** {len(underperforming)}

Provide 5 specific, actionable recommendations for government program managers.
Each should be one concise sentence.

Return ONLY a valid JSON array (no markdown):
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

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")

        # Fallback
        return [
            "Accelerate disbursement processes to improve implementation rate",
            "Provide technical assistance to underperforming projects",
            "Conduct mid-quarter review meetings with implementing agencies",
            "Strengthen monitoring and evaluation systems",
            "Address identified bottlenecks in procurement and approval workflows"
        ]

    def _generate_monthly_summary(self, month_name, year, stats) -> str:
        """Generate monthly summary."""
        return f"""
**{month_name} {year} M&E Summary**

During {month_name} {year}, {stats['total_ppas']} PPAs were monitored with a total budget allocation of ₱{stats['total_budget']:,.2f}.

**Performance Highlights:**
- {stats['status_breakdown']['completed']} project(s) completed
- {stats['status_breakdown']['ongoing']} project(s) ongoing
- Disbursement rate: {stats['disbursement_rate']:.1f}%

**Financial Performance:**
Total disbursements reached ₱{stats['total_disbursed']:,.2f}, representing {stats['disbursement_rate']:.1f}% of allocated budget.
"""

    def _generate_fallback_executive_summary(self, quarter, year, stats) -> str:
        """Fallback executive summary when AI fails."""
        return f"""
**Executive Summary - {quarter} {year}**

During {quarter} {year}, the Office for Other Bangsamoro Communities monitored {stats['total_ppas']} Projects, Programs, and Activities (PPAs) with a combined budget allocation of ₱{stats['total_budget']:,.2f}.

**Key Performance Indicators:**
The portfolio achieved a disbursement rate of {stats['disbursement_rate']:.1f}%, with {stats['status_breakdown']['ongoing']} PPAs currently ongoing and {stats['status_breakdown']['completed']} completed during the quarter. Average budget utilization across all projects stands at {stats['average_budget_utilization']:.1f}%.

**Status Overview:**
Of the total PPAs, {stats['status_breakdown']['planning']} are in planning stage, {stats['status_breakdown']['ongoing']} are actively being implemented, and {stats['status_breakdown']['completed']} have been successfully completed. {stats['status_breakdown']['on_hold']} project(s) are currently on hold pending resolution of identified issues.

**Moving Forward:**
Continued focus on accelerating implementation and addressing bottlenecks will be essential to achieving annual targets. Enhanced monitoring and technical support for underperforming projects remain priorities for the next quarter.
"""

    def _generate_fallback_ppa_report(self, ppa, timeline_progress, budget_util) -> str:
        """Fallback PPA status report when AI fails."""
        return f"""
**Status Report: {ppa.title}**

**Current Status:** {ppa.get_status_display() if hasattr(ppa, 'get_status_display') else ppa.status}

The project is currently {timeline_progress:.1f}% complete in terms of timeline and has utilized {budget_util:.1f}% of its ₱{ppa.budget_allocation:,.2f} budget allocation.

**Progress:**
- Start Date: {ppa.start_date}
- Target Completion: {ppa.target_completion}
- Budget Disbursed: ₱{ppa.total_disbursements_sum or 0:,.2f}

**Next Steps:**
Continue implementation according to approved work plan and maintain regular monitoring and reporting.
"""
