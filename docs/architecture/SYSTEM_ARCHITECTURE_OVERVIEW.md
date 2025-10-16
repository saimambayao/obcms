# OBCMS/BMMS System Architecture Overview

**Version**: 1.0
**Date**: October 16, 2025
**Status**: Production Ready (OBCMS) → BMMS Implementation in Progress

---

## Executive Summary

The **Office for Other Bangsamoro Communities Management System (OBCMS)** is a comprehensive Django-based platform designed for community development and governmental operations. The system is currently transitioning to become the **Bangsamoro Ministerial Management System (BMMS)** - a multi-tenant system that will serve all 44 BARMM Ministries, Offices, and Agencies (MOAs).

This document provides a complete architectural overview of the system, including technology stack, application modules, and design patterns following the client interfacing structure.

---

## Technology Stack

### Backend Technologies

#### Core Framework
- **Python**: 3.12 (Primary runtime)
- **Django**: 5.2.0 (Web framework)
- **Django REST Framework**: 3.14.0 (API development)

#### Database Technologies
- **Development**: SQLite with comprehensive data integrity
- **Production**: PostgreSQL 17-alpine with connection pooling
- **Geographic Data**: JSONField with GeoJSON (no PostGIS required)

#### Authentication & Security
- **JWT Authentication**: SimpleJWT 5.3.0 (1-hour access, 7-day refresh)
- **Security Monitoring**: Django Axes 6.1.0 (failed login tracking)
- **Audit Logging**: Django Auditlog 3.0.0 (comprehensive audit trails)
- **Rate Limiting**: Django Ratelimit 4.1.0 with custom throttling

#### Background Task Processing
- **Celery**: 5.3.0 (distributed task queue)
- **Redis**: 5.0.0 (message broker and caching)
- **Task Scheduling**: Celery Beat with database scheduler

### Frontend Technologies

#### Core Web Technologies
- **HTML**: HTML5 with semantic markup
- **CSS**: Tailwind CSS 3.4.17 with custom Bangsamoro theming
- **JavaScript**: Vanilla JS with HTMX for dynamic interactions
- **Template Engine**: Django Templates with component architecture

#### Interactive Components
- **HTMX**: Dynamic content loading without page refreshes
- **FullCalendar**: Calendar and scheduling components
- **Leaflet.js**: Interactive mapping and geographic visualization
- **Alpine.js**: Enhanced UI interactions (with vanilla JS fallback)

#### UI/UX Standards
- **Accessibility**: WCAG 2.1 AA compliance (48px minimum touch targets)
- **Responsive Design**: Mobile-first approach with breakpoint variants
- **Design System**: Custom Bangsamoro color scheme (Ocean/Emerald gradients)

### Infrastructure & Deployment

#### Containerization
- **Docker**: Multi-stage builds with optimized layers
- **Docker Compose**: Full stack orchestration
- **Production Optimization**: Gunicorn WSGI server with health checks

#### Deployment Platforms
- **Primary**: Sevalla cloud platform
- **Alternative**: Coolify container orchestration
- **Static Files**: WhiteNoise 6.6.0 with CDN support

#### Monitoring & Observability
- **Error Tracking**: Sentry SDK 1.25.0
- **Performance Monitoring**: New Relic 9.0.0
- **Application Metrics**: Django Prometheus 2.3.0
- **SQL Analysis**: Django Silk 5.0.0

---

## Application Architecture

### System Overview

The OBCMS/BMMS system follows a **modular monolithic architecture** with clear separation of concerns. The system is designed to scale from single-tenant (OBCMS) to multi-tenant (BMMS) operations serving 44 MOAs.

### Multi-Tenant Design

#### Organization-Based Data Isolation
- **Data Boundaries**: MOA A cannot see MOA B's data
- **Context Switching**: Middleware-based organization context
- **OCM Oversight**: Read-only aggregated access for Office of Chief Minister
- **Configurable Modes**: `obcms` (single-tenant) → `bmms` (multi-tenant)

#### Role-Based Access Control (RBAC)
- **User Types**: admin, oobc_executive, oobc_staff, cm_office, bmoa, lgu, nga, community_leader, researcher
- **Feature-Level Permissions**: Granular access control by module
- **MOA-Specific Permissions**: Custom decorators for Ministry-specific access
- **Audit Logging**: Comprehensive tracking of all sensitive operations

---

## Module Structure (Following Client/Navbar Interface)

### Foundation Layer

#### 1. `common/` - Core Foundation
**Purpose**: Provides shared models, utilities, and base functionality

**Key Components**:
- **User Management**: Extended user model with custom user types
- **Administrative Hierarchy**: Region → Province → Municipality → Barangay
- **Calendar System**: Resource booking, recurring events, external sync
- **Work Item Model**: Unified work hierarchy system
- **Audit Logging**: Comprehensive audit trail for compliance
- **AI Assistant**: Chat system with conversation history

**Key Models**:
- `User` (extends Django's AbstractUser)
- `Region`, `Province`, `Municipality`, `Barangay`
- `WorkItem`, `Calendar`, `ResourceBooking`
- `AIConversation`, `AIMessage`

#### 2. `organizations/` - BMMS Multi-Tenant Foundation
**Purpose**: BMMS Phase 1 foundation for organizational management

**Key Components**:
- **Organization Model**: Multi-tenant organization structure
- **Organization Context**: Middleware for context switching
- **MOA Management**: Ministry, Office, Agency categorization
- **OCM Integration**: Chief Minister oversight capabilities

---

### Primary User Modules (Main Navigation)

#### 3. `communities/` - Community Data Management
**Purpose**: Manages comprehensive community profiles and geographic data

**Navigation Path**: Dashboard → OBC Data → Select Administrative Level

**Key Components**:
- **OBCCommunity**: Detailed socio-demographic profiles (100+ fields)
- **Geographic Models**: GIS integration with GeoJSON support
- **Stakeholder Management**: Community leaders and key persons
- **Population Reconciliation**: Automated cross-level validation

**Geographic Information System**:
- **GeoJSON Support**: Native geographic data storage
- **Interactive Maps**: Leaflet.js integration
- **Spatial Data Points**: Location-based information
- **Administrative Boundaries**: Hierarchical geographic structure

**Data Categories**:
- Population demographics (age groups, vulnerable sectors)
- Cultural and religious information
- Infrastructure and service access
- Livelihood and economic activities
- Governance and leadership structures
- Development challenges and aspirations

#### 4. `mana/` - Monitoring & Assessment
**Purpose**: Needs assessment and baseline study management

**Navigation Path**: Dashboard → MANA → Regional/Provincial Views

**Key Components**:
- **Assessment**: Multi-level assessment management
- **AssessmentCategory**: Assessment types and methodologies
- **Geographic Integration**: Link with community geographic data
- **Timeline Management**: Assessment scheduling and tracking

**Assessment Types**:
- Needs Assessment (community-level needs identification)
- Baseline Study (comprehensive community profiling)
- Impact Assessment (program evaluation)
- Special Studies (targeted research)

#### 5. `coordination/` - Stakeholder Engagement
**Purpose**: Manages stakeholder relationships, partnerships, and communication

**Navigation Path**: Dashboard → Coordination → Partnerships/Activities

**Key Components**:
- **StakeholderEngagement**: IAP2 framework-based tracking
- **Organization**: Stakeholder management (BMOAs, LGUs, NGOs)
- **Partnership**: MOA/MOU management with milestones
- **Communication**: Multi-channel communication tracking
- **InterMOAPartnership**: Cross-ministry collaboration

**IAP2 Participation Levels**:
- Inform → Consult → Involve → Collaborate → Empower
- Tracking of stakeholder engagement levels
- Communication automation and scheduling

#### 6. `recommendations/` - Policy & Document Management
**Purpose**: Policy recommendations and document tracking

**Navigation Path**: Dashboard → Recommendations → Policies/Programs/Services

**Sub-modules**:
- **documents**: Document management and version control
- **policies**: Policy lifecycle tracking
- **policy_tracking**: Implementation monitoring

**Key Features**:
- Policy recommendation tracking
- Document version control
- Implementation status monitoring
- Cross-reference with community needs

#### 7. `monitoring/` - Performance Tracking
**Purpose**: Program performance monitoring and evaluation

**Navigation Path**: Dashboard → M&E → Performance Metrics

**Key Components**:
- **PPA Tracking**: Program, Project, Activity progress
- **Budget Variance**: Financial performance monitoring
- **Compliance Monitoring**: Regulatory requirement tracking
- **OCM Oversight**: Aggregated reporting for Chief Minister

**Monitoring Types**:
- Physical accomplishment tracking
- Financial utilization monitoring
- Compliance status reporting
- Impact measurement and evaluation

---

### Administrative Modules

#### 8. `budget_preparation/` & `budget_execution/` - Financial Management
**Purpose**: Budget planning and execution with compliance

**Navigation Path**: Dashboard → Budget Management → Preparation/Execution

**Compliance Features**:
- **Parliament Bill No. 325 Section 78**: Legal compliance
- **Multi-level Approvals**: Budget approval workflows
- **Financial Audit Trail**: Complete transaction logging
- **Budget Variance Tracking**: Performance monitoring

**Budget Cycle**:
1. Budget Preparation (Planning and Proposal)
2. Budget Approval (Multi-level review)
3. Budget Execution (Implementation and monitoring)
4. Budget Reporting (Performance and variance analysis)

#### 9. `planning/` - Strategic Planning
**Purpose**: Long-term strategic planning and BMMS implementation

**Navigation Path**: Dashboard → Planning → Strategic Plans

**Key Components**:
- **Strategic Plans**: Long-term development planning
- **Implementation Tracking**: Plan execution monitoring
- **BMMS Transition**: Multi-tenant implementation planning
- **Resource Allocation**: Planning resource distribution

#### 10. `ocm/` - Office of Chief Minister
**Purpose**: OCM oversight and aggregation layer

**Navigation Path**: Dashboard → OCM Oversight → Aggregated Reports

**Key Components**:
- **Aggregated Reporting**: Cross-MOA data aggregation
- **Oversight Dashboard**: Chief Minister monitoring interface
- **Policy Monitoring**: Implementation tracking across MOAs
- **Resource Allocation**: Cross-ministry resource planning

---

### Supporting Systems

#### 11. `ai_assistant/` - AI-Powered Features
**Purpose**: AI integration for intelligent assistance and analysis

**Navigation Path**: Available throughout system via chat widget

**AI Features**:
- **Google Gemini 2.5 Flash**: Natural language processing
- **Vector Search**: 12,450+ embeddings for semantic search
- **Cultural AI**: Bangsamoro-specific prompt templates
- **Intelligent Classification**: 12-category needs classification

**AI Capabilities**:
- Natural language query processing
- Semantic document search
- Automated report generation
- Cultural context understanding

#### 12. `services/` - Service Catalog
**Purpose**: Service directory and delivery tracking

**Navigation Path**: Dashboard → Services → Service Catalog/Applications

**Key Features**:
- **Service Directory**: Comprehensive service listing
- **Eligibility Management**: Service qualification criteria
- **Delivery Tracking**: Service provision monitoring
- **Impact Assessment**: Service effectiveness measurement

#### 13. `project_central/` - Project Management
**Purpose**: Integrated project management system

**Navigation Path**: Dashboard → Projects → Project Management

**Key Features**:
- **Workflow Automation**: Task and process automation
- **Resource Allocation**: Human and resource management
- **Progress Monitoring**: Real-time project tracking
- **Collaboration Tools**: Team coordination features

---

## User Interface Architecture

### Navigation Structure

#### Role-Based Navigation
The system implements **role-based navigation** that adapts based on user type:

**MOA Users**:
- Direct link to their organization (`{{ user|get_coordination_label }}`)
- Module access restricted to their scope
- Limited administrative features

**OOBC Staff**:
- Full module access with dropdown menus
- Administrative capabilities
- Cross-organization view (in OBCMS mode)

**MANA Participants**:
- Restricted to Provincial/Regional MANA views
- Limited coordination access
- Community-focused interface

#### Responsive Design
- **Desktop**: Full navigation with dropdowns and breadcrumbs
- **Mobile**: Collapsible sidebar (80vw sliding menu)
- **Tablet**: Adaptive layout with touch optimization

### Template Architecture

#### Base Template System
- **Base Template**: `src/templates/base.html` (master layout)
- **Login Template**: `src/templates/common/login.html` (authentication)
- **Dashboard Template**: `src/templates/common/dashboard.html` (main hub)

#### Component Organization
**Reusable Components** (`src/templates/components/`):
- `form_field.html`, `form_field_input.html`, `form_field_select.html`
- `modal.html`, `data_table_card.html`
- `ai_chat_widget.html`, `calendar_widget.html`, `kanban_board.html`
- `organization_selector.html`, `location_selection.html`

**Module Partials** (`src/templates/**/partials/`):
- Module-specific partials for dynamic content
- HTMX fragments for instant UI updates
- Reusable template components

### UI/UX Standards

#### Accessibility Compliance
- **WCAG 2.1 AA**: Full accessibility compliance
- **Color Contrast**: 4.5:1 ratio for text readability
- **Keyboard Navigation**: Complete keyboard support
- **Screen Reader Support**: ARIA labels and semantic HTML

#### Design System
- **Color Scheme**: Bangsamoro Ocean/Emerald gradients
- **Typography**: Consistent font hierarchy
- **Components**: Standardized UI components
- **Responsive**: Mobile-first responsive design

---

## Database Architecture

### Data Model Design

#### Administrative Hierarchy
```python
Region → Province → Municipality → Barangay
```

#### Organization Hierarchy (BMMS)
```python
Office of Chief Minister (OCM)
├── Ministry A
│   ├── Office A1
│   └── Agency A2
├── Ministry B
│   ├── Office B1
│   └── Agency B2
└── [42 more MOAs]
```

#### Data Isolation Strategy
- **Organization-Scoped Queries**: All queries filtered by organization context
- **Soft Delete**: Data preservation with audit trails
- **Temporal Tracking**: Created/updated timestamps with user attribution
- **Audit Logging**: Complete change tracking for sensitive data

### Geographic Data Implementation

#### GeoJSON Integration
- **No PostGIS Required**: Using Django JSONField for geographic data
- **Spatial Queries**: Custom database functions for geographic operations
- **Map Visualization**: Leaflet.js integration for interactive maps
- **Data Layers**: Multiple geographic data layers with styling

#### Administrative Boundaries
- **Hierarchical Structure**: Nested administrative boundaries
- **Spatial Validation**: Boundary validation and cleanup
- **Data Reconciliation**: Population data across administrative levels

---

## Security Architecture

### Authentication & Authorization

#### Multi-Layer Authentication
1. **JWT Authentication**: Stateless tokens with refresh mechanism
2. **Session Fallback**: Traditional sessions for compatibility
3. **Failed Login Tracking**: IP-based blocking with Axes
4. **Rate Limiting**: Custom throttling by user type

#### Permission System
- **Django Permissions**: Standard Django permission framework
- **Custom Decorators**: Module-specific permission checks
- **RBAC Integration**: Role-based access control
- **Feature Flags**: Conditional feature access

### Data Protection

#### Audit Logging
- **Comprehensive Logging**: All sensitive operations logged
- **Financial Audit Trail**: Parliament Bill No. 325 compliance
- **User Attribution**: All actions linked to specific users
- **Change History**: Complete change tracking

#### Security Headers
- **HSTS**: HTTP Strict Transport Security
- **CSP**: Content Security Policy
- **CORS**: Cross-Origin Resource Sharing
- **SSL Redirect**: Automatic HTTPS redirection

---

## Performance Architecture

### Caching Strategy

#### Redis Caching
- **Session Storage**: Redis-based session management
- **Query Caching**: Database query result caching
- **Fragment Caching**: Template fragment caching
- **Application-Level Caching**: Custom caching logic

#### Database Optimization
- **Connection Pooling**: PostgreSQL connection optimization
- **Query Optimization**: Strategic database indexing
- **Pagination**: Efficient data pagination
- **Bulk Operations**: Optimized bulk data operations

### Background Task Processing

#### Celery Integration
- **Task Queuing**: Asynchronous task processing
- **Scheduled Tasks**: Celery Beat for recurring tasks
- **Error Handling**: Comprehensive error tracking
- **Task Monitoring**: Flower-based task monitoring

---

## Integration Architecture

### External Service Integration

#### AI Services
- **Google Gemini API**: Natural language processing
- **Vector Database**: FAISS for semantic search
- **Local AI**: On-premise AI capabilities
- **Cultural Context**: Bangsamoro-specific AI training

#### Communication Services
- **Email Services**: Multi-provider email delivery
- **SMS Integration**: Twilio for SMS notifications
- **Calendar Sync**: Google, Outlook, Apple Calendar
- **Push Notifications**: Real-time notifications

### API Architecture

#### REST API Design
- **DRF Integration**: Django REST Framework for APIs
- **Versioning**: API versioning support (`/api/v1/`)
- **Authentication**: JWT-based API authentication
- **Documentation**: OpenAPI 3.0 specification

#### Data Import/Export
- **Bulk Import**: Excel/CSV data import capabilities
- **Data Validation**: Comprehensive data validation
- **Export Formats**: Multiple export format support
- **Integration APIs**: External system integration

---

## Deployment Architecture

### Container Strategy

#### Multi-Stage Docker Build
1. **Node.js Stage**: Tailwind CSS compilation
2. **Python Base**: System dependencies
3. **Development**: Full development stack
4. **Production**: Optimized production build

#### Orchestration
- **Docker Compose**: Local development environment
- **Production**: Container orchestration platform
- **Health Checks**: Comprehensive health monitoring
- **Auto-scaling**: Horizontal scaling support

### Environment Management

#### Configuration Strategy
- **Environment Variables**: Comprehensive configuration management
- **Settings Modules**: Environment-specific Django settings
- **Secret Management**: Secure secret storage
- **Feature Flags**: Runtime feature toggling

#### Deployment Pipeline
- **Development**: Local development environment
- **Staging**: Pre-production testing environment
- **Production**: Live production environment
- **Monitoring**: Continuous monitoring and alerting

---

## Monitoring & Observability

### Application Monitoring

#### Performance Metrics
- **Response Times**: API and page response time tracking
- **Error Rates**: Comprehensive error tracking
- **User Activity**: User interaction analytics
- **System Health**: Application health monitoring

#### Logging Strategy
- **Structured Logging**: JSON-based structured logging
- **Log Levels**: Comprehensive log level management
- **Log Aggregation**: Centralized log collection
- **Alerting**: Automated alert system

### Business Intelligence

#### Usage Analytics
- **User Engagement**: User interaction tracking
- **Feature Usage**: Feature adoption monitoring
- **Performance Metrics**: Business KPI tracking
- **Reporting**: Automated report generation

---

## Future Architecture (BMMS Roadmap)

### BMMS Implementation Phases

#### Phase 1: Foundation (CRITICAL)
- Organizations app implementation
- Multi-tenant infrastructure
- Organization context middleware

#### Phase 2: Planning Module (HIGH)
- Strategic planning enhancement
- Cross-MOA planning capabilities

#### Phase 3: Budgeting Module (CRITICAL)
- Parliament Bill No. 325 implementation
- Cross-MOA budget management

#### Phase 4-8: Progressive Rollout
- Coordination enhancement
- Module migration
- Pilot MOA onboarding (3 MOAs)
- Full rollout (44 MOAs)

### Scalability Considerations

#### Horizontal Scaling
- **Database Scaling**: Read replicas and sharding
- **Application Scaling**: Load balancing support
- **Cache Scaling**: Distributed caching
- **Task Scaling**: Celery cluster scaling

#### Microservices Migration Path
- **Modular Design**: Service-oriented architecture ready
- **API Gateway**: Centralized API management
- **Service Discovery**: Dynamic service registration
- **Inter-Service Communication**: Service mesh implementation

---

## Conclusion

The OBCMS/BMMS system represents a sophisticated, enterprise-grade Django application with advanced features for community development, stakeholder coordination, and governmental operations. The architecture demonstrates:

1. **Scalability**: Multi-tenant, microservices-ready design
2. **Security**: Comprehensive security with audit trails
3. **Integration**: Rich API ecosystem with external systems
4. **Compliance**: Legal and regulatory compliance features
5. **User Experience**: Intuitive interface with advanced capabilities

The system is well-positioned for the BMMS transition, with a clear architectural path from single-tenant (OBCMS) to multi-tenant (BMMS) operations serving all 44 BARMM Ministries, Offices, and Agencies.

---

## Documentation References

- [Development Guide](../development/README.md)
- [Deployment Guide](../deployment/)
- [UI Standards](../ui/OBCMS_UI_STANDARDS_MASTER.md)
- [BMMS Planning](../plans/bmms/README.md)
- [Testing Documentation](../testing/)

---

*This document is maintained as part of the OBCMS/BMMS project documentation. For the most current version, please refer to the project repository.*