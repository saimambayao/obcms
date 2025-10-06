#!/usr/bin/env python
"""
OBCMS AI Services Verification Script

Automated health check for all AI services and modules.
Verifies:
- AI service implementations exist
- Gemini API connectivity
- Service initialization
- Basic functionality
"""

import os
import sys
import django
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / 'src'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings.development')
django.setup()

# Now import Django components
from django.conf import settings
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)


def print_header(text):
    """Print section header"""
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"{Fore.CYAN}{text}")
    print(f"{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}")


def print_success(text):
    """Print success message"""
    print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")


def print_error(text):
    """Print error message"""
    print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")


def print_warning(text):
    """Print warning message"""
    print(f"{Fore.YELLOW}⚠️  {text}{Style.RESET_ALL}")


def print_info(text):
    """Print info message"""
    print(f"{Fore.BLUE}ℹ️  {text}{Style.RESET_ALL}")


def check_google_api_key():
    """Check if Google API key is configured"""
    print_header("1. GOOGLE API KEY CONFIGURATION")

    api_key = getattr(settings, 'GOOGLE_API_KEY', None)

    if api_key and api_key != 'your-google-api-key-here':
        print_success("Google API Key is configured")
        return True
    else:
        print_error("Google API Key is NOT configured")
        print_info("Set GOOGLE_API_KEY in .env file")
        return False


def check_ai_service_implementations():
    """Check if all AI service modules exist"""
    print_header("2. AI SERVICE IMPLEMENTATIONS")

    modules = {
        'Communities AI': 'communities.ai_services',
        'MANA AI': 'mana.ai_services',
        'Coordination AI': 'coordination.ai_services',
        'Policy AI': 'recommendations.policies.ai_services',
        'M&E AI': 'project_central.ai_services',
        'Unified Search': 'common.ai_services.unified_search',
        'Chat Assistant': 'common.ai_services.chat',
    }

    results = {}

    for name, module_path in modules.items():
        try:
            __import__(module_path)
            print_success(f"{name}: {module_path}")
            results[name] = True
        except ImportError as e:
            print_error(f"{name}: {module_path} - {str(e)}")
            results[name] = False

    return results


def check_service_initialization():
    """Test initialization of each AI service"""
    print_header("3. SERVICE INITIALIZATION TESTS")

    tests = []

    # Communities AI Services
    try:
        from communities.ai_services.data_validator import CommunityDataValidator
        from communities.ai_services.needs_classifier import CommunityNeedsClassifier
        from communities.ai_services.community_matcher import CommunityMatcher

        validator = CommunityDataValidator()
        classifier = CommunityNeedsClassifier()
        matcher = CommunityMatcher()

        print_success("Communities AI: DataValidator, NeedsClassifier, CommunityMatcher")
        tests.append(('Communities AI', True))
    except Exception as e:
        print_error(f"Communities AI: {str(e)}")
        tests.append(('Communities AI', False))

    # MANA AI Services
    try:
        from mana.ai_services.response_analyzer import ResponseAnalyzer
        from mana.ai_services.theme_extractor import ThemeExtractor
        from mana.ai_services.needs_extractor import NeedsExtractor
        from mana.ai_services.report_generator import AssessmentReportGenerator
        from mana.ai_services.cultural_validator import BangsomoroCulturalValidator

        analyzer = ResponseAnalyzer()
        extractor = ThemeExtractor()
        needs = NeedsExtractor()
        generator = AssessmentReportGenerator()
        validator = BangsomoroCulturalValidator()

        print_success("MANA AI: All 5 services initialized")
        tests.append(('MANA AI', True))
    except Exception as e:
        print_error(f"MANA AI: {str(e)}")
        tests.append(('MANA AI', False))

    # Coordination AI Services
    try:
        from coordination.ai_services.stakeholder_matcher import StakeholderMatcher
        from coordination.ai_services.partnership_predictor import PartnershipPredictor
        from coordination.ai_services.meeting_intelligence import MeetingIntelligence
        from coordination.ai_services.resource_optimizer import ResourceOptimizer

        matcher = StakeholderMatcher()
        predictor = PartnershipPredictor()
        intelligence = MeetingIntelligence()
        optimizer = ResourceOptimizer()

        print_success("Coordination AI: All 4 services initialized")
        tests.append(('Coordination AI', True))
    except Exception as e:
        print_error(f"Coordination AI: {str(e)}")
        tests.append(('Coordination AI', False))

    # Policy AI Services
    try:
        from recommendations.policies.ai_services.evidence_gatherer import CrossModuleEvidenceGatherer
        from recommendations.policies.ai_services.policy_generator import PolicyGenerator
        from recommendations.policies.ai_services.impact_simulator import PolicyImpactSimulator
        from recommendations.policies.ai_services.compliance_checker import RegulatoryComplianceChecker

        gatherer = CrossModuleEvidenceGatherer()
        generator = PolicyGenerator()
        simulator = PolicyImpactSimulator()
        checker = RegulatoryComplianceChecker()

        print_success("Policy AI: All 4 services initialized")
        tests.append(('Policy AI', True))
    except Exception as e:
        print_error(f"Policy AI: {str(e)}")
        tests.append(('Policy AI', False))

    # M&E AI Services
    try:
        from project_central.ai_services.anomaly_detector import PPAAnomalyDetector
        from project_central.ai_services.performance_forecaster import PerformanceForecaster
        from project_central.ai_services.report_generator import MEReportGenerator
        from project_central.ai_services.risk_analyzer import RiskAnalyzer

        detector = PPAAnomalyDetector()
        forecaster = PerformanceForecaster()
        generator = MEReportGenerator()
        analyzer = RiskAnalyzer()

        print_success("M&E AI: All 4 services initialized")
        tests.append(('M&E AI', True))
    except Exception as e:
        print_error(f"M&E AI: {str(e)}")
        tests.append(('M&E AI', False))

    # Unified Search
    try:
        from common.ai_services.unified_search import UnifiedSearchService

        search = UnifiedSearchService()

        print_success("Unified Search: Service initialized")
        tests.append(('Unified Search', True))
    except Exception as e:
        print_error(f"Unified Search: {str(e)}")
        tests.append(('Unified Search', False))

    # Chat Assistant
    try:
        from common.ai_services.chat import (
            get_conversational_assistant,
            get_query_executor,
            get_intent_classifier,
        )

        assistant = get_conversational_assistant()
        executor = get_query_executor()
        classifier = get_intent_classifier()

        print_success("Chat Assistant: All components initialized")
        tests.append(('Chat Assistant', True))
    except Exception as e:
        print_error(f"Chat Assistant: {str(e)}")
        tests.append(('Chat Assistant', False))

    return tests


def check_gemini_connectivity():
    """Test Gemini API connectivity"""
    print_header("4. GEMINI API CONNECTIVITY")

    try:
        from ai_assistant.services.gemini_service import GeminiService

        gemini = GeminiService()

        # Test simple text generation
        result = gemini.generate_text("Say 'Hello OBCMS' (test)")

        if result.get('success'):
            print_success("Gemini API is accessible and responding")
            return True
        else:
            print_error(f"Gemini API error: {result.get('error')}")
            return False
    except Exception as e:
        print_error(f"Gemini API connection failed: {str(e)}")
        return False


def check_embedding_service():
    """Test embedding service"""
    print_header("5. EMBEDDING SERVICE")

    try:
        from ai_assistant.services.embedding_service import EmbeddingService

        service = EmbeddingService()

        # Test embedding generation
        result = service.generate_embedding("Test text for embedding")

        if result.get('success'):
            print_success(f"Embedding service working (dimension: {result.get('dimension')})")
            return True
        else:
            print_error(f"Embedding service error: {result.get('error')}")
            return False
    except Exception as e:
        print_error(f"Embedding service failed: {str(e)}")
        return False


def check_vector_store():
    """Test vector store operations"""
    print_header("6. VECTOR STORE")

    try:
        from ai_assistant.services.vector_store import VectorStore

        store = VectorStore()

        # Test basic operations
        test_embedding = [0.1] * 768  # Gemini embedding dimension

        # Test store
        result = store.store_embedding(
            content_type='test',
            content_id='test-1',
            embedding=test_embedding,
            metadata={'test': True}
        )

        if result.get('success'):
            print_success("Vector store: Store operation successful")

            # Test search
            search_result = store.search_similar(
                embedding=test_embedding,
                content_type='test',
                limit=5
            )

            if search_result.get('success'):
                print_success("Vector store: Search operation successful")

                # Clean up
                store.delete_embedding('test', 'test-1')
                print_success("Vector store: Delete operation successful")
                return True
            else:
                print_error(f"Vector store search failed: {search_result.get('error')}")
                return False
        else:
            print_error(f"Vector store failed: {result.get('error')}")
            return False
    except Exception as e:
        print_error(f"Vector store error: {str(e)}")
        return False


def generate_summary(results):
    """Generate verification summary"""
    print_header("VERIFICATION SUMMARY")

    total_checks = sum(len(v) if isinstance(v, list) else 1 for v in results.values())
    passed_checks = sum(
        sum(1 for r in v if r[1]) if isinstance(v, list) else (1 if v else 0)
        for v in results.values()
    )

    pass_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0

    print(f"\n{Fore.CYAN}Total Checks: {total_checks}")
    print(f"{Fore.GREEN}Passed: {passed_checks}")
    print(f"{Fore.RED}Failed: {total_checks - passed_checks}")
    print(f"{Fore.YELLOW}Pass Rate: {pass_rate:.1f}%{Style.RESET_ALL}\n")

    if pass_rate == 100:
        print_success("ALL CHECKS PASSED! AI services are ready for UAT.")
    elif pass_rate >= 80:
        print_warning("Most checks passed. Review failed items before UAT.")
    else:
        print_error("Multiple failures detected. Fix issues before UAT.")

    return pass_rate


def main():
    """Main verification function"""
    print(f"\n{Fore.MAGENTA}{'*' * 70}")
    print(f"{Fore.MAGENTA}OBCMS AI SERVICES VERIFICATION")
    print(f"{Fore.MAGENTA}{'*' * 70}{Style.RESET_ALL}\n")

    results = {}

    # Run all checks
    results['api_key'] = check_google_api_key()
    results['implementations'] = check_ai_service_implementations()
    results['initialization'] = check_service_initialization()

    # Only test connectivity if API key is configured
    if results['api_key']:
        results['gemini'] = check_gemini_connectivity()
        results['embedding'] = check_embedding_service()
        results['vector_store'] = check_vector_store()
    else:
        print_warning("Skipping API connectivity tests (no API key)")
        results['gemini'] = False
        results['embedding'] = False
        results['vector_store'] = False

    # Generate summary
    pass_rate = generate_summary(results)

    # Exit with appropriate code
    sys.exit(0 if pass_rate == 100 else 1)


if __name__ == '__main__':
    main()
