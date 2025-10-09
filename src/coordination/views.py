"""Frontend views for the coordination module."""

import json
import logging
import warnings
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils import timezone

from common.utils.moa_permissions import moa_can_edit_organization

from common.models import RecurringEventPattern
from common.work_item_model import WorkItem
from common.forms.work_items import WorkItemForm
from monitoring.models import MonitoringEntry
from monitoring.services import build_moa_budget_tracking

from .forms import (
    OrganizationContactFormSet,
    OrganizationForm,
    PartnershipDocumentFormSet,
    PartnershipForm,
    PartnershipMilestoneFormSet,
    PartnershipSignatoryFormSet,
    RecurringEventPatternForm,
    StakeholderEngagementForm,
)
# Event model removed - use WorkItem with work_type='activity' instead
from .models import Organization, Partnership, StakeholderEngagement


logger = logging.getLogger(__name__)

# Event-related helper functions removed - use WorkItem calendar serialization instead
# _calendar_iso, _combine_event_datetime, _serialize_coordination_event deleted


def _split_paragraphs(text_value):
    """Normalize multiline text into readable paragraph blocks."""

    if not text_value:
        return []

    normalized = text_value.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        return []

    paragraphs = [
        paragraph.strip()
        for paragraph in normalized.split("\n\n")
        if paragraph.strip()
    ]
    if paragraphs:
        return paragraphs

    # Fall back to a single paragraph when only single newlines are present.
    single_lines = [
        line.strip()
        for line in normalized.split("\n")
        if line.strip()
    ]
    if single_lines:
        return [" ".join(single_lines)]

    return []


def _split_list_items(text_value):
    """Convert a newline or bullet separated string into a clean list."""

    if not text_value:
        return []

    normalized = text_value.replace("\r\n", "\n").replace("\r", "\n")

    items = []
    for line in normalized.split("\n"):
        cleaned = line.strip()
        if not cleaned:
            continue
        cleaned = cleaned.lstrip("-•*").strip()
        if cleaned:
            items.append(cleaned)
    return items


def _organization_form(request, organization_id=None):
    """Shared create/update handler for organization form flow."""

    organization_id = (
        organization_id
        or request.GET.get("organization")
        or request.POST.get("organization_id")
    )
    is_edit = bool(organization_id)
    organization = None

    if is_edit:
        try:
            organization = get_object_or_404(Organization, pk=organization_id)
            if not request.user.has_perm("coordination.change_organization"):
                raise PermissionDenied
        except (Organization.DoesNotExist, ValueError):
            # Invalid or non-existent organization ID - treat as create
            is_edit = False
            organization = None

    if not is_edit:
        if not request.user.has_perm("coordination.add_organization"):
            raise PermissionDenied

    form_instance = organization or Organization(created_by=request.user)

    if request.method == "POST":
        form_kwargs = {"instance": organization} if is_edit else {}
        form = OrganizationForm(request.POST, **form_kwargs)
        formset = OrganizationContactFormSet(
            request.POST,
            instance=form_instance,
            prefix="contacts",
        )

        if form.is_valid() and formset.is_valid():
            saved_organization = form.save(commit=False)
            if not is_edit:
                saved_organization.created_by = request.user
            saved_organization.save()
            formset.instance = saved_organization
            formset.save()
            if is_edit:
                messages.success(request, "Organization successfully updated.")
                return redirect(
                    "common:coordination_organization_detail",
                    organization_id=saved_organization.pk,
                )
            messages.success(request, "Organization successfully created.")
            return redirect("common:coordination_organizations")
        messages.error(request, "Please correct the errors below before submitting.")
        if form.errors:
            logger.warning("Organization form errors: %s", form.errors)
        if formset.errors or formset.non_form_errors():
            logger.warning(
                "Organization contact formset errors: %s | non-form: %s",
                formset.errors,
                formset.non_form_errors(),
            )
    else:
        form_kwargs = {"instance": organization} if is_edit else {}
        form = OrganizationForm(**form_kwargs)
        formset = OrganizationContactFormSet(
            instance=form_instance,
            prefix="contacts",
        )

    context = {
        "form": form,
        "formset": formset,
        "return_url": reverse("common:coordination_organizations"),
        "is_edit": is_edit,
        "organization": organization,
    }
    return render(request, "coordination/organization_form.html", context)


@login_required
def organization_create(request):
    """Render and process the frontend organization creation form."""

    return _organization_form(request)


@moa_can_edit_organization
@login_required
def organization_edit(request, organization_id):
    """Render and process the frontend organization edit form."""

    return _organization_form(request, organization_id=organization_id)


@login_required
def organization_detail(request, organization_id):
    """Display organization details in the frontend directory."""

    organization = get_object_or_404(
        Organization.objects.select_related("created_by").prefetch_related(
            "contacts",
            "led_partnerships__lead_organization",
            "partnerships__lead_organization",
        ),
        pk=organization_id,
    )

    led_partnerships = list(organization.led_partnerships.all())
    led_partnership_ids = {partnership.pk for partnership in led_partnerships}
    member_partnerships = [
        partnership
        for partnership in organization.partnerships.all()
        if partnership.pk not in led_partnership_ids
    ]
    contacts = list(organization.contacts.all())
    total_partnerships = len(led_partnerships) + len(member_partnerships)

    moa_ppas_queryset = (
        MonitoringEntry.objects.filter(
            category="moa_ppa", implementing_moa=organization
        )
        .select_related("implementing_moa")
        .order_by("-updated_at")
    )
    moa_ppas = list(moa_ppas_queryset)
    moa_ppas_total_budget = sum(
        (ppa.budget_allocation or Decimal("0")) for ppa in moa_ppas
    )

    auto_special_text = ""
    display_notes = organization.notes
    if organization.notes and organization.notes.startswith("Special Provisions:"):
        auto_special_text = organization.notes[len("Special Provisions:"):].lstrip()
        display_notes = ""

    ppa_special_provisions = []
    for ppa in moa_ppas:
        support_text = (ppa.support_required or "").strip()
        if not support_text:
            continue
        if support_text.startswith("Special Provision:"):
            _, _, support_text = support_text.partition(":")
            support_text = support_text.lstrip()
        ppa_special_provisions.append({
            "entry": ppa,
            "text": support_text,
        })

    # Collect work items and budget data for MOA tabs
    moa_work_items = []
    moa_work_items_stats = {
        "total": 0,
        "in_progress": 0,
        "completed": 0,
        "avg_progress": 0,
    }
    moa_budget_stats = {
        "total_budget": Decimal("0.00"),
        "total_allocated": Decimal("0.00"),
        "total_expenditure": Decimal("0.00"),
        "utilization_rate": 0.0,
        "total_variance": Decimal("0.00"),
    }

    if organization.organization_type == "bmoa" and moa_ppas:
        # Get all work items for this MOA's PPAs
        moa_work_items = WorkItem.objects.filter(
            ppa_category="moa_ppa",
            implementing_moa=organization,
        ).select_related(
            "related_ppa",
            "created_by",
        ).prefetch_related(
            "assignees",
            "teams",
        ).order_by("-created_at")[
            :100
        ]  # Limit to 100 most recent

        # Calculate work items stats
        work_items_list = list(moa_work_items)
        moa_work_items_stats = {
            "total": len(work_items_list),
            "in_progress": sum(
                1 for wi in work_items_list if wi.status == "in_progress"
            ),
            "completed": sum(1 for wi in work_items_list if wi.status == "completed"),
            "avg_progress": (
                sum(wi.progress for wi in work_items_list) / len(work_items_list)
                if work_items_list
                else 0
            ),
        }

        budget_context = build_moa_budget_tracking(organization, moa_ppas)
        moa_ppas = budget_context["moa_ppas"]
        moa_budget_stats = budget_context["moa_budget_stats"]
        moa_ppas_total_budget = moa_budget_stats["total_budget"]

    mandate_paragraphs = _split_paragraphs(organization.mandate)
    powers_and_functions_items = _split_list_items(
        organization.powers_and_functions
    )

    context = {
        "organization": organization,
        "contacts": contacts,
        "led_partnerships": led_partnerships,
        "member_partnerships": member_partnerships,
        "return_url": reverse("common:coordination_organizations"),
        "total_partnerships": total_partnerships,
        "moa_ppas_count": len(moa_ppas),
        "moa_ppas": moa_ppas,
        "moa_ppas_total_budget": moa_ppas_total_budget,
        "organization_notes_display": display_notes,
        "moa_special_provisions_text": auto_special_text,
        "ppa_special_provisions": ppa_special_provisions,
        # MOA tabs data
        "moa_work_items": moa_work_items,
        "moa_work_items_stats": moa_work_items_stats,
        "moa_budget_stats": moa_budget_stats,
        "organization_mandate_paragraphs": mandate_paragraphs,
        "organization_powers_and_functions": powers_and_functions_items,
    }
    return render(request, "coordination/organization_detail.html", context)


@moa_can_edit_organization
@login_required
def organization_delete(request, organization_id):
    """Handle deletion of an organization from the frontend UI."""

    organization = get_object_or_404(Organization, pk=organization_id)

    if not request.user.has_perm("coordination.delete_organization"):
        raise PermissionDenied

    if request.method == "POST":
        try:
            organization.delete()
        except ProtectedError as error:
            logger.warning(
                "Failed to delete organization %s due to protected relations: %s",
                organization.pk,
                error,
            )
            messages.error(
                request,
                "Unable to delete this organization because it is referenced by other records.",
            )
            return redirect(
                "common:coordination_organization_detail",
                organization_id=organization.pk,
            )
        messages.success(request, "Organization successfully deleted.")
        return redirect("common:coordination_organizations")

    context = {
        "organization": organization,
        "return_url": reverse("common:coordination_organizations"),
    }
    return render(request, "coordination/organization_confirm_delete.html", context)


@login_required
def partnership_create(request):
    """Render and process the frontend partnership creation form."""

    if not request.user.has_perm("coordination.add_partnership"):
        raise PermissionDenied

    partnership_instance = Partnership(created_by=request.user)

    if request.method == "POST":
        form = PartnershipForm(request.POST, request.FILES)
        signatory_formset = PartnershipSignatoryFormSet(
            request.POST,
            instance=partnership_instance,
            prefix="signatories",
        )
        milestone_formset = PartnershipMilestoneFormSet(
            request.POST,
            instance=partnership_instance,
            prefix="milestones",
        )
        document_formset = PartnershipDocumentFormSet(
            request.POST,
            request.FILES,
            instance=partnership_instance,
            prefix="documents",
        )

        if (
            form.is_valid()
            and signatory_formset.is_valid()
            and milestone_formset.is_valid()
            and document_formset.is_valid()
        ):
            partnership = form.save(commit=False)
            partnership.created_by = request.user
            partnership.save()
            if hasattr(form, "save_m2m"):
                form.save_m2m()

            signatory_formset.instance = partnership
            milestone_formset.instance = partnership
            document_formset.instance = partnership

            signatory_formset.save()
            milestone_formset.save()
            document_formset.save()

            messages.success(request, "Partnership successfully created.")
            return redirect("common:coordination_partnerships")
    else:
        form = PartnershipForm()
        signatory_formset = PartnershipSignatoryFormSet(
            instance=partnership_instance,
            prefix="signatories",
        )
        milestone_formset = PartnershipMilestoneFormSet(
            instance=partnership_instance,
            prefix="milestones",
        )
        document_formset = PartnershipDocumentFormSet(
            instance=partnership_instance,
            prefix="documents",
        )

    context = {
        "form": form,
        "signatory_formset": signatory_formset,
        "milestone_formset": milestone_formset,
        "document_formset": document_formset,
        "return_url": reverse("common:coordination_partnerships"),
        "page_title": "Create Partnership",
        "breadcrumb_label": "Create Partnership",
        "page_heading": "New Partnership Agreement",
        "submit_label": "Create partnership",
        "is_edit": False,
    }
    return render(request, "coordination/partnership_form.html", context)


@login_required
def partnership_detail(request, partnership_id):
    """Render a partnership summary mirroring community detail views."""

    partnership = get_object_or_404(
        Partnership.objects.select_related(
            "lead_organization",
            "focal_person",
            "backup_focal_person",
            "created_by",
        ).prefetch_related(
            "organizations",
            "communities",
            "signatories__organization",
            "milestones",
            "documents",
        ),
        pk=partnership_id,
    )

    signatories = partnership.signatories.select_related("organization").all()
    milestones = partnership.milestones.all()
    documents = partnership.documents.all()

    context = {
        "partnership": partnership,
        "signatories": signatories,
        "milestones": milestones,
        "documents": documents,
        "return_url": reverse("common:coordination_partnerships"),
    }
    return render(request, "coordination/partnership_view.html", context)


@login_required
def partnership_update(request, partnership_id):
    """Update an existing partnership using the shared frontend form."""

    if not request.user.has_perm("coordination.change_partnership"):
        raise PermissionDenied

    partnership = get_object_or_404(
        Partnership.objects.select_related("lead_organization"), pk=partnership_id
    )

    if request.method == "POST":
        form = PartnershipForm(request.POST, request.FILES, instance=partnership)
        signatory_formset = PartnershipSignatoryFormSet(
            request.POST,
            instance=partnership,
            prefix="signatories",
        )
        milestone_formset = PartnershipMilestoneFormSet(
            request.POST,
            instance=partnership,
            prefix="milestones",
        )
        document_formset = PartnershipDocumentFormSet(
            request.POST,
            request.FILES,
            instance=partnership,
            prefix="documents",
        )

        if (
            form.is_valid()
            and signatory_formset.is_valid()
            and milestone_formset.is_valid()
            and document_formset.is_valid()
        ):
            with transaction.atomic():
                partnership = form.save(commit=False)
                partnership.save()
                if hasattr(form, "save_m2m"):
                    form.save_m2m()

                signatory_formset.save()
                milestone_formset.save()
                document_formset.save()

            messages.success(request, "Partnership successfully updated.")
            return redirect("common:coordination_partnership_view", partnership.pk)
    else:
        form = PartnershipForm(instance=partnership)
        signatory_formset = PartnershipSignatoryFormSet(
            instance=partnership,
            prefix="signatories",
        )
        milestone_formset = PartnershipMilestoneFormSet(
            instance=partnership,
            prefix="milestones",
        )
        document_formset = PartnershipDocumentFormSet(
            instance=partnership,
            prefix="documents",
        )

    context = {
        "form": form,
        "signatory_formset": signatory_formset,
        "milestone_formset": milestone_formset,
        "document_formset": document_formset,
        "partnership": partnership,
        "return_url": reverse("common:coordination_partnerships"),
        "page_title": "Edit Partnership",
        "breadcrumb_label": "Edit Partnership",
        "page_heading": f"Edit {partnership.title}",
        "submit_label": "Save changes",
        "is_edit": True,
    }
    return render(request, "coordination/partnership_form.html", context)


@login_required
@require_POST
def partnership_delete(request, partnership_id):
    """Delete an existing partnership entry."""
    if not request.user.has_perm("coordination.delete_partnership"):
        raise PermissionDenied

    partnership = get_object_or_404(Partnership, pk=partnership_id)
    title = partnership.title

    with transaction.atomic():
        partnership.delete()

    messages.success(request, f'Partnership "{title}" has been removed.')
    return redirect("common:coordination_partnerships")


# event_create function removed - use WorkItem create view with work_type='activity' instead

@login_required
def engagement_create(request):
    """Render and process creation of coordination activities."""

    if not request.user.has_perm("coordination.add_stakeholderengagement"):
        raise PermissionDenied

    initial = {
        "status": "planned",
        "priority": "medium",
        "planned_date": timezone.now().replace(
            hour=9, minute=0, second=0, microsecond=0
        ),
    }

    if request.method == "POST":
        form = StakeholderEngagementForm(request.POST)
        if form.is_valid():
            engagement = form.save(commit=False)
            engagement.created_by = request.user
            engagement.save()
            if hasattr(form, "save_m2m"):
                form.save_m2m()
            messages.success(request, "Coordination activity recorded successfully.")
            return redirect("common:coordination_home")
        messages.error(
            request, "Please correct the highlighted errors before submitting."
        )
        if form.errors:
            logger.warning("Stakeholder engagement form errors: %s", form.errors)
    else:
        form = StakeholderEngagementForm(initial=initial)

    context = {
        "form": form,
        "return_url": reverse("common:coordination_home"),
        "page_title": "Log Coordination Activity",
        "page_heading": "Record Coordination Activity",
        "submit_label": "Save Activity",
    }
    return render(request, "coordination/activity_form.html", context)


# calendar_overview function removed - use unified calendar with WorkItem filtering instead

@login_required
def event_create_recurring(request):
    """Create a recurring activity with recurrence pattern configuration."""

    if not request.user.has_perm("coordination.add_event"):
        raise PermissionDenied

    initial = {
        "work_type": "activity",
        "status": "not_started",
        "priority": "medium",
        "start_date": timezone.now().date(),
        "is_calendar_visible": True,
    }

    if request.method == "POST":
        work_item_form = WorkItemForm(request.POST, initial={"work_type": "activity"})
        pattern_form = RecurringEventPatternForm(request.POST)

        if work_item_form.is_valid() and pattern_form.is_valid():
            with transaction.atomic():
                # Save the recurrence pattern first
                pattern = pattern_form.save()

                # Save the work item with the pattern
                work_item = work_item_form.save(commit=False)
                work_item.work_type = "activity"
                work_item.created_by = request.user
                # Store recurrence pattern in type_specific_data
                if not work_item.type_specific_data:
                    work_item.type_specific_data = {}
                work_item.type_specific_data["is_recurring"] = True
                work_item.type_specific_data["recurrence_pattern_id"] = pattern.id
                work_item.save()

                if hasattr(work_item_form, "save_m2m"):
                    work_item_form.save_m2m()

            messages.success(
                request,
                f"Recurring activity '{work_item.title}' successfully created. "
                f"Instances will be generated automatically.",
            )
            return redirect("common:coordination_events")

        messages.error(
            request, "Please correct the highlighted errors before submitting."
        )
        if work_item_form.errors:
            logger.warning("WorkItem form errors: %s", work_item_form.errors)
        if pattern_form.errors:
            logger.warning("Recurrence pattern form errors: %s", pattern_form.errors)
    else:
        work_item_form = WorkItemForm(initial=initial)
        pattern_form = RecurringEventPatternForm()

    context = {
        "event_form": work_item_form,  # Keep 'event_form' for template compatibility
        "pattern_form": pattern_form,
        "return_url": reverse("common:coordination_events"),
        "page_title": "Schedule Recurring Activity",
        "page_heading": "Schedule New Recurring Activity",
        "submit_label": "Create Recurring Activity",
    }
    return render(request, "coordination/event_recurring_form.html", context)


@login_required
def event_edit_instance(request, event_id):
    """Edit a specific work item (activity) instance with recurring logic."""

    if not request.user.has_perm("coordination.change_event"):
        raise PermissionDenied

    work_item = get_object_or_404(WorkItem, pk=event_id, work_type="activity")

    # Check if this is a recurring work item
    type_data = work_item.type_specific_data or {}
    is_recurring = type_data.get("is_recurring", False)
    recurrence_parent_id = type_data.get("recurrence_parent_id")
    is_recurring_instance = recurrence_parent_id is not None
    is_recurring_parent = is_recurring and not is_recurring_instance

    edit_scope = request.POST.get("edit_scope", "this")  # 'this', 'future', or 'all'

    if request.method == "POST" and "confirm_scope" in request.POST:
        form = WorkItemForm(request.POST, instance=work_item)

        if form.is_valid():
            with transaction.atomic():
                if edit_scope == "this":
                    # Edit only this instance - mark as exception
                    updated_item = form.save(commit=False)
                    if not updated_item.type_specific_data:
                        updated_item.type_specific_data = {}
                    updated_item.type_specific_data["is_recurrence_exception"] = True
                    updated_item.save()
                    if hasattr(form, "save_m2m"):
                        form.save_m2m()
                    messages.success(
                        request, "This activity instance has been updated successfully."
                    )

                elif edit_scope == "future" and is_recurring_instance:
                    # Edit this and all future instances
                    parent_id = recurrence_parent_id
                    future_instances = WorkItem.objects.filter(
                        work_type="activity",
                        type_specific_data__recurrence_parent_id=parent_id,
                        start_date__gte=work_item.start_date,
                    )

                    # Update all future instances
                    for instance in future_instances:
                        for field in form.changed_data:
                            setattr(instance, field, form.cleaned_data[field])
                        instance.save()

                    messages.success(
                        request,
                        f"This and {future_instances.count() - 1} future instances updated.",
                    )

                elif edit_scope == "all" or (
                    edit_scope == "future" and is_recurring_parent
                ):
                    # Edit parent work item and all instances
                    parent = work_item if is_recurring_parent else WorkItem.objects.get(pk=recurrence_parent_id)

                    # Update parent
                    for field in form.changed_data:
                        setattr(parent, field, form.cleaned_data[field])
                    parent.save()

                    # Update all instances
                    instances = WorkItem.objects.filter(
                        work_type="activity",
                        type_specific_data__recurrence_parent_id=parent.pk
                    )
                    for instance in instances:
                        for field in form.changed_data:
                            setattr(instance, field, form.cleaned_data[field])
                        instance.save()

                    messages.success(
                        request,
                        f"Parent activity and all {instances.count()} instances updated.",
                    )

            return redirect("common:coordination_events")

        messages.error(
            request, "Please correct the highlighted errors before submitting."
        )
        if form.errors:
            logger.warning("WorkItem form errors: %s", form.errors)
    else:
        form = WorkItemForm(instance=work_item)

    # Provide scope options in context
    scope_options = []
    if is_recurring_instance or is_recurring_parent:
        scope_options.append(
            {"value": "this", "label": "Only this activity", "description": ""}
        )
        if is_recurring_instance:
            parent_id = recurrence_parent_id
            future_count = WorkItem.objects.filter(
                work_type="activity",
                type_specific_data__recurrence_parent_id=parent_id,
                start_date__gte=work_item.start_date
            ).count()
            scope_options.append(
                {
                    "value": "future",
                    "label": "This and future activities",
                    "description": f"Will update {future_count} activities",
                }
            )
        scope_options.append(
            {
                "value": "all",
                "label": "All activities in series",
                "description": "Will update the entire recurring series",
            }
        )

    context = {
        "form": form,
        "event": work_item,  # Keep 'event' for template compatibility
        "is_recurring_instance": is_recurring_instance,
        "is_recurring_parent": is_recurring_parent,
        "scope_options": scope_options,
        "return_url": reverse("common:coordination_events"),
        "page_title": "Edit Activity Instance",
        "page_heading": f"Edit {work_item.title}",
        "submit_label": "Save Changes",
    }
    return render(request, "coordination/event_edit_instance.html", context)


@login_required
def coordination_event_modal(request, event_id):
    """Render coordination activity quick-update modal (WorkItem-based)."""

    work_item = get_object_or_404(
        WorkItem.objects.prefetch_related("assignees", "teams", "children"),
        pk=event_id,
        work_type="activity"
    )

    if not (
        request.user.is_staff
        or request.user.is_superuser
        or work_item.created_by == request.user
        or request.user.has_perm("coordination.change_event")
    ):
        raise PermissionDenied

    if request.method == "POST":
        form = WorkItemForm(request.POST, instance=work_item)
        if form.is_valid():
            form.save()
            work_item.refresh_from_db()

            # Serialize for calendar update
            payload = {
                "id": str(work_item.id),
                "title": work_item.title,
                "start": work_item.start_date.isoformat() if work_item.start_date else None,
                "end": work_item.due_date.isoformat() if work_item.due_date else None,
                "backgroundColor": work_item.calendar_color or "#3B82F6",
                "extendedProps": {
                    "status": work_item.status,
                    "priority": work_item.priority,
                }
            }

            context = {
                "event": work_item,  # Keep 'event' for template compatibility
                "form": WorkItemForm(instance=work_item),
                "save_success": True,
                "assignees": work_item.assignees.all(),
                "teams": work_item.teams.all(),
                "linked_tasks": work_item.children.filter(work_type="task"),
            }
            response = render(
                request, "coordination/partials/event_modal.html", context
            )
            trigger_payload = {
                "show-toast": "Activity updated successfully",
                "calendar-close-modal": True,
                "calendar-event-updated": payload,
            }
            response["HX-Trigger"] = json.dumps(trigger_payload)
            return response
    else:
        form = WorkItemForm(instance=work_item)

    context = {
        "event": work_item,  # Keep 'event' for template compatibility
        "form": form,
        "save_success": False,
        "assignees": work_item.assignees.all(),
        "teams": work_item.teams.all(),
        "linked_tasks": work_item.children.filter(work_type="task"),
    }
    return render(request, "coordination/partials/event_modal.html", context)


@login_required
def coordination_event_delete(request, event_id):
    """Delete a coordination activity (WorkItem)."""
    logger.info(f"Attempting to delete activity {event_id}")
    work_item = get_object_or_404(WorkItem, pk=event_id, work_type="activity")

    # Check permissions
    if not (
        request.user.is_staff
        or request.user.is_superuser
        or work_item.created_by == request.user
        or request.user.has_perm("coordination.delete_event")
    ):
        raise PermissionDenied

    # Check if this is a confirmation request
    if request.POST.get("confirm") == "yes":
        activity_title = work_item.title
        logger.info(f"Deleting activity: {activity_title}")
        work_item.delete()
        logger.info(f"Activity {activity_title} deleted successfully")

        # SIMPLE APPROACH: Just add message and redirect
        messages.success(request, f'Activity "{activity_title}" deleted successfully')
        return redirect("common:oobc_calendar")

    # For non-confirmation POST, redirect to calendar
    return redirect("common:oobc_calendar")


# ===================================
# Phase 3: Enhanced Resource Booking
# ===================================


@login_required
def resource_bookings_feed(request, resource_id):
    """
    Return resource bookings as JSON feed for FullCalendar.
    Shows approved and pending bookings.
    """
    from common.models import CalendarResource, CalendarResourceBooking
    from django.http import JsonResponse

    resource = get_object_or_404(CalendarResource, id=resource_id)

    # Get bookings for this resource
    bookings = CalendarResourceBooking.objects.filter(
        resource=resource, status__in=["approved", "pending"]
    ).select_related("booked_by")

    events = []
    for booking in bookings:
        events.append(
            {
                "id": str(booking.id),
                "title": f"{booking.booked_by.get_full_name()} - {booking.status}",
                "start": booking.start_datetime.isoformat(),
                "end": booking.end_datetime.isoformat(),
                "backgroundColor": (
                    "#10b981" if booking.status == "approved" else "#f59e0b"
                ),
                "borderColor": "#059669" if booking.status == "approved" else "#d97706",
                "extendedProps": {
                    "status": booking.status,
                    "bookedBy": booking.booked_by.get_full_name(),
                    "notes": booking.notes,
                },
            }
        )

    return JsonResponse(events, safe=False)


@login_required
def calendar_check_conflicts(request):
    """
    Real-time conflict checking via HTMX.
    Returns HTML fragment with warnings or success message.
    """
    from common.models import CalendarResource, CalendarResourceBooking
    from django.http import HttpResponse
    from datetime import datetime

    resource_id = request.GET.get("resource_id")
    start = request.GET.get("start_datetime")
    end = request.GET.get("end_datetime")

    if not (resource_id and start and end):
        return HttpResponse("")

    try:
        resource = get_object_or_404(CalendarResource, id=resource_id)

        # Parse datetime strings (ISO format from datetime-local input)
        start_dt = timezone.make_aware(datetime.fromisoformat(start))
        end_dt = timezone.make_aware(datetime.fromisoformat(end))

        # Check for overlapping bookings
        conflicts = CalendarResourceBooking.objects.filter(
            resource=resource,
            status__in=["approved", "pending"],
            start_datetime__lt=end_dt,
            end_datetime__gt=start_dt,
        ).select_related("booked_by")

        if conflicts.exists():
            html = '<div class="border-l-4 border-yellow-500 bg-yellow-50 p-4 rounded">'
            html += '<div class="flex items-center mb-2">'
            html += '<i class="fas fa-exclamation-triangle text-yellow-600 mr-2"></i>'
            html += f'<span class="font-semibold text-yellow-800">{conflicts.count()} conflicting booking(s) found:</span>'
            html += "</div>"
            html += '<ul class="ml-6 list-disc space-y-1">'
            for booking in conflicts:
                status_class = (
                    "bg-green-100 text-green-800"
                    if booking.status == "approved"
                    else "bg-yellow-100 text-yellow-800"
                )
                html += f'<li class="text-sm text-yellow-800">'
                html += f'{booking.start_datetime.strftime("%b %d, %I:%M %p")} - '
                html += f'{booking.end_datetime.strftime("%I:%M %p")} '
                html += f'<span class="px-2 py-1 text-xs rounded {status_class}">'
                html += f"{booking.get_status_display()}"
                html += f"</span>"
                html += f" by {booking.booked_by.get_full_name()}"
                html += f"</li>"
            html += "</ul>"
            html += "</div>"
            return HttpResponse(html)
        else:
            html = '<div class="border-l-4 border-green-500 bg-green-50 p-4 rounded">'
            html += '<div class="flex items-center">'
            html += '<i class="fas fa-check-circle text-green-600 mr-2"></i>'
            html += '<span class="text-green-800 font-medium">Resource available for selected time</span>'
            html += "</div>"
            html += "</div>"
            return HttpResponse(html)
    except Exception as e:
        logger.error(f"Error checking conflicts: {e}")
        return HttpResponse(
            f'<div class="border-l-4 border-red-500 bg-red-50 p-4 rounded text-red-800">Error checking conflicts</div>'
        )


@login_required
def resource_booking_form(request, resource_id):
    """
    Render and process resource booking form with availability calendar.
    """
    from common.models import CalendarResource, CalendarResourceBooking

    resource = get_object_or_404(CalendarResource, id=resource_id)

    if request.method == "POST":
        # Extract form data
        start_datetime = request.POST.get("start_datetime")
        end_datetime = request.POST.get("end_datetime")
        purpose = request.POST.get("purpose")
        is_recurring = request.POST.get("is_recurring") == "on"

        try:
            # Parse datetimes
            start_dt = timezone.make_aware(datetime.fromisoformat(start_datetime))
            end_dt = timezone.make_aware(datetime.fromisoformat(end_datetime))

            # Create booking
            with transaction.atomic():
                booking = CalendarResourceBooking.objects.create(
                    resource=resource,
                    booked_by=request.user,
                    start_datetime=start_dt,
                    end_datetime=end_dt,
                    notes=purpose,
                    status="pending" if resource.requires_approval else "approved",
                )

                # Handle recurring bookings
                if is_recurring:
                    recurrence_pattern = request.POST.get("recurrence_pattern")
                    recurrence_end = request.POST.get("recurrence_end_date")

                    if recurrence_end:
                        end_date = datetime.fromisoformat(recurrence_end).date()
                        current_date = start_dt

                        # Generate recurring instances (limit to 52 weeks)
                        count = 0
                        while current_date.date() < end_date and count < 52:
                            if recurrence_pattern == "daily":
                                current_date += timedelta(days=1)
                            elif recurrence_pattern == "weekly":
                                current_date += timedelta(weeks=1)
                            elif recurrence_pattern == "biweekly":
                                current_date += timedelta(weeks=2)
                            elif recurrence_pattern == "monthly":
                                # Add roughly 30 days
                                current_date += timedelta(days=30)

                            if current_date.date() <= end_date:
                                new_end = current_date + (end_dt - start_dt)
                                CalendarResourceBooking.objects.create(
                                    resource=resource,
                                    booked_by=request.user,
                                    start_datetime=current_date,
                                    end_datetime=new_end,
                                    notes=f"{purpose} (Recurring)",
                                    status=(
                                        "pending"
                                        if resource.requires_approval
                                        else "approved"
                                    ),
                                )
                                count += 1

            messages.success(
                request,
                f"Resource booking submitted successfully. Status: {'Pending Approval' if resource.requires_approval else 'Approved'}",
            )
            return redirect("common:coordination_home")

        except Exception as e:
            logger.error(f"Error creating booking: {e}")
            messages.error(request, f"Error creating booking: {str(e)}")

    context = {
        "resource": resource,
        "return_url": reverse("common:coordination_home"),
        "page_title": f"Book {resource.name}",
        "page_heading": f"Book {resource.name}",
    }
    return render(request, "coordination/resource_booking_form.html", context)


# ===================================
# Phase 3: Event Attendance Tracking
# ===================================


@login_required
def event_attendance_tracker(request, event_id):
    """
    Main attendance tracking interface with QR scanner and live updates.
    """
    from .models import EventAttendance, EventParticipant

    work_item = get_object_or_404(WorkItem, id=event_id, work_type="activity")

    context = {
        "event": work_item,  # Keep 'event' for template compatibility
        "return_url": reverse("common:coordination_events"),
        "page_title": f"Attendance - {work_item.title}",
        "page_heading": f"Attendance Tracker: {work_item.title}",
    }
    return render(request, "coordination/event_attendance_tracker.html", context)


@login_required
def event_attendance_count(request, event_id):
    """
    Return HTML fragment with live attendance counter.
    Polled every 10 seconds by HTMX.
    """
    from .models import EventAttendance
    from django.http import HttpResponse

    work_item = get_object_or_404(WorkItem, id=event_id, work_type="activity")
    event = work_item  # For backward compatibility with variable names below

    # Count checked-in participants
    checked_in = EventAttendance.objects.filter(
        event=event, checked_in_at__isnull=False
    ).count()

    # Count expected participants
    expected = event.participants.count()
    percentage = (checked_in / expected * 100) if expected > 0 else 0

    # Calculate circumference for SVG circle
    circumference = 2 * 3.14159 * 45  # radius = 45
    offset = circumference - (percentage / 100 * circumference)

    # Generate HTML
    html = f"""
    <div class="flex flex-col items-center">
        <div class="relative w-48 h-48 mb-4">
            <!-- SVG Circular Progress -->
            <svg viewBox="0 0 100 100" class="transform -rotate-90 w-full h-full">
                <circle cx="50" cy="50" r="45" fill="none" stroke="#e5e7eb" stroke-width="8"/>
                <circle cx="50" cy="50" r="45" fill="none" stroke="#10b981" stroke-width="8"
                        stroke-dasharray="{circumference}"
                        stroke-dashoffset="{offset}"
                        stroke-linecap="round"
                        class="transition-all duration-500"/>
            </svg>

            <!-- Counter Text (centered) -->
            <div class="absolute inset-0 flex flex-col items-center justify-center">
                <span class="text-5xl font-bold text-gray-900">{checked_in}</span>
                <span class="text-xl text-gray-600">/ {expected}</span>
            </div>
        </div>

        <p class="text-center text-lg">
            <strong class="text-2xl text-emerald-600">{percentage:.0f}%</strong>
            <span class="text-gray-600 ml-2">attendance</span>
        </p>

        <p class="text-sm text-gray-500 mt-2">
            Last updated: {timezone.now().strftime("%I:%M:%S %p")}
        </p>
    </div>
    """

    return HttpResponse(html)


@login_required
def event_participant_list(request, event_id):
    """
    Return HTML fragment with participant list.
    Shows check-in status for each participant.
    """
    from .models import EventAttendance
    from django.http import HttpResponse

    work_item = get_object_or_404(WorkItem, id=event_id, work_type="activity")
    event = work_item  # For backward compatibility with variable names below
    participants = event.participants.all().select_related("user", "contact")

    html = '<div class="space-y-2">'

    for participant in participants:
        # Check if participant has checked in
        attendance = EventAttendance.objects.filter(
            event=event, participant=participant
        ).first()

        checked_in = attendance and attendance.checked_in_at

        html += f"""
        <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
             data-participant-id="{participant.id}">
            <div class="flex items-center space-x-3">
                <div class="flex-shrink-0">
                    {f'<i class="fas fa-check-circle text-green-500 text-xl"></i>' if checked_in else '<i class="far fa-clock text-gray-400 text-xl"></i>'}
                </div>
                <div>
                    <p class="font-semibold text-gray-900">{participant.participant_name}</p>
                    <p class="text-sm text-gray-600">{participant.participant_email or 'No email'}</p>
                    {f'<p class="text-xs text-green-600 mt-1"><i class="fas fa-check mr-1"></i>Checked in at {attendance.checked_in_at.strftime("%I:%M %p")}</p>' if checked_in else ''}
                </div>
            </div>

            {'' if checked_in else f'''
            <button class="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors text-sm font-medium"
                    hx-post="{reverse('common:coordination_event_check_in', kwargs={'event_id': event.id})}"
                    hx-vals='{{"participant_id": "{participant.id}", "method": "manual"}}'
                    hx-target="[data-participant-id='{participant.id}']"
                    hx-swap="outerHTML"
                    hx-headers='{{"X-CSRFToken": "{request.META.get('CSRF_COOKIE', '')}"}}'>
                <i class="fas fa-user-check mr-1"></i>Check In
            </button>
            '''}
        </div>
        """

    if not participants.exists():
        html += '<p class="text-center text-gray-500 py-8">No participants registered yet.</p>'

    html += "</div>"

    return HttpResponse(html)


@login_required
@require_POST
def event_check_in(request, event_id):
    """
    Handle participant check-in (manual or QR code).
    Returns updated participant row HTML.
    """
    from .models import EventAttendance, EventParticipant
    from django.http import HttpResponse

    work_item = get_object_or_404(WorkItem, id=event_id, work_type="activity")
    event = work_item  # For backward compatibility with variable names below
    participant_id = request.POST.get("participant_id")
    method = request.POST.get("method", "manual")

    try:
        participant = get_object_or_404(
            EventParticipant, id=participant_id, event=event
        )

        # Create or update attendance record
        attendance, created = EventAttendance.objects.get_or_create(
            event=event,
            participant=participant,
            defaults={
                "checked_in_at": timezone.now(),
                "check_in_method": method,
            },
        )

        if not created and not attendance.checked_in_at:
            attendance.checked_in_at = timezone.now()
            attendance.check_in_method = method
            attendance.save()

        # Return updated participant row HTML
        html = f"""
        <div class="flex items-center justify-between p-4 bg-green-50 rounded-lg border-l-4 border-green-500"
             data-participant-id="{participant.id}">
            <div class="flex items-center space-x-3">
                <div class="flex-shrink-0">
                    <i class="fas fa-check-circle text-green-500 text-xl"></i>
                </div>
                <div>
                    <p class="font-semibold text-gray-900">{participant.participant_name}</p>
                    <p class="text-sm text-gray-600">{participant.participant_email or 'No email'}</p>
                    <p class="text-xs text-green-600 mt-1">
                        <i class="fas fa-check mr-1"></i>Checked in at {attendance.checked_in_at.strftime("%I:%M %p")}
                        via {method.replace('_', ' ').title()}
                    </p>
                </div>
            </div>
            <div class="text-green-600">
                <i class="fas fa-check text-2xl"></i>
            </div>
        </div>
        """

        return HttpResponse(html)

    except Exception as e:
        logger.error(f"Error checking in participant: {e}")
        return HttpResponse(
            f'<div class="p-4 bg-red-50 rounded-lg text-red-800">Error: {str(e)}</div>',
            status=400,
        )


@login_required
def moa_calendar_feed(request, organization_id):
    """
    Calendar feed endpoint for a specific MOA.

    Returns JSON calendar events containing all work items from all PPAs
    implemented by this MOA (filtered by implementing_moa for isolation).

    Args:
        organization_id: UUID of the Organization (MOA)

    Returns:
        JsonResponse with calendar events in FullCalendar format
    """
    from common.work_item_model import WorkItem
    from django.http import JsonResponse
    from datetime import datetime

    try:
        organization = Organization.objects.get(id=organization_id)
    except Organization.DoesNotExist:
        return JsonResponse({'error': 'Organization not found'}, status=404)

    # Get all work items for this MOA's PPAs
    work_items = WorkItem.objects.filter(
        ppa_category='moa_ppa',
        implementing_moa=organization,
        is_calendar_visible=True
    ).select_related(
        'related_ppa',
        'created_by'
    ).prefetch_related(
        'assignees',
        'teams'
    )

    # Build calendar events
    events = []
    for item in work_items:
        # Skip items without dates
        if not item.start_date:
            continue

        # Determine color based on work type
        color_map = {
            'project': '#3b82f6',  # Blue
            'activity': '#10b981',  # Emerald
            'task': '#8b5cf6',     # Purple
            'subtask': '#f59e0b',  # Amber
        }

        event = {
            'id': str(item.id),
            'title': item.title,
            'start': item.start_date.isoformat(),
            'end': (item.due_date or item.start_date).isoformat(),
            'allDay': not (item.start_time and item.end_time),
            'backgroundColor': color_map.get(item.work_type, '#6b7280'),
            'borderColor': color_map.get(item.work_type, '#6b7280'),
            'textColor': '#ffffff',
            'extendedProps': {
                'work_item_id': str(item.id),
                'work_type': item.work_type,
                'status': item.status,
                'priority': item.priority,
                'progress': item.progress,
                'description': item.description or '',
                'ppa_title': item.related_ppa.title if item.related_ppa else '',
            }
        }

        # Add time if available
        if item.start_time:
            start_datetime = datetime.combine(item.start_date, item.start_time)
            event['start'] = start_datetime.isoformat()

        if item.end_time and item.due_date:
            end_datetime = datetime.combine(item.due_date, item.end_time)
            event['end'] = end_datetime.isoformat()

        events.append(event)

    return JsonResponse(events, safe=False)
