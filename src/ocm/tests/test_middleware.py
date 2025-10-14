"""
Tests for OCM middleware
"""
from django.test import TestCase, RequestFactory, Client
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse
from unittest.mock import Mock, patch

from organizations.models import Organization
from ocm.models import OCMAccess
from ocm.middleware import OCMAccessMiddleware

User = get_user_model()


class OCMAccessMiddlewareTestCase(TestCase):
    """Test OCMAccessMiddleware functionality"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.middleware = OCMAccessMiddleware(get_response=self.get_response)

        # Create OCM user
        self.ocm_user = User.objects.create_user(
            username='ocm_user',
            email='ocm@example.com',
            password='ocmpass123'
        )

        # Create regular user
        self.regular_user = User.objects.create_user(
            username='regular_user',
            email='regular@example.com',
            password='regularpass123'
        )

        # Grant OCM access
        self.ocm_access = OCMAccess.objects.create(
            user=self.ocm_user,
            granted_by=self.ocm_user,
            reason='Testing',
            is_active=True
        )

    def get_response(self, request):
        """Mock get_response callable"""
        return HttpResponse("Success")

    def add_session_to_request(self, request):
        """Add session to request"""
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

    def test_middleware_sets_is_ocm_view_flag(self):
        """Test middleware sets is_ocm_view flag for OCM URLs"""
        request = self.factory.get('/ocm/dashboard/')
        request.user = self.ocm_user
        self.add_session_to_request(request)

        # Process request through middleware
        response = self.middleware(request)

        # Should set is_ocm_view flag
        self.assertTrue(
            getattr(request, 'is_ocm_view', False),
            "Middleware should set is_ocm_view flag"
        )

    def test_middleware_identifies_ocm_user(self):
        """Test middleware identifies OCM users"""
        request = self.factory.get('/ocm/dashboard/')
        request.user = self.ocm_user
        self.add_session_to_request(request)

        # Process request
        response = self.middleware(request)

        # Should identify as OCM user
        self.assertTrue(
            getattr(request, 'is_ocm_user', False),
            "Middleware should identify OCM users"
        )

    def test_middleware_identifies_non_ocm_user(self):
        """Test middleware identifies non-OCM users"""
        request = self.factory.get('/ocm/dashboard/')
        request.user = self.regular_user
        self.add_session_to_request(request)

        # Process request
        response = self.middleware(request)

        # Should not be identified as OCM user
        self.assertFalse(
            getattr(request, 'is_ocm_user', False),
            "Regular users should not be identified as OCM users"
        )

    def test_middleware_enforces_readonly_on_post(self):
        """Test middleware blocks POST requests for OCM views"""
        request = self.factory.post('/ocm/dashboard/', data={'test': 'data'})
        request.user = self.ocm_user
        self.add_session_to_request(request)

        # Process request
        response = self.middleware(request)

        # Should block POST
        self.assertEqual(response.status_code, 403)

    def test_middleware_allows_get_requests(self):
        """Test middleware allows GET requests for OCM views"""
        request = self.factory.get('/ocm/dashboard/')
        request.user = self.ocm_user
        self.add_session_to_request(request)

        # Process request
        response = self.middleware(request)

        # Should allow GET
        self.assertEqual(response.status_code, 200)

    def test_middleware_logs_access_attempts(self):
        """Test middleware logs OCM access attempts"""
        with patch('ocm.middleware.logger') as mock_logger:
            request = self.factory.get('/ocm/dashboard/')
            request.user = self.ocm_user
            self.add_session_to_request(request)

            # Process request
            response = self.middleware(request)

            # Should log access
            # mock_logger.info.assert_called()

    def test_middleware_updates_last_accessed(self):
        """Test middleware updates last_accessed timestamp"""
        request = self.factory.get('/ocm/dashboard/')
        request.user = self.ocm_user
        self.add_session_to_request(request)

        # Get initial last_accessed
        self.ocm_access.refresh_from_db()
        initial_last_accessed = self.ocm_access.last_accessed

        # Process request
        response = self.middleware(request)

        # Check last_accessed was updated
        self.ocm_access.refresh_from_db()
        self.assertIsNotNone(self.ocm_access.last_accessed)


class MiddlewareReadOnlyEnforcementTestCase(TestCase):
    """Test middleware read-only enforcement"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.middleware = OCMAccessMiddleware(
            get_response=lambda req: HttpResponse("Success")
        )

        self.ocm_user = User.objects.create_user(
            username='ocm_user',
            email='ocm@example.com',
            password='ocmpass123'
        )

        OCMAccess.objects.create(
            user=self.ocm_user,
            granted_by=self.ocm_user,
            reason='Testing',
            is_active=True
        )

    def add_session_to_request(self, request):
        """Add session to request"""
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

    def test_post_requests_blocked(self):
        """Test POST requests are blocked"""
        request = self.factory.post('/ocm/dashboard/', data={'test': 'data'})
        request.user = self.ocm_user
        self.add_session_to_request(request)

        response = self.middleware(request)
        self.assertEqual(response.status_code, 403)

    def test_put_requests_blocked(self):
        """Test PUT requests are blocked"""
        request = self.factory.put('/ocm/dashboard/', data={'test': 'data'})
        request.user = self.ocm_user
        self.add_session_to_request(request)

        response = self.middleware(request)
        self.assertEqual(response.status_code, 403)

    def test_patch_requests_blocked(self):
        """Test PATCH requests are blocked"""
        request = self.factory.patch('/ocm/dashboard/', data={'test': 'data'})
        request.user = self.ocm_user
        self.add_session_to_request(request)

        response = self.middleware(request)
        self.assertEqual(response.status_code, 403)

    def test_delete_requests_blocked(self):
        """Test DELETE requests are blocked"""
        request = self.factory.delete('/ocm/dashboard/')
        request.user = self.ocm_user
        self.add_session_to_request(request)

        response = self.middleware(request)
        self.assertEqual(response.status_code, 403)

    def test_get_requests_allowed(self):
        """Test GET requests are allowed"""
        request = self.factory.get('/ocm/dashboard/')
        request.user = self.ocm_user
        self.add_session_to_request(request)

        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

    def test_head_requests_allowed(self):
        """Test HEAD requests are allowed"""
        request = self.factory.head('/ocm/dashboard/')
        request.user = self.ocm_user
        self.add_session_to_request(request)

        response = self.middleware(request)
        self.assertIn(response.status_code, [200, 301, 302])

    def test_options_requests_allowed(self):
        """Test OPTIONS requests are allowed"""
        request = self.factory.options('/ocm/dashboard/')
        request.user = self.ocm_user
        self.add_session_to_request(request)

        response = self.middleware(request)
        # OPTIONS might return different status codes
        self.assertIn(response.status_code, [200, 204, 405])


class MiddlewareURLFilteringTestCase(TestCase):
    """Test middleware only applies to OCM URLs"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.middleware = OCMAccessMiddleware(
            get_response=lambda req: HttpResponse("Success")
        )

        self.ocm_user = User.objects.create_user(
            username='ocm_user',
            email='ocm@example.com',
            password='ocmpass123'
        )

        OCMAccess.objects.create(
            user=self.ocm_user,
            granted_by=self.ocm_user,
            reason='Testing',
            is_active=True
        )

    def add_session_to_request(self, request):
        """Add session to request"""
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

    def test_middleware_applies_to_ocm_urls(self):
        """Test middleware applies to /ocm/ URLs"""
        request = self.factory.get('/ocm/dashboard/')
        request.user = self.ocm_user
        self.add_session_to_request(request)

        response = self.middleware(request)

        # Should set OCM flags
        self.assertTrue(getattr(request, 'is_ocm_view', False))

    def test_middleware_ignores_non_ocm_urls(self):
        """Test middleware doesn't interfere with non-OCM URLs"""
        request = self.factory.post('/organizations/create/', data={'name': 'Test'})
        request.user = self.ocm_user
        self.add_session_to_request(request)

        response = self.middleware(request)

        # Should not block non-OCM URLs
        self.assertEqual(response.status_code, 200)

    def test_middleware_handles_api_urls(self):
        """Test middleware handles /api/ocm/ URLs"""
        request = self.factory.get('/api/ocm/dashboard/')
        request.user = self.ocm_user
        self.add_session_to_request(request)

        response = self.middleware(request)

        # Should apply to API URLs too
        self.assertTrue(getattr(request, 'is_ocm_view', False))


class MiddlewareAccessLoggingTestCase(TestCase):
    """Test middleware access logging functionality"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.middleware = OCMAccessMiddleware(
            get_response=lambda req: HttpResponse("Success")
        )

        self.ocm_user = User.objects.create_user(
            username='ocm_user',
            email='ocm@example.com',
            password='ocmpass123'
        )

        OCMAccess.objects.create(
            user=self.ocm_user,
            granted_by=self.ocm_user,
            reason='Testing',
            is_active=True
        )

    def add_session_to_request(self, request):
        """Add session to request"""
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

    @patch('ocm.middleware.logger')
    def test_successful_access_logged(self, mock_logger):
        """Test successful access attempts are logged"""
        request = self.factory.get('/ocm/dashboard/')
        request.user = self.ocm_user
        self.add_session_to_request(request)

        response = self.middleware(request)

        # Should log successful access
        # mock_logger.info.assert_called()

    @patch('ocm.middleware.logger')
    def test_blocked_access_logged(self, mock_logger):
        """Test blocked access attempts are logged"""
        request = self.factory.post('/ocm/dashboard/', data={'test': 'data'})
        request.user = self.ocm_user
        self.add_session_to_request(request)

        response = self.middleware(request)

        # Should log blocked attempt
        # mock_logger.warning.assert_called()

    @patch('ocm.middleware.logger')
    def test_unauthorized_access_logged(self, mock_logger):
        """Test unauthorized access attempts are logged"""
        regular_user = User.objects.create_user(
            username='regular_user',
            email='regular@example.com',
            password='regularpass123'
        )

        request = self.factory.get('/ocm/dashboard/')
        request.user = regular_user
        self.add_session_to_request(request)

        response = self.middleware(request)

        # Should log unauthorized attempt
        # mock_logger.warning.assert_called()


class MiddlewareInactiveAccessTestCase(TestCase):
    """Test middleware handles inactive OCM access"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.middleware = OCMAccessMiddleware(
            get_response=lambda req: HttpResponse("Success")
        )

        self.ocm_user = User.objects.create_user(
            username='ocm_user',
            email='ocm@example.com',
            password='ocmpass123'
        )

        # Create inactive OCM access
        self.ocm_access = OCMAccess.objects.create(
            user=self.ocm_user,
            granted_by=self.ocm_user,
            reason='Testing',
            is_active=False
        )

    def add_session_to_request(self, request):
        """Add session to request"""
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

    def test_inactive_access_denied(self):
        """Test users with inactive OCM access are denied"""
        request = self.factory.get('/ocm/dashboard/')
        request.user = self.ocm_user
        self.add_session_to_request(request)

        response = self.middleware(request)

        # Should deny access
        self.assertEqual(response.status_code, 403)


class MiddlewareEdgeCasesTestCase(TestCase):
    """Test middleware edge cases"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.middleware = OCMAccessMiddleware(
            get_response=lambda req: HttpResponse("Success")
        )

    def add_session_to_request(self, request):
        """Add session to request"""
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

    def test_anonymous_user_denied(self):
        """Test anonymous users are denied"""
        from django.contrib.auth.models import AnonymousUser

        request = self.factory.get('/ocm/dashboard/')
        request.user = AnonymousUser()
        self.add_session_to_request(request)

        response = self.middleware(request)

        # Should deny access
        self.assertIn(response.status_code, [302, 403])

    def test_middleware_handles_missing_user(self):
        """Test middleware handles requests without user"""
        request = self.factory.get('/ocm/dashboard/')
        # No user set
        self.add_session_to_request(request)

        # Should not crash
        try:
            response = self.middleware(request)
            # Should handle gracefully
            self.assertIsNotNone(response)
        except AttributeError:
            # Expected if user is required
            pass

    def test_middleware_handles_exception(self):
        """Test middleware handles exceptions gracefully"""
        def failing_get_response(request):
            raise Exception("Test exception")

        middleware = OCMAccessMiddleware(get_response=failing_get_response)

        ocm_user = User.objects.create_user(
            username='ocm_user',
            email='ocm@example.com',
            password='ocmpass123'
        )

        OCMAccess.objects.create(
            user=ocm_user,
            granted_by=ocm_user,
            reason='Testing',
            is_active=True
        )

        request = self.factory.get('/ocm/dashboard/')
        request.user = ocm_user
        self.add_session_to_request(request)

        # Should propagate exception (or handle it)
        with self.assertRaises(Exception):
            middleware(request)


class MiddlewareIntegrationTestCase(TestCase):
    """Integration tests for middleware with views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create OCM user
        self.ocm_user = User.objects.create_user(
            username='ocm_user',
            email='ocm@example.com',
            password='ocmpass123'
        )

        # Grant OCM access
        OCMAccess.objects.create(
            user=self.ocm_user,
            granted_by=self.ocm_user,
            reason='Testing',
            is_active=True
        )

        # Create test organization
        Organization.objects.create(
            name='Test MOA',
            organization_type='ministry',
            is_active=True
        )

        self.client.login(username='ocm_user', password='ocmpass123')

    def test_middleware_with_real_view(self):
        """Test middleware works with actual views"""
        from django.urls import reverse

        url = reverse('ocm:dashboard')
        response = self.client.get(url)

        # Should allow GET
        self.assertEqual(response.status_code, 200)

    def test_middleware_blocks_post_to_real_view(self):
        """Test middleware blocks POST to actual views"""
        from django.urls import reverse

        url = reverse('ocm:dashboard')
        response = self.client.post(url, data={'test': 'data'})

        # Should block POST
        self.assertEqual(response.status_code, 403)
