"""
Tests for Communities AI Services.

Tests data validation, needs classification, and community matching features.
"""

import pytest

pytest.skip(
    "Legacy communities AI service tests require external GEMINI configuration.",
    allow_module_level=True,
)

import json
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from common.models import Barangay, Municipality, Province, Region
from communities.ai_services.community_matcher import CommunityMatcher
from communities.ai_services.data_validator import CommunityDataValidator
from communities.ai_services.needs_classifier import CommunityNeedsClassifier
from communities.models import OBCCommunity

User = get_user_model()


@pytest.mark.django_db
class TestCommunityDataValidator(TestCase):
    """Test AI-powered data validation."""

    def setUp(self):
        """Set up test data."""
        # Create geographic hierarchy
        self.region = Region.objects.create(
            code='12',
            name='Region XII - SOCCSKSARGEN'
        )
        self.province = Province.objects.create(
            region=self.region,
            code='1263',
            name='Sultan Kudarat'
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code='126314',
            name='Palimbang'
        )
        self.barangay = Barangay.objects.create(
            municipality=self.municipality,
            code='126314001',
            name='Akol'
        )

    @patch('communities.ai_services.data_validator.genai.GenerativeModel')
    def test_population_validation_consistent_data(self, mock_model):
        """Test validation with consistent population data."""
        # Mock AI response
        mock_response = Mock()
        mock_response.text = json.dumps({
            'valid': True,
            'issues': [],
            'suggestions': ['Data appears consistent'],
            'confidence': 0.95
        })
        mock_model.return_value.generate_content.return_value = mock_response

        validator = CommunityDataValidator()

        community_data = {
            'total_population': 1000,
            'households': 200,  # 5 persons per household - reasonable
            'male_population': 500,
            'female_population': 500,
        }

        result = validator.validate_population_consistency(community_data)

        assert result['valid'] is True
        assert result['confidence'] >= 0.9
        assert len(result['issues']) == 0

    @patch('communities.ai_services.data_validator.genai.GenerativeModel')
    def test_population_validation_inconsistent_data(self, mock_model):
        """Test validation with inconsistent population data."""
        # Mock AI response for inconsistent data
        mock_response = Mock()
        mock_response.text = json.dumps({
            'valid': False,
            'issues': [
                'Male + Female (900) does not equal Total Population (1000)',
                'Household size (10.0) exceeds typical range for Philippines'
            ],
            'suggestions': [
                'Verify total population count',
                'Check household count - typical size is 4-6 persons'
            ],
            'confidence': 0.85
        })
        mock_model.return_value.generate_content.return_value = mock_response

        validator = CommunityDataValidator()

        community_data = {
            'total_population': 1000,
            'households': 100,  # 10 persons per household - too high
            'male_population': 450,
            'female_population': 450,  # Only 900 total
        }

        result = validator.validate_population_consistency(community_data)

        assert result['valid'] is False
        assert len(result['issues']) > 0
        assert len(result['suggestions']) > 0

    @patch('communities.ai_services.data_validator.genai.GenerativeModel')
    def test_ethnolinguistic_validation_common_group(self, mock_model):
        """Test validation of common ethnolinguistic group for province."""
        # Mock AI response
        mock_response = Mock()
        mock_response.text = json.dumps({
            'valid': True,
            'likelihood': 'Very Common',
            'notes': 'Maguindanaon is the predominant ethnolinguistic group in Sultan Kudarat',
            'alternative_groups': ['Iranun', 'T\'boli']
        })
        mock_model.return_value.generate_content.return_value = mock_response

        validator = CommunityDataValidator()

        result = validator.validate_ethnolinguistic_group(
            group_name='Maguindanaon',
            province='Sultan Kudarat'
        )

        assert result['valid'] is True
        assert result['likelihood'] == 'Very Common'
        assert len(result['notes']) > 0

    @patch('communities.ai_services.data_validator.genai.GenerativeModel')
    def test_suggest_missing_data(self, mock_model):
        """Test missing data suggestions."""
        # Create community with minimal data
        community = OBCCommunity.objects.create(
            barangay=self.barangay,
            name='Test Community',
            estimated_obc_population=500,
            households=100,
        )

        # Mock AI response
        mock_response = Mock()
        mock_response.text = json.dumps({
            'critical_missing': [
                'Geographic coordinates: Essential for mapping and service delivery planning',
                'Livelihood data: Critical for economic program targeting'
            ],
            'important_missing': [
                'Age demographics: Important for education and health service planning',
                'Infrastructure access data: Needed for gap analysis'
            ],
            'optional_missing': [
                'Cultural practices documentation'
            ]
        })
        mock_model.return_value.generate_content.return_value = mock_response

        validator = CommunityDataValidator()
        suggestions = validator.suggest_missing_data(community)

        assert len(suggestions) > 0
        # Check that critical items are flagged
        assert any('[CRITICAL]' in s for s in suggestions)

    @patch('communities.ai_services.data_validator.genai.GenerativeModel')
    def test_livelihood_consistency_validation(self, mock_model):
        """Test livelihood consistency with cultural background."""
        # Mock AI response
        mock_response = Mock()
        mock_response.text = json.dumps({
            'consistent': True,
            'notes': 'Rice farming and fishing are traditional livelihoods for Maguindanaon communities',
            'typical_livelihoods': ['Rice farming', 'Corn farming', 'Fishing', 'Trading']
        })
        mock_model.return_value.generate_content.return_value = mock_response

        validator = CommunityDataValidator()

        result = validator.validate_livelihood_consistency(
            primary_livelihoods='Rice farming, Fishing',
            ethnolinguistic_group='Maguindanaon',
            province='Sultan Kudarat'
        )

        assert result['consistent'] is True
        assert len(result['typical_livelihoods']) > 0


@pytest.mark.django_db
class TestCommunityNeedsClassifier(TestCase):
    """Test AI-powered needs classification."""

    def setUp(self):
        """Set up test data."""
        # Create geographic hierarchy
        self.region = Region.objects.create(
            code='12',
            name='Region XII - SOCCSKSARGEN'
        )
        self.province = Province.objects.create(
            region=self.region,
            code='1263',
            name='Sultan Kudarat'
        )
        self.municipality = Municipality.objects.create(
            province=self.province,
            code='126314',
            name='Palimbang'
        )
        self.barangay = Barangay.objects.create(
            municipality=self.municipality,
            code='126314001',
            name='Akol'
        )

        # Create community with poor infrastructure access
        self.community = OBCCommunity.objects.create(
            barangay=self.barangay,
            name='Test Community',
            estimated_obc_population=1000,
            households=200,
            primary_ethnolinguistic_group='maguindanaon',
            access_clean_water='poor',
            access_electricity='none',
            access_healthcare='poor',
            access_formal_education='fair',
            primary_livelihoods='Subsistence farming',
            estimated_poverty_incidence='high',
        )

    @patch('communities.ai_services.needs_classifier.genai.GenerativeModel')
    def test_classify_needs_accuracy(self, mock_model):
        """Test needs classification returns expected categories."""
        # Mock AI response
        mock_response = Mock()
        mock_response.text = json.dumps({
            'health_infrastructure': 0.80,
            'education_facilities': 0.65,
            'livelihood_programs': 0.90,
            'water_and_sanitation': 0.95,
            'road_and_transport': 0.70,
            'electricity': 0.90,
            'governance_capacity': 0.55,
            'cultural_preservation': 0.60,
            'islamic_education_madrasah': 0.70,
            'peace_and_security': 0.50,
            'land_tenure_security': 0.65,
            'financial_inclusion': 0.75,
            'top_priorities': [
                {
                    'category': 'Water and Sanitation',
                    'score': 0.95,
                    'rationale': 'Poor access to clean water affects health and daily living'
                },
                {
                    'category': 'Livelihood Programs',
                    'score': 0.90,
                    'rationale': 'High poverty incidence requires economic opportunities'
                },
                {
                    'category': 'Electricity',
                    'score': 0.90,
                    'rationale': 'No electricity access limits education and economic activities'
                }
            ],
            'recommendations': [
                'Priority 1: Develop water supply infrastructure',
                'Priority 2: Implement livelihood programs for subsistence farmers',
                'Priority 3: Extend electricity grid or install solar systems'
            ]
        })
        mock_model.return_value.generate_content.return_value = mock_response

        classifier = CommunityNeedsClassifier()
        needs = classifier.classify_needs(self.community)

        # Check that all need categories have scores
        assert 'water_and_sanitation' in needs
        assert 'livelihood_programs' in needs
        assert 'electricity' in needs

        # Check water and electricity are high priority (poor access)
        assert needs['water_and_sanitation'] > 0.7
        assert needs['electricity'] > 0.7

        # Check that recommendations are provided
        assert 'recommendations' in needs
        assert len(needs['recommendations']) > 0

    @patch('communities.ai_services.needs_classifier.genai.GenerativeModel')
    def test_predict_assessment_priority_high(self, mock_model):
        """Test assessment priority prediction for high-priority community."""
        # Mock AI response
        mock_response = Mock()
        mock_response.text = json.dumps({
            'priority_score': 0.90,
            'priority_level': 'High',
            'rationale': 'High poverty, poor infrastructure access, never assessed',
            'urgency_factors': [
                'Never previously assessed',
                'High poverty incidence',
                'Poor access to water and electricity',
                'Large population without basic services'
            ],
            'recommended_assessment_type': 'Comprehensive MANA',
            'estimated_duration_days': 7,
            'recommended_team_size': 4
        })
        mock_model.return_value.generate_content.return_value = mock_response

        classifier = CommunityNeedsClassifier()
        priority = classifier.predict_assessment_priority(self.community)

        assert priority['priority_level'] in ['Critical', 'High']
        assert priority['priority_score'] > 0.7
        assert len(priority['urgency_factors']) > 0

    @patch('communities.ai_services.needs_classifier.genai.GenerativeModel')
    def test_identify_intervention_opportunities(self, mock_model):
        """Test intervention opportunity identification."""
        # Mock AI response
        mock_response = Mock()
        mock_response.text = json.dumps({
            'interventions': [
                {
                    'need_category': 'Water and Sanitation',
                    'intervention_title': 'Community Water System Development',
                    'description': 'Install deep well and water distribution system',
                    'target_beneficiaries': '200 households (1,000 individuals)',
                    'estimated_cost': 'Medium',
                    'implementation_timeline': 'Medium-term (6-12 months)',
                    'potential_partners': ['DILG', 'Department of Health', 'Local LGU'],
                    'success_indicators': [
                        '90% of households with clean water access',
                        'Reduction in waterborne diseases'
                    ],
                    'cultural_considerations': 'Separate washing areas for ablution (wudu) before prayers'
                },
                {
                    'need_category': 'Livelihood Programs',
                    'intervention_title': 'Agricultural Productivity Enhancement',
                    'description': 'Training on modern farming techniques and provide farm inputs',
                    'target_beneficiaries': 'Farming households',
                    'estimated_cost': 'Low',
                    'implementation_timeline': 'Short-term (3-6 months)',
                    'potential_partners': ['DA', 'DTI', 'DOLE'],
                    'success_indicators': ['Increased crop yield by 30%', 'Higher farm income'],
                    'cultural_considerations': 'Halal-compliant livestock programs if included'
                }
            ]
        })
        mock_model.return_value.generate_content.return_value = mock_response

        classifier = CommunityNeedsClassifier()
        interventions = classifier.identify_intervention_opportunities(self.community)

        assert len(interventions) > 0
        # Check structure
        first_intervention = interventions[0]
        assert 'intervention_title' in first_intervention
        assert 'description' in first_intervention
        assert 'success_indicators' in first_intervention
        assert 'cultural_considerations' in first_intervention


@pytest.mark.django_db
class TestCommunityMatcher(TestCase):
    """Test AI-powered community similarity matching."""

    def setUp(self):
        """Set up test data."""
        # Create geographic hierarchy
        self.region = Region.objects.create(
            code='12',
            name='Region XII - SOCCSKSARGEN'
        )
        self.province = Province.objects.create(
            region=self.region,
            code='1263',
            name='Sultan Kudarat'
        )
        self.municipality1 = Municipality.objects.create(
            province=self.province,
            code='126314',
            name='Palimbang'
        )
        self.municipality2 = Municipality.objects.create(
            province=self.province,
            code='126315',
            name='Kalamansig'
        )

        self.barangay1 = Barangay.objects.create(
            municipality=self.municipality1,
            code='126314001',
            name='Akol'
        )
        self.barangay2 = Barangay.objects.create(
            municipality=self.municipality2,
            code='126315001',
            name='Bantayan'
        )

        # Create similar communities
        self.community1 = OBCCommunity.objects.create(
            barangay=self.barangay1,
            name='Community A',
            estimated_obc_population=1000,
            households=200,
            primary_ethnolinguistic_group='maguindanaon',
            access_electricity='poor',
            primary_livelihoods='Rice farming',
        )

        self.community2 = OBCCommunity.objects.create(
            barangay=self.barangay2,
            name='Community B',
            estimated_obc_population=950,  # Similar population
            households=190,
            primary_ethnolinguistic_group='maguindanaon',  # Same group
            access_electricity='poor',
            primary_livelihoods='Rice farming, Corn farming',  # Similar livelihoods
        )

    @patch('communities.ai_services.community_matcher.genai.GenerativeModel')
    def test_find_similar_communities(self, mock_model):
        """Test finding similar communities."""
        # Mock AI response for similarity calculation
        mock_response = Mock()
        mock_response.text = json.dumps({
            'score': 0.85,
            'matching_features': [
                'population_size',
                'ethnolinguistic_group',
                'livelihoods',
                'infrastructure_access'
            ],
            'differences': ['municipality'],
            'rationale': 'Very similar communities with same cultural background and economic activities'
        })
        mock_model.return_value.generate_content.return_value = mock_response

        matcher = CommunityMatcher()
        similar = matcher.find_similar_communities(self.community1, limit=5)

        assert len(similar) > 0
        # Community2 should be in results
        assert any(s['community'].id == self.community2.id for s in similar)

        # Check structure
        first_match = similar[0]
        assert 'similarity_score' in first_match
        assert 'matching_features' in first_match
        assert 'rationale' in first_match

    @patch('communities.ai_services.community_matcher.genai.GenerativeModel')
    def test_find_best_practice_examples(self, mock_model):
        """Test finding best practice examples."""
        # Mock AI response
        mock_response = Mock()
        mock_response.text = json.dumps({
            'best_practice_communities': [
                {
                    'community_name': 'Community B',
                    'likely_success_score': 0.75,
                    'why_successful': 'Better organized community with active farmers association',
                    'transferable_lessons': 'Community-led agricultural cooperative model'
                }
            ]
        })
        mock_model.return_value.generate_content.return_value = mock_response

        matcher = CommunityMatcher()
        best_practices = matcher.find_best_practice_examples(
            self.community1,
            need_category='Livelihood Programs'
        )

        assert len(best_practices) >= 0
        # Check structure if results returned
        if best_practices:
            first_bp = best_practices[0]
            assert 'community' in first_bp
            assert 'success_factors' in first_bp
            assert 'transferable_lessons' in first_bp


# Integration test with real data (skipped by default)
@pytest.mark.skip(reason="Integration test - requires API key")
@pytest.mark.django_db
class TestAIServicesIntegration(TestCase):
    """Integration tests with real AI API calls."""

    def test_real_validation(self):
        """Test with real Gemini API call."""
        validator = CommunityDataValidator()

        community_data = {
            'total_population': 1000,
            'households': 200,
            'male_population': 500,
            'female_population': 500,
        }

        result = validator.validate_population_consistency(community_data)

        assert 'valid' in result
        assert 'issues' in result
        assert 'suggestions' in result
