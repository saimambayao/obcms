"""
Result Ranker for Cross-Module Search

Ranks and deduplicates results from multiple modules.
"""

import logging
from datetime import date
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ResultRanker:
    """
    Rank search results from multiple modules.

    Ranking factors:
    - Similarity score (50% weight)
    - Recency (20% weight)
    - Completeness (20% weight)
    - User relevance (10% weight)
    """

    # Ranking weights
    SIMILARITY_WEIGHT = 0.5
    RECENCY_WEIGHT = 0.2
    COMPLETENESS_WEIGHT = 0.2
    RELEVANCE_WEIGHT = 0.1

    def __init__(self):
        """Initialize the result ranker."""
        pass

    def rank_cross_module(self, results: Dict[str, List[Dict]], query: str) -> Dict[str, List[Dict]]:
        """
        Rank results from multiple modules.

        Args:
            results: Dict mapping module names to result lists
            query: Original search query

        Returns:
            Ranked results grouped by module
        """
        # Flatten all results with module info
        all_results = []

        for module, items in results.items():
            for item in items:
                item['module'] = module
                item['rank_score'] = self._calculate_rank_score(item, query)
                all_results.append(item)

        # Sort by rank score (descending)
        all_results.sort(key=lambda x: x['rank_score'], reverse=True)

        # Group back by module (preserving rank order)
        grouped = {module: [] for module in results.keys()}

        for item in all_results:
            grouped[item['module']].append(item)

        logger.info(
            f"Ranked {len(all_results)} results across {len(grouped)} modules"
        )

        return grouped

    def _calculate_rank_score(self, item: Dict, query: str) -> float:
        """
        Calculate multi-factor ranking score.

        Args:
            item: Search result item
            query: Search query

        Returns:
            Rank score (0-1)
        """
        score = 0.0

        # 1. Similarity score (0-0.5)
        similarity = item.get('similarity_score', 0.0)
        score += similarity * self.SIMILARITY_WEIGHT

        # 2. Recency (0-0.2)
        recency = self._calculate_recency(item['object'])
        score += recency * self.RECENCY_WEIGHT

        # 3. Completeness (0-0.2)
        completeness = self._assess_completeness(item['object'])
        score += completeness * self.COMPLETENESS_WEIGHT

        # 4. User relevance (0-0.1)
        relevance = self._assess_relevance(item, query)
        score += relevance * self.RELEVANCE_WEIGHT

        return min(score, 1.0)

    def _calculate_recency(self, obj: Any) -> float:
        """
        Calculate recency score (0-1).

        More recent = higher score.
        """
        # Find date field
        date_field = None
        for field in ['created_at', 'updated_at', 'date', 'start_date']:
            if hasattr(obj, field):
                date_field = field
                break

        if not date_field:
            return 0.5  # Neutral score if no date

        obj_date = getattr(obj, date_field)
        if not obj_date:
            return 0.5

        # Convert to date if datetime
        if hasattr(obj_date, 'date'):
            obj_date = obj_date.date()

        # Calculate days old
        days_old = (date.today() - obj_date).days

        # Decay over 365 days (1 year)
        recency_score = max(0, 1 - (days_old / 365))

        return recency_score

    def _assess_completeness(self, obj: Any) -> float:
        """
        Assess data completeness (0-1).

        More complete data = higher score.
        """
        # Check for common optional fields
        optional_fields = [
            'description',
            'details',
            'notes',
            'objectives',
            'expected_outcomes',
            'recommendations',
        ]

        filled_count = 0
        total_count = 0

        for field in optional_fields:
            if hasattr(obj, field):
                total_count += 1
                value = getattr(obj, field)
                if value and str(value).strip():
                    filled_count += 1

        if total_count == 0:
            return 0.5  # Neutral if no optional fields

        completeness = filled_count / total_count
        return completeness

    def _assess_relevance(self, item: Dict, query: str) -> float:
        """
        Assess user relevance (0-1).

        Based on:
        - Query term matches in title/name
        - Module relevance
        """
        obj = item['object']
        query_lower = query.lower()

        # Check title/name fields
        for field in ['title', 'name']:
            if hasattr(obj, field):
                value = getattr(obj, field)
                if value:
                    value_str = str(value).lower()
                    # Exact match in title = high relevance
                    if query_lower in value_str:
                        return 1.0
                    # Partial match = medium relevance
                    query_words = query_lower.split()
                    if any(word in value_str for word in query_words if len(word) > 3):
                        return 0.7

        # Default medium relevance
        return 0.5

    def deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """
        Remove duplicate results.

        Args:
            results: List of search results

        Returns:
            Deduplicated results
        """
        seen = set()
        deduped = []

        for item in results:
            obj = item['object']
            module = item['module']

            # Create unique key
            key = f"{module}:{obj.id}"

            if key not in seen:
                seen.add(key)
                deduped.append(item)

        if len(seen) < len(results):
            logger.info(f"Removed {len(results) - len(seen)} duplicate results")

        return deduped
