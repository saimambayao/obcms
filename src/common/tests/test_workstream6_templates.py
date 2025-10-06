"""
Tests for Workstream 6: New Query Categories

Tests 120 templates across 4 categories:
- Temporal (30 templates)
- Cross-Domain (40 templates)
- Analytics (30 templates)
- Comparison (20 templates)
"""

import pytest
from common.ai_services.chat.query_templates import get_template_registry
from common.ai_services.chat.query_templates.temporal import (
    TEMPORAL_DATE_RANGE_TEMPLATES,
    TEMPORAL_TREND_TEMPLATES,
    TEMPORAL_HISTORICAL_TEMPLATES,
)
from common.ai_services.chat.query_templates.cross_domain import (
    CROSS_DOMAIN_COMMUNITIES_MANA_TEMPLATES,
    CROSS_DOMAIN_MANA_COORDINATION_TEMPLATES,
    CROSS_DOMAIN_PIPELINE_TEMPLATES,
)
from common.ai_services.chat.query_templates.analytics import (
    ANALYTICS_STATISTICAL_TEMPLATES,
    ANALYTICS_PATTERN_TEMPLATES,
    ANALYTICS_PREDICTIVE_TEMPLATES,
)
from common.ai_services.chat.query_templates.comparison import (
    COMPARISON_LOCATION_TEMPLATES,
    COMPARISON_ETHNICITY_TEMPLATES,
    COMPARISON_METRIC_TEMPLATES,
)


# =============================================================================
# TEMPORAL TEMPLATES TESTS (30 templates)
# =============================================================================

class TestTemporalTemplates:
    """Test temporal query templates."""

    def test_temporal_date_range_count(self):
        """Test date range templates count."""
        assert len(TEMPORAL_DATE_RANGE_TEMPLATES) == 10

    def test_temporal_trend_count(self):
        """Test trend analysis templates count."""
        assert len(TEMPORAL_TREND_TEMPLATES) == 10

    def test_temporal_historical_count(self):
        """Test historical analysis templates count."""
        assert len(TEMPORAL_HISTORICAL_TEMPLATES) == 10

    def test_temporal_category_assignment(self):
        """Test all temporal templates have correct category."""
        for template in TEMPORAL_DATE_RANGE_TEMPLATES:
            assert template.category == 'temporal'
        for template in TEMPORAL_TREND_TEMPLATES:
            assert template.category == 'temporal'
        for template in TEMPORAL_HISTORICAL_TEMPLATES:
            assert template.category == 'temporal'

    def test_temporal_unique_ids(self):
        """Test all temporal templates have unique IDs."""
        all_templates = (
            TEMPORAL_DATE_RANGE_TEMPLATES +
            TEMPORAL_TREND_TEMPLATES +
            TEMPORAL_HISTORICAL_TEMPLATES
        )
        ids = [t.id for t in all_templates]
        assert len(ids) == len(set(ids)), "Duplicate IDs found"

    def test_count_by_date_range_matches(self):
        """Test date range pattern matching."""
        template = TEMPORAL_DATE_RANGE_TEMPLATES[0]
        assert template.matches("Assessments last 30 days")
        assert template.matches("PPAs this quarter")
        assert template.matches("Projects in last 6 months")

    def test_assessment_completion_trends_matches(self):
        """Test trend pattern matching."""
        template = None
        for t in TEMPORAL_TREND_TEMPLATES:
            if t.id == 'assessment_completion_trends':
                template = t
                break
        assert template is not None
        assert template.matches("Assessment trends over time")
        assert template.matches("Assessment completion trends")

    def test_historical_comparison_matches(self):
        """Test historical comparison pattern matching."""
        template = TEMPORAL_HISTORICAL_TEMPLATES[0]
        assert template.matches("2024 vs 2023 comparison")
        assert template.matches("Compare 2025 and 2024")


# =============================================================================
# CROSS-DOMAIN TEMPLATES TESTS (40 templates)
# =============================================================================

class TestCrossDomainTemplates:
    """Test cross-domain query templates."""

    def test_communities_mana_count(self):
        """Test Communities+MANA templates count."""
        assert len(CROSS_DOMAIN_COMMUNITIES_MANA_TEMPLATES) == 15

    def test_mana_coordination_count(self):
        """Test MANA+Coordination templates count."""
        assert len(CROSS_DOMAIN_MANA_COORDINATION_TEMPLATES) == 10

    def test_pipeline_count(self):
        """Test Needs→Policies→PPAs pipeline templates count."""
        assert len(CROSS_DOMAIN_PIPELINE_TEMPLATES) == 15

    def test_cross_domain_category_assignment(self):
        """Test all cross-domain templates have correct category."""
        for template in CROSS_DOMAIN_COMMUNITIES_MANA_TEMPLATES:
            assert template.category == 'cross_domain'
        for template in CROSS_DOMAIN_MANA_COORDINATION_TEMPLATES:
            assert template.category == 'cross_domain'
        for template in CROSS_DOMAIN_PIPELINE_TEMPLATES:
            assert template.category == 'cross_domain'

    def test_cross_domain_unique_ids(self):
        """Test all cross-domain templates have unique IDs."""
        all_templates = (
            CROSS_DOMAIN_COMMUNITIES_MANA_TEMPLATES +
            CROSS_DOMAIN_MANA_COORDINATION_TEMPLATES +
            CROSS_DOMAIN_PIPELINE_TEMPLATES
        )
        ids = [t.id for t in all_templates]
        assert len(ids) == len(set(ids)), "Duplicate IDs found"

    def test_communities_with_assessments_matches(self):
        """Test communities with assessments pattern matching."""
        template = CROSS_DOMAIN_COMMUNITIES_MANA_TEMPLATES[0]
        assert template.matches("Communities with active assessments")
        assert template.matches("Communities having assessments")

    def test_needs_to_ppas_pipeline_matches(self):
        """Test needs to PPAs pipeline pattern matching."""
        template = None
        for t in CROSS_DOMAIN_PIPELINE_TEMPLATES:
            if t.id == 'needs_to_ppas_pipeline':
                template = t
                break
        assert template is not None
        assert template.matches("Needs to PPAs pipeline")
        assert template.matches("Needs to projects addressing them")

    def test_needs_without_ppas_matches(self):
        """Test unaddressed needs pattern matching."""
        template = None
        for t in CROSS_DOMAIN_PIPELINE_TEMPLATES:
            if t.id == 'needs_without_ppas':
                template = t
                break
        assert template is not None
        assert template.matches("Needs without PPAs")
        assert template.matches("Unaddressed needs")

    def test_pipeline_critical_priority(self):
        """Test pipeline templates have high priority."""
        critical_templates = [
            'needs_to_ppas_pipeline',
            'needs_without_ppas',
            'needs_policy_ppa_flow',
            'unfunded_needs_analysis',
        ]
        for template in CROSS_DOMAIN_PIPELINE_TEMPLATES:
            if template.id in critical_templates:
                assert template.priority >= 8, f"{template.id} should have priority >= 8"


# =============================================================================
# ANALYTICS TEMPLATES TESTS (30 templates)
# =============================================================================

class TestAnalyticsTemplates:
    """Test analytics query templates."""

    def test_statistical_count(self):
        """Test statistical templates count."""
        assert len(ANALYTICS_STATISTICAL_TEMPLATES) == 10

    def test_pattern_count(self):
        """Test pattern identification templates count."""
        assert len(ANALYTICS_PATTERN_TEMPLATES) == 10

    def test_predictive_count(self):
        """Test predictive indicators templates count."""
        assert len(ANALYTICS_PREDICTIVE_TEMPLATES) == 10

    def test_analytics_category_assignment(self):
        """Test all analytics templates have correct category."""
        for template in ANALYTICS_STATISTICAL_TEMPLATES:
            assert template.category == 'analytics'
        for template in ANALYTICS_PATTERN_TEMPLATES:
            assert template.category == 'analytics'
        for template in ANALYTICS_PREDICTIVE_TEMPLATES:
            assert template.category == 'analytics'

    def test_analytics_unique_ids(self):
        """Test all analytics templates have unique IDs."""
        all_templates = (
            ANALYTICS_STATISTICAL_TEMPLATES +
            ANALYTICS_PATTERN_TEMPLATES +
            ANALYTICS_PREDICTIVE_TEMPLATES
        )
        ids = [t.id for t in all_templates]
        assert len(ids) == len(set(ids)), "Duplicate IDs found"

    def test_statistical_summary_matches(self):
        """Test statistical summary pattern matching."""
        template = ANALYTICS_STATISTICAL_TEMPLATES[0]
        assert template.matches("Statistical summary")
        assert template.matches("Stats analysis")

    def test_clustering_analysis_matches(self):
        """Test clustering pattern matching."""
        template = ANALYTICS_PATTERN_TEMPLATES[0]
        assert template.matches("Identify clusters")
        assert template.matches("Clustering analysis")

    def test_risk_scoring_matches(self):
        """Test risk scoring pattern matching."""
        template = ANALYTICS_PREDICTIVE_TEMPLATES[0]
        assert template.matches("Risk score by project")
        assert template.matches("Risk assessment")


# =============================================================================
# COMPARISON TEMPLATES TESTS (20 templates)
# =============================================================================

class TestComparisonTemplates:
    """Test comparison query templates."""

    def test_location_comparison_count(self):
        """Test location comparison templates count."""
        assert len(COMPARISON_LOCATION_TEMPLATES) == 8

    def test_ethnicity_comparison_count(self):
        """Test ethnicity comparison templates count."""
        assert len(COMPARISON_ETHNICITY_TEMPLATES) == 6

    def test_metric_comparison_count(self):
        """Test metric comparison templates count."""
        assert len(COMPARISON_METRIC_TEMPLATES) == 6

    def test_comparison_category_assignment(self):
        """Test all comparison templates have correct category."""
        for template in COMPARISON_LOCATION_TEMPLATES:
            assert template.category == 'comparison'
        for template in COMPARISON_ETHNICITY_TEMPLATES:
            assert template.category == 'comparison'
        for template in COMPARISON_METRIC_TEMPLATES:
            assert template.category == 'comparison'

    def test_comparison_unique_ids(self):
        """Test all comparison templates have unique IDs."""
        all_templates = (
            COMPARISON_LOCATION_TEMPLATES +
            COMPARISON_ETHNICITY_TEMPLATES +
            COMPARISON_METRIC_TEMPLATES
        )
        ids = [t.id for t in all_templates]
        assert len(ids) == len(set(ids)), "Duplicate IDs found"

    def test_region_vs_region_matches(self):
        """Test region comparison pattern matching."""
        template = COMPARISON_LOCATION_TEMPLATES[0]
        assert template.matches("Compare Region IX vs Region X")
        assert template.matches("Region IX versus Region XII")

    def test_ethnicity_demographics_matches(self):
        """Test ethnicity demographics comparison pattern matching."""
        template = COMPARISON_ETHNICITY_TEMPLATES[0]
        assert template.matches("Compare ethnic groups demographics")
        assert template.matches("Ethnicity demographic comparison")

    def test_budget_efficiency_matches(self):
        """Test budget efficiency comparison pattern matching."""
        template = COMPARISON_METRIC_TEMPLATES[0]
        assert template.matches("Budget efficiency comparison")
        assert template.matches("Compare cost efficiency")


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestWorkstream6Integration:
    """Integration tests for all Workstream 6 templates."""

    def test_all_templates_registered(self):
        """Test all 120 templates are registered."""
        registry = get_template_registry()

        # Check temporal templates
        temporal_templates = registry.get_templates_by_category('temporal')
        assert len(temporal_templates) >= 30, "Should have at least 30 temporal templates"

        # Check cross-domain templates
        cross_domain_templates = registry.get_templates_by_category('cross_domain')
        assert len(cross_domain_templates) >= 40, "Should have at least 40 cross-domain templates"

        # Check analytics templates
        analytics_templates = registry.get_templates_by_category('analytics')
        assert len(analytics_templates) >= 30, "Should have at least 30 analytics templates"

        # Check comparison templates
        comparison_templates = registry.get_templates_by_category('comparison')
        assert len(comparison_templates) >= 20, "Should have at least 20 comparison templates"

    def test_total_template_count(self):
        """Test total template count includes all categories."""
        registry = get_template_registry()
        stats = registry.get_stats()

        # Workstream 6 adds 120 templates minimum
        assert stats['total_templates'] >= 120, "Should have at least 120 templates from Workstream 6"

    def test_no_duplicate_ids_across_categories(self):
        """Test no duplicate IDs across all categories."""
        registry = get_template_registry()
        all_templates = registry.get_all_templates()

        ids = [t.id for t in all_templates]
        assert len(ids) == len(set(ids)), "Duplicate IDs found across categories"

    def test_new_categories_available(self):
        """Test new categories are available."""
        registry = get_template_registry()
        categories = registry.get_categories()

        assert 'temporal' in categories
        assert 'cross_domain' in categories
        assert 'analytics' in categories
        assert 'comparison' in categories

    def test_all_templates_have_examples(self):
        """Test all templates have example queries."""
        registry = get_template_registry()

        for category in ['temporal', 'cross_domain', 'analytics', 'comparison']:
            templates = registry.get_templates_by_category(category)
            for template in templates:
                assert len(template.examples) > 0, f"Template {template.id} has no examples"

    def test_all_templates_have_descriptions(self):
        """Test all templates have descriptions."""
        registry = get_template_registry()

        for category in ['temporal', 'cross_domain', 'analytics', 'comparison']:
            templates = registry.get_templates_by_category(category)
            for template in templates:
                assert template.description, f"Template {template.id} has no description"

    def test_all_templates_have_tags(self):
        """Test all templates have tags."""
        registry = get_template_registry()

        for category in ['temporal', 'cross_domain', 'analytics', 'comparison']:
            templates = registry.get_templates_by_category(category)
            for template in templates:
                assert len(template.tags) > 0, f"Template {template.id} has no tags"

    def test_temporal_pattern_matching(self):
        """Test temporal queries match correctly."""
        registry = get_template_registry()

        test_queries = [
            "Assessments last 30 days",
            "Assessment trends over time",
            "2024 vs 2023 comparison",
        ]

        for query in test_queries:
            matches = registry.search_templates(query, category='temporal')
            assert len(matches) > 0, f"No matches found for: {query}"

    def test_cross_domain_pattern_matching(self):
        """Test cross-domain queries match correctly."""
        registry = get_template_registry()

        test_queries = [
            "Communities with assessments",
            "Needs without PPAs",
            "Partnerships supporting assessments",
        ]

        for query in test_queries:
            matches = registry.search_templates(query, category='cross_domain')
            assert len(matches) > 0, f"No matches found for: {query}"

    def test_analytics_pattern_matching(self):
        """Test analytics queries match correctly."""
        registry = get_template_registry()

        test_queries = [
            "Statistical summary",
            "Clustering analysis",
            "Risk assessment",
        ]

        for query in test_queries:
            matches = registry.search_templates(query, category='analytics')
            assert len(matches) > 0, f"No matches found for: {query}"

    def test_comparison_pattern_matching(self):
        """Test comparison queries match correctly."""
        registry = get_template_registry()

        test_queries = [
            "Region IX vs Region X",
            "Compare ethnic groups",
            "Budget efficiency comparison",
        ]

        for query in test_queries:
            matches = registry.search_templates(query, category='comparison')
            assert len(matches) > 0, f"No matches found for: {query}"


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
