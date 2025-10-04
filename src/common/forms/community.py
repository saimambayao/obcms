"""Community data entry forms and field metadata."""

from django import forms
from django.db import models as django_models

from communities.models import (
    CommunityProfileBase,
    MunicipalityCoverage,
    OBCCommunity,
    ProvinceCoverage,
)
from common.models import Region, Province, Municipality

from . import mixins as _location_mixins

LocationSelectionMixin = _location_mixins.LocationSelectionMixin
enhanced_ensure_location_coordinates = (
    _location_mixins.enhanced_ensure_location_coordinates
)


COMMUNITY_PROFILE_FIELDS = [
    field.name
    for field in CommunityProfileBase._meta.get_fields()
    if isinstance(field, django_models.Field)
    and not field.auto_created
    and field.editable
]

COMMUNITY_PROFILE_WIDGETS = {
    "obc_id": forms.TextInput(
        attrs={"class": "form-control", "placeholder": "e.g., R12-SK-PAL-001"}
    ),
    "community_names": forms.TextInput(
        attrs={
            "class": "form-control",
            "placeholder": "Common name(s) used for the community",
        }
    ),
    "purok_sitio": forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Specific Purok/Sitio"}
    ),
    "specific_location": forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Additional location details"}
    ),
    "languages_spoken": forms.TextInput(
        attrs={
            "class": "form-control",
            "placeholder": "Languages spoken (comma-separated)",
        }
    ),
    "other_ethnolinguistic_groups": forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Other groups (comma-separated)"}
    ),
    "community_leader": forms.TextInput(attrs={"class": "form-control"}),
    "leader_contact": forms.TextInput(attrs={"class": "form-control"}),
    "estimated_obc_population": forms.NumberInput(
        attrs={"class": "form-control", "min": "0"}
    ),
    "total_barangay_population": forms.NumberInput(
        attrs={"class": "form-control", "min": "0"}
    ),
    "households": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "families": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "children_0_9": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "adolescents_10_14": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "youth_15_30": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "adults_31_59": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "seniors_60_plus": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "women_count": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "solo_parents_count": forms.NumberInput(
        attrs={"class": "form-control", "min": "0"}
    ),
    "pwd_count": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "farmers_count": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "fisherfolk_count": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "indigenous_peoples_count": forms.NumberInput(
        attrs={"class": "form-control", "min": "0"}
    ),
    "idps_count": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "csos_count": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "associations_count": forms.NumberInput(
        attrs={"class": "form-control", "min": "0"}
    ),
    "unemployed_count": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    "migrants_transients_count": forms.NumberInput(
        attrs={"class": "form-control", "min": "0"}
    ),
    "religious_leaders_count": forms.NumberInput(
        attrs={"class": "form-control", "min": "0"}
    ),
    "established_year": forms.NumberInput(
        attrs={"class": "form-control", "min": "1800", "max": "2030"}
    ),
    "latitude": forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
    "longitude": forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
    "number_of_peoples_organizations": forms.NumberInput(
        attrs={"class": "form-control", "min": "0"}
    ),
    "number_of_cooperatives": forms.NumberInput(
        attrs={"class": "form-control", "min": "0"}
    ),
    "number_of_social_enterprises": forms.NumberInput(
        attrs={"class": "form-control", "min": "0"}
    ),
    "number_of_micro_enterprises": forms.NumberInput(
        attrs={"class": "form-control", "min": "0"}
    ),
    "number_of_unbanked_obc": forms.NumberInput(
        attrs={"class": "form-control", "min": "0"}
    ),
    "settlement_type": forms.Select(attrs={"class": "form-control"}),
    "proximity_to_barmm": forms.Select(attrs={"class": "form-control"}),
    "primary_ethnolinguistic_group": forms.Select(attrs={"class": "form-control"}),
    "estimated_poverty_incidence": forms.Select(attrs={"class": "form-control"}),
    "unemployment_rate": forms.Select(attrs={"class": "form-control"}),
    "financial_access_level": forms.Select(attrs={"class": "form-control"}),
    "relationship_with_lgu": forms.Select(attrs={"class": "form-control"}),
    "access_formal_education": forms.Select(attrs={"class": "form-control"}),
    "access_als": forms.Select(attrs={"class": "form-control"}),
    "access_madrasah": forms.Select(attrs={"class": "form-control"}),
    "access_healthcare": forms.Select(attrs={"class": "form-control"}),
    "access_clean_water": forms.Select(attrs={"class": "form-control"}),
    "access_sanitation": forms.Select(attrs={"class": "form-control"}),
    "access_electricity": forms.Select(attrs={"class": "form-control"}),
    "access_roads_transport": forms.Select(attrs={"class": "form-control"}),
    "access_communication": forms.Select(attrs={"class": "form-control"}),
    "source_document_reference": forms.Textarea(
        attrs={"class": "form-control", "rows": 2}
    ),
    "primary_livelihoods": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    "secondary_livelihoods": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    "land_tenure_issues": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    "brief_historical_background": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "origin_story": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    "migration_history": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    "cultural_practices_traditions": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "religious_affiliation": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    "traditional_leaders_role": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "cultural_preservation_efforts": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "formal_political_representation": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "informal_leadership_structures": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "community_organizations": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "participation_local_governance": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "access_government_info": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "governance_policy_challenges": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "peace_security_priorities": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "specific_project_proposals": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "key_findings_last_assessment": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "assessment_data_sources": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "identified_gaps": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    "key_community_leaders": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    "relevant_lgu_officials": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "notes": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
    "other_vulnerable_sectors": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "other_cultural_facilities": forms.Textarea(
        attrs={"class": "form-control", "rows": 3}
    ),
    "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
}

COMMUNITY_PROFILE_LABELS = {
    "obc_id": "OBC ID",
    "source_document_reference": "Source Document Reference",
    "community_names": "Community Name(s)",
    "purok_sitio": "Puro/Sitio",
    "specific_location": "Specific Location",
    "settlement_type": "Settlement Type",
    "proximity_to_barmm": "Proximity to BARMM",
    "estimated_obc_population": "Estimated OBC Population",
    "total_barangay_population": "Total Population",
    "households": "Households",
    "families": "Families",
    "primary_ethnolinguistic_group": "Primary Ethnolinguistic Group",
    "other_ethnolinguistic_groups": "Other Ethnolinguistic Groups",
    "languages_spoken": "Languages Spoken",
    "women_count": "Number of Women",
    "solo_parents_count": "Number of Solo Parents",
    "pwd_count": "Number of PWDs",
    "farmers_count": "Number of Farmers",
    "fisherfolk_count": "Number of Fisherfolk",
    "indigenous_peoples_count": "Number of Indigenous Peoples",
    "idps_count": "Number of IDPs",
    "csos_count": "Number of CSOs",
    "associations_count": "Number of Associations",
    "unemployed_count": "Number of Unemployed",
    "migrants_transients_count": "Number of Migrants/Transients",
    "other_vulnerable_sectors": "Other Vulnerable Sectors",
    "estimated_poverty_incidence": "Estimated Poverty Incidence",
    "number_of_peoples_organizations": "Number of People's Organizations",
    "number_of_cooperatives": "Number of Cooperatives",
    "number_of_social_enterprises": "Number of Social Enterprises",
    "number_of_micro_enterprises": "Number of Micro-Enterprises",
    "number_of_unbanked_obc": "Number of Unbanked OBC Individuals",
    "financial_access_level": "Access to Banking and Financial Services",
    "access_formal_education": "Access to Formal Education",
    "access_als": "Access to ALS",
    "access_madrasah": "Access to Madrasah",
    "access_healthcare": "Access to Healthcare",
    "access_clean_water": "Access to Clean Water",
    "access_sanitation": "Access to Sanitation (Waste Management)",
    "access_electricity": "Access to Electricity",
    "access_roads_transport": "Access to Roads/Transport",
    "access_communication": "Access to Communication",
    "religious_leaders_count": "Number of Ulama / Religious Leaders",
    "brief_historical_background": "Brief Historical Background",
    "established_year": "Established Year",
    "origin_story": "Origin Story",
    "migration_history": "Migration History",
    "cultural_practices_traditions": "Cultural Practices & Traditions",
    "religious_affiliation": "Religious Affiliation",
    "traditional_leaders_role": "Role of Traditional Leaders",
    "cultural_preservation_efforts": "Cultural Preservation Efforts",
    "mosques_count": "Number of Mosques",
    "madrasah_count": "Number of Madrasah",
    "asatidz_count": "Number of Asatidz",
    "other_cultural_facilities": "Other Cultural Facilities / Artefacts / Assets",
    "formal_political_representation": "Formal Political Representation",
    "informal_leadership_structures": "Informal Leadership Structures",
    "community_organizations": "Community Organizations",
    "relationship_with_lgu": "Relationship with LGU",
    "participation_local_governance": "Participation in Local Governance",
    "access_government_info": "Access to Government Information",
    "governance_policy_challenges": "Governance & Policy Challenges",
    "access_public_services_challenges": "Access to Public Services Challenges",
    "land_ownership_security_issues": "Land Ownership & Security Issues",
    "economic_disparities": "Economic Disparities",
    "social_instability_conflict": "Social Instability / Conflict",
    "cultural_miscommunication": "Cultural Miscommunication",
    "gender_inequality_issues": "Gender Inequality Issues",
    "substance_abuse_issues": "Substance Abuse Issues",
    "investment_scam_issues": "Investment Scam Issues",
    "environmental_degradation": "Environmental Degradation",
    "other_challenges": "Other Challenges",
    "challenges_impact": "Impact of Challenges",
    "key_aspirations": "Key Aspirations",
    "infrastructure_priorities": "Infrastructure Priorities",
    "livelihood_program_priorities": "Livelihood Program Priorities",
    "education_priorities": "Education Priorities",
    "healthcare_priorities": "Healthcare Priorities",
    "cultural_preservation_priorities": "Cultural Preservation Priorities",
    "peace_security_priorities": "Peace & Security Priorities",
    "specific_project_proposals": "Specific Project Proposals",
    "unemployment_rate": "Unemployment Rate",
    "needs_assessment_date": "Needs Assessment Date",
    "key_findings_last_assessment": "Key Findings (Last Assessment)",
    "assessment_data_sources": "Assessment Data Sources",
    "identified_gaps": "Identified Gaps",
    "key_community_leaders": "Key Community Leaders",
    "relevant_lgu_officials": "Relevant LGU Officials",
    "community_leader": "Primary Community Leader",
    "leader_contact": "Community Leader Contact",
    "is_active": "Active Record",
    "notes": "Additional Notes",
}


class MunicipalityCoverageForm(LocationSelectionMixin, forms.ModelForm):
    """Form for recording municipalities or cities with Bangsamoro presence."""

    # Configure location fields - barangay not required for municipality coverage
    location_fields_config = {
        "region": {"required": True, "level": "region", "zoom": 7},
        "province": {"required": True, "level": "province", "zoom": 9},
        "municipality": {"required": True, "level": "municipality", "zoom": 12},
    }

    region = forms.ModelChoiceField(
        queryset=Region.objects.filter(is_active=True).order_by("code", "name"),
        required=True,
        label="Region",
    )
    province = forms.ModelChoiceField(
        queryset=Province.objects.none(),
        required=True,
        label="Province",
    )

    class Meta:
        model = MunicipalityCoverage
        fields = (
            "municipality",
            "total_obc_communities",
            "existing_support_programs",
            "auto_sync",
            *COMMUNITY_PROFILE_FIELDS,
        )
        widgets = {
            "total_obc_communities": forms.NumberInput(
                attrs={
                    "class": "block w-full py-3 px-4 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500",
                    "min": "0",
                }
            ),
            "existing_support_programs": forms.Textarea(
                attrs={
                    "class": "block w-full py-3 px-4 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500",
                    "rows": 3,
                }
            ),
            "auto_sync": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                }
            ),
            **COMMUNITY_PROFILE_WIDGETS,
        }
        labels = {
            "region": "Region",
            "province": "Province",
            "municipality": "Municipality / City",
            "total_obc_communities": "Identified Bangsamoro Communities",
            "existing_support_programs": "Existing Support Programs",
            "auto_sync": "Automatically sync totals from barangay communities",
            **COMMUNITY_PROFILE_LABELS,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Additional logic specific to municipality coverage
        municipality_field = self.fields.get("municipality")
        if municipality_field:
            # Exclude municipalities that already have coverage
            existing_coverage_ids = set(
                MunicipalityCoverage.objects.values_list("municipality_id", flat=True)
            )
            if self.instance and self.instance.pk:
                existing_coverage_ids.discard(self.instance.municipality_id)

            if existing_coverage_ids:
                current_queryset = municipality_field.queryset
                municipality_field.queryset = current_queryset.exclude(
                    pk__in=existing_coverage_ids
                )


class ProvinceCoverageForm(LocationSelectionMixin, forms.ModelForm):
    """Form for recording province-level Bangsamoro coverage."""

    location_fields_config = {
        "region": {"required": True, "level": "region", "zoom": 7},
        "province": {"required": True, "level": "province", "zoom": 9},
    }

    region = forms.ModelChoiceField(
        queryset=Region.objects.filter(is_active=True).order_by("code", "name"),
        required=True,
        label="Region",
    )
    province = forms.ModelChoiceField(
        queryset=Province.objects.none(),
        required=True,
        label="Province",
    )

    class Meta:
        model = ProvinceCoverage
        fields = (
            "province",
            "total_municipalities",
            "total_obc_communities",
            "existing_support_programs",
            "auto_sync",
            *COMMUNITY_PROFILE_FIELDS,
        )
        widgets = {
            "total_municipalities": forms.NumberInput(
                attrs={
                    "class": "block w-full py-3 px-4 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500",
                    "min": "0",
                }
            ),
            "total_obc_communities": forms.NumberInput(
                attrs={
                    "class": "block w-full py-3 px-4 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500",
                    "min": "0",
                }
            ),
            "existing_support_programs": forms.Textarea(
                attrs={
                    "class": "block w-full py-3 px-4 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500",
                    "rows": 3,
                }
            ),
            "auto_sync": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                }
            ),
            **COMMUNITY_PROFILE_WIDGETS,
        }
        labels = {
            "region": "Region",
            "province": "Province",
            "total_municipalities": "Municipalities / Cities Tracked",
            "total_obc_communities": "Barangay OBCs (aggregated)",
            "existing_support_programs": "Existing Support Programs",
            "auto_sync": "Automatically sync totals from municipal coverage",
            **COMMUNITY_PROFILE_LABELS,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        province_field = self.fields.get("province")
        if province_field:
            province_choices = Province.objects.select_related("region").order_by(
                "region__name", "name"
            )
            province_field.queryset = province_choices

            existing_coverage_ids = set(
                ProvinceCoverage.objects.values_list("province_id", flat=True)
            )
            if self.instance and self.instance.pk:
                existing_coverage_ids.discard(self.instance.province_id)

            if existing_coverage_ids:
                province_field.queryset = province_field.queryset.exclude(
                    pk__in=existing_coverage_ids
                )

        if self.instance and self.instance.pk:
            self.fields["region"].initial = self.instance.province.region
            self.fields["province"].initial = self.instance.province


class OBCCommunityForm(LocationSelectionMixin, forms.ModelForm):
    """Comprehensive form for creating or editing OBC communities."""

    # Configure location fields - all levels including barangay
    location_fields_config = {
        "region": {"required": True, "level": "region", "zoom": 7},
        "province": {"required": True, "level": "province", "zoom": 9},
        "municipality": {"required": True, "level": "municipality", "zoom": 12},
        "barangay": {"required": True, "level": "barangay", "zoom": 15},
    }

    region = forms.ModelChoiceField(
        queryset=Region.objects.filter(is_active=True).order_by("code", "name"),
        required=True,
        label="Region",
    )
    province = forms.ModelChoiceField(
        queryset=Province.objects.none(),
        required=True,
        label="Province",
    )
    municipality = forms.ModelChoiceField(
        queryset=Municipality.objects.none(),
        required=True,
        label="Municipality / City",
    )

    class Meta:
        model = OBCCommunity
        fields = ["barangay", *COMMUNITY_PROFILE_FIELDS]
        widgets = {
            **COMMUNITY_PROFILE_WIDGETS,
        }
        labels = {
            "region": "Region",
            "province": "Province",
            "municipality": "Municipality / City",
            "barangay": "Barangay",
            **COMMUNITY_PROFILE_LABELS,
        }

    def clean(self):
        """Validate that OBC population does not exceed total barangay population."""
        cleaned_data = super().clean()
        estimated_obc_population = cleaned_data.get("estimated_obc_population")
        total_barangay_population = cleaned_data.get("total_barangay_population")

        # Only validate if both values are provided
        if (
            estimated_obc_population is not None
            and total_barangay_population is not None
            and estimated_obc_population > 0
            and total_barangay_population > 0
        ):
            if estimated_obc_population > total_barangay_population:
                raise forms.ValidationError(
                    {
                        "estimated_obc_population": "Estimated OBC Population cannot exceed Total Barangay Population. "
                        f"The total barangay population is {total_barangay_population:,}, "
                        f"but you entered an OBC population of {estimated_obc_population:,}."
                    }
                )

        return cleaned_data


__all__ = [
    "COMMUNITY_PROFILE_FIELDS",
    "COMMUNITY_PROFILE_WIDGETS",
    "COMMUNITY_PROFILE_LABELS",
    "MunicipalityCoverageForm",
    "ProvinceCoverageForm",
    "OBCCommunityForm",
]
