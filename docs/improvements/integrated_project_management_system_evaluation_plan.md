# Integrated Project Management System: Evaluation & Implementation Plan

**Document Status**: Implementation Roadmap
**Date Created**: October 1, 2025
**Reference Documents**:
- [Planning & Budgeting Implementation Evaluation](✅planning_budgeting_implementation_evaluation.md)
- [Integrated Calendar System Evaluation Plan](integrated_calendar_system_evaluation_plan.md)
- [OBC Guidelines Assistance](../guidelines/OBC_guidelines_assistance.md)

---

## Executive Summary

This document evaluates the OBCMS codebase and presents a comprehensive plan for an **Integrated Project Management System** that connects:

- **Planning & Budgeting** (Annual Investment Planning, Budget Allocation, Scenario Planning)
- **MOA and OOBC PPAs** (Programs, Projects, and Activities)
- **OBC Data** (community profiles and demographics)
- **MANA** (Mapping and Needs Assessment)
- **Coordination** (multi-stakeholder partnerships)
- **Recommendations** (Policies, Programs, Services)
- **M&E** (Monitoring and Evaluation)
- **Other OBCMS/OOBC mandates and functions**

### The Role of Planning & Budgeting

**Planning & Budgeting is the financial backbone of the integrated project management system.** It transforms identified community needs and policy recommendations into funded, actionable projects through:

1. **Evidence-Based Budgeting**: Needs from MANA assessments directly inform budget allocation priorities
2. **Strategic Alignment**: Annual planning cycles align with multi-year strategic goals
3. **Multi-Source Funding**: Coordinate GAA, Block Grant, LGU, and donor funding streams
4. **Participatory Processes**: Community voting on budget priorities ensures grassroots engagement
5. **Budget Approval Workflow**: Structured 5-stage approval process ensures accountability
6. **Cost-Effectiveness Tracking**: Monitor cost per beneficiary and optimize resource allocation
7. **Real-Time Budget Monitoring**: Track budget ceilings, obligations, and disbursements throughout fiscal year

### Key Findings

**🟢 Excellent Foundation (70-85% Complete)**:
The codebase has **exceptional data models** and **well-designed integration patterns** already in place. Most foundational features from the planning & budgeting evaluation have been implemented.

**🟡 Missing Integration Layer (15-30% Complete)**:
- No unified project management dashboard/interface
- Limited cross-module workflow automation
- Fragmented user experience across modules
- No centralized task management for PPAs
- Incomplete M&E analytics and reporting dashboards

**🔴 Critical Need**:
An **integrated project management layer** that sits above existing modules to:
1. Provide unified project lifecycle management (Need → Budget → Implementation → M&E)
2. Enable seamless cross-module workflows with budget approval gates
3. Consolidate monitoring, evaluation, and financial reporting
4. Create a single source of truth for all OOBC projects and budgets
5. **Integrate planning & budgeting throughout the project lifecycle** - not as a separate module, but as the financial dimension of every project decision

---

## Table of Contents

1. [Current System Evaluation](#current-system-evaluation)
   - Module 1: OBC Data (Communities)
   - Module 2: MANA (Mapping and Needs Assessment)
   - Module 3: Coordination (Partnerships & Stakeholder Engagement)
   - Module 4: Monitoring (PPAs and M&E)
   - **Module 5: Planning & Budgeting** ⭐
   - Module 6: Policy Recommendations
   - Module 7: Services (Service Catalog)
   - Module 8: Staff Task Management
2. [Integration Architecture](#integration-architecture)
3. [Integrated Project Management Features](#integrated-project-management-features)
   - Feature 1: Portfolio Dashboard
   - Feature 2: Project Lifecycle Workflow
   - Feature 3: Integrated Task Management
   - Feature 4: M&E Analytics Dashboard
   - Feature 5: Automated Alerts & Notifications
   - **Feature 6: Planning & Budgeting Management** ⭐
   - Feature 7: Integrated Reporting
4. [Implementation Plan](#implementation-plan)
5. [Technical Specifications](#technical-specifications)

---

## Current System Evaluation

### Module 1: OBC Data (Communities)
**Location**: `src/communities/models.py`
**Maturity**: 🟢 **85% Complete**

#### Existing Features ✅

**`OBCCommunity` Model** - Comprehensive community profile system:
- **Demographics**: Population, households, families, age distribution
- **Vulnerable Sectors**: Women, PWD, farmers, fisherfolk, IDPs, migrants
- **Ethnolinguistic Groups**: 23 distinct groups tracked
- **Economic Data**: MSMEs, cooperatives, unbanked populations
- **Cultural/Religious**: Mosques, madrasah, religious leaders, asatidz
- **Geographic**: Coordinates, proximity to BARMM, settlement types
- **Infrastructure**: Healthcare, education, utilities access

#### Strengths
- ✅ Comprehensive demographic tracking
- ✅ Excellent vulnerable sector categorization
- ✅ Cultural and religious data well-structured
- ✅ Geographic mapping support

#### Gaps
- ❌ No unified "community needs dashboard" linking to MANA
- ❌ Limited visualization of community-level project impacts
- ❌ No real-time update mechanism for community data changes

---

### Module 2: MANA (Mapping and Needs Assessment)
**Location**: `src/mana/models.py`
**Maturity**: 🟢 **90% Complete**

#### Existing Features ✅

**`Assessment` Model** (lines 64-350):
- Assessment levels: regional, provincial, municipal, barangay, community
- Methodologies: desk review, survey, KII, workshop, participatory, mixed
- Status workflow: planning → data_collection → analysis → reporting → completed
- Priority levels: low, medium, high, critical
- Geographic coverage with cascading relationships

**`Need` Model** (lines 866-1050+) - **EXCELLENT**:
- **Comprehensive need tracking** with full lifecycle
- **Built-in prioritization**: urgency_level, impact_severity, feasibility, priority_score, priority_rank
- **Community participation fields** (Phase 1 implemented):
  - `submission_type`: assessment_driven vs. community_submitted
  - `submitted_by_user`: Community leader submission
  - `community_votes`: Participatory budgeting support
  - `forwarded_to_mao`: MAO coordination workflow
  - `linked_ppa`: Budget linkage to MonitoringEntry
- **Status workflow**: identified → validated → prioritized → planned → in_progress → completed
- **Evidence tracking**: evidence_sources, validation_method, is_validated

#### Strengths
- ✅ Excellent prioritization framework
- ✅ Community participation built-in
- ✅ Budget linkage implemented
- ✅ MAO coordination workflow
- ✅ Comprehensive status tracking

#### Gaps
- ❌ No centralized "needs gap analysis" dashboard
- ❌ Limited bulk operations for needs management
- ❌ No automated alerts when high-priority needs remain unfunded

---

### Module 3: Coordination (Partnerships & Stakeholder Engagement)
**Location**: `src/coordination/models.py`
**Maturity**: 🟢 **80% Complete**

#### Existing Features ✅

**`Organization` Model** (lines 579-820):
- Organization types: bmoa (MAO), lgu, nga, ingo, ngo, cso, academic, etc.
- Partnership levels: implementing, funding, technical, coordinating
- Mandate and functions documentation
- Contact information and key personnel
- Partnership status tracking

**`MAOFocalPerson` Model** (lines 822-913) - **NEW in Phase 1**:
- Primary/alternate focal person tracking
- Contact information management
- Appointment date tracking
- Active status management

**`MAOQuarterlyReport` Model** (lines 1935-2024) - **NEW in Phase 1**:
- Links to quarterly coordination meetings
- PPAs implemented tracking (M2M to MonitoringEntry)
- Regions covered
- Budget and beneficiary counts
- Accomplishments, challenges, plans, coordination needs

**`StakeholderEngagement` Model** (lines 66-150):
- Engagement types: consultation, workshop, FGD, community assembly
- IAP2 participation levels: inform, consult, involve, collaborate, empower
- Budget tracking
- Feedback system

**`Partnership` Model** (lines 2547+):
- Partnership types: moa, mou, joint_project, service_agreement
- Lead and partner organizations
- Scope, objectives, deliverables
- Financial commitments
- Performance monitoring

**`Event` Model** (lines 1400+):
- Event types: meeting, consultation, workshop, planning, review
- Quarterly meeting support: `is_quarterly_coordination`, `quarter`, `fiscal_year`
- Participant tracking
- Action items with dependencies
- Document management

#### Strengths
- ✅ Comprehensive stakeholder engagement system
- ✅ MAO coordination fully implemented
- ✅ Quarterly reporting workflow in place
- ✅ Partnership management robust

#### Gaps
- ❌ No unified "coordination dashboard" showing all partnerships, engagements, and meetings
- ❌ Limited visualization of MAO participation rates
- ❌ No automated reminders for quarterly report submissions

---

### Module 4: Monitoring (PPAs and M&E)
**Location**: `src/monitoring/models.py`
**Maturity**: 🟢 **85% Complete**

#### Existing Features ✅

**`MonitoringEntry` Model** - **COMPREHENSIVE PPA TRACKING**:

**Categories**:
- `moa_ppa`: MOA Project/Program/Activity
- `oobc_ppa`: OOBC Project/Program/Activity
- `obc_request`: OBC Request or Proposal

**Core Relationships** (PHASE 1 INTEGRATION):
```python
# Many-to-Many (NEW)
needs_addressed = M2M to mana.Need
implementing_policies = M2M to policy_tracking.PolicyRecommendation

# Foreign Keys
lead_organization → coordination.Organization
implementing_moa → coordination.Organization
supporting_organizations → M2M coordination.Organization
submitted_by_community → communities.OBCCommunity
communities → M2M communities.OBCCommunity
related_assessment → mana.Assessment
related_event → coordination.Event
related_policy → policy_tracking.PolicyRecommendation (DEPRECATED)
```

**Budget & Financial Tracking**:
- Appropriation class: PS (Personnel Services), MOOE, CO (Capital Outlay)
- Funding sources: GAA, Block Grant, LGU, Donor, Internal, Others
- Budget ceiling, allocation, OBC allocation
- Cost per beneficiary, cost-effectiveness rating
- Funding flows with obligations and disbursements

**Planning & Alignment**:
- Sector classification: economic, social, infrastructure, environment, governance, peace
- Strategic alignment: `goal_alignment` JSONField
- Moral governance pillar tracking
- Compliance flags: GAD, CCET, Indigenous Peoples, Peace, SDG
- Plan year, fiscal year, program code

**M&E Framework**:
```python
outcome_framework = JSONField(default=dict)
# Structure: {
#   "outputs": [{"indicator": "...", "target": 100, "actual": 85}],
#   "outcomes": [{"indicator": "...", "target": 90, "actual": 88}],
#   "impacts": [{"indicator": "...", "target": 75, "actual": null}]
# }
```
- Standard outcome indicators (M2M to OutcomeIndicator)
- Progress percentage (0-100%)
- Accomplishments (TextField)
- Challenges (TextField)
- Support required

**Status Tracking**:
- PPA status: planning, ongoing, completed, on_hold, cancelled
- Request status: submitted, under_review, endorsed, approved, in_progress, completed, declined
- Priority levels: low, medium, high, urgent

#### Strengths
- ✅ Comprehensive PPA tracking
- ✅ Excellent budget and financial management
- ✅ Strong integration with needs and policies (M2M)
- ✅ Structured M&E framework
- ✅ Multiple funding source support
- ✅ Cost-effectiveness tracking

#### Gaps
- ❌ No unified "project dashboard" showing PPA lifecycle
- ❌ Limited real-time M&E analytics dashboard
- ❌ No automated progress alerts
- ❌ No consolidated view of PPAs by strategic goal

---

### Module 5: Planning & Budgeting
**Location**: `src/monitoring/models.py`, `src/monitoring/strategic_models.py`
**Maturity**: 🟢 **80% Complete**

#### Existing Features ✅

**Budget Management in `MonitoringEntry`**:

```python
# Appropriation & Funding
appropriation_class = CharField  # PS, MOOE, CO
funding_source = CharField       # GAA, Block Grant, LGU, Donor, etc.
funding_source_other = CharField

# Budget Amounts
budget_ceiling = DecimalField    # For scenario planning
budget_allocation = DecimalField # Actual allocation
budget_obc_allocation = DecimalField  # OBC-specific
budget_currency = CharField

# Slots & Cost Analysis
total_slots = PositiveIntegerField
obc_slots = PositiveIntegerField
cost_per_beneficiary = DecimalField
cost_effectiveness_rating = CharField  # very_high, high, moderate, low

# Strategic Alignment
plan_year = PositiveIntegerField
fiscal_year = PositiveIntegerField
program_code = CharField
plan_reference = CharField       # Reference to PDP/PIP/AIP
goal_alignment = JSONField       # Strategic tags
moral_governance_pillar = CharField

# Compliance Flags
compliance_gad = BooleanField          # Gender and Development
compliance_ccet = BooleanField         # Climate Change Expenditure
benefits_indigenous_peoples = BooleanField
supports_peace_agenda = BooleanField
supports_sdg = BooleanField
```

**`FundingFlow` Model** (tracking obligations and disbursements):
```python
class FundingFlow(models.Model):
    monitoring_entry = FK to MonitoringEntry
    flow_type = CharField  # 'allocation', 'obligation', 'disbursement'
    amount = DecimalField
    transaction_date = DateField
    funding_source = CharField
    allotment_class = CharField  # PS, MOOE, CO
    document_reference = CharField
    notes = TextField
```

**Strategic Planning Models**:

**`StrategicGoal` Model**:
- Multi-year goals (3-5 years)
- Sector classification
- Budget estimation: `estimated_total_budget`
- Target and baseline values
- Links to PPAs: `linked_ppas` (M2M MonitoringEntry)
- Links to policies: `linked_policies` (M2M PolicyRecommendation)
- Progress tracking

**`AnnualPlanningCycle` Model**:
- Fiscal year tracking
- Budget envelope: `total_budget_envelope`, `allocated_budget`
- Timeline milestones: planning → budget_preparation → approval → execution → monitoring
- Links to strategic goals, PPAs, and needs
- Status workflow tracking
- Document management (plan_document_url, budget_document_url)
- Budget utilization rate calculation

**Budget Ceilings**:
Currently tracked at PPA level (`budget_ceiling` field in MonitoringEntry)

#### Strengths
- ✅ Comprehensive budget tracking per PPA
- ✅ Multi-source funding support (GAA, Block Grant, Donor, etc.)
- ✅ Appropriation class tracking (PS/MOOE/CO)
- ✅ Cost-effectiveness analysis
- ✅ Strategic planning framework (multi-year + annual)
- ✅ Budget envelope management
- ✅ Funding flow tracking (allocation → obligation → disbursement)
- ✅ Compliance tagging (GAD, CCET, IP, SDG)

#### Gaps
- ❌ No centralized "Budget Planning Dashboard"
- ❌ No budget scenario comparison tools
- ❌ Limited budget ceiling management (no per-sector/per-source ceilings)
- ❌ No automated budget vs. actual variance analysis
- ❌ No budget approval workflow (status tracking only)
- ❌ No participatory budgeting interface (though Need.community_votes exists)
- ❌ No budget allocation by region visualization
- ❌ No forecasting tools for future years

---

### Module 6: Policy Recommendations
**Location**: `src/recommendations/policy_tracking/models.py`
**Maturity**: 🟢 **85% Complete**

#### Existing Features ✅

**`PolicyRecommendation` Model** (lines 16-335):
- **Status workflow**: draft → under_review → submitted → approved → in_implementation → implemented
- **Priority levels**: low, medium, high, urgent, critical
- **Categories**: economic, social, cultural, rehabilitation, protection
- **Relationships**:
  - `target_communities` → M2M OBCCommunity
  - `related_assessments` → M2M Assessment
  - `related_needs` → M2M Need
  - `implementing_ppas` ← M2M MonitoringEntry (reverse relationship)
- **Evidence system**: PolicyEvidence model
- **Impact tracking**: PolicyImpact model
- **Document management**: PolicyDocument model
- **Budget implications**: budget field
- **Resource requirements**: resource_requirements field

**`PolicyEvidence` Model**:
- Evidence types: quantitative, qualitative, research, needs assessment, consultation
- Reliability levels
- Verification workflow

**`PolicyImpact` Model**:
- Impact types: economic, social, educational, cultural, etc.
- Baseline, target, current, final values
- Measurement methods and units
- Target achievement percentage
- Confidence levels and data quality ratings

#### Strengths
- ✅ Comprehensive policy tracking
- ✅ Excellent evidence-based system
- ✅ Impact measurement framework
- ✅ Strong linkage to needs and assessments
- ✅ Budget implications tracking

#### Gaps
- ❌ No "policy implementation dashboard" showing aggregate progress
- ❌ No automated alerts for policy milestones
- ❌ Limited visualization of policy-to-budget linkage

---

### Module 7: Services (Service Catalog)
**Location**: `src/services/models.py`
**Maturity**: 🟢 **75% Complete** (NEW - Phase 3)

#### Existing Features ✅

**`ServiceOffering` Model**:
- Service types: financial, training, livelihood, education, health, infrastructure, legal, social, technical
- Status: draft, active, paused, closed, archived
- Eligibility levels: individual, household, community, organization, LGU
- **Relationships**:
  - `offering_mao` → coordination.Organization (bmoa only)
  - `focal_person` → coordination.MAOFocalPerson
  - `linked_ppas` → M2M monitoring.MonitoringEntry
- Budget allocated and utilized tracking
- Slot management: total_slots, slots_filled
- Application timeline management
- Application process documentation

**`ServiceApplication` Model** (referenced but not shown in snippet):
- Application workflow
- Status tracking
- Applicant information

#### Strengths
- ✅ Service catalog infrastructure
- ✅ MAO ownership clear
- ✅ Budget linkage to PPAs
- ✅ Slot management

#### Gaps
- ❌ No public-facing service catalog view
- ❌ Limited application tracking dashboard
- ❌ No automated matching of services to needs

---

### Module 8: Staff Task Management
**Location**: `src/common/models.py` (StaffTask, StaffTeam)
**Maturity**: 🟢 **75% Complete**

#### Existing Features ✅

**`StaffTask` Model**:
- Task management with status workflow (todo, in_progress, completed, cancelled)
- Priority levels (low, normal, high, urgent)
- Due dates and reminders
- Task dependencies
- Links to events: `linked_event` → coordination.Event
- Assignments: `assigned_to` (User), `assigned_team` (StaffTeam)
- Progress percentage tracking
- Kanban-style views supported

**`StaffTeam` Model**:
- Team structure
- Team members
- Team lead designation

#### Strengths
- ✅ Comprehensive task management
- ✅ Team collaboration support
- ✅ Dependency tracking
- ✅ Kanban view implemented

#### Gaps
- ❌ No direct link to PPAs (MonitoringEntry)
- ❌ No link to project workflows
- ❌ No automated task generation based on workflows
- ❌ No PPA-specific task templates

---

#### Existing Features ✅

**`StrategicGoal` Model**:
- Multi-year goals (3-5 years)
- Sector classification
- Priority levels: critical, high, medium, low
- Alignment tracking: RDP, national framework
- Target and baseline values with units
- Budget estimation
- **Relationships**:
  - `lead_agency` → coordination.Organization
  - `supporting_agencies` → M2M coordination.Organization
  - `linked_ppas` → M2M monitoring.MonitoringEntry
  - `linked_policies` → M2M policy_tracking.PolicyRecommendation
- Progress percentage tracking

**`AnnualPlanningCycle` Model**:
- Fiscal year tracking
- Timeline milestones: planning, budget prep, approval, execution
- Budget envelope and allocation tracking
- **Relationships**:
  - `strategic_goals` → M2M StrategicGoal
  - `monitoring_entries` → M2M monitoring.MonitoringEntry
  - `needs_addressed` → M2M mana.Need
- Status workflow: planning → budget_preparation → budget_approval → execution → monitoring → completed
- Budget utilization rate calculation

#### Strengths
- ✅ Multi-year strategic planning framework
- ✅ Annual planning cycle tracking
- ✅ Strong linkage to PPAs, goals, needs
- ✅ Budget envelope management

#### Gaps
- ❌ No strategic planning dashboard
- ❌ No multi-year progress visualization
- ❌ Limited scenario planning tools

---

## Integration Architecture

### Current Integration Status

```
┌──────────────────────────────────────────────────────────────────┐
│                    EXISTING INTEGRATION LAYER                     │
│                         (Well-Designed)                           │
└──────────────────────────────────────────────────────────────────┘

┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   OBC Data  │  │    MANA     │  │ Coordination│  │   Policies  │
│ Communities │  │ Assessments │  │Organizations│  │Recommendations│
│             │  │    Needs    │  │  Partnerships│  │             │
│             │  │             │  │   Events    │  │             │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │                │
       │                │                │                │
       │         ┌──────┴────────────────┴────────┬───────┘
       │         │                                 │
       │         ▼                                 ▼
       │  ┌──────────────────────────────────────────────┐
       │  │         MONITORING (PPAs & M&E)              │
       │  │         MonitoringEntry Model                │
       │  │  ┌────────────────────────────────────────┐  │
       └─▶│  │ Relationships:                         │  │
          │  │ • communities (M2M OBCCommunity)       │  │
          │  │ • needs_addressed (M2M Need)           │  │
          │  │ • implementing_policies (M2M Policy)   │  │
          │  │ • lead_organization (FK Organization)  │  │
          │  │ • related_assessment (FK Assessment)   │  │
          │  │ • related_event (FK Event)             │  │
          │  └────────────────────────────────────────┘  │
          └──────────────────────────────────────────────┘
                           │
                           ▼
                 ┌──────────────────┐
                 │  Services        │
                 │  ServiceOffering │
                 │  (linked_ppas)   │
                 └──────────────────┘
                           │
                           ▼
                 ┌──────────────────┐
                 │ Strategic Planning│
                 │  AnnualPlanningCycle│
                 │  (monitoring_entries)│
                 └──────────────────┘
```

### ✅ Existing Integration Strengths

1. **MonitoringEntry as Central Hub**: PPAs connect to all modules
2. **Need Model Integration**: Links communities, assessments, policies, and budget
3. **MAO Coordination**: Organization model connects to PPAs, services, and reports
4. **Strategic Alignment**: Planning cycles link goals, PPAs, and needs
5. **Policy-Budget Linkage**: M2M relationships enable comprehensive tracking

### ❌ Missing Integration Layer

**Problem**: While data models are well-integrated, there's **no unified user interface** or **workflow management layer** that brings everything together.

**What's Missing**:
1. **Unified Project Dashboard**: No single view showing PPA lifecycle from need → **budget planning** → policy → **budget approval** → implementation → M&E → **financial closeout**
2. **Cross-Module Workflows**: No automated workflows that span needs assessment, budget planning, approval gates, and implementation
3. **Budget-Aware Task Management**: No task system that integrates budget milestones (submission deadlines, approval stages, disbursement tracking)
4. **Integrated Financial Reporting**: No consolidated dashboards showing budget utilization alongside programmatic outcomes
5. **Real-time Budget Alerts**: Limited automation for budget ceiling warnings, approval bottlenecks, disbursement delays
6. **Participatory Budgeting Interface**: Community voting on budget priorities exists in data model but no UI workflow

---

## Integrated Project Management Features

### Proposed Architecture: "Project Management Portal"

**Concept**: Create an **integrated project management layer** called **"Project Management Portal"** that provides:
- Unified project lifecycle management (**with budget planning integrated at every stage**)
- Cross-module workflow orchestration (**including budget approval gates**)
- Centralized monitoring, evaluation, **and financial tracking**
- Consolidated reporting and analytics (**programmatic + financial**)
- Task management integrated with PPAs **and budget milestones**

```
┌──────────────────────────────────────────────────────────────────┐
│                        PROJECT CENTRAL                            │
│              Integrated Project Management Layer                  │
│                                                                    │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐     │
│  │   Portfolio    │  │    Project     │  │  M&E + Budget  │     │
│  │   Dashboard    │  │   Workflow     │  │   Analytics    │     │
│  │ (Budget View)  │  │(Budget Gates)  │  │ (Cost-Benefit) │     │
│  └────────────────┘  └────────────────┘  └────────────────┘     │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐     │
│  │  Task Manager  │  │    Alerts &    │  │    Reports     │     │
│  │ (Budget Tasks) │  │  Notifications │  │(Financial+M&E) │     │
│  └────────────────┘  └────────────────┘  └────────────────┘     │
└────────────┬───────────────────────────────────────┬─────────────┘
             │                                       │
        ┌────┴────────────────────────────────────┬──┴────┬────────┐
        ▼                                         ▼       ▼        ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐
  │OBC Data  │  │  MANA    │  │Coordination│  │Monitoring│  │ Policies │  │Planning &   │
  │          │  │          │  │           │  │  (PPAs)  │  │          │  │Budgeting ⭐ │
  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └─────────────┘
                                                  │
                                                  ├─ Budget Planning
                                                  ├─ Annual Cycles
                                                  ├─ Approval Workflow
                                                  ├─ FundingFlow
                                                  ├─ Budget Ceilings
                                                  └─ Scenario Planning
```

**Key Integration Point**: Planning & Budgeting is not a separate module but the **financial dimension** that runs through:
- **Portfolio Dashboard**: Shows budget allocation, utilization rates, and spending by sector/source
- **Project Workflow**: Budget planning is Stage 4, Approval is Stage 5 (with multi-stage budget approval)
- **M&E Analytics**: Cost-effectiveness, cost per beneficiary, budget vs. actual variance
- **Alerts**: Budget ceiling warnings, approval delays, disbursement tracking
- **Reports**: All reports include financial data alongside programmatic outcomes

---

### Feature 1: Portfolio Dashboard

**Purpose**: Provide a unified, real-time view of all OOBC projects (MOA PPAs, OOBC PPAs, OBC requests)

#### Components

**1. Executive Summary Cards**:
```
┌─────────────────────────────────────────────────────────────────┐
│  Total Budget         Active Projects      High-Priority Needs  │
│  ₱ 245M               48 (86% on track)    12 unfunded          │
│                                                                  │
│  OBC Beneficiaries    MAOs Engaged         Policies Implemented │
│  45,230 people        15 / 18 MAOs         6 / 10 policies      │
└─────────────────────────────────────────────────────────────────┘
```

**2. Project Pipeline View**:
```
┌─────────────────────────────────────────────────────────────────┐
│                        PROJECT PIPELINE                          │
│                                                                  │
│  NEEDS → PLANNING → APPROVED → IMPLEMENTATION → COMPLETED       │
│   [25]  →  [18]   →   [32]   →      [48]      →    [27]        │
│                                                                  │
│  Click any stage to drill down...                                │
└─────────────────────────────────────────────────────────────────┘
```

**3. Budget Utilization**:
- By sector (pie chart)
- By funding source (bar chart)
- By region (map visualization)
- Quarterly trend (line chart)

**4. Strategic Goal Progress**:
- List of strategic goals with progress bars
- PPAs contributing to each goal
- On-track / at-risk indicators

**5. Alerts & Actions Required**:
```
⚠️  12 high-priority needs remain unfunded
⚠️  3 PPAs have missed milestone dates
⚠️  5 MAOs have not submitted Q2 reports
✅  Q3 Planning Cycle: 85% complete
```

#### Technical Implementation

**View**: `src/common/views/portfolio_dashboard.py`

```python
@login_required
def portfolio_dashboard_view(request):
    """
    Integrated portfolio dashboard showing project lifecycle.
    """
    # Aggregate data from all modules
    data = {
        # Summary metrics
        'total_budget': MonitoringEntry.objects.aggregate(Sum('budget_allocation'))['budget_allocation__sum'],
        'active_projects': MonitoringEntry.objects.filter(status='ongoing').count(),
        'unfunded_needs': Need.objects.filter(linked_ppa__isnull=True, priority_score__gte=4.0).count(),
        'total_beneficiaries': sum_beneficiaries_from_ppas(),
        'mao_engagement_rate': calculate_mao_participation(),
        'policy_implementation_rate': calculate_policy_completion(),

        # Pipeline data
        'needs_identified': Need.objects.filter(status='identified').count(),
        'needs_validated': Need.objects.filter(status='validated').count(),
        'ppas_planning': MonitoringEntry.objects.filter(status='planning').count(),
        'ppas_ongoing': MonitoringEntry.objects.filter(status='ongoing').count(),
        'ppas_completed': MonitoringEntry.objects.filter(status='completed').count(),

        # Budget breakdown
        'budget_by_sector': get_budget_by_sector(),
        'budget_by_funding_source': get_budget_by_funding_source(),
        'budget_by_region': get_budget_by_region(),
        'budget_trend': get_quarterly_budget_trend(),

        # Strategic goals
        'strategic_goals': StrategicGoal.objects.filter(status='active').annotate(
            ppa_count=Count('linked_ppas'),
            avg_progress=Avg('linked_ppas__progress')
        ),

        # Alerts
        'unfunded_high_priority_needs': get_unfunded_needs(priority_threshold=4.0),
        'overdue_ppas': get_overdue_ppas(),
        'pending_mao_reports': get_pending_quarterly_reports(),
    }

    return render(request, 'project_central/portfolio_dashboard.html', data)
```

---

### Feature 2: Project Lifecycle Workflow

**Purpose**: Guide users through the complete project lifecycle from need identification to completion

#### Workflow Stages

```
┌──────────────────────────────────────────────────────────────────┐
│                    PROJECT LIFECYCLE WORKFLOW                     │
└──────────────────────────────────────────────────────────────────┘

1. NEED IDENTIFICATION
   ↓ Community submits need OR Assessment identifies need
   ↓ MANA validates and prioritizes need
   ↓ **Budget: Preliminary cost estimation** (Need.estimated_cost)

2. POLICY LINKAGE (Optional)
   ↓ Check if need addresses existing policy recommendation
   ↓ If yes: link Need → PolicyRecommendation
   ↓ **Budget: Check policy budget implications**

3. MAO COORDINATION
   ↓ OOBC forwards need to appropriate MAO
   ↓ MAO reviews and commits to address need
   ↓ **Budget: MAO confirms funding availability or seeks sources**

4. BUDGET PLANNING ⭐ **CRITICAL FINANCIAL STAGE**
   ↓ MAO creates PPA (MonitoringEntry) with budget details
   ↓ Link PPA → Need (needs_addressed M2M)
   ↓ Link PPA → Policy (implementing_policies M2M)
   ↓ **Set budget allocation, funding source (GAA/Block Grant/LGU/Donor)**
   ↓ **Set appropriation class (PS/MOOE/CO)**
   ↓ **Calculate cost per beneficiary, set OBC allocation**
   ↓ **Tag compliance flags (GAD, CCET, IP, Peace, SDG)**
   ↓ **Assign to Annual Planning Cycle (fiscal year)**
   ↓ **Check against budget ceilings (sector/funding source)**
   ↓ PPA approval_status: 'draft'

5. APPROVAL ⭐ **5-STAGE BUDGET APPROVAL WORKFLOW**
   ↓ Stage 1: Technical Review (OOBC Staff validates program design)
   ↓ Stage 2: Budget Review (Finance Officer validates cost estimates)
   ↓ Stage 3: Stakeholder Consultation (if required - community/MAO feedback)
   ↓ Stage 4: Executive Approval (Chief Minister's Office final sign-off)
   ↓ Stage 5: Enactment (PPA officially included in budget document)
   ↓ **Each stage creates automated tasks and notifications**
   ↓ **Budget ceiling enforcement: reject if exceeds sector/source ceiling**
   ↓ PPA approval_status: 'draft' → 'technical_review' → 'budget_review' → 'executive_approval' → 'approved' → 'enacted'

6. IMPLEMENTATION
   ↓ PPA status: planning → ongoing
   ↓ **Budget status: Allocation → Obligation (FundingFlow created)**
   ↓ Regular monitoring updates (progress, accomplishments, challenges)
   ↓ **Financial tracking: Record disbursements (FundingFlow)**
   ↓ Task management (staff assignments with budget-related tasks)
   ↓ **Monitor budget vs. actual spending**

7. MONITORING & EVALUATION
   ↓ Progress tracking (0-100%)
   ↓ Outcome framework updates (outputs, outcomes, impacts)
   ↓ Accomplishments and challenges documented
   ↓ **Cost-effectiveness calculated (cost_per_beneficiary, rating)**
   ↓ **Budget utilization tracking (obligation rate, disbursement rate)**
   ↓ **Variance analysis (budget vs. actual, reasons for over/under spending)**

8. COMPLETION & FINANCIAL CLOSEOUT
   ↓ PPA status: completed
   ↓ Need status: completed
   ↓ **Final financial reconciliation**
   ↓ **Budget savings/overruns documented**
   ↓ Final evaluation and reporting (programmatic + financial)
   ↓ Lessons learned captured (including budget/cost lessons)
   ↓ **Update cost-effectiveness database for future planning**
```

#### Technical Implementation

**Model**: `src/project_central/models.py`

```python
class ProjectWorkflow(models.Model):
    """
    Tracks project workflow stages and orchestrates cross-module processes.

    This model doesn't replace MonitoringEntry but adds workflow management.
    """

    WORKFLOW_STAGES = [
        ('need_identification', 'Need Identification'),
        ('need_validation', 'Need Validation'),
        ('policy_linkage', 'Policy Linkage'),
        ('mao_coordination', 'MAO Coordination'),
        ('budget_planning', 'Budget Planning'),
        ('approval', 'Approval Process'),
        ('implementation', 'Implementation'),
        ('monitoring', 'Monitoring & Evaluation'),
        ('completion', 'Completion'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Core Relationships
    primary_need = models.OneToOneField(
        'mana.Need',
        on_delete=models.CASCADE,
        related_name='project_workflow',
        help_text="Primary need driving this project"
    )

    ppa = models.OneToOneField(
        'monitoring.MonitoringEntry',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='project_workflow',
        help_text="PPA implementing this project"
    )

    # Workflow State
    current_stage = models.CharField(
        max_length=30,
        choices=WORKFLOW_STAGES,
        default='need_identification',
    )

    stage_history = models.JSONField(
        default=list,
        help_text="History of stage transitions with timestamps"
    )

    # Participants
    project_lead = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='led_projects',
        help_text="OOBC staff leading this project"
    )

    mao_focal_person = models.ForeignKey(
        'coordination.MAOFocalPerson',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coordinated_projects',
        help_text="MAO focal person coordinating"
    )

    # Timeline
    initiated_date = models.DateField(help_text="Date project workflow started")
    target_completion_date = models.DateField(null=True, blank=True)
    actual_completion_date = models.DateField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def advance_stage(self, new_stage, user):
        """Advance workflow to next stage with validation."""
        self.stage_history.append({
            'stage': new_stage,
            'timestamp': timezone.now().isoformat(),
            'user': user.username,
        })
        self.current_stage = new_stage
        self.save()

        # Trigger stage-specific actions
        self._trigger_stage_actions(new_stage)

    def _trigger_stage_actions(self, stage):
        """Execute automated actions for stage transitions."""
        if stage == 'mao_coordination':
            # Send notification to MAO focal person
            send_mao_notification(self)
        elif stage == 'approval':
            # Create approval workflow tasks
            create_approval_tasks(self)
        elif stage == 'implementation':
            # Update PPA status
            if self.ppa:
                self.ppa.status = 'ongoing'
                self.ppa.save()
```

**View**: `src/project_central/views.py`

```python
@login_required
def project_workflow_detail(request, workflow_id):
    """
    Show detailed project workflow with stage-by-stage progress.
    """
    workflow = get_object_or_404(ProjectWorkflow, id=workflow_id)

    context = {
        'workflow': workflow,
        'need': workflow.primary_need,
        'ppa': workflow.ppa,
        'community': workflow.primary_need.community,
        'related_policies': workflow.ppa.implementing_policies.all() if workflow.ppa else [],
        'tasks': WorkflowTask.objects.filter(workflow=workflow),
        'timeline': workflow.stage_history,
        'next_actions': get_next_actions_for_stage(workflow.current_stage),
    }

    return render(request, 'project_central/workflow_detail.html', context)


@login_required
@require_POST
def advance_project_stage(request, workflow_id):
    """
    Advance project to next workflow stage.
    """
    workflow = get_object_or_404(ProjectWorkflow, id=workflow_id)
    new_stage = request.POST.get('new_stage')

    # Validate stage transition
    if not can_advance_to_stage(workflow, new_stage):
        messages.error(request, "Cannot advance to this stage. Prerequisites not met.")
        return redirect('project_workflow_detail', workflow_id=workflow_id)

    # Advance stage
    workflow.advance_stage(new_stage, request.user)

    messages.success(request, f"Project advanced to: {workflow.get_current_stage_display()}")
    return redirect('project_workflow_detail', workflow_id=workflow_id)
```

---

### Feature 3: Integrated Task Management

**Purpose**: Connect task management to project workflow and PPAs

#### Architecture

**Extend Existing StaffTask Model**:

```python
# In src/common/models.py - enhance existing StaffTask model

class StaffTask(models.Model):
    # ... existing fields ...

    # NEW: Project Integration
    linked_workflow = models.ForeignKey(
        'project_central.ProjectWorkflow',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='tasks',
        help_text="Link task to project workflow"
    )

    linked_ppa = models.ForeignKey(
        'monitoring.MonitoringEntry',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='tasks',
        help_text="Link task to PPA"
    )

    workflow_stage = models.CharField(
        max_length=30,
        blank=True,
        help_text="Workflow stage this task belongs to"
    )

    auto_generated = models.BooleanField(
        default=False,
        help_text="Whether this task was automatically generated by workflow"
    )
```

**Automated Task Generation**:

When project workflow advances, automatically create tasks:

```python
def create_approval_tasks(workflow):
    """Auto-create tasks for approval stage."""

    # Task 1: Prepare budget justification
    StaffTask.objects.create(
        title=f"Prepare budget justification for {workflow.primary_need.title}",
        description="Compile evidence from MANA assessment and community needs",
        assigned_to=workflow.project_lead,
        due_date=timezone.now() + timedelta(days=7),
        priority='high',
        linked_workflow=workflow,
        linked_ppa=workflow.ppa,
        workflow_stage='approval',
        auto_generated=True,
    )

    # Task 2: Stakeholder consultation
    if requires_stakeholder_consultation(workflow):
        StaffTask.objects.create(
            title=f"Schedule stakeholder consultation for {workflow.primary_need.title}",
            description="Engage community and MAO for budget approval consultation",
            assigned_to=workflow.project_lead,
            due_date=timezone.now() + timedelta(days=14),
            priority='high',
            linked_workflow=workflow,
            workflow_stage='approval',
            auto_generated=True,
        )
```

#### Task Dashboard Integration

**View**: Enhanced staff task view with project context

```python
@login_required
def my_tasks_with_projects(request):
    """
    Show user's tasks grouped by project workflow.
    """
    user_tasks = StaffTask.objects.filter(
        assigned_to=request.user,
        status__in=['todo', 'in_progress']
    ).select_related(
        'linked_workflow',
        'linked_ppa',
        'linked_event'
    )

    # Group by project
    project_tasks = {}
    standalone_tasks = []

    for task in user_tasks:
        if task.linked_workflow:
            workflow_id = str(task.linked_workflow.id)
            if workflow_id not in project_tasks:
                project_tasks[workflow_id] = {
                    'workflow': task.linked_workflow,
                    'tasks': []
                }
            project_tasks[workflow_id]['tasks'].append(task)
        else:
            standalone_tasks.append(task)

    context = {
        'project_tasks': project_tasks.values(),
        'standalone_tasks': standalone_tasks,
        'overdue_tasks': user_tasks.filter(due_date__lt=timezone.now().date()),
    }

    return render(request, 'project_central/my_tasks.html', context)
```

---

### Feature 4: M&E Analytics Dashboard

**Purpose**: Centralized monitoring, evaluation, and reporting hub

#### Components

**1. Performance Scorecard**:
```
┌─────────────────────────────────────────────────────────────────┐
│                      PERFORMANCE SCORECARD                       │
│                                                                  │
│  PPAs On Track: 42 / 48 (88%)    ████████████████░░  88%        │
│  Budget Utilization: 65%          ████████████████░░  65%        │
│  Outcome Achievement: 78%         ████████████████░░  78%        │
│  Cost Effectiveness: High         ✓ Target Met                   │
└─────────────────────────────────────────────────────────────────┘
```

**2. Needs-to-Results Chain**:
- How many needs identified?
- How many needs funded?
- How many PPAs in progress?
- How many PPAs showing impact?

```
Needs Identified (180) → Funded (120) → In Progress (48) → Completed (27) → Impact Achieved (22)
     100%                  67%              40%               22%                18%
```

**3. Sector Performance Comparison**:
- Table/chart comparing sectors
- Columns: Budget, PPAs, Beneficiaries, Outcome Achievement %, Cost per Beneficiary

**4. Geographic Distribution**:
- Map showing PPAs by region/province
- Heat map by budget allocation
- OBC beneficiaries by location

**5. Policy Impact Tracker**:
- List of 10 OOBC policy recommendations
- PPAs implementing each policy
- Budget allocated per policy
- Implementation progress
- Beneficiaries reached

**6. MAO Participation Report**:
- MAO engagement rates
- Quarterly report submission compliance
- Budget allocated per MAO
- PPAs implemented per MAO

#### Technical Implementation

**View**: `src/project_central/views.py`

```python
@login_required
def me_analytics_dashboard(request):
    """
    Centralized M&E analytics dashboard.
    """
    fiscal_year = request.GET.get('fiscal_year', timezone.now().year)

    # Performance metrics
    ppas_qs = MonitoringEntry.objects.filter(fiscal_year=fiscal_year)

    performance = {
        'total_ppas': ppas_qs.count(),
        'on_track_ppas': ppas_qs.filter(progress__gte=70).count(),
        'budget_allocated': ppas_qs.aggregate(Sum('budget_allocation'))['budget_allocation__sum'] or 0,
        'budget_obligated': calculate_total_obligations(ppas_qs),
        'outcome_achievement_avg': calculate_outcome_achievement(ppas_qs),
        'cost_effectiveness_distribution': get_cost_effectiveness_distribution(ppas_qs),
    }

    # Needs-to-results chain
    needs_qs = Need.objects.all()
    results_chain = {
        'needs_identified': needs_qs.count(),
        'needs_funded': needs_qs.filter(linked_ppa__isnull=False).count(),
        'ppas_in_progress': ppas_qs.filter(status='ongoing').count(),
        'ppas_completed': ppas_qs.filter(status='completed').count(),
        'impact_achieved': count_ppas_with_positive_outcomes(ppas_qs),
    }

    # Sector performance
    sector_performance = ppas_qs.values('sector').annotate(
        total_budget=Sum('budget_allocation'),
        ppa_count=Count('id'),
        avg_progress=Avg('progress'),
        total_beneficiaries=Sum('obc_slots'),
        avg_cost_per_beneficiary=Avg('cost_per_beneficiary'),
    ).order_by('-total_budget')

    # Geographic distribution
    geographic_data = get_ppa_geographic_distribution(ppas_qs)

    # Policy impact
    policy_impact = PolicyRecommendation.objects.annotate(
        ppa_count=Count('implementing_ppas'),
        total_budget=Sum('implementing_ppas__budget_allocation'),
        avg_progress=Avg('implementing_ppas__progress'),
        beneficiary_count=Sum('implementing_ppas__obc_slots'),
    )

    # MAO participation
    mao_participation = get_mao_participation_metrics(fiscal_year)

    context = {
        'fiscal_year': fiscal_year,
        'performance': performance,
        'results_chain': results_chain,
        'sector_performance': sector_performance,
        'geographic_data': geographic_data,
        'policy_impact': policy_impact,
        'mao_participation': mao_participation,
    }

    return render(request, 'project_central/me_analytics.html', context)
```

---

### Feature 5: Automated Alerts & Notifications

**Purpose**: Proactive alerts for critical events requiring attention

#### Alert Types

**1. Unfunded High-Priority Needs**:
```
⚠️  12 high-priority needs remain unfunded (priority score ≥ 4.0)
    → View Needs Gap Analysis
    → Start Budget Planning
```

**2. Overdue PPAs**:
```
⚠️  3 PPAs have missed their milestone dates
    → Project A: 5 days overdue
    → Project B: 12 days overdue
    → Project C: 20 days overdue
```

**3. Quarterly Report Pending**:
```
⚠️  5 MAOs have not submitted Q2 quarterly reports
    → DepEd: Report due 5 days ago
    → DOH: Report due 3 days ago
    → ...
```

**4. Budget Ceiling Alert**:
```
⚠️  Education sector approaching budget ceiling (92% utilized)
    → Current allocation: ₱92M / ₱100M ceiling
    → Remaining: ₱8M
```

**5. Policy Implementation Lagging**:
```
⚠️  Policy #3 implementation behind schedule
    → Target: 50% by Q2 | Actual: 28%
    → 2 PPAs delayed
```

#### Technical Implementation

**Alert Generation Service**: `src/project_central/services/alert_service.py`

```python
class AlertService:
    """Service for generating and managing project alerts."""

    @staticmethod
    def generate_daily_alerts():
        """Generate all alerts for the day (run via Celery task)."""
        alerts = []

        # 1. Unfunded High-Priority Needs
        unfunded_needs = Need.objects.filter(
            linked_ppa__isnull=True,
            priority_score__gte=4.0,
            status__in=['validated', 'prioritized']
        )
        if unfunded_needs.count() > 0:
            alerts.append(Alert.objects.create(
                alert_type='unfunded_needs',
                severity='high',
                title=f"{unfunded_needs.count()} high-priority needs unfunded",
                description="These needs have been validated but no PPAs have been created to address them.",
                action_url=reverse('needs_gap_analysis'),
                related_needs=list(unfunded_needs.values_list('id', flat=True)),
            ))

        # 2. Overdue PPAs
        overdue_ppas = MonitoringEntry.objects.filter(
            status='ongoing',
            next_milestone_date__lt=timezone.now().date()
        )
        for ppa in overdue_ppas:
            days_overdue = (timezone.now().date() - ppa.next_milestone_date).days
            alerts.append(Alert.objects.create(
                alert_type='overdue_ppa',
                severity='medium' if days_overdue < 10 else 'high',
                title=f"PPA overdue: {ppa.title}",
                description=f"{days_overdue} days past milestone date",
                action_url=reverse('monitoring_entry_detail', args=[ppa.id]),
                related_ppa_id=ppa.id,
            ))

        # 3. Pending Quarterly Reports
        current_quarter = get_current_quarter()
        mao_report_deadline = get_mao_report_deadline(current_quarter)

        if timezone.now().date() > mao_report_deadline:
            maos_with_reports = MAOQuarterlyReport.objects.filter(
                meeting__quarter=current_quarter,
                meeting__fiscal_year=timezone.now().year
            ).values_list('mao_id', flat=True)

            maos_without_reports = Organization.objects.filter(
                organization_type='bmoa',
                is_active=True
            ).exclude(id__in=maos_with_reports)

            if maos_without_reports.exists():
                alerts.append(Alert.objects.create(
                    alert_type='pending_mao_report',
                    severity='medium',
                    title=f"{maos_without_reports.count()} MAOs have not submitted {current_quarter} reports",
                    description="Quarterly reports are overdue",
                    action_url=reverse('quarterly_reports_pending'),
                ))

        # 4. Budget Ceiling Alerts
        for sector in MonitoringEntry.SECTOR_CHOICES:
            sector_code = sector[0]
            ceiling_alert = check_budget_ceiling(sector_code)
            if ceiling_alert:
                alerts.append(ceiling_alert)

        # 5. Policy Implementation Lagging
        for policy in PolicyRecommendation.objects.filter(status='in_implementation'):
            if is_policy_lagging(policy):
                alerts.append(Alert.objects.create(
                    alert_type='policy_lagging',
                    severity='medium',
                    title=f"Policy implementation behind schedule: {policy.title}",
                    description=get_policy_lag_description(policy),
                    action_url=reverse('policy_detail', args=[policy.id]),
                ))

        return alerts

    @staticmethod
    def get_user_alerts(user):
        """Get alerts relevant to a specific user."""
        # Return alerts based on user role and responsibilities
        pass


# Celery task for daily alert generation
@shared_task
def generate_daily_alerts_task():
    """Daily task to generate alerts."""
    AlertService.generate_daily_alerts()
```

**Alert Model**: `src/project_central/models.py`

```python
class Alert(models.Model):
    """System-generated alerts for project management."""

    ALERT_TYPES = [
        ('unfunded_needs', 'Unfunded High-Priority Needs'),
        ('overdue_ppa', 'Overdue PPA'),
        ('pending_mao_report', 'Pending MAO Report'),
        ('budget_ceiling', 'Budget Ceiling Alert'),
        ('policy_lagging', 'Policy Implementation Lagging'),
    ]

    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    title = models.CharField(max_length=255)
    description = models.TextField()
    action_url = models.CharField(max_length=500, help_text="URL to take action")

    # Optional relationships
    related_ppa = models.ForeignKey(
        'monitoring.MonitoringEntry',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='alerts'
    )

    related_needs = models.ManyToManyField('mana.Need', blank=True)
    related_policy = models.ForeignKey(
        'policy_tracking.PolicyRecommendation',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='alerts'
    )

    # Status
    is_active = models.BooleanField(default=True)
    acknowledged_by = models.ManyToManyField(User, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['alert_type', 'is_active']),
            models.Index(fields=['severity', 'is_active']),
        ]
```

---

### Feature 6: Planning & Budgeting Management

**Purpose**: Centralized budget planning, allocation, and approval workflow for PPAs

#### Components

**1. Budget Planning Dashboard**:
```
┌─────────────────────────────────────────────────────────────────┐
│                      BUDGET PLANNING FY 2026                     │
│                                                                  │
│  Total Budget Envelope: ₱500M    Allocated: ₱420M (84%)         │
│  Remaining: ₱80M                 PPAs: 48                        │
│                                                                  │
│  By Sector:                      By Funding Source:             │
│  • Education:      ₱150M (35%)   • GAA:         ₱300M (71%)     │
│  • Livelihood:     ₱120M (29%)   • Block Grant:  ₱100M (24%)    │
│  • Infrastructure: ₱80M  (19%)   • LGU:          ₱20M  (5%)     │
│  • Health:         ₱70M  (17%)                                   │
│                                                                  │
│  Budget Ceiling Alerts:                                          │
│  ⚠️  Education sector approaching ceiling (92% utilized)         │
└─────────────────────────────────────────────────────────────────┘
```

**2. Annual Planning Cycle Workflow**:
```
Planning Cycle FY 2026
───────────────────────
Timeline:
✅ Planning Start:        Jan 15, 2025
✅ Budget Submission Due: Mar 31, 2025
⏳ Budget Approval:        Jun 30, 2025
⏸  Execution Start:       Jan 1, 2026

Current Phase: Budget Approval (65% complete)

Tasks Remaining:
- Review 5 pending PPA proposals
- Conduct 2 sector allocation meetings
- Finalize budget document
```

**3. PPA Budget Builder Interface**:
- **Needs-First Approach**: Start with prioritized Need records
- **Policy Alignment**: Select which policies PPA implements
- **Budget Calculator**: Auto-calculate cost per beneficiary
- **Funding Source Allocation**: Split budget across multiple sources
- **Compliance Tagging**: GAD, CCET, IP, SDG flags
- **Strategic Goal Mapping**: Link to strategic goals

**4. Budget Approval Workflow**:
```
PPA Approval Pipeline
─────────────────────
Draft (12) → Under Review (8) → Approved (3) → Enacted (0)

Approval Stages:
1. Technical Review (OOBC Staff)
2. Budget Review (Finance Officer)
3. Stakeholder Consultation (if required)
4. Executive Approval (Chief Minister's Office)
5. Enactment (Official budget document)
```

**5. Participatory Budgeting Interface**:
```
Community Participatory Budgeting Session
Region IX - Q2 2025 Budget Allocation: ₱20M

Top 10 Unfunded High-Priority Needs (Community Voting):
┌────────────────────────────────────────┬───────┬──────────┐
│ Need Title                             │ Votes │ Est. Cost│
├────────────────────────────────────────┼───────┼──────────┤
│ Water system for Barangay Centro       │  45   │ ₱3.5M    │
│ Scholarship program for 50 students    │  38   │ ₱2.0M    │
│ Livelihood training for fisherfolk     │  35   │ ₱1.8M    │
│ Health center construction              │  32   │ ₱5.0M    │
│ Road improvement (3km)                  │  28   │ ₱6.0M    │
└────────────────────────────────────────┴───────┴──────────┘

Budget Allocation Tool:
→ Select needs to fund (total ≤ ₱20M)
→ Adjust allocations
→ Submit for approval
```

**6. Budget Scenario Planner**:
```
Scenario Comparison FY 2026

┌─────────────────────┬──────────┬──────────┬──────────┐
│ Sector              │Scenario A│Scenario B│Scenario C│
├─────────────────────┼──────────┼──────────┼──────────┤
│ Education           │  ₱150M   │  ₱180M   │  ₱120M   │
│ Livelihood          │  ₱120M   │  ₱100M   │  ₱140M   │
│ Infrastructure      │  ₱80M    │  ₱70M    │  ₱90M    │
│ Health              │  ₱70M    │  ₱80M    │  ₱60M    │
│ Governance          │  ₱40M    │  ₱30M    │  ₱50M    │
│ Cultural            │  ₱40M    │  ₱40M    │  ₱40M    │
├─────────────────────┼──────────┼──────────┼──────────┤
│ TOTAL               │  ₱500M   │  ₱500M   │  ₱500M   │
│ Needs Funded        │   65%    │   70%    │   60%    │
│ Beneficiaries       │  42,000  │  45,000  │  38,000  │
└─────────────────────┴──────────┴──────────┴──────────┘

Select Scenario A ○  Scenario B ●  Scenario C ○
```

**7. Budget Ceiling Management**:
- **Per-Sector Ceilings**: Set maximum allocation per sector
- **Per-Funding-Source Ceilings**: Manage GAA, Block Grant, LGU ceilings separately
- **Real-time Alerts**: Warn when approaching 90% of ceiling
- **Automatic Enforcement**: Prevent over-allocation

**8. Budget-to-Actual Variance Analysis**:
```
Variance Analysis FY 2025 (Actual vs. Budget)

Education Sector:
Budget:      ₱150M  ─────────────────────────
Obligation:  ₱142M  ───────────────────────── 95%
Disbursement:₱128M  ──────────────────────  85%
Variance:    -₱22M  (Under-spent by 15%)

Reasons for Variance:
• 3 PPAs delayed due to procurement issues
• 1 PPA cancelled due to LGU partnership withdrawal
• 2 PPAs re-scoped with lower costs
```

#### Technical Implementation

**Model Enhancements**: `src/monitoring/models.py`

```python
# Extend MonitoringEntry
class MonitoringEntry(models.Model):
    # ... existing fields ...

    # BUDGET APPROVAL WORKFLOW
    APPROVAL_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('technical_review', 'Technical Review'),
        ('budget_review', 'Budget Review'),
        ('stakeholder_consultation', 'Stakeholder Consultation'),
        ('executive_approval', 'Executive Approval'),
        ('approved', 'Approved'),
        ('enacted', 'Enacted'),
        ('rejected', 'Rejected'),
    ]

    approval_status = models.CharField(
        max_length=30,
        choices=APPROVAL_STATUS_CHOICES,
        default='draft',
        help_text="Budget approval workflow status"
    )

    approval_history = models.JSONField(
        default=list,
        help_text="History of approval stages with timestamps and reviewers"
    )

    reviewed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reviewed_ppas',
        help_text="Technical reviewer"
    )

    budget_approved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='budget_approved_ppas',
        help_text="Budget/finance officer who approved"
    )

    executive_approved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='executive_approved_ppas',
        help_text="Executive approver (e.g., Chief Minister's Office)"
    )

    enacted_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when PPA was enacted into official budget"
    )

    @property
    def approval_progress_percentage(self):
        """Calculate approval workflow progress."""
        stages = ['draft', 'technical_review', 'budget_review', 'executive_approval', 'approved', 'enacted']
        if self.approval_status == 'rejected':
            return 0
        try:
            current_index = stages.index(self.approval_status)
            return int((current_index + 1) / len(stages) * 100)
        except ValueError:
            return 0
```

**New Models**: `src/monitoring/budget_models.py`

```python
class BudgetCeiling(models.Model):
    """
    Budget ceilings for scenario planning and allocation control.
    Can be set per sector, per funding source, or both.
    """

    CEILING_TYPES = [
        ('sector', 'Sector Ceiling'),
        ('funding_source', 'Funding Source Ceiling'),
        ('combined', 'Sector + Funding Source Ceiling'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    fiscal_year = models.PositiveIntegerField(
        validators=[MinValueValidator(2020), MaxValueValidator(2050)]
    )

    ceiling_type = models.CharField(max_length=20, choices=CEILING_TYPES)

    # Optional sector (for sector-specific ceilings)
    sector = models.CharField(
        max_length=32,
        choices=MonitoringEntry.SECTOR_CHOICES,
        blank=True,
        help_text="Sector this ceiling applies to (if sector-specific)"
    )

    # Optional funding source (for source-specific ceilings)
    funding_source = models.CharField(
        max_length=32,
        choices=MonitoringEntry.FUNDING_SOURCE_CHOICES,
        blank=True,
        help_text="Funding source this ceiling applies to (if source-specific)"
    )

    ceiling_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Maximum budget amount for this ceiling"
    )

    allocated_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Currently allocated amount"
    )

    # Threshold for alerts
    alert_threshold = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.90'),
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Threshold percentage for alerts (e.g., 0.90 = 90%)"
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['fiscal_year', 'sector', 'funding_source']
        ordering = ['fiscal_year', 'sector', 'funding_source']

    def __str__(self):
        parts = [f"FY {self.fiscal_year}"]
        if self.sector:
            parts.append(f"{self.get_sector_display()}")
        if self.funding_source:
            parts.append(f"{self.get_funding_source_display()}")
        return " - ".join(parts)

    @property
    def remaining_ceiling(self):
        """Calculate remaining budget ceiling."""
        return self.ceiling_amount - self.allocated_amount

    @property
    def utilization_rate(self):
        """Calculate ceiling utilization rate (0-100%)."""
        if self.ceiling_amount > 0:
            return float(self.allocated_amount / self.ceiling_amount * 100)
        return 0.0

    @property
    def is_exceeded(self):
        """Check if ceiling is exceeded."""
        return self.allocated_amount > self.ceiling_amount

    @property
    def is_near_ceiling(self):
        """Check if allocation is near ceiling (above alert threshold)."""
        return self.utilization_rate >= float(self.alert_threshold * 100)


class BudgetScenario(models.Model):
    """
    Budget scenarios for planning and comparison.
    Allows creating multiple allocation scenarios before finalizing.
    """

    ALLOCATION_STRATEGIES = [
        ('needs_based', 'Needs-Based (Prioritize high-priority needs)'),
        ('equity_based', 'Equity-Based (Equal distribution per region)'),
        ('performance_based', 'Performance-Based (Reward high-performing sectors)'),
        ('policy_based', 'Policy-Based (Align with policy recommendations)'),
        ('participatory', 'Participatory (Based on community voting)'),
        ('custom', 'Custom Allocation'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    fiscal_year = models.PositiveIntegerField(
        validators=[MinValueValidator(2020), MaxValueValidator(2050)]
    )

    scenario_name = models.CharField(
        max_length=255,
        help_text="Name of the budget scenario (e.g., 'Conservative', 'Aggressive Growth')"
    )

    description = models.TextField(help_text="Description of scenario assumptions")

    allocation_strategy = models.CharField(
        max_length=20,
        choices=ALLOCATION_STRATEGIES,
        help_text="Strategy used for allocation"
    )

    total_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Total budget envelope for this scenario"
    )

    # Sector allocations (JSON)
    sector_allocations = models.JSONField(
        default=dict,
        help_text="Budget allocation per sector {sector: amount}"
    )

    # Regional allocations (JSON)
    regional_allocations = models.JSONField(
        default=dict,
        help_text="Budget allocation per region {region_id: amount}"
    )

    # Projected outcomes
    projected_beneficiaries = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Estimated total beneficiaries"
    )

    projected_needs_funded = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Estimated number of needs that will be funded"
    )

    projected_funding_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Projected percentage of needs funded"
    )

    # Status
    is_approved = models.BooleanField(
        default=False,
        help_text="Whether this scenario was approved and enacted"
    )

    approved_date = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='approved_scenarios'
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_scenarios'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fiscal_year', '-created_at']
        unique_together = ['fiscal_year', 'scenario_name']

    def __str__(self):
        return f"{self.scenario_name} - FY {self.fiscal_year}"

    @property
    def total_sector_allocations(self):
        """Sum of all sector allocations."""
        return sum(Decimal(str(amt)) for amt in self.sector_allocations.values())

    @property
    def budget_allocation_rate(self):
        """Percentage of budget allocated to sectors."""
        total_allocated = self.total_sector_allocations
        if self.total_budget > 0:
            return float(total_allocated / self.total_budget * 100)
        return 0.0
```

**Views**: `src/project_central/views.py`

```python
@login_required
def budget_planning_dashboard(request, fiscal_year=None):
    """
    Centralized budget planning dashboard.
    """
    if not fiscal_year:
        fiscal_year = timezone.now().year + 1  # Default to next year

    # Get annual planning cycle
    try:
        cycle = AnnualPlanningCycle.objects.get(fiscal_year=fiscal_year)
    except AnnualPlanningCycle.DoesNotExist:
        cycle = None

    # Budget metrics
    ppas_qs = MonitoringEntry.objects.filter(fiscal_year=fiscal_year)

    budget_metrics = {
        'total_envelope': cycle.total_budget_envelope if cycle else 0,
        'allocated': ppas_qs.aggregate(Sum('budget_allocation'))['budget_allocation__sum'] or 0,
        'ppa_count': ppas_qs.count(),
        'utilization_rate': 0,
    }
    if budget_metrics['total_envelope'] > 0:
        budget_metrics['utilization_rate'] = (
            budget_metrics['allocated'] / budget_metrics['total_envelope'] * 100
        )

    # By sector
    by_sector = ppas_qs.values('sector').annotate(
        total=Sum('budget_allocation'),
        count=Count('id')
    ).order_by('-total')

    # By funding source
    by_funding_source = ppas_qs.values('funding_source').annotate(
        total=Sum('budget_allocation'),
        count=Count('id')
    ).order_by('-total')

    # Budget ceilings
    ceilings = BudgetCeiling.objects.filter(fiscal_year=fiscal_year)
    ceiling_alerts = []
    for ceiling in ceilings:
        # Recalculate allocated amount
        if ceiling.sector and ceiling.funding_source:
            allocated = ppas_qs.filter(
                sector=ceiling.sector,
                funding_source=ceiling.funding_source
            ).aggregate(Sum('budget_allocation'))['budget_allocation__sum'] or 0
        elif ceiling.sector:
            allocated = ppas_qs.filter(
                sector=ceiling.sector
            ).aggregate(Sum('budget_allocation'))['budget_allocation__sum'] or 0
        elif ceiling.funding_source:
            allocated = ppas_qs.filter(
                funding_source=ceiling.funding_source
            ).aggregate(Sum('budget_allocation'))['budget_allocation__sum'] or 0
        else:
            allocated = 0

        ceiling.allocated_amount = allocated
        ceiling.save()

        if ceiling.is_near_ceiling or ceiling.is_exceeded:
            ceiling_alerts.append(ceiling)

    # Budget scenarios
    scenarios = BudgetScenario.objects.filter(fiscal_year=fiscal_year)

    context = {
        'fiscal_year': fiscal_year,
        'cycle': cycle,
        'budget_metrics': budget_metrics,
        'by_sector': by_sector,
        'by_funding_source': by_funding_source,
        'ceilings': ceilings,
        'ceiling_alerts': ceiling_alerts,
        'scenarios': scenarios,
    }

    return render(request, 'project_central/budget_planning_dashboard.html', context)


@login_required
@require_POST
def create_budget_scenario(request, fiscal_year):
    """Create a new budget scenario for comparison."""
    scenario = BudgetScenario.objects.create(
        fiscal_year=fiscal_year,
        scenario_name=request.POST.get('scenario_name'),
        description=request.POST.get('description'),
        allocation_strategy=request.POST.get('allocation_strategy'),
        total_budget=request.POST.get('total_budget'),
        sector_allocations=json.loads(request.POST.get('sector_allocations', '{}')),
        regional_allocations=json.loads(request.POST.get('regional_allocations', '{}')),
        created_by=request.user,
    )

    messages.success(request, f"Budget scenario '{scenario.scenario_name}' created successfully.")
    return redirect('budget_planning_dashboard', fiscal_year=fiscal_year)


@login_required
def participatory_budgeting_session(request, session_id):
    """
    Interface for participatory budgeting session.
    Community representatives vote on prioritized needs.
    """
    # Get engagement session
    session = get_object_or_404(StakeholderEngagement, id=session_id, is_participatory_budgeting=True)

    # Get unfunded high-priority needs for region
    unfunded_needs = Need.objects.filter(
        linked_ppa__isnull=True,
        status='prioritized',
        priority_score__gte=4.0,
        community__barangay__municipality__province__region=session.region
    ).annotate(
        vote_count=F('community_votes')
    ).order_by('-vote_count', '-priority_score')

    # Budget allocation available
    budget_available = session.budget_amount_to_allocate or 0

    context = {
        'session': session,
        'unfunded_needs': unfunded_needs,
        'budget_available': budget_available,
        'voting_open': session.is_voting_open,
    }

    return render(request, 'project_central/participatory_budgeting.html', context)


@login_required
@require_POST
def vote_for_need(request, need_id):
    """Cast a vote for a need during participatory budgeting."""
    need = get_object_or_404(Need, id=need_id)

    # Increment vote count
    need.community_votes = F('community_votes') + 1
    need.save()
    need.refresh_from_db()

    return JsonResponse({
        'success': True,
        'need_id': str(need.id),
        'new_vote_count': need.community_votes
    })
```

#### Integration with Project Workflow

Budget planning integrates with the project lifecycle workflow:

```python
# In ProjectWorkflow model
def _trigger_stage_actions(self, stage):
    """Execute automated actions for stage transitions."""

    # ... existing stage actions ...

    if stage == 'budget_planning':
        # Create draft MonitoringEntry with pre-filled data
        if not self.ppa:
            ppa = MonitoringEntry.objects.create(
                title=f"PPA for {self.primary_need.title}",
                category='moa_ppa' if self.mao_focal_person else 'oobc_ppa',
                summary=self.primary_need.description,
                lead_organization=self.forwarded_to_mao if self.mao_focal_person else None,
                fiscal_year=timezone.now().year + 1,
                sector=self.primary_need.category.sector,
                status='planning',
                approval_status='draft',
            )
            ppa.needs_addressed.add(self.primary_need)
            self.ppa = ppa
            self.save()

            # Create task for budget planning
            StaffTask.objects.create(
                title=f"Complete budget planning for {ppa.title}",
                description="Fill in budget details, funding sources, and cost estimates",
                assigned_to=self.project_lead,
                linked_workflow=self,
                linked_ppa=ppa,
                workflow_stage='budget_planning',
                priority='high',
                due_date=timezone.now() + timedelta(days=14),
                auto_generated=True,
            )

    elif stage == 'approval':
        # Start approval workflow
        if self.ppa:
            self.ppa.approval_status = 'technical_review'
            self.ppa.save()

            # Create approval tasks (as shown earlier)
            create_approval_tasks(self)
```

---

### Feature 7: Integrated Reporting

**Purpose**: Generate comprehensive reports spanning multiple modules

#### Report Types

**1. Project Portfolio Report**:
- Executive summary
- All active projects with status
- Budget utilization by sector
- Geographic distribution
- Key performance indicators

**2. Needs Assessment Impact Report**:
- Needs identified (from MANA)
- Needs addressed (linked to PPAs)
- Gap analysis (unfunded needs)
- Community impact metrics

**3. Policy Implementation Report**:
- Status of 10 OOBC policy recommendations
- PPAs implementing each policy
- Budget allocated per policy
- Outcomes achieved
- Beneficiaries reached

**4. MAO Coordination Report**:
- MAO participation rates
- Quarterly report compliance
- PPAs implemented per MAO
- Budget allocated per MAO
- Collaboration metrics

**5. M&E Consolidated Report**:
- Outcome achievement rates
- Cost-effectiveness analysis
- Success stories and lessons learned
- Recommendations for improvement

#### Technical Implementation

**Report Generator Service**: `src/project_central/services/report_generator.py`

```python
class ReportGenerator:
    """Service for generating integrated reports."""

    @staticmethod
    def generate_portfolio_report(fiscal_year):
        """Generate comprehensive project portfolio report."""

        report_data = {
            'title': f'Project Portfolio Report - FY {fiscal_year}',
            'generated_date': timezone.now(),
            'fiscal_year': fiscal_year,

            # Executive Summary
            'executive_summary': {
                'total_budget': get_total_budget(fiscal_year),
                'active_projects': get_active_projects_count(fiscal_year),
                'total_beneficiaries': get_total_beneficiaries(fiscal_year),
                'mao_participation': get_mao_participation_rate(fiscal_year),
                'outcome_achievement': get_avg_outcome_achievement(fiscal_year),
            },

            # Projects by Status
            'projects_by_status': get_projects_grouped_by_status(fiscal_year),

            # Budget Analysis
            'budget_by_sector': get_budget_breakdown_by_sector(fiscal_year),
            'budget_by_funding_source': get_budget_breakdown_by_funding_source(fiscal_year),
            'budget_by_region': get_budget_breakdown_by_region(fiscal_year),

            # Geographic Distribution
            'geographic_data': get_geographic_distribution(fiscal_year),

            # KPIs
            'kpis': calculate_kpis(fiscal_year),
        }

        # Generate PDF
        pdf_path = render_pdf_report('portfolio_report_template.html', report_data)
        return pdf_path

    @staticmethod
    def generate_needs_impact_report():
        """Generate needs assessment impact report."""

        needs_qs = Need.objects.all()
        ppas_qs = MonitoringEntry.objects.all()

        report_data = {
            'title': 'Needs Assessment Impact Report',
            'generated_date': timezone.now(),

            # Needs Summary
            'total_needs': needs_qs.count(),
            'needs_by_status': needs_qs.values('status').annotate(count=Count('id')),
            'needs_by_sector': needs_qs.values('category__sector').annotate(count=Count('id')),
            'needs_by_urgency': needs_qs.values('urgency_level').annotate(count=Count('id')),

            # Impact Analysis
            'needs_funded': needs_qs.filter(linked_ppa__isnull=False).count(),
            'needs_unfunded': needs_qs.filter(linked_ppa__isnull=True).count(),
            'funding_rate': calculate_funding_rate(needs_qs),

            # Gap Analysis
            'unfunded_high_priority': needs_qs.filter(
                linked_ppa__isnull=True,
                priority_score__gte=4.0
            ),
            'geographic_gaps': identify_geographic_gaps(needs_qs),
            'sector_gaps': identify_sector_gaps(needs_qs),

            # Community Impact
            'communities_served': get_communities_with_needs_addressed(needs_qs),
            'total_affected_population': needs_qs.aggregate(Sum('affected_population'))['affected_population__sum'],
            'population_served': calculate_population_served(needs_qs),
        }

        pdf_path = render_pdf_report('needs_impact_report_template.html', report_data)
        return pdf_path
```

---

## Implementation Plan

### Phase 1: Foundation 

**Goal**: Create core Project Management Portal infrastructure **with budget tracking integration**

#### Deliverables

1. **New Django App**: `src/project_central/`
   - Create app structure
   - Configure URLs
   - Set up base templates

2. **Data Models**:
   - `ProjectWorkflow` model
   - `Alert` model
   - **`BudgetCeiling` model** (for sector/funding source ceilings)
   - **`BudgetScenario` model** (for scenario planning)
   - Migrations

3. **Extend Existing Models**:
   - Add `linked_workflow` to `StaffTask`
   - Add `linked_ppa` to `StaffTask`
   - **Add `approval_status`, `approval_history` to `MonitoringEntry`** (budget approval workflow)
   - **Add `reviewed_by`, `budget_approved_by`, `executive_approved_by` to `MonitoringEntry`**

4. **Base Views**:
   - Portfolio dashboard (basic version **with budget metrics**)
   - Project workflow detail view
   - Alert listing view
   - **Budget planning dashboard (basic version)**

#### Success Criteria

- ✅ Project Management Portal app installed and accessible
- ✅ ProjectWorkflow model can be created and linked to Need + PPA
- ✅ Portfolio dashboard shows summary metrics **including budget allocation and utilization**
- ✅ Users can view project workflow details **with budget approval status**
- ✅ **Budget ceilings can be set and tracked**

---

### Phase 2: Workflow Management + Budget Approval 

**Goal**: Implement full project lifecycle workflow **with 5-stage budget approval process**

#### Deliverables

1. **Workflow Stage Management**:
   - Stage advancement logic
   - Stage validation rules **including budget approval gates**
   - Stage-specific forms **with budget fields**

2. **Budget Approval Workflow** ⭐:
   - **5-stage approval process** (draft → technical_review → budget_review → executive_approval → approved → enacted)
   - **Approval task auto-generation** for each stage
   - **Budget ceiling validation** (reject if exceeds sector/source ceiling)
   - **Approval history tracking** (who approved, when, comments)

3. **Automated Task Generation**:
   - Task templates for each workflow stage
   - **Budget-specific tasks** (prepare budget justification, conduct cost analysis, submit for approval)
   - Auto-create tasks on stage transitions
   - Task-to-workflow linkage

4. **UI Components**:
   - Workflow progress indicator **with budget approval status**
   - Stage-specific action buttons
   - Task management integrated view
   - **Budget approval dashboard** (pending approvals, approval queue)

5. **Notifications**:
   - Email notifications for stage transitions
   - In-app notifications for assigned tasks
   - **Budget approval notifications** (submission, approvals, rejections)

#### Success Criteria

- ✅ Can advance project through all workflow stages
- ✅ **Budget approval workflow functions correctly (all 5 stages)**
- ✅ **Budget ceiling enforcement works** (prevents over-allocation)
- ✅ Tasks automatically generated at appropriate stages
- ✅ Users receive notifications for assignments **and budget approvals**
- ✅ Workflow history tracked **including approval trail**

---

### Phase 3: Analytics & Financial Reporting 

**Goal**: Build comprehensive M&E analytics dashboard **with integrated financial tracking**

#### Deliverables

1. **M&E + Budget Analytics Dashboard** ⭐:
   - Performance scorecard **with budget utilization metrics**
   - Needs-to-results chain **with funding rates**
   - Sector performance comparison **including cost-effectiveness**
   - Geographic distribution map **with budget allocation overlay**
   - Policy impact tracker **with budget allocated per policy**
   - MAO participation report **with budget execution rates**
   - **Budget vs. Actual variance analysis**
   - **FundingFlow tracking** (allocation → obligation → disbursement)

2. **Data Aggregation Services**:
   - Budget aggregation functions **by sector, funding source, region**
   - Outcome achievement calculations
   - Cost-effectiveness analysis **(cost per beneficiary, efficiency ratings)**
   - Geographic data processing
   - **Budget utilization rate calculations**
   - **Obligation and disbursement rate tracking**

3. **Visualizations**:
   - Chart.js / Plotly integrations
   - Interactive maps (Leaflet) **with budget heat maps**
   - Progress bars and indicators
   - Trend lines and forecasts **for budget spending**
   - **Budget ceiling gauges** (visual indicators of ceiling utilization)

4. **Export Functionality**:
   - Export dashboards to PDF
   - Export data to Excel **with financial tabs**
   - Export charts as images

#### Success Criteria

- ✅ M&E dashboard shows real-time data **including financial metrics**
- ✅ All major KPIs calculated correctly **including budget KPIs**
- ✅ **Budget utilization, obligation, and disbursement rates accurate**
- ✅ **Cost-effectiveness analysis functional**
- ✅ Visualizations render properly
- ✅ Data can be exported in multiple formats **with financial data**

---

### Phase 4: Alerts & Automation 

**Goal**: Implement automated alerts and proactive monitoring **with budget-focused alerts**

#### Deliverables

1. **Alert Generation Service**:
   - Daily alert generation (Celery task)
   - Alert prioritization logic
   - Alert acknowledgment system

2. **Alert Types Implementation**:
   - Unfunded high-priority needs **(with estimated budget required)**
   - Overdue PPAs
   - Pending quarterly reports
   - **Budget ceiling alerts** ⭐ **(sector/funding source approaching limits)**
   - Policy implementation lagging
   - **Budget approval bottlenecks** (PPAs stuck in approval stages)
   - **Disbursement delays** (low disbursement rates)
   - **Underspending alerts** (PPAs with low obligation rates)
   - **Overspending warnings** (PPAs exceeding budget allocation)

3. **Notification System**:
   - Email alerts
   - In-app notifications
   - SMS alerts (optional)
   - Webhook support (optional)

4. **Alert Dashboard**:
   - Alert listing with filters
   - Alert detail views
   - Bulk acknowledgment
   - Alert history
   - **Budget alert summary** (count by type, urgency level)

#### Success Criteria

- ✅ Alerts generated daily via Celery
- ✅ Users receive relevant alerts **including budget alerts**
- ✅ **Budget ceiling alerts trigger at 90% threshold**
- ✅ **Approval bottleneck alerts identify stuck PPAs**
- ✅ Alerts can be acknowledged and resolved
- ✅ Alert dashboard accessible and functional

---

### Phase 5: Integrated Reporting + Budget Reports 

**Goal**: Create comprehensive integrated reports **with financial data throughout**

#### Deliverables

1. **Report Generator Service**:
   - PDF generation (WeasyPrint or ReportLab)
   - Excel generation (openpyxl)
   - Report templates **with budget sections**

2. **Report Types** (all include financial data):
   - **Project portfolio report** (programmatic + budget allocation, utilization, spending trends)
   - **Needs assessment impact report** (needs funded vs. unfunded with budget gap analysis)
   - **Policy implementation report** (budget allocated per policy, cost-effectiveness)
   - **MAO coordination report** (MAO budget execution, disbursement rates)
   - **M&E consolidated report** (outcomes + cost-benefit analysis)
   - **Budget execution report** ⭐ **(NEW: obligations, disbursements, variance by sector/source)**
   - **Annual planning cycle report** ⭐ **(NEW: budget envelope utilization, allocation decisions)**

3. **Report Scheduling**:
   - Scheduled report generation (Celery)
   - Report archive management
   - Report distribution (email)
   - **Quarterly budget reports auto-generated**

4. **Report UI**:
   - Report listing view
   - Report preview
   - Report download
   - Report sharing
   - **Budget report dashboard** (quick access to financial reports)

#### Success Criteria

- ✅ All report types can be generated **with financial data**
- ✅ Reports contain accurate data **including budget figures**
- ✅ **Budget execution reports show obligations and disbursements correctly**
- ✅ Reports can be scheduled
- ✅ Reports can be downloaded and shared
- ✅ **Excel exports include detailed financial tabs**

---

### Phase 6: UI/UX Enhancement 

**Goal**: Polish user interface and experience

#### Deliverables

1. **Responsive Design**:
   - Mobile-optimized views
   - Tablet layouts
   - Print-friendly views

2. **Interactive Features**:
   - HTMX-powered interactions
   - Real-time updates
   - Drag-and-drop (if applicable)
   - Inline editing

3. **Dashboard Customization**:
   - User-configurable widgets
   - Saved views
   - Personalized dashboards

4. **Accessibility**:
   - WCAG 2.1 AA compliance
   - Keyboard navigation
   - Screen reader support
   - High contrast mode

#### Success Criteria

- ✅ All views responsive on mobile/tablet
- ✅ HTMX interactions smooth and fast
- ✅ Users can customize dashboards
- ✅ Accessibility standards met

---

### Phase 7: Integration Testing & Refinement 

**Goal**: Comprehensive testing and bug fixes

#### Deliverables

1. **Testing**:
   - Unit tests for all models and services
   - Integration tests for workflows
   - UI/UX testing
   - Performance testing
   - Load testing

2. **Documentation**:
   - User manual
   - Admin guide
   - API documentation
   - Developer documentation

3. **Training Materials**:
   - Video tutorials
   - Quick start guides
   - FAQs
   - Training slides

4. **Bug Fixes & Optimizations**:
   - Performance optimizations
   - Bug fixes
   - Code refactoring
   - Security hardening

#### Success Criteria

- ✅ Test coverage > 80%
- ✅ All major bugs fixed
- ✅ Documentation complete
- ✅ Training materials ready

---

### Phase 8: Deployment & Training 

**Goal**: Launch Project Management Portal and train users

#### Deliverables

1. **Production Deployment**:
   - Deploy to production server
   - Configure Celery workers
   - Set up monitoring (Sentry, etc.)
   - Configure backups

2. **Data Migration**:
   - Create ProjectWorkflow for existing PPAs (optional)
   - Historical data migration (if needed)

3. **User Training**:
   - OOBC staff training (3 days)
   - MAO focal person training (1 day)
   - Refresher sessions (ongoing)

4. **Support Plan**:
   - Support ticketing system
   - Regular check-ins
   - Feedback collection

#### Success Criteria

- ✅ Project Management Portal live in production
- ✅ All users trained
- ✅ Support plan in place
- ✅ Positive user feedback

---

## Technical Specifications

### New Django App Structure

```
src/project_central/
├── __init__.py
├── apps.py
├── models.py                  # ProjectWorkflow, Alert
├── admin.py
├── urls.py
├── views.py                   # Dashboard and workflow views
├── forms.py
├── services/
│   ├── __init__.py
│   ├── alert_service.py       # Alert generation logic
│   ├── report_generator.py    # Report generation
│   ├── workflow_service.py    # Workflow automation
│   └── analytics_service.py   # Data aggregation
├── tasks.py                   # Celery tasks
├── templates/
│   └── project_central/
│       ├── base.html
│       ├── portfolio_dashboard.html
│       ├── workflow_detail.html
│       ├── me_analytics.html
│       ├── alerts_list.html
│       └── reports_list.html
├── static/
│   └── project_central/
│       ├── css/
│       ├── js/
│       └── img/
├── tests/
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_services.py
│   └── test_workflows.py
└── migrations/
    └── 0001_initial.py
```

### Database Schema Changes

#### New Tables (2)

1. **`project_central_projectworkflow`**:
   - Tracks project lifecycle workflow
   - Links Need → PPA
   - Stores workflow stage history

2. **`project_central_alert`**:
   - System-generated alerts
   - Alert types, severity, status
   - Links to related objects (PPA, Need, Policy)

#### Modified Tables (1)

1. **`common_stafftask`**:
   - Add `linked_workflow` FK to ProjectWorkflow
   - Add `linked_ppa` FK to MonitoringEntry
   - Add `workflow_stage` CharField
   - Add `auto_generated` BooleanField

### URL Structure

```python
# src/project_central/urls.py
urlpatterns = [
    # Portfolio Dashboard
    path('dashboard/', views.portfolio_dashboard_view, name='portfolio_dashboard'),

    # Project Workflows
    path('projects/', views.project_list_view, name='project_list'),
    path('projects/<uuid:workflow_id>/', views.project_workflow_detail, name='project_workflow_detail'),
    path('projects/<uuid:workflow_id>/advance/', views.advance_project_stage, name='advance_project_stage'),
    path('projects/create/', views.create_project_workflow, name='create_project_workflow'),

    # M&E Analytics
    path('analytics/', views.me_analytics_dashboard, name='me_analytics_dashboard'),
    path('analytics/sector/<str:sector>/', views.sector_analytics, name='sector_analytics'),
    path('analytics/geographic/', views.geographic_analytics, name='geographic_analytics'),
    path('analytics/policy/<uuid:policy_id>/', views.policy_analytics, name='policy_analytics'),

    # Alerts
    path('alerts/', views.alert_list_view, name='alert_list'),
    path('alerts/<uuid:alert_id>/', views.alert_detail_view, name='alert_detail'),
    path('alerts/<uuid:alert_id>/acknowledge/', views.acknowledge_alert, name='acknowledge_alert'),

    # Reports
    path('reports/', views.report_list_view, name='report_list'),
    path('reports/portfolio/generate/', views.generate_portfolio_report, name='generate_portfolio_report'),
    path('reports/needs-impact/generate/', views.generate_needs_impact_report, name='generate_needs_impact_report'),
    path('reports/policy/generate/', views.generate_policy_report, name='generate_policy_report'),
    path('reports/mao/generate/', views.generate_mao_report, name='generate_mao_report'),
    path('reports/<uuid:report_id>/download/', views.download_report, name='download_report'),

    # Tasks (Enhanced)
    path('tasks/', views.my_tasks_with_projects, name='my_tasks_with_projects'),
]
```

### Celery Tasks

```python
# src/project_central/tasks.py

from celery import shared_task
from .services.alert_service import AlertService
from .services.report_generator import ReportGenerator

@shared_task
def generate_daily_alerts_task():
    """Daily task to generate alerts."""
    AlertService.generate_daily_alerts()

@shared_task
def generate_weekly_portfolio_report_task():
    """Weekly task to generate portfolio report."""
    import datetime
    current_year = datetime.datetime.now().year
    ReportGenerator.generate_portfolio_report(current_year)

@shared_task
def generate_monthly_consolidated_report_task():
    """Monthly task to generate consolidated M&E report."""
    ReportGenerator.generate_consolidated_me_report()
```

### Performance Considerations

#### Caching Strategy

```python
# Cache dashboard aggregations
from django.core.cache import cache

def get_portfolio_metrics(fiscal_year):
    cache_key = f'portfolio_metrics_{fiscal_year}'
    metrics = cache.get(cache_key)

    if not metrics:
        metrics = compute_portfolio_metrics(fiscal_year)
        cache.set(cache_key, metrics, timeout=3600)  # 1 hour

    return metrics

# Invalidate cache when data changes
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=MonitoringEntry)
def invalidate_portfolio_cache(sender, instance, **kwargs):
    cache_key = f'portfolio_metrics_{instance.fiscal_year}'
    cache.delete(cache_key)
```

#### Database Indexing

```python
# In ProjectWorkflow model
class Meta:
    indexes = [
        models.Index(fields=['current_stage', 'initiated_date']),
        models.Index(fields=['project_lead', 'current_stage']),
        models.Index(fields=['mao_focal_person', 'current_stage']),
    ]

# In Alert model
class Meta:
    indexes = [
        models.Index(fields=['alert_type', 'is_active']),
        models.Index(fields=['severity', 'is_active', '-created_at']),
    ]
```

#### Query Optimization

```python
# Use select_related and prefetch_related
workflows = ProjectWorkflow.objects.select_related(
    'primary_need',
    'primary_need__community',
    'primary_need__assessment',
    'ppa',
    'ppa__lead_organization',
    'project_lead',
    'mao_focal_person',
).prefetch_related(
    'ppa__implementing_policies',
    'ppa__needs_addressed',
    'tasks',
)
```

---

## Success Criteria

### Quantitative Metrics

**System Adoption**:
- ✅ 90%+ of OOBC staff use Project Management Portal regularly
- ✅ 80%+ of MAO focal persons access Project Management Portal monthly
- ✅ 70%+ of active PPAs have associated ProjectWorkflow
- ✅ **100% of PPAs go through budget approval workflow** (after Phase 2)

**Data Quality**:
- ✅ 95%+ of PPAs have complete data (all required fields filled **including budget details**)
- ✅ 90%+ of needs have budget linkage (if funded)
- ✅ 85%+ of policies have PPAs linked
- ✅ **100% of PPAs have funding source, appropriation class, and fiscal year specified**
- ✅ **90%+ of PPAs have cost per beneficiary calculated**

**Performance**:
- ✅ Portfolio dashboard loads < 2 seconds
- ✅ Report generation completes < 30 seconds
- ✅ Alert generation runs < 5 minutes daily
- ✅ **Budget dashboard loads < 3 seconds** (with aggregations cached)

**Workflow Efficiency**:
- ✅ 40% reduction in time to create new PPAs (with workflow guidance **and budget templates**)
- ✅ 50% reduction in missed deadlines (with automated alerts)
- ✅ 60% reduction in manual reporting time (with automated reports)
- ✅ **30% faster budget approval process** (5-stage workflow vs. ad-hoc approvals)
- ✅ **80% reduction in budget data entry errors** (validation and ceiling checks)

**Budget & Financial Metrics** ⭐:
- ✅ **Budget utilization rate: 85-95%** (optimal range, not too low or too high)
- ✅ **Obligation rate: 90%+** by end of fiscal year
- ✅ **Disbursement rate: 75%+** by end of fiscal year
- ✅ **Budget ceiling compliance: 100%** (no over-allocation)
- ✅ **Cost-effectiveness rating: 80%+ of PPAs rated "high" or "very high"**
- ✅ **Funding rate for high-priority needs: 70%+** (percentage of needs with priority score ≥4.0 that are funded)
- ✅ **Budget variance: ±10%** (actual vs. budgeted spending within acceptable range)

### Qualitative Metrics

**User Satisfaction**:
- ✅ Positive feedback from OOBC staff on project visibility **and budget transparency**
- ✅ MAO focal persons find coordination easier
- ✅ Leadership reports improved decision-making capability **with real-time budget data**
- ✅ **Finance officers report faster budget review process**
- ✅ **Community representatives engaged through participatory budgeting sessions**

**Transparency**:
- ✅ Clear visibility into project pipeline **including budget status**
- ✅ Easy access to project status for all stakeholders
- ✅ Improved accountability with workflow tracking **and approval trails**
- ✅ **Budget allocation decisions documented and justified**
- ✅ **Budget ceiling compliance visible to all planners**

**Integration**:
- ✅ Seamless data flow between modules (no manual re-entry)
- ✅ Single source of truth for project information **and financial data**
- ✅ Reduced data silos
- ✅ **Budget data automatically flows from Need (estimated_cost) → PPA (budget_allocation) → FundingFlow (obligations/disbursements)**
- ✅ **Cost-effectiveness lessons learned inform future budget planning**

---

## Conclusion

### Summary

The OBCMS codebase has **exceptional foundations** for integrated project management:
- ✅ Comprehensive data models across all modules
- ✅ Well-designed integration patterns (M2M relationships, FKs)
- ✅ Strong evidence-based budgeting infrastructure
- ✅ Excellent MAO coordination framework
- ✅ Robust policy tracking and M&E capabilities

**The missing piece**: A **unified project management layer** (Project Management Portal) that:
1. Provides a single interface for project lifecycle management **with integrated budgeting**
2. Orchestrates cross-module workflows **including budget approval gates**
3. Consolidates monitoring, evaluation, **and financial reporting**
4. Automates alerts and notifications **including budget warnings**
5. Creates a holistic view of OOBC project portfolio **with financial dimensions**

### Strategic Value

**Project Management Portal with Integrated Planning & Budgeting** will transform OBCMS from a **collection of excellent modules** into a **fully integrated project management system** that:

- **Improves Transparency**: Stakeholders see complete project lifecycle **from need → budget → implementation → financial results**
- **Enhances Coordination**: MAOs, communities, and OOBC work seamlessly **with clear budget commitments**
- **Enables Evidence-Based Budgeting**: Real-time analytics inform budget allocation based on **cost-effectiveness, needs prioritization, and policy alignment**
- **Increases Accountability**: Clear workflow stages and task management **with multi-stage budget approval and spending tracking**
- **Demonstrates Impact**: Consolidated reporting shows needs → policies → PPAs → outcomes **with cost-benefit analysis**
- **Optimizes Resource Allocation**: Budget ceiling management, scenario planning, and variance analysis enable **efficient use of limited resources**
- **Strengthens Participatory Governance**: Community voting on budget priorities ensures **grassroots engagement in fiscal decisions**
- **Facilitates Multi-Source Funding**: Coordinate GAA, Block Grant, LGU, and donor funds **in one integrated system**

### Next Steps

1. **Review & Approval**: Present this plan to OOBC leadership
2. **Prioritization**: Confirm phase sequencing and resource allocation
3. **Sprint Planning**: Break Phase 1 into 2-week sprints
4. **Kickoff**: Begin Phase 1 (Foundation) development
5. **Iterative Delivery**: Deploy features incrementally with user feedback

---

**Document Version**: 1.0
**Last Updated**: October 1, 2025

---

## Appendix: 63 Actionable Implementation Tasks

### PHASE 1: Foundation - 11 Tasks

1. ✅ **Create new Django app 'project_central'** with structure, URLs, and base templates
2. ✅ **Implement ProjectWorkflow model** - tracks lifecycle, links Need→PPA, stores stage history
3. ✅ **Implement Alert model** - system alerts with types, severity, status, related object links
4. ✅ **Implement BudgetCeiling model** - sector/funding source ceiling tracking
5. ✅ **Implement BudgetScenario model** - scenario planning support
6. ✅ **Extend StaffTask model** - add linked_workflow, linked_ppa, workflow_stage, auto_generated fields
7. ✅ **Extend MonitoringEntry model** - add approval_status, approval_history, reviewer fields for budget approval workflow
8. ✅ **Create portfolio dashboard view** with budget metrics (total budget, active projects, beneficiaries, budget utilization)
9. ✅ **Create project workflow detail view** - shows stages, budget approval status, timeline
10. ✅ **Create alert listing view** with filters and acknowledgment
11. ✅ **Create basic budget planning dashboard** - budget allocation, utilization by sector/source

### PHASE 2: Workflow Management + Budget Approval - 8 Tasks

12. ✅ **Implement workflow stage management** - advancement logic, validation rules, budget approval gates
13. ✅ **Implement 5-stage budget approval workflow** - draft→technical_review→budget_review→executive_approval→approved→enacted
14. ✅ **Implement budget ceiling validation** - reject PPAs exceeding sector/source ceilings
15. ✅ **Implement approval history tracking** - who approved, when, comments at each stage
16. ✅ **Create automated task generation system** - task templates per workflow stage, budget-specific tasks
17. ✅ **Build workflow progress indicator UI** with budget approval status visualization
18. ✅ **Build budget approval dashboard** - pending approvals queue, approval actions
19. ✅ **Implement notification system** - email + in-app for stage transitions, budget approvals

### PHASE 3: Analytics & Financial Reporting - 11 Tasks

20. ✅ **Build comprehensive M&E + Budget Analytics Dashboard** - performance scorecard, budget utilization metrics
21. ✅ **Implement needs-to-results chain visualization** with funding rates
22. ✅ **Implement sector performance comparison** with cost-effectiveness analysis
23. ✅ **Build geographic distribution map** with budget allocation overlay
24. ✅ **Create policy impact tracker** - budget allocated per policy, implementation progress
25. ✅ **Create MAO participation report** - engagement rates, budget execution rates
26. ✅ **Implement budget vs. actual variance analysis**
27. ✅ **Implement FundingFlow tracking** - allocation→obligation→disbursement visualization
28. ✅ **Create data aggregation services** - budget by sector/source/region, utilization rates, cost-effectiveness
29. ✅ **Integrate visualizations** - Chart.js/Plotly for charts, Leaflet for budget heat maps, budget ceiling gauges
30. ✅ **Implement export functionality** - PDF, Excel with financial tabs, charts as images

### PHASE 4: Alerts & Automation - 10 Tasks

31. ✅ **Create alert generation service** with daily Celery task
32. ✅ **Implement unfunded high-priority needs alerts** - with budget estimates
33. ✅ **Implement overdue PPAs alerts**
34. ✅ **Implement pending quarterly reports alerts**
35. ✅ **Implement budget ceiling alerts** - trigger at 90% threshold by sector/funding source
36. ✅ **Implement policy implementation lagging alerts**
37. ✅ **Implement budget approval bottleneck alerts** - PPAs stuck in approval stages
38. ✅ **Implement disbursement delay alerts** - low disbursement rates
39. ✅ **Implement underspending and overspending alerts**
40. ✅ **Build alert dashboard** with filters, detail views, bulk acknowledgment, budget alert summary

### PHASE 5: Integrated Reporting - 10 Tasks

41. ✅ **Create report generator service** - PDF via WeasyPrint/ReportLab, Excel via openpyxl
42. ✅ **Implement project portfolio report** - programmatic + budget allocation, utilization, spending trends
43. ✅ **Implement needs assessment impact report** - needs funded vs unfunded with budget gap analysis
44. ✅ **Implement policy implementation report** - budget allocated per policy, cost-effectiveness
45. ✅ **Implement MAO coordination report** - MAO budget execution, disbursement rates
46. ✅ **Implement M&E consolidated report** - outcomes + cost-benefit analysis
47. ✅ **Implement budget execution report** - obligations, disbursements, variance by sector/source
48. ✅ **Implement annual planning cycle report** - budget envelope utilization, allocation decisions
49. ✅ **Implement report scheduling** with Celery - quarterly budget reports auto-generated
50. ✅ **Build report UI** - listing, preview, download, sharing, budget report dashboard

### PHASE 6: UI/UX Enhancement - 4 Tasks

51. ✅ **Implement responsive design** - mobile-optimized, tablet layouts, print-friendly views
52. ✅ **Implement HTMX-powered interactive features** - real-time updates, inline editing
53. ✅ **Implement dashboard customization** - user-configurable widgets, saved views, personalized dashboards
54. ✅ **Ensure WCAG 2.1 AA accessibility compliance** - keyboard navigation, screen reader, high contrast

### PHASE 7: Testing & Documentation - 5 Tasks

55. ✅ **Write comprehensive unit tests** - models, services, workflows - target >80% coverage
56. ✅ **Write integration tests** - workflow transitions, approval processes, alert generation
57. ✅ **Conduct UI/UX testing and performance/load testing**
58. ✅ **Create documentation** - user manual, admin guide, API docs, developer docs
59. ✅ **Create training materials** - video tutorials, quick start guides, FAQs, training slides
60. ✅ **Perform bug fixes, code refactoring, security hardening, and performance optimizations**

### PHASE 8: Deployment & Training - 4 Tasks

61. ✅ **Deploy to production** - configure Celery workers, monitoring via Sentry, backups
62. ✅ **Migrate data** - create ProjectWorkflow for existing PPAs, historical data migration
63. ✅ **Conduct user training** - OOBC staff 3-day training, MAO focal persons 1-day training
64. ✅ **Set up support plan** - ticketing system, regular check-ins, feedback collection

---

**Implementation Status**: Ready to begin
**Total Tasks**: 63
**Estimated Timeline**: 32 weeks (8 months)
**Priority**: Phase 1 (Foundation) - Begin immediately
**Next Review**: After Phase 1 completion
