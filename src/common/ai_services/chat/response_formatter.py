"""
Response Formatter for Conversational AI

Formats query results into natural, conversational responses.
Handles different data types and creates follow-up suggestions.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """
    Format query results into natural language responses.

    Features:
    - Context-aware formatting
    - Data visualization suggestions
    - Follow-up question generation
    - Markdown support for rich formatting
    """

    def format_query_result(
        self,
        result: Any,
        result_type: str,
        original_question: str,
        entities: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Format query result into conversational response.

        Args:
            result: Query result from QueryExecutor
            result_type: Type of result (count, list, aggregate)
            original_question: User's original question
            entities: Detected entities from the query

        Returns:
            Dictionary with:
                - response: Natural language response text
                - data: Structured data for UI display
                - suggestions: Follow-up questions
                - visualization: Suggested visualization type
        """
        entities = entities or []

        # Route to appropriate formatter
        if result_type == 'municipality_city_breakdown':
            return self._format_municipality_city_breakdown(result, original_question, entities)
        elif isinstance(result, int):
            return self._format_count(result, original_question, entities)
        elif isinstance(result, dict):
            return self._format_aggregate(result, original_question, entities)
        elif isinstance(result, list):
            return self._format_list(result, original_question, entities)
        else:
            return self._format_generic(result, original_question)

    def _format_count(
        self, count: int, question: str, entities: List[str]
    ) -> Dict[str, Any]:
        """Format count results."""
        # Determine entity type for natural response from question
        question_lower = question.lower()
        if 'province' in question_lower:
            entity = 'province'
        elif 'region' in question_lower:
            entity = 'region'
        elif 'municipality' in question_lower or 'municipalities' in question_lower:
            entity = 'municipality'
        elif 'barangay' in question_lower:
            entity = 'barangay'
        elif 'communit' in question_lower:
            entity = 'community'
        elif entities and isinstance(entities, list) and len(entities) > 0:
            entity = entities[0]
        else:
            entity = "items"
        entity_name = self._pluralize(entity, count)

        # Build natural response
        if count == 0:
            text = f"There are no {entity_name} matching your query."
        elif count == 1:
            text = f"There is 1 {entity.rstrip('s')} matching your query."
        else:
            text = f"There are {count:,} {entity_name} matching your query."

        # Generate suggestions
        suggestions = self._generate_count_suggestions(entity, count)

        return {
            "response": text,
            "data": {"count": count, "entity": entity},
            "suggestions": suggestions,
            "visualization": "number" if count < 10 else "bar_chart",
        }

    def _format_municipality_city_breakdown(
        self, data: Dict, question: str, entities: List[str]
    ) -> Dict[str, Any]:
        """Format municipality and city breakdown results."""
        municipalities = data.get('municipalities', 0)
        cities = data.get('cities', 0)
        total = municipalities + cities

        # Build natural response
        if total == 0:
            text = "There are no municipalities or cities in the system."
        else:
            text = f"There are {municipalities:,} municipalities and {cities:,} cities."

        # Generate suggestions
        suggestions = [
            "Show me the list of municipalities",
            "Show me the list of cities",
            "Which provinces have the most municipalities?",
            "Show municipalities by region"
        ]

        return {
            "response": text,
            "data": {
                "municipalities": municipalities,
                "cities": cities,
                "total": total
            },
            "suggestions": suggestions,
            "visualization": "pie_chart",
        }

    def _format_aggregate(
        self, aggregate: Dict, question: str, entities: List[str]
    ) -> Dict[str, Any]:
        """Format aggregate results (sum, avg, etc.)."""
        lines = []

        for key, value in aggregate.items():
            # Parse aggregate key (e.g., 'total_population__sum')
            parts = key.split("__")
            field_name = parts[0].replace("_", " ").title()
            agg_type = parts[1].upper() if len(parts) > 1 else "VALUE"

            # Format value
            if isinstance(value, float):
                formatted_value = f"{value:,.2f}"
            elif isinstance(value, int):
                formatted_value = f"{value:,}"
            else:
                formatted_value = str(value)

            lines.append(f"**{field_name} ({agg_type})**: {formatted_value}")

        text = "Here are the aggregate results:\n\n" + "\n".join(lines)

        # Generate suggestions
        entity = entities[0] if entities else "data"
        suggestions = [
            f"Show me the detailed breakdown",
            f"Compare this across regions",
            f"What's the trend over time?",
        ]

        return {
            "response": text,
            "data": aggregate,
            "suggestions": suggestions,
            "visualization": "metric_cards",
        }

    def _format_list(
        self, items: List[Dict], question: str, entities: List[str]
    ) -> Dict[str, Any]:
        """Format list results."""
        count = len(items)
        entity = entities[0] if entities else "results"
        entity_name = self._pluralize(entity, count)

        # Build intro
        if count == 0:
            text = f"No {entity_name} found matching your query."
            suggestions = [f"Try a broader search", "Show me all {entity}"]
            return {
                "response": text,
                "data": {"items": [], "count": 0},
                "suggestions": suggestions,
                "visualization": None,
            }

        # Limit preview items
        preview_count = min(count, 5)
        preview_items = items[:preview_count]

        # Build response
        text = f"Found {count:,} {entity_name}. "

        if count > preview_count:
            text += f"Here are the first {preview_count}:\n\n"
        else:
            text += "Here they are:\n\n"

        # Format each item
        for i, item in enumerate(preview_items, 1):
            text += self._format_list_item(i, item, entity)

        if count > preview_count:
            text += f"\n*Showing {preview_count} of {count:,} total results*"

        # Generate suggestions
        suggestions = self._generate_list_suggestions(entity, count, items)

        return {
            "response": text,
            "data": {"items": items, "count": count, "preview_count": preview_count},
            "suggestions": suggestions,
            "visualization": "table" if count > 10 else "list",
        }

    def _format_list_item(self, index: int, item: Dict, entity: str) -> str:
        """Format a single list item."""
        # Try to find meaningful fields to display
        display_fields = []

        # Common field names to prioritize
        priority_fields = ["name", "title", "description", "status", "date"]

        # Add priority fields first
        for field in priority_fields:
            if field in item and item[field]:
                value = item[field]
                # Truncate long values
                if isinstance(value, str) and len(value) > 100:
                    value = value[:97] + "..."
                display_fields.append(f"**{field.title()}**: {value}")

        # If no priority fields, use first few fields
        if not display_fields:
            for key, value in list(item.items())[:3]:
                if key != "id" and value:
                    if isinstance(value, str) and len(value) > 100:
                        value = value[:97] + "..."
                    display_fields.append(
                        f"**{key.replace('_', ' ').title()}**: {value}"
                    )

        item_text = f"{index}. " + " | ".join(display_fields) + "\n"
        return item_text

    def _format_generic(self, result: Any, question: str) -> Dict[str, Any]:
        """Fallback formatter for unknown result types."""
        text = f"Here's what I found:\n\n{str(result)}"

        return {
            "response": text,
            "data": {"result": str(result)},
            "suggestions": ["Can you clarify your question?", "Show me more details"],
            "visualization": None,
        }

    def _generate_count_suggestions(self, entity: str, count: int) -> List[str]:
        """Generate follow-up suggestions for count queries."""
        suggestions = []

        if count > 0:
            suggestions.append(f"Show me the list of {entity}")
            suggestions.append(f"Break down by region")
            suggestions.append(f"Compare with other areas")

        suggestions.append(f"What are the needs in these {entity}?")

        return suggestions[:3]  # Limit to 3

    def _generate_list_suggestions(
        self, entity: str, count: int, items: List[Dict]
    ) -> List[str]:
        """Generate follow-up suggestions for list queries."""
        suggestions = []

        if count > 5:
            suggestions.append(f"Show me more details")

        suggestions.append(f"Filter these {entity}")
        suggestions.append(f"Analyze these results")

        # Try to suggest entity-specific actions
        if "communities" in entity:
            suggestions.append("Show MANA assessments for these")
        elif "workshops" in entity or "mana" in entity:
            suggestions.append("What were the key findings?")
        elif "policies" in entity:
            suggestions.append("Which ones are approved?")
        elif "projects" in entity or "ppa" in entity:
            suggestions.append("What's the total budget?")

        return suggestions[:3]  # Limit to 3

    def _pluralize(self, word: str, count: int) -> str:
        """Simple pluralization."""
        if count == 1:
            return word.rstrip("s")
        elif word.endswith("s"):
            return word
        else:
            return word + "s"

    def format_error(self, error_message: str, query: str) -> Dict[str, Any]:
        """Format error message in a helpful way."""
        text = "I encountered an issue processing your request:\n\n"
        text += f"*{error_message}*\n\n"
        text += "You can try:\n"
        text += "- Rephrasing your question\n"
        text += "- Being more specific\n"
        text += "- Asking for help with available commands"

        return {
            "response": text,
            "data": {"error": error_message, "query": query},
            "suggestions": [
                "What can you help me with?",
                "Show me example queries",
                "Help with search",
            ],
            "visualization": None,
        }

    def format_help(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """Format comprehensive help response."""
        text = "**OBCMS AI Assistant - Quick Help**\n\n"
        text += "I can help you with:\n\n"

        text += "**📊 Data Queries**\n"
        text += "Ask about communities, assessments, and activities:\n"
        text += "- 'How many communities are in Region IX?'\n"
        text += "- 'Show me MANA assessments in Zamboanga'\n"
        text += "- 'List coordination workshops this month'\n"
        text += "- 'Count active policy recommendations'\n\n"

        text += "**📈 Analysis** (Coming Soon)\n"
        text += "- 'What are the top needs in Region IX?'\n"
        text += "- 'Analyze MANA trends by region'\n"
        text += "- 'Compare project completion rates'\n\n"

        text += "**🧭 Navigation**\n"
        text += "- 'Take me to the dashboard'\n"
        text += "- 'Open the MANA module'\n"
        text += "- 'Go to communities page'\n\n"

        text += "**💡 Tips:**\n"
        text += "- Use natural language - just ask!\n"
        text += "- Click any suggestion chip to try it\n"
        text += "- Be specific about locations or dates\n\n"

        text += "Try clicking one of the quick query chips below to get started!"

        return {
            "response": text,
            "data": {"topic": topic},
            "suggestions": [
                "How many communities are there?",
                "Show me recent assessments",
                "List coordination activities",
            ],
            "visualization": None,
        }

    def format_greeting(self) -> Dict[str, Any]:
        """Format greeting response."""
        text = "Hello! I'm the OBCMS AI Assistant.\n\n"
        text += "I can help you:\n"
        text += "- Find data about communities, workshops, and projects\n"
        text += "- Analyze trends and patterns\n"
        text += "- Navigate the system\n\n"
        text += "What would you like to know?"

        return {
            "response": text,
            "data": {},
            "suggestions": [
                "How many communities are in the system?",
                "Show me recent MANA assessments",
                "What are the top priorities?",
            ],
            "visualization": None,
        }

    # ============================================================================
    # ADVANCED FORMATTERS (Phase 2 Enhancements)
    # ============================================================================

    def format_count_response(
        self, count: int, entity_type: str, filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format count responses with contextual information.

        Args:
            count: Number of entities
            entity_type: Type of entity (communities, assessments, etc.)
            filters: Applied filters for context

        Returns:
            Formatted response string

        Example:
            >>> format_count_response(15, "communities", {"region": "Region IX"})
            "Found 15 communities in Region IX"
        """
        if count == 0:
            response = f"No {entity_type} found"
        elif count == 1:
            # Singularize entity type (simple approach)
            singular = entity_type
            if entity_type.endswith('ies'):
                # communities -> community, activities -> activity
                singular = entity_type[:-3] + 'y'
            elif entity_type.endswith('es'):
                # passes -> pass, classes -> class
                singular = entity_type[:-2]
            elif entity_type.endswith('s'):
                # items -> item, projects -> project
                singular = entity_type[:-1]
            response = f"Found 1 {singular}"
        else:
            response = f"Found {count:,} {entity_type}"

        # Add filter context
        if filters:
            filter_parts = []
            for key, value in filters.items():
                # Format key (remove underscores, capitalize)
                formatted_key = key.replace('_', ' ')
                filter_parts.append(f"{formatted_key}: {value}")

            if filter_parts:
                response += f" ({', '.join(filter_parts)})"

        return response

    def format_list_response(
        self,
        items: List[Dict[str, Any]],
        entity_type: str,
        format_type: str = "bulleted"
    ) -> str:
        """
        Format list responses as bulleted or numbered lists.

        Args:
            items: List of items to format
            entity_type: Type of entity
            format_type: "bulleted" or "numbered"

        Returns:
            Formatted list string

        Example:
            >>> items = [{"name": "Community A"}, {"name": "Community B"}]
            >>> format_list_response(items, "communities", "bulleted")
            "Communities (2):\n• Community A\n• Community B"
        """
        if not items:
            return f"No {entity_type} to display"

        count = len(items)
        response = f"{entity_type.title()} ({count}):\n"

        for i, item in enumerate(items, 1):
            # Try to extract display value
            display_value = (
                item.get('name') or
                item.get('title') or
                item.get('description') or
                str(item)
            )

            # Truncate if too long
            if isinstance(display_value, str) and len(display_value) > 80:
                display_value = display_value[:77] + "..."

            # Format line
            if format_type == "numbered":
                response += f"{i}. {display_value}\n"
            else:  # bulleted
                response += f"• {display_value}\n"

        return response.rstrip()

    def format_aggregate_response(
        self,
        data: Dict[str, Any],
        metric: str
    ) -> str:
        """
        Format aggregate/statistical summary responses.

        Args:
            data: Dictionary of aggregate values
            metric: Metric being aggregated

        Returns:
            Formatted aggregate string

        Example:
            >>> data = {"total": 150000, "average": 5000, "min": 1000, "max": 10000}
            >>> format_aggregate_response(data, "budget")
            "Budget Statistics:\nTotal: ₱150,000\nAverage: ₱5,000\nMin: ₱1,000\nMax: ₱10,000"
        """
        response = f"{metric.title()} Statistics:\n"

        # Define formatting for known metrics
        currency_metrics = ['budget', 'funding', 'cost', 'amount', 'allocation']
        is_currency = any(term in metric.lower() for term in currency_metrics)

        for key, value in data.items():
            # Format key
            formatted_key = key.replace('_', ' ').title()

            # Format value
            if is_currency and isinstance(value, (int, float)):
                formatted_value = f"₱{value:,.2f}" if isinstance(value, float) else f"₱{value:,}"
            elif isinstance(value, float):
                formatted_value = f"{value:,.2f}"
            elif isinstance(value, int):
                formatted_value = f"{value:,}"
            else:
                formatted_value = str(value)

            response += f"{formatted_key}: {formatted_value}\n"

        return response.rstrip()

    def format_trend_response(
        self,
        data: List[Dict[str, Any]],
        time_period: str
    ) -> str:
        """
        Format trend analysis responses.

        Args:
            data: List of data points with time series
            time_period: Time period being analyzed

        Returns:
            Formatted trend string

        Example:
            >>> data = [{"month": "Jan", "value": 10}, {"month": "Feb", "value": 15}]
            >>> format_trend_response(data, "monthly")
            "Trend Analysis (Monthly):\nJan: 10\nFeb: 15 (↑50%)"
        """
        if not data or len(data) < 2:
            return f"Insufficient data for {time_period} trend analysis"

        response = f"Trend Analysis ({time_period.title()}):\n"

        for i, point in enumerate(data):
            # Extract time and value
            time_label = (
                point.get('month') or
                point.get('date') or
                point.get('period') or
                f"Period {i+1}"
            )
            value = point.get('value') or point.get('count') or 0

            line = f"{time_label}: {value:,}"

            # Calculate change from previous period
            if i > 0:
                prev_value = data[i-1].get('value') or data[i-1].get('count') or 0
                if prev_value > 0:
                    change_pct = ((value - prev_value) / prev_value) * 100
                    arrow = "↑" if change_pct > 0 else "↓" if change_pct < 0 else "→"
                    line += f" ({arrow}{abs(change_pct):.1f}%)"

            response += line + "\n"

        return response.rstrip()

    def format_comparison_response(
        self,
        data1: Dict[str, Any],
        data2: Dict[str, Any],
        label1: str = "A",
        label2: str = "B"
    ) -> str:
        """
        Format side-by-side comparison responses.

        Args:
            data1: First dataset
            data2: Second dataset
            label1: Label for first dataset
            label2: Label for second dataset

        Returns:
            Formatted comparison string

        Example:
            >>> data1 = {"communities": 15, "assessments": 8}
            >>> data2 = {"communities": 20, "assessments": 5}
            >>> format_comparison_response(data1, data2, "Region IX", "Region X")
            "Comparison (Region IX vs Region X):\nCommunities: 15 vs 20 (Δ5)\nAssessments: 8 vs 5 (Δ-3)"
        """
        response = f"Comparison ({label1} vs {label2}):\n"

        # Get all keys from both datasets
        all_keys = set(data1.keys()) | set(data2.keys())

        for key in sorted(all_keys):
            value1 = data1.get(key, 0)
            value2 = data2.get(key, 0)

            # Format key
            formatted_key = key.replace('_', ' ').title()

            # Format values
            if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                diff = value2 - value1
                diff_str = f"Δ{diff:+,}" if diff != 0 else "="

                formatted_value1 = f"{value1:,.2f}" if isinstance(value1, float) else f"{value1:,}"
                formatted_value2 = f"{value2:,.2f}" if isinstance(value2, float) else f"{value2:,}"

                response += f"{formatted_key}: {formatted_value1} vs {formatted_value2} ({diff_str})\n"
            else:
                response += f"{formatted_key}: {value1} vs {value2}\n"

        return response.rstrip()


# Singleton instance
_formatter = None


def get_response_formatter() -> ResponseFormatter:
    """Get singleton response formatter instance."""
    global _formatter
    if _formatter is None:
        _formatter = ResponseFormatter()
    return _formatter
