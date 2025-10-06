"""
Tests for the SimilaritySearchService.

Run with:
    pytest src/ai_assistant/tests/test_similarity_search.py -v
"""

import tempfile
from pathlib import Path

import numpy as np
import pytest
from django.contrib.contenttypes.models import ContentType

from ai_assistant.models import DocumentEmbedding
from ai_assistant.services.embedding_service import get_embedding_service
from ai_assistant.services.similarity_search import (
    SimilaritySearchService,
    get_similarity_search_service,
)
from ai_assistant.services.vector_store import VectorStore


@pytest.fixture
def populated_community_store():
    """Create a populated community vector store for testing."""
    embedding_service = get_embedding_service()
    store = VectorStore('communities_test', dimension=embedding_service.get_dimension())

    # Add sample community embeddings
    texts = [
        "Tausug fishing community in Zamboanga Peninsula coastal area",
        "Muslim fisher folk community near the sea",
        "Agricultural highland community with rice farming",
        "Christian farming community in mountain region",
        "Urban Muslim community in city center",
    ]

    embeddings = embedding_service.batch_generate(texts)
    metadata_list = [
        {
            'id': i + 1,
            'type': 'community',
            'module': 'communities',
            'data': {
                'name': f'Community {i + 1}',
                'municipality': 'Test Municipality',
                'province': 'Test Province',
                'region': 'Region IX'
            }
        }
        for i in range(len(texts))
    ]

    store.add_vectors(embeddings, metadata_list)

    # Save to temp location
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / 'communities_test.index'
        store.save(str(filepath))
        yield store, filepath


class TestSimilaritySearchService:
    """Test cases for SimilaritySearchService."""

    def test_initialization(self):
        """Test that service initializes correctly."""
        service = SimilaritySearchService()
        assert service is not None
        assert service.embedding_service is not None

    def test_singleton_service(self):
        """Test that get_similarity_search_service returns same instance."""
        service1 = get_similarity_search_service()
        service2 = get_similarity_search_service()
        assert service1 is service2

    @pytest.mark.skip(reason="Requires actual vector store file")
    def test_search_communities_basic(self):
        """Test basic community search."""
        service = SimilaritySearchService()

        # This test would work if communities index exists
        results = service.search_communities(
            "fishing community near coast",
            limit=5,
            threshold=0.3
        )

        # Results could be empty if index doesn't exist
        assert isinstance(results, list)

    def test_search_empty_index(self):
        """Test searching on non-existent index."""
        service = SimilaritySearchService()

        results = service.search_communities(
            "test query",
            limit=5
        )

        # Should return empty list for non-existent index
        assert results == []

    def test_get_index_stats(self):
        """Test getting statistics for all indices."""
        service = SimilaritySearchService()
        stats = service.get_index_stats()

        assert isinstance(stats, dict)
        assert 'communities' in stats
        assert 'assessments' in stats
        assert 'policies' in stats

    def test_format_community_text(self):
        """Test formatting community data as text."""
        from communities.models import BarangayOBC, Municipality, Province, Region

        service = SimilaritySearchService()

        # Create mock community (not saved to DB)
        class MockBarangay:
            name = "Test Barangay"

        class MockMunicipality:
            name = "Test Municipality"

        class MockProvince:
            name = "Test Province"

        class MockRegion:
            name = "Region IX"

        class MockCommunity:
            name = "Test Community"
            barangay = MockBarangay()
            municipality = MockMunicipality()
            province = MockProvince()
            region = MockRegion()
            total_population = 5000

        community = MockCommunity()
        text = service._format_community_text(community)

        assert "Test Community" in text
        assert "Test Barangay" in text
        assert "Test Municipality" in text
        assert "Test Province" in text
        assert "Region IX" in text
        assert "5000" in text

    def test_format_policy_text(self):
        """Test formatting policy data as text."""
        service = SimilaritySearchService()

        # Create mock policy
        class MockPolicy:
            title = "Test Policy"
            description = "Test Description"
            status = 'draft'

            def get_status_display(self):
                return "Draft"

        policy = MockPolicy()
        text = service._format_policy_text(policy)

        assert "Test Policy" in text
        assert "Test Description" in text
        assert "Draft" in text


@pytest.mark.django_db
class TestSimilaritySearchIntegration:
    """Integration tests for SimilaritySearchService."""

    def test_service_with_database_context(self):
        """Test that service works in Django context."""
        service = get_similarity_search_service()
        assert service is not None

    def test_search_all_modules(self):
        """Test unified search across modules."""
        service = SimilaritySearchService()

        results = service.search_all(
            "education program",
            limit=5,
            threshold=0.5
        )

        assert isinstance(results, dict)
        assert 'communities' in results
        assert 'assessments' in results
        assert 'policies' in results
        assert isinstance(results['communities'], list)
        assert isinstance(results['assessments'], list)
        assert isinstance(results['policies'], list)

    @pytest.mark.skip(reason="Requires actual data in database")
    def test_find_similar_communities(self):
        """Test finding similar communities."""
        service = SimilaritySearchService()

        # This would work with actual community data
        # For now, just verify the method exists and handles errors
        results = service.find_similar_communities(
            community_id=99999,  # Non-existent ID
            limit=5
        )

        assert isinstance(results, list)

    @pytest.mark.skip(reason="Requires actual data in database")
    def test_find_similar_policies(self):
        """Test finding similar policies."""
        service = SimilaritySearchService()

        results = service.find_similar_policies(
            policy_id=99999,  # Non-existent ID
            limit=5
        )

        assert isinstance(results, list)


@pytest.mark.django_db
class TestDocumentEmbeddingModel:
    """Test the DocumentEmbedding model."""

    def test_create_document_embedding(self):
        """Test creating a DocumentEmbedding instance."""
        from communities.models import Region

        # Create a test region
        region = Region.objects.create(
            code='TEST',
            name='Test Region'
        )

        content_type = ContentType.objects.get_for_model(Region)

        embedding = DocumentEmbedding.objects.create(
            content_type=content_type,
            object_id=region.id,
            embedding_hash='test_hash_123',
            index_name='test_index',
            model_used='test_model',
            dimension=384
        )

        assert embedding.id is not None
        assert embedding.content_object == region
        assert embedding.embedding_hash == 'test_hash_123'
        assert embedding.index_name == 'test_index'

    def test_is_indexed(self):
        """Test checking if object is indexed."""
        from communities.models import Region

        region = Region.objects.create(
            code='TEST2',
            name='Test Region 2'
        )

        # Should not be indexed initially
        assert not DocumentEmbedding.is_indexed(region, 'communities')

        # Create embedding
        content_type = ContentType.objects.get_for_model(Region)
        DocumentEmbedding.objects.create(
            content_type=content_type,
            object_id=region.id,
            embedding_hash='hash',
            index_name='communities'
        )

        # Should now be indexed
        assert DocumentEmbedding.is_indexed(region, 'communities')

    def test_get_or_create_for_object(self):
        """Test get_or_create_for_object method."""
        from communities.models import Region

        region = Region.objects.create(
            code='TEST3',
            name='Test Region 3'
        )

        # First call should create
        embedding1, created1 = DocumentEmbedding.get_or_create_for_object(
            region,
            'communities',
            'hash_abc'
        )

        assert created1 is True
        assert embedding1.embedding_hash == 'hash_abc'

        # Second call should get existing
        embedding2, created2 = DocumentEmbedding.get_or_create_for_object(
            region,
            'communities',
            'hash_xyz'
        )

        assert created2 is False
        assert embedding2.id == embedding1.id

    def test_unique_constraint(self):
        """Test unique constraint on content_type, object_id, index_name."""
        from communities.models import Region

        region = Region.objects.create(
            code='TEST4',
            name='Test Region 4'
        )

        content_type = ContentType.objects.get_for_model(Region)

        # Create first embedding
        DocumentEmbedding.objects.create(
            content_type=content_type,
            object_id=region.id,
            embedding_hash='hash1',
            index_name='communities'
        )

        # Should not allow duplicate
        with pytest.raises(Exception):  # IntegrityError
            DocumentEmbedding.objects.create(
                content_type=content_type,
                object_id=region.id,
                embedding_hash='hash2',
                index_name='communities'
            )
