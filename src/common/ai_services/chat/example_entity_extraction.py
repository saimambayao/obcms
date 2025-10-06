#!/usr/bin/env python
"""
Example usage of the Entity Extractor service.

This script demonstrates how to use the EntityExtractor to extract
structured entities from natural language queries.

Usage:
    python example_entity_extraction.py
"""

import os
import sys
import django

# Setup Django environment
# Add the src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, src_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings')
django.setup()

from common.ai_services.chat.entity_extractor import EntityExtractor
import time


def print_separator(char='=', length=70):
    """Print a separator line."""
    print(char * length)


def print_entity_details(entities):
    """Print detailed information about extracted entities."""
    if not entities:
        print("  ❌ No entities extracted")
        return

    for entity_type, entity_data in entities.items():
        if isinstance(entity_data, dict):
            value = entity_data.get('value', 'N/A')
            confidence = entity_data.get('confidence', 0)
            print(f"  ✓ {entity_type}: {value} (confidence: {confidence:.2f})")
        elif isinstance(entity_data, list):
            for item in entity_data:
                value = item.get('value', 'N/A')
                confidence = item.get('confidence', 0)
                print(f"  ✓ {entity_type}: {value} (confidence: {confidence:.2f})")


def example_1_basic_extraction():
    """Example 1: Basic multi-entity extraction."""
    print_separator()
    print("EXAMPLE 1: Basic Multi-Entity Extraction")
    print_separator()
    print()

    extractor = EntityExtractor()

    query = "maranao fishing communities in zamboanga last 6 months"
    print(f"Query: \"{query}\"")
    print()

    start = time.perf_counter()
    entities = extractor.extract_entities(query)
    duration = (time.perf_counter() - start) * 1000

    print(f"Extraction time: {duration:.2f}ms")
    print(f"Entities extracted: {len(entities)}")
    print()
    print("Details:")
    print_entity_details(entities)
    print()


def example_2_entity_summary():
    """Example 2: Generate human-readable summary."""
    print_separator()
    print("EXAMPLE 2: Human-Readable Summary")
    print_separator()
    print()

    extractor = EntityExtractor()

    queries = [
        "top 10 maguindanao farmers in sultan kudarat",
        "ongoing workshops in region xii this year",
        "recent tausug communities in zamboanga del sur",
    ]

    for query in queries:
        entities = extractor.extract_entities(query)
        summary = extractor.get_entity_summary(entities)

        print(f"Query: \"{query}\"")
        print(f"Summary: {summary}")
        print()


def example_3_validation():
    """Example 3: Entity validation."""
    print_separator()
    print("EXAMPLE 3: Entity Validation")
    print_separator()
    print()

    extractor = EntityExtractor()

    query = "maranao fishing communities in zamboanga"
    print(f"Query: \"{query}\"")
    print()

    entities = extractor.extract_entities(query)
    is_valid, issues = extractor.validate_entities(entities)

    print(f"Valid: {is_valid}")
    print(f"Issues: {issues if issues else 'None'}")
    print()

    if is_valid:
        print("✅ All entities are valid and consistent")
    else:
        print("❌ Validation issues detected:")
        for issue in issues:
            print(f"  - {issue}")
    print()


def example_4_individual_resolvers():
    """Example 4: Using individual resolvers."""
    print_separator()
    print("EXAMPLE 4: Individual Resolvers")
    print_separator()
    print()

    from common.ai_services.chat.entity_resolvers import (
        LocationResolver,
        EthnicGroupResolver,
        LivelihoodResolver,
        DateRangeResolver,
    )

    print("Location Resolver:")
    lr = LocationResolver()
    result = lr.resolve("zamboanga peninsula")
    print(f"  'zamboanga peninsula' → {result}")
    print()

    print("Ethnic Group Resolver:")
    egr = EthnicGroupResolver()
    result = egr.resolve("maranao communities")
    print(f"  'maranao communities' → {result}")
    print()

    print("Livelihood Resolver:")
    lvr = LivelihoodResolver()
    result = lvr.resolve("fishing communities")
    print(f"  'fishing communities' → {result}")
    print()

    print("Date Range Resolver:")
    drr = DateRangeResolver()
    result = drr.resolve("last 6 months")
    print(f"  'last 6 months' → range_type: {result.get('range_type')}")
    print()


def example_5_fuzzy_matching():
    """Example 5: Fuzzy matching with typos."""
    print_separator()
    print("EXAMPLE 5: Fuzzy Matching (Typos)")
    print_separator()
    print()

    extractor = EntityExtractor()

    queries_with_typos = [
        ("marano fishermen zambanga", "Typos in ethnic group and location"),
        ("tausog weaving", "Typo in ethnic group"),
        ("fising communities region 9", "Typo in livelihood"),
    ]

    for query, description in queries_with_typos:
        print(f"{description}:")
        print(f"  Query: \"{query}\"")

        entities = extractor.extract_entities(query)
        if entities:
            print(f"  Extracted: {list(entities.keys())}")
            print_entity_details(entities)
        else:
            print("  No entities extracted")
        print()


def example_6_performance_benchmark():
    """Example 6: Performance benchmark."""
    print_separator()
    print("EXAMPLE 6: Performance Benchmark")
    print_separator()
    print()

    extractor = EntityExtractor()

    test_queries = [
        "maranao fishing communities zamboanga",
        "top 5 maguindanao farmers sultan kudarat",
        "ongoing workshops region xii this year",
        "recent tausug communities",
        "completed assessments from jan to mar 2024",
        "yakan weaving communities zamboanga del sur",
        "10 farming communities region x",
        "badjao fishing in zamboanga sibugay",
    ]

    print(f"Testing {len(test_queries)} queries...")
    print()

    times = []
    for i, query in enumerate(test_queries, 1):
        start = time.perf_counter()
        entities = extractor.extract_entities(query)
        duration = (time.perf_counter() - start) * 1000
        times.append(duration)

        print(f"{i}. \"{query[:50]}...\" → {duration:.2f}ms ({len(entities)} entities)")

    print()
    avg_time = sum(times) / len(times)
    max_time = max(times)
    min_time = min(times)

    print(f"Average time: {avg_time:.2f}ms")
    print(f"Min time: {min_time:.2f}ms")
    print(f"Max time: {max_time:.2f}ms")
    print(f"Target: <20ms")
    print()

    if avg_time < 20:
        print("✅ PASS - Performance meets target!")
    else:
        print("❌ FAIL - Performance below target")
    print()


def main():
    """Run all examples."""
    print()
    print_separator('█')
    print("ENTITY EXTRACTOR - USAGE EXAMPLES")
    print_separator('█')
    print()

    try:
        example_1_basic_extraction()
        example_2_entity_summary()
        example_3_validation()
        example_4_individual_resolvers()
        example_5_fuzzy_matching()
        example_6_performance_benchmark()

        print_separator('█')
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print_separator('█')
        print()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
