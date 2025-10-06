"""
Query Templates Package for OBCMS Chat System

This package contains pre-defined query templates that map natural language
patterns to Django ORM queries without requiring AI processing.

Performance: <50ms query generation
Coverage: 60+ templates for Communities and MANA modules
"""

# Import to auto-register all templates on module import
from .communities_mana_templates import (
    register_all_communities_mana_templates,
    register_communities_templates,
    register_mana_templates,
)

__all__ = [
    "register_all_communities_mana_templates",
    "register_communities_templates",
    "register_mana_templates",
]
