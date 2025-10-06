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
        except (ImportError, ValueError) as e:
            self.gemini = None
            self.has_gemini = False
            logger.warning(
                f"Gemini service not available - using rule-based responses only: {e}"
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
        Falls back to Gemini AI for conversational response if query fails.
        """
        entities = intent_result.get("entities", [])

        # Generate ORM query using AI or rule-based approach
        if self.has_gemini:
            query_string = self._generate_query_with_ai(message, entities, context)
        else:
            query_string = self._generate_query_rule_based(message, entities)

        # If query generation failed, fallback to Gemini conversational AI
        if not query_string:
            if self.has_gemini:
                logger.info(
                    "Structured query failed, falling back to Gemini conversational AI"
                )
                return self._fallback_to_gemini(message, context)
            else:
                return self.response_formatter.format_error(
                    error_message="Could not understand your data query",
                    query=message,
                )

        logger.info(f"Generated query: {query_string}")

        # Execute query
        exec_result = self.query_executor.execute(query_string)

        # If query execution failed, fallback to Gemini conversational AI
        if not exec_result["success"]:
            if self.has_gemini:
                logger.info(
                    f"Query execution failed ({exec_result['error']}), "
                    f"falling back to Gemini conversational AI"
                )
                return self._fallback_to_gemini(message, context)
            else:
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

            # Extract text from Gemini response
            if not response.get("success"):
                logger.error(f"Gemini query generation failed: {response.get('error')}")
                return None

            response_text = response.get("text", "")

            # Parse JSON response
            query_data = json.loads(response_text)
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
        """
        Generate query using rule-based approach (fallback).

        Enhanced to handle cities, municipalities, and various location types.
        """
        message_lower = message.lower()

        # Extract location entities from message
        location = self._extract_location_from_message(message_lower)

        # Simple pattern matching
        if "how many" in message_lower or "count" in message_lower:
            if "communities" in entities or "barangay" in message_lower or "obc" in message_lower:
                # Build query with location filter if provided
                if location:
                    # Try multiple location types (province, city/municipality)
                    return f"OBCCommunity.objects.filter(Q(barangay__municipality__name__icontains='{location}') | Q(barangay__municipality__province__name__icontains='{location}')).count()"
                else:
                    return "OBCCommunity.objects.all().count()"

            elif "workshops" in entities or "workshop" in message_lower:
                return "Workshop.objects.all().count()"

            elif "policies" in entities or "policy" in message_lower:
                return "PolicyRecommendation.objects.all().count()"

            elif "projects" in entities or "ppa" in message_lower:
                return "PPA.objects.all().count()"

        # List/show queries
        elif any(word in message_lower for word in ["list", "show", "tell me about", "about"]):
            if "communities" in entities or "barangay" in message_lower or "obc" in message_lower:
                if location:
                    return f"OBCCommunity.objects.filter(Q(barangay__municipality__name__icontains='{location}') | Q(barangay__municipality__province__name__icontains='{location}'))"
                else:
                    return "OBCCommunity.objects.all()"

        return None

    def _extract_location_from_message(self, message_lower: str) -> Optional[str]:
        """
        Extract location name from message.

        Handles cities, municipalities, provinces.
        """
        # Common location patterns
        location_patterns = [
            r"in ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",  # "in Davao City"
            r"at ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",  # "at Zamboanga"
            r"from ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",  # "from Cotabato"
        ]

        # Try to extract from original message (before lowercasing)
        import re
        for pattern in location_patterns:
            match = re.search(pattern, message_lower, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # Clean up common words
                location = location.replace(" city", "").replace(" province", "").strip()
                if len(location) > 3:  # Avoid single chars
                    return location

        # Known cities/provinces in OBCMS coverage
        known_locations = [
            "zamboanga", "davao", "cotabato", "sultan kudarat", "lanao",
            "bukidnon", "cagayan de oro", "iligan", "marawi",
            "zamboanga del sur", "zamboanga del norte", "zamboanga sibugay"
        ]

        for location in known_locations:
            if location in message_lower:
                return location.title()

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

    def _fallback_to_gemini(self, message: str, context: Dict) -> Dict[str, any]:
        """
        Fallback to Gemini conversational AI when structured query fails.

        Used when:
        - Query generation fails
        - Query execution fails
        - User asks questions that don't fit structured data queries

        Returns a natural language response using Gemini's conversational capabilities.
        """
        try:
            # Build conversational prompt with OBCMS context
            prompt = self._build_conversational_prompt(message, context)

            # Generate response using Gemini
            response = self.gemini.generate_text(prompt)

            # Extract text from Gemini response dict
            if not response.get("success"):
                logger.error(f"Gemini fallback failed: {response.get('error')}")
                return self.response_formatter.format_error(
                    error_message="I couldn't process your question. Please try rephrasing it.",
                    query=message,
                )

            response_text = response.get("text", "")

            return {
                "response": response_text,
                "data": {},
                "suggestions": [
                    "Tell me more",
                    "What else can you help with?",
                    "Show me some data",
                ],
                "visualization": None,
            }

        except Exception as e:
            logger.error(f"Gemini fallback failed: {e}", exc_info=True)
            return self.response_formatter.format_error(
                error_message="I couldn't process your question. Please try rephrasing it.",
                query=message,
            )

    def _build_conversational_prompt(self, message: str, context: Dict) -> str:
        """
        Build prompt for Gemini conversational response.

        Provides OBCMS context to help Gemini give relevant answers.
        """
        prompt = f"""You are the OBCMS AI Assistant helping users with the Office for Other Bangsamoro Communities system.

User Question: "{message}"

Context: OBCMS manages data about Bangsamoro communities outside BARMM, including:
- Community profiles (demographics, needs, services)
- MANA assessments (Mapping and Needs Assessment)
- Coordination activities (partnerships, workshops)
- Policy recommendations
- Project management

Please provide a helpful, conversational response to the user's question. If you don't have specific data, guide them on what they can ask or where they can find the information in the system.

Keep your response concise (2-3 sentences) and friendly.

Response:"""

        return prompt

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
