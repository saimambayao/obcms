"""
Tests for Gemini Chat Service Enhancement

Tests the chat_with_ai() helper function and related chat-specific features.
"""

import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch

from ai_assistant.services.gemini_service import GeminiService


@pytest.fixture
def gemini_service():
    """Create GeminiService instance for testing."""
    with patch('ai_assistant.services.gemini_service.genai'):
        service = GeminiService(temperature=0.8)
        return service


class TestChatWithAI:
    """Test suite for chat_with_ai() function."""

    def test_basic_chat_message(self, gemini_service):
        """Test basic chat message processing."""
        # Mock the generate_text method
        mock_response = {
            "success": True,
            "text": (
                "Based on the latest data, there are 47 Bangsamoro communities in Region IX.\n\n"
                "SUGGESTIONS:\n"
                "- Show me details about these communities\n"
                "- Which provinces have the most communities?\n"
                "- What are the main needs in Region IX?"
            ),
            "tokens_used": 150,
            "cost": 0.000045,
            "response_time": 0.8,
            "cached": False,
        }

        gemini_service.generate_text = MagicMock(return_value=mock_response)

        # Test chat
        result = gemini_service.chat_with_ai(
            user_message="How many communities are in Region IX?",
            context="User viewing Communities dashboard"
        )

        # Assertions
        assert result["success"] is True
        assert "47 Bangsamoro communities" in result["message"]
        assert len(result["suggestions"]) == 3
        assert result["tokens_used"] == 150
        assert result["cost"] == 0.000045
        assert result["cached"] is False

    def test_chat_with_conversation_history(self, gemini_service):
        """Test chat with conversation history context."""
        conversation_history = [
            {"role": "user", "content": "How many communities are there?"},
            {"role": "assistant", "content": "There are 150 communities total."},
            {"role": "user", "content": "What about Region IX?"},
        ]

        mock_response = {
            "success": True,
            "text": (
                "In Region IX specifically, there are 47 Bangsamoro communities.\n\n"
                "SUGGESTIONS:\n"
                "- Compare with other regions\n"
                "- Show breakdown by province"
            ),
            "tokens_used": 180,
            "cost": 0.000054,
            "response_time": 0.9,
            "cached": False,
        }

        gemini_service.generate_text = MagicMock(return_value=mock_response)

        result = gemini_service.chat_with_ai(
            user_message="What about Region IX?",
            conversation_history=conversation_history
        )

        assert result["success"] is True
        assert "Region IX" in result["message"]
        assert len(result["suggestions"]) >= 2

    def test_error_handling_api_key_error(self, gemini_service):
        """Test error handling for API key errors."""
        mock_response = {
            "success": False,
            "error": "Invalid API key",
            "response_time": 0.1,
        }

        gemini_service.generate_text = MagicMock(return_value=mock_response)

        result = gemini_service.chat_with_ai(
            user_message="Test message"
        )

        assert result["success"] is False
        assert "trouble connecting" in result["message"]
        assert "system administrator" in result["message"]
        assert len(result["suggestions"]) > 0

    def test_error_handling_rate_limit(self, gemini_service):
        """Test error handling for rate limit errors."""
        mock_response = {
            "success": False,
            "error": "Rate limit exceeded",
            "response_time": 0.1,
        }

        gemini_service.generate_text = MagicMock(return_value=mock_response)

        result = gemini_service.chat_with_ai(
            user_message="Test message"
        )

        assert result["success"] is False
        assert "high demand" in result["message"]
        assert "try again" in result["message"]

    def test_error_handling_timeout(self, gemini_service):
        """Test error handling for timeout errors."""
        mock_response = {
            "success": False,
            "error": "Request timed out",
            "response_time": 10.0,
        }

        gemini_service.generate_text = MagicMock(return_value=mock_response)

        result = gemini_service.chat_with_ai(
            user_message="Complex query"
        )

        assert result["success"] is False
        assert "took too long" in result["message"]
        assert "simpler question" in result["message"]

    def test_error_handling_network_error(self, gemini_service):
        """Test error handling for network errors."""
        mock_response = {
            "success": False,
            "error": "Network connection failed",
            "response_time": 0.5,
        }

        gemini_service.generate_text = MagicMock(return_value=mock_response)

        result = gemini_service.chat_with_ai(
            user_message="Test message"
        )

        assert result["success"] is False
        assert "network" in result["message"].lower()
        assert "internet connection" in result["message"]


class TestChatSystemContext:
    """Test suite for OBCMS chat system context."""

    def test_build_chat_system_context(self, gemini_service):
        """Test chat system context building."""
        context = gemini_service._build_chat_system_context()

        # Check for key OBCMS modules
        assert "Communities Module" in context
        assert "MANA" in context
        assert "Coordination Module" in context
        assert "Policy Recommendations" in context
        assert "Project Central" in context

        # Check for capabilities
        assert "CAPABILITIES" in context.upper()
        assert "Bangsamoro cultural context" in context

        # Check for response guidelines
        assert "RESPONSE GUIDELINES" in context.upper()
        assert "culturally sensitive" in context

    def test_build_chat_system_context_with_additional(self, gemini_service):
        """Test system context with additional context."""
        context = gemini_service._build_chat_system_context(
            additional_context="User is viewing MANA Assessment #123"
        )

        assert "ADDITIONAL CONTEXT" in context
        assert "MANA Assessment #123" in context

    def test_build_chat_prompt_basic(self, gemini_service):
        """Test basic chat prompt building."""
        prompt = gemini_service._build_chat_prompt(
            user_message="How many communities?",
            system_context="Test system context",
            conversation_history=None
        )

        assert "SYSTEM CONTEXT" in prompt
        assert "Test system context" in prompt
        assert "BANGSAMORO CULTURAL CONTEXT" in prompt
        assert "USER: How many communities?" in prompt
        assert "ASSISTANT:" in prompt

    def test_build_chat_prompt_with_history(self, gemini_service):
        """Test chat prompt building with conversation history."""
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help?"},
            {"role": "user", "content": "Show me communities"},
        ]

        prompt = gemini_service._build_chat_prompt(
            user_message="How many?",
            system_context="Test context",
            conversation_history=history
        )

        assert "CONVERSATION HISTORY" in prompt
        assert "USER: Hello" in prompt
        assert "ASSISTANT: Hi! How can I help?" in prompt
        assert "USER: Show me communities" in prompt

    def test_build_chat_prompt_limits_history(self, gemini_service):
        """Test that conversation history is limited to last 5 exchanges."""
        # Create 10 exchanges (should only keep last 5)
        history = [
            {"role": "user", "content": f"Message {i}"}
            for i in range(10)
        ]

        prompt = gemini_service._build_chat_prompt(
            user_message="Current message",
            system_context="Test",
            conversation_history=history
        )

        # Should only have messages 5-9 (last 5)
        assert "Message 5" in prompt
        assert "Message 9" in prompt
        assert "Message 0" not in prompt
        assert "Message 4" not in prompt


class TestResponseParsing:
    """Test suite for response parsing."""

    def test_parse_chat_response_with_suggestions(self, gemini_service):
        """Test parsing response with suggestions."""
        response_text = """Based on the data, there are 47 communities in Region IX.

SUGGESTIONS:
- Show me details about these communities
- Which provinces have the most?
- What are the priority needs?"""

        parsed = gemini_service._parse_chat_response(response_text)

        assert "47 communities" in parsed["message"]
        assert len(parsed["suggestions"]) == 3
        assert "Show me details" in parsed["suggestions"][0]
        assert "Which provinces" in parsed["suggestions"][1]

    def test_parse_chat_response_with_bullet_variations(self, gemini_service):
        """Test parsing suggestions with different bullet styles."""
        response_text = """Here's the answer.

SUGGESTIONS:
- Question with dash
• Question with bullet
* Question with asterisk
Question without bullet"""

        parsed = gemini_service._parse_chat_response(response_text)

        assert len(parsed["suggestions"]) == 3  # Max 3
        # All should be cleaned of leading symbols
        for suggestion in parsed["suggestions"]:
            assert not suggestion.startswith("-")
            assert not suggestion.startswith("•")
            assert not suggestion.startswith("*")

    def test_parse_chat_response_without_suggestions(self, gemini_service):
        """Test parsing response without suggestions section."""
        response_text = "This is just a plain response without suggestions."

        parsed = gemini_service._parse_chat_response(response_text)

        assert parsed["message"] == response_text
        # Should have fallback suggestions
        assert len(parsed["suggestions"]) > 0
        assert "How many communities" in parsed["suggestions"][0]

    def test_parse_chat_response_empty_suggestions(self, gemini_service):
        """Test parsing response with empty suggestions section."""
        response_text = """Here's the answer.

SUGGESTIONS:"""

        parsed = gemini_service._parse_chat_response(response_text)

        # Should use fallback suggestions
        assert len(parsed["suggestions"]) > 0


class TestUserFriendlyErrors:
    """Test suite for user-friendly error messages."""

    def test_api_key_error_message(self, gemini_service):
        """Test API key error conversion."""
        message = gemini_service._get_user_friendly_error("Invalid API key")

        assert "trouble connecting" in message
        assert "system administrator" in message

    def test_rate_limit_error_message(self, gemini_service):
        """Test rate limit error conversion."""
        message = gemini_service._get_user_friendly_error("Rate limit exceeded")

        assert "high demand" in message
        assert "try again" in message

    def test_timeout_error_message(self, gemini_service):
        """Test timeout error conversion."""
        message = gemini_service._get_user_friendly_error("Request timed out")

        assert "took too long" in message
        assert "simpler question" in message

    def test_network_error_message(self, gemini_service):
        """Test network error conversion."""
        message = gemini_service._get_user_friendly_error("Network connection failed")

        assert "network" in message.lower()
        assert "internet connection" in message

    def test_content_policy_error_message(self, gemini_service):
        """Test content policy error conversion."""
        message = gemini_service._get_user_friendly_error("Safety policy violation")

        assert "content guidelines" in message
        assert "rephrasing" in message

    def test_generic_error_message(self, gemini_service):
        """Test generic error conversion."""
        message = gemini_service._get_user_friendly_error("Unknown weird error")

        assert "encountered an issue" in message
        assert "try again" in message


class TestFallbackSuggestions:
    """Test suite for fallback suggestions."""

    def test_get_fallback_suggestions(self, gemini_service):
        """Test fallback suggestions generation."""
        suggestions = gemini_service._get_fallback_suggestions()

        assert len(suggestions) >= 3
        assert any("communities" in s.lower() for s in suggestions)
        assert any("mana" in s.lower() for s in suggestions)
        assert any("help" in s.lower() for s in suggestions)


class TestChatIntegration:
    """Integration tests for chat functionality."""

    @pytest.mark.integration
    def test_full_chat_flow_success(self, gemini_service):
        """Test complete chat flow with successful response."""
        # Mock successful generation
        mock_response = {
            "success": True,
            "text": (
                "There are 150 OBC communities across Regions IX, X, XI, and XII.\n\n"
                "SUGGESTIONS:\n"
                "- Show breakdown by region\n"
                "- Which region has the most?\n"
                "- Show me recent assessments"
            ),
            "tokens_used": 200,
            "cost": 0.00006,
            "response_time": 1.2,
            "cached": False,
        }

        gemini_service.generate_text = MagicMock(return_value=mock_response)

        result = gemini_service.chat_with_ai(
            user_message="How many OBC communities are there?",
            context="User on Communities dashboard"
        )

        # Verify structure
        assert "success" in result
        assert "message" in result
        assert "suggestions" in result
        assert "tokens_used" in result
        assert "cost" in result
        assert "response_time" in result
        assert "cached" in result

        # Verify content
        assert result["success"] is True
        assert "150 OBC communities" in result["message"]
        assert len(result["suggestions"]) == 3

    @pytest.mark.integration
    def test_full_chat_flow_error(self, gemini_service):
        """Test complete chat flow with error response."""
        # Mock error
        mock_response = {
            "success": False,
            "error": "API rate limit exceeded",
            "response_time": 0.2,
        }

        gemini_service.generate_text = MagicMock(return_value=mock_response)

        result = gemini_service.chat_with_ai(
            user_message="Test message"
        )

        # Verify error handling
        assert result["success"] is False
        assert "high demand" in result["message"]
        assert len(result["suggestions"]) > 0
        assert result["tokens_used"] == 0
        assert result["cost"] == 0.0
