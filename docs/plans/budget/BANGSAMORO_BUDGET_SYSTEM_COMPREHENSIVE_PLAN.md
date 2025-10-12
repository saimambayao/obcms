# Bangsamoro Budget System Implementation Plan for OBCMS
## Comprehensive Development Plan for Planning and Budgeting Module

**Document Version:** 1.0  
**Date:** October 12, 2025  
**Status:** Draft for Review  
**Classification:** Internal Use Only

---

## Executive Summary

This comprehensive plan outlines the development and implementation of the Bangsamoro Budget System within the OBCMS platform, fully compliant with Parliament Bill No. 925 (Bangsamoro Budget System Act). The system will digitalize the entire budget cycle from preparation through execution, monitoring, and accountability, serving the Bangsamoro Government's fiscal responsibility principles and transparency requirements.

The implementation integrates with OBCMS's existing WorkItem hierarchy, project management capabilities, and AI-assisted decision support to create a unified platform for budget planning, authorization, execution, and oversight.

**Key Implementation Metrics:**
- **Timeline:** 18-month phased rollout
- **Budget Cycle Coverage:** Complete fiscal year cycle (January 1 - December 31)
- **User Base:** 500+ budget officers, reviewers, and approvers across ministries
- **Integration Points:** 8 major OBCMS modules
- **Compliance Framework:** Full alignment with Bangsamoro Budget System Act

---

## Table of Contents

### Part I: Foundation and Framework
1. [Legal and Regulatory Foundation](#1-legal-and-regulatory-foundation)
2. [System Architecture and Technical Specifications](#2-system-architecture-and-technical-specifications)
3. [Integration with OBCMS Ecosystem](#3-integration-with-obcms-ecosystem)

### Part II: Budget Cycle Implementation
4. [Budget Preparation Module](#4-budget-preparation-module)
5. [Budget Authorization and Approval](#5-budget-authorization-and-approval)
6. [Budget Execution and Controls](#6-budget-execution-and-controls)
7. [Financial Management and Treasury](#7-financial-management-and-treasury)

### Part III: Accountability and Oversight
8. [Accountability and Reporting Framework](#8-accountability-and-reporting-framework)
9. [Transparency and Public Participation](#9-transparency-and-public-participation)
10. [Monitoring and Performance Evaluation](#10-monitoring-and-performance-evaluation)

### Part IV: Implementation and Operations
11. [Implementation Roadmap and Phases](#11-implementation-roadmap-and-phases)
12. [Data Models and Database Schema](#12-data-models-and-database-schema)
13. [User Roles, Permissions, and Workflows](#13-user-roles-permissions-and-workflows)
14. [AI-Assisted Budget Intelligence](#14-ai-assisted-budget-intelligence)
15. [Security, Audit, and Compliance](#15-security-audit-and-compliance)

### Part V: Operations and Maintenance
16. [Training and Capacity Development](#16-training-and-capacity-development)
17. [Testing and Quality Assurance Strategy](#17-testing-and-quality-assurance-strategy)
18. [Risk Management and Contingency Planning](#18-risk-management-and-contingency-planning)
19. [Maintenance and Continuous Improvement](#19-maintenance-and-continuous-improvement)

### Appendices
- [Appendix A: Legislative Provisions Matrix](#appendix-a-legislative-provisions-matrix)
- [Appendix B: Budget Forms and Templates](#appendix-b-budget-forms-and-templates)
- [Appendix C: API Specifications](#appendix-c-api-specifications)
- [Appendix D: Glossary of Terms](#appendix-d-glossary-of-terms)

---

## Part I: Foundation and Framework

### 1. Legal and Regulatory Foundation

#### 1.1 Primary Legislative Framework

The Bangsamoro Budget System implementation is governed by **Parliament Bill No. 925** titled "An Act Prescribing a Budget System for the Bangsamoro Government," which establishes comprehensive requirements for budget preparation, authorization, execution, and accountability.

**Key Legislative Provisions:**

**Section 2. Declaration of Policy** establishes that **"The Bangsamoro Government hereby declares that the principles of accountability, integrity, and moral governance shall be realized and maintained in the use of public funds and resources by ensuring transparency, fiscal responsibility, results-orientation, efficiency, and effectiveness in line with the aims of meaningful fiscal autonomy towards the attainment of economic self-sufficiency and genuine development in the Bangsamoro Autonomous Region."**

This policy declaration drives the following implementation requirements:

1. **Transparency Requirements** (Section 2.c)
   - Public involvement in resource management
   - Facilitated access to financial affairs information
   - Open disclosure policy mandated by BOL

2. **Integration and Coordination** (Section 2.d)
   - Unified planning, programming, and budgeting systems
   - Coordinated disbursement and reporting mechanisms
   - Performance monitoring and review integration
   - Alignment with National Government and LGU relationships

3. **Internal Controls** (Section 2.e)
   - Safeguards in managing public finances
   - Risk management frameworks
   - Internal control systems

#### 1.2 Fiscal Responsibility Principles

**Section 5. Fiscal Responsibility Principles** requires the Bangsamoro Government to pursue policy objectives in accordance with:

1. **Sound Economic and Fiscal Policies** (Section 5.a)
   - Geared toward political, economic, and social objectives
   - Strategic alignment with development goals

2. **Sustainable Resource Management** (Section 5.b)
   - Fiscally sustainable resource utilization
   - Long-term financial viability

3. **Debt Management** (Section 5.c)
   - Sustainable level of public debt maintenance
   - Appropriate balance between revenue and expenditure
   - Alignment with macroeconomic targets

4. **Prudent Fiscal Risk Management** (Section 5.d)
   - Proactive risk assessment and mitigation

#### 1.3 Budget Coordinating Committee

**Section 6. Bangsamoro Budget Coordinating Committee** created by Executive Order No. 0003, series of 2023, has the following functions and responsibilities:

1. **Macroeconomic Coordination** (Section 6.a)
   - Review and approve macroeconomic targets
   - Revenue projections and aggregate budget level recommendations
   - Expenditure priorities determination
   - Consolidated public sector financial position assessment
   - Fiscal program development for the Bangsamoro Government

2. **Annual Program Recommendations** (Section 6.b)
   - Level of annual expenditure program determination
   - Regional spending ceiling establishment
   - Consideration of sustainable development goals
   - Macroeconomic assumptions integration
   - Projected revenue collections assessment
   - Borrowing measures implementation
   - Overall economic policies alignment

3. **Revenue and Borrowing Measures** (Section 6.c)
   - Revenue measure recommendations to Chief Minister
   - Borrowing implementation based on revenue projections
   - Fiscal needs assessment for the Bangsamoro Autonomous Region

4. **Performance Reviews** (Section 6.d)
   - Periodic reviews of costs, accomplishments, and performance standards
   - Development project examination

5. **Fiscal Policy and Strategy** (Section 6.e)
   - Bangsamoro Statement of Fiscal Policy preparation
   - Medium-term Fiscal Strategy development
   - Regular updates with Chief Minister approval

6. **Annual Fiscal Reporting** (Section 6.f)
   - Annual Fiscal Report on macroeconomic and fiscal performance
   - Coverage of preceding fiscal year
   - Comparative analysis against forecasts and objectives

#### 1.4 Statement of Fiscal Policy and Medium-Term Fiscal Strategy

**Section 7. Statement of Fiscal Policy** requires:
- Measurable medium-term macroeconomic and fiscal objectives
- Forecasts consistent with Fiscal Responsibility Principles
- Submission to Parliament within ninety (90) days from commencement of term of office

**Section 8. Medium-Term Fiscal Strategy** mandates:
- Consistency with approved measurable fiscal objectives in the Bangsamoro Statement of Fiscal Policy
- MFBM specification of contents requirements
- Submission by Chief Minister to Parliament not later than March 15th of current year
- Publication on official website within seven (7) days after Parliament submission
- First Medium-Term Fiscal Strategy required after conclusion of first election and organization of new Government

#### 1.5 Fiscal Reporting Requirements

**Section 9. Fiscal Report** establishes:
- Annual Fiscal Report preparation by BBCC
- Information on macroeconomic and fiscal outturns for period covered
- Comparison against forecasts and objectives stated in Medium-Term Fiscal Strategy
- Submission to Parliament not later than thirty (30) days from Fourth Monday of July
- Publication on official website within seven (7) days after Parliament submission
- First Annual Fiscal Report required after conclusion of first elections

#### 1.6 Deviations from Fiscal Objectives

**Section 10. Deviations from Fiscal Objectives** allows temporary deviations from medium-term fiscal objectives in approved Bangsamoro Statement of Fiscal Policy where deviation is due to:
- Major natural disaster
- Unanticipated severe economic shock
- Other significant unforeseeable events

Deviations may be accommodated through:
- Accessing the Contingent Fund
- Prudent fiscal policy adjustments
- Use of other flexibilities authorized in the Act

**Requirements:** Reasons for deviations and measures to address such deviations shall be disclosed in the Annual Fiscal Report.

#### 1.7 Shared Fiscal Discipline

**Section 11. Shared Fiscal Discipline** establishes accountability frameworks:

**Parliament Responsibilities** (Section 11.a):
All proposed expenditure bills shall, upon filing, include a Financial and Budgetary Information Sheet containing:
- Estimate of financial and budgetary implications for initial year of implementation
- Projections for next five (5) years
- MFBM guidelines prescribing form, content, appropriate offices, and implications

**Spending Agencies Responsibilities** (Section 11.b):
Heads of Bangsamoro M/O/As, BGOCCs, and Constituent LGUs (to extent provided in Section 3) shall be responsible for:
1. Promptly informing MFBM of significant changes, issues, and risks impacting Bangsamoro Government finances
2. Participating in processes to develop Medium-Term Fiscal Strategy, Budget Priorities Framework, and Proposed Bangsamoro Budget
3. Managing respective M/O/As, including BGOCCs and resources, in efficient, effective, and economical manner to deliver outputs and attain outcomes
4. Monitoring physical and financial implementation of programs, activities, and projects
5. Implementing measures to ensure contractual commitments do not exceed appropriated amounts
6. Ensuring respective M/O/As settle contractual obligations or approve payments within time prescribed by law
7. Instituting effective and efficient management systems, procedures, and practices for assets, liabilities, and personnel, including internal controls, risk management, and performance review
8. Ensuring respective M/O/As take due regard of recommendations provided in internal and external audit evaluation reports
9. Providing accounting and reporting of public finances as required
10. Providing credible and realistic cash forecasts for timely and accurate cash programming
11. Ensuring proper accounting and reporting through integrated budget monitoring and information system or online information system
12. Fulfilling any other responsibilities or duties as prescribed or deemed necessary

#### 1.8 Capacity Development Requirements

**Section 12. Capacity Development Requirements on Public Financial Management** mandates:
- All M/O/As shall formulate capacity development requirements on public financial management (PFM)
- Conduct relevant training programs
- MFBM oversight of formulation to ensure alignment with objectives
- MFBM coordination with CSC for BARMM and Development Academy of the Bangsamoro
- Formulation of competency-based human resource policies for PFM positions
- MFBM oversight of capacity development requirements on PFM

---

### 2. System Architecture and Technical Specifications

#### 2.1 Technology Stack

The Bangsamoro Budget System leverages OBCMS's existing technology foundation:

**Backend Framework:**
- **Django 5.2+**: Core web framework
- **Django REST Framework**: API layer for external integrations
- **Celery**: Background task processing for budget calculations, report generation, and scheduled tasks
- **Redis**: Message broker and caching layer

**Database:**
- **Primary**: PostgreSQL 14+ for production (via DATABASE_URL)
- **Development**: SQLite for local development
- **Features**: JSONB fields for flexible budget metadata, full-text search capabilities, transaction-level ACID compliance

**Frontend Technologies:**
- **Django Templates**: Server-side rendering
- **Tailwind CSS**: Utility-first styling framework
- **Alpine.js**: Lightweight JavaScript framework for interactivity
- **HTMX**: Instant UI updates and progressive enhancement
- **Chart.js**: Budget visualization and analytics

**AI and Intelligence:**
- **Gemini API Integration**: Natural language query processing
- **Vector Embeddings**: Document search and semantic matching
- **Query Templates**: 300+ curated templates for budget intelligence queries

**Authentication and Security:**
- **Django Authentication**: User management and sessions
- **JWT Tokens**: API authentication
- **Role-Based Access Control (RBAC)**: Granular permission system
- **Audit Logging**: Complete action tracking via django-auditlog

**Storage:**
- **Local Filesystem**: Development and small deployments
- **S3-Compatible Storage**: Production media and document storage
- **Document Versioning**: Git-like version control for budget documents

#### 2.2 System Architecture Layers

**Layer 1: Presentation Layer**
```
┌─────────────────────────────────────────────────────────────┐
│                    Web Browser Interface                     │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │  Budget      │  Approval    │  Monitoring Dashboard    │ │
│  │  Preparation │  Workflows   │  & Reports               │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
│             │ HTMX + Alpine.js + Chart.js                    │
└─────────────┼──────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │  Django      │  Budget      │  Workflow Engine         │ │
│  │  Views       │  Services    │  & State Machine         │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │  API         │  AI Query    │  Celery Task Queue       │ │
│  │  Endpoints   │  Processing  │  (Reports, Calculations) │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└─────────────┼──────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Domain Layer                              │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │  Budget      │  M/O/A       │  Financial Accountability│ │
│  │  Models      │  Management  │  & Controls              │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │  GAAB/BESF   │  Allotment   │  BED (Budget Execution   │ │
│  │  Models      │  & Release   │  Documents)              │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└─────────────┼──────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │  PostgreSQL  │  Redis       │  S3 Storage              │ │
│  │  Database    │  Cache       │  (Documents, Reports)    │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

#### 2.3 Core Django Applications Structure

The Budget System will be implemented across multiple Django applications within the OBCMS ecosystem:

**New Budget Applications:**
```
src/
├── budget_system/           # Core budget system coordination
│   ├── models/
│   │   ├── fiscal_policy.py        # Statement of Fiscal Policy, MTFS
│   │   ├── budget_call.py          # Annual Budget Call management
│   │   ├── budget_priorities.py    # Budget Priorities Framework
│   │   └── bbcc.py                 # Budget Coordinating Committee
│   ├── services/
│   │   ├── fiscal_strategy.py      # Fiscal policy calculations
│   │   ├── macroeconomic.py        # Revenue projections, targets
│   │   └── budget_ceiling.py       # Expenditure ceiling calculations
│   └── views/
│       ├── fiscal_policy.py        # BBCC dashboard, fiscal reports
│       ├── budget_call.py          # Budget Call management UI
│       └── priorities.py           # Priorities Framework UI
│
├── budget_preparation/      # Budget preparation and proposal
│   ├── models/
│   │   ├── proposed_budget.py      # Proposed Bangsamoro Budget
│   │   ├── moa_budget.py           # M/O/A budget proposals
│   │   ├── program_budget.py       # Program and project budgets
│   │   ├── besf.py                 # Budget of Expenditure & Sources of Financing
│   │   └── bed.py                  # Budget Execution Documents
│   ├── services/
│   │   ├── budget_builder.py       # Budget preparation services
│   │   ├── validation.py           # Budget validation rules
│   │   ├── endorsement.py          # Budget endorsing authorities
│   │   └── calculation.py          # Budget calculations engine
│   └── views/
│       ├── preparation.py          # Budget preparation UI
│       ├── endorsement.py          # Endorsement workflow UI
│       └── besf.py                 # BESF preparation UI
│
├── budget_authorization/    # Parliament approval and GAAB
│   ├── models/
│   │   ├── gaab.py                 # General Appropriations Act of Bangsamoro
│   │   ├── parliament_bill.py      # Parliament consideration process
│   │   ├── committee_report.py     # Committee review and reports
│   │   └── amendments.py           # Budget amendments during approval
│   ├── services/
│   │   ├── parliament_workflow.py  # Parliament approval process
│   │   ├── reading_schedule.py     # First, second, third readings
│   │   └── gaab_publication.py     # GAAB publication services
│   └── views/
│       ├── parliament.py           # Parliament consideration UI
│       ├── committee.py            # Committee review UI
│       └── gaab.py                 # GAAB management UI
│
├── budget_execution/        # Allotment, obligation, disbursement
│   ├── models/
│   │   ├── gaabao.py               # GAAB as Allotment Order
│   │   ├── saro.py                 # Special Allotment Release Order
│   │   ├── allotment.py            # Allotment tracking
│   │   ├── obligation.py           # Obligational Authority
│   │   ├── disbursement.py         # Disbursement Authority (NCA, NCAA, NTA)
│   │   ├── myca.py                 # Multi-Year Contracting Authority
│   │   └── savings.py              # Savings declarations and augmentation
│   ├── services/
│   │   ├── allotment_release.py    # Allotment issuance logic
│   │   ├── obligation_tracking.py  # Obligation monitoring
│   │   ├── disbursement.py         # Disbursement processing
│   │   ├── cash_budgeting.py       # Cash budgeting system
│   │   └── virement.py             # Budget modification rules
│   └── views/
│       ├── allotment.py            # Allotment management UI
│       ├── obligation.py           # Obligation tracking UI
│       ├── disbursement.py         # Disbursement UI
│       └── cash_programming.py     # Cash budgeting UI
│
├── financial_management/    # Treasury, STA, investments
│   ├── models/
│   │   ├── treasury.py             # Bangsamoro Treasury Office
│   │   ├── sta.py                  # Single Treasury Account
│   │   ├── general_fund.py         # General Fund management
│   │   ├── special_funds.py        # Special Purpose Funds
│   │   ├── revolving_fund.py       # Revolving Fund
│   │   └── investments.py          # Investment management
│   ├── services/
│   │   ├── cash_management.py      # Treasury cash management
│   │   ├── sta_operations.py       # STA operations
│   │   ├── investment_strategy.py  # Investment services
│   │   └── fund_allocation.py      # Fund management services
│   └── views/
│       ├── treasury_dashboard.py   # Treasury operations UI
│       ├── sta.py                  # STA management UI
│       └── investments.py          # Investment tracking UI
│
├── financial_accountability/ # Reporting, audit, performance
│   ├── models/
│   │   ├── bfar.py                 # Budget & Financial Accountability Reports
│   │   ├── annual_report.py        # Annual reports to Parliament
│   │   ├── fiscal_report.py        # Annual Fiscal Report
│   │   ├── audit_finding.py        # COA audit findings
│   │   └── performance_indicator.py # Performance indicators
│   ├── services/
│   │   ├── reporting.py            # Reporting generation services
│   │   ├── consolidation.py        # Financial consolidation
│   │   ├── performance_eval.py     # Performance evaluation
│   │   └── audit_integration.py    # COA integration services
│   └── views/
│       ├── bfar.py                 # BFAR submission and monitoring
│       ├── reports.py              # Report generation UI
│       ├── parliament_reports.py   # Parliament reporting UI
│       └── performance.py          # Performance monitoring UI
│
└── budget_transparency/     # Public access and participation
    ├── models/
    │   ├── transparency_seal.py    # Transparency seal management
    │   ├── peoples_budget.py       # Citizen-friendly budget summaries
    │   ├── public_consultation.py  # Public participation records
    │   └── disclosure.py           # Public disclosure requirements
    ├── services/
    │   ├── publication.py          # Budget publication services
    │   ├── citizen_budget.py       # Citizen budget generation
    │   └── participation.py        # Public participation mechanisms
    └── views/
        ├── public_portal.py        # Public-facing budget portal
        ├── transparency.py         # Transparency seal UI
        └── participation.py        # Public participation UI
```

**Integration with Existing OBCMS Applications:**
```
src/
├── project_central/         # EXISTING - Enhanced for budget integration
│   ├── models/
│   │   └── budget_linkage.py       # Links WorkItems to budget items
│   └── services/
│       └── budget_tracking.py      # Budget utilization tracking
│
├── monitoring/              # EXISTING - Enhanced for budget performance
│   ├── services/
│   │   └── budget_performance.py   # Budget vs. actual monitoring
│   └── views/
│       └── budget_analytics.py     # Budget performance dashboards
│
└── ai_assistant/            # EXISTING - Enhanced with budget queries
    └── query_templates/
        └── budget/                 # Budget-specific query templates
            ├── appropriations.py   # Appropriation queries
            ├── execution.py        # Execution status queries
            ├── performance.py      # Performance analysis queries
            └── compliance.py       # Compliance checking queries
```

#### 2.4 Database Schema Overview

**Core Budget Tables:**
```sql
-- Fiscal Policy and Strategy
fiscal_policy_statement
medium_term_fiscal_strategy
annual_fiscal_report
bbcc_meeting
bbcc_decision

-- Budget Preparation
budget_call
budget_priorities_framework
proposed_bangsamoro_budget
moa_budget_proposal
program_budget
project_budget
besf (Budget of Expenditure and Sources of Financing)

-- Budget Authorization
parliament_bill
committee_review
parliament_reading
gaab (General Appropriations Act of Bangsamoro)
gaab_item
supplemental_appropriation

-- Budget Execution
gaabao (GAAB as Allotment Order)
saro (Special Allotment Release Order)
allotment
allotment_class (PS, MOOE, FE, CO)
obligation
obligational_authority
disbursement_authority (NCA, NCAA, NTA)
multi_year_contracting_authority
savings_declaration
augmentation

-- Financial Management
single_treasury_account
general_fund
special_purpose_fund
  - contingent_fund
  - special_development_fund
  - lgu_statutory_shares
  - local_government_support_fund
revolving_fund
investment

-- Accountability and Reporting
budget_financial_accountability_report
annual_accomplishment_report
fiscal_report_to_parliament
performance_indicator
audit_finding

-- Transparency and Public Participation
transparency_seal
peoples_budget_summary
public_consultation_record
budget_disclosure

-- Integration with WorkItems
budget_workitem_link
workitem_budget_allocation
workitem_budget_utilization
```

**Key Relationships:**
```
GAAB (1) ─── (M) GAAB_ITEM
GAAB_ITEM (1) ─── (M) ALLOTMENT
ALLOTMENT (1) ─── (M) OBLIGATION
OBLIGATION (1) ─── (M) DISBURSEMENT
MOA_BUDGET_PROPOSAL (1) ─── (M) PROGRAM_BUDGET
PROGRAM_BUDGET (1) ─── (M) PROJECT_BUDGET
PROJECT_BUDGET (1) ─── (1) WORKITEM (from project_central)
```

#### 2.5 Performance and Scalability Requirements

**Response Time Targets:**
- Budget dashboard loading: < 2 seconds
- Budget proposal submission: < 3 seconds
- Report generation (standard): < 10 seconds
- Report generation (complex annual): < 60 seconds
- AI query response: < 5 seconds
- Budget validation: < 5 seconds

**Scalability Targets:**
- Support 500+ concurrent users during budget season
- Handle 50+ M/O/As submitting budgets simultaneously
- Process 10,000+ budget line items per fiscal year
- Store 10+ years of historical budget data
- Generate reports for all M/O/As within 1 hour

**Data Volumes (Annual):**
- Budget line items: ~10,000 per fiscal year
- Transactions (allotments, obligations, disbursements): ~50,000 per year
- Documents and attachments: ~5,000 files, ~50 GB
- Audit log entries: ~500,000 records per year

---

### 3. Integration with OBCMS Ecosystem

#### 3.1 WorkItem Integration

The Budget System deeply integrates with OBCMS's unified WorkItem hierarchy to enable seamless tracking from budget appropriation through project execution.

**WorkItem Hierarchy and Budget Links:**
```
Initiative (Strategic Level)
    └─ Project (Implementation Level)
        └─ Activity (Operational Level)
            └─ Task (Execution Level)

Each level can have:
- Budget Allocation (from GAAB appropriation)
- Budget Utilization (actual spending)
- Funding Source (General Fund, Special Fund, etc.)
- Budget Status (allocated, obligated, disbursed)
```

**Budget-WorkItem Integration Model:**
```python
class BudgetWorkItemLink(models.Model):
    """Links budget appropriations to WorkItems"""
    
    # Budget side
    gaab_item = models.ForeignKey('GAABItem', on_delete=models.CASCADE)
    allotment = models.ForeignKey('Allotment', on_delete=models.SET_NULL, null=True)
    
    # WorkItem side
    workitem = models.ForeignKey('WorkItem', on_delete=models.CASCADE)
    
    # Financial tracking
    allocated_amount = models.DecimalField(max_digits=15, decimal_places=2)
    obligated_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    disbursed_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Metadata
    fiscal_year = models.IntegerField()
    allotment_class = models.CharField(max_length=10)  # PS, MOOE, FE, CO
    date_linked = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('gaab_item', 'workitem', 'fiscal_year')
```

**Integration Features:**
1. **Automatic Budget Tracking**: As WorkItems progress, automatically track budget utilization
2. **Budget Alerts**: Notify project managers when budget thresholds are reached
3. **Real-time Dashboards**: Show budget status on WorkItem cards and detail views
4. **Budget Variance Analysis**: Compare planned vs. actual spending at WorkItem level

#### 3.2 Project Central Integration

**Enhanced Project Central Features:**
- **Budget tab** on project detail pages showing:
  - Allocated budget by allotment class
  - Obligated amounts and outstanding commitments
  - Disbursed amounts and payment status
  - Budget utilization percentage
  - Variance analysis (planned vs. actual)

- **Budget planning tools** in project creation:
  - Budget estimate templates by project type
  - Historical cost data reference
  - Multi-year budget planning for long-term projects

- **Budget approval workflows**:
  - Integration with project approval requiring budget confirmation
  - Automatic check of budget availability before project approval
  - Budget endorsement routing to MFBM

#### 3.3 Monitoring and Evaluation Integration

**Budget Performance Monitoring:**
- **Financial Performance Indicators**:
  - Budget absorption rate
  - Obligation rate
  - Disbursement rate
  - Spending efficiency ratio
  - Budget variance (planned vs. actual)

- **Integration with M&E Dashboards**:
  - Budget vs. physical accomplishment analysis
  - Cost-effectiveness metrics
  - Return on investment calculations
  - Budget performance by M/O/A, program, and project

**Automated Performance Reporting:**
- Quarterly budget performance reports
- Budget and Financial Accountability Reports (BFARs)
- Budget utilization heatmaps
- Spending trend analysis

#### 3.4 Communities Module Integration

**Budget Allocation by Geographic Area:**
- Track budget allocations to OBC communities
- Monitor spending by province, city, municipality
- Analyze per capita spending by community
- Geographic budget visualization on maps

**Community Needs Assessment Budget Linkage:**
- Link MANA (Mapping and Needs Assessment) findings to budget priorities
- Track budget allocation vs. community needs
- Monitor implementation of community-prioritized projects

#### 3.5 Coordination Module Integration

**Stakeholder Budget Coordination:**
- Track MOA implementation budgets
- Monitor partner agency funding commitments
- Coordinate joint programming and budgeting
- Manage PPP (Public-Private Partnership) budget tracking

**Inter-Agency Budget Coordination:**
- Share budget information with partner agencies
- Coordinate convergence programs
- Track multi-agency funded projects
- Monitor counterpart funding

#### 3.6 AI Assistant Integration

**Budget Intelligence Queries:**
The AI Assistant will be enhanced with 100+ budget-specific query templates:

**Budget Appropriation Queries:**
- "What is the total approved budget for education sector in FY 2026?"
- "Show me the budget breakdown by M/O/A for current fiscal year"
- "Which programs have the highest budget allocation?"
- "Compare budget allocations across the last 3 fiscal years"

**Budget Execution Queries:**
- "What is the current budget utilization rate for MFBM?"
- "Show me projects with low budget absorption"
- "Which M/O/As have unutilized allotments?"
- "What is the disbursement status for infrastructure projects?"

**Budget Performance Queries:**
- "Compare planned vs. actual spending for Q3"
- "Which programs are over budget?"
- "Show me budget variance analysis by sector"
- "What is the average budget absorption rate across all M/O/As?"

**Budget Compliance Queries:**
- "Are there any savings that can be declared?"
- "Check for appropriations exceeding approved amounts"
- "Show me pending budget augmentation requests"
- "Which M/O/As have not submitted their BFARs?"

**Natural Language Budget Reports:**
Users can request reports in natural language:
- "Generate a budget utilization report for the last quarter"
- "Create a comparison of education spending vs. last year"
- "Prepare a budget performance summary for the Cabinet meeting"

---

## Part II: Budget Cycle Implementation

### 4. Budget Preparation Module

#### 4.1 Budget Philosophies Implementation

**Section 13. Budget Philosophies** establishes four governing principles to be implemented in the system:

**4.1.1 Programmatic Philosophy**
```python
class ProgramBudget(models.Model):
    """
    Implements programmatic budgeting philosophy:
    Plans and budgets shall be allocated based on carefully planned 
    P/A/Ps that are strategic, responsive, and implementation-ready.
    """
    
    program_name = models.CharField(max_length=255)
    strategic_objective = models.TextField()
    
    # Link to approved development plan
    bdp_linkage = models.ForeignKey('BangsamoroDevelopmentPlan', 
                                    on_delete=models.CASCADE)
    bdip_linkage = models.ForeignKey('BangsamoroDevelopmentInvestmentProgram',
                                     on_delete=models.CASCADE)
    
    # Implementation readiness assessment
    is_implementation_ready = models.BooleanField(default=False)
    readiness_score = models.IntegerField(validators=[MinValueValidator(0), 
                                                       MaxValueValidator(10)])
    
    # Strategic alignment
    aligns_with_strategy = models.BooleanField()
    strategic_alignment_notes = models.TextField()
    
    # Responsiveness to needs
    responds_to_needs = models.BooleanField()
    needs_assessment_reference = models.ForeignKey('NeedsAssessment',
                                                    on_delete=models.SET_NULL,
                                                    null=True)
```

**System Features for Programmatic Budgeting:**
- Mandatory linkage to approved BDP (Bangsamoro Development Plan)
- Mandatory linkage to BDIP (Bangsamoro Development Investment Program)
- Implementation readiness checklist before budget proposal submission
- Strategic alignment verification workflow
- Integration with MANA module for needs assessment validation

**4.1.2 Transparent Philosophy**
```python
class BudgetTransparencyLog(models.Model):
    """
    Implements transparency philosophy:
    Full disclosure of all financial and fiscal-related information 
    on how public resources are allocated and utilized promptly 
    and systematically.
    """
    
    disclosure_type = models.CharField(max_length=50, choices=[
        ('BUDGET_PROPOSAL', 'Budget Proposal'),
        ('ALLOTMENT', 'Allotment Release'),
        ('OBLIGATION', 'Obligation Incurrence'),
        ('DISBURSEMENT', 'Disbursement'),
        ('REPORT', 'Financial Report'),
    ])
    
    disclosure_date = models.DateTimeField(auto_now_add=True)
    public_disclosure_date = models.DateTimeField()  # Must be within 7 days
    
    document = models.FileField(upload_to='budget_disclosures/')
    transparency_seal_link = models.URLField()
    
    # Compliance tracking
    disclosed_on_time = models.BooleanField()
    disclosure_delay_days = models.IntegerField(default=0)
    
    class Meta:
        indexes = [
            models.Index(fields=['disclosure_type', 'disclosure_date']),
        ]
```

**System Features for Transparency:**
- Automatic publication to transparency seal section of official website
- Public-facing budget portal with citizen-friendly summaries
- Real-time disclosure tracking and compliance monitoring
- Automated alerts for disclosure deadlines
- Public comment and feedback mechanisms

**4.1.3 Performance-Based Philosophy**
```python
class PerformanceBudgetLink(models.Model):
    """
    Implements performance-based philosophy:
    The allocation of funds shall relate to the achievement of 
    planned results and shall be evaluated against pre-determined 
    performance indicators and standards.
    """
    
    budget_item = models.ForeignKey('GAABItem', on_delete=models.CASCADE)
    
    # Performance indicators
    performance_indicators = models.ManyToManyField('PerformanceIndicator')
    
    # Pre-determined targets
    target_output_quantity = models.DecimalField(max_digits=12, decimal_places=2)
    target_output_unit = models.CharField(max_length=50)
    target_quality_standard = models.TextField()
    target_completion_date = models.DateField()
    
    # Budget-performance linkage
    cost_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    efficiency_target = models.DecimalField(max_digits=5, decimal_places=2)  # percentage
    
    # Evaluation results
    actual_output_quantity = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    quality_rating = models.IntegerField(validators=[MinValueValidator(1), 
                                                      MaxValueValidator(5)], 
                                          null=True)
    variance_analysis = models.TextField(blank=True)
```

**System Features for Performance-Based Budgeting:**
- Mandatory performance indicators for all budget proposals
- Pre-determined performance standards and targets
- Budget allocation algorithms considering past performance
- Real-time performance vs. budget monitoring
- Automated variance analysis and alerting
- Performance evaluation integration with budget releases

**4.1.4 Phased Manner Philosophy**
```python
class BudgetPhase(models.Model):
    """
    Implements phased manner philosophy:
    Program design and budget allocations shall be sequenced based 
    on the maturity and readiness of P/A/Ps, with each phase having 
    a clear timeframe, objectives, deliverables, and performance 
    indicators to ensure effective and efficient implementation.
    """
    
    project_budget = models.ForeignKey('ProjectBudget', on_delete=models.CASCADE)
    
    # Phase identification
    phase_number = models.IntegerField()
    phase_name = models.CharField(max_length=100)
    
    # Timeframe
    start_date = models.DateField()
    end_date = models.DateField()
    duration_months = models.IntegerField()
    
    # Objectives and deliverables
    phase_objectives = models.TextField()
    deliverables = models.TextField()
    
    # Budget allocation
    budget_amount = models.DecimalField(max_digits=15, decimal_places=2)
    budget_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Performance indicators
    performance_indicators = models.ManyToManyField('PerformanceIndicator')
    
    # Maturity and readiness
    maturity_level = models.CharField(max_length=20, choices=[
        ('CONCEPT', 'Concept Stage'),
        ('DESIGN', 'Design Stage'),
        ('READY', 'Implementation Ready'),
        ('ONGOING', 'Implementation Ongoing'),
        ('COMPLETED', 'Completed'),
    ])
    
    readiness_checklist_complete = models.BooleanField(default=False)
    
    # Dependencies
    depends_on_phase = models.ForeignKey('self', on_delete=models.SET_NULL,
                                          null=True, blank=True)
    
    class Meta:
        unique_together = ('project_budget', 'phase_number')
        ordering = ['phase_number']
```

**System Features for Phased Implementation:**
- Multi-phase budget planning wizard
- Automatic budget sequencing based on phase dependencies
- Phase readiness assessment before fund release
- Milestone-based fund release automation
- Phase performance monitoring dashboards
- Automatic alerts for phase completion and next phase activation

#### 4.2 Governing Principles in Budget Preparation

**Section 14. Governing Principles in Budget Preparation** establishes four key principles:

**4.2.1 Overall Expenditure Program Inclusion**
```python
def validate_budget_inclusion(budget_proposal):
    """
    Validates Section 14(a): The overall expenditure program of the 
    Bangsamoro Government for a given fiscal year shall be included, 
    identifying those requiring approval by Parliament and those 
    authorized under existing laws/acts.
    """
    
    required_checks = {
        'has_expenditure_program': False,
        'parliament_approval_identified': False,
        'existing_law_authorization_identified': False,
        'complete_fiscal_year_coverage': False,
    }
    
    # Check expenditure program exists
    if budget_proposal.expenditure_program:
        required_checks['has_expenditure_program'] = True
    
    # Check Parliament approval requirements identified
    items_requiring_parliament = budget_proposal.items.filter(
        requires_parliament_approval=True
    )
    if items_requiring_parliament.exists():
        required_checks['parliament_approval_identified'] = True
    
    # Check existing law authorizations identified
    items_with_existing_authorization = budget_proposal.items.filter(
        authorized_by_existing_law__isnull=False
    )
    if items_with_existing_authorization.exists():
        required_checks['existing_law_authorization_identified'] = True
    
    # Check fiscal year coverage
    if budget_proposal.covers_full_fiscal_year():
        required_checks['complete_fiscal_year_coverage'] = True
    
    return all(required_checks.values()), required_checks
```

**4.2.2 Performance-Informed Budget**
```python
class PerformanceInformedBudget(models.Model):
    """
    Implements Section 14(b): Both the financial and non-financial 
    performance indicators and standards of M/O/As shall be presented 
    in the Proposed Bangsamoro Budget to ensure a performance-informed 
    budget.
    """
    
    moa_budget = models.ForeignKey('MOABudgetProposal', on_delete=models.CASCADE)
    
    # Financial indicators
    budget_utilization_rate_previous = models.DecimalField(max_digits=5, 
                                                            decimal_places=2)
    obligation_rate_previous = models.DecimalField(max_digits=5, decimal_places=2)
    disbursement_rate_previous = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Non-financial indicators
    output_delivery_rate = models.DecimalField(max_digits=5, decimal_places=2)
    quality_rating = models.IntegerField(validators=[MinValueValidator(1),
                                                      MaxValueValidator(5)])
    beneficiary_satisfaction_score = models.DecimalField(max_digits=4, 
                                                          decimal_places=2)
    
    # Performance standards
    meets_performance_standards = models.BooleanField()
    performance_gaps_identified = models.TextField()
    improvement_plan = models.TextField()
    
    # Historical performance
    three_year_performance_trend = models.JSONField(default=dict)
    
    def calculate_performance_score(self):
        """Calculate overall performance score for budget allocation"""
        weights = {
            'budget_utilization': 0.20,
            'output_delivery': 0.30,
            'quality_rating': 0.25,
            'beneficiary_satisfaction': 0.25,
        }
        
        score = (
            (self.budget_utilization_rate_previous * weights['budget_utilization']) +
            (self.output_delivery_rate * weights['output_delivery']) +
            ((self.quality_rating / 5 * 100) * weights['quality_rating']) +
            (self.beneficiary_satisfaction_score * weights['beneficiary_satisfaction'])
        )
        
        return round(score, 2)
```

**4.2.3 Geographic Disaggregation**
```python
class GeographicBudgetDisaggregation(models.Model):
    """
    Implements Section 14(c): Items of appropriations shall be reflected 
    by M/O/A or by other method of disaggregation as the MFBM may prescribe 
    and shall be presented for information purposes by geographical area.
    """
    
    budget_item = models.ForeignKey('GAABItem', on_delete=models.CASCADE)
    
    # Geographic hierarchy
    region = models.CharField(max_length=100, default='BARMM')
    province = models.ForeignKey('Province', on_delete=models.CASCADE, 
                                  null=True, blank=True)
    city = models.ForeignKey('City', on_delete=models.CASCADE, 
                             null=True, blank=True)
    municipality = models.ForeignKey('Municipality', on_delete=models.CASCADE,
                                      null=True, blank=True)
    barangay = models.ForeignKey('Barangay', on_delete=models.CASCADE,
                                  null=True, blank=True)
    
    # Budget allocation by area
    allocated_amount = models.DecimalField(max_digits=15, decimal_places=2)
    percentage_of_total = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Beneficiary information
    estimated_beneficiaries = models.IntegerField()
    per_capita_allocation = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Geographic metadata
    is_obc_community = models.BooleanField(default=False)
    obc_community = models.ForeignKey('OBCCommunity', on_delete=models.SET_NULL,
                                       null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['province', 'city', 'municipality']),
            models.Index(fields=['is_obc_community']),
        ]
```

**System Features for Geographic Disaggregation:**
- Interactive budget map visualization
- Province/city/municipality drill-down views
- Per capita budget allocation analysis
- OBC community budget tracking
- Geographic equity analysis
- Beneficiary-based budget planning

**4.2.4 Prohibition of Unfunded Appropriations**
```python
def validate_funded_appropriation(budget_proposal):
    """
    Implements Section 14(d): In addition to the requirement under 
    Section 11(a) of this Act, no new appropriations for any expenditure, 
    the amount of which is not covered by the estimated income from the 
    existing sources of revenue or available current surplus, including 
    transfers from the National Government, may be proposed unless 
    supported by a corresponding proposal for new revenue-raising measures 
    sufficient to cover the same.
    """
    
    # Calculate total proposed appropriations
    total_proposed = budget_proposal.total_appropriations()
    
    # Calculate available funding sources
    available_funding = {
        'estimated_revenue': budget_proposal.estimated_revenue,
        'current_surplus': budget_proposal.current_surplus,
        'national_transfers': budget_proposal.national_government_transfers,
        'proposed_new_revenue': budget_proposal.proposed_new_revenue_measures,
    }
    
    total_available = sum(available_funding.values())
    
    # Check if appropriations are fully funded
    is_funded = total_proposed <= total_available
    funding_gap = max(0, total_proposed - total_available)
    
    validation_result = {
        'is_funded': is_funded,
        'total_proposed': total_proposed,
        'total_available': total_available,
        'funding_gap': funding_gap,
        'requires_new_revenue_measures': funding_gap > 0,
    }
    
    if funding_gap > 0:
        validation_result['message'] = (
            f"Funding gap of {funding_gap:,.2f} detected. "
            f"New revenue-raising measures required to cover the gap."
        )
    
    return validation_result


class NewRevenueMeasure(models.Model):
    """
    Tracks proposed new revenue-raising measures to cover budget gaps
    """
    
    budget_proposal = models.ForeignKey('ProposedBangsamoroBudget',
                                        on_delete=models.CASCADE)
    
    measure_title = models.CharField(max_length=255)
    measure_description = models.TextField()
    
    # Revenue projection
    projected_revenue = models.DecimalField(max_digits=15, decimal_places=2)
    implementation_timeline = models.CharField(max_length=100)
    
    # Legal basis
    requires_new_legislation = models.BooleanField()
    proposed_legislation_reference = models.CharField(max_length=255, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('PROPOSED', 'Proposed'),
        ('UNDER_REVIEW', 'Under Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ])
```

#### 4.3 Planning-Programming-Budgeting Continuum

**Section 15. Planning-Programming-Budgeting Continuum** requires:
```python
class BudgetPlanningContinuum(models.Model):
    """
    Implements Section 15: Bangsamoro budget priorities shall be based 
    on the regional development strategies specified in the approved 
    Bangsamoro Development Plan (BDP), considering the level of capability 
    and performance of the implementing M/O/A.
    """
    
    # Link to planning documents
    bdp = models.ForeignKey('BangsamoroDevelopmentPlan', on_delete=models.CASCADE)
    bdip = models.ForeignKey('BangsamoroDevelopmentInvestmentProgram',
                             on_delete=models.CASCADE)
    
    # Regional development strategies
    regional_strategy = models.TextField()
    strategic_priority_area = models.CharField(max_length=255)
    
    # Link to budget
    budget_allocation = models.DecimalField(max_digits=15, decimal_places=2)
    fiscal_year = models.IntegerField()
    
    # Implementation capacity assessment
    implementing_moa = models.ForeignKey('MinistryOfficeAgency',
                                          on_delete=models.CASCADE)
    capability_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    performance_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Budget ceiling determination
    approved_ceiling = models.DecimalField(max_digits=15, decimal_places=2)
    ceiling_adjustment_factor = models.DecimalField(max_digits=4, 
                                                     decimal_places=2)
    
    class Meta:
        unique_together = ('bdp', 'fiscal_year', 'implementing_moa')
```

**System Features:**
- Automatic BDP/BDIP linkage validation
- Strategic alignment scoring
- Capability and performance assessment workflows
- Budget ceiling calculator based on performance
- Medium-term budget projection based on BDIP
- Priority program identification and tracking

#### 4.4 Budget Priorities Framework

**Section 16. Budget Priorities Framework** implementation:
```python
class BudgetPrioritiesFramework(models.Model):
    """
    Implements Section 16: The BBCC shall present to the Chief Minister 
    and the Cabinet, in April of each year, a Budget Priorities Framework 
    that shall guide the formulation of the budget for the following year.
    """
    
    fiscal_year = models.IntegerField(unique=True)
    presentation_date = models.DateField()  # Must be in April
    
    # From Medium-Term Fiscal Strategy
    mtfs_reference = models.ForeignKey('MediumTermFiscalStrategy',
                                        on_delete=models.CASCADE)
    fiscal_strategy_summary = models.TextField()
    budget_targets = models.JSONField()
    
    # Priority areas from BDP and BDIP
    priority_areas = models.JSONField()  # List of priority spending areas
    priority_programs = models.JSONField()  # List of priority programs
    
    # Allocation parameters
    estimated_fiscal_space = models.DecimalField(max_digits=15, decimal_places=2)
    planned_allocation = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Gender-responsive budgeting
    gender_responsive_allocation = models.DecimalField(max_digits=15, 
                                                        decimal_places=2)
    gender_allocation_percentage = models.DecimalField(max_digits=5, 
                                                        decimal_places=2)
    gender_development_plan_reference = models.TextField()
    
    # Sectoral priorities
    education_priority_percentage = models.DecimalField(max_digits=5, 
                                                         decimal_places=2)
    health_priority_percentage = models.DecimalField(max_digits=5, 
                                                      decimal_places=2)
    social_services_priority_percentage = models.DecimalField(max_digits=5,
                                                               decimal_places=2)
    
    # Cabinet approval
    approved_by_cabinet = models.BooleanField(default=False)
    cabinet_approval_date = models.DateField(null=True, blank=True)
    
    # MFBM requirements
    additional_mfbm_requirements = models.JSONField(default=dict)
    
    def validate_gender_allocation(self):
        """
        Validates Section 16 requirement: at least five percent (5%) 
        of the total budget appropriation of each M/O/A and BGOCC shall 
        be set aside for gender-responsive programs following a gender 
        and development plan.
        """
        minimum_required = self.planned_allocation * Decimal('0.05')
        return self.gender_responsive_allocation >= minimum_required
    
    class Meta:
        ordering = ['-fiscal_year']
```

**System Workflow:**
1. **March**: BBCC prepares Budget Priorities Framework
2. **April**: BBCC presents to Chief Minister and Cabinet
3. **Cabinet approval**: Framework approved with or without modifications
4. **MFBM processing**: Budget Call issued based on approved framework
5. **M/O/A compliance**: Budget proposals aligned with framework priorities

#### 4.5 Annual Budget Preparation Process

**Section 17. Annual Budget Preparation Process** implementation:
```python
class AnnualBudgetCall(models.Model):
    """
    Implements Section 17: The MFBM, through the Bangsamoro Budget Office, 
    shall determine the budget preparation process and calendar in the 
    annual Budget Call to be presented during the annual budget forum.
    """
    
    fiscal_year = models.IntegerField(unique=True)
    
    # Budget Call issuance
    issuance_date = models.DateField()
    issued_by = models.ForeignKey('User', on_delete=models.PROTECT,
                                   related_name='budget_calls_issued')
    
    # Budget forum
    budget_forum_date = models.DateField()
    budget_forum_attendance = models.ManyToManyField('User',
                                                      related_name='budget_forums_attended')
    
    # Process and calendar
    budget_calendar = models.JSONField()  # Detailed timeline
    submission_deadline = models.DateField()
    review_period_start = models.DateField()
    review_period_end = models.DateField()
    
    # Forms and templates
    budget_forms = models.ManyToManyField('BudgetForm')
    required_documents = models.JSONField()
    
    # Guidelines
    preparation_guidelines = models.TextField()
    technical_instructions = models.FileField(upload_to='budget_calls/')
    
    # Ceiling allocations
    overall_ceiling = models.DecimalField(max_digits=15, decimal_places=2)
    
    def get_moa_ceiling(self, moa):
        """Get budget ceiling for specific M/O/A"""
        try:
            return MOABudgetCeiling.objects.get(
                budget_call=self,
                moa=moa
            ).ceiling_amount
        except MOABudgetCeiling.DoesNotExist:
            return None


class MOABudgetCeiling(models.Model):
    """Budget ceiling allocation for each M/O/A"""
    
    budget_call = models.ForeignKey('AnnualBudgetCall', on_delete=models.CASCADE)
    moa = models.ForeignKey('MinistryOfficeAgency', on_delete=models.CASCADE)
    
    # Ceiling amounts
    ceiling_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # By allotment class
    ps_ceiling = models.DecimalField(max_digits=15, decimal_places=2)
    mooe_ceiling = models.DecimalField(max_digits=15, decimal_places=2)
    fe_ceiling = models.DecimalField(max_digits=15, decimal_places=2)
    co_ceiling = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Basis for ceiling
    previous_year_allocation = models.DecimalField(max_digits=15, decimal_places=2)
    performance_factor = models.DecimalField(max_digits=4, decimal_places=2)
    priority_adjustment = models.DecimalField(max_digits=4, decimal_places=2)
    
    class Meta:
        unique_together = ('budget_call', 'moa')
```

#### 4.6 Budget Proposal Preparation

**Section 18. Budget Proposal** implementation:
```python
class MOABudgetProposal(models.Model):
    """
    Implements Section 18: Heads of M/O/As, the Speaker of the Parliament, 
    and the Presiding Justice of the Shari'ah High Court, shall submit 
    their budget proposals to the MFBM following the processes, forms, 
    and calendar prescribed by the MFBM.
    """
    
    budget_call = models.ForeignKey('AnnualBudgetCall', on_delete=models.CASCADE)
    fiscal_year = models.IntegerField()
    
    # Submitting entity
    moa = models.ForeignKey('MinistryOfficeAgency', on_delete=models.CASCADE,
                            null=True, blank=True)
    parliament = models.BooleanField(default=False)  # Parliament budget
    shariah_high_court = models.BooleanField(default=False)  # Court budget
    
    # Submission information
    submitted_by = models.ForeignKey('User', on_delete=models.PROTECT,
                                      related_name='budget_proposals_submitted')
    submission_date = models.DateTimeField(auto_now_add=True)
    submission_status = models.CharField(max_length=20, choices=[
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('UNDER_REVIEW', 'Under Review'),
        ('RETURNED', 'Returned for Revision'),
        ('ENDORSED', 'Endorsed'),
        ('APPROVED', 'Approved'),
    ])
    
    # Required information per Section 18
    # (a) Organizational outcomes, performance indicators, programs, and projects
    organizational_outcomes = models.TextField()
    performance_indicators = models.ManyToManyField('PerformanceIndicator')
    programs = models.ManyToManyField('ProgramBudget')
    projects = models.ManyToManyField('ProjectBudget')
    
    # (b) Linkage of work and financial proposals to approved BDP and BDIP
    bdp_linkage = models.TextField()
    bdip_linkage = models.TextField()
    
    # (c) Estimated Current Operating Expenditures and Capital Outlays
    current_operating_expenditures = models.DecimalField(max_digits=15, 
                                                          decimal_places=2)
    capital_outlays = models.DecimalField(max_digits=15, decimal_places=2)
    comparative_previous_year = models.DecimalField(max_digits=15, 
                                                     decimal_places=2)
    comparative_current_year = models.DecimalField(max_digits=15, 
                                                    decimal_places=2)
    
    # (d) Major thrusts and priority programs
    major_thrusts = models.TextField()
    priority_programs_description = models.TextField()
    expected_results = models.TextField()
    work_description = models.TextField()
    cost_per_unit = models.JSONField()  # Dictionary of cost per unit by activity
    objects_of_expenditure = models.JSONField()  # Breakdown by object
    
    # (e) Organization charts and staffing patterns
    org_chart = models.FileField(upload_to='budget_proposals/org_charts/')
    staffing_pattern = models.FileField(upload_to='budget_proposals/staffing/')
    position_list = models.JSONField()
    proposed_salaries = models.JSONField()
    position_classification_proposal = models.TextField()
    salary_change_justification = models.TextField()
    
    # (f) Other information required by MFBM
    additional_information = models.JSONField(default=dict)
    
    # Total amounts
    total_proposed_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    class Meta:
        unique_together = ('budget_call', 'moa', 'fiscal_year')
        ordering = ['-fiscal_year', 'moa']
```

#### 4.7 Budget Endorsing Authorities

**Section 19. Budget Endorsing Authorities** implementation:
```python
class BudgetEndorsingAuthority(models.Model):
    """
    Implements Section 19: The Heads of M/O/As that the MFBM has authorized 
    or may authorize to assist in the review and endorsement of budget 
    proposals of M/O/As and BGOCCs shall, in addition to their respective 
    existing mandates and functions, perform specific responsibilities.
    """
    
    # Authority designation
    moa_head = models.ForeignKey('User', on_delete=models.CASCADE)
    authorized_by_mfbm = models.BooleanField(default=False)
    authorization_date = models.DateField()
    
    # Scope of authority
    can_review_moas = models.ManyToManyField('MinistryOfficeAgency',
                                              related_name='reviewing_authorities')
    can_review_bgoccs = models.ManyToManyField('BGOCC',
                                                 related_name='reviewing_authorities')
    
    # Functions per Section 19
    
    # (a) Review budget proposals of other M/O/As
    def review_budget_proposal(self, proposal):
        """
        Review budget proposals to ensure compliance with standards set 
        under relevant laws, acts, and rules and regulations administered 
        by the Budget Endorsing Authorities.
        """
        review = BudgetEndorsementReview(
            proposal=proposal,
            reviewed_by=self.moa_head,
            review_type='TECHNICAL_COMPLIANCE'
        )
        
        # Technical compliance checks
        review.check_legal_compliance()
        review.check_technical_standards()
        review.check_documentation_completeness()
        
        return review
    
    # (b) Endorse budget proposals
    def endorse_budget_proposal(self, proposal):
        """
        Endorse the budget proposals of M/O/As upon verification that 
        budget proposals conform to relevant technical standards.
        """
        if not proposal.passes_technical_review():
            raise ValueError("Proposal does not meet technical standards")
        
        endorsement = BudgetEndorsement(
            proposal=proposal,
            endorsed_by=self.moa_head,
            endorsement_date=timezone.now()
        )
        endorsement.save()
        
        proposal.submission_status = 'ENDORSED'
        proposal.save()
        
        return endorsement
    
    # (c) Other functions prescribed by MFBM
    additional_functions = models.JSONField(default=dict)


class BudgetEndorsementReview(models.Model):
    """Records of budget proposal reviews"""
    
    proposal = models.ForeignKey('MOABudgetProposal', on_delete=models.CASCADE)
    reviewed_by = models.ForeignKey('User', on_delete=models.PROTECT)
    review_date = models.DateTimeField(auto_now_add=True)
    
    review_type = models.CharField(max_length=50, choices=[
        ('TECHNICAL_COMPLIANCE', 'Technical Compliance'),
        ('FINANCIAL_ANALYSIS', 'Financial Analysis'),
        ('PERFORMANCE_ASSESSMENT', 'Performance Assessment'),
        ('STRATEGIC_ALIGNMENT', 'Strategic Alignment'),
    ])
    
    # Review findings
    complies_with_laws = models.BooleanField()
    meets_technical_standards = models.BooleanField()
    documentation_complete = models.BooleanField()
    
    findings = models.TextField()
    recommendations = models.TextField()
    
    # Decision
    recommendation_decision = models.CharField(max_length=20, choices=[
        ('ENDORSE', 'Recommend for Endorsement'),
        ('REVISE', 'Return for Revision'),
        ('REJECT', 'Reject'),
    ])


class BudgetEndorsement(models.Model):
    """Official endorsement records"""
    
    proposal = models.ForeignKey('MOABudgetProposal', on_delete=models.CASCADE)
    endorsed_by = models.ForeignKey('User', on_delete=models.PROTECT)
    endorsement_date = models.DateTimeField()
    
    endorsement_notes = models.TextField()
    conditional_endorsement = models.BooleanField(default=False)
    conditions = models.TextField(blank=True)
    
    # Digital signature
    digital_signature = models.TextField()  # Encrypted signature
    signature_verified = models.BooleanField(default=False)
```

#### 4.8 Budget Evaluation Criteria

**Section 20. Budget Evaluation** implementation:
```python
class BudgetEvaluationCriteria(models.Model):
    """
    Implements Section 20: The proposed P/A/Ps of M/O/As shall be reviewed 
    based on their respective merits, using the following criteria
    """
    
    proposal = models.ForeignKey('MOABudgetProposal', on_delete=models.CASCADE)
    evaluated_by = models.ForeignKey('User', on_delete=models.PROTECT)
    evaluation_date = models.DateTimeField(auto_now_add=True)
    
    # (a) Relationship with the approved priority agenda of the Chief Minister
    priority_alignment_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    priority_alignment_notes = models.TextField()
    aligns_with_priority_agenda = models.BooleanField()
    
    # (b) Past performance vis-a-vis target spending
    past_performance_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    previous_allotments_not_obligated = models.DecimalField(max_digits=15,
                                                             decimal_places=2)
    obligation_rate_previous_years = models.JSONField()  # Historical data
    performance_analysis = models.TextField()
    
    # (c) Implementation-readiness
    implementation_readiness_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    has_development_plan = models.BooleanField()
    has_master_plan = models.BooleanField()
    has_road_map = models.BooleanField()
    moa_capability_demonstrated = models.BooleanField()
    readiness_assessment = models.TextField()
    
    # (d) Program convergence
    program_convergence_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    contributes_to_other_programs = models.BooleanField()
    convergence_analysis = models.TextField()
    coordination_mechanisms = models.TextField()
    
    # (e) All sources of funds and authorized uses
    funding_sources_complete = models.BooleanField()
    funding_sources_disclosed = models.JSONField()  # List of sources
    authorized_uses_clear = models.BooleanField()
    funding_analysis = models.TextField()
    
    # (f) Other similar criteria determined by MFBM
    additional_criteria = models.JSONField(default=dict)
    additional_criteria_scores = models.JSONField(default=dict)
    
    # Overall evaluation
    overall_score = models.DecimalField(max_digits=5, decimal_places=2)
    evaluation_result = models.CharField(max_length=20, choices=[
        ('APPROVED', 'Approved'),
        ('APPROVED_WITH_CONDITIONS', 'Approved with Conditions'),
        ('FOR_REVISION', 'For Revision'),
        ('DISAPPROVED', 'Disapproved'),
    ])
    
    evaluation_summary = models.TextField()
    recommendations = models.TextField()
    
    def calculate_overall_score(self):
        """Calculate weighted overall score"""
        weights = {
            'priority_alignment': 0.25,
            'past_performance': 0.20,
            'implementation_readiness': 0.25,
            'program_convergence': 0.15,
            'funding_completeness': 0.15,
        }
        
        score = (
            (self.priority_alignment_score * weights['priority_alignment']) +
            (self.past_performance_score * weights['past_performance']) +
            (self.implementation_readiness_score * weights['implementation_readiness']) +
            (self.program_convergence_score * weights['program_convergence']) +
            ((10 if self.funding_sources_complete else 0) * weights['funding_completeness'])
        )
        
        self.overall_score = round(score, 2)
        return self.overall_score
```

---

### 5. Budget Authorization and Approval

#### 5.1 BGOCC Budgetary Needs

**Section 21. Budgetary Needs of Bangsamoro Government-Owned or Controlled Corporations** implementation:
```python
class BGOCCBudgetNeed(models.Model):
    """
    Implements Section 21: The operating budgets of BGOCCs shall be 
    subject to review and approval as part of the budget preparation 
    process consistent with the policy of the Bangsamoro Government 
    to actively exercise its ownership rights in BGOCCs and promote 
    growth by ensuring that operations are consistent with regional 
    development policies and programs.
    """
    
    bgocc = models.ForeignKey('BGOCC', on_delete=models.CASCADE)
    fiscal_year = models.IntegerField()
    
    # Operating budget
    operating_budget = models.DecimalField(max_digits=15, decimal_places=2)
    revenue_projection = models.DecimalField(max_digits=15, decimal_places=2)
    operating_subsidy_request = models.DecimalField(max_digits=15, 
                                                     decimal_places=2)
    
    # Capital or equity contribution
    capital_contribution_request = models.DecimalField(max_digits=15,
                                                        decimal_places=2, 
                                                        default=0)
    equity_injection_request = models.DecimalField(max_digits=15, 
                                                    decimal_places=2,
                                                    default=0)
    
    # Evaluation criteria per Section 62
    # (a) Assets and resources used efficiently
    asset_utilization_ratio = models.DecimalField(max_digits=5, decimal_places=2)
    resource_efficiency_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    efficiency_analysis = models.TextField()
    
    # (b) Exposure of Bangsamoro Government to expenditures and liabilities
    contingent_liabilities = models.DecimalField(max_digits=15, decimal_places=2)
    guaranteed_loans = models.DecimalField(max_digits=15, decimal_places=2)
    potential_expenditure_exposure = models.DecimalField(max_digits=15, 
                                                          decimal_places=2)
    risk_assessment = models.TextField()
    
    # Prudence and returns assessment
    operations_warranted = models.BooleanField()
    prudent_means_utilized = models.BooleanField()
    expected_social_returns = models.TextField()
    expected_physical_returns = models.TextField()
    expected_economic_returns = models.TextField()
    returns_analysis = models.TextField()
    
    # Regional development alignment
    aligns_with_regional_policies = models.BooleanField()
    aligns_with_regional_programs = models.BooleanField()
    alignment_justification = models.TextField()
    
    # Review and approval
    review_status = models.CharField(max_length=20, choices=[
        ('SUBMITTED', 'Submitted'),
        ('UNDER_REVIEW', 'Under Review'),
        ('APPROVED', 'Approved'),
        ('APPROVED_PARTIAL', 'Partially Approved'),
        ('DISAPPROVED', 'Disapproved'),
    ])
    
    approved_operating_subsidy = models.DecimalField(max_digits=15,
                                                      decimal_places=2,
                                                      null=True, blank=True)
    approved_capital_contribution = models.DecimalField(max_digits=15,
                                                         decimal_places=2,
                                                         null=True, blank=True)
    
    # Liability guarantee restrictions
    def validate_liability_guarantee(self):
        """
        Validates Section 21: In no case shall the Bangsamoro Government 
        be liable for any implied guarantee asserted by any person or 
        entity for any borrowing by any BGOCC.
        """
        # Check for any implied guarantees
        has_implied_guarantee = False
        
        if self.bgocc.has_implied_government_guarantee:
            has_implied_guarantee = True
        
        if has_implied_guarantee:
            raise ValueError(
                "Bangsamoro Government cannot be liable for implied "
                "guarantees for BGOCC borrowing. Any money paid by the "
                "Bangsamoro Government under authority of law and expenses "
                "associated with the same shall constitute a debt due to "
                "the Bangsamoro Government from the BGOCC for whose benefit "
                "the payment was made."
            )
        
        return True
    
    class Meta:
        unique_together = ('bgocc', 'fiscal_year')
```

#### 5.2 Proposed Bangsamoro Budget Submission

**Section 22. The Proposed Bangsamoro Budget** implementation:
```python
class ProposedBangsamoroBudget(models.Model):
    """
    Implements Section 22: The Chief Minister shall submit the Proposed 
    Bangsamoro Budget to the Parliament, as far as practicable not later 
    than the thirtieth (30th) of September of each year.
    """
    
    fiscal_year = models.IntegerField(unique=True)
    
    # Submission information
    submitted_by_chief_minister = models.BooleanField(default=False)
    submission_date = models.DateField()
    deadline_date = models.DateField()  # September 30th
    submitted_on_time = models.BooleanField()
    
    # Publication requirement
    published_on_website = models.BooleanField(default=False)
    publication_date = models.DateField(null=True, blank=True)
    published_same_day = models.BooleanField()
    website_url = models.URLField(blank=True)
    
    # Budget components
    total_budget = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Link to constituent documents
    besf = models.OneToOneField('BESF', on_delete=models.CASCADE, 
                                 related_name='proposed_budget')
    chief_minister_message = models.ForeignKey('ChiefMinisterBudgetMessage',
                                                on_delete=models.CASCADE)
    expenditure_program = models.ForeignKey('BangsamoroExpenditureProgram',
                                             on_delete=models.CASCADE)
    
    # M/O/A budget proposals
    moa_proposals = models.ManyToManyField('MOABudgetProposal')
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('PREPARATION', 'In Preparation'),
        ('SUBMITTED', 'Submitted to Parliament'),
        ('UNDER_CONSIDERATION', 'Under Parliament Consideration'),
        ('ENACTED', 'Enacted as GAAB'),
        ('RE-ENACTED', 'Re-enacted'),
    ])
    
    def check_submission_compliance(self):
        """Check compliance with Section 22 requirements"""
        compliance = {
            'submitted_by_september_30': self.submitted_on_time,
            'published_same_day_as_submission': self.published_same_day,
            'mfbm_published_on_website': self.published_on_website,
        }
        
        return all(compliance.values()), compliance


class ChiefMinisterBudgetMessage(models.Model):
    """
    Implements Section 23(a): Chief Minister's Budget Message provides 
    a preview of the Proposed Bangsamoro Budget, explaining the principles, 
    objectives, and policy framework adopted and the spending priorities 
    for the fiscal year.
    """
    
    fiscal_year = models.IntegerField(unique=True)
    
    # Message content
    message_text = models.TextField()
    
    # Required elements
    principles_explanation = models.TextField()
    objectives_explanation = models.TextField()
    policy_framework = models.TextField()
    spending_priorities = models.TextField()
    
    # Economic context
    economic_outlook = models.TextField()
    fiscal_outlook = models.TextField()
    
    # Strategic direction
    strategic_initiatives = models.TextField()
    major_reforms = models.TextField()
    
    # Document
    message_document = models.FileField(upload_to='budget/cm_messages/')
    
    # Publication
    published = models.BooleanField(default=False)
    publication_date = models.DateField(null=True, blank=True)



class BangsamoroExpenditureProgram(models.Model):
    """
    Implements Section 23(b): Bangsamoro Expenditure Program outlines 
    the strategic objectives, details of the annual expenditure program, 
    and other performance information.
    """
    
    fiscal_year = models.IntegerField(unique=True)
    
    # Strategic objectives
    strategic_objectives = models.TextField()
    
    # Expenditure program details
    total_expenditure = models.DecimalField(max_digits=15, decimal_places=2)
    
    # By sector
    education_expenditure = models.DecimalField(max_digits=15, decimal_places=2)
    health_expenditure = models.DecimalField(max_digits=15, decimal_places=2)
    infrastructure_expenditure = models.DecimalField(max_digits=15, decimal_places=2)
    social_services_expenditure = models.DecimalField(max_digits=15, decimal_places=2)
    other_expenditure = models.DecimalField(max_digits=15, decimal_places=2)
    
    # By M/O/A
    moa_allocations = models.JSONField()
    
    # Performance information
    performance_targets = models.JSONField()
    key_performance_indicators = models.ManyToManyField('PerformanceIndicator')
    
    # Program details
    program_descriptions = models.TextField()
    expected_outcomes = models.TextField()
    
    # Document
    program_document = models.FileField(upload_to='budget/expenditure_programs/')


class BESF(models.Model):
    """
    Implements Section 23(c): Budget of Expenditure and Sources of Financing 
    (BESF) contains, among others, the macroeconomic parameters, dimensions 
    of the annual expenditure program, revenues, financing, and outstanding 
    debt; and an overview of the financial positions of BGOCCs, LGUs, and 
    public-private partnership (PPP) projects within the Bangsamoro 
    Autonomous Region.
    """
    
    fiscal_year = models.IntegerField(unique=True)
    
    # Macroeconomic parameters
    gdp_growth_forecast = models.DecimalField(max_digits=5, decimal_places=2)
    inflation_forecast = models.DecimalField(max_digits=5, decimal_places=2)
    unemployment_rate_forecast = models.DecimalField(max_digits=5, decimal_places=2)
    exchange_rate_forecast = models.DecimalField(max_digits=8, decimal_places=4)
    
    macroeconomic_assumptions = models.TextField()
    
    # Dimensions of annual expenditure program
    total_expenditure = models.DecimalField(max_digits=15, decimal_places=2)
    
    # By allotment class
    personnel_services = models.DecimalField(max_digits=15, decimal_places=2)
    maintenance_operating_expenses = models.DecimalField(max_digits=15, decimal_places=2)
    financial_expenses = models.DecimalField(max_digits=15, decimal_places=2)
    capital_outlays = models.DecimalField(max_digits=15, decimal_places=2)
    
    # By function
    general_public_services = models.DecimalField(max_digits=15, decimal_places=2)
    education = models.DecimalField(max_digits=15, decimal_places=2)
    health = models.DecimalField(max_digits=15, decimal_places=2)
    social_protection = models.DecimalField(max_digits=15, decimal_places=2)
    economic_affairs = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Revenues
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Revenue sources
    national_internal_revenue_share = models.DecimalField(max_digits=15, decimal_places=2)
    natural_resources_share = models.DecimalField(max_digits=15, decimal_places=2)
    block_grant = models.DecimalField(max_digits=15, decimal_places=2)
    regional_taxes = models.DecimalField(max_digits=15, decimal_places=2)
    other_revenues = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Financing
    total_financing = models.DecimalField(max_digits=15, decimal_places=2)
    domestic_borrowing = models.DecimalField(max_digits=15, decimal_places=2)
    foreign_borrowing = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Outstanding debt
    total_outstanding_debt = models.DecimalField(max_digits=15, decimal_places=2)
    domestic_debt = models.DecimalField(max_digits=15, decimal_places=2)
    foreign_debt = models.DecimalField(max_digits=15, decimal_places=2)
    debt_to_gdp_ratio = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Financial positions
    bgocc_financial_position = models.JSONField()
    lgu_financial_position = models.JSONField()
    ppp_projects_overview = models.JSONField()
    
    # Document
    besf_document = models.FileField(upload_to='budget/besf/')
```

#### 5.3 Chief Minister's Approval of Proposed Budget

**Section 24. Chief Minister's Approval of the Proposed Bangsamoro Budget** implementation:
```python
class ChiefMinisterBudgetApproval(models.Model):
    """
    Implements Section 24: The Proposed Bangsamoro Budget submitted by 
    the Chief Minister shall be the basis of the General Appropriations 
    Bill of the Bangsamoro (GABB). No legislative proposal involving the 
    appropriations of funds shall be transmitted to the Parliament without 
    the approval of the Chief Minister.
    """
    
    proposed_budget = models.OneToOneField('ProposedBangsamoroBudget',
                                            on_delete=models.CASCADE)
    
    # Chief Minister approval
    approved_by_chief_minister = models.BooleanField(default=False)
    approval_date = models.DateTimeField(null=True, blank=True)
    approved_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Approval notes
    approval_notes = models.TextField(blank=True)
    conditions = models.TextField(blank=True)
    
    # Prohibition enforcement
    def validate_transmission_to_parliament(self):
        """
        Enforce Section 24: No legislative proposal involving the 
        appropriations of funds shall be transmitted to the Parliament 
        without the approval of the Chief Minister.
        """
        if not self.approved_by_chief_minister:
            raise ValidationError(
                "Legislative proposal involving appropriations cannot be "
                "transmitted to Parliament without Chief Minister approval."
            )
        
        return True
    
    # GABB generation
    gabb = models.OneToOneField('ParliamentBill', on_delete=models.SET_NULL,
                                 null=True, blank=True,
                                 related_name='cm_approved_budget')


def enforce_cm_approval_for_appropriations(legislative_proposal):
    """
    System-wide enforcement of Section 24 requirement
    """
    if legislative_proposal.involves_appropriations:
        if not legislative_proposal.has_cm_approval():
            raise PermissionDenied(
                "This legislative proposal involves appropriations and "
                "requires Chief Minister approval before transmission "
                "to Parliament."
            )
```

#### 5.4 Schedule of Budget Consideration

**Section 25. Schedule of Budget Consideration** implementation:
```python
class ParliamentBudgetConsideration(models.Model):
    """
    Implements Section 25: The Parliament shall prioritize the consideration 
    and enactment of the GABB and the corresponding revenue bill, if any.
    """
    
    gabb = models.OneToOneField('ParliamentBill', on_delete=models.CASCADE,
                                 related_name='budget_consideration')
    revenue_bill = models.ForeignKey('ParliamentBill', on_delete=models.SET_NULL,
                                      null=True, blank=True,
                                      related_name='revenue_bill_consideration')
    
    fiscal_year = models.IntegerField()
    
    # Filing and calendaring
    filed_date = models.DateField()
    calendared_for_first_reading = models.DateField()
    
    # Timeline per Section 25
    # Filed and calendared for first reading within 5 calendar days from budget submission
    first_reading_deadline = models.DateField()  # filed_date + 5 days
    first_reading_compliant = models.BooleanField()
    
    # First reading
    first_reading_date = models.DateField(null=True, blank=True)
    
    # Second reading discussion start (within 5 calendar days after first reading)
    second_reading_start_deadline = models.DateField()  # first_reading_date + 5 days
    second_reading_start_date = models.DateField(null=True, blank=True)
    second_reading_start_compliant = models.BooleanField()
    
    # Committee referral (Parliament shall refer to committee)
    committee_referral_date = models.DateField(null=True, blank=True)
    committee = models.ForeignKey('ParliamentCommittee', on_delete=models.SET_NULL,
                                   null=True)
    
    # Committee report (no later than 60 calendar days from referral)
    committee_report_deadline = models.DateField()  # committee_referral_date + 60 days
    committee_report_date = models.DateField(null=True, blank=True)
    committee_report_compliant = models.BooleanField()
    
    # Debate and amendments (terminate within 30 calendar days from committee report)
    debate_termination_deadline = models.DateField()  # committee_report_date + 30 days
    debate_terminated_date = models.DateField(null=True, blank=True)
    debate_compliant = models.BooleanField()
    
    # Third and final reading (3 days after conclusion of second reading)
    third_reading_deadline = models.DateField()  # debate_terminated_date + 3 days
    third_reading_date = models.DateField(null=True, blank=True)
    
    # Certified/Emergency bill provisions
    is_certified_bill = models.BooleanField(default=False)
    is_emergency_bill = models.BooleanField(default=False)
    three_day_requirement_waived = models.BooleanField(default=False)
    voting_same_day_as_approval = models.BooleanField(default=False)
    
    # Overall compliance
    overall_timeline_compliant = models.BooleanField()
    
    def calculate_compliance(self):
        """Calculate overall timeline compliance"""
        checks = [
            self.first_reading_compliant,
            self.second_reading_start_compliant,
            self.committee_report_compliant,
            self.debate_compliant,
        ]
        
        self.overall_timeline_compliant = all(checks)
        return self.overall_timeline_compliant


class ParliamentBill(models.Model):
    """General Appropriations Bill of the Bangsamoro (GABB)"""
    
    bill_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    fiscal_year = models.IntegerField()
    
    # Bill type
    bill_type = models.CharField(max_length=20, choices=[
        ('GAAB', 'General Appropriations Act of Bangsamoro'),
        ('SUPPLEMENTAL', 'Supplemental Appropriation'),
        ('REVENUE', 'Revenue Bill'),
        ('OTHER', 'Other Bill'),
    ])
    
    # Filing
    filed_by = models.CharField(max_length=100)
    filed_date = models.DateField()
    
    # Content
    total_appropriation = models.DecimalField(max_digits=15, decimal_places=2)
    bill_text = models.TextField()
    bill_document = models.FileField(upload_to='parliament/bills/')
    
    # Status
    status = models.CharField(max_length=30, choices=[
        ('FILED', 'Filed'),
        ('FIRST_READING', 'First Reading'),
        ('COMMITTEE_REVIEW', 'Committee Review'),
        ('SECOND_READING', 'Second Reading'),
        ('THIRD_READING', 'Third Reading'),
        ('ENACTED', 'Enacted'),
        ('VETOED', 'Vetoed'),
    ])
    
    # Enactment
    enacted_date = models.DateField(null=True, blank=True)
    gaab = models.OneToOneField('GAAB', on_delete=models.SET_NULL,
                                 null=True, blank=True)


class ParliamentCommittee(models.Model):
    """Parliament committees for budget review"""
    
    name = models.CharField(max_length=255)
    committee_type = models.CharField(max_length=50, choices=[
        ('APPROPRIATIONS', 'Committee on Appropriations'),
        ('WAYS_MEANS', 'Committee on Ways and Means'),
        ('FINANCE', 'Committee on Finance'),
        ('OTHER', 'Other Committee'),
    ])
    
    members = models.ManyToManyField('User', through='CommitteeMembership')
    chairperson = models.ForeignKey('User', on_delete=models.SET_NULL,
                                     null=True, related_name='chaired_committees')


class CommitteeReport(models.Model):
    """Committee report on GABB"""
    
    bill = models.ForeignKey('ParliamentBill', on_delete=models.CASCADE)
    committee = models.ForeignKey('ParliamentCommittee', on_delete=models.CASCADE)
    
    report_date = models.DateField()
    report_number = models.CharField(max_length=50)
    
    # Report content
    findings = models.TextField()
    recommendations = models.TextField()
    proposed_amendments = models.TextField()
    
    # Voting
    committee_vote_for = models.IntegerField()
    committee_vote_against = models.IntegerField()
    committee_vote_abstain = models.IntegerField()
    
    # Report document
    report_document = models.FileField(upload_to='parliament/committee_reports/')
```

#### 5.5 Content of the General Appropriations Act of the Bangsamoro

**Section 26. Content of the General Appropriations Act of the Bangsamoro** implementation:
```python
class GAAB(models.Model):
    """
    Implements Section 26: The General Appropriations Act of the 
    Bangsamoro (GAAB) shall outline budgetary programs and projects 
    for each M/O/A.
    """
    
    fiscal_year = models.IntegerField(unique=True)
    
    # Enactment information
    act_number = models.CharField(max_length=50, unique=True)
    enacted_date = models.DateField()
    effective_date = models.DateField()
    
    # Parliament bill that became GAAB
    parliament_bill = models.OneToOneField('ParliamentBill',
                                            on_delete=models.CASCADE,
                                            related_name='enacted_gaab')
    
    # Total appropriation
    total_appropriation = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Account codes requirement (Section 26.a)
    uses_uniform_account_codes = models.BooleanField(default=True)
    account_coding_system = models.CharField(max_length=100,
                                              default='Modified UACS')
    
    # Program classification requirement (Section 26.b)
    uses_program_expenditure_classification = models.BooleanField(default=True)
    
    # GAAB document
    gaab_document = models.FileField(upload_to='gaab/')
    
    # Publication
    published = models.BooleanField(default=False)
    publication_date = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'GAAB'
        verbose_name_plural = 'GAABs'
        ordering = ['-fiscal_year']


class GAABItem(models.Model):
    """
    Individual appropriation items in the GAAB.
    Each P/A/P shall have its corresponding appropriation.
    """
    
    gaab = models.ForeignKey('GAAB', on_delete=models.CASCADE,
                             related_name='items')
    
    # M/O/A
    moa = models.ForeignKey('MinistryOfficeAgency', on_delete=models.CASCADE)
    
    # Program/Activity/Project
    program = models.ForeignKey('ProgramBudget', on_delete=models.SET_NULL,
                                 null=True)
    activity = models.ForeignKey('ActivityBudget', on_delete=models.SET_NULL,
                                  null=True, blank=True)
    project = models.ForeignKey('ProjectBudget', on_delete=models.SET_NULL,
                                 null=True, blank=True)
    
    # Appropriation details
    item_code = models.CharField(max_length=50)  # Account code
    item_description = models.TextField()
    appropriated_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Allotment class
    allotment_class = models.CharField(max_length=10, choices=[
        ('PS', 'Personnel Services'),
        ('MOOE', 'Maintenance and Other Operating Expenses'),
        ('FE', 'Financial Expenses'),
        ('CO', 'Capital Outlays'),
    ])
    
    # Program classification
    program_classification = models.CharField(max_length=100)
    
    # Statutory provisions (for specific M/O/As or general applicability)
    statutory_provision = models.TextField(blank=True)
    applies_to_specific_moa = models.BooleanField(default=True)
    general_applicability = models.BooleanField(default=False)
    
    # Performance targets
    target_outputs = models.TextField()
    performance_indicators = models.ManyToManyField('PerformanceIndicator')
    
    # Geographic allocation (if applicable)
    geographic_allocations = models.ManyToManyField('GeographicBudgetDisaggregation')
    
    class Meta:
        ordering = ['moa', 'item_code']
        indexes = [
            models.Index(fields=['gaab', 'moa']),
            models.Index(fields=['item_code']),
        ]


class UniformAccountCode(models.Model):
    """
    Implements Section 26(a): Uniform accounts coding system that shall 
    apply to all the assets, liabilities, equities, income, and expenses 
    of the Bangsamoro Government.
    """
    
    code = models.CharField(max_length=20, unique=True)
    code_level = models.IntegerField()  # 1=Major, 2=Minor, 3=Sub-minor, etc.
    
    parent_code = models.ForeignKey('self', on_delete=models.CASCADE,
                                     null=True, blank=True,
                                     related_name='sub_codes')
    
    # Code description
    description = models.CharField(max_length=255)
    detailed_description = models.TextField()
    
    # Classification
    account_type = models.CharField(max_length=20, choices=[
        ('ASSET', 'Asset'),
        ('LIABILITY', 'Liability'),
        ('EQUITY', 'Equity'),
        ('INCOME', 'Income/Revenue'),
        ('EXPENSE', 'Expense'),
    ])
    
    # Usage scope
    applies_to_financial_transactions = models.BooleanField(default=True)
    applies_to_appropriations = models.BooleanField(default=True)
    applies_to_reporting = models.BooleanField(default=True)
    
    # Active status
    is_active = models.BooleanField(default=True)
    effective_date = models.DateField()
    
    class Meta:
        ordering = ['code']


class ProgramExpenditureClassification(models.Model):
    """
    Implements Section 26(b): Program Expenditure Classification that 
    groups line items under the objectives or outcomes to which they 
    contribute. Performance information shall be provided for each program 
    to facilitate the evaluation of its cost-effectiveness and provide 
    better information for analysis and feedback for planning and 
    prioritization of expenditures.
    """
    
    program_code = models.CharField(max_length=20, unique=True)
    program_name = models.CharField(max_length=255)
    
    # Objectives and outcomes
    program_objectives = models.TextField()
    expected_outcomes = models.TextField()
    
    # Line items under this program
    line_items = models.ManyToManyField('GAABItem')
    
    # Total program budget
    total_program_budget = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Performance information for evaluation
    performance_indicators = models.ManyToManyField('PerformanceIndicator')
    cost_effectiveness_metrics = models.JSONField(default=dict)
    
    # Analysis and feedback
    analysis_notes = models.TextField(blank=True)
    planning_feedback = models.TextField(blank=True)
    prioritization_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True, blank=True
    )
    
    class Meta:
        ordering = ['program_code']
```

#### 5.6 Lump Sum Appropriations

**Section 27. Lump Sum Appropriations** implementation:
```python
class LumpSumAppropriationCategory(models.Model):
    """
    Implements Section 27: To promote the transparent and detailed 
    disclosure of all proposed government spending, lump sum appropriations 
    and special purpose funds (SPFs) in the GAAB shall include specific 
    categories defined in the Act.
    """
    
    CATEGORY_CHOICES = [
        ('CONTINGENT_FUND', 'Contingent Fund'),
        ('SPECIAL_DEVELOPMENT_FUND', 'Special Development Fund'),
        ('LGU_STATUTORY_SHARES', 'Statutory Shares of Constituent LGUs'),
        ('LOCAL_GOVT_SUPPORT_FUND', 'Local Government Support Fund'),
        ('OTHER_SPF', 'Other Special Purpose Fund'),
    ]
    
    gaab = models.ForeignKey('GAAB', on_delete=models.CASCADE,
                             related_name='lump_sum_appropriations')
    
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    category_description = models.TextField()
    
    # Appropriated amount
    appropriated_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Parliamentary approval requirement
    approved_by_parliament = models.BooleanField()
    approval_date = models.DateField(null=True, blank=True)
    
    # Exceptional circumstances justification (for other SPFs)
    is_exceptional_circumstance = models.BooleanField(default=False)
    exceptional_justification = models.TextField(blank=True)
    public_interest_justification = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('gaab', 'category')


class ContingentFund(models.Model):
    """
    Implements Section 28: The Contingent Fund shall cover the funding 
    requirements of new or urgent projects and activities of M/O/As that 
    need to be implemented or paid during the fiscal year.
    """
    
    gaab = models.ForeignKey('GAAB', on_delete=models.CASCADE)
    fiscal_year = models.IntegerField()
    
    # Total appropriation for Contingent Fund
    total_appropriation = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Remaining balance
    remaining_balance = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Covered purposes per Section 28
    PURPOSE_CHOICES = [
        ('NEWLY_CREATED_MOA', 'Requirements of newly-created M/O/As'),
        ('SPECIAL_PROJECTS', 'Special projects to align with national development priorities'),
        ('APPROPRIATION_DEFICIENCIES', 'Deficiencies in appropriations for disaster-related purposes'),
        ('LEGAL_OBLIGATION', 'Legal obligation arising from final and executory decisions'),
        ('UNFORESEEN_REQUIREMENTS', 'Urgent and unforeseen requirements'),
    ]
    
    def create_release(self, purpose, amount, recipient_moa, justification):
        """Create a release from the Contingent Fund"""
        
        if amount > self.remaining_balance:
            raise ValueError("Insufficient balance in Contingent Fund")
        
        release = ContingentFundRelease(
            contingent_fund=self,
            purpose=purpose,
            amount=amount,
            recipient_moa=recipient_moa,
            justification=justification
        )
        
        # Release requires Chief Minister approval
        release.status = 'PENDING_CM_APPROVAL'
        release.save()
        
        return release


class ContingentFundRelease(models.Model):
    """
    Releases from the Contingent Fund per Section 28
    """
    
    contingent_fund = models.ForeignKey('ContingentFund', on_delete=models.CASCADE,
                                         related_name='releases')
    
    # Release details
    purpose = models.CharField(max_length=50, 
                                choices=ContingentFund.PURPOSE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    recipient_moa = models.ForeignKey('MinistryOfficeAgency',
                                       on_delete=models.CASCADE)
    
    # Justification and documentation per Section 28
    justification = models.TextField()
    
    # Documentary requirements (shall be submitted but not limited to)
    indicative_program_plans = models.FileField(upload_to='contingent_fund/plans/',
                                                 blank=True)
    construction_plans = models.FileField(upload_to='contingent_fund/construction/',
                                           blank=True)
    program_of_works = models.FileField(upload_to='contingent_fund/pow/',
                                         blank=True)
    indicative_procurement_plan = models.FileField(upload_to='contingent_fund/procurement/',
                                                     blank=True)
    cost_benefit_analysis = models.FileField(upload_to='contingent_fund/analysis/',
                                              blank=True)
    beneficiaries_list = models.FileField(upload_to='contingent_fund/beneficiaries/',
                                           blank=True)
    
    # MFBM review and recommendation
    mfbm_reviewed = models.BooleanField(default=False)
    mfbm_review_date = models.DateField(null=True, blank=True)
    mfbm_recommendation = models.TextField(blank=True)
    
    # Chief Minister approval
    status = models.CharField(max_length=30, choices=[
        ('PENDING_MFBM_REVIEW', 'Pending MFBM Review'),
        ('PENDING_CM_APPROVAL', 'Pending Chief Minister Approval'),
        ('APPROVED', 'Approved'),
        ('DISAPPROVED', 'Disapproved'),
    ])
    
    cm_approved = models.BooleanField(default=False)
    cm_approval_date = models.DateField(null=True, blank=True)
    cm_approval_notes = models.TextField(blank=True)
    
    # Release date
    release_date = models.DateField(null=True, blank=True)
    
    # Reporting requirement
    reported_in_annual_fiscal_report = models.BooleanField(default=False)
    
    def process_release(self):
        """
        Process release after approval per Section 28:
        Releases from the Contingent Fund shall be reflected in the annual 
        fiscal reports, including information on the date of release, the 
        amount covered, corresponding purpose/s, and recipient M/O/A.
        """
        if not self.cm_approved:
            raise ValueError("Release must be approved by Chief Minister")
        
        # Deduct from Contingent Fund balance
        self.contingent_fund.remaining_balance -= self.amount
        self.contingent_fund.save()
        
        # Set release date
        self.release_date = timezone.now().date()
        self.save()
        
        # Create fiscal report entry
        fiscal_report_entry = FiscalReportContingentFundRelease(
            contingent_fund_release=self,
            release_date=self.release_date,
            amount=self.amount,
            purpose=self.get_purpose_display(),
            recipient_moa=self.recipient_moa
        )
        fiscal_report_entry.save()
```

---

## Part III: Accountability and Oversight

### 8. Accountability and Reporting Framework

#### 8.1 Submission of Budget and Financial Accountability Reports

**Section 59. Submission of Budget and Financial Accountability Reports** implementation:
```python
class BudgetFinancialAccountabilityReport(models.Model):
    """
    Implements Section 59: Each M/O/A shall report to the MFBM the current 
    status of its appropriations, cumulative allotments, obligations incurred 
    or liquidated, total disbursements, unliquidated obligations and unexpended 
    balances, and the result of expended appropriations.
    """
    
    moa = models.ForeignKey('MinistryOfficeAgency', on_delete=models.CASCADE)
    fiscal_year = models.IntegerField()
    reporting_period = models.CharField(max_length=20, choices=[
        ('Q1', 'First Quarter'),
        ('Q2', 'Second Quarter'),
        ('Q3', 'Third Quarter'),
        ('Q4', 'Fourth Quarter / Year-End'),
    ])
    
    # Submission information
    submitted_date = models.DateTimeField(auto_now_add=True)
    submission_deadline = models.DateField()
    submitted_on_time = models.BooleanField()
    
    # Appropriations status
    total_appropriations = models.DecimalField(max_digits=15, decimal_places=2)
    
    # By allotment class
    ps_appropriation = models.DecimalField(max_digits=15, decimal_places=2)
    mooe_appropriation = models.DecimalField(max_digits=15, decimal_places=2)
    fe_appropriation = models.DecimalField(max_digits=15, decimal_places=2)
    co_appropriation = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Cumulative allotments
    total_allotments = models.DecimalField(max_digits=15, decimal_places=2)
    ps_allotments = models.DecimalField(max_digits=15, decimal_places=2)
    mooe_allotments = models.DecimalField(max_digits=15, decimal_places=2)
    fe_allotments = models.DecimalField(max_digits=15, decimal_places=2)
    co_allotments = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Obligations incurred or liquidated
    total_obligations = models.DecimalField(max_digits=15, decimal_places=2)
    ps_obligations = models.DecimalField(max_digits=15, decimal_places=2)
    mooe_obligations = models.DecimalField(max_digits=15, decimal_places=2)
    fe_obligations = models.DecimalField(max_digits=15, decimal_places=2)
    co_obligations = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Total disbursements
    total_disbursements = models.DecimalField(max_digits=15, decimal_places=2)
    ps_disbursements = models.DecimalField(max_digits=15, decimal_places=2)
    mooe_disbursements = models.DecimalField(max_digits=15, decimal_places=2)
    fe_disbursements = models.DecimalField(max_digits=15, decimal_places=2)
    co_disbursements = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Unliquidated obligations
    unliquidated_obligations = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Unexpended balances
    unexpended_balances = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Result of expended appropriations
    expended_appropriations_result = models.TextField()
    
    # Performance versus plans and targets
    performance_summary = models.TextField()
    variance_analysis = models.TextField()
    
    # Supporting documents
    bfar_document = models.FileField(upload_to='bfars/')
    
    # MFBM review
    reviewed_by_mfbm = models.BooleanField(default=False)
    mfbm_review_date = models.DateField(null=True, blank=True)
    mfbm_comments = models.TextField(blank=True)
    
    # Compliance metrics
    budget_utilization_rate = models.DecimalField(max_digits=5, decimal_places=2)
    obligation_rate = models.DecimalField(max_digits=5, decimal_places=2)
    disbursement_rate = models.DecimalField(max_digits=5, decimal_places=2)
    
    def calculate_utilization_rates(self):
        """Calculate budget utilization metrics"""
        
        if self.total_appropriations > 0:
            self.budget_utilization_rate = (
                (self.total_allotments / self.total_appropriations) * 100
            )
            
        if self.total_allotments > 0:
            self.obligation_rate = (
                (self.total_obligations / self.total_allotments) * 100
            )
            
        if self.total_obligations > 0:
            self.disbursement_rate = (
                (self.total_disbursements / self.total_obligations) * 100
            )
        
        self.save()
    
    class Meta:
        unique_together = ('moa', 'fiscal_year', 'reporting_period')
        ordering = ['-fiscal_year', 'reporting_period', 'moa']
```

---

## Part IV: Implementation and Operations

### 11. Implementation Roadmap and Phases

#### 11.1 Overall Implementation Strategy

The Bangsamoro Budget System will be implemented in six phases over 18 months:

**Phase 1: Foundation and Core Systems (Months 1-4)**
- Legal framework setup and compliance mapping
- Database schema design and implementation
- User authentication and role-based access control
- Basic budget preparation module
- Integration with existing OBCMS infrastructure

**Phase 2: Budget Preparation and Planning (Months 5-7)**
- Budget Call management
- Budget Priorities Framework
- M/O/A budget proposal workflows
- Budget endorsement and evaluation
- BESF generation
- Chief Minister approval workflows

**Phase 3: Budget Authorization (Months 8-10)**
- Parliament bill management
- Committee review workflows
- Budget amendment tracking
- GAAB generation and management
- Account codes and program classification
- Lump sum appropriations and SPF management

**Phase 4: Budget Execution (Months 11-13)**
- Allotment release (GAABAO, SARO)
- Obligation tracking
- Disbursement management
- Cash budgeting system
- Multi-year contracting
- Savings and augmentation

**Phase 5: Financial Management and Treasury (Months 14-15)**
- Single Treasury Account
- General Fund and Special Purpose Funds
- Revolving Fund management
- Investment management
- Cash management

**Phase 6: Accountability and Transparency (Months 16-18)**
- BFAR generation and submission
- Annual reports to Parliament
- Fiscal Report preparation
- Transparency seal implementation
- People's Budget summaries
- Public participation mechanisms
- Full system integration testing
- User acceptance testing
- Go-live preparation

#### 11.2 Phase 1 Implementation Details

**Deliverables:**
1. Legal compliance matrix mapping all Act provisions to system features
2. Complete database schema with all tables and relationships
3. User management system with RBAC
4. Budget preparation forms and templates
5. Basic workflow engine
6. Integration with OBCMS WorkItem system
7. Development environment setup

**Technical Tasks:**
- Django applications structure creation
- PostgreSQL database setup
- Redis configuration for Celery
- HTMX and Alpine.js integration for UI
- API endpoints for external integration
- Audit logging implementation
- Initial test suite

**Duration:** 4 months
**Team Size:** 6 developers, 2 QA, 1 project manager, 1 business analyst

#### 11.3 Success Criteria

Each phase will be evaluated against the following success criteria:

**Functional Completeness:**
- All required features implemented per Act provisions
- 100% of legislative requirements mapped to system features
- All workflows operational and tested

**Performance:**
- Response times meet specified targets
- System handles concurrent users without degradation
- Reports generate within specified timeframes

**Compliance:**
- Full compliance with Bangsamoro Budget System Act
- Audit trail for all transactions
- Security requirements met

**User Acceptance:**
- Positive feedback from user acceptance testing
- Training completion for all user roles
- User documentation complete and accessible

**Integration:**
- Seamless integration with existing OBCMS modules
- API endpoints functional and documented
- Data migration successful (if applicable)

---

## Conclusion

This comprehensive plan provides the foundation for implementing a world-class budget system for the Bangsamoro Government, fully compliant with the Bangsamoro Budget System Act and aligned with international best practices in public financial management.

The phased implementation approach ensures systematic rollout while maintaining operational continuity. Integration with the existing OBCMS ecosystem leverages proven infrastructure and ensures consistency across all government management functions.

Success will be measured not only by technical implementation but by the system's contribution to fiscal responsibility, transparency, and accountability in the Bangsamoro Autonomous Region.

---

**Document Control:**
- Version: 1.0 (Draft)
- Date: October 12, 2025
- Classification: Internal Use Only
- Next Review: Upon completion of Phase 1
- Approval Required: MFBM, BBCC, Chief Minister

**Prepared by:** OBCMS Development Team  
**For:** Bangsamoro Transition Authority

---

*BANGSAMORO KA, SAAN KA MAN!*
