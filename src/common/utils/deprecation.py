"""
Deprecation utilities for marking legacy code.

This module provides decorators and helpers for managing deprecated code
during the transition to the WorkItem unified work hierarchy system.
"""

import functools
import warnings
from datetime import date
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.html import format_html


def deprecated(replacement=None, message=None, category=PendingDeprecationWarning, return_410_after=None):
    """
    Decorator to mark a view as deprecated and optionally redirect to replacement.

    Args:
        replacement: URL name or callable to redirect to (optional)
        message: Custom deprecation message (optional)
        category: Warning category (default: PendingDeprecationWarning)
        return_410_after: Date after which to return 410 Gone instead of redirect (optional)

    Example:
        @deprecated(replacement='common:work_item_list', message='Use WorkItem instead')
        def staff_task_list(request):
            # This view is deprecated
            pass
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Build deprecation message
            default_msg = f"{view_func.__name__} is deprecated."
            if replacement:
                if callable(replacement):
                    default_msg += f" Use {replacement.__name__} instead."
                else:
                    default_msg += f" Use {replacement} instead."

            warning_message = message or default_msg

            # Log deprecation warning
            warnings.warn(warning_message, category, stacklevel=2)

            # Check if we should return 410 Gone
            if return_410_after and isinstance(return_410_after, date):
                from django.utils import timezone
                if timezone.now().date() > return_410_after:
                    return HttpResponse(
                        status=410,
                        content=f"This endpoint has been removed. {warning_message}".encode()
                    )

            # Redirect to replacement if provided
            if replacement:
                if callable(replacement):
                    return replacement(request, *args, **kwargs)
                else:
                    # It's a URL name
                    return redirect(replacement)

            # Otherwise, execute the original view (with warning logged)
            return view_func(request, *args, **kwargs)

        # Mark the function as deprecated
        wrapper._is_deprecated = True
        wrapper._deprecation_message = message or f"{view_func.__name__} is deprecated"
        wrapper._replacement = replacement

        return wrapper
    return decorator


def deprecation_warning(view_name, replacement_view=None):
    """
    Helper function to log deprecation warnings from within views.

    Args:
        view_name: Name of the deprecated view
        replacement_view: Name of the replacement view (optional)
    """
    message = f"{view_name} is deprecated."
    if replacement_view:
        message += f" Use {replacement_view} instead."

    warnings.warn(message, PendingDeprecationWarning, stacklevel=2)


def get_deprecation_banner_html(replacement_url=None, replacement_text="Work Items"):
    """
    Generate HTML for deprecation notice banner.

    Args:
        replacement_url: URL to link to the replacement interface
        replacement_text: Display text for the replacement link

    Returns:
        HTML string for deprecation banner
    """
    if replacement_url:
        link_html = format_html(
            '<a href="{}" class="underline font-semibold text-amber-800 hover:text-amber-900">{}</a>',
            replacement_url,
            replacement_text
        )
    else:
        link_html = format_html('<span class="font-semibold">{}</span>', replacement_text)

    return format_html(
        '<div class="bg-amber-50 border-l-4 border-amber-500 p-4 mb-4 rounded-r-lg">'
        '<div class="flex items-start">'
        '<div class="flex-shrink-0">'
        '<i class="fas fa-exclamation-triangle text-amber-500 text-xl"></i>'
        '</div>'
        '<div class="ml-4 flex-1">'
        '<h3 class="text-sm font-semibold text-amber-800">Deprecation Notice</h3>'
        '<div class="mt-1 text-sm text-amber-700">'
        '<p>'
        'This interface is deprecated and will be removed in a future release. '
        'Please use {} instead for enhanced features and better performance.'
        '</p>'
        '</div>'
        '</div>'
        '</div>'
        '</div>',
        link_html
    )


def get_admin_deprecation_notice(replacement_admin_url=None, replacement_name="WorkItem"):
    """
    Generate HTML for admin interface deprecation notice.

    Args:
        replacement_admin_url: URL to the replacement admin interface
        replacement_name: Name of the replacement model

    Returns:
        HTML string for admin deprecation notice
    """
    if replacement_admin_url:
        link_html = format_html(
            '<a href="{}" style="font-weight: bold; text-decoration: underline; color: #92400e;">{} admin</a>',
            replacement_admin_url,
            replacement_name
        )
    else:
        link_html = format_html('<strong>{} admin</strong>', replacement_name)

    return format_html(
        '<div style="background-color: #fffbeb; border: 2px solid #f59e0b; padding: 16px; '
        'margin-bottom: 20px; border-radius: 8px; border-left: 6px solid #f59e0b;">'
        '<div style="display: flex; align-items: start;">'
        '<span style="font-size: 24px; margin-right: 12px;">⚠️</span>'
        '<div>'
        '<strong style="color: #92400e; font-size: 16px;">Deprecation Warning</strong><br>'
        '<span style="color: #78350f; font-size: 14px; margin-top: 4px; display: block;">'
        'This admin interface is deprecated and will be removed in a future release. '
        'Please use {} instead.'
        '</span>'
        '</div>'
        '</div>'
        '</div>',
        link_html
    )
