#!/usr/bin/env python
"""
Comprehensive View and API Testing Suite for OBCMS
Tests all view classes, functions, API endpoints, and URL routing configurations
"""

import os
import sys
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Add the src directory to Python path
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings')

import django
django.setup()

from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

User = get_user_model()

class ViewTestResult:
    """Container for view test results"""
    def __init__(self, name: str, view_type: str):
        self.name = name
        self.view_type = view_type
        self.import_success = False
        self.import_error = None
        self.url_found = False
        self.url_patterns = []
        self.methods_tested = []
        self.methods_passed = []
        self.methods_failed = []
        self.permissions_checked = []
        self.templates_found = []
        self.context_data = {}
        self.api_endpoints = []
        self.api_responses = {}
        self.errors = []

class ComprehensiveViewTester:
    """Comprehensive view and API testing class"""

    def __init__(self):
        self.results = {}
        self.client = Client()
        self.api_client = APIClient()
        self.test_user = None
        self.setup_test_user()

    def setup_test_user(self):
        """Create a test user for authentication"""
        try:
            self.test_user = User.objects.create_user(
                username='testviewuser',
                email='test@example.com',
                password='testpass123'
            )
            self.client.login(username='testviewuser', password='testpass123')
            self.api_client.force_authenticate(user=self.test_user)
        except Exception as e:
            print(f"Warning: Could not create test user: {e}")

    def test_view_import(self, module_path: str, view_name: str) -> ViewTestResult:
        """Test importing a view class or function"""
        result = ViewTestResult(view_name, "Unknown")

        try:
            # Import the module
            module = importlib.import_module(module_path)

            # Get the view class/function
            view = getattr(module, view_name)

            # Determine view type
            if inspect.isclass(view):
                if hasattr(view, 'as_view'):
                    result.view_type = "Class-Based View"
                    if hasattr(view, 'queryset') or hasattr(view, 'serializer_class'):
                        result.view_type = "DRF ViewSet/APIView"
                else:
                    result.view_type = "Class"
            elif inspect.isfunction(view):
                result.view_type = "Function-Based View"

            result.import_success = True

            # Test view methods if class-based
            if inspect.isclass(view) and hasattr(view, 'as_view'):
                self.test_class_based_view_methods(view, result)

        except ImportError as e:
            result.import_error = str(e)
            result.errors.append(f"Import error: {e}")
        except AttributeError as e:
            result.import_error = str(e)
            result.errors.append(f"Attribute error: {e}")
        except Exception as e:
            result.import_error = str(e)
            result.errors.append(f"Unexpected error: {e}")

        return result

    def test_class_based_view_methods(self, view_class, result):
        """Test methods of a class-based view"""
        common_methods = ['get', 'post', 'put', 'patch', 'delete', 'get_queryset',
                         'get_context_data', 'get_object', 'form_valid']

        for method_name in common_methods:
            if hasattr(view_class, method_name):
                result.methods_tested.append(method_name)
                try:
                    method = getattr(view_class, method_name)
                    if callable(method):
                        # Basic method validation
                        result.methods_passed.append(method_name)
                    else:
                        result.methods_failed.append(method_name)
                except Exception as e:
                    result.methods_failed.append(method_name)
                    result.errors.append(f"Method {method_name} error: {e}")

    def test_url_routing(self, view_name: str, url_patterns: List[str]) -> ViewTestResult:
        """Test URL routing for a view"""
        result = ViewTestResult(view_name, "URL Routing Test")

        for pattern in url_patterns:
            try:
                # Try to resolve the URL pattern
                if pattern.startswith('/'):
                    pattern = pattern[1:]  # Remove leading slash

                resolved = resolve(pattern)
                result.url_found = True
                result.url_patterns.append(pattern)

                # Check if view name matches
                if hasattr(resolved.func, '__name__'):
                    if resolved.func.__name__ == view_name or view_name in str(resolved.func):
                        result.url_found = True

            except Exception as e:
                result.errors.append(f"URL pattern '{pattern}' error: {e}")

        return result

    def test_api_endpoint(self, endpoint_name: str, url: str, methods: List[str] = None) -> ViewTestResult:
        """Test API endpoint functionality"""
        if methods is None:
            methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']

        result = ViewTestResult(endpoint_name, "API Endpoint")
        result.api_endpoints.append(url)

        for method in methods:
            try:
                if method == 'GET':
                    response = self.api_client.get(url)
                elif method == 'POST':
                    response = self.api_client.post(url, {})
                elif method == 'PUT':
                    response = self.api_client.put(url, {})
                elif method == 'PATCH':
                    response = self.api_client.patch(url, {})
                elif method == 'DELETE':
                    response = self.api_client.delete(url)

                result.api_responses[method] = {
                    'status_code': response.status_code,
                    'content_type': response.get('Content-Type', ''),
                    'has_data': bool(response.data) if hasattr(response, 'data') else False
                }

            except Exception as e:
                result.errors.append(f"API {method} {url} error: {e}")

        return result

    def scan_and_test_views(self):
        """Scan and test all views in the project"""
        print("=" * 80)
        print("COMPREHENSIVE VIEW AND API TESTING SUITE")
        print("=" * 80)

        # Define view modules and their views
        view_modules = {
            'common.views': [
                'DashboardView', 'SearchView', 'UnifiedSearchView', 'HealthCheckView',
                'LoginView', 'LogoutView', 'ProfileView', 'RegisterView'
            ],
            'common.views.auth': [
                'LoginView', 'LogoutView', 'RegisterView', 'ProfileView',
                'PasswordChangeView', 'PasswordResetView'
            ],
            'common.views.dashboard': [
                'DashboardView', 'DashboardAPIView'
            ],
            'common.views.search': [
                'SearchView', 'UnifiedSearchView', 'SearchAPIView'
            ],
            'common.views.calendar': [
                'CalendarView', 'CalendarAPIView'
            ],
            'communities.views': [
                'CommunityListView', 'CommunityDetailView', 'CommunityCreateView',
                'CommunityUpdateView', 'CommunityDeleteView'
            ],
            'communities.api.viewsets': [
                'CommunityViewSet', 'BarangayViewSet', 'MunicipalityViewSet',
                'ProvinceViewSet', 'RegionViewSet'
            ],
            'mana.views': [
                'AssessmentListView', 'AssessmentDetailView', 'AssessmentCreateView',
                'AssessmentUpdateView', 'MonitoringListView', 'MonitoringDetailView'
            ],
            'mana.api_views': [
                'AssessmentViewSet', 'MonitoringViewSet', 'FacilitatorViewSet',
                'ParticipantViewSet'
            ],
            'coordination.views': [
                'CoordinationListView', 'CoordinationDetailView', 'PartnershipListView',
                'PartnershipDetailView', 'MeetingListView', 'MeetingDetailView'
            ],
            'coordination.api_views': [
                'CoordinationViewSet', 'PartnershipViewSet', 'MeetingViewSet'
            ],
            'organizations.views': [
                'OrganizationListView', 'OrganizationDetailView', 'OrganizationCreateView',
                'OrganizationUpdateView', 'MemberListView', 'PermissionManagementView'
            ]
        }

        # Test each view module
        for module_path, view_names in view_modules.items():
            print(f"\n{'='*60}")
            print(f"Testing Module: {module_path}")
            print(f"{'='*60}")

            for view_name in view_names:
                print(f"\nTesting View: {view_name}")
                print("-" * 40)

                # Test view import
                result = self.test_view_import(module_path, view_name)
                self.results[f"{module_path}.{view_name}"] = result

                if result.import_success:
                    print(f"✓ Import successful - Type: {result.view_type}")

                    if result.methods_tested:
                        print(f"  Methods found: {', '.join(result.methods_tested)}")
                        if result.methods_passed:
                            print(f"  ✓ Passed: {', '.join(result.methods_passed)}")
                        if result.methods_failed:
                            print(f"  ✗ Failed: {', '.join(result.methods_failed)}")
                else:
                    print(f"✗ Import failed: {result.import_error}")
                    if result.errors:
                        for error in result.errors:
                            print(f"  Error: {error}")

    def test_url_patterns(self):
        """Test URL patterns and routing"""
        print(f"\n{'='*60}")
        print("TESTING URL ROUTING CONFIGURATIONS")
        print(f"{'='*60}")

        # Common URL patterns to test
        common_urls = [
            ('/', 'home'),
            ('/dashboard/', 'dashboard'),
            ('/login/', 'login'),
            ('/logout/', 'logout'),
            ('/profile/', 'profile'),
            ('/search/', 'search'),
            ('/api/v1/communities/', 'communities_api'),
            ('/api/v1/assessments/', 'assessments_api'),
            ('/api/v1/coordination/', 'coordination_api'),
            ('/api/v1/organizations/', 'organizations_api'),
        ]

        for url_pattern, name in common_urls:
            print(f"\nTesting URL: {url_pattern} ({name})")
            try:
                resolved = resolve(url_pattern[1:] if url_pattern.startswith('/') else url_pattern)
                print(f"✓ Resolves to: {resolved.func}")
                print(f"  View name: {resolved.view_name}")
                print(f"  Namespace: {resolved.namespace}")
            except Exception as e:
                print(f"✗ Resolution failed: {e}")

    def generate_report(self):
        """Generate comprehensive test report"""
        print(f"\n{'='*80}")
        print("COMPREHENSIVE VIEW AND API TEST REPORT")
        print(f"{'='*80}")

        total_views = len(self.results)
        successful_imports = sum(1 for r in self.results.values() if r.import_success)
        failed_imports = total_views - successful_imports

        print(f"\nSUMMARY:")
        print(f"  Total Views Tested: {total_views}")
        print(f"  Successful Imports: {successful_imports}")
        print(f"  Failed Imports: {failed_imports}")
        print(f"  Success Rate: {(successful_imports/total_views*100):.1f}%" if total_views > 0 else "N/A")

        # View Type Distribution
        view_types = {}
        for result in self.results.values():
            if result.import_success:
                view_types[result.view_type] = view_types.get(result.view_type, 0) + 1

        print(f"\nVIEW TYPE DISTRIBUTION:")
        for view_type, count in view_types.items():
            print(f"  {view_type}: {count}")

        # Failed Imports
        if failed_imports > 0:
            print(f"\nFAILED IMPORTS:")
            for name, result in self.results.items():
                if not result.import_success:
                    print(f"  ✗ {name}: {result.import_error}")

        # Successful Views with Methods
        print(f"\nSUCCESSFUL VIEW ANALYSIS:")
        for name, result in self.results.items():
            if result.import_success:
                print(f"\n  ✓ {name} ({result.view_type})")
                if result.methods_tested:
                    print(f"    Methods: {', '.join(result.methods_tested)}")
                if result.url_patterns:
                    print(f"    URLs: {', '.join(result.url_patterns)}")
                if result.api_endpoints:
                    print(f"    API Endpoints: {', '.join(result.api_endpoints)}")

        return self.results

def main():
    """Main test execution function"""
    tester = ComprehensiveViewTester()

    # Run all tests
    tester.scan_and_test_views()
    tester.test_url_patterns()

    # Generate report
    results = tester.generate_report()

    # Return results for further processing
    return results

if __name__ == "__main__":
    main()