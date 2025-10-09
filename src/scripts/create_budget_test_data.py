#!/usr/bin/env python
"""
Create sample work items for testing budget tracking functionality.

This script creates 3 work items per PPA demonstrating:
- GREEN: Under budget (60% utilization)
- AMBER: Near budget limit (97% utilization)
- RED: Over budget (105% utilization)
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.development')
django.setup()

from monitoring.models import MonitoringEntry
from common.work_item_model import WorkItem
from decimal import Decimal
from django.db.models import Sum
from django.contrib.auth import get_user_model

User = get_user_model()


def main():
    """Create comprehensive test data for budget tracking."""

    # Get or create system user
    system_user, _ = User.objects.get_or_create(
        username='system',
        defaults={
            'first_name': 'System',
            'last_name': 'User',
            'is_active': False
        }
    )

    # Find PPAs with budgets
    ppas = MonitoringEntry.objects.filter(
        category='moa_ppa',
        budget_allocation__gt=0
    ).order_by('-budget_allocation')[:3]

    if not ppas:
        print("❌ No PPAs with budgets found!")
        return

    print("\n" + "=" * 80)
    print("CREATING SAMPLE WORK ITEMS FOR BUDGET TRACKING TEST")
    print("=" * 80)

    created_items = []

    for ppa in ppas:
        print(f"\n\n📋 PPA: {ppa.title}")
        print(f"   Budget: ₱{ppa.budget_allocation:,.2f}")
        print(f"   MOA: {ppa.implementing_moa.name if ppa.implementing_moa else 'N/A'}")
        print("-" * 80)

        # Calculate budgets for 3 components (equal split)
        component_budget = ppa.budget_allocation / Decimal('3')

        work_items_data = [
            {
                'title': f'{ppa.title} - Infrastructure Component',
                'budget': component_budget,
                'expenditure': component_budget * Decimal('0.60'),  # 60% - GREEN
                'work_type': 'activity',
                'status': 'in_progress',
                'progress': 60,
                'notes': 'Under budget - efficient procurement. Savings available.',
                'scenario': 'GREEN'
            },
            {
                'title': f'{ppa.title} - Capacity Building Component',
                'budget': component_budget,
                'expenditure': component_budget * Decimal('0.97'),  # 97% - AMBER
                'work_type': 'activity',
                'status': 'in_progress',
                'progress': 97,
                'notes': 'Near budget limit - requires monitoring.',
                'scenario': 'AMBER'
            },
            {
                'title': f'{ppa.title} - Equipment Component',
                'budget': component_budget,
                'expenditure': component_budget * Decimal('1.05'),  # 105% - RED
                'work_type': 'task',
                'status': 'in_progress',
                'progress': 100,
                'notes': 'Over budget - price increases. Needs augmentation.',
                'scenario': 'RED'
            },
        ]

        for item_data in work_items_data:
            variance = item_data['expenditure'] - item_data['budget']
            variance_pct = (variance / item_data['budget']) * 100

            # Create work item
            work_item = WorkItem.objects.create(
                work_type=item_data['work_type'],
                title=item_data['title'],
                description=f"Test component for budget tracking - {item_data['scenario']} scenario",
                status=item_data['status'],
                priority='medium',
                progress=item_data['progress'],
                allocated_budget=item_data['budget'],
                actual_expenditure=item_data['expenditure'],
                budget_notes=item_data['notes'],
                related_ppa=ppa,
                created_by=system_user,
                auto_calculate_progress=False,
                is_calendar_visible=True,
            )

            status_icon = "🟢" if variance_pct < -5 else "🟡" if variance_pct < 2 else "🔴"

            print(f"\n  {status_icon} {item_data['scenario']}: {work_item.title[:50]}...")
            print(f"     Allocated: ₱{item_data['budget']:,.2f}")
            print(f"     Spent:     ₱{item_data['expenditure']:,.2f}")
            print(f"     Variance:  ₱{variance:,.2f} ({variance_pct:+.2f}%)")
            print(f"     ✅ Created ID: {work_item.id}")

            created_items.append(work_item)

    # Print summary
    print("\n\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print(f"\n✅ Total Work Items Created: {len(created_items)}")
    print(f"✅ PPAs Processed: {ppas.count()}")

    print("\n\nBudget Status Distribution:")

    green = sum(1 for wi in created_items if ((wi.actual_expenditure - wi.allocated_budget) / wi.allocated_budget * 100) < -5)
    amber = sum(1 for wi in created_items if -5 <= ((wi.actual_expenditure - wi.allocated_budget) / wi.allocated_budget * 100) < 2)
    red = sum(1 for wi in created_items if ((wi.actual_expenditure - wi.allocated_budget) / wi.allocated_budget * 100) >= 2)

    print(f"  🟢 Under Budget (GREEN): {green} items")
    print(f"  🟡 Near Limit (AMBER):   {amber} items")
    print(f"  🔴 Over Budget (RED):    {red} items")

    print("\n\nPer-PPA Aggregation:")
    for ppa in ppas:
        agg = WorkItem.objects.filter(related_ppa=ppa).aggregate(
            total_allocated=Sum('allocated_budget'),
            total_spent=Sum('actual_expenditure')
        )

        if agg['total_allocated']:
            variance = agg['total_spent'] - agg['total_allocated']
            variance_pct = (variance / agg['total_allocated']) * 100

            print(f"\n  📊 {ppa.title[:50]}...")
            print(f"     PPA Budget:     ₱{ppa.budget_allocation:,.2f}")
            print(f"     Total Allocated: ₱{agg['total_allocated']:,.2f}")
            print(f"     Total Spent:     ₱{agg['total_spent']:,.2f}")
            print(f"     Variance:        ₱{variance:,.2f} ({variance_pct:+.2f}%)")

    print("\n" + "=" * 80)
    print("✅ TEST DATA CREATION COMPLETE!")
    print("=" * 80)
    print("\nYou can now:")
    print("1. View PPAs in the monitoring dashboard")
    print("2. Check work items tab for each PPA")
    print("3. Verify budget tracking displays (green/amber/red indicators)")
    print("4. Test budget variance calculations")
    print("\n")


if __name__ == '__main__':
    main()
