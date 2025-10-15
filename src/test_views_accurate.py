#!/usr/bin/env python
"""
Accurate View and API Testing Suite for OBCMS
Tests actual view classes, functions, API endpoints, and URL routing configurations
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
from django.urls import reverse, resolve, get_resolver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

User = get_user_model()

class ViewTestResult:
    """Container for view test results"""
    def __init__(self, name: str, module_path: str):
        self.name = name
        self.module_path = module_path
        self.import_success = False
        self.import_error = None
        self.view_type = "Unknown"
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

class AccurateViewTester:
    """Accurate view and API testing class based on actual view implementations"""

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
        result = ViewTestResult(view_name, module_path)

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

    def discover_views_in_module(self, module_path: str) -> List[str]:
        """Discover all views in a module"""
        views = []
        try:
            module = importlib.import_module(module_path)

            # Check __all__ attribute first
            if hasattr(module, '__all__'):
                views.extend(module.__all__)

            # Scan module for classes and functions that look like views
            for name, obj in inspect.getmembers(module):
                if name.startswith('_'):
                    continue

                if inspect.isclass(obj):
                    # Check if it's a view class
                    if (hasattr(obj, 'as_view') or
                        'View' in name or
                        any(base.__name__.endswith('View') for base in obj.__mro__)):
                        views.append(name)
                elif inspect.isfunction(obj):
                    # Check if it's a view function
                    if (hasattr(obj, '__wrapped__') and  # decorated function
                        any(decorator.__name__ in ['login_required', 'require_http_methods']
                            for decorator in getattr(obj, '__wrapped__', []).__class__.__mro__ if hasattr(decorator, '__name__'))):
                        views.append(name)

        except ImportError as e:
            print(f"Could not import module {module_path}: {e}")

        return list(set(views))  # Remove duplicates

    def test_url_patterns(self):
        """Test URL patterns and routing"""
        print(f"\n{'='*60}")
        print("TESTING URL ROUTING CONFIGURATIONS")
        print(f"{'='*60}")

        resolver = get_resolver()
        url_patterns = []

        def collect_patterns(patterns, prefix=''):
            for pattern in patterns:
                if hasattr(pattern, 'url_patterns'):
                    # This is an include() - recurse
                    new_prefix = prefix + str(pattern.pattern)
                    collect_patterns(pattern.url_patterns, new_prefix)
                else:
                    # This is a URL pattern
                    url = prefix + str(pattern.pattern)
                    if hasattr(pattern, 'name') and pattern.name:
                        url_patterns.append((url, pattern.name, pattern.callback))

        collect_patterns(resolver.url_patterns)

        # Test common URL patterns
        test_urls = [
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

        for url_pattern, expected_name in test_urls:
            print(f"\nTesting URL: {url_pattern} ({expected_name})")
            try:
                resolved = resolve(url_pattern[1:] if url_pattern.startswith('/') else url_pattern)
                print(f"✓ Resolves to: {resolved.func}")
                print(f"  View name: {getattr(resolved.func, '__name__', 'No name')}")
                print(f"  Namespace: {resolved.namespace}")

                # Check if any of our URL patterns match
                for url, name, callback in url_patterns:
                    if expected_name in name.lower():
                        print(f"  ✓ Found matching pattern: {name}")
                        break
                else:
                    print(f"  ⚠ No matching pattern found for {expected_name}")

            except Exception as e:
                print(f"✗ Resolution failed: {e}")

        return url_patterns

    def scan_and_test_views(self):
        """Scan and test all views in the project"""
        print("=" * 80)
        print("ACCURATE VIEW AND API TESTING SUITE")
        print("=" * 80)

        # Define actual view modules based on the codebase
        view_modules = {
            'common.views.auth': [
                'CustomLoginView', 'CustomLogoutView', 'UserRegistrationView',
                'MOARegistrationView', 'MOARegistrationSuccessView', 'profile', 'page_restricted'
            ],
            'common.views.dashboard': [
                'dashboard', 'dashboard_stats_cards', 'dashboard_metrics'
            ],
            'common.views.search': [
                # Will discover actual views
            ],
            'common.views.calendar': [
                'work_items_calendar_feed', 'work_item_modal'
            ],
            'communities.views': [
                'OBCCommunityViewSet', 'StakeholderViewSet', 'StakeholderEngagementViewSet',
                'CommunityLivelihoodViewSet', 'CommunityInfrastructureViewSet',
                'add_data_layer', 'create_visualization', 'geographic_data_list'
            ],
            'mana.views': [
                # Will discover actual views
            ],
            'mana.api_views': [
                'AssessmentViewSet'
            ],
            'coordination.views': [
                # Will discover actual views
            ],
            'coordination.api_views': [
                'PartnershipViewSet'
            ],
            'organizations.views': [
                # Will discover actual views
            ]
        }

        # Test each view module
        for module_path, expected_views in view_modules.items():
            print(f"\n{'='*60}")
            print(f"Testing Module: {module_path}")
            print(f"{'='*60}")

            # Discover views if none provided
            if not expected_views:
                discovered_views = self.discover_views_in_module(module_path)
                if discovered_views:
                    print(f"Discovered views: {', '.join(discovered_views)}")
                    expected_views = discovered_views[:10]  # Limit to first 10

            for view_name in expected_views:
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

    def test_api_endpoints(self):
        """Test API endpoint functionality"""
        print(f"\n{'='*60}")
        print("TESTING API ENDPOINTS")
        print(f"{'='*60}")

        # Test known API endpoints
        api_endpoints = [
            ('/api/v1/communities/', ['GET', 'POST']),
            ('/api/v1/communities/statistics/', ['GET']),
            ('/api/v1/stakeholders/', ['GET', 'POST']),
            ('/api/v1/stakeholders/statistics/', ['GET']),
            ('/api/v1/assessments/', ['GET', 'POST']),
            ('/api/v1/partnerships/', ['GET', 'POST']),
        ]

        for endpoint, methods in api_endpoints:
            print(f"\nTesting API Endpoint: {endpoint}")
            print(f"Methods: {', '.join(methods)}")
            print("-" * 40)

            for method in methods:
                try:
                    if method == 'GET':
                        response = self.api_client.get(endpoint)
                    elif method == 'POST':
                        response = self.api_client.post(endpoint, {})

                    print(f"  {method}: {response.status_code} - {response.get('Content-Type', '')}")

                    if hasattr(response, 'data') and response.data:
                        if isinstance(response.data, dict):
                            print(f"    Data keys: {list(response.data.keys())}")
                        elif isinstance(response.data, list):
                            print(f"    Data: List with {len(response.data)} items")

                except Exception as e:
                    print(f"  {method}: Error - {e}")

    def generate_report(self):
        """Generate comprehensive test report"""
        print(f"\n{'='*80}")
        print("ACCURATE VIEW AND API TEST REPORT")
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

        # Module Distribution
        modules = {}
        for name, result in self.results.items():
            module = name.split('.')[0] + '.' + name.split('.')[1]
            modules[module] = modules.get(module, {'total': 0, 'success': 0})
            modules[module]['total'] += 1
            if result.import_success:
                modules[module]['success'] += 1

        print(f"\nMODULE DISTRIBUTION:")
        for module, stats in modules.items():
            success_rate = (stats['success']/stats['total']*100) if stats['total'] > 0 else 0
            print(f"  {module}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")

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

        return self.results

def main():
    """Main test execution function"""
    tester = AccurateViewTester()

    # Run all tests
    tester.scan_and_test_views()
    tester.test_url_patterns()
    tester.test_api_endpoints()

    # Generate report
    results = tester.generate_report()

    # Return results for further processing
    return results

if __name__ == "__main__":
    main()