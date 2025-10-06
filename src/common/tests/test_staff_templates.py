"""
Tests for Staff Query Templates

Validates pattern matching, entity extraction, and query generation
for staff directory, task management, preferences, and activity queries.
"""

import pytest
from common.ai_services.chat.query_templates.staff import (
    STAFF_TEMPLATES,
    STAFF_DIRECTORY_TEMPLATES,
    TASK_MANAGEMENT_TEMPLATES,
    USER_PREFERENCES_TEMPLATES,
    ACTIVITY_TRACKING_TEMPLATES,
)
from common.ai_services.chat.query_templates.base import QueryTemplate


class TestStaffTemplateStructure:
    """Test template structure and organization."""

    def test_staff_templates_combined(self):
        """Test that STAFF_TEMPLATES combines all template groups."""
        expected_count = (
            len(STAFF_DIRECTORY_TEMPLATES) +
            len(TASK_MANAGEMENT_TEMPLATES) +
            len(USER_PREFERENCES_TEMPLATES) +
            len(ACTIVITY_TRACKING_TEMPLATES)
        )
        assert len(STAFF_TEMPLATES) == expected_count
        assert len(STAFF_TEMPLATES) >= 15  # Minimum 15 templates

    def test_all_templates_are_query_templates(self):
        """Test that all templates are QueryTemplate instances."""
        for template in STAFF_TEMPLATES:
            assert isinstance(template, QueryTemplate)
            assert hasattr(template, 'id')
            assert hasattr(template, 'category')
            assert hasattr(template, 'pattern')

    def test_all_templates_have_category_staff(self):
        """Test that all templates belong to 'staff' category."""
        for template in STAFF_TEMPLATES:
            assert template.category == 'staff'

    def test_template_ids_are_unique(self):
        """Test that all template IDs are unique."""
        template_ids = [t.id for t in STAFF_TEMPLATES]
        assert len(template_ids) == len(set(template_ids))

    def test_all_templates_have_examples(self):
        """Test that all templates have example queries."""
        for template in STAFF_TEMPLATES:
            assert len(template.examples) > 0


class TestStaffDirectoryTemplates:
    """Test staff directory query templates."""

    def test_staff_all_users_pattern(self):
        """Test pattern matching for listing all staff."""
        template = next(t for t in STAFF_TEMPLATES if t.id == 'staff_all_users')

        # Should match
        assert template.matches("show me all staff")
        assert template.matches("list users")
        assert template.matches("display team members")
        assert template.matches("get all staff")

        # Should not match
        assert not template.matches("show me coordinators")
        assert not template.matches("count staff")

    def test_staff_by_role_pattern(self):
        """Test pattern matching for staff by role."""
        template = next(t for t in STAFF_TEMPLATES if t.id == 'staff_by_role')

        # Should match
        assert template.matches("show me coordinators")
        assert template.matches("list admins")
        assert template.matches("display managers")

        # Should not match
        assert not template.matches("show all staff")
        assert not template.matches("count users")

    def test_staff_count_total_pattern(self):
        """Test pattern matching for staff count."""
        template = next(t for t in STAFF_TEMPLATES if t.id == 'staff_count_total')

        # Should match
        assert template.matches("how many staff do we have?")
        assert template.matches("count users")
        assert template.matches("total staff")
        assert template.matches("number of team members")

        # Should not match
        assert not template.matches("show staff")
        assert not template.matches("list users")

    def test_staff_count_by_role_pattern(self):
        """Test pattern matching for staff count by role."""
        template = next(t for t in STAFF_TEMPLATES if t.id == 'staff_count_by_role')

        # Should match
        assert template.matches("how many coordinators?")
        assert template.matches("count admins")
        assert template.matches("total managers")

        # Should not match
        assert not template.matches("how many staff?")
        assert not template.matches("list coordinators")

    def test_staff_search_by_name_pattern(self):
        """Test pattern matching for staff search."""
        template = next(t for t in STAFF_TEMPLATES if t.id == 'staff_search_by_name')

        # Should match
        assert template.matches("find John staff")
        assert template.matches("search Maria user")
        assert template.matches("who is Ahmed?")

        # Should not match
        assert not template.matches("show all staff")
        assert not template.matches("count users")


class TestTaskManagementTemplates:
    """Test task management query templates."""

    def test_tasks_my_tasks_pattern(self):
        """Test pattern matching for my tasks."""
        template = next(t for t in STAFF_TEMPLATES if t.id == 'tasks_my_tasks')

        # Should match
        assert template.matches("my tasks")
        assert template.matches("show my tasks")
        assert template.matches("get my tasks")
        assert template.matches("what are my tasks?")

        # Should not match
        assert not template.matches("team tasks")
        assert not template.matches("overdue tasks")

    def test_tasks_overdue_pattern(self):
        """Test pattern matching for overdue tasks."""
        template = next(t for t in STAFF_TEMPLATES if t.id == 'tasks_overdue')

        # Should match
        assert template.matches("overdue tasks")
        assert template.matches("late tasks")
        assert template.matches("past due tasks")

        # Should not match
        assert not template.matches("my tasks")
        assert not template.matches("completed tasks")

    def test_tasks_today_pattern(self):
        """Test pattern matching for today's tasks."""
        template = next(t for t in STAFF_TEMPLATES if t.id == 'tasks_today')

        # Should match
        assert template.matches("today tasks")
        assert template.matches("today's tasks")
        assert template.matches("tasks for today")

        # Should not match
        assert not template.matches("overdue tasks")
        assert not template.matches("completed tasks")

    def test_tasks_completed_pattern(self):
        """Test pattern matching for completed tasks."""
        template = next(t for t in STAFF_TEMPLATES if t.id == 'tasks_completed')

        # Should match
        assert template.matches("completed tasks")
        assert template.matches("done tasks")
        assert template.matches("finished tasks")

        # Should not match
        assert not template.matches("my tasks")
        assert not template.matches("overdue tasks")

    def test_tasks_high_priority_pattern(self):
        """Test pattern matching for high priority tasks."""
        template = next(t for t in STAFF_TEMPLATES if t.id == 'tasks_high_priority')

        # Should match
        assert template.matches("high priority tasks")
        assert template.matches("urgent tasks")
        assert template.matches("critical tasks")

        # Should not match
        assert not template.matches("my tasks")
        assert not template.matches("completed tasks")

    def test_tasks_count_my_tasks_pattern(self):
        """Test pattern matching for task count."""
        template = next(t for t in STAFF_TEMPLATES if t.id == 'tasks_count_my_tasks')

        # Should match
        assert template.matches("how many my tasks?")
        assert template.matches("count my tasks")
        assert template.matches("how many tasks do I have?")

        # Should not match
        assert not template.matches("my tasks")
        assert not template.matches("show tasks")


class TestUserPreferencesTemplates:
    """Test user preferences query templates."""

    def test_preferences_notification_settings_pattern(self):
        """Test pattern matching for notification settings."""
        template = next(t for t in STAFF_TEMPLATES if t.id == 'preferences_notification_settings')

        # Should match
        assert template.matches("notification settings")
        assert template.matches("alert preferences")
        assert template.matches("email settings")

        # Should not match
        assert not template.matches("dashboard settings")
        assert not template.matches("my tasks")

    def test_preferences_dashboard_config_pattern(self):
        """Test pattern matching for dashboard settings."""
        template = next(t for t in STAFF_TEMPLATES if t.id == 'preferences_dashboard_config')

        # Should match
        assert template.matches("dashboard settings")
        assert template.matches("home preferences")
        assert template.matches("dashboard config")

        # Should not match
        assert not template.matches("notification settings")
        assert not template.matches("my tasks")


class TestActivityTrackingTemplates:
    """Test activity tracking query templates."""

    def test_activity_recent_pattern(self):
        """Test pattern matching for recent activity."""
        template = next(t for t in STAFF_TEMPLATES if t.id == 'activity_recent')

        # Should match
        assert template.matches("recent activity")
        assert template.matches("latest activity")
        assert template.matches("my activity")
        assert template.matches("activity history")

        # Should not match
        assert not template.matches("work log")
        assert not template.matches("my tasks")

    def test_activity_work_log_pattern(self):
        """Test pattern matching for work log."""
        template = next(t for t in STAFF_TEMPLATES if t.id == 'activity_work_log')

        # Should match
        assert template.matches("work log")
        assert template.matches("time log")
        assert template.matches("my contributions")
        assert template.matches("work summary")

        # Should not match
        assert not template.matches("recent activity")
        assert not template.matches("my tasks")


class TestStaffTemplatePriorities:
    """Test template priority assignments."""

    def test_my_tasks_has_highest_priority(self):
        """Test that my tasks has priority 10."""
        template = next(t for t in STAFF_TEMPLATES if t.id == 'tasks_my_tasks')
        assert template.priority == 10

    def test_overdue_tasks_has_high_priority(self):
        """Test that overdue tasks has priority 10."""
        template = next(t for t in STAFF_TEMPLATES if t.id == 'tasks_overdue')
        assert template.priority == 10

    def test_search_by_name_has_high_priority(self):
        """Test that name search has priority 9."""
        template = next(t for t in STAFF_TEMPLATES if t.id == 'staff_search_by_name')
        assert template.priority == 9

    def test_all_priorities_in_valid_range(self):
        """Test that all priorities are between 1 and 10."""
        for template in STAFF_TEMPLATES:
            assert 1 <= template.priority <= 10


class TestStaffTemplateTags:
    """Test template tagging."""

    def test_directory_templates_have_staff_tag(self):
        """Test that directory templates are tagged 'staff'."""
        for template in STAFF_DIRECTORY_TEMPLATES:
            assert 'staff' in template.tags

    def test_task_templates_have_tasks_tag(self):
        """Test that task templates are tagged 'tasks'."""
        for template in TASK_MANAGEMENT_TEMPLATES:
            assert 'tasks' in template.tags

    def test_count_templates_have_count_tag(self):
        """Test that count templates are tagged 'count'."""
        count_templates = [t for t in STAFF_TEMPLATES if 'count' in t.id]
        for template in count_templates:
            assert 'count' in template.tags

    def test_list_templates_have_list_tag(self):
        """Test that list templates are tagged 'list'."""
        list_templates = [t for t in STAFF_TEMPLATES if 'list' in t.query_template or 'all' in t.id]
        for template in list_templates:
            assert 'list' in template.tags


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
