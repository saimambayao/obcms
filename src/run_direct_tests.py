#!/usr/bin/env python
"""
Direct test runner for OBCMS component testing.
Runs tests directly without pytest configuration.
"""

import os
import sys
import django

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.base')

# Setup Django
django.setup()

def test_organizations_models():
    """Test organization models directly."""
    from organizations.models import Organization, OrganizationMembership
    from django.contrib.auth import get_user_model
    from django.db import IntegrityError

    User = get_user_model()

    print("Testing Organization Models...")

    # Test 1: Create organization
    try:
        org = Organization.objects.create(
            code='TEST1',
            name='Test Organization 1',
            org_type='office',
            is_active=True,
        )
        print(f"✅ Organization created: {org}")
        assert org.code == 'TEST1'
        assert org.name == 'Test Organization 1'
        assert org.org_type == 'office'
    except Exception as e:
        print(f"❌ Organization creation failed: {e}")
        return False

    # Test 2: Test unique constraint
    try:
        Organization.objects.create(
            code='TEST1',
            name='Duplicate Organization',
            org_type='office',
        )
        print("❌ Unique constraint test failed - duplicate allowed")
        return False
    except IntegrityError:
        print("✅ Unique constraint working correctly")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

    # Test 3: Create user and membership
    try:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )

        membership = OrganizationMembership.objects.create(
            user=user,
            organization=org,
            role='staff',
            is_primary=True,
        )
        print(f"✅ Membership created: {membership}")
        assert membership.user == user
        assert membership.organization == org
        assert membership.role == 'staff'
    except Exception as e:
        print(f"❌ Membership creation failed: {e}")
        return False

    print("✅ Organization model tests passed!")
    return True

def test_ai_services():
    """Test AI services functionality."""
    try:
        from ai_assistant.services.embedding_service import EmbeddingService
        from ai_assistant.services.similarity_search import SimilaritySearchService

        print("Testing AI Services...")

        # Test embedding service initialization
        embedding_service = EmbeddingService()
        print("✅ EmbeddingService initialized")

        # Test similarity search initialization
        similarity_search = SimilaritySearchService()
        print("✅ SimilaritySearchService initialized")

        print("✅ AI services tests passed!")
        return True

    except Exception as e:
        print(f"❌ AI services test failed: {e}")
        return False

def test_common_services():
    """Test common services."""
    try:
        from common.ai_services.unified_search import UnifiedSearchEngine

        print("Testing Common Services...")

        # Test unified search initialization
        unified_search = UnifiedSearchEngine()
        print("✅ UnifiedSearchEngine initialized")

        print("✅ Common services tests passed!")
        return True

    except Exception as e:
        print(f"❌ Common services test failed: {e}")
        return False

def test_database_connection():
    """Test database connection and basic operations."""
    try:
        from django.db import connection

        print("Testing Database Connection...")

        # Test basic query
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1

        print("✅ Database connection working")
        return True

    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def test_django_configuration():
    """Test Django configuration."""
    try:
        from django.conf import settings
        from django.contrib.auth import get_user_model

        print("Testing Django Configuration...")

        # Test that Django is properly configured
        assert settings.configured
        print("✅ Django configured")

        # Test that user model is available
        User = get_user_model()
        print(f"✅ User model available: {User.__name__}")

        # Test that apps are loaded
        from django.apps import apps
        all_apps = [app.name for app in apps.get_app_configs()]
        print(f"✅ {len(all_apps)} apps loaded")

        return True

    except Exception as e:
        print(f"❌ Django configuration test failed: {e}")
        return False

def main():
    """Run all component tests."""
    print("=" * 60)
    print("OBCMS COMPONENT TESTS")
    print("=" * 60)

    tests = [
        ("Django Configuration", test_django_configuration),
        ("Database Connection", test_database_connection),
        ("Organization Models", test_organizations_models),
        ("AI Services", test_ai_services),
        ("Common Services", test_common_services),
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
    print("TEST SUMMARY")
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
        print("🎉 ALL COMPONENT TESTS PASSED!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())