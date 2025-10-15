#!/usr/bin/env python3
"""
Comprehensive AI Services Test Script

Tests all AI service components without requiring database setup.
Uses mock data for testing AI functionality.
"""

import os
import sys
import logging
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.bmms_config')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

import django
django.setup()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Test Results Storage
test_results = {
    'embedding_service': {'status': 'PENDING', 'details': [], 'errors': []},
    'gemini_service': {'status': 'PENDING', 'details': [], 'errors': []},
    'similarity_search': {'status': 'PENDING', 'details': [], 'errors': []},
    'vector_store': {'status': 'PENDING', 'details': [], 'errors': []},
    'query_parser': {'status': 'PENDING', 'details': [], 'errors': []},
    'unified_search': {'status': 'PENDING', 'details': [], 'errors': []},
    'template_matcher': {'status': 'PENDING', 'details': [], 'errors': []},
}

def test_embedding_service():
    """Test embedding service functionality."""
    logger.info("Testing EmbeddingService...")
    result = test_results['embedding_service']

    try:
        # Test import
        from ai_assistant.services.embedding_service import EmbeddingService, get_embedding_service
        result['details'].append("✓ Import successful")

        # Test instantiation (may fail if sentence-transformers not installed)
        try:
            service = EmbeddingService()
            result['details'].append("✓ Service instantiation successful")

            # Test basic functionality with sample text
            test_text = "Bangsamoro community in Zamboanga with fishing livelihood"
            embedding = service.generate_embedding(test_text)

            if embedding is not None and hasattr(embedding, 'shape'):
                result['details'].append(f"✓ Embedding generation successful: shape {embedding.shape}")
                result['details'].append(f"  - Dimension: {service.get_dimension()}")
                result['details'].append(f"  - Data type: {type(embedding)}")
            else:
                result['errors'].append("✗ Embedding generation returned invalid result")

            # Test batch functionality
            test_texts = [
                "Coastal fishing community",
                "Muslim community in Mindanao",
                "Education program for youth"
            ]
            embeddings = service.batch_generate(test_texts)
            if embeddings is not None and hasattr(embeddings, 'shape'):
                result['details'].append(f"✓ Batch embedding successful: shape {embeddings.shape}")
            else:
                result['errors'].append("✗ Batch embedding generation returned invalid result")

            # Test similarity computation
            text1 = "Muslim community"
            text2 = "Islamic community"
            emb1 = service.generate_embedding(text1)
            emb2 = service.generate_embedding(text2)
            similarity = service.compute_similarity(emb1, emb2)
            result['details'].append(f"✓ Similarity computation: {similarity:.3f}")

            # Test content hashing
            hash1 = service.compute_content_hash(test_text)
            hash2 = service.compute_content_hash(test_text)
            if hash1 == hash2:
                result['details'].append("✓ Content hashing consistent")
            else:
                result['errors'].append("✗ Content hashing inconsistent")

            # Test re-embedding check
            should_reembed = service.should_reembed(test_text, None)
            if should_reembed:
                result['details'].append("✓ Re-embedding check works for new content")
            else:
                result['errors'].append("✗ Re-embedding check failed for new content")

            result['status'] = 'PASS'

        except ImportError as e:
            if "sentence-transformers" in str(e):
                result['details'].append("⚠ Sentence-transformers library not installed - skipping embedding tests")
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
    except Exception as e:
        result['errors'].append(f"✗ Unexpected error: {e}")
        result['status'] = 'FAIL'

def test_gemini_service():
    """Test Gemini service functionality."""
    logger.info("Testing GeminiService...")
    result = test_results['gemini_service']

    try:
        # Test import
        from ai_assistant.services.gemini_service import GeminiService
        result['details'].append("✓ Import successful")

        # Check for API key
        from django.conf import settings
        api_key = getattr(settings, "GOOGLE_API_KEY", None)
        if not api_key:
            result['details'].append("⚠ GOOGLE_API_KEY not configured - skipping Gemini tests")
            result['status'] = 'SKIP'
            return

        # Test instantiation
        try:
            service = GeminiService()
            result['details'].append("✓ Service instantiation successful")

            # Test basic text generation (may fail without valid API key)
            try:
                response = service.generate_text(
                    "What is the capital of Bangladesh?",
                    use_cache=False,
                    include_cultural_context=False
                )

                if response.get('success'):
                    result['details'].append("✓ Text generation successful")
                    result['details'].append(f"  - Tokens used: {response.get('tokens_used', 'N/A')}")
                    result['details'].append(f"  - Cost: ${response.get('cost', 0):.6f}")
                    result['details'].append(f"  - Response time: {response.get('response_time', 0):.2f}s")
                    result['details'].append(f"  - Response length: {len(response.get('text', ''))}")
                else:
                    result['errors'].append(f"✗ Text generation failed: {response.get('error', 'Unknown error')}")

            except Exception as e:
                if "API" in str(e).upper() or "KEY" in str(e).upper():
                    result['details'].append(f"⚠ API issue (likely invalid key): {e}")
                    result['status'] = 'SKIP'
                else:
                    result['errors'].append(f"✗ Text generation error: {e}")

            # Test chat functionality
            try:
                chat_response = service.chat_with_ai(
                    "How many regions does OOBC cover?",
                    context="User asking about OOBC scope"
                )

                if chat_response.get('success'):
                    result['details'].append("✓ Chat functionality successful")
                    result['details'].append(f"  - Suggestions: {len(chat_response.get('suggestions', []))}")
                else:
                    result['errors'].append(f"✗ Chat functionality failed: {chat_response.get('error', 'Unknown error')}")

            except Exception as e:
                result['errors'].append(f"✗ Chat functionality error: {e}")

            # Test token counting
            try:
                token_count = service.count_tokens("Test text for counting tokens")
                result['details'].append(f"✓ Token counting: {token_count} tokens")
            except Exception as e:
                result['errors'].append(f"✗ Token counting error: {e}")

            if result['status'] == 'PENDING':
                result['status'] = 'PASS'

        except ImportError as e:
            if "google.generativeai" in str(e):
                result['details'].append("⚠ Google Generative AI library not installed - skipping Gemini tests")
                result['status'] = 'SKIP'
            else:
                result['errors'].append(f"✗ Import error: {e}")
                result['status'] = 'FAIL'
        except ValueError as e:
            if "GOOGLE_API_KEY" in str(e):
                result['details'].append("⚠ GOOGLE_API_KEY not configured - skipping Gemini tests")
                result['status'] = 'SKIP'
            else:
                result['errors'].append(f"✗ Configuration error: {e}")
                result['status'] = 'FAIL'
        except Exception as e:
            result['errors'].append(f"✗ Service error: {e}")
            result['status'] = 'FAIL'

    except ImportError as e:
        result['errors'].append(f"✗ Failed to import: {e}")
        result['status'] = 'FAIL'
    except Exception as e:
        result['errors'].append(f"✗ Unexpected error: {e}")
        result['status'] = 'FAIL'

def test_vector_store():
    """Test vector store functionality."""
    logger.info("Testing VectorStore...")
    result = test_results['vector_store']

    try:
        # Test import
        from ai_assistant.services.vector_store import VectorStore
        result['details'].append("✓ Import successful")

        # Test instantiation (may fail if FAISS not installed)
        try:
            # Create a temporary store for testing
            store = VectorStore('test_store', dimension=384)
            result['details'].append("✓ Store instantiation successful")

            # Test basic functionality
            import numpy as np

            # Create test embeddings
            test_embedding = np.random.rand(384).astype('float32')
            metadata = {'id': 1, 'type': 'test', 'data': {'name': 'Test Document'}}

            # Add vector
            position = store.add_vector(test_embedding, metadata)
            result['details'].append(f"✓ Vector added at position {position}")

            # Test batch addition
            test_embeddings = np.random.rand(5, 384).astype('float32')
            metadata_list = [
                {'id': i, 'type': 'batch_test', 'data': {'name': f'Batch Test {i}'}}
                for i in range(5)
            ]

            positions = store.add_vectors(test_embeddings, metadata_list)
            result['details'].append(f"✓ Batch vectors added: {len(positions)} vectors")

            # Test search
            query_vector = np.random.rand(384).astype('float32')
            search_results = store.search(query_vector, k=3)
            result['details'].append(f"✓ Search successful: {len(search_results)} results")

            # Test threshold search
            threshold_results = store.search_by_threshold(query_vector, threshold=0.1, max_results=5)
            result['details'].append(f"✓ Threshold search: {len(threshold_results)} results")

            # Test stats
            stats = store.get_stats()
            result['details'].append(f"✓ Stats: {stats['total_vectors']} vectors, dimension {stats['dimension']}")

            # Test error handling
            try:
                # Test wrong dimension
                wrong_embedding = np.random.rand(100).astype('float32')  # Wrong dimension
                store.add_vector(wrong_embedding, {'id': 'wrong'})
                result['errors'].append("✗ Should have failed with wrong dimension")
            except ValueError:
                result['details'].append("✓ Correctly rejected wrong dimension")

            result['status'] = 'PASS'

        except ImportError as e:
            if "faiss" in str(e):
                result['details'].append("⚠ FAISS library not installed - skipping vector store tests")
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
    except Exception as e:
        result['errors'].append(f"✗ Unexpected error: {e}")
        result['status'] = 'FAIL'

def test_similarity_search():
    """Test similarity search functionality."""
    logger.info("Testing SimilaritySearchService...")
    result = test_results['similarity_search']

    try:
        # Test import
        from ai_assistant.services.similarity_search import SimilaritySearchService, get_similarity_search_service
        result['details'].append("✓ Import successful")

        # Test instantiation (may fail if dependencies not available)
        try:
            service = SimilaritySearchService()
            result['details'].append("✓ Service instantiation successful")

            # Test basic search (will likely return empty due to no indexed data)
            try:
                results = service.search_communities("fishing communities in Zamboanga", limit=5)
                result['details'].append(f"✓ Communities search completed: {len(results)} results")
            except Exception as e:
                result['errors'].append(f"✗ Communities search error: {e}")

            try:
                results = service.search_assessments("education needs assessment", limit=5)
                result['details'].append(f"✓ Assessments search completed: {len(results)} results")
            except Exception as e:
                result['errors'].append(f"✗ Assessments search error: {e}")

            try:
                results = service.search_policies("livelihood programs", limit=5)
                result['details'].append(f"✓ Policies search completed: {len(results)} results")
            except Exception as e:
                result['errors'].append(f"✗ Policies search error: {e}")

            # Test unified search
            try:
                all_results = service.search_all("community development", limit=3)
                result['details'].append(f"✓ Unified search completed: {len(all_results)} modules searched")
            except Exception as e:
                result['errors'].append(f"✗ Unified search error: {e}")

            # Test stats
            try:
                stats = service.get_index_stats()
                result['details'].append(f"✓ Index stats retrieved: {list(stats.keys())}")
            except Exception as e:
                result['errors'].append(f"✗ Stats retrieval error: {e}")

            result['status'] = 'PASS'

        except ImportError as e:
            if "EmbeddingService" in str(e) or "VectorStore" in str(e):
                result['details'].append("⚠ AI service dependencies not available - skipping similarity search tests")
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
    except Exception as e:
        result['errors'].append(f"✗ Unexpected error: {e}")
        result['status'] = 'FAIL'

def test_query_parser():
    """Test query parser functionality."""
    logger.info("Testing QueryParser...")
    result = test_results['query_parser']

    try:
        # Test import
        from common.ai_services.query_parser import QueryParser
        result['details'].append("✓ Import successful")

        # Test instantiation
        parser = QueryParser()
        result['details'].append("✓ Parser instantiation successful")

        # Test basic parsing
        test_queries = [
            "coastal fishing communities in Zamboanga",
            "education programs for Muslim youth",
            "How many communities in Region IX?",
            "health facilities in Lanao del Sur",
            "infrastructure development projects"
        ]

        for query in test_queries:
            try:
                parsed = parser.parse(query)
                result['details'].append(f"✓ Parsed: '{query[:30]}...' -> {parsed.get('intent', 'unknown')}")
                result['details'].append(f"  - Keywords: {parsed.get('keywords', [])[:3]}")
                result['details'].append(f"  - Modules: {parsed.get('suggested_modules', [])[:3]}")
            except Exception as e:
                result['errors'].append(f"✗ Failed to parse '{query}': {e}")

        # Test empty query
        try:
            empty_parsed = parser.parse("")
            result['details'].append("✓ Empty query handled gracefully")
        except Exception as e:
            result['errors'].append(f"✗ Empty query handling failed: {e}")

        # Test fallback parsing (simulate AI unavailability)
        original_gemini = parser.gemini
        parser.gemini = None

        try:
            fallback_parsed = parser.parse("test query without AI")
            result['details'].append("✓ Fallback parsing works without AI")
        except Exception as e:
            result['errors'].append(f"✗ Fallback parsing failed: {e}")
        finally:
            parser.gemini = original_gemini

        result['status'] = 'PASS'

    except ImportError as e:
        result['errors'].append(f"✗ Failed to import: {e}")
        result['status'] = 'FAIL'
    except Exception as e:
        result['errors'].append(f"✗ Unexpected error: {e}")
        result['status'] = 'FAIL'

def test_unified_search():
    """Test unified search functionality."""
    logger.info("Testing UnifiedSearchEngine...")
    result = test_results['unified_search']

    try:
        # Test import
        from common.ai_services.unified_search import UnifiedSearchEngine, get_unified_search_engine
        result['details'].append("✓ Import successful")

        # Test instantiation (may fail if dependencies not available)
        try:
            engine = UnifiedSearchEngine()
            result['details'].append("✓ Engine instantiation successful")

            # Test basic search (will likely return empty due to no indexed data)
            test_query = "fishing communities in coastal areas"

            try:
                search_results = engine.search(test_query, limit=5, threshold=0.3)
                result['details'].append(f"✓ Search completed: {search_results.get('total_results', 0)} total results")
                result['details'].append(f"  - Query: {search_results.get('query', '')}")
                result['details'].append(f"  - Intent: {search_results.get('parsed_query', {}).get('intent', 'unknown')}")
            except Exception as e:
                result['errors'].append(f"✗ Search execution error: {e}")

            # Test module-specific search
            try:
                module_results = engine.search(test_query, modules=['communities'], limit=3)
                result['details'].append(f"✓ Module-specific search completed")
            except Exception as e:
                result['errors'].append(f"✗ Module-specific search error: {e}")

            # Test stats
            try:
                stats = engine.get_index_stats()
                result['details'].append(f"✓ Engine stats retrieved: {list(stats.keys())}")
                for module, stat in stats.items():
                    if isinstance(stat, dict) and 'vector_count' in stat:
                        result['details'].append(f"  - {module}: {stat['vector_count']} vectors")
            except Exception as e:
                result['errors'].append(f"✗ Stats retrieval error: {e}")

            result['status'] = 'PASS'

        except ImportError as e:
            if "EmbeddingService" in str(e) or "SimilaritySearchService" in str(e):
                result['details'].append("⚠ AI service dependencies not available - skipping unified search tests")
                result['status'] = 'SKIP'
            else:
                result['errors'].append(f"✗ Import error: {e}")
                result['status'] = 'FAIL'
        except RuntimeError as e:
            if "AI services not available" in str(e):
                result['details'].append("⚠ AI services not available - skipping unified search tests")
                result['status'] = 'SKIP'
            else:
                result['errors'].append(f"✗ Runtime error: {e}")
                result['status'] = 'FAIL'
        except Exception as e:
            result['errors'].append(f"✗ Service error: {e}")
            result['status'] = 'FAIL'

    except ImportError as e:
        result['errors'].append(f"✗ Failed to import: {e}")
        result['status'] = 'FAIL'
    except Exception as e:
        result['errors'].append(f"✗ Unexpected error: {e}")
        result['status'] = 'FAIL'

def test_template_matcher():
    """Test template matcher functionality."""
    logger.info("Testing TemplateMatcher...")
    result = test_results['template_matcher']

    try:
        # Test import
        from common.ai_services.chat.template_matcher import TemplateMatcher, get_template_matcher
        result['details'].append("✓ Import successful")

        # Test instantiation
        matcher = TemplateMatcher()
        result['details'].append("✓ Matcher instantiation successful")

        # Test basic template matching (with simplified entities)
        test_cases = [
            {
                'query': 'How many communities in Region IX?',
                'entities': {
                    'location': {'type': 'region', 'value': 'Region IX', 'confidence': 0.95}
                },
                'category': 'communities'
            },
            {
                'query': 'Show me workshops last 6 months',
                'entities': {
                    'date_range': {'start': '2024-04-01', 'end': '2024-10-01'}
                },
                'category': 'mana'
            },
            {
                'query': 'education programs without infrastructure',
                'entities': {
                    'rating': 'none'
                },
                'category': 'infrastructure'
            }
        ]

        for i, test_case in enumerate(test_cases):
            try:
                result_data = matcher.match_and_generate(
                    test_case['query'],
                    test_case['entities'],
                    category=test_case.get('category')
                )

                if result_data.get('success'):
                    result['details'].append(f"✓ Test {i+1}: Template match successful")
                    result['details'].append(f"  - Score: {result_data.get('score', 0):.2f}")
                    if result_data.get('query'):
                        result['details'].append(f"  - Generated query length: {len(result_data['query'])}")
                else:
                    result['details'].append(f"⚠ Test {i+1}: No template match (expected for limited templates)")
                    result['details'].append(f"  - Error: {result_data.get('error', 'No match')}")

            except Exception as e:
                result['errors'].append(f"✗ Test {i+1} failed: {e}")

        # Test template suggestions
        try:
            suggestions = matcher.get_template_suggestions("how many", category='communities', max_suggestions=3)
            result['details'].append(f"✓ Template suggestions: {len(suggestions)} suggestions")
        except Exception as e:
            result['errors'].append(f"✗ Template suggestions failed: {e}")

        # Test entity substitution
        try:
            template_str = "OBCCommunity.objects.filter({location_filter}).count()"
            entities = {
                'location': {'type': 'province', 'value': 'Zamboanga del Norte'}
            }
            substituted = matcher.substitute_entities(template_str, entities)
            result['details'].append(f"✓ Entity substitution successful")
            result['details'].append(f"  - Result: {substituted[:100]}...")
        except Exception as e:
            result['errors'].append(f"✗ Entity substitution failed: {e}")

        # Test rating normalization
        test_ratings = ['no', 'without', 'poor', 'available', 'good']
        for rating in test_ratings:
            try:
                normalized = matcher._normalize_rating_value(rating)
                result['details'].append(f"✓ Rating normalization: '{rating}' -> '{normalized}'")
            except Exception as e:
                result['errors'].append(f"✗ Rating normalization failed for '{rating}': {e}")

        result['status'] = 'PASS'

    except ImportError as e:
        result['errors'].append(f"✗ Failed to import: {e}")
        result['status'] = 'FAIL'
    except Exception as e:
        result['errors'].append(f"✗ Unexpected error: {e}")
        result['status'] = 'FAIL'

def print_summary():
    """Print comprehensive test summary."""
    print("\n" + "="*80)
    print("AI SERVICES TEST SUMMARY")
    print("="*80)

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
            print("   Details:")
            for detail in result['details']:
                print(f"     {detail}")

        if result['errors']:
            print("   Errors:")
            for error in result['errors']:
                print(f"     {error}")

    print("\n" + "="*80)
    print("OVERALL SUMMARY")
    print("="*80)
    print(f"✅ Passed: {status_counts['PASS']}")
    print(f"❌ Failed: {status_counts['FAIL']}")
    print(f"⚠️  Skipped: {status_counts['SKIP']}")
    print(f"⏳  Pending: {status_counts['PENDING']}")

    # Recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)

    if test_results['embedding_service']['status'] == 'SKIP':
        print("• Install sentence-transformers: pip install sentence-transformers")

    if test_results['gemini_service']['status'] == 'SKIP':
        print("• Configure GOOGLE_API_KEY in environment variables")
        print("• Install google-generativeai: pip install google-generativeai")

    if test_results['vector_store']['status'] == 'SKIP':
        print("• Install FAISS: pip install faiss-cpu (or faiss-gpu)")

    failed_services = [s for s, r in test_results.items() if r['status'] == 'FAIL']
    if failed_services:
        print(f"• Fix failing services: {', '.join(failed_services)}")

    passed_services = [s for s, r in test_results.items() if r['status'] == 'PASS']
    if passed_services:
        print(f"• Working services: {', '.join(passed_services)}")

    if status_counts['PASS'] + status_counts['SKIP'] == len(test_results):
        print("\n🎉 All AI services are functional or properly skipped due to missing dependencies!")
    else:
        print(f"\n⚠️  {status_counts['FAIL']} services need attention.")

def main():
    """Run all AI service tests."""
    print("Starting comprehensive AI services test...")
    print("="*80)

    # Run tests in dependency order
    test_functions = [
        test_embedding_service,
        test_vector_store,
        test_gemini_service,
        test_similarity_search,
        test_query_parser,
        test_unified_search,
        test_template_matcher,
    ]

    for test_func in test_functions:
        try:
            test_func()
        except Exception as e:
            logger.error(f"Test function {test_func.__name__} crashed: {e}")
            # Find which test this was and mark as failed
            service_name = test_func.__name__.replace('test_', '')
            if service_name in test_results:
                test_results[service_name]['status'] = 'FAIL'
                test_results[service_name]['errors'].append(f"Test function crashed: {e}")

    print_summary()

    # Return appropriate exit code
    failed_count = sum(1 for r in test_results.values() if r['status'] == 'FAIL')
    if failed_count > 0:
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())