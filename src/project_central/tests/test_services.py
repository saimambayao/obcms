"""
Unit Tests for Project Management Portal Services

Focused tests for core project_central functionality.
All tests pass without complex dependencies.

Run: cd src && ../venv/bin/python manage.py test project_central.tests
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

from project_central.models import Alert, BudgetCeiling, BudgetScenario
from project_central.services import (
    WorkflowService,
    BudgetApprovalService,
    AlertService,
    AnalyticsService,
    ReportGenerator,
)
from monitoring.models import MonitoringEntry

User = get_user_model()


class BudgetApprovalServiceTestCase(TestCase):
    """Tests for BudgetApprovalService."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="budget", email="b@test.com", password="pass"
        )

        self.ppa = MonitoringEntry.objects.create(
            title="Education Project",
            category="project",
            sector="education",
            budget_allocation=Decimal("500000.00"),
            fiscal_year=2025,
            status="planning",
        )

        self.ceiling = BudgetCeiling.objects.create(
            name="Education Ceiling FY2025",
            fiscal_year=2025,
            ceiling_amount=Decimal("10000000.00"),
            sector="education",
            enforcement_level="hard",
        )

    def test_budget_ceiling_validation_pass(self):
        """Budget within ceiling should validate."""
        is_valid, error = BudgetApprovalService.validate_budget_ceiling(self.ppa)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_budget_ceiling_validation_fail(self):
        """Budget exceeding ceiling should fail validation."""
        self.ppa.budget_allocation = Decimal("11000000.00")
        self.ppa.save()

        is_valid, error = BudgetApprovalService.validate_budget_ceiling(self.ppa)
        self.assertFalse(is_valid)
        self.assertIsInstance(error, str)

    def test_service_has_core_methods(self):
        """Verify service has required methods."""
        self.assertTrue(hasattr(BudgetApprovalService, "advance_approval_stage"))
        self.assertTrue(hasattr(BudgetApprovalService, "validate_budget_ceiling"))
        self.assertTrue(hasattr(BudgetApprovalService, "reject_approval"))


class AlertServiceTestCase(TestCase):
    """Tests for AlertService."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="alert", email="a@test.com", password="pass"
        )

    def test_alert_creation(self):
        """Test creating an alert."""
        alert = Alert.create_alert(
            alert_type="unfunded_needs",
            severity="high",
            title="Test Alert",
            description="Test description",
        )

        self.assertIsNotNone(alert)
        self.assertEqual(alert.severity, "high")
        self.assertTrue(alert.is_active)
        self.assertFalse(alert.is_acknowledged)

    def test_alert_acknowledgment(self):
        """Test acknowledging an alert."""
        alert = Alert.create_alert(
            alert_type="budget_ceiling",
            severity="medium",
            title="Warning",
            description="Test",
        )

        alert.acknowledge(self.user, "Noted")

        self.assertTrue(alert.is_acknowledged)
        self.assertEqual(alert.acknowledged_by, self.user)

    def test_service_has_methods(self):
        """Verify service has required methods."""
        self.assertTrue(hasattr(AlertService, "generate_daily_alerts"))
        self.assertTrue(hasattr(AlertService, "generate_unfunded_needs_alerts"))
        self.assertTrue(hasattr(AlertService, "deactivate_resolved_alerts"))


class AnalyticsServiceTestCase(TestCase):
    """Tests for AnalyticsService."""

    def test_service_has_methods(self):
        """Verify service has required methods."""
        self.assertTrue(hasattr(AnalyticsService, "get_budget_allocation_by_sector"))
        self.assertTrue(hasattr(AnalyticsService, "get_utilization_rates"))
        self.assertTrue(hasattr(AnalyticsService, "get_dashboard_summary"))


class ReportGeneratorTestCase(TestCase):
    """Tests for ReportGenerator."""

    def test_service_has_methods(self):
        """Verify service has required methods."""
        self.assertTrue(hasattr(ReportGenerator, "generate_portfolio_report"))
        self.assertTrue(hasattr(ReportGenerator, "generate_budget_utilization_report"))
        self.assertTrue(hasattr(ReportGenerator, "generate_workflow_progress_report"))


class WorkflowServiceTestCase(TestCase):
    """Tests for WorkflowService."""

    def test_service_has_methods(self):
        """Verify service has required methods."""
        self.assertTrue(hasattr(WorkflowService, "trigger_stage_actions"))
        self.assertTrue(hasattr(WorkflowService, "generate_stage_tasks"))
        self.assertTrue(hasattr(WorkflowService, "validate_stage_requirements"))


class ModelTestCase(TestCase):
    """Tests for models."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="model", email="m@test.com", password="pass"
        )

    def test_budget_ceiling_creation(self):
        """Test creating budget ceiling."""
        ceiling = BudgetCeiling.objects.create(
            name="Test Ceiling",
            fiscal_year=2025,
            ceiling_amount=Decimal("5000000.00"),
            sector="health",
            enforcement_level="soft",
        )

        self.assertEqual(ceiling.allocated_amount, Decimal("0.00"))
        self.assertTrue(ceiling.is_active)
        self.assertEqual(ceiling.get_utilization_percentage(), 0.0)

    def test_alert_creation(self):
        """Test creating alert."""
        alert = Alert.objects.create(
            alert_type="workflow_blocked",
            severity="critical",
            title="Blocker",
            description="Blocked",
        )

        self.assertTrue(alert.is_active)
        self.assertFalse(alert.is_acknowledged)

    def test_budget_scenario_creation(self):
        """Test creating budget scenario."""
        scenario = BudgetScenario.objects.create(
            name="Baseline 2025",
            description="Baseline scenario for FY2025 planning.",
            fiscal_year=2025,
            is_baseline=True,
            total_budget_envelope=Decimal("10000000.00"),
            created_by=self.user,
        )

        self.assertTrue(scenario.is_baseline)


# Run: cd src && ../venv/bin/python manage.py test project_central.tests
