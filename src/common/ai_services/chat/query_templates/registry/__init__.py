"""
Advanced Template Registry Infrastructure for OBCMS Chat System

Provides enhanced registry capabilities with lazy loading, trie indexing,
and multi-level caching for scaling to 500+ templates while maintaining
<10ms match performance.

Architecture:
- LazyTemplateLoader: On-demand template loading by category
- PatternTrie: Efficient pattern prefix matching to reduce search space
- AdvancedTemplateRegistry: Enhanced registry with all optimizations

Usage:
    from common.ai_services.chat.query_templates.registry import get_advanced_registry

    registry = get_advanced_registry()
    templates = registry.search_templates("how many communities in Region IX")
"""

from common.ai_services.chat.query_templates.registry.template_loader import (
    LazyTemplateLoader,
)
from common.ai_services.chat.query_templates.registry.pattern_trie import PatternTrie
from common.ai_services.chat.query_templates.registry.advanced_registry import (
    AdvancedTemplateRegistry,
    get_advanced_registry,
)

__all__ = [
    'LazyTemplateLoader',
    'PatternTrie',
    'AdvancedTemplateRegistry',
    'get_advanced_registry',
]
