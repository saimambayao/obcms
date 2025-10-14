"""
Tests for OCM decorators
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views import View

from ocm.models import OCMAccess
from ocm.decorators import (
    require_ocm_access,
    enforce_readonly,
    ocm_readonly_view
)

User = get_user_model()


class RequireOCMAccessDecoratorTestCase(TestCase):
    """Test require_ocm_access decorator"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()

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

        # Create test view function
        @require_ocm_access
        def test_view(request):
            return HttpResponse("Success")

        self.test_view = test_view

    def test_ocm_user_allowed(self):
        """Test OCM user with active access is allowed"""
        request = self.factory.get('/ocm/dashboard/')
        request.user = self.ocm_user

        response = self.test_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Success")

    def test_regular_user_denied(self):
        """Test regular user without OCM access is denied"""
        request = self.factory.get('/ocm/dashboard/')
        request.user = self.regular_user

        response = self.test_view(request)
        self.assertEqual(response.status_code, 403)

    def test_inactive_ocm_access_denied(self):
        """Test user with inactive OCM access is denied"""
        # Deactivate access
        self.ocm_access.is_active = False
        self.ocm_access.save()

        request = self.factory.get('/ocm/dashboard/')
        request.user = self.ocm_user

        response = self.test_view(request)
        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_denied(self):
        """Test anonymous user is denied"""
        from django.contrib.auth.models import AnonymousUser

        request = self.factory.get('/ocm/dashboard/')
        request.user = AnonymousUser()

        response = self.test_view(request)
        # Should redirect to login or return 403
        self.assertIn(response.status_code, [302, 403])

    def test_last_accessed_updated(self):
        """Test last_accessed timestamp is updated"""
        request = self.factory.get('/ocm/dashboard/')
        request.user = self.ocm_user

        # Initially last_accessed is None
        self.ocm_access.refresh_from_db()
        original_last_accessed = self.ocm_access.last_accessed

        # Make request
        response = self.test_view(request)
        self.assertEqual(response.status_code, 200)

        # Check last_accessed was updated
        self.ocm_access.refresh_from_db()
        self.assertIsNotNone(self.ocm_access.last_accessed)
        if original_last_accessed:
            self.assertGreater(
                self.ocm_access.last_accessed,
                original_last_accessed
            )


class EnforceReadonlyDecoratorTestCase(TestCase):
    """Test enforce_readonly decorator"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create test view
        @enforce_readonly
        def test_view(request):
            return HttpResponse("Success")

        self.test_view = test_view

    def test_get_request_allowed(self):
        """Test GET requests are allowed"""
        request = self.factory.get('/ocm/data/')
        request.user = self.user

        response = self.test_view(request)
        self.assertEqual(response.status_code, 200)

    def test_head_request_allowed(self):
        """Test HEAD requests are allowed"""
        request = self.factory.head('/ocm/data/')
        request.user = self.user

        response = self.test_view(request)
        self.assertEqual(response.status_code, 200)

    def test_options_request_allowed(self):
        """Test OPTIONS requests are allowed"""
        request = self.factory.options('/ocm/data/')
        request.user = self.user

        response = self.test_view(request)
        self.assertEqual(response.status_code, 200)

    def test_post_request_blocked(self):
        """Test POST requests are blocked"""
        request = self.factory.post('/ocm/data/')
        request.user = self.user

        response = self.test_view(request)
        self.assertEqual(response.status_code, 403)

    def test_put_request_blocked(self):
        """Test PUT requests are blocked"""
        request = self.factory.put('/ocm/data/1/')
        request.user = self.user

        response = self.test_view(request)
        self.assertEqual(response.status_code, 403)

    def test_patch_request_blocked(self):
        """Test PATCH requests are blocked"""
        request = self.factory.patch('/ocm/data/1/')
        request.user = self.user

        response = self.test_view(request)
        self.assertEqual(response.status_code, 403)

    def test_delete_request_blocked(self):
        """Test DELETE requests are blocked"""
        request = self.factory.delete('/ocm/data/1/')
        request.user = self.user

        response = self.test_view(request)
        self.assertEqual(response.status_code, 403)

    def test_error_message_content(self):
        """Test error message for blocked requests"""
        request = self.factory.post('/ocm/data/')
        request.user = self.user

        response = self.test_view(request)
        self.assertEqual(response.status_code, 403)
        self.assertIn(
            b'read-only' or b'Read-only',
            response.content.lower()
        )


class OCMReadonlyViewDecoratorTestCase(TestCase):
    """Test ocm_readonly_view combined decorator"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()

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

        # Create regular user
        self.regular_user = User.objects.create_user(
            username='regular_user',
            email='regular@example.com',
            password='regularpass123'
        )

        # Create test view with combined decorator
        @ocm_readonly_view
        def test_view(request):
            return HttpResponse("Success")

        self.test_view = test_view

    def test_ocm_user_get_allowed(self):
        """Test OCM user GET request is allowed"""
        request = self.factory.get('/ocm/dashboard/')
        request.user = self.ocm_user

        response = self.test_view(request)
        self.assertEqual(response.status_code, 200)

    def test_ocm_user_post_blocked(self):
        """Test OCM user POST request is blocked"""
        request = self.factory.post('/ocm/dashboard/')
        request.user = self.ocm_user

        response = self.test_view(request)
        self.assertEqual(response.status_code, 403)

    def test_regular_user_get_denied(self):
        """Test regular user GET request is denied"""
        request = self.factory.get('/ocm/dashboard/')
        request.user = self.regular_user

        response = self.test_view(request)
        self.assertEqual(response.status_code, 403)

    def test_regular_user_post_denied(self):
        """Test regular user POST request is denied"""
        request = self.factory.post('/ocm/dashboard/')
        request.user = self.regular_user

        response = self.test_view(request)
        self.assertEqual(response.status_code, 403)


class DecoratorOnClassBasedViewTestCase(TestCase):
    """Test decorators on class-based views"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()

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

        # Create test class-based view
        class TestView(View):
            @method_decorator(ocm_readonly_view)
            def dispatch(self, *args, **kwargs):
                return super().dispatch(*args, **kwargs)

            def get(self, request):
                return HttpResponse("GET Success")

            def post(self, request):
                return HttpResponse("POST Success")

        self.view_class = TestView

    def test_cbv_get_allowed(self):
        """Test GET on class-based view is allowed"""
        request = self.factory.get('/ocm/dashboard/')
        request.user = self.ocm_user

        view = self.view_class.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "GET Success")

    def test_cbv_post_blocked(self):
        """Test POST on class-based view is blocked"""
        request = self.factory.post('/ocm/dashboard/')
        request.user = self.ocm_user

        view = self.view_class.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 403)


class DecoratorOrderTestCase(TestCase):
    """Test decorator execution order"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()

        self.ocm_user = User.objects.create_user(
            username='ocm_user',
            email='ocm@example.com',
            password='ocmpass123'
        )

        self.regular_user = User.objects.create_user(
            username='regular_user',
            email='regular@example.com',
            password='regularpass123'
        )

        OCMAccess.objects.create(
            user=self.ocm_user,
            granted_by=self.ocm_user,
            reason='Testing',
            is_active=True
        )

    def test_decorator_order_matters(self):
        """Test decorator order: access check before readonly check"""
        # Correct order: require_ocm_access then enforce_readonly
        @require_ocm_access
        @enforce_readonly
        def correct_view(request):
            return HttpResponse("Success")

        # Regular user should be blocked by access check first
        request = self.factory.post('/ocm/dashboard/')
        request.user = self.regular_user

        response = correct_view(request)
        # Should fail at access check (403)
        self.assertEqual(response.status_code, 403)

    def test_combined_decorator_order(self):
        """Test ocm_readonly_view applies decorators in correct order"""
        @ocm_readonly_view
        def test_view(request):
            return HttpResponse("Success")

        # Test with regular user and POST (should fail at access check)
        request = self.factory.post('/ocm/dashboard/')
        request.user = self.regular_user

        response = test_view(request)
        self.assertEqual(response.status_code, 403)

        # Test with OCM user and POST (should fail at readonly check)
        request = self.factory.post('/ocm/dashboard/')
        request.user = self.ocm_user

        response = test_view(request)
        self.assertEqual(response.status_code, 403)
