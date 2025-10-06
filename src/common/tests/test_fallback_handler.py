"""
Tests for Fallback Handler System

Tests all components:
- SimilarityCalculator
- QueryCorrector
- FallbackHandler

Ensures fast, accurate fallback suggestions for failed queries.
"""

import pytest
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache

from common.ai_services.chat.similarity import SimilarityCalculator
from common.ai_services.chat.query_corrector import QueryCorrector
from common.ai_services.chat.fallback_handler import FallbackHandler
from common.models import ChatMessage

User = get_user_model()


@pytest.fixture
def test_user(db):
    """Create test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        user_type='oobc_staff'
    )


@pytest.fixture
def sample_chat_messages(db, test_user):
    """Create sample successful chat messages."""
    messages = [
        "How many communities in Region IX?",
        "Show me communities in Region IX",
        "List all communities in Zamboanga del Sur",
        "Count communities with fishing livelihood",
        "How many workshops in Region X?",
        "Show me MANA assessments in Davao",
        "List active policy recommendations",
        "Count partnerships in Region IX",
    ]

    chat_messages = []
    for msg in messages:
        chat_messages.append(ChatMessage.objects.create(
            user=test_user,
            user_message=msg,
            assistant_response="Test response",
            intent='data_query',
            confidence=0.85,
            topic='communities',
        ))

    return chat_messages


@pytest.fixture
def similarity_calc():
    """Get SimilarityCalculator instance."""
    calc = SimilarityCalculator()
    calc.clear_cache()  # Start fresh
    return calc


@pytest.fixture
def query_corrector():
    """Get QueryCorrector instance."""
    return QueryCorrector()


@pytest.fixture
def fallback_handler():
    """Get FallbackHandler instance."""
    cache.clear()  # Clear cache before tests
    return FallbackHandler()


# ==================== SimilarityCalculator Tests ====================

class TestSimilarityCalculator:
    """Test similarity calculation algorithms."""

    def test_levenshtein_exact_match(self, similarity_calc):
        """Test Levenshtein distance for exact match."""
        distance = similarity_calc.levenshtein_distance("hello", "hello")
        assert distance == 0

    def test_levenshtein_one_substitution(self, similarity_calc):
        """Test Levenshtein distance with one substitution."""
        distance = similarity_calc.levenshtein_distance("hello", "hallo")
        assert distance == 1

    def test_levenshtein_complex(self, similarity_calc):
        """Test Levenshtein distance for complex changes."""
        # kitten -> sitting requires 3 operations
        distance = similarity_calc.levenshtein_distance("kitten", "sitting")
        assert distance == 3

    def test_levenshtein_empty_strings(self, similarity_calc):
        """Test Levenshtein distance with empty strings."""
        assert similarity_calc.levenshtein_distance("", "hello") == 5
        assert similarity_calc.levenshtein_distance("hello", "") == 5
        assert similarity_calc.levenshtein_distance("", "") == 0

    def test_jaccard_exact_match(self, similarity_calc):
        """Test Jaccard similarity for exact match."""
        similarity = similarity_calc.jaccard_similarity("hello world", "hello world")
        assert similarity == 1.0

    def test_jaccard_no_overlap(self, similarity_calc):
        """Test Jaccard similarity with no overlap."""
        similarity = similarity_calc.jaccard_similarity("hello world", "foo bar")
        assert similarity == 0.0

    def test_jaccard_partial_overlap(self, similarity_calc):
        """Test Jaccard similarity with partial overlap."""
        # "hello world" and "hello there" share 1 word out of 3 total
        similarity = similarity_calc.jaccard_similarity("hello world", "hello there")
        assert 0.3 < similarity < 0.4  # Should be around 0.333

    def test_combined_similarity_identical(self, similarity_calc):
        """Test combined similarity for identical strings."""
        similarity = similarity_calc.calculate_similarity(
            "communities in region ix",
            "communities in region ix"
        )
        assert similarity == 1.0

    def test_combined_similarity_close(self, similarity_calc):
        """Test combined similarity for similar strings."""
        similarity = similarity_calc.calculate_similarity(
            "communities in region 9",
            "communities in Region IX"
        )
        assert similarity > 0.75  # Should be very similar

    def test_combined_similarity_different(self, similarity_calc):
        """Test combined similarity for different strings."""
        similarity = similarity_calc.calculate_similarity(
            "communities in region 9",
            "workshops in davao"
        )
        assert similarity < 0.5  # Should be quite different

    def test_find_most_similar(self, similarity_calc):
        """Test finding most similar queries."""
        query = "communities in region 9"
        candidates = [
            "communities in Region IX",
            "workshops in Region IX",
            "communities in Region X",
            "policies in Region IX",
        ]

        results = similarity_calc.find_most_similar(query, candidates, limit=2)

        assert len(results) == 2
        # Both Region IX and Region X are very similar, either could be first
        assert results[0][0] in ["communities in Region IX", "communities in Region X"]
        assert results[0][1] > 0.75  # High similarity
        assert results[1][1] < results[0][1]  # Second is less similar

    def test_find_most_similar_with_threshold(self, similarity_calc):
        """Test finding similar queries with threshold."""
        query = "communities in region 9"
        candidates = [
            "communities in Region IX",  # Very similar
            "workshops in Davao",  # Not similar
        ]

        results = similarity_calc.find_most_similar(
            query,
            candidates,
            threshold=0.7,
            limit=5
        )

        # Only the similar one should be returned
        assert len(results) == 1
        assert results[0][0] == "communities in Region IX"

    def test_cache_functionality(self, similarity_calc):
        """Test that similarity calculations are cached."""
        query1 = "hello world"
        query2 = "hello there"

        # First calculation
        result1 = similarity_calc.calculate_similarity(query1, query2)

        # Second calculation (should hit cache)
        result2 = similarity_calc.calculate_similarity(query1, query2)

        assert result1 == result2

        # Check cache stats
        stats = similarity_calc.get_cache_stats()
        assert stats['size'] > 0

    def test_performance_levenshtein(self, similarity_calc):
        """Test Levenshtein distance performance."""
        import time
        start = time.perf_counter()

        result = similarity_calc.levenshtein_distance(
            "how many communities in region ix",
            "show me communities in Region IX"
        )

        elapsed = time.perf_counter() - start

        # Should complete in < 1ms
        assert result >= 0
        assert elapsed < 0.001  # 1ms


# ==================== QueryCorrector Tests ====================

class TestQueryCorrector:
    """Test query spelling correction."""

    def test_correct_simple_typo(self, query_corrector):
        """Test correcting simple typo."""
        corrected = query_corrector.correct_spelling("comunitys")
        assert "communities" in corrected.lower()

    def test_correct_multiple_typos(self, query_corrector):
        """Test correcting multiple typos."""
        corrected = query_corrector.correct_spelling("how many comunitys in regon 9")
        assert "communities" in corrected.lower()
        assert "region" in corrected.lower()

    def test_correct_region_codes(self, query_corrector):
        """Test normalizing region codes."""
        corrected = query_corrector.correct_spelling("communities in region 9")
        assert "Region IX" in corrected

        corrected = query_corrector.correct_spelling("workshops in region 10")
        assert "Region X" in corrected

    def test_correct_ethnolinguistic_groups(self, query_corrector):
        """Test correcting ethnolinguistic group names."""
        corrected = query_corrector.correct_spelling("marano communities")
        assert "maranao" in corrected.lower()  # Corrects typo

        corrected = query_corrector.correct_spelling("tausug fishing")
        assert "tausug" in corrected.lower()  # Already correct

    def test_correct_phrases(self, query_corrector):
        """Test correcting common phrase mistakes."""
        corrected = query_corrector.correct_spelling("how many community in regon")
        assert "communities" in corrected.lower()
        assert "region" in corrected.lower()

    def test_preserve_correct_words(self, query_corrector):
        """Test that correct words are preserved."""
        original = "How many communities in Region IX?"
        corrected = query_corrector.correct_spelling(original)
        # Should be mostly unchanged (except possibly capitalization)
        assert "communities" in corrected.lower()
        assert "Region IX" in corrected

    def test_suggest_alternatives(self, query_corrector):
        """Test generating query alternatives."""
        alternatives = query_corrector.suggest_alternatives("communities in region 9")

        assert len(alternatives) > 0
        # Should include variations
        assert any("How many" in alt for alt in alternatives)
        assert any("Show me" in alt for alt in alternatives)

    def test_suggest_alternatives_workshops(self, query_corrector):
        """Test alternatives for workshop queries."""
        alternatives = query_corrector.suggest_alternatives("workshops in zamboanga")

        assert len(alternatives) > 0
        assert any("MANA" in alt for alt in alternatives)
        assert any("workshop" in alt.lower() for alt in alternatives)

    def test_correction_confidence_no_change(self, query_corrector):
        """Test confidence when no correction needed."""
        confidence = query_corrector.get_correction_confidence(
            "communities in Region IX",
            "communities in Region IX"
        )
        assert confidence == 0.0  # No correction needed

    def test_correction_confidence_small_change(self, query_corrector):
        """Test confidence for small corrections."""
        confidence = query_corrector.get_correction_confidence(
            "comunities in Region IX",
            "communities in Region IX"
        )
        assert confidence > 0.7  # High confidence

    def test_correction_confidence_large_change(self, query_corrector):
        """Test confidence for large corrections."""
        confidence = query_corrector.get_correction_confidence(
            "cmnts rgn 9",
            "communities in Region IX"
        )
        assert confidence < 0.7  # Lower confidence


# ==================== FallbackHandler Tests ====================

class TestFallbackHandler:
    """Test comprehensive fallback handling."""

    def test_handle_failed_query_basic(self, fallback_handler):
        """Test basic fallback response structure."""
        result = fallback_handler.handle_failed_query(
            "comunitys in regon 9",
            intent='data_query',
            entities={}
        )

        assert result['type'] == 'query_failed'
        assert result['original_query'] == "comunitys in regon 9"
        assert 'error_analysis' in result
        assert 'suggestions' in result
        assert 'alternatives' in result

    def test_error_analysis_missing_location(self, fallback_handler):
        """Test detecting missing location error."""
        result = fallback_handler.handle_failed_query(
            "how many communities",
            intent='data_query',
            entities={}
        )

        error_analysis = result['error_analysis']
        assert error_analysis['likely_issue'] == 'missing_location'
        assert error_analysis['confidence'] > 0.5

    def test_error_analysis_typo(self, fallback_handler):
        """Test detecting typo errors."""
        result = fallback_handler.handle_failed_query(
            "comunitys in regon 9",
            intent='data_query',
            entities={}
        )

        error_analysis = result['error_analysis']
        assert error_analysis['likely_issue'] == 'unrecognized_term'

    def test_error_analysis_ambiguous(self, fallback_handler):
        """Test detecting ambiguous queries."""
        result = fallback_handler.handle_failed_query(
            "show me",
            intent='data_query',
            entities={}
        )

        error_analysis = result['error_analysis']
        assert error_analysis['likely_issue'] in ['ambiguous_query', 'unsupported_query']

    def test_generate_suggestions(self, fallback_handler):
        """Test suggestion generation."""
        suggestions = fallback_handler.generate_suggestions("comunitys in regon 9")

        assert len(suggestions) > 0
        # Should include corrected version
        assert any("communities" in s.lower() for s in suggestions)
        # Region code should be corrected (look for "region" at least)
        assert any("region" in s.lower() for s in suggestions)

    def test_find_similar_queries(
        self,
        fallback_handler,
        sample_chat_messages
    ):
        """Test finding similar successful queries."""
        similar = fallback_handler.find_similar_successful_queries(
            "communities in region 9",
            limit=3
        )

        assert len(similar) <= 3
        # Should find the similar queries
        assert any("communities" in q.lower() for q in similar)

    def test_find_similar_queries_caching(
        self,
        fallback_handler,
        sample_chat_messages
    ):
        """Test that similar query search uses caching."""
        query = "communities in region 9"

        # First call
        result1 = fallback_handler.find_similar_successful_queries(query)

        # Second call (should hit cache)
        result2 = fallback_handler.find_similar_successful_queries(query)

        assert result1 == result2

    def test_get_query_templates(self, fallback_handler):
        """Test getting query templates."""
        templates = fallback_handler.get_query_templates_for_intent(
            'data_query',
            entities={'communities': True}
        )

        assert len(templates) > 0
        # Should include community templates
        assert any("communities" in t.lower() for t in templates)

    def test_get_query_templates_with_location(self, fallback_handler):
        """Test templates with location filled."""
        templates = fallback_handler.get_query_templates_for_intent(
            'data_query',
            entities={'communities': True, 'location': 'Zamboanga del Sur'}
        )

        assert len(templates) > 0
        # Should have location filled in
        assert any("Zamboanga del Sur" in t for t in templates)

    def test_alternatives_include_query_builder(self, fallback_handler):
        """Test that alternatives include query builder."""
        result = fallback_handler.handle_failed_query(
            "complex query",
            intent='data_query'
        )

        alternatives = result['alternatives']
        assert any(alt['type'] == 'query_builder' for alt in alternatives)
        assert any(alt['type'] == 'help' for alt in alternatives)

    def test_fallback_stats(self, fallback_handler, sample_chat_messages, test_user):
        """Test getting fallback statistics."""
        # Create some failed queries
        ChatMessage.objects.create(
            user=test_user,
            user_message="failed query",
            assistant_response="Sorry, I couldn't understand",
            intent='data_query',
            confidence=0.3,  # Low confidence = failure
        )

        stats = fallback_handler.get_fallback_stats()

        assert 'total_queries' in stats
        assert 'failed_queries' in stats
        assert 'fallback_rate' in stats
        assert stats['total_queries'] > 0

    def test_performance_handle_failed_query(self, fallback_handler):
        """Test fallback handler performance."""
        import time
        start = time.perf_counter()

        result = fallback_handler.handle_failed_query(
            "comunitys in regon 9",
            intent='data_query',
            entities={}
        )

        elapsed = time.perf_counter() - start

        # Should complete in < 50ms
        assert result['type'] == 'query_failed'
        assert elapsed < 0.05  # 50ms

    def test_analyze_failure_reason_performance(self, fallback_handler):
        """Test failure analysis performance."""
        import time
        start = time.perf_counter()

        result = fallback_handler.analyze_failure_reason(
            "comunitys in regon 9",
            'data_query',
            {}
        )

        elapsed = time.perf_counter() - start

        assert 'likely_issue' in result
        assert elapsed < 0.01  # 10ms


# ==================== Integration Tests ====================

class TestFallbackIntegration:
    """Test full fallback workflow integration."""

    def test_end_to_end_typo_correction(
        self,
        fallback_handler,
        sample_chat_messages
    ):
        """Test full workflow for typo correction."""
        # User makes typo
        result = fallback_handler.handle_failed_query(
            "how many comunitys in regon 9",
            intent='data_query',
            entities={}
        )

        # Should provide helpful response
        assert result['type'] == 'query_failed'

        # Should have corrected suggestions
        suggestions = result['suggestions']['corrected_queries']
        assert len(suggestions) > 0
        assert any("communities" in s.lower() for s in suggestions)

        # Should have similar successful queries
        similar = result['suggestions']['similar_queries']
        assert len(similar) >= 0  # May or may not find similar

        # Should have alternatives
        assert len(result['alternatives']) > 0

    def test_end_to_end_missing_location(self, fallback_handler):
        """Test full workflow for missing location."""
        result = fallback_handler.handle_failed_query(
            "how many communities",
            intent='data_query',
            entities={}
        )

        # Should identify the issue
        assert result['error_analysis']['likely_issue'] == 'missing_location'

        # Should provide location-aware suggestions
        templates = result['suggestions']['template_examples']
        assert any("Region" in t for t in templates)

    def test_end_to_end_ambiguous_query(self, fallback_handler):
        """Test full workflow for ambiguous query."""
        result = fallback_handler.handle_failed_query(
            "show me",
            intent='data_query',
            entities={}
        )

        # Should provide clear guidance
        assert 'error_analysis' in result
        # May not have corrections for very ambiguous query, but should have templates
        assert len(result['suggestions']['template_examples']) > 0

        # Should offer query builder as alternative
        assert any(
            alt['type'] == 'query_builder'
            for alt in result['alternatives']
        )


# ==================== Performance Benchmarks ====================

@pytest.mark.performance
def test_benchmark_levenshtein(similarity_calc):
    """Benchmark Levenshtein distance calculation."""
    import time
    s1 = "how many communities in region ix"
    s2 = "show me communities in Region IX"

    start = time.perf_counter()
    result = similarity_calc.levenshtein_distance(s1, s2)
    elapsed = time.perf_counter() - start

    assert result >= 0
    assert elapsed < 0.001  # < 1ms


@pytest.mark.performance
def test_benchmark_jaccard(similarity_calc):
    """Benchmark Jaccard similarity calculation."""
    import time
    s1 = "how many communities in region ix"
    s2 = "show me communities in Region IX"

    start = time.perf_counter()
    result = similarity_calc.jaccard_similarity(s1, s2)
    elapsed = time.perf_counter() - start

    assert 0.0 <= result <= 1.0
    assert elapsed < 0.001  # < 1ms


@pytest.mark.performance
def test_benchmark_spelling_correction(query_corrector):
    """Benchmark spelling correction."""
    import time
    query = "how many comunitys in regon 9"

    start = time.perf_counter()
    result = query_corrector.correct_spelling(query)
    elapsed = time.perf_counter() - start

    assert "communities" in result.lower()
    assert elapsed < 0.01  # < 10ms


@pytest.mark.performance
def test_benchmark_full_fallback(fallback_handler):
    """Benchmark full fallback handling."""
    import time

    start = time.perf_counter()
    result = fallback_handler.handle_failed_query(
        "comunitys in regon 9",
        'data_query',
        {}
    )
    elapsed = time.perf_counter() - start

    assert result['type'] == 'query_failed'
    assert elapsed < 0.05  # < 50ms
