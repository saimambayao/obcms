#!/usr/bin/env python
"""
Verify all OBCMS URLs are properly configured.

This script checks that all expected URL patterns from the integrated
project management system and other modules are correctly registered.
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings')
django.setup()

from django.urls import get_resolver, NoReverseMatch


def check_urls():
    """Check all expected URLs exist."""
    resolver = get_resolver()

    expected_urls = [
        # Phase 1: Foundation & Dashboard
        ('common:dashboard', 'Dashboard'),
        ('common:dashboard_metrics', 'Dashboard Metrics API (if exists)'),
        ('common:dashboard_activity', 'Dashboard Activity Feed (if exists)'),
        ('common:dashboard_alerts', 'Dashboard Alerts (if exists)'),

        # Phase 4: Project Management Portal Foundation
        ('project_central:portfolio_dashboard', 'Portfolio Dashboard'),
        ('project_central:dashboard', 'Project Management Portal Dashboard (alias)'),
        ('project_central:project_list', 'Project List'),
        ('project_central:create_project_workflow', 'Create Project Workflow'),

        # Phase 5: Workflow & Budget Approval
        ('project_central:budget_approval_dashboard', 'Budget Approval Dashboard'),

        # Phase 6: M&E Analytics
        ('project_central:me_analytics_dashboard', 'M&E Analytics Dashboard'),
        ('project_central:sector_analytics', 'Sector Analytics'),
        ('project_central:geographic_analytics', 'Geographic Analytics'),

        # Phase 7: Alerts & Reporting
        ('project_central:alert_list', 'Alerts List'),
        ('project_central:report_list', 'Reports List'),

        # Budget Planning
        ('project_central:budget_planning_dashboard', 'Budget Planning Dashboard'),

        # Common URLs
        ('common:communities_home', 'Communities Home'),
        ('common:mana_home', 'MANA Home'),
        ('common:coordination_home', 'Coordination Home'),
        ('common:recommendations_home', 'Recommendations Home'),
        ('common:oobc_management_home', 'OOBC Management Home'),

        # Monitoring URLs
        ('monitoring:home', 'Monitoring Home'),
        ('monitoring:moa_ppas', 'MOA PPAs'),
        ('monitoring:oobc_initiatives', 'OOBC Initiatives'),
        ('monitoring:obc_requests', 'OBC Requests'),
    ]

    print("=" * 80)
    print("OBCMS URL Configuration Verification")
    print("=" * 80)
    print()

    missing = []
    found = []

    for url_name, description in expected_urls:
        try:
            # Try to reverse the URL
            resolver.reverse(url_name)
            print(f"✅ {url_name:<50} {description}")
            found.append((url_name, description))
        except NoReverseMatch:
            print(f"❌ {url_name:<50} {description} - MISSING")
            missing.append((url_name, description))

    print()
    print("=" * 80)
    print(f"Summary: {len(found)}/{len(expected_urls)} URLs found")
    print("=" * 80)

    if missing:
        print()
        print(f"⚠️  {len(missing)} URL(s) missing:")
        for url_name, description in missing:
            print(f"   - {url_name}: {description}")
        print()
        return False
    else:
        print()
        print(f"✅ All {len(expected_urls)} URLs configured correctly!")
        print()
        return True


if __name__ == '__main__':
    success = check_urls()
    sys.exit(0 if success else 1)
