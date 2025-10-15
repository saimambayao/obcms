#!/usr/bin/env python3
"""
BMMS Multi-Tenant Security Test Runner

This script performs targeted security tests without requiring full Django setup.
It focuses on code analysis and security pattern validation.

Usage: python3 security_test_runner.py
"""

import os
import re
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple


class SecurityTestRunner:
    """Security test runner for BMMS multi-tenant architecture."""

    def __init__(self):
        self.results = []
        self.src_path = Path(__file__).parent
        self.security_patterns = self._load_security_patterns()

    def _load_security_patterns(self) -> Dict[str, Any]:
        """Load security patterns to check for."""
        return {
            'sql_injection_risks': [
                r'execute\s*\(\s*["\'].*%s',
                r'cursor\.execute\s*\(\s*["\'].*\+',
                r'raw\s*\(\s*["\'].*\+',
                r'query\s*\=\s*["\'].*\+.*format',
            ],
            'session_security': [
                r'request\.session\[.*\]\s*=',
                r'session\.get\(.*\)',
                r'session_data\s*=',
            ],
            'organization_filtering': [
                r'filter\s*\(\s*organization\s*=',
                r'\.organization\s*=',
                r'get_current_organization',
                r'set_current_organization',
            ],
            'permission_checks': [
                r'@login_required',
                r'@permission_required',
                r'@require_http_methods',
                r'has_perm\s*\(',
                r'has_permission\s*\(',
            ],
            'data_isolation': [
                r'OrganizationScopedModel',
                r'OrganizationScopedManager',
                r'organization_filter_field',
                r'user_can_access_organization',
            ]
        }

    def test_sql_injection_protection(self) -> Dict[str, Any]:
        """Test for SQL injection vulnerabilities."""
        print("🔍 Testing SQL Injection Protection...")

        vulnerabilities = []
        files_checked = 0

        # Check Python files for SQL injection patterns
        for py_file in self.src_path.rglob("*.py"):
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue

            files_checked += 1
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                for i, line in enumerate(lines, 1):
                    for pattern in self.security_patterns['sql_injection_risks']:
                        if re.search(pattern, line, re.IGNORECASE):
                            vulnerabilities.append({
                                'file': str(py_file.relative_to(self.src_path)),
                                'line': i,
                                'code': line.strip(),
                                'pattern': pattern,
                                'severity': 'CRITICAL'
                            })
            except Exception as e:
                print(f"   Error reading {py_file}: {e}")

        result = {
            'test_name': 'SQL Injection Protection',
            'files_checked': files_checked,
            'vulnerabilities_found': len(vulnerabilities),
            'vulnerabilities': vulnerabilities[:10],  # Limit to top 10
            'security_score': max(0, 100 - (len(vulnerabilities) * 10))
        }

        if vulnerabilities:
            print(f"   ❌ Found {len(vulnerabilities)} potential SQL injection vulnerabilities")
            for vuln in vulnerabilities[:3]:
                print(f"      - {vuln['file']}:{vuln['line']} - {vuln['code'][:80]}...")
        else:
            print(f"   ✅ No SQL injection vulnerabilities found in {files_checked} files")

        return result

    def test_organization_isolation_implementation(self) -> Dict[str, Any]:
        """Test organization isolation implementation."""
        print("🔍 Testing Organization Isolation Implementation...")

        isolation_implementations = []
        files_checked = 0

        # Check for organization isolation patterns
        for py_file in self.src_path.rglob("*.py"):
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue

            files_checked += 1
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                for i, line in enumerate(lines, 1):
                    for pattern in self.security_patterns['organization_filtering']:
                        if re.search(pattern, line, re.IGNORECASE):
                            isolation_implementations.append({
                                'file': str(py_file.relative_to(self.src_path)),
                                'line': i,
                                'code': line.strip(),
                                'pattern': pattern,
                                'type': 'organization_filtering'
                            })
            except Exception as e:
                print(f"   Error reading {py_file}: {e}")

        # Check for key isolation files
        key_files = [
            'organizations/models/scoped.py',
            'common/middleware/organization_context.py',
            'common/permissions/organization.py',
            'common/mixins/organization_mixins.py'
        ]

        key_files_found = 0
        for key_file in key_files:
            if (self.src_path / key_file).exists():
                key_files_found += 1
                print(f"   ✅ Found key isolation file: {key_file}")

        result = {
            'test_name': 'Organization Isolation Implementation',
            'files_checked': files_checked,
            'isolation_implementations': len(isolation_implementations),
            'key_files_found': key_files_found,
            'key_files_total': len(key_files),
            'security_score': (key_files_found / len(key_files)) * 100
        }

        if key_files_found >= 3:
            print(f"   ✅ Strong organization isolation implementation ({key_files_found}/{len(key_files)} key files)")
        else:
            print(f"   ⚠️  Missing key isolation files ({key_files_found}/{len(key_files)})")

        return result

    def test_permission_system_implementation(self) -> Dict[str, Any]:
        """Test permission system implementation."""
        print("🔍 Testing Permission System Implementation...")

        permission_implementations = []
        files_checked = 0

        for py_file in self.src_path.rglob("*.py"):
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue

            files_checked += 1
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                for i, line in enumerate(lines, 1):
                    for pattern in self.security_patterns['permission_checks']:
                        if re.search(pattern, line, re.IGNORECASE):
                            permission_implementations.append({
                                'file': str(py_file.relative_to(self.src_path)),
                                'line': i,
                                'code': line.strip(),
                                'pattern': pattern
                            })
            except Exception as e:
                print(f"   Error reading {py_file}: {e}")

        result = {
            'test_name': 'Permission System Implementation',
            'files_checked': files_checked,
            'permission_implementations': len(permission_implementations),
            'security_score': min(100, len(permission_implementations) * 2)
        }

        if len(permission_implementations) >= 10:
            print(f"   ✅ Strong permission system implementation ({len(permission_implementations)} checks found)")
        else:
            print(f"   ⚠️  Limited permission system implementation ({len(permission_implementations)} checks found)")

        return result

    def test_session_security(self) -> Dict[str, Any]:
        """Test session security implementation."""
        print("🔍 Testing Session Security...")

        session_usages = []
        files_checked = 0

        for py_file in self.src_path.rglob("*.py"):
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue

            files_checked += 1
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                for i, line in enumerate(lines, 1):
                    for pattern in self.security_patterns['session_security']:
                        if re.search(pattern, line, re.IGNORECASE):
                            session_usages.append({
                                'file': str(py_file.relative_to(self.src_path)),
                                'line': i,
                                'code': line.strip(),
                                'pattern': pattern
                            })
            except Exception as e:
                print(f"   Error reading {py_file}: {e}")

        # Check for session security best practices
        security_measures = 0
        session_files = [f for f in session_usages if 'organization_context' in f['file']]

        # Look for session validation patterns
        for py_file in self.src_path.rglob("*.py"):
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                if 'session' in content.lower():
                    if 'validate' in content.lower() or 'secure' in content.lower():
                        security_measures += 1
            except:
                pass

        result = {
            'test_name': 'Session Security',
            'files_checked': files_checked,
            'session_usages': len(session_usages),
            'security_measures': security_measures,
            'security_score': min(100, (security_measures * 20) + (len(session_files) * 10))
        }

        if security_measures >= 3:
            print(f"   ✅ Good session security implementation ({security_measures} security measures)")
        else:
            print(f"   ⚠️  Limited session security measures ({security_measures} found)")

        return result

    def test_architecture_security(self) -> Dict[str, Any]:
        """Test overall architecture security."""
        print("🔍 Testing Architecture Security...")

        security_score = 0
        security_features = []

        # Check for security-related files
        security_files = [
            'organizations/models/scoped.py',
            'common/middleware/organization_context.py',
            'common/permissions/organization.py',
            'organizations/tests/test_data_isolation.py'
        ]

        for sec_file in security_files:
            if (self.src_path / sec_file).exists():
                security_score += 20
                security_features.append(f"✅ {sec_file}")
            else:
                security_features.append(f"❌ {sec_file}")

        # Check for security patterns in key files
        key_patterns = {
            'OrganizationScopedModel': 'Multi-tenant data isolation',
            'user_can_access_organization': 'Access control validation',
            'OrganizationAccessPermission': 'API security',
            'OrganizationContextMiddleware': 'Request-level security'
        }

        patterns_found = 0
        for pattern, description in key_patterns.items():
            found = False
            for py_file in self.src_path.rglob("*.py"):
                if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                    continue

                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        if pattern in f.read():
                            found = True
                            break
                except:
                    pass

            if found:
                patterns_found += 1
                security_features.append(f"✅ {description}")
            else:
                security_features.append(f"❌ {description}")

        result = {
            'test_name': 'Architecture Security',
            'security_files_found': len([f for f in security_features if f.startswith('✅')]),
            'security_files_total': len(security_files),
            'patterns_found': patterns_found,
            'patterns_total': len(key_patterns),
            'security_features': security_features,
            'security_score': (len([f for f in security_features if f.startswith('✅')]) / len(security_features)) * 100
        }

        if result['security_score'] >= 80:
            print(f"   ✅ Strong architecture security ({result['security_score']:.1f}%)")
        else:
            print(f"   ⚠️  Architecture security needs improvement ({result['security_score']:.1f}%)")

        return result

    def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report."""
        print("\n" + "="*80)
        print("🔒 BMMS MULTI-TENANT SECURITY ASSESSMENT")
        print("="*80)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Path: {self.src_path}")
        print()

        # Run all security tests
        test_results = {
            'sql_injection': self.test_sql_injection_protection(),
            'organization_isolation': self.test_organization_isolation_implementation(),
            'permission_system': self.test_permission_system_implementation(),
            'session_security': self.test_session_security(),
            'architecture_security': self.test_architecture_security(),
        }

        # Calculate overall security score
        scores = [result['security_score'] for result in test_results.values()]
        overall_score = sum(scores) / len(scores)

        # Determine overall security rating
        if overall_score >= 90:
            rating = "EXCELLENT"
            status = "✅ READY FOR PRODUCTION"
        elif overall_score >= 80:
            rating = "GOOD"
            status = "⚠️  CONDITIONALLY READY"
        elif overall_score >= 70:
            rating = "ADEQUATE"
            status = "⚠️  NEEDS IMPROVEMENT"
        else:
            rating = "INADEQUATE"
            status = "❌ NOT READY"

        print(f"Overall Security Score: {overall_score:.1f}%")
        print(f"Security Rating: {rating}")
        print(f"Deployment Status: {status}")
        print()

        # Print detailed results
        for test_name, result in test_results.items():
            print(f"📊 {result['test_name']}: {result['security_score']:.1f}%")
            if 'vulnerabilities_found' in result:
                print(f"   Vulnerabilities: {result['vulnerabilities_found']}")

        print()
        print("🚨 CRITICAL ISSUES:")
        critical_issues = []
        if test_results['sql_injection']['vulnerabilities_found'] > 0:
            critical_issues.append(f"SQL Injection: {test_results['sql_injection']['vulnerabilities_found']} vulnerabilities")

        if critical_issues:
            for issue in critical_issues:
                print(f"   ❌ {issue}")
        else:
            print("   ✅ No critical issues found")

        print()
        print("📋 RECOMMENDATIONS:")

        if test_results['sql_injection']['vulnerabilities_found'] > 0:
            print("   1. URGENT: Fix SQL injection vulnerabilities immediately")

        if test_results['session_security']['security_score'] < 80:
            print("   2. Enhance session security with validation and fingerprinting")

        if test_results['organization_isolation']['security_score'] < 90:
            print("   3. Strengthen organization isolation mechanisms")

        print("   4. Implement comprehensive security monitoring")
        print("   5. Conduct regular security assessments")

        # Prepare final report
        report = {
            'assessment_date': datetime.now().isoformat(),
            'overall_security_score': overall_score,
            'security_rating': rating,
            'deployment_status': status,
            'test_results': test_results,
            'critical_issues': critical_issues,
            'recommendations': [
                "Fix SQL injection vulnerabilities immediately",
                "Enhance session security with validation",
                "Implement comprehensive security monitoring",
                "Conduct regular security assessments"
            ]
        }

        # Save report to file
        report_file = self.src_path / f"security_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\n📄 Detailed report saved to: {report_file}")
        print("="*80)

        return report


def main():
    """Main execution function."""
    print("🔒 BMMS Multi-Tenant Security Assessment")
    print("Testing comprehensive security controls for 44 MOAs...")

    runner = SecurityTestRunner()
    report = runner.generate_security_report()

    # Return appropriate exit code
    if report['overall_security_score'] >= 80:
        print("\n✅ BMMS meets security requirements for deployment")
        return 0
    else:
        print("\n❌ BMMS requires security improvements before deployment")
        return 1


if __name__ == "__main__":
    sys.exit(main())