"""
Tests for health check endpoints.

Tests the liveness and readiness probes used by Docker/Kubernetes orchestration.
"""

import json
from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache


class HealthEndpointTests(TestCase):
    """Test health check endpoints functionality."""

    def test_liveness_endpoint(self):
        """Test the /live/ endpoint returns correct response."""
        response = self.client.get(reverse('liveness'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        data = json.loads(response.content)
        self.assertEqual(data, {'status': 'alive'})

    def test_readiness_endpoint_success(self):
        """Test the /ready/ endpoint returns success when all systems are ready."""
        response = self.client.get(reverse('readiness_probe'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        data = json.loads(response.content)
        self.assertIn('ready', data)
        self.assertIn('checks', data)
        self.assertIn('database', data['checks'])
        self.assertIn('cache', data['checks'])
        self.assertIn('migrations', data['checks'])

    def test_readiness_endpoint_structure(self):
        """Test the /ready/ endpoint returns the correct structure."""
        response = self.client.get(reverse('readiness_probe'))

        data = json.loads(response.content)

        # Check main structure
        self.assertIsInstance(data['ready'], bool)
        self.assertIsInstance(data['checks'], dict)

        # Check checks structure
        checks = data['checks']
        self.assertIsInstance(checks['database'], bool)
        self.assertIsInstance(checks['cache'], bool)
        self.assertIsInstance(checks['migrations'], bool)

    def test_cache_connectivity_check(self):
        """Test cache connectivity check function."""
        from obc_management.views.health import check_cache_connectivity

        # Set and get a test value
        cache.set('health_test', 'test_value', timeout=10)
        result = cache.get('health_test')
        cache.delete('health_test')

        # Should return True when cache is working
        self.assertTrue(result == 'test_value')

    def test_database_connectivity_check(self):
        """Test database connectivity check function."""
        from obc_management.views.health import check_database_connectivity

        # Should return True when database is accessible
        result = check_database_connectivity()
        self.assertIsInstance(result, bool)

    def test_migration_check(self):
        """Test migration check function."""
        from obc_management.views.health import check_pending_migrations

        # Should return True when migrations are up to date
        result = check_pending_migrations()
        self.assertIsInstance(result, bool)

    def test_endpoints_no_cache_headers(self):
        """Test that health endpoints have proper cache control."""
        # Test liveness endpoint
        response = self.client.get(reverse('liveness'))
        self.assertIn('Cache-Control', response)
        self.assertIn('no-store', response['Cache-Control'])

        # Test readiness endpoint
        response = self.client.get(reverse('readiness_probe'))
        self.assertIn('Cache-Control', response)
        self.assertIn('no-store', response['Cache-Control'])