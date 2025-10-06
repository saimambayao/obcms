"""
Cache Service - Redis caching layer for AI responses.

This service provides:
- Response caching with TTL
- Cache key generation
- Cache invalidation
- Cache statistics
"""

import hashlib
import json
import logging
from datetime import timedelta
from typing import Any, Dict, Optional

from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


class CacheService:
    """
    Service for caching AI responses and related data.

    Features:
    - Automatic cache key generation
    - TTL management (Time To Live)
    - Cache invalidation patterns
    - Statistics tracking
    """

    # Default TTL values (in seconds)
    DEFAULT_TTL = 86400  # 24 hours
    STATIC_CONTENT_TTL = 604800  # 7 days
    SHORT_TTL = 3600  # 1 hour

    # Cache key prefixes
    PREFIX_AI_RESPONSE = "ai_response"
    PREFIX_CULTURAL_CONTEXT = "cultural_context"
    PREFIX_POLICY_ANALYSIS = "policy_analysis"
    PREFIX_DOCUMENT_GEN = "document_gen"

    def __init__(self):
        """Initialize cache service."""
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'invalidations': 0,
        }

    def get_or_generate(
        self,
        key_params: Dict[str, Any],
        generator_func: callable,
        ttl: Optional[int] = None,
        prefix: str = PREFIX_AI_RESPONSE
    ) -> Any:
        """
        Get cached value or generate if not found.

        Args:
            key_params: Parameters to generate cache key
            generator_func: Function to call if cache miss
            ttl: Time to live in seconds (None = default)
            prefix: Cache key prefix

        Returns:
            Cached or generated value
        """
        cache_key = self.generate_key(key_params, prefix)

        # Try to get from cache
        cached_value = self.get(cache_key)
        if cached_value is not None:
            self.stats['hits'] += 1
            logger.debug(f"Cache HIT: {cache_key}")
            return cached_value

        # Cache miss - generate value
        self.stats['misses'] += 1
        logger.debug(f"Cache MISS: {cache_key}")

        value = generator_func()

        # Store in cache
        self.set(cache_key, value, ttl)

        return value

    def get(self, cache_key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            cache_key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            value = cache.get(cache_key)
            return value
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set(
        self,
        cache_key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.

        Args:
            cache_key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None = default)

        Returns:
            bool: Success status
        """
        try:
            ttl = ttl or self.DEFAULT_TTL
            cache.set(cache_key, value, ttl)
            self.stats['sets'] += 1
            logger.debug(f"Cache SET: {cache_key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def invalidate(self, cache_key: str) -> bool:
        """
        Invalidate (delete) cache entry.

        Args:
            cache_key: Cache key to invalidate

        Returns:
            bool: Success status
        """
        try:
            cache.delete(cache_key)
            self.stats['invalidations'] += 1
            logger.info(f"Cache INVALIDATED: {cache_key}")
            return True
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            return False

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all cache entries matching pattern.

        Args:
            pattern: Pattern to match (e.g., "ai_response:policy_123:*")

        Returns:
            int: Number of keys invalidated
        """
        try:
            # Note: This requires Redis backend with keys pattern support
            keys = cache.keys(pattern)
            count = 0
            for key in keys:
                cache.delete(key)
                count += 1

            self.stats['invalidations'] += count
            logger.info(f"Cache PATTERN INVALIDATED: {pattern} ({count} keys)")
            return count
        except AttributeError:
            logger.warning(
                "Pattern invalidation not supported by cache backend"
            )
            return 0
        except Exception as e:
            logger.error(f"Pattern invalidation error: {e}")
            return 0

    def generate_key(
        self,
        params: Dict[str, Any],
        prefix: str = PREFIX_AI_RESPONSE
    ) -> str:
        """
        Generate cache key from parameters.

        Args:
            params: Parameters dictionary
            prefix: Key prefix

        Returns:
            str: Generated cache key
        """
        # Sort params for consistent keys
        sorted_params = sorted(params.items())

        # Create hash from params
        param_string = json.dumps(sorted_params, sort_keys=True)
        param_hash = hashlib.md5(param_string.encode()).hexdigest()

        return f"{prefix}:{param_hash}"

    def get_ttl_for_content_type(self, content_type: str) -> int:
        """
        Get appropriate TTL for content type.

        Args:
            content_type: Type of content (static, dynamic, analysis, etc.)

        Returns:
            int: TTL in seconds
        """
        ttl_map = {
            'static': self.STATIC_CONTENT_TTL,  # 7 days
            'cultural_context': self.STATIC_CONTENT_TTL,
            'analysis': self.DEFAULT_TTL,  # 24 hours
            'chat': self.SHORT_TTL,  # 1 hour
            'document': self.DEFAULT_TTL,
        }

        return ttl_map.get(content_type, self.DEFAULT_TTL)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with cache statistics
        """
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (
            (self.stats['hits'] / total_requests * 100)
            if total_requests > 0
            else 0
        )

        return {
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'hit_rate': round(hit_rate, 2),
            'sets': self.stats['sets'],
            'invalidations': self.stats['invalidations'],
            'total_requests': total_requests,
        }

    def reset_stats(self):
        """Reset cache statistics."""
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'invalidations': 0,
        }
        logger.info("Cache statistics reset")

    def warm_cache(self, data_items: list, prefix: str, ttl: Optional[int] = None):
        """
        Warm cache with precomputed data.

        Args:
            data_items: List of (key_params, value) tuples
            prefix: Cache key prefix
            ttl: Time to live (None = default)
        """
        count = 0
        for key_params, value in data_items:
            cache_key = self.generate_key(key_params, prefix)
            if self.set(cache_key, value, ttl):
                count += 1

        logger.info(f"Cache warmed: {count} items with prefix '{prefix}'")
        return count

    def clear_all(self) -> bool:
        """
        Clear all cache entries.

        WARNING: Use with caution!

        Returns:
            bool: Success status
        """
        try:
            cache.clear()
            logger.warning("ALL cache entries cleared")
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False


class PolicyCacheManager:
    """Specialized cache manager for policy-related AI operations."""

    def __init__(self):
        self.cache_service = CacheService()

    def cache_policy_analysis(
        self,
        policy_id: str,
        analysis_type: str,
        analysis_data: Dict[str, Any]
    ) -> str:
        """
        Cache policy analysis results.

        Returns:
            str: Cache key
        """
        key_params = {
            'policy_id': policy_id,
            'analysis_type': analysis_type,
        }

        cache_key = self.cache_service.generate_key(
            key_params,
            CacheService.PREFIX_POLICY_ANALYSIS
        )

        self.cache_service.set(
            cache_key,
            analysis_data,
            self.cache_service.DEFAULT_TTL
        )

        return cache_key

    def get_policy_analysis(
        self,
        policy_id: str,
        analysis_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached policy analysis."""
        key_params = {
            'policy_id': policy_id,
            'analysis_type': analysis_type,
        }

        cache_key = self.cache_service.generate_key(
            key_params,
            CacheService.PREFIX_POLICY_ANALYSIS
        )

        return self.cache_service.get(cache_key)

    def invalidate_policy_cache(self, policy_id: str) -> int:
        """Invalidate all cache entries for a policy."""
        pattern = f"{CacheService.PREFIX_POLICY_ANALYSIS}:*{policy_id}*"
        return self.cache_service.invalidate_pattern(pattern)
