"""
Tests for Needs Query Templates

Comprehensive test suite for the 12 critical needs query templates.
Tests pattern matching, entity extraction, and Django ORM query generation.
"""

import pytest
import re
from common.ai_services.chat.query_templates.needs import (
    NEEDS_TEMPLATES,
    NEEDS_COUNT_TEMPLATES,
    NEEDS_ANALYSIS_TEMPLATES,
    NEEDS_CROSS_DOMAIN_TEMPLATES,
)
from common.ai_services.chat.entity_extractor import EntityExtractor


class TestNeedsTemplateStructure:
    """Test basic structure and completeness of needs templates."""

    def test_total_template_count(self):
        """Verify we have exactly 12 needs templates."""
        assert len(NEEDS_TEMPLATES) == 12, "Should have 12 needs templates"

    def test_template_categories(self):
        """Verify templates are organized into correct categories."""
        assert len(NEEDS_COUNT_TEMPLATES) == 5, "Should have 5 count templates"
        assert len(NEEDS_ANALYSIS_TEMPLATES) == 5, "Should have 5 analysis templates"
        assert len(NEEDS_CROSS_DOMAIN_TEMPLATES) == 2, "Should have 2 cross-domain templates"

    def test_all_templates_have_required_fields(self):
        """Verify all templates have required fields."""
        for template in NEEDS_TEMPLATES:
            assert hasattr(template, 'id'), f"Template missing 'id': {template}"
            assert hasattr(template, 'category'), f"Template missing 'category': {template.id}"
            assert hasattr(template, 'pattern'), f"Template missing 'pattern': {template.id}"
            assert hasattr(template, 'query_template'), f"Template missing 'query_template': {template.id}"
            assert hasattr(template, 'examples'), f"Template missing 'examples': {template.id}"
            assert template.category == 'needs', f"Template has wrong category: {template.id}"

    def test_all_templates_have_examples(self):
        """Verify all templates have at least 3 examples."""
        for template in NEEDS_TEMPLATES:
            assert len(template.examples) >= 3, f"Template {template.id} needs at least 3 examples"


class TestNeedsCountTemplates:
    """Test count query templates (5 templates)."""

    def test_count_all_needs_pattern(self):
        """Test 'count all needs' pattern matching."""
        template = next(t for t in NEEDS_COUNT_TEMPLATES if t.id == 'count_all_needs')

        test_queries = [
            'how many needs',
            'total needs',
            'count all needs',
            'number of identified needs',
            'how many community needs',
        ]

        for query in test_queries:
            assert re.search(template.pattern, query, re.IGNORECASE), \
                f"Pattern should match: {query}"

    def test_count_needs_by_priority_pattern(self):
        """Test 'count needs by priority' pattern matching."""
        template = next(t for t in NEEDS_COUNT_TEMPLATES if t.id == 'count_needs_by_priority')

        test_queries = [
            'how many critical needs',
            'count high priority needs',
            'total immediate needs',
            'number of urgent needs',
        ]

        for query in test_queries:
            assert re.search(template.pattern, query, re.IGNORECASE), \
                f"Pattern should match: {query}"

    def test_count_needs_by_sector_pattern(self):
        """Test 'count needs by sector' pattern matching."""
        template = next(t for t in NEEDS_COUNT_TEMPLATES if t.id == 'count_needs_by_sector')

        test_queries = [
            'how many infrastructure needs',
            'count education needs',
            'total health sector needs',
            'number of livelihood needs',
        ]

        for query in test_queries:
            assert re.search(template.pattern, query, re.IGNORECASE), \
                f"Pattern should match: {query}"

    def test_count_needs_by_location_pattern(self):
        """Test 'count needs by location' pattern matching."""
        template = next(t for t in NEEDS_COUNT_TEMPLATES if t.id == 'count_needs_by_location')

        test_queries = [
            'how many needs in Region IX',
            'count needs in Zamboanga del Sur',
            'total needs in Sultan Kudarat',
        ]

        for query in test_queries:
            assert re.search(template.pattern, query, re.IGNORECASE), \
                f"Pattern should match: {query}"

    def test_count_needs_by_status_pattern(self):
        """Test 'count needs by status' pattern matching."""
        template = next(t for t in NEEDS_COUNT_TEMPLATES if t.id == 'count_needs_by_status')

        test_queries = [
            'how many unmet needs',
            'count fulfilled needs',
            'total ongoing needs',
            'number of identified needs',
        ]

        for query in test_queries:
            assert re.search(template.pattern, query, re.IGNORECASE), \
                f"Pattern should match: {query}"


class TestNeedsAnalysisTemplates:
    """Test needs analysis templates (5 templates)."""

    def test_list_unmet_needs_pattern(self):
        """Test 'list unmet needs' pattern matching."""
        template = next(t for t in NEEDS_ANALYSIS_TEMPLATES if t.id == 'list_unmet_needs')

        test_queries = [
            'show me unmet needs',
            'list unfulfilled needs',
            'display unaddressed needs',
            'needs without funding',
        ]

        for query in test_queries:
            assert re.search(template.pattern, query, re.IGNORECASE), \
                f"Pattern should match: {query}"

    def test_list_top_priority_needs_pattern(self):
        """Test 'list top priority needs' pattern matching."""
        template = next(t for t in NEEDS_ANALYSIS_TEMPLATES if t.id == 'list_top_priority_needs')

        test_queries = [
            'top priority needs',
            'top 10 critical needs',
            'highest priority needs',
            'most critical needs',
        ]

        for query in test_queries:
            assert re.search(template.pattern, query, re.IGNORECASE), \
                f"Pattern should match: {query}"

    def test_needs_by_assessment_pattern(self):
        """Test 'needs by assessment' pattern matching."""
        template = next(t for t in NEEDS_ANALYSIS_TEMPLATES if t.id == 'needs_by_assessment')

        test_queries = [
            'needs from assessment X',
            'needs identified in workshop',
            'show needs in assessment abc123',
        ]

        for query in test_queries:
            assert re.search(template.pattern, query, re.IGNORECASE), \
                f"Pattern should match: {query}"

    def test_needs_by_community_pattern(self):
        """Test 'needs by community' pattern matching."""
        template = next(t for t in NEEDS_ANALYSIS_TEMPLATES if t.id == 'needs_by_community')

        test_queries = [
            'needs for community Y',
            'what needs does this community have',
            'show needs in some community',
            'list needs in Maranao community',
        ]

        for query in test_queries:
            assert re.search(template.pattern, query, re.IGNORECASE), \
                f"Pattern should match: {query}"

    def test_list_needs_by_sector_pattern(self):
        """Test 'list needs by sector' pattern matching."""
        template = next(t for t in NEEDS_ANALYSIS_TEMPLATES if t.id == 'list_needs_by_sector')

        test_queries = [
            'show infrastructure needs',
            'list education needs',
            'display health sector needs',
            'show me livelihood needs',
        ]

        for query in test_queries:
            assert re.search(template.pattern, query, re.IGNORECASE), \
                f"Pattern should match: {query}"


class TestNeedsCrossDomainTemplates:
    """Test cross-domain query templates (2 templates)."""

    def test_needs_with_ppas_pattern(self):
        """Test 'needs with PPAs' pattern matching."""
        template = next(t for t in NEEDS_CROSS_DOMAIN_TEMPLATES if t.id == 'needs_with_ppas')

        test_queries = [
            'needs with implementing PPAs',
            'show addressed needs',
            'needs with funding',
            'needs with programs',
        ]

        for query in test_queries:
            assert re.search(template.pattern, query, re.IGNORECASE), \
                f"Pattern should match: {query}"

    def test_needs_without_ppas_pattern(self):
        """Test 'needs without PPAs' pattern matching."""
        template = next(t for t in NEEDS_CROSS_DOMAIN_TEMPLATES if t.id == 'needs_without_ppas')

        test_queries = [
            'needs not yet addressed',
            'unaddressed needs',
            'needs without PPAs',
            'needs without funding',
        ]

        for query in test_queries:
            assert re.search(template.pattern, query, re.IGNORECASE), \
                f"Pattern should match: {query}"


class TestEntityExtraction:
    """Test entity extraction for needs queries."""

    def setup_method(self):
        """Initialize entity extractor for tests."""
        self.extractor = EntityExtractor()

    def test_extract_sector_entity(self):
        """Test sector entity extraction."""
        queries = [
            ('how many infrastructure needs', 'infrastructure'),
            ('count education needs', 'education'),
            ('health sector needs', 'health'),
            ('show governance needs', 'governance'),
        ]

        for query, expected_sector in queries:
            entities = self.extractor.extract_entities(query)
            assert 'sector' in entities, f"Should extract sector from: {query}"
            assert entities['sector']['value'] == expected_sector, \
                f"Expected sector '{expected_sector}' from: {query}"

    def test_extract_priority_level_entity(self):
        """Test priority level entity extraction."""
        queries = [
            ('critical needs', 'immediate'),
            ('high priority needs', 'short_term'),
            ('urgent needs', 'immediate'),
            ('low priority needs', 'long_term'),
        ]

        for query, expected_priority in queries:
            entities = self.extractor.extract_entities(query)
            assert 'priority_level' in entities, f"Should extract priority from: {query}"
            assert entities['priority_level']['value'] == expected_priority, \
                f"Expected priority '{expected_priority}' from: {query}"

    def test_extract_urgency_level_entity(self):
        """Test urgency level entity extraction."""
        queries = [
            ('immediate needs', 'immediate'),
            ('short term needs', 'short_term'),
            ('long term needs', 'long_term'),
        ]

        for query, expected_urgency in queries:
            entities = self.extractor.extract_entities(query)
            assert 'urgency_level' in entities, f"Should extract urgency from: {query}"
            assert entities['urgency_level']['value'] == expected_urgency, \
                f"Expected urgency '{expected_urgency}' from: {query}"

    def test_extract_need_status_entity(self):
        """Test need status entity extraction."""
        queries = [
            ('unmet needs', 'identified'),
            ('fulfilled needs', 'completed'),
            ('ongoing needs', 'in_progress'),
            ('planned needs', 'planned'),
        ]

        for query, expected_status in queries:
            entities = self.extractor.extract_entities(query)
            assert 'need_status' in entities, f"Should extract status from: {query}"
            assert entities['need_status']['value'] == expected_status, \
                f"Expected status '{expected_status}' from: {query}"

    def test_extract_location_entity(self):
        """Test location entity extraction in needs queries."""
        query = "needs in region ix"
        entities = self.extractor.extract_entities(query)

        assert 'location' in entities, "Should extract location"
        assert entities['location']['value'] == 'Region IX', "Should identify Region IX"

    def test_extract_multiple_entities(self):
        """Test extraction of multiple entities from single query."""
        query = "critical infrastructure needs in region ix"
        entities = self.extractor.extract_entities(query)

        # Should extract all three entities
        assert 'sector' in entities, "Should extract sector"
        assert 'priority_level' in entities, "Should extract priority"
        assert 'location' in entities, "Should extract location"

        assert entities['sector']['value'] == 'infrastructure'
        assert entities['priority_level']['value'] == 'immediate'
        assert entities['location']['value'] == 'Region IX'


class TestQueryTemplateGeneration:
    """Test Django ORM query generation from templates."""

    def test_count_all_needs_query(self):
        """Test query generation for count_all_needs."""
        template = next(t for t in NEEDS_COUNT_TEMPLATES if t.id == 'count_all_needs')
        query = template.query_template

        assert 'Need.objects.count()' == query, "Should generate correct count query"

    def test_count_needs_by_sector_requires_sector_entity(self):
        """Test that count_needs_by_sector requires sector entity."""
        template = next(t for t in NEEDS_COUNT_TEMPLATES if t.id == 'count_needs_by_sector')

        assert 'sector' in template.required_entities or '{sector_filter}' in template.query_template, \
            "Should require sector entity or have sector filter placeholder"

    def test_list_unmet_needs_query(self):
        """Test query generation for list_unmet_needs."""
        template = next(t for t in NEEDS_ANALYSIS_TEMPLATES if t.id == 'list_unmet_needs')
        query = template.query_template

        # Should filter for identified status and null linked_ppa
        assert 'status="identified"' in query, "Should filter by identified status"
        assert 'linked_ppa__isnull=True' in query, "Should filter for null PPA"

    def test_needs_with_ppas_query(self):
        """Test query generation for needs_with_ppas."""
        template = next(t for t in NEEDS_CROSS_DOMAIN_TEMPLATES if t.id == 'needs_with_ppas')
        query = template.query_template

        # Should filter for non-null linked_ppa
        assert 'linked_ppa__isnull=False' in query, "Should filter for non-null PPA"

    def test_needs_without_ppas_query(self):
        """Test query generation for needs_without_ppas (gap analysis)."""
        template = next(t for t in NEEDS_CROSS_DOMAIN_TEMPLATES if t.id == 'needs_without_ppas')
        query = template.query_template

        # Should filter for null linked_ppa (gap analysis)
        assert 'linked_ppa__isnull=True' in query, "Should filter for null PPA (gap)"


class TestTemplateMetadata:
    """Test template metadata (priority, tags, descriptions)."""

    def test_all_critical_templates_high_priority(self):
        """Verify all needs templates have high priority (9-10)."""
        for template in NEEDS_TEMPLATES:
            assert template.priority >= 9, \
                f"Template {template.id} should have priority >= 9 (CRITICAL)"

    def test_all_templates_have_tags(self):
        """Verify all templates have appropriate tags."""
        for template in NEEDS_TEMPLATES:
            assert hasattr(template, 'tags'), f"Template {template.id} missing tags"
            assert len(template.tags) >= 2, f"Template {template.id} needs at least 2 tags"
            assert 'needs' in template.tags, f"Template {template.id} should have 'needs' tag"

    def test_count_templates_have_count_tag(self):
        """Verify count templates have 'count' tag."""
        for template in NEEDS_COUNT_TEMPLATES:
            assert 'count' in template.tags, f"Count template {template.id} needs 'count' tag"

    def test_list_templates_have_list_tag(self):
        """Verify list templates have 'list' tag."""
        for template in NEEDS_ANALYSIS_TEMPLATES:
            if template.id.startswith('list_'):
                assert 'list' in template.tags, f"List template {template.id} needs 'list' tag"

    def test_cross_domain_templates_have_relevant_tags(self):
        """Verify cross-domain templates have 'ppas' or 'gap' tags."""
        for template in NEEDS_CROSS_DOMAIN_TEMPLATES:
            assert 'ppas' in template.tags or 'gap' in template.tags, \
                f"Cross-domain template {template.id} needs 'ppas' or 'gap' tag"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
