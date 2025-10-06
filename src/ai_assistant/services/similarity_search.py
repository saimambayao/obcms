"""
Similarity Search Service

High-level semantic search across OBCMS modules.

Provides unified interface for:
- Community similarity search
- MANA assessment search
- Policy recommendation search
- Cross-module unified search
"""

import logging
from typing import Dict, List, Optional

from django.contrib.contenttypes.models import ContentType

from .embedding_service import get_embedding_service
from .vector_store import VectorStore

logger = logging.getLogger(__name__)


class SimilaritySearchService:
    """
    High-level semantic search service for OBCMS.

    Features:
    - Module-specific search (communities, assessments, policies)
    - Unified cross-module search
    - Find similar items based on content
    - Configurable similarity thresholds
    """

    def __init__(self):
        """Initialize the similarity search service."""
        self.embedding_service = get_embedding_service()
        self._stores = {}  # Cache for loaded vector stores

    def _get_store(self, store_name: str) -> VectorStore:
        """
        Get or load a vector store.

        Args:
            store_name: Name of the store to load

        Returns:
            VectorStore instance
        """
        if store_name not in self._stores:
            try:
                self._stores[store_name] = VectorStore.load(store_name)
                logger.info(f"Loaded vector store '{store_name}'")
            except FileNotFoundError:
                logger.warning(
                    f"Vector store '{store_name}' not found. Creating empty store."
                )
                self._stores[store_name] = VectorStore(
                    store_name, dimension=self.embedding_service.get_dimension()
                )
        return self._stores[store_name]

    def search_communities(
        self, query: str, limit: int = 10, threshold: float = 0.5
    ) -> List[Dict]:
        """
        Search for similar communities.

        Args:
            query: Search query (e.g., "Muslim community in Zamboanga with fishing livelihood")
            limit: Maximum number of results
            threshold: Minimum similarity score (0-1)

        Returns:
            List of dicts with community info and similarity scores

        Example:
            >>> service = SimilaritySearchService()
            >>> results = service.search_communities(
            ...     "Tausug community in coastal area",
            ...     limit=5
            ... )
            >>> for result in results:
            ...     print(f"{result['name']}: {result['similarity']:.2f}")
        """
        store = self._get_store("communities")

        if store.vector_count == 0:
            logger.warning("Communities index is empty")
            return []

        # Generate query embedding
        query_vector = self.embedding_service.generate_embedding(query)

        # Search
        raw_results = store.search_by_threshold(
            query_vector, threshold=threshold, max_results=limit
        )

        # Format results
        results = []
        for pos, similarity, meta in raw_results:
            results.append(
                {
                    "id": meta.get("id"),
                    "type": meta.get("type"),
                    "similarity": similarity,
                    "metadata": meta.get("data", {}),
                }
            )

        logger.info(f"Found {len(results)} communities for query: {query[:50]}...")
        return results

    def search_assessments(
        self, query: str, limit: int = 10, threshold: float = 0.5
    ) -> List[Dict]:
        """
        Search for similar MANA assessments.

        Args:
            query: Search query (e.g., "education needs assessment")
            limit: Maximum number of results
            threshold: Minimum similarity score

        Returns:
            List of dicts with assessment info and similarity scores
        """
        store = self._get_store("assessments")

        if store.vector_count == 0:
            logger.warning("Assessments index is empty")
            return []

        query_vector = self.embedding_service.generate_embedding(query)

        raw_results = store.search_by_threshold(
            query_vector, threshold=threshold, max_results=limit
        )

        results = []
        for pos, similarity, meta in raw_results:
            results.append(
                {
                    "id": meta.get("id"),
                    "type": meta.get("type"),
                    "similarity": similarity,
                    "metadata": meta.get("data", {}),
                }
            )

        logger.info(f"Found {len(results)} assessments for query: {query[:50]}...")
        return results

    def search_policies(
        self, query: str, limit: int = 10, threshold: float = 0.5
    ) -> List[Dict]:
        """
        Search for similar policy recommendations.

        Args:
            query: Search query (e.g., "livelihood program for fisher folk")
            limit: Maximum number of results
            threshold: Minimum similarity score

        Returns:
            List of dicts with policy info and similarity scores
        """
        store = self._get_store("policies")

        if store.vector_count == 0:
            logger.warning("Policies index is empty")
            return []

        query_vector = self.embedding_service.generate_embedding(query)

        raw_results = store.search_by_threshold(
            query_vector, threshold=threshold, max_results=limit
        )

        results = []
        for pos, similarity, meta in raw_results:
            results.append(
                {
                    "id": meta.get("id"),
                    "type": meta.get("type"),
                    "similarity": similarity,
                    "metadata": meta.get("data", {}),
                }
            )

        logger.info(f"Found {len(results)} policies for query: {query[:50]}...")
        return results

    def search_all(
        self, query: str, limit: int = 10, threshold: float = 0.5
    ) -> Dict[str, List[Dict]]:
        """
        Unified search across all modules.

        Args:
            query: Search query
            limit: Maximum results per module
            threshold: Minimum similarity score

        Returns:
            Dict with results grouped by module:
            {
                'communities': [...],
                'assessments': [...],
                'policies': [...]
            }

        Example:
            >>> service = SimilaritySearchService()
            >>> results = service.search_all("education program")
            >>> print(f"Communities: {len(results['communities'])}")
            >>> print(f"Assessments: {len(results['assessments'])}")
            >>> print(f"Policies: {len(results['policies'])}")
        """
        return {
            "communities": self.search_communities(query, limit, threshold),
            "assessments": self.search_assessments(query, limit, threshold),
            "policies": self.search_policies(query, limit, threshold),
        }

    def find_similar_communities(
        self, community_id: int, limit: int = 5, threshold: float = 0.7
    ) -> List[Dict]:
        """
        Find communities similar to a given community.

        Args:
            community_id: ID of the reference community
            limit: Maximum number of similar communities
            threshold: Minimum similarity score (higher threshold for "similar")

        Returns:
            List of similar communities with scores

        Example:
            >>> service = SimilaritySearchService()
            >>> similar = service.find_similar_communities(community_id=123, limit=5)
            >>> for result in similar:
            ...     print(f"Community {result['id']}: {result['similarity']:.2f}")
        """
        from communities.models import OBCCommunity

        store = self._get_store("communities")

        # Find the reference community's embedding
        reference_embedding = None
        for meta in store.metadata:
            if meta.get("type") == "community" and meta.get("id") == community_id:
                # Get the embedding from the store
                # Note: We need to search by exact match first
                break

        if reference_embedding is None:
            logger.warning(f"Community {community_id} not found in index")
            return []

        # For now, get the community and generate its embedding
        try:
            community = OBCCommunity.objects.get(id=community_id)
            text = self._format_community_text(community)
            query_vector = self.embedding_service.generate_embedding(text)
        except OBCCommunity.DoesNotExist:
            logger.error(f"Community {community_id} does not exist")
            return []

        # Search for similar communities
        raw_results = store.search_by_threshold(
            query_vector,
            threshold=threshold,
            max_results=limit + 1,  # +1 to exclude self
        )

        # Filter out the reference community itself
        results = []
        for pos, similarity, meta in raw_results:
            if meta.get("id") != community_id:
                results.append(
                    {
                        "id": meta.get("id"),
                        "type": meta.get("type"),
                        "similarity": similarity,
                        "metadata": meta.get("data", {}),
                    }
                )

        return results[:limit]

    def find_similar_assessments(
        self, assessment_id: int, limit: int = 5, threshold: float = 0.7
    ) -> List[Dict]:
        """
        Find assessments similar to a given assessment.

        Args:
            assessment_id: ID of the reference assessment
            limit: Maximum number of similar assessments
            threshold: Minimum similarity score

        Returns:
            List of similar assessments with scores
        """
        # Implementation similar to find_similar_communities
        # Will be implemented when MANA models are integrated
        logger.warning("find_similar_assessments not yet implemented")
        return []

    def find_similar_policies(
        self, policy_id: int, limit: int = 5, threshold: float = 0.7
    ) -> List[Dict]:
        """
        Find policies similar to a given policy.

        Args:
            policy_id: ID of the reference policy
            limit: Maximum number of similar policies
            threshold: Minimum similarity score

        Returns:
            List of similar policies with scores
        """
        from recommendations.policy_tracking.models import PolicyRecommendation

        store = self._get_store("policies")

        try:
            policy = PolicyRecommendation.objects.get(id=policy_id)
            text = self._format_policy_text(policy)
            query_vector = self.embedding_service.generate_embedding(text)
        except PolicyRecommendation.DoesNotExist:
            logger.error(f"Policy {policy_id} does not exist")
            return []

        raw_results = store.search_by_threshold(
            query_vector, threshold=threshold, max_results=limit + 1
        )

        # Filter out the reference policy itself
        results = []
        for pos, similarity, meta in raw_results:
            if meta.get("id") != policy_id:
                results.append(
                    {
                        "id": meta.get("id"),
                        "type": meta.get("type"),
                        "similarity": similarity,
                        "metadata": meta.get("data", {}),
                    }
                )

        return results[:limit]

    def _format_community_text(self, community) -> str:
        """
        Format community data as text for embedding.

        Args:
            community: OBCCommunity instance

        Returns:
            Formatted text representation
        """
        parts = [
            f"Community Names: {community.community_names}",
            f"Barangay: {community.barangay.name}",
            f"Municipality: {community.barangay.municipality.name}",
            f"Province: {community.barangay.municipality.province.name}",
            f"Region: {community.barangay.municipality.province.region.name}",
        ]

        if community.estimated_obc_population:
            parts.append(f"Population: {community.estimated_obc_population}")

        if community.households:
            parts.append(f"Households: {community.households}")

        if (
            hasattr(community, "ethnolinguistic_groups")
            and community.ethnolinguistic_groups
        ):
            parts.append(f"Ethnolinguistic Groups: {community.ethnolinguistic_groups}")

        if hasattr(community, "primary_livelihoods") and community.primary_livelihoods:
            parts.append(f"Primary Livelihoods: {community.primary_livelihoods}")

        if hasattr(community, "notes") and community.notes:
            parts.append(f"Notes: {community.notes}")

        return "\n".join(parts)

    def _format_policy_text(self, policy) -> str:
        """
        Format policy data as text for embedding.

        Args:
            policy: PolicyRecommendation instance

        Returns:
            Formatted text representation
        """
        parts = [
            f"Title: {policy.title}",
            f"Status: {policy.get_status_display()}",
        ]

        if policy.description:
            parts.append(f"Description: {policy.description}")

        if policy.sector:
            parts.append(f"Sector: {policy.get_sector_display()}")

        if policy.priority_level:
            parts.append(f"Priority: {policy.get_priority_level_display()}")

        if hasattr(policy, "target_communities") and policy.target_communities:
            parts.append(f"Target Communities: {policy.target_communities}")

        if hasattr(policy, "expected_impact") and policy.expected_impact:
            parts.append(f"Expected Impact: {policy.expected_impact}")

        return "\n".join(parts)

    def get_index_stats(self) -> Dict:
        """
        Get statistics for all vector indices.

        Returns:
            Dict with stats for each index
        """
        stats = {}
        for store_name in ["communities", "assessments", "policies"]:
            try:
                store = self._get_store(store_name)
                stats[store_name] = store.get_stats()
            except Exception as e:
                logger.error(f"Error getting stats for {store_name}: {e}")
                stats[store_name] = {"error": str(e)}

        return stats


# Global singleton instance
_search_service = None


def get_similarity_search_service() -> SimilaritySearchService:
    """
    Get or create the global similarity search service instance.

    Returns:
        Singleton SimilaritySearchService instance
    """
    global _search_service
    if _search_service is None:
        _search_service = SimilaritySearchService()
    return _search_service
