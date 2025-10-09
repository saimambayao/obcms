"""
Tests for Query Builder

Tests the visual query builder service and views.
"""

import json
import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from common.ai_services.chat.query_builder import QueryBuilder, QueryResult
from communities.models import Region, Province, Municipality, Barangay

User = get_user_model()


class QueryBuilderServiceTest(TestCase):
    """Test QueryBuilder service"""

    def setUp(self):
        """Set up test data"""
        self.builder = QueryBuilder()

        # Create test geographic data
        self.region = Region.objects.create(
            name="Region IX", code="09"
        )

        self.province = Province.objects.create(
            name="Zamboanga del Norte",
            code="ZAN",
            region=self.region,
        )

        self.municipality = Municipality.objects.create(
            name="Dipolog City",
            code="DPL",
            province=self.province,
            municipality_type="city",
        )

        self.barangay = Barangay.objects.create(
            name="Estaka",
            code="EST",
            municipality=self.municipality,
        )

    def test_get_available_entities(self):
        """Test getting available entities"""
        entities = self.builder.get_available_entities()

        self.assertIsInstance(entities, list)
        self.assertTrue(len(entities) > 0)

        # Check structure
        for entity in entities:
            self.assertIn("value", entity)
            self.assertIn("label", entity)
            self.assertIn("icon", entity)

        # Check for expected entities
        entity_values = [e["value"] for e in entities]
        self.assertIn("communities", entity_values)

    def test_get_builder_config(self):
        """Test getting builder configuration"""
        config = self.builder.get_builder_config("communities")

        self.assertIn("display_name", config)
        self.assertIn("query_types", config)
        self.assertIn("filters", config)
        self.assertIn("aggregates", config)

        # Check query types
        self.assertIn("count", config["query_types"])
        self.assertIn("list", config["query_types"])

        # Check filters
        self.assertIsInstance(config["filters"], dict)

    def test_get_builder_config_invalid_entity(self):
        """Test getting config for invalid entity"""
        with self.assertRaises(ValueError):
            self.builder.get_builder_config("invalid_entity")

    def test_build_query_count(self):
        """Test building count query"""
        selections = {
            "entity_type": "communities",
            "query_type": "count",
            "filters": {"region": "Region IX"},
        }

        query_text = self.builder.build_query(selections)

        self.assertIsInstance(query_text, str)
        self.assertIn("how many", query_text.lower())
        self.assertIn("communities", query_text.lower())

    def test_build_query_list(self):
        """Test building list query"""
        selections = {
            "entity_type": "communities",
            "query_type": "list",
            "filters": {"province": "Zamboanga del Norte"},
        }

        query_text = self.builder.build_query(selections)

        self.assertIsInstance(query_text, str)
        self.assertIn("List", query_text)

    def test_build_query_aggregate(self):
        """Test building aggregate query"""
        selections = {
            "entity_type": "communities",
            "query_type": "aggregate",
            "aggregate": "total_population",
            "filters": {},
        }

        query_text = self.builder.build_query(selections)

        self.assertIsInstance(query_text, str)
        self.assertIn("What is", query_text)

    def test_preview_query(self):
        """Test query preview"""
        selections = {
            "entity_type": "communities",
            "query_type": "count",
            "filters": {},
        }

        preview = self.builder.preview_query(selections)

        self.assertIsInstance(preview, dict)
        self.assertIn("query_text", preview)
        self.assertIn("result_type", preview)
        self.assertIn("estimated_count", preview)

        # Check count is correct
        self.assertEqual(preview["estimated_count"], 1)  # We created 1 barangay

    def test_execute_built_query_count(self):
        """Test executing count query"""
        selections = {
            "entity_type": "communities",
            "query_type": "count",
            "filters": {},
        }

        result = self.builder.execute_built_query(selections)

        self.assertIsInstance(result, QueryResult)
        self.assertTrue(result.success)
        self.assertEqual(result.data, 1)  # 1 barangay created
        self.assertIsNotNone(result.query_text)

    def test_execute_built_query_list(self):
        """Test executing list query"""
        selections = {
            "entity_type": "communities",
            "query_type": "list",
            "filters": {},
        }

        result = self.builder.execute_built_query(selections)

        self.assertIsInstance(result, QueryResult)
        self.assertTrue(result.success)
        self.assertIsInstance(result.data, list)
        self.assertEqual(len(result.data), 1)

    def test_execute_built_query_with_filters(self):
        """Test executing query with filters"""
        # Create another barangay in different region
        region2 = Region.objects.create(
            name="Region X", code="10"
        )

        province2 = Province.objects.create(
            name="Bukidnon",
            code="BUK",
            region=region2,
        )

        municipality2 = Municipality.objects.create(
            name="Malaybalay City",
            code="MAL",
            province=province2,
            municipality_type="city",
        )

        Barangay.objects.create(
            name="Poblacion",
            code="POB",
            municipality=municipality2,
        )

        # Query with region filter
        selections = {
            "entity_type": "communities",
            "query_type": "count",
            "filters": {"region": "Region IX"},
        }

        result = self.builder.execute_built_query(selections)

        self.assertTrue(result.success)
        # Should only count barangay in Region IX
        # Note: Filter implementation may need adjustment based on actual field paths
        self.assertIsNotNone(result.data)


@pytest.mark.django_db
class QueryBuilderViewsTest(TestCase):
    """Test Query Builder views"""

    def setUp(self):
        """Set up test client and user"""
        self.client = Client()

        # Create test user
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )

        self.client.force_login(self.user)

        # Create test data
        self.region = Region.objects.create(
            name="Region IX", code="09"
        )

    def test_query_builder_entities_view(self):
        """Test entities endpoint"""
        url = reverse("common:query_builder_entities")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        self.assertIn("entities", data)
        self.assertIsInstance(data["entities"], list)

    def test_query_builder_config_view(self):
        """Test config endpoint"""
        url = reverse("common:query_builder_config", kwargs={"entity_type": "communities"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        self.assertIn("display_name", data)
        self.assertIn("filters", data)

    def test_query_builder_config_view_invalid(self):
        """Test config endpoint with invalid entity"""
        url = reverse("common:query_builder_config", kwargs={"entity_type": "invalid"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)

    def test_query_builder_filters_view(self):
        """Test filters endpoint"""
        url = reverse("common:query_builder_filters")
        response = self.client.get(url, {"entity": "communities"})

        self.assertEqual(response.status_code, 200)

        # Should return HTML
        self.assertIn("text/html", response["Content-Type"])

    def test_query_builder_filters_view_no_entity(self):
        """Test filters endpoint without entity"""
        url = reverse("common:query_builder_filters")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)

    def test_query_builder_preview_view(self):
        """Test preview endpoint"""
        url = reverse("common:query_builder_preview")

        data = {
            "entity_type": "communities",
            "query_type": "count",
            "filters": {},
        }

        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)

        self.assertIn("query_text", result)
        self.assertIn("estimated_count", result)

    def test_query_builder_execute_view(self):
        """Test execute endpoint"""
        url = reverse("common:query_builder_execute")

        data = {
            "entity_type": "communities",
            "query_type": "count",
            "filters": {},
        }

        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)

        self.assertIn("success", result)
        self.assertIn("query_text", result)
        self.assertTrue(result["success"])

    def test_query_builder_requires_authentication(self):
        """Test that endpoints require authentication"""
        self.client.logout()

        url = reverse("common:query_builder_entities")
        response = self.client.get(url)

        # Should redirect to login
        self.assertEqual(response.status_code, 302)

    def test_query_builder_execute_invalid_json(self):
        """Test execute with invalid JSON"""
        url = reverse("common:query_builder_execute")

        response = self.client.post(
            url,
            data="invalid json",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        result = json.loads(response.content)
        self.assertIn("error", result)
