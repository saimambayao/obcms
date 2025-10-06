"""
Legacy Models Archive - Project Management Portal

====================================================================================
DEPRECATED: ProjectWorkflow
====================================================================================

This model is DEPRECATED and maintained for backward compatibility only.
All new development should use the WorkItem model (common.work_item_model.WorkItem).

Migration Status:
- WorkItem model: ACTIVE (supports project workflows via item_type='project')
- Data migration: COMPLETE (workflows migrated to WorkItem)
- Templates: UPDATED (all use WorkItem URLs)
- Calendar: INTEGRATED (WorkItem events display correctly)

Legacy Model Location:
- ProjectWorkflow: src/project_central/models.py (line 17+)

DO NOT:
- Import this model in new code
- Create new ProjectWorkflow instances (use WorkItem with item_type='project')
- Add new features to ProjectWorkflow
- Reference ProjectWorkflow in new views/templates

Phase 4 Deprecation Plan:
docs/refactor/LEGACY_CODE_DEPRECATION_PLAN.md

For questions, see:
- docs/refactor/UNIFIED_WORK_HIERARCHY_EVALUATION.md
- docs/refactor/WORKITEM_MIGRATION_COMPLETE.md
"""

__all__ = []  # Explicitly empty - do not export anything
