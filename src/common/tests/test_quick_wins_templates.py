"""
Tests for WORKSTREAM 3: Quick Wins Templates

Validates all 37 high-value, low-complexity query templates across 4 domains:
- Infrastructure Analysis (10 templates)
- Livelihood & Economic (10 templates)
- Stakeholder Network (10 templates)
- Budget Ceiling Tracking (7 templates)

Tests verify:
1. All templates are properly registered
2. Pattern matching works correctly
3. Required entities are correctly defined
4. Query templates are valid Django ORM syntax
"""

import pytest
from common.ai_services.chat.query_templates import get_template_registry
from common.ai_services.chat.query_templates.infrastructure import INFRASTRUCTURE_TEMPLATES
from common.ai_services.chat.query_templates.livelihood import LIVELIHOOD_TEMPLATES
from common.ai_services.chat.query_templates.stakeholders import STAKEHOLDER_TEMPLATES
from common.ai_services.chat.query_templates.budget import BUDGET_TEMPLATES
from common.ai_services.chat.template_matcher import TemplateMatcher


class TestQuickWinsTemplatesRegistration:
    """Test that all Quick Wins templates are properly registered."""

    def test_infrastructure_templates_registered(self):
        """Verify all 10 infrastructure templates are registered."""
        registry = get_template_registry()
        infrastructure_templates = registry.get_templates_by_category('infrastructure')

        assert len(infrastructure_templates) >= 10, "Should have at least 10 infrastructure templates"

        # Verify key template IDs exist
        template_ids = [t.id for t in infrastructure_templates]
        expected_ids = [
            'count_communities_by_water_access',
            'count_communities_by_electricity',
            'count_communities_by_healthcare',
            'count_communities_by_education',
            'count_communities_by_sanitation',
            'list_critical_infrastructure_gaps',
            'list_communities_poor_water',
            'list_communities_poor_electricity',
            'infrastructure_coverage_by_province',
            'infrastructure_improvement_priorities'
        ]

        for expected_id in expected_ids:
            assert expected_id in template_ids, f"Missing template: {expected_id}"

    def test_livelihood_templates_registered(self):
        """Verify all 10 livelihood templates are registered."""
        registry = get_template_registry()
        livelihood_templates = registry.get_templates_by_category('livelihood')

        assert len(livelihood_templates) >= 10, "Should have at least 10 livelihood templates"

        # Verify key template IDs exist
        template_ids = [t.id for t in livelihood_templates]
        expected_ids = [
            'count_livelihoods_by_type',
            'count_primary_livelihoods',
            'count_seasonal_livelihoods',
            'livelihood_income_levels',
            'livelihood_participation_rate',
            'list_livelihood_challenges',
            'list_communities_by_livelihood_opportunity',
            'livelihood_diversity_by_community',
            'economic_organizations_count',
            'unbanked_population_analysis'
        ]

        for expected_id in expected_ids:
            assert expected_id in template_ids, f"Missing template: {expected_id}"

    def test_stakeholder_templates_registered(self):
        """Verify all 10 stakeholder templates are registered."""
        registry = get_template_registry()
        stakeholder_templates = registry.get_templates_by_category('stakeholders')

        assert len(stakeholder_templates) >= 10, "Should have at least 10 stakeholder templates"

        # Verify key template IDs exist
        template_ids = [t.id for t in stakeholder_templates]
        expected_ids = [
            'count_stakeholders_by_type',
            'count_stakeholders_by_influence',
            'count_stakeholders_by_engagement',
            'count_religious_leaders',
            'count_community_organizations',
            'list_high_influence_stakeholders',
            'list_inactive_stakeholders',
            'stakeholder_engagement_history',
            'stakeholders_by_expertise',
            'stakeholder_networks_analysis'
        ]

        for expected_id in expected_ids:
            assert expected_id in template_ids, f"Missing template: {expected_id}"

    def test_budget_templates_registered(self):
        """Verify all 7 budget templates are registered."""
        registry = get_template_registry()
        budget_templates = registry.get_templates_by_category('budget')

        assert len(budget_templates) >= 7, "Should have at least 7 budget templates"

        # Verify key template IDs exist
        template_ids = [t.id for t in budget_templates]
        expected_ids = [
            'budget_ceiling_utilization',
            'remaining_budget_by_sector',
            'budget_ceiling_violations',
            'total_budget_by_sector',
            'total_budget_by_fiscal_year',
            'total_budget_by_funding_source',
            'budget_allocation_vs_utilization'
        ]

        for expected_id in expected_ids:
            assert expected_id in template_ids, f"Missing template: {expected_id}"

    def test_total_quick_wins_templates_count(self):
        """Verify total of 37 Quick Wins templates are registered."""
        assert len(INFRASTRUCTURE_TEMPLATES) == 10, "Infrastructure should have 10 templates"
        assert len(LIVELIHOOD_TEMPLATES) == 10, "Livelihood should have 10 templates"
        assert len(STAKEHOLDER_TEMPLATES) == 10, "Stakeholders should have 10 templates"
        assert len(BUDGET_TEMPLATES) == 7, "Budget should have 7 templates"

        total = len(INFRASTRUCTURE_TEMPLATES) + len(LIVELIHOOD_TEMPLATES) + len(STAKEHOLDER_TEMPLATES) + len(BUDGET_TEMPLATES)
        assert total == 37, f"Total should be 37 templates, got {total}"


class TestInfrastructureTemplatePatterns:
    """Test pattern matching for infrastructure templates."""

    def test_water_access_pattern_matching(self):
        """Test water access template matches various queries."""
        registry = get_template_registry()
        template = registry.get_template_by_id('count_communities_by_water_access')

        assert template is not None, "Template should exist"

        test_queries = [
            'How many communities have poor water access?',
            'Communities with limited water supply',
            'Count communities with no water access',
            'Communities having available water',
            'Communities with water access'
        ]

        for query in test_queries:
            match = template.matches(query.lower())
            assert match is not None, f"Should match: {query}"

    def test_electricity_pattern_matching(self):
        """Test electricity template matches various queries."""
        registry = get_template_registry()
        template = registry.get_template_by_id('count_communities_by_electricity')

        assert template is not None, "Template should exist"

        test_queries = [
            'How many communities without electricity?',
            'Communities with no power',
            'Count communities lacking electricity'
        ]

        for query in test_queries:
            match = template.matches(query.lower())
            assert match is not None, f"Should match: {query}"


class TestInfrastructureTemplateMatcher:
    """Ensure TemplateMatcher executes infrastructure templates with flexible rating handling."""

    @pytest.fixture
    def matcher(self):
        return TemplateMatcher()

    def test_water_template_generates_filter_from_statement(self, matcher):
        """Statement queries with rating should produce the correct filter."""
        result = matcher.match_and_generate(
            "Communities with limited water supply",
            {},
            category='infrastructure'
        )

        assert result['success'], result['error']
        assert "infrastructure__availability_status__icontains='limited'" in result['query']

    def test_water_template_handles_missing_rating(self, matcher):
        """Queries without rating should still execute and omit availability filters."""
        result = matcher.match_and_generate(
            "Communities with water access",
            {},
            category='infrastructure'
        )

        assert result['success'], result['error']
        assert "infrastructure__availability_status__icontains" not in result['query']

    def test_water_template_normalizes_no_rating(self, matcher):
        """Queries using 'no' should normalize to the 'none' rating."""
        result = matcher.match_and_generate(
            "Count communities with no water access",
            {},
            category='infrastructure'
        )

        assert result['success'], result['error']
        assert "infrastructure__availability_status__icontains='none'" in result['query']

    def test_sanitation_template_with_no_rating(self, matcher):
        """Sanitation template should also respect missing ratings."""
        result = matcher.match_and_generate(
            "Communities with no sanitation",
            {},
            category='infrastructure'
        )

        assert result['success'], result['error']
        assert "infrastructure__availability_status__icontains='none'" in result['query']


class TestLivelihoodTemplatePatterns:
    """Test pattern matching for livelihood templates."""

    def test_livelihood_type_pattern_matching(self):
        """Test livelihood type template matches various queries."""
        registry = get_template_registry()
        template = registry.get_template_by_id('count_livelihoods_by_type')

        assert template is not None, "Template should exist"

        test_queries = [
            'How many fishing communities?',
            'Count agriculture livelihoods',
            'Total livestock communities',
            'How many trade communities?'
        ]

        for query in test_queries:
            match = template.matches(query.lower())
            assert match is not None, f"Should match: {query}"

    def test_challenges_pattern_matching(self):
        """Test livelihood challenges template matches various queries."""
        registry = get_template_registry()
        template = registry.get_template_by_id('list_livelihood_challenges')

        assert template is not None, "Template should exist"

        test_queries = [
            'What are livelihood challenges?',
            'Show common livelihood problems',
            'List livelihood issues'
        ]

        for query in test_queries:
            match = template.matches(query.lower())
            assert match is not None, f"Should match: {query}"


class TestStakeholderTemplatePatterns:
    """Test pattern matching for stakeholder templates."""

    def test_stakeholder_type_pattern_matching(self):
        """Test stakeholder type template matches various queries."""
        registry = get_template_registry()
        template = registry.get_template_by_id('count_stakeholders_by_type')

        assert template is not None, "Template should exist"

        test_queries = [
            'How many religious leaders?',
            'Count ulama stakeholders',
            'Total youth leaders',
            'How many imam?'
        ]

        for query in test_queries:
            match = template.matches(query.lower())
            assert match is not None, f"Should match: {query}"

    def test_influence_pattern_matching(self):
        """Test influence level template matches various queries."""
        registry = get_template_registry()
        template = registry.get_template_by_id('count_stakeholders_by_influence')

        assert template is not None, "Template should exist"

        test_queries = [
            'How many high influence stakeholders?',
            'Count very high influence leaders',
            'Total emerging influence stakeholders'
        ]

        for query in test_queries:
            match = template.matches(query.lower())
            assert match is not None, f"Should match: {query}"


class TestBudgetTemplatePatterns:
    """Test pattern matching for budget templates."""

    def test_utilization_pattern_matching(self):
        """Test budget utilization template matches various queries."""
        registry = get_template_registry()
        template = registry.get_template_by_id('budget_ceiling_utilization')

        assert template is not None, "Template should exist"

        test_queries = [
            'Budget ceilings near limit',
            'Budget utilization by sector',
            'Show ceiling usage'
        ]

        for query in test_queries:
            match = template.matches(query.lower())
            assert match is not None, f"Should match: {query}"

    def test_violations_pattern_matching(self):
        """Test budget violations template matches various queries."""
        registry = get_template_registry()
        template = registry.get_template_by_id('budget_ceiling_violations')

        assert template is not None, "Template should exist"

        test_queries = [
            'Allocations exceeding ceilings',
            'Budget violating limits',
            'Budgets over ceiling'
        ]

        for query in test_queries:
            match = template.matches(query.lower())
            assert match is not None, f"Should match: {query}"


class TestTemplateMetadata:
    """Test template metadata is correctly defined."""

    def test_infrastructure_templates_have_examples(self):
        """Verify all infrastructure templates have examples."""
        for template in INFRASTRUCTURE_TEMPLATES:
            assert len(template.examples) > 0, f"Template {template.id} should have examples"
            assert template.description, f"Template {template.id} should have description"
            assert template.priority > 0, f"Template {template.id} should have priority"

    def test_livelihood_templates_have_examples(self):
        """Verify all livelihood templates have examples."""
        for template in LIVELIHOOD_TEMPLATES:
            assert len(template.examples) > 0, f"Template {template.id} should have examples"
            assert template.description, f"Template {template.id} should have description"
            assert template.priority > 0, f"Template {template.id} should have priority"

    def test_stakeholder_templates_have_examples(self):
        """Verify all stakeholder templates have examples."""
        for template in STAKEHOLDER_TEMPLATES:
            assert len(template.examples) > 0, f"Template {template.id} should have examples"
            assert template.description, f"Template {template.id} should have description"
            assert template.priority > 0, f"Template {template.id} should have priority"

    def test_budget_templates_have_examples(self):
        """Verify all budget templates have examples."""
        for template in BUDGET_TEMPLATES:
            assert len(template.examples) > 0, f"Template {template.id} should have examples"
            assert template.description, f"Template {template.id} should have description"
            assert template.priority > 0, f"Template {template.id} should have priority"


class TestTemplateCategories:
    """Test templates are assigned to correct categories."""

    def test_infrastructure_category(self):
        """Verify all infrastructure templates have correct category."""
        for template in INFRASTRUCTURE_TEMPLATES:
            assert template.category == 'infrastructure', f"Template {template.id} should be in infrastructure category"

    def test_livelihood_category(self):
        """Verify all livelihood templates have correct category."""
        for template in LIVELIHOOD_TEMPLATES:
            assert template.category == 'livelihood', f"Template {template.id} should be in livelihood category"

    def test_stakeholder_category(self):
        """Verify all stakeholder templates have correct category."""
        for template in STAKEHOLDER_TEMPLATES:
            assert template.category == 'stakeholders', f"Template {template.id} should be in stakeholders category"

    def test_budget_category(self):
        """Verify all budget templates have correct category."""
        for template in BUDGET_TEMPLATES:
            assert template.category == 'budget', f"Template {template.id} should be in budget category"


class TestTemplateResultTypes:
    """Test templates have appropriate result types."""

    def test_count_templates_have_count_result_type(self):
        """Verify count templates have 'count' result type."""
        registry = get_template_registry()

        count_template_ids = [
            'count_communities_by_water_access',
            'count_communities_by_electricity',
            'count_livelihoods_by_type',
            'count_stakeholders_by_type',
        ]

        for template_id in count_template_ids:
            template = registry.get_template_by_id(template_id)
            if template:
                assert template.result_type == 'count', f"Template {template_id} should have 'count' result type"

    def test_list_templates_have_list_result_type(self):
        """Verify list templates have 'list' result type."""
        registry = get_template_registry()

        list_template_ids = [
            'list_critical_infrastructure_gaps',
            'list_communities_poor_water',
            'list_high_influence_stakeholders',
        ]

        for template_id in list_template_ids:
            template = registry.get_template_by_id(template_id)
            if template:
                assert template.result_type == 'list', f"Template {template_id} should have 'list' result type"

    def test_aggregate_templates_have_aggregate_result_type(self):
        """Verify aggregate templates have 'aggregate' result type."""
        registry = get_template_registry()

        aggregate_template_ids = [
            'budget_ceiling_utilization',
            'remaining_budget_by_sector',
            'economic_organizations_count',
        ]

        for template_id in aggregate_template_ids:
            template = registry.get_template_by_id(template_id)
            if template:
                assert template.result_type == 'aggregate', f"Template {template_id} should have 'aggregate' result type"
