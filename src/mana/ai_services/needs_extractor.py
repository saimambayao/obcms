"""
Needs Extractor
Extract and categorize community needs from workshop responses
"""

import json
import logging
from typing import Dict, List

from django.core.cache import cache
from django.utils import timezone

from ai_assistant.ai_engine import GeminiAIEngine
from ai_assistant.cultural_context import BangsomoroCulturalContext

logger = logging.getLogger(__name__)


class NeedsExtractor:
    """Extract and categorize community needs from assessment data"""

    # Comprehensive need categories for Bangsamoro communities
    NEED_CATEGORIES = {
        "health": {
            "keywords": [
                "health",
                "clinic",
                "hospital",
                "medicine",
                "doctor",
                "nurse",
                "medical",
            ],
            "icon": "fa-heartbeat",
            "color": "#dc2626",
        },
        "education": {
            "keywords": [
                "school",
                "education",
                "learning",
                "teacher",
                "classroom",
                "madrasah",
            ],
            "icon": "fa-graduation-cap",
            "color": "#2563eb",
        },
        "infrastructure": {
            "keywords": [
                "road",
                "bridge",
                "building",
                "facility",
                "construction",
                "repair",
            ],
            "icon": "fa-road",
            "color": "#7c3aed",
        },
        "livelihood": {
            "keywords": [
                "job",
                "income",
                "business",
                "livelihood",
                "farming",
                "agriculture",
                "fishing",
            ],
            "icon": "fa-briefcase",
            "color": "#059669",
        },
        "water": {
            "keywords": [
                "water",
                "well",
                "sanitation",
                "toilet",
                "hygiene",
                "drainage",
            ],
            "icon": "fa-tint",
            "color": "#0891b2",
        },
        "electricity": {
            "keywords": [
                "electricity",
                "power",
                "light",
                "generator",
                "solar",
                "energy",
            ],
            "icon": "fa-bolt",
            "color": "#f59e0b",
        },
        "governance": {
            "keywords": [
                "governance",
                "leader",
                "council",
                "official",
                "services",
                "representation",
            ],
            "icon": "fa-landmark",
            "color": "#6366f1",
        },
        "culture": {
            "keywords": [
                "culture",
                "tradition",
                "mosque",
                "islamic",
                "halal",
                "madrasa",
                "quran",
            ],
            "icon": "fa-mosque",
            "color": "#10b981",
        },
        "peace_security": {
            "keywords": [
                "peace",
                "security",
                "safety",
                "conflict",
                "protection",
                "police",
            ],
            "icon": "fa-shield-alt",
            "color": "#8b5cf6",
        },
        "social_services": {
            "keywords": [
                "social",
                "welfare",
                "assistance",
                "support",
                "subsidy",
                "aid",
            ],
            "icon": "fa-hands-helping",
            "color": "#ec4899",
        },
    }

    def __init__(self):
        """Initialize needs extractor with AI engine"""
        self.ai_engine = GeminiAIEngine()
        self.cultural_context = BangsomoroCulturalContext()

    def extract_needs(self, workshop_responses: List[str], context: str = "") -> Dict:
        """
        Extract and categorize needs from workshop responses

        Args:
            workshop_responses: List of response texts
            context: Additional context (community name, workshop type, etc.)

        Returns:
            dict: {
                'health': {
                    'priority': 'HIGH',
                    'needs': ['Build health clinic', 'Hire resident doctor'],
                    'urgency': 0.85,
                    'beneficiaries': 2500,
                    'category_score': 0.9
                },
                ...
            }
        """
        if not workshop_responses:
            return {}

        # Check cache
        cache_key = f"mana_needs_{hash(str(workshop_responses) + context)}"
        cached_needs = cache.get(cache_key)
        if cached_needs:
            logger.info("Using cached needs extraction")
            return cached_needs

        # Prepare cultural context
        cultural_guidelines = self.cultural_context.get_base_context()

        # Category descriptions
        categories_desc = "\n".join(
            [
                f"- {cat.replace('_', ' ').title()}: {', '.join(data['keywords'])}"
                for cat, data in self.NEED_CATEGORIES.items()
            ]
        )

        # Build extraction prompt
        prompt = f"""
{cultural_guidelines}

TASK: Extract and categorize community needs from assessment responses

CONTEXT: {context if context else 'Community needs assessment'}

COMMUNITY RESPONSES ({len(workshop_responses)} total):
{self._format_responses(workshop_responses)}

NEED CATEGORIES:
{categories_desc}

EXTRACTION REQUIREMENTS:
For each relevant category, provide:
1. Priority: CRITICAL/HIGH/MEDIUM/LOW based on urgency and importance
2. Specific Needs: List of concrete, actionable needs mentioned
3. Urgency Score: 0-1 (0=low urgency, 1=critical/immediate)
4. Estimated Beneficiaries: Approximate number of people affected
5. Category Score: 0-1 confidence that this category is truly a priority

ANALYSIS GUIDELINES:
- Focus on concrete, actionable needs
- Consider cultural context and Islamic values
- Prioritize based on: number of mentions, urgency in language, impact on community
- Estimate beneficiaries based on typical OBC barangay population (500-5000 people)
- Only include categories with clear evidence from responses

OUTPUT FORMAT (JSON):
{{
    "health": {{
        "priority": "HIGH",
        "needs": ["Build barangay health station", "Provide medicine supply"],
        "urgency": 0.85,
        "beneficiaries": 2500,
        "category_score": 0.9,
        "key_mentions": 15
    }},
    "education": {{
        "priority": "MEDIUM",
        "needs": ["Renovate school building", "Add more teachers"],
        "urgency": 0.6,
        "beneficiaries": 800,
        "category_score": 0.75,
        "key_mentions": 8
    }}
}}

Only include categories with clear evidence. Omit categories with no mentions.
"""

        try:
            # Generate needs extraction using Gemini
            response = self.ai_engine.model.generate_content(prompt)
            result_text = response.text.strip()

            # Clean JSON from markdown
            if result_text.startswith("```json"):
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif result_text.startswith("```"):
                result_text = result_text.split("```")[1].split("```")[0].strip()

            # Parse needs
            needs = json.loads(result_text)

            # Enrich with metadata
            for category, data in needs.items():
                if category in self.NEED_CATEGORIES:
                    data["icon"] = self.NEED_CATEGORIES[category]["icon"]
                    data["color"] = self.NEED_CATEGORIES[category]["color"]
                    data["category_name"] = category.replace("_", " ").title()

            # Cache for 3 days
            cache.set(cache_key, needs, timeout=86400 * 3)

            logger.info(f"Successfully extracted needs for {len(needs)} categories")
            return needs

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse needs extraction JSON: {e}")
            return self._fallback_needs_extraction(workshop_responses)

        except Exception as e:
            logger.error(f"Error extracting needs: {e}")
            return {}

    def rank_needs_by_priority(
        self, needs: Dict, ranking_criteria: Dict = None
    ) -> List[Dict]:
        """
        Rank extracted needs by priority considering multiple factors

        Args:
            needs: Needs dictionary from extract_needs()
            ranking_criteria: Optional custom weights for ranking

        Returns:
            List of needs sorted by priority score
        """
        if not needs:
            return []

        # Default ranking criteria weights
        criteria = ranking_criteria or {
            "urgency": 0.35,
            "beneficiaries": 0.25,
            "category_score": 0.25,
            "priority_level": 0.15,
        }

        priority_values = {"CRITICAL": 1.0, "HIGH": 0.75, "MEDIUM": 0.5, "LOW": 0.25}

        ranked_needs = []

        for category, data in needs.items():
            # Calculate composite score
            urgency_score = data.get("urgency", 0.5) * criteria["urgency"]

            beneficiaries_normalized = min(data.get("beneficiaries", 0) / 5000, 1.0)
            beneficiaries_score = beneficiaries_normalized * criteria["beneficiaries"]

            category_score = data.get("category_score", 0.5) * criteria["category_score"]

            priority_level = priority_values.get(data.get("priority", "MEDIUM"), 0.5)
            priority_score = priority_level * criteria["priority_level"]

            composite_score = (
                urgency_score + beneficiaries_score + category_score + priority_score
            )

            ranked_needs.append(
                {
                    "category": category,
                    "category_name": category.replace("_", " ").title(),
                    "priority": data.get("priority", "MEDIUM"),
                    "needs": data.get("needs", []),
                    "urgency": data.get("urgency", 0.5),
                    "beneficiaries": data.get("beneficiaries", 0),
                    "composite_score": round(composite_score, 3),
                    "icon": data.get("icon", "fa-circle"),
                    "color": data.get("color", "#6b7280"),
                }
            )

        # Sort by composite score
        ranked_needs.sort(key=lambda x: x["composite_score"], reverse=True)

        return ranked_needs

    def generate_needs_prioritization_matrix(
        self, needs: Dict, community_context: Dict = None
    ) -> Dict:
        """
        Generate a prioritization matrix based on impact vs effort

        Args:
            needs: Extracted needs
            community_context: Optional community info (budget, capacity, etc.)

        Returns:
            dict: Matrix categorizing needs into quadrants
        """
        if not needs:
            return {}

        # Use AI to estimate effort required for each need
        ranked_needs = self.rank_needs_by_priority(needs)

        # Categorize into quadrants
        matrix = {
            "quick_wins": [],  # High impact, low effort
            "strategic_projects": [],  # High impact, high effort
            "fill_ins": [],  # Low impact, low effort
            "hard_slogs": [],  # Low impact, high effort
        }

        for need in ranked_needs:
            impact = need["composite_score"]
            # Estimate effort based on category and beneficiaries
            effort = self._estimate_effort(need)

            # Categorize
            if impact > 0.6:
                if effort < 0.5:
                    matrix["quick_wins"].append({**need, "effort": effort})
                else:
                    matrix["strategic_projects"].append({**need, "effort": effort})
            else:
                if effort < 0.5:
                    matrix["fill_ins"].append({**need, "effort": effort})
                else:
                    matrix["hard_slogs"].append({**need, "effort": effort})

        return matrix

    def _format_responses(self, responses: List[str]) -> str:
        """Format responses for AI prompt"""
        formatted = []
        for i, response in enumerate(responses[:80], 1):  # Limit to 80
            if len(response) > 400:
                response = response[:397] + "..."
            formatted.append(f"{i}. {response}")

        if len(responses) > 80:
            formatted.append(
                f"\n... and {len(responses) - 80} more responses (showing first 80)"
            )

        return "\n".join(formatted)

    def _fallback_needs_extraction(self, responses: List[str]) -> Dict:
        """Simple keyword-based extraction as fallback"""
        needs = {}

        for category, data in self.NEED_CATEGORIES.items():
            keywords = data["keywords"]
            mention_count = 0
            example_needs = []

            for response in responses:
                response_lower = response.lower()
                if any(keyword in response_lower for keyword in keywords):
                    mention_count += 1
                    if len(example_needs) < 3:
                        # Extract sentence containing keyword
                        for sentence in response.split("."):
                            if any(keyword in sentence.lower() for keyword in keywords):
                                example_needs.append(sentence.strip())
                                break

            if mention_count > 0:
                # Calculate simple priority
                if mention_count >= len(responses) * 0.3:
                    priority = "HIGH"
                    urgency = 0.8
                elif mention_count >= len(responses) * 0.15:
                    priority = "MEDIUM"
                    urgency = 0.5
                else:
                    priority = "LOW"
                    urgency = 0.3

                needs[category] = {
                    "priority": priority,
                    "needs": example_needs[:5],
                    "urgency": urgency,
                    "beneficiaries": min(mention_count * 100, 3000),
                    "category_score": min(mention_count / len(responses), 1.0),
                    "key_mentions": mention_count,
                    "icon": data["icon"],
                    "color": data["color"],
                    "category_name": category.replace("_", " ").title(),
                }

        return needs

    def _estimate_effort(self, need: Dict) -> float:
        """
        Estimate effort required for implementing need

        Returns:
            float: 0-1 (0=low effort, 1=high effort)
        """
        # Simple heuristic based on category and beneficiaries
        category = need.get("category", "")
        beneficiaries = need.get("beneficiaries", 0)

        # High-effort categories
        if category in ["infrastructure", "electricity", "health"]:
            base_effort = 0.7
        elif category in ["education", "water"]:
            base_effort = 0.6
        else:
            base_effort = 0.4

        # Adjust by scale (beneficiaries)
        if beneficiaries > 3000:
            scale_multiplier = 1.2
        elif beneficiaries > 1500:
            scale_multiplier = 1.0
        else:
            scale_multiplier = 0.8

        effort = min(base_effort * scale_multiplier, 1.0)
        return round(effort, 2)
