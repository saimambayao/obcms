"""
Base Query Template Infrastructure for OBCMS Chat System

Provides core classes for pattern-based query templates that convert
natural language queries into Django ORM queries without AI.

Architecture:
- QueryTemplate: Individual template with pattern, query, and metadata
- TemplateRegistry: Central registry for all templates (singleton)
- Template validation and priority scoring
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class QueryTemplate:
    """
    Pattern-based template for converting natural language to Django ORM queries.

    A template defines:
    - Pattern: Regex to match user queries
    - Query template: Django ORM query with placeholders
    - Required/optional entities: What data must/can be extracted
    - Examples: Sample queries that match this template
    - Priority: Ranking for disambiguation

    Example:
        >>> template = QueryTemplate(
        ...     id='count_communities_location',
        ...     pattern=r'(?:how many|count).*communit.*(?:in|at)\\s+(.+)',
        ...     query_template='OBCCommunity.objects.filter({location_filter}).count()',
        ...     required_entities=['location'],
        ...     optional_entities=[],
        ...     examples=['How many communities in Region IX?'],
        ...     priority=10,
        ...     category='communities'
        ... )
    """

    # Core identification
    category: str
    pattern: str

    # Pattern matching
    compiled_pattern: Optional[re.Pattern] = field(default=None, init=False, repr=False)

    # Query generation (supports both styles)
    query_template: str = ""
    query_builder: Optional[Any] = None  # Callable function for dynamic queries
    required_entities: List[str] = field(default_factory=list)
    optional_entities: List[str] = field(default_factory=list)
    result_type: str = "list"  # "count", "list", "aggregate", "single"

    # Metadata
    description: str = ""
    examples: List[str] = field(default_factory=list)
    example_queries: List[str] = field(default_factory=list)  # Alias for examples
    priority: int = 5  # 1 (lowest) to 100 (highest)
    tags: List[str] = field(default_factory=list)

    # Optional fields for compatibility
    id: str = ""
    intent: str = "data_query"

    def __post_init__(self):
        """Compile regex pattern and generate ID after initialization."""
        # Auto-generate ID if not provided
        if not self.id:
            # Generate ID from category and pattern
            import hashlib
            pattern_hash = hashlib.md5(self.pattern.encode()).hexdigest()[:8]
            self.id = f"{self.category}_{pattern_hash}"

        # Compile regex pattern
        try:
            self.compiled_pattern = re.compile(self.pattern, re.IGNORECASE)
        except re.error as e:
            logger.error(f"Invalid regex pattern in template {self.id}: {e}")
            self.compiled_pattern = None

        # Merge example_queries into examples for compatibility
        if self.example_queries and not self.examples:
            self.examples = self.example_queries

    def matches(self, query: str) -> Optional[re.Match]:
        """
        Check if query matches this template's pattern.

        Args:
            query: User's natural language query (normalized)

        Returns:
            Match object if successful, None otherwise

        Example:
            >>> template.matches("how many communities in zamboanga")
            <re.Match object; span=(0, 37), match='how many communities in zamboanga'>
        """
        if not self.compiled_pattern:
            return None

        if not query:
            return None

        return self.compiled_pattern.search(query)

    def can_execute(self, entities: Dict[str, Any]) -> bool:
        """
        Check if all required entities are present for execution.

        Args:
            entities: Dictionary of extracted entities

        Returns:
            True if all required entities present, False otherwise

        Example:
            >>> entities = {'location': {'type': 'region', 'value': 'Region IX'}}
            >>> template.can_execute(entities)
            True
        """
        for required_entity in self.required_entities:
            if required_entity not in entities:
                return False
        return True

    def get_missing_entities(self, entities: Dict[str, Any]) -> List[str]:
        """
        Get list of missing required entities.

        Args:
            entities: Dictionary of extracted entities

        Returns:
            List of missing entity names

        Example:
            >>> entities = {}
            >>> template.get_missing_entities(entities)
            ['location']
        """
        missing = []
        for required_entity in self.required_entities:
            if required_entity not in entities:
                missing.append(required_entity)
        return missing

    def score_match(self, query: str, entities: Dict[str, Any]) -> float:
        """
        Score how well this template matches the query.

        Scoring factors:
        - Pattern match: +0.4
        - Priority: +0.3 (normalized)
        - Entity completeness: +0.3

        Args:
            query: User's query
            entities: Extracted entities

        Returns:
            Score between 0.0 and 1.0

        Example:
            >>> score = template.score_match("how many communities", {'location': ...})
            >>> print(f"{score:.2f}")
            0.85
        """
        score = 0.0

        # Pattern match (0.4)
        if self.matches(query):
            score += 0.4

        # Priority (0.3, normalized from 1-10)
        score += (self.priority / 10.0) * 0.3

        # Entity completeness (0.3)
        total_entities = len(self.required_entities) + len(self.optional_entities)
        if total_entities > 0:
            provided_entities = sum(
                1
                for entity in self.required_entities + self.optional_entities
                if entity in entities
            )
            entity_score = provided_entities / total_entities
            score += entity_score * 0.3

        return min(score, 1.0)

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"QueryTemplate(id='{self.id}', category='{self.category}', "
            f"priority={self.priority})"
        )


class TemplateRegistry:
    """
    Central registry for all query templates.

    Implements singleton pattern to ensure one global registry.
    Templates are organized by category and can be searched/filtered.

    Usage:
        >>> registry = TemplateRegistry.get_instance()
        >>> registry.register(template)
        >>> templates = registry.get_templates_by_category('communities')
    """

    _instance: Optional['TemplateRegistry'] = None

    def __init__(self):
        """Initialize empty registry."""
        if TemplateRegistry._instance is not None:
            logger.warning(
                "TemplateRegistry instantiated multiple times. "
                "Use get_instance() instead."
            )

        self._templates: Dict[str, QueryTemplate] = {}
        self._category_index: Dict[str, List[str]] = {}
        self._tag_index: Dict[str, List[str]] = {}

    @classmethod
    def get_instance(cls) -> 'TemplateRegistry':
        """
        Get singleton instance of template registry.

        Returns:
            The global TemplateRegistry instance

        Example:
            >>> registry = TemplateRegistry.get_instance()
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton instance (mainly for testing)."""
        cls._instance = None

    def register(self, template: QueryTemplate) -> None:
        """
        Register a query template.

        Args:
            template: QueryTemplate instance to register

        Raises:
            ValueError: If template ID already exists

        Example:
            >>> registry.register(QueryTemplate(...))
        """
        if template.id in self._templates:
            raise ValueError(
                f"Template with id '{template.id}' already registered. "
                f"Use unique IDs for each template."
            )

        # Add to main storage
        self._templates[template.id] = template

        # Index by category
        if template.category not in self._category_index:
            self._category_index[template.category] = []
        self._category_index[template.category].append(template.id)

        # Index by tags
        for tag in template.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = []
            self._tag_index[tag].append(template.id)

        logger.debug(f"Registered template: {template.id} (category: {template.category})")

    def register_many(self, templates: List[QueryTemplate]) -> None:
        """
        Register multiple templates at once.

        Args:
            templates: List of QueryTemplate instances

        Example:
            >>> registry.register_many([template1, template2, template3])
        """
        for template in templates:
            try:
                self.register(template)
            except ValueError as e:
                logger.error(f"Failed to register template: {e}")

    def get_template(self, template_id: str) -> Optional[QueryTemplate]:
        """
        Get template by ID.

        Args:
            template_id: Unique template identifier

        Returns:
            QueryTemplate if found, None otherwise

        Example:
            >>> template = registry.get_template('count_communities_location')
        """
        return self._templates.get(template_id)

    def get_all_templates(self) -> List[QueryTemplate]:
        """
        Get all registered templates.

        Returns:
            List of all QueryTemplate instances

        Example:
            >>> all_templates = registry.get_all_templates()
            >>> print(len(all_templates))
            30
        """
        return list(self._templates.values())

    def get_templates_by_category(self, category: str) -> List[QueryTemplate]:
        """
        Get all templates in a category.

        Args:
            category: Category name (e.g., 'communities', 'mana', 'general')

        Returns:
            List of QueryTemplate instances in category

        Example:
            >>> community_templates = registry.get_templates_by_category('communities')
        """
        template_ids = self._category_index.get(category, [])
        return [self._templates[tid] for tid in template_ids]

    def get_templates_by_tag(self, tag: str) -> List[QueryTemplate]:
        """
        Get all templates with a specific tag.

        Args:
            tag: Tag name (e.g., 'count', 'list', 'filter')

        Returns:
            List of QueryTemplate instances with tag

        Example:
            >>> count_templates = registry.get_templates_by_tag('count')
        """
        template_ids = self._tag_index.get(tag, [])
        return [self._templates[tid] for tid in template_ids]

    def search_templates(
        self,
        query: str,
        category: Optional[str] = None,
        min_priority: int = 1,
    ) -> List[QueryTemplate]:
        """
        Search for templates matching a query.

        Args:
            query: User's natural language query
            category: Optional category filter
            min_priority: Minimum priority threshold (1-10)

        Returns:
            List of matching templates, sorted by match score

        Example:
            >>> matches = registry.search_templates(
            ...     "how many communities in zamboanga",
            ...     category='communities'
            ... )
        """
        # Get candidate templates
        if category:
            candidates = self.get_templates_by_category(category)
        else:
            candidates = self.get_all_templates()

        # Filter by priority
        candidates = [t for t in candidates if t.priority >= min_priority]

        # Find matches
        matches = []
        for template in candidates:
            if template.matches(query):
                matches.append(template)

        return matches

    def get_categories(self) -> List[str]:
        """
        Get list of all registered categories.

        Returns:
            List of category names

        Example:
            >>> categories = registry.get_categories()
            >>> print(categories)
            ['communities', 'mana', 'general']
        """
        return list(self._category_index.keys())

    def get_tags(self) -> List[str]:
        """
        Get list of all registered tags.

        Returns:
            List of tag names

        Example:
            >>> tags = registry.get_tags()
        """
        return list(self._tag_index.keys())

    def get_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics.

        Returns:
            Dictionary with template counts by category and overall

        Example:
            >>> stats = registry.get_stats()
            >>> print(stats)
            {
                'total_templates': 30,
                'categories': {
                    'communities': 10,
                    'mana': 10,
                    'general': 10
                },
                'tags': {...}
            }
        """
        return {
            'total_templates': len(self._templates),
            'categories': {
                cat: len(tids) for cat, tids in self._category_index.items()
            },
            'tags': {tag: len(tids) for tag, tids in self._tag_index.items()},
            'avg_priority': (
                sum(t.priority for t in self._templates.values())
                / len(self._templates)
                if self._templates
                else 0
            ),
        }

    def clear(self) -> None:
        """Clear all templates (mainly for testing)."""
        self._templates.clear()
        self._category_index.clear()
        self._tag_index.clear()
        logger.debug("Template registry cleared")


# =============================================================================
# HELPER FUNCTIONS FOR QUERY GENERATION
# =============================================================================

def build_location_filter(entities: Dict[str, Any], base_field: str = "") -> str:
    """
    Build location filter clause from extracted location entity.

    Args:
        entities: Dictionary of extracted entities
        base_field: Base field prefix (e.g., "barangay__municipality")

    Returns:
        Django ORM filter string for location

    Example:
        >>> entities = {'location': {'type': 'region', 'value': 'Region IX'}}
        >>> build_location_filter(entities)
        "region__name__icontains='Region IX'"
    """
    location = entities.get('location')
    if not location:
        return ""

    loc_type = location.get('type', 'region')
    loc_value = location.get('value', '')

    if not loc_value:
        return ""

    # Build filter based on location type
    if loc_type == 'region':
        if base_field:
            return f"{base_field}__region__name__icontains='{loc_value}'"
        return f"region__name__icontains='{loc_value}'"
    elif loc_type == 'province':
        if base_field:
            return f"{base_field}__province__name__icontains='{loc_value}'"
        return f"province__name__icontains='{loc_value}'"
    elif loc_type == 'municipality':
        if base_field:
            return f"{base_field}__municipality__name__icontains='{loc_value}'"
        return f"municipality__name__icontains='{loc_value}'"
    elif loc_type == 'barangay':
        if base_field:
            return f"{base_field}__barangay__name__icontains='{loc_value}'"
        return f"barangay__name__icontains='{loc_value}'"
    else:
        # Generic search across all location levels
        return f"Q(region__name__icontains='{loc_value}') | Q(province__name__icontains='{loc_value}') | Q(municipality__name__icontains='{loc_value}')"


def build_status_filter(entities: Dict[str, Any], status_field: str = 'status') -> str:
    """
    Build status filter clause from extracted status entity.

    Args:
        entities: Dictionary of extracted entities
        status_field: Name of the status field (default: 'status')

    Returns:
        Django ORM filter string for status

    Example:
        >>> entities = {'status': 'active'}
        >>> build_status_filter(entities)
        "status='active'"
    """
    status = entities.get('status')
    if not status:
        return ""

    # Handle status value extraction
    if isinstance(status, dict):
        status_value = status.get('value', '')
    else:
        status_value = str(status)

    if not status_value:
        return ""

    # Normalize status values
    status_value = status_value.lower().replace(' ', '_')

    return f"{status_field}='{status_value}'"


def build_date_range_filter(entities: Dict[str, Any], date_field: str = 'created_at') -> str:
    """
    Build date range filter clause from extracted date entities.

    Args:
        entities: Dictionary of extracted entities
        date_field: Name of the date field to filter

    Returns:
        Django ORM filter string for date range

    Example:
        >>> entities = {'date_start': '2025-01-01', 'date_end': '2025-12-31'}
        >>> build_date_range_filter(entities, 'start_date')
        "start_date__gte='2025-01-01', start_date__lte='2025-12-31'"
    """
    date_start = entities.get('date_start')
    date_end = entities.get('date_end')

    filters = []

    if date_start:
        if isinstance(date_start, dict):
            date_start = date_start.get('value', '')
        filters.append(f"{date_field}__gte='{date_start}'")

    if date_end:
        if isinstance(date_end, dict):
            date_end = date_end.get('value', '')
        filters.append(f"{date_field}__lte='{date_end}'")

    return ', '.join(filters) if filters else ""


# =============================================================================
# GLOBAL SINGLETON ACCESSOR
# =============================================================================

def get_template_registry() -> TemplateRegistry:
    """
    Get the global template registry instance.

    This is the recommended way to access the registry.

    Returns:
        The singleton TemplateRegistry instance

    Example:
        >>> from common.ai_services.chat.query_templates import get_template_registry
        >>> registry = get_template_registry()
    """
    return TemplateRegistry.get_instance()
