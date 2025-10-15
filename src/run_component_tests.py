#!/usr/bin/env python
"""
Custom test runner for OBCMS component testing.
Bypasses pytest configuration issues and runs tests directly.
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.base')

# Setup Django
django.setup()

# Import pytest and run tests directly
import pytest

if __name__ == "__main__":
    # Get test modules from command line arguments
    test_args = sys.argv[1:] if len(sys.argv) > 1 else [
        'organizations/tests/test_models.py',
        'organizations/tests/test_data_isolation.py',
        'common/tests/',
    ]

    # Run pytest with minimal configuration
    exit_code = pytest.main([
        '-v',
        '--tb=short',
        '--no-cov',
        '-p', 'no:django',
    ] + test_args)

    sys.exit(exit_code)