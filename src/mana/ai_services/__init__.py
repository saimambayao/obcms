"""
MANA AI Services
AI-powered analysis and intelligence for Mapping and Needs Assessment
"""

import logging

logger = logging.getLogger(__name__)

# Optional AI services - gracefully handle missing dependencies
try:
    from .response_analyzer import ResponseAnalyzer
    from .theme_extractor import ThemeExtractor
    from .needs_extractor import NeedsExtractor
    from .report_generator import AssessmentReportGenerator
    from .cultural_validator import BangsomoroCulturalValidator

    AI_SERVICES_AVAILABLE = True

except ImportError as e:
    AI_SERVICES_AVAILABLE = False
    logger.warning(
        f"MANA AI services could not be loaded - AI features will be disabled. "
        f"Error: {e}. Install AI dependencies with: pip install -r requirements/ai.txt"
    )

    # Create stub classes for when AI is not available
    class ResponseAnalyzer:
        """Stub class - AI features disabled"""
        def __init__(self):
            raise RuntimeError("AI services not available - missing dependencies")

    class ThemeExtractor:
        """Stub class - AI features disabled"""
        def __init__(self):
            raise RuntimeError("AI services not available - missing dependencies")

    class NeedsExtractor:
        """Stub class - AI features disabled"""
        def __init__(self):
            raise RuntimeError("AI services not available - missing dependencies")

    class AssessmentReportGenerator:
        """Stub class - AI features disabled"""
        def __init__(self):
            raise RuntimeError("AI services not available - missing dependencies")

    class BangsomoroCulturalValidator:
        """Stub class - AI features disabled"""
        def __init__(self):
            raise RuntimeError("AI services not available - missing dependencies")

__all__ = [
    'ResponseAnalyzer',
    'ThemeExtractor',
    'NeedsExtractor',
    'AssessmentReportGenerator',
    'BangsomoroCulturalValidator',
    'AI_SERVICES_AVAILABLE',
]
