"""
Conversational AI Chat Engine

Main orchestrator for the OBCMS conversational assistant.
Routes queries, coordinates components, and generates responses.
"""

import json
import logging
from typing import Dict, Optional

from django.conf import settings

from .clarification import get_clarification_handler
from .conversation_manager import get_conversation_manager
from .entity_extractor import EntityExtractor
from .fallback_handler import get_fallback_handler
from .faq_handler import get_faq_handler
from .intent_classifier import get_intent_classifier
from .query_executor import get_query_executor
from .query_templates import get_template_matcher
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
        # Core components (NEW PIPELINE - NO AI FALLBACK BY DEFAULT)
        self.faq_handler = get_faq_handler()
        self.entity_extractor = EntityExtractor()
        self.conversation_manager = get_conversation_manager()
        self.intent_classifier = get_intent_classifier()
        self.clarification_handler = get_clarification_handler()
        self.template_matcher = get_template_matcher()
        self.query_executor = get_query_executor()
        self.response_formatter = get_response_formatter()
        self.fallback_handler = get_fallback_handler()

        # Feature flag for AI fallback (DEPRECATED - set to False by default)
        self.use_ai_fallback = getattr(settings, 'CHAT_USE_AI_FALLBACK', False)

        # Legacy AI service (DEPRECATED - only if explicitly enabled)
        if self.use_ai_fallback:
            try:
                from ai_assistant.services.gemini_service import GeminiService

                # Higher temperature (0.8) for more natural conversational responses
                self.gemini = GeminiService(temperature=0.8)
                self.has_gemini = True
                logger.warning(
                    "AI fallback enabled (DEPRECATED) - consider using rule-based pipeline only"
                )
            except (ImportError, ValueError) as e:
                self.gemini = None
                self.has_gemini = False
                logger.info(
                    f"Gemini service not available - using rule-based responses only: {e}"
                )
        else:
            self.gemini = None
            self.has_gemini = False
            logger.info("Chat engine initialized with NO AI FALLBACK (production mode)")

    def chat(self, user_id: int, message: str) -> Dict[str, any]:
        """
        Process user message and generate response using NEW UNIFIED PIPELINE.

        Pipeline Flow (NO AI FALLBACK):
        1. Try FAQ instant response
        2. Extract entities from query
        3. Classify intent
        4. Check if clarification needed
        5. Try template-based query execution
        6. Fallback with helpful suggestions (NO AI)

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
                - source: Response source (faq, template, fallback, etc.)

        Example:
            >>> assistant = ConversationalAssistant()
            >>> result = assistant.chat(
            ...     user_id=1,
            ...     message="How many communities are in Region IX?"
            ... )
            >>> print(result['response'])
            'There are 47 communities in Region IX.'
        """
        import time

        pipeline_start = time.time()

        try:
            # =====================================================
            # STAGE 1: Try FAQ instant response (< 10ms target)
            # =====================================================
            stage_start = time.time()
            faq_result = self.faq_handler.try_faq(message)
            stage_time = (time.time() - stage_start) * 1000

            if faq_result:
                total_time = (time.time() - pipeline_start) * 1000
                logger.info(
                    f"User {user_id} query: '{message}' | "
                    f"Source: FAQ | "
                    f"Stage time: {stage_time:.2f}ms | "
                    f"Total time: {total_time:.2f}ms"
                )
                return self._format_faq_response(faq_result, user_id, message)

            # =====================================================
            # STAGE 2: Extract entities from query
            # =====================================================
            stage_start = time.time()
            entities = self.entity_extractor.extract_entities(message)
            stage_time = (time.time() - stage_start) * 1000

            logger.info(
                f"User {user_id} query: '{message}' | "
                f"Entities extracted: {list(entities.keys())} | "
                f"Stage time: {stage_time:.2f}ms"
            )

            # =====================================================
            # STAGE 3: Classify intent
            # =====================================================
            stage_start = time.time()
            context = self.conversation_manager.get_context(user_id)
            intent_result = self.intent_classifier.classify(message, context)
            stage_time = (time.time() - stage_start) * 1000

            logger.info(
                f"User {user_id} query: '{message}' | "
                f"Intent: {intent_result['type']} "
                f"(confidence: {intent_result['confidence']:.2f}) | "
                f"Stage time: {stage_time:.2f}ms"
            )

            # =====================================================
            # STAGE 4: Check if clarification needed
            # =====================================================
            stage_start = time.time()
            clarification_needed = self.clarification_handler.needs_clarification(
                query=message, entities=entities, intent=intent_result["type"]
            )
            stage_time = (time.time() - stage_start) * 1000

            if clarification_needed:
                total_time = (time.time() - pipeline_start) * 1000
                logger.info(
                    f"User {user_id} query: '{message}' | "
                    f"Source: Clarification | "
                    f"Issue: {clarification_needed.get('issue_type')} | "
                    f"Stage time: {stage_time:.2f}ms | "
                    f"Total time: {total_time:.2f}ms"
                )
                return {
                    "type": "clarification",
                    "response": clarification_needed["message"],
                    "clarification": clarification_needed,
                    "data": {},
                    "suggestions": [],
                    "visualization": None,
                    "intent": intent_result["type"],
                    "confidence": intent_result["confidence"],
                    "source": "clarification",
                }

            # =====================================================
            # STAGE 5: Route to appropriate handler
            # =====================================================
            stage_start = time.time()
            if intent_result["type"] == "data_query":
                result = self._handle_data_query_new_pipeline(
                    message, intent_result, entities, context
                )
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

            stage_time = (time.time() - stage_start) * 1000
            total_time = (time.time() - pipeline_start) * 1000

            logger.info(
                f"User {user_id} query: '{message}' | "
                f"Handler stage time: {stage_time:.2f}ms | "
                f"Total time: {total_time:.2f}ms"
            )

            # =====================================================
            # STAGE 6: Store conversation exchange
            # =====================================================
            self.conversation_manager.add_exchange(
                user_id=user_id,
                user_message=message,
                assistant_response=result["response"],
                intent=intent_result["type"],
                confidence=intent_result["confidence"],
                entities=list(entities.keys()),
            )

            # Add metadata
            result["intent"] = intent_result["type"]
            result["confidence"] = intent_result["confidence"]
            result["response_time"] = total_time

            return result

        except Exception as e:
            logger.error(f"Chat error for user {user_id}: {str(e)}", exc_info=True)
            return self.response_formatter.format_error(
                error_message=f"An error occurred: {str(e)}",
                query=message,
            )

    def _format_faq_response(
        self, faq_result: Dict, user_id: int, message: str
    ) -> Dict[str, any]:
        """
        Format FAQ response for chat interface.

        Args:
            faq_result: FAQ handler result
            user_id: User ID
            message: Original message

        Returns:
            Formatted response dict
        """
        # Store FAQ hit in conversation history
        self.conversation_manager.add_exchange(
            user_id=user_id,
            user_message=message,
            assistant_response=faq_result['answer'],
            intent='faq',
            confidence=faq_result.get('confidence', 1.0),
            entities=[],
        )

        return {
            "response": faq_result['answer'],
            "data": {},
            "suggestions": faq_result.get('related_queries', [])
            or faq_result.get('examples', []),
            "visualization": None,
            "intent": "faq",
            "confidence": faq_result.get('confidence', 1.0),
            "source": "faq",
            "response_time": faq_result.get('response_time', 0),
        }

    def _handle_data_query_new_pipeline(
        self,
        message: str,
        intent_result: Dict,
        entities: Dict,
        context: Dict,
    ) -> Dict[str, any]:
        """
        Handle data query using NEW TEMPLATE-BASED PIPELINE (NO AI).

        Pipeline:
        1. Find matching query templates
        2. Generate Django ORM query from template
        3. Execute query safely
        4. Format result
        5. If all fails, use fallback handler (NO AI)

        Args:
            message: User's query
            intent_result: Intent classification result
            entities: Extracted entities
            context: Conversation context

        Returns:
            Response dictionary
        """
        # =====================================================
        # STEP 1: Find matching query templates
        # =====================================================
        matching_templates = self.template_matcher.find_matching_templates(
            message, entities, intent_result["type"]
        )

        if not matching_templates:
            logger.info(
                f"No matching templates for query: '{message}' | "
                f"Intent: {intent_result['type']} | "
                f"Entities: {list(entities.keys())}"
            )
            # Fallback to old rule-based approach or fallback handler
            return self._handle_data_query_fallback(message, entities, context)

        # =====================================================
        # STEP 2: Try each matching template (priority order)
        # =====================================================
        for template in matching_templates:
            try:
                logger.info(
                    f"Trying template: {template.id} (priority: {template.priority})"
                )

                # Generate query from template
                query_string = self.template_matcher.generate_query(template, entities)

                # Execute query
                exec_result = self.query_executor.execute(query_string)

                if exec_result["success"]:
                    # Format response
                    formatted = self.response_formatter.format_query_result(
                        result=exec_result["result"],
                        result_type=template.result_type,
                        original_question=message,
                        entities=entities,
                    )

                    # Add source metadata
                    formatted["source"] = "template"
                    formatted["template_id"] = template.id

                    logger.info(
                        f"Query successful | Template: {template.id} | "
                        f"Result type: {template.result_type}"
                    )

                    return formatted
                else:
                    logger.warning(
                        f"Template {template.id} query failed: {exec_result.get('error')}"
                    )
                    # Try next template

            except Exception as e:
                logger.error(
                    f"Template {template.id} execution error: {str(e)}", exc_info=True
                )
                # Try next template
                continue

        # =====================================================
        # STEP 3: All templates failed - use fallback handler
        # =====================================================
        logger.warning(
            f"All templates failed for query: '{message}' | "
            f"Tried {len(matching_templates)} templates"
        )
        return self._handle_data_query_fallback(message, entities, context)

    def _handle_data_query_fallback(
        self,
        message: str,
        entities: Dict,
        context: Dict,
    ) -> Dict[str, any]:
        """
        Fallback handler when template-based approach fails.

        Uses:
        1. Legacy rule-based query generation (if applicable)
        2. Fallback handler with suggestions (NO AI)

        Args:
            message: User's query
            entities: Extracted entities
            context: Conversation context

        Returns:
            Response dictionary
        """
        # Try legacy rule-based approach
        legacy_query = self._generate_query_rule_based(message, list(entities.keys()))

        if legacy_query:
            try:
                exec_result = self.query_executor.execute(legacy_query)

                if exec_result["success"]:
                    formatted = self.response_formatter.format_query_result(
                        result=exec_result["result"],
                        result_type=exec_result["query_info"].get("result_type", "unknown"),
                        original_question=message,
                        entities=entities,
                    )
                    formatted["source"] = "rule_based"
                    return formatted
            except Exception as e:
                logger.error(f"Legacy query execution error: {str(e)}", exc_info=True)

        # =====================================================
        # FINAL FALLBACK: Use fallback handler (NO AI)
        # =====================================================
        logger.info("Using rule-based fallback handler")
        fallback_result = self.fallback_handler.handle_failed_query(
            query=message,
            intent='data_query',
            entities=entities
        )

        return self._format_fallback_response(fallback_result, message)

    def _format_fallback_response(
        self, fallback_result: Dict, message: str
    ) -> Dict[str, any]:
        """
        Format fallback handler result for chat interface.

        Args:
            fallback_result: Fallback handler result
            message: Original query

        Returns:
            Formatted response dict
        """
        error_analysis = fallback_result.get('error_analysis', {})
        suggestions = fallback_result.get('suggestions', {})
        alternatives = fallback_result.get('alternatives', [])

        # Build response message
        response_parts = [
            f"I couldn't process your query: \"{message}\"",
            "",
            f"**Issue**: {error_analysis.get('explanation', 'Query could not be processed')}",
            "",
        ]

        # Add corrected queries
        corrected = suggestions.get('corrected_queries', [])
        if corrected:
            response_parts.append("**Did you mean:**")
            for query in corrected[:3]:
                response_parts.append(f"• {query}")
            response_parts.append("")

        # Add similar successful queries
        similar = suggestions.get('similar_queries', [])
        if similar:
            response_parts.append("**Similar queries that worked:**")
            for query in similar[:3]:
                response_parts.append(f"• {query}")
            response_parts.append("")

        # Add template examples
        templates = suggestions.get('template_examples', [])
        if templates:
            response_parts.append("**Example queries you can try:**")
            for query in templates[:3]:
                response_parts.append(f"• {query}")

        response_text = "\n".join(response_parts)

        # Combine all suggestions
        all_suggestions = (
            corrected[:3] + similar[:3] + templates[:3]
        )

        return {
            "response": response_text,
            "data": {
                "error_analysis": error_analysis,
                "alternatives": alternatives,
            },
            "suggestions": all_suggestions[:5],
            "visualization": None,
            "source": "fallback",
            "confidence": 0.0,
        }

    # REMOVED: _handle_data_query (old AI-based method)
    # Now uses _handle_data_query_new_pipeline exclusively

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

    # REMOVED: _fallback_to_gemini (deprecated AI fallback)
    # Now uses fallback_handler.handle_failed_query() exclusively

    # REMOVED: _build_conversational_prompt (deprecated AI prompt builder)
    # Replaced with rule-based fallback handler

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
