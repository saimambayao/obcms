# OBCMS AI Chat Query Reference

**Generated:** 2025-10-06 22:47:17
**Total Templates:** 470

## Table of Contents

1. [ANALYTICS](#analytics) (30 templates)
2. [BUDGET](#budget) (7 templates)
3. [COMMUNITIES](#communities) (58 templates)
4. [COMPARISON](#comparison) (20 templates)
5. [COORDINATION](#coordination) (55 templates)
6. [CROSS_DOMAIN](#cross_domain) (39 templates)
7. [GENERAL](#general) (15 templates)
8. [GEOGRAPHIC](#geographic) (48 templates)
9. [INFRASTRUCTURE](#infrastructure) (10 templates)
10. [LIVELIHOOD](#livelihood) (10 templates)
11. [MANA](#mana) (33 templates)
12. [POLICIES](#policies) (45 templates)
13. [PROJECTS](#projects) (45 templates)
14. [STAFF](#staff) (15 templates)
15. [STAKEHOLDERS](#stakeholders) (10 templates)
16. [TEMPORAL](#temporal) (30 templates)

## Quick Reference: Common Queries

Here are some example queries you can try:

### communities

- How many municipalities do we have?
- How many cities?
- How many provinces do we have?
- How many regions do we have?
- How many barangays do we have?

### mana

- Critical needs
- Workshops in Region IX
- How many workshops in Region IX?
- Assessments in Region IX
- Unmet needs

### coordination

- Partnership abc-123
- Organization abc-123
- Meeting abc-123
- Find organization DSWD
- Meetings from 2025-01-01 to 2025-12-31

### policies

- How many approved policies?
- How many policies in education sector?
- How many high priority policies?
- How many national level policies?
- How many policies with evidence?

### projects

- How many projects by MSWDO?
- How many projects in education sector?
- How many projects in Region IX?
- How many overdue projects?
- Budget in Region IX

### staff

- My tasks
- Overdue tasks
- Today tasks
- Find John staff
- High priority tasks

### general

- How to create assessment
- How to edit assessment
- Go to dashboard
- Help
- System status

### geographic

- Show me all regions
- Show me Region IX
- Show me all provinces
- How many provinces in Region IX?
- Show provinces in Region IX

### infrastructure

- How many communities have poor water access?
- How many communities without electricity?
- How many communities with no health facilities?
- How many communities without schools nearby?
- How many communities have poor sanitation?

### livelihood

- How many fishing communities?
- Distribution of primary livelihoods
- Communities by livelihood income level
- What are livelihood challenges?
- Show communities with livelihood opportunities

### stakeholders

- How many religious leaders?
- How many ulama?
- How many high influence stakeholders?
- How many active stakeholders?
- Show high influence stakeholders

### budget

- Budget ceilings near limit
- Remaining budget by sector
- Allocations exceeding ceilings
- Total budget by sector
- Total budget by fiscal year

### temporal

- Last 7 days
- Between January 1 and March 31
- Assessments last 30 days
- Projects in FY 2024
- Assessments in January

### cross_domain

- Needs to PPAs pipeline
- Needs without PPAs
- Complete flow: Needs to Policies to PPAs
- High-priority needs without funding
- Communities with active assessments

### analytics

- Statistical summary
- Distribution analysis
- Outliers by Z-score
- Correlation between metrics
- 90th percentile values

### comparison

- Compare Region IX vs Region X
- Compare provinces
- Compare municipalities
- Compare 3+ locations
- Rank regions by metric

---

## Detailed Template Reference

## ANALYTICS

**Total Templates:** 30

### statistical_summary

**Description:** Mean, median, mode, std dev statistics

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type, field

**Example Queries:**
- `Statistical summary`
- `Stats analysis`
- `Statistical overview`
- `Show statistics`

**Query Template:** `{model}.objects.aggregate(count=Count("id"), mean=Avg("{field}"), median=Percentile("{field}", 0.5),...`


### distribution_analysis

**Description:** Distribution by value buckets

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type, field, thresholds

**Example Queries:**
- `Distribution analysis`
- `Distribution by buckets`
- `Show distribution breakdown`
- `Bucket analysis`

**Query Template:** `{model}.objects.annotate(bucket=Case(When({field}__lte={lower}, then=Value("Low")), When({field}__lt...`


### outlier_detection

**Description:** Outlier detection using Z-score

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type, field

**Example Queries:**
- `Outliers by Z-score`
- `Anomaly detection`
- `Detect unusual values`
- `Find outliers`

**Query Template:** `{model}.objects.annotate(z_score=({field} - Avg("{field}")) / StdDev("{field}")).filter(Q(z_score__g...`


### correlation_analysis

**Description:** Correlation between two metrics

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** fields

**Optional Entities:** model_type

**Example Queries:**
- `Correlation between metrics`
- `Correlation analysis`
- `Measure correlation`
- `Relationship between fields`

**Query Template:** `{model}.objects.aggregate(correlation=Corr("{field1}", "{field2}"))`


### percentile_ranking

**Description:** Percentile ranking analysis

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type, field, percentile

**Example Queries:**
- `90th percentile values`
- `Percentile ranking`
- `Top percentile analysis`
- `Show 95th percentile`

**Query Template:** `{model}.objects.aggregate(p50=Percentile("{field}", 0.5), p75=Percentile("{field}", 0.75), p90=Perce...`


### aggregation_by_dimension

**Description:** Aggregate by multiple dimensions

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** dimensions

**Optional Entities:** model_type, field

**Example Queries:**
- `Aggregate by multiple dimensions`
- `Multi-dimensional analysis`
- `Cross-tabulation`
- `Pivot analysis`

**Query Template:** `{model}.objects.values("{dim1}", "{dim2}").annotate(count=Count("id"), total=Sum("{value_field}"), a...`


### weighted_averages

**Description:** Weighted averages by dimension

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** fields

**Optional Entities:** model_type

**Example Queries:**
- `Weighted by population`
- `Weighted average`
- `Weighted by budget`
- `Population-weighted average`

**Query Template:** `{model}.objects.aggregate(weighted_avg=Sum(F("{value_field}") * F("{weight_field}")) / Sum("{weight_...`


### segmentation

**Description:** Segmentation by characteristics

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** group_by

**Optional Entities:** model_type, field

**Example Queries:**
- `Group by characteristics`
- `Segmentation analysis`
- `Segment by attributes`
- `Customer segmentation`

**Query Template:** `{model}.objects.values("{segment_field}").annotate(count=Count("id"), avg_value=Avg("{value_field}")...`


### anomaly_detection

**Description:** Detect unusual patterns

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type, field

**Example Queries:**
- `Detect anomalies`
- `Unusual patterns`
- `Find irregularities`
- `Anomaly detection`

**Query Template:** `{model}.objects.annotate(deviation=Abs(F("{field}") - Avg("{field}"))).filter(deviation__gt=2 * StdD...`


### pattern_matching

**Description:** Pattern matching by profile

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** profile_attributes

**Optional Entities:** reference_id

**Example Queries:**
- `Communities with similar profiles`
- `Match community characteristics`
- `Find similar demographic profiles`
- `Pattern matching`

**Query Template:** `OBCCommunity.objects.filter(primary_ethnolinguistic_group="{ethnicity}", primary_livelihood="{liveli...`


### grouping_by_characteristics

**Description:** Group by multiple characteristics

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** grouping_fields

**Optional Entities:** model_type

**Example Queries:**
- `Group by demographics`
- `Group by characteristics`
- `Cluster by attributes`
- `Categorize by features`

**Query Template:** `{model}.objects.values("{char1}", "{char2}").annotate(count=Count("id")).order_by("-count")[:30]`


### hotspot_identification

**Description:** Identify geographic hotspots

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** location_field

**Optional Entities:** model_type, threshold

**Example Queries:**
- `Identify hotspots`
- `High-density areas`
- `Concentration analysis`
- `Where are concentrations?`

**Query Template:** `{model}.objects.values("{location_field}").annotate(count=Count("id"), density=Count("id") / Count("...`


### risk_scoring

**Description:** Risk scoring and assessment

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type, risk_factors

**Example Queries:**
- `Risk score by project`
- `Risk assessment`
- `Community risk levels`
- `Calculate risk scores`

**Query Template:** `{model}.objects.annotate(risk_score=Case(When({high_risk_condition}, then=Value(3)), When({medium_ri...`


### success_indicators

**Description:** Indicators of successful outcomes

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type, success_criteria

**Example Queries:**
- `Indicators of success`
- `Success factors`
- `What predicts success?`
- `Success rate analysis`

**Query Template:** `{model}.objects.filter(status="completed").values("{factor_field}").annotate(count=Count("id"), succ...`


### capacity_analysis

**Description:** Capacity vs demand analysis

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type

**Example Queries:**
- `Capacity vs demand`
- `Capacity analysis`
- `Utilization rate`
- `Capacity shortfall`

**Query Template:** `{model}.objects.aggregate(total_capacity=Sum("{capacity_field}"), total_demand=Sum("{demand_field}")...`


### efficiency_metrics

**Description:** Efficiency indicators and metrics

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** efficiency_fields

**Optional Entities:** model_type, group_by

**Example Queries:**
- `Efficiency indicators`
- `Efficiency metrics`
- `Cost efficiency`
- `Output per input`

**Query Template:** `{model}.objects.annotate(efficiency=F("{output_field}") / F("{input_field}")).values("{group_field}"...`


### early_warning_indicators

**Description:** Early warning indicators

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type, warning_criteria

**Example Queries:**
- `Early warning indicators`
- `Warning signs`
- `Red flags`
- `Risk indicators`

**Query Template:** `{model}.objects.filter({warning_conditions}).annotate(warning_count=Count("id", filter={warning_filt...`


### impact_prediction

**Description:** Predict project/policy impact

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type, impact_factors

**Example Queries:**
- `Predicted impact`
- `Impact prediction`
- `Expected outcomes`
- `Forecast impact`

**Query Template:** `{model}.objects.annotate(predicted_impact=F("{beneficiaries}") * F("{impact_factor}")).values("{cate...`


### resource_optimization

**Description:** Optimal resource allocation

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type, optimization_criteria

**Example Queries:**
- `Optimal resource allocation`
- `Resource optimization`
- `Best distribution`
- `Optimize allocation`

**Query Template:** `{model}.objects.annotate(efficiency_score=F("{output}") / F("{resource}"), priority_score=Case(When(...`


### variance_analysis

**Description:** Variance by group

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** group_by

**Optional Entities:** model_type, field

**Example Queries:**
- `Variance analysis`
- `Variance by group`
- `Measure variability`
- `Group variance`

**Query Template:** `{model}.objects.values("{group_field}").annotate(variance=Variance("{value_field}"), std_dev=StdDev(...`


### coefficient_of_variation

**Description:** Coefficient of variation (CV)

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** group_by

**Optional Entities:** model_type, field

**Example Queries:**
- `Coefficient of variation`
- `Variability measure`
- `CV analysis`
- `Relative variability`

**Query Template:** `{model}.objects.values("{group_field}").annotate(mean=Avg("{value_field}"), std_dev=StdDev("{value_f...`


### confidence_intervals

**Description:** Statistical confidence intervals

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type, field, confidence_level

**Example Queries:**
- `Confidence intervals`
- `95% confidence range`
- `Statistical confidence`
- `Margin of error`

**Query Template:** `{model}.objects.aggregate(mean=Avg("{field}"), std_dev=StdDev("{field}"), count=Count("id")).annotat...`


### clustering_analysis

**Description:** Clustering and pattern identification

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type, fields

**Example Queries:**
- `Identify clusters`
- `Clustering analysis`
- `Group similar items`
- `Find patterns`

**Query Template:** `{model}.objects.annotate(cluster_key=Concat(Substr(Cast("{field1}", CharField()), 1, 1), Substr(Cast...`


### similarity_analysis

**Description:** Find similar items

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** reference_id

**Optional Entities:** model_type

**Example Queries:**
- `Find similar communities`
- `Similar projects`
- `Similarity analysis`
- `Communities like this one`

**Query Template:** `{model}.objects.filter({base_filters}).annotate(similarity_score=0).order_by("-similarity_score")[:2...`


### network_analysis

**Description:** Network and connection patterns

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Network analysis`
- `Connection patterns`
- `Partnership networks`
- `Collaboration patterns`

**Query Template:** `Partnership.objects.annotate(partner_count=Count("partners")).values("focus_areas").annotate(partner...`


### hierarchy_analysis

**Description:** Hierarchical relationship analysis

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** hierarchy_field

**Optional Entities:** model_type

**Example Queries:**
- `Hierarchical analysis`
- `Parent-child relationships`
- `Hierarchy patterns`
- `Tree structure analysis`

**Query Template:** `{model}.objects.values("{parent_field}").annotate(children_count=Count("id"), avg_value=Avg("{value_...`


### factor_analysis

**Description:** Contributing factor analysis

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** factors

**Optional Entities:** model_type

**Example Queries:**
- `Contributing factors`
- `Factor analysis`
- `What factors contribute?`
- `Identify key factors`

**Query Template:** `{model}.objects.values("{factor_field}").annotate(count=Count("id"), avg_outcome=Avg("{outcome_field...`


### gap_prediction

**Description:** Predict future gaps and shortfalls

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type, projection_factor

**Example Queries:**
- `Predict future gaps`
- `Gap prediction`
- `Project shortfalls`
- `Forecast deficits`

**Query Template:** `{model}.objects.annotate(current_value=F("{field}"), projected_value=F("{field}") * 1.1, gap=F("proj...`


### performance_prediction

**Description:** Predict future performance

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type, prediction_factors

**Example Queries:**
- `Predicted performance`
- `Performance prediction`
- `Forecast outcomes`
- `Expected performance`

**Query Template:** `{model}.objects.annotate(predicted_score=({factor1_weight} * F("{factor1}") + {factor2_weight} * F("...`


### trend_projection

**Description:** Project trends into future

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type, time_period

**Example Queries:**
- `Project future trends`
- `Trend projection`
- `Forecast trajectory`
- `Extrapolate trends`

**Query Template:** `{model}.objects.filter(created_at__gte=timezone.now() - timedelta(days=365)).annotate(month=TruncMon...`


## BUDGET

**Total Templates:** 7

### budget_ceiling_utilization

**Description:** Show budget ceiling utilization rates by sector

**Priority:** 9/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Budget ceilings near limit`
- `Budget utilization by sector`
- `Show ceiling usage`
- `Budget allocation rates`
- `Which ceilings are near limit?`

**Query Template:** `BudgetCeiling.objects.filter(is_active=True).annotate(utilization_rate=ExpressionWrapper(F('allocate...`


### remaining_budget_by_sector

**Description:** Calculate remaining budget under each ceiling by sector

**Priority:** 9/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Remaining budget by sector`
- `Available budget under ceilings`
- `Unused budget by sector`
- `How much budget is left?`
- `Budget remaining under ceilings`

**Query Template:** `BudgetCeiling.objects.filter(is_active=True).annotate(remaining=ExpressionWrapper(F('ceiling_amount'...`


### budget_ceiling_violations

**Description:** Identify allocations exceeding budget ceilings

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Allocations exceeding ceilings`
- `Budget violating limits`
- `Budgets over ceiling`
- `Which allocations exceed limits?`
- `Ceiling violations`

**Query Template:** `BudgetCeiling.objects.filter(is_active=True, allocated_amount__gt=F('ceiling_amount')).values('name'...`


### total_budget_by_sector

**Description:** Total budget allocated by sector

**Priority:** 8/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Total budget by sector`
- `Sum budget allocated by sector`
- `Budget totals per sector`
- `Sector budget summary`
- `How much budget per sector?`

**Query Template:** `BudgetCeiling.objects.filter(is_active=True).values('sector').annotate(total_ceiling=Sum('ceiling_am...`


### total_budget_by_fiscal_year

**Description:** Total budget by fiscal year

**Priority:** 8/100
**Intent:** data_query
**Result Type:** aggregate

**Optional Entities:** fiscal_year

**Example Queries:**
- `Total budget by fiscal year`
- `Sum budget for FY 2025`
- `Budget totals in 2024`
- `How much budget per year?`
- `Budget by year`

**Query Template:** `BudgetCeiling.objects.filter(is_active=True, fiscal_year='{fiscal_year}').aggregate(total_ceiling=Su...`


### total_budget_by_funding_source

**Description:** Total budget by funding source (GAA, block grant, donor, etc.)

**Priority:** 8/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Total budget by funding source`
- `Sum budget from GAA`
- `Budget totals by block grant`
- `How much from donor funding?`
- `Budget by LGU`

**Query Template:** `BudgetCeiling.objects.filter(is_active=True).values('funding_source').annotate(total_ceiling=Sum('ce...`


### budget_allocation_vs_utilization

**Description:** Compare budget allocation vs utilization rates

**Priority:** 8/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Budget allocation vs utilization`
- `Allocation versus spending`
- `Compare budget to utilization`
- `Allocation compared to disbursement`
- `Budget vs actual spending`

**Query Template:** `BudgetCeiling.objects.filter(is_active=True).annotate(utilization_rate=ExpressionWrapper(F('allocate...`


## COMMUNITIES

**Total Templates:** 58

### count_all_municipalities

**Description:** Count municipalities and cities separately

**Priority:** 11/100
**Intent:** data_query
**Result Type:** municipality_city_breakdown

**Example Queries:**
- `How many municipalities do we have?`
- `Total municipalities`
- `Count municipalities`
- `Number of municipalities`

**Query Template:** `{"municipalities": Municipality.objects.filter(municipality_type="municipality").count(), "cities": ...`


### count_cities_only

**Description:** Count cities only (excluding regular municipalities)

**Priority:** 11/100
**Intent:** data_query
**Result Type:** count

**Example Queries:**
- `How many cities?`
- `Total cities`
- `Count cities`
- `Number of cities`

**Query Template:** `Municipality.objects.filter(municipality_type__in=["city", "component_city", "independent_city"]).co...`


### count_all_provinces

**Description:** Count total provinces in OBC Data

**Priority:** 10/100
**Intent:** data_query
**Result Type:** count

**Example Queries:**
- `How many provinces do we have?`
- `Total provinces`
- `Count provinces`
- `Number of provinces`
- `How many provinces in OBC Data?`

**Query Template:** `Province.objects.count()`


### count_all_regions

**Description:** Count total regions in OBC Data

**Priority:** 10/100
**Intent:** data_query
**Result Type:** count

**Example Queries:**
- `How many regions do we have?`
- `Total regions`
- `Count regions`
- `Number of regions`

**Query Template:** `Region.objects.count()`


### count_all_barangays

**Description:** Count total barangays in OBC Data

**Priority:** 10/100
**Intent:** data_query
**Result Type:** count

**Example Queries:**
- `How many barangays do we have?`
- `Total barangays`
- `Count barangays`
- `Number of barangays`

**Query Template:** `Barangay.objects.count()`


### filter_ethnicity_location_livelihood

**Description:** Filter by ethnicity, livelihood, and location

**Priority:** 10/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** ethnolinguistic_group, livelihood, location

**Example Queries:**
- `Maranao fishing communities in Region IX`
- `Maguindanaon farming communities in Cotabato`

**Query Template:** `OBCCommunity.objects.filter(primary_ethnolinguistic_group__icontains="{ethnicity}", {location_filter...`


### count_communities_by_location

**Description:** Count communities in specific location

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** location

**Example Queries:**
- `How many communities in Region IX?`
- `Count communities in Zamboanga del Sur`
- `Total communities in Sultan Kudarat`
- `Communities in Cotabato City`

**Query Template:** `OBCCommunity.objects.filter({location_filter}).count()`


### count_ethnicity_location

**Description:** Count communities by ethnicity and location

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** ethnolinguistic_group, location

**Example Queries:**
- `How many Maranao communities in Region IX?`
- `Count Maguindanaon population in Cotabato`
- `Total Tausug communities in Zamboanga`

**Query Template:** `OBCCommunity.objects.filter(primary_ethnolinguistic_group__icontains="{ethnicity}", {location_filter...`


### filter_ethnicity_livelihood

**Description:** Filter communities by ethnicity and livelihood

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** ethnolinguistic_group, livelihood

**Example Queries:**
- `Maranao fishing communities`
- `Maguindanaon farming communities`
- `Tausug trading communities`

**Query Template:** `OBCCommunity.objects.filter(primary_ethnolinguistic_group__icontains="{ethnicity}", primary_liveliho...`


### filter_location_livelihood

**Description:** Filter communities by location and livelihood

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** location, livelihood

**Example Queries:**
- `Fishing communities in Region IX`
- `Farming communities in Cotabato`
- `Trading communities in Zamboanga`

**Query Template:** `OBCCommunity.objects.filter({location_filter}, primary_livelihood__icontains="{livelihood}").select_...`


### count_communities_by_ethnicity

**Description:** Count communities by ethnolinguistic group

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** ethnolinguistic_group

**Example Queries:**
- `How many Maranao communities?`
- `Count Maguindanaon communities`
- `Total Tausug communities`
- `Yakan communities count`

**Query Template:** `OBCCommunity.objects.filter(primary_ethnolinguistic_group__icontains="{ethnicity}").count()`


### count_communities_by_livelihood

**Description:** Count communities by primary livelihood

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** livelihood

**Example Queries:**
- `How many communities with fishing livelihood?`
- `Count communities having farming`
- `Total communities with trading livelihood`

**Query Template:** `OBCCommunity.objects.filter(primary_livelihood__icontains="{livelihood}").count()`


### list_communities_by_location

**Description:** List communities in specific location

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** location

**Example Queries:**
- `Show me communities in Region IX`
- `List communities in Zamboanga`
- `Display communities in Cotabato`
- `Communities in Region XII`

**Query Template:** `OBCCommunity.objects.filter({location_filter}).select_related("barangay__municipality__province__reg...`


### list_communities_by_ethnicity

**Description:** List communities by ethnolinguistic group

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** ethnolinguistic_group

**Example Queries:**
- `Show me Maranao communities`
- `List Maguindanaon communities`
- `Display Tausug communities`

**Query Template:** `OBCCommunity.objects.filter(primary_ethnolinguistic_group__icontains="{ethnicity}").select_related("...`


### list_communities_by_livelihood

**Description:** List communities by livelihood

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** livelihood

**Example Queries:**
- `Show me communities with fishing livelihood`
- `List communities with farming`
- `Display communities with trading livelihood`

**Query Template:** `OBCCommunity.objects.filter(primary_livelihood__icontains="{livelihood}").select_related("barangay__...`


### aggregate_total_population

**Description:** Total OBC population across all communities

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Total OBC population`
- `Overall population`
- `Combined population of all communities`
- `What is the total population?`

**Query Template:** `OBCCommunity.objects.aggregate(total=Sum("estimated_obc_population"))["total"]`


### aggregate_population_by_location

**Description:** Total population in specific location

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** location

**Example Queries:**
- `Total population in Region IX`
- `Overall population in Zamboanga`
- `Population in Cotabato`

**Query Template:** `OBCCommunity.objects.filter({location_filter}).aggregate(total=Sum("estimated_obc_population"))["tot...`


### aggregate_pwd_count

**Description:** Total PWDs across all communities

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `How many PWDs?`
- `Total persons with disabilities`
- `Count disabled population`
- `PWD count`

**Query Template:** `OBCCommunity.objects.aggregate(total=Sum("pwd_count"))["total"]`


### aggregate_idp_count

**Description:** Total IDPs across all communities

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `How many IDPs?`
- `Total internally displaced persons`
- `Count IDPs`
- `Displaced persons count`

**Query Template:** `OBCCommunity.objects.aggregate(total=Sum("idps_count"))["total"]`


### aggregate_vulnerable_sectors

**Description:** Summary of vulnerable sectors across communities

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Vulnerable sectors`
- `Show vulnerable groups`
- `Disadvantaged populations`
- `Vulnerable population breakdown`

**Query Template:** `OBCCommunity.objects.aggregate(pwd=Sum("pwd_count"), solo_parents=Sum("solo_parents_count"), idps=Su...`


### demographics_by_location

**Description:** Demographic breakdown for specific location

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** location

**Example Queries:**
- `Demographics in Region IX`
- `Population breakdown for Zamboanga`
- `Demographics of Cotabato`

**Query Template:** `OBCCommunity.objects.filter({location_filter}).aggregate(total_pop=Sum("estimated_obc_population"), ...`


### ethnicity_distribution

**Description:** Distribution of ethnolinguistic groups

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Ethnicity distribution`
- `Ethnic breakdown`
- `Ethnolinguistic groups`
- `Show ethnic distribution`

**Query Template:** `OBCCommunity.objects.values("primary_ethnolinguistic_group").annotate(count=Count("id"), total_pop=S...`


### ethnic_diversity_by_location

**Description:** Ethnic diversity in specific location

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** location

**Example Queries:**
- `Ethnic diversity in Region IX`
- `Ethnolinguistic groups in Zamboanga`
- `Show ethnic groups in Cotabato`

**Query Template:** `OBCCommunity.objects.filter({location_filter}).values("primary_ethnolinguistic_group").annotate(coun...`


### population_by_ethnicity

**Description:** Total population for specific ethnic group

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** ethnolinguistic_group

**Example Queries:**
- `Population of Maranao`
- `Population by Maguindanaon`
- `Tausug population`
- `Yakan population total`

**Query Template:** `OBCCommunity.objects.filter(primary_ethnolinguistic_group__icontains="{ethnicity}").aggregate(total=...`


### ethnicity_locations

**Description:** Locations of specific ethnic group

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** ethnolinguistic_group

**Example Queries:**
- `Where are Maranao communities?`
- `Where do Tausug live?`
- `Maguindanaon locations`
- `Where do Yakan reside?`

**Query Template:** `OBCCommunity.objects.filter(primary_ethnolinguistic_group__icontains="{ethnicity}").values("barangay...`


### largest_ethnic_group_by_location

**Description:** Largest ethnic group in location

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** location

**Example Queries:**
- `Largest ethnic group in Region IX`
- `Dominant ethnic group in Zamboanga`
- `Main ethnic group in Cotabato`

**Query Template:** `OBCCommunity.objects.filter({location_filter}).values("primary_ethnolinguistic_group").annotate(coun...`


### ethnicity_livelihood_correlation

**Description:** Livelihood patterns by ethnic group

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** ethnolinguistic_group

**Example Queries:**
- `Maranao livelihoods`
- `Tausug economic activities`
- `What do Maguindanaon do for livelihood?`
- `Yakan livelihood patterns`

**Query Template:** `OBCCommunity.objects.filter(primary_ethnolinguistic_group__icontains="{ethnicity}").values("primary_...`


### livelihood_by_location

**Description:** Livelihood distribution in location

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** location

**Example Queries:**
- `Livelihoods in Region IX`
- `Economic activities in Zamboanga`
- `Livelihoods at Cotabato`

**Query Template:** `OBCCommunity.objects.filter({location_filter}).values("primary_livelihood").annotate(count=Count("id...`


### count_total_communities

**Description:** Count total OBC communities

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `How many communities are there?`
- `Total communities`
- `Count all OBC communities`
- `Number of communities`
- `How many OBC communities?`

**Query Template:** `OBCCommunity.objects.count()`


### list_recent_communities

**Description:** List recently added communities

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Recent communities`
- `Latest OBC communities`
- `Newly added communities`
- `Show recent communities`

**Query Template:** `OBCCommunity.objects.all().select_related("barangay__municipality__province__region").order_by("-cre...`


### aggregate_average_household

**Description:** Average household size across communities

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Average household size`
- `Mean households per community`
- `What is the average household size?`

**Query Template:** `OBCCommunity.objects.aggregate(avg_households=Avg("households"), avg_population=Avg("estimated_obc_p...`


### aggregate_top_ethnicities

**Description:** Top ethnolinguistic groups by community count

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Top ethnolinguistic groups`
- `Main ethnic groups`
- `Major ethnic communities`
- `Primary ethnolinguistic groups`

**Query Template:** `OBCCommunity.objects.values("primary_ethnolinguistic_group").annotate(count=Count("id")).order_by("-...`


### aggregate_top_livelihoods

**Description:** Top livelihoods across communities

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Top livelihoods`
- `Main livelihoods`
- `Common economic activities`
- `Primary livelihoods`

**Query Template:** `OBCCommunity.objects.values("primary_livelihood").annotate(count=Count("id")).order_by("-count")[:10...`


### aggregate_largest_communities

**Description:** Largest communities by population

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** numbers

**Example Queries:**
- `Largest communities`
- `Biggest populations`
- `Top 10 largest communities`
- `Show largest communities`

**Query Template:** `OBCCommunity.objects.filter(estimated_obc_population__isnull=False).select_related("barangay__munici...`


### filter_recent_additions

**Description:** Recently added communities (last 30 days)

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Recent community additions`
- `Latest community additions`
- `New communities added this month`

**Query Template:** `OBCCommunity.objects.filter(created_at__gte=timezone.now() - timedelta(days=30)).select_related("bar...`


### aggregate_age_distribution

**Description:** Age distribution across all communities

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Age distribution`
- `Population by age`
- `Show age breakdown`
- `What is the age distribution?`

**Query Template:** `OBCCommunity.objects.aggregate(children=Sum("children_0_9"), adolescents=Sum("adolescents_10_14"), y...`


### aggregate_children_count

**Description:** Total children (0-9 years) across communities

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `How many children?`
- `Total children`
- `Count children in communities`
- `Number of kids`

**Query Template:** `OBCCommunity.objects.aggregate(total_children=Sum("children_0_9"), total_adolescents=Sum("adolescent...`


### aggregate_youth_count

**Description:** Total youth (15-30 years) across communities

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `How many youth?`
- `Total youth`
- `Count youth population`
- `Young people count`

**Query Template:** `OBCCommunity.objects.aggregate(total=Sum("youth_15_30"))["total"]`


### aggregate_seniors_count

**Description:** Total seniors (60+ years) across communities

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `How many seniors?`
- `Total elderly`
- `Count senior citizens`
- `Elderly population`

**Query Template:** `OBCCommunity.objects.aggregate(total=Sum("seniors_60_plus"))["total"]`


### aggregate_solo_parents_count

**Description:** Total solo parents across communities

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `How many solo parents?`
- `Total solo parents`
- `Count solo parents`
- `Solo parent population`

**Query Template:** `OBCCommunity.objects.aggregate(total=Sum("solo_parents_count"))["total"]`


### aggregate_women_count

**Description:** Total women across communities

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `How many women?`
- `Total women`
- `Count women population`
- `Women count`

**Query Template:** `OBCCommunity.objects.aggregate(total=Sum("women_count"))["total"]`


### communities_by_population_range

**Description:** Filter communities by population range

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** numbers

**Example Queries:**
- `Communities with population over 1000`
- `Communities with population under 500`
- `How many communities with population over 2000?`

**Query Template:** `OBCCommunity.objects.filter(estimated_obc_population__gte={population}).count()`


### average_household_size_by_location

**Description:** Average household size in specific location

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** location

**Example Queries:**
- `Average household size in Region IX`
- `Average household for Zamboanga`
- `Household size in Cotabato`

**Query Template:** `OBCCommunity.objects.filter({location_filter}).aggregate(avg_households=Avg("households"), avg_popul...`


### multi_ethnic_communities

**Description:** Communities with multiple ethnic groups

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Multi-ethnic communities`
- `Show diverse communities`
- `Mixed ethnic communities`
- `Communities with multiple ethnic groups`

**Query Template:** `OBCCommunity.objects.exclude(other_ethnolinguistic_groups__exact="").select_related("barangay__munic...`


### languages_spoken

**Description:** Languages spoken across communities

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Languages spoken`
- `What languages are spoken?`
- `Show dialects spoken`
- `Language diversity`

**Query Template:** `OBCCommunity.objects.exclude(languages_spoken__exact="").values("languages_spoken").annotate(count=C...`


### ethnic_population_percentage

**Description:** Percentage of communities by ethnic group

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** ethnolinguistic_group

**Example Queries:**
- `Percentage of Maranao`
- `What percentage are Tausug?`
- `Maguindanaon percentage`
- `Share of Yakan communities`

**Query Template:** `OBCCommunity.objects.aggregate(total=Count("id"), ethnic_count=Count("id", filter=Q(primary_ethnolin...`


### livelihood_distribution

**Description:** Distribution of livelihoods

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Livelihood distribution`
- `Economic breakdown`
- `Livelihood patterns`
- `Show economic distribution`

**Query Template:** `OBCCommunity.objects.values("primary_livelihood").annotate(count=Count("id"), total_pop=Sum("estimat...`


### farmers_count_total

**Description:** Total farmers across communities

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `How many farmers?`
- `Total farmers`
- `Count farming population`
- `Farmer count`

**Query Template:** `OBCCommunity.objects.aggregate(total=Sum("farmers_count"))["total"]`


### fisherfolk_count_total

**Description:** Total fisherfolk across communities

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `How many fisherfolk?`
- `Total fishermen`
- `Count fishers`
- `Fisherfolk count`

**Query Template:** `OBCCommunity.objects.aggregate(total=Sum("fisherfolk_count"))["total"]`


### unemployed_count_total

**Description:** Total unemployed across communities

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `How many unemployed?`
- `Total unemployed`
- `Count unemployment`
- `Unemployed population`

**Query Template:** `OBCCommunity.objects.aggregate(total=Sum("unemployed_count"))["total"]`


### livelihood_diversity_index

**Description:** Livelihood diversity across communities

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Livelihood diversity`
- `Economic variety`
- `How diverse are livelihoods?`
- `Show livelihood diversity`

**Query Template:** `OBCCommunity.objects.values("primary_livelihood", "secondary_livelihood").annotate(count=Count("id")...`


### primary_vs_secondary_livelihood

**Description:** Comparison of primary and secondary livelihoods

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Primary vs secondary livelihood`
- `Primary versus secondary livelihood`
- `Compare primary and secondary livelihoods`
- `Primary livelihood compared to secondary`

**Query Template:** `OBCCommunity.objects.exclude(primary_livelihood__exact="", secondary_livelihood__exact="").values("p...`


### income_levels_distribution

**Description:** Income level distribution

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Income levels`
- `Income distribution`
- `Earnings range`
- `Show income levels`

**Query Template:** `OBCCommunity.objects.exclude(income_level__exact="").values("income_level").annotate(count=Count("id...`


### livelihood_by_proximity

**Description:** Livelihood patterns by BARMM proximity

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Livelihoods by proximity to BARMM`
- `Economic activities by BARMM proximity`
- `How does proximity affect livelihood?`

**Query Template:** `OBCCommunity.objects.values("proximity_to_barmm", "primary_livelihood").annotate(count=Count("id"))....`


### list_all_communities

**Description:** List all OBC communities

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show me communities`
- `List all OBC communities`
- `Display communities`
- `Get all communities`

**Query Template:** `OBCCommunity.objects.all().order_by("-created_at")[:20]`


### aggregate_proximity_barmm

**Description:** Communities grouped by proximity to BARMM

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Communities by proximity to BARMM`
- `Group communities by BARMM proximity`
- `How many adjacent to BARMM?`

**Query Template:** `OBCCommunity.objects.values("proximity_to_barmm").annotate(count=Count("id")).order_by("-count")`


### rare_ethnic_groups

**Description:** Ethnic groups with few communities

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Rare ethnic groups`
- `Small ethnic groups`
- `Minority ethnic groups`
- `Less common ethnic groups`

**Query Template:** `OBCCommunity.objects.values("primary_ethnolinguistic_group").annotate(count=Count("id")).filter(coun...`


### communities_with_multiple_livelihoods

**Description:** Communities with both primary and secondary livelihoods

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Communities with multiple livelihoods`
- `Communities with both livelihoods`
- `Dual livelihood communities`
- `Show communities with secondary livelihoods`

**Query Template:** `OBCCommunity.objects.exclude(primary_livelihood__exact="", secondary_livelihood__exact="").select_re...`


## COMPARISON

**Total Templates:** 20

### region_vs_region

**Description:** Compare two regions

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** locations

**Example Queries:**
- `Compare Region IX vs Region X`
- `Region IX versus Region XII`
- `Region X compared to Region XI`
- `Compare Regions IX and X`

**Query Template:** `OBCCommunity.objects.filter(Q(barangay__municipality__province__region__name__icontains="{region1}")...`


### province_vs_province

**Description:** Compare two provinces

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** locations

**Example Queries:**
- `Compare provinces`
- `Zamboanga del Sur vs Cotabato`
- `Province comparison`
- `Compare two provinces`

**Query Template:** `OBCCommunity.objects.filter(Q(barangay__municipality__province__name__icontains="{province1}") | Q(b...`


### municipality_comparison

**Description:** Compare two municipalities

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** locations

**Example Queries:**
- `Compare municipalities`
- `Municipality A vs Municipality B`
- `Compare two municipalities`
- `Municipality comparison`

**Query Template:** `OBCCommunity.objects.filter(Q(barangay__municipality__name__icontains="{muni1}") | Q(barangay__munic...`


### multi_location_comparison

**Description:** Compare multiple locations

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** locations

**Optional Entities:** model_type

**Example Queries:**
- `Compare 3+ locations`
- `Compare multiple regions`
- `Multi-location comparison`
- `Compare several provinces`

**Query Template:** `{model}.objects.filter({location_filters}).values("{location_field}").annotate(count=Count("id"), to...`


### location_ranking

**Description:** Rank locations by metric

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** location_level, metric

**Optional Entities:** model_type

**Example Queries:**
- `Rank regions by metric`
- `Ranking provinces by population`
- `Rank municipalities by assessments`
- `Location ranking`

**Query Template:** `{model}.objects.values("{location_field}").annotate(metric_value=Sum("{metric_field}")).order_by("-m...`


### ethnicity_demographics

**Description:** Compare demographics by ethnic group

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** ethnolinguistic_groups

**Example Queries:**
- `Compare ethnic groups demographics`
- `Ethnicity demographic comparison`
- `Compare Maranao vs Tausug demographics`
- `Ethnic group characteristics`

**Query Template:** `OBCCommunity.objects.values("primary_ethnolinguistic_group").annotate(communities=Count("id"), total...`


### ethnicity_needs

**Description:** Needs comparison by ethnic group

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** ethnolinguistic_groups

**Example Queries:**
- `Needs by ethnic group`
- `Compare needs across ethnicities`
- `Ethnic group needs analysis`
- `Which ethnic groups have most needs?`

**Query Template:** `OBCCommunity.objects.filter(assessments__identified_needs__isnull=False).values("primary_ethnolingui...`


### ethnicity_coverage

**Description:** Service coverage by ethnic group

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** ethnolinguistic_groups

**Example Queries:**
- `Service coverage by ethnic group`
- `Coverage by ethnicity`
- `Which ethnic groups are underserved?`
- `Ethnic group access rates`

**Query Template:** `OBCCommunity.objects.values("primary_ethnolinguistic_group").annotate(total_communities=Count("id"),...`


### ethnicity_resource_allocation

**Description:** Resource allocation by ethnic group

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** ethnolinguistic_groups

**Example Queries:**
- `Resource allocation by group`
- `Budget by ethnicity`
- `Funding allocation by ethnic group`
- `Ethnic group budget comparison`

**Query Template:** `OBCCommunity.objects.filter(assessments__identified_needs__addressing_ppas__isnull=False).values("pr...`


### budget_efficiency

**Description:** Budget efficiency comparison

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** group_by

**Example Queries:**
- `Budget efficiency comparison`
- `Compare cost efficiency`
- `Budget efficiency by MOA`
- `Most efficient spending`

**Query Template:** `MonitoringEntry.objects.filter(actual_budget__gt=0, beneficiaries_count__gt=0).values("{group_field}...`


### project_success_rates

**Description:** Success rate comparison

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** group_by

**Example Queries:**
- `Success rate by MOA`
- `Success rate by sector`
- `Compare project success rates`
- `Which MOA has best success rate?`

**Query Template:** `MonitoringEntry.objects.values("{group_field}").annotate(total_projects=Count("id"), completed=Count...`


### cost_per_beneficiary

**Description:** Cost per beneficiary comparison

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** group_by

**Example Queries:**
- `Cost per beneficiary comparison`
- `Cost efficiency by sector`
- `Compare cost per beneficiary`
- `Most cost-effective projects`

**Query Template:** `MonitoringEntry.objects.filter(actual_budget__gt=0, beneficiaries_count__gt=0).annotate(cost_per_ben...`


### location_benchmarking

**Description:** Benchmark location against average

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** location, metric

**Optional Entities:** model_type

**Example Queries:**
- `Benchmark against average`
- `Compare to national average`
- `Regional benchmarking`
- `Performance vs average`

**Query Template:** `{model}.objects.values("{location_field}").annotate(location_value=Avg("{metric_field}")).annotate(o...`


### location_gap_analysis

**Description:** Gap analysis between locations

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** locations, metric

**Optional Entities:** model_type

**Example Queries:**
- `Gap between locations`
- `Regional gap analysis`
- `Location disparity`
- `Inequality between regions`

**Query Template:** `{model}.objects.values("{location_field}").annotate(metric_value={metric_calculation}).aggregate(max...`


### location_performance_matrix

**Description:** Performance matrix across locations

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** locations, metrics

**Optional Entities:** model_type

**Example Queries:**
- `Performance comparison matrix`
- `Multi-metric location comparison`
- `Location performance grid`
- `Compare locations across metrics`

**Query Template:** `{model}.objects.values("{location_field}").annotate(metric1=Avg("{metric1_field}"), metric2=Avg("{me...`


### ethnicity_outcomes

**Description:** Outcomes comparison by ethnic group

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** ethnolinguistic_groups

**Example Queries:**
- `Outcomes by ethnic group`
- `Compare ethnic group outcomes`
- `Success rates by ethnicity`
- `Ethnic group impact`

**Query Template:** `OBCCommunity.objects.filter(assessments__isnull=False).values("primary_ethnolinguistic_group").annot...`


### ethnicity_participation

**Description:** Participation rates by ethnic group

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** ethnolinguistic_groups

**Example Queries:**
- `Participation rates by ethnicity`
- `Ethnic group engagement`
- `Compare participation across ethnicities`
- `Engagement by ethnic group`

**Query Template:** `Assessment.objects.values("community__primary_ethnolinguistic_group").annotate(assessments=Count("id...`


### completion_time_comparison

**Description:** Completion time comparison

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** group_by

**Example Queries:**
- `Completion time by type`
- `Compare project durations`
- `Average completion time comparison`
- `Which projects finish fastest?`

**Query Template:** `MonitoringEntry.objects.filter(completion_date__isnull=False).annotate(duration=(F("completion_date"...`


### coverage_comparison

**Description:** Coverage rate comparison

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** group_by

**Optional Entities:** model_type, coverage_criteria

**Example Queries:**
- `Coverage rates comparison`
- `Compare coverage by region`
- `Assessment coverage comparison`
- `Service coverage by location`

**Query Template:** `{model}.objects.values("{group_field}").annotate(total_target=Count("id"), covered=Count("id", filte...`


### performance_benchmarking

**Description:** Performance benchmarking

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** performance_metric

**Optional Entities:** model_type, group_by

**Example Queries:**
- `Performance vs benchmarks`
- `Benchmark comparison`
- `Compare to performance standards`
- `Performance gap analysis`

**Query Template:** `{model}.objects.values("{group_field}").annotate(performance_score={performance_calculation}, benchm...`


## COORDINATION

**Total Templates:** 55

### coordination_fca8f522

**Description:** Partnership details

**Priority:** 80/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** id

**Example Queries:**
- `Partnership abc-123`
- `Show me partnership details`


### coordination_5f90c766

**Description:** Organization details

**Priority:** 80/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** id

**Example Queries:**
- `Organization abc-123`
- `Show me organization details`


### coordination_fb2e2029

**Description:** Meeting details

**Priority:** 80/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** id

**Example Queries:**
- `Meeting abc-123`
- `Show me meeting details`


### coordination_a79f8c32

**Description:** Search organizations by name

**Priority:** 75/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** name

**Example Queries:**
- `Find organization DSWD`
- `Search organization Red Cross`


### coordination_dec9d5cf

**Description:** Meetings in date range

**Priority:** 75/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** date_start, date_end

**Example Queries:**
- `Meetings from 2025-01-01 to 2025-12-31`


### coordination_aa5317ed

**Description:** Resources for specific partnership

**Priority:** 75/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** id

**Example Queries:**
- `Resources for partnership abc-123`
- `Resources in partnership xyz`


### coordination_b4f889d1

**Description:** MOAs expiring within 90 days

**Priority:** 75/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `MOAs expiring`
- `MOUs needing renewal`
- `MOA renewal`


### coordination_5f6b110c

**Description:** MOAs with specific agency

**Priority:** 75/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** organization

**Example Queries:**
- `MOAs with DSWD`
- `MOUs with BARMM`
- `Memorandum with OPAPP`


### coordination_9ec10753

**Description:** Count partnerships in location

**Priority:** 70/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** location

**Example Queries:**
- `Partnerships in Region IX`
- `How many partnerships in Zamboanga del Sur?`


### coordination_ee2bef06

**Description:** Partnerships with specific organization

**Priority:** 70/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** organization

**Example Queries:**
- `Partnerships with BARMM`
- `How many partnerships with DSWD?`


### coordination_86944e46

**Description:** Organizations in sector

**Priority:** 70/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** sector

**Example Queries:**
- `Organizations in health sector`
- `Education sector organizations`


### coordination_a2dc9bab

**Description:** NGOs in location

**Priority:** 70/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** location

**Example Queries:**
- `NGOs in Region IX`
- `How many NGOs in Zamboanga?`


### coordination_c38dfc65

**Description:** Organizations in location

**Priority:** 70/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** location

**Example Queries:**
- `Organizations in Region IX`
- `Organizations in Zamboanga`


### coordination_009305cb

**Description:** Meetings with organization

**Priority:** 70/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** organization

**Example Queries:**
- `Meetings with BARMM`
- `How many meetings with DSWD?`


### coordination_a81ed62c

**Description:** Meetings in location

**Priority:** 70/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** location

**Example Queries:**
- `Meetings in Region IX`
- `How many meetings in Zamboanga?`


### coordination_5848c7dd

**Description:** Today's meetings

**Priority:** 70/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Today's meetings`
- `Meetings today`


### coordination_04ba7c77

**Description:** Activities by organization

**Priority:** 70/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** organization

**Example Queries:**
- `Activities with DSWD`
- `Activities by BARMM`


### coordination_c64a7808

**Description:** Active MOAs/MOUs count

**Priority:** 70/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Active MOAs`
- `MOUs`
- `Memorandum of agreements`


### coordination_e2b40807

**Description:** MOAs pending renewal

**Priority:** 70/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `MOAs pending renewal`
- `MOUs needing renewal`


### coordination_5242fad1

**Description:** Engagement history for organization

**Priority:** 70/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** organization

**Example Queries:**
- `Engagement history for DSWD`
- `Engagement history of BARMM`


### coordination_8673cef5

**Description:** Partnerships in sector

**Priority:** 65/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** sector

**Example Queries:**
- `Partnerships in education sector`
- `Health sector partnerships`


### coordination_023d5abd

**Description:** Organizations by type

**Priority:** 65/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** type

**Example Queries:**
- `NGO organizations`
- `Government organizations`


### coordination_9e96bbb4

**Description:** Activities by engagement type

**Priority:** 65/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** type

**Example Queries:**
- `Workshop activities`
- `Training activities`
- `Consultation activities`


### coordination_eadeae8f

**Description:** Resource allocation across partnerships

**Priority:** 65/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Resource allocation`
- `Show resource allocation`


### coordination_bf593c5b

**Description:** List all MOAs/MOUs

**Priority:** 65/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `List all MOAs`
- `Show MOUs`
- `All memorandums`


### coordination_38987073

**Description:** Partnership effectiveness metrics

**Priority:** 65/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Partnership effectiveness`
- `How effective are partnerships?`


### coordination_f84e6850

**Description:** Activity level by organization

**Priority:** 65/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Organization activity level`
- `Agency activity level`
- `Most active organizations`


### coordination_e9c39b0a

**Description:** Collaboration trends over time

**Priority:** 65/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** date_start, date_end

**Example Queries:**
- `Collaboration trends`
- `Partnership trends`
- `Show collaboration trends`


### coordination_30d1b82f

**Description:** Outcomes from completed engagements

**Priority:** 65/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Engagement outcomes`
- `Show engagement outcomes`
- `What were the outcomes?`


### coordination_31615600

**Description:** Partnership milestones achieved

**Priority:** 65/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Partnership milestones`
- `Show milestones`
- `Deliverables achieved`


### coordination_83f13a1c

**Description:** Count active partnerships

**Priority:** 60/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Active partnerships`
- `Show me ongoing partnerships`


### coordination_9ce86791

**Description:** Recently created partnerships

**Priority:** 60/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Recent partnerships`
- `Show me recent partnerships`


### coordination_6a67d560

**Description:** Partnerships by status

**Priority:** 60/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** status

**Example Queries:**
- `Completed partnerships`
- `Pending partnerships`


### coordination_88f209b3

**Description:** Government agency count

**Priority:** 60/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Government agencies`
- `How many government agencies?`


### coordination_097bde7e

**Description:** Recent meetings

**Priority:** 60/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Recent meetings`
- `Show me recent meetings`


### coordination_2af8f5d3

**Description:** Upcoming meeting schedule

**Priority:** 60/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Meeting schedule`
- `Show me meeting schedule`


### coordination_19bcb0e4

**Description:** List coordination activities (non-meeting)

**Priority:** 60/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Coordination activities`
- `Show coordination activities`


### coordination_131a4bff

**Description:** Activity timeline for date range

**Priority:** 60/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** date_start, date_end

**Example Queries:**
- `Activity timeline`
- `Show activity timeline`


### coordination_952407a2

**Description:** List shared resources in partnerships

**Priority:** 60/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Shared resources`
- `Show shared resources`
- `Resources being shared`


### coordination_0d6ed80d

**Description:** Count partnerships with resource sharing

**Priority:** 60/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Partnerships with resources`
- `How many partnerships with resource sharing?`


### coordination_e8085d11

**Description:** Stakeholder engagement metrics

**Priority:** 60/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Engagement metrics`
- `Show engagement statistics`


### coordination_e033e491

**Description:** Partnership distribution by sector

**Priority:** 60/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Partnerships by sector`
- `Sector distribution`


### coordination_63e3a2fc

**Description:** Historical partnerships

**Priority:** 60/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Historical partnerships`
- `Past partnerships`
- `Completed partnerships`


### coordination_d232c499

**Description:** Recent stakeholder engagements

**Priority:** 60/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Recent engagements`
- `Latest engagements`
- `Show recent engagements`


### coordination_63126a32

**Description:** List all partnerships

**Priority:** 55/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `List all partnerships`
- `Show partnerships`


### coordination_413858c8

**Description:** Active stakeholder organizations

**Priority:** 55/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Active stakeholders`
- `Show me active organizations`


### coordination_9f3f8d5d

**Description:** List all organizations

**Priority:** 55/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `List all organizations`
- `Show organizations`


### coordination_fdea3f5b

**Description:** Completed meetings count

**Priority:** 55/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Completed meetings`
- `How many completed meetings?`


### coordination_16931e7d

**Description:** Planned meetings count

**Priority:** 55/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Planned meetings`
- `How many planned meetings?`


### coordination_2a2d9076

**Description:** Types of resources being shared

**Priority:** 55/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Types of resources shared`
- `Resource types`
- `What resources are shared?`


### coordination_cec93f79

**Description:** Total partnership count

**Priority:** 50/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `How many partnerships?`
- `Total partnerships`
- `Count partnerships`


### coordination_d3e19785

**Description:** Total organization count

**Priority:** 50/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `How many organizations?`
- `Total organizations`


### coordination_db94c713

**Description:** Total meeting count

**Priority:** 50/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `How many meetings?`
- `Total meetings`


### coordination_ee756c08

**Description:** Total activity count

**Priority:** 50/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `How many activities?`
- `Total activities`
- `Count activities`


### coordination_69bf2e2e

**Description:** Partnerships by type

**Priority:** 40/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** type

**Example Queries:**
- `Technical partnerships`
- `Funding partnerships`


## CROSS_DOMAIN

**Total Templates:** 39

### needs_to_ppas_pipeline

**Description:** Needs and PPAs addressing them

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Needs to PPAs pipeline`
- `Needs to projects addressing them`
- `Needs flow to PPAs`
- `Track needs to implementation`

**Query Template:** `Need.objects.annotate(ppa_count=Count("addressing_ppas")).values("sector", "ppa_count").order_by("-p...`


### needs_without_ppas

**Description:** Unaddressed needs without PPAs

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** sector, priority

**Example Queries:**
- `Needs without PPAs`
- `Unaddressed needs`
- `Needs lacking implementation`
- `Which needs have no projects?`

**Query Template:** `Need.objects.filter(addressing_ppas__isnull=True, status__in=["identified", "validated"]).select_rel...`


### needs_policy_ppa_flow

**Description:** Complete needs-policies-PPAs pipeline

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Complete flow: Needs to Policies to PPAs`
- `Full pipeline tracking`
- `Needs policy PPA flow`
- `Track complete implementation chain`

**Query Template:** `Need.objects.annotate(policy_count=Count("related_policies"), ppa_count=Count("addressing_ppas")).va...`


### unfunded_needs_analysis

**Description:** High-priority unfunded needs

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `High-priority needs without funding`
- `Critical needs lacking PPAs`
- `Unfunded priority needs`
- `High priority gaps`

**Query Template:** `Need.objects.filter(priority__in=["high", "critical"], addressing_ppas__isnull=True).select_related(...`


### communities_with_assessments

**Description:** Communities with assessments

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** status

**Example Queries:**
- `Communities with active assessments`
- `Communities having assessments`
- `Show communities with assessments`
- `Which communities have assessments?`

**Query Template:** `OBCCommunity.objects.filter(assessments__isnull=False).distinct().select_related("barangay__municipa...`


### communities_without_assessments

**Description:** Communities without any assessments

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** location

**Example Queries:**
- `Communities without assessments`
- `Communities never assessed`
- `No assessment communities`
- `Which communities lack assessments?`

**Query Template:** `OBCCommunity.objects.filter(assessments__isnull=True).select_related("barangay__municipality__provin...`


### communities_recent_assessment

**Description:** Communities assessed in timeframe

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** time_period

**Example Queries:**
- `Communities assessed in last 12 months`
- `Communities assessed within past year`
- `Recent assessments by community`
- `Communities assessed last 6 months`

**Query Template:** `OBCCommunity.objects.filter(assessments__created_at__gte=timezone.now() - timedelta({period}={value}...`


### communities_with_unmet_needs

**Description:** Communities with unaddressed needs

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** location

**Example Queries:**
- `Communities with unmet needs`
- `Unaddressed needs by community`
- `Communities needing support`
- `Show communities with open needs`

**Query Template:** `OBCCommunity.objects.filter(assessments__identified_needs__status__in=["identified", "validated"]).d...`


### communities_priority_needs

**Description:** Communities with high-priority needs

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Communities with critical needs`
- `High priority needs by community`
- `Priority needs communities`
- `Communities needing urgent support`

**Query Template:** `OBCCommunity.objects.filter(assessments__identified_needs__priority__in=["high", "critical"]).distin...`


### needs_with_budget

**Description:** Needs with budget allocation

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Needs with budget allocated`
- `Funded needs`
- `Needs with funding assigned`
- `Which needs have budget?`

**Query Template:** `Need.objects.filter(addressing_ppas__actual_budget__gt=0).distinct().annotate(total_budget=Sum("addr...`


### policies_implementing_needs

**Description:** Policies addressing identified needs

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Policies addressing needs`
- `Recommendations implementing needs`
- `Policies for identified needs`
- `Policy-needs linkage`

**Query Template:** `PolicyRecommendation.objects.filter(related_needs__isnull=False).distinct().prefetch_related("relate...`


### ppas_addressing_needs

**Description:** PPAs addressing identified needs

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `PPAs addressing needs`
- `Projects implementing needs`
- `PPAs for identified needs`
- `Implementation of needs`

**Query Template:** `MonitoringEntry.objects.filter(addresses_needs__isnull=False).distinct().prefetch_related("addresses...`


### needs_coverage_by_sector

**Description:** Needs coverage by sector

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Needs addressed vs unmet by sector`
- `Needs coverage by sector`
- `Sector-wise needs status`
- `Implementation rate by sector`

**Query Template:** `Need.objects.values("sector").annotate(total_needs=Count("id"), addressed_needs=Count("id", filter=Q...`


### needs_budget_allocation

**Description:** Budget allocation to needs by sector

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Budget allocated to needs by sector`
- `Funding by sector for needs`
- `Sector budget allocation`
- `How much budget per sector?`

**Query Template:** `Need.objects.filter(addressing_ppas__actual_budget__gt=0).values("sector").annotate(total_budget=Sum...`


### evidence_based_budgeting

**Description:** Evidence-based budgeting flow

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Assessment to needs to budget flow`
- `Evidence-based budgeting`
- `Needs to funding conversion`
- `Data-driven budget allocation`

**Query Template:** `Assessment.objects.annotate(needs_count=Count("identified_needs"), funded_needs=Count("identified_ne...`


### assessment_coverage_by_ethnicity

**Description:** Assessment coverage by ethnic group

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Assessment coverage by ethnic group`
- `Coverage by ethnicity`
- `Which ethnic groups are assessed?`
- `Assessment penetration by ethnicity`

**Query Template:** `OBCCommunity.objects.values("primary_ethnolinguistic_group").annotate(total_communities=Count("id"),...`


### needs_per_community

**Description:** Average needs per community

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Average needs identified per community`
- `Mean needs per community`
- `Needs per community average`
- `How many needs per community?`

**Query Template:** `OBCCommunity.objects.annotate(needs_count=Count("assessments__identified_needs")).aggregate(avg_need...`


### communities_by_needs_count

**Description:** Communities ranked by needs count

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Communities with most identified needs`
- `Communities by needs count`
- `Top communities by needs`
- `Most needs identified`

**Query Template:** `OBCCommunity.objects.annotate(needs_count=Count("assessments__identified_needs")).filter(needs_count...`


### assessment_to_needs_pipeline

**Description:** Assessments and their identified needs

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Assessment to needs pipeline`
- `Assessments to needs identified`
- `Assessment needs flow`
- `Track assessment to needs conversion`

**Query Template:** `Assessment.objects.annotate(needs_count=Count("identified_needs")).values("status", "needs_count").o...`


### communities_multiple_assessments

**Description:** Communities with multiple assessments

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** number

**Example Queries:**
- `Communities with 2+ assessments`
- `Communities with multiple assessments`
- `Multiple assessments per community`
- `Communities assessed more than once`

**Query Template:** `OBCCommunity.objects.annotate(assessment_count=Count("assessments")).filter(assessment_count__gte={m...`


### community_assessment_history

**Description:** Complete assessment history for community

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** community_id

**Example Queries:**
- `Full assessment history by community`
- `Assessment history for community`
- `Show all assessments for this community`
- `Community assessment timeline`

**Query Template:** `Assessment.objects.select_related("community", "lead_organization").filter(community_id={community_i...`


### communities_by_assessment_status

**Description:** Communities grouped by assessment status

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Communities by assessment status`
- `Group communities by assessment phase`
- `Assessment status distribution`
- `Communities in each assessment stage`

**Query Template:** `OBCCommunity.objects.filter(assessments__isnull=False).values("assessments__status").annotate(commun...`


### assessment_geographic_coverage

**Description:** Assessment coverage by geographic area

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** location_level

**Example Queries:**
- `Assessment coverage by province`
- `Geographic coverage by region`
- `Assessment penetration by province`
- `Coverage map by location`

**Query Template:** `OBCCommunity.objects.values("barangay__municipality__province__{level}__name").annotate(total_commun...`


### assessment_participation_rate

**Description:** Community participation in assessments

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Community participation in assessments`
- `Participation rate by assessment`
- `Engagement in assessments`
- `Community involvement tracking`

**Query Template:** `Assessment.objects.values("community__name").annotate(participant_count=Count("participants")).order...`


### communities_assessment_gap

**Description:** Time since last assessment per community

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Time since last assessment`
- `Assessment gap by community`
- `Days since last assessment`
- `Communities needing reassessment`

**Query Template:** `OBCCommunity.objects.annotate(last_assessment=Max("assessments__created_at"), days_since=timezone.no...`


### partnerships_supporting_assessments

**Description:** Partnerships supporting assessments

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Partnerships supporting assessments`
- `Partnerships linked to assessments`
- `Assessment partnerships`
- `Which partnerships support assessments?`

**Query Template:** `Partnership.objects.filter(related_assessments__isnull=False).distinct().prefetch_related("partners"...`


### stakeholder_engagement_in_workshops

**Description:** Stakeholders engaged in MANA activities

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Stakeholders in MANA workshops`
- `Stakeholders participating in assessments`
- `Workshop participants`
- `Who attends MANA workshops?`

**Query Template:** `StakeholderOrganization.objects.filter(engagements__related_assessment__isnull=False).distinct().ann...`


### moa_assessment_leadership

**Description:** MOAs leading assessments

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `MOAs leading assessments`
- `Ministries conducting assessments`
- `Agencies leading MANA`
- `Government assessment leadership`

**Query Template:** `StakeholderOrganization.objects.filter(organization_type__in=["government", "moa"]).annotate(assessm...`


### coordination_to_assessment

**Description:** Engagements linked to assessments

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Engagements to assessments`
- `Coordination to assessment flow`
- `Meetings leading to assessments`
- `Engagement assessment linkage`

**Query Template:** `StakeholderEngagement.objects.filter(related_assessment__isnull=False).values("engagement_type").ann...`


### assessment_stakeholder_count

**Description:** Stakeholder count per assessment

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Stakeholder participation by assessment`
- `Count stakeholders per assessment`
- `Assessment participation levels`
- `How many stakeholders per assessment?`

**Query Template:** `Assessment.objects.annotate(stakeholder_count=Count("participating_organizations")).order_by("-stake...`


### multi_stakeholder_assessments

**Description:** Assessments with multiple stakeholders

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** number

**Example Queries:**
- `Assessments with 3+ organizations`
- `Multi-stakeholder assessments`
- `Assessments with multiple partners`
- `Collaborative assessments`

**Query Template:** `Assessment.objects.annotate(org_count=Count("participating_organizations")).filter(org_count__gte={m...`


### assessment_facilitators

**Description:** Staff members facilitating assessments

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Staff facilitating assessments`
- `Assessment facilitators`
- `Who leads assessments?`
- `Staff assessment workload`

**Query Template:** `User.objects.filter(facilitated_assessments__isnull=False).annotate(assessment_count=Count("facilita...`


### engagement_assessment_linkage

**Description:** Engagements linked to assessments

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Engagements linked to assessments`
- `Related engagements to assessments`
- `Show engagement-assessment links`
- `Coordination supporting assessments`

**Query Template:** `StakeholderEngagement.objects.filter(related_assessment__isnull=False).select_related("related_asses...`


### partnership_assessment_support

**Description:** Partnerships supporting MANA activities

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Partnerships supporting MANA`
- `MANA partnerships`
- `Partnerships for assessments`
- `Collaborative MANA support`

**Query Template:** `Partnership.objects.filter(focus_areas__icontains="mana").prefetch_related("partners").annotate(asse...`


### stakeholder_assessment_coverage

**Description:** Stakeholder participation across assessments

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Stakeholder coverage across assessments`
- `Stakeholder assessment participation`
- `Which stakeholders are most involved?`
- `Assessment engagement by stakeholder`

**Query Template:** `StakeholderOrganization.objects.annotate(assessment_count=Count("participated_assessments")).filter(...`


### needs_with_multiple_ppas

**Description:** Needs with multiple PPAs

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Needs addressed by multiple PPAs`
- `Needs with multiple projects`
- `Multi-PPA needs`
- `Comprehensive need addressing`

**Query Template:** `Need.objects.annotate(ppa_count=Count("addressing_ppas")).filter(ppa_count__gte=2).order_by("-ppa_co...`


### ppas_by_needs_addressed

**Description:** PPAs ranked by needs addressed

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `PPAs ranked by needs addressed count`
- `Projects by needs addressed`
- `Most impactful PPAs`
- `PPAs addressing most needs`

**Query Template:** `MonitoringEntry.objects.annotate(needs_count=Count("addresses_needs")).filter(needs_count__gt=0).ord...`


### needs_implementation_gap

**Description:** Time gap from need to implementation

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Time from need identification to PPA start`
- `Gap between need and implementation`
- `Implementation lag analysis`
- `How long from need to action?`

**Query Template:** `Need.objects.filter(addressing_ppas__isnull=False).annotate(gap_days=(Min("addressing_ppas__start_da...`


### cross_sector_needs_analysis

**Description:** Needs addressed by multiple sectors

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Needs spanning multiple sectors`
- `Cross-sector needs analysis`
- `Multi-sector needs`
- `Needs requiring coordination`

**Query Template:** `Need.objects.filter(addressing_ppas__isnull=False).annotate(ppa_sectors=ArrayAgg("addressing_ppas__s...`


## GENERAL

**Total Templates:** 15

### help_how_to_create

**Description:** Help with creating entities

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** entity

**Example Queries:**
- `How to create assessment`
- `How do I add community`
- `Help me create project`
- `How to add new task`
- `How do I make a report?`

**Query Template:** `help_create_{entity}`


### help_how_to_edit

**Description:** Help with editing entities

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** entity

**Example Queries:**
- `How to edit assessment`
- `How do I update community`
- `Help me modify project`
- `How to change task status`
- `How do I update profile?`

**Query Template:** `help_edit_{entity}`


### navigation_go_to_module

**Description:** Navigate to module

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** module

**Example Queries:**
- `Go to dashboard`
- `Open communities`
- `Navigate to MANA`
- `Take me to projects`
- `Go to coordination`

**Query Template:** `get_module_url("{module}")`


### help_general

**Description:** General help request

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Help`
- `I need help`
- `Assist me`
- `How do I use this?`
- `User guide`

**Query Template:** `help_content`


### system_status

**Description:** Check system status

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `System status`
- `Server status`
- `Application health`
- `Is system running?`
- `Check system state`

**Query Template:** `get_system_status()`


### navigation_dashboard

**Description:** Go to dashboard

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Home`
- `Dashboard`
- `Main page`
- `Go home`
- `Take me to dashboard`

**Query Template:** `redirect_to_dashboard()`


### navigation_find_page

**Description:** Search for pages

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** keyword

**Example Queries:**
- `Find page reports`
- `Search section analytics`
- `Where is module settings?`
- `Find reports page`
- `Search for communities section`

**Query Template:** `search_pages("{keyword}")`


### metadata_audit_log

**Description:** Show audit trail

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** entity

**Example Queries:**
- `Audit log for assessment`
- `History of community`
- `Changes for project`
- `Log of this task`
- `Show history for report`

**Query Template:** `AuditLog.objects.filter(object_repr__icontains="{entity}").select_related("user", "content_type").or...`


### help_documentation_link

**Description:** Access documentation

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** module

**Example Queries:**
- `Documentation`
- `User manual`
- `Guide for communities`
- `Tutorial for MANA`
- `Show docs`

**Query Template:** `get_documentation({module})`


### help_faq

**Description:** Show FAQ list

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `FAQ`
- `Frequently asked questions`
- `Common questions`
- `Show FAQ`
- `Help FAQ`

**Query Template:** `get_faq_list()`


### system_updates

**Description:** Show recent system updates

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Recent updates`
- `Latest changes`
- `New features`
- `Latest releases`
- `What changed recently?`

**Query Template:** `SystemUpdate.objects.filter(published=True).order_by("-created_at")[:10]`


### system_announcements

**Description:** Show active announcements

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Announcements`
- `System news`
- `Notices`
- `Show announcements`
- `Recent notices`

**Query Template:** `Announcement.objects.filter(published=True, expiry_date__gte=timezone.now()).order_by("-priority", "...`


### metadata_created_by

**Description:** Show entity creator

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** entity

**Example Queries:**
- `Who created this assessment?`
- `Who created community profile?`
- `Who created this project?`
- `Who created this task?`

**Query Template:** `get_creator_info("{entity}")`


### metadata_modified_date

**Description:** Show modification date

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** entity

**Example Queries:**
- `When was this modified?`
- `What time was assessment updated?`
- `When was community changed?`
- `When was project edited?`

**Query Template:** `get_modification_date("{entity}")`


### system_version

**Description:** Show system version

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Version`
- `Build number`
- `Release info`
- `What version?`
- `System version`

**Query Template:** `get_system_version()`


## GEOGRAPHIC

**Total Templates:** 48

### list_all_regions

**Description:** List all regions in OBC coverage

**Priority:** 10/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show me all regions`
- `List regions`
- `Display regions`
- `What are the regions?`
- `Get all regions`

**Query Template:** `Region.objects.all().order_by("name")`


### region_by_name

**Description:** Get specific region details

**Priority:** 10/100
**Intent:** data_query
**Result Type:** single

**Required Entities:** region

**Example Queries:**
- `Show me Region IX`
- `Get Region XII details`
- `Information about Region X`
- `Details of BARMM region`

**Query Template:** `Region.objects.filter(name__icontains="{region_name}").first()`


### list_all_provinces

**Description:** List all provinces with region grouping

**Priority:** 10/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show me all provinces`
- `List provinces`
- `Display provinces`
- `What are the provinces?`
- `Get all provinces`

**Query Template:** `Province.objects.all().order_by("region__name", "name")`


### count_provinces_by_region

**Description:** Count provinces in specific region

**Priority:** 10/100
**Intent:** data_query
**Result Type:** count

**Required Entities:** region

**Example Queries:**
- `How many provinces in Region IX?`
- `Count provinces in Region XII`
- `Provinces within BARMM`

**Query Template:** `Province.objects.filter(region__name__icontains="{region_name}").count()`


### list_provinces_by_region

**Description:** List provinces in specific region

**Priority:** 10/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** region

**Example Queries:**
- `Show provinces in Region IX`
- `List provinces of Region XII`
- `Display provinces in BARMM`
- `Get provinces within Region X`

**Query Template:** `Province.objects.filter(region__name__icontains="{region_name}").order_by("name")`


### province_by_name

**Description:** Get specific province details

**Priority:** 10/100
**Intent:** data_query
**Result Type:** single

**Required Entities:** province

**Example Queries:**
- `Show me Zamboanga del Sur province`
- `Get Cotabato province details`
- `Information about Sultan Kudarat province`

**Query Template:** `Province.objects.filter(name__icontains="{province_name}").first()`


### count_all_municipalities_geographic

**Description:** Count municipalities and cities separately

**Priority:** 10/100
**Intent:** data_query
**Result Type:** municipality_city_breakdown

**Example Queries:**
- `How many municipalities?`
- `Count municipalities`
- `Number of municipalities`

**Query Template:** `{"municipalities": Municipality.objects.filter(municipality_type="municipality").count(), "cities": ...`


### count_cities_only_geographic

**Description:** Count cities only (excluding regular municipalities)

**Priority:** 10/100
**Intent:** data_query
**Result Type:** count

**Example Queries:**
- `How many cities?`
- `Count cities`
- `Total cities`
- `Number of cities`

**Query Template:** `Municipality.objects.filter(municipality_type__in=["city", "component_city", "independent_city"]).co...`


### list_all_municipalities

**Description:** List all municipalities/cities with province grouping

**Priority:** 10/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show me all municipalities`
- `List municipalities`
- `Display cities`
- `What are the municipalities?`
- `Get all municipalities`

**Query Template:** `Municipality.objects.all().order_by("province__name", "name")`


### count_municipalities_by_province

**Description:** Count municipalities in specific province

**Priority:** 10/100
**Intent:** data_query
**Result Type:** count

**Required Entities:** province

**Example Queries:**
- `How many municipalities in Cotabato?`
- `Count cities in Zamboanga del Sur`
- `Municipalities within Sultan Kudarat`

**Query Template:** `Municipality.objects.filter(province__name__icontains="{province_name}").count()`


### list_municipalities_by_province

**Description:** List municipalities in specific province

**Priority:** 10/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** province

**Example Queries:**
- `Show municipalities in Cotabato`
- `List cities of Sultan Kudarat`
- `Display municipalities within Zamboanga del Sur`
- `Get municipalities in Cotabato province`

**Query Template:** `Municipality.objects.filter(province__name__icontains="{province_name}").order_by("name")`


### municipality_by_name

**Description:** Get specific municipality details

**Priority:** 10/100
**Intent:** data_query
**Result Type:** single

**Required Entities:** municipality

**Example Queries:**
- `Show me Pagadian City`
- `Get Cotabato City details`
- `Information about Tacurong municipality`

**Query Template:** `Municipality.objects.filter(name__icontains="{municipality_name}").first()`


### list_all_barangays

**Description:** List all barangays with municipality grouping

**Priority:** 10/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show me all barangays`
- `List barangays`
- `Display barangays`
- `What are the barangays?`
- `Get all barangays`

**Query Template:** `Barangay.objects.all().order_by("municipality__name", "name")`


### count_barangays_by_municipality

**Description:** Count barangays in specific municipality

**Priority:** 10/100
**Intent:** data_query
**Result Type:** count

**Required Entities:** municipality

**Example Queries:**
- `How many barangays in Pagadian?`
- `Count barangays in Cotabato City`
- `Barangays within Tacurong`

**Query Template:** `Barangay.objects.filter(municipality__name__icontains="{municipality_name}").count()`


### list_barangays_by_municipality

**Description:** List barangays in specific municipality

**Priority:** 10/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** municipality

**Example Queries:**
- `Show barangays in Pagadian`
- `List barangays of Cotabato City`
- `Display barangays within Tacurong`
- `Get barangays in Zamboanga City`

**Query Template:** `Barangay.objects.filter(municipality__name__icontains="{municipality_name}").order_by("name")`


### barangay_by_name

**Description:** Get specific barangay details

**Priority:** 10/100
**Intent:** data_query
**Result Type:** single

**Required Entities:** barangay

**Example Queries:**
- `Show me Barangay Poblacion`
- `Get Barangay Matina details`
- `Information about Barangay Rosary Heights`

**Query Template:** `Barangay.objects.filter(name__icontains="{barangay_name}").first()`


### count_regions_with_obc

**Description:** Count regions with OBC presence

**Priority:** 9/100
**Intent:** data_query
**Result Type:** count

**Example Queries:**
- `How many regions with OBC?`
- `Count regions with communities`
- `Regions having OBC presence`

**Query Template:** `Region.objects.filter(provinces__municipalities__barangays__obc_communities__isnull=False).distinct(...`


### barangays_with_obc

**Description:** Barangays with OBC communities

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Which barangays have OBC?`
- `Barangays with communities`
- `What barangays have OBC presence?`

**Query Template:** `Barangay.objects.filter(obc_communities__isnull=False).distinct()`


### region_demographics

**Description:** OBC population totals by region

**Priority:** 8/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Show population by region`
- `Get OBC population by region`
- `Population breakdown by region`

**Query Template:** `Region.objects.annotate(total_pop=Sum("provinces__municipalities__barangays__obc_communities__estima...`


### region_communities_count

**Description:** Community count per region

**Priority:** 8/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Show communities per region`
- `Get OBC communities by region`
- `Count communities in each region`

**Query Template:** `Region.objects.annotate(community_count=Count("provinces__municipalities__barangays__obc_communities...`


### regions_by_population_density

**Description:** Regions ranked by OBC population

**Priority:** 8/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Rank regions by OBC population`
- `Sort regions by population`
- `Order regions by OBC population`

**Query Template:** `Region.objects.annotate(total_pop=Sum("provinces__municipalities__barangays__obc_communities__estima...`


### province_demographics

**Description:** OBC population totals by province

**Priority:** 8/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Show population by province`
- `Get OBC population by province`
- `Population breakdown by province`

**Query Template:** `Province.objects.annotate(total_pop=Sum("municipalities__barangays__obc_communities__estimated_obc_p...`


### province_communities_count

**Description:** Community count per province

**Priority:** 8/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Show communities per province`
- `Get OBC communities by province`
- `Count communities in each province`

**Query Template:** `Province.objects.annotate(community_count=Count("municipalities__barangays__obc_communities", distin...`


### provinces_by_obc_population

**Description:** Provinces ranked by OBC population

**Priority:** 8/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Rank provinces by OBC population`
- `Sort provinces by population`
- `Order provinces by OBC population`

**Query Template:** `Province.objects.annotate(total_pop=Sum("municipalities__barangays__obc_communities__estimated_obc_p...`


### municipality_demographics

**Description:** OBC population totals by municipality

**Priority:** 8/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Show population by municipality`
- `Get OBC population by municipality`
- `Population breakdown by municipality`

**Query Template:** `Municipality.objects.annotate(total_pop=Sum("barangays__obc_communities__estimated_obc_population"))...`


### municipality_communities_count

**Description:** Community count per municipality

**Priority:** 8/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Show communities per municipality`
- `Get OBC communities by municipality`
- `Count communities in each municipality`

**Query Template:** `Municipality.objects.annotate(community_count=Count("barangays__obc_communities", distinct=True)).or...`


### barangay_demographics

**Description:** OBC population totals by barangay

**Priority:** 8/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Show population by barangay`
- `Get OBC population by barangay`
- `Population breakdown by barangay`

**Query Template:** `Barangay.objects.annotate(total_pop=Sum("obc_communities__estimated_obc_population")).order_by("-tot...`


### administrative_hierarchy

**Description:** Full administrative hierarchy: Region → Province → Municipality → Barangay

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show administrative hierarchy`
- `Display hierarchy`
- `Get administrative structure`

**Query Template:** `Region.objects.all().prefetch_related("provinces__municipalities__barangays")`


### geographic_rollup_summary

**Description:** Summary stats rolled up by administrative level

**Priority:** 8/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Show geographic summary`
- `Get administrative summary`
- `Geographic rollup`

**Query Template:** `{"regions": Region.objects.count(), "provinces": Province.objects.count(), "municipalities": Municip...`


### regions_with_boundaries

**Description:** Regions with GeoJSON boundaries

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Which regions have boundaries?`
- `Regions with GeoJSON`
- `What regions have geographic data?`

**Query Template:** `Region.objects.filter(boundary_geojson__isnull=False)`


### region_coverage_analysis

**Description:** Assessment coverage by region

**Priority:** 7/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Show assessment coverage by region`
- `Get MANA coverage per region`
- `Assessment distribution by region`

**Query Template:** `Region.objects.annotate(assessment_count=Count("provinces__municipalities__barangays__obc_communitie...`


### region_ppa_count

**Description:** PPA count per region

**Priority:** 7/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Show PPAs by region`
- `Get projects per region`
- `Count programs in each region`

**Query Template:** `Region.objects.annotate(ppa_count=Count("provinces__municipalities__barangays__obc_communities__acti...`


### region_budget_allocation

**Description:** Budget allocation by region

**Priority:** 7/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Show budget allocation by region`
- `Get budget by region`
- `Budget distribution per region`

**Query Template:** `Region.objects.annotate(total_budget=Sum("provinces__municipalities__barangays__obc_communities__act...`


### region_needs_count

**Description:** Identified needs count by region

**Priority:** 7/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Show identified needs by region`
- `Get needs per region`
- `Count needs in each region`

**Query Template:** `Region.objects.annotate(needs_count=Count("provinces__municipalities__barangays__obc_communities__ne...`


### provinces_with_boundaries

**Description:** Provinces with GeoJSON boundaries

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Which provinces have boundaries?`
- `Provinces with GeoJSON`
- `What provinces have geographic data?`

**Query Template:** `Province.objects.filter(boundary_geojson__isnull=False)`


### province_coverage_analysis

**Description:** Assessment coverage by province

**Priority:** 7/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Show assessment coverage by province`
- `Get MANA coverage per province`
- `Assessment distribution by province`

**Query Template:** `Province.objects.annotate(assessment_count=Count("municipalities__barangays__obc_communities__assess...`


### province_ppa_count

**Description:** PPA count per province

**Priority:** 7/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Show PPAs by province`
- `Get projects per province`
- `Count programs in each province`

**Query Template:** `Province.objects.annotate(ppa_count=Count("municipalities__barangays__obc_communities__activities", ...`


### province_budget_allocation

**Description:** Budget allocation by province

**Priority:** 7/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Show budget allocation by province`
- `Get budget by province`
- `Budget distribution per province`

**Query Template:** `Province.objects.annotate(total_budget=Sum("municipalities__barangays__obc_communities__activities__...`


### municipalities_by_urban_rural

**Description:** Municipalities by urban/rural classification

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** urban_rural_classification

**Example Queries:**
- `Show urban municipalities`
- `List rural cities`
- `Display urban areas`

**Query Template:** `Municipality.objects.filter(is_urban={"urban": "True", "rural": "False"}["{classification}"])`


### municipality_ppa_count

**Description:** PPA count per municipality

**Priority:** 7/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Show PPAs by municipality`
- `Get projects per municipality`
- `Count programs in each municipality`

**Query Template:** `Municipality.objects.annotate(ppa_count=Count("barangays__obc_communities__activities", distinct=Tru...`


### municipality_budget

**Description:** Budget allocation by municipality

**Priority:** 7/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Show budget by municipality`
- `Get budget per municipality`
- `Budget distribution by municipality`

**Query Template:** `Municipality.objects.annotate(total_budget=Sum("barangays__obc_communities__activities__budget_alloc...`


### municipalities_with_high_obc

**Description:** Municipalities above population threshold

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** population_threshold

**Example Queries:**
- `Show municipalities with high OBC population`
- `List municipalities with over 1000 OBC population`
- `Municipalities with more than 500 OBC`

**Query Template:** `Municipality.objects.annotate(total_pop=Sum("barangays__obc_communities__estimated_obc_population"))...`


### barangays_with_coordinates

**Description:** Barangays with GPS coordinates

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Which barangays have coordinates?`
- `Barangays with GPS`
- `What barangays have location data?`

**Query Template:** `Barangay.objects.filter(center_coordinates__isnull=False)`


### geographic_coverage_gaps

**Description:** Administrative units without OBC presence

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show geographic coverage gaps`
- `Find gaps in coverage`
- `Identify administrative units without OBC`
- `Show coverage gaps`
- `Find geographic gaps`

**Query Template:** `Municipality.objects.annotate(community_count=Count("barangays__obc_communities")).filter(community_...`


### geographic_comparison

**Description:** Compare two geographic areas

**Priority:** 7/100
**Intent:** data_query
**Result Type:** aggregate

**Required Entities:** location, location

**Example Queries:**
- `Compare Region IX vs Region X`
- `Contrast Cotabato and Sultan Kudarat`
- `Compare Zamboanga del Sur and Zamboanga del Norte`

**Query Template:** `# Comparison query - extract stats for both locations`


### municipalities_administrative_data

**Description:** Administrative information for municipalities

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show administrative data for municipalities`
- `Get administrative info for municipalities`
- `Municipality administrative information`

**Query Template:** `Municipality.objects.all().select_related("province__region")`


### adjacent_administrative_units

**Description:** Find adjacent administrative units (requires GeoJSON)

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** location

**Example Queries:**
- `Show adjacent provinces to Cotabato`
- `Find neighboring municipalities to Pagadian`
- `Get provinces near Sultan Kudarat`

**Query Template:** `# Adjacent units query requires spatial analysis`


### administrative_boundaries_export

**Description:** Export GeoJSON boundaries for mapping

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Export administrative boundaries`
- `Download GeoJSON boundaries`
- `Get boundary data`
- `Export boundaries`
- `Download boundaries`

**Query Template:** `{"regions": Region.objects.filter(boundary_geojson__isnull=False), "provinces": Province.objects.fil...`


## INFRASTRUCTURE

**Total Templates:** 10

### count_communities_by_water_access

**Description:** Count communities by water access rating

**Priority:** 9/100
**Intent:** data_query
**Result Type:** count

**Required Entities:** rating

**Example Queries:**
- `How many communities have poor water access?`
- `Communities with limited water supply`
- `Count communities with no water access`
- `Communities having available water`
- `Total communities with poor water`

**Query Template:** `OBCCommunity.objects.filter(infrastructure__infrastructure_type='water', infrastructure__availabilit...`


### count_communities_by_electricity

**Description:** Count communities without adequate electricity access

**Priority:** 9/100
**Intent:** data_query
**Result Type:** count

**Example Queries:**
- `How many communities without electricity?`
- `Communities with no power`
- `Count communities lacking electricity`
- `Communities need electricity`
- `Total communities with poor electricity`

**Query Template:** `OBCCommunity.objects.filter(infrastructure__infrastructure_type='electricity', infrastructure__avail...`


### count_communities_by_healthcare

**Description:** Count communities with inadequate healthcare facilities

**Priority:** 9/100
**Intent:** data_query
**Result Type:** count

**Example Queries:**
- `How many communities with no health facilities?`
- `Communities without healthcare`
- `Count communities lacking health centers`
- `Communities need health facilities`
- `Total communities with poor health access`

**Query Template:** `OBCCommunity.objects.filter(infrastructure__infrastructure_type='health', infrastructure__availabili...`


### count_communities_by_education

**Description:** Count communities with inadequate education facilities

**Priority:** 9/100
**Intent:** data_query
**Result Type:** count

**Example Queries:**
- `How many communities without schools nearby?`
- `Communities with no education facilities`
- `Count communities lacking schools`
- `Communities need schools`
- `Total communities with poor education access`

**Query Template:** `OBCCommunity.objects.filter(infrastructure__infrastructure_type='education', infrastructure__availab...`


### count_communities_by_sanitation

**Description:** Count communities by sanitation/waste management access

**Priority:** 8/100
**Intent:** data_query
**Result Type:** count

**Required Entities:** rating

**Example Queries:**
- `How many communities have poor sanitation?`
- `Communities with limited waste management`
- `Count communities by drainage rating`
- `Communities with no sanitation`
- `Total communities with available drainage`

**Query Template:** `OBCCommunity.objects.filter(Q(infrastructure__infrastructure_type='waste') | Q(infrastructure__infra...`


### list_critical_infrastructure_gaps

**Description:** List communities with critical/high priority infrastructure needs

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show communities with critical infrastructure needs`
- `List communities with urgent infrastructure gaps`
- `Find communities with high priority improvements`
- `Display communities with critical needs`
- `Communities with priority infrastructure gaps`

**Query Template:** `OBCCommunity.objects.filter(infrastructure__priority_for_improvement__in=['critical', 'high']).disti...`


### list_communities_poor_water

**Description:** List communities needing water infrastructure improvements

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show communities needing water improvements`
- `List communities with poor water supply`
- `Which communities lack water access?`
- `Find communities without water`
- `Communities requiring water improvements`

**Query Template:** `OBCCommunity.objects.filter(infrastructure__infrastructure_type='water', infrastructure__availabilit...`


### list_communities_poor_electricity

**Description:** List communities needing electricity infrastructure improvements

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show communities needing electricity`
- `List communities with poor power access`
- `Which communities lack electricity?`
- `Find communities without power`
- `Communities requiring electricity improvements`

**Query Template:** `OBCCommunity.objects.filter(infrastructure__infrastructure_type='electricity', infrastructure__avail...`


### infrastructure_coverage_by_province

**Description:** Show infrastructure availability summary grouped by province

**Priority:** 7/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Show infrastructure availability by province`
- `Infrastructure coverage summary by province`
- `Display water access by province`
- `List electricity availability by province`
- `Health facilities breakdown by province`

**Query Template:** `CommunityInfrastructure.objects.values('community__barangay__municipality__province__name', 'infrast...`


### infrastructure_improvement_priorities

**Description:** List infrastructure flagged for priority improvements

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show infrastructure flagged as priority`
- `List critical infrastructure improvements`
- `What infrastructure projects are urgent?`
- `Which improvements are high priority?`
- `Infrastructure marked as critical`

**Query Template:** `CommunityInfrastructure.objects.filter(priority_for_improvement__in=['critical', 'high']).select_rel...`


## LIVELIHOOD

**Total Templates:** 10

### count_livelihoods_by_type

**Description:** Count livelihoods by type (fishing, agriculture, etc.)

**Priority:** 9/100
**Intent:** data_query
**Result Type:** count

**Required Entities:** livelihood_type

**Example Queries:**
- `How many fishing communities?`
- `Count agriculture livelihoods`
- `Total livestock communities`
- `How many trade communities?`
- `Handicraft livelihoods count`

**Query Template:** `CommunityLivelihood.objects.filter(livelihood_type__icontains='{livelihood_type}').count()`


### count_primary_livelihoods

**Description:** Show distribution of primary livelihoods across communities

**Priority:** 8/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Distribution of primary livelihoods`
- `Breakdown of livelihoods`
- `Summary of economic activities`
- `Primary livelihood distribution`
- `Livelihood breakdown`

**Query Template:** `CommunityLivelihood.objects.filter(is_primary_livelihood=True).values('livelihood_type').annotate(co...`


### livelihood_income_levels

**Description:** Show communities grouped by livelihood income level

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** income_level

**Example Queries:**
- `Communities by livelihood income level`
- `Livelihoods with low income`
- `Communities with moderate income`
- `High income livelihoods`
- `Income level breakdown`

**Query Template:** `CommunityLivelihood.objects.filter(income_level__icontains='{income_level}').select_related('communi...`


### list_livelihood_challenges

**Description:** List common livelihood challenges faced by communities

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `What are livelihood challenges?`
- `Show common livelihood problems`
- `List livelihood issues`
- `Common livelihood difficulties`
- `Challenges in livelihoods`

**Query Template:** `CommunityLivelihood.objects.exclude(challenges='').values('livelihood_type', 'challenges', 'communit...`


### list_communities_by_livelihood_opportunity

**Description:** List communities with documented livelihood opportunities

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show communities with livelihood opportunities`
- `List livelihoods with potential`
- `Which communities have livelihood prospects?`
- `Communities with opportunities`
- `Livelihood potential by community`

**Query Template:** `CommunityLivelihood.objects.exclude(opportunities='').select_related('community__barangay').values('...`


### count_seasonal_livelihoods

**Description:** Count seasonal vs year-round livelihoods

**Priority:** 7/100
**Intent:** data_query
**Result Type:** count

**Example Queries:**
- `How many seasonal livelihoods?`
- `Count year-round activities`
- `Total seasonal jobs`
- `Permanent livelihood count`
- `Seasonal vs year-round breakdown`

**Query Template:** `CommunityLivelihood.objects.filter(seasonal=True).count() if 'seasonal' in query else CommunityLivel...`


### livelihood_participation_rate

**Description:** Calculate average participation rate in primary livelihoods

**Priority:** 7/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Participation rate in primary livelihood`
- `Percentage involved in livelihoods`
- `How many participating in primary livelihood?`
- `Average involvement in livelihoods`
- `Livelihood participation rate`

**Query Template:** `CommunityLivelihood.objects.filter(is_primary_livelihood=True).aggregate(avg_participation=Avg('perc...`


### livelihood_diversity_by_community

**Description:** Show communities with multiple/diversified livelihoods

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Communities with multiple livelihoods`
- `Communities having diverse activities`
- `Variety of income sources by community`
- `Communities with diversified livelihoods`
- `Livelihood diversity by community`

**Query Template:** `CommunityLivelihood.objects.values('community__barangay__name', 'community__id').annotate(livelihood...`


### economic_organizations_count

**Description:** Count economic organizations (cooperatives, enterprises) by location

**Priority:** 7/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `How many cooperatives by location?`
- `Count social enterprises in communities`
- `Total cooperatives per community`
- `Economic organizations count`
- `Cooperatives and enterprises total`

**Query Template:** `OBCCommunity.objects.aggregate(total_cooperatives=Sum('number_of_cooperatives'), total_enterprises=S...`


### unbanked_population_analysis

**Description:** Show communities with unbanked population

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Communities with unbanked population`
- `How many unbanked residents?`
- `Count communities without banking access`
- `Communities having unbanked people`
- `Unbanked population by community`

**Query Template:** `OBCCommunity.objects.filter(number_of_unbanked_obc__gt=0).values('barangay__name', 'barangay__munici...`


## MANA

**Total Templates:** 33

### mana_4bec99a1

**Description:** List critical needs

**Priority:** 10/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Critical needs`
- `Emergency needs`
- `Urgent needs`
- `Show critical needs`


### mana_b478238f

**Description:** List workshops in specific location

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** location

**Example Queries:**
- `Workshops in Region IX`
- `Workshops in Zamboanga`
- `Show workshops in Cotabato`
- `List workshops in Sultan Kudarat`


### mana_bc5a89e9

**Description:** Count workshops in location

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** location

**Example Queries:**
- `How many workshops in Region IX?`
- `Count workshops in Zamboanga`
- `Workshops in Cotabato count`


### mana_c1b050c4

**Description:** List assessments in specific location

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** location

**Example Queries:**
- `Assessments in Region IX`
- `Assessments in Zamboanga`
- `Show assessments for Cotabato`


### mana_66f18ee3

**Description:** List unmet needs from assessments

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Unmet needs`
- `Unfulfilled needs`
- `Outstanding needs`
- `Show unmet needs`


### mana_b65d9e3d

**Description:** List priority needs

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Priority needs`
- `High-priority needs`
- `Urgent needs`
- `Show priority needs`


### mana_ef750003

**Description:** List needs in specific location

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** location

**Example Queries:**
- `Needs in Region IX`
- `Needs in Zamboanga`
- `Show needs for Cotabato`
- `Identified needs at Sultan Kudarat`


### mana_6877ab88

**Description:** Count participants from location

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** location

**Example Queries:**
- `Participants from Region IX`
- `Participants in Zamboanga`
- `How many participants from Cotabato?`


### mana_349ebd9a

**Description:** List recent workshops (last 90 days)

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Recent workshops`
- `Latest workshops`
- `Current workshops`
- `Show recent workshops`


### mana_15eb593d

**Description:** List upcoming workshops

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Upcoming workshops`
- `Future workshops`
- `Scheduled workshops`
- `Planned workshops`


### mana_08ab2608

**Description:** List workshops in date range

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** date_range

**Example Queries:**
- `Workshops in 2024`
- `Workshops from January to March`
- `Workshops during last 6 months`
- `Workshops this year`


### mana_86dc98ca

**Description:** List assessments by status

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** status

**Example Queries:**
- `Completed assessments`
- `Ongoing assessments`
- `Planning assessments`
- `Show completed assessments`


### mana_99d9626a

**Description:** Count assessments by status

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** status

**Example Queries:**
- `How many completed assessments?`
- `Count ongoing assessments`
- `Total planning assessments`


### mana_f12a92ce

**Description:** List pending/ongoing assessments

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Pending assessments`
- `Ongoing assessments`
- `In-progress assessments`
- `Show pending assessments`


### mana_21d49753

**Description:** Get assessment completion rate

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Assessment completion rate`
- `Assessment success rate`
- `What is the assessment completion rate?`
- `Show completion rate`


### mana_e7ea1d99

**Description:** Get assessment coverage by region

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Assessment coverage by region`
- `Assessment distribution per region`
- `Show assessment coverage`
- `Regional assessment coverage`


### mana_8a4a777b

**Description:** Get assessments for OBC communities

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Community assessments`
- `OBC assessments`
- `Show community assessments`
- `List OBC community assessments`


### mana_c3714636

**Description:** List validated assessments

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Validated assessments`
- `Approved assessments`
- `Verified assessments`
- `Show validated assessments`


### mana_7132921b

**Description:** List assessments pending validation

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Pending validation assessments`
- `Assessments awaiting validation`
- `Assessments under review`
- `Show pending validation`


### mana_7dba5d11

**Description:** List needs by category

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Needs by category`
- `Needs by type`
- `Show needs categories`
- `Breakdown of needs by category`


### mana_1dee7bd9

**Description:** List all workshop activities

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show me workshops`
- `List all workshops`
- `Display workshops`
- `Get workshops`


### mana_78acd188

**Description:** Count total workshops

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `How many workshops?`
- `Total workshops`
- `Count workshops`
- `Number of workshops`


### mana_8f4daf13

**Description:** List all assessments

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show me assessments`
- `List all assessments`
- `Display assessments`
- `Get assessments`


### mana_1f8b79c2

**Description:** List recent assessments

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Recent assessments`
- `Latest assessments`
- `Show recent assessments`


### mana_0b5a9cc8

**Description:** Count total assessments

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `How many assessments?`
- `Total assessments`
- `Count assessments`


### mana_a2a108e4

**Description:** List assessments by category

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Assessments by category`
- `Assessments by type`
- `Show assessment categories`
- `Assessment breakdown by category`


### mana_9088cfe0

**Description:** Count total workshop participants

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `How many participants?`
- `Total workshop participants`
- `Count participants`
- `Number of participants`


### mana_7e3d2766

**Description:** List workshop participants

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show me participants`
- `List workshop participants`
- `Display participants`


### mana_c485d994

**Description:** Get participant demographic summary

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Participant demographics`
- `Attendee breakdown`
- `Participant stats`
- `Show participant demographics`


### mana_37e388ea

**Description:** Count participants by role/type

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Participants by role`
- `Participants by type`
- `Breakdown by participant type`


### mana_ae667dd3

**Description:** List workshop synthesis reports

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Workshop synthesis`
- `Workshop findings`
- `Show workshop summaries`
- `Workshop reports`


### mana_a76a94c5

**Description:** Get workshop findings summary

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show workshop findings`
- `Get findings`
- `Display workshop findings`
- `Workshop findings summary`


### mana_5c6fdbcb

**Description:** List workshop outputs

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Workshop outputs`
- `Workshop results`
- `Show workshop deliverables`
- `Assessment outputs`


## POLICIES

**Total Templates:** 45

### count_policies_by_status

**Description:** Count policies by status

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** status

**Example Queries:**
- `How many approved policies?`
- `Count draft policies`
- `Total implemented policies`
- `Policies under review`

**Query Template:** `PolicyRecommendation.objects.filter({status_filter}).count()`


### count_policies_by_sector

**Description:** Count policies by sector

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** sector

**Example Queries:**
- `How many policies in education sector?`
- `Count policies for health`
- `Total policies in infrastructure sector`

**Query Template:** `PolicyRecommendation.objects.filter(category__icontains="{sector}").count()`


### count_policies_by_priority

**Description:** Count policies by priority level

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** priority

**Example Queries:**
- `How many high priority policies?`
- `Count critical priority policies`
- `Total urgent policies`

**Query Template:** `PolicyRecommendation.objects.filter(priority__icontains="{priority}").count()`


### count_policies_by_scope

**Description:** Count policies by geographic scope

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** scope

**Example Queries:**
- `How many national level policies?`
- `Count regional policies`
- `Total provincial policies`

**Query Template:** `PolicyRecommendation.objects.filter(scope__icontains="{scope}").count()`


### count_policies_with_evidence

**Description:** Count policies with evidence base

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `How many policies with evidence?`
- `Count policies with supporting data`
- `Total policies with documentation`

**Query Template:** `PolicyRecommendation.objects.filter(evidence_base__isnull=False).exclude(evidence_base="").count()`


### count_policies_pending_legislation

**Description:** Count policies pending legislation

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `How many policies pending legislation?`
- `Count policies awaiting approval`
- `Total policies submitted for legislation`

**Query Template:** `PolicyRecommendation.objects.filter(status__in=["submitted", "under_review"]).count()`


### list_policies_by_status

**Description:** List policies by status

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** status

**Example Queries:**
- `Show me approved policies`
- `List draft policies`
- `Display implemented policies`
- `Policies under review`

**Query Template:** `PolicyRecommendation.objects.filter({status_filter}).select_related("created_by").order_by("-created...`


### list_policies_by_sector

**Description:** List policies by sector

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** sector

**Example Queries:**
- `Show me policies in education sector`
- `List policies for health`
- `Display infrastructure policies`

**Query Template:** `PolicyRecommendation.objects.filter(category__icontains="{sector}").select_related("created_by").ord...`


### list_policies_by_priority

**Description:** List policies by priority level

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** priority

**Example Queries:**
- `Show me high priority policies`
- `List critical priority policies`
- `Display urgent policies`

**Query Template:** `PolicyRecommendation.objects.filter(priority__icontains="{priority}").select_related("created_by").o...`


### list_policies_with_evidence

**Description:** List policies with evidence base

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show me policies with evidence`
- `List policies with supporting data`
- `Display policies with documentation`

**Query Template:** `PolicyRecommendation.objects.filter(evidence_base__isnull=False).exclude(evidence_base="").select_re...`


### list_policies_by_scope

**Description:** List policies by geographic scope

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** scope

**Example Queries:**
- `Show me national level policies`
- `List regional policies`
- `Display provincial policies`

**Query Template:** `PolicyRecommendation.objects.filter(scope__icontains="{scope}").select_related("created_by").order_b...`


### search_policies_keyword

**Description:** Search policies by keyword

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** keyword

**Example Queries:**
- `Search for policies about education`
- `Find policies on livelihood`
- `Search policy recommendations related to health`

**Query Template:** `PolicyRecommendation.objects.filter(Q(title__icontains="{keyword}") | Q(description__icontains="{key...`


### list_policies_pending_legislation

**Description:** List policies pending legislation

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show me policies pending legislation`
- `List policies awaiting approval`
- `Display policies submitted for legislation`

**Query Template:** `PolicyRecommendation.objects.filter(status__in=["submitted", "under_review"]).select_related("create...`


### policies_with_impact_evidence

**Description:** Policies with impact evidence

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Policies with impact evidence`
- `Policy recommendations with outcome data`
- `Policies with impact results`

**Query Template:** `PolicyRecommendation.objects.filter(impact_indicators__isnull=False).exclude(impact_indicators="").s...`


### policies_evidence_based

**Description:** Evidence-based policy recommendations

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Evidence-based policies`
- `Evidence based policy recommendations`
- `Show me evidence-based policies`

**Query Template:** `PolicyRecommendation.objects.filter(evidence_base__isnull=False).exclude(evidence_base="").select_re...`


### policies_assessment_based

**Description:** Policies based on assessments

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Policies based on assessments`
- `Policy recommendations from needs analysis`
- `Policies derived from assessments`

**Query Template:** `PolicyRecommendation.objects.filter(related_needs__isnull=False).distinct().prefetch_related("relate...`


### policy_implementation_status

**Description:** Policy implementation status overview

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Policy implementation status`
- `Policies progress tracking`
- `Show me policy implementation status`

**Query Template:** `PolicyRecommendation.objects.values("status").annotate(count=Count("id")).order_by("-count")`


### policy_implementation_rate

**Description:** Policy implementation rate

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Policy implementation rate`
- `Policies completion percentage`
- `What is the policy implementation rate?`

**Query Template:** `PolicyRecommendation.objects.aggregate(total=Count("id"), implemented=Count("id", filter=Q(status="i...`


### policies_implementation_progress

**Description:** Policies currently in implementation

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Policies in implementation`
- `Policy recommendations under progress`
- `Show me policies being implemented`

**Query Template:** `PolicyRecommendation.objects.filter(status__in=["approved", "under_implementation"]).select_related(...`


### policies_fully_implemented

**Description:** Fully implemented policies

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Fully implemented policies`
- `Completed policy recommendations`
- `Show me implemented policies`

**Query Template:** `PolicyRecommendation.objects.filter(status="implemented").select_related("created_by").order_by("-im...`


### policies_overdue_implementation

**Description:** Policies with overdue implementation

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Overdue policy implementation`
- `Delayed policies`
- `Past due policy implementation`

**Query Template:** `PolicyRecommendation.objects.filter(status__in=["approved", "under_implementation"], target_implemen...`


### count_total_policies

**Description:** Count total policy recommendations

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `How many policies are there?`
- `Total policies`
- `Count all policy recommendations`
- `Number of policies`
- `How many policy recommendations?`

**Query Template:** `PolicyRecommendation.objects.count()`


### count_policies_with_stakeholders

**Description:** Count policies with stakeholder involvement

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `How many policies with stakeholder engagement?`
- `Count policies with consultation`
- `Total policies with stakeholders`

**Query Template:** `PolicyRecommendation.objects.filter(stakeholders__isnull=False).distinct().count()`


### count_policies_by_type

**Description:** Count by recommendation type

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** type

**Example Queries:**
- `How many policy recommendations?`
- `Count program initiatives`
- `Total service recommendations`

**Query Template:** `PolicyRecommendation.objects.filter(recommendation_type__icontains="{type}").count()`


### count_policies_recent

**Description:** Count recently created policies (last 90 days)

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `How many recent policies?`
- `Count new policy recommendations`
- `Total latest policies`

**Query Template:** `PolicyRecommendation.objects.filter(created_at__gte=timezone.now() - timedelta(days=90)).count()`


### list_recent_policies

**Description:** List recently added policies

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Recent policies`
- `Latest policy recommendations`
- `Newly added policies`
- `Show recent policies`

**Query Template:** `PolicyRecommendation.objects.all().select_related("created_by").order_by("-created_at")[:20]`


### list_policies_with_stakeholders

**Description:** List policies with stakeholder involvement

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show me policies with stakeholder engagement`
- `List policies with consultation`
- `Display policies with stakeholders`

**Query Template:** `PolicyRecommendation.objects.filter(stakeholders__isnull=False).distinct().prefetch_related("stakeho...`


### list_policies_by_author

**Description:** List policies by author

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** author

**Example Queries:**
- `Show me policies by John Doe`
- `List policies created by admin`
- `Display policy recommendations from staff`

**Query Template:** `PolicyRecommendation.objects.filter(created_by__username__icontains="{author}").select_related("crea...`


### list_top_priority_policies

**Description:** List top priority policies

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Top priority policies`
- `Highest priority policy recommendations`
- `Show me top priority policies`

**Query Template:** `PolicyRecommendation.objects.filter(priority__in=["high", "critical", "urgent"]).select_related("cre...`


### policies_supporting_data

**Description:** Policies with supporting data

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Policies with supporting data`
- `Policy recommendations with baseline evidence`
- `Policies with research documentation`

**Query Template:** `PolicyRecommendation.objects.filter(Q(evidence_base__isnull=False) | Q(supporting_documents__isnull=...`


### policies_without_evidence

**Description:** Policies without evidence base

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Policies without evidence`
- `Policy recommendations lacking supporting data`
- `Policies missing documentation`

**Query Template:** `PolicyRecommendation.objects.filter(Q(evidence_base__isnull=True) | Q(evidence_base="")).select_rela...`


### policies_evidence_quality

**Description:** Policies ranked by evidence quality

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Policies by evidence quality`
- `Policy recommendations data strength`
- `Policies evidence completeness`

**Query Template:** `PolicyRecommendation.objects.annotate(has_evidence=Case(When(evidence_base__isnull=False, then=1), d...`


### policies_impact_assessment

**Description:** Policies with impact assessment

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Policies with impact assessment`
- `Policy recommendations with outcome evaluation`
- `Policies with impact measurement`

**Query Template:** `PolicyRecommendation.objects.filter(impact_indicators__isnull=False).exclude(impact_indicators="").s...`


### policies_research_backed

**Description:** Research-backed policy recommendations

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Research-backed policies`
- `Research backed policy recommendations`
- `Show me research-backed policies`

**Query Template:** `PolicyRecommendation.objects.filter(evidence_base__icontains="research").select_related("created_by"...`


### policies_implementation_gaps

**Description:** Policies with implementation gaps

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Policy implementation gaps`
- `Policies implementation challenges`
- `Policy execution barriers`

**Query Template:** `PolicyRecommendation.objects.filter(status__in=["approved", "under_review"]).exclude(implementation_...`


### policies_implementation_timeline

**Description:** Policy implementation timeline

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Policy implementation timeline`
- `Policies rollout schedule`
- `Policy implementation timeframe`

**Query Template:** `PolicyRecommendation.objects.filter(status__in=["approved", "under_implementation"]).exclude(target_...`


### policies_implementation_success

**Description:** Successfully implemented policies

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Successful policy implementation`
- `Effective policies`
- `High-impact policy implementation`

**Query Template:** `PolicyRecommendation.objects.filter(status="implemented", impact_indicators__isnull=False).exclude(i...`


### policies_by_stakeholder

**Description:** Policies by stakeholder

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** stakeholder

**Example Queries:**
- `Policies involving MOA stakeholder`
- `Policy recommendations with OOBC`
- `Policies from community stakeholders`

**Query Template:** `PolicyRecommendation.objects.filter(stakeholders__name__icontains="{stakeholder}").distinct().prefet...`


### policies_consultation_records

**Description:** Policies with consultation records

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Policy consultation records`
- `Policies engagement history`
- `Policy consultation summary`

**Query Template:** `PolicyRecommendation.objects.filter(consultation_records__isnull=False).exclude(consultation_records...`


### policies_multi_stakeholder

**Description:** Multi-stakeholder policy recommendations

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Multi-stakeholder policies`
- `Collaborative policy recommendations`
- `Policies with multiple stakeholders`

**Query Template:** `PolicyRecommendation.objects.annotate(stakeholder_count=Count("stakeholders")).filter(stakeholder_co...`


### policies_stakeholder_feedback

**Description:** Policies with stakeholder feedback

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Policy stakeholder feedback`
- `Policies with community input`
- `Policy stakeholder comments`

**Query Template:** `PolicyRecommendation.objects.filter(stakeholder_feedback__isnull=False).exclude(stakeholder_feedback...`


### policies_public_consultation

**Description:** Policies with public consultation

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Policies with public consultation`
- `Policy recommendations with community participation`
- `Policies with public input`

**Query Template:** `PolicyRecommendation.objects.filter(public_consultation=True).select_related("created_by").order_by(...`


### policies_without_stakeholders

**Description:** Policies without stakeholder involvement

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Policies without stakeholder engagement`
- `Policy recommendations lacking consultation`
- `Policies missing stakeholders`

**Query Template:** `PolicyRecommendation.objects.filter(stakeholders__isnull=True).select_related("created_by").order_by...`


### list_all_policies

**Description:** List all policy recommendations

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show me policies`
- `List all policy recommendations`
- `Display policies`
- `Get all policies`

**Query Template:** `PolicyRecommendation.objects.all().select_related("created_by").order_by("-created_at")[:20]`


### policies_stakeholder_count

**Description:** Policies ranked by stakeholder count

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Policies by stakeholder count`
- `Policy recommendations by partner number`
- `Policies ranked by stakeholders`

**Query Template:** `PolicyRecommendation.objects.annotate(stakeholder_count=Count("stakeholders")).filter(stakeholder_co...`


## PROJECTS

**Total Templates:** 45

### count_projects_by_ministry

**Description:** Count projects by ministry/agency

**Priority:** 9/100
**Intent:** data_query
**Result Type:** count

**Required Entities:** ministry

**Example Queries:**
- `How many projects by MSWDO?`
- `Count PPAs from MILG`
- `Total programs of BARMM`
- `Projects by Ministry of Health`

**Query Template:** `MonitoringEntry.objects.filter(implementing_agency__icontains="{ministry}").count()`


### count_projects_by_sector

**Description:** Count projects by sector

**Priority:** 9/100
**Intent:** data_query
**Result Type:** count

**Required Entities:** sector

**Example Queries:**
- `How many projects in education sector?`
- `Count PPAs in health sector`
- `Total programs in infrastructure sector`
- `Projects in economic sector`

**Query Template:** `MonitoringEntry.objects.filter(sector__icontains="{sector}").count()`


### count_projects_by_location

**Description:** Count projects in location

**Priority:** 9/100
**Intent:** data_query
**Result Type:** count

**Required Entities:** location

**Example Queries:**
- `How many projects in Region IX?`
- `Count PPAs in Zamboanga`
- `Total programs in Cotabato`
- `Projects in Region XII`

**Query Template:** `MonitoringEntry.objects.filter(Q(location__icontains="{location}")).count()`


### count_overdue_projects

**Description:** Count overdue projects

**Priority:** 9/100
**Intent:** data_query
**Result Type:** count

**Example Queries:**
- `How many overdue projects?`
- `Count delayed PPAs`
- `Total late programs`
- `Number of overdue projects`

**Query Template:** `MonitoringEntry.objects.filter(end_date__lt=timezone.now().date(), status="ongoing").count()`


### budget_by_location

**Description:** Total budget in specific location

**Priority:** 9/100
**Intent:** data_query
**Result Type:** aggregate

**Required Entities:** location

**Example Queries:**
- `Budget in Region IX`
- `Budget for Zamboanga`
- `Budget allocated to Cotabato`
- `Total budget in Region XII`

**Query Template:** `MonitoringEntry.objects.filter(Q(location__icontains="{location}")).aggregate(total=Sum("budget_allo...`


### beneficiaries_by_location

**Description:** Total beneficiaries in location

**Priority:** 9/100
**Intent:** data_query
**Result Type:** aggregate

**Required Entities:** location

**Example Queries:**
- `Beneficiaries in Region IX`
- `Beneficiaries at Zamboanga`
- `Beneficiaries from Cotabato`
- `People served in Region XII`

**Query Template:** `MonitoringEntry.objects.filter(Q(location__icontains="{location}")).aggregate(total=Sum("target_bene...`


### list_active_projects

**Description:** List active/ongoing projects

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show me active projects`
- `List ongoing PPAs`
- `Display active programs`
- `Get ongoing projects`

**Query Template:** `MonitoringEntry.objects.filter(status="ongoing").order_by("-start_date")[:30]`


### list_completed_projects

**Description:** List completed projects

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show me completed projects`
- `List finished PPAs`
- `Display done programs`
- `Get completed projects`

**Query Template:** `MonitoringEntry.objects.filter(status="completed").order_by("-end_date")[:30]`


### list_projects_by_ministry

**Description:** List projects by specific ministry/agency

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** ministry

**Example Queries:**
- `Show me projects by MSWDO`
- `List PPAs from MILG`
- `Display programs of BARMM`
- `Projects by Ministry of Health`

**Query Template:** `MonitoringEntry.objects.filter(implementing_agency__icontains="{ministry}").order_by("-created_at")[...`


### list_projects_by_sector

**Description:** List projects by sector

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** sector

**Example Queries:**
- `Show me projects in education sector`
- `List PPAs in health sector`
- `Display programs in infrastructure sector`
- `Projects in economic sector`

**Query Template:** `MonitoringEntry.objects.filter(sector__icontains="{sector}").order_by("-budget_allocation")[:30]`


### list_projects_by_location

**Description:** List projects in specific location

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** location

**Example Queries:**
- `Show me projects in Region IX`
- `List PPAs in Zamboanga`
- `Display programs in Cotabato`
- `Projects in Region XII`

**Query Template:** `MonitoringEntry.objects.filter(Q(location__icontains="{location}")).order_by("-start_date")[:30]`


### list_overdue_projects

**Description:** List overdue projects

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show me overdue projects`
- `List delayed PPAs`
- `Display late programs`
- `Get overdue projects`

**Query Template:** `MonitoringEntry.objects.filter(end_date__lt=timezone.now().date(), status="ongoing").order_by("end_d...`


### count_active_projects

**Description:** Count active/ongoing projects

**Priority:** 8/100
**Intent:** data_query
**Result Type:** count

**Example Queries:**
- `How many active projects?`
- `Count ongoing PPAs`
- `Total active programs`
- `Number of ongoing projects`

**Query Template:** `MonitoringEntry.objects.filter(status="ongoing").count()`


### count_completed_projects

**Description:** Count completed projects

**Priority:** 8/100
**Intent:** data_query
**Result Type:** count

**Example Queries:**
- `How many completed projects?`
- `Count finished PPAs`
- `Total completed programs`
- `Number of done projects`

**Query Template:** `MonitoringEntry.objects.filter(status="completed").count()`


### count_projects_by_type

**Description:** Count entries by type

**Priority:** 8/100
**Intent:** data_query
**Result Type:** count

**Required Entities:** type

**Example Queries:**
- `How many project entries?`
- `Count program PPAs`
- `Total activity entries`
- `Number of programs`

**Query Template:** `MonitoringEntry.objects.filter(entry_type__icontains="{type}").count()`


### count_projects_by_year

**Description:** Count projects by year

**Priority:** 8/100
**Intent:** data_query
**Result Type:** count

**Required Entities:** year

**Example Queries:**
- `How many projects in 2025?`
- `Count PPAs started in 2024`
- `Total programs from 2023`
- `Projects in 2024`

**Query Template:** `MonitoringEntry.objects.filter(start_date__year={year}).count()`


### count_projects_ending_soon

**Description:** Count projects ending within 30 days

**Priority:** 8/100
**Intent:** data_query
**Result Type:** count

**Example Queries:**
- `How many projects ending soon?`
- `Count PPAs ending this month`
- `Total programs ending soon`
- `Projects ending within 30 days`

**Query Template:** `MonitoringEntry.objects.filter(end_date__gte=timezone.now().date(), end_date__lte=timezone.now().dat...`


### total_budget_allocation

**Description:** Total budget allocation across all projects

**Priority:** 8/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Total budget allocation`
- `Overall budget for PPAs`
- `Combined project budget`
- `What is the total budget?`

**Query Template:** `MonitoringEntry.objects.aggregate(total=Sum("budget_allocation"))["total"]`


### budget_by_sector

**Description:** Budget breakdown by sector

**Priority:** 8/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Budget by sector`
- `Budget per sector`
- `Budget for each sector`
- `Sector budget breakdown`

**Query Template:** `MonitoringEntry.objects.values("sector").annotate(total_budget=Sum("budget_allocation")).order_by("-...`


### budget_by_ministry

**Description:** Budget breakdown by ministry/agency

**Priority:** 8/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Budget by ministry`
- `Budget per agency`
- `Budget for each MOA`
- `Ministry budget breakdown`

**Query Template:** `MonitoringEntry.objects.values("implementing_agency").annotate(total_budget=Sum("budget_allocation")...`


### budget_utilization_rate

**Description:** Overall budget utilization statistics

**Priority:** 8/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Budget utilization rate`
- `Budget usage percentage`
- `Budget spending rate`
- `Show me budget utilization`

**Query Template:** `MonitoringEntry.objects.aggregate(total_allocated=Sum("budget_allocation"), total_utilized=Sum("budg...`


### underutilized_budget_projects

**Description:** Projects with low budget utilization (<50%)

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Underutilized budget projects`
- `Low utilization PPAs`
- `Projects with unused budget`
- `Budget underutilization`

**Query Template:** `MonitoringEntry.objects.filter(budget_utilized__lt=F("budget_allocation") * 0.5, status="ongoing").o...`


### budget_range_projects

**Description:** Projects within budget range

**Priority:** 8/100
**Intent:** data_query
**Result Type:** count

**Required Entities:** min_budget, max_budget

**Example Queries:**
- `Projects with budget from 1000000 to 5000000`
- `PPAs with budget between 500000 and 2000000`
- `Programs with budget from 2M to 10M`

**Query Template:** `MonitoringEntry.objects.filter(budget_allocation__gte={min_budget}, budget_allocation__lte={max_budg...`


### budget_overrun_projects

**Description:** Projects with budget overruns

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Budget overrun projects`
- `Over budget PPAs`
- `Projects that exceeded budget`
- `Budget overruns`

**Query Template:** `MonitoringEntry.objects.filter(budget_utilized__gt=F("budget_allocation")).order_by("-budget_utilize...`


### total_beneficiaries

**Description:** Total beneficiaries across all projects

**Priority:** 8/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Total beneficiaries`
- `Overall people served`
- `Combined target population`
- `How many beneficiaries?`

**Query Template:** `MonitoringEntry.objects.aggregate(total=Sum("target_beneficiaries"))["total"]`


### beneficiaries_by_sector

**Description:** Beneficiaries by sector

**Priority:** 8/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Beneficiaries by sector`
- `Beneficiaries per sector`
- `Beneficiaries in each sector`
- `Sector beneficiary breakdown`

**Query Template:** `MonitoringEntry.objects.values("sector").annotate(total_beneficiaries=Sum("target_beneficiaries")).o...`


### project_completion_rates

**Description:** Overall completion statistics

**Priority:** 8/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Project completion rates`
- `PPA completion percentage`
- `Program completion status`
- `Overall completion rates`

**Query Template:** `MonitoringEntry.objects.aggregate(avg_completion=Avg("completion_percentage"), total=Count("id"), co...`


### projects_ending_this_month

**Description:** Projects ending within 30 days

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Projects ending this month`
- `PPAs ending soon`
- `Programs ending this quarter`
- `Projects ending within 30 days`

**Query Template:** `MonitoringEntry.objects.filter(end_date__gte=timezone.now().date(), end_date__lte=timezone.now().dat...`


### project_timeline_by_year

**Description:** Project timeline by year

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** year

**Example Queries:**
- `Projects timeline by 2025`
- `PPAs timeline in 2024`
- `Programs timeline by 2023`
- `Show project timeline in 2025`

**Query Template:** `MonitoringEntry.objects.filter(start_date__year={year}).values("id", "title", "start_date", "end_dat...`


### delayed_projects_analysis

**Description:** Analysis of delayed/overdue projects

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Delayed projects analysis`
- `Overdue PPAs report`
- `Late programs analysis`
- `Projects behind schedule`

**Query Template:** `MonitoringEntry.objects.filter(end_date__lt=timezone.now().date(), status="ongoing").annotate(delay_...`


### list_recent_projects

**Description:** List recently added projects

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Recent projects`
- `Latest PPAs`
- `Newly added programs`
- `Show recent projects`

**Query Template:** `MonitoringEntry.objects.all().order_by("-created_at")[:20]`


### list_projects_by_type

**Description:** List entries by type (project/program/activity)

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** type

**Example Queries:**
- `Show me project entries`
- `List program PPAs`
- `Display activity entries`
- `Show programs`

**Query Template:** `MonitoringEntry.objects.filter(entry_type__icontains="{type}").order_by("-created_at")[:30]`


### list_high_budget_projects

**Description:** List projects with budget over 10M

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show me high budget projects`
- `List large budget PPAs`
- `Display high budget programs`
- `Projects with large budgets`

**Query Template:** `MonitoringEntry.objects.filter(budget_allocation__gte=10000000).order_by("-budget_allocation")[:20]`


### count_total_projects

**Description:** Count total projects/PPAs

**Priority:** 7/100
**Intent:** data_query
**Result Type:** count

**Example Queries:**
- `How many projects are there?`
- `Total PPAs`
- `Count all projects`
- `Number of programs`
- `How many activities?`

**Query Template:** `MonitoringEntry.objects.count()`


### top_budget_projects

**Description:** Top 10 projects by budget

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Top budget projects`
- `Highest funded PPAs`
- `Largest budget programs`
- `Show me top funded projects`

**Query Template:** `MonitoringEntry.objects.filter(budget_allocation__isnull=False).order_by("-budget_allocation")[:10]`


### budget_balance_analysis

**Description:** Total budget balance/remaining

**Priority:** 7/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Budget balance`
- `Budget remaining`
- `How much budget is left?`
- `Total budget balance`

**Query Template:** `MonitoringEntry.objects.aggregate(total_balance=Sum("budget_balance"), total_allocated=Sum("budget_a...`


### project_outcomes

**Description:** Project outcomes and achievements

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Project outcomes`
- `PPA results`
- `Program achievements`
- `Project impact`

**Query Template:** `MonitoringEntry.objects.filter(status="completed").values("id", "title", "outcomes", "target_benefic...`


### highest_impact_projects

**Description:** Projects with highest beneficiary impact

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Highest impact projects`
- `Most impact PPAs`
- `Top impact programs`
- `Projects with highest impact`

**Query Template:** `MonitoringEntry.objects.filter(actual_beneficiaries__isnull=False).order_by("-actual_beneficiaries")...`


### beneficiary_reach_rate

**Description:** Beneficiary reach/achievement rates

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Beneficiary reach rate`
- `Beneficiary achievement percentage`
- `Beneficiary attainment rate`
- `How many beneficiaries reached?`

**Query Template:** `MonitoringEntry.objects.filter(target_beneficiaries__gt=0, actual_beneficiaries__isnull=False).annot...`


### communities_served

**Description:** Total communities served by projects

**Priority:** 7/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Communities served`
- `Barangays reached`
- `Communities covered`
- `How many communities benefited?`

**Query Template:** `MonitoringEntry.objects.aggregate(total=Sum("communities_served"))["total"]`


### sector_impact_comparison

**Description:** Compare impact across sectors

**Priority:** 7/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Compare impact by sector`
- `Comparison of outcomes across sectors`
- `Compare results by sector`
- `Sector impact comparison`

**Query Template:** `MonitoringEntry.objects.values("sector").annotate(total_beneficiaries=Sum("actual_beneficiaries"), t...`


### active_project_timeline

**Description:** Timeline of active projects

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Active projects timeline`
- `Ongoing PPAs timeline`
- `Active programs timeline`
- `Show ongoing project timeline`

**Query Template:** `MonitoringEntry.objects.filter(status="ongoing").values("id", "title", "start_date", "end_date", "co...`


### completion_by_quarter

**Description:** Project completion by quarter

**Priority:** 7/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Projects completion by quarter`
- `PPAs completion by quarter`
- `Program completion by quarter`
- `Quarterly completion report`

**Query Template:** `MonitoringEntry.objects.filter(status="completed").annotate(quarter=ExtractQuarter("end_date"), year...`


### project_duration_analysis

**Description:** Project duration statistics

**Priority:** 7/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `Project duration analysis`
- `PPA duration average`
- `Program duration statistics`
- `Average project duration`

**Query Template:** `MonitoringEntry.objects.filter(start_date__isnull=False, end_date__isnull=False).annotate(duration=E...`


### list_all_projects

**Description:** List all projects/PPAs

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show me projects`
- `List all PPAs`
- `Display programs`
- `Get all projects`

**Query Template:** `MonitoringEntry.objects.all().order_by("-created_at")[:20]`


## STAFF

**Total Templates:** 15

### tasks_my_tasks

**Description:** Show current user tasks

**Priority:** 10/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `My tasks`
- `Show my tasks`
- `Get my tasks`
- `List my tasks`
- `What are my tasks?`

**Query Template:** `Task.objects.filter(assigned_to=request.user, status__in=["pending", "in_progress"]).order_by("due_d...`


### tasks_overdue

**Description:** Show overdue tasks

**Priority:** 10/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Overdue tasks`
- `Late tasks`
- `Past due tasks`
- `Show overdue tasks`
- `My overdue tasks`

**Query Template:** `Task.objects.filter(assigned_to=request.user, status__in=["pending", "in_progress"], due_date__lt=ti...`


### tasks_today

**Description:** Show tasks due today

**Priority:** 10/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Today tasks`
- `Today's tasks`
- `Tasks for today`
- `What tasks do I have today?`
- `Show today tasks`

**Query Template:** `Task.objects.filter(assigned_to=request.user, due_date__date=timezone.now().date()).order_by("-prior...`


### staff_search_by_name

**Description:** Search staff by name

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** name

**Example Queries:**
- `Find John staff`
- `Search Maria user`
- `Who is Ahmed?`
- `Find staff named Sarah`

**Query Template:** `User.objects.filter(Q(first_name__icontains="{name}") | Q(last_name__icontains="{name}")).order_by("...`


### tasks_high_priority

**Description:** Show high priority tasks

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `High priority tasks`
- `Urgent tasks`
- `Critical tasks`
- `Show high priority tasks`
- `My urgent tasks`

**Query Template:** `Task.objects.filter(assigned_to=request.user, priority__in=["high", "critical"], status__in=["pendin...`


### staff_by_role

**Description:** List staff by role/group

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** role

**Example Queries:**
- `Show me coordinators`
- `List admins`
- `Display managers`
- `Get all coordinators`
- `Show staff users`

**Query Template:** `User.objects.filter(is_active=True, groups__name__icontains="{role}").order_by("last_name")[:50]`


### staff_count_total

**Description:** Count total active staff

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `How many staff do we have?`
- `Count users`
- `Total staff`
- `Number of team members`
- `Staff count`

**Query Template:** `User.objects.filter(is_active=True).count()`


### staff_count_by_role

**Description:** Count staff by role

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** role

**Example Queries:**
- `How many coordinators?`
- `Count admins`
- `Total managers`
- `Number of coordinators`

**Query Template:** `User.objects.filter(is_active=True, groups__name__icontains="{role}").count()`


### tasks_count_my_tasks

**Description:** Count current user tasks

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `How many my tasks?`
- `Count my tasks`
- `How many tasks do I have?`
- `Number of my tasks`

**Query Template:** `Task.objects.filter(assigned_to=request.user, status__in=["pending", "in_progress"]).count()`


### staff_all_users

**Description:** List all active staff members

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show me all staff`
- `List users`
- `Display team members`
- `Get all staff`
- `Staff directory`

**Query Template:** `User.objects.filter(is_active=True).order_by("last_name", "first_name")[:50]`


### tasks_completed

**Description:** Show completed tasks

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Completed tasks`
- `Done tasks`
- `Finished tasks`
- `My completed tasks`
- `Show completed tasks`

**Query Template:** `Task.objects.filter(assigned_to=request.user, status="completed").order_by("-updated_at")[:30]`


### preferences_notification_settings

**Description:** Show notification settings

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Notification settings`
- `Alert preferences`
- `Email settings`
- `My notification settings`
- `Show notification preferences`

**Query Template:** `request.user.notification_preferences`


### activity_recent

**Description:** Show recent user activity

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Recent activity`
- `Latest activity`
- `My activity`
- `My actions`
- `Activity history`

**Query Template:** `AuditLog.objects.filter(user=request.user).select_related("content_type").order_by("-timestamp")[:30...`


### preferences_dashboard_config

**Description:** Show dashboard preferences

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Dashboard settings`
- `Home preferences`
- `Dashboard config`
- `Dashboard customization`
- `My dashboard settings`

**Query Template:** `request.user.dashboard_preferences`


### activity_work_log

**Description:** Show work log and contributions

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Work log`
- `Time log`
- `My contributions`
- `Show my work`
- `Work summary`

**Query Template:** `Task.objects.filter(assigned_to=request.user).values("status").annotate(count=Count("id"), hours=Sum...`


## STAKEHOLDERS

**Total Templates:** 10

### count_stakeholders_by_type

**Description:** Count stakeholders by type (religious, youth, women, etc.)

**Priority:** 9/100
**Intent:** data_query
**Result Type:** count

**Required Entities:** stakeholder_type

**Example Queries:**
- `How many religious leaders?`
- `Count ulama stakeholders`
- `Total youth leaders`
- `How many imam?`
- `Women leaders count`

**Query Template:** `Stakeholder.objects.filter(stakeholder_type__icontains='{stakeholder_type}').count()`


### count_religious_leaders

**Description:** Count religious leaders (Ulama, Imams, Ustadz)

**Priority:** 9/100
**Intent:** data_query
**Result Type:** count

**Example Queries:**
- `How many ulama?`
- `Count imams`
- `Total ustadz`
- `Religious leaders count`
- `How many religious teachers?`

**Query Template:** `Stakeholder.objects.filter(Q(stakeholder_type='ulama') | Q(stakeholder_type='imam') | Q(stakeholder_...`


### count_stakeholders_by_influence

**Description:** Count stakeholders by influence level

**Priority:** 8/100
**Intent:** data_query
**Result Type:** count

**Required Entities:** influence

**Example Queries:**
- `How many high influence stakeholders?`
- `Count very high influence leaders`
- `Total emerging influence stakeholders`
- `Medium influence leaders count`
- `How many influential stakeholders?`

**Query Template:** `Stakeholder.objects.filter(influence_level__icontains='{influence}').count()`


### count_stakeholders_by_engagement

**Description:** Count stakeholders by engagement level

**Priority:** 8/100
**Intent:** data_query
**Result Type:** count

**Required Entities:** engagement

**Example Queries:**
- `How many active stakeholders?`
- `Count very active leaders`
- `Total inactive stakeholders`
- `Limited engagement leaders count`
- `Moderate stakeholders count`

**Query Template:** `Stakeholder.objects.filter(engagement_level__icontains='{engagement}').count()`


### list_high_influence_stakeholders

**Description:** List stakeholders with high/very high influence

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show high influence stakeholders`
- `List very high influence leaders`
- `Who are the influential stakeholders?`
- `Find high influence leaders`
- `Which leaders have high influence?`

**Query Template:** `Stakeholder.objects.filter(influence_level__in=['high', 'very_high']).select_related('community__bar...`


### list_inactive_stakeholders

**Description:** List inactive or limited engagement stakeholders

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Show inactive stakeholders`
- `List stakeholders with limited engagement`
- `Who are the inactive leaders?`
- `Find stakeholders needing re-engagement`
- `Which leaders are inactive?`

**Query Template:** `Stakeholder.objects.filter(engagement_level__in=['inactive', 'limited'], is_active=True).select_rela...`


### count_community_organizations

**Description:** Count CSOs and associations by community

**Priority:** 7/100
**Intent:** data_query
**Result Type:** aggregate

**Example Queries:**
- `How many CSOs by community?`
- `Count civil society organizations`
- `Total associations per community`
- `Community organizations count`
- `CSO count`

**Query Template:** `OBCCommunity.objects.aggregate(total_csos=Sum('csos_count'), total_associations=Sum('associations_co...`


### stakeholder_engagement_history

**Description:** Show engagement history for specific stakeholder

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** stakeholder_name

**Example Queries:**
- `Engagement history for Ustadz Abdullah`
- `Activities record of Imam Hassan`
- `Interactions by Datu Miguel`
- `Show engagement for Barangay Captain Maria`
- `Stakeholder activities for Juan Santos`

**Query Template:** `Stakeholder.objects.filter(Q(full_name__icontains='{stakeholder_name}') | Q(nickname__icontains='{st...`


### stakeholders_by_expertise

**Description:** Find stakeholders by specific expertise or skills

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** expertise

**Example Queries:**
- `Stakeholders with expertise in education`
- `Leaders having health skills`
- `Experts by agriculture specialization`
- `Stakeholders with livelihood expertise`
- `Who has expertise in peace building?`

**Query Template:** `Stakeholder.objects.filter(Q(position__icontains='{expertise}') | Q(responsibilities__icontains='{ex...`


### stakeholder_networks_analysis

**Description:** Analyze stakeholder networks and external connections

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Stakeholder connections by community`
- `Network analysis`
- `Show stakeholder relationships`
- `Network connections`
- `Stakeholder network analysis`

**Query Template:** `Stakeholder.objects.exclude(external_connections='').select_related('community__barangay').values('f...`


## TEMPORAL

**Total Templates:** 30

### count_last_n_days

**Description:** Count items in last N days

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** number

**Optional Entities:** model_type

**Example Queries:**
- `Last 7 days`
- `Past 30 days assessments`
- `Previous 90 days PPAs`
- `How many in last 14 days?`

**Query Template:** `{model}.objects.filter(created_at__gte=timezone.now() - timedelta(days={days})).count()`


### count_between_dates

**Description:** Count items between two dates

**Priority:** 9/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** date_start, date_end

**Optional Entities:** model_type

**Example Queries:**
- `Between January 1 and March 31`
- `From 2024-01-01 to 2024-06-30`
- `Assessments between Jan 1 and Dec 31 2024`

**Query Template:** `{model}.objects.filter(created_at__gte="{start_date}", created_at__lte="{end_date}").count()`


### count_by_date_range

**Description:** Count items within date range

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** time_period

**Optional Entities:** model_type

**Example Queries:**
- `Assessments last 30 days`
- `PPAs this quarter`
- `Projects in last 6 months`
- `Meetings last week`
- `How many assessments in the past 90 days?`

**Query Template:** `{model}.objects.filter(created_at__gte=timezone.now() - timedelta({period}={value})).count()`


### count_by_fiscal_year

**Description:** Count items in specific fiscal year

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** fiscal_year

**Optional Entities:** model_type

**Example Queries:**
- `Projects in FY 2024`
- `Assessments for fiscal year 2025`
- `PPAs during FY 2023`
- `How many projects in fiscal year 2024?`

**Query Template:** `{model}.objects.filter(start_date__year={year}).count()`


### count_by_month

**Description:** Count items in specific month

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** month

**Optional Entities:** year, model_type

**Example Queries:**
- `Assessments in January`
- `PPAs during March 2024`
- `Projects for December 2023`
- `How many assessments in January 2024?`

**Query Template:** `{model}.objects.filter(created_at__month={month}, created_at__year={year}).count()`


### count_year_to_date

**Description:** Count items year to date

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type

**Example Queries:**
- `YTD assessments`
- `Year to date PPAs`
- `This year projects`
- `How many assessments year to date?`

**Query Template:** `{model}.objects.filter(created_at__year=timezone.now().year).count()`


### count_current_period

**Description:** Count items in current period

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** time_period

**Optional Entities:** model_type

**Example Queries:**
- `This week assessments`
- `Current month PPAs`
- `This quarter projects`
- `Current year total`

**Query Template:** `{model}.objects.filter(created_at__gte={period_start}).count()`


### historical_comparison

**Description:** Compare two years

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** years

**Optional Entities:** model_type

**Example Queries:**
- `2024 vs 2023 comparison`
- `Compare 2025 and 2024`
- `2023 versus 2022`
- `Year over year 2024 vs 2023`

**Query Template:** `{model}.objects.filter(Q(created_at__year={year1}) | Q(created_at__year={year2})).values("created_at...`


### overdue_analysis

**Description:** Overdue items analysis

**Priority:** 8/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type

**Example Queries:**
- `Items overdue by days`
- `Overdue analysis`
- `Past due items`
- `Delayed projects`

**Query Template:** `{model}.objects.filter(target_date__lt=timezone.now(), status__in=["planning", "in_progress"]).annot...`


### count_by_quarter

**Description:** Group items by quarter

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type, year

**Example Queries:**
- `Budget by quarter`
- `PPAs per quarter`
- `Projects by quarter 2024`
- `Show quarterly distribution`

**Query Template:** `{model}.objects.annotate(quarter=ExtractQuarter("start_date")).values("quarter").annotate(count=Coun...`


### count_before_date

**Description:** Count items before specific date

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** date_end

**Optional Entities:** model_type

**Example Queries:**
- `Before December 2024`
- `Assessments before 2024-06-30`
- `PPAs before January 2025`

**Query Template:** `{model}.objects.filter(created_at__lt="{date}").count()`


### count_after_date

**Description:** Count items after specific date

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** date_start

**Optional Entities:** model_type

**Example Queries:**
- `After January 2025`
- `Assessments after 2024-12-31`
- `PPAs after June 1`

**Query Template:** `{model}.objects.filter(created_at__gt="{date}").count()`


### assessment_completion_trends

**Description:** Assessment completion trends by month

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** time_period

**Example Queries:**
- `Assessment trends over time`
- `Assessment completion trends`
- `Show assessment trends`
- `Track assessment completions`

**Query Template:** `Assessment.objects.filter(status="completed").annotate(month=TruncMonth("completion_date")).values("...`


### ppa_implementation_trends

**Description:** PPA implementation trends by month

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** time_period

**Example Queries:**
- `Project starts by month`
- `PPA implementation trends`
- `Project trends over time`
- `Monthly project launches`

**Query Template:** `MonitoringEntry.objects.annotate(month=TruncMonth("start_date")).values("month").annotate(count=Coun...`


### budget_utilization_trends

**Description:** Budget utilization trends by quarter

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** time_period

**Example Queries:**
- `Budget spend over quarters`
- `Budget utilization trends`
- `Quarterly budget spending`
- `Track budget over time`

**Query Template:** `MonitoringEntry.objects.annotate(quarter=ExtractQuarter("start_date")).values("quarter").annotate(to...`


### needs_identification_trends

**Description:** Needs identification trends by month

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** time_period

**Example Queries:**
- `Needs identified per month`
- `Needs identification trends`
- `Track needs over time`
- `Monthly needs discovery`

**Query Template:** `Need.objects.annotate(month=TruncMonth("created_at")).values("month").annotate(count=Count("id")).or...`


### engagement_frequency_trends

**Description:** Engagement frequency trends by month

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** time_period

**Example Queries:**
- `Meeting frequency trends`
- `Engagement trends over time`
- `Stakeholder meeting patterns`
- `Track engagement frequency`

**Query Template:** `StakeholderEngagement.objects.annotate(month=TruncMonth("engagement_date")).values("month").annotate...`


### growth_rate_analysis

**Description:** Year-over-year growth rate analysis

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type

**Example Queries:**
- `YoY growth in assessments`
- `Year over year project growth`
- `Growth rate analysis`
- `Annual growth trends`

**Query Template:** `{model}.objects.annotate(year=ExtractYear("created_at")).values("year").annotate(count=Count("id"))....`


### period_comparisons

**Description:** Period-to-period comparison

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** quarters

**Optional Entities:** model_type, year

**Example Queries:**
- `Q1 vs Q2 comparison`
- `Compare Q3 and Q4`
- `Quarter 1 versus quarter 2`
- `Q2 2024 vs Q2 2023`

**Query Template:** `{model}.objects.filter(Q(created_at__quarter={q1}) | Q(created_at__quarter={q2})).values("created_at...`


### cumulative_totals

**Description:** Cumulative totals over time

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type, time_period

**Example Queries:**
- `Cumulative assessments over time`
- `Running total of PPAs`
- `Accumulated projects`
- `Show cumulative totals`

**Query Template:** `{model}.objects.filter(created_at__lte=timezone.now()).annotate(month=TruncMonth("created_at")).valu...`


### milestone_tracking

**Description:** Time to complete by category

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type

**Example Queries:**
- `Time to complete by project type`
- `Average completion time`
- `Duration by category`
- `Milestone completion tracking`

**Query Template:** `MonitoringEntry.objects.filter(completion_date__isnull=False).annotate(duration=F("completion_date")...`


### completion_duration

**Description:** Average completion duration by type

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** group_by

**Optional Entities:** model_type

**Example Queries:**
- `Average duration by type`
- `Mean completion time by category`
- `Duration analysis by project type`
- `Average time to complete`

**Query Template:** `{model}.objects.filter(completion_date__isnull=False).annotate(duration=F("completion_date") - F("st...`


### aging_analysis

**Description:** Age distribution analysis

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type

**Example Queries:**
- `Items by age (0-30, 30-60, 60+ days)`
- `Aging analysis`
- `Age distribution`
- `How old are items?`

**Query Template:** `{model}.objects.annotate(age_days=(timezone.now() - F("created_at")).days).aggregate(age_0_30=Count(...`


### time_to_approval

**Description:** Average time to approval

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Example Queries:**
- `Average approval time`
- `Time to approval`
- `How long for approval?`
- `Approval duration`

**Query Template:** `MonitoringEntry.objects.filter(approval_date__isnull=False).annotate(approval_time=F("approval_date"...`


### historical_averages

**Description:** Historical averages by period

**Priority:** 7/100
**Intent:** data_query
**Result Type:** list

**Required Entities:** time_period

**Optional Entities:** model_type

**Example Queries:**
- `Historical average by month`
- `Mean per quarter`
- `Average by period`
- `Typical monthly count`

**Query Template:** `{model}.objects.annotate(period=Trunc{period_type}("created_at")).values("period").annotate(count=Co...`


### seasonal_patterns

**Description:** Seasonal pattern analysis by month

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type

**Example Queries:**
- `Seasonal variations`
- `Monthly patterns`
- `Seasonality analysis`
- `Patterns by month`

**Query Template:** `{model}.objects.annotate(month=ExtractMonth("created_at")).values("month").annotate(count=Count("id"...`


### momentum_analysis

**Description:** Momentum and velocity analysis

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type

**Example Queries:**
- `Increasing trends`
- `Momentum analysis`
- `Velocity tracking`
- `Show acceleration`

**Query Template:** `{model}.objects.filter(created_at__gte=timezone.now() - timedelta(days=180)).annotate(week=TruncWeek...`


### forecast_projections

**Description:** Forecast and projection analysis

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type, time_period

**Example Queries:**
- `Projected completions next quarter`
- `Forecast upcoming assessments`
- `Predict next quarter PPAs`
- `Projection analysis`

**Query Template:** `{model}.objects.filter(created_at__gte=timezone.now() - timedelta(days=365)).annotate(quarter=Extrac...`


### recurrence_patterns

**Description:** Recurring event patterns

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type

**Example Queries:**
- `Recurring events schedule`
- `Repeating meetings`
- `Regular assessments pattern`
- `Scheduled engagement frequency`

**Query Template:** `StakeholderEngagement.objects.values("engagement_type").annotate(count=Count("id"), avg_interval=Avg...`


### anniversary_tracking

**Description:** Items created ~1 year ago

**Priority:** 6/100
**Intent:** data_query
**Result Type:** list

**Optional Entities:** model_type

**Example Queries:**
- `Items from 1 year ago`
- `Anniversary tracking`
- `From last year`
- `One year old items`

**Query Template:** `{model}.objects.filter(created_at__gte=timezone.now() - timedelta(days=365), created_at__lte=timezon...`


---

## Entity Types Reference

### model_type

**Used in 59 templates**

Templates: count_by_date_range, count_by_fiscal_year, count_by_month, count_by_quarter, count_year_to_date, count_last_n_days, count_between_dates, count_before_date, count_after_date, count_current_period
... and 49 more

### location

**Used in 30 templates**

Templates: count_communities_by_location, count_ethnicity_location, list_communities_by_location, aggregate_population_by_location, filter_location_livelihood, filter_ethnicity_location_livelihood, demographics_by_location, average_household_size_by_location, ethnic_diversity_by_location, largest_ethnic_group_by_location
... and 20 more

### time_period

**Used in 12 templates**

Templates: count_by_date_range, count_current_period, assessment_completion_trends, ppa_implementation_trends, budget_utilization_trends, needs_identification_trends, engagement_frequency_trends, forecast_projections, cumulative_totals, historical_averages
... and 2 more

### group_by

**Used in 11 templates**

Templates: completion_duration, variance_analysis, coefficient_of_variation, segmentation, efficiency_metrics, budget_efficiency, project_success_rates, completion_time_comparison, cost_per_beneficiary, coverage_comparison
... and 1 more

### field

**Used in 10 templates**

Templates: statistical_summary, distribution_analysis, outlier_detection, variance_analysis, percentile_ranking, coefficient_of_variation, aggregation_by_dimension, confidence_intervals, segmentation, anomaly_detection

### ethnolinguistic_group

**Used in 9 templates**

Templates: count_communities_by_ethnicity, count_ethnicity_location, list_communities_by_ethnicity, filter_ethnicity_livelihood, filter_ethnicity_location_livelihood, population_by_ethnicity, ethnicity_locations, ethnicity_livelihood_correlation, ethnic_population_percentage

### sector

**Used in 7 templates**

Templates: coordination_8673cef5, coordination_86944e46, count_policies_by_sector, list_policies_by_sector, list_projects_by_sector, count_projects_by_sector, needs_without_ppas

### status

**Used in 6 templates**

Templates: mana_86dc98ca, mana_99d9626a, coordination_6a67d560, count_policies_by_status, list_policies_by_status, communities_with_assessments

### type

**Used in 6 templates**

Templates: coordination_69bf2e2e, coordination_023d5abd, coordination_9e96bbb4, count_policies_by_type, list_projects_by_type, count_projects_by_type

### locations

**Used in 6 templates**

Templates: region_vs_region, province_vs_province, municipality_comparison, multi_location_comparison, location_gap_analysis, location_performance_matrix

### ethnolinguistic_groups

**Used in 6 templates**

Templates: ethnicity_demographics, ethnicity_needs, ethnicity_outcomes, ethnicity_coverage, ethnicity_participation, ethnicity_resource_allocation

### livelihood

**Used in 5 templates**

Templates: count_communities_by_livelihood, list_communities_by_livelihood, filter_ethnicity_livelihood, filter_location_livelihood, filter_ethnicity_location_livelihood

### organization

**Used in 5 templates**

Templates: coordination_ee2bef06, coordination_009305cb, coordination_04ba7c77, coordination_5f6b110c, coordination_5242fad1

### date_start

**Used in 5 templates**

Templates: coordination_dec9d5cf, coordination_131a4bff, coordination_e9c39b0a, count_between_dates, count_after_date

### date_end

**Used in 5 templates**

Templates: coordination_dec9d5cf, coordination_131a4bff, coordination_e9c39b0a, count_between_dates, count_before_date

### year

**Used in 5 templates**

Templates: count_projects_by_year, project_timeline_by_year, count_by_month, count_by_quarter, period_comparisons

### entity

**Used in 5 templates**

Templates: help_how_to_create, help_how_to_edit, metadata_created_by, metadata_modified_date, metadata_audit_log

### id

**Used in 4 templates**

Templates: coordination_fca8f522, coordination_5f90c766, coordination_fb2e2029, coordination_aa5317ed

### priority

**Used in 3 templates**

Templates: count_policies_by_priority, list_policies_by_priority, needs_without_ppas

### region

**Used in 3 templates**

Templates: region_by_name, count_provinces_by_region, list_provinces_by_region

### province

**Used in 3 templates**

Templates: province_by_name, count_municipalities_by_province, list_municipalities_by_province

### municipality

**Used in 3 templates**

Templates: municipality_by_name, count_barangays_by_municipality, list_barangays_by_municipality

### number

**Used in 3 templates**

Templates: count_last_n_days, communities_multiple_assessments, multi_stakeholder_assessments

### fields

**Used in 3 templates**

Templates: correlation_analysis, weighted_averages, clustering_analysis

### metric

**Used in 3 templates**

Templates: location_ranking, location_benchmarking, location_gap_analysis

### numbers

**Used in 2 templates**

Templates: aggregate_largest_communities, communities_by_population_range

### name

**Used in 2 templates**

Templates: coordination_a79f8c32, staff_search_by_name

### scope

**Used in 2 templates**

Templates: count_policies_by_scope, list_policies_by_scope

### keyword

**Used in 2 templates**

Templates: search_policies_keyword, navigation_find_page

### ministry

**Used in 2 templates**

Templates: list_projects_by_ministry, count_projects_by_ministry

### role

**Used in 2 templates**

Templates: staff_by_role, staff_count_by_role

### module

**Used in 2 templates**

Templates: help_documentation_link, navigation_go_to_module

### rating

**Used in 2 templates**

Templates: count_communities_by_water_access, count_communities_by_sanitation

### fiscal_year

**Used in 2 templates**

Templates: total_budget_by_fiscal_year, count_by_fiscal_year

### location_level

**Used in 2 templates**

Templates: assessment_geographic_coverage, location_ranking

### reference_id

**Used in 2 templates**

Templates: similarity_analysis, pattern_matching

### date_range

**Used in 1 templates**

Templates: mana_08ab2608

### author

**Used in 1 templates**

Templates: list_policies_by_author

### stakeholder

**Used in 1 templates**

Templates: policies_by_stakeholder

### min_budget

**Used in 1 templates**

Templates: budget_range_projects

### max_budget

**Used in 1 templates**

Templates: budget_range_projects

### urban_rural_classification

**Used in 1 templates**

Templates: municipalities_by_urban_rural

### population_threshold

**Used in 1 templates**

Templates: municipalities_with_high_obc

### barangay

**Used in 1 templates**

Templates: barangay_by_name

### livelihood_type

**Used in 1 templates**

Templates: count_livelihoods_by_type

### income_level

**Used in 1 templates**

Templates: livelihood_income_levels

### stakeholder_type

**Used in 1 templates**

Templates: count_stakeholders_by_type

### influence

**Used in 1 templates**

Templates: count_stakeholders_by_influence

### engagement

**Used in 1 templates**

Templates: count_stakeholders_by_engagement

### stakeholder_name

**Used in 1 templates**

Templates: stakeholder_engagement_history

### expertise

**Used in 1 templates**

Templates: stakeholders_by_expertise

### month

**Used in 1 templates**

Templates: count_by_month

### quarters

**Used in 1 templates**

Templates: period_comparisons

### years

**Used in 1 templates**

Templates: historical_comparison

### community_id

**Used in 1 templates**

Templates: community_assessment_history

### thresholds

**Used in 1 templates**

Templates: distribution_analysis

### percentile

**Used in 1 templates**

Templates: percentile_ranking

### dimensions

**Used in 1 templates**

Templates: aggregation_by_dimension

### confidence_level

**Used in 1 templates**

Templates: confidence_intervals

### profile_attributes

**Used in 1 templates**

Templates: pattern_matching

### grouping_fields

**Used in 1 templates**

Templates: grouping_by_characteristics

### location_field

**Used in 1 templates**

Templates: hotspot_identification

### threshold

**Used in 1 templates**

Templates: hotspot_identification

### hierarchy_field

**Used in 1 templates**

Templates: hierarchy_analysis

### factors

**Used in 1 templates**

Templates: factor_analysis

### risk_factors

**Used in 1 templates**

Templates: risk_scoring

### success_criteria

**Used in 1 templates**

Templates: success_indicators

### projection_factor

**Used in 1 templates**

Templates: gap_prediction

### efficiency_fields

**Used in 1 templates**

Templates: efficiency_metrics

### prediction_factors

**Used in 1 templates**

Templates: performance_prediction

### warning_criteria

**Used in 1 templates**

Templates: early_warning_indicators

### impact_factors

**Used in 1 templates**

Templates: impact_prediction

### optimization_criteria

**Used in 1 templates**

Templates: resource_optimization

### metrics

**Used in 1 templates**

Templates: location_performance_matrix

### coverage_criteria

**Used in 1 templates**

Templates: coverage_comparison

### performance_metric

**Used in 1 templates**

Templates: performance_benchmarking


---

## Intent Types Reference

### data_query

**470 templates use this intent**
