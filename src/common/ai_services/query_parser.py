"""
Query Parser for Natural Language Search

Parses natural language queries into structured search parameters.
"""

import json
import logging
from typing import Any, Dict, List

from ai_assistant.services import GeminiService

logger = logging.getLogger(__name__)


class QueryParser:
    """
    Parse natural language search queries.

    Extracts:
    - Keywords (main search terms)
    - Filters (location, sector, date range)
    - Intent (find_communities, analyze_needs, track_projects)
    - Suggested modules to search
    """

    def __init__(self):
        """Initialize the query parser."""
        self.gemini = GeminiService(temperature=0.2)  # Low temperature for consistency

    def parse(self, query: str) -> Dict[str, Any]:
        """
        Parse natural language query.

        Args:
            query: User query string

        Returns:
            {
                'keywords': List[str],
                'filters': {
                    'location': str,
                    'sector': str,
                    'date_range': dict
                },
                'intent': str,
                'suggested_modules': List[str]
            }
        """
        if not query or not query.strip():
            return self._empty_parse()

        try:
            # Build parsing prompt
            prompt = self._build_parsing_prompt(query)

            # Generate response
            response = self.gemini.generate_text(
                prompt,
                use_cache=True,
                cache_ttl=3600,  # Cache for 1 hour
                include_cultural_context=False
            )

            if response.get('success'):
                parsed = self._extract_json(response['text'])
                return self._validate_parsed(parsed)
            else:
                logger.warning(f"Query parsing failed: {response.get('error')}")
                return self._fallback_parse(query)

        except Exception as e:
            logger.error(f"Error parsing query: {e}")
            return self._fallback_parse(query)

    def _build_parsing_prompt(self, query: str) -> str:
        """Build prompt for query parsing."""
        return f"""
Parse this OBCMS search query into structured format:

Query: "{query}"

Extract the following information:

1. KEYWORDS: Main search terms (list of strings)
2. FILTERS:
   - location: Geographic filter (region, province, municipality, barangay)
   - sector: Sector/category (education, health, livelihood, infrastructure, etc.)
   - date_range: Time period (if mentioned)
3. INTENT: What is the user trying to find?
   - find_communities: Looking for community profiles
   - analyze_needs: Looking for needs assessments
   - track_projects: Looking for projects/programs
   - review_policies: Looking for policy recommendations
   - find_organizations: Looking for partner organizations
   - general_search: General/mixed search
4. SUGGESTED_MODULES: Which modules to search (communities, mana, policies, coordination, projects)

Return ONLY a JSON object in this exact format:
{{
    "keywords": ["keyword1", "keyword2"],
    "filters": {{
        "location": "location_name or null",
        "sector": "sector_name or null",
        "date_range": null
    }},
    "intent": "intent_name",
    "suggested_modules": ["module1", "module2"]
}}

Examples:

Query: "coastal fishing communities in Zamboanga"
{{
    "keywords": ["coastal", "fishing", "communities"],
    "filters": {{
        "location": "Zamboanga",
        "sector": "livelihood",
        "date_range": null
    }},
    "intent": "find_communities",
    "suggested_modules": ["communities", "mana"]
}}

Query: "education programs for Muslim youth"
{{
    "keywords": ["education", "programs", "Muslim", "youth"],
    "filters": {{
        "location": null,
        "sector": "education",
        "date_range": null
    }},
    "intent": "track_projects",
    "suggested_modules": ["projects", "mana", "coordination"]
}}

Now parse: "{query}"
"""

    def _extract_json(self, text: str) -> Dict:
        """Extract JSON from AI response."""
        # Find JSON object in response
        text = text.strip()

        # Try to find JSON markers
        start_idx = text.find('{')
        end_idx = text.rfind('}')

        if start_idx == -1 or end_idx == -1:
            raise ValueError("No JSON object found in response")

        json_str = text[start_idx:end_idx + 1]

        # Parse JSON
        return json.loads(json_str)

    def _validate_parsed(self, parsed: Dict) -> Dict:
        """Validate and normalize parsed query."""
        # Ensure all required keys exist
        validated = {
            'keywords': parsed.get('keywords', []),
            'filters': {
                'location': parsed.get('filters', {}).get('location'),
                'sector': parsed.get('filters', {}).get('sector'),
                'date_range': parsed.get('filters', {}).get('date_range'),
            },
            'intent': parsed.get('intent', 'general_search'),
            'suggested_modules': parsed.get('suggested_modules', [
                'communities', 'mana', 'policies', 'coordination', 'projects'
            ])
        }

        # Validate module names
        valid_modules = ['communities', 'mana', 'policies', 'coordination', 'projects']
        validated['suggested_modules'] = [
            m for m in validated['suggested_modules']
            if m in valid_modules
        ]

        if not validated['suggested_modules']:
            validated['suggested_modules'] = valid_modules

        return validated

    def _fallback_parse(self, query: str) -> Dict:
        """Fallback parsing when AI fails."""
        # Simple keyword extraction
        keywords = [w for w in query.lower().split() if len(w) > 3]

        # Check for location mentions
        location = None
        location_keywords = ['zamboanga', 'cotabato', 'lanao', 'sultan kudarat', 'davao']
        for loc in location_keywords:
            if loc in query.lower():
                location = loc.title()
                break

        # Check for sector mentions
        sector = None
        sector_keywords = ['education', 'health', 'livelihood', 'infrastructure', 'agriculture']
        for sect in sector_keywords:
            if sect in query.lower():
                sector = sect
                break

        return {
            'keywords': keywords[:5],  # Limit to 5 keywords
            'filters': {
                'location': location,
                'sector': sector,
                'date_range': None,
            },
            'intent': 'general_search',
            'suggested_modules': ['communities', 'mana', 'policies', 'coordination', 'projects']
        }

    def _empty_parse(self) -> Dict:
        """Return empty parse result."""
        return {
            'keywords': [],
            'filters': {
                'location': None,
                'sector': None,
                'date_range': None,
            },
            'intent': 'general_search',
            'suggested_modules': []
        }
