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
import re
import time
from decimal import Decimal
from typing import Any, Dict, Iterator, Optional

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class InputValidator:
    """Input validation and sanitization for AI services."""

    # Maximum allowed lengths
    MAX_PROMPT_LENGTH = 10000
    MAX_USER_MESSAGE_LENGTH = 2000
    MAX_CONTEXT_LENGTH = 5000

    # Blocked content patterns
    BLOCKED_PATTERNS = [
        # SQL injection patterns
        r'(?i)(union\s+select|drop\s+table|delete\s+from|insert\s+into)',
        # Command injection patterns
        r'(?i)(\$\(|`|eval|exec|system)',
        # Script injection patterns
        r'(?i)(<script|javascript:|vbscript:|onload=|onerror=)',
        # File path injection
        r'(?i)(\.\.[/\\]|[a-z]:[/\\]|/etc/|/proc/)',
        # Basic XSS patterns
        r'(?i)(<iframe|<object|<embed|<link|<meta)',
    ]

    @classmethod
    def sanitize_input(cls, text: str, max_length: int = None) -> str:
        """
        Sanitize user input by removing or blocking malicious content.

        Args:
            text: Input text to sanitize
            max_length: Maximum allowed length (defaults to class default)

        Returns:
            Sanitized text or raises ValueError if blocked content found
        """
        if not isinstance(text, str):
            raise ValueError("Input must be a string")

        if max_length is None:
            max_length = cls.MAX_PROMPT_LENGTH

        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length]
            logger.warning(f"Input truncated to {max_length} characters")

        # Check for blocked patterns
        for pattern in cls.BLOCKED_PATTERNS:
            if re.search(pattern, text):
                logger.warning(f"Blocked content detected in input: {pattern}")
                raise ValueError("Input contains potentially malicious content")

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    @classmethod
    def validate_chat_message(cls, user_message: str) -> str:
        """Validate and sanitize chat message specifically."""
        return cls.sanitize_input(user_message, cls.MAX_USER_MESSAGE_LENGTH)

    @classmethod
    def validate_context(cls, context: str) -> str:
        """Validate and sanitize context data."""
        if not context:
            return ""
        return cls.sanitize_input(context, cls.MAX_CONTEXT_LENGTH)


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

    # Gemini Flash pricing (as of 2025)
    # gemini-flash-latest: $0.30 input / $2.50 output per million tokens
    INPUT_TOKEN_COST = Decimal("0.0003")  # per 1K tokens ($0.30 / 1M * 1K)
    OUTPUT_TOKEN_COST = Decimal("0.0025")  # per 1K tokens ($2.50 / 1M * 1K)

    def __init__(
        self,
        model_name: str = "gemini-flash-latest",
        temperature: float = 0.7,
        max_retries: int = 3,
    ):
        """
        Initialize Gemini service.

        Args:
            model_name: Gemini model to use (default: gemini-flash-latest)
            temperature: Generation temperature 0-1 (default: 0.7)
            max_retries: Maximum retry attempts (default: 3)
        """
        # Import Google Generative AI here to avoid heavy imports during Django startup
        try:
            import google.generativeai as genai
        except ImportError as e:
            logger.error(f"Google Generative AI library not available: {e}")
            raise RuntimeError(f"Google Generative AI library is required but not installed: {e}")

        self.model_name = model_name
        self.temperature = temperature
        self.max_retries = max_retries

        # Configure Gemini API with secure key handling
        api_key = getattr(settings, "GOOGLE_API_KEY", None)
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in settings")

        # SECURITY: Validate API key format
        if not isinstance(api_key, str) or len(api_key) < 20:
            logger.error("Invalid API key format detected")
            raise ValueError("Invalid API key format")

        # SECURITY: Log API key status without exposing the key
        if api_key:
            logger.info("Google API key configured successfully")
        else:
            logger.error("Google API key is missing or invalid")
            raise ValueError("GOOGLE_API_KEY not properly configured")

        try:
            genai.configure(api_key=api_key)
            logger.info("Gemini API configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {type(e).__name__}")
            raise RuntimeError(f"Failed to configure Gemini API: {e}")

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
        from ai_assistant.cultural_context import BangsomoroCulturalContext
        self.cultural_context = BangsomoroCulturalContext()

        logger.info(f"GeminiService initialized with model: {self.model_name}")

    def generate_text(
        self,
        prompt: str,
        system_context: Optional[str] = None,
        use_cache: bool = True,
        cache_ttl: int = 86400,  # 24 hours
        include_cultural_context: bool = True,
        **generation_kwargs,
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

        # SECURITY: Validate and sanitize inputs
        try:
            sanitized_prompt = InputValidator.sanitize_input(prompt)
            if system_context:
                sanitized_context = InputValidator.validate_context(system_context)
            else:
                sanitized_context = None
        except ValueError as e:
            logger.warning(f"Input validation failed: {e}")
            return {
                "success": False,
                "error": "Invalid input detected",
                "text": None,
                "tokens_used": 0,
                "cost": 0.0,
                "response_time": time.time() - start_time,
                "model": self.model_name,
                "cached": False,
            }

        # Build full prompt with sanitized inputs
        full_prompt = self._build_prompt(
            sanitized_prompt, sanitized_context, include_cultural_context
        )

        # Check cache
        cache_key = self._get_cache_key(full_prompt)
        if use_cache:
            cached_response = cache.get(cache_key)
            if cached_response:
                cached_response["cached"] = True
                cached_response["response_time"] = time.time() - start_time
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
                    "success": True,
                    "text": response.text,
                    "tokens_used": tokens_used,
                    "cost": float(cost),
                    "response_time": response_time,
                    "model": self.model_name,
                    "cached": False,
                    "prompt_hash": cache_key,
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
                    wait_time = 2**attempt
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    # Final attempt failed
                    logger.error(f"All retry attempts failed: {str(e)}")
                    return {
                        "success": False,
                        "error": str(e),
                        "text": None,
                        "tokens_used": 0,
                        "cost": 0.0,
                        "response_time": time.time() - start_time,
                        "model": self.model_name,
                        "cached": False,
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
            prompt, system_context, include_cultural_context
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
        include_cultural_context: bool = True,
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

        input_cost = Decimal(str(input_tokens / 1000)) * self.INPUT_TOKEN_COST
        output_cost = Decimal(str(output_tokens / 1000)) * self.OUTPUT_TOKEN_COST

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

    def chat_with_ai(
        self,
        user_message: str,
        context: Optional[str] = None,
        conversation_history: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Helper function specifically for the OBCMS chat widget.

        Optimized for conversational responses with OBCMS domain knowledge.

        Args:
            user_message: The user's chat message
            context: Optional additional context (e.g., current page, user role)
            conversation_history: Optional list of previous exchanges
                Format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]

        Returns:
            Dict containing:
                - success: bool (True if successful, False on error)
                - message: str (AI response or error message)
                - tokens_used: int (token count)
                - cost: float (API cost in USD)
                - response_time: float (seconds)
                - suggestions: list[str] (follow-up suggestions)
                - cached: bool (whether response was cached)

        Example:
            >>> service = GeminiService(temperature=0.8)  # More creative for chat
            >>> result = service.chat_with_ai(
            ...     user_message="How many communities are in Region IX?",
            ...     context="User viewing Communities dashboard"
            ... )
            >>> print(result['message'])
            'Based on the latest data, there are 47 Bangsamoro communities...'
            >>> print(result['suggestions'])
            ['Show me details about these communities', 'Which provinces have the most?']
        """
        try:
            # Build OBCMS chat system context
            system_context = self._build_chat_system_context(context)

            # Build full prompt with conversation history
            full_prompt = self._build_chat_prompt(
                user_message=user_message,
                system_context=system_context,
                conversation_history=conversation_history,
            )

            # Generate response
            response_result = self.generate_text(
                prompt=full_prompt,
                system_context=None,  # Already included in full_prompt
                use_cache=True,
                cache_ttl=3600,  # 1 hour cache for chat (shorter than default)
                include_cultural_context=True,
            )

            if not response_result["success"]:
                # Return user-friendly error
                return {
                    "success": False,
                    "message": self._get_user_friendly_error(
                        response_result.get("error", "Unknown error")
                    ),
                    "tokens_used": 0,
                    "cost": 0.0,
                    "response_time": response_result.get("response_time", 0),
                    "suggestions": self._get_fallback_suggestions(),
                    "cached": False,
                }

            # Parse AI response to extract message and suggestions
            parsed_response = self._parse_chat_response(response_result["text"])

            return {
                "success": True,
                "message": parsed_response["message"],
                "tokens_used": response_result["tokens_used"],
                "cost": response_result["cost"],
                "response_time": response_result["response_time"],
                "suggestions": parsed_response["suggestions"],
                "cached": response_result.get("cached", False),
            }

        except Exception as e:
            logger.error(f"Chat error: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": self._get_user_friendly_error(str(e)),
                "tokens_used": 0,
                "cost": 0.0,
                "response_time": 0,
                "suggestions": self._get_fallback_suggestions(),
                "cached": False,
            }

    def _build_chat_system_context(self, additional_context: Optional[str] = None) -> str:
        """
        Build system context specifically for OBCMS chat assistant.

        Includes information about available data and capabilities.
        """
        base_context = """You are the OBCMS AI Assistant, helping staff at the Office for Other Bangsamoro Communities (OOBC) access and understand data.

OBCMS MODULES AND DATA YOU CAN HELP WITH:

1. **Communities Module**
   - OBC (Other Bangsamoro Communities) profiles and demographics
   - Geographic data: Regions IX, X, XI, XII (outside BARMM)
   - Ethnolinguistic groups: Maranao, Maguindanao, Tausug, Sama-Bajau, Yakan, etc.
   - Provincial and municipal community distribution

2. **MANA (Mapping and Needs Assessment)**
   - Community needs assessments across sectors
   - Priority needs identification (Health, Education, Infrastructure, Livelihood, etc.)
   - Assessment status tracking (Draft, Under Review, Approved, Published)
   - Regional and community-level assessment data

3. **Coordination Module**
   - Multi-stakeholder partnerships (NGOs, LGUs, national agencies)
   - Workshops and capacity-building activities
   - Partnership agreements and MOAs
   - Resource coordination and allocation

4. **Policy Recommendations**
   - Evidence-based policy proposals
   - Policy tracking and implementation status
   - Impact assessments and monitoring
   - Compliance with Islamic principles and Bangsamoro cultural values

5. **Project Management (Project Central)**
   - Programs, Projects, and Activities (PPAs) from various MOAs
   - Budget allocation and execution tracking
   - Timeline and milestone monitoring
   - Performance metrics and reporting

YOUR CAPABILITIES:
- Answer questions about OBCMS data ("How many communities...", "Show me...", "What is...")
- Provide summaries and insights from stored data
- Help navigate the OBCMS system
- Explain OBCMS features and processes
- Respect Bangsamoro cultural context in all responses

RESPONSE GUIDELINES:
- Be concise but informative (2-4 sentences for simple queries)
- Use natural, conversational language
- Include specific numbers and data when available
- Always be culturally sensitive (see Bangsamoro context below)
- Suggest relevant follow-up questions
- If you don't have data, say so clearly and suggest alternatives

RESPONSE FORMAT:
Provide your response as natural text, then on a new line starting with "SUGGESTIONS:", provide 2-3 brief follow-up questions the user might ask next."""

        if additional_context:
            base_context += f"\n\nADDITIONAL CONTEXT:\n{additional_context}"

        return base_context

    def _build_chat_prompt(
        self,
        user_message: str,
        system_context: str,
        conversation_history: Optional[list] = None,
    ) -> str:
        """Build full chat prompt with conversation history."""
        parts = [f"SYSTEM CONTEXT:\n{system_context}\n"]

        # Add cultural context
        parts.append(
            f"BANGSAMORO CULTURAL CONTEXT:\n"
            f"{self.cultural_context.get_base_context()}\n"
        )

        # Add conversation history if provided
        if conversation_history:
            parts.append("CONVERSATION HISTORY:")
            for exchange in conversation_history[-5:]:  # Last 5 exchanges only
                role = exchange.get("role", "user")
                content = exchange.get("content", "")
                parts.append(f"{role.upper()}: {content}")
            parts.append("")  # Blank line separator

        # Add current user message
        parts.append(f"USER: {user_message}\n")
        parts.append(
            "ASSISTANT: (Respond naturally, then add 'SUGGESTIONS:' with 2-3 follow-up questions)"
        )

        return "\n".join(parts)

    def _parse_chat_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse AI response to extract message and suggestions.

        Expected format:
        Main response text here...

        SUGGESTIONS:
        - Follow-up question 1
        - Follow-up question 2
        """
        parts = response_text.split("SUGGESTIONS:", 1)

        message = parts[0].strip()
        suggestions = []

        if len(parts) > 1:
            # Extract suggestions
            suggestions_text = parts[1].strip()
            for line in suggestions_text.split("\n"):
                line = line.strip()
                if line:
                    # Remove leading dash or bullet
                    clean_line = line.lstrip("- •*").strip()
                    if clean_line:
                        suggestions.append(clean_line)

        # Fallback suggestions if none provided
        if not suggestions:
            suggestions = self._get_fallback_suggestions()

        return {"message": message, "suggestions": suggestions[:3]}  # Max 3 suggestions

    def _get_user_friendly_error(self, error_str: str) -> str:
        """
        Convert technical error messages to user-friendly ones.

        Args:
            error_str: Technical error message

        Returns:
            User-friendly error message
        """
        error_lower = error_str.lower()

        # API key errors
        if "api key" in error_lower or "authentication" in error_lower:
            return (
                "I'm having trouble connecting to the AI service. "
                "Please contact your system administrator."
            )

        # Rate limit errors
        if "rate limit" in error_lower or "quota" in error_lower:
            return (
                "I'm currently experiencing high demand. "
                "Please try again in a few moments."
            )

        # Timeout errors
        if "timeout" in error_lower or "timed out" in error_lower:
            return (
                "The request took too long to process. "
                "Please try a simpler question or try again later."
            )

        # Network errors
        if (
            "network" in error_lower
            or "connection" in error_lower
            or "dns" in error_lower
        ):
            return (
                "I'm having trouble connecting to the network. "
                "Please check your internet connection and try again."
            )

        # Content policy errors
        if "safety" in error_lower or "policy" in error_lower:
            return (
                "I couldn't process that request due to content guidelines. "
                "Please try rephrasing your question."
            )

        # Generic fallback
        return (
            "I encountered an issue while processing your request. "
            "Please try again or contact support if the problem persists."
        )

    def _get_fallback_suggestions(self) -> list[str]:
        """Get default follow-up suggestions when AI doesn't provide any."""
        return [
            "How many communities are in Region IX?",
            "Show me recent MANA assessments",
            "What can you help me with?",
        ]
