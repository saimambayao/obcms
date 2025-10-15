#!/usr/bin/env python3
"""
Test authenticated access to Planning & Budgeting pages
Verifies actual page rendering with login
"""

import os
import sys

import pytest

try:
    import django
except ImportError:  # pragma: no cover - handled via skip
    pytest.skip(
        "Django is required for authenticated access script",
        allow_module_level=True,
    )

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_section(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BLUE}{'-'*len(text)}{Colors.END}")

def print_result(name, passed, details=""):
    symbol = "✓" if passed else "✗"
    color = Colors.GREEN if passed else Colors.RED
    print(f"{color}{symbol} {name}{Colors.END}")
    if details:
        print(f"  {Colors.YELLOW}{details}{Colors.END}")

def main():
    print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}AUTHENTICATED ACCESS TEST - Planning & Budgeting Module{Colors.END}")
    print(f"{Colors.BOLD}{'='*80}{Colors.END}")

    # Get admin user
    admin_user = User.objects.filter(is_staff=True, is_active=True).first()
    if not admin_user:
        print(f"{Colors.RED}✗ No admin user found{Colors.END}")
        return False

    print(f"\n{Colors.GREEN}✓ Using admin user: {admin_user.username}{Colors.END}")

    # Create authenticated client
    client = Client()
    client.force_login(admin_user)

    all_passed = True

    # Test 1: OOBC Management Home
    print_section("Test 1: OOBC Management Home Page")

    try:
        response = client.get('/oobc-management/')

        if response.status_code == 200:
            content = response.content.decode('utf-8')

            # Check for key elements
            checks = {
                "Planning & Budgeting Hub link": 'Planning & Budgeting' in content,
                "Organizational Management section": 'Organizational Management' in content,
                "OOBC Calendar card": 'OOBC Calendar' in content,
                "Staff Management card": 'Staff Management' in content,
                "User Approvals card": 'User Approvals' in content,
                "No Phase sections (cleaned up)": 'Phase 4:' not in content and 'Phase 5:' not in content,
            }

            for check_name, result in checks.items():
                print_result(check_name, result)
                if not result:
                    all_passed = False

            print(f"\n  {Colors.YELLOW}Content size: {len(content):,} bytes{Colors.END}")
            print(f"  {Colors.YELLOW}Status: HTTP {response.status_code}{Colors.END}")
        else:
            print_result("OOBC Management page loads", False, f"HTTP {response.status_code}")
            all_passed = False

    except Exception as e:
        print_result("OOBC Management page access", False, str(e))
        all_passed = False

    # Test 2: Planning & Budgeting Page
    print_section("Test 2: Planning & Budgeting Page")

    try:
        response = client.get('/oobc-management/planning-budgeting/')

        if response.status_code == 200:
            content = response.content.decode('utf-8')

            # Check for P&B feature sections
            checks = {
                "Page loads successfully": True,
                "Frequently Used section": 'Frequently Used' in content,
                "Participatory Budgeting section": 'Participatory Budgeting' in content,
                "Strategic Planning section": 'Strategic Planning' in content,
                "Scenario Planning section": 'Scenario Planning' in content,
                "Analytics & Forecasting section": 'Analytics & Forecasting' in content,
                "Gap Analysis card": 'Gap Analysis' in content,
                "Community Voting card": 'Community Voting' in content,
                "Strategic Goals card": 'Strategic Goals' in content,
                "Budget Scenarios card": 'Budget Scenarios' in content,
                "Analytics Dashboard card": 'Analytics Dashboard' in content,
            }

            feature_count = 0
            for check_name, result in checks.items():
                print_result(check_name, result)
                if result and check_name != "Page loads successfully":
                    feature_count += 1
                if not result:
                    all_passed = False

            print(f"\n  {Colors.GREEN}✓ {feature_count} P&B sections/features found{Colors.END}")
            print(f"  {Colors.YELLOW}Content size: {len(content):,} bytes{Colors.END}")
            print(f"  {Colors.YELLOW}Status: HTTP {response.status_code}{Colors.END}")
        else:
            print_result("Planning & Budgeting page loads", False, f"HTTP {response.status_code}")
            all_passed = False

    except Exception as e:
        print_result("Planning & Budgeting page access", False, str(e))
        all_passed = False

    # Test 3: Sample P&B Feature Page
    print_section("Test 3: Sample P&B Feature (Gap Analysis)")

    try:
        response = client.get('/oobc-management/gap-analysis/')

        if response.status_code == 200:
            print_result("Gap Analysis page loads", True, f"HTTP {response.status_code}")
        else:
            print_result("Gap Analysis page loads", False, f"HTTP {response.status_code}")
            all_passed = False

    except Exception as e:
        print_result("Gap Analysis page access", False, str(e))
        all_passed = False

    # Summary
    print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}SUMMARY{Colors.END}")
    print(f"{Colors.BOLD}{'='*80}{Colors.END}\n")

    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL AUTHENTICATED TESTS PASSED{Colors.END}")
        print(f"{Colors.GREEN}  • OOBC Management page renders correctly{Colors.END}")
        print(f"{Colors.GREEN}  • Planning & Budgeting page has all sections{Colors.END}")
        print(f"{Colors.GREEN}  • P&B features are accessible{Colors.END}")
        print(f"{Colors.GREEN}  • Architecture reorganization successful{Colors.END}\n")
        return True
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.END}")
        print(f"{Colors.YELLOW}Review the output above for details{Colors.END}\n")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
