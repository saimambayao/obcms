#!/usr/bin/env python
"""Verify budget tracking test data."""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.development')
django.setup()

from monitoring.models import MonitoringEntry
from common.work_item_model import WorkItem
from decimal import Decimal
from django.db.models import Sum


def main():
    """Verify created test data."""

    print("\n" + "="*80)
    print("BUDGET TRACKING VERIFICATION")
    print("="*80)

    # Get PPAs that have work items
    ppas_with_work = []
    all_ppas = MonitoringEntry.objects.filter(
        category='moa_ppa',
        budget_allocation__gt=0
    ).order_by('-budget_allocation')[:5]

    for ppa in all_ppas:
        wi_count = WorkItem.objects.filter(related_ppa=ppa).count()
        if wi_count > 0:
            ppas_with_work.append(ppa)

    if not ppas_with_work:
        print("❌ No PPAs with work items found!")
        return

    print(f"\nFound {len(ppas_with_work)} PPAs with work items")

    for ppa in ppas_with_work[:3]:  # Limit to 3 for readability
        print(f"\n\n{'='*80}")
        print(f"PPA: {ppa.title}")
        print(f"PPA Budget: ₱{ppa.budget_allocation:,.2f}")
        print(f"{'='*80}")

        work_items = WorkItem.objects.filter(related_ppa=ppa).order_by('created_at')

        print(f"\nWork Items ({work_items.count()}):")
        print("-" * 80)

        for wi in work_items:
            if wi.allocated_budget and wi.allocated_budget > 0:
                variance = wi.actual_expenditure - wi.allocated_budget
                variance_pct = (variance / wi.allocated_budget) * 100
                utilization_pct = (wi.actual_expenditure / wi.allocated_budget) * 100

                # Determine status
                if variance_pct > 2:
                    status = "🔴 OVER BUDGET"
                    status_class = "over-budget"
                elif variance_pct > -5:
                    status = "🟡 NEAR LIMIT"
                    status_class = "near-limit"
                else:
                    status = "🟢 UNDER BUDGET"
                    status_class = "under-budget"

                print(f"\n{status}")
                print(f"  Title: {wi.title[:70]}...")
                print(f"  Type: {wi.get_work_type_display()}")
                print(f"  Status: {wi.get_status_display()} ({wi.progress}% complete)")
                print(f"  Allocated: ₱{wi.allocated_budget:,.2f}")
                print(f"  Spent:     ₱{wi.actual_expenditure:,.2f}")
                print(f"  Variance:  ₱{variance:,.2f} ({variance_pct:+.2f}%)")
                print(f"  Utilization: {utilization_pct:.2f}%")
                print(f"  CSS Class: {status_class}")

        # PPA Aggregation
        agg = WorkItem.objects.filter(related_ppa=ppa).aggregate(
            total_allocated=Sum('allocated_budget'),
            total_spent=Sum('actual_expenditure')
        )

        if agg['total_allocated']:
            ppa_variance = agg['total_spent'] - agg['total_allocated']
            ppa_variance_pct = (ppa_variance / agg['total_allocated']) * 100

            print(f"\n{'='*80}")
            print(f"PPA TOTALS:")
            print(f"  Original PPA Budget:  ₱{ppa.budget_allocation:,.2f}")
            print(f"  Work Items Allocated: ₱{agg['total_allocated']:,.2f}")
            print(f"  Work Items Spent:     ₱{agg['total_spent']:,.2f}")
            print(f"  Overall Variance:     ₱{ppa_variance:,.2f} ({ppa_variance_pct:+.2f}%)")

            # Check if work items sum to PPA budget
            budget_diff = abs(ppa.budget_allocation - agg['total_allocated'])
            if budget_diff < Decimal('0.01'):
                print(f"  ✅ Work item budgets match PPA budget")
            else:
                print(f"  ⚠️  Difference: ₱{budget_diff:,.2f}")

    # Overall statistics
    print("\n\n" + "="*80)
    print("OVERALL STATISTICS")
    print("="*80)

    all_work_items = WorkItem.objects.filter(
        related_ppa__isnull=False,
        allocated_budget__gt=0
    )

    green = 0
    amber = 0
    red = 0

    for wi in all_work_items:
        if wi.allocated_budget and wi.allocated_budget > 0:
            variance_pct = ((wi.actual_expenditure - wi.allocated_budget) / wi.allocated_budget) * 100
            if variance_pct > 2:
                red += 1
            elif variance_pct > -5:
                amber += 1
            else:
                green += 1

    total = green + amber + red

    print(f"\nBudget Status Distribution:")
    print(f"  🟢 Under Budget (GREEN): {green} items ({green/total*100:.1f}%)")
    print(f"  🟡 Near Limit (AMBER):   {amber} items ({amber/total*100:.1f}%)")
    print(f"  🔴 Over Budget (RED):    {red} items ({red/total*100:.1f}%)")
    print(f"  Total:                   {total} items")

    print("\n\nBudget Status Thresholds:")
    print("  🟢 GREEN:  variance < -5% (efficient, under budget)")
    print("  🟡 AMBER:  -5% <= variance < +2% (close to budget, monitor)")
    print("  🔴 RED:    variance >= +2% (over budget, action needed)")

    print("\n" + "="*80)
    print("✅ VERIFICATION COMPLETE!")
    print("="*80)
    print("\nNext Steps:")
    print("1. Access the monitoring dashboard to view PPAs")
    print("2. Click on a PPA to see the Work Items tab")
    print("3. Verify budget tracking displays with color indicators")
    print("4. Test variance calculations and status colors")
    print("\n")


if __name__ == '__main__':
    main()
