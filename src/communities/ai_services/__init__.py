"""
AI Services for Communities Module

This package provides AI-powered features for community data validation,
needs classification, and similarity matching using Google Gemini.
"""

from .data_validator import CommunityDataValidator
from .needs_classifier import CommunityNeedsClassifier
from .community_matcher import CommunityMatcher

__all__ = [
    'CommunityDataValidator',
    'CommunityNeedsClassifier',
    'CommunityMatcher',
]
