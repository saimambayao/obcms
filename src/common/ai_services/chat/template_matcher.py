"""
Template Matcher for OBCMS Chat System

Matches user queries to query templates and generates database queries.
Provides pattern-based query generation without requiring AI.

Architecture:
- TemplateMatcher: Main class for finding and ranking template matches
- Entity substitution and query generation
- Template validation and scoring

Performance target: <10ms per match
"""

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TemplateMatcher:
    """
    Matches queries to templates and generates database queries.

    Provides pattern-based query generation by:
    1. Finding templates matching the query pattern
    2. Ranking templates by match quality
    3. Validating required entities are present
    4. Substituting entities into query template
    5. Generating executable Django ORM query

    Example:
        >>> matcher = TemplateMatcher()
        >>> entities = {
        ...     'location': {'type': 'region', 'value': 'Region IX', 'confidence': 0.95}
        ... }
        >>> result = matcher.match_and_generate(
        ...     "How many communities in Region IX?",
        ...     entities,
        ...     intent='data_query'
        ... )
        >>> print(result['query'])
        "OBCCommunity.objects.filter(barangay__municipality__province__region__name__icontains='Region IX').count()"
    """

    def __init__(self):
        """Initialize template matcher."""
        self._registry = None
        logger.debug("TemplateMatcher initialized (registry will be loaded lazily)")
        # Map regex capture group names to canonical entity keys we support injecting.
        self._group_entity_map = {
            'rating': 'rating',
        }

    @property
    def registry(self):
        """Lazy load the template registry to avoid circular dependency."""
        if self._registry is None:
            # Lazy import to avoid circular dependency
            from common.ai_services.chat.query_templates.base import get_template_registry as _get_template_registry_base
            self._registry = _get_template_registry_base()
            # TEMPORARILY DISABLED template registration to test server startup
            # Ensure templates are registered
            # if not self._registry.get_all_templates():
            #     from common.ai_services.chat.query_templates import _register_all_templates
            #     _register_all_templates(registry=self._registry)
            logger.debug("TemplateMatcher registry loaded lazily (templates disabled)")
        return self._registry

    def match_and_generate(
        self,
        query: str,
        entities: Dict[str, Any],
        intent: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Match query to template and generate database query.

        Args:
            query: User's natural language query
            entities: Extracted entities from query
            intent: Optional intent filter (data_query, analysis, etc.)
            category: Optional category filter (communities, mana, etc.)

        Returns:
            Dictionary with:
                - success: bool - Whether matching succeeded
                - template: QueryTemplate - Matched template (if found)
                - query: str - Generated Django ORM query (if successful)
                - score: float - Match score (0.0-1.0)
                - error: str - Error message (if failed)
                - missing_entities: List[str] - Missing required entities

        Example:
            >>> result = matcher.match_and_generate(
            ...     "How many workshops in last 6 months?",
            ...     entities={'date_range': {...}},
            ...     category='mana'
            ... )
        """
        try:
            # Step 1: Find matching templates
            matches = self.find_matching_templates(query, entities, intent, category)

            if not matches:
                return {
                    'success': False,
                    'template': None,
                    'query': None,
                    'score': 0.0,
                    'error': 'No matching templates found',
                    'missing_entities': [],
                }

            # Step 2: Rank templates and pick best match
            ranked_matches = self.rank_templates(matches, query, entities)
            best_match = ranked_matches[0]

            # Merge regex capture groups into the entity set so templates can use them
            entities_for_template: Dict[str, Any] = dict(entities)
            match_obj = best_match.get('match')
            if match_obj:
                for group_name, group_value in match_obj.groupdict().items():
                    if not group_value:
                        continue

                    entity_key = self._group_entity_map.get(group_name)
                    if not entity_key:
                        continue

                    normalized_value = group_value.strip().lower()
                    if not normalized_value:
                        continue

                    existing_entity = entities_for_template.get(entity_key)
                    if isinstance(existing_entity, dict) and existing_entity.get('value'):
                        continue

                    entities_for_template[entity_key] = {'value': normalized_value}

            # Step 3: Validate entities
            validation = self.validate_template(best_match['template'], entities_for_template)
            if not validation['is_valid']:
                return {
                    'success': False,
                    'template': best_match['template'],
                    'query': None,
                    'score': best_match['score'],
                    'error': validation['error'],
                    'missing_entities': validation['missing_entities'],
                }

            # Step 4: Generate query
            query_string = self.generate_query(best_match['template'], entities_for_template)

            return {
                'success': True,
                'template': best_match['template'],
                'query': query_string,
                'score': best_match['score'],
                'error': None,
                'missing_entities': [],
            }

        except Exception as e:
            logger.error(f"Error in match_and_generate: {e}", exc_info=True)
            return {
                'success': False,
                'template': None,
                'query': None,
                'score': 0.0,
                'error': f"Internal error: {str(e)}",
                'missing_entities': [],
            }

    def find_matching_templates(
        self,
        query: str,
        entities: Dict[str, Any],
        intent: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List:  # Lazy type annotation to avoid circular import
        """
        Find all templates matching the query pattern.

        Args:
            query: User's natural language query (normalized)
            entities: Extracted entities
            intent: Optional intent filter
            category: Optional category filter

        Returns:
            List of matching QueryTemplate instances

        Example:
            >>> matches = matcher.find_matching_templates(
            ...     "how many communities",
            ...     {},
            ...     category='communities'
            ... )
        """
        # Use registry's search method
        matches = self.registry.search_templates(
            query=query,
            category=category,
            min_priority=1,
        )

        # Additional filtering if needed
        filtered_matches = []
        for template in matches:
            # Check pattern match
            if not template.matches(query):
                continue

            # Add to results
            filtered_matches.append(template)

        logger.debug(f"Found {len(filtered_matches)} matching templates for query: {query[:50]}...")
        return filtered_matches

    def rank_templates(
        self,
        templates: List[QueryTemplate],
        query: str,
        entities: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Rank templates by match quality.

        Ranking factors:
        - Pattern match quality
        - Priority score
        - Entity completeness
        - Template specificity

        Args:
            templates: List of candidate templates
            query: User's query
            entities: Extracted entities

        Returns:
            List of dicts with 'template' and 'score', sorted by score (desc)

        Example:
            >>> ranked = matcher.rank_templates(matches, query, entities)
            >>> print(ranked[0]['score'])
            0.92
        """
        ranked = []

        for template in templates:
            # Capture regex match for later entity extraction
            match = template.matches(query)

            # Calculate match score
            score = template.score_match(query, entities)

            ranked.append({
                'template': template,
                'score': score,
                'match': match,
            })

        # Sort by score (descending)
        ranked.sort(key=lambda x: x['score'], reverse=True)

        logger.debug(
            f"Ranked {len(ranked)} templates, best score: "
            f"{ranked[0]['score']:.2f}" if ranked else "N/A"
        )

        return ranked

    def validate_template(
        self,
        template,  # QueryTemplate - lazy type to avoid circular import
        entities: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate that template can be executed with given entities.

        Args:
            template: QueryTemplate to validate
            entities: Extracted entities

        Returns:
            Dictionary with:
                - is_valid: bool
                - error: str (if invalid)
                - missing_entities: List[str]

        Example:
            >>> validation = matcher.validate_template(template, entities)
            >>> print(validation['is_valid'])
            True
        """
        # Check required entities
        missing_entities = template.get_missing_entities(entities)

        if missing_entities:
            return {
                'is_valid': False,
                'error': f"Missing required entities: {', '.join(missing_entities)}",
                'missing_entities': missing_entities,
            }

        return {
            'is_valid': True,
            'error': None,
            'missing_entities': [],
        }

    def substitute_entities(
        self,
        template_string: str,
        entities: Dict[str, Any],
    ) -> str:
        """
        Substitute entity placeholders in template string.

        Supports placeholders like:
        - {location_filter} - Location-based filter
        - {status_filter} - Status-based filter
        - {date_range_filter} - Date range filter
        - {limit} - Result limit
        - Direct entity values: {location.value}, {status.value}

        Args:
            template_string: Query template with placeholders
            entities: Extracted entities

        Returns:
            Template string with placeholders substituted

        Example:
            >>> template = "OBCCommunity.objects.filter({location_filter}).count()"
            >>> entities = {'location': {'type': 'region', 'value': 'Region IX'}}
            >>> result = matcher.substitute_entities(template, entities)
            >>> print(result)
            "OBCCommunity.objects.filter(barangay__municipality__province__region__name__icontains='Region IX').count()"
        """
        result = template_string

        # Build filter clauses
        filters = {}

        # Location filter
        if 'location' in entities:
            location_entity = entities['location']
            location_value = location_entity.get('value', '')
            location_type = location_entity.get('type', 'unknown')

            if location_type == 'region':
                filters['location_filter'] = (
                    f"barangay__municipality__province__region__name__icontains='{location_value}'"
                )
            elif location_type == 'province':
                filters['location_filter'] = (
                    f"barangay__municipality__province__name__icontains='{location_value}'"
                )
            elif location_type == 'municipality':
                filters['location_filter'] = (
                    f"barangay__municipality__name__icontains='{location_value}'"
                )
            elif location_type == 'barangay':
                filters['location_filter'] = (
                    f"barangay__name__icontains='{location_value}'"
                )
            else:
                # Fallback: search across all levels
                filters['location_filter'] = (
                    f"Q(barangay__municipality__province__region__name__icontains='{location_value}') | "
                    f"Q(barangay__municipality__province__name__icontains='{location_value}') | "
                    f"Q(barangay__municipality__name__icontains='{location_value}') | "
                    f"Q(barangay__name__icontains='{location_value}')"
                )

        # Status filter
        if 'status' in entities:
            status_value = entities['status'].get('value', '')
            filters['status_filter'] = f"status__iexact='{status_value}'"

        # Date range filter
        if 'date_range' in entities:
            date_range = entities['date_range']
            start_date = date_range.get('start')
            end_date = date_range.get('end')

            if start_date and end_date:
                filters['date_range_filter'] = (
                    f"created_at__gte='{start_date.isoformat()}', "
                    f"created_at__lte='{end_date.isoformat()}'"
                )
            elif start_date:
                filters['date_range_filter'] = f"created_at__gte='{start_date.isoformat()}'"
            elif end_date:
                filters['date_range_filter'] = f"created_at__lte='{end_date.isoformat()}'"

        # Ethnolinguistic group filter
        if 'ethnolinguistic_group' in entities:
            group_value = entities['ethnolinguistic_group'].get('value', '')
            filters['ethnic_group_filter'] = (
                f"primary_ethnic_group__icontains='{group_value}'"
            )

        # Livelihood filter
        if 'livelihood' in entities:
            livelihood_value = entities['livelihood'].get('value', '')
            filters['livelihood_filter'] = (
                f"primary_livelihood__icontains='{livelihood_value}'"
            )

        # Rating/availability filter for infrastructure templates
        rating_entity = entities.get('rating')
        rating_value = ''
        if rating_entity:
            if isinstance(rating_entity, dict):
                rating_value = rating_entity.get('value', '')
            elif isinstance(rating_entity, str):
                rating_value = rating_entity

        normalized_rating = self._normalize_rating_value(rating_value)
        if normalized_rating:
            filters['rating_filter'] = (
                f", infrastructure__availability_status__icontains='{normalized_rating}'"
            )
            filters['rating'] = normalized_rating
        else:
            filters['rating_filter'] = ''

        # Limit/count
        if 'numbers' in entities and entities['numbers']:
            limit_value = entities['numbers'][0].get('value', 20)
            filters['limit'] = str(limit_value)
        else:
            filters['limit'] = '20'  # Default limit

        # Substitute all placeholders
        for placeholder, value in filters.items():
            result = result.replace(f'{{{placeholder}}}', value)

        # Clean up any remaining unfilled placeholders
        # Replace with safe defaults or remove them
        result = re.sub(r'\{[^}]+\}', '', result)

        return result

    def generate_query(
        self,
        template,  # QueryTemplate - lazy type to avoid circular import
        entities: Dict[str, Any],
    ) -> str:
        """
        Generate executable Django ORM query from template.

        Args:
            template: QueryTemplate to use
            entities: Extracted entities

        Returns:
            Django ORM query string ready for execution

        Example:
            >>> query = matcher.generate_query(template, entities)
            >>> print(query)
            "OBCCommunity.objects.filter(...).count()"
        """
        # Substitute entities into template
        query_string = self.substitute_entities(
            template.query_template,
            entities,
        )

        logger.debug(f"Generated query from template {template.id}: {query_string[:100]}...")

        return query_string

    def _normalize_rating_value(self, value: str) -> Optional[str]:
        """
        Normalize infrastructure availability ratings captured from patterns.

        Ensures consistent values even when queries use variations
        like "no" instead of "none".
        """
        if not value:
            return None

        normalized = value.strip().lower()
        if not normalized:
            return None

        rating_map = {
            'no': 'none',
            'none': 'none',
            'without': 'none',
            'poor': 'poor',
            'limited': 'limited',
            'available': 'available',
            'good': 'good',
        }

        return rating_map.get(normalized, normalized)

    def get_template_suggestions(
        self,
        partial_query: str,
        category: Optional[str] = None,
        max_suggestions: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Get template suggestions for partial query (autocomplete).

        Args:
            partial_query: Partial user query
            category: Optional category filter
            max_suggestions: Maximum suggestions to return

        Returns:
            List of suggestion dicts with template info and example

        Example:
            >>> suggestions = matcher.get_template_suggestions("how many", "communities")
            >>> for s in suggestions:
            ...     print(s['example'])
            "How many communities in Region IX?"
            "How many communities by livelihood?"
        """
        suggestions = []

        # Get candidate templates
        if category:
            candidates = self.registry.get_templates_by_category(category)
        else:
            candidates = self.registry.get_all_templates()

        # Find partial matches
        partial_lower = partial_query.lower()

        for template in candidates:
            # Check if any example starts with partial query
            for example in template.examples:
                if example.lower().startswith(partial_lower):
                    suggestions.append({
                        'template_id': template.id,
                        'category': template.category,
                        'example': example,
                        'description': template.description,
                        'priority': template.priority,
                    })
                    break  # Only add one example per template

            if len(suggestions) >= max_suggestions:
                break

        # Sort by priority
        suggestions.sort(key=lambda x: x['priority'], reverse=True)

        return suggestions[:max_suggestions]


# Singleton instance
_matcher = None


def get_template_matcher() -> TemplateMatcher:
    """
    Get singleton template matcher instance.

    Returns:
        The global TemplateMatcher instance

    Example:
        >>> from common.ai_services.chat.template_matcher import get_template_matcher
        >>> matcher = get_template_matcher()
    """
    global _matcher
    if _matcher is None:
        _matcher = TemplateMatcher()
    return _matcher
