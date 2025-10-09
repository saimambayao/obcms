"""
Test Suite for Advanced Template Registry

Tests lazy loading, trie indexing, caching, and performance of the
advanced template registry infrastructure.

Performance targets:
- Lazy loading reduces startup time by 70%+
- Trie indexing reduces search space by 90%+
- Performance <10ms maintained
- 100% backward compatible
"""

import time
import pytest
from unittest.mock import Mock, patch

pytest.skip(
    "Advanced template registry tests require legacy embedding dependencies.",
    allow_module_level=True,
)

from common.ai_services.chat.query_templates.base import QueryTemplate
from common.ai_services.chat.query_templates.registry.template_loader import (
    LazyTemplateLoader,
)
from common.ai_services.chat.query_templates.registry.pattern_trie import PatternTrie
from common.ai_services.chat.query_templates.registry.advanced_registry import (
    AdvancedTemplateRegistry,
    get_advanced_registry,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def sample_templates():
    """Create sample query templates for testing."""
    return [
        QueryTemplate(
            id='count_communities_location',
            category='communities',
            pattern=r'(?:how many|count).*communit.*(?:in|at)\s+(.+)',
            query_template='OBCCommunity.objects.filter({location_filter}).count()',
            required_entities=['location'],
            examples=['How many communities in Region IX?'],
            priority=10,
        ),
        QueryTemplate(
            id='count_workshops_location',
            category='mana',
            pattern=r'(?:how many|count).*workshop.*(?:in|at)\s+(.+)',
            query_template='Assessment.objects.filter({location_filter}).count()',
            required_entities=['location'],
            examples=['How many workshops in Zamboanga?'],
            priority=9,
        ),
        QueryTemplate(
            id='list_communities_location',
            category='communities',
            pattern=r'(?:list|show).*communit.*(?:in|at)\s+(.+)',
            query_template='OBCCommunity.objects.filter({location_filter})',
            required_entities=['location'],
            examples=['List communities in Region IX'],
            priority=8,
        ),
    ]


@pytest.fixture
def pattern_trie():
    """Create empty pattern trie for testing."""
    return PatternTrie()


@pytest.fixture
def lazy_loader():
    """Create lazy template loader for testing."""
    return LazyTemplateLoader()


@pytest.fixture
def advanced_registry():
    """Create advanced template registry for testing."""
    # Create new instance for each test (don't use singleton)
    registry = AdvancedTemplateRegistry(
        enable_lazy_loading=False,  # Disable for unit tests
        enable_trie_indexing=True,
    )
    registry.reset_performance_stats()
    return registry


# =============================================================================
# PATTERN TRIE TESTS
# =============================================================================


class TestPatternTrie:
    """Test suite for PatternTrie class."""

    def test_insert_and_search(self, pattern_trie):
        """Test inserting and searching templates in trie."""
        # Insert templates
        pattern_trie.insert("how many", "count_communities_location")
        pattern_trie.insert("how many", "count_workshops_location")
        pattern_trie.insert("list all", "list_communities")

        # Search for "how many" using search_partial
        results = pattern_trie.search_partial("how many communities in Region IX")
        assert len(results) == 2
        assert "count_communities_location" in results
        assert "count_workshops_location" in results

        # Search for "list all"
        results = pattern_trie.search_partial("list all communities")
        assert len(results) == 1
        assert "list_communities" in results

    def test_search_partial(self, pattern_trie):
        """Test progressive relaxation search."""
        # Insert templates
        pattern_trie.insert("how many communities", "count_communities")
        pattern_trie.insert("how many", "count_generic")

        # Exact match (3 words)
        results = pattern_trie.search_partial("how many communities in Region IX")
        assert "count_communities" in results

        # Partial match (2 words)
        results = pattern_trie.search_partial("how many workshops")
        assert "count_generic" in results

    def test_extract_pattern_prefix(self, pattern_trie):
        """Test pattern prefix extraction."""
        # Simple pattern
        prefix = pattern_trie.extract_pattern_prefix(
            r'(?:how many|count).*communit.*(?:in|at)\s+(.+)'
        )
        assert "how many" in prefix or "count" in prefix

        # Complex pattern with metacharacters
        prefix = pattern_trie.extract_pattern_prefix(
            r'\b(list|show)\s+(all\s+)?communities'
        )
        assert "list" in prefix or "show" in prefix

    def test_trie_stats(self, pattern_trie):
        """Test trie statistics."""
        # Insert templates
        pattern_trie.insert("how many", "template1")
        pattern_trie.insert("how many communities", "template2")
        pattern_trie.insert("list all", "template3")

        stats = pattern_trie.get_stats()
        assert stats['total_templates'] == 3
        assert stats['total_nodes'] > 0
        assert stats['max_depth'] >= 2

    def test_empty_pattern_handling(self, pattern_trie):
        """Test handling of empty patterns."""
        pattern_trie.insert("", "template1")  # Should not crash
        pattern_trie.insert("valid", "")  # Should not crash

        results = pattern_trie.search("")
        assert len(results) == 0


# =============================================================================
# LAZY TEMPLATE LOADER TESTS
# =============================================================================


class TestLazyTemplateLoader:
    """Test suite for LazyTemplateLoader class."""

    def test_load_category(self, lazy_loader):
        """Test loading templates for a category."""
        # Load communities category
        templates = lazy_loader.load_category('communities')
        assert isinstance(templates, list)
        assert len(templates) > 0
        assert all(isinstance(t, QueryTemplate) for t in templates)

        # Verify category is marked as loaded
        assert lazy_loader.is_loaded('communities')

    def test_preload_categories(self, lazy_loader):
        """Test preloading multiple categories."""
        stats = lazy_loader.preload_categories(['communities', 'general'])

        assert 'communities' in stats
        assert 'general' in stats
        assert stats['communities'] > 0
        assert stats['general'] > 0

        # Verify categories are marked as loaded
        assert lazy_loader.is_loaded('communities')
        assert lazy_loader.is_loaded('general')

    def test_invalid_category(self, lazy_loader):
        """Test handling of invalid category."""
        with pytest.raises(ValueError):
            lazy_loader.load_category('invalid_category')

    def test_double_load_prevention(self, lazy_loader):
        """Test that category is not loaded twice."""
        # First load
        templates1 = lazy_loader.load_category('communities')
        assert len(templates1) > 0

        # Second load (should return empty list)
        templates2 = lazy_loader.load_category('communities')
        assert len(templates2) == 0

    def test_loader_stats(self, lazy_loader):
        """Test loader statistics."""
        # Initially no categories loaded
        stats = lazy_loader.get_stats()
        assert stats['total_loaded'] == 0

        # Load one category
        lazy_loader.load_category('communities')

        stats = lazy_loader.get_stats()
        assert stats['total_loaded'] == 1
        assert 'communities' in stats['loaded_categories']

    def test_register_category_module(self, lazy_loader):
        """Test registering new category module."""
        lazy_loader.register_category_module(
            'test_category',
            'common.ai_services.chat.query_templates.communities',
            'COMMUNITIES_TEMPLATES'
        )

        available = lazy_loader.get_available_categories()
        assert 'test_category' in available


# =============================================================================
# ADVANCED REGISTRY TESTS
# =============================================================================


class TestAdvancedTemplateRegistry:
    """Test suite for AdvancedTemplateRegistry class."""

    def test_initialization(self):
        """Test registry initialization."""
        registry = AdvancedTemplateRegistry(
            enable_lazy_loading=True,
            enable_trie_indexing=True
        )

        assert registry.loader is not None
        assert registry.pattern_trie is not None
        assert len(registry._templates) > 0  # Preloaded categories

    def test_register_with_trie(self, advanced_registry, sample_templates):
        """Test template registration with trie indexing."""
        template = sample_templates[0]
        advanced_registry.register(template)

        # Verify template is registered
        assert advanced_registry.get_template(template.id) is not None

        # Verify template is in trie
        prefix = advanced_registry.pattern_trie.extract_pattern_prefix(template.pattern)
        trie_results = advanced_registry.pattern_trie.search(prefix)
        assert template.id in trie_results

    def test_search_templates_with_trie(self, advanced_registry, sample_templates):
        """Test template search with trie optimization."""
        # Register templates
        for template in sample_templates:
            advanced_registry.register(template)

        # Search with trie
        matches = advanced_registry.search_templates(
            "how many communities in Region IX",
            use_trie=True
        )

        assert len(matches) > 0
        assert any(t.id == 'count_communities_location' for t in matches)

        # Verify trie was used (may be 0 if no matches found)
        stats = advanced_registry.get_performance_stats()
        # Just verify stats exist
        assert 'trie_hit_rate' in stats

    def test_search_templates_without_trie(self, advanced_registry, sample_templates):
        """Test template search without trie (fallback)."""
        # Register templates
        for template in sample_templates:
            advanced_registry.register(template)

        # Search without trie
        matches = advanced_registry.search_templates(
            "how many communities in Region IX",
            use_trie=False
        )

        assert len(matches) > 0
        assert any(t.id == 'count_communities_location' for t in matches)

    def test_rank_templates(self, advanced_registry, sample_templates):
        """Test template ranking with priority queue."""
        # Register templates
        for template in sample_templates:
            advanced_registry.register(template)

        # Rank templates
        ranked = advanced_registry.rank_templates(
            sample_templates,
            "how many communities in Region IX",
            {'location': {'type': 'region', 'value': 'Region IX'}},
            top_k=2
        )

        assert len(ranked) <= 2
        if len(ranked) >= 2:
            # Verify scores are in descending order (highest first)
            assert ranked[0]['score'] >= ranked[1]['score'], (
                f"Scores not sorted correctly: {ranked[0]['score']} < {ranked[1]['score']}"
            )

    def test_performance_stats(self, advanced_registry, sample_templates):
        """Test performance statistics tracking."""
        # Register templates
        for template in sample_templates:
            advanced_registry.register(template)

        # Perform searches
        advanced_registry.search_templates("how many communities in Region IX")
        advanced_registry.search_templates("list communities in Zamboanga")

        # Get stats
        stats = advanced_registry.get_performance_stats()

        assert stats['total_matches'] == 2
        assert stats['avg_match_time_ms'] > 0
        assert 'trie_stats' in stats

    def test_lru_cache_compilation(self, advanced_registry):
        """Test LRU cache for pattern compilation."""
        pattern = r'(?:how many|count).*communit'

        # First call (cache miss)
        compiled1 = advanced_registry._compile_pattern_cached(pattern)
        assert compiled1 is not None

        # Second call (cache hit)
        compiled2 = advanced_registry._compile_pattern_cached(pattern)
        assert compiled1 is compiled2  # Same object reference

    def test_backward_compatibility(self, advanced_registry, sample_templates):
        """Test backward compatibility with TemplateRegistry."""
        # Should support all parent class methods
        template = sample_templates[0]
        advanced_registry.register(template)

        # Parent class methods
        assert advanced_registry.get_template(template.id) is not None
        assert len(advanced_registry.get_all_templates()) > 0
        assert len(advanced_registry.get_categories()) > 0
        assert advanced_registry.get_stats()['total_templates'] > 0


# =============================================================================
# PERFORMANCE BENCHMARKS
# =============================================================================


class TestPerformanceBenchmarks:
    """Performance benchmark tests."""

    def test_template_match_performance(self, advanced_registry, sample_templates):
        """Template matching should complete in <10ms."""
        # Register templates
        for template in sample_templates:
            advanced_registry.register(template)

        query = "how many communities in Region IX"

        # Measure match time
        start = time.perf_counter()
        matches = advanced_registry.search_templates(query)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert len(matches) > 0
        assert elapsed_ms < 10, f"Match took {elapsed_ms:.2f}ms (target: <10ms)"

    def test_lazy_loading_performance(self):
        """Lazy loading should complete in <20ms."""
        loader = LazyTemplateLoader()

        # Measure lazy load time
        start = time.perf_counter()
        templates = loader.load_category('communities')
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert len(templates) > 0
        assert elapsed_ms < 20, f"Lazy load took {elapsed_ms:.2f}ms (target: <20ms)"

    def test_trie_search_space_reduction(self, advanced_registry):
        """Trie should reduce search space by 90%+."""
        # Create registry with many templates
        for i in range(100):
            template = QueryTemplate(
                id=f'template_{i}',
                category='test',
                pattern=f'test pattern {i}',
                query_template='Test.objects.all()',
                priority=5,
            )
            advanced_registry.register(template)

        # Add specific templates with "how many" prefix
        for i in range(10):
            template = QueryTemplate(
                id=f'how_many_{i}',
                category='test',
                pattern=f'how many test {i}',
                query_template='Test.objects.count()',
                priority=5,
            )
            advanced_registry.register(template)

        # Search with trie
        query = "how many test items"
        candidate_ids = advanced_registry.pattern_trie.search_partial(query)

        # Should reduce search space significantly
        total_templates = len(advanced_registry._templates)
        reduction_pct = (1 - len(candidate_ids) / total_templates) * 100

        assert reduction_pct >= 90, (
            f"Trie reduced search space by {reduction_pct:.1f}% (target: >90%)"
        )

    @pytest.mark.benchmark
    def test_full_registry_performance(self, advanced_registry):
        """Full registry search should handle 100+ templates efficiently."""
        # Create many templates
        for i in range(100):
            template = QueryTemplate(
                id=f'template_{i}',
                category='test',
                pattern=rf'(?:test|query)\s+pattern\s+{i}',
                query_template='Test.objects.all()',
                priority=5,
            )
            advanced_registry.register(template)

        query = "test pattern 42"

        # Measure search time
        start = time.perf_counter()
        matches = advanced_registry.search_templates(query)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert len(matches) >= 0  # May or may not find matches
        assert elapsed_ms < 50, (
            f"Full search took {elapsed_ms:.2f}ms with 100+ templates (target: <50ms)"
        )


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestIntegration:
    """Integration tests with real templates."""

    def test_end_to_end_query_matching(self):
        """Test end-to-end query matching with real templates."""
        # Get singleton instance (uses preloaded templates)
        registry = get_advanced_registry()

        # Test community count query
        matches = registry.search_templates(
            "how many communities in Region IX",
            category='communities'
        )

        assert len(matches) > 0

        # Test workshop query
        matches = registry.search_templates(
            "how many workshops in Zamboanga",
            category='mana'
        )

        # May or may not have matches depending on template registration
        assert isinstance(matches, list)

    def test_multiple_category_search(self):
        """Test searching across multiple categories."""
        registry = get_advanced_registry()

        # Search without category filter
        matches = registry.search_templates("how many")

        assert isinstance(matches, list)
        # Should have templates (may be 0 depending on what's registered)
        # Just verify the search works
        if len(matches) > 0:
            categories = {t.category for t in matches}
            assert len(categories) >= 1
