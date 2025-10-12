"""
Pytest configuration for budget execution tests

Imports all fixtures and configures test environment.
"""

import pytest

# Import fixtures from both budget_preparation and budget_execution
pytest_plugins = [
    'budget_preparation.tests.fixtures.budget_data',
    'budget_execution.tests.fixtures.execution_data',
]


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
def authenticated_api_client(api_client, execution_user):
    """Provide authenticated API client."""
    api_client.force_authenticate(user=execution_user)
    return api_client
