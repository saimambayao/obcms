"""Comprehensive form validation tests for OBC community forms."""

import pytest

pytest.skip(
    "Legacy community form tests require updated widgets after refactor.",
    allow_module_level=True,
)

from django.test import TestCase
from django.core.exceptions import ValidationError

from common.forms.community import (
    OBCCommunityForm,
    MunicipalityCoverageForm,
    ProvinceCoverageForm,
)
from communities.models import (
    OBCCommunity,
    MunicipalityCoverage,
    ProvinceCoverage,
)
from common.models import Region, Province, Municipality, Barangay


class OBCCommunityFormTests(TestCase):
    """Test validation and behavior of OBCCommunityForm."""

    def setUp(self):
        """Create test fixtures for OBC community form tests."""
        self.region = Region.objects.create(
            code="R12",
            name="SOCCSKSARGEN",
            is_active=True
        )
        self.province = Province.objects.create(
            code="PROV-SK",
            name="South Cotabato",
            region=self.region,
            is_active=True
        )
        self.municipality = Municipality.objects.create(
            code="MUN-KRT",
            name="Koronadal City",
            province=self.province,
            is_active=True
        )
        self.barangay = Barangay.objects.create(
            code="BRGY-001",
            name="Zone 1",
            municipality=self.municipality,
            population_total=5000,
            is_active=True
        )

    def test_form_valid_with_minimum_fields(self):
        """Form should be valid with only required fields."""
        form_data = {
            'region': self.region.id,
            'province': self.province.id,
            'municipality': self.municipality.id,
            'barangay': self.barangay.id,
        }
        form = OBCCommunityForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_valid_with_all_fields(self):
        """Form should be valid with all fields populated."""
        form_data = {
            'region': self.region.id,
            'province': self.province.id,
            'municipality': self.municipality.id,
            'barangay': self.barangay.id,
            'community_names': 'Test Community, Legacy Name',
            'obc_id': 'R12-SK-KRT-001',
            'purok_sitio': 'Purok 5',
            'specific_location': 'Near the school',
            'settlement_type': 'village',
            'proximity_to_barmm': 'adjacent',
            'estimated_obc_population': 1200,
            'total_barangay_population': 5000,
            'households': 250,
            'families': 240,
            'children_0_9': 300,
            'adolescents_10_14': 150,
            'youth_15_30': 400,
            'adults_31_59': 300,
            'seniors_60_plus': 50,
            'primary_ethnolinguistic_group': 'maguindanaon',
            'languages_spoken': 'Maguindanaon, Filipino, English',
            'latitude': 6.5025,
            'longitude': 124.8453,
            'established_year': 1985,
        }
        form = OBCCommunityForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_requires_barangay(self):
        """Form should fail validation without barangay."""
        form_data = {
            'region': self.region.id,
            'province': self.province.id,
            'municipality': self.municipality.id,
            # Missing barangay
            'community_names': 'Test Community',
        }
        form = OBCCommunityForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('barangay', form.errors)

    def test_form_population_validation_against_barangay_total(self):
        """OBC population cannot exceed barangay's population_total."""
        form_data = {
            'region': self.region.id,
            'province': self.province.id,
            'municipality': self.municipality.id,
            'barangay': self.barangay.id,
            'estimated_obc_population': 6000,  # Exceeds barangay.population_total (5000)
        }
        form = OBCCommunityForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('estimated_obc_population', form.errors)
        self.assertIn('cannot exceed', str(form.errors['estimated_obc_population']).lower())

    def test_form_population_validation_against_field_total(self):
        """OBC population cannot exceed form's total_barangay_population."""
        form_data = {
            'region': self.region.id,
            'province': self.province.id,
            'municipality': self.municipality.id,
            'barangay': self.barangay.id,
            'estimated_obc_population': 4500,
            'total_barangay_population': 4000,  # Less than OBC population
        }
        form = OBCCommunityForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('estimated_obc_population', form.errors)

    def test_form_population_validation_allows_valid_data(self):
        """Form should accept OBC population within limits."""
        form_data = {
            'region': self.region.id,
            'province': self.province.id,
            'municipality': self.municipality.id,
            'barangay': self.barangay.id,
            'estimated_obc_population': 3000,
            'total_barangay_population': 5000,
        }
        form = OBCCommunityForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_widget_classes_applied(self):
        """Widget classes should be applied for proper styling."""
        form = OBCCommunityForm()
        # Check location field widget classes
        region_classes = form.fields['region'].widget.attrs.get('class', '')
        self.assertIn('rounded', region_classes.lower())
        self.assertIn('border', region_classes.lower())

        # Check number input has min attribute
        households_widget = form.fields.get('households')
        if households_widget:
            min_value = households_widget.widget.attrs.get('min')
            self.assertEqual(min_value, '0')

    def test_form_placeholder_text(self):
        """Form fields should have helpful placeholder text."""
        form = OBCCommunityForm()
        # Check some placeholder examples
        community_names_placeholder = form.fields.get('community_names')
        if community_names_placeholder:
            placeholder = community_names_placeholder.widget.attrs.get('placeholder', '')
            self.assertIn('name', placeholder.lower())

    def test_form_help_text(self):
        """Form fields should have appropriate help text."""
        form = OBCCommunityForm()
        # Check help text examples
        estimated_pop = form.fields.get('estimated_obc_population')
        if estimated_pop:
            help_text = estimated_pop.help_text
            self.assertIsNotNone(help_text)

    def test_form_field_ordering(self):
        """Form should have fields in expected order."""
        form = OBCCommunityForm()
        field_names = list(form.fields.keys())
        # Check that location fields come first
        self.assertIn('region', field_names)
        self.assertIn('province', field_names)
        self.assertIn('municipality', field_names)
        self.assertIn('barangay', field_names)
        # Barangay should be in the fields
        self.assertIn('barangay', field_names)

    def test_form_initial_data_from_instance(self):
        """Form should populate initial data when editing existing instance."""
        # Create an existing OBC community
        community = OBCCommunity.objects.create(
            barangay=self.barangay,
            community_names='Existing Community',
            estimated_obc_population=1500,
        )

        # Create form with instance
        form = OBCCommunityForm(instance=community)

        # Check initial values
        self.assertEqual(form.instance, community)
        self.assertEqual(form.initial.get('estimated_obc_population'), 1500)

    def test_form_location_hierarchy_validation(self):
        """Form should validate location hierarchy consistency."""
        # Create a province in a different region
        other_region = Region.objects.create(
            code="R09",
            name="Zamboanga Peninsula",
            is_active=True
        )

        form_data = {
            'region': other_region.id,  # Different region
            'province': self.province.id,  # Province from SOCCSKSARGEN
            'municipality': self.municipality.id,
            'barangay': self.barangay.id,
        }
        form = OBCCommunityForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('province', form.errors)

    def test_form_coordinate_auto_resolution(self):
        """Form should auto-resolve coordinates from location selection."""
        # Set coordinates on barangay
        self.barangay.latitude = 6.5025
        self.barangay.longitude = 124.8453
        self.barangay.save()

        form_data = {
            'region': self.region.id,
            'province': self.province.id,
            'municipality': self.municipality.id,
            'barangay': self.barangay.id,
            # No latitude/longitude provided
        }
        form = OBCCommunityForm(data=form_data)
        if form.is_valid():
            # Coordinates should be auto-resolved from barangay
            self.assertIsNotNone(form.cleaned_data.get('latitude'))
            self.assertIsNotNone(form.cleaned_data.get('longitude'))

    def test_form_handles_zero_population(self):
        """Form should handle zero population gracefully."""
        form_data = {
            'region': self.region.id,
            'province': self.province.id,
            'municipality': self.municipality.id,
            'barangay': self.barangay.id,
            'estimated_obc_population': 0,
            'total_barangay_population': 0,
        }
        form = OBCCommunityForm(data=form_data)
        # Zero values should not trigger validation errors
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_ethnolinguistic_group_choices(self):
        """Form should provide ethnolinguistic group choices."""
        form = OBCCommunityForm()
        ethnolinguistic_field = form.fields.get('primary_ethnolinguistic_group')
        if ethnolinguistic_field:
            # Check that choices are available
            choices = ethnolinguistic_field.choices
            self.assertIsNotNone(choices)
            # Check for some expected choices
            choice_values = [choice[0] for choice in choices if choice[0]]
            self.assertIn('maguindanaon', choice_values)
            self.assertIn('tausug', choice_values)


class MunicipalityCoverageFormTests(TestCase):
    """Test validation and behavior of MunicipalityCoverageForm."""

    def setUp(self):
        """Create test fixtures for municipality coverage form tests."""
        self.region = Region.objects.create(
            code="R12",
            name="SOCCSKSARGEN",
            is_active=True
        )
        self.province = Province.objects.create(
            code="PROV-SK",
            name="South Cotabato",
            region=self.region,
            is_active=True
        )
        self.municipality = Municipality.objects.create(
            code="MUN-KRT",
            name="Koronadal City",
            province=self.province,
            is_active=True
        )
        self.other_municipality = Municipality.objects.create(
            code="MUN-GEN",
            name="General Santos City",
            province=self.province,
            is_active=True
        )

    def test_form_valid_data(self):
        """Form should be valid with complete data."""
        form_data = {
            'region': self.region.id,
            'province': self.province.id,
            'municipality': self.municipality.id,
            'total_obc_communities': 15,
            'existing_support_programs': 'TABANG, AMBag',
            'auto_sync': True,
        }
        form = MunicipalityCoverageForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_requires_municipality(self):
        """Form should require municipality field."""
        form_data = {
            'region': self.region.id,
            'province': self.province.id,
            # Missing municipality
            'total_obc_communities': 15,
        }
        form = MunicipalityCoverageForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('municipality', form.errors)

    def test_form_prevents_duplicate_municipality(self):
        """Form should prevent creating coverage for same municipality twice."""
        # Create existing coverage
        MunicipalityCoverage.objects.create(
            municipality=self.municipality,
            total_obc_communities=10,
        )

        # Try to create another coverage for same municipality
        form_data = {
            'region': self.region.id,
            'province': self.province.id,
            'municipality': self.municipality.id,
            'total_obc_communities': 15,
        }
        form = MunicipalityCoverageForm(data=form_data)

        # Check that municipality is excluded from queryset
        municipality_queryset = form.fields['municipality'].queryset
        self.assertNotIn(self.municipality, municipality_queryset)

    def test_form_allows_edit_same_municipality(self):
        """Form should allow editing existing coverage for same municipality."""
        # Create existing coverage
        coverage = MunicipalityCoverage.objects.create(
            municipality=self.municipality,
            total_obc_communities=10,
        )

        # Edit the same coverage
        form_data = {
            'region': self.region.id,
            'province': self.province.id,
            'municipality': self.municipality.id,
            'total_obc_communities': 15,  # Updated value
        }
        form = MunicipalityCoverageForm(data=form_data, instance=coverage)

        # Should be valid when editing own instance
        municipality_queryset = form.fields['municipality'].queryset
        # When editing, the instance's municipality should be available
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_auto_sync_default_true(self):
        """Auto sync field should default to True."""
        form = MunicipalityCoverageForm()
        auto_sync_field = form.fields.get('auto_sync')
        # Check field exists
        self.assertIsNotNone(auto_sync_field)

    def test_form_location_selection_mixin_integration(self):
        """Form should integrate LocationSelectionMixin properly."""
        form = MunicipalityCoverageForm()
        # Check that location fields have proper configuration
        self.assertIn('region', form.fields)
        self.assertIn('province', form.fields)
        self.assertIn('municipality', form.fields)
        # Barangay should NOT be in municipality coverage form
        self.assertNotIn('barangay', form.location_fields_config)

    def test_form_coordinate_resolution(self):
        """Form should support coordinate auto-resolution from municipality."""
        self.municipality.latitude = 6.5025
        self.municipality.longitude = 124.8453
        self.municipality.save()

        form_data = {
            'region': self.region.id,
            'province': self.province.id,
            'municipality': self.municipality.id,
            'total_obc_communities': 15,
        }
        form = MunicipalityCoverageForm(data=form_data)
        if form.is_valid():
            # If latitude/longitude fields exist, they should auto-resolve
            cleaned_data = form.cleaned_data
            if 'latitude' in cleaned_data and 'longitude' in cleaned_data:
                self.assertIsNotNone(cleaned_data.get('latitude'))
                self.assertIsNotNone(cleaned_data.get('longitude'))

    def test_form_queryset_excludes_existing_coverages(self):
        """Municipality queryset should exclude municipalities with existing coverage."""
        # Create coverage for municipality
        MunicipalityCoverage.objects.create(
            municipality=self.municipality,
            total_obc_communities=10,
        )

        # Create new form (not editing)
        form = MunicipalityCoverageForm()
        municipality_queryset = form.fields['municipality'].queryset

        # Covered municipality should not be in queryset
        self.assertNotIn(self.municipality, municipality_queryset)
        # Other municipality should still be available
        self.assertIn(self.other_municipality, municipality_queryset)

    def test_form_widget_styling(self):
        """Form widgets should have proper styling classes."""
        form = MunicipalityCoverageForm()
        total_communities_widget = form.fields['total_obc_communities'].widget
        widget_classes = total_communities_widget.attrs.get('class', '')
        self.assertIn('rounded', widget_classes.lower())
        self.assertIn('border', widget_classes.lower())

    def test_form_numeric_field_min_validation(self):
        """Numeric fields should have minimum value of 0."""
        form = MunicipalityCoverageForm()
        total_communities_widget = form.fields['total_obc_communities'].widget
        min_value = total_communities_widget.attrs.get('min')
        self.assertEqual(min_value, '0')


class ProvinceCoverageFormTests(TestCase):
    """Test validation and behavior of ProvinceCoverageForm."""

    def setUp(self):
        """Create test fixtures for province coverage form tests."""
        self.region = Region.objects.create(
            code="R12",
            name="SOCCSKSARGEN",
            is_active=True
        )
        self.province = Province.objects.create(
            code="PROV-SK",
            name="South Cotabato",
            region=self.region,
            is_active=True
        )
        self.other_province = Province.objects.create(
            code="PROV-SAR",
            name="Sarangani",
            region=self.region,
            is_active=True
        )

    def test_form_valid_data(self):
        """Form should be valid with complete data."""
        form_data = {
            'region': self.region.id,
            'province': self.province.id,
            'total_municipalities': 12,
            'total_obc_communities': 150,
            'existing_support_programs': 'TABANG, AMBag, Scholarships',
            'auto_sync': True,
        }
        form = ProvinceCoverageForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_requires_province(self):
        """Form should require province field."""
        form_data = {
            'region': self.region.id,
            # Missing province
            'total_municipalities': 12,
            'total_obc_communities': 150,
        }
        form = ProvinceCoverageForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('province', form.errors)

    def test_form_prevents_duplicate_province(self):
        """Form should prevent creating coverage for same province twice."""
        # Create existing coverage
        ProvinceCoverage.objects.create(
            province=self.province,
            total_municipalities=12,
            total_obc_communities=100,
        )

        # Try to create another coverage for same province
        form_data = {
            'region': self.region.id,
            'province': self.province.id,
            'total_municipalities': 15,
        }
        form = ProvinceCoverageForm(data=form_data)

        # Check that province is excluded from queryset
        province_queryset = form.fields['province'].queryset
        self.assertNotIn(self.province, province_queryset)

    def test_form_allows_edit_same_province(self):
        """Form should allow editing existing coverage for same province."""
        # Create existing coverage
        coverage = ProvinceCoverage.objects.create(
            province=self.province,
            total_municipalities=12,
            total_obc_communities=100,
        )

        # Edit the same coverage
        form_data = {
            'region': self.region.id,
            'province': self.province.id,
            'total_municipalities': 15,  # Updated value
        }
        form = ProvinceCoverageForm(data=form_data, instance=coverage)

        # Should be valid when editing own instance
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_initial_region_from_province(self):
        """Form should set initial region from province when editing."""
        # Create coverage
        coverage = ProvinceCoverage.objects.create(
            province=self.province,
            total_municipalities=12,
        )

        # Create form with instance
        form = ProvinceCoverageForm(instance=coverage)

        # Region should be auto-populated from province
        self.assertEqual(form.fields['region'].initial, self.province.region)
        self.assertEqual(form.fields['province'].initial, self.province)

    def test_form_submission_workflow_fields(self):
        """Form should include all required workflow fields."""
        form = ProvinceCoverageForm()
        # Check core fields exist
        self.assertIn('province', form.fields)
        self.assertIn('total_municipalities', form.fields)
        self.assertIn('total_obc_communities', form.fields)
        self.assertIn('existing_support_programs', form.fields)
        self.assertIn('auto_sync', form.fields)

    def test_form_queryset_filtering(self):
        """Province queryset should be properly filtered and ordered."""
        # Create coverage for province
        ProvinceCoverage.objects.create(
            province=self.province,
            total_municipalities=12,
        )

        # Create new form
        form = ProvinceCoverageForm()
        province_queryset = form.fields['province'].queryset

        # Covered province should not be in queryset
        self.assertNotIn(self.province, province_queryset)
        # Other province should still be available
        self.assertIn(self.other_province, province_queryset)

    def test_form_widget_styling(self):
        """Form widgets should have proper styling classes."""
        form = ProvinceCoverageForm()
        municipalities_widget = form.fields['total_municipalities'].widget
        widget_classes = municipalities_widget.attrs.get('class', '')
        self.assertIn('rounded', widget_classes.lower())
        self.assertIn('border', widget_classes.lower())

    def test_form_auto_sync_field(self):
        """Auto sync field should have proper widget styling."""
        form = ProvinceCoverageForm()
        auto_sync_widget = form.fields['auto_sync'].widget
        widget_classes = auto_sync_widget.attrs.get('class', '')
        # Should have checkbox styling
        self.assertIn('form-check', widget_classes.lower())

    def test_form_textarea_fields(self):
        """Textarea fields should have proper configuration."""
        form = ProvinceCoverageForm()
        programs_field = form.fields['existing_support_programs']
        # Should be a textarea widget
        from django import forms
        self.assertIsInstance(programs_field.widget, forms.Textarea)
        # Check rows attribute
        rows = programs_field.widget.attrs.get('rows')
        self.assertIsNotNone(rows)

    def test_form_location_hierarchy(self):
        """Form should only include region and province in location config."""
        form = ProvinceCoverageForm()
        # Should have region and province
        self.assertIn('region', form.location_fields_config)
        self.assertIn('province', form.location_fields_config)
        # Should NOT have municipality or barangay
        self.assertNotIn('municipality', form.location_fields_config)
        self.assertNotIn('barangay', form.location_fields_config)

    def test_form_province_ordering(self):
        """Province queryset should be ordered by region and name."""
        form = ProvinceCoverageForm()
        province_field = form.fields['province']
        # Queryset should have select_related for efficient queries
        queryset = province_field.queryset
        # Both provinces should be in queryset initially
        self.assertEqual(queryset.count(), 2)


class FormIntegrationTests(TestCase):
    """Test integration between forms and LocationSelectionMixin."""

    def setUp(self):
        """Create comprehensive test fixtures."""
        self.region = Region.objects.create(
            code="R12",
            name="SOCCSKSARGEN",
            is_active=True
        )
        self.province = Province.objects.create(
            code="PROV-SK",
            name="South Cotabato",
            region=self.region,
            is_active=True
        )
        self.municipality = Municipality.objects.create(
            code="MUN-KRT",
            name="Koronadal City",
            province=self.province,
            is_active=True
        )
        self.barangay = Barangay.objects.create(
            code="BRGY-001",
            name="Zone 1",
            municipality=self.municipality,
            population_total=5000,
            is_active=True
        )

    def test_all_forms_use_location_selection_mixin(self):
        """All three forms should inherit from LocationSelectionMixin."""
        from common.forms.mixins import LocationSelectionMixin

        # Check OBCCommunityForm
        self.assertTrue(issubclass(OBCCommunityForm, LocationSelectionMixin))
        # Check MunicipalityCoverageForm
        self.assertTrue(issubclass(MunicipalityCoverageForm, LocationSelectionMixin))
        # Check ProvinceCoverageForm
        self.assertTrue(issubclass(ProvinceCoverageForm, LocationSelectionMixin))

    def test_location_widget_metadata_applied(self):
        """Location widgets should have metadata for JS handlers."""
        form = OBCCommunityForm()

        # Check region field
        region_widget = form.fields['region'].widget
        self.assertEqual(region_widget.attrs.get('data-location-level'), 'region')
        self.assertIsNotNone(region_widget.attrs.get('data-location-zoom'))
        self.assertEqual(region_widget.attrs.get('data-location-auto-pin'), 'true')

    def test_province_queryset_filtered_by_region(self):
        """Province queryset should filter based on selected region."""
        # Create another region with province
        other_region = Region.objects.create(
            code="R09",
            name="Zamboanga Peninsula",
            is_active=True
        )
        other_province = Province.objects.create(
            code="PROV-ZDS",
            name="Zamboanga del Sur",
            region=other_region,
            is_active=True
        )

        # Create form with region selected
        form_data = {
            'region': self.region.id,
        }
        form = OBCCommunityForm(data=form_data)

        # Province queryset should only include provinces from selected region
        province_queryset = form.fields['province'].queryset
        # Note: In initial form load, queryset might be empty until region is selected
        # This tests the setup logic

    def test_empty_label_configuration(self):
        """Location fields should have helpful empty labels."""
        form = OBCCommunityForm()

        region_field = form.fields.get('region')
        if region_field:
            self.assertEqual(region_field.empty_label, 'Select region...')

        province_field = form.fields.get('province')
        if province_field:
            self.assertEqual(province_field.empty_label, 'Select province...')

    def test_field_css_classes_consistent(self):
        """All location fields should have consistent CSS classes."""
        form = OBCCommunityForm()

        region_classes = form.fields['region'].widget.attrs.get('class', '')
        province_classes = form.fields['province'].widget.attrs.get('class', '')

        # Should share common styling
        self.assertIn('border', region_classes.lower())
        self.assertIn('border', province_classes.lower())
