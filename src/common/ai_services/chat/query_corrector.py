"""
Query Corrector for Typos and Common Mistakes

Automatically corrects spelling errors and suggests query alternatives.
Uses dictionary-based corrections for domain-specific terms.
"""

import logging
import re
from typing import List, Optional

from .similarity import get_similarity_calculator

logger = logging.getLogger(__name__)


class QueryCorrector:
    """
    Correct common typos and suggest query alternatives.

    Features:
    - Dictionary-based corrections for domain terms
    - Fuzzy matching for close matches
    - Common mistake patterns
    - Contextual suggestions
    """

    # Common typo corrections (typo -> correct)
    TYPO_DICTIONARY = {
        # Communities
        'comunity': 'community',
        'comunitys': 'communities',
        'comunities': 'communities',
        'comunties': 'communities',
        'communitys': 'communities',
        'obc': 'OBC',
        'obcs': 'OBCs',

        # Regions
        'regon': 'region',
        'regeon': 'region',
        'rejoin': 'region',
        'ragion': 'region',

        # Locations
        'zamboanga': 'Zamboanga',
        'zambonga': 'Zamboanga',
        'davao': 'Davao',
        'cotabato': 'Cotabato',
        'soccsksargen': 'SOCCSKSARGEN',
        'soccksargen': 'SOCCSKSARGEN',

        # Ethnolinguistic groups
        'marano': 'Maranao',
        'maranaos': 'Maranao',
        'maguindanao': 'Maguindanao',
        'maguindanaos': 'Maguindanao',
        'tausug': 'Tausug',
        'tausugs': 'Tausug',
        'badjao': 'Badjao',
        'badjaos': 'Badjao',

        # MANA/Workshops
        'workshp': 'workshop',
        'worshop': 'workshop',
        'workship': 'workshop',
        'asessment': 'assessment',
        'assesment': 'assessment',
        'assement': 'assessment',
        'manna': 'MANA',

        # Coordination
        'partnership': 'partnership',
        'partneship': 'partnership',
        'stakeholder': 'stakeholder',
        'stakholders': 'stakeholders',
        'organization': 'organization',
        'organisaton': 'organization',

        # Policies
        'recomendation': 'recommendation',
        'recomendations': 'recommendations',
        'recomendations': 'recommendations',
        'policys': 'policies',
        'policeis': 'policies',

        # Actions
        'shwo': 'show',
        'sho': 'show',
        'lsit': 'list',
        'cunt': 'count',
        'connt': 'count',

        # Common words
        'the': 'the',
        'in': 'in',
        'of': 'of',
        'and': 'and',
    }

    # Region code variations
    REGION_CODE_MAPPING = {
        '9': 'IX',
        'ix': 'IX',
        '10': 'X',
        'x': 'X',
        '11': 'XI',
        'xi': 'XI',
        '12': 'XII',
        'xii': 'XII',
        'region 9': 'Region IX',
        'region 10': 'Region X',
        'region 11': 'Region XI',
        'region 12': 'Region XII',
    }

    # Common phrase corrections
    PHRASE_CORRECTIONS = {
        'how many community': 'how many communities',
        'show me community': 'show me communities',
        'list all community': 'list all communities',
        'in regon': 'in region',
        'from regon': 'from region',
        'workshp in': 'workshop in',
        'workshps in': 'workshops in',
    }

    def __init__(self):
        """Initialize query corrector."""
        self.similarity_calc = get_similarity_calculator()
        # Compile regex patterns for performance
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for phrase corrections."""
        self._phrase_patterns = {}
        for wrong, correct in self.PHRASE_CORRECTIONS.items():
            pattern = re.compile(r'\b' + re.escape(wrong) + r'\b', re.IGNORECASE)
            self._phrase_patterns[pattern] = correct

    def correct_spelling(self, query: str) -> str:
        """
        Correct spelling errors in query.

        Args:
            query: Raw user query

        Returns:
            Corrected query string

        Example:
            >>> corrector = QueryCorrector()
            >>> corrector.correct_spelling("how many comunitys in regon 9")
            "how many communities in region IX"
        """
        corrected = query

        # Step 1: Correct region codes
        corrected = self._correct_region_codes(corrected)

        # Step 2: Correct phrases
        corrected = self._correct_phrases(corrected)

        # Step 3: Correct individual words
        corrected = self._correct_words(corrected)

        return corrected

    def _correct_region_codes(self, query: str) -> str:
        """Normalize region code references."""
        result = query

        # Replace region codes (case-insensitive)
        for variant, standard in self.REGION_CODE_MAPPING.items():
            # Use word boundaries to avoid partial replacements
            pattern = r'\bregion\s+' + re.escape(variant) + r'\b'
            result = re.sub(pattern, f'Region {standard}', result, flags=re.IGNORECASE)

            # Also handle standalone codes after "in" or "from"
            pattern = r'\b(in|from)\s+' + re.escape(variant) + r'\b'
            result = re.sub(pattern, rf'\1 Region {standard}', result, flags=re.IGNORECASE)

        return result

    def _correct_phrases(self, query: str) -> str:
        """Correct common phrase mistakes."""
        result = query

        for pattern, correction in self._phrase_patterns.items():
            result = pattern.sub(correction, result)

        return result

    def _correct_words(self, query: str) -> str:
        """Correct individual word typos."""
        words = query.split()
        corrected_words = []

        for word in words:
            # Check if word (lowercase) is in dictionary
            word_lower = word.lower()

            if word_lower in self.TYPO_DICTIONARY:
                # Use correction, preserve original case pattern
                correction = self.TYPO_DICTIONARY[word_lower]
                corrected_words.append(self._preserve_case(word, correction))
            else:
                # Keep original
                corrected_words.append(word)

        return ' '.join(corrected_words)

    def _preserve_case(self, original: str, correction: str) -> str:
        """
        Apply correction while preserving case pattern of original.

        Examples:
            HELLO -> WORLD
            Hello -> World
            hello -> world
        """
        if original.isupper():
            return correction.upper()
        elif original[0].isupper() if original else False:
            return correction.capitalize()
        else:
            return correction.lower()

    def suggest_alternatives(self, query: str, limit: int = 5) -> List[str]:
        """
        Generate alternative query phrasings.

        Args:
            query: Original query
            limit: Maximum number of alternatives

        Returns:
            List of alternative query strings

        Example:
            >>> corrector = QueryCorrector()
            >>> corrector.suggest_alternatives("communities in region 9")
            [
                "How many communities are in Region IX?",
                "Show me communities in Region IX",
                "List all communities in Region IX",
                "Count communities in Region IX",
                "Communities located in Region IX"
            ]
        """
        alternatives = []

        # First, correct spelling
        corrected = self.correct_spelling(query)
        if corrected != query:
            alternatives.append(corrected)

        # Generate variations based on detected entities
        entities = self._extract_entities(corrected)

        if 'communities' in entities and 'location' in entities:
            location = entities.get('location', 'Region IX')
            alternatives.extend([
                f"How many communities are in {location}?",
                f"Show me communities in {location}",
                f"List all communities in {location}",
                f"Count communities in {location}",
                f"Communities located in {location}"
            ])

        elif 'workshops' in entities and 'location' in entities:
            location = entities.get('location', 'Region IX')
            alternatives.extend([
                f"How many workshops in {location}?",
                f"Show me MANA workshops in {location}",
                f"List workshops conducted in {location}",
                f"Count assessments in {location}"
            ])

        elif 'policies' in entities:
            alternatives.extend([
                "Show me all policy recommendations",
                "List active policy recommendations",
                "How many policy recommendations?",
                "Show me draft policies"
            ])

        elif 'partnerships' in entities:
            alternatives.extend([
                "List all partnerships",
                "Show me active partnerships",
                "How many partnerships?",
                "Count coordination partnerships"
            ])

        # Remove duplicates and limit
        unique_alternatives = []
        seen = set()
        for alt in alternatives:
            alt_lower = alt.lower()
            if alt_lower not in seen:
                unique_alternatives.append(alt)
                seen.add(alt_lower)

        return unique_alternatives[:limit]

    def _extract_entities(self, query: str) -> dict:
        """Extract entities from query for generating alternatives."""
        query_lower = query.lower()
        entities = {}

        # Check for communities
        if any(term in query_lower for term in ['community', 'communities', 'obc', 'barangay']):
            entities['communities'] = True

        # Check for workshops
        if any(term in query_lower for term in ['workshop', 'assessment', 'mana']):
            entities['workshops'] = True

        # Check for policies
        if any(term in query_lower for term in ['policy', 'policies', 'recommendation']):
            entities['policies'] = True

        # Check for partnerships
        if any(term in query_lower for term in ['partnership', 'coordination', 'stakeholder']):
            entities['partnerships'] = True

        # Extract location
        location_match = re.search(r'(region\s+[IX]+|zamboanga|davao|cotabato)', query, re.IGNORECASE)
        if location_match:
            entities['location'] = location_match.group(0)

        return entities

    def get_correction_confidence(self, original: str, corrected: str) -> float:
        """
        Calculate confidence in correction.

        Args:
            original: Original query
            corrected: Corrected query

        Returns:
            Confidence score (0.0 to 1.0)
            1.0 = high confidence in correction
            0.0 = no confidence (no correction needed)
        """
        if original == corrected:
            return 0.0  # No correction needed

        # Calculate how many words were corrected
        orig_words = set(original.lower().split())
        corr_words = set(corrected.lower().split())

        changed_words = orig_words.symmetric_difference(corr_words)
        total_words = len(orig_words)

        if total_words == 0:
            return 0.0

        # More changes = lower confidence
        change_ratio = len(changed_words) / total_words
        confidence = 1.0 - (change_ratio * 0.5)  # Max 50% penalty

        return max(0.0, min(1.0, confidence))


# Singleton instance
_corrector = None


def get_query_corrector() -> QueryCorrector:
    """Get singleton query corrector instance."""
    global _corrector
    if _corrector is None:
        _corrector = QueryCorrector()
    return _corrector
