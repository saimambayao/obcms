"""
Unified Semantic Search Engine

Provides semantic search across all OBCMS modules with natural language queries.
"""

import logging
from datetime import date
from typing import Any, Dict, List, Optional

from django.apps import apps

logger = logging.getLogger(__name__)


class UnifiedSearchEngine:
    """
    Universal semantic search across all OBCMS modules.

    Supports searching:
    - Communities (Community profiles, demographics, livelihoods)
    - MANA (Workshop activities, responses, assessments)
    - Policies (Policy recommendations and tracking)
    - Coordination (Organizations, stakeholders, partnerships)
    - Projects (Monitoring entries, PPAs, programs)
    """

    SEARCHABLE_MODULES = {
        'communities': {
            'model': 'CommunityProfileBase',
            'app': 'communities',
            'fields': ['name', 'description', 'primary_livelihood', 'ethnolinguistic_group'],
            'display_template': 'search/results/community.html',
            'vector_store': 'communities',
        },
        'mana': {
            'model': 'WorkshopActivity',
            'app': 'mana',
            'fields': ['title', 'description', 'findings', 'recommendations'],
            'display_template': 'search/results/workshop.html',
            'vector_store': 'assessments',
        },
        'policies': {
            'model': 'PolicyRecommendation',
            'app': 'recommendations.policy_tracking',
            'fields': ['title', 'description', 'problem_statement', 'proposed_solution'],
            'display_template': 'search/results/policy.html',
            'vector_store': 'policies',
        },
        'coordination': {
            'model': 'Organization',
            'app': 'coordination',
            'fields': ['name', 'description', 'sector', 'services_offered'],
            'display_template': 'search/results/organization.html',
            'vector_store': 'organizations',
        },
        'projects': {
            'model': 'MonitoringEntry',
            'app': 'monitoring',
            'fields': ['title', 'description', 'objectives', 'expected_outcomes'],
            'display_template': 'search/results/project.html',
            'vector_store': 'projects',
        }
    }

    def __init__(self):
        """Initialize the unified search engine."""
        # Import AI services with proper error handling
        try:
            from ai_assistant.services import (
                EmbeddingService,
                GeminiService,
                SimilaritySearchService,
                HAS_EMBEDDING_SERVICE,
                HAS_SIMILARITY_SEARCH
            )

            if not HAS_EMBEDDING_SERVICE:
                raise ImportError("EmbeddingService not available")
            if not HAS_SIMILARITY_SEARCH:
                raise ImportError("SimilaritySearchService not available")

            self.embedding_service = EmbeddingService()
            self.similarity_search = SimilaritySearchService()
            self.gemini = GeminiService()

        except ImportError as e:
            logger.error(f"AI services not available for unified search: {e}")
            raise RuntimeError(
                f"Unified search requires AI services. Install required dependencies: {e}"
            )

        # Import query parser and ranker (lazy import to avoid circular deps)
        from .query_parser import QueryParser
        from .result_ranker import ResultRanker

        self.query_parser = QueryParser()
        self.ranker = ResultRanker()

        logger.info("UnifiedSearchEngine initialized")

    def search(
        self,
        query: str,
        modules: Optional[List[str]] = None,
        limit: int = 20,
        threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Universal search across modules.

        Args:
            query: Natural language query (e.g., "coastal fishing communities in Zamboanga")
            modules: Filter by modules (default: all)
            limit: Max results per module
            threshold: Minimum similarity score (0-1)

        Returns:
            {
                'query': str,
                'parsed_query': dict,
                'results': dict (by module),
                'total_results': int,
                'summary': str
            }
        """
        logger.info(f"Unified search: {query}")

        # Parse query
        parsed = self.query_parser.parse(query)

        # Select modules to search
        if modules is None:
            modules = list(self.SEARCHABLE_MODULES.keys())

        # Validate modules
        modules = [m for m in modules if m in self.SEARCHABLE_MODULES]

        # Search each module
        results = {}
        for module in modules:
            try:
                results[module] = self._search_module(
                    module, query, parsed, limit, threshold
                )
            except Exception as e:
                logger.error(f"Error searching module {module}: {e}")
                results[module] = []

        # Rank and combine results
        ranked_results = self.ranker.rank_cross_module(results, query)

        # Generate summary
        summary = self._generate_summary(query, ranked_results)

        total_results = sum(len(r) for r in ranked_results.values())

        return {
            'query': query,
            'parsed_query': parsed,
            'results': ranked_results,
            'total_results': total_results,
            'summary': summary,
        }

    def _search_module(
        self,
        module: str,
        query: str,
        parsed: Dict,
        limit: int,
        threshold: float
    ) -> List[Dict]:
        """Search within a specific module using vector similarity."""
        config = self.SEARCHABLE_MODULES[module]

        # Get model class
        try:
            Model = apps.get_model(config['app'], config['model'])
        except LookupError:
            logger.error(f"Model {config['app']}.{config['model']} not found")
            return []

        # Generate query embedding
        query_vector = self.embedding_service.generate_embedding(query)

        # Search using similarity search service
        store_name = config['vector_store']
        try:
            from ai_assistant.services import VectorStore, HAS_VECTOR_STORE
            if not HAS_VECTOR_STORE:
                logger.warning(f"VectorStore not available. Skipping {module}.")
                return []
            store = VectorStore.load(store_name)
        except FileNotFoundError:
            logger.warning(f"Vector store '{store_name}' not found. Skipping {module}.")
            return []

        # Search vector store
        raw_results = store.search_by_threshold(
            query_vector,
            threshold=threshold,
            max_results=limit * 2  # Get more for filtering
        )

        # Format results
        results = []
        for position, similarity, metadata in raw_results:
            obj_id = metadata.get('id')
            if not obj_id:
                continue

            try:
                obj = Model.objects.get(id=obj_id)
                results.append({
                    'object': obj,
                    'module': module,
                    'similarity_score': similarity,
                    'snippet': self._extract_snippet(obj, query, config['fields']),
                    'template': config['display_template'],
                    'metadata': metadata,
                })
            except Model.DoesNotExist:
                logger.warning(f"{Model.__name__} {obj_id} not found")
                continue

        # Apply filters from parsed query
        results = self._apply_filters(results, parsed.get('filters', {}))

        return results[:limit]

    def _extract_snippet(self, obj: Any, query: str, fields: List[str]) -> str:
        """
        Extract relevant snippet from object.

        Args:
            obj: Model instance
            query: Search query
            fields: Fields to extract from

        Returns:
            Formatted snippet string
        """
        parts = []
        query_lower = query.lower()

        for field in fields:
            if hasattr(obj, field):
                value = getattr(obj, field)
                if value:
                    value_str = str(value)
                    # Highlight relevant parts
                    if query_lower in value_str.lower():
                        parts.append(value_str[:200])

        if not parts:
            # Fallback: use first available field
            for field in fields:
                if hasattr(obj, field):
                    value = getattr(obj, field)
                    if value:
                        parts.append(str(value)[:200])
                        break

        return " | ".join(parts) if parts else str(obj)

    def _apply_filters(self, results: List[Dict], filters: Dict) -> List[Dict]:
        """
        Apply filters to results based on parsed query.

        Args:
            results: List of search results
            filters: Filter criteria from parsed query

        Returns:
            Filtered results
        """
        if not filters:
            return results

        filtered = results

        # Location filter
        if 'location' in filters:
            location = filters['location'].lower()
            filtered = [
                r for r in filtered
                if self._matches_location(r['object'], location)
            ]

        # Sector filter
        if 'sector' in filters:
            sector = filters['sector'].lower()
            filtered = [
                r for r in filtered
                if self._matches_sector(r['object'], sector)
            ]

        # Date range filter
        if 'date_range' in filters:
            date_range = filters['date_range']
            filtered = [
                r for r in filtered
                if self._matches_date_range(r['object'], date_range)
            ]

        return filtered

    def _matches_location(self, obj: Any, location: str) -> bool:
        """Check if object matches location filter."""
        # Check common location fields
        for field in ['region', 'province', 'municipality', 'barangay']:
            if hasattr(obj, field):
                value = getattr(obj, field)
                if value:
                    value_str = str(value).lower()
                    if location in value_str:
                        return True

        # Check nested relationships
        if hasattr(obj, 'community'):
            community = getattr(obj, 'community')
            if community:
                return self._matches_location(community, location)

        return False

    def _matches_sector(self, obj: Any, sector: str) -> bool:
        """Check if object matches sector filter."""
        if hasattr(obj, 'sector'):
            value = getattr(obj, 'sector')
            if value:
                return sector in str(value).lower()

        if hasattr(obj, 'category'):
            value = getattr(obj, 'category')
            if value:
                return sector in str(value).lower()

        return False

    def _matches_date_range(self, obj: Any, date_range: Dict) -> bool:
        """Check if object matches date range filter."""
        date_field = None

        # Find date field
        for field in ['created_at', 'date', 'start_date', 'updated_at']:
            if hasattr(obj, field):
                date_field = field
                break

        if not date_field:
            return True  # No date field, include by default

        obj_date = getattr(obj, date_field)
        if not obj_date:
            return True

        # Convert to date if datetime
        if hasattr(obj_date, 'date'):
            obj_date = obj_date.date()

        # Check range
        start = date_range.get('start')
        end = date_range.get('end')

        if start and obj_date < start:
            return False

        if end and obj_date > end:
            return False

        return True

    def _generate_summary(self, query: str, results: Dict[str, List]) -> str:
        """
        Generate AI summary of search results.

        Args:
            query: Search query
            results: Results by module

        Returns:
            Summary text
        """
        total = sum(len(r) for r in results.values())

        if total == 0:
            return f"No results found for '{query}'. Try different keywords."

        # Build summary prompt
        result_counts = {
            module: len(items)
            for module, items in results.items()
            if len(items) > 0
        }

        prompt = f"""
Summarize these search results in 2-3 sentences:

Query: "{query}"

Results:
{self._format_result_counts(result_counts)}

Total: {total} results

Provide helpful context about what was found. Be specific and concise.
"""

        try:
            response = self.gemini.generate_text(
                prompt,
                temperature=0.4,
                use_cache=False,
                include_cultural_context=False
            )

            if response.get('success'):
                return response['text']
            else:
                return self._fallback_summary(query, total, result_counts)

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return self._fallback_summary(query, total, result_counts)

    def _format_result_counts(self, result_counts: Dict[str, int]) -> str:
        """Format result counts for prompt."""
        lines = []
        for module, count in result_counts.items():
            module_name = module.replace('_', ' ').title()
            lines.append(f"- {module_name}: {count} found")
        return "\n".join(lines)

    def _fallback_summary(self, query: str, total: int, result_counts: Dict) -> str:
        """Fallback summary when AI generation fails."""
        modules = ", ".join(result_counts.keys())
        return (
            f"Found {total} results for '{query}' across {len(result_counts)} modules "
            f"({modules})."
        )

    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get statistics for all search indices.

        Returns:
            Dict with stats for each module
        """
        stats = {}

        for module, config in self.SEARCHABLE_MODULES.items():
            try:
                from ai_assistant.services import VectorStore, HAS_VECTOR_STORE
                if not HAS_VECTOR_STORE:
                    stats[module] = {
                        'vector_count': 0,
                        'dimension': 0,
                        'model': config['model'],
                        'status': 'vector_store_unavailable'
                    }
                    continue
                store = VectorStore.load(config['vector_store'])
                stats[module] = {
                    'vector_count': store.vector_count,
                    'dimension': store.dimension,
                    'model': config['model'],
                }
            except FileNotFoundError:
                stats[module] = {
                    'vector_count': 0,
                    'dimension': 0,
                    'model': config['model'],
                    'status': 'not_indexed'
                }
            except Exception as e:
                logger.error(f"Error getting stats for {module}: {e}")
                stats[module] = {'error': str(e)}

        return stats

    def reindex_module(self, module: str) -> Dict[str, Any]:
        """
        Reindex a specific module.

        Args:
            module: Module name to reindex

        Returns:
            Indexing statistics
        """
        if module not in self.SEARCHABLE_MODULES:
            raise ValueError(f"Unknown module: {module}")

        config = self.SEARCHABLE_MODULES[module]

        # Get model
        try:
            Model = apps.get_model(config['app'], config['model'])
        except LookupError:
            raise ValueError(f"Model {config['app']}.{config['model']} not found")

        # Get all objects
        objects = Model.objects.all()
        total_count = objects.count()

        logger.info(f"Reindexing {module}: {total_count} objects")

        # Create/load vector store
        from ai_assistant.services import VectorStore, HAS_VECTOR_STORE
        if not HAS_VECTOR_STORE:
            raise RuntimeError("VectorStore not available for reindexing")
        store = VectorStore(
            config['vector_store'],
            dimension=self.embedding_service.get_dimension()
        )

        # Generate embeddings and add to store
        indexed_count = 0
        for obj in objects:
            try:
                # Format object as text
                text = self._format_object_text(obj, config['fields'])

                # Generate embedding
                embedding = self.embedding_service.generate_embedding(text)

                # Add to store
                metadata = {
                    'id': obj.id,
                    'type': module,
                    'model': config['model'],
                }
                store.add_vector(embedding, metadata)

                indexed_count += 1

                if indexed_count % 100 == 0:
                    logger.info(f"Indexed {indexed_count}/{total_count} {module}")

            except Exception as e:
                logger.error(f"Error indexing {module} {obj.id}: {e}")
                continue

        # Save store
        store.save()

        logger.info(f"Reindexing complete: {indexed_count}/{total_count} {module}")

        return {
            'module': module,
            'total': total_count,
            'indexed': indexed_count,
            'skipped': total_count - indexed_count,
        }

    def _format_object_text(self, obj: Any, fields: List[str]) -> str:
        """
        Format object as text for embedding.

        Args:
            obj: Model instance
            fields: Fields to include

        Returns:
            Formatted text
        """
        parts = []

        for field in fields:
            if hasattr(obj, field):
                value = getattr(obj, field)
                if value:
                    parts.append(f"{field.replace('_', ' ').title()}: {value}")

        return "\n".join(parts)


# Global singleton instance
_search_engine_instance = None


def get_unified_search_engine() -> UnifiedSearchEngine:
    """
    Get or create the global unified search engine instance.

    Returns:
        Singleton UnifiedSearchEngine instance
    """
    global _search_engine_instance
    if _search_engine_instance is None:
        _search_engine_instance = UnifiedSearchEngine()
    return _search_engine_instance
