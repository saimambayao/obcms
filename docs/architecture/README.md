# Architecture Documentation

This directory contains comprehensive architectural documentation for the OBCMS/BMMS system.

## Documents

### [System Architecture Overview](./SYSTEM_ARCHITECTURE_OVERVIEW.md)
**Primary Document**: Complete technical architecture of the OBCMS/BMMS system including:
- Technology stack analysis
- Module structure following client interface
- Database and security architecture
- Performance and deployment considerations
- BMMS transition roadmap

### Quick Reference

#### System Overview
- **Current State**: OBCMS (single-tenant for OOBC)
- **Target State**: BMMS (multi-tenant for 44 BARMM MOAs)
- **Architecture**: Modular monolithic with microservices readiness
- **Framework**: Django 5.2.0 with DRF 3.14.0

#### Key Technologies
- **Backend**: Python 3.12, Django 5.2, PostgreSQL, Redis, Celery
- **Frontend**: Tailwind CSS, HTMX, Vanilla JavaScript, Django Templates
- **Infrastructure**: Docker, Sevalla/Coolify, Gunicorn, Nginx
- **AI**: Google Gemini 2.5 Flash, Vector Search (12,450+ embeddings)

#### Module Structure (Client Interface)
1. **Foundation Layer**
   - `common/` - Core models, users, calendar
   - `organizations/` - BMMS multi-tenant foundation

2. **Primary User Modules (Main Navigation)**
   - `communities/` - OBC Data management
   - `mana/` - Needs assessment
   - `coordination/` - Partnerships & communication
   - `recommendations/` - Policies & programs
   - `monitoring/` - M&E with OCM oversight

3. **Administrative Modules**
   - `budget_preparation/` & `budget_execution/` - Financial management
   - `planning/` - Strategic planning
   - `ocm/` - Office of Chief Minister

4. **Supporting Systems**
   - `ai_assistant/` - AI-powered features
   - `services/` - Service catalog
   - `project_central/` - Project management

#### Architecture Highlights
- **Multi-Tenant**: Organization-based data isolation
- **Security**: Comprehensive audit logging and RBAC
- **Scalability**: Connection pooling, caching, background tasks
- **Compliance**: Parliament Bill No. 325, Data Privacy Act 2012
- **Accessibility**: WCAG 2.1 AA compliance

---

## Related Documentation

- [Development Guide](../development/README.md) - Development setup and guidelines
- [Deployment Guide](../deployment/) - Production deployment procedures
- [UI Standards](../ui/OBCMS_UI_STANDARDS_MASTER.md) - UI/UX design standards
- [BMMS Planning](../plans/bmms/README.md) - BMMS implementation planning
- [Testing Documentation](../testing/) - Testing strategies and results
- [API Documentation](../api/) - REST API specifications

---

*Last Updated: October 16, 2025*