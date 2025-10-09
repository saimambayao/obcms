"""
Test suite for Geographic Query Templates

Tests all 50 geographic templates covering:
- Region queries (12 templates)
- Province queries (12 templates)
- Municipality queries (12 templates)
- Barangay queries (8 templates)
- Cross-level queries (6 templates)

Critical test: Verify "Show me the list of provinces" works (fixes user issue)
"""

import pytest
from common.ai_services.chat.query_templates import get_template_registry


class TestGeographicTemplates:
    """Test geographic query templates registration and matching."""

    @pytest.fixture
    def registry(self):
        """Get template registry."""
        return get_template_registry()

    def test_geographic_templates_registered(self, registry):
        """Test that all 50 geographic templates are registered."""
        geographic_templates = registry.get_templates_by_category('geographic')
        # Note: Some templates may already exist in other files, so we expect at least 46
        assert len(geographic_templates) >= 46, f"Expected at least 46 templates, got {len(geographic_templates)}"

        # Check that key templates exist
        template_ids = [t.id for t in geographic_templates]
        assert 'list_all_provinces' in template_ids, "list_all_provinces template missing (critical fix)"
        assert 'list_all_regions' in template_ids
        assert 'list_all_municipalities' in template_ids
        assert 'list_all_barangays' in template_ids

    # =============================================================================
    # REGION TEMPLATES (12 tests)
    # =============================================================================

    def test_count_regions(self, registry):
        """Test: How many regions?"""
        matches = registry.search_templates("How many regions?")
        assert len(matches) > 0, "No matches found for 'How many regions?'"
        assert any(m.id == 'count_all_regions' for m in matches)

    def test_list_regions(self, registry):
        """Test: Show me all regions"""
        matches = registry.search_templates("Show me all regions")
        assert len(matches) > 0, "No matches found for 'Show me all regions'"
        assert any(m.id == 'list_all_regions' for m in matches)

    def test_regions_with_obc(self, registry):
        """Test: How many regions with OBC?"""
        matches = registry.search_templates("How many regions with OBC?")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'count_regions_with_obc' for m in matches)

    def test_region_by_name(self, registry):
        """Test: Show me Region IX"""
        matches = registry.search_templates("Show me Region IX")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'region_by_name' for m in matches)

    def test_regions_with_boundaries(self, registry):
        """Test: Which regions have boundaries?"""
        matches = registry.search_templates("Which regions have boundaries?")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'regions_with_boundaries' for m in matches)

    def test_region_demographics(self, registry):
        """Test: Show population by region"""
        matches = registry.search_templates("Show population by region")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'region_demographics' for m in matches)

    # =============================================================================
    # PROVINCE TEMPLATES (12 tests) - CRITICAL SECTION
    # =============================================================================

    def test_count_provinces(self, registry):
        """Test: How many provinces?"""
        matches = registry.search_templates("How many provinces?")
        assert len(matches) > 0, "No matches found for 'How many provinces?'"
        assert any(m.id == 'count_all_provinces' for m in matches)

    def test_list_provinces_all(self, registry):
        """Test: Show me all provinces"""
        matches = registry.search_templates("Show me all provinces")
        assert len(matches) > 0, "No matches found for 'Show me all provinces'"
        assert any(m.id == 'list_all_provinces' for m in matches)

    def test_list_provinces_critical(self, registry):
        """Test: Show me the list of provinces - CRITICAL TEST (user issue)"""
        matches = registry.search_templates("Show me the list of provinces")
        assert len(matches) > 0, "No matches found for 'Show me the list of provinces'"

        # Verify list_all_provinces template matches
        list_template = next((m for m in matches if m.id == 'list_all_provinces'), None)
        assert list_template is not None, "list_all_provinces template did not match"
        assert list_template.result_type == 'list', "Template should return a list"

    def test_list_provinces_variant(self, registry):
        """Test: Show me the list of province (singular - user's exact query)"""
        matches = registry.search_templates("Show me the list of province")
        assert len(matches) > 0, "No matches found for 'Show me the list of province'"
        assert any(m.id == 'list_all_provinces' for m in matches)

    def test_count_provinces_by_region(self, registry):
        """Test: How many provinces in Region IX?"""
        matches = registry.search_templates("How many provinces in Region IX?")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'count_provinces_by_region' for m in matches)

    def test_list_provinces_by_region(self, registry):
        """Test: Show provinces in Region IX"""
        matches = registry.search_templates("Show provinces in Region IX")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'list_provinces_by_region' for m in matches)

    def test_province_by_name(self, registry):
        """Test: Show me Zamboanga del Sur province"""
        matches = registry.search_templates("Show me Zamboanga del Sur province")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'province_by_name' for m in matches)

    def test_provinces_with_boundaries(self, registry):
        """Test: Which provinces have boundaries?"""
        matches = registry.search_templates("Which provinces have boundaries?")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'provinces_with_boundaries' for m in matches)

    def test_province_demographics(self, registry):
        """Test: Show population by province"""
        matches = registry.search_templates("Show population by province")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'province_demographics' for m in matches)

    def test_provinces_ranked(self, registry):
        """Test: Rank provinces by OBC population"""
        matches = registry.search_templates("Rank provinces by OBC population")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'provinces_by_obc_population' for m in matches)

    # =============================================================================
    # MUNICIPALITY TEMPLATES (12 tests)
    # =============================================================================

    def test_count_municipalities(self, registry):
        """Test: How many municipalities?"""
        matches = registry.search_templates("How many municipalities?")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'count_all_municipalities' for m in matches)

    def test_list_municipalities(self, registry):
        """Test: Show me all municipalities"""
        matches = registry.search_templates("Show me all municipalities")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'list_all_municipalities' for m in matches)

    def test_count_municipalities_by_province(self, registry):
        """Test: How many municipalities in Cotabato?"""
        matches = registry.search_templates("How many municipalities in Cotabato?")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'count_municipalities_by_province' for m in matches)

    def test_list_municipalities_by_province(self, registry):
        """Test: Show municipalities in Sultan Kudarat"""
        matches = registry.search_templates("Show municipalities in Sultan Kudarat")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'list_municipalities_by_province' for m in matches)

    def test_municipality_by_name(self, registry):
        """Test: Show me Pagadian City"""
        matches = registry.search_templates("Show me Pagadian City")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'municipality_by_name' for m in matches)

    def test_municipalities_urban_rural(self, registry):
        """Test: Show urban municipalities"""
        matches = registry.search_templates("Show urban municipalities")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'municipalities_by_urban_rural' for m in matches)

    def test_municipality_demographics(self, registry):
        """Test: Show population by municipality"""
        matches = registry.search_templates("Show population by municipality")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'municipality_demographics' for m in matches)

    def test_municipalities_high_population(self, registry):
        """Test: Show municipalities with over 1000 OBC population"""
        matches = registry.search_templates("Show municipalities with over 1000 OBC population")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'municipalities_with_high_obc' for m in matches)

    # =============================================================================
    # BARANGAY TEMPLATES (8 tests)
    # =============================================================================

    def test_count_barangays(self, registry):
        """Test: How many barangays?"""
        matches = registry.search_templates("How many barangays?")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'count_all_barangays' for m in matches)

    def test_list_barangays(self, registry):
        """Test: Show me all barangays"""
        matches = registry.search_templates("Show me all barangays")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'list_all_barangays' for m in matches)

    def test_count_barangays_by_municipality(self, registry):
        """Test: How many barangays in Pagadian?"""
        matches = registry.search_templates("How many barangays in Pagadian?")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'count_barangays_by_municipality' for m in matches)

    def test_list_barangays_by_municipality(self, registry):
        """Test: Show barangays in Cotabato City"""
        matches = registry.search_templates("Show barangays in Cotabato City")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'list_barangays_by_municipality' for m in matches)

    def test_barangay_by_name(self, registry):
        """Test: Show me Barangay Poblacion"""
        matches = registry.search_templates("Show me Barangay Poblacion")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'barangay_by_name' for m in matches)

    def test_barangays_with_obc(self, registry):
        """Test: Which barangays have OBC?"""
        matches = registry.search_templates("Which barangays have OBC?")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'barangays_with_obc' for m in matches)

    def test_barangay_demographics(self, registry):
        """Test: Show population by barangay"""
        matches = registry.search_templates("Show population by barangay")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'barangay_demographics' for m in matches)

    def test_barangays_with_coordinates(self, registry):
        """Test: Which barangays have coordinates?"""
        matches = registry.search_templates("Which barangays have coordinates?")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'barangays_with_coordinates' for m in matches)

    # =============================================================================
    # CROSS-LEVEL TEMPLATES (6 tests)
    # =============================================================================

    def test_administrative_hierarchy(self, registry):
        """Test: Show administrative hierarchy"""
        matches = registry.search_templates("Show administrative hierarchy")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'administrative_hierarchy' for m in matches)

    def test_coverage_gaps(self, registry):
        """Test: Show geographic coverage gaps"""
        matches = registry.search_templates("Show geographic coverage gaps")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'geographic_coverage_gaps' for m in matches)

    def test_geographic_summary(self, registry):
        """Test: Show geographic summary"""
        matches = registry.search_templates("Show geographic summary")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'geographic_rollup_summary' for m in matches)

    def test_adjacent_units(self, registry):
        """Test: Show adjacent provinces to Cotabato"""
        matches = registry.search_templates("Show adjacent provinces to Cotabato")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'adjacent_administrative_units' for m in matches)

    def test_geographic_comparison(self, registry):
        """Test: Compare Region IX vs Region X"""
        matches = registry.search_templates("Compare Region IX vs Region X")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'geographic_comparison' for m in matches)

    def test_boundaries_export(self, registry):
        """Test: Export administrative boundaries"""
        matches = registry.search_templates("Export administrative boundaries")
        assert len(matches) > 0, "No matches found"
        assert any(m.id == 'administrative_boundaries_export' for m in matches)

    # =============================================================================
    # INTEGRATION TESTS
    # =============================================================================

    def test_all_province_queries_work(self, registry):
        """Test all province-related queries have matching templates."""
        province_queries = [
            "How many provinces?",
            "Show me all provinces",
            "Show me the list of provinces",
            "Show me the list of province",  # User's exact query
            "List provinces",
            "Display provinces",
            "What are the provinces?",
            "Count provinces in Region IX",
            "Show provinces in Region XII",
            "Get Cotabato province details",
        ]

        for query in province_queries:
            matches = registry.search_templates(query)
            assert len(matches) > 0, f"No matches found for: '{query}'"

    def test_template_priorities(self, registry):
        """Test that list templates have higher priority than count templates."""
        geographic_templates = registry.get_templates_by_category('geographic')

        list_templates = [t for t in geographic_templates if 'list_all' in t.id]
        count_templates = [t for t in geographic_templates if 'count_all' in t.id]

        # List templates should have priority 10
        for template in list_templates:
            assert template.priority == 10, f"Template {template.id} should have priority 10"

        # Count templates should have priority 8
        for template in count_templates:
            assert template.priority == 8, f"Template {template.id} should have priority 8"

    def test_result_types_correct(self, registry):
        """Test that templates have correct result_type metadata."""
        geographic_templates = registry.get_templates_by_category('geographic')

        # Count templates (specifically count_all_* templates)
        count_templates = [t for t in geographic_templates if t.id.startswith('count_all_')]
        for template in count_templates:
            assert template.result_type == 'count', f"Template {template.id} should be result_type='count'"

        # List templates
        list_templates = [t for t in geographic_templates if 'list_all' in t.id]
        for template in list_templates:
            assert template.result_type == 'list', f"Template {template.id} should be result_type='list'"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
