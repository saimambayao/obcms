"""
Enhanced Middleware Tests for Organizations App (BMMS Phase 1).

Tests OrganizationMiddleware functionality including:
- Organization extraction from URL patterns
- Access control enforcement
- Thread-local storage management
- Fallback to primary organization
- Superuser bypass behavior
- Enhanced audit logging
- OCM special access patterns
- Thread-safe concurrent requests
- Performance and memory management
- Integration with common middleware
"""

import pytest
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden

from organizations.models import Organization, OrganizationMembership, _thread_locals
from organizations.middleware import OrganizationMiddleware

User = get_user_model()


@pytest.mark.django_db
class TestOrganizationMiddleware:
    """Test OrganizationMiddleware."""

    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        def dummy_get_response(request):
            return None
        return OrganizationMiddleware(dummy_get_response)

    @pytest.fixture
    def factory(self):
        """Create request factory."""
        return RequestFactory()

    @pytest.fixture
    def organization(self):
        """Create test organization."""
        return Organization.objects.create(
            code='OOBC',
            name='Office for Other Bangsamoro Communities',
            org_type='office',
        )

    @pytest.fixture
    def user_with_membership(self, organization):
        """Create user with organization membership."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        OrganizationMembership.objects.create(
            user=user,
            organization=organization,
            role='staff',
            is_primary=True,
        )
        return user

    def test_middleware_extracts_org_from_url(self, middleware, factory, organization):
        """Test middleware extracts organization code from URL."""
        request = factory.get('/moa/OOBC/dashboard/')
        request.user = User.objects.create_user(
            username='superuser',
            is_superuser=True
        )

        org_code = middleware._extract_org_code(request.path)
        assert org_code == 'OOBC'

    def test_middleware_sets_request_organization(self, middleware, factory, user_with_membership, organization):
        """Test middleware sets request.organization attribute."""
        request = factory.get(f'/moa/{organization.code}/dashboard/')
        request.user = user_with_membership

        # Process request
        def dummy_response(req):
            # Check that organization is set
            assert hasattr(req, 'organization')
            assert req.organization == organization
            return None

        middleware.get_response = dummy_response
        middleware(request)

    def test_middleware_denies_unauthorized_access(self, middleware, factory, organization):
        """Test middleware blocks users without membership."""
        # Create user without membership
        user = User.objects.create_user(
            username='unauthorized',
            email='unauth@example.com',
            password='testpass123',
        )

        request = factory.get(f'/moa/{organization.code}/dashboard/')
        request.user = user

        def dummy_response(req):
            return None

        middleware.get_response = dummy_response
        response = middleware(request)

        # Should return 403 Forbidden
        assert isinstance(response, HttpResponseForbidden)
        assert organization.name in str(response.content)

    def test_middleware_allows_superuser_access(self, middleware, factory, organization):
        """Test middleware allows superuser access to any organization."""
        superuser = User.objects.create_user(
            username='admin',
            is_superuser=True,
        )

        request = factory.get(f'/moa/{organization.code}/dashboard/')
        request.user = superuser

        def dummy_response(req):
            assert req.organization == organization
            return None

        middleware.get_response = dummy_response
        response = middleware(request)

        # Should not return 403
        assert not isinstance(response, HttpResponseForbidden)

    def test_middleware_fallback_to_primary_org(self, middleware, factory, user_with_membership, organization):
        """Test middleware uses primary organization when no org in URL."""
        request = factory.get('/dashboard/')  # No /moa/CODE/ in URL
        request.user = user_with_membership

        def dummy_response(req):
            assert hasattr(req, 'organization')
            assert req.organization == organization
            return None

        middleware.get_response = dummy_response
        middleware(request)

    def test_thread_local_cleanup_after_request(self, middleware, factory, user_with_membership, organization):
        """Test thread-local storage is cleaned up after request."""
        request = factory.get(f'/moa/{organization.code}/dashboard/')
        request.user = user_with_membership

        def dummy_response(req):
            # During request, thread-local should have organization
            assert hasattr(_thread_locals, 'organization')
            assert _thread_locals.organization == organization
            return None

        middleware.get_response = dummy_response
        middleware(request)

        # After request, thread-local should be cleaned up
        assert not hasattr(_thread_locals, 'organization')
        assert not hasattr(_thread_locals, 'request')

    def test_invalid_org_code_returns_403(self, middleware, factory):
        """Test middleware returns 403 for invalid organization code."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )

        request = factory.get('/moa/INVALID/dashboard/')
        request.user = user

        def dummy_response(req):
            return None

        middleware.get_response = dummy_response
        response = middleware(request)

        # Should return 403 Forbidden
        assert isinstance(response, HttpResponseForbidden)
        assert 'Invalid organization code' in str(response.content)

    def test_middleware_extracts_org_code_uppercase(self, middleware, factory):
        """Test middleware converts org code to uppercase."""
        request = factory.get('/moa/oobc/dashboard/')
        org_code = middleware._extract_org_code(request.path)
        assert org_code == 'OOBC'

    def test_middleware_no_org_in_url_pattern(self, middleware, factory):
        """Test middleware returns None when URL has no org pattern."""
        request = factory.get('/some/random/path/')
        org_code = middleware._extract_org_code(request.path)
        assert org_code is None

    def test_middleware_unauthenticated_user(self, middleware, factory, organization):
        """Test middleware behavior with unauthenticated user."""
        from django.contrib.auth.models import AnonymousUser

        request = factory.get(f'/moa/{organization.code}/dashboard/')
        request.user = AnonymousUser()

        def dummy_response(req):
            # Should not crash, but organization should not be set
            # or should handle gracefully
            return None

        middleware.get_response = dummy_response
        response = middleware(request)

        # Depending on implementation, may return 403 or set org to None
        # This test validates middleware doesn't crash
        assert response is None or isinstance(response, HttpResponseForbidden)

    def test_middleware_multiple_organizations_user(self, middleware, factory):
        """Test middleware with user having multiple organization memberships."""
        org1 = Organization.objects.create(
            code='OOBC',
            name='Office for Other Bangsamoro Communities',
            org_type='office',
        )
        org2 = Organization.objects.create(
            code='MOH',
            name='Ministry of Health',
            org_type='ministry',
        )

        user = User.objects.create_user(
            username='multiorg',
            email='multi@example.com',
            password='testpass123',
        )

        # User is member of both organizations
        OrganizationMembership.objects.create(
            user=user,
            organization=org1,
            role='staff',
            is_primary=True,
        )
        OrganizationMembership.objects.create(
            user=user,
            organization=org2,
            role='viewer',
            is_primary=False,
        )

        # Request to org2
        request = factory.get(f'/moa/{org2.code}/dashboard/')
        request.user = user

        def dummy_response(req):
            # Should allow access since user is member
            assert req.organization == org2
            return None

        middleware.get_response = dummy_response
        response = middleware(request)

        assert not isinstance(response, HttpResponseForbidden)

    def test_middleware_thread_local_isolation(self, middleware, factory, organization):
        """Test thread-local storage doesn't leak between requests."""
        user1 = User.objects.create_user(username='user1')
        user2 = User.objects.create_user(username='user2')

        OrganizationMembership.objects.create(
            user=user1,
            organization=organization,
            role='staff',
            is_primary=True,
        )

        # First request
        request1 = factory.get(f'/moa/{organization.code}/page1/')
        request1.user = user1

        def dummy_response1(req):
            assert _thread_locals.organization == organization
            return None

        middleware.get_response = dummy_response1
        middleware(request1)

        # Thread-local should be cleaned up
        assert not hasattr(_thread_locals, 'organization')

        # Second request (different user, no org in URL)
        request2 = factory.get('/page2/')
        request2.user = user2

        def dummy_response2(req):
            # Should not have organization from previous request
            org = getattr(_thread_locals, 'organization', None)
            # Either None or user2's primary org, but NOT user1's org
            if org:
                assert org != organization or user2.organization_memberships.filter(
                    organization=organization
                ).exists()
            return None

        middleware.get_response = dummy_response2
        middleware(request2)


@pytest.mark.django_db
class TestEnhancedMiddlewareFeatures:
    """Test enhanced middleware features."""

    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        def dummy_get_response(request):
            return None
        return OrganizationMiddleware(dummy_get_response)

    @pytest.fixture
    def factory(self):
        """Create request factory."""
        return RequestFactory()

    @pytest.fixture
    def organizations(self):
        """Create test organizations."""
        oobc = Organization.objects.create(
            code='OOBC',
            name='Office for Other Bangsamoro Communities',
            org_type='office',
        )
        moh = Organization.objects.create(
            code='MOH',
            name='Ministry of Health',
            org_type='ministry',
        )
        ocm = Organization.objects.create(
            code='OCM',
            name='Office of the Chief Minister',
            org_type='office',
        )
        return {'oobc': oobc, 'moh': moh, 'ocm': ocm}

    @pytest.fixture
    def ocm_user(self, organizations):
        """Create OCM user."""
        user = User.objects.create_user(
            username='ocm_user',
            email='ocm@example.com',
            password='testpass123',
            user_type='cm_office'
        )
        OrganizationMembership.objects.create(
            user=user,
            organization=organizations['ocm'],
            role='admin',
            is_primary=True,
        )
        return user

    def test_ocm_user_access_any_organization(self, middleware, factory, organizations):
        """Test OCM user can access any organization."""
        oobc_user = User.objects.create_user(
            username='oobc_user',
            email='oobc@example.com',
            password='testpass123'
        )
        OrganizationMembership.objects.create(
            user=oobc_user,
            organization=organizations['oobc'],
            role='staff',
            is_primary=True,
        )

        request = factory.get(f'/moa/{organizations["moh"].code}/dashboard/')
        request.user = organizations['ocm']

        def dummy_response(req):
            assert req.organization == organizations['moh']
            return None

        middleware.get_response = dummy_response
        response = middleware(request)

        # OCM user should have access
        assert not isinstance(response, HttpResponseForbidden)

    def test_audit_logging_context_changes(self, middleware, factory, organizations):
        """Test audit logging for organization context changes."""
        import logging
        from unittest.mock import Mock

        # Mock audit logger
        with patch('organizations.middleware.audit_logger') as mock_audit:
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123'
            )
            OrganizationMembership.objects.create(
                user=user,
                organization=organizations['moh'],
                role='staff',
                is_primary=True,
            )

            request = factory.get(f'/moa/{organizations["moh"].code}/dashboard/')
            request.user = user

            def dummy_response(req):
                return None

            middleware.get_response = dummy_response
            middleware(request)

            # Verify audit logging was called
            mock_audit.info.assert_called()
            call_args = mock_audit.info.call_args[0][0]
            assert 'Organization context set' in call_args
            assert organizations['moh'].code in call_args

    def test_security_logging_unauthorized_access(self, middleware, factory, organizations):
        """Test security logging for unauthorized access attempts."""
        from unittest.mock import Mock

        # Mock security logger
        with patch('organizations.middleware.security_logger') as mock_security:
            user = User.objects.create_user(
                username='unauthorized',
                email='unauth@example.com',
                password='testpass123'
            )

            request = factory.get(f'/moa/{organizations["moh"].code}/dashboard/')
            request.user = user

            def dummy_response(req):
                return None

            middleware.get_response = dummy_response
            response = middleware(request)

            # Should return 403 and log security event
            assert isinstance(response, HttpResponseForbidden)
            mock_security.warning.assert_called()

    def test_thread_context_utilities(self, middleware, factory, organizations):
        """Test thread-local context utilities."""
        from organizations.middleware import get_thread_context, is_ocm_context

        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        OrganizationMembership.objects.create(
            user=user,
            organization=organizations['moh'],
            role='staff',
            is_primary=True,
        )

        request = factory.get(f'/moa/{organizations["moh"].code}/dashboard/')
        request.user = user

        def dummy_response(req):
            # Test context utilities during request
            context = get_thread_context()
            assert context['organization_id'] == organizations['moh'].id
            assert context['organization_code'] == organizations['moh'].code
            assert context['user_id'] == user.id
            assert not context['is_ocm_user']  # Regular user
            assert not is_ocm_context()
            return None

        middleware.get_response = dummy_response
        middleware(request)

    def test_ocm_context_detection(self, middleware, factory, organizations):
        """Test OCM context detection."""
        from organizations.middleware import get_thread_context, is_ocm_context

        request = factory.get(f'/moa/{organizations["moh"].code}/dashboard/')
        request.user = organizations['ocm']

        def dummy_response(req):
            # Test OCM context detection
            context = get_thread_context()
            assert context['is_ocm_user']  # OCM user
            assert is_ocm_context()
            return None

        middleware.get_response = dummy_response
        middleware(request)

    def test_performance_monitoring(self, middleware, factory, organizations):
        """Test performance monitoring features."""
        import time

        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        OrganizationMembership.objects.create(
            user=user,
            organization=organizations['moh'],
            role='staff',
            is_primary=True,
        )

        request = factory.get(f'/moa/{organizations["moh"].code}/dashboard/')
        request.user = user

        def dummy_response(req):
            # Simulate some processing time
            time.sleep(0.01)
            return None

        middleware.get_response = dummy_response

        # Record start time
        start_time = time.time()
        middleware(request)
        end_time = time.time()

        # Should complete quickly (under 100ms for simple request)
        assert (end_time - start_time) < 0.1

    def test_thread_local_cleanup_comprehensive(self, middleware, factory, organizations):
        """Test comprehensive thread-local cleanup."""
        from organizations.middleware import get_thread_context

        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        OrganizationMembership.objects.create(
            user=user,
            organization=organizations['moh'],
            role='staff',
            is_primary=True,
        )

        request = factory.get(f'/moa/{organizations["moh"].code}/dashboard/')
        request.user = user

        def dummy_response(req):
            # During request, context should be populated
            context = get_thread_context()
            assert 'organization_id' in context
            assert 'user_id' in context
            return None

        middleware.get_response = dummy_response
        middleware(request)

        # After request, context should be cleaned up
        context = get_thread_context()
        assert context == {}

    def test_client_ip_extraction(self, middleware, factory, organizations):
        """Test client IP extraction with various headers."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        OrganizationMembership.objects.create(
            user=user,
            organization=organizations['moh'],
            role='staff',
            is_primary=True,
        )

        # Test with X-Forwarded-For header
        request = factory.get(f'/moa/{organizations["moh"].code}/dashboard/')
        request.user = user
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.100, 10.0.0.1'

        ip = middleware._get_client_ip(request)
        assert ip == '192.168.1.100'

        # Test with Cloudflare header
        request = factory.get(f'/moa/{organizations["moh"].code}/dashboard/')
        request.user = user
        request.META['HTTP_CF_CONNECTING_IP'] = '203.0.113.1'

        ip = middleware._get_client_ip(request)
        assert ip == '203.0.113.1'

        # Test fallback to REMOTE_ADDR
        request = factory.get(f'/moa/{organizations["moh"].code}/dashboard/')
        request.user = user
        request.META['REMOTE_ADDR'] = '127.0.0.1'

        ip = middleware._get_client_ip(request)
        assert ip == '127.0.0.1'

    def test_mode_aware_behavior_obcms(self, middleware, factory, organizations):
        """Test OBCMS mode auto-injection of default organization."""
        from unittest.mock import patch

        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        request = factory.get('/dashboard/')
        request.user = user

        with patch('organizations.middleware.is_obcms_mode', return_value=True):
            with patch('organizations.middleware.get_or_create_default_organization') as mock_default:
                mock_default.return_value = (organizations['oobc'], None)

                def dummy_response(req):
                    assert req.organization == organizations['oobc']
                    return None

                middleware.get_response = dummy_response
                middleware(request)

                # Should call default organization creation
                mock_default.assert_called_once()

    def test_error_handling_and_logging(self, middleware, factory, organizations):
        """Test error handling and logging."""
        from unittest.mock import patch

        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        request = factory.get(f'/moa/{organizations["moh"].code}/dashboard/')
        request.user = user

        # Mock get_response to raise an exception
        def failing_response(req):
            raise ValueError("Test error")

        middleware.get_response = failing_response

        with patch('organizations.middleware.security_logger') as mock_security:
            # Should re-raise the exception
            with pytest.raises(ValueError):
                middleware(request)

            # Should log the error
            mock_security.error.assert_called()
            call_args = mock_security.error.call_args[0][0]
            assert 'Organization context error' in call_args
            assert 'Test error' in call_args
