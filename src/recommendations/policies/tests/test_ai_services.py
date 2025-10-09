"""
Tests for Policy AI Services

Tests for:
- Evidence gathering
- Policy generation
- Impact simulation
- Compliance checking
"""

import pytest

pytest.skip(
    "Policy AI service tests require external embedding/AI dependencies.",
    allow_module_level=True,
)

import json
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from django.test import TestCase

from recommendations.policies.ai_services import (
    CrossModuleEvidenceGatherer,
    PolicyGenerator,
    PolicyImpactSimulator,
    RegulatoryComplianceChecker,
)


class TestEvidenceGatherer(TestCase):
    """Tests for CrossModuleEvidenceGatherer"""

    def setUp(self):
        """Set up test fixtures"""
        self.gatherer = CrossModuleEvidenceGatherer()

    @patch('recommendations.policies.ai_services.evidence_gatherer.get_similarity_search_service')
    def test_gather_evidence(self, mock_search_service):
        """Test evidence gathering from multiple modules"""
        # Mock search service
        mock_service = MagicMock()
        mock_service.search_assessments.return_value = [
            {'id': 1, 'similarity': 0.85, 'metadata': {'title': 'Assessment 1'}},
            {'id': 2, 'similarity': 0.75, 'metadata': {'title': 'Assessment 2'}}
        ]
        mock_service.search_communities.return_value = [
            {'id': 1, 'similarity': 0.80, 'metadata': {'name': 'Community 1'}}
        ]
        mock_service.search_policies.return_value = []
        mock_search_service.return_value = mock_service

        # Test gathering evidence
        evidence = self.gatherer.gather_evidence(
            policy_topic="Healthcare access",
            modules=['assessments', 'communities']
        )

        # Assertions
        self.assertIn('mana_assessments', evidence)
        self.assertIn('community_data', evidence)
        self.assertEqual(len(evidence['mana_assessments']), 2)
        self.assertEqual(len(evidence['community_data']), 1)
        self.assertEqual(evidence['total_citations'], 3)

    @patch('recommendations.policies.ai_services.evidence_gatherer.GeminiService')
    def test_synthesize_evidence(self, mock_gemini):
        """Test AI evidence synthesis"""
        # Mock Gemini response
        mock_service = MagicMock()
        mock_service.generate_text.return_value = {
            'success': True,
            'text': json.dumps({
                'synthesis': 'Evidence shows strong need for healthcare...',
                'key_findings': ['Finding 1', 'Finding 2'],
                'data_gaps': ['Gap 1'],
                'strength_of_evidence': 'strong',
                'confidence_score': 0.85
            })
        }
        mock_gemini.return_value = mock_service

        # Test synthesis
        evidence = {
            'mana_assessments': [{'id': 1}],
            'community_data': [{'id': 1}],
            'total_citations': 2
        }
        synthesis = self.gatherer.synthesize_evidence(evidence, "Healthcare")

        # Assertions
        self.assertEqual(synthesis['strength_of_evidence'], 'strong')
        self.assertEqual(synthesis['confidence_score'], 0.85)
        self.assertEqual(len(synthesis['key_findings']), 2)

    def test_get_evidence_stats(self):
        """Test evidence statistics calculation"""
        evidence = {
            'mana_assessments': [
                {'similarity': 0.8},
                {'similarity': 0.7}
            ],
            'community_data': [
                {'similarity': 0.9}
            ],
            'project_outcomes': [],
            'total_citations': 3
        }

        stats = self.gatherer.get_evidence_stats(evidence)

        self.assertEqual(stats['total_sources'], 3)
        self.assertEqual(stats['by_module']['mana_assessments'], 2)
        self.assertEqual(stats['by_module']['community_data'], 1)
        self.assertAlmostEqual(stats['avg_similarity'], 0.8, places=1)


class TestPolicyGenerator(TestCase):
    """Tests for PolicyGenerator"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = PolicyGenerator()

    @patch('recommendations.policies.ai_services.policy_generator.get_evidence_gatherer')
    @patch('recommendations.policies.ai_services.policy_generator.GeminiService')
    def test_generate_policy_recommendation(self, mock_gemini, mock_gatherer):
        """Test AI policy generation"""
        # Mock evidence gatherer
        mock_gatherer_instance = MagicMock()
        mock_gatherer_instance.gather_evidence.return_value = {
            'total_citations': 5
        }
        mock_gatherer_instance.synthesize_evidence.return_value = {
            'synthesis': 'Strong evidence...',
            'strength_of_evidence': 'strong'
        }
        mock_gatherer.return_value = mock_gatherer_instance

        # Mock Gemini
        mock_gemini_instance = MagicMock()
        mock_gemini_instance.generate_text.return_value = {
            'success': True,
            'text': json.dumps({
                'title': 'Healthcare Access Expansion Program',
                'executive_summary': 'This policy aims to...',
                'problem_statement': 'Many communities lack...',
                'estimated_cost': 5000000,
                'citations': ['Source 1', 'Source 2']
            }),
            'cost': 0.05,
            'tokens_used': 2000
        }
        mock_gemini.return_value = mock_gemini_instance

        # Test policy generation
        policy = self.generator.generate_policy_recommendation(
            issue="Healthcare access for coastal communities",
            evidence=None,
            category='social_development'
        )

        # Assertions
        self.assertIn('title', policy)
        self.assertIn('executive_summary', policy)
        self.assertTrue(policy.get('generated_by_ai'))
        self.assertEqual(policy['evidence_sources_count'], 5)

    @patch('recommendations.policies.ai_services.policy_generator.GeminiService')
    def test_refine_policy(self, mock_gemini):
        """Test policy refinement based on feedback"""
        # Mock Gemini
        mock_service = MagicMock()
        mock_service.generate_text.return_value = {
            'success': True,
            'text': json.dumps({
                'title': 'Refined Policy Title',
                'executive_summary': 'Refined summary...'
            })
        }
        mock_gemini.return_value = mock_service

        # Test refinement
        policy_data = {
            'title': 'Original Policy',
            'executive_summary': 'Original summary'
        }
        refined = self.generator.refine_policy(
            policy_data=policy_data,
            feedback="Please add more budget details"
        )

        # Assertions
        self.assertTrue(refined.get('refined'))
        self.assertIn('Refined', refined['title'])

    @patch('recommendations.policies.ai_services.policy_generator.GeminiService')
    def test_generate_quick_policy(self, mock_gemini):
        """Test quick policy draft generation"""
        # Mock Gemini
        mock_service = MagicMock()
        mock_service.generate_text.return_value = {
            'success': True,
            'text': json.dumps({
                'title': 'Quick Policy',
                'executive_summary': 'Quick summary'
            })
        }
        mock_gemini.return_value = mock_service

        # Test quick policy
        policy = self.generator.generate_quick_policy(
            issue="Emergency response",
            template_type='urgent'
        )

        # Assertions
        self.assertTrue(policy.get('quick_draft'))
        self.assertEqual(policy['template_type'], 'urgent')


class TestImpactSimulator(TestCase):
    """Tests for PolicyImpactSimulator"""

    def setUp(self):
        """Set up test fixtures"""
        self.simulator = PolicyImpactSimulator()

    @patch('recommendations.policies.ai_services.impact_simulator.GeminiService')
    def test_simulate_impact(self, mock_gemini):
        """Test policy impact simulation"""
        # Mock Gemini
        mock_service = MagicMock()
        mock_service.generate_text.return_value = {
            'success': True,
            'text': json.dumps({
                'scenario_name': 'realistic',
                'beneficiaries_reached': 5000,
                'cost_per_beneficiary': 250,
                'timeline_months': 12,
                'success_probability': 0.70,
                'risk_factors': ['Risk 1', 'Risk 2'],
                'critical_success_factors': ['CSF 1', 'CSF 2'],
                'impact_metrics': {
                    'economic_impact_php': 1000000,
                    'social_impact_score': 75,
                    'community_satisfaction': 80,
                    'sustainability_score': 70
                }
            })
        }
        mock_gemini.return_value = mock_service

        # Test simulation
        policy_dict = {
            'id': 'test-id',
            'title': 'Test Policy',
            'description': 'Test description',
            'estimated_cost': 1000000,
            'target_communities_count': 5
        }
        result = self.simulator.simulate_impact(
            policy_data=policy_dict,
            scenarios=['realistic'],
            use_cache=False
        )

        # Assertions
        self.assertIn('scenarios', result)
        self.assertIn('realistic', result['scenarios'])
        scenario = result['scenarios']['realistic']
        self.assertEqual(scenario['beneficiaries_reached'], 5000)
        self.assertEqual(scenario['cost_per_beneficiary'], 250)

    def test_compare_scenarios(self):
        """Test scenario comparison"""
        scenario_results = {
            'best_case': {
                'beneficiaries_reached': 10000,
                'cost_per_beneficiary': 200,
                'success_probability': 0.85
            },
            'realistic': {
                'beneficiaries_reached': 7000,
                'cost_per_beneficiary': 250,
                'success_probability': 0.70
            },
            'worst_case': {
                'beneficiaries_reached': 3000,
                'cost_per_beneficiary': 400,
                'success_probability': 0.45
            }
        }

        comparison = self.simulator._compare_scenarios(scenario_results)

        # Assertions
        self.assertEqual(comparison['best_reach'], 'best_case')
        self.assertEqual(comparison['best_efficiency'], 'best_case')

    def test_generate_fallback_scenario(self):
        """Test fallback scenario generation when AI fails"""
        policy_dict = {
            'estimated_cost': 1000000,
            'target_communities_count': 5
        }
        scenario_config = {
            'funding_multiplier': 1.0,
            'efficiency_multiplier': 1.2,
            'success_probability': 0.85
        }

        fallback = self.simulator._generate_fallback_scenario(
            policy_dict,
            'best_case',
            scenario_config
        )

        # Assertions
        self.assertTrue(fallback.get('fallback'))
        self.assertEqual(fallback['scenario_name'], 'best_case')
        self.assertGreater(fallback['beneficiaries_reached'], 0)


class TestComplianceChecker(TestCase):
    """Tests for RegulatoryComplianceChecker"""

    def setUp(self):
        """Set up test fixtures"""
        self.checker = RegulatoryComplianceChecker()

    @patch('recommendations.policies.ai_services.compliance_checker.GeminiService')
    def test_check_compliance(self, mock_gemini):
        """Test BARMM compliance checking"""
        # Mock Gemini
        mock_service = MagicMock()
        mock_service.generate_text.return_value = {
            'success': True,
            'text': json.dumps({
                'compliant': True,
                'compliance_score': 0.92,
                'relevant_laws': ['R.A. 11054', 'R.A. 11310'],
                'compliance_details': {
                    'R.A. 11054': {
                        'compliant': True,
                        'notes': 'Aligns with BOL provisions'
                    }
                },
                'conflicts': [],
                'recommendations': ['Consider adding FPIC requirement'],
                'risk_level': 'low',
                'risk_explanation': 'Minimal legal risks identified'
            }),
            'cost': 0.03
        }
        mock_gemini.return_value = mock_service

        # Test compliance check
        result = self.checker.check_compliance(
            policy_text="This policy aims to improve education access...",
            policy_title="Education Access Policy",
            category="education"
        )

        # Assertions
        self.assertTrue(result['compliant'])
        self.assertEqual(result['compliance_score'], 0.92)
        self.assertEqual(result['risk_level'], 'low')
        self.assertEqual(len(result['relevant_laws']), 2)

    @patch('recommendations.policies.ai_services.compliance_checker.GeminiService')
    def test_quick_compliance_check(self, mock_gemini):
        """Test quick compliance check"""
        # Mock Gemini
        mock_service = MagicMock()
        mock_service.generate_text.return_value = {
            'success': True,
            'text': json.dumps({
                'compliant': True,
                'compliance_score': 0.85,
                'concerns': ['Concern 1', 'Concern 2'],
                'risk_level': 'low'
            })
        }
        mock_gemini.return_value = mock_service

        # Test quick check
        result = self.checker.check_quick_compliance(
            policy_text="Test policy text",
            focus_area='cultural'
        )

        # Assertions
        self.assertTrue(result['compliant'])
        self.assertEqual(len(result['concerns']), 2)

    @patch('recommendations.policies.ai_services.compliance_checker.GeminiService')
    def test_get_compliance_guidelines(self, mock_gemini):
        """Test compliance guidelines retrieval"""
        # Mock Gemini
        mock_service = MagicMock()
        mock_service.generate_text.return_value = {
            'success': True,
            'text': json.dumps({
                'key_laws': ['R.A. 11054'],
                'must_haves': ['FPIC', 'Cultural sensitivity'],
                'common_pitfalls': ['Lack of consultation'],
                'best_practices': ['Engage traditional leaders']
            })
        }
        mock_gemini.return_value = mock_service

        # Test guidelines
        guidelines = self.checker.get_compliance_guidelines('education')

        # Assertions
        self.assertEqual(guidelines['category'], 'education')
        self.assertIn('key_laws', guidelines)
        self.assertIn('must_haves', guidelines)

    def test_build_legal_context(self):
        """Test legal context building"""
        context = self.checker._build_legal_context()

        # Assertions
        self.assertIn('R.A. 11054', context)
        self.assertIn('Bangsamoro Organic Law', context)
        self.assertIn('Presidential Decree No. 1083', context)

    def test_generate_fallback_compliance(self):
        """Test fallback compliance result"""
        fallback = self.checker._generate_fallback_compliance("Test policy")

        # Assertions
        self.assertIsNone(fallback['compliant'])
        self.assertTrue(fallback.get('fallback'))
        self.assertEqual(fallback['compliance_score'], 0.0)
        self.assertIn('manual legal review required', fallback['recommendations'][0])


# Pytest markers for integration tests
@pytest.mark.integration
class TestAIServicesIntegration(TestCase):
    """Integration tests requiring actual AI services"""

    @pytest.mark.skipif(
        not hasattr('settings', 'GOOGLE_API_KEY'),
        reason="Google API key not configured"
    )
    def test_end_to_end_policy_generation(self):
        """Test complete policy generation workflow"""
        # This test would run with actual AI services
        # Skip if API key not available
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
