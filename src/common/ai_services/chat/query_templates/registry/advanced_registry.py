"""
Advanced Template Registry for OBCMS Chat System

Enhanced registry with lazy loading, trie indexing, and multi-level caching
for scaling to 500+ templates while maintaining <10ms match performance.

Performance Targets:
- Template match: <10ms (99th percentile)
- Registry lookup: <2ms
- Lazy load: <20ms per category
- Cache hit rate: >75%

Architecture:
- Extends TemplateRegistry with optimizations
- LazyTemplateLoader for on-demand loading
- PatternTrie for efficient prefix matching
- LRU cache for pattern compilation and match results
- Priority queue for top-k template ranking
"""

import heapq
import logging
import time
from functools import lru_cache
from typing import Any, Dict, List, Optional

from common.ai_services.chat.query_templates.base import (
    QueryTemplate,
    TemplateRegistry,
)
from common.ai_services.chat.query_templates.registry.template_loader import (
    LazyTemplateLoader,
)
from common.ai_services.chat.query_templates.registry.pattern_trie import PatternTrie

logger = logging.getLogger(__name__)


class AdvancedTemplateRegistry(TemplateRegistry):
    """
    Enhanced template registry with lazy loading and advanced indexing.

    Features:
    - Lazy loading: Load templates on-demand by category
    - Trie indexing: Reduce search space from 500+ to ~50 candidates
    - Multi-level caching: LRU cache for patterns and matches
    - Priority queue: Efficient top-k template ranking

    Usage:
        >>> registry = AdvancedTemplateRegistry()
        >>> templates = registry.search_templates("how many communities in Region IX")
        >>> print(len(templates))
        3
    """

    _advanced_instance: Optional['AdvancedTemplateRegistry'] = None

    def __init__(self, enable_lazy_loading: bool = True, enable_trie_indexing: bool = True):
        """
        Initialize advanced registry with optimizations.

        Args:
            enable_lazy_loading: Enable lazy template loading (default: True)
            enable_trie_indexing: Enable pattern trie indexing (default: True)
        """
        super().__init__()

        # Feature flags
        self.enable_lazy_loading = enable_lazy_loading
        self.enable_trie_indexing = enable_trie_indexing

        # Lazy loading
        self.loader = LazyTemplateLoader() if enable_lazy_loading else None

        # Pattern trie indexing
        self.pattern_trie = PatternTrie() if enable_trie_indexing else None

        # Performance metrics
        self._performance_stats = {
            'match_times': [],
            'cache_hits': 0,
            'cache_misses': 0,
            'trie_hits': 0,
            'trie_misses': 0,
            'lazy_loads': 0,
        }

        # Preload high-priority categories
        if enable_lazy_loading:
            self._preload_high_priority_categories()

        # Build pattern index
        if enable_trie_indexing:
            self._build_pattern_index()

        logger.info(
            f"AdvancedTemplateRegistry initialized: "
            f"lazy_loading={enable_lazy_loading}, "
            f"trie_indexing={enable_trie_indexing}"
        )

    @classmethod
    def get_advanced_instance(cls) -> 'AdvancedTemplateRegistry':
        """
        Get singleton instance of advanced registry.

        Returns:
            The global AdvancedTemplateRegistry instance

        Example:
            >>> registry = AdvancedTemplateRegistry.get_advanced_instance()
        """
        if cls._advanced_instance is None:
            cls._advanced_instance = cls()
        return cls._advanced_instance

    def _preload_high_priority_categories(self) -> None:
        """
        Preload commonly accessed categories during startup.

        High-priority categories:
        - communities: Most frequently queried
        - general: Help and FAQ queries
        - staff: Task management queries
        """
        if not self.loader:
            return

        high_priority = ['communities', 'general', 'staff']

        logger.info(f"Preloading high-priority categories: {high_priority}")

        for category in high_priority:
            try:
                templates = self.loader.load_category(category)
                if templates:
                    self.register_many(templates)
                    logger.debug(f"Preloaded {len(templates)} templates for {category}")
            except ValueError as e:
                logger.error(f"Failed to preload category '{category}': {e}")

        logger.info(
            f"Preloading complete: {len(self._templates)} templates loaded"
        )

    def _build_pattern_index(self) -> None:
        """
        Build trie index from template patterns.

        Extracts first 2-3 words from each pattern as prefix and
        inserts into trie for fast lookup.
        """
        if not self.pattern_trie:
            return

        logger.debug("Building pattern trie index...")

        for template in self.get_all_templates():
            # Extract pattern prefix
            prefix = self.pattern_trie.extract_pattern_prefix(template.pattern)

            if prefix:
                self.pattern_trie.insert(prefix, template.id)

        stats = self.pattern_trie.get_stats()
        logger.info(
            f"Pattern trie built: {stats['total_nodes']} nodes, "
            f"{stats['total_templates']} templates indexed, "
            f"max_depth={stats['max_depth']}"
        )

    def register(self, template: QueryTemplate) -> None:
        """
        Register a query template with trie indexing.

        Args:
            template: QueryTemplate instance to register

        Example:
            >>> registry.register(QueryTemplate(...))
        """
        # Register in parent class
        super().register(template)

        # Add to pattern trie if enabled
        if self.pattern_trie:
            prefix = self.pattern_trie.extract_pattern_prefix(template.pattern)
            if prefix:
                self.pattern_trie.insert(prefix, template.id)

    def get_templates_by_category(self, category: str) -> List[QueryTemplate]:
        """
        Get all templates in a category with lazy loading.

        Args:
            category: Category name

        Returns:
            List of QueryTemplate instances in category

        Example:
            >>> templates = registry.get_templates_by_category('mana')
        """
        # Check if category already loaded
        if category not in self._category_index and self.loader:
            # Lazy load category
            logger.debug(f"Lazy-loading category: {category}")
            start_time = time.perf_counter()

            try:
                templates = self.loader.load_category(category)
                if templates:
                    self.register_many(templates)
                    self._performance_stats['lazy_loads'] += 1

                elapsed_ms = (time.perf_counter() - start_time) * 1000
                logger.info(
                    f"Lazy-loaded {len(templates)} templates for '{category}' "
                    f"in {elapsed_ms:.2f}ms"
                )

            except ValueError as e:
                logger.error(f"Failed to lazy-load category '{category}': {e}")

        # Return templates from parent class
        return super().get_templates_by_category(category)

    def search_templates(
        self,
        query: str,
        category: Optional[str] = None,
        min_priority: int = 1,
        use_trie: bool = True,
    ) -> List[QueryTemplate]:
        """
        Search for templates matching a query with trie optimization.

        Process:
        1. Use trie to get candidate template IDs (~50 instead of 500)
        2. Filter by category if provided
        3. Test regex match only on candidates
        4. Sort by match score

        Args:
            query: User's natural language query
            category: Optional category filter
            min_priority: Minimum priority threshold (1-10)
            use_trie: Use trie indexing if available (default: True)

        Returns:
            List of matching templates, sorted by match score

        Example:
            >>> matches = registry.search_templates(
            ...     "how many communities in zamboanga",
            ...     category='communities'
            ... )
        """
        start_time = time.perf_counter()

        # Lazy load category if needed
        if category and self.loader and not self.loader.is_loaded(category):
            self.get_templates_by_category(category)

        # Get candidate templates
        if use_trie and self.pattern_trie:
            # Use trie to reduce search space
            candidate_ids = self.pattern_trie.search_partial(query)

            if candidate_ids:
                self._performance_stats['trie_hits'] += 1

                # Get candidate templates
                candidates = [
                    self.get_template(tid)
                    for tid in candidate_ids
                    if self.get_template(tid) is not None
                ]

                logger.debug(
                    f"Trie reduced search space: {len(self._templates)} → {len(candidates)}"
                )
            else:
                # Trie miss, fallback to full scan
                self._performance_stats['trie_misses'] += 1
                logger.debug("Trie miss, using full scan")
                candidates = self.get_all_templates()
        else:
            # Trie disabled, use full scan
            candidates = self.get_all_templates()

        # Filter by category
        if category:
            candidates = [t for t in candidates if t.category == category]

        # Filter by priority
        candidates = [t for t in candidates if t.priority >= min_priority]

        # Find matches (expensive regex matching only on candidates)
        matches = [t for t in candidates if t.matches(query)]

        # Record performance
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        self._performance_stats['match_times'].append(elapsed_ms)

        logger.debug(
            f"Search completed in {elapsed_ms:.2f}ms: "
            f"{len(candidates)} candidates → {len(matches)} matches"
        )

        return matches

    def rank_templates(
        self,
        templates: List[QueryTemplate],
        query: str,
        entities: Dict[str, Any],
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Rank templates using priority queue (heap).

        Instead of:
        1. Score all templates (O(n))
        2. Sort all templates (O(n log n))
        3. Return top k (O(k))

        Use priority queue:
        1. Score all templates (O(n))
        2. Maintain heap of top k (O(n log k))
        3. Return heap (O(k log k))

        Performance: O(n log n) → O(n log k), where k << n

        Args:
            templates: List of candidate templates
            query: User's query
            entities: Extracted entities
            top_k: Number of top templates to return (default: 10)

        Returns:
            List of top-k templates with scores

        Example:
            >>> ranked = registry.rank_templates(
            ...     templates,
            ...     "how many communities",
            ...     {'location': {'type': 'region', 'value': 'Region IX'}},
            ...     top_k=5
            ... )
        """
        # Min-heap of top-k templates (score, template)
        # Use negative score for max-heap behavior
        heap = []

        for template in templates:
            score = template.score_match(query, entities)

            if len(heap) < top_k:
                # Heap not full, add template
                heapq.heappush(heap, (-score, template))
            elif score > -heap[0][0]:
                # New template better than worst in heap
                heapq.heapreplace(heap, (-score, template))

        # Convert heap to ranked list (sorted by score descending)
        ranked = sorted(heap, reverse=True)

        return [
            {
                'template': template,
                'score': -score,
                'id': template.id,
                'category': template.category,
                'priority': template.priority,
            }
            for score, template in ranked
        ]

    @lru_cache(maxsize=1000)
    def _compile_pattern_cached(self, pattern: str):
        """
        Compile regex pattern with LRU cache.

        Avoids recompiling the same pattern multiple times.
        Cache size: 1000 patterns (sufficient for 500+ templates)

        Args:
            pattern: Regex pattern string

        Returns:
            Compiled regex pattern

        Example:
            >>> compiled = registry._compile_pattern_cached(r'how many.*communities')
        """
        import re
        return re.compile(pattern, re.IGNORECASE)

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics.

        Returns:
            Dictionary with performance metrics

        Example:
            >>> stats = registry.get_performance_stats()
            >>> print(stats['avg_match_time_ms'])
            3.5
        """
        match_times = self._performance_stats['match_times']

        if match_times:
            avg_match_time = sum(match_times) / len(match_times)
            p99_match_time = sorted(match_times)[int(len(match_times) * 0.99)]
        else:
            avg_match_time = 0
            p99_match_time = 0

        cache_hits = self._performance_stats['cache_hits']
        cache_misses = self._performance_stats['cache_misses']
        total_cache_ops = cache_hits + cache_misses
        cache_hit_rate = (cache_hits / total_cache_ops * 100) if total_cache_ops > 0 else 0

        trie_hits = self._performance_stats['trie_hits']
        trie_misses = self._performance_stats['trie_misses']
        total_trie_ops = trie_hits + trie_misses
        trie_hit_rate = (trie_hits / total_trie_ops * 100) if total_trie_ops > 0 else 0

        return {
            'avg_match_time_ms': avg_match_time,
            'p99_match_time_ms': p99_match_time,
            'total_matches': len(match_times),
            'cache_hit_rate': cache_hit_rate,
            'trie_hit_rate': trie_hit_rate,
            'lazy_loads': self._performance_stats['lazy_loads'],
            'total_templates': len(self._templates),
            'trie_stats': self.pattern_trie.get_stats() if self.pattern_trie else {},
            'loader_stats': self.loader.get_stats() if self.loader else {},
        }

    def reset_performance_stats(self) -> None:
        """Reset performance statistics (mainly for testing)."""
        self._performance_stats = {
            'match_times': [],
            'cache_hits': 0,
            'cache_misses': 0,
            'trie_hits': 0,
            'trie_misses': 0,
            'lazy_loads': 0,
        }
        logger.debug("Performance stats reset")

    def __repr__(self):
        stats = self.get_stats()
        perf_stats = self.get_performance_stats()
        return (
            f"AdvancedTemplateRegistry("
            f"templates={stats['total_templates']}, "
            f"categories={len(stats['categories'])}, "
            f"avg_match_time={perf_stats['avg_match_time_ms']:.2f}ms)"
        )


# =============================================================================
# GLOBAL SINGLETON ACCESSOR
# =============================================================================

_advanced_registry_instance: Optional[AdvancedTemplateRegistry] = None


def get_advanced_registry() -> AdvancedTemplateRegistry:
    """
    Get the global advanced template registry instance.

    This is the recommended way to access the advanced registry.

    Returns:
        The singleton AdvancedTemplateRegistry instance

    Example:
        >>> from common.ai_services.chat.query_templates.registry import get_advanced_registry
        >>> registry = get_advanced_registry()
    """
    global _advanced_registry_instance

    if _advanced_registry_instance is None:
        _advanced_registry_instance = AdvancedTemplateRegistry()

    return _advanced_registry_instance
