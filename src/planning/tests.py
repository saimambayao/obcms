"""
Comprehensive Test Suite for Planning Module

Tests cover:
- Model creation, validation, and business logic
- View CRUD operations and permissions
- Full planning workflow integration
- Progress calculations and deadline tracking

Target: 80%+ test coverage
"""

from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
import datetime

from .models import StrategicPlan, StrategicGoal, AnnualWorkPlan, WorkPlanObjective

User = get_user_model()


class StrategicPlanModelTest(TestCase):
    """Test StrategicPlan model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@oobc.gov',
            password='testpass123'
        )

    def test_create_strategic_plan(self):
        """Test creating a strategic plan"""
        plan = StrategicPlan.objects.create(
            title='OOBC Strategic Plan 2024-2028',
            start_year=2024,
            end_year=2028,
            vision='Test vision statement',
            mission='Test mission statement',
            status='draft',
            created_by=self.user
        )

        self.assertEqual(plan.title, 'OOBC Strategic Plan 2024-2028')
        self.assertEqual(plan.year_range, '2024-2028')
        self.assertEqual(plan.duration_years, 5)
        self.assertFalse(plan.is_active)

    def test_year_range_validation(self):
        """Test that end year must be after start year"""
        plan = StrategicPlan(
            title='Invalid Plan',
            start_year=2028,
            end_year=2024,  # Invalid: before start year
            vision='Test',
            mission='Test',
            created_by=self.user
        )

        with self.assertRaises(ValidationError):
            plan.clean()

    def test_max_duration_validation(self):
        """Test that plans cannot exceed 10 years"""
        plan = StrategicPlan(
            title='Too Long Plan',
            start_year=2024,
            end_year=2035,  # 11 years
            vision='Test',
            mission='Test',
            created_by=self.user
        )

        with self.assertRaises(ValidationError):
            plan.clean()

    def test_overall_progress_calculation(self):
        """Test overall progress calculation from goals"""
        plan = StrategicPlan.objects.create(
            title='Test Plan',
            start_year=2024,
            end_year=2028,
            vision='Test',
            mission='Test',
            created_by=self.user
        )

        # Create goals with different completion percentages
        StrategicGoal.objects.create(
            strategic_plan=plan,
            title='Goal 1',
            description='Test',
            target_metric='Count',
            target_value=100,
            completion_percentage=50
        )
        StrategicGoal.objects.create(
            strategic_plan=plan,
            title='Goal 2',
            description='Test',
            target_metric='Count',
            target_value=100,
            completion_percentage=75
        )

        # Overall progress should be (50 + 75) / 2 = 62.5
        self.assertEqual(plan.overall_progress, 62.5)

    def test_year_range_property(self):
        """Test year_range property returns correct format"""
        plan = StrategicPlan.objects.create(
            title='Test Plan',
            start_year=2024,
            end_year=2028,
            vision='Test',
            mission='Test',
            created_by=self.user
        )

        self.assertEqual(plan.year_range, '2024-2028')

    def test_duration_years_property(self):
        """Test duration_years property calculates correctly"""
        plan = StrategicPlan.objects.create(
            title='Test Plan',
            start_year=2024,
            end_year=2028,
            vision='Test',
            mission='Test',
            created_by=self.user
        )

        # 2024, 2025, 2026, 2027, 2028 = 5 years
        self.assertEqual(plan.duration_years, 5)

    def test_is_active_property(self):
        """Test is_active property works correctly"""
        # Test draft plan
        draft_plan = StrategicPlan.objects.create(
            title='Draft Plan',
            start_year=2024,
            end_year=2028,
            vision='Test',
            mission='Test',
            status='draft',
            created_by=self.user
        )
        self.assertFalse(draft_plan.is_active)

        # Test active plan
        active_plan = StrategicPlan.objects.create(
            title='Active Plan',
            start_year=2024,
            end_year=2028,
            vision='Test',
            mission='Test',
            status='active',
            created_by=self.user
        )
        self.assertTrue(active_plan.is_active)


class StrategicGoalModelTest(TestCase):
    """Test StrategicGoal model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@oobc.gov',
            password='testpass123'
        )
        self.plan = StrategicPlan.objects.create(
            title='Test Plan',
            start_year=2024,
            end_year=2028,
            vision='Test',
            mission='Test',
            created_by=self.user
        )

    def test_create_strategic_goal(self):
        """Test creating a strategic goal"""
        goal = StrategicGoal.objects.create(
            strategic_plan=self.plan,
            title='Test Goal',
            description='Test description',
            target_metric='Schools built',
            target_value=20,
            current_value=5,
            completion_percentage=25,
            priority='high'
        )

        self.assertEqual(goal.title, 'Test Goal')
        self.assertEqual(goal.priority, 'high')
        self.assertEqual(float(goal.completion_percentage), 25.0)

    def test_goal_string_representation(self):
        """Test __str__ method shows title and percentage"""
        goal = StrategicGoal.objects.create(
            strategic_plan=self.plan,
            title='Education Goal',
            description='Test',
            target_metric='Schools',
            target_value=20,
            completion_percentage=75
        )

        self.assertEqual(str(goal), 'Education Goal (75%)')

    def test_is_on_track_calculation(self):
        """Test is_on_track property logic"""
        # Create goal at 50% completion
        goal = StrategicGoal.objects.create(
            strategic_plan=self.plan,
            title='Test Goal',
            description='Test',
            target_metric='Schools built',
            target_value=20,
            current_value=10,
            completion_percentage=50
        )

        # Should have is_on_track attribute
        self.assertIsNotNone(goal.is_on_track)
        self.assertIsInstance(goal.is_on_track, bool)

    def test_completion_percentage_validation(self):
        """Test completion percentage is validated to 0-100 range"""
        # Test valid percentage
        goal = StrategicGoal.objects.create(
            strategic_plan=self.plan,
            title='Valid Goal',
            description='Test',
            target_metric='Count',
            target_value=100,
            completion_percentage=50
        )
        self.assertEqual(float(goal.completion_percentage), 50.0)

        # Test invalid percentage (> 100) - should raise validation error
        with self.assertRaises(ValidationError):
            invalid_goal = StrategicGoal(
                strategic_plan=self.plan,
                title='Invalid Goal',
                description='Test',
                target_metric='Count',
                target_value=100,
                completion_percentage=150
            )
            invalid_goal.full_clean()


class AnnualWorkPlanModelTest(TestCase):
    """Test AnnualWorkPlan model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@oobc.gov',
            password='testpass123'
        )
        self.plan = StrategicPlan.objects.create(
            title='Test Plan',
            start_year=2024,
            end_year=2028,
            vision='Test',
            mission='Test',
            created_by=self.user
        )

    def test_create_annual_work_plan(self):
        """Test creating an annual work plan"""
        annual_plan = AnnualWorkPlan.objects.create(
            strategic_plan=self.plan,
            title='Annual Plan 2024',
            year=2024,
            description='Test annual plan',
            status='draft',
            created_by=self.user
        )

        self.assertEqual(annual_plan.title, 'Annual Plan 2024')
        self.assertEqual(annual_plan.year, 2024)
        self.assertEqual(str(annual_plan), 'Annual Plan 2024 (2024)')

    def test_year_validation(self):
        """Test year must be within strategic plan range"""
        # Valid year within range
        valid_plan = AnnualWorkPlan(
            strategic_plan=self.plan,
            title='Valid Annual Plan',
            year=2025,  # Within 2024-2028
            created_by=self.user
        )
        valid_plan.clean()  # Should not raise

        # Invalid year before range
        invalid_plan_before = AnnualWorkPlan(
            strategic_plan=self.plan,
            title='Invalid Annual Plan',
            year=2023,  # Before 2024
            created_by=self.user
        )
        with self.assertRaises(ValidationError):
            invalid_plan_before.clean()

        # Invalid year after range
        invalid_plan_after = AnnualWorkPlan(
            strategic_plan=self.plan,
            title='Invalid Annual Plan',
            year=2029,  # After 2028
            created_by=self.user
        )
        with self.assertRaises(ValidationError):
            invalid_plan_after.clean()

    def test_overall_progress_calculation(self):
        """Test overall progress calculated from objectives"""
        annual_plan = AnnualWorkPlan.objects.create(
            strategic_plan=self.plan,
            title='Annual Plan 2024',
            year=2024,
            created_by=self.user
        )

        # Create objectives with different completion percentages
        WorkPlanObjective.objects.create(
            annual_work_plan=annual_plan,
            title='Objective 1',
            description='Test',
            target_date=timezone.now().date() + datetime.timedelta(days=30),
            indicator='Count',
            target_value=10,
            completion_percentage=40
        )
        WorkPlanObjective.objects.create(
            annual_work_plan=annual_plan,
            title='Objective 2',
            description='Test',
            target_date=timezone.now().date() + datetime.timedelta(days=30),
            indicator='Count',
            target_value=10,
            completion_percentage=60
        )

        # Overall progress should be (40 + 60) / 2 = 50
        self.assertEqual(annual_plan.overall_progress, 50.0)

    def test_total_objectives_property(self):
        """Test total_objectives property returns correct count"""
        annual_plan = AnnualWorkPlan.objects.create(
            strategic_plan=self.plan,
            title='Annual Plan 2024',
            year=2024,
            created_by=self.user
        )

        # Initially zero
        self.assertEqual(annual_plan.total_objectives, 0)

        # Create 3 objectives
        for i in range(3):
            WorkPlanObjective.objects.create(
                annual_work_plan=annual_plan,
                title=f'Objective {i+1}',
                description='Test',
                target_date=timezone.now().date() + datetime.timedelta(days=30),
                indicator='Count',
                target_value=10
            )

        self.assertEqual(annual_plan.total_objectives, 3)

    def test_completed_objectives_property(self):
        """Test completed_objectives property returns correct count"""
        annual_plan = AnnualWorkPlan.objects.create(
            strategic_plan=self.plan,
            title='Annual Plan 2024',
            year=2024,
            created_by=self.user
        )

        # Create objectives with different statuses
        WorkPlanObjective.objects.create(
            annual_work_plan=annual_plan,
            title='Completed Objective',
            description='Test',
            target_date=timezone.now().date(),
            indicator='Count',
            target_value=10,
            status='completed'
        )
        WorkPlanObjective.objects.create(
            annual_work_plan=annual_plan,
            title='In Progress Objective',
            description='Test',
            target_date=timezone.now().date() + datetime.timedelta(days=30),
            indicator='Count',
            target_value=10,
            status='in_progress'
        )

        self.assertEqual(annual_plan.completed_objectives, 1)

    def test_unique_together_constraint(self):
        """Test unique_together constraint on strategic_plan + year"""
        # Create first annual plan
        AnnualWorkPlan.objects.create(
            strategic_plan=self.plan,
            title='Annual Plan 2024',
            year=2024,
            created_by=self.user
        )

        # Try to create duplicate (same plan + year) - should raise IntegrityError
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            AnnualWorkPlan.objects.create(
                strategic_plan=self.plan,
                title='Duplicate Annual Plan 2024',
                year=2024,  # Same year
                created_by=self.user
            )


class WorkPlanObjectiveModelTest(TestCase):
    """Test WorkPlanObjective model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@oobc.gov',
            password='testpass123'
        )
        self.plan = StrategicPlan.objects.create(
            title='Test Plan',
            start_year=2024,
            end_year=2028,
            vision='Test',
            mission='Test',
            created_by=self.user
        )
        self.annual_plan = AnnualWorkPlan.objects.create(
            strategic_plan=self.plan,
            title='Annual Plan 2024',
            year=2024,
            created_by=self.user
        )

    def test_create_work_plan_objective(self):
        """Test creating a work plan objective"""
        objective = WorkPlanObjective.objects.create(
            annual_work_plan=self.annual_plan,
            title='Build Classrooms',
            description='Build 5 classrooms in Lanao del Sur',
            target_date=timezone.now().date() + datetime.timedelta(days=90),
            indicator='Classrooms built',
            baseline_value=0,
            target_value=5,
            current_value=2,
            completion_percentage=40
        )

        self.assertEqual(objective.title, 'Build Classrooms')
        self.assertEqual(float(objective.target_value), 5.0)
        self.assertEqual(float(objective.completion_percentage), 40.0)

    def test_is_overdue_property(self):
        """Test is_overdue property logic"""
        # Create overdue objective (past target date, not completed)
        overdue_objective = WorkPlanObjective.objects.create(
            annual_work_plan=self.annual_plan,
            title='Overdue Objective',
            description='Test',
            target_date=timezone.now().date() - datetime.timedelta(days=10),  # Past date
            indicator='Count',
            target_value=10,
            status='in_progress'  # Not completed
        )
        self.assertTrue(overdue_objective.is_overdue)

        # Create on-time objective (future target date)
        ontime_objective = WorkPlanObjective.objects.create(
            annual_work_plan=self.annual_plan,
            title='On-time Objective',
            description='Test',
            target_date=timezone.now().date() + datetime.timedelta(days=30),  # Future date
            indicator='Count',
            target_value=10,
            status='in_progress'
        )
        self.assertFalse(ontime_objective.is_overdue)

        # Create completed objective (past date but completed)
        completed_objective = WorkPlanObjective.objects.create(
            annual_work_plan=self.annual_plan,
            title='Completed Objective',
            description='Test',
            target_date=timezone.now().date() - datetime.timedelta(days=5),  # Past date
            indicator='Count',
            target_value=10,
            status='completed'  # Completed
        )
        self.assertFalse(completed_objective.is_overdue)

    def test_days_remaining_property(self):
        """Test days_remaining property calculation"""
        target_date = timezone.now().date() + datetime.timedelta(days=30)
        objective = WorkPlanObjective.objects.create(
            annual_work_plan=self.annual_plan,
            title='Test Objective',
            description='Test',
            target_date=target_date,
            indicator='Count',
            target_value=10
        )

        # Should be approximately 30 days (allowing for test execution time)
        self.assertAlmostEqual(objective.days_remaining, 30, delta=1)

    def test_update_progress_from_indicator_method(self):
        """Test update_progress_from_indicator method calculates correctly"""
        objective = WorkPlanObjective.objects.create(
            annual_work_plan=self.annual_plan,
            title='Test Objective',
            description='Test',
            target_date=timezone.now().date() + datetime.timedelta(days=30),
            indicator='Schools built',
            baseline_value=0,
            target_value=10,
            current_value=5,  # 50% progress
            completion_percentage=0  # Will be calculated
        )

        # Update progress from indicator
        objective.update_progress_from_indicator()

        # Refresh from database
        objective.refresh_from_db()

        # Progress should be 50% ((5-0)/(10-0) * 100 = 50)
        self.assertEqual(float(objective.completion_percentage), 50.0)


class StrategicPlanViewsTest(TestCase):
    """Test strategic plan views"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@oobc.gov',
            password='testpass123'
        )
        self.client.force_login(self.user)

        self.plan = StrategicPlan.objects.create(
            title='Test Plan',
            start_year=2024,
            end_year=2028,
            vision='Test vision',
            mission='Test mission',
            status='active',
            created_by=self.user
        )

    def test_strategic_plan_list_view(self):
        """Test strategic plan list view"""
        url = reverse('planning:strategic_list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Plan')

    def test_strategic_plan_detail_view(self):
        """Test strategic plan detail view"""
        url = reverse('planning:strategic_detail', kwargs={'pk': self.plan.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Plan')
        self.assertContains(response, '2024-2028')

    def test_strategic_plan_create_view_get(self):
        """Test GET request to create view"""
        url = reverse('planning:strategic_create')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_strategic_plan_create_view_post(self):
        """Test POST request to create view"""
        url = reverse('planning:strategic_create')
        data = {
            'title': 'New Strategic Plan',
            'start_year': 2025,
            'end_year': 2029,
            'vision': 'New vision',
            'mission': 'New mission',
            'status': 'draft',
        }
        response = self.client.post(url, data)

        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)

        # Verify plan was created
        new_plan = StrategicPlan.objects.get(title='New Strategic Plan')
        self.assertEqual(new_plan.start_year, 2025)
        self.assertEqual(new_plan.created_by, self.user)

    def test_strategic_plan_edit_view(self):
        """Test edit view for strategic plan"""
        url = reverse('planning:strategic_edit', kwargs={'pk': self.plan.pk})

        # Test GET
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST
        data = {
            'title': 'Updated Plan Title',
            'start_year': 2024,
            'end_year': 2028,
            'vision': 'Updated vision',
            'mission': 'Updated mission',
            'status': 'active',
        }
        response = self.client.post(url, data)

        # Should redirect after successful update
        self.assertEqual(response.status_code, 302)

        # Verify update
        self.plan.refresh_from_db()
        self.assertEqual(self.plan.title, 'Updated Plan Title')

    def test_strategic_plan_delete_view(self):
        """Test delete view for strategic plan"""
        url = reverse('planning:strategic_delete', kwargs={'pk': self.plan.pk})
        response = self.client.post(url)

        # Should redirect after deletion
        self.assertEqual(response.status_code, 302)

        # Verify plan was deleted (or archived)
        # Note: Actual implementation may archive instead of delete
        self.assertFalse(StrategicPlan.objects.filter(pk=self.plan.pk, status='active').exists())

    def test_unauthenticated_access_redirects(self):
        """Test that unauthenticated users are redirected"""
        self.client.logout()

        url = reverse('planning:strategic_list')
        response = self.client.get(url)

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)


class PlanningIntegrationTest(TestCase):
    """Test full planning flow integration"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@oobc.gov',
            password='testpass123'
        )

        # Create strategic plan
        self.strategic_plan = StrategicPlan.objects.create(
            title='OOBC Strategic Plan 2024-2028',
            start_year=2024,
            end_year=2028,
            vision='Test vision',
            mission='Test mission',
            status='active',
            created_by=self.user
        )

        # Create strategic goal
        self.strategic_goal = StrategicGoal.objects.create(
            strategic_plan=self.strategic_plan,
            title='Improve Education Access',
            description='Build schools in OBCs',
            target_metric='Schools built',
            target_value=20,
            priority='critical'
        )

        # Create annual work plan
        self.annual_plan = AnnualWorkPlan.objects.create(
            strategic_plan=self.strategic_plan,
            title='OOBC Annual Work Plan 2024',
            year=2024,
            status='active',
            created_by=self.user
        )

    def test_strategic_plan_to_goal_to_objective_flow(self):
        """Test full flow from strategic plan to objectives"""
        # Create objective linked to strategic goal
        objective = WorkPlanObjective.objects.create(
            annual_work_plan=self.annual_plan,
            strategic_goal=self.strategic_goal,
            title='Build 5 classrooms in Lanao del Sur',
            description='Construct 5 new classrooms',
            target_date=timezone.now().date() + datetime.timedelta(days=90),
            indicator='Classrooms built',
            baseline_value=0,
            target_value=5,
            current_value=3,
            completion_percentage=60
        )

        # Verify relationships
        self.assertEqual(objective.annual_work_plan, self.annual_plan)
        self.assertEqual(objective.strategic_goal, self.strategic_goal)
        self.assertEqual(self.annual_plan.strategic_plan, self.strategic_plan)

        # Verify objective is in goal's related objectives
        self.assertIn(objective, self.strategic_goal.work_plan_objectives.all())

    def test_goal_progress_affects_plan_progress(self):
        """Test that goal progress affects overall strategic plan progress"""
        # Initially, plan should have 0% progress (one goal at 0%)
        initial_progress = self.strategic_plan.overall_progress
        self.assertEqual(initial_progress, 0.0)

        # Update goal completion percentage
        self.strategic_goal.completion_percentage = 50
        self.strategic_goal.save()

        # Strategic plan progress should reflect goal progress
        updated_progress = self.strategic_plan.overall_progress
        self.assertEqual(updated_progress, 50.0)

        # Add another goal at different completion
        second_goal = StrategicGoal.objects.create(
            strategic_plan=self.strategic_plan,
            title='Improve Healthcare Access',
            description='Build health centers',
            target_metric='Health centers built',
            target_value=10,
            completion_percentage=75,
            priority='high'
        )

        # Plan progress should be average of both goals: (50 + 75) / 2 = 62.5
        final_progress = self.strategic_plan.overall_progress
        self.assertEqual(final_progress, 62.5)
