#!/usr/bin/env python
"""Simplified test for MANA data isolation."""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from organizations.models import Organization
from organizations.models.scoped import set_current_organization
from mana.models import Assessment
from datetime import date

User = get_user_model()

print("=" * 70)
print("MANA APP - DATA ISOLATION TEST (Simplified)")
print("=" * 70)

# Use existing admin user
admin_user = User.objects.get(username='admin')
print(f"\n✅ Using admin user: {admin_user.username}")

# Get/Create organizations
oobc = Organization.objects.get(code='OOBC')
print(f"✅ OOBC: {oobc.name} (ID: {oobc.id})")

moh, _ = Organization.objects.get_or_create(
    code='MOH_TEST',
    defaults={
        'name': 'Ministry of Health (Test)',
        'short_name': 'MOH',
        'organization_type': 'ministry',
        'is_active': True
    }
)
print(f"✅ Test MOA: {moh.name} (ID: {moh.id})")

# Test 1: Create with OOBC
print("\n" + "-" * 70)
print("TEST 1: Create assessment in OOBC context")
print("-" * 70)

set_current_organization(oobc)
oobc_assessment = Assessment.objects.create(
    title='OOBC Test Assessment',
    assessment_type='needs_assessment',
    status='planning',
    assessment_level='community',
    date_started=date.today(),
    lead_assessor=admin_user,
    target_beneficiaries=100
)
print(f"✅ Created: {oobc_assessment.title}")
print(f"   Organization: {oobc_assessment.organization.code}")

# Test 2: Create with MOH
print("\n" + "-" * 70)
print("TEST 2: Create assessment in MOH context")
print("-" * 70)

set_current_organization(moh)
moh_assessment = Assessment.objects.create(
    title='MOH Test Assessment',
    assessment_type='needs_assessment',
    status='planning',
    assessment_level='regional',
    date_started=date.today(),
    lead_assessor=admin_user,
    target_beneficiaries=500
)
print(f"✅ Created: {moh_assessment.title}")
print(f"   Organization: {moh_assessment.organization.code}")

# Test 3: Isolation check
print("\n" + "-" * 70)
print("TEST 3: Verify data isolation")
print("-" * 70)

set_current_organization(oobc)
oobc_count = Assessment.objects.count()
print(f"✅ OOBC sees {oobc_count} assessment(s)")

set_current_organization(moh)
moh_count = Assessment.objects.count()
print(f"✅ MOH sees {moh_count} assessment(s)")

total_count = Assessment.all_objects.count()
print(f"✅ all_objects sees {total_count} assessment(s)")

# Verify isolation
success = (oobc_count == 1 and moh_count == 1 and total_count == 2)

if success:
    print("\n✅ PASS: Data isolation working correctly!")
else:
    print("\n❌ FAIL: Data isolation not working!")

# Cleanup
print("\n" + "-" * 70)
print("CLEANUP")
print("-" * 70)

Assessment.all_objects.all().delete()
moh.delete()
print("✅ Test data removed")

print("\n" + "=" * 70)
if success:
    print("✅ ALL TESTS PASSED - BMMS Phase 6 Complete")
else:
    print("❌ TESTS FAILED")
print("=" * 70)

sys.exit(0 if success else 1)
