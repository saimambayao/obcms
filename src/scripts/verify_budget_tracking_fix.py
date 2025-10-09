#!/usr/bin/env python
"""
Verify Work Item Budget Tracking Fix

This script verifies that the budget tracking service correctly excludes
execution project roots and only counts actual child work items.

Usage:
    cd src
    python scripts/verify_budget_tracking_fix.py
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "obc_management.settings.development")
django.setup()

from decimal import Decimal
from monitoring.models import MonitoringEntry
from monitoring.services.budget_tracking import build_moa_budget_tracking
from common.work_item_model import WorkItem


def verify_ppa_budget_tracking(ppa_id: str):
    """Verify budget tracking for a specific PPA."""
    try:
        ppa = MonitoringEntry.objects.get(id=ppa_id)
    except MonitoringEntry.DoesNotExist:
        print(f"❌ PPA with ID {ppa_id} not found")
        return False

    print(f"\n{'='*80}")
    print(f"Verifying PPA: {ppa.title}")
    print(f"{'='*80}")

    # Get all work items related to this PPA (before filtering)
    all_work_items = WorkItem.objects.filter(related_ppa=ppa)
    print(f"\n📊 Total work items with related_ppa={ppa_id}: {all_work_items.count()}")

    if not all_work_items.exists():
        print("✅ No work items found - budget should be ₱0.00")
        return True

    # Categorize work items
    execution_roots = all_work_items.filter(
        parent__isnull=True, work_type=WorkItem.WORK_TYPE_PROJECT
    )
    child_work_items = all_work_items.exclude(
        parent__isnull=True, work_type=WorkItem.WORK_TYPE_PROJECT
    )

    print(f"\n📋 Work Item Breakdown:")
    print(f"  - Execution Project Roots: {execution_roots.count()}")
    for root in execution_roots:
        budget_val = root.allocated_budget or Decimal('0.00')
        print(f"    • {root.title}: ₱{budget_val:,.2f} (SHOULD BE EXCLUDED)")

    print(f"  - Child Work Items: {child_work_items.count()}")
    for child in child_work_items:
        parent_info = f" (parent: {child.parent.title})" if child.parent else ""
        budget_val = child.allocated_budget or Decimal('0.00')
        print(
            f"    • {child.title} ({child.work_type}): "
            f"₱{budget_val:,.2f}{parent_info}"
        )

    # Calculate expected budget (manual)
    expected_budget = sum(
        (child.allocated_budget or Decimal("0.00") for child in child_work_items),
        Decimal("0.00"),
    )

    # Get budget tracking results
    organization = ppa.implementing_moa
    budget_data = build_moa_budget_tracking(organization)

    # Find this PPA in results
    actual_budget = None
    for moa_ppa in budget_data["moa_ppas"]:
        if str(moa_ppa.id) == str(ppa.id):
            actual_budget = moa_ppa.work_item_budget
            break

    print(f"\n💰 Budget Calculation:")
    print(f"  - Expected (child work items only): ₱{expected_budget:,.2f}")
    print(f"  - Actual (from budget_tracking): ₱{actual_budget:,.2f}")

    # Verify
    if actual_budget == expected_budget:
        print(f"\n✅ PASS: Budget tracking correctly excludes execution project roots")
        return True
    else:
        print(f"\n❌ FAIL: Budget mismatch!")
        print(f"  Expected: ₱{expected_budget:,.2f}")
        print(f"  Got: ₱{actual_budget:,.2f}")
        print(f"  Difference: ₱{abs(actual_budget - expected_budget):,.2f}")
        return False


def verify_all_moa_ppas():
    """Verify budget tracking for all MOA PPAs with work items."""
    print("\n" + "=" * 80)
    print("WORK ITEM BUDGET TRACKING VERIFICATION")
    print("=" * 80)

    # Get all MOA PPAs with execution projects
    moa_ppas = MonitoringEntry.objects.filter(
        category="moa_ppa", execution_project__isnull=False
    ).select_related("implementing_moa", "execution_project")

    if not moa_ppas.exists():
        print("\n⚠️  No MOA PPAs with execution projects found")
        return True

    print(f"\nFound {moa_ppas.count()} MOA PPAs with execution projects")

    results = []
    for ppa in moa_ppas:
        passed = verify_ppa_budget_tracking(str(ppa.id))
        results.append((ppa.title, passed))

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    total = len(results)
    passed = sum(1 for _, p in results if p)
    failed = total - passed

    for title, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {title}")

    print(f"\nResults: {passed}/{total} passed, {failed}/{total} failed")

    if failed == 0:
        print("\n🎉 All budget tracking calculations are correct!")
        return True
    else:
        print(f"\n⚠️  {failed} PPA(s) have incorrect budget tracking")
        return False


if __name__ == "__main__":
    # Run verification
    success = verify_all_moa_ppas()

    # Exit with appropriate code
    sys.exit(0 if success else 1)
