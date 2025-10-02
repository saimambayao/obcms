#!/usr/bin/env python
"""
Run Django deployment checks with proper environment variables.
This script sets up minimal required environment variables to test deployment configuration.
"""
import os
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Set required environment variables for deployment checks
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "obc_management.settings.production")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-deployment-checks-only-minimum-50-chars")
os.environ.setdefault("DEBUG", "0")
os.environ.setdefault("ALLOWED_HOSTS", "localhost,127.0.0.1,staging.example.com")
os.environ.setdefault("CSRF_TRUSTED_ORIGINS", "https://staging.example.com,http://localhost")
os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
os.environ.setdefault("EMAIL_HOST", "smtp.example.com")
os.environ.setdefault("EMAIL_PORT", "587")
os.environ.setdefault("EMAIL_USE_TLS", "1")
os.environ.setdefault("EMAIL_HOST_USER", "test@example.com")
os.environ.setdefault("EMAIL_HOST_PASSWORD", "test_password")
os.environ.setdefault("DEFAULT_FROM_EMAIL", "test@example.com")

# Now run Django management command
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    execute_from_command_line(["manage.py", "check", "--deploy"])
