# OOBC Organization Quick Reference

⚡ **Quick access guide for OOBC organization management**

## Quick Command

```bash
# Ensure OOBC exists with correct data (idempotent)
python manage.py ensure_oobc_organization
```

## OOBC Details

| Field | Value |
|-------|-------|
| **Name** | Office for Other Bangsamoro Communities |
| **Acronym** | OOBC |
| **Type** | bmoa (BARMM Ministry/Agency/Office) |
| **Is Priority** | ✅ True |
| **Is Active** | ✅ True |

## Quick Verification

```bash
# Check if OOBC exists
python manage.py shell -c "from coordination.models import Organization; print('OOBC exists:', Organization.objects.filter(acronym='OOBC').exists())"

# Get OOBC ID
python manage.py shell -c "from coordination.models import Organization; oobc = Organization.objects.filter(acronym='OOBC').first(); print('ID:', oobc.id if oobc else 'Not found')"
```

## Common Operations

### Get OOBC in Python/Django Shell
```python
from coordination.models import Organization

# Method 1: By acronym (recommended)
oobc = Organization.objects.filter(acronym='OOBC').first()

# Method 2: By name
oobc = Organization.objects.filter(name='Office for Other Bangsamoro Communities').first()

# Method 3: Get or create
oobc, created = Organization.objects.get_or_create(
    acronym='OOBC',
    defaults={
        'name': 'Office for Other Bangsamoro Communities',
        'organization_type': 'bmoa',
        'is_active': True,
        'is_priority': True,
    }
)
```

### Use in Views/Code
```python
from coordination.models import Organization

def my_view(request):
    # Get OOBC for filtering/context
    oobc = Organization.objects.filter(acronym='OOBC').first()

    # Use in queries
    partnerships = Partnership.objects.filter(
        organizations=oobc
    )

    return render(request, 'template.html', {
        'oobc': oobc,
        'partnerships': partnerships,
    })
```

## Files Location

| File | Path |
|------|------|
| **Management Command** | `src/coordination/management/commands/ensure_oobc_organization.py` |
| **Full Documentation** | `docs/deployment/OOBC_ORGANIZATION_VERIFICATION.md` |
| **Quick Reference** | `docs/deployment/OOBC_QUICK_REFERENCE.md` ← You are here |
| **Data Source** | `src/data_imports/datasets/barmm_ministries.yaml` |
| **Model Definition** | `src/coordination/models.py` (Organization model) |

## Deployment Steps

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Navigate to src directory:**
   ```bash
   cd src
   ```

3. **Run OOBC setup command:**
   ```bash
   python manage.py ensure_oobc_organization
   ```

4. **Verify success:**
   - Look for: `✓ OOBC organization already has correct data` or `✓ Updated OOBC organization`
   - Confirm `Is Priority: True` in output

## Expected Output

✅ **Success:**
```
✓ OOBC organization already has correct data

================================================================================
OOBC Organization Details:
================================================================================
ID: 7ba7fc8f-32ac-4947-8be6-6eb5fe560957
Name: Office for Other Bangsamoro Communities
Acronym: OOBC
Type: bmoa
...
Is Priority: True
================================================================================
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Command not found | Activate venv: `source venv/bin/activate` |
| Django not installed | Ensure you're in venv and run from `src/` |
| OOBC not found | Run `python manage.py ensure_oobc_organization` |
| is_priority is False | Run `python manage.py ensure_oobc_organization` |

## Related Documentation

- 📖 [Full Verification Report](OOBC_ORGANIZATION_VERIFICATION.md)
- 📖 [BMMS Transition Plan](../plans/bmms/TRANSITION_PLAN.md)
- 📖 [Organization Model](../../src/coordination/models.py)

---

**Last Updated:** October 13, 2025
