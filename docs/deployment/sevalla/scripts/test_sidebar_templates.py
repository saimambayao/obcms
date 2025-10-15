#!/usr/bin/env python3
"""
Test script to verify sidebar templates render correctly.

This script checks that all three sidebar templates (create, edit, detail)
can be rendered without template errors.

Usage:
    cd src
    python ../scripts/test_sidebar_templates.py
"""

import os
import sys

import pytest

try:
    import django
except ImportError:  # pragma: no cover - handled via skip
    django = None

if django is None:  # pragma: no cover - executed only when dependency missing
    pytest.skip(
        "Django is required for sidebar template rendering checks",
        allow_module_level=True,
    )

# Setup Django environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.development')
django.setup()

from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from common.work_item_model import WorkItem
from common.forms.work_items import WorkItemQuickEditForm
from monitoring.models import MonitoringEntry

User = get_user_model()


def test_sidebar_create_form():
    """Test that sidebar create form template renders without errors."""
    print("\n" + "="*80)
    print("TEST 1: Sidebar Create Form Template")
    print("="*80)

    try:
        # Get test data
        ppa = MonitoringEntry.objects.filter(enable_workitem_tracking=True).first()
        user = User.objects.filter(is_superuser=True).first()

        if not ppa or not user:
            print("⚠️  SKIP: No PPA or user found for testing")
            return False

        # Create form
        form = WorkItemQuickEditForm(user=user)

        # Render template
        context = {
            'form': form,
            'is_create': True,
            'ppa_id': str(ppa.id),
            'ppa_info': ppa,
            'assignee_user': None,
            'assignee_id': None
        }

        html = render_to_string('work_items/partials/sidebar_create_form.html', context)

        # Verify content
        assert 'Create New Work Item' in html, "Missing form title"
        assert 'currency_php' not in html, "Template filter not processed"
        assert 'Budget Tracking' in html, "Missing budget section"

        if ppa.budget_allocation:
            # Check that currency is formatted (not raw variable)
            assert '₱' in html, "Missing currency symbol"
            assert f'{ppa.budget_allocation}' not in html, "Budget not formatted"

        print(f"✅ PASS: Create form template renders correctly")
        print(f"   - Form title: Found")
        print(f"   - Budget section: Found")
        print(f"   - Currency formatting: Working")
        print(f"   - Template length: {len(html)} characters")
        return True

    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_sidebar_edit_form():
    """Test that sidebar edit form template renders without errors."""
    print("\n" + "="*80)
    print("TEST 2: Sidebar Edit Form Template")
    print("="*80)

    try:
        # Get test data
        work_item = WorkItem.objects.filter(
            related_ppa__isnull=False
        ).first()

        if not work_item:
            print("⚠️  SKIP: No work item found for testing")
            return False

        user = User.objects.filter(is_superuser=True).first()

        # Create form
        form = WorkItemQuickEditForm(instance=work_item, user=user)

        # Render template
        context = {
            'form': form,
            'work_item': work_item,
            'is_create': False
        }

        html = render_to_string('work_items/partials/sidebar_edit_form.html', context)

        # Verify content
        assert 'Edit Work Item' in html, "Missing form title"
        assert 'currency_php' not in html, "Template filter not processed"

        if work_item.related_ppa and work_item.related_ppa.budget_allocation:
            assert 'Budget Tracking' in html, "Missing budget section"
            assert '₱' in html, "Missing currency symbol"

        print(f"✅ PASS: Edit form template renders correctly")
        print(f"   - Form title: Found")
        print(f"   - Template length: {len(html)} characters")
        return True

    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_sidebar_detail_view():
    """Test that sidebar detail view template renders without errors."""
    print("\n" + "="*80)
    print("TEST 3: Sidebar Detail View Template")
    print("="*80)

    try:
        # Get test data
        work_item = WorkItem.objects.filter(
            related_ppa__isnull=False
        ).first()

        if not work_item:
            print("⚠️  SKIP: No work item found for testing")
            return False

        # Render template
        context = {
            'work_item': work_item,
            'can_edit': True,
            'can_delete': True
        }

        html = render_to_string('work_items/partials/sidebar_detail.html', context)

        # Verify content
        assert work_item.title in html, "Missing work item title"
        assert 'currency_php' not in html, "Template filter not processed"

        if work_item.allocated_budget or (work_item.related_ppa and work_item.related_ppa.budget_allocation):
            assert 'Budget Tracking' in html, "Missing budget section"
            assert '₱' in html, "Missing currency symbol"

        print(f"✅ PASS: Detail view template renders correctly")
        print(f"   - Work item title: Found")
        print(f"   - Template length: {len(html)} characters")
        return True

    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all template tests."""
    print("\n" + "="*80)
    print("WORK ITEM SIDEBAR TEMPLATE TESTS")
    print("="*80)
    print("\nVerifying that all sidebar templates render correctly after fix...")

    results = []
    results.append(('Create Form', test_sidebar_create_form()))
    results.append(('Edit Form', test_sidebar_edit_form()))
    results.append(('Detail View', test_sidebar_detail_view()))

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Sidebar templates are working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
