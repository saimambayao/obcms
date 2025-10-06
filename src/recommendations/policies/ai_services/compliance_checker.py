"""
Regulatory Compliance Checker

Checks policy recommendations for compliance with BARMM laws and regulations.
Uses AI to analyze policy text against known legal framework.
"""

import json
import logging
from typing import Dict, List, Optional

from ai_assistant.services import GeminiService

logger = logging.getLogger(__name__)


class RegulatoryComplianceChecker:
    """Check policy compliance with BARMM regulations"""

    # Major BARMM and Philippine laws relevant to OBC policies
    BARMM_LEGAL_FRAMEWORK = {
        'R.A. 11054': {
            'full_name': 'Bangsamoro Organic Law (BOL)',
            'year': 2018,
            'description': 'Establishes the Bangsamoro Autonomous Region in Muslim Mindanao',
            'key_provisions': [
                'Article III: Basic Rights',
                'Article VII: Education and Madaris',
                'Article VIII: Social Justice and Human Rights',
                'Article IX: Shariah Justice System',
                'Article XIII: Intergovernmental Relations'
            ]
        },
        'R.A. 11310': {
            'full_name': 'Bangsamoro Autonomous Region Appropriations Act',
            'year': 2019,
            'description': 'Provides appropriations for BARMM operations',
            'key_provisions': [
                'Block grant allocation',
                'Special development fund',
                'Internal revenue allotment'
            ]
        },
        'R.A. 9054': {
            'full_name': 'ARMM Organic Act',
            'year': 2001,
            'description': 'Previous organic act (superseded by R.A. 11054)',
            'key_provisions': [
                'Historical reference for OBC provisions',
                'Transitional provisions'
            ]
        },
        'Presidential Decree No. 1083': {
            'full_name': 'Code of Muslim Personal Laws',
            'year': 1977,
            'description': 'Governs Muslim personal, family, and property relations',
            'key_provisions': [
                'Shariah-compliant governance',
                'Islamic family law',
                'Halal certification'
            ]
        },
        'R.A. 10354': {
            'full_name': 'Responsible Parenthood and Reproductive Health Act',
            'year': 2012,
            'description': 'Reproductive health with cultural sensitivity',
            'key_provisions': [
                'Culturally-sensitive health services',
                'Respect for religious beliefs'
            ]
        },
        'Indigenous Peoples Rights Act (IPRA)': {
            'full_name': 'Republic Act No. 8371',
            'year': 1997,
            'description': 'Protection of indigenous cultural communities',
            'key_provisions': [
                'Free, prior, and informed consent (FPIC)',
                'Cultural integrity',
                'Ancestral domain protection'
            ]
        },
        'Local Government Code': {
            'full_name': 'Republic Act No. 7160',
            'year': 1991,
            'description': 'Devolution and local autonomy',
            'key_provisions': [
                'LGU powers and functions',
                'Inter-governmental coordination',
                'Revenue allocation'
            ]
        },
        'Data Privacy Act': {
            'full_name': 'Republic Act No. 10173',
            'year': 2012,
            'description': 'Protection of personal information',
            'key_provisions': [
                'Consent requirements',
                'Data security',
                'Privacy rights'
            ]
        }
    }

    def __init__(self):
        """Initialize compliance checker"""
        self.gemini = GeminiService(temperature=0.2)  # Low temperature for legal analysis

    def check_compliance(
        self,
        policy_text: str,
        policy_title: str = 'Untitled Policy',
        category: str = 'general'
    ) -> Dict:
        """
        Check if policy complies with BARMM regulations

        Args:
            policy_text: Full policy text to analyze
            policy_title: Title of the policy
            category: Policy category (helps identify relevant laws)

        Returns:
            {
                'compliant': True/False,
                'compliance_score': 0.92,
                'relevant_laws': ['R.A. 11054', ...],
                'compliance_details': {...},
                'conflicts': [],
                'recommendations': [],
                'risk_level': 'low|medium|high'
            }
        """
        logger.info(f"Checking compliance for: {policy_title}")

        # Build legal framework context
        legal_context = self._build_legal_context()

        prompt = f"""
TASK: Analyze this policy recommendation for compliance with BARMM and Philippine laws.

POLICY TITLE: {policy_title}
POLICY CATEGORY: {category}

POLICY TEXT:
{policy_text}

RELEVANT LEGAL FRAMEWORK:
{legal_context}

COMPLIANCE ANALYSIS INSTRUCTIONS:

1. IDENTIFY RELEVANT LAWS
   - Which laws from the framework are most relevant to this policy?
   - Consider the policy's category, scope, and objectives

2. COMPLIANCE CHECK
   - Does the policy comply with each relevant law?
   - Are there any direct conflicts or violations?
   - Are there potential indirect compliance issues?

3. SPECIFIC CONSIDERATIONS FOR BARMM/OBC POLICIES:
   - Respect for Islamic values and Shariah principles
   - Cultural sensitivity and customary law
   - Intergovernmental coordination (BARMM-LGU-National)
   - Free, Prior, and Informed Consent (FPIC) where applicable
   - Data privacy and confidentiality
   - Non-discrimination and equity

4. RISK ASSESSMENT
   - Legal risk level: Low, Medium, or High
   - What could go wrong legally?

5. RECOMMENDATIONS
   - How can compliance be improved?
   - What safeguards should be added?
   - Any required legal procedures or clearances?

OUTPUT FORMAT: Valid JSON with structure:
{{
    "compliant": true/false,
    "compliance_score": <0-1>,
    "relevant_laws": ["R.A. 11054", "R.A. 11310", ...],
    "compliance_details": {{
        "R.A. 11054": {{
            "compliant": true/false,
            "notes": "Explanation of compliance or conflict"
        }},
        ...
    }},
    "conflicts": [
        {{
            "law": "R.A. XXXXX",
            "provision": "Article X, Section Y",
            "conflict": "Description of the conflict",
            "severity": "low|medium|high"
        }}
    ],
    "recommendations": [
        "Recommendation 1: Add FPIC requirement for community consultations",
        "Recommendation 2: Include Shariah compliance certification",
        ...
    ],
    "risk_level": "low|medium|high",
    "risk_explanation": "Brief explanation of legal risks"
}}
"""

        response = self.gemini.generate_text(
            prompt,
            use_cache=True,
            cache_ttl=86400,  # Cache for 24 hours
            include_cultural_context=False  # Legal analysis doesn't need cultural context
        )

        if response['success']:
            try:
                result = json.loads(response['text'])

                # Add metadata
                result['checked_at'] = str(timezone.now())
                result['ai_cost'] = response['cost']
                result['policy_title'] = policy_title

                logger.info(
                    f"Compliance check complete: {result.get('compliance_score', 0):.2%} compliant, "
                    f"{result.get('risk_level', 'unknown')} risk"
                )

                return result

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse compliance check JSON: {e}")
                return self._generate_fallback_compliance(policy_text)

        else:
            logger.error(f"Compliance check failed: {response.get('error')}")
            return self._generate_fallback_compliance(policy_text)

    def check_quick_compliance(
        self,
        policy_text: str,
        focus_area: str = 'general'
    ) -> Dict:
        """
        Quick compliance check focusing on specific area

        Args:
            policy_text: Policy text to check
            focus_area: 'cultural', 'procedural', 'budgetary', 'general'

        Returns:
            Simplified compliance result
        """
        focus_laws = {
            'cultural': ['R.A. 11054', 'Presidential Decree No. 1083', 'Indigenous Peoples Rights Act (IPRA)'],
            'procedural': ['Local Government Code', 'R.A. 11054'],
            'budgetary': ['R.A. 11310', 'R.A. 11054'],
            'general': list(self.BARMM_LEGAL_FRAMEWORK.keys())
        }

        relevant_laws = focus_laws.get(focus_area, focus_laws['general'])

        prompt = f"""
Quick compliance check for this policy text focusing on {focus_area} compliance.

POLICY TEXT:
{policy_text}

RELEVANT LAWS: {', '.join(relevant_laws)}

Provide:
1. Is it compliant? (Yes/No)
2. Compliance score (0-1)
3. Top 3 concerns (if any)
4. Risk level (low/medium/high)

JSON format with keys: compliant, compliance_score, concerns, risk_level
"""

        response = self.gemini.generate_text(
            prompt,
            use_cache=True,
            include_cultural_context=False
        )

        if response['success']:
            try:
                return json.loads(response['text'])
            except json.JSONDecodeError:
                return {'compliant': None, 'error': 'Parse error'}
        else:
            return {'compliant': None, 'error': response.get('error')}

    def get_compliance_guidelines(
        self,
        policy_category: str
    ) -> Dict:
        """
        Get compliance guidelines for a specific policy category

        Args:
            policy_category: Policy category (e.g., 'education', 'healthcare')

        Returns:
            {
                'category': '...',
                'key_laws': [...],
                'must_haves': [...],
                'common_pitfalls': [...],
                'best_practices': [...]
            }
        """
        prompt = f"""
Provide compliance guidelines for {policy_category} policies in the BARMM/OBC context.

Based on the BARMM legal framework, what are:
1. Key Laws: Most relevant laws for this category
2. Must-Haves: Essential compliance requirements
3. Common Pitfalls: What policy makers often miss
4. Best Practices: How to ensure strong compliance

JSON format.
"""

        response = self.gemini.generate_text(
            prompt,
            use_cache=True,
            cache_ttl=604800,  # Cache for 1 week (guidelines don't change often)
            include_cultural_context=True
        )

        if response['success']:
            try:
                guidelines = json.loads(response['text'])
                guidelines['category'] = policy_category
                return guidelines
            except json.JSONDecodeError:
                return self._generate_fallback_guidelines(policy_category)
        else:
            return self._generate_fallback_guidelines(policy_category)

    def _build_legal_context(self) -> str:
        """Build legal framework context for AI prompts"""
        context_lines = ["BARMM AND PHILIPPINE LEGAL FRAMEWORK:\n"]

        for law_code, law_info in self.BARMM_LEGAL_FRAMEWORK.items():
            context_lines.append(f"\n{law_code}: {law_info['full_name']} ({law_info['year']})")
            context_lines.append(f"   {law_info['description']}")
            context_lines.append(f"   Key Provisions:")
            for provision in law_info['key_provisions']:
                context_lines.append(f"   - {provision}")

        return "\n".join(context_lines)

    def _generate_fallback_compliance(self, policy_text: str) -> Dict:
        """Generate fallback compliance result if AI fails"""
        return {
            'compliant': None,
            'compliance_score': 0.0,
            'relevant_laws': list(self.BARMM_LEGAL_FRAMEWORK.keys()),
            'compliance_details': {},
            'conflicts': [],
            'recommendations': [
                'AI compliance check failed - manual legal review required',
                'Consult with legal counsel before implementation',
                'Review against R.A. 11054 (BOL) provisions'
            ],
            'risk_level': 'unknown',
            'risk_explanation': 'Unable to assess risk - AI service unavailable',
            'fallback': True
        }

    def _generate_fallback_guidelines(self, category: str) -> Dict:
        """Generate fallback guidelines if AI fails"""
        return {
            'category': category,
            'key_laws': ['R.A. 11054', 'Local Government Code'],
            'must_haves': [
                'Alignment with Bangsamoro Organic Law',
                'Cultural sensitivity',
                'Stakeholder consultation'
            ],
            'common_pitfalls': [
                'Insufficient community engagement',
                'Lack of cultural appropriateness',
                'Unclear implementation mechanisms'
            ],
            'best_practices': [
                'Conduct thorough legal review',
                'Engage with traditional leaders',
                'Ensure Shariah compliance where applicable'
            ],
            'fallback': True
        }


# Global singleton
_compliance_checker = None


def get_compliance_checker() -> RegulatoryComplianceChecker:
    """Get or create global compliance checker instance"""
    global _compliance_checker
    if _compliance_checker is None:
        _compliance_checker = RegulatoryComplianceChecker()
    return _compliance_checker


# Fix missing import
from django.utils import timezone
