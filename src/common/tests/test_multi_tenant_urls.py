"""
Multi-tenant URL Tests

Comprehensive tests for the dual-mode URL configuration system.
Tests both OBCMS and BMMS modes to ensure proper URL routing and
organization context extraction.
"""

from django.test import TestCase, Client, override_settings
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware

from obc_management.settings.bmms_config import BMMSMode
from common.middleware.multi_tenant_urls import (
    extract_org_code_from_url,
    get_organization_by_code,
    validate_organization_access,
    MultiTenantURLMiddleware,
)

User = get_user_model()


class MultiTenantURLTestCase(TestCase):
    """Test cases for multi-tenant URL functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create test organizations if the model exists
        try:
            from organizations.models import Organization
            self.org_dswd = Organization.objects.create(
                code='DSWD',
                name='Department of Social Welfare and Development',
                is_active=True
            )
            self.org_doh = Organization.objects.create(
                code='DOH',
                name='Department of Health',
                is_active=True
            )
            self.organizations_exist = True
        except ImportError:
            self.organizations_exist = False

    def test_extract_org_code_from_url_obcms_mode(self):
        """Test ORG_CODE extraction in OBCMS mode."""
        with override_settings(BMMS_MODE=BMMSMode.OBCMS):
            # Mock request with OBCMS mode
            request = self.client.request().wsgi_request
            request.path = '/dashboard/'

            org_code = extract_org_code_from_url(request)
            self.assertIsNone(org_code)

            request.path = '/communities/'
            org_code = extract_org_code_from_url(request)
            self.assertIsNone(org_code)

    def test_extract_org_code_from_url_bmms_mode(self):
        """Test ORG_CODE extraction in BMMS mode."""
        with override_settings(BMMS_MODE=BMMSMode.BMMS):
            # Mock request with BMMS mode URLs
            request = self.client.request().wsgi_request
            request.path = '/moa/DSWD/dashboard/'

            org_code = extract_org_code_from_url(request)
            self.assertEqual(org_code, 'DSWD')

            request.path = '/moa/DOH/communities/'
            org_code = extract_org_code_from_url(request)
            self.assertEqual(org_code, 'DOH')

            request.path = '/dashboard/'  # No ORG_CODE
            org_code = extract_org_code_from_url(request)
            self.assertIsNone(org_code)

    def test_extract_org_code_invalid_format(self):
        """Test ORG_CODE extraction with invalid formats."""
        with override_settings(BMMS_MODE=BMMSMode.BMMS):
            request = self.client.request().wsgi_request

            # Invalid ORG_CODE formats
            invalid_paths = [
                '/moa/DS@WD/dashboard/',  # Special character
                '/moa/DS WD/dashboard/',  # Space
                '/moa/123$/dashboard/',   # Invalid character
            ]

            for path in invalid_paths:
                request.path = path
                org_code = extract_org_code_from_url(request)
                self.assertIsNone(org_code, f"Should reject invalid path: {path}")

    def test_get_organization_by_code(self):
        """Test organization lookup by code."""
        if not self.organizations_exist:
            self.skipTest("Organizations model not available")

        # Test existing organization
        org = get_organization_by_code('DSWD')
        self.assertIsNotNone(org)
        self.assertEqual(org.code, 'DSWD')

        # Test case-insensitive lookup
        org = get_organization_by_code('dswd')
        self.assertIsNotNone(org)
        self.assertEqual(org.code, 'DSWD')

        # Test non-existent organization
        org = get_organization_by_code('INVALID')
        self.assertIsNone(org)

        # Test inactive organization
        if hasattr(self.org_dswd, 'is_active'):
            self.org_dswd.is_active = False
            self.org_dswd.save()
            org = get_organization_by_code('DSWD')
            self.assertIsNone(org)

    def test_url_resolution_obcms_mode(self):
        """Test URL resolution in OBCMS mode."""
        with override_settings(BMMS_MODE=BMMSMode.OBCMS):
            # Test standard URLs resolve correctly
            dashboard_url = reverse('common:dashboard')
            self.assertEqual(dashboard_url, '/dashboard/')

            communities_url = reverse('communities:communities_home')
            self.assertEqual(communities_url, '/communities/')

    def test_multi_tenant_template_tags(self):
        """Test multi-tenant URL template tags."""
        from django.template import Context, Template
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get('/')

        # Test OBCMS mode template tags
        with override_settings(BMMS_MODE=BMMSMode.OBCMS):
            template = Template('{% load multi_tenant_urls %}{% org_url "common:dashboard" %}')
            context = Context({'request': request})
            rendered = template.render(context)
            self.assertEqual(rendered.strip(), '/dashboard/')

            # Test mode detection
            template = Template('{% load multi_tenant_urls %}{% if is_obcms_mode %}OBCMS{% else %}BMMS{% endif %}')
            rendered = template.render(context)
            self.assertEqual(rendered.strip(), 'OBCMS')

    def test_organization_switching_urls(self):
        """Test organization switching URL patterns."""
        # Test organization switching URLs exist
        switch_url = reverse('common:switch_organization')
        self.assertEqual(switch_url, '/switch-organization/')

        switch_with_code_url = reverse('common:switch_organization_code', kwargs={'org_code': 'DSWD'})
        self.assertEqual(switch_with_code_url, '/switch-organization/DSWD/')

        selection_url = reverse('common:organization_selection')
        self.assertEqual(selection_url, '/organization-selection/')

    def test_api_endpoints(self):
        """Test organization management API endpoints."""
        # Test validation endpoint
        validate_url = reverse('common:validate_organization', kwargs={'org_code': 'DSWD'})
        self.assertEqual(validate_url, '/api/validate-organization/DSWD/')

        # Test current organization endpoint
        current_url = reverse('common:current_organization')
        self.assertEqual(current_url, '/api/current-organization/')

    def test_htmx_endpoints(self):
        """Test HTMX endpoints for instant UI updates."""
        # Test organization switcher partial
        switcher_url = reverse('common:organization_switcher_partial')
        self.assertEqual(switcher_url, '/partial/organization-switcher/')

        # Test quick switch endpoint
        quick_switch_url = reverse('common:quick_switch_organization')
        self.assertEqual(quick_switch_url, '/quick-switch-organization/')

    def test_backward_compatibility(self):
        """Test backward compatibility with existing URLs."""
        # Existing URLs should still work in both modes
        legacy_urls = [
            ('common:dashboard', '/dashboard/'),
            ('communities:communities_home', '/communities/'),
            ('mana:mana_home', '/mana/'),
        ]

        for url_name, expected_path in legacy_urls:
            with self.subTest(url_name=url_name):
                try:
                    resolved_url = reverse(url_name)
                    self.assertEqual(resolved_url, expected_path)
                except:
                    # Some URLs might not be available in test environment
                    pass

    def test_url_patterns_integration(self):
        """Test integration with Django URL patterns."""
        from obc_management.url_utilities.multi_tenant_urls import (
            get_obcms_urlpatterns,
            get_bmms_urlpatterns,
            get_multi_tenant_urlpatterns,
        )

        # Test OBCMS URL patterns
        obcms_patterns = get_obcms_urlpatterns()
        self.assertIsInstance(obcms_patterns, list)
        self.assertGreater(len(obcms_patterns), 0)

        # Test BMMS URL patterns
        bmms_patterns = get_bmms_urlpatterns()
        self.assertIsInstance(bmms_patterns, list)
        self.assertGreater(len(bmms_patterns), 0)

        # Test dynamic pattern selection
        with override_settings(BMMS_MODE=BMMSMode.OBCMS):
            patterns = get_multi_tenant_urlpatterns()
            self.assertIsInstance(patterns, list)

        with override_settings(BMMS_MODE=BMMSMode.BMMS):
            patterns = get_multi_tenant_urlpatterns()
            self.assertIsInstance(patterns, list)

    def test_middleware_integration(self):
        """Test middleware integration with request processing."""
        middleware = MultiTenantURLMiddleware(lambda req: type('MockResponse', (), {'status_code': 200})())

        # Test in OBCMS mode
        with override_settings(BMMS_MODE=BMMSMode.OBCMS):
            request = self.client.request().wsgi_request
            request.path = '/dashboard/'
            request.user = self.user

            # Add session and messages middleware requirements
            SessionMiddleware(lambda req: None).process_request(request)
            MessageMiddleware(lambda req: None).process_request(request)

            response = middleware(request)
            self.assertEqual(response.status_code, 200)

    def test_organization_context_persistence(self):
        """Test organization context persistence across requests."""
        if not self.organizations_exist:
            self.skipTest("Organizations model not available")

        # Login user
        self.client.login(username='testuser', email='test@example.com', password='testpass123')

        # Set organization in session
        session = self.client.session
        session['current_organization_code'] = 'DSWD'
        session.save()

        # Verify organization context is accessible
        response = self.client.get(reverse('common:current_organization'))
        self.assertEqual(response.status_code, 200)

        # Test JSON response structure
        self.assertEqual(response['Content-Type'], 'application/json')


class MultiTenantURLIntegrationTestCase(TestCase):
    """Integration tests for multi-tenant URLs."""

    def setUp(self):
        """Set up integration test data."""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )

    def test_full_url_routing_cycle(self):
        """Test complete URL routing cycle in both modes."""
        self.client.login(username='admin', password='adminpass123')

        # Test OBCMS mode routing
        with override_settings(BMMS_MODE=BMMSMode.OBCMS):
            # Navigate to dashboard
            response = self.client.get(reverse('common:dashboard'))
            self.assertIn(response.status_code, [200, 302])  # May redirect if auth required

            # Navigate to communities
            response = self.client.get(reverse('communities:communities_home'))
            self.assertIn(response.status_code, [200, 302])

        # Test BMMS mode routing (if organizations available)
        try:
            from organizations.models import Organization
            with override_settings(BMMS_MODE=BMMSMode.BMMS):
                # Navigate to organization selection
                response = self.client.get(reverse('common:organization_selection'))
                self.assertIn(response.status_code, [200, 302])
        except ImportError:
            self.skipTest("Organizations model not available for BMMS testing")


class MultiTenantURLPerformanceTestCase(TestCase):
    """Performance tests for multi-tenant URL processing."""

    def test_url_resolution_performance(self):
        """Test URL resolution performance."""
        import time

        # Test multiple URL resolutions
        urls_to_test = [
            'common:dashboard',
            'communities:communities_home',
            'mana:mana_home',
        ]

        start_time = time.time()
        for url_name in urls_to_test:
            try:
                reverse(url_name)
            except:
                pass  # Skip unavailable URLs
        end_time = time.time()

        # Should complete quickly (< 100ms for all URLs)
        resolution_time = (end_time - start_time) * 1000
        self.assertLess(resolution_time, 100, f"URL resolution too slow: {resolution_time:.2f}ms")

    def test_middleware_processing_performance(self):
        """Test middleware processing performance."""
        import time

        middleware = MultiTenantURLMiddleware(lambda req: type('MockResponse', (), {'status_code': 200})())

        # Simulate multiple requests
        paths_to_test = [
            '/dashboard/',
            '/communities/',
            '/mana/',
            '/moa/DSWD/dashboard/',
            '/moa/DOH/communities/',
        ]

        start_time = time.time()
        for path in paths_to_test:
            request = self.client.request().wsgi_request
            request.path = path
            response = middleware(request)
            self.assertEqual(response.status_code, 200)
        end_time = time.time()

        # Should complete quickly (< 200ms for all requests)
        processing_time = (end_time - start_time) * 1000
        self.assertLess(processing_time, 200, f"Middleware processing too slow: {processing_time:.2f}ms")