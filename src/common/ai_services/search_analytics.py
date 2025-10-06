"""
Search Analytics

Track and analyze search patterns to improve results.
"""

import logging
from collections import Counter
from datetime import datetime, timedelta
from typing import Dict, List

from django.core.cache import cache
from django.db import models

logger = logging.getLogger(__name__)


class SearchAnalytics:
    """
    Track and analyze search patterns.

    Features:
    - Query frequency tracking
    - Popular searches identification
    - Zero-result query detection
    - Search improvement suggestions
    """

    CACHE_PREFIX = 'search_analytics:'
    CACHE_TTL = 86400  # 24 hours

    def __init__(self):
        """Initialize search analytics."""
        pass

    def log_search(
        self,
        query: str,
        results_count: int,
        user_id: int = None,
        modules_searched: List[str] = None
    ):
        """
        Log a search query.

        Args:
            query: Search query
            results_count: Number of results found
            user_id: User who performed search
            modules_searched: Modules included in search
        """
        # Store in cache for recent queries
        cache_key = f"{self.CACHE_PREFIX}recent_queries"
        recent = cache.get(cache_key, [])

        recent.append({
            'query': query,
            'results_count': results_count,
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'modules': modules_searched or [],
        })

        # Keep only last 1000 queries
        recent = recent[-1000:]

        cache.set(cache_key, recent, self.CACHE_TTL)

        # Track zero-result queries separately
        if results_count == 0:
            self._log_zero_result_query(query)

        # Track query frequency
        self._increment_query_count(query)

    def _log_zero_result_query(self, query: str):
        """Track queries with zero results."""
        cache_key = f"{self.CACHE_PREFIX}zero_results"
        zero_results = cache.get(cache_key, [])

        zero_results.append({
            'query': query,
            'timestamp': datetime.now().isoformat(),
        })

        zero_results = zero_results[-500:]  # Keep last 500
        cache.set(cache_key, zero_results, self.CACHE_TTL)

    def _increment_query_count(self, query: str):
        """Increment query frequency counter."""
        cache_key = f"{self.CACHE_PREFIX}query_counts"
        counts = cache.get(cache_key, {})

        normalized = query.lower().strip()
        counts[normalized] = counts.get(normalized, 0) + 1

        cache.set(cache_key, counts, self.CACHE_TTL * 7)  # 7 days

    def get_popular_queries(self, limit: int = 10) -> List[Dict]:
        """
        Get most popular search queries.

        Args:
            limit: Number of queries to return

        Returns:
            List of {'query': str, 'count': int}
        """
        cache_key = f"{self.CACHE_PREFIX}query_counts"
        counts = cache.get(cache_key, {})

        # Sort by count
        sorted_queries = sorted(
            counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {'query': query, 'count': count}
            for query, count in sorted_queries[:limit]
        ]

    def get_zero_result_queries(self, limit: int = 20) -> List[Dict]:
        """
        Get queries with zero results.

        Args:
            limit: Number of queries to return

        Returns:
            List of zero-result queries
        """
        cache_key = f"{self.CACHE_PREFIX}zero_results"
        zero_results = cache.get(cache_key, [])

        return zero_results[-limit:]

    def identify_patterns(self) -> Dict:
        """
        Identify search patterns.

        Returns:
            Dict with pattern insights
        """
        cache_key = f"{self.CACHE_PREFIX}recent_queries"
        recent = cache.get(cache_key, [])

        if not recent:
            return {
                'total_searches': 0,
                'top_keywords': [],
                'popular_modules': [],
                'avg_results': 0,
            }

        # Extract insights
        total = len(recent)
        all_queries = [r['query'] for r in recent]
        all_modules = [m for r in recent for m in r.get('modules', [])]
        all_results = [r['results_count'] for r in recent]

        # Top keywords
        all_words = []
        for query in all_queries:
            words = [w.lower() for w in query.split() if len(w) > 3]
            all_words.extend(words)

        keyword_counts = Counter(all_words)
        top_keywords = [
            {'keyword': k, 'count': v}
            for k, v in keyword_counts.most_common(10)
        ]

        # Popular modules
        module_counts = Counter(all_modules)
        popular_modules = [
            {'module': k, 'count': v}
            for k, v in module_counts.most_common(5)
        ]

        # Average results
        avg_results = sum(all_results) / len(all_results) if all_results else 0

        return {
            'total_searches': total,
            'top_keywords': top_keywords,
            'popular_modules': popular_modules,
            'avg_results': round(avg_results, 1),
            'zero_result_rate': sum(1 for r in all_results if r == 0) / total if total > 0 else 0,
        }

    def suggest_improvements(self) -> List[str]:
        """
        Suggest search improvements based on patterns.

        Returns:
            List of improvement suggestions
        """
        suggestions = []

        # Check zero-result queries
        zero_results = self.get_zero_result_queries(limit=50)
        if len(zero_results) > 10:
            suggestions.append(
                f"High number of zero-result queries ({len(zero_results)}). "
                "Consider expanding vector index coverage."
            )

        # Check patterns
        patterns = self.identify_patterns()

        if patterns['zero_result_rate'] > 0.3:
            suggestions.append(
                f"Zero-result rate is high ({patterns['zero_result_rate']:.1%}). "
                "Review query parsing and index quality."
            )

        if patterns['avg_results'] < 5:
            suggestions.append(
                f"Average results count is low ({patterns['avg_results']}). "
                "Consider lowering similarity threshold."
            )

        # Check popular keywords
        if patterns['top_keywords']:
            top_keyword = patterns['top_keywords'][0]['keyword']
            suggestions.append(
                f"Most searched keyword: '{top_keyword}'. "
                "Ensure good coverage for this topic."
            )

        return suggestions if suggestions else ["Search performance looks good!"]
