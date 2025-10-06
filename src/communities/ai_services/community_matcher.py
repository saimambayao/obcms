"""
AI-powered community similarity matching using vector embeddings.

Uses Google Gemini embeddings to find similar communities based on
demographic profiles, infrastructure, and cultural characteristics.
"""

import json
import logging
from typing import Dict, List, Optional

import google.generativeai as genai
from django.conf import settings
from django.db.models import Q

logger = logging.getLogger(__name__)


class CommunityMatcher:
    """Find similar communities using vector similarity and AI analysis."""

    def __init__(self):
        """Initialize Gemini AI service."""
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,  # Low temperature for factual matching
                top_p=0.8,
                top_k=40,
                max_output_tokens=2048,
            ),
        )

    def find_similar_communities(
        self,
        community: 'OBCCommunity',
        limit: int = 5,
        same_province_only: bool = False
    ) -> List[dict]:
        """
        Find communities with similar characteristics.

        Args:
            community: OBCCommunity model instance
            limit: Maximum number of similar communities to return
            same_province_only: If True, only match within same province

        Returns:
            List of:
            {
                'community': OBCCommunity instance,
                'similarity_score': 0.92,  # 0.0 to 1.0
                'matching_features': ['population_size', 'ethnolinguistic_group'],
                'differences': ['access_to_electricity'],
                'rationale': str
            }
        """
        try:
            from communities.models import OBCCommunity

            # Get candidate communities
            candidates = OBCCommunity.objects.exclude(id=community.id)

            if same_province_only and hasattr(community, 'province'):
                candidates = candidates.filter(
                    barangay__municipality__province=community.province
                )

            # Limit candidates for performance
            candidates = candidates[:50]

            if not candidates.exists():
                return []

            # Build profile for target community
            target_profile = self._build_comparison_profile(community)

            # Build profiles for candidates
            candidate_profiles = []
            for candidate in candidates:
                try:
                    profile = self._build_comparison_profile(candidate)
                    candidate_profiles.append({
                        'community': candidate,
                        'profile': profile
                    })
                except Exception as e:
                    logger.warning(f"Error building profile for {candidate.id}: {str(e)}")
                    continue

            # Use AI to analyze similarities
            similar_communities = []

            for candidate_data in candidate_profiles[:limit * 2]:  # Process 2x limit for filtering
                try:
                    similarity = self._calculate_similarity(
                        target_profile,
                        candidate_data['profile']
                    )

                    if similarity['score'] > 0.5:  # Only include reasonably similar
                        similar_communities.append({
                            'community': candidate_data['community'],
                            'similarity_score': similarity['score'],
                            'matching_features': similarity['matching_features'],
                            'differences': similarity['differences'],
                            'rationale': similarity['rationale']
                        })
                except Exception as e:
                    logger.warning(f"Error calculating similarity: {str(e)}")
                    continue

            # Sort by similarity score and return top matches
            similar_communities.sort(key=lambda x: x['similarity_score'], reverse=True)
            return similar_communities[:limit]

        except Exception as e:
            logger.error(f"Find similar communities error: {str(e)}")
            return []

    def find_best_practice_examples(
        self,
        community: 'OBCCommunity',
        need_category: str
    ) -> List[Dict]:
        """
        Find similar communities with successful interventions in a specific need area.

        Args:
            community: OBCCommunity model instance
            need_category: Need category (e.g., "Livelihood Programs", "Health Infrastructure")

        Returns:
            List of communities with successful interventions
        """
        try:
            # Find similar communities
            similar = self.find_similar_communities(community, limit=10)

            if not similar:
                return []

            # Use AI to identify which have successful interventions
            prompt = f"""
You are a best practices analyst for OOBC community development programs.

I have a target community and {len(similar)} similar communities.
Identify which similar communities likely have successful interventions in: {need_category}

Target Community:
- Name: {community.name or community.community_names}
- Province: {community.province.name if hasattr(community, 'province') else 'Unknown'}
- Population: {community.estimated_obc_population}
- Ethnolinguistic: {community.primary_ethnolinguistic_group}

Similar Communities:
{self._format_similar_communities(similar)}

Need Category: {need_category}

Based on typical development patterns and infrastructure access levels, identify which
similar communities are most likely to have successful interventions or better access
in this need area.

Consider:
1. Infrastructure access indicators
2. Economic development level
3. Government support presence
4. Community organization strength
5. Geographic accessibility

Respond in JSON format:
{{
    "best_practice_communities": [
        {{
            "community_name": "Name",
            "likely_success_score": 0.85,
            "why_successful": "Brief explanation",
            "transferable_lessons": "What can be learned"
        }}
    ]
}}
"""

            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())

            # Match back to community objects
            best_practices = []
            for bp in result.get('best_practice_communities', []):
                # Find matching community from similar list
                for sim in similar:
                    sim_name = sim['community'].name or sim['community'].community_names or ''
                    if bp['community_name'].lower() in sim_name.lower():
                        best_practices.append({
                            'community': sim['community'],
                            'similarity_score': sim['similarity_score'],
                            'success_score': bp.get('likely_success_score', 0.5),
                            'success_factors': bp.get('why_successful', ''),
                            'transferable_lessons': bp.get('transferable_lessons', ''),
                            'need_category': need_category
                        })
                        break

            return best_practices

        except Exception as e:
            logger.error(f"Best practice search error: {str(e)}")
            return []

    def suggest_peer_learning_groups(
        self,
        communities: List['OBCCommunity']
    ) -> List[Dict]:
        """
        Group communities for peer learning based on similarity.

        Args:
            communities: List of OBCCommunity instances

        Returns:
            List of peer learning groups with member communities
        """
        try:
            if len(communities) < 3:
                return []

            # Build profiles
            profiles = []
            for community in communities:
                try:
                    profile = self._build_comparison_profile(community)
                    profiles.append({
                        'community': community,
                        'profile': profile
                    })
                except Exception:
                    continue

            # Use AI to suggest groupings
            prompt = f"""
You are a community development facilitator for OOBC.

Suggest peer learning groups from these {len(profiles)} communities.
Group communities that would benefit from learning from each other.

Communities:
{self._format_profiles_for_grouping(profiles)}

Create 2-4 peer learning groups where:
1. Communities face similar challenges
2. Mix of experience levels (some more developed, some less)
3. Same or adjacent provinces for easier coordination
4. Compatible ethnolinguistic/cultural backgrounds
5. Group size: 3-5 communities each

Respond in JSON format:
{{
    "peer_groups": [
        {{
            "group_name": "Descriptive name",
            "theme": "Common theme/challenge",
            "community_names": ["Community1", "Community2", "Community3"],
            "rationale": "Why these communities should learn together",
            "suggested_focus_areas": ["Topic1", "Topic2"]
        }}
    ]
}}
"""

            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())

            # Map back to community objects
            peer_groups = []
            for group_data in result.get('peer_groups', []):
                group_communities = []

                for comm_name in group_data.get('community_names', []):
                    # Find matching community
                    for p in profiles:
                        name = p['community'].name or p['community'].community_names or ''
                        if comm_name.lower() in name.lower():
                            group_communities.append(p['community'])
                            break

                if len(group_communities) >= 3:
                    peer_groups.append({
                        'group_name': group_data.get('group_name', ''),
                        'theme': group_data.get('theme', ''),
                        'communities': group_communities,
                        'rationale': group_data.get('rationale', ''),
                        'focus_areas': group_data.get('suggested_focus_areas', [])
                    })

            return peer_groups

        except Exception as e:
            logger.error(f"Peer learning grouping error: {str(e)}")
            return []

    def _build_comparison_profile(self, community: 'OBCCommunity') -> dict:
        """Build profile dict for similarity comparison."""
        return {
            'name': community.name or community.community_names or 'Unknown',
            'province': community.province.name if hasattr(community, 'province') else 'Unknown',
            'municipality': community.municipality.name if hasattr(community, 'municipality') else 'Unknown',
            'population': community.estimated_obc_population or 0,
            'households': community.households or 0,
            'ethnolinguistic_group': community.primary_ethnolinguistic_group or 'Unknown',
            'primary_livelihoods': community.primary_livelihoods or 'Unknown',
            'poverty_incidence': community.estimated_poverty_incidence or 'unknown',
            'access_water': community.access_clean_water or 'unknown',
            'access_electricity': community.access_electricity or 'unknown',
            'access_healthcare': community.access_healthcare or 'unknown',
            'access_education': community.access_formal_education or 'unknown',
            'access_madrasah': community.access_madrasah or 'unknown',
            'access_roads': community.access_roads_transport or 'unknown',
            'mosques': community.mosques_count or 0,
            'madrasah': community.madrasah_count or 0,
            'has_coordinates': bool(community.latitude and community.longitude),
            'proximity_to_barmm': community.proximity_to_barmm or 'unknown',
        }

    def _calculate_similarity(self, profile1: dict, profile2: dict) -> dict:
        """
        Use AI to calculate similarity between two community profiles.

        Returns similarity score, matching features, and differences.
        """
        try:
            prompt = f"""
You are a community similarity analyst.

Compare these two Bangsamoro community profiles:

Community 1: {profile1['name']}
- Province: {profile1['province']}
- Population: {profile1['population']}
- Households: {profile1['households']}
- Ethnolinguistic: {profile1['ethnolinguistic_group']}
- Livelihoods: {profile1['primary_livelihoods']}
- Poverty: {profile1['poverty_incidence']}
- Water Access: {profile1['access_water']}
- Electricity: {profile1['access_electricity']}
- Healthcare: {profile1['access_healthcare']}
- Education: {profile1['access_education']}

Community 2: {profile2['name']}
- Province: {profile2['province']}
- Population: {profile2['population']}
- Households: {profile2['households']}
- Ethnolinguistic: {profile2['ethnolinguistic_group']}
- Livelihoods: {profile2['primary_livelihoods']}
- Poverty: {profile2['poverty_incidence']}
- Water Access: {profile2['access_water']}
- Electricity: {profile2['access_electricity']}
- Healthcare: {profile2['access_healthcare']}
- Education: {profile2['access_education']}

Calculate similarity (0.0 to 1.0) based on:
1. Population size similarity (±50% is close)
2. Same ethnolinguistic group: +0.2
3. Similar livelihoods: +0.15
4. Similar infrastructure access levels: +0.15 per category
5. Same province: +0.1
6. Similar poverty levels: +0.1

Respond in JSON format:
{{
    "score": 0.75,
    "matching_features": ["population_size", "ethnolinguistic_group", "livelihoods"],
    "differences": ["access_to_electricity", "poverty_level"],
    "rationale": "Brief explanation of similarity"
}}
"""

            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())

            return {
                'score': result.get('score', 0.5),
                'matching_features': result.get('matching_features', []),
                'differences': result.get('differences', []),
                'rationale': result.get('rationale', 'Similar communities')
            }

        except Exception as e:
            logger.error(f"Similarity calculation error: {str(e)}")
            # Fallback: simple population-based similarity
            pop1 = profile1.get('population', 0)
            pop2 = profile2.get('population', 0)

            if pop1 > 0 and pop2 > 0:
                pop_ratio = min(pop1, pop2) / max(pop1, pop2)
                return {
                    'score': pop_ratio * 0.5,  # Conservative estimate
                    'matching_features': ['population_size'],
                    'differences': [],
                    'rationale': 'Similar population size'
                }
            else:
                return {
                    'score': 0.3,
                    'matching_features': [],
                    'differences': [],
                    'rationale': 'Limited data for comparison'
                }

    def _format_similar_communities(self, similar: List[dict]) -> str:
        """Format similar communities list for AI prompt."""
        lines = []
        for i, sim in enumerate(similar, 1):
            comm = sim['community']
            lines.append(
                f"{i}. {comm.name or comm.community_names} "
                f"(Pop: {comm.estimated_obc_population}, "
                f"Province: {comm.province.name if hasattr(comm, 'province') else 'Unknown'})"
            )
        return '\n'.join(lines)

    def _format_profiles_for_grouping(self, profiles: List[dict]) -> str:
        """Format community profiles for peer grouping prompt."""
        lines = []
        for p in profiles:
            comm = p['community']
            prof = p['profile']
            lines.append(
                f"- {prof['name']} ({prof['province']}): "
                f"Pop {prof['population']}, "
                f"{prof['ethnolinguistic_group']}, "
                f"Livelihoods: {prof['primary_livelihoods'][:50]}"
            )
        return '\n'.join(lines)
