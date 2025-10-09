"""
WorkItem Integration Methods for MonitoringEntry

This module contains the 5 integration methods that should be added to the MonitoringEntry model.
These methods will be copied into src/monitoring/models.py after the is_under_obligated property.
"""

from decimal import Decimal
from django.core.exceptions import ValidationError


def create_execution_project(self, structure_template='activity', created_by=None):
    """
    Create root WorkItem project for execution tracking.

    This method creates a hierarchical WorkItem structure for tracking PPA execution.
    It integrates with the WorkItemGenerationService (to be created in Phase 2) to
    generate a structured breakdown of activities/tasks.

    Args:
        structure_template (str): Template structure type. Options:
            - 'activity': Create activities for each outcome/output
            - 'milestone': Create tasks for each milestone
            - 'budget': Create structure based on budget categories
            Default: 'activity'
        created_by (User): User creating the execution project. Defaults to system user.

    Returns:
        WorkItem: The root project WorkItem instance

    Raises:
        ValidationError: If execution project already exists or PPA lacks required data

    Example:
        >>> entry = MonitoringEntry.objects.get(id='some-uuid')
        >>> project = entry.create_execution_project(
        ...     structure_template='activity',
        ...     created_by=request.user
        ... )
        >>> print(f"Created project: {project.title}")
        >>> print(f"Child activities: {project.get_children().count()}")
    """
    from django.contrib.auth import get_user_model
    from common.work_item_model import WorkItem
    from django.contrib.contenttypes.models import ContentType

    # Validation: Check if execution project already exists
    ct = ContentType.objects.get_for_model(self.__class__)
    existing_projects = WorkItem.objects.filter(
        content_type=ct,
        object_id=self.id,
        work_type=WorkItem.WORK_TYPE_PROJECT,
        parent__isnull=True
    )

    if existing_projects.exists():
        raise ValidationError(
            f"Execution project already exists for {self.title}. "
            "Delete the existing project before creating a new one."
        )

    # Validation: Ensure PPA has required data
    if not self.title:
        raise ValidationError("MonitoringEntry must have a title to create execution project.")

    # Get or create system user
    if created_by is None:
        User = get_user_model()
        system_user, _ = User.objects.get_or_create(
            username='system',
            defaults={
                'first_name': 'System',
                'last_name': 'User',
                'is_active': False
            }
        )
        created_by = system_user

    # Create root project WorkItem
    project = WorkItem.objects.create(
        work_type=WorkItem.WORK_TYPE_PROJECT,
        title=f"{self.title} - Execution Plan",
        description=f"Execution tracking for {self.get_category_display()}: {self.title}",
        status=self._map_monitoring_status_to_workitem(),
        priority=self._map_monitoring_priority_to_workitem(),
        start_date=self.start_date,
        due_date=self.target_end_date,
        progress=self.progress,
        created_by=created_by,
        auto_calculate_progress=True,
        is_calendar_visible=True,
        related_ppa=self,
        allocated_budget=self.budget_allocation,
        actual_expenditure=Decimal('0.00'),
        project_data={
            'monitoring_entry_id': str(self.id),
            'structure_template': structure_template,
            'budget_allocation': str(self.budget_allocation) if self.budget_allocation else None,
            'fiscal_year': self.fiscal_year,
        }
    )

    # Link to MonitoringEntry via Generic Foreign Key
    project.content_type = ct
    project.object_id = self.id
    project.save()

    # Populate isolation fields for MOA/OOBC filtering
    project.populate_isolation_fields()
    project.save(update_fields=['ppa_category', 'implementing_moa'])

    # Phase 2: Call WorkItemGenerationService to generate child structure
    # This will be implemented in Phase 2
    # from common.services.workitem_generation import WorkItemGenerationService
    # service = WorkItemGenerationService(project, self)
    # service.generate_structure(template=structure_template)

    return project


def _map_monitoring_status_to_workitem(self):
    """Map MonitoringEntry status to WorkItem status."""
    from common.work_item_model import WorkItem

    status_mapping = {
        'planning': WorkItem.STATUS_NOT_STARTED,
        'ongoing': WorkItem.STATUS_IN_PROGRESS,
        'completed': WorkItem.STATUS_COMPLETED,
        'on_hold': WorkItem.STATUS_BLOCKED,
        'cancelled': WorkItem.STATUS_CANCELLED,
    }
    return status_mapping.get(self.status, WorkItem.STATUS_NOT_STARTED)


def _map_monitoring_priority_to_workitem(self):
    """Map MonitoringEntry priority to WorkItem priority."""
    from common.work_item_model import WorkItem

    priority_mapping = {
        'low': WorkItem.PRIORITY_LOW,
        'medium': WorkItem.PRIORITY_MEDIUM,
        'high': WorkItem.PRIORITY_HIGH,
        'urgent': WorkItem.PRIORITY_URGENT,
    }
    return priority_mapping.get(self.priority, WorkItem.PRIORITY_MEDIUM)


def sync_progress_from_workitem(self):
    """
    Calculate progress from execution_project descendants and update self.progress.

    This method syncs the MonitoringEntry progress with the completion status of
    its associated WorkItem execution project. Progress is calculated based on
    completed descendants (activities/tasks).

    Returns:
        int: Calculated progress percentage (0-100)

    Example:
        >>> entry = MonitoringEntry.objects.get(id='some-uuid')
        >>> calculated_progress = entry.sync_progress_from_workitem()
        >>> print(f"Progress updated: {calculated_progress}%")
        >>> entry.refresh_from_db()
        >>> assert entry.progress == calculated_progress
    """
    from common.work_item_model import WorkItem
    from django.contrib.contenttypes.models import ContentType

    # Find execution project
    try:
        ct = ContentType.objects.get_for_model(self.__class__)
        execution_project = WorkItem.objects.get(
            content_type=ct,
            object_id=self.id,
            work_type=WorkItem.WORK_TYPE_PROJECT,
            parent__isnull=True  # Root project only
        )
    except WorkItem.DoesNotExist:
        # No execution project exists, return current progress
        return self.progress
    except WorkItem.MultipleObjectsReturned:
        # Multiple projects found, use the latest
        ct = ContentType.objects.get_for_model(self.__class__)
        execution_project = WorkItem.objects.filter(
            content_type=ct,
            object_id=self.id,
            work_type=WorkItem.WORK_TYPE_PROJECT,
            parent__isnull=True
        ).latest('created_at')

    # Calculate progress from descendants
    descendants = execution_project.get_descendants()
    if not descendants.exists():
        # No children, use project's own progress
        calculated_progress = execution_project.progress
    else:
        # Calculate based on completed descendants
        total_descendants = descendants.count()
        completed_descendants = descendants.filter(
            status=WorkItem.STATUS_COMPLETED
        ).count()

        if total_descendants > 0:
            calculated_progress = int((completed_descendants / total_descendants) * 100)
        else:
            calculated_progress = 0

    # Update MonitoringEntry progress
    if self.progress != calculated_progress:
        self.progress = calculated_progress
        self.save(update_fields=['progress', 'updated_at'])

    return calculated_progress


def sync_status_from_workitem(self):
    """
    Map WorkItem status to MonitoringEntry status and update self.status.

    This method syncs the MonitoringEntry status with the status of its
    associated WorkItem execution project.

    Returns:
        str: Updated status value

    Example:
        >>> entry = MonitoringEntry.objects.get(id='some-uuid')
        >>> updated_status = entry.sync_status_from_workitem()
        >>> print(f"Status updated: {updated_status}")
        >>> entry.refresh_from_db()
        >>> assert entry.status == updated_status
    """
    from common.work_item_model import WorkItem
    from django.contrib.contenttypes.models import ContentType

    # Find execution project
    try:
        ct = ContentType.objects.get_for_model(self.__class__)
        execution_project = WorkItem.objects.get(
            content_type=ct,
            object_id=self.id,
            work_type=WorkItem.WORK_TYPE_PROJECT,
            parent__isnull=True
        )
    except WorkItem.DoesNotExist:
        # No execution project exists, return current status
        return self.status
    except WorkItem.MultipleObjectsReturned:
        # Multiple projects found, use the latest
        ct = ContentType.objects.get_for_model(self.__class__)
        execution_project = WorkItem.objects.filter(
            content_type=ct,
            object_id=self.id,
            work_type=WorkItem.WORK_TYPE_PROJECT,
            parent__isnull=True
        ).latest('created_at')

    # Map WorkItem status to MonitoringEntry status
    workitem_status = execution_project.status
    status_mapping = {
        WorkItem.STATUS_NOT_STARTED: 'planning',
        WorkItem.STATUS_IN_PROGRESS: 'ongoing',
        WorkItem.STATUS_AT_RISK: 'ongoing',  # Keep as ongoing but flag risk
        WorkItem.STATUS_BLOCKED: 'on_hold',
        WorkItem.STATUS_COMPLETED: 'completed',
        WorkItem.STATUS_CANCELLED: 'cancelled',
    }

    mapped_status = status_mapping.get(workitem_status, self.status)

    # Update MonitoringEntry status
    if self.status != mapped_status:
        self.status = mapped_status
        self.save(update_fields=['status', 'updated_at'])

    return mapped_status


def get_budget_allocation_tree(self):
    """
    Return hierarchical budget breakdown as dict.

    This method returns a nested dictionary representing the budget allocation
    across the WorkItem hierarchy, including allocated budgets and actual
    expenditures per work item with variance calculations.

    Returns:
        dict: Hierarchical budget breakdown with structure:
            {
                'work_item_id': str,
                'title': str,
                'work_type': str,
                'allocated_budget': Decimal,
                'actual_expenditure': Decimal,
                'variance': Decimal,
                'variance_pct': float,
                'children': [...]  # Recursive children
            }

    Example:
        >>> entry = MonitoringEntry.objects.get(id='some-uuid')
        >>> budget_tree = entry.get_budget_allocation_tree()
        >>> print(f"Root budget: ₱{budget_tree['allocated_budget']:,.2f}")
        >>> for child in budget_tree['children']:
        ...     print(f"  {child['title']}: ₱{child['allocated_budget']:,.2f}")
    """
    from common.work_item_model import WorkItem
    from django.contrib.contenttypes.models import ContentType

    # Find execution project
    try:
        ct = ContentType.objects.get_for_model(self.__class__)
        execution_project = WorkItem.objects.get(
            content_type=ct,
            object_id=self.id,
            work_type=WorkItem.WORK_TYPE_PROJECT,
            parent__isnull=True
        )
    except WorkItem.DoesNotExist:
        # No execution project exists, return basic structure
        return {
            'work_item_id': None,
            'title': self.title,
            'work_type': 'monitoring_entry',
            'allocated_budget': self.budget_allocation or Decimal('0.00'),
            'actual_expenditure': self.total_disbursements,
            'variance': (self.total_disbursements - (self.budget_allocation or Decimal('0.00'))),
            'variance_pct': self._calculate_variance_pct(
                self.budget_allocation or Decimal('0.00'),
                self.total_disbursements
            ),
            'children': []
        }
    except WorkItem.MultipleObjectsReturned:
        ct = ContentType.objects.get_for_model(self.__class__)
        execution_project = WorkItem.objects.filter(
            content_type=ct,
            object_id=self.id,
            work_type=WorkItem.WORK_TYPE_PROJECT,
            parent__isnull=True
        ).latest('created_at')

    # Build hierarchical tree recursively
    def build_tree(work_item):
        """Recursively build budget tree for a work item."""
        allocated = work_item.allocated_budget or Decimal('0.00')
        actual = work_item.actual_expenditure or Decimal('0.00')
        variance = actual - allocated
        variance_pct = self._calculate_variance_pct(allocated, actual)

        node = {
            'work_item_id': str(work_item.id),
            'title': work_item.title,
            'work_type': work_item.work_type,
            'work_type_display': work_item.get_work_type_display(),
            'allocated_budget': allocated,
            'actual_expenditure': actual,
            'variance': variance,
            'variance_pct': variance_pct,
            'status': work_item.status,
            'progress': work_item.progress,
            'children': []
        }

        # Recursively add children
        children = work_item.get_children()
        for child in children:
            node['children'].append(build_tree(child))

        return node

    return build_tree(execution_project)


def _calculate_variance_pct(self, allocated, actual):
    """Calculate variance percentage."""
    if allocated == 0:
        return 0.0
    variance = actual - allocated
    return float((variance / allocated) * 100)


def validate_budget_distribution(self):
    """
    Validate sum of child budgets equals PPA budget.

    This method ensures budget consistency across the WorkItem hierarchy by
    validating that the sum of allocated budgets in child work items matches
    the MonitoringEntry's budget_allocation.

    Returns:
        bool: True if budget distribution is valid

    Raises:
        ValidationError: If sum of child budgets doesn't match PPA budget

    Example:
        >>> entry = MonitoringEntry.objects.get(id='some-uuid')
        >>> try:
        ...     entry.validate_budget_distribution()
        ...     print("Budget distribution is valid")
        ... except ValidationError as e:
        ...     print(f"Validation failed: {e.message}")
    """
    from common.work_item_model import WorkItem
    from django.contrib.contenttypes.models import ContentType

    # Find execution project
    try:
        ct = ContentType.objects.get_for_model(self.__class__)
        execution_project = WorkItem.objects.get(
            content_type=ct,
            object_id=self.id,
            work_type=WorkItem.WORK_TYPE_PROJECT,
            parent__isnull=True
        )
    except WorkItem.DoesNotExist:
        # No execution project exists, validation passes
        return True
    except WorkItem.MultipleObjectsReturned:
        ct = ContentType.objects.get_for_model(self.__class__)
        execution_project = WorkItem.objects.filter(
            content_type=ct,
            object_id=self.id,
            work_type=WorkItem.WORK_TYPE_PROJECT,
            parent__isnull=True
        ).latest('created_at')

    # Get PPA budget allocation
    ppa_budget = self.budget_allocation or Decimal('0.00')

    # Calculate sum of child budgets (immediate children only)
    children = execution_project.get_children()
    if not children.exists():
        # No children, validation passes
        return True

    # Sum allocated budgets from children
    child_budget_sum = Decimal('0.00')
    for child in children:
        allocated = child.allocated_budget or Decimal('0.00')
        child_budget_sum += allocated

    # Tolerance for decimal comparison (0.01 = 1 cent)
    tolerance = Decimal('0.01')
    difference = abs(ppa_budget - child_budget_sum)

    if difference > tolerance:
        raise ValidationError(
            f"Budget distribution mismatch: PPA budget is ₱{ppa_budget:,.2f}, "
            f"but sum of child budgets is ₱{child_budget_sum:,.2f}. "
            f"Difference: ₱{difference:,.2f}. "
            f"Please adjust child budget allocations to match the total PPA budget."
        )

    return True
