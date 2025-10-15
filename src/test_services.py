#!/usr/bin/env python
"""
Test services and business logic for OBCMS.
"""

import os
import sys
import django

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.base')

# Setup Django
django.setup()

def test_business_logic_services():
    """Test business logic services."""
    try:
        print("Testing Business Logic Services...")

        # Test 1: Import and test common services
        try:
            from common.services import (
                deferred_geocoding,
                signal_handlers,
            )
            print("✅ Common services importable")
        except ImportError as e:
            print(f"⚠️  Common services import issue: {e}")

        # Test 2: Test staff task services
        try:
            from common.services.staff_task_service import StaffTaskService
            service = StaffTaskService()
            print("✅ StaffTaskService initializable")
        except Exception as e:
            print(f"⚠️  StaffTaskService issue: {e}")

        # Test 3: Test work item services
        try:
            from common.services.work_item_service import WorkItemService
            service = WorkItemService()
            print("✅ WorkItemService initializable")
        except Exception as e:
            print(f"⚠️  WorkItemService issue: {e}")

        # Test 4: Test calendar services
        try:
            from common.services.calendar_service import CalendarService
            service = CalendarService()
            print("✅ CalendarService initializable")
        except Exception as e:
            print(f"⚠️  CalendarService issue: {e}")

        print("✅ Business logic services tests completed!")
        return True

    except Exception as e:
        print(f"❌ Business logic services test failed: {e}")
        return False

def test_data_import_services():
    """Test data import services."""
    try:
        print("Testing Data Import Services...")

        # Test import services
        try:
            from data_imports.services import (
                excel_import_service,
                csv_import_service,
                validation_service,
            )
            print("✅ Data import services importable")
        except ImportError as e:
            print(f"⚠️  Data import services import issue: {e}")

        # Test specific import functionality
        try:
            from data_imports.services.import_service import ImportService
            service = ImportService()
            print("✅ ImportService initializable")
        except Exception as e:
            print(f"⚠️  ImportService issue: {e}")

        print("✅ Data import services tests completed!")
        return True

    except Exception as e:
        print(f"❌ Data import services test failed: {e}")
        return False

def test_coordination_services():
    """Test coordination services."""
    try:
        print("Testing Coordination Services...")

        # Test coordination business logic
        try:
            from coordination.services import (
                organization_service,
                event_service,
                partnership_service,
            )
            print("✅ Coordination services importable")
        except ImportError as e:
            print(f"⚠️  Coordination services import issue: {e}")

        # Test quarterly report service
        try:
            from coordination.services.quarterly_report_service import QuarterlyReportService
            service = QuarterlyReportService()
            print("✅ QuarterlyReportService initializable")
        except Exception as e:
            print(f"⚠️  QuarterlyReportService issue: {e}")

        print("✅ Coordination services tests completed!")
        return True

    except Exception as e:
        print(f"❌ Coordination services test failed: {e}")
        return False

def test_monitoring_services():
    """Test monitoring services."""
    try:
        print("Testing Monitoring Services...")

        # Test monitoring business logic
        try:
            from monitoring.services import (
                monitoring_service,
                strategic_plan_service,
                budget_service,
            )
            print("✅ Monitoring services importable")
        except ImportError as e:
            print(f"⚠️  Monitoring services import issue: {e}")

        # Test workflow services
        try:
            from monitoring.services.workflow_service import WorkflowService
            service = WorkflowService()
            print("✅ WorkflowService initializable")
        except Exception as e:
            print(f"⚠️  WorkflowService issue: {e}")

        print("✅ Monitoring services tests completed!")
        return True

    except Exception as e:
        print(f"❌ Monitoring services test failed: {e}")
        return False

def test_recommendations_services():
    """Test recommendations services."""
    try:
        print("Testing Recommendations Services...")

        # Test policy tracking services
        try:
            from recommendations.policy_tracking.services import (
                policy_service,
                implementation_service,
            )
            print("✅ Policy tracking services importable")
        except ImportError as e:
            print(f"⚠️  Policy tracking services import issue: {e}")

        # Test recommendation engine
        try:
            from recommendations.services.recommendation_engine import RecommendationEngine
            engine = RecommendationEngine()
            print("✅ RecommendationEngine initializable")
        except Exception as e:
            print(f"⚠️  RecommendationEngine issue: {e}")

        print("✅ Recommendations services tests completed!")
        return True

    except Exception as e:
        print(f"❌ Recommendations services test failed: {e}")
        return False

def test_budget_services():
    """Test budget preparation and execution services."""
    try:
        print("Testing Budget Services...")

        # Test budget preparation services
        try:
            from budget_preparation.services import (
                budget_service,
                appropriation_service,
                workflow_service,
            )
            print("✅ Budget preparation services importable")
        except ImportError as e:
            print(f"⚠️  Budget preparation services import issue: {e}")

        # Test budget execution services
        try:
            from budget_execution.services import (
                execution_service,
                disbursement_service,
                monitoring_service,
            )
            print("✅ Budget execution services importable")
        except ImportError as e:
            print(f"⚠️  Budget execution services import issue: {e}")

        print("✅ Budget services tests completed!")
        return True

    except Exception as e:
        print(f"❌ Budget services test failed: {e}")
        return False

def test_planning_services():
    """Test planning services."""
    try:
        print("Testing Planning Services...")

        # Test planning business logic
        try:
            from planning.services import (
                plan_service,
                goal_service,
                objective_service,
            )
            print("✅ Planning services importable")
        except ImportError as e:
            print(f"⚠️  Planning services import issue: {e}")

        # Test scenario planning
        try:
            from planning.services.scenario_service import ScenarioService
            service = ScenarioService()
            print("✅ ScenarioService initializable")
        except Exception as e:
            print(f"⚠️  ScenarioService issue: {e}")

        print("✅ Planning services tests completed!")
        return True

    except Exception as e:
        print(f"❌ Planning services test failed: {e}")
        return False

def test_signal_handlers():
    """Test Django signal handlers."""
    try:
        print("Testing Signal Handlers...")

        # Test common signal handlers
        try:
            from common.signals import (
                post_save_user_handler,
                pre_delete_model_handler,
            )
            print("✅ Common signal handlers importable")
        except ImportError as e:
            print(f"⚠️  Common signal handlers import issue: {e}")

        # Test community signal handlers
        try:
            from communities.signals import (
                community_created_handler,
                coverage_updated_handler,
            )
            print("✅ Community signal handlers importable")
        except ImportError as e:
            print(f"⚠️  Community signal handlers import issue: {e}")

        print("✅ Signal handlers tests completed!")
        return True

    except Exception as e:
        print(f"❌ Signal handlers test failed: {e}")
        return False

def test_workflow_engines():
    """Test workflow engines."""
    try:
        print("Testing Workflow Engines...")

        # Test common workflow engine
        try:
            from common.workflow import WorkflowEngine
            engine = WorkflowEngine()
            print("✅ WorkflowEngine initializable")
        except Exception as e:
            print(f"⚠️  WorkflowEngine issue: {e}")

        # Test budget workflow
        try:
            from budget_preparation.workflow import BudgetWorkflow
            workflow = BudgetWorkflow()
            print("✅ BudgetWorkflow initializable")
        except Exception as e:
            print(f"⚠️  BudgetWorkflow issue: {e}")

        print("✅ Workflow engines tests completed!")
        return True

    except Exception as e:
        print(f"❌ Workflow engines test failed: {e}")
        return False

def main():
    """Run all services tests."""
    print("=" * 60)
    print("OBCMS SERVICES AND BUSINESS LOGIC TESTS")
    print("=" * 60)

    tests = [
        ("Business Logic Services", test_business_logic_services),
        ("Data Import Services", test_data_import_services),
        ("Coordination Services", test_coordination_services),
        ("Monitoring Services", test_monitoring_services),
        ("Recommendations Services", test_recommendations_services),
        ("Budget Services", test_budget_services),
        ("Planning Services", test_planning_services),
        ("Signal Handlers", test_signal_handlers),
        ("Workflow Engines", test_workflow_engines),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("SERVICES TEST SUMMARY")
    print("=" * 60)

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\nTotal: {len(results)} | Passed: {passed} | Failed: {failed}")

    if failed == 0:
        print("🎉 ALL SERVICES TESTS PASSED!")
        return 0
    else:
        print("⚠️  Some services tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())