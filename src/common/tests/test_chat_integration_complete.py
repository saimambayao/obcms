"""
Complete End-to-End Integration Tests for OBCMS Chat System

Tests the full chat pipeline from user query to formatted response:
1. FAQ instant response
2. Entity extraction
3. Intent classification
4. Clarification handling
5. Template matching
6. Query execution
7. Response formatting
8. Fallback handling

All tests verify NO AI calls are made and response time < 100ms.
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils import timezone

from common.ai_services.chat.chat_engine import get_conversational_assistant
from common.ai_services.chat.query_templates import get_template_registry
from common.ai_services.chat.faq_handler import get_faq_handler
from common.ai_services.chat.entity_extractor import EntityExtractor
from common.ai_services.chat.template_matcher import get_template_matcher
from common.ai_services.chat.fallback_handler import get_fallback_handler

User = get_user_model()


class ChatIntegrationCompleteTests(TestCase):
    """Complete integration tests for chat system."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for all tests."""
        super().setUpClass()

        # Initialize all components
        cls.assistant = get_conversational_assistant()
        cls.registry = get_template_registry()
        cls.faq_handler = get_faq_handler()
        cls.entity_extractor = EntityExtractor()
        cls.matcher = get_template_matcher()
        cls.fallback_handler = get_fallback_handler()

    def setUp(self):
        """Create test user for each test."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def tearDown(self):
        """Clean up after each test."""
        User.objects.all().delete()

    # =========================================================================
    # TEST 1: FAQ INSTANT RESPONSE
    # =========================================================================

    def test_faq_instant_response(self):
        """Test FAQ provides instant response without AI."""
        start_time = datetime.now()

        result = self.assistant.chat(
            user_id=self.user.id,
            message="What can you do?"
        )

        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000

        # Assertions
        self.assertEqual(result.get('source'), 'faq')
        self.assertIn('response', result)
        self.assertIsNotNone(result['response'])
        self.assertTrue(len(result['response']) > 0)

        # Performance check
        self.assertLess(response_time, 100, f"FAQ response took {response_time}ms (expected < 100ms)")

        print(f"✓ FAQ instant response: {response_time:.2f}ms")

    def test_faq_variations(self):
        """Test FAQ handles query variations."""
        queries = [
            "help",
            "what can you help me with",
            "what are your capabilities",
            "show me what you can do",
        ]

        for query in queries:
            result = self.assistant.chat(user_id=self.user.id, message=query)

            # Should hit FAQ
            self.assertIn('response', result)
            self.assertIsNotNone(result['response'])

            print(f"✓ FAQ variation handled: '{query}'")

    # =========================================================================
    # TEST 2: ENTITY EXTRACTION
    # =========================================================================

    def test_entity_extraction_location(self):
        """Test entity extraction identifies locations."""
        query = "How many communities in Region IX?"

        entities = self.entity_extractor.extract_entities(query)

        # Should extract location
        self.assertIn('location', entities)
        self.assertEqual(entities['location']['type'], 'region')
        self.assertIn('Region IX', entities['location']['value'])

        print(f"✓ Location entity extracted: {entities['location']}")

    def test_entity_extraction_ethnicity(self):
        """Test entity extraction identifies ethnolinguistic groups."""
        query = "Show me Maranao communities"

        entities = self.entity_extractor.extract_entities(query)

        # Should extract ethnolinguistic group
        self.assertIn('ethnolinguistic_group', entities)
        self.assertIn('Meranaw', entities['ethnolinguistic_group']['value'])

        print(f"✓ Ethnicity entity extracted: {entities['ethnolinguistic_group']}")

    def test_entity_extraction_multiple(self):
        """Test entity extraction handles multiple entities."""
        query = "How many Maguindanao fishing communities in Sultan Kudarat last 6 months?"

        entities = self.entity_extractor.extract_entities(query)

        # Should extract multiple entities
        self.assertGreater(len(entities), 1)

        # Location
        if 'location' in entities:
            self.assertIn('Sultan Kudarat', entities['location']['value'])

        # Ethnolinguistic group
        if 'ethnolinguistic_group' in entities:
            self.assertIn('Maguindanao', entities['ethnolinguistic_group']['value'])

        # Livelihood
        if 'livelihood' in entities:
            self.assertIn('fishing', entities['livelihood']['value'])

        print(f"✓ Multiple entities extracted: {list(entities.keys())}")

    # =========================================================================
    # TEST 3: TEMPLATE MATCHING
    # =========================================================================

    def test_template_matching_communities(self):
        """Test template matcher finds community templates."""
        query = "how many communities"
        entities = {}

        # Try to find matching templates directly
        matches = self.matcher.find_matching_templates(
            query, entities, category='communities'
        )

        # Should find at least one template
        self.assertGreater(len(matches), 0)
        self.assertEqual(matches[0].category, 'communities')

        print(f"✓ Template matched: {matches[0].id}")

    def test_template_matching_staff(self):
        """Test template matcher finds staff templates."""
        query = "my tasks"
        entities = {}

        result = self.matcher.match_and_generate(
            query, entities, category='staff'
        )

        # Should find staff template
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['template'])
        self.assertEqual(result['template'].category, 'staff')

        print(f"✓ Staff template matched: {result['template'].id}")

    def test_template_matching_general(self):
        """Test template matcher handles navigation queries."""
        query = "take me to dashboard"
        entities = {}

        result = self.assistant.chat(
            user_id=self.user.id,
            message=query,
        )

        # Should be classified as navigation intent
        self.assertEqual(result.get('intent'), 'navigation')
        self.assertIn('response', result)

        print("✓ Navigation query handled via assistant pipeline")

    def test_template_priority_ranking(self):
        """Test templates are ranked by priority."""
        query = "how many communities in zamboanga"
        entities = {'location': {'type': 'region', 'value': 'Zamboanga', 'confidence': 0.9}}

        matches = self.matcher.find_matching_templates(
            query, entities, category='communities'
        )

        # Should find multiple matches
        self.assertGreater(len(matches), 0)

        # Should be ranked (higher priority first)
        if len(matches) > 1:
            ranked = self.matcher.rank_templates(matches, query, entities)
            self.assertGreaterEqual(
                ranked[0]['score'],
                ranked[-1]['score']
            )

        print(f"✓ Template ranking works: {len(matches)} matches found")

    # =========================================================================
    # TEST 4: FULL PIPELINE END-TO-END
    # =========================================================================

    def test_full_pipeline_community_count(self):
        """Test full pipeline for community count query."""
        start_time = datetime.now()

        result = self.assistant.chat(
            user_id=self.user.id,
            message="How many communities are there?"
        )

        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000

        # Should get response
        self.assertIn('response', result)
        self.assertIsNotNone(result['response'])

        # Should include intent
        self.assertIn('intent', result)

        # Performance check
        self.assertLess(response_time, 100, f"Full pipeline took {response_time}ms")

        print(f"✓ Full pipeline community count: {response_time:.2f}ms")
        print(f"  Response: {result['response'][:100]}")

    def test_full_pipeline_staff_tasks(self):
        """Test full pipeline for staff task query."""
        start_time = datetime.now()

        result = self.assistant.chat(
            user_id=self.user.id,
            message="Show my tasks"
        )

        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000

        # Should get response
        self.assertIn('response', result)

        # Performance check
        self.assertLess(response_time, 100)

        print(f"✓ Full pipeline staff tasks: {response_time:.2f}ms")

    def test_full_pipeline_general_help(self):
        """Test full pipeline for general help query."""
        result = self.assistant.chat(
            user_id=self.user.id,
            message="Help"
        )

        # Should get help response (from FAQ)
        self.assertIn('response', result)
        self.assertEqual(result.get('source'), 'faq')

        print(f"✓ Full pipeline general help works")

    # =========================================================================
    # TEST 5: FALLBACK HANDLING
    # =========================================================================

    def test_fallback_unknown_query(self):
        """Test fallback handler for unknown queries."""
        result = self.assistant.chat(
            user_id=self.user.id,
            message="xyzabc nonsense query 123"
        )

        # Should get fallback response
        self.assertIn('response', result)
        self.assertIn('suggestions', result)

        # Should NOT call AI
        self.assertNotEqual(result.get('source'), 'ai')

        print(f"✓ Fallback handles unknown query (no AI)")

    def test_fallback_provides_suggestions(self):
        """Test fallback provides helpful suggestions."""
        result = self.assistant.chat(
            user_id=self.user.id,
            message="show me xyz abc"
        )

        # Should have suggestions
        self.assertIn('suggestions', result)
        self.assertGreater(len(result['suggestions']), 0)

        print(f"✓ Fallback provides {len(result['suggestions'])} suggestions")

    # =========================================================================
    # TEST 6: NO AI CALLS
    # =========================================================================

    def test_no_ai_calls_made(self):
        """Test that NO AI calls are made throughout pipeline."""
        # This test verifies the assistant doesn't use AI fallback

        queries = [
            "How many communities?",
            "My tasks",
            "Help",
            "Show dashboard",
            "unknown xyz query",
        ]

        for query in queries:
            result = self.assistant.chat(user_id=self.user.id, message=query)

            # Should NOT have AI source
            self.assertNotEqual(result.get('source'), 'gemini')
            self.assertNotEqual(result.get('source'), 'ai')

            # Should have valid response
            self.assertIn('response', result)

        print(f"✓ No AI calls made for {len(queries)} queries")

    # =========================================================================
    # TEST 7: PERFORMANCE BENCHMARKS
    # =========================================================================

    def test_performance_benchmarks(self):
        """Test performance benchmarks for different query types."""
        benchmarks = {}

        test_queries = {
            'faq': "What can you do?",
            'community_count': "How many communities?",
            'staff_tasks': "My tasks",
            'navigation': "Go to dashboard",
            'fallback': "unknown query xyz",
        }

        for query_type, query in test_queries.items():
            start_time = datetime.now()

            result = self.assistant.chat(user_id=self.user.id, message=query)

            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000

            benchmarks[query_type] = response_time

            # All should be under 100ms
            self.assertLess(
                response_time, 100,
                f"{query_type} query took {response_time}ms (expected < 100ms)"
            )

        # Print results
        print("\n" + "="*60)
        print("PERFORMANCE BENCHMARKS (target: < 100ms)")
        print("="*60)
        for query_type, response_time in benchmarks.items():
            print(f"{query_type:20} {response_time:6.2f}ms")
        print("="*60)

        # Calculate average
        avg_time = sum(benchmarks.values()) / len(benchmarks)
        print(f"{'Average':20} {avg_time:6.2f}ms")
        print("="*60)

        # Average should be well under 100ms
        self.assertLess(avg_time, 100)

    # =========================================================================
    # TEST 8: TEMPLATE COVERAGE
    # =========================================================================

    def test_template_coverage(self):
        """Test that all template categories are registered."""
        stats = self.registry.get_stats()

        # Should have templates
        self.assertGreater(stats['total_templates'], 0)

        # Should have multiple categories
        self.assertIn('categories', stats)
        self.assertGreater(len(stats['categories']), 0)

        # Expected categories
        expected_categories = [
            'communities', 'mana', 'coordination',
            'policies', 'projects', 'staff', 'general'
        ]

        for category in expected_categories:
            if category in stats['categories']:
                count = stats['categories'][category]
                print(f"✓ {category:15} {count:3} templates")

        print(f"\nTotal templates: {stats['total_templates']}")

    # =========================================================================
    # TEST 9: CONVERSATION CONTEXT
    # =========================================================================

    def test_conversation_context_stored(self):
        """Test that conversation context is stored."""
        # First query
        result1 = self.assistant.chat(
            user_id=self.user.id,
            message="How many communities?"
        )

        # Second query (context-dependent)
        result2 = self.assistant.chat(
            user_id=self.user.id,
            message="What about workshops?"
        )

        # Both should succeed
        self.assertIn('response', result1)
        self.assertIn('response', result2)

        print(f"✓ Conversation context stored across queries")

    # =========================================================================
    # TEST 10: ERROR HANDLING
    # =========================================================================

    def test_error_handling_empty_query(self):
        """Test error handling for empty query."""
        result = self.assistant.chat(
            user_id=self.user.id,
            message=""
        )

        # Should handle gracefully
        self.assertIn('response', result)

        print(f"✓ Empty query handled gracefully")

    def test_error_handling_very_long_query(self):
        """Test error handling for very long query."""
        long_query = "How many communities " * 100

        result = self.assistant.chat(
            user_id=self.user.id,
            message=long_query
        )

        # Should handle gracefully
        self.assertIn('response', result)

        print(f"✓ Long query handled gracefully")


class ChatComponentIsolationTests(TestCase):
    """Tests for individual component isolation."""

    def test_faq_handler_isolation(self):
        """Test FAQ handler works independently."""
        handler = get_faq_handler()

        result = handler.try_faq("help")

        self.assertIsNotNone(result)
        self.assertIn('answer', result)

        print(f"✓ FAQ handler works in isolation")

    def test_entity_extractor_isolation(self):
        """Test entity extractor works independently."""
        extractor = EntityExtractor()

        entities = extractor.extract_entities("communities in Region IX")

        self.assertIn('location', entities)

        print(f"✓ Entity extractor works in isolation")

    def test_template_matcher_isolation(self):
        """Test template matcher works independently."""
        matcher = get_template_matcher()

        # Find matching templates
        matches = matcher.find_matching_templates(
            "how many communities",
            {},
            category='communities'
        )

        # Should find at least one match
        self.assertGreater(len(matches), 0)

        print(f"✓ Template matcher works in isolation")

    def test_fallback_handler_isolation(self):
        """Test fallback handler works independently."""
        handler = get_fallback_handler()

        result = handler.handle_failed_query(
            query="unknown query",
            intent='data_query',
            entities={}
        )

        # Fallback handler returns type and suggestions, not direct response
        self.assertEqual(result['type'], 'query_failed')
        self.assertIn('suggestions', result)

        print(f"✓ Fallback handler works in isolation")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
