"""
Gemini Service - Core Google Gemini API integration for OBCMS.

This service provides:
- Text generation with retry logic
- Streaming and non-streaming responses
- Rate limiting with exponential backoff
- Token counting and cost estimation
- Cultural context integration
"""

import hashlib
import logging
import time
from decimal import Decimal
from typing import Any, Dict, Iterator, Optional

import google.generativeai as genai
from django.conf import settings
from django.core.cache import cache

from ai_assistant.cultural_context import BangsomoroCulturalContext

logger = logging.getLogger(__name__)


class GeminiService:
    """
    Core service for Google Gemini API integration.

    Features:
    - Retry logic with exponential backoff
    - Rate limiting protection
    - Token counting and cost tracking
    - Response caching
    - Cultural context integration
    """

    # Gemini Pro pricing (as of 2025)
    INPUT_TOKEN_COST = Decimal('0.00025')   # per 1K tokens
    OUTPUT_TOKEN_COST = Decimal('0.00075')  # per 1K tokens

    def __init__(
        self,
        model_name: str = 'gemini-1.5-pro',
        temperature: float = 0.7,
        max_retries: int = 3
    ):
        """
        Initialize Gemini service.

        Args:
            model_name: Gemini model to use (default: gemini-1.5-pro)
            temperature: Generation temperature 0-1 (default: 0.7)
            max_retries: Maximum retry attempts (default: 3)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_retries = max_retries

        # Configure Gemini API
        api_key = getattr(settings, 'GOOGLE_API_KEY', None)
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in settings")

        genai.configure(api_key=api_key)

        # Initialize model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=genai.types.GenerationConfig(
                temperature=self.temperature,
                top_p=0.8,
                top_k=40,
                max_output_tokens=8192,
            ),
        )

        # Initialize cultural context
        self.cultural_context = BangsomoroCulturalContext()

        logger.info(f"GeminiService initialized with model: {self.model_name}")

    def generate_text(
        self,
        prompt: str,
        system_context: Optional[str] = None,
        use_cache: bool = True,
        cache_ttl: int = 86400,  # 24 hours
        include_cultural_context: bool = True,
        **generation_kwargs
    ) -> Dict[str, Any]:
        """
        Generate text using Gemini API with retry logic.

        Args:
            prompt: User prompt
            system_context: Optional system context to prepend
            use_cache: Whether to use caching (default: True)
            cache_ttl: Cache time-to-live in seconds (default: 24 hours)
            include_cultural_context: Include Bangsamoro cultural context
            **generation_kwargs: Additional generation config parameters

        Returns:
            Dict containing:
                - success: bool
                - text: str (generated text)
                - tokens_used: int
                - cost: Decimal
                - response_time: float
                - model: str
                - cached: bool
                - error: str (if failed)
        """
        start_time = time.time()

        # Build full prompt
        full_prompt = self._build_prompt(
            prompt,
            system_context,
            include_cultural_context
        )

        # Check cache
        cache_key = self._get_cache_key(full_prompt)
        if use_cache:
            cached_response = cache.get(cache_key)
            if cached_response:
                cached_response['cached'] = True
                cached_response['response_time'] = time.time() - start_time
                logger.info("Returning cached response")
                return cached_response

        # Generate with retry logic
        for attempt in range(self.max_retries):
            try:
                response = self.model.generate_content(full_prompt)

                # Calculate metrics
                response_time = time.time() - start_time
                tokens_used = self._estimate_tokens(full_prompt, response.text)
                cost = self._calculate_cost(tokens_used)

                result = {
                    'success': True,
                    'text': response.text,
                    'tokens_used': tokens_used,
                    'cost': float(cost),
                    'response_time': response_time,
                    'model': self.model_name,
                    'cached': False,
                    'prompt_hash': cache_key,
                }

                # Cache successful response
                if use_cache:
                    cache.set(cache_key, result, cache_ttl)

                logger.info(
                    f"Generated response in {response_time:.2f}s, "
                    f"{tokens_used} tokens, ${cost:.6f}"
                )

                return result

            except Exception as e:
                logger.warning(
                    f"Attempt {attempt + 1}/{self.max_retries} failed: {str(e)}"
                )

                if attempt < self.max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    # Final attempt failed
                    logger.error(f"All retry attempts failed: {str(e)}")
                    return {
                        'success': False,
                        'error': str(e),
                        'text': None,
                        'tokens_used': 0,
                        'cost': 0.0,
                        'response_time': time.time() - start_time,
                        'model': self.model_name,
                        'cached': False,
                    }

    def generate_stream(
        self,
        prompt: str,
        system_context: Optional[str] = None,
        include_cultural_context: bool = True,
    ) -> Iterator[str]:
        """
        Generate streaming response from Gemini.

        Args:
            prompt: User prompt
            system_context: Optional system context
            include_cultural_context: Include Bangsamoro cultural context

        Yields:
            str: Text chunks as they are generated
        """
        full_prompt = self._build_prompt(
            prompt,
            system_context,
            include_cultural_context
        )

        try:
            response = self.model.generate_content(full_prompt, stream=True)

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Streaming generation failed: {str(e)}")
            yield f"Error: {str(e)}"

    def _build_prompt(
        self,
        prompt: str,
        system_context: Optional[str] = None,
        include_cultural_context: bool = True
    ) -> str:
        """Build full prompt with system context and cultural context."""
        parts = []

        # Add system context if provided
        if system_context:
            parts.append(f"SYSTEM CONTEXT:\n{system_context}\n")

        # Add cultural context if requested
        if include_cultural_context:
            parts.append(
                f"BANGSAMORO CULTURAL CONTEXT:\n"
                f"{self.cultural_context.get_base_context()}\n"
            )

        # Add user prompt
        parts.append(f"USER REQUEST:\n{prompt}")

        return "\n".join(parts)

    def _get_cache_key(self, prompt: str) -> str:
        """Generate cache key from prompt and model settings."""
        key_string = f"{prompt}|{self.model_name}|{self.temperature}"
        return hashlib.sha256(key_string.encode()).hexdigest()

    def _estimate_tokens(self, prompt: str, response: str) -> int:
        """
        Estimate token count (rough approximation).

        Rule of thumb: ~4 characters per token for English,
        ~6 characters per token for Filipino/Arabic
        """
        total_chars = len(prompt) + len(response)
        # Average 5 chars per token
        return total_chars // 5

    def _calculate_cost(self, tokens_used: int) -> Decimal:
        """Calculate API cost based on token usage."""
        # Assume 60/40 split input/output
        input_tokens = int(tokens_used * 0.6)
        output_tokens = int(tokens_used * 0.4)

        input_cost = (input_tokens / 1000) * self.INPUT_TOKEN_COST
        output_cost = (output_tokens / 1000) * self.OUTPUT_TOKEN_COST

        return input_cost + output_cost

    def count_tokens(self, text: str) -> int:
        """
        Count tokens using Gemini's token counter.

        Note: This makes an API call to get exact token count.
        Use _estimate_tokens() for quick approximation.
        """
        try:
            result = self.model.count_tokens(text)
            return result.total_tokens
        except Exception as e:
            logger.warning(f"Token counting failed: {e}, using estimation")
            return self._estimate_tokens(text, "")
