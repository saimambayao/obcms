"""
HTMX response utilities for standardized error handling.

This module provides consistent error response patterns for HTMX endpoints
across OBCMS, ensuring uniform user experience with toast notifications.
"""

import json
from typing import Optional

from django.http import HttpResponse


def htmx_403_response(
    message: Optional[str] = None,
    trigger_toast: bool = True
) -> HttpResponse:
    """
    Return standardized 403 (Forbidden) response for HTMX requests.

    This function provides a consistent way to handle permission denied errors
    in HTMX endpoints, with automatic error toast notifications and minimal
    HTML content.

    Args:
        message: Custom error message to display to the user.
                Defaults to: "You do not have permission to perform this action."
        trigger_toast: Whether to trigger the error toast notification.
                      Defaults to True.

    Returns:
        HttpResponse with:
        - Status code 403
        - HX-Trigger header for error toast (if trigger_toast=True)
        - Minimal HTML content (empty string)

    Example:
        >>> from common.utils.htmx_responses import htmx_403_response
        >>>
        >>> # Basic usage with default message
        >>> if not has_permission(request.user):
        >>>     return htmx_403_response()
        >>>
        >>> # With custom message
        >>> if not can_approve_users(request.user):
        >>>     return htmx_403_response(
        >>>         message="Only coordinators can approve user registrations."
        >>>     )
        >>>
        >>> # Without toast notification (silent)
        >>> if not is_owner(request.user, obj):
        >>>     return htmx_403_response(
        >>>         message="Access denied",
        >>>         trigger_toast=False
        >>>     )

    Integration:
        Works seamlessly with the global error toast component defined in
        src/templates/components/error_toast.html and the HX-Trigger event
        listener in src/templates/base.html.

        The 'show-toast' event is automatically handled by the global
        JavaScript listener that displays the error message in a styled
        toast notification.
    """
    # Set default message if none provided
    if message is None:
        message = "You do not have permission to perform this action."

    # Prepare response headers
    headers = {}

    # Add HX-Trigger header for error toast if requested
    if trigger_toast:
        headers["HX-Trigger"] = json.dumps({
            "show-toast": message
        })

    # Return 403 response with headers and empty content
    return HttpResponse(
        status=403,
        headers=headers,
        content=""  # Minimal content - HTMX handles UI updates
    )


def htmx_error_response(
    message: str,
    status: int = 400,
    trigger_toast: bool = True
) -> HttpResponse:
    """
    Return standardized error response for HTMX requests.

    Generic error response utility for various HTTP error codes.
    Use htmx_403_response() for permission-specific errors.

    Args:
        message: Error message to display to the user.
        status: HTTP status code. Defaults to 400 (Bad Request).
        trigger_toast: Whether to trigger the error toast notification.
                      Defaults to True.

    Returns:
        HttpResponse with specified status code and error toast trigger.

    Example:
        >>> # 400 Bad Request
        >>> if not form.is_valid():
        >>>     return htmx_error_response(
        >>>         message="Invalid form data. Please check your inputs.",
        >>>         status=400
        >>>     )
        >>>
        >>> # 404 Not Found
        >>> if not obj:
        >>>     return htmx_error_response(
        >>>         message="Resource not found.",
        >>>         status=404
        >>>     )
        >>>
        >>> # 500 Server Error
        >>> return htmx_error_response(
        >>>     message="An unexpected error occurred. Please try again.",
        >>>     status=500
        >>> )
    """
    headers = {}

    if trigger_toast:
        headers["HX-Trigger"] = json.dumps({
            "show-toast": message
        })

    return HttpResponse(
        status=status,
        headers=headers,
        content=""
    )


def htmx_success_response(
    message: str,
    additional_triggers: Optional[dict] = None
) -> HttpResponse:
    """
    Return standardized success response for HTMX requests.

    Args:
        message: Success message to display in toast.
        additional_triggers: Optional dict of additional HX-Trigger events.
                           The 'show-toast' trigger is automatically included.

    Returns:
        HttpResponse with 200 status and success toast trigger.

    Example:
        >>> # Basic success
        >>> return htmx_success_response(
        >>>     message="User approved successfully"
        >>> )
        >>>
        >>> # With additional triggers for UI updates
        >>> return htmx_success_response(
        >>>     message="User endorsed to OOBC",
        >>>     additional_triggers={
        >>>         "user-endorsed": {"id": user_id},
        >>>         "refresh-list": True
        >>>     }
        >>> )
    """
    triggers = {"show-toast": message}

    if additional_triggers:
        triggers.update(additional_triggers)

    return HttpResponse(
        status=200,
        headers={"HX-Trigger": json.dumps(triggers)},
        content=""
    )


__all__ = [
    "htmx_403_response",
    "htmx_error_response",
    "htmx_success_response",
]
