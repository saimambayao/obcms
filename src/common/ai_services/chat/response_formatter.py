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
                - text: Natural language response
                - data: Structured data for UI display
                - suggestions: Follow-up questions
                - visualization: Suggested visualization type
        """
        entities = entities or []

        # Route to appropriate formatter
        if isinstance(result, int):
            return self._format_count(result, original_question, entities)
        elif isinstance(result, dict):
            return self._format_aggregate(result, original_question, entities)
        elif isinstance(result, list):
            return self._format_list(result, original_question, entities)
        else:
            return self._format_generic(result, original_question)

    def _format_count(self, count: int, question: str, entities: List[str]) -> Dict[str, Any]:
        """Format count results."""
        # Determine entity type for natural response
        entity = entities[0] if entities else 'items'
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
            'text': text,
            'data': {'count': count, 'entity': entity},
            'suggestions': suggestions,
            'visualization': 'number' if count < 10 else 'bar_chart',
        }

    def _format_aggregate(self, aggregate: Dict, question: str, entities: List[str]) -> Dict[str, Any]:
        """Format aggregate results (sum, avg, etc.)."""
        lines = []

        for key, value in aggregate.items():
            # Parse aggregate key (e.g., 'total_population__sum')
            parts = key.split('__')
            field_name = parts[0].replace('_', ' ').title()
            agg_type = parts[1].upper() if len(parts) > 1 else 'VALUE'

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
        entity = entities[0] if entities else 'data'
        suggestions = [
            f"Show me the detailed breakdown",
            f"Compare this across regions",
            f"What's the trend over time?",
        ]

        return {
            'text': text,
            'data': aggregate,
            'suggestions': suggestions,
            'visualization': 'metric_cards',
        }

    def _format_list(self, items: List[Dict], question: str, entities: List[str]) -> Dict[str, Any]:
        """Format list results."""
        count = len(items)
        entity = entities[0] if entities else 'results'
        entity_name = self._pluralize(entity, count)

        # Build intro
        if count == 0:
            text = f"No {entity_name} found matching your query."
            suggestions = [f"Try a broader search", "Show me all {entity}"]
            return {
                'text': text,
                'data': {'items': [], 'count': 0},
                'suggestions': suggestions,
                'visualization': None,
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
            'text': text,
            'data': {'items': items, 'count': count, 'preview_count': preview_count},
            'suggestions': suggestions,
            'visualization': 'table' if count > 10 else 'list',
        }

    def _format_list_item(self, index: int, item: Dict, entity: str) -> str:
        """Format a single list item."""
        # Try to find meaningful fields to display
        display_fields = []

        # Common field names to prioritize
        priority_fields = ['name', 'title', 'description', 'status', 'date']

        # Add priority fields first
        for field in priority_fields:
            if field in item and item[field]:
                value = item[field]
                # Truncate long values
                if isinstance(value, str) and len(value) > 100:
                    value = value[:97] + '...'
                display_fields.append(f"**{field.title()}**: {value}")

        # If no priority fields, use first few fields
        if not display_fields:
            for key, value in list(item.items())[:3]:
                if key != 'id' and value:
                    if isinstance(value, str) and len(value) > 100:
                        value = value[:97] + '...'
                    display_fields.append(f"**{key.replace('_', ' ').title()}**: {value}")

        item_text = f"{index}. " + " | ".join(display_fields) + "\n"
        return item_text

    def _format_generic(self, result: Any, question: str) -> Dict[str, Any]:
        """Fallback formatter for unknown result types."""
        text = f"Here's what I found:\n\n{str(result)}"

        return {
            'text': text,
            'data': {'result': str(result)},
            'suggestions': ['Can you clarify your question?', 'Show me more details'],
            'visualization': None,
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

    def _generate_list_suggestions(self, entity: str, count: int, items: List[Dict]) -> List[str]:
        """Generate follow-up suggestions for list queries."""
        suggestions = []

        if count > 5:
            suggestions.append(f"Show me more details")

        suggestions.append(f"Filter these {entity}")
        suggestions.append(f"Analyze these results")

        # Try to suggest entity-specific actions
        if 'communities' in entity:
            suggestions.append("Show MANA assessments for these")
        elif 'workshops' in entity or 'mana' in entity:
            suggestions.append("What were the key findings?")
        elif 'policies' in entity:
            suggestions.append("Which ones are approved?")
        elif 'projects' in entity or 'ppa' in entity:
            suggestions.append("What's the total budget?")

        return suggestions[:3]  # Limit to 3

    def _pluralize(self, word: str, count: int) -> str:
        """Simple pluralization."""
        if count == 1:
            return word.rstrip('s')
        elif word.endswith('s'):
            return word
        else:
            return word + 's'

    def format_error(self, error_message: str, query: str) -> Dict[str, Any]:
        """Format error message in a helpful way."""
        text = "I encountered an issue processing your request:\n\n"
        text += f"*{error_message}*\n\n"
        text += "You can try:\n"
        text += "- Rephrasing your question\n"
        text += "- Being more specific\n"
        text += "- Asking for help with available commands"

        return {
            'text': text,
            'data': {'error': error_message, 'query': query},
            'suggestions': [
                'What can you help me with?',
                'Show me example queries',
                'Help with search',
            ],
            'visualization': None,
        }

    def format_help(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """Format help response."""
        text = "**OBCMS AI Assistant Help**\n\n"
        text += "I can help you with:\n\n"
        text += "**Data Queries**\n"
        text += "- 'How many communities are in Zamboanga?'\n"
        text += "- 'List all workshops in 2025'\n"
        text += "- 'Show me active policy recommendations'\n\n"
        text += "**Analysis**\n"
        text += "- 'What are the top needs in Region IX?'\n"
        text += "- 'Analyze MANA assessment trends'\n"
        text += "- 'Compare project completion rates'\n\n"
        text += "**Navigation**\n"
        text += "- 'Take me to the dashboard'\n"
        text += "- 'Open the MANA module'\n\n"
        text += "Just ask me in natural language!"

        return {
            'text': text,
            'data': {'topic': topic},
            'suggestions': [
                'How many communities are there?',
                'Show me recent workshops',
                'What can you analyze?',
            ],
            'visualization': None,
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
            'text': text,
            'data': {},
            'suggestions': [
                'How many communities are in the system?',
                'Show me recent MANA assessments',
                'What are the top priorities?',
            ],
            'visualization': None,
        }


# Singleton instance
_formatter = None


def get_response_formatter() -> ResponseFormatter:
    """Get singleton response formatter instance."""
    global _formatter
    if _formatter is None:
        _formatter = ResponseFormatter()
    return _formatter
