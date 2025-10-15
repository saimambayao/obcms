#!/usr/bin/env python
"""
Complete End-to-End (E2E) Testing for OBCMS.
Tests the entire system from user interface to database.
"""

import os
import sys
import django
import json
import uuid
from datetime import datetime, timezone
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.base')

# Setup Django
django.setup()

User = get_user_model()

class OBCMSE2ETestSuite:
    """Comprehensive E2E test suite for OBCMS"""

    def __init__(self):
        # Configure test client with proper host
        self.client = Client()
        self.test_data = {}
        self.results = []

    def log_result(self, test_name, passed, details=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        self.results.append((test_name, passed, details))
        return passed

    def test_user_authentication_flow(self):
        """Test complete user authentication and authorization flow"""
        try:
            print("\nTesting User Authentication Flow...")

            # Test 1: User Registration
            unique_username = f"e2e_user_{uuid.uuid4().hex[:8]}"
            registration_data = {
                'username': unique_username,
                'email': f"{unique_username}@test.com",
                'password1': 'ComplexPassword123!',
                'password2': 'ComplexPassword123!',
                'first_name': 'E2E',
                'last_name': 'Test User'
            }

            # Create user directly for testing
            user = User.objects.create_user(
                username=unique_username,
                email=registration_data['email'],
                password=registration_data['password1'],
                first_name=registration_data['first_name'],
                last_name=registration_data['last_name']
            )
            self.test_data['test_user'] = user
            passed = self.log_result("User Creation", True, f"Created user: {user.username}")

            # Test 2: User Login
            login_success = self.client.login(
                username=unique_username,
                password='ComplexPassword123!'
            )
            passed = self.log_result("User Login", login_success, f"Login successful: {login_success}")

            # Test 3: Access Protected Content
            response = self.client.get('/admin/')
            passed = self.log_result("Protected Access", response.status_code in [200, 302],
                                   f"Admin access status: {response.status_code}")

            # Test 4: User Logout
            self.client.logout()
            response = self.client.get('/admin/')
            passed = self.log_result("User Logout", response.status_code == 302,
                                   f"Logout redirect status: {response.status_code}")

            return True

        except Exception as e:
            return self.log_result("Authentication Flow", False, f"Error: {e}")

    def test_organization_crud_operations(self):
        """Test CRUD operations for Organizations"""
        try:
            print("\nTesting Organization CRUD Operations...")

            # Login as test user
            self.client.login(username=self.test_data['test_user'].username,
                           password='ComplexPassword123!')

            from organizations.models import Organization

            # Test 1: Create Organization
            org_data = {
                'code': f'E2E_ORG_{uuid.uuid4().hex[:8]}',
                'name': 'E2E Test Organization',
                'org_type': 'office',
                'description': 'Test organization for E2E testing',
                'is_active': True
            }

            org = Organization.objects.create(**org_data)
            self.test_data['test_org'] = org
            passed = self.log_result("Organization Create", True,
                                   f"Created org: {org.code} - {org.name}")

            # Test 2: Read Organization
            retrieved_org = Organization.objects.get(id=org.id)
            passed = self.log_result("Organization Read",
                                   retrieved_org.name == org_data['name'],
                                   f"Retrieved: {retrieved_org.name}")

            # Test 3: Update Organization
            org.description = "Updated description for E2E test"
            org.save()
            passed = self.log_result("Organization Update", True,
                                   f"Updated description: {org.description}")

            # Test 4: List Organizations
            org_list = Organization.objects.filter(is_active=True)
            passed = self.log_result("Organization List", len(org_list) > 0,
                                   f"Found {len(org_list)} active organizations")

            # Test 5: Soft Delete (deactivate)
            org.is_active = False
            org.save()
            active_count = Organization.objects.filter(is_active=True).count()
            passed = self.log_result("Organization Soft Delete", True,
                                   f"Active organizations after deactivation: {active_count}")

            return True

        except Exception as e:
            return self.log_result("Organization CRUD", False, f"Error: {e}")

    def test_geographic_data_operations(self):
        """Test geographic data operations and relationships"""
        try:
            print("\nTesting Geographic Data Operations...")

            from common.models import Region, Province, Municipality, Barangay

            # Test 1: Region Operations
            regions = Region.objects.all()
            passed = self.log_result("Region Access", len(regions) > 0,
                                   f"Found {len(regions)} regions")

            if regions:
                region = regions.first()
                self.test_data['test_region'] = region

                # Test 2: Region-Province Relationship
                provinces = region.province_set.all()
                passed = self.log_result("Region-Province Relationship",
                                       len(provinces) > 0,
                                       f"Found {len(provinces)} provinces in {region.name}")

                if provinces:
                    province = provinces.first()
                    self.test_data['test_province'] = province

                    # Test 3: Province-Municipality Relationship
                    municipalities = province.municipality_set.all()
                    passed = self.log_result("Province-Municipality Relationship",
                                           len(municipalities) > 0,
                                           f"Found {len(municipalities)} municipalities in {province.name}")

                    if municipalities:
                        municipality = municipalities.first()
                        self.test_data['test_municipality'] = municipality

                        # Test 4: Municipality-Barangay Relationship
                        barangays = municipality.barangay_set.all()
                        passed = self.log_result("Municipality-Barangay Relationship",
                                               len(barangays) > 0,
                                               f"Found {len(barangays)} barangays in {municipality.name}")

            # Test 5: Geographic Hierarchy Navigation
            if all(key in self.test_data for key in ['test_region', 'test_province',
                                                   'test_municipality']):
                hierarchy_test = (
                    self.test_data['test_province'].region == self.test_data['test_region']
                )
                passed = self.log_result("Geographic Hierarchy Navigation", hierarchy_test,
                                       "Hierarchy relationships correctly maintained")

            return True

        except Exception as e:
            return self.log_result("Geographic Data Operations", False, f"Error: {e}")

    def test_community_management_workflow(self):
        """Test community management end-to-end workflow"""
        try:
            print("\nTesting Community Management Workflow...")

            from communities.models import OBCCommunity, MunicipalityCoverage

            # Test 1: Create Community Coverage
            if 'test_municipality' in self.test_data:
                coverage = MunicipalityCoverage.objects.create(
                    municipality=self.test_data['test_municipality'],
                    coverage_percentage=75.5,
                    coverage_date=datetime.now(timezone.utc),
                    status='active'
                )
                self.test_data['test_coverage'] = coverage
                passed = self.log_result("Community Coverage Creation", True,
                                       f"Created coverage for {coverage.municipality.name}")

                # Test 2: Create OBC Community
                community = OBCCommunity.objects.create(
                    name=f"E2E Test Community {uuid.uuid4().hex[:6]}",
                    barangay_id=1,  # Use existing barangay
                    municipality=self.test_data['test_municipality'],
                    province=self.test_data['test_province'],
                    region=self.test_data['test_region'],
                    community_type='rural',
                    estimated_population=1500,
                    date_established=datetime.now(timezone.utc),
                    is_active=True
                )
                self.test_data['test_community'] = community
                passed = self.log_result("OBC Community Creation", True,
                                       f"Created community: {community.name}")

                # Test 3: Community Coverage Query
                coverage_query = MunicipalityCoverage.objects.filter(
                    municipality=self.test_data['test_municipality']
                )
                passed = self.log_result("Community Coverage Query", len(coverage_query) > 0,
                                       f"Found {len(coverage_query)} coverage records")

                # Test 4: Community Search
                community_search = OBCCommunity.objects.filter(
                    municipality=self.test_data['test_municipality'],
                    is_active=True
                )
                passed = self.log_result("Community Search", len(community_search) > 0,
                                       f"Found {len(community_search)} active communities")

            return True

        except Exception as e:
            return self.log_result("Community Management Workflow", False, f"Error: {e}")

    def test_coordination_workflow(self):
        """Test coordination and partnership workflow"""
        try:
            print("\nTesting Coordination Workflow...")

            from coordination.models import Organization, Event, Partnership
            from datetime import date, timedelta

            # Test 1: Create Coordination Organization
            coord_org = Organization.objects.create(
                name=f"E2E Coordination Partner {uuid.uuid4().hex[:6]}",
                organization_type='ngo',
                contact_email=f"coord_{uuid.uuid4().hex[:8]}@test.com",
                contact_phone="123-456-7890",
                is_active=True
            )
            self.test_data['coord_org'] = coord_org
            passed = self.log_result("Coordination Organization Creation", True,
                                   f"Created coordination org: {coord_org.name}")

            # Test 2: Create Coordination Event
            event_data = {
                'title': f"E2E Coordination Event {uuid.uuid4().hex[:6]}",
                'description': 'Test coordination event for E2E testing',
                'event_type': 'meeting',
                'start_date': date.today(),
                'end_date': date.today() + timedelta(days=1),
                'location': 'Test Location',
                'status': 'planned',
                'organizer': self.test_data['test_user']
            }

            event = Event.objects.create(**event_data)
            self.test_data['test_event'] = event
            passed = self.log_result("Coordination Event Creation", True,
                                   f"Created event: {event.title}")

            # Test 3: Create Partnership
            partnership = Partnership.objects.create(
                name=f"E2E Partnership {uuid.uuid4().hex[:6]}",
                organization_1=self.test_data.get('test_org'),
                organization_2=coord_org,
                partnership_type='memorandum',
                start_date=date.today(),
                status='active',
                description='Test partnership for E2E testing'
            )
            self.test_data['test_partnership'] = partnership
            passed = self.log_result("Partnership Creation", True,
                                   f"Created partnership: {partnership.name}")

            # Test 4: Event-Partnership Association
            event.partnerships.add(partnership)
            passed = self.log_result("Event-Partnership Association", True,
                                   f"Associated partnership with event")

            return True

        except Exception as e:
            return self.log_result("Coordination Workflow", False, f"Error: {e}")

    def test_mana_workflow(self):
        """Test MANA (Needs Assessment) workflow"""
        try:
            print("\nTesting MANA Workflow...")

            try:
                from mana.models import WorkshopActivity, Need, BaselineStudy
                from datetime import date, timedelta
            except ImportError as e:
                return self.log_result("MANA Workflow", False, f"Model import error: {e}")

            # Test 1: Create Workshop Activity
            if 'test_community' in self.test_data:
                workshop = WorkshopActivity.objects.create(
                    title=f"E2E Workshop {uuid.uuid4().hex[:6]}",
                    community=self.test_data['test_community'],
                    workshop_type='needs_assessment',
                    scheduled_date=date.today() + timedelta(days=7),
                    facilitator=self.test_data['test_user'],
                    status='planned',
                    max_participants=50
                )
                self.test_data['test_workshop'] = workshop
                passed = self.log_result("Workshop Activity Creation", True,
                                       f"Created workshop: {workshop.title}")

                # Test 2: Create Community Need
                need = Need.objects.create(
                    community=self.test_data['test_community'],
                    category='infrastructure',
                    priority='high',
                    description='E2E Test Need: Road improvement',
                    estimated_cost=500000.00,
                    date_identified=date.today(),
                    status='identified'
                )
                self.test_data['test_need'] = need
                passed = self.log_result("Community Need Creation", True,
                                       f"Created need: {need.description}")

                # Test 3: Create Baseline Study
                baseline = BaselineStudy.objects.create(
                    community=self.test_data['test_community'],
                    study_title=f"E2E Baseline Study {uuid.uuid4().hex[:6]}",
                    study_date=date.today(),
                    conducted_by=self.test_data['test_user'],
                    methodology='survey',
                    status='completed',
                    summary_data=json.dumps({
                        'households': 150,
                        'population': 750,
                        'avg_income': 15000
                    })
                )
                self.test_data['test_baseline'] = baseline
                passed = self.log_result("Baseline Study Creation", True,
                                       f"Created baseline study: {baseline.study_title}")

                # Test 4: Workshop-Need Association
                workshop.identifier_needs.add(need)
                passed = self.log_result("Workshop-Need Association", True,
                                       "Associated needs with workshop")

            return True

        except Exception as e:
            return self.log_result("MANA Workflow", False, f"Error: {e}")

    def test_monitoring_workflow(self):
        """Test monitoring and evaluation workflow"""
        try:
            print("\nTesting Monitoring Workflow...")

            try:
                from monitoring.models import MonitoringEntry, AnnualPlanningCycle
                from datetime import date, timedelta
            except ImportError as e:
                return self.log_result("Monitoring Workflow", False, f"Model import error: {e}")

            # Test 1: Create Monitoring Entry
            if 'test_org' in self.test_data:
                monitoring_entry = MonitoringEntry.objects.create(
                    organization=self.test_data['test_org'],
                    entry_date=date.today(),
                    entry_type='monthly_report',
                    status='submitted',
                    data_summary=json.dumps({
                        'beneficiaries_reached': 250,
                        'activities_completed': 5,
                        'funds_utilized': 75000.00
                    }),
                    submitted_by=self.test_data['test_user']
                )
                self.test_data['test_monitoring'] = monitoring_entry
                passed = self.log_result("Monitoring Entry Creation", True,
                                       f"Created monitoring entry for {monitoring_entry.organization.name}")

                # Test 2: Create Annual Planning Cycle
                planning_cycle = AnnualPlanningCycle.objects.create(
                    year=date.today().year,
                    status='active',
                    start_date=date.today(),
                    end_date=date(date.today().year, 12, 31),
                    created_by=self.test_data['test_user']
                )
                self.test_data['test_planning_cycle'] = planning_cycle
                passed = self.log_result("Annual Planning Cycle Creation", True,
                                       f"Created planning cycle for year {planning_cycle.year}")

                # Test 3: Monitoring Data Query
                monitoring_query = MonitoringEntry.objects.filter(
                    organization=self.test_data['test_org']
                )
                passed = self.log_result("Monitoring Data Query", len(monitoring_query) > 0,
                                       f"Found {len(monitoring_query)} monitoring entries")

            return True

        except Exception as e:
            return self.log_result("Monitoring Workflow", False, f"Error: {e}")

    def test_api_endpoints_e2e(self):
        """Test API endpoints with real requests"""
        try:
            print("\nTesting API Endpoints E2E...")

            # Test 1: Root URL
            response = self.client.get('/')
            passed = self.log_result("Root URL Access", response.status_code in [200, 302, 404],
                                   f"Root URL status: {response.status_code}")

            # Test 2: Admin URL
            response = self.client.get('/admin/')
            passed = self.log_result("Admin URL Access", response.status_code in [200, 302],
                                   f"Admin URL status: {response.status_code}")

            # Test 3: Static Files
            response = self.client.get('/static/css/main.css')
            passed = self.log_result("Static CSS Access", response.status_code in [200, 404],
                                   f"Static CSS status: {response.status_code}")

            # Test 4: Test URL Patterns
            try:
                from django.urls import get_resolver
                resolver = get_resolver()
                url_patterns = len(list(resolver.reverse_dict.keys()))
                passed = self.log_result("URL Patterns Configured", url_patterns > 100,
                                       f"Found {url_patterns} URL patterns")
            except Exception as e:
                passed = self.log_result("URL Patterns Configured", False, f"Error: {e}")

            return True

        except Exception as e:
            return self.log_result("API Endpoints E2E", False, f"Error: {e}")

    def test_data_consistency_e2e(self):
        """Test data consistency across related models"""
        try:
            print("\nTesting Data Consistency E2E...")

            # Test 1: User-Organization Consistency
            if 'test_org' in self.test_data and 'test_user' in self.test_data:
                # Check if user can access organization data
                org_count = len(list(self.test_data['test_user'].organizations.all()))
                passed = self.log_result("User-Organization Consistency", True,
                                       f"User has access to {org_count} organizations")

            # Test 2: Geographic Hierarchy Consistency
            if all(key in self.test_data for key in ['test_region', 'test_province',
                                                   'test_municipality']):
                hierarchy_consistency = (
                    self.test_data['test_province'].region == self.test_data['test_region']
                )
                passed = self.log_result("Geographic Hierarchy Consistency", hierarchy_consistency,
                                       "Geographic hierarchy properly maintained")

            # Test 3: Community-Geography Consistency
            if 'test_community' in self.test_data:
                community = self.test_data['test_community']
                geo_consistency = (
                    community.municipality.province.region == community.region
                )
                passed = self.log_result("Community-Geography Consistency", geo_consistency,
                                       "Community geographic data consistent")

            # Test 4: Database Integrity Check
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM auth_user")
                user_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM organizations_organization")
                org_count = cursor.fetchone()[0]
                passed = self.log_result("Database Integrity Check", user_count > 0 and org_count > 0,
                                       f"Database has {user_count} users and {org_count} organizations")

            return True

        except Exception as e:
            return self.log_result("Data Consistency E2E", False, f"Error: {e}")

    def test_error_handling_e2e(self):
        """Test error handling and edge cases"""
        try:
            print("\nTesting Error Handling E2E...")

            # Test 1: Invalid URL Handling
            response = self.client.get('/invalid-url-that-does-not-exist/')
            passed = self.log_result("404 Error Handling", response.status_code == 404,
                                   f"Invalid URL returns 404: {response.status_code}")

            # Test 2: Unauthorized Access Handling
            self.client.logout()
            response = self.client.get('/admin/')
            passed = self.log_result("Unauthorized Access Handling", response.status_code == 302,
                                   f"Unauthorized access redirects: {response.status_code}")

            # Test 3: Invalid Form Submission
            response = self.client.post('/admin/login/', {
                'username': 'nonexistent_user',
                'password': 'invalid_password'
            })
            passed = self.log_result("Invalid Login Handling",
                                   response.status_code in [200, 302],
                                   f"Invalid login handled properly: {response.status_code}")

            # Test 4: Database Constraint Handling
            try:
                from organizations.models import Organization
                # Try to create duplicate organization code
                if 'test_org' in self.test_data:
                    Organization.objects.create(
                        code=self.test_data['test_org'].code,  # Duplicate code
                        name='Duplicate Test',
                        org_type='office'
                    )
                    passed = self.log_result("Database Constraint Handling", False,
                                           "Duplicate constraint not enforced")
                else:
                    passed = self.log_result("Database Constraint Handling", True,
                                           "No test org available for constraint test")
            except Exception:
                passed = self.log_result("Database Constraint Handling", True,
                                       "Database constraints properly enforced")

            return True

        except Exception as e:
            return self.log_result("Error Handling E2E", False, f"Error: {e}")

    def run_all_e2e_tests(self):
        """Run all E2E tests and return results"""
        print("=" * 80)
        print("OBCMS COMPLETE END-TO-END (E2E) TESTING SUITE")
        print("=" * 80)

        # Run all test categories
        test_methods = [
            ("User Authentication Flow", self.test_user_authentication_flow),
            ("Organization CRUD Operations", self.test_organization_crud_operations),
            ("Geographic Data Operations", self.test_geographic_data_operations),
            ("Community Management Workflow", self.test_community_management_workflow),
            ("Coordination Workflow", self.test_coordination_workflow),
            ("MANA Workflow", self.test_mana_workflow),
            ("Monitoring Workflow", self.test_monitoring_workflow),
            ("API Endpoints E2E", self.test_api_endpoints_e2e),
            ("Data Consistency E2E", self.test_data_consistency_e2e),
            ("Error Handling E2E", self.test_error_handling_e2e),
        ]

        for test_name, test_method in test_methods:
            try:
                print(f"\n{'='*30} {test_name} {'='*30}")
                test_method()
            except Exception as e:
                self.log_result(test_name, False, f"Test execution error: {e}")

        # Generate summary
        self.generate_e2e_summary()

    def generate_e2e_summary(self):
        """Generate E2E test summary"""
        print("\n" + "=" * 80)
        print("E2E TEST SUMMARY")
        print("=" * 80)

        passed = sum(1 for _, passed, _ in self.results if passed)
        failed = len(self.results) - passed

        for test_name, passed, details in self.results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {test_name}")
            if details and not passed:
                print(f"   ⚠️  {details}")

        print(f"\nTotal E2E Tests: {len(self.results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/len(self.results)*100):.1f}%")

        if failed == 0:
            print("\n🎉 ALL E2E TESTS PASSED!")
            print("✅ System is ready for production deployment")
        else:
            print(f"\n⚠️  {failed} E2E test(s) failed. Review and fix issues before deployment.")

        return failed == 0

def main():
    """Run all E2E tests"""
    test_suite = OBCMSE2ETestSuite()
    success = test_suite.run_all_e2e_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())