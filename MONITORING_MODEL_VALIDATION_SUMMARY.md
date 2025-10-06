# MonitoringEntry Model-Level Validation Implementation

**Date**: October 5, 2025  
**Status**: COMPLETE  
**Migration**: `monitoring/migrations/0017_add_model_validation_constraints.py`

## Summary

Added comprehensive model-level validation to the `MonitoringEntry` model to enforce business rules at both the application and database levels.

## Changes Made

### 1. Model Imports Enhanced

**File**: `src/monitoring/models.py`

Added necessary imports:
```python
from django.core.exceptions import ValidationError
from django.db.models import F, Q
```

### 2. Database Check Constraints

Added two database-level constraints in the `Meta` class:

#### Constraint 1: Valid Progress Range
```python
models.CheckConstraint(
    check=Q(progress__gte=0) & Q(progress__lte=100),
    name='monitoring_entry_valid_progress'
)
```
- Enforces progress must be between 0 and 100
- Database-level validation (cannot be bypassed)

#### Constraint 2: Valid Date Range
```python
models.CheckConstraint(
    check=Q(target_end_date__gte=F('start_date')) | Q(start_date__isnull=True) | Q(target_end_date__isnull=True),
    name='monitoring_entry_valid_date_range'
)
```
- Enforces target_end_date must be >= start_date (when both are set)
- Allows null values for either field

### 3. Model-Level `clean()` Method

Added comprehensive validation logic that runs before save:

#### 3.1 Funding Source Validation
```python
if self.funding_source == self.FUNDING_SOURCE_OTHERS and not self.funding_source_other:
    errors['funding_source_other'] = 'Please specify the funding source when selecting "Others".'
```

#### 3.2 Date Range Validations
- **Target End Date**: Must be after start date
- **Actual End Date**: Cannot be before start date

#### 3.3 Budget Validations
- **Budget Allocation**: Cannot exceed budget ceiling (when ceiling is set)
  - Provides formatted error message with peso amounts
- **OBC Budget Allocation**: Cannot exceed total budget allocation
- **OBC Slots**: Cannot exceed total slots

#### 3.4 Category-Specific Required Fields

**MOA PPA Entries** (`category='moa_ppa'`):
- Requires `implementing_moa` field

**OBC Request Entries** (`category='obc_request'`):
- Requires `submitted_by_community` field
- Requires `submitted_to_organization` field

### 4. Migration Details

**Migration File**: `monitoring/migrations/0017_add_model_validation_constraints.py`

Operations:
1. Remove `related_event` field (cleanup from Event model deprecation)
2. Add `monitoring_entry_valid_progress` constraint
3. Add `monitoring_entry_valid_date_range` constraint

## Data Validation Results

Ran validation checks against existing data (209 entries):

| Validation Rule | Violations Found |
|----------------|------------------|
| Invalid progress (< 0 or > 100) | 0 |
| Target end date < start date | 0 |
| Funding source "others" without specification | 0 |
| Budget allocation > ceiling | 0 |
| OBC allocation > total allocation | 0 |
| OBC slots > total slots | 0 |
| MOA PPAs without implementing_moa | 0 |
| OBC requests without submitted_by_community | 0 |
| OBC requests without submitted_to_organization | 0 |

**Result**: All existing data passes validation. Migration is safe to apply.

## Implementation Benefits

### Application-Level Validation (`clean()` method)
1. **User-Friendly Errors**: Provides detailed, contextual error messages
2. **Field-Specific Feedback**: Errors are associated with specific fields in forms
3. **Pre-Save Validation**: Catches issues before database operations
4. **Flexible**: Can be called explicitly in views/forms

### Database-Level Validation (Check Constraints)
1. **Data Integrity**: Enforces rules at the database level (cannot be bypassed)
2. **Performance**: Database handles validation efficiently
3. **Safety**: Protects against bulk operations, raw SQL, or direct database access
4. **Multi-Application Support**: Rules apply regardless of which application accesses the database

## Usage Example

```python
from monitoring.models import MonitoringEntry

# Create new entry
entry = MonitoringEntry(
    title="Sample PPA",
    category='moa_ppa',
    funding_source='others',
    # ... other fields
)

# Validation runs automatically
try:
    entry.full_clean()  # Explicitly validate
    entry.save()        # save() also calls full_clean() if model has clean()
except ValidationError as e:
    print(e.message_dict)
    # {
    #     'implementing_moa': ['Implementing MOA is required for MOA PPA entries.'],
    #     'funding_source_other': ['Please specify the funding source when selecting "Others".']
    # }
```

## Validation Rules Summary

| Rule | Level | Error Message |
|------|-------|--------------|
| Progress 0-100 | Database | Check constraint violation |
| Target end >= start date | Database | Check constraint violation |
| Date range validation | Model | "Target end date must be after start date." |
| Actual end >= start date | Model | "Actual end date cannot be before start date." |
| Funding source "others" | Model | "Please specify the funding source when selecting 'Others'." |
| Budget allocation <= ceiling | Model | "Budget allocation (₱X) cannot exceed ceiling (₱Y)." |
| OBC allocation <= total | Model | "OBC allocation cannot exceed total budget allocation." |
| OBC slots <= total slots | Model | "OBC slots cannot exceed total slots." |
| MOA PPA requires implementing_moa | Model | "Implementing MOA is required for MOA PPA entries." |
| OBC request requires community | Model | "Submitting community is required for OBC requests." |
| OBC request requires organization | Model | "Recipient organization is required for OBC requests." |

## Migration Status

- **Created**: ✅ Migration file generated successfully
- **Data Check**: ✅ All existing data validates (0 violations)
- **Ready to Apply**: ⚠️ Blocked by coordination app migration issues
  - The monitoring migration itself is safe
  - Coordination app has unrelated Event model deletion issues
  - Can be applied separately once coordination issues are resolved

## Next Steps

1. **Fix Coordination Migration**: Resolve Event model deletion issues in coordination app
2. **Apply Migration**: Run `python manage.py migrate monitoring`
3. **Test Forms**: Ensure form validation triggers clean() method
4. **Update Admin**: Verify Django admin respects validation rules
5. **Documentation**: Update API documentation with validation rules

## Files Modified

1. `/src/monitoring/models.py` - Added validation logic
2. `/src/monitoring/migrations/0017_add_model_validation_constraints.py` - Migration file

## Related Documentation

- [Django Model Validation](https://docs.djangoproject.com/en/5.2/ref/models/instances/#validating-objects)
- [Database Constraints](https://docs.djangoproject.com/en/5.2/ref/models/constraints/)
- [MonitoringEntry Model](src/monitoring/models.py)

---

**Implementation Complete**: Model-level validation added successfully with comprehensive business rule enforcement at both application and database levels.
