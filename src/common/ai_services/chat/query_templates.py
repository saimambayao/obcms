"""
Query Templates for OBCMS Chat System

Provides pre-defined query templates that map natural language patterns
to Django ORM queries. No AI required.

Performance target: <50ms query generation
"""

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class QueryTemplate:
    """
    A query template that maps natural language patterns to Django ORM queries.

    Attributes:
        id: Unique template identifier
        name: Human-readable template name
        description: What this template does
        patterns: List of regex patterns that trigger this template
        intent: Intent type (data_query, analysis, etc.)
        entity_requirements: Required entities for this template
        query_template: Django ORM query template with placeholders
        result_type: Type of result (count, list, single, aggregate)
        priority: Priority for matching (higher = preferred)
    """

    id: str
    name: str
    description: str
    patterns: List[str]
    intent: str
    entity_requirements: List[str]
    query_template: str
    result_type: str
    priority: int = 5


class TemplateMatcher:
    """
    Matches natural language queries to predefined templates.

    Features:
    - Pattern matching with placeholders
    - Entity validation
    - Priority-based selection
    - Query generation from templates
    """

    def __init__(self):
        """Initialize template matcher with base templates."""
        self.templates = self._load_base_templates()

    def _load_base_templates(self) -> List[QueryTemplate]:
        """
        Load base query templates.

        Returns:
            List of QueryTemplate instances
        """
        return [
            # ==========================================
            # COMMUNITY QUERIES
            # ==========================================
            QueryTemplate(
                id="count_communities_by_location",
                name="Count communities by location",
                description="Count OBC communities in a specific location",
                patterns=[
                    r"how many (obc )?communities (in|at|from) (?P<location>.+)",
                    r"count (obc )?communities (in|at|from) (?P<location>.+)",
                    r"number of (obc )?communities (in|at|from) (?P<location>.+)",
                    r"total (obc )?communities (in|at|from) (?P<location>.+)",
                ],
                intent="data_query",
                entity_requirements=["location"],
                query_template="OBCCommunity.objects.filter({location_filter}).count()",
                result_type="count",
                priority=10,
            ),
            QueryTemplate(
                id="list_communities_by_location",
                name="List communities by location",
                description="Show all OBC communities in a location",
                patterns=[
                    r"(list|show|display) (obc )?communities (in|at|from) (?P<location>.+)",
                    r"(obc )?communities (in|at|from) (?P<location>.+)",
                    r"what (obc )?communities are (in|at|from) (?P<location>.+)",
                ],
                intent="data_query",
                entity_requirements=["location"],
                query_template="OBCCommunity.objects.filter({location_filter})",
                result_type="list",
                priority=9,
            ),
            QueryTemplate(
                id="count_communities_by_ethnic_group",
                name="Count communities by ethnolinguistic group",
                description="Count communities of a specific ethnolinguistic group",
                patterns=[
                    r"how many (?P<ethnic_group>\w+) communities",
                    r"count (?P<ethnic_group>\w+) communities",
                    r"number of (?P<ethnic_group>\w+) communities",
                ],
                intent="data_query",
                entity_requirements=["ethnolinguistic_group"],
                query_template="OBCCommunity.objects.filter(primary_ethnolinguistic_group__icontains='{ethnolinguistic_group}').count()",
                result_type="count",
                priority=9,
            ),
            QueryTemplate(
                id="communities_by_livelihood",
                name="Communities by livelihood",
                description="Find communities with specific livelihood",
                patterns=[
                    r"(?P<livelihood>\w+) communities",
                    r"communities (with|having) (?P<livelihood>\w+) livelihood",
                    r"(show|list) (?P<livelihood>\w+) communities",
                ],
                intent="data_query",
                entity_requirements=["livelihood"],
                query_template="OBCCommunity.objects.filter(primary_livelihoods__icontains='{livelihood}')",
                result_type="list",
                priority=8,
            ),
            QueryTemplate(
                id="count_all_communities",
                name="Count all communities",
                description="Count total OBC communities",
                patterns=[
                    r"how many (obc )?communities( are there)?",
                    r"count (all )?(obc )?communities",
                    r"total (obc )?communities",
                    r"number of (obc )?communities",
                ],
                intent="data_query",
                entity_requirements=[],
                query_template="OBCCommunity.objects.all().count()",
                result_type="count",
                priority=7,
            ),
            # ==========================================
            # WORKSHOP/ASSESSMENT QUERIES
            # ==========================================
            QueryTemplate(
                id="count_workshops_by_location",
                name="Count workshops by location",
                description="Count MANA assessments in a location",
                patterns=[
                    r"how many (mana )?(workshops|assessments) (in|at|from) (?P<location>.+)",
                    r"count (mana )?(workshops|assessments) (in|at|from) (?P<location>.+)",
                ],
                intent="data_query",
                entity_requirements=["location"],
                query_template="Assessment.objects.filter({location_filter}).count()",
                result_type="count",
                priority=10,
            ),
            QueryTemplate(
                id="recent_workshops",
                name="Recent workshops",
                description="Show recent MANA assessments",
                patterns=[
                    r"recent (mana )?(workshops|assessments)",
                    r"(show|list) recent (mana )?(workshops|assessments)",
                    r"latest (mana )?(workshops|assessments)",
                ],
                intent="data_query",
                entity_requirements=[],
                query_template="Assessment.objects.order_by('-actual_start_date')[:10]",
                result_type="list",
                priority=9,
            ),
            QueryTemplate(
                id="count_all_workshops",
                name="Count all workshops",
                description="Count total MANA assessments",
                patterns=[
                    r"how many (mana )?(workshops|assessments)( are there)?",
                    r"count (all )?(mana )?(workshops|assessments)",
                    r"total (mana )?(workshops|assessments)",
                ],
                intent="data_query",
                entity_requirements=[],
                query_template="Assessment.objects.all().count()",
                result_type="count",
                priority=7,
            ),
            # ==========================================
            # PARTNERSHIP QUERIES
            # ==========================================
            QueryTemplate(
                id="active_partnerships",
                name="Active partnerships",
                description="List active coordination partnerships",
                patterns=[
                    r"(show|list|display) active partnerships",
                    r"active partnerships",
                    r"current partnerships",
                ],
                intent="data_query",
                entity_requirements=[],
                query_template="Partnership.objects.filter(status='active')",
                result_type="list",
                priority=9,
            ),
            QueryTemplate(
                id="count_partnerships",
                name="Count partnerships",
                description="Count total partnerships",
                patterns=[
                    r"how many partnerships( are there)?",
                    r"count (all )?partnerships",
                    r"total partnerships",
                    r"number of partnerships",
                ],
                intent="data_query",
                entity_requirements=[],
                query_template="Partnership.objects.all().count()",
                result_type="count",
                priority=7,
            ),
            # ==========================================
            # POLICY QUERIES
            # ==========================================
            QueryTemplate(
                id="list_policies",
                name="List policy recommendations",
                description="Show all policy recommendations",
                patterns=[
                    r"(show|list|display) (all )?polic(y|ies)( recommendations)?",
                    r"polic(y|ies)( recommendations)?",
                ],
                intent="data_query",
                entity_requirements=[],
                query_template="PolicyRecommendation.objects.all()",
                result_type="list",
                priority=8,
            ),
            QueryTemplate(
                id="count_policies_by_status",
                name="Count policies by status",
                description="Count policy recommendations by status",
                patterns=[
                    r"how many (?P<status>\w+) polic(y|ies)",
                    r"count (?P<status>\w+) polic(y|ies)",
                    r"(?P<status>\w+) polic(y|ies) count",
                ],
                intent="data_query",
                entity_requirements=["status"],
                query_template="PolicyRecommendation.objects.filter(status='{status}').count()",
                result_type="count",
                priority=9,
            ),
            # ==========================================
            # GEOGRAPHIC QUERIES
            # ==========================================
            QueryTemplate(
                id="list_regions",
                name="List regions",
                description="Show all regions covered by OBCMS",
                patterns=[
                    r"(show|list|display) (all )?regions",
                    r"what regions",
                    r"which regions",
                ],
                intent="data_query",
                entity_requirements=[],
                query_template="Region.objects.all()",
                result_type="list",
                priority=8,
            ),
            QueryTemplate(
                id="count_provinces",
                name="Count all provinces",
                description="Count total provinces in OBC Data",
                patterns=[
                    r"how many provinces",
                    r"total provinces",
                    r"count (of )?provinces",
                    r"number of provinces",
                    r"how many provinces .+ in .+ obc data",
                ],
                intent="data_query",
                entity_requirements=[],
                query_template="Province.objects.count()",
                result_type="count",
                priority=10,
            ),
            QueryTemplate(
                id="count_regions",
                name="Count all regions",
                description="Count total regions in OBC Data",
                patterns=[
                    r"how many regions",
                    r"total regions",
                    r"count (of )?regions",
                    r"number of regions",
                ],
                intent="data_query",
                entity_requirements=[],
                query_template="Region.objects.count()",
                result_type="count",
                priority=10,
            ),
            QueryTemplate(
                id="count_municipalities",
                name="Count all municipalities",
                description="Count total municipalities in OBC Data",
                patterns=[
                    r"how many municipalities",
                    r"total municipalities",
                    r"count (of )?municipalities",
                    r"number of municipalities",
                ],
                intent="data_query",
                entity_requirements=[],
                query_template="Municipality.objects.count()",
                result_type="count",
                priority=10,
            ),
            QueryTemplate(
                id="count_barangays",
                name="Count all barangays",
                description="Count total barangays in OBC Data",
                patterns=[
                    r"how many barangays",
                    r"total barangays",
                    r"count (of )?barangays",
                    r"number of barangays",
                ],
                intent="data_query",
                entity_requirements=[],
                query_template="Barangay.objects.count()",
                result_type="count",
                priority=10,
            ),
            QueryTemplate(
                id="provinces_by_region",
                name="Provinces by region",
                description="List provinces in a region",
                patterns=[
                    r"provinces (in|at|from) (?P<location>.+)",
                    r"(show|list) provinces (in|at|from) (?P<location>.+)",
                    r"what provinces are (in|at|from) (?P<location>.+)",
                ],
                intent="data_query",
                entity_requirements=["location"],
                query_template="Province.objects.filter({location_filter})",
                result_type="list",
                priority=9,
            ),
        ]

    def find_matching_templates(
        self, query: str, entities: Dict[str, Any], intent: str
    ) -> List[QueryTemplate]:
        """
        Find templates that match the query.

        Args:
            query: Natural language query
            entities: Extracted entities
            intent: Query intent

        Returns:
            List of matching templates, sorted by priority (highest first)

        Example:
            >>> matcher = TemplateMatcher()
            >>> entities = {'location': {'value': 'Region IX', 'type': 'region'}}
            >>> templates = matcher.find_matching_templates(
            ...     "how many communities in Region IX",
            ...     entities,
            ...     'data_query'
            ... )
        """
        query_lower = query.lower().strip()
        matches = []

        for template in self.templates:
            # Check intent match
            if template.intent != intent:
                continue

            # Check if required entities are present
            if not self._has_required_entities(template, entities):
                continue

            # Try pattern matching
            for pattern in template.patterns:
                match = re.search(pattern, query_lower, re.IGNORECASE)
                if match:
                    matches.append(template)
                    logger.info(
                        f"Template matched: {template.id} (pattern: {pattern})"
                    )
                    break

        # Sort by priority (highest first)
        matches.sort(key=lambda t: t.priority, reverse=True)

        return matches

    def _has_required_entities(
        self, template: QueryTemplate, entities: Dict[str, Any]
    ) -> bool:
        """
        Check if all required entities are present.

        Args:
            template: Query template
            entities: Extracted entities

        Returns:
            True if all required entities are present
        """
        if not template.entity_requirements:
            return True

        for required_entity in template.entity_requirements:
            if required_entity not in entities:
                return False

        return True

    def generate_query(
        self, template: QueryTemplate, entities: Dict[str, Any]
    ) -> str:
        """
        Generate Django ORM query from template.

        Args:
            template: Query template
            entities: Extracted entities

        Returns:
            Django ORM query string

        Example:
            >>> template = QueryTemplate(...)
            >>> entities = {'location': {'value': 'Region IX', 'type': 'region'}}
            >>> query = matcher.generate_query(template, entities)
            >>> print(query)
            "OBCCommunity.objects.filter(barangay__municipality__province__region__name__icontains='Region IX').count()"
        """
        query = template.query_template

        # Replace location placeholder
        if "{location_filter}" in query:
            location_filter = self._build_location_filter(entities.get("location"))
            query = query.replace("{location_filter}", location_filter)

        # Replace ethnolinguistic group placeholder
        if "{ethnolinguistic_group}" in query:
            ethnic_group = entities.get("ethnolinguistic_group", {}).get("value", "")
            query = query.replace("{ethnolinguistic_group}", ethnic_group)

        # Replace livelihood placeholder
        if "{livelihood}" in query:
            livelihood = entities.get("livelihood", {}).get("value", "")
            query = query.replace("{livelihood}", livelihood)

        # Replace status placeholder
        if "{status}" in query:
            status = entities.get("status", {}).get("value", "")
            query = query.replace("{status}", status)

        # Replace date range placeholders
        if "{date_start}" in query or "{date_end}" in query:
            date_range = entities.get("date_range", {})
            if date_range:
                start = date_range.get("start", "")
                end = date_range.get("end", "")
                query = query.replace("{date_start}", str(start))
                query = query.replace("{date_end}", str(end))

        logger.info(f"Generated query: {query}")
        return query

    def _build_location_filter(self, location: Optional[Dict[str, Any]]) -> str:
        """
        Build Django ORM filter for location entity.

        Args:
            location: Location entity dict with type and value

        Returns:
            Django ORM filter string

        Example:
            >>> _build_location_filter({'type': 'region', 'value': 'Region IX'})
            "barangay__municipality__province__region__name__icontains='Region IX'"
        """
        if not location:
            return ""

        location_type = location.get("type", "")
        location_value = location.get("value", "")

        if not location_value:
            return ""

        # Build filter based on location type
        filter_map = {
            "region": f"barangay__municipality__province__region__name__icontains='{location_value}'",
            "province": f"barangay__municipality__province__name__icontains='{location_value}'",
            "municipality": f"barangay__municipality__name__icontains='{location_value}'",
            "barangay": f"barangay__name__icontains='{location_value}'",
        }

        # Default: try multiple location levels (most flexible)
        default_filter = (
            f"Q(barangay__municipality__name__icontains='{location_value}') | "
            f"Q(barangay__municipality__province__name__icontains='{location_value}') | "
            f"Q(barangay__municipality__province__region__name__icontains='{location_value}')"
        )

        return filter_map.get(location_type, default_filter)

    def add_template(self, template: QueryTemplate):
        """
        Add a new query template.

        Args:
            template: QueryTemplate instance
        """
        self.templates.append(template)
        logger.info(f"Added template: {template.id}")

    def get_template_by_id(self, template_id: str) -> Optional[QueryTemplate]:
        """
        Get template by ID.

        Args:
            template_id: Template ID

        Returns:
            QueryTemplate instance or None
        """
        for template in self.templates:
            if template.id == template_id:
                return template
        return None

    def get_templates_by_intent(self, intent: str) -> List[QueryTemplate]:
        """
        Get all templates for a specific intent.

        Args:
            intent: Intent type

        Returns:
            List of templates for that intent
        """
        return [t for t in self.templates if t.intent == intent]

    def get_template_stats(self) -> Dict[str, Any]:
        """
        Get template matcher statistics.

        Returns:
            Dict with template counts by intent, priority distribution, etc.
        """
        stats = {
            "total_templates": len(self.templates),
            "by_intent": {},
            "by_result_type": {},
            "avg_priority": 0.0,
        }

        # Count by intent
        for template in self.templates:
            stats["by_intent"][template.intent] = (
                stats["by_intent"].get(template.intent, 0) + 1
            )
            stats["by_result_type"][template.result_type] = (
                stats["by_result_type"].get(template.result_type, 0) + 1
            )

        # Average priority
        if self.templates:
            stats["avg_priority"] = sum(t.priority for t in self.templates) / len(
                self.templates
            )

        return stats


# Singleton instance
_matcher = None


def get_template_matcher() -> TemplateMatcher:
    """Get singleton template matcher instance."""
    global _matcher
    if _matcher is None:
        _matcher = TemplateMatcher()
    return _matcher
