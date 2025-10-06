"""
Clarification Handler for OBCMS Chat System

Detects ambiguous queries and asks structured clarification questions.
NO AI FALLBACK - uses rule-based detection and predefined options.
"""

import json
import logging
import uuid
from typing import Dict, List, Optional

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


def _check_missing_location(entities, intent, query=""):
    """Check if location is missing for queries that need it."""
    if intent not in ["data_query", "analysis"]:
        return False

    # Handle both list and dict entities
    if isinstance(entities, dict):
        has_location = "location" in entities
        entity_list = list(entities.keys())
    elif isinstance(entities, (list, set)):
        has_location = "location" in entities
        entity_list = list(entities)
    else:
        return False

    # Check for aggregate/count queries that don't need location
    query_lower = query.lower()
    aggregate_patterns = [
        "how many provinces",
        "how many regions",
        "how many municipalities",
        "how many barangays",
        "total provinces",
        "total regions",
        "total municipalities",
        "total barangays",
        "count of provinces",
        "count of regions",
        "count of municipalities",
        "list provinces",
        "list regions",
        "list municipalities",
    ]

    # If it's an aggregate query about administrative divisions, don't require location
    if any(pattern in query_lower for pattern in aggregate_patterns):
        return False

    # Check if any relevant keywords present (in entities OR query)
    relevant_keywords = ["communities", "workshops", "projects"]
    has_relevant = any(kw in entity_list for kw in relevant_keywords) or any(
        kw in query_lower for kw in relevant_keywords
    )

    return not has_location and has_relevant


def _check_ambiguous_date(entities, intent):
    """Check if date range is ambiguous."""
    if intent not in ["data_query", "analysis"]:
        return False

    # Handle both list and dict entities
    if isinstance(entities, dict):
        has_date = "date_range" in entities
        entity_str = str(entities).lower()
    elif isinstance(entities, (list, set)):
        has_date = "date_range" in entities
        entity_str = " ".join(str(e).lower() for e in entities)
    else:
        return False

    # Check for date-related terms
    date_terms = ["recent", "latest", "trend", "analysis"]
    has_date_terms = any(term in entity_str for term in date_terms)

    return not has_date and has_date_terms


def _check_missing_status(entities, intent):
    """Check if status is missing for project queries."""
    if intent != "data_query":
        return False

    # Handle both list and dict entities
    if isinstance(entities, dict):
        has_status = "status" in entities
        has_projects = "projects" in entities
    elif isinstance(entities, (list, set)):
        has_status = "status" in entities
        has_projects = "projects" in entities
    else:
        return False

    return has_projects and not has_status


def _check_ambiguous_community_type(entities, intent):
    """Check if community type filter is ambiguous."""
    if intent != "data_query":
        return False

    # Handle both list and dict entities
    if isinstance(entities, dict):
        has_communities = "communities" in entities
        has_livelihood = "livelihood" in entities
        has_ethnic = "ethnolinguistic_group" in entities
    elif isinstance(entities, (list, set)):
        has_communities = "communities" in entities
        has_livelihood = "livelihood" in entities
        has_ethnic = "ethnolinguistic_group" in entities
    else:
        return False

    return has_communities and not has_livelihood and not has_ethnic


class ClarificationHandler:
    """
    Handle query clarification for ambiguous user input.

    Features:
    - Detect missing entities (location, date range, etc.)
    - Generate structured clarification questions
    - Store/retrieve clarification context
    - Apply user selections to refine queries
    - Support multi-turn clarifications
    """

    # Clarification rules with conditions and options
    CLARIFICATION_RULES = {
        "missing_location": {
            "condition": lambda entities, intent, query="": _check_missing_location(entities, intent, query),
            "question": "Which region would you like to know about?",
            "options": [
                {
                    "label": "Region IX (Zamboanga Peninsula)",
                    "value": "region_ix",
                    "icon": "map-marker-alt",
                },
                {
                    "label": "Region X (Northern Mindanao)",
                    "value": "region_x",
                    "icon": "map-marker-alt",
                },
                {
                    "label": "Region XI (Davao Region)",
                    "value": "region_xi",
                    "icon": "map-marker-alt",
                },
                {
                    "label": "Region XII (SOCCSKSARGEN)",
                    "value": "region_xii",
                    "icon": "map-marker-alt",
                },
                {"label": "All regions", "value": "all", "icon": "globe"},
            ],
            "priority": "high",
            "entity_key": "location",
        },
        "ambiguous_date": {
            "condition": lambda entities, intent, query="": _check_ambiguous_date(entities, intent),
            "question": "Which time period are you interested in?",
            "options": [
                {"label": "Last 30 days", "value": "last_30_days", "icon": "calendar"},
                {
                    "label": "Last 3 months",
                    "value": "last_3_months",
                    "icon": "calendar",
                },
                {"label": "This year (2025)", "value": "this_year", "icon": "calendar"},
                {"label": "All time", "value": "all_time", "icon": "calendar-alt"},
            ],
            "priority": "medium",
            "entity_key": "date_range",
        },
        "missing_status": {
            "condition": lambda entities, intent, query="": _check_missing_status(entities, intent),
            "question": "Which project status?",
            "options": [
                {"label": "Active projects", "value": "active", "icon": "check-circle"},
                {
                    "label": "Completed projects",
                    "value": "completed",
                    "icon": "flag-checkered",
                },
                {"label": "All projects", "value": "all", "icon": "list"},
            ],
            "priority": "low",
            "entity_key": "status",
        },
        "ambiguous_community_type": {
            "condition": lambda entities, intent, query="": _check_ambiguous_community_type(entities, intent),
            "question": "What type of communities are you looking for?",
            "options": [
                {
                    "label": "By livelihood (fishing, farming, etc.)",
                    "value": "livelihood_filter",
                    "icon": "briefcase",
                },
                {
                    "label": "By ethnolinguistic group",
                    "value": "ethnic_filter",
                    "icon": "users",
                },
                {"label": "All communities", "value": "all", "icon": "th-large"},
            ],
            "priority": "medium",
            "entity_key": "filter_type",
        },
    }

    # Location mapping for refinement
    LOCATION_MAPPING = {
        "region_ix": "Region IX",
        "region_x": "Region X",
        "region_xi": "Region XI",
        "region_xii": "Region XII",
        "all": None,
    }

    # Date range mapping
    DATE_RANGE_MAPPING = {
        "last_30_days": {"days": 30, "label": "in the last 30 days"},
        "last_3_months": {"days": 90, "label": "in the last 3 months"},
        "this_year": {"year": 2025, "label": "this year"},
        "all_time": {"all": True, "label": ""},
    }

    # Status mapping
    STATUS_MAPPING = {
        "active": {"value": "active", "label": "active"},
        "completed": {"value": "completed", "label": "completed"},
        "all": {"value": None, "label": ""},
    }

    # Cache TTL for clarification sessions (30 minutes)
    CLARIFICATION_TTL = 1800

    def __init__(self):
        """Initialize clarification handler."""
        self.cache_prefix = "chat_clarification"

    def needs_clarification(
        self, query: str, entities: Dict, intent: str
    ) -> Optional[Dict]:
        """
        Check if query needs clarification.

        Args:
            query: Original user query
            entities: Extracted entities (can be dict or list)
            intent: Classified intent

        Returns:
            Clarification dialog dict if needed, None otherwise

        Example:
            >>> handler = ClarificationHandler()
            >>> result = handler.needs_clarification(
            ...     "communities fishing",
            ...     {"livelihood": "fishing"},
            ...     "data_query"
            ... )
            >>> print(result["question"])
            "Which region would you like to know about?"
        """
        # Check each rule in priority order
        sorted_rules = sorted(
            self.CLARIFICATION_RULES.items(),
            key=lambda x: self._priority_score(x[1].get("priority", "low")),
            reverse=True,
        )

        for issue_type, rule in sorted_rules:
            try:
                condition = rule["condition"]
                # Pass both entities and query to condition for context
                if condition(entities, intent, query):
                    logger.info(
                        f"Clarification needed: {issue_type} for query: {query}"
                    )
                    return self.generate_clarification_dialog(
                        issue_type=issue_type,
                        context={
                            "query": query,
                            "entities": entities,
                            "intent": intent,
                        },
                    )
            except Exception as e:
                logger.error(f"Error checking clarification rule {issue_type}: {e}")
                continue

        return None

    def generate_clarification_dialog(
        self, issue_type: str, context: Dict
    ) -> Dict[str, any]:
        """
        Generate clarification dialog for a specific issue.

        Args:
            issue_type: Type of clarification needed
            context: Query context (query, entities, intent)

        Returns:
            Clarification dialog dictionary

        Example:
            >>> handler = ClarificationHandler()
            >>> dialog = handler.generate_clarification_dialog(
            ...     "missing_location",
            ...     {"query": "communities", "entities": {}, "intent": "data_query"}
            ... )
            >>> print(dialog["type"])
            "clarification_needed"
        """
        rule = self.CLARIFICATION_RULES.get(issue_type)
        if not rule:
            logger.error(f"Unknown clarification type: {issue_type}")
            return {}

        # Generate unique session ID
        session_id = str(uuid.uuid4())
        clarification_id = f"{issue_type}_{session_id[:8]}"

        # Store clarification context
        self.store_clarification_context(
            session_id=session_id,
            context={
                "original_query": context.get("query"),
                "entities": context.get("entities", {}),
                "intent": context.get("intent"),
                "issue_type": issue_type,
                "clarification_id": clarification_id,
            },
        )

        return {
            "type": "clarification_needed",
            "message": rule["question"],
            "options": rule["options"],
            "original_query": context.get("query"),
            "session_id": session_id,
            "clarification_id": clarification_id,
            "issue_type": issue_type,
            "priority": rule.get("priority", "medium"),
        }

    def apply_clarification(
        self, original_query: str, user_choice: Dict, session_id: str
    ) -> Dict[str, any]:
        """
        Apply user's clarification choice to refine the query.

        Args:
            original_query: Original user query
            user_choice: User's selected option (e.g., {"value": "region_ix", "issue_type": "missing_location"})
            session_id: Session ID for context retrieval

        Returns:
            Dictionary with:
                - refined_query: Updated query string
                - entities: Updated entities dict
                - needs_more_clarification: Boolean

        Example:
            >>> handler = ClarificationHandler()
            >>> result = handler.apply_clarification(
            ...     "communities fishing",
            ...     {"value": "region_ix", "issue_type": "missing_location"},
            ...     "session-123"
            ... )
            >>> print(result["refined_query"])
            "communities fishing in Region IX"
        """
        # Retrieve stored context
        context = self.get_clarification_context(session_id)
        if not context:
            logger.warning(f"No context found for session: {session_id}")
            return {
                "refined_query": original_query,
                "entities": {},
                "needs_more_clarification": False,
            }

        issue_type = user_choice.get("issue_type") or context.get("issue_type")
        choice_value = user_choice.get("value")

        # Get original entities
        entities = context.get("entities", {}).copy()

        # Apply refinement based on issue type
        refined_query = original_query
        entity_key = self.CLARIFICATION_RULES[issue_type].get("entity_key")

        if issue_type == "missing_location":
            location = self.LOCATION_MAPPING.get(choice_value)
            if location:
                refined_query = f"{original_query} in {location}"
                entities["location"] = location
            entities[entity_key] = choice_value

        elif issue_type == "ambiguous_date":
            date_info = self.DATE_RANGE_MAPPING.get(choice_value, {})
            label = date_info.get("label", "")
            if label:
                refined_query = f"{original_query} {label}"
            entities[entity_key] = choice_value
            entities["date_range_data"] = date_info

        elif issue_type == "missing_status":
            status_info = self.STATUS_MAPPING.get(choice_value, {})
            label = status_info.get("label", "")
            if label and label != "":
                refined_query = f"{label} {original_query}"
            entities[entity_key] = choice_value

        elif issue_type == "ambiguous_community_type":
            entities[entity_key] = choice_value
            if choice_value != "all":
                refined_query = f"{original_query} ({choice_value.replace('_', ' ')})"

        # Check if more clarification needed
        intent = context.get("intent", "data_query")
        needs_more = self.needs_clarification(refined_query, entities, intent)

        # Clean up session if no more clarification needed
        if not needs_more:
            self.clear_clarification_context(session_id)

        logger.info(
            f"Applied clarification: {original_query} -> {refined_query} "
            f"(entities: {entities})"
        )

        return {
            "refined_query": refined_query,
            "entities": entities,
            "needs_more_clarification": bool(needs_more),
            "next_clarification": needs_more,
        }

    def store_clarification_context(self, session_id: str, context: Dict) -> None:
        """
        Store clarification context in Redis cache.

        Args:
            session_id: Unique session identifier
            context: Context dictionary to store

        Example:
            >>> handler = ClarificationHandler()
            >>> handler.store_clarification_context(
            ...     "session-123",
            ...     {"query": "test", "entities": {}}
            ... )
        """
        cache_key = f"{self.cache_prefix}:{session_id}"
        try:
            cache.set(cache_key, json.dumps(context), timeout=self.CLARIFICATION_TTL)
            logger.debug(f"Stored clarification context: {cache_key}")
        except Exception as e:
            logger.error(f"Failed to store clarification context: {e}")

    def get_clarification_context(self, session_id: str) -> Optional[Dict]:
        """
        Retrieve clarification context from Redis cache.

        Args:
            session_id: Session identifier

        Returns:
            Context dictionary or None if not found

        Example:
            >>> handler = ClarificationHandler()
            >>> context = handler.get_clarification_context("session-123")
        """
        cache_key = f"{self.cache_prefix}:{session_id}"
        try:
            data = cache.get(cache_key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Failed to retrieve clarification context: {e}")

        return None

    def clear_clarification_context(self, session_id: str) -> None:
        """
        Clear clarification context from cache.

        Args:
            session_id: Session identifier

        Example:
            >>> handler = ClarificationHandler()
            >>> handler.clear_clarification_context("session-123")
        """
        cache_key = f"{self.cache_prefix}:{session_id}"
        try:
            cache.delete(cache_key)
            logger.debug(f"Cleared clarification context: {cache_key}")
        except Exception as e:
            logger.error(f"Failed to clear clarification context: {e}")

    def _priority_score(self, priority: str) -> int:
        """Convert priority string to numeric score."""
        priority_map = {"high": 3, "medium": 2, "low": 1}
        return priority_map.get(priority, 0)


# Singleton instance
_clarification_handler = None


def get_clarification_handler() -> ClarificationHandler:
    """Get singleton clarification handler instance."""
    global _clarification_handler
    if _clarification_handler is None:
        _clarification_handler = ClarificationHandler()
    return _clarification_handler
