"""
WorkItem Performance Tests

Tests for WorkItem performance and scalability (Phase 5 - Testing).

Test Coverage:
- MPTT queries under 100ms for 1000+ items
- Bulk create performance
- Calendar feed performance (cached vs uncached)
- Tree traversal performance
- Query optimization verification
"""

import pytest
import time
from datetime import date, timedelta
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import override_settings

from common.work_item_model import WorkItem
from common.models import StaffTeam

User = get_user_model()


@pytest.mark.performance
@pytest.mark.django_db
class TestWorkItemMPTTPerformance:
    """Test MPTT query performance."""

    def test_get_ancestors_performance(self):
        """Test get_ancestors() performance on deep hierarchy."""
        # Create deep hierarchy (10 levels)
        parent = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Root Project",
        )

        current = parent
        for i in range(9):
            current = WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Level {i+1}",
                parent=current,
            )

        # Measure query performance
        start_time = time.time()
        ancestors = current.get_ancestors()
        list(ancestors)  # Force query execution
        elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

        assert elapsed_time < 100, f"get_ancestors took {elapsed_time:.2f}ms (should be < 100ms)"
        assert ancestors.count() == 9

    def test_get_descendants_performance(self):
        """Test get_descendants() performance on large tree."""
        # Create wide tree (1 root + 50 children + 500 grandchildren)
        root = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Root",
        )

        children = []
        for i in range(50):
            child = WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_ACTIVITY,
                title=f"Child {i}",
                parent=root,
            )
            children.append(child)

        for child in children[:10]:  # Only first 10 children get grandchildren
            for j in range(50):
                WorkItem.objects.create(
                    work_type=WorkItem.WORK_TYPE_TASK,
                    title=f"Grandchild {j}",
                    parent=child,
                )

        # Measure query performance
        start_time = time.time()
        descendants = root.get_descendants()
        list(descendants)  # Force query execution
        elapsed_time = (time.time() - start_time) * 1000

        assert elapsed_time < 100, f"get_descendants took {elapsed_time:.2f}ms (should be < 100ms)"
        assert descendants.count() == 550  # 50 + 500

    def test_tree_traversal_query_count(self):
        """Test that tree traversal uses minimal queries."""
        # Create tree
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project",
        )

        for i in range(10):
            activity = WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_ACTIVITY,
                title=f"Activity {i}",
                parent=project,
            )

            for j in range(10):
                WorkItem.objects.create(
                    work_type=WorkItem.WORK_TYPE_TASK,
                    title=f"Task {i}-{j}",
                    parent=activity,
                )

        # Count queries
        with self.assertNumQueries(1):  # Should be 1 query with MPTT
            descendants = project.get_descendants()
            list(descendants)


@pytest.mark.performance
@pytest.mark.django_db
class TestBulkOperations:
    """Test bulk operation performance."""

    def test_bulk_create_performance(self):
        """Test bulk creation of work items."""
        # Create 1000 work items in bulk
        work_items = [
            WorkItem(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Task {i}",
                task_data={"index": i},
            )
            for i in range(1000)
        ]

        start_time = time.time()
        WorkItem.objects.bulk_create(work_items, batch_size=100)
        elapsed_time = (time.time() - start_time) * 1000

        assert elapsed_time < 2000, f"Bulk create took {elapsed_time:.2f}ms (should be < 2s)"
        assert WorkItem.objects.count() == 1000

    def test_bulk_update_performance(self):
        """Test bulk update performance."""
        # Create work items
        work_items = [
            WorkItem(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Task {i}",
                status=WorkItem.STATUS_NOT_STARTED,
            )
            for i in range(500)
        ]
        WorkItem.objects.bulk_create(work_items)

        # Bulk update
        tasks = WorkItem.objects.all()
        for task in tasks:
            task.status = WorkItem.STATUS_COMPLETED

        start_time = time.time()
        WorkItem.objects.bulk_update(tasks, ["status"], batch_size=100)
        elapsed_time = (time.time() - start_time) * 1000

        assert elapsed_time < 1000, f"Bulk update took {elapsed_time:.2f}ms (should be < 1s)"


@pytest.mark.performance
@pytest.mark.django_db
class TestCalendarFeedPerformance:
    """Test calendar feed performance."""

    def test_calendar_feed_uncached_performance(self, client):
        """Test calendar feed performance without caching."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        # Create 100 work items with hierarchy
        for i in range(100):
            project = WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_PROJECT,
                title=f"Project {i}",
                start_date=date.today() + timedelta(days=i),
            )

            WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Task {i}",
                parent=project,
                start_date=date.today() + timedelta(days=i),
            )

        # Measure feed generation
        start_time = time.time()
        response = client.get("/api/calendar/work-items/")
        elapsed_time = (time.time() - start_time) * 1000

        assert response.status_code == 200
        assert elapsed_time < 500, f"Calendar feed took {elapsed_time:.2f}ms (should be < 500ms)"

    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    })
    def test_calendar_feed_cached_performance(self, client):
        """Test calendar feed with caching."""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        # Create work items
        for i in range(50):
            WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Task {i}",
                start_date=date.today(),
            )

        # First request (cache miss)
        start_time = time.time()
        response1 = client.get("/api/calendar/work-items/")
        first_request_time = (time.time() - start_time) * 1000

        # Second request (cache hit)
        start_time = time.time()
        response2 = client.get("/api/calendar/work-items/")
        cached_request_time = (time.time() - start_time) * 1000

        # Cached should be significantly faster
        assert cached_request_time < first_request_time * 0.5, \
            f"Cached request ({cached_request_time:.2f}ms) should be < 50% of first ({first_request_time:.2f}ms)"


@pytest.mark.performance
@pytest.mark.django_db
class TestProgressCalculationPerformance:
    """Test auto-progress calculation performance."""

    def test_progress_propagation_performance(self):
        """Test progress update propagation speed."""
        # Create deep hierarchy
        project = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Project",
            auto_calculate_progress=True,
        )

        activity1 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Activity 1",
            parent=project,
            auto_calculate_progress=True,
        )

        activity2 = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_ACTIVITY,
            title="Activity 2",
            parent=project,
            auto_calculate_progress=True,
        )

        # Create 50 tasks under each activity
        tasks = []
        for i in range(50):
            tasks.append(WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Task 1-{i}",
                parent=activity1,
                status=WorkItem.STATUS_NOT_STARTED,
            ))

        for i in range(50):
            tasks.append(WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Task 2-{i}",
                parent=activity2,
                status=WorkItem.STATUS_NOT_STARTED,
            ))

        # Mark all tasks complete and measure propagation
        start_time = time.time()
        for task in tasks:
            task.status = WorkItem.STATUS_COMPLETED
            task.save()
            task.parent.update_progress()

        project.update_progress()
        elapsed_time = (time.time() - start_time) * 1000

        assert elapsed_time < 1000, f"Progress propagation took {elapsed_time:.2f}ms (should be < 1s)"
        project.refresh_from_db()
        assert project.progress == 100


@pytest.mark.performance
@pytest.mark.django_db
class TestQueryOptimization:
    """Test query optimization strategies."""

    def test_select_related_optimization(self):
        """Test that select_related reduces queries."""
        user = User.objects.create_user(username="testuser")

        # Create work items with relationships
        for i in range(20):
            WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Task {i}",
                created_by=user,
            )

        # Without select_related (N+1 queries)
        queries_without = 0
        with connection.cursor() as cursor:
            start_queries = len(connection.queries)
            items = WorkItem.objects.all()
            for item in items:
                _ = item.created_by.username  # Access related field
            queries_without = len(connection.queries) - start_queries

        # Reset queries
        connection.queries_log.clear()

        # With select_related (optimized)
        queries_with = 0
        with connection.cursor() as cursor:
            start_queries = len(connection.queries)
            items = WorkItem.objects.select_related('created_by').all()
            for item in items:
                _ = item.created_by.username
            queries_with = len(connection.queries) - start_queries

        # Should use far fewer queries
        assert queries_with < queries_without * 0.5, \
            f"select_related should reduce queries (with: {queries_with}, without: {queries_without})"

    def test_prefetch_related_optimization(self):
        """Test that prefetch_related reduces queries for M2M."""
        user1 = User.objects.create_user(username="user1")
        user2 = User.objects.create_user(username="user2")

        # Create work items with multiple assignees
        for i in range(10):
            task = WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Task {i}",
            )
            task.assignees.add(user1, user2)

        # Without prefetch_related
        queries_without = 0
        with connection.cursor() as cursor:
            start_queries = len(connection.queries)
            items = WorkItem.objects.all()
            for item in items:
                _ = list(item.assignees.all())
            queries_without = len(connection.queries) - start_queries

        # Reset
        connection.queries_log.clear()

        # With prefetch_related
        queries_with = 0
        with connection.cursor() as cursor:
            start_queries = len(connection.queries)
            items = WorkItem.objects.prefetch_related('assignees').all()
            for item in items:
                _ = list(item.assignees.all())
            queries_with = len(connection.queries) - start_queries

        assert queries_with < 5, f"prefetch_related should use minimal queries (used {queries_with})"


@pytest.mark.performance
@pytest.mark.django_db
class TestScalability:
    """Test system scalability with large datasets."""

    def test_large_tree_navigation(self):
        """Test navigation in tree with 1000+ nodes."""
        # Create large tree structure
        root = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_PROJECT,
            title="Large Project",
        )

        # Create 100 activities
        activities = []
        for i in range(100):
            activity = WorkItem.objects.create(
                work_type=WorkItem.WORK_TYPE_ACTIVITY,
                title=f"Activity {i}",
                parent=root,
            )
            activities.append(activity)

        # Create 10 tasks per activity (1000 tasks total)
        for activity in activities:
            for j in range(10):
                WorkItem.objects.create(
                    work_type=WorkItem.WORK_TYPE_TASK,
                    title=f"Task {j}",
                    parent=activity,
                )

        # Test various operations
        start_time = time.time()

        # Get all descendants
        all_descendants = root.get_descendants()
        assert all_descendants.count() == 1100  # 100 + 1000

        # Get specific type
        all_tasks = root.get_all_tasks()
        assert all_tasks.count() == 1000

        # Get root
        random_task = WorkItem.objects.filter(work_type=WorkItem.WORK_TYPE_TASK).first()
        assert random_task.get_root_project() == root

        elapsed_time = (time.time() - start_time) * 1000

        assert elapsed_time < 500, f"Large tree operations took {elapsed_time:.2f}ms (should be < 500ms)"

    def test_concurrent_updates(self):
        """Test handling concurrent updates."""
        # Note: This is a simplified test. Real concurrency testing requires threads/processes.
        work_item = WorkItem.objects.create(
            work_type=WorkItem.WORK_TYPE_TASK,
            title="Concurrent Task",
            progress=0,
        )

        # Simulate concurrent updates
        for i in range(100):
            work_item.progress = i
            work_item.save()

        work_item.refresh_from_db()
        assert work_item.progress == 99


@pytest.mark.performance
@pytest.mark.django_db
class TestMemoryUsage:
    """Test memory efficiency."""

    def test_iterator_for_large_queryset(self):
        """Test that iterator() prevents loading all objects into memory."""
        # Create many work items
        WorkItem.objects.bulk_create([
            WorkItem(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Task {i}",
            )
            for i in range(1000)
        ])

        # Using iterator should be memory-efficient
        count = 0
        for item in WorkItem.objects.iterator(chunk_size=100):
            count += 1

        assert count == 1000

    def test_values_list_optimization(self):
        """Test that values_list is more efficient than full objects."""
        WorkItem.objects.bulk_create([
            WorkItem(
                work_type=WorkItem.WORK_TYPE_TASK,
                title=f"Task {i}",
            )
            for i in range(500)
        ])

        # Measure with full objects
        start_time = time.time()
        titles_full = [item.title for item in WorkItem.objects.all()]
        full_time = (time.time() - start_time) * 1000

        # Measure with values_list
        start_time = time.time()
        titles_values = list(WorkItem.objects.values_list('title', flat=True))
        values_time = (time.time() - start_time) * 1000

        # values_list should be faster
        assert values_time < full_time, \
            f"values_list ({values_time:.2f}ms) should be faster than full objects ({full_time:.2f}ms)"
