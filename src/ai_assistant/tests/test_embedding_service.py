"""
Tests for the EmbeddingService.

Run with:
    pytest src/ai_assistant/tests/test_embedding_service.py -v
"""

import numpy as np
import pytest

from ai_assistant.services.embedding_service import EmbeddingService, get_embedding_service


class TestEmbeddingService:
    """Test cases for EmbeddingService."""

    def test_initialization(self):
        """Test that the service initializes correctly."""
        service = EmbeddingService()
        assert service is not None
        assert service.get_dimension() == 384  # all-MiniLM-L6-v2 dimension

    def test_singleton_service(self):
        """Test that get_embedding_service returns the same instance."""
        service1 = get_embedding_service()
        service2 = get_embedding_service()
        assert service1 is service2

    def test_generate_embedding_single(self):
        """Test generating embedding for a single text."""
        service = EmbeddingService()
        text = "Bangsamoro community in Zamboanga Peninsula"

        embedding = service.generate_embedding(text)

        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (384,)
        assert not np.all(embedding == 0)  # Should not be all zeros

    def test_generate_embedding_empty_text(self):
        """Test that empty text returns zero vector."""
        service = EmbeddingService()

        embedding = service.generate_embedding("")

        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (384,)
        assert np.all(embedding == 0)  # Should be all zeros

    def test_batch_generate(self):
        """Test generating embeddings in batch."""
        service = EmbeddingService()
        texts = [
            "First community in Region IX",
            "Second community in Region X",
            "Third community in Region XI"
        ]

        embeddings = service.batch_generate(texts)

        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape == (3, 384)
        # Check that embeddings are different
        assert not np.allclose(embeddings[0], embeddings[1])

    def test_batch_generate_empty_list(self):
        """Test batch generation with empty list."""
        service = EmbeddingService()

        embeddings = service.batch_generate([])

        assert isinstance(embeddings, np.ndarray)
        assert len(embeddings) == 0

    def test_compute_similarity(self):
        """Test computing similarity between embeddings."""
        service = EmbeddingService()

        # Similar texts should have high similarity
        emb1 = service.generate_embedding("Muslim community in coastal area")
        emb2 = service.generate_embedding("Islamic community near the sea")

        # Very different texts should have lower similarity
        emb3 = service.generate_embedding("Agricultural farming techniques")

        sim_similar = service.compute_similarity(emb1, emb2)
        sim_different = service.compute_similarity(emb1, emb3)

        assert 0 <= sim_similar <= 1
        assert 0 <= sim_different <= 1
        assert sim_similar > sim_different  # Similar texts should score higher

    def test_compute_content_hash(self):
        """Test computing content hash."""
        service = EmbeddingService()

        text = "Test content for hashing"
        hash1 = service.compute_content_hash(text)
        hash2 = service.compute_content_hash(text)

        assert hash1 == hash2  # Same text should produce same hash
        assert len(hash1) == 32  # MD5 hash is 32 characters

        # Different text should produce different hash
        hash3 = service.compute_content_hash("Different content")
        assert hash1 != hash3

    def test_should_reembed(self):
        """Test checking if content needs re-embedding."""
        service = EmbeddingService()

        text = "Original content"
        stored_hash = service.compute_content_hash(text)

        # Same content should not need re-embedding
        assert not service.should_reembed(text, stored_hash)

        # Different content should need re-embedding
        assert service.should_reembed("Modified content", stored_hash)

        # No stored hash should need re-embedding
        assert service.should_reembed(text, None)

    def test_normalized_embeddings(self):
        """Test that embeddings are L2 normalized when requested."""
        service = EmbeddingService()

        text = "Test normalization"
        embedding = service.generate_embedding(text, normalize=True)

        # Normalized vector should have L2 norm close to 1
        norm = np.linalg.norm(embedding)
        assert abs(norm - 1.0) < 0.01  # Allow small floating point error

    def test_semantic_similarity_example(self):
        """Test real-world semantic similarity example."""
        service = EmbeddingService()

        # Communities with similar characteristics
        texts = [
            "Tausug fishing community in Zamboanga",
            "Muslim fisher folk community in coastal area",
            "Agricultural highland community with rice farming",
            "Christian farming community in mountain region"
        ]

        embeddings = service.batch_generate(texts)

        # Compute all pairwise similarities
        sim_01 = service.compute_similarity(embeddings[0], embeddings[1])
        sim_23 = service.compute_similarity(embeddings[2], embeddings[3])
        sim_02 = service.compute_similarity(embeddings[0], embeddings[2])

        # Similar pairs should score higher than dissimilar pairs
        assert sim_01 > 0.5  # Fishing communities should be similar
        assert sim_23 > 0.5  # Farming communities should be similar
        assert sim_02 < sim_01  # Fishing vs farming should be less similar


@pytest.mark.django_db
class TestEmbeddingServiceIntegration:
    """Integration tests for EmbeddingService with Django."""

    def test_service_with_database(self):
        """Test that service works in Django context."""
        service = get_embedding_service()
        text = "Integration test"

        embedding = service.generate_embedding(text)

        assert embedding is not None
        assert len(embedding) == 384
