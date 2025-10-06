"""
Entity Resolvers for OBCMS Chat System.

This module provides specialized resolvers for different entity types:
- LocationResolver: Fuzzy matching for geographic locations
- EthnicGroupResolver: Ethnolinguistic group variations
- LivelihoodResolver: Livelihood keyword mapping
- DateRangeResolver: Natural language date parsing
- StatusResolver: Workflow and task status recognition
- NumberResolver: Number extraction (cardinal, ordinal, written)

Each resolver returns entities with confidence scores (0.0-1.0).
"""

import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    from django.utils import timezone
    from django.db.models import Q
    HAS_DJANGO = True
except ImportError:
    # Fallback for testing without Django
    import pytz
    class timezone:
        @staticmethod
        def now():
            return datetime.now(pytz.UTC)
        @staticmethod
        def get_current_timezone():
            return pytz.UTC
    Q = None
    HAS_DJANGO = False


class LocationResolver:
    """
    Resolve location entities with fuzzy matching and database validation.

    Handles regions, provinces, municipalities, and barangays.
    Supports common variations and misspellings.
    """

    # Region patterns with variations
    REGION_PATTERNS = {
        'IX': {
            'names': ['region ix', 'region 9', 'zamboanga', 'zamboanga peninsula', 'r9', 'rix'],
            'official_name': 'Region IX',
            'code': 'IX',
        },
        'X': {
            'names': ['region x', 'region 10', 'northern mindanao', 'r10', 'rx'],
            'official_name': 'Region X',
            'code': 'X',
        },
        'XI': {
            'names': ['region xi', 'region 11', 'davao', 'davao region', 'r11', 'rxi'],
            'official_name': 'Region XI',
            'code': 'XI',
        },
        'XII': {
            'names': ['region xii', 'region 12', 'soccsksargen', 'socsksargen', 'r12', 'rxii'],
            'official_name': 'Region XII',
            'code': 'XII',
        },
    }

    # Common province name variations
    PROVINCE_VARIATIONS = {
        'sultan kudarat': ['sultan kudarat', 'sk', 's. kudarat', 'skudarat'],
        'maguindanao': ['maguindanao', 'maguindanao del norte', 'maguindanao del sur'],
        'south cotabato': ['south cotabato', 's cotabato', 'socot', 's. cotabato'],
        'sarangani': ['sarangani', 'saranggani'],
        'cotabato': ['cotabato', 'north cotabato', 'n cotabato'],
        'zamboanga del norte': ['zamboanga del norte', 'zdn', 'z del norte'],
        'zamboanga del sur': ['zamboanga del sur', 'zds', 'z del sur'],
        'zamboanga sibugay': ['zamboanga sibugay', 'sibugay'],
        'bukidnon': ['bukidnon', 'bukidnon province'],
        'misamis oriental': ['misamis oriental', 'mis or', 'misor'],
        'misamis occidental': ['misamis occidental', 'mis occ', 'misocc'],
        'lanao del norte': ['lanao del norte', 'ldn', 'l del norte'],
        'davao del norte': ['davao del norte', 'ddn', 'd del norte'],
        'davao del sur': ['davao del sur', 'dds', 'd del sur'],
        'davao oriental': ['davao oriental', 'dor', 'd oriental'],
        'davao de oro': ['davao de oro', 'compostela valley', 'comval'],
        'davao occidental': ['davao occidental', 'docc', 'd occidental'],
    }

    def __init__(self):
        """Initialize location resolver with cached data."""
        self._region_cache = None
        self._province_cache = None

    def resolve(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Resolve location entity from query.

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with location type, value, and confidence or None

        Example:
            >>> resolve("communities in zamboanga")
            {'type': 'region', 'value': 'Region IX', 'confidence': 0.85}
        """
        # Try region patterns first (highest priority)
        region = self._match_region(query)
        if region:
            return region

        # Try province patterns
        province = self._match_province(query)
        if province:
            return province

        # Try database lookup for municipalities
        municipality = self._match_municipality(query)
        if municipality:
            return municipality

        return None

    def _match_region(self, query: str) -> Optional[Dict[str, Any]]:
        """Match region from query using pattern matching."""
        for region_code, region_data in self.REGION_PATTERNS.items():
            for name_variant in region_data['names']:
                if name_variant in query:
                    # Calculate confidence based on match quality
                    confidence = 0.95 if name_variant.startswith('region') else 0.85

                    return {
                        'type': 'region',
                        'value': region_data['official_name'],
                        'code': region_data['code'],
                        'confidence': confidence,
                    }
        return None

    def _match_province(self, query: str) -> Optional[Dict[str, Any]]:
        """Match province from query using fuzzy matching."""
        for province_name, variations in self.PROVINCE_VARIATIONS.items():
            for variant in variations:
                if variant in query:
                    # Calculate confidence based on match length
                    confidence = min(0.92, 0.7 + (len(variant) / 20))

                    # Try to get actual province from database for validation
                    validated_name = self._validate_province_db(province_name)

                    return {
                        'type': 'province',
                        'value': validated_name or province_name.title(),
                        'confidence': confidence if validated_name else confidence * 0.9,
                    }
        return None

    def _match_municipality(self, query: str) -> Optional[Dict[str, Any]]:
        """Match municipality from query using database lookup."""
        if not HAS_DJANGO:
            return None

        try:
            from common.models import Municipality

            # Extract potential municipality names (2-3 word phrases)
            words = query.split()
            for i in range(len(words)):
                for length in [3, 2, 1]:  # Try 3-word, then 2-word, then 1-word
                    if i + length <= len(words):
                        phrase = ' '.join(words[i:i+length])

                        # Case-insensitive lookup
                        municipality = Municipality.objects.filter(
                            Q(name__iexact=phrase) | Q(name__icontains=phrase)
                        ).first()

                        if municipality:
                            confidence = 0.90 if municipality.name.lower() == phrase else 0.75
                            return {
                                'type': 'municipality',
                                'value': municipality.name,
                                'province': municipality.province.name,
                                'region': municipality.province.region.name,
                                'confidence': confidence,
                            }
        except Exception:
            # Database not available or model import failed
            pass

        return None

    def _validate_province_db(self, province_name: str) -> Optional[str]:
        """Validate and get official province name from database."""
        if not HAS_DJANGO:
            return None

        try:
            from common.models import Province

            province = Province.objects.filter(
                Q(name__iexact=province_name) | Q(name__icontains=province_name)
            ).first()

            if province:
                return province.name
        except Exception:
            pass

        return None


class EthnicGroupResolver:
    """
    Resolve ethnolinguistic group entities with variation handling.

    Handles common misspellings and alternative names for ethnic groups.
    """

    # Ethnolinguistic group variations (maps variations to official names)
    ETHNIC_GROUP_VARIATIONS = {
        'meranaw': ['maranao', 'marano', 'meranaw', 'meranaos', 'maranaos'],
        'maguindanaon': ['maguindanao', 'maguindanaon', 'magindanao', 'maguindanons'],
        'tausug': ['tausug', 'tausog', 'tausugs', 'tau sug'],
        'sama': ['sama', 'sama-bajau', 'sama bajau', 'bajau', 'badjao'],
        'badjao': ['badjao', 'badjaos', 'bajo', 'sama badjao'],
        'yakan': ['yakan', 'yakans', 'yaken'],
        'iranun': ['iranun', 'iranon', 'ilanun', 'iranuns'],
        'kagan_kalagan': ['kalagan', 'kagan', 'kagan kalagan', 'kaagan'],
        'kolibugan': ['kolibugan', 'kalibugan', 'kolibogan'],
        'sangil': ['sangil', 'sangir', 'sangils'],
        'molbog': ['molbog', 'mulbug', 'molbogs'],
        'jama_mapun': ['jama mapun', 'yakan', 'mapun'],
        'palawani': ['palawani', 'palawan', 'palawanos'],
    }

    def resolve(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Resolve ethnolinguistic group entity from query.

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with ethnic group value and confidence or None

        Example:
            >>> resolve("maranao communities")
            {'value': 'Meranaw', 'confidence': 0.95}
        """
        for official_name, variations in self.ETHNIC_GROUP_VARIATIONS.items():
            for variant in variations:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(variant) + r'\b'
                if re.search(pattern, query):
                    # Calculate confidence based on match quality
                    confidence = 0.95 if variant == official_name else 0.90

                    # Return official name (properly formatted)
                    display_name = official_name.replace('_', ' ').title()

                    return {
                        'value': display_name,
                        'confidence': confidence,
                    }

        return None


class LivelihoodResolver:
    """
    Resolve livelihood entities with keyword mapping.

    Maps various forms to standard livelihood categories.
    """

    # Livelihood keywords (maps keywords to standard livelihoods)
    LIVELIHOOD_KEYWORDS = {
        'farming': ['farming', 'farmer', 'farmers', 'agriculture', 'agricultural', 'crops', 'rice', 'corn', 'vegetables'],
        'fishing': ['fishing', 'fisher', 'fisherman', 'fishermen', 'fisherfolk', 'fish', 'aquaculture'],
        'trading': ['trading', 'trader', 'traders', 'merchant', 'merchants', 'business', 'sari-sari'],
        'weaving': ['weaving', 'weaver', 'weavers', 'textile', 'textiles', 'handloom'],
        'livestock': ['livestock', 'cattle', 'poultry', 'chicken', 'goat', 'carabao', 'animal husbandry'],
        'carpentry': ['carpentry', 'carpenter', 'carpenters', 'woodwork', 'woodworking'],
        'masonry': ['masonry', 'mason', 'masons', 'construction', 'builder'],
        'driving': ['driving', 'driver', 'drivers', 'tricycle', 'jeepney', 'transport'],
        'vending': ['vending', 'vendor', 'vendors', 'street vendor', 'market vendor'],
        'handicrafts': ['handicraft', 'handicrafts', 'artisan', 'artisans', 'crafts'],
    }

    def resolve(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Resolve livelihood entity from query.

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with livelihood value and confidence or None

        Example:
            >>> resolve("fishing communities")
            {'value': 'fishing', 'confidence': 0.90}
        """
        for livelihood, keywords in self.LIVELIHOOD_KEYWORDS.items():
            for keyword in keywords:
                # Use word boundaries for exact matches
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, query):
                    # Calculate confidence based on keyword specificity
                    confidence = 0.95 if keyword == livelihood else 0.90

                    return {
                        'value': livelihood,
                        'confidence': confidence,
                    }

        return None


class DateRangeResolver:
    """
    Resolve date range entities from natural language.

    Handles both relative ("last 30 days") and absolute ("2024", "jan to mar") dates.
    """

    def resolve(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Resolve date range entity from query.

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with start, end dates, and confidence or None

        Example:
            >>> resolve("last 6 months")
            {
                'start': datetime(2024, 4, 6),
                'end': datetime(2025, 10, 6),
                'confidence': 1.0,
                'range_type': 'relative'
            }
        """
        # Try relative date patterns first
        relative = self._parse_relative_date(query)
        if relative:
            return relative

        # Try absolute date patterns
        absolute = self._parse_absolute_date(query)
        if absolute:
            return absolute

        # Try year-only patterns
        year = self._parse_year(query)
        if year:
            return year

        return None

    def _parse_relative_date(self, query: str) -> Optional[Dict[str, Any]]:
        """Parse relative date ranges like 'last 30 days', 'last 6 months'."""
        now = timezone.now()

        # Last N days
        match = re.search(r'last (\d+) days?', query)
        if match:
            days = int(match.group(1))
            return {
                'start': now - timedelta(days=days),
                'end': now,
                'confidence': 1.0,
                'range_type': 'relative',
            }

        # Last N months
        match = re.search(r'last (\d+) months?', query)
        if match:
            months = int(match.group(1))
            start = now - timedelta(days=months * 30)  # Approximate
            return {
                'start': start,
                'end': now,
                'confidence': 1.0,
                'range_type': 'relative',
            }

        # Last N weeks
        match = re.search(r'last (\d+) weeks?', query)
        if match:
            weeks = int(match.group(1))
            return {
                'start': now - timedelta(weeks=weeks),
                'end': now,
                'confidence': 1.0,
                'range_type': 'relative',
            }

        # This year
        if 'this year' in query or 'current year' in query:
            return {
                'start': datetime(now.year, 1, 1, tzinfo=timezone.get_current_timezone()),
                'end': now,
                'confidence': 1.0,
                'range_type': 'relative',
            }

        # Last year
        if 'last year' in query:
            last_year = now.year - 1
            return {
                'start': datetime(last_year, 1, 1, tzinfo=timezone.get_current_timezone()),
                'end': datetime(last_year, 12, 31, 23, 59, 59, tzinfo=timezone.get_current_timezone()),
                'confidence': 1.0,
                'range_type': 'relative',
            }

        # Recent / latest (default to last 30 days)
        if any(word in query for word in ['recent', 'latest', 'current']):
            return {
                'start': now - timedelta(days=30),
                'end': now,
                'confidence': 0.85,
                'range_type': 'relative',
            }

        return None

    def _parse_absolute_date(self, query: str) -> Optional[Dict[str, Any]]:
        """Parse absolute date ranges like 'from jan to mar', 'january 2024'."""
        # Month name to number mapping
        months = {
            'jan': 1, 'january': 1,
            'feb': 2, 'february': 2,
            'mar': 3, 'march': 3,
            'apr': 4, 'april': 4,
            'may': 5,
            'jun': 6, 'june': 6,
            'jul': 7, 'july': 7,
            'aug': 8, 'august': 8,
            'sep': 9, 'sept': 9, 'september': 9,
            'oct': 10, 'october': 10,
            'nov': 11, 'november': 11,
            'dec': 12, 'december': 12,
        }

        now = timezone.now()
        current_year = now.year

        # Month range: "from jan to mar", "january to march"
        pattern = r'from (\w+) to (\w+)'
        match = re.search(pattern, query)
        if match:
            start_month_str = match.group(1).lower()
            end_month_str = match.group(2).lower()

            start_month = months.get(start_month_str)
            end_month = months.get(end_month_str)

            if start_month and end_month:
                start = datetime(current_year, start_month, 1, tzinfo=timezone.get_current_timezone())
                # Get last day of end month
                if end_month == 12:
                    end = datetime(current_year, 12, 31, 23, 59, 59, tzinfo=timezone.get_current_timezone())
                else:
                    end = datetime(current_year, end_month + 1, 1, tzinfo=timezone.get_current_timezone()) - timedelta(seconds=1)

                return {
                    'start': start,
                    'end': end,
                    'confidence': 0.95,
                    'range_type': 'absolute',
                }

        # Single month: "january 2024", "jan 2024"
        pattern = r'(\w+)\s+(\d{4})'
        match = re.search(pattern, query)
        if match:
            month_str = match.group(1).lower()
            year = int(match.group(2))

            month = months.get(month_str)
            if month:
                start = datetime(year, month, 1, tzinfo=timezone.get_current_timezone())
                # Get last day of month
                if month == 12:
                    end = datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.get_current_timezone())
                else:
                    end = datetime(year, month + 1, 1, tzinfo=timezone.get_current_timezone()) - timedelta(seconds=1)

                return {
                    'start': start,
                    'end': end,
                    'confidence': 0.95,
                    'range_type': 'absolute',
                }

        return None

    def _parse_year(self, query: str) -> Optional[Dict[str, Any]]:
        """Parse year-only patterns like '2024', 'in 2023'."""
        # Match 4-digit year
        match = re.search(r'\b(20\d{2})\b', query)
        if match:
            year = int(match.group(1))

            return {
                'start': datetime(year, 1, 1, tzinfo=timezone.get_current_timezone()),
                'end': datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.get_current_timezone()),
                'confidence': 0.90,
                'range_type': 'absolute',
            }

        return None


class StatusResolver:
    """
    Resolve status entities for workflows, tasks, and projects.

    Handles various status keywords and variations.
    """

    # Status keywords mapping
    STATUS_KEYWORDS = {
        'ongoing': ['ongoing', 'in progress', 'active', 'in-progress', 'running'],
        'completed': ['completed', 'done', 'finished', 'complete', 'closed'],
        'draft': ['draft', 'drafts', 'drafted'],
        'pending': ['pending', 'waiting', 'awaiting'],
        'approved': ['approved', 'accepted', 'confirmed'],
        'rejected': ['rejected', 'declined', 'denied'],
        'cancelled': ['cancelled', 'canceled', 'cancelled'],
        'suspended': ['suspended', 'paused', 'on hold'],
        'planned': ['planned', 'scheduled', 'upcoming'],
    }

    def resolve(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Resolve status entity from query.

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with status value and confidence or None

        Example:
            >>> resolve("ongoing projects")
            {'value': 'ongoing', 'confidence': 0.95}
        """
        for status, keywords in self.STATUS_KEYWORDS.items():
            for keyword in keywords:
                # Use word boundaries for exact matches
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, query):
                    # Calculate confidence based on keyword specificity
                    confidence = 0.95 if keyword == status else 0.90

                    return {
                        'value': status,
                        'confidence': confidence,
                    }

        return None


class NumberResolver:
    """
    Resolve number entities (cardinal, ordinal, written).

    Extracts numbers from queries for use in "top N", "first N", etc.
    """

    # Written numbers mapping
    WRITTEN_NUMBERS = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
        'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20,
        'twenty-five': 25, 'thirty': 30, 'forty': 40, 'fifty': 50,
        'hundred': 100, 'thousand': 1000,
    }

    # Ordinal patterns
    ORDINAL_PATTERNS = {
        'first': 1, '1st': 1,
        'second': 2, '2nd': 2,
        'third': 3, '3rd': 3,
        'fourth': 4, '4th': 4,
        'fifth': 5, '5th': 5,
        'sixth': 6, '6th': 6,
        'seventh': 7, '7th': 7,
        'eighth': 8, '8th': 8,
        'ninth': 9, '9th': 9,
        'tenth': 10, '10th': 10,
    }

    def resolve(self, query: str) -> List[Dict[str, Any]]:
        """
        Resolve number entities from query.

        Args:
            query: Normalized query string (lowercase)

        Returns:
            List of dictionaries with number value, type, and confidence

        Example:
            >>> resolve("top 5 communities")
            [{'value': 5, 'type': 'cardinal', 'confidence': 1.0}]
        """
        numbers = []

        # Extract cardinal numbers (digits)
        cardinal_matches = re.finditer(r'\b(\d+)\b', query)
        for match in cardinal_matches:
            numbers.append({
                'value': int(match.group(1)),
                'type': 'cardinal',
                'confidence': 1.0,
            })

        # Extract written numbers
        for word, value in self.WRITTEN_NUMBERS.items():
            pattern = r'\b' + re.escape(word) + r'\b'
            if re.search(pattern, query):
                numbers.append({
                    'value': value,
                    'type': 'cardinal',
                    'confidence': 0.95,
                })

        # Extract ordinal numbers
        for word, value in self.ORDINAL_PATTERNS.items():
            pattern = r'\b' + re.escape(word) + r'\b'
            if re.search(pattern, query):
                numbers.append({
                    'value': value,
                    'type': 'ordinal',
                    'confidence': 0.95,
                })

        # Remove duplicates (keep highest confidence)
        unique_numbers = {}
        for num in numbers:
            value = num['value']
            if value not in unique_numbers or num['confidence'] > unique_numbers[value]['confidence']:
                unique_numbers[value] = num

        return list(unique_numbers.values())


class SectorResolver:
    """
    Resolve development sector entities from needs queries.

    Handles sector names from NeedsCategory model:
    - education, economic_development, social_development, cultural_development
    - infrastructure, health, governance, environment, security (peace and security)
    """

    # Development sector mapping
    SECTOR_PATTERNS = {
        'education': ['education', 'educational', 'school', 'learning', 'training'],
        'economic_development': ['economic', 'economy', 'livelihood', 'business', 'enterprise'],
        'social_development': ['social', 'community development', 'social welfare'],
        'cultural_development': ['cultural', 'culture', 'heritage', 'tradition'],
        'infrastructure': ['infrastructure', 'roads', 'bridges', 'facilities', 'buildings'],
        'health': ['health', 'medical', 'healthcare', 'clinic', 'hospital', 'wellness'],
        'governance': ['governance', 'government', 'administration', 'leadership'],
        'environment': ['environment', 'environmental', 'ecology', 'nature', 'conservation'],
        'security': ['security', 'peace', 'safety', 'protection', 'conflict'],
    }

    def resolve(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Resolve sector entity from query.

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with sector value and confidence score
            or None if no sector found

        Example:
            >>> resolve("infrastructure needs")
            {'value': 'infrastructure', 'confidence': 0.95}
        """
        for sector, patterns in self.SECTOR_PATTERNS.items():
            for pattern in patterns:
                if re.search(r'\b' + re.escape(pattern) + r'\b', query):
                    # Direct match in query
                    return {
                        'value': sector,
                        'confidence': 0.95 if pattern == sector else 0.90
                    }

        return None


class PriorityLevelResolver:
    """
    Resolve priority level entities from needs queries.

    Maps common priority terms to Need model urgency_levels:
    - critical/immediate → "immediate"
    - high/urgent → "short_term"
    - medium → "medium_term"
    - low → "long_term"
    """

    # Priority level mapping
    PRIORITY_PATTERNS = {
        'immediate': ['critical', 'immediate', 'urgent', 'emergency', 'asap'],
        'short_term': ['high', 'high priority', 'important', 'pressing'],
        'medium_term': ['medium', 'moderate', 'normal'],
        'long_term': ['low', 'low priority', 'future', 'long-term'],
    }

    def resolve(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Resolve priority level entity from query.

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with urgency_level value and confidence score
            or None if no priority found

        Example:
            >>> resolve("critical needs")
            {'value': 'immediate', 'urgency_level': 'immediate', 'confidence': 0.95}
        """
        for urgency_level, patterns in self.PRIORITY_PATTERNS.items():
            for pattern in patterns:
                if re.search(r'\b' + re.escape(pattern) + r'\b', query):
                    return {
                        'value': urgency_level,
                        'urgency_level': urgency_level,
                        'confidence': 0.95
                    }

        return None


class UrgencyLevelResolver:
    """
    Resolve urgency level entities from needs queries.

    Direct mapping to Need model urgency_level choices:
    - immediate (Within 1 month)
    - short_term (1-6 months)
    - medium_term (6-12 months)
    - long_term (1+ years)
    """

    # Urgency level patterns (explicit)
    URGENCY_PATTERNS = {
        'immediate': ['immediate', 'within 1 month', 'within a month', 'asap', 'right now'],
        'short_term': ['short term', 'short-term', '1-6 months', 'few months'],
        'medium_term': ['medium term', 'medium-term', '6-12 months', 'this year'],
        'long_term': ['long term', 'long-term', 'over a year', '1+ years', 'future'],
    }

    def resolve(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Resolve urgency level entity from query.

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with urgency_level value and confidence score
            or None if no urgency found

        Example:
            >>> resolve("immediate needs")
            {'value': 'immediate', 'confidence': 1.0}
        """
        for urgency_level, patterns in self.URGENCY_PATTERNS.items():
            for pattern in patterns:
                if re.search(r'\b' + re.escape(pattern) + r'\b', query):
                    return {
                        'value': urgency_level,
                        'confidence': 1.0
                    }

        return None


class NeedStatusResolver:
    """
    Resolve need status entities from queries.

    Maps common status terms to Need model status choices:
    - unmet/unfulfilled → "identified"
    - met/fulfilled → "completed"
    - partially_met/ongoing → "in_progress"
    - planned → "planned"
    - validated → "validated"
    - prioritized → "prioritized"
    - deferred → "deferred"
    - rejected → "rejected"
    """

    # Need status mapping
    STATUS_PATTERNS = {
        'identified': ['identified', 'unmet', 'unfulfilled', 'unaddressed', 'pending'],
        'validated': ['validated', 'verified', 'confirmed'],
        'prioritized': ['prioritized', 'ranked'],
        'planned': ['planned', 'scheduled', 'programmed'],
        'in_progress': ['in progress', 'ongoing', 'active', 'implementing', 'partially met'],
        'completed': ['completed', 'met', 'fulfilled', 'addressed', 'finished', 'done'],
        'deferred': ['deferred', 'postponed', 'delayed'],
        'rejected': ['rejected', 'declined', 'cancelled'],
    }

    def resolve(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Resolve need status entity from query.

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with status value and confidence score
            or None if no status found

        Example:
            >>> resolve("unmet needs")
            {'value': 'identified', 'confidence': 0.95}
        """
        for status, patterns in self.STATUS_PATTERNS.items():
            for pattern in patterns:
                if re.search(r'\b' + re.escape(pattern) + r'\b', query):
                    return {
                        'value': status,
                        'confidence': 0.95
                    }

        return None


class MinistryResolver:
    """
    Resolve ministry/MOA entities from queries.

    Maps ministry names and variations to standard MOA codes.
    """

    # Ministry patterns mapping
    MINISTRY_PATTERNS = {
        'MILG': ['milg', 'local government', 'ministry of local government'],
        'MSSD': ['mssd', 'social services', 'social development', 'ministry of social services'],
        'MHPW': ['mhpw', 'health', 'public works', 'ministry of health'],
        'MBDA': ['mbda', 'basic education', 'ministry of basic education'],
        'MHEA': ['mhea', 'higher education', 'ministry of higher education'],
        'MOJ': ['moj', 'justice', 'ministry of justice'],
        'MOI': ['moi', 'interior', 'ministry of interior'],
        'MTIT': ['mtit', 'transportation', 'ministry of transportation'],
        'MENR': ['menr', 'environment', 'natural resources', 'ministry of environment'],
        'MAFAR': ['mafar', 'agriculture', 'fisheries', 'ministry of agriculture'],
        'MTRADEIN': ['mtradein', 'trade', 'investment', 'ministry of trade'],
        'MLGD': ['mlgd', 'labor', 'employment', 'ministry of labor'],
    }

    def resolve(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Resolve ministry entity from query.

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with ministry code and confidence score
            or None if no ministry found

        Example:
            >>> resolve("MILG projects")
            {'value': 'MILG', 'confidence': 0.95}
        """
        for ministry_code, patterns in self.MINISTRY_PATTERNS.items():
            for pattern in patterns:
                if re.search(r'\b' + re.escape(pattern) + r'\b', query, re.IGNORECASE):
                    confidence = 0.95 if pattern == ministry_code.lower() else 0.90
                    return {
                        'value': ministry_code,
                        'confidence': confidence
                    }

        return None


class BudgetRangeResolver:
    """
    Resolve budget range entities from queries.

    Handles budget amounts and ranges with various formats.
    """

    def resolve(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Resolve budget range entity from query.

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with budget range (min, max) and confidence score
            or None if no budget range found

        Example:
            >>> resolve("projects under 1M")
            {'min': 0, 'max': 1000000, 'confidence': 0.95}
        """
        # Pattern: "under X million/M" - allow optional space before M
        match = re.search(r'under (\d+(?:\.\d+)?)\s*(?:million|m(?!\w))', query, re.IGNORECASE)
        if match:
            amount = float(match.group(1)) * 1_000_000
            return {
                'min': 0,
                'max': int(amount),
                'confidence': 0.95
            }

        # Pattern: "over X million/M" - allow optional space before M
        match = re.search(r'over (\d+(?:\.\d+)?)\s*(?:million|m(?!\w))', query, re.IGNORECASE)
        if match:
            amount = float(match.group(1)) * 1_000_000
            return {
                'min': int(amount),
                'max': None,
                'confidence': 0.95
            }

        # Pattern: "between X and Y million/M"
        match = re.search(r'between (\d+(?:\.\d+)?)\s*(?:and|to)\s*(\d+(?:\.\d+)?)\s*(?:million|m(?!\w))', query, re.IGNORECASE)
        if match:
            min_amount = float(match.group(1)) * 1_000_000
            max_amount = float(match.group(2)) * 1_000_000
            return {
                'min': int(min_amount),
                'max': int(max_amount),
                'confidence': 0.95
            }

        # Pattern: "X million budget"
        match = re.search(r'(\d+(?:\.\d+)?)\s*(?:million|m(?!\w))\s+budget', query, re.IGNORECASE)
        if match:
            amount = float(match.group(1)) * 1_000_000
            return {
                'min': int(amount * 0.9),  # 10% tolerance
                'max': int(amount * 1.1),
                'confidence': 0.90
            }

        return None


class AssessmentTypeResolver:
    """
    Resolve assessment type entities from queries.

    Maps assessment type keywords to standard types.
    """

    # Assessment type patterns
    ASSESSMENT_PATTERNS = {
        'rapid': ['rapid', 'quick', 'fast', 'emergency'],
        'comprehensive': ['comprehensive', 'detailed', 'thorough', 'full', 'complete'],
        'baseline': ['baseline', 'initial', 'starting', 'benchmark'],
        'thematic': ['thematic', 'sectoral', 'sector-specific', 'focused'],
        'needs_assessment': ['needs assessment', 'na', 'mana'],
        'impact': ['impact', 'outcome', 'effect', 'result'],
        'monitoring': ['monitoring', 'progress', 'tracking'],
    }

    def resolve(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Resolve assessment type entity from query.

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with assessment type and confidence score
            or None if no assessment type found

        Example:
            >>> resolve("rapid assessment")
            {'value': 'rapid', 'confidence': 0.95}
        """
        for assessment_type, patterns in self.ASSESSMENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(r'\b' + re.escape(pattern) + r'\b', query, re.IGNORECASE):
                    confidence = 0.95 if pattern == assessment_type else 0.90
                    return {
                        'value': assessment_type,
                        'confidence': confidence
                    }

        return None


class PartnershipTypeResolver:
    """
    Resolve partnership type entities from queries.

    Maps partnership keywords to standard types.
    """

    # Partnership type patterns
    PARTNERSHIP_PATTERNS = {
        'MOA': ['moa', 'memorandum of agreement', 'agreement'],
        'MOU': ['mou', 'memorandum of understanding', 'understanding'],
        'collaboration': ['collaboration', 'collaborative', 'partnership', 'joint'],
        'joint_program': ['joint program', 'joint project', 'joint initiative'],
        'technical_assistance': ['technical assistance', 'ta', 'technical support'],
        'capacity_building': ['capacity building', 'training', 'capability development'],
        'coordination': ['coordination', 'coordinated', 'multi-stakeholder'],
    }

    def resolve(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Resolve partnership type entity from query.

        Args:
            query: Normalized query string (lowercase)

        Returns:
            Dictionary with partnership type and confidence score
            or None if no partnership type found

        Example:
            >>> resolve("MOA with DSWD")
            {'value': 'MOA', 'confidence': 0.95}
        """
        for partnership_type, patterns in self.PARTNERSHIP_PATTERNS.items():
            for pattern in patterns:
                if re.search(r'\b' + re.escape(pattern) + r'\b', query, re.IGNORECASE):
                    confidence = 0.95 if pattern == partnership_type.lower() else 0.90
                    return {
                        'value': partnership_type,
                        'confidence': confidence
                    }

        return None
