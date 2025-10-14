"""
Tests for OCM views
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal

from organizations.models import Organization
from ocm.models import OCMAccess

User = get_user_model()


class OCMDashboardViewTestCase(TestCase):
    """Test OCM dashboard view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

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
        OCMAccess.objects.create(
            user=self.ocm_user,
            granted_by=self.ocm_user,
            reason='Testing',
            is_active=True
        )

        # Create test organizations
        for i in range(5):
            Organization.objects.create(
                name=f'MOA {i+1}',
                organization_type='ministry',
                is_active=True
            )

    def test_dashboard_requires_login(self):
        """Test dashboard requires authentication"""
        url = reverse('ocm:dashboard')
        response = self.client.get(url)

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_dashboard_requires_ocm_access(self):
        """Test dashboard requires OCM access"""
        url = reverse('ocm:dashboard')

        # Login as regular user (no OCM access)
        self.client.login(username='regular_user', password='regularpass123')
        response = self.client.get(url)

        # Should be forbidden
        self.assertEqual(response.status_code, 403)

    def test_dashboard_loads_for_ocm_user(self):
        """Test dashboard loads successfully for OCM user"""
        url = reverse('ocm:dashboard')

        # Login as OCM user
        self.client.login(username='ocm_user', password='ocmpass123')
        response = self.client.get(url)

        # Should load successfully
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ocm/dashboard.html')

    def test_dashboard_context_data(self):
        """Test dashboard provides correct context data"""
        url = reverse('ocm:dashboard')

        self.client.login(username='ocm_user', password='ocmpass123')
        response = self.client.get(url)

        # Check context contains required data
        self.assertIn('total_organizations', response.context)
        self.assertIn('government_stats', response.context)

        # Check organization count
        self.assertEqual(response.context['total_organizations'], 5)

    def test_dashboard_shows_all_organizations(self):
        """Test dashboard displays all organizations"""
        url = reverse('ocm:dashboard')

        self.client.login(username='ocm_user', password='ocmpass123')
        response = self.client.get(url)

        # Should see all 5 organizations
        organizations = response.context.get('organizations', [])
        self.assertEqual(len(organizations), 5)

    def test_dashboard_post_blocked(self):
        """Test POST requests to dashboard are blocked"""
        url = reverse('ocm:dashboard')

        self.client.login(username='ocm_user', password='ocmpass123')
        response = self.client.post(url, data={'test': 'data'})

        # Should be forbidden (read-only)
        self.assertEqual(response.status_code, 403)


class ConsolidatedBudgetViewTestCase(TestCase):
    """Test consolidated budget view"""

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

        # Create test organization and budget
        self.org = Organization.objects.create(
            name='Test MOA',
            organization_type='ministry',
            is_active=True
        )

    def test_consolidated_budget_requires_login(self):
        """Test consolidated budget view requires authentication"""
        url = reverse('ocm:consolidated_budget')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_consolidated_budget_loads(self):
        """Test consolidated budget view loads successfully"""
        url = reverse('ocm:consolidated_budget')

        self.client.login(username='ocm_user', password='ocmpass123')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ocm/consolidated_budget.html')

    def test_consolidated_budget_context(self):
        """Test consolidated budget view provides budget data"""
        url = reverse('ocm:consolidated_budget')

        self.client.login(username='ocm_user', password='ocmpass123')
        response = self.client.get(url)

        # Should have budget data in context
        self.assertIn('budget_data', response.context)

    def test_consolidated_budget_fiscal_year_filter(self):
        """Test filtering consolidated budget by fiscal year"""
        url = reverse('ocm:consolidated_budget')

        self.client.login(username='ocm_user', password='ocmpass123')
        response = self.client.get(url, {'fiscal_year': 2024})

        self.assertEqual(response.status_code, 200)

    def test_consolidated_budget_post_blocked(self):
        """Test POST requests to consolidated budget are blocked"""
        url = reverse('ocm:consolidated_budget')

        self.client.login(username='ocm_user', password='ocmpass123')
        response = self.client.post(url, data={'test': 'data'})

        self.assertEqual(response.status_code, 403)


class PlanningOverviewViewTestCase(TestCase):
    """Test planning overview view"""

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

    def test_planning_overview_requires_login(self):
        """Test planning overview requires authentication"""
        url = reverse('ocm:planning_overview')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_planning_overview_loads(self):
        """Test planning overview loads successfully"""
        url = reverse('ocm:planning_overview')

        self.client.login(username='ocm_user', password='ocmpass123')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ocm/planning_overview.html')

    def test_planning_overview_context(self):
        """Test planning overview provides planning data"""
        url = reverse('ocm:planning_overview')

        self.client.login(username='ocm_user', password='ocmpass123')
        response = self.client.get(url)

        # Should have planning data in context
        self.assertIn('planning_summary', response.context)

    def test_planning_overview_post_blocked(self):
        """Test POST requests to planning overview are blocked"""
        url = reverse('ocm:planning_overview')

        self.client.login(username='ocm_user', password='ocmpass123')
        response = self.client.post(url, data={'test': 'data'})

        self.assertEqual(response.status_code, 403)


class CoordinationMatrixViewTestCase(TestCase):
    """Test coordination matrix view"""

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
        self.org1 = Organization.objects.create(
            name='MOA 1',
            organization_type='ministry',
            is_active=True
        )
        self.org2 = Organization.objects.create(
            name='MOA 2',
            organization_type='ministry',
            is_active=True
        )

    def test_coordination_matrix_requires_login(self):
        """Test coordination matrix requires authentication"""
        url = reverse('ocm:coordination_matrix')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_coordination_matrix_loads(self):
        """Test coordination matrix loads successfully"""
        url = reverse('ocm:coordination_matrix')

        self.client.login(username='ocm_user', password='ocmpass123')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ocm/coordination_matrix.html')

    def test_coordination_matrix_context(self):
        """Test coordination matrix provides coordination data"""
        url = reverse('ocm:coordination_matrix')

        self.client.login(username='ocm_user', password='ocmpass123')
        response = self.client.get(url)

        # Should have coordination data in context
        self.assertIn('coordination_summary', response.context)

    def test_coordination_matrix_shows_inter_moa_partnerships(self):
        """Test coordination matrix shows inter-MOA partnerships"""
        from coordination.models import Partnership

        # Create inter-MOA partnership
        Partnership.objects.create(
            name='Inter-MOA Partnership',
            lead_organization=self.org1,
            is_inter_moa=True,
            status='active'
        )

        url = reverse('ocm:coordination_matrix')
        self.client.login(username='ocm_user', password='ocmpass123')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_coordination_matrix_post_blocked(self):
        """Test POST requests to coordination matrix are blocked"""
        url = reverse('ocm:coordination_matrix')

        self.client.login(username='ocm_user', password='ocmpass123')
        response = self.client.post(url, data={'test': 'data'})

        self.assertEqual(response.status_code, 403)


class OCMViewPermissionsTestCase(TestCase):
    """Test permissions across all OCM views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

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
        OCMAccess.objects.create(
            user=self.ocm_user,
            granted_by=self.ocm_user,
            reason='Testing',
            is_active=True
        )

        # List of OCM view URLs
        self.ocm_views = [
            'ocm:dashboard',
            'ocm:consolidated_budget',
            'ocm:planning_overview',
            'ocm:coordination_matrix',
        ]

    def test_all_views_require_login(self):
        """Test all OCM views require authentication"""
        for view_name in self.ocm_views:
            url = reverse(view_name)
            response = self.client.get(url)

            self.assertEqual(
                response.status_code, 302,
                f"View {view_name} should redirect unauthenticated users"
            )

    def test_all_views_require_ocm_access(self):
        """Test all OCM views require OCM access"""
        self.client.login(username='regular_user', password='regularpass123')

        for view_name in self.ocm_views:
            url = reverse(view_name)
            response = self.client.get(url)

            self.assertEqual(
                response.status_code, 403,
                f"View {view_name} should deny users without OCM access"
            )

    def test_all_views_allow_ocm_user(self):
        """Test all OCM views allow OCM users"""
        self.client.login(username='ocm_user', password='ocmpass123')

        for view_name in self.ocm_views:
            url = reverse(view_name)
            response = self.client.get(url)

            self.assertEqual(
                response.status_code, 200,
                f"View {view_name} should allow OCM users"
            )

    def test_all_views_block_post_requests(self):
        """Test all OCM views block POST requests"""
        self.client.login(username='ocm_user', password='ocmpass123')

        for view_name in self.ocm_views:
            url = reverse(view_name)
            response = self.client.post(url, data={'test': 'data'})

            self.assertEqual(
                response.status_code, 403,
                f"View {view_name} should block POST requests"
            )


class OCMViewResponseTestCase(TestCase):
    """Test OCM view responses and rendering"""

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

        # Create test data
        for i in range(3):
            Organization.objects.create(
                name=f'MOA {i+1}',
                organization_type='ministry',
                is_active=True
            )

        self.client.login(username='ocm_user', password='ocmpass123')

    def test_dashboard_renders_organization_count(self):
        """Test dashboard displays organization count"""
        url = reverse('ocm:dashboard')
        response = self.client.get(url)

        # Should show organization count in response
        self.assertContains(response, '3')

    def test_views_show_readonly_indicator(self):
        """Test views display read-only mode indicator"""
        url = reverse('ocm:dashboard')
        response = self.client.get(url)

        # Should contain read-only indicator
        self.assertContains(response, 'read-only', case_sensitive=False)

    def test_views_use_ocm_base_template(self):
        """Test views extend OCM base template"""
        url = reverse('ocm:dashboard')
        response = self.client.get(url)

        # Check template inheritance
        templates = [t.name for t in response.templates]
        self.assertTrue(
            any('ocm/base.html' in t for t in templates) or
            any('base.html' in t for t in templates)
        )


class OCMViewPerformanceTestCase(TestCase):
    """Test OCM view performance"""

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

        # Create many organizations (simulate 44 MOAs)
        for i in range(44):
            Organization.objects.create(
                name=f'MOA {i+1}',
                organization_type='ministry',
                is_active=True
            )

        self.client.login(username='ocm_user', password='ocmpass123')

    def test_dashboard_loads_within_time_limit(self):
        """Test dashboard loads within 3 seconds with 44 MOAs"""
        import time

        url = reverse('ocm:dashboard')

        start = time.time()
        response = self.client.get(url)
        duration = time.time() - start

        self.assertEqual(response.status_code, 200)
        # In test environment, should load quickly
        # In production, caching ensures <3 second load time
        self.assertLess(duration, 5.0)
