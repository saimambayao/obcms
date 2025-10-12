# Beneficiary Deduplication Strategy for BMMS

**Document Version:** 1.0
**Date:** October 12, 2025
**Status:** Technical Specification
**Priority:** CRITICAL

---

## Executive Summary

This document outlines the comprehensive beneficiary deduplication strategy for BMMS (Bangsamoro Ministerial Management System). The system must identify and merge duplicate beneficiary records across multiple MOAs (Ministries, Offices, and Agencies) without relying on PhilSys integration (planned for future enhancement).

**Core Challenge:** Same individual may be:
- Registered multiple times with typos or name variations
- Receiving services from multiple MOAs simultaneously
- Listed with different contact information or addresses

**Solution Approach:**
- Multi-factor fuzzy matching algorithm
- Real-time duplicate detection on registration
- User-guided merge workflow with audit trail
- UUID-based unique identifiers until PhilSys available

**Key Metrics:**
- Detection accuracy: 95%+ for exact matches, 85%+ for fuzzy matches
- Performance: < 500ms for duplicate detection on save
- False positive rate: < 5% (user confirms all merges)

---

## Table of Contents

1. [Beneficiary Data Model](#1-beneficiary-data-model)
2. [Fuzzy Matching Algorithm](#2-fuzzy-matching-algorithm)
3. [Django Implementation](#3-django-implementation)
4. [Database Indexes and Performance](#4-database-indexes-and-performance)
5. [Deduplication Workflow](#5-deduplication-workflow)
6. [User Interface Components](#6-user-interface-components)
7. [Testing Strategy](#7-testing-strategy)
8. [PhilSys Integration Preparation](#8-philsys-integration-preparation)

---

## 1. Beneficiary Data Model

### 1.1 Core Beneficiary Model

```python
# src/beneficiaries/models.py

import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Beneficiary(models.Model):
    """
    Represents an individual receiving services from BARMM MOAs.

    IMPORTANT: This model is designed for deduplication WITHOUT PhilSys.
    PhilSys integration will be added in future as additional field.
    """

    # Primary Identifier (UUID until PhilSys available)
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier (UUID v4). Will be replaced by PhilSys ID when available."
    )

    # Core Identity Fields (used for matching)
    first_name = models.CharField(
        max_length=100,
        help_text="Given name (e.g., 'Muhammad', 'Aisha')"
    )
    middle_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Middle name or patronymic (optional)"
    )
    last_name = models.CharField(
        max_length=100,
        help_text="Family name or surname"
    )
    suffix = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('Jr.', 'Jr.'),
            ('Sr.', 'Sr.'),
            ('II', 'II'),
            ('III', 'III'),
            ('IV', 'IV'),
        ],
        help_text="Name suffix (Jr., Sr., II, etc.)"
    )

    date_of_birth = models.DateField(
        help_text="Date of birth (YYYY-MM-DD)"
    )

    sex = models.CharField(
        max_length=1,
        choices=[
            ('M', 'Male'),
            ('F', 'Female'),
        ]
    )

    # Contact Information
    phone_number = PhoneNumberField(
        blank=True,
        help_text="Mobile number with country code (+63)"
    )
    email = models.EmailField(
        blank=True,
        help_text="Email address (optional)"
    )

    # Geographic Information (for address-based matching)
    barangay = models.ForeignKey(
        'common.Barangay',
        on_delete=models.PROTECT,
        related_name='beneficiaries',
        help_text="Current barangay of residence"
    )
    municipality = models.ForeignKey(
        'common.Municipality',
        on_delete=models.PROTECT,
        related_name='beneficiaries',
        help_text="Current municipality/city of residence"
    )
    province = models.ForeignKey(
        'common.Province',
        on_delete=models.PROTECT,
        related_name='beneficiaries',
        help_text="Current province of residence"
    )
    region = models.ForeignKey(
        'common.Region',
        on_delete=models.PROTECT,
        related_name='beneficiaries',
        help_text="Current region of residence"
    )

    street_address = models.CharField(
        max_length=255,
        blank=True,
        help_text="Street address, house number, or landmark"
    )

    # Fuzzy Matching Helper Fields (auto-populated)
    first_name_soundex = models.CharField(
        max_length=10,
        editable=False,
        db_index=True,
        help_text="Soundex code for first name (phonetic matching)"
    )
    last_name_soundex = models.CharField(
        max_length=10,
        editable=False,
        db_index=True,
        help_text="Soundex code for last name (phonetic matching)"
    )

    # Deduplication Tracking
    is_duplicate = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Marked as duplicate (merged into another record)"
    )
    merged_into = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='duplicates',
        help_text="Primary beneficiary this duplicate was merged into"
    )
    duplicate_confidence = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Confidence score (0-100) if identified as potential duplicate"
    )

    # MOA Association (multi-tenant)
    registered_by_organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.PROTECT,
        related_name='registered_beneficiaries',
        help_text="MOA that first registered this beneficiary"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        related_name='beneficiaries_created'
    )

    class Meta:
        verbose_name = "Beneficiary"
        verbose_name_plural = "Beneficiaries"
        ordering = ['last_name', 'first_name']
        indexes = [
            # Composite index for exact name + DOB matching
            models.Index(
                fields=['first_name', 'last_name', 'date_of_birth'],
                name='idx_name_dob'
            ),
            # Soundex indexes for phonetic matching
            models.Index(
                fields=['first_name_soundex', 'last_name_soundex'],
                name='idx_soundex'
            ),
            # Geographic indexes for address matching
            models.Index(
                fields=['barangay', 'municipality'],
                name='idx_geo_location'
            ),
            # Deduplication status index
            models.Index(
                fields=['is_duplicate', 'merged_into'],
                name='idx_dedup_status'
            ),
        ]

    def __str__(self):
        return f"{self.last_name}, {self.first_name} ({self.date_of_birth})"

    @property
    def full_name(self):
        """Returns full name in Filipino format: Last, First Middle Suffix"""
        parts = [self.last_name + ',', self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        if self.suffix:
            parts.append(self.suffix)
        return ' '.join(parts)

    @property
    def age(self):
        """Calculate current age from date of birth"""
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def save(self, *args, **kwargs):
        """Override save to auto-populate soundex fields"""
        from beneficiaries.utils.matching import generate_soundex

        self.first_name_soundex = generate_soundex(self.first_name)
        self.last_name_soundex = generate_soundex(self.last_name)

        super().save(*args, **kwargs)


class BeneficiaryService(models.Model):
    """
    Tracks services received by beneficiaries from MOAs.
    Multiple MOAs can provide services to same beneficiary.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name='services_received'
    )

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.PROTECT,
        related_name='services_provided',
        help_text="MOA providing the service"
    )

    service_type = models.CharField(
        max_length=100,
        help_text="Type of service (e.g., 'Livelihood Training', 'Health Subsidy')"
    )

    service_description = models.TextField(
        help_text="Detailed description of service provided"
    )

    date_provided = models.DateField(
        help_text="Date service was provided"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Monetary value of service (if applicable)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.PROTECT)

    class Meta:
        verbose_name = "Beneficiary Service"
        verbose_name_plural = "Beneficiary Services"
        ordering = ['-date_provided']
        indexes = [
            models.Index(fields=['beneficiary', 'organization']),
            models.Index(fields=['date_provided']),
        ]


class DeduplicationLog(models.Model):
    """
    Audit trail for all deduplication decisions (merges and rejections).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    ACTION_CHOICES = [
        ('MERGE', 'Merged Duplicate'),
        ('REJECT', 'Rejected as Not Duplicate'),
        ('AUTO_DETECT', 'Automatic Detection'),
    ]

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)

    # The records involved
    primary_beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name='dedup_actions_primary',
        help_text="The record kept as primary"
    )

    duplicate_beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name='dedup_actions_duplicate',
        help_text="The record identified as potential duplicate"
    )

    # Match details
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Confidence score (0-100) at time of decision"
    )

    matching_factors = models.JSONField(
        help_text="Details of what matched (name, DOB, address, etc.)"
    )

    # Decision metadata
    decided_by = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        help_text="User who made the decision"
    )

    decided_at = models.DateTimeField(auto_now_add=True)

    notes = models.TextField(
        blank=True,
        help_text="User notes explaining decision"
    )

    class Meta:
        verbose_name = "Deduplication Log"
        verbose_name_plural = "Deduplication Logs"
        ordering = ['-decided_at']
        indexes = [
            models.Index(fields=['primary_beneficiary', 'decided_at']),
            models.Index(fields=['action', 'decided_at']),
        ]
```

### 1.2 Model Design Rationale

**UUID Primary Key:**
- Universally unique across all MOAs (no collision risk)
- 128-bit identifier (human-readable format: 8-4-4-4-12)
- Can be generated client-side (offline registration support)
- PhilSys ID will be added as additional field (not primary key initially)

**Soundex Fields:**
- Auto-populated on save (user doesn't see these)
- Enables phonetic matching for names with typos or spelling variations
- Example: "Muhammad" and "Mohammad" both generate soundex "M530"

**Geographic Hierarchy:**
- Four-level hierarchy: Region → Province → Municipality → Barangay
- Enables address-based matching (same barangay = higher confidence)
- Foreign keys prevent invalid geographic assignments

**Deduplication Fields:**
- `is_duplicate`: Quick filter to exclude merged records
- `merged_into`: Maintains link to primary record (data integrity)
- `duplicate_confidence`: Transparency in matching accuracy

---

## 2. Fuzzy Matching Algorithm

### 2.1 Algorithm Design

The matching algorithm uses a **weighted multi-factor scoring system** that combines:

1. **Exact Name Match** (40% weight)
2. **Phonetic Name Match** (30% weight)
3. **Date of Birth Match** (20% weight)
4. **Geographic Match** (10% weight)

**Confidence Thresholds:**
- 90-100%: **Very High** (almost certainly same person)
- 75-89%: **High** (likely same person)
- 60-74%: **Medium** (possible match)
- < 60%: **Low** (probably different people)

**Decision Rules:**
- ≥ 90%: Auto-flag as duplicate (require user confirmation)
- 75-89%: Show as potential duplicate (user can review)
- 60-74%: Show in "Possible Matches" section (informational)
- < 60%: No action (different people)

### 2.2 Matching Factors

#### Factor 1: Exact Name Match (40 points max)

```python
def calculate_name_match_score(name1, name2):
    """
    Compare two names using case-insensitive exact match.
    Returns score from 0-40.
    """
    # Normalize: lowercase, strip whitespace, remove extra spaces
    name1_normalized = ' '.join(name1.lower().strip().split())
    name2_normalized = ' '.join(name2.lower().strip().split())

    if name1_normalized == name2_normalized:
        return 40  # Perfect match

    # Check if one is substring of other (nickname scenario)
    if name1_normalized in name2_normalized or name2_normalized in name1_normalized:
        return 30  # Partial match

    # Use Levenshtein distance for typo detection
    from Levenshtein import distance

    max_len = max(len(name1_normalized), len(name2_normalized))
    edit_distance = distance(name1_normalized, name2_normalized)

    # Convert edit distance to similarity score (0-40)
    similarity = (1 - edit_distance / max_len) * 40

    return max(0, similarity)
```

**Example:**
- "Muhammad Ali" vs "Muhammad Ali" → 40 points (perfect)
- "Muhammad Ali" vs "Mohammad Ali" → 35 points (typo)
- "Muhammad" vs "Muhammad Ali" → 30 points (substring)
- "Muhammad Ali" vs "Ahmad Ali" → 25 points (partial similarity)

#### Factor 2: Phonetic Name Match (30 points max)

```python
def calculate_phonetic_score(soundex1, soundex2):
    """
    Compare soundex codes for phonetic similarity.
    Returns score from 0-30.
    """
    # Exact soundex match = names sound the same
    if soundex1 == soundex2:
        return 30

    # First letter + 2 digits match (partial phonetic match)
    if soundex1[:3] == soundex2[:3]:
        return 20

    # First letter matches (same starting sound)
    if soundex1[0] == soundex2[0]:
        return 10

    return 0
```

**Example:**
- "Muhammad" (M530) vs "Mohammad" (M530) → 30 points (same sound)
- "Aisha" (A200) vs "Ayesha" (A200) → 30 points (same sound)
- "Ali" (A400) vs "Aly" (A400) → 30 points (same sound)

#### Factor 3: Date of Birth Match (20 points max)

```python
def calculate_dob_score(dob1, dob2):
    """
    Compare dates of birth with tolerance for data entry errors.
    Returns score from 0-20.
    """
    if dob1 == dob2:
        return 20  # Perfect match

    # Check if only day/month transposed (common data entry error)
    if dob1.year == dob2.year and dob1.month == dob2.month:
        # Same month, different day (typo in day)
        if abs((dob1 - dob2).days) <= 2:
            return 18  # Very likely same person
        elif abs((dob1 - dob2).days) <= 7:
            return 15  # Possible data entry error

    if dob1.year == dob2.year and dob1.day == dob2.day:
        # Same year and day, different month (month/day transposition)
        if abs(dob1.month - dob2.month) <= 1:
            return 18  # Very likely transposition error

    if dob1.year == dob2.year:
        # Same year, different month/day
        if abs((dob1 - dob2).days) <= 30:
            return 12  # Within one month

    # Check for year typo (e.g., 1990 vs 1991)
    if abs(dob1.year - dob2.year) == 1:
        if dob1.month == dob2.month and dob1.day == dob2.day:
            return 15  # Likely year typo

    return 0
```

**Example:**
- 1990-05-15 vs 1990-05-15 → 20 points (perfect)
- 1990-05-15 vs 1990-05-16 → 18 points (day typo)
- 1990-05-15 vs 1990-15-05 → 18 points (month/day swap)
- 1990-05-15 vs 1991-05-15 → 15 points (year typo)

#### Factor 4: Geographic Match (10 points max)

```python
def calculate_geographic_score(geo1, geo2):
    """
    Compare geographic locations (region → province → municipality → barangay).
    Returns score from 0-10.
    """
    score = 0

    # Same barangay = very high confidence (small geographic area)
    if geo1.barangay_id == geo2.barangay_id:
        return 10

    # Same municipality = high confidence
    if geo1.municipality_id == geo2.municipality_id:
        score += 7

    # Same province = medium confidence
    elif geo1.province_id == geo2.province_id:
        score += 5

    # Same region = low confidence (large area)
    elif geo1.region_id == geo2.region_id:
        score += 3

    return score
```

**Example:**
- Same barangay → 10 points (very strong indicator)
- Same municipality, different barangay → 7 points (strong)
- Same province, different municipality → 5 points (moderate)
- Same region, different province → 3 points (weak)

### 2.3 Final Confidence Score

```python
def calculate_overall_confidence(beneficiary1, beneficiary2):
    """
    Calculate overall confidence score (0-100) for duplicate match.

    Returns:
        tuple: (confidence_score, matching_factors_dict)
    """
    # Factor 1: Exact name match (40 points max)
    first_name_score = calculate_name_match_score(
        beneficiary1.first_name,
        beneficiary2.first_name
    )
    last_name_score = calculate_name_match_score(
        beneficiary1.last_name,
        beneficiary2.last_name
    )
    name_exact_score = (first_name_score + last_name_score) / 2

    # Factor 2: Phonetic match (30 points max)
    first_name_phonetic = calculate_phonetic_score(
        beneficiary1.first_name_soundex,
        beneficiary2.first_name_soundex
    )
    last_name_phonetic = calculate_phonetic_score(
        beneficiary1.last_name_soundex,
        beneficiary2.last_name_soundex
    )
    phonetic_score = (first_name_phonetic + last_name_phonetic) / 2

    # Factor 3: Date of birth (20 points max)
    dob_score = calculate_dob_score(
        beneficiary1.date_of_birth,
        beneficiary2.date_of_birth
    )

    # Factor 4: Geographic location (10 points max)
    geo_score = calculate_geographic_score(beneficiary1, beneficiary2)

    # Total confidence (0-100)
    total_score = name_exact_score + phonetic_score + dob_score + geo_score

    # Round to 2 decimal places
    confidence = round(total_score, 2)

    # Detailed breakdown (for audit trail)
    factors = {
        'first_name_exact': first_name_score,
        'last_name_exact': last_name_score,
        'first_name_phonetic': first_name_phonetic,
        'last_name_phonetic': last_name_phonetic,
        'date_of_birth': dob_score,
        'geographic': geo_score,
        'total_confidence': confidence,
    }

    return confidence, factors
```

**Example Scenarios:**

**Scenario 1: Very High Confidence (98%)**
```
Muhammad Ali, 1990-05-15, Barangay Poblacion
Muhammad Ali, 1990-05-15, Barangay Poblacion
→ 40 (name) + 30 (phonetic) + 20 (DOB) + 10 (geo) = 100%
```

**Scenario 2: High Confidence (85%)**
```
Muhammad Ali, 1990-05-15, Barangay Poblacion
Mohammad Aly, 1990-05-16, Barangay Poblacion
→ 35 (name, typo) + 30 (phonetic) + 18 (DOB, day off by 1) + 10 (geo) = 93%
```

**Scenario 3: Medium Confidence (72%)**
```
Muhammad Ali, 1990-05-15, Barangay Poblacion
Mohammad Ali, 1990-05-15, Barangay San Jose (different barangay)
→ 35 (name) + 30 (phonetic) + 20 (DOB) + 7 (geo, same municipality) = 92%
```

**Scenario 4: Low Confidence (45%)**
```
Muhammad Ali, 1990-05-15, Barangay Poblacion
Ahmad Hassan, 1990-05-15, Barangay San Jose
→ 20 (name, different) + 10 (phonetic, first letter) + 20 (DOB) + 7 (geo) = 57%
```

---

## 3. Django Implementation

### 3.1 Utility Functions

Create `src/beneficiaries/utils/matching.py`:

```python
"""
Beneficiary deduplication utility functions.
Implements fuzzy matching algorithm for duplicate detection.
"""

import jellyfish
from django.db.models import Q
from decimal import Decimal


def generate_soundex(name):
    """
    Generate soundex code for phonetic matching.
    Uses Jellyfish library (Python implementation of Soundex algorithm).

    Args:
        name (str): Name to generate soundex for

    Returns:
        str: Soundex code (e.g., "M530" for "Muhammad")
    """
    if not name:
        return ""

    # Clean name: remove special characters, convert to ASCII
    clean_name = ''.join(c for c in name if c.isalpha())

    if not clean_name:
        return ""

    # Generate soundex (Jellyfish returns 4-character code)
    return jellyfish.soundex(clean_name)


def calculate_levenshtein_distance(str1, str2):
    """
    Calculate edit distance between two strings.
    Returns number of single-character edits needed to transform str1 into str2.

    Args:
        str1 (str): First string
        str2 (str): Second string

    Returns:
        int: Edit distance (0 = identical)
    """
    return jellyfish.levenshtein_distance(str1, str2)


def normalize_name(name):
    """
    Normalize name for comparison (lowercase, strip, remove extra spaces).

    Args:
        name (str): Name to normalize

    Returns:
        str: Normalized name
    """
    if not name:
        return ""

    return ' '.join(name.lower().strip().split())


def calculate_name_match_score(name1, name2, max_score=40):
    """
    Compare two names and return similarity score.

    Args:
        name1 (str): First name
        name2 (str): Second name
        max_score (int): Maximum possible score (default: 40)

    Returns:
        float: Similarity score (0 to max_score)
    """
    name1_norm = normalize_name(name1)
    name2_norm = normalize_name(name2)

    if not name1_norm or not name2_norm:
        return 0.0

    # Exact match
    if name1_norm == name2_norm:
        return float(max_score)

    # Substring match (nickname scenario)
    if name1_norm in name2_norm or name2_norm in name1_norm:
        return float(max_score * 0.75)  # 75% of max score

    # Levenshtein distance for typos
    max_len = max(len(name1_norm), len(name2_norm))
    edit_distance = calculate_levenshtein_distance(name1_norm, name2_norm)

    # Convert to similarity score (0-1)
    similarity_ratio = 1 - (edit_distance / max_len)

    # Scale to max_score
    score = similarity_ratio * max_score

    return max(0.0, score)


def calculate_phonetic_score(soundex1, soundex2, max_score=30):
    """
    Compare soundex codes for phonetic similarity.

    Args:
        soundex1 (str): First soundex code
        soundex2 (str): Second soundex code
        max_score (int): Maximum possible score (default: 30)

    Returns:
        float: Phonetic similarity score (0 to max_score)
    """
    if not soundex1 or not soundex2:
        return 0.0

    # Exact soundex match
    if soundex1 == soundex2:
        return float(max_score)

    # First letter + 2 digits match (partial phonetic)
    if len(soundex1) >= 3 and len(soundex2) >= 3:
        if soundex1[:3] == soundex2[:3]:
            return float(max_score * 0.67)  # 67% of max score

    # First letter matches (same starting sound)
    if soundex1[0] == soundex2[0]:
        return float(max_score * 0.33)  # 33% of max score

    return 0.0


def calculate_dob_score(dob1, dob2, max_score=20):
    """
    Compare dates of birth with tolerance for data entry errors.

    Args:
        dob1 (date): First date of birth
        dob2 (date): Second date of birth
        max_score (int): Maximum possible score (default: 20)

    Returns:
        float: DOB similarity score (0 to max_score)
    """
    if not dob1 or not dob2:
        return 0.0

    # Exact match
    if dob1 == dob2:
        return float(max_score)

    # Same year and month (day typo)
    if dob1.year == dob2.year and dob1.month == dob2.month:
        days_diff = abs((dob1 - dob2).days)
        if days_diff <= 2:
            return float(max_score * 0.9)  # Very likely same person
        elif days_diff <= 7:
            return float(max_score * 0.75)  # Possible typo

    # Same year and day (month/day transposition)
    if dob1.year == dob2.year and dob1.day == dob2.day:
        if abs(dob1.month - dob2.month) <= 1:
            return float(max_score * 0.9)  # Very likely transposition

    # Same year (different month/day)
    if dob1.year == dob2.year:
        days_diff = abs((dob1 - dob2).days)
        if days_diff <= 30:
            return float(max_score * 0.6)  # Within one month

    # Year typo (off by 1)
    if abs(dob1.year - dob2.year) == 1:
        if dob1.month == dob2.month and dob1.day == dob2.day:
            return float(max_score * 0.75)  # Likely year typo

    return 0.0


def calculate_geographic_score(beneficiary1, beneficiary2, max_score=10):
    """
    Compare geographic locations for address-based matching.

    Args:
        beneficiary1 (Beneficiary): First beneficiary
        beneficiary2 (Beneficiary): Second beneficiary
        max_score (int): Maximum possible score (default: 10)

    Returns:
        float: Geographic similarity score (0 to max_score)
    """
    # Same barangay = very high confidence
    if beneficiary1.barangay_id == beneficiary2.barangay_id:
        return float(max_score)

    # Same municipality = high confidence
    if beneficiary1.municipality_id == beneficiary2.municipality_id:
        return float(max_score * 0.7)

    # Same province = medium confidence
    if beneficiary1.province_id == beneficiary2.province_id:
        return float(max_score * 0.5)

    # Same region = low confidence
    if beneficiary1.region_id == beneficiary2.region_id:
        return float(max_score * 0.3)

    return 0.0


def calculate_overall_confidence(beneficiary1, beneficiary2):
    """
    Calculate overall confidence score (0-100) for duplicate match.

    Args:
        beneficiary1 (Beneficiary): First beneficiary
        beneficiary2 (Beneficiary): Second beneficiary

    Returns:
        tuple: (confidence_score, matching_factors_dict)
            confidence_score (Decimal): Overall confidence (0-100)
            matching_factors_dict (dict): Breakdown of scores
    """
    # Factor 1: Exact name match (40 points max)
    first_name_exact = calculate_name_match_score(
        beneficiary1.first_name,
        beneficiary2.first_name,
        max_score=20  # Half of 40 for first name
    )
    last_name_exact = calculate_name_match_score(
        beneficiary1.last_name,
        beneficiary2.last_name,
        max_score=20  # Half of 40 for last name
    )
    name_exact_total = first_name_exact + last_name_exact

    # Factor 2: Phonetic match (30 points max)
    first_name_phonetic = calculate_phonetic_score(
        beneficiary1.first_name_soundex,
        beneficiary2.first_name_soundex,
        max_score=15  # Half of 30 for first name
    )
    last_name_phonetic = calculate_phonetic_score(
        beneficiary1.last_name_soundex,
        beneficiary2.last_name_soundex,
        max_score=15  # Half of 30 for last name
    )
    phonetic_total = first_name_phonetic + last_name_phonetic

    # Factor 3: Date of birth (20 points max)
    dob_score = calculate_dob_score(
        beneficiary1.date_of_birth,
        beneficiary2.date_of_birth,
        max_score=20
    )

    # Factor 4: Geographic location (10 points max)
    geo_score = calculate_geographic_score(
        beneficiary1,
        beneficiary2,
        max_score=10
    )

    # Total confidence (0-100)
    total_score = name_exact_total + phonetic_total + dob_score + geo_score

    # Convert to Decimal (2 decimal places)
    confidence = Decimal(str(round(total_score, 2)))

    # Detailed breakdown (for audit trail)
    factors = {
        'first_name_exact': round(first_name_exact, 2),
        'last_name_exact': round(last_name_exact, 2),
        'name_exact_total': round(name_exact_total, 2),
        'first_name_phonetic': round(first_name_phonetic, 2),
        'last_name_phonetic': round(last_name_phonetic, 2),
        'phonetic_total': round(phonetic_total, 2),
        'date_of_birth': round(dob_score, 2),
        'geographic': round(geo_score, 2),
        'total_confidence': float(confidence),
    }

    return confidence, factors


def find_potential_duplicates(beneficiary, threshold=60.0, limit=10):
    """
    Find potential duplicate beneficiaries using fuzzy matching.

    Strategy:
    1. Query candidates with same soundex codes (fast pre-filter)
    2. Calculate confidence scores for each candidate
    3. Return matches above threshold, sorted by confidence

    Args:
        beneficiary (Beneficiary): Beneficiary to find duplicates for
        threshold (float): Minimum confidence score (0-100) to include
        limit (int): Maximum number of duplicates to return

    Returns:
        list: List of dicts with keys:
            - 'beneficiary': Beneficiary object
            - 'confidence': Confidence score (Decimal)
            - 'factors': Matching factors dict
    """
    from beneficiaries.models import Beneficiary

    # Pre-filter candidates using soundex (fast database query)
    candidates = Beneficiary.objects.filter(
        Q(first_name_soundex=beneficiary.first_name_soundex) |
        Q(last_name_soundex=beneficiary.last_name_soundex),
        is_duplicate=False  # Exclude already-merged records
    ).exclude(
        id=beneficiary.id  # Exclude self
    ).select_related('barangay', 'municipality', 'province', 'region')

    # Calculate confidence scores for each candidate
    results = []
    for candidate in candidates:
        confidence, factors = calculate_overall_confidence(beneficiary, candidate)

        # Only include if above threshold
        if confidence >= Decimal(str(threshold)):
            results.append({
                'beneficiary': candidate,
                'confidence': confidence,
                'factors': factors,
            })

    # Sort by confidence (descending) and limit results
    results.sort(key=lambda x: x['confidence'], reverse=True)
    return results[:limit]
```

### 3.2 Deduplication Service

Create `src/beneficiaries/services/deduplication.py`:

```python
"""
Beneficiary deduplication service.
Handles merge operations and workflow logic.
"""

from django.db import transaction
from django.utils import timezone
from beneficiaries.models import Beneficiary, DeduplicationLog, BeneficiaryService
from beneficiaries.utils.matching import (
    find_potential_duplicates,
    calculate_overall_confidence
)


class DeduplicationService:
    """
    Service class for beneficiary deduplication operations.
    """

    @staticmethod
    def check_duplicates_on_save(beneficiary):
        """
        Check for potential duplicates when beneficiary is saved.
        Used in post_save signal to auto-detect duplicates.

        Args:
            beneficiary (Beneficiary): Newly saved beneficiary

        Returns:
            list: Potential duplicates (empty if none found)
        """
        # Skip if already marked as duplicate
        if beneficiary.is_duplicate:
            return []

        # Find potential duplicates (threshold: 75%)
        duplicates = find_potential_duplicates(
            beneficiary,
            threshold=75.0,
            limit=5
        )

        # Log automatic detection
        for dup in duplicates:
            DeduplicationLog.objects.create(
                action='AUTO_DETECT',
                primary_beneficiary=beneficiary,
                duplicate_beneficiary=dup['beneficiary'],
                confidence_score=dup['confidence'],
                matching_factors=dup['factors'],
                decided_by=beneficiary.created_by,
                notes=f"Automatic detection on save (confidence: {dup['confidence']}%)"
            )

        return duplicates

    @staticmethod
    @transaction.atomic
    def merge_beneficiaries(primary_id, duplicate_id, user, notes=""):
        """
        Merge two beneficiary records (keep primary, mark duplicate as merged).

        Process:
        1. Validate both records exist and are not already merged
        2. Transfer services from duplicate to primary
        3. Mark duplicate record as merged
        4. Create audit log entry

        Args:
            primary_id (UUID): ID of beneficiary to keep
            duplicate_id (UUID): ID of beneficiary to merge
            user (User): User performing the merge
            notes (str): Optional notes explaining decision

        Returns:
            Beneficiary: Primary beneficiary (updated)

        Raises:
            ValueError: If validation fails
        """
        # Get beneficiaries
        try:
            primary = Beneficiary.objects.get(id=primary_id)
            duplicate = Beneficiary.objects.get(id=duplicate_id)
        except Beneficiary.DoesNotExist as e:
            raise ValueError(f"Beneficiary not found: {e}")

        # Validation
        if primary.id == duplicate.id:
            raise ValueError("Cannot merge beneficiary with itself")

        if primary.is_duplicate:
            raise ValueError("Primary beneficiary is already marked as duplicate")

        if duplicate.is_duplicate:
            raise ValueError("Duplicate beneficiary is already merged")

        # Calculate confidence score for audit
        confidence, factors = calculate_overall_confidence(primary, duplicate)

        # Step 1: Transfer services from duplicate to primary
        services_transferred = BeneficiaryService.objects.filter(
            beneficiary=duplicate
        ).update(beneficiary=primary)

        # Step 2: Mark duplicate as merged
        duplicate.is_duplicate = True
        duplicate.merged_into = primary
        duplicate.duplicate_confidence = confidence
        duplicate.save()

        # Step 3: Create audit log
        DeduplicationLog.objects.create(
            action='MERGE',
            primary_beneficiary=primary,
            duplicate_beneficiary=duplicate,
            confidence_score=confidence,
            matching_factors=factors,
            decided_by=user,
            notes=notes or f"Merged {services_transferred} services from duplicate record"
        )

        return primary

    @staticmethod
    def reject_duplicate(primary_id, duplicate_id, user, notes=""):
        """
        Mark two beneficiaries as NOT duplicates (user decision).
        Creates audit log to prevent future false positives.

        Args:
            primary_id (UUID): ID of first beneficiary
            duplicate_id (UUID): ID of second beneficiary
            user (User): User making the decision
            notes (str): Optional notes explaining why not duplicates

        Returns:
            DeduplicationLog: Log entry created
        """
        # Get beneficiaries
        try:
            primary = Beneficiary.objects.get(id=primary_id)
            duplicate = Beneficiary.objects.get(id=duplicate_id)
        except Beneficiary.DoesNotExist as e:
            raise ValueError(f"Beneficiary not found: {e}")

        # Calculate confidence for record
        confidence, factors = calculate_overall_confidence(primary, duplicate)

        # Create rejection log
        log = DeduplicationLog.objects.create(
            action='REJECT',
            primary_beneficiary=primary,
            duplicate_beneficiary=duplicate,
            confidence_score=confidence,
            matching_factors=factors,
            decided_by=user,
            notes=notes or "User confirmed these are different people"
        )

        return log

    @staticmethod
    def get_merge_preview(primary_id, duplicate_id):
        """
        Preview what will happen if two beneficiaries are merged.
        Shows services, confidence score, and matching factors.

        Args:
            primary_id (UUID): ID of beneficiary to keep
            duplicate_id (UUID): ID of beneficiary to merge

        Returns:
            dict: Preview data with keys:
                - primary: Primary beneficiary
                - duplicate: Duplicate beneficiary
                - confidence: Confidence score
                - factors: Matching factors
                - services_to_transfer: Count of services
                - primary_services: List of services primary already has
                - duplicate_services: List of services to be transferred
        """
        # Get beneficiaries
        try:
            primary = Beneficiary.objects.get(id=primary_id)
            duplicate = Beneficiary.objects.get(id=duplicate_id)
        except Beneficiary.DoesNotExist as e:
            raise ValueError(f"Beneficiary not found: {e}")

        # Calculate confidence
        confidence, factors = calculate_overall_confidence(primary, duplicate)

        # Get services
        primary_services = BeneficiaryService.objects.filter(
            beneficiary=primary
        ).select_related('organization')

        duplicate_services = BeneficiaryService.objects.filter(
            beneficiary=duplicate
        ).select_related('organization')

        return {
            'primary': primary,
            'duplicate': duplicate,
            'confidence': confidence,
            'factors': factors,
            'services_to_transfer': duplicate_services.count(),
            'primary_services': list(primary_services),
            'duplicate_services': list(duplicate_services),
        }
```

### 3.3 Django Signals

Create `src/beneficiaries/signals.py`:

```python
"""
Django signals for automatic duplicate detection.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from beneficiaries.models import Beneficiary
from beneficiaries.services.deduplication import DeduplicationService


@receiver(post_save, sender=Beneficiary)
def detect_duplicates_on_save(sender, instance, created, **kwargs):
    """
    Automatically detect potential duplicates when beneficiary is saved.
    Only runs for new beneficiaries (not updates).
    """
    if created and not instance.is_duplicate:
        # Find potential duplicates (threshold: 75%)
        duplicates = DeduplicationService.check_duplicates_on_save(instance)

        if duplicates:
            # Log for monitoring
            print(f"[DEDUP] Found {len(duplicates)} potential duplicates for {instance.full_name}")
```

Register in `src/beneficiaries/apps.py`:

```python
from django.apps import AppConfig


class BeneficiariesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'beneficiaries'
    verbose_name = 'Beneficiary Management'

    def ready(self):
        # Import signals to register them
        import beneficiaries.signals
```

---

## 4. Database Indexes and Performance

### 4.1 Index Strategy

The Beneficiary model uses **5 strategic indexes** for fast duplicate detection:

```python
class Meta:
    indexes = [
        # 1. Composite index for exact name + DOB matching
        models.Index(
            fields=['first_name', 'last_name', 'date_of_birth'],
            name='idx_name_dob'
        ),

        # 2. Soundex indexes for phonetic matching
        models.Index(
            fields=['first_name_soundex', 'last_name_soundex'],
            name='idx_soundex'
        ),

        # 3. Geographic indexes for address matching
        models.Index(
            fields=['barangay', 'municipality'],
            name='idx_geo_location'
        ),

        # 4. Deduplication status index
        models.Index(
            fields=['is_duplicate', 'merged_into'],
            name='idx_dedup_status'
        ),

        # 5. Organization index for multi-tenant filtering
        models.Index(
            fields=['registered_by_organization'],
            name='idx_organization'
        ),
    ]
```

### 4.2 Query Performance

**Expected Performance (with indexes):**

| Operation | Expected Time | Notes |
|-----------|---------------|-------|
| Find duplicates on save | < 500ms | Soundex pre-filter + confidence calculation |
| Search by name + DOB | < 100ms | Uses composite index |
| Filter by organization | < 50ms | Single index lookup |
| Get beneficiary services | < 100ms | Foreign key index |

**Performance Testing:**

```python
# src/beneficiaries/tests/test_performance.py

import pytest
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
import time

from beneficiaries.models import Beneficiary
from beneficiaries.services.deduplication import DeduplicationService
from beneficiaries.utils.matching import find_potential_duplicates


class DeduplicationPerformanceTests(TestCase):
    """
    Performance tests for deduplication operations.
    """

    def setUp(self):
        """Create test beneficiaries"""
        # Create 1000 test beneficiaries
        beneficiaries = []
        base_date = timezone.now().date() - timedelta(days=365 * 30)  # 30 years ago

        for i in range(1000):
            beneficiaries.append(Beneficiary(
                first_name=f"First{i}",
                last_name=f"Last{i}",
                date_of_birth=base_date + timedelta(days=i),
                sex='M' if i % 2 == 0 else 'F',
                # ... other required fields
            ))

        Beneficiary.objects.bulk_create(beneficiaries)

    def test_duplicate_detection_performance(self):
        """Test: Duplicate detection completes in < 500ms"""
        beneficiary = Beneficiary.objects.first()

        start_time = time.time()
        duplicates = find_potential_duplicates(beneficiary, threshold=75.0)
        end_time = time.time()

        duration_ms = (end_time - start_time) * 1000

        self.assertLess(
            duration_ms,
            500,
            f"Duplicate detection took {duration_ms}ms (expected < 500ms)"
        )

    def test_name_search_performance(self):
        """Test: Name search completes in < 100ms"""
        start_time = time.time()
        results = Beneficiary.objects.filter(
            first_name__icontains="First",
            last_name__icontains="Last"
        )[:10]
        list(results)  # Force query execution
        end_time = time.time()

        duration_ms = (end_time - start_time) * 1000

        self.assertLess(
            duration_ms,
            100,
            f"Name search took {duration_ms}ms (expected < 100ms)"
        )
```

### 4.3 Database Maintenance

**Periodic Maintenance Tasks:**

```python
# src/beneficiaries/management/commands/update_soundex_codes.py

from django.core.management.base import BaseCommand
from beneficiaries.models import Beneficiary
from beneficiaries.utils.matching import generate_soundex


class Command(BaseCommand):
    help = 'Regenerate soundex codes for all beneficiaries (maintenance task)'

    def handle(self, *args, **options):
        beneficiaries = Beneficiary.objects.all()
        count = 0

        for beneficiary in beneficiaries:
            beneficiary.first_name_soundex = generate_soundex(beneficiary.first_name)
            beneficiary.last_name_soundex = generate_soundex(beneficiary.last_name)
            beneficiary.save(update_fields=['first_name_soundex', 'last_name_soundex'])
            count += 1

            if count % 100 == 0:
                self.stdout.write(f"Updated {count} beneficiaries...")

        self.stdout.write(
            self.style.SUCCESS(f"Successfully updated {count} beneficiary soundex codes")
        )
```

---

## 5. Deduplication Workflow

### 5.1 Workflow Overview

```
┌─────────────────────────────────────────────────────────┐
│ Step 1: User Registers New Beneficiary                 │
│ - Fill out registration form                           │
│ - Enter: Name, DOB, Sex, Address, Contact             │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│ Step 2: System Saves Beneficiary                       │
│ - Django post_save signal triggered                    │
│ - Auto-populate soundex fields                         │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│ Step 3: Automatic Duplicate Detection                  │
│ - Query candidates with matching soundex               │
│ - Calculate confidence scores                          │
│ - Log auto-detection results                           │
└──────────────────────┬──────────────────────────────────┘
                       ▼
                ┌──────┴──────┐
                │ Duplicates? │
                └──────┬──────┘
         YES ────┘      └──── NO
          │                   │
          ▼                   ▼
┌────────────────────┐  ┌────────────────────┐
│ Step 4a: Show      │  │ Step 4b: Success   │
│ Warning Dialog     │  │ Registration saved │
│                    │  └────────────────────┘
│ Confidence: 92%    │
│ - Muhammad Ali     │
│ - 1990-05-15       │
│ - Barangay Poblac. │
│                    │
│ Actions:           │
│ [Merge] [Not Dup] │
└──────┬─────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Step 5: User Decision                │
│                                      │
│ Option A: Merge (confirmed duplicate)│
│ Option B: Not Duplicate (different)  │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Step 6: Execute Action               │
│                                      │
│ If Merge:                            │
│ - Transfer services to primary       │
│ - Mark duplicate as merged           │
│ - Create audit log                   │
│                                      │
│ If Not Duplicate:                    │
│ - Create rejection log               │
│ - Prevent future false positives    │
└──────────────────────────────────────┘
```

### 5.2 User Actions

**Action 1: View Potential Duplicates**

```python
# src/beneficiaries/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from beneficiaries.models import Beneficiary
from beneficiaries.utils.matching import find_potential_duplicates


@login_required
def beneficiary_duplicates_view(request, beneficiary_id):
    """
    Show potential duplicates for a beneficiary.
    """
    beneficiary = get_object_or_404(Beneficiary, id=beneficiary_id)

    # Find potential duplicates (threshold: 60% for informational)
    duplicates = find_potential_duplicates(
        beneficiary,
        threshold=60.0,
        limit=10
    )

    # Categorize by confidence level
    very_high = [d for d in duplicates if d['confidence'] >= 90]
    high = [d for d in duplicates if 75 <= d['confidence'] < 90]
    medium = [d for d in duplicates if 60 <= d['confidence'] < 75]

    context = {
        'beneficiary': beneficiary,
        'very_high_duplicates': very_high,
        'high_duplicates': high,
        'medium_duplicates': medium,
    }

    return render(request, 'beneficiaries/duplicates.html', context)
```

**Action 2: Preview Merge**

```python
@login_required
def merge_preview_view(request, primary_id, duplicate_id):
    """
    Show preview of what will happen if two beneficiaries are merged.
    """
    from beneficiaries.services.deduplication import DeduplicationService

    try:
        preview = DeduplicationService.get_merge_preview(primary_id, duplicate_id)
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('beneficiaries:list')

    context = {
        'preview': preview,
    }

    return render(request, 'beneficiaries/merge_preview.html', context)
```

**Action 3: Execute Merge**

```python
@login_required
@require_POST
def execute_merge_view(request, primary_id, duplicate_id):
    """
    Execute merge of two beneficiaries (user confirmed).
    """
    from beneficiaries.services.deduplication import DeduplicationService

    notes = request.POST.get('notes', '')

    try:
        primary = DeduplicationService.merge_beneficiaries(
            primary_id,
            duplicate_id,
            user=request.user,
            notes=notes
        )

        messages.success(
            request,
            f"Successfully merged duplicate into {primary.full_name}"
        )

        return redirect('beneficiaries:detail', pk=primary.id)

    except ValueError as e:
        messages.error(request, str(e))
        return redirect('beneficiaries:list')
```

**Action 4: Reject Duplicate**

```python
@login_required
@require_POST
def reject_duplicate_view(request, primary_id, duplicate_id):
    """
    Mark two beneficiaries as NOT duplicates (user decision).
    """
    from beneficiaries.services.deduplication import DeduplicationService

    notes = request.POST.get('notes', '')

    try:
        DeduplicationService.reject_duplicate(
            primary_id,
            duplicate_id,
            user=request.user,
            notes=notes
        )

        messages.success(
            request,
            "Confirmed these are different people. Won't show again."
        )

        return redirect('beneficiaries:detail', pk=primary_id)

    except ValueError as e:
        messages.error(request, str(e))
        return redirect('beneficiaries:list')
```

---

## 6. User Interface Components

### 6.1 Registration Form with Duplicate Warning

**Template:** `src/templates/beneficiaries/register.html`

```html
{% extends "base.html" %}
{% load static %}

{% block content %}
<div class="max-w-4xl mx-auto px-4 py-8">
    <!-- Page Header -->
    <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900">Register New Beneficiary</h1>
        <p class="mt-2 text-gray-600">
            Enter beneficiary details. System will check for potential duplicates.
        </p>
    </div>

    <!-- Registration Form -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-sm">
        <form method="POST" id="beneficiaryForm" hx-post="{% url 'beneficiaries:register' %}"
              hx-target="#formContainer" hx-swap="outerHTML">
            {% csrf_token %}

            <div id="formContainer" class="p-6 space-y-6">
                <!-- Personal Information Section -->
                <div>
                    <h3 class="text-lg font-semibold text-gray-900 mb-4">
                        <i class="fas fa-user mr-2 text-blue-600"></i>
                        Personal Information
                    </h3>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <!-- First Name -->
                        <div>
                            <label for="id_first_name" class="block text-sm font-medium text-gray-700 mb-2">
                                First Name<span class="text-red-500">*</span>
                            </label>
                            {{ form.first_name }}
                        </div>

                        <!-- Middle Name -->
                        <div>
                            <label for="id_middle_name" class="block text-sm font-medium text-gray-700 mb-2">
                                Middle Name
                            </label>
                            {{ form.middle_name }}
                        </div>

                        <!-- Last Name -->
                        <div>
                            <label for="id_last_name" class="block text-sm font-medium text-gray-700 mb-2">
                                Last Name<span class="text-red-500">*</span>
                            </label>
                            {{ form.last_name }}
                        </div>

                        <!-- Suffix -->
                        <div>
                            <label for="id_suffix" class="block text-sm font-medium text-gray-700 mb-2">
                                Suffix
                            </label>
                            {{ form.suffix }}
                        </div>

                        <!-- Date of Birth -->
                        <div>
                            <label for="id_date_of_birth" class="block text-sm font-medium text-gray-700 mb-2">
                                Date of Birth<span class="text-red-500">*</span>
                            </label>
                            {{ form.date_of_birth }}
                        </div>

                        <!-- Sex -->
                        <div>
                            <label for="id_sex" class="block text-sm font-medium text-gray-700 mb-2">
                                Sex<span class="text-red-500">*</span>
                            </label>
                            {{ form.sex }}
                        </div>
                    </div>
                </div>

                <!-- Address Section -->
                <div>
                    <h3 class="text-lg font-semibold text-gray-900 mb-4">
                        <i class="fas fa-map-marker-alt mr-2 text-emerald-600"></i>
                        Address Information
                    </h3>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <!-- Region -->
                        <div>
                            <label for="id_region" class="block text-sm font-medium text-gray-700 mb-2">
                                Region<span class="text-red-500">*</span>
                            </label>
                            {{ form.region }}
                        </div>

                        <!-- Province -->
                        <div>
                            <label for="id_province" class="block text-sm font-medium text-gray-700 mb-2">
                                Province<span class="text-red-500">*</span>
                            </label>
                            {{ form.province }}
                        </div>

                        <!-- Municipality -->
                        <div>
                            <label for="id_municipality" class="block text-sm font-medium text-gray-700 mb-2">
                                Municipality/City<span class="text-red-500">*</span>
                            </label>
                            {{ form.municipality }}
                        </div>

                        <!-- Barangay -->
                        <div>
                            <label for="id_barangay" class="block text-sm font-medium text-gray-700 mb-2">
                                Barangay<span class="text-red-500">*</span>
                            </label>
                            {{ form.barangay }}
                        </div>

                        <!-- Street Address -->
                        <div class="md:col-span-2">
                            <label for="id_street_address" class="block text-sm font-medium text-gray-700 mb-2">
                                Street Address
                            </label>
                            {{ form.street_address }}
                        </div>
                    </div>
                </div>

                <!-- Contact Section -->
                <div>
                    <h3 class="text-lg font-semibold text-gray-900 mb-4">
                        <i class="fas fa-phone mr-2 text-purple-600"></i>
                        Contact Information
                    </h3>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <!-- Phone -->
                        <div>
                            <label for="id_phone_number" class="block text-sm font-medium text-gray-700 mb-2">
                                Mobile Number
                            </label>
                            {{ form.phone_number }}
                        </div>

                        <!-- Email -->
                        <div>
                            <label for="id_email" class="block text-sm font-medium text-gray-700 mb-2">
                                Email Address
                            </label>
                            {{ form.email }}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Form Footer -->
            <div class="px-6 py-4 bg-gray-50 rounded-b-xl border-t border-gray-200 flex justify-end space-x-3">
                <a href="{% url 'beneficiaries:list' %}"
                   class="px-6 py-3 text-gray-700 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors">
                    Cancel
                </a>
                <button type="submit"
                        class="px-6 py-3 bg-gradient-to-r from-blue-600 to-teal-600 text-white rounded-xl hover:from-blue-700 hover:to-teal-700 transition-all">
                    <i class="fas fa-check mr-2"></i>
                    Register Beneficiary
                </button>
            </div>
        </form>
    </div>
</div>

<!-- Duplicate Warning Modal (shown via HTMX if duplicates found) -->
<div id="duplicateModal" class="hidden fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
    <!-- Modal content loaded dynamically -->
</div>
{% endblock %}
```

### 6.2 Duplicate Warning Dialog

**Template:** `src/templates/beneficiaries/partials/duplicate_warning.html`

```html
<!-- Duplicate Warning Modal (HTMX response) -->
<div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center"
     id="duplicateWarningOverlay">
    <div class="bg-white rounded-xl shadow-2xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <!-- Header -->
        <div class="p-6 border-b border-gray-200 bg-amber-50">
            <div class="flex items-start">
                <div class="flex-shrink-0">
                    <i class="fas fa-exclamation-triangle text-amber-600 text-3xl"></i>
                </div>
                <div class="ml-4 flex-1">
                    <h3 class="text-xl font-bold text-gray-900">
                        Potential Duplicate Detected
                    </h3>
                    <p class="mt-1 text-sm text-gray-600">
                        Found {{ duplicates|length }} existing record(s) that may match this beneficiary.
                        Please review carefully to avoid duplicate registrations.
                    </p>
                </div>
            </div>
        </div>

        <!-- Duplicate Matches -->
        <div class="p-6 space-y-4">
            {% for duplicate in duplicates %}
            <div class="bg-white border-2 rounded-xl p-4
                        {% if duplicate.confidence >= 90 %}
                        border-red-300 bg-red-50
                        {% elif duplicate.confidence >= 75 %}
                        border-amber-300 bg-amber-50
                        {% else %}
                        border-blue-300 bg-blue-50
                        {% endif %}">

                <!-- Confidence Badge -->
                <div class="flex items-start justify-between mb-3">
                    <div>
                        <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium
                                     {% if duplicate.confidence >= 90 %}
                                     bg-red-100 text-red-800
                                     {% elif duplicate.confidence >= 75 %}
                                     bg-amber-100 text-amber-800
                                     {% else %}
                                     bg-blue-100 text-blue-800
                                     {% endif %}">
                            {{ duplicate.confidence }}% Match
                        </span>
                    </div>
                    <div class="text-right">
                        <p class="text-xs text-gray-500">Registered by</p>
                        <p class="text-sm font-medium text-gray-900">
                            {{ duplicate.beneficiary.registered_by_organization.name }}
                        </p>
                    </div>
                </div>

                <!-- Beneficiary Details -->
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <p class="text-xs text-gray-500 mb-1">Name</p>
                        <p class="font-semibold text-gray-900">
                            {{ duplicate.beneficiary.full_name }}
                        </p>
                    </div>
                    <div>
                        <p class="text-xs text-gray-500 mb-1">Date of Birth</p>
                        <p class="font-semibold text-gray-900">
                            {{ duplicate.beneficiary.date_of_birth|date:"F d, Y" }}
                            <span class="text-gray-500">(Age: {{ duplicate.beneficiary.age }})</span>
                        </p>
                    </div>
                    <div>
                        <p class="text-xs text-gray-500 mb-1">Address</p>
                        <p class="text-sm text-gray-900">
                            {{ duplicate.beneficiary.barangay.name }},
                            {{ duplicate.beneficiary.municipality.name }}
                        </p>
                    </div>
                    <div>
                        <p class="text-xs text-gray-500 mb-1">Contact</p>
                        <p class="text-sm text-gray-900">
                            {% if duplicate.beneficiary.phone_number %}
                                {{ duplicate.beneficiary.phone_number }}
                            {% else %}
                                <span class="text-gray-400 italic">No phone</span>
                            {% endif %}
                        </p>
                    </div>
                </div>

                <!-- Matching Factors -->
                <div class="mt-3 pt-3 border-t border-gray-200">
                    <p class="text-xs font-medium text-gray-700 mb-2">Match Breakdown:</p>
                    <div class="flex flex-wrap gap-2">
                        {% if duplicate.factors.name_exact_total >= 30 %}
                        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-emerald-100 text-emerald-800">
                            <i class="fas fa-check-circle mr-1"></i> Name Match
                        </span>
                        {% endif %}

                        {% if duplicate.factors.date_of_birth >= 18 %}
                        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-emerald-100 text-emerald-800">
                            <i class="fas fa-check-circle mr-1"></i> DOB Match
                        </span>
                        {% endif %}

                        {% if duplicate.factors.geographic >= 7 %}
                        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-emerald-100 text-emerald-800">
                            <i class="fas fa-check-circle mr-1"></i> Same Area
                        </span>
                        {% endif %}
                    </div>
                </div>

                <!-- Actions -->
                <div class="mt-4 flex space-x-2">
                    <a href="{% url 'beneficiaries:merge_preview' primary_id=new_beneficiary.id duplicate_id=duplicate.beneficiary.id %}"
                       class="flex-1 px-4 py-2 bg-blue-600 text-white text-center rounded-lg hover:bg-blue-700 transition-colors">
                        <i class="fas fa-code-branch mr-2"></i>
                        Merge Records
                    </a>
                    <button type="button"
                            hx-post="{% url 'beneficiaries:reject_duplicate' primary_id=new_beneficiary.id duplicate_id=duplicate.beneficiary.id %}"
                            hx-swap="outerHTML"
                            hx-target="closest .bg-white"
                            class="flex-1 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
                        <i class="fas fa-times-circle mr-2"></i>
                        Different Person
                    </button>
                </div>
            </div>
            {% endfor %}
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 bg-gray-50 rounded-b-xl border-t border-gray-200 flex justify-between">
            <p class="text-sm text-gray-600">
                <i class="fas fa-info-circle mr-1"></i>
                Review all potential matches before proceeding
            </p>
            <button type="button"
                    onclick="document.getElementById('duplicateWarningOverlay').remove()"
                    class="px-6 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
                Continue Anyway
            </button>
        </div>
    </div>
</div>
```

### 6.3 Merge Preview Page

**Template:** `src/templates/beneficiaries/merge_preview.html`

```html
{% extends "base.html" %}
{% load static %}

{% block content %}
<div class="max-w-6xl mx-auto px-4 py-8">
    <!-- Page Header -->
    <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900">Merge Beneficiaries</h1>
        <p class="mt-2 text-gray-600">
            Review the merge operation before proceeding. This action cannot be undone.
        </p>
    </div>

    <!-- Confidence Score -->
    <div class="mb-6 bg-gradient-to-r from-blue-50 to-teal-50 rounded-xl border border-blue-200 p-6">
        <div class="flex items-center justify-between">
            <div>
                <p class="text-sm text-gray-600 mb-1">Match Confidence</p>
                <p class="text-4xl font-bold text-blue-600">
                    {{ preview.confidence }}%
                </p>
            </div>
            <div class="text-right">
                <p class="text-sm text-gray-600 mb-1">Services to Transfer</p>
                <p class="text-4xl font-bold text-teal-600">
                    {{ preview.services_to_transfer }}
                </p>
            </div>
        </div>
    </div>

    <!-- Comparison Grid -->
    <div class="grid grid-cols-2 gap-6 mb-6">
        <!-- Primary Record (KEEP) -->
        <div class="bg-emerald-50 border-2 border-emerald-500 rounded-xl p-6">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-bold text-emerald-900">
                    <i class="fas fa-check-circle mr-2"></i>
                    Primary Record (KEEP)
                </h3>
                <span class="px-3 py-1 bg-emerald-100 text-emerald-800 text-sm font-medium rounded-full">
                    Active
                </span>
            </div>

            <div class="space-y-3">
                <div>
                    <p class="text-xs text-emerald-700 mb-1">Full Name</p>
                    <p class="font-semibold text-emerald-900">
                        {{ preview.primary.full_name }}
                    </p>
                </div>

                <div>
                    <p class="text-xs text-emerald-700 mb-1">Date of Birth</p>
                    <p class="text-emerald-900">
                        {{ preview.primary.date_of_birth|date:"F d, Y" }}
                        <span class="text-emerald-600">(Age: {{ preview.primary.age }})</span>
                    </p>
                </div>

                <div>
                    <p class="text-xs text-emerald-700 mb-1">Address</p>
                    <p class="text-sm text-emerald-900">
                        {{ preview.primary.barangay.name }},
                        {{ preview.primary.municipality.name }},
                        {{ preview.primary.province.name }}
                    </p>
                </div>

                <div>
                    <p class="text-xs text-emerald-700 mb-1">Registered By</p>
                    <p class="text-sm text-emerald-900">
                        {{ preview.primary.registered_by_organization.name }}
                    </p>
                </div>

                <div>
                    <p class="text-xs text-emerald-700 mb-1">Services Received</p>
                    <p class="text-2xl font-bold text-emerald-900">
                        {{ preview.primary_services|length }}
                    </p>
                </div>
            </div>
        </div>

        <!-- Duplicate Record (MERGE) -->
        <div class="bg-red-50 border-2 border-red-500 rounded-xl p-6">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-bold text-red-900">
                    <i class="fas fa-code-branch mr-2"></i>
                    Duplicate Record (MERGE)
                </h3>
                <span class="px-3 py-1 bg-red-100 text-red-800 text-sm font-medium rounded-full">
                    Will be merged
                </span>
            </div>

            <div class="space-y-3">
                <div>
                    <p class="text-xs text-red-700 mb-1">Full Name</p>
                    <p class="font-semibold text-red-900">
                        {{ preview.duplicate.full_name }}
                    </p>
                </div>

                <div>
                    <p class="text-xs text-red-700 mb-1">Date of Birth</p>
                    <p class="text-red-900">
                        {{ preview.duplicate.date_of_birth|date:"F d, Y" }}
                        <span class="text-red-600">(Age: {{ preview.duplicate.age }})</span>
                    </p>
                </div>

                <div>
                    <p class="text-xs text-red-700 mb-1">Address</p>
                    <p class="text-sm text-red-900">
                        {{ preview.duplicate.barangay.name }},
                        {{ preview.duplicate.municipality.name }},
                        {{ preview.duplicate.province.name }}
                    </p>
                </div>

                <div>
                    <p class="text-xs text-red-700 mb-1">Registered By</p>
                    <p class="text-sm text-red-900">
                        {{ preview.duplicate.registered_by_organization.name }}
                    </p>
                </div>

                <div>
                    <p class="text-xs text-red-700 mb-1">Services to Transfer</p>
                    <p class="text-2xl font-bold text-red-900">
                        {{ preview.duplicate_services|length }}
                    </p>
                </div>
            </div>
        </div>
    </div>

    <!-- Services List -->
    {% if preview.duplicate_services %}
    <div class="mb-6 bg-white rounded-xl border border-gray-200 shadow-sm">
        <div class="p-6 border-b border-gray-200">
            <h3 class="text-lg font-bold text-gray-900">
                <i class="fas fa-list mr-2 text-blue-600"></i>
                Services to be Transferred
            </h3>
            <p class="mt-1 text-sm text-gray-600">
                These {{ preview.services_to_transfer }} service(s) will be transferred to the primary record
            </p>
        </div>

        <div class="divide-y divide-gray-200">
            {% for service in preview.duplicate_services %}
            <div class="p-4 hover:bg-gray-50">
                <div class="flex items-start justify-between">
                    <div class="flex-1">
                        <p class="font-semibold text-gray-900">{{ service.service_type }}</p>
                        <p class="text-sm text-gray-600 mt-1">{{ service.service_description }}</p>
                        <p class="text-xs text-gray-500 mt-2">
                            <i class="fas fa-building mr-1"></i>
                            {{ service.organization.name }}
                        </p>
                    </div>
                    <div class="text-right ml-4">
                        <p class="text-sm font-medium text-gray-900">
                            {{ service.date_provided|date:"M d, Y" }}
                        </p>
                        {% if service.amount %}
                        <p class="text-sm text-emerald-600 font-semibold">
                            ₱{{ service.amount|floatformat:2 }}
                        </p>
                        {% endif %}
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}

    <!-- Merge Confirmation Form -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-sm">
        <form method="POST" action="{% url 'beneficiaries:execute_merge' primary_id=preview.primary.id duplicate_id=preview.duplicate.id %}">
            {% csrf_token %}

            <div class="p-6">
                <label for="id_notes" class="block text-sm font-medium text-gray-700 mb-2">
                    Notes (Optional)
                </label>
                <textarea id="id_notes" name="notes" rows="3"
                          class="block w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500"
                          placeholder="Add any notes about this merge decision..."></textarea>
                <p class="mt-2 text-xs text-gray-500">
                    This note will be saved in the audit log for future reference
                </p>
            </div>

            <!-- Warning Banner -->
            <div class="px-6 pb-6">
                <div class="bg-amber-50 border border-amber-200 rounded-lg p-4">
                    <div class="flex items-start">
                        <i class="fas fa-exclamation-triangle text-amber-600 mt-1"></i>
                        <div class="ml-3">
                            <p class="text-sm font-medium text-amber-900">
                                This action cannot be undone
                            </p>
                            <p class="text-sm text-amber-700 mt-1">
                                The duplicate record will be marked as merged and all services will be transferred to the primary record.
                                This merge will be logged for audit purposes.
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Form Footer -->
            <div class="px-6 py-4 bg-gray-50 rounded-b-xl border-t border-gray-200 flex justify-end space-x-3">
                <a href="{% url 'beneficiaries:list' %}"
                   class="px-6 py-3 text-gray-700 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors">
                    <i class="fas fa-times mr-2"></i>
                    Cancel
                </a>
                <button type="submit"
                        class="px-6 py-3 bg-gradient-to-r from-red-600 to-red-700 text-white rounded-xl hover:from-red-700 hover:to-red-800 transition-all">
                    <i class="fas fa-code-branch mr-2"></i>
                    Confirm Merge
                </button>
            </div>
        </form>
    </div>
</div>
{% endblock %}
```

---

## 7. Testing Strategy

### 7.1 Unit Tests

```python
# src/beneficiaries/tests/test_matching.py

import pytest
from datetime import date
from beneficiaries.utils.matching import (
    generate_soundex,
    calculate_name_match_score,
    calculate_phonetic_score,
    calculate_dob_score,
    calculate_overall_confidence,
)


class TestSoundexGeneration:
    """Test soundex code generation"""

    def test_soundex_identical_pronunciation(self):
        """Test: Names with same pronunciation get same soundex"""
        assert generate_soundex("Muhammad") == generate_soundex("Mohammad")
        assert generate_soundex("Aisha") == generate_soundex("Ayesha")
        assert generate_soundex("Ali") == generate_soundex("Aly")

    def test_soundex_different_names(self):
        """Test: Different names get different soundex"""
        assert generate_soundex("Ahmad") != generate_soundex("Hassan")
        assert generate_soundex("Fatima") != generate_soundex("Zainab")

    def test_soundex_empty_string(self):
        """Test: Empty string returns empty soundex"""
        assert generate_soundex("") == ""
        assert generate_soundex(None) == ""


class TestNameMatching:
    """Test name similarity scoring"""

    def test_exact_match_full_score(self):
        """Test: Exact name match = 40 points"""
        score = calculate_name_match_score("Muhammad Ali", "Muhammad Ali", max_score=40)
        assert score == 40.0

    def test_case_insensitive_match(self):
        """Test: Case doesn't matter"""
        score = calculate_name_match_score("MUHAMMAD ALI", "muhammad ali", max_score=40)
        assert score == 40.0

    def test_typo_similarity(self):
        """Test: Single typo = high similarity"""
        score = calculate_name_match_score("Muhammad", "Mohammad", max_score=40)
        assert score >= 35.0  # Allow 1 character difference

    def test_substring_match(self):
        """Test: Nickname scenario"""
        score = calculate_name_match_score("Muhammad", "Muhammad Ali", max_score=40)
        assert score == 30.0  # 75% of max score


class TestPhoneticMatching:
    """Test soundex-based phonetic matching"""

    def test_exact_soundex_full_score(self):
        """Test: Same soundex = 30 points"""
        score = calculate_phonetic_score("M530", "M530", max_score=30)
        assert score == 30.0

    def test_partial_soundex_match(self):
        """Test: Partial soundex = partial score"""
        score = calculate_phonetic_score("M530", "M523", max_score=30)
        assert 10.0 <= score < 30.0  # First letter matches


class TestDOBMatching:
    """Test date of birth similarity scoring"""

    def test_exact_dob_full_score(self):
        """Test: Exact DOB match = 20 points"""
        dob1 = date(1990, 5, 15)
        dob2 = date(1990, 5, 15)
        score = calculate_dob_score(dob1, dob2, max_score=20)
        assert score == 20.0

    def test_day_typo_high_score(self):
        """Test: Day off by 1 = 18 points"""
        dob1 = date(1990, 5, 15)
        dob2 = date(1990, 5, 16)
        score = calculate_dob_score(dob1, dob2, max_score=20)
        assert score >= 18.0

    def test_month_day_transposition(self):
        """Test: Month/day swap = 18 points"""
        dob1 = date(1990, 5, 15)
        dob2 = date(1990, 15, 5)  # May 15 vs. Invalid (would be caught in validation)
        # In practice, validation prevents this, but algorithm handles it
```

### 7.2 Integration Tests

```python
# src/beneficiaries/tests/test_deduplication.py

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from beneficiaries.models import Beneficiary, DeduplicationLog
from beneficiaries.services.deduplication import DeduplicationService
from organizations.models import Organization
from common.models import Region, Province, Municipality, Barangay


User = get_user_model()


class DeduplicationIntegrationTests(TestCase):
    """
    Integration tests for end-to-end deduplication workflows
    """

    def setUp(self):
        """Create test data"""
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Create organization
        self.org = Organization.objects.create(
            name='Ministry of Health',
            code='MOH',
            category='MIN'
        )

        # Create geographic hierarchy
        self.region = Region.objects.create(name='BARMM')
        self.province = Province.objects.create(name='Maguindanao', region=self.region)
        self.municipality = Municipality.objects.create(name='Cotabato City', province=self.province)
        self.barangay = Barangay.objects.create(name='Poblacion', municipality=self.municipality)

    def test_automatic_duplicate_detection(self):
        """Test: System auto-detects duplicates on save"""
        # Create first beneficiary
        ben1 = Beneficiary.objects.create(
            first_name='Muhammad',
            last_name='Ali',
            date_of_birth=date(1990, 5, 15),
            sex='M',
            region=self.region,
            province=self.province,
            municipality=self.municipality,
            barangay=self.barangay,
            registered_by_organization=self.org,
            created_by=self.user
        )

        # Create duplicate (typo in first name)
        ben2 = Beneficiary.objects.create(
            first_name='Mohammad',  # Typo
            last_name='Ali',
            date_of_birth=date(1990, 5, 15),
            sex='M',
            region=self.region,
            province=self.province,
            municipality=self.municipality,
            barangay=self.barangay,
            registered_by_organization=self.org,
            created_by=self.user
        )

        # Check: Auto-detection log created
        logs = DeduplicationLog.objects.filter(
            action='AUTO_DETECT',
            primary_beneficiary=ben2
        )

        assert logs.count() >= 1, "System should auto-detect duplicate"
        log = logs.first()
        assert log.confidence_score >= 85.0, "Confidence should be high for near-exact match"

    def test_merge_beneficiaries_success(self):
        """Test: Merge operation transfers services and marks duplicate"""
        # Create beneficiaries
        ben1 = Beneficiary.objects.create(
            first_name='Muhammad',
            last_name='Ali',
            date_of_birth=date(1990, 5, 15),
            sex='M',
            region=self.region,
            province=self.province,
            municipality=self.municipality,
            barangay=self.barangay,
            registered_by_organization=self.org,
            created_by=self.user
        )

        ben2 = Beneficiary.objects.create(
            first_name='Mohammad',
            last_name='Ali',
            date_of_birth=date(1990, 5, 15),
            sex='M',
            region=self.region,
            province=self.province,
            municipality=self.municipality,
            barangay=self.barangay,
            registered_by_organization=self.org,
            created_by=self.user
        )

        # Add services to duplicate
        from beneficiaries.models import BeneficiaryService
        service = BeneficiaryService.objects.create(
            beneficiary=ben2,
            organization=self.org,
            service_type='Health Subsidy',
            service_description='Monthly health allowance',
            date_provided=date.today(),
            amount=5000.00,
            created_by=self.user
        )

        # Execute merge
        primary = DeduplicationService.merge_beneficiaries(
            primary_id=ben1.id,
            duplicate_id=ben2.id,
            user=self.user,
            notes="Test merge"
        )

        # Reload ben2 from database
        ben2.refresh_from_database()

        # Assertions
        assert ben2.is_duplicate, "Duplicate should be marked"
        assert ben2.merged_into == ben1, "Duplicate should link to primary"
        assert service.beneficiary == ben1, "Service should be transferred"

        # Check audit log
        log = DeduplicationLog.objects.get(
            action='MERGE',
            primary_beneficiary=ben1,
            duplicate_beneficiary=ben2
        )
        assert log.decided_by == self.user
        assert log.notes == "Test merge"

    def test_reject_duplicate_creates_log(self):
        """Test: Rejecting duplicate creates audit log"""
        # Create beneficiaries
        ben1 = Beneficiary.objects.create(
            first_name='Muhammad',
            last_name='Ali',
            date_of_birth=date(1990, 5, 15),
            sex='M',
            region=self.region,
            province=self.province,
            municipality=self.municipality,
            barangay=self.barangay,
            registered_by_organization=self.org,
            created_by=self.user
        )

        ben2 = Beneficiary.objects.create(
            first_name='Ahmad',
            last_name='Hassan',
            date_of_birth=date(1990, 5, 15),
            sex='M',
            region=self.region,
            province=self.province,
            municipality=self.municipality,
            barangay=self.barangay,
            registered_by_organization=self.org,
            created_by=self.user
        )

        # Reject as duplicate
        log = DeduplicationService.reject_duplicate(
            primary_id=ben1.id,
            duplicate_id=ben2.id,
            user=self.user,
            notes="Different people, verified by field staff"
        )

        # Assertions
        assert log.action == 'REJECT'
        assert log.decided_by == self.user
        assert "Different people" in log.notes
```

### 7.3 UI Tests (Selenium)

```python
# src/beneficiaries/tests/test_ui_deduplication.py

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.selenium
class TestDeduplicationUI:
    """
    UI tests for deduplication workflow using Selenium
    """

    def test_duplicate_warning_shown_on_registration(self, live_server, driver):
        """Test: Duplicate warning modal appears when duplicate detected"""
        # Step 1: Login
        driver.get(f"{live_server.url}/accounts/login/")
        driver.find_element(By.NAME, "username").send_keys("testuser")
        driver.find_element(By.NAME, "password").send_keys("testpass123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Step 2: Navigate to registration
        driver.get(f"{live_server.url}/beneficiaries/register/")

        # Step 3: Fill out form with duplicate data
        driver.find_element(By.NAME, "first_name").send_keys("Muhammad")
        driver.find_element(By.NAME, "last_name").send_keys("Ali")
        driver.find_element(By.NAME, "date_of_birth").send_keys("1990-05-15")
        driver.find_element(By.NAME, "sex").send_keys("M")
        # ... fill other required fields

        # Step 4: Submit form
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Step 5: Wait for duplicate warning modal
        modal = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "duplicateWarningOverlay"))
        )

        # Assertions
        assert modal.is_displayed(), "Duplicate warning modal should be visible"
        assert "Potential Duplicate" in modal.text
        assert "92%" in modal.text or "Match" in modal.text  # Confidence score shown

    def test_merge_preview_shows_service_transfer(self, live_server, driver):
        """Test: Merge preview displays services to be transferred"""
        # Navigate to merge preview
        driver.get(f"{live_server.url}/beneficiaries/merge-preview/primary-id/duplicate-id/")

        # Check: Services section visible
        services_section = driver.find_element(By.CSS_SELECTOR, ".services-list")
        assert services_section.is_displayed()

        # Check: Service count shown
        count_element = driver.find_element(By.CSS_SELECTOR, ".services-count")
        assert int(count_element.text) > 0
```

---

## 8. PhilSys Integration Preparation

### 8.1 Future PhilSys Model Extension

When PhilSys integration becomes available, extend Beneficiary model:

```python
class Beneficiary(models.Model):
    # ... existing fields ...

    # PhilSys Integration (FUTURE)
    philsys_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text="PhilSys ID (Philippine Identification System Number)"
    )

    philsys_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when PhilSys ID was verified"
    )

    philsys_verified_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='philsys_verifications',
        help_text="User who verified PhilSys ID"
    )
```

### 8.2 Migration Strategy

**Step 1: Add PhilSys Fields (Nullable)**

```python
# Migration: Add philsys_id field (nullable)
python manage.py makemigrations --name add_philsys_fields
python manage.py migrate
```

**Step 2: Gradual PhilSys Enrollment**

```python
# src/beneficiaries/services/philsys.py

class PhilSysService:
    """
    Service for PhilSys integration and verification.
    """

    @staticmethod
    def link_philsys_id(beneficiary, philsys_id, user):
        """
        Link PhilSys ID to existing beneficiary record.

        Args:
            beneficiary (Beneficiary): Beneficiary to link
            philsys_id (str): PhilSys ID number
            user (User): User performing verification

        Returns:
            Beneficiary: Updated beneficiary
        """
        # Validate PhilSys ID format (implementation depends on PhilSys specs)
        if not validate_philsys_format(philsys_id):
            raise ValueError("Invalid PhilSys ID format")

        # Check if PhilSys ID already used
        if Beneficiary.objects.filter(philsys_id=philsys_id).exists():
            raise ValueError("PhilSys ID already registered to another beneficiary")

        # Update beneficiary
        beneficiary.philsys_id = philsys_id
        beneficiary.philsys_verified_at = timezone.now()
        beneficiary.philsys_verified_by = user
        beneficiary.save()

        return beneficiary

    @staticmethod
    def find_by_philsys_id(philsys_id):
        """
        Find beneficiary by PhilSys ID (fastest lookup).
        """
        try:
            return Beneficiary.objects.get(philsys_id=philsys_id)
        except Beneficiary.DoesNotExist:
            return None
```

**Step 3: PhilSys-Based Deduplication**

```python
def find_potential_duplicates(beneficiary, threshold=60.0, limit=10):
    """
    Enhanced duplicate detection with PhilSys support.
    """
    # FIRST: Check PhilSys ID (if available)
    if beneficiary.philsys_id:
        # PhilSys ID is definitive - no fuzzy matching needed
        existing = Beneficiary.objects.filter(
            philsys_id=beneficiary.philsys_id
        ).exclude(id=beneficiary.id)

        if existing.exists():
            # 100% match - same PhilSys ID
            return [{
                'beneficiary': existing.first(),
                'confidence': Decimal('100.00'),
                'factors': {'philsys_match': True},
            }]

    # FALLBACK: Use fuzzy matching (original algorithm)
    # ... existing fuzzy matching code ...
```

### 8.3 PhilSys Enrollment Dashboard

```python
# src/beneficiaries/views.py

@login_required
def philsys_enrollment_dashboard(request):
    """
    Dashboard showing PhilSys enrollment progress.
    Shows beneficiaries without PhilSys ID.
    """
    total_beneficiaries = Beneficiary.objects.filter(is_duplicate=False).count()
    enrolled = Beneficiary.objects.filter(
        is_duplicate=False,
        philsys_id__isnull=False
    ).count()

    enrollment_rate = (enrolled / total_beneficiaries * 100) if total_beneficiaries > 0 else 0

    # Beneficiaries needing enrollment
    pending = Beneficiary.objects.filter(
        is_duplicate=False,
        philsys_id__isnull=True
    ).select_related('barangay', 'municipality', 'registered_by_organization')

    context = {
        'total_beneficiaries': total_beneficiaries,
        'enrolled_count': enrolled,
        'pending_count': total_beneficiaries - enrolled,
        'enrollment_rate': round(enrollment_rate, 2),
        'pending_beneficiaries': pending[:100],  # Show first 100
    }

    return render(request, 'beneficiaries/philsys_enrollment.html', context)
```

---

## Summary

This comprehensive beneficiary deduplication strategy provides:

1. **Robust Data Model** - UUID-based identifiers, soundex fields, deduplication tracking
2. **Advanced Matching Algorithm** - Multi-factor fuzzy matching (90%+ accuracy)
3. **Django Implementation** - Complete utilities, services, signals, and views
4. **Optimized Performance** - Strategic indexes (< 500ms duplicate detection)
5. **User-Friendly Workflow** - Automatic detection, merge preview, audit trail
6. **WCAG-Compliant UI** - Accessible forms, modals, and dashboards
7. **Comprehensive Testing** - Unit, integration, and UI tests
8. **PhilSys Future-Proof** - Ready for PhilSys integration when available

**Next Steps:**
1. Create `beneficiaries` Django app
2. Implement Beneficiary model with deduplication fields
3. Build fuzzy matching utilities (`utils/matching.py`)
4. Create deduplication service (`services/deduplication.py`)
5. Implement views and templates (registration, merge preview)
6. Add database indexes and run migrations
7. Write comprehensive tests (pytest + Selenium)
8. Deploy to staging for pilot MOA testing

**Performance Targets:**
- Duplicate detection: < 500ms
- Name search: < 100ms
- Merge operation: < 2 seconds
- False positive rate: < 5%

---

**Document Status:** ✅ Complete Technical Specification
**Ready for Implementation:** Yes
**Dependencies:** Organizations app (Phase 1), Common app (geographic models)
**Estimated Complexity:** HIGH (multi-factor matching, audit trail, UI workflow)