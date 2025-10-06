"""
Performance Benchmarks for OBCMS Query Template System

Dedicated performance testing suite focusing on:
- Template loading speed
- Pattern matching latency
- Entity extraction speed
- Memory efficiency
- Concurrent query handling
- Cache effectiveness

Created: 2025-10-06
Target: All operations <50ms, loading <500ms
"""

import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

import pytest
from django.test import TestCase

from common.ai_services.chat.query_templates import get_template_registry
from common.ai_services.chat.entity_extractor import EntityExtractor
from common.ai_services.chat.template_matcher import TemplateMatcher


class TemplateLoadingPerformanceTests(TestCase):
    """Test template loading and initialization performance."""

    def test_initial_load_time(self):
        """Templates should load in <500ms on first import."""
        start = time.time()

        # Force fresh import
        from common.ai_services.chat.query_templates import _register_all_templates
        _register_all_templates()

        registry = get_template_registry()
        templates = registry.get_all_templates()

        elapsed_ms = (time.time() - start) * 1000

        print(f"\nInitial template loading:")
        print(f"  Loaded: {len(templates)} templates")
        print(f"  Time: {elapsed_ms:.2f}ms")
        print(f"  Target: <500ms")

        self.assertGreaterEqual(len(templates), 468, "Should load 468+ templates")
        self.assertLess(elapsed_ms, 500, "Initial load should be <500ms")

    def test_cached_access_time(self):
        """Cached template access should be nearly instant."""
        registry = get_template_registry()

        # Warm up cache
        _ = registry.get_all_templates()

        # Measure cached access
        iterations = 100
        timings = []

        for _ in range(iterations):
            start = time.time()
            templates = registry.get_all_templates()
            elapsed_ms = (time.time() - start) * 1000
            timings.append(elapsed_ms)

        avg_time = statistics.mean(timings)
        median_time = statistics.median(timings)

        print(f"\nCached template access (100 iterations):")
        print(f"  Average: {avg_time:.4f}ms")
        print(f"  Median: {median_time:.4f}ms")
        print(f"  Target: <1ms")

        self.assertLess(avg_time, 1.0, "Cached access should be <1ms")

    def test_category_filter_performance(self):
        """Filtering templates by category should be fast."""
        registry = get_template_registry()

        categories = ['communities', 'mana', 'coordination', 'policies', 'projects']
        timings = []

        for category in categories * 20:  # 100 total
            start = time.time()
            templates = registry.get_templates_by_category(category)
            elapsed_ms = (time.time() - start) * 1000
            timings.append(elapsed_ms)

        avg_time = statistics.mean(timings)

        print(f"\nCategory filtering (100 operations):")
        print(f"  Average: {avg_time:.4f}ms")
        print(f"  Target: <1ms")

        self.assertLess(avg_time, 1.0, "Category filtering should be <1ms")


class PatternMatchingPerformanceTests(TestCase):
    """Test pattern matching performance."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        super().setUpClass()
        cls.registry = get_template_registry()
        cls.all_templates = cls.registry.get_all_templates()

    def test_single_query_matching(self):
        """Single query matching should be <10ms."""
        test_queries = [
            "How many communities?",
            "Show me MANA assessments",
            "Active partnerships",
            "Budget utilization",
            "Projects in Region IX",
        ]

        timings = []

        for query in test_queries * 20:  # 100 total
            start = time.time()

            matches = []
            for template in self.all_templates:
                if template.matches(query):
                    matches.append(template)

            elapsed_ms = (time.time() - start) * 1000
            timings.append(elapsed_ms)

        avg_time = statistics.mean(timings)
        p95_time = statistics.quantiles(timings, n=20)[18]  # 95th percentile

        print(f"\nSingle query matching (100 queries):")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  P95: {p95_time:.2f}ms")
        print(f"  Target: <10ms average")

        self.assertLess(avg_time, 10, "Pattern matching should average <10ms")

    def test_complex_query_matching(self):
        """Complex multi-entity queries should still be fast."""
        complex_queries = [
            "Show me Maranao fishing communities in Region IX from last 6 months",
            "MILG infrastructure projects in Zamboanga del Norte completed in 2024",
            "Top 10 urgent health needs by priority level in Cotabato province",
        ]

        timings = []

        for query in complex_queries * 20:  # 60 total
            start = time.time()

            matches = []
            for template in self.all_templates:
                if template.matches(query):
                    matches.append(template)

            elapsed_ms = (time.time() - start) * 1000
            timings.append(elapsed_ms)

        avg_time = statistics.mean(timings)

        print(f"\nComplex query matching (60 queries):")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Target: <15ms")

        self.assertLess(avg_time, 15, "Complex matching should be <15ms")

    def test_no_match_performance(self):
        """Queries with no matches should fail fast."""
        no_match_queries = [
            "xyzabc nonsense query",
            "completely unrelated garbage text",
            "nothing will match this random string",
        ]

        timings = []

        for query in no_match_queries * 20:  # 60 total
            start = time.time()

            matches = []
            for template in self.all_templates:
                if template.matches(query):
                    matches.append(template)

            elapsed_ms = (time.time() - start) * 1000
            timings.append(elapsed_ms)

        avg_time = statistics.mean(timings)

        print(f"\nNo-match query performance (60 queries):")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Target: <5ms (should fail fast)")

        self.assertLess(avg_time, 5, "No-match should fail fast <5ms")


class EntityExtractionPerformanceTests(TestCase):
    """Test entity extraction performance."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        super().setUpClass()
        cls.extractor = EntityExtractor()

    def test_simple_entity_extraction(self):
        """Simple entity extraction should be <10ms."""
        simple_queries = [
            "Region IX",
            "Maranao communities",
            "fishing livelihood",
            "last month",
            "completed status",
        ]

        timings = []

        for query in simple_queries * 20:  # 100 total
            start = time.time()
            entities = self.extractor.extract_entities(query)
            elapsed_ms = (time.time() - start) * 1000
            timings.append(elapsed_ms)

        avg_time = statistics.mean(timings)

        print(f"\nSimple entity extraction (100 queries):")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Target: <10ms")

        self.assertLess(avg_time, 10, "Simple extraction should be <10ms")

    def test_complex_entity_extraction(self):
        """Complex multi-entity extraction should be <20ms."""
        complex_queries = [
            "Maranao fishing communities in Zamboanga del Norte last 6 months",
            "MILG infrastructure projects in Region IX 2024 urgent priority",
            "Top 10 health needs in Cotabato completed status by municipality",
        ]

        timings = []

        for query in complex_queries * 20:  # 60 total
            start = time.time()
            entities = self.extractor.extract_entities(query)
            elapsed_ms = (time.time() - start) * 1000
            timings.append(elapsed_ms)

        avg_time = statistics.mean(timings)
        p95_time = statistics.quantiles(timings, n=20)[18]

        print(f"\nComplex entity extraction (60 queries):")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  P95: {p95_time:.2f}ms")
        print(f"  Target: <20ms average")

        self.assertLess(avg_time, 20, "Complex extraction should be <20ms")

    def test_location_resolution_performance(self):
        """Location entity resolution should be fast."""
        location_queries = [
            "Region IX",
            "Zamboanga del Norte",
            "Sindangan municipality",
            "Barangay Poblacion",
        ]

        timings = []

        for query in location_queries * 25:  # 100 total
            start = time.time()
            entities = self.extractor.extract_entities(query)
            elapsed_ms = (time.time() - start) * 1000
            timings.append(elapsed_ms)

        avg_time = statistics.mean(timings)

        print(f"\nLocation resolution (100 queries):")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Target: <10ms")

        self.assertLess(avg_time, 10, "Location resolution should be <10ms")


class EndToEndPerformanceTests(TestCase):
    """Test complete query pipeline performance."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        super().setUpClass()
        cls.extractor = EntityExtractor()
        cls.matcher = TemplateMatcher()

    def test_full_pipeline_performance(self):
        """Complete pipeline should be <50ms."""
        test_queries = [
            "How many Maranao communities in Region IX?",
            "Show me MANA assessments from last year",
            "Active partnerships with UN agencies",
            "MILG budget utilization rate",
            "Top 5 urgent infrastructure needs",
        ]

        timings = []

        for query in test_queries * 20:  # 100 total
            start = time.time()

            # Full pipeline
            entities = self.extractor.extract_entities(query)
            result = self.matcher.match_and_generate(query, entities)

            elapsed_ms = (time.time() - start) * 1000
            timings.append(elapsed_ms)

        avg_time = statistics.mean(timings)
        median_time = statistics.median(timings)
        p95_time = statistics.quantiles(timings, n=20)[18]
        p99_time = statistics.quantiles(timings, n=100)[98]

        print(f"\nEnd-to-end pipeline (100 queries):")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Median: {median_time:.2f}ms")
        print(f"  P95: {p95_time:.2f}ms")
        print(f"  P99: {p99_time:.2f}ms")
        print(f"  Target: <50ms average")

        self.assertLess(avg_time, 50, "End-to-end pipeline should be <50ms")

    def test_successful_vs_failed_query_performance(self):
        """Compare performance of successful vs failed queries."""
        successful_queries = [
            "How many communities?",
            "Show me assessments",
            "Active partnerships",
        ]

        failed_queries = [
            "xyzabc nonsense",
            "completely random text",
            "nothing matches this",
        ]

        successful_timings = []
        for query in successful_queries * 20:
            start = time.time()
            entities = self.extractor.extract_entities(query)
            result = self.matcher.match_and_generate(query, entities)
            elapsed_ms = (time.time() - start) * 1000
            successful_timings.append(elapsed_ms)

        failed_timings = []
        for query in failed_queries * 20:
            start = time.time()
            entities = self.extractor.extract_entities(query)
            result = self.matcher.match_and_generate(query, entities)
            elapsed_ms = (time.time() - start) * 1000
            failed_timings.append(elapsed_ms)

        avg_successful = statistics.mean(successful_timings)
        avg_failed = statistics.mean(failed_timings)

        print(f"\nSuccessful vs Failed Queries:")
        print(f"  Successful average: {avg_successful:.2f}ms")
        print(f"  Failed average: {avg_failed:.2f}ms")
        print(f"  Ratio: {avg_successful / avg_failed:.2f}x")

        # Failed queries should not be significantly slower
        self.assertLess(
            avg_failed,
            avg_successful * 1.5,
            "Failed queries should not be >1.5x slower"
        )


class ConcurrencyPerformanceTests(TestCase):
    """Test concurrent query handling performance."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        super().setUpClass()
        cls.extractor = EntityExtractor()
        cls.matcher = TemplateMatcher()

    def test_concurrent_query_processing(self):
        """System should handle concurrent queries efficiently."""
        test_queries = [
            "How many communities?",
            "Show me assessments",
            "Active partnerships",
            "Budget utilization",
            "Projects in Region IX",
        ] * 10  # 50 queries

        def process_query(query):
            """Process a single query."""
            start = time.time()
            entities = self.extractor.extract_entities(query)
            result = self.matcher.match_and_generate(query, entities)
            elapsed_ms = (time.time() - start) * 1000
            return elapsed_ms

        # Test with different thread counts
        thread_counts = [1, 5, 10]

        for num_threads in thread_counts:
            start = time.time()

            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = [executor.submit(process_query, q) for q in test_queries]
                timings = [f.result() for f in as_completed(futures)]

            total_time = (time.time() - start) * 1000
            avg_query_time = statistics.mean(timings)
            throughput = len(test_queries) / (total_time / 1000)  # queries/sec

            print(f"\nConcurrent processing ({num_threads} threads, 50 queries):")
            print(f"  Total time: {total_time:.2f}ms")
            print(f"  Avg query time: {avg_query_time:.2f}ms")
            print(f"  Throughput: {throughput:.1f} queries/sec")

            # All queries should complete in reasonable time
            self.assertLess(
                total_time,
                5000,  # 5 seconds for 50 queries
                f"Concurrent processing too slow with {num_threads} threads"
            )


class MemoryPerformanceTests(TestCase):
    """Test memory usage and efficiency."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        super().setUpClass()
        cls.registry = get_template_registry()
        cls.extractor = EntityExtractor()
        cls.matcher = TemplateMatcher()

    def test_template_memory_usage(self):
        """Template memory usage should be reasonable (<100MB)."""
        import sys

        templates = self.registry.get_all_templates()

        # Calculate total size
        total_size = sum(sys.getsizeof(t) for t in templates)
        total_size_mb = total_size / (1024 * 1024)

        # Calculate average size per template
        avg_size_bytes = total_size / len(templates)

        print(f"\nTemplate memory usage:")
        print(f"  Total templates: {len(templates)}")
        print(f"  Total size: {total_size_mb:.2f} MB")
        print(f"  Average per template: {avg_size_bytes:.0f} bytes")
        print(f"  Target: <100 MB total")

        self.assertLess(
            total_size_mb,
            100,
            f"Template memory usage {total_size_mb:.2f}MB exceeds 100MB"
        )

    def test_entity_extractor_memory(self):
        """Entity extractor should not leak memory."""
        import sys

        # Get baseline memory
        baseline_size = sys.getsizeof(self.extractor)

        # Process many queries
        for i in range(1000):
            query = f"Query {i} with various entities Region IX Maranao fishing"
            _ = self.extractor.extract_entities(query)

        # Check memory after processing
        after_size = sys.getsizeof(self.extractor)

        print(f"\nEntity extractor memory:")
        print(f"  Baseline: {baseline_size} bytes")
        print(f"  After 1000 queries: {after_size} bytes")
        print(f"  Difference: {after_size - baseline_size} bytes")

        # Should not grow significantly
        growth_percent = ((after_size - baseline_size) / baseline_size) * 100

        self.assertLess(
            growth_percent,
            50,
            f"Entity extractor memory grew by {growth_percent:.1f}%"
        )


class ScalabilityTests(TestCase):
    """Test system scalability with increasing load."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        super().setUpClass()
        cls.extractor = EntityExtractor()
        cls.matcher = TemplateMatcher()

    def test_performance_degradation_with_load(self):
        """Performance should degrade gracefully with increased load."""
        query = "How many communities in Region IX?"

        # Test with increasing query counts
        query_counts = [10, 50, 100, 500]
        results = []

        for count in query_counts:
            timings = []

            for _ in range(count):
                start = time.time()
                entities = self.extractor.extract_entities(query)
                result = self.matcher.match_and_generate(query, entities)
                elapsed_ms = (time.time() - start) * 1000
                timings.append(elapsed_ms)

            avg_time = statistics.mean(timings)
            median_time = statistics.median(timings)

            results.append({
                'count': count,
                'avg': avg_time,
                'median': median_time,
            })

            print(f"\nLoad test ({count} queries):")
            print(f"  Average: {avg_time:.2f}ms")
            print(f"  Median: {median_time:.2f}ms")

        # Performance should not degrade significantly
        # Compare first and last
        first_avg = results[0]['avg']
        last_avg = results[-1]['avg']
        degradation = (last_avg - first_avg) / first_avg * 100

        print(f"\nPerformance degradation:")
        print(f"  First batch ({results[0]['count']} queries): {first_avg:.2f}ms")
        print(f"  Last batch ({results[-1]['count']} queries): {last_avg:.2f}ms")
        print(f"  Degradation: {degradation:.1f}%")

        self.assertLess(
            degradation,
            50,
            f"Performance degraded by {degradation:.1f}% (threshold: 50%)"
        )


# =============================================================================
# PYTEST MARKS
# =============================================================================

# Mark all tests in this module as performance tests
pytestmark = pytest.mark.performance
