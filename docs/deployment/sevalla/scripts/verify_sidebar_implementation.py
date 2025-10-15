#!/usr/bin/env python
"""
Verification Script: Work Item Sidebar Detail Implementation
=============================================================

This script verifies that all components of the work item sidebar detail
view are properly implemented and accessible.

Run from project root:
    python verify_sidebar_implementation.py
"""

import sys
import os
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
CHECK = f'{GREEN}✓{RESET}'
CROSS = f'{RED}✗{RESET}'
INFO = f'{BLUE}ℹ{RESET}'

def check_file_exists(path, description):
    """Check if a file exists and print result."""
    if Path(path).exists():
        print(f"{CHECK} {description}: {GREEN}{path}{RESET}")
        return True
    else:
        print(f"{CROSS} {description}: {RED}{path}{RESET}")
        return False

def check_content_in_file(path, pattern, description):
    """Check if content exists in file."""
    try:
        with open(path, 'r') as f:
            content = f.read()
            if pattern in content:
                print(f"{CHECK} {description}")
                return True
            else:
                print(f"{CROSS} {description}")
                return False
    except FileNotFoundError:
        print(f"{CROSS} {description} - File not found: {path}")
        return False

def main():
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}Work Item Sidebar Detail Implementation Verification{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

    # Get the project root (parent of scripts folder)
    base_path = Path(__file__).parent.parent
    src_path = base_path / 'src'

    results = []

    # 1. Check backend view file
    print(f"{YELLOW}[1/7] Backend View Implementation{RESET}")
    view_file = src_path / 'common' / 'views' / 'work_items.py'
    results.append(check_file_exists(view_file, "View file exists"))
    results.append(check_content_in_file(
        view_file,
        'def work_item_sidebar_detail',
        "Function 'work_item_sidebar_detail' defined"
    ))
    results.append(check_content_in_file(
        view_file,
        'get_work_item_permissions',
        "Permission check implemented"
    ))
    print()

    # 2. Check URL configuration
    print(f"{YELLOW}[2/7] URL Configuration{RESET}")
    urls_file = src_path / 'common' / 'urls.py'
    results.append(check_file_exists(urls_file, "URLs file exists"))
    results.append(check_content_in_file(
        urls_file,
        'work_item_sidebar_detail',
        "URL pattern registered"
    ))
    results.append(check_content_in_file(
        urls_file,
        'name="work_item_sidebar_detail"',
        "URL name configured"
    ))
    print()

    # 3. Check view exports
    print(f"{YELLOW}[3/7] View Exports{RESET}")
    init_file = src_path / 'common' / 'views' / '__init__.py'
    results.append(check_file_exists(init_file, "View __init__ file exists"))
    results.append(check_content_in_file(
        init_file,
        'work_item_sidebar_detail',
        "View imported in __init__.py"
    ))
    print()

    # 4. Check template
    print(f"{YELLOW}[4/7] Template Implementation{RESET}")
    template_file = src_path / 'templates' / 'common' / 'partials' / 'calendar_event_detail.html'
    results.append(check_file_exists(template_file, "Detail template exists"))
    results.append(check_content_in_file(
        template_file,
        'work_item.title',
        "Template renders work item title"
    ))
    results.append(check_content_in_file(
        template_file,
        'can_edit',
        "Permission checks in template"
    ))
    results.append(check_content_in_file(
        template_file,
        'work_item_sidebar_edit',
        "Edit button configured"
    ))
    print()

    # 5. Check model
    print(f"{YELLOW}[5/7] WorkItem Model{RESET}")
    model_file = src_path / 'common' / 'work_item_model.py'
    results.append(check_file_exists(model_file, "WorkItem model exists"))
    results.append(check_content_in_file(
        model_file,
        'class WorkItem',
        "WorkItem class defined"
    ))
    results.append(check_content_in_file(
        model_file,
        'MPTTModel',
        "MPTT hierarchy support"
    ))
    print()

    # 6. Check calendar integration
    print(f"{YELLOW}[6/7] Calendar Integration{RESET}")
    calendar_file = src_path / 'templates' / 'common' / 'oobc_calendar.html'
    results.append(check_file_exists(calendar_file, "Calendar template exists"))
    results.append(check_content_in_file(
        calendar_file,
        'handleEventClick',
        "Event click handler implemented"
    ))
    results.append(check_content_in_file(
        calendar_file,
        'sidebar/detail/',
        "Sidebar detail URL referenced"
    ))
    print()

    # 7. Check edit form integration
    print(f"{YELLOW}[7/7] Edit Form Integration{RESET}")
    edit_form_file = src_path / 'templates' / 'common' / 'partials' / 'calendar_event_edit_form.html'
    results.append(check_file_exists(edit_form_file, "Edit form template exists"))
    results.append(check_content_in_file(
        edit_form_file,
        "url 'common:work_item_sidebar_detail'",
        "Cancel button returns to detail view"
    ))
    print()

    # Summary
    print(f"{BLUE}{'='*70}{RESET}")
    total_checks = len(results)
    passed_checks = sum(results)
    failed_checks = total_checks - passed_checks

    print(f"\n{BLUE}Summary:{RESET}")
    print(f"  Total checks: {total_checks}")
    print(f"  {GREEN}Passed: {passed_checks}{RESET}")
    if failed_checks > 0:
        print(f"  {RED}Failed: {failed_checks}{RESET}")

    print(f"\n{BLUE}{'='*70}{RESET}\n")

    if all(results):
        print(f"{GREEN}✓ All checks passed! Implementation is complete.{RESET}\n")
        return 0
    else:
        print(f"{RED}✗ Some checks failed. Please review the implementation.{RESET}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
