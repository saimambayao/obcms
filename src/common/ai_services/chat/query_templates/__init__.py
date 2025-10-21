"""
Query Templates for OBCMS Chat System

Pattern-based query templates that convert natural language into Django ORM queries.
Provides a structured approach to common queries without requiring AI.

Organization:
- base.py: Core template classes and registry
- communities.py: Community-related query templates
- mana.py: MANA workshop and assessment templates
- coordination.py: Coordination partnerships, organizations, meetings
- policies.py: Policy recommendation query templates
- projects.py: Project Central (PPA) query templates
- staff.py: Staff & user management, tasks, activity tracking templates [15 templates]
- general.py: System help, navigation, metadata queries [15 templates]
- geographic.py: Geographic queries (Region → Province → Municipality → Barangay)
- infrastructure.py: Infrastructure analysis templates (water, electricity, health, education)
- livelihood.py: Livelihood & economic templates (income, opportunities, challenges)
- stakeholders.py: Stakeholder network templates (leaders, influence, engagement)
- budget.py: Budget ceiling tracking templates (allocation, utilization, violations)
- temporal.py: Time-based queries (date ranges, trends, historical analysis) [30 templates]
- cross_domain.py: Cross-module relationships (Communities+MANA, MANA+Coordination, Pipeline) [40 templates]
- analytics.py: Advanced analytics (statistics, patterns, predictive) [30 templates]
- comparison.py: Comparative analysis (locations, ethnicities, metrics) [20 templates]

Usage:
    from common.ai_services.chat.query_templates import get_template_registry

    registry = get_template_registry()
    templates = registry.get_templates_by_category('communities')
"""

import logging

from common.ai_services.chat.query_templates.base import (
    QueryTemplate,
    TemplateRegistry,
    get_template_registry as _get_template_registry_base,
)

logger = logging.getLogger(__name__)

# =============================================================================
# AUTO-REGISTER ALL TEMPLATES ON MODULE IMPORT
# =============================================================================

def get_template_registry():
    """Return the global registry, lazy-loading templates if needed."""
    registry = _get_template_registry_base()
    if not registry.get_all_templates():
        # Lazy-load templates on first request (not at startup)
        _register_all_templates(registry=registry)
        logger.info("Templates lazy-loaded on first access")
    return registry


def get_template_matcher():
    """Lazy import to avoid circular dependency at module import time."""
    from common.ai_services.chat.template_matcher import get_template_matcher as _get_template_matcher

    return _get_template_matcher()


def _register_all_templates(registry=None):
    """
    Auto-register all query templates from all modules.

    This function is called automatically when the module is imported,
    ensuring all templates are available in the global registry.
    """
    registry = registry or _get_template_registry_base()

    # Import all template collections
    try:
        from common.ai_services.chat.query_templates.communities import COMMUNITIES_TEMPLATES
        registry.register_many(COMMUNITIES_TEMPLATES)
        logger.info(f"Registered {len(COMMUNITIES_TEMPLATES)} community templates")
    except Exception as e:
        logger.error(f"Failed to register community templates: {e}")

    try:
        from common.ai_services.chat.query_templates.mana import MANA_TEMPLATES
        registry.register_many(MANA_TEMPLATES)
        logger.info(f"Registered {len(MANA_TEMPLATES)} MANA templates")
    except Exception as e:
        logger.error(f"Failed to register MANA templates: {e}")

    try:
        from common.ai_services.chat.query_templates.coordination import COORDINATION_TEMPLATES
        registry.register_many(COORDINATION_TEMPLATES)
        logger.info(f"Registered {len(COORDINATION_TEMPLATES)} coordination templates")
    except Exception as e:
        logger.error(f"Failed to register coordination templates: {e}")

    try:
        from common.ai_services.chat.query_templates.policies import POLICIES_TEMPLATES
        registry.register_many(POLICIES_TEMPLATES)
        logger.info(f"Registered {len(POLICIES_TEMPLATES)} policy templates")
    except Exception as e:
        logger.error(f"Failed to register policy templates: {e}")

    try:
        from common.ai_services.chat.query_templates.projects import PROJECTS_TEMPLATES
        registry.register_many(PROJECTS_TEMPLATES)
        logger.info(f"Registered {len(PROJECTS_TEMPLATES)} project templates")
    except Exception as e:
        logger.error(f"Failed to register project templates: {e}")

    # Import from separate staff.py and general.py files
    try:
        from common.ai_services.chat.query_templates.staff import STAFF_TEMPLATES
        registry.register_many(STAFF_TEMPLATES)
        logger.info(f"Registered {len(STAFF_TEMPLATES)} staff templates")
    except Exception as e:
        logger.error(f"Failed to register staff templates: {e}")

    try:
        from common.ai_services.chat.query_templates.general import GENERAL_TEMPLATES
        registry.register_many(GENERAL_TEMPLATES)
        logger.info(f"Registered {len(GENERAL_TEMPLATES)} general templates")
    except Exception as e:
        logger.error(f"Failed to register general templates: {e}")

    try:
        from common.ai_services.chat.query_templates.geographic import GEOGRAPHIC_TEMPLATES
        registry.register_many(GEOGRAPHIC_TEMPLATES)
        logger.info(f"Registered {len(GEOGRAPHIC_TEMPLATES)} geographic templates")
    except Exception as e:
        logger.error(f"Failed to register geographic templates: {e}")

    # =========================================================================
    # WORKSTREAM 3: Quick Wins Templates (37 templates across 4 domains)
    # =========================================================================
    try:
        from common.ai_services.chat.query_templates.infrastructure import INFRASTRUCTURE_TEMPLATES
        registry.register_many(INFRASTRUCTURE_TEMPLATES)
        logger.info(f"Registered {len(INFRASTRUCTURE_TEMPLATES)} infrastructure templates")
    except Exception as e:
        logger.error(f"Failed to register infrastructure templates: {e}")

    try:
        from common.ai_services.chat.query_templates.livelihood import LIVELIHOOD_TEMPLATES
        registry.register_many(LIVELIHOOD_TEMPLATES)
        logger.info(f"Registered {len(LIVELIHOOD_TEMPLATES)} livelihood templates")
    except Exception as e:
        logger.error(f"Failed to register livelihood templates: {e}")

    try:
        from common.ai_services.chat.query_templates.stakeholders import STAKEHOLDER_TEMPLATES
        registry.register_many(STAKEHOLDER_TEMPLATES)
        logger.info(f"Registered {len(STAKEHOLDER_TEMPLATES)} stakeholder templates")
    except Exception as e:
        logger.error(f"Failed to register stakeholder templates: {e}")

    try:
        from common.ai_services.chat.query_templates.budget import BUDGET_TEMPLATES
        registry.register_many(BUDGET_TEMPLATES)
        logger.info(f"Registered {len(BUDGET_TEMPLATES)} budget templates")
    except Exception as e:
        logger.error(f"Failed to register budget templates: {e}")

    # =========================================================================
    # WORKSTREAM 6: New Query Categories (120 templates across 4 domains)
    # =========================================================================
    try:
        from common.ai_services.chat.query_templates.temporal import TEMPORAL_TEMPLATES
        registry.register_many(TEMPORAL_TEMPLATES)
        logger.info(f"Registered {len(TEMPORAL_TEMPLATES)} temporal templates")
    except Exception as e:
        logger.error(f"Failed to register temporal templates: {e}")

    try:
        from common.ai_services.chat.query_templates.cross_domain import CROSS_DOMAIN_TEMPLATES
        registry.register_many(CROSS_DOMAIN_TEMPLATES)
        logger.info(f"Registered {len(CROSS_DOMAIN_TEMPLATES)} cross-domain templates")
    except Exception as e:
        logger.error(f"Failed to register cross-domain templates: {e}")

    try:
        from common.ai_services.chat.query_templates.analytics import ANALYTICS_TEMPLATES
        registry.register_many(ANALYTICS_TEMPLATES)
        logger.info(f"Registered {len(ANALYTICS_TEMPLATES)} analytics templates")
    except Exception as e:
        logger.error(f"Failed to register analytics templates: {e}")

    try:
        from common.ai_services.chat.query_templates.comparison import COMPARISON_TEMPLATES
        registry.register_many(COMPARISON_TEMPLATES)
        logger.info(f"Registered {len(COMPARISON_TEMPLATES)} comparison templates")
    except Exception as e:
        logger.error(f"Failed to register comparison templates: {e}")

    # Log final stats
    stats = registry.get_stats()
    logger.info(
        f"Template registration complete: {stats['total_templates']} total templates "
        f"across {len(stats['categories'])} categories"
    )


# Auto-register templates when module is imported
# Skip during app startup if SKIP_TEMPLATE_INIT is set (speeds up deployment)
import os
if os.getenv('SKIP_TEMPLATE_INIT') != '1':
    _register_all_templates()


__all__ = [
    'QueryTemplate',
    'TemplateRegistry',
    'get_template_registry',
    'get_template_matcher',
]
