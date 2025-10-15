"""Access control middleware for MANA participants and facilitators."""

from django.shortcuts import redirect
from django.urls import resolve


class MANAAccessControlMiddleware:
    """
    Restrict MANA Participants and Facilitators to only access:
    - Provincial OBC management pages
    - Regional MANA pages
    - Their own profile
    - Logout

    MANA users are identified by:
    - NOT is_staff
    - NOT is_superuser
    - Has can_access_regional_mana permission
    """

    # URL patterns that MANA users CAN access
    ALLOWED_URL_PATTERNS = [
        # Auth and profile
        "common:login",
        "common:logout",
        "common:profile",
        "common:dashboard",  # Allow dashboard (it will redirect appropriately)
        "common:home",  # Alias for dashboard
        # Provincial OBC
        "communities:communities_manage_provincial",
        "communities:communities_manage_provincial_obc",
        "communities:communities_view_provincial",
        "communities:communities_edit_provincial",
        "communities:communities_delete_provincial",
        "communities:communities_restore_provincial",
        "communities:communities_submit_provincial",
        "communities:communities_add_province",
        # Regional MANA
        "mana:mana_regional_overview",
        "mana:mana_provincial_overview",
        "mana:mana_provincial_card_detail",
        "mana:mana_province_edit",
        "mana:mana_province_delete",
        "mana:mana_manage_assessments",
        "mana:mana_assessment_detail",
        # MANA app (all regional MANA workshop URLs)
        "mana:",  # Allow all MANA app URLs
        # Static/media files
        "/static/",
        "/media/",
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is a MANA user (participant or facilitator)
        if request.user.is_authenticated:
            is_mana_user = (
                not request.user.is_staff
                and not request.user.is_superuser
                and request.user.has_perm("mana.can_access_regional_mana")
            )

            if is_mana_user:
                # Get current URL path
                path = request.path

                # Allow static/media files
                if path.startswith("/static/") or path.startswith("/media/"):
                    return self.get_response(request)

                # Check if URL is in allowed list
                try:
                    current_url = resolve(path)
                    url_name = current_url.url_name
                    namespace = current_url.namespace

                    # Build full URL name
                    if namespace:
                        full_url_name = f"{namespace}:{url_name}"
                    else:
                        full_url_name = url_name

                    # Check if URL is allowed
                    is_allowed = False

                    # Check exact matches
                    if full_url_name in self.ALLOWED_URL_PATTERNS:
                        is_allowed = True

                    # Check namespace patterns (e.g., "mana:")
                    for pattern in self.ALLOWED_URL_PATTERNS:
                        if pattern.endswith(":") and full_url_name.startswith(pattern):
                            is_allowed = True
                            break

                    if not is_allowed:
                        # Redirect to Regional MANA overview instead of raising PermissionDenied
                        return redirect("mana:mana_regional_overview")

                except Exception:
                    # If URL resolution fails, allow request to continue
                    # (will be handled by Django's normal 404)
                    pass

        response = self.get_response(request)
        return response
