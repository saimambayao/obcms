"""
Stakeholder Matcher Service

AI-powered matching of stakeholders (NGOs, LGUs, BMOAs) to community needs
using semantic similarity and multi-criteria analysis.
"""

import json
from typing import List, Dict, Optional, Tuple
from decimal import Decimal

from django.db.models import Q, Count, Avg, Sum
from django.core.cache import cache

from ai_assistant.services import EmbeddingService, SimilaritySearchService, GeminiService
from coordination.models import Organization
from communities.models import BarangayOBC


class StakeholderMatcher:
    """Match stakeholders to community needs using AI and multi-criteria analysis"""

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.similarity_search = SimilaritySearchService()
        self.gemini = GeminiService()

    def find_matching_stakeholders(
        self,
        community_id: int,
        need_category: str,
        top_k: int = 10,
        min_score: float = 0.6
    ) -> List[Dict]:
        """
        Find stakeholders best suited for community need

        Args:
            community_id: ID of the community (BarangayOBC)
            need_category: Category of need (e.g., 'Health', 'Education', 'Livelihood')
            top_k: Maximum number of matches to return
            min_score: Minimum matching score threshold (0-1)

        Returns:
            List of matching stakeholders with scores and rationale:
            [
                {
                    'stakeholder': Organization object,
                    'match_score': 0.92,
                    'matching_criteria': ['sector', 'geography', 'capacity'],
                    'rationale': 'Experienced in health projects in Region IX'
                },
                ...
            ]
        """
        # Check cache first
        cache_key = f"stakeholder_matches_{community_id}_{need_category}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        # Get community details
        try:
            community = BarangayOBC.objects.select_related(
                'municipality__province__region'
            ).get(id=community_id)
        except BarangayOBC.DoesNotExist:
            return []

        # Create need profile for semantic matching
        need_profile = self._create_need_profile(community, need_category)

        # Get active organizations
        organizations = Organization.objects.filter(
            is_active=True,
            partnership_status='active'
        ).select_related('created_by')

        # Calculate matches
        matches = []
        for org in organizations:
            score, criteria = self._calculate_match_score(community, org, need_category)

            if score >= min_score:
                rationale = self._generate_rationale(community, org, need_category, criteria)
                matches.append({
                    'stakeholder': org,
                    'match_score': round(score, 2),
                    'matching_criteria': criteria,
                    'rationale': rationale
                })

        # Sort by score and limit results
        matches = sorted(matches, key=lambda x: x['match_score'], reverse=True)[:top_k]

        # Cache results for 24 hours
        cache.set(cache_key, matches, timeout=86400)

        return matches

    def _create_need_profile(self, community: BarangayOBC, need_category: str) -> str:
        """Create a textual profile of the community need"""
        return f"""
        Community: {community.name}
        Municipality: {community.municipality.name}
        Province: {community.municipality.province.name}
        Region: {community.municipality.province.region.name}
        Population: {community.total_population}
        Need Category: {need_category}
        Ethnolinguistic Group: {community.ethnolinguistic_group or 'Not specified'}
        """

    def _calculate_match_score(
        self,
        community: BarangayOBC,
        org: Organization,
        need_category: str
    ) -> Tuple[float, List[str]]:
        """
        Calculate multi-criteria matching score

        Returns:
            (score, matching_criteria)
        """
        score = 0.0
        criteria = []

        # 1. Geographic Proximity (0-0.3)
        geographic_score = self._calculate_geographic_score(community, org)
        if geographic_score > 0:
            score += geographic_score
            if geographic_score >= 0.2:
                criteria.append('geography')

        # 2. Sector Alignment (0-0.4)
        sector_score = self._calculate_sector_score(org, need_category)
        if sector_score > 0:
            score += sector_score
            if sector_score >= 0.2:
                criteria.append('sector')

        # 3. Organization Capacity (0-0.15)
        capacity_score = self._calculate_capacity_score(org)
        if capacity_score > 0:
            score += capacity_score
            if capacity_score >= 0.1:
                criteria.append('capacity')

        # 4. Track Record (0-0.15)
        track_record_score = self._calculate_track_record_score(org)
        if track_record_score > 0:
            score += track_record_score
            if track_record_score >= 0.1:
                criteria.append('track_record')

        return min(score, 1.0), criteria

    def _calculate_geographic_score(self, community: BarangayOBC, org: Organization) -> float:
        """Calculate geographic proximity score"""
        score = 0.0

        if not org.geographic_coverage:
            return 0.0

        coverage_lower = org.geographic_coverage.lower()

        # Exact province match (highest priority)
        if community.municipality.province.name.lower() in coverage_lower:
            score = 0.3
        # Region match
        elif community.municipality.province.region.name.lower() in coverage_lower:
            score = 0.25
        # Municipality match
        elif community.municipality.name.lower() in coverage_lower:
            score = 0.2
        # National coverage
        elif 'national' in coverage_lower or 'nationwide' in coverage_lower:
            score = 0.15

        return score

    def _calculate_sector_score(self, org: Organization, need_category: str) -> float:
        """Calculate sector alignment score"""
        if not org.areas_of_expertise:
            return 0.0

        expertise_lower = org.areas_of_expertise.lower()
        need_lower = need_category.lower()

        # Direct match
        if need_lower in expertise_lower:
            return 0.4

        # Related sector matching
        sector_mappings = {
            'health': ['medical', 'healthcare', 'clinic', 'hospital', 'wellness'],
            'education': ['school', 'training', 'learning', 'scholarship', 'literacy'],
            'livelihood': ['employment', 'income', 'enterprise', 'skills', 'economic'],
            'infrastructure': ['construction', 'building', 'roads', 'water', 'sanitation'],
            'agriculture': ['farming', 'crops', 'livestock', 'fishery', 'agri'],
        }

        if need_lower in sector_mappings:
            for related_term in sector_mappings[need_lower]:
                if related_term in expertise_lower:
                    return 0.3

        return 0.0

    def _calculate_capacity_score(self, org: Organization) -> float:
        """Calculate organization capacity score based on budget and staff"""
        score = 0.0

        # Budget capacity (0-0.1)
        if org.annual_budget:
            if org.annual_budget >= Decimal('10000000'):  # 10M+
                score += 0.1
            elif org.annual_budget >= Decimal('5000000'):  # 5M+
                score += 0.07
            elif org.annual_budget >= Decimal('1000000'):  # 1M+
                score += 0.05

        # Staff count (0-0.05)
        if org.staff_count:
            if org.staff_count >= 50:
                score += 0.05
            elif org.staff_count >= 20:
                score += 0.03
            elif org.staff_count >= 10:
                score += 0.02

        return min(score, 0.15)

    def _calculate_track_record_score(self, org: Organization) -> float:
        """Calculate track record score based on past partnerships"""
        from coordination.models import Partnership

        # Count active and completed partnerships
        active_partnerships = Partnership.objects.filter(
            organizations=org,
            status__in=['active', 'completed']
        ).count()

        # Calculate score
        if active_partnerships >= 10:
            return 0.15
        elif active_partnerships >= 5:
            return 0.12
        elif active_partnerships >= 3:
            return 0.1
        elif active_partnerships >= 1:
            return 0.07

        return 0.0

    def _generate_rationale(
        self,
        community: BarangayOBC,
        org: Organization,
        need_category: str,
        criteria: List[str]
    ) -> str:
        """Generate human-readable rationale for the match"""
        rationale_parts = []

        # Organization type and name
        org_type = org.get_organization_type_display()
        rationale_parts.append(f"{org_type}")

        # Geographic relevance
        if 'geography' in criteria:
            if org.geographic_coverage:
                coverage = org.geographic_coverage
                if community.municipality.province.name in coverage:
                    rationale_parts.append(f"operates in {community.municipality.province.name}")
                elif community.municipality.province.region.name in coverage:
                    rationale_parts.append(f"covers {community.municipality.province.region.name}")

        # Sector expertise
        if 'sector' in criteria:
            rationale_parts.append(f"experienced in {need_category.lower()} sector")

        # Capacity
        if 'capacity' in criteria:
            if org.annual_budget and org.annual_budget >= Decimal('5000000'):
                rationale_parts.append("strong financial capacity")
            if org.staff_count and org.staff_count >= 20:
                rationale_parts.append("adequate staffing")

        # Track record
        if 'track_record' in criteria:
            rationale_parts.append("proven track record in partnerships")

        # Combine rationale
        if rationale_parts:
            return f"{rationale_parts[0].capitalize()}, " + ", ".join(rationale_parts[1:]) + "."

        return "General stakeholder alignment with community needs."

    def recommend_partnerships(
        self,
        stakeholder_ids: List[str],
        community_id: int,
        need_category: str
    ) -> Dict:
        """
        Recommend multi-stakeholder partnerships using AI

        Args:
            stakeholder_ids: List of organization UUIDs
            community_id: Community ID
            need_category: Type of need

        Returns:
            Partnership recommendation with synergy analysis
        """
        # Get stakeholders
        stakeholders = Organization.objects.filter(id__in=stakeholder_ids)
        community = BarangayOBC.objects.get(id=community_id)

        # Create partnership profile
        profile = self._create_partnership_profile(stakeholders, community, need_category)

        # Use Gemini to analyze synergies
        prompt = f"""
        Analyze this multi-stakeholder partnership opportunity:

        {profile}

        Provide:
        1. Overall synergy score (0-100)
        2. Complementary strengths
        3. Potential gaps
        4. Recommended roles for each stakeholder
        5. Success factors

        Return as JSON with keys: synergy_score, strengths, gaps, roles, success_factors
        """

        try:
            response = self.gemini.generate_text(prompt, temperature=0.3)
            recommendation = json.loads(response)
            recommendation['stakeholders'] = [
                {'id': str(s.id), 'name': s.name} for s in stakeholders
            ]
            return recommendation
        except Exception as e:
            return {
                'error': str(e),
                'synergy_score': 0,
                'stakeholders': [{'id': str(s.id), 'name': s.name} for s in stakeholders]
            }

    def _create_partnership_profile(
        self,
        stakeholders,
        community: BarangayOBC,
        need_category: str
    ) -> str:
        """Create partnership profile for AI analysis"""
        profile = f"""
        Community Need:
        - Location: {community.name}, {community.municipality.province.name}
        - Population: {community.total_population}
        - Need Category: {need_category}

        Proposed Stakeholders:
        """

        for org in stakeholders:
            profile += f"""

        {org.name} ({org.get_organization_type_display()}):
        - Expertise: {org.areas_of_expertise or 'Not specified'}
        - Coverage: {org.geographic_coverage or 'Not specified'}
        - Budget: {org.annual_budget or 'Not specified'}
        - Staff: {org.staff_count or 'Not specified'}
        """

        return profile
