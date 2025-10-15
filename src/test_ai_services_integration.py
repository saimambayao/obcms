#!/usr/bin/env python
"""
Comprehensive AI Services Integration Test Script

Tests all AI-powered features in OBCMS/BMMS system:
- AI Assistant Services (EmbeddingService, GeminiService, SimilaritySearch, VectorStore)
- Common AI Services (UnifiedSearch, TemplateMatcher, QueryParser)
- AI-powered features and document search
- Performance metrics and integration testing

Usage:
    python test_ai_services_integration.py [--verbose] [--save-report]
"""

import os
import sys
import time
import json
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.development')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIServicesIntegrationTester:
    """Comprehensive AI services integration tester."""

    def __init__(self, verbose: bool = False):
        """Initialize the tester."""
        self.verbose = verbose
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'ai_assistant_services': {},
            'common_ai_services': {},
            'ai_features': {},
            'performance_metrics': {},
            'integration_status': {},
            'errors': [],
            'recommendations': []
        }

        print("=" * 80)
        print("OBCMS/BMMS AI SERVICES INTEGRATION TEST")
        print("=" * 80)
        print(f"Started at: {self.test_results['timestamp']}")
        print()

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all AI services tests."""
        try:
            # Test AI Assistant Services
            self.test_ai_assistant_services()

            # Test Common AI Services
            self.test_common_ai_services()

            # Test AI-powered features
            self.test_ai_features()

            # Test performance metrics
            self.test_performance_metrics()

            # Test integration across apps
            self.test_integration_across_apps()

            # Generate recommendations
            self.generate_recommendations()

            return self.test_results

        except Exception as e:
            logger.error(f"Test execution failed: {str(e)}")
            self.test_results['errors'].append({
                'type': 'execution_error',
                'message': str(e),
                'traceback': traceback.format_exc()
            })
            return self.test_results

    def test_ai_assistant_services(self):
        """Test AI Assistant Services."""
        print("🔧 TESTING AI ASSISTANT SERVICES")
        print("-" * 50)

        results = {}

        # Test EmbeddingService
        results['embedding_service'] = self.test_embedding_service()

        # Test VectorStore
        results['vector_store'] = self.test_vector_store()

        # Test SimilaritySearch
        results['similarity_search'] = self.test_similarity_search()

        # Test GeminiService
        results['gemini_service'] = self.test_gemini_service()

        self.test_results['ai_assistant_services'] = results
        print()

    def test_embedding_service(self) -> Dict[str, Any]:
        """Test EmbeddingService functionality."""
        print("Testing EmbeddingService...")

        result = {
            'available': False,
            'model_loaded': False,
            'embedding_generation': False,
            'batch_processing': False,
            'similarity_calculation': False,
            'performance': {},
            'errors': []
        }

        try:
            from ai_assistant.services import EmbeddingService, HAS_EMBEDDING_SERVICE

            result['available'] = HAS_EMBEDDING_SERVICE

            if HAS_EMBEDDING_SERVICE:
                service = EmbeddingService()
                result['model_loaded'] = True

                # Test single embedding generation
                start_time = time.time()
                embedding = service.generate_embedding("Bangsamoro community in Zamboanga")
                end_time = time.time()

                if embedding is not None and len(embedding) > 0:
                    result['embedding_generation'] = True
                    result['performance']['single_embedding_time'] = end_time - start_time
                    result['performance']['embedding_dimension'] = len(embedding)

                    if self.verbose:
                        print(f"  ✓ Generated embedding: {len(embedding)} dimensions in {end_time - start_time:.3f}s")

                # Test batch processing
                texts = [
                    "Muslim community in Lanao del Sur",
                    "Fishing village in Sulu",
                    "Maranao settlers in Cotabato",
                    "Tausug community in Zamboanga",
                    "Agricultural community in Sultan Kudarat"
                ]

                start_time = time.time()
                embeddings = service.batch_generate(texts)
                end_time = time.time()

                if embeddings is not None and len(embeddings) == len(texts):
                    result['batch_processing'] = True
                    result['performance']['batch_embedding_time'] = end_time - start_time
                    result['performance']['batch_throughput'] = len(texts) / (end_time - start_time)

                    if self.verbose:
                        print(f"  ✓ Batch processed {len(texts)} texts in {end_time - start_time:.3f}s")

                # Test similarity calculation
                if len(embeddings) >= 2:
                    similarity = service.compute_similarity(embeddings[0], embeddings[1])
                    if isinstance(similarity, (int, float)):
                        result['similarity_calculation'] = True
                        result['performance']['sample_similarity'] = float(similarity)

                        if self.verbose:
                            print(f"  ✓ Computed similarity: {similarity:.3f}")
            else:
                result['errors'].append("EmbeddingService not available - missing sentence-transformers")
                print("  ❌ EmbeddingService not available")

        except Exception as e:
            error_msg = f"EmbeddingService test failed: {str(e)}"
            result['errors'].append(error_msg)
            print(f"  ❌ {error_msg}")

            if self.verbose:
                print(f"    Traceback: {traceback.format_exc()}")

        return result

    def test_vector_store(self) -> Dict[str, Any]:
        """Test VectorStore functionality."""
        print("Testing VectorStore...")

        result = {
            'available': False,
            'create_store': False,
            'add_vectors': False,
            'search_functionality': False,
            'persistence': False,
            'performance': {},
            'errors': []
        }

        try:
            from ai_assistant.services import VectorStore, HAS_VECTOR_STORE

            result['available'] = HAS_VECTOR_STORE

            if HAS_VECTOR_STORE:
                import numpy as np

                # Create test store
                start_time = time.time()
                store = VectorStore('test_store', dimension=384)
                end_time = time.time()

                result['create_store'] = True
                result['performance']['create_time'] = end_time - start_time

                if self.verbose:
                    print(f"  ✓ Created vector store in {end_time - start_time:.3f}s")

                # Add test vectors
                test_vectors = np.random.rand(10, 384).astype('float32')
                test_metadata = [
                    {'id': i, 'type': 'test', 'data': f'test_item_{i}'}
                    for i in range(10)
                ]

                start_time = time.time()
                positions = store.add_vectors(test_vectors, test_metadata)
                end_time = time.time()

                if len(positions) == 10:
                    result['add_vectors'] = True
                    result['performance']['add_time'] = end_time - start_time
                    result['performance']['vectors_added'] = len(positions)

                    if self.verbose:
                        print(f"  ✓ Added {len(positions)} vectors in {end_time - start_time:.3f}s")

                # Test search
                query_vector = np.random.rand(384).astype('float32')

                start_time = time.time()
                search_results = store.search(query_vector, k=5)
                end_time = time.time()

                if len(search_results) > 0:
                    result['search_functionality'] = True
                    result['performance']['search_time'] = end_time - start_time
                    result['performance']['results_found'] = len(search_results)

                    if self.verbose:
                        print(f"  ✓ Found {len(search_results)} results in {end_time - start_time:.3f}s")

                # Test persistence (optional - might fail without proper permissions)
                try:
                    start_time = time.time()
                    store.save()
                    end_time = time.time()

                    result['persistence'] = True
                    result['performance']['save_time'] = end_time - start_time

                    if self.verbose:
                        print(f"  ✓ Saved store in {end_time - start_time:.3f}s")

                    # Clean up test files
                    import os
                    store_path = store.get_storage_path()
                    if store_path.exists():
                        os.remove(store_path)
                    metadata_path = store_path.with_suffix('.metadata')
                    if metadata_path.exists():
                        os.remove(metadata_path)

                except Exception as save_error:
                    result['persistence'] = False
                    result['errors'].append(f"Save test failed: {str(save_error)}")
                    if self.verbose:
                        print(f"  ⚠ Save test failed: {save_error}")
            else:
                result['errors'].append("VectorStore not available - missing FAISS")
                print("  ❌ VectorStore not available")

        except Exception as e:
            error_msg = f"VectorStore test failed: {str(e)}"
            result['errors'].append(error_msg)
            print(f"  ❌ {error_msg}")

            if self.verbose:
                print(f"    Traceback: {traceback.format_exc()}")

        return result

    def test_similarity_search(self) -> Dict[str, Any]:
        """Test SimilaritySearchService functionality."""
        print("Testing SimilaritySearchService...")

        result = {
            'available': False,
            'service_initialization': False,
            'community_search': False,
            'assessment_search': False,
            'policy_search': False,
            'unified_search': False,
            'performance': {},
            'errors': []
        }

        try:
            from ai_assistant.services import (
                SimilaritySearchService,
                HAS_SIMILARITY_SEARCH,
                HAS_EMBEDDING_SERVICE,
                HAS_VECTOR_STORE
            )

            result['available'] = HAS_SIMILARITY_SEARCH and HAS_EMBEDDING_SERVICE and HAS_VECTOR_STORE

            if result['available']:
                service = SimilaritySearchService()
                result['service_initialization'] = True

                if self.verbose:
                    print("  ✓ SimilaritySearchService initialized")

                # Test searches (will show warnings if indices don't exist)
                test_queries = [
                    ("coastal fishing communities", 'communities'),
                    ("education needs assessment", 'assessments'),
                    ("livelihood programs", 'policies')
                ]

                for query, module in test_queries:
                    try:
                        start_time = time.time()

                        if module == 'communities':
                            results = service.search_communities(query, limit=5)
                        elif module == 'assessments':
                            results = service.search_assessments(query, limit=5)
                        elif module == 'policies':
                            results = service.search_policies(query, limit=5)

                        end_time = time.time()

                        # Store results (even if empty - means search works but no data)
                        result[f'{module}_search'] = True
                        result['performance'][f'{module}_search_time'] = end_time - start_time
                        result['performance'][f'{module}_results'] = len(results)

                        if self.verbose:
                            if results:
                                print(f"  ✓ {module} search: {len(results)} results in {end_time - start_time:.3f}s")
                            else:
                                print(f"  ⚠ {module} search: 0 results (service works, no indexed data)")

                    except Exception as search_error:
                        result['errors'].append(f"{module} search failed: {str(search_error)}")
                        if self.verbose:
                            print(f"  ❌ {module} search failed: {search_error}")

                # Test unified search
                try:
                    start_time = time.time()
                    unified_results = service.search_all("Bangsamoro communities", limit=5)
                    end_time = time.time()

                    result['unified_search'] = True
                    result['performance']['unified_search_time'] = end_time - start_time
                    result['performance']['unified_total_results'] = sum(
                        len(v) for v in unified_results.values()
                    )

                    if self.verbose:
                        total = sum(len(v) for v in unified_results.values())
                        print(f"  ✓ Unified search: {total} total results in {end_time - start_time:.3f}s")

                except Exception as unified_error:
                    result['errors'].append(f"Unified search failed: {str(unified_error)}")
                    if self.verbose:
                        print(f"  ❌ Unified search failed: {unified_error}")
            else:
                missing = []
                if not HAS_SIMILARITY_SEARCH:
                    missing.append("SimilaritySearchService")
                if not HAS_EMBEDDING_SERVICE:
                    missing.append("EmbeddingService")
                if not HAS_VECTOR_STORE:
                    missing.append("VectorStore")

                result['errors'].append(f"Missing dependencies: {', '.join(missing)}")
                print(f"  ❌ SimilaritySearchService not available - missing {', '.join(missing)}")

        except Exception as e:
            error_msg = f"SimilaritySearchService test failed: {str(e)}"
            result['errors'].append(error_msg)
            print(f"  ❌ {error_msg}")

            if self.verbose:
                print(f"    Traceback: {traceback.format_exc()}")

        return result

    def test_gemini_service(self) -> Dict[str, Any]:
        """Test GeminiService functionality."""
        print("Testing GeminiService...")

        result = {
            'available': False,
            'service_initialization': False,
            'text_generation': False,
            'streaming_generation': False,
            'chat_functionality': False,
            'caching': False,
            'performance': {},
            'errors': []
        }

        try:
            from ai_assistant.services import GeminiService

            # Try to initialize service (may fail if API key not configured)
            try:
                service = GeminiService()
                result['available'] = True
                result['service_initialization'] = True

                if self.verbose:
                    print("  ✓ GeminiService initialized")
            except Exception as init_error:
                result['errors'].append(f"Service initialization failed: {str(init_error)}")
                print(f"  ❌ GeminiService initialization failed: {init_error}")
                return result

            # Test basic text generation
            try:
                start_time = time.time()
                response = service.generate_text(
                    "What is the Office for Other Bangsamoro Communities?",
                    use_cache=False,
                    include_cultural_context=False
                )
                end_time = time.time()

                if response.get('success') and response.get('text'):
                    result['text_generation'] = True
                    result['performance']['text_generation_time'] = end_time - start_time
                    result['performance']['tokens_used'] = response.get('tokens_used', 0)
                    result['performance']['cost'] = response.get('cost', 0.0)

                    if self.verbose:
                        print(f"  ✓ Text generation: {response['tokens_used']} tokens in {end_time - start_time:.3f}s")
                        print(f"    Cost: ${response['cost']:.6f}")
                else:
                    result['errors'].append(f"Text generation failed: {response.get('error', 'Unknown error')}")
                    print(f"  ❌ Text generation failed: {response.get('error')}")

            except Exception as gen_error:
                result['errors'].append(f"Text generation test failed: {str(gen_error)}")
                print(f"  ❌ Text generation test failed: {gen_error}")

            # Test streaming
            try:
                start_time = time.time()
                chunks = list(service.generate_stream(
                    "Briefly describe Bangsamoro communities",
                    include_cultural_context=False
                ))
                end_time = time.time()

                if chunks:
                    result['streaming_generation'] = True
                    result['performance']['streaming_time'] = end_time - start_time
                    result['performance']['streaming_chunks'] = len(chunks)

                    if self.verbose:
                        print(f"  ✓ Streaming: {len(chunks)} chunks in {end_time - start_time:.3f}s")
                else:
                    result['errors'].append("Streaming returned no chunks")
                    print("  ❌ Streaming returned no chunks")

            except Exception as stream_error:
                result['errors'].append(f"Streaming test failed: {str(stream_error)}")
                print(f"  ❌ Streaming test failed: {stream_error}")

            # Test chat functionality
            try:
                start_time = time.time()
                chat_response = service.chat_with_ai(
                    "How can OBCMS help Bangsamoro communities?"
                )
                end_time = time.time()

                if chat_response.get('success') and chat_response.get('message'):
                    result['chat_functionality'] = True
                    result['performance']['chat_time'] = end_time - start_time
                    result['performance']['chat_tokens'] = chat_response.get('tokens_used', 0)
                    result['performance']['chat_suggestions'] = len(chat_response.get('suggestions', []))

                    if self.verbose:
                        print(f"  ✓ Chat: {chat_response['tokens_used']} tokens in {end_time - start_time:.3f}s")
                        print(f"    Suggestions: {len(chat_response.get('suggestions', []))}")
                else:
                    result['errors'].append(f"Chat failed: {chat_response.get('error', 'Unknown error')}")
                    print(f"  ❌ Chat failed: {chat_response.get('error')}")

            except Exception as chat_error:
                result['errors'].append(f"Chat test failed: {str(chat_error)}")
                print(f"  ❌ Chat test failed: {chat_error}")

            # Test caching
            try:
                # First call
                start_time = time.time()
                response1 = service.generate_text(
                    "Test query for caching",
                    use_cache=True
                )
                first_time = time.time() - start_time

                # Second call (should be cached)
                start_time = time.time()
                response2 = service.generate_text(
                    "Test query for caching",
                    use_cache=True
                )
                second_time = time.time() - start_time

                if response1.get('success') and response2.get('success'):
                    if response2.get('cached', False):
                        result['caching'] = True
                        result['performance']['cache_speedup'] = first_time / second_time if second_time > 0 else 0

                        if self.verbose:
                            print(f"  ✓ Caching working: {second_time:.3f}s vs {first_time:.3f}s")
                    else:
                        result['errors'].append("Cache not working as expected")
                        if self.verbose:
                            print("  ⚠ Cache not working - second call not cached")
                else:
                    result['errors'].append("Cache test failed - one or both calls failed")

            except Exception as cache_error:
                result['errors'].append(f"Cache test failed: {str(cache_error)}")
                print(f"  ❌ Cache test failed: {cache_error}")

        except Exception as e:
            error_msg = f"GeminiService test failed: {str(e)}"
            result['errors'].append(error_msg)
            print(f"  ❌ {error_msg}")

            if self.verbose:
                print(f"    Traceback: {traceback.format_exc()}")

        return result

    def test_common_ai_services(self):
        """Test Common AI Services."""
        print("🤖 TESTING COMMON AI SERVICES")
        print("-" * 50)

        results = {}

        # Test UnifiedSearchEngine
        results['unified_search_engine'] = self.test_unified_search_engine()

        # Test QueryParser
        results['query_parser'] = self.test_query_parser()

        # Test TemplateMatcher
        results['template_matcher'] = self.test_template_matcher()

        self.test_results['common_ai_services'] = results
        print()

    def test_unified_search_engine(self) -> Dict[str, Any]:
        """Test UnifiedSearchEngine functionality."""
        print("Testing UnifiedSearchEngine...")

        result = {
            'available': False,
            'service_initialization': False,
            'query_parsing': False,
            'module_search': False,
            'result_ranking': False,
            'summary_generation': False,
            'performance': {},
            'errors': []
        }

        try:
            from common.ai_services import UnifiedSearchEngine, HAS_UNIFIED_SEARCH

            result['available'] = HAS_UNIFIED_SEARCH

            if HAS_UNIFIED_SEARCH:
                engine = UnifiedSearchEngine()
                result['service_initialization'] = True

                if self.verbose:
                    print("  ✓ UnifiedSearchEngine initialized")

                # Test search functionality
                test_queries = [
                    "Bangsamoro communities in Region IX",
                    "education programs for Muslim youth",
                    "livelihood assistance for fisher folk"
                ]

                for query in test_queries:
                    try:
                        start_time = time.time()
                        search_results = engine.search(query, limit=10)
                        end_time = time.time()

                        if search_results and 'results' in search_results:
                            total_results = search_results.get('total_results', 0)
                            result['module_search'] = True
                            result['performance'][f'search_time_{len(query.split())}_words'] = end_time - start_time

                            if self.verbose:
                                print(f"  ✓ Search '{query[:20]}...': {total_results} results in {end_time - start_time:.3f}s")

                            # Test summary generation
                            if search_results.get('summary'):
                                result['summary_generation'] = True

                                if self.verbose:
                                    print(f"    Summary: {search_results['summary'][:100]}...")
                        else:
                            result['errors'].append(f"Search returned invalid results for: {query}")

                    except Exception as search_error:
                        result['errors'].append(f"Search failed for '{query}': {str(search_error)}")
                        if self.verbose:
                            print(f"  ❌ Search failed for '{query}': {search_error}")

                # Test index statistics
                try:
                    stats = engine.get_index_stats()
                    result['performance']['index_stats'] = stats

                    if self.verbose:
                        print("  ✓ Index statistics retrieved")
                        for module, stat in stats.items():
                            if isinstance(stat, dict) and 'vector_count' in stat:
                                print(f"    {module}: {stat['vector_count']} vectors")

                except Exception as stats_error:
                    result['errors'].append(f"Index stats failed: {str(stats_error)}")
                    if self.verbose:
                        print(f"  ❌ Index stats failed: {stats_error}")
            else:
                result['errors'].append("UnifiedSearchEngine not available - missing dependencies")
                print("  ❌ UnifiedSearchEngine not available")

        except Exception as e:
            error_msg = f"UnifiedSearchEngine test failed: {str(e)}"
            result['errors'].append(error_msg)
            print(f"  ❌ {error_msg}")

            if self.verbose:
                print(f"    Traceback: {traceback.format_exc()}")

        return result

    def test_query_parser(self) -> Dict[str, Any]:
        """Test QueryParser functionality."""
        print("Testing QueryParser...")

        result = {
            'available': False,
            'service_initialization': False,
            'query_parsing': False,
            'intent_recognition': False,
            'filter_extraction': False,
            'fallback_parsing': False,
            'performance': {},
            'errors': []
        }

        try:
            from common.ai_services import QueryParser

            parser = QueryParser()
            result['available'] = True
            result['service_initialization'] = True

            if self.verbose:
                print("  ✓ QueryParser initialized")

            # Test query parsing
            test_queries = [
                "coastal fishing communities in Zamboanga",
                "education programs in Region IX",
                "health services for Muslim communities last year",
                "infrastructure projects in Lanao del Sur"
            ]

            for query in test_queries:
                try:
                    start_time = time.time()
                    parsed = parser.parse(query)
                    end_time = time.time()

                    if parsed and isinstance(parsed, dict):
                        result['query_parsing'] = True

                        # Check for required fields
                        if parsed.get('keywords'):
                            result['intent_recognition'] = True
                        if parsed.get('filters'):
                            result['filter_extraction'] = True

                        result['performance'][f'parse_time_{len(query.split())}_words'] = end_time - start_time

                        if self.verbose:
                            print(f"  ✓ Parsed: '{query[:30]}...'")
                            print(f"    Keywords: {parsed.get('keywords', [])}")
                            print(f"    Intent: {parsed.get('intent')}")
                            print(f"    Modules: {parsed.get('suggested_modules', [])}")
                    else:
                        result['errors'].append(f"Invalid parse result for: {query}")

                except Exception as parse_error:
                    result['errors'].append(f"Parse failed for '{query}': {str(parse_error)}")
                    if self.verbose:
                        print(f"  ❌ Parse failed for '{query}': {parse_error}")

            # Test fallback parsing (if Gemini not available)
            if not hasattr(parser, 'gemini') or parser.gemini is None:
                result['fallback_parsing'] = True
                if self.verbose:
                    print("  ✓ Fallback parsing available")

        except Exception as e:
            error_msg = f"QueryParser test failed: {str(e)}"
            result['errors'].append(error_msg)
            print(f"  ❌ {error_msg}")

            if self.verbose:
                print(f"    Traceback: {traceback.format_exc()}")

        return result

    def test_template_matcher(self) -> Dict[str, Any]:
        """Test TemplateMatcher functionality."""
        print("Testing TemplateMatcher...")

        result = {
            'available': False,
            'service_initialization': False,
            'template_matching': False,
            'query_generation': False,
            'entity_substitution': False,
            'performance': {},
            'errors': []
        }

        try:
            from common.ai_services.chat.template_matcher import get_template_matcher

            matcher = get_template_matcher()
            result['available'] = True
            result['service_initialization'] = True

            if self.verbose:
                print("  ✓ TemplateMatcher initialized")

            # Test template matching
            test_queries = [
                ("How many communities in Region IX?", {
                    'location': {'type': 'region', 'value': 'Region IX', 'confidence': 0.95}
                }),
                ("Show me workshops in last 6 months", {
                    'date_range': {'start': '2024-10-15', 'end': '2025-04-15'}
                }),
                ("What policies for education sector?", {
                    'sector': {'type': 'sector', 'value': 'education', 'confidence': 0.90}
                })
            ]

            for query, entities in test_queries:
                try:
                    start_time = time.time()
                    match_result = matcher.match_and_generate(
                        query,
                        entities,
                        intent='data_query'
                    )
                    end_time = time.time()

                    if match_result and isinstance(match_result, dict):
                        if match_result.get('success'):
                            result['template_matching'] = True

                            if match_result.get('query'):
                                result['query_generation'] = True

                            if entities:
                                result['entity_substitution'] = True

                            result['performance'][f'match_time_{len(query.split())}_words'] = end_time - start_time
                            result['performance'][f'match_score_{len(query.split())}_words'] = match_result.get('score', 0.0)

                            if self.verbose:
                                print(f"  ✓ Matched: '{query[:30]}...'")
                                print(f"    Score: {match_result.get('score', 0.0):.2f}")
                                if match_result.get('query'):
                                    print(f"    Generated: {match_result['query'][:100]}...")
                        else:
                            result['errors'].append(f"Template match failed for: {query} - {match_result.get('error')}")
                            if self.verbose:
                                print(f"  ⚠ Template match failed: {match_result.get('error')}")
                    else:
                        result['errors'].append(f"Invalid match result for: {query}")

                except Exception as match_error:
                    result['errors'].append(f"Match failed for '{query}': {str(match_error)}")
                    if self.verbose:
                        print(f"  ❌ Match failed for '{query}': {match_error}")

        except Exception as e:
            error_msg = f"TemplateMatcher test failed: {str(e)}"
            result['errors'].append(error_msg)
            print(f"  ❌ {error_msg}")

            if self.verbose:
                print(f"    Traceback: {traceback.format_exc()}")

        return result

    def test_ai_features(self):
        """Test AI-powered features."""
        print("✨ TESTING AI-POWERED FEATURES")
        print("-" * 50)

        results = {}

        # Test semantic search
        results['semantic_search'] = self.test_semantic_search()

        # Test intelligent recommendations
        results['intelligent_recommendations'] = self.test_intelligent_recommendations()

        # Test natural language processing
        results['natural_language_processing'] = self.test_natural_language_processing()

        self.test_results['ai_features'] = results
        print()

    def test_semantic_search(self) -> Dict[str, Any]:
        """Test semantic search capabilities."""
        print("Testing Semantic Search...")

        result = {
            'available': False,
            'cross_module_search': False,
            'similarity_matching': False,
            'context_awareness': False,
            'performance': {},
            'errors': []
        }

        try:
            # Test if semantic search components are available
            from ai_assistant.services import HAS_EMBEDDING_SERVICE, HAS_VECTOR_STORE, HAS_SIMILARITY_SEARCH
            from common.ai_services import HAS_UNIFIED_SEARCH

            result['available'] = HAS_EMBEDDING_SERVICE and HAS_VECTOR_STORE and HAS_SIMILARITY_SEARCH

            if result['available']:
                # Test cross-module search
                try:
                    from common.ai_services import UnifiedSearchEngine
                    engine = UnifiedSearchEngine()

                    start_time = time.time()
                    results = engine.search("Muslim communities education programs", limit=20)
                    end_time = time.time()

                    if results and 'results' in results:
                        result['cross_module_search'] = True
                        result['performance']['cross_module_search_time'] = end_time - start_time
                        result['performance']['modules_searched'] = len(results['results'])

                        if self.verbose:
                            print(f"  ✓ Cross-module search in {end_time - start_time:.3f}s")
                            for module, items in results['results'].items():
                                if items:
                                    print(f"    {module}: {len(items)} results")
                    else:
                        result['errors'].append("Cross-module search returned invalid results")

                except Exception as cms_error:
                    result['errors'].append(f"Cross-module search failed: {str(cms_error)}")
                    print(f"  ❌ Cross-module search failed: {cms_error}")

                # Test similarity matching
                try:
                    from ai_assistant.services import SimilaritySearchService
                    service = SimilaritySearchService()

                    # Test with a semantic query
                    start_time = time.time()
                    similar = service.search_communities("coastal fishing villages", limit=5)
                    end_time = time.time()

                    result['similarity_matching'] = True  # Service works even if no data
                    result['performance']['similarity_search_time'] = end_time - start_time

                    if self.verbose:
                        print(f"  ✓ Similarity search in {end_time - start_time:.3f}s")
                        if similar:
                            print(f"    Found {len(similar)} similar communities")
                        else:
                            print("    No indexed communities found (service works)")

                except Exception as sim_error:
                    result['errors'].append(f"Similarity matching failed: {str(sim_error)}")
                    print(f"  ❌ Similarity matching failed: {sim_error}")

                # Test context awareness
                try:
                    from ai_assistant.services import GeminiService
                    gemini = GeminiService()

                    start_time = time.time()
                    response = gemini.chat_with_ai(
                        "What are the main needs of coastal fishing communities in BARMM?",
                        context="User is viewing community needs assessment dashboard"
                    )
                    end_time = time.time()

                    if response.get('success'):
                        result['context_awareness'] = True
                        result['performance']['context_aware_time'] = end_time - start_time

                        if self.verbose:
                            print(f"  ✓ Context-aware response in {end_time - start_time:.3f}s")
                    else:
                        result['errors'].append("Context-aware response failed")

                except Exception as ctx_error:
                    result['errors'].append(f"Context awareness test failed: {str(ctx_error)}")
                    print(f"  ❌ Context awareness test failed: {ctx_error}")
            else:
                missing = []
                if not HAS_EMBEDDING_SERVICE:
                    missing.append("EmbeddingService")
                if not HAS_VECTOR_STORE:
                    missing.append("VectorStore")
                if not HAS_SIMILARITY_SEARCH:
                    missing.append("SimilaritySearchService")

                result['errors'].append(f"Missing semantic search dependencies: {', '.join(missing)}")
                print(f"  ❌ Semantic search not available - missing {', '.join(missing)}")

        except Exception as e:
            error_msg = f"Semantic search test failed: {str(e)}"
            result['errors'].append(error_msg)
            print(f"  ❌ {error_msg}")

            if self.verbose:
                print(f"    Traceback: {traceback.format_exc()}")

        return result

    def test_intelligent_recommendations(self) -> Dict[str, Any]:
        """Test intelligent recommendation capabilities."""
        print("Testing Intelligent Recommendations...")

        result = {
            'available': False,
            'content_recommendations': False,
            'similar_content_suggestions': False,
            'personalization': False,
            'performance': {},
            'errors': []
        }

        try:
            # Test AI-powered recommendations
            from ai_assistant.services import GeminiService

            service = GeminiService()
            result['available'] = True

            # Test content recommendations
            try:
                prompt = """
                Based on this community profile, recommend 3 specific programs:
                - Community: Coastal fishing village in Sulu
                - Population: 250 households
                - Main livelihood: Small-scale fishing
                - Challenges: Declining fish catch, limited market access

                Recommend specific OOBC programs for this community.
                """

                start_time = time.time()
                response = service.generate_text(prompt)
                end_time = time.time()

                if response.get('success') and response.get('text'):
                    result['content_recommendations'] = True
                    result['performance']['recommendation_time'] = end_time - start_time

                    if self.verbose:
                        print(f"  ✓ Generated recommendations in {end_time - start_time:.3f}s")
                        print(f"    Response length: {len(response['text'])} characters")
                else:
                    result['errors'].append("Content recommendation generation failed")

            except Exception as rec_error:
                result['errors'].append(f"Content recommendation failed: {str(rec_error)}")
                print(f"  ❌ Content recommendation failed: {rec_error}")

            # Test similar content suggestions
            try:
                from ai_assistant.services import SimilaritySearchService

                search_service = SimilaritySearchService()

                start_time = time.time()
                similar_communities = search_service.search_communities(
                    "fishing village with market access challenges",
                    limit=3
                )
                end_time = time.time()

                result['similar_content_suggestions'] = True  # Service works
                result['performance']['similarity_suggestion_time'] = end_time - start_time

                if self.verbose:
                    print(f"  ✓ Similar content suggestions in {end_time - start_time:.3f}s")
                    if similar_communities:
                        print(f"    Found {len(similar_communities)} similar communities")
                    else:
                        print("    No indexed communities (service works)")

            except Exception as sim_error:
                result['errors'].append(f"Similar content suggestions failed: {str(sim_error)}")
                print(f"  ❌ Similar content suggestions failed: {sim_error}")

            # Test personalization (user role-based responses)
            try:
                start_time = time.time()
                admin_response = service.chat_with_ai(
                    "Show me community assessment data",
                    context="User is an OOBC Administrator"
                )

                staff_response = service.chat_with_ai(
                    "Show me community assessment data",
                    context="User is a Field Staff"
                )
                end_time = time.time()

                if admin_response.get('success') and staff_response.get('success'):
                    result['personalization'] = True
                    result['performance']['personalization_time'] = end_time - start_time

                    if self.verbose:
                        print(f"  ✓ Personalized responses in {end_time - start_time:.3f}s")
                        if admin_response['message'] != staff_response['message']:
                            print("    ✓ Responses differ by user role")
                        else:
                            print("    ⚠ Responses are identical (may need improvement)")
                else:
                    result['errors'].append("Personalization test failed")

            except Exception as pers_error:
                result['errors'].append(f"Personalization test failed: {str(pers_error)}")
                print(f"  ❌ Personalization test failed: {pers_error}")

        except Exception as e:
            error_msg = f"Intelligent recommendations test failed: {str(e)}"
            result['errors'].append(error_msg)
            print(f"  ❌ {error_msg}")

            if self.verbose:
                print(f"    Traceback: {traceback.format_exc()}")

        return result

    def test_natural_language_processing(self) -> Dict[str, Any]:
        """Test natural language processing capabilities."""
        print("Testing Natural Language Processing...")

        result = {
            'available': False,
            'entity_extraction': False,
            'intent_classification': False,
            'language_understanding': False,
            'cultural_context': False,
            'performance': {},
            'errors': []
        }

        try:
            # Test entity extraction
            from common.ai_services.chat.entity_extractor import EntityExtractor

            extractor = EntityExtractor()
            result['available'] = True

            # Test entity extraction
            test_texts = [
                "How many Tausug communities are in Zamboanga del Norte?",
                "Show me fishing livelihood programs in Sulu last year",
                "What are the education needs of Maranao communities in Lanao?",
                "Health services for Muslim communities in Region IX"
            ]

            for text in test_texts:
                try:
                    start_time = time.time()
                    entities = extractor.extract_entities(text)
                    end_time = time.time()

                    if entities:
                        result['entity_extraction'] = True
                        result['performance'][f'entity_extraction_{len(text.split())}_words'] = end_time - start_time

                        if self.verbose:
                            print(f"  ✓ Extracted entities from: '{text[:40]}...'")
                            for entity_type, entity_list in entities.items():
                                if entity_list:
                                    print(f"    {entity_type}: {entity_list}")
                    else:
                        result['errors'].append(f"No entities extracted from: {text}")

                except Exception as ext_error:
                    result['errors'].append(f"Entity extraction failed: {str(ext_error)}")
                    print(f"  ❌ Entity extraction failed: {ext_error}")

            # Test intent classification
            try:
                from common.ai_services import QueryParser

                parser = QueryParser()

                for text in test_texts:
                    start_time = time.time()
                    parsed = parser.parse(text)
                    end_time = time.time()

                    if parsed and parsed.get('intent'):
                        result['intent_classification'] = True
                        result['performance'][f'intent_classification_{len(text.split())}_words'] = end_time - start_time

                        if self.verbose:
                            print(f"  ✓ Intent for '{text[:30]}...': {parsed.get('intent')}")
                    else:
                        result['errors'].append(f"Intent classification failed for: {text}")

            except Exception as intent_error:
                result['errors'].append(f"Intent classification failed: {str(intent_error)}")
                print(f"  ❌ Intent classification failed: {intent_error}")

            # Test language understanding
            try:
                from ai_assistant.services import GeminiService

                gemini = GeminiService()

                complex_query = """
                Compare the educational attainment levels between Maranao communities
                in Lanao del Sur and Tausug communities in Sulu, focusing on factors
                that affect school attendance rates.
                """

                start_time = time.time()
                response = gemini.generate_text(complex_query)
                end_time = time.time()

                if response.get('success') and response.get('text'):
                    result['language_understanding'] = True
                    result['performance']['complex_understanding_time'] = end_time - start_time

                    if self.verbose:
                        print(f"  ✓ Complex query understanding in {end_time - start_time:.3f}s")
                        print(f"    Response: {response['text'][:100]}...")
                else:
                    result['errors'].append("Complex language understanding failed")

            except Exception as lang_error:
                result['errors'].append(f"Language understanding test failed: {str(lang_error)}")
                print(f"  ❌ Language understanding test failed: {lang_error}")

            # Test cultural context integration
            try:
                start_time = time.time()
                response = gemini.generate_text(
                    "What considerations are important when working with Muslim communities?",
                    include_cultural_context=True
                )
                end_time = time.time()

                if response.get('success'):
                    result['cultural_context'] = True
                    result['performance']['cultural_context_time'] = end_time - start_time

                    if self.verbose:
                        print(f"  ✓ Cultural context integration in {end_time - start_time:.3f}s")
                else:
                    result['errors'].append("Cultural context integration failed")

            except Exception as cult_error:
                result['errors'].append(f"Cultural context test failed: {str(cult_error)}")
                print(f"  ❌ Cultural context test failed: {cult_error}")

        except Exception as e:
            error_msg = f"NLP test failed: {str(e)}"
            result['errors'].append(error_msg)
            print(f"  ❌ {error_msg}")

            if self.verbose:
                print(f"    Traceback: {traceback.format_exc()}")

        return result

    def test_performance_metrics(self):
        """Test AI performance metrics."""
        print("📊 TESTING PERFORMANCE METRICS")
        print("-" * 50)

        results = {}

        # Test embedding performance
        results['embedding_performance'] = self.test_embedding_performance()

        # Test search performance
        results['search_performance'] = self.test_search_performance()

        # Test memory usage
        results['memory_usage'] = self.test_memory_usage()

        self.test_results['performance_metrics'] = results
        print()

    def test_embedding_performance(self) -> Dict[str, Any]:
        """Test embedding generation performance."""
        print("Testing Embedding Performance...")

        result = {
            'single_embedding': {},
            'batch_embedding': {},
            'similarity_calculation': {},
            'errors': []
        }

        try:
            from ai_assistant.services import EmbeddingService, HAS_EMBEDDING_SERVICE

            if not HAS_EMBEDDING_SERVICE:
                result['errors'].append("EmbeddingService not available")
                return result

            service = EmbeddingService()

            # Test single embedding performance
            texts = [
                "Short text",
                "Medium length text with some details about the community",
                "Very long text that describes in detail the various aspects of Bangsamoro communities including their cultural practices, economic activities, social structures, and the challenges they face in maintaining their traditional way of life while adapting to modern development"
            ]

            for text in texts:
                try:
                    # Multiple iterations for average
                    times = []
                    for _ in range(5):
                        start_time = time.time()
                        embedding = service.generate_embedding(text)
                        end_time = time.time()
                        times.append(end_time - start_time)

                    avg_time = sum(times) / len(times)
                    result['single_embedding'][f'len_{len(text)}'] = {
                        'avg_time': avg_time,
                        'min_time': min(times),
                        'max_time': max(times),
                        'dimension': len(embedding) if embedding is not None else 0
                    }

                    if self.verbose:
                        print(f"  ✓ Single embedding (len={len(text)}): {avg_time:.3f}s avg")

                except Exception as e:
                    result['errors'].append(f"Single embedding test failed: {str(e)}")

            # Test batch performance
            batch_sizes = [1, 5, 10, 25]

            for batch_size in batch_sizes:
                try:
                    batch_texts = [texts[1]] * batch_size

                    start_time = time.time()
                    embeddings = service.batch_generate(batch_texts)
                    end_time = time.time()

                    if embeddings is not None and len(embeddings) == batch_size:
                        throughput = batch_size / (end_time - start_time)
                        result['batch_embedding'][f'batch_{batch_size}'] = {
                            'total_time': end_time - start_time,
                            'throughput': throughput,
                            'avg_per_item': (end_time - start_time) / batch_size
                        }

                        if self.verbose:
                            print(f"  ✓ Batch {batch_size}: {throughput:.1f} items/sec")
                    else:
                        result['errors'].append(f"Batch embedding failed for size {batch_size}")

                except Exception as e:
                    result['errors'].append(f"Batch test failed for size {batch_size}: {str(e)}")

            # Test similarity calculation performance
            try:
                import numpy as np

                # Generate test embeddings
                embedding1 = service.generate_embedding(texts[0])
                embedding2 = service.generate_embedding(texts[1])

                times = []
                for _ in range(1000):
                    start_time = time.time()
                    similarity = service.compute_similarity(embedding1, embedding2)
                    end_time = time.time()
                    times.append(end_time - start_time)

                avg_time = sum(times) / len(times)
                result['similarity_calculation'] = {
                    'avg_time': avg_time,
                    'total_tests': len(times),
                    'throughput': 1 / avg_time
                }

                if self.verbose:
                    print(f"  ✓ Similarity calculation: {1/avg_time:.0f} ops/sec")

            except Exception as e:
                result['errors'].append(f"Similarity calculation test failed: {str(e)}")

        except Exception as e:
            error_msg = f"Embedding performance test failed: {str(e)}"
            result['errors'].append(error_msg)
            print(f"  ❌ {error_msg}")

        return result

    def test_search_performance(self) -> Dict[str, Any]:
        """Test search performance."""
        print("Testing Search Performance...")

        result = {
            'vector_search': {},
            'semantic_search': {},
            'unified_search': {},
            'errors': []
        }

        try:
            # Test vector search performance
            from ai_assistant.services import VectorStore, HAS_VECTOR_STORE
            from ai_assistant.services import EmbeddingService, HAS_EMBEDDING_SERVICE

            if HAS_VECTOR_STORE and HAS_EMBEDDING_SERVICE:
                import numpy as np

                # Create test store
                store = VectorStore('performance_test', dimension=384)

                # Add test vectors
                sizes = [100, 500, 1000]

                for size in sizes:
                    try:
                        test_vectors = np.random.rand(size, 384).astype('float32')
                        test_metadata = [{'id': i, 'type': 'test'} for i in range(size)]

                        # Add vectors
                        start_time = time.time()
                        store.add_vectors(test_vectors, test_metadata)
                        add_time = time.time() - start_time

                        # Test search performance
                        query_vector = np.random.rand(384).astype('float32')

                        search_times = []
                        for _ in range(10):
                            start_time = time.time()
                            results = store.search(query_vector, k=10)
                            end_time = time.time()
                            search_times.append(end_time - start_time)

                        avg_search_time = sum(search_times) / len(search_times)

                        result['vector_search'][f'size_{size}'] = {
                            'add_time': add_time,
                            'avg_search_time': avg_search_time,
                            'search_throughput': 1 / avg_search_time,
                            'vectors_count': size
                        }

                        if self.verbose:
                            print(f"  ✓ Vector search (n={size}): {avg_search_time:.4f}s avg, {1/avg_search_time:.0f} ops/sec")

                    except Exception as e:
                        result['errors'].append(f"Vector search test failed for size {size}: {str(e)}")
            else:
                result['errors'].append("VectorStore or EmbeddingService not available")

            # Test semantic search performance
            from common.ai_services import UnifiedSearchEngine, HAS_UNIFIED_SEARCH

            if HAS_UNIFIED_SEARCH:
                try:
                    engine = UnifiedSearchEngine()

                    queries = [
                        "short",
                        "medium length query about communities",
                        "very long detailed query about specific aspects of Bangsamoro communities and their needs"
                    ]

                    for query in queries:
                        try:
                            times = []
                            for _ in range(3):
                                start_time = time.time()
                                results = engine.search(query, limit=20)
                                end_time = time.time()
                                times.append(end_time - start_time)

                            avg_time = sum(times) / len(times)
                            result['semantic_search'][f'len_{len(query)}'] = {
                                'avg_time': avg_time,
                                'total_results': results.get('total_results', 0) if results else 0
                            }

                            if self.verbose:
                                print(f"  ✓ Semantic search (len={len(query)}): {avg_time:.3f}s avg")

                        except Exception as e:
                            result['errors'].append(f"Semantic search failed for query length {len(query)}: {str(e)}")
                except Exception as e:
                    result['errors'].append(f"Semantic search test failed: {str(e)}")
            else:
                result['errors'].append("UnifiedSearchEngine not available")

        except Exception as e:
            error_msg = f"Search performance test failed: {str(e)}"
            result['errors'].append(error_msg)
            print(f"  ❌ {error_msg}")

        return result

    def test_memory_usage(self) -> Dict[str, Any]:
        """Test memory usage of AI services."""
        print("Testing Memory Usage...")

        result = {
            'embedding_service': {},
            'vector_store': {},
            'gemini_service': {},
            'errors': []
        }

        try:
            import psutil
            import os

            process = psutil.Process(os.getpid())

            # Get baseline memory
            baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

            # Test EmbeddingService memory
            try:
                from ai_assistant.services import EmbeddingService, HAS_EMBEDDING_SERVICE

                if HAS_EMBEDDING_SERVICE:
                    pre_load_memory = process.memory_info().rss / 1024 / 1024
                    service = EmbeddingService()
                    post_load_memory = process.memory_info().rss / 1024 / 1024

                    result['embedding_service'] = {
                        'baseline_mb': baseline_memory,
                        'pre_load_mb': pre_load_memory,
                        'post_load_mb': post_load_memory,
                        'model_overhead_mb': post_load_memory - pre_load_memory
                    }

                    if self.verbose:
                        overhead = post_load_memory - pre_load_memory
                        print(f"  ✓ EmbeddingService model overhead: {overhead:.1f} MB")
                else:
                    result['errors'].append("EmbeddingService not available")

            except Exception as e:
                result['errors'].append(f"EmbeddingService memory test failed: {str(e)}")

            # Test VectorStore memory
            try:
                from ai_assistant.services import VectorStore, HAS_VECTOR_STORE

                if HAS_VECTOR_STORE:
                    import numpy as np

                    pre_store_memory = process.memory_info().rss / 1024 / 1024

                    # Create store with vectors
                    store = VectorStore('memory_test', dimension=384)
                    test_vectors = np.random.rand(1000, 384).astype('float32')
                    test_metadata = [{'id': i, 'type': 'test'} for i in range(1000)]

                    store.add_vectors(test_vectors, test_metadata)
                    post_store_memory = process.memory_info().rss / 1024 / 1024

                    result['vector_store'] = {
                        'pre_store_mb': pre_store_memory,
                        'post_store_mb': post_store_memory,
                        'memory_per_1000_vectors_mb': post_store_memory - pre_store_memory,
                        'vectors_stored': 1000
                    }

                    if self.verbose:
                        memory_1000 = post_store_memory - pre_store_memory
                        print(f"  ✓ VectorStore: {memory_1000:.1f} MB for 1000 vectors")

                        # Clean up
                        store_path = store.get_storage_path()
                        if store_path.exists():
                            os.remove(store_path)
                        metadata_path = store_path.with_suffix('.metadata')
                        if metadata_path.exists():
                            os.remove(metadata_path)
                else:
                    result['errors'].append("VectorStore not available")

            except Exception as e:
                result['errors'].append(f"VectorStore memory test failed: {str(e)}")

            # Test GeminiService memory
            try:
                from ai_assistant.services import GeminiService

                pre_gemini_memory = process.memory_info().rss / 1024 / 1024
                service = GeminiService()
                post_init_memory = process.memory_info().rss / 1024 / 1024

                # Generate some text
                response = service.generate_text("Test query", use_cache=False)
                post_generation_memory = process.memory_info().rss / 1024 / 1024

                result['gemini_service'] = {
                    'pre_init_mb': pre_gemini_memory,
                    'post_init_mb': post_init_memory,
                    'post_generation_mb': post_generation_memory,
                    'init_overhead_mb': post_init_memory - pre_gemini_memory,
                    'generation_overhead_mb': post_generation_memory - post_init_memory
                }

                if self.verbose:
                    init_overhead = post_init_memory - pre_gemini_memory
                    gen_overhead = post_generation_memory - post_init_memory
                    print(f"  ✓ GeminiService: {init_overhead:.1f} MB init, {gen_overhead:.1f} MB generation")

            except Exception as e:
                result['errors'].append(f"GeminiService memory test failed: {str(e)}")

        except ImportError:
            result['errors'].append("psutil not available for memory testing")
            print("  ⚠ psutil not available - skipping memory tests")
        except Exception as e:
            error_msg = f"Memory usage test failed: {str(e)}"
            result['errors'].append(error_msg)
            print(f"  ❌ {error_msg}")

        return result

    def test_integration_across_apps(self):
        """Test AI services integration across different apps."""
        print("🔗 TESTING INTEGRATION ACROSS APPS")
        print("-" * 50)

        results = {}

        # Test Communities integration
        results['communities_integration'] = self.test_communities_integration()

        # Test MANA integration
        results['mana_integration'] = self.test_mana_integration()

        # Test Policies integration
        results['policies_integration'] = self.test_policies_integration()

        # Test Coordination integration
        results['coordination_integration'] = self.test_coordination_integration()

        self.test_results['integration_status'] = results
        print()

    def test_communities_integration(self) -> Dict[str, Any]:
        """Test AI integration with Communities module."""
        print("Testing Communities Integration...")

        result = {
            'model_access': False,
            'search_integration': False,
            'ai_features': False,
            'errors': []
        }

        try:
            # Test model access
            try:
                from communities.models import CommunityProfileBase

                # Check if model exists and is accessible
                count = CommunityProfileBase.objects.count()
                result['model_access'] = True

                if self.verbose:
                    print(f"  ✓ Communities model accessible: {count} profiles")

            except Exception as model_error:
                result['errors'].append(f"Communities model access failed: {str(model_error)}")
                print(f"  ❌ Communities model access failed: {model_error}")
                return result

            # Test search integration
            try:
                from ai_assistant.services import SimilaritySearchService, HAS_SIMILARITY_SEARCH

                if HAS_SIMILARITY_SEARCH:
                    service = SimilaritySearchService()

                    # Test community search
                    results = service.search_communities("Muslim communities", limit=5)
                    result['search_integration'] = True

                    if self.verbose:
                        if results:
                            print(f"  ✓ Community search integration: {len(results)} results")
                        else:
                            print("  ⚠ Community search works but no indexed data")
                else:
                    result['errors'].append("SimilaritySearchService not available")

            except Exception as search_error:
                result['errors'].append(f"Community search integration failed: {str(search_error)}")
                print(f"  ❌ Community search integration failed: {search_error}")

            # Test AI features
            try:
                from ai_assistant.services import GeminiService

                gemini = GeminiService()

                # Test community-specific queries
                query = """
                Analyze this community profile and provide insights:
                - Location: Coastal area in Zamboanga
                - Population: 150 households
                - Primary livelihood: Fishing
                - Challenges: Limited market access, climate change impacts

                Provide specific recommendations for OOBC programs.
                """

                response = gemini.generate_text(query)

                if response.get('success'):
                    result['ai_features'] = True

                    if self.verbose:
                        print("  ✓ AI community analysis working")
                else:
                    result['errors'].append("AI community analysis failed")

            except Exception as ai_error:
                result['errors'].append(f"AI features test failed: {str(ai_error)}")
                print(f"  ❌ AI features test failed: {ai_error}")

        except Exception as e:
            error_msg = f"Communities integration test failed: {str(e)}"
            result['errors'].append(error_msg)
            print(f"  ❌ {error_msg}")

        return result

    def test_mana_integration(self) -> Dict[str, Any]:
        """Test AI integration with MANA module."""
        print("Testing MANA Integration...")

        result = {
            'model_access': False,
            'assessment_analysis': False,
            'needs_extraction': False,
            'recommendation_generation': False,
            'errors': []
        }

        try:
            # Test model access
            try:
                from mana.models import WorkshopActivity

                count = WorkshopActivity.objects.count()
                result['model_access'] = True

                if self.verbose:
                    print(f"  ✓ MANA model accessible: {count} activities")

            except Exception as model_error:
                result['errors'].append(f"MANA model access failed: {str(model_error)}")
                print(f"  ❌ MANA model access failed: {model_error}")
                return result

            # Test assessment analysis
            try:
                from ai_assistant.services import GeminiService

                gemini = GeminiService()

                # Test needs assessment analysis
                sample_assessment = """
                Community Needs Assessment - Tausug Fishing Village:

                Education Needs:
                - Elementary school overcrowded (150 students, 3 classrooms)
                - No high school within 10km
                - Lack of textbooks and learning materials

                Health Needs:
                - No health center in barangay
                - Nearest clinic 15km away
                - High incidence of water-borne diseases

                Infrastructure Needs:
                - Unpaved roads become impassable during rainy season
                - No reliable electricity supply
                - Limited access to clean water
                """

                response = gemini.generate_text(
                    f"Analyze this needs assessment and identify priority needs:\n{sample_assessment}"
                )

                if response.get('success'):
                    result['assessment_analysis'] = True

                    if self.verbose:
                        print("  ✓ AI needs assessment analysis working")
                else:
                    result['errors'].append("Needs assessment analysis failed")

            except Exception as analysis_error:
                result['errors'].append(f"Assessment analysis failed: {str(analysis_error)}")
                print(f"  ❌ Assessment analysis failed: {analysis_error}")

            # Test needs extraction
            try:
                response = gemini.generate_text(
                    f"Extract specific needs from this assessment and categorize them:\n{sample_assessment}",
                    temperature=0.3
                )

                if response.get('success'):
                    result['needs_extraction'] = True

                    if self.verbose:
                        print("  ✓ AI needs extraction working")
                else:
                    result['errors'].append("Needs extraction failed")

            except Exception as extraction_error:
                result['errors'].append(f"Needs extraction failed: {str(extraction_error)}")
                print(f"  ❌ Needs extraction failed: {extraction_error}")

            # Test recommendation generation
            try:
                response = gemini.generate_text(
                    f"Based on the needs assessment, generate 3 specific program recommendations:\n{sample_assessment}"
                )

                if response.get('success'):
                    result['recommendation_generation'] = True

                    if self.verbose:
                        print("  ✓ AI recommendation generation working")
                else:
                    result['errors'].append("Recommendation generation failed")

            except Exception as rec_error:
                result['errors'].append(f"Recommendation generation failed: {str(rec_error)}")
                print(f"  ❌ Recommendation generation failed: {rec_error}")

        except Exception as e:
            error_msg = f"MANA integration test failed: {str(e)}"
            result['errors'].append(error_msg)
            print(f"  ❌ {error_msg}")

        return result

    def test_policies_integration(self) -> Dict[str, Any]:
        """Test AI integration with Policies module."""
        print("Testing Policies Integration...")

        result = {
            'model_access': False,
            'policy_analysis': False,
            'impact_assessment': False,
            'policy_recommendations': False,
            'errors': []
        }

        try:
            # Test model access
            try:
                from recommendations.policy_tracking.models import PolicyRecommendation

                count = PolicyRecommendation.objects.count()
                result['model_access'] = True

                if self.verbose:
                    print(f"  ✓ Policies model accessible: {count} policies")

            except Exception as model_error:
                result['errors'].append(f"Policies model access failed: {str(model_error)}")
                print(f"  ❌ Policies model access failed: {model_error}")
                return result

            # Test policy analysis
            try:
                from ai_assistant.services import GeminiService

                gemini = GeminiService()

                sample_policy = """
                Policy Recommendation: Sustainable Livelihood Program for Coastal Communities

                Problem Statement:
                Coastal fishing communities face declining fish catches due to:
                - Overfishing in traditional grounds
                - Climate change impacts on marine ecosystems
                - Limited alternative livelihood options
                - Poor market access for fish products

                Proposed Solution:
                1. Establish community-managed marine protected areas
                2. Provide training in sustainable aquaculture
                3. Develop cold storage and processing facilities
                4. Create direct market linkages to urban centers

                Budget Required: ₱5,000,000
                Implementation Timeline: 24 months
                Target Beneficiaries: 500 households across 5 communities
                """

                response = gemini.generate_text(
                    f"Analyze this policy recommendation for strengths, weaknesses, and feasibility:\n{sample_policy}"
                )

                if response.get('success'):
                    result['policy_analysis'] = True

                    if self.verbose:
                        print("  ✓ AI policy analysis working")
                else:
                    result['errors'].append("Policy analysis failed")

            except Exception as analysis_error:
                result['errors'].append(f"Policy analysis failed: {str(analysis_error)}")
                print(f"  ❌ Policy analysis failed: {analysis_error}")

            # Test impact assessment
            try:
                response = gemini.generate_text(
                    f"Assess the potential social, economic, and environmental impact of this policy:\n{sample_policy}"
                )

                if response.get('success'):
                    result['impact_assessment'] = True

                    if self.verbose:
                        print("  ✓ AI impact assessment working")
                else:
                    result['errors'].append("Impact assessment failed")

            except Exception as impact_error:
                result['errors'].append(f"Impact assessment failed: {str(impact_error)}")
                print(f"  ❌ Impact assessment failed: {impact_error}")

            # Test policy recommendations
            try:
                response = gemini.generate_text(
                    f"Review this policy and suggest improvements or additional recommendations:\n{sample_policy}"
                )

                if response.get('success'):
                    result['policy_recommendations'] = True

                    if self.verbose:
                        print("  ✓ AI policy recommendations working")
                else:
                    result['errors'].append("Policy recommendations failed")

            except Exception as rec_error:
                result['errors'].append(f"Policy recommendations failed: {str(rec_error)}")
                print(f"  ❌ Policy recommendations failed: {rec_error}")

        except Exception as e:
            error_msg = f"Policies integration test failed: {str(e)}"
            result['errors'].append(error_msg)
            print(f"  ❌ {error_msg}")

        return result

    def test_coordination_integration(self) -> Dict[str, Any]:
        """Test AI integration with Coordination module."""
        print("Testing Coordination Integration...")

        result = {
            'model_access': False,
            'partner_matching': False,
            'collaboration_analysis': False,
            'resource_optimization': False,
            'errors': []
        }

        try:
            # Test model access
            try:
                from coordination.models import Organization

                count = Organization.objects.count()
                result['model_access'] = True

                if self.verbose:
                    print(f"  ✓ Coordination model accessible: {count} organizations")

            except Exception as model_error:
                result['errors'].append(f"Coordination model access failed: {str(model_error)}")
                print(f"  ❌ Coordination model access failed: {model_error}")
                return result

            # Test partner matching
            try:
                from ai_assistant.services import GeminiService

                gemini = GeminiService()

                community_needs = """
                Community: Coastal fishing village in Sulu
                Needs:
                - Education support for children
                - Healthcare services
                - Livelihood diversification
                - Infrastructure development

                Available Partners:
                - NGO A: Education programs (working in nearby province)
                - NGO B: Health services (limited capacity)
                - NGO C: Livelihood training (agriculture focus)
                - LGU: Infrastructure projects (budget constraints)
                """

                response = gemini.generate_text(
                    f"Analyze and recommend the best partner organizations for this community based on their needs and available partners:\n{community_needs}"
                )

                if response.get('success'):
                    result['partner_matching'] = True

                    if self.verbose:
                        print("  ✓ AI partner matching working")
                else:
                    result['errors'].append("Partner matching failed")

            except Exception as matching_error:
                result['errors'].append(f"Partner matching failed: {str(matching_error)}")
                print(f"  ❌ Partner matching failed: {matching_error}")

            # Test collaboration analysis
            try:
                response = gemini.generate_text(
                    f"Analyze potential collaboration opportunities between the listed partners for maximum impact in addressing the community needs:\n{community_needs}"
                )

                if response.get('success'):
                    result['collaboration_analysis'] = True

                    if self.verbose:
                        print("  ✓ AI collaboration analysis working")
                else:
                    result['errors'].append("Collaboration analysis failed")

            except Exception as collab_error:
                result['errors'].append(f"Collaboration analysis failed: {str(collab_error)}")
                print(f"  ❌ Collaboration analysis failed: {collab_error}")

            # Test resource optimization
            try:
                response = gemini.generate_text(
                    f"Optimize resource allocation among the partners to address community needs most effectively:\n{community_needs}"
                )

                if response.get('success'):
                    result['resource_optimization'] = True

                    if self.verbose:
                        print("  ✓ AI resource optimization working")
                else:
                    result['errors'].append("Resource optimization failed")

            except Exception as opt_error:
                result['errors'].append(f"Resource optimization failed: {str(opt_error)}")
                print(f"  ❌ Resource optimization failed: {opt_error}")

        except Exception as e:
            error_msg = f"Coordination integration test failed: {str(e)}"
            result['errors'].append(error_msg)
            print(f"  ❌ {error_msg}")

        return result

    def generate_recommendations(self):
        """Generate recommendations based on test results."""
        print("💡 GENERATING RECOMMENDATIONS")
        print("-" * 50)

        recommendations = []

        # Check AI Assistant Services
        ai_results = self.test_results.get('ai_assistant_services', {})

        # EmbeddingService recommendations
        embedding_result = ai_results.get('embedding_service', {})
        if not embedding_result.get('available'):
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Dependencies',
                'issue': 'EmbeddingService not available',
                'recommendation': 'Install sentence-transformers library: pip install sentence-transformers',
                'impact': 'No semantic search capabilities'
            })
        elif not embedding_result.get('model_loaded'):
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Configuration',
                'issue': 'Embedding model failed to load',
                'recommendation': 'Check internet connection and model download permissions',
                'impact': 'Core AI functionality unavailable'
            })

        # VectorStore recommendations
        vector_result = ai_results.get('vector_store', {})
        if not vector_result.get('available'):
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Dependencies',
                'issue': 'VectorStore not available',
                'recommendation': 'Install FAISS library: pip install faiss-cpu',
                'impact': 'No vector similarity search'
            })

        # GeminiService recommendations
        gemini_result = ai_results.get('gemini_service', {})
        if not gemini_result.get('available'):
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Configuration',
                'issue': 'GeminiService not available',
                'recommendation': 'Configure GOOGLE_API_KEY in environment variables',
                'impact': 'No AI text generation capabilities'
            })
        elif not gemini_result.get('text_generation'):
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Configuration',
                'issue': 'Gemini API calls failing',
                'recommendation': 'Check API key validity and network connectivity',
                'impact': 'AI chat and analysis features unavailable'
            })

        # Check Common AI Services
        common_results = self.test_results.get('common_ai_services', {})

        # UnifiedSearchEngine recommendations
        unified_result = common_results.get('unified_search_engine', {})
        if not unified_result.get('available'):
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Dependencies',
                'issue': 'UnifiedSearchEngine not available',
                'recommendation': 'Ensure all AI assistant services are properly installed',
                'impact': 'No cross-module semantic search'
            })

        # Performance recommendations
        perf_results = self.test_results.get('performance_metrics', {})

        # Embedding performance
        embedding_perf = perf_results.get('embedding_performance', {})
        if embedding_perf.get('single_embedding'):
            for length, metrics in embedding_perf['single_embedding'].items():
                if metrics['avg_time'] > 1.0:  # More than 1 second
                    recommendations.append({
                        'priority': 'MEDIUM',
                        'category': 'Performance',
                        'issue': f'Slow embedding generation for {length}',
                        'recommendation': 'Consider caching embeddings or using GPU acceleration',
                        'impact': 'Poor user experience for search features'
                    })

        # Memory usage recommendations
        memory_results = perf_results.get('memory_usage', {})
        if memory_results.get('embedding_service', {}).get('model_overhead_mb', 0) > 500:
            recommendations.append({
                'priority': 'LOW',
                'category': 'Performance',
                'issue': 'High memory usage for embedding model',
                'recommendation': 'Consider using a smaller model or model quantization',
                'impact': 'Higher server memory requirements'
            })

        # Integration recommendations
        integration_results = self.test_results.get('integration_status', {})

        for module, results in integration_results.items():
            if not results.get('model_access'):
                recommendations.append({
                    'priority': 'HIGH',
                    'category': 'Integration',
                    'issue': f'{module} model access failed',
                    'recommendation': f'Check database migrations for {module} module',
                    'impact': f'AI features unavailable for {module}'
                })

        # Data indexing recommendations
        similarity_result = ai_results.get('similarity_search', {})
        if similarity_result.get('service_initialization') and not similarity_result.get('community_search'):
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Data',
                'issue': 'No indexed data found for semantic search',
                'recommendation': 'Run indexing commands to populate vector stores with existing data',
                'impact': 'Semantic search returns empty results'
            })

        # Add general recommendations
        recommendations.extend([
            {
                'priority': 'LOW',
                'category': 'Monitoring',
                'issue': 'No AI service monitoring',
                'recommendation': 'Implement logging and monitoring for AI service health',
                'impact': 'Difficult to detect AI service failures'
            },
            {
                'priority': 'MEDIUM',
                'category': 'Testing',
                'issue': 'Limited automated testing for AI features',
                'recommendation': 'Create unit tests for AI service integration',
                'impact': 'Risk of regressions in AI functionality'
            },
            {
                'priority': 'LOW',
                'category': 'Documentation',
                'issue': 'AI features may lack user documentation',
                'recommendation': 'Create user guides for AI-powered features',
                'impact': 'Users may not utilize AI capabilities effectively'
            }
        ])

        # Sort by priority
        priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))

        self.test_results['recommendations'] = recommendations

        # Print recommendations
        for rec in recommendations:
            priority_icon = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(rec['priority'], '⚪')
            print(f"{priority_icon} {rec['priority']} PRIORITY - {rec['category']}")
            print(f"   Issue: {rec['issue']}")
            print(f"   Recommendation: {rec['recommendation']}")
            print(f"   Impact: {rec['impact']}")
            print()

    def save_report(self, filename: str = None):
        """Save test results to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_services_test_report_{timestamp}.json"

        try:
            with open(filename, 'w') as f:
                json.dump(self.test_results, f, indent=2, default=str)

            print(f"📄 Test report saved to: {filename}")
            return filename

        except Exception as e:
            print(f"❌ Failed to save report: {str(e)}")
            return None

    def print_summary(self):
        """Print test summary."""
        print("=" * 80)
        print("AI SERVICES INTEGRATION TEST SUMMARY")
        print("=" * 80)

        # AI Assistant Services Summary
        ai_results = self.test_results.get('ai_assistant_services', {})
        print("\n🔧 AI ASSISTANT SERVICES")

        services = [
            ('EmbeddingService', ai_results.get('embedding_service', {})),
            ('VectorStore', ai_results.get('vector_store', {})),
            ('SimilaritySearch', ai_results.get('similarity_search', {})),
            ('GeminiService', ai_results.get('gemini_service', {}))
        ]

        for name, result in services:
            status = "✅ AVAILABLE" if result.get('available') else "❌ UNAVAILABLE"
            errors = len(result.get('errors', []))
            if errors > 0:
                status += f" ({errors} errors)"
            print(f"  {name}: {status}")

        # Common AI Services Summary
        common_results = self.test_results.get('common_ai_services', {})
        print("\n🤖 COMMON AI SERVICES")

        services = [
            ('UnifiedSearchEngine', common_results.get('unified_search_engine', {})),
            ('QueryParser', common_results.get('query_parser', {})),
            ('TemplateMatcher', common_results.get('template_matcher', {}))
        ]

        for name, result in services:
            status = "✅ AVAILABLE" if result.get('available') else "❌ UNAVAILABLE"
            errors = len(result.get('errors', []))
            if errors > 0:
                status += f" ({errors} errors)"
            print(f"  {name}: {status}")

        # AI Features Summary
        ai_features = self.test_results.get('ai_features', {})
        print("\n✨ AI-POWERED FEATURES")

        features = [
            ('Semantic Search', ai_features.get('semantic_search', {})),
            ('Intelligent Recommendations', ai_features.get('intelligent_recommendations', {})),
            ('Natural Language Processing', ai_features.get('natural_language_processing', {}))
        ]

        for name, result in features:
            status = "✅ WORKING" if result.get('available') else "❌ NOT WORKING"
            print(f"  {name}: {status}")

        # Integration Summary
        integration = self.test_results.get('integration_status', {})
        print("\n🔗 MODULE INTEGRATION")

        modules = [
            ('Communities', integration.get('communities_integration', {})),
            ('MANA', integration.get('mana_integration', {})),
            ('Policies', integration.get('policies_integration', {})),
            ('Coordination', integration.get('coordination_integration', {}))
        ]

        for name, result in modules:
            status = "✅ INTEGRATED" if result.get('model_access') else "❌ NOT INTEGRATED"
            features = sum([
                result.get('search_integration', False),
                result.get('ai_features', False),
                result.get('assessment_analysis', False),
                result.get('policy_analysis', False),
                result.get('partner_matching', False)
            ])
            if features > 0:
                status += f" ({features} AI features)"
            print(f"  {name}: {status}")

        # Recommendations Summary
        recommendations = self.test_results.get('recommendations', [])
        print(f"\n💡 RECOMMENDATIONS")
        print(f"  Total: {len(recommendations)}")

        high_priority = sum(1 for r in recommendations if r.get('priority') == 'HIGH')
        medium_priority = sum(1 for r in recommendations if r.get('priority') == 'MEDIUM')
        low_priority = sum(1 for r in recommendations if r.get('priority') == 'LOW')

        if high_priority > 0:
            print(f"  🔴 High Priority: {high_priority}")
        if medium_priority > 0:
            print(f"  🟡 Medium Priority: {medium_priority}")
        if low_priority > 0:
            print(f"  🟢 Low Priority: {low_priority}")

        # Overall Status
        total_errors = sum(
            len(result.get('errors', []))
            for category_results in [
                ai_results.values(),
                common_results.values(),
                ai_features.values(),
                integration.values()
            ]
            for result in category_results
        )

        print(f"\n📊 OVERALL STATUS")
        if total_errors == 0:
            print("  🟢 All AI services working correctly")
        elif total_errors <= 5:
            print("  🟡 Minor issues detected")
        elif total_errors <= 10:
            print("  🟠 Several issues need attention")
        else:
            print("  🔴 Major issues detected")

        print(f"  Total errors: {total_errors}")
        print("=" * 80)


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description='Test OBCMS/BMMS AI Services Integration')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--save-report', '-s', action='store_true', help='Save report to JSON file')
    parser.add_argument('--output', '-o', type=str, help='Output filename for report')

    args = parser.parse_args()

    # Run tests
    tester = AIServicesIntegrationTester(verbose=args.verbose)
    results = tester.run_all_tests()

    # Print summary
    tester.print_summary()

    # Save report if requested
    if args.save_report:
        filename = args.output if args.output else None
        tester.save_report(filename)

    return results


if __name__ == '__main__':
    main()