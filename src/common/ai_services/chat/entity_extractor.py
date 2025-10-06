"""
Entity Extractor for OBCMS Chat System.

This module extracts structured entities from natural language queries without using AI.
Supports locations, ethnolinguistic groups, livelihoods, date ranges, status, and numbers.

Performance target: <20ms per extraction
"""

import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

try:
    from django.utils import timezone
except ImportError:
    # Fallback for testing without Django
    import pytz
    class timezone:
        @staticmethod
        def now():
            return datetime.now(pytz.UTC)
        @staticmethod
        def get_current_timezone():
            return pytz.UTC

from common.ai_services.chat.entity_resolvers import (
    LocationResolver,
    EthnicGroupResolver,
    LivelihoodResolver,
    DateRangeResolver,
    StatusResolver,
    NumberResolver,
    SectorResolver,
    PriorityLevelResolver,
    UrgencyLevelResolver,
    NeedStatusResolver,
    MinistryResolver,
    BudgetRangeResolver,
    AssessmentTypeResolver,
    PartnershipTypeResolver,
)


class EntityExtractor:
    """
    Extract structured entities from natural language queries.

    Uses pattern matching, fuzzy matching, and database validation to extract:
    - Locations (regions, provinces, municipalities, barangays)
    - Ethnolinguistic groups (Maranao, Maguindanao, Tausug, etc.)
    - Livelihoods (farming, fishing, trading, etc.)
    - Date ranges (absolute and relative)
    - Status values (ongoing, completed, draft, etc.)
    - Numbers (cardinal and ordinal)

    Example:
        >>> extractor = EntityExtractor()
        >>> entities = extractor.extract_entities("maranao fishing communities zamboanga last 6 months")
        >>> print(entities)
        {
            'ethnolinguistic_group': {'value': 'Meranaw', 'confidence': 0.95},
            'livelihood': {'value': 'fishing', 'confidence': 0.90},
            'location': {'type': 'region', 'value': 'Region IX', 'confidence': 0.85},
            'date_range': {'start': datetime(...), 'end': datetime(...), 'confidence': 1.0}
        }
    """

    def __init__(self):
        """Initialize entity resolvers."""
        self.location_resolver = LocationResolver()
        self.ethnic_group_resolver = EthnicGroupResolver()
        self.livelihood_resolver = LivelihoodResolver()
        self.date_range_resolver = DateRangeResolver()
        self.status_resolver = StatusResolver()
        self.number_resolver = NumberResolver()

        # Needs-specific resolvers
        self.sector_resolver = SectorResolver()
        self.priority_level_resolver = PriorityLevelResolver()
        self.urgency_level_resolver = UrgencyLevelResolver()
        self.need_status_resolver = NeedStatusResolver()

        # Advanced entity resolvers
        self.ministry_resolver = MinistryResolver()
        self.budget_range_resolver = BudgetRangeResolver()
        self.assessment_type_resolver = AssessmentTypeResolver()
        self.partnership_type_resolver = PartnershipTypeResolver()

    def extract_entities(self, query: str) -> Dict[str, Any]:
        """
        Extract all entities from a natural language query.

        Args:
            query: Natural language query string

        Returns:
            Dictionary of extracted entities with confidence scores

        Example:
            >>> extract_entities("show me maguindanao farmers in sultan kudarat")
            {
                'ethnolinguistic_group': {'value': 'Maguindanaon', 'confidence': 0.95},
                'livelihood': {'value': 'farming', 'confidence': 0.90},
                'location': {'type': 'province', 'value': 'Sultan Kudarat', 'confidence': 0.92}
            }
        """
        if not query or not isinstance(query, str):
            return {}

        # Normalize query
        normalized_query = query.lower().strip()

        entities = {}

        # Extract each entity type
        location = self._extract_location(normalized_query)
        if location:
            entities['location'] = location

        ethnic_group = self._extract_ethnolinguistic_group(normalized_query)
        if ethnic_group:
            entities['ethnolinguistic_group'] = ethnic_group

        livelihood = self._extract_livelihood(normalized_query)
        if livelihood:
            entities['livelihood'] = livelihood

        date_range = self._extract_date_range(normalized_query)
        if date_range:
            entities['date_range'] = date_range

        status = self._extract_status(normalized_query)
        if status:
            entities['status'] = status

        numbers = self._extract_numbers(normalized_query)
        if numbers:
            entities['numbers'] = numbers

        # Needs-specific entities
        sector = self._extract_sector(normalized_query)
        if sector:
            entities['sector'] = sector

        priority_level = self._extract_priority_level(normalized_query)
        if priority_level:
            entities['priority_level'] = priority_level

        urgency_level = self._extract_urgency_level(normalized_query)
        if urgency_level:
            entities['urgency_level'] = urgency_level

        need_status = self._extract_need_status(normalized_query)
        if need_status:
            entities['need_status'] = need_status

        # Advanced entities
        ministry = self._extract_ministry(normalized_query)
        if ministry:
            entities['ministry'] = ministry

        budget_range = self._extract_budget_range(normalized_query)
        if budget_range:
            entities['budget_range'] = budget_range

        assessment_type = self._extract_assessment_type(normalized_query)
        if assessment_type:
            entities['assessment_type'] = assessment_type

        partnership_type = self._extract_partnership_type(normalized_query)
        if partnership_type:
            entities['partnership_type'] = partnership_type

        return entities

    def _extract_location(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Extract location entities from query.

        Recognizes:
        - Regions: "region ix", "region 9", "zamboanga", "r9"
        - Provinces: "sultan kudarat", "maguindanao", "south cotabato"
        - Municipalities: specific municipality names
        - Barangays: specific barangay names

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with location type, value, and confidence score
            or None if no location found

        Example:
            >>> _extract_location("communities in region ix")
            {'type': 'region', 'value': 'Region IX', 'confidence': 0.95}
        """
        return self.location_resolver.resolve(query)

    def _extract_ethnolinguistic_group(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Extract ethnolinguistic group entities from query.

        Recognizes variations and common misspellings:
        - "maranao", "marano", "meranaw" → "Meranaw"
        - "maguindanao", "maguindanaon" → "Maguindanaon"
        - "tausug", "tausog" → "Tausug"
        - etc.

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with ethnolinguistic group value and confidence score
            or None if no group found

        Example:
            >>> _extract_ethnolinguistic_group("maranao communities")
            {'value': 'Meranaw', 'confidence': 0.95}
        """
        return self.ethnic_group_resolver.resolve(query)

    def _extract_livelihood(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Extract livelihood entities from query.

        Recognizes:
        - Primary livelihoods: farming, fishing, trading, weaving, livestock
        - Alternative forms: "farmers" → "farming", "fishermen" → "fishing"

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with livelihood value and confidence score
            or None if no livelihood found

        Example:
            >>> _extract_livelihood("fishing communities")
            {'value': 'fishing', 'confidence': 0.90}
        """
        return self.livelihood_resolver.resolve(query)

    def _extract_date_range(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Extract date range entities from query.

        Recognizes:
        - Relative: "last 30 days", "last 6 months", "this year"
        - Absolute: "2024", "from jan to mar", "january 2024"
        - Keywords: "recent", "latest", "current"

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with start date, end date, and confidence score
            or None if no date range found

        Example:
            >>> _extract_date_range("last 6 months")
            {
                'start': datetime(2024, 4, 6),
                'end': datetime(2025, 10, 6),
                'confidence': 1.0,
                'range_type': 'relative'
            }
        """
        return self.date_range_resolver.resolve(query)

    def _extract_status(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Extract status entities from query.

        Recognizes:
        - Workflow status: ongoing, completed, draft, pending, approved
        - Task status: in progress, done, todo, cancelled
        - Project status: active, inactive, suspended

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with status value and confidence score
            or None if no status found

        Example:
            >>> _extract_status("ongoing projects")
            {'value': 'ongoing', 'confidence': 0.95}
        """
        return self.status_resolver.resolve(query)

    def _extract_numbers(self, query: str) -> List[Dict[str, Any]]:
        """
        Extract number entities from query.

        Recognizes:
        - Cardinal: "5", "25", "1000"
        - Ordinal: "first", "2nd", "third"
        - Written: "five", "twenty-five"

        Args:
            query: Normalized query string (lowercase)

        Returns:
            List of dictionaries with number value, type, and confidence score
            Empty list if no numbers found

        Example:
            >>> _extract_numbers("top 5 communities")
            [{'value': 5, 'type': 'cardinal', 'confidence': 1.0}]
        """
        return self.number_resolver.resolve(query)

    def get_entity_summary(self, entities: Dict[str, Any]) -> str:
        """
        Generate human-readable summary of extracted entities.

        Args:
            entities: Dictionary of extracted entities

        Returns:
            Human-readable summary string

        Example:
            >>> entities = extract_entities("maranao fishing zamboanga")
            >>> get_entity_summary(entities)
            "Found: Meranaw communities, fishing livelihood, Region IX"
        """
        parts = []

        if 'ethnolinguistic_group' in entities:
            parts.append(entities['ethnolinguistic_group']['value'])

        if 'livelihood' in entities:
            parts.append(f"{entities['livelihood']['value']} livelihood")

        if 'location' in entities:
            loc = entities['location']
            parts.append(f"{loc['value']} ({loc['type']})")

        if 'date_range' in entities:
            dr = entities['date_range']
            if dr.get('range_type') == 'relative':
                parts.append(f"recent data")
            else:
                parts.append(f"from {dr['start'].date()} to {dr['end'].date()}")

        if 'status' in entities:
            parts.append(f"{entities['status']['value']} status")

        if 'numbers' in entities and entities['numbers']:
            nums = entities['numbers']
            if nums:
                parts.append(f"top {nums[0]['value']}")

        if not parts:
            return "No entities detected"

        return "Found: " + ", ".join(parts)

    def validate_entities(self, entities: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate extracted entities for completeness and consistency.

        Args:
            entities: Dictionary of extracted entities

        Returns:
            Tuple of (is_valid, list_of_issues)

        Example:
            >>> entities = {'location': {'type': 'region', 'value': 'Region IX'}}
            >>> validate_entities(entities)
            (True, [])
        """
        issues = []

        # Check for conflicting locations
        if 'location' in entities:
            loc = entities['location']
            if loc.get('confidence', 0) < 0.5:
                issues.append(f"Low confidence location: {loc.get('value')} ({loc.get('confidence'):.2f})")

        # Check for conflicting dates
        if 'date_range' in entities:
            dr = entities['date_range']
            if dr.get('start') and dr.get('end'):
                if dr['start'] > dr['end']:
                    issues.append(f"Invalid date range: start ({dr['start']}) after end ({dr['end']})")

        # Check for low confidence entities
        for entity_type, entity_data in entities.items():
            if isinstance(entity_data, dict) and 'confidence' in entity_data:
                if entity_data['confidence'] < 0.3:
                    issues.append(f"Very low confidence {entity_type}: {entity_data.get('value')}")

        is_valid = len(issues) == 0
        return is_valid, issues

    def _extract_sector(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Extract development sector entities from query.

        Recognizes:
        - Development sectors: education, infrastructure, health, governance, etc.
        - Sector keywords: school, roads, clinic, etc.

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with sector value and confidence score
            or None if no sector found

        Example:
            >>> _extract_sector("infrastructure needs")
            {'value': 'infrastructure', 'confidence': 0.95}
        """
        return self.sector_resolver.resolve(query)

    def _extract_priority_level(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Extract priority level entities from query.

        Recognizes:
        - Priority terms: critical, high, medium, low
        - Urgency terms: immediate, urgent, pressing

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with priority level and confidence score
            or None if no priority found

        Example:
            >>> _extract_priority_level("critical needs")
            {'value': 'immediate', 'urgency_level': 'immediate', 'confidence': 0.95}
        """
        return self.priority_level_resolver.resolve(query)

    def _extract_urgency_level(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Extract urgency level entities from query.

        Recognizes:
        - Explicit urgency: immediate, short-term, medium-term, long-term
        - Time frames: within 1 month, 1-6 months, etc.

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with urgency level and confidence score
            or None if no urgency found

        Example:
            >>> _extract_urgency_level("immediate needs")
            {'value': 'immediate', 'confidence': 1.0}
        """
        return self.urgency_level_resolver.resolve(query)

    def _extract_need_status(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Extract need status entities from query.

        Recognizes:
        - Fulfillment status: unmet, met, partially met
        - Workflow status: identified, validated, planned, in progress, completed

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with need status and confidence score
            or None if no status found

        Example:
            >>> _extract_need_status("unmet needs")
            {'value': 'identified', 'confidence': 0.95}
        """
        return self.need_status_resolver.resolve(query)

    def _extract_ministry(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Extract ministry/MOA entities from query.

        Recognizes:
        - Ministry names: MILG, MSSD, MHPW, etc.
        - Alternative forms: "ministry of local government" → "MILG"

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with ministry value and confidence score
            or None if no ministry found

        Example:
            >>> _extract_ministry("MILG projects")
            {'value': 'MILG', 'confidence': 0.95}
        """
        return self.ministry_resolver.resolve(query)

    def _extract_budget_range(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Extract budget range entities from query.

        Recognizes:
        - Budget amounts: "under 1M", "over 5M", "between 1M and 5M"
        - Range types: minimum, maximum, exact

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with budget range and confidence score
            or None if no budget range found

        Example:
            >>> _extract_budget_range("projects under 1M")
            {'min': 0, 'max': 1000000, 'confidence': 0.95}
        """
        return self.budget_range_resolver.resolve(query)

    def _extract_assessment_type(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Extract assessment type entities from query.

        Recognizes:
        - Assessment types: rapid, comprehensive, baseline, thematic
        - Alternative forms: "quick assessment" → "rapid"

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with assessment type and confidence score
            or None if no assessment type found

        Example:
            >>> _extract_assessment_type("rapid assessment")
            {'value': 'rapid', 'confidence': 0.95}
        """
        return self.assessment_type_resolver.resolve(query)

    def _extract_partnership_type(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Extract partnership type entities from query.

        Recognizes:
        - Partnership types: MOA, MOU, collaboration, joint program
        - Alternative forms: "agreement" → "MOA"

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with partnership type and confidence score
            or None if no partnership type found

        Example:
            >>> _extract_partnership_type("MOA with DSWD")
            {'value': 'MOA', 'confidence': 0.95}
        """
        return self.partnership_type_resolver.resolve(query)
