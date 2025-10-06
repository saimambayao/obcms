# OBC Population Data Correction ✅

**Date:** October 6, 2025
**Status:** Successfully Corrected
**Records Affected:** 6,589 OBC Communities

---

## Critical Issue Identified

The initial OBC data generation incorrectly assumed that:
```
estimated_obc_population = total_barangay_population
```

This is **fundamentally incorrect** because:

### The Critical Distinction

**Total Barangay Population** = ALL people living in the barangay (regardless of ethnicity/identity)

**Estimated OBC Population** = ONLY those identified as belonging to Other Bangsamoro Communities (a SUBSET)

---

## Problem Statement

### What Was Wrong

The management command `generate_obc_communities.py` originally set:
- `estimated_obc_population` = barangay.population_total ❌
- `population` (legacy field) = barangay.population_total ❌

This created **misleading data** because:
1. It implied that 100% of barangay residents are OBC members
2. Municipal aggregates showed inflated OBC population numbers
3. The system couldn't distinguish between total population and actual OBC population

### Impact on Municipal Data

At http://localhost:8000/communities/managemunicipal/, the municipal coverage records showed:
- Incorrect aggregated OBC populations (inflated)
- Could not distinguish OBC-specific needs from general barangay needs
- Policy recommendations would target wrong population sizes

---

## Solution Implemented

### 1. Fixed Management Command

**File:** `src/communities/management/commands/generate_obc_communities.py`

**Changes:**
```python
# BEFORE (INCORRECT)
"estimated_obc_population": barangay.population_total,  # WRONG!
"population": barangay.population_total,

# AFTER (CORRECT)
"estimated_obc_population": None,  # Must be researched separately
"population": None,  # OBC-specific (to be researched)
"total_barangay_population": barangay.population_total,  # Context data
```

### 2. Created Correction Command

**File:** `src/communities/management/commands/fix_obc_population_data.py`

This command:
- Identifies all OBC communities where `estimated_obc_population` equals `total_barangay_population`
- Sets `estimated_obc_population` to NULL (requires research)
- Sets `population` (legacy) to NULL
- Preserves `total_barangay_population` as context data
- Optionally refreshes municipal coverage aggregates

**Usage:**
```bash
# Preview changes
python manage.py fix_obc_population_data --dry-run

# Fix barangay OBC data
python manage.py fix_obc_population_data

# Fix barangay data AND refresh municipal aggregates
python manage.py fix_obc_population_data --also-fix-municipal
```

---

## Correction Results

### Barangay OBC Communities

**Before Correction:**
```
Total OBC Communities: 6,612
With estimated_obc_population: 6,589 (INCORRECT - all equal to total)
```

**After Correction:**
```
Total OBC Communities: 6,612
With estimated_obc_population: 20 (pre-existing data only)
WITHOUT estimated_obc_population: 6,592 (correctly set to NULL)
With total_barangay_population: 6,594 (context data preserved)
```

### Municipal Coverage

**Before Correction:**
```
Municipal estimated_obc_population: Inflated (incorrect aggregates)
```

**After Correction:**
```
Municipal estimated_obc_population: NULL (correctly reflects lack of data)
Total barangay population: 20,126,266 (context data preserved)
Auto-sync: Correctly aggregates from NULL barangay values
```

---

## Data Model Explanation

### Field Definitions

```python
OBCCommunity (Barangay-level):
  estimated_obc_population: NULL     # Requires field research/MANA
  total_barangay_population: 54,096  # Full barangay population (context)
  population: NULL                   # Legacy field (OBC-specific)

MunicipalityCoverage (Municipal-level):
  estimated_obc_population: NULL     # Aggregated from barangays (NULL)
  total_barangay_population: SUM     # Aggregated total populations
```

### Auto-Sync Behavior

When `auto_sync=True` on municipal coverage:
- Aggregates numeric fields from barangay OBC communities
- `estimated_obc_population` aggregates to NULL (if all barangays are NULL)
- `total_barangay_population` sums correctly
- Prevents misleading inflated OBC population counts

---

## Why This Matters

### Correct Policy Planning

**WRONG Approach (Before):**
```
Municipality X has 100,000 "OBC population"
→ Plan programs for 100,000 people
→ Over-allocated resources
→ Incorrect targeting
```

**CORRECT Approach (After):**
```
Municipality X has:
  - Total population: 100,000 (context)
  - OBC population: NULL (requires assessment)
→ Conduct MANA assessment first
→ Identify actual 15,000 OBC individuals
→ Plan programs accurately for 15,000
→ Correct resource allocation
```

### Research Requirements

To populate `estimated_obc_population`, OOBC must:

1. **Field Surveys**
   - Community mapping exercises
   - Ethnolinguistic identity verification
   - Household-level enumeration

2. **MANA Assessments**
   - Mapping and Needs Assessment
   - Community consultations
   - Stakeholder interviews

3. **LGU Coordination**
   - Verify barangay records
   - Cross-reference with barangay officials
   - Document OBC settlement patterns

4. **Data Entry**
   - Update `estimated_obc_population` with researched values
   - Document source and methodology
   - Municipal aggregates auto-sync

---

## Verification Examples

### Sample Corrected Data

**Barangay OBC (Region XII):**
```
Barangay: Apopong, General Santos City
OBC ID: XII-SC-GS-5982
estimated_obc_population: NULL (requires MANA assessment)
total_barangay_population: 54,096 (from PSA data)
Coordinates: (6.1066, 125.1717)
Status: Active, awaiting assessment
```

**Municipal Coverage (Corrected):**
```
Municipality: General Santos City
estimated_obc_population: NULL (no barangay data yet)
total_barangay_population: 722,059 (aggregated from barangays)
Total OBC Communities: X barangays mapped
Auto-sync: TRUE
```

---

## Next Steps for OOBC

### 1. Prioritize Assessment Areas

Identify high-priority municipalities based on:
- Historical OBC presence
- Proximity to BARMM
- Ethnolinguistic community clusters
- Coordination requests

### 2. Conduct MANA Assessments

For each priority barangay:
- [ ] Community mapping
- [ ] Household enumeration
- [ ] OBC population estimation
- [ ] Data validation with LGU

### 3. Update Database

After field assessment:
```python
# Update OBC community with researched data
obc.estimated_obc_population = 3500  # From assessment
obc.source_document_reference = "MANA Assessment 2025-Q1, Conducted Oct 2025"
obc.needs_assessment_date = datetime.date(2025, 10, 15)
obc.save()

# Municipal coverage auto-syncs
municipality_coverage.refresh_from_communities()
```

### 4. Quality Assurance

Ensure data quality:
- `estimated_obc_population` ≤ `total_barangay_population` (always)
- Document data sources
- Track assessment dates
- Periodic re-assessment (every 3-5 years)

---

## Files Modified

### Commands Created
1. `src/communities/management/commands/generate_obc_communities.py` - Fixed
2. `src/communities/management/commands/fix_obc_population_data.py` - New

### Documentation
1. `OBC_DATA_GENERATION_COMPLETE.md` - Updated
2. `OBC_POPULATION_CORRECTION.md` - This file

---

## Technical Notes

### Database Query Examples

**Check data quality:**
```python
# Find communities where OBC pop > Total pop (ERROR)
bad_data = OBCCommunity.objects.filter(
    estimated_obc_population__gt=F('total_barangay_population')
)

# Should return 0 after correction
assert bad_data.count() == 0
```

**Track research progress:**
```python
# Communities with researched OBC data
researched = OBCCommunity.objects.filter(
    estimated_obc_population__isnull=False
).count()

# Communities pending research
pending = OBCCommunity.objects.filter(
    estimated_obc_population__isnull=True
).count()

print(f"Researched: {researched}")
print(f"Pending: {pending}")
print(f"Progress: {researched / (researched + pending) * 100:.1f}%")
```

---

## Success Criteria ✅

- [x] Fixed `generate_obc_communities.py` to NOT set estimated_obc_population
- [x] Created `fix_obc_population_data.py` correction command
- [x] Corrected 6,589 existing OBC community records
- [x] Refreshed municipal coverage aggregates
- [x] Documented the critical distinction
- [x] Provided clear guidance for future data collection

---

## Conclusion

The OBC population data has been **correctly** set to NULL, acknowledging that:

1. **OBC population is NOT the same as total barangay population**
2. **Actual OBC populations require field research**
3. **Total barangay population is preserved as context data**
4. **Municipal aggregates reflect the correct NULL state**
5. **Future MANA assessments will populate the actual values**

The system now accurately represents the data collection reality: we have geographic and demographic context, but specific OBC population figures require dedicated field work.

---

**Corrected:** October 6, 2025
**Command:** `python manage.py fix_obc_population_data --also-fix-municipal`
**Documentation:** This file + OBC_DATA_GENERATION_COMPLETE.md (updated)
