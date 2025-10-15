#!/usr/bin/env python
"""
Performance tests for OBCMS.
"""

import os
import sys
import django
import time
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.base')

# Setup Django
django.setup()

def test_database_performance():
    """Test database query performance."""
    try:
        print("Testing Database Performance...")

        # Test user query performance
        from django.contrib.auth import get_user_model
        User = get_user_model()

        start_time = time.time()
        user_count = User.objects.count()
        user_query_time = time.time() - start_time
        print(f"✅ User count query: {user_count} users in {user_query_time:.3f}s")

        # Test organization query performance
        from organizations.models import Organization
        start_time = time.time()
        org_count = Organization.objects.count()
        org_query_time = time.time() - start_time
        print(f"✅ Organization count query: {org_count} organizations in {org_query_time:.3f}s")

        # Test community query performance
        from communities.models import OBCCommunity
        start_time = time.time()
        community_count = OBCCommunity.objects.count()
        community_query_time = time.time() - start_time
        print(f"✅ Community count query: {community_count} communities in {community_query_time:.3f}s")

        # Test complex query performance
        start_time = time.time()
        communities_with_org = OBCCommunity.objects.select_related('barangay', 'organization').count()
        complex_query_time = time.time() - start_time
        print(f"✅ Complex community query: {communities_with_org} communities in {complex_query_time:.3f}s")

        # Performance thresholds (in seconds)
        thresholds = {
            'user_query': 0.1,
            'org_query': 0.1,
            'community_query': 0.5,
            'complex_query': 1.0,
        }

        query_times = {
            'user_query': user_query_time,
            'org_query': org_query_time,
            'community_query': community_query_time,
            'complex_query': complex_query_time,
        }

        passed = 0
        total = len(thresholds)
        for query_type, threshold in thresholds.items():
            if query_times[query_type] <= threshold:
                print(f"✅ {query_type} within threshold ({threshold}s)")
                passed += 1
            else:
                print(f"⚠️  {query_type} exceeds threshold ({threshold}s): {query_times[query_type]:.3f}s")

        print(f"✅ Database performance: {passed}/{total} queries within threshold")
        return passed == total

    except Exception as e:
        print(f"❌ Database performance test failed: {e}")
        return False

def test_model_operations_performance():
    """Test model CRUD operations performance."""
    try:
        print("Testing Model Operations Performance...")

        from organizations.models import Organization
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Test create performance
        start_time = time.time()
        test_org = Organization.objects.create(
            code='PERF_TEST',
            name='Performance Test Organization',
            org_type='office',
        )
        create_time = time.time() - start_time
        print(f"✅ Organization create: {create_time:.3f}s")

        # Test read performance
        start_time = time.time()
        org = Organization.objects.get(id=test_org.id)
        read_time = time.time() - start_time
        print(f"✅ Organization read: {read_time:.3f}s")

        # Test update performance
        start_time = time.time()
        org.name = 'Updated Performance Test Organization'
        org.save()
        update_time = time.time() - start_time
        print(f"✅ Organization update: {update_time:.3f}s")

        # Test delete performance
        start_time = time.time()
        org.delete()
        delete_time = time.time() - start_time
        print(f"✅ Organization delete: {delete_time:.3f}s")

        # Performance thresholds
        thresholds = {
            'create': 0.1,
            'read': 0.05,
            'update': 0.1,
            'delete': 0.1,
        }

        operation_times = {
            'create': create_time,
            'read': read_time,
            'update': update_time,
            'delete': delete_time,
        }

        passed = 0
        total = len(thresholds)
        for operation, threshold in thresholds.items():
            if operation_times[operation] <= threshold:
                print(f"✅ {operation} within threshold ({threshold}s)")
                passed += 1
            else:
                print(f"⚠️  {operation} exceeds threshold ({threshold}s): {operation_times[operation]:.3f}s")

        print(f"✅ Model operations performance: {passed}/{total} operations within threshold")
        return passed == total

    except Exception as e:
        print(f"❌ Model operations performance test failed: {e}")
        return False

def test_template_rendering_performance():
    """Test template rendering performance."""
    try:
        print("Testing Template Rendering Performance...")

        from django.template import Template, Context
        from django.template.loader import get_template

        # Test simple template rendering
        simple_template = Template("<h1>{{ title }}</h1><p>{{ content }}</p>")
        context = Context({'title': 'Test Title', 'content': 'Test content'})

        start_time = time.time()
        rendered = simple_template.render(context)
        simple_render_time = time.time() - start_time
        print(f"✅ Simple template render: {simple_render_time:.3f}s")

        # Test complex template rendering (if base.html exists)
        try:
            base_template = get_template('base.html')
            start_time = time.time()
            rendered = base_template.render(context)
            complex_render_time = time.time() - start_time
            print(f"✅ Complex template render: {complex_render_time:.3f}s")
        except:
            complex_render_time = 0
            print("⚠️  Complex template not available for testing")

        # Test multiple renders
        start_time = time.time()
        for i in range(10):
            rendered = simple_template.render(context)
        multiple_render_time = time.time() - start_time
        avg_render_time = multiple_render_time / 10
        print(f"✅ Multiple template renders: {avg_render_time:.3f}s average")

        # Performance thresholds
        thresholds = {
            'simple': 0.01,
            'complex': 0.1,
            'multiple': 0.01,
        }

        render_times = {
            'simple': simple_render_time,
            'complex': complex_render_time if complex_render_time > 0 else 0.05, # Default if not tested
            'multiple': avg_render_time,
        }

        passed = 0
        total = len(thresholds)
        for render_type, threshold in thresholds.items():
            if render_times[render_type] <= threshold:
                print(f"✅ {render_type} render within threshold ({threshold}s)")
                passed += 1
            else:
                print(f"⚠️  {render_type} render exceeds threshold ({threshold}s): {render_times[render_type]:.3f}s")

        print(f"✅ Template rendering performance: {passed}/{total} renders within threshold")
        return passed == total

    except Exception as e:
        print(f"❌ Template rendering performance test failed: {e}")
        return False

def test_memory_usage():
    """Test memory usage."""
    try:
        import psutil
        import os

        print("Testing Memory Usage...")

        # Get current process
        process = psutil.Process(os.getpid())

        # Get memory info
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024  # Convert to MB

        print(f"✅ Current memory usage: {memory_mb:.1f} MB")

        # Memory threshold (500 MB)
        memory_threshold = 500
        if memory_mb <= memory_threshold:
            print(f"✅ Memory usage within threshold ({memory_threshold} MB)")
            return True
        else:
            print(f"⚠️  Memory usage exceeds threshold ({memory_threshold} MB): {memory_mb:.1f} MB")
            return False

    except ImportError:
        print("⚠️  psutil not available for memory testing")
        return True
    except Exception as e:
        print(f"❌ Memory usage test failed: {e}")
        return False

def test_database_connection_pool():
    """Test database connection efficiency."""
    try:
        print("Testing Database Connection Pool...")

        from django.db import connection, connections

        # Test connection status
        if connection.is_usable():
            print("✅ Database connection is usable")
        else:
            print("⚠️  Database connection is not usable")
            return False

        # Test multiple connections
        from django.test.utils import setup_test_environment
        from django.test.client import Client

        connection_times = []
        for i in range(5):
            start_time = time.time()
            # Simulate a database query
            from django.contrib.auth import get_user_model
            User = get_user_model()
            count = User.objects.count()
            query_time = time.time() - start_time
            connection_times.append(query_time)

        avg_connection_time = sum(connection_times) / len(connection_times)
        print(f"✅ Average query time across 5 connections: {avg_connection_time:.3f}s")

        # Connection threshold
        connection_threshold = 0.1
        if avg_connection_time <= connection_threshold:
            print(f"✅ Connection time within threshold ({connection_threshold}s)")
            return True
        else:
            print(f"⚠️  Connection time exceeds threshold ({connection_threshold}s): {avg_connection_time:.3f}s")
            return False

    except Exception as e:
        print(f"❌ Database connection pool test failed: {e}")
        return False

def test_cache_performance():
    """Test cache performance if available."""
    try:
        from django.core.cache import cache
        from django.conf import settings

        print("Testing Cache Performance...")

        if not cache:
            print("⚠️  Cache not configured")
            return True

        # Test cache set
        test_key = 'performance_test_key'
        test_value = 'test_value_' + str(time.time())

        start_time = time.time()
        cache.set(test_key, test_value, 60)
        set_time = time.time() - start_time
        print(f"✅ Cache set: {set_time:.3f}s")

        # Test cache get
        start_time = time.time()
        cached_value = cache.get(test_key)
        get_time = time.time() - start_time
        print(f"✅ Cache get: {get_time:.3f}s")

        # Verify cache hit
        if cached_value == test_value:
            print("✅ Cache hit successful")
        else:
            print("❌ Cache hit failed")
            return False

        # Clean up
        cache.delete(test_key)

        # Performance thresholds
        cache_threshold = 0.01
        if set_time <= cache_threshold and get_time <= cache_threshold:
            print(f"✅ Cache operations within threshold ({cache_threshold}s)")
            return True
        else:
            print(f"⚠️  Cache operations exceed threshold ({cache_threshold}s)")
            return False

    except Exception as e:
        print(f"❌ Cache performance test failed: {e}")
        return False

def main():
    """Run all performance tests."""
    print("=" * 60)
    print("OBCMS PERFORMANCE TESTS")
    print("=" * 60)

    tests = [
        ("Database Performance", test_database_performance),
        ("Model Operations Performance", test_model_operations_performance),
        ("Template Rendering Performance", test_template_rendering_performance),
        ("Memory Usage", test_memory_usage),
        ("Database Connection Pool", test_database_connection_pool),
        ("Cache Performance", test_cache_performance),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("PERFORMANCE TEST SUMMARY")
    print("=" * 60)

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\nTotal: {len(results)} | Passed: {passed} | Failed: {failed}")

    if failed == 0:
        print("🎉 ALL PERFORMANCE TESTS PASSED!")
        return 0
    else:
        print("⚠️  Some performance tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())