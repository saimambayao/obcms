#!/usr/bin/env python
"""
Simplified API Security Test Runner for OBCMS/BMMS

This script runs comprehensive API security tests and generates a detailed report.
"""

import os
import sys
import json
import subprocess
from datetime import datetime

def main():
    """Run the API security tests using Django's test runner"""
    print("🚀 Starting API Security and Integration Testing")
    print(f"📅 Test started at: {datetime.now().isoformat()}")

    # Change to the src directory
    src_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(src_dir)

    # Create test report directory
    report_dir = os.path.join(src_dir, 'test_reports')
    os.makedirs(report_dir, exist_ok=True)

    # Test categories and corresponding test commands
    test_categories = [
        {
            'name': 'Authentication System',
            'description': 'JWT tokens, login/logout, session management',
            'tests': [
                'test_api_endpoints.AuthenticationTests.test_jwt_token_obtain',
                'test_api_endpoints.AuthenticationTests.test_jwt_token_refresh',
                'test_api_endpoints.AuthenticationTests.test_login_flow',
                'test_api_endpoints.AuthenticationTests.test_logout_flow',
                'test_api_endpoints.AuthenticationTests.test_invalid_credentials',
            ]
        },
        {
            'name': 'RBAC Permission System',
            'description': 'Role-based access control, organization permissions',
            'tests': [
                'test_api_endpoints.RBACTests.test_superuser_full_access',
                'test_api_endpoints.RBACTests.test_oobc_multi_organization_access',
                'test_api_endpoints.RBACTests.test_moa_single_organization_access',
                'test_api_endpoints.RBACTests.test_organization_switching_permissions',
                'test_api_endpoints.RBACTests.test_permission_inheritance',
            ]
        },
        {
            'name': 'API Endpoint Security',
            'description': 'API endpoints across all apps',
            'tests': [
                'test_api_endpoints.APITests.test_common_api_endpoints',
                'test_api_endpoints.APITests.test_communities_api_endpoints',
                'test_api_endpoints.APITests.test_mana_api_endpoints',
                'test_api_endpoints.APITests.test_coordination_api_endpoints',
                'test_api_endpoints.APITests.test_policies_api_endpoints',
            ]
        },
        {
            'name': 'Data Isolation',
            'description': 'Organization-based data isolation',
            'tests': [
                'test_api_endpoints.DataIsolationTests.test_moa_cross_organization_prevention',
                'test_api_endpoints.DataIsolationTests.test_oobc_cross_organization_access',
                'test_api_endpoints.DataIsolationTests.test_data_scoping_by_organization',
                'test_api_endpoints.DataIsolationTests.test_sensitive_data_protection',
            ]
        },
        {
            'name': 'Security Features',
            'description': 'CSRF, rate limiting, input validation',
            'tests': [
                'test_api_endpoints.SecurityTests.test_csrf_protection',
                'test_api_endpoints.SecurityTests.test_rate_limiting',
                'test_api_endpoints.SecurityTests.test_input_validation',
                'test_api_endpoints.SecurityTests.test_sql_injection_protection',
                'test_api_endpoints.SecurityTests.test_xss_protection',
            ]
        },
        {
            'name': 'Multi-Tenant Behavior',
            'description': 'BMMS multi-tenant architecture',
            'tests': [
                'test_api_endpoints.MultiTenantTests.test_organization_context_middleware',
                'test_api_endpoints.MultiTenantTests.test_ocm_readonly_aggregation',
                'test_api_endpoints.MultiTenantTests.test_tenant_data_isolation',
                'test_api_endpoints.MultiTenantTests.test_cross_tenant_access_prevention',
            ]
        }
    ]

    # Initialize results
    test_results = {
        'test_summary': {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'info': 0,
            'success_rate': 0,
            'timestamp': datetime.now().isoformat()
        },
        'test_categories': [],
        'test_environment': {
            'base_url': 'http://localhost:8000',
            'django_settings': 'obc_management.settings.development',
        }
    }

    print("\n" + "="*80)
    print("COMPREHENSIVE API SECURITY TESTING")
    print("="*80)

    total_passed = 0
    total_failed = 0
    total_tests = 0

    for category in test_categories:
        print(f"\n🔸 Testing {category['name']}")
        print(f"   {category['description']}")

        category_results = {
            'name': category['name'],
            'description': category['description'],
            'tests': [],
            'passed': 0,
            'failed': 0,
            'total': len(category['tests'])
        }

        for test_method in category['tests']:
            total_tests += 1

            # Run the test using Django's test runner
            try:
                cmd = [
                    'python', 'manage.py', 'test',
                    f'--verbosity=2',
                    f'--keepdb',
                    test_method
                ]

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60  # 60 second timeout per test
                )

                if result.returncode == 0:
                    status = "PASS"
                    total_passed += 1
                    category_results['passed'] += 1
                    print(f"   ✅ {test_method.split('.')[-1]}: PASSED")
                else:
                    status = "FAIL"
                    total_failed += 1
                    category_results['failed'] += 1
                    print(f"   ❌ {test_method.split('.')[-1]}: FAILED")
                    if "FAILED" in result.stdout:
                        # Extract failure reason
                        lines = result.stdout.split('\n')
                        for line in lines:
                            if 'FAILED' in line and 'assert' in line.lower():
                                print(f"      Reason: {line.strip()}")
                                break

                category_results['tests'].append({
                    'name': test_method,
                    'status': status,
                    'output': result.stdout,
                    'error': result.stderr if result.returncode != 0 else None
                })

            except subprocess.TimeoutExpired:
                status = "FAIL"
                total_failed += 1
                category_results['failed'] += 1
                print(f"   ❌ {test_method.split('.')[-1]}: TIMEOUT")
                category_results['tests'].append({
                    'name': test_method,
                    'status': status,
                    'error': 'Test timed out after 60 seconds'
                })

            except Exception as e:
                status = "FAIL"
                total_failed += 1
                category_results['failed'] += 1
                print(f"   ❌ {test_method.split('.')[-1]}: ERROR - {str(e)}")
                category_results['tests'].append({
                    'name': test_method,
                    'status': status,
                    'error': str(e)
                })

        test_results['test_categories'].append(category_results)

        # Print category summary
        category_success_rate = (category_results['passed'] / category_results['total']) * 100
        print(f"   📊 Category Summary: {category_results['passed']}/{category_results['total']} passed ({category_success_rate:.1f}%)")

    # Update summary
    test_results['test_summary'].update({
        'total_tests': total_tests,
        'passed': total_passed,
        'failed': total_failed,
        'success_rate': (total_passed / total_tests * 100) if total_tests > 0 else 0
    })

    # Generate comprehensive report
    print("\n" + "="*80)
    print("API SECURITY TEST REPORT")
    print("="*80)

    print(f"\n📊 OVERALL SUMMARY:")
    print(f"   Total Tests: {total_tests}")
    print(f"   ✅ Passed: {total_passed}")
    print(f"   ❌ Failed: {total_failed}")
    print(f"   Success Rate: {test_results['test_summary']['success_rate']:.1f}%")

    print(f"\n📋 RESULTS BY CATEGORY:")
    for category in test_results['test_categories']:
        success_rate = (category['passed'] / category['total']) * 100
        status_icon = "✅" if success_rate == 100 else "⚠️" if success_rate >= 80 else "❌"
        print(f"   {status_icon} {category['name']}: {category['passed']}/{category['total']} ({success_rate:.1f}%)")

    # Security assessment
    print(f"\n🔒 SECURITY ASSESSMENT:")

    auth_results = next((c for c in test_results['test_categories'] if 'Authentication' in c['name']), None)
    rbac_results = next((c for c in test_results['test_categories'] if 'RBAC' in c['name']), None)
    isolation_results = next((c for c in test_results['test_categories'] if 'Data Isolation' in c['name']), None)
    security_results = next((c for c in test_results['test_categories'] if 'Security' in c['name']), None)

    auth_status = "✅ Robust" if auth_results and auth_results['failed'] == 0 else "⚠️ Needs attention"
    rbac_status = "✅ Working" if rbac_results and rbac_results['failed'] == 0 else "⚠️ Issues found"
    isolation_status = "✅ Effective" if isolation_results and isolation_results['failed'] == 0 else "⚠️ Vulnerabilities"
    security_status = "✅ Adequate" if security_results and security_results['failed'] <= 1 else "⚠️ Improvements needed"

    print(f"   Authentication System: {auth_status}")
    print(f"   RBAC Implementation: {rbac_status}")
    print(f"   Data Isolation: {isolation_status}")
    print(f"   API Security: {security_status}")

    # Recommendations
    print(f"\n🎯 SECURITY RECOMMENDATIONS:")

    if total_failed > 0:
        print(f"   1. 🚨 CRITICAL: Address {total_failed} failed tests immediately")

    critical_categories = [c for c in test_results['test_categories'] if c['failed'] > 0]
    for category in critical_categories:
        if category['failed'] >= 2:
            print(f"   2. 📋 Review {category['name']} - {category['failed']} failures found")

    print(f"   3. 🔍 Implement continuous API security monitoring")
    print(f"   4. 🛡️ Set up automated security alerts for suspicious activity")
    print(f"   5. 📊 Regular penetration testing for API endpoints")
    print(f"   6. 🔐 Monitor RBAC permission changes and access patterns")

    # Export detailed report
    report_path = os.path.join(report_dir, f'api_security_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    try:
        with open(report_path, 'w') as f:
            json.dump(test_results, f, indent=2, default=str)
        print(f"\n📄 Detailed report exported to: {report_path}")
    except Exception as e:
        print(f"\n⚠️ Could not export report: {e}")

    # Return exit code based on results
    if total_failed == 0:
        print(f"\n🎉 ALL SECURITY TESTS PASSED!")
        print(f"✅ API endpoints are secure and properly configured")
        return 0
    else:
        print(f"\n⚠️ {total_failed} TESTS FAILED - REVIEW REQUIRED")
        print(f"🔧 Address security issues before production deployment")
        return 1

if __name__ == "__main__":
    sys.exit(main())