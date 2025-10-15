"""
AI Assistant Services

This module provides core AI services including:
- Gemini API integration for text generation
- Redis caching layer for AI responses
- Prompt templates for common operations
- Embedding generation for semantic search
- Vector store for similarity matching
- Semantic search across OBCMS modules
"""

import logging

from .cache_service import CacheService, PolicyCacheManager
from .gemini_service import GeminiService
from .prompt_templates import PromptTemplates

logger = logging.getLogger(__name__)

# Import embedding and search services if they exist (heavy ML dependencies)
try:
    from .embedding_service import EmbeddingService
    HAS_EMBEDDING_SERVICE = True
except ImportError as e:
    EmbeddingService = None
    HAS_EMBEDDING_SERVICE = False
    logger.warning(f"EmbeddingService not available: {e}")

try:
    from .similarity_search import SimilaritySearchService, get_similarity_search_service
    HAS_SIMILARITY_SEARCH = True
except ImportError as e:
    SimilaritySearchService = None
    get_similarity_search_service = None
    HAS_SIMILARITY_SEARCH = False
    logger.warning(f"SimilaritySearchService not available: {e}")

try:
    from .vector_store import VectorStore
    HAS_VECTOR_STORE = True
except ImportError as e:
    VectorStore = None
    HAS_VECTOR_STORE = False
    logger.warning(f"VectorStore not available: {e}")

__all__ = [
    'GeminiService',
    'CacheService',
    'PolicyCacheManager',
    'PromptTemplates',
    'EmbeddingService',
    'VectorStore',
    'SimilaritySearchService',
    'get_similarity_search_service',
    'HAS_EMBEDDING_SERVICE',
    'HAS_SIMILARITY_SEARCH',
    'HAS_VECTOR_STORE',
]
