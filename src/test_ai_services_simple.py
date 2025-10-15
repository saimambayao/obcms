#!/usr/bin/env python3
"""
Simple AI Services Test Script

Tests AI service components with minimal Django setup to avoid model import issues.
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Test Results Storage
test_results = {
    'embedding_service': {'status': 'PENDING', 'details': [], 'errors': []},
    'gemini_service': {'status': 'PENDING', 'details': [], 'errors': []},
    'vector_store': {'status': 'PENDING', 'details': [], 'errors': []},
    'template_matcher': {'status': 'PENDING', 'details': [], 'errors': []},
}

def test_embedding_service_standalone():
    """Test embedding service without Django."""
    logger.info("Testing EmbeddingService (standalone)...")
    result = test_results['embedding_service']

    try:
        # Test direct import without Django
        import sys
        sys.path.insert(0, str(Path(__file__).parent / 'ai_assistant' / 'services'))

        from embedding_service import EmbeddingService
        result['details'].append("✓ Import successful")

        # Test instantiation
        try:
            service = EmbeddingService()
            result['details'].append("✓ Service instantiation successful")

            # Test basic functionality
            test_text = "Bangsamoro community in Zamboanga"
            embedding = service.generate_embedding(test_text)

            if embedding is not None and hasattr(embedding, 'shape'):
                result['details'].append(f"✓ Embedding generation: shape {embedding.shape}")
                result['details'].append(f"  - Dimension: {service.get_dimension()}")
            else:
                result['errors'].append("✗ Invalid embedding result")

            # Test similarity
            text1 = "Muslim community"
            text2 = "Islamic community"
            emb1 = service.generate_embedding(text1)
            emb2 = service.generate_embedding(text2)
            similarity = service.compute_similarity(emb1, emb2)
            result['details'].append(f"✓ Similarity computation: {similarity:.3f}")

            result['status'] = 'PASS'

        except ImportError as e:
            if "sentence-transformers" in str(e):
                result['details'].append("⚠ sentence-transformers not installed")
                result['status'] = 'SKIP'
            else:
                result['errors'].append(f"✗ Import error: {e}")
                result['status'] = 'FAIL'
        except Exception as e:
            result['errors'].append(f"✗ Service error: {e}")
            result['status'] = 'FAIL'

    except ImportError as e:
        result['errors'].append(f"✗ Failed to import: {e}")
        result['status'] = 'FAIL'

def test_vector_store_standalone():
    """Test vector store without Django."""
    logger.info("Testing VectorStore (standalone)...")
    result = test_results['vector_store']

    try:
        # Test direct import
        import sys
        sys.path.insert(0, str(Path(__file__).parent / 'ai_assistant' / 'services'))

        from vector_store import VectorStore
        result['details'].append("✓ Import successful")

        try:
            # Mock settings for testing
            import types
            mock_settings = types.SimpleNamespace()
            mock_settings.BASE_DIR = Path(__file__).parent

            # Temporarily replace settings
            import ai_assistant.services.vector_store as vs_module
            original_settings = getattr(vs_module, 'settings', None)
            vs_module.settings = mock_settings

            # Create test store
            store = VectorStore('test_store', dimension=384)
            result['details'].append("✓ Store instantiation successful")

            # Test basic functionality
            import numpy as np

            test_embedding = np.random.rand(384).astype('float32')
            metadata = {'id': 1, 'type': 'test'}

            position = store.add_vector(test_embedding, metadata)
            result['details'].append(f"✓ Vector added at position {position}")

            # Test search
            query_vector = np.random.rand(384).astype('float32')
            search_results = store.search(query_vector, k=3)
            result['details'].append(f"✓ Search: {len(search_results)} results")

            # Restore original settings
            vs_module.settings = original_settings

            result['status'] = 'PASS'

        except ImportError as e:
            if "faiss" in str(e):
                result['details'].append("⚠ FAISS not installed")
                result['status'] = 'SKIP'
            else:
                result['errors'].append(f"✗ Import error: {e}")
                result['status'] = 'FAIL'
        except Exception as e:
            result['errors'].append(f"✗ Service error: {e}")
            result['status'] = 'FAIL'

    except ImportError as e:
        result['errors'].append(f"✗ Failed to import: {e}")
        result['status'] = 'FAIL'

def test_gemini_service_standalone():
    """Test Gemini service with minimal setup."""
    logger.info("Testing GeminiService (standalone)...")
    result = test_results['gemini_service']

    try:
        # Test direct import
        import sys
        sys.path.insert(0, str(Path(__file__).parent / 'ai_assistant' / 'services'))

        from gemini_service import GeminiService
        result['details'].append("✓ Import successful")

        # Mock settings for testing
        import types
        mock_settings = types.SimpleNamespace()
        mock_settings.GOOGLE_API_KEY = None  # No API key for testing

        try:
            # Temporarily replace settings
            import ai_assistant.services.gemini_service as gs_module
            original_settings = getattr(gs_module, 'settings', None)
            gs_module.settings = mock_settings

            # This should fail gracefully due to missing API key
            try:
                service = GeminiService()
                result['errors'].append("✗ Should have failed without API key")
            except ValueError as e:
                if "GOOGLE_API_KEY" in str(e):
                    result['details'].append("✓ Correctly rejected missing API key")
                else:
                    result['errors'].append(f"✗ Unexpected error: {e}")

            # Restore original settings
            gs_module.settings = original_settings

            result['status'] = 'PASS'

        except ImportError as e:
            if "google.generativeai" in str(e):
                result['details'].append("⚠ Google Generative AI not installed")
                result['status'] = 'SKIP'
            else:
                result['errors'].append(f"✗ Import error: {e}")
                result['status'] = 'FAIL'

    except ImportError as e:
        result['errors'].append(f"✗ Failed to import: {e}")
        result['status'] = 'FAIL'

def test_template_matcher_standalone():
    """Test template matcher without Django."""
    logger.info("Testing TemplateMatcher (standalone)...")
    result = test_results['template_matcher']

    try:
        # Test direct import
        import sys
        sys.path.insert(0, str(Path(__file__).parent / 'common' / 'ai_services' / 'chat'))

        from template_matcher import TemplateMatcher
        result['details'].append("✓ Import successful")

        try:
            matcher = TemplateMatcher()
            result['details'].append("✓ Matcher instantiation successful")

            # Test entity substitution
            template_str = "Test {location_filter} with {rating}"
            entities = {
                'location': {'type': 'province', 'value': 'Zamboanga del Norte'},
                'rating': 'none'
            }
            substituted = matcher.substitute_entities(template_str, entities)
            result['details'].append(f"✓ Entity substitution: {substituted}")

            # Test rating normalization
            normalized = matcher._normalize_rating_value('no')
            result['details'].append(f"✓ Rating normalization: 'no' -> '{normalized}'")

            result['status'] = 'PASS'

        except Exception as e:
            result['errors'].append(f"✗ Service error: {e}")
            result['status'] = 'FAIL'

    except ImportError as e:
        result['errors'].append(f"✗ Failed to import: {e}")
        result['status'] = 'FAIL'

def print_summary():
    """Print test summary."""
    print("\n" + "="*60)
    print("AI SERVICES TEST SUMMARY (STANDALONE)")
    print("="*60)

    status_counts = {'PASS': 0, 'FAIL': 0, 'SKIP': 0, 'PENDING': 0}

    for service, result in test_results.items():
        status = result['status']
        status_counts[status] += 1

        status_symbol = {
            'PASS': '✅',
            'FAIL': '❌',
            'SKIP': '⚠️',
            'PENDING': '⏳'
        }[status]

        print(f"\n{status_symbol} {service.upper()}: {status}")

        if result['details']:
            for detail in result['details']:
                print(f"   {detail}")

        if result['errors']:
            for error in result['errors']:
                print(f"   ERROR: {error}")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"✅ Passed: {status_counts['PASS']}")
    print(f"❌ Failed: {status_counts['FAIL']}")
    print(f"⚠️  Skipped: {status_counts['SKIP']}")
    print(f"⏳  Pending: {status_counts['PENDING']}")

    print("\nRECOMMENDATIONS:")
    if test_results['embedding_service']['status'] == 'SKIP':
        print("• Install sentence-transformers: pip install sentence-transformers")
    if test_results['gemini_service']['status'] == 'SKIP':
        print("• Install google-generativeai: pip install google-generativeai")
    if test_results['vector_store']['status'] == 'SKIP':
        print("• Install FAISS: pip install faiss-cpu")

def main():
    """Run standalone AI service tests."""
    print("Starting standalone AI services test...")
    print("="*60)

    test_functions = [
        test_embedding_service_standalone,
        test_vector_store_standalone,
        test_gemini_service_standalone,
        test_template_matcher_standalone,
    ]

    for test_func in test_functions:
        try:
            test_func()
        except Exception as e:
            logger.error(f"Test function {test_func.__name__} crashed: {e}")
            service_name = test_func.__name__.replace('test_', '').replace('_standalone', '')
            if service_name in test_results:
                test_results[service_name]['status'] = 'FAIL'
                test_results[service_name]['errors'].append(f"Test crashed: {e}")

    print_summary()

    # Return appropriate exit code
    failed_count = sum(1 for r in test_results.values() if r['status'] == 'FAIL')
    return 1 if failed_count > 0 else 0

if __name__ == "__main__":
    sys.exit(main())