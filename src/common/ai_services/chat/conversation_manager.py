"""
Conversation Manager for Conversational AI

Manages conversation state, context tracking, and history.
Enables multi-turn conversations with context awareness.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from django.core.cache import cache
from django.db.models import Count

logger = logging.getLogger(__name__)


class ConversationManager:
    """
    Manage multi-turn conversation state and context.

    Features:
    - Conversation history storage
    - Entity tracking across turns
    - Topic detection and switching
    - Context window management
    - Session management
    """

    # Cache timeout for conversation context (30 minutes)
    CONTEXT_TIMEOUT = 60 * 30

    # Maximum turns to keep in context
    MAX_CONTEXT_TURNS = 5

    # Session timeout (2 hours of inactivity)
    SESSION_TIMEOUT = 60 * 60 * 2

    def __init__(self):
        """Initialize conversation manager."""
        pass

    def get_context(self, user_id: int, turns: int = None) -> Dict[str, any]:
        """
        Get conversation context for a user.

        Args:
            user_id: User ID
            turns: Number of recent turns to include (default: MAX_CONTEXT_TURNS)

        Returns:
            Dictionary with:
                - history: List of recent exchanges
                - last_topic: Last detected topic
                - entities_mentioned: Entities mentioned in conversation
                - session_id: Current session ID
        """
        if turns is None:
            turns = self.MAX_CONTEXT_TURNS

        # Try cache first
        cache_key = f"chat_context_{user_id}"
        cached_context = cache.get(cache_key)

        if cached_context:
            return cached_context

        # Fetch from database
        from common.models import ChatMessage

        messages = ChatMessage.objects.filter(
            user_id=user_id
        ).order_by('-created_at')[:turns]

        # Build context
        history = []
        entities = set()
        topics = []

        for msg in reversed(list(messages)):
            history.append({
                'user': msg.user_message,
                'assistant': msg.assistant_response,
                'timestamp': msg.created_at.isoformat(),
            })

            # Track entities
            if msg.entities:
                entities.update(msg.entities)

            # Track topics
            if msg.topic:
                topics.append(msg.topic)

        last_topic = topics[-1] if topics else None

        context = {
            'history': history,
            'last_topic': last_topic,
            'entities_mentioned': list(entities),
            'session_id': self._get_or_create_session(user_id),
            'turn_count': len(history),
        }

        # Cache for quick access
        cache.set(cache_key, context, self.CONTEXT_TIMEOUT)

        return context

    def add_exchange(
        self,
        user_id: int,
        user_message: str,
        assistant_response: str,
        intent: str = None,
        confidence: float = None,
        entities: List[str] = None,
    ):
        """
        Store a conversation exchange.

        Args:
            user_id: User ID
            user_message: User's message
            assistant_response: Assistant's response
            intent: Detected intent
            confidence: Intent confidence score
            entities: Detected entities
        """
        from common.models import ChatMessage

        # Detect topic
        topic = self._classify_topic(user_message, entities)

        # Create message record
        ChatMessage.objects.create(
            user_id=user_id,
            user_message=user_message,
            assistant_response=assistant_response,
            intent=intent or 'unknown',
            confidence=confidence or 0.0,
            topic=topic,
            entities=entities or [],
            session_id=self._get_or_create_session(user_id),
        )

        # Invalidate cache to include new message
        cache_key = f"chat_context_{user_id}"
        cache.delete(cache_key)

        # Update session timestamp
        self._update_session_timestamp(user_id)

    def _classify_topic(self, message: str, entities: List[str] = None) -> str:
        """
        Classify the topic of a message.

        Topics:
        - communities: Barangay/community queries
        - mana: Workshop/assessment queries
        - coordination: Partnership/stakeholder queries
        - policies: Policy recommendation queries
        - projects: PPA/project queries
        - general: Other queries
        """
        message_lower = message.lower()
        entities = entities or []

        # Topic keywords
        topic_keywords = {
            'communities': ['barangay', 'community', 'obc', 'municipality', 'province'],
            'mana': ['workshop', 'assessment', 'mana', 'needs', 'consultation'],
            'coordination': ['partner', 'stakeholder', 'organization', 'coordination'],
            'policies': ['policy', 'recommendation', 'proposal'],
            'projects': ['project', 'ppa', 'program', 'activity', 'budget'],
        }

        # Score each topic
        scores = {}
        for topic, keywords in topic_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in message_lower:
                    score += 1
            if topic in entities:
                score += 2
            scores[topic] = score

        # Return highest scoring topic
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        else:
            return 'general'

    def _get_or_create_session(self, user_id: int) -> str:
        """
        Get or create a session ID for the user.

        Sessions group conversations and timeout after inactivity.
        """
        session_key = f"chat_session_{user_id}"
        session_id = cache.get(session_key)

        if not session_id:
            # Create new session
            session_id = f"session_{user_id}_{datetime.now().timestamp()}"
            cache.set(session_key, session_id, self.SESSION_TIMEOUT)

        return session_id

    def _update_session_timestamp(self, user_id: int):
        """Update session last activity timestamp."""
        session_key = f"chat_session_{user_id}"
        session_id = cache.get(session_key)

        if session_id:
            # Refresh timeout
            cache.set(session_key, session_id, self.SESSION_TIMEOUT)

    def get_conversation_stats(self, user_id: int) -> Dict[str, any]:
        """
        Get statistics about user's conversations.

        Returns:
            Dictionary with message counts, topics, etc.
        """
        from common.models import ChatMessage

        # Get all messages for user
        messages = ChatMessage.objects.filter(user_id=user_id)

        # Calculate stats
        total_messages = messages.count()
        topics = messages.values('topic').annotate(count=Count('topic')).order_by('-count')
        recent_messages = messages.filter(
            created_at__gte=datetime.now() - timedelta(days=7)
        ).count()

        return {
            'total_messages': total_messages,
            'recent_messages_7d': recent_messages,
            'top_topics': [
                {'topic': t['topic'], 'count': t['count']}
                for t in topics[:5]
            ],
            'first_message': messages.order_by('created_at').first(),
            'last_message': messages.order_by('-created_at').first(),
        }

    def clear_context(self, user_id: int):
        """Clear cached context for a user."""
        cache_key = f"chat_context_{user_id}"
        cache.delete(cache_key)

    def end_session(self, user_id: int):
        """End the current session for a user."""
        session_key = f"chat_session_{user_id}"
        cache.delete(session_key)
        self.clear_context(user_id)

    def extract_entities_from_history(self, user_id: int) -> Dict[str, List[str]]:
        """
        Extract all entities mentioned in conversation history.

        Returns:
            Dictionary mapping entity types to lists of mentioned entities
        """
        context = self.get_context(user_id)

        entities_by_type = {
            'communities': [],
            'workshops': [],
            'policies': [],
            'projects': [],
            'organizations': [],
            'regions': [],
        }

        for entity_type in context.get('entities_mentioned', []):
            # Map generic entity types to specific ones
            if entity_type in entities_by_type:
                entities_by_type[entity_type].append(entity_type)

        return entities_by_type

    def suggest_follow_up(self, user_id: int, current_topic: str) -> List[str]:
        """
        Suggest follow-up questions based on conversation history.

        Args:
            user_id: User ID
            current_topic: Current topic of conversation

        Returns:
            List of suggested follow-up questions
        """
        context = self.get_context(user_id)

        # Topic-specific suggestions
        topic_suggestions = {
            'communities': [
                "Show me MANA assessments for these communities",
                "What are the demographics?",
                "Which ones have active projects?",
            ],
            'mana': [
                "What were the key findings?",
                "Show me the recommendations",
                "How many participants attended?",
            ],
            'coordination': [
                "What sectors do they focus on?",
                "Show me their partnerships",
                "What's their coverage area?",
            ],
            'policies': [
                "Which ones are approved?",
                "Show me evidence-based policies",
                "What communities do they target?",
            ],
            'projects': [
                "What's the total budget?",
                "Show completion status",
                "Which ministry is responsible?",
            ],
        }

        suggestions = topic_suggestions.get(current_topic, [
            "Can you show me more details?",
            "What else can you tell me?",
            "How does this compare to other areas?",
        ])

        return suggestions[:3]  # Return top 3

    def get_conversation_summary(self, user_id: int, session_id: str = None) -> str:
        """
        Generate a summary of the conversation.

        Args:
            user_id: User ID
            session_id: Optional session ID to summarize specific session

        Returns:
            Natural language summary of conversation
        """
        from common.models import ChatMessage

        # Get messages
        if session_id:
            messages = ChatMessage.objects.filter(
                user_id=user_id,
                session_id=session_id,
            ).order_by('created_at')
        else:
            messages = ChatMessage.objects.filter(
                user_id=user_id,
            ).order_by('-created_at')[:self.MAX_CONTEXT_TURNS]

        if not messages:
            return "No conversation history available."

        # Build summary
        message_count = len(messages)
        topics = {}
        for msg in messages:
            topics[msg.topic] = topics.get(msg.topic, 0) + 1

        top_topic = max(topics, key=topics.get) if topics else 'general'

        summary = f"Conversation with {message_count} exchanges, "
        summary += f"primarily about {top_topic}."

        return summary


# Singleton instance
_manager = None


def get_conversation_manager() -> ConversationManager:
    """Get singleton conversation manager instance."""
    global _manager
    if _manager is None:
        _manager = ConversationManager()
    return _manager
