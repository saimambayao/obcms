"""
AI-Powered Policy Generator

Generates evidence-based policy recommendations using AI and cross-module evidence.
Integrates with OBCMS cultural context and BARMM governance standards.
"""

import json
import logging
from typing import Dict, List, Optional

from ai_assistant.services import GeminiService
from .evidence_gatherer import get_evidence_gatherer

logger = logging.getLogger(__name__)


# Bangsamoro Cultural Context for Policy Generation
BANGSAMORO_CULTURAL_CONTEXT = """
BANGSAMORO CULTURAL CONTEXT FOR POLICY DEVELOPMENT:

1. Islamic Values and Shariah Principles
   - Respect for Islamic traditions and Shariah-compliant approaches
   - Integration of Madaris (Islamic schools) in education policies
   - Halal certification and Islamic economic principles
   - Accommodation of religious practices and observances

2. Customary Law and Traditions
   - Recognition of customary law (adat) alongside Shariah
   - Traditional governance structures (datus, sultans)
   - Tribal conflict resolution mechanisms
   - Cultural preservation and heritage protection

3. Ethnolinguistic Diversity
   - Major groups: Maguindanaon, Maranao, Tausug, Sama, Yakan, and others
   - Language considerations in service delivery
   - Cultural sensitivity in program implementation
   - Inter-ethnic harmony and cohesion

4. Historical Context
   - Mindanao conflict and peace process awareness
   - Bangsamoro Organic Law (BOL) implementation
   - Transitional justice and reconciliation
   - Decolonization and self-determination

5. Geographic and Economic Context
   - Rural and coastal community focus
   - Agriculture and fishing livelihoods
   - Limited infrastructure in remote areas
   - Economic development challenges

6. BARMM Governance Structure
   - Parliamentary system with Chief Minister
   - Regional ministries and agencies
   - Intergovernmental relations with national government
   - Coordination with LGUs and traditional leaders
"""


class PolicyGenerator:
    """Generate evidence-based policy recommendations using AI"""

    def __init__(self):
        """Initialize policy generator with AI services"""
        self.gemini = GeminiService(temperature=0.6)  # Balanced creativity/accuracy
        self.evidence_gatherer = get_evidence_gatherer()

    def generate_policy_recommendation(
        self,
        issue: str,
        evidence: Optional[Dict] = None,
        target_communities: Optional[List[int]] = None,
        category: str = 'social_development',
        scope: str = 'regional'
    ) -> Dict:
        """
        Auto-generate comprehensive policy recommendation using AI

        Args:
            issue: Policy issue/topic (e.g., "Healthcare access for coastal communities")
            evidence: Pre-gathered evidence dict (if None, will gather automatically)
            target_communities: List of community IDs
            category: Policy category (economic_development, social_development, etc.)
            scope: Policy scope (national, regional, provincial, etc.)

        Returns:
            {
                'title': '...',
                'reference_number': 'OOBC-POL-2025-0001',
                'executive_summary': '...',
                'problem_statement': '...',
                'rationale': '...',
                'proposed_solution': '...',
                'policy_objectives': '...',
                'expected_outcomes': '...',
                'implementation_strategy': '...',
                'budget_implications': '...',
                'success_metrics': '...',
                'citations': [...]
            }
        """
        logger.info(f"Generating policy recommendation for: {issue}")

        # Gather evidence if not provided
        if evidence is None:
            evidence = self.evidence_gatherer.gather_evidence(issue)
            evidence_synthesis = self.evidence_gatherer.synthesize_evidence(evidence, issue)
        else:
            evidence_synthesis = self.evidence_gatherer.synthesize_evidence(evidence, issue)

        # Build comprehensive prompt
        prompt = f"""
{BANGSAMORO_CULTURAL_CONTEXT}

TASK: Generate a comprehensive policy recommendation for the Office for Other Bangsamoro Communities (OOBC).

POLICY ISSUE: {issue}

POLICY CONTEXT:
- Category: {category}
- Scope: {scope}
- Target Communities: {len(target_communities) if target_communities else 'Multiple'} Bangsamoro communities outside BARMM

EVIDENCE BASE:
{json.dumps(evidence_synthesis, indent=2)}

EVIDENCE SOURCES:
- MANA Assessments: {len(evidence.get('mana_assessments', []))}
- Community Data: {len(evidence.get('community_data', []))}
- Project Outcomes: {len(evidence.get('project_outcomes', []))}
- Policy Precedents: {len(evidence.get('policy_precedents', []))}

INSTRUCTIONS:
Generate a comprehensive, evidence-based policy recommendation with the following components:

1. TITLE (concise, action-oriented, 8-12 words)
   Example: "Expanding Healthcare Access for Coastal Bangsamoro Communities"

2. EXECUTIVE SUMMARY (150-200 words)
   - Overview of the issue
   - Proposed solution summary
   - Expected impact
   - Implementation timeframe

3. PROBLEM STATEMENT (300-400 words)
   - Clear articulation of the problem
   - Data and evidence supporting the problem
   - Root causes analysis
   - Current gaps in services/policies

4. RATIONALE (200-300 words)
   - Why this policy is needed
   - Alignment with BARMM priorities
   - Cultural and contextual justification
   - Evidence base supporting the approach

5. PROPOSED SOLUTION (400-500 words)
   - Detailed description of the policy intervention
   - Key components and mechanisms
   - Target beneficiaries
   - Geographic scope

6. POLICY OBJECTIVES (3-5 SMART objectives)
   - Specific, Measurable, Achievable, Relevant, Time-bound
   - Each objective should be clear and quantifiable

7. EXPECTED OUTCOMES (250-300 words)
   - Short-term outcomes (1-2 years)
   - Long-term outcomes (3-5 years)
   - Quantified impact where possible
   - Alignment with SDGs and BARMM development goals

8. IMPLEMENTATION STRATEGY (300-400 words)
   - Implementation phases
   - Responsible agencies/partners
   - Timeline and milestones
   - Resource mobilization plan

9. BUDGET IMPLICATIONS (200-250 words)
   - Estimated total cost
   - Budget breakdown by major component
   - Funding sources
   - Cost-benefit analysis summary

10. SUCCESS METRICS (5-7 specific indicators)
    - Key Performance Indicators (KPIs)
    - Baseline, target, and measurement method
    - Monitoring and evaluation framework

11. CITATIONS (numbered list)
    - Reference to evidence sources used
    - MANA assessments, community data, research, etc.

REQUIREMENTS:
- Use culturally appropriate language for Bangsamoro context
- Ensure alignment with Islamic values where relevant
- Reference specific evidence sources
- Provide realistic, implementable solutions
- Include risk mitigation considerations
- Address equity and inclusion
- Consider sustainability

OUTPUT FORMAT: Return as valid JSON with the following structure:
{{
    "title": "...",
    "executive_summary": "...",
    "problem_statement": "...",
    "rationale": "...",
    "proposed_solution": "...",
    "policy_objectives": "...",
    "expected_outcomes": "...",
    "implementation_strategy": "...",
    "budget_implications": "...",
    "success_metrics": "...",
    "estimated_cost": 5000000,
    "citations": ["Citation 1", "Citation 2", ...]
}}
"""

        response = self.gemini.generate_text(
            prompt,
            use_cache=False,  # Don't cache policy generation
            include_cultural_context=True
        )

        if response['success']:
            try:
                # Parse JSON response
                policy_data = json.loads(response['text'])

                # Add metadata
                policy_data['generated_by_ai'] = True
                policy_data['evidence_sources_count'] = evidence.get('total_citations', 0)
                policy_data['evidence_strength'] = evidence_synthesis.get('strength_of_evidence', 'unknown')
                policy_data['generation_cost'] = response['cost']
                policy_data['tokens_used'] = response['tokens_used']

                logger.info(f"Policy recommendation generated successfully: {policy_data.get('title')}")
                return policy_data

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                return {
                    'error': 'Failed to parse AI response',
                    'raw_response': response['text']
                }
        else:
            logger.error(f"Policy generation failed: {response.get('error')}")
            return {
                'error': response.get('error'),
                'success': False
            }

    def refine_policy(
        self,
        policy_data: Dict,
        feedback: str,
        focus_areas: Optional[List[str]] = None
    ) -> Dict:
        """
        Iteratively refine policy based on stakeholder feedback

        Args:
            policy_data: Existing policy data dict
            feedback: Stakeholder feedback text
            focus_areas: Specific areas to refine (e.g., ['budget', 'implementation'])

        Returns:
            Updated policy dict with refined sections
        """
        logger.info("Refining policy based on feedback")

        focus_section = "all sections"
        if focus_areas:
            focus_section = ", ".join(focus_areas)

        prompt = f"""
TASK: Refine this policy recommendation based on stakeholder feedback.

CURRENT POLICY:
Title: {policy_data.get('title')}

{json.dumps(policy_data, indent=2)}

STAKEHOLDER FEEDBACK:
{feedback}

FOCUS AREAS FOR REFINEMENT: {focus_section}

INSTRUCTIONS:
1. Carefully review the feedback
2. Identify specific areas needing improvement
3. Revise the policy to address the feedback
4. Maintain the overall structure and objectives
5. Ensure cultural appropriateness for Bangsamoro context

OUTPUT: Return the COMPLETE refined policy as valid JSON with the same structure as the original.
"""

        response = self.gemini.generate_text(
            prompt,
            use_cache=False,
            include_cultural_context=True
        )

        if response['success']:
            try:
                refined_policy = json.loads(response['text'])
                refined_policy['refined'] = True
                refined_policy['refinement_feedback'] = feedback

                logger.info("Policy refinement completed")
                return refined_policy

            except json.JSONDecodeError:
                logger.error("Failed to parse refined policy JSON")
                return policy_data  # Return original if refinement fails

        else:
            logger.error(f"Policy refinement failed: {response.get('error')}")
            return policy_data

    def generate_quick_policy(
        self,
        issue: str,
        template_type: str = 'standard'
    ) -> Dict:
        """
        Generate a quick policy draft without extensive evidence gathering

        Args:
            issue: Policy issue description
            template_type: 'standard', 'urgent', 'pilot_program'

        Returns:
            Basic policy structure dict
        """
        logger.info(f"Generating quick policy draft: {issue}")

        templates = {
            'standard': "Comprehensive policy recommendation",
            'urgent': "Urgent policy intervention (streamlined)",
            'pilot_program': "Pilot program proposal"
        }

        template_description = templates.get(template_type, templates['standard'])

        prompt = f"""
{BANGSAMORO_CULTURAL_CONTEXT}

Generate a {template_description} for:
ISSUE: {issue}

Create a concise but complete policy recommendation with:
1. Title
2. Executive Summary (100 words)
3. Problem Statement (150 words)
4. Proposed Solution (200 words)
5. Key Objectives (3-4 objectives)
6. Expected Outcomes
7. Budget Estimate (rough)

Output as JSON format.
"""

        response = self.gemini.generate_text(
            prompt,
            use_cache=False,
            include_cultural_context=True
        )

        if response['success']:
            try:
                policy = json.loads(response['text'])
                policy['quick_draft'] = True
                policy['template_type'] = template_type
                return policy
            except json.JSONDecodeError:
                return {'error': 'Failed to parse quick policy'}
        else:
            return {'error': response.get('error')}


# Global singleton
_policy_generator = None


def get_policy_generator() -> PolicyGenerator:
    """Get or create global policy generator instance"""
    global _policy_generator
    if _policy_generator is None:
        _policy_generator = PolicyGenerator()
    return _policy_generator
