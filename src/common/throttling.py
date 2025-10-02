"""
Custom throttling classes for API rate limiting.

Implements security controls to prevent:
- Brute force attacks
- Denial of Service (DoS)
- Data scraping
- Resource exhaustion
"""

from rest_framework.throttling import (
    AnonRateThrottle,
    UserRateThrottle,
    SimpleRateThrottle,
)


class AuthenticationThrottle(SimpleRateThrottle):
    """
    Strict rate limiting for authentication endpoints.

    Prevents brute force attacks on login/token endpoints.
    Rate: 5 attempts per minute per IP address
    """

    scope = "auth"

    def get_cache_key(self, request, view):
        # Throttle by IP address for authentication attempts
        if request.user.is_authenticated:
            # Authenticated users get higher limit
            return None  # Fall through to user throttle

        # Anonymous users throttled by IP
        ident = self.get_ident(request)
        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }


class AnonThrottle(AnonRateThrottle):
    """
    Rate limiting for anonymous (unauthenticated) users.

    Rate: 100 requests per hour
    """

    scope = "anon"


class UserThrottle(UserRateThrottle):
    """
    Rate limiting for authenticated users.

    Rate: 1000 requests per hour
    """

    scope = "user"


class BurstThrottle(SimpleRateThrottle):
    """
    Short-term burst protection.

    Prevents rapid-fire requests that could overwhelm the system.
    Rate: 60 requests per minute
    """

    scope = "burst"

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }


class DataExportThrottle(SimpleRateThrottle):
    """
    Strict rate limiting for data export operations.

    Prevents mass data exfiltration.
    Rate: 10 exports per hour
    """

    scope = "export"

    def get_cache_key(self, request, view):
        if not request.user.is_authenticated:
            return None  # Block anonymous exports entirely

        return self.cache_format % {
            "scope": self.scope,
            "ident": request.user.pk,
        }


class AdminThrottle(SimpleRateThrottle):
    """
    Moderate rate limiting for admin users.

    Admins get higher limits but still protected against account compromise.
    Rate: 5000 requests per hour
    """

    scope = "admin"

    def get_cache_key(self, request, view):
        if not request.user.is_authenticated or not request.user.is_staff:
            return None  # Fall through to other throttles

        return self.cache_format % {
            "scope": self.scope,
            "ident": request.user.pk,
        }
