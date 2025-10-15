#!/usr/bin/env python
"""
Basic component tests for OBCMS without heavy AI dependencies.
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
    """Test organization models."""
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

def test_geographic_models():
    """Test geographic models."""
    try:
        from common.models import Region, Province, Municipality, Barangay

        print("Testing Geographic Models...")

        # Test Region
        region = Region.objects.get(name='Region IX')
        print(f"✅ Region found: {region}")

        # Test Province
        province = Province.objects.get(region=region, name='Zamboanga del Norte')
        print(f"✅ Province found: {province}")

        # Test Municipality
        municipality = Municipality.objects.get(province=province, name='Dapitan City')
        print(f"✅ Municipality found: {municipality}")

        # Test Barangay
        barangay = Barangay.objects.get(municipality=municipality, name='Barangay 1')
        print(f"✅ Barangay found: {barangay}")

        print("✅ Geographic model tests passed!")
        return True

    except Exception as e:
        print(f"❌ Geographic model test failed: {e}")
        return False

def test_common_models():
    """Test common models."""
    try:
        from common.models import StaffTask, WorkItem, User

        print("Testing Common Models...")

        # Test User model
        user_count = User.objects.count()
        print(f"✅ User model accessible ({user_count} users)")

        # Test StaffTask model
        task_count = StaffTask.objects.count()
        print(f"✅ StaffTask model accessible ({task_count} tasks)")

        # Test WorkItem model
        workitem_count = WorkItem.objects.count()
        print(f"✅ WorkItem model accessible ({workitem_count} work items)")

        print("✅ Common model tests passed!")
        return True

    except Exception as e:
        print(f"❌ Common model test failed: {e}")
        return False

def test_communities_models():
    """Test communities models."""
    try:
        from communities.models import OBCCommunity, MunicipalityCoverage

        print("Testing Communities Models...")

        # Test MunicipalityCoverage
        coverage_count = MunicipalityCoverage.objects.count()
        print(f"✅ MunicipalityCoverage model accessible ({coverage_count} coverages)")

        # Test OBCCommunity
        community_count = OBCCommunity.objects.count()
        print(f"✅ OBCCommunity model accessible ({community_count} communities)")

        print("✅ Communities model tests passed!")
        return True

    except Exception as e:
        print(f"❌ Communities model test failed: {e}")
        return False

def test_coordination_models():
    """Test coordination models."""
    try:
        from coordination.models import Organization, Event, Partnership

        print("Testing Coordination Models...")

        # Test Organization
        org_count = Organization.objects.count()
        print(f"✅ Coordination Organization model accessible ({org_count} organizations)")

        # Test Event
        event_count = Event.objects.count()
        print(f"✅ Event model accessible ({event_count} events)")

        # Test Partnership
        partnership_count = Partnership.objects.count()
        print(f"✅ Partnership model accessible ({partnership_count} partnerships)")

        print("✅ Coordination model tests passed!")
        return True

    except Exception as e:
        print(f"❌ Coordination model test failed: {e}")
        return False

def test_mana_models():
    """Test MANA models."""
    try:
        from mana.models import WorkshopActivity, Assessment, Need

        print("Testing MANA Models...")

        # Test WorkshopActivity
        workshop_count = WorkshopActivity.objects.count()
        print(f"✅ WorkshopActivity model accessible ({workshop_count} workshops)")

        # Test Assessment
        assessment_count = Assessment.objects.count()
        print(f"✅ Assessment model accessible ({assessment_count} assessments)")

        # Test Need
        need_count = Need.objects.count()
        print(f"✅ Need model accessible ({need_count} needs)")

        print("✅ MANA model tests passed!")
        return True

    except Exception as e:
        print(f"❌ MANA model test failed: {e}")
        return False

def test_monitoring_models():
    """Test monitoring models."""
    try:
        from monitoring.models import MonitoringEntry, StrategicPlan

        print("Testing Monitoring Models...")

        # Test MonitoringEntry
        entry_count = MonitoringEntry.objects.count()
        print(f"✅ MonitoringEntry model accessible ({entry_count} entries)")

        # Test StrategicPlan
        plan_count = StrategicPlan.objects.count()
        print(f"✅ StrategicPlan model accessible ({plan_count} plans)")

        print("✅ Monitoring model tests passed!")
        return True

    except Exception as e:
        print(f"❌ Monitoring model test failed: {e}")
        return False

def test_recommendations_models():
    """Test recommendations models."""
    try:
        from recommendations.policy_tracking.models import PolicyRecommendation

        print("Testing Recommendations Models...")

        # Test PolicyRecommendation
        policy_count = PolicyRecommendation.objects.count()
        print(f"✅ PolicyRecommendation model accessible ({policy_count} policies)")

        print("✅ Recommendations model tests passed!")
        return True

    except Exception as e:
        print(f"❌ Recommendations model test failed: {e}")
        return False

def test_database_operations():
    """Test basic database operations."""
    try:
        from django.db import connection
        from django.contrib.auth import get_user_model

        print("Testing Database Operations...")

        # Test basic query
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM auth_user")
            user_count = cursor.fetchone()[0]
            print(f"✅ Database query working ({user_count} users)")

        # Test Django ORM
        User = get_user_model()
        django_user_count = User.objects.count()
        print(f"✅ Django ORM working ({django_user_count} users)")

        # Test relationship queries
        from organizations.models import Organization
        org_count = Organization.objects.count()
        print(f"✅ Relationship queries working ({org_count} organizations)")

        print("✅ Database operations tests passed!")
        return True

    except Exception as e:
        print(f"❌ Database operations test failed: {e}")
        return False

def main():
    """Run all basic component tests."""
    print("=" * 60)
    print("OBCMS BASIC COMPONENT TESTS")
    print("=" * 60)

    tests = [
        ("Database Operations", test_database_operations),
        ("Organization Models", test_organizations_models),
        ("Geographic Models", test_geographic_models),
        ("Common Models", test_common_models),
        ("Communities Models", test_communities_models),
        ("Coordination Models", test_coordination_models),
        ("MANA Models", test_mana_models),
        ("Monitoring Models", test_monitoring_models),
        ("Recommendations Models", test_recommendations_models),
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
        print("🎉 ALL BASIC COMPONENT TESTS PASSED!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())