"""
Pytest configuration for budget preparation tests

Imports all fixtures and configures test environment.
"""

import pytest
import sys
from pathlib import Path

# Import all fixtures from fixtures module
pytest_plugins = [
    'budget_preparation.tests.fixtures.budget_data',
]

# Configure Django for tests
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'budget_preparation',
            'budget_execution',
            'planning',
            'monitoring',
            'coordination',
            'common',
        ],
        USE_TZ=True,
    )
    django.setup()


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests automatically."""
    pass


@pytest.fixture
def api_client():
    """Provide DRF API client for API tests."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client, test_user):
    """Provide authenticated API client."""
    api_client.force_authenticate(user=test_user)
    return api_client
