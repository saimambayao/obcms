"""
Response Analyzer
AI-powered analysis of MANA workshop responses
"""

import json
import logging
from typing import Dict, List, Optional

from django.core.cache import cache

from ai_assistant.ai_engine import GeminiAIEngine
from ai_assistant.cultural_context import BangsomoroCulturalContext

logger = logging.getLogger(__name__)


class ResponseAnalyzer:
    """Analyze MANA workshop responses using AI"""

    def __init__(self):
        """Initialize the analyzer with Gemini AI engine"""
        self.ai_engine = GeminiAIEngine()
        self.cultural_context = BangsomoroCulturalContext()

    def analyze_question_responses(
        self, question: str, responses: List[str], question_type: str = "text"
    ) -> Dict:
        """
        Analyze all responses to a single workshop question

        Args:
            question: The question text
            responses: List of response texts from participants
            question_type: Type of question (text, multiple_choice, etc.)

        Returns:
            dict: {
                'summary': 'Common themes across responses',
                'key_points': ['point1', 'point2', ...],
                'sentiment': 'positive/neutral/negative',
                'action_items': ['action1', 'action2'],
                'confidence': 0.85
            }
        """
        if not responses:
            return {
                "summary": "No responses available",
                "key_points": [],
                "sentiment": "neutral",
                "action_items": [],
                "confidence": 0.0,
            }

        # Check cache first
        cache_key = f"mana_response_analysis_{hash(question + str(responses))}"
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Using cached analysis for question: {question[:50]}...")
            return cached_result

        # Prepare cultural context
        cultural_guidelines = self.cultural_context.get_base_context()

        # Build analysis prompt
        prompt = f"""
{cultural_guidelines}

TASK: Analyze community workshop responses with cultural sensitivity

QUESTION ASKED: "{question}"

COMMUNITY RESPONSES ({len(responses)} total):
{self._format_responses(responses)}

ANALYSIS REQUIREMENTS:
1. Summary: Provide a concise 2-3 sentence summary of common themes
2. Key Points: Extract 3-5 most important points mentioned by participants
3. Sentiment: Overall sentiment (positive/neutral/negative/mixed)
4. Action Items: Suggest 2-4 concrete action items based on responses
5. Confidence: Your confidence in this analysis (0-1)

CULTURAL CONSIDERATIONS:
- Respect Islamic values and Bangsamoro traditions
- Acknowledge community-specific contexts
- Use culturally appropriate terminology
- Consider historical and social factors affecting OBC communities

OUTPUT FORMAT (JSON):
{{
    "summary": "Clear, concise summary",
    "key_points": ["point 1", "point 2", "point 3"],
    "sentiment": "positive|neutral|negative|mixed",
    "action_items": ["action 1", "action 2"],
    "confidence": 0.85
}}
"""

        try:
            # Generate analysis using Gemini
            response = self.ai_engine.model.generate_content(prompt)
            result_text = response.text.strip()

            # Clean JSON from markdown code blocks if present
            if result_text.startswith("```json"):
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif result_text.startswith("```"):
                result_text = result_text.split("```")[1].split("```")[0].strip()

            # Parse JSON response
            analysis = json.loads(result_text)

            # Validate structure
            analysis.setdefault("summary", "Analysis completed")
            analysis.setdefault("key_points", [])
            analysis.setdefault("sentiment", "neutral")
            analysis.setdefault("action_items", [])
            analysis.setdefault("confidence", 0.7)

            # Cache result for 24 hours
            cache.set(cache_key, analysis, timeout=86400)

            logger.info(
                f"Successfully analyzed {len(responses)} responses for question"
            )
            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"Raw response: {result_text}")
            return {
                "summary": "Analysis completed but formatting error occurred",
                "key_points": ["Error parsing detailed analysis"],
                "sentiment": "neutral",
                "action_items": ["Review responses manually"],
                "confidence": 0.3,
            }

        except Exception as e:
            logger.error(f"Error analyzing responses: {e}")
            return {
                "summary": f"Error during analysis: {str(e)}",
                "key_points": [],
                "sentiment": "neutral",
                "action_items": ["Review system logs", "Retry analysis"],
                "confidence": 0.0,
            }

    def aggregate_workshop_insights(self, workshop_id: int) -> Dict:
        """
        Aggregate insights from entire workshop

        Args:
            workshop_id: Workshop activity ID

        Returns:
            dict: Comprehensive workshop insights
        """
        from mana.models import WorkshopActivity, WorkshopResponse

        try:
            workshop = WorkshopActivity.objects.get(id=workshop_id)
            responses = WorkshopResponse.objects.filter(
                workshop=workshop, status="submitted"
            )

            if not responses.exists():
                return {
                    "status": "no_data",
                    "message": "No submitted responses available",
                    "workshop_title": workshop.workshop_type,
                    "total_responses": 0,
                }

            # Group responses by question
            question_groups = {}
            for response in responses:
                question_id = response.question_id
                if question_id not in question_groups:
                    question_groups[question_id] = []

                # Extract text from response_data
                response_text = self._extract_response_text(response.response_data)
                if response_text:
                    question_groups[question_id].append(response_text)

            # Analyze each question group
            question_analyses = {}
            for question_id, response_texts in question_groups.items():
                # Try to get question text
                question_text = f"Question {question_id}"

                analysis = self.analyze_question_responses(
                    question_text, response_texts
                )
                question_analyses[question_id] = {
                    "question": question_text,
                    "response_count": len(response_texts),
                    "analysis": analysis,
                }

            # Generate overall workshop summary
            overall_summary = self._generate_overall_summary(
                workshop, question_analyses
            )

            return {
                "status": "success",
                "workshop_title": workshop.workshop_type,
                "total_responses": responses.count(),
                "question_count": len(question_groups),
                "question_analyses": question_analyses,
                "overall_summary": overall_summary,
                "analyzed_at": str(timezone.now()),
            }

        except WorkshopActivity.DoesNotExist:
            logger.error(f"Workshop {workshop_id} not found")
            return {"status": "error", "message": "Workshop not found"}

        except Exception as e:
            logger.error(f"Error aggregating workshop insights: {e}")
            return {"status": "error", "message": str(e)}

    def _format_responses(self, responses: List[str]) -> str:
        """Format responses for AI prompt"""
        formatted = []
        for i, response in enumerate(responses[:50], 1):  # Limit to 50 for tokens
            # Truncate very long responses
            if len(response) > 500:
                response = response[:497] + "..."
            formatted.append(f"{i}. {response}")

        if len(responses) > 50:
            formatted.append(
                f"\n... and {len(responses) - 50} more responses (showing first 50)"
            )

        return "\n".join(formatted)

    def _extract_response_text(self, response_data: Dict) -> Optional[str]:
        """Extract text content from response data JSON"""
        if isinstance(response_data, str):
            return response_data

        if isinstance(response_data, dict):
            # Try common field names
            for field in ["text", "answer", "response", "value", "content"]:
                if field in response_data:
                    return str(response_data[field])

            # If it's a dict with nested structure, convert to string
            return json.dumps(response_data)

        return str(response_data)

    def _generate_overall_summary(
        self, workshop, question_analyses: Dict
    ) -> Dict:
        """Generate overall workshop summary from question analyses"""
        # Aggregate key points
        all_key_points = []
        all_action_items = []
        sentiments = []

        for q_analysis in question_analyses.values():
            analysis = q_analysis["analysis"]
            all_key_points.extend(analysis.get("key_points", []))
            all_action_items.extend(analysis.get("action_items", []))
            sentiments.append(analysis.get("sentiment", "neutral"))

        # Determine overall sentiment
        if sentiments:
            sentiment_counts = {
                "positive": sentiments.count("positive"),
                "neutral": sentiments.count("neutral"),
                "negative": sentiments.count("negative"),
                "mixed": sentiments.count("mixed"),
            }
            overall_sentiment = max(sentiment_counts, key=sentiment_counts.get)
        else:
            overall_sentiment = "neutral"

        return {
            "summary": f"Workshop completed with {len(question_analyses)} question areas analyzed",
            "total_key_points": len(all_key_points),
            "total_action_items": len(all_action_items),
            "overall_sentiment": overall_sentiment,
            "top_key_points": all_key_points[:10],  # Top 10 key points
            "recommended_actions": all_action_items[:8],  # Top 8 actions
        }


# Import timezone at module level (fixing circular import)
from django.utils import timezone
