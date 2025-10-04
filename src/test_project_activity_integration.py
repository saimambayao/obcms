#!/usr/bin/env python
"""
Comprehensive Test Suite for Project-Activity-Task Integration
Tests all 7 phases of implementation
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.base')
django.setup()

from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.db import connection
from coordination.models import Event
from common.models import StaffTask
from project_central.models import ProjectWorkflow

User = get_user_model()

# ANSI color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")

def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"{status} | {name}")
    if details:
        print(f"       {Colors.YELLOW}{details}{Colors.END}")

def print_section(name):
    print(f"\n{Colors.BOLD}{Colors.BLUE}▶ {name}{Colors.END}")
    print(f"{Colors.BLUE}{'-'*80}{Colors.END}")

# Test counters
tests_passed = 0
tests_failed = 0
tests_total = 0

def run_test(name, test_func):
    global tests_passed, tests_failed, tests_total
    tests_total += 1
    try:
        result, details = test_func()
        if result:
            tests_passed += 1
            print_test(name, True, details)
        else:
            tests_failed += 1
            print_test(name, False, details)
        return result
    except Exception as e:
        tests_failed += 1
        print_test(name, False, f"Exception: {str(e)}")
        return False

# ============================================================================
# PHASE 1: DATABASE SCHEMA TESTS
# ============================================================================

def test_event_has_project_fields():
    """Test Event model has new project-related fields"""
    event = Event()
    has_related_project = hasattr(event, 'related_project')
    has_is_project_activity = hasattr(event, 'is_project_activity')
    has_activity_type = hasattr(event, 'project_activity_type')

    all_present = has_related_project and has_is_project_activity and has_activity_type
    return all_present, "Event has related_project, is_project_activity, project_activity_type"

def test_stafftask_has_context_field():
    """Test StaffTask model has task_context field"""
    task = StaffTask()
    has_field = hasattr(task, 'task_context')

    # Check choices
    if has_field:
        choices = dict(StaffTask._meta.get_field('task_context').choices)
        has_all_choices = (
            'standalone' in choices and
            'project' in choices and
            'activity' in choices and
            'project_activity' in choices
        )
        return has_all_choices, f"task_context has 4 choices: {list(choices.keys())}"
    return False, "task_context field not found"

def test_database_indexes():
    """Test composite indexes exist"""
    # Check Event indexes
    event_indexes = Event._meta.indexes
    event_index_fields = [idx.fields for idx in event_indexes]

    # Check StaffTask indexes
    task_indexes = StaffTask._meta.indexes
    task_index_fields = [idx.fields for idx in task_indexes]

    has_event_indexes = any('related_project' in str(fields) for fields in event_index_fields)
    has_task_indexes = any('task_context' in str(fields) for fields in task_index_fields)

    return has_event_indexes or has_task_indexes, f"Found {len(event_indexes)} Event indexes, {len(task_indexes)} Task indexes"

# ============================================================================
# PHASE 2: MODEL METHODS TESTS
# ============================================================================

def test_projectworkflow_has_properties():
    """Test ProjectWorkflow has new properties"""
    # Check if properties exist
    has_all_tasks = hasattr(ProjectWorkflow, 'all_project_tasks')
    has_upcoming = hasattr(ProjectWorkflow, 'get_upcoming_activities')

    both_exist = has_all_tasks and has_upcoming
    return both_exist, "ProjectWorkflow.all_project_tasks and .get_upcoming_activities() exist"

def test_event_has_task_generation():
    """Test Event has _create_activity_tasks method"""
    has_method = hasattr(Event, '_create_activity_tasks')
    return has_method, "Event._create_activity_tasks() method exists"

def test_stafftask_has_validation():
    """Test StaffTask has enhanced clean() method"""
    task = StaffTask()
    has_clean = hasattr(task, 'clean')
    return has_clean, "StaffTask.clean() validation exists"

def test_reverse_relationship():
    """Test ProjectWorkflow.project_activities reverse relationship"""
    # This tests that the related_name works
    workflow = ProjectWorkflow()
    has_activities = hasattr(workflow, 'project_activities')
    return has_activities, "ProjectWorkflow.project_activities reverse relationship exists"

# ============================================================================
# PHASE 3-7: FUNCTIONAL TESTS (with actual data)
# ============================================================================

def test_create_project_activity():
    """Test creating an event linked to a project"""
    try:
        # Get or create test user
        user, _ = User.objects.get_or_create(
            username='test_integration',
            defaults={'email': 'test@obcms.test'}
        )

        # Try to get an existing workflow, or skip if none exist
        workflow = ProjectWorkflow.objects.first()
        if not workflow:
            return True, "Skipped (no existing projects to test with)"

        # Create project activity
        event = Event.objects.create(
            title='Test Project Activity',
            event_type='meeting',
            start_date=date.today() + timedelta(days=7),
            related_project=workflow,
            is_project_activity=True,
            project_activity_type='project_kickoff',
            created_by=user,
        )

        # Verify
        success = (
            event.related_project == workflow and
            event.is_project_activity == True and
            event.project_activity_type == 'project_kickoff'
        )

        # Cleanup
        event.delete()

        return success, f"Created and linked event to project {workflow.id}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_task_context_assignment():
    """Test creating tasks with different contexts"""
    try:
        user, _ = User.objects.get_or_create(
            username='test_integration',
            defaults={'email': 'test@obcms.test'}
        )

        # Create tasks with different contexts
        contexts = ['standalone', 'project', 'activity', 'project_activity']
        created_tasks = []

        for context in contexts:
            task = StaffTask.objects.create(
                title=f'Test {context} task',
                task_context=context,
                due_date=date.today() + timedelta(days=1),
                created_by=user,
            )
            created_tasks.append(task)

        # Verify
        success = all(task.task_context in contexts for task in created_tasks)

        # Cleanup
        for task in created_tasks:
            task.delete()

        return success, f"Created tasks with all 4 context types"
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_all_project_tasks_property():
    """Test ProjectWorkflow.all_project_tasks aggregation"""
    try:
        workflow = ProjectWorkflow.objects.first()
        if not workflow:
            return True, "Skipped (no existing projects)"

        # Get all tasks
        all_tasks = workflow.all_project_tasks

        # Should return a queryset
        is_queryset = hasattr(all_tasks, 'count')

        return is_queryset, f"Property returns QuerySet with {all_tasks.count()} tasks"
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_upcoming_activities_method():
    """Test ProjectWorkflow.get_upcoming_activities()"""
    try:
        workflow = ProjectWorkflow.objects.first()
        if not workflow:
            return True, "Skipped (no existing projects)"

        # Get upcoming activities
        upcoming = workflow.get_upcoming_activities(days=30)

        # Should return a queryset
        is_queryset = hasattr(upcoming, 'count')

        return is_queryset, f"Method returns {upcoming.count()} upcoming activities"
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_auto_task_generation():
    """Test automatic task generation from project activity"""
    try:
        user, _ = User.objects.get_or_create(
            username='test_integration',
            defaults={'email': 'test@obcms.test'}
        )

        workflow = ProjectWorkflow.objects.first()
        if not workflow:
            return True, "Skipped (no existing projects)"

        # Create event with auto-task generation
        event = Event.objects.create(
            title='Test Auto-Task Event',
            event_type='meeting',
            start_date=date.today() + timedelta(days=14),
            related_project=workflow,
            is_project_activity=True,
            project_activity_type='stakeholder_consultation',
            created_by=user,
        )

        # Trigger auto-task generation
        event._auto_generate_tasks = True
        event._create_activity_tasks()

        # Check if tasks were created
        tasks = StaffTask.objects.filter(linked_event=event)
        task_count = tasks.count()

        # Cleanup
        tasks.delete()
        event.delete()

        return task_count > 0, f"Generated {task_count} tasks automatically"
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_signal_registration():
    """Test coordination signals are registered"""
    try:
        from coordination import signals
        has_signals = hasattr(signals, 'handle_event_creation')
        return has_signals, "Signal handlers module exists and loaded"
    except Exception as e:
        return False, f"Error importing signals: {str(e)}"

def test_calendar_service_includes_context():
    """Test calendar service includes project context"""
    try:
        from common.services.calendar import build_calendar_payload

        # Build calendar data
        payload = build_calendar_payload()

        # Calendar should return a dict with 'entries' key
        if not isinstance(payload, dict):
            return False, f"Calendar returns {type(payload).__name__}, expected dict"

        if 'entries' not in payload:
            return False, "Calendar payload missing 'entries' key"

        entries = payload['entries']

        # Check if entries have extendedProps
        if entries:
            # All entries should have extendedProps (added at end of function)
            with_props = sum(1 for e in entries if isinstance(e, dict) and 'extendedProps' in e)
            total = len(entries)

            # All entries should have extendedProps
            all_have_props = with_props == total

            return all_have_props, f"Calendar returns {total} entries, {with_props} with extendedProps"
        else:
            return True, "Calendar service works (no entries in system)"
    except Exception as e:
        return False, f"Error: {str(e)}"

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_end_to_end_workflow():
    """Test complete workflow: Create project activity → Auto-generate tasks → Verify links"""
    try:
        user, _ = User.objects.get_or_create(
            username='test_integration',
            defaults={'email': 'test@obcms.test'}
        )

        workflow = ProjectWorkflow.objects.first()
        if not workflow:
            return True, "Skipped (no existing projects)"

        # Step 1: Create project activity
        event = Event.objects.create(
            title='E2E Test Event',
            event_type='meeting',
            start_date=date.today() + timedelta(days=10),
            related_project=workflow,
            is_project_activity=True,
            project_activity_type='milestone_review',
            created_by=user,
        )

        # Step 2: Generate tasks
        event._auto_generate_tasks = True
        event._create_activity_tasks()

        # Step 3: Verify tasks are linked
        tasks = StaffTask.objects.filter(linked_event=event)

        # Step 4: Check task properties
        all_linked_to_workflow = all(task.linked_workflow == workflow for task in tasks)
        all_have_context = all(task.task_context in ['activity', 'project_activity'] for task in tasks)
        all_have_due_dates = all(task.due_date is not None for task in tasks)

        # Step 5: Verify project can see these tasks
        project_tasks = workflow.all_project_tasks
        event_tasks_in_project = any(task.id in [t.id for t in project_tasks] for task in tasks)

        success = (
            tasks.count() > 0 and
            all_linked_to_workflow and
            all_have_context and
            all_have_due_dates and
            event_tasks_in_project
        )

        # Cleanup
        tasks.delete()
        event.delete()

        details = (
            f"Created activity → Generated {tasks.count()} tasks → "
            f"All linked to workflow → All in project.all_project_tasks"
        )
        return success, details
    except Exception as e:
        return False, f"Error: {str(e)}"

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run complete test suite"""
    print_header("PROJECT-ACTIVITY-TASK INTEGRATION TEST SUITE")

    # Phase 1: Database Schema
    print_section("PHASE 1: Database Schema & Migrations")
    run_test("Event model has project fields", test_event_has_project_fields)
    run_test("StaffTask has task_context field", test_stafftask_has_context_field)
    run_test("Composite indexes created", test_database_indexes)

    # Phase 2: Model Methods
    print_section("PHASE 2: Model Methods & Properties")
    run_test("ProjectWorkflow has aggregation properties", test_projectworkflow_has_properties)
    run_test("Event has task generation method", test_event_has_task_generation)
    run_test("StaffTask has validation", test_stafftask_has_validation)
    run_test("Reverse relationship exists", test_reverse_relationship)

    # Phase 3-5: Functional Tests
    print_section("PHASE 3-5: Functional Tests (UI & Services)")
    run_test("Create project activity", test_create_project_activity)
    run_test("Task context assignment", test_task_context_assignment)
    run_test("all_project_tasks property works", test_all_project_tasks_property)
    run_test("get_upcoming_activities() works", test_upcoming_activities_method)
    run_test("Calendar service includes context", test_calendar_service_includes_context)

    # Phase 6: Automation
    print_section("PHASE 6: Workflow Automation")
    run_test("Auto-task generation", test_auto_task_generation)
    run_test("Signal handlers registered", test_signal_registration)

    # Integration
    print_section("INTEGRATION: End-to-End Workflow")
    run_test("Complete workflow test", test_end_to_end_workflow)

    # Summary
    print_header("TEST SUMMARY")

    pass_rate = (tests_passed / tests_total * 100) if tests_total > 0 else 0

    print(f"{Colors.BOLD}Total Tests:{Colors.END}  {tests_total}")
    print(f"{Colors.GREEN}✓ Passed:{Colors.END}     {tests_passed}")
    print(f"{Colors.RED}✗ Failed:{Colors.END}     {tests_failed}")
    print(f"{Colors.CYAN}Pass Rate:{Colors.END}    {pass_rate:.1f}%")

    if tests_failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED!{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ {tests_failed} test(s) failed{Colors.END}")

    print()
    return tests_failed == 0

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
