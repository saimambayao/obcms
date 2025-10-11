from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]

TEMPLATE_CASES = [
    pytest.param(
        "communities",
        "src/templates/communities/provincial_manage.html",
        [
            '''hx-get="{% url 'common:communities_manage_provincial' %}"''',
            '''hx-target="#provincial-results-container"''',
            '''hx-trigger="change from:select, submit"''',
        ],
        id="communities-provincial-filters",
    ),
    pytest.param(
        "communities",
        "src/templates/communities/partials/provincial_manage_results.html",
        ['''components/data_table_card.html'''],
        id="communities-provincial-table-card",
    ),
    pytest.param(
        "coordination",
        "src/templates/coordination/resource_booking_form.html",
        [
            '''hx-get="{% url 'common:coordination_check_conflicts' %}"''',
            '''hx-target="#conflict-warnings"''',
            '''hx-trigger="change delay:500ms"''',
        ],
        id="coordination-resource-booking-conflict-check",
    ),
    pytest.param(
        "coordination",
        "src/templates/coordination/event_attendance_tracker.html",
        [
            '''hx-get="{% url 'common:coordination_event_attendance_count' event_id=event.id %}"''',
            '''hx-trigger="load, every 10s"''',
            '''class="min-h-[300px] flex items-center justify-center"''',
        ],
        id="coordination-event-attendance-refresh",
    ),
    pytest.param(
        "mana",
        "src/templates/mana/mana_assessment_detail_ai.html",
        [
            '''hx-get="{% url 'mana:ai_response_analysis' assessment.id %}"''',
            '''hx-trigger="load"''',
            '''hx-swap="innerHTML"''',
        ],
        id="mana-assessment-ai-panels",
    ),
    pytest.param(
        "mana",
        "src/templates/mana/mana_assessment_edit.html",
        [
            '''components/form_field_select.html''',
            '''components/form_field.html''',
        ],
        id="mana-assessment-form-components",
    ),
    pytest.param(
        "policies",
        "src/templates/recommendations/recommendations_new.html",
        [
            '''class="w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] transition-all duration-200"''',
            '''Example: Policy framework for OBC rights protection''',
        ],
        id="policies-creation-form-standards",
    ),
    pytest.param(
        "recommendations",
        "src/templates/recommendations/recommendations_home.html",
        [
            '''hx-get="{% url 'common:recommendations_stats_cards' %}"''',
            '''hx-trigger="load, every 60s"''',
            '''hx-swap="innerHTML swap:300ms"''',
        ],
        id="recommendations-home-live-stats",
    ),
    pytest.param(
        "policy_tracking",
        "src/templates/recommendations/policy_tracking/widgets/evidence_dashboard.html",
        [
            '''toggleEvidenceSources()''',
            '''bg-gradient-to-br from-blue-500 to-teal-500''',
        ],
        id="policy-tracking-evidence-dashboard",
    ),
    pytest.param(
        "policy_tracking",
        "src/templates/recommendations/policy_tracking/widgets/impact_simulation.html",
        [
            '''scenario-tab px-4 py-2 text-sm font-medium border-b-2 transition-colors''',
            '''bg-gradient-to-br from-blue-50 to-blue-100''',
        ],
        id="policy-tracking-impact-scenarios",
    ),
    pytest.param(
        "documents",
        "src/templates/recommendations/documents/library_dashboard.html",
        ['''components/data_table_card.html'''],
        id="documents-ui-missing",
        marks=pytest.mark.xfail(
            reason="Documents module UI templates are not yet implemented.",
            strict=False,
        ),
    ),
    pytest.param(
        "project_central",
        "src/templates/project_central/portfolio_dashboard.html",
        [
            '''{% url 'project_central:alert_list' %}''',
            '''inline-flex items-center justify-center rounded-xl bg-white text-emerald-600 font-semibold px-4 py-2.5 shadow hover:bg-emerald-50 transition-all duration-200''',
        ],
        id="project-central-portfolio-dashboard",
    ),
    pytest.param(
        "project_central",
        "src/templates/project_central/ai_insights_section.html",
        [
            '''hx-get="{% url 'project_central:ai_anomaly_detection' project.id %}"''',
            '''hx-trigger="load"''',
            '''hx-swap="innerHTML"''',
        ],
        id="project-central-ai-insights",
    ),
    pytest.param(
        "ai_assistant",
        "src/templates/components/ai_chat_widget.html",
        [
            '''hx-post="{% url 'common:chat_message' %}"''',
            '''hx-on::before-request="prepareMessage(event)"''',
            '''aria-live="polite"''',
        ],
        id="ai-assistant-chat-widget",
    ),
    pytest.param(
        "monitoring",
        "src/templates/monitoring/partials/_ppa_work_item_row.html",
        [
            '''hx-get="{% url 'common:work_item_tree_partial' pk=work_item.pk %}"''',
            '''data-hx-target="#ppa-sidebar-content"''',
            '''data-work-item-id="{{ work_item.id }}"''',
        ],
        id="monitoring-ppa-work-item-row",
    ),
    pytest.param(
        "common",
        "src/templates/common/dashboard.html",
        [
            '''hx-get="{% url 'common:dashboard_stats_cards' %}"''',
            '''hx-trigger="load, every 60s"''',
            '''hx-swap="innerHTML swap:300ms"''',
        ],
        id="common-dashboard-live-stats",
    ),
    pytest.param(
        "data_imports",
        "src/templates/data_imports/import_dashboard.html",
        ['''hx-post'''],
        id="data-imports-ui-missing",
        marks=pytest.mark.xfail(
            reason="Data imports module lacks dedicated UI templates.",
            strict=False,
        ),
    ),
    pytest.param(
        "common dashboards & analytics",
        "src/templates/common/analytics_dashboard.html",
        [
            '''bg-white rounded-xl shadow-sm border border-gray-200 p-6''',
            '''bg-gradient-to-r from-purple-500 to-blue-600''',
        ],
        id="common-analytics-dashboard",
    ),
]


@pytest.mark.parametrize("module, template_path, expected_snippets", TEMPLATE_CASES)
def test_frontend_ui_components_follow_standards(module, template_path, expected_snippets):
    template_file = REPO_ROOT / template_path
    assert template_file.exists(), f"{module} template missing: {template_path}"
    content = template_file.read_text()
    for snippet in expected_snippets:
        assert (
            snippet in content
        ), f"{module} template {template_path} missing snippet: {snippet}"
