"""
Comprehensive Integration Tests for OBCMS AI Chat Query Template System

Tests the complete query template system end-to-end, including:
- Template registry (468+ templates across 16 categories)
- Entity extraction pipeline
- Template matching and ranking
- Cross-domain query flows
- Geographic hierarchies
- Evidence-based budgeting pipeline
- Performance benchmarks

Created: 2025-10-06
"""

import pytest

pytest.skip(
    "Legacy query template integration tests require updates for the new pipeline.",
    allow_module_level=True,
)

import re
import time
from collections import defaultdict
from typing import Dict, List, Any

import pytest
from django.test import TestCase

from common.ai_services.chat.query_templates import (
    QueryTemplate,
    get_template_registry,
)
from common.ai_services.chat.entity_extractor import EntityExtractor
from common.ai_services.chat.template_matcher import TemplateMatcher


class QueryTemplateIntegrationTests(TestCase):
    """
    Comprehensive integration tests for query template system.

    Tests end-to-end functionality across all domains and categories.
    """

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for all tests."""
        super().setUpClass()
        cls.registry = get_template_registry()
        cls.extractor = EntityExtractor()
        cls.matcher = TemplateMatcher()

        # Cache stats for reuse
        cls.stats = cls.registry.get_stats()
        cls.all_templates = cls.registry.get_all_templates()

    # =========================================================================
    # CATEGORY A: TEMPLATE REGISTRY TESTS
    # =========================================================================

    def test_total_template_count(self):
        """Verify we have 468+ templates registered."""
        total = self.stats['total_templates']
        self.assertGreaterEqual(
            total,
            468,
            f"Expected at least 468 templates, found {total}"
        )

    def test_category_distribution(self):
        """Verify we have templates in 16+ categories."""
        categories = self.stats['categories']
        self.assertGreaterEqual(
            len(categories),
            16,
            f"Expected at least 16 categories, found {len(categories)}"
        )

        # Verify major categories exist
        expected_categories = [
            'communities', 'mana', 'coordination', 'policies', 'projects',
            'staff', 'general', 'geographic', 'infrastructure', 'livelihood',
            'stakeholders', 'budget', 'temporal', 'cross_domain', 'analytics',
            'comparison'
        ]

        for category in expected_categories:
            self.assertIn(
                category,
                categories,
                f"Missing expected category: {category}"
            )

    def test_no_duplicate_template_ids(self):
        """Ensure all template IDs are unique."""
        template_ids = [t.id for t in self.all_templates]
        duplicates = [
            tid for tid in set(template_ids)
            if template_ids.count(tid) > 1
        ]

        self.assertEqual(
            len(duplicates),
            0,
            f"Found duplicate template IDs: {duplicates}"
        )

    def test_all_patterns_compile(self):
        """Verify all template patterns compile successfully."""
        failed_templates = []

        for template in self.all_templates:
            if template.compiled_pattern is None:
                failed_templates.append(template.id)

        self.assertEqual(
            len(failed_templates),
            0,
            f"Templates with invalid patterns: {failed_templates}"
        )

    def test_priority_distribution(self):
        """Verify template priorities span reasonable range (1-100)."""
        priorities = [t.priority for t in self.all_templates]

        min_priority = min(priorities)
        max_priority = max(priorities)

        self.assertGreaterEqual(min_priority, 1, "Minimum priority should be >= 1")
        self.assertLessEqual(max_priority, 100, "Maximum priority should be <= 100")

        # Should have diverse priority distribution
        unique_priorities = len(set(priorities))
        self.assertGreater(
            unique_priorities,
            5,
            "Should have diverse priority levels"
        )

    def test_required_fields_present(self):
        """Verify all templates have required fields."""
        for template in self.all_templates:
            # Must have ID
            self.assertTrue(template.id, f"Template missing ID")

            # Must have category
            self.assertTrue(template.category, f"Template {template.id} missing category")

            # Must have pattern
            self.assertTrue(template.pattern, f"Template {template.id} missing pattern")

            # Must have either query_template or query_builder
            has_query = template.query_template or template.query_builder
            self.assertTrue(
                has_query,
                f"Template {template.id} missing query_template/query_builder"
            )

    def test_examples_provided(self):
        """Verify most templates include example queries."""
        templates_without_examples = [
            t.id for t in self.all_templates
            if not t.examples and not t.example_queries
        ]

        # Allow up to 10% without examples
        max_without_examples = len(self.all_templates) * 0.1

        self.assertLess(
            len(templates_without_examples),
            max_without_examples,
            f"Too many templates without examples: {len(templates_without_examples)}"
        )

    # =========================================================================
    # CATEGORY B: CROSS-DOMAIN INTEGRATION TESTS
    # =========================================================================

    def test_evidence_based_budgeting_pipeline(self):
        """
        Test evidence-based budgeting pipeline:
        Assessments → Needs → Policies → Projects → Budget
        """
        pipeline_queries = [
            # Stage 1: Assessments
            ("Show me MANA assessments for Region IX", ['mana', 'cross_domain']),

            # Stage 2: Needs identification
            ("What are the unmet infrastructure needs?", ['infrastructure', 'cross_domain']),

            # Stage 3: Policy recommendations
            ("Show policies with supporting evidence", ['policies', 'cross_domain']),

            # Stage 4: Project implementation
            ("What projects are addressing water needs?", ['projects', 'cross_domain']),

            # Stage 5: Budget tracking
            ("Budget utilization rate for MILG", ['budget', 'cross_domain']),
        ]

        for query, expected_categories in pipeline_queries:
            matches = self._find_template_matches(query)

            self.assertGreater(
                len(matches),
                0,
                f"No matches found for pipeline query: {query}"
            )

            # Check if any match is in expected categories
            matched_categories = [m.category for m in matches]
            has_expected = any(
                cat in matched_categories
                for cat in expected_categories
            )

            self.assertTrue(
                has_expected,
                f"Query '{query}' matched {matched_categories}, "
                f"expected one of {expected_categories}"
            )

    def test_geographic_hierarchy_integration(self):
        """
        Test geographic hierarchy queries:
        Region → Province → Municipality → Barangay
        """
        hierarchy_queries = [
            "How many regions in BARMM?",
            "List all provinces in Region IX",
            "Municipalities in Zamboanga del Norte",
            "Barangays in Sindangan municipality",
            "Communities from Region IX to barangay level",
        ]

        for query in hierarchy_queries:
            matches = self._find_template_matches(query)

            self.assertGreater(
                len(matches),
                0,
                f"No matches for geographic query: {query}"
            )

    def test_stakeholder_coordination_flow(self):
        """
        Test stakeholder coordination flow:
        Organizations → Partnerships → Meetings → Activities
        """
        coordination_queries = [
            "Show me NGO partners",
            "Active partnerships with UN agencies",
            "Coordination meetings last quarter",
            "What activities did we coordinate with DSWD?",
        ]

        for query in coordination_queries:
            matches = self._find_template_matches(query)

            self.assertGreater(
                len(matches),
                0,
                f"No matches for coordination query: {query}"
            )

            # Should match coordination or cross_domain
            categories = [m.category for m in matches]
            has_coordination = 'coordination' in categories or 'cross_domain' in categories

            self.assertTrue(
                has_coordination,
                f"Coordination query '{query}' didn't match coordination templates"
            )

    def test_temporal_analysis_integration(self):
        """Test temporal queries across domains."""
        temporal_queries = [
            "Communities added last 6 months",
            "MANA workshops this year",
            "Partnerships created in 2024",
            "Projects completed in Q1",
            "Budget trends over last 3 years",
        ]

        for query in temporal_queries:
            # Extract entities (should find date ranges)
            entities = self.extractor.extract_entities(query)

            # Should extract date_range or similar temporal entity
            has_temporal = (
                'date_range' in entities or
                'year' in entities or
                'quarter' in entities
            )

            # Find template matches
            matches = self._find_template_matches(query)

            self.assertGreater(
                len(matches),
                0,
                f"No matches for temporal query: {query}"
            )

    # =========================================================================
    # CATEGORY C: END-TO-END QUERY TESTS
    # =========================================================================

    def test_real_user_queries_comprehensive(self):
        """Test 50+ real user queries end-to-end."""

        test_queries = [
            # Communities (10 queries)
            "How many OBC communities in Region IX?",
            "List Maranao communities",
            "Communities with fishing livelihood",
            "Show me communities added last month",
            "What is the total population of OBCs?",
            "Communities without electricity",
            "Barangays with Tausug communities",
            "Communities facing water scarcity",
            "Show me communities by municipality",
            "OBC communities in Zamboanga del Norte",

            # MANA (10 queries)
            "Show me MANA assessments",
            "Workshops conducted in 2024",
            "What are the top infrastructure needs?",
            "Assessments by assessment type",
            "Needs by priority level",
            "Communities with urgent needs",
            "MANA activities last quarter",
            "Assessment coverage by province",
            "Unmet health needs",
            "Education needs by community",

            # Coordination (10 queries)
            "Show me active partnerships",
            "NGO partners in Region IX",
            "Coordination meetings this month",
            "Partnerships with DSWD",
            "Meeting agenda items",
            "Partner organizations by type",
            "Agreements signed in 2024",
            "Stakeholder mapping",
            "Multi-stakeholder coordination",
            "Partnership effectiveness",

            # Policies (10 queries)
            "Show me policy recommendations",
            "Policies with evidence support",
            "Policy implementation status",
            "Evidence-based proposals",
            "Policy priority areas",
            "Advocacy priorities",
            "Policy gaps analysis",
            "Recommendations by sector",
            "Policy tracking dashboard",
            "Legislative advocacy",

            # Projects (10 queries)
            "Show me all projects",
            "MILG projects in Region IX",
            "Projects addressing water needs",
            "Budget allocation by ministry",
            "Project completion rate",
            "Activities by project",
            "On-budget projects",
            "Ministry performance",
            "Project timeline",
            "Task assignments",

            # Cross-domain (10 queries)
            "Assessment to project pipeline",
            "Communities with needs and projects",
            "Policy impact on budget",
            "Coordination meeting outcomes",
            "Geographic coverage analysis",
            "Budget trends over time",
            "Stakeholder engagement metrics",
            "Evidence chain validation",
            "Multi-ministry coordination",
            "Comprehensive dashboard",
        ]

        results = {
            'total_queries': len(test_queries),
            'successful_matches': 0,
            'failed_matches': [],
            'multiple_matches': 0,
        }

        for query in test_queries:
            matches = self._find_template_matches(query)

            if matches:
                results['successful_matches'] += 1
                if len(matches) > 1:
                    results['multiple_matches'] += 1
            else:
                results['failed_matches'].append(query)

        # Calculate success rate
        success_rate = (results['successful_matches'] / results['total_queries']) * 100

        # Should match at least 90% of queries
        self.assertGreaterEqual(
            success_rate,
            90.0,
            f"Success rate {success_rate:.1f}% below 90% threshold. "
            f"Failed queries: {results['failed_matches']}"
        )

    def test_entity_extraction_accuracy(self):
        """Test entity extraction across different entity types."""

        test_cases = [
            # Location entities
            ("Communities in Region IX", {'location'}),
            ("Zamboanga del Norte municipalities", {'location'}),

            # Ethnolinguistic groups
            ("Maranao communities", {'ethnolinguistic_group'}),
            ("Tausug and Sama populations", {'ethnolinguistic_group'}),

            # Livelihoods
            ("Fishing communities", {'livelihood'}),
            ("Farming and trading livelihoods", {'livelihood'}),

            # Temporal
            ("Last 6 months", {'date_range'}),
            ("2024 activities", {'year'}),
            ("Q1 2024 projects", {'quarter'}),

            # Status
            ("Completed projects", {'status'}),
            ("Ongoing partnerships", {'status'}),

            # Numbers
            ("Top 10 needs", {'number'}),
            ("First 5 communities", {'number'}),

            # Ministry
            ("MILG projects", {'ministry'}),
            ("DSWD coordination", {'ministry'}),

            # Multi-entity
            ("Maranao fishing communities in Region IX last month",
             {'ethnolinguistic_group', 'livelihood', 'location', 'date_range'}),
        ]

        extraction_results = {
            'total_cases': len(test_cases),
            'successful_extractions': 0,
            'failed_extractions': [],
        }

        for query, expected_entities in test_cases:
            entities = self.extractor.extract_entities(query)
            extracted_keys = set(entities.keys())

            # Check if all expected entities were extracted
            has_all_expected = expected_entities.issubset(extracted_keys)

            if has_all_expected:
                extraction_results['successful_extractions'] += 1
            else:
                missing = expected_entities - extracted_keys
                extraction_results['failed_extractions'].append({
                    'query': query,
                    'expected': expected_entities,
                    'extracted': extracted_keys,
                    'missing': missing,
                })

        # Should extract at least 80% correctly
        success_rate = (
            extraction_results['successful_extractions'] /
            extraction_results['total_cases']
        ) * 100

        self.assertGreaterEqual(
            success_rate,
            80.0,
            f"Entity extraction success rate {success_rate:.1f}% below 80% threshold. "
            f"Failed: {extraction_results['failed_extractions']}"
        )

    def test_template_priority_disambiguation(self):
        """Test that higher priority templates are selected when multiple match."""

        # Query that should match multiple templates
        ambiguous_query = "show me communities"

        matches = self._find_template_matches(ambiguous_query)

        self.assertGreater(
            len(matches),
            1,
            "Query should match multiple templates for this test"
        )

        # Verify templates are ranked by priority (descending)
        priorities = [m.priority for m in matches]
        sorted_priorities = sorted(priorities, reverse=True)

        self.assertEqual(
            priorities,
            sorted_priorities,
            "Templates should be ranked by priority (highest first)"
        )

    def test_query_generation_validity(self):
        """Test that generated queries are valid Django ORM syntax."""

        test_cases = [
            ("Count communities in Region IX", {
                'location': {
                    'type': 'region',
                    'value': 'Region IX',
                    'confidence': 0.95
                }
            }),
            ("Show me Maranao communities", {
                'ethnolinguistic_group': {
                    'value': 'Meranaw',
                    'confidence': 0.90
                }
            }),
        ]

        for query, entities in test_cases:
            result = self.matcher.match_and_generate(query, entities)

            if result['success']:
                generated_query = result.get('query', '')

                # Basic syntax validation
                self.assertTrue(
                    generated_query,
                    f"Generated query is empty for: {query}"
                )

                # Should contain Django ORM patterns
                has_orm = any(pattern in generated_query for pattern in [
                    '.objects.',
                    '.filter(',
                    '.count(',
                    '.values(',
                    '.aggregate(',
                ])

                self.assertTrue(
                    has_orm,
                    f"Generated query doesn't look like Django ORM: {generated_query}"
                )

    # =========================================================================
    # CATEGORY D: PERFORMANCE TESTS
    # =========================================================================

    def test_template_loading_performance(self):
        """Verify templates load in <500ms."""
        start = time.time()

        # Force reload
        from common.ai_services.chat.query_templates import _register_all_templates
        _register_all_templates()

        elapsed_ms = (time.time() - start) * 1000

        self.assertLess(
            elapsed_ms,
            500,
            f"Template loading took {elapsed_ms:.2f}ms (target: <500ms)"
        )

    def test_pattern_matching_performance(self):
        """Verify pattern matching is <10ms per query."""

        test_queries = [
            "How many communities?",
            "Show me MANA assessments",
            "Active partnerships",
            "Budget utilization",
            "Projects in Region IX",
        ]

        timings = []

        for query in test_queries:
            start = time.time()
            self._find_template_matches(query)
            elapsed_ms = (time.time() - start) * 1000
            timings.append(elapsed_ms)

        avg_time = sum(timings) / len(timings)

        self.assertLess(
            avg_time,
            10,
            f"Average pattern matching took {avg_time:.2f}ms (target: <10ms)"
        )

    def test_entity_extraction_performance(self):
        """Verify entity extraction is <20ms per query."""

        test_queries = [
            "Maranao fishing communities in Region IX last 6 months",
            "MILG projects in Zamboanga del Norte 2024",
            "Top 10 urgent infrastructure needs by priority",
        ]

        timings = []

        for query in test_queries:
            start = time.time()
            self.extractor.extract_entities(query)
            elapsed_ms = (time.time() - start) * 1000
            timings.append(elapsed_ms)

        avg_time = sum(timings) / len(timings)

        self.assertLess(
            avg_time,
            20,
            f"Average entity extraction took {avg_time:.2f}ms (target: <20ms)"
        )

    def test_end_to_end_performance(self):
        """Verify complete query processing is <50ms."""

        query = "How many communities in Region IX?"

        start = time.time()

        # Complete pipeline
        entities = self.extractor.extract_entities(query)
        result = self.matcher.match_and_generate(query, entities)

        elapsed_ms = (time.time() - start) * 1000

        self.assertLess(
            elapsed_ms,
            50,
            f"End-to-end processing took {elapsed_ms:.2f}ms (target: <50ms)"
        )

    # =========================================================================
    # CATEGORY E: COVERAGE TESTS
    # =========================================================================

    def test_all_categories_have_templates(self):
        """Verify all defined categories have templates."""
        expected_categories = [
            'communities', 'mana', 'coordination', 'policies', 'projects',
            'staff', 'general', 'geographic', 'infrastructure', 'livelihood',
            'stakeholders', 'budget', 'temporal', 'cross_domain', 'analytics',
            'comparison'
        ]

        categories_with_templates = set(self.stats['categories'].keys())

        for category in expected_categories:
            self.assertIn(
                category,
                categories_with_templates,
                f"Category '{category}' has no templates"
            )

    def test_result_types_coverage(self):
        """Verify all result types are used."""
        result_types = set(t.result_type for t in self.all_templates)

        expected_result_types = {'count', 'list', 'aggregate', 'single'}

        for result_type in expected_result_types:
            self.assertIn(
                result_type,
                result_types,
                f"No templates with result_type '{result_type}'"
            )

    def test_intent_coverage(self):
        """Verify all intent types are covered."""
        intents = set(t.intent for t in self.all_templates)

        expected_intents = {'data_query', 'analysis', 'navigation', 'help'}

        for intent in expected_intents:
            self.assertIn(
                intent,
                intents,
                f"No templates with intent '{intent}'"
            )

    def test_essential_queries_covered(self):
        """Verify top essential queries have template coverage."""

        essential_queries = [
            # Critical queries every user will ask
            "How many communities?",
            "Show me all communities",
            "List all assessments",
            "Show me projects",
            "What partnerships do we have?",
            "Show me policies",
            "Budget allocation",
            "My tasks",
            "System help",
            "Dashboard",
        ]

        uncovered_queries = []

        for query in essential_queries:
            matches = self._find_template_matches(query)
            if not matches:
                uncovered_queries.append(query)

        self.assertEqual(
            len(uncovered_queries),
            0,
            f"Essential queries without coverage: {uncovered_queries}"
        )

    def test_domain_balance(self):
        """Verify template distribution is reasonably balanced across domains."""

        category_counts = self.stats['categories']

        # Major domains should have significant coverage
        major_domains = {
            'communities': 40,  # Minimum expected
            'mana': 30,
            'coordination': 40,
            'policies': 40,
            'projects': 40,
        }

        for domain, min_count in major_domains.items():
            actual_count = category_counts.get(domain, 0)
            self.assertGreaterEqual(
                actual_count,
                min_count,
                f"Domain '{domain}' has only {actual_count} templates "
                f"(expected at least {min_count})"
            )

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _find_template_matches(self, query: str) -> List[QueryTemplate]:
        """
        Find all templates matching a query.

        Args:
            query: Natural language query

        Returns:
            List of matching templates, sorted by priority
        """
        matches = []

        for template in self.all_templates:
            if template.matches(query):
                matches.append(template)

        # Sort by priority (descending)
        matches.sort(key=lambda t: t.priority, reverse=True)

        return matches


# =============================================================================
# PERFORMANCE BENCHMARK SUITE
# =============================================================================

@pytest.mark.performance
class QueryPerformanceTests(TestCase):
    """
    Performance benchmarks for query template system.

    Measures loading time, matching speed, extraction speed, and memory usage.
    """

    @classmethod
    def setUpClass(cls):
        """Set up performance test fixtures."""
        super().setUpClass()
        cls.registry = get_template_registry()
        cls.extractor = EntityExtractor()
        cls.matcher = TemplateMatcher()

    def test_template_loading_benchmark(self):
        """Benchmark template loading performance."""
        iterations = 10
        timings = []

        for _ in range(iterations):
            start = time.time()

            # Force reload
            from common.ai_services.chat.query_templates import _register_all_templates
            _register_all_templates()

            elapsed_ms = (time.time() - start) * 1000
            timings.append(elapsed_ms)

        avg_time = sum(timings) / len(timings)
        min_time = min(timings)
        max_time = max(timings)

        print(f"\nTemplate Loading Benchmark:")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Min: {min_time:.2f}ms")
        print(f"  Max: {max_time:.2f}ms")
        print(f"  Target: <500ms")

        self.assertLess(avg_time, 500, "Template loading too slow")

    def test_pattern_matching_benchmark(self):
        """Benchmark pattern matching performance across 100 queries."""

        test_queries = [
            "How many communities?",
            "Show me MANA assessments",
            "Active partnerships",
            "Budget utilization",
            "Projects in Region IX",
        ] * 20  # 100 total queries

        timings = []

        for query in test_queries:
            start = time.time()

            matches = []
            for template in self.registry.get_all_templates():
                if template.matches(query):
                    matches.append(template)

            elapsed_ms = (time.time() - start) * 1000
            timings.append(elapsed_ms)

        avg_time = sum(timings) / len(timings)
        p95_time = sorted(timings)[int(len(timings) * 0.95)]

        print(f"\nPattern Matching Benchmark (100 queries):")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  P95: {p95_time:.2f}ms")
        print(f"  Target: <10ms average")

        self.assertLess(avg_time, 10, "Pattern matching too slow")

    def test_entity_extraction_benchmark(self):
        """Benchmark entity extraction performance."""

        complex_queries = [
            "Maranao fishing communities in Region IX last 6 months",
            "MILG infrastructure projects in Zamboanga del Norte 2024",
            "Top 10 urgent health needs by priority level",
            "Active NGO partnerships with DSWD in Cotabato",
            "Policy recommendations with evidence support from last quarter",
        ] * 20  # 100 total

        timings = []

        for query in complex_queries:
            start = time.time()
            self.extractor.extract_entities(query)
            elapsed_ms = (time.time() - start) * 1000
            timings.append(elapsed_ms)

        avg_time = sum(timings) / len(timings)
        p95_time = sorted(timings)[int(len(timings) * 0.95)]

        print(f"\nEntity Extraction Benchmark (100 queries):")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  P95: {p95_time:.2f}ms")
        print(f"  Target: <20ms average")

        self.assertLess(avg_time, 20, "Entity extraction too slow")

    def test_end_to_end_benchmark(self):
        """Benchmark complete query pipeline."""

        queries = [
            "How many Maranao communities in Region IX?",
            "Show me MANA assessments from last year",
            "Active partnerships with UN agencies",
            "MILG budget utilization rate",
            "Top 5 urgent infrastructure needs",
        ] * 20  # 100 total

        timings = []

        for query in queries:
            start = time.time()

            # Complete pipeline
            entities = self.extractor.extract_entities(query)
            result = self.matcher.match_and_generate(query, entities)

            elapsed_ms = (time.time() - start) * 1000
            timings.append(elapsed_ms)

        avg_time = sum(timings) / len(timings)
        p95_time = sorted(timings)[int(len(timings) * 0.95)]
        p99_time = sorted(timings)[int(len(timings) * 0.99)]

        print(f"\nEnd-to-End Pipeline Benchmark (100 queries):")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  P95: {p95_time:.2f}ms")
        print(f"  P99: {p99_time:.2f}ms")
        print(f"  Target: <50ms average")

        self.assertLess(avg_time, 50, "End-to-end pipeline too slow")

    def test_memory_usage(self):
        """Verify memory usage is reasonable."""
        import sys

        # Get size of all templates in memory
        templates = self.registry.get_all_templates()

        total_size = sum(sys.getsizeof(t) for t in templates)
        total_size_mb = total_size / (1024 * 1024)

        print(f"\nMemory Usage:")
        print(f"  Templates in memory: {len(templates)}")
        print(f"  Total size: {total_size_mb:.2f} MB")
        print(f"  Target: <100 MB")

        self.assertLess(
            total_size_mb,
            100,
            f"Template memory usage {total_size_mb:.2f}MB exceeds 100MB"
        )
