"""
Performance and Load Testing for Integrated Systems
Tests system performance under realistic data volumes and query loads.

Tests cover:
1. Calendar aggregation performance with large datasets
2. Task dashboard query optimization
3. Project portfolio dashboard performance
4. Database query efficiency (N+1 prevention)
5. Caching effectiveness
"""

import time
from datetime import date, datetime, time as dt_time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import connection, reset_queries
from django.test import TestCase, override_settings
from django.test.utils import override_settings
from django.utils import timezone

from common.models import StaffTask, Team
from common.services.calendar import build_calendar_payload, invalidate_calendar_cache
from communities.models import OBCCommunity
from coordination.models import Event, Partnership, StakeholderEngagement
from mana.models import Assessment, Need, Survey, WorkshopActivity
from monitoring.models import MonitoringEntry
from recommendations.policy_tracking.models import PolicyRecommendation

User = get_user_model()


class CalendarPerformanceTestCase(TestCase):
    """Test calendar aggregation performance with realistic data volumes."""

    @classmethod
    def setUpTestData(cls):
        """Create large realistic dataset for performance testing."""
        # Create users
        cls.users = []
        for i in range(10):
            user = User.objects.create_user(
                username=f"user{i}",
                email=f"user{i}@example.com",
                password="testpass123",
            )
            cls.users.append(user)

        cls.coordinator = cls.users[0]

        # Create teams
        cls.teams = []
        for i in range(5):
            team = Team.objects.create(
                name=f"Team {i+1}", slug=f"team-{i+1}", description=f"Test team {i+1}"
            )
            # Add 2 users to each team
            team.members.add(
                cls.users[i * 2],
                cls.users[i * 2 + 1] if i * 2 + 1 < len(cls.users) else cls.users[0],
            )
            cls.teams.append(team)

        # Create communities
        cls.communities = []
        for i in range(50):
            community = OBCCommunity.objects.create(
                name=f"Community {i+1}",
                barangay_name=f"Barangay {i+1}",
                municipality_name=f"Municipality {(i % 10) + 1}",
                province_name=f"Province {(i % 5) + 1}",
                region="Region IX",
            )
            cls.communities.append(community)

        # Create needs (100)
        cls.needs = []
        for i in range(100):
            need = Need.objects.create(
                title=f"Need {i+1}",
                description=f"Community need {i+1}",
                need_type=[
                    "education",
                    "health",
                    "infrastructure",
                    "economic",
                    "social",
                ][i % 5],
                urgency_level=["low", "medium", "high", "critical"][i % 4],
                status=["identified", "prioritized", "in_progress"][i % 3],
                community=cls.communities[i % len(cls.communities)],
                identified_by=cls.users[i % len(cls.users)],
            )
            cls.needs.append(need)

        # Create assessments (50)
        cls.assessments = []
        for i in range(50):
            base_date = date(2025, 10, 1) + timedelta(days=i * 7)
            assessment = Assessment.objects.create(
                title=f"Assessment {i+1}",
                methodology=["survey", "focus_group", "participatory", "mixed"][i % 4],
                status=["planning", "data_collection", "analysis", "completed"][i % 4],
                planning_completion_date=base_date,
                data_collection_end_date=base_date + timedelta(days=30),
                analysis_completion_date=base_date + timedelta(days=60),
                report_due_date=base_date + timedelta(days=90),
                lead_facilitator=cls.users[i % len(cls.users)],
            )
            cls.assessments.append(assessment)

        # Create PPAs (100)
        cls.ppas = []
        for i in range(100):
            start = date(2025, 10, 1) + timedelta(days=i * 3)
            ppa = MonitoringEntry.objects.create(
                title=f"PPA {i+1}",
                description=f"Program/Project/Activity {i+1}",
                category=["oobc_ppa", "moa_ppa"][i % 2],
                status=["planning", "ongoing", "completed"][i % 3],
                budget_allocation=Decimal(str(1000000 + i * 100000)),
                start_date=start,
                end_date=start + timedelta(days=365),
                created_by=cls.users[i % len(cls.users)],
            )
            # Link to random needs
            ppa.needs_addressed.add(cls.needs[i % len(cls.needs)])
            if i % 3 == 0:
                ppa.needs_addressed.add(cls.needs[(i + 1) % len(cls.needs)])
            cls.ppas.append(ppa)

        # Create events (200)
        cls.events = []
        for i in range(200):
            event_date = date(2025, 10, 1) + timedelta(days=i * 2)
            event = Event.objects.create(
                title=f"Event {i+1}",
                description=f"Coordination event {i+1}",
                event_type=["meeting", "workshop", "consultation", "field_visit"][
                    i % 4
                ],
                start_date=event_date,
                start_time=dt_time(9, 0),
                end_date=event_date,
                end_time=dt_time(17, 0),
                organizer=cls.users[i % len(cls.users)],
                is_quarterly_coordination=(i % 20 == 0),
                quarter=((i // 20) % 4) + 1 if i % 20 == 0 else None,
                fiscal_year=2025 if i % 20 == 0 else None,
            )
            cls.events.append(event)

        # Create stakeholder engagements (150)
        cls.engagements = []
        for i in range(150):
            engagement_date = date(2025, 10, 1) + timedelta(days=i * 3)
            engagement = StakeholderEngagement.objects.create(
                title=f"Engagement {i+1}",
                description=f"Stakeholder engagement {i+1}",
                engagement_type=["meeting", "consultation", "dialogue"][i % 3],
                scheduled_date=engagement_date,
                start_time=dt_time(10, 0),
                end_time=dt_time(12, 0),
                facilitator=cls.users[i % len(cls.users)],
            )
            cls.engagements.append(engagement)

        # Tasks will be auto-created by signal handlers
        # Wait a moment for signals to complete
        print(f"Created test dataset:")
        print(f"  - {len(cls.users)} users")
        print(f"  - {len(cls.teams)} teams")
        print(f"  - {len(cls.communities)} communities")
        print(f"  - {len(cls.needs)} needs")
        print(f"  - {len(cls.assessments)} assessments")
        print(f"  - {len(cls.ppas)} PPAs")
        print(f"  - {len(cls.events)} events")
        print(f"  - {len(cls.engagements)} stakeholder engagements")

        # Count auto-generated tasks
        task_count = StaffTask.objects.count()
        print(f"  - {task_count} tasks (auto-generated)")

    def setUp(self):
        """Clear cache before each test."""
        cache.clear()
        reset_queries()

    @override_settings(DEBUG=True)
    def test_calendar_aggregation_performance(self):
        """
        Test calendar aggregation with large dataset.

        Target: Complete in under 2 seconds with < 100 queries.
        """
        print("\n" + "=" * 70)
        print("CALENDAR AGGREGATION PERFORMANCE TEST")
        print("=" * 70)

        # Warm up (first query might be slower due to Django startup)
        build_calendar_payload()
        cache.clear()
        reset_queries()

        # Actual performance test
        start_time = time.time()
        payload = build_calendar_payload()
        end_time = time.time()

        duration = end_time - start_time
        query_count = len(connection.queries)
        entry_count = len(payload["entries"])

        print(f"\nResults:")
        print(f"  Duration: {duration:.3f} seconds")
        print(f"  Queries: {query_count}")
        print(f"  Entries: {entry_count}")
        print(f"  Modules: {len(payload['module_stats'])}")

        # Performance assertions
        self.assertLess(
            duration,
            2.0,
            f"Calendar aggregation took {duration:.3f}s, should be under 2s",
        )

        self.assertLess(
            query_count,
            100,
            f"Calendar aggregation used {query_count} queries, should be under 100",
        )

        self.assertGreater(entry_count, 0, "Calendar should have entries")

        # Show query breakdown if > 50 queries
        if query_count > 50:
            print("\nWarning: High query count. Sample queries:")
            for i, query in enumerate(connection.queries[:5]):
                print(f"\nQuery {i+1}:")
                print(f"  Time: {query['time']}s")
                print(f"  SQL: {query['sql'][:200]}...")

    @override_settings(DEBUG=True)
    def test_calendar_caching_effectiveness(self):
        """
        Test that caching improves calendar performance.

        Second call should be significantly faster due to caching.
        """
        print("\n" + "=" * 70)
        print("CALENDAR CACHING EFFECTIVENESS TEST")
        print("=" * 70)

        cache.clear()
        reset_queries()

        # First call (uncached)
        start_time = time.time()
        payload1 = build_calendar_payload()
        end_time = time.time()
        uncached_duration = end_time - start_time
        uncached_queries = len(connection.queries)

        reset_queries()

        # Second call (should use cache)
        start_time = time.time()
        payload2 = build_calendar_payload()
        end_time = time.time()
        cached_duration = end_time - start_time
        cached_queries = len(connection.queries)

        print(f"\nResults:")
        print(f"  Uncached: {uncached_duration:.3f}s, {uncached_queries} queries")
        print(f"  Cached:   {cached_duration:.3f}s, {cached_queries} queries")
        print(
            f"  Speedup:  {(uncached_duration/cached_duration if cached_duration > 0 else 0):.1f}x"
        )

        # Cached should be faster
        self.assertLess(
            cached_duration,
            uncached_duration,
            "Cached call should be faster than uncached",
        )

        # Should have fewer queries when cached
        self.assertLessEqual(
            cached_queries,
            uncached_queries,
            "Cached call should use fewer or equal queries",
        )

    @override_settings(DEBUG=True)
    def test_filtered_calendar_performance(self):
        """
        Test calendar performance with module filtering.

        Filtering should reduce query time.
        """
        print("\n" + "=" * 70)
        print("FILTERED CALENDAR PERFORMANCE TEST")
        print("=" * 70)

        cache.clear()
        reset_queries()

        # Test each module filter
        modules_to_test = ["coordination", "mana", "monitoring", "staff"]

        for module in modules_to_test:
            cache.clear()
            reset_queries()

            start_time = time.time()
            payload = build_calendar_payload(filter_modules=[module])
            end_time = time.time()

            duration = end_time - start_time
            query_count = len(connection.queries)
            entry_count = len(payload["entries"])

            print(f"\n{module.upper()}:")
            print(f"  Duration: {duration:.3f}s")
            print(f"  Queries: {query_count}")
            print(f"  Entries: {entry_count}")

            # Filtered calls should be reasonably fast
            self.assertLess(
                duration,
                1.5,
                f"Filtered calendar ({module}) should complete in under 1.5s",
            )


class TaskDashboardPerformanceTestCase(TestCase):
    """Test task dashboard query performance."""

    @classmethod
    def setUpTestData(cls):
        """Create test data."""
        # Create users and tasks
        cls.user = User.objects.create_user(
            username="taskuser", email="taskuser@example.com", password="testpass123"
        )

        cls.team = Team.objects.create(
            name="Task Team", slug="task-team", description="Team for task testing"
        )
        cls.team.members.add(cls.user)

        # Create PPAs
        cls.ppas = []
        for i in range(20):
            ppa = MonitoringEntry.objects.create(
                title=f"PPA for Tasks {i+1}",
                category="oobc_ppa",
                status="ongoing",
                budget_allocation=Decimal("1000000.00"),
                created_by=cls.user,
            )
            cls.ppas.append(ppa)

        # Create many tasks assigned to user
        for i in range(500):
            task = StaffTask.objects.create(
                title=f"Task {i+1}",
                description=f"Test task {i+1}",
                domain=["mana", "coordination", "monitoring", "policy"][i % 4],
                status=[
                    StaffTask.STATUS_NOT_STARTED,
                    StaffTask.STATUS_IN_PROGRESS,
                    StaffTask.STATUS_COMPLETED,
                ][i % 3],
                priority=["low", "medium", "high"][i % 3],
                related_ppa=cls.ppas[i % len(cls.ppas)] if i % 3 == 0 else None,
                created_by=cls.user,
                due_date=date(2025, 10, 1) + timedelta(days=i),
            )
            task.assignees.add(cls.user)
            task.teams.add(cls.team)

        print(f"Created 500 tasks for performance testing")

    @override_settings(DEBUG=True)
    def test_user_task_query_performance(self):
        """
        Test querying user's tasks with proper optimization.

        Target: Complete in under 1 second with < 20 queries.
        """
        print("\n" + "=" * 70)
        print("TASK DASHBOARD QUERY PERFORMANCE TEST")
        print("=" * 70)

        reset_queries()

        # Simulate task dashboard query
        start_time = time.time()

        my_tasks = (
            StaffTask.objects.filter(
                assignees=self.user,
                status__in=[StaffTask.STATUS_NOT_STARTED, StaffTask.STATUS_IN_PROGRESS],
            )
            .select_related(
                "related_assessment", "related_ppa", "linked_event", "created_by"
            )
            .prefetch_related("assignees", "teams", "teams__members")[:50]
        )  # Limit to 50 for dashboard

        # Force evaluation
        task_list = list(my_tasks)

        end_time = time.time()

        duration = end_time - start_time
        query_count = len(connection.queries)

        print(f"\nResults:")
        print(f"  Duration: {duration:.3f}s")
        print(f"  Queries: {query_count}")
        print(f"  Tasks retrieved: {len(task_list)}")

        # Performance assertions
        self.assertLess(
            duration, 1.0, f"Task query took {duration:.3f}s, should be under 1s"
        )

        self.assertLess(
            query_count,
            20,
            f"Task query used {query_count} queries, should be under 20",
        )

        self.assertGreater(len(task_list), 0, "Should retrieve tasks")

    @override_settings(DEBUG=True)
    def test_task_filtering_performance(self):
        """Test performance of filtered task queries."""
        print("\n" + "=" * 70)
        print("TASK FILTERING PERFORMANCE TEST")
        print("=" * 70)

        filters_to_test = [
            ("domain", {"domain": "mana"}),
            ("status", {"status": StaffTask.STATUS_IN_PROGRESS}),
            ("priority", {"priority": "high"}),
            (
                "due_soon",
                {
                    "due_date__gte": date.today(),
                    "due_date__lte": date.today() + timedelta(days=7),
                },
            ),
        ]

        for filter_name, filter_kwargs in filters_to_test:
            reset_queries()

            start_time = time.time()

            tasks = (
                StaffTask.objects.filter(assignees=self.user, **filter_kwargs)
                .select_related("related_ppa")
                .prefetch_related("assignees")[:50]
            )

            task_list = list(tasks)

            end_time = time.time()

            duration = end_time - start_time
            query_count = len(connection.queries)

            print(f"\n{filter_name.upper()}:")
            print(f"  Duration: {duration:.3f}s")
            print(f"  Queries: {query_count}")
            print(f"  Results: {len(task_list)}")

            # All filtered queries should be fast
            self.assertLess(
                duration,
                0.5,
                f"Filtered task query ({filter_name}) should complete in under 0.5s",
            )


class ProjectPortfolioDashboardPerformanceTestCase(TestCase):
    """Test project portfolio dashboard performance."""

    @classmethod
    def setUpTestData(cls):
        """Create test data."""
        cls.user = User.objects.create_user(
            username="pmuser", email="pm@example.com", password="testpass123"
        )

        # Create 100 PPAs with various statuses and budgets
        for i in range(100):
            start_date = date(2025, 1, 1) + timedelta(days=i * 3)
            MonitoringEntry.objects.create(
                title=f"Portfolio PPA {i+1}",
                category=["oobc_ppa", "moa_ppa"][i % 2],
                status=["planning", "ongoing", "completed", "on_hold"][i % 4],
                budget_allocation=Decimal(str(500000 + i * 50000)),
                start_date=start_date,
                end_date=start_date + timedelta(days=365),
                progress=(i * 10) % 100,  # Progress from 0-90%
                created_by=cls.user,
            )

        print(f"Created 100 PPAs for portfolio testing")

    @override_settings(DEBUG=True)
    def test_portfolio_overview_performance(self):
        """
        Test portfolio dashboard overview query.

        Should aggregate all PPAs efficiently.
        """
        print("\n" + "=" * 70)
        print("PORTFOLIO DASHBOARD PERFORMANCE TEST")
        print("=" * 70)

        reset_queries()

        start_time = time.time()

        # Simulate portfolio dashboard query
        from django.db.models import Sum, Avg, Count, Q

        ppas = MonitoringEntry.objects.filter(
            category__in=["oobc_ppa", "moa_ppa"]
        ).select_related("created_by")

        # Get aggregates
        stats = ppas.aggregate(
            total_budget=Sum("budget_allocation"),
            avg_progress=Avg("progress"),
            total_ppas=Count("id"),
            active_ppas=Count("id", filter=Q(status="ongoing")),
            completed_ppas=Count("id", filter=Q(status="completed")),
        )

        # Get PPA list with stats
        ppa_list = list(
            ppas.values(
                "id",
                "title",
                "category",
                "status",
                "budget_allocation",
                "progress",
                "start_date",
                "end_date",
            )[:50]
        )

        end_time = time.time()

        duration = end_time - start_time
        query_count = len(connection.queries)

        print(f"\nResults:")
        print(f"  Duration: {duration:.3f}s")
        print(f"  Queries: {query_count}")
        print(f"  PPAs: {len(ppa_list)}")
        print(f"  Total Budget: {stats['total_budget']}")
        print(f"  Avg Progress: {stats['avg_progress']:.1f}%")

        # Performance assertions
        self.assertLess(
            duration, 1.0, f"Portfolio query took {duration:.3f}s, should be under 1s"
        )

        self.assertLess(
            query_count,
            15,
            f"Portfolio query used {query_count} queries, should be under 15",
        )


class StressTestCase(TestCase):
    """Stress tests with extreme data volumes."""

    @override_settings(DEBUG=True)
    def test_calendar_with_date_range_filtering(self):
        """
        Test that date range filtering properly limits data.

        Without date filtering, queries could be extremely slow.
        """
        print("\n" + "=" * 70)
        print("DATE RANGE FILTERING TEST")
        print("=" * 70)

        # Create user
        user = User.objects.create_user(
            username="dateuser", email="date@example.com", password="testpass123"
        )

        # Create events across 2 years
        for i in range(200):
            event_date = date(2024, 1, 1) + timedelta(days=i * 3)
            Event.objects.create(
                title=f"Historical Event {i+1}",
                event_type="meeting",
                start_date=event_date,
                start_time=dt_time(10, 0),
                organizer=user,
            )

        reset_queries()

        # Query with date range (1 month window)
        # Note: Current build_calendar_payload doesn't take date range
        # This tests that the implementation handles large datasets gracefully
        start_time = time.time()
        payload = build_calendar_payload(filter_modules=["coordination"])
        end_time = time.time()

        duration = end_time - start_time
        entry_count = len(payload["entries"])

        print(f"\nResults:")
        print(f"  Duration: {duration:.3f}s")
        print(f"  Entries: {entry_count}")

        # Should still complete in reasonable time even with many events
        self.assertLess(duration, 3.0, "Calendar should handle large datasets")

    def test_concurrent_calendar_requests(self):
        """
        Test calendar performance under concurrent access.

        Simulates multiple users accessing calendar simultaneously.
        """
        print("\n" + "=" * 70)
        print("CONCURRENT ACCESS TEST")
        print("=" * 70)

        import threading

        # Create test data
        user = User.objects.create_user(
            username="concurrent",
            email="concurrent@example.com",
            password="testpass123",
        )

        for i in range(50):
            Event.objects.create(
                title=f"Concurrent Test Event {i+1}",
                event_type="meeting",
                start_date=date(2025, 11, 1) + timedelta(days=i),
                start_time=dt_time(10, 0),
                organizer=user,
            )

        results = []

        def fetch_calendar():
            """Fetch calendar payload."""
            start = time.time()
            payload = build_calendar_payload()
            duration = time.time() - start
            results.append(duration)

        # Simulate 10 concurrent requests
        threads = []
        for i in range(10):
            thread = threading.Thread(target=fetch_calendar)
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        avg_duration = sum(results) / len(results) if results else 0
        max_duration = max(results) if results else 0

        print(f"\nResults ({len(results)} concurrent requests):")
        print(f"  Average: {avg_duration:.3f}s")
        print(f"  Maximum: {max_duration:.3f}s")

        # All requests should complete in reasonable time
        self.assertLess(
            max_duration, 5.0, "Concurrent requests should complete in under 5s"
        )


def run_performance_test_suite():
    """
    Convenience function to run all performance tests.

    Usage:
        python manage.py shell
        >>> from tests.test_performance_load import run_performance_test_suite
        >>> run_performance_test_suite()
    """
    from django.test import TestSuite, TextTestRunner

    suite = TestSuite()

    # Add all test cases
    suite.addTests(
        [
            CalendarPerformanceTestCase("test_calendar_aggregation_performance"),
            CalendarPerformanceTestCase("test_calendar_caching_effectiveness"),
            CalendarPerformanceTestCase("test_filtered_calendar_performance"),
            TaskDashboardPerformanceTestCase("test_user_task_query_performance"),
            TaskDashboardPerformanceTestCase("test_task_filtering_performance"),
            ProjectPortfolioDashboardPerformanceTestCase(
                "test_portfolio_overview_performance"
            ),
            StressTestCase("test_calendar_with_date_range_filtering"),
            StressTestCase("test_concurrent_calendar_requests"),
        ]
    )

    runner = TextTestRunner(verbosity=2)
    runner.run(suite)

    print("\n" + "=" * 70)
    print("PERFORMANCE TEST SUITE COMPLETE")
    print("=" * 70)
