# Query Template Categories

This directory contains auto-generated documentation for query templates organized by category.

## Current Categories (151 Templates)

- **[communities](communities.md)** - 25 templates for OBC community queries
- **[coordination](coordination.md)** - 30 templates for stakeholder coordination
- **[mana](mana.md)** - 21 templates for MANA workshop and assessment queries
- **[policies](policies.md)** - 25 templates for policy recommendation tracking
- **[projects](projects.md)** - 25 templates for Project Central (PPA) queries
- **[staff](staff.md)** - 10 templates for staff and task management
- **[general](general.md)** - 15 templates for system help and FAQs

## Planned Categories (424 New Templates)

### Core Domain Enhancements
- **communities_enhanced** - 40 new templates (25 → 65 total)
- **coordination_enhanced** - 45 new templates (30 → 75 total)
- **mana_enhanced** - 39 new templates (21 → 60 total)
- **policies_enhanced** - 35 new templates (25 → 60 total)
- **projects_enhanced** - 35 new templates (25 → 60 total)
- **staff_enhanced** - 10 new templates (10 → 35 total)
- **general_enhanced** - 5 new templates (15 → 30 total)

### New Domains (8 Categories)
- **geographic** - 40 templates for location-focused queries
- **temporal** - 30 templates for time-based queries
- **cross_domain** - 30 templates for multi-module queries
- **analytics** - 25 templates for advanced analytics
- **reports** - 20 templates for report generation
- **validation** - 15 templates for data quality checks
- **audit** - 15 templates for change tracking
- **admin** - 15 templates for system administration

## Documentation Generation

Documentation is auto-generated using:

```bash
# Generate docs for all categories
python manage.py generate_template_docs --all

# Generate docs for specific category
python manage.py generate_template_docs --category communities
```

## Template Count by Query Type

### Current Distribution (151 templates)

```
COUNT:      45 templates (30%)
LIST:       40 templates (26%)
GET:        20 templates (13%)
FIND:       25 templates (17%)
AGGREGATE:  15 templates (10%)
Other:       6 templates (4%)
```

### Target Distribution (575 templates)

```
COUNT:      150 templates (26%)
LIST:       140 templates (24%)
GET:         70 templates (12%)
FIND:        80 templates (14%)
COMPARE:     30 templates (5%)
TREND:       25 templates (4%)
AGGREGATE:   40 templates (7%)
RANK:        15 templates (3%)
VALIDATE:    15 templates (3%)
EXPORT:      10 templates (2%)
```

---

**Note**: Documentation files in this directory are auto-generated. Do not edit manually. Run `generate_template_docs` command to update.
