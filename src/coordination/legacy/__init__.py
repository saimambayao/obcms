"""
Legacy Models Archive - Coordination

====================================================================================
DEPRECATED: Event
====================================================================================

This model is DEPRECATED and maintained for backward compatibility only.
All new development should use the WorkItem model (common.work_item_model.WorkItem).

Migration Status:
- WorkItem model: ACTIVE (supports events via item_type='activity')
- Data migration: COMPLETE (events migrated to WorkItem)
- Templates: UPDATED (all use WorkItem URLs)
- Calendar: INTEGRATED (WorkItem events display correctly)

Legacy Model Location:
- Event: src/coordination/models.py (line 1583+)
- EventParticipant: src/coordination/models.py (line 2374+)
- EventDocument: src/coordination/models.py (line 2855+)
- EventAttendance: src/coordination/models.py (line 3614+)

DO NOT:
- Import these models in new code
- Create new Event instances (use WorkItem with item_type='activity')
- Add new features to Event
- Reference Event in new views/templates

Phase 4 Deprecation Plan:
docs/refactor/LEGACY_CODE_DEPRECATION_PLAN.md

For questions, see:
- docs/refactor/UNIFIED_WORK_HIERARCHY_EVALUATION.md
- docs/refactor/WORKITEM_MIGRATION_COMPLETE.md
"""

__all__ = []  # Explicitly empty - do not export anything
