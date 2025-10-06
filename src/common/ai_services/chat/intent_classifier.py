"""
Intent Classifier for Conversational AI

Classifies user intent to route queries appropriately.
Uses pattern matching and keyword analysis for fast classification.
"""

import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class IntentClassifier:
    """
    Classify user intent from natural language messages.

    Intent Types:
    - data_query: Request for data ("How many communities?")
    - analysis: Request for insights ("What are the top needs?")
    - navigation: Request to go somewhere ("Show me the dashboard")
    - help: Request for assistance ("How do I create a workshop?")
    - general: Conversational or unclear intent
    """

    # Intent patterns with keywords and regex patterns
    INTENT_PATTERNS = {
        'data_query': {
            'keywords': [
                'how many', 'count', 'list', 'show me', 'find', 'get',
                'which', 'what are', 'total', 'number of', 'display',
            ],
            'patterns': [
                r'how many .+ (are|in|have)',
                r'(count|total|number of) .+',
                r'(list|show|display) (all|the) .+',
                r'which .+ (are|have|in)',
            ],
            'entities': ['communities', 'workshops', 'policies', 'projects', 'organizations'],
        },
        'analysis': {
            'keywords': [
                'analyze', 'compare', 'trend', 'insight', 'summary',
                'top', 'most', 'least', 'average', 'common',
                'distribution', 'breakdown', 'pattern',
            ],
            'patterns': [
                r'(what|which) (are|is) the (top|most|least) .+',
                r'(analyze|compare|summarize) .+',
                r'(trend|pattern|distribution) (of|in|for) .+',
            ],
            'entities': ['needs', 'priorities', 'sectors', 'regions'],
        },
        'navigation': {
            'keywords': [
                'go to', 'navigate', 'open', 'take me', 'redirect',
                'dashboard', 'page', 'view', 'section',
            ],
            'patterns': [
                r'(go to|navigate to|open|show) (the )?(dashboard|page|view)',
                r'(take me to|redirect to) .+',
            ],
            'entities': ['dashboard', 'communities', 'mana', 'coordination', 'policies'],
        },
        'help': {
            'keywords': [
                'help', 'how do i', 'how to', 'explain', 'what is',
                'guide', 'tutorial', 'instructions', 'steps',
            ],
            'patterns': [
                r'how (do i|to|can i) .+',
                r'(what is|explain) .+',
                r'(help|guide|tutorial) (me with|on|for) .+',
            ],
            'entities': ['create', 'update', 'delete', 'search', 'filter'],
        },
        'general': {
            'keywords': ['hi', 'hello', 'thanks', 'thank you', 'okay', 'yes', 'no'],
            'patterns': [r'^(hi|hello|hey)', r'(thanks|thank you)'],
            'entities': [],
        },
    }

    # Data entities (models)
    DATA_ENTITIES = {
        'communities': ['barangay', 'community', 'communities', 'obc'],
        'workshops': ['workshop', 'assessment', 'mana', 'consultation'],
        'policies': ['policy', 'recommendation', 'proposal'],
        'projects': ['project', 'ppa', 'program', 'activity'],
        'organizations': ['organization', 'partner', 'stakeholder', 'agency'],
        'regions': ['region', 'province', 'municipality', 'area'],
    }

    # Action verbs
    ACTION_VERBS = {
        'create': ['create', 'add', 'new', 'register'],
        'read': ['show', 'display', 'view', 'get', 'find', 'list'],
        'update': ['update', 'edit', 'modify', 'change'],
        'delete': ['delete', 'remove'],
        'filter': ['filter', 'search', 'where'],
        'aggregate': ['count', 'total', 'sum', 'average'],
    }

    def __init__(self):
        """Initialize intent classifier."""
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for faster matching."""
        self._compiled_patterns = {}
        for intent, config in self.INTENT_PATTERNS.items():
            self._compiled_patterns[intent] = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in config.get('patterns', [])
            ]

    def classify(self, message: str, context: Optional[Dict] = None) -> Dict[str, any]:
        """
        Classify user message intent.

        Args:
            message: User's natural language message
            context: Optional conversation context

        Returns:
            Dictionary with:
                - type: Intent type (data_query, analysis, etc.)
                - confidence: Confidence score (0.0-1.0)
                - entities: Detected entities
                - action: Detected action verb
                - routing: Suggested routing information

        Example:
            >>> classifier = IntentClassifier()
            >>> result = classifier.classify("How many communities are in Zamboanga?")
            >>> print(result['type'])
            'data_query'
        """
        message_lower = message.lower().strip()

        # Calculate scores for each intent
        scores = {}
        for intent in self.INTENT_PATTERNS.keys():
            scores[intent] = self._score_intent(message_lower, intent)

        # Get highest scoring intent
        best_intent = max(scores, key=scores.get)
        confidence = scores[best_intent]

        # Extract entities and actions
        entities = self._extract_entities(message_lower)
        action = self._extract_action(message_lower)

        # Build routing information
        routing = self._build_routing(best_intent, entities, action)

        return {
            'type': best_intent,
            'confidence': confidence,
            'entities': entities,
            'action': action,
            'routing': routing,
            'all_scores': scores,
        }

    def _score_intent(self, message: str, intent: str) -> float:
        """
        Score how well message matches an intent.

        Scoring:
        - Keyword match: +0.3 per keyword
        - Pattern match: +0.5 per pattern
        - Entity match: +0.2 per entity
        - Max score: 1.0
        """
        score = 0.0
        config = self.INTENT_PATTERNS[intent]

        # Check keyword matches
        keywords = config.get('keywords', [])
        keyword_matches = sum(1 for kw in keywords if kw in message)
        if keyword_matches > 0:
            score += min(keyword_matches * 0.3, 0.6)

        # Check pattern matches
        patterns = self._compiled_patterns.get(intent, [])
        pattern_matches = sum(1 for pattern in patterns if pattern.search(message))
        if pattern_matches > 0:
            score += min(pattern_matches * 0.5, 0.8)

        # Check entity matches
        entities = config.get('entities', [])
        entity_matches = sum(1 for entity in entities if entity in message)
        if entity_matches > 0:
            score += min(entity_matches * 0.2, 0.4)

        # Normalize to 0-1
        return min(score, 1.0)

    def _extract_entities(self, message: str) -> List[str]:
        """Extract data entities from message."""
        entities = []

        for entity_type, keywords in self.DATA_ENTITIES.items():
            for keyword in keywords:
                if keyword in message:
                    entities.append(entity_type)
                    break  # Only add each entity type once

        return entities

    def _extract_action(self, message: str) -> Optional[str]:
        """Extract action verb from message."""
        for action, verbs in self.ACTION_VERBS.items():
            for verb in verbs:
                if verb in message:
                    return action

        return None

    def _build_routing(self, intent: str, entities: List[str], action: Optional[str]) -> Dict[str, any]:
        """
        Build routing information for the intent.

        Returns:
            Dictionary with suggested handling approach
        """
        routing = {
            'intent': intent,
            'handler': None,
            'parameters': {},
        }

        if intent == 'data_query':
            routing['handler'] = 'query_executor'
            routing['parameters'] = {
                'entities': entities,
                'action': action or 'read',
            }

        elif intent == 'analysis':
            routing['handler'] = 'analysis_engine'
            routing['parameters'] = {
                'entities': entities,
                'analysis_type': 'insights',
            }

        elif intent == 'navigation':
            routing['handler'] = 'navigation_handler'
            routing['parameters'] = {
                'target': entities[0] if entities else 'dashboard',
            }

        elif intent == 'help':
            routing['handler'] = 'help_system'
            routing['parameters'] = {
                'topic': entities[0] if entities else 'general',
            }

        elif intent == 'general':
            routing['handler'] = 'conversational'
            routing['parameters'] = {}

        return routing

    def get_intent_description(self, intent: str) -> str:
        """Get human-readable description of an intent."""
        descriptions = {
            'data_query': 'Request for specific data from the system',
            'analysis': 'Request for analytical insights and patterns',
            'navigation': 'Request to navigate to a different page',
            'help': 'Request for help or instructions',
            'general': 'General conversation or greeting',
        }
        return descriptions.get(intent, 'Unknown intent')

    def get_example_queries(self, intent: str) -> List[str]:
        """Get example queries for an intent."""
        examples = {
            'data_query': [
                'How many communities are in Region IX?',
                'List all workshops in Zamboanga del Sur',
                'Show me active policy recommendations',
                'Count organizations in the coordination network',
            ],
            'analysis': [
                'What are the top needs in coastal communities?',
                'Analyze MANA assessment trends',
                'Compare project completion rates by region',
                'Show me the most common ethnolinguistic groups',
            ],
            'navigation': [
                'Take me to the dashboard',
                'Open the MANA module',
                'Go to coordination page',
            ],
            'help': [
                'How do I create a new workshop?',
                'What is a policy recommendation?',
                'Help me search for communities',
            ],
            'general': [
                'Hello!',
                'Thank you',
                'What can you help me with?',
            ],
        }
        return examples.get(intent, [])


# Singleton instance
_classifier = None


def get_intent_classifier() -> IntentClassifier:
    """Get singleton intent classifier instance."""
    global _classifier
    if _classifier is None:
        _classifier = IntentClassifier()
    return _classifier
