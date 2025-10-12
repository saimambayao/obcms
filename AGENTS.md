# AGENTS.md

This file provides guidance to AI agents working with code in this repository.

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

## Agent Guidelines

### 1. Always Use Correct Terminology
- ✅ "Bangsamoro Ministerial Management System" (BMMS)
- ✅ "Office of the Chief Minister" (OCM)
- ❌ "Bangsamoro Management & Monitoring System"
- ❌ "CMO" or "Chief Minister's Office"

### 2. Multi-Tenant Architecture Awareness
- Every MOA has isolated data (MOA A cannot see MOA B's data)
- OCM has read-only aggregated view across all MOAs
- Always use organization-scoped queries in views and APIs
- Test data isolation rigorously (100% pass rate required)

### 3. Django Development Patterns
- Use timezone-aware datetime fields (USE_TZ = True)
- Implement proper __str__ methods for admin interface
- Use DRF for APIs with proper serializers and permissions
- Follow organization-scoped filtering patterns

### 4. Code Quality Standards
- Format code with Black and isort
- Write comprehensive tests (unit, integration, component, performance)
- Maintain WCAG 2.1 AA accessibility compliance
- Use HTMX for instant UI updates (no full page reloads)

### 5. Security and Compliance
- Enforce data isolation (organization-based access control)
- Implement audit logging for all sensitive operations
- Follow Data Privacy Act 2012 compliance for beneficiary data
- Use proper authentication and authorization (JWT + session)

### 6. Documentation
- All new documentation goes in docs/ directory
- Update docs/README.md index when creating new docs
- Use relative links within documentation
- Follow naming convention: lowercase with underscores

### 7. Testing Requirements
- **Data Isolation**: 100% pass rate required
- **Performance**: Dashboard loads < 200ms, API responses < 100ms
- **Accessibility**: WCAG 2.1 AA compliance mandatory
- **Security**: Organization boundary enforcement tested

### 8. BMMS Implementation Phases

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

## Reference Documentation

For comprehensive development guidelines, refer to:

- **[CLAUDE.md](CLAUDE.md)** - Complete development guidelines for Claude Code
- **[docs/plans/bmms/README.md](docs/plans/bmms/README.md)** - BMMS planning overview
- **[docs/plans/bmms/TRANSITION_PLAN.md](docs/plans/bmms/TRANSITION_PLAN.md)** - Complete 8-phase implementation guide
- **[docs/README.md](docs/README.md)** - Full documentation index
- **[docs/ui/OBCMS_UI_STANDARDS_MASTER.md](docs/ui/OBCMS_UI_STANDARDS_MASTER.md)** - UI/UX standards

## Contact

For questions or clarifications:
- **Technical:** OBCMS System Architect (Claude Sonnet 4.5)
- **Project Management:** BMMS Project Manager
- **Stakeholders:** OOBC Director, OCM Representative, Pilot MOA Leads

---

**Remember:** BMMS = Bangsamoro **Ministerial** Management System (serving **Ministries**)
**Remember:** OCM = **Office** of the Chief Minister (NOT "CMO")
