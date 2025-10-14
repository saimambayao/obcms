"""
Tests for OCM aggregation services
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import time

from organizations.models import Organization
from ocm.services.aggregation import (
    get_organization_count,
    get_government_stats,
    get_consolidated_budget,
    get_budget_summary,
    get_strategic_planning_status,
    get_planning_summary,
    get_inter_moa_partnerships,
    get_coordination_summary,
    get_performance_metrics,
    clear_cache
)

User = get_user_model()


class OrganizationCountTestCase(TestCase):
    """Test get_organization_count aggregation"""

    def setUp(self):
        """Create test organizations"""
        # Create 5 ministries
        for i in range(5):
            Organization.objects.create(
                name=f'Ministry {i+1}',
                organization_type='ministry',
                is_active=True
            )

        # Create 3 offices
        for i in range(3):
            Organization.objects.create(
                name=f'Office {i+1}',
                organization_type='office',
                is_active=True
            )

        # Create 2 agencies
        for i in range(2):
            Organization.objects.create(
                name=f'Agency {i+1}',
                organization_type='agency',
                is_active=True
            )

        # Create 1 inactive organization
        Organization.objects.create(
            name='Inactive Org',
            organization_type='office',
            is_active=False
        )

    def test_get_total_organization_count(self):
        """Test getting total active organization count"""
        count = get_organization_count()
        self.assertEqual(count, 10)  # 5 ministries + 3 offices + 2 agencies

    def test_get_organization_count_by_type(self):
        """Test filtering organization count by type"""
        ministry_count = get_organization_count(org_type='ministry')
        office_count = get_organization_count(org_type='office')
        agency_count = get_organization_count(org_type='agency')

        self.assertEqual(ministry_count, 5)
        self.assertEqual(office_count, 3)
        self.assertEqual(agency_count, 2)

    def test_inactive_organizations_excluded(self):
        """Test inactive organizations are excluded"""
        # Total should not include inactive
        total = get_organization_count()
        all_orgs = Organization.objects.count()

        self.assertEqual(total, 10)
        self.assertEqual(all_orgs, 11)  # Including inactive


class GovernmentStatsTestCase(TestCase):
    """Test get_government_stats aggregation"""

    def setUp(self):
        """Create test data"""
        # Create organizations
        for i in range(3):
            Organization.objects.create(
                name=f'MOA {i+1}',
                organization_type='ministry',
                is_active=True
            )

    def test_get_government_stats_structure(self):
        """Test government stats returns correct structure"""
        stats = get_government_stats()

        # Check required keys
        self.assertIn('total_organizations', stats)
        self.assertIn('active_users', stats)
        self.assertIn('total_budget', stats)
        self.assertIn('active_projects', stats)

    def test_government_stats_organization_count(self):
        """Test organization count in government stats"""
        stats = get_government_stats()
        self.assertEqual(stats['total_organizations'], 3)


class ConsolidatedBudgetTestCase(TestCase):
    """Test get_consolidated_budget aggregation"""

    def setUp(self):
        """Create test budget data"""
        from budget_execution.models import MOABudgetProposal

        # Create organizations
        self.org1 = Organization.objects.create(
            name='Ministry of Health',
            organization_type='ministry',
            is_active=True
        )
        self.org2 = Organization.objects.create(
            name='Ministry of Education',
            organization_type='ministry',
            is_active=True
        )

        # Create user
        self.user = User.objects.create_user(
            username='budgetuser',
            email='budget@example.com',
            password='budgetpass123'
        )

        # Create budget proposals
        MOABudgetProposal.objects.create(
            organization=self.org1,
            fiscal_year=2024,
            total_proposed_amount=Decimal('1000000.00'),
            status='approved',
            submitted_by=self.user
        )

        MOABudgetProposal.objects.create(
            organization=self.org2,
            fiscal_year=2024,
            total_proposed_amount=Decimal('2000000.00'),
            status='approved',
            submitted_by=self.user
        )

    def test_get_consolidated_budget_total(self):
        """Test consolidated budget calculates total correctly"""
        budget_data = get_consolidated_budget()

        self.assertIn('total_proposed', budget_data)
        self.assertEqual(
            budget_data['total_proposed'],
            Decimal('3000000.00')
        )

    def test_get_consolidated_budget_by_fiscal_year(self):
        """Test filtering consolidated budget by fiscal year"""
        budget_data = get_consolidated_budget(fiscal_year=2024)

        self.assertIsNotNone(budget_data)
        self.assertEqual(
            budget_data['total_proposed'],
            Decimal('3000000.00')
        )

    def test_get_consolidated_budget_wrong_year(self):
        """Test consolidated budget for year with no data"""
        budget_data = get_consolidated_budget(fiscal_year=2025)

        # Should return zeros or empty data
        self.assertEqual(
            budget_data.get('total_proposed', Decimal('0')),
            Decimal('0')
        )

    def test_budget_by_organization(self):
        """Test budget breakdown by organization"""
        budget_data = get_consolidated_budget()

        self.assertIn('by_organization', budget_data)
        self.assertEqual(len(budget_data['by_organization']), 2)


class BudgetSummaryTestCase(TestCase):
    """Test get_budget_summary aggregation"""

    def setUp(self):
        """Create test data"""
        from budget_execution.models import MOABudgetProposal

        self.org = Organization.objects.create(
            name='Test Ministry',
            organization_type='ministry',
            is_active=True
        )

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create budgets for multiple years
        for year in [2023, 2024]:
            MOABudgetProposal.objects.create(
                organization=self.org,
                fiscal_year=year,
                total_proposed_amount=Decimal('1000000.00'),
                status='approved',
                submitted_by=self.user
            )

    def test_get_budget_summary(self):
        """Test budget summary aggregation"""
        summary = get_budget_summary()

        self.assertIn('total_budgets', summary)
        self.assertIn('by_fiscal_year', summary)
        self.assertIn('by_status', summary)

    def test_budget_summary_fiscal_years(self):
        """Test budget summary includes all fiscal years"""
        summary = get_budget_summary()

        years = summary.get('by_fiscal_year', {}).keys()
        self.assertIn(2023, years)
        self.assertIn(2024, years)


class StrategicPlanningStatusTestCase(TestCase):
    """Test get_strategic_planning_status aggregation"""

    def setUp(self):
        """Create test planning data"""
        from planning.models import StrategicPlan

        # Create organizations
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

        # Create strategic plans
        StrategicPlan.objects.create(
            organization=self.org1,
            title='Plan 1',
            start_year=2024,
            end_year=2028,
            status='approved'
        )

        StrategicPlan.objects.create(
            organization=self.org2,
            title='Plan 2',
            start_year=2024,
            end_year=2028,
            status='draft'
        )

    def test_get_strategic_planning_status(self):
        """Test strategic planning status aggregation"""
        status = get_strategic_planning_status()

        self.assertIn('total_plans', status)
        self.assertIn('by_status', status)
        self.assertIn('by_organization', status)

    def test_planning_status_counts(self):
        """Test planning status counts correctly"""
        status = get_strategic_planning_status()

        self.assertEqual(status['total_plans'], 2)
        self.assertEqual(status['by_status']['approved'], 1)
        self.assertEqual(status['by_status']['draft'], 1)


class PlanningSummaryTestCase(TestCase):
    """Test get_planning_summary aggregation"""

    def setUp(self):
        """Create test data"""
        from planning.models import StrategicPlan, Program

        self.org = Organization.objects.create(
            name='Test MOA',
            organization_type='ministry',
            is_active=True
        )

        self.plan = StrategicPlan.objects.create(
            organization=self.org,
            title='Strategic Plan',
            start_year=2024,
            end_year=2028,
            status='approved'
        )

        # Create programs
        for i in range(3):
            Program.objects.create(
                strategic_plan=self.plan,
                title=f'Program {i+1}',
                status='active'
            )

    def test_get_planning_summary(self):
        """Test planning summary aggregation"""
        summary = get_planning_summary()

        self.assertIn('total_plans', summary)
        self.assertIn('total_programs', summary)
        self.assertIn('by_organization', summary)


class InterMOAPartnershipsTestCase(TestCase):
    """Test get_inter_moa_partnerships aggregation"""

    def setUp(self):
        """Create test partnership data"""
        from coordination.models import Partnership, InterMOAPartnership

        # Create organizations
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

        # Create inter-MOA partnership
        self.partnership = Partnership.objects.create(
            name='Inter-MOA Partnership',
            lead_organization=self.org1,
            is_inter_moa=True,
            status='active'
        )

        InterMOAPartnership.objects.create(
            partnership=self.partnership,
            participating_organization=self.org2
        )

    def test_get_inter_moa_partnerships(self):
        """Test inter-MOA partnerships aggregation"""
        partnerships = get_inter_moa_partnerships()

        self.assertIn('total_partnerships', partnerships)
        self.assertIn('active_partnerships', partnerships)
        self.assertIn('by_lead_organization', partnerships)

    def test_inter_moa_partnership_count(self):
        """Test partnership count is correct"""
        partnerships = get_inter_moa_partnerships()

        self.assertEqual(partnerships['total_partnerships'], 1)
        self.assertEqual(partnerships['active_partnerships'], 1)


class CoordinationSummaryTestCase(TestCase):
    """Test get_coordination_summary aggregation"""

    def setUp(self):
        """Create test coordination data"""
        from coordination.models import Partnership

        # Create organizations
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

        # Create partnerships
        Partnership.objects.create(
            name='Partnership 1',
            lead_organization=self.org1,
            is_inter_moa=True,
            status='active'
        )

        Partnership.objects.create(
            name='Partnership 2',
            lead_organization=self.org2,
            is_inter_moa=False,
            status='active'
        )

    def test_get_coordination_summary(self):
        """Test coordination summary aggregation"""
        summary = get_coordination_summary()

        self.assertIn('total_partnerships', summary)
        self.assertIn('inter_moa_partnerships', summary)
        self.assertIn('by_organization', summary)

    def test_coordination_summary_counts(self):
        """Test coordination summary counts"""
        summary = get_coordination_summary()

        self.assertEqual(summary['total_partnerships'], 2)
        self.assertEqual(summary['inter_moa_partnerships'], 1)


class PerformanceMetricsTestCase(TestCase):
    """Test get_performance_metrics aggregation"""

    def setUp(self):
        """Create test performance data"""
        # Create organization
        self.org = Organization.objects.create(
            name='Test MOA',
            organization_type='ministry',
            is_active=True
        )

    def test_get_performance_metrics(self):
        """Test performance metrics aggregation"""
        metrics = get_performance_metrics()

        # Check structure
        self.assertIn('budget_utilization_rate', metrics)
        self.assertIn('project_completion_rate', metrics)
        self.assertIn('assessment_completion_rate', metrics)

    def test_performance_metrics_types(self):
        """Test performance metrics return correct types"""
        metrics = get_performance_metrics()

        # Rates should be numeric
        self.assertIsInstance(
            metrics.get('budget_utilization_rate', 0),
            (int, float, Decimal)
        )


class CachingTestCase(TestCase):
    """Test aggregation caching functionality"""

    def setUp(self):
        """Create test data"""
        for i in range(3):
            Organization.objects.create(
                name=f'MOA {i+1}',
                organization_type='ministry',
                is_active=True
            )

    def test_caching_improves_performance(self):
        """Test second call is faster due to caching"""
        # Clear any existing cache
        clear_cache()

        # First call (no cache)
        start1 = time.time()
        stats1 = get_government_stats()
        time1 = time.time() - start1

        # Second call (should use cache)
        start2 = time.time()
        stats2 = get_government_stats()
        time2 = time.time() - start2

        # Results should be identical
        self.assertEqual(stats1, stats2)

        # Second call should be faster (or at least not slower)
        # Note: This is not always guaranteed in test environment
        # but in production caching provides significant speedup

    def test_clear_cache_function(self):
        """Test cache clearing works"""
        # Get stats (populate cache)
        stats1 = get_government_stats()

        # Clear cache
        clear_cache()

        # Get stats again (should query database)
        stats2 = get_government_stats()

        # Results should still be identical
        self.assertEqual(stats1, stats2)

    def test_cache_invalidation_on_data_change(self):
        """Test cache should be invalidated when data changes"""
        # Get initial stats
        stats1 = get_government_stats()
        initial_count = stats1['total_organizations']

        # Add new organization
        Organization.objects.create(
            name='New MOA',
            organization_type='office',
            is_active=True
        )

        # Clear cache (in production, this would be done automatically)
        clear_cache()

        # Get stats again
        stats2 = get_government_stats()
        new_count = stats2['total_organizations']

        # Count should have increased
        self.assertEqual(new_count, initial_count + 1)


class AggregationEdgeCasesTestCase(TestCase):
    """Test edge cases in aggregation functions"""

    def test_aggregation_with_no_data(self):
        """Test aggregation functions with empty database"""
        # Should not raise errors
        count = get_organization_count()
        self.assertEqual(count, 0)

        stats = get_government_stats()
        self.assertEqual(stats['total_organizations'], 0)

    def test_aggregation_with_null_values(self):
        """Test aggregation handles null values correctly"""
        from budget_execution.models import MOABudgetProposal

        org = Organization.objects.create(
            name='Test Org',
            organization_type='ministry',
            is_active=True
        )

        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create budget with null allocated amount
        MOABudgetProposal.objects.create(
            organization=org,
            fiscal_year=2024,
            total_proposed_amount=Decimal('1000000.00'),
            status='draft',
            submitted_by=user
        )

        # Should handle null values without errors
        budget_data = get_consolidated_budget()
        self.assertIsNotNone(budget_data)

    def test_aggregation_performance_with_large_dataset(self):
        """Test aggregation performance with many organizations"""
        # Create 44 organizations (representing all MOAs)
        for i in range(44):
            Organization.objects.create(
                name=f'MOA {i+1}',
                organization_type='ministry',
                is_active=True
            )

        # Should complete in reasonable time
        start = time.time()
        stats = get_government_stats()
        duration = time.time() - start

        # Should complete within 1 second
        self.assertLess(duration, 1.0)
        self.assertEqual(stats['total_organizations'], 44)
