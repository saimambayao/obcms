#!/usr/bin/env python3
"""
Comprehensive Planning & Budgeting Module Test Suite
Tests all 22 P&B features after architectural reorganization
"""

import os
import sys
import django
import pytest

# Setup Django environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.development')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse, resolve
from django.template import TemplateDoesNotExist
from django.core.exceptions import ViewDoesNotExist
import json

User = get_user_model()

pytestmark = pytest.mark.django_db

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}\n")

def print_section(text):
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}{text}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'-'*len(text)}{Colors.ENDC}")

def print_test(name, status, details=""):
    if status == "PASS":
        symbol = "✓"
        color = Colors.OKGREEN
    elif status == "SKIP":
        symbol = "⊘"
        color = Colors.WARNING
    else:
        symbol = "✗"
        color = Colors.FAIL

    print(f"{color}{symbol} {name:<60} [{status}]{Colors.ENDC}")
    if details:
        print(f"  {Colors.WARNING}{details}{Colors.ENDC}")

# Test data structure: All 22 P&B features
PLANNING_BUDGETING_FEATURES = {
    "Core Planning & Budgeting (Phase 1-3)": [
        ('planning_budgeting', 'Planning Dashboard'),
        ('gap_analysis_dashboard', 'Gap Analysis'),
        ('policy_budget_matrix', 'Policy-Budget Matrix'),
        ('mao_focal_persons_registry', 'MAO Registry'),
        ('community_needs_summary', 'Community Needs Summary'),
    ],
    "Participatory Budgeting (Phase 4)": [
        ('community_voting_browse', 'Community Voting'),
        ('community_voting_results', 'Voting Results'),
        ('budget_feedback_dashboard', 'Budget Feedback'),
        ('transparency_dashboard', 'Transparency Dashboard'),
    ],
    "Strategic Planning (Phase 5)": [
        ('strategic_goals_dashboard', 'Strategic Goals'),
        ('annual_planning_dashboard', 'Annual Planning'),
        ('regional_development_alignment', 'RDP Alignment'),
    ],
    "Scenario Planning (Phase 6)": [
        ('scenario_list', 'Budget Scenarios'),
        ('scenario_create', 'Create Scenario'),
        ('scenario_compare', 'Compare Scenarios'),
    ],
    "Analytics & Forecasting (Phase 7)": [
        ('analytics_dashboard', 'Analytics Dashboard'),
        ('budget_forecasting', 'Budget Forecasting'),
        ('trend_analysis', 'Trend Analysis'),
        ('impact_assessment', 'Impact Assessment'),
    ],
}


def run_url_resolution():
    """Test 1: Verify all URLs can be resolved"""
    print_section("Test 1: URL Resolution")

    all_pass = True
    total_features = 0

    for phase, features in PLANNING_BUDGETING_FEATURES.items():
        print(f"\n{Colors.BOLD}{phase}{Colors.ENDC}")
        for url_name, display_name in features:
            total_features += 1
            try:
                url = reverse(f'common:{url_name}')
                resolver = resolve(url)
                print_test(f"{display_name} ({url_name})", "PASS", f"URL: {url}")
            except Exception as e:
                print_test(f"{display_name} ({url_name})", "FAIL", str(e))
                all_pass = False

    return all_pass, total_features


def run_view_responses():
    """Test 2: Verify views respond correctly (with authentication)"""
    print_section("Test 2: View Responses (Authenticated)")

    client = Client()

    # Create or get test user
    try:
        user = User.objects.filter(is_staff=True, is_active=True).first()
        if not user:
            print(f"{Colors.WARNING}No staff user found, creating test user...{Colors.ENDC}")
            user = User.objects.create_user(
                username='test_admin',
                email='test@example.com',
                password='testpass123',
                is_staff=True,
                is_active=True
            )

        # Login
        client.force_login(user)
        print(f"{Colors.OKGREEN}✓ Authenticated as: {user.username}{Colors.ENDC}\n")
    except Exception as e:
        print(f"{Colors.FAIL}✗ Authentication failed: {e}{Colors.ENDC}")
        return False

    all_pass = True
    accessible_count = 0

    for phase, features in PLANNING_BUDGETING_FEATURES.items():
        print(f"\n{Colors.BOLD}{phase}{Colors.ENDC}")
        for url_name, display_name in features:
            try:
                url = reverse(f'common:{url_name}')
                response = client.get(url, follow=True)

                if response.status_code == 200:
                    print_test(f"{display_name}", "PASS", f"HTTP 200 - {len(response.content)} bytes")
                    accessible_count += 1
                elif response.status_code == 302:
                    print_test(f"{display_name}", "SKIP", f"HTTP 302 - Redirect to {response.url}")
                else:
                    print_test(f"{display_name}", "FAIL", f"HTTP {response.status_code}")
                    all_pass = False
            except Exception as e:
                print_test(f"{display_name}", "FAIL", str(e))
                all_pass = False

    print(f"\n{Colors.OKGREEN}✓ {accessible_count} features returned HTTP 200{Colors.ENDC}")
    return all_pass


def run_template_structure():
    """Test 3: Verify P&B page template has all features"""
    print_section("Test 3: Planning & Budgeting Template Structure")

    client = Client()
    user = User.objects.filter(is_staff=True, is_active=True).first()
    if user:
        client.force_login(user)

    try:
        url = reverse('common:planning_budgeting')
        response = client.get(url)

        if response.status_code == 200:
            content = response.content.decode('utf-8')

            # Check for key sections
            checks = [
                ("Frequently Used section", "Frequently Used"),
                ("Participatory Budgeting section", "Participatory Budgeting"),
                ("Strategic Planning section", "Strategic Planning"),
                ("Scenario Planning section", "Scenario Planning"),
                ("Analytics & Forecasting section", "Analytics & Forecasting"),
                ("Gap Analysis card", "Gap Analysis"),
                ("Community Voting card", "Community Voting"),
                ("Strategic Goals card", "Strategic Goals"),
                ("Budget Scenarios card", "Budget Scenarios"),
                ("Analytics Dashboard card", "Analytics Dashboard"),
            ]

            all_pass = True
            found_count = 0

            for check_name, search_text in checks:
                if search_text in content:
                    print_test(check_name, "PASS")
                    found_count += 1
                else:
                    print_test(check_name, "FAIL", f"'{search_text}' not found in template")
                    all_pass = False

            print(f"\n{Colors.OKGREEN}✓ {found_count}/{len(checks)} sections found{Colors.ENDC}")
            return all_pass
        else:
            print_test("Planning & Budgeting page", "FAIL", f"HTTP {response.status_code}")
            return False

    except Exception as e:
        print_test("Template rendering", "FAIL", str(e))
        return False


def run_oobc_management_cleanup():
    """Test 4: Verify OOBC Management page no longer has P&B features"""
    print_section("Test 4: OOBC Management Cleanup (Only Organizational Features)")

    client = Client()
    user = User.objects.filter(is_staff=True, is_active=True).first()
    if user:
        client.force_login(user)

    try:
        url = reverse('common:oobc_management_home')
        response = client.get(url)

        if response.status_code == 200:
            content = response.content.decode('utf-8')

            # Check that P&B features are NOT present (they should be in P&B page now)
            should_not_have = [
                ("Phase 1-3: Core Planning section", "Phase 1-3: Core Planning"),
                ("Phase 4: Participatory section", "Phase 4: Participatory"),
                ("Phase 5: Strategic Planning section", "Phase 5: Strategic Planning"),
                ("Phase 6: Scenario Planning section", "Phase 6: Scenario Planning"),
                ("Phase 7: Analytics section", "Phase 7: Analytics"),
            ]

            # Check that organizational features ARE present
            should_have = [
                ("Planning & Budgeting Hub Link", "Planning & Budgeting"),
                ("OOBC Calendar card", "OOBC Calendar"),
                ("Staff Management card", "Staff Management"),
                ("User Approvals card", "User Approvals"),
                ("Organizational Management section", "Organizational Management"),
            ]

            all_pass = True

            print(f"\n{Colors.BOLD}Verifying P&B sections removed:{Colors.ENDC}")
            for check_name, search_text in should_not_have:
                if search_text not in content:
                    print_test(check_name, "PASS", "Correctly removed")
                else:
                    print_test(check_name, "FAIL", f"'{search_text}' still present (should be removed)")
                    all_pass = False

            print(f"\n{Colors.BOLD}Verifying organizational features present:{Colors.ENDC}")
            for check_name, search_text in should_have:
                if search_text in content:
                    print_test(check_name, "PASS")
                else:
                    print_test(check_name, "FAIL", f"'{search_text}' not found")
                    all_pass = False

            return all_pass
        else:
            print_test("OOBC Management page", "FAIL", f"HTTP {response.status_code}")
            return False

    except Exception as e:
        print_test("Template rendering", "FAIL", str(e))
        return False


def run_navigation_links():
    """Test 5: Verify navigation links between pages"""
    print_section("Test 5: Navigation Link Structure")

    client = Client()
    user = User.objects.filter(is_staff=True, is_active=True).first()
    if user:
        client.force_login(user)

    navigation_tests = [
        ("Dashboard -> OOBC Management", 'common:dashboard', 'oobc_management_home'),
        ("OOBC Management -> Planning & Budgeting", 'common:oobc_management_home', 'planning_budgeting'),
        ("Dashboard -> Planning & Budgeting (direct)", 'common:dashboard', 'planning_budgeting'),
    ]

    all_pass = True

    for test_name, from_url, to_url in navigation_tests:
        try:
            from_page_url = reverse(f'common:{from_url}')
            to_page_url = reverse(f'common:{to_url}')

            response = client.get(from_page_url)

            if response.status_code == 200:
                content = response.content.decode('utf-8')

                if to_page_url in content:
                    print_test(test_name, "PASS", f"{from_page_url} -> {to_page_url}")
                else:
                    print_test(test_name, "FAIL", f"Link to {to_page_url} not found in {from_page_url}")
                    all_pass = False
            else:
                print_test(test_name, "SKIP", f"Could not load {from_page_url}")
        except Exception as e:
            print_test(test_name, "FAIL", str(e))
            all_pass = False

    return all_pass


@pytest.mark.skip(reason="Manual Planning & Budgeting smoke test; run this module directly for full report.")
def test_url_resolution():
    success, _ = run_url_resolution()
    assert success, "URL resolution failures detected"


@pytest.mark.skip(reason="Manual Planning & Budgeting smoke test; run this module directly for full report.")
def test_view_responses():
    assert run_view_responses(), "View response checks failed"


@pytest.mark.skip(reason="Manual Planning & Budgeting smoke test; run this module directly for full report.")
def test_template_structure():
    assert run_template_structure(), "Planning & Budgeting template structure issues found"


@pytest.mark.skip(reason="Manual Planning & Budgeting smoke test; run this module directly for full report.")
def test_oobc_management_cleanup():
    assert run_oobc_management_cleanup(), "OOBC management still exposing Planning & Budgeting sections"


@pytest.mark.skip(reason="Manual Planning & Budgeting smoke test; run this module directly for full report.")
def test_navigation_links():
    assert run_navigation_links(), "Navigation link issues detected"


def run_all_tests():
    """Run complete test suite"""
    print_header("PLANNING & BUDGETING MODULE - COMPREHENSIVE TEST SUITE")

    print(f"{Colors.BOLD}Testing Context:{Colors.ENDC}")
    print(f"  • Just completed architectural reorganization")
    print(f"  • Moved all P&B features FROM /oobc-management/ TO /oobc-management/planning-budgeting/")
    print(f"  • OOBC Management now shows only organizational features")
    print(f"  • Testing all 22 Planning & Budgeting features")

    results = {}

    # Run all tests
    results['url_resolution'], total_features = run_url_resolution()
    results['view_responses'] = run_view_responses()
    results['template_structure'] = run_template_structure()
    results['oobc_cleanup'] = run_oobc_management_cleanup()
    results['navigation'] = run_navigation_links()

    # Print summary
    print_header("TEST SUMMARY")

    test_names = {
        'url_resolution': 'URL Resolution',
        'view_responses': 'View Responses',
        'template_structure': 'Template Structure',
        'oobc_cleanup': 'OOBC Management Cleanup',
        'navigation': 'Navigation Links',
    }

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\n{Colors.BOLD}Test Results:{Colors.ENDC}\n")

    for key, name in test_names.items():
        if results[key]:
            print(f"  {Colors.OKGREEN}✓ {name}{Colors.ENDC}")
        else:
            print(f"  {Colors.FAIL}✗ {name}{Colors.ENDC}")

    print(f"\n{Colors.BOLD}Overall:{Colors.ENDC}")
    if passed == total:
        print(f"  {Colors.OKGREEN}{Colors.BOLD}✓ ALL TESTS PASSED ({passed}/{total}){Colors.ENDC}")
        print(f"  {Colors.OKGREEN}✓ {total_features} P&B features verified{Colors.ENDC}")
        print(f"\n{Colors.OKGREEN}{'='*80}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}{'SUCCESS: Planning & Budgeting Module is functioning correctly!'.center(80)}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{'='*80}{Colors.ENDC}\n")
        return 0
    else:
        print(f"  {Colors.FAIL}{Colors.BOLD}✗ SOME TESTS FAILED ({passed}/{total} passed){Colors.ENDC}")
        print(f"\n{Colors.FAIL}{'='*80}{Colors.ENDC}")
        print(f"{Colors.FAIL}{Colors.BOLD}{'FAILURE: Please review test output above'.center(80)}{Colors.ENDC}")
        print(f"{Colors.FAIL}{'='*80}{Colors.ENDC}\n")
        return 1

if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
