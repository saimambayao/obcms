# Organizational Beneficiary Models - Executive Summary

**Date:** October 12, 2025
**Status:** ✅ Design Complete
**Designer:** OBCMS System Architect (Claude Sonnet 4.5)

---

## Quick Overview

This document summarizes the Django model design for **Organizational Beneficiaries** in BMMS - organizations that benefit from government programs (cooperatives, associations, businesses, LGUs, NGOs).

**Full Documentation:** [ORGANIZATIONAL_BENEFICIARY_MODELS.md](ORGANIZATIONAL_BENEFICIARY_MODELS.md)

---

## Three Core Models

### 1. OrganizationalBeneficiary
**Purpose:** Track organizations that benefit from government programs

**Key Features:**
- Organization profile (name, type, registration details)
- Geographic location (Barangay → Municipality → Province → Region)
- Contact information (contact person, phone, email)
- MOA attribution (which MOA registered this beneficiary)
- Verification workflow (is_verified, verified_by, verification_date)
- Membership count (for cooperatives, associations)

**Primary Key:** UUID
**Unique Identifier:** `unique_id` (SEC/DTI registration or auto-generated)

---

### 2. OrganizationalBeneficiaryEnrollment
**Purpose:** Track enrollment of organizations in specific PPAs

**Key Features:**
- Links OrganizationalBeneficiary to ProgramProjectActivity (PPA)
- Enrollment status (enrolled, active, completed, withdrawn)
- MOA attribution (which MOA enrolled them)
- Expected vs. actual impact metrics
- Enrollment date and completion tracking

**Unique Constraint:** One organization can only enroll once per PPA

---

### 3. OrganizationalBeneficiaryMember (Optional)
**Purpose:** Link organizational beneficiaries to individual beneficiaries

**Key Features:**
- Membership relationship (who belongs to which organization)
- Membership role (member, officer, president, treasurer, etc.)
- Membership dates (start/end)
- Active status tracking

**Use Case:** Track officers and key members of cooperatives/associations

---

## Database Relationships

```
┌─────────────────────────────────┐
│ OrganizationalBeneficiary       │
│ ───────────────────────────── │
│ • id (UUID, PK)                 │
│ • organization_name             │
│ • organization_type             │
│ • unique_id (UNIQUE)            │
│ • barangay (FK)                 │
│ • municipality (FK)             │
│ • created_by_organization (FK)  │
│ • is_verified, verified_by      │
└─────────────────────────────────┘
           │
           │ 1:N
           ▼
┌─────────────────────────────────┐
│ OrganizationalBeneficiary       │
│      Enrollment                 │
│ ───────────────────────────── │
│ • id (UUID, PK)                 │
│ • organizational_beneficiary    │
│ • ppa (FK to PPA)               │
│ • organization (FK to MOA)      │
│ • enrollment_date               │
│ • status (enrolled/active)      │
│ • expected_impact               │
└─────────────────────────────────┘
           │
           │ 1:N
           ▼
┌─────────────────────────────────┐
│ OrganizationalBeneficiary       │
│       Member                    │
│ ───────────────────────────── │
│ • id (UUID, PK)                 │
│ • organizational_beneficiary    │
│ • individual_beneficiary (FK)   │
│ • membership_role               │
│ • membership_start_date         │
└─────────────────────────────────┘
```

---

## Integration with OBCMS/BMMS

### Geographic Hierarchy (Existing)
```
Region → Province → Municipality → Barangay
```
OrganizationalBeneficiary links to Barangay and Municipality from `common.models`

### MOA Attribution (BMMS Core)
```
Organization (MOA) → OrganizationalBeneficiary
Organization (MOA) → OrganizationalBeneficiaryEnrollment
```
Each organizational beneficiary is "owned" by a specific MOA (Ministry/Office/Agency).

**Data Isolation:** MOA A cannot see organizational beneficiaries registered by MOA B.

### PPA Integration (Phase 2)
```
ProgramProjectActivity → OrganizationalBeneficiaryEnrollment
```
Organizations enroll in PPAs (Programs, Projects, Activities) from the planning module.

---

## Organization Types Supported

1. **Cooperative** - CDA-registered cooperatives
2. **Association** - SEC-registered associations
3. **Business** - Private businesses (DTI/SEC)
4. **LGU** - Local Government Units
5. **NGO** - Non-Governmental Organizations
6. **CBO** - Community-Based Organizations
7. **People's Organization**
8. **Federation** - Federations of cooperatives/associations
9. **Union** - Labor unions
10. **Guild** - Professional guilds
11. **Social Enterprise**
12. **Foundation**
13. **Other**

---

## Key Fields

### OrganizationalBeneficiary
```python
# Identification
unique_id = "REG-SEC-12345" or "ORG-A1B2C3D4"
organization_name = "Balangasan Farmers Cooperative"
organization_type = "cooperative"

# Registration
registration_number = "CDA-12345"
registration_date = date(2020, 1, 15)
registration_agency = "Cooperative Development Authority"

# Contact
contact_person_name = "Juan Dela Cruz"
contact_person_position = "President"
contact_number = "09171234567"
email = "balangasanfarmer@example.com"

# Location
address = "Purok 1, Balangasan"
barangay = Barangay.objects.get(code='BALANGASAN')
municipality = Municipality.objects.get(code='PAGADIAN')

# BMMS Attribution
created_by_organization = Organization.objects.get(acronym='MAFAR')

# Verification
is_verified = True
verified_by = User.objects.get(username='mafar_verifier')
verified_date = date(2024, 3, 1)

# Status
is_active = True
number_of_members = 150
```

---

## Verification Workflow

### Step 1: Registration
MOA staff registers an organizational beneficiary:
```python
org_beneficiary = OrganizationalBeneficiary.objects.create(
    organization_name="Balangasan Farmers Cooperative",
    organization_type="cooperative",
    # ... other fields
    created_by_organization=mafar_organization,
    is_verified=False,  # Pending verification
)
```

### Step 2: Verification
MOA verifier confirms legitimacy:
```python
org_beneficiary.is_verified = True
org_beneficiary.verified_by = verifier_user
org_beneficiary.verified_date = timezone.now().date()
org_beneficiary.verification_notes = "Verified CDA registration certificate"
org_beneficiary.save()
```

### Step 3: Enrollment
After verification, organization can be enrolled in PPAs:
```python
enrollment = OrganizationalBeneficiaryEnrollment.objects.create(
    organizational_beneficiary=org_beneficiary,
    ppa=irrigation_ppa,
    organization=mafar_organization,
    status='enrolled',
    expected_members_served=150,
)
```

---

## Business Rules

### Validation Rules
1. ✅ **Geographic Hierarchy:** Barangay must belong to selected Municipality
2. ✅ **Verification Required:** Only verified organizations can be enrolled in PPAs
3. ✅ **Active Status:** Cannot enroll inactive organizations
4. ✅ **Unique Enrollment:** One organization can only enroll once per PPA
5. ✅ **Date Validation:** End dates must be after start dates
6. ✅ **MOA Attribution:** All beneficiaries must be attributed to a specific MOA

### Auto-Generated Fields
- `unique_id`: Auto-generated if not provided (uses registration number or UUID)
- `municipality`: Auto-populated from barangay if not specified
- `created_at`, `updated_at`: Automatic timestamps

---

## Sample Queries

### Filter by MOA (Organization-Scoped)
```python
# Get all organizational beneficiaries registered by MAFAR
mafar_beneficiaries = OrganizationalBeneficiary.objects.filter(
    created_by_organization__acronym='MAFAR'
)

# Get active cooperatives in Zamboanga Peninsula
zambo_coops = OrganizationalBeneficiary.objects.filter(
    organization_type='cooperative',
    is_active=True,
    municipality__province__region__code='IX'
)
```

### Get Enrollments by Status
```python
# Active enrollments for a specific PPA
active_enrollments = OrganizationalBeneficiaryEnrollment.objects.filter(
    ppa=irrigation_ppa,
    status='active'
).select_related('organizational_beneficiary', 'organization')
```

### Members of an Organization
```python
# Get all officers of a cooperative
officers = OrganizationalBeneficiaryMember.objects.filter(
    organizational_beneficiary=balangasan_coop,
    membership_role__in=['president', 'vice_president', 'treasurer'],
    is_active=True
)
```

---

## Performance Optimizations

### Strategic Indexes
- `organization_name` (text search)
- `organization_type`, `is_active` (filtering)
- `barangay`, `municipality` (geographic queries)
- `created_by_organization`, `is_verified` (MOA scoping)
- `enrollment_date`, `status` (timeline queries)

### Efficient Query Patterns
```python
# Fetch with related data (reduce N+1 queries)
orgs = OrganizationalBeneficiary.objects.select_related(
    'barangay__municipality__province__region',
    'created_by_organization',
    'verified_by'
).prefetch_related(
    'enrollments__ppa'
)
```

---

## Migration Strategy

### Phase 1 (Current) - Foundation
```bash
# Create OrganizationalBeneficiary model
python manage.py makemigrations beneficiaries
python manage.py migrate beneficiaries
```

**Dependencies:**
- ✅ `common.models` (Barangay, Municipality)
- ✅ `coordination.models` (Organization)

---

### Phase 2 (After Planning Module) - Enrollments
```bash
# Create OrganizationalBeneficiaryEnrollment model
python manage.py makemigrations beneficiaries
python manage.py migrate beneficiaries
```

**Dependencies:**
- ✅ OrganizationalBeneficiary (Phase 1)
- ⏳ `planning.ProgramProjectActivity` (Phase 2 of BMMS)

---

### Phase 3 (After Individual Beneficiary Tracking) - Members
```bash
# Create OrganizationalBeneficiaryMember model
python manage.py makemigrations beneficiaries
python manage.py migrate beneficiaries
```

**Dependencies:**
- ✅ OrganizationalBeneficiary (Phase 1)
- ⏳ `beneficiaries.IndividualBeneficiary` (Future)

---

## Admin Interface

### OrganizationalBeneficiary Admin
- **List View:** Name, Type, Municipality, Barangay, Verified, Active, MOA
- **Filters:** Organization Type, Verified Status, Active Status, MOA, Region
- **Search:** Name, Unique ID, Registration Number, Contact Person
- **Fieldsets:** Profile, Registration, Contact, Location, BMMS Attribution, Verification, Status, Metadata

### OrganizationalBeneficiaryEnrollment Admin
- **List View:** Organization, PPA, Status, Enrollment Date, MOA, Expected Impact
- **Filters:** Status, MOA, Enrollment Date
- **Search:** Organization Name, PPA Name

### OrganizationalBeneficiaryMember Admin
- **List View:** Individual, Organization, Role, Start Date, Active
- **Filters:** Role, Active Status, Start Date
- **Search:** Organization Name, Individual Name

---

## API Endpoints (Recommended)

```
GET    /api/organizational-beneficiaries/
POST   /api/organizational-beneficiaries/
GET    /api/organizational-beneficiaries/<uuid:pk>/
PUT    /api/organizational-beneficiaries/<uuid:pk>/
DELETE /api/organizational-beneficiaries/<uuid:pk>/

GET    /api/organizational-beneficiaries/<uuid:org_id>/enrollments/
POST   /api/organizational-beneficiaries/<uuid:org_id>/enrollments/
GET    /api/enrollments/<uuid:pk>/
PUT    /api/enrollments/<uuid:pk>/

GET    /api/organizational-beneficiaries/<uuid:org_id>/members/
POST   /api/organizational-beneficiaries/<uuid:org_id>/members/
GET    /api/members/<uuid:pk>/

POST   /api/organizational-beneficiaries/<uuid:pk>/verify/

GET    /api/organizational-beneficiaries/stats/
```

---

## Security & Access Control

### MOA Scoping
- Each organizational beneficiary belongs to one MOA
- MOA staff can only see/edit their own organization's beneficiaries
- OCM (Office of the Chief Minister) sees aggregated read-only data from all MOAs

### Verification Workflow
- New organizations start as `is_verified=False`
- Only authorized MOA staff can verify organizations
- Only verified organizations can be enrolled in PPAs

### Audit Trail
- `created_by` - User who created the record
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp
- `verified_by`, `verified_date` - Verification tracking
- `notes` - Additional context/history

---

## Testing Checklist

### Unit Tests
- ✅ Model creation and validation
- ✅ Geographic hierarchy validation (barangay → municipality)
- ✅ Unique constraints (unique_id, organization per PPA)
- ✅ Business rules (verification required, active status)
- ✅ Auto-generated fields (unique_id, municipality)
- ✅ Property methods (province, region, enrollment_count)

### Integration Tests
- ✅ Admin interface CRUD operations
- ✅ API endpoints (list, create, retrieve, update, delete)
- ✅ Verification workflow
- ✅ Enrollment workflow (with PPA)
- ✅ Member management

### Performance Tests
- ✅ Query optimization with select_related/prefetch_related
- ✅ Index usage verification
- ✅ Large dataset handling (1000+ organizations)

---

## Implementation Checklist

### Prerequisites
- [ ] Review BMMS TRANSITION_PLAN.md
- [ ] Verify coordination.Organization model exists
- [ ] Verify common.models (Barangay, Municipality) exist
- [ ] Confirm User model configuration

### Implementation Steps
- [ ] Create Django app: `python manage.py startapp beneficiaries`
- [ ] Copy OrganizationalBeneficiary model to models.py
- [ ] Create migrations: `python manage.py makemigrations beneficiaries`
- [ ] Apply migrations: `python manage.py migrate beneficiaries`
- [ ] Register admin interface (admin.py)
- [ ] Create serializers (serializers.py)
- [ ] Create views and URLs (views.py, urls.py)
- [ ] Write tests (tests/test_models.py, tests/test_api.py)
- [ ] Run tests: `pytest beneficiaries/`
- [ ] Update documentation

---

## Benefits

### For BMMS
- ✅ **Organization-Scoped:** Full MOA attribution and data isolation
- ✅ **Geographic Integration:** Seamless integration with existing OBCMS hierarchy
- ✅ **Extensible:** Ready for PPA enrollments and individual member linkage
- ✅ **Production-Ready:** Comprehensive validation, indexes, and audit trails

### For MOAs
- ✅ **Track Beneficiary Organizations:** Know which organizations benefit from programs
- ✅ **Verification Workflow:** Ensure legitimacy before enrollment
- ✅ **Impact Measurement:** Track expected vs. actual impact
- ✅ **Membership Tracking:** Link organizations to individual beneficiaries

### For Organizations
- ✅ **Official Recognition:** Formal registration in government system
- ✅ **Access to Programs:** Enroll in PPAs and government initiatives
- ✅ **Transparent Process:** Clear verification and enrollment workflow
- ✅ **Data Privacy:** MOA-specific data isolation

---

## Next Steps

1. **Review & Approve:** Review this design with BMMS stakeholders
2. **Create Django App:** Set up `beneficiaries` app structure
3. **Implement Phase 1:** OrganizationalBeneficiary model
4. **Build Admin Interface:** Configure Django admin for data entry
5. **Create API:** Build RESTful endpoints for frontend integration
6. **Build UI:** Design user interface for organizational beneficiary management
7. **User Training:** Train MOA staff on organizational beneficiary tracking
8. **Phase 2 Integration:** Add enrollments after planning module is ready
9. **Phase 3 Integration:** Add member linkage after individual beneficiary tracking is ready

---

## Questions?

For detailed implementation guidance, see:
- **[ORGANIZATIONAL_BENEFICIARY_MODELS.md](ORGANIZATIONAL_BENEFICIARY_MODELS.md)** - Complete model specification
- **[BMMS TRANSITION_PLAN.md](TRANSITION_PLAN.md)** - Full BMMS implementation plan
- **[OBCMS Development Guide](../../development/README.md)** - Development guidelines

---

**Document Version:** 1.0
**Last Updated:** October 12, 2025
**Status:** ✅ Design Complete - Ready for Implementation
**Prepared by:** OBCMS System Architect (Claude Sonnet 4.5)
