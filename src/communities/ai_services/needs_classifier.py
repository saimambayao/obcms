"""
AI-powered needs classification for Bangsamoro communities.

Uses Google Gemini to predict community needs based on demographic profiles,
infrastructure access, and cultural context.
"""

import json
import logging
from typing import Dict, List, Optional

import google.generativeai as genai
from django.conf import settings

from ai_assistant.cultural_context import BangsomoroCulturalContext

logger = logging.getLogger(__name__)


class CommunityNeedsClassifier:
    """Classify and predict community needs using AI."""

    NEED_CATEGORIES = [
        'Health Infrastructure',
        'Education Facilities',
        'Livelihood Programs',
        'Water and Sanitation',
        'Road and Transport',
        'Electricity',
        'Governance Capacity',
        'Cultural Preservation',
        'Islamic Education (Madrasah)',
        'Peace and Security',
        'Land Tenure Security',
        'Financial Inclusion',
    ]

    def __init__(self):
        """Initialize Gemini AI service."""
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,  # Moderate temperature for needs prediction
                top_p=0.8,
                top_k=40,
                max_output_tokens=2048,
            ),
        )
        self.cultural_context = BangsomoroCulturalContext()

    def classify_needs(self, community: 'OBCCommunity') -> dict:
        """
        Predict primary needs based on community characteristics.

        Args:
            community: OBCCommunity model instance

        Returns:
            {
                'health_infrastructure': 0.85,  # Confidence scores (0-1)
                'education_facilities': 0.72,
                'livelihood_programs': 0.90,
                ...
                'top_priorities': [
                    {
                        'category': 'Livelihood Programs',
                        'score': 0.90,
                        'rationale': 'High unemployment and limited economic opportunities'
                    },
                    ...
                ],
                'recommendations': List[str]
            }
        """
        try:
            # Build comprehensive community profile
            profile = self._build_community_profile(community)

            prompt = f"""
You are a needs assessment expert for Bangsamoro communities outside BARMM.

Analyze this community profile and predict their primary development needs.

{self.cultural_context.get_base_context()}

Community Profile:
Name: {profile['name']}
Province: {profile['province']}
Population: {profile['population']}
Households: {profile['households']}
Ethnolinguistic Group: {profile['ethnolinguistic_group']}

Demographics:
- Children (0-9): {profile.get('children_0_9', 'Unknown')}
- Youth (15-30): {profile.get('youth_15_30', 'Unknown')}
- Seniors (60+): {profile.get('seniors_60_plus', 'Unknown')}
- PWDs: {profile.get('pwd_count', 'Unknown')}
- Solo Parents: {profile.get('solo_parents_count', 'Unknown')}

Infrastructure Access:
- Clean Water: {profile.get('access_clean_water', 'Unknown')}
- Electricity: {profile.get('access_electricity', 'Unknown')}
- Healthcare: {profile.get('access_healthcare', 'Unknown')}
- Formal Education: {profile.get('access_formal_education', 'Unknown')}
- Madrasah/Islamic Education: {profile.get('access_madrasah', 'Unknown')}
- Roads/Transport: {profile.get('access_roads_transport', 'Unknown')}

Economic Context:
- Primary Livelihoods: {profile.get('primary_livelihoods', 'Unknown')}
- Poverty Incidence: {profile.get('estimated_poverty_incidence', 'Unknown')}
- Unemployment Rate: {profile.get('unemployment_rate', 'Unknown')}

Cultural/Religious:
- Mosques: {profile.get('mosques_count', 0)}
- Madrasah: {profile.get('madrasah_count', 0)}
- Religious Leaders: {profile.get('religious_leaders_count', 0)}

Challenges Reported:
{profile.get('challenges_summary', 'None reported')}

Predict needs in these categories with confidence scores (0.0 to 1.0):
{', '.join(self.NEED_CATEGORIES)}

Consider:
1. Population size and vulnerable groups
2. Geographic location and accessibility
3. Cultural and religious infrastructure needs
4. Economic opportunities and livelihoods
5. Basic service access gaps
6. Typical needs for this ethnolinguistic group
7. OOBC priorities for communities outside BARMM

Respond in JSON format:
{{
    "health_infrastructure": 0.75,
    "education_facilities": 0.65,
    "livelihood_programs": 0.90,
    "water_and_sanitation": 0.80,
    "road_and_transport": 0.70,
    "electricity": 0.85,
    "governance_capacity": 0.55,
    "cultural_preservation": 0.60,
    "islamic_education_madrasah": 0.70,
    "peace_and_security": 0.50,
    "land_tenure_security": 0.65,
    "financial_inclusion": 0.75,
    "top_priorities": [
        {{
            "category": "Need Category",
            "score": 0.90,
            "rationale": "Brief explanation why this is a priority"
        }}
    ],
    "recommendations": [
        "Specific actionable recommendation 1",
        "Specific actionable recommendation 2"
    ]
}}
"""

            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())

            # Ensure all categories have scores
            for category in self.NEED_CATEGORIES:
                key = self._category_to_key(category)
                if key not in result:
                    result[key] = 0.5  # Default moderate priority

            return result

        except Exception as e:
            logger.error(f"Needs classification error: {str(e)}")
            # Return default moderate scores on error
            return {
                self._category_to_key(cat): 0.5
                for cat in self.NEED_CATEGORIES
            } | {
                'top_priorities': [],
                'recommendations': [f'AI classification error: {str(e)}'],
                'error': True
            }

    def predict_assessment_priority(self, community: 'OBCCommunity') -> dict:
        """
        Predict if this community should be prioritized for MANA (needs assessment).

        Args:
            community: OBCCommunity model instance

        Returns:
            {
                'priority_score': float,  # 0.0 to 1.0
                'priority_level': str,  # 'Critical', 'High', 'Medium', 'Low'
                'rationale': str,
                'urgency_factors': List[str],
                'recommended_assessment_type': str
            }
        """
        try:
            profile = self._build_community_profile(community)

            prompt = f"""
You are a MANA (Mapping and Needs Assessment) prioritization expert for OOBC.

Determine assessment priority for this community:

Community: {profile['name']}
Province: {profile['province']}
Population: {profile['population']}
Last Assessment: {profile.get('needs_assessment_date', 'Never assessed')}

Key Indicators:
- Poverty Incidence: {profile.get('estimated_poverty_incidence', 'Unknown')}
- Infrastructure Access: {self._summarize_access(profile)}
- Vulnerable Populations: {profile.get('pwd_count', 0)} PWDs, {profile.get('idps_count', 0)} IDPs
- Data Completeness: {self._assess_data_completeness(profile)}%

Challenges Reported:
{profile.get('challenges_summary', 'None')}

MANA Prioritization Criteria:
1. Never assessed OR last assessment >3 years ago
2. High poverty incidence (>40%)
3. Poor infrastructure access (multiple "poor" or "none" ratings)
4. Large vulnerable populations (IDPs, PWDs, solo parents)
5. Security concerns or conflict-affected areas
6. Low data completeness (need baseline data)
7. Expressed community aspirations/requests
8. Strategic importance for OOBC programs

Respond in JSON format:
{{
    "priority_score": 0.85,
    "priority_level": "High",
    "rationale": "Brief explanation of priority determination",
    "urgency_factors": [
        "Never previously assessed",
        "High poverty incidence",
        "Large IDP population"
    ],
    "recommended_assessment_type": "Comprehensive MANA" or "Rapid Assessment" or "Follow-up Assessment",
    "estimated_duration_days": 5,
    "recommended_team_size": 3
}}
"""

            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())

            return result

        except Exception as e:
            logger.error(f"Assessment priority prediction error: {str(e)}")
            return {
                'priority_score': 0.5,
                'priority_level': 'Medium',
                'rationale': f'Unable to determine priority: {str(e)}',
                'urgency_factors': [],
                'recommended_assessment_type': 'Standard Assessment'
            }

    def identify_intervention_opportunities(self, community: 'OBCCommunity') -> List[Dict]:
        """
        Identify specific intervention opportunities based on community profile.

        Args:
            community: OBCCommunity model instance

        Returns:
            List of intervention opportunities with details
        """
        try:
            profile = self._build_community_profile(community)
            needs = self.classify_needs(community)

            # Get top 3 priority needs
            sorted_needs = sorted(
                [(k, v) for k, v in needs.items() if k not in ['top_priorities', 'recommendations', 'error']],
                key=lambda x: x[1],
                reverse=True
            )[:3]

            prompt = f"""
You are a program development specialist for OOBC.

Based on top priority needs for this community, identify specific intervention opportunities:

Community: {profile['name']}
Province: {profile['province']}
Population: {profile['population']}
Ethnolinguistic Group: {profile['ethnolinguistic_group']}

Top Priority Needs:
{chr(10).join([f'- {self._key_to_category(k)}: {v:.0%} priority' for k, v in sorted_needs])}

Primary Livelihoods: {profile.get('primary_livelihoods', 'Unknown')}
Cultural Assets: {profile.get('mosques_count', 0)} mosques, {profile.get('madrasah_count', 0)} madrasah

For each top priority need, suggest 1-2 specific, culturally appropriate interventions that:
1. Address the identified need directly
2. Are feasible for OOBC to implement or coordinate
3. Respect Islamic values and Bangsamoro culture
4. Can be implemented with community participation
5. Have measurable outcomes

Respond in JSON format:
{{
    "interventions": [
        {{
            "need_category": "Category name",
            "intervention_title": "Short title",
            "description": "What will be done",
            "target_beneficiaries": "Who benefits",
            "estimated_cost": "Low/Medium/High",
            "implementation_timeline": "Short/Medium/Long-term",
            "potential_partners": ["Partner1", "Partner2"],
            "success_indicators": ["Indicator1", "Indicator2"],
            "cultural_considerations": "How this respects local culture"
        }}
    ]
}}
"""

            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())

            return result.get('interventions', [])

        except Exception as e:
            logger.error(f"Intervention identification error: {str(e)}")
            return []

    def _build_community_profile(self, community: 'OBCCommunity') -> dict:
        """Build comprehensive community profile dict for AI prompts."""
        return {
            'name': community.name or community.community_names or 'Unknown',
            'province': community.province.name if hasattr(community, 'province') else 'Unknown',
            'municipality': community.municipality.name if hasattr(community, 'municipality') else 'Unknown',
            'population': community.estimated_obc_population or 0,
            'households': community.households or 0,
            'ethnolinguistic_group': community.primary_ethnolinguistic_group or 'Unknown',
            'children_0_9': community.children_0_9,
            'youth_15_30': community.youth_15_30,
            'seniors_60_plus': community.seniors_60_plus,
            'pwd_count': community.pwd_count,
            'solo_parents_count': community.solo_parents_count,
            'idps_count': community.idps_count,
            'farmers_count': community.farmers_count,
            'fisherfolk_count': community.fisherfolk_count,
            'access_clean_water': community.access_clean_water or 'Unknown',
            'access_electricity': community.access_electricity or 'Unknown',
            'access_healthcare': community.access_healthcare or 'Unknown',
            'access_formal_education': community.access_formal_education or 'Unknown',
            'access_madrasah': community.access_madrasah or 'Unknown',
            'access_roads_transport': community.access_roads_transport or 'Unknown',
            'primary_livelihoods': community.primary_livelihoods or 'Unknown',
            'estimated_poverty_incidence': community.estimated_poverty_incidence or 'Unknown',
            'unemployment_rate': community.unemployment_rate or 'Unknown',
            'mosques_count': community.mosques_count or 0,
            'madrasah_count': community.madrasah_count or 0,
            'religious_leaders_count': community.religious_leaders_count or 0,
            'needs_assessment_date': community.needs_assessment_date,
            'challenges_summary': self._summarize_challenges(community),
        }

    def _summarize_challenges(self, community: 'OBCCommunity') -> str:
        """Summarize reported challenges."""
        challenges = []
        if community.governance_policy_challenges:
            challenges.append(f"Governance: {community.governance_policy_challenges[:100]}")
        if community.economic_disparities:
            challenges.append(f"Economic: {community.economic_disparities[:100]}")
        if community.access_public_services_challenges:
            challenges.append(f"Services: {community.access_public_services_challenges[:100]}")

        return '; '.join(challenges) if challenges else 'None reported'

    def _summarize_access(self, profile: dict) -> str:
        """Summarize infrastructure access levels."""
        access_fields = [
            'access_clean_water',
            'access_electricity',
            'access_healthcare',
            'access_formal_education'
        ]
        access_levels = [profile.get(field, 'Unknown') for field in access_fields]

        poor_count = sum(1 for level in access_levels if level in ['poor', 'none'])
        good_count = sum(1 for level in access_levels if level in ['good', 'excellent'])

        return f"{good_count} good, {poor_count} poor/none"

    def _assess_data_completeness(self, profile: dict) -> int:
        """Calculate data completeness percentage."""
        critical_fields = [
            'population', 'households', 'ethnolinguistic_group',
            'access_clean_water', 'access_electricity', 'access_healthcare',
            'primary_livelihoods'
        ]

        filled_count = sum(
            1 for field in critical_fields
            if profile.get(field) not in [None, 'Unknown', 'unknown', '', 0]
        )

        return int((filled_count / len(critical_fields)) * 100)

    def _category_to_key(self, category: str) -> str:
        """Convert category name to dictionary key."""
        return category.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')

    def _key_to_category(self, key: str) -> str:
        """Convert dictionary key back to category name."""
        for category in self.NEED_CATEGORIES:
            if self._category_to_key(category) == key:
                return category
        return key.replace('_', ' ').title()
