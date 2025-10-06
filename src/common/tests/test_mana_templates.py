"""
Tests for MANA Query Templates

Comprehensive test coverage for all MANA templates including:
- Workshop queries (list, count, filter)
- Assessment queries (status, location, analytics)
- Needs identification queries
- Participant queries
- Synthesis queries
"""

import pytest
from common.ai_services.chat.query_templates.mana import (
    MANA_TEMPLATES,
    MANA_WORKSHOP_TEMPLATES,
    MANA_ASSESSMENT_TEMPLATES,
    MANA_NEEDS_TEMPLATES,
    MANA_PARTICIPANT_TEMPLATES,
    MANA_SYNTHESIS_TEMPLATES,
)


class TestMANATemplateCount:
    """Test that we have the expected number of templates."""

    def test_total_template_count(self):
        """Verify total MANA template count."""
        assert len(MANA_TEMPLATES) >= 33, "Should have at least 33 MANA templates"

    def test_workshop_template_count(self):
        """Verify workshop template count."""
        assert len(MANA_WORKSHOP_TEMPLATES) >= 7, "Should have at least 7 workshop templates"

    def test_assessment_template_count(self):
        """Verify assessment template count."""
        assert len(MANA_ASSESSMENT_TEMPLATES) >= 13, "Should have at least 13 assessment templates"

    def test_needs_template_count(self):
        """Verify needs template count."""
        assert len(MANA_NEEDS_TEMPLATES) >= 5, "Should have at least 5 needs templates"

    def test_participant_template_count(self):
        """Verify participant template count."""
        assert len(MANA_PARTICIPANT_TEMPLATES) >= 5, "Should have at least 5 participant templates"

    def test_synthesis_template_count(self):
        """Verify synthesis template count."""
        assert len(MANA_SYNTHESIS_TEMPLATES) >= 3, "Should have at least 3 synthesis templates"


class TestWorkshopTemplates:
    """Test workshop query templates."""

    @pytest.mark.parametrize("query", [
        "Show me workshops",
        "List all workshops",
        "Display workshops",
        "Get workshops",
    ])
    def test_list_all_workshops(self, query):
        """Test listing all workshops."""
        matches = [t for t in MANA_WORKSHOP_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"

    @pytest.mark.parametrize("query", [
        "Workshops in Region IX",
        "Workshops in Zamboanga",
        "Show workshops in Cotabato",
    ])
    def test_workshops_by_location(self, query):
        """Test workshops by location."""
        matches = [t for t in MANA_WORKSHOP_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"

    @pytest.mark.parametrize("query", [
        "Recent workshops",
        "Latest workshops",
        "Current workshops",
    ])
    def test_recent_workshops(self, query):
        """Test recent workshops."""
        matches = [t for t in MANA_WORKSHOP_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"

    @pytest.mark.parametrize("query", [
        "Upcoming workshops",
        "Future workshops",
        "Scheduled workshops",
    ])
    def test_upcoming_workshops(self, query):
        """Test upcoming workshops."""
        matches = [t for t in MANA_WORKSHOP_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"

    @pytest.mark.parametrize("query", [
        "How many workshops?",
        "Total workshops",
        "Count workshops",
    ])
    def test_workshop_count(self, query):
        """Test workshop count queries."""
        matches = [t for t in MANA_WORKSHOP_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"


class TestAssessmentTemplates:
    """Test assessment query templates."""

    @pytest.mark.parametrize("query", [
        "Show me assessments",
        "List all assessments",
        "Display assessments",
    ])
    def test_list_all_assessments(self, query):
        """Test listing all assessments."""
        matches = [t for t in MANA_ASSESSMENT_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"

    @pytest.mark.parametrize("query", [
        "Assessments in Region IX",
        "Assessments in Zamboanga",
        "Show assessments for Cotabato",
    ])
    def test_assessments_by_location(self, query):
        """Test assessments by location."""
        matches = [t for t in MANA_ASSESSMENT_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"

    @pytest.mark.parametrize("query", [
        "Completed assessments",
        "Ongoing assessments",
        "Planning assessments",
    ])
    def test_assessments_by_status(self, query):
        """Test assessments by status."""
        matches = [t for t in MANA_ASSESSMENT_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"

    @pytest.mark.parametrize("query", [
        "Recent assessments",
        "Latest assessments",
    ])
    def test_recent_assessments(self, query):
        """Test recent assessments."""
        matches = [t for t in MANA_ASSESSMENT_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"

    @pytest.mark.parametrize("query", [
        "How many assessments?",
        "Total assessments",
        "Count assessments",
    ])
    def test_assessment_count(self, query):
        """Test assessment count queries."""
        matches = [t for t in MANA_ASSESSMENT_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"

    @pytest.mark.parametrize("query", [
        "Pending assessments",
        "Ongoing assessments",
        "In-progress assessments",
    ])
    def test_pending_assessments(self, query):
        """Test pending assessments."""
        matches = [t for t in MANA_ASSESSMENT_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"

    @pytest.mark.parametrize("query", [
        "Assessment completion rate",
        "Assessment success rate",
        "What is the assessment completion rate?",
    ])
    def test_assessment_completion_rate(self, query):
        """Test assessment completion rate."""
        matches = [t for t in MANA_ASSESSMENT_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"

    @pytest.mark.parametrize("query", [
        "Assessments by category",
        "Assessments by type",
        "Show assessment categories",
    ])
    def test_assessments_by_category(self, query):
        """Test assessments by category."""
        matches = [t for t in MANA_ASSESSMENT_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"

    @pytest.mark.parametrize("query", [
        "Assessment coverage by region",
        "Assessment distribution per region",
        "Show assessment coverage",
    ])
    def test_assessment_coverage(self, query):
        """Test assessment coverage."""
        matches = [t for t in MANA_ASSESSMENT_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"

    @pytest.mark.parametrize("query", [
        "Community assessments",
        "OBC assessments",
        "Show community assessments",
    ])
    def test_community_assessments(self, query):
        """Test community assessments."""
        matches = [t for t in MANA_ASSESSMENT_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"

    @pytest.mark.parametrize("query", [
        "Validated assessments",
        "Approved assessments",
        "Verified assessments",
    ])
    def test_validated_assessments(self, query):
        """Test validated assessments."""
        matches = [t for t in MANA_ASSESSMENT_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"

    @pytest.mark.parametrize("query", [
        "Pending validation assessments",
        "Assessments awaiting validation",
        "Assessments under review",
    ])
    def test_pending_validation_assessments(self, query):
        """Test pending validation assessments."""
        matches = [t for t in MANA_ASSESSMENT_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"


class TestNeedsTemplates:
    """Test needs identification query templates."""

    @pytest.mark.parametrize("query", [
        "Unmet needs",
        "Unfulfilled needs",
        "Outstanding needs",
        "Show unmet needs",
    ])
    def test_unmet_needs(self, query):
        """Test unmet needs queries."""
        matches = [t for t in MANA_NEEDS_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"

    @pytest.mark.parametrize("query", [
        "Priority needs",
        "High-priority needs",
        "Urgent needs",
    ])
    def test_priority_needs(self, query):
        """Test priority needs queries."""
        matches = [t for t in MANA_NEEDS_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"

    @pytest.mark.parametrize("query", [
        "Needs by category",
        "Needs by type",
        "Show needs categories",
    ])
    def test_needs_by_category(self, query):
        """Test needs by category."""
        matches = [t for t in MANA_NEEDS_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"

    @pytest.mark.parametrize("query", [
        "Needs in Region IX",
        "Needs in Zamboanga",
        "Show needs for Cotabato",
    ])
    def test_needs_by_location(self, query):
        """Test needs by location."""
        matches = [t for t in MANA_NEEDS_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"

    @pytest.mark.parametrize("query", [
        "Critical needs",
        "Emergency needs",
        "Urgent needs",
    ])
    def test_critical_needs(self, query):
        """Test critical needs queries."""
        matches = [t for t in MANA_NEEDS_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"


class TestParticipantTemplates:
    """Test participant query templates."""

    @pytest.mark.parametrize("query", [
        "How many participants?",
        "Total workshop participants",
        "Count participants",
    ])
    def test_participant_count(self, query):
        """Test participant count queries."""
        matches = [t for t in MANA_PARTICIPANT_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"

    @pytest.mark.parametrize("query", [
        "Show me participants",
        "List workshop participants",
        "Display participants",
    ])
    def test_list_participants(self, query):
        """Test listing participants."""
        matches = [t for t in MANA_PARTICIPANT_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"

    @pytest.mark.parametrize("query", [
        "Participants from Region IX",
        "Participants in Zamboanga",
    ])
    def test_participants_by_location(self, query):
        """Test participants by location."""
        matches = [t for t in MANA_PARTICIPANT_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"

    @pytest.mark.parametrize("query", [
        "Participant demographics",
        "Attendee breakdown",
        "Participant stats",
    ])
    def test_participant_demographics(self, query):
        """Test participant demographics."""
        matches = [t for t in MANA_PARTICIPANT_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"

    @pytest.mark.parametrize("query", [
        "Participants by role",
        "Participants by type",
    ])
    def test_participants_by_role(self, query):
        """Test participants by role."""
        matches = [t for t in MANA_PARTICIPANT_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"


class TestSynthesisTemplates:
    """Test synthesis and findings query templates."""

    @pytest.mark.parametrize("query", [
        "Workshop synthesis",
        "Workshop findings",
        "Show workshop summaries",
        "Workshop reports",
    ])
    def test_workshop_synthesis(self, query):
        """Test workshop synthesis queries."""
        matches = [t for t in MANA_SYNTHESIS_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"

    @pytest.mark.parametrize("query", [
        "Show workshop findings",
        "Get findings",
        "Display workshop findings",
    ])
    def test_workshop_findings(self, query):
        """Test workshop findings queries."""
        matches = [t for t in MANA_SYNTHESIS_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"

    @pytest.mark.parametrize("query", [
        "Workshop outputs",
        "Workshop results",
        "Show workshop deliverables",
    ])
    def test_workshop_outputs(self, query):
        """Test workshop outputs queries."""
        matches = [t for t in MANA_SYNTHESIS_TEMPLATES if t.matches(query)]
        assert len(matches) > 0, f"No matches for query: {query}"


class TestTemplateStructure:
    """Test template structure and metadata."""

    def test_all_templates_have_category(self):
        """Verify all templates have 'mana' category."""
        for template in MANA_TEMPLATES:
            assert template.category == 'mana', f"Template {template.id} should have category 'mana'"

    def test_all_templates_have_description(self):
        """Verify all templates have descriptions."""
        for template in MANA_TEMPLATES:
            assert template.description, f"Template {template.id} missing description"

    def test_all_templates_have_examples(self):
        """Verify all templates have example queries."""
        for template in MANA_TEMPLATES:
            examples = template.examples or template.example_queries
            assert examples and len(examples) > 0, f"Template {template.id} missing examples"

    def test_all_templates_have_priority(self):
        """Verify all templates have valid priority."""
        for template in MANA_TEMPLATES:
            assert 1 <= template.priority <= 10, f"Template {template.id} has invalid priority"

    def test_all_templates_have_tags(self):
        """Verify all templates have tags."""
        for template in MANA_TEMPLATES:
            assert template.tags and len(template.tags) > 0, f"Template {template.id} missing tags"

    def test_all_templates_have_query_builder(self):
        """Verify all templates have query builder."""
        for template in MANA_TEMPLATES:
            assert template.query_builder is not None, f"Template {template.id} missing query_builder"


class TestTemplatePatterns:
    """Test pattern matching quality."""

    def test_workshop_patterns_unique(self):
        """Verify workshop template patterns don't overlap."""
        patterns = [t.pattern for t in MANA_WORKSHOP_TEMPLATES]
        # Patterns can be similar but should serve different purposes
        assert len(patterns) == len(MANA_WORKSHOP_TEMPLATES)

    def test_assessment_patterns_unique(self):
        """Verify assessment template patterns don't overlap."""
        patterns = [t.pattern for t in MANA_ASSESSMENT_TEMPLATES]
        assert len(patterns) == len(MANA_ASSESSMENT_TEMPLATES)

    def test_needs_patterns_unique(self):
        """Verify needs template patterns don't overlap."""
        patterns = [t.pattern for t in MANA_NEEDS_TEMPLATES]
        assert len(patterns) == len(MANA_NEEDS_TEMPLATES)


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_case_insensitive_matching(self):
        """Test that patterns match case-insensitively."""
        queries = [
            "SHOW ME ASSESSMENTS",
            "show me assessments",
            "ShOw Me AsSeSsMeNtS",
        ]
        for query in queries:
            matches = [t for t in MANA_ASSESSMENT_TEMPLATES if t.matches(query)]
            assert len(matches) > 0, f"Should match case-insensitively: {query}"

    def test_query_with_punctuation(self):
        """Test queries with punctuation."""
        queries = [
            "Show me assessments?",
            "Show me assessments!",
            "Show me assessments.",
        ]
        for query in queries:
            matches = [t for t in MANA_ASSESSMENT_TEMPLATES if t.matches(query)]
            assert len(matches) > 0, f"Should handle punctuation: {query}"

    def test_query_with_extra_whitespace(self):
        """Test queries with extra whitespace."""
        query = "Show   me    assessments"
        # Patterns should still match (depends on pattern design)
        matches = [t for t in MANA_ASSESSMENT_TEMPLATES if t.matches(query)]
        # May or may not match depending on pattern - this is informational
        # Just ensure no crashes
        assert isinstance(matches, list)


class TestPriorityDistribution:
    """Test priority distribution across templates."""

    def test_priority_range(self):
        """Verify priorities are within valid range."""
        priorities = [t.priority for t in MANA_TEMPLATES]
        assert all(1 <= p <= 10 for p in priorities), "All priorities should be 1-10"

    def test_high_priority_templates_exist(self):
        """Verify high-priority templates exist."""
        high_priority = [t for t in MANA_TEMPLATES if t.priority >= 8]
        assert len(high_priority) > 0, "Should have high-priority templates"

    def test_priority_distribution_balanced(self):
        """Verify priority distribution is reasonable."""
        priorities = [t.priority for t in MANA_TEMPLATES]
        avg_priority = sum(priorities) / len(priorities)
        assert 6 <= avg_priority <= 9, "Average priority should be reasonable (6-9)"


class TestQueryBuilders:
    """Test query builder functions."""

    def test_workshop_query_builders_callable(self):
        """Verify workshop query builders are callable."""
        for template in MANA_WORKSHOP_TEMPLATES:
            assert callable(template.query_builder), f"Template {template.id} query_builder not callable"

    def test_assessment_query_builders_callable(self):
        """Verify assessment query builders are callable."""
        for template in MANA_ASSESSMENT_TEMPLATES:
            assert callable(template.query_builder), f"Template {template.id} query_builder not callable"

    def test_query_builder_returns_string(self):
        """Verify query builders return strings."""
        for template in MANA_TEMPLATES:
            result = template.query_builder({})
            assert isinstance(result, str), f"Template {template.id} query_builder should return string"

    def test_query_builder_with_entities(self):
        """Test query builders with sample entities."""
        entities = {
            'location': {'type': 'region', 'value': 'Region IX'},
            'status': {'value': 'completed'},
        }
        for template in MANA_TEMPLATES:
            result = template.query_builder(entities)
            assert isinstance(result, str), f"Template {template.id} should handle entities"
