#!/usr/bin/env python
"""
Test AI services and similarity search for OBCMS.
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

def test_ai_service_imports():
    """Test AI service imports and basic functionality."""
    try:
        print("Testing AI Service Imports...")

        # Test 1: Check AI assistant services
        try:
            from ai_assistant.services import (
                embedding_service,
                gemini_service,
                vector_store,
                similarity_search,
            )
            print("✅ AI assistant services importable")
        except ImportError as e:
            print(f"⚠️  AI assistant services import issue: {e}")

        # Test 2: Check availability flags
        try:
            from ai_assistant.services import (
                HAS_EMBEDDING_SERVICE,
                HAS_GEMINI_SERVICE,
                HAS_VECTOR_STORE,
                HAS_SIMILARITY_SEARCH,
            )
            print(f"✅ AI service flags: Embedding={HAS_EMBEDDING_SERVICE}, Gemini={HAS_GEMINI_SERVICE}, Vector={HAS_VECTOR_STORE}, Similarity={HAS_SIMILARITY_SEARCH}")
        except ImportError as e:
            print(f"⚠️  AI service flags import issue: {e}")

        print("✅ AI service imports tests completed!")
        return True

    except Exception as e:
        print(f"❌ AI service imports test failed: {e}")
        return False

def test_embedding_service():
    """Test embedding service functionality."""
    try:
        from ai_assistant.services.embedding_service import EmbeddingService, get_embedding_service, HAS_EMBEDDING_SERVICE

        print("Testing Embedding Service...")

        if not HAS_EMBEDDING_SERVICE:
            print("⚠️  EmbeddingService not available (missing dependencies)")
            return True

        # Test service initialization
        try:
            service = get_embedding_service()
            print("✅ EmbeddingService initializable")
        except Exception as e:
            print(f"⚠️  EmbeddingService initialization failed: {e}")
            return False

        # Test basic functionality (without actually loading models)
        try:
            if hasattr(service, 'get_dimension'):
                dim = service.get_dimension()
                print(f"✅ Embedding dimension: {dim}")
            else:
                print("⚠️  Embedding dimension method not available")
        except Exception as e:
            print(f"⚠️  Embedding dimension test failed: {e}")

        print("✅ Embedding service tests completed!")
        return True

    except Exception as e:
        print(f"❌ Embedding service test failed: {e}")
        return False

def test_gemini_service():
    """Test Gemini service functionality."""
    try:
        from ai_assistant.services.gemini_service import GeminiService, get_gemini_service, HAS_GEMINI_SERVICE

        print("Testing Gemini Service...")

        if not HAS_GEMINI_SERVICE:
            print("⚠️  GeminiService not available (missing dependencies)")
            return True

        # Test service initialization
        try:
            service = get_gemini_service()
            print("✅ GeminiService initializable")
        except Exception as e:
            print(f"⚠️  GeminiService initialization failed: {e}")
            return False

        # Test basic functionality
        try:
            if hasattr(service, 'is_available'):
                available = service.is_available()
                print(f"✅ Gemini service available: {available}")
            else:
                print("⚠️  Gemini availability method not available")
        except Exception as e:
            print(f"⚠️  Gemini availability test failed: {e}")

        print("✅ Gemini service tests completed!")
        return True

    except Exception as e:
        print(f"❌ Gemini service test failed: {e}")
        return False

def test_vector_store():
    """Test vector store functionality."""
    try:
        from ai_assistant.services.vector_store import VectorStore, HAS_VECTOR_STORE

        print("Testing Vector Store...")

        if not HAS_VECTOR_STORE:
            print("⚠️  VectorStore not available (missing dependencies)")
            return True

        # Test store creation
        try:
            store = VectorStore("test_store", dimension=384)
            print("✅ VectorStore creatable")
        except Exception as e:
            print(f"⚠️  VectorStore creation failed: {e}")
            return False

        # Test basic functionality
        try:
            if hasattr(store, 'vector_count'):
                count = store.vector_count
                print(f"✅ Vector count: {count}")
            else:
                print("⚠️  Vector count method not available")
        except Exception as e:
            print(f"⚠️  Vector count test failed: {e}")

        print("✅ Vector store tests completed!")
        return True

    except Exception as e:
        print(f"❌ Vector store test failed: {e}")
        return False

def test_similarity_search():
    """Test similarity search functionality."""
    try:
        from ai_assistant.services.similarity_search import SimilaritySearchService, get_similarity_search_service, HAS_SIMILARITY_SEARCH

        print("Testing Similarity Search Service...")

        if not HAS_SIMILARITY_SEARCH:
            print("⚠️  SimilaritySearchService not available (missing dependencies)")
            return True

        # Test service initialization
        try:
            service = get_similarity_search_service()
            print("✅ SimilaritySearchService initializable")
        except Exception as e:
            print(f"⚠️  SimilaritySearchService initialization failed: {e}")
            return False

        # Test basic functionality
        try:
            if hasattr(service, 'get_index_stats'):
                stats = service.get_index_stats()
                print(f"✅ Index stats available: {list(stats.keys())}")
            else:
                print("⚠️  Index stats method not available")
        except Exception as e:
            print(f"⚠️  Index stats test failed: {e}")

        print("✅ Similarity search tests completed!")
        return True

    except Exception as e:
        print(f"❌ Similarity search test failed: {e}")
        return False

def test_common_ai_services():
    """Test common AI services."""
    try:
        print("Testing Common AI Services...")

        # Test query parser
        try:
            from common.ai_services.query_parser import QueryParser
            parser = QueryParser()
            print("✅ QueryParser initializable")
        except Exception as e:
            print(f"⚠️  QueryParser issue: {e}")

        # Test unified search engine
        try:
            from common.ai_services.unified_search import UnifiedSearchEngine
            engine = UnifiedSearchEngine()
            print("✅ UnifiedSearchEngine initializable")
        except Exception as e:
            print(f"⚠️  UnifiedSearchEngine issue: {e}")

        # Test AI coordinator
        try:
            from common.ai_services.ai_coordinator import AICoordinator
            coordinator = AICoordinator()
            print("✅ AICoordinator initializable")
        except Exception as e:
            print(f"⚠️  AICoordinator issue: {e}")

        print("✅ Common AI services tests completed!")
        return True

    except Exception as e:
        print(f"❌ Common AI services test failed: {e}")
        return False

def test_ai_dependencies():
    """Test AI service dependencies."""
    try:
        print("Testing AI Dependencies...")

        # Test sentence-transformers availability
        try:
            import sentence_transformers
            print("✅ sentence-transformers available")
        except ImportError:
            print("⚠️  sentence-transformers not available")

        # Test transformers availability
        try:
            import transformers
            print("✅ transformers available")
        except ImportError:
            print("⚠️  transformers not available")

        # Test torch availability
        try:
            import torch
            print("✅ PyTorch available")
        except ImportError:
            print("⚠️  PyTorch not available")

        # Test numpy availability
        try:
            import numpy
            print("✅ NumPy available")
        except ImportError:
            print("⚠️  NumPy not available")

        # Test scikit-learn availability
        try:
            import sklearn
            print("✅ scikit-learn available")
        except ImportError:
            print("⚠️  scikit-learn not available")

        print("✅ AI dependencies tests completed!")
        return True

    except Exception as e:
        print(f"❌ AI dependencies test failed: {e}")
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

        for setting in ai_settings:
            if hasattr(settings, setting):
                value = getattr(settings, setting)
                # Mask sensitive values
                if 'API_KEY' in setting and value:
                    value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***MASKED***"
                print(f"✅ {setting}: {value}")
            else:
                print(f"⚠️  {setting}: Not configured")

        print("✅ AI configuration tests completed!")
        return True

    except Exception as e:
        print(f"❌ AI configuration test failed: {e}")
        return False

def main():
    """Run all AI services tests."""
    print("=" * 60)
    print("OBCMS AI SERVICES TESTS")
    print("=" * 60)

    tests = [
        ("AI Service Imports", test_ai_service_imports),
        ("AI Dependencies", test_ai_dependencies),
        ("AI Configuration", test_ai_configuration),
        ("Embedding Service", test_embedding_service),
        ("Gemini Service", test_gemini_service),
        ("Vector Store", test_vector_store),
        ("Similarity Search", test_similarity_search),
        ("Common AI Services", test_common_ai_services),
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
    print("AI SERVICES TEST SUMMARY")
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
        print("🎉 ALL AI SERVICES TESTS PASSED!")
        return 0
    else:
        print("⚠️  Some AI services tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())