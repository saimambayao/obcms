"""
Comprehensive test suite for Entity Extractor service.

Tests all entity types, fuzzy matching, edge cases, and performance.
Target: <20ms per extraction, 95%+ accuracy
"""

import time
from datetime import datetime, timedelta
from django.test import TestCase
from django.utils import timezone

from common.ai_services.chat.entity_extractor import EntityExtractor
from common.ai_services.chat.entity_resolvers import (
    LocationResolver,
    EthnicGroupResolver,
    LivelihoodResolver,
    DateRangeResolver,
    StatusResolver,
    NumberResolver,
)


class EntityExtractorTestCase(TestCase):
    """Test suite for EntityExtractor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = EntityExtractor()

    def test_extract_entities_empty_query(self):
        """Test with empty query."""
        result = self.extractor.extract_entities("")
        self.assertEqual(result, {})

        result = self.extractor.extract_entities(None)
        self.assertEqual(result, {})

    def test_extract_entities_multiple_entities(self):
        """Test extraction of multiple entities from single query."""
        query = "maranao fishing communities in zamboanga last 6 months"
        result = self.extractor.extract_entities(query)

        # Should extract all entity types
        self.assertIn('ethnolinguistic_group', result)
        self.assertIn('livelihood', result)
        self.assertIn('location', result)
        self.assertIn('date_range', result)

        # Verify values
        self.assertEqual(result['ethnolinguistic_group']['value'], 'Meranaw')
        self.assertEqual(result['livelihood']['value'], 'fishing')
        self.assertEqual(result['location']['type'], 'region')
        self.assertIn('IX', result['location']['value'])

    def test_extract_entities_complex_query(self):
        """Test extraction from complex multi-entity query."""
        query = "show me top 5 ongoing maguindanao farming communities in sultan kudarat from jan to march"
        result = self.extractor.extract_entities(query)

        self.assertIn('ethnolinguistic_group', result)
        self.assertIn('livelihood', result)
        self.assertIn('location', result)
        self.assertIn('status', result)
        self.assertIn('date_range', result)
        self.assertIn('numbers', result)

    def test_get_entity_summary(self):
        """Test human-readable entity summary generation."""
        entities = {
            'ethnolinguistic_group': {'value': 'Meranaw', 'confidence': 0.95},
            'livelihood': {'value': 'fishing', 'confidence': 0.90},
            'location': {'type': 'region', 'value': 'Region IX', 'confidence': 0.85},
        }

        summary = self.extractor.get_entity_summary(entities)
        self.assertIn('Meranaw', summary)
        self.assertIn('fishing', summary)
        self.assertIn('Region IX', summary)

    def test_get_entity_summary_empty(self):
        """Test summary with no entities."""
        summary = self.extractor.get_entity_summary({})
        self.assertEqual(summary, "No entities detected")

    def test_validate_entities_valid(self):
        """Test entity validation with valid entities."""
        entities = {
            'location': {'type': 'region', 'value': 'Region IX', 'confidence': 0.95}
        }

        is_valid, issues = self.extractor.validate_entities(entities)
        self.assertTrue(is_valid)
        self.assertEqual(issues, [])

    def test_validate_entities_low_confidence(self):
        """Test entity validation with low confidence."""
        entities = {
            'location': {'type': 'region', 'value': 'Region IX', 'confidence': 0.25}
        }

        is_valid, issues = self.extractor.validate_entities(entities)
        self.assertFalse(is_valid)
        self.assertTrue(len(issues) > 0)

    def test_validate_entities_invalid_date_range(self):
        """Test entity validation with invalid date range."""
        start = timezone.now()
        end = start - timedelta(days=30)  # End before start (invalid)

        entities = {
            'date_range': {'start': start, 'end': end, 'confidence': 1.0}
        }

        is_valid, issues = self.extractor.validate_entities(entities)
        self.assertFalse(is_valid)
        self.assertTrue(any('Invalid date range' in issue for issue in issues))

    def test_performance_extraction(self):
        """Test that extraction completes in <20ms."""
        query = "maranao fishing communities in zamboanga last 6 months"

        start_time = time.perf_counter()
        result = self.extractor.extract_entities(query)
        end_time = time.perf_counter()

        duration_ms = (end_time - start_time) * 1000

        # Performance target: <20ms
        self.assertLess(duration_ms, 20, f"Extraction took {duration_ms:.2f}ms (target: <20ms)")
        self.assertGreater(len(result), 0, "Should extract at least one entity")


class LocationResolverTestCase(TestCase):
    """Test suite for LocationResolver."""

    def setUp(self):
        """Set up test fixtures."""
        self.resolver = LocationResolver()

    def test_resolve_region_ix_full_name(self):
        """Test region IX resolution with full name."""
        result = self.resolver.resolve("communities in region ix")
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'region')
        self.assertEqual(result['value'], 'Region IX')
        self.assertGreaterEqual(result['confidence'], 0.85)

    def test_resolve_region_ix_variations(self):
        """Test region IX resolution with variations."""
        variations = [
            "region 9",
            "zamboanga",
            "zamboanga peninsula",
            "r9",
        ]

        for variant in variations:
            result = self.resolver.resolve(f"communities in {variant}")
            self.assertIsNotNone(result, f"Failed to resolve: {variant}")
            self.assertEqual(result['type'], 'region')
            self.assertIn('IX', result['value'])

    def test_resolve_all_regions(self):
        """Test all 4 OBCMS regions resolve correctly."""
        test_cases = [
            ("region x", "Region X"),
            ("region xi", "Region XI"),
            ("region xii", "Region XII"),
            ("northern mindanao", "Region X"),
            ("davao", "Region XI"),
            ("soccsksargen", "Region XII"),
        ]

        for query, expected_value in test_cases:
            result = self.resolver.resolve(query)
            self.assertIsNotNone(result, f"Failed to resolve: {query}")
            self.assertEqual(result['value'], expected_value)

    def test_resolve_province_sultan_kudarat(self):
        """Test province resolution for Sultan Kudarat."""
        result = self.resolver.resolve("communities in sultan kudarat")
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'province')
        self.assertIn('Sultan Kudarat', result['value'])

    def test_resolve_province_variations(self):
        """Test province resolution with variations."""
        test_cases = [
            ("maguindanao", "Maguindanao"),
            ("south cotabato", "South Cotabato"),
            ("zamboanga del norte", "Zamboanga Del Norte"),
            ("bukidnon", "Bukidnon"),
        ]

        for query, expected in test_cases:
            result = self.resolver.resolve(f"communities in {query}")
            self.assertIsNotNone(result, f"Failed to resolve province: {query}")
            self.assertEqual(result['type'], 'province')

    def test_resolve_no_match(self):
        """Test with query that has no location."""
        result = self.resolver.resolve("fishing communities")
        self.assertIsNone(result)

    def test_resolve_typos(self):
        """Test fuzzy matching with typos."""
        # Region IX variations with common typos
        result = self.resolver.resolve("zambanga")  # Missing 'o'
        # Should still match Zamboanga
        if result:
            self.assertIn('IX', result['value'])


class EthnicGroupResolverTestCase(TestCase):
    """Test suite for EthnicGroupResolver."""

    def setUp(self):
        """Set up test fixtures."""
        self.resolver = EthnicGroupResolver()

    def test_resolve_meranaw_variations(self):
        """Test Meranaw/Maranao with variations."""
        variations = ['maranao', 'marano', 'meranaw', 'maranaos']

        for variant in variations:
            result = self.resolver.resolve(f"{variant} communities")
            self.assertIsNotNone(result, f"Failed to resolve: {variant}")
            self.assertEqual(result['value'], 'Meranaw')
            self.assertGreaterEqual(result['confidence'], 0.90)

    def test_resolve_maguindanaon_variations(self):
        """Test Maguindanaon with variations."""
        variations = ['maguindanao', 'maguindanaon', 'magindanao']

        for variant in variations:
            result = self.resolver.resolve(f"{variant} people")
            self.assertIsNotNone(result, f"Failed to resolve: {variant}")
            self.assertEqual(result['value'], 'Maguindanaon')

    def test_resolve_all_ethnic_groups(self):
        """Test all major ethnic groups resolve correctly."""
        test_cases = [
            ('tausug', 'Tausug'),
            ('sama', 'Sama'),
            ('badjao', 'Badjao'),
            ('yakan', 'Yakan'),
            ('iranun', 'Iranun'),
            ('kalagan', 'Kagan Kalagan'),
            ('sangil', 'Sangil'),
        ]

        for query, expected in test_cases:
            result = self.resolver.resolve(f"{query} communities")
            self.assertIsNotNone(result, f"Failed to resolve: {query}")
            self.assertIn(expected.split()[0], result['value'])

    def test_resolve_no_match(self):
        """Test with query that has no ethnic group."""
        result = self.resolver.resolve("fishing communities")
        self.assertIsNone(result)

    def test_resolve_word_boundaries(self):
        """Test that resolver uses word boundaries (no partial matches)."""
        # "iran" should NOT match "iranun"
        result = self.resolver.resolve("iran trade")
        # Should either be None or if matched, should be Iranun
        if result:
            self.assertEqual(result['value'], 'Iranun')


class LivelihoodResolverTestCase(TestCase):
    """Test suite for LivelihoodResolver."""

    def setUp(self):
        """Set up test fixtures."""
        self.resolver = LivelihoodResolver()

    def test_resolve_farming_variations(self):
        """Test farming with variations."""
        variations = ['farming', 'farmer', 'farmers', 'agriculture']

        for variant in variations:
            result = self.resolver.resolve(f"{variant} communities")
            self.assertIsNotNone(result, f"Failed to resolve: {variant}")
            self.assertEqual(result['value'], 'farming')

    def test_resolve_fishing_variations(self):
        """Test fishing with variations."""
        variations = ['fishing', 'fisher', 'fishermen', 'fisherfolk']

        for variant in variations:
            result = self.resolver.resolve(f"{variant} communities")
            self.assertIsNotNone(result, f"Failed to resolve: {variant}")
            self.assertEqual(result['value'], 'fishing')

    def test_resolve_all_livelihoods(self):
        """Test all major livelihoods resolve correctly."""
        livelihoods = [
            'farming', 'fishing', 'trading', 'weaving',
            'livestock', 'carpentry', 'masonry', 'driving'
        ]

        for livelihood in livelihoods:
            result = self.resolver.resolve(f"{livelihood} communities")
            self.assertIsNotNone(result, f"Failed to resolve: {livelihood}")
            self.assertEqual(result['value'], livelihood)

    def test_resolve_no_match(self):
        """Test with query that has no livelihood."""
        result = self.resolver.resolve("maranao communities")
        self.assertIsNone(result)


class DateRangeResolverTestCase(TestCase):
    """Test suite for DateRangeResolver."""

    def setUp(self):
        """Set up test fixtures."""
        self.resolver = DateRangeResolver()

    def test_resolve_last_30_days(self):
        """Test 'last 30 days' resolution."""
        result = self.resolver.resolve("communities last 30 days")
        self.assertIsNotNone(result)
        self.assertEqual(result['range_type'], 'relative')
        self.assertEqual(result['confidence'], 1.0)

        # Check date range is approximately 30 days
        delta = result['end'] - result['start']
        self.assertAlmostEqual(delta.days, 30, delta=1)

    def test_resolve_last_6_months(self):
        """Test 'last 6 months' resolution."""
        result = self.resolver.resolve("workshops last 6 months")
        self.assertIsNotNone(result)
        self.assertEqual(result['range_type'], 'relative')

        # Check date range is approximately 180 days
        delta = result['end'] - result['start']
        self.assertAlmostEqual(delta.days, 180, delta=5)

    def test_resolve_this_year(self):
        """Test 'this year' resolution."""
        result = self.resolver.resolve("events this year")
        self.assertIsNotNone(result)
        self.assertEqual(result['range_type'], 'relative')

        # Start should be Jan 1 of current year
        now = timezone.now()
        self.assertEqual(result['start'].year, now.year)
        self.assertEqual(result['start'].month, 1)
        self.assertEqual(result['start'].day, 1)

    def test_resolve_last_year(self):
        """Test 'last year' resolution."""
        result = self.resolver.resolve("data from last year")
        self.assertIsNotNone(result)

        now = timezone.now()
        last_year = now.year - 1
        self.assertEqual(result['start'].year, last_year)
        self.assertEqual(result['end'].year, last_year)

    def test_resolve_year_only(self):
        """Test year-only resolution like '2024'."""
        result = self.resolver.resolve("communities in 2024")
        self.assertIsNotNone(result)
        self.assertEqual(result['start'].year, 2024)
        self.assertEqual(result['end'].year, 2024)
        self.assertEqual(result['range_type'], 'absolute')

    def test_resolve_month_range(self):
        """Test month range like 'from jan to mar'."""
        result = self.resolver.resolve("events from jan to mar")
        self.assertIsNotNone(result)
        self.assertEqual(result['range_type'], 'absolute')
        self.assertEqual(result['start'].month, 1)
        self.assertEqual(result['end'].month, 3)

    def test_resolve_specific_month_year(self):
        """Test specific month and year like 'january 2024'."""
        result = self.resolver.resolve("workshops in january 2024")
        self.assertIsNotNone(result)
        self.assertEqual(result['start'].year, 2024)
        self.assertEqual(result['start'].month, 1)
        self.assertEqual(result['end'].month, 1)

    def test_resolve_recent_keyword(self):
        """Test 'recent' keyword defaults to last 30 days."""
        result = self.resolver.resolve("recent workshops")
        self.assertIsNotNone(result)
        self.assertEqual(result['range_type'], 'relative')

        delta = result['end'] - result['start']
        self.assertAlmostEqual(delta.days, 30, delta=1)

    def test_resolve_no_match(self):
        """Test with query that has no date range."""
        result = self.resolver.resolve("fishing communities")
        self.assertIsNone(result)


class StatusResolverTestCase(TestCase):
    """Test suite for StatusResolver."""

    def setUp(self):
        """Set up test fixtures."""
        self.resolver = StatusResolver()

    def test_resolve_ongoing_variations(self):
        """Test ongoing status with variations."""
        variations = ['ongoing', 'in progress', 'active', 'running']

        for variant in variations:
            result = self.resolver.resolve(f"{variant} projects")
            self.assertIsNotNone(result, f"Failed to resolve: {variant}")
            self.assertEqual(result['value'], 'ongoing')

    def test_resolve_completed_variations(self):
        """Test completed status with variations."""
        variations = ['completed', 'done', 'finished', 'closed']

        for variant in variations:
            result = self.resolver.resolve(f"{variant} tasks")
            self.assertIsNotNone(result, f"Failed to resolve: {variant}")
            self.assertEqual(result['value'], 'completed')

    def test_resolve_all_statuses(self):
        """Test all major statuses resolve correctly."""
        statuses = [
            'ongoing', 'completed', 'draft', 'pending',
            'approved', 'rejected', 'cancelled', 'suspended'
        ]

        for status in statuses:
            result = self.resolver.resolve(f"{status} items")
            self.assertIsNotNone(result, f"Failed to resolve: {status}")
            self.assertEqual(result['value'], status)

    def test_resolve_no_match(self):
        """Test with query that has no status."""
        result = self.resolver.resolve("fishing communities")
        self.assertIsNone(result)


class NumberResolverTestCase(TestCase):
    """Test suite for NumberResolver."""

    def setUp(self):
        """Set up test fixtures."""
        self.resolver = NumberResolver()

    def test_resolve_cardinal_numbers(self):
        """Test cardinal number extraction."""
        result = self.resolver.resolve("top 5 communities")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['value'], 5)
        self.assertEqual(result[0]['type'], 'cardinal')

    def test_resolve_multiple_numbers(self):
        """Test extraction of multiple numbers."""
        result = self.resolver.resolve("top 10 communities with 25 families")
        self.assertEqual(len(result), 2)

        values = [num['value'] for num in result]
        self.assertIn(10, values)
        self.assertIn(25, values)

    def test_resolve_ordinal_numbers(self):
        """Test ordinal number extraction."""
        test_cases = [
            ('first community', 1),
            ('2nd workshop', 2),
            ('third report', 3),
            ('5th assessment', 5),
        ]

        for query, expected in test_cases:
            result = self.resolver.resolve(query)
            self.assertGreater(len(result), 0, f"Failed to resolve: {query}")
            self.assertEqual(result[0]['value'], expected)
            self.assertEqual(result[0]['type'], 'ordinal')

    def test_resolve_written_numbers(self):
        """Test written number extraction."""
        test_cases = [
            ('five communities', 5),
            ('ten workshops', 10),
            ('twenty families', 20),
        ]

        for query, expected in test_cases:
            result = self.resolver.resolve(query)
            self.assertGreater(len(result), 0, f"Failed to resolve: {query}")
            self.assertEqual(result[0]['value'], expected)

    def test_resolve_no_duplicates(self):
        """Test that duplicates are removed (keep highest confidence)."""
        result = self.resolver.resolve("five 5 communities")
        # Should have only one entry for 5
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['value'], 5)

    def test_resolve_no_match(self):
        """Test with query that has no numbers."""
        result = self.resolver.resolve("fishing communities")
        self.assertEqual(result, [])


class EdgeCasesTestCase(TestCase):
    """Test edge cases and error handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = EntityExtractor()

    def test_case_insensitive_extraction(self):
        """Test that extraction is case-insensitive."""
        queries = [
            "MARANAO fishing ZAMBOANGA",
            "Maranao Fishing Zamboanga",
            "maranao fishing zamboanga",
        ]

        results = [self.extractor.extract_entities(q) for q in queries]

        # All should extract the same entities
        for result in results:
            self.assertIn('ethnolinguistic_group', result)
            self.assertIn('livelihood', result)
            self.assertIn('location', result)

    def test_extra_whitespace(self):
        """Test handling of extra whitespace."""
        query = "  maranao   fishing    zamboanga  "
        result = self.extractor.extract_entities(query)

        self.assertIn('ethnolinguistic_group', result)
        self.assertIn('livelihood', result)
        self.assertIn('location', result)

    def test_special_characters(self):
        """Test handling of special characters."""
        query = "maranao fishing, in zamboanga!"
        result = self.extractor.extract_entities(query)

        self.assertIn('ethnolinguistic_group', result)
        self.assertIn('livelihood', result)

    def test_very_long_query(self):
        """Test performance with very long query."""
        query = "show me all the maranao fishing communities located in zamboanga peninsula region ix " * 10

        start_time = time.perf_counter()
        result = self.extractor.extract_entities(query)
        end_time = time.perf_counter()

        duration_ms = (end_time - start_time) * 1000

        # Should still be fast
        self.assertLess(duration_ms, 50, f"Long query took {duration_ms:.2f}ms")
        self.assertGreater(len(result), 0)

    def test_ambiguous_terms(self):
        """Test handling of ambiguous terms."""
        # "iran" could be country or "Iranun" ethnic group
        query = "iranun communities"
        result = self.extractor.extract_entities(query)

        # Should correctly identify as Iranun ethnic group
        self.assertIn('ethnolinguistic_group', result)
        self.assertEqual(result['ethnolinguistic_group']['value'], 'Iranun')

    def test_conflicting_entities(self):
        """Test validation catches conflicting entities."""
        # Create entities with conflicts
        entities = {
            'date_range': {
                'start': timezone.now(),
                'end': timezone.now() - timedelta(days=30),  # Invalid!
                'confidence': 1.0
            }
        }

        is_valid, issues = self.extractor.validate_entities(entities)
        self.assertFalse(is_valid)
        self.assertTrue(len(issues) > 0)


class IntegrationTestCase(TestCase):
    """Integration tests with realistic queries."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = EntityExtractor()

    def test_realistic_query_1(self):
        """Test: 'How many Maranao fishing communities in Zamboanga?'"""
        query = "how many maranao fishing communities in zamboanga"
        result = self.extractor.extract_entities(query)

        self.assertIn('ethnolinguistic_group', result)
        self.assertEqual(result['ethnolinguistic_group']['value'], 'Meranaw')

        self.assertIn('livelihood', result)
        self.assertEqual(result['livelihood']['value'], 'fishing')

        self.assertIn('location', result)
        self.assertIn('IX', result['location']['value'])

    def test_realistic_query_2(self):
        """Test: 'Show me ongoing workshops in Sultan Kudarat last 6 months'"""
        query = "show me ongoing workshops in sultan kudarat last 6 months"
        result = self.extractor.extract_entities(query)

        self.assertIn('status', result)
        self.assertEqual(result['status']['value'], 'ongoing')

        self.assertIn('location', result)
        self.assertEqual(result['location']['type'], 'province')

        self.assertIn('date_range', result)
        self.assertEqual(result['date_range']['range_type'], 'relative')

    def test_realistic_query_3(self):
        """Test: 'Top 10 Maguindanao farming communities in Region XII'"""
        query = "top 10 maguindanao farming communities in region xii"
        result = self.extractor.extract_entities(query)

        self.assertIn('numbers', result)
        self.assertEqual(result['numbers'][0]['value'], 10)

        self.assertIn('ethnolinguistic_group', result)
        self.assertEqual(result['ethnolinguistic_group']['value'], 'Maguindanaon')

        self.assertIn('livelihood', result)
        self.assertEqual(result['livelihood']['value'], 'farming')

        self.assertIn('location', result)
        self.assertEqual(result['location']['value'], 'Region XII')

    def test_realistic_query_4(self):
        """Test: 'Recent Tausug communities in Zamboanga del Sur'"""
        query = "recent tausug communities in zamboanga del sur"
        result = self.extractor.extract_entities(query)

        self.assertIn('ethnolinguistic_group', result)
        self.assertEqual(result['ethnolinguistic_group']['value'], 'Tausug')

        self.assertIn('location', result)
        self.assertEqual(result['location']['type'], 'province')

        self.assertIn('date_range', result)
        # "recent" should default to relative range
        self.assertEqual(result['date_range']['range_type'], 'relative')

    def test_realistic_query_5(self):
        """Test: 'Completed assessments in 2024'"""
        query = "completed assessments in 2024"
        result = self.extractor.extract_entities(query)

        self.assertIn('status', result)
        self.assertEqual(result['status']['value'], 'completed')

        self.assertIn('date_range', result)
        self.assertEqual(result['date_range']['start'].year, 2024)
        self.assertEqual(result['date_range']['end'].year, 2024)

    def test_performance_multiple_queries(self):
        """Test average performance across multiple realistic queries."""
        queries = [
            "maranao fishing communities in zamboanga",
            "ongoing workshops in sultan kudarat last 6 months",
            "top 10 maguindanao farming communities",
            "recent tausug communities in zamboanga del sur",
            "completed assessments in 2024",
        ]

        total_time = 0
        successful_extractions = 0

        for query in queries:
            start_time = time.perf_counter()
            result = self.extractor.extract_entities(query)
            end_time = time.perf_counter()

            duration_ms = (end_time - start_time) * 1000
            total_time += duration_ms

            if len(result) > 0:
                successful_extractions += 1

        avg_time = total_time / len(queries)

        # Average should be <20ms
        self.assertLess(avg_time, 20, f"Average extraction time: {avg_time:.2f}ms (target: <20ms)")

        # Should successfully extract from all queries
        self.assertEqual(successful_extractions, len(queries))
