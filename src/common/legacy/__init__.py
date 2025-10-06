"""
Legacy Models Archive

====================================================================================
DEPRECATED: StaffTask, TaskTemplate, TaskTemplateItem
====================================================================================

These models are DEPRECATED and maintained for backward compatibility only.
All new development should use the WorkItem model (common.work_item_model.WorkItem).

Migration Status:
- WorkItem model: ACTIVE (src/common/work_item_model.py)
- Data migration: COMPLETE (36 WorkItems migrated)
- Templates: UPDATED (all use WorkItem URLs)
- Calendar: INTEGRATED (WorkItem events display correctly)
- Feature flags: USE_WORKITEM_MODEL=1, USE_UNIFIED_CALENDAR=1

Legacy Model Locations:
- StaffTask: src/common/models.py (lines 628-1446)
- TaskTemplate: src/common/models.py (lines 1448-1469)
- TaskTemplateItem: src/common/models.py (lines 1472-1530)

DO NOT:
- Import these models in new code
- Create new StaffTask instances (use WorkItem instead)
- Add new features to StaffTask
- Reference StaffTask in new views/templates

Phase 4 Deprecation Plan:
docs/refactor/LEGACY_CODE_DEPRECATION_PLAN.md

For questions, see:
- docs/refactor/UNIFIED_WORK_HIERARCHY_EVALUATION.md
- docs/refactor/WORKITEM_MIGRATION_COMPLETE.md
"""

# DO NOT add model imports here - this is documentation only
# Legacy models remain in their original locations for backward compatibility

__all__ = []  # Explicitly empty - do not export anything
