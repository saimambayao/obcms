# OBCMS Modules and Applications Documentation

**Last Updated:** 2025-10-12
**System Version:** OBCMS v1.0 (Django 4.2, Python 3.12)
**Purpose:** Comprehensive guide to OBCMS system organization

---

## Overview

The **OBC Management System (OBCMS)** is a comprehensive digital platform serving the Office for Other Bangsamoro Communities (OOBC) in supporting Bangsamoro communities outside the BARMM (Bangsamoro Autonomous Region in Muslim Mindanao). The system operates across **Regions IX, X, XI, and XII** and provides integrated management for communities, coordination, monitoring, and policy development.

This documentation provides three complementary perspectives:

1. **User-Facing Organization** - How users navigate and interact with the system
2. **Technical Organization** - How the codebase is structured (Django apps)
3. **Domain Architecture** - How modules relate to each other and support the OOBC mission

---

## Documentation Structure

### Core Documents

1. **[01-user-facing-organization.md](01-user-facing-organization.md)** ⭐ **Start Here**
   - Navigation menu structure
   - Role-based access patterns
   - User workflows and dashboards
   - URL routing from user perspective

2. **[02-technical-organization.md](02-technical-organization.md)** 🔧 **For Developers**
   - Django app structure (14 apps)
   - Models, views, and API endpoints
   - Database architecture
   - Inter-app dependencies

3. **[03-domain-architecture.md](03-domain-architecture.md)** 📊 **For System Understanding**
   - Module purposes and use cases
   - Cross-module data flow
   - User workflows across modules
   - Business logic and mission alignment

4. **[04-module-navigation-mapping.md](04-module-navigation-mapping.md)** 🗺️ **Integration View**
   - How navbar maps to Django apps
   - URL patterns to code locations
   - Quick reference for finding features

---

## Quick Reference

### System Modules (User Perspective)

| Navigation Label | Module Purpose | Primary Users |
|------------------|----------------|---------------|
| **OBC Data** | Community profiles and demographics | OOBC Staff, Analysts |
| **MANA** | Mapping and needs assessment | Facilitators, Participants |
| **Coordination** | Multi-stakeholder partnerships | Coordination Officers, MOA Staff |
| **Recommendations** | Evidence-based policy proposals | Policy Officers, Executives |
| **M&E** | Monitoring projects and programs | M&E Officers, MOA Staff |
| **OOBC Mgt** | Internal operations and planning | OOBC Staff, Executives |

### Django Applications (Technical Perspective)

| App Name | Domain | Key Models |
|----------|--------|------------|
| `common` | Foundation | User, Region, Province, Municipality, Barangay, WorkItem |
| `communities` | Community Data | OBCCommunity, MunicipalityCoverage, ProvinceCoverage |
| `mana` | Assessments | Assessment, AssessmentParticipant, AssessmentFinding |
| `coordination` | Partnerships | Organization, Partnership, StakeholderEngagement |
| `monitoring` | M&E System | (PPAs, MOAs, Performance tracking) |
| `recommendations` | Policy System | (Policy recommendations, tracking) |
| `project_central` | Project Mgmt | (Projects, workflows, resources) |

---

## Key System Features

### 🌍 **Geographic Hierarchy**
```
Region → Province → Municipality → Barangay → OBC Community
```
- **13 ethnolinguistic groups** tracked across geographic levels
- **JSONField** for GeoJSON boundaries (NO PostGIS required)
- **Auto-aggregation** from barangay to municipal to provincial levels

### 👥 **Role-Based Access**
- **OOBC Staff** - Full system access (6 main modules)
- **MOA Focal Users** - Limited to their organization profile and M&E reporting
- **MANA Participants** - Sequential workshop access only
- **Community Leaders** - Read-only community profiles

### 🔄 **Unified Work Management**
- **WorkItem Model** - Single hierarchy for tasks, activities, projects
- **MPTT (Modified Preorder Tree Traversal)** - Efficient hierarchical queries
- **Calendar Integration** - All work items visible in unified calendar

### 📅 **Advanced Calendar System**
- **RFC 5545 Compliant** - iCalendar recurrence patterns
- **Resource Booking** - Vehicles, equipment, rooms, facilitators
- **Multi-channel Notifications** - Email, SMS, push, in-app
- **External Calendar Sync** - Google, Outlook, Apple

### 🤖 **AI Capabilities**
- **Communities:** Data validation, needs classification, similarity matching
- **MANA:** Response analysis, theme extraction, auto-report generation
- **Coordination:** Stakeholder matching, partnership prediction, meeting summarization
- **Policies:** Evidence synthesis, impact simulation, compliance checking
- **M&E:** Budget anomaly detection, timeline prediction, performance forecasting
- **Staff:** Conversational AI chat, natural language queries

---

## System Architecture Highlights

### 1. **Evidence-Based Cycle**
```
Communities → MANA → Policies → Coordination → M&E → (feedback) Communities
```

### 2. **Two MANA Systems** (Isolated)
- **Legacy MANA** - Staff multi-assessment management (`/mana/regional/`)
- **Sequential Workshops** - Participant 5-workshop progression (`/mana/workshops/`)

### 3. **PostgreSQL-Ready**
- ✅ **118 migrations** verified compatible
- ✅ **Case-insensitive queries** (100% audited)
- ✅ **JSONField geographic data** (no PostGIS dependency)
- ✅ **Production settings** hardened and optimized

### 4. **Modern Tech Stack**
- **Backend:** Django 4.2, Python 3.12, PostgreSQL
- **Frontend:** HTMX, Tailwind CSS, Alpine.js
- **Maps:** Leaflet.js with GeoJSON
- **Calendar:** FullCalendar with advanced features
- **API:** Django REST Framework with JWT auth

---

## Getting Started

### For Users
👉 Start with **[01-user-facing-organization.md](01-user-facing-organization.md)** to understand how to navigate the system.

### For Developers
👉 Start with **[02-technical-organization.md](02-technical-organization.md)** to understand the codebase structure.

### For System Architects
👉 Start with **[03-domain-architecture.md](03-domain-architecture.md)** to understand business logic and module relationships.

### For Quick Reference
👉 Use **[04-module-navigation-mapping.md](04-module-navigation-mapping.md)** to find specific features quickly.

---

## Related Documentation

### Deployment & Operations
- [PostgreSQL Migration Summary](../../deployment/POSTGRESQL_MIGRATION_SUMMARY.md)
- [Staging Environment Guide](../../env/staging-complete.md)
- [Production Deployment Checklist](../../deployment/deployment-coolify.md)

### Development Guidelines
- [CLAUDE.md](../../../CLAUDE.md) - AI assistant guidance
- [Development Guide](../../development/README.md) - Developer setup
- [UI Components & Standards](../../ui/OBCMS_UI_COMPONENTS_STANDARDS.md)

### Testing & Quality
- [Performance Test Results](../../testing/PERFORMANCE_TEST_RESULTS.md)
- [Test Coverage Reports](../../testing/)

### Feature Documentation
- [WorkItem Migration](../../refactor/WORKITEM_MIGRATION_COMPLETE.md)
- [Geographic Data Implementation](../../improvements/geography/GEOGRAPHIC_DATA_IMPLEMENTATION.md)
- [Calendar System Documentation](../../improvements/calendar/)

---

## Contribution Guidelines

When working with OBCMS modules:

1. ✅ **Follow UI Standards** - Reference [OBCMS_UI_COMPONENTS_STANDARDS.md](../../ui/OBCMS_UI_COMPONENTS_STANDARDS.md)
2. ✅ **Maintain Role-Based Access** - Respect permission filters
3. ✅ **Use Case-Insensitive Queries** - Always use `__icontains`, `__iexact`
4. ✅ **Document New Features** - Update relevant module documentation
5. ✅ **Test Across Roles** - Verify OOBC Staff, MOA, MANA Participant views
6. ✅ **Update API Docs** - Document new endpoints in API v1

---

## Support & Resources

- **Technical Issues:** See [GitHub Issues](https://github.com/oobc/obcms/issues)
- **User Documentation:** [docs/guidelines/](../../guidelines/)
- **API Documentation:** [API v1 Reference](../../api/v1/)
- **Training Materials:** [docs/training/](../../training/)

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-12 | Initial comprehensive documentation | Claude Code |

---

**For Questions:** Contact OBCMS Development Team
