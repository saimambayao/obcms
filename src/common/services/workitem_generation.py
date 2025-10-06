"""
WorkItem Generation Service for auto-generating WorkItem hierarchies from PPA templates.

This service creates structured work breakdown structures (WBS) from MonitoringEntry (PPA)
instances using predefined templates.

Usage:
    from common.services.workitem_generation import WorkItemGenerationService

    # Generate from template
    service = WorkItemGenerationService()
    root_project = service.generate_from_ppa(ppa, template='program', created_by=user)

    # Generate from outcome framework
    root_project = service.generate_from_outcome_framework(ppa, created_by=user)

Templates:
    - PROGRAM_TEMPLATE: Planning (20%), Implementation (60%), M&E (20%)
    - ACTIVITY_TEMPLATE: Preparation (15%), Execution (75%), Completion (10%)
    - MILESTONE_TEMPLATE: Based on PPA milestone_dates JSON field
    - MINIMAL_TEMPLATE: Single task "Main Deliverable" (100%)
"""

import logging
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from typing import Optional, Dict, List, Any

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)
User = get_user_model()


class WorkItemGenerationService:
    """
    Service for auto-generating WorkItem hierarchies from PPA templates.

    Creates structured work breakdown structures (WBS) with budget distribution
    and schedule allocation based on predefined templates.
    """

    # ========== TEMPLATE DEFINITIONS ==========

    PROGRAM_TEMPLATE = {
        "name": "program",
        "description": "Full program structure with planning, implementation, and M&E phases",
        "structure": [
            {
                "title": "Planning & Design",
                "work_type": "sub_project",
                "budget_percentage": Decimal("20.00"),
                "duration_percentage": Decimal("20.00"),
                "priority": "high",
                "children": [
                    {
                        "title": "Needs Assessment & Feasibility Study",
                        "work_type": "activity",
                        "budget_percentage": Decimal("50.00"),  # Of parent
                    },
                    {
                        "title": "Stakeholder Consultation",
                        "work_type": "activity",
                        "budget_percentage": Decimal("30.00"),
                    },
                    {
                        "title": "Program Design & Approval",
                        "work_type": "activity",
                        "budget_percentage": Decimal("20.00"),
                    },
                ],
            },
            {
                "title": "Implementation",
                "work_type": "sub_project",
                "budget_percentage": Decimal("60.00"),
                "duration_percentage": Decimal("65.00"),
                "priority": "critical",
                "children": [
                    {
                        "title": "Phase 1: Launch & Mobilization",
                        "work_type": "activity",
                        "budget_percentage": Decimal("30.00"),
                    },
                    {
                        "title": "Phase 2: Service Delivery",
                        "work_type": "activity",
                        "budget_percentage": Decimal("50.00"),
                    },
                    {
                        "title": "Phase 3: Consolidation",
                        "work_type": "activity",
                        "budget_percentage": Decimal("20.00"),
                    },
                ],
            },
            {
                "title": "Monitoring & Evaluation",
                "work_type": "sub_project",
                "budget_percentage": Decimal("20.00"),
                "duration_percentage": Decimal("15.00"),
                "priority": "medium",
                "children": [
                    {
                        "title": "Data Collection & Analysis",
                        "work_type": "activity",
                        "budget_percentage": Decimal("40.00"),
                    },
                    {
                        "title": "Impact Assessment",
                        "work_type": "activity",
                        "budget_percentage": Decimal("40.00"),
                    },
                    {
                        "title": "Final Report & Documentation",
                        "work_type": "activity",
                        "budget_percentage": Decimal("20.00"),
                    },
                ],
            },
        ],
    }

    ACTIVITY_TEMPLATE = {
        "name": "activity",
        "description": "Standard activity structure with preparation, execution, completion",
        "structure": [
            {
                "title": "Preparation",
                "work_type": "activity",
                "budget_percentage": Decimal("15.00"),
                "duration_percentage": Decimal("20.00"),
                "priority": "high",
                "children": [
                    {
                        "title": "Planning & Coordination",
                        "work_type": "task",
                        "budget_percentage": Decimal("50.00"),
                    },
                    {
                        "title": "Resource Mobilization",
                        "work_type": "task",
                        "budget_percentage": Decimal("50.00"),
                    },
                ],
            },
            {
                "title": "Execution",
                "work_type": "activity",
                "budget_percentage": Decimal("75.00"),
                "duration_percentage": Decimal("70.00"),
                "priority": "critical",
                "children": [
                    {
                        "title": "Core Activities",
                        "work_type": "task",
                        "budget_percentage": Decimal("80.00"),
                    },
                    {
                        "title": "Support & Logistics",
                        "work_type": "task",
                        "budget_percentage": Decimal("20.00"),
                    },
                ],
            },
            {
                "title": "Completion",
                "work_type": "activity",
                "budget_percentage": Decimal("10.00"),
                "duration_percentage": Decimal("10.00"),
                "priority": "medium",
                "children": [
                    {
                        "title": "Documentation & Reporting",
                        "work_type": "task",
                        "budget_percentage": Decimal("60.00"),
                    },
                    {
                        "title": "Lessons Learned",
                        "work_type": "task",
                        "budget_percentage": Decimal("40.00"),
                    },
                ],
            },
        ],
    }

    MINIMAL_TEMPLATE = {
        "name": "minimal",
        "description": "Simplest structure for small PPAs",
        "structure": [
            {
                "title": "Main Deliverable",
                "work_type": "task",
                "budget_percentage": Decimal("100.00"),
                "duration_percentage": Decimal("100.00"),
                "priority": "high",
            }
        ],
    }

    TEMPLATES = {
        "program": PROGRAM_TEMPLATE,
        "activity": ACTIVITY_TEMPLATE,
        "minimal": MINIMAL_TEMPLATE,
    }

    # ========== VALIDATION METHODS ==========

    def validate_template(self, template: str) -> bool:
        """
        Validate that template exists.

        Args:
            template: Template name (program, activity, milestone, minimal)

        Returns:
            True if valid, False otherwise
        """
        return template in self.TEMPLATES or template == "milestone"

    def _validate_ppa(self, ppa) -> None:
        """Validate PPA instance before generation."""
        if not ppa:
            raise ValidationError("PPA instance is required")

        if not ppa.title:
            raise ValidationError("PPA must have a title")

    # ========== BUDGET DISTRIBUTION METHODS ==========

    def _distribute_budget(
        self,
        total_budget: Optional[Decimal],
        percentage: Decimal,
    ) -> Optional[Decimal]:
        """
        Distribute budget based on percentage.

        Args:
            total_budget: Total budget to distribute
            percentage: Percentage allocation (0-100)

        Returns:
            Allocated budget or None if total_budget is None
        """
        if total_budget is None or total_budget == 0:
            return None

        try:
            # Calculate allocation
            allocation = (total_budget * percentage) / Decimal("100.00")
            # Round to 2 decimal places
            return allocation.quantize(Decimal("0.01"))
        except (InvalidOperation, TypeError):
            logger.warning(
                f"Invalid budget calculation: total={total_budget}, percentage={percentage}"
            )
            return None

    def _distribute_dates(
        self,
        start_date: Optional[date],
        end_date: Optional[date],
        duration_percentage: Decimal,
        offset_percentage: Decimal = Decimal("0.00"),
    ) -> tuple[Optional[date], Optional[date]]:
        """
        Distribute dates based on duration percentage.

        Args:
            start_date: Project start date
            end_date: Project end date
            duration_percentage: Percentage of total duration (0-100)
            offset_percentage: Offset from start (0-100)

        Returns:
            Tuple of (start_date, end_date) or (None, None)
        """
        if not start_date or not end_date:
            return None, None

        try:
            # Calculate total duration in days
            total_days = (end_date - start_date).days

            # Calculate offset days
            offset_days = int((total_days * offset_percentage) / Decimal("100.00"))

            # Calculate duration days
            duration_days = int((total_days * duration_percentage) / Decimal("100.00"))

            # Calculate new dates
            new_start = start_date + timedelta(days=offset_days)
            new_end = new_start + timedelta(days=duration_days)

            return new_start, new_end
        except (TypeError, ValueError) as e:
            logger.warning(f"Invalid date calculation: {e}")
            return None, None

    # ========== WORKITEM CREATION METHODS ==========

    def _create_workitem(
        self,
        ppa,
        title: str,
        work_type: str,
        parent=None,
        allocated_budget: Optional[Decimal] = None,
        start_date: Optional[date] = None,
        due_date: Optional[date] = None,
        priority: str = "medium",
        created_by: Optional[User] = None,
        **kwargs,
    ):
        """
        Create a single WorkItem instance.

        Args:
            ppa: Source MonitoringEntry (PPA)
            title: WorkItem title
            work_type: WorkItem type (project, sub_project, activity, task)
            parent: Parent WorkItem (None for root)
            allocated_budget: Budget allocation
            start_date: Start date
            due_date: Due date
            priority: Priority level
            created_by: User who created the work item
            **kwargs: Additional WorkItem fields

        Returns:
            WorkItem instance
        """
        from common.work_item_model import WorkItem

        # Map PPA status to WorkItem status
        status_mapping = {
            "planning": WorkItem.STATUS_NOT_STARTED,
            "ongoing": WorkItem.STATUS_IN_PROGRESS,
            "completed": WorkItem.STATUS_COMPLETED,
            "on_hold": WorkItem.STATUS_BLOCKED,
            "cancelled": WorkItem.STATUS_CANCELLED,
        }

        workitem = WorkItem(
            work_type=work_type,
            title=title,
            description=kwargs.get("description", ""),
            parent=parent,
            status=status_mapping.get(ppa.status, WorkItem.STATUS_NOT_STARTED),
            priority=priority,
            start_date=start_date,
            due_date=due_date,
            allocated_budget=allocated_budget,
            related_ppa=ppa,
            created_by=created_by,
            is_calendar_visible=True,
        )

        # Set domain-specific data
        if work_type in ["project", "sub_project"]:
            workitem.project_data = {
                "ppa_category": ppa.category,
                "fiscal_year": ppa.fiscal_year,
                "sector": ppa.sector,
            }
        elif work_type in ["activity", "sub_activity"]:
            workitem.activity_data = {
                "implementing_moa": str(ppa.implementing_moa.id) if ppa.implementing_moa else None,
                "coverage_region": str(ppa.coverage_region.id) if ppa.coverage_region else None,
            }

        workitem.full_clean()
        workitem.save()

        logger.info(
            f"Created WorkItem: {workitem.get_work_type_display()} - {workitem.title}"
        )

        return workitem

    def _create_hierarchy_from_structure(
        self,
        ppa,
        structure: List[Dict[str, Any]],
        parent,
        total_budget: Optional[Decimal],
        start_date: Optional[date],
        end_date: Optional[date],
        created_by: Optional[User],
        offset_percentage: Decimal = Decimal("0.00"),
    ) -> List:
        """
        Recursively create WorkItem hierarchy from structure definition.

        Args:
            ppa: Source PPA
            structure: List of structure definitions
            parent: Parent WorkItem
            total_budget: Total budget for this level
            start_date: Start date
            end_date: End date
            created_by: User
            offset_percentage: Cumulative offset for date calculation

        Returns:
            List of created WorkItems
        """
        created_items = []
        cumulative_offset = offset_percentage

        for item_def in structure:
            # Extract definition fields
            title = item_def.get("title")
            work_type = item_def.get("work_type")
            budget_pct = item_def.get("budget_percentage", Decimal("0.00"))
            duration_pct = item_def.get("duration_percentage", budget_pct)
            priority = item_def.get("priority", "medium")
            children_def = item_def.get("children", [])

            # Calculate budget allocation
            allocated_budget = self._distribute_budget(total_budget, budget_pct)

            # Calculate dates
            item_start, item_end = self._distribute_dates(
                start_date, end_date, duration_pct, cumulative_offset
            )

            # Create WorkItem
            workitem = self._create_workitem(
                ppa=ppa,
                title=title,
                work_type=work_type,
                parent=parent,
                allocated_budget=allocated_budget,
                start_date=item_start,
                due_date=item_end,
                priority=priority,
                created_by=created_by,
            )

            created_items.append(workitem)

            # Create children if defined
            if children_def:
                child_items = self._create_hierarchy_from_structure(
                    ppa=ppa,
                    structure=children_def,
                    parent=workitem,
                    total_budget=allocated_budget,
                    start_date=item_start,
                    end_date=item_end,
                    created_by=created_by,
                )
                created_items.extend(child_items)

            # Update cumulative offset for next sibling
            cumulative_offset += duration_pct

        return created_items

    # ========== MAIN GENERATION METHODS ==========

    @transaction.atomic
    def generate_from_ppa(
        self,
        ppa,
        template: str = "activity",
        created_by: Optional[User] = None,
    ):
        """
        Create root project WorkItem from PPA using specified template.

        Args:
            ppa: MonitoringEntry instance
            template: Template name (program, activity, minimal, milestone)
            created_by: User creating the work items

        Returns:
            Root WorkItem instance

        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        self._validate_ppa(ppa)

        if not self.validate_template(template):
            raise ValidationError(f"Invalid template: {template}")

        # Handle milestone template separately
        if template == "milestone":
            return self._generate_from_milestone_template(ppa, created_by)

        # Get template definition
        template_def = self.TEMPLATES[template]
        structure = template_def["structure"]

        # Create root project
        root_project = self._create_workitem(
            ppa=ppa,
            title=ppa.title,
            work_type="project",
            parent=None,
            allocated_budget=ppa.budget_allocation,
            start_date=ppa.start_date,
            due_date=ppa.target_end_date,
            priority=ppa.priority if ppa.priority else "medium",
            created_by=created_by,
            description=ppa.summary,
        )

        logger.info(f"Created root project for PPA: {ppa.title} (template: {template})")

        # Generate hierarchy
        self._create_hierarchy_from_structure(
            ppa=ppa,
            structure=structure,
            parent=root_project,
            total_budget=ppa.budget_allocation,
            start_date=ppa.start_date,
            end_date=ppa.target_end_date,
            created_by=created_by,
        )

        logger.info(
            f"Generated WorkItem hierarchy for PPA {ppa.id}: "
            f"{root_project.get_descendants().count()} items created"
        )

        return root_project

    def _generate_from_milestone_template(
        self,
        ppa,
        created_by: Optional[User],
    ):
        """
        Generate WorkItems from PPA milestone_dates JSON field.

        Creates one activity per milestone with equal budget distribution.

        Args:
            ppa: MonitoringEntry instance
            created_by: User creating the work items

        Returns:
            Root WorkItem instance
        """
        from common.work_item_model import WorkItem

        # Create root project
        root_project = self._create_workitem(
            ppa=ppa,
            title=ppa.title,
            work_type="project",
            parent=None,
            allocated_budget=ppa.budget_allocation,
            start_date=ppa.start_date,
            due_date=ppa.target_end_date,
            priority=ppa.priority if ppa.priority else "medium",
            created_by=created_by,
            description=ppa.summary,
        )

        # Extract milestones
        milestones = ppa.milestone_dates or []

        if not milestones:
            logger.warning(f"PPA {ppa.id} has no milestones, creating minimal structure")
            # Create single task
            self._create_workitem(
                ppa=ppa,
                title="Main Deliverable",
                work_type="task",
                parent=root_project,
                allocated_budget=ppa.budget_allocation,
                start_date=ppa.start_date,
                due_date=ppa.target_end_date,
                priority="high",
                created_by=created_by,
            )
            return root_project

        # Calculate equal budget distribution
        milestone_count = len(milestones)
        budget_per_milestone = None

        if ppa.budget_allocation:
            budget_per_milestone = (ppa.budget_allocation / milestone_count).quantize(
                Decimal("0.01")
            )

        # Create activity per milestone
        for idx, milestone in enumerate(milestones):
            milestone_title = milestone.get("title", f"Milestone {idx + 1}")
            milestone_date = milestone.get("date")
            milestone_status = milestone.get("status", "upcoming")

            # Map milestone status to WorkItem status
            status_map = {
                "upcoming": WorkItem.STATUS_NOT_STARTED,
                "in_progress": WorkItem.STATUS_IN_PROGRESS,
                "completed": WorkItem.STATUS_COMPLETED,
                "delayed": WorkItem.STATUS_AT_RISK,
            }

            # Create activity
            activity = self._create_workitem(
                ppa=ppa,
                title=milestone_title,
                work_type="activity",
                parent=root_project,
                allocated_budget=budget_per_milestone,
                start_date=ppa.start_date,
                due_date=milestone_date,
                priority=ppa.priority if ppa.priority else "medium",
                created_by=created_by,
            )

            # Override status from milestone
            activity.status = status_map.get(milestone_status, WorkItem.STATUS_NOT_STARTED)
            activity.save(update_fields=["status"])

        logger.info(
            f"Generated milestone-based hierarchy for PPA {ppa.id}: "
            f"{milestone_count} milestones"
        )

        return root_project

    @transaction.atomic
    def generate_from_outcome_framework(
        self,
        ppa,
        created_by: Optional[User] = None,
    ):
        """
        Generate WorkItems from PPA outcome_framework JSON field.

        Creates activities from outcomes and tasks from outputs.

        Expected outcome_framework structure:
        {
            "outcomes": [
                {
                    "title": "Outcome 1",
                    "outputs": [
                        {"title": "Output 1.1"},
                        {"title": "Output 1.2"}
                    ]
                }
            ]
        }

        Args:
            ppa: MonitoringEntry instance
            created_by: User creating the work items

        Returns:
            Root WorkItem instance

        Raises:
            ValidationError: If outcome_framework is missing or invalid
        """
        self._validate_ppa(ppa)

        # Create root project
        root_project = self._create_workitem(
            ppa=ppa,
            title=ppa.title,
            work_type="project",
            parent=None,
            allocated_budget=ppa.budget_allocation,
            start_date=ppa.start_date,
            due_date=ppa.target_end_date,
            priority=ppa.priority if ppa.priority else "medium",
            created_by=created_by,
            description=ppa.summary,
        )

        # Extract outcome framework
        outcome_framework = ppa.outcome_framework or {}
        outcomes = outcome_framework.get("outcomes", [])

        if not outcomes:
            logger.warning(
                f"PPA {ppa.id} has no outcome framework, falling back to minimal template"
            )
            # Create single task
            self._create_workitem(
                ppa=ppa,
                title="Main Deliverable",
                work_type="task",
                parent=root_project,
                allocated_budget=ppa.budget_allocation,
                start_date=ppa.start_date,
                due_date=ppa.target_end_date,
                priority="high",
                created_by=created_by,
            )
            return root_project

        # Calculate budget per outcome (equal distribution)
        outcome_count = len(outcomes)
        budget_per_outcome = None

        if ppa.budget_allocation:
            budget_per_outcome = (ppa.budget_allocation / outcome_count).quantize(
                Decimal("0.01")
            )

        # Create activities from outcomes
        for outcome in outcomes:
            outcome_title = outcome.get("title", "Untitled Outcome")
            outputs = outcome.get("outputs", [])

            # Create activity for outcome
            activity = self._create_workitem(
                ppa=ppa,
                title=outcome_title,
                work_type="activity",
                parent=root_project,
                allocated_budget=budget_per_outcome,
                start_date=ppa.start_date,
                due_date=ppa.target_end_date,
                priority="high",
                created_by=created_by,
            )

            # Calculate budget per output
            output_count = len(outputs) if outputs else 1
            budget_per_output = None

            if budget_per_outcome:
                budget_per_output = (budget_per_outcome / output_count).quantize(
                    Decimal("0.01")
                )

            # Create tasks from outputs
            if outputs:
                for output in outputs:
                    output_title = output.get("title", "Untitled Output")

                    self._create_workitem(
                        ppa=ppa,
                        title=output_title,
                        work_type="task",
                        parent=activity,
                        allocated_budget=budget_per_output,
                        start_date=ppa.start_date,
                        due_date=ppa.target_end_date,
                        priority="medium",
                        created_by=created_by,
                    )

        logger.info(
            f"Generated outcome-based hierarchy for PPA {ppa.id}: "
            f"{root_project.get_descendants().count()} items created"
        )

        return root_project
