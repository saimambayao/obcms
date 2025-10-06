"""
Tests for General System Query Templates

Validates pattern matching, entity extraction, and query generation
for help, system status, navigation, and metadata queries.
"""

import pytest
from common.ai_services.chat.query_templates.general import (
    GENERAL_TEMPLATES,
    HELP_DOCUMENTATION_TEMPLATES,
    SYSTEM_STATUS_TEMPLATES,
    NAVIGATION_TEMPLATES,
    METADATA_TEMPLATES,
)
from common.ai_services.chat.query_templates.base import QueryTemplate


class TestGeneralTemplateStructure:
    """Test template structure and organization."""

    def test_general_templates_combined(self):
        """Test that GENERAL_TEMPLATES combines all template groups."""
        expected_count = (
            len(HELP_DOCUMENTATION_TEMPLATES) +
            len(SYSTEM_STATUS_TEMPLATES) +
            len(NAVIGATION_TEMPLATES) +
            len(METADATA_TEMPLATES)
        )
        assert len(GENERAL_TEMPLATES) == expected_count
        assert len(GENERAL_TEMPLATES) >= 15  # Minimum 15 templates

    def test_all_templates_are_query_templates(self):
        """Test that all templates are QueryTemplate instances."""
        for template in GENERAL_TEMPLATES:
            assert isinstance(template, QueryTemplate)
            assert hasattr(template, 'id')
            assert hasattr(template, 'category')
            assert hasattr(template, 'pattern')

    def test_all_templates_have_category_general(self):
        """Test that all templates belong to 'general' category."""
        for template in GENERAL_TEMPLATES:
            assert template.category == 'general'

    def test_template_ids_are_unique(self):
        """Test that all template IDs are unique."""
        template_ids = [t.id for t in GENERAL_TEMPLATES]
        assert len(template_ids) == len(set(template_ids))

    def test_all_templates_have_examples(self):
        """Test that all templates have example queries."""
        for template in GENERAL_TEMPLATES:
            assert len(template.examples) > 0


class TestHelpDocumentationTemplates:
    """Test help and documentation query templates."""

    def test_help_general_pattern(self):
        """Test pattern matching for general help."""
        template = next(t for t in GENERAL_TEMPLATES if t.id == 'help_general')

        # Should match
        assert template.matches("help")
        assert template.matches("I need help")
        assert template.matches("assist me")
        assert template.matches("how do I use this?")

        # Should not match
        assert not template.matches("system status")
        assert not template.matches("go to dashboard")

    def test_help_how_to_create_pattern(self):
        """Test pattern matching for create help."""
        template = next(t for t in GENERAL_TEMPLATES if t.id == 'help_how_to_create')

        # Should match
        assert template.matches("how to create assessment")
        assert template.matches("how do I add community")
        assert template.matches("help me create project")
        assert template.matches("how to add new task")

        # Should not match
        assert not template.matches("help")
        assert not template.matches("how to edit")

    def test_help_how_to_edit_pattern(self):
        """Test pattern matching for edit help."""
        template = next(t for t in GENERAL_TEMPLATES if t.id == 'help_how_to_edit')

        # Should match
        assert template.matches("how to edit assessment")
        assert template.matches("how do I update community")
        assert template.matches("help me modify project")
        assert template.matches("how to change task status")

        # Should not match
        assert not template.matches("help")
        assert not template.matches("how to create")

    def test_help_documentation_link_pattern(self):
        """Test pattern matching for documentation access."""
        template = next(t for t in GENERAL_TEMPLATES if t.id == 'help_documentation_link')

        # Should match
        assert template.matches("documentation")
        assert template.matches("user manual")
        assert template.matches("guide for communities")
        assert template.matches("show docs")

        # Should not match
        assert not template.matches("help")
        assert not template.matches("FAQ")

    def test_help_faq_pattern(self):
        """Test pattern matching for FAQ."""
        template = next(t for t in GENERAL_TEMPLATES if t.id == 'help_faq')

        # Should match
        assert template.matches("FAQ")
        assert template.matches("frequently asked questions")
        assert template.matches("common questions")

        # Should not match
        assert not template.matches("help")
        assert not template.matches("documentation")


class TestSystemStatusTemplates:
    """Test system status query templates."""

    def test_system_status_pattern(self):
        """Test pattern matching for system status."""
        template = next(t for t in GENERAL_TEMPLATES if t.id == 'system_status')

        # Should match
        assert template.matches("system status")
        assert template.matches("server status")
        assert template.matches("application health")
        assert template.matches("is system running?")

        # Should not match
        assert not template.matches("system updates")
        assert not template.matches("version")

    def test_system_updates_pattern(self):
        """Test pattern matching for system updates."""
        template = next(t for t in GENERAL_TEMPLATES if t.id == 'system_updates')

        # Should match
        assert template.matches("recent updates")
        assert template.matches("latest changes")
        assert template.matches("new features")
        assert template.matches("what changed recently?")

        # Should not match
        assert not template.matches("system status")
        assert not template.matches("announcements")

    def test_system_announcements_pattern(self):
        """Test pattern matching for announcements."""
        template = next(t for t in GENERAL_TEMPLATES if t.id == 'system_announcements')

        # Should match
        assert template.matches("announcements")
        assert template.matches("system news")
        assert template.matches("notices")

        # Should not match
        assert not template.matches("system status")
        assert not template.matches("updates")

    def test_system_version_pattern(self):
        """Test pattern matching for version info."""
        template = next(t for t in GENERAL_TEMPLATES if t.id == 'system_version')

        # Should match
        assert template.matches("version")
        assert template.matches("build number")
        assert template.matches("release info")
        assert template.matches("what version?")

        # Should not match
        assert not template.matches("system status")
        assert not template.matches("updates")


class TestNavigationTemplates:
    """Test navigation query templates."""

    def test_navigation_go_to_module_pattern(self):
        """Test pattern matching for module navigation."""
        template = next(t for t in GENERAL_TEMPLATES if t.id == 'navigation_go_to_module')

        # Should match
        assert template.matches("go to dashboard")
        assert template.matches("open communities")
        assert template.matches("navigate to MANA")
        assert template.matches("take me to projects")

        # Should not match
        assert not template.matches("help")
        assert not template.matches("system status")

    def test_navigation_dashboard_pattern(self):
        """Test pattern matching for dashboard navigation."""
        template = next(t for t in GENERAL_TEMPLATES if t.id == 'navigation_dashboard')

        # Should match
        assert template.matches("home")
        assert template.matches("dashboard")
        assert template.matches("main page")
        assert template.matches("go home")

        # Should not match
        assert not template.matches("go to communities")
        assert not template.matches("help")

    def test_navigation_find_page_pattern(self):
        """Test pattern matching for page search."""
        template = next(t for t in GENERAL_TEMPLATES if t.id == 'navigation_find_page')

        # Should match
        assert template.matches("find page reports")
        assert template.matches("search section analytics")
        assert template.matches("where is module settings?")

        # Should not match
        assert not template.matches("dashboard")
        assert not template.matches("help")


class TestMetadataTemplates:
    """Test metadata query templates."""

    def test_metadata_created_by_pattern(self):
        """Test pattern matching for creator info."""
        template = next(t for t in GENERAL_TEMPLATES if t.id == 'metadata_created_by')

        # Should match
        assert template.matches("who created this assessment?")
        assert template.matches("who created community profile?")
        assert template.matches("who created this project?")

        # Should not match
        assert not template.matches("when was this modified?")
        assert not template.matches("audit log")

    def test_metadata_modified_date_pattern(self):
        """Test pattern matching for modification date."""
        template = next(t for t in GENERAL_TEMPLATES if t.id == 'metadata_modified_date')

        # Should match
        assert template.matches("when was this modified?")
        assert template.matches("what time was assessment updated?")
        assert template.matches("when was community changed?")

        # Should not match
        assert not template.matches("who created this?")
        assert not template.matches("audit log")

    def test_metadata_audit_log_pattern(self):
        """Test pattern matching for audit trail."""
        template = next(t for t in GENERAL_TEMPLATES if t.id == 'metadata_audit_log')

        # Should match
        assert template.matches("audit log for assessment")
        assert template.matches("history of community")
        assert template.matches("changes for project")
        assert template.matches("show history for report")

        # Should not match
        assert not template.matches("who created this?")
        assert not template.matches("when was this modified?")


class TestGeneralTemplatePriorities:
    """Test template priority assignments."""

    def test_module_navigation_has_high_priority(self):
        """Test that module navigation has priority 9."""
        template = next(t for t in GENERAL_TEMPLATES if t.id == 'navigation_go_to_module')
        assert template.priority == 9

    def test_how_to_create_has_high_priority(self):
        """Test that create help has priority 9."""
        template = next(t for t in GENERAL_TEMPLATES if t.id == 'help_how_to_create')
        assert template.priority == 9

    def test_how_to_edit_has_high_priority(self):
        """Test that edit help has priority 9."""
        template = next(t for t in GENERAL_TEMPLATES if t.id == 'help_how_to_edit')
        assert template.priority == 9

    def test_all_priorities_in_valid_range(self):
        """Test that all priorities are between 1 and 10."""
        for template in GENERAL_TEMPLATES:
            assert 1 <= template.priority <= 10


class TestGeneralTemplateTags:
    """Test template tagging."""

    def test_help_templates_have_help_tag(self):
        """Test that help templates are tagged 'help'."""
        for template in HELP_DOCUMENTATION_TEMPLATES:
            assert 'help' in template.tags

    def test_system_templates_have_system_tag(self):
        """Test that system templates are tagged 'system'."""
        for template in SYSTEM_STATUS_TEMPLATES:
            assert 'system' in template.tags

    def test_navigation_templates_have_navigation_tag(self):
        """Test that navigation templates are tagged 'navigation'."""
        for template in NAVIGATION_TEMPLATES:
            assert 'navigation' in template.tags

    def test_metadata_templates_have_metadata_tag(self):
        """Test that metadata templates are tagged 'metadata'."""
        for template in METADATA_TEMPLATES:
            assert 'metadata' in template.tags


class TestGeneralTemplateEntityExtraction:
    """Test entity extraction from patterns."""

    def test_how_to_create_extracts_entity(self):
        """Test that create help extracts entity name."""
        template = next(t for t in GENERAL_TEMPLATES if t.id == 'help_how_to_create')
        match = template.matches("how to create assessment")
        assert match is not None
        assert 'entity' in match.groupdict()

    def test_how_to_edit_extracts_entity(self):
        """Test that edit help extracts entity name."""
        template = next(t for t in GENERAL_TEMPLATES if t.id == 'help_how_to_edit')
        match = template.matches("how to edit community profile")
        assert match is not None
        assert 'entity' in match.groupdict()

    def test_navigation_extracts_module(self):
        """Test that navigation extracts module name."""
        template = next(t for t in GENERAL_TEMPLATES if t.id == 'navigation_go_to_module')
        match = template.matches("go to communities")
        assert match is not None
        assert 'module' in match.groupdict()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
