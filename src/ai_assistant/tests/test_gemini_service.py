"""
Tests for Gemini AI Service.
"""

import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.test import TestCase

from ai_assistant.services.gemini_service import GeminiService


class TestGeminiService(TestCase):
    """Test cases for GeminiService."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = GeminiService(
            model_name='gemini-1.5-pro',
            temperature=0.7
        )

    @patch('google.generativeai.GenerativeModel')
    def test_initialization(self, mock_model):
        """Test service initialization."""
        service = GeminiService()

        assert service.model_name == 'gemini-1.5-pro'
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

        cost = self.service._calculate_cost(tokens_used, 'gemini-1.5-pro')

        # With 1000 tokens (600 input, 400 output):
        # Input: (600/1000) * $0.00025 = $0.00015
        # Output: (400/1000) * $0.00075 = $0.0003
        # Total: $0.00045
        expected_cost = Decimal('0.00045')
        assert abs(cost - expected_cost) < Decimal('0.00001')

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

    @patch('google.generativeai.GenerativeModel.generate_content')
    def test_generate_text_success(self, mock_generate):
        """Test successful text generation."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.text = "This is a generated response."
        mock_generate.return_value = mock_response

        result = self.service.generate_text(
            prompt="Test prompt",
            use_cache=False
        )

        assert result['success'] is True
        assert result['text'] == "This is a generated response."
        assert result['tokens_used'] > 0
        assert result['cost'] > 0
        assert result['response_time'] >= 0
        assert result['model'] == 'gemini-1.5-pro'
        assert result['cached'] is False

    @patch('google.generativeai.GenerativeModel.generate_content')
    def test_generate_text_with_retry(self, mock_generate):
        """Test retry logic on failure."""
        # First call fails, second succeeds
        mock_response = MagicMock()
        mock_response.text = "Success after retry"

        mock_generate.side_effect = [
            Exception("API Error"),
            mock_response
        ]

        result = self.service.generate_text(
            prompt="Test prompt",
            use_cache=False
        )

        # Should succeed after retry
        assert result['success'] is True
        assert result['text'] == "Success after retry"
        assert mock_generate.call_count == 2

    @patch('google.generativeai.GenerativeModel.generate_content')
    def test_generate_text_max_retries(self, mock_generate):
        """Test max retries exhausted."""
        # All calls fail
        mock_generate.side_effect = Exception("API Error")

        service = GeminiService(max_retries=3)
        result = service.generate_text(
            prompt="Test prompt",
            use_cache=False
        )

        # Should fail after max retries
        assert result['success'] is False
        assert 'error' in result
        assert mock_generate.call_count == 3

    def test_prompt_building(self):
        """Test prompt building with context."""
        prompt = "User question"
        system_context = "System instructions"

        full_prompt = self.service._build_prompt(
            prompt=prompt,
            system_context=system_context,
            include_cultural_context=False
        )

        assert "System instructions" in full_prompt
        assert "User question" in full_prompt

    def test_prompt_with_cultural_context(self):
        """Test prompt with cultural context included."""
        prompt = "User question"

        full_prompt = self.service._build_prompt(
            prompt=prompt,
            system_context=None,
            include_cultural_context=True
        )

        # Should include Bangsamoro cultural context
        assert "Bangsamoro" in full_prompt or "BANGSAMORO" in full_prompt
        assert "OOBC" in full_prompt or "Other Bangsamoro Communities" in full_prompt

    @patch('django.core.cache.cache.get')
    @patch('django.core.cache.cache.set')
    @patch('google.generativeai.GenerativeModel.generate_content')
    def test_caching_behavior(self, mock_generate, mock_cache_set, mock_cache_get):
        """Test caching behavior."""
        # First call - cache miss
        mock_cache_get.return_value = None
        mock_response = MagicMock()
        mock_response.text = "Generated response"
        mock_generate.return_value = mock_response

        result1 = self.service.generate_text(
            prompt="Test",
            use_cache=True
        )

        assert result1['cached'] is False
        assert mock_generate.called
        assert mock_cache_set.called

        # Second call - cache hit
        mock_cache_get.return_value = result1
        result2 = self.service.generate_text(
            prompt="Test",
            use_cache=True
        )

        assert result2['cached'] is True


@pytest.mark.django_db
class TestGeminiServiceIntegration:
    """Integration tests (require actual API key)."""

    @pytest.mark.skipif(
        not hasattr(settings, 'GOOGLE_API_KEY') or not settings.GOOGLE_API_KEY,
        reason="GOOGLE_API_KEY not configured"
    )
    def test_real_api_call(self):
        """Test actual API call (only if API key is configured)."""
        service = GeminiService()

        result = service.generate_text(
            prompt="Say 'Hello' in one word.",
            include_cultural_context=False,
            use_cache=False
        )

        assert result['success'] is True
        assert len(result['text']) > 0
        assert result['tokens_used'] > 0
        assert result['cost'] > 0

    @pytest.mark.skipif(
        not hasattr(settings, 'GOOGLE_API_KEY') or not settings.GOOGLE_API_KEY,
        reason="GOOGLE_API_KEY not configured"
    )
    def test_streaming_response(self):
        """Test streaming API call."""
        service = GeminiService()

        chunks = list(service.generate_stream(
            prompt="Count from 1 to 3.",
            include_cultural_context=False
        ))

        assert len(chunks) > 0
        full_response = "".join(chunks)
        assert len(full_response) > 0
