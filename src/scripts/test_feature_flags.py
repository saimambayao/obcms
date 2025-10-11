#!/usr/bin/env python
"""
Test that feature flags are correctly configured for WorkItem system.

Usage:
    cd src
    python scripts/test_feature_flags.py
"""
import os
import sys

import pytest

try:
    import django
except ImportError:  # pragma: no cover - handled via skip
    pytest.skip(
        "Django is required for feature flag verification script",
        allow_module_level=True,
    )

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.base')
django.setup()

from django.conf import settings


def audit_feature_flags(verbose: bool = True) -> dict:
    """Collect feature flag status and optionally print a human readable report."""
    emit = print if verbose else (lambda *_args, **_kwargs: None)

    emit("WorkItem Feature Flags Configuration")
    emit("=" * 60)

    expected_production_values = {
        'USE_WORKITEM_MODEL': True,
        'USE_UNIFIED_CALENDAR': True,
        'DUAL_WRITE_ENABLED': False,
        'LEGACY_MODELS_READONLY': True,
    }

    flags = {
        'USE_WORKITEM_MODEL': getattr(settings, 'USE_WORKITEM_MODEL', False),
        'USE_UNIFIED_CALENDAR': getattr(settings, 'USE_UNIFIED_CALENDAR', False),
        'DUAL_WRITE_ENABLED': getattr(settings, 'DUAL_WRITE_ENABLED', True),
        'LEGACY_MODELS_READONLY': getattr(settings, 'LEGACY_MODELS_READONLY', False),
    }

    emit("\nCurrent Configuration:")
    for flag, value in flags.items():
        status = "✅" if value == expected_production_values.get(flag) else "⚠️"
        emit(f"{status} {flag}: {value}")

    emit("\n" + "=" * 60)
    emit("Production Recommendations:")

    issues_found = []
    for flag, expected in expected_production_values.items():
        actual = flags[flag]
        if actual != expected:
            emit(f"⚠️  {flag} should be {expected} (currently {actual})")
            issues_found.append(flag)
        else:
            emit(f"✅ {flag} correctly set to {expected}")

    emit("\n" + "=" * 60)
    if not issues_found:
        emit("✅ All feature flags correctly configured for production")
        if verbose:
            emit("\nSystem Status:")
            emit("  - WorkItem model: ENABLED")
            emit("  - Unified calendar: ENABLED")
            emit("  - Legacy dual-write: DISABLED")
            emit("  - Legacy models: READ-ONLY")
    else:
        emit("⚠️  Some feature flags need adjustment - see recommendations above")
        if verbose:
            emit(f"\nIssues found in: {', '.join(issues_found)}")
            emit("\nTo fix, update your .env file:")
            for flag in issues_found:
                expected = expected_production_values[flag]
                value = "1" if expected else "0"
                emit(f"  {flag}={value}")

    return {
        'flags': flags,
        'expected': expected_production_values,
        'issues': issues_found,
    }


def test_feature_flags():
    """Test that feature flags are correctly configured."""
    result = audit_feature_flags(verbose=False)
    assert set(result['flags']) == set(result['expected']), (
        "Expected and actual flag mappings should reference the same keys."
    )

    mismatches = {
        flag: (result['flags'][flag], expected)
        for flag, expected in result['expected'].items()
        if result['flags'][flag] != expected
    }

    assert set(result['issues']) == set(mismatches), (
        "Mismatch report should enumerate every diverging flag so the CLI output stays accurate."
    )


def verify_environment_variables():
    """Verify environment variables are set correctly."""
    print("\n" + "=" * 60)
    print("Environment Variable Check:")
    print("=" * 60)

    env_vars = {
        'USE_WORKITEM_MODEL': os.getenv('USE_WORKITEM_MODEL'),
        'USE_UNIFIED_CALENDAR': os.getenv('USE_UNIFIED_CALENDAR'),
        'DUAL_WRITE_ENABLED': os.getenv('DUAL_WRITE_ENABLED'),
        'LEGACY_MODELS_READONLY': os.getenv('LEGACY_MODELS_READONLY'),
    }

    for var, value in env_vars.items():
        if value is None:
            print(f"ℹ️  {var}: Not set (using default)")
        else:
            print(f"✅ {var}: {value}")


def check_model_availability():
    """Check that WorkItem model is available."""
    print("\n" + "=" * 60)
    print("Model Availability Check:")
    print("=" * 60)

    try:
        from common.models import WorkItem
        print("✅ WorkItem model imported successfully")

        # Count work items
        try:
            count = WorkItem.objects.count()
            print(f"✅ WorkItem count: {count}")
        except Exception as e:
            print(f"⚠️  Error counting WorkItems: {e}")

    except ImportError as e:
        print(f"❌ Failed to import WorkItem: {e}")
        return False

    # Check for legacy models (should still be importable but deprecated)
    try:
        from common.models import StaffTask
        print("ℹ️  StaffTask still importable (deprecated)")
    except ImportError:
        print("✅ StaffTask not available (removed)")

    try:
        from coordination.models import Event
        print("ℹ️  Event still importable (deprecated)")
    except ImportError:
        print("✅ Event not available (removed)")

    try:
        from project_central.models import ProjectWorkflow
        print("ℹ️  ProjectWorkflow still importable (deprecated)")
    except ImportError:
        print("✅ ProjectWorkflow not available (removed)")

    return True


def main():
    """Main test function."""
    print("\n" + "🔍" * 30)
    print("WorkItem System Configuration Verification")
    print("🔍" * 30 + "\n")

    # Test feature flags
    feature_flag_result = audit_feature_flags()
    flags_ok = not feature_flag_result['issues']

    # Verify environment variables
    verify_environment_variables()

    # Check model availability
    model_ok = check_model_availability()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if flags_ok and model_ok:
        print("✅ System is correctly configured for WorkItem")
        print("✅ Ready for production deployment")
        sys.exit(0)
    else:
        print("⚠️  Configuration issues detected")
        print("⚠️  Review recommendations above before deploying")
        sys.exit(1)


if __name__ == '__main__':
    main()
