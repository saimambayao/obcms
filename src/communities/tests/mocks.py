"""Mock geocoding services for testing.

This module provides mock implementations of geocoding services to speed up tests
by avoiding real API calls to Google Maps, ArcGIS, and Nominatim.
"""

from unittest.mock import MagicMock, patch
from typing import Optional, Tuple
from contextlib import contextmanager
from django.db.models.signals import post_save


class MockGeocoder:
    """Mock geocoding service that returns predictable coordinates based on location name."""

    @staticmethod
    def enhanced_ensure_location_coordinates(obj) -> Tuple[Optional[float], Optional[float], bool, str]:
        """
        Mock implementation of enhanced_ensure_location_coordinates.

        Returns predictable coordinates based on the object's name hash,
        ensuring consistency across test runs.

        Returns:
            (lat, lng, updated, source) where:
            - lat, lng: Mock coordinates based on object name
            - updated: Always False (pretend coordinates existed)
            - source: 'mock'
        """
        # Generate predictable coordinates based on object name
        name = getattr(obj, 'name', 'default')

        # Use hash to generate consistent but varied coordinates
        # Philippines approximate bounds: lat 4.5-21.5, lng 116-127
        hash_value = abs(hash(name))

        # Generate latitude between 6.0 and 20.0 (Philippines range)
        lat = 6.0 + (hash_value % 1400) / 100.0

        # Generate longitude between 119.0 and 127.0 (Philippines range)
        lng = 119.0 + ((hash_value >> 8) % 800) / 100.0

        # Update the object with mock coordinates (GeoJSON format: [lng, lat])
        if hasattr(obj, 'center_coordinates') and not obj.center_coordinates:
            obj.center_coordinates = [lng, lat]
            # Don't actually save to avoid triggering signals again
            # obj.save(update_fields=['center_coordinates'])

        return lat, lng, False, 'mock'

    @staticmethod
    def _geocode_with_google(query: str):
        """Mock Google geocoding - returns None to skip."""
        from common.services.enhanced_geocoding import GeocodeResult
        return GeocodeResult(None, None, "low", "google")

    @staticmethod
    def _geocode_with_arcgis(query: str):
        """Mock ArcGIS geocoding - returns mock coordinates."""
        from common.services.enhanced_geocoding import GeocodeResult

        # Generate predictable coordinates from query
        hash_value = abs(hash(query))
        lat = 6.0 + (hash_value % 1400) / 100.0
        lng = 119.0 + ((hash_value >> 8) % 800) / 100.0

        return GeocodeResult(
            latitude=lat,
            longitude=lng,
            accuracy="high",
            source="arcgis",
            formatted_address=query,
            confidence=95.0,
            bounding_box=[lng - 0.1, lat - 0.1, lng + 0.1, lat + 0.1]
        )

    @staticmethod
    def _geocode_with_nominatim(query: str):
        """Mock Nominatim geocoding - returns None to skip."""
        from common.services.enhanced_geocoding import GeocodeResult
        return GeocodeResult(None, None, "low", "nominatim")


@contextmanager
def mock_geocoding():
    """
    Context manager to mock geocoding API calls in tests.

    This patches all geocoding providers to return instant mock responses
    instead of making real API calls, providing massive performance improvements.

    Usage:
        with mock_geocoding():
            # Your test code here
            municipality = Municipality.objects.create(...)
    """
    # Patch all three geocoding providers
    with patch('common.services.enhanced_geocoding._geocode_with_google', side_effect=MockGeocoder._geocode_with_google), \
         patch('common.services.enhanced_geocoding._geocode_with_arcgis', side_effect=MockGeocoder._geocode_with_arcgis), \
         patch('common.services.enhanced_geocoding._geocode_with_nominatim', side_effect=MockGeocoder._geocode_with_nominatim):
        yield


def mock_geocoding_providers():
    """
    Context manager to mock individual geocoding providers.

    This patches the individual geocoding functions (_geocode_with_google, etc.)
    to avoid making real API calls.

    Usage:
        with mock_geocoding_providers():
            # Your test code here
            result = enhanced_geocode_location(obj)
    """
    patches = [
        patch(
            'common.services.enhanced_geocoding._geocode_with_google',
            side_effect=MockGeocoder._geocode_with_google
        ),
        patch(
            'common.services.enhanced_geocoding._geocode_with_arcgis',
            side_effect=MockGeocoder._geocode_with_arcgis
        ),
        patch(
            'common.services.enhanced_geocoding._geocode_with_nominatim',
            side_effect=MockGeocoder._geocode_with_nominatim
        ),
    ]

    # Return a context manager that manages all patches
    from contextlib import ExitStack
    return ExitStack().enter_context(*patches)
