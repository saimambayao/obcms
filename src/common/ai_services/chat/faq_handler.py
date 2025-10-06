"""
FAQ Handler Service for OBCMS Chat System

This module provides instant responses to common questions using pre-computed
answers and fuzzy matching. No AI fallback required.

Version: 2.0 - Enhanced FAQ System
- Priority-based matching (5-20 range, higher = more important)
- Enhanced metadata (source verification, analytics, maintenance)
- 100+ FAQs across 5 categories
- Simple question handling

Performance Target: <10ms response time
Hit Rate Target: 80%
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher
from django.core.cache import cache
from django.db.models import Count, Sum, Q
from django.utils import timezone
import logging
import time

from .faq_data import (
    get_all_faqs,
    get_faq_by_id,
    PATTERN_TO_FAQ_MAP,
    EnhancedFAQ,
)

logger = logging.getLogger(__name__)


class FAQHandler:
    """
    Handles FAQ queries with pre-computed answers and fuzzy matching.

    Features:
    - Instant responses for common questions
    - Fuzzy matching for typo tolerance
    - Statistics caching (24h TTL)
    - Hit tracking and analytics
    """

    # Cache keys
    CACHE_KEY_PREFIX = "faq_"
    STATS_CACHE_KEY = "faq_stats_cache"
    FAQ_HITS_KEY = "faq_hits"

    # Fuzzy matching threshold (0.0 to 1.0)
    FUZZY_THRESHOLD = 0.75

    def __init__(self):
        """Initialize FAQ handler with base responses."""
        self.base_faqs = self._get_base_faqs()
        self.enhanced_faqs = get_all_faqs()  # Load enhanced FAQs from faq_data
        self.pattern_map = PATTERN_TO_FAQ_MAP  # Pre-built pattern map

    def _get_base_faqs(self) -> Dict[str, Dict]:
        """
        Get base FAQ responses (static).

        Returns:
            Dict mapping FAQ patterns to response data
        """
        return {
            'how many regions': {
                'answer': 'OBCMS covers 4 regions: Region IX (Zamboanga Peninsula), '
                         'Region X (Northern Mindanao), Region XI (Davao Region), '
                         'and Region XII (SOCCSKSARGEN).',
                'related_queries': [
                    'Show all regions',
                    'Which provinces in Region IX?',
                    'List all provinces'
                ],
                'category': 'geography',
                'priority': 10
            },
            'what regions': {
                'answer': 'OBCMS covers 4 regions: Region IX (Zamboanga Peninsula), '
                         'Region X (Northern Mindanao), Region XI (Davao Region), '
                         'and Region XII (SOCCSKSARGEN).',
                'related_queries': [
                    'Show all regions',
                    'Which provinces in Region IX?',
                    'List all provinces'
                ],
                'category': 'geography',
                'priority': 10
            },
            'which regions': {
                'answer': 'OBCMS covers 4 regions: Region IX (Zamboanga Peninsula), '
                         'Region X (Northern Mindanao), Region XI (Davao Region), '
                         'and Region XII (SOCCSKSARGEN).',
                'related_queries': [
                    'Show all regions',
                    'Which provinces in Region IX?',
                    'List all provinces'
                ],
                'category': 'geography',
                'priority': 10
            },
            'where is cotabato': {
                'answer': 'Cotabato (also known as North Cotabato) is a province in Region XII (SOCCSKSARGEN).',
                'related_queries': [
                    'Show provinces in Region XII',
                    'What is SOCCSKSARGEN?',
                    'List all provinces'
                ],
                'category': 'geography',
                'priority': 12
            },
            'where is zamboanga': {
                'answer': 'There are three Zamboanga provinces, all in Region IX (Zamboanga Peninsula): '
                         'Zamboanga del Norte, Zamboanga del Sur, and Zamboanga Sibugay.',
                'related_queries': [
                    'Show provinces in Region IX',
                    'What is Zamboanga Peninsula?',
                    'List all provinces'
                ],
                'category': 'geography',
                'priority': 12
            },
            'where is bukidnon': {
                'answer': 'Bukidnon is a province in Region X (Northern Mindanao).',
                'related_queries': [
                    'Show provinces in Region X',
                    'What is Northern Mindanao?',
                    'List all provinces'
                ],
                'category': 'geography',
                'priority': 12
            },
            'where is davao': {
                'answer': 'There are five Davao provinces, all in Region XI (Davao Region): '
                         'Davao del Norte, Davao del Sur, Davao Oriental, Davao de Oro, and Davao Occidental.',
                'related_queries': [
                    'Show provinces in Region XI',
                    'What is Davao Region?',
                    'List all provinces'
                ],
                'category': 'geography',
                'priority': 12
            },
            'what can you do': {
                'answer': 'I can help you with:\n'
                         '• Count communities, workshops, assessments, and policies\n'
                         '• List items filtered by location, date, or status\n'
                         '• Show statistics and aggregated data\n'
                         '• Find specific records by name or criteria',
                'examples': [
                    'How many communities in Region IX?',
                    'Show recent workshops',
                    'List active partnerships',
                    'Top livelihoods in Zamboanga'
                ],
                'category': 'help',
                'priority': 10
            },
            'what do you do': {
                'answer': 'I can help you with:\n'
                         '• Count communities, workshops, assessments, and policies\n'
                         '• List items filtered by location, date, or status\n'
                         '• Show statistics and aggregated data\n'
                         '• Find specific records by name or criteria',
                'examples': [
                    'How many communities in Region IX?',
                    'Show recent workshops',
                    'List active partnerships',
                    'Top livelihoods in Zamboanga'
                ],
                'category': 'help',
                'priority': 10
            },
            'help': {
                'answer': 'I can help you with:\n'
                         '• Count communities, workshops, assessments, and policies\n'
                         '• List items filtered by location, date, or status\n'
                         '• Show statistics and aggregated data\n'
                         '• Find specific records by name or criteria',
                'examples': [
                    'How many communities in Region IX?',
                    'Show recent workshops',
                    'List active partnerships',
                    'Top livelihoods in Zamboanga'
                ],
                'category': 'help',
                'priority': 10
            },
            'what modules': {
                'answer': 'OBCMS has these main modules:\n'
                         '• Communities - OBC profiles and demographics\n'
                         '• MANA - Mapping and Needs Assessment workshops\n'
                         '• Coordination - Partnerships and stakeholder management\n'
                         '• Policies - Policy recommendations and tracking\n'
                         '• M&E - Projects, Programs, and Activities (PPAs)\n'
                         '• Staff - Task management and calendar',
                'related_queries': [
                    'Show communities',
                    'List workshops',
                    'View partnerships'
                ],
                'category': 'system',
                'priority': 10
            },
            'system modules': {
                'answer': 'OBCMS has these main modules:\n'
                         '• Communities - OBC profiles and demographics\n'
                         '• MANA - Mapping and Needs Assessment workshops\n'
                         '• Coordination - Partnerships and stakeholder management\n'
                         '• Policies - Policy recommendations and tracking\n'
                         '• M&E - Projects, Programs, and Activities (PPAs)\n'
                         '• Staff - Task management and calendar',
                'related_queries': [
                    'Show communities',
                    'List workshops',
                    'View partnerships'
                ],
                'category': 'system',
                'priority': 10
            },
            'top ethnolinguistic groups': {
                'answer': None,  # Will be populated from cache
                'cache_key': 'top_ethnic_groups',
                'category': 'statistics',
                'priority': 9
            },
            'top livelihoods': {
                'answer': None,  # Will be populated from cache
                'cache_key': 'top_livelihoods',
                'category': 'statistics',
                'priority': 9
            },
            'total communities': {
                'answer': None,  # Will be populated from cache
                'cache_key': 'total_communities',
                'category': 'statistics',
                'priority': 10
            },
            'how many communities': {
                'answer': None,  # Will be populated from cache
                'cache_key': 'total_communities',
                'category': 'statistics',
                'priority': 10
            },
            'how many municipalities': {
                'answer': None,  # Will be populated from cache
                'cache_key': 'municipalities_only',
                'category': 'statistics',
                'priority': 11  # Higher priority than communities to avoid fuzzy matching
            },
            'how many cities': {
                'answer': None,  # Will be populated from cache
                'cache_key': 'cities_only',
                'category': 'statistics',
                'priority': 11
            },
            'total workshops': {
                'answer': None,  # Will be populated from cache
                'cache_key': 'total_workshops',
                'category': 'statistics',
                'priority': 9
            },
            'how many workshops': {
                'answer': None,  # Will be populated from cache
                'cache_key': 'total_workshops',
                'category': 'statistics',
                'priority': 9
            },
            'total policies': {
                'answer': None,  # Will be populated from cache
                'cache_key': 'total_policies',
                'category': 'statistics',
                'priority': 9
            },
            'total partnerships': {
                'answer': None,  # Will be populated from cache
                'cache_key': 'total_partnerships',
                'category': 'statistics',
                'priority': 9
            },
            'active partnerships': {
                'answer': None,  # Will be populated from cache
                'cache_key': 'active_partnerships',
                'category': 'statistics',
                'priority': 9
            }
        }

    def try_faq(self, query: str) -> Optional[Dict]:
        """
        Try to match query against FAQ database.

        Enhanced matching with priority:
        1. Enhanced FAQs (priority 18-20 first, then descending)
        2. Legacy FAQs (backward compatibility)

        Args:
            query: User's natural language query

        Returns:
            Response dict if matched, None otherwise
            {
                'answer': str,
                'confidence': float,
                'source': 'faq',
                'response_time': float (ms),
                'related_queries': List[str],
                'examples': List[str],
                'faq_id': str (enhanced FAQs only),
                'priority': int (enhanced FAQs only)
            }
        """
        start_time = time.time()

        # Normalize query
        normalized_query = self._normalize_query(query)

        # Return None for empty queries
        if not normalized_query or normalized_query.strip() == '':
            return None

        # STEP 1: Try enhanced FAQs first (priority-based)
        enhanced_match = self._try_enhanced_faq(normalized_query)
        if enhanced_match:
            response = self._build_enhanced_response(
                enhanced_match['faq'],
                enhanced_match['confidence'],
                start_time,
                matched_pattern=enhanced_match['pattern']
            )
            self._track_enhanced_hit(enhanced_match['faq'].id)
            return response

        # STEP 2: Fall back to legacy FAQs (backward compatibility)
        # Try exact match first
        exact_match = self._exact_match(normalized_query)
        if exact_match:
            response = self._build_response(
                exact_match,
                1.0,
                start_time,
                matched_pattern=exact_match['pattern']
            )
            self._track_hit(exact_match['pattern'])
            return response

        # Try fuzzy match
        fuzzy_match = self._fuzzy_match(normalized_query)
        if fuzzy_match:
            response = self._build_response(
                fuzzy_match['faq'],
                fuzzy_match['confidence'],
                start_time,
                matched_pattern=fuzzy_match['pattern']
            )
            self._track_hit(fuzzy_match['pattern'])
            return response

        # No match
        logger.debug(f"FAQ: No match for query: {query}")
        return None

    def _normalize_query(self, query: str) -> str:
        """
        Normalize query for matching.

        Args:
            query: Raw user query

        Returns:
            Normalized query string
        """
        # Convert to lowercase
        normalized = query.lower().strip()

        # Remove punctuation
        for char in '?!.,;:':
            normalized = normalized.replace(char, '')

        # Remove extra whitespace
        normalized = ' '.join(normalized.split())

        return normalized

    def _exact_match(self, normalized_query: str) -> Optional[Dict]:
        """
        Try exact pattern match.

        Args:
            normalized_query: Normalized query string

        Returns:
            FAQ data if matched, None otherwise
        """
        for pattern, faq_data in self.base_faqs.items():
            if normalized_query == pattern or normalized_query in pattern or pattern in normalized_query:
                # Get answer (from cache if needed)
                answer = self._get_faq_answer(faq_data)
                if answer:
                    return {
                        'pattern': pattern,
                        'answer': answer,
                        'related_queries': faq_data.get('related_queries', []),
                        'examples': faq_data.get('examples', []),
                        'category': faq_data.get('category', 'general')
                    }
        return None

    def _fuzzy_match(self, normalized_query: str) -> Optional[Dict]:
        """
        Try fuzzy pattern match using Levenshtein-style similarity.

        Args:
            normalized_query: Normalized query string

        Returns:
            Dict with matched FAQ and confidence, or None
        """
        best_match = None
        best_confidence = 0.0

        for pattern, faq_data in self.base_faqs.items():
            confidence = self._similarity_score(normalized_query, pattern)

            if confidence >= self.FUZZY_THRESHOLD and confidence > best_confidence:
                answer = self._get_faq_answer(faq_data)
                if answer:
                    best_match = {
                        'pattern': pattern,
                        'faq': {
                            'pattern': pattern,
                            'answer': answer,
                            'related_queries': faq_data.get('related_queries', []),
                            'examples': faq_data.get('examples', []),
                            'category': faq_data.get('category', 'general')
                        },
                        'confidence': confidence
                    }
                    best_confidence = confidence

        return best_match

    def _similarity_score(self, query: str, pattern: str) -> float:
        """
        Calculate similarity score between query and pattern.

        Uses SequenceMatcher for fuzzy string matching.

        Args:
            query: User query
            pattern: FAQ pattern

        Returns:
            Similarity score (0.0 to 1.0)
        """
        return SequenceMatcher(None, query, pattern).ratio()

    def _get_faq_answer(self, faq_data: Dict) -> Optional[str]:
        """
        Get FAQ answer (from cache if dynamic, or static).

        Args:
            faq_data: FAQ data dictionary

        Returns:
            Answer string or None
        """
        # If static answer exists, return it
        if faq_data.get('answer'):
            return faq_data['answer']

        # If cache_key exists, get from cache
        cache_key = faq_data.get('cache_key')
        if cache_key:
            stats = self._get_cached_stats()
            return stats.get(cache_key)

        return None

    def _build_response(
        self,
        faq_data: Dict,
        confidence: float,
        start_time: float,
        matched_pattern: str
    ) -> Dict:
        """
        Build FAQ response dictionary.

        Args:
            faq_data: FAQ data
            confidence: Match confidence score
            start_time: Request start time
            matched_pattern: The pattern that was matched

        Returns:
            Response dictionary
        """
        response_time_ms = (time.time() - start_time) * 1000

        return {
            'answer': faq_data['answer'],
            'confidence': confidence,
            'source': 'faq',
            'response_time': round(response_time_ms, 2),
            'related_queries': faq_data.get('related_queries', []),
            'examples': faq_data.get('examples', []),
            'category': faq_data.get('category', 'general'),
            'matched_pattern': matched_pattern
        }

    def _track_hit(self, pattern: str):
        """
        Track FAQ hit for analytics.

        Args:
            pattern: The FAQ pattern that was matched
        """
        try:
            # Get current hits
            hits = cache.get(self.FAQ_HITS_KEY, {})

            # Increment hit count
            hits[pattern] = hits.get(pattern, 0) + 1

            # Store back (24h TTL)
            cache.set(self.FAQ_HITS_KEY, hits, 86400)

            logger.info(f"FAQ hit tracked: {pattern} (total: {hits[pattern]})")
        except Exception as e:
            logger.error(f"Error tracking FAQ hit: {e}")

    def add_faq(self, pattern: str, response: Dict):
        """
        Add a new FAQ entry.

        Args:
            pattern: Query pattern to match
            response: FAQ response data
        """
        self.base_faqs[pattern.lower()] = response
        logger.info(f"Added FAQ: {pattern}")

    def update_stats_cache(self) -> Dict[str, str]:
        """
        Update pre-computed statistics cache.

        Queries database for current stats and caches them.

        Returns:
            Dict of computed statistics
        """
        try:
            stats = {}

            # Try to import and query communities
            try:
                from communities.models import OBCCommunity

                total_communities = OBCCommunity.objects.count()
                stats['total_communities'] = (
                    f"There are {total_communities} OBC communities registered in the system."
                )

                # Communities by region
                communities_by_region = OBCCommunity.objects.values(
                    'barangay__municipality__province__region__name'
                ).annotate(count=Count('id')).order_by('-count')

                region_breakdown = '\n'.join([
                    f"• {item['barangay__municipality__province__region__name']}: {item['count']} communities"
                    for item in communities_by_region
                ])

                if region_breakdown:
                    stats['total_communities'] += f"\n\nBreakdown by region:\n{region_breakdown}"

                # Top ethnolinguistic groups
                top_ethnic = OBCCommunity.objects.exclude(
                    primary_ethnolinguistic_group__isnull=True
                ).exclude(
                    primary_ethnolinguistic_group=''
                ).values(
                    'primary_ethnolinguistic_group'
                ).annotate(
                    count=Count('id')
                ).order_by('-count')[:5]

                if top_ethnic:
                    ethnic_list = '\n'.join([
                        f"{i+1}. {item['primary_ethnolinguistic_group']}: {item['count']} communities"
                        for i, item in enumerate(top_ethnic)
                    ])
                    stats['top_ethnic_groups'] = (
                        f"Top 5 ethnolinguistic groups:\n{ethnic_list}"
                    )

                # Top livelihoods
                top_livelihoods = OBCCommunity.objects.exclude(
                    primary_livelihoods__isnull=True
                ).exclude(
                    primary_livelihoods=''
                ).values(
                    'primary_livelihoods'
                ).annotate(
                    count=Count('id')
                ).order_by('-count')[:5]

                if top_livelihoods:
                    livelihood_list = '\n'.join([
                        f"{i+1}. {item['primary_livelihoods']}: {item['count']} communities"
                        for i, item in enumerate(top_livelihoods)
                    ])
                    stats['top_livelihoods'] = (
                        f"Top 5 livelihoods:\n{livelihood_list}"
                    )
            except ImportError:
                logger.warning("Communities app not available for FAQ stats")

            # Try to import and query municipalities and cities separately
            try:
                from communities.models import Municipality

                # Count municipalities only (excluding cities)
                municipalities_count = Municipality.objects.filter(municipality_type="municipality").count()
                stats['municipalities_only'] = (
                    f"There are {municipalities_count} municipalities in the OBCMS database (excluding cities)."
                )

                # Count cities only (excluding municipalities)
                cities_count = Municipality.objects.exclude(municipality_type="municipality").count()
                stats['cities_only'] = (
                    f"There are {cities_count} cities in the OBCMS database (excluding municipalities)."
                )

                # Combined count for reference
                total_muni_cities = Municipality.objects.count()
                stats['total_municipalities_and_cities'] = (
                    f"There are {total_muni_cities} municipalities and cities combined "
                    f"({municipalities_count} municipalities + {cities_count} cities)."
                )
            except ImportError:
                logger.warning("Municipality model not available for FAQ stats")

            # Try to import and query workshops
            try:
                from mana.models import Assessment

                current_year = timezone.now().year
                total_workshops = Assessment.objects.filter(
                    Q(planned_start_date__year=current_year) |
                    Q(actual_start_date__year=current_year)
                ).count()
                stats['total_workshops'] = (
                    f"There are {total_workshops} assessments conducted in {current_year}."
                )
            except (ImportError, Exception) as e:
                logger.warning(f"MANA app not available for FAQ stats: {e}")

            # Try to import and query partnerships
            try:
                from coordination.models import Partnership

                total_partnerships = Partnership.objects.count()
                active_partnerships = Partnership.objects.filter(
                    status='active'
                ).count()

                stats['total_partnerships'] = (
                    f"There are {total_partnerships} partnerships registered "
                    f"({active_partnerships} active)."
                )
                stats['active_partnerships'] = (
                    f"There are {active_partnerships} active partnerships."
                )
            except ImportError:
                logger.warning("Coordination app not available for FAQ stats")

            # Cache for 24 hours
            cache.set(self.STATS_CACHE_KEY, stats, 86400)

            logger.info(f"FAQ stats cache updated: {len(stats)} entries")
            return stats

        except Exception as e:
            logger.error(f"Error updating FAQ stats cache: {e}")
            return {}

    def _get_cached_stats(self) -> Dict[str, str]:
        """
        Get cached statistics.

        Returns:
            Dict of cached stats
        """
        stats = cache.get(self.STATS_CACHE_KEY, {})

        # If cache is empty, update it
        if not stats:
            stats = self.update_stats_cache()

        return stats

    def get_popular_faqs(self, limit: int = 10) -> List[Dict]:
        """
        Get most popular FAQs by hit count.

        Args:
            limit: Maximum number of FAQs to return

        Returns:
            List of FAQ dicts sorted by popularity
        """
        hits = cache.get(self.FAQ_HITS_KEY, {})

        # Sort by hit count
        sorted_patterns = sorted(
            hits.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

        popular_faqs = []
        for pattern, hit_count in sorted_patterns:
            faq_data = self.base_faqs.get(pattern)
            if faq_data:
                popular_faqs.append({
                    'pattern': pattern,
                    'answer': self._get_faq_answer(faq_data),
                    'hit_count': hit_count,
                    'category': faq_data.get('category', 'general')
                })

        return popular_faqs

    def _try_enhanced_faq(self, normalized_query: str) -> Optional[Dict]:
        """
        Try matching against enhanced FAQs (priority-based).

        Args:
            normalized_query: Normalized query string

        Returns:
            Dict with matched FAQ and confidence, or None
        """
        best_match = None
        best_confidence = 0.0
        best_priority = -1

        # Sort enhanced FAQs by priority (highest first)
        sorted_faqs = sorted(self.enhanced_faqs, key=lambda f: f.priority, reverse=True)

        for faq in sorted_faqs:
            # Try exact match against all patterns
            for pattern in faq.get_all_patterns():
                if normalized_query == pattern or pattern in normalized_query or normalized_query in pattern:
                    # Exact match - return immediately
                    return {
                        'faq': faq,
                        'confidence': 1.0,
                        'pattern': pattern,
                    }

            # Try fuzzy match
            for pattern in faq.get_all_patterns():
                confidence = self._similarity_score(normalized_query, pattern)

                # Consider both confidence and priority
                # Higher priority FAQs can match with slightly lower confidence
                adjusted_threshold = self.FUZZY_THRESHOLD
                if faq.priority >= 18:
                    adjusted_threshold -= 0.05  # More lenient for critical FAQs

                if confidence >= adjusted_threshold:
                    # Prefer higher priority, then higher confidence
                    if (faq.priority > best_priority or
                        (faq.priority == best_priority and confidence > best_confidence)):
                        best_match = {
                            'faq': faq,
                            'confidence': confidence,
                            'pattern': pattern,
                        }
                        best_confidence = confidence
                        best_priority = faq.priority

        return best_match

    def _build_enhanced_response(
        self,
        faq: EnhancedFAQ,
        confidence: float,
        start_time: float,
        matched_pattern: str
    ) -> Dict:
        """
        Build response from enhanced FAQ.

        Args:
            faq: EnhancedFAQ object
            confidence: Match confidence score
            start_time: Request start time
            matched_pattern: The pattern that was matched

        Returns:
            Response dictionary with enhanced metadata
        """
        response_time_ms = (time.time() - start_time) * 1000

        return {
            'answer': faq.response,
            'confidence': confidence,
            'source': 'faq_enhanced',
            'response_time': round(response_time_ms, 2),
            'related_queries': faq.related_queries,
            'examples': faq.examples,
            'category': faq.category,
            'priority': faq.priority,
            'faq_id': faq.id,
            'matched_pattern': matched_pattern,
            'source_doc': faq.source,
            'source_url': faq.source_url,
        }

    def _track_enhanced_hit(self, faq_id: str):
        """
        Track enhanced FAQ hit for analytics.

        Args:
            faq_id: The enhanced FAQ ID that was matched
        """
        try:
            # Get current hits for enhanced FAQs
            enhanced_hits_key = f"{self.FAQ_HITS_KEY}_enhanced"
            hits = cache.get(enhanced_hits_key, {})

            # Increment hit count
            hits[faq_id] = hits.get(faq_id, 0) + 1

            # Store back (24h TTL)
            cache.set(enhanced_hits_key, hits, 86400)

            logger.info(f"Enhanced FAQ hit tracked: {faq_id} (total: {hits[faq_id]})")
        except Exception as e:
            logger.error(f"Error tracking enhanced FAQ hit: {e}")

    def get_faq_stats(self) -> Dict:
        """
        Get FAQ handler statistics (legacy + enhanced).

        Returns:
            Dict with FAQ stats including enhanced FAQs
        """
        # Legacy FAQ stats
        legacy_hits = cache.get(self.FAQ_HITS_KEY, {})
        legacy_total_hits = sum(legacy_hits.values())
        legacy_total_faqs = len(self.base_faqs)
        legacy_faqs_with_hits = len([p for p in legacy_hits if legacy_hits[p] > 0])

        # Enhanced FAQ stats
        enhanced_hits_key = f"{self.FAQ_HITS_KEY}_enhanced"
        enhanced_hits = cache.get(enhanced_hits_key, {})
        enhanced_total_hits = sum(enhanced_hits.values())
        enhanced_total_faqs = len(self.enhanced_faqs)
        enhanced_faqs_with_hits = len([p for p in enhanced_hits if enhanced_hits[p] > 0])

        # Combined stats
        total_faqs = legacy_total_faqs + enhanced_total_faqs
        total_hits = legacy_total_hits + enhanced_total_hits
        total_faqs_with_hits = legacy_faqs_with_hits + enhanced_faqs_with_hits

        return {
            # Overall stats
            'total_faqs': total_faqs,
            'total_hits': total_hits,
            'faqs_with_hits': total_faqs_with_hits,
            'hit_rate': round(total_faqs_with_hits / total_faqs * 100, 2) if total_faqs > 0 else 0,

            # Legacy FAQs
            'legacy_faqs': {
                'total': legacy_total_faqs,
                'hits': legacy_total_hits,
                'with_hits': legacy_faqs_with_hits,
                'popular': self.get_popular_faqs(5),
            },

            # Enhanced FAQs
            'enhanced_faqs': {
                'total': enhanced_total_faqs,
                'hits': enhanced_total_hits,
                'with_hits': enhanced_faqs_with_hits,
                'popular': self.get_popular_enhanced_faqs(5),
                'by_category': self._get_enhanced_stats_by_category(),
                'by_priority': self._get_enhanced_stats_by_priority(),
            },
        }

    def get_popular_enhanced_faqs(self, limit: int = 10) -> List[Dict]:
        """
        Get most popular enhanced FAQs by hit count.

        Args:
            limit: Maximum number of FAQs to return

        Returns:
            List of enhanced FAQ dicts sorted by popularity
        """
        enhanced_hits_key = f"{self.FAQ_HITS_KEY}_enhanced"
        hits = cache.get(enhanced_hits_key, {})

        # Sort by hit count
        sorted_faq_ids = sorted(
            hits.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

        popular_faqs = []
        for faq_id, hit_count in sorted_faq_ids:
            faq = get_faq_by_id(faq_id)
            if faq:
                popular_faqs.append({
                    'id': faq.id,
                    'question': faq.primary_question,
                    'category': faq.category,
                    'priority': faq.priority,
                    'hit_count': hit_count,
                })

        return popular_faqs

    def _get_enhanced_stats_by_category(self) -> Dict[str, Dict]:
        """Get enhanced FAQ statistics grouped by category."""
        enhanced_hits_key = f"{self.FAQ_HITS_KEY}_enhanced"
        hits = cache.get(enhanced_hits_key, {})

        categories = {}
        for faq in self.enhanced_faqs:
            if faq.category not in categories:
                categories[faq.category] = {
                    'total': 0,
                    'hits': 0,
                    'with_hits': 0,
                }

            categories[faq.category]['total'] += 1
            hit_count = hits.get(faq.id, 0)
            categories[faq.category]['hits'] += hit_count
            if hit_count > 0:
                categories[faq.category]['with_hits'] += 1

        return categories

    def _get_enhanced_stats_by_priority(self) -> Dict[str, Dict]:
        """Get enhanced FAQ statistics grouped by priority range."""
        enhanced_hits_key = f"{self.FAQ_HITS_KEY}_enhanced"
        hits = cache.get(enhanced_hits_key, {})

        priority_ranges = {
            'critical_18_20': {'min': 18, 'max': 20, 'total': 0, 'hits': 0},
            'high_15_17': {'min': 15, 'max': 17, 'total': 0, 'hits': 0},
            'medium_12_14': {'min': 12, 'max': 14, 'total': 0, 'hits': 0},
            'standard_10_11': {'min': 10, 'max': 11, 'total': 0, 'hits': 0},
            'low_5_9': {'min': 5, 'max': 9, 'total': 0, 'hits': 0},
        }

        for faq in self.enhanced_faqs:
            for range_key, range_data in priority_ranges.items():
                if range_data['min'] <= faq.priority <= range_data['max']:
                    range_data['total'] += 1
                    range_data['hits'] += hits.get(faq.id, 0)
                    break

        return priority_ranges


# Singleton instance
_faq_handler = None


def get_faq_handler() -> FAQHandler:
    """Get singleton FAQ handler instance."""
    global _faq_handler
    if _faq_handler is None:
        _faq_handler = FAQHandler()
    return _faq_handler
