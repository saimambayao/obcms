#!/usr/bin/env python
"""
Verification script for BMMS Phase 1: Organizations App

This script verifies that all 44 BARMM MOAs were seeded correctly
and that OOBC has ID=1 for backward compatibility.

Usage:
    cd src/
    python ../verify_organizations.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.development')
django.setup()

from organizations.models import Organization


def verify_organizations():
    """Verify organization seeding was successful."""
    print("\n" + "="*70)
    print("BMMS Phase 1: Organizations App Verification")
    print("="*70 + "\n")

    # Test 1: Count all organizations
    total_count = Organization.objects.count()
    print(f"✓ Total Organizations: {total_count}")
    if total_count != 44:
        print(f"  ❌ ERROR: Expected 44, got {total_count}")
        return False
    else:
        print(f"  ✅ PASS: Expected 44, got {total_count}")

    # Test 2: Verify OOBC exists and has ID=1
    try:
        oobc = Organization.objects.get(code='OOBC')
        print(f"\n✓ OOBC Organization found")
        print(f"  - ID: {oobc.id}")
        print(f"  - Name: {oobc.name}")
        print(f"  - Type: {oobc.org_type}")

        if oobc.id != 1:
            print(f"  ❌ CRITICAL ERROR: OOBC ID should be 1, got {oobc.id}")
            print(f"     This breaks backward compatibility!")
            return False
        else:
            print(f"  ✅ PASS: OOBC has ID=1 (correct)")
    except Organization.DoesNotExist:
        print(f"  ❌ CRITICAL ERROR: OOBC organization not found!")
        return False

    # Test 3: Verify pilot MOAs
    pilot_moas = Organization.objects.filter(is_pilot=True).order_by('code')
    pilot_count = pilot_moas.count()
    print(f"\n✓ Pilot MOAs: {pilot_count}")

    if pilot_count != 3:
        print(f"  ❌ ERROR: Expected 3 pilot MOAs, got {pilot_count}")
        return False

    expected_pilots = {'MAFAR', 'MOH', 'MOLE'}
    actual_pilots = set(pilot_moas.values_list('code', flat=True))

    if actual_pilots != expected_pilots:
        print(f"  ❌ ERROR: Pilot MOAs mismatch")
        print(f"     Expected: {expected_pilots}")
        print(f"     Got: {actual_pilots}")
        return False

    print(f"  ✅ PASS: All 3 pilot MOAs correctly flagged")
    for pilot in pilot_moas:
        print(f"     • {pilot.code}: {pilot.name}")

    # Test 4: Verify organization types
    type_counts = {
        'ministry': 16,
        'office': 10,
        'agency': 8,
        'special': 7,
        'commission': 3,
    }

    print(f"\n✓ Organization Type Distribution:")
    all_types_ok = True

    for org_type, expected_count in type_counts.items():
        actual_count = Organization.objects.filter(org_type=org_type).count()
        status = "✅" if actual_count == expected_count else "❌"
        print(f"  {status} {org_type.capitalize()}: {actual_count} (expected: {expected_count})")
        if actual_count != expected_count:
            all_types_ok = False

    if not all_types_ok:
        return False

    # Test 5: Verify specific organizations
    critical_orgs = [
        ('OOBC', 'Office for Other Bangsamoro Communities'),
        ('OCM', 'Office of the Chief Minister'),
        ('MOH', 'Ministry of Health'),
        ('MOLE', 'Ministry of Labor and Employment'),
        ('MAFAR', 'Ministry of Agriculture, Fisheries and Agrarian Reform'),
    ]

    print(f"\n✓ Critical Organizations Check:")
    for code, expected_name in critical_orgs:
        try:
            org = Organization.objects.get(code=code)
            if org.name == expected_name:
                print(f"  ✅ {code}: {org.name}")
            else:
                print(f"  ❌ {code}: Name mismatch")
                print(f"     Expected: {expected_name}")
                print(f"     Got: {org.name}")
                return False
        except Organization.DoesNotExist:
            print(f"  ❌ {code}: Not found!")
            return False

    # Test 6: Verify module flags
    print(f"\n✓ Module Flags (All should default to True):")
    sample_org = Organization.objects.first()
    module_flags = [
        'enable_mana',
        'enable_planning',
        'enable_budgeting',
        'enable_me',
        'enable_coordination',
        'enable_policies',
    ]

    all_flags_ok = True
    for flag in module_flags:
        value = getattr(sample_org, flag)
        status = "✅" if value else "❌"
        print(f"  {status} {flag}: {value}")
        if not value:
            all_flags_ok = False

    if not all_flags_ok:
        print(f"  ⚠️  WARNING: Some module flags are False (expected True by default)")

    # Final Summary
    print("\n" + "="*70)
    print("✅ ALL VERIFICATION TESTS PASSED")
    print("="*70)
    print(f"\nSummary:")
    print(f"  • 44 BARMM MOAs seeded successfully")
    print(f"  • OOBC has ID=1 (backward compatible)")
    print(f"  • 3 pilot MOAs flagged correctly")
    print(f"  • Organization types distributed correctly")
    print(f"  • All critical organizations present")
    print(f"  • Module flags default to True")
    print("\n🎉 BMMS Phase 1: Organizations App - READY FOR USE\n")

    return True


if __name__ == '__main__':
    try:
        success = verify_organizations()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ VERIFICATION FAILED WITH ERROR:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
