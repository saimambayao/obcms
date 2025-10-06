"""
Common AI Services for OBCMS

This module provides cross-module AI services including:
- Unified semantic search across all modules
- Natural language query parsing
- Cross-module result ranking
- Search analytics and pattern tracking
- Conversational AI chat assistant
- Entity extraction for natural language queries
"""

# Entity Extraction (no AI, no external dependencies)
from .chat.entity_extractor import EntityExtractor
from .chat.entity_resolvers import (
    LocationResolver,
    EthnicGroupResolver,
    LivelihoodResolver,
    DateRangeResolver,
    StatusResolver,
    NumberResolver,
)

# Unified Search (requires EmbeddingService - optional)
try:
    from .unified_search import UnifiedSearchEngine
    from .query_parser import QueryParser
    from .result_ranker import ResultRanker
    from .search_analytics import SearchAnalytics
    HAS_UNIFIED_SEARCH = True
except ImportError:
    UnifiedSearchEngine = None
    QueryParser = None
    ResultRanker = None
    SearchAnalytics = None
    HAS_UNIFIED_SEARCH = False

# Conversational AI Chat (requires GeminiService)
try:
    from .chat import (
        ConversationalAssistant,
        ConversationManager,
        get_conversational_assistant,
        get_conversation_manager,
    )
    HAS_CHAT = True
except ImportError:
    ConversationalAssistant = None
    ConversationManager = None
    get_conversational_assistant = None
    get_conversation_manager = None
    HAS_CHAT = False

__all__ = [
    # Entity Extraction
    'EntityExtractor',
    'LocationResolver',
    'EthnicGroupResolver',
    'LivelihoodResolver',
    'DateRangeResolver',
    'StatusResolver',
    'NumberResolver',
    # Unified Search
    'UnifiedSearchEngine',
    'QueryParser',
    'ResultRanker',
    'SearchAnalytics',
    'HAS_UNIFIED_SEARCH',
    # Conversational AI
    'ConversationalAssistant',
    'ConversationManager',
    'get_conversational_assistant',
    'get_conversation_manager',
    'HAS_CHAT',
]
