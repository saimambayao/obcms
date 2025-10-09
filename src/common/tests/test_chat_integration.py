"""
Integration tests for AI Chat functionality.

Tests the complete flow from chat widget → view → service → response.
"""

import json
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from common.models import ChatMessage

User = get_user_model()


class ChatIntegrationTestCase(TestCase):
    """
    Test AI chat widget integration.
    """

    def setUp(self):
        """Set up test user and client."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.client = Client()
        # Use force_login to bypass Axes authentication backend
        self.client.force_login(self.user)

        self.chat_url = reverse('common:chat_message')

    def test_chat_message_success(self):
        """Test successful chat message processing without AI fallback."""
        response = self.client.post(
            self.chat_url,
            {'message': 'How many communities in Region IX?'},
        )

        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'communities', response.content)
        self.assertIn(b'ai-message-bot', response.content)

        # Verify message saved to database
        chat_messages = ChatMessage.objects.filter(user=self.user)
        self.assertEqual(chat_messages.count(), 1)

        message = chat_messages.first()
        self.assertEqual(message.user_message, 'How many communities in Region IX?')
        self.assertIn('communities', message.assistant_response.lower())

    def test_chat_message_requires_auth(self):
        """Test that chat endpoint requires authentication."""
        # Logout
        self.client.logout()

        # Try to send message
        response = self.client.post(
            self.chat_url,
            {'message': 'Test message'},
        )

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_chat_message_empty_message(self):
        """Test that empty messages are rejected."""
        response = self.client.post(
            self.chat_url,
            {'message': '   '},  # Whitespace only
        )

        # Should return error
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Please enter a message', response.content)

    def test_chat_message_post_only(self):
        """Test that GET requests are not allowed."""
        response = self.client.get(self.chat_url)

        # Should return 405 Method Not Allowed
        self.assertEqual(response.status_code, 405)

    @patch('common.views.chat.get_conversational_assistant')
    def test_chat_message_handles_errors(self, mock_get_assistant):
        """Test error handling when assistant raises exception."""
        mock_assistant = MagicMock()
        mock_assistant.chat.side_effect = Exception('API Error')
        mock_get_assistant.return_value = mock_assistant

        response = self.client.post(
            self.chat_url,
            {'message': 'Test question'},
        )

        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Error:', response.content)

    def test_chat_history(self):
        """Test retrieving chat history."""
        # Create some messages
        ChatMessage.objects.create(
            user=self.user,
            user_message='First question',
            assistant_response='First answer',
            intent='query',
            topic='communities',
        )
        ChatMessage.objects.create(
            user=self.user,
            user_message='Second question',
            assistant_response='Second answer',
            intent='query',
            topic='mana',
        )

        # Get history
        response = self.client.get(reverse('common:chat_history'))

        # Verify response
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('history', data)
        self.assertEqual(len(data['history']), 2)

        # Check first message
        first_msg = data['history'][0]
        self.assertEqual(first_msg['user_message'], 'First question')
        self.assertEqual(first_msg['assistant_response'], 'First answer')
        self.assertEqual(first_msg['intent'], 'query')

    def test_chat_history_limit(self):
        """Test chat history respects limit parameter."""
        # Create 25 messages
        for i in range(25):
            ChatMessage.objects.create(
                user=self.user,
                user_message=f'Question {i}',
                assistant_response=f'Answer {i}',
            )

        # Get history with limit
        response = self.client.get(
            reverse('common:chat_history'),
            {'limit': 10},
        )

        data = response.json()
        self.assertEqual(len(data['history']), 10)

    def test_clear_chat_history(self):
        """Test clearing chat history."""
        # Create messages
        ChatMessage.objects.create(
            user=self.user,
            user_message='Question',
            assistant_response='Answer',
        )

        # Verify message exists
        self.assertEqual(ChatMessage.objects.filter(user=self.user).count(), 1)

        # Clear history
        response = self.client.delete(reverse('common:chat_clear'))

        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

        # Verify messages deleted
        self.assertEqual(ChatMessage.objects.filter(user=self.user).count(), 0)

    def test_chat_capabilities(self):
        """Test getting chat capabilities."""
        response = self.client.get(reverse('common:chat_capabilities'))

        # Verify response
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('capabilities', data)

        capabilities = data['capabilities']
        self.assertIn('intents', capabilities)
        self.assertIn('available_models', capabilities)
        self.assertIsInstance(capabilities['intents'], list)
