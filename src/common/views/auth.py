"""Authentication and account management views."""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView

from ..constants import STAFF_USER_TYPES
from ..forms import CustomLoginForm, UserRegistrationForm, MOARegistrationForm
from ..models import StaffProfile, User
from coordination.models import Organization
from ..security_logging import (
    log_failed_login,
    log_successful_login,
    log_logout,
    log_admin_action,
)
from .management import build_staff_profile_detail_context


class CustomLoginView(LoginView):
    """Custom login view with OBC branding and approval check."""

    template_name = "common/login.html"
    form_class = CustomLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        """Process valid login form with security logging."""
        user = form.get_user()

        # Check if user account is approved
        if not user.is_approved and not user.is_superuser:
            # Log failed login due to unapproved account
            log_failed_login(self.request, user.username, reason="Account pending approval")
            messages.error(
                self.request,
                "Your account is pending approval. Please contact the administrator.",
            )
            return self.form_invalid(form)

        # Log successful login
        log_successful_login(self.request, user)

        return super().form_valid(form)

    def form_invalid(self, form):
        """Process invalid login form with security logging."""
        # Log failed login attempt (if username was provided)
        username = form.data.get('username', 'Unknown')
        if username:
            log_failed_login(self.request, username, reason="Invalid credentials")

        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    """Custom logout view with security logging."""

    template_name = "common/logged_out.html"
    http_method_names = ['get', 'post']  # Allow GET requests for logout links

    def get(self, request, *args, **kwargs):
        """Handle GET logout request."""
        # Log logout before user is logged out
        if request.user.is_authenticated:
            log_logout(request, request.user)

        # Perform logout
        auth_logout(request)

        # Render the logged out page
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        """Handle POST logout request."""
        # Log logout before user is logged out
        if request.user.is_authenticated:
            log_logout(request, request.user)

        # Perform logout
        auth_logout(request)

        # Render the logged out page
        return render(request, self.template_name)


class UserRegistrationView(CreateView):
    """User registration view with approval workflow."""

    model = User
    form_class = UserRegistrationForm
    template_name = "common/register.html"
    success_url = reverse_lazy("common:login")

    def form_valid(self, form):
        """Process valid registration form with security logging."""
        response = super().form_valid(form)

        # Log new user registration
        from ..security_logging import log_security_event
        log_security_event(
            self.request,
            event_type="User Registration",
            details=f"New user registered: {self.object.username} ({self.object.email})",
            severity="INFO"
        )

        messages.success(
            self.request,
            "Registration successful! Your account is pending approval. "
            "You will be notified once your account is approved.",
        )
        return response


@login_required
def profile(request):
    """User profile view."""
    user = request.user

    if user.user_type in STAFF_USER_TYPES:
        staff_profile = (
            StaffProfile.objects.select_related("user")
            .filter(user=user)
            .first()
        )
        if staff_profile:
            context = build_staff_profile_detail_context(
                request,
                staff_profile,
                base_url=reverse("common:profile"),
                viewing_user=user,
                allow_delete=False,
            )
            return render(request, "common/staff_profile_detail.html", context)

    return render(request, "common/profile.html", {"user": user})


@login_required
def page_restricted(request):
    """Render the restricted-access placeholder screen."""
    return render(request, "common/page_restricted.html")


class MOARegistrationView(CreateView):
    """
    MOA staff self-registration view.
    Creates unapproved accounts that require admin approval.
    """

    model = User
    form_class = MOARegistrationForm
    template_name = "common/auth/moa_register.html"
    success_url = reverse_lazy("common:moa_register_success")

    def get_context_data(self, **kwargs):
        """Inject organization directory metadata for dynamic filtering."""
        context = super().get_context_data(**kwargs)

        organizations = (
            Organization.objects.filter(
                organization_type__in=MOARegistrationForm.MOA_ORGANIZATION_TYPES,
                is_active=True,
            )
            .order_by("name")
        )
        grouped = {choice[0]: [] for choice in MOARegistrationForm.MOA_USER_TYPES}
        for org in organizations:
            grouped.setdefault(org.organization_type, []).append(
                {
                    "id": str(org.id),
                    "name": org.display_name if hasattr(org, "display_name") else org.name,
                }
            )

        context["organizations_by_type"] = grouped

        organization_field = context["form"].fields["organization"]
        context["organization_placeholder"] = (
            organization_field.widget.attrs.get("data-placeholder")
            or organization_field.empty_label
            or "Select your organization"
        )

        return context

    def form_valid(self, form):
        """Process valid MOA registration with email notifications."""
        response = super().form_valid(form)

        # Log new MOA staff registration
        from ..security_logging import log_security_event
        log_security_event(
            self.request,
            event_type="MOA Staff Registration",
            details=(
                f"New MOA staff registered: {self.object.username} "
                f"({self.object.get_user_type_display()}) - {self.object.organization}"
            ),
            severity="INFO"
        )

        # Send notification email to user
        try:
            send_mail(
                subject="OBCMS Registration Received - Pending Approval",
                message=(
                    f"Dear {self.object.get_full_name()},\n\n"
                    f"Thank you for registering with the OBCMS platform.\n\n"
                    f"Your registration details:\n"
                    f"Username: {self.object.username}\n"
                    f"Email: {self.object.email}\n"
                    f"Organization: {self.object.organization}\n"
                    f"Position: {self.object.position}\n\n"
                    f"Your account is currently pending approval by OOBC administrators. "
                    f"You will receive another email once your account has been approved.\n\n"
                    f"If you did not register for this account, please contact us immediately at "
                    f"{settings.DEFAULT_FROM_EMAIL}.\n\n"
                    f"Best regards,\n"
                    f"OOBC Management System"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.object.email],
                fail_silently=True,
            )
        except Exception as e:
            # Log email error but don't prevent registration
            log_security_event(
                self.request,
                event_type="Email Error",
                details=f"Failed to send registration confirmation to {self.object.email}: {str(e)}",
                severity="WARNING"
            )

        # Send notification to administrators
        try:
            admin_emails = User.objects.filter(
                is_superuser=True,
                is_active=True,
                email__isnull=False
            ).exclude(email='').values_list('email', flat=True)

            if admin_emails:
                send_mail(
                    subject=f"New MOA Staff Registration: {self.object.get_full_name()}",
                    message=(
                        f"A new MOA staff member has registered and is awaiting approval:\n\n"
                        f"Name: {self.object.get_full_name()}\n"
                        f"Username: {self.object.username}\n"
                        f"Email: {self.object.email}\n"
                        f"Organization Type: {self.object.get_user_type_display()}\n"
                        f"Organization: {self.object.organization}\n"
                        f"Position: {self.object.position}\n"
                        f"Contact: {self.object.contact_number}\n\n"
                        f"Please review and approve this registration at:\n"
                f"{self.request.build_absolute_uri(reverse('common:moa_approval_list'))}\n\n"
                        f"OOBC Management System"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=list(admin_emails),
                    fail_silently=True,
                )
        except Exception as e:
            # Log email error but don't prevent registration
            log_security_event(
                self.request,
                event_type="Email Error",
                details=f"Failed to send admin notification for {self.object.username}: {str(e)}",
                severity="WARNING"
            )

        return response


class MOARegistrationSuccessView(TemplateView):
    """Success page shown after MOA staff registration."""

    template_name = "common/auth/moa_register_success.html"


__all__ = [
    "CustomLoginView",
    "CustomLogoutView",
    "UserRegistrationView",
    "MOARegistrationView",
    "MOARegistrationSuccessView",
    "profile",
    "page_restricted",
]
