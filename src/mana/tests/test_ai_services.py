"""
Tests for MANA AI Services
"""

import pytest

pytest.skip(
    "MANA AI service tests require external GEMINI configuration.",
    allow_module_level=True,
)

import json
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase

from common.models import Barangay, Municipality, Province, Region
from mana.ai_services.cultural_validator import BangsomoroCulturalValidator
from mana.ai_services.needs_extractor import NeedsExtractor
from mana.ai_services.report_generator import AssessmentReportGenerator
from mana.ai_services.response_analyzer import ResponseAnalyzer
from mana.ai_services.theme_extractor import ThemeExtractor
from mana.models import Assessment, AssessmentCategory, WorkshopActivity

User = get_user_model()


@pytest.mark.django_db
class TestResponseAnalyzer(TestCase):
    """Test ResponseAnalyzer service"""

    def setUp(self):
        """Set up test fixtures"""
        cache.clear()

        # Create test user
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Create geographic hierarchy
        self.region = Region.objects.create(
            psgc_code="090000000", name="Region IX", region_name="Zamboanga Peninsula"
        )

        self.province = Province.objects.create(
            psgc_code="097300000",
            name="Zamboanga del Sur",
            region=self.region,
        )

        self.municipality = Municipality.objects.create(
            psgc_code="097301000",
            name="Pagadian City",
            province=self.province,
        )

        self.barangay = Barangay.objects.create(
            psgc_code="097301001",
            name="Balangasan",
            municipality=self.municipality,
        )

        # Create assessment
        self.category = AssessmentCategory.objects.create(
            name="OBC-MANA Workshop",
            category_type="needs_assessment",
        )

        self.assessment = Assessment.objects.create(
            title="Test Assessment",
            category=self.category,
            description="Test description",
            objectives="Test objectives",
            assessment_level="barangay",
            primary_methodology="workshop",
            barangay=self.barangay,
            municipality=self.municipality,
            province=self.province,
            lead_assessor=self.user,
            created_by=self.user,
            planned_start_date="2024-01-01",
            planned_end_date="2024-01-31",
        )

        self.analyzer = ResponseAnalyzer()

    @patch("mana.ai_services.response_analyzer.GeminiAIEngine")
    def test_analyze_question_responses(self, mock_gemini):
        """Test analyzing responses to a single question"""
        # Mock AI response
        mock_response = MagicMock()
        mock_response.text = json.dumps(
            {
                "summary": "Community needs better healthcare access",
                "key_points": ["No clinic nearby", "Medicine shortage", "No doctor"],
                "sentiment": "negative",
                "action_items": ["Build health clinic", "Hire resident doctor"],
                "confidence": 0.85,
            }
        )

        mock_gemini.return_value.model.generate_content.return_value = mock_response

        # Test data
        question = "What are the main health concerns in your community?"
        responses = [
            "We need a clinic nearby",
            "Medicine is very expensive and hard to get",
            "No doctor available in our barangay",
        ]

        # Run analysis
        result = self.analyzer.analyze_question_responses(question, responses)

        # Assertions
        self.assertIn("summary", result)
        self.assertIn("key_points", result)
        self.assertEqual(result["sentiment"], "negative")
        self.assertEqual(len(result["action_items"]), 2)
        self.assertGreaterEqual(result["confidence"], 0.8)

    def test_analyze_empty_responses(self):
        """Test handling of empty responses"""
        result = self.analyzer.analyze_question_responses("Test question?", [])

        self.assertEqual(result["summary"], "No responses available")
        self.assertEqual(result["sentiment"], "neutral")
        self.assertEqual(result["confidence"], 0.0)


@pytest.mark.django_db
class TestThemeExtractor(TestCase):
    """Test ThemeExtractor service"""

    def setUp(self):
        """Set up test fixtures"""
        cache.clear()
        self.extractor = ThemeExtractor()

    @patch("mana.ai_services.theme_extractor.GeminiAIEngine")
    def test_extract_themes(self, mock_gemini):
        """Test theme extraction from responses"""
        # Mock AI response
        mock_response = MagicMock()
        mock_response.text = json.dumps(
            [
                {
                    "theme": "Healthcare Access",
                    "frequency": 15,
                    "example_quotes": ["Need clinic", "No doctor"],
                    "sub_themes": ["Clinic construction", "Medical staff"],
                    "priority": "high",
                    "category": "health",
                },
                {
                    "theme": "Education Quality",
                    "frequency": 10,
                    "example_quotes": ["Need more teachers", "School repairs"],
                    "sub_themes": ["Teacher shortage", "Infrastructure"],
                    "priority": "medium",
                    "category": "education",
                },
            ]
        )

        mock_gemini.return_value.model.generate_content.return_value = mock_response

        # Test data
        responses = [
            "We need healthcare facilities",
            "Education quality is poor",
            "No clinic nearby",
            "School needs repairs",
        ] * 5  # Repeat to have enough responses

        # Run extraction
        themes = self.extractor.extract_themes(responses, num_themes=5)

        # Assertions
        self.assertGreaterEqual(len(themes), 1)
        self.assertEqual(themes[0]["theme"], "Healthcare Access")
        self.assertEqual(themes[0]["frequency"], 15)
        self.assertEqual(themes[0]["priority"], "high")

    def test_fallback_theme_extraction(self):
        """Test fallback keyword-based extraction"""
        responses = [
            "We need better health services",
            "Education is important",
            "Need water supply",
            "Health clinic required",
        ]

        # Force fallback by providing invalid JSON response
        themes = self.extractor._fallback_theme_extraction(responses, num_themes=5)

        self.assertIsInstance(themes, list)
        # Should identify health theme
        health_themes = [t for t in themes if t["category"] == "health"]
        self.assertGreater(len(health_themes), 0)


@pytest.mark.django_db
class TestNeedsExtractor(TestCase):
    """Test NeedsExtractor service"""

    def setUp(self):
        """Set up test fixtures"""
        cache.clear()
        self.extractor = NeedsExtractor()

    @patch("mana.ai_services.needs_extractor.GeminiAIEngine")
    def test_extract_needs(self, mock_gemini):
        """Test needs extraction from responses"""
        # Mock AI response
        mock_response = MagicMock()
        mock_response.text = json.dumps(
            {
                "health": {
                    "priority": "HIGH",
                    "needs": ["Build health clinic", "Hire doctor"],
                    "urgency": 0.85,
                    "beneficiaries": 2500,
                    "category_score": 0.9,
                    "key_mentions": 15,
                },
                "education": {
                    "priority": "MEDIUM",
                    "needs": ["Repair school", "Add teachers"],
                    "urgency": 0.6,
                    "beneficiaries": 800,
                    "category_score": 0.75,
                    "key_mentions": 8,
                },
            }
        )

        mock_gemini.return_value.model.generate_content.return_value = mock_response

        # Test data
        responses = [
            "We urgently need a health clinic",
            "School building needs repairs",
            "No doctor in our barangay",
        ] * 10

        # Run extraction
        needs = self.extractor.extract_needs(responses, context="Test Community")

        # Assertions
        self.assertIn("health", needs)
        self.assertEqual(needs["health"]["priority"], "HIGH")
        self.assertGreaterEqual(needs["health"]["urgency"], 0.8)
        self.assertGreater(needs["health"]["beneficiaries"], 0)

    def test_rank_needs_by_priority(self):
        """Test needs ranking algorithm"""
        needs = {
            "health": {
                "priority": "HIGH",
                "needs": ["Build clinic"],
                "urgency": 0.9,
                "beneficiaries": 3000,
                "category_score": 0.85,
            },
            "education": {
                "priority": "MEDIUM",
                "needs": ["Repair school"],
                "urgency": 0.5,
                "beneficiaries": 500,
                "category_score": 0.6,
            },
        }

        ranked = self.extractor.rank_needs_by_priority(needs)

        # Assertions
        self.assertEqual(len(ranked), 2)
        # Health should be ranked higher
        self.assertEqual(ranked[0]["category"], "health")
        self.assertGreater(ranked[0]["composite_score"], ranked[1]["composite_score"])

    def test_generate_prioritization_matrix(self):
        """Test prioritization matrix generation"""
        needs = {
            "health": {
                "priority": "HIGH",
                "needs": ["Build clinic"],
                "urgency": 0.9,
                "beneficiaries": 3000,
                "category_score": 0.9,
            },
            "water": {
                "priority": "LOW",
                "needs": ["Improve drainage"],
                "urgency": 0.3,
                "beneficiaries": 200,
                "category_score": 0.4,
            },
        }

        matrix = self.extractor.generate_needs_prioritization_matrix(needs)

        # Assertions
        self.assertIn("quick_wins", matrix)
        self.assertIn("strategic_projects", matrix)
        self.assertIn("fill_ins", matrix)
        self.assertIn("hard_slogs", matrix)


@pytest.mark.django_db
class TestReportGenerator(TestCase):
    """Test AssessmentReportGenerator service"""

    def setUp(self):
        """Set up test fixtures"""
        cache.clear()

        # Create minimal test setup
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.generator = AssessmentReportGenerator()

    def test_format_needs_for_report(self):
        """Test needs formatting for report"""
        needs = {
            "health": {
                "priority": "HIGH",
                "needs": ["Build clinic", "Hire doctor", "Medicine supply"],
                "beneficiaries": 2500,
            },
            "education": {
                "priority": "MEDIUM",
                "needs": ["Repair school", "Add teachers"],
                "beneficiaries": 800,
            },
        }

        formatted = self.generator._format_needs_for_report(needs)

        self.assertIn("Health [HIGH]", formatted)
        self.assertIn("2500 people", formatted)

    def test_format_themes_for_report(self):
        """Test themes formatting for report"""
        themes = [
            {
                "theme": "Healthcare Access",
                "frequency": 15,
                "priority": "high",
            },
            {
                "theme": "Education Quality",
                "frequency": 10,
                "priority": "medium",
            },
        ]

        formatted = self.generator._format_themes_for_report(themes)

        self.assertIn("Healthcare Access", formatted)
        self.assertIn("15x", formatted)


@pytest.mark.django_db
class TestCulturalValidator(TestCase):
    """Test BangsomoroCulturalValidator service"""

    def setUp(self):
        """Set up test fixtures"""
        cache.clear()
        self.validator = BangsomoroCulturalValidator()

    def test_quick_scan_prohibited_terms(self):
        """Test quick scan for prohibited terms"""
        text_with_issues = "The tribal community needs development assistance."

        issues = self.validator._quick_scan_for_issues(text_with_issues)

        self.assertGreater(len(issues), 0)
        self.assertEqual(issues[0]["type"], "terminology")
        self.assertIn("tribal", issues[0]["text"])

    def test_validate_needs_list(self):
        """Test validation of needs list"""
        needs = [
            "Improve healthcare access",  # Good
            "Support tribal leadership",  # Contains prohibited term
            "Build community center",  # Good
        ]

        result = self.validator.validate_needs_list(needs)

        self.assertFalse(result["valid"])
        self.assertEqual(result["flagged_count"], 1)
        self.assertLess(result["score"], 1.0)

    def test_validate_appropriate_content(self):
        """Test validation of culturally appropriate content"""
        appropriate_text = """
        This assessment was conducted in the Bangsamoro community of Balangasan.
        Community leaders and elders participated in the workshop.
        The assessment respects Islamic values and Maguindanao traditions.
        """

        # For this test, we'll just check quick scan
        issues = self.validator._quick_scan_for_issues(appropriate_text)

        # Should have no issues from quick scan
        self.assertEqual(len(issues), 0)

    def test_generate_compliance_report(self):
        """Test compliance report generation"""
        validation_results = {
            "score": 0.75,
            "appropriate": False,
            "issues": [
                {
                    "type": "terminology",
                    "severity": "high",
                    "text": "tribal",
                    "explanation": "Use 'community' instead",
                }
            ],
            "suggestions": [
                {
                    "original": "tribal",
                    "recommended": "community-based",
                    "reason": "More respectful terminology",
                }
            ],
            "strengths": ["Respectful language overall"],
        }

        report = self.validator.generate_cultural_compliance_report(validation_results)

        self.assertIn("CULTURAL SENSITIVITY COMPLIANCE REPORT", report)
        self.assertIn("Overall Score", report)
        self.assertIn("NEEDS REVISION", report)  # Because appropriate=False
        self.assertIn("ISSUES IDENTIFIED", report)


@pytest.mark.django_db
class TestIntegration(TestCase):
    """Integration tests for AI services working together"""

    def setUp(self):
        """Set up test fixtures"""
        cache.clear()

        self.analyzer = ResponseAnalyzer()
        self.theme_extractor = ThemeExtractor()
        self.needs_extractor = NeedsExtractor()
        self.validator = BangsomoroCulturalValidator()

    @patch("mana.ai_services.response_analyzer.GeminiAIEngine")
    @patch("mana.ai_services.theme_extractor.GeminiAIEngine")
    @patch("mana.ai_services.needs_extractor.GeminiAIEngine")
    def test_full_analysis_workflow(
        self, mock_needs_ai, mock_theme_ai, mock_analysis_ai
    ):
        """Test complete analysis workflow"""
        # Mock responses for all services
        mock_analysis_ai.return_value.model.generate_content.return_value.text = (
            json.dumps(
                {
                    "summary": "Health is top priority",
                    "key_points": ["Clinic needed", "Medicine shortage"],
                    "sentiment": "concerned",
                    "action_items": ["Build clinic"],
                    "confidence": 0.85,
                }
            )
        )

        mock_theme_ai.return_value.model.generate_content.return_value.text = (
            json.dumps(
                [
                    {
                        "theme": "Healthcare",
                        "frequency": 20,
                        "example_quotes": ["Need clinic"],
                        "sub_themes": ["Access", "Quality"],
                        "priority": "high",
                        "category": "health",
                    }
                ]
            )
        )

        mock_needs_ai.return_value.model.generate_content.return_value.text = (
            json.dumps(
                {
                    "health": {
                        "priority": "HIGH",
                        "needs": ["Build clinic"],
                        "urgency": 0.9,
                        "beneficiaries": 2500,
                        "category_score": 0.9,
                        "key_mentions": 20,
                    }
                }
            )
        )

        # Test data
        test_responses = [
            "We need better healthcare",
            "No clinic in our barangay",
            "Medicine is expensive",
        ] * 5

        # Run full workflow
        analysis = self.analyzer.analyze_question_responses(
            "What are community needs?", test_responses
        )
        themes = self.theme_extractor.extract_themes(test_responses)
        needs = self.needs_extractor.extract_needs(test_responses)

        # Validate results
        validation = self.validator.validate_needs_list(needs.get("health", {}).get("needs", []))

        # Assertions
        self.assertIn("summary", analysis)
        self.assertGreater(len(themes), 0)
        self.assertIn("health", needs)
        self.assertTrue(validation["valid"])  # Should be valid (no prohibited terms)


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
