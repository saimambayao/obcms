"""URL configuration for Monitoring & Evaluation API endpoints."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import MonitoringEntryViewSet, MonitoringUpdateViewSet
from .api import (
    StrategicGoalViewSet,
    AnnualPlanningCycleViewSet,
    BudgetScenarioViewSet,
    ScenarioAllocationViewSet,
)

app_name = "monitoring_api"

router = DefaultRouter()

# Phase 3: PPA WorkItem Integration APIs
# The following custom actions are registered on MonitoringEntryViewSet:
#   - POST /entries/{id}/enable-workitem-tracking/
#   - GET  /entries/{id}/budget-allocation-tree/
#   - POST /entries/{id}/distribute-budget/
#   - POST /entries/{id}/sync-from-workitem/
router.register(r"entries", MonitoringEntryViewSet)
router.register(r"updates", MonitoringUpdateViewSet)

# Phase 5: Strategic Planning APIs
router.register(r"strategic-goals", StrategicGoalViewSet, basename="strategic-goal")
router.register(
    r"planning-cycles", AnnualPlanningCycleViewSet, basename="planning-cycle"
)

# Phase 6: Scenario Planning & Budget Optimization APIs
router.register(r"scenarios", BudgetScenarioViewSet, basename="scenario")
router.register(r"allocations", ScenarioAllocationViewSet, basename="allocation")

urlpatterns = [path("", include(router.urls))]
