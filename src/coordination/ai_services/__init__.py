"""
AI Services for Coordination Module

This package provides AI-powered features for stakeholder matching,
partnership prediction, and meeting intelligence using Google Gemini.
"""

from .stakeholder_matcher import StakeholderMatcher
from .partnership_predictor import PartnershipPredictor
from .meeting_intelligence import MeetingIntelligence
from .resource_optimizer import ResourceOptimizer

__all__ = [
    'StakeholderMatcher',
    'PartnershipPredictor',
    'MeetingIntelligence',
    'ResourceOptimizer',
]
