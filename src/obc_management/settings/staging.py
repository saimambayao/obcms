"""Staging settings for the BMMS pilot environment."""

from django.core.exceptions import ImproperlyConfigured

# Import from base instead of production to reuse defaults
from .base import *  # noqa


FEATURE_FLAGS = globals().get("FEATURE_FLAGS", {})


REQUIRED_ENV_VARS = [
    "SECRET_KEY",
    "DATABASE_URL",
    "ALLOWED_HOSTS",
    "CSRF_TRUSTED_ORIGINS",
    "REDIS_URL",
    "CELERY_BROKER_URL",
    "DEFAULT_FROM_EMAIL",
]


def _validate_required_env_vars() -> None:
    missing = [var for var in REQUIRED_ENV_VARS if not env.str(var, default="").strip()]
    if missing:
        raise ImproperlyConfigured(
            "Missing required staging environment variables: " + ", ".join(sorted(missing))
        )


_validate_required_env_vars()


# Production-like settings
DEBUG = False
TEMPLATE_DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])


# Feature flags for the pilot environment
FEATURE_FLAGS.setdefault("pilot_mode", env.bool("FEATURE_PILOT_MODE", default=True))
FEATURE_FLAGS.setdefault(
    "allow_pilot_signups", env.bool("FEATURE_ALLOW_PILOT_SIGNUPS", default=False)
)


# Email settings
EMAIL_BACKEND = env.str(
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
DEFAULT_FROM_EMAIL = env.str(
    "DEFAULT_FROM_EMAIL", default="BMMS Pilot Support <support@bmms.local>"
)
PILOT_SUPPORT_EMAIL = env.str(
    "PILOT_SUPPORT_EMAIL", default="support@bmms.local"
)


# Security configuration
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=True)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=True)
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_BROWSER_XSS_FILTER = True
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=60 * 60 * 24 * 365)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True
)
SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=True)


# Database connection pooling
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DB_CONN_MAX_AGE", default=600)
DATABASES["default"]["CONN_HEALTH_CHECKS"] = env.bool(
    "DB_CONN_HEALTH_CHECKS", default=True
)


# Celery configuration
CELERY_BROKER_URL = env.str("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = env.str("CELERY_RESULT_BACKEND", default=CELERY_BROKER_URL)
CELERY_WORKER_MAX_TASKS_PER_CHILD = env.int(
    "CELERY_WORKER_MAX_TASKS_PER_CHILD", default=1000
)
CELERY_WORKER_PREFETCH_MULTIPLIER = env.int("CELERY_WORKER_PREFETCH_MULTIPLIER", default=4)
CELERY_TASK_TIME_LIMIT = env.int("CELERY_TASK_TIME_LIMIT", default=300)
CELERY_TASK_SOFT_TIME_LIMIT = env.int("CELERY_TASK_SOFT_TIME_LIMIT", default=240)
CELERY_TASK_ACKS_LATE = env.bool("CELERY_TASK_ACKS_LATE", default=True)
CELERY_WORKER_SEND_TASK_EVENTS = True
CELERY_TASK_SEND_SENT_EVENT = True
CELERY_WORKER_SOFT_SHUTDOWN_TIMEOUT = 60.0
CELERY_WORKER_ENABLE_SOFT_SHUTDOWN_ON_IDLE = True


# Pilot onboarding constants
PILOT_ORGANIZATION_CODES = env.list(
    "PILOT_ORGANIZATION_CODES", default=["MOH", "MOLE", "MAFAR"]
)
PILOT_DEFAULT_PASSWORD_LENGTH = env.int("PILOT_DEFAULT_PASSWORD_LENGTH", default=16)
BACKUP_DIRECTORY = env.str(
    "BACKUP_DIRECTORY", default=str(BASE_DIR.parent / "backups" / "pilot")
)
BACKUP_RETENTION_DAYS = env.int("BACKUP_RETENTION_DAYS", default=30)


# Logging configuration
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
    },
}
