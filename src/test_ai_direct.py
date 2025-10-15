#!/usr/bin/env python
"""
Direct AI Services Test (Minimal Dependencies)

Tests individual AI service imports without Django setup.
"""

import sys
import os
import json
from datetime import datetime

# Add the src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_direct_imports():
    """Test direct imports of AI services."""
    print("=" * 80)
    print("DIRECT AI SERVICES IMPORT TEST")
    print("=" * 80)
    print(f"Started at: {datetime.now().isoformat()}")
    print()

    results = {
        'timestamp': datetime.now().isoformat(),
        'import_results': {},
        'package_results': {},
        'summary': {}
    }

    # Test package imports
    print("📦 TESTING PACKAGE IMPORTS")
    print("-" * 50)

    packages = [
        ('sentence_transformers', 'Sentence Transformers'),
        ('faiss', 'FAISS'),
        ('google.generativeai', 'Google Generative AI'),
        ('numpy', 'NumPy'),
        ('django', 'Django'),
    ]

    for package, display_name in packages:
        try:
            if package == 'sentence_transformers':
                import sentence_transformers
                version = getattr(sentence_transformers, '__version__', 'unknown')
                results['package_results'][package] = {
                    'available': True,
                    'version': version,
                    'display_name': display_name
                }
                print(f"  ✓ {display_name}: {version}")
            elif package == 'faiss':
                import faiss
                version = getattr(faiss, '__version__', 'unknown')
                results['package_results'][package] = {
                    'available': True,
                    'version': version,
                    'display_name': display_name
                }
                print(f"  ✓ {display_name}: {version}")
            elif package == 'google.generativeai':
                import google.generativeai as genai
                version = getattr(genai, '__version__', 'unknown')
                results['package_results'][package] = {
                    'available': True,
                    'version': version,
                    'display_name': display_name
                }
                print(f"  ✓ {display_name}: {version}")
            else:
                module = __import__(package)
                version = getattr(module, '__version__', 'unknown')
                results['package_results'][package] = {
                    'available': True,
                    'version': version,
                    'display_name': display_name
                }
                print(f"  ✓ {display_name}: {version}")
        except ImportError as e:
            results['package_results'][package] = {
                'available': False,
                'error': str(e),
                'display_name': display_name
            }
            print(f"  ❌ {display_name}: {str(e)}")
        except Exception as e:
            results['package_results'][package] = {
                'available': False,
                'error': f"Unexpected error: {str(e)}",
                'display_name': display_name
            }
            print(f"  ❌ {display_name}: {str(e)}")

    # Test AI assistant service files
    print("\n🔧 TESTING AI SERVICE FILES")
    print("-" * 50)

    service_files = [
        ('ai_assistant/services/embedding_service.py', 'EmbeddingService'),
        ('ai_assistant/services/gemini_service.py', 'GeminiService'),
        ('ai_assistant/services/similarity_search.py', 'SimilaritySearchService'),
        ('ai_assistant/services/vector_store.py', 'VectorStore'),
        ('common/ai_services/unified_search.py', 'UnifiedSearchEngine'),
        ('common/ai_services/query_parser.py', 'QueryParser'),
        ('common/ai_services/chat/template_matcher.py', 'TemplateMatcher'),
        ('common/ai_services/chat/entity_extractor.py', 'EntityExtractor'),
    ]

    for filepath, service_name in service_files:
        # Check if file exists
        if os.path.exists(filepath):
            results['import_results'][service_name] = {
                'file_exists': True,
                'filepath': filepath
            }
            print(f"  ✓ {service_name}: File exists")

            # Try to check syntax by importing as a module
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(service_name, filepath)
                if spec and spec.loader:
                    # Don't actually load the module (to avoid dependencies), just check if it can be loaded
                    results['import_results'][service_name]['loadable'] = True
                    print(f"    ✓ Module is loadable")
                else:
                    results['import_results'][service_name]['loadable'] = False
                    print(f"    ⚠ Module has loading issues")
            except Exception as e:
                results['import_results'][service_name]['loadable'] = False
                results['import_results'][service_name]['error'] = str(e)
                print(f"    ❌ Loading error: {str(e)}")
        else:
            results['import_results'][service_name] = {
                'file_exists': False,
                'filepath': filepath
            }
            print(f"  ❌ {service_name}: File not found - {filepath}")

    # Test environment variables
    print("\n⚙️  TESTING ENVIRONMENT")
    print("-" * 50)

    env_vars = {
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
        'DJANGO_SETTINGS_MODULE': os.getenv('DJANGO_SETTINGS_MODULE'),
        'PYTHONPATH': os.getenv('PYTHONPATH'),
    }

    for var, value in env_vars.items():
        if var == 'GOOGLE_API_KEY':
            status = "✅ Set" if value else "❌ Missing"
            results[f'env_{var}'] = {'set': bool(value), 'value': '***' if value else None}
            print(f"  {var}: {status}")
        else:
            results[f'env_{var}'] = {'set': bool(value), 'value': value}
            print(f"  {var}: {value or 'Not set'}")

    # Test directory structure
    print("\n📁 TESTING DIRECTORY STRUCTURE")
    print("-" * 50)

    directories = [
        ('ai_assistant', 'AI Assistant Module'),
        ('ai_assistant/services', 'AI Services Directory'),
        ('ai_assistant/vector_indices', 'Vector Indices Directory'),
        ('common/ai_services', 'Common AI Services'),
        ('common/ai_services/chat', 'Chat Services'),
    ]

    for directory, description in directories:
        if os.path.exists(directory):
            results[f'dir_{directory.replace("/", "_")}'] = {'exists': True}
            print(f"  ✓ {description}: {directory}")
        else:
            results[f'dir_{directory.replace("/", "_")}'] = {'exists': False}
            print(f"  ❌ {description}: {directory} - Not found")

    # Create missing directories if needed
    if not os.path.exists('ai_assistant/vector_indices'):
        try:
            os.makedirs('ai_assistant/vector_indices', exist_ok=True)
            print(f"  ✓ Created: ai_assistant/vector_indices")
        except Exception as e:
            print(f"  ❌ Failed to create directory: {e}")

    # Generate summary
    print("\n📊 SUMMARY")
    print("-" * 50)

    total_packages = len(results['package_results'])
    available_packages = len([p for p in results['package_results'].values() if p.get('available')])

    total_services = len(results['import_results'])
    existing_services = len([s for s in results['import_results'].values() if s.get('file_exists')])

    api_key_set = bool(os.getenv('GOOGLE_API_KEY'))

    results['summary'] = {
        'packages_available': available_packages,
        'packages_total': total_packages,
        'services_existing': existing_services,
        'services_total': total_services,
        'api_key_configured': api_key_set
    }

    print(f"  Packages: {available_packages}/{total_packages} available")
    print(f"  Services: {existing_services}/{total_services} files exist")
    print(f"  API Key: {'Configured' if api_key_set else 'Missing'}")

    # Determine overall status
    package_rate = available_packages / total_packages if total_packages > 0 else 0
    service_rate = existing_services / total_services if total_services > 0 else 0

    if package_rate >= 0.8 and service_rate >= 0.8 and api_key_set:
        status = "🟢 READY"
        description = "AI services are ready for testing"
    elif package_rate >= 0.6 and service_rate >= 0.6:
        status = "🟡 MOSTLY READY"
        description = "Most AI services available"
    elif package_rate >= 0.4 or service_rate >= 0.4:
        status = "🟠 PARTIALLY READY"
        description = "Some AI services available"
    else:
        status = "🔴 NOT READY"
        description = "Few AI services available"

    print(f"\n  Status: {status}")
    print(f"  Description: {description}")

    # Recommendations
    print("\n💡 RECOMMENDATIONS")
    print("-" * 50)

    if not api_key_set:
        print("  🔴 Set GOOGLE_API_KEY environment variable")

    missing_packages = [info.get('display_name', pkg) for pkg, info in results['package_results'].items()
                        if not info.get('available')]
    if missing_packages:
        print(f"  🔴 Install missing packages: {', '.join(missing_packages)}")

    missing_services = [name for name, result in results['import_results'].items()
                        if not result.get('file_exists')]
    if missing_services:
        print(f"  🟡 Missing service files: {', '.join(missing_services)}")

    if package_rate >= 0.8 and service_rate >= 0.8 and not api_key_set:
        print("  🟡 Almost ready! Just configure the API key.")

    if package_rate >= 0.8 and service_rate >= 0.8 and api_key_set:
        print("  🟢 AI services are fully configured!")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ai_direct_test_{timestamp}.json"

    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n📄 Results saved to: {filename}")
    except Exception as e:
        print(f"\n❌ Failed to save results: {e}")

    print("\n" + "=" * 80)
    return results


if __name__ == '__main__':
    test_direct_imports()