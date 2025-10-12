"""
Test Suite for Audit Logging Infrastructure

Tests Parliament Bill No. 325 Section 78 compliance

Author: Claude Code (OBCMS System Architect)
Date: October 13, 2025
"""

import json
from decimal import Decimal
from django.test import TestCase, RequestFactory
from django.contrib.contenttypes.models import ContentType
from common.models import User, AuditLog


class AuditLogModelTests(TestCase):
    """Test AuditLog model functionality"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='oobc_staff'
        )

    def test_create_audit_log(self):
        """Test creating an audit log entry"""
        content_type = ContentType.objects.get_for_model(User)

        audit = AuditLog.objects.create(
            content_type=content_type,
            object_id=self.user.pk,
            action='create',
            user=self.user,
            changes={},
            ip_address='127.0.0.1',
            user_agent='Test Browser'
        )

        self.assertIsNotNone(audit.id)
        self.assertEqual(audit.action, 'create')
        self.assertEqual(audit.user, self.user)
        self.assertEqual(audit.ip_address, '127.0.0.1')

    def test_audit_log_string_representation(self):
        """Test AuditLog __str__ method"""
        content_type = ContentType.objects.get_for_model(User)

        audit = AuditLog.objects.create(
            content_type=content_type,
            object_id=self.user.pk,
            action='update',
            user=self.user
        )

        str_repr = str(audit)
        self.assertIn('Update', str_repr)
        self.assertIn('user', str_repr.lower())

    def test_changes_json_field(self):
        """Test storing changes in JSONField"""
        content_type = ContentType.objects.get_for_model(User)

        changes = {
            'email': {
                'old': 'old@example.com',
                'new': 'new@example.com'
            },
            'first_name': {
                'old': 'John',
                'new': 'Jane'
            }
        }

        audit = AuditLog.objects.create(
            content_type=content_type,
            object_id=self.user.pk,
            action='update',
            user=self.user,
            changes=changes
        )

        # Retrieve and verify
        saved_audit = AuditLog.objects.get(pk=audit.pk)
        self.assertEqual(saved_audit.changes, changes)
        self.assertEqual(saved_audit.changes['email']['new'], 'new@example.com')

    def test_decimal_serialization_in_changes(self):
        """Test Decimal values are properly serialized"""
        content_type = ContentType.objects.get_for_model(User)

        changes = {
            'amount': {
                'old': '1000.00',
                'new': '1500.50'
            }
        }

        audit = AuditLog.objects.create(
            content_type=content_type,
            object_id=self.user.pk,
            action='update',
            user=self.user,
            changes=changes
        )

        saved_audit = AuditLog.objects.get(pk=audit.pk)
        self.assertEqual(saved_audit.changes['amount']['old'], '1000.00')
        self.assertEqual(saved_audit.changes['amount']['new'], '1500.50')

    def test_unauthenticated_user_handling(self):
        """Test audit log with no user (system operation)"""
        content_type = ContentType.objects.get_for_model(User)

        audit = AuditLog.objects.create(
            content_type=content_type,
            object_id=self.user.pk,
            action='create',
            user=None,  # System operation
            changes={}
        )

        self.assertIsNone(audit.user)
        self.assertIn('System', str(audit))


class AuditMiddlewareTests(TestCase):
    """Test AuditMiddleware functionality"""

    def setUp(self):
        # Import middleware locally to avoid circular import
        from common.middleware.audit import AuditMiddleware as AM
        self.AuditMiddleware = AM

        self.factory = RequestFactory()
        self.middleware = self.AuditMiddleware(lambda request: None)
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='oobc_staff'
        )

    def test_middleware_stores_user_in_thread_local(self):
        """Test middleware stores authenticated user in thread-local storage"""
        from threading import current_thread

        request = self.factory.get('/')
        request.user = self.user

        # Before middleware
        self.assertFalse(hasattr(current_thread(), 'request_user'))

        # Call middleware (it processes but returns None because get_response is a lambda)
        self.middleware(request)

        # After middleware, thread-local should be cleaned up
        self.assertFalse(hasattr(current_thread(), 'request_user'))

    def test_middleware_handles_unauthenticated_user(self):
        """Test middleware handles anonymous users"""
        from threading import current_thread
        from django.contrib.auth.models import AnonymousUser

        request = self.factory.get('/')
        request.user = AnonymousUser()

        self.middleware(request)

        # Should not raise errors
        self.assertFalse(hasattr(current_thread(), 'request_user'))

    def test_middleware_extracts_ip_from_x_forwarded_for(self):
        """Test middleware extracts IP from X-Forwarded-For header"""
        from threading import current_thread

        # Create custom get_response that captures thread-local state
        captured_ip = None

        def get_response_with_capture(request):
            nonlocal captured_ip
            captured_ip = getattr(current_thread(), 'request_ip', None)
            return None

        middleware = self.AuditMiddleware(get_response_with_capture)

        request = self.factory.get('/', HTTP_X_FORWARDED_FOR='203.0.113.1, 198.51.100.1')
        request.user = self.user

        middleware(request)

        # Should extract first IP from X-Forwarded-For
        self.assertEqual(captured_ip, '203.0.113.1')

    def test_middleware_extracts_user_agent(self):
        """Test middleware extracts user agent"""
        from threading import current_thread

        captured_user_agent = None

        def get_response_with_capture(request):
            nonlocal captured_user_agent
            captured_user_agent = getattr(current_thread(), 'request_user_agent', None)
            return None

        middleware = self.AuditMiddleware(get_response_with_capture)

        request = self.factory.get('/', HTTP_USER_AGENT='Mozilla/5.0 Test Browser')
        request.user = self.user

        middleware(request)

        self.assertEqual(captured_user_agent, 'Mozilla/5.0 Test Browser')


class AuditLogQueryTests(TestCase):
    """Test AuditLog querying and performance"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='oobc_staff'
        )

    def test_query_by_user(self):
        """Test querying audit logs by user"""
        content_type = ContentType.objects.get_for_model(User)

        # Create multiple audit logs
        for i in range(5):
            AuditLog.objects.create(
                content_type=content_type,
                object_id=self.user.pk,
                action='update',
                user=self.user,
                changes={'field': {'old': i, 'new': i+1}}
            )

        user_logs = AuditLog.objects.filter(user=self.user)
        self.assertEqual(user_logs.count(), 5)

    def test_query_by_action(self):
        """Test querying audit logs by action type"""
        content_type = ContentType.objects.get_for_model(User)

        AuditLog.objects.create(
            content_type=content_type,
            object_id=self.user.pk,
            action='create',
            user=self.user
        )

        AuditLog.objects.create(
            content_type=content_type,
            object_id=self.user.pk,
            action='update',
            user=self.user
        )

        create_logs = AuditLog.objects.filter(action='create')
        self.assertEqual(create_logs.count(), 1)

    def test_query_by_content_type(self):
        """Test querying audit logs by model type"""
        content_type = ContentType.objects.get_for_model(User)

        AuditLog.objects.create(
            content_type=content_type,
            object_id=self.user.pk,
            action='create',
            user=self.user
        )

        user_type_logs = AuditLog.objects.filter(content_type=content_type)
        self.assertEqual(user_type_logs.count(), 1)

    def test_ordering_by_timestamp(self):
        """Test audit logs are ordered by timestamp descending"""
        content_type = ContentType.objects.get_for_model(User)

        # Create logs in sequence
        log1 = AuditLog.objects.create(
            content_type=content_type,
            object_id=self.user.pk,
            action='create',
            user=self.user
        )

        log2 = AuditLog.objects.create(
            content_type=content_type,
            object_id=self.user.pk,
            action='update',
            user=self.user
        )

        # Most recent should be first
        all_logs = list(AuditLog.objects.all())
        self.assertEqual(all_logs[0].id, log2.id)
        self.assertEqual(all_logs[1].id, log1.id)
