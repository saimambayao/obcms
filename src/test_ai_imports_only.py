#!/usr/bin/env python
"""
AI Services Import and Configuration Test Only

Tests imports and basic configuration without service initialization.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.development')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Reduce logging to avoid noise

def test_ai_services_imports():
    """Test AI services imports only."""
    print("=" * 80)
    print("OBCMS/BMMS AI SERVICES IMPORT TEST")
    print("=" * 80)
    print(f"Started at: {datetime.now().isoformat()}")
    print()

    results = {
        'timestamp': datetime.now().isoformat(),
        'imports': {},
        'configuration': {},
        'dependencies': {},
        'overall_status': {}
    }

    # Test imports
    print("📦 TESTING IMPORTS")
    print("-" * 50)

    import_tests = [
        ('EmbeddingService', 'ai_assistant.services.embedding_service', 'EmbeddingService'),
        ('GeminiService', 'ai_assistant.services.gemini_service', 'GeminiService'),
        ('SimilaritySearchService', 'ai_assistant.services.similarity_search', 'SimilaritySearchService'),
        ('VectorStore', 'ai_assistant.services.vector_store', 'VectorStore'),
        ('CacheService', 'ai_assistant.services.cache_service', 'CacheService'),
        ('PromptTemplates', 'ai_assistant.services.prompt_templates', 'PromptTemplates'),
    ]

    for name, module, class_name in import_tests:
        try:
            module_imported = __import__(module, fromlist=[class_name])
            service_class = getattr(module_imported, class_name)
            results['imports'][name] = {
                'imported': True,
                'available': True,
                'class_name': class_name,
                'module_path': module
            }
            print(f"  ✓ {name}: Imported successfully")
        except ImportError as e:
            results['imports'][name] = {
                'imported': False,
                'available': False,
                'error': str(e),
                'class_name': class_name,
                'module_path': module
            }
            print(f"  ❌ {name}: Import failed - {str(e)}")
        except Exception as e:
            results['imports'][name] = {
                'imported': False,
                'available': False,
                'error': f"Unexpected error: {str(e)}",
                'class_name': class_name,
                'module_path': module
            }
            print(f"  ❌ {name}: Unexpected error - {str(e)}")

    # Test Common AI Services imports
    print("\nTesting Common AI Services imports...")

    common_import_tests = [
        ('UnifiedSearchEngine', 'common.ai_services.unified_search', 'UnifiedSearchEngine'),
        ('QueryParser', 'common.ai_services.query_parser', 'QueryParser'),
        ('TemplateMatcher', 'common.ai_services.chat.template_matcher', 'get_template_matcher'),
        ('EntityExtractor', 'common.ai_services.chat.entity_extractor', 'EntityExtractor'),
        ('HAS_UNIFIED_SEARCH', 'common.ai_services', 'HAS_UNIFIED_SEARCH'),
        ('HAS_CHAT', 'common.ai_services', 'HAS_CHAT'),
    ]

    for name, module, import_name in common_import_tests:
        try:
            module_imported = __import__(module, fromlist=[import_name])
            if name.startswith('HAS_'):
                service_available = getattr(module_imported, import_name)
                results['imports'][name] = {
                    'imported': True,
                    'available': service_available,
                    'type': 'flag'
                }
                print(f"  ✓ {name}: {service_available}")
            else:
                service_class = getattr(module_imported, import_name)
                results['imports'][name] = {
                    'imported': True,
                    'available': True,
                    'class_name': import_name,
                    'module_path': module
                }
                print(f"  ✓ {name}: Imported successfully")
        except ImportError as e:
            results['imports'][name] = {
                'imported': False,
                'available': False,
                'error': str(e),
                'module_path': module
            }
            print(f"  ❌ {name}: Import failed - {str(e)}")
        except Exception as e:
            results['imports'][name] = {
                'imported': False,
                'available': False,
                'error': f"Unexpected error: {str(e)}",
                'module_path': module
            }
            print(f"  ❌ {name}: Unexpected error - {str(e)}")

    # Test service availability flags
    print("\nTesting service availability flags...")
    try:
        from ai_assistant.services import (
            HAS_EMBEDDING_SERVICE,
            HAS_SIMILARITY_SEARCH,
            HAS_VECTOR_STORE
        )

        results['imports']['availability_flags'] = {
            'HAS_EMBEDDING_SERVICE': HAS_EMBEDDING_SERVICE,
            'HAS_SIMILARITY_SEARCH': HAS_SIMILARITY_SEARCH,
            'HAS_VECTOR_STORE': HAS_VECTOR_STORE
        }

        print(f"  HAS_EMBEDDING_SERVICE: {HAS_EMBEDDING_SERVICE}")
        print(f"  HAS_SIMILARITY_SEARCH: {HAS_SIMILARITY_SEARCH}")
        print(f"  HAS_VECTOR_STORE: {HAS_VECTOR_STORE}")
    except Exception as e:
        results['imports']['availability_flags'] = {'error': str(e)}
        print(f"  ❌ Availability flags test failed: {e}")

    # Test configuration
    print("\n⚙️  TESTING CONFIGURATION")
    print("-" * 50)

    from django.conf import settings

    ai_settings = {
        'GOOGLE_API_KEY': hasattr(settings, 'GOOGLE_API_KEY') and bool(getattr(settings, 'GOOGLE_API_KEY', None)),
        'AI_ENABLED': getattr(settings, 'AI_ENABLED', False),
        'AI_CACHE_TIMEOUT': getattr(settings, 'AI_CACHE_TIMEOUT', 3600),
        'AI_MAX_TOKENS': getattr(settings, 'AI_MAX_TOKENS', 4000),
    }

    results['configuration']['django_settings'] = ai_settings

    for setting, value in ai_settings.items():
        if setting == 'GOOGLE_API_KEY':
            status = "✅ Configured" if value else "❌ Missing"
            print(f"  {setting}: {status}")
        else:
            print(f"  {setting}: {value}")

    # Test environment variables
    print("\nTesting environment variables...")

    env_vars = {
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
        'DJANGO_SETTINGS_MODULE': os.getenv('DJANGO_SETTINGS_MODULE'),
    }

    results['configuration']['environment_variables'] = env_vars

    for var, value in env_vars.items():
        if var == 'GOOGLE_API_KEY':
            status = "✅ Set" if value else "❌ Missing"
            print(f"  {var}: {status}")
        else:
            print(f"  {var}: {value}")

    # Test file system permissions
    print("\nTesting file system permissions...")

    try:
        ai_indices_path = os.path.join(settings.BASE_DIR, 'ai_assistant', 'vector_indices')
        os.makedirs(ai_indices_path, exist_ok=True)

        test_file = os.path.join(ai_indices_path, 'test_write.tmp')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)

            results['configuration']['file_permissions'] = {
                'readable': True,
                'writable': True,
                'directory_exists': True,
                'path': ai_indices_path
            }
            print(f"  ✓ AI indices directory: {ai_indices_path}")
            print("  ✓ Read/write permissions: OK")
        except Exception as write_error:
            results['configuration']['file_permissions'] = {
                'readable': False,
                'writable': False,
                'error': str(write_error),
                'path': ai_indices_path
            }
            print(f"  ❌ Write permissions failed: {write_error}")
    except Exception as path_error:
        results['configuration']['file_permissions'] = {'error': str(path_error)}
        print(f"  ❌ Path creation failed: {path_error}")

    # Test dependencies
    print("\n📚 TESTING DEPENDENCIES")
    print("-" * 50)

    packages = [
        ('django', 'Django'),
        ('numpy', 'NumPy'),
        ('google.generativeai', 'Google Generative AI'),
        ('sentence_transformers', 'Sentence Transformers'),
        ('faiss', 'FAISS'),
    ]

    for package, display_name in packages:
        try:
            if package == 'sentence_transformers':
                import sentence_transformers
                version = getattr(sentence_transformers, '__version__', 'unknown')
                results['dependencies'][package] = {
                    'available': True,
                    'version': version,
                    'display_name': display_name
                }
                print(f"  ✓ {display_name}: {version}")
            elif package == 'faiss':
                import faiss
                version = getattr(faiss, '__version__', 'unknown')
                results['dependencies'][package] = {
                    'available': True,
                    'version': version,
                    'display_name': display_name
                }
                print(f"  ✓ {display_name}: {version}")
            elif package == 'google.generativeai':
                import google.generativeai as genai
                version = getattr(genai, '__version__', 'unknown')
                results['dependencies'][package] = {
                    'available': True,
                    'version': version,
                    'display_name': display_name
                }
                print(f"  ✓ {display_name}: {version}")
            else:
                module = __import__(package)
                version = getattr(module, '__version__', 'unknown')
                results['dependencies'][package] = {
                    'available': True,
                    'version': version,
                    'display_name': display_name
                }
                print(f"  ✓ {display_name}: {version}")
        except ImportError:
            results['dependencies'][package] = {
                'available': False,
                'display_name': display_name
            }
            print(f"  ❌ {display_name}: Not installed")

    # Calculate overall status
    print("\n📊 OVERALL STATUS")
    print("-" * 50)

    total_imports = len([k for k in results['imports'].keys() if not k.startswith('HAS_')])
    successful_imports = len([v for v in results['imports'].values() if v.get('imported')])

    api_key_configured = results['configuration']['django_settings'].get('GOOGLE_API_KEY', False)
    file_perms_ok = results['configuration']['file_permissions'].get('writable', False)

    total_deps = len(results['dependencies'])
    available_deps = len([v for v in results['dependencies'].values() if v.get('available')])

    results['overall_status'] = {
        'imports_success': successful_imports,
        'imports_total': total_imports,
        'api_key_configured': api_key_configured,
        'file_permissions_ok': file_perms_ok,
        'dependencies_available': available_deps,
        'dependencies_total': total_deps
    }

    print(f"  Imports: {successful_imports}/{total_imports} successful")
    print(f"  Dependencies: {available_deps}/{total_deps} available")
    print(f"  API Key: {'Configured' if api_key_configured else 'Missing'}")
    print(f"  File Permissions: {'OK' if file_perms_ok else 'Issue'}")

    # Generate status
    success_rate = successful_imports / total_imports if total_imports > 0 else 0
    dep_rate = available_deps / total_deps if total_deps > 0 else 0

    if success_rate >= 0.8 and dep_rate >= 0.8 and api_key_configured:
        status = "🟢 EXCELLENT"
        description = "Most AI services available and properly configured"
    elif success_rate >= 0.6 and dep_rate >= 0.6:
        status = "🟡 GOOD"
        description = "Most core AI services available"
    elif success_rate >= 0.4 and dep_rate >= 0.4:
        status = "🟠 FAIR"
        description = "Some AI services available"
    else:
        status = "🔴 POOR"
        description = "Few AI services available"

    print(f"\n  Status: {status}")
    print(f"  Description: {description}")

    # Generate recommendations
    print("\n💡 QUICK RECOMMENDATIONS")
    print("-" * 50)

    if not api_key_configured:
        print("  🔴 Set GOOGLE_API_KEY in environment variables or Django settings")

    missing_services = [name for name, result in results['imports'].items()
                       if not result.get('imported') and not name.startswith('HAS_')]
    if missing_services:
        print(f"  🟡 Install missing services: {', '.join(missing_services)}")

    missing_deps = [info.get('display_name', pkg) for pkg, info in results['dependencies'].items()
                   if not info.get('available')]
    if missing_deps:
        print(f"  🔴 Install missing dependencies: {', '.join(missing_deps)}")

    if not file_perms_ok:
        print("  🔴 Fix file permissions for ai_assistant/vector_indices directory")

    if success_rate >= 0.8 and dep_rate >= 0.8 and api_key_configured:
        print("  🟢 AI services are properly configured!")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ai_imports_test_results_{timestamp}.json"

    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n📄 Results saved to: {filename}")
    except Exception as e:
        print(f"\n❌ Failed to save results: {e}")

    print("\n" + "=" * 80)
    return results


if __name__ == '__main__':
    test_ai_services_imports()