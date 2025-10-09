"""
Comprehensive Tests for AI Chat Widget and Gemini Integration

Tests specifically for:
- Gemini Service integration
- Chat widget backend (HTMX responses)
- API key verification
- Rate limiting and error handling
- Performance metrics
"""

import json
import time
from decimal import Decimal
from unittest.mock import Mock, patch, PropertyMock

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from common.models import ChatMessage

User = get_user_model()


# ========== FIXTURES ==========


@pytest.fixture
def user(db):
    """Create test user."""
    return User.objects.create_user(
        username="testuser",
        email="test@obcms.gov.ph",
        password="testpass123",
        user_type="oobc_staff",
    )


@pytest.fixture
def authenticated_client(user):
    """Create authenticated test client."""
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def mock_gemini_success():
    """Mock successful Gemini API response."""
    return {
        "success": True,
        "message": "There are 47 OBC communities in Region IX (Zamboanga Peninsula).",
        "tokens_used": 150,
        "cost": 0.000525,
        "response_time": 0.85,
        "suggestions": [
            "Show me communities in Region X",
            "What provinces have the most communities?",
            "List communities in Zamboanga del Sur",
        ],
        "cached": False,
    }


@pytest.fixture
def mock_gemini_error():
    """Mock failed Gemini API response."""
    return {
        "success": False,
        "message": "I'm currently experiencing high demand. Please try again in a few moments.",
        "tokens_used": 0,
        "cost": 0.0,
        "response_time": 0.1,
        "suggestions": [
            "How many communities are in Region IX?",
            "Show me recent MANA assessments",
            "What can you help me with?",
        ],
        "cached": False,
    }


# ========== GEMINI SERVICE TESTS ==========


@pytest.mark.django_db
class TestGeminiServiceIntegration:
    """Test GeminiService integration with chat functionality."""

    def test_gemini_service_initialization(self):
        """Test that GeminiService initializes correctly."""
        from ai_assistant.services.gemini_service import GeminiService

        service = GeminiService()

        assert service.model_name == "gemini-flash-latest"
        assert service.temperature == 0.7
        assert service.max_retries == 3
        assert service.cultural_context is not None

    def test_gemini_service_custom_temperature(self):
        """Test GeminiService with custom temperature for chat."""
        from ai_assistant.services.gemini_service import GeminiService

        # Chat should use higher temperature (0.8) for more natural responses
        service = GeminiService(temperature=0.8)

        assert service.temperature == 0.8

    @patch("google.generativeai.GenerativeModel")
    def test_chat_with_ai_method(self, mock_model_class):
        """Test chat_with_ai method specifically for chat widget."""
        from ai_assistant.services.gemini_service import GeminiService

        # Mock the API response
        mock_response = Mock()
        mock_response.text = """Based on the latest OBCMS data, there are 47 Bangsamoro communities identified in Region IX (Zamboanga Peninsula).

SUGGESTIONS:
- Show me details about these communities
- Which provinces have the most communities?
- What are the primary needs in Region IX?"""

        mock_model_instance = Mock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model_instance

        service = GeminiService(temperature=0.8)
        result = service.chat_with_ai(
            user_message="How many communities are in Region IX?",
            context="User viewing Communities dashboard",
        )

        assert result["success"] is True
        assert "47" in result["message"]
        assert len(result["suggestions"]) == 3
        assert result["tokens_used"] > 0
        assert result["cost"] > 0

    @patch("google.generativeai.GenerativeModel")
    def test_chat_with_ai_includes_cultural_context(self, mock_model_class):
        """Test that chat_with_ai includes Bangsamoro cultural context."""
        from ai_assistant.services.gemini_service import GeminiService

        mock_response = Mock()
        mock_response.text = "Test response\n\nSUGGESTIONS:\n- Question 1\n- Question 2"

        mock_model_instance = Mock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model_instance

        service = GeminiService()
        service.chat_with_ai(
            user_message="Tell me about OBC communities",
            context=None,
        )

        # Verify generate_content was called
        assert mock_model_instance.generate_content.called

        # Get the prompt that was passed
        call_args = mock_model_instance.generate_content.call_args[0][0]

        # Should include cultural context
        assert "BANGSAMORO" in call_args or "Bangsamoro" in call_args

    @patch("google.generativeai.GenerativeModel")
    def test_chat_with_ai_handles_api_errors(self, mock_model_class):
        """Test error handling in chat_with_ai."""
        from ai_assistant.services.gemini_service import GeminiService

        # Mock API failure
        mock_model_instance = Mock()
        mock_model_instance.generate_content.side_effect = Exception(
            "API rate limit exceeded"
        )
        mock_model_class.return_value = mock_model_instance

        service = GeminiService()
        result = service.chat_with_ai(
            user_message="Test question",
        )

        # Should return user-friendly error
        assert result["success"] is False
        assert "high demand" in result["message"] or "try again" in result["message"]
        assert len(result["suggestions"]) > 0
        assert result["tokens_used"] == 0

    @patch("google.generativeai.GenerativeModel")
    def test_chat_with_conversation_history(self, mock_model_class):
        """Test chat_with_ai with conversation history."""
        from ai_assistant.services.gemini_service import GeminiService

        mock_response = Mock()
        mock_response.text = "Based on your previous question...\n\nSUGGESTIONS:\n- Next Q"

        mock_model_instance = Mock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model_instance

        service = GeminiService()

        history = [
            {"role": "user", "content": "How many communities?"},
            {"role": "assistant", "content": "There are 47 communities."},
        ]

        result = service.chat_with_ai(
            user_message="Where are they located?",
            conversation_history=history,
        )

        assert result["success"] is True

        # Verify history was included in prompt
        call_args = mock_model_instance.generate_content.call_args[0][0]
        assert "How many communities?" in call_args

    def test_token_estimation_accuracy(self):
        """Test token estimation is reasonable."""
        from ai_assistant.services.gemini_service import GeminiService

        service = GeminiService()

        # Test various text lengths
        short_text = "Hello"
        medium_text = "How many communities are there in Region IX?"
        long_text = "This is a much longer text with many more words to estimate tokens for. " * 5

        short_tokens = service._estimate_tokens(short_text, "")
        medium_tokens = service._estimate_tokens(medium_text, "")
        long_tokens = service._estimate_tokens(long_text, "")

        # Longer text should have more tokens
        assert long_tokens > medium_tokens > short_tokens

        # Roughly 1 token per 5 characters
        assert abs(short_tokens - len(short_text) // 5) <= 2
        assert abs(medium_tokens - len(medium_text) // 5) <= 5

    def test_cost_calculation(self):
        """Test API cost calculation."""
        from ai_assistant.services.gemini_service import GeminiService

        service = GeminiService()

        # Test cost for 1000 tokens
        cost = service._calculate_cost(1000)

        # Cost should be reasonable (less than $0.01 for 1000 tokens)
        assert isinstance(cost, Decimal)
        assert float(cost) < 0.01
        assert float(cost) > 0.0001

    @patch("google.generativeai.GenerativeModel")
    def test_retry_logic(self, mock_model_class):
        """Test retry logic on API failures."""
        from ai_assistant.services.gemini_service import GeminiService

        # Mock API failing twice, then succeeding
        mock_response = Mock()
        mock_response.text = "Success after retries"

        mock_model_instance = Mock()
        mock_model_instance.generate_content.side_effect = [
            Exception("Temporary error 1"),
            Exception("Temporary error 2"),
            mock_response,
        ]
        mock_model_class.return_value = mock_model_instance

        service = GeminiService(max_retries=3)
        result = service.generate_text(
            prompt="Test retry",
            use_cache=False,
        )

        # Should succeed after retries
        assert result["success"] is True
        assert "Success after retries" in result["text"]
        assert mock_model_instance.generate_content.call_count == 3

    @patch("google.generativeai.GenerativeModel")
    def test_caching_mechanism(self, mock_model_class):
        """Test response caching."""
        from ai_assistant.services.gemini_service import GeminiService

        mock_response = Mock()
        mock_response.text = "Cached response"

        mock_model_instance = Mock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model_instance

        service = GeminiService()

        # First call - should hit API
        result1 = service.generate_text(
            prompt="Same prompt",
            use_cache=True,
        )

        # Second call - should use cache
        result2 = service.generate_text(
            prompt="Same prompt",
            use_cache=True,
        )

        # API should only be called once
        assert mock_model_instance.generate_content.call_count == 1

        # Both results should be successful
        assert result1["success"] is True
        assert result2["success"] is True
        assert result2["cached"] is True


# ========== CHAT WIDGET BACKEND TESTS ==========


@pytest.mark.django_db
class TestChatWidgetBackend:
    """Test chat widget backend views and HTMX integration."""

    def test_chat_message_endpoint_exists(self, authenticated_client):
        """Test that chat message endpoint exists."""
        response = authenticated_client.post(
            reverse("common:chat_message"),
            {"message": "Test"},
        )

        # Should not return 404
        assert response.status_code != 404

    def test_chat_message_requires_authentication(self):
        """Test that unauthenticated requests are rejected."""
        client = Client()

        response = client.post(
            reverse("common:chat_message"),
            {"message": "Test"},
        )

        # Should redirect to login
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_chat_message_rejects_empty_message(self, authenticated_client):
        """Test that empty messages are rejected."""
        response = authenticated_client.post(
            reverse("common:chat_message"),
            {"message": ""},
        )

        assert response.status_code == 400
        assert b"Please enter a message" in response.content

    def test_chat_message_rejects_whitespace(self, authenticated_client):
        """Test that whitespace-only messages are rejected."""
        response = authenticated_client.post(
            reverse("common:chat_message"),
            {"message": "   \n\t  "},
        )

        assert response.status_code == 400

    @patch("ai_assistant.services.gemini_service.GeminiService.chat_with_ai")
    def test_chat_message_success_with_gemini(
        self, mock_chat_ai, authenticated_client, user, mock_gemini_success
    ):
        """Test successful chat message with Gemini integration."""
        mock_chat_ai.return_value = mock_gemini_success

        response = authenticated_client.post(
            reverse("common:chat_message"),
            {"message": "How many communities in Region IX?"},
        )

        assert response.status_code == 200

        # Should store message in database
        messages = ChatMessage.objects.filter(user=user)
        assert messages.count() == 1

    @patch("ai_assistant.services.gemini_service.GeminiService.chat_with_ai")
    def test_chat_message_handles_gemini_error(
        self, mock_chat_ai, authenticated_client, mock_gemini_error
    ):
        """Test error handling when Gemini fails."""
        mock_chat_ai.return_value = mock_gemini_error

        response = authenticated_client.post(
            reverse("common:chat_message"),
            {"message": "Test question"},
        )

        # Should still return 200 with error message
        assert response.status_code == 200

    def test_chat_message_htmx_headers(self, authenticated_client):
        """Test that HTMX requests are recognized."""
        with patch(
            "ai_assistant.services.gemini_service.GeminiService.chat_with_ai"
        ) as mock:
            mock.return_value = {
                "success": True,
                "message": "Test response",
                "suggestions": [],
                "tokens_used": 50,
                "cost": 0.0001,
                "cached": False,
            }

            response = authenticated_client.post(
                reverse("common:chat_message"),
                {"message": "Test"},
                HTTP_HX_REQUEST="true",
            )

            # Should return HTML for HTMX swap
            assert response.status_code == 200
            assert response["Content-Type"] == "text/html; charset=utf-8"

    def test_chat_history_endpoint(self, authenticated_client, user):
        """Test chat history retrieval."""
        # Create test messages
        ChatMessage.objects.create(
            user=user,
            user_message="Question 1",
            assistant_response="Answer 1",
            intent="data_query",
        )
        ChatMessage.objects.create(
            user=user,
            user_message="Question 2",
            assistant_response="Answer 2",
            intent="help",
        )

        response = authenticated_client.get(reverse("common:chat_history"))

        assert response.status_code == 200

        data = response.json()
        assert "history" in data
        assert len(data["history"]) == 2

    def test_chat_history_respects_limit(self, authenticated_client, user):
        """Test that history limit parameter works."""
        # Create 10 messages
        for i in range(10):
            ChatMessage.objects.create(
                user=user,
                user_message=f"Question {i}",
                assistant_response=f"Answer {i}",
                intent="data_query",
            )

        # Request only 5
        response = authenticated_client.get(
            reverse("common:chat_history"),
            {"limit": 5},
        )

        data = response.json()
        assert len(data["history"]) == 5

    def test_chat_history_user_isolation(self, authenticated_client, user):
        """Test that users only see their own messages."""
        # Create message for test user
        ChatMessage.objects.create(
            user=user,
            user_message="My question",
            assistant_response="My answer",
            intent="help",
        )

        # Create message for other user
        other_user = User.objects.create_user(
            username="otheruser",
            password="otherpass",
            user_type="oobc_staff",
        )
        ChatMessage.objects.create(
            user=other_user,
            user_message="Other question",
            assistant_response="Other answer",
            intent="help",
        )

        response = authenticated_client.get(reverse("common:chat_history"))

        data = response.json()
        assert len(data["history"]) == 1
        assert data["history"][0]["user_message"] == "My question"

    def test_clear_chat_history(self, authenticated_client, user):
        """Test clearing chat history."""
        # Create messages
        ChatMessage.objects.create(
            user=user,
            user_message="Test",
            assistant_response="Answer",
            intent="help",
        )

        response = authenticated_client.delete(reverse("common:chat_clear"))

        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True

        # Verify messages deleted
        assert ChatMessage.objects.filter(user=user).count() == 0


# ========== API KEY VERIFICATION ==========


class TestAPIKeyConfiguration(TestCase):
    """Test that API keys are properly configured."""

    def test_google_api_key_exists(self):
        """Test that GOOGLE_API_KEY is configured."""
        assert hasattr(settings, "GOOGLE_API_KEY")
        assert settings.GOOGLE_API_KEY is not None
        assert len(settings.GOOGLE_API_KEY) > 0

    def test_google_api_key_not_placeholder(self):
        """Test that API key is not a placeholder value."""
        api_key = settings.GOOGLE_API_KEY

        # Should not be common placeholder values
        placeholders = [
            "your-api-key",
            "YOUR_API_KEY",
            "replace-me",
            "changeme",
            "xxx",
            "test",
        ]

        for placeholder in placeholders:
            assert placeholder.lower() not in api_key.lower()

    def test_gemini_service_loads_api_key(self):
        """Test that GeminiService loads the API key."""
        from ai_assistant.services.gemini_service import GeminiService

        try:
            service = GeminiService()
            # If initialization succeeds, API key was loaded
            assert service is not None
        except ValueError as e:
            pytest.fail(f"GeminiService failed to initialize: {e}")


@pytest.mark.skipif(
    not hasattr(settings, "GOOGLE_API_KEY") or not settings.GOOGLE_API_KEY,
    reason="GOOGLE_API_KEY not configured",
)
@pytest.mark.slow
class TestGeminiAPIConnectivity(TestCase):
    """
    Test actual Gemini API connectivity.

    WARNING: These tests make real API calls and consume quota.
    Only run when explicitly testing integration.
    """

    def test_gemini_api_simple_request(self):
        """Test a simple API request to Gemini."""
        from ai_assistant.services.gemini_service import GeminiService

        try:
            service = GeminiService()
            result = service.generate_text(
                prompt="Say 'Hello OBCMS' in exactly 2 words",
                use_cache=False,
            )

            assert result["success"] is True
            assert result["text"] is not None
            assert len(result["text"]) > 0
            assert result["tokens_used"] > 0

        except Exception as e:
            pytest.fail(f"Gemini API connectivity test failed: {e}")

    def test_gemini_chat_request(self):
        """Test chat_with_ai method with real API."""
        from ai_assistant.services.gemini_service import GeminiService

        try:
            service = GeminiService(temperature=0.8)
            result = service.chat_with_ai(
                user_message="How many communities are in OBCMS?",
                context="Testing API connectivity",
            )

            assert result["success"] is True
            assert result["message"] is not None
            assert result["tokens_used"] > 0
            assert len(result["suggestions"]) > 0

        except Exception as e:
            pytest.fail(f"Gemini chat API test failed: {e}")


# ========== PERFORMANCE TESTS ==========


@pytest.mark.django_db
class TestChatPerformance:
    """Test chat performance and efficiency."""

    @patch("ai_assistant.services.gemini_service.GeminiService.chat_with_ai")
    def test_chat_response_time(
        self, mock_chat_ai, authenticated_client, mock_gemini_success
    ):
        """Test that chat responses are reasonably fast."""
        mock_chat_ai.return_value = mock_gemini_success

        start = time.time()
        response = authenticated_client.post(
            reverse("common:chat_message"),
            {"message": "Quick test"},
        )
        elapsed = time.time() - start

        assert response.status_code == 200
        # Should respond within 2 seconds (excluding actual API call)
        assert elapsed < 2.0

    def test_chat_history_loads_efficiently(self, authenticated_client, user):
        """Test that chat history loads efficiently with many messages."""
        # Create 100 messages
        for i in range(100):
            ChatMessage.objects.create(
                user=user,
                user_message=f"Question {i}",
                assistant_response=f"Answer {i}",
                intent="data_query",
            )

        start = time.time()
        response = authenticated_client.get(
            reverse("common:chat_history"),
            {"limit": 20},
        )
        elapsed = time.time() - start

        assert response.status_code == 200
        # Should load within 1 second
        assert elapsed < 1.0

        data = response.json()
        assert len(data["history"]) == 20

    @pytest.mark.skipif(
        connection.vendor == "sqlite",
        reason="SQLite locks on concurrent writes; test requires multi-threaded support.",
    )
    def test_concurrent_requests_handling(
        self, authenticated_client
    ):
        """Test handling multiple concurrent chat requests."""
        import threading

        results = []
        errors = []

        def make_request():
            try:
                response = authenticated_client.post(
                    reverse("common:chat_message"),
                    {"message": "Concurrent test"},
                )
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        # Create 5 concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all to complete
        for thread in threads:
            thread.join(timeout=10)

        # All should succeed
        assert len(errors) == 0
        assert all(status == 200 for status in results)


# ========== ERROR HANDLING TESTS ==========


@pytest.mark.django_db
class TestChatErrorHandling:
    """Test error handling in chat functionality."""

    @patch("common.views.chat.get_conversational_assistant")
    def test_gemini_rate_limit_error(
        self, mock_get_assistant, authenticated_client
    ):
        """Test handling of rate limit errors."""
        mock_assistant = Mock()
        mock_assistant.chat.side_effect = Exception("429: Rate limit exceeded")
        mock_get_assistant.return_value = mock_assistant

        response = authenticated_client.post(
            reverse("common:chat_message"),
            {"message": "Test"},
        )

        # Should return 500 with error message
        assert response.status_code == 500
        assert b"Error:" in response.content

    @patch("common.views.chat.get_conversational_assistant")
    def test_gemini_timeout_error(self, mock_get_assistant, authenticated_client):
        """Test handling of timeout errors."""
        mock_assistant = Mock()
        mock_assistant.chat.side_effect = TimeoutError("Request timed out")
        mock_get_assistant.return_value = mock_assistant

        response = authenticated_client.post(
            reverse("common:chat_message"),
            {"message": "Test"},
        )

        assert response.status_code == 500

    def test_database_error_handling(self, authenticated_client, user):
        """Test handling of database errors."""
        with patch(
            "common.models.ChatMessage.objects.create"
        ) as mock_create:
            mock_create.side_effect = Exception("Database connection failed")

            initial_count = ChatMessage.objects.filter(user=user).count()

            # Should not crash the view
            response = authenticated_client.post(
                reverse("common:chat_message"),
                {"message": "Test"},
            )

            # Gracefully handle error with 200 response and no persisted message
            assert response.status_code == 200
            assert ChatMessage.objects.filter(user=user).count() == initial_count
            assert mock_create.called
