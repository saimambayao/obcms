"""
Tests for Gemini AI Service.
"""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings
from django.test import TestCase

from ai_assistant.services.gemini_service import GeminiService


@pytest.fixture
def gemini_service():
    """Create GeminiService instance for testing."""
    with patch('ai_assistant.services.gemini_service.genai'):
        with patch('django.conf.settings.GOOGLE_API_KEY', 'test-api-key'):
            service = GeminiService(model_name="gemini-flash-latest", temperature=0.7)
            return service


class TestGeminiService(TestCase):
    """Test cases for GeminiService."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock genai module and settings
        with patch('ai_assistant.services.gemini_service.genai'):
            with patch('django.conf.settings.GOOGLE_API_KEY', 'test-api-key'):
                self.service = GeminiService(model_name="gemini-flash-latest", temperature=0.7)

    def test_initialization(self):
        """Test service initialization."""
        with patch('ai_assistant.services.gemini_service.genai'):
            with patch('django.conf.settings.GOOGLE_API_KEY', 'test-api-key'):
                service = GeminiService()

        assert service.model_name == "gemini-flash-latest"
        assert service.temperature == 0.7
        assert service.max_retries == 3

    def test_token_estimation(self):
        """Test token count estimation."""
        prompt = "This is a test prompt."
        response = "This is a test response."

        tokens = self.service._estimate_tokens(prompt, response)

        # Should estimate ~10-15 tokens for this short text
        assert tokens > 5
        assert tokens < 20

    def test_cost_calculation(self):
        """Test cost calculation."""
        tokens_used = 1000

        cost = self.service._calculate_cost(tokens_used)

        # With 1000 tokens (60/40 split input/output per implementation):
        # gemini-flash-latest pricing: $0.30 input / $2.50 output per million
        # Input: (600/1000) * $0.0003 = $0.00018
        # Output: (400/1000) * $0.0025 = $0.001
        # Total: $0.00118
        expected_cost = Decimal("0.00118")
        assert abs(cost - expected_cost) < Decimal("0.00001")

    def test_cache_key_generation(self):
        """Test cache key generation."""
        prompt = "Test prompt"

        key1 = self.service._get_cache_key(prompt)
        key2 = self.service._get_cache_key(prompt)
        key3 = self.service._get_cache_key("Different prompt")

        # Same prompt should generate same key
        assert key1 == key2

        # Different prompts should generate different keys
        assert key1 != key3

        # Key should be SHA256 hash (64 chars)
        assert len(key1) == 64

    def test_generate_text_success(self):
        """Test successful text generation."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.text = "This is a generated response."

        with patch.object(self.service.model, 'generate_content', return_value=mock_response):
            result = self.service.generate_text(prompt="Test prompt", use_cache=False)

            assert result["success"] is True
            assert result["text"] == "This is a generated response."
            assert result["tokens_used"] > 0
            assert result["cost"] > 0
            assert result["response_time"] >= 0
            assert result["model"] == "gemini-flash-latest"
            assert result["cached"] is False

    def test_generate_text_with_retry(self):
        """Test retry logic on failure."""
        # First call fails, second succeeds
        mock_response = MagicMock()
        mock_response.text = "Success after retry"

        with patch.object(self.service.model, 'generate_content', side_effect=[Exception("API Error"), mock_response]) as mock_generate:
            result = self.service.generate_text(prompt="Test prompt", use_cache=False)

            # Should succeed after retry
            assert result["success"] is True
            assert result["text"] == "Success after retry"
            assert mock_generate.call_count == 2

    def test_generate_text_max_retries(self):
        """Test max retries exhausted."""
        with patch('ai_assistant.services.gemini_service.genai'):
            with patch('django.conf.settings.GOOGLE_API_KEY', 'test-api-key'):
                service = GeminiService(max_retries=3)

        # Mock generate_content on the service's model instance
        with patch.object(service.model, 'generate_content', side_effect=Exception("API Error")) as mock_generate:
            result = service.generate_text(prompt="Test prompt", use_cache=False)

            # Should fail after max retries
            assert result["success"] is False
            assert "error" in result
            assert mock_generate.call_count == 3

    def test_prompt_building(self):
        """Test prompt building with context."""
        prompt = "User question"
        system_context = "System instructions"

        full_prompt = self.service._build_prompt(
            prompt=prompt, system_context=system_context, include_cultural_context=False
        )

        assert "System instructions" in full_prompt
        assert "User question" in full_prompt

    def test_prompt_with_cultural_context(self):
        """Test prompt with cultural context included."""
        prompt = "User question"

        full_prompt = self.service._build_prompt(
            prompt=prompt, system_context=None, include_cultural_context=True
        )

        # Should include Bangsamoro cultural context
        # The cultural context includes "BANGSAMORO CULTURAL CONTEXT" header
        assert "BANGSAMORO CULTURAL CONTEXT" in full_prompt or "BANGSAMORO" in full_prompt

    @patch("django.core.cache.cache.get")
    @patch("django.core.cache.cache.set")
    def test_caching_behavior(self, mock_cache_set, mock_cache_get):
        """Test caching behavior."""
        # First call - cache miss
        mock_cache_get.return_value = None
        mock_response = MagicMock()
        mock_response.text = "Generated response"

        with patch.object(self.service.model, 'generate_content', return_value=mock_response) as mock_generate:
            result1 = self.service.generate_text(prompt="Test", use_cache=True)

            assert result1["cached"] is False
            assert mock_generate.called
            assert mock_cache_set.called

        # Second call - cache hit
        mock_cache_get.return_value = result1
        result2 = self.service.generate_text(prompt="Test", use_cache=True)

        assert result2["cached"] is True


@pytest.mark.django_db
class TestGeminiServiceIntegration:
    """Integration tests (require actual API key)."""

    @pytest.mark.skipif(
        not hasattr(settings, "GOOGLE_API_KEY") or not settings.GOOGLE_API_KEY,
        reason="GOOGLE_API_KEY not configured",
    )
    def test_real_api_call(self):
        """Test actual API call (only if API key is configured)."""
        service = GeminiService()

        result = service.generate_text(
            prompt="Say 'Hello' in one word.",
            include_cultural_context=False,
            use_cache=False,
        )

        assert result["success"] is True
        assert len(result["text"]) > 0
        assert result["tokens_used"] > 0
        assert result["cost"] > 0

    @pytest.mark.skipif(
        not hasattr(settings, "GOOGLE_API_KEY") or not settings.GOOGLE_API_KEY,
        reason="GOOGLE_API_KEY not configured",
    )
    def test_streaming_response(self):
        """Test streaming API call."""
        service = GeminiService()

        chunks = list(
            service.generate_stream(
                prompt="Count from 1 to 3.", include_cultural_context=False
            )
        )

        assert len(chunks) > 0
        full_response = "".join(chunks)
        assert len(full_response) > 0
