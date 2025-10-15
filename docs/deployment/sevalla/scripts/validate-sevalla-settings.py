#!/usr/bin/env python3
"""
Sevalla Settings Validation Script

Validates Django settings for Sevalla deployment.
Usage: python validate-sevalla-settings.py [--settings-path PATH]

Example:
    python validate-sevalla-settings.py
    python validate-sevalla-settings.py --settings-path /app/src/obc_management/settings/sevalla.py
"""

import os
import sys
import argparse
import re
from pathlib import Path

def validate_secret_key(secret_key):
    """Validate Django SECRET_KEY strength."""
    if not secret_key:
        return False, "SECRET_KEY is empty"
    
    if len(secret_key) < 50:
        return False, "SECRET_KEY should be at least 50 characters"
    
    # Check for weak/default patterns
    weak_patterns = [
        'django-insecure',
        'test',
        'dev',
        'sample',
        'example',
        'localhost'
    ]
    
    for pattern in weak_patterns:
        if pattern.lower() in secret_key.lower():
            return False, f"SECRET_KEY contains weak pattern: {pattern}"
    
    return True, "SECRET_KEY is strong"

def validate_database_url(database_url):
    """Validate DATABASE_URL format."""
    if not database_url:
        return False, "DATABASE_URL is empty"
    
    # Check PostgreSQL URL format
    postgres_pattern = r'^postgres://([^:]+):([^@]+)@([^:]+):(\d+)/([^/]+)$'
    match = re.match(postgres_pattern, database_url)
    
    if not match:
        return False, "DATABASE_URL should be in format: postgres://user:password@host:port/database"
    
    user, password, host, port, database = match.groups()
    
    # Validate components
    if not user or not password or not host:
        return False, "DATABASE_URL missing required components (user, password, host)"
    
    try:
        port_int = int(port)
        if port_int < 1 or port_int > 65535:
            return False, f"DATABASE_URL port {port} is out of valid range (1-65535)"
    except ValueError:
        return False, f"DATABASE_URL port '{port}' is not a valid number"
    
    return True, "DATABASE_URL format is valid"

def validate_redis_url(redis_url):
    """Validate REDIS_URL format."""
    if not redis_url:
        return False, "REDIS_URL is empty"
    
    # Check Redis URL format
    redis_pattern = r'^redis://(:?([^@]+)@)?([^:]+):(\d+)/(\d+)$'
    match = re.match(redis_pattern, redis_url)
    
    if not match:
        return False, "REDIS_URL should be in format: redis://[:password@]host:port/database"
    
    password, host, port, database = match.groups()
    
    # Validate components
    if not host:
        return False, "REDIS_URL missing host"
    
    try:
        port_int = int(port)
        if port_int < 1 or port_int > 65535:
            return False, f"REDIS_URL port {port} is out of valid range (1-65535)"
    except ValueError:
        return False, f"REDIS_URL port '{port}' is not a valid number"
    
    return True, "REDIS_URL format is valid"

def validate_aws_credentials(access_key, secret_key, bucket_name, endpoint_url):
    """Validate AWS/S3 credentials for Sevalla storage."""
    errors = []
    
    if not access_key:
        errors.append("AWS_ACCESS_KEY_ID is empty")
    
    if not secret_key:
        errors.append("AWS_SECRET_ACCESS_KEY is empty")
    
    if not bucket_name:
        errors.append("AWS_STORAGE_BUCKET_NAME is empty")
    else:
        # Basic bucket name validation
        if len(bucket_name) < 3 or len(bucket_name) > 63:
            errors.append("AWS_STORAGE_BUCKET_NAME should be 3-63 characters")
        
        if not re.match(r'^[a-z0-9.-]+$', bucket_name.lower()):
            errors.append("AWS_STORAGE_BUCKET_NAME should contain only lowercase letters, numbers, dots, and hyphens")
    
    if not endpoint_url:
        errors.append("AWS_S3_ENDPOINT_URL is empty")
    else:
        if not endpoint_url.startswith(('http://', 'https://')):
            errors.append("AWS_S3_ENDPOINT_URL should start with http:// or https://")
    
    return len(errors) == 0, "; ".join(errors) if errors else "AWS credentials are valid"

def validate_allowed_hosts(allowed_hosts):
    """Validate ALLOWED_HOSTS configuration."""
    if not allowed_hosts:
        return False, "ALLOWED_HOSTS is empty"
    
    if isinstance(allowed_hosts, str):
        hosts = [host.strip() for host in allowed_hosts.split(',')]
    else:
        hosts = allowed_hosts
    
    if not hosts:
        return False, "ALLOWED_HOSTS contains no valid hosts"
    
    valid_patterns = []
    for host in hosts:
        host = host.strip()
        if not host:
            continue
        
        # Check for valid patterns
        if host == '*':
            valid_patterns.append(host)
        elif host.startswith('*.'):
            valid_patterns.append(host)
        elif re.match(r'^[a-zA-Z0-9.-]+$', host):
            valid_patterns.append(host)
        else:
            return False, f"Invalid host pattern: {host}"
    
    if not valid_patterns:
        return False, "No valid ALLOWED_HOSTS patterns found"
    
    return True, f"ALLOWED_HOSTS configured: {', '.join(valid_patterns[:3])}{'...' if len(valid_patterns) > 3 else ''}"

def validate_django_settings(settings_path):
    """Validate Django settings file for Sevalla deployment."""
    try:
        # Import the settings module
        sys.path.insert(0, str(Path(settings_path).parent.parent))
        module_name = Path(settings_path).stem
        
        spec = __import__(module_name)
        
        # Get required settings
        required_settings = {
            'SECRET_KEY': None,
            'DATABASE_URL': None,
            'REDIS_URL': None,
            'AWS_ACCESS_KEY_ID': None,
            'AWS_SECRET_ACCESS_KEY': None,
            'AWS_STORAGE_BUCKET_NAME': None,
            'AWS_S3_ENDPOINT_URL': None,
            'ALLOWED_HOSTS': None,
            'DEBUG': None,
            'DJANGO_SETTINGS_MODULE': None,
        }
        
        for setting in required_settings:
            if hasattr(spec, setting):
                required_settings[setting] = getattr(spec, setting)
        
        # Validate each setting
        results = []
        
        # Validate SECRET_KEY
        valid, message = validate_secret_key(required_settings['SECRET_KEY'])
        results.append(('SECRET_KEY', valid, message))
        
        # Validate DATABASE_URL
        valid, message = validate_database_url(required_settings['DATABASE_URL'])
        results.append(('DATABASE_URL', valid, message))
        
        # Validate REDIS_URL
        valid, message = validate_redis_url(required_settings['REDIS_URL'])
        results.append(('REDIS_URL', valid, message))
        
        # Validate AWS credentials
        valid, message = validate_aws_credentials(
            required_settings['AWS_ACCESS_KEY_ID'],
            required_settings['AWS_SECRET_ACCESS_KEY'],
            required_settings['AWS_STORAGE_BUCKET_NAME'],
            required_settings['AWS_S3_ENDPOINT_URL']
        )
        results.append(('AWS Credentials', valid, message))
        
        # Validate ALLOWED_HOSTS
        valid, message = validate_allowed_hosts(required_settings['ALLOWED_HOSTS'])
        results.append(('ALLOWED_HOSTS', valid, message))
        
        # Validate DEBUG setting
        debug_value = required_settings['DEBUG']
        debug_valid = not debug_value  # DEBUG should be False in production
        debug_message = "DEBUG is correctly set to False" if not debug_value else "WARNING: DEBUG should be False in production"
        results.append(('DEBUG Setting', debug_valid, debug_message))
        
        # Validate DJANGO_SETTINGS_MODULE
        settings_module = required_settings['DJANGO_SETTINGS_MODULE']
        if settings_module:
            settings_valid = 'sevalla' in settings_module.lower() or 'production' in settings_module.lower()
            settings_message = f"DJANGO_SETTINGS_MODULE: {settings_module}"
            results.append(('Settings Module', settings_valid, settings_message))
        
        return results
        
    except ImportError as e:
        return [('Import Error', False, f"Failed to import settings: {e}")]
    except Exception as e:
        return [('Error', False, f"Validation error: {e}")")

def print_results(results):
    """Print validation results in a formatted way."""
    print("\n" + "="*60)
    print("     OBCMS Sevalla Settings Validation Results")
    print("="*60)
    
    all_valid = True
    for setting, valid, message in results:
        status = "✅ PASS" if valid else "❌ FAIL"
        print(f"{status:<8} {setting:<18} {message}")
        if not valid:
            all_valid = False
    
    print("="*60)
    
    if all_valid:
        print("🎉 All settings are valid for Sevalla deployment!")
    else:
        print("⚠️  Some settings need attention before deployment.")
    
    print("="*60)
    
    return all_valid

def main():
    parser = argparse.ArgumentParser(description='Validate OBCMS settings for Sevalla deployment')
    parser.add_argument(
        '--settings-path', 
        type=str, 
        default='src/obc_management/settings/sevalla.py',
        help='Path to Django settings file'
    )
    
    args = parser.parse_args()
    
    # Check if settings file exists
    settings_path = Path(args.settings_path)
    if not settings_path.exists():
        print(f"❌ Settings file not found: {args.settings_path}")
        sys.exit(1)
    
    # Validate settings
    results = validate_django_settings(args.settings_path)
    
    # Print results
    success = print_results(results)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
