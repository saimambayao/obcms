# Population Reconciliation Guide

## Overview

The OBCMS system now supports **unattributed population tracking** - showing OBC population estimates that haven't been mapped to specific lower-level administrative units yet.

## How It Works

### 🔄 Two Modes of Operation

#### 1. **AUTO-SYNC MODE** (Default) ✅
- **Municipal OBC** population = SUM of all Barangay OBCs
- **Provincial OBC** population = SUM of all Municipal OBCs
- **No unattributed population** possible
- **100% attribution** guaranteed
- Use when: All OBCs have been mapped to specific locations

#### 2. **MANUAL OVERRIDE MODE** ⚠️
- Staff can enter **higher population estimates**
- System shows the **difference** as unattributed
- Use when: You have population estimates but incomplete mapping

---

## Scenarios

### Scenario 1: Complete Mapping (Auto-Sync)

```
Municipality: Zamboanga del Sur
Auto-sync: ✅ Enabled

Population Breakdown:
  Total Municipal:         50,000
  Attributed to Barangays: 50,000
  Unattributed (orphaned):      0
  Attribution Rate:          100%
```

✅ **Result**: Perfect data - all population mapped to barangays

---

### Scenario 2: Incomplete Mapping (Manual Override)

```
Municipality: Sample Municipality
Auto-sync: ❌ Disabled (Manual Entry)

Steps taken:
1. Staff knows ~10,000 OBCs exist in the municipality
2. Only 4,000 have been mapped to specific barangays
3. Set estimated_obc_population = 10,000
4. Set auto_sync = False

Population Breakdown:
  Total Municipal:         10,000
  Attributed to Barangays:  4,000
  Unattributed (orphaned):  6,000 ⚠️
  Attribution Rate:            40%
```

⚠️ **Result**: **6,000 population** with **NO corresponding barangay OBC**

This represents: **"Estimated OBC Population not yet mapped to specific barangays"**

---

## Provincial Level

Same logic applies at provincial level:

```
Province: Sample Province
Auto-sync: ❌ Disabled

Population Breakdown:
  Total Provincial:                15,000
  Attributed to Municipalities:    10,000
  Unattributed (orphaned):          5,000 ⚠️
  Attribution Rate:                   66.7%
```

The **5,000 unattributed** represents: **"Estimated OBC Population not yet mapped to specific municipalities"**

---

## Available Properties

### For Municipal OBC (`MunicipalityCoverage`)

```python
# Calculate attributed population
municipal_obc.barangay_attributed_population
# Returns: Sum of all Barangay OBCs

# Calculate unattributed (orphaned) population
municipal_obc.unattributed_population
# Returns: 0 if auto_sync=True
# Returns: municipal_total - barangay_total if auto_sync=False

# Get full reconciliation breakdown
municipal_obc.population_reconciliation
# Returns:
{
    "total_municipal": 10000,
    "attributed_to_barangays": 4000,
    "unattributed": 6000,
    "attribution_rate": 40.0,
    "auto_sync_enabled": False
}
```

### For Provincial OBC (`ProvinceCoverage`)

```python
# Calculate attributed population
provincial_obc.municipal_attributed_population
# Returns: Sum of all Municipal OBCs

# Calculate unattributed (orphaned) population
provincial_obc.unattributed_population
# Returns: 0 if auto_sync=True
# Returns: provincial_total - municipal_total if auto_sync=False

# Get full reconciliation breakdown
provincial_obc.population_reconciliation
# Returns:
{
    "total_provincial": 15000,
    "attributed_to_municipalities": 10000,
    "unattributed": 5000,
    "attribution_rate": 66.7,
    "auto_sync_enabled": False
}
```

---

## Template Usage

### Display Warning for Data Gaps

```django
{% if municipal_obc.unattributed_population > 0 %}
    <div class="alert alert-warning">
        <i class="fas fa-exclamation-triangle"></i>
        <strong>Data Gap Identified:</strong>

        <p>
            {{ municipal_obc.unattributed_population|intcomma }} OBC population
            estimated but not yet mapped to specific barangays.
        </p>

        <p class="mb-0">
            <strong>Attribution Rate:</strong>
            {{ municipal_obc.population_reconciliation.attribution_rate }}%
        </p>

        <small class="text-muted">
            Complete barangay-level mapping to improve data accuracy.
        </small>
    </div>
{% endif %}
```

### Display Reconciliation Breakdown

```django
<div class="card">
    <div class="card-header">Population Reconciliation</div>
    <div class="card-body">
        {% with recon=municipal_obc.population_reconciliation %}
            <table class="table">
                <tr>
                    <td>Total Municipal Estimate:</td>
                    <td class="text-end">{{ recon.total_municipal|intcomma }}</td>
                </tr>
                <tr>
                    <td>Attributed to Barangays:</td>
                    <td class="text-end text-success">
                        {{ recon.attributed_to_barangays|intcomma }}
                    </td>
                </tr>
                <tr>
                    <td>Unattributed (Orphaned):</td>
                    <td class="text-end {% if recon.unattributed > 0 %}text-warning{% endif %}">
                        {{ recon.unattributed|intcomma }}
                    </td>
                </tr>
                <tr class="table-primary">
                    <td><strong>Attribution Rate:</strong></td>
                    <td class="text-end">
                        <strong>{{ recon.attribution_rate }}%</strong>
                    </td>
                </tr>
            </table>
        {% endwith %}
    </div>
</div>
```

---

## Use Cases

### 1. Initial Data Entry
- Staff conducts survey and estimates 50,000 OBCs in a province
- Haven't mapped to municipalities yet
- Create Provincial OBC with `auto_sync=False`, population=50,000
- Shows 50,000 unattributed until municipalities are added

### 2. Gradual Mapping
- Start with provincial estimate: 50,000
- Map 10 municipalities totaling 30,000
- System shows: 20,000 still unattributed
- Continue mapping until 100% attribution

### 3. Quality Assurance
- Use `attribution_rate` to track data completeness
- Target: 100% attribution before finalizing reports
- Identify municipalities with data gaps

### 4. Reporting
- Show stakeholders the data coverage
- Transparent about what's mapped vs. estimated
- Track progress over time

---

## Best Practices

### ✅ DO:
1. Use **auto-sync=True** (default) when all data is mapped
2. Use **auto-sync=False** only for initial estimates
3. Monitor `attribution_rate` - aim for 100%
4. Display unattributed warnings to staff
5. Gradually map unattributed population to specific locations

### ❌ DON'T:
1. Leave large unattributed populations indefinitely
2. Mix auto-sync and manual entries without understanding the impact
3. Ignore attribution warnings
4. Disable auto-sync without a good reason

---

## Migration Strategy

If you have existing data with unattributed population:

1. **Identify gaps**: Check `.unattributed_population` across all records
2. **Plan mapping**: Prioritize municipalities/provinces with low attribution rates
3. **Conduct assessments**: Map OBCs to specific barangays/municipalities
4. **Enable auto-sync**: Once mapped, set `auto_sync=True`
5. **Verify**: Ensure `attribution_rate = 100%`

---

## Summary

| Level | Attributed From | Unattributed Meaning | Property |
|-------|----------------|---------------------|----------|
| **Municipal** | Barangay OBCs | Population not mapped to barangays | `.unattributed_population` |
| **Provincial** | Municipal OBCs | Population not mapped to municipalities | `.unattributed_population` |

**Key Insight**: The system **explicitly tracks data gaps**, making it transparent what's been mapped vs. what's still estimated.
