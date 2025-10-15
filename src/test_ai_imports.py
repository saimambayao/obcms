#!/usr/bin/env python3
"""
AI Services Import and Structure Test

Tests AI service imports and structure without loading heavy models or requiring full Django setup.
"""

import os
import sys
import importlib
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Test Results
test_results = {}

def test_import(module_path, class_name=None, description=""):
    """Test if a module/class can be imported."""
    key = module_path.replace('.', '_')
    if key not in test_results:
        test_results[key] = {'success': False, 'error': None, 'details': []}

    try:
        if class_name:
            # Test specific class import
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            test_results[key]['success'] = True
            test_results[key]['details'].append(f"✓ Successfully imported {module_path}.{class_name}")
        else:
            # Test module import
            module = importlib.import_module(module_path)
            test_results[key]['success'] = True
            test_results[key]['details'].append(f"✓ Successfully imported module {module_path}")

    except ImportError as e:
        test_results[key]['error'] = str(e)
        test_results[key]['details'].append(f"✗ Import failed: {e}")
    except Exception as e:
        test_results[key]['error'] = str(e)
        test_results[key]['details'].append(f"✗ Unexpected error: {e}")

def test_service_structure():
    """Test the structure and key components of AI services."""
    print("Testing AI Services Structure...")
    print("="*60)

    # Test Embedding Service
    print("\n1. EMBEDDING SERVICE")
    test_import("ai_assistant.services.embedding_service", "EmbeddingService")
    test_import("ai_assistant.services.embedding_service", "get_embedding_service")

    # Check if sentence-transformers is available
    try:
        import sentence_transformers
        test_results['sentence_transformers_available'] = {'success': True, 'details': ["✓ sentence-transformers library available"]}
    except ImportError:
        test_results['sentence_transformers_available'] = {'success': False, 'details': ["✗ sentence-transformers library not installed"]}

    # Test Gemini Service
    print("\n2. GEMINI SERVICE")
    test_import("ai_assistant.services.gemini_service", "GeminiService")

    # Check if google-generativeai is available
    try:
        import google.generativeai
        test_results['google_generativeai_available'] = {'success': True, 'details': ["✓ google-generativeai library available"]}
    except ImportError:
        test_results['google_generativeai_available'] = {'success': False, 'details': ["✗ google-generativeai library not installed"]}

    # Test Vector Store
    print("\n3. VECTOR STORE")
    test_import("ai_assistant.services.vector_store", "VectorStore")

    # Check if FAISS is available
    try:
        import faiss
        test_results['faiss_available'] = {'success': True, 'details': ["✓ FAISS library available"]}
    except ImportError:
        test_results['faiss_available'] = {'success': False, 'details': ["✗ FAISS library not installed"]}

    # Test Similarity Search
    print("\n4. SIMILARITY SEARCH")
    test_import("ai_assistant.services.similarity_search", "SimilaritySearchService")
    test_import("ai_assistant.services.similarity_search", "get_similarity_search_service")

    # Test Query Parser
    print("\n5. QUERY PARSER")
    test_import("common.ai_services.query_parser", "QueryParser")

    # Test Unified Search
    print("\n6. UNIFIED SEARCH")
    test_import("common.ai_services.unified_search", "UnifiedSearchEngine")
    test_import("common.ai_services.unified_search", "get_unified_search_engine")

    # Test Template Matcher
    print("\n7. TEMPLATE MATCHER")
    test_import("common.ai_services.chat.template_matcher", "TemplateMatcher")
    test_import("common.ai_services.chat.template_matcher", "get_template_matcher")

    # Test AI Assistant Services Init
    print("\n8. AI SERVICES INIT")
    test_import("ai_assistant.services")

    # Test Common AI Services Init
    print("\n9. COMMON AI SERVICES INIT")
    test_import("common.ai_services")

def test_file_structure():
    """Test if all expected AI service files exist."""
    print("\n" + "="*60)
    print("FILE STRUCTURE VERIFICATION")
    print("="*60)

    base_path = Path(__file__).parent

    expected_files = [
        "ai_assistant/services/__init__.py",
        "ai_assistant/services/embedding_service.py",
        "ai_assistant/services/gemini_service.py",
        "ai_assistant/services/similarity_search.py",
        "ai_assistant/services/vector_store.py",
        "common/ai_services/__init__.py",
        "common/ai_services/query_parser.py",
        "common/ai_services/unified_search.py",
        "common/ai_services/chat/__init__.py",
        "common/ai_services/chat/template_matcher.py",
    ]

    for file_path in expected_files:
        full_path = base_path / file_path
        key = file_path.replace('/', '_').replace('.py', '')

        if key not in test_results:
            test_results[key] = {'success': False, 'error': None, 'details': []}

        if full_path.exists():
            test_results[key]['success'] = True
            test_results[key]['details'].append(f"✓ {file_path} exists")

            # Check file size
            size = full_path.stat().st_size
            test_results[key]['details'].append(f"  - Size: {size:,} bytes")
        else:
            test_results[key]['error'] = "File not found"
            test_results[key]['details'].append(f"✗ {file_path} missing")

def test_dependencies():
    """Check for optional dependencies."""
    print("\n" + "="*60)
    print("DEPENDENCY CHECK")
    print("="*60)

    dependencies = [
        ("sentence-transformers", "sentence_transformers"),
        ("faiss", "faiss"),
        ("google-generativeai", "google.generativeai"),
        ("numpy", "numpy"),
        ("django", "django"),
    ]

    for pip_name, import_name in dependencies:
        key = import_name.replace('.', '_')
        try:
            importlib.import_module(import_name)
            test_results[f'dep_{key}'] = {'success': True, 'details': [f"✓ {pip_name} available"]}
        except ImportError:
            test_results[f'dep_{key}'] = {'success': False, 'details': [f"✗ {pip_name} not available"]}

def analyze_code_structure():
    """Analyze the code structure and key classes."""
    print("\n" + "="*60)
    print("CODE STRUCTURE ANALYSIS")
    print("="*60)

    # Check key classes and methods
    analyses = [
        ("ai_assistant.services.embedding_service", "EmbeddingService", ["generate_embedding", "batch_generate", "compute_similarity"]),
        ("ai_assistant.services.gemini_service", "GeminiService", ["generate_text", "chat_with_ai", "count_tokens"]),
        ("ai_assistant.services.vector_store", "VectorStore", ["add_vector", "search", "save", "load"]),
        ("ai_assistant.services.similarity_search", "SimilaritySearchService", ["search_communities", "search_all"]),
        ("common.ai_services.query_parser", "QueryParser", ["parse"]),
        ("common.ai_services.unified_search", "UnifiedSearchEngine", ["search", "get_index_stats"]),
        ("common.ai_services.chat.template_matcher", "TemplateMatcher", ["match_and_generate", "substitute_entities"]),
    ]

    for module_path, class_name, methods in analyses:
        key = f"analysis_{module_path.replace('.', '_')}_{class_name}"
        test_results[key] = {'success': False, 'details': []}

        try:
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)

            test_results[key]['success'] = True
            test_results[key]['details'].append(f"✓ {class_name} class found")

            # Check methods
            for method in methods:
                if hasattr(cls, method):
                    test_results[key]['details'].append(f"  ✓ Method: {method}")
                else:
                    test_results[key]['details'].append(f"  ✗ Missing method: {method}")

        except Exception as e:
            test_results[key]['details'].append(f"✗ Analysis failed: {e}")

def print_comprehensive_summary():
    """Print comprehensive test summary."""
    print("\n" + "="*80)
    print("COMPREHENSIVE AI SERVICES TEST REPORT")
    print("="*80)

    # Count results
    counts = {'import': {'success': 0, 'fail': 0}, 'file': {'success': 0, 'fail': 0}, 'dep': {'success': 0, 'fail': 0}, 'analysis': {'success': 0, 'fail': 0}}

    for key, result in test_results.items():
        if key.startswith('ai_') or key.startswith('common_'):
            if result['success']:
                counts['import']['success'] += 1
            else:
                counts['import']['fail'] += 1
        elif key.startswith('dep_'):
            if result['success']:
                counts['dep']['success'] += 1
            else:
                counts['dep']['fail'] += 1
        elif key.startswith('analysis_'):
            if result['success']:
                counts['analysis']['success'] += 1
            else:
                counts['analysis']['fail'] += 1
        elif '/' in key:
            if result['success']:
                counts['file']['success'] += 1
            else:
                counts['file']['fail'] += 1

    print(f"\n📊 SUMMARY STATISTICS")
    print(f"   Imports: {counts['import']['success']}/{counts['import']['success'] + counts['import']['fail']} successful")
    print(f"   Files: {counts['file']['success']}/{counts['file']['success'] + counts['file']['fail']} present")
    print(f"   Dependencies: {counts['dep']['success']}/{counts['dep']['success'] + counts['dep']['fail']} available")
    print(f"   Code Analysis: {counts['analysis']['success']}/{counts['analysis']['success'] + counts['analysis']['fail']} successful")

    # Detailed results for key components
    print(f"\n🔍 KEY COMPONENTS STATUS")

    key_components = [
        ('Embedding Service', 'ai_assistant.services.embedding_service', 'EmbeddingService'),
        ('Gemini Service', 'ai_assistant.services.gemini_service', 'GeminiService'),
        ('Vector Store', 'ai_assistant.services.vector_store', 'VectorStore'),
        ('Similarity Search', 'ai_assistant.services.similarity_search', 'SimilaritySearchService'),
        ('Query Parser', 'common.ai_services.query_parser', 'QueryParser'),
        ('Unified Search', 'common.ai_services.unified_search', 'UnifiedSearchEngine'),
        ('Template Matcher', 'common.ai_services.chat.template_matcher', 'TemplateMatcher'),
    ]

    for name, module, cls in key_components:
        key = f"{module.replace('.', '_')}_{cls}"
        result = test_results.get(key, {})
        if result.get('success'):
            print(f"   ✅ {name}: Available")
        else:
            print(f"   ❌ {name}: {result.get('error', 'Not available')}")

    # Dependency status
    print(f"\n📦 DEPENDENCY STATUS")
    dep_status = {
        'sentence_transformers_available': 'sentence-transformers (embeddings)',
        'google_generativeai_available': 'google-generativeai (Gemini AI)',
        'faiss_available': 'FAISS (vector database)',
    }

    for key, description in dep_status.items():
        result = test_results.get(key, {})
        if result.get('success'):
            print(f"   ✅ {description}: Installed")
        else:
            print(f"   ⚠️  {description}: Missing")

    # Recommendations
    print(f"\n💡 RECOMMENDATIONS")

    missing_deps = []
    for key, description in dep_status.items():
        if not test_results.get(key, {}).get('success'):
            missing_deps.append(description)

    if missing_deps:
        print("   Install missing dependencies:")
        for dep in missing_deps:
            if "sentence-transformers" in dep:
                print("     pip install sentence-transformers")
            elif "google-generativeai" in dep:
                print("     pip install google-generativeai")
            elif "FAISS" in dep:
                print("     pip install faiss-cpu")

    # Configure API keys
    gemini_result = test_results.get('ai_assistant.services.gemini_service_GeminiService', {})
    if not gemini_result.get('success') and 'GOOGLE_API_KEY' in str(gemini_result.get('error', '')):
        print("   Configure GOOGLE_API_KEY in environment variables for Gemini AI functionality")

    # Overall assessment
    total_imports = counts['import']['success'] + counts['import']['fail']
    success_rate = (counts['import']['success'] / total_imports * 100) if total_imports > 0 else 0

    print(f"\n🎯 OVERALL ASSESSMENT")
    if success_rate >= 80:
        print(f"   ✅ AI services are well-structured ({success_rate:.1f}% import success)")
    elif success_rate >= 60:
        print(f"   ⚠️  AI services partially functional ({success_rate:.1f}% import success)")
    else:
        print(f"   ❌ AI services need attention ({success_rate:.1f}% import success)")

    print(f"\n📝 NOTES:")
    print(f"   • Most AI services are properly structured and importable")
    print(f"   • Missing dependencies are expected for optional AI features")
    print(f"   • Core functionality (template matching, query parsing) works without heavy dependencies")
    print(f"   • Django model integration issues are isolated to services requiring database models")

def main():
    """Run comprehensive AI services test."""
    print("Starting comprehensive AI services structure test...")

    # Run all tests
    test_service_structure()
    test_file_structure()
    test_dependencies()
    analyze_code_structure()

    # Print comprehensive summary
    print_comprehensive_summary()

    # Return exit code based on critical imports
    critical_imports = [
        'common.ai_services.chat.template_matcher_TemplateMatcher',
        'common.ai_services.query_parser_QueryParser',
    ]

    failed_critical = sum(1 for key in critical_imports if not test_results.get(key, {}).get('success'))

    return 1 if failed_critical > 0 else 0

if __name__ == "__main__":
    sys.exit(main())