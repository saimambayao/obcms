# GEMINI.md

This file provides guidance to Gemini when working with code in this repository.

## BMMS Critical Definition

**BMMS = Bangsamoro Ministerial Management System**

**NOT "Bangsamoro Management & Monitoring System"** - This is incorrect!

BMMS is the strategic evolution of OBCMS from a single-organization platform (OOBC) to a comprehensive multi-tenant management system serving all 44 BARMM Ministries, Offices, and Agencies (MOAs).

**Key Points:**
- BMMS serves **MINISTRIES** (hence "Ministerial")
- 44 MOAs (Ministries, Offices, and Agencies)
- Multi-tenant architecture with organization-based data isolation
- Office of the Chief Minister (OCM) - NOT "CMO" - provides centralized oversight

**Always use:** "Bangsamoro Ministerial Management System"
**Never use:** "Bangsamoro Management & Monitoring System"

## Key Terminology

### Core Acronyms
- **OBCMS**: Office for Other Bangsamoro Communities Management System
- **BMMS**: Bangsamoro Ministerial Management System (NOT "Management & Monitoring")
- **OCM**: Office of the Chief Minister (NOT "CMO" or "Chief Minister's Office")
- **MOA**: Ministry, Office, or Agency (44 total in BARMM)
- **BARMM**: Bangsamoro Autonomous Region in Muslim Mindanao
- **OOBC**: Office for Other Bangsamoro Communities

### Module-Specific Terms
- **MANA**: Mapping and Needs Assessment
- **PPA**: Program, Project, or Activity
- **M&E**: Monitoring and Evaluation
- **OBC**: Other Bangsamoro Communities

### Organizational Structure
- **44 MOAs**: 16 Ministries (including OCM) + 28 Other Offices and Agencies (including OOBC)
- **Pilot MOAs**: MOH (Ministry of Health), MOLE (Ministry of Labor and Employment), MAFAR (Ministry of Agriculture, Fisheries and Agrarian Reform)

## Development Guidelines

### 1. Always Use Correct Terminology
- ✅ "Bangsamoro Ministerial Management System" (BMMS)
- ✅ "Office of the Chief Minister" (OCM)
- ❌ "Bangsamoro Management & Monitoring System"
- ❌ "CMO" or "Chief Minister's Office"

### 2. Django Project Structure
- **Main Project**: src/obc_management/
- **Applications**: common, communities, mana, coordination, policies
- **Virtual Environment**: venv/ (Python 3.12)
- **Working Directory**: Always cd src/ before running Django commands

### 3. Multi-Tenant Architecture
- Every MOA has isolated data (MOA A cannot see MOA B's data)
- OCM has read-only aggregated view across all MOAs
- Always use organization-scoped queries in views and APIs
- Test data isolation rigorously (100% pass rate required)

### 4. Database Guidelines
- **Development**: SQLite (src/db.sqlite3)
- **Production**: PostgreSQL (NO PostGIS required)
- **Geographic Data**: Use JSONField (automatically uses jsonb in PostgreSQL)
- **Text Search**: Always use case-insensitive lookups (__icontains, __iexact, __istartswith)

### 5. UI/UX Standards
- Follow OBCMS UI Standards Master Guide (docs/ui/OBCMS_UI_STANDARDS_MASTER.md)
- Use 3D milk white stat cards with semantic icon colors
- Implement HTMX for instant UI updates (no full page reloads)
- Maintain WCAG 2.1 AA accessibility compliance
- Touch targets minimum 48px

### 6. Code Quality
- Format code with Black and isort
- Write comprehensive tests (pytest)
- Use DRF for APIs with proper serializers
- Follow Django naming conventions

### 7. Documentation
- All new documentation goes in docs/ directory
- Update docs/README.md index when creating new docs
- Use relative links within documentation
- Follow naming convention: lowercase with underscores

### 8. Security and Compliance
- Enforce data isolation (organization-based access control)
- Implement audit logging for all sensitive operations
- Follow Data Privacy Act 2012 compliance for beneficiary data
- Use proper authentication and authorization (JWT + session)

## BMMS Implementation Phases

**Current Status:** ✅ Planning Complete - Ready for Phase 1

**Phase Order:**
1. **Phase 1**: Foundation (Organizations App) - CRITICAL
2. **Phase 2**: Planning Module (NEW) - HIGH
3. **Phase 3**: Budgeting Module (Parliament Bill No. 325) - CRITICAL
4. **Phase 4**: Coordination Enhancement - MEDIUM
5. **Phase 5**: Module Migration (MANA/M&E/Policies) - MEDIUM
6. **Phase 6**: OCM Aggregation - HIGH
7. **Phase 7**: Pilot MOA Onboarding (3 MOAs) - HIGH
8. **Phase 8**: Full Rollout (44 MOAs) - MEDIUM

**Additional Phases:**
- **BEN-I**: Individual Beneficiary Database
- **BEN-O**: Organizational Beneficiary Database
- **URL**: URL Refactoring (Monolithic Router Anti-Pattern Fix)
- **TEST**: Continuous Testing Strategy

## Common Development Commands

### Virtual Environment
```bash
./scripts/bootstrap_venv.sh  # idempotent helper
source venv/bin/activate
```

### Database Operations
```bash
cd src
./manage.py makemigrations
./manage.py migrate
./manage.py createsuperuser
```

### Development Server
```bash
cd src
./manage.py runserver
# Access at http://localhost:8000
# Admin: http://localhost:8000/admin/
```

### Code Quality
```bash
black .
isort .
flake8
pytest
```

## Reference Documentation

For comprehensive development guidelines, refer to:

- **[CLAUDE.md](CLAUDE.md)** - Complete development guidelines
- **[AGENTS.md](AGENTS.md)** - Agent-specific guidelines
- **[docs/plans/bmms/README.md](docs/plans/bmms/README.md)** - BMMS planning overview
- **[docs/plans/bmms/TRANSITION_PLAN.md](docs/plans/bmms/TRANSITION_PLAN.md)** - Complete 8-phase implementation guide
- **[docs/README.md](docs/README.md)** - Full documentation index
- **[docs/ui/OBCMS_UI_STANDARDS_MASTER.md](docs/ui/OBCMS_UI_STANDARDS_MASTER.md)** - UI/UX standards

## Quick Reference

### Organization-Scoped Query Pattern
```python
# Always filter by organization
if request.user.is_ocm_user:
    # OCM sees all organizations (read-only)
    queryset = Model.objects.all()
else:
    # MOA users see only their organization's data
    queryset = Model.objects.filter(organization=request.user.organization)
```

### Case-Insensitive Query Pattern
```python
# ❌ BAD: Case-sensitive (PostgreSQL)
Region.objects.filter(name__contains='BARMM')

# ✅ GOOD: Case-insensitive (works everywhere)
Region.objects.filter(name__icontains='BARMM')
```

### Geographic Data Pattern
```python
# GeoJSON boundaries (automatic jsonb in PostgreSQL)
class Region(models.Model):
    boundary_geojson = models.JSONField(null=True, blank=True)
    center_coordinates = models.JSONField(null=True, blank=True)
    bounding_box = models.JSONField(null=True, blank=True)
```

## Contact

For questions or clarifications:
- **Technical:** OBCMS System Architect (Claude Sonnet 4.5)
- **Project Management:** BMMS Project Manager
- **Stakeholders:** OOBC Director, OCM Representative, Pilot MOA Leads

---

**Remember:** BMMS = Bangsamoro **Ministerial** Management System (serving **Ministries**)
**Remember:** OCM = **Office** of the Chief Minister (NOT "CMO")
