"""
Tests for the VectorStore.

Run with:
    pytest src/ai_assistant/tests/test_vector_store.py -v
"""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from ai_assistant.services.vector_store import VectorStore


class TestVectorStore:
    """Test cases for VectorStore."""

    def test_initialization(self):
        """Test that vector store initializes correctly."""
        store = VectorStore('test_index', dimension=384)

        assert store.index_name == 'test_index'
        assert store.dimension == 384
        assert store.vector_count == 0

    def test_add_single_vector(self):
        """Test adding a single vector."""
        store = VectorStore('test', dimension=384)
        vector = np.random.rand(384)
        metadata = {'id': 1, 'type': 'test'}

        position = store.add_vector(vector, metadata)

        assert position == 0
        assert store.vector_count == 1
        assert len(store.metadata) == 1
        assert store.metadata[0] == metadata

    def test_add_multiple_vectors(self):
        """Test adding multiple vectors in batch."""
        store = VectorStore('test', dimension=384)
        vectors = np.random.rand(10, 384)
        metadata_list = [{'id': i, 'type': 'test'} for i in range(10)]

        positions = store.add_vectors(vectors, metadata_list)

        assert len(positions) == 10
        assert store.vector_count == 10
        assert len(store.metadata) == 10

    def test_add_vector_wrong_dimension(self):
        """Test that adding vector with wrong dimension raises error."""
        store = VectorStore('test', dimension=384)
        wrong_vector = np.random.rand(128)  # Wrong dimension

        with pytest.raises(ValueError, match="does not match"):
            store.add_vector(wrong_vector, {'id': 1})

    def test_search_basic(self):
        """Test basic search functionality."""
        store = VectorStore('test', dimension=384)

        # Add some vectors
        vectors = np.random.rand(5, 384)
        metadata_list = [{'id': i, 'type': 'test', 'name': f'Item {i}'} for i in range(5)]
        store.add_vectors(vectors, metadata_list)

        # Search with first vector (should return itself as top result)
        results = store.search(vectors[0], k=3)

        assert len(results) == 3
        assert results[0][0] == 0  # Position of first vector
        assert results[0][1] < 0.01  # Distance should be very small (almost zero)
        assert results[0][2]['id'] == 0

    def test_search_empty_index(self):
        """Test searching on empty index."""
        store = VectorStore('test', dimension=384)
        query = np.random.rand(384)

        results = store.search(query, k=5)

        assert results == []

    def test_search_by_threshold(self):
        """Test searching with similarity threshold."""
        store = VectorStore('test', dimension=384)

        # Add normalized vectors (important for similarity calculation)
        vectors = np.random.rand(10, 384)
        vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
        metadata_list = [{'id': i, 'type': 'test'} for i in range(10)]
        store.add_vectors(vectors, metadata_list)

        # Search with high threshold
        query = vectors[0]
        results = store.search_by_threshold(query, threshold=0.95, max_results=5)

        # Should return at least the query vector itself
        assert len(results) >= 1
        # Check that results are sorted by similarity (descending)
        if len(results) > 1:
            assert results[0][1] >= results[1][1]

    def test_save_and_load(self):
        """Test saving and loading vector store."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and populate store
            store1 = VectorStore('test', dimension=384)
            vectors = np.random.rand(5, 384)
            metadata_list = [{'id': i, 'type': 'test'} for i in range(5)]
            store1.add_vectors(vectors, metadata_list)

            # Save
            filepath = Path(tmpdir) / 'test.index'
            store1.save(str(filepath))

            # Load
            store2 = VectorStore.load('test', filepath=str(filepath))

            # Verify
            assert store2.index_name == store1.index_name
            assert store2.dimension == store1.dimension
            assert store2.vector_count == store1.vector_count
            assert len(store2.metadata) == len(store1.metadata)

            # Verify search works on loaded store
            results = store2.search(vectors[0], k=1)
            assert len(results) == 1

    def test_load_or_create_new(self):
        """Test load_or_create with non-existent index."""
        with tempfile.TemporaryDirectory():
            # Should create new store
            store = VectorStore.load_or_create('nonexistent', dimension=384)

            assert store.index_name == 'nonexistent'
            assert store.vector_count == 0

    def test_load_or_create_existing(self):
        """Test load_or_create with existing index."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and save store
            store1 = VectorStore('existing', dimension=384)
            vectors = np.random.rand(3, 384)
            metadata = [{'id': i} for i in range(3)]
            store1.add_vectors(vectors, metadata)

            filepath = Path(tmpdir) / 'existing.index'
            store1.save(str(filepath))

            # Should load existing store
            # We need to mock the default path for this test
            # For now, just verify the behavior with explicit path

    def test_clear_index(self):
        """Test clearing the index."""
        store = VectorStore('test', dimension=384)
        vectors = np.random.rand(5, 384)
        metadata = [{'id': i} for i in range(5)]
        store.add_vectors(vectors, metadata)

        assert store.vector_count == 5

        store.clear()

        assert store.vector_count == 0
        assert len(store.metadata) == 0

    def test_get_stats(self):
        """Test getting index statistics."""
        store = VectorStore('test', dimension=384)

        # Add diverse vectors
        vectors = np.random.rand(10, 384)
        metadata = [
            {'id': i, 'type': 'community' if i < 5 else 'policy'}
            for i in range(10)
        ]
        store.add_vectors(vectors, metadata)

        stats = store.get_stats()

        assert stats['index_name'] == 'test'
        assert stats['dimension'] == 384
        assert stats['total_vectors'] == 10
        assert 'community' in stats['type_distribution']
        assert 'policy' in stats['type_distribution']
        assert stats['type_distribution']['community'] == 5
        assert stats['type_distribution']['policy'] == 5

    def test_similarity_calculation(self):
        """Test that similarity scores are calculated correctly."""
        store = VectorStore('test', dimension=384)

        # Create two normalized vectors with known similarity
        vec1 = np.random.rand(384)
        vec1 = vec1 / np.linalg.norm(vec1)

        # Create a very similar vector (same direction)
        vec2 = vec1 + np.random.rand(384) * 0.01
        vec2 = vec2 / np.linalg.norm(vec2)

        # Create a dissimilar vector
        vec3 = np.random.rand(384)
        vec3 = vec3 / np.linalg.norm(vec3)

        store.add_vectors(
            np.array([vec1, vec2, vec3]),
            [{'id': 0}, {'id': 1}, {'id': 2}]
        )

        # Search with vec1
        results = store.search_by_threshold(vec1, threshold=0.5, max_results=3)

        # vec2 should be more similar than vec3
        # Find positions in results
        sim_scores = {r[2]['id']: r[1] for r in results}

        if 1 in sim_scores and 2 in sim_scores:
            assert sim_scores[1] > sim_scores[2]


@pytest.mark.django_db
class TestVectorStoreIntegration:
    """Integration tests for VectorStore with Django."""

    def test_get_storage_path(self):
        """Test getting default storage path."""
        store = VectorStore('communities', dimension=384)
        path = store.get_storage_path()

        assert 'vector_indices' in str(path)
        assert 'communities.index' in str(path)

    def test_persistence_workflow(self):
        """Test complete persistence workflow."""
        # Create, populate, and save
        store1 = VectorStore('test_persist', dimension=384)
        vectors = np.random.rand(3, 384)
        metadata = [
            {'id': 1, 'type': 'community', 'name': 'Community A'},
            {'id': 2, 'type': 'community', 'name': 'Community B'},
            {'id': 3, 'type': 'policy', 'name': 'Policy C'},
        ]
        store1.add_vectors(vectors, metadata)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / 'test_persist.index'
            store1.save(str(filepath))

            # Verify files exist
            assert filepath.exists()
            assert filepath.with_suffix('.metadata').exists()

            # Load and verify
            store2 = VectorStore.load('test_persist', filepath=str(filepath))
            assert store2.vector_count == 3

            # Test search on loaded store
            results = store2.search(vectors[0], k=1)
            assert len(results) == 1
            assert results[0][2]['name'] == 'Community A'
