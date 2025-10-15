#!/usr/bin/env python
"""
Basic AI services test that doesn't load heavy models.
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

def test_ai_basic_imports():
    """Test basic AI imports without loading models."""
    try:
        print("Testing Basic AI Imports...")

        # Test 1: Check AI assistant module structure
        try:
            import ai_assistant.services
            print("✅ ai_assistant.services module available")
        except ImportError as e:
            print(f"❌ ai_assistant.services module not available: {e}")
            return False

        # Test 2: Check individual service modules
        service_modules = [
            'ai_assistant.services.embedding_service',
            'ai_assistant.services.gemini_service',
            'ai_assistant.services.vector_store',
            'ai_assistant.services.similarity_search',
        ]

        for module_name in service_modules:
            try:
                __import__(module_name)
                print(f"✅ {module_name} available")
            except ImportError as e:
                print(f"⚠️  {module_name} not available: {e}")

        # Test 3: Check common AI services
        common_ai_modules = [
            'common.ai_services.query_parser',
            'common.ai_services.unified_search',
        ]

        for module_name in common_ai_modules:
            try:
                __import__(module_name)
                print(f"✅ {module_name} available")
            except ImportError as e:
                print(f"⚠️  {module_name} not available: {e}")

        print("✅ Basic AI imports tests completed!")
        return True

    except Exception as e:
        print(f"❌ Basic AI imports test failed: {e}")
        return False

def test_ai_service_flags():
    """Test AI service availability flags."""
    try:
        print("Testing AI Service Flags...")

        # Import service flags
        try:
            from ai_assistant.services import (
                HAS_EMBEDDING_SERVICE,
                HAS_GEMINI_SERVICE,
                HAS_VECTOR_STORE,
                HAS_SIMILARITY_SEARCH,
            )
            print(f"✅ Service flags imported successfully")
            print(f"   - Embedding Service: {HAS_EMBEDDING_SERVICE}")
            print(f"   - Gemini Service: {HAS_GEMINI_SERVICE}")
            print(f"   - Vector Store: {HAS_VECTOR_STORE}")
            print(f"   - Similarity Search: {HAS_SIMILARITY_SEARCH}")
        except ImportError as e:
            print(f"⚠️  Service flags import failed: {e}")

        print("✅ AI service flags tests completed!")
        return True

    except Exception as e:
        print(f"❌ AI service flags test failed: {e}")
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

def test_ai_dependencies():
    """Test AI service dependencies."""
    try:
        print("Testing AI Dependencies...")

        # Test key AI dependencies
        dependencies = [
            ('sentence_transformers', 'sentence-transformers'),
            ('transformers', 'transformers'),
            ('torch', 'PyTorch'),
            ('numpy', 'NumPy'),
            ('sklearn', 'scikit-learn'),
        ]

        available_deps = 0
        for module_name, display_name in dependencies:
            try:
                __import__(module_name)
                print(f"✅ {display_name} available")
                available_deps += 1
            except ImportError:
                print(f"⚠️  {display_name} not available")

        print(f"✅ {available_deps}/{len(dependencies)} AI dependencies available")
        print("✅ AI dependencies tests completed!")
        return True

    except Exception as e:
        print(f"❌ AI dependencies test failed: {e}")
        return False

def test_ai_models_structure():
    """Test AI model classes structure."""
    try:
        print("Testing AI Model Classes Structure...")

        # Test embedding service class
        try:
            from ai_assistant.services.embedding_service import EmbeddingService
            print("✅ EmbeddingService class available")
        except ImportError as e:
            print(f"⚠️  EmbeddingService class not available: {e}")

        # Test similarity search class
        try:
            from ai_assistant.services.similarity_search import SimilaritySearchService
            print("✅ SimilaritySearchService class available")
        except ImportError as e:
            print(f"⚠️  SimilaritySearchService class not available: {e}")

        # Test vector store class
        try:
            from ai_assistant.services.vector_store import VectorStore
            print("✅ VectorStore class available")
        except ImportError as e:
            print(f"⚠️  VectorStore class not available: {e}")

        # Test unified search class
        try:
            from common.ai_services.unified_search import UnifiedSearchEngine
            print("✅ UnifiedSearchEngine class available")
        except ImportError as e:
            print(f"⚠️  UnifiedSearchEngine class not available: {e}")

        print("✅ AI model classes structure tests completed!")
        return True

    except Exception as e:
        print(f"❌ AI model classes structure test failed: {e}")
        return False

def main():
    """Run all basic AI services tests."""
    print("=" * 60)
    print("OBCMS BASIC AI SERVICES TESTS")
    print("=" * 60)

    tests = [
        ("Basic AI Imports", test_ai_basic_imports),
        ("AI Service Flags", test_ai_service_flags),
        ("AI Configuration", test_ai_configuration),
        ("AI Dependencies", test_ai_dependencies),
        ("AI Model Classes Structure", test_ai_models_structure),
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
    print("BASIC AI SERVICES TEST SUMMARY")
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
        print("🎉 ALL BASIC AI SERVICES TESTS PASSED!")
        return 0
    else:
        print("⚠️  Some basic AI services tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())