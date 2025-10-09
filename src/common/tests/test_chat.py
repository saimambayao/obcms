"""
Tests for Conversational AI Chat System

Tests all components: query executor, intent classifier, response formatter,
conversation manager, and chat engine.
"""

import json
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from common.ai_services.chat import (
    get_conversational_assistant,
    get_conversation_manager,
    get_intent_classifier,
    get_query_executor,
    get_response_formatter,
)
from common.models import ChatMessage

User = get_user_model()


class QueryExecutorTestCase(TestCase):
    """Test safe query execution."""

    def setUp(self):
        self.executor = get_query_executor()

    def test_safe_count_query(self):
        """Test safe count query execution."""
        result = self.executor.execute("OBCCommunity.objects.all().count()")

        self.assertTrue(result['success'])
        self.assertIn('result', result)
        self.assertEqual(result['query_info']['result_type'], 'int')

    def test_dangerous_delete_blocked(self):
        """Test that delete operations are blocked."""
        result = self.executor.execute("OBCCommunity.objects.all().delete()")

        self.assertFalse(result['success'])
        self.assertIn('Unsafe query', result['error'])

    def test_dangerous_update_blocked(self):
        """Test that update operations are blocked."""
        result = self.executor.execute(
            "OBCCommunity.objects.filter(id=1).update(community_names='Hacked')"
        )

        self.assertFalse(result['success'])
        self.assertIn('Unsafe query', result['error'])

    def test_dangerous_create_blocked(self):
        """Test that create operations are blocked."""
        result = self.executor.execute(
            "OBCCommunity.objects.create(community_names='Hacked')"
        )

        self.assertFalse(result['success'])
        self.assertIn('Unsafe query', result['error'])

    def test_dangerous_eval_blocked(self):
        """Test that eval is blocked."""
        result = self.executor.execute("eval('print(1)')")

        self.assertFalse(result['success'])
        self.assertIn('Unsafe query', result['error'])

    def test_dangerous_import_blocked(self):
        """Test that imports are blocked."""
        result = self.executor.execute("import os; os.system('ls')")

        self.assertFalse(result['success'])
        self.assertIn('Unsafe query', result['error'])

    def test_invalid_model_blocked(self):
        """Test that invalid models are blocked."""
        result = self.executor.execute("FakeModel.objects.all().count()")

        self.assertFalse(result['success'])

    def test_get_available_models(self):
        """Test getting available models."""
        models = self.executor.get_available_models()

        self.assertIsInstance(models, list)
        self.assertTrue(len(models) > 0)

        # Check structure
        for model in models:
            self.assertIn('model_name', model)
            self.assertIn('fields', model)


class IntentClassifierTestCase(TestCase):
    """Test intent classification."""

    def setUp(self):
        self.classifier = get_intent_classifier()

    def test_data_query_intent(self):
        """Test data query intent detection."""
        message = "How many communities are in Region IX?"
        result = self.classifier.classify(message)

        self.assertEqual(result['type'], 'data_query')
        self.assertGreater(result['confidence'], 0.5)
        self.assertIn('communities', result['entities'])

    def test_analysis_intent(self):
        """Test analysis intent detection."""
        message = "What are the top needs in coastal communities?"
        result = self.classifier.classify(message)

        self.assertEqual(result['type'], 'analysis')
        self.assertGreater(result['confidence'], 0.5)

    def test_navigation_intent(self):
        """Test navigation intent detection."""
        message = "Take me to the dashboard"
        result = self.classifier.classify(message)

        self.assertEqual(result['type'], 'navigation')
        self.assertGreater(result['confidence'], 0.5)

    def test_help_intent(self):
        """Test help intent detection."""
        message = "How do I create a new workshop?"
        result = self.classifier.classify(message)

        self.assertEqual(result['type'], 'help')
        self.assertGreater(result['confidence'], 0.5)

    def test_general_intent(self):
        """Test general conversational intent."""
        message = "Hello!"
        result = self.classifier.classify(message)

        self.assertEqual(result['type'], 'general')

    def test_get_example_queries(self):
        """Test getting example queries."""
        examples = self.classifier.get_example_queries('data_query')

        self.assertIsInstance(examples, list)
        self.assertTrue(len(examples) > 0)


class ResponseFormatterTestCase(TestCase):
    """Test response formatting."""

    def setUp(self):
        self.formatter = get_response_formatter()

    def test_format_count_result(self):
        """Test formatting count results."""
        result = self.formatter.format_query_result(
            result=42,
            result_type='count',
            original_question="How many communities are there?",
            entities=['communities'],
        )

        self.assertIn('response', result)
        self.assertIn('42', result['response'])
        self.assertIn('suggestions', result)
        self.assertTrue(len(result['suggestions']) > 0)

    def test_format_zero_count(self):
        """Test formatting zero count."""
        result = self.formatter.format_query_result(
            result=0,
            result_type='count',
            original_question="How many fake items?",
            entities=['items'],
        )

        self.assertIn('no', result['response'].lower())

    def test_format_list_result(self):
        """Test formatting list results."""
        items = [
            {'id': 1, 'name': 'Item 1'},
            {'id': 2, 'name': 'Item 2'},
        ]

        result = self.formatter.format_query_result(
            result=items,
            result_type='list',
            original_question="Show me items",
            entities=['items'],
        )

        self.assertIn('response', result)
        self.assertIn('data', result)
        self.assertEqual(result['data']['count'], 2)

    def test_format_help(self):
        """Test formatting help response."""
        result = self.formatter.format_help()

        self.assertIn('response', result)
        self.assertIn('OBCMS', result['response'])
        self.assertIn('suggestions', result)

    def test_format_greeting(self):
        """Test formatting greeting."""
        result = self.formatter.format_greeting()

        self.assertIn('response', result)
        self.assertIn('Hello', result['response'])

    def test_format_error(self):
        """Test formatting errors."""
        result = self.formatter.format_error(
            error_message="Something went wrong",
            query="Test query",
        )

        self.assertIn('response', result)
        self.assertIn('Something went wrong', result['response'])


class ConversationManagerTestCase(TestCase):
    """Test conversation management."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            user_type='oobc_staff',
        )
        self.manager = get_conversation_manager()

    def test_add_exchange(self):
        """Test adding conversation exchange."""
        self.manager.add_exchange(
            user_id=self.user.id,
            user_message="Test question",
            assistant_response="Test answer",
            intent='data_query',
            confidence=0.9,
            entities=['communities'],
        )

        # Verify it was saved
        messages = ChatMessage.objects.filter(user=self.user)
        self.assertEqual(messages.count(), 1)

        msg = messages.first()
        self.assertEqual(msg.user_message, "Test question")
        self.assertEqual(msg.intent, 'data_query')

    def test_get_context(self):
        """Test getting conversation context."""
        # Add some exchanges
        for i in range(3):
            self.manager.add_exchange(
                user_id=self.user.id,
                user_message=f"Question {i}",
                assistant_response=f"Answer {i}",
                intent='data_query',
                entities=['communities'],
            )

        # Get context
        context = self.manager.get_context(self.user.id)

        self.assertIn('history', context)
        self.assertEqual(len(context['history']), 3)
        self.assertIn('entities_mentioned', context)

    def test_get_conversation_stats(self):
        """Test getting conversation stats."""
        # Add exchanges
        self.manager.add_exchange(
            user_id=self.user.id,
            user_message="Test",
            assistant_response="Answer",
            intent='data_query',
            entities=['communities'],
        )

        stats = self.manager.get_conversation_stats(self.user.id)

        self.assertIn('total_messages', stats)
        self.assertEqual(stats['total_messages'], 1)

    def test_clear_context(self):
        """Test clearing context."""
        self.manager.add_exchange(
            user_id=self.user.id,
            user_message="Test",
            assistant_response="Answer",
        )

        self.manager.clear_context(self.user.id)

        # Context should be empty (no cache)
        # But database records remain
        messages = ChatMessage.objects.filter(user=self.user)
        self.assertEqual(messages.count(), 1)


class ChatEngineTestCase(TestCase):
    """Test main chat engine."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            user_type='oobc_staff',
        )
        self.assistant = get_conversational_assistant()

    def test_greeting(self):
        """Test greeting response."""
        result = self.assistant.chat(
            user_id=self.user.id,
            message="Hello",
        )

        self.assertIn('response', result)
        self.assertIn('intent', result)
        self.assertEqual(result['intent'], 'general')

    def test_help_query(self):
        """Test help query."""
        result = self.assistant.chat(
            user_id=self.user.id,
            message="What can you help me with?",
        )

        self.assertIn('response', result)
        self.assertEqual(result['intent'], 'faq')
        self.assertIn("help you", result['response'].lower())

    def test_data_query(self):
        """Test data query handling."""
        result = self.assistant.chat(
            user_id=self.user.id,
            message="How many communities are there?",
        )

        self.assertIn('response', result)
        self.assertEqual(result['intent'], 'faq')
        self.assertIn("communities", result['response'].lower())

    def test_conversation_history_stored(self):
        """Test that conversation is stored."""
        self.assistant.chat(
            user_id=self.user.id,
            message="Test message",
        )

        messages = ChatMessage.objects.filter(user=self.user)
        self.assertEqual(messages.count(), 1)

    def test_get_capabilities(self):
        """Test getting capabilities."""
        capabilities = self.assistant.get_capabilities()

        self.assertIn('intents', capabilities)
        self.assertIn('available_models', capabilities)
        self.assertTrue(len(capabilities['intents']) > 0)


class ChatViewsTestCase(TestCase):
    """Test chat views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            user_type='oobc_staff',
        )
        # Use force_login to bypass axes backend authentication requirement
        self.client.force_login(self.user)

    def test_chat_message_view(self):
        """Test chat message endpoint."""
        response = self.client.post(
            reverse('common:chat_message'),
            {'message': 'Hello'},
        )

        self.assertEqual(response.status_code, 200)

    def test_chat_message_empty(self):
        """Test empty message is rejected."""
        response = self.client.post(
            reverse('common:chat_message'),
            {'message': ''},
        )

        self.assertEqual(response.status_code, 400)

    def test_chat_history_view(self):
        """Test chat history endpoint."""
        # Add a message first
        ChatMessage.objects.create(
            user=self.user,
            user_message="Test",
            assistant_response="Answer",
            intent='general',
            confidence=0.9,
        )

        response = self.client.get(reverse('common:chat_history'))

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('history', data)
        self.assertEqual(len(data['history']), 1)

    def test_clear_chat_history(self):
        """Test clearing chat history."""
        # Add a message
        ChatMessage.objects.create(
            user=self.user,
            user_message="Test",
            assistant_response="Answer",
            intent='general',
            confidence=0.9,
        )

        response = self.client.delete(reverse('common:chat_clear'))

        self.assertEqual(response.status_code, 200)

        # Verify deleted
        messages = ChatMessage.objects.filter(user=self.user)
        self.assertEqual(messages.count(), 0)

    def test_chat_stats_view(self):
        """Test chat stats endpoint."""
        response = self.client.get(reverse('common:chat_stats'))

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('stats', data)

    def test_chat_capabilities_view(self):
        """Test capabilities endpoint."""
        response = self.client.get(reverse('common:chat_capabilities'))

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('capabilities', data)

    def test_login_required(self):
        """Test that login is required."""
        self.client.logout()

        response = self.client.post(
            reverse('common:chat_message'),
            {'message': 'Test'},
        )

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
