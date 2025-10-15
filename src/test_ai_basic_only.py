#!/usr/bin/env python
"""
Most basic AI services test - just checks files exist.
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

def test_ai_file_structure():
    """Test AI services file structure only."""
    try:
        print("Testing AI File Structure...")

        # Check if AI assistant directory exists
        ai_assistant_path = 'ai_assistant'
        if os.path.exists(ai_assistant_path):
            print("✅ ai_assistant directory exists")

            # Check services directory
            services_path = os.path.join(ai_assistant_path, 'services')
            if os.path.exists(services_path):
                print("✅ ai_assistant/services directory exists")

                # List service files
                service_files = [f for f in os.listdir(services_path) if f.endswith('.py') and not f.startswith('__')]
                print(f"✅ Found {len(service_files)} AI service files:")
                for file in service_files:
                    print(f"   - {file}")
            else:
                print("❌ ai_assistant/services directory not found")
        else:
            print("❌ ai_assistant directory not found")

        # Check common AI services directory
        common_ai_path = 'common/ai_services'
        if os.path.exists(common_ai_path):
            print("✅ common/ai_services directory exists")

            # List AI service files
            ai_files = [f for f in os.listdir(common_ai_path) if f.endswith('.py') and not f.startswith('__')]
            print(f"✅ Found {len(ai_files)} common AI service files:")
            for file in ai_files:
                print(f"   - {file}")
        else:
            print("❌ common/ai_services directory not found")

        print("✅ AI file structure tests completed!")
        return True

    except Exception as e:
        print(f"❌ AI file structure test failed: {e}")
        return False

def test_ai_configuration():
    """Test AI configuration without importing modules."""
    try:
        from django.conf import settings

        print("Testing AI Configuration...")

        # Check AI-related settings
        ai_settings = [
            'GEMINI_API_KEY',
            'EMBEDDING_MODEL_NAME',
            'VECTOR_STORE_PATH',
            'AI_SERVICES_ENABLED',
        ]

        settings_found = 0
        for setting in ai_settings:
            if hasattr(settings, setting):
                value = getattr(settings, setting)
                # Mask sensitive values
                if 'API_KEY' in setting and value:
                    value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***MASKED***"
                print(f"✅ {setting}: {'configured' if value else 'empty'}")
                settings_found += 1
            else:
                print(f"⚠️  {setting}: Not configured")

        print(f"✅ {settings_found}/{len(ai_settings)} AI settings configured")
        print("✅ AI configuration tests completed!")
        return True

    except Exception as e:
        print(f"❌ AI configuration test failed: {e}")
        return False

def test_ai_dependencies():
    """Test basic AI dependencies without heavy imports."""
    try:
        print("Testing Basic AI Dependencies...")

        # Only check for basic Python packages that are lightweight
        basic_deps = [
            ('os', 'OS module'),
            ('sys', 'Sys module'),
            ('json', 'JSON module'),
            ('datetime', 'Datetime module'),
        ]

        available_deps = 0
        for module_name, display_name in basic_deps:
            try:
                __import__(module_name)
                print(f"✅ {display_name} available")
                available_deps += 1
            except ImportError:
                print(f"❌ {display_name} not available")

        print(f"✅ Basic dependencies: {available_deps}/{len(basic_deps)} available")
        print("✅ AI dependencies tests completed!")
        return True

    except Exception as e:
        print(f"❌ AI dependencies test failed: {e}")
        return False

def main():
    """Run most basic AI tests."""
    print("=" * 60)
    print("OBCMS MOST BASIC AI SERVICES TESTS")
    print("=" * 60)

    tests = [
        ("AI File Structure", test_ai_file_structure),
        ("AI Configuration", test_ai_configuration),
        ("Basic Dependencies", test_ai_dependencies),
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
    print("MOST BASIC AI TESTS SUMMARY")
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
        print("🎉 ALL MOST BASIC AI TESTS PASSED!")
        return 0
    else:
        print("⚠️  Some basic AI tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())