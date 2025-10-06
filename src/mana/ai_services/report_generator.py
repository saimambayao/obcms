"""
Report Generator
Auto-generate comprehensive assessment reports using AI
"""

import json
import logging
from typing import Dict, List, Optional

from django.core.cache import cache
from django.utils import timezone

from ai_assistant.ai_engine import GeminiAIEngine
from ai_assistant.cultural_context import BangsomoroCulturalContext

from .needs_extractor import NeedsExtractor
from .response_analyzer import ResponseAnalyzer
from .theme_extractor import ThemeExtractor

logger = logging.getLogger(__name__)


class AssessmentReportGenerator:
    """Generate comprehensive MANA assessment reports"""

    def __init__(self):
        """Initialize report generator with AI services"""
        self.ai_engine = GeminiAIEngine()
        self.cultural_context = BangsomoroCulturalContext()
        self.response_analyzer = ResponseAnalyzer()
        self.theme_extractor = ThemeExtractor()
        self.needs_extractor = NeedsExtractor()

    def generate_executive_summary(
        self, workshop_id: int, max_words: int = 700
    ) -> str:
        """
        Generate executive summary of assessment

        Args:
            workshop_id: Workshop activity ID
            max_words: Maximum word count for summary

        Returns:
            str: Professional executive summary
        """
        from mana.models import WorkshopActivity

        try:
            workshop = WorkshopActivity.objects.get(id=workshop_id)

            # Gather analysis data
            insights = self.response_analyzer.aggregate_workshop_insights(workshop_id)

            if insights.get("status") != "success":
                return f"Executive summary unavailable: {insights.get('message', 'No data')}"

            # Extract needs and themes
            all_responses = self._collect_workshop_responses(workshop)

            needs = self.needs_extractor.extract_needs(
                all_responses,
                context=f"{workshop.workshop_type} - {workshop.barangay.name}",
            )

            themes = self.theme_extractor.extract_themes(
                all_responses, num_themes=5, context=workshop.workshop_type
            )

            # Prepare report context
            cultural_guidelines = self.cultural_context.get_base_context()

            # Build generation prompt
            prompt = f"""
{cultural_guidelines}

TASK: Generate a professional executive summary for this community assessment

WORKSHOP DETAILS:
- Type: {workshop.workshop_type}
- Location: {workshop.barangay.name}, {workshop.municipality.name}, {workshop.province.name}
- Date: {workshop.workshop_date}
- Participants: {workshop.participants.count()} community members
- Status: {workshop.get_status_display()}

KEY FINDINGS:
{json.dumps(insights.get('overall_summary', {}), indent=2)}

IDENTIFIED NEEDS (by priority):
{self._format_needs_for_report(needs)}

MAJOR THEMES:
{self._format_themes_for_report(themes)}

COMMUNITY CONTEXT:
- Geographic Scope: OBC (Other Bangsamoro Communities) outside BARMM
- Cultural Context: Bangsamoro Muslim community
- Administrative Level: Barangay-level assessment

REPORT REQUIREMENTS:
Generate a professional executive summary ({max_words} words maximum) that includes:

1. COMMUNITY OVERVIEW (1 paragraph)
   - Location and community profile
   - Assessment purpose and methodology
   - Participation details

2. KEY FINDINGS (2-3 paragraphs)
   - Most critical needs identified
   - Major themes from community input
   - Overall community sentiment and priorities

3. PRIORITY RECOMMENDATIONS (1-2 paragraphs)
   - Top 3-5 recommended interventions
   - Urgency and beneficiary impact
   - Cultural considerations for implementation

4. NEXT STEPS (1 paragraph)
   - Immediate actions required
   - Stakeholder engagement needed
   - Timeline considerations

STYLE GUIDELINES:
- Use professional, government-appropriate language
- Be objective and evidence-based
- Respect Bangsamoro cultural context and Islamic values
- Use specific data points and numbers
- Avoid jargon; write for general government audience
- Include proper references to OOBC mission

Write the executive summary now.
"""

            # Generate summary using Gemini
            response = self.ai_engine.model.generate_content(prompt)
            summary = response.text.strip()

            # Cache for 7 days
            cache_key = f"mana_exec_summary_{workshop_id}"
            cache.set(cache_key, summary, timeout=86400 * 7)

            logger.info(f"Successfully generated executive summary for workshop {workshop_id}")
            return summary

        except WorkshopActivity.DoesNotExist:
            logger.error(f"Workshop {workshop_id} not found")
            return "Error: Workshop not found"

        except Exception as e:
            logger.error(f"Error generating executive summary: {e}")
            return f"Error generating summary: {str(e)}"

    def generate_full_report(self, workshop_id: int) -> Dict:
        """
        Generate full assessment report with all sections

        Args:
            workshop_id: Workshop activity ID

        Returns:
            dict: Structured report data ready for PDF/template rendering
        """
        from mana.models import WorkshopActivity

        try:
            workshop = WorkshopActivity.objects.get(id=workshop_id)

            # Check cache
            cache_key = f"mana_full_report_{workshop_id}"
            cached_report = cache.get(cache_key)
            if cached_report:
                logger.info(f"Using cached full report for workshop {workshop_id}")
                return cached_report

            # Collect data
            all_responses = self._collect_workshop_responses(workshop)
            insights = self.response_analyzer.aggregate_workshop_insights(workshop_id)
            needs = self.needs_extractor.extract_needs(all_responses)
            themes = self.theme_extractor.extract_themes(all_responses, num_themes=8)
            ranked_needs = self.needs_extractor.rank_needs_by_priority(needs)

            # Generate sections
            executive_summary = self.generate_executive_summary(workshop_id)

            methodology_section = self._generate_methodology_section(workshop)

            findings_section = self._generate_findings_section(
                insights, themes, ranked_needs
            )

            recommendations_section = self._generate_recommendations_section(
                ranked_needs, workshop
            )

            # Compile full report
            full_report = {
                "metadata": {
                    "report_title": f"Community Needs Assessment Report: {workshop.barangay.name}",
                    "workshop_type": workshop.workshop_type,
                    "location": {
                        "barangay": workshop.barangay.name,
                        "municipality": workshop.municipality.name,
                        "province": workshop.province.name,
                    },
                    "assessment_date": str(workshop.workshop_date),
                    "report_generated": str(timezone.now().date()),
                    "total_participants": workshop.participants.count(),
                    "total_responses": len(all_responses),
                },
                "sections": {
                    "executive_summary": executive_summary,
                    "methodology": methodology_section,
                    "findings": findings_section,
                    "recommendations": recommendations_section,
                },
                "appendices": {
                    "needs_analysis": ranked_needs,
                    "themes": themes,
                    "detailed_insights": insights,
                },
            }

            # Cache for 14 days
            cache.set(cache_key, full_report, timeout=86400 * 14)

            logger.info(f"Successfully generated full report for workshop {workshop_id}")
            return full_report

        except WorkshopActivity.DoesNotExist:
            logger.error(f"Workshop {workshop_id} not found")
            return {"error": "Workshop not found"}

        except Exception as e:
            logger.error(f"Error generating full report: {e}")
            return {"error": str(e)}

    def generate_comparison_report(
        self, community_ids: List[int], title: str = "Community Comparison Report"
    ) -> Dict:
        """
        Compare needs across multiple communities

        Args:
            community_ids: List of OBC Community IDs
            title: Report title

        Returns:
            dict: Comparative analysis report
        """
        from mana.models import Assessment, WorkshopActivity

        try:
            community_data = []

            for community_id in community_ids:
                # Get latest completed assessment
                assessment = (
                    Assessment.objects.filter(
                        barangay__obc_community_id=community_id,
                        status__in=["completed", "reporting"],
                    )
                    .order_by("-created_at")
                    .first()
                )

                if not assessment:
                    continue

                # Get workshop data
                workshops = WorkshopActivity.objects.filter(assessment=assessment)

                for workshop in workshops:
                    responses = self._collect_workshop_responses(workshop)
                    if responses:
                        needs = self.needs_extractor.extract_needs(responses)
                        themes = self.theme_extractor.extract_themes(responses)

                        community_data.append(
                            {
                                "community_id": community_id,
                                "barangay": assessment.barangay.name,
                                "municipality": assessment.municipality.name,
                                "assessment_date": str(assessment.created_at.date()),
                                "needs": needs,
                                "themes": themes,
                            }
                        )
                        break  # One workshop per community

            if not community_data:
                return {"error": "No assessment data found for specified communities"}

            # Generate comparative analysis
            comparison_analysis = self._generate_comparative_analysis(community_data)

            report = {
                "title": title,
                "generated_at": str(timezone.now()),
                "communities_analyzed": len(community_data),
                "community_data": community_data,
                "comparative_analysis": comparison_analysis,
            }

            return report

        except Exception as e:
            logger.error(f"Error generating comparison report: {e}")
            return {"error": str(e)}

    def _collect_workshop_responses(self, workshop) -> List[str]:
        """Collect all text responses from a workshop"""
        responses = []

        for response in workshop.structured_responses.filter(status="submitted"):
            text = self._extract_response_text(response.response_data)
            if text:
                responses.append(text)

        return responses

    def _extract_response_text(self, response_data) -> Optional[str]:
        """Extract text from response data"""
        if isinstance(response_data, str):
            return response_data

        if isinstance(response_data, dict):
            for field in ["text", "answer", "response", "value", "content"]:
                if field in response_data:
                    return str(response_data[field])
            return json.dumps(response_data)

        return str(response_data)

    def _format_needs_for_report(self, needs: Dict) -> str:
        """Format needs dictionary for report generation"""
        if not needs:
            return "No specific needs identified"

        formatted = []
        for category, data in needs.items():
            priority = data.get("priority", "MEDIUM")
            need_list = data.get("needs", [])
            beneficiaries = data.get("beneficiaries", 0)

            formatted.append(
                f"- {category.replace('_', ' ').title()} [{priority}]: "
                f"{', '.join(need_list[:3])} (affects ~{beneficiaries} people)"
            )

        return "\n".join(formatted[:8])  # Top 8 categories

    def _format_themes_for_report(self, themes: List[Dict]) -> str:
        """Format themes list for report generation"""
        if not themes:
            return "No major themes identified"

        formatted = []
        for i, theme in enumerate(themes[:6], 1):  # Top 6 themes
            theme_name = theme.get("theme", "Unnamed")
            frequency = theme.get("frequency", 0)
            priority = theme.get("priority", "medium")

            formatted.append(f"{i}. {theme_name} (mentioned {frequency}x, priority: {priority})")

        return "\n".join(formatted)

    def _generate_methodology_section(self, workshop) -> str:
        """Generate methodology section"""
        return f"""
This assessment was conducted using participatory workshop methodology in {workshop.barangay.name}, {workshop.municipality.name}.

Workshop Type: {workshop.workshop_type}
Date: {workshop.workshop_date}
Participants: {workshop.participants.count()} community members representing diverse sectors

The assessment utilized structured questionnaires and facilitated group discussions to gather community input. All responses were analyzed using AI-powered thematic analysis while maintaining cultural sensitivity to Bangsamoro traditions and Islamic values.
"""

    def _generate_findings_section(
        self, insights: Dict, themes: List[Dict], ranked_needs: List[Dict]
    ) -> str:
        """Generate findings section"""
        # Build narrative from data
        top_themes = [t.get("theme", "") for t in themes[:5]]
        top_needs = [n.get("category_name", "") for n in ranked_needs[:5]]

        sentiment = insights.get("overall_summary", {}).get("overall_sentiment", "neutral")

        findings = f"""
COMMUNITY SENTIMENT: {sentiment.upper()}

KEY THEMES IDENTIFIED:
The assessment revealed {len(themes)} major thematic areas. The most prominent themes include: {', '.join(top_themes)}.

PRIORITY NEEDS:
Analysis of community responses identified critical needs in the following areas:
"""

        for i, need in enumerate(ranked_needs[:5], 1):
            findings += f"\n{i}. {need['category_name']} - {need['priority']} priority (affects ~{need['beneficiaries']} beneficiaries)"

        return findings

    def _generate_recommendations_section(
        self, ranked_needs: List[Dict], workshop
    ) -> str:
        """Generate recommendations section"""
        if not ranked_needs:
            return "Recommendations pending detailed analysis."

        recommendations = "PRIORITY RECOMMENDATIONS:\n\n"

        for i, need in enumerate(ranked_needs[:5], 1):
            category = need["category_name"]
            priority = need["priority"]
            specific_needs = need.get("needs", [])

            recommendations += f"{i}. {category} ({priority} Priority)\n"
            recommendations += f"   Recommended Actions:\n"

            for j, specific_need in enumerate(specific_needs[:3], 1):
                recommendations += f"   - {specific_need}\n"

            recommendations += "\n"

        recommendations += f"\nAll recommendations should be implemented with cultural sensitivity and community participation, respecting Bangsamoro traditions and Islamic values."

        return recommendations

    def _generate_comparative_analysis(self, community_data: List[Dict]) -> str:
        """Generate comparative analysis across communities"""
        # Identify common needs
        all_needs = {}

        for community in community_data:
            for category, data in community.get("needs", {}).items():
                if category not in all_needs:
                    all_needs[category] = 0
                all_needs[category] += 1

        # Sort by frequency
        common_needs = sorted(all_needs.items(), key=lambda x: x[1], reverse=True)

        analysis = f"CROSS-COMMUNITY ANALYSIS:\n\n"
        analysis += f"Analyzed {len(community_data)} communities.\n\n"
        analysis += f"COMMON NEEDS ACROSS COMMUNITIES:\n"

        for category, count in common_needs[:8]:
            percentage = (count / len(community_data)) * 100
            analysis += f"- {category.replace('_', ' ').title()}: {count}/{len(community_data)} communities ({percentage:.0f}%)\n"

        return analysis
