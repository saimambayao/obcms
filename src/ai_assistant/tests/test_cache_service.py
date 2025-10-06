"""
Tests for Cache Service.
"""

import pytest
from unittest.mock import MagicMock, patch

from django.core.cache import cache
from django.test import TestCase

from ai_assistant.services.cache_service import CacheService, PolicyCacheManager


class TestCacheService(TestCase):
    """Test cases for CacheService."""

    def setUp(self):
        """Set up test fixtures."""
        self.cache_service = CacheService()
        # Clear cache before each test
        cache.clear()
        self.cache_service.reset_stats()

    def tearDown(self):
        """Clean up after each test."""
        cache.clear()

    def test_initialization(self):
        """Test service initialization."""
        service = CacheService()

        assert service.DEFAULT_TTL == 86400  # 24 hours
        assert service.STATIC_CONTENT_TTL == 604800  # 7 days
        assert service.SHORT_TTL == 3600  # 1 hour

    def test_cache_set_and_get(self):
        """Test basic cache operations."""
        key = "test_key"
        value = {"data": "test"}

        # Set value
        success = self.cache_service.set(key, value, ttl=60)
        assert success is True

        # Get value
        retrieved = self.cache_service.get(key)
        assert retrieved == value

    def test_cache_miss(self):
        """Test cache miss."""
        value = self.cache_service.get("nonexistent_key")
        assert value is None

    def test_get_or_generate(self):
        """Test get_or_generate with cache miss."""
        key_params = {"param1": "value1"}
        generator_called = False

        def generator():
            nonlocal generator_called
            generator_called = True
            return {"generated": "data"}

        # First call - cache miss
        result = self.cache_service.get_or_generate(
            key_params=key_params,
            generator_func=generator,
            ttl=60
        )

        assert generator_called is True
        assert result == {"generated": "data"}
        assert self.cache_service.stats['misses'] == 1

        # Second call - cache hit
        generator_called = False
        result2 = self.cache_service.get_or_generate(
            key_params=key_params,
            generator_func=generator,
            ttl=60
        )

        assert generator_called is False
        assert result2 == {"generated": "data"}
        assert self.cache_service.stats['hits'] == 1

    def test_cache_invalidation(self):
        """Test cache invalidation."""
        key = "test_key"
        value = {"data": "test"}

        # Set and verify
        self.cache_service.set(key, value)
        assert self.cache_service.get(key) == value

        # Invalidate
        success = self.cache_service.invalidate(key)
        assert success is True

        # Verify invalidated
        assert self.cache_service.get(key) is None

    def test_key_generation(self):
        """Test cache key generation."""
        params1 = {"a": 1, "b": 2}
        params2 = {"b": 2, "a": 1}  # Different order, same content
        params3 = {"a": 1, "b": 3}  # Different value

        key1 = self.cache_service.generate_key(params1)
        key2 = self.cache_service.generate_key(params2)
        key3 = self.cache_service.generate_key(params3)

        # Same params (different order) should generate same key
        assert key1 == key2

        # Different params should generate different key
        assert key1 != key3

    def test_ttl_by_content_type(self):
        """Test TTL selection by content type."""
        ttl_static = self.cache_service.get_ttl_for_content_type('static')
        ttl_chat = self.cache_service.get_ttl_for_content_type('chat')
        ttl_analysis = self.cache_service.get_ttl_for_content_type('analysis')

        assert ttl_static == 604800  # 7 days
        assert ttl_chat == 3600  # 1 hour
        assert ttl_analysis == 86400  # 24 hours

    def test_cache_statistics(self):
        """Test cache statistics tracking."""
        # Initial stats
        stats = self.cache_service.get_stats()
        assert stats['hits'] == 0
        assert stats['misses'] == 0
        assert stats['hit_rate'] == 0

        # Perform operations
        key_params = {"test": "data"}
        self.cache_service.get_or_generate(
            key_params=key_params,
            generator_func=lambda: "value"
        )  # Miss

        self.cache_service.get_or_generate(
            key_params=key_params,
            generator_func=lambda: "value"
        )  # Hit

        # Check stats
        stats = self.cache_service.get_stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 50.0

    def test_cache_warming(self):
        """Test cache warming."""
        data_items = [
            ({"id": 1}, "value1"),
            ({"id": 2}, "value2"),
            ({"id": 3}, "value3"),
        ]

        count = self.cache_service.warm_cache(
            data_items=data_items,
            prefix="test_prefix",
            ttl=60
        )

        assert count == 3

        # Verify items are cached
        for key_params, expected_value in data_items:
            key = self.cache_service.generate_key(key_params, "test_prefix")
            assert self.cache_service.get(key) == expected_value

    def test_stats_reset(self):
        """Test statistics reset."""
        # Generate some stats
        self.cache_service.stats['hits'] = 10
        self.cache_service.stats['misses'] = 5

        # Reset
        self.cache_service.reset_stats()

        # Verify reset
        assert self.cache_service.stats['hits'] == 0
        assert self.cache_service.stats['misses'] == 0


class TestPolicyCacheManager(TestCase):
    """Test cases for PolicyCacheManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = PolicyCacheManager()
        cache.clear()

    def tearDown(self):
        """Clean up after each test."""
        cache.clear()

    def test_cache_policy_analysis(self):
        """Test caching policy analysis."""
        policy_id = "policy_123"
        analysis_type = "impact_assessment"
        analysis_data = {
            "impact": "high",
            "recommendations": ["rec1", "rec2"]
        }

        cache_key = self.manager.cache_policy_analysis(
            policy_id=policy_id,
            analysis_type=analysis_type,
            analysis_data=analysis_data
        )

        assert cache_key is not None
        assert len(cache_key) > 0

    def test_get_policy_analysis(self):
        """Test retrieving cached policy analysis."""
        policy_id = "policy_456"
        analysis_type = "stakeholder_analysis"
        analysis_data = {"stakeholders": ["group1", "group2"]}

        # Cache the analysis
        self.manager.cache_policy_analysis(
            policy_id=policy_id,
            analysis_type=analysis_type,
            analysis_data=analysis_data
        )

        # Retrieve it
        retrieved = self.manager.get_policy_analysis(
            policy_id=policy_id,
            analysis_type=analysis_type
        )

        assert retrieved == analysis_data

    def test_get_nonexistent_analysis(self):
        """Test retrieving nonexistent analysis."""
        result = self.manager.get_policy_analysis(
            policy_id="nonexistent",
            analysis_type="analysis"
        )

        assert result is None

    @patch('django.core.cache.cache.keys')
    @patch('django.core.cache.cache.delete')
    def test_invalidate_policy_cache(self, mock_delete, mock_keys):
        """Test invalidating all cache entries for a policy."""
        policy_id = "policy_789"

        # Mock keys return
        mock_keys.return_value = [
            f"policy_analysis:hash1_{policy_id}",
            f"policy_analysis:hash2_{policy_id}",
        ]

        count = self.manager.invalidate_policy_cache(policy_id)

        # Should delete matching keys
        assert mock_delete.call_count == 2


@pytest.mark.django_db
class TestCacheServiceIntegration:
    """Integration tests for cache service."""

    def test_cache_with_redis(self):
        """Test cache operations with actual Redis backend."""
        service = CacheService()

        # Clear cache
        cache.clear()

        # Test operations
        key_params = {"integration_test": True}
        value = {"data": "integration_test_value"}

        # Generate and cache
        result = service.get_or_generate(
            key_params=key_params,
            generator_func=lambda: value,
            ttl=60
        )

        assert result == value

        # Verify cached
        cache_key = service.generate_key(key_params)
        cached_value = cache.get(cache_key)
        assert cached_value == value

        # Clean up
        cache.delete(cache_key)
