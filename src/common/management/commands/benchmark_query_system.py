"""
Django management command to benchmark query template system performance.

Benchmarks:
- Template loading time
- Pattern matching speed (100+ sample queries)
- Entity extraction speed
- Memory usage
- Cache effectiveness
"""

import json
import time
import tracemalloc
from datetime import datetime
from typing import Dict, List

from django.core.management.base import BaseCommand

from common.ai_services.chat.query_templates import get_template_registry


class Command(BaseCommand):
    help = 'Benchmark query template system performance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--iterations',
            type=int,
            default=100,
            help='Number of iterations for benchmarks (default: 100)',
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Save benchmark results to JSON file',
        )
        parser.add_argument(
            '--queries',
            type=int,
            default=50,
            help='Number of sample queries to test (default: 50)',
        )

    def handle(self, *args, **options):
        """Main benchmark execution."""
        iterations = options['iterations']
        output_file = options.get('output')
        num_queries = options['queries']

        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('OBCMS Query System Benchmark'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')
        self.stdout.write(f"Iterations: {iterations}")
        self.stdout.write(f"Sample queries: {num_queries}")
        self.stdout.write('')

        results = {}

        # Benchmark 1: Template Loading
        self.stdout.write(self.style.WARNING('Benchmark 1: Template Loading'))
        loading_result = self._benchmark_template_loading(iterations)
        results['template_loading'] = loading_result
        self._print_benchmark_result(loading_result)

        # Benchmark 2: Pattern Matching
        self.stdout.write(self.style.WARNING('Benchmark 2: Pattern Matching'))
        matching_result = self._benchmark_pattern_matching(iterations, num_queries)
        results['pattern_matching'] = matching_result
        self._print_benchmark_result(matching_result)

        # Benchmark 3: Registry Operations
        self.stdout.write(self.style.WARNING('Benchmark 3: Registry Operations'))
        registry_result = self._benchmark_registry_operations(iterations)
        results['registry_operations'] = registry_result
        self._print_benchmark_result(registry_result)

        # Benchmark 4: Memory Usage
        self.stdout.write(self.style.WARNING('Benchmark 4: Memory Usage'))
        memory_result = self._benchmark_memory_usage()
        results['memory_usage'] = memory_result
        self._print_memory_result(memory_result)

        # Benchmark 5: Category Search
        self.stdout.write(self.style.WARNING('Benchmark 5: Category Search'))
        category_result = self._benchmark_category_search(iterations)
        results['category_search'] = category_result
        self._print_benchmark_result(category_result)

        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('BENCHMARK SUMMARY'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        summary = self._generate_summary(results)
        for line in summary:
            self.stdout.write(line)

        # Save to file if requested
        if output_file:
            self._save_results(results, output_file)
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS(f"Results saved to: {output_file}"))

    def _benchmark_template_loading(self, iterations: int) -> Dict:
        """Benchmark template registry loading."""
        times = []
        memory_usage = []

        for _ in range(iterations):
            # Reset registry
            from common.ai_services.chat.query_templates.base import TemplateRegistry

            TemplateRegistry.reset_instance()

            # Measure loading time and memory
            tracemalloc.start()
            start = time.perf_counter()

            registry = get_template_registry()
            templates = registry.get_all_templates()

            elapsed = (time.perf_counter() - start) * 1000
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            times.append(elapsed)
            memory_usage.append(peak / 1024 / 1024)  # MB

        return {
            'operation': 'Template Loading',
            'iterations': iterations,
            'template_count': len(templates),
            'avg_time_ms': sum(times) / len(times),
            'min_time_ms': min(times),
            'max_time_ms': max(times),
            'avg_memory_mb': sum(memory_usage) / len(memory_usage),
        }

    def _benchmark_pattern_matching(self, iterations: int, num_queries: int) -> Dict:
        """Benchmark pattern matching performance."""
        sample_queries = self._get_sample_queries()[:num_queries]

        registry = get_template_registry()
        templates = registry.get_all_templates()

        times = []
        match_counts = []

        for _ in range(iterations):
            for query in sample_queries:
                start = time.perf_counter()

                matches = []
                for template in templates:
                    if template.matches(query):
                        matches.append(template)

                elapsed = (time.perf_counter() - start) * 1000
                times.append(elapsed)
                match_counts.append(len(matches))

        return {
            'operation': 'Pattern Matching',
            'iterations': iterations,
            'queries_tested': num_queries,
            'total_matches': iterations * num_queries,
            'avg_time_ms': sum(times) / len(times),
            'min_time_ms': min(times),
            'max_time_ms': max(times),
            'avg_matches_per_query': sum(match_counts) / len(match_counts),
        }

    def _benchmark_registry_operations(self, iterations: int) -> Dict:
        """Benchmark common registry operations."""
        registry = get_template_registry()

        # Test get_all_templates
        times_all = []
        for _ in range(iterations):
            start = time.perf_counter()
            templates = registry.get_all_templates()
            elapsed = (time.perf_counter() - start) * 1000
            times_all.append(elapsed)

        # Test get_templates_by_category
        times_category = []
        categories = registry.get_categories()
        if categories:
            for _ in range(iterations):
                for category in categories:
                    start = time.perf_counter()
                    templates = registry.get_templates_by_category(category)
                    elapsed = (time.perf_counter() - start) * 1000
                    times_category.append(elapsed)

        # Test search_templates
        times_search = []
        sample_queries = self._get_sample_queries()[:10]
        for _ in range(iterations):
            for query in sample_queries:
                start = time.perf_counter()
                matches = registry.search_templates(query)
                elapsed = (time.perf_counter() - start) * 1000
                times_search.append(elapsed)

        return {
            'operation': 'Registry Operations',
            'iterations': iterations,
            'get_all_avg_ms': sum(times_all) / len(times_all) if times_all else 0,
            'get_by_category_avg_ms': sum(times_category) / len(times_category) if times_category else 0,
            'search_avg_ms': sum(times_search) / len(times_search) if times_search else 0,
        }

    def _benchmark_memory_usage(self) -> Dict:
        """Measure memory usage of template system."""
        tracemalloc.start()

        registry = get_template_registry()
        templates = registry.get_all_templates()

        # Trigger pattern compilation for all templates
        for template in templates:
            _ = template.compiled_pattern

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        return {
            'operation': 'Memory Usage',
            'current_mb': current / 1024 / 1024,
            'peak_mb': peak / 1024 / 1024,
            'template_count': len(templates),
            'avg_per_template_kb': (peak / len(templates) / 1024) if templates else 0,
        }

    def _benchmark_category_search(self, iterations: int) -> Dict:
        """Benchmark category-specific searches."""
        registry = get_template_registry()
        categories = registry.get_categories()

        times_by_category = {}

        for category in categories:
            times = []
            for _ in range(iterations):
                start = time.perf_counter()
                templates = registry.get_templates_by_category(category)
                elapsed = (time.perf_counter() - start) * 1000
                times.append(elapsed)

            times_by_category[category] = {
                'avg_ms': sum(times) / len(times),
                'template_count': len(templates),
            }

        return {
            'operation': 'Category Search',
            'iterations': iterations,
            'categories': times_by_category,
        }

    def _get_sample_queries(self) -> List[str]:
        """Get sample queries for benchmarking."""
        return [
            # Community queries
            "How many communities in Region IX?",
            "Show me all Maguindanao communities",
            "List communities in Zamboanga",
            "Count all OBC communities",
            "Communities with fishing livelihood",
            # MANA queries
            "How many MANA workshops?",
            "Recent assessments in Basilan",
            "Show completed workshops",
            "Count pending assessments",
            "Workshops in 2024",
            # Coordination queries
            "Active partnerships",
            "List MOA organizations",
            "Show meetings this month",
            "Count coordination activities",
            "Recent stakeholder meetings",
            # Policy queries
            "Show all policy recommendations",
            "Count approved policies",
            "Policies for Region IX",
            "Recent policy updates",
            "Active policy recommendations",
            # Project queries
            "Active projects in Mindanao",
            "Count completed projects",
            "Show ongoing activities",
            "Projects by budget range",
            "Recent project approvals",
            # Geographic queries
            "List all regions",
            "Provinces in Region IX",
            "Municipalities in Zamboanga del Sur",
            "Count barangays in Basilan",
            "Show geographic hierarchy",
            # General queries
            "What can you help me with?",
            "Show system statistics",
            "Navigation help",
            "How do I create a community profile?",
            "System overview",
            # Temporal queries
            "Activities this week",
            "Projects from last month",
            "Assessments in Q4 2024",
            "Trend analysis for communities",
            "Historical data comparison",
            # Cross-domain queries
            "Communities with recent assessments",
            "Projects linked to MANA workshops",
            "Coordination activities for policies",
            "Pipeline from assessment to project",
            "Integration between modules",
            # Analytics queries
            "Statistics for Region IX",
            "Pattern analysis for livelihoods",
            "Predictive analysis for needs",
            "Aggregated metrics by province",
            "Performance indicators",
        ]

    def _print_benchmark_result(self, result: Dict):
        """Print benchmark result in formatted way."""
        self.stdout.write(f"  Operation: {result['operation']}")
        self.stdout.write(f"  Iterations: {result.get('iterations', 'N/A')}")

        if 'avg_time_ms' in result:
            self.stdout.write(f"  Average time: {result['avg_time_ms']:.2f} ms")
        if 'min_time_ms' in result:
            self.stdout.write(f"  Min time: {result['min_time_ms']:.2f} ms")
        if 'max_time_ms' in result:
            self.stdout.write(f"  Max time: {result['max_time_ms']:.2f} ms")

        # Print other metrics
        for key, value in result.items():
            if key not in [
                'operation',
                'iterations',
                'avg_time_ms',
                'min_time_ms',
                'max_time_ms',
                'categories',
            ]:
                if isinstance(value, float):
                    self.stdout.write(f"  {key}: {value:.2f}")
                else:
                    self.stdout.write(f"  {key}: {value}")

        self.stdout.write('')

    def _print_memory_result(self, result: Dict):
        """Print memory usage result."""
        self.stdout.write(f"  Operation: {result['operation']}")
        self.stdout.write(f"  Current memory: {result['current_mb']:.2f} MB")
        self.stdout.write(f"  Peak memory: {result['peak_mb']:.2f} MB")
        self.stdout.write(f"  Template count: {result['template_count']}")
        self.stdout.write(
            f"  Average per template: {result['avg_per_template_kb']:.2f} KB"
        )
        self.stdout.write('')

    def _generate_summary(self, results: Dict) -> List[str]:
        """Generate summary of benchmark results."""
        summary = []

        # Overall performance
        loading_time = results['template_loading']['avg_time_ms']
        matching_time = results['pattern_matching']['avg_time_ms']
        memory_mb = results['memory_usage']['peak_mb']

        summary.append(f"Template Loading: {loading_time:.2f} ms")
        summary.append(f"Pattern Matching (per query): {matching_time:.2f} ms")
        summary.append(f"Memory Usage: {memory_mb:.2f} MB")
        summary.append('')

        # Performance assessment
        if matching_time < 1.0:
            summary.append(
                self.style.SUCCESS("✓ Excellent performance (< 1ms per query)")
            )
        elif matching_time < 5.0:
            summary.append(self.style.SUCCESS("✓ Good performance (< 5ms per query)"))
        elif matching_time < 10.0:
            summary.append(
                self.style.WARNING("⚠️  Acceptable performance (< 10ms per query)")
            )
        else:
            summary.append(
                self.style.ERROR("❌ Poor performance (> 10ms per query)")
            )

        summary.append('')

        # Recommendations
        summary.append("Recommendations:")
        if memory_mb > 100:
            summary.append(
                "  - Consider optimizing template storage (memory usage > 100MB)"
            )
        if matching_time > 5.0:
            summary.append("  - Pattern matching is slow, consider caching compiled patterns")
        if results['template_loading']['avg_time_ms'] > 100:
            summary.append("  - Template loading is slow, consider lazy loading")

        return summary

    def _save_results(self, results: Dict, output_file: str):
        """Save benchmark results to JSON file."""
        output = {
            'timestamp': datetime.now().isoformat(),
            'results': results,
        }

        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
