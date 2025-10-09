"""
Test suite for Advanced Entity Extractors (Phase 2).

Tests the 6 new entity extractors:
- MinistryResolver
- BudgetRangeResolver
- AssessmentTypeResolver
- PartnershipTypeResolver
- Plus additional sector/priority extractors

Target: <20ms per extraction, 95%+ accuracy
"""

import pytest

import time
from django.test import TestCase

from common.ai_services.chat.entity_extractor import EntityExtractor
from common.ai_services.chat.entity_resolvers import (
    MinistryResolver,
    BudgetRangeResolver,
    AssessmentTypeResolver,
    PartnershipTypeResolver,
)


class MinistryResolverTestCase(TestCase):
    """Test suite for MinistryResolver."""

    def setUp(self):
        """Set up test fixtures."""
        self.resolver = MinistryResolver()

    def test_extract_ministry_milg(self):
        """Test MILG extraction."""
        result = self.resolver.resolve("MILG projects in Region IX")
        self.assertIsNotNone(result)
        self.assertEqual(result['value'], 'MILG')
        self.assertGreaterEqual(result['confidence'], 0.90)

    def test_extract_ministry_mssd(self):
        """Test MSSD extraction."""
        result = self.resolver.resolve("ministry of social services programs")
        self.assertIsNotNone(result)
        self.assertEqual(result['value'], 'MSSD')
        self.assertGreaterEqual(result['confidence'], 0.90)

    def test_extract_ministry_variations(self):
        """Test ministry name variations."""
        queries = [
            ("local government initiatives", 'MILG'),
            ("ministry of social services programs", 'MSSD'),
            ("ministry of health programs", 'MHPW'),
            ("ministry of basic education projects", 'MBDA'),
        ]

        for query, expected_ministry in queries:
            result = self.resolver.resolve(query)
            self.assertIsNotNone(result, f"Failed to extract ministry from: {query}")
            self.assertEqual(result['value'], expected_ministry)

    def test_extract_ministry_none(self):
        """Test query with no ministry."""
        result = self.resolver.resolve("show me all communities")
        self.assertIsNone(result)


class BudgetRangeResolverTestCase(TestCase):
    """Test suite for BudgetRangeResolver."""

    def setUp(self):
        """Set up test fixtures."""
        self.resolver = BudgetRangeResolver()

    def test_extract_budget_under(self):
        """Test 'under X million' pattern."""
        result = self.resolver.resolve("projects under 1M")
        self.assertIsNotNone(result)
        self.assertEqual(result['min'], 0)
        self.assertEqual(result['max'], 1_000_000)
        self.assertGreaterEqual(result['confidence'], 0.95)

    def test_extract_budget_over(self):
        """Test 'over X million' pattern."""
        result = self.resolver.resolve("programs over 5 million")
        self.assertIsNotNone(result)
        self.assertEqual(result['min'], 5_000_000)
        self.assertIsNone(result['max'])
        self.assertGreaterEqual(result['confidence'], 0.95)

    def test_extract_budget_between(self):
        """Test 'between X and Y' pattern."""
        result = self.resolver.resolve("projects between 1 and 5 million")
        self.assertIsNotNone(result)
        self.assertEqual(result['min'], 1_000_000)
        self.assertEqual(result['max'], 5_000_000)
        self.assertGreaterEqual(result['confidence'], 0.95)

    def test_extract_budget_exact(self):
        """Test 'X million budget' pattern."""
        result = self.resolver.resolve("2 million budget allocation")
        self.assertIsNotNone(result)
        self.assertEqual(result['min'], 1_800_000)  # 10% tolerance
        self.assertEqual(result['max'], 2_200_000)
        self.assertGreaterEqual(result['confidence'], 0.90)

    def test_extract_budget_decimal(self):
        """Test decimal amounts."""
        result = self.resolver.resolve("projects under 2.5 million")
        self.assertIsNotNone(result)
        self.assertEqual(result['min'], 0)
        self.assertEqual(result['max'], 2_500_000)

    def test_extract_budget_none(self):
        """Test query with no budget."""
        result = self.resolver.resolve("show me all projects")
        self.assertIsNone(result)


class AssessmentTypeResolverTestCase(TestCase):
    """Test suite for AssessmentTypeResolver."""

    def setUp(self):
        """Set up test fixtures."""
        self.resolver = AssessmentTypeResolver()

    def test_extract_assessment_rapid(self):
        """Test rapid assessment extraction."""
        queries = [
            "rapid assessment results",
            "quick assessment in Region IX",
            "fast assessment needed",
        ]

        for query in queries:
            result = self.resolver.resolve(query)
            self.assertIsNotNone(result, f"Failed on: {query}")
            self.assertEqual(result['value'], 'rapid')
            self.assertGreaterEqual(result['confidence'], 0.90)

    def test_extract_assessment_comprehensive(self):
        """Test comprehensive assessment extraction."""
        result = self.resolver.resolve("comprehensive assessment report")
        self.assertIsNotNone(result)
        self.assertEqual(result['value'], 'comprehensive')
        self.assertGreaterEqual(result['confidence'], 0.95)

    def test_extract_assessment_baseline(self):
        """Test baseline assessment extraction."""
        result = self.resolver.resolve("baseline assessment data")
        self.assertIsNotNone(result)
        self.assertEqual(result['value'], 'baseline')

    def test_extract_assessment_thematic(self):
        """Test thematic assessment extraction."""
        result = self.resolver.resolve("thematic assessment on education")
        self.assertIsNotNone(result)
        self.assertEqual(result['value'], 'thematic')

    def test_extract_assessment_needs(self):
        """Test needs assessment extraction."""
        result = self.resolver.resolve("needs assessment completed")
        self.assertIsNotNone(result)
        self.assertEqual(result['value'], 'needs_assessment')

    def test_extract_assessment_none(self):
        """Test query with no assessment type."""
        result = self.resolver.resolve("show me all data")
        self.assertIsNone(result)


class PartnershipTypeResolverTestCase(TestCase):
    """Test suite for PartnershipTypeResolver."""

    def setUp(self):
        """Set up test fixtures."""
        self.resolver = PartnershipTypeResolver()

    def test_extract_partnership_moa(self):
        """Test MOA extraction."""
        queries = [
            "MOA with DSWD",
            "memorandum of agreement signed",
            "new agreement with NGO",
        ]

        for query in queries:
            result = self.resolver.resolve(query)
            self.assertIsNotNone(result, f"Failed on: {query}")
            self.assertEqual(result['value'], 'MOA')
            self.assertGreaterEqual(result['confidence'], 0.90)

    def test_extract_partnership_mou(self):
        """Test MOU extraction."""
        result = self.resolver.resolve("MOU with local government")
        self.assertIsNotNone(result)
        self.assertEqual(result['value'], 'MOU')
        self.assertGreaterEqual(result['confidence'], 0.95)

    def test_extract_partnership_collaboration(self):
        """Test collaboration extraction."""
        queries = [
            "collaboration with stakeholders",
            "joint partnership program",
        ]

        for query in queries:
            result = self.resolver.resolve(query)
            self.assertIsNotNone(result, f"Failed on: {query}")
            self.assertEqual(result['value'], 'collaboration')

    def test_extract_partnership_technical_assistance(self):
        """Test technical assistance extraction."""
        result = self.resolver.resolve("technical assistance from UNDP")
        self.assertIsNotNone(result)
        self.assertEqual(result['value'], 'technical_assistance')

    def test_extract_partnership_capacity_building(self):
        """Test capacity building extraction."""
        result = self.resolver.resolve("capacity building training")
        self.assertIsNotNone(result)
        self.assertEqual(result['value'], 'capacity_building')

    def test_extract_partnership_none(self):
        """Test query with no partnership type."""
        result = self.resolver.resolve("show me all activities")
        self.assertIsNone(result)


class AdvancedEntityExtractorTestCase(TestCase):
    """Integration tests for EntityExtractor with advanced extractors."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = EntityExtractor()

    def test_extract_ministry_entities(self):
        """Test ministry entity extraction through EntityExtractor."""
        query = "MILG projects in Region IX"
        result = self.extractor.extract_entities(query)

        self.assertIn('ministry', result)
        self.assertEqual(result['ministry']['value'], 'MILG')

    def test_extract_budget_entities(self):
        """Test budget range entity extraction."""
        query = "projects under 1M in Zamboanga"
        result = self.extractor.extract_entities(query)

        self.assertIn('budget_range', result)
        self.assertEqual(result['budget_range']['min'], 0)
        self.assertEqual(result['budget_range']['max'], 1_000_000)

    def test_extract_assessment_entities(self):
        """Test assessment type entity extraction."""
        query = "rapid assessment results"
        result = self.extractor.extract_entities(query)

        self.assertIn('assessment_type', result)
        self.assertEqual(result['assessment_type']['value'], 'rapid')

    def test_extract_partnership_entities(self):
        """Test partnership type entity extraction."""
        query = "MOA with DSWD for social programs"
        result = self.extractor.extract_entities(query)

        self.assertIn('partnership_type', result)
        self.assertEqual(result['partnership_type']['value'], 'MOA')

    def test_extract_complex_query_with_advanced_entities(self):
        """Test complex query with multiple advanced entities."""
        query = "MILG projects under 5M with MOA in Region IX last year"
        result = self.extractor.extract_entities(query)

        # Should extract ministry, budget, partnership, location, date
        self.assertIn('ministry', result)
        self.assertIn('budget_range', result)
        self.assertIn('partnership_type', result)
        self.assertIn('location', result)
        self.assertIn('date_range', result)

        # Verify values
        self.assertEqual(result['ministry']['value'], 'MILG')
        self.assertEqual(result['budget_range']['max'], 5_000_000)
        self.assertEqual(result['partnership_type']['value'], 'MOA')

    def test_performance_advanced_extractors(self):
        """Test performance of advanced entity extractors."""
        queries = [
            "MILG projects under 1M",
            "rapid assessment with MOA",
            "comprehensive assessment over 5 million",
            "MSSD programs with technical assistance",
        ]

        total_time = 0
        for query in queries:
            start = time.time()
            result = self.extractor.extract_entities(query)
            elapsed = (time.time() - start) * 1000  # ms

            total_time += elapsed
            self.assertLess(elapsed, 20, f"Extraction took {elapsed:.2f}ms (target: <20ms)")

        avg_time = total_time / len(queries)
        print(f"\nAdvanced entity extraction average: {avg_time:.2f}ms")


class AdvancedResolverEdgeCasesTestCase(TestCase):
    """Edge case tests for advanced resolvers."""

    def test_ministry_case_insensitive(self):
        """Test case-insensitive ministry extraction."""
        resolver = MinistryResolver()

        queries = [
            "MILG projects",
            "milg projects",
            "Milg projects",
        ]

        for query in queries:
            result = resolver.resolve(query)
            self.assertIsNotNone(result)
            self.assertEqual(result['value'], 'MILG')

    def test_budget_various_formats(self):
        """Test budget extraction with various formats."""
        resolver = BudgetRangeResolver()

        # Test 'M' vs 'million'
        result1 = resolver.resolve("under 5M")
        result2 = resolver.resolve("under 5 million")

        self.assertEqual(result1['max'], result2['max'])

    def test_assessment_keyword_boundaries(self):
        """Test assessment type with word boundaries."""
        resolver = AssessmentTypeResolver()

        # Should NOT match "assessment" in "reassessment"
        result = resolver.resolve("rapid reassessment")
        # Should still match "rapid"
        self.assertIsNotNone(result)
        self.assertEqual(result['value'], 'rapid')

    def test_partnership_multiple_types(self):
        """Test query with multiple partnership types."""
        extractor = EntityExtractor()

        # Should extract first match (MOA has higher priority)
        query = "MOA and MOU with stakeholders"
        result = extractor.extract_entities(query)

        self.assertIn('partnership_type', result)
        # Should return first match (MOA)
        self.assertEqual(result['partnership_type']['value'], 'MOA')
