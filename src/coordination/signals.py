"""Signal handlers for coordination app.

Note: Legacy Event and ProjectWorkflow signals have been removed.
These models have been migrated to WorkItem.

For WorkItem signals, see: common/signals/workitem_sync.py
"""
import logging

logger = logging.getLogger(__name__)

# All legacy signals removed - WorkItem handles events via its own signal system
