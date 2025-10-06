"""
Error Handler - Robust error handling for AI operations.

This module provides:
- Retry strategies with exponential backoff
- Error classification and handling
- Graceful degradation
- Error logging and reporting
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification."""
    API_ERROR = "api_error"
    RATE_LIMIT = "rate_limit"
    AUTHENTICATION = "authentication"
    TIMEOUT = "timeout"
    INVALID_REQUEST = "invalid_request"
    SERVER_ERROR = "server_error"
    NETWORK_ERROR = "network_error"
    UNKNOWN = "unknown"


@dataclass
class RetryStrategy:
    """Configuration for retry logic."""
    max_attempts: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    exponential_base: float = 2.0
    jitter: bool = True


class AIErrorHandler:
    """
    Comprehensive error handler for AI operations.

    Features:
    - Automatic retry with exponential backoff
    - Error classification and severity assignment
    - Graceful fallback responses
    - Detailed error logging
    """

    def __init__(self, retry_strategy: Optional[RetryStrategy] = None):
        """
        Initialize error handler.

        Args:
            retry_strategy: Retry configuration (default: standard strategy)
        """
        self.retry_strategy = retry_strategy or RetryStrategy()
        self.error_counts = {}

    def handle_with_retry(
        self,
        operation: Callable,
        operation_name: str,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute operation with retry logic.

        Args:
            operation: Function to execute
            operation_name: Name for logging
            *args, **kwargs: Arguments for operation

        Returns:
            Dict with success status and result/error
        """
        last_error = None

        for attempt in range(1, self.retry_strategy.max_attempts + 1):
            try:
                result = operation(*args, **kwargs)
                if attempt > 1:
                    logger.info(
                        f"{operation_name} succeeded on attempt {attempt}"
                    )
                return {
                    'success': True,
                    'result': result,
                    'attempts': attempt
                }

            except Exception as e:
                last_error = e
                error_info = self.classify_error(e)

                logger.warning(
                    f"{operation_name} failed (attempt {attempt}/"
                    f"{self.retry_strategy.max_attempts}): {str(e)} "
                    f"[{error_info['category'].value}]"
                )

                # Track error
                self._track_error(operation_name, error_info)

                # Check if should retry
                if not self._should_retry(error_info, attempt):
                    break

                # Calculate delay
                if attempt < self.retry_strategy.max_attempts:
                    delay = self._calculate_delay(attempt)
                    logger.info(f"Retrying in {delay:.2f}s...")
                    time.sleep(delay)

        # All retries failed
        error_info = self.classify_error(last_error)
        return {
            'success': False,
            'error': str(last_error),
            'error_info': error_info,
            'attempts': self.retry_strategy.max_attempts,
            'fallback_message': self._get_fallback_message(error_info)
        }

    def classify_error(self, error: Exception) -> Dict[str, Any]:
        """
        Classify error by category and severity.

        Args:
            error: Exception to classify

        Returns:
            Dict with error classification
        """
        error_str = str(error).lower()

        # Determine category
        if 'rate limit' in error_str or '429' in error_str:
            category = ErrorCategory.RATE_LIMIT
            severity = ErrorSeverity.HIGH
        elif 'timeout' in error_str:
            category = ErrorCategory.TIMEOUT
            severity = ErrorSeverity.MEDIUM
        elif 'authentication' in error_str or 'api key' in error_str or '401' in error_str:
            category = ErrorCategory.AUTHENTICATION
            severity = ErrorSeverity.CRITICAL
        elif 'invalid' in error_str or '400' in error_str:
            category = ErrorCategory.INVALID_REQUEST
            severity = ErrorSeverity.MEDIUM
        elif '500' in error_str or '502' in error_str or '503' in error_str:
            category = ErrorCategory.SERVER_ERROR
            severity = ErrorSeverity.HIGH
        elif 'network' in error_str or 'connection' in error_str:
            category = ErrorCategory.NETWORK_ERROR
            severity = ErrorSeverity.HIGH
        else:
            category = ErrorCategory.UNKNOWN
            severity = ErrorSeverity.MEDIUM

        return {
            'category': category,
            'severity': severity,
            'message': str(error),
            'type': type(error).__name__
        }

    def _should_retry(self, error_info: Dict, attempt: int) -> bool:
        """Determine if error should be retried."""
        # Don't retry authentication errors
        if error_info['category'] == ErrorCategory.AUTHENTICATION:
            return False

        # Don't retry invalid requests
        if error_info['category'] == ErrorCategory.INVALID_REQUEST:
            return False

        # Always retry rate limits and server errors
        if error_info['category'] in [
            ErrorCategory.RATE_LIMIT,
            ErrorCategory.SERVER_ERROR,
            ErrorCategory.TIMEOUT,
            ErrorCategory.NETWORK_ERROR
        ]:
            return attempt < self.retry_strategy.max_attempts

        # Retry unknown errors up to max attempts
        return attempt < self.retry_strategy.max_attempts

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate retry delay with exponential backoff."""
        delay = min(
            self.retry_strategy.base_delay * (
                self.retry_strategy.exponential_base ** (attempt - 1)
            ),
            self.retry_strategy.max_delay
        )

        # Add jitter to prevent thundering herd
        if self.retry_strategy.jitter:
            import random
            jitter = random.uniform(0, delay * 0.1)
            delay += jitter

        return delay

    def _track_error(self, operation_name: str, error_info: Dict):
        """Track error occurrence for monitoring."""
        key = f"{operation_name}:{error_info['category'].value}"
        self.error_counts[key] = self.error_counts.get(key, 0) + 1

    def _get_fallback_message(self, error_info: Dict) -> str:
        """Get user-friendly fallback message based on error."""
        fallbacks = {
            ErrorCategory.RATE_LIMIT: (
                "The AI service is currently experiencing high demand. "
                "Please try again in a few moments."
            ),
            ErrorCategory.TIMEOUT: (
                "The request took too long to process. "
                "Please try with a shorter or simpler request."
            ),
            ErrorCategory.AUTHENTICATION: (
                "AI service authentication failed. "
                "Please contact system administrator."
            ),
            ErrorCategory.INVALID_REQUEST: (
                "The request could not be processed. "
                "Please check your input and try again."
            ),
            ErrorCategory.SERVER_ERROR: (
                "The AI service is temporarily unavailable. "
                "Please try again later."
            ),
            ErrorCategory.NETWORK_ERROR: (
                "Network connection issue. "
                "Please check your connection and try again."
            ),
            ErrorCategory.UNKNOWN: (
                "An unexpected error occurred. "
                "Please try again or contact support if the issue persists."
            ),
        }

        return fallbacks.get(
            error_info['category'],
            fallbacks[ErrorCategory.UNKNOWN]
        )

    def get_error_stats(self) -> Dict[str, int]:
        """Get error statistics."""
        return dict(self.error_counts)

    def reset_error_stats(self):
        """Reset error statistics."""
        self.error_counts.clear()


class GracefulDegradation:
    """Provide graceful fallback responses when AI fails."""

    @staticmethod
    def get_fallback_response(
        operation_type: str,
        context: Optional[Dict] = None
    ) -> str:
        """
        Get fallback response when AI is unavailable.

        Args:
            operation_type: Type of operation (chat, analysis, etc.)
            context: Optional context data

        Returns:
            Fallback response text
        """
        fallbacks = {
            'chat': (
                "I apologize, but I'm currently unable to generate a response. "
                "Please try again in a moment, or contact support if the issue persists."
            ),
            'analysis': (
                "Unable to generate AI analysis at this time. "
                "Please review the policy manually or try again later."
            ),
            'document': (
                "Document generation is temporarily unavailable. "
                "Please try again later or use the manual document templates."
            ),
            'evidence_review': (
                "AI evidence review is currently unavailable. "
                "Please conduct manual evidence review using established guidelines."
            ),
            'cultural_guidance': (
                "AI cultural guidance is temporarily unavailable. "
                "Please consult with cultural advisors or refer to the Bangsamoro "
                "Cultural Context documentation."
            ),
        }

        return fallbacks.get(
            operation_type,
            "The AI service is temporarily unavailable. Please try again later."
        )

    @staticmethod
    def get_partial_response(
        operation_type: str,
        partial_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Get partial response when operation partially succeeds.

        Args:
            operation_type: Type of operation
            partial_data: Any partial data available

        Returns:
            Dict with partial response
        """
        return {
            'success': 'partial',
            'message': (
                "The AI service provided a partial response. "
                "Some information may be incomplete."
            ),
            'data': partial_data or {},
            'recommendation': (
                "Please review the partial results and supplement "
                "with manual analysis if needed."
            )
        }
