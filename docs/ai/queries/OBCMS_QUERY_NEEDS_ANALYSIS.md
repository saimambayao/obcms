# OBCMS Query Needs Analysis

**Document Status**: DRAFT
**Date**: October 6, 2025
**Purpose**: Comprehensive analysis of OBCMS data models and user query patterns to identify high-priority query templates for implementation

---

## Executive Summary

This analysis examines OBCMS data models, user needs, and existing query template coverage (151 templates across 7 categories) to identify gaps and prioritize new query templates for implementation. The analysis reveals:

- **Current Coverage**: Strong coverage for basic counts and lists, but gaps in cross-domain queries, aggregates, and analytical insights
- **High-Priority Gap**: Cross-model relationship queries (e.g., communities → needs → PPAs → budget flows)
- **Quick Wins Identified**: 25+ high-value, low-complexity queries ready for immediate implementation
- **Strategic Opportunities**: Evidence-based budgeting queries linking needs, policies, and projects

---

## 1. Data Model Analysis

### 1.1 Core Domain Models

#### **Communities Module** (Primary: OBCCommunity)
**Key Models:**
- `OBCCommunity` - Core community profiles with 100+ demographic/socioeconomic fields
- `MunicipalityCoverage` - Municipality-level aggregations
- `ProvinceCoverage` - Province-level aggregations
- `Stakeholder` - Community leaders, religious figures, teachers (1,300+ entries)
- `CommunityLivelihood` - Livelihood activities by community
- `CommunityInfrastructure` - Infrastructure availability tracking
- `GeographicDataLayer` - GIS/mapping data layers
- `SpatialDataPoint` - Individual spatial points (facilities, sites)

**Queryable Relationships:**
```python
OBCCommunity
  ├─→ barangay → municipality → province → region (geographic hierarchy)
  ├─→ stakeholders (community leaders, religious figures)
  ├─→ livelihoods (agriculture, fishing, trade, etc.)
  ├─→ infrastructure (water, electricity, health, education)
  ├─→ assessments (MANA workshops)
  ├─→ stakeholder_engagements (coordination activities)
  ├─→ monitoring_entries (PPAs benefiting community)
  └─→ geographic_layers (GIS data)
```

**Aggregate-Worthy Fields:**
- **Demographics**: `estimated_obc_population`, `households`, `families`
- **Age Groups**: `children_0_9`, `adolescents_10_14`, `youth_15_30`, `adults_31_59`, `seniors_60_plus`
- **Vulnerable Sectors**: `women_count`, `pwd_count`, `idps_count`, `solo_parents_count`, `farmers_count`, `fisherfolk_count`, `unemployed_count`
- **Organizations**: `csos_count`, `associations_count`, `number_of_cooperatives`, `number_of_micro_enterprises`
- **Religious/Cultural**: `mosques_count`, `madrasah_count`, `asatidz_count`, `religious_leaders_count`

#### **MANA Module** (Mapping & Needs Assessment)
**Key Models:**
- `Assessment` - Workshops, surveys, field visits (UUID primary key)
- `AssessmentCategory` - Needs assessment, baseline study, impact assessment
- `AssessmentTeamMember` - Team roles (team leader, facilitator, documenter)
- `Survey` - Survey instruments within assessments
- `Need` - Identified community needs (infrastructure, livelihood, education, health)

**Queryable Relationships:**
```python
Assessment
  ├─→ community (OBCCommunity) [nullable - can be regional/provincial]
  ├─→ region/province/municipality/barangay (flexible geographic scope)
  ├─→ category (AssessmentCategory)
  ├─→ lead_assessor (User)
  ├─→ team_members (through AssessmentTeamMember)
  ├─→ needs (Need) - identified community needs
  ├─→ stakeholder_engagements (coordination activities)
  └─→ monitoring_entries (resulting PPAs)

Need
  ├─→ assessment (Assessment)
  ├─→ implementing_ppas (MonitoringEntry) - PPAs addressing this need
  └─→ communities (OBCCommunity) - affected communities
```

**Critical Fields:**
- **Status**: `planning`, `preparation`, `data_collection`, `analysis`, `reporting`, `completed`, `cancelled`
- **Priority**: `low`, `medium`, `high`, `critical`
- **Level**: `regional`, `provincial`, `city_municipal`, `barangay`, `community`
- **Methodology**: `desk_review`, `survey`, `kii`, `workshop`, `participatory`, `observation`, `mixed`
- **Timeline**: `planned_start_date`, `planned_end_date`, `actual_start_date`, `actual_end_date`
- **Budget**: `estimated_budget`, `actual_budget`

#### **Coordination Module** (Partnerships & Stakeholder Engagement)
**Key Models:**
- `Organization` - MOAs, NGOs, CSOs, LGUs (500+ organizations)
- `StakeholderEngagement` - Consultations, meetings, workshops (UUID primary key)
- `Partnership` - Multi-stakeholder agreements
- `EngagementFacilitator` - Staff facilitating engagements

**Queryable Relationships:**
```python
StakeholderEngagement
  ├─→ community (OBCCommunity)
  ├─→ engagement_type (StakeholderEngagementType)
  ├─→ related_assessment (Assessment) [nullable]
  ├─→ facilitators (User through EngagementFacilitator)
  ├─→ recurrence_pattern (RecurringEventPattern) [if recurring]
  └─→ funding_flows (budget tracking)

Organization
  ├─→ monitoring_entries (as lead/supporting/implementing)
  ├─→ partnerships (multi-stakeholder agreements)
  └─→ stakeholder_engagements (hosted/attended)
```

**Critical Fields:**
- **Status**: `planned`, `scheduled`, `in_progress`, `completed`, `postponed`, `cancelled`
- **Priority**: `low`, `medium`, `high`, `critical`
- **Participation Level**: `inform`, `consult`, `involve`, `collaborate`, `empower`
- **Attendance**: `target_participants`, `actual_participants`
- **Budget**: `budget_allocated`, `actual_cost`
- **Satisfaction**: `satisfaction_rating` (1-5 stars)

#### **Project Central / Monitoring Module** (PPAs)
**Key Models:**
- `MonitoringEntry` - Core PPA model (Projects/Programs/Activities) (UUID primary key)
- `BudgetApprovalStage` - Budget approval workflow tracking
- `BudgetCeiling` - Sector/fiscal year budget limits
- `FundingFlow` - Allocations, obligations, disbursements
- `StandardOutcomeIndicator` - Outcome indicators (SDG-aligned)

**Queryable Relationships:**
```python
MonitoringEntry (PPA)
  ├─→ lead_organization (Organization) - primary implementer
  ├─→ supporting_organizations (Organization) - partners
  ├─→ implementing_moa (Organization) - MOA responsible
  ├─→ submitted_by_community (OBCCommunity) [if community request]
  ├─→ communities (OBCCommunity) - benefiting communities
  ├─→ submitted_to_organization (Organization) [if request]
  ├─→ related_assessment (Assessment) - originating MANA workshop
  ├─→ needs_addressed (Need) - community needs addressed
  ├─→ implementing_policies (PolicyRecommendation) - policies implemented
  ├─→ funding_flows (FundingFlow) - budget allocations/disbursements
  ├─→ standard_outcome_indicators (StandardOutcomeIndicator) - SDG tracking
  └─→ approval_stages (BudgetApprovalStage) - approval workflow
```

**Critical Fields:**
- **Category**: `moa_ppa` (MOA project), `oobc_ppa` (OOBC-led), `obc_request` (community request)
- **Status**: `planning`, `ongoing`, `completed`, `on_hold`, `cancelled`
- **Request Status**: `submitted`, `under_review`, `endorsed`, `approved`, `in_progress`, `completed`, `declined`
- **Priority**: `low`, `medium`, `high`, `urgent`
- **Sector**: `economic`, `social`, `infrastructure`, `environment`, `governance`, `peace_security`
- **Budget**: `budget_allocation`, `budget_utilized`, `budget_variance`
- **Funding**: `funding_source` (GAA, block grant, LGU, donor)
- **Timeline**: `plan_year`, `fiscal_year`, `start_date`, `target_completion_date`
- **Progress**: `progress` (0-100%)

#### **Policy Tracking Module**
**Key Models:**
- `PolicyRecommendation` - Evidence-based policy proposals
- `PolicyDocument` - Policy documents and resolutions
- `PolicyAdoptionStage` - Adoption tracking

**Queryable Relationships:**
```python
PolicyRecommendation
  ├─→ implementing_ppas (MonitoringEntry) - PPAs implementing policy
  ├─→ related_assessment (Assessment) - evidence base
  └─→ communities (OBCCommunity) - affected communities
```

---

## 2. User Query Patterns

### 2.1 Government Staff Personas

#### **Provincial Coordinators**
**Information Needs:**
- "How many communities in my province?"
- "Which communities have the highest poverty incidence?"
- "What PPAs are benefiting Maguindanaon communities?"
- "Show me completed assessments in Region XII"
- "Budget utilization by sector in my province"

#### **MOA Program Officers**
**Information Needs:**
- "List all infrastructure projects in Sultan Kudarat"
- "PPAs implemented by DSWD in FY 2024"
- "Community requests pending approval"
- "Average project completion rate by MOA"
- "Budget variance across economic development projects"

#### **MANA Coordinators**
**Information Needs:**
- "Assessments scheduled for next month"
- "Communities without recent assessments"
- "Top 10 priority needs identified across Region IX"
- "Assessment completion rate by team leader"
- "Needs assessment coverage by ethnolinguistic group"

#### **Executive Management**
**Information Needs:**
- "Total OBC population across all regions"
- "Budget allocation vs. utilization by sector"
- "High-priority PPAs at risk of delays"
- "Communities with critical infrastructure gaps"
- "Policy adoption rate by recommendation type"
- "ROI analysis: PPAs by cost-effectiveness rating"

### 2.2 Priority Query Types

#### **Tier 1: Mission-Critical (Daily Use)**
1. **Count & Aggregate Queries** - "How many X?" / "Total Y"
2. **Status Tracking** - "Show pending/ongoing/completed X"
3. **Location Filters** - "Communities/PPAs/Assessments in [location]"
4. **Budget Tracking** - "Budget allocated/utilized for X"
5. **Priority Flagging** - "High-priority/urgent items requiring attention"

#### **Tier 2: Decision Support (Weekly Use)**
1. **Cross-Domain Analysis** - "Communities with needs but no PPAs"
2. **Trend Analysis** - "Assessment completion trends over time"
3. **Gap Identification** - "Uncovered communities/sectors/needs"
4. **Performance Metrics** - "Average project duration/budget variance"
5. **Demographic Insights** - "Vulnerable sector distribution by location"

#### **Tier 3: Strategic Planning (Monthly/Quarterly)**
1. **Evidence-Based Budgeting** - "Needs → Policies → PPAs pipeline"
2. **Impact Assessment** - "Beneficiaries reached by sector"
3. **Resource Optimization** - "Cost per beneficiary by project type"
4. **Coverage Analysis** - "Geographic/demographic coverage gaps"
5. **Partnership Analysis** - "MOA collaboration patterns"

---

## 3. Gap Analysis

### 3.1 Current Template Coverage (151 Templates)

**Strong Coverage:**
- ✅ Communities: Basic counts (total, by location, by ethnicity)
- ✅ Communities: Simple lists (show communities, filter by attributes)
- ✅ MANA: Assessment counts and status queries
- ✅ Coordination: Engagement counts and upcoming events
- ✅ Projects: PPA counts by status/sector
- ✅ Staff: Task management and workflow queries
- ✅ Geography: Administrative unit counts (regions, provinces, municipalities, barangays)

**Moderate Coverage:**
- ⚠️ Communities: Aggregate demographics (population totals, age distributions)
- ⚠️ MANA: Assessment team performance metrics
- ⚠️ Coordination: Partnership analysis queries
- ⚠️ Projects: Budget tracking and variance analysis

**Critical Gaps:**
- ❌ **Cross-Domain Relationships**: Communities → Needs → PPAs (evidence-based budgeting)
- ❌ **Multi-Level Aggregations**: Province → Municipality → Barangay → Community rollups
- ❌ **Time-Series Analysis**: Trends over fiscal years, quarters, months
- ❌ **Comparative Analysis**: Regional/provincial comparisons, MOA performance benchmarking
- ❌ **Risk & Gap Identification**: Overdue projects, uncovered communities, unfunded needs
- ❌ **Impact Metrics**: Beneficiaries reached, cost per beneficiary, outcome achievement
- ❌ **Geographic Intelligence**: Spatial queries (distance, proximity, clustering)
- ❌ **Stakeholder Network Analysis**: Organization collaboration patterns
- ❌ **Budget Intelligence**: Ceiling utilization, allocation efficiency, variance patterns

### 3.2 Under-Served Domains

#### **Needs Management (Need Model)** - 0 templates
- No query templates exist for the `Need` model
- Critical for evidence-based budgeting: Needs → Policies → PPAs
- Missing: "Top 10 unmet needs", "Needs by sector/location", "Needs coverage analysis"

#### **Budget Tracking (FundingFlow Model)** - 2 templates
- Only basic budget allocation queries
- Missing: Disbursement tracking, tranche analysis, variance reports
- Missing: Budget ceiling enforcement, utilization rates, allocation efficiency

#### **Stakeholder Management (Stakeholder Model)** - 0 templates
- Rich community leader/religious figure data unused
- Missing: "Stakeholders by influence level", "Engagement history", "Network analysis"

#### **Infrastructure Tracking (CommunityInfrastructure Model)** - 0 templates
- Detailed infrastructure data (water, electricity, health, education) not queryable
- Missing: "Infrastructure coverage gaps", "Priority improvement areas", "Access ratings"

#### **Livelihood Analysis (CommunityLivelihood Model)** - 1 template
- Single count query for primary livelihood
- Missing: "Livelihood diversity", "Seasonal patterns", "Income levels", "Challenges analysis"

#### **Geographic Intelligence (GeographicDataLayer, SpatialDataPoint)** - 0 templates
- GIS/mapping data models exist but no query templates
- Missing: "Facilities within X km", "Service coverage analysis", "Spatial clustering"

### 3.3 Cross-Domain Query Gaps

**Evidence-Based Budgeting Pipeline:**
```
Assessments → Needs Identified → Policy Recommendations → PPAs Implemented → Budget Flows
```
- ❌ "Show PPAs addressing needs from Assessment X"
- ❌ "Needs identified but not yet addressed by any PPA"
- ❌ "PPAs implementing Policy Recommendation Y"
- ❌ "Budget allocated to needs in high-priority sectors"

**Community-Centric View:**
```
OBCCommunity → Stakeholders → Assessments → Needs → PPAs → Engagements
```
- ❌ "Community profile with all related activities"
- ❌ "Communities with assessments but no follow-up PPAs"
- ❌ "Stakeholder engagement frequency by community"

**MOA Performance Tracking:**
```
Organization → PPAs (lead/supporting) → Budget Flows → Outcome Indicators
```
- ❌ "MOA portfolio: all projects, total budget, completion rate"
- ❌ "MOA collaboration patterns: partnerships, joint PPAs"
- ❌ "Average project duration/budget by implementing MOA"

---

## 4. Priority Matrix

### 4.1 Quick Wins (High Value, Low Complexity)

#### **Needs Management** (Priority: CRITICAL)
1. ✅ `count_all_needs` - Total needs identified
2. ✅ `count_needs_by_sector` - Needs by sector (infrastructure, livelihood, education, health)
3. ✅ `count_needs_by_location` - Needs by region/province/municipality
4. ✅ `list_unmet_needs` - Needs without implementing PPAs
5. ✅ `list_top_priority_needs` - Needs by priority (critical, high)

**Implementation**: Simple filter/count queries, no complex joins
**Value**: Enables evidence-based budgeting, fills major gap
**Complexity**: LOW (1-2 days)

#### **Infrastructure Gaps** (Priority: HIGH)
6. ✅ `count_communities_by_infrastructure_type` - e.g., "How many communities with poor water access?"
7. ✅ `list_infrastructure_gaps` - Communities with critical infrastructure needs
8. ✅ `infrastructure_coverage_by_location` - Infrastructure availability by province

**Implementation**: Filter on `CommunityInfrastructure.availability_status` and `priority_for_improvement`
**Value**: Informs infrastructure planning decisions
**Complexity**: LOW (1 day)

#### **Livelihood Diversity** (Priority: HIGH)
9. ✅ `count_livelihoods_by_type` - Distribution of primary livelihoods
10. ✅ `list_communities_by_livelihood_challenges` - Communities facing livelihood issues
11. ✅ `livelihood_income_analysis` - Communities by income level from livelihood

**Implementation**: Aggregate on `CommunityLivelihood` model
**Value**: Supports economic development planning
**Complexity**: LOW (1 day)

#### **Stakeholder Network** (Priority: MEDIUM)
12. ✅ `count_stakeholders_by_type` - Community leaders, religious figures, youth leaders
13. ✅ `list_high_influence_stakeholders` - Stakeholders with high/very high influence
14. ✅ `stakeholder_engagement_frequency` - Active vs. inactive stakeholders

**Implementation**: Filter/aggregate on `Stakeholder` model
**Value**: Supports community engagement strategy
**Complexity**: LOW (1 day)

#### **Budget Ceiling Tracking** (Priority: HIGH)
15. ✅ `budget_ceiling_utilization` - Ceilings near/exceeding limits
16. ✅ `remaining_budget_by_sector` - Available budget under ceilings
17. ✅ `budget_ceiling_violations` - Allocations exceeding hard limits

**Implementation**: Use `BudgetCeiling.get_utilization_percentage()` and filters
**Value**: Prevents over-allocation, enforces fiscal discipline
**Complexity**: LOW (1 day)

#### **Cross-Domain Quick Wins** (Priority: HIGH)
18. ✅ `communities_with_assessments_but_no_ppas` - Gap identification
19. ✅ `needs_addressed_by_ppa_count` - PPAs by number of needs addressed
20. ✅ `ppas_by_implementing_policy` - PPAs implementing specific policy

**Implementation**: Simple joins with EXISTS/NOT EXISTS filters
**Value**: Reveals critical gaps in implementation pipeline
**Complexity**: LOW-MEDIUM (2 days)

#### **Demographic Intelligence** (Priority: MEDIUM)
21. ✅ `total_obc_population_by_region` - Population totals
22. ✅ `vulnerable_sector_distribution` - PWDs, IDPs, solo parents by location
23. ✅ `age_demographics_by_province` - Youth, seniors, children distribution
24. ✅ `average_household_size_by_location` - Household metrics

**Implementation**: Aggregate sums on demographic fields
**Value**: Supports demographic analysis and targeting
**Complexity**: LOW (1 day)

#### **Spatial Intelligence (Basic)** (Priority: MEDIUM)
25. ✅ `communities_with_coordinates` - Communities with GIS data
26. ✅ `spatial_points_by_type` - Facilities, mosques, schools by community
27. ✅ `communities_missing_coordinates` - GIS data gaps

**Implementation**: Filter on `latitude`/`longitude` NULL/NOT NULL
**Value**: Supports mapping and spatial planning
**Complexity**: LOW (1 day)

**Total Quick Wins: 27 queries | Estimated Implementation: 10-15 days**

---

### 4.2 Strategic Queries (High Value, High Complexity)

#### **Evidence-Based Budgeting Pipeline** (Priority: CRITICAL)
28. 🟡 `needs_to_ppas_pipeline` - Full pipeline: Assessment → Needs → Policies → PPAs → Budget
29. 🟡 `unfunded_needs_analysis` - High-priority needs without budget allocation
30. 🟡 `policy_implementation_rate` - % of policy recommendations with implementing PPAs
31. 🟡 `needs_coverage_by_sector` - Sector-wise needs addressed vs. unmet

**Implementation**: Multi-table joins (4-6 models), aggregation, conditional logic
**Value**: Core evidence-based budgeting capability
**Complexity**: HIGH (5-7 days each)

#### **MOA Performance Dashboards** (Priority: HIGH)
32. 🟡 `moa_portfolio_summary` - All PPAs, total budget, completion rate, beneficiaries
33. 🟡 `moa_budget_efficiency` - Cost per beneficiary, budget variance, utilization rate
34. 🟡 `moa_collaboration_matrix` - Partnership patterns, joint PPAs, supporting roles
35. 🟡 `moa_sector_specialization` - Primary sectors, project types, success rate

**Implementation**: Complex aggregations, subqueries, performance optimization
**Value**: MOA accountability and performance tracking
**Complexity**: HIGH (4-6 days each)

#### **Time-Series & Trend Analysis** (Priority: MEDIUM)
36. 🟡 `assessment_completion_trends` - Completion rate over time (monthly/quarterly)
37. 🟡 `ppa_implementation_timeline` - Average project duration by sector/MOA
38. 🟡 `budget_utilization_trends` - Disbursement patterns over fiscal years
39. 🟡 `stakeholder_engagement_frequency_trends` - Engagement patterns over time

**Implementation**: Date aggregations, time bucketing, trend calculations
**Value**: Predictive insights, planning optimization
**Complexity**: MEDIUM-HIGH (3-5 days each)

#### **Geographic Intelligence (Advanced)** (Priority: MEDIUM)
40. 🟡 `facilities_within_radius` - Facilities within X km of community
41. 🟡 `service_coverage_analysis` - Communities within service radius
42. 🟡 `spatial_clustering_analysis` - Identify OBC population clusters
43. 🟡 `infrastructure_proximity_analysis` - Distance to nearest health/education facility

**Implementation**: Spatial calculations, distance formulas, clustering algorithms
**Value**: Service delivery optimization, facility planning
**Complexity**: HIGH (4-6 days each)

#### **Impact & Outcome Tracking** (Priority: HIGH)
44. 🟡 `beneficiaries_reached_by_sector` - Total beneficiaries by PPA sector
45. 🟡 `cost_per_beneficiary_analysis` - ROI by project type
46. 🟡 `outcome_indicator_achievement` - SDG indicator progress
47. 🟡 `community_coverage_rate` - % of communities reached by PPAs

**Implementation**: Joins across PPAs, communities, outcome indicators, aggregations
**Value**: Impact reporting, SDG tracking, accountability
**Complexity**: MEDIUM-HIGH (4-5 days each)

#### **Risk & Gap Identification** (Priority: HIGH)
48. 🟡 `overdue_projects_risk_analysis` - Projects past target date, severity scoring
49. 🟡 `uncovered_communities_report` - Communities without assessments/PPAs/engagements
50. 🟡 `budget_variance_alerts` - Projects with significant cost overruns
51. 🟡 `approval_bottlenecks` - PPAs stuck in approval stages > X days

**Implementation**: Multi-criteria filtering, risk scoring, date calculations
**Value**: Proactive risk management, early intervention
**Complexity**: MEDIUM-HIGH (3-5 days each)

**Total Strategic Queries: 24 queries | Estimated Implementation: 90-120 days**

---

## 5. Specific Query Recommendations (Top 100)

### 5.1 Needs Management (12 queries)

#### **Basic Needs Queries** (Priority: CRITICAL)
1. `count_all_needs` - Total needs identified across all assessments
2. `count_needs_by_priority` - Needs by priority (critical, high, medium, low)
3. `count_needs_by_sector` - Needs by sector (infrastructure, livelihood, education, health, governance)
4. `count_needs_by_location` - Needs by region/province/municipality
5. `count_needs_by_status` - Needs by fulfillment status (unmet, partially met, met)

#### **Needs Analysis** (Priority: HIGH)
6. `list_unmet_needs` - Needs without any implementing PPAs
7. `list_partially_met_needs` - Needs with PPAs but not fully addressed
8. `list_top_priority_needs` - Top 20 highest-priority needs
9. `needs_by_assessment` - Needs identified in specific assessment
10. `needs_by_community` - All needs for specific community

#### **Cross-Domain Needs** (Priority: HIGH)
11. `needs_with_ppas` - Needs with implementing PPAs (show PPA count)
12. `needs_with_budget_allocation` - Needs with total budget allocated

**Example Natural Language Queries:**
- "How many critical needs have been identified?"
- "Show me unmet infrastructure needs in Region XII"
- "What needs were identified in the Cotabato assessment?"
- "List top 10 priority needs without any PPAs"
- "Total budget allocated to education needs"

---

### 5.2 Infrastructure Analysis (10 queries)

#### **Infrastructure Coverage** (Priority: HIGH)
13. `count_communities_by_water_access` - Communities by water access rating (poor, fair, good, excellent)
14. `count_communities_by_electricity_access` - Communities by electricity access
15. `count_communities_by_healthcare_access` - Communities by healthcare facility access
16. `count_communities_by_education_access` - Communities by school access
17. `count_communities_by_sanitation_access` - Communities by sanitation facility access

#### **Infrastructure Gaps** (Priority: HIGH)
18. `list_communities_poor_water` - Communities with poor/no water supply
19. `list_communities_poor_electricity` - Communities with poor/no electricity
20. `list_critical_infrastructure_gaps` - Communities with critical priority infrastructure needs
21. `infrastructure_coverage_by_province` - Infrastructure availability summary by province
22. `infrastructure_improvement_priorities` - Infrastructure items flagged for improvement

**Example Natural Language Queries:**
- "How many communities have poor water access?"
- "Show communities with no electricity in Zamboanga Peninsula"
- "List critical infrastructure gaps in Region X"
- "Infrastructure coverage summary for Sultan Kudarat"
- "Communities needing urgent healthcare facility improvements"

---

### 5.3 Livelihood & Economic Development (10 queries)

#### **Livelihood Distribution** (Priority: HIGH)
23. `count_livelihoods_by_type` - Distribution by livelihood type (agriculture, fishing, trade, etc.)
24. `count_primary_livelihoods_by_community` - Communities by primary livelihood
25. `count_seasonal_livelihoods` - Seasonal vs. year-round livelihoods
26. `livelihood_income_levels` - Communities by livelihood income level
27. `livelihood_participation_rate` - % of community involved in primary livelihood

#### **Livelihood Challenges** (Priority: MEDIUM)
28. `list_livelihood_challenges_by_type` - Common challenges by livelihood type
29. `list_communities_livelihood_opportunities` - Communities with identified opportunities
30. `livelihood_diversity_index` - Communities with multiple livelihood types
31. `economic_organizations_count` - Cooperatives, social enterprises, micro-enterprises by location
32. `unbanked_population_analysis` - Communities with high unbanked OBC population

**Example Natural Language Queries:**
- "How many communities rely on fishing as primary livelihood?"
- "Show communities with low-income livelihoods in Cotabato"
- "List challenges faced by farming communities"
- "Communities with diversified livelihood opportunities"
- "Cooperatives count by province"

---

### 5.4 Stakeholder & Community Leadership (10 queries)

#### **Stakeholder Distribution** (Priority: MEDIUM)
33. `count_stakeholders_by_type` - Community leaders, religious figures, youth leaders, etc.
34. `count_stakeholders_by_influence_level` - High, medium, low influence stakeholders
35. `count_stakeholders_by_engagement_level` - Active, moderate, limited engagement
36. `count_religious_leaders_by_community` - Ulama, Imams, Ustadz distribution
37. `count_community_organizations` - CSOs, associations by community

#### **Stakeholder Engagement** (Priority: MEDIUM)
38. `list_high_influence_stakeholders` - Stakeholders with high/very high influence
39. `list_inactive_stakeholders` - Stakeholders with limited/no engagement
40. `stakeholder_engagement_history` - Engagement activities by stakeholder
41. `stakeholders_by_expertise` - Stakeholders by special skills/expertise
42. `stakeholder_networks_analysis` - External networks and connections

**Example Natural Language Queries:**
- "How many religious leaders in Maguindanaon communities?"
- "Show high-influence stakeholders in Region IX"
- "List inactive community leaders needing re-engagement"
- "Stakeholders with agricultural expertise"
- "Community organizations in Sultan Kudarat province"

---

### 5.5 Budget & Financial Tracking (12 queries)

#### **Budget Allocation** (Priority: CRITICAL)
43. `total_budget_by_sector` - Total budget allocated by sector
44. `total_budget_by_fiscal_year` - Budget by fiscal year
45. `total_budget_by_funding_source` - Budget by GAA, block grant, LGU, donor
46. `total_budget_by_moa` - Budget by implementing MOA
47. `budget_allocation_vs_utilization` - Allocated vs. utilized by sector

#### **Budget Ceilings & Enforcement** (Priority: HIGH)
48. `budget_ceiling_utilization_by_sector` - % of ceiling utilized
49. `budget_ceilings_near_limit` - Ceilings at 90%+ utilization
50. `budget_ceiling_violations` - Allocations exceeding hard limits
51. `remaining_budget_by_sector` - Available budget under ceilings

#### **Funding Flows** (Priority: HIGH)
52. `funding_flow_by_tranche_type` - Allocations, obligations, disbursements
53. `disbursement_rate_by_ppa` - % of allocated budget disbursed
54. `budget_variance_analysis` - PPAs with significant over/under budget

**Example Natural Language Queries:**
- "Total budget allocated to infrastructure sector?"
- "Show budget utilization by sector for FY 2024"
- "Budget ceilings near limit for economic development"
- "Disbursement rate for DSWD projects"
- "PPAs with budget overruns > 20%"

---

### 5.6 Assessment & MANA (12 queries)

#### **Assessment Coverage** (Priority: HIGH)
55. `count_assessments_by_status` - Planning, data collection, completed, etc.
56. `count_assessments_by_level` - Regional, provincial, municipal, barangay, community
57. `count_assessments_by_methodology` - Survey, KII, workshop, participatory
58. `assessments_by_location` - Assessments in specific region/province
59. `assessments_by_date_range` - Assessments planned/completed in date range

#### **Assessment Performance** (Priority: MEDIUM)
60. `assessment_completion_rate_by_team_leader` - Completion % by lead assessor
61. `assessment_duration_analysis` - Average duration by methodology
62. `assessment_budget_variance` - Budget overruns/savings
63. `overdue_assessments` - Assessments past planned end date

#### **Assessment-Needs Linkage** (Priority: HIGH)
64. `needs_identified_per_assessment` - Average needs identified
65. `communities_without_recent_assessment` - Communities not assessed in last 12 months
66. `assessment_coverage_by_ethnicity` - Ethnolinguistic group coverage

**Example Natural Language Queries:**
- "How many assessments are in data collection phase?"
- "Show completed barangay-level assessments in Region X"
- "Assessments using participatory methodology"
- "Average needs identified per community assessment"
- "Tausug communities without assessment in 2024"
- "Team leaders with highest completion rate"

---

### 5.7 Coordination & Partnerships (10 queries)

#### **Stakeholder Engagement Tracking** (Priority: HIGH)
67. `count_engagements_by_type` - Consultations, meetings, workshops, FGDs
68. `count_engagements_by_status` - Planned, scheduled, completed, cancelled
69. `engagements_by_community` - All engagements for specific community
70. `engagements_by_date_range` - Upcoming/past engagements
71. `engagement_participation_rate` - Actual vs. target participants

#### **Partnership Analysis** (Priority: MEDIUM)
72. `count_organizations_by_type` - MOAs, NGOs, CSOs, LGUs, private sector
73. `organization_collaboration_count` - Organizations by number of partnerships
74. `moa_joint_projects` - PPAs with multiple implementing MOAs
75. `engagement_satisfaction_scores` - Average satisfaction by engagement type
76. `recurring_engagements_schedule` - Recurring coordination meetings

**Example Natural Language Queries:**
- "How many consultations scheduled for next month?"
- "Show all engagements with Tausug communities"
- "Organizations with most partnerships"
- "Average satisfaction score for FGDs"
- "Joint projects between DSWD and DepEd"

---

### 5.8 Projects & PPAs (16 queries)

#### **PPA Status & Progress** (Priority: CRITICAL)
77. `count_ppas_by_status` - Planning, ongoing, completed, on-hold, cancelled
78. `count_ppas_by_category` - MOA PPA, OOBC PPA, OBC request
79. `count_ppas_by_sector` - Economic, social, infrastructure, environment, etc.
80. `count_ppas_by_priority` - Low, medium, high, urgent
81. `ppas_by_location` - PPAs in specific region/province/municipality

#### **PPA Implementation** (Priority: HIGH)
82. `ppas_by_implementing_moa` - All PPAs by specific MOA
83. `ppas_by_benefiting_community` - PPAs targeting specific community
84. `overdue_ppas` - PPAs past target completion date
85. `ppas_by_progress_range` - PPAs 0-25%, 25-50%, 50-75%, 75-100%
86. `average_ppa_completion_time` - Average duration by sector/MOA

#### **PPA Budget Tracking** (Priority: HIGH)
87. `ppas_by_budget_range` - PPAs by budget size (small, medium, large)
88. `ppa_budget_variance_analysis` - PPAs with significant variance
89. `ppas_by_funding_source` - PPAs by GAA, block grant, donor, etc.
90. `ppa_disbursement_status` - Allocated vs. disbursed

#### **Cross-Domain PPA Queries** (Priority: HIGH)
91. `ppas_addressing_needs` - PPAs with linked needs
92. `ppas_implementing_policies` - PPAs implementing policy recommendations

**Example Natural Language Queries:**
- "How many PPAs are ongoing in Region XII?"
- "Show all infrastructure PPAs by DPWH"
- "OBC community requests pending approval"
- "Projects with > 50% budget variance"
- "PPAs past target completion date"
- "Average project duration for livelihood PPAs"

---

### 5.9 Demographics & Vulnerable Sectors (12 queries)

#### **Population Statistics** (Priority: HIGH)
93. `total_obc_population_by_region` - Population totals by region
94. `total_obc_population_by_province` - Population totals by province
95. `total_obc_population_by_ethnicity` - Population by ethnolinguistic group
96. `average_household_size_by_location` - Household metrics
97. `population_density_ranking` - Communities by OBC population size

#### **Age Demographics** (Priority: MEDIUM)
98. `youth_population_distribution` - Youth (15-30) by location
99. `children_population_distribution` - Children (0-9) by location
100. `seniors_population_distribution` - Seniors (60+) by location
101. `age_dependency_ratio` - Youth + seniors vs. working-age adults

#### **Vulnerable Sectors** (Priority: HIGH)
102. `pwd_count_by_location` - Persons with disabilities distribution
103. `idp_count_by_location` - Internally displaced persons
104. `solo_parents_count_by_location` - Solo parents distribution

**Example Natural Language Queries:**
- "Total OBC population in Region IX?"
- "Maguindanaon population across all regions"
- "Communities with highest youth population"
- "PWD count in Sultan Kudarat"
- "Communities with high IDP concentration"

---

### 5.10 Geographic & Spatial Intelligence (8 queries - Basic)

#### **GIS Data Coverage** (Priority: MEDIUM)
105. `communities_with_coordinates` - Communities with lat/long data
106. `communities_missing_coordinates` - GIS data gaps
107. `spatial_points_by_type` - Facilities, mosques, schools count
108. `geographic_layers_by_community` - GIS layers available

#### **Spatial Queries (Basic)** (Priority: MEDIUM)
109. `communities_by_proximity_to_barmm` - Adjacent, near, distant
110. `facilities_count_by_community` - Health, education, religious facilities
111. `communities_with_boundary_data` - Communities with GeoJSON boundaries
112. `mapping_coverage_gaps` - Communities needing GIS data collection

**Example Natural Language Queries:**
- "How many communities have GPS coordinates?"
- "Communities adjacent to BARMM boundaries"
- "Count of health facilities in Cotabato communities"
- "Communities missing boundary GeoJSON data"

---

## 6. Implementation Roadmap

### Phase 1: Quick Wins (Weeks 1-3)
**Focus**: High-value, low-complexity queries filling critical gaps
**Deliverables**: 27 query templates

**Week 1: Needs & Infrastructure**
- Needs management queries (5)
- Infrastructure gap queries (3)
- Implementation: 8 templates

**Week 2: Livelihoods & Stakeholders**
- Livelihood analysis queries (3)
- Stakeholder network queries (3)
- Budget ceiling tracking (3)
- Implementation: 9 templates

**Week 3: Cross-Domain & Demographics**
- Cross-domain quick wins (3)
- Demographic intelligence (4)
- Spatial intelligence (basic) (3)
- Implementation: 10 templates

**Testing & Validation**: End of Week 3
- Query performance optimization
- Response formatting standardization
- Integration testing with chat engine

---

### Phase 2: Strategic Queries (Weeks 4-8)
**Focus**: High-value, high-complexity queries enabling advanced analytics
**Deliverables**: 24 strategic query templates

**Week 4-5: Evidence-Based Budgeting**
- Needs → Policies → PPAs pipeline (4)
- Implementation: Complex joins, aggregations

**Week 6-7: MOA Performance & Time-Series**
- MOA portfolio dashboards (4)
- Trend analysis queries (4)
- Implementation: Performance optimization, caching

**Week 8: Impact & Risk**
- Impact & outcome tracking (4)
- Risk & gap identification (4)
- Implementation: Risk scoring, alert logic

**Testing & Validation**: End of Week 8
- Performance testing under load
- Accuracy validation against manual queries
- User acceptance testing

---

### Phase 3: Domain Completion (Weeks 9-12)
**Focus**: Complete coverage across all domains
**Deliverables**: 49+ additional query templates

**Week 9: Assessment & MANA**
- 12 assessment-focused queries
- Assessment-needs linkage

**Week 10: Coordination & Partnerships**
- 10 engagement & partnership queries
- Organization collaboration analysis

**Week 11: Projects & PPAs**
- 16 comprehensive PPA queries
- Budget tracking, progress monitoring

**Week 12: Demographics & Spatial**
- 12 demographic/vulnerable sector queries
- 8 basic spatial intelligence queries
- Final testing and deployment

---

## 7. Success Metrics

### Query Template Metrics
- **Coverage**: Target 200+ templates (from 151 baseline)
- **Response Time**: < 500ms for 90% of queries
- **Accuracy**: 95%+ match with manual query results
- **User Adoption**: 70%+ of queries handled by templates (vs. AI fallback)

### User Experience Metrics
- **Clarity**: 90%+ of responses immediately understandable
- **Relevance**: 85%+ of responses directly answer user's question
- **Satisfaction**: 4.0+ average rating (5-point scale)

### Business Impact Metrics
- **Decision Speed**: 40% reduction in time to get critical information
- **Data Access**: 60% increase in staff querying data independently
- **Evidence-Based Decisions**: 50% increase in needs-based PPA planning

---

## 8. Conclusion & Next Steps

### Key Findings
1. **Strong Foundation**: 151 existing templates provide solid coverage for basic queries
2. **Critical Gaps**: Needs management, budget tracking, cross-domain relationships under-served
3. **Quick Wins Available**: 27 high-value, low-complexity queries ready for immediate implementation
4. **Strategic Opportunities**: Evidence-based budgeting pipeline is high-priority, high-impact

### Recommendations
1. **Prioritize Quick Wins**: Implement 27 quick win queries in Weeks 1-3 for immediate value
2. **Focus on Evidence-Based Budgeting**: Needs → Policies → PPAs pipeline is critical for OBCMS mission
3. **Invest in Cross-Domain Queries**: Relationships between models are where highest value lies
4. **Optimize Performance**: Pre-compute aggregates, use caching, optimize join strategies

### Next Steps
1. ✅ **Review & Approve**: Stakeholder review of this analysis (Week 0)
2. ⏭️ **Implement Phase 1**: Quick wins (Weeks 1-3)
3. ⏭️ **Implement Phase 2**: Strategic queries (Weeks 4-8)
4. ⏭️ **Implement Phase 3**: Domain completion (Weeks 9-12)
5. ⏭️ **Performance Testing**: Load testing, optimization (Week 13)
6. ⏭️ **Production Deployment**: Staged rollout (Week 14)

---

**Document Prepared By**: Claude Code Analysis
**Review Status**: PENDING STAKEHOLDER REVIEW
**Last Updated**: October 6, 2025
**Related Documents**:
- [Query Templates Base](../../../src/common/ai_services/chat/query_templates/base.py)
- [Existing Communities Templates](../../../src/common/ai_services/chat/query_templates/communities.py)
- [OBCMS Data Models](../../../src/communities/models.py)
