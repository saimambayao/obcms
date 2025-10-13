"""MOA staff approval views."""

import json
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView

from ..models import User
from ..security_logging import log_security_event
from ..utils.htmx_responses import htmx_403_response
from ..utils.permissions import (
    can_approve_moa_users,
    get_pending_first_level_count,
    get_pending_moa_count,
    is_moa_focal_approver,
)


class MOAApprovalListView(ListView):
    """
    Dashboard for reviewing and approving MOA staff registrations.
    Only accessible to authorized approvers.
    """

    model = User
    template_name = "common/approval/moa_approval_list.html"
    context_object_name = "pending_users"
    paginate_by = 20

    def get_template_names(self):
        """Return partial template for HTMX requests, full template otherwise."""
        if self.request.headers.get('HX-Request'):
            return ["common/approval/moa_approval_list_partial.html"]
        return [self.template_name]

    def dispatch(self, request, *args, **kwargs):
        """Check if user has approval permissions."""
        self.is_level_two_approver = can_approve_moa_users(request.user)
        self.is_level_one_approver = is_moa_focal_approver(request.user)
        self.moa_organization = getattr(request.user, "moa_organization", None)
        if not (self.is_level_two_approver or self.is_level_one_approver):
            messages.error(
                request,
                "You do not have permission to approve MOA staff registrations."
            )
            raise PermissionDenied("User lacks required permission to approve MOA staff registrations")

        self.approval_stage = self._determine_stage(request)

        return super().dispatch(request, *args, **kwargs)

    def _determine_stage(self, request):
        """Resolve which approval stage the current session should manage."""
        stage_param = request.GET.get("stage")
        if stage_param == "focal" and self.is_level_one_approver:
            return "focal"
        if stage_param == "final" and self.is_level_two_approver:
            return "final"

        if self.is_level_two_approver:
            return "final"
        return "focal"

    def _stage_url(self, stage):
        """Generate a URL that switches the approval stage."""
        query = self.request.GET.copy()
        query["stage"] = stage
        encoded = query.urlencode()
        return f"{self.request.path}?{encoded}" if encoded else f"{self.request.path}?stage={stage}"

    def get_queryset(self):
        """Get all pending MOA staff registrations."""
        base_queryset = User.objects.filter(
            user_type__in=['bmoa', 'lgu', 'nga'],
            is_active=True,
        ).select_related('approved_by', 'moa_first_level_approved_by', 'moa_organization')

        if self.approval_stage == "focal":
            if not self.moa_organization:
                return base_queryset.none()
            return (
                base_queryset.filter(
                    moa_organization=self.moa_organization,
                    moa_first_level_approved=False,
                    is_approved=False,
                )
                .exclude(id=self.request.user.id)
                .order_by('-date_joined')
            )

        # Final stage (OOBC staff, superusers, coordinators)
        return (
            base_queryset.filter(
                moa_first_level_approved=True,
                is_approved=False,
            )
            .order_by('-moa_first_level_approved_at', '-date_joined')
        )

    def get_context_data(self, **kwargs):
        """Add approval statistics to context."""
        context = super().get_context_data(**kwargs)

        if self.approval_stage == "focal":
            org_users = User.objects.filter(
                moa_organization=self.moa_organization,
                user_type__in=['bmoa', 'lgu', 'nga'],
                is_active=True,
            )
            pending_count = get_pending_first_level_count(self.moa_organization)
            context['stats'] = {
                'pending_count': pending_count,
                'approved_count': org_users.filter(
                    moa_first_level_approved=True,
                    is_approved=False,
                ).count(),
                'total_count': org_users.count(),
            }
            context['stage_title'] = "Level 1 • Focal Person Endorsement"
            context['approve_button_label'] = "Endorse to OOBC"
            context['approve_button_icon'] = "fas fa-share-square"
            context['approve_url_name'] = "common:approve_moa_user_stage_one"
            context['pending_label'] = "Awaiting Focal Review"
            context['show_endorsed_column'] = False
        else:
            all_moa_users = User.objects.filter(
                user_type__in=['bmoa', 'lgu', 'nga'],
                is_active=True,
            )
            context['stats'] = {
                'pending_count': get_pending_moa_count(),
                'approved_count': all_moa_users.filter(is_approved=True).count(),
                'total_count': all_moa_users.count(),
            }
            context['stage_title'] = "Level 2 • OOBC Coordinator Approval"
            context['approve_button_label'] = "Finalize Approval"
            context['approve_button_icon'] = "fas fa-check"
            context['approve_url_name'] = "common:approve_moa_user"
            context['pending_label'] = "Awaiting OOBC Approval"
            context['show_endorsed_column'] = True

        context['approval_stage'] = self.approval_stage
        context['stage_options'] = self._build_stage_options()

        return context

    def _build_stage_options(self):
        options = []
        if self.is_level_one_approver:
            options.append(
                {
                    "stage": "focal",
                    "label": "Level 1 (Focal)",
                    "active": self.approval_stage == "focal",
                    "url": self._stage_url("focal"),
                }
            )
        if self.is_level_two_approver:
            options.append(
                {
                    "stage": "final",
                    "label": "Level 2 (OOBC)",
                    "active": self.approval_stage == "final",
                    "url": self._stage_url("final"),
                }
            )
        return options


def _redirect_to_approval_list(request, stage=None):
    """Redirect back to the approvals dashboard, preserving the active stage."""
    target_url = reverse('common:moa_approval_list')
    stage = stage or request.GET.get('stage')
    if stage:
        return redirect(f"{target_url}?stage={stage}")
    return redirect(target_url)


@login_required
def approve_moa_user_stage_one(request, user_id):
    """
    Provide first-level approval by a MOA/NGA/LGU focal person.
    """
    if not is_moa_focal_approver(request.user):
        return htmx_403_response(
            message="You do not have permission to endorse users for OOBC approval."
        )

    user_to_endorse = get_object_or_404(
        User,
        id=user_id,
        user_type__in=['bmoa', 'lgu', 'nga'],
        is_active=True,
        is_approved=False,
        moa_first_level_approved=False,
    )

    if (
        not request.user.moa_organization
        or request.user.moa_organization_id != user_to_endorse.moa_organization_id
    ):
        return htmx_403_response(
            message="You can only endorse users from your assigned organization."
        )

    user_to_endorse.moa_first_level_approved = True
    user_to_endorse.moa_first_level_approved_by = request.user
    user_to_endorse.moa_first_level_approved_at = timezone.now()
    user_to_endorse.save(
        update_fields=[
            "moa_first_level_approved",
            "moa_first_level_approved_by",
            "moa_first_level_approved_at",
        ]
    )

    log_security_event(
        request,
        event_type="MOA User Endorsed",
        details=(
            f"{request.user.username} endorsed MOA staff: "
            f"{user_to_endorse.username} ({user_to_endorse.get_user_type_display()}) "
            f"- {user_to_endorse.organization}"
        ),
        severity="INFO",
    )

    # Notify the applicant of the endorsement
    try:
        send_mail(
            subject="OBCMS Registration Endorsed",
            message=(
                f"Dear {user_to_endorse.get_full_name()},\n\n"
                f"Your OBCMS registration has been endorsed by "
                f"{request.user.get_full_name() or request.user.username}. "
                f"Our OOBC coordinators will now complete the final account review.\n\n"
                f"You will receive another email once the OOBC approval is complete.\n\n"
                f"Best regards,\n"
                f"OOBC Management System"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_to_endorse.email],
            fail_silently=True,
        )
    except Exception as exc:
        log_security_event(
            request,
            event_type="Email Error",
            details=(
                f"Failed to send endorsement email to {user_to_endorse.email}: {str(exc)}"
            ),
            severity="WARNING",
        )

    if request.headers.get("HX-Request"):
        return HttpResponse(
            status=200,
            headers={
                "HX-Trigger": json.dumps(
                    {
                        "user-approved": {"id": user_id},
                        "user-endorsed": {"id": user_id},
                        "show-toast": f"Endorsed {user_to_endorse.get_full_name()}",
                        "refresh-list": True,
                    }
                )
            },
        )

    messages.success(
        request,
        f"Successfully endorsed {user_to_endorse.get_full_name()} for OOBC approval.",
    )
    return _redirect_to_approval_list(request, stage="focal")


@login_required
def approve_moa_user(request, user_id):
    """
    Approve a MOA staff registration.
    Sends email notification to the user.
    """
    # Check permissions
    if not can_approve_moa_users(request.user):
        return htmx_403_response(
            message="You do not have permission to approve users."
        )

    # Get user to approve
    user_to_approve = get_object_or_404(
        User,
        id=user_id,
        user_type__in=['bmoa', 'lgu', 'nga'],
        is_approved=False,
    )

    override = (
        request.GET.get("override") == "1"
        or request.POST.get("override") == "1"
    )

    if not user_to_approve.moa_first_level_approved and not override:
        risk_url = reverse("common:moa_approval_risk_prompt", args=[user_id])
        stage = request.GET.get("stage") or request.POST.get("stage") or "final"
        if request.headers.get("HX-Request"):
            return HttpResponse(
                status=200,
                headers={
                    "HX-Redirect": f"{risk_url}?stage={stage}",
                },
            )
        return redirect(f"{risk_url}?stage={stage}")

    # Approve user
    user_to_approve.is_approved = True
    user_to_approve.approved_by = request.user
    user_to_approve.approved_at = timezone.now()
    user_to_approve.save()

    # Log approval
    log_security_event(
        request,
        event_type="MOA User Approved",
        details=(
            f"{request.user.username} approved MOA staff: "
            f"{user_to_approve.username} ({user_to_approve.get_user_type_display()}) "
            f"- {user_to_approve.organization}"
        ),
        severity="INFO"
    )

    # Send approval email to user
    try:
        login_url = request.build_absolute_uri(reverse('common:login'))

        send_mail(
            subject="OBCMS Account Approved - Welcome!",
            message=(
                f"Dear {user_to_approve.get_full_name()},\n\n"
                f"Great news! Your OBCMS account has been approved by {request.user.get_full_name()}.\n\n"
                f"You can now log in to the system with your credentials:\n"
                f"Username: {user_to_approve.username}\n"
                f"Login URL: {login_url}\n\n"
                f"If you forgot your password, you can reset it using the 'Forgot Password' link on the login page.\n\n"
                f"Welcome to the OBCMS platform! We're excited to have you on board.\n\n"
                f"Best regards,\n"
                f"OOBC Management System"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_to_approve.email],
            fail_silently=True,
        )
    except Exception as e:
        # Log email error but don't prevent approval
        log_security_event(
            request,
            event_type="Email Error",
            details=f"Failed to send approval email to {user_to_approve.email}: {str(e)}",
            severity="WARNING"
        )

    # Return HTMX response
    if request.headers.get('HX-Request'):
        return HttpResponse(
            status=200,
            headers={
                'HX-Trigger': json.dumps({
                    'user-approved': {'id': user_id},
                    'show-toast': f'Approved {user_to_approve.get_full_name()}',
                    'refresh-list': True
                })
            }
        )

    # Fallback for non-HTMX requests
    messages.success(
        request,
        f"Successfully approved {user_to_approve.get_full_name()}"
    )
    return _redirect_to_approval_list(request, stage="final")


@login_required
def reject_moa_user(request, user_id):
    """
    Reject a MOA staff registration.
    Deactivates the account and sends notification email.
    """
    # Check permissions
    is_final_approver = can_approve_moa_users(request.user)
    is_focal_approver = is_moa_focal_approver(request.user)
    if not (is_final_approver or is_focal_approver):
        return htmx_403_response(
            message="You do not have permission to reject users."
        )

    # Get user to reject
    user_to_reject = get_object_or_404(
        User,
        id=user_id,
        user_type__in=['bmoa', 'lgu', 'nga'],
        is_approved=False
    )

    if (
        is_focal_approver
        and not is_final_approver
        and (
            not request.user.moa_organization
            or request.user.moa_organization_id != user_to_reject.moa_organization_id
        )
    ):
        return htmx_403_response(
            message="You can only reject registrations from your organization."
        )

    # Deactivate user (soft delete)
    user_to_reject.is_active = False
    user_to_reject.moa_first_level_approved = False
    user_to_reject.moa_first_level_approved_by = None
    user_to_reject.moa_first_level_approved_at = None
    user_to_reject.approved_by = None
    user_to_reject.approved_at = None
    user_to_reject.is_approved = False
    user_to_reject.save()

    # Log rejection
    log_security_event(
        request,
        event_type="MOA User Rejected",
        details=(
            f"{request.user.username} rejected MOA staff registration: "
            f"{user_to_reject.username} ({user_to_reject.get_user_type_display()}) "
            f"- {user_to_reject.organization}"
        ),
        severity="INFO"
    )

    # Send rejection email
    try:
        send_mail(
            subject="OBCMS Registration Update",
            message=(
                f"Dear {user_to_reject.get_full_name()},\n\n"
                f"Thank you for your interest in the OBCMS platform.\n\n"
                f"After reviewing your registration, we are unable to approve your account at this time. "
                f"This may be due to incomplete information or verification requirements.\n\n"
                f"If you believe this is an error or have questions, please contact us at:\n"
                f"{settings.DEFAULT_FROM_EMAIL}\n\n"
                f"Best regards,\n"
                f"OOBC Management System"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_to_reject.email],
            fail_silently=True,
        )
    except Exception as e:
        # Log email error but don't prevent rejection
        log_security_event(
            request,
            event_type="Email Error",
            details=f"Failed to send rejection email to {user_to_reject.email}: {str(e)}",
            severity="WARNING"
        )

    # Return HTMX response
    if request.headers.get('HX-Request'):
        return HttpResponse(
            status=200,
            headers={
                'HX-Trigger': json.dumps({
                    'user-rejected': {'id': user_id},
                    'show-toast': f'Rejected {user_to_reject.get_full_name()}',
                    'refresh-list': True
                })
            }
        )

    # Fallback for non-HTMX requests
    messages.warning(
        request,
        f"Rejected registration for {user_to_reject.get_full_name()}"
    )
    preferred_stage = 'final' if is_final_approver else 'focal'
    return _redirect_to_approval_list(request, stage=preferred_stage)


@login_required
def moa_approval_risk_prompt(request, user_id):
    """
    Display a risk confirmation screen for OOBC approvers when bypassing focal endorsement.
    """
    if not can_approve_moa_users(request.user):
        return htmx_403_response(
            message="You do not have permission to finalize approvals."
        )

    stage = request.GET.get("stage") or "final"

    user_to_approve = get_object_or_404(
        User,
        id=user_id,
        user_type__in=['bmoa', 'lgu', 'nga'],
        is_active=True,
        is_approved=False,
    )

    if user_to_approve.moa_first_level_approved:
        approve_url = (
            f"{reverse('common:approve_moa_user', args=[user_id])}?stage={stage}"
        )
        return redirect(approve_url)

    approvals_root = reverse('common:moa_approval_list')
    back_url = f"{approvals_root}?stage={stage}" if stage else approvals_root

    context = {
        "stage": stage,
        "pending_user": user_to_approve,
        "back_url": back_url,
        "approve_url": reverse("common:approve_moa_user", args=[user_id]),
    }
    return render(request, "common/approval/moa_risk_confirmation.html", context)


__all__ = [
    'MOAApprovalListView',
    'moa_approval_risk_prompt',
    'approve_moa_user_stage_one',
    'approve_moa_user',
    'reject_moa_user',
]
