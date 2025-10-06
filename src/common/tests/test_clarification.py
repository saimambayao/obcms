"""
Tests for Clarification Handler

Tests clarification detection, dialog generation, context storage,
and multi-turn clarification flows.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from django.core.cache import cache

from common.ai_services.chat.clarification import (
    ClarificationHandler,
    get_clarification_handler,
)


@pytest.fixture
def clarification_handler():
    """Create a ClarificationHandler instance."""
    return ClarificationHandler()


@pytest.fixture
def clear_cache():
    """Clear cache before and after each test."""
    cache.clear()
    yield
    cache.clear()


class TestClarificationDetection:
    """Test clarification need detection."""

    def test_missing_location_detected(self, clarification_handler):
        """Test detection of missing location for community query."""
        result = clarification_handler.needs_clarification(
            query="show communities",
            entities={"communities": True},
            intent="data_query",
        )

        assert result is not None
        assert result["type"] == "clarification_needed"
        assert result["issue_type"] == "missing_location"
        assert "region" in result["message"].lower()
        assert len(result["options"]) == 5  # 4 regions + "All"

    def test_no_clarification_when_location_present(self, clarification_handler):
        """Test no clarification when location is provided."""
        result = clarification_handler.needs_clarification(
            query="show communities in Region IX",
            entities={"communities": True, "location": "Region IX"},
            intent="data_query",
        )

        # May still need other clarifications, but not location
        if result:
            assert result["issue_type"] != "missing_location"

    def test_ambiguous_date_detected(self, clarification_handler):
        """Test detection of missing date range for trend analysis."""
        result = clarification_handler.needs_clarification(
            query="show recent workshops",
            entities={"workshops": True},
            intent="analysis",
        )

        assert result is not None
        assert result["type"] == "clarification_needed"
        # Could be missing_location or ambiguous_date depending on priority
        assert result["issue_type"] in ["missing_location", "ambiguous_date"]

    def test_missing_status_detected(self, clarification_handler):
        """Test detection of missing status for project query."""
        result = clarification_handler.needs_clarification(
            query="show projects",
            entities={"projects": True, "location": "Region IX"},
            intent="data_query",
        )

        # Location is present, might detect missing status
        # Depends on rule priority
        if result:
            assert result["type"] == "clarification_needed"

    def test_general_intent_no_clarification(self, clarification_handler):
        """Test that general intents don't trigger clarification."""
        result = clarification_handler.needs_clarification(
            query="hello", entities={}, intent="general"
        )

        assert result is None

    def test_help_intent_no_clarification(self, clarification_handler):
        """Test that help intents don't trigger clarification."""
        result = clarification_handler.needs_clarification(
            query="how do I create a workshop?", entities={"create": True}, intent="help"
        )

        assert result is None


class TestClarificationDialogGeneration:
    """Test clarification dialog generation."""

    def test_generate_missing_location_dialog(self, clarification_handler):
        """Test generation of location clarification dialog."""
        dialog = clarification_handler.generate_clarification_dialog(
            issue_type="missing_location",
            context={
                "query": "communities",
                "entities": {"communities": True},
                "intent": "data_query",
            },
        )

        assert dialog["type"] == "clarification_needed"
        assert dialog["issue_type"] == "missing_location"
        assert dialog["message"] == "Which region would you like to know about?"
        assert len(dialog["options"]) == 5
        assert dialog["session_id"]
        assert dialog["clarification_id"]
        assert dialog["priority"] == "high"

        # Check options structure
        for option in dialog["options"]:
            assert "label" in option
            assert "value" in option
            assert "icon" in option

    def test_generate_date_range_dialog(self, clarification_handler):
        """Test generation of date range clarification dialog."""
        dialog = clarification_handler.generate_clarification_dialog(
            issue_type="ambiguous_date",
            context={
                "query": "recent assessments",
                "entities": {},
                "intent": "analysis",
            },
        )

        assert dialog["type"] == "clarification_needed"
        assert dialog["issue_type"] == "ambiguous_date"
        assert "time period" in dialog["message"].lower()
        assert len(dialog["options"]) == 4  # Last 30 days, 3 months, year, all time

    def test_session_id_uniqueness(self, clarification_handler):
        """Test that each dialog gets a unique session ID."""
        dialog1 = clarification_handler.generate_clarification_dialog(
            issue_type="missing_location",
            context={"query": "test1", "entities": {}, "intent": "data_query"},
        )

        dialog2 = clarification_handler.generate_clarification_dialog(
            issue_type="missing_location",
            context={"query": "test2", "entities": {}, "intent": "data_query"},
        )

        assert dialog1["session_id"] != dialog2["session_id"]
        assert dialog1["clarification_id"] != dialog2["clarification_id"]


class TestContextStorage:
    """Test clarification context storage and retrieval."""

    def test_store_and_retrieve_context(self, clarification_handler, clear_cache):
        """Test storing and retrieving clarification context."""
        session_id = "test-session-123"
        context = {
            "original_query": "communities fishing",
            "entities": {"livelihood": "fishing"},
            "intent": "data_query",
            "issue_type": "missing_location",
        }

        # Store context
        clarification_handler.store_clarification_context(session_id, context)

        # Retrieve context
        retrieved = clarification_handler.get_clarification_context(session_id)

        assert retrieved is not None
        assert retrieved["original_query"] == context["original_query"]
        assert retrieved["entities"] == context["entities"]
        assert retrieved["intent"] == context["intent"]
        assert retrieved["issue_type"] == context["issue_type"]

    def test_retrieve_nonexistent_context(self, clarification_handler, clear_cache):
        """Test retrieving context that doesn't exist."""
        result = clarification_handler.get_clarification_context("nonexistent-session")

        assert result is None

    def test_clear_context(self, clarification_handler, clear_cache):
        """Test clearing clarification context."""
        session_id = "test-session-456"
        context = {"query": "test", "entities": {}}

        # Store context
        clarification_handler.store_clarification_context(session_id, context)

        # Verify it exists
        assert clarification_handler.get_clarification_context(session_id) is not None

        # Clear context
        clarification_handler.clear_clarification_context(session_id)

        # Verify it's gone
        assert clarification_handler.get_clarification_context(session_id) is None

    @pytest.mark.django_db
    def test_context_ttl(self, clarification_handler, clear_cache):
        """Test that context expires after TTL."""
        session_id = "test-session-ttl"
        context = {"query": "test", "entities": {}}

        # Store with very short TTL
        with patch.object(
            clarification_handler, "CLARIFICATION_TTL", 1
        ):  # 1 second TTL
            clarification_handler.store_clarification_context(session_id, context)

            # Should exist immediately
            assert (
                clarification_handler.get_clarification_context(session_id) is not None
            )

            # Wait for expiration
            import time

            time.sleep(2)

            # Should be gone
            assert clarification_handler.get_clarification_context(session_id) is None


class TestClarificationApplication:
    """Test applying user clarification choices."""

    def test_apply_location_clarification(self, clarification_handler, clear_cache):
        """Test applying location clarification choice."""
        session_id = "test-session-789"
        original_query = "communities fishing"

        # Store context
        context = {
            "original_query": original_query,
            "entities": {"livelihood": "fishing"},
            "intent": "data_query",
            "issue_type": "missing_location",
        }
        clarification_handler.store_clarification_context(session_id, context)

        # Apply clarification
        result = clarification_handler.apply_clarification(
            original_query=original_query,
            user_choice={"value": "region_ix", "issue_type": "missing_location"},
            session_id=session_id,
        )

        assert result["refined_query"] == "communities fishing in Region IX"
        # The entity_key 'location' gets the choice value, not the mapped location
        assert result["entities"]["location"] == "region_ix"
        assert "location" in result["entities"]

    def test_apply_date_clarification(self, clarification_handler, clear_cache):
        """Test applying date range clarification choice."""
        session_id = "test-session-date"
        original_query = "recent workshops"

        # Store context
        context = {
            "original_query": original_query,
            "entities": {"workshops": True},
            "intent": "data_query",
            "issue_type": "ambiguous_date",
        }
        clarification_handler.store_clarification_context(session_id, context)

        # Apply clarification
        result = clarification_handler.apply_clarification(
            original_query=original_query,
            user_choice={"value": "last_30_days", "issue_type": "ambiguous_date"},
            session_id=session_id,
        )

        assert "in the last 30 days" in result["refined_query"]
        assert result["entities"]["date_range"] == "last_30_days"
        assert "date_range_data" in result["entities"]
        assert result["entities"]["date_range_data"]["days"] == 30

    def test_apply_status_clarification(self, clarification_handler, clear_cache):
        """Test applying status clarification choice."""
        session_id = "test-session-status"
        original_query = "show projects"

        # Store context
        context = {
            "original_query": original_query,
            "entities": {"projects": True},
            "intent": "data_query",
            "issue_type": "missing_status",
        }
        clarification_handler.store_clarification_context(session_id, context)

        # Apply clarification
        result = clarification_handler.apply_clarification(
            original_query=original_query,
            user_choice={"value": "active", "issue_type": "missing_status"},
            session_id=session_id,
        )

        assert "active" in result["refined_query"]
        assert result["entities"]["status"] == "active"

    def test_apply_all_option(self, clarification_handler, clear_cache):
        """Test applying 'all' option doesn't add location to query."""
        session_id = "test-session-all"
        original_query = "communities"

        # Store context
        context = {
            "original_query": original_query,
            "entities": {},
            "intent": "data_query",
            "issue_type": "missing_location",
        }
        clarification_handler.store_clarification_context(session_id, context)

        # Apply "all" clarification
        result = clarification_handler.apply_clarification(
            original_query=original_query,
            user_choice={"value": "all", "issue_type": "missing_location"},
            session_id=session_id,
        )

        # Query should not have location appended
        assert result["refined_query"] == original_query
        assert result["entities"]["location"] == "all"


class TestMultiTurnClarification:
    """Test multi-turn clarification flows."""

    def test_multiple_clarifications_needed(self, clarification_handler, clear_cache):
        """Test detecting multiple clarifications needed sequentially."""
        # First query - missing location
        result1 = clarification_handler.needs_clarification(
            query="communities", entities={}, intent="data_query"
        )

        assert result1 is not None
        # High priority rule (missing_location) should be detected first
        assert result1["issue_type"] == "missing_location"

    def test_sequential_clarifications(self, clarification_handler, clear_cache):
        """Test applying clarifications sequentially."""
        session_id = "test-multi-turn"
        original_query = "communities"

        # Store initial context
        context = {
            "original_query": original_query,
            "entities": {},
            "intent": "data_query",
            "issue_type": "missing_location",
        }
        clarification_handler.store_clarification_context(session_id, context)

        # Apply first clarification (location)
        result1 = clarification_handler.apply_clarification(
            original_query=original_query,
            user_choice={"value": "region_ix", "issue_type": "missing_location"},
            session_id=session_id,
        )

        refined_query = result1["refined_query"]
        entities = result1["entities"]

        # Check if more clarification needed
        if result1.get("needs_more_clarification"):
            next_clarification = result1.get("next_clarification")
            assert next_clarification is not None
            assert next_clarification["type"] == "clarification_needed"

    def test_no_more_clarification_after_all_resolved(
        self, clarification_handler, clear_cache
    ):
        """Test that no clarification needed when all entities present."""
        result = clarification_handler.needs_clarification(
            query="communities in Region IX with fishing livelihood",
            entities={
                "communities": True,
                "location": "Region IX",
                "livelihood": "fishing",
            },
            intent="data_query",
        )

        # Should not need clarification
        assert result is None


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_invalid_issue_type(self, clarification_handler):
        """Test handling of invalid issue type."""
        dialog = clarification_handler.generate_clarification_dialog(
            issue_type="invalid_type",
            context={"query": "test", "entities": {}, "intent": "data_query"},
        )

        assert dialog == {}

    def test_empty_query(self, clarification_handler):
        """Test handling of empty query."""
        result = clarification_handler.needs_clarification(
            query="", entities={}, intent="data_query"
        )

        assert result is None

    def test_none_entities(self, clarification_handler):
        """Test handling of None entities."""
        result = clarification_handler.needs_clarification(
            query="test", entities=None, intent="data_query"
        )

        # Should handle gracefully (no crash)
        # Result depends on rule conditions

    def test_apply_clarification_without_stored_context(
        self, clarification_handler, clear_cache
    ):
        """Test applying clarification when context doesn't exist."""
        result = clarification_handler.apply_clarification(
            original_query="test",
            user_choice={"value": "region_ix", "issue_type": "missing_location"},
            session_id="nonexistent-session",
        )

        # Should return original query unchanged
        assert result["refined_query"] == "test"
        assert result["entities"] == {}
        assert result["needs_more_clarification"] is False


class TestSingletonInstance:
    """Test singleton pattern for clarification handler."""

    def test_get_singleton_instance(self):
        """Test that get_clarification_handler returns singleton."""
        handler1 = get_clarification_handler()
        handler2 = get_clarification_handler()

        assert handler1 is handler2

    def test_singleton_preserves_state(self):
        """Test that singleton preserves state across calls."""
        handler1 = get_clarification_handler()
        handler1.test_attribute = "test_value"

        handler2 = get_clarification_handler()

        assert hasattr(handler2, "test_attribute")
        assert handler2.test_attribute == "test_value"

        # Clean up
        delattr(handler2, "test_attribute")


class TestPriorityOrdering:
    """Test clarification priority ordering."""

    def test_high_priority_first(self, clarification_handler):
        """Test that high priority clarifications are detected first."""
        # Query that could trigger multiple clarifications
        result = clarification_handler.needs_clarification(
            query="show communities", entities={}, intent="data_query"
        )

        assert result is not None
        # Missing location is high priority
        assert result["priority"] == "high"
        assert result["issue_type"] == "missing_location"

    def test_priority_score_calculation(self, clarification_handler):
        """Test priority score calculation."""
        assert clarification_handler._priority_score("high") == 3
        assert clarification_handler._priority_score("medium") == 2
        assert clarification_handler._priority_score("low") == 1
        assert clarification_handler._priority_score("unknown") == 0


# Performance Tests (Optional - requires pytest-benchmark)
# Uncomment if pytest-benchmark is installed: pip install pytest-benchmark
#
# class TestPerformance:
#     """Test performance of clarification operations."""
#
#     def test_detection_performance(self, clarification_handler, benchmark):
#         """Test performance of clarification detection."""
#
#         def detect():
#             return clarification_handler.needs_clarification(
#                 query="communities", entities={}, intent="data_query"
#             )
#
#         # Should complete in < 50ms
#         result = benchmark(detect)
#         assert result is not None
#
#     def test_dialog_generation_performance(self, clarification_handler, benchmark):
#         """Test performance of dialog generation."""
#
#         def generate():
#             return clarification_handler.generate_clarification_dialog(
#                 issue_type="missing_location",
#                 context={"query": "test", "entities": {}, "intent": "data_query"},
#             )
#
#         # Should complete in < 50ms
#         result = benchmark(generate)
#         assert result["type"] == "clarification_needed"
#
#     @pytest.mark.django_db
#     def test_context_storage_performance(
#         self, clarification_handler, benchmark, clear_cache
#     ):
#         """Test performance of context storage."""
#         context = {
#             "query": "test",
#             "entities": {"test": True},
#             "intent": "data_query",
#         }
#
#         def store():
#             clarification_handler.store_clarification_context(
#                 "test-session-perf", context
#             )
#
#         # Should complete in < 10ms
#         benchmark(store)
