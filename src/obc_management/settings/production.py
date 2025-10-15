"""
Production settings for OBCMS.

DO NOT use this in development.
Enforces security best practices and production-grade configurations.
"""

from .base import *  # noqa

# SECURITY: Force DEBUG off in production (no environment override)
DEBUG = False
TEMPLATE_DEBUG = False

# SECURITY: Allowed hosts (strict validation)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
if not ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS must be explicitly set in production")

# SECURITY: CSRF trusted origins (required for HTTPS behind proxy)
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
if not CSRF_TRUSTED_ORIGINS:
    raise ValueError(
        "CSRF_TRUSTED_ORIGINS must be set for production HTTPS\n"
        "Example: CSRF_TRUSTED_ORIGINS=https://obcms.gov.ph,https://www.obcms.gov.ph\n"
        "IMPORTANT: Must include https:// scheme, not just domain names"
    )

# Validate CSRF_TRUSTED_ORIGINS format
for origin in CSRF_TRUSTED_ORIGINS:
    if not origin.startswith(("https://", "http://")):
        raise ValueError(
            f"Invalid CSRF_TRUSTED_ORIGINS format: {origin}\n"
            "Each origin must include the scheme (https:// or http://)\n"
            f"Example: https://{origin} (not just {origin})"
        )

# SECURITY: Force HTTPS redirects
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)

# SECURITY: HTTP Strict Transport Security (HSTS)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# SECURITY: Secure cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Strict"  # CSRF protection via SameSite
CSRF_COOKIE_SAMESITE = "Strict"

# SECURITY: Additional headers
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_BROWSER_XSS_FILTER = True

# SECURITY: Content Security Policy (CSP)
# Restricts resource loading to prevent XSS and data injection attacks
# Customizable via environment variable for flexibility
CSP_DEFAULT = (
    "default-src 'self'; "
    "script-src 'self' https://cdn.tailwindcss.com 'unsafe-inline'; "
    "style-src 'self' https://cdnjs.cloudflare.com https://cdn.tailwindcss.com 'unsafe-inline'; "
    "font-src 'self' https://cdnjs.cloudflare.com data:; "
    "img-src 'self' data: https:; "
    "connect-src 'self'; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "form-action 'self';"
)
CONTENT_SECURITY_POLICY = env.str("CONTENT_SECURITY_POLICY", default=CSP_DEFAULT)

# Add CSP middleware to inject headers
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "common.middleware.ContentSecurityPolicyMiddleware",  # CSP headers (production)
] + [
    m
    for m in MIDDLEWARE
    if m
    not in [
        "django.middleware.security.SecurityMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
    ]
]

# SECURITY: Proxy SSL header (for Coolify/Traefik/Nginx)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# SECURITY: CORS Configuration for Production
# Override base.py localhost settings with production domain
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
if not CORS_ALLOWED_ORIGINS:
    # WARNING: CORS_ALLOWED_ORIGINS must be set in production .env
    # Example: CORS_ALLOWED_ORIGINS=https://obcms.example.gov.ph,https://api.obcms.example.gov.ph
    pass  # Will use empty list, effectively blocking cross-origin requests (secure default)

# Never allow all origins in production
CORS_ALLOW_ALL_ORIGINS = False

# ADMIN: Restrict admin access by IP if needed
# ALLOWED_ADMIN_IPS = env.list('ALLOWED_ADMIN_IPS', default=[])

# LOGGING: Production logging (stdout/stderr for Docker)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": env.str("LOG_LEVEL", default="INFO"),
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "celery": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# PERFORMANCE: Database connection pooling
DATABASES["default"]["CONN_MAX_AGE"] = 600  # 10 minutes
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True  # Django 4.1+

# If using PgBouncer transaction pooling, uncomment:
# DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = True

# EMAIL: Warn if production email backend is not configured
# Allow console backend for staging/testing environments
if EMAIL_BACKEND == "django.core.mail.backends.console.EmailBackend":
    import warnings
    warnings.warn(
        "EMAIL_BACKEND is set to console - emails will not be sent. "
        "Configure SMTP for production.",
        UserWarning
    )

# CELERY: Production task settings
CELERY_WORKER_MAX_TASKS_PER_CHILD = (
    1000  # Restart worker after N tasks (memory leak protection)
)
CELERY_WORKER_PREFETCH_MULTIPLIER = 4  # Tasks to prefetch per worker
CELERY_TASK_TIME_LIMIT = 300  # Hard timeout (5 minutes)
CELERY_TASK_SOFT_TIME_LIMIT = 240  # Soft timeout (4 minutes)
CELERY_TASK_ACKS_LATE = True  # Acknowledge task after completion (retry on failure)
CELERY_WORKER_SEND_TASK_EVENTS = True  # Enable monitoring
CELERY_TASK_SEND_SENT_EVENT = True

# Celery 5.5+ Soft Shutdown (graceful task completion on worker restart)
CELERY_WORKER_SOFT_SHUTDOWN_TIMEOUT = 60.0  # Seconds to wait for tasks to finish
CELERY_WORKER_ENABLE_SOFT_SHUTDOWN_ON_IDLE = True  # Prevent losing ETA/retry tasks

# ============================================================================
# SECURITY ENHANCEMENT: Disable DRF Browsable API in Production
# ============================================================================
# Remove HTML browsable API renderer to prevent information disclosure
# API will only return JSON responses
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
    # BrowsableAPIRenderer intentionally removed for production security
]
