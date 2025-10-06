"""
Meeting Intelligence Service

Extract insights from meeting minutes, generate summaries, and auto-create action items.
"""

import json
import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache

from ai_assistant.services import GeminiService
from coordination.models import StakeholderEngagement

User = get_user_model()


class MeetingIntelligence:
    """Extract insights from meetings and transcripts"""

    def __init__(self):
        self.gemini = GeminiService()

    def summarize_meeting(self, meeting_id: str) -> Dict:
        """
        Generate executive summary of coordination meeting

        Args:
            meeting_id: UUID of StakeholderEngagement

        Returns:
            {
                'summary': '...',
                'key_decisions': [...],
                'action_items': [...],
                'attendees_summary': '...',
                'next_steps': [...],
                'sentiment': 'positive/neutral/negative',
                'topics_discussed': [...]
            }
        """
        # Check cache
        cache_key = f"meeting_summary_{meeting_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        try:
            meeting = StakeholderEngagement.objects.select_related(
                'community',
                'engagement_type',
                'created_by'
            ).prefetch_related('facilitators').get(id=meeting_id)
        except StakeholderEngagement.DoesNotExist:
            return {'error': 'Meeting not found'}

        # Build comprehensive meeting context
        meeting_context = self._build_meeting_context(meeting)

        # Generate summary using AI
        prompt = self._build_summary_prompt(meeting_context)

        try:
            response = self.gemini.generate_text(prompt, temperature=0.4)
            summary = json.loads(response)

            # Add metadata
            summary['meeting_id'] = str(meeting_id)
            summary['meeting_title'] = meeting.title
            summary['meeting_date'] = meeting.planned_date.isoformat()

            # Cache for 7 days
            cache.set(cache_key, summary, timeout=86400 * 7)

            return summary

        except Exception as e:
            # Fallback to basic summary
            return self._fallback_summary(meeting)

    def _build_meeting_context(self, meeting: StakeholderEngagement) -> Dict:
        """Build comprehensive meeting context"""
        facilitators = meeting.facilitators.all()

        return {
            'title': meeting.title,
            'type': meeting.engagement_type.name,
            'date': meeting.planned_date.strftime('%Y-%m-%d'),
            'community': meeting.community.name,
            'objectives': meeting.objectives,
            'facilitators': [f.get_full_name() or f.username for f in facilitators],
            'target_participants': meeting.target_participants,
            'actual_participants': meeting.actual_participants,
            'minutes': meeting.meeting_minutes or 'No minutes recorded',
            'outcomes': meeting.key_outcomes or 'No outcomes recorded',
            'feedback': meeting.feedback_summary or 'No feedback recorded',
            'action_items': meeting.action_items or 'No action items recorded',
        }

    def _build_summary_prompt(self, context: Dict) -> str:
        """Build AI prompt for meeting summarization"""
        return f"""
Summarize this coordination meeting:

Meeting: {context['title']}
Type: {context['type']}
Date: {context['date']}
Community: {context['community']}

Objectives:
{context['objectives']}

Facilitators: {', '.join(context['facilitators'])}
Participants: {context['actual_participants']} of {context['target_participants']} expected

Minutes:
{context['minutes']}

Outcomes:
{context['outcomes']}

Feedback:
{context['feedback']}

Action Items:
{context['action_items']}

Provide a comprehensive analysis:
1. Executive summary (3-4 sentences capturing key points)
2. Key decisions made (list of concrete decisions)
3. Action items with owners (extract from minutes/action items)
4. Attendees summary (participation analysis)
5. Next steps (logical follow-up actions)
6. Sentiment (positive/neutral/negative based on feedback and outcomes)
7. Topics discussed (main discussion topics)

Return as JSON with keys: summary, key_decisions, action_items, attendees_summary, next_steps, sentiment, topics_discussed
"""

    def _fallback_summary(self, meeting: StakeholderEngagement) -> Dict:
        """Fallback summary when AI fails"""
        return {
            'meeting_id': str(meeting.id),
            'meeting_title': meeting.title,
            'meeting_date': meeting.planned_date.isoformat(),
            'summary': f"{meeting.title} was held on {meeting.planned_date.strftime('%B %d, %Y')} "
                      f"in {meeting.community.name}. {meeting.actual_participants} participants attended.",
            'key_decisions': self._extract_decisions_simple(meeting.meeting_minutes or ''),
            'action_items': self._extract_action_items_simple(meeting.action_items or ''),
            'attendees_summary': f"{meeting.actual_participants} of {meeting.target_participants} expected participants attended",
            'next_steps': ['Follow up on action items', 'Schedule next meeting'],
            'sentiment': 'neutral',
            'topics_discussed': [meeting.engagement_type.name]
        }

    def _extract_decisions_simple(self, text: str) -> List[str]:
        """Simple extraction of decisions from text"""
        decisions = []
        # Look for decision markers
        patterns = [
            r'decided to (.+?)[\.\n]',
            r'decision: (.+?)[\.\n]',
            r'agreed to (.+?)[\.\n]',
            r'resolved to (.+?)[\.\n]'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            decisions.extend(matches)

        return decisions[:5] if decisions else ['No explicit decisions recorded']

    def _extract_action_items_simple(self, text: str) -> List[str]:
        """Simple extraction of action items"""
        items = []
        # Split by line and look for action patterns
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if any(marker in line.lower() for marker in ['action:', 'todo:', '- ', '* ']):
                items.append(line.lstrip('- *'))

        return items[:10] if items else ['No action items specified']

    def extract_action_items(self, meeting_id: str) -> List[Dict]:
        """
        Extract structured action items from meeting

        Returns:
            [
                {
                    'task': 'Follow up with LGU',
                    'owner': 'John Doe',
                    'deadline': '2025-10-15',
                    'priority': 'HIGH',
                    'status': 'NOT_STARTED'
                },
                ...
            ]
        """
        try:
            meeting = StakeholderEngagement.objects.get(id=meeting_id)
        except StakeholderEngagement.DoesNotExist:
            return []

        # Build prompt for structured extraction
        prompt = f"""
Extract structured action items from this meeting:

Title: {meeting.title}
Minutes: {meeting.meeting_minutes or 'N/A'}
Action Items: {meeting.action_items or 'N/A'}
Outcomes: {meeting.key_outcomes or 'N/A'}

For each action item, extract:
1. Task description (what needs to be done)
2. Owner (person responsible, or "Unassigned")
3. Deadline (date, or estimate based on urgency, format: YYYY-MM-DD)
4. Priority (HIGH/MEDIUM/LOW based on context)
5. Status (always "NOT_STARTED" for new items)

Return as JSON array with keys: task, owner, deadline, priority, status
If no clear action items, return empty array.
"""

        try:
            response = self.gemini.generate_text(prompt, temperature=0.2)
            action_items = json.loads(response)
            return action_items if isinstance(action_items, list) else []
        except Exception as e:
            # Fallback: extract from text
            return self._extract_actions_fallback(meeting)

    def _extract_actions_fallback(self, meeting: StakeholderEngagement) -> List[Dict]:
        """Fallback action item extraction"""
        items = []
        text = meeting.action_items or meeting.meeting_minutes or ''

        # Simple pattern matching
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if any(marker in line.lower() for marker in ['action:', 'todo:', 'follow up']):
                items.append({
                    'task': line[:200],  # Limit length
                    'owner': 'Unassigned',
                    'deadline': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                    'priority': 'MEDIUM',
                    'status': 'NOT_STARTED'
                })

        return items[:10]  # Limit to 10 items

    def auto_create_tasks(self, meeting_id: str) -> List:
        """
        Automatically create WorkItem tasks from meeting action items

        Args:
            meeting_id: StakeholderEngagement UUID

        Returns:
            List of created WorkItem objects
        """
        from common.models import WorkItem

        action_items = self.extract_action_items(meeting_id)

        try:
            meeting = StakeholderEngagement.objects.get(id=meeting_id)
        except StakeholderEngagement.DoesNotExist:
            return []

        created_tasks = []

        for item in action_items:
            # Try to find user by name
            assigned_user = None
            if item['owner'] != 'Unassigned':
                # Try to match user by name
                name_parts = item['owner'].split()
                if name_parts:
                    users = User.objects.filter(
                        Q(first_name__icontains=name_parts[0]) |
                        Q(last_name__icontains=name_parts[-1])
                    )
                    if users.exists():
                        assigned_user = users.first()

            # Map priority
            priority_map = {
                'HIGH': 'high',
                'MEDIUM': 'medium',
                'LOW': 'low'
            }

            # Create WorkItem
            try:
                task = WorkItem.objects.create(
                    title=item['task'][:200],  # Limit title length
                    description=f"Action item from meeting: {meeting.title}\n\n"
                               f"Meeting Date: {meeting.planned_date.strftime('%Y-%m-%d')}\n"
                               f"Community: {meeting.community.name}",
                    assigned_to=assigned_user or meeting.created_by,
                    due_date=datetime.strptime(item['deadline'], '%Y-%m-%d').date(),
                    priority=priority_map.get(item['priority'], 'medium'),
                    status='todo',
                    created_by=meeting.created_by
                )
                created_tasks.append(task)
            except Exception as e:
                # Skip invalid items
                continue

        return created_tasks

    def analyze_meeting_effectiveness(self, meeting_id: str) -> Dict:
        """
        Analyze meeting effectiveness based on outcomes, participation, and feedback

        Returns:
            {
                'effectiveness_score': 0.85,
                'participation_rate': 0.95,
                'outcome_quality': 'high',
                'feedback_sentiment': 'positive',
                'recommendations': [...]
            }
        """
        try:
            meeting = StakeholderEngagement.objects.get(id=meeting_id)
        except StakeholderEngagement.DoesNotExist:
            return {'error': 'Meeting not found'}

        # Calculate participation rate
        participation_rate = (
            meeting.actual_participants / meeting.target_participants
            if meeting.target_participants > 0 else 0
        )

        # Analyze outcomes
        has_outcomes = bool(meeting.key_outcomes)
        has_action_items = bool(meeting.action_items)
        has_feedback = bool(meeting.feedback_summary)

        # Calculate effectiveness score
        score = 0.0
        if participation_rate >= 0.8:
            score += 0.3
        elif participation_rate >= 0.6:
            score += 0.2
        elif participation_rate >= 0.4:
            score += 0.1

        if has_outcomes:
            score += 0.3
        if has_action_items:
            score += 0.2
        if has_feedback:
            score += 0.2

        # Determine outcome quality
        if has_outcomes and has_action_items:
            outcome_quality = 'high'
        elif has_outcomes or has_action_items:
            outcome_quality = 'medium'
        else:
            outcome_quality = 'low'

        # Generate recommendations
        recommendations = []
        if participation_rate < 0.6:
            recommendations.append('Improve participant engagement and outreach')
        if not has_outcomes:
            recommendations.append('Document clear meeting outcomes and decisions')
        if not has_action_items:
            recommendations.append('Define specific action items with owners and deadlines')
        if not has_feedback:
            recommendations.append('Collect participant feedback for continuous improvement')

        if score >= 0.8:
            recommendations.append('Excellent meeting execution - replicate this approach')

        return {
            'effectiveness_score': round(score, 2),
            'participation_rate': round(participation_rate, 2),
            'outcome_quality': outcome_quality,
            'feedback_sentiment': 'positive' if meeting.satisfaction_rating and meeting.satisfaction_rating >= 4 else 'neutral',
            'recommendations': recommendations or ['Meeting was well-executed'],
            'metrics': {
                'target_participants': meeting.target_participants,
                'actual_participants': meeting.actual_participants,
                'has_outcomes': has_outcomes,
                'has_action_items': has_action_items,
                'satisfaction_rating': meeting.satisfaction_rating
            }
        }

    def generate_meeting_report(self, meeting_id: str) -> str:
        """
        Generate a formatted meeting report

        Returns:
            Markdown-formatted meeting report
        """
        summary = self.summarize_meeting(meeting_id)
        effectiveness = self.analyze_meeting_effectiveness(meeting_id)

        try:
            meeting = StakeholderEngagement.objects.get(id=meeting_id)
        except StakeholderEngagement.DoesNotExist:
            return "Meeting not found"

        report = f"""
# Meeting Report: {meeting.title}

**Date:** {meeting.planned_date.strftime('%B %d, %Y')}
**Community:** {meeting.community.name}
**Type:** {meeting.engagement_type.name}

---

## Executive Summary

{summary.get('summary', 'No summary available')}

---

## Participation

- **Target Participants:** {meeting.target_participants}
- **Actual Participants:** {meeting.actual_participants}
- **Participation Rate:** {effectiveness['participation_rate'] * 100:.0f}%

---

## Key Decisions

{self._format_list(summary.get('key_decisions', []))}

---

## Action Items

{self._format_action_items(summary.get('action_items', []))}

---

## Next Steps

{self._format_list(summary.get('next_steps', []))}

---

## Effectiveness Analysis

- **Overall Score:** {effectiveness['effectiveness_score'] * 100:.0f}%
- **Outcome Quality:** {effectiveness['outcome_quality'].capitalize()}
- **Sentiment:** {effectiveness['feedback_sentiment'].capitalize()}

### Recommendations

{self._format_list(effectiveness.get('recommendations', []))}

---

*Report generated on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        return report.strip()

    def _format_list(self, items: List[str]) -> str:
        """Format list items as markdown"""
        if not items:
            return "*None*"
        return '\n'.join([f"- {item}" for item in items])

    def _format_action_items(self, items: List) -> str:
        """Format action items as markdown"""
        if not items:
            return "*No action items*"

        if isinstance(items[0], dict):
            return '\n'.join([
                f"- **{item.get('task', 'N/A')}** (Owner: {item.get('owner', 'Unassigned')}, "
                f"Due: {item.get('deadline', 'TBD')})"
                for item in items
            ])
        else:
            return self._format_list(items)
