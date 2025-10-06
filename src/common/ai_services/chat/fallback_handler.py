"""
Fallback Handler for Failed Queries

Provides helpful suggestions and guidance when queries fail.
No AI required - uses pattern matching, similarity analysis, and templates.
"""

import logging
from datetime import timedelta
from typing import Dict, List, Optional

from django.core.cache import cache
from django.utils import timezone

from .query_corrector import get_query_corrector
from .similarity import get_similarity_calculator

logger = logging.getLogger(__name__)


class FallbackHandler:
    """
    Handle failed queries with helpful suggestions and alternatives.

    Features:
    - Automatic spelling correction
    - Similar successful query finder
    - Template-based query examples
    - Failure reason analysis
    - Query builder suggestions
    """

    # Common query templates by intent
    QUERY_TEMPLATES = {
        'data_query': {
            'communities': [
                "How many communities in {location}?",
                "Show me communities in {location}",
                "List all communities in {location}",
                "Count communities in {location}",
                "Communities with {livelihood} livelihood",
                "Show me {ethnic_group} communities",
            ],
            'workshops': [
                "How many workshops in {location}?",
                "Show me MANA assessments in {location}",
                "List workshops conducted in {location}",
                "Recent workshops in {location}",
                "Workshops about {theme}",
            ],
            'policies': [
                "Show me all policy recommendations",
                "List active policy recommendations",
                "How many policy recommendations?",
                "Show me draft policies",
                "Policies for {sector} sector",
            ],
            'partnerships': [
                "List all partnerships",
                "Show me active partnerships",
                "How many partnerships in {location}?",
                "Count coordination partnerships",
                "Partnerships with {organization}",
            ],
            'projects': [
                "Show me all projects",
                "List projects in {location}",
                "How many ongoing projects?",
                "Projects by {ministry}",
                "Completed projects in {location}",
            ],
        },
        'analysis': {
            'communities': [
                "What are the top needs in {location}?",
                "Most common ethnolinguistic groups in {location}",
                "Distribution of livelihoods in {location}",
                "Community trends in {location}",
            ],
            'workshops': [
                "What are the most common workshop themes?",
                "Workshop participation trends",
                "Assessment priorities by {location}",
            ],
        }
    }

    # Failure patterns and explanations
    FAILURE_PATTERNS = {
        'missing_location': {
            'indicators': ['communities', 'workshops', 'projects'],
            'explanation': 'This query usually requires a location (region, province, or municipality)',
            'suggestion': 'Try adding "in Region IX" or "in Zamboanga del Sur"',
        },
        'unrecognized_term': {
            'indicators': ['typo', 'misspelling', 'unknown'],
            'explanation': 'Some terms in your query were not recognized',
            'suggestion': 'Check spelling or use the query builder',
        },
        'ambiguous_query': {
            'indicators': ['unclear', 'multiple', 'which'],
            'explanation': 'Your query could mean multiple things',
            'suggestion': 'Try being more specific about what you want to know',
        },
        'unsupported_query': {
            'indicators': ['cannot', 'unsupported', 'not available'],
            'explanation': 'This type of query is not yet supported',
            'suggestion': 'Try using the visual query builder or manual filtering',
        },
    }

    def __init__(self):
        """Initialize fallback handler."""
        self.corrector = get_query_corrector()
        self.similarity_calc = get_similarity_calculator()
        self._cache_timeout = 300  # 5 minutes

    def handle_failed_query(
        self,
        query: str,
        intent: str = 'data_query',
        entities: Optional[Dict] = None
    ) -> Dict:
        """
        Handle a failed query with comprehensive suggestions.

        Args:
            query: Original user query
            intent: Classified intent (data_query, analysis, etc.)
            entities: Extracted entities (if any)

        Returns:
            Dictionary with:
                - type: 'query_failed'
                - original_query: Original query string
                - error_analysis: Failure analysis
                - suggestions: Corrected queries, similar queries, templates
                - alternatives: Query builder, help links

        Example:
            >>> handler = FallbackHandler()
            >>> result = handler.handle_failed_query(
            ...     "comunitys in regon 9",
            ...     'data_query',
            ...     {}
            ... )
            >>> print(result['suggestions']['corrected_queries'])
            ['How many communities in Region IX?', 'Show me communities in Region IX']
        """
        entities = entities or {}

        # Step 1: Analyze failure reason
        error_analysis = self.analyze_failure_reason(query, intent, entities)

        # Step 2: Generate corrected queries
        corrected_queries = self.generate_suggestions(query)

        # Step 3: Find similar successful queries
        similar_queries = self.find_similar_successful_queries(query, limit=5)

        # Step 4: Get template examples
        template_examples = self.get_query_templates_for_intent(intent, entities)

        # Step 5: Build alternative actions
        alternatives = self._build_alternatives(query, intent)

        return {
            'type': 'query_failed',
            'original_query': query,
            'error_analysis': error_analysis,
            'suggestions': {
                'corrected_queries': corrected_queries,
                'similar_queries': similar_queries,
                'template_examples': template_examples,
            },
            'alternatives': alternatives,
        }

    def analyze_failure_reason(
        self,
        query: str,
        intent: str,
        entities: Dict
    ) -> Dict[str, any]:
        """
        Analyze why a query failed.

        Args:
            query: Failed query
            intent: Query intent
            entities: Extracted entities

        Returns:
            Dictionary with:
                - likely_issue: Issue type (missing_location, unrecognized_term, etc.)
                - confidence: Confidence in diagnosis (0.0 to 1.0)
                - explanation: Human-readable explanation
                - suggestion: What to do next
        """
        query_lower = query.lower()
        scores = {}

        # Score each failure pattern
        for pattern_name, pattern_info in self.FAILURE_PATTERNS.items():
            score = 0.0

            # Check indicators
            indicators = pattern_info.get('indicators', [])
            matches = sum(1 for indicator in indicators if indicator in query_lower)
            if matches > 0:
                score += 0.5

            # Check for missing location
            if pattern_name == 'missing_location':
                if any(term in query_lower for term in ['communities', 'workshops', 'projects']):
                    if not any(loc in query_lower for loc in ['region', 'province', 'zamboanga', 'davao']):
                        score += 0.6

            # Check for typos
            if pattern_name == 'unrecognized_term':
                corrected = self.corrector.correct_spelling(query)
                if corrected != query:
                    score += 0.7

            # Check for ambiguity
            if pattern_name == 'ambiguous_query':
                if len(query.split()) < 3:  # Very short query
                    score += 0.4
                if not entities or len(entities) == 0:
                    score += 0.3

            scores[pattern_name] = min(score, 1.0)

        # Get highest scoring pattern
        if scores:
            likely_issue = max(scores, key=scores.get)
            confidence = scores[likely_issue]
        else:
            likely_issue = 'unsupported_query'
            confidence = 0.5

        pattern_info = self.FAILURE_PATTERNS.get(likely_issue, {})

        return {
            'likely_issue': likely_issue,
            'confidence': confidence,
            'explanation': pattern_info.get('explanation', 'Query could not be processed'),
            'suggestion': pattern_info.get('suggestion', 'Try rephrasing your query'),
        }

    def generate_suggestions(self, query: str) -> List[str]:
        """
        Generate suggested corrected queries.

        Args:
            query: Original query

        Returns:
            List of corrected query suggestions
        """
        suggestions = []

        # Get corrected version
        corrected = self.corrector.correct_spelling(query)
        if corrected != query:
            suggestions.append(corrected)

        # Get alternative phrasings
        alternatives = self.corrector.suggest_alternatives(query, limit=4)
        suggestions.extend(alternatives)

        # Remove duplicates while preserving order
        unique_suggestions = []
        seen = set()
        for suggestion in suggestions:
            suggestion_lower = suggestion.lower()
            if suggestion_lower not in seen:
                unique_suggestions.append(suggestion)
                seen.add(suggestion_lower)

        return unique_suggestions[:5]  # Top 5 suggestions

    def find_similar_successful_queries(
        self,
        query: str,
        limit: int = 5
    ) -> List[str]:
        """
        Find similar successful queries from history.

        Args:
            query: Failed query
            limit: Maximum number of results

        Returns:
            List of similar successful query strings

        Uses caching to improve performance.
        """
        # Check cache first
        # Sanitize cache key - remove spaces and special chars for memcached compatibility
        import hashlib
        query_hash = hashlib.md5(query.encode()).hexdigest()[:16]
        cache_key = f'similar_queries_{query_hash}'
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        try:
            # Import here to avoid circular dependency
            from common.models import ChatMessage

            # Get successful queries from last 30 days
            cutoff_date = timezone.now() - timedelta(days=30)
            successful_queries = ChatMessage.objects.filter(
                confidence__gte=0.7,
                created_at__gte=cutoff_date
            ).values_list('user_message', flat=True).distinct()[:100]

            # Calculate similarity
            candidates = list(successful_queries)
            similar = self.similarity_calc.find_most_similar(
                query,
                candidates,
                threshold=0.5,  # Only return reasonably similar queries
                limit=limit
            )

            # Extract just the query strings
            result = [q for q, score in similar]

            # Cache result
            cache.set(cache_key, result, self._cache_timeout)

            return result

        except Exception as e:
            logger.warning(f"Could not find similar queries: {e}")
            return []

    def get_query_templates_for_intent(
        self,
        intent: str,
        entities: Optional[Dict] = None
    ) -> List[str]:
        """
        Get query templates for given intent.

        Args:
            intent: Query intent (data_query, analysis, etc.)
            entities: Optional entities to fill templates

        Returns:
            List of example query templates
        """
        entities = entities or {}
        templates = []

        intent_templates = self.QUERY_TEMPLATES.get(intent, {})

        # Get templates for detected entities
        for entity_type, entity_templates in intent_templates.items():
            if entity_type in entities or not entities:
                templates.extend(entity_templates)

        # Limit to 5 templates
        templates = templates[:5]

        # Try to fill in placeholders if we have entities
        filled_templates = []
        for template in templates:
            filled = template

            # Replace placeholders
            if '{location}' in template and 'location' in entities:
                filled = filled.replace('{location}', entities['location'])
            elif '{location}' in template:
                filled = filled.replace('{location}', 'Region IX')

            if '{livelihood}' in template:
                filled = filled.replace('{livelihood}', 'fishing')

            if '{ethnic_group}' in template:
                filled = filled.replace('{ethnic_group}', 'Maranao')

            if '{theme}' in template:
                filled = filled.replace('{theme}', 'livelihood')

            if '{sector}' in template:
                filled = filled.replace('{sector}', 'education')

            if '{organization}' in template:
                filled = filled.replace('{organization}', 'BARMM')

            if '{ministry}' in template:
                filled = filled.replace('{ministry}', 'MSWDO')

            filled_templates.append(filled)

        return filled_templates

    def _build_alternatives(self, query: str, intent: str) -> List[Dict]:
        """
        Build alternative action suggestions.

        Args:
            query: Original query
            intent: Query intent

        Returns:
            List of alternative actions
        """
        alternatives = [
            {
                'type': 'query_builder',
                'label': 'Build query step-by-step',
                'description': 'Use visual query builder (guaranteed to work)',
                'action': 'open_query_builder',
                'icon': 'fa-magic',
            },
            {
                'type': 'help',
                'label': 'Learn query syntax',
                'description': 'See examples and documentation',
                'action': 'open_help',
                'url': '/help/chat-queries/',
                'icon': 'fa-book',
            },
        ]

        # Add intent-specific alternatives
        if intent == 'data_query':
            alternatives.append({
                'type': 'direct_search',
                'label': 'Use advanced search',
                'description': 'Search with filters in the module',
                'action': 'open_search',
                'icon': 'fa-search',
            })

        return alternatives

    def get_fallback_stats(self) -> Dict:
        """
        Get statistics about fallback usage.

        Returns:
            Dictionary with fallback metrics
        """
        try:
            from common.models import ChatMessage

            # Get queries from last 30 days
            cutoff_date = timezone.now() - timedelta(days=30)
            total_queries = ChatMessage.objects.filter(
                created_at__gte=cutoff_date
            ).count()

            failed_queries = ChatMessage.objects.filter(
                created_at__gte=cutoff_date,
                confidence__lt=0.5
            ).count()

            fallback_rate = (failed_queries / total_queries * 100) if total_queries > 0 else 0

            return {
                'total_queries': total_queries,
                'failed_queries': failed_queries,
                'fallback_rate': round(fallback_rate, 2),
                'period_days': 30,
            }

        except Exception as e:
            logger.warning(f"Could not get fallback stats: {e}")
            return {
                'total_queries': 0,
                'failed_queries': 0,
                'fallback_rate': 0,
                'period_days': 30,
            }


# Singleton instance
_handler = None


def get_fallback_handler() -> FallbackHandler:
    """Get singleton fallback handler instance."""
    global _handler
    if _handler is None:
        _handler = FallbackHandler()
    return _handler
