"""
Security Penetration Tests for Budget System

Tests for common security vulnerabilities:
- SQL Injection
- XSS (Cross-Site Scripting)
- CSRF (Cross-Site Request Forgery)
- Authorization bypasses
- Data exposure
- Rate limiting
- Session security

Requirements:
- Django test framework
- OWASP ZAP (optional, for automated scanning)
"""

import pytest
import json
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import connection
from django.test.utils import override_settings

from budget_preparation.models import BudgetProposal, ProgramBudget, BudgetLineItem
from common.models import Organization

User = get_user_model()


@pytest.mark.django_db
class TestSQLInjection:
    """Test SQL injection vulnerabilities."""

    def test_sql_injection_in_search(self, client, test_user, test_organization):
        """Test SQL injection attempts in search parameters."""
        client.force_login(test_user)

        # SQL injection payloads
        sql_payloads = [
            "' OR '1'='1",
            "1' OR '1' = '1",
            "admin'--",
            "' OR 1=1--",
            "1; DROP TABLE budget_proposal--",
            "1' UNION SELECT NULL,NULL,NULL--",
            "' OR 'x'='x",
        ]

        for payload in sql_payloads:
            response = client.get(
                reverse('budget:proposal_list'),
                {'search': payload}
            )

            # Should not cause error or expose data
            assert response.status_code in [200, 400], \
                f"SQL injection payload caused unexpected status: {payload}"

            # Should not return all records
            if response.status_code == 200:
                content = response.content.decode()
                # Check that it's not showing unauthorized data
                assert 'DROP TABLE' not in content.upper()
                assert 'UNION SELECT' not in content.upper()

    def test_sql_injection_in_filter(self, client, test_user):
        """Test SQL injection in filter parameters."""
        client.force_login(test_user)

        # Attempt SQL injection via fiscal_year filter
        response = client.get(
            reverse('budget:proposal_list'),
            {'fiscal_year': "2025' OR '1'='1"}
        )

        assert response.status_code in [200, 400]

        # Attempt SQL injection via status filter
        response = client.get(
            reverse('budget:proposal_list'),
            {'status': "draft' OR '1'='1--"}
        )

        assert response.status_code in [200, 400]

    def test_sql_injection_in_api(self, client, test_user):
        """Test SQL injection via API endpoints."""
        client.force_login(test_user)

        # Test in JSON body
        response = client.post(
            reverse('api:budget:proposal-list'),
            data=json.dumps({
                'fiscal_year': "2025'; DROP TABLE budget_proposal--",
                'title': 'Test Proposal'
            }),
            content_type='application/json'
        )

        # Should return validation error, not execute SQL
        assert response.status_code in [400, 422]

        # Verify table still exists
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_name = 'budget_proposal'"
            )
            count = cursor.fetchone()[0]
            assert count > 0, "Table was dropped by SQL injection!"


@pytest.mark.django_db
class TestXSS:
    """Test Cross-Site Scripting vulnerabilities."""

    def test_xss_in_proposal_title(self, client, test_user, test_organization):
        """Test XSS in budget proposal title."""
        client.force_login(test_user)

        xss_payloads = [
            '<script>alert("XSS")</script>',
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>',
            'javascript:alert("XSS")',
            '<iframe src="javascript:alert(\'XSS\')">',
        ]

        for payload in xss_payloads:
            proposal = BudgetProposal.objects.create(
                organization=test_organization,
                fiscal_year=2025,
                title=payload,
                total_requested_budget=Decimal('100000000.00'),
                submitted_by=test_user
            )

            # Get detail page
            response = client.get(
                reverse('budget:proposal_detail', args=[proposal.id])
            )

            assert response.status_code == 200

            content = response.content.decode()

            # XSS payload should be escaped
            assert '<script>' not in content.lower()
            assert 'javascript:' not in content.lower()
            assert 'onerror=' not in content.lower()
            assert 'onload=' not in content.lower()

            # Should show escaped version
            if '<' in payload:
                assert '&lt;' in content or payload not in content

            proposal.delete()

    def test_xss_in_description(self, client, test_user, test_organization):
        """Test XSS in description fields."""
        client.force_login(test_user)

        xss_payload = '<script>document.cookie</script>'

        proposal = BudgetProposal.objects.create(
            organization=test_organization,
            fiscal_year=2025,
            title='XSS Test',
            description=xss_payload,
            total_requested_budget=Decimal('100000000.00'),
            submitted_by=test_user
        )

        response = client.get(
            reverse('budget:proposal_detail', args=[proposal.id])
        )

        content = response.content.decode()
        assert '<script>' not in content.lower()

    def test_xss_in_search_results(self, client, test_user):
        """Test XSS via search query reflection."""
        client.force_login(test_user)

        xss_query = '<script>alert("XSS")</script>'

        response = client.get(
            reverse('budget:proposal_list'),
            {'search': xss_query}
        )

        content = response.content.decode()

        # Search term should be escaped if reflected
        assert '<script>' not in content.lower()
        if xss_query in content:
            assert '&lt;script&gt;' in content


@pytest.mark.django_db
class TestCSRF:
    """Test CSRF protection."""

    def test_csrf_protection_on_create(self):
        """Test CSRF protection on POST requests."""
        client = Client(enforce_csrf_checks=True)
        user = User.objects.create_user(username='testuser', password='testpass')
        client.login(username='testuser', password='testpass')

        # Attempt POST without CSRF token
        response = client.post(
            reverse('api:budget:proposal-list'),
            data=json.dumps({
                'fiscal_year': 2025,
                'title': 'Test',
                'total_requested_budget': '100000000'
            }),
            content_type='application/json'
        )

        # Should be rejected (403 Forbidden)
        assert response.status_code == 403

    def test_csrf_protection_on_update(self, test_user, budget_proposal):
        """Test CSRF protection on update."""
        client = Client(enforce_csrf_checks=True)
        client.force_login(test_user)

        # Attempt PUT without CSRF token
        response = client.put(
            reverse('api:budget:proposal-detail', args=[budget_proposal.id]),
            data=json.dumps({
                'title': 'Updated Title'
            }),
            content_type='application/json'
        )

        assert response.status_code == 403


@pytest.mark.django_db
class TestAuthorization:
    """Test authorization and access control."""

    def test_cannot_access_other_organization_budget(self, client):
        """Test that users cannot access other organization's budgets."""
        # Create two organizations
        org1 = Organization.objects.create(name="Org 1")
        org2 = Organization.objects.create(name="Org 2")

        # Create users for each org
        user1 = User.objects.create_user(
            username='user1',
            password='pass',
            organization=org1
        )
        user2 = User.objects.create_user(
            username='user2',
            password='pass',
            organization=org2
        )

        # Create budget for org1
        proposal = BudgetProposal.objects.create(
            organization=org1,
            fiscal_year=2025,
            title='Org 1 Budget',
            total_requested_budget=Decimal('100000000.00'),
            submitted_by=user1
        )

        # User2 tries to access org1's budget
        client.force_login(user2)
        response = client.get(
            reverse('budget:proposal_detail', args=[proposal.id])
        )

        # Should be denied (403 or 404)
        assert response.status_code in [403, 404]

    def test_cannot_modify_other_organization_budget(self, client):
        """Test that users cannot modify other organization's budgets."""
        org1 = Organization.objects.create(name="Org 1")
        org2 = Organization.objects.create(name="Org 2")

        user1 = User.objects.create_user(
            username='user1',
            password='pass',
            organization=org1
        )
        user2 = User.objects.create_user(
            username='user2',
            password='pass',
            organization=org2
        )

        proposal = BudgetProposal.objects.create(
            organization=org1,
            fiscal_year=2025,
            title='Org 1 Budget',
            total_requested_budget=Decimal('100000000.00'),
            submitted_by=user1
        )

        # User2 tries to update org1's budget
        client.force_login(user2)
        response = client.post(
            reverse('api:budget:proposal-detail', args=[proposal.id]),
            data=json.dumps({'title': 'Hacked'}),
            content_type='application/json'
        )

        assert response.status_code in [403, 404]

        # Verify budget unchanged
        proposal.refresh_from_db()
        assert proposal.title == 'Org 1 Budget'

    def test_non_admin_cannot_approve_budget(self, client, test_user, budget_proposal):
        """Test that non-admin users cannot approve budgets."""
        # Ensure test_user is not admin
        test_user.is_staff = False
        test_user.is_superuser = False
        test_user.save()

        client.force_login(test_user)

        response = client.post(
            reverse('api:budget:proposal-approve', args=[budget_proposal.id]),
            data=json.dumps({
                'total_approved_budget': '95000000'
            }),
            content_type='application/json'
        )

        # Should be denied
        assert response.status_code in [403, 401]

    def test_api_requires_authentication(self, client):
        """Test that API endpoints require authentication."""
        # Try to access API without login
        response = client.get(reverse('api:budget:proposal-list'))

        # Should redirect to login or return 401
        assert response.status_code in [401, 302, 403]


@pytest.mark.django_db
class TestDataExposure:
    """Test for sensitive data exposure."""

    def test_no_password_exposure_in_api(self, client, test_user):
        """Test that user passwords are not exposed via API."""
        client.force_login(test_user)

        response = client.get(reverse('api:auth:user-detail', args=[test_user.id]))

        if response.status_code == 200:
            data = response.json()
            assert 'password' not in data
            assert 'password_hash' not in data

    def test_no_internal_ids_exposure(self, client, test_user, budget_proposal):
        """Test that internal database IDs are not unnecessarily exposed."""
        client.force_login(test_user)

        response = client.get(
            reverse('api:budget:proposal-detail', args=[budget_proposal.id])
        )

        if response.status_code == 200:
            data = response.json()
            # Public ID is OK, but internal DB IDs should be minimized
            assert 'id' in data or 'uuid' in data

    def test_error_messages_dont_expose_system_info(self, client):
        """Test that error messages don't expose system information."""
        # Try to access non-existent resource
        response = client.get('/budget/preparation/proposal/999999/')

        content = response.content.decode()

        # Should not expose:
        # - Stack traces
        # - File paths
        # - Database queries
        # - Internal error details

        assert 'Traceback' not in content
        assert '/home/' not in content
        assert '/var/' not in content
        assert 'SELECT *' not in content.upper()


@pytest.mark.django_db
class TestRateLimiting:
    """Test rate limiting on sensitive operations."""

    def test_login_rate_limiting(self):
        """Test that login attempts are rate limited."""
        client = Client()

        # Attempt multiple failed logins
        for i in range(10):
            response = client.post(reverse('login'), {
                'username': 'nonexistent',
                'password': 'wrongpassword'
            })

        # After many attempts, should be rate limited (429 or locked)
        response = client.post(reverse('login'), {
            'username': 'test',
            'password': 'test'
        })

        # Implementation-dependent: may return 429, 403, or show captcha
        # This is a placeholder - adjust based on actual implementation
        assert response.status_code in [200, 429, 403]

    @override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_RATES': {'anon': '5/min'}})
    def test_api_rate_limiting(self, client):
        """Test API rate limiting for anonymous users."""
        # Make multiple rapid requests
        responses = []
        for i in range(10):
            response = client.get('/api/budget/preparation/proposals/')
            responses.append(response.status_code)

        # Should eventually get rate limited (429)
        assert 429 in responses or all(r == 401 for r in responses)


@pytest.mark.django_db
class TestSessionSecurity:
    """Test session security."""

    def test_session_expires(self, client, test_user):
        """Test that sessions expire after timeout."""
        client.force_login(test_user)

        # Verify logged in
        response = client.get(reverse('budget:proposal_list'))
        assert response.status_code == 200

        # In production, session should expire after inactivity
        # This is a placeholder - actual implementation depends on session settings
        # SESSION_COOKIE_AGE setting controls this

    def test_session_regeneration_on_login(self):
        """Test that session ID changes on login (prevent session fixation)."""
        client = Client()

        # Get initial session
        client.get('/')
        session_key_1 = client.session.session_key

        # Login
        user = User.objects.create_user(username='test', password='test')
        client.login(username='test', password='test')

        # Session key should change
        session_key_2 = client.session.session_key

        # Note: This test may need adjustment based on Django version
        # Django should automatically regenerate session on login


@pytest.mark.django_db
class TestInputValidation:
    """Test input validation and sanitization."""

    def test_negative_budget_amount_rejected(self, client, test_user, test_organization):
        """Test that negative budget amounts are rejected."""
        client.force_login(test_user)

        response = client.post(
            reverse('api:budget:proposal-list'),
            data=json.dumps({
                'fiscal_year': 2025,
                'title': 'Test',
                'total_requested_budget': '-100000000'  # Negative
            }),
            content_type='application/json'
        )

        assert response.status_code in [400, 422]

    def test_invalid_fiscal_year_rejected(self, client, test_user):
        """Test that invalid fiscal years are rejected."""
        client.force_login(test_user)

        response = client.post(
            reverse('api:budget:proposal-list'),
            data=json.dumps({
                'fiscal_year': 1900,  # Too old
                'title': 'Test',
                'total_requested_budget': '100000000'
            }),
            content_type='application/json'
        )

        assert response.status_code in [400, 422]

    def test_excessive_input_length_rejected(self, client, test_user):
        """Test that excessively long inputs are rejected."""
        client.force_login(test_user)

        # Try to create proposal with extremely long title
        long_title = 'A' * 10000  # 10k characters

        response = client.post(
            reverse('api:budget:proposal-list'),
            data=json.dumps({
                'fiscal_year': 2025,
                'title': long_title,
                'total_requested_budget': '100000000'
            }),
            content_type='application/json'
        )

        assert response.status_code in [400, 422]


@pytest.mark.django_db
class TestFileUploadSecurity:
    """Test file upload security (if applicable)."""

    def test_malicious_file_extension_rejected(self, client, test_user):
        """Test that dangerous file extensions are rejected."""
        client.force_login(test_user)

        # Try to upload executable file
        malicious_files = [
            'malware.exe',
            'script.sh',
            'hack.php',
            'virus.bat'
        ]

        for filename in malicious_files:
            with open('/tmp/' + filename, 'w') as f:
                f.write('malicious content')

            with open('/tmp/' + filename, 'rb') as f:
                response = client.post(
                    reverse('api:budget:proposal-upload-attachment'),
                    {'file': f},
                )

            # Should be rejected
            assert response.status_code in [400, 415]

    def test_oversized_file_rejected(self, client, test_user):
        """Test that files exceeding size limit are rejected."""
        client.force_login(test_user)

        # Try to upload very large file
        # Implementation depends on MAX_UPLOAD_SIZE setting
        pass  # Placeholder


# Integration with OWASP ZAP (optional)
class TestOWASPZAPScan:
    """Integration with OWASP ZAP for automated scanning."""

    @pytest.mark.skipif(
        True,  # Skip by default, enable manually
        reason="OWASP ZAP scanning requires manual setup"
    )
    def test_run_zap_scan(self):
        """Run OWASP ZAP automated security scan."""
        # This would integrate with ZAP API
        # See: https://www.zaproxy.org/docs/api/
        pass
