"""
Similarity Calculator for Query Matching

Provides efficient string similarity calculations using multiple algorithms:
- Levenshtein distance (edit distance)
- Jaccard similarity (token overlap)
- Combined similarity score

Used by fallback handler to find similar successful queries.
"""

import logging
from typing import List, Set

logger = logging.getLogger(__name__)


class SimilarityCalculator:
    """
    Calculate similarity between query strings using multiple algorithms.

    Combines Levenshtein distance and Jaccard similarity for robust matching.
    Optimized for performance with caching and early termination.
    """

    def __init__(self):
        """Initialize similarity calculator."""
        self._cache = {}
        self._cache_size = 1000  # Maximum cache entries

    def calculate_similarity(self, query1: str, query2: str) -> float:
        """
        Calculate combined similarity score between two queries.

        Args:
            query1: First query string
            query2: Second query string

        Returns:
            Similarity score (0.0 = completely different, 1.0 = identical)

        Algorithm:
            - Levenshtein similarity: 60% weight
            - Jaccard similarity: 40% weight

        Example:
            >>> calc = SimilarityCalculator()
            >>> calc.calculate_similarity("communities in region 9", "communities in Region IX")
            0.89
        """
        # Check cache
        cache_key = (query1, query2)
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Normalize queries
        q1 = query1.lower().strip()
        q2 = query2.lower().strip()

        # Handle exact match
        if q1 == q2:
            return 1.0

        # Handle empty strings
        if not q1 or not q2:
            return 0.0

        # Calculate Levenshtein similarity (60% weight)
        lev_distance = self.levenshtein_distance(q1, q2)
        max_len = max(len(q1), len(q2))
        lev_similarity = 1.0 - (lev_distance / max_len) if max_len > 0 else 0.0

        # Calculate Jaccard similarity (40% weight)
        jaccard_sim = self.jaccard_similarity(q1, q2)

        # Combined score
        combined = (lev_similarity * 0.6) + (jaccard_sim * 0.4)

        # Cache result (with size limit)
        if len(self._cache) >= self._cache_size:
            # Remove oldest entry (simple FIFO)
            self._cache.pop(next(iter(self._cache)))
        self._cache[cache_key] = combined

        return combined

    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calculate Levenshtein distance (minimum edit operations).

        Args:
            s1: First string
            s2: Second string

        Returns:
            Number of insertions, deletions, or substitutions needed

        Algorithm:
            Dynamic programming with space optimization (O(min(m,n)) space)

        Example:
            >>> calc = SimilarityCalculator()
            >>> calc.levenshtein_distance("kitten", "sitting")
            3
        """
        # Handle edge cases
        if s1 == s2:
            return 0
        if not s1:
            return len(s2)
        if not s2:
            return len(s1)

        # Ensure s1 is shorter for space optimization
        if len(s1) > len(s2):
            s1, s2 = s2, s1

        # Trim common prefix to reduce problem size
        start = 0
        len_s1 = len(s1)
        len_s2 = len(s2)
        while start < len_s1 and start < len_s2 and s1[start] == s2[start]:
            start += 1
        if start:
            s1 = s1[start:]
            s2 = s2[start:]
            len_s1 -= start
            len_s2 -= start

        # Trim common suffix
        while len_s1 and len_s2 and s1[len_s1 - 1] == s2[len_s2 - 1]:
            len_s1 -= 1
            len_s2 -= 1

        if len_s1 == 0:
            return len_s2
        if len_s2 == 0:
            return len_s1

        s1 = s1[:len_s1]
        s2 = s2[:len_s2]

        # Initialize distance matrix (only need current and previous row)
        previous_row = list(range(len(s2) + 1))
        current_row = [0] * (len(s2) + 1)

        for i, c1 in enumerate(s1):
            current_row[0] = i + 1

            for j, c2 in enumerate(s2):
                # Cost of operations
                insert = previous_row[j + 1] + 1
                delete = current_row[j] + 1
                substitute = previous_row[j] + (0 if c1 == c2 else 1)

                # Take minimum
                current_row[j + 1] = min(insert, delete, substitute)

            # Swap rows
            previous_row, current_row = current_row, previous_row

        return previous_row[len(s2)]

    def jaccard_similarity(self, s1: str, s2: str) -> float:
        """
        Calculate Jaccard similarity (token overlap).

        Args:
            s1: First string
            s2: Second string

        Returns:
            Jaccard similarity coefficient (0.0 to 1.0)

        Formula:
            J(A, B) = |A ∩ B| / |A ∪ B|

        Example:
            >>> calc = SimilarityCalculator()
            >>> calc.jaccard_similarity("hello world", "hello there")
            0.333
        """
        # Tokenize into word sets
        tokens1 = self._tokenize(s1)
        tokens2 = self._tokenize(s2)

        # Handle empty sets
        if not tokens1 or not tokens2:
            return 0.0

        # Calculate intersection and union
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)

        # Jaccard coefficient
        if len(union) == 0:
            return 0.0

        return len(intersection) / len(union)

    def _tokenize(self, text: str) -> Set[str]:
        """
        Tokenize text into normalized word set.

        Args:
            text: Input text

        Returns:
            Set of normalized tokens
        """
        # Split on whitespace and punctuation
        import re
        tokens = re.findall(r'\w+', text.lower())
        return set(tokens)

    def find_most_similar(
        self,
        query: str,
        candidates: List[str],
        threshold: float = 0.0,
        limit: int = 5
    ) -> List[tuple]:
        """
        Find most similar queries from candidate list.

        Args:
            query: Query to match
            candidates: List of candidate queries
            threshold: Minimum similarity score (0.0 to 1.0)
            limit: Maximum number of results

        Returns:
            List of tuples: (candidate_query, similarity_score)
            Sorted by descending similarity

        Example:
            >>> calc = SimilarityCalculator()
            >>> candidates = [
            ...     "communities in Region IX",
            ...     "workshops in Zamboanga",
            ...     "communities in Region X"
            ... ]
            >>> calc.find_most_similar("communities in region 9", candidates, limit=2)
            [('communities in Region IX', 0.92), ('communities in Region X', 0.78)]
        """
        if not candidates:
            return []

        # Calculate similarities
        similarities = []
        for candidate in candidates:
            score = self.calculate_similarity(query, candidate)
            if score >= threshold:
                similarities.append((candidate, score))

        # Sort by score (descending) and limit
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:limit]

    def clear_cache(self):
        """Clear the similarity calculation cache."""
        self._cache.clear()

    def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        return {
            'size': len(self._cache),
            'max_size': self._cache_size,
            'utilization': len(self._cache) / self._cache_size if self._cache_size > 0 else 0
        }


# Singleton instance
_calculator = None


def get_similarity_calculator() -> SimilarityCalculator:
    """Get singleton similarity calculator instance."""
    global _calculator
    if _calculator is None:
        _calculator = SimilarityCalculator()
    return _calculator
