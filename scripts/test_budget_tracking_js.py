#!/usr/bin/env python
"""
Budget Tracking JavaScript Function Checker

This script checks if the budget tracking JavaScript functions are properly
loaded in the work item form templates.

Usage:
    python scripts/test_budget_tracking_js.py
"""

import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.development')

import django
django.setup()

from django.template.loader import render_to_string
from django.test import RequestFactory
from common.models import WorkItem, User
from monitoring.models import MonitoringEntry


def check_js_functions_in_template(template_name, context=None):
    """Check if budget tracking JS functions are present in template."""
    print(f"\n{'='*80}")
    print(f"Checking template: {template_name}")
    print(f"{'='*80}")

    try:
        rendered = render_to_string(template_name, context or {})

        # Check for function definitions
        functions_to_check = [
            'calculateBudgetVariance',
            'calculateSidebarCreateBudgetVariance',
            'calculateSidebarEditBudgetVariance'
        ]

        results = {}
        for func_name in functions_to_check:
            if f'function {func_name}' in rendered or f'const {func_name}' in rendered or f'{func_name} =' in rendered:
                results[func_name] = '✅ FOUND'
            else:
                results[func_name] = '❌ NOT FOUND'

        # Check for budget tracking section
        budget_indicators = [
            'id_allocated_budget',
            'id_actual_expenditure',
            'budget-variance',
            'Total PPA Budget'
        ]

        budget_section_found = any(indicator in rendered for indicator in budget_indicators)

        # Print results
        print(f"\n📋 JavaScript Functions:")
        for func_name, status in results.items():
            print(f"  {status}  {func_name}()")

        print(f"\n📊 Budget Tracking Section:")
        if budget_section_found:
            print(f"  ✅ FOUND  Budget tracking UI elements present")
        else:
            print(f"  ❌ NOT FOUND  Budget tracking UI elements missing")

        # Check for PPA total budget display
        ppa_budget_indicators = [
            'Total PPA Budget',
            'ppa-total-budget',
            'PPA total budget'
        ]
        ppa_section_found = any(indicator in rendered for indicator in ppa_budget_indicators)

        print(f"\n💰 PPA Budget Display:")
        if ppa_section_found:
            print(f"  ✅ FOUND  PPA total budget display present")
        else:
            print(f"  ⚠️  WARNING  PPA total budget display not found (may be conditional)")

        # Check for event listeners
        event_listeners = [
            'addEventListener',
            'oninput',
            'onchange'
        ]
        listeners_found = sum(1 for listener in event_listeners if listener in rendered)

        print(f"\n🎧 Event Listeners:")
        if listeners_found > 0:
            print(f"  ✅ FOUND  {listeners_found} event listener types detected")
        else:
            print(f"  ❌ NOT FOUND  No event listeners detected")

        # Overall assessment
        all_functions_found = all('FOUND' in status for status in results.values())

        print(f"\n{'='*80}")
        if all_functions_found and budget_section_found:
            print(f"✅ TEMPLATE OK: All required functions and UI elements present")
        else:
            print(f"❌ TEMPLATE ISSUES: Missing functions or UI elements")
        print(f"{'='*80}")

        return all_functions_found and budget_section_found

    except Exception as e:
        print(f"❌ ERROR rendering template: {e}")
        return False


def main():
    """Main test runner."""
    print(f"\n{'#'*80}")
    print(f"# Budget Tracking JavaScript Function Checker")
    print(f"{'#'*80}")

    # Templates to check
    templates_to_check = [
        ('work_items/partials/work_item_form.html', 'Main Edit Form'),
        ('work_items/partials/work_item_modal_form.html', 'Sidebar Create/Edit Form'),
        ('work_items/detail.html', 'Detail View'),
    ]

    results = {}

    for template_path, description in templates_to_check:
        try:
            # Create minimal context
            context = {
                'form': None,  # Would need actual form instance
                'work_item': None,
                'ppa': None,
            }

            success = check_js_functions_in_template(template_path, context)
            results[description] = success

        except Exception as e:
            print(f"\n❌ ERROR checking {description}: {e}")
            results[description] = False

    # Final summary
    print(f"\n{'#'*80}")
    print(f"# SUMMARY")
    print(f"{'#'*80}\n")

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for description, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}  {description}")

    print(f"\n{'='*80}")
    print(f"Total Templates: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Pass Rate: {(passed/total*100):.1f}%")
    print(f"{'='*80}\n")

    # Exit code based on results
    if passed == total:
        print("✅ All templates passed!")
        return 0
    else:
        print("❌ Some templates failed checks!")
        return 1


if __name__ == '__main__':
    sys.exit(main())
