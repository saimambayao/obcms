"""
Deprecated URL Redirect Middleware - Phase 0: URL Refactoring

This middleware provides backward compatibility during the URL refactoring migration.
It redirects old `common:` namespace URLs to their new module-specific namespaces.

**Transition Period:** 30 days after Phase 0 completion
**After Transition:** Remove this middleware from settings.MIDDLEWARE

**Migration Status:**
- Phase 0.2: Recommendations → policies: namespace
- Phase 0.3: MANA → mana: namespace
- Phase 0.4: Communities → communities: namespace
- Phase 0.5: Coordination → coordination: namespace

**Usage:**
1. Add to settings.MIDDLEWARE
2. Monitor deprecation warnings in logs
3. Update template references to new namespaces
4. After 30 days with zero usage, remove middleware
"""

import logging
import re
from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch
from urllib.parse import quote, unquote

logger = logging.getLogger(__name__)


class DeprecatedURLRedirectMiddleware:
    """
    Middleware to handle deprecated common: namespace URLs and redirect to new namespaces.

    This provides seamless backward compatibility during the Phase 0 URL refactoring migration.
    """

    # URL Mapping: old common: namespace → new module namespace
    URL_MAPPING = {
        # ============================================================================
        # RECOMMENDATIONS MODULE → policies: namespace (Phase 0.2)
        # ============================================================================
        'common:recommendations_home': 'policies:home',
        'common:recommendations_stats_cards': 'policies:stats_cards',
        'common:recommendations_new': 'policies:new',
        'common:recommendations_create': 'policies:create',
        'common:recommendations_autosave': 'policies:autosave',
        'common:recommendations_manage': 'policies:manage',
        'common:recommendations_programs': 'policies:programs',
        'common:recommendations_services': 'policies:services',
        'common:recommendations_view': 'policies:view',
        'common:recommendations_edit': 'policies:edit',
        'common:recommendations_delete': 'policies:delete',
        'common:recommendations_by_area': 'policies:by_area',

        # ============================================================================
        # MANA MODULE → mana: namespace (Phase 0.3)
        # ============================================================================
        'common:mana_home': 'mana:home',
        'common:mana_stats_cards': 'mana:stats_cards',
        'common:mana_regional_overview': 'mana:regional_overview',
        'common:mana_provincial_overview': 'mana:provincial_overview',
        'common:mana_provincial_card_detail': 'mana:provincial_card_detail',
        'common:mana_province_edit': 'mana:province_edit',
        'common:mana_province_delete': 'mana:province_delete',
        'common:mana_desk_review': 'mana:desk_review',
        'common:mana_survey_module': 'mana:survey_module',
        'common:mana_kii': 'mana:kii',
        'common:mana_playbook': 'mana:playbook',
        'common:mana_activity_planner': 'mana:activity_planner',
        'common:mana_activity_log': 'mana:activity_log',
        'common:mana_activity_processing': 'mana:activity_processing',
        'common:mana_new_assessment': 'mana:new_assessment',
        'common:mana_manage_assessments': 'mana:manage_assessments',
        'common:mana_assessment_detail': 'mana:assessment_detail',
        'common:mana_assessment_edit': 'mana:assessment_edit',
        'common:mana_assessment_delete': 'mana:assessment_delete',
        'common:mana_geographic_data': 'mana:geographic_data',

        # ============================================================================
        # COMMUNITIES MODULE → communities: namespace (Phase 0.4)
        # ============================================================================
        'common:communities_home': 'communities:communities_home',
        'common:communities_add': 'communities:communities_add',
        'common:communities_add_municipality': 'communities:communities_add_municipality',
        'common:communities_add_province': 'communities:communities_add_province',
        'common:communities_view': 'communities:communities_view',
        'common:communities_edit': 'communities:communities_edit',
        'common:communities_delete': 'communities:communities_delete',
        'common:communities_restore': 'communities:communities_restore',
        'common:communities_manage': 'communities:communities_manage',
        'common:communities_manage_municipal': 'communities:communities_manage_municipal',
        'common:communities_manage_barangay_obc': 'communities:communities_manage_barangay_obc',
        'common:communities_manage_municipal_obc': 'communities:communities_manage_municipal_obc',
        'common:communities_manage_provincial': 'communities:communities_manage_provincial',
        'common:communities_manage_provincial_obc': 'communities:communities_manage_provincial_obc',
        'common:communities_view_municipal': 'communities:communities_view_municipal',
        'common:communities_edit_municipal': 'communities:communities_edit_municipal',
        'common:communities_delete_municipal': 'communities:communities_delete_municipal',
        'common:communities_restore_municipal': 'communities:communities_restore_municipal',
        'common:communities_view_provincial': 'communities:communities_view_provincial',
        'common:communities_edit_provincial': 'communities:communities_edit_provincial',
        'common:communities_delete_provincial': 'communities:communities_delete_provincial',
        'common:communities_submit_provincial': 'communities:communities_submit_provincial',
        'common:communities_restore_provincial': 'communities:communities_restore_provincial',
        'common:communities_stakeholders': 'communities:communities_stakeholders',
        'common:location_centroid': 'communities:location_centroid',
        'common:import_communities': 'communities:import_csv',
        'common:export_communities': 'communities:export',
        'common:generate_obc_report': 'communities:generate_report',
        'common:data_guidelines': 'communities:data_guidelines',

        # ============================================================================
        # COORDINATION MODULE → coordination: namespace (Phase 0.5)
        # ============================================================================
        # Core Coordination
        'common:coordination_home': 'coordination:home',
        'common:coordination_events': 'coordination:events',
        'common:coordination_calendar': 'coordination:calendar',
        'common:coordination_view_all': 'coordination:view_all',
        'common:coordination_activity_add': 'coordination:activity_add',
        'common:coordination_activity_create': 'coordination:activity_create',
        'common:coordination_note_add': 'coordination:note_add',
        'common:coordination_note_create': 'coordination:note_create',
        'common:coordination_note_activity_options': 'coordination:note_activity_options',

        # Organizations
        'common:coordination_organizations': 'coordination:organizations',
        'common:coordination_organization_add': 'coordination:organization_add',
        'common:coordination_organization_edit': 'coordination:organization_edit',
        'common:coordination_organization_delete': 'coordination:organization_delete',
        'common:coordination_organization_work_items_partial': 'coordination:organization_work_items_partial',
        'common:coordination_organization_detail': 'coordination:organization_detail',

        # Partnerships
        'common:coordination_partnerships': 'coordination:partnerships',
        'common:coordination_partnership_add': 'coordination:partnership_add',
        'common:coordination_partnership_view': 'coordination:partnership_view',
        'common:coordination_partnership_edit': 'coordination:partnership_edit',
        'common:coordination_partnership_delete': 'coordination:partnership_delete',

        # Calendar Resources
        'common:calendar_resource_list': 'coordination:calendar_resource_list',
        'common:calendar_resource_create': 'coordination:calendar_resource_create',
        'common:calendar_resource_detail': 'coordination:calendar_resource_detail',
        'common:calendar_resource_edit': 'coordination:calendar_resource_edit',
        'common:calendar_resource_delete': 'coordination:calendar_resource_delete',
        'common:calendar_resource_calendar': 'coordination:calendar_resource_calendar',
        'common:calendar_booking_request': 'coordination:calendar_booking_request',
        'common:calendar_booking_list': 'coordination:calendar_booking_list',
        'common:calendar_booking_request_general': 'coordination:calendar_booking_request_general',
        'common:calendar_booking_approve': 'coordination:calendar_booking_approve',
        'common:coordination_resource_bookings_feed': 'coordination:resource_bookings_feed',
        'common:coordination_check_conflicts': 'coordination:check_conflicts',
        'common:coordination_resource_booking_form': 'coordination:resource_booking_form',

        # Staff Leave
        'common:staff_leave_list': 'coordination:staff_leave_list',
        'common:staff_leave_request': 'coordination:staff_leave_request',
        'common:staff_leave_approve': 'coordination:staff_leave_approve',

        # Calendar Sharing
        'common:calendar_share_create': 'coordination:calendar_share_create',
        'common:calendar_share_manage': 'coordination:calendar_share_manage',
        'common:calendar_share_view': 'coordination:calendar_share_view',
        'common:calendar_share_toggle': 'coordination:calendar_share_toggle',
        'common:calendar_share_delete': 'coordination:calendar_share_delete',
    }

    def __init__(self, get_response):
        self.get_response = get_response
        self.usage_count = 0  # Track deprecated URL usage

    def __call__(self, request):
        """Process each request to detect and redirect deprecated URLs."""
        # Check if request path matches a deprecated URL pattern
        deprecated_url = self._get_deprecated_url_name(request.path)

        if deprecated_url and deprecated_url in self.URL_MAPPING:
            # Log deprecation warning
            self._log_deprecation(request, deprecated_url)

            # Get new URL and redirect
            new_url_name = self.URL_MAPPING[deprecated_url]
            try:
                new_path = self._build_new_path(request.path, deprecated_url, new_url_name)
                if new_path:
                    logger.info(f"Redirecting {request.path} → {new_path}")
                    return redirect(new_path, permanent=True)  # 301 redirect
            except NoReverseMatch as e:
                logger.error(f"Failed to reverse {new_url_name}: {e}")

        response = self.get_response(request)
        return response

    def _get_deprecated_url_name(self, path):
        """
        Extract the deprecated URL name from the request path.

        This is a heuristic approach - checks path patterns against known deprecated URLs.

        IMPORTANT: Only match paths that are NOT already in the new namespace location.
        For example, /coordination/* URLs are already migrated, so don't redirect them.
        """
        # Skip URLs that are already in their new namespace locations
        # These phases are complete and URLs are no longer deprecated:

        # Phase 6: OCM aggregation layer (never deprecated)
        if path.startswith('/ocm/'):
            return None

        # Phase 0.5: Coordination (complete)
        if path.startswith('/coordination/'):
            return None

        # Phase 0.4: Communities (complete)
        if path.startswith('/communities/'):
            return None

        # Phase 0.3: MANA (complete)
        if path.startswith('/mana/'):
            return None

        # Phase 0.2: Recommendations/Policies (complete)
        if path.startswith('/policies/'):
            return None

        # Recommendations patterns
        if '/recommendations/' in path:
            if path.endswith('/recommendations/'):
                return 'common:recommendations_home'
            elif '/recommendations/new/' in path:
                return 'common:recommendations_new'
            elif '/recommendations/manage/' in path:
                return 'common:recommendations_manage'
            elif '/recommendations/programs/' in path:
                return 'common:recommendations_programs'
            elif '/recommendations/services/' in path:
                return 'common:recommendations_services'
            elif '/view/' in path:
                return 'common:recommendations_view'
            elif '/edit/' in path:
                return 'common:recommendations_edit'
            elif '/delete/' in path:
                return 'common:recommendations_delete'
            elif '/area/' in path:
                return 'common:recommendations_by_area'

        # MANA patterns
        if '/mana/' in path:
            if path.endswith('/mana/'):
                return 'common:mana_home'
            elif '/mana/regional/' in path:
                return 'common:mana_regional_overview'
            elif '/mana/provincial/' in path and '/edit/' in path:
                return 'common:mana_province_edit'
            elif '/mana/provincial/' in path and '/delete/' in path:
                return 'common:mana_province_delete'
            elif '/mana/provincial/' in path and not ('edit' in path or 'delete' in path):
                if path.count('/') == 4:  # /mana/provincial/<id>/
                    return 'common:mana_provincial_card_detail'
                else:
                    return 'common:mana_provincial_overview'
            elif '/mana/desk-review/' in path:
                return 'common:mana_desk_review'
            elif '/mana/survey/' in path:
                return 'common:mana_survey_module'
            elif '/mana/kii/' in path:
                return 'common:mana_kii'
            elif '/mana/playbook/' in path:
                return 'common:mana_playbook'
            elif '/mana/activity-planner/' in path:
                return 'common:mana_activity_planner'
            elif '/mana/activity-log/' in path:
                return 'common:mana_activity_log'
            elif '/mana/new-assessment/' in path:
                return 'common:mana_new_assessment'
            elif '/mana/manage-assessments/' in path and '/edit/' in path:
                return 'common:mana_assessment_edit'
            elif '/mana/manage-assessments/' in path and '/delete/' in path:
                return 'common:mana_assessment_delete'
            elif '/mana/manage-assessments/' in path and path.count('/') > 3:
                return 'common:mana_assessment_detail'
            elif '/mana/manage-assessments/' in path:
                return 'common:mana_manage_assessments'
            elif '/mana/geographic-data/' in path:
                return 'common:mana_geographic_data'

        # Communities patterns
        if '/communities/' in path:
            if path.endswith('/communities/'):
                return 'common:communities_home'
            elif '/communities/add-municipality/' in path:
                return 'common:communities_add_municipality'
            elif '/communities/add-province/' in path:
                return 'common:communities_add_province'
            elif '/communities/add/' in path:
                return 'common:communities_add'
            elif '/communities/managemunicipal/' in path:
                return 'common:communities_manage_municipal'
            elif '/communities/managebarangayobc/' in path:
                return 'common:communities_manage_barangay_obc'
            elif '/communities/managemunicipalobc/' in path:
                return 'common:communities_manage_municipal_obc'
            elif '/communities/manageprovincial/' in path:
                return 'common:communities_manage_provincial'
            elif '/communities/manageprovincialobc/' in path:
                return 'common:communities_manage_provincial_obc'
            elif '/communities/manage/' in path:
                return 'common:communities_manage'
            elif '/communities/municipal/' in path and '/edit/' in path:
                return 'common:communities_edit_municipal'
            elif '/communities/municipal/' in path and '/delete/' in path:
                return 'common:communities_delete_municipal'
            elif '/communities/municipal/' in path and '/restore/' in path:
                return 'common:communities_restore_municipal'
            elif '/communities/municipal/' in path:
                return 'common:communities_view_municipal'
            elif '/communities/province/' in path and '/edit/' in path:
                return 'common:communities_edit_provincial'
            elif '/communities/province/' in path and '/delete/' in path:
                return 'common:communities_delete_provincial'
            elif '/communities/province/' in path and '/submit/' in path:
                return 'common:communities_submit_provincial'
            elif '/communities/province/' in path and '/restore/' in path:
                return 'common:communities_restore_provincial'
            elif '/communities/province/' in path:
                return 'common:communities_view_provincial'
            elif '/communities/stakeholders/' in path:
                return 'common:communities_stakeholders'
            elif '/edit/' in path:
                return 'common:communities_edit'
            elif '/delete/' in path:
                return 'common:communities_delete'
            elif '/restore/' in path:
                return 'common:communities_restore'
            elif path.count('/') >= 3 and re.search(r'/communities/\d+/', path):
                return 'common:communities_view'

        # Data management
        if '/communities/import/' in path:
            return 'common:import_communities'
        if '/communities/export/' in path:
            return 'common:export_communities'
        if '/communities/report/' in path:
            return 'common:generate_obc_report'
        if '/data-guidelines/' in path:
            return 'common:data_guidelines'
        if '/locations/centroid/' in path:
            return 'common:location_centroid'

        # Coordination patterns
        if '/coordination/' in path:
            if path.endswith('/coordination/'):
                return 'common:coordination_home'
            elif '/coordination/organizations/' in path and '/edit/' in path:
                return 'common:coordination_organization_edit'
            elif '/coordination/organizations/' in path and '/delete/' in path:
                return 'common:coordination_organization_delete'
            elif '/coordination/organizations/' in path and '/work-items/partial/' in path:
                return 'common:coordination_organization_work_items_partial'
            elif '/coordination/organizations/' in path and '/add/' in path:
                return 'common:coordination_organization_add'
            elif '/coordination/organizations/' in path and path.count('/') > 3:
                return 'common:coordination_organization_detail'
            elif '/coordination/organizations/' in path:
                return 'common:coordination_organizations'
            elif '/coordination/partnerships/' in path and '/edit/' in path:
                return 'common:coordination_partnership_edit'
            elif '/coordination/partnerships/' in path and '/delete/' in path:
                return 'common:coordination_partnership_delete'
            elif '/coordination/partnerships/' in path and '/add/' in path:
                return 'common:coordination_partnership_add'
            elif '/coordination/partnerships/' in path and path.count('/') > 3:
                return 'common:coordination_partnership_view'
            elif '/coordination/partnerships/' in path:
                return 'common:coordination_partnerships'
            elif '/coordination/events/' in path:
                return 'common:coordination_events'
            elif '/coordination/calendar/' in path:
                return 'common:coordination_calendar'
            elif '/coordination/view-all/' in path:
                return 'common:coordination_view_all'
            elif '/coordination/activities/add/' in path:
                return 'common:coordination_activity_add'
            elif '/coordination/notes/add/' in path:
                return 'common:coordination_note_add'
            elif '/coordination/notes/activity-options/' in path:
                return 'common:coordination_note_activity_options'
            elif '/coordination/resources/' in path and '/bookings/feed/' in path:
                return 'common:coordination_resource_bookings_feed'
            elif '/coordination/resources/check-conflicts/' in path:
                return 'common:coordination_check_conflicts'
            elif '/coordination/resources/' in path and '/book-enhanced/' in path:
                return 'common:coordination_resource_booking_form'

        # Calendar resource management patterns
        if '/oobc-management/calendar/resources/' in path:
            if '/oobc-management/calendar/resources/add/' in path:
                return 'common:calendar_resource_create'
            elif '/oobc-management/calendar/resources/' in path and '/edit/' in path:
                return 'common:calendar_resource_edit'
            elif '/oobc-management/calendar/resources/' in path and '/delete/' in path:
                return 'common:calendar_resource_delete'
            elif '/oobc-management/calendar/resources/' in path and '/calendar/' in path:
                return 'common:calendar_resource_calendar'
            elif '/oobc-management/calendar/resources/' in path and '/book/' in path:
                return 'common:calendar_booking_request'
            elif '/oobc-management/calendar/resources/' in path and path.count('/') > 4:
                return 'common:calendar_resource_detail'
            elif path.endswith('/oobc-management/calendar/resources/'):
                return 'common:calendar_resource_list'

        if '/oobc-management/calendar/bookings/' in path:
            if '/oobc-management/calendar/bookings/request/' in path:
                return 'common:calendar_booking_request_general'
            elif '/oobc-management/calendar/bookings/' in path and '/approve/' in path:
                return 'common:calendar_booking_approve'
            elif path.endswith('/oobc-management/calendar/bookings/'):
                return 'common:calendar_booking_list'

        # Staff leave patterns
        if '/oobc-management/staff/leave/' in path:
            if '/oobc-management/staff/leave/request/' in path:
                return 'common:staff_leave_request'
            elif '/oobc-management/staff/leave/' in path and '/approve/' in path:
                return 'common:staff_leave_approve'
            elif path.endswith('/oobc-management/staff/leave/'):
                return 'common:staff_leave_list'

        # Calendar sharing patterns
        if '/oobc-management/calendar/share/' in path:
            if path.endswith('/oobc-management/calendar/share/'):
                return 'common:calendar_share_create'
            elif '/oobc-management/calendar/share/manage/' in path:
                return 'common:calendar_share_manage'
            elif '/oobc-management/calendar/share/' in path and '/toggle/' in path:
                return 'common:calendar_share_toggle'
            elif '/oobc-management/calendar/share/' in path and '/delete/' in path:
                return 'common:calendar_share_delete'

        if '/calendar/shared/' in path:
            return 'common:calendar_share_view'

        return None

    def _build_new_path(self, old_path, old_url_name, new_url_name):
        """
        Build the new path from the old path.

        This preserves URL parameters and path segments while changing the namespace.
        """
        # For now, simple path replacement
        # Extract module from new namespace (e.g., 'communities:home' → 'communities')
        new_module = new_url_name.split(':')[0]
        new_name = new_url_name.split(':')[1]

        # Pattern replacements
        replacements = {
            # Recommendations
            '/recommendations/': f'/{new_module}/',

            # MANA
            '/mana/': f'/{new_module}/',

            # Communities
            '/communities/': f'/{new_module}/',
            '/locations/centroid/': f'/{new_module}/locations/centroid/',

            # Coordination
            '/coordination/': f'/{new_module}/',
            '/oobc-management/calendar/resources/': f'/{new_module}/calendar/resources/',
            '/oobc-management/calendar/bookings/': f'/{new_module}/calendar/bookings/',
            '/oobc-management/staff/leave/': f'/{new_module}/staff/leave/',
            '/oobc-management/calendar/share/': f'/{new_module}/calendar/share/',
            '/calendar/shared/': f'/{new_module}/calendar/shared/',
        }

        new_path = old_path
        for old_pattern, new_pattern in replacements.items():
            if old_pattern in old_path:
                new_path = old_path.replace(old_pattern, new_pattern, 1)
                break

        return new_path

    def _log_deprecation(self, request, deprecated_url):
        """Log deprecation warning with details."""
        self.usage_count += 1

        logger.warning(
            f"⚠️ DEPRECATED URL USED (#{self.usage_count}): {deprecated_url}\n"
            f"   Path: {request.path}\n"
            f"   Method: {request.method}\n"
            f"   User: {request.user if hasattr(request, 'user') else 'Anonymous'}\n"
            f"   Referer: {request.META.get('HTTP_REFERER', 'N/A')}\n"
            f"   New URL: {self.URL_MAPPING.get(deprecated_url, 'Unknown')}\n"
            f"   Action Required: Update template reference from {{% url '{deprecated_url}' %}} "
            f"to {{% url '{self.URL_MAPPING.get(deprecated_url, 'Unknown')}' %}}"
        )

        # Also log to console for development visibility
        print(f"\n🚨 DEPRECATED URL: {deprecated_url} → {self.URL_MAPPING.get(deprecated_url)}")
        print(f"   Update in template: {request.META.get('HTTP_REFERER', 'Unknown template')}\n")
