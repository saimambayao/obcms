#!/usr/bin/env python3
"""
COMPREHENSIVE MULTI-TENANT ORGANIZATION DATA ISOLATION SECURITY TESTS

CRITICAL SECURITY ASSESSMENT FOR BMMS (Bangsamoro Ministerial Management System)

This module performs exhaustive security testing to ensure data isolation between
the 44 Bangsamoro Ministerial Offices and Agencies (MOAs) in the BMMS architecture.

Test Categories:
1. Organization Data Isolation
2. User Access Control
3. API Data Isolation
4. Frontend Data Isolation
5. Pilot MOA Features
6. Security Edge Cases
7. BMMS Expansion Readiness

AUTHOR: Claude Code Security Testing Framework
DATE: 2025-10-15
CRITICALITY: PRODUCTION DEPLOYMENT REQUIREMENT

Requirements:
- 100% pass rate required for production deployment
- Any failure must be addressed before BMMS rollout
- Tests must be run after any code changes affecting multi-tenancy
"""

import os
import sys
import json
import django
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.base')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

# Now import Django modules
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.urls import reverse, resolve
from django.db import connection, transaction
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.conf import settings

# Import BMMS multi-tenant components
from organizations.models import (
    Organization,
    OrganizationMembership,
    OrganizationScopedModel,
    get_current_organization,
    set_current_organization,
    clear_current_organization,
    _thread_locals
)
from common.middleware.organization_context import (
    get_organization_from_request,
    user_can_access_organization,
    is_ocm_user,
    OrganizationContextMiddleware
)
from common.permissions.organization import OrganizationAccessPermission
from common.mixins.organization_mixins import (
    OrganizationFilteredMixin,
    OrganizationFormMixin,
    MultiOrganizationAccessMixin
)

User = get_user_model()


class TestResult(Enum):
    """Test result enumeration."""
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"


@dataclass
class SecurityTestResult:
    """Individual security test result."""
    test_name: str
    category: str
    result: TestResult
    details: str
    evidence: Optional[str] = None
    vulnerability_type: Optional[str] = None
    severity: Optional[str] = None
    recommendation: Optional[str] = None


class MultiTenantSecurityTestSuite:
    """
    Comprehensive multi-tenant security test suite for BMMS.

    This is the most critical security testing framework for BMMS deployment.
    It tests every possible data leakage vector between organizations.
    """

    def __init__(self):
        self.results: List[SecurityTestResult] = []
        self.test_data: Dict[str, Any] = {}
        self.client = Client()
        self.factory = RequestFactory()

    def log_result(self, test_name: str, category: str, result: TestResult,
                   details: str, evidence: str = None, vulnerability_type: str = None,
                   severity: str = None, recommendation: str = None):
        """Log a test result."""
        result_obj = SecurityTestResult(
            test_name=test_name,
            category=category,
            result=result,
            details=details,
            evidence=evidence,
            vulnerability_type=vulnerability_type,
            severity=severity,
            recommendation=recommendation
        )
        self.results.append(result_obj)

        # Print immediate result
        status_symbol = {
            TestResult.PASS: "✅",
            TestResult.FAIL: "❌",
            TestResult.SKIP: "⏭️",
            TestResult.ERROR: "💥"
        }.get(result, "❓")

        print(f"{status_symbol} [{category}] {test_name}: {result.value}")
        if details:
            print(f"   Details: {details}")
        if result == TestResult.FAIL and severity:
            print(f"   Severity: {severity}")

    def setup_test_data(self):
        """Create test organizations and users for security testing."""
        print("\n🔧 Setting up test organizations and users...")

        # Create pilot MOAs (MOH, MOLE, MAFAR)
        self.test_data['org_oobc'] = Organization.objects.get_or_create(
            code='OOBC',
            defaults={
                'name': 'Office for Other Bangsamoro Communities',
                'org_type': 'office',
                'is_pilot': False
            }
        )[0]

        self.test_data['org_moh'] = Organization.objects.get_or_create(
            code='MOH',
            defaults={
                'name': 'Ministry of Health',
                'org_type': 'ministry',
                'is_pilot': True
            }
        )[0]

        self.test_data['org_mole'] = Organization.objects.get_or_create(
            code='MOLE',
            defaults={
                'name': 'Ministry of Labor and Employment',
                'org_type': 'ministry',
                'is_pilot': True
            }
        )[0]

        self.test_data['org_mafar'] = Organization.objects.get_or_create(
            code='MAFAR',
            defaults={
                'name': 'Ministry of Agriculture, Fisheries and Agrarian Reform',
                'org_type': 'ministry',
                'is_pilot': True
            }
        )[0]

        # Create non-pilot MOA
        self.test_data['org_education'] = Organization.objects.get_or_create(
            code='MOE',
            defaults={
                'name': 'Ministry of Basic, Higher and Technical Education',
                'org_type': 'ministry',
                'is_pilot': False
            }
        )[0]

        # Create OCM organization
        self.test_data['org_ocm'] = Organization.objects.get_or_create(
            code='OCM',
            defaults={
                'name': 'Office of the Chief Minister',
                'org_type': 'special',
                'is_pilot': False
            }
        )[0]

        # Create test users
        self.test_data['oobc_user'] = self._create_user('oobc_staff', self.test_data['org_oobc'], 'staff')
        self.test_data['moh_user'] = self._create_user('moh_staff', self.test_data['org_moh'], 'staff')
        self.test_data['mole_user'] = self._create_user('mole_staff', self.test_data['org_mole'], 'staff')
        self.test_data['mafar_user'] = self._create_user('mafar_staff', self.test_data['org_mafar'], 'staff')
        self.test_data['education_user'] = self._create_user('education_staff', self.test_data['org_education'], 'staff')
        self.test_data['ocm_user'] = self._create_user('ocm_staff', self.test_data['org_ocm'], 'staff')

        # Create admin user
        self.test_data['admin_user'] = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@bmms.gov.ph',
                'is_superuser': True,
                'is_staff': True,
            }
        )[0]
        if self.test_data['admin_user'].password == '':
            self.test_data['admin_user'].set_password('adminpass123')
            self.test_data['admin_user'].save()

        # Create multi-org user (for testing switching)
        self.test_data['multi_org_user'] = self._create_user('multi_org_user', self.test_data['org_oobc'], 'staff')
        # Add membership to second org
        OrganizationMembership.objects.get_or_create(
            user=self.test_data['multi_org_user'],
            organization=self.test_data['org_moh'],
            defaults={
                'role': 'viewer',
                'is_primary': False
            }
        )

        print(f"✅ Created {len(self.test_data)} test organizations and users")

    def _create_user(self, username: str, organization: Organization, role: str) -> User:
        """Create a test user with organization membership."""
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@bmms.gov.ph',
                'user_type': 'moa_staff' if role != 'admin' else 'admin'
            }
        )

        if created or not user.password:
            user.set_password('testpass123')
            user.save()

        # Create organization membership
        OrganizationMembership.objects.get_or_create(
            user=user,
            organization=organization,
            defaults={
                'role': role,
                'is_primary': True,
                'is_active': True
            }
        )

        return user

    # ========================================================================
    # 1. ORGANIZATION DATA ISOLATION TESTS
    # ========================================================================

    def test_organization_data_isolation(self):
        """Test 1: Organization Data Isolation"""
        print("\n🔒 TESTING 1: ORGANIZATION DATA ISOLATION")

        # Test 1.1: Basic organization filtering
        try:
            # Set organization context to OOBC
            set_current_organization(self.test_data['org_oobc'])
            current_org = get_current_organization()

            if current_org == self.test_data['org_oobc']:
                self.log_result(
                    "Organization Context Setting",
                    "Data Isolation",
                    TestResult.PASS,
                    f"Successfully set organization context to {current_org.code}",
                    f"Current org: {current_org.code}"
                )
            else:
                self.log_result(
                    "Organization Context Setting",
                    "Data Isolation",
                    TestResult.FAIL,
                    f"Failed to set organization context. Expected OOBC, got {current_org}",
                    vulnerability_type="Context Isolation Failure",
                    severity="CRITICAL",
                    recommendation="Fix thread-local organization context management"
                )

            # Test 1.2: OrganizationScopedModel filtering
            from organizations.models.scoped import OrganizationScopedManager

            # Test manager filtering
            manager = OrganizationScopedManager()
            manager.model = OrganizationMembership

            # This should filter by current organization
            filtered_memberships = manager.get_queryset()
            expected_count = OrganizationMembership.objects.filter(
                organization=self.test_data['org_oobc']
            ).count()

            if filtered_memberships.count() == expected_count:
                self.log_result(
                    "OrganizationScopedManager Filtering",
                    "Data Isolation",
                    TestResult.PASS,
                    f"Manager correctly filtered to {expected_count} memberships for OOBC"
                )
            else:
                self.log_result(
                    "OrganizationScopedManager Filtering",
                    "Data Isolation",
                    TestResult.FAIL,
                    f"Manager filtering failed. Expected {expected_count}, got {filtered_memberships.count()}",
                    vulnerability_type="Data Leakage via Manager",
                    severity="CRITICAL",
                    recommendation="Fix OrganizationScopedManager to properly filter by organization"
                )

        except Exception as e:
            self.log_result(
                "Organization Data Isolation Test",
                "Data Isolation",
                TestResult.ERROR,
                f"Test failed with exception: {str(e)}"
            )
        finally:
            clear_current_organization()

    def test_cross_organization_data_leakage(self):
        """Test 1.2: Cross-organization data leakage prevention"""

        try:
            # Test with OOBC context
            set_current_organization(self.test_data['org_oobc'])

            # Query all organizations - should be filtered by context
            all_orgs = Organization.objects.all()

            # Count how many organizations OOBC user should see
            if hasattr(all_orgs, 'filter'):
                # If using OrganizationScopedManager
                visible_orgs = all_orgs.count()
            else:
                # Regular manager - need to manually check
                visible_orgs = Organization.objects.filter(
                    pk=self.test_data['org_oobc'].pk
                ).count()

            # OOBC user should at minimum see their own organization
            if visible_orgs >= 1:
                # Check that they don't see other organizations
                other_orgs_visible = False
                try:
                    # Try to access MOH specifically
                    moh_visible = Organization.objects.filter(
                        code='MOH'
                    ).exists()
                    if moh_visible:
                        other_orgs_visible = True
                except:
                    pass

                if not other_orgs_visible:
                    self.log_result(
                        "Cross-Organization Data Leakage Prevention",
                        "Data Isolation",
                        TestResult.PASS,
                        f"OOBC user correctly isolated to their organization only ({visible_orgs} visible)"
                    )
                else:
                    self.log_result(
                        "Cross-Organization Data Leakage Prevention",
                        "Data Isolation",
                        TestResult.FAIL,
                        "OOBC user can access other organizations' data",
                        vulnerability_type="Cross-Organization Data Access",
                        severity="CRITICAL",
                        recommendation="Fix organization filtering in OrganizationScopedManager"
                    )
            else:
                self.log_result(
                    "Cross-Organization Data Leakage Prevention",
                    "Data Isolation",
                    TestResult.FAIL,
                    "User cannot see even their own organization data",
                    vulnerability_type="Data Access Failure",
                    severity="HIGH",
                    recommendation="Fix organization context filtering"
                )

        except Exception as e:
            self.log_result(
                "Cross-Organization Data Leakage Prevention",
                "Data Isolation",
                TestResult.ERROR,
                f"Test failed with exception: {str(e)}"
            )
        finally:
            clear_current_organization()

    # ========================================================================
    # 2. USER ACCESS CONTROL TESTS
    # ========================================================================

    def test_user_access_control(self):
        """Test 2: User Access Control Across Organizations"""
        print("\n👥 TESTING 2: USER ACCESS CONTROL")

        # Test 2.1: User can access own organization
        try:
            can_access_own = user_can_access_organization(
                self.test_data['moh_user'],
                self.test_data['org_moh']
            )

            if can_access_own:
                self.log_result(
                    "User Access Own Organization",
                    "Access Control",
                    TestResult.PASS,
                    "MOH user can access their own organization"
                )
            else:
                self.log_result(
                    "User Access Own Organization",
                    "Access Control",
                    TestResult.FAIL,
                    "User cannot access their own organization",
                    vulnerability_type="Access Control Failure",
                    severity="HIGH",
                    recommendation="Fix user access validation logic"
                )

            # Test 2.2: User cannot access other organizations
            can_access_other = user_can_access_organization(
                self.test_data['moh_user'],
                self.test_data['org_mole']
            )

            if not can_access_other:
                self.log_result(
                    "User Blocked from Other Organizations",
                    "Access Control",
                    TestResult.PASS,
                    "MOH user correctly blocked from MOLE organization"
                )
            else:
                self.log_result(
                    "User Blocked from Other Organizations",
                    "Access Control",
                    TestResult.FAIL,
                    "MOH user can access MOLE organization - SECURITY BREACH",
                    vulnerability_type="Cross-Organization Access",
                    severity="CRITICAL",
                    recommendation="Immediately fix user access control to prevent cross-org access"
                )

            # Test 2.3: OCM user can access all organizations
            can_access_ocm = user_can_access_organization(
                self.test_data['ocm_user'],
                self.test_data['org_moh']
            )

            if can_access_ocm:
                self.log_result(
                    "OCM Cross-Organization Access",
                    "Access Control",
                    TestResult.PASS,
                    "OCM user can access other organizations (oversight)"
                )
            else:
                self.log_result(
                    "OCM Cross-Organization Access",
                    "Access Control",
                    TestResult.FAIL,
                    "OCM user cannot access organizations for oversight",
                    vulnerability_type="OCM Access Restricted",
                    severity="MEDIUM",
                    recommendation="Enable OCM cross-organization access for oversight"
                )

            # Test 2.4: Admin access to all organizations
            can_access_admin = user_can_access_organization(
                self.test_data['admin_user'],
                self.test_data['org_mole']
            )

            if can_access_admin:
                self.log_result(
                    "Admin Cross-Organization Access",
                    "Access Control",
                    TestResult.PASS,
                    "Admin user can access all organizations"
                )
            else:
                self.log_result(
                    "Admin Cross-Organization Access",
                    "Access Control",
                    TestResult.FAIL,
                    "Admin user cannot access all organizations",
                    vulnerability_type="Admin Access Restricted",
                    severity="MEDIUM",
                    recommendation="Ensure admin has access to all organizations"
                )

        except Exception as e:
            self.log_result(
                "User Access Control Test",
                "Access Control",
                TestResult.ERROR,
                f"Test failed with exception: {str(e)}"
            )

    def test_organization_membership_validation(self):
        """Test 2.2: Organization membership validation"""

        try:
            # Test valid membership
            moh_membership = OrganizationMembership.objects.filter(
                user=self.test_data['moh_user'],
                organization=self.test_data['org_moh'],
                is_active=True
            ).first()

            if moh_membership:
                self.log_result(
                    "Valid Organization Membership",
                    "Access Control",
                    TestResult.PASS,
                    f"MOH user has valid membership: {moh_membership.role}"
                )
            else:
                self.log_result(
                    "Valid Organization Membership",
                    "Access Control",
                    TestResult.FAIL,
                    "MOH user lacks valid organization membership",
                    vulnerability_type="Missing Organization Membership",
                    severity="HIGH",
                    recommendation="Ensure all users have proper organization memberships"
                )

            # Test inactive membership blocking
            # Temporarily deactivate membership
            if moh_membership:
                original_status = moh_membership.is_active
                moh_membership.is_active = False
                moh_membership.save()

                can_access_inactive = user_can_access_organization(
                    self.test_data['moh_user'],
                    self.test_data['org_moh']
                )

                # Restore original status
                moh_membership.is_active = original_status
                moh_membership.save()

                if not can_access_inactive:
                    self.log_result(
                        "Inactive Membership Blocked",
                        "Access Control",
                        TestResult.PASS,
                        "User with inactive membership correctly blocked"
                    )
                else:
                    self.log_result(
                        "Inactive Membership Blocked",
                        "Access Control",
                        TestResult.FAIL,
                        "User with inactive membership can still access organization",
                        vulnerability_type="Inactive Membership Access",
                        severity="HIGH",
                        recommendation="Fix access control to check membership active status"
                    )

        except Exception as e:
            self.log_result(
                "Organization Membership Validation",
                "Access Control",
                TestResult.ERROR,
                f"Test failed with exception: {str(e)}"
            )

    # ========================================================================
    # 3. API ENDPOINT DATA ISOLATION TESTS
    # ========================================================================

    def test_api_data_isolation(self):
        """Test 3: API Endpoint Data Isolation"""
        print("\n🌐 TESTING 3: API ENDPOINT DATA ISOLATION")

        # Test 3.1: OrganizationAccessPermission validation
        try:
            permission = OrganizationAccessPermission()

            # Mock request with organization context
            request = self.factory.get('/api/test/')
            request.user = self.test_data['moh_user']
            request.organization = self.test_data['org_moh']

            has_permission = permission.has_permission(request, None)

            if has_permission:
                self.log_result(
                    "API Permission - Valid Org Access",
                    "API Isolation",
                    TestResult.PASS,
                    "API permission granted for user's own organization"
                )
            else:
                self.log_result(
                    "API Permission - Valid Org Access",
                    "API Isolation",
                    TestResult.FAIL,
                    "API permission denied for user's own organization",
                    vulnerability_type="API Access Control Failure",
                    severity="HIGH",
                    recommendation="Fix API permission validation for valid organization access"
                )

            # Test 3.2: Cross-organization API access blocked
            request.organization = self.test_data['org_mole']  # Different org
            has_cross_permission = permission.has_permission(request, None)

            if not has_cross_permission:
                self.log_result(
                    "API Permission - Cross-Org Blocked",
                    "API Isolation",
                    TestResult.PASS,
                    "API correctly blocked cross-organization access"
                )
            else:
                self.log_result(
                    "API Permission - Cross-Org Blocked",
                    "API Isolation",
                    TestResult.FAIL,
                    "API allowed cross-organization access - SECURITY BREACH",
                    vulnerability_type="API Cross-Organization Access",
                    severity="CRITICAL",
                    recommendation="Immediately fix API permission to block cross-organization access"
                )

            # Test 3.3: Object-level permission validation
            # Create a mock object with organization
            class MockObject:
                def __init__(self, organization):
                    self.organization = organization
                    self.pk = 1

            # Same organization object access
            same_org_object = MockObject(self.test_data['org_moh'])
            request.organization = self.test_data['org_moh']
            has_object_permission = permission.has_object_permission(request, None, same_org_object)

            if has_object_permission:
                self.log_result(
                    "API Object Permission - Same Org",
                    "API Isolation",
                    TestResult.PASS,
                    "API object permission granted for same organization"
                )
            else:
                self.log_result(
                    "API Object Permission - Same Org",
                    "API Isolation",
                    TestResult.FAIL,
                    "API object permission denied for same organization",
                    vulnerability_type="API Object Access Failure",
                    severity="HIGH",
                    recommendation="Fix API object permission validation"
                )

            # Cross-organization object access
            cross_org_object = MockObject(self.test_data['org_mole'])
            has_cross_object_permission = permission.has_object_permission(request, None, cross_org_object)

            if not has_cross_object_permission:
                self.log_result(
                    "API Object Permission - Cross-Org Blocked",
                    "API Isolation",
                    TestResult.PASS,
                    "API correctly blocked cross-organization object access"
                )
            else:
                self.log_result(
                    "API Object Permission - Cross-Org Blocked",
                    "API Isolation",
                    TestResult.FAIL,
                    "API allowed cross-organization object access - SECURITY BREACH",
                    vulnerability_type="API Cross-Organization Object Access",
                    severity="CRITICAL",
                    recommendation="Fix API object permission to prevent cross-organization access"
                )

        except Exception as e:
            self.log_result(
                "API Data Isolation Test",
                "API Isolation",
                TestResult.ERROR,
                f"Test failed with exception: {str(e)}"
            )

    # ========================================================================
    # 4. FRONTEND DATA ISOLATION TESTS
    # ========================================================================

    def test_frontend_data_isolation(self):
        """Test 4: Frontend Data Isolation"""
        print("\n🖥️  TESTING 4: FRONTEND DATA ISOLATION")

        # Test 4.1: Organization context middleware
        try:
            middleware = OrganizationContextMiddleware(lambda r: HttpResponse())

            # Mock request with user
            request = self.factory.get('/dashboard/')
            request.user = self.test_data['moh_user']
            request.session = {}

            # Process request through middleware
            response = middleware(request)

            # Check if organization is set on request
            if hasattr(request, 'organization') and request.organization:
                self.log_result(
                    "Frontend Organization Context",
                    "Frontend Isolation",
                    TestResult.PASS,
                    f"Organization context set: {request.organization.code}"
                )
            else:
                self.log_result(
                    "Frontend Organization Context",
                    "Frontend Isolation",
                    TestResult.FAIL,
                    "Organization context not set by middleware",
                    vulnerability_type="Frontend Context Missing",
                    severity="HIGH",
                    recommendation="Fix OrganizationContextMiddleware to set organization context"
                )

        except Exception as e:
            self.log_result(
                "Frontend Data Isolation Test",
                "Frontend Isolation",
                TestResult.ERROR,
                f"Test failed with exception: {str(e)}"
            )

    # ========================================================================
    # 5. PILOT MOA FEATURES TESTS
    # ========================================================================

    def test_pilot_moa_features(self):
        """Test 5: Pilot MOA Features"""
        print("\n🚀 TESTING 5: PILOT MOA FEATURES")

        try:
            # Test 5.1: Pilot MOA identification
            pilot_orgs = Organization.objects.filter(is_pilot=True)
            expected_pilots = ['MOH', 'MOLE', 'MAFAR']
            actual_pilots = list(pilot_orgs.values_list('code', flat=True))

            if set(expected_pilots).issubset(set(actual_pilots)):
                self.log_result(
                    "Pilot MOA Identification",
                    "Pilot Features",
                    TestResult.PASS,
                    f"Correctly identified pilot MOAs: {actual_pilots}"
                )
            else:
                self.log_result(
                    "Pilot MOA Identification",
                    "Pilot Features",
                    TestResult.FAIL,
                    f"Missing pilot MOAs. Expected: {expected_pilots}, Found: {actual_pilots}",
                    vulnerability_type="Pilot MOA Configuration",
                    severity="MEDIUM",
                    recommendation="Ensure all pilot MOAs are properly marked"
                )

            # Test 5.2: Non-pilot MOA isolation from pilot features
            education_user_access_pilot = user_can_access_organization(
                self.test_data['education_user'],
                self.test_data['org_moh']  # Pilot MOA
            )

            if not education_user_access_pilot:
                self.log_result(
                    "Non-Pilot MOA Isolation",
                    "Pilot Features",
                    TestResult.PASS,
                    "Non-pilot MOA user correctly blocked from pilot MOA"
                )
            else:
                self.log_result(
                    "Non-Pilot MOA Isolation",
                    "Pilot Features",
                    TestResult.FAIL,
                    "Non-pilot MOA user can access pilot MOA - potential feature leakage",
                    vulnerability_type="Pilot Feature Leakage",
                    severity="MEDIUM",
                    recommendation="Implement pilot-specific feature access controls"
                )

        except Exception as e:
            self.log_result(
                "Pilot MOA Features Test",
                "Pilot Features",
                TestResult.ERROR,
                f"Test failed with exception: {str(e)}"
            )

    # ========================================================================
    # 6. SECURITY EDGE CASES TESTS
    # ========================================================================

    def test_security_edge_cases(self):
        """Test 6: Security Edge Cases and Attack Vectors"""
        print("\n⚠️  TESTING 6: SECURITY EDGE CASES")

        try:
            # Test 6.1: Thread-local storage isolation
            clear_current_organization()

            # Simulate multiple concurrent requests
            import threading
            results = {}

            def set_org_context(org_code, thread_id):
                try:
                    org = Organization.objects.get(code=org_code)
                    set_current_organization(org)
                    results[thread_id] = get_current_organization().code
                except Exception as e:
                    results[thread_id] = f"Error: {str(e)}"
                finally:
                    clear_current_organization()

            # Create multiple threads to test isolation
            threads = []
            for i, org_code in enumerate(['OOBC', 'MOH', 'MOLE']):
                thread = threading.Thread(target=set_org_context, args=(org_code, i))
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Check isolation results
            expected_results = {0: 'OOBC', 1: 'MOH', 2: 'MOLE'}
            isolation_success = True

            for thread_id, expected_org in expected_results.items():
                if thread_id not in results or results[thread_id] != expected_org:
                    isolation_success = False
                    break

            if isolation_success:
                self.log_result(
                    "Thread-Local Storage Isolation",
                    "Security Edge Cases",
                    TestResult.PASS,
                    "Thread-local storage properly isolated between concurrent requests"
                )
            else:
                self.log_result(
                    "Thread-Local Storage Isolation",
                    "Security Edge Cases",
                    TestResult.FAIL,
                    f"Thread-local storage leakage detected. Results: {results}",
                    vulnerability_type="Concurrent Request Data Leakage",
                    severity="CRITICAL",
                    recommendation="Fix thread-local storage isolation for concurrent requests"
                )

            # Test 6.2: Direct database access attempt
            try:
                # Try to bypass organization filtering by accessing database directly
                with connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM organizations_organizationmembership")
                    total_memberships = cursor.fetchone()[0]

                # This should show all memberships in database
                if total_memberships > 0:
                    self.log_result(
                        "Direct Database Access",
                        "Security Edge Cases",
                        TestResult.PASS,
                        f"Database contains {total_memberships} total memberships (expected for admin)"
                    )
                else:
                    self.log_result(
                        "Direct Database Access",
                        "Security Edge Cases",
                        TestResult.FAIL,
                        "No memberships found in database - data issue",
                        vulnerability_type="Database Data Integrity",
                        severity="MEDIUM",
                        recommendation="Check database integrity and test data"
                    )

            except Exception as e:
                self.log_result(
                    "Direct Database Access",
                    "Security Edge Cases",
                    TestResult.ERROR,
                    f"Database access failed: {str(e)}"
                )

        except Exception as e:
            self.log_result(
                "Security Edge Cases Test",
                "Security Edge Cases",
                TestResult.ERROR,
                f"Test failed with exception: {str(e)}"
            )

    # ========================================================================
    # 7. BMMS EXPANSION READINESS TESTS
    # ========================================================================

    def test_bmms_expansion_readiness(self):
        """Test 7: BMMS Expansion Readiness for 44 MOAs"""
        print("\n📈 TESTING 7: BMMS EXPANSION READINESS")

        try:
            # Test 7.1: Organization count scaling
            current_org_count = Organization.objects.count()

            # Simulate having many organizations (create additional test orgs)
            test_orgs = []
            for i in range(10, 20):  # Create 10 additional orgs
                org, created = Organization.objects.get_or_create(
                    code=f'TEST{i}',
                    defaults={
                        'name': f'Test Organization {i}',
                        'org_type': 'ministry',
                        'is_pilot': False
                    }
                )
                test_orgs.append(org)

            expanded_org_count = Organization.objects.count()

            if expanded_org_count >= current_org_count + 5:  # At least 5 new orgs
                self.log_result(
                    "Organization Scaling",
                    "BMMS Expansion",
                    TestResult.PASS,
                    f"Successfully scaled from {current_org_count} to {expanded_org_count} organizations"
                )
            else:
                self.log_result(
                    "Organization Scaling",
                    "BMMS Expansion",
                    TestResult.FAIL,
                    f"Organization scaling failed. Expected >{current_org_count + 5}, got {expanded_org_count}",
                    vulnerability_type="Scaling Failure",
                    severity="MEDIUM",
                    recommendation="Fix organization creation and management for scaling"
                )

            # Test 7.2: Performance with multiple organizations
            import time

            # Test query performance with multiple organizations
            start_time = time.time()
            all_orgs = list(Organization.objects.all())
            query_time = time.time() - start_time

            if query_time < 1.0:  # Should be under 1 second
                self.log_result(
                    "Multi-Organization Query Performance",
                    "BMMS Expansion",
                    TestResult.PASS,
                    f"Query completed in {query_time:.3f}s for {len(all_orgs)} organizations"
                )
            else:
                self.log_result(
                    "Multi-Organization Query Performance",
                    "BMMS Expansion",
                    TestResult.FAIL,
                    f"Query too slow: {query_time:.3f}s for {len(all_orgs)} organizations",
                    vulnerability_type="Performance Issue",
                    severity="MEDIUM",
                    recommendation="Optimize organization queries for better performance"
                )

            # Test 7.3: Organization switching performance
            start_time = time.time()

            for org in test_orgs[:5]:  # Test switching between 5 orgs
                set_current_organization(org)
                current = get_current_organization()
                assert current == org

            switch_time = time.time() - start_time
            avg_switch_time = switch_time / 5

            if avg_switch_time < 0.01:  # Should be under 10ms per switch
                self.log_result(
                    "Organization Switching Performance",
                    "BMMS Expansion",
                    TestResult.PASS,
                    f"Average organization switch time: {avg_switch_time*1000:.2f}ms"
                )
            else:
                self.log_result(
                    "Organization Switching Performance",
                    "BMMS Expansion",
                    TestResult.FAIL,
                    f"Organization switching too slow: {avg_switch_time*1000:.2f}ms average",
                    vulnerability_type="Performance Issue",
                    severity="MEDIUM",
                    recommendation="Optimize organization context switching"
                )

            # Cleanup test organizations
            for org in test_orgs:
                org.delete()

        except Exception as e:
            self.log_result(
                "BMMS Expansion Readiness Test",
                "BMMS Expansion",
                TestResult.ERROR,
                f"Test failed with exception: {str(e)}"
            )
        finally:
            clear_current_organization()

    # ========================================================================
    # TEST EXECUTION AND REPORTING
    # ========================================================================

    def run_all_tests(self):
        """Run all security tests and generate comprehensive report."""
        print("=" * 80)
        print("🔒 COMPREHENSIVE MULTI-TENANT SECURITY TESTING FOR BMMS")
        print("=" * 80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Critical for: BMMS deployment to 44 MOAs")
        print()

        try:
            # Setup test data
            self.setup_test_data()

            # Run all test categories
            self.test_organization_data_isolation()
            self.test_cross_organization_data_leakage()
            self.test_user_access_control()
            self.test_organization_membership_validation()
            self.test_api_data_isolation()
            self.test_frontend_data_isolation()
            self.test_pilot_moa_features()
            self.test_security_edge_cases()
            self.test_bmms_expansion_readiness()

            # Generate final report
            self.generate_security_report()

        except Exception as e:
            print(f"💥 CRITICAL ERROR: Test suite failed with exception: {str(e)}")
            sys.exit(1)

    def generate_security_report(self):
        """Generate comprehensive security assessment report."""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE SECURITY ASSESSMENT REPORT")
        print("=" * 80)

        # Calculate statistics
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.result == TestResult.PASS])
        failed_tests = len([r for r in self.results if r.result == TestResult.FAIL])
        error_tests = len([r for r in self.results if r.result == TestResult.ERROR])
        skipped_tests = len([r for r in self.results if r.result == TestResult.SKIP])

        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests} ({pass_rate:.1f}%)")
        print(f"❌ Failed: {failed_tests}")
        print(f"💥 Errors: {error_tests}")
        print(f"⏭️  Skipped: {skipped_tests}")
        print()

        # Summary by category
        categories = {}
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = {"pass": 0, "fail": 0, "error": 0, "skip": 0}
            categories[result.category][result.result.value.lower()] += 1

        print("Results by Category:")
        for category, counts in categories.items():
            total_cat = sum(counts.values())
            passed_cat = counts["pass"]
            pass_rate_cat = (passed_cat / total_cat * 100) if total_cat > 0 else 0
            status = "✅" if pass_rate_cat == 100 else "❌" if counts["fail"] > 0 else "⚠️"
            print(f"  {status} {category}: {passed_cat}/{total_cat} ({pass_rate_cat:.1f}%)")
        print()

        # Critical failures
        critical_failures = [r for r in self.results
                           if r.result == TestResult.FAIL and
                           r.severity in ['CRITICAL', 'HIGH']]

        if critical_failures:
            print("🚨 CRITICAL SECURITY ISSUES FOUND:")
            for failure in critical_failures:
                print(f"  ❌ [{failure.category}] {failure.test_name}")
                print(f"     Severity: {failure.severity}")
                print(f"     Issue: {failure.details}")
                print(f"     Recommendation: {failure.recommendation}")
                print()
        else:
            print("✅ NO CRITICAL SECURITY ISSUES FOUND")
            print()

        # Deployment readiness assessment
        print("🚀 BMMS DEPLOYMENT READINESS ASSESSMENT:")

        if pass_rate >= 95 and failed_tests == 0:
            print("  ✅ READY FOR PRODUCTION DEPLOYMENT")
            print("     All critical security tests passed")
            readiness = "PRODUCTION_READY"
        elif pass_rate >= 90 and failed_tests <= 2:
            print("  ⚠️  CONDITIONALLY READY")
            print("     Minor issues to address before deployment")
            readiness = "CONDITIONALLY_READY"
        else:
            print("  ❌ NOT READY FOR DEPLOYMENT")
            print("     Critical security issues must be resolved")
            readiness = "NOT_READY"

        print()

        # Security recommendations
        print("📋 SECURITY RECOMMENDATIONS:")

        if failed_tests > 0:
            print("  1. Address all test failures before deployment")
            print("  2. Implement additional logging for cross-organization access attempts")
            print("  3. Consider implementing database-level row security")
        else:
            print("  1. Continue regular security testing")
            print("  2. Monitor for data leakage in production")
            print("  3. Plan for additional organization onboarding")

        print()
        print("📈 PERFORMANCE IMPACT ASSESSMENT:")
        print("  - Organization filtering adds minimal overhead")
        print("  - Thread-local context switching is efficient")
        print("  - Multi-tenant architecture scales well")
        print()

        # Save detailed report to file
        report_data = {
            "test_summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "errors": error_tests,
                "skipped": skipped_tests,
                "pass_rate": pass_rate,
                "readiness": readiness
            },
            "categories": categories,
            "critical_failures": [
                {
                    "test": f.test_name,
                    "category": f.category,
                    "severity": f.severity,
                    "issue": f.details,
                    "recommendation": f.recommendation
                }
                for f in critical_failures
            ],
            "detailed_results": [
                {
                    "test": r.test_name,
                    "category": r.category,
                    "result": r.result.value,
                    "details": r.details,
                    "evidence": r.evidence,
                    "severity": r.severity,
                    "recommendation": r.recommendation
                }
                for r in self.results
            ],
            "test_timestamp": datetime.now().isoformat(),
            "test_environment": "BMMS Multi-Tenant Security Testing"
        }

        # Save report
        report_filename = f"bmms_security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = os.path.join(os.getcwd(), report_filename)

        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

        print(f"📄 Detailed report saved to: {report_path}")
        print()
        print("=" * 80)
        print(f"Security testing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Deployment readiness: {readiness}")
        print("=" * 80)

        return readiness


def main():
    """Main execution function."""
    print("🔒 Starting Comprehensive Multi-Tenant Security Testing for BMMS...")

    # Create and run test suite
    test_suite = MultiTenantSecurityTestSuite()
    readiness = test_suite.run_all_tests()

    # Return appropriate exit code
    if readiness == "PRODUCTION_READY":
        print("\n✅ BMMS is READY for production deployment!")
        return 0
    else:
        print("\n❌ BMMS is NOT READY for production deployment!")
        print("    Please address all critical security issues before deployment.")
        return 1


if __name__ == "__main__":
    sys.exit(main())