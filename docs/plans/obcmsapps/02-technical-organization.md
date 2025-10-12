# OBCMS Technical Organization

**Document:** 02-technical-organization.md
**Last Updated:** 2025-10-12
**Purpose:** Complete guide to OBCMS Django application structure and technical architecture

---

## Table of Contents

1. [Django Applications Overview](#django-applications-overview)
2. [Core Applications](#core-applications)
3. [URL Organization](#url-organization)
4. [Inter-App Dependencies](#inter-app-dependencies)
5. [Technical Architecture](#technical-architecture)
6. [Database Strategy](#database-strategy)
7. [API Architecture](#api-architecture)

---

## Django Applications Overview

OBCMS consists of **14 Django applications** organized into 3 tiers:

### Foundation Tier (1 app)
- `common` - Base models, utilities, shared functionality

### Domain Tier (8 apps)
- `communities` - OBC community profiles and demographics
- `mana` - Mapping and Needs Assessment
- `coordination` - Multi-stakeholder coordination
- `monitoring` - M&E system for PPAs/MOAs
- `recommendations` - Policy recommendations (parent app)
  - `recommendations.policies` - Policy tracking
  - `recommendations.documents` - Document management
  - `recommendations.policy_tracking` - Implementation monitoring
- `project_central` - Integrated project management

### Support Tier (5 apps)
- `municipal_profiles` - Municipal data aggregation
- `services` - Service catalog and applications
- `data_imports` - Data import utilities
- `ai_assistant` - AI assistant with vector search

---

## Core Applications

### 1. COMMON APP (Foundation Layer)

**Location:** `src/common/`
**Purpose:** Provides base models, utilities, and shared functionality

#### Key Models

##### A. User Management
```python
# src/common/models.py

class User(AbstractUser):
    """Custom user model with organization linkage"""
    user_type = models.CharField(
        max_length=20,
        choices=[
            ('admin', 'System Administrator'),
            ('oobc_executive', 'OOBC Executive'),
            ('oobc_staff', 'OOBC Staff'),
            ('cm_office', 'Chief Minister Office'),
            ('bmoa', 'BARMM Ministry/Office/Agency'),
            ('lgu', 'Local Government Unit'),
            ('nga', 'National Government Agency'),
            ('community_leader', 'Community Leader'),
            ('researcher', 'Researcher'),
        ]
    )
    moa_organization = models.ForeignKey(
        'coordination.Organization',
        null=True, blank=True,
        on_delete=models.SET_NULL
    )
    is_approved = models.BooleanField(default=False)
    approval_tier = models.IntegerField(default=0)  # Two-tier approval

    # Permission helpers
    def can_edit_ppa(self, ppa):
        """Check if user can edit specific PPA"""
        pass

    def can_view_ppa(self, ppa):
        """Check if user can view specific PPA"""
        pass

class StaffProfile(models.Model):
    """Extended staff metadata"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employment_status = models.CharField(max_length=20)
    employment_type = models.CharField(max_length=20)
    purpose = models.TextField()  # Job purpose
    key_result_areas = models.JSONField(default=list)  # KRAs
    deliverables = models.JSONField(default=list)
    core_competencies = models.JSONField(default=list)
    leadership_competencies = models.JSONField(default=list)
    functional_competencies = models.JSONField(default=list)
```

##### B. Administrative Hierarchy (Geographic Data)
```python
class Region(models.Model):
    """Geographic region with GeoJSON boundaries"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)

    # Geographic data (NO PostGIS required)
    boundary_geojson = models.JSONField(null=True, blank=True)  # GeoJSON
    center_coordinates = models.JSONField(null=True, blank=True)  # {lat, lng}
    bounding_box = models.JSONField(null=True, blank=True)  # [[S,W],[N,E]]

    population = models.IntegerField(default=0)
    area_sq_km = models.DecimalField(max_digits=10, decimal_places=2)

class Province(models.Model):
    """Province within a region"""
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    boundary_geojson = models.JSONField(null=True, blank=True)
    center_coordinates = models.JSONField(null=True, blank=True)
    bounding_box = models.JSONField(null=True, blank=True)

class Municipality(models.Model):
    """Municipality or city within a province"""
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    classification = models.CharField(
        max_length=20,
        choices=[('city', 'City'), ('municipality', 'Municipality')]
    )
    boundary_geojson = models.JSONField(null=True, blank=True)
    center_coordinates = models.JSONField(null=True, blank=True)

class Barangay(models.Model):
    """Barangay within a municipality"""
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    boundary_geojson = models.JSONField(null=True, blank=True)
    center_coordinates = models.JSONField(null=True, blank=True)
    population = models.IntegerField(default=0)
```

##### C. Unified Work Hierarchy (WorkItem System)
```python
class WorkItem(MPTTModel):
    """Unified model for tasks, activities, and projects"""
    WORK_TYPE_CHOICES = [
        ('task', 'Task'),
        ('activity', 'Activity'),
        ('project', 'Project'),
    ]

    work_type = models.CharField(max_length=20, choices=WORK_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Hierarchical structure (MPTT)
    parent = TreeForeignKey(
        'self',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='children'
    )

    # Status workflow
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('review', 'Under Review'),
            ('completed', 'Completed'),
            ('deferred', 'Deferred'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )

    # Assignment
    assigned_to = models.ForeignKey(
        User,
        null=True, blank=True,
        on_delete=models.SET_NULL
    )

    # Timing
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)

    # Priority
    priority = models.CharField(
        max_length=10,
        choices=[
            ('critical', 'Critical'),
            ('high', 'High'),
            ('medium', 'Medium'),
            ('low', 'Low'),
        ],
        default='medium'
    )

# Proxy models for backward compatibility
class StaffTaskProxy(WorkItem):
    """Proxy for tasks (work_type='task')"""
    class Meta:
        proxy = True

class EventProxy(WorkItem):
    """Proxy for activities (work_type='activity')"""
    class Meta:
        proxy = True

class ProjectWorkflowProxy(WorkItem):
    """Proxy for projects (work_type='project')"""
    class Meta:
        proxy = True
```

##### D. Advanced Calendar System (RFC 5545 Compatible)
```python
class RecurringEventPattern(models.Model):
    """RFC 5545-compliant recurrence patterns"""
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    work_item = models.OneToOneField(WorkItem, on_delete=models.CASCADE)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    interval = models.PositiveIntegerField(default=1)

    # Weekly recurrence
    by_day = models.JSONField(null=True, blank=True)  # ['MO', 'WE', 'FR']

    # Monthly recurrence
    by_month_day = models.JSONField(null=True, blank=True)  # [1, 15, -1]
    by_set_pos = models.IntegerField(null=True, blank=True)  # 1st, 2nd, last

    # Yearly recurrence
    by_month = models.JSONField(null=True, blank=True)  # [1, 6, 12]

    # End conditions
    count = models.PositiveIntegerField(null=True, blank=True)
    until = models.DateField(null=True, blank=True)

class CalendarResource(models.Model):
    """Bookable resources (vehicles, equipment, rooms)"""
    RESOURCE_TYPE_CHOICES = [
        ('vehicle', 'Vehicle'),
        ('equipment', 'Equipment'),
        ('room', 'Meeting Room'),
        ('facilitator', 'Facilitator'),
    ]

    name = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES)
    capacity = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    # Conflict detection
    def check_availability(self, start_date, end_date):
        """Check if resource is available for booking"""
        pass

class CalendarResourceBooking(models.Model):
    """Resource scheduling with conflict detection"""
    resource = models.ForeignKey(CalendarResource, on_delete=models.CASCADE)
    work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('requested', 'Requested'),
            ('confirmed', 'Confirmed'),
            ('cancelled', 'Cancelled'),
        ],
        default='requested'
    )

class CalendarNotification(models.Model):
    """Multi-channel notifications"""
    NOTIFICATION_TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App'),
    ]

    work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPE_CHOICES)
    minutes_before = models.IntegerField(default=15)
    is_enabled = models.BooleanField(default=True)

class ExternalCalendarSync(models.Model):
    """Google/Outlook/Apple calendar sync"""
    PROVIDER_CHOICES = [
        ('google', 'Google Calendar'),
        ('outlook', 'Outlook'),
        ('apple', 'Apple Calendar'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.CharField(max_length=10, choices=PROVIDER_CHOICES)
    access_token = models.TextField()
    refresh_token = models.TextField()
    last_sync = models.DateTimeField(null=True, blank=True)
```

##### E. Staff Management
```python
class StaffTeam(models.Model):
    """Operational teams"""
    name = models.CharField(max_length=200)
    focus_area = models.CharField(
        max_length=50,
        choices=[
            ('strategy', 'Strategic Planning'),
            ('implementation', 'Implementation'),
            ('monitoring', 'Monitoring & Evaluation'),
        ]
    )

class StaffTeamMembership(models.Model):
    """Team assignments with roles"""
    team = models.ForeignKey(StaffTeam, on_delete=models.CASCADE)
    staff = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20,
        choices=[
            ('lead', 'Team Lead'),
            ('member', 'Member'),
            ('coordinator', 'Coordinator'),
        ]
    )

class TrainingProgram(models.Model):
    """Staff development programs"""
    title = models.CharField(max_length=255)
    provider = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    competencies_covered = models.JSONField(default=list)

class TrainingEnrollment(models.Model):
    """Training participation tracking"""
    program = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE)
    staff = models.ForeignKey(User, on_delete=models.CASCADE)
    completion_status = models.CharField(max_length=20)

class PerformanceTarget(models.Model):
    """KPI tracking"""
    TARGET_LEVEL_CHOICES = [
        ('individual', 'Individual'),
        ('team', 'Team'),
        ('office', 'Office-wide'),
    ]

    title = models.CharField(max_length=255)
    target_level = models.CharField(max_length=20, choices=TARGET_LEVEL_CHOICES)
    metric = models.CharField(max_length=100)
    target_value = models.DecimalField(max_digits=10, decimal_places=2)
    actual_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    period = models.CharField(max_length=20)  # Q1-2025, FY2025
```

#### Views & URLs

**URL Namespace:** `common`

```python
# src/common/urls.py

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Administrative hierarchy
    path('regions/', views.region_list, name='region_list'),
    path('provinces/', views.province_list, name='province_list'),
    path('municipalities/', views.municipality_list, name='municipality_list'),
    path('barangays/', views.barangay_list, name='barangay_list'),

    # Staff management
    path('staff/', views.staff_list, name='staff_management'),
    path('staff/<int:pk>/', views.staff_detail, name='staff_detail'),
    path('teams/', views.team_list, name='team_list'),

    # Work items (unified)
    path('work-items/', views.work_item_list, name='work_item_list'),
    path('work-items/<int:pk>/', views.work_item_detail, name='work_item_detail'),

    # Calendar
    path('calendar/', views.calendar_view, name='oobc_calendar'),
    path('calendar/resources/', views.resource_list, name='resource_list'),

    # User approvals
    path('approvals/', views.user_approvals, name='user_approvals'),
]
```

**API Endpoints:**
```python
# src/common/api_urls.py

urlpatterns = [
    path('regions/', views.RegionListAPIView.as_view()),
    path('provinces/', views.ProvinceListAPIView.as_view()),
    path('municipalities/', views.MunicipalityListAPIView.as_view()),
    path('barangays/', views.BarangayListAPIView.as_view()),
]
```

---

### 2. COMMUNITIES APP (OBC Data)

**Location:** `src/communities/`
**Purpose:** Comprehensive community profiling and demographic tracking

#### Key Models

```python
# src/communities/models.py

class CommunityProfileBase(models.Model):
    """Abstract base class for community profiles"""

    # 11-Section Profile
    # 1. Basic Demographics
    total_population = models.IntegerField(default=0)
    households = models.IntegerField(default=0)
    age_demographics = models.JSONField(default=dict)  # children, youth, adults

    # 2. Vulnerable Sectors
    pwd_count = models.IntegerField(default=0)
    solo_parents = models.IntegerField(default=0)
    idps = models.IntegerField(default=0)
    farmers = models.IntegerField(default=0)
    fisherfolk = models.IntegerField(default=0)

    # 3. Socio-Economic Indicators
    average_income = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    unemployment_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    # 4. Cultural Context
    ethnolinguistic_groups = models.JSONField(default=list)
    primary_language = models.CharField(max_length=100)

    # 5. Islamic Facilities
    mosques = models.IntegerField(default=0)
    madrasah = models.IntegerField(default=0)
    asatidz_count = models.IntegerField(default=0)

    # 6-11. (Infrastructure, Services, Governance, etc.)

    class Meta:
        abstract = True

class OBCCommunity(CommunityProfileBase):
    """Barangay-level OBC community"""
    barangay = models.OneToOneField('common.Barangay', on_delete=models.CASCADE)

    # Ethnolinguistic groups (13 groups)
    ETHNOLINGUISTIC_CHOICES = [
        ('maguindanaon', 'Maguindanaon'),
        ('tausug', 'Tausug'),
        ('yakan', 'Yakan'),
        ('sama', 'Sama'),
        ('maranao', 'Maranao'),
        ('kalibugan', 'Kalibugan'),
        ('sangil', 'Sangil'),
        ('molbog', 'Molbog'),
        ('jama_mapun', 'Jama Mapun'),
        ('palawani', 'Palawani'),
        ('iranun', 'Iranun'),
        ('teduray', 'Teduray'),
        ('lambangian', 'Lambangian'),
    ]

    dominant_ethnolinguistic_group = models.CharField(
        max_length=50,
        choices=ETHNOLINGUISTIC_CHOICES
    )

    # Settlement classification
    settlement_type = models.CharField(
        max_length=20,
        choices=[
            ('urban', 'Urban'),
            ('rural', 'Rural'),
            ('coastal', 'Coastal'),
            ('upland', 'Upland'),
        ]
    )

    # Geographic coordinates
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)

    # Proximity to BARMM
    proximity_to_barmm = models.CharField(
        max_length=20,
        choices=[
            ('adjacent', 'Adjacent to BARMM'),
            ('nearby', 'Nearby (< 50km)'),
            ('distant', 'Distant (> 50km)'),
        ]
    )

    # Soft delete
    is_deleted = models.BooleanField(default=False)

class MunicipalityCoverage(models.Model):
    """Municipality-level OBC aggregation"""
    municipality = models.OneToOneField('common.Municipality', on_delete=models.CASCADE)

    # Auto-synced from barangay OBCs
    total_obc_population = models.IntegerField(default=0)
    covered_barangays = models.IntegerField(default=0)
    key_barangays = models.JSONField(default=list)

    last_synced = models.DateTimeField(auto_now=True)

class ProvinceCoverage(models.Model):
    """Province-level OBC aggregation"""
    province = models.OneToOneField('common.Province', on_delete=models.CASCADE)

    # Auto-synced from municipal coverages
    total_obc_population = models.IntegerField(default=0)
    covered_municipalities = models.IntegerField(default=0)

    # Submission workflow (MANA participants)
    submission_status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
        ],
        default='draft'
    )

class CommunityLivelihood(models.Model):
    """Economic activities tracking"""
    community = models.ForeignKey(OBCCommunity, on_delete=models.CASCADE)

    LIVELIHOOD_CATEGORIES = [
        ('agriculture', 'Agriculture/Farming'),
        ('fishing', 'Fishing'),
        ('livestock', 'Livestock Raising'),
        ('trading', 'Trading/Retail'),
        ('handicraft', 'Handicraft/Weaving'),
        ('transport', 'Transportation Services'),
        ('construction', 'Construction'),
        ('government', 'Government Employment'),
        ('professional', 'Professional Services'),
        ('remittance', 'OFW Remittances'),
        ('other', 'Other'),
    ]

    livelihood_category = models.CharField(max_length=20, choices=LIVELIHOOD_CATEGORIES)
    households_engaged = models.IntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    is_seasonal = models.BooleanField(default=False)

class Stakeholder(models.Model):
    """Community stakeholders"""
    community = models.ForeignKey(OBCCommunity, on_delete=models.CASCADE)

    STAKEHOLDER_TYPES = [
        ('imam', 'Imam'),
        ('elder', 'Community Elder'),
        ('ustadz', 'Ustadz'),
        ('datu', 'Datu'),
        ('chieftain', 'Chieftain'),
        ('barangay_official', 'Barangay Official'),
        ('women_leader', 'Women Leader'),
        ('youth_leader', 'Youth Leader'),
        ('teacher', 'Teacher'),
        ('health_worker', 'Health Worker'),
        ('farmer_leader', 'Farmer Leader'),
        ('fisherfolk_leader', 'Fisherfolk Leader'),
        ('business_owner', 'Business Owner'),
        ('ngo_representative', 'NGO Representative'),
    ]

    stakeholder_type = models.CharField(max_length=30, choices=STAKEHOLDER_TYPES)
    name = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=20, blank=True)
    influence_level = models.CharField(
        max_length=10,
        choices=[
            ('high', 'High'),
            ('medium', 'Medium'),
            ('low', 'Low'),
        ]
    )

class GeographicDataLayer(models.Model):
    """Map layers (moved from MANA)"""
    LAYER_TYPE_CHOICES = [
        ('point', 'Point'),
        ('line', 'Line'),
        ('polygon', 'Polygon'),
        ('raster', 'Raster'),
        ('heatmap', 'Heatmap'),
        ('cluster', 'Cluster'),
    ]

    name = models.CharField(max_length=200)
    layer_type = models.CharField(max_length=20, choices=LAYER_TYPE_CHOICES)
    geojson_data = models.JSONField()  # GeoJSON format
    style = models.JSONField(default=dict)  # Leaflet styling
    is_visible_by_default = models.BooleanField(default=False)
    access_level = models.CharField(max_length=20)
```

#### Views & URLs

**URL Namespace:** `common` (communities routes)

```python
# src/communities/urls.py (included in common)

urlpatterns = [
    # Barangay OBCs
    path('communities/', views.obc_list, name='communities_manage'),
    path('communities/<int:pk>/', views.obc_detail, name='obc_detail'),
    path('communities/<int:pk>/edit/', views.obc_edit, name='obc_edit'),

    # Municipal OBCs
    path('communities/municipal/', views.municipal_coverage_list, name='communities_manage_municipal'),

    # Provincial OBCs
    path('communities/provincial/', views.provincial_coverage_list, name='communities_manage_provincial'),

    # Geographic data
    path('communities/geographic-data/', views.geographic_layers, name='mana_geographic_data'),

    # Stakeholders
    path('communities/<int:community_pk>/stakeholders/', views.stakeholder_list, name='stakeholder_list'),
]
```

---

### 3. MANA APP (Mapping and Needs Assessment)

**Location:** `src/mana/`
**Purpose:** Systematic community needs assessment and mapping

#### Key Models

```python
# src/mana/models.py

class Assessment(models.Model):
    """MANA assessment session"""
    title = models.CharField(max_length=255)
    community = models.ForeignKey('communities.OBCCommunity', on_delete=models.CASCADE)
    assessment_date = models.DateField()

    # Assessment type
    assessment_type = models.CharField(
        max_length=20,
        choices=[
            ('baseline', 'Baseline'),
            ('thematic', 'Thematic'),
            ('follow_up', 'Follow-up'),
        ]
    )

    # Themes (SERC)
    themes = models.JSONField(default=list)  # Social, Economic, Rights, Cultural

    status = models.CharField(
        max_length=20,
        choices=[
            ('planning', 'Planning'),
            ('ongoing', 'Ongoing'),
            ('completed', 'Completed'),
            ('validated', 'Validated'),
        ],
        default='planning'
    )

class AssessmentParticipant(models.Model):
    """Workshop participants"""
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    user = models.ForeignKey('common.User', on_delete=models.CASCADE)

    PARTICIPANT_TYPE_CHOICES = [
        ('elder', 'Community Elder'),
        ('women_leader', 'Women Leader'),
        ('youth', 'Youth Representative'),
        ('religious', 'Religious Leader'),
        ('government', 'Government Official'),
    ]

    participant_type = models.CharField(max_length=20, choices=PARTICIPANT_TYPE_CHOICES)

    # Sequential workshop progress
    workshop_1_completed = models.BooleanField(default=False)
    workshop_2_completed = models.BooleanField(default=False)
    workshop_3_completed = models.BooleanField(default=False)
    workshop_4_completed = models.BooleanField(default=False)
    workshop_5_completed = models.BooleanField(default=False)

class AssessmentFinding(models.Model):
    """Assessment results"""
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)

    FINDING_TYPE_CHOICES = [
        ('strength', 'Community Strength'),
        ('need', 'Identified Need'),
        ('gap', 'Service Gap'),
        ('opportunity', 'Development Opportunity'),
        ('risk', 'Risk/Challenge'),
    ]

    finding_type = models.CharField(max_length=20, choices=FINDING_TYPE_CHOICES)
    description = models.TextField()
    priority_level = models.CharField(max_length=10)
    affected_sectors = models.JSONField(default=list)

class AssessmentRecommendation(models.Model):
    """Action recommendations"""
    finding = models.ForeignKey(AssessmentFinding, on_delete=models.CASCADE)
    recommendation = models.TextField()
    responsible_agency = models.CharField(max_length=200)
    timeframe = models.CharField(max_length=50)
    estimated_budget = models.DecimalField(max_digits=12, decimal_places=2, null=True)
```

#### Views & URLs

**URL Namespace:** `common` (MANA routes)

```python
# src/mana/urls.py (included in common)

urlpatterns = [
    # Regional/Provincial overviews (staff)
    path('mana/regional/', views.regional_overview, name='mana_regional_overview'),
    path('mana/provincial/', views.provincial_overview, name='mana_provincial_overview'),

    # Assessment tools (staff)
    path('mana/desk-review/', views.desk_review, name='mana_desk_review'),
    path('mana/survey/', views.survey_module, name='mana_survey_module'),
    path('mana/kii/', views.kii_module, name='mana_kii'),

    # Sequential workshops (participants)
    path('mana/workshops/assessments/<int:assessment_id>/participant/',
         views.participant_workshop, name='mana_participant_workshop'),
]
```

---

### 4. COORDINATION APP (Multi-Stakeholder Partnerships)

**Location:** `src/coordination/`
**Purpose:** Partnership management and stakeholder engagement

#### Key Models

```python
# src/coordination/models.py

class Organization(models.Model):
    """Partner organizations"""
    ORGANIZATION_TYPE_CHOICES = [
        ('bmoa', 'BARMM Ministry/Office/Agency'),
        ('lgu', 'Local Government Unit'),
        ('nga', 'National Government Agency'),
        ('ingo', 'International NGO'),
        ('lngo', 'Local NGO'),
        ('cso', 'Civil Society Organization'),
        ('academic', 'Academic Institution'),
        ('religious', 'Religious Organization'),
        ('private', 'Private Sector'),
        ('coop', 'Cooperative'),
        ('assoc', 'Association'),
        ('media', 'Media Organization'),
        ('donor', 'Donor Agency'),
    ]

    name = models.CharField(max_length=255)
    organization_type = models.CharField(max_length=20, choices=ORGANIZATION_TYPE_CHOICES)

    # Government agencies only
    mandate = models.TextField(blank=True)
    powers = models.JSONField(default=list)

    # Geographic hierarchy linkage
    region = models.ForeignKey('common.Region', null=True, on_delete=models.SET_NULL)
    province = models.ForeignKey('common.Province', null=True, on_delete=models.SET_NULL)
    municipality = models.ForeignKey('common.Municipality', null=True, on_delete=models.SET_NULL)

    # Key personnel
    head_official = models.CharField(max_length=200, blank=True)
    focal_person = models.CharField(max_length=200, blank=True)

    # Engagement metrics
    partnership_level = models.CharField(
        max_length=20,
        choices=[
            ('strategic', 'Strategic Partner'),
            ('active', 'Active Partner'),
            ('occasional', 'Occasional Partner'),
            ('potential', 'Potential Partner'),
        ]
    )

    budget_size = models.CharField(max_length=20, blank=True)
    staff_count = models.IntegerField(null=True, blank=True)

class Partnership(models.Model):
    """Formal partnership agreements"""
    PARTNERSHIP_TYPE_CHOICES = [
        ('moa', 'Memorandum of Agreement'),
        ('mou', 'Memorandum of Understanding'),
        ('contract', 'Service Contract'),
        ('grant', 'Grant Agreement'),
        ('joint_program', 'Joint Program'),
        ('network', 'Network/Coalition'),
        ('technical', 'Technical Cooperation'),
        ('exchange', 'Knowledge Exchange'),
        ('secondment', 'Staff Secondment'),
    ]

    title = models.CharField(max_length=255)
    partnership_type = models.CharField(max_length=20, choices=PARTNERSHIP_TYPE_CHOICES)

    # Multi-organization support
    organizations = models.ManyToManyField(Organization, related_name='partnerships')

    # Status workflow
    status = models.CharField(
        max_length=20,
        choices=[
            ('concept', 'Concept'),
            ('draft', 'Draft'),
            ('review', 'Under Review'),
            ('negotiation', 'Negotiation'),
            ('pending_signature', 'Pending Signature'),
            ('active', 'Active'),
            ('suspended', 'Suspended'),
            ('completed', 'Completed'),
            ('expired', 'Expired'),
            ('terminated', 'Terminated'),
            ('renewed', 'Renewed'),
            ('archived', 'Archived'),
        ],
        default='concept'
    )

    # Timeline
    start_date = models.DateField()
    end_date = models.DateField()

    # Budget
    total_budget = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    contribution_breakdown = models.JSONField(default=dict)

    # Performance
    performance_indicators = models.JSONField(default=list)
    risk_factors = models.JSONField(default=list)

class StakeholderEngagement(models.Model):
    """Engagement activities"""
    ENGAGEMENT_TYPE_CHOICES = [
        ('consultation', 'Consultation'),
        ('meeting', 'Meeting'),
        ('workshop', 'Workshop'),
        ('fgd', 'Focus Group Discussion'),
        ('interview', 'Interview'),
        ('field_visit', 'Field Visit'),
        ('conference', 'Conference'),
        ('training', 'Training'),
        ('ceremonial', 'Ceremonial Event'),
        ('monitoring', 'Monitoring Visit'),
    ]

    title = models.CharField(max_length=255)
    engagement_type = models.CharField(max_length=20, choices=ENGAGEMENT_TYPE_CHOICES)
    organizations = models.ManyToManyField(Organization)

    # Related work item
    work_item = models.ForeignKey('common.WorkItem', null=True, on_delete=models.SET_NULL)

    # Linked assessment (if MANA-related)
    related_assessment = models.ForeignKey('mana.Assessment', null=True, on_delete=models.SET_NULL)

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('planned', 'Planned'),
            ('confirmed', 'Confirmed'),
            ('ongoing', 'Ongoing'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
            ('postponed', 'Postponed'),
        ],
        default='planned'
    )

    # Attendance
    attendance = models.JSONField(default=dict)  # {org_id: participant_count}

    # Outcomes
    key_outcomes = models.TextField(blank=True)
    feedback_summary = models.TextField(blank=True)
    satisfaction_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True)

class Communication(models.Model):
    """Communication tracking"""
    COMMUNICATION_TYPE_CHOICES = [
        ('email', 'Email'),
        ('letter', 'Official Letter'),
        ('memo', 'Memorandum'),
        ('meeting', 'In-Person Meeting'),
        ('phone', 'Phone Call'),
        ('video', 'Video Conference'),
        ('sms', 'SMS'),
        ('social_media', 'Social Media'),
        ('portal', 'Online Portal'),
        ('report', 'Report'),
        ('presentation', 'Presentation'),
        ('press_release', 'Press Release'),
        ('announcement', 'Public Announcement'),
        ('newsletter', 'Newsletter'),
        ('endorsement', 'Endorsement Letter'),
    ]

    subject = models.CharField(max_length=255)
    communication_type = models.CharField(max_length=20, choices=COMMUNICATION_TYPE_CHOICES)

    # Direction
    direction = models.CharField(
        max_length=10,
        choices=[
            ('incoming', 'Incoming'),
            ('outgoing', 'Outgoing'),
            ('internal', 'Internal'),
        ]
    )

    # Organizations involved
    from_organization = models.ForeignKey(
        Organization,
        related_name='sent_communications',
        on_delete=models.CASCADE
    )
    to_organizations = models.ManyToManyField(
        Organization,
        related_name='received_communications'
    )

    # Priority
    priority = models.CharField(
        max_length=10,
        choices=[
            ('urgent', 'Urgent'),
            ('high', 'High'),
            ('normal', 'Normal'),
            ('low', 'Low'),
        ],
        default='normal'
    )

    # Follow-up
    requires_response = models.BooleanField(default=False)
    response_deadline = models.DateField(null=True, blank=True)
    response_status = models.CharField(max_length=20, blank=True)
```

#### Views & URLs

**URL Namespace:** `common` (coordination routes)

```python
# src/coordination/urls.py (included in common)

urlpatterns = [
    # Organizations
    path('coordination/organizations/', views.organization_list, name='coordination_organizations'),
    path('coordination/organizations/<int:pk>/', views.organization_detail, name='organization_detail'),

    # Partnerships
    path('coordination/partnerships/', views.partnership_list, name='coordination_partnerships'),
    path('coordination/partnerships/<int:pk>/', views.partnership_detail, name='partnership_detail'),

    # Engagements
    path('coordination/events/', views.engagement_list, name='coordination_events'),
    path('coordination/events/<int:pk>/', views.engagement_detail, name='engagement_detail'),

    # Communications
    path('coordination/communications/', views.communication_list, name='communication_list'),
]
```

---

### 5. MONITORING APP (M&E System)

**Location:** `src/monitoring/`
**Purpose:** Monitor Programs, Projects, and Activities (PPAs) of MOAs

#### Key Models (Inferred)

```python
# src/monitoring/models.py (inferred structure)

class MOA(models.Model):
    """Ministry, Office, or Agency"""
    organization = models.OneToOneField('coordination.Organization', on_delete=models.CASCADE)
    # Additional MOA-specific fields

class PPA(models.Model):
    """Program, Project, or Activity"""
    moa = models.ForeignKey(MOA, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    ppa_type = models.CharField(
        max_length=10,
        choices=[
            ('program', 'Program'),
            ('project', 'Project'),
            ('activity', 'Activity'),
        ]
    )
    budget = models.DecimalField(max_digits=14, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()

    # Beneficiary tracking
    target_communities = models.ManyToManyField('communities.OBCCommunity')
    beneficiary_count = models.IntegerField(default=0)
```

#### Views & URLs

**URL Namespace:** `monitoring`

```python
# src/monitoring/urls.py

urlpatterns = [
    path('', views.me_home, name='home'),
    path('moa-ppas/', views.moa_ppa_list, name='moa_ppas'),
    path('oobc-initiatives/', views.oobc_initiatives, name='oobc_initiatives'),
    path('obc-requests/', views.obc_requests, name='obc_requests'),
]
```

---

### 6. PROJECT_CENTRAL APP (Project Management)

**Location:** `src/project_central/`
**Purpose:** Integrated project management portal

#### URLs

**URL Namespace:** `project_central`

```python
# src/project_central/urls.py

urlpatterns = [
    path('portfolio/', views.portfolio_dashboard, name='portfolio_dashboard'),
    path('analytics/', views.me_analytics_dashboard, name='me_analytics_dashboard'),
    path('resources/', views.resource_management, name='resource_management'),
]
```

**Legacy Redirects:**
```python
# src/obc_management/urls.py

# Redirect /project-central/* to /project-management/*
path('project-central/', RedirectView.as_view(url='/project-management/', permanent=True)),
```

---

### 7. RECOMMENDATIONS APP (Policy System)

**Location:** `src/recommendations/`
**Purpose:** Parent app for policy recommendations

#### Sub-Apps

**A. recommendations.policies** - Policy tracking
**B. recommendations.documents** - Document management
**C. recommendations.policy_tracking** - Implementation monitoring

#### URLs

**URL Namespaces:** Various

```python
# src/recommendations/policies/urls.py

urlpatterns = [
    path('', views.policy_list, name='recommendations_manage'),
    path('<int:pk>/', views.policy_detail, name='policy_detail'),
    path('programs/', views.programs_list, name='recommendations_programs'),
    path('services/', views.services_list, name='recommendations_services'),
]

# src/recommendations/documents/urls.py

urlpatterns = [
    path('', views.document_repository, name='document_list'),
    path('<int:pk>/', views.document_detail, name='document_detail'),
]
```

---

## URL Organization

### Main URL Patterns

```python
# src/obc_management/urls.py

urlpatterns = [
    # Health checks
    path("health/", health_check),
    path("ready/", readiness_check),

    # Admin
    path("admin/", admin.site.urls),

    # Main apps
    path("", include("common.urls")),  # Dashboard, staff, calendar, OBC data, MANA, Coordination
    path("policies/", include("recommendations.policies.urls")),
    path("monitoring/", include("monitoring.urls")),
    path("project-management/", include("project_central.urls")),
    path("documents/", include("recommendations.documents.urls")),

    # API v1 (current stable)
    path("api/v1/", include("api.v1.urls")),

    # Legacy API (to be migrated)
    path("api/administrative/", include("common.api_urls")),
    path("api/communities/", include("communities.api_urls")),
    path("api/mana/", include("mana.api_urls")),
    path("api/coordination/", include("coordination.api_urls")),
    path("api/policies/", include("recommendations.policies.api_urls")),

    # Authentication
    path("api-auth/", include("rest_framework.urls")),
]
```

---

## Inter-App Dependencies

### Dependency Graph

```
common (foundation)
  ├─→ communities (uses Region, Province, Municipality, Barangay, User)
  ├─→ mana (uses User, WorkItem)
  ├─→ coordination (uses User, WorkItem, Region, Province)
  ├─→ monitoring (uses User)
  ├─→ recommendations (uses User)
  └─→ project_central (uses User, WorkItem)

communities
  ├─→ coordination (OBCCommunity referenced)
  └─→ mana (OBCCommunity referenced)

mana
  ├─→ communities (Assessment.community → OBCCommunity)
  └─→ coordination (StakeholderEngagement.related_assessment)

coordination
  ├─→ mana (StakeholderEngagement.related_assessment)
  └─→ monitoring (Organization used for MOA tracking)

monitoring
  └─→ coordination (Organization for MOAs)
  └─→ communities (PPA.target_communities → OBCCommunity)
```

### Shared Models (Cross-Module)

| Model | Source App | Used By |
|-------|------------|---------|
| **User** | common | All apps |
| **Region/Province/Municipality/Barangay** | common | communities, mana, coordination |
| **WorkItem** | common | coordination, project_central |
| **OBCCommunity** | communities | mana, coordination, monitoring |
| **Organization** | coordination | monitoring (MOA tracking) |
| **Assessment** | mana | coordination (engagement linking) |

---

## Technical Architecture

### 1. WorkItem Migration (Unified Work Hierarchy)

**Background:** Legacy models created fragmentation:
- `common.models.StaffTask` (staff tasks)
- `coordination.models.Event` (engagements/activities)
- `project_central.models.ProjectWorkflow` (project workflows)

**Solution:** Single `WorkItem` model with polymorphic behavior

**Implementation:**
```python
# All work items in one table
WorkItem(work_type='task')      # Replaces StaffTask
WorkItem(work_type='activity')  # Replaces Event
WorkItem(work_type='project')   # Replaces ProjectWorkflow

# Proxy models for backward compatibility
StaffTaskProxy → filters WorkItem(work_type='task')
EventProxy → filters WorkItem(work_type='activity')
ProjectWorkflowProxy → filters WorkItem(work_type='project')
```

**Benefits:**
- ✅ Unified calendar view
- ✅ Hierarchical task structure (MPTT)
- ✅ Single API endpoint for all work
- ✅ Consistent status workflow
- ✅ Simplified queries and reporting

**See:** `docs/refactor/WORKITEM_MIGRATION_COMPLETE.md`

---

### 2. Geographic Data (Production-Ready)

**Decision:** Use JSONField (NOT PostGIS)

**Implementation:**
```python
class Region(models.Model):
    # PostgreSQL automatically uses 'jsonb' type for JSONField
    boundary_geojson = models.JSONField(null=True, blank=True)  # GeoJSON
    center_coordinates = models.JSONField(null=True, blank=True)  # {lat, lng}
    bounding_box = models.JSONField(null=True, blank=True)  # [[S,W],[N,E]]
```

**PostgreSQL Storage:**
- Automatically uses `jsonb` type (efficient, indexed)
- Supports JSON operators (->>, ->, @>, etc.)
- Human-readable (easy debugging)
- Perfect for Leaflet.js (GeoJSON native)

**Why NOT PostGIS:**
- Current use case: Display boundaries, store coordinates
- NOT needed: Spatial joins, distance queries, geometric calculations
- Avoid unnecessary complexity and dependencies

**See:** `docs/improvements/geography/GEOGRAPHIC_DATA_IMPLEMENTATION.md`

---

### 3. Two MANA Systems (Isolation)

**Decision:** Legacy MANA (staff) + Sequential Workshops (participants) remain separate

**Staff MANA:**
- URLs: `/mana/regional/`, `/mana/provincial/`, `/mana/desk-review/`
- Multi-assessment management
- Aggregate analysis tools
- Full administrative control

**Participant Workshops:**
- URLs: `/mana/workshops/assessments/{id}/participant/`
- 5-workshop sequential progression
- Gated access (cannot skip workshops)
- Focused, simplified UX

**Enforcement:**
- Middleware (`ManaParticipantAccessMiddleware`)
- View-level permission checks
- Separate URL namespaces

---

### 4. Case-Insensitive Queries (PostgreSQL Compatibility)

**Critical:** PostgreSQL is case-sensitive by default (unlike SQLite)

**Standard Practice:**
```python
# ❌ BAD: Case-sensitive
Region.objects.filter(name__contains='BARMM')

# ✅ GOOD: Case-insensitive
Region.objects.filter(name__icontains='BARMM')
User.objects.filter(email__iexact='admin@oobc.gov')
```

**Lookup Reference:**
- `__icontains` - Case-insensitive contains
- `__istartswith` - Case-insensitive starts with
- `__iendswith` - Case-insensitive ends with
- `__iexact` - Case-insensitive exact match

**Status:** ✅ OBCMS codebase 100% compatible (verified via audit)

**See:** `docs/deployment/CASE_SENSITIVE_QUERY_AUDIT.md`

---

## Database Strategy

### Development
- **Database:** SQLite (`db.sqlite3`)
- **Location:** `src/db.sqlite3`
- **⚠️ CRITICAL:** NEVER delete the database (contains valuable dev data)

### Production
- **Database:** PostgreSQL
- **Migration:** 118 migrations verified compatible
- **Geographic Data:** JSONField (NO PostGIS extension needed)
- **Connection Pooling:** `CONN_MAX_AGE = 600` (production settings)

### Migration Process

```bash
# 1. Create PostgreSQL database
CREATE DATABASE obcms_prod ENCODING 'UTF8';
CREATE USER obcms_user WITH PASSWORD 'secure-password';
GRANT ALL PRIVILEGES ON DATABASE obcms_prod TO obcms_user;

# 2. Update .env
DATABASE_URL=postgres://obcms_user:password@localhost:5432/obcms_prod

# 3. Run migrations
cd src
python manage.py migrate

# Expected: All 118 migrations apply successfully in 2-5 minutes
```

**See:** `docs/deployment/POSTGRESQL_MIGRATION_SUMMARY.md`

---

## API Architecture

### Versioned APIs

**Current Stable:** `/api/v1/`
```python
# src/api/v1/urls.py

urlpatterns = [
    path('communities/', include('api.v1.communities_urls')),
    path('coordination/', include('api.v1.coordination_urls')),
    path('mana/', include('api.v1.mana_urls')),
]
```

**Legacy APIs:** (Being migrated, deprecation warnings)
```python
path("api/administrative/", include("common.api_urls")),
path("api/communities/", include("communities.api_urls")),
path("api/mana/", include("mana.api_urls")),
path("api/coordination/", include("coordination.api_urls")),
```

### API Features

- **Django REST Framework** with pagination, filtering, ordering
- **JWT Authentication** via `djangorestframework-simplejwt`
- **Browsable API** for development (`/api/v1/`)
- **Versioning** for backward compatibility

### Example API Endpoints

```python
# Communities
GET /api/v1/communities/ - List OBC communities
GET /api/v1/communities/{id}/ - Community detail
POST /api/v1/communities/ - Create community (staff only)

# GeoJSON Endpoints
GET /api/v1/communities/geojson/ - All communities as GeoJSON
GET /api/v1/regions/{id}/boundary/ - Region boundary GeoJSON

# Coordination
GET /api/v1/coordination/organizations/ - List organizations
GET /api/v1/coordination/partnerships/ - List partnerships

# MANA
GET /api/v1/mana/assessments/ - List assessments
GET /api/v1/mana/findings/ - Assessment findings
```

---

## Third-Party Integrations

### Backend Libraries

| Package | Purpose |
|---------|---------|
| `django-filters` | Advanced filtering for APIs |
| `django-extensions` | Developer utilities (`shell_plus`, `graph_models`) |
| `django-crispy-forms` | Form rendering |
| `django-auditlog` | Compliance logging |
| `django-axes` | Failed login tracking |
| `django-mptt` | Hierarchical data (WorkItem) |
| `djangorestframework` | RESTful APIs |
| `djangorestframework-simplejwt` | JWT authentication |

### Frontend Integrations

| Library | Purpose |
|---------|---------|
| **HTMX** | Instant UI updates (no full page reloads) |
| **Tailwind CSS** | Responsive, government-appropriate styling |
| **Alpine.js** | Minimal JavaScript reactivity |
| **Leaflet.js** | Interactive maps (GeoJSON native) |
| **FullCalendar** | Advanced calendar UI |
| **FontAwesome 5** | Icon library |

---

## Testing Strategy

### Test Coverage

**Overall:** 99.2% (254/256 tests passing)

**Test Types:**
- Unit tests: Model validation, business logic
- Integration tests: API endpoints, workflows
- Performance tests: Calendar rendering, resource booking (83% pass rate)

**Run Tests:**
```bash
pytest -v
pytest tests/performance/ -v
coverage run -m pytest
coverage report
```

**See:** `docs/testing/PERFORMANCE_TEST_RESULTS.md`

---

## Deployment Readiness

### Key Documents
1. **[PostgreSQL Migration Summary](../../deployment/POSTGRESQL_MIGRATION_SUMMARY.md)** ⭐ READ FIRST
2. **[PostgreSQL Migration Review](../../deployment/POSTGRESQL_MIGRATION_REVIEW.md)** ⭐ TECHNICAL
3. **[Staging Environment Guide](../../env/staging-complete.md)** ⭐ 12-STEP PROCEDURE

### Deployment Checklist
- ✅ 118 migrations PostgreSQL-compatible
- ✅ Geographic data JSONField (NO PostGIS)
- ✅ Case-insensitive queries 100% compatible
- ✅ Security settings production-ready
- ✅ Performance optimizations (connection pooling)
- ✅ UI refinements complete

---

## Related Documentation

- [User-Facing Organization](01-user-facing-organization.md) - Navigation and user flows
- [Domain Architecture](03-domain-architecture.md) - Module relationships and business logic
- [Module Navigation Mapping](04-module-navigation-mapping.md) - Quick reference

---

**Last Updated:** 2025-10-12
**Django Version:** 4.2
**Python Version:** 3.12
**Database:** SQLite (dev) → PostgreSQL (production-ready)
