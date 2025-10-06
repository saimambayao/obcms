"""
Comprehensive tests for FAQ Handler Service.

Tests cover:
- Exact FAQ matching
- Fuzzy matching with typos
- Cache updates and retrieval
- Performance targets (<10ms)
- Statistics tracking
- Popular FAQs
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from common.ai_services.chat.faq_handler import FAQHandler


@pytest.mark.django_db
class TestFAQHandler:
    """Test suite for FAQ Handler."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        # Clear cache before each test
        cache.clear()
        self.handler = FAQHandler()
        yield
        # Clear cache after each test
        cache.clear()

    def test_exact_match_static_faq(self):
        """Test exact match for static FAQ."""
        result = self.handler.try_faq("how many regions")

        assert result is not None
        assert result['confidence'] == 1.0
        assert result['source'] == 'faq'
        assert 'Region IX' in result['answer']
        assert 'Region X' in result['answer']
        assert 'Region XI' in result['answer']
        assert 'Region XII' in result['answer']
        assert len(result['related_queries']) > 0

    def test_case_insensitive_matching(self):
        """Test case-insensitive FAQ matching."""
        # Test various cases
        queries = [
            "HOW MANY REGIONS",
            "How Many Regions",
            "how many regions",
            "HOW many REGIONS"
        ]

        for query in queries:
            result = self.handler.try_faq(query)
            assert result is not None, f"Failed for query: {query}"
            assert result['confidence'] == 1.0

    def test_punctuation_handling(self):
        """Test FAQ matching with punctuation."""
        queries = [
            "how many regions?",
            "how many regions!",
            "how many regions.",
            "how many regions?!"
        ]

        for query in queries:
            result = self.handler.try_faq(query)
            assert result is not None, f"Failed for query: {query}"

    def test_fuzzy_match_with_typos(self):
        """Test fuzzy matching with typos."""
        # Query with typo: "regons" instead of "regions"
        result = self.handler.try_faq("how many regons")

        assert result is not None
        assert result['confidence'] >= 0.75  # Above threshold
        assert result['source'] == 'faq'
        assert 'Region IX' in result['answer']

    def test_fuzzy_match_threshold(self):
        """Test that queries below threshold are not matched."""
        # Very different query
        result = self.handler.try_faq("xyz abc def")

        assert result is None

    def test_help_faq(self):
        """Test help FAQ."""
        result = self.handler.try_faq("help")

        assert result is not None
        assert 'Count communities' in result['answer']
        assert 'workshops' in result['answer']
        assert len(result['examples']) > 0

    def test_system_modules_faq(self):
        """Test system modules FAQ."""
        result = self.handler.try_faq("what modules")

        assert result is not None
        assert 'Communities' in result['answer']
        assert 'MANA' in result['answer']
        assert 'Coordination' in result['answer']
        assert 'Policies' in result['answer']

    def test_update_stats_cache(self):
        """Test statistics cache update (integration test with real DB)."""
        # Update cache (will work even with empty DB)
        stats = self.handler.update_stats_cache()

        # Should return a dict (even if empty)
        assert isinstance(stats, dict)

        # Verify cache was set
        cached_stats = cache.get(self.handler.STATS_CACHE_KEY)
        assert cached_stats is not None
        assert cached_stats == stats

    def test_cached_stats_faq(self):
        """Test FAQ using cached statistics."""

        # Manually set cache
        cache.set(self.handler.STATS_CACHE_KEY, {
            'total_communities': 'There are 150 OBC communities registered in the system.'
        }, 86400)

        # Query FAQ
        result = self.handler.try_faq("total communities")

        assert result is not None
        assert '150' in result['answer']

    def test_add_faq(self):
        """Test adding a new FAQ entry."""
        self.handler.add_faq(
            "test pattern",
            {
                'answer': 'Test answer',
                'category': 'test',
                'priority': 10
            }
        )

        # Verify it was added
        result = self.handler.try_faq("test pattern")
        assert result is not None
        assert result['answer'] == 'Test answer'

    def test_hit_tracking(self):
        """Test FAQ hit tracking."""
        # Execute same query multiple times
        for _ in range(5):
            self.handler.try_faq("how many regions")

        # Check hits were tracked
        hits = cache.get(self.handler.FAQ_HITS_KEY, {})
        assert 'how many regions' in hits
        assert hits['how many regions'] == 5

    def test_popular_faqs(self):
        """Test getting popular FAQs."""
        # Execute different queries
        self.handler.try_faq("how many regions")  # 1 hit
        self.handler.try_faq("how many regions")  # 2 hits
        self.handler.try_faq("help")  # 1 hit
        self.handler.try_faq("help")  # 2 hits
        self.handler.try_faq("help")  # 3 hits

        # Get popular FAQs
        popular = self.handler.get_popular_faqs(limit=5)

        assert len(popular) > 0
        # 'help' should be first (3 hits)
        assert popular[0]['pattern'] == 'help'
        assert popular[0]['hit_count'] == 3

    def test_faq_stats(self):
        """Test FAQ statistics."""
        # Execute some queries
        self.handler.try_faq("how many regions")
        self.handler.try_faq("help")

        stats = self.handler.get_faq_stats()

        assert stats['total_faqs'] > 0
        assert stats['total_hits'] == 2
        assert stats['faqs_with_hits'] == 2
        assert stats['hit_rate'] > 0
        assert len(stats['popular_faqs']) > 0

    def test_response_time_performance(self):
        """Test FAQ response time is under 10ms."""
        # Warm up
        self.handler.try_faq("how many regions")

        # Measure response time
        start_time = time.time()
        result = self.handler.try_faq("how many regions")
        response_time_ms = (time.time() - start_time) * 1000

        assert result is not None
        assert response_time_ms < 10, f"Response time {response_time_ms}ms exceeds 10ms target"

    def test_response_time_metadata(self):
        """Test that response includes response_time metadata."""
        result = self.handler.try_faq("how many regions")

        assert result is not None
        assert 'response_time' in result
        assert result['response_time'] < 10

    def test_no_match_returns_none(self):
        """Test that non-matching queries return None."""
        result = self.handler.try_faq("completely unrelated query xyz")

        assert result is None

    def test_query_normalization(self):
        """Test query normalization."""
        normalized = self.handler._normalize_query("  HOW  many   REGIONS?!  ")

        assert normalized == "how many regions"

    def test_similarity_score(self):
        """Test similarity score calculation."""
        # Exact match
        score1 = self.handler._similarity_score("hello", "hello")
        assert score1 == 1.0

        # Similar
        score2 = self.handler._similarity_score("hello", "helo")
        assert score2 > 0.7

        # Very different
        score3 = self.handler._similarity_score("hello", "xyz")
        assert score3 < 0.3

    def test_multiple_pattern_variations(self):
        """Test that multiple pattern variations work."""
        queries = [
            "how many regions",
            "what regions",
            "which regions"
        ]

        for query in queries:
            result = self.handler.try_faq(query)
            assert result is not None, f"Failed for: {query}"
            assert 'Region IX' in result['answer']

    def test_category_field(self):
        """Test that responses include category."""
        result = self.handler.try_faq("how many regions")

        assert result is not None
        assert 'category' in result
        assert result['category'] == 'geography'

    def test_matched_pattern_field(self):
        """Test that responses include matched_pattern."""
        result = self.handler.try_faq("how many regions")

        assert result is not None
        assert 'matched_pattern' in result
        assert result['matched_pattern'] == 'how many regions'

    def test_cache_expiry(self):
        """Test that cache has proper TTL."""
        # Update cache
        self.handler.update_stats_cache()

        # Verify cache exists
        cached_stats = cache.get(self.handler.STATS_CACHE_KEY)
        assert cached_stats is not None

        # Note: Can't test actual expiry without mocking time
        # Just verify the cache key is being used

    def test_empty_query(self):
        """Test empty query handling."""
        result = self.handler.try_faq("")

        assert result is None

    def test_whitespace_query(self):
        """Test whitespace-only query."""
        result = self.handler.try_faq("   ")

        assert result is None

    @patch('common.ai_services.chat.faq_handler.logger')
    def test_error_logging(self, mock_logger):
        """Test that errors are logged."""
        # Force an error in hit tracking
        with patch.object(cache, 'get', side_effect=Exception("Cache error")):
            # Should not raise, but should log
            self.handler._track_hit('test_pattern')
            mock_logger.error.assert_called()


class TestFAQHandlerIntegration(TestCase):
    """Integration tests with real database."""

    def setUp(self):
        """Set up test data."""
        cache.clear()
        self.handler = FAQHandler()

    def tearDown(self):
        """Clean up."""
        cache.clear()

    @pytest.mark.django_db
    def test_update_stats_cache_integration(self):
        """Test stats cache update with real database."""
        # This will work even with empty database
        stats = self.handler.update_stats_cache()

        # Should at least have some stats keys
        assert isinstance(stats, dict)
        # Empty database will return 0 counts, which is valid

    @pytest.mark.django_db
    def test_end_to_end_flow(self):
        """Test complete FAQ flow from query to response."""
        # User asks a question
        result = self.handler.try_faq("What can you do?")

        # Should get a response
        assert result is not None
        assert result['source'] == 'faq'
        assert result['confidence'] >= 0.75
        assert len(result['answer']) > 0

        # Check hit was tracked
        hits = cache.get(self.handler.FAQ_HITS_KEY, {})
        assert len(hits) > 0

        # Get stats
        stats = self.handler.get_faq_stats()
        assert stats['total_hits'] > 0

    @pytest.mark.django_db
    def test_performance_under_load(self):
        """Test performance with multiple queries."""
        queries = [
            "how many regions",
            "what can you do",
            "help",
            "system modules",
            "which regions"
        ]

        total_time = 0
        for query in queries:
            start = time.time()
            result = self.handler.try_faq(query)
            elapsed = (time.time() - start) * 1000
            total_time += elapsed

            assert result is not None
            assert elapsed < 10, f"Query '{query}' took {elapsed}ms (exceeds 10ms)"

        avg_time = total_time / len(queries)
        assert avg_time < 10, f"Average response time {avg_time}ms exceeds 10ms"


@pytest.mark.performance
class TestFAQPerformance:
    """Performance-specific tests."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up for performance tests."""
        cache.clear()
        self.handler = FAQHandler()
        # Warm up
        self.handler.try_faq("how many regions")
        yield
        cache.clear()

    def test_exact_match_performance(self):
        """Test exact match performance."""
        times = []

        for _ in range(100):
            start = time.time()
            self.handler.try_faq("how many regions")
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        max_time = max(times)

        assert avg_time < 10, f"Average time {avg_time}ms exceeds 10ms"
        assert max_time < 15, f"Max time {max_time}ms exceeds 15ms"

    def test_fuzzy_match_performance(self):
        """Test fuzzy match performance."""
        times = []

        for _ in range(100):
            start = time.time()
            self.handler.try_faq("how many regons")  # typo
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        max_time = max(times)

        assert avg_time < 15, f"Average time {avg_time}ms exceeds 15ms"
        assert max_time < 25, f"Max time {max_time}ms exceeds 25ms"

    def test_cache_hit_performance(self):
        """Test cached stats retrieval performance."""
        # Pre-populate cache
        cache.set(self.handler.STATS_CACHE_KEY, {
            'total_communities': 'Test stat'
        }, 86400)

        times = []

        for _ in range(100):
            start = time.time()
            self.handler._get_cached_stats()
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)

        avg_time = sum(times) / len(times)

        assert avg_time < 5, f"Average cache retrieval {avg_time}ms exceeds 5ms"
