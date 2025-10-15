#!/usr/bin/env python
"""
Simplified BMMS Performance Testing Suite

Tests OBCMS/BMMS system performance for 44 BARMM Ministries, Offices, and Agencies (MOAs).
This version doesn't require additional dependencies.
"""

import os
import sys
import time
import json
import statistics
import threading
import concurrent.futures
import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.base')

import django
django.setup()

# Import BMMS models
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.test.client import Client
from django.db import connection, connections
from django.db.models import Count, Sum, Avg
from django.core.cache import cache

User = get_user_model()


def run_performance_tests():
    """Run simplified performance tests."""
    print("=" * 80)
    print("🚀 SIMPLIFIED BMMS PERFORMANCE TESTING SUITE")
    print("Bangsamoro Ministerial Management System")
    print("Testing for 44 MOAs production readiness")
    print("=" * 80)

    metrics = []

    # Test 1: Database Query Performance
    print("\n📊 Testing Database Query Performance...")

    # Test user query
    start_time = time.time()
    user_count = User.objects.count()
    user_query_time = time.time() - start_time

    metric = {
        "operation": "Database: User Count Query",
        "target_time": 0.1,
        "actual_time": user_query_time,
        "passed": user_query_time <= 0.1,
        "details": {"user_count": user_count}
    }
    metrics.append(metric)

    status = "✅" if metric["passed"] else "❌"
    print(f"   {status} User Count Query: {user_query_time:.3f}s (target: 0.1s)")

    # Test organization query
    try:
        from organizations.models import Organization

        start_time = time.time()
        org_count = Organization.objects.count()
        org_query_time = time.time() - start_time

        metric = {
            "operation": "Database: Organization Count Query",
            "target_time": 0.1,
            "actual_time": org_query_time,
            "passed": org_query_time <= 0.1,
            "details": {"org_count": org_count}
        }
        metrics.append(metric)

        status = "✅" if metric["passed"] else "❌"
        print(f"   {status} Organization Count Query: {org_query_time:.3f}s (target: 0.1s)")

    except Exception as e:
        print(f"   ❌ Organization Query: Error - {str(e)}")
        metric = {
            "operation": "Database: Organization Count Query",
            "target_time": 0.1,
            "actual_time": 999.0,
            "passed": False,
            "details": {"error": str(e)}
        }
        metrics.append(metric)

    # Test community query
    try:
        from communities.models import OBCCommunity

        start_time = time.time()
        community_count = OBCCommunity.objects.count()
        community_query_time = time.time() - start_time

        metric = {
            "operation": "Database: Community Count Query",
            "target_time": 0.1,
            "actual_time": community_query_time,
            "passed": community_query_time <= 0.1,
            "details": {"community_count": community_count}
        }
        metrics.append(metric)

        status = "✅" if metric["passed"] else "❌"
        print(f"   {status} Community Count Query: {community_query_time:.3f}s (target: 0.1s)")

    except Exception as e:
        print(f"   ❌ Community Query: Error - {str(e)}")
        metric = {
            "operation": "Database: Community Count Query",
            "target_time": 0.1,
            "actual_time": 999.0,
            "passed": False,
            "details": {"error": str(e)}
        }
        metrics.append(metric)

    # Test 2: Complex Query Performance
    print("\n🔍 Testing Complex Query Performance...")

    try:
        from communities.models import OBCCommunity
        from organizations.models import Organization

        start_time = time.time()
        communities_with_org = OBCCommunity.objects.select_related('organization').count()
        complex_query_time = time.time() - start_time

        metric = {
            "operation": "Database: Complex Community Query",
            "target_time": 0.2,
            "actual_time": complex_query_time,
            "passed": complex_query_time <= 0.2,
            "details": {"communities_with_org": communities_with_org}
        }
        metrics.append(metric)

        status = "✅" if metric["passed"] else "❌"
        print(f"   {status} Complex Community Query: {complex_query_time:.3f}s (target: 0.2s)")

    except Exception as e:
        print(f"   ❌ Complex Query: Error - {str(e)}")
        metric = {
            "operation": "Database: Complex Community Query",
            "target_time": 0.2,
            "actual_time": 999.0,
            "passed": False,
            "details": {"error": str(e)}
        }
        metrics.append(metric)

    # Test 3: Database Connection Pool
    print("\n🔗 Testing Database Connection Pool...")

    def database_operation():
        start_time = time.time()
        User.objects.count()
        return time.time() - start_time

    # Test with 10 concurrent connections
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(database_operation) for _ in range(20)]
        times = [f.result() for f in concurrent.futures.as_completed(futures)]

    avg_time = statistics.mean(times)
    max_time = max(times)

    metric = {
        "operation": "Database: Connection Pool (10 threads)",
        "target_time": 0.15,
        "actual_time": avg_time,
        "passed": avg_time <= 0.15,
        "details": {
            "thread_count": 10,
            "max_time": max_time,
            "operations": len(times)
        }
    }
    metrics.append(metric)

    status = "✅" if metric["passed"] else "❌"
    print(f"   {status} Connection Pool (10 threads): avg {avg_time:.3f}s, max {max_time:.3f}s")

    # Test 4: API Performance
    print("\n🌐 Testing API Performance...")

    # Create test user for API testing
    try:
        test_user = User.objects.create_user(
            username='perf_test_user',
            email='perf_test@example.com',
            password='test123456',
            first_name='Performance',
            last_name='Test User'
        )
    except Exception:
        test_user = User.objects.filter(username='perf_test_user').first()

    client = Client()
    client.force_login(test_user)

    # Test dashboard page
    start_time = time.time()
    response = client.get('/dashboard/')
    dashboard_time = time.time() - start_time

    metric = {
        "operation": "Frontend: Dashboard Page Load",
        "target_time": 2.0,
        "actual_time": dashboard_time,
        "passed": dashboard_time <= 2.0,
        "details": {
            "status_code": response.status_code,
            "response_size": len(response.content) if hasattr(response, 'content') else 0
        }
    }
    metrics.append(metric)

    status = "✅" if metric["passed"] else "❌"
    print(f"   {status} Dashboard Page Load: {dashboard_time:.3f}s (target: 2.0s)")

    # Test 5: Cache Performance
    print("\n💾 Testing Cache Performance...")

    try:
        # Test cache set
        test_key = 'performance_test_key'
        test_value = f'test_value_{int(time.time())}'

        start_time = time.time()
        cache.set(test_key, test_value, 60)
        set_time = time.time() - start_time

        # Test cache get
        start_time = time.time()
        cached_value = cache.get(test_key)
        get_time = time.time() - start_time

        total_time = set_time + get_time

        metric = {
            "operation": "Cache: Set and Get Operations",
            "target_time": 0.02,
            "actual_time": total_time,
            "passed": total_time <= 0.02,
            "details": {
                "set_time": set_time,
                "get_time": get_time,
                "cache_hit": cached_value == test_value
            }
        }
        metrics.append(metric)

        status = "✅" if metric["passed"] else "❌"
        print(f"   {status} Cache Operations: {total_time:.3f}s (set: {set_time:.3f}s, get: {get_time:.3f}s)")

        # Clean up
        cache.delete(test_key)

    except Exception as e:
        print(f"   ❌ Cache Test: Error - {str(e)}")
        metric = {
            "operation": "Cache: Set and Get Operations",
            "target_time": 0.02,
            "actual_time": 999.0,
            "passed": False,
            "details": {"error": str(e)}
        }
        metrics.append(metric)

    # Test 6: Concurrent User Simulation
    print("\n👥 Testing Concurrent User Simulation...")

    def simulate_user_activity():
        """Simulate basic user activity."""
        client = Client()
        client.force_login(test_user)

        start_time = time.time()
        try:
            response = client.get('/dashboard/')
            actual_time = time.time() - start_time
            return actual_time, response.status_code == 200
        except Exception:
            return time.time() - start_time, False

    # Test with 25 concurrent users
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        futures = [executor.submit(simulate_user_activity) for _ in range(50)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    times = [r[0] for r in results]
    success_count = sum(1 for r in results if r[1])

    avg_time = statistics.mean(times)
    success_rate = success_count / len(results)

    metric = {
        "operation": "Stress: Concurrent Users (25 threads)",
        "target_time": 1.0,
        "actual_time": avg_time,
        "passed": avg_time <= 1.0 and success_rate >= 0.9,
        "details": {
            "concurrency": 25,
            "total_requests": len(results),
            "successful_requests": success_count,
            "success_rate": success_rate
        }
    }
    metrics.append(metric)

    status = "✅" if metric["passed"] else "❌"
    print(f"   {status} Concurrent Users: avg {avg_time:.3f}s, success {success_rate:.1%}")

    # Test 7: Geographic Performance
    print("\n🗺️ Testing Geographic Performance...")

    try:
        from communities.models import OBCCommunity

        # Test coordinate query
        start_time = time.time()
        communities_in_region = OBCCommunity.objects.filter(region='Region IX').count()
        geo_query_time = time.time() - start_time

        metric = {
            "operation": "Geographic: Region Query",
            "target_time": 0.1,
            "actual_time": geo_query_time,
            "passed": geo_query_time <= 0.1,
            "details": {"communities_in_region": communities_in_region}
        }
        metrics.append(metric)

        status = "✅" if metric["passed"] else "❌"
        print(f"   {status} Geographic Region Query: {geo_query_time:.3f}s (target: 0.1s)")

    except Exception as e:
        print(f"   ❌ Geographic Query: Error - {str(e)}")
        metric = {
            "operation": "Geographic: Region Query",
            "target_time": 0.1,
            "actual_time": 999.0,
            "passed": False,
            "details": {"error": str(e)}
        }
        metrics.append(metric)

    # Test 8: Model Operations Performance
    print("\n📝 Testing Model Operations Performance...")

    try:
        from organizations.models import Organization

        # Test create performance
        start_time = time.time()
        test_org = Organization.objects.create(
            code='PERF_TEST_ORG',
            name='Performance Test Organization',
            org_type='office',
        )
        create_time = time.time() - start_time

        # Test read performance
        start_time = time.time()
        org = Organization.objects.get(id=test_org.id)
        read_time = time.time() - start_time

        # Test update performance
        start_time = time.time()
        org.name = 'Updated Performance Test Organization'
        org.save()
        update_time = time.time() - start_time

        # Test delete performance
        start_time = time.time()
        org.delete()
        delete_time = time.time() - start_time

        total_time = create_time + read_time + update_time + delete_time

        metric = {
            "operation": "Database: CRUD Operations",
            "target_time": 0.3,
            "actual_time": total_time,
            "passed": total_time <= 0.3,
            "details": {
                "create_time": create_time,
                "read_time": read_time,
                "update_time": update_time,
                "delete_time": delete_time
            }
        }
        metrics.append(metric)

        status = "✅" if metric["passed"] else "❌"
        print(f"   {status} CRUD Operations: {total_time:.3f}s (create: {create_time:.3f}s, read: {read_time:.3f}s, update: {update_time:.3f}s, delete: {delete_time:.3f}s)")

    except Exception as e:
        print(f"   ❌ Model Operations: Error - {str(e)}")
        metric = {
            "operation": "Database: CRUD Operations",
            "target_time": 0.3,
            "actual_time": 999.0,
            "passed": False,
            "details": {"error": str(e)}
        }
        metrics.append(metric)

    # Generate Report
    print("\n📊 Generating Performance Report...")

    total_tests = len(metrics)
    passed_tests = sum(1 for m in metrics if m["passed"])
    failed_tests = total_tests - passed_tests
    success_rate = passed_tests / total_tests if total_tests > 0 else 0

    # Calculate statistics
    all_times = [m["actual_time"] for m in metrics if m["actual_time"] < 900]  # Exclude errors
    avg_response_time = statistics.mean(all_times) if all_times else 0
    max_response_time = max(all_times) if all_times else 0
    min_response_time = min(all_times) if all_times else 0

    # Group metrics by category
    categories = {}
    for metric in metrics:
        category = metric["operation"].split(":")[0]
        if category not in categories:
            categories[category] = []
        categories[category].append(metric)

    # Generate recommendations
    recommendations = []
    for category, cat_metrics in categories.items():
        failed = [m for m in cat_metrics if not m["passed"]]
        if failed:
            recommendations.append({
                "category": category,
                "failed_count": len(failed),
                "priority": "HIGH" if category in ["Database", "API", "Frontend"] else "MEDIUM",
                "recommendation": get_category_recommendation(category)
            })

    # Create report
    report = {
        "test_run": {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "bmms_mode": "testing",
            "python_version": sys.version,
            "django_version": django.get_version()
        },
        "performance_summary": {
            "avg_response_time": avg_response_time,
            "max_response_time": max_response_time,
            "min_response_time": min_response_time,
            "median_response_time": statistics.median(all_times) if all_times else 0
        },
        "category_performance": {},
        "detailed_metrics": metrics,
        "recommendations": recommendations
    }

    # Category performance
    for category, cat_metrics in categories.items():
        passed = sum(1 for m in cat_metrics if m["passed"])
        total = len(cat_metrics)
        cat_times = [m["actual_time"] for m in cat_metrics if m["actual_time"] < 900]
        cat_avg = statistics.mean(cat_times) if cat_times else 0

        report["category_performance"][category] = {
            "total_tests": total,
            "passed_tests": passed,
            "success_rate": passed / total,
            "avg_response_time": cat_avg
        }

    # Save report
    report_path = "/tmp/bmms_simple_performance_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"   ✅ Performance report saved to {report_path}")

    # Print summary
    print(f"\n📊 PERFORMANCE TEST SUMMARY")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {failed_tests}")
    print(f"   Success Rate: {success_rate:.1%}")
    print(f"   Avg Response Time: {avg_response_time:.3f}s")
    print(f"   Max Response Time: {max_response_time:.3f}s")
    print(f"   Min Response Time: {min_response_time:.3f}s")

    # Category breakdown
    print(f"\n📈 PERFORMANCE BY CATEGORY")
    for category, cat_metrics in categories.items():
        passed = sum(1 for m in cat_metrics if m["passed"])
        total = len(cat_metrics)
        cat_times = [m["actual_time"] for m in cat_metrics if m["actual_time"] < 900]
        cat_avg = statistics.mean(cat_times) if cat_times else 0

        print(f"   {category}: {passed}/{total} passed, avg {cat_avg:.3f}s")

    # Recommendations
    if recommendations:
        print(f"\n💡 RECOMMENDATIONS")
        for rec in recommendations:
            print(f"   {rec['category']} ({rec['priority']}): {rec['recommendation']}")

    # Overall assessment
    print(f"\n🎯 BMMS PRODUCTION READINESS ASSESSMENT")
    if success_rate >= 0.9 and avg_response_time <= 0.5:
        print("✅ EXCELLENT: System is ready for BMMS production deployment")
    elif success_rate >= 0.8 and avg_response_time <= 1.0:
        print("⚠️  GOOD: System is mostly ready, minor optimizations needed")
    elif success_rate >= 0.6 and avg_response_time <= 2.0:
        print("⚠️  ACCEPTABLE: System needs significant optimizations before production")
    else:
        print("❌ NOT READY: System requires major performance improvements")

    print(f"   Success Rate: {success_rate:.1%} (target: >90%)")
    print(f"   Avg Response Time: {avg_response_time:.3f}s (target: <0.5s)")
    print(f"   Categories Tested: {len(categories)}")

    return report


def get_category_recommendation(category):
    """Get specific recommendations for a category."""
    recommendations = {
        "Database": "Consider adding database indexes, optimizing queries, or implementing query result caching.",
        "Frontend": "Optimize template rendering, implement response caching, or reduce database queries per page.",
        "API": "Review API endpoint efficiency, implement response caching, or optimize database queries.",
        "Geographic": "Optimize spatial queries, consider geographic indexing, or implement coordinate caching.",
        "Cache": "Review cache configuration, consider using Redis for better performance, or optimize cache keys.",
        "Stress": "Scale up resources, implement connection pooling, or optimize resource usage patterns."
    }

    return recommendations.get(category, "Review and optimize the failing operations.")


if __name__ == "__main__":
    run_performance_tests()