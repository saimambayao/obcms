# BARMM Budget Cycle - OBCMS Integration Visual Summary

**Date:** October 5, 2025
**Last Updated:** October 6, 2025
**Purpose:** Visual reference for BARMM budget cycle integration with OBCMS

**Note**: This document uses correct BARMM agency nomenclature:
- **MFBM**: Ministry of Finance and Budget Management (budget formulation, execution, fiscal policy)
- **BPDA**: Bangsamoro Planning and Development Authority (planning, development coordination, BDP alignment)
- **BICTO**: Bangsamoro ICT Office (ICT infrastructure, OBCMS platform, e-governance)

---

## 1. Budget Cycle Timeline (12-Month View)

```
BARMM BUDGET CYCLE - FISCAL YEAR 2025
═══════════════════════════════════════════════════════════════

JAN  FEB  MAR  APR  MAY  JUN  JUL  AUG  SEP  OCT  NOV  DEC
─────────────────────────────────────────────────────────────
 │    │    │    │    │    │    │    │    │    │    │    │
 │◄───────────────PHASE 1: FORMULATION─────────────────►│
 │                                                        │
 ▼                                                        │
Budget Call                                              │
Issued (MFBM)                                            │
                                                          │
    ▼                                                     │
    MOA Proposal                                         │
    Preparation                                          │
                                                          │
              ▼                                          │
              Technical Budget                           │
              Hearings (MFBM)                            │
                                                          │
                        ▼                                │
                        Budget Document                  │
                        Preparation                      │
                                                          │
                              ◄─────PHASE 2: LEGISLATION───────────►
                              │                                     │
                              ▼                                     │
                              Executive Budget                      │
                              Submission (CM)                       │
                                                                    │
                                    ▼                              │
                                    Parliamentary                   │
                                    Hearings                        │
                                                                    │
                                          ▼                        │
                                          Public                    │
                                          Consultations             │
                                                                    │
                                                ▼                  │
                                                Floor              │
                                                Deliberation       │
                                                                    │
                                                      ▼            │
                                                      Parliament   │
                                                      Approval     │
                                                                    │
                                                            ▼      │
                                                            Budget │
                                                            Enactment

NEXT FISCAL YEAR (FY 2025)
═══════════════════════════════════════════════════════════════

JAN  FEB  MAR  APR  MAY  JUN  JUL  AUG  SEP  OCT  NOV  DEC
─────────────────────────────────────────────────────────────
 │◄──────────────────PHASE 3: EXECUTION──────────────────────►│
 │                                                              │
 ▼                                                              │
Allotment Release (Quarterly)                                  │
                                                                │
 ▼                                                              │
Obligation of Funds                                            │
                                                                │
 ▼                                                              │
Disbursement                                                   │
                                                                │
 ▼                                                              │
Monthly Monitoring & Reporting                                 │


FOLLOWING FISCAL YEAR (FY 2026)
═══════════════════════════════════════════════════════════════

JAN  FEB  MAR  APR  MAY  JUN  JUL  AUG  SEP  OCT  NOV  DEC
─────────────────────────────────────────────────────────────
 │◄────PHASE 4: ACCOUNTABILITY──────►│
 │                                    │
 ▼                                    │
Annual                                │
Accomplishment                        │
Reports                               │
                                      │
       ▼                              │
       COA Audit                      │
       (Financial,                    │
        Compliance,                   │
        Performance)                  │
                                      │
             ▼                        │
             Audit Report             │
             Issuance                 │
                                      │
                   ▼                  │
                   Parliamentary      │
                   Oversight          │
```

---

## 2. OBCMS Workflow Stages Mapping

```
BARMM BUDGET PHASE          OBCMS WORKFLOW STAGE         OBCMS APPROVAL STATUS
══════════════════          ═══════════════════          ═════════════════════

PHASE 1: FORMULATION
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ Budget Call     │   ═══>  │ budget_call     │         │ draft           │
│ (MFBM Issues)   │         │ (milestone)     │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
         │                           │                           │
         ↓                           ↓                           ↓
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ MOA Proposal    │   ═══>  │ formulation     │         │ draft           │
│ Preparation     │         │ (in_progress)   │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
         │                           │                           │
         ↓                           ↓                           ↓
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ Technical       │   ═══>  │ formulation     │         │ technical_review│
│ Review (MFBM)   │         │ (in_progress)   │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
         │                           │                           │
         ↓                           ↓                           ↓
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ Budget Hearing  │   ═══>  │ technical_      │         │ budget_review   │
│ (MFBM Director) │         │ hearing         │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
         │                           │                           │
         ↓                           ↓                           ↓

PHASE 2: LEGISLATION
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ Executive       │   ═══>  │ legislation     │         │ executive_      │
│ Submission (CM) │         │ (in_progress)   │         │ approval        │
└─────────────────┘         └─────────────────┘         └─────────────────┘
         │                           │                           │
         ↓                           ↓                           ↓
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ Public          │   ═══>  │ legislation     │         │ stakeholder_    │
│ Consultation    │         │ (in_progress)   │         │ consultation    │
└─────────────────┘         └─────────────────┘         └─────────────────┘
         │                           │                           │
         ↓                           ↓                           ↓
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ Parliament      │   ═══>  │ legislation     │         │ approved        │
│ Approval        │         │ (in_progress)   │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
         │                           │                           │
         ↓                           ↓                           ↓
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ Budget          │   ═══>  │ legislation     │         │ enacted         │
│ Enactment       │         │ (completed)     │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
         │                           │                           │
         ↓                           ↓                           ↓

PHASE 3: EXECUTION
┌─────────────────┐         ┌─────────────────┐
│ Allotment       │   ═══>  │ execution       │         MonitoringEntryFunding
│ Release         │         │ (in_progress)   │         (allocation tranches)
└─────────────────┘         └─────────────────┘
         │                           │
         ↓                           ↓
┌─────────────────┐         ┌─────────────────┐
│ Obligation      │   ═══>  │ execution       │         MonitoringEntryFunding
│                 │         │ (in_progress)   │         (obligation tranches)
└─────────────────┘         └─────────────────┘
         │                           │
         ↓                           ↓
┌─────────────────┐         ┌─────────────────┐
│ Disbursement    │   ═══>  │ execution       │         MonitoringEntryFunding
│                 │         │ (in_progress)   │         (disbursement tranches)
└─────────────────┘         └─────────────────┘
         │                           │
         ↓                           ↓

PHASE 4: ACCOUNTABILITY
┌─────────────────┐         ┌─────────────────┐
│ Annual Reports  │   ═══>  │ accountability  │         MonitoringUpdate
│                 │         │ (in_progress)   │         (accomplishments)
└─────────────────┘         └─────────────────┘
         │                           │
         ↓                           ↓
┌─────────────────┐         ┌─────────────────┐
│ COA Audit       │   ═══>  │ accountability  │         coa_audit_status
│                 │         │ (in_progress)   │         (pending/completed)
└─────────────────┘         └─────────────────┘
         │                           │
         ↓                           ↓
┌─────────────────┐         ┌─────────────────┐
│ Parliamentary   │   ═══>  │ accountability  │         Alert
│ Oversight       │         │ (completed)     │         (audit findings)
└─────────────────┘         └─────────────────┘
```

---

## 3. Data Flow Diagram

```
BARMM STAKEHOLDERS              OBCMS SYSTEM                DATABASE MODELS
═══════════════════              ════════════                ═══════════════

┌───────────────┐
│ MFBM Director │
└──────┬────────┘
       │ Issues Budget Call
       ↓
┌──────────────────────┐        ┌─────────────────┐
│ BUDGET CALL CIRCULAR │  ═══>  │ BudgetCall      │  (NEW)
│ (Ceilings per MOA)   │        │ Model           │
└──────────────────────┘        └────────┬────────┘
                                         │
                                         ↓ Celery Task
                                ┌─────────────────────────┐
                                │ Auto-create Draft PPAs  │
                                │ per MOA                 │
                                └────────┬────────────────┘
                                         │
                                         ↓
                                ┌─────────────────┐
                                │ MonitoringEntry │
                                │ (category:      │
                                │  'moa_ppa')     │
                                └────────┬────────┘
       ┌─────────────────────────────────┘
       │
       ↓
┌──────────────┐
│ MOA Staff    │
└──────┬───────┘
       │ Fills PPA Proposal
       ↓
┌──────────────────────┐        ┌─────────────────┐
│ PPA BUDGET PROPOSAL  │  ═══>  │ MonitoringEntry │
│ (Budget allocation,  │        │ .budget_        │
│  sector, outcomes)   │        │  allocation     │
└──────────────────────┘        └────────┬────────┘
                                         │
                                         ↓
                                ┌─────────────────┐
                                │ approval_status │
                                │ = 'draft'       │
                                └────────┬────────┘
       ┌─────────────────────────────────┘
       │
       ↓
┌──────────────┐
│ MFBM Analyst │
└──────┬───────┘
       │ Reviews PPA
       ↓
┌──────────────────────┐        ┌─────────────────┐
│ TECHNICAL REVIEW     │  ═══>  │ approval_status │
│ (Comments, feedback) │        │ = 'technical_   │
│                      │        │    review'      │
└──────────────────────┘        └────────┬────────┘
                                         │
                                         ↓
                                ┌─────────────────┐
                                │ approval_history│
                                │ (JSON append)   │
                                └────────┬────────┘
       ┌─────────────────────────────────┘
       │
       ↓
┌───────────────┐
│ MFBM Director │
└──────┬────────┘
       │ Budget Hearing
       ↓
┌──────────────────────┐        ┌─────────────────┐
│ BUDGET HEARING       │  ═══>  │ approval_status │
│ (Approve/Reject)     │        │ = 'budget_      │
│                      │        │    review'      │
└──────────────────────┘        └────────┬────────┘
                                         │
                                         ↓
                                ┌─────────────────────┐
                                │ MonitoringEntry     │
                                │ WorkflowStage       │
                                │ .stage =            │
                                │  'technical_hearing'│
                                └────────┬────────────┘
       ┌─────────────────────────────────┘
       │
       ↓
┌──────────────┐
│ Chief        │
│ Minister     │
└──────┬───────┘
       │ Submits to Parliament
       ↓
┌──────────────────────┐        ┌─────────────────┐
│ EXECUTIVE BUDGET     │  ═══>  │ approval_status │
│ SUBMISSION           │        │ = 'executive_   │
│                      │        │    approval'    │
└──────────────────────┘        └────────┬────────┘
                                         │
                                         ↓
                                ┌─────────────────┐
                                │ MonitoringEntry │
                                │ WorkflowStage   │
                                │ .stage =        │
                                │  'legislation'  │
                                └────────┬────────┘
       ┌─────────────────────────────────┘
       │
       ↓
┌──────────────┐
│ Bangsamoro   │
│ Parliament   │
└──────┬───────┘
       │ Public Consultation + Approval
       ↓
┌──────────────────────┐        ┌─────────────────┐
│ PARLIAMENT APPROVAL  │  ═══>  │ approval_status │
│ (Budget Bill Vote)   │        │ = 'approved'    │
└──────────────────────┘        └────────┬────────┘
                                         │
                                         ↓
                                ┌─────────────────┐
                                │ approval_status │
                                │ = 'enacted'     │
                                └────────┬────────┘
       ┌─────────────────────────────────┘
       │
       ↓
┌──────────────┐
│ MOA          │
│ (Execution)  │
└──────┬───────┘
       │ Implement PPA
       ↓
┌──────────────────────┐        ┌─────────────────────┐
│ BUDGET EXECUTION     │  ═══>  │ MonitoringEntry     │
│ (Allotment,          │        │ Funding             │
│  Obligation,         │        │ .tranche_type       │
│  Disbursement)       │        │ (allocation,        │
└──────────────────────┘        │  obligation,        │
                                │  disbursement)      │
                                └────────┬────────────┘
                                         │
                                         ↓
                                ┌─────────────────┐
                                │ MonitoringUpdate│
                                │ (progress,      │
                                │  accomplishments│
                                │  challenges)    │
                                └────────┬────────┘
       ┌─────────────────────────────────┘
       │
       ↓
┌──────────────┐
│ COA Auditors │
└──────┬───────┘
       │ Annual Audit
       ↓
┌──────────────────────┐        ┌─────────────────┐
│ COA AUDIT REPORT     │  ═══>  │ coa_audit_      │
│ (Findings,           │        │  reference      │
│  Recommendations)    │        │ coa_audit_      │
└──────────────────────┘        │  findings       │
                                └────────┬────────┘
                                         │
                                         ↓
                                ┌─────────────────┐
                                │ Alert           │
                                │ (audit findings)│
                                └─────────────────┘
```

---

## 4. Compliance Checklist Matrix

```
BARMM BUDGET REQUIREMENT                OBCMS FIELD               STATUS
════════════════════════                ═══════════               ══════

BUDGET FORMULATION
├─ Fiscal Year                          fiscal_year               ✅ Complete
├─ Planning Year (AIP)                  plan_year                 ✅ Complete
├─ Budget Ceiling (MOA Allocation)      budget_ceiling            ✅ Complete
├─ Proposed Budget Amount               budget_allocation         ✅ Complete
├─ Appropriation Class (PS/MOOE/CO)     appropriation_class       ✅ Complete
├─ Funding Source (GAA/Block Grant)     funding_source            ✅ Complete
├─ Sectoral Classification              sector                    ✅ Complete
├─ Program Code (DBM)                   program_code              ✅ Complete
└─ Plan Reference (PDP/PIP/AIP)         plan_reference            ✅ Complete

STRATEGIC ALIGNMENT
├─ BEGMP Pillar                         goal_alignment (JSON)     ✅ Complete
├─ Moral Governance Pillar              moral_governance_pillar   ✅ Complete
├─ SDG Alignment                        supports_sdg              ✅ Complete
├─ PDP Alignment                        plan_reference            ✅ Complete
├─ GAD Tagging                          compliance_gad            ✅ Complete
├─ CCET Tagging                         compliance_ccet           ✅ Complete
├─ IP Beneficiary Flag                  benefits_indigenous_      ✅ Complete
│                                       peoples
└─ Peace Agenda Flag                    supports_peace_agenda     ✅ Complete

APPROVAL WORKFLOW
├─ Draft Stage                          approval_status='draft'   ✅ Complete
├─ Technical Review                     approval_status=          ✅ Complete
│                                       'technical_review'
├─ Budget Review                        approval_status=          ✅ Complete
│                                       'budget_review'
├─ Stakeholder Consultation             approval_status=          ✅ Complete
│                                       'stakeholder_consultation'
├─ Executive Approval                   approval_status=          ✅ Complete
│                                       'executive_approval'
├─ Parliament Approval                  approval_status=          ✅ Complete
│                                       'approved'
├─ Budget Enactment                     approval_status='enacted' ✅ Complete
└─ Approval History Logging             approval_history (JSON)   ✅ Complete

BUDGET EXECUTION
├─ Allotment Release Tracking           MonitoringEntryFunding    ✅ Complete
│                                       (tranche_type=
│                                        'allocation')
├─ Obligation Recording                 MonitoringEntryFunding    ✅ Complete
│                                       (tranche_type=
│                                        'obligation')
├─ Disbursement Tracking                MonitoringEntryFunding    ✅ Complete
│                                       (tranche_type=
│                                        'disbursement')
├─ Obligation Rate Calculation          obligation_rate           ✅ Complete
│                                       (property)
├─ Disbursement Rate Calculation        disbursement_rate         ✅ Complete
│                                       (property)
└─ Budget Utilization Rate              budget_utilization_rate   ✅ Complete
                                        (property)

M&E AND OUTCOMES
├─ Outcome Framework                    outcome_framework (JSON)  ✅ Complete
├─ Standard Outcome Indicators          standard_outcome_         ✅ Complete
│                                       indicators (M2M)
├─ Physical Progress (%)                progress                  ✅ Complete
├─ Accomplishments                      accomplishments           ✅ Complete
├─ Challenges                           challenges                ✅ Complete
├─ OBC Beneficiaries                    obcs_benefited            ✅ Complete
└─ Monitoring Updates                   MonitoringUpdate (FK)     ✅ Complete

ACCOUNTABILITY
├─ Annual Reports                       MonitoringUpdate          ✅ Complete
├─ COA Audit Reference                  [PROPOSED FIELD]          ⚠️ Missing
├─ COA Audit Findings                   [PROPOSED FIELD]          ⚠️ Missing
├─ COA Audit Status                     [PROPOSED FIELD]          ⚠️ Missing
└─ Audit Log (Full Change History)      django-auditlog           ✅ Complete

REPORTING REQUIREMENTS
├─ MFBM Budget Execution Report         [EXPORT TEMPLATE]         ⚠️ Missing
│  (Monthly, Excel)
├─ COA Annual Audit Report              [EXPORT TEMPLATE]         ⚠️ Missing
│  (Yearly, Excel)
├─ Parliament Performance Report        [EXPORT TEMPLATE]         ⚠️ Missing
│  (Quarterly, PDF)
└─ DBM Compliance Report                [EXPORT TEMPLATE]         ⚠️ Missing
   (Yearly, Excel)

AUTOMATION
├─ Budget Call Auto-Creation            [CELERY TASK]             ⚠️ Missing
├─ Approval Deadline Reminders          [CELERY BEAT]             ⚠️ Missing
├─ Workflow Stage Auto-Sync             [DJANGO SIGNAL]           ⚠️ Missing
└─ Budget Execution Auto-Init           [DJANGO SIGNAL]           ⚠️ Missing

═══════════════════════════════════════════════════════════════
OVERALL COMPLIANCE SUMMARY
═══════════════════════════════════════════════════════════════

COMPLETE:     42 items  (85%)  ✅
MISSING:       7 items  (15%)  ⚠️
───────────────────────────────
TOTAL:        49 items (100%)
```

---

## 5. Integration Checkpoints

```
BARMM BUDGET MILESTONE      OBCMS TRIGGER               AUTOMATED ACTION
═══════════════════════      ═════════════               ════════════════

Budget Call Issuance         Admin creates               Celery Task:
(MFBM, January)              BudgetCall record          - Auto-create draft
                             ───────────────►              MonitoringEntry
                                                           per MOA
                                                        - Set approval_status
                                                          = 'draft'
                                                        - Create workflow
                                                          stage 'budget_call'

MOA Proposal Deadline        due_date approaching        Celery Beat:
(March)                      ───────────────►            - Send email reminder
                                                          to MOA staff
                                                        - Create Alert
                                                          (deadline warning)

Technical Review Complete    approval_status changed     Django Signal:
(MFBM Analyst, April)        to 'technical_review'      - Update workflow
                             ───────────────►              stage 'formulation'
                                                          to 'completed'
                                                        - Log in approval_
                                                          history JSON

Budget Hearing Complete      approval_status changed     Django Signal:
(MFBM Director, May)         to 'budget_review'         - Create workflow
                             ───────────────►              stage 'technical_
                                                          hearing' (completed)

Executive Submission         approval_status changed     Django Signal:
(Chief Minister, June)       to 'executive_approval'    - Create workflow
                             ───────────────►              stage 'legislation'
                                                          (in_progress)

Public Consultation          approval_status changed     Django Signal:
Required (August)            to 'stakeholder_           - Create Alert
                             consultation'                (consultation
                             ───────────────►              required)
                                                        - Send email to
                                                          Parliament Committee

Parliament Approval          approval_status changed     Django Signal:
(November)                   to 'approved'              - Update workflow
                             ───────────────►              stage 'legislation'
                                                          (completed)

Budget Enactment             approval_status changed     Django Signal:
(Chief Minister, December)   to 'enacted'               - Create workflow
                             ───────────────►              stage 'execution'
                                                          (in_progress)
                                                        - Auto-create
                                                          MonitoringEntry
                                                          Funding records
                                                          (quarterly
                                                          allotments)

Allotment Release            MonitoringEntryFunding      Email Notification:
(Quarterly)                  created                    - Notify MOA Finance
                             (tranche_type=               Officer
                             'allocation')              - Update dashboard
                             ───────────────►

Fiscal Year End              MonitoringUpdate            Celery Task:
(December)                   .progress < 100%           - Generate alerts for
                             ───────────────►              incomplete PPAs
                                                        - Flag for rollover
                                                          to next FY

Annual Report Due            fiscal_year ends            Celery Beat:
(Next FY, March)             ───────────────►            - Send reminder to
                                                          MOA Directors
                                                        - Create workflow
                                                          stage 'accountability'

COA Audit Complete           Admin updates               Django Signal:
(Next FY, June)              coa_audit_status           - Create Alert if
                             to 'completed'               findings exist
                             ───────────────►            - Send notification
                                                          to MOA Director
```

---

## 6. Gap Summary (Visual)

```
CRITICAL GAPS (Must Fix Immediately)
════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────┐
│ GAP 1: Workflow Automation                           │
├──────────────────────────────────────────────────────┤
│ Issue:    Approval status changes don't trigger      │
│           workflow stage updates                     │
│ Impact:   Manual synchronization required            │
│ Solution: Django signals (post_save)                 │
│ Effort:   MODERATE                                   │
│ Priority: CRITICAL                                   │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ GAP 2: MFBM Budget Execution Report Export           │
├──────────────────────────────────────────────────────┤
│ Issue:    Report data available but no Excel export  │
│ Impact:   Cannot deliver monthly reports to MFBM     │
│ Solution: Create openpyxl template                   │
│ Effort:   SIMPLE                                     │
│ Priority: CRITICAL                                   │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ GAP 3: Deadline Reminder System                      │
├──────────────────────────────────────────────────────┤
│ Issue:    No automatic reminders for deadlines       │
│ Impact:   Risk of missing budget submission dates    │
│ Solution: Celery beat task (daily checks)            │
│ Effort:   SIMPLE                                     │
│ Priority: CRITICAL                                   │
└──────────────────────────────────────────────────────┘


HIGH PRIORITY ENHANCEMENTS
════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────┐
│ ENHANCEMENT 1: Budget Call Automation                │
├──────────────────────────────────────────────────────┤
│ Benefit:  Auto-create draft PPAs when budget call    │
│           is issued                                  │
│ Impact:   Reduces MOA workload by 50%                │
│ Solution: Celery task + BudgetCall model             │
│ Effort:   MODERATE                                   │
│ Priority: HIGH                                       │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ ENHANCEMENT 2: COA Audit Report Export               │
├──────────────────────────────────────────────────────┤
│ Benefit:  Full COA compliance with procurement trace │
│ Impact:   Zero audit findings on budget tracking     │
│ Solution: Excel template + PhilGEPS integration      │
│ Effort:   MODERATE                                   │
│ Priority: HIGH                                       │
└──────────────────────────────────────────────────────┘
```

---

## 7. Recommended Actions (Priority Order)

```
IMMEDIATE ACTIONS (Next Development Sprint)
═══════════════════════════════════════════════════════

┌───┬──────────────────────────────────┬──────────┬──────────┐
│ # │ ACTION                           │ EFFORT   │ IMPACT   │
├───┼──────────────────────────────────┼──────────┼──────────┤
│ 1 │ Implement Workflow Sync Signals  │ MODERATE │ CRITICAL │
│   │ (approval_status → workflow)     │          │          │
├───┼──────────────────────────────────┼──────────┼──────────┤
│ 2 │ Create MFBM Report Excel Template│ SIMPLE   │ CRITICAL │
│   │ (monthly budget execution)       │          │          │
├───┼──────────────────────────────────┼──────────┼──────────┤
│ 3 │ Deploy Deadline Reminder System  │ SIMPLE   │ CRITICAL │
│   │ (Celery beat + email)            │          │          │
└───┴──────────────────────────────────┴──────────┴──────────┘


SHORT-TERM ENHANCEMENTS (Next 2 Sprints)
═══════════════════════════════════════════════════════

┌───┬──────────────────────────────────┬──────────┬──────────┐
│ # │ ACTION                           │ EFFORT   │ IMPACT   │
├───┼──────────────────────────────────┼──────────┼──────────┤
│ 4 │ Budget Call Automation           │ MODERATE │ HIGH     │
│   │ (auto-create draft PPAs)         │          │          │
├───┼──────────────────────────────────┼──────────┼──────────┤
│ 5 │ COA Audit Report Template        │ MODERATE │ HIGH     │
│   │ (annual audit compliance)        │          │          │
├───┼──────────────────────────────────┼──────────┼──────────┤
│ 6 │ Parliament Performance Reports   │ MODERATE │ HIGH     │
│   │ (quarterly PDF with narratives)  │          │          │
└───┴──────────────────────────────────┴──────────┴──────────┘


LONG-TERM IMPROVEMENTS (Future Cycle)
═══════════════════════════════════════════════════════

┌───┬──────────────────────────────────┬──────────┬──────────┐
│ # │ ACTION                           │ EFFORT   │ IMPACT   │
├───┼──────────────────────────────────┼──────────┼──────────┤
│ 7 │ PhilGEPS Integration             │ COMPLEX  │ MEDIUM   │
│   │ (procurement-budget linkage)     │          │          │
├───┼──────────────────────────────────┼──────────┼──────────┤
│ 8 │ Real-time Budget Dashboard       │ COMPLEX  │ MEDIUM   │
│   │ (public transparency portal)     │          │          │
├───┼──────────────────────────────────┼──────────┼──────────┤
│ 9 │ Budget Execution Auto-Init       │ MODERATE │ MEDIUM   │
│   │ (auto-create funding flows)      │          │          │
└───┴──────────────────────────────────┴──────────┴──────────┘
```

---

**Document Owner:** BICTO Project Management Team (OBCMS Platform)
**Visual Design Date:** October 5, 2025
**Last Updated:** October 6, 2025
**Companion Document:** BARMM_BUDGET_CYCLE_MAPPING.md

**Agency Coordination:**
- **MFBM**: Budget formulation, execution, fiscal policy oversight
- **BPDA**: Development planning, BDP alignment coordination
- **BICTO**: ICT infrastructure, OBCMS platform maintenance

---

**End of Visual Summary**
