"""Authentication and account management views."""

from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView

from ..constants import STAFF_USER_TYPES
from ..forms import CustomLoginForm, UserRegistrationForm
from ..models import StaffProfile, User
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

    http_method_names = ['get', 'post']  # Allow GET requests for logout links

    def get_next_page(self):
        """Send users back to login with dashboard as the default next target."""
        return f"{reverse('common:login')}?next=/"

    def dispatch(self, request, *args, **kwargs):
        """Handle logout with security logging."""
        # Log logout before user is logged out
        if request.user.is_authenticated:
            log_logout(request, request.user)

        return super().dispatch(request, *args, **kwargs)


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


__all__ = [
    "CustomLoginView",
    "CustomLogoutView",
    "UserRegistrationView",
    "profile",
    "page_restricted",
]
