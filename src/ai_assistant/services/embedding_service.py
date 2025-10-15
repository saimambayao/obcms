"""
Embedding Service

Generates vector embeddings for text using Sentence Transformers.
Uses 'all-MiniLM-L6-v2' model (384 dimensions, fast, accurate).

Why Sentence Transformers:
- Local execution (no API costs)
- Fast inference (100+ docs/sec)
- High quality embeddings
- No external dependencies
- Perfect for <100K documents
"""

import hashlib
import logging
from typing import List, Optional, Union

import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Generate embeddings using Sentence Transformers.

    Model: all-MiniLM-L6-v2
    - Dimensions: 384 (smaller than 768, faster)
    - Performance: Excellent for semantic similarity
    - Speed: ~100+ sentences/second on CPU
    - Memory: ~100MB model size
    """

    # Class-level cache for the model
    _model = None
    _model_name = 'sentence-transformers/all-MiniLM-L6-v2'

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the embedding service.

        Args:
            model_name: Optional custom model name. Defaults to all-MiniLM-L6-v2
        """
        self.model_name = model_name or self._model_name
        self._ensure_model_loaded()

    def _ensure_model_loaded(self):
        """Load the sentence transformer model (singleton pattern)."""
        if EmbeddingService._model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            try:
                # Import here to avoid heavy imports during Django startup
                from sentence_transformers import SentenceTransformer
                EmbeddingService._model = SentenceTransformer(self.model_name)
                logger.info(f"Model loaded successfully. Embedding dimension: {self.get_dimension()}")
            except ImportError as e:
                logger.error(f"SentenceTransformers library not available: {e}")
                raise RuntimeError(f"SentenceTransformers library is required but not installed: {e}")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise RuntimeError(f"Could not load embedding model: {e}")

    @property
    def model(self):
        """Get the loaded model instance."""
        self._ensure_model_loaded()
        return EmbeddingService._model

    def get_dimension(self) -> int:
        """Get the embedding dimension of the current model."""
        return self.model.get_sentence_embedding_dimension()

    def generate_embedding(self, text: str, normalize: bool = True) -> np.ndarray:
        """
        Generate embedding vector for a single text.

        Args:
            text: Input text to encode
            normalize: Whether to L2 normalize the embedding (recommended for cosine similarity)

        Returns:
            numpy array of shape (dimension,)

        Example:
            >>> service = EmbeddingService()
            >>> embedding = service.generate_embedding("Bangsamoro community in Zamboanga")
            >>> embedding.shape
            (384,)
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding generation")
            return np.zeros(self.get_dimension())

        try:
            embedding = self.model.encode(
                text,
                normalize_embeddings=normalize,
                show_progress_bar=False
            )
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def batch_generate(
        self,
        texts: List[str],
        normalize: bool = True,
        batch_size: int = 32,
        show_progress: bool = False
    ) -> np.ndarray:
        """
        Generate embeddings for multiple texts in batches.

        Args:
            texts: List of input texts
            normalize: Whether to L2 normalize embeddings
            batch_size: Number of texts to process at once
            show_progress: Whether to show progress bar

        Returns:
            numpy array of shape (len(texts), dimension)

        Example:
            >>> service = EmbeddingService()
            >>> texts = ["First community", "Second community", "Third community"]
            >>> embeddings = service.batch_generate(texts)
            >>> embeddings.shape
            (3, 384)
        """
        if not texts:
            logger.warning("Empty text list provided for batch embedding generation")
            return np.array([])

        # Filter out empty texts
        valid_texts = [text if text and text.strip() else "" for text in texts]

        try:
            embeddings = self.model.encode(
                valid_texts,
                normalize_embeddings=normalize,
                batch_size=batch_size,
                show_progress_bar=show_progress
            )
            return embeddings
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise

    def compute_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score (0 to 1, higher = more similar)

        Example:
            >>> service = EmbeddingService()
            >>> emb1 = service.generate_embedding("Bangsamoro community")
            >>> emb2 = service.generate_embedding("Muslim community")
            >>> similarity = service.compute_similarity(emb1, emb2)
            >>> print(f"Similarity: {similarity:.3f}")
        """
        # For normalized embeddings, dot product = cosine similarity
        return np.dot(embedding1, embedding2)

    def compute_content_hash(self, text: str) -> str:
        """
        Compute MD5 hash of text content.
        Used to detect if content has changed and needs re-embedding.

        Args:
            text: Input text

        Returns:
            MD5 hash string
        """
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def should_reembed(
        self,
        current_text: str,
        stored_hash: Optional[str]
    ) -> bool:
        """
        Check if text needs to be re-embedded.

        Args:
            current_text: Current text content
            stored_hash: Previously stored content hash

        Returns:
            True if re-embedding is needed
        """
        if not stored_hash:
            return True

        current_hash = self.compute_content_hash(current_text)
        return current_hash != stored_hash


# Global singleton instance
_service_instance = None


def get_embedding_service() -> EmbeddingService:
    """
    Get or create the global embedding service instance.

    Returns:
        Singleton EmbeddingService instance
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = EmbeddingService()
    return _service_instance
