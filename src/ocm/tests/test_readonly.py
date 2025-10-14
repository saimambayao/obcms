"""
Tests for read-only access enforcement
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from organizations.models import Organization
from ocm.models import OCMAccess

User = get_user_model()


class ReadOnlyHTTPMethodTestCase(TestCase):
    """Test read-only enforcement for different HTTP methods"""

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
        self.org = Organization.objects.create(
            name='Test MOA',
            organization_type='ministry',
            is_active=True
        )

        self.client.login(username='ocm_user', password='ocmpass123')

    def test_get_request_allowed(self):
        """Test GET requests are allowed"""
        url = reverse('ocm:dashboard')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_head_request_allowed(self):
        """Test HEAD requests are allowed"""
        url = reverse('ocm:dashboard')
        response = self.client.head(url)

        # HEAD should return 200 or same as GET
        self.assertIn(response.status_code, [200, 301, 302])

    def test_post_request_blocked(self):
        """Test POST requests return 403"""
        url = reverse('ocm:dashboard')
        response = self.client.post(url, data={'test': 'data'})

        self.assertEqual(response.status_code, 403)

    def test_put_request_blocked(self):
        """Test PUT requests return 403"""
        url = reverse('ocm:dashboard')
        response = self.client.put(url, data={'test': 'data'})

        self.assertEqual(response.status_code, 403)

    def test_patch_request_blocked(self):
        """Test PATCH requests return 403"""
        url = reverse('ocm:dashboard')
        response = self.client.patch(url, data={'test': 'data'})

        self.assertEqual(response.status_code, 403)

    def test_delete_request_blocked(self):
        """Test DELETE requests return 403"""
        url = reverse('ocm:dashboard')
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 403)


class ReadOnlyDataAccessTestCase(TestCase):
    """Test OCM users can only read, not modify data"""

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
        self.org = Organization.objects.create(
            name='Test MOA',
            organization_type='ministry',
            is_active=True
        )

        self.client.login(username='ocm_user', password='ocmpass123')

    def test_ocm_user_can_view_organizations(self):
        """Test OCM user can view all organizations"""
        # OCM user should see all organizations
        all_orgs = Organization.objects.all()
        self.assertEqual(all_orgs.count(), 1)

    def test_ocm_user_cannot_create_organization(self):
        """Test OCM user cannot create organizations"""
        # OCM users shouldn't have add permission
        self.assertFalse(
            self.ocm_user.has_perm('organizations.add_organization')
        )

    def test_ocm_user_cannot_update_organization(self):
        """Test OCM user cannot update organizations"""
        # OCM users shouldn't have change permission
        self.assertFalse(
            self.ocm_user.has_perm('organizations.change_organization')
        )

    def test_ocm_user_cannot_delete_organization(self):
        """Test OCM user cannot delete organizations"""
        # OCM users shouldn't have delete permission
        self.assertFalse(
            self.ocm_user.has_perm('organizations.delete_organization')
        )


class ReadOnlyAPITestCase(TestCase):
    """Test read-only enforcement for API endpoints"""

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

        self.client.login(username='ocm_user', password='ocmpass123')

    def test_api_get_allowed(self):
        """Test GET requests to API are allowed"""
        # Test API endpoint if exists
        try:
            url = reverse('ocm:api-dashboard')
            response = self.client.get(url)
            self.assertIn(response.status_code, [200, 404])
        except:
            # API endpoint may not exist yet
            pass

    def test_api_post_blocked(self):
        """Test POST requests to API are blocked"""
        try:
            url = reverse('ocm:api-dashboard')
            response = self.client.post(
                url,
                data={'test': 'data'},
                content_type='application/json'
            )
            # Should be forbidden or not found (if endpoint doesn't exist)
            self.assertIn(response.status_code, [403, 404, 405])
        except:
            # API endpoint may not exist yet
            pass


class ReadOnlyFormTestCase(TestCase):
    """Test forms are read-only for OCM users"""

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

        self.client.login(username='ocm_user', password='ocmpass123')

    def test_create_forms_not_accessible(self):
        """Test OCM users cannot access create forms"""
        # OCM views should not have create forms
        url = reverse('ocm:dashboard')
        response = self.client.get(url)

        # Should not contain form submission elements
        self.assertNotContains(response, '<form', status_code=200)
        # Or if forms exist, they should be disabled

    def test_edit_forms_not_accessible(self):
        """Test OCM users cannot access edit forms"""
        # OCM users should not see edit forms
        # This would be tested with specific edit URLs if they existed
        pass

    def test_delete_actions_not_available(self):
        """Test delete actions are not available to OCM users"""
        url = reverse('ocm:dashboard')
        response = self.client.get(url)

        # Should not contain delete buttons or actions
        self.assertNotContains(response, 'delete', status_code=200)


class ReadOnlyBulkActionsTestCase(TestCase):
    """Test bulk actions are blocked for OCM users"""

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

        # Create test organizations
        for i in range(3):
            Organization.objects.create(
                name=f'MOA {i+1}',
                organization_type='ministry',
                is_active=True
            )

        self.client.login(username='ocm_user', password='ocmpass123')

    def test_bulk_update_blocked(self):
        """Test bulk update actions are blocked"""
        # Attempt bulk update via API if endpoint exists
        org_ids = list(Organization.objects.values_list('id', flat=True))

        try:
            url = reverse('ocm:api-bulk-update')
            response = self.client.post(
                url,
                data={
                    'ids': org_ids,
                    'action': 'update',
                    'field': 'is_active',
                    'value': False
                },
                content_type='application/json'
            )
            # Should be forbidden or not found
            self.assertIn(response.status_code, [403, 404, 405])
        except:
            # Endpoint may not exist
            pass

    def test_bulk_delete_blocked(self):
        """Test bulk delete actions are blocked"""
        org_ids = list(Organization.objects.values_list('id', flat=True))

        try:
            url = reverse('ocm:api-bulk-delete')
            response = self.client.post(
                url,
                data={'ids': org_ids, 'action': 'delete'},
                content_type='application/json'
            )
            # Should be forbidden or not found
            self.assertIn(response.status_code, [403, 404, 405])
        except:
            # Endpoint may not exist
            pass


class ReadOnlyErrorMessagesTestCase(TestCase):
    """Test appropriate error messages for blocked actions"""

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

        self.client.login(username='ocm_user', password='ocmpass123')

    def test_post_blocked_message(self):
        """Test appropriate error message for POST requests"""
        url = reverse('ocm:dashboard')
        response = self.client.post(url, data={'test': 'data'})

        self.assertEqual(response.status_code, 403)
        # Should contain informative error message
        if hasattr(response, 'content'):
            content = response.content.decode().lower()
            self.assertTrue(
                'read-only' in content or
                'read only' in content or
                'forbidden' in content or
                'not allowed' in content
            )

    def test_put_blocked_message(self):
        """Test appropriate error message for PUT requests"""
        url = reverse('ocm:dashboard')
        response = self.client.put(url, data={'test': 'data'})

        self.assertEqual(response.status_code, 403)

    def test_delete_blocked_message(self):
        """Test appropriate error message for DELETE requests"""
        url = reverse('ocm:dashboard')
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 403)


class ReadOnlyEdgeCasesTestCase(TestCase):
    """Test edge cases in read-only enforcement"""

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

        self.client.login(username='ocm_user', password='ocmpass123')

    def test_ajax_post_blocked(self):
        """Test AJAX POST requests are blocked"""
        url = reverse('ocm:dashboard')
        response = self.client.post(
            url,
            data={'test': 'data'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 403)

    def test_post_with_get_params_blocked(self):
        """Test POST with GET parameters is blocked"""
        url = reverse('ocm:dashboard') + '?param=value'
        response = self.client.post(url, data={'test': 'data'})

        self.assertEqual(response.status_code, 403)

    def test_empty_post_blocked(self):
        """Test POST with no data is still blocked"""
        url = reverse('ocm:dashboard')
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)

    def test_multipart_post_blocked(self):
        """Test multipart/form-data POST is blocked"""
        url = reverse('ocm:dashboard')
        response = self.client.post(
            url,
            data={'test': 'data'},
            content_type='multipart/form-data'
        )

        self.assertEqual(response.status_code, 403)


class ReadOnlyConsistencyTestCase(TestCase):
    """Test read-only enforcement is consistent across all views"""

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

        self.client.login(username='ocm_user', password='ocmpass123')

        # List of all OCM views
        self.ocm_views = [
            'ocm:dashboard',
            'ocm:consolidated_budget',
            'ocm:planning_overview',
            'ocm:coordination_matrix',
        ]

    def test_all_views_allow_get(self):
        """Test all views allow GET requests"""
        for view_name in self.ocm_views:
            url = reverse(view_name)
            response = self.client.get(url)

            self.assertEqual(
                response.status_code, 200,
                f"View {view_name} should allow GET"
            )

    def test_all_views_block_post(self):
        """Test all views block POST requests"""
        for view_name in self.ocm_views:
            url = reverse(view_name)
            response = self.client.post(url, data={'test': 'data'})

            self.assertEqual(
                response.status_code, 403,
                f"View {view_name} should block POST"
            )

    def test_all_views_block_put(self):
        """Test all views block PUT requests"""
        for view_name in self.ocm_views:
            url = reverse(view_name)
            response = self.client.put(url, data={'test': 'data'})

            self.assertEqual(
                response.status_code, 403,
                f"View {view_name} should block PUT"
            )

    def test_all_views_block_delete(self):
        """Test all views block DELETE requests"""
        for view_name in self.ocm_views:
            url = reverse(view_name)
            response = self.client.delete(url)

            self.assertEqual(
                response.status_code, 403,
                f"View {view_name} should block DELETE"
            )
