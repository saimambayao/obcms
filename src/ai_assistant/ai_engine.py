import json
import logging
import time
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.utils import timezone

# Optional AI dependencies - gracefully handle missing packages
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(
        "google-generativeai not installed. AI features will be disabled. "
        "Install with: pip install google-generativeai"
    )

from .cultural_context import BangsomoroCulturalContext

logger = logging.getLogger(__name__)


class GeminiAIEngine:
    """AI Engine for Google Gemini 2.5 Flash integration with OBC Management System."""

    def __init__(self):
        """Initialize the Gemini AI engine with proper configuration."""
        if not GENAI_AVAILABLE:
            logger.warning("Gemini AI Engine initialized without AI libraries - AI features disabled")
            self.model = None
            self.cultural_context = BangsomoroCulturalContext()
            self.system_prompts = {}
            return

        # Configure Gemini API
        genai.configure(api_key=settings.GOOGLE_API_KEY)

        # Initialize the model
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.8,
                top_k=40,
                max_output_tokens=2048,
            ),
        )

        # Initialize cultural context
        self.cultural_context = BangsomoroCulturalContext()

        # System prompts for different use cases
        self.system_prompts = {
            "policy_chat": self._get_policy_chat_system_prompt(),
            "document_generation": self._get_document_generation_system_prompt(),
            "analysis": self._get_analysis_system_prompt(),
            "evidence_review": self._get_evidence_review_system_prompt(),
            "cultural_guidance": self._get_cultural_guidance_system_prompt(),
        }

    def _get_policy_chat_system_prompt(self) -> str:
        """Get system prompt for policy chat conversations."""
        return f"""You are an AI assistant for the Office for Other Bangsamoro Communities (OOBC) Management System. 
        
Your role is to help users understand and work with policy recommendations for Bangsamoro communities outside BARMM.

Key responsibilities:
1. Answer questions about existing policy recommendations
2. Provide insights on policy implementation strategies
3. Suggest improvements based on evidence and best practices
4. Maintain cultural sensitivity for Bangsamoro communities
5. Reference specific data from the OBC Management System when available

Cultural Context:
{self.cultural_context.get_base_context()}

Guidelines:
- Always maintain respect for Bangsamoro culture and Islamic values
- Use inclusive language that recognizes diversity within Bangsamoro communities
- Consider the specific challenges of communities outside BARMM
- Suggest culturally appropriate solutions and implementations
- Be specific about geographic scope (Regions IX and XII primarily)

Current date: {timezone.now().strftime('%Y-%m-%d')}"""

    def _get_document_generation_system_prompt(self) -> str:
        """Get system prompt for document generation."""
        return f"""You are an AI document generator for the Office for Other Bangsamoro Communities (OOBC).

Your role is to create professional government documents including:
- Policy briefs and recommendations
- Executive summaries
- Implementation plans
- Impact assessments
- Stakeholder reports

Document Standards:
- Use professional government formatting
- Include proper citations and references
- Structure content logically with clear sections
- Maintain objectivity and evidence-based analysis
- Include cultural considerations for Bangsamoro communities

Cultural Context:
{self.cultural_context.get_base_context()}

Output Format:
- Start with document title and type
- Include executive summary
- Use numbered sections and subsections
- End with recommendations and next steps
- Include proper government document footer

Current date: {timezone.now().strftime('%Y-%m-%d')}"""

    def _get_analysis_system_prompt(self) -> str:
        """Get system prompt for policy analysis."""
        return f"""You are an AI policy analyst for the Office for Other Bangsamoro Communities (OOBC).

Your role is to analyze policy recommendations and provide insights on:
- Policy effectiveness and potential impact
- Implementation challenges and opportunities
- Stakeholder analysis and engagement strategies
- Cultural considerations and community acceptance
- Risk assessment and mitigation strategies

Analysis Framework:
1. Situation Analysis - Current state and challenges
2. Stakeholder Mapping - Key actors and their interests
3. Cultural Impact Assessment - Effects on Bangsamoro communities
4. Implementation Feasibility - Resources, timeline, barriers
5. Risk Assessment - Potential challenges and mitigation
6. Success Metrics - How to measure effectiveness

Cultural Context:
{self.cultural_context.get_base_context()}

Guidelines:
- Provide evidence-based analysis
- Consider multiple perspectives and scenarios
- Include quantitative and qualitative assessments
- Highlight cultural sensitivity requirements
- Suggest actionable recommendations

Current date: {timezone.now().strftime('%Y-%m-%d')}"""

    def _get_evidence_review_system_prompt(self) -> str:
        """Get system prompt for evidence review."""
        return f"""You are an AI evidence reviewer for the Office for Other Bangsamoro Communities (OOBC).

Your role is to review and analyze evidence supporting policy recommendations:
- Assess evidence quality and reliability
- Identify gaps in supporting data
- Suggest additional evidence needed
- Synthesize findings from multiple sources
- Validate claims and recommendations

Evidence Evaluation Criteria:
1. Relevance - How well does evidence support the policy?
2. Reliability - Source credibility and methodology quality
3. Validity - Accuracy and representativeness of data
4. Timeliness - Recency and current applicability
5. Cultural Appropriateness - Relevance to Bangsamoro communities

Cultural Context:
{self.cultural_context.get_base_context()}

Guidelines:
- Apply rigorous evidence standards
- Consider cultural context in data interpretation
- Identify potential biases or limitations
- Suggest culturally appropriate data collection methods
- Recommend evidence-based improvements

Current date: {timezone.now().strftime('%Y-%m-%d')}"""

    def _get_cultural_guidance_system_prompt(self) -> str:
        """Get system prompt for cultural guidance."""
        return f"""You are an AI cultural advisor for the Office for Other Bangsamoro Communities (OOBC).

Your role is to provide guidance on cultural considerations for policy recommendations:
- Assess cultural impact and appropriateness
- Suggest culturally sensitive implementation approaches
- Identify potential cultural barriers or conflicts
- Recommend community engagement strategies
- Ensure Islamic values and Bangsamoro traditions are respected

Cultural Framework:
{self.cultural_context.get_detailed_context()}

Key Considerations:
- Islamic principles and Shariah compatibility
- Traditional governance structures (Datu, Sultan systems)
- Ethnolinguistic diversity within Bangsamoro communities
- Historical context and trauma-informed approaches
- Economic patterns (agriculture, fishing, traditional crafts)
- Educational needs (Madaris integration, Arabic language)

Guidelines:
- Prioritize community self-determination
- Respect traditional knowledge and practices
- Suggest inclusive and participatory approaches
- Consider intergenerational perspectives
- Promote cultural preservation alongside development

Current date: {timezone.now().strftime('%Y-%m-%d')}"""

    def generate_response(
        self,
        prompt: str,
        conversation_type: str = "policy_chat",
        context_data: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """Generate AI response using Gemini 2.5 Flash."""
        start_time = time.time()

        # Check if AI is available
        if not GENAI_AVAILABLE or self.model is None:
            return {
                "success": False,
                "error": "AI features are not available - google-generativeai package not installed",
                "response": "AI features are currently disabled. Please install the required AI packages or contact your administrator.",
                "model_used": "none",
                "response_time": time.time() - start_time,
                "timestamp": timezone.now().isoformat(),
            }

        try:
            # Build conversation context
            full_prompt = self._build_conversation_prompt(
                prompt, conversation_type, context_data, conversation_history
            )

            # Generate response using Gemini
            response = self.model.generate_content(full_prompt)

            # Process response
            response_time = time.time() - start_time

            result = {
                "success": True,
                "response": response.text,
                "model_used": "gemini-2.5-flash",
                "response_time": response_time,
                "timestamp": timezone.now().isoformat(),
                "conversation_type": conversation_type,
                "metadata": {
                    "prompt_length": len(full_prompt),
                    "response_length": len(response.text),
                    "cultural_context_applied": True,
                },
            }

            # Add any extracted insights
            if conversation_type in ["analysis", "evidence_review"]:
                result["insights"] = self._extract_insights(
                    response.text, conversation_type
                )

            logger.info(f"Gemini AI response generated in {response_time:.2f}s")
            return result

        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": "I apologize, but I encountered an error while processing your request. Please try again or contact support if the issue persists.",
                "model_used": "gemini-2.5-flash",
                "response_time": time.time() - start_time,
                "timestamp": timezone.now().isoformat(),
            }

    def _build_conversation_prompt(
        self,
        prompt: str,
        conversation_type: str,
        context_data: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None,
    ) -> str:
        """Build the full conversation prompt with system context."""

        # Start with system prompt
        full_prompt = self.system_prompts.get(
            conversation_type, self.system_prompts["policy_chat"]
        )

        # Add specific context data if provided
        if context_data:
            full_prompt += "\n\nCurrent Context:\n"
            if "policy" in context_data:
                policy = context_data["policy"]
                full_prompt += f"Policy: {policy.get('title', '')}\n"
                full_prompt += f"Category: {policy.get('category', '')}\n"
                full_prompt += f"Status: {policy.get('status', '')}\n"
                full_prompt += f"Description: {policy.get('description', '')}\n"

            if "communities" in context_data:
                communities = context_data["communities"]
                full_prompt += f"Related Communities: {', '.join(communities)}\n"

        # Add conversation history if provided
        if conversation_history:
            full_prompt += "\n\nConversation History:\n"
            for msg in conversation_history[-5:]:  # Last 5 messages for context
                role = msg.get("role", "user")
                content = msg.get("content", "")
                full_prompt += f"{role.title()}: {content}\n"

        # Add current user prompt
        full_prompt += f"\n\nUser: {prompt}\n\nAssistant:"

        return full_prompt

    def _extract_insights(
        self, response_text: str, conversation_type: str
    ) -> List[Dict]:
        """Extract structured insights from AI response."""
        insights = []

        try:
            # Look for key insights patterns in the response
            if conversation_type == "analysis":
                # Extract policy analysis insights
                if "recommendation" in response_text.lower():
                    insights.append(
                        {
                            "type": "recommendation",
                            "content": self._extract_recommendations(response_text),
                        }
                    )

                if "risk" in response_text.lower():
                    insights.append(
                        {
                            "type": "risk_assessment",
                            "content": self._extract_risks(response_text),
                        }
                    )

            elif conversation_type == "evidence_review":
                # Extract evidence quality insights
                if "evidence" in response_text.lower():
                    insights.append(
                        {
                            "type": "evidence_quality",
                            "content": self._extract_evidence_assessment(response_text),
                        }
                    )

        except Exception as e:
            logger.warning(f"Could not extract insights: {str(e)}")

        return insights

    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations from response text."""
        recommendations = []
        lines = text.split("\n")

        for line in lines:
            line = line.strip()
            if any(
                keyword in line.lower()
                for keyword in ["recommend", "suggest", "should", "propose"]
            ):
                if len(line) > 20:  # Filter out very short lines
                    recommendations.append(line)

        return recommendations[:5]  # Limit to top 5

    def _extract_risks(self, text: str) -> List[str]:
        """Extract risks from response text."""
        risks = []
        lines = text.split("\n")

        for line in lines:
            line = line.strip()
            if any(
                keyword in line.lower()
                for keyword in ["risk", "challenge", "concern", "barrier"]
            ):
                if len(line) > 20:
                    risks.append(line)

        return risks[:5]

    def _extract_evidence_assessment(self, text: str) -> Dict[str, Any]:
        """Extract evidence assessment from response text."""
        assessment = {
            "quality_indicators": [],
            "gaps_identified": [],
            "recommendations": [],
        }

        lines = text.split("\n")
        current_section = None

        for line in lines:
            line = line.strip().lower()
            if "quality" in line:
                current_section = "quality_indicators"
            elif "gap" in line or "missing" in line:
                current_section = "gaps_identified"
            elif "recommend" in line:
                current_section = "recommendations"
            elif current_section and len(line) > 20:
                assessment[current_section].append(line)

        return assessment

    def generate_document(
        self,
        document_type: str,
        policy_data: Dict,
        additional_context: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Generate a structured document using Gemini."""

        # Check if AI is available
        if not GENAI_AVAILABLE or self.model is None:
            return {
                "success": False,
                "error": "AI features are not available",
                "response": "AI document generation is currently disabled.",
            }

        prompt = self._build_document_prompt(
            document_type, policy_data, additional_context
        )

        response = self.generate_response(
            prompt=prompt,
            conversation_type="document_generation",
            context_data={"policy": policy_data},
        )

        if response["success"]:
            # Parse document structure
            content = response["response"]
            sections = self._parse_document_sections(content)

            response["document_structure"] = {
                "title": self._extract_title(content),
                "sections": sections,
                "key_points": self._extract_key_points(content),
            }

        return response

    def _build_document_prompt(
        self,
        document_type: str,
        policy_data: Dict,
        additional_context: Optional[Dict] = None,
    ) -> str:
        """Build prompt for document generation."""

        prompts = {
            "policy_brief": f"""Generate a professional policy brief for the following policy recommendation:

Title: {policy_data.get('title', '')}
Category: {policy_data.get('category', '')}
Description: {policy_data.get('description', '')}
Problem Statement: {policy_data.get('problem_statement', '')}
Proposed Solution: {policy_data.get('proposed_solution', '')}
Expected Outcomes: {policy_data.get('expected_outcomes', '')}

Create a comprehensive policy brief that includes:
1. Executive Summary
2. Problem Analysis
3. Policy Recommendation
4. Implementation Strategy
5. Expected Impact
6. Cultural Considerations for Bangsamoro Communities
7. Resource Requirements
8. Risk Assessment
9. Monitoring and Evaluation
10. Conclusion and Next Steps

Ensure the document is professional, evidence-based, and culturally sensitive.""",
            "executive_summary": f"""Create an executive summary for the policy recommendation:

{policy_data.get('title', '')}

Key details:
- Category: {policy_data.get('category', '')}
- Status: {policy_data.get('status', '')}
- Priority: {policy_data.get('priority', '')}
- Description: {policy_data.get('description', '')}
- Expected Outcomes: {policy_data.get('expected_outcomes', '')}

The executive summary should be concise (1-2 pages) and include:
1. Policy Overview
2. Key Recommendations
3. Expected Benefits
4. Implementation Timeline
5. Resource Requirements
6. Success Metrics""",
        }

        return prompts.get(document_type, prompts["policy_brief"])

    def _parse_document_sections(self, content: str) -> List[Dict]:
        """Parse document content into structured sections."""
        sections = []
        lines = content.split("\n")
        current_section = None
        current_content = []

        for line in lines:
            line = line.strip()

            # Check if line is a section header (numbered or has header indicators)
            if (
                line
                and (line[0].isdigit() and "." in line[:5])
                or line.startswith("#")
                or line.isupper()
                and len(line) < 100
            ):

                # Save previous section if exists
                if current_section:
                    sections.append(
                        {
                            "title": current_section,
                            "content": "\n".join(current_content).strip(),
                        }
                    )

                # Start new section
                current_section = line
                current_content = []
            else:
                if line:  # Add non-empty lines to current section
                    current_content.append(line)

        # Add last section
        if current_section:
            sections.append(
                {
                    "title": current_section,
                    "content": "\n".join(current_content).strip(),
                }
            )

        return sections

    def _extract_title(self, content: str) -> str:
        """Extract document title from content."""
        lines = content.split("\n")
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and not line.startswith("#"):
                return line
        return "Generated Document"

    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from document content."""
        key_points = []
        lines = content.split("\n")

        for line in lines:
            line = line.strip()
            # Look for bullet points or numbered items
            if (
                line.startswith("•")
                or line.startswith("-")
                or line.startswith("*")
                or (line and line[0].isdigit() and "." in line[:5])
            ):
                if len(line) > 10:  # Filter short lines
                    key_points.append(line)

        return key_points[:10]  # Limit to top 10 key points
