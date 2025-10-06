"""Pytest fixtures for communities tests."""

import pytest
from unittest.mock import patch
from .mocks import MockGeocoder


@pytest.fixture(autouse=True)
def mock_geocoding_for_all_tests():
    """
    Automatically mock geocoding for all tests in the communities app.

    This fixture is autouse=True, so it runs for every test automatically.
    """
    with patch('common.services.enhanced_geocoding._geocode_with_google', side_effect=MockGeocoder._geocode_with_google), \
         patch('common.services.enhanced_geocoding._geocode_with_arcgis', side_effect=MockGeocoder._geocode_with_arcgis), \
         patch('common.services.enhanced_geocoding._geocode_with_nominatim', side_effect=MockGeocoder._geocode_with_nominatim):
        yield
