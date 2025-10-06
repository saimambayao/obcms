"""
Performance test suite for WorkItem-PPA integration.

Tests cover:
- Budget distribution performance (1000+ items <100ms)
- Tree generation performance for large hierarchies
- API response time benchmarks (all endpoints <200ms)
- Database query optimization
"""

import pytest
import time
from decimal import Decimal
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from common.work_item_model import WorkItem
from coordination.models import Organization
from monitoring.models import MonitoringEntry
from monitoring.services.budget_distribution import BudgetDistributionService

User = get_user_model()


@pytest.mark.performance
@pytest.mark.django_db
class TestWorkItemPerformance:
    """Performance tests for WorkItem-PPA integration."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username="perf_user",
            password="testpass123",
            user_type="oobc_staff",
            is_approved=True,
        )

        self.organization = Organization.objects.create(
            name="Performance Test Org",
            acronym="PTO",
            organization_type="bmoa",
            created_by=self.user,
        )

        self.client = Client()
        self.client.force_login(self.user)

        self.service = BudgetDistributionService()

    def test_budget_distribution_performance_100_items(self):
        """Test budget distribution with 100 work items completes <50ms."""
        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="100 Items PPA",
            implementing_moa=self.organization,
            budget_allocation=Decimal("100000000.00"),  # 100M
            fiscal_year=2025,
            created_by=self.user,
        )

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="100 Items Project",
            ppa_source=ppa,
            budget_allocation=Decimal("100000000.00"),
        )

        # Create 100 tasks
        for i in range(100):
            WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Task {i+1}",
                parent=project,
                ppa_source=ppa,
            )

        # Benchmark distribution
        start = time.time()
        result = self.service.distribute_equal(
            parent=project,
            total_budget=Decimal("100000000.00"),
        )
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert result["success"] is True
        assert len(result["allocations"]) == 100
        assert elapsed < 50  # Less than 50ms

    def test_budget_distribution_performance_1000_items(self):
        """Test budget distribution with 1000 work items completes <100ms."""
        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="1000 Items PPA",
            implementing_moa=self.organization,
            budget_allocation=Decimal("1000000000.00"),  # 1B
            fiscal_year=2025,
            created_by=self.user,
        )

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="1000 Items Project",
            ppa_source=ppa,
            budget_allocation=Decimal("1000000000.00"),
        )

        # Create 1000 tasks
        WorkItem.objects.bulk_create(
            [
                WorkItem(
                    work_type=WorkItem.WORK_TYPE_TASK,
                    title=f"Task {i+1}",
                    parent=project,
                    ppa_source=ppa,
                )
                for i in range(1000)
            ]
        )

        # Benchmark distribution
        start = time.time()
        result = self.service.distribute_equal(
            parent=project,
            total_budget=Decimal("1000000000.00"),
        )
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert result["success"] is True
        assert len(result["allocations"]) == 1000
        assert elapsed < 100  # Less than 100ms

    def test_tree_generation_performance_deep_hierarchy(self):
        """Test tree generation for 5-level deep hierarchy completes <200ms."""
        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Deep Hierarchy PPA",
            implementing_moa=self.organization,
            budget_allocation=Decimal("10000000.00"),
            fiscal_year=2025,
            created_by=self.user,
        )

        # Create 5-level hierarchy: Project > 3 Activities > 5 Tasks each > 3 Subtasks each
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Deep Project",
            ppa_source=ppa,
            budget_allocation=Decimal("10000000.00"),
        )

        for i in range(3):  # 3 activities
            activity = WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_ACTIVITY,
                title=f"Activity {i+1}",
                parent=project,
                ppa_source=ppa,
                budget_allocation=Decimal("3333333.33"),
            )

            for j in range(5):  # 5 tasks per activity
                task = WorkItem.objects.create(
                    work_type=WorkItem.WORK_TYPE_TASK,
                    title=f"Task {i+1}.{j+1}",
                    parent=activity,
                    ppa_source=ppa,
                    budget_allocation=Decimal("666666.67"),
                )

                for k in range(3):  # 3 subtasks per task
                    WorkItem.objects.create(
                        work_type=WorkItem.WORK_TYPE_SUBTASK,
                        title=f"Subtask {i+1}.{j+1}.{k+1}",
                        parent=task,
                        ppa_source=ppa,
                        budget_allocation=Decimal("222222.22"),
                    )

        # Total: 1 project + 3 activities + 15 tasks + 45 subtasks = 64 items

        # Benchmark tree generation
        start = time.time()
        tree = ppa.get_budget_allocation_tree()
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert tree is not None
        assert "children" in tree
        assert elapsed < 200  # Less than 200ms

    def test_api_response_time_enable_tracking(self):
        """Test enable_workitem_tracking API responds <200ms."""
        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="API Performance PPA",
            implementing_moa=self.organization,
            budget_allocation=Decimal("5000000.00"),
            fiscal_year=2025,
            approval_status="approved",
            created_by=self.user,
        )

        url = reverse("monitoring:ppa-enable-workitem-tracking", kwargs={"pk": ppa.pk})

        # Benchmark API call
        start = time.time()
        response = self.client.post(
            url, {"template": "program"}, content_type="application/json"
        )
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert response.status_code == 200
        assert elapsed < 200  # Less than 200ms

    def test_api_response_time_budget_tree(self):
        """Test budget_allocation_tree API responds <200ms."""
        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Budget Tree PPA",
            implementing_moa=self.organization,
            budget_allocation=Decimal("5000000.00"),
            fiscal_year=2025,
            created_by=self.user,
        )

        # Create moderate hierarchy
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Budget Tree Project",
            ppa_source=ppa,
            budget_allocation=Decimal("5000000.00"),
        )

        for i in range(10):
            WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Task {i+1}",
                parent=project,
                ppa_source=ppa,
                budget_allocation=Decimal("500000.00"),
            )

        url = reverse("monitoring:ppa-budget-tree", kwargs={"pk": ppa.pk})

        # Benchmark API call
        start = time.time()
        response = self.client.get(url)
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert response.status_code == 200
        assert elapsed < 200  # Less than 200ms

    def test_api_response_time_distribute_budget(self):
        """Test distribute_budget API responds <200ms."""
        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Distribute Budget PPA",
            implementing_moa=self.organization,
            budget_allocation=Decimal("10000000.00"),
            fiscal_year=2025,
            created_by=self.user,
        )

        result = ppa.enable_workitem_tracking(template="activity")

        url = reverse("monitoring:ppa-distribute-budget", kwargs={"pk": ppa.pk})

        # Benchmark API call
        start = time.time()
        response = self.client.post(
            url, {"method": "equal", "apply": False}, content_type="application/json"
        )
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert response.status_code == 200
        assert elapsed < 200  # Less than 200ms

    def test_database_query_count_budget_tree(self):
        """Test budget_allocation_tree uses efficient queries (< 10 queries)."""
        from django.test.utils import override_settings
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Query Count PPA",
            implementing_moa=self.organization,
            budget_allocation=Decimal("5000000.00"),
            fiscal_year=2025,
            created_by=self.user,
        )

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Query Count Project",
            ppa_source=ppa,
            budget_allocation=Decimal("5000000.00"),
        )

        # Create 20 tasks
        for i in range(20):
            WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Task {i+1}",
                parent=project,
                ppa_source=ppa,
                budget_allocation=Decimal("250000.00"),
            )

        # Count queries
        with CaptureQueriesContext(connection) as context:
            tree = ppa.get_budget_allocation_tree()

        query_count = len(context.captured_queries)

        assert query_count < 10  # Should use prefetch/select_related

    def test_bulk_operations_performance(self):
        """Test bulk WorkItem creation and update performance."""
        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Bulk Ops PPA",
            implementing_moa=self.organization,
            budget_allocation=Decimal("100000000.00"),
            fiscal_year=2025,
            created_by=self.user,
        )

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Bulk Project",
            ppa_source=ppa,
        )

        # Benchmark bulk creation
        start = time.time()
        WorkItem.objects.bulk_create(
            [
                WorkItem(
                    work_type=WorkItem.WORK_TYPE_TASK,
                    title=f"Bulk Task {i+1}",
                    parent=project,
                    ppa_source=ppa,
                )
                for i in range(500)
            ]
        )
        create_elapsed = (time.time() - start) * 1000

        # Should create 500 items in < 200ms
        assert create_elapsed < 200

        # Benchmark bulk update
        tasks = WorkItem.objects.filter(parent=project)

        start = time.time()
        for task in tasks:
            task.budget_allocation = Decimal("200000.00")

        WorkItem.objects.bulk_update(
            tasks, ["budget_allocation"], batch_size=100
        )
        update_elapsed = (time.time() - start) * 1000

        # Should update 500 items in < 300ms
        assert update_elapsed < 300

    def test_progress_calculation_performance(self):
        """Test progress calculation for large hierarchies <100ms."""
        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Progress Calc PPA",
            implementing_moa=self.organization,
            budget_allocation=Decimal("10000000.00"),
            fiscal_year=2025,
            created_by=self.user,
        )

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Progress Project",
            ppa_source=ppa,
        )

        # Create 100 tasks with various progress
        import random

        for i in range(100):
            WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Task {i+1}",
                parent=project,
                ppa_source=ppa,
                progress=random.randint(0, 100),
            )

        # Benchmark progress sync
        start = time.time()
        ppa.sync_progress_from_workitem()
        elapsed = (time.time() - start) * 1000

        assert elapsed < 100  # Less than 100ms

    @pytest.mark.parametrize("item_count", [10, 50, 100, 500])
    def test_distribution_scaling(self, item_count):
        """Test budget distribution scales linearly."""
        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name=f"Scaling {item_count} PPA",
            implementing_moa=self.organization,
            budget_allocation=Decimal("100000000.00"),
            fiscal_year=2025,
            created_by=self.user,
        )

        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title=f"Scaling {item_count} Project",
            ppa_source=ppa,
            budget_allocation=Decimal("100000000.00"),
        )

        # Create items
        WorkItem.objects.bulk_create(
            [
                WorkItem(
                    work_type=WorkItem.WORK_TYPE_TASK,
                    title=f"Task {i+1}",
                    parent=project,
                    ppa_source=ppa,
                )
                for i in range(item_count)
            ]
        )

        # Benchmark
        start = time.time()
        result = self.service.distribute_equal(
            parent=project,
            total_budget=Decimal("100000000.00"),
        )
        elapsed = (time.time() - start) * 1000

        # Should scale linearly: ~0.5ms per item
        expected_max = item_count * 0.5

        assert elapsed < expected_max
        assert result["success"] is True

    def test_memory_usage_large_hierarchy(self):
        """Test memory usage remains reasonable for large hierarchies."""
        import tracemalloc

        ppa = MonitoringEntry.objects.create(
            category="moa_ppa",
            name="Memory Test PPA",
            implementing_moa=self.organization,
            budget_allocation=Decimal("50000000.00"),
            fiscal_year=2025,
            created_by=self.user,
        )

        # Start tracking memory
        tracemalloc.start()

        # Create large hierarchy
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Memory Project",
            ppa_source=ppa,
        )

        for i in range(200):
            WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Task {i+1}",
                parent=project,
                ppa_source=ppa,
            )

        # Get budget tree
        tree = ppa.get_budget_allocation_tree()

        # Check memory usage
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Peak memory should be < 10MB
        assert peak < 10 * 1024 * 1024  # 10 MB in bytes
