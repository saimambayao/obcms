#!/usr/bin/env python
"""
Environment Variable Validation Script for OBCMS Deployment

This script validates that all required environment variables are set correctly
before deployment to staging or production environments.

Usage:
    python scripts/validate_env.py [--env-file .env.staging]

Exit codes:
    0 - All validations passed
    1 - Critical validations failed
    2 - Warnings present (non-blocking)
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import urlparse


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class ValidationResult:
    """Result of an environment validation check."""
    def __init__(self, passed: bool, message: str, severity: str = "error"):
        self.passed = passed
        self.message = message
        self.severity = severity  # "error", "warning", "info"


class EnvValidator:
    """Validates environment variables for OBCMS deployment."""

    def __init__(self, env_file: str = None):
        self.env_file = env_file
        self.env_vars = {}
        self.errors = []
        self.warnings = []
        self.info = []

    def load_env_file(self):
        """Load environment variables from file if provided."""
        if not self.env_file:
            # Use system environment
            self.env_vars = dict(os.environ)
            print(f"{Colors.BLUE}Using system environment variables{Colors.END}\n")
            return

        env_path = Path(self.env_file)
        if not env_path.exists():
            print(f"{Colors.RED}Error: Environment file not found: {self.env_file}{Colors.END}")
            sys.exit(1)

        print(f"{Colors.BLUE}Loading environment from: {self.env_file}{Colors.END}\n")

        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        self.env_vars[key.strip()] = value.strip()

    def validate(self) -> bool:
        """Run all validation checks."""
        print(f"{Colors.BOLD}OBCMS Environment Validation{Colors.END}")
        print("=" * 70)
        print()

        # Run all validation methods
        self._validate_django_settings()
        self._validate_secret_key()
        self._validate_debug_mode()
        self._validate_allowed_hosts()
        self._validate_csrf_trusted_origins()
        self._validate_database()
        self._validate_redis()
        self._validate_email()
        self._validate_security_headers()
        self._validate_gunicorn()

        # Print results
        self._print_results()

        # Return overall status
        return len(self.errors) == 0

    def _validate_django_settings(self):
        """Validate DJANGO_SETTINGS_MODULE."""
        var = 'DJANGO_SETTINGS_MODULE'
        value = self.env_vars.get(var)

        if not value:
            self.errors.append(f"{var} is not set")
        elif value not in ['obc_management.settings.production', 'obc_management.settings.staging']:
            self.errors.append(f"{var} should be 'obc_management.settings.production' or 'staging', got: {value}")
        else:
            self.info.append(f"✓ {var} = {value}")

    def _validate_secret_key(self):
        """Validate SECRET_KEY."""
        var = 'SECRET_KEY'
        value = self.env_vars.get(var)

        if not value:
            self.errors.append(f"{var} is not set - CRITICAL security issue!")
        elif len(value) < 50:
            self.errors.append(f"{var} is too short ({len(value)} chars). Minimum 50 characters required.")
        elif value == 'your-secret-key-here' or 'example' in value.lower() or 'test' in value.lower():
            self.errors.append(f"{var} appears to be a placeholder value. Generate unique key!")
        else:
            self.info.append(f"✓ {var} set (length: {len(value)} chars)")

    def _validate_debug_mode(self):
        """Validate DEBUG setting."""
        var = 'DEBUG'
        value = self.env_vars.get(var, '1')

        if value not in ['0', 'False', 'false', 'FALSE']:
            self.errors.append(f"{var} must be set to 0 or False in production! Current: {value}")
        else:
            self.info.append(f"✓ {var} = {value} (production mode)")

    def _validate_allowed_hosts(self):
        """Validate ALLOWED_HOSTS."""
        var = 'ALLOWED_HOSTS'
        value = self.env_vars.get(var)

        if not value:
            self.errors.append(f"{var} is not set")
            return

        hosts = [h.strip() for h in value.split(',')]

        if not hosts or hosts == ['']:
            self.errors.append(f"{var} is empty")
        elif 'example.com' in value or 'yourdomain' in value.lower():
            self.warnings.append(f"{var} contains placeholder values: {value}")
        else:
            self.info.append(f"✓ {var} configured with {len(hosts)} host(s)")
            for host in hosts[:3]:  # Show first 3
                self.info.append(f"  - {host}")

    def _validate_csrf_trusted_origins(self):
        """Validate CSRF_TRUSTED_ORIGINS."""
        var = 'CSRF_TRUSTED_ORIGINS'
        value = self.env_vars.get(var)

        if not value:
            self.errors.append(f"{var} is not set")
            return

        origins = [o.strip() for o in value.split(',')]

        for origin in origins:
            if not origin.startswith(('http://', 'https://')):
                self.errors.append(f"{var} must include scheme (http:// or https://). Invalid: {origin}")

        if 'example.com' in value:
            self.warnings.append(f"{var} contains placeholder 'example.com'")
        elif len(origins) > 0:
            self.info.append(f"✓ {var} configured with {len(origins)} origin(s)")

    def _validate_database(self):
        """Validate DATABASE_URL."""
        var = 'DATABASE_URL'
        value = self.env_vars.get(var)

        if not value:
            self.errors.append(f"{var} is not set")
            return

        try:
            parsed = urlparse(value)

            if parsed.scheme == 'sqlite':
                self.warnings.append(f"{var} using SQLite - PostgreSQL recommended for production")
            elif parsed.scheme in ['postgres', 'postgresql']:
                self.info.append(f"✓ {var} configured for PostgreSQL")

                # Check for default/weak passwords
                if parsed.password:
                    if len(parsed.password) < 12:
                        self.warnings.append(f"Database password is short ({len(parsed.password)} chars). Recommend 20+ characters.")
                    if parsed.password in ['password', 'postgres', 'admin']:
                        self.errors.append(f"Database password is weak/default. Use strong random password!")
            else:
                self.warnings.append(f"{var} using unknown scheme: {parsed.scheme}")

        except Exception as e:
            self.errors.append(f"{var} is malformed: {e}")

    def _validate_redis(self):
        """Validate REDIS_URL."""
        var = 'REDIS_URL'
        value = self.env_vars.get(var)

        if not value:
            self.warnings.append(f"{var} is not set - caching and Celery will not work")
            return

        try:
            parsed = urlparse(value)
            if parsed.scheme != 'redis':
                self.errors.append(f"{var} should use redis:// scheme, got: {parsed.scheme}")
            else:
                self.info.append(f"✓ {var} configured")
        except Exception as e:
            self.errors.append(f"{var} is malformed: {e}")

    def _validate_email(self):
        """Validate email configuration."""
        backend = self.env_vars.get('EMAIL_BACKEND')

        if not backend:
            self.warnings.append("EMAIL_BACKEND not set")
            return

        if 'console' in backend.lower():
            self.errors.append("EMAIL_BACKEND is console backend - not allowed in production!")
        elif 'smtp' in backend.lower():
            self.info.append(f"✓ EMAIL_BACKEND configured for SMTP")

            # Check SMTP settings
            required_smtp = ['EMAIL_HOST', 'EMAIL_PORT', 'EMAIL_HOST_USER']
            missing_smtp = [var for var in required_smtp if not self.env_vars.get(var)]

            if missing_smtp:
                self.warnings.append(f"SMTP backend but missing: {', '.join(missing_smtp)}")

    def _validate_security_headers(self):
        """Validate security header settings."""
        secure_ssl = self.env_vars.get('SECURE_SSL_REDIRECT', '1')
        if secure_ssl not in ['1', 'True', 'true']:
            self.warnings.append(f"SECURE_SSL_REDIRECT should be enabled in production")
        else:
            self.info.append(f"✓ SSL redirect enabled")

        hsts_seconds = self.env_vars.get('SECURE_HSTS_SECONDS', '0')
        try:
            hsts_val = int(hsts_seconds)
            if hsts_val < 3600:
                self.warnings.append(f"SECURE_HSTS_SECONDS is low ({hsts_val}). Recommend 31536000 (1 year)")
            else:
                self.info.append(f"✓ HSTS configured ({hsts_val} seconds)")
        except ValueError:
            self.warnings.append(f"SECURE_HSTS_SECONDS is not a number: {hsts_seconds}")

    def _validate_gunicorn(self):
        """Validate Gunicorn configuration."""
        workers = self.env_vars.get('GUNICORN_WORKERS')

        if workers:
            try:
                worker_count = int(workers)
                if worker_count < 2:
                    self.warnings.append(f"GUNICORN_WORKERS is low ({worker_count}). Recommend (2 × CPU cores) + 1")
                elif worker_count > 20:
                    self.warnings.append(f"GUNICORN_WORKERS is high ({worker_count}). May cause memory issues.")
                else:
                    self.info.append(f"✓ Gunicorn workers = {worker_count}")
            except ValueError:
                self.errors.append(f"GUNICORN_WORKERS is not a number: {workers}")
        else:
            self.info.append("  GUNICORN_WORKERS not set (will use defaults)")

    def _print_results(self):
        """Print validation results."""
        print()
        print("=" * 70)
        print(f"{Colors.BOLD}Validation Results{Colors.END}")
        print("=" * 70)
        print()

        # Print errors
        if self.errors:
            print(f"{Colors.RED}{Colors.BOLD}✗ ERRORS ({len(self.errors)}):{Colors.END}")
            for error in self.errors:
                print(f"  {Colors.RED}✗ {error}{Colors.END}")
            print()

        # Print warnings
        if self.warnings:
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠ WARNINGS ({len(self.warnings)}):{Colors.END}")
            for warning in self.warnings:
                print(f"  {Colors.YELLOW}⚠ {warning}{Colors.END}")
            print()

        # Print info
        if self.info:
            print(f"{Colors.GREEN}{Colors.BOLD}✓ PASSED CHECKS ({len(self.info)}):{Colors.END}")
            for info_msg in self.info:
                print(f"  {Colors.GREEN}{info_msg}{Colors.END}")
            print()

        # Final summary
        print("=" * 70)
        if not self.errors and not self.warnings:
            print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL VALIDATIONS PASSED{Colors.END}")
            print(f"{Colors.GREEN}Environment is ready for deployment!{Colors.END}")
        elif not self.errors:
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠ PASSED WITH WARNINGS{Colors.END}")
            print(f"{Colors.YELLOW}Review warnings before deployment{Colors.END}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}✗ VALIDATION FAILED{Colors.END}")
            print(f"{Colors.RED}Fix errors before deployment!{Colors.END}")
        print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Validate OBCMS deployment environment variables')
    parser.add_argument('--env-file', help='Path to .env file (optional, uses system env if not provided)')
    parser.add_argument('--quiet', action='store_true', help='Only show errors')

    args = parser.parse_args()

    validator = EnvValidator(env_file=args.env_file)
    validator.load_env_file()

    passed = validator.validate()

    # Exit with appropriate code
    if not passed:
        sys.exit(1)
    elif validator.warnings:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
