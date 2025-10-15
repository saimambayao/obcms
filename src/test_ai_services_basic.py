#!/usr/bin/env python
"""
Basic AI Services Integration Test Script

Tests AI services availability and basic functionality without heavy model downloads.
Focuses on import testing and configuration validation.
"""

import os
import sys
import time
import json
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional

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

class BasicAIServicesTester:
    """Basic AI services availability and configuration tester."""

    def __init__(self, verbose: bool = False):
        """Initialize the tester."""
        self.verbose = verbose
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'import_tests': {},
            'configuration_tests': {},
            'basic_functionality': {},
            'dependency_status': {},
            'errors': [],
            'recommendations': []
        }

        print("=" * 80)
        print("OBCMS/BMMS AI SERVICES BASIC INTEGRATION TEST")
        print("=" * 80)
        print(f"Started at: {self.test_results['timestamp']}")
        print()

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all basic AI services tests."""
        try:
            # Test imports
            self.test_imports()

            # Test configuration
            self.test_configuration()

            # Test basic functionality
            self.test_basic_functionality()

            # Test dependencies
            self.test_dependencies()

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

    def test_imports(self):
        """Test AI services imports."""
        print("📦 TESTING AI SERVICES IMPORTS")
        print("-" * 50)

        results = {}

        # Test AI Assistant Services imports
        print("Testing AI Assistant Services imports...")

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
                results[name] = {
                    'imported': True,
                    'available': True,
                    'class_name': class_name,
                    'module_path': module
                }
                print(f"  ✓ {name}: Imported successfully")
            except ImportError as e:
                results[name] = {
                    'imported': False,
                    'available': False,
                    'error': str(e),
                    'class_name': class_name,
                    'module_path': module
                }
                print(f"  ❌ {name}: Import failed - {str(e)}")
            except Exception as e:
                results[name] = {
                    'imported': False,
                    'available': False,
                    'error': f"Unexpected error: {str(e)}",
                    'class_name': class_name,
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

            results['availability_flags'] = {
                'HAS_EMBEDDING_SERVICE': HAS_EMBEDDING_SERVICE,
                'HAS_SIMILARITY_SEARCH': HAS_SIMILARITY_SEARCH,
                'HAS_VECTOR_STORE': HAS_VECTOR_STORE
            }

            print(f"  HAS_EMBEDDING_SERVICE: {HAS_EMBEDDING_SERVICE}")
            print(f"  HAS_SIMILARITY_SEARCH: {HAS_SIMILARITY_SEARCH}")
            print(f"  HAS_VECTOR_STORE: {HAS_VECTOR_STORE}")
        except Exception as e:
            results['availability_flags'] = {'error': str(e)}
            print(f"  ❌ Availability flags test failed: {e}")

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
                    results[name] = {
                        'imported': True,
                        'available': service_available,
                        'type': 'flag'
                    }
                    print(f"  ✓ {name}: {service_available}")
                else:
                    service_class = getattr(module_imported, import_name)
                    results[name] = {
                        'imported': True,
                        'available': True,
                        'class_name': import_name,
                        'module_path': module
                    }
                    print(f"  ✓ {name}: Imported successfully")
            except ImportError as e:
                results[name] = {
                    'imported': False,
                    'available': False,
                    'error': str(e),
                    'module_path': module
                }
                print(f"  ❌ {name}: Import failed - {str(e)}")
            except Exception as e:
                results[name] = {
                    'imported': False,
                    'available': False,
                    'error': f"Unexpected error: {str(e)}",
                    'module_path': module
                }
                print(f"  ❌ {name}: Unexpected error - {str(e)}")

        self.test_results['import_tests'] = results
        print()

    def test_configuration(self):
        """Test AI services configuration."""
        print("⚙️  TESTING AI SERVICES CONFIGURATION")
        print("-" * 50)

        results = {}

        # Test Django settings
        print("Testing Django settings...")

        from django.conf import settings

        ai_settings = {
            'GOOGLE_API_KEY': hasattr(settings, 'GOOGLE_API_KEY') and bool(getattr(settings, 'GOOGLE_API_KEY', None)),
            'AI_ENABLED': getattr(settings, 'AI_ENABLED', False),
            'AI_CACHE_TIMEOUT': getattr(settings, 'AI_CACHE_TIMEOUT', 3600),
            'AI_MAX_TOKENS': getattr(settings, 'AI_MAX_TOKENS', 4000),
        }

        results['django_settings'] = ai_settings

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
            'PYTHONPATH': os.getenv('PYTHONPATH'),
        }

        results['environment_variables'] = env_vars

        for var, value in env_vars.items():
            if var == 'GOOGLE_API_KEY':
                status = "✅ Set" if value else "❌ Missing"
                print(f"  {var}: {status}")
            else:
                print(f"  {var}: {value}")

        # Test GeminiService configuration if available
        print("\nTesting GeminiService configuration...")
        try:
            from ai_assistant.services import GeminiService

            # Try to initialize (may fail if no API key)
            try:
                service = GeminiService()
                results['gemini_config'] = {
                    'configurable': True,
                    'model_name': service.model_name,
                    'temperature': service.temperature,
                    'max_retries': service.max_retries,
                    'cultural_context': hasattr(service, 'cultural_context')
                }
                print("  ✓ GeminiService: Configurable")
                print(f"    Model: {service.model_name}")
                print(f"    Temperature: {service.temperature}")
            except Exception as config_error:
                results['gemini_config'] = {
                    'configurable': False,
                    'error': str(config_error)
                }
                print(f"  ❌ GeminiService: {config_error}")
        except ImportError:
            results['gemini_config'] = {'configurable': False, 'error': 'Not imported'}
            print("  ❌ GeminiService: Not available")

        # Test file system permissions for AI indices
        print("\nTesting file system permissions...")

        try:
            ai_indices_path = os.path.join(settings.BASE_DIR, 'ai_assistant', 'vector_indices')

            # Test directory creation
            os.makedirs(ai_indices_path, exist_ok=True)

            # Test write permissions
            test_file = os.path.join(ai_indices_path, 'test_write.tmp')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)

                results['file_permissions'] = {
                    'readable': True,
                    'writable': True,
                    'directory_exists': True,
                    'path': ai_indices_path
                }
                print(f"  ✓ AI indices directory: {ai_indices_path}")
                print("  ✓ Read/write permissions: OK")
            except Exception as write_error:
                results['file_permissions'] = {
                    'readable': False,
                    'writable': False,
                    'error': str(write_error),
                    'path': ai_indices_path
                }
                print(f"  ❌ Write permissions failed: {write_error}")
        except Exception as path_error:
            results['file_permissions'] = {'error': str(path_error)}
            print(f"  ❌ Path creation failed: {path_error}")

        self.test_results['configuration_tests'] = results
        print()

    def test_basic_functionality(self):
        """Test basic AI services functionality without heavy operations."""
        print("🔧 TESTING BASIC FUNCTIONALITY")
        print("-" * 50)

        results = {}

        # Test GeminiService basic functionality
        print("Testing GeminiService basic functionality...")
        try:
            from ai_assistant.services import GeminiService

            service = GeminiService()

            # Test token counting (doesn't require API call)
            test_text = "This is a test text for token counting."
            try:
                token_count = service.count_tokens(test_text)
                results['token_counting'] = {
                    'working': True,
                    'sample_text': test_text,
                    'token_count': token_count
                }
                print(f"  ✓ Token counting: {token_count} tokens")
            except Exception as token_error:
                results['token_counting'] = {
                    'working': False,
                    'error': str(token_error)
                }
                print(f"  ❌ Token counting failed: {token_error}")

            # Test prompt building
            try:
                test_prompt = service._build_prompt(
                    "Test query",
                    system_context="System test",
                    include_cultural_context=False
                )
                results['prompt_building'] = {
                    'working': True,
                    'sample_prompt_length': len(test_prompt)
                }
                print(f"  ✓ Prompt building: {len(test_prompt)} characters")
            except Exception as prompt_error:
                results['prompt_building'] = {
                    'working': False,
                    'error': str(prompt_error)
                }
                print(f"  ❌ Prompt building failed: {prompt_error}")

        except ImportError:
            results['gemini_service'] = {'available': False}
            print("  ❌ GeminiService not available")

        # Test TemplateMatcher basic functionality
        print("\nTesting TemplateMatcher basic functionality...")
        try:
            from common.ai_services.chat.template_matcher import get_template_matcher

            matcher = get_template_matcher()

            # Test template suggestions
            try:
                suggestions = matcher.get_template_suggestions("how many", "communities", 3)
                results['template_suggestions'] = {
                    'working': True,
                    'suggestions_count': len(suggestions)
                }
                print(f"  ✓ Template suggestions: {len(suggestions)} suggestions")
            except Exception as suggest_error:
                results['template_suggestions'] = {
                    'working': False,
                    'error': str(suggest_error)
                }
                print(f"  ❌ Template suggestions failed: {suggest_error}")

        except ImportError:
            results['template_matcher'] = {'available': False}
            print("  ❌ TemplateMatcher not available")

        # Test EntityExtractor basic functionality
        print("\nTesting EntityExtractor basic functionality...")
        try:
            from common.ai_services.chat.entity_extractor import EntityExtractor

            extractor = EntityExtractor()

            # Test entity extraction
            test_text = "How many Tausug communities are in Zamboanga del Norte?"
            try:
                entities = extractor.extract_entities(test_text)
                results['entity_extraction'] = {
                    'working': True,
                    'sample_text': test_text,
                    'entities_found': entities
                }
                print(f"  ✓ Entity extraction: {len(entities)} entity types")
                for entity_type, entity_list in entities.items():
                    if entity_list:
                        print(f"    {entity_type}: {entity_list}")
            except Exception as extract_error:
                results['entity_extraction'] = {
                    'working': False,
                    'error': str(extract_error)
                }
                print(f"  ❌ Entity extraction failed: {extract_error}")

        except ImportError:
            results['entity_extractor'] = {'available': False}
            print("  ❌ EntityExtractor not available")

        # Test basic caching
        print("\nTesting basic caching functionality...")
        try:
            from django.core.cache import cache

            # Test cache set/get
            test_key = "ai_test_key"
            test_value = {"test": "data", "timestamp": time.time()}

            cache.set(test_key, test_value, 60)
            retrieved = cache.get(test_key)

            if retrieved == test_value:
                results['cache_functionality'] = {
                    'working': True,
                    'backend': str(cache.__class__.__name__)
                }
                print(f"  ✓ Cache: {cache.__class__.__name__}")
            else:
                results['cache_functionality'] = {
                    'working': False,
                    'error': 'Cache set/get mismatch'
                }
                print("  ❌ Cache: Set/get mismatch")

            # Clean up
            cache.delete(test_key)

        except Exception as cache_error:
            results['cache_functionality'] = {
                'working': False,
                'error': str(cache_error)
            }
            print(f"  ❌ Cache functionality failed: {cache_error}")

        self.test_results['basic_functionality'] = results
        print()

    def test_dependencies(self):
        """Test dependency availability."""
        print("📚 TESTING DEPENDENCIES")
        print("-" * 50)

        results = {}

        # Test required packages
        packages = [
            ('django', 'Django'),
            ('numpy', 'NumPy'),
            ('google.generativeai', 'Google Generative AI'),
            ('sentence_transformers', 'Sentence Transformers'),
            ('faiss', 'FAISS'),
            ('psutil', 'psutil (optional)'),
        ]

        print("Testing Python packages...")
        for package, display_name in packages:
            try:
                if package == 'sentence_transformers':
                    import sentence_transformers
                    version = getattr(sentence_transformers, '__version__', 'unknown')
                    results[package] = {
                        'available': True,
                        'version': version,
                        'display_name': display_name
                    }
                    print(f"  ✓ {display_name}: {version}")
                elif package == 'faiss':
                    import faiss
                    version = getattr(faiss, '__version__', 'unknown')
                    results[package] = {
                        'available': True,
                        'version': version,
                        'display_name': display_name
                    }
                    print(f"  ✓ {display_name}: {version}")
                elif package == 'google.generativeai':
                    import google.generativeai as genai
                    version = getattr(genai, '__version__', 'unknown')
                    results[package] = {
                        'available': True,
                        'version': version,
                        'display_name': display_name
                    }
                    print(f"  ✓ {display_name}: {version}")
                else:
                    module = __import__(package)
                    version = getattr(module, '__version__', 'unknown')
                    results[package] = {
                        'available': True,
                        'version': version,
                        'display_name': display_name
                    }
                    print(f"  ✓ {display_name}: {version}")
            except ImportError:
                results[package] = {
                    'available': False,
                    'display_name': display_name
                }
                print(f"  ❌ {display_name}: Not installed")

        # Test model availability (without downloading)
        print("\nTesting model availability...")
        try:
            from ai_assistant.services import EmbeddingService

            # Check if we can create service (will download model if needed)
            # We'll skip this for now to avoid long downloads
            results['model_availability'] = {
                'status': 'not_tested',
                'reason': 'Skipping to avoid model download'
            }
            print("  ⚠ Embedding model: Not tested (avoids download)")
        except ImportError:
            results['model_availability'] = {
                'status': 'unavailable',
                'reason': 'EmbeddingService not importable'
            }
            print("  ❌ Embedding model: Service not available")

        self.test_results['dependency_status'] = results
        print()

    def generate_recommendations(self):
        """Generate recommendations based on test results."""
        print("💡 GENERATING RECOMMENDATIONS")
        print("-" * 50)

        recommendations = []

        # Check import results
        import_results = self.test_results.get('import_tests', {})

        # Check critical services
        critical_services = ['GeminiService', 'EmbeddingService', 'VectorStore']
        for service in critical_services:
            service_result = import_results.get(service, {})
            if not service_result.get('imported'):
                recommendations.append({
                    'priority': 'HIGH',
                    'category': 'Dependencies',
                    'issue': f'{service} not available',
                    'recommendation': self._get_dependency_recommendation(service),
                    'impact': 'Core AI functionality unavailable'
                })

        # Check configuration
        config_results = self.test_results.get('configuration_tests', {})
        django_settings = config_results.get('django_settings', {})

        if not django_settings.get('GOOGLE_API_KEY'):
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Configuration',
                'issue': 'Google API key not configured',
                'recommendation': 'Set GOOGLE_API_KEY in Django settings or environment variables',
                'impact': 'Gemini AI features unavailable'
            })

        if not django_settings.get('AI_ENABLED'):
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Configuration',
                'issue': 'AI features not enabled',
                'recommendation': 'Set AI_ENABLED=True in Django settings',
                'impact': 'AI features may be disabled'
            })

        # Check file permissions
        file_perms = config_results.get('file_permissions', {})
        if not file_perms.get('writable'):
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Configuration',
                'issue': 'AI indices directory not writable',
                'recommendation': 'Check permissions for ai_assistant/vector_indices directory',
                'impact': 'Vector search cannot save indices'
            })

        # Check dependency status
        dep_results = self.test_results.get('dependency_status', {})

        missing_packages = []
        for package, info in dep_results.items():
            if not info.get('available'):
                missing_packages.append(info.get('display_name', package))

        if missing_packages:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Dependencies',
                'issue': f'Missing packages: {", ".join(missing_packages)}',
                'recommendation': 'Install missing packages using pip',
                'impact': 'Corresponding AI features unavailable'
            })

        # Basic functionality recommendations
        func_results = self.test_results.get('basic_functionality', {})

        gemini_config = config_results.get('gemini_config', {})
        if not gemini_config.get('configurable'):
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Configuration',
                'issue': 'GeminiService not configurable',
                'recommendation': 'Check API key configuration and network connectivity',
                'impact': 'All AI generation features unavailable'
            })

        # Add general recommendations
        recommendations.extend([
            {
                'priority': 'MEDIUM',
                'category': 'Performance',
                'issue': 'Model download time',
                'recommendation': 'Pre-download models during deployment to avoid user delays',
                'impact': 'Better user experience'
            },
            {
                'priority': 'LOW',
                'category': 'Monitoring',
                'issue': 'No AI service health monitoring',
                'recommendation': 'Implement health checks for AI services',
                'impact': 'Better system reliability'
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

    def _get_dependency_recommendation(self, service: str) -> str:
        """Get installation recommendation for a service."""
        recommendations = {
            'GeminiService': 'pip install google-generativeai',
            'EmbeddingService': 'pip install sentence-transformers',
            'VectorStore': 'pip install faiss-cpu',
            'SimilaritySearchService': 'Install EmbeddingService and VectorStore dependencies'
        }
        return recommendations.get(service, 'Check documentation for installation instructions')

    def save_report(self, filename: str = None):
        """Save test results to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_services_basic_test_report_{timestamp}.json"

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
        print("AI SERVICES BASIC INTEGRATION TEST SUMMARY")
        print("=" * 80)

        # Import Status
        import_results = self.test_results.get('import_tests', {})
        print("\n📦 IMPORT STATUS")

        services = [
            ('EmbeddingService', import_results.get('EmbeddingService', {})),
            ('GeminiService', import_results.get('GeminiService', {})),
            ('VectorStore', import_results.get('VectorStore', {})),
            ('SimilaritySearchService', import_results.get('SimilaritySearchService', {})),
            ('UnifiedSearchEngine', import_results.get('UnifiedSearchEngine', {})),
            ('QueryParser', import_results.get('QueryParser', {})),
            ('TemplateMatcher', import_results.get('TemplateMatcher', {})),
        ]

        for name, result in services:
            status = "✅ IMPORTED" if result.get('imported') else "❌ NOT IMPORTED"
            print(f"  {name}: {status}")

        # Configuration Status
        config_results = self.test_results.get('configuration_tests', {})
        print("\n⚙️  CONFIGURATION STATUS")

        api_key_configured = config_results.get('django_settings', {}).get('GOOGLE_API_KEY', False)
        file_perms_ok = config_results.get('file_permissions', {}).get('writable', False)

        print(f"  Google API Key: {'✅ Configured' if api_key_configured else '❌ Missing'}")
        print(f"  File Permissions: {'✅ OK' if file_perms_ok else '❌ Issue'}")

        # Dependency Status
        dep_results = self.test_results.get('dependency_status', {})
        print("\n📚 DEPENDENCY STATUS")

        critical_deps = ['django', 'numpy', 'google.generativeai']
        for dep in critical_deps:
            info = dep_results.get(dep, {})
            status = "✅ AVAILABLE" if info.get('available') else "❌ MISSING"
            version = f" ({info.get('version', 'unknown')})" if info.get('available') else ""
            print(f"  {info.get('display_name', dep)}: {status}{version}")

        # Basic Functionality Status
        func_results = self.test_results.get('basic_functionality', {})
        print("\n🔧 BASIC FUNCTIONALITY")

        functionalities = [
            ('Token Counting', func_results.get('token_counting', {})),
            ('Entity Extraction', func_results.get('entity_extraction', {})),
            ('Cache System', func_results.get('cache_functionality', {})),
            ('Template Matching', func_results.get('template_suggestions', {})),
        ]

        for name, result in functionalities:
            status = "✅ WORKING" if result.get('working') else "❌ NOT WORKING"
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
        total_imported = sum(1 for result in import_results.values() if result.get('imported'))
        total_services = len([s for s in import_results.keys() if not s.startswith('HAS_')])

        print(f"\n📊 OVERALL STATUS")
        if total_imported == total_services and api_key_configured:
            print("  🟢 All AI services properly configured")
        elif total_imported >= total_services * 0.7:
            print("  🟡 Most AI services available")
        elif total_imported >= total_services * 0.5:
            print("  🟠 Some AI services available")
        else:
            print("  🔴 Few AI services available")

        print(f"  Services imported: {total_imported}/{total_services}")
        print("=" * 80)


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description='Test OBCMS/BMMS AI Services Basic Integration')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--save-report', '-s', action='store_true', help='Save report to JSON file')
    parser.add_argument('--output', '-o', type=str, help='Output filename for report')

    args = parser.parse_args()

    # Run tests
    tester = BasicAIServicesTester(verbose=args.verbose)
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