"""
AI Services for Project Management (M&E/PPAs)

This package provides AI-powered capabilities for:
- Anomaly detection (budget overruns, timeline delays)
- Automated reporting (quarterly/monthly M&E reports)
- Performance forecasting (completion dates, budget utilization)
- Risk analysis (identifying project risks)
"""

from .anomaly_detector import PPAAnomalyDetector
from .report_generator import MEReportGenerator
from .performance_forecaster import PerformanceForecaster
from .risk_analyzer import RiskAnalyzer

__all__ = [
    'PPAAnomalyDetector',
    'MEReportGenerator',
    'PerformanceForecaster',
    'RiskAnalyzer',
]
