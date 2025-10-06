"""
Cultural Validator
Validate content for cultural appropriateness and Bangsamoro sensitivity
"""

import json
import logging
from typing import Dict, List

from django.core.cache import cache

from ai_assistant.ai_engine import GeminiAIEngine
from ai_assistant.cultural_context import BangsomoroCulturalContext

logger = logging.getLogger(__name__)


class BangsomoroCulturalValidator:
    """Validate content for cultural appropriateness for Bangsamoro communities"""

    CULTURAL_GUIDELINES = """
BANGSAMORO CULTURAL SENSITIVITY GUIDELINES:

1. RELIGIOUS RESPECT
   - Respect Islamic values, practices, and traditions
   - Use proper Islamic terminology (e.g., "Masjid" or "Mosque", not "temple")
   - Acknowledge the importance of halal practices
   - Honor religious observances (Ramadan, Friday prayers, Islamic holidays)

2. CULTURAL TERMINOLOGY
   - Use "Bangsamoro" (preferred) or "Moro" (acceptable), never "tribal" or "minority"
   - Recognize ethnolinguistic diversity: Maguindanao, Maranao, Tausug, Sama, Yakan, etc.
   - Use "community leaders" or "traditional leaders", not "tribal chiefs"
   - Respect titles: Datu, Sultan, Ustadz, Imam

3. HISTORICAL CONTEXT
   - Acknowledge historical struggles and aspirations for self-determination
   - Recognize the peace process and BARMM establishment
   - Be sensitive to historical marginalization and displacement
   - Avoid stereotypes about conflict or violence

4. COMMUNITY STRUCTURE
   - Honor traditional leadership alongside formal governance
   - Recognize extended family (kaum) and clan structures
   - Respect gender roles while promoting inclusive development
   - Acknowledge role of madrasah education alongside formal schooling

5. GEOGRAPHIC SENSITIVITY
   - Recognize OBC communities are OUTSIDE BARMM territory
   - Acknowledge unique challenges of being outside the autonomous region
   - Respect desire for connection to broader Bangsamoro identity
   - Understand displacement and historical migration patterns

6. LANGUAGE & COMMUNICATION
   - Use inclusive, respectful language
   - Avoid deficit-based framing ("backward", "underdeveloped")
   - Emphasize community assets and resilience
   - Use person-first language

7. DEVELOPMENT APPROACH
   - Prioritize community participation and ownership
   - Respect traditional knowledge and practices
   - Ensure cultural compatibility of interventions
   - Consider Islamic principles in program design
"""

    PROHIBITED_TERMS = [
        "tribal",
        "primitive",
        "backward",
        "uncivilized",
        "minority group",
        "savage",
        "insurgent",  # without proper context
        "terrorist",  # avoid stereotyping
    ]

    PREFERRED_ALTERNATIVES = {
        "tribal": "community-based / traditional",
        "minority": "Bangsamoro community / OBC community",
        "backward": "underserved / marginalized",
        "uncivilized": "traditional / indigenous",
        "tribal chief": "community leader / traditional leader / Datu",
        "mosque temple": "mosque / masjid",
    }

    def __init__(self):
        """Initialize cultural validator with AI engine"""
        self.ai_engine = GeminiAIEngine()
        self.cultural_context = BangsomoroCulturalContext()

    def validate_report_content(self, report_text: str) -> Dict:
        """
        Check if report is culturally appropriate

        Args:
            report_text: Report content to validate

        Returns:
            dict: {
                'appropriate': True/False,
                'score': 0.92,
                'issues': [
                    {'type': 'terminology', 'severity': 'high', 'text': '...', 'line': 42}
                ],
                'suggestions': [
                    {'original': 'tribal', 'recommended': 'community-based', 'line': 42}
                ],
                'strengths': ['Respectful language', 'Acknowledges Islamic values']
            }
        """
        if not report_text or len(report_text.strip()) < 50:
            return {
                "appropriate": True,
                "score": 1.0,
                "issues": [],
                "suggestions": [],
                "message": "Content too short to validate",
            }

        # Check cache
        cache_key = f"cultural_validation_{hash(report_text)}"
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info("Using cached cultural validation")
            return cached_result

        # Quick check for prohibited terms
        quick_issues = self._quick_scan_for_issues(report_text)

        # Build validation prompt
        cultural_guidelines = self.cultural_context.get_base_context()

        prompt = f"""
{cultural_guidelines}

{self.CULTURAL_GUIDELINES}

TASK: Validate this report for cultural appropriateness and sensitivity to Bangsamoro communities

REPORT CONTENT:
{report_text[:4000]}  # Limit for token efficiency

VALIDATION CRITERIA:
1. Language Appropriateness
   - Check for prohibited or insensitive terms
   - Verify use of respectful, inclusive language
   - Identify any stereotypes or generalizations

2. Cultural Sensitivity
   - Respect for Islamic values and practices
   - Proper use of cultural terminology
   - Acknowledgment of community diversity

3. Historical Context
   - Appropriate framing of Bangsamoro history
   - Sensitivity to conflict and peace process
   - Recognition of OBC-specific context

4. Development Framing
   - Asset-based vs. deficit-based language
   - Community participation emphasis
   - Cultural compatibility of recommendations

PROVIDE DETAILED ANALYSIS:
1. Overall Appropriateness Score (0-1, where 1 = fully appropriate)
2. Specific Issues Found (if any)
3. Suggested Improvements
4. Strengths of the content

OUTPUT FORMAT (JSON):
{{
    "appropriate": true/false,
    "score": 0.92,
    "issues": [
        {{
            "type": "terminology|framing|stereotype|historical|religious",
            "severity": "critical|high|medium|low",
            "text": "problematic text excerpt",
            "explanation": "why this is problematic",
            "line_number": 42
        }}
    ],
    "suggestions": [
        {{
            "original": "problematic phrase",
            "recommended": "culturally appropriate alternative",
            "reason": "explanation of why alternative is better"
        }}
    ],
    "strengths": [
        "What the report does well culturally"
    ],
    "overall_assessment": "Brief summary of cultural appropriateness"
}}
"""

        try:
            # Generate validation using Gemini
            response = self.ai_engine.model.generate_content(prompt)
            result_text = response.text.strip()

            # Clean JSON from markdown
            if result_text.startswith("```json"):
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif result_text.startswith("```"):
                result_text = result_text.split("```")[1].split("```")[0].strip()

            # Parse validation result
            validation = json.loads(result_text)

            # Merge with quick scan issues
            if quick_issues:
                validation["issues"] = validation.get("issues", []) + quick_issues

            # Recalculate score if critical issues found
            critical_issues = [
                i for i in validation.get("issues", []) if i.get("severity") == "critical"
            ]

            if critical_issues:
                validation["score"] = min(validation.get("score", 1.0), 0.6)
                validation["appropriate"] = False

            # Ensure required fields
            validation.setdefault("appropriate", True)
            validation.setdefault("score", 0.85)
            validation.setdefault("issues", [])
            validation.setdefault("suggestions", [])
            validation.setdefault("strengths", [])

            # Cache for 30 days
            cache.set(cache_key, validation, timeout=86400 * 30)

            logger.info(
                f"Cultural validation completed. Score: {validation.get('score', 0):.2f}"
            )
            return validation

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse cultural validation JSON: {e}")
            return {
                "appropriate": True,
                "score": 0.7,
                "issues": quick_issues,
                "suggestions": [],
                "message": "AI validation failed, basic scan completed",
            }

        except Exception as e:
            logger.error(f"Error during cultural validation: {e}")
            return {
                "appropriate": False,
                "score": 0.0,
                "issues": [
                    {
                        "type": "system",
                        "severity": "high",
                        "text": str(e),
                        "explanation": "Validation system error",
                    }
                ],
                "suggestions": [],
            }

    def validate_needs_list(self, needs: List[str]) -> Dict:
        """
        Validate a list of identified needs for cultural appropriateness

        Args:
            needs: List of need statements

        Returns:
            dict: Validation results with flagged items
        """
        if not needs:
            return {"valid": True, "flagged_needs": [], "score": 1.0}

        flagged_needs = []

        for i, need in enumerate(needs):
            # Check for prohibited terms
            need_lower = need.lower()

            for prohibited in self.PROHIBITED_TERMS:
                if prohibited in need_lower:
                    flagged_needs.append(
                        {
                            "index": i,
                            "need": need,
                            "issue": f"Contains prohibited term: '{prohibited}'",
                            "suggestion": self.PREFERRED_ALTERNATIVES.get(
                                prohibited, "Use more respectful terminology"
                            ),
                        }
                    )

        score = 1.0 - (len(flagged_needs) / len(needs)) if needs else 1.0

        return {
            "valid": len(flagged_needs) == 0,
            "flagged_needs": flagged_needs,
            "score": score,
            "total_needs": len(needs),
            "flagged_count": len(flagged_needs),
        }

    def suggest_culturally_appropriate_phrasing(
        self, original_text: str, context: str = ""
    ) -> Dict:
        """
        Suggest culturally appropriate alternatives for problematic text

        Args:
            original_text: Text that may need improvement
            context: Additional context about where this text appears

        Returns:
            dict: Suggestions for improvement
        """
        cultural_guidelines = self.cultural_context.get_base_context()

        prompt = f"""
{cultural_guidelines}

{self.CULTURAL_GUIDELINES}

TASK: Suggest culturally appropriate phrasing for Bangsamoro communities

ORIGINAL TEXT:
"{original_text}"

CONTEXT: {context if context else "Community needs assessment report"}

Provide 2-3 alternative phrasings that are:
- Culturally sensitive and respectful
- Appropriate for Bangsamoro communities
- Professional and government-appropriate
- Specific and actionable

OUTPUT FORMAT (JSON):
{{
    "suggestions": [
        {{
            "phrasing": "alternative phrasing 1",
            "rationale": "why this is culturally appropriate"
        }},
        {{
            "phrasing": "alternative phrasing 2",
            "rationale": "why this is better"
        }}
    ]
}}
"""

        try:
            response = self.ai_engine.model.generate_content(prompt)
            result_text = response.text.strip()

            # Clean JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()

            suggestions = json.loads(result_text)
            return suggestions

        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return {"suggestions": []}

    def _quick_scan_for_issues(self, text: str) -> List[Dict]:
        """Quick scan for obvious problematic terms"""
        issues = []
        text_lower = text.lower()

        for prohibited in self.PROHIBITED_TERMS:
            if prohibited in text_lower:
                # Find line number
                lines = text.split("\n")
                for line_num, line in enumerate(lines, 1):
                    if prohibited in line.lower():
                        issues.append(
                            {
                                "type": "terminology",
                                "severity": "high",
                                "text": prohibited,
                                "explanation": f"Use of prohibited term '{prohibited}'",
                                "line_number": line_num,
                                "quick_scan": True,
                            }
                        )
                        break

        return issues

    def generate_cultural_compliance_report(self, validation_results: Dict) -> str:
        """
        Generate a human-readable cultural compliance report

        Args:
            validation_results: Results from validate_report_content()

        Returns:
            str: Formatted compliance report
        """
        score = validation_results.get("score", 0)
        appropriate = validation_results.get("appropriate", False)
        issues = validation_results.get("issues", [])
        suggestions = validation_results.get("suggestions", [])
        strengths = validation_results.get("strengths", [])

        report = "CULTURAL SENSITIVITY COMPLIANCE REPORT\n"
        report += "=" * 50 + "\n\n"

        # Overall score
        report += f"Overall Score: {score:.2%}\n"
        report += f"Status: {'APPROVED' if appropriate else 'NEEDS REVISION'}\n\n"

        # Strengths
        if strengths:
            report += "STRENGTHS:\n"
            for strength in strengths:
                report += f"  - {strength}\n"
            report += "\n"

        # Issues
        if issues:
            report += f"ISSUES IDENTIFIED ({len(issues)}):\n"
            for i, issue in enumerate(issues, 1):
                severity = issue.get("severity", "medium").upper()
                issue_type = issue.get("type", "general")
                explanation = issue.get("explanation", "")

                report += f"  {i}. [{severity}] {issue_type.title()}\n"
                report += f"     {explanation}\n"

                if "text" in issue:
                    report += f"     Text: \"{issue['text']}\"\n"

                report += "\n"

        # Suggestions
        if suggestions:
            report += f"RECOMMENDED CHANGES ({len(suggestions)}):\n"
            for i, suggestion in enumerate(suggestions, 1):
                original = suggestion.get("original", "")
                recommended = suggestion.get("recommended", "")
                reason = suggestion.get("reason", "")

                report += f"  {i}. Change: \"{original}\" → \"{recommended}\"\n"
                if reason:
                    report += f"     Reason: {reason}\n"
                report += "\n"

        # Conclusion
        report += "CONCLUSION:\n"
        if appropriate:
            report += "This content meets cultural sensitivity standards for Bangsamoro communities.\n"
        else:
            report += "This content requires revision to meet cultural sensitivity standards.\n"
            report += "Please address the issues identified above before publication.\n"

        return report
