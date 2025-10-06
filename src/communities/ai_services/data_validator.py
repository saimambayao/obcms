"""
AI-powered data validation for community demographic data.

Uses Google Gemini to validate population consistency, ethnolinguistic groups,
and identify missing data in community profiles.
"""

import json
import logging
from typing import Dict, List, Optional

import google.generativeai as genai
from django.conf import settings

from ai_assistant.cultural_context import BangsomoroCulturalContext

logger = logging.getLogger(__name__)


class CommunityDataValidator:
    """AI-powered validation for community data."""

    def __init__(self):
        """Initialize Gemini AI service."""
        # Check if API key is configured
        self.api_key = getattr(settings, 'GOOGLE_API_KEY', None)
        self.model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash-exp')

        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,  # Low temperature for factual validation
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=1024,
                ),
            )
        else:
            self.model = None
            logger.warning("GOOGLE_API_KEY not configured. AI validation features will be disabled.")

        self.cultural_context = BangsomoroCulturalContext()

    def validate_population_consistency(self, community_data: dict) -> dict:
        """
        Check if population, households, and demographics are consistent.

        Args:
            community_data: Dict containing:
                - total_population: int
                - households: int
                - male_population: int (optional)
                - female_population: int (optional)
                - estimated_obc_population: int (optional)
                - total_barangay_population: int (optional)

        Returns:
            {
                'valid': bool,
                'issues': List[str],
                'suggestions': List[str],
                'confidence': float  # 0.0 to 1.0
            }
        """
        if not self.model:
            logger.warning("AI validation not available (API key not configured)")
            return {
                'valid': True,  # Don't block on missing AI
                'issues': [],
                'suggestions': ['AI validation not configured. Please set GOOGLE_API_KEY in settings.'],
                'confidence': 0.0
            }

        try:
            total_pop = community_data.get('total_population') or community_data.get('estimated_obc_population', 0)
            households = community_data.get('households', 0)
            male = community_data.get('male_population')
            female = community_data.get('female_population')
            barangay_pop = community_data.get('total_barangay_population')

            # Build validation prompt
            prompt = f"""
You are a data validation expert for Philippine Bangsamoro community demographics.

Validate this community demographic data for consistency:

Total OBC Population: {total_pop}
Households: {households}
Male Population: {male if male else 'Not provided'}
Female Population: {female if female else 'Not provided'}
Total Barangay Population: {barangay_pop if barangay_pop else 'Not provided'}

Philippine Context:
- Typical household size in Philippines: 4-6 persons
- In Bangsamoro communities: 5-8 persons (larger families)
- Gender ratio should be close to 1:1 (50-52% male, 48-50% female)
- OBC population should not exceed total barangay population

Check for:
1. Male + Female = Total Population (if both provided)
2. Reasonable household size (Total Population / Households)
3. OBC population <= Barangay population (if both provided)
4. Gender ratio within reasonable bounds
5. Any impossible values (negative, zero when should have value)

Respond in JSON format ONLY:
{{
    "valid": true/false,
    "issues": ["issue1", "issue2"],
    "suggestions": ["suggestion1", "suggestion2"],
    "confidence": 0.95
}}
"""

            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())

            # Ensure expected structure
            return {
                'valid': result.get('valid', False),
                'issues': result.get('issues', []),
                'suggestions': result.get('suggestions', []),
                'confidence': result.get('confidence', 0.5)
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse validation response: {str(e)}")
            return {
                'valid': False,
                'issues': ['AI validation service error'],
                'suggestions': ['Please verify data manually'],
                'confidence': 0.0
            }
        except Exception as e:
            logger.error(f"Population validation error: {str(e)}")
            return {
                'valid': False,
                'issues': [f'Validation error: {str(e)}'],
                'suggestions': ['Please check data and try again'],
                'confidence': 0.0
            }

    def validate_ethnolinguistic_group(self, group_name: str, province: str) -> dict:
        """
        Validate if ethnolinguistic group is common in this province.

        Args:
            group_name: Name of the ethnolinguistic group
            province: Province name

        Returns:
            {
                'valid': bool,
                'likelihood': str,  # 'Very Common', 'Common', 'Uncommon', 'Rare'
                'notes': str,
                'alternative_groups': List[str]
            }
        """
        try:
            cultural_info = self.cultural_context.get_base_context()

            prompt = f"""
You are an expert on Bangsamoro ethnolinguistic groups in the Philippines.

Validate this ethnolinguistic group for the given province:

Ethnolinguistic Group: {group_name}
Province: {province}

Cultural Context:
{cultural_info}

Major Bangsamoro ethnolinguistic groups:
- Maguindanaon (mainly in Maguindanao, Sultan Kudarat, North Cotabato)
- Meranaw/Maranao (mainly in Lanao del Sur, Lanao del Norte)
- Tausug (mainly in Sulu, Zamboanga)
- Sama/Samal (coastal areas, Tawi-Tawi)
- Yakan (Basilan)
- Iranun (Maguindanao, Lanao)
- Badjao (coastal areas, mobile communities)
- Kalagan/Kagan (Davao region)
- Sangil (Davao, Sarangani)

Assess:
1. Is this group commonly found in this province?
2. What is the likelihood? (Very Common, Common, Uncommon, Rare, Unknown)
3. Are there any historical migrations to this area?
4. What other groups might be more common here?

Respond in JSON format ONLY:
{{
    "valid": true/false,
    "likelihood": "Common",
    "notes": "Brief historical/geographic context",
    "alternative_groups": ["Group1", "Group2"]
}}
"""

            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())

            return {
                'valid': result.get('valid', True),
                'likelihood': result.get('likelihood', 'Unknown'),
                'notes': result.get('notes', ''),
                'alternative_groups': result.get('alternative_groups', [])
            }

        except Exception as e:
            logger.error(f"Ethnolinguistic validation error: {str(e)}")
            return {
                'valid': True,  # Don't block submission on validation error
                'likelihood': 'Unknown',
                'notes': f'Validation error: {str(e)}',
                'alternative_groups': []
            }

    def suggest_missing_data(self, community: 'OBCCommunity') -> List[str]:
        """
        Suggest what data might be missing based on community profile.

        Args:
            community: OBCCommunity model instance

        Returns:
            List of suggested missing data fields with priorities
        """
        try:
            # Analyze community data completeness
            profile_data = {
                'name': community.name or community.community_names,
                'population': community.estimated_obc_population,
                'households': community.households,
                'ethnolinguistic_group': community.primary_ethnolinguistic_group,
                'province': community.province.name if hasattr(community, 'province') else None,
                'has_coordinates': bool(community.latitude and community.longitude),
                'has_livelihoods': bool(community.primary_livelihoods),
                'has_infrastructure_access': any([
                    community.access_clean_water,
                    community.access_electricity,
                    community.access_healthcare,
                    community.access_formal_education
                ]),
                'has_age_demographics': any([
                    community.children_0_9,
                    community.youth_15_30,
                    community.adults_31_59,
                    community.seniors_60_plus
                ]),
                'has_vulnerable_sectors': any([
                    community.pwd_count,
                    community.solo_parents_count,
                    community.farmers_count
                ]),
            }

            prompt = f"""
You are a data completeness analyst for Bangsamoro community profiles.

Analyze this community profile and suggest critical missing data:

Community: {profile_data['name']}
Province: {profile_data['province']}
Population: {profile_data['population']}
Households: {profile_data['households']}
Ethnolinguistic Group: {profile_data['ethnolinguistic_group']}

Data Completeness:
- Geographic coordinates: {'Yes' if profile_data['has_coordinates'] else 'MISSING'}
- Livelihood information: {'Yes' if profile_data['has_livelihoods'] else 'MISSING'}
- Infrastructure access data: {'Yes' if profile_data['has_infrastructure_access'] else 'MISSING'}
- Age demographics: {'Yes' if profile_data['has_age_demographics'] else 'MISSING'}
- Vulnerable sectors data: {'Yes' if profile_data['has_vulnerable_sectors'] else 'MISSING'}

Prioritize missing data that:
1. Is essential for needs assessment (MANA)
2. Helps determine service delivery priorities
3. Enables program planning and coordination
4. Supports policy recommendations

Respond in JSON format with prioritized suggestions:
{{
    "critical_missing": ["field1: reason", "field2: reason"],
    "important_missing": ["field3: reason"],
    "optional_missing": ["field4: reason"]
}}
"""

            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())

            # Flatten all suggestions with priority labels
            suggestions = []
            for item in result.get('critical_missing', []):
                suggestions.append(f"[CRITICAL] {item}")
            for item in result.get('important_missing', []):
                suggestions.append(f"[IMPORTANT] {item}")
            for item in result.get('optional_missing', []):
                suggestions.append(f"[OPTIONAL] {item}")

            return suggestions

        except Exception as e:
            logger.error(f"Missing data suggestion error: {str(e)}")
            return [
                "[CRITICAL] Unable to generate suggestions due to AI service error",
                "[IMPORTANT] Please review data completeness manually"
            ]

    def validate_livelihood_consistency(
        self,
        primary_livelihoods: str,
        ethnolinguistic_group: str,
        province: str
    ) -> dict:
        """
        Validate if reported livelihoods are consistent with cultural background and location.

        Args:
            primary_livelihoods: Comma-separated livelihood activities
            ethnolinguistic_group: Primary ethnolinguistic group
            province: Province name

        Returns:
            {
                'consistent': bool,
                'notes': str,
                'typical_livelihoods': List[str]
            }
        """
        try:
            cultural_info = self.cultural_context.get_detailed_context()

            prompt = f"""
You are an expert on Bangsamoro communities' traditional and modern livelihoods.

Validate livelihood consistency:

Primary Livelihoods: {primary_livelihoods}
Ethnolinguistic Group: {ethnolinguistic_group}
Province: {province}

Cultural Context:
{cultural_info}

Common livelihoods by group:
- Maguindanaon: Rice farming, corn, vegetables, trade
- Meranaw: Lake fishing, farming, metalwork, trade
- Tausug: Fishing, seaweed farming, trade, pearl diving
- Sama/Badjao: Fishing, boat-making, seaweed farming
- Yakan: Farming, weaving, basket-making
- Iranun: Farming, fishing, boat-building
- Kalagan: Farming, fishing, copra production

Assess:
1. Are these livelihoods typical for this group?
2. Do they match the geographic location?
3. What are the most common livelihoods for this combination?

Respond in JSON format:
{{
    "consistent": true/false,
    "notes": "Brief assessment",
    "typical_livelihoods": ["livelihood1", "livelihood2"]
}}
"""

            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())

            return {
                'consistent': result.get('consistent', True),
                'notes': result.get('notes', ''),
                'typical_livelihoods': result.get('typical_livelihoods', [])
            }

        except Exception as e:
            logger.error(f"Livelihood validation error: {str(e)}")
            return {
                'consistent': True,
                'notes': f'Validation error: {str(e)}',
                'typical_livelihoods': []
            }
