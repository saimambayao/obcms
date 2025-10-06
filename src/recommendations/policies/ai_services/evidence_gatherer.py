"""
Cross-Module Evidence Gatherer

Gathers evidence from across OBCMS modules for evidence-based policy development.
Uses vector similarity search to find relevant information from:
- MANA assessments
- Community profiles
- Project outcomes
- Coordination stakeholder data
"""

import logging
from typing import Dict, List, Optional

from ai_assistant.services import GeminiService, get_similarity_search_service

logger = logging.getLogger(__name__)


class CrossModuleEvidenceGatherer:
    """Gather evidence from all OBCMS modules for policy development"""

    def __init__(self):
        """Initialize evidence gatherer with AI services"""
        self.similarity_search = get_similarity_search_service()
        self.gemini = GeminiService(temperature=0.4)  # Lower temperature for factual synthesis

    def gather_evidence(
        self,
        policy_topic: str,
        modules: Optional[List[str]] = None,
        limit_per_module: int = 10,
        similarity_threshold: float = 0.5
    ) -> Dict:
        """
        Search across modules for relevant evidence

        Args:
            policy_topic: e.g., "Healthcare access for coastal communities"
            modules: ['communities', 'assessments', 'policies', 'projects']
            limit_per_module: Maximum results per module (default: 10)
            similarity_threshold: Minimum similarity score (default: 0.5)

        Returns:
            {
                'mana_assessments': [...],
                'community_data': [...],
                'project_outcomes': [...],
                'policy_precedents': [...],
                'total_citations': 42
            }
        """
        if modules is None:
            modules = ['communities', 'assessments', 'policies', 'projects']

        logger.info(f"Gathering evidence for: {policy_topic}")

        evidence = {
            'mana_assessments': [],
            'community_data': [],
            'project_outcomes': [],
            'policy_precedents': [],
            'total_citations': 0
        }

        # Search MANA assessments
        if 'assessments' in modules or 'mana' in modules:
            evidence['mana_assessments'] = self._search_mana(
                policy_topic,
                limit=limit_per_module,
                threshold=similarity_threshold
            )

        # Search community profiles
        if 'communities' in modules:
            evidence['community_data'] = self._search_communities(
                policy_topic,
                limit=limit_per_module,
                threshold=similarity_threshold
            )

        # Search existing policies (precedents)
        if 'policies' in modules:
            evidence['policy_precedents'] = self._search_policies(
                policy_topic,
                limit=limit_per_module,
                threshold=similarity_threshold
            )

        # Search project outcomes
        if 'projects' in modules:
            evidence['project_outcomes'] = self._search_projects(
                policy_topic,
                limit=limit_per_module,
                threshold=similarity_threshold
            )

        # Count total citations
        evidence['total_citations'] = sum(
            len(v) for v in evidence.values() if isinstance(v, list)
        )

        logger.info(f"Gathered {evidence['total_citations']} total citations")

        return evidence

    def synthesize_evidence(self, evidence: Dict, policy_topic: str) -> Dict:
        """
        Use AI to synthesize evidence into coherent narrative

        Args:
            evidence: Evidence dict from gather_evidence()
            policy_topic: The policy topic being analyzed

        Returns:
            {
                'synthesis': 'Comprehensive evidence summary...',
                'key_findings': ['Finding 1', 'Finding 2', ...],
                'data_gaps': ['Gap 1', 'Gap 2', ...],
                'strength_of_evidence': 'weak|moderate|strong',
                'confidence_score': 0.85
            }
        """
        prompt = f"""
Synthesize this evidence for policy development on "{policy_topic}":

MANA ASSESSMENTS ({len(evidence.get('mana_assessments', []))} sources):
{self._format_sources(evidence.get('mana_assessments', []))}

COMMUNITY DATA ({len(evidence.get('community_data', []))} sources):
{self._format_sources(evidence.get('community_data', []))}

PROJECT OUTCOMES ({len(evidence.get('project_outcomes', []))} sources):
{self._format_sources(evidence.get('project_outcomes', []))}

POLICY PRECEDENTS ({len(evidence.get('policy_precedents', []))} sources):
{self._format_sources(evidence.get('policy_precedents', []))}

Create a comprehensive evidence synthesis with:
1. Evidence Summary (200-300 words): Synthesize key patterns and insights
2. Key Findings: List 3-5 most important findings with citations
3. Data Gaps: Identify what information is missing
4. Strength of Evidence: Assess as "weak", "moderate", or "strong"
5. Confidence Score: 0-1 based on evidence quality and quantity

Use academic/government tone appropriate for policy documents.

IMPORTANT: Return response in JSON format with keys:
- synthesis (string)
- key_findings (array of strings)
- data_gaps (array of strings)
- strength_of_evidence (string: weak/moderate/strong)
- confidence_score (float 0-1)
"""

        response = self.gemini.generate_text(
            prompt,
            use_cache=True,
            cache_ttl=3600  # Cache for 1 hour
        )

        if response['success']:
            try:
                # Parse JSON response
                import json
                result = json.loads(response['text'])
                logger.info("Evidence synthesis completed successfully")
                return result
            except json.JSONDecodeError:
                logger.error("Failed to parse AI response as JSON")
                return {
                    'synthesis': response['text'],
                    'key_findings': [],
                    'data_gaps': [],
                    'strength_of_evidence': 'unknown',
                    'confidence_score': 0.0
                }
        else:
            logger.error(f"Evidence synthesis failed: {response.get('error')}")
            return {
                'synthesis': 'Evidence synthesis failed.',
                'key_findings': [],
                'data_gaps': ['AI synthesis unavailable'],
                'strength_of_evidence': 'unknown',
                'confidence_score': 0.0
            }

    def _search_mana(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.5
    ) -> List[Dict]:
        """Search MANA assessments"""
        try:
            results = self.similarity_search.search_assessments(
                query,
                limit=limit,
                threshold=threshold
            )

            # Format results with source type
            formatted = []
            for result in results:
                formatted.append({
                    'id': result['id'],
                    'type': 'mana_assessment',
                    'similarity': result['similarity'],
                    'source': result.get('metadata', {}),
                })

            logger.info(f"Found {len(formatted)} MANA assessments")
            return formatted

        except Exception as e:
            logger.error(f"MANA search failed: {e}")
            return []

    def _search_communities(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.5
    ) -> List[Dict]:
        """Search community profiles"""
        try:
            results = self.similarity_search.search_communities(
                query,
                limit=limit,
                threshold=threshold
            )

            formatted = []
            for result in results:
                formatted.append({
                    'id': result['id'],
                    'type': 'community',
                    'similarity': result['similarity'],
                    'source': result.get('metadata', {}),
                })

            logger.info(f"Found {len(formatted)} communities")
            return formatted

        except Exception as e:
            logger.error(f"Community search failed: {e}")
            return []

    def _search_policies(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.5
    ) -> List[Dict]:
        """Search existing policy recommendations"""
        try:
            results = self.similarity_search.search_policies(
                query,
                limit=limit,
                threshold=threshold
            )

            formatted = []
            for result in results:
                formatted.append({
                    'id': result['id'],
                    'type': 'policy',
                    'similarity': result['similarity'],
                    'source': result.get('metadata', {}),
                })

            logger.info(f"Found {len(formatted)} policy precedents")
            return formatted

        except Exception as e:
            logger.error(f"Policy search failed: {e}")
            return []

    def _search_projects(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.5
    ) -> List[Dict]:
        """Search project outcomes and data"""
        try:
            # Import project models
            from project_central.models import Project

            # For now, do a simple database search
            # TODO: Integrate with vector search when project indexing is implemented
            projects = Project.objects.filter(
                models.Q(title__icontains=query) |
                models.Q(description__icontains=query) |
                models.Q(objectives__icontains=query)
            )[:limit]

            formatted = []
            for project in projects:
                formatted.append({
                    'id': project.id,
                    'type': 'project',
                    'similarity': 0.7,  # Placeholder
                    'source': {
                        'title': project.title,
                        'description': project.description,
                        'status': project.status,
                    },
                })

            logger.info(f"Found {len(formatted)} projects")
            return formatted

        except Exception as e:
            logger.error(f"Project search failed: {e}")
            return []

    def _format_sources(self, sources: List[Dict]) -> str:
        """Format sources for AI prompt"""
        if not sources:
            return "No sources found."

        formatted_lines = []
        for i, source in enumerate(sources[:10], 1):  # Limit to top 10
            source_data = source.get('source', {})
            similarity = source.get('similarity', 0)

            # Extract key information
            title = source_data.get('title') or source_data.get('name') or 'Untitled'
            description = source_data.get('description', '')[:200]  # First 200 chars

            formatted_lines.append(
                f"{i}. [{title}] (relevance: {similarity:.2f})\n   {description}"
            )

        return "\n".join(formatted_lines)

    def get_evidence_stats(self, evidence: Dict) -> Dict:
        """
        Get statistics about gathered evidence

        Returns:
            {
                'total_sources': 42,
                'by_module': {'mana': 10, 'communities': 15, ...},
                'avg_similarity': 0.75,
                'coverage_score': 0.85
            }
        """
        stats = {
            'total_sources': evidence.get('total_citations', 0),
            'by_module': {},
            'avg_similarity': 0.0,
            'coverage_score': 0.0
        }

        # Count by module
        for module, sources in evidence.items():
            if isinstance(sources, list):
                stats['by_module'][module] = len(sources)

        # Calculate average similarity
        all_similarities = []
        for sources in evidence.values():
            if isinstance(sources, list):
                for source in sources:
                    if 'similarity' in source:
                        all_similarities.append(source['similarity'])

        if all_similarities:
            stats['avg_similarity'] = sum(all_similarities) / len(all_similarities)

        # Coverage score (how many modules have data)
        modules_with_data = sum(1 for v in stats['by_module'].values() if v > 0)
        stats['coverage_score'] = modules_with_data / 4  # 4 possible modules

        return stats


# Global singleton instance
_evidence_gatherer = None


def get_evidence_gatherer() -> CrossModuleEvidenceGatherer:
    """Get or create the global evidence gatherer instance"""
    global _evidence_gatherer
    if _evidence_gatherer is None:
        _evidence_gatherer = CrossModuleEvidenceGatherer()
    return _evidence_gatherer
