"""MOA staff approval views."""

import json
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView

from ..models import User
from ..security_logging import log_security_event
from ..utils.permissions import can_approve_moa_users, get_pending_moa_count


class MOAApprovalListView(ListView):
    """
    Dashboard for reviewing and approving MOA staff registrations.
    Only accessible to authorized approvers.
    """

    model = User
    template_name = "common/approval/moa_approval_list.html"
    context_object_name = "pending_users"
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        """Check if user has approval permissions."""
        if not can_approve_moa_users(request.user):
            messages.error(
                request,
                "You do not have permission to approve MOA staff registrations."
            )
            from django.shortcuts import redirect
            return redirect('common:page_restricted')

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Get all pending MOA staff registrations."""
        return User.objects.filter(
            user_type__in=['bmoa', 'lgu', 'nga'],
            is_approved=False,
            is_active=True
        ).select_related('approved_by').order_by('-date_joined')

    def get_context_data(self, **kwargs):
        """Add approval statistics to context."""
        context = super().get_context_data(**kwargs)

        # Get statistics
        all_moa_users = User.objects.filter(user_type__in=['bmoa', 'lgu', 'nga'])
        context['stats'] = {
            'pending_count': get_pending_moa_count(),
            'approved_count': all_moa_users.filter(is_approved=True).count(),
            'total_count': all_moa_users.count(),
        }

        return context


@login_required
def approve_moa_user(request, user_id):
    """
    Approve a MOA staff registration.
    Sends email notification to the user.
    """
    # Check permissions
    if not can_approve_moa_users(request.user):
        return HttpResponse(
            status=403,
            content="You do not have permission to approve users."
        )

    # Get user to approve
    user_to_approve = get_object_or_404(
        User,
        id=user_id,
        user_type__in=['bmoa', 'lgu', 'nga'],
        is_approved=False
    )

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
    from django.shortcuts import redirect
    return redirect('common:moa_approval_list')


@login_required
def reject_moa_user(request, user_id):
    """
    Reject a MOA staff registration.
    Deactivates the account and sends notification email.
    """
    # Check permissions
    if not can_approve_moa_users(request.user):
        return HttpResponse(
            status=403,
            content="You do not have permission to reject users."
        )

    # Get user to reject
    user_to_reject = get_object_or_404(
        User,
        id=user_id,
        user_type__in=['bmoa', 'lgu', 'nga'],
        is_approved=False
    )

    # Deactivate user (soft delete)
    user_to_reject.is_active = False
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
    from django.shortcuts import redirect
    return redirect('common:moa_approval_list')


__all__ = [
    'MOAApprovalListView',
    'approve_moa_user',
    'reject_moa_user',
]
