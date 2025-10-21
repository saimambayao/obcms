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

# Allow internal Kubernetes/Docker IPs for health checks
# Kubernetes pod network typically uses 10.x.x.x or 172.x.x.x
# This allows health check probes to succeed without compromising security
# Can be customized via INTERNAL_IPS environment variable if needed
import re

INTERNAL_IPS = env.list("INTERNAL_IPS", default=['127.0.0.1', 'localhost'])

# Custom ALLOWED_HOSTS validation that accepts internal Kubernetes IPs
class AllowInternalIPsValidator:
    """Allow requests from Kubernetes internal pod network for health checks."""

    def __init__(self, allowed_hosts, internal_networks=None):
        self.allowed_hosts = allowed_hosts
        # Default Kubernetes pod networks (10.x.x.x, 172.16-31.x.x)
        self.internal_networks = internal_networks or [
            r'^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$',           # 10.0.0.0/8
            r'^172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3}$',  # 172.16.0.0/12
            r'^192\.168\.\d{1,3}\.\d{1,3}$',              # 192.168.0.0/16
        ]

    def __contains__(self, host):
        # Remove port from host if present
        host_without_port = host.split(':')[0]

        # Check against configured ALLOWED_HOSTS
        if host in self.allowed_hosts or host_without_port in self.allowed_hosts:
            return True

        # Check if it's an internal IP (for health checks)
        for pattern in self.internal_networks:
            if re.match(pattern, host_without_port):
                return True

        return False

# Wrap ALLOWED_HOSTS with validator that accepts internal IPs
ALLOWED_HOSTS = AllowInternalIPsValidator(ALLOWED_HOSTS + INTERNAL_IPS)

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

# SECURITY: Secure cookies (production-only overrides)
SESSION_COOKIE_SECURE = True  # HTTPS-only session cookies
CSRF_COOKIE_SECURE = True  # HTTPS-only CSRF cookies
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Strict"  # Strict for CSRF (prevent cross-site form submission)

# Session Security (Production Override)
SESSION_COOKIE_AGE = 28800  # 8 hours (was 2 weeks in base.py)
SESSION_COOKIE_SAMESITE = "Strict"  # Stricter than base.py's "Lax"
SESSION_COOKIE_HTTPONLY = True
SESSION_SAVE_EVERY_REQUEST = True  # Extend session on activity
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Keep 8-hour timeout

# Session cookie name (security through obscurity)
SESSION_COOKIE_NAME = env.str("SESSION_COOKIE_NAME", default="obcms_sessionid")

# SECURITY: Strict SECRET_KEY validation for production
if DEBUG:
    raise ValueError("DEBUG must be False in production")

if not SECRET_KEY or len(SECRET_KEY) < 50:
    raise ValueError("Production requires a strong SECRET_KEY (50+ characters)")

if SECRET_KEY.startswith('django-insecure'):
    raise ValueError(
        "Production cannot use django-insecure SECRET_KEY. "
        "Generate a cryptographically secure key and set SECRET_KEY in environment."
    )

# SECURITY: Additional headers
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# REMOVED: SECURE_BROWSER_XSS_FILTER (deprecated in modern browsers)

# NEW: Referrer Policy
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# NEW: Permissions Policy (restrict browser features)
PERMISSIONS_POLICY = {
    "accelerometer": [],
    "camera": [],
    "geolocation": [],
    "microphone": [],
    "payment": [],
    "usb": [],
}

# SECURITY: Content Security Policy (CSP)
# Strict CSP without 'unsafe-inline' - use nonce or hash-based approach
# For Bootstrap/Tailwind inline styles, consider:
# 1. Using nonce-based CSP (django-csp package)
# 2. Extracting inline styles to external files
# 3. Using hash-based CSP for specific inline blocks
CSP_DEFAULT = (
    "default-src 'self'; "
    "script-src 'self' https://cdn.tailwindcss.com https://unpkg.com; "
    "style-src 'self' https://cdnjs.cloudflare.com https://cdn.tailwindcss.com https://unpkg.com; "
    "font-src 'self' https://cdnjs.cloudflare.com data:; "
    "img-src 'self' data: https:; "
    "connect-src 'self'; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "form-action 'self';"
)
CONTENT_SECURITY_POLICY = env.str("CONTENT_SECURITY_POLICY", default=CSP_DEFAULT)

# Admin IP whitelist (restrict /admin/ access to specific IPs)
ADMIN_IP_WHITELIST = env.list("ADMIN_IP_WHITELIST", default=[])
# Example: ADMIN_IP_WHITELIST=192.168.1.100,10.0.0.0/8,172.16.0.0/12

# Metrics Authentication (Prometheus endpoint protection)
METRICS_TOKEN = env.str("METRICS_TOKEN", default="")
# Generate with: openssl rand -hex 32
# Example: METRICS_TOKEN=a1b2c3d4e5f6...

# Add CSP and admin IP restriction middleware
_base_middleware = [
    m
    for m in MIDDLEWARE
    if m
    not in [
        "django.middleware.security.SecurityMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
        "django_prometheus.middleware.PrometheusAfterMiddleware",  # Will be re-added at the end
    ]
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "common.middleware.ContentSecurityPolicyMiddleware",  # CSP headers (production)
    "common.middleware.AdminIPWhitelistMiddleware",  # Admin IP restriction (production)
] + _base_middleware + [
    "common.middleware.MetricsAuthenticationMiddleware",  # Protect metrics endpoint
    "django_prometheus.middleware.PrometheusAfterMiddleware",  # Must be last for metrics
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

# ============================================================================
# DATABASE SSL/TLS CONFIGURATION
# ============================================================================
# PostgreSQL SSL/TLS encryption for production security
if 'postgres' in DATABASES['default']['ENGINE']:
    # SSL mode: require, verify-ca, or verify-full
    db_sslmode = env.str('DB_SSLMODE', default='require')

    # Only configure SSL options if not using verify-none/disable
    if db_sslmode not in ['disable', 'allow', 'prefer']:
        DATABASES['default']['OPTIONS'] = DATABASES['default'].get('OPTIONS', {})
        DATABASES['default']['OPTIONS'].update({
            'sslmode': db_sslmode,
        })

        # Add SSL certificate if using verify-ca or verify-full
        if db_sslmode in ['verify-ca', 'verify-full']:
            db_ssl_cert = env.str('DB_SSL_CERT', default='')
            if db_ssl_cert:
                DATABASES['default']['OPTIONS']['sslrootcert'] = db_ssl_cert
            else:
                # Use system CA certificates
                DATABASES['default']['OPTIONS']['sslrootcert'] = '/etc/ssl/certs/ca-certificates.crt'

# EMAIL: Ensure production email backend is configured
if EMAIL_BACKEND == "django.core.mail.backends.console.EmailBackend":
    raise ValueError("EMAIL_BACKEND must be configured for production (not console)")

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
