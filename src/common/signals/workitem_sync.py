"""
WorkItem Sync Signals

Note: Legacy dual-write signals have been removed.
StaffTask, Event, and ProjectWorkflow models have been completely removed
from the codebase. All work management is now done through WorkItem.

The migration to WorkItem is complete - see: docs/refactor/WORKITEM_MIGRATION_COMPLETE.md

WorkItem signals for create/update/delete are handled in common/models/work_item_model.py
"""

import logging

logger = logging.getLogger(__name__)

# All legacy sync signals removed - WorkItem is now the only model
