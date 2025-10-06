"""
Redirect views for deprecated URLs.

This module provides custom redirect views that:
1. Log deprecation events
2. Show user-friendly messages
3. Preserve query parameters
4. Perform permanent (301) or temporary (302) redirects
"""

import logging
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.utils.http import urlencode

# Deprecation logger
deprecation_logger = logging.getLogger('deprecation')


class DeprecatedRedirectView(View):
    """
    Custom redirect view for deprecated URLs.

    Features:
    - Logs deprecation event
    - Shows Django message to user
    - Preserves query parameters
    - Configurable redirect target
    - Supports both permanent (301) and temporary (302) redirects
    """

    # Override these in URL configuration
    pattern_name = None  # Target URL name (e.g., 'common:work_item_list')
    permanent = False  # 301 (permanent) or 302 (temporary)
    message = None  # Custom deprecation message
    return_410_after = None  # Date after which to return 410 Gone

    def get(self, request, *args, **kwargs):
        """Handle GET requests to deprecated URLs."""
        return self._handle_redirect(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handle POST requests to deprecated URLs."""
        return self._handle_redirect(request, *args, **kwargs)

    def _handle_redirect(self, request, *args, **kwargs):
        """
        Handle the redirect with logging and user messaging.
        """
        # Check if we should return 410 Gone
        if self.return_410_after:
            from django.utils import timezone
            if timezone.now().date() > self.return_410_after:
                return HttpResponse(
                    content=self._get_410_message(),
                    status=410,
                    content_type='text/html'
                )

        # Log deprecation event
        self._log_deprecation(request)

        # Show user message
        self._show_user_message(request)

        # Build redirect URL with query parameters
        redirect_url = self._build_redirect_url(request, *args, **kwargs)

        # Perform redirect
        if self.permanent:
            return redirect(redirect_url, permanent=True)
        else:
            return redirect(redirect_url)

    def _log_deprecation(self, request):
        """Log the deprecation event."""
        user_info = (
            f"{request.user.username} (ID: {request.user.id})"
            if request.user.is_authenticated
            else "Anonymous"
        )

        deprecation_logger.warning(
            f"Deprecated URL redirect | "
            f"From: {request.path} | "
            f"To: {self.pattern_name} | "
            f"User: {user_info} | "
            f"IP: {self._get_client_ip(request)} | "
            f"Referer: {request.META.get('HTTP_REFERER', 'Direct')}"
        )

    def _show_user_message(self, request):
        """Show deprecation message to the user."""
        if self.message:
            message_text = self.message
        else:
            message_text = (
                "This URL is deprecated and will be removed soon. "
                "You have been redirected to the new Work Items interface."
            )

        messages.warning(request, message_text)

    def _build_redirect_url(self, request, *args, **kwargs):
        """Build the redirect URL with query parameters."""
        if not self.pattern_name:
            raise ValueError("pattern_name must be set on DeprecatedRedirectView")

        # Get base redirect URL
        redirect_url = reverse(self.pattern_name)

        # Preserve query parameters
        if request.GET:
            query_string = urlencode(request.GET)
            redirect_url = f"{redirect_url}?{query_string}"

        return redirect_url

    def _get_client_ip(self, request):
        """Get client IP address (proxy-aware)."""
        cf_connecting_ip = request.META.get('HTTP_CF_CONNECTING_IP')
        if cf_connecting_ip:
            return cf_connecting_ip

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()

        return request.META.get('REMOTE_ADDR', 'Unknown')

    def _get_410_message(self):
        """Get HTML message for 410 Gone response."""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>410 Gone - Endpoint Removed</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }
                .container {
                    background: white;
                    padding: 3rem;
                    border-radius: 1rem;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    text-align: center;
                    max-width: 500px;
                }
                h1 {
                    font-size: 4rem;
                    margin: 0;
                    color: #667eea;
                }
                h2 {
                    font-size: 1.5rem;
                    margin: 1rem 0;
                    color: #333;
                }
                p {
                    color: #666;
                    line-height: 1.6;
                }
                .button {
                    display: inline-block;
                    margin-top: 2rem;
                    padding: 0.75rem 2rem;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 0.5rem;
                    font-weight: 600;
                    transition: transform 0.2s;
                }
                .button:hover {
                    transform: translateY(-2px);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>410</h1>
                <h2>Endpoint Removed</h2>
                <p>
                    This endpoint has been permanently removed and replaced by
                    the unified Work Item system.
                </p>
                <p>
                    Please update your bookmarks and scripts to use the new interface.
                </p>
                <a href="/oobc-management/work-items/" class="button">
                    Go to Work Items
                </a>
            </div>
        </body>
        </html>
        """.encode('utf-8')


class StaffTaskRedirectView(DeprecatedRedirectView):
    """Redirect from old StaffTask URLs to WorkItem."""
    pattern_name = 'common:work_item_list'
    permanent = False
    message = (
        "Staff Tasks have been migrated to Work Items. "
        "This interface provides enhanced features including hierarchical task management."
    )


class ProjectWorkflowRedirectView(DeprecatedRedirectView):
    """Redirect from old ProjectWorkflow URLs to WorkItem."""
    pattern_name = 'common:work_item_list'
    permanent = False
    message = (
        "Project Workflows have been migrated to Work Items. "
        "Use the new unified interface for better project management."
    )


class EventRedirectView(DeprecatedRedirectView):
    """Redirect from old Event URLs to WorkItem."""
    pattern_name = 'common:work_item_list'
    permanent = False
    message = (
        "Events have been migrated to Work Items. "
        "The new system provides enhanced calendar integration and activity tracking."
    )
