"""
Tests for Template Matcher Infrastructure

Tests the pattern-based query template matching system including:
- Template registration and retrieval
- Pattern matching and scoring
- Entity validation and substitution
- Query generation
- Edge cases and error handling
"""

import pytest
from datetime import datetime, timedelta

from common.ai_services.chat.query_templates.base import (
    QueryTemplate,
    TemplateRegistry,
    get_template_registry,
)
from common.ai_services.chat.template_matcher import (
    TemplateMatcher,
    get_template_matcher,
)


@pytest.fixture
def registry():
    """Provide a fresh template registry for each test."""
    TemplateRegistry.reset_instance()
    return TemplateRegistry.get_instance()


@pytest.fixture
def matcher():
    """Provide a fresh template matcher for each test."""
    TemplateRegistry.reset_instance()
    return TemplateMatcher()


@pytest.fixture
def sample_templates():
    """Provide sample templates for testing."""
    return [
        QueryTemplate(
            id='count_communities_location',
            category='communities',
            pattern=r'(?:how many|count|total).*communit.*(?:in|at)\s+(.+)',
            query_template='OBCCommunity.objects.filter({location_filter}).count()',
            required_entities=['location'],
            optional_entities=[],
            examples=[
                'How many communities in Region IX?',
                'Count communities in Zamboanga',
                'Total communities at Davao'
            ],
            priority=10,
            description='Count OBC communities in a location'
        ),
        QueryTemplate(
            id='list_workshops_location',
            category='mana',
            pattern=r'(?:show|list|display).*workshop.*(?:in|at)\s+(.+)',
            query_template='WorkshopActivity.objects.filter({location_filter}).order_by("-date_conducted")',
            required_entities=['location'],
            optional_entities=['date_range'],
            examples=[
                'Show workshops in Davao',
                'List workshops at Region X',
                'Display workshop activities in Zamboanga'
            ],
            priority=8,
            description='List workshops in a location'
        ),
        QueryTemplate(
            id='get_community_by_name',
            category='communities',
            pattern=r'(?:find|get|show).*community.*(?:named|called)\s+(.+)',
            query_template='OBCCommunity.objects.filter(name__icontains={community_name})',
            required_entities=['community_name'],
            optional_entities=['location'],
            examples=[
                'Find community named Badjao',
                'Get community called Teduray',
                'Show community named Maguindanao'
            ],
            priority=9,
            description='Find community by name'
        ),
        QueryTemplate(
            id='count_all_communities',
            category='communities',
            pattern=r'(?:how many|count|total)\s+(?:all\s+)?communit',
            query_template='OBCCommunity.objects.all().count()',
            required_entities=[],
            optional_entities=[],
            examples=[
                'How many communities?',
                'Count all communities',
                'Total communities'
            ],
            priority=7,
            description='Count all communities'
        ),
    ]


class TestQueryTemplate:
    """Test QueryTemplate class functionality."""

    def test_template_creation(self):
        """Test creating a query template."""
        template = QueryTemplate(
            id='test_template',
            category='test',
            pattern=r'test.*query',
            query_template='Model.objects.filter(field={value})',
            required_entities=['value'],
            optional_entities=['filter'],
            examples=['test query example'],
            priority=5,
            description='Test template'
        )

        assert template.id == 'test_template'
        assert template.category == 'test'
        assert template.pattern == r'test.*query'
        assert template.priority == 5
        assert template.compiled_pattern is not None

    def test_pattern_compilation_error(self):
        """Test handling of invalid regex pattern."""
        # Invalid regex - unclosed group
        template = QueryTemplate(
            id='invalid_regex',
            category='test',
            pattern=r'(?:unclosed',  # Invalid regex
            query_template='Model.objects.all()',
            required_entities=[],
        )

        # Should handle gracefully with None compiled_pattern
        assert template.compiled_pattern is None

    def test_matches_query(self):
        """Test pattern matching against queries."""
        template = QueryTemplate(
            id='test',
            category='test',
            pattern=r'(?:how many|count).*communities.*(?:in|at)\s+(.+)',
            query_template='OBCCommunity.objects.filter({location_filter}).count()',
            required_entities=['location'],
        )

        # Should match
        assert template.matches('how many communities in Region IX') is not None
        assert template.matches('count communities at Zamboanga') is not None

        # Should not match
        assert template.matches('show communities in Region IX') is None
        assert template.matches('random unrelated query') is None

    def test_can_execute_with_entities(self):
        """Test entity requirement validation."""
        template = QueryTemplate(
            id='test',
            category='test',
            pattern=r'test',
            query_template='Model.objects.filter({location_filter}, {status_filter})',
            required_entities=['location', 'status'],
            optional_entities=['date_range'],
        )

        # All required entities present
        entities_complete = {
            'location': {'type': 'region', 'value': 'Region IX'},
            'status': {'value': 'active'},
        }
        assert template.can_execute(entities_complete) is True

        # Missing one required entity
        entities_incomplete = {
            'location': {'type': 'region', 'value': 'Region IX'},
        }
        assert template.can_execute(entities_incomplete) is False

        # Missing all required entities
        entities_empty = {}
        assert template.can_execute(entities_empty) is False

    def test_get_missing_entities(self):
        """Test identifying missing required entities."""
        template = QueryTemplate(
            id='test',
            category='test',
            pattern=r'test',
            query_template='Model.objects.filter({location_filter}, {status_filter})',
            required_entities=['location', 'status', 'date_range'],
        )

        entities = {
            'location': {'type': 'region', 'value': 'Region IX'},
        }

        missing = template.get_missing_entities(entities)
        assert 'status' in missing
        assert 'date_range' in missing
        assert 'location' not in missing
        assert len(missing) == 2

    def test_score_match(self):
        """Test match scoring algorithm."""
        template = QueryTemplate(
            id='test',
            category='test',
            pattern=r'how many communities',
            query_template='OBCCommunity.objects.filter({location_filter}).count()',
            required_entities=['location'],
            optional_entities=['date_range'],
            priority=8,
        )

        # Perfect match with all entities
        entities_complete = {
            'location': {'type': 'region', 'value': 'Region IX'},
            'date_range': {'start': '2024-01-01', 'end': '2024-12-31'},
        }
        score_complete = template.score_match('how many communities', entities_complete)
        assert score_complete > 0.8  # Should be high

        # Match with only required entities
        entities_partial = {
            'location': {'type': 'region', 'value': 'Region IX'},
        }
        score_partial = template.score_match('how many communities', entities_partial)
        assert 0.5 < score_partial < score_complete

        # No match - will still have some score from priority (0.24 from priority + 0.3 from entities)
        # but should be significantly lower than a match
        score_no_match = template.score_match('show workshops', entities_complete)
        assert score_no_match < 0.6  # Should be less than partial match
        assert score_no_match < score_partial  # Should be less than matches with required entities


class TestTemplateRegistry:
    """Test TemplateRegistry class functionality."""

    def test_singleton_pattern(self):
        """Test registry implements singleton pattern."""
        registry1 = TemplateRegistry.get_instance()
        registry2 = TemplateRegistry.get_instance()

        assert registry1 is registry2

    def test_register_template(self, registry, sample_templates):
        """Test registering a single template."""
        template = sample_templates[0]
        registry.register(template)

        retrieved = registry.get_template(template.id)
        assert retrieved is template
        assert retrieved.id == template.id

    def test_register_duplicate_id_raises_error(self, registry, sample_templates):
        """Test registering duplicate template ID raises error."""
        template = sample_templates[0]
        registry.register(template)

        # Try to register another template with same ID
        duplicate = QueryTemplate(
            id=template.id,  # Same ID
            category='different',
            pattern=r'different',
            query_template='Different.objects.all()',
            required_entities=[],
        )

        with pytest.raises(ValueError, match='already registered'):
            registry.register(duplicate)

    def test_register_many(self, registry, sample_templates):
        """Test registering multiple templates."""
        registry.register_many(sample_templates)

        assert len(registry.get_all_templates()) == len(sample_templates)

        for template in sample_templates:
            retrieved = registry.get_template(template.id)
            assert retrieved is template

    def test_get_templates_by_category(self, registry, sample_templates):
        """Test retrieving templates by category."""
        registry.register_many(sample_templates)

        community_templates = registry.get_templates_by_category('communities')
        assert len(community_templates) == 3  # 3 community templates

        mana_templates = registry.get_templates_by_category('mana')
        assert len(mana_templates) == 1  # 1 mana template

        empty_category = registry.get_templates_by_category('nonexistent')
        assert len(empty_category) == 0

    def test_get_all_templates(self, registry, sample_templates):
        """Test retrieving all templates."""
        registry.register_many(sample_templates)

        all_templates = registry.get_all_templates()
        assert len(all_templates) == len(sample_templates)

    def test_search_templates(self, registry, sample_templates):
        """Test template search functionality."""
        registry.register_many(sample_templates)

        # Search with category filter
        matches = registry.search_templates(
            query='how many communities in Region IX',
            category='communities'
        )
        assert len(matches) > 0
        assert all(t.category == 'communities' for t in matches)

        # Search without category filter
        all_matches = registry.search_templates(
            query='show workshops in Davao'
        )
        assert len(all_matches) > 0

    def test_get_categories(self, registry, sample_templates):
        """Test getting list of categories."""
        registry.register_many(sample_templates)

        categories = registry.get_categories()
        assert 'communities' in categories
        assert 'mana' in categories

    def test_get_stats(self, registry, sample_templates):
        """Test registry statistics."""
        registry.register_many(sample_templates)

        stats = registry.get_stats()
        assert stats['total_templates'] == len(sample_templates)
        assert 'communities' in stats['categories']
        assert stats['categories']['communities'] == 3
        assert stats['avg_priority'] > 0

    def test_clear_registry(self, registry, sample_templates):
        """Test clearing all templates."""
        registry.register_many(sample_templates)
        assert len(registry.get_all_templates()) == len(sample_templates)

        registry.clear()
        assert len(registry.get_all_templates()) == 0


class TestTemplateMatcher:
    """Test TemplateMatcher class functionality."""

    def test_matcher_initialization(self, matcher):
        """Test matcher initializes with registry."""
        assert matcher.registry is not None

    def test_find_matching_templates(self, matcher, sample_templates):
        """Test finding templates matching a query."""
        matcher.registry.register_many(sample_templates)

        entities = {
            'location': {'type': 'region', 'value': 'Region IX'}
        }

        matches = matcher.find_matching_templates(
            query='how many communities in Region IX',
            entities=entities,
            category='communities'
        )

        assert len(matches) > 0
        assert all(isinstance(t, QueryTemplate) for t in matches)

    def test_rank_templates(self, matcher, sample_templates):
        """Test template ranking by match quality."""
        matcher.registry.register_many(sample_templates)

        # Get matching templates first
        matches = matcher.find_matching_templates(
            query='how many communities in Region IX',
            entities={'location': {'type': 'region', 'value': 'Region IX'}},
            category='communities'
        )

        # Rank them
        ranked = matcher.rank_templates(
            templates=matches,
            query='how many communities in Region IX',
            entities={'location': {'type': 'region', 'value': 'Region IX'}}
        )

        # Should be sorted by score (descending)
        assert len(ranked) > 0
        for i in range(len(ranked) - 1):
            assert ranked[i]['score'] >= ranked[i + 1]['score']

    def test_validate_template(self, matcher):
        """Test template validation with entities."""
        template = QueryTemplate(
            id='test',
            category='test',
            pattern=r'test',
            query_template='Model.objects.filter({location_filter})',
            required_entities=['location'],
        )

        # Valid - all required entities present
        entities_valid = {
            'location': {'type': 'region', 'value': 'Region IX'}
        }
        validation = matcher.validate_template(template, entities_valid)
        assert validation['is_valid'] is True
        assert len(validation['missing_entities']) == 0

        # Invalid - missing required entity
        entities_invalid = {}
        validation = matcher.validate_template(template, entities_invalid)
        assert validation['is_valid'] is False
        assert 'location' in validation['missing_entities']

    def test_substitute_entities_location(self, matcher):
        """Test entity substitution for location filters."""
        template_string = 'OBCCommunity.objects.filter({location_filter})'

        # Region filter
        entities_region = {
            'location': {'type': 'region', 'value': 'Region IX'}
        }
        result = matcher.substitute_entities(template_string, entities_region)
        assert 'region__name__icontains' in result
        assert 'Region IX' in result

        # Province filter
        entities_province = {
            'location': {'type': 'province', 'value': 'Zamboanga del Norte'}
        }
        result = matcher.substitute_entities(template_string, entities_province)
        assert 'province__name__icontains' in result
        assert 'Zamboanga del Norte' in result

        # Municipality filter
        entities_municipality = {
            'location': {'type': 'municipality', 'value': 'Dipolog'}
        }
        result = matcher.substitute_entities(template_string, entities_municipality)
        assert 'municipality__name__icontains' in result
        assert 'Dipolog' in result

    def test_substitute_entities_status(self, matcher):
        """Test entity substitution for status filters."""
        template_string = 'Model.objects.filter({status_filter})'

        entities = {
            'status': {'value': 'active'}
        }
        result = matcher.substitute_entities(template_string, entities)
        assert 'status__iexact' in result
        assert 'active' in result

    def test_substitute_entities_date_range(self, matcher):
        """Test entity substitution for date range filters."""
        template_string = 'Model.objects.filter({date_range_filter})'

        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)

        entities = {
            'date_range': {
                'start': start_date,
                'end': end_date
            }
        }
        result = matcher.substitute_entities(template_string, entities)
        assert 'created_at__gte' in result
        assert 'created_at__lte' in result
        assert '2024-01-01' in result
        assert '2024-12-31' in result

    def test_generate_query(self, matcher):
        """Test complete query generation."""
        template = QueryTemplate(
            id='test',
            category='test',
            pattern=r'test',
            query_template='OBCCommunity.objects.filter({location_filter}).count()',
            required_entities=['location'],
        )

        entities = {
            'location': {'type': 'region', 'value': 'Region IX'}
        }

        query = matcher.generate_query(template, entities)
        assert 'OBCCommunity.objects.filter' in query
        assert 'region__name__icontains' in query
        assert 'Region IX' in query
        assert '.count()' in query

    def test_match_and_generate_success(self, matcher, sample_templates):
        """Test complete match and generate workflow - success case."""
        matcher.registry.register_many(sample_templates)

        result = matcher.match_and_generate(
            query='how many communities in Region IX',
            entities={'location': {'type': 'region', 'value': 'Region IX'}},
            category='communities'
        )

        assert result['success'] is True
        assert result['template'] is not None
        assert result['query'] is not None
        assert result['score'] > 0
        assert result['error'] is None
        assert len(result['missing_entities']) == 0

    def test_match_and_generate_no_match(self, matcher, sample_templates):
        """Test match and generate with no matching templates."""
        matcher.registry.register_many(sample_templates)

        result = matcher.match_and_generate(
            query='completely unrelated query that matches nothing',
            entities={},
            category='communities'
        )

        assert result['success'] is False
        assert result['template'] is None
        assert result['query'] is None
        assert 'No matching templates' in result['error']

    def test_match_and_generate_missing_entities(self, matcher, sample_templates):
        """Test match and generate with missing required entities."""
        matcher.registry.register_many(sample_templates)

        result = matcher.match_and_generate(
            query='how many communities in Region IX',
            entities={},  # Missing required 'location' entity
            category='communities'
        )

        assert result['success'] is False
        assert 'location' in result['missing_entities']

    def test_get_template_suggestions(self, matcher, sample_templates):
        """Test template autocomplete suggestions."""
        matcher.registry.register_many(sample_templates)

        suggestions = matcher.get_template_suggestions(
            partial_query='how many',
            category='communities',
            max_suggestions=5
        )

        assert len(suggestions) > 0
        assert all('example' in s for s in suggestions)
        assert all(s['category'] == 'communities' for s in suggestions)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_query(self, matcher):
        """Test handling of empty query."""
        template = QueryTemplate(
            id='test',
            category='test',
            pattern=r'test',
            query_template='Model.objects.all()',
            required_entities=[],
        )

        assert template.matches('') is None
        assert template.matches(None) is None

    def test_none_entities(self, matcher):
        """Test handling of None entities."""
        template = QueryTemplate(
            id='test',
            category='test',
            pattern=r'test',
            query_template='Model.objects.filter({location_filter})',
            required_entities=['location'],
        )

        # Should handle gracefully
        missing = template.get_missing_entities({})
        assert 'location' in missing

    def test_special_characters_in_query(self, matcher):
        """Test handling of special characters in queries."""
        template = QueryTemplate(
            id='test',
            category='test',
            pattern=r'communities.*\$.*\d+',
            query_template='Model.objects.all()',
            required_entities=[],
        )

        # Should compile pattern successfully
        assert template.compiled_pattern is not None

        # Should match queries with special chars
        match = template.matches('communities $100 budget')
        assert match is not None

    def test_case_insensitive_matching(self, matcher):
        """Test case-insensitive pattern matching."""
        template = QueryTemplate(
            id='test',
            category='test',
            pattern=r'how many communities',
            query_template='OBCCommunity.objects.all().count()',
            required_entities=[],
        )

        # All should match (case-insensitive)
        assert template.matches('how many communities') is not None
        assert template.matches('HOW MANY COMMUNITIES') is not None
        assert template.matches('How Many Communities') is not None

    def test_unicode_in_location_names(self, matcher):
        """Test handling of Unicode characters in location names."""
        template_string = 'OBCCommunity.objects.filter({location_filter})'

        entities = {
            'location': {'type': 'municipality', 'value': 'Mañgañga'}
        }

        result = matcher.substitute_entities(template_string, entities)
        assert 'Mañgañga' in result


class TestGlobalSingletons:
    """Test global singleton accessors."""

    def test_get_template_registry_singleton(self):
        """Test global template registry accessor."""
        registry1 = get_template_registry()
        registry2 = get_template_registry()

        assert registry1 is registry2

    def test_get_template_matcher_singleton(self):
        """Test global template matcher accessor."""
        matcher1 = get_template_matcher()
        matcher2 = get_template_matcher()

        assert matcher1 is matcher2
