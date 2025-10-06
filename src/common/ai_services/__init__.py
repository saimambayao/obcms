"""
Common AI Services for OBCMS

This module provides cross-module AI services including:
- Unified semantic search across all modules
- Natural language query parsing
- Cross-module result ranking
- Search analytics and pattern tracking
- Conversational AI chat assistant
"""

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
    'UnifiedSearchEngine',
    'QueryParser',
    'ResultRanker',
    'SearchAnalytics',
    'HAS_UNIFIED_SEARCH',
    'ConversationalAssistant',
    'ConversationManager',
    'get_conversational_assistant',
    'get_conversation_manager',
    'HAS_CHAT',
]
