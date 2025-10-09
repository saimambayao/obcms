"""
Conversational AI Chat Engine

Main orchestrator for the OBCMS conversational assistant.
Routes queries, coordinates components, and generates responses.
"""

import json
import logging
from typing import Dict, Optional

from .conversation_manager import get_conversation_manager
from .intent_classifier import get_intent_classifier
from .query_executor import get_query_executor
from .response_formatter import get_response_formatter

logger = logging.getLogger(__name__)


class ConversationalAssistant:
    """
    Natural language assistant for OBCMS.

    Features:
    - Intent classification and routing
    - Safe query execution
    - Multi-turn conversation support
    - Context-aware responses
    - Follow-up suggestions
    """

    def __init__(self):
        """Initialize conversational assistant with all components."""
        self.conversation_manager = get_conversation_manager()
        self.intent_classifier = get_intent_classifier()
        self.query_executor = get_query_executor()
        self.response_formatter = get_response_formatter()

        # Try to import Gemini service (optional for enhanced responses)
        try:
            from ai_assistant.services.gemini_service import GeminiService

            # Higher temperature (0.8) for more natural conversational responses
            self.gemini = GeminiService(temperature=0.8)
            self.has_gemini = True
            logger.info("Gemini service initialized for conversational chat")
        except ImportError:
            self.gemini = None
            self.has_gemini = False
            logger.warning(
                "Gemini service not available - using rule-based responses only"
            )

    def chat(self, user_id: int, message: str) -> Dict[str, any]:
        """
        Process user message and generate response.

        Args:
            user_id: User ID
            message: User's natural language message

        Returns:
            Dictionary with:
                - response: Natural language response text
                - data: Structured data for UI display
                - suggestions: Follow-up question suggestions
                - intent: Detected intent type
                - confidence: Intent confidence score
                - visualization: Suggested visualization type

        Example:
            >>> assistant = ConversationalAssistant()
            >>> result = assistant.chat(
            ...     user_id=1,
            ...     message="How many communities are in Region IX?"
            ... )
            >>> print(result['response'])
            'There are 47 communities in Region IX.'
        """
        try:
            # Step 1: Get conversation context
            context = self.conversation_manager.get_context(user_id)

            # Step 2: Classify intent
            intent_result = self.intent_classifier.classify(message, context)

            logger.info(
                f"User {user_id} query: '{message}' | "
                f"Intent: {intent_result['type']} "
                f"(confidence: {intent_result['confidence']:.2f})"
            )

            # Step 3: Route to appropriate handler
            if intent_result["type"] == "data_query":
                result = self._handle_data_query(message, intent_result, context)
            elif intent_result["type"] == "analysis":
                result = self._handle_analysis(message, intent_result, context)
            elif intent_result["type"] == "navigation":
                result = self._handle_navigation(message, intent_result)
            elif intent_result["type"] == "help":
                result = self._handle_help(message, intent_result)
            elif intent_result["type"] == "general":
                result = self._handle_general(message, context)
            else:
                result = self._handle_unknown(message)

            # Step 4: Store conversation exchange
            self.conversation_manager.add_exchange(
                user_id=user_id,
                user_message=message,
                assistant_response=result["response"],
                intent=intent_result["type"],
                confidence=intent_result["confidence"],
                entities=intent_result.get("entities", []),
            )

            # Step 5: Add metadata
            result["intent"] = intent_result["type"]
            result["confidence"] = intent_result["confidence"]

            return result

        except Exception as e:
            logger.error(f"Chat error for user {user_id}: {str(e)}", exc_info=True)
            return self.response_formatter.format_error(
                error_message=f"An error occurred: {str(e)}",
                query=message,
            )

    def _handle_data_query(
        self,
        message: str,
        intent_result: Dict,
        context: Dict,
    ) -> Dict[str, any]:
        """
        Handle data query intent.

        Converts natural language to Django ORM query and executes it.
        """
        entities = intent_result.get("entities", [])

        # Generate ORM query using AI or rule-based approach
        if self.has_gemini:
            query_string = self._generate_query_with_ai(message, entities, context)
        else:
            query_string = self._generate_query_rule_based(message, entities)

        if not query_string:
            return self.response_formatter.format_error(
                error_message="Could not understand your data query",
                query=message,
            )

        logger.info(f"Generated query: {query_string}")

        # Execute query
        exec_result = self.query_executor.execute(query_string)

        if not exec_result["success"]:
            return self.response_formatter.format_error(
                error_message=exec_result["error"],
                query=message,
            )

        # Format response
        result_type = exec_result["query_info"].get("result_type", "unknown")
        formatted = self.response_formatter.format_query_result(
            result=exec_result["result"],
            result_type=result_type,
            original_question=message,
            entities=entities,
        )

        return formatted

    def _generate_query_with_ai(
        self,
        message: str,
        entities: list,
        context: Dict,
    ) -> Optional[str]:
        """Generate Django ORM query using Gemini AI."""
        # Get available models
        available_models = self.query_executor.get_available_models()

        # Build prompt
        prompt = self._build_query_generation_prompt(
            message, entities, available_models
        )

        try:
            # Generate query
            response = self.gemini.generate_text(prompt)

            # Parse JSON response
            query_data = json.loads(response)
            query_string = query_data.get("query")

            return query_string

        except Exception as e:
            logger.error(f"AI query generation failed: {e}")
            return None

    def _build_query_generation_prompt(
        self,
        message: str,
        entities: list,
        available_models: list,
    ) -> str:
        """Build prompt for AI query generation."""
        prompt = f"""Convert this natural language question to a Django ORM query.

Question: "{message}"
Detected Entities: {entities}

Available Models:
"""
        for model in available_models:
            prompt += f"\n- {model['model_name']}: {model.get('verbose_name', '')}"
            prompt += f"\n  Fields: {', '.join(model['fields'][:10])}"

        prompt += """

Requirements:
1. Return ONLY a valid Django ORM query as a string
2. Use only READ operations (filter, count, aggregate, values)
3. NO write operations (create, update, delete, save)
4. Return JSON format: {"query": "ModelName.objects.filter(...).count()", "explanation": "..."}

Example:
{"query": "OBCCommunity.objects.filter(barangay__municipality__province__name__icontains='Zamboanga').count()", "explanation": "Count communities in Zamboanga"}

Your response (JSON only):
"""
        return prompt

    def _generate_query_rule_based(self, message: str, entities: list) -> Optional[str]:
        """Generate query using rule-based approach (fallback)."""
        message_lower = message.lower()

        # Simple pattern matching
        if "how many" in message_lower or "count" in message_lower:
            if "communities" in entities or "barangay" in message_lower:
                # Extract location if mentioned
                if "zamboanga" in message_lower:
                    return "OBCCommunity.objects.filter(barangay__municipality__province__name__icontains='Zamboanga').count()"
                elif "region" in message_lower:
                    return "OBCCommunity.objects.all().count()"

            elif "workshops" in entities or "workshop" in message_lower:
                return "Workshop.objects.all().count()"

            elif "policies" in entities or "policy" in message_lower:
                return "PolicyRecommendation.objects.all().count()"

            elif "projects" in entities or "ppa" in message_lower:
                return "PPA.objects.all().count()"

        return None

    def _handle_analysis(
        self,
        message: str,
        intent_result: Dict,
        context: Dict,
    ) -> Dict[str, any]:
        """
        Handle analysis intent.

        Requires fetching data and performing analysis.
        """
        if not self.has_gemini:
            return {
                "response": "Analysis features require AI integration. Please contact an administrator.",
                "data": {},
                "suggestions": ["Show me data instead", "Help with queries"],
                "visualization": None,
            }

        # For now, provide a helpful message
        # TODO: Implement full analysis engine
        return {
            "response": "Analysis features are coming soon! For now, you can ask me to show you specific data.",
            "data": {},
            "suggestions": [
                "How many communities are there?",
                "List all workshops",
                "Show me active projects",
            ],
            "visualization": None,
        }

    def _handle_navigation(self, message: str, intent_result: Dict) -> Dict[str, any]:
        """Handle navigation intent."""
        entities = intent_result.get("entities", [])
        target = entities[0] if entities else "dashboard"

        # Map entity to URL
        url_map = {
            "dashboard": "/dashboard/",
            "communities": "/communities/",
            "mana": "/mana/",
            "coordination": "/coordination/",
            "policies": "/policies/",
            "projects": "/project-central/",
        }

        url = url_map.get(target, "/dashboard/")

        return {
            "response": f"I'll take you to the {target} page.",
            "data": {"redirect_url": url},
            "suggestions": [],
            "visualization": None,
        }

    def _handle_help(self, message: str, intent_result: Dict) -> Dict[str, any]:
        """Handle help intent."""
        entities = intent_result.get("entities", [])
        topic = entities[0] if entities else None

        return self.response_formatter.format_help(topic)

    def _handle_general(self, message: str, context: Dict) -> Dict[str, any]:
        """Handle general conversational intent."""
        message_lower = message.lower()

        # Greetings
        if any(word in message_lower for word in ["hi", "hello", "hey"]):
            return self.response_formatter.format_greeting()

        # Thanks
        elif any(word in message_lower for word in ["thanks", "thank you"]):
            return {
                "response": "You're welcome! Is there anything else I can help you with?",
                "data": {},
                "suggestions": [
                    "How many communities are there?",
                    "Show me recent assessments",
                    "What can you do?",
                ],
                "visualization": None,
            }

        # Fallback
        else:
            return self.response_formatter.format_help()

    def _handle_unknown(self, message: str) -> Dict[str, any]:
        """Handle unknown intent."""
        return {
            "response": "I'm not sure how to help with that. Can you try rephrasing your question?",
            "data": {},
            "suggestions": [
                "What can you help me with?",
                "How many communities are there?",
                "Show me example queries",
            ],
            "visualization": None,
        }

    def get_capabilities(self) -> Dict[str, any]:
        """
        Get information about assistant capabilities.

        Returns:
            Dictionary with supported intents, example queries, etc.
        """
        capabilities = {
            "intents": [],
            "has_ai": self.has_gemini,
            "available_models": self.query_executor.get_available_models(),
        }

        # Add intent info
        for intent in ["data_query", "analysis", "navigation", "help", "general"]:
            capabilities["intents"].append(
                {
                    "type": intent,
                    "description": self.intent_classifier.get_intent_description(
                        intent
                    ),
                    "examples": self.intent_classifier.get_example_queries(intent),
                }
            )

        return capabilities


# Singleton instance
_assistant = None


def get_conversational_assistant() -> ConversationalAssistant:
    """Get singleton conversational assistant instance."""
    global _assistant
    if _assistant is None:
        _assistant = ConversationalAssistant()
    return _assistant
