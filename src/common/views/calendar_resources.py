"""Views for calendar resource and booking management."""

import json
import uuid
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from common.forms import (
    CalendarResourceForm,
    CalendarResourceBookingForm,
    StaffLeaveForm,
)
from common.models import (
    CalendarResource,
    CalendarResourceBooking,
    StaffLeave,
)


@login_required
def resource_list(request):
    """Display all calendar resources with filtering and search."""

    # Get filter parameters
    resource_type = request.GET.get("type")
    status_filter = request.GET.get("status")
    search_query = request.GET.get("q")

    # Base queryset
    resources = CalendarResource.objects.all()

    # Apply filters
    if resource_type:
        resources = resources.filter(resource_type=resource_type)

    if status_filter:
        status_filter = status_filter.lower()
        if status_filter == "available":
            resources = resources.filter(is_available=True)
        elif status_filter in {"unavailable", "inactive"}:
            resources = resources.filter(is_available=False)

    if search_query:
        resources = resources.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(location__icontains=search_query)
        )

    # Order by type and name
    resources = resources.order_by("resource_type", "name")

    # Get stats
    stats = {
        "total": CalendarResource.objects.count(),
        "available": CalendarResource.objects.filter(is_available=True).count(),
        "unavailable": CalendarResource.objects.filter(is_available=False).count(),
        "vehicles": CalendarResource.objects.filter(
            resource_type=CalendarResource.RESOURCE_VEHICLE
        ).count(),
        "equipment": CalendarResource.objects.filter(
            resource_type=CalendarResource.RESOURCE_EQUIPMENT
        ).count(),
        "rooms": CalendarResource.objects.filter(
            resource_type=CalendarResource.RESOURCE_ROOM
        ).count(),
        "facilitators": CalendarResource.objects.filter(
            resource_type=CalendarResource.RESOURCE_FACILITATOR
        ).count(),
    }

    context = {
        "resources": resources,
        "stats": stats,
        "resource_type_filter": resource_type,
        "status_filter": status_filter,
        "search_query": search_query or "",
        "resource_types": CalendarResource.RESOURCE_TYPE_CHOICES,
        "statuses": [
            ("available", "Available"),
            ("unavailable", "Unavailable"),
        ],
    }

    return render(request, "common/calendar/resource_list.html", context)


@login_required
def resource_create(request):
    """Create a new calendar resource."""

    if not request.user.has_perm("common.add_calendarresource"):
        raise PermissionDenied

    if request.method == "POST":
        form = CalendarResourceForm(request.POST)
        if form.is_valid():
            resource = form.save()
            messages.success(
                request, f"Resource '{resource.name}' created successfully."
            )
            return redirect("common:calendar_resource_list")
        messages.error(request, "Please correct the errors below.")
    else:
        form = CalendarResourceForm()

    context = {
        "form": form,
        "page_title": "Add Calendar Resource",
        "page_heading": "Add New Calendar Resource",
        "submit_label": "Create Resource",
        "return_url": reverse("common:calendar_resource_list"),
    }

    return render(request, "common/calendar/resource_form.html", context)


@login_required
def resource_detail(request, resource_id):
    """View resource details and booking history."""

    resource = get_object_or_404(CalendarResource, pk=resource_id)

    # Get upcoming bookings
    now = timezone.now()
    upcoming_bookings = (
        CalendarResourceBooking.objects.filter(
            resource=resource,
            start_datetime__gte=now,
            status__in=[
                CalendarResourceBooking.STATUS_PENDING,
                CalendarResourceBooking.STATUS_APPROVED,
            ],
        )
        .select_related("booked_by", "approved_by")
        .order_by("start_datetime")[:10]
    )

    # Get recent bookings
    past_bookings = (
        CalendarResourceBooking.objects.filter(
            resource=resource,
            end_datetime__lt=now,
        )
        .select_related("booked_by", "approved_by")
        .order_by("-end_datetime")[:10]
    )

    # Calculate utilization (last 30 days)
    thirty_days_ago = now - timedelta(days=30)
    total_bookings = CalendarResourceBooking.objects.filter(
        resource=resource,
        start_datetime__gte=thirty_days_ago,
        status=CalendarResourceBooking.STATUS_APPROVED,
    ).count()

    context = {
        "resource": resource,
        "upcoming_bookings": upcoming_bookings,
        "past_bookings": past_bookings,
        "total_bookings_30d": total_bookings,
        "return_url": reverse("common:calendar_resource_list"),
    }

    return render(request, "common/calendar/resource_detail.html", context)


@login_required
def resource_edit(request, resource_id):
    """Edit an existing calendar resource."""

    if not request.user.has_perm("common.change_calendarresource"):
        raise PermissionDenied

    resource = get_object_or_404(CalendarResource, pk=resource_id)

    if request.method == "POST":
        form = CalendarResourceForm(request.POST, instance=resource)
        if form.is_valid():
            resource = form.save()
            messages.success(
                request, f"Resource '{resource.name}' updated successfully."
            )
            return redirect("common:calendar_resource_detail", resource_id=resource.pk)
        messages.error(request, "Please correct the errors below.")
    else:
        form = CalendarResourceForm(instance=resource)

    context = {
        "form": form,
        "resource": resource,
        "page_title": "Edit Resource",
        "page_heading": f"Edit {resource.name}",
        "submit_label": "Save Changes",
        "return_url": reverse("common:calendar_resource_detail", args=[resource.pk]),
    }

    return render(request, "common/calendar/resource_form.html", context)


@login_required
@require_POST
def resource_delete(request, resource_id):
    """Delete a calendar resource."""

    if not request.user.has_perm("common.delete_calendarresource"):
        raise PermissionDenied

    resource = get_object_or_404(CalendarResource, pk=resource_id)

    # Check for active bookings
    active_bookings = CalendarResourceBooking.objects.filter(
        resource=resource,
        start_datetime__gte=timezone.now(),
        status__in=[
            CalendarResourceBooking.STATUS_PENDING,
            CalendarResourceBooking.STATUS_APPROVED,
        ],
    ).count()

    if active_bookings > 0:
        messages.error(
            request,
            f"Cannot delete '{resource.name}' - it has {active_bookings} active bookings.",
        )
        return redirect("common:calendar_resource_detail", resource_id=resource.pk)

    resource_name = resource.name
    resource.delete()

    messages.success(request, f"Resource '{resource_name}' deleted successfully.")
    return redirect("common:calendar_resource_list")


@login_required
def resource_calendar(request, resource_id):
    """Calendar view showing resource availability and bookings."""

    resource = get_object_or_404(CalendarResource, pk=resource_id)

    # Get all bookings for this resource
    bookings = CalendarResourceBooking.objects.filter(resource=resource).select_related(
        "booked_by", "approved_by"
    )

    # Build calendar entries
    calendar_entries = []
    for booking in bookings:
        # Color based on status
        if booking.status == CalendarResourceBooking.STATUS_APPROVED:
            bg_color = "#10b981"  # green
        elif booking.status == CalendarResourceBooking.STATUS_PENDING:
            bg_color = "#f59e0b"  # amber
        elif booking.status == CalendarResourceBooking.STATUS_REJECTED:
            bg_color = "#ef4444"  # red
        else:  # cancelled
            bg_color = "#6b7280"  # gray

        calendar_entries.append(
            {
                "id": str(booking.pk),
                "title": f"{booking.booked_by.get_full_name()} - {booking.notes[:30] if booking.notes else 'Booking'}",
                "start": booking.start_datetime.isoformat(),
                "end": booking.end_datetime.isoformat(),
                "backgroundColor": bg_color,
                "extendedProps": {
                    "status": booking.status,
                    "booked_by": booking.booked_by.get_full_name(),
                    "notes": booking.notes,
                },
            }
        )

    context = {
        "resource": resource,
        "calendar_events_json": json.dumps(calendar_entries),
        "return_url": reverse("common:calendar_resource_detail", args=[resource.pk]),
    }

    return render(request, "common/calendar/resource_calendar.html", context)


@login_required
def booking_request(request, resource_id=None):
    """Request a resource booking."""

    if not request.user.has_perm("common.add_calendarresourcebooking"):
        raise PermissionDenied

    resource = None
    if resource_id:
        resource = get_object_or_404(CalendarResource, pk=resource_id)

    if request.method == "POST":
        form = CalendarResourceBookingForm(request.POST, user=request.user)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.booked_by = request.user
            if not booking.object_id:
                booking.object_id = uuid.uuid4()

            # Auto-approve if resource doesn't require approval
            selected_resource = form.cleaned_data["resource"]
            if form.event:
                booking.content_type = ContentType.objects.get_for_model(form.event)
                booking.object_id = form.event.pk
            else:
                booking.content_type = ContentType.objects.get_for_model(
                    CalendarResource
                )
                booking.object_id = selected_resource.pk
            if not getattr(selected_resource, "requires_approval", False):
                booking.status = CalendarResourceBooking.STATUS_APPROVED
                booking.approved_by = request.user

            booking.save()

            if booking.status == CalendarResourceBooking.STATUS_APPROVED:
                messages.success(
                    request, f"Resource '{selected_resource.name}' booked successfully."
                )
            else:
                messages.success(
                    request,
                    f"Booking request submitted for '{selected_resource.name}'. "
                    "Awaiting approval.",
                )

            return redirect(
                "common:calendar_resource_detail", resource_id=selected_resource.pk
            )

        messages.error(request, "Please correct the errors below.")
    else:
        initial = {}
        if resource:
            initial["resource"] = resource.pk
        form = CalendarResourceBookingForm(user=request.user, initial=initial)

    context = {
        "form": form,
        "resource": resource,
        "page_title": "Request Resource Booking",
        "page_heading": (
            f"Book {resource.name}" if resource else "Request Resource Booking"
        ),
        "submit_label": "Submit Booking Request",
        "return_url": reverse("common:calendar_resource_list"),
    }

    return render(request, "common/calendar/booking_request_form.html", context)


@login_required
def booking_approve(request, booking_id):
    """Approve or reject a booking request."""

    if not request.user.has_perm("common.change_calendarresourcebooking"):
        raise PermissionDenied

    booking = get_object_or_404(CalendarResourceBooking, pk=booking_id)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "approve":
            # Check for conflicts again
            overlapping = CalendarResourceBooking.objects.filter(
                resource=booking.resource,
                start_datetime__lt=booking.end_datetime,
                end_datetime__gt=booking.start_datetime,
                status=CalendarResourceBooking.STATUS_APPROVED,
            ).exclude(pk=booking.pk)

            if overlapping.exists():
                messages.error(
                    request,
                    "Cannot approve - resource is already booked during this time.",
                )
                return redirect("common:calendar_booking_detail", booking_id=booking.pk)

            booking.status = CalendarResourceBooking.STATUS_APPROVED
            booking.approved_by = request.user
            booking.save()

            messages.success(
                request, f"Booking approved for {booking.booked_by.get_full_name()}."
            )

        elif action == "reject":
            booking.status = CalendarResourceBooking.STATUS_REJECTED
            booking.approved_by = request.user
            booking.save()

            messages.success(request, "Booking request rejected.")

        return redirect(
            "common:calendar_resource_detail", resource_id=booking.resource.pk
        )

    context = {
        "booking": booking,
        "return_url": reverse(
            "common:calendar_resource_detail", args=[booking.resource.pk]
        ),
    }

    return render(request, "common/calendar/booking_approve.html", context)


@login_required
def booking_list(request):
    """List all bookings with filtering."""

    # Get filters
    status_filter = request.GET.get("status")
    resource_filter = request.GET.get("resource")
    user_bookings = request.GET.get("my_bookings") == "true"

    # Base queryset
    bookings = CalendarResourceBooking.objects.select_related(
        "resource", "booked_by", "approved_by"
    )

    # Apply filters
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    if resource_filter:
        bookings = bookings.filter(resource_id=resource_filter)

    if user_bookings:
        bookings = bookings.filter(booked_by=request.user)

    # Order by date
    bookings = bookings.order_by("-start_datetime")

    context = {
        "bookings": bookings,
        "status_filter": status_filter,
        "resource_filter": resource_filter,
        "user_bookings": user_bookings,
        "statuses": CalendarResourceBooking.STATUS_CHOICES,
        "resources": CalendarResource.objects.all().order_by("name"),
    }

    return render(request, "common/calendar/booking_list.html", context)


@login_required
def staff_leave_request(request):
    """Submit a staff leave request."""

    if request.method == "POST":
        form = StaffLeaveForm(request.POST, user=request.user)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.staff = request.user
            leave.save()

            messages.success(
                request, "Leave request submitted successfully. Awaiting approval."
            )
            return redirect("common:staff_leave_list")

        messages.error(request, "Please correct the errors below.")
    else:
        form = StaffLeaveForm(user=request.user)

    context = {
        "form": form,
        "page_title": "Request Leave",
        "page_heading": "Submit Leave Request",
        "submit_label": "Submit Request",
        "return_url": reverse("common:staff_leave_list"),
    }

    return render(request, "common/calendar/leave_request_form.html", context)


@login_required
def staff_leave_list(request):
    """List all leave requests."""

    # Show user's own leaves by default, or all if admin
    if request.user.is_staff and request.GET.get("all") == "true":
        leaves = StaffLeave.objects.all()
    else:
        leaves = StaffLeave.objects.filter(staff=request.user)

    leaves = leaves.select_related("staff", "approved_by").order_by("-start_date")

    context = {
        "leaves": leaves,
        "can_view_all": request.user.is_staff,
        "viewing_all": request.GET.get("all") == "true",
    }

    return render(request, "common/calendar/leave_list.html", context)


@login_required
@require_POST
def staff_leave_approve(request, leave_id):
    """Approve or reject a leave request."""

    if not request.user.has_perm("common.change_staffleave"):
        raise PermissionDenied

    leave = get_object_or_404(StaffLeave, pk=leave_id)
    action = request.POST.get("action")
    if action not in {"approve", "reject"}:
        status_value = (request.POST.get("status") or "").lower()
        if status_value == StaffLeave.STATUS_APPROVED:
            action = "approve"
        elif status_value == StaffLeave.STATUS_REJECTED:
            action = "reject"

    if action == "approve":
        leave.status = StaffLeave.STATUS_APPROVED
        leave.approved_by = request.user
        leave.save()
        messages.success(request, f"Leave approved for {leave.staff.get_full_name()}.")
    elif action == "reject":
        leave.status = StaffLeave.STATUS_REJECTED
        leave.approved_by = request.user
        leave.save()
        messages.success(request, "Leave request rejected.")

    return redirect("common:staff_leave_list")
