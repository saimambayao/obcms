#!/usr/bin/env python3
"""
BMMS Environment Variable Validation Script

Validates .env files against required variables for different profiles
(development, staging, production).

Usage:
    python scripts/validate_env.py .env --profile staging
    python scripts/validate_env.py /path/to/.env --profile production
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Set
from urllib.parse import urlparse


# Required variables for each profile
REQUIRED_VARS = {
    "base": [
        "SECRET_KEY",
        "DATABASE_URL",
        "ALLOWED_HOSTS",
        "DJANGO_SETTINGS_MODULE",
    ],
    "development": [
        "SECRET_KEY",
        "DATABASE_URL",
    ],
    "staging": [
        "SECRET_KEY",
        "DATABASE_URL",
        "ALLOWED_HOSTS",
        "CSRF_TRUSTED_ORIGINS",
        "REDIS_URL",
        "CELERY_BROKER_URL",
        "DEFAULT_FROM_EMAIL",
        "BASE_URL",
    ],
    "production": [
        "SECRET_KEY",
        "DATABASE_URL",
        "ALLOWED_HOSTS",
        "CSRF_TRUSTED_ORIGINS",
        "REDIS_URL",
        "CELERY_BROKER_URL",
        "DEFAULT_FROM_EMAIL",
        "EMAIL_HOST",
        "EMAIL_HOST_USER",
        "EMAIL_HOST_PASSWORD",
        "BASE_URL",
        "SENTRY_DSN",
    ],
}

# Security validations
MIN_SECRET_KEY_LENGTH = 50
PLACEHOLDER_VALUES = [
    "your-secret-key-here",
    "your-password-here",
    "your-email@gmail.com",
    "your-app-password-here",
]


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def parse_env_file(file_path: Path) -> Dict[str, str]:
    """Parse .env file and return dictionary of variables"""
    env_vars = {}

    if not file_path.exists():
        raise ValidationError(f"File not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Parse KEY=VALUE
            if '=' in line:
                key, _, value = line.partition('=')
                key = key.strip()
                value = value.strip()

                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]

                env_vars[key] = value

    return env_vars


def validate_required_vars(env_vars: Dict[str, str], profile: str) -> List[str]:
    """Check if all required variables are present"""
    errors = []
    required = set(REQUIRED_VARS.get(profile, []))

    missing = required - set(env_vars.keys())
    if missing:
        errors.append(f"Missing required variables: {', '.join(sorted(missing))}")

    # Check for empty values
    empty = [key for key in required if key in env_vars and not env_vars[key].strip()]
    if empty:
        errors.append(f"Empty required variables: {', '.join(sorted(empty))}")

    return errors


def validate_secret_key(secret_key: str) -> List[str]:
    """Validate SECRET_KEY meets security requirements"""
    errors = []

    if len(secret_key) < MIN_SECRET_KEY_LENGTH:
        errors.append(
            f"SECRET_KEY too short ({len(secret_key)} chars, minimum {MIN_SECRET_KEY_LENGTH})"
        )

    if any(placeholder in secret_key for placeholder in PLACEHOLDER_VALUES):
        errors.append("SECRET_KEY contains placeholder value - generate a new one")

    return errors


def validate_database_url(db_url: str) -> List[str]:
    """Validate DATABASE_URL format"""
    errors = []

    try:
        parsed = urlparse(db_url)

        if not parsed.scheme:
            errors.append("DATABASE_URL missing scheme (e.g., postgresql://)")

        if parsed.scheme not in ['postgresql', 'postgres', 'sqlite']:
            errors.append(f"Unsupported DATABASE_URL scheme: {parsed.scheme}")

        if parsed.scheme in ['postgresql', 'postgres']:
            if not parsed.hostname:
                errors.append("DATABASE_URL missing hostname")
            if not parsed.path or parsed.path == '/':
                errors.append("DATABASE_URL missing database name")

    except Exception as e:
        errors.append(f"Invalid DATABASE_URL format: {e}")

    return errors


def validate_urls(env_vars: Dict[str, str]) -> List[str]:
    """Validate URL format for various settings"""
    errors = []

    # Validate BASE_URL
    if 'BASE_URL' in env_vars:
        base_url = env_vars['BASE_URL']
        if not base_url.startswith(('http://', 'https://')):
            errors.append("BASE_URL must start with http:// or https://")

    # Validate REDIS_URL
    if 'REDIS_URL' in env_vars:
        redis_url = env_vars['REDIS_URL']
        if not redis_url.startswith('redis://'):
            errors.append("REDIS_URL must start with redis://")

    return errors


def validate_email_settings(env_vars: Dict[str, str], profile: str) -> List[str]:
    """Validate email configuration"""
    errors = []

    if profile in ['staging', 'production']:
        if 'DEFAULT_FROM_EMAIL' in env_vars:
            from_email = env_vars['DEFAULT_FROM_EMAIL']
            if any(placeholder in from_email for placeholder in PLACEHOLDER_VALUES):
                errors.append("DEFAULT_FROM_EMAIL contains placeholder value")

        if 'EMAIL_HOST_USER' in env_vars:
            email_user = env_vars['EMAIL_HOST_USER']
            if any(placeholder in email_user for placeholder in PLACEHOLDER_VALUES):
                errors.append("EMAIL_HOST_USER contains placeholder value")

    return errors


def validate_security_settings(env_vars: Dict[str, str], profile: str) -> List[str]:
    """Validate security-related settings"""
    errors = []
    warnings = []

    if profile == 'production':
        # Check SSL redirect is enabled
        if env_vars.get('SECURE_SSL_REDIRECT', '').lower() != 'true':
            errors.append("SECURE_SSL_REDIRECT must be 'true' in production")

        # Check secure cookies
        if env_vars.get('SESSION_COOKIE_SECURE', '').lower() != 'true':
            errors.append("SESSION_COOKIE_SECURE must be 'true' in production")

        if env_vars.get('CSRF_COOKIE_SECURE', '').lower() != 'true':
            errors.append("CSRF_COOKIE_SECURE must be 'true' in production")

    return errors


def main():
    parser = argparse.ArgumentParser(
        description='Validate BMMS environment variables'
    )
    parser.add_argument(
        'env_file',
        type=Path,
        help='Path to .env file to validate'
    )
    parser.add_argument(
        '--profile',
        choices=['development', 'staging', 'production'],
        default='staging',
        help='Environment profile to validate against (default: staging)'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Treat warnings as errors'
    )

    args = parser.parse_args()

    print(f"Validating {args.env_file} for {args.profile} profile...")
    print("=" * 70)

    try:
        # Parse env file
        env_vars = parse_env_file(args.env_file)
        print(f"✓ Parsed {len(env_vars)} environment variables")

        all_errors = []
        all_warnings = []

        # Run validations
        all_errors.extend(validate_required_vars(env_vars, args.profile))

        if 'SECRET_KEY' in env_vars:
            all_errors.extend(validate_secret_key(env_vars['SECRET_KEY']))

        if 'DATABASE_URL' in env_vars:
            all_errors.extend(validate_database_url(env_vars['DATABASE_URL']))

        all_errors.extend(validate_urls(env_vars))
        all_errors.extend(validate_email_settings(env_vars, args.profile))
        all_errors.extend(validate_security_settings(env_vars, args.profile))

        # Print results
        print()
        if all_errors:
            print("ERRORS:")
            for error in all_errors:
                print(f"  ✗ {error}")

        if all_warnings:
            print("\nWARNINGS:")
            for warning in all_warnings:
                print(f"  ⚠ {warning}")

        print()
        print("=" * 70)

        if all_errors or (args.strict and all_warnings):
            print("❌ VALIDATION FAILED")
            return 1
        elif all_warnings:
            print("⚠️  VALIDATION PASSED WITH WARNINGS")
            return 0
        else:
            print("✅ VALIDATION PASSED")
            return 0

    except ValidationError as e:
        print(f"\n❌ VALIDATION ERROR: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
