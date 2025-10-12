# OBCMS Domain Architecture & Module Relationships

**Document:** 03-domain-architecture.md
**Last Updated:** 2025-10-12
**Purpose:** Understanding how OBCMS modules relate to each other and support the OOBC mission

---

## Table of Contents

1. [Mission Context](#mission-context)
2. [Core Domains](#core-domains)
3. [Module Interaction & Data Flow](#module-interaction--data-flow)
4. [User Workflows](#user-workflows)
5. [Business Logic](#business-logic)
6. [Cultural & Governance](#cultural--governance)

---

## Mission Context

### OOBC (Office for Other Bangsamoro Communities)

The OOBC serves **Other Bangsamoro Communities** (OBC) residing **outside the Bangsamoro Autonomous Region in Muslim Mindanao (BARMM)**.

**Geographic Scope:**
- **Region IX** - Zamboanga Peninsula
- **Region X** - Northern Mindanao
- **Region XI** - Davao Region
- **Region XII** - SOCCSKSARGEN

**Legal Mandate:**
- **Bangsamoro Organic Law (BOL)** - Constitutional basis
- **Bangsamoro Administrative Code** - Implementing guidelines
- **Moral Governance Principles** - Islamic values integration

**Mission:**
*"To ensure the rights, welfare, and development of Bangsamoro communities outside BARMM through evidence-based policy development, strategic coordination, and effective monitoring."*

---

## Core Domains

### 1. Communities Module (Know the Communities)

**Purpose:** *Comprehensive profiling enables targeted interventions*

#### Real-World Use Cases

**A. Demographic Profiling**
- Track **13 ethnolinguistic groups** (Maguindanaon, Tausug, Yakan, Sama, Maranao, etc.)
- Monitor vulnerable sectors (PWDs, solo parents, IDPs, farmers, fisherfolk)
- Document age demographics for targeted programs

**Example:**
> *"In Region XII, OOBC identifies 45 barangays with >70% Maguindanaon population facing high unemployment (>40%). This data triggers livelihood assessment (MANA) and partnership formation (Coordination) with BARMM Ministry of Agriculture."*

**B. Infrastructure Gap Analysis**
- Rate 10 infrastructure types (water, health, education, roads, etc.)
- Prioritize improvements based on community feedback
- Map facilities (mosques, madrasah, health centers)

**Example:**
> *"Municipality X shows 15 barangays without safe water access. OOBC uses this data to recommend policy for 'OBC Water Security Program' and coordinates with LGU + Department of Health for implementation."*

**C. Stakeholder Mapping**
- Document 14 stakeholder types (Imams, elders, ustadz, datus, chieftains, etc.)
- Track influence levels and engagement history
- Maintain contact information for consultations

**Example:**
> *"Before conducting MANA workshop in Province Y, facilitators review stakeholder database to invite elders (3), women leaders (5), youth representatives (4), and religious leaders (2) ensuring balanced representation."*

#### Primary Users
- OOBC Staff (data entry, analysis)
- Assessment Coordinators (baseline data for MANA)
- Policy Analysts (evidence gathering)

#### AI Features
- **Data validation** - Population consistency checks, ethnolinguistic verification
- **Needs classifier** - 12 categories with confidence scores
- **Community similarity** - Benchmarking and best practice sharing
- **Anomaly detection** - Flag unusual data patterns

---

### 2. MANA Module (Assess Needs & Context)

**Purpose:** *Evidence-based understanding of socio-economic-cultural conditions*

#### Two-System Architecture

**System 1: Legacy MANA (Staff Only)**
- Multi-assessment management
- Aggregate analysis across provinces/regions
- Desk reviews and secondary data synthesis

**System 2: Sequential Workshop System (Participants)**
- 5-workshop structured progression
- Community stakeholder input collection
- Culturally-sensitive facilitation

#### Real-World Use Cases

**A. Baseline Mapping**
- Collect comprehensive needs data (Social, Economic, Rights, Cultural)
- Document existing services and gaps
- Establish baseline for future M&E

**Example:**
> *"Region IX baseline (2024): 120 barangays assessed, identifying education gaps (45%), livelihood needs (67%), and cultural preservation priorities (38%). Data feeds into 3-year strategic plan."*

**B. Thematic Studies**
- Deep-dive assessments in specific sectors (health, education, livelihoods, cultural heritage)
- Specialized methodologies (KII, FGD, surveys)
- Expert-led analysis

**Example:**
> *"Healthcare Access Study (Region X): Identifies 4 municipalities with zero Bangsamoro healthcare workers. Recommendation triggers partnership with BARMM Ministry of Health for 'OBC Health Workforce Development Program'."*

**C. Participatory Assessment (5-Workshop Sequence)**

**Workshop 1:** Understanding Community Context
- Community history and demographics
- Cultural practices and traditions
- Existing resources and capacities

**Workshop 2:** Aspirations and Priorities
- Community vision for development
- Priority needs identification
- Resource mapping

**Workshop 3:** Collaboration and Empowerment
- Stakeholder analysis
- Partnership opportunities
- Community action planning

**Workshop 4:** Feedback on Existing Initiatives
- Review of government programs
- Assessment of effectiveness
- Recommendations for improvement

**Workshop 5:** Needs, Challenges, Factors, Outcomes
- Comprehensive needs validation
- Root cause analysis
- Expected outcomes definition

**Example:**
> *"Province Y MANA (50 participants): 5 workshops completed over 3 months. AI synthesis generates 12 priority recommendations across 4 themes (Social, Economic, Rights, Cultural). Provincial-level report submitted to OOBC ED for policy development."*

#### Primary Users
- **Facilitators** - Manage workshop progression, generate syntheses
- **Participants** - Community representatives (elders, women leaders, youth)
- **OOBC Staff** - Analyze findings, develop recommendations

#### AI Features
- **Response analysis** - Theme extraction, sentiment analysis
- **Needs extraction** - 10 categories auto-identified
- **Auto-report generation** - Executive summaries, findings
- **Cultural validation** - Bangsamoro appropriateness checking
- **Meeting intelligence** - Summarization, action items

---

### 3. Coordination Module (Mobilize Partnerships)

**Purpose:** *Whole-of-government approach via BMOA/LGU/NGA collaboration*

#### Real-World Use Cases

**A. Stakeholder Engagement**
- Track consultations, meetings, field visits across **10 engagement types**
- Document attendance, outcomes, satisfaction ratings
- Follow-up management and action item tracking

**Example:**
> *"Quarterly Coordination Meeting (Region XII): 15 organizations attend (4 BMOAs, 6 LGUs, 3 NGAs, 2 CSOs). OOBC presents MANA findings on education gaps. Commitment secured: BARMM Ministry of Basic Education allocates 5 scholarships per municipality for OBC students. Partnership agreement drafted (6-month timeline)."*

**B. Partnership Management**
- Manage **9 partnership types** (MOA, MOU, contracts, grants, joint programs)
- Track **12 status states** (concept → active → completed/expired)
- Monitor milestones, budget contributions, performance indicators

**Example:**
> *"MOA with BARMM Ministry of Agriculture (Active): 3-year livelihood program serving 8 municipalities in Region IX. Budget: ₱15M (BMOA: ₱10M, OOBC: ₱3M, LGU counterpart: ₱2M). Q1-2025 milestone: 250 farmers trained in halal agriculture. Status: On track (92% completion)."*

**C. MOA Coordination**
- Quarterly meetings with Bangsamoro ministries
- Focal person management (primary + alternate)
- Service delivery commitment tracking

**Example:**
> *"BMOA Focal Network (12 ministries): Each ministry designates primary and alternate focal persons. OOBC maintains contact database, schedules quarterly coordination, tracks service delivery commitments per ministry (health: 5 commitments, education: 8 commitments, agriculture: 6 commitments)."*

**D. Communication Tracking**
- Document **15 communication types** (email, letter, memo, meeting, phone, etc.)
- Direction tracking (incoming/outgoing/internal)
- Priority levels and response deadlines

**Example:**
> *"Endorsement Letter to Chief Minister Office (Outgoing): OOBC ED transmits 5 policy recommendations with 31+ evidence citations. Priority: HIGH. Response deadline: 30 days. Status: Received by OCM (Week 2), under review by Bangsamoro Parliament Legal Committee (Week 4)."*

**E. Resource Booking**
- Schedule vehicles, equipment, meeting rooms, facilitators
- Conflict detection for double-booking prevention
- Calendar integration for organization-wide visibility

**Example:**
> *"Field Visit to Region XI (Week 3): OOBC books 2 vehicles (March 15-17), 1 facilitator (Ustadz Ahmad), 1 meeting room at provincial office (March 16, 2-4 PM). System detects: Vehicle A conflict (already booked March 15). Alternative suggested: Vehicle C (available)."*

#### Primary Users
- **OOBC Coordination Officers** - Manage inter-agency relationships
- **MOA Focal Persons** - Primary and alternate contacts from BARMM agencies
- **LGU Representatives** - Local government coordination
- **NGA Partners** - National government collaboration

#### AI Features
- **Stakeholder matching** - Multi-criteria similarity
- **Partnership success prediction** - ML-based scoring
- **Meeting summarization** - Key points, action items
- **Auto-task creation** - From meeting transcripts
- **Resource optimization** - Booking recommendations

---

### 4. Policies Module (Recommend Solutions)

**Purpose:** *Transform evidence into actionable, culturally-appropriate recommendations*

#### Real-World Use Cases

**A. Evidence Synthesis**
- Aggregate data from Communities, MANA, Coordination modules
- Minimum **31+ citations** per recommendation
- Cross-reference existing policies for gaps

**Example:**
> *"Policy Recommendation: 'OBC Livelihood Support Program' - Evidence base: 12 MANA assessments (unemployment rate >40% in 45 barangays), 8 coordination meetings (stakeholder consensus), 5 community profiles (farmer/fisherfolk demographics), 3 MOA commitments (Agriculture, Trade, Finance), 2 existing policy gaps identified."*

**B. Policy Drafting**
- Develop recommendations (targeted or clustered/thematic)
- 4 categories: Social, Economic, Rights, Cultural
- Compliance with BOL and Bangsamoro Administrative Code

**Example:**
> *"Targeted Recommendation: 'Madrasah Support Act' - Addresses lack of government recognition and funding for OBC madrasah. Cultural alignment: Respects Islamic education traditions. Legal compliance: Aligned with BOL Article VII (Education) and BAC Section 12 (Cultural Heritage)."*

**C. Impact Assessment**
- Simulate **4 scenarios** (Optimistic, Realistic, Pessimistic, Community-Led)
- Budget projections and beneficiary estimates
- Risk analysis and mitigation strategies

**Example:**
> *"Impact Simulation: 'OBC Health Worker Program' - Optimistic: 50 healthcare workers trained (Year 1), 200 workers (Year 3), ₱25M budget. Realistic: 30 workers (Year 1), 120 workers (Year 3), ₱18M budget. Pessimistic: 15 workers (Year 1), 60 workers (Year 3), ₱12M budget. Community-Led: 25 workers (Year 1, volunteer-based), 100 workers (Year 3), ₱8M budget."*

**D. Prioritization**
- **Category A** (High Importance/High Urgency) - Critical, immediate-impact measures
- **Category B** (High Importance/Low Urgency) - Essential, phased interventions
- **Category C** (Low Importance/Low Urgency) - Supportive, future-oriented proposals

**Example:**
> *"Prioritization (Q1-2025): Category A (5 recommendations - education, health, livelihoods), Category B (8 recommendations - infrastructure, cultural preservation), Category C (3 recommendations - research, documentation)."*

**E. Endorsement Workflow**
1. **Preliminary Assessment** - Review MANA, consultations, existing policies
2. **Formulation** - Draft policy options with evidence
3. **Validation** - Stakeholder feedback loops
4. **Prioritization** - A/B/C categorization
5. **Endorsement** - OOBC ED → Office of Chief Minister → Bangsamoro Parliament

**Example:**
> *"Policy Lifecycle: 'OBC Education Support Act' - Formulation (Month 1-2), Validation via 3 stakeholder consultations (Month 3), Prioritization as Category A (Month 4), OOBC ED endorsement (Month 5), OCM review (Month 6), Bangsamoro Parliament first reading (Month 7)."*

#### Primary Users
- **Policy Officers** - Draft and refine recommendations
- **OOBC Executive Director** - Review and endorse
- **Chief Minister Office** - Receive and approve
- **Bangsamoro Parliament** - Legislative action

#### AI Features
- **Cross-module evidence gathering** - 31+ citations auto-collected
- **AI policy generation** - Culturally appropriate drafts
- **Impact simulation** - 4 scenarios modeled
- **BARMM compliance checking** - BOL/BAC alignment
- **Evidence synthesis** - Summarization and coherence

---

### 5. M&E Module (Track Impact & Accountability)

**Purpose:** *Ensure services reach OBCs, budgets are utilized, outcomes achieved*

#### Real-World Use Cases

**A. PPA Tracking (Programs, Projects, Activities)**
- Monitor ministry/agency projects serving OBCs
- Track allocations, utilization, variances
- Performance dashboard with KPIs, milestones, delivery timelines

**Example:**
> *"BARMM Ministry of Agriculture PPA: 'Halal Livelihood Program' - Budget: ₱10M (allocated), ₱8.2M (utilized 82%), ₱1.8M (remaining). Timeline: Q1-Q4 2025. Milestones: Q1 (250 farmers trained - COMPLETED), Q2 (500 farmers trained - IN PROGRESS 60%), Q3 (Market linkage - PENDING). Alert: Q2 milestone at risk (70% complete with 15 days remaining)."*

**B. Budget Monitoring**
- Track allocations vs utilization
- Variance analysis (over/under spending)
- Early warning system for delays/overruns

**Example:**
> *"Budget Alert: Ministry of Health 'OBC Mobile Clinic Program' - Budget: ₱5M, Utilized: ₱2.1M (42%), Timeline: 60% elapsed. Alert triggered: Utilization rate significantly below timeline progress. Recommendation: Expedite procurement or reallocate to avoid fund reversal."*

**C. Impact Evaluation**
- Measure outcomes against baselines (from MANA)
- Beneficiary tracking by community
- Before/after comparative analysis

**Example:**
> *"Impact Evaluation: 'OBC Water Security Program' (Region XII) - Baseline (2023): 15 barangays without safe water access. Post-implementation (2025): 12 barangays now have potable water systems. Beneficiaries: 8,500 individuals (3,200 households). Outcome: 80% reduction in waterborne diseases (health center data)."*

**D. Alert System**
- Flag delays, budget overruns, quality issues
- Automated notifications to MOA focal persons
- Risk scoring (low, medium, high, critical)

**Example:**
> *"Critical Alert: 'OBC Scholarship Program' - Risk: HIGH - Disbursement delayed 45 days beyond schedule. 120 students affected. Impact: Potential dropout (15 students at risk). Action: OOBC convenes emergency coordination meeting with BARMM Ministry of Basic Education. Resolution: Express disbursement approved (3-day timeline)."*

#### Primary Users
- **OOBC M&E Officers** - Monitor all initiatives
- **MOA Staff** - Report on their agency's PPAs
- **OOBC Executives** - Strategic oversight
- **Policy Officers** - Use M&E data for future recommendations

#### AI Features
- **Budget anomaly detection** - 95%+ accuracy
- **Timeline delay prediction** - Proactive alerts
- **Automated M&E reporting** - Quarterly reports generated
- **Performance forecasting** - 70-75% accuracy
- **Risk analysis** - Early warning system

---

### 6. Staff Management Module (Operational Excellence)

**Purpose:** *Efficient internal operations enable effective external service delivery*

#### Real-World Use Cases

**A. Profile Management**
- Job descriptions, competencies (core, leadership, functional)
- Performance targets (individual, team, office-wide)
- Qualifications and certifications

**Example:**
> *"Staff Profile: Coordination Officer II - KRAs: (1) MOA partnership management, (2) Quarterly coordination meetings, (3) Communication tracking. Performance targets: 12 partnerships maintained (Q1-Q4), 4 coordination meetings facilitated, 85%+ satisfaction rating from partners."*

**B. Team Coordination**
- Operational teams with focus areas (strategy, implementation, monitoring)
- Team leads and membership roles
- Cross-functional collaboration

**Example:**
> *"M&E Team: 5 members (1 lead, 4 members) - Focus: Monitoring MOA PPAs, performance reporting. Q1-2025 deliverables: 12 MOA performance reports, 3 impact evaluations, 1 comprehensive M&E report to OOBC ED."*

**C. Task Management**
- Integrated kanban system for work items
- Hierarchical task structure (projects → activities → tasks)
- Status workflow (pending → in_progress → completed)

**Example:**
> *"Project: 'Region IX MANA Campaign' - 15 activities, 45 tasks. Status: 12 activities completed, 3 in progress. Q1 milestone: 50 participants registered (ACHIEVED 100%), 5 workshops facilitated (IN PROGRESS 60%)."*

**D. Training Tracking**
- Capacity building programs and enrollments
- Competency development pathways
- Certification and completion status

**Example:**
> *"Training Program: 'MANA Facilitation Masterclass' - 10 staff enrolled, 8 completed (80% completion rate). Competencies covered: Culturally-sensitive facilitation, data analysis, AI synthesis tools. Post-training assessment: Average score 87% (target: 80%)."*

**E. Leave Management**
- Vacation, sick leave, official business tracking
- Calendar integration for resource planning
- Balance tracking and approval workflow

**Example:**
> *"Leave Request: Coordination Officer (5 days vacation, March 10-14) - Impact: 2 coordination meetings scheduled during leave. Action: Team lead reassigns meetings to alternate officer. Calendar updated, resource booking adjusted (vehicle A released, meeting room cancelled)."*

#### Primary Users
- **OOBC Staff** - All staff members
- **HR Officers** - Personnel management
- **Team Leads** - Task assignment
- **Executives** - Performance monitoring

#### AI Features
- **Conversational AI chat** - Natural language data queries
- **Multi-turn conversations** - Context-aware responses
- **Intent classification** - Auto-suggestions for common tasks
- **Data exploration** - Visualizations and insights

---

## Module Interaction & Data Flow

### Evidence-Based Cycle

```
1. COMMUNITIES → MANA
   └─ Baseline profiles feed assessment design
   └─ Geographic boundaries define coverage
   └─ Stakeholder lists identify participants

2. MANA → POLICIES
   └─ Findings become policy evidence (31+ citations)
   └─ Consultation feedback validates recommendations
   └─ Prioritized needs inform policy objectives

3. POLICIES → COORDINATION
   └─ Recommendations trigger partnership formation
   └─ Implementation requires MOA/LGU/NGA coordination
   └─ Service delivery tracked via partnerships

4. COORDINATION → M&E
   └─ Partnership activities become monitored PPAs
   └─ Resource allocations tracked against budgets
   └─ Delivery timelines generate performance data

5. M&E → COMMUNITIES (Feedback Loop)
   └─ Impact data updates community profiles
   └─ Lessons learned inform future assessments
   └─ Performance gaps trigger new recommendations
```

### Cross-Module Data Dependencies

**Communities ↔ MANA:**
- `Assessment.community` → `OBCCommunity` (one assessment per community)
- `WorkshopParticipantAccount.user` → Community stakeholders
- Geographic layers link to barangays/municipalities

**MANA ↔ Coordination:**
- `StakeholderEngagement.related_assessment` → `Assessment`
- Workshop findings inform engagement strategies
- Coordination notes document MANA-related meetings

**Coordination ↔ Policies:**
- Partnership agreements operationalize policy recommendations
- MOA/LGU commitments tracked as policy implementation actions
- Communication records provide evidence for policy reviews

**Communities ↔ M&E:**
- PPA beneficiaries linked to specific OBC communities
- Project locations mapped to barangays/municipalities
- Impact metrics update community needs status

**All Modules → Calendar System:**
- `WorkItem` model (unified work hierarchy) links events, tasks, activities
- `CalendarResource` enables cross-module resource booking
- `RecurringEventPattern` supports scheduled engagements

---

## User Workflows

### Workflow 1: Addressing Livelihood Needs (OOBC Staff)

**Scenario:** Region XII unemployment crisis (45 barangays, >40% unemployment rate)

**Step 1: Communities Module**
```
Action: Query barangay profiles for unemployment data
Outcome: 45 barangays identified, 67% primary livelihood = agriculture/fishing
```

**Step 2: MANA Module**
```
Action: Design livelihood assessment targeting fisherfolk and farmers
Outcome: 120 participants enrolled (elders, farmers, fisherfolk leaders, women)
```

**Step 3: Coordination Module**
```
Action: Engage BARMM Ministry of Agriculture, LGU officials, NGO partners
Outcome: 3 coordination meetings, commitment secured (livelihood training program)
```

**Step 4: Policies Module**
```
Action: Draft recommendation for "OBC Livelihood Support Program"
Outcome: Policy endorsed by OOBC ED, submitted to OCM
```

**Step 5: M&E Module**
```
Action: Track implementation once approved (budget, timelines, beneficiaries)
Outcome: Q1 milestone (250 farmers trained) achieved, Q2 milestone in progress
```

---

### Workflow 2: MOA Focal Person Reporting (MOA Staff)

**Scenario:** BARMM Ministry quarterly services reporting

**Step 1: User Account**
```
Action: Login as MOA staff (linked to `moa_organization`)
Outcome: Dashboard shows ministry's PPAs and reporting deadlines
```

**Step 2: M&E Module**
```
Action: Report PPAs delivered to OBCs (view-only for non-MOA PPAs)
Outcome: 5 PPAs updated (budget utilization, beneficiary counts, milestones)
```

**Step 3: Coordination Module**
```
Action: Update partnership milestones, submit communication records
Outcome: 2 partnerships updated, 1 meeting minute submitted
```

**Step 4: Policies Module**
```
Action: Review recommendations relevant to ministry (read-only)
Outcome: 3 recommendations noted, feedback provided via coordination meeting
```

**Step 5: Staff Module**
```
Action: Participate in quarterly coordination meeting (via calendar)
Outcome: Meeting attendance logged, action items assigned
```

---

### Workflow 3: MANA Facilitator Conducting Workshop (Facilitator)

**Scenario:** Regional workshop in Zamboanga Peninsula (50 participants)

**Step 1: MANA Module**
```
Action: Import 50 participants (elders, women leaders, youth)
Outcome: Participant accounts created, credentials distributed
```

**Step 2: Communities Module**
```
Action: Verify participant barangays/municipalities for coverage analysis
Outcome: 15 barangays represented across 5 municipalities
```

**Step 3: MANA Workshops**
```
Action: Facilitate 5 sequential workshops, monitor 85%+ submission rate
Outcome: Workshop 1 (98% completion), Workshop 2 (92%), Workshop 3 (88%)...
```

**Step 4: AI Synthesis**
```
Action: Generate province-level and stakeholder-type insights
Outcome: 12 priority needs identified, 4 themes synthesized (SERC)
```

**Step 5: Coordination Module**
```
Action: Document workshop as `StakeholderEngagement` activity
Outcome: Engagement logged, attendance recorded, satisfaction rating 4.5/5
```

**Step 6: Policies Module**
```
Action: Submit findings to policy team for recommendation development
Outcome: Findings feed 3 policy recommendations (education, health, livelihood)
```

---

### Workflow 4: Community Leader Accessing System (Community Leader)

**Scenario:** OBC representative monitoring community profile

**Step 1: User Account**
```
Action: Login as `community_leader` (limited access)
Outcome: Dashboard shows own community profile, relevant announcements
```

**Step 2: Communities Module**
```
Action: View own community profile (read-only)
Outcome: Review population, demographics, infrastructure ratings, stakeholder list
```

**Step 3: MANA Workshops**
```
Action: Complete assigned workshops (if registered as participant)
Outcome: Workshop 1 completed, Workshop 2 unlocked
```

**Step 4: Coordination Module**
```
Action: Receive engagement invitations, provide feedback
Outcome: RSVP to coordination meeting, submit pre-meeting feedback form
```

**Step 5: Dashboard**
```
Action: View relevant announcements, calendar events
Outcome: 2 upcoming events (coordination meeting, training opportunity)
```

---

## Business Logic

### 1. Geographic Hierarchy (Auto-Aggregation)

```
Region → Province → Municipality → Barangay → OBC Community

Auto-sync workflow:
1. Update barangay OBC profile
2. Trigger municipal coverage sync (total population, covered barangays)
3. Trigger provincial coverage sync (total population, covered municipalities)
4. Update regional dashboard (aggregate statistics)
```

**Unattributed Population Tracking:**
- Municipal coverage total vs sum of barangay OBCs
- Identifies gaps in barangay-level mapping
- Flags data quality issues

**Soft-Delete:**
- Archived records preserved for historical analysis
- `is_deleted=True` excludes from active queries
- Enables data recovery if needed

---

### 2. Sequential Workshop Progression (MANA)

```
Workshop 1 (UNLOCKED) → Complete → Auto-unlock Workshop 2 → Repeat until Workshop 5
```

**Gated Access:**
- Cannot skip workshops (enforced via `WorkshopAccessManager`)
- Prevents data quality issues (incomplete context)
- Ensures proper facilitation sequence

**Read-Only Completed:**
- Past workshops accessible for review, not editing
- Preserves data integrity
- Allows participants to reference previous inputs

**Facilitator Override:**
- Manual unlock/reset capabilities for exceptional cases
- Logged for audit trail
- Requires supervisor approval

---

### 3. Partnership Lifecycle (Coordination)

```
Concept → Draft → Review → Negotiation → Pending Signature → Active → Completed/Expired
```

**Milestone Tracking:**
- Deliverables, payments, reviews linked to timeline
- Auto-alerts for approaching deadlines
- Status indicators (on track, at risk, delayed)

**Signatory Management:**
- Multiple signatories per organization
- Approval workflow (sequential or parallel)
- Digital signature support (future)

**Document Versioning:**
- Amendments, addendums, appendices tracked separately
- Version history maintained
- Access control (confidential/public)

---

### 4. Policy Prioritization (Policies)

**Category A (High Importance/High Urgency):**
- Critical, immediate-impact measures
- Fast-track approval process
- Quarterly review cycle

**Category B (High Importance/Low Urgency):**
- Essential, phased interventions
- Standard approval process
- Semi-annual review cycle

**Category C (Low Importance/Low Urgency):**
- Supportive, future-oriented proposals
- Research and feasibility studies
- Annual review cycle

---

### 5. Unified Work Hierarchy (All Modules)

**WorkItem Model:** Single table for events, tasks, activities, workflows

**Polymorphic:**
- `work_type` field differentiates (event/task/activity/workflow)
- Shared attributes (status, priority, assignment, dates)
- Type-specific attributes in JSONField

**Hierarchical:**
- Parent-child relationships for subtasks (up to 5 levels)
- MPTT (Modified Preorder Tree Traversal) for efficient queries
- Cascading status updates (optional)

**Calendar Integration:**
- All work items appear in unified calendar view
- Resource booking linked to work items
- Recurrence patterns supported

---

## Cultural & Governance

### Cultural Sensitivity Framework

**13 Ethnolinguistic Groups:**
- Maguindanaon, Tausug, Yakan, Sama, Maranao, Kalibugan, Sangil, Molbog, Jama Mapun, Palawani, Iranun, Teduray, Lambangian
- System recognizes Bangsamoro diversity
- Custom fields per ethnolinguistic group (language, cultural practices)

**Islamic Facilities Tracking:**
- Mosques, madrasah, asatidz (teachers), ulama (scholars) counts
- Prayer times and Ramadan schedules
- Halal certification and Islamic finance tracking

**Traditional Leadership:**
- Respect for Imams, Elders, Ustadz, Datus, Chieftains
- Customary law integration (where applicable)
- Consensus-building facilitation protocols

**Language Support:**
- Multilingual (English, Filipino, Arabic, Maguindanaon, Maranao, Tausug)
- Translation services for policy documents
- Culturally-appropriate terminology

---

### Moral Governance Principles

**Transparency:**
- Audit trails across all modules
- Public access to non-sensitive data
- Open data initiatives

**Accountability:**
- User actions logged, decisions attributed
- Performance metrics published
- Complaint mechanisms accessible

**Equity:**
- Vulnerable sectors prioritized (women, youth, PWDs, IDPs)
- Geographic balance ensured (all 4 regions)
- Resource allocation fairness

**Participation:**
- Community voices central to assessments and consultations
- Stakeholder engagement mandated
- Feedback loops institutionalized

---

### Data Sovereignty

**Community Ownership:**
- OBCs retain control over their data
- Consent mechanisms for data sharing
- Right to review and correct data

**Consent Tracking:**
- Workshop participants consent recorded
- Data usage purposes disclosed
- Opt-out mechanisms available

**Access Restrictions:**
- Geographic boundaries enforced (staff access limited to assigned regions)
- Organizational boundaries enforced (MOA staff see only their PPAs)
- Role-based permissions granular

---

## Conclusion

The OBCMS domain architecture is **evidence-based, community-centered, and mission-aligned**. Each module serves a distinct purpose while contributing to the unified goal:

**"Enhancing the welfare of Bangsamoro communities outside BARMM through data-driven, culturally-sensitive, collaborative governance."**

### Key Success Factors

1. **Evidence-Based Cycle** - Communities → MANA → Policies → Coordination → M&E → (feedback) Communities
2. **Role-Based Access** - Right people, right data, right time
3. **AI-Augmented** - Intelligent automation enhances (not replaces) human judgment
4. **Culturally-Sensitive** - Islamic values, Bangsamoro traditions, moral governance
5. **Mission-Aligned** - Every feature serves OOBC statutory mandate

---

## Related Documentation

- [User-Facing Organization](01-user-facing-organization.md) - Navigation and user flows
- [Technical Organization](02-technical-organization.md) - Django app structure
- [Module Navigation Mapping](04-module-navigation-mapping.md) - Quick reference

---

**Last Updated:** 2025-10-12
**Mission:** Office for Other Bangsamoro Communities (OOBC)
**Legal Basis:** Bangsamoro Organic Law (BOL) + Bangsamoro Administrative Code
