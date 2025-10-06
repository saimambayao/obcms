"""
Tests for Policies Query Templates

Validates 45 policy recommendation query templates across 5 categories:
- Count queries (10 templates)
- List queries (12 templates)
- Evidence-based queries (8 templates)
- Implementation tracking (8 templates)
- Stakeholder queries (7 templates)
"""

import pytest
from common.ai_services.chat.query_templates.policies import (
    POLICIES_TEMPLATES,
    POLICIES_COUNT_TEMPLATES,
    POLICIES_LIST_TEMPLATES,
    POLICIES_EVIDENCE_TEMPLATES,
    POLICIES_IMPLEMENTATION_TEMPLATES,
    POLICIES_STAKEHOLDER_TEMPLATES,
)


class TestPoliciesTemplateStructure:
    """Test template structure and metadata."""

    def test_all_templates_present(self):
        """Verify all 45 templates are included."""
        assert len(POLICIES_TEMPLATES) == 45, f"Expected 45 templates, got {len(POLICIES_TEMPLATES)}"

    def test_template_categories_count(self):
        """Verify template counts by category."""
        assert len(POLICIES_COUNT_TEMPLATES) == 10, "Expected 10 count templates"
        assert len(POLICIES_LIST_TEMPLATES) == 12, "Expected 12 list templates"
        assert len(POLICIES_EVIDENCE_TEMPLATES) == 8, "Expected 8 evidence templates"
        assert len(POLICIES_IMPLEMENTATION_TEMPLATES) == 8, "Expected 8 implementation templates"
        assert len(POLICIES_STAKEHOLDER_TEMPLATES) == 7, "Expected 7 stakeholder templates"

    def test_all_templates_have_unique_ids(self):
        """Verify all templates have unique IDs."""
        template_ids = [t.id for t in POLICIES_TEMPLATES]
        assert len(template_ids) == len(set(template_ids)), "Duplicate template IDs found"

    def test_all_templates_have_category(self):
        """Verify all templates have 'policies' category."""
        for template in POLICIES_TEMPLATES:
            assert template.category == 'policies', f"Template {template.id} has wrong category: {template.category}"

    def test_all_templates_have_patterns(self):
        """Verify all templates have non-empty patterns."""
        for template in POLICIES_TEMPLATES:
            assert template.pattern, f"Template {template.id} has empty pattern"
            assert template.compiled_pattern, f"Template {template.id} pattern failed to compile"

    def test_all_templates_have_examples(self):
        """Verify all templates have example queries."""
        for template in POLICIES_TEMPLATES:
            assert template.examples, f"Template {template.id} has no examples"
            assert len(template.examples) >= 2, f"Template {template.id} has too few examples"

    def test_all_templates_have_priority(self):
        """Verify all templates have priority between 1-10."""
        for template in POLICIES_TEMPLATES:
            assert 1 <= template.priority <= 10, f"Template {template.id} priority {template.priority} out of range"

    def test_all_templates_have_tags(self):
        """Verify all templates have tags."""
        for template in POLICIES_TEMPLATES:
            assert template.tags, f"Template {template.id} has no tags"
            assert 'policies' in template.tags, f"Template {template.id} missing 'policies' tag"


class TestPoliciesCountTemplates:
    """Test count query templates."""

    def test_count_total_policies_pattern(self):
        """Test total policies count pattern."""
        template = next(t for t in POLICIES_COUNT_TEMPLATES if t.id == 'count_total_policies')

        test_queries = [
            "How many policies are there?",
            "Total policies",
            "Count all policy recommendations",
            "Number of policies"
        ]

        for query in test_queries:
            assert template.matches(query.lower()), f"Failed to match: {query}"

    def test_count_policies_by_status_pattern(self):
        """Test policies by status count pattern."""
        template = next(t for t in POLICIES_COUNT_TEMPLATES if t.id == 'count_policies_by_status')

        test_queries = [
            "How many approved policies?",
            "Count draft policies",
            "Total implemented policies",
            "Policies under review"
        ]

        for query in test_queries:
            assert template.matches(query.lower()), f"Failed to match: {query}"

    def test_count_policies_by_sector_pattern(self):
        """Test policies by sector count pattern."""
        template = next(t for t in POLICIES_COUNT_TEMPLATES if t.id == 'count_policies_by_sector')

        test_queries = [
            "How many policies in education sector?",
            "Count policies for health",
            "Total policies in infrastructure sector"
        ]

        for query in test_queries:
            assert template.matches(query.lower()), f"Failed to match: {query}"

    def test_count_policies_by_priority_pattern(self):
        """Test policies by priority count pattern."""
        template = next(t for t in POLICIES_COUNT_TEMPLATES if t.id == 'count_policies_by_priority')

        test_queries = [
            "How many high priority policies?",
            "Count critical priority policies",
            "Total urgent policies"
        ]

        for query in test_queries:
            assert template.matches(query.lower()), f"Failed to match: {query}"

    def test_count_policies_with_evidence_pattern(self):
        """Test policies with evidence count pattern."""
        template = next(t for t in POLICIES_COUNT_TEMPLATES if t.id == 'count_policies_with_evidence')

        test_queries = [
            "How many policies with evidence?",
            "Count policies with supporting data",
            "Total policies with documentation"
        ]

        for query in test_queries:
            assert template.matches(query.lower()), f"Failed to match: {query}"


class TestPoliciesListTemplates:
    """Test list query templates."""

    def test_list_all_policies_pattern(self):
        """Test list all policies pattern."""
        template = next(t for t in POLICIES_LIST_TEMPLATES if t.id == 'list_all_policies')

        test_queries = [
            "Show me policies",
            "List all policy recommendations",
            "Display policies",
            "Get all policies"
        ]

        for query in test_queries:
            assert template.matches(query.lower()), f"Failed to match: {query}"

    def test_list_policies_by_status_pattern(self):
        """Test list policies by status pattern."""
        template = next(t for t in POLICIES_LIST_TEMPLATES if t.id == 'list_policies_by_status')

        test_queries = [
            "Show me approved policies",
            "List draft policies",
            "Display implemented policies",
            "Policies under review"
        ]

        for query in test_queries:
            assert template.matches(query.lower()), f"Failed to match: {query}"

    def test_list_policies_by_sector_pattern(self):
        """Test list policies by sector pattern."""
        template = next(t for t in POLICIES_LIST_TEMPLATES if t.id == 'list_policies_by_sector')

        test_queries = [
            "Show me policies in education sector",
            "List policies for health",
            "Display infrastructure policies"
        ]

        for query in test_queries:
            assert template.matches(query.lower()), f"Failed to match: {query}"

    def test_search_policies_keyword_pattern(self):
        """Test search policies by keyword pattern."""
        template = next(t for t in POLICIES_LIST_TEMPLATES if t.id == 'search_policies_keyword')

        test_queries = [
            "Search for policies about education",
            "Find policies on livelihood",
            "Search policy recommendations related to health"
        ]

        for query in test_queries:
            assert template.matches(query.lower()), f"Failed to match: {query}"

    def test_list_recent_policies_pattern(self):
        """Test list recent policies pattern."""
        template = next(t for t in POLICIES_LIST_TEMPLATES if t.id == 'list_recent_policies')

        test_queries = [
            "Recent policies",
            "Latest policy recommendations",
            "Newly added policies",
            "Show recent policies"
        ]

        for query in test_queries:
            assert template.matches(query.lower()), f"Failed to match: {query}"


class TestPoliciesEvidenceTemplates:
    """Test evidence-based query templates."""

    def test_policies_with_impact_evidence_pattern(self):
        """Test policies with impact evidence pattern."""
        template = next(t for t in POLICIES_EVIDENCE_TEMPLATES if t.id == 'policies_with_impact_evidence')

        test_queries = [
            "Policies with impact evidence",
            "Policy recommendations with outcome data",
            "Policies with impact results"
        ]

        for query in test_queries:
            assert template.matches(query.lower()), f"Failed to match: {query}"

    def test_policies_evidence_based_pattern(self):
        """Test evidence-based policies pattern."""
        template = next(t for t in POLICIES_EVIDENCE_TEMPLATES if t.id == 'policies_evidence_based')

        test_queries = [
            "Evidence-based policies",
            "Evidence based policy recommendations",
            "Show me evidence-based policies"
        ]

        for query in test_queries:
            assert template.matches(query.lower()), f"Failed to match: {query}"

    def test_policies_supporting_data_pattern(self):
        """Test policies with supporting data pattern."""
        template = next(t for t in POLICIES_EVIDENCE_TEMPLATES if t.id == 'policies_supporting_data')

        test_queries = [
            "Policies with supporting data",
            "Policy recommendations with baseline evidence",
            "Policies with research documentation"
        ]

        for query in test_queries:
            assert template.matches(query.lower()), f"Failed to match: {query}"

    def test_policies_assessment_based_pattern(self):
        """Test policies based on assessments pattern."""
        template = next(t for t in POLICIES_EVIDENCE_TEMPLATES if t.id == 'policies_assessment_based')

        test_queries = [
            "Policies based on assessments",
            "Policy recommendations from needs analysis",
            "Policies derived from assessments"
        ]

        for query in test_queries:
            assert template.matches(query.lower()), f"Failed to match: {query}"

    def test_policies_without_evidence_pattern(self):
        """Test policies without evidence pattern."""
        template = next(t for t in POLICIES_EVIDENCE_TEMPLATES if t.id == 'policies_without_evidence')

        test_queries = [
            "Policies without evidence",
            "Policy recommendations lacking supporting data",
            "Policies missing documentation"
        ]

        for query in test_queries:
            assert template.matches(query.lower()), f"Failed to match: {query}"


class TestPoliciesImplementationTemplates:
    """Test implementation tracking templates."""

    def test_policy_implementation_status_pattern(self):
        """Test policy implementation status pattern."""
        template = next(t for t in POLICIES_IMPLEMENTATION_TEMPLATES if t.id == 'policy_implementation_status')

        test_queries = [
            "Policy implementation status",
            "Policies progress tracking",
            "Show me policy implementation status"
        ]

        for query in test_queries:
            assert template.matches(query.lower()), f"Failed to match: {query}"

    def test_policy_implementation_rate_pattern(self):
        """Test policy implementation rate pattern."""
        template = next(t for t in POLICIES_IMPLEMENTATION_TEMPLATES if t.id == 'policy_implementation_rate')

        test_queries = [
            "Policy implementation rate",
            "Policies completion percentage",
            "What is the policy implementation rate?"
        ]

        for query in test_queries:
            assert template.matches(query.lower()), f"Failed to match: {query}"

    def test_policies_implementation_progress_pattern(self):
        """Test policies in implementation pattern."""
        template = next(t for t in POLICIES_IMPLEMENTATION_TEMPLATES if t.id == 'policies_implementation_progress')

        test_queries = [
            "Policies in implementation",
            "Policy recommendations under progress",
            "Show me policies being implemented"
        ]

        for query in test_queries:
            assert template.matches(query.lower()), f"Failed to match: {query}"

    def test_policies_fully_implemented_pattern(self):
        """Test fully implemented policies pattern."""
        template = next(t for t in POLICIES_IMPLEMENTATION_TEMPLATES if t.id == 'policies_fully_implemented')

        test_queries = [
            "Fully implemented policies",
            "Completed policy recommendations",
            "Show me implemented policies"
        ]

        for query in test_queries:
            assert template.matches(query.lower()), f"Failed to match: {query}"

    def test_policies_overdue_implementation_pattern(self):
        """Test overdue implementation pattern."""
        template = next(t for t in POLICIES_IMPLEMENTATION_TEMPLATES if t.id == 'policies_overdue_implementation')

        test_queries = [
            "Overdue policy implementation",
            "Delayed policies",
            "Past due policy implementation"
        ]

        for query in test_queries:
            assert template.matches(query.lower()), f"Failed to match: {query}"


class TestPoliciesStakeholderTemplates:
    """Test stakeholder query templates."""

    def test_policies_by_stakeholder_pattern(self):
        """Test policies by stakeholder pattern."""
        template = next(t for t in POLICIES_STAKEHOLDER_TEMPLATES if t.id == 'policies_by_stakeholder')

        test_queries = [
            "Policies involving MOA stakeholder",
            "Policy recommendations with OOBC",
            "Policies from community stakeholders"
        ]

        for query in test_queries:
            assert template.matches(query.lower()), f"Failed to match: {query}"

    def test_policies_consultation_records_pattern(self):
        """Test policies consultation records pattern."""
        template = next(t for t in POLICIES_STAKEHOLDER_TEMPLATES if t.id == 'policies_consultation_records')

        test_queries = [
            "Policy consultation records",
            "Policies engagement history",
            "Policy consultation summary"
        ]

        for query in test_queries:
            assert template.matches(query.lower()), f"Failed to match: {query}"

    def test_policies_multi_stakeholder_pattern(self):
        """Test multi-stakeholder policies pattern."""
        template = next(t for t in POLICIES_STAKEHOLDER_TEMPLATES if t.id == 'policies_multi_stakeholder')

        test_queries = [
            "Multi-stakeholder policies",
            "Collaborative policy recommendations",
            "Policies with multiple stakeholders"
        ]

        for query in test_queries:
            assert template.matches(query.lower()), f"Failed to match: {query}"

    def test_policies_stakeholder_feedback_pattern(self):
        """Test policies stakeholder feedback pattern."""
        template = next(t for t in POLICIES_STAKEHOLDER_TEMPLATES if t.id == 'policies_stakeholder_feedback')

        test_queries = [
            "Policy stakeholder feedback",
            "Policies with community input",
            "Policy stakeholder comments"
        ]

        for query in test_queries:
            assert template.matches(query.lower()), f"Failed to match: {query}"

    def test_policies_without_stakeholders_pattern(self):
        """Test policies without stakeholders pattern."""
        template = next(t for t in POLICIES_STAKEHOLDER_TEMPLATES if t.id == 'policies_without_stakeholders')

        test_queries = [
            "Policies without stakeholder engagement",
            "Policy recommendations lacking consultation",
            "Policies missing stakeholders"
        ]

        for query in test_queries:
            assert template.matches(query.lower()), f"Failed to match: {query}"


class TestPoliciesQueryGeneration:
    """Test Django ORM query generation."""

    def test_count_queries_have_count_method(self):
        """Verify count queries use .count() method."""
        for template in POLICIES_COUNT_TEMPLATES:
            assert '.count()' in template.query_template, \
                f"Count template {template.id} missing .count() method"

    def test_list_queries_have_ordering(self):
        """Verify list queries use .order_by() method."""
        for template in POLICIES_LIST_TEMPLATES:
            assert 'order_by' in template.query_template, \
                f"List template {template.id} missing ordering"

    def test_list_queries_have_limits(self):
        """Verify list queries have result limits."""
        for template in POLICIES_LIST_TEMPLATES:
            assert '[:' in template.query_template or '.count()' in template.query_template, \
                f"List template {template.id} missing result limit"

    def test_evidence_queries_check_fields(self):
        """Verify evidence queries check appropriate fields."""
        evidence_fields = ['evidence_base', 'impact_indicators', 'supporting_documents', 'related_needs']

        for template in POLICIES_EVIDENCE_TEMPLATES:
            has_evidence_field = any(field in template.query_template for field in evidence_fields)
            assert has_evidence_field, \
                f"Evidence template {template.id} missing evidence field check"

    def test_implementation_queries_check_status(self):
        """Verify implementation queries check status or related fields."""
        implementation_indicators = ['status', 'implementation', 'target_implementation_date']

        for template in POLICIES_IMPLEMENTATION_TEMPLATES:
            has_indicator = any(indicator in template.query_template for indicator in implementation_indicators)
            assert has_indicator, \
                f"Implementation template {template.id} missing implementation indicator"


class TestPoliciesTemplateIntegration:
    """Test template integration and uniqueness."""

    def test_no_overlapping_patterns(self):
        """Test that high-priority templates don't overlap."""
        high_priority_templates = [t for t in POLICIES_TEMPLATES if t.priority >= 8]

        test_queries = [
            "How many approved policies?",
            "Show me policies with evidence",
            "Policy implementation status",
            "Policies by stakeholder"
        ]

        for query in test_queries:
            matching_templates = [t for t in high_priority_templates if t.matches(query.lower())]
            # Some overlap is acceptable, but should be limited
            assert len(matching_templates) <= 3, \
                f"Query '{query}' matched too many high-priority templates: {len(matching_templates)}"

    def test_template_examples_unique(self):
        """Verify example queries are relatively unique."""
        all_examples = []
        for template in POLICIES_TEMPLATES:
            all_examples.extend([ex.lower() for ex in template.examples])

        # Allow some duplication, but not excessive
        unique_count = len(set(all_examples))
        total_count = len(all_examples)
        uniqueness_ratio = unique_count / total_count

        assert uniqueness_ratio >= 0.7, \
            f"Example queries not unique enough: {uniqueness_ratio:.2%} unique"

    def test_required_entities_validation(self):
        """Verify templates with entity placeholders declare required entities."""
        for template in POLICIES_TEMPLATES:
            # Check for entity placeholders like {sector}, {status}, etc.
            placeholders = [
                'sector', 'status', 'priority', 'scope', 'keyword',
                'author', 'stakeholder', 'type'
            ]

            for placeholder in placeholders:
                if f'{{{placeholder}}}' in template.query_template:
                    # Should be in required or optional entities
                    assert placeholder in template.required_entities or \
                           placeholder in template.optional_entities, \
                        f"Template {template.id} uses {{{placeholder}}} but doesn't declare it"

    def test_comprehensive_coverage(self):
        """Verify comprehensive coverage of policy query types."""
        # Check coverage of key query types
        has_count = any('count' in t.tags for t in POLICIES_TEMPLATES)
        has_list = any('list' in t.tags for t in POLICIES_TEMPLATES)
        has_evidence = any('evidence' in t.tags for t in POLICIES_TEMPLATES)
        has_implementation = any('implementation' in t.tags for t in POLICIES_TEMPLATES)
        has_stakeholders = any('stakeholders' in t.tags for t in POLICIES_TEMPLATES)

        assert all([has_count, has_list, has_evidence, has_implementation, has_stakeholders]), \
            "Missing coverage for key policy query types"


# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
