from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from common.models import Barangay, Municipality, Province, Region

User = get_user_model()


AGGREGATED_NUMERIC_FIELDS = [
    "estimated_obc_population",
    "total_barangay_population",
    "households",
    "families",
    "children_0_9",
    "adolescents_10_14",
    "youth_15_30",
    "adults_31_59",
    "seniors_60_plus",
    "women_count",
    "solo_parents_count",
    "pwd_count",
    "farmers_count",
    "fisherfolk_count",
    "unemployed_count",
    "indigenous_peoples_count",
    "idps_count",
    "migrants_transients_count",
    "csos_count",
    "associations_count",
    "number_of_peoples_organizations",
    "number_of_cooperatives",
    "number_of_social_enterprises",
    "number_of_micro_enterprises",
    "number_of_unbanked_obc",
    "mosques_count",
    "madrasah_count",
    "asatidz_count",
    "religious_leaders_count",
]


class ActiveCommunityManager(models.Manager):
    """Default manager that hides soft-deleted records."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class CommunityProfileBase(models.Model):
    """Shared socio-demographic profile fields for communities and municipalities."""

    SETTLEMENT_TYPE_CHOICES = [
        ("village", "Village"),
        ("subdivision", "Subdivision"),
        ("sitio", "Sitio"),
        ("purok", "Purok"),
        ("compound", "Compound"),
        ("dispersed", "Dispersed Settlement"),
    ]

    # I. IDENTIFICATION AND LOCATION
    # Unique identifier for the specific OBC
    obc_id = models.CharField(
        max_length=50,
        default="",
        blank=True,
        help_text="Unique identifier for the OBC (e.g., R12-SK-PAL-001)",
    )

    # Source document reference
    source_document_reference = models.TextField(
        blank=True,
        help_text="Document source and page number (e.g., 'OBC MANA Region 12, p.7')",
    )

    # Community name(s)
    community_names = models.TextField(
        default="",
        blank=True,
        help_text="Common name(s) used to refer to the community (comma-separated)",
    )

    purok_sitio = models.CharField(
        max_length=255, blank=True, help_text="Specific Purok/Sitio within the barangay"
    )

    specific_location = models.CharField(
        max_length=255, blank=True, help_text="Additional specific location details"
    )

    settlement_type = models.CharField(
        max_length=20,
        choices=SETTLEMENT_TYPE_CHOICES,
        default="village",
        help_text="Type of settlement",
    )

    # Geographic coordinates for mapping
    latitude = models.FloatField(
        null=True, blank=True, help_text="Latitude coordinate for mapping"
    )

    longitude = models.FloatField(
        null=True, blank=True, help_text="Longitude coordinate for mapping"
    )

    # Proximity to BARMM
    PROXIMITY_CHOICES = [
        ("adjacent", "Adjacent to BARMM"),
        ("near", "Near BARMM"),
        ("distant", "Distant from BARMM"),
    ]

    proximity_to_barmm = models.CharField(
        max_length=20,
        choices=PROXIMITY_CHOICES,
        blank=True,
        help_text="Proximity to BARMM boundaries",
    )

    # II. DEMOGRAPHIC PROFILE
    # Population data
    estimated_obc_population = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of individuals identified as part of the OBC",
    )

    total_barangay_population = models.PositiveIntegerField(
        null=True, blank=True, help_text="Total barangay population for context"
    )

    households = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of households in the community"
    )

    families = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of families in the community"
    )

    # Primary ethnolinguistic groups
    ETHNOLINGUISTIC_CHOICES = [
        ("badjao", "Badjao"),
        ("iranun", "Iranun"),
        ("jama_mapun", "Jama Mapun"),
        ("kagan_kalagan", "Kagan/Kalagan"),
        ("kolibugan", "Kolibugan"),
        ("maguindanaon", "Maguindanaon"),
        ("meranaw", "Meranaw"),
        ("molbog", "Molbog"),
        ("palawani", "Palawani"),
        ("sama", "Sama"),
        ("sangil", "Sangil"),
        ("tausug", "Tausug"),
        ("yakan", "Yakan"),
        ("other", "Other"),
    ]

    primary_ethnolinguistic_group = models.CharField(
        max_length=50,
        choices=ETHNOLINGUISTIC_CHOICES,
        blank=True,
        help_text="Primary ethnolinguistic group",
    )

    other_ethnolinguistic_groups = models.TextField(
        blank=True, help_text="Other ethnolinguistic groups present (comma-separated)"
    )

    languages_spoken = models.TextField(
        blank=True, help_text="Languages spoken in the community (comma-separated)"
    )

    # Age Demographics
    children_0_9 = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of children aged 0-9"
    )

    adolescents_10_14 = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of adolescents aged 10-14"
    )

    youth_15_30 = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of youth aged 15-30"
    )

    adults_31_59 = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of adults aged 31-59"
    )

    seniors_60_plus = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of seniors aged 60 and above"
    )

    # Vulnerable sectors
    women_count = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of women in the community"
    )

    solo_parents_count = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of solo parents"
    )

    pwd_count = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of Persons with Disabilities (PWDs)"
    )

    farmers_count = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of farmers"
    )

    fisherfolk_count = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of fisherfolk"
    )

    indigenous_peoples_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of Indigenous Peoples (if distinct within OBC)",
    )

    idps_count = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of Internally Displaced Persons (IDPs)"
    )

    csos_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of Civil Society Organizations (CSOs) in the community",
    )

    associations_count = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of Associations in the community"
    )

    unemployed_count = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of unemployed individuals"
    )

    migrants_transients_count = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of migrants/transients"
    )

    other_vulnerable_sectors = models.TextField(
        blank=True, help_text="Other vulnerable sectors not listed above"
    )

    # III. SOCIO-ECONOMIC PROFILE
    # Primary livelihoods
    primary_livelihoods = models.TextField(
        blank=True,
        help_text="Primary livelihoods (e.g., Rice Farming, Coconut Production, Fishing)",
    )

    secondary_livelihoods = models.TextField(
        blank=True, help_text="Secondary livelihoods in the community"
    )

    # Poverty and economic status
    POVERTY_INCIDENCE_CHOICES = [
        ("unknown", "Unknown"),
        ("very_low", "Very Low (<10%)"),
        ("low", "Low (10-20%)"),
        ("moderate", "Moderate (20-30%)"),
        ("high", "High (30-40%)"),
        ("very_high", "Very High (40-50%)"),
        ("extremely_high", "Extremely High (>50%)"),
    ]

    estimated_poverty_incidence = models.CharField(
        max_length=20,
        choices=POVERTY_INCIDENCE_CHOICES,
        blank=True,
        help_text="Estimated poverty incidence within OBC",
    )

    # Access to basic services (rating system)
    ACCESS_RATING_CHOICES = [
        ("excellent", "Excellent"),
        ("good", "Good"),
        ("fair", "Fair"),
        ("poor", "Poor"),
        ("none", "None"),
    ]

    access_formal_education = models.CharField(
        max_length=20,
        choices=ACCESS_RATING_CHOICES,
        blank=True,
        help_text="Access to formal schools",
    )

    access_als = models.CharField(
        max_length=20,
        choices=ACCESS_RATING_CHOICES,
        blank=True,
        help_text="Access to Alternative Learning System (ALS)",
    )

    access_madrasah = models.CharField(
        max_length=20,
        choices=ACCESS_RATING_CHOICES,
        blank=True,
        help_text="Access to Madrasah/Islamic education",
    )

    access_healthcare = models.CharField(
        max_length=20,
        choices=ACCESS_RATING_CHOICES,
        blank=True,
        help_text="Access to healthcare facilities",
    )

    access_clean_water = models.CharField(
        max_length=20,
        choices=ACCESS_RATING_CHOICES,
        blank=True,
        help_text="Access to clean water supply",
    )

    access_sanitation = models.CharField(
        max_length=20,
        choices=ACCESS_RATING_CHOICES,
        blank=True,
        help_text="Access to sanitation facilities",
    )

    access_electricity = models.CharField(
        max_length=20,
        choices=ACCESS_RATING_CHOICES,
        blank=True,
        help_text="Access to electricity",
    )

    access_roads_transport = models.CharField(
        max_length=20,
        choices=ACCESS_RATING_CHOICES,
        blank=True,
        help_text="Access to roads and transportation",
    )

    access_communication = models.CharField(
        max_length=20,
        choices=ACCESS_RATING_CHOICES,
        blank=True,
        help_text="Access to communication (mobile/internet)",
    )

    # Land tenure and economic issues
    land_tenure_issues = models.TextField(
        blank=True,
        help_text="Land tenure issues (lack of titles, disputes, ancestral domain claims)",
    )

    number_of_peoples_organizations = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of People's Organizations in the community",
    )

    number_of_cooperatives = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of Cooperatives in the community"
    )

    number_of_social_enterprises = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of Social Enterprises in the community"
    )

    number_of_micro_enterprises = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of Micro-Enterprises (such as Sari-Sari Stores, etc.)",
    )

    number_of_unbanked_obc = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of OBC Individuals without Access to Financial Services (Unbanked)",
    )

    financial_access_level = models.CharField(
        max_length=20,
        choices=ACCESS_RATING_CHOICES,
        blank=True,
        help_text="Access to banking and financial services",
    )

    # IV. CULTURAL AND HISTORICAL CONTEXT
    # Historical background
    brief_historical_background = models.TextField(
        blank=True, help_text="Key historical narratives of the community in the area"
    )

    established_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1800), MaxValueValidator(2030)],
        help_text="Year the community was established",
    )

    origin_story = models.TextField(
        blank=True, help_text="Story of how the community was established"
    )

    migration_history = models.TextField(
        blank=True, help_text="Migration history and patterns"
    )

    # Cultural practices and traditions
    cultural_practices_traditions = models.TextField(
        blank=True, help_text="Notable customs, traditions, festivals"
    )

    religious_affiliation = models.TextField(
        blank=True, help_text="Religious affiliation and specific practices"
    )

    traditional_leaders_role = models.TextField(
        blank=True, help_text="Role of traditional leaders (Imams, Elders, Chieftains)"
    )

    cultural_preservation_efforts = models.TextField(
        blank=True, help_text="Existing cultural preservation efforts"
    )

    # Religious and cultural facilities
    mosques_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of mosques accessible to the community",
    )

    madrasah_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of madrasah/Islamic schools accessible to the community",
    )

    asatidz_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of Asatidz (Islamic teachers/instructors)",
    )

    religious_leaders_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of Ulama or religious leaders (Imam, Ustadz, etc.)",
    )

    other_cultural_facilities = models.TextField(
        blank=True,
        help_text="Other cultural facilities, artefacts, or assets not listed above",
    )

    # V. GOVERNANCE AND COMMUNITY LEADERSHIP
    # Political representation and leadership
    formal_political_representation = models.TextField(
        blank=True, help_text="Presence in Barangay Council, LGU representation"
    )

    informal_leadership_structures = models.TextField(
        blank=True, help_text="Description of informal leadership structures"
    )

    community_organizations = models.TextField(
        blank=True,
        help_text="Community organizations/associations (name, focus, contact)",
    )

    RELATIONSHIP_LGU_CHOICES = [
        ("collaborative", "Collaborative"),
        ("strained", "Strained"),
        ("minimal", "Minimal"),
        ("good", "Good"),
        ("excellent", "Excellent"),
    ]

    relationship_with_lgu = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_LGU_CHOICES,
        blank=True,
        help_text="Relationship with LGU",
    )

    participation_local_governance = models.TextField(
        blank=True, help_text="Participation in local governance and planning"
    )

    access_government_info = models.TextField(
        blank=True, help_text="Access to information on government programs"
    )

    # VI. CHALLENGES AND BARRIERS
    # Governance and policy challenges
    governance_policy_challenges = models.TextField(
        blank=True, help_text="Marginalization, lack of representation issues"
    )

    access_public_services_challenges = models.TextField(
        blank=True,
        help_text="Challenges in accessing education, health, infrastructure",
    )

    land_ownership_security_issues = models.TextField(
        blank=True, help_text="Land ownership and security challenges"
    )

    economic_disparities = models.TextField(
        blank=True, help_text="Poverty, limited employment, economic challenges"
    )

    social_instability_conflict = models.TextField(
        blank=True, help_text="Rido, security issues, social conflicts"
    )

    cultural_miscommunication = models.TextField(
        blank=True, help_text="Cultural miscommunication challenges"
    )

    gender_inequality_issues = models.TextField(
        blank=True, help_text="Gender inequality, early marriage issues"
    )

    substance_abuse_issues = models.TextField(
        blank=True, help_text="Drug use, substance abuse issues"
    )

    investment_scam_issues = models.TextField(
        blank=True, help_text="Investment scams and financial fraud issues"
    )

    environmental_degradation = models.TextField(
        blank=True, help_text="Mining, illegal fishing, environmental issues"
    )

    other_challenges = models.TextField(
        blank=True,
        help_text="Other specific challenges (ISAL education, Halal industry, etc.)",
    )

    challenges_impact = models.TextField(
        blank=True, help_text="Impact of these challenges on the community"
    )

    # VII. COMMUNITY ASPIRATIONS AND DEVELOPMENT PRIORITIES
    key_aspirations = models.TextField(
        blank=True,
        help_text="Key community aspirations (poverty eradication, improved services, etc.)",
    )

    infrastructure_priorities = models.TextField(
        blank=True,
        help_text="Infrastructure development priorities (roads, water, health, schools)",
    )

    livelihood_program_priorities = models.TextField(
        blank=True,
        help_text="Livelihood program priorities (agriculture, fisheries, SMEs, Halal, ecotourism)",
    )

    education_priorities = models.TextField(
        blank=True,
        help_text="Education priorities (scholarships, skills training, Madrasah support)",
    )

    healthcare_priorities = models.TextField(
        blank=True, help_text="Healthcare access priorities"
    )

    cultural_preservation_priorities = models.TextField(
        blank=True, help_text="Cultural preservation initiative priorities"
    )

    peace_security_priorities = models.TextField(
        blank=True, help_text="Peace and order/conflict resolution priorities"
    )

    specific_project_proposals = models.TextField(
        blank=True, help_text="Specific project proposals/ideas from the community"
    )

    # Employment context
    UNEMPLOYMENT_RATE_CHOICES = [
        ("", "Select..."),
        ("unknown", "Unknown"),
        ("very_low", "Very Low (<10%)"),
        ("low", "Low (10-20%)"),
        ("moderate", "Moderate (20-30%)"),
        ("high", "High (30-40%)"),
        ("very_high", "Very High (40-50%)"),
        ("extremely_high", "Extremely High (>50%)"),
    ]

    unemployment_rate = models.CharField(
        max_length=20,
        choices=UNEMPLOYMENT_RATE_CHOICES,
        blank=True,
        help_text="Estimated unemployment rate within the community",
    )

    # X. NEEDS ASSESSMENT DATA
    needs_assessment_date = models.DateField(
        null=True, blank=True, help_text="Date of last needs assessment"
    )

    key_findings_last_assessment = models.TextField(
        blank=True, help_text="Key findings from last needs assessment"
    )

    assessment_data_sources = models.TextField(
        blank=True,
        help_text="Data sources (community consultations, surveys, LGU data)",
    )

    identified_gaps = models.TextField(
        blank=True, help_text="Identified gaps based on assessments"
    )

    # XI. CONTACT INFORMATION
    key_community_leaders = models.TextField(
        blank=True,
        help_text="Key community leader(s)/focal person(s) with contact details",
    )

    relevant_lgu_officials = models.TextField(
        blank=True, help_text="Relevant LGU official(s) and their contact information"
    )

    # Legacy fields for backward compatibility
    community_leader = models.CharField(
        max_length=255, blank=True, help_text="Name of the primary community leader"
    )

    leader_contact = models.CharField(
        max_length=100, blank=True, help_text="Contact information for community leader"
    )

    # Administrative
    is_active = models.BooleanField(
        default=True, help_text="Whether this community record is active"
    )

    notes = models.TextField(
        blank=True, help_text="Additional notes about the community"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_deleted = models.BooleanField(
        default=False,
        help_text="Indicates whether this record has been archived instead of fully removed.",
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when this record was archived for removal.",
    )
    deleted_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="deleted_%(class)ss",
        help_text="User who archived this record for deletion review.",
    )

    class Meta:
        abstract = True

    @property
    def total_age_demographics(self):
        """Calculate total from age demographics."""
        total = 0
        if self.children_0_9:
            total += self.children_0_9
        if self.adolescents_10_14:
            total += self.adolescents_10_14
        if self.youth_15_30:
            total += self.youth_15_30
        if self.adults_31_59:
            total += self.adults_31_59
        if self.seniors_60_plus:
            total += self.seniors_60_plus
        return total

    @property
    def average_household_size(self):
        """Calculate average household size."""
        if self.households and self.estimated_obc_population:
            return round(self.estimated_obc_population / self.households, 1)
        return None

    @property
    def percentage_obc_in_barangay(self):
        """Calculate percentage of OBCs in barangay."""
        if self.estimated_obc_population and self.total_barangay_population:
            return round(
                (self.estimated_obc_population / self.total_barangay_population) * 100,
                2,
            )
        return None

    @property
    def coordinates(self):
        """Return coordinates as [longitude, latitude] for GeoJSON."""
        if self.latitude and self.longitude:
            return [self.longitude, self.latitude]
        return None

    def soft_delete(self, *, user=None):
        """Mark the record as deleted without removing it from the database."""
        if self.is_deleted:
            return
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if user is not None:
            self.deleted_by = user
        self.save(
            update_fields=["is_deleted", "deleted_at", "deleted_by", "updated_at"]
        )

    def restore(self):
        """Reinstate a soft-deleted record."""
        if not self.is_deleted:
            return
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])


class OBCCommunity(CommunityProfileBase):
    """
    Enhanced model for Other Bangsamoro Community profiles.
    Represents OBC settlements outside BARMM with comprehensive data fields
    based on the OBC Database specifications for Regions 9 and 12.
    """

    objects = ActiveCommunityManager()
    all_objects = models.Manager()

    # Legacy compatibility fields retained for existing workflows/tests
    name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Primary community name (legacy field retained for compatibility)",
    )

    population = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Total population of the community (legacy field retained for compatibility)",
    )

    primary_language = models.CharField(
        max_length=100,
        blank=True,
        help_text="Primary language spoken in the community (legacy field retained for compatibility)",
    )

    other_languages = models.CharField(
        max_length=255,
        blank=True,
        help_text="Other languages spoken (comma-separated, legacy field retained for compatibility)",
    )

    cultural_background = models.TextField(
        blank=True,
        help_text="Cultural background and traditions (legacy field retained for compatibility)",
    )

    religious_practices = models.TextField(
        blank=True,
        help_text="Religious practices and observances (legacy field retained for compatibility)",
    )

    priority_needs = models.TextField(
        blank=True,
        help_text="Priority needs identified for the community (legacy field retained for compatibility)",
    )

    # Geographic location for community-level entries
    barangay = models.ForeignKey(
        Barangay,
        on_delete=models.CASCADE,
        related_name="obc_communities",
        help_text="Barangay where the community is located",
    )

    class Meta:
        db_table = "communities_obc_community"
        ordering = [
            "barangay__municipality__province__region__code",
            "barangay__municipality__province__name",
            "barangay__municipality__name",
            "barangay__name",
        ]
        verbose_name = "OBC Community"
        verbose_name_plural = "OBC Communities"
        constraints = [
            models.UniqueConstraint(
                fields=["barangay"],
                name="unique_obccommunity_per_barangay",
            )
        ]

    def __str__(self):
        location = (
            f"{self.barangay.name}, {self.barangay.municipality.name}, {self.barangay.province.name}"
            if self.barangay_id
            else ""
        )
        if self.display_name and location:
            return f"{self.display_name} - {location}"
        return self.display_name or location

    @property
    def display_name(self):
        """Return the preferred display label for the community."""
        if self.name:
            return self.name.strip()
        if self.community_names:
            names = [n.strip() for n in self.community_names.split(",") if n.strip()]
            if names:
                return names[0]
        if self.barangay_id:
            return self.barangay.name
        return ""

    def save(self, *args, **kwargs):
        """Keep derived legacy fields in sync with expanded profile data."""
        # Ensure community_names always includes the legacy name as the first entry
        if self.name:
            existing_names = [
                n.strip() for n in (self.community_names or "").split(",") if n.strip()
            ]
            name_clean = self.name.strip()
            if existing_names:
                existing_names = [name_clean] + [
                    n for n in existing_names if n.lower() != name_clean.lower()
                ]
            else:
                existing_names = [name_clean]
            self.community_names = ", ".join(existing_names)

        # Ensure languages_spoken mirrors primary/other language legacy fields
        language_entries = []
        if self.primary_language:
            language_entries.append(self.primary_language.strip())
        if self.other_languages:
            language_entries.extend(
                [
                    lang.strip()
                    for lang in self.other_languages.split(",")
                    if lang.strip()
                ]
            )
        if language_entries:
            seen = set()
            normalised = []
            for lang in language_entries:
                key = lang.lower()
                if key not in seen:
                    seen.add(key)
                    normalised.append(lang)
            self.languages_spoken = ", ".join(normalised)

        super().save(*args, **kwargs)

    @property
    def full_location(self):
        """Return the full administrative location path."""
        location = f"{self.barangay.full_path}"
        if self.specific_location:
            location += f" > {self.specific_location}"
        return location

    @property
    def region(self):
        """Return the region this community belongs to."""
        return self.barangay.region

    @property
    def province(self):
        """Return the province this community belongs to."""
        return self.barangay.province

    @property
    def municipality(self):
        """Return the municipality this community belongs to."""
        return self.barangay.municipality


class CommunityLivelihood(models.Model):
    """
    Model for tracking different livelihood activities within OBC communities.
    """

    LIVELIHOOD_CATEGORIES = [
        ("agriculture", "Agriculture"),
        ("fishing", "Fishing"),
        ("livestock", "Livestock"),
        ("trade", "Trade/Business"),
        ("services", "Services"),
        ("handicrafts", "Handicrafts"),
        ("transportation", "Transportation"),
        ("construction", "Construction"),
        ("government", "Government Employment"),
        ("private_employment", "Private Employment"),
        ("other", "Other"),
    ]

    community = models.ForeignKey(
        OBCCommunity, on_delete=models.CASCADE, related_name="livelihoods"
    )

    livelihood_type = models.CharField(
        max_length=50,
        choices=LIVELIHOOD_CATEGORIES,
        help_text="Type of livelihood activity",
    )

    specific_activity = models.CharField(
        max_length=255,
        help_text="Specific livelihood activity (e.g., rice farming, tricycle driving)",
    )

    description = models.TextField(
        blank=True, help_text="Detailed description of the livelihood activity"
    )

    households_involved = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of households involved in this livelihood",
    )

    percentage_of_community = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage of community involved in this livelihood",
    )

    is_primary_livelihood = models.BooleanField(
        default=False,
        help_text="Whether this is the primary livelihood for the community",
    )

    seasonal = models.BooleanField(
        default=False, help_text="Whether this livelihood is seasonal"
    )

    income_level = models.CharField(
        max_length=20,
        choices=[
            ("very_low", "Very Low"),
            ("low", "Low"),
            ("moderate", "Moderate"),
            ("high", "High"),
            ("very_high", "Very High"),
        ],
        blank=True,
        help_text="General income level from this livelihood",
    )

    challenges = models.TextField(
        blank=True, help_text="Challenges faced in this livelihood activity"
    )

    opportunities = models.TextField(
        blank=True, help_text="Opportunities for improvement or expansion"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "communities_livelihood"
        ordering = [
            "community__barangay__name",
            "-is_primary_livelihood",
            "livelihood_type",
        ]
        verbose_name = "Community Livelihood"
        verbose_name_plural = "Community Livelihoods"

    def __str__(self):
        primary = " (Primary)" if self.is_primary_livelihood else ""
        return f"{self.specific_activity} - {self.community.barangay.name}{primary}"


class CommunityInfrastructure(models.Model):
    """
    Model for tracking infrastructure availability in OBC communities.
    """

    INFRASTRUCTURE_TYPES = [
        ("water", "Water Supply"),
        ("electricity", "Electricity"),
        ("roads", "Roads/Transportation"),
        ("communication", "Communication/Internet"),
        ("health", "Health Facilities"),
        ("education", "Education Facilities"),
        ("religious", "Religious Facilities"),
        ("market", "Market/Trading Post"),
        ("waste", "Waste Management"),
        ("drainage", "Drainage System"),
    ]

    AVAILABILITY_STATUS = [
        ("available", "Available"),
        ("limited", "Limited"),
        ("poor", "Poor Quality"),
        ("none", "Not Available"),
        ("planned", "Planned/Proposed"),
    ]

    community = models.ForeignKey(
        OBCCommunity, on_delete=models.CASCADE, related_name="infrastructure"
    )

    infrastructure_type = models.CharField(
        max_length=50, choices=INFRASTRUCTURE_TYPES, help_text="Type of infrastructure"
    )

    availability_status = models.CharField(
        max_length=20,
        choices=AVAILABILITY_STATUS,
        help_text="Current availability status",
    )

    description = models.TextField(
        blank=True, help_text="Detailed description of the infrastructure"
    )

    coverage_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage of community with access",
    )

    condition = models.CharField(
        max_length=20,
        choices=[
            ("excellent", "Excellent"),
            ("good", "Good"),
            ("fair", "Fair"),
            ("poor", "Poor"),
            ("very_poor", "Very Poor"),
        ],
        blank=True,
        help_text="Physical condition of the infrastructure",
    )

    priority_for_improvement = models.CharField(
        max_length=20,
        choices=[
            ("critical", "Critical"),
            ("high", "High"),
            ("medium", "Medium"),
            ("low", "Low"),
        ],
        default="medium",
        help_text="Priority level for improvement",
    )

    notes = models.TextField(
        blank=True, help_text="Additional notes about the infrastructure"
    )

    last_assessed = models.DateField(
        null=True,
        blank=True,
        help_text="Date when this infrastructure was last assessed",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "communities_infrastructure"
        ordering = ["community__barangay__name", "infrastructure_type"]
        verbose_name = "Community Infrastructure"
        verbose_name_plural = "Community Infrastructure"
        unique_together = ["community", "infrastructure_type"]

    def __str__(self):
        return f"{self.get_infrastructure_type_display()} - {self.community.barangay.name} ({self.get_availability_status_display()})"


class Stakeholder(models.Model):
    """
    Model for tracking key stakeholders in OBC communities including
    community leaders, religious figures, and teachers.
    """

    STAKEHOLDER_TYPES = [
        ("community_leader", "Community Leader"),
        ("barangay_captain", "Barangay Captain"),
        ("tribal_leader", "Tribal Leader/Datu"),
        ("ulama", "Ulama"),
        ("imam", "Imam/Khatib"),
        ("ustadz", "Ustadz/Religious Teacher"),
        ("arabic_teacher", "ALIVE/Arabic Teacher"),
        ("madrasa_teacher", "Madrasah Teacher"),
        ("youth_leader", "Youth Leader"),
        ("women_leader", "Women Leader"),
        ("business_leader", "Business Leader"),
        ("cooperative_leader", "Cooperative Leader"),
        ("health_worker", "Community Health Worker"),
        ("volunteer", "Community Volunteer"),
        ("other", "Other"),
    ]

    INFLUENCE_LEVELS = [
        ("very_high", "Very High"),
        ("high", "High"),
        ("medium", "Medium"),
        ("low", "Low"),
        ("emerging", "Emerging"),
    ]

    ENGAGEMENT_LEVELS = [
        ("very_active", "Very Active"),
        ("active", "Active"),
        ("moderate", "Moderate"),
        ("limited", "Limited"),
        ("inactive", "Inactive"),
    ]

    # Basic Information
    full_name = models.CharField(
        max_length=255, help_text="Full name of the stakeholder"
    )

    nickname = models.CharField(
        max_length=100,
        blank=True,
        help_text="Common nickname or title (e.g., Ustadz Abdullah)",
    )

    stakeholder_type = models.CharField(
        max_length=50,
        choices=STAKEHOLDER_TYPES,
        help_text="Type/role of stakeholder in the community",
    )

    community = models.ForeignKey(
        OBCCommunity,
        on_delete=models.CASCADE,
        related_name="stakeholders",
        help_text="OBC community where this stakeholder is active",
    )

    # Role and Position
    position = models.CharField(
        max_length=255, blank=True, help_text="Official position or title held"
    )

    organization = models.CharField(
        max_length=255,
        blank=True,
        help_text="Organization or institution they represent",
    )

    responsibilities = models.TextField(
        blank=True, help_text="Key responsibilities and duties"
    )

    # Contact Information
    contact_number = models.CharField(
        max_length=20, blank=True, help_text="Primary contact number"
    )

    alternate_contact = models.CharField(
        max_length=20, blank=True, help_text="Alternate contact number"
    )

    email = models.EmailField(blank=True, help_text="Email address")

    address = models.TextField(
        blank=True, help_text="Physical address within the community"
    )

    # Influence and Engagement
    influence_level = models.CharField(
        max_length=20,
        choices=INFLUENCE_LEVELS,
        default="medium",
        help_text="Level of influence within the community",
    )

    engagement_level = models.CharField(
        max_length=20,
        choices=ENGAGEMENT_LEVELS,
        default="active",
        help_text="Level of engagement in community activities",
    )

    areas_of_influence = models.TextField(
        blank=True,
        help_text="Specific areas where they have influence (e.g., youth, religious matters, livelihood)",
    )

    # Background Information
    age = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(18), MaxValueValidator(100)],
        help_text="Age of the stakeholder",
    )

    educational_background = models.CharField(
        max_length=255,
        blank=True,
        help_text="Educational background and qualifications",
    )

    cultural_background = models.CharField(
        max_length=255, blank=True, help_text="Cultural or ethnic background"
    )

    languages_spoken = models.CharField(
        max_length=255, blank=True, help_text="Languages spoken (comma-separated)"
    )

    # Service and History
    since_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1950), MaxValueValidator(2030)],
        help_text="Year they started serving in this role",
    )

    years_in_community = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of years living in this community"
    )

    previous_roles = models.TextField(
        blank=True, help_text="Previous roles or positions held in the community"
    )

    # Additional Information
    special_skills = models.TextField(
        blank=True, help_text="Special skills or expertise they bring to the community"
    )

    networks = models.TextField(
        blank=True, help_text="External networks or connections they have"
    )

    achievements = models.TextField(
        blank=True, help_text="Notable achievements or contributions to the community"
    )

    challenges_faced = models.TextField(
        blank=True, help_text="Challenges they face in their role"
    )

    support_needed = models.TextField(
        blank=True, help_text="Support or resources they need to be more effective"
    )

    # Administrative
    is_active = models.BooleanField(
        default=True, help_text="Whether this stakeholder is currently active"
    )

    is_verified = models.BooleanField(
        default=False, help_text="Whether the stakeholder information has been verified"
    )

    verification_date = models.DateField(
        null=True, blank=True, help_text="Date when information was last verified"
    )

    notes = models.TextField(
        blank=True, help_text="Additional notes about the stakeholder"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "communities_stakeholder"
        ordering = ["community__barangay__name", "stakeholder_type", "full_name"]
        verbose_name = "Community Stakeholder"
        verbose_name_plural = "Community Stakeholders"
        unique_together = ["full_name", "community", "stakeholder_type"]

    def __str__(self):
        display_name = self.nickname if self.nickname else self.full_name
        community_label = self.community.display_name
        return f"{display_name} ({self.get_stakeholder_type_display()}) - {community_label}"

    @property
    def display_name(self):
        """Return the preferred display name."""
        return self.nickname if self.nickname else self.full_name

    @property
    def years_of_service(self):
        """Calculate years of service if since_year is provided."""
        if self.since_year:
            from datetime import datetime

            return datetime.now().year - self.since_year
        return None

    @property
    def contact_info(self):
        """Return formatted contact information."""
        contacts = []
        if self.contact_number:
            contacts.append(f"Mobile: {self.contact_number}")
        if self.alternate_contact:
            contacts.append(f"Alt: {self.alternate_contact}")
        if self.email:
            contacts.append(f"Email: {self.email}")
        return " | ".join(contacts) if contacts else "No contact info"


class StakeholderEngagement(models.Model):
    """
    Model for tracking stakeholder engagement activities and interactions.
    """

    ENGAGEMENT_TYPES = [
        ("meeting", "Community Meeting"),
        ("consultation", "Consultation"),
        ("training", "Training/Workshop"),
        ("assessment", "Assessment/Survey"),
        ("project_activity", "Project Activity"),
        ("religious_activity", "Religious Activity"),
        ("cultural_event", "Cultural Event"),
        ("emergency_response", "Emergency Response"),
        ("coordination", "Coordination Meeting"),
        ("other", "Other"),
    ]

    ENGAGEMENT_OUTCOMES = [
        ("very_positive", "Very Positive"),
        ("positive", "Positive"),
        ("neutral", "Neutral"),
        ("challenging", "Challenging"),
        ("negative", "Negative"),
    ]

    stakeholder = models.ForeignKey(
        Stakeholder,
        on_delete=models.CASCADE,
        related_name="engagements",
        help_text="Stakeholder involved in this engagement",
    )

    engagement_type = models.CharField(
        max_length=50, choices=ENGAGEMENT_TYPES, help_text="Type of engagement activity"
    )

    title = models.CharField(
        max_length=255, help_text="Title or subject of the engagement"
    )

    description = models.TextField(help_text="Detailed description of the engagement")

    date = models.DateField(help_text="Date of the engagement")

    duration_hours = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Duration in hours",
    )

    location = models.CharField(
        max_length=255, blank=True, help_text="Location where engagement took place"
    )

    participants_count = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of participants involved"
    )

    outcome = models.CharField(
        max_length=20,
        choices=ENGAGEMENT_OUTCOMES,
        default="positive",
        help_text="Overall outcome of the engagement",
    )

    key_points = models.TextField(
        blank=True, help_text="Key points discussed or outcomes achieved"
    )

    action_items = models.TextField(
        blank=True, help_text="Action items or follow-up tasks identified"
    )

    challenges_encountered = models.TextField(
        blank=True, help_text="Challenges or issues encountered"
    )

    stakeholder_feedback = models.TextField(
        blank=True, help_text="Feedback provided by the stakeholder"
    )

    follow_up_needed = models.BooleanField(
        default=False, help_text="Whether follow-up is needed"
    )

    follow_up_date = models.DateField(
        null=True, blank=True, help_text="Date for follow-up if needed"
    )

    documented_by = models.CharField(
        max_length=255, help_text="Person who documented this engagement"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "communities_stakeholder_engagement"
        ordering = ["-date", "stakeholder__full_name"]
        verbose_name = "Stakeholder Engagement"
        verbose_name_plural = "Stakeholder Engagements"

    def __str__(self):
        return f"{self.title} - {self.stakeholder.display_name} ({self.date})"


class MunicipalityCoverage(CommunityProfileBase):
    """Tracks municipalities or cities with notable Bangsamoro presence."""

    objects = ActiveCommunityManager()
    all_objects = models.Manager()

    municipality = models.OneToOneField(
        Municipality,
        on_delete=models.CASCADE,
        related_name="obc_coverage",
        help_text="LGU where Bangsamoro communities are present",
    )
    total_obc_communities = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of identified Bangsamoro communities in the municipality",
    )
    key_barangays = models.TextField(
        blank=True,
        help_text="Barangays or sitios with notable Bangsamoro presence (comma-separated)",
    )
    existing_support_programs = models.TextField(
        blank=True,
        help_text="Active government or partner support programs",
    )
    auto_sync = models.BooleanField(
        default=True,
        help_text="Keep totals in sync with registered barangay communities",
    )
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="municipality_coverages_created",
        help_text="User who recorded this municipality",
    )
    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="municipality_coverages_updated",
        help_text="User who last updated this record",
    )

    class Meta:
        ordering = [
            "municipality__province__region__name",
            "municipality__province__name",
            "municipality__name",
        ]
        verbose_name = "Bangsamoro Municipality OBC"
        verbose_name_plural = "Bangsamoro Municipality OBCs"

    def __str__(self):
        return f"{self.municipality.name} Bangsamoro Coverage"

    @property
    def region(self):
        """Shortcut to the parent region."""
        return self.municipality.province.region

    @property
    def province(self):
        """Shortcut to the parent province."""
        return self.municipality.province

    @property
    def display_name(self):
        """Return municipality name with province for dashboards."""
        return f"{self.municipality.name}, {self.province.name}"

    @property
    def full_location(self):
        """Return formatted location string for serializers."""
        return f"{self.municipality.name}, {self.province.name}"

    @property
    def barangay_attributed_population(self):
        """Calculate total population attributed to barangay OBCs."""
        from django.db.models import Sum

        return (
            OBCCommunity.objects.filter(
                barangay__municipality=self.municipality
            ).aggregate(total=Sum("estimated_obc_population"))["total"]
            or 0
        )

    @property
    def unattributed_population(self):
        """
        Calculate population NOT attributed to any barangay OBC.

        This represents estimated OBC population in the municipality
        that hasn't been mapped to specific barangays yet.

        Returns 0 if auto_sync is enabled (everything is attributed).
        """
        if self.auto_sync:
            return 0

        municipal_total = self.estimated_obc_population or 0
        barangay_total = self.barangay_attributed_population

        return max(0, municipal_total - barangay_total)

    @property
    def population_reconciliation(self):
        """
        Return a dict showing population breakdown for reconciliation.

        Useful for displaying in templates and understanding data gaps.
        """
        municipal_total = self.estimated_obc_population or 0
        barangay_total = self.barangay_attributed_population
        unattributed = self.unattributed_population

        return {
            "total_municipal": municipal_total,
            "attributed_to_barangays": barangay_total,
            "unattributed": unattributed,
            "attribution_rate": (
                round((barangay_total / municipal_total * 100), 1)
                if municipal_total > 0
                else 0
            ),
            "auto_sync_enabled": self.auto_sync,
        }

    def refresh_from_communities(self):
        """Aggregate community data for this municipality when auto-sync is enabled."""
        if self.auto_sync:
            communities = OBCCommunity.objects.filter(
                barangay__municipality=self.municipality
            )

            aggregates = communities.aggregate(
                **{
                    f"{field}__sum": models.Sum(field)
                    for field in AGGREGATED_NUMERIC_FIELDS
                }
            )
            key_barangays = (
                communities.values_list("barangay__name", flat=True)
                .order_by("barangay__name")
                .distinct()
            )

            update_kwargs = {
                "total_obc_communities": communities.count(),
                "key_barangays": ", ".join(key_barangays),
            }

            for field in AGGREGATED_NUMERIC_FIELDS:
                update_kwargs[field] = aggregates.get(f"{field}__sum") or 0

            MunicipalityCoverage.objects.filter(pk=self.pk).update(**update_kwargs)
            for field, value in update_kwargs.items():
                setattr(self, field, value)

        province = self.province
        if province:
            ProvinceCoverage.sync_for_province(province)

    @classmethod
    def sync_for_municipality(cls, municipality):
        """Create or update coverage using barangay data."""
        existing = cls.all_objects.filter(municipality=municipality).first()
        if existing and existing.is_deleted:
            # Leave archived coverages untouched until explicitly restored.
            return existing

        coverage, _ = cls.objects.get_or_create(municipality=municipality)
        coverage.refresh_from_communities()
        return coverage


class ProvinceCoverage(CommunityProfileBase):
    """Aggregated Bangsamoro coverage data at the provincial level."""

    objects = ActiveCommunityManager()
    all_objects = models.Manager()

    province = models.OneToOneField(
        Province,
        on_delete=models.CASCADE,
        related_name="obc_coverage",
        help_text="Province covering multiple municipal OBC records",
    )
    total_municipalities = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of municipalities or cities with OBC coverage",
    )
    total_obc_communities = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Total barangay-level OBC communities aggregated from municipalities",
    )
    key_municipalities = models.TextField(
        blank=True,
        help_text="Municipalities with notable Bangsamoro presence (comma-separated)",
    )
    existing_support_programs = models.TextField(
        blank=True,
        help_text="Active support programs at the provincial level",
    )
    auto_sync = models.BooleanField(
        default=True,
        help_text="Keep provincial totals in sync with municipal coverage records",
    )
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="province_coverages_created",
        help_text="User who recorded this province",
    )
    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="province_coverages_updated",
        help_text="User who last updated this record",
    )
    is_submitted = models.BooleanField(
        default=False,
        help_text="Whether this record has been submitted by a MANA participant (becomes read-only)",
    )
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when this record was submitted",
    )
    submitted_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="province_coverages_submitted",
        help_text="User who submitted this record",
    )

    class Meta:
        ordering = [
            "province__region__name",
            "province__name",
        ]
        verbose_name = "Bangsamoro Province OBC"
        verbose_name_plural = "Bangsamoro Province OBCs"

    def __str__(self):
        return f"{self.province.name} Bangsamoro Coverage"

    @property
    def region(self):
        """Shortcut to the parent region."""
        return self.province.region

    @property
    def display_name(self):
        """Return province name with region for dashboards."""
        region = self.region
        if region:
            return f"{self.province.name}, {region.name}"
        return self.province.name

    @property
    def full_location(self):
        """Return formatted location string for serializers."""
        region = self.region
        if region:
            return f"{self.province.name}, Region {region.code}"
        return self.province.name

    @property
    def municipal_attributed_population(self):
        """Calculate total population attributed to municipal OBCs."""
        from django.db.models import Sum

        return (
            MunicipalityCoverage.objects.filter(
                municipality__province=self.province, is_deleted=False
            ).aggregate(total=Sum("estimated_obc_population"))["total"]
            or 0
        )

    @property
    def unattributed_population(self):
        """
        Calculate population NOT attributed to any municipal OBC.

        This represents estimated OBC population in the province
        that hasn't been mapped to specific municipalities yet.

        Returns 0 if auto_sync is enabled (everything is attributed).
        """
        if self.auto_sync:
            return 0

        provincial_total = self.estimated_obc_population or 0
        municipal_total = self.municipal_attributed_population

        return max(0, provincial_total - municipal_total)

    @property
    def population_reconciliation(self):
        """
        Return a dict showing population breakdown for reconciliation.

        Useful for displaying in templates and understanding data gaps.
        """
        provincial_total = self.estimated_obc_population or 0
        municipal_total = self.municipal_attributed_population
        unattributed = self.unattributed_population

        return {
            "total_provincial": provincial_total,
            "attributed_to_municipalities": municipal_total,
            "unattributed": unattributed,
            "attribution_rate": (
                round((municipal_total / provincial_total * 100), 1)
                if provincial_total > 0
                else 0
            ),
            "auto_sync_enabled": self.auto_sync,
        }

    def refresh_from_municipalities(self):
        """Aggregate municipal data for this province when auto-sync is enabled."""
        if not self.auto_sync:
            return

        municipal_coverages = MunicipalityCoverage.objects.filter(
            municipality__province=self.province,
            is_deleted=False,
        )

        aggregates = municipal_coverages.aggregate(
            **{
                f"{field}__sum": models.Sum(field)
                for field in AGGREGATED_NUMERIC_FIELDS
            }
        )

        total_barangay_communities = (
            municipal_coverages.aggregate(total=models.Sum("total_obc_communities"))[
                "total"
            ]
            or 0
        )

        key_municipalities = (
            municipal_coverages.values_list("municipality__name", flat=True)
            .order_by("municipality__name")
            .distinct()
        )

        update_kwargs = {
            "total_municipalities": municipal_coverages.count(),
            "total_obc_communities": total_barangay_communities,
            "key_municipalities": ", ".join(key_municipalities),
        }

        for field in AGGREGATED_NUMERIC_FIELDS:
            update_kwargs[field] = aggregates.get(f"{field}__sum") or 0

        ProvinceCoverage.objects.filter(pk=self.pk).update(**update_kwargs)
        for field, value in update_kwargs.items():
            setattr(self, field, value)

    @classmethod
    def sync_for_province(cls, province):
        """Create or update coverage using municipal data."""
        if province is None:
            return None

        existing = cls.all_objects.filter(province=province).first()
        if existing and existing.is_deleted:
            return existing

        coverage, _ = cls.objects.get_or_create(province=province)
        coverage.refresh_from_municipalities()
        return coverage


# ============================================================================
# GEOGRAPHIC DATA MODELS (Moved from mana app for better organization)
# ============================================================================


class GeographicDataLayer(models.Model):
    """Model for managing geographic data layers for mapping and visualization."""

    LAYER_TYPES = [
        ("point", "Point Data"),
        ("line", "Line/Route Data"),
        ("polygon", "Polygon/Area Data"),
        ("raster", "Raster/Satellite Data"),
        ("heatmap", "Heatmap Data"),
        ("cluster", "Clustered Data"),
    ]

    DATA_SOURCES = [
        ("field_survey", "Field Survey"),
        ("satellite_imagery", "Satellite Imagery"),
        ("government_data", "Government Dataset"),
        ("community_mapping", "Community Mapping"),
        ("third_party", "Third Party Source"),
        ("mobile_app", "Mobile Application"),
        ("gps_tracking", "GPS Tracking"),
    ]

    name = models.CharField(
        max_length=150, help_text="Name of the geographic data layer"
    )

    description = models.TextField(
        help_text="Description of the data layer and its purpose"
    )

    layer_type = models.CharField(
        max_length=15, choices=LAYER_TYPES, help_text="Type of geographic data"
    )

    data_source = models.CharField(
        max_length=20, choices=DATA_SOURCES, help_text="Source of the geographic data"
    )

    # Community and Assessment Relations
    community = models.ForeignKey(
        "OBCCommunity",
        on_delete=models.CASCADE,
        related_name="geographic_layers",
        null=True,
        blank=True,
        help_text="Community this layer relates to (if applicable)",
    )

    assessment = models.ForeignKey(
        "mana.Assessment",
        on_delete=models.CASCADE,
        related_name="geographic_layers",
        null=True,
        blank=True,
        help_text="Assessment this layer was created for (if applicable)",
    )

    # Administrative Relations (for direct geographic data linkage)
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name="geographic_layers",
        null=True,
        blank=True,
        help_text="Region this layer covers or relates to",
    )

    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name="geographic_layers",
        null=True,
        blank=True,
        help_text="Province this layer covers or relates to",
    )

    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE,
        related_name="geographic_layers",
        null=True,
        blank=True,
        help_text="Municipality this layer covers or relates to",
    )

    barangay = models.ForeignKey(
        Barangay,
        on_delete=models.CASCADE,
        related_name="geographic_layers",
        null=True,
        blank=True,
        help_text="Barangay this layer covers or relates to",
    )

    # Geographic Data
    geojson_data = models.JSONField(help_text="GeoJSON data for the layer")

    bounding_box = models.JSONField(
        null=True,
        blank=True,
        help_text="Bounding box coordinates [min_lng, min_lat, max_lng, max_lat]",
    )

    center_point = models.JSONField(
        null=True,
        blank=True,
        help_text="Center point coordinates [longitude, latitude]",
    )

    # Styling and Display
    style_properties = models.JSONField(
        null=True,
        blank=True,
        help_text="Styling properties for map display (colors, symbols, etc.)",
    )

    zoom_level_min = models.IntegerField(
        default=1, help_text="Minimum zoom level for layer visibility"
    )

    zoom_level_max = models.IntegerField(
        default=18, help_text="Maximum zoom level for layer visibility"
    )

    is_visible = models.BooleanField(
        default=True, help_text="Whether the layer is visible by default"
    )

    opacity = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Layer opacity (0.0 to 1.0)",
    )

    # Metadata and Attribution
    data_collection_date = models.DateField(
        null=True, blank=True, help_text="Date when the data was collected"
    )

    accuracy_meters = models.FloatField(
        null=True, blank=True, help_text="Estimated accuracy in meters"
    )

    coordinate_system = models.CharField(
        max_length=50,
        default="EPSG:4326",
        help_text="Coordinate reference system (e.g., EPSG:4326)",
    )

    attribution = models.TextField(
        blank=True, help_text="Data attribution and source credits"
    )

    license_info = models.CharField(
        max_length=100, blank=True, help_text="License information for the data"
    )

    # Access Control
    is_public = models.BooleanField(
        default=False, help_text="Whether this layer is publicly accessible"
    )

    access_groups = models.JSONField(
        null=True, blank=True, help_text="User groups that have access to this layer"
    )

    # Technical Properties
    feature_count = models.IntegerField(
        default=0, help_text="Number of features in the layer"
    )

    file_size_bytes = models.BigIntegerField(
        null=True, blank=True, help_text="Size of the data in bytes"
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_geo_layers",
        help_text="User who created this layer",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["community", "layer_type"]),
            models.Index(fields=["assessment", "data_source"]),
            models.Index(fields=["is_public", "is_visible"]),
        ]

    def clean(self):
        """Validate administrative hierarchy relationships."""
        super().clean()

        # Check administrative hierarchy consistency
        if (
            self.barangay
            and self.municipality
            and self.barangay.municipality != self.municipality
        ):
            raise ValidationError("Barangay must belong to the specified municipality")

        if (
            self.municipality
            and self.province
            and self.municipality.province != self.province
        ):
            raise ValidationError("Municipality must belong to the specified province")

        if self.province and self.region and self.province.region != self.region:
            raise ValidationError("Province must belong to the specified region")

    @property
    def administrative_level(self):
        """Return the most specific administrative level this layer covers."""
        if self.barangay:
            return "barangay"
        elif self.municipality:
            return "municipality"
        elif self.province:
            return "province"
        elif self.region:
            return "region"
        elif self.community:
            return "community"
        return "none"

    @property
    def full_administrative_path(self):
        """Return the full administrative path for this layer."""
        if self.barangay:
            return self.barangay.full_path
        elif self.municipality:
            return self.municipality.full_path
        elif self.province:
            return self.province.full_path
        elif self.region:
            return f"Region {self.region.code} - {self.region.name}"
        elif self.community:
            return self.community.full_location
        return "No administrative assignment"

    def get_related_obc_communities(self):
        """Get OBC Communities that fall within this layer's administrative scope."""
        if self.barangay:
            return self.barangay.obc_communities.all()
        elif self.municipality:
            return OBCCommunity.objects.filter(barangay__municipality=self.municipality)
        elif self.province:
            return OBCCommunity.objects.filter(
                barangay__municipality__province=self.province
            )
        elif self.region:
            return OBCCommunity.objects.filter(
                barangay__municipality__province__region=self.region
            )
        elif self.community:
            return [self.community]
        return []

    def to_map_payload(self):
        """Serialize the layer for client-side map rendering."""

        return {
            "id": self.pk,
            "name": self.name,
            "layer_type": self.layer_type,
            "layer_type_display": self.get_layer_type_display(),
            "data_source": self.data_source,
            "administrative_path": self.full_administrative_path,
            "geojson": self.geojson_data,
            "style": self.style_properties or {},
            "opacity": self.opacity,
            "is_visible": self.is_visible,
            "center": self.center_point,
            "bounds": self.bounding_box,
            "zoom_min": self.zoom_level_min,
            "zoom_max": self.zoom_level_max,
            "attribution": self.attribution,
            "license": self.license_info,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __str__(self):
        return f"{self.name} ({self.get_layer_type_display()})"


class MapVisualization(models.Model):
    """Model for managing map visualizations and configurations."""

    VISUALIZATION_TYPES = [
        ("basic_map", "Basic Map"),
        ("choropleth", "Choropleth Map"),
        ("heat_map", "Heat Map"),
        ("cluster_map", "Cluster Map"),
        ("timeline_map", "Timeline Map"),
        ("comparison_map", "Comparison Map"),
        ("story_map", "Story Map"),
    ]

    MAP_PROVIDERS = [
        ("openstreetmap", "OpenStreetMap"),
        ("satellite", "Satellite Imagery"),
        ("terrain", "Terrain Map"),
        ("dark", "Dark Theme"),
        ("light", "Light Theme"),
        ("custom", "Custom Basemap"),
    ]

    title = models.CharField(max_length=200, help_text="Title of the map visualization")

    description = models.TextField(
        help_text="Description and purpose of the visualization"
    )

    visualization_type = models.CharField(
        max_length=20,
        choices=VISUALIZATION_TYPES,
        help_text="Type of map visualization",
    )

    # Relations
    community = models.ForeignKey(
        "OBCCommunity",
        on_delete=models.CASCADE,
        related_name="community_map_visualizations",
        null=True,
        blank=True,
        help_text="Community this visualization focuses on",
    )

    assessment = models.ForeignKey(
        "mana.Assessment",
        on_delete=models.CASCADE,
        related_name="map_visualizations",
        null=True,
        blank=True,
        help_text="Assessment this visualization was created for",
    )

    layers = models.ManyToManyField(
        GeographicDataLayer,
        related_name="visualizations",
        help_text="Geographic layers included in this visualization",
    )

    # Map Configuration
    basemap_provider = models.CharField(
        max_length=20,
        choices=MAP_PROVIDERS,
        default="openstreetmap",
        help_text="Base map provider",
    )

    initial_zoom = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(18)],
        help_text="Initial zoom level",
    )

    initial_center = models.JSONField(
        help_text="Initial center point [longitude, latitude]"
    )

    bounding_box = models.JSONField(
        null=True,
        blank=True,
        help_text="Map bounding box [min_lng, min_lat, max_lng, max_lat]",
    )

    # Visualization Settings
    color_scheme = models.JSONField(
        null=True, blank=True, help_text="Color scheme configuration"
    )

    legend_configuration = models.JSONField(
        null=True, blank=True, help_text="Legend display configuration"
    )

    popup_template = models.TextField(
        blank=True, help_text="HTML template for feature popups"
    )

    filters_configuration = models.JSONField(
        null=True, blank=True, help_text="Interactive filters configuration"
    )

    # Interactivity
    is_interactive = models.BooleanField(
        default=True, help_text="Whether the map allows user interaction"
    )

    enable_clustering = models.BooleanField(
        default=False, help_text="Whether to enable point clustering"
    )

    enable_search = models.BooleanField(
        default=False, help_text="Whether to enable location search"
    )

    enable_drawing = models.BooleanField(
        default=False, help_text="Whether to enable drawing tools"
    )

    # Sharing and Access
    is_public = models.BooleanField(
        default=False, help_text="Whether this visualization is publicly accessible"
    )

    is_embedded = models.BooleanField(
        default=False, help_text="Whether this visualization can be embedded"
    )

    share_token = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text="Unique token for sharing the visualization",
    )

    # Analytics
    view_count = models.IntegerField(
        default=0, help_text="Number of times this visualization has been viewed"
    )

    last_viewed = models.DateTimeField(
        null=True, blank=True, help_text="Last time this visualization was viewed"
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_visualizations",
        help_text="User who created this visualization",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_visualization_type_display()})"

    def save(self, *args, **kwargs):
        """Generate share token if needed."""
        if not self.share_token:
            import secrets

            self.share_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)


class SpatialDataPoint(models.Model):
    """Model for individual spatial data points with attributes."""

    POINT_TYPES = [
        ("community_center", "Community Center"),
        ("health_facility", "Health Facility"),
        ("school", "Educational Facility"),
        ("mosque", "Mosque/Religious Site"),
        ("government_office", "Government Office"),
        ("market", "Market/Commerce"),
        ("infrastructure", "Infrastructure"),
        ("natural_resource", "Natural Resource"),
        ("cultural_site", "Cultural Site"),
        ("hazard_area", "Hazard/Risk Area"),
        ("project_site", "Project Location"),
        ("assessment_point", "Assessment Point"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("planned", "Planned"),
        ("under_construction", "Under Construction"),
        ("abandoned", "Abandoned"),
        ("needs_verification", "Needs Verification"),
    ]

    # Basic Information
    name = models.CharField(max_length=200, help_text="Name or identifier of the point")

    description = models.TextField(blank=True, help_text="Description of the point")

    point_type = models.CharField(
        max_length=25, choices=POINT_TYPES, help_text="Type of spatial point"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
        help_text="Current status of the point",
    )

    # Geographic Information
    latitude = models.FloatField(help_text="Latitude coordinate")

    longitude = models.FloatField(help_text="Longitude coordinate")

    elevation = models.FloatField(
        null=True, blank=True, help_text="Elevation in meters above sea level"
    )

    accuracy_meters = models.FloatField(
        null=True, blank=True, help_text="GPS accuracy in meters"
    )

    # Relations
    community = models.ForeignKey(
        "OBCCommunity",
        on_delete=models.CASCADE,
        related_name="spatial_points",
        help_text="Community this point belongs to",
    )

    assessment = models.ForeignKey(
        "mana.Assessment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="spatial_points",
        help_text="Assessment that identified this point",
    )

    data_layer = models.ForeignKey(
        GeographicDataLayer,
        on_delete=models.CASCADE,
        related_name="data_points",
        help_text="Geographic layer this point belongs to",
    )

    # Attributes
    attributes = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional attributes and properties (JSON format)",
    )

    # Data Collection Information
    collected_date = models.DateTimeField(
        default=timezone.now, help_text="Date and time when point was collected"
    )

    collection_method = models.CharField(
        max_length=50, blank=True, help_text="Method used to collect this point"
    )

    is_verified = models.BooleanField(
        default=False, help_text="Whether this point has been verified"
    )

    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_points",
        help_text="User who verified this point",
    )

    verification_date = models.DateTimeField(
        null=True, blank=True, help_text="Date when point was verified"
    )

    # Photo and Media
    photo_url = models.URLField(blank=True, help_text="URL to photo of the location")

    media_files = models.JSONField(
        null=True, blank=True, help_text="References to associated media files"
    )

    # Metadata
    collected_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="collected_points",
        help_text="User who collected this point",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-collected_date"]
        indexes = [
            models.Index(fields=["community", "point_type"]),
            models.Index(fields=["latitude", "longitude"]),
            models.Index(fields=["data_layer", "status"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_point_type_display()})"

    @property
    def coordinates(self):
        """Return coordinates as [longitude, latitude] for GeoJSON."""
        return [self.longitude, self.latitude]


class CommunityEvent(models.Model):
    """
    Community-level events and observances for calendar integration.
    Tracks cultural celebrations, meetings, trainings, and emergencies.
    """

    EVENT_CULTURAL = "cultural"
    EVENT_RELIGIOUS = "religious"
    EVENT_MEETING = "meeting"
    EVENT_TRAINING = "training"
    EVENT_DISASTER = "disaster"
    EVENT_OTHER = "other"
    EVENT_TYPE_CHOICES = [
        (EVENT_CULTURAL, "Cultural Celebration"),
        (EVENT_RELIGIOUS, "Religious Observance"),
        (EVENT_MEETING, "Community Meeting"),
        (EVENT_TRAINING, "Community Training"),
        (EVENT_DISASTER, "Disaster/Emergency"),
        (EVENT_OTHER, "Other"),
    ]

    community = models.ForeignKey(
        "OBCCommunity",
        on_delete=models.CASCADE,
        related_name="community_events",
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    event_type = models.CharField(
        max_length=30,
        choices=EVENT_TYPE_CHOICES,
    )

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    all_day = models.BooleanField(default=True)

    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    location = models.CharField(max_length=255, blank=True)
    organizer = models.CharField(max_length=255, blank=True)

    is_public = models.BooleanField(
        default=True,
        help_text="Show on public calendar",
    )

    # Recurrence support
    is_recurring = models.BooleanField(
        default=False, help_text="Whether this is a recurring event"
    )

    recurrence_pattern = models.ForeignKey(
        "common.RecurringEventPattern",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="recurring_community_events",
        help_text="Recurrence pattern configuration",
    )

    recurrence_parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="recurrence_instances",
        help_text="Parent event if this is a recurrence instance",
    )

    is_recurrence_exception = models.BooleanField(
        default=False,
        help_text="True if this instance was edited separately",
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_community_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "communities_community_event"
        ordering = ["-start_date"]
        verbose_name = "Community Event"
        verbose_name_plural = "Community Events"

    def __str__(self):
        return f"{self.title} - {self.community.name}"
