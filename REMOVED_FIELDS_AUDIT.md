# Comprehensive Audit: Removed Database Fields Still Referenced in Code

**Date:** 2025-10-25  
**Thoroughness:** Very Thorough  
**Status:** Critical Issues Found

---

## Executive Summary

This audit identified **5 database fields** that were removed via migrations but **9 code locations** still reference them. These references will cause runtime errors (FieldError or KeyError) when:
- Serializers try to include removed fields
- Views try to aggregate data on removed fields
- Data aggregation services reference removed fields

All issues are in the `communities` app migrations and affect the `OBCCommunity` and `MunicipalityCoverage` models.

---

## Removed Fields Inventory

### 1. children_0_12 and youth_13_30
- **Migration:** `/src/communities/migrations/0012_remove_municipalitycoverage_children_0_12_and_more.py`
- **Removed from:** 
  - `OBCCommunity` (line 23)
  - `MunicipalityCoverage` (line 15)
- **Reason:** Replaced with more granular age ranges: `children_0_9`, `adolescents_10_14`, `youth_15_30`
- **Replacement Fields:** 
  - `children_0_9` (PositiveIntegerField)
  - `adolescents_10_14` (PositiveIntegerField) 
  - `youth_15_30` (PositiveIntegerField)

### 2. has_madrasah and has_mosque
- **Migration:** `/src/communities/migrations/0011_remove_municipalitycoverage_has_madrasah_and_more.py`
- **Removed from:**
  - `MunicipalityCoverage` (lines 82-87)
  - `OBCCommunity` (Note: Never actually added, so not removed)
- **Reason:** Replaced with count fields for more precise tracking
- **Replacement Fields:**
  - `madrasah_count` (PositiveIntegerField, default=0)
  - `mosques_count` (PositiveIntegerField, default=0)

### 3. elderly_count
- **Migration:** `/src/communities/migrations/0014_remove_municipalitycoverage_elderly_count_and_more.py`
- **Removed from:**
  - `OBCCommunity` (line 30)
  - `MunicipalityCoverage` (line 18)
- **Reason:** Consolidated with other vulnerable sector fields
- **Replacement Field:** None - field was deprecated without direct replacement

### 4. religious_leaders_ulama_count
- **Migration:** `/src/communities/migrations/0014_remove_municipalitycoverage_elderly_count_and_more.py`
- **Removed from:**
  - `OBCCommunity` (line 34)
  - `MunicipalityCoverage` (line 22)
- **Reason:** Consolidated into a single `religious_leaders_count` field
- **Replacement Field:** `religious_leaders_count` (PositiveIntegerField)

### 5. teachers_asatidz_count
- **Migration:** `/src/communities/migrations/0014_remove_municipalitycoverage_elderly_count_and_more.py`
- **Removed from:**
  - `OBCCommunity` (line 38)
  - `MunicipalityCoverage` (line 26)
- **Reason:** Consolidated into a single `asatidz_count` field
- **Replacement Field:** `asatidz_count` (PositiveIntegerField)

---

## Code References (Issues Found)

### Issue 1: OBCCommunitySerializer Includes Removed Fields
**File:** `/src/communities/serializers.py`  
**Lines:** 118-119  
**Class:** `OBCCommunitySerializer`  
**Severity:** HIGH - Will cause FieldError when serializing instances

```python
# BROKEN CODE
class Meta:
    model = OBCCommunity
    fields = [
        ...
        "children_0_12",      # LINE 118 - REMOVED FIELD
        "youth_13_30",        # LINE 119 - REMOVED FIELD
        ...
    ]
```

**Impact:** Any API call using `OBCCommunitySerializer` will fail with:
```
FieldDoesNotExist: OBCCommunity has no field named 'children_0_12'
```

**Fix Required:** Replace with:
```python
"children_0_9",
"adolescents_10_14",
"youth_15_30",
```

---

### Issue 2: Common Views - Vulnerable Sectors Aggregation
**File:** `/src/common/views.py`  
**Lines:** 331, 335, 336  
**Function:** `communities_home()`  
**Severity:** HIGH - Will cause FieldError when querying

```python
# LINE 328-339 - BROKEN CODE
vulnerable_sectors = communities.aggregate(
    total_women=Sum("women_count"),
    total_pwd=Sum("pwd_count"),
    total_elderly=Sum("elderly_count"),              # LINE 331 - REMOVED
    total_idps=Sum("idps_count"),
    total_farmers=Sum("farmers_count"),
    total_fisherfolk=Sum("fisherfolk_count"),
    total_teachers_asatidz=Sum("teachers_asatidz_count"),      # LINE 335 - REMOVED
    total_religious_leaders_ulama=Sum("religious_leaders_ulama_count"),  # LINE 336 - REMOVED
    total_csos=Sum("csos_count"),
    total_associations=Sum("associations_count"),
)
```

**Impact:** Dashboard will fail to load with FieldError

**Fix Required:** 
- Remove `elderly_count` aggregation (no direct replacement exists)
- Replace `teachers_asatidz_count` with `asatidz_count`
- Replace `religious_leaders_ulama_count` with `religious_leaders_count`

---

### Issue 3: Municipal Profiles Services - AGGREGATABLE_FIELDS
**File:** `/src/municipal_profiles/services.py`  
**Lines:** 28-54  
**Dictionary:** `AGGREGATABLE_FIELDS`  
**Severity:** CRITICAL - Will cause silent data loss in aggregations

```python
# BROKEN CODE
AGGREGATABLE_FIELDS = {
    ...
    "children_0_12",                      # LINE 33 - REMOVED
    "youth_13_30",                        # LINE 34 - REMOVED
    ...
    "elderly_count",                      # LINE 39 - REMOVED
    ...
    "religious_leaders_ulama_count",      # LINE 45 - REMOVED
    ...
    "teachers_asatidz_count",             # LINE 48 - REMOVED
    ...
}
```

**Impact:** Municipal profile aggregation will attempt to sum non-existent fields, potentially causing:
- Silent failures (if error handling catches KeyError)
- Incorrect aggregation results
- Database query errors

**Fix Required:** Remove all 5 fields from the dictionary and add replacement fields where applicable:
```python
AGGREGATABLE_FIELDS = {
    ...
    "children_0_9",
    "adolescents_10_14",
    "youth_15_30",
    # Remove elderly_count (no replacement)
    ...
    "religious_leaders_count",
    ...
    "asatidz_count",
    ...
}
```

---

## Summary Table

| Field Name | Removed in | Models | Code References | Severity |
|---|---|---|---|---|
| children_0_12 | 0012 | OBCCommunity, MunicipalityCoverage | serializers.py (2x), services.py (1x) | HIGH |
| youth_13_30 | 0012 | OBCCommunity, MunicipalityCoverage | serializers.py (2x), services.py (1x) | HIGH |
| has_madrasah | 0011 | MunicipalityCoverage only | None | LOW |
| has_mosque | 0011 | MunicipalityCoverage only | None | LOW |
| elderly_count | 0014 | OBCCommunity, MunicipalityCoverage | views.py (1x), services.py (1x) | HIGH |
| religious_leaders_ulama_count | 0014 | OBCCommunity, MunicipalityCoverage | views.py (1x), services.py (1x) | HIGH |
| teachers_asatidz_count | 0014 | OBCCommunity, MunicipalityCoverage | views.py (1x), services.py (1x) | HIGH |

---

## Affected Code Locations (Complete List)

### 1. Serializer References
- **File:** `/src/communities/serializers.py`
  - **Lines 118-119:** OBCCommunitySerializer.Meta.fields list
  - **Issue:** Includes `children_0_12` and `youth_13_30`

### 2. View References  
- **File:** `/src/common/views.py`
  - **Lines 331, 335-336:** communities_home() aggregation query
  - **Issue:** Queries non-existent fields:
    - `elderly_count`
    - `teachers_asatidz_count`
    - `religious_leaders_ulama_count`

### 3. Services References
- **File:** `/src/municipal_profiles/services.py`
  - **Lines 33-34, 39, 45, 48:** AGGREGATABLE_FIELDS dictionary
  - **Issue:** References 5 removed fields in set of aggregatable fields

---

## Recommended Actions

### Priority 1: Fix Serializers (Immediate)
Update `/src/communities/serializers.py` line 118-119:
```python
# Replace:
"children_0_12",
"youth_13_30",

# With:
"children_0_9",
"adolescents_10_14",
"youth_15_30",
```

### Priority 2: Fix Views (High)
Update `/src/common/views.py` lines 331, 335-336:
```python
# Remove elderly_count aggregation entirely
# Replace:
total_teachers_asatidz=Sum("teachers_asatidz_count"),
total_religious_leaders_ulama=Sum("religious_leaders_ulama_count"),

# With:
total_asatidz=Sum("asatidz_count"),
total_religious_leaders=Sum("religious_leaders_count"),
```

### Priority 3: Fix Services (Critical)
Update `/src/municipal_profiles/services.py` lines 33-34, 39, 45, 48:
```python
AGGREGATABLE_FIELDS = {
    "estimated_obc_population",
    "total_barangay_population",
    "households",
    "families",
    # REMOVE: "children_0_12",  # REMOVED
    # REMOVE: "youth_13_30",    # REMOVED
    "children_0_9",             # NEW
    "adolescents_10_14",        # NEW
    "youth_15_30",              # NEW
    "adults_31_59",
    "seniors_60_plus",
    "women_count",
    "solo_parents_count",
    # REMOVE: "elderly_count",  # REMOVED (no replacement)
    "pwd_count",
    "farmers_count",
    "fisherfolk_count",
    "indigenous_peoples_count",
    "idps_count",
    # REMOVE: "religious_leaders_ulama_count",  # REMOVED
    "religious_leaders_count",  # REPLACEMENT
    "csos_count",
    "associations_count",
    # REMOVE: "teachers_asatidz_count",  # REMOVED
    "asatidz_count",           # REPLACEMENT
    "number_of_peoples_organizations",
    "number_of_cooperatives",
    "number_of_social_enterprises",
    "number_of_micro_enterprises",
    "number_of_unbanked_obc",
}
```

---

## Testing Strategy

After fixes:

1. **Serializer Tests:** Verify OBCCommunitySerializer can be instantiated
2. **View Tests:** Test `communities_home()` view renders without errors
3. **Service Tests:** Test `compute_aggregate_for_municipality()` executes successfully
4. **API Tests:** Test all endpoints using OBCCommunitySerializer
5. **Integration Tests:** Test full dashboard flow

---

## Notes

- **has_madrasah** and **has_mosque** are only referenced in migration 0011 (data migration), no code references found
- **elderly_count** has NO direct replacement field - requires decision on how to handle this data
- All three problematic views/services are in the **communities** app
- No admin.py references found (good - admin is clean)
- No forms.py references found (good - forms are clean)

---

**Prepared by:** Claude Code Audit System  
**Status:** Report Generated  
**Action Required:** Yes - Critical issues need fixing before deployment
