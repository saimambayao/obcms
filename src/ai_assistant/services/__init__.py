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

from .cache_service import CacheService, PolicyCacheManager
from .gemini_service import GeminiService
from .prompt_templates import PromptTemplates

# Import existing services if they exist
try:
    from .embedding_service import EmbeddingService
    from .similarity_search import SimilaritySearchService
    from .vector_store import VectorStore

    __all__ = [
        'GeminiService',
        'CacheService',
        'PolicyCacheManager',
        'PromptTemplates',
        'EmbeddingService',
        'VectorStore',
        'SimilaritySearchService',
    ]
except ImportError:
    __all__ = [
        'GeminiService',
        'CacheService',
        'PolicyCacheManager',
        'PromptTemplates',
    ]
