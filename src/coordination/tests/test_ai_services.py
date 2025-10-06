"""
Tests for Coordination AI Services
"""

import json
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from coordination.models import (
    Organization,
    Partnership,
    StakeholderEngagement,
    StakeholderEngagementType,
    PartnershipMilestone
)
from communities.models import OBCCommunity
from common.models import Region, Province, Municipality, Barangay
from coordination.ai_services.stakeholder_matcher import StakeholderMatcher
from coordination.ai_services.partnership_predictor import PartnershipPredictor
from coordination.ai_services.meeting_intelligence import MeetingIntelligence
from coordination.ai_services.resource_optimizer import ResourceOptimizer

User = get_user_model()


class StakeholderMatcherTestCase(TestCase):
    """Test AI stakeholder matching functionality"""

    def setUp(self):
        """Set up test data"""
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@oobc.gov.ph',
            password='testpass123'
        )

        # Create geographic hierarchy
        self.region = Region.objects.create(
            name='Zamboanga Peninsula',
            code='09'
        )

        self.province = Province.objects.create(
            name='Zamboanga del Sur',
            code='ZDS',
            region=self.region
        )

        self.municipality = Municipality.objects.create(
            name='Pagadian City',
            code='PAG',
            province=self.province
        )

        self.barangay = Barangay.objects.create(
            name='Balangasan',
            code='BAL',
            municipality=self.municipality
        )

        self.community = OBCCommunity.objects.create(
            name='Balangasan OBC',
            barangay=self.barangay,
            estimated_obc_population=5000,
            primary_ethnolinguistic_group='kagan_kalagan'
        )

        # Create organizations
        self.org1 = Organization.objects.create(
            name='Health NGO',
            organization_type='ngo',
            areas_of_expertise='Health, Medical Services, Clinic Operations',
            geographic_coverage='Zamboanga del Sur, Zamboanga del Norte',
            annual_budget=Decimal('5000000'),
            staff_count=25,
            is_active=True,
            partnership_status='active',
            created_by=self.user
        )

        self.org2 = Organization.objects.create(
            name='Education Foundation',
            organization_type='ngo',
            areas_of_expertise='Education, Training, Scholarship Programs',
            geographic_coverage='Region IX',
            annual_budget=Decimal('3000000'),
            staff_count=15,
            is_active=True,
            partnership_status='active',
            created_by=self.user
        )

        self.matcher = StakeholderMatcher()

    def test_find_matching_stakeholders(self):
        """Test finding matching stakeholders for a community need"""
        matches = self.matcher.find_matching_stakeholders(
            community_id=self.community.id,
            need_category='Health'
        )

        self.assertIsInstance(matches, list)
        self.assertGreater(len(matches), 0)

        # Health NGO should be first match
        top_match = matches[0]
        self.assertEqual(top_match['stakeholder'].id, self.org1.id)
        self.assertGreater(top_match['match_score'], 0.6)
        self.assertIn('sector', top_match['matching_criteria'])

    def test_geographic_proximity_scoring(self):
        """Test geographic proximity scoring"""
        score = self.matcher._calculate_geographic_score(self.community, self.org1)
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 0.3)

    def test_sector_alignment_scoring(self):
        """Test sector alignment scoring"""
        # Health match
        health_score = self.matcher._calculate_sector_score(self.org1, 'Health')
        self.assertEqual(health_score, 0.4)  # Direct match

        # No match
        no_match_score = self.matcher._calculate_sector_score(self.org1, 'Agriculture')
        self.assertEqual(no_match_score, 0.0)

    @patch('coordination.ai_services.stakeholder_matcher.GeminiService')
    def test_recommend_partnerships(self, mock_gemini):
        """Test multi-stakeholder partnership recommendations"""
        # Mock AI response
        mock_gemini.return_value.generate_text.return_value = json.dumps({
            'synergy_score': 85,
            'strengths': ['Complementary expertise', 'Broad coverage'],
            'gaps': ['Limited agriculture expertise'],
            'roles': {
                str(self.org1.id): 'Health services provider',
                str(self.org2.id): 'Training and capacity building'
            },
            'success_factors': ['Strong partnership history', 'Geographic alignment']
        })

        recommendation = self.matcher.recommend_partnerships(
            stakeholder_ids=[str(self.org1.id), str(self.org2.id)],
            community_id=self.community.id,
            need_category='Health and Education'
        )

        self.assertIn('synergy_score', recommendation)
        self.assertEqual(recommendation['synergy_score'], 85)
        self.assertIn('stakeholders', recommendation)


class PartnershipPredictorTestCase(TestCase):
    """Test partnership success prediction"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Create geographic data
        self.region = Region.objects.create(
            name='Zamboanga Peninsula',
            code='09'
        )

        self.province = Province.objects.create(
            name='Zamboanga del Sur',
            code='ZDS',
            region=self.region
        )

        self.municipality = Municipality.objects.create(
            name='Pagadian City',
            code='PAG',
            province=self.province
        )

        self.barangay = Barangay.objects.create(
            name='Test Barangay',
            code='TST',
            municipality=self.municipality
        )

        self.community = OBCCommunity.objects.create(
            name='Test Community',
            barangay=self.barangay,
            estimated_obc_population=3000
        )

        # Create organization with track record
        self.org = Organization.objects.create(
            name='Test Org',
            organization_type='ngo',
            areas_of_expertise='Health, Education',
            geographic_coverage='Zamboanga del Sur',
            annual_budget=Decimal('5000000'),
            staff_count=20,
            is_active=True,
            partnership_status='active',
            created_by=self.user
        )

        # Create past partnerships
        for i in range(3):
            Partnership.objects.create(
                title=f'Partnership {i+1}',
                partnership_type='moa',
                description='Test partnership',
                objectives='Test objectives',
                scope='Test scope',
                lead_organization=self.org,
                status='completed',
                created_by=self.user
            )

        self.predictor = PartnershipPredictor()

    def test_predict_success(self):
        """Test partnership success prediction"""
        prediction = self.predictor.predict_success(
            stakeholder_id=str(self.org.id),
            community_id=self.community.id,
            project_type='Health',
            budget=Decimal('1000000')
        )

        self.assertIn('success_probability', prediction)
        self.assertIn('confidence_level', prediction)
        self.assertIn('risk_factors', prediction)
        self.assertIn('success_factors', prediction)
        self.assertIn('recommendations', prediction)

        # Check probability is valid
        self.assertGreaterEqual(prediction['success_probability'], 0)
        self.assertLessEqual(prediction['success_probability'], 1)

    def test_extract_features(self):
        """Test feature extraction for prediction"""
        features = self.predictor._extract_features(
            stakeholder_id=str(self.org.id),
            community_id=self.community.id,
            project_type='Health',
            budget=Decimal('1000000')
        )

        self.assertEqual(features['stakeholder_name'], 'Test Org')
        self.assertEqual(features['past_projects_count'], 3)
        self.assertEqual(features['completed_projects_count'], 3)
        self.assertEqual(features['success_rate'], 100.0)
        self.assertTrue(features['geographic_match'])
        self.assertTrue(features['sector_match'])

    def test_analyze_partnership_portfolio(self):
        """Test portfolio analysis"""
        analysis = self.predictor.analyze_partnership_portfolio(str(self.org.id))

        self.assertIn('organization', analysis)
        self.assertIn('total_partnerships', analysis)
        self.assertIn('success_rate', analysis)
        self.assertEqual(analysis['total_partnerships'], 3)
        self.assertEqual(analysis['completed_partnerships'], 3)


class MeetingIntelligenceTestCase(TestCase):
    """Test meeting intelligence and summarization"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Create geographic data
        self.region = Region.objects.create(
            name='Zamboanga Peninsula',
            code='09'
        )

        self.province = Province.objects.create(
            name='Zamboanga del Sur',
            code='ZDS',
            region=self.region
        )

        self.municipality = Municipality.objects.create(
            name='Pagadian City',
            code='PAG',
            province=self.province
        )

        self.barangay = Barangay.objects.create(
            name='Test Barangay',
            code='TST',
            municipality=self.municipality
        )

        self.community = OBCCommunity.objects.create(
            name='Test Community',
            barangay=self.barangay,
            estimated_obc_population=3000
        )

        # Create engagement type
        self.engagement_type = StakeholderEngagementType.objects.create(
            name='Coordination Meeting',
            category='meeting',
            description='Regular coordination meeting'
        )

        # Create meeting
        self.meeting = StakeholderEngagement.objects.create(
            title='Q1 Coordination Meeting',
            engagement_type=self.engagement_type,
            description='Quarterly coordination meeting',
            objectives='Review progress and plan next quarter',
            community=self.community,
            planned_date=timezone.now(),
            venue='Community Hall',
            address='Balangasan, Pagadian City',
            target_participants=20,
            actual_participants=18,
            stakeholder_groups='LGU, NGOs, Community Leaders',
            methodology='Participatory discussion',
            meeting_minutes='Discussed health and education needs. Agreed to form working groups.',
            key_outcomes='Formed 2 working groups, scheduled next meeting',
            action_items='1. Form health working group\n2. Schedule skills training\n3. Follow up with LGU',
            created_by=self.user,
            status='completed'
        )

        self.intelligence = MeetingIntelligence()

    @patch('coordination.ai_services.meeting_intelligence.GeminiService')
    def test_summarize_meeting(self, mock_gemini):
        """Test meeting summarization"""
        # Mock AI response
        mock_gemini.return_value.generate_text.return_value = json.dumps({
            'summary': 'Productive coordination meeting with 18 participants.',
            'key_decisions': ['Form health working group', 'Schedule skills training'],
            'action_items': [
                {'task': 'Form health working group', 'owner': 'John Doe', 'deadline': '2025-10-15'},
                {'task': 'Schedule skills training', 'owner': 'Jane Smith', 'deadline': '2025-10-20'}
            ],
            'attendees_summary': '18 of 20 expected participants attended (90%)',
            'next_steps': ['Convene working groups', 'Prepare training materials'],
            'sentiment': 'positive',
            'topics_discussed': ['Health needs', 'Education', 'Skills training']
        })

        summary = self.intelligence.summarize_meeting(str(self.meeting.id))

        self.assertIn('summary', summary)
        self.assertIn('key_decisions', summary)
        self.assertIn('action_items', summary)
        self.assertEqual(summary['sentiment'], 'positive')

    def test_extract_action_items_simple(self):
        """Test simple action item extraction"""
        items = self.intelligence._extract_action_items_simple(self.meeting.action_items)

        self.assertGreater(len(items), 0)
        self.assertIn('Form health working group', items[0])

    def test_analyze_meeting_effectiveness(self):
        """Test meeting effectiveness analysis"""
        analysis = self.intelligence.analyze_meeting_effectiveness(str(self.meeting.id))

        self.assertIn('effectiveness_score', analysis)
        self.assertIn('participation_rate', analysis)
        self.assertIn('outcome_quality', analysis)

        # Check participation rate
        expected_rate = 18 / 20
        self.assertEqual(analysis['participation_rate'], expected_rate)

    def test_generate_meeting_report(self):
        """Test meeting report generation"""
        report = self.intelligence.generate_meeting_report(str(self.meeting.id))

        self.assertIn('Meeting Report', report)
        self.assertIn(self.meeting.title, report)
        self.assertIn('Executive Summary', report)


class ResourceOptimizerTestCase(TestCase):
    """Test resource optimization"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Create multiple communities
        self.region = Region.objects.create(
            name='Zamboanga Peninsula',
            code='09'
        )

        self.province = Province.objects.create(
            name='Zamboanga del Sur',
            code='ZDS',
            region=self.region
        )

        self.municipality = Municipality.objects.create(
            name='Pagadian City',
            code='PAG',
            province=self.province
        )

        self.communities = []
        for i in range(3):
            barangay = Barangay.objects.create(
                name=f'Barangay {i+1}',
                code=f'BRG{i+1}',
                municipality=self.municipality
            )
            community = OBCCommunity.objects.create(
                name=f'Community {i+1}',
                barangay=barangay,
                estimated_obc_population=5000 + (i * 2000)
            )
            self.communities.append(community)

        self.optimizer = ResourceOptimizer()

    def test_optimize_budget_allocation(self):
        """Test budget allocation optimization"""
        community_ids = [c.id for c in self.communities]
        total_budget = Decimal('10000000')

        result = self.optimizer.optimize_budget_allocation(
            total_budget=total_budget,
            communities=community_ids
        )

        self.assertIn('allocations', result)
        self.assertIn('optimization_criteria', result)
        self.assertIn('recommendations', result)

        # Check allocations sum to total
        allocated_sum = sum(a['allocated_budget'] for a in result['allocations'])
        self.assertAlmostEqual(allocated_sum, float(total_budget), places=2)

        # Check all communities received allocation
        self.assertEqual(len(result['allocations']), len(self.communities))

    def test_calculate_community_priority(self):
        """Test community priority calculation"""
        weights = {
            'population': 0.3,
            'needs_severity': 0.3,
            'accessibility': 0.2,
            'prior_investment': 0.2
        }

        score = self.optimizer._calculate_community_priority(
            self.communities[0],
            weights
        )

        self.assertGreater(score, 0)
        self.assertLessEqual(score, 1.0)

    def test_analyze_resource_utilization(self):
        """Test resource utilization analysis"""
        # Create organization with partnerships
        org = Organization.objects.create(
            name='Test Org',
            organization_type='ngo',
            annual_budget=Decimal('10000000'),
            is_active=True,
            partnership_status='active',
            created_by=self.user
        )

        # Create active partnerships
        Partnership.objects.create(
            title='Partnership 1',
            partnership_type='moa',
            description='Test',
            objectives='Test',
            scope='Test',
            lead_organization=org,
            partner_contribution=Decimal('6000000'),
            status='active',
            created_by=self.user
        )

        analysis = self.optimizer.analyze_resource_utilization(str(org.id))

        self.assertIn('total_committed_budget', analysis)
        self.assertIn('utilization_rate', analysis)
        self.assertIn('capacity_status', analysis)

        # Utilization should be 60%
        self.assertAlmostEqual(analysis['utilization_rate'], 0.6, places=1)


class CeleryTasksTestCase(TestCase):
    """Test Celery background tasks"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    @patch('coordination.tasks.MeetingIntelligence')
    def test_analyze_meeting_task(self, mock_intelligence):
        """Test meeting analysis task"""
        from coordination.tasks import analyze_meeting

        # Mock service
        mock_service = MagicMock()
        mock_service.summarize_meeting.return_value = {'summary': 'Test summary'}
        mock_service.auto_create_tasks.return_value = []
        mock_intelligence.return_value = mock_service

        result = analyze_meeting('test-meeting-id')

        self.assertIn('meeting_id', result)
        self.assertEqual(result['meeting_id'], 'test-meeting-id')

    @patch('coordination.tasks.StakeholderMatcher')
    def test_match_stakeholders_task(self, mock_matcher):
        """Test stakeholder matching task"""
        from coordination.tasks import match_stakeholders_for_communities

        # Mock service
        mock_service = MagicMock()
        mock_service.find_matching_stakeholders.return_value = []
        mock_matcher.return_value = mock_service

        # Mock communities
        with patch('coordination.tasks.OBCCommunity') as mock_community:
            mock_community.objects.filter.return_value.select_related.return_value = []

            result = match_stakeholders_for_communities()

            self.assertIn('communities_processed', result)
            self.assertIn('matches_generated', result)
