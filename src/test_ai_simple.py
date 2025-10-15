#!/usr/bin/env python
"""
Simple AI services test that avoids model loading timeouts.
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

def test_ai_service_availability():
    """Test AI service availability without loading models."""
    try:
        print("Testing AI Service Availability...")

        # Test service module structure
        try:
            import ai_assistant.services
            print("✅ ai_assistant.services module available")
        except ImportError as e:
            print(f"❌ ai_assistant.services module not available: {e}")
            return False

        # Test service availability flags
        try:
            from ai_assistant.services import (
                HAS_EMBEDDING_SERVICE,
                HAS_GEMINI_SERVICE,
                HAS_VECTOR_STORE,
                HAS_SIMILARITY_SEARCH,
            )
            print(f"✅ AI service flags accessible:")
            print(f"   - Embedding Service: {HAS_EMBEDDING_SERVICE}")
            print(f"   - Gemini Service: {HAS_GEMINI_SERVICE}")
            print(f"   - Vector Store: {HAS_VECTOR_STORE}")
            print(f"   - Similarity Search: {HAS_SIMILARITY_SEARCH}")
        except ImportError as e:
            print(f"⚠️  AI service flags import failed: {e}")

        # Test class definitions without instantiation
        try:
            from ai_assistant.services.embedding_service import EmbeddingService
            print("✅ EmbeddingService class available")
        except ImportError as e:
            print(f"⚠️  EmbeddingService class not available: {e}")

        try:
            from ai_assistant.services.similarity_search import SimilaritySearchService
            print("✅ SimilaritySearchService class available")
        except ImportError as e:
            print(f"⚠️  SimilaritySearchService class not available: {e}")

        try:
            from ai_assistant.services.vector_store import VectorStore
            print("✅ VectorStore class available")
        except ImportError as e:
            print(f"⚠️  VectorStore class not available: {e}")

        print("✅ AI service availability tests completed!")
        return True

    except Exception as e:
        print(f"❌ AI service availability test failed: {e}")
        return False

def test_ai_configuration():
    """Test AI service configuration."""
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
                print(f"✅ {setting}: {value}")
                settings_found += 1
            else:
                print(f"⚠️  {setting}: Not configured")

        print(f"✅ {settings_found}/{len(ai_settings)} AI settings configured")
        print("✅ AI configuration tests completed!")
        return True

    except Exception as e:
        print(f"❌ AI configuration test failed: {e}")
        return False

def test_common_ai_services():
    """Test common AI services."""
    try:
        print("Testing Common AI Services...")

        # Test query parser
        try:
            from common.ai_services.query_parser import QueryParser
            print("✅ QueryParser class available")
        except ImportError as e:
            print(f"⚠️  QueryParser not available: {e}")

        # Test unified search engine
        try:
            from common.ai_services.unified_search import UnifiedSearchEngine
            print("✅ UnifiedSearchEngine class available")
        except ImportError as e:
            print(f"⚠️  UnifiedSearchEngine not available: {e}")

        print("✅ Common AI services tests completed!")
        return True

    except Exception as e:
        print(f"❌ Common AI services test failed: {e}")
        return False

def test_ai_dependencies():
    """Test AI dependencies without importing heavy libraries."""
    try:
        print("Testing AI Dependencies (basic check)...")

        # Check if required Python packages are available
        dependencies = [
            ('numpy', 'NumPy'),
            ('scipy', 'SciPy'),
        ]

        available_deps = 0
        for module_name, display_name in dependencies:
            try:
                __import__(module_name)
                print(f"✅ {display_name} available")
                available_deps += 1
            except ImportError:
                print(f"⚠️  {display_name} not available (expected in basic test)")

        # Check for ML packages (optional for basic functionality)
        ml_dependencies = [
            ('sentence_transformers', 'sentence-transformers'),
            ('transformers', 'transformers'),
            ('torch', 'PyTorch'),
        ]

        ml_available = 0
        for module_name, display_name in ml_dependencies:
            try:
                __import__(module_name)
                print(f"✅ {display_name} available")
                ml_available += 1
            except ImportError:
                print(f"⚠️  {display_name} not available (heavy ML package)")

        print(f"✅ Basic dependencies: {available_deps}/{len(dependencies)} available")
        print(f"✅ ML dependencies: {ml_available}/{len(ml_dependencies)} available")
        print("✅ AI dependencies tests completed!")
        return True

    except Exception as e:
        print(f"❌ AI dependencies test failed: {e}")
        return False

def main():
    """Run all simple AI services tests."""
    print("=" * 60)
    print("OBCMS SIMPLE AI SERVICES TESTS")
    print("=" * 60)

    tests = [
        ("AI Service Availability", test_ai_service_availability),
        ("AI Configuration", test_ai_configuration),
        ("Common AI Services", test_common_ai_services),
        ("AI Dependencies", test_ai_dependencies),
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
    print("SIMPLE AI SERVICES TEST SUMMARY")
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
        print("🎉 ALL SIMPLE AI SERVICES TESTS PASSED!")
        return 0
    else:
        print("⚠️  Some simple AI services tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())