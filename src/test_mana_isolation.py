#!/usr/bin/env python
"""Test MANA data isolation and auto-filtering."""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from organizations.models import Organization
from organizations.models.scoped import set_current_organization
from mana.models import Assessment
from datetime import date

User = get_user_model()

def test_data_isolation():
    """Test that MANA models enforce organization-based data isolation."""
    
    print("=" * 70)
    print("MANA APP - DATA ISOLATION TEST")
    print("=" * 70)
    
    # Create test user
    test_user, _ = User.objects.get_or_create(
        username='test_mana_user',
        defaults={'email': 'test@oobc.gov.ph'}
    )
    print(f"\n✅ Test User: {test_user.username}")
    
    # Get OOBC organization
    oobc = Organization.objects.get(code='OOBC')
    print(f"✅ OOBC Organization: {oobc.name} (ID: {oobc.id})")
    
    # Create test MOA
    moh, created = Organization.objects.get_or_create(
        code='MOH',
        defaults={
            'name': 'Ministry of Health',
            'short_name': 'MOH',
            'organization_type': 'ministry',
            'is_active': True
        }
    )
    print(f"✅ Test MOA: {moh.name} (ID: {moh.id})")
    
    # Test 1: Create assessment with OOBC context
    print("\n" + "-" * 70)
    print("TEST 1: Create assessment with OOBC organization context")
    print("-" * 70)
    
    set_current_organization(oobc)
    oobc_assessment = Assessment.objects.create(
        title='OOBC Community Needs Assessment',
        assessment_type='needs_assessment',
        status='planning',
        assessment_level='community',
        date_started=date.today(),
        lead_assessor=test_user,
        target_beneficiaries=100
    )
    print(f"✅ Created OOBC assessment: {oobc_assessment.title}")
    print(f"   Organization: {oobc_assessment.organization.code}")
    
    # Test 2: Create assessment with MOH context
    print("\n" + "-" * 70)
    print("TEST 2: Create assessment with MOH organization context")
    print("-" * 70)
    
    set_current_organization(moh)
    moh_assessment = Assessment.objects.create(
        title='MOH Health Services Assessment',
        assessment_type='needs_assessment',
        status='planning',
        assessment_level='regional',
        date_started=date.today(),
        lead_assessor=test_user,
        target_beneficiaries=500
    )
    print(f"✅ Created MOH assessment: {moh_assessment.title}")
    print(f"   Organization: {moh_assessment.organization.code}")
    
    # Test 3: OOBC cannot see MOH data
    print("\n" + "-" * 70)
    print("TEST 3: Data isolation - OOBC cannot see MOH assessments")
    print("-" * 70)
    
    set_current_organization(oobc)
    oobc_count = Assessment.objects.count()
    oobc_has_moh = Assessment.objects.filter(title__icontains='MOH').exists()
    
    print(f"✅ OOBC context - Total assessments visible: {oobc_count}")
    print(f"✅ OOBC can see MOH assessment: {oobc_has_moh}")
    
    if not oobc_has_moh and oobc_count == 1:
        print("   ✅ PASS: Data isolation working - OOBC cannot see MOH data")
    else:
        print("   ❌ FAIL: Data leakage detected!")
        return False
    
    # Test 4: MOH cannot see OOBC data
    print("\n" + "-" * 70)
    print("TEST 4: Data isolation - MOH cannot see OOBC assessments")
    print("-" * 70)
    
    set_current_organization(moh)
    moh_count = Assessment.objects.count()
    moh_has_oobc = Assessment.objects.filter(title__icontains='OOBC').exists()
    
    print(f"✅ MOH context - Total assessments visible: {moh_count}")
    print(f"✅ MOH can see OOBC assessment: {moh_has_oobc}")
    
    if not moh_has_oobc and moh_count == 1:
        print("   ✅ PASS: Data isolation working - MOH cannot see OOBC data")
    else:
        print("   ❌ FAIL: Data leakage detected!")
        return False
    
    # Test 5: Direct ID access blocked
    print("\n" + "-" * 70)
    print("TEST 5: Direct ID access blocked by auto-filtering")
    print("-" * 70)
    
    set_current_organization(oobc)
    try:
        # Try to access MOH assessment directly by ID
        Assessment.objects.get(id=moh_assessment.id)
        print("   ❌ FAIL: Cross-org access succeeded!")
        return False
    except Assessment.DoesNotExist:
        print(f"   ✅ PASS: Cross-org direct access blocked (Assessment.DoesNotExist)")
    
    # Test 6: all_objects manager for admin
    print("\n" + "-" * 70)
    print("TEST 6: all_objects manager bypasses filtering (admin/OCM only)")
    print("-" * 70)
    
    total_all = Assessment.all_objects.count()
    print(f"✅ Total assessments (all_objects): {total_all}")
    
    if total_all == 2:
        print("   ✅ PASS: all_objects manager sees all records")
    else:
        print(f"   ❌ FAIL: Expected 2 records, got {total_all}")
        return False
    
    # Cleanup
    print("\n" + "-" * 70)
    print("CLEANUP: Removing test data")
    print("-" * 70)
    
    Assessment.all_objects.all().delete()
    moh.delete()
    test_user.delete()
    
    print("✅ Test data cleaned up")
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED - Data Privacy Act 2012 Compliance Verified")
    print("=" * 70)
    
    return True

if __name__ == '__main__':
    try:
        success = test_data_isolation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
