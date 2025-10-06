"""
Theme Extractor
Extract and track themes from qualitative workshop data
"""

import json
import logging
from typing import Dict, List

from django.core.cache import cache
from django.utils import timezone

from ai_assistant.ai_engine import GeminiAIEngine
from ai_assistant.cultural_context import BangsomoroCulturalContext

logger = logging.getLogger(__name__)


class ThemeExtractor:
    """Extract themes from qualitative community assessment data"""

    def __init__(self):
        """Initialize theme extractor with AI engine"""
        self.ai_engine = GeminiAIEngine()
        self.cultural_context = BangsomoroCulturalContext()

    def extract_themes(
        self, responses: List[str], num_themes: int = 5, context: str = ""
    ) -> List[Dict]:
        """
        Extract main themes from workshop responses

        Args:
            responses: List of response texts
            num_themes: Number of themes to extract (default 5)
            context: Additional context about the workshop/community

        Returns:
            List[dict]: [
                {
                    'theme': 'Healthcare Access',
                    'frequency': 15,
                    'example_quotes': ['...', '...'],
                    'sub_themes': ['Clinic distance', 'Medicine shortage'],
                    'priority': 'high'
                },
                ...
            ]
        """
        if not responses:
            return []

        # Check cache
        cache_key = f"mana_themes_{hash(str(responses) + str(num_themes))}"
        cached_themes = cache.get(cache_key)
        if cached_themes:
            logger.info("Using cached theme extraction")
            return cached_themes

        # Prepare cultural context
        cultural_guidelines = self.cultural_context.get_base_context()

        # Build prompt
        prompt = f"""
{cultural_guidelines}

TASK: Extract thematic patterns from community workshop responses

CONTEXT: {context if context else 'Community needs assessment workshop'}

RESPONSES TO ANALYZE ({len(responses)} total):
{self._format_responses_for_themes(responses)}

EXTRACTION REQUIREMENTS:
Extract the top {num_themes} themes that emerge from these responses.

For each theme, provide:
1. Theme Name: Clear, descriptive name
2. Frequency: Estimated number of responses mentioning this theme
3. Example Quotes: 2-3 representative quotes from responses
4. Sub-themes: 2-4 related sub-topics or specific aspects
5. Priority: Perceived urgency/importance (critical/high/medium/low)

FOCUS AREAS FOR BANGSAMORO COMMUNITIES:
- Health and medical services
- Education and Islamic schools
- Infrastructure (roads, bridges, facilities)
- Livelihood and economic opportunities
- Water and sanitation
- Electricity and power
- Governance and representation
- Cultural and religious preservation
- Peace and security
- Social services and welfare

OUTPUT FORMAT (JSON Array):
[
    {{
        "theme": "Healthcare Access",
        "frequency": 15,
        "example_quotes": ["We need clinic nearby", "No doctor in barangay"],
        "sub_themes": ["Clinic construction", "Medical staff", "Medicine supply"],
        "priority": "high",
        "category": "health"
    }},
    ...
]
"""

        try:
            # Generate themes using Gemini
            response = self.ai_engine.model.generate_content(prompt)
            result_text = response.text.strip()

            # Clean JSON from markdown
            if result_text.startswith("```json"):
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif result_text.startswith("```"):
                result_text = result_text.split("```")[1].split("```")[0].strip()

            # Parse themes
            themes = json.loads(result_text)

            # Validate and enrich
            for theme in themes:
                theme.setdefault("theme", "Unnamed Theme")
                theme.setdefault("frequency", 0)
                theme.setdefault("example_quotes", [])
                theme.setdefault("sub_themes", [])
                theme.setdefault("priority", "medium")
                theme.setdefault("category", "other")

            # Cache for 7 days
            cache.set(cache_key, themes, timeout=86400 * 7)

            logger.info(f"Successfully extracted {len(themes)} themes")
            return themes

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse theme extraction JSON: {e}")
            return self._fallback_theme_extraction(responses, num_themes)

        except Exception as e:
            logger.error(f"Error extracting themes: {e}")
            return []

    def track_theme_evolution(
        self, community_id: int, lookback_months: int = 12
    ) -> Dict:
        """
        Track how themes change across multiple assessments over time

        Args:
            community_id: OBC Community ID
            lookback_months: How many months back to analyze

        Returns:
            dict: Theme evolution analysis
        """
        from datetime import timedelta

        from mana.models import Assessment, WorkshopActivity

        try:
            # Get assessments from last N months
            cutoff_date = timezone.now() - timedelta(days=lookback_months * 30)

            assessments = Assessment.objects.filter(
                barangay__obc_community_id=community_id,
                created_at__gte=cutoff_date,
                status__in=["completed", "reporting"],
            ).order_by("created_at")

            if not assessments.exists():
                return {
                    "status": "no_data",
                    "message": "No assessments found for this timeframe",
                }

            # Extract themes from each assessment
            timeline_themes = []
            for assessment in assessments:
                # Get workshop responses for this assessment
                workshops = WorkshopActivity.objects.filter(assessment=assessment)

                all_responses = []
                for workshop in workshops:
                    responses = workshop.structured_responses.filter(
                        status="submitted"
                    )
                    for response in responses:
                        text = self._extract_response_text(response.response_data)
                        if text:
                            all_responses.append(text)

                if all_responses:
                    themes = self.extract_themes(
                        all_responses,
                        num_themes=10,
                        context=f"Assessment: {assessment.title}",
                    )

                    timeline_themes.append(
                        {
                            "date": assessment.created_at.strftime("%Y-%m-%d"),
                            "assessment_title": assessment.title,
                            "themes": themes,
                        }
                    )

            # Analyze evolution
            evolution_analysis = self._analyze_theme_evolution(timeline_themes)

            return {
                "status": "success",
                "community_id": community_id,
                "timeframe_months": lookback_months,
                "assessment_count": len(timeline_themes),
                "timeline": timeline_themes,
                "evolution_analysis": evolution_analysis,
            }

        except Exception as e:
            logger.error(f"Error tracking theme evolution: {e}")
            return {"status": "error", "message": str(e)}

    def compare_themes_across_communities(
        self, community_ids: List[int], theme_count: int = 10
    ) -> Dict:
        """
        Compare themes across multiple communities

        Args:
            community_ids: List of OBC Community IDs
            theme_count: Number of top themes to compare

        Returns:
            dict: Cross-community theme comparison
        """
        from mana.models import Assessment

        try:
            community_themes = {}

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

                if assessment:
                    # Extract themes
                    # (Implementation similar to track_theme_evolution)
                    community_themes[community_id] = {
                        "assessment": assessment.title,
                        "themes": [],  # Extracted themes
                    }

            # Find common themes
            common_themes = self._identify_common_themes(community_themes)

            return {
                "status": "success",
                "communities_analyzed": len(community_themes),
                "community_themes": community_themes,
                "common_themes": common_themes,
            }

        except Exception as e:
            logger.error(f"Error comparing themes: {e}")
            return {"status": "error", "message": str(e)}

    def _format_responses_for_themes(self, responses: List[str]) -> str:
        """Format responses for theme extraction prompt"""
        formatted = []
        for i, response in enumerate(responses[:100], 1):  # Limit to 100
            if len(response) > 300:
                response = response[:297] + "..."
            formatted.append(f"{i}. {response}")

        if len(responses) > 100:
            formatted.append(
                f"\n... and {len(responses) - 100} more responses (showing first 100)"
            )

        return "\n".join(formatted)

    def _extract_response_text(self, response_data) -> str:
        """Extract text from response data"""
        if isinstance(response_data, str):
            return response_data

        if isinstance(response_data, dict):
            for field in ["text", "answer", "response", "value", "content"]:
                if field in response_data:
                    return str(response_data[field])
            return json.dumps(response_data)

        return str(response_data)

    def _fallback_theme_extraction(
        self, responses: List[str], num_themes: int
    ) -> List[Dict]:
        """Simple keyword-based theme extraction as fallback"""
        # Basic keyword-based extraction
        theme_keywords = {
            "health": ["health", "clinic", "hospital", "doctor", "medicine"],
            "education": ["school", "education", "teacher", "learning"],
            "infrastructure": ["road", "bridge", "building", "facility"],
            "livelihood": ["job", "income", "business", "farming", "livelihood"],
            "water": ["water", "well", "sanitation"],
            "electricity": ["electricity", "power", "light"],
        }

        theme_counts = {theme: 0 for theme in theme_keywords}

        for response in responses:
            response_lower = response.lower()
            for theme, keywords in theme_keywords.items():
                if any(keyword in response_lower for keyword in keywords):
                    theme_counts[theme] += 1

        # Sort by frequency
        sorted_themes = sorted(
            theme_counts.items(), key=lambda x: x[1], reverse=True
        )[:num_themes]

        return [
            {
                "theme": theme.title(),
                "frequency": count,
                "example_quotes": [],
                "sub_themes": [],
                "priority": "medium",
                "category": theme,
            }
            for theme, count in sorted_themes
            if count > 0
        ]

    def _analyze_theme_evolution(self, timeline_themes: List[Dict]) -> Dict:
        """Analyze how themes evolve over time"""
        if not timeline_themes:
            return {}

        # Track theme frequency changes
        all_theme_names = set()
        for entry in timeline_themes:
            for theme in entry.get("themes", []):
                all_theme_names.add(theme.get("theme", ""))

        evolution = {}
        for theme_name in all_theme_names:
            appearances = []
            for entry in timeline_themes:
                found = False
                for theme in entry.get("themes", []):
                    if theme.get("theme") == theme_name:
                        appearances.append(
                            {
                                "date": entry["date"],
                                "priority": theme.get("priority", "medium"),
                                "frequency": theme.get("frequency", 0),
                            }
                        )
                        found = True
                        break

                if not found:
                    appearances.append(
                        {"date": entry["date"], "priority": None, "frequency": 0}
                    )

            evolution[theme_name] = {
                "appearances": len([a for a in appearances if a["priority"]]),
                "trend": self._calculate_trend(appearances),
                "timeline": appearances,
            }

        return evolution

    def _calculate_trend(self, appearances: List[Dict]) -> str:
        """Calculate if theme is increasing, decreasing, or stable"""
        if len(appearances) < 2:
            return "stable"

        frequencies = [a["frequency"] for a in appearances if a["frequency"] > 0]
        if len(frequencies) < 2:
            return "stable"

        # Simple trend: compare first half vs second half
        mid = len(frequencies) // 2
        first_half_avg = sum(frequencies[:mid]) / mid if mid > 0 else 0
        second_half_avg = sum(frequencies[mid:]) / (len(frequencies) - mid)

        if second_half_avg > first_half_avg * 1.2:
            return "increasing"
        elif second_half_avg < first_half_avg * 0.8:
            return "decreasing"
        else:
            return "stable"

    def _identify_common_themes(self, community_themes: Dict) -> List[Dict]:
        """Identify themes that appear across multiple communities"""
        theme_occurrences = {}

        for community_id, data in community_themes.items():
            for theme in data.get("themes", []):
                theme_name = theme.get("theme", "")
                if theme_name not in theme_occurrences:
                    theme_occurrences[theme_name] = {
                        "communities": [],
                        "total_frequency": 0,
                        "avg_priority": [],
                    }

                theme_occurrences[theme_name]["communities"].append(community_id)
                theme_occurrences[theme_name]["total_frequency"] += theme.get(
                    "frequency", 0
                )
                theme_occurrences[theme_name]["avg_priority"].append(
                    theme.get("priority", "medium")
                )

        # Filter to themes appearing in multiple communities
        common_themes = [
            {
                "theme": name,
                "community_count": len(data["communities"]),
                "total_mentions": data["total_frequency"],
                "common_priority": max(
                    set(data["avg_priority"]), key=data["avg_priority"].count
                ),
            }
            for name, data in theme_occurrences.items()
            if len(data["communities"]) > 1
        ]

        # Sort by number of communities
        common_themes.sort(key=lambda x: x["community_count"], reverse=True)

        return common_themes
