"""
Policy Impact Simulator

Simulates potential impact of policy recommendations under different scenarios.
Uses AI to model outcomes based on historical data and similar policies.
"""

import json
import logging
from decimal import Decimal
from typing import Dict, List, Optional

from django.core.cache import cache

from ai_assistant.services import GeminiService

logger = logging.getLogger(__name__)


class PolicyImpactSimulator:
    """Simulate policy impact under different scenarios"""

    SCENARIOS = {
        'best_case': {
            'name': 'Best Case Scenario',
            'description': 'Optimal conditions: full funding, ideal implementation, strong stakeholder buy-in',
            'funding_multiplier': 1.0,
            'efficiency_multiplier': 1.2,
            'success_probability': 0.85,
        },
        'realistic': {
            'name': 'Realistic Scenario',
            'description': 'Typical conditions: normal constraints, moderate funding, standard implementation',
            'funding_multiplier': 0.85,
            'efficiency_multiplier': 1.0,
            'success_probability': 0.70,
        },
        'worst_case': {
            'name': 'Worst Case Scenario',
            'description': 'Challenging conditions: budget cuts, implementation delays, resistance',
            'funding_multiplier': 0.60,
            'efficiency_multiplier': 0.75,
            'success_probability': 0.45,
        },
        'pilot': {
            'name': 'Pilot Program',
            'description': 'Limited rollout: test implementation in 2-3 communities first',
            'funding_multiplier': 0.30,
            'efficiency_multiplier': 1.1,
            'success_probability': 0.75,
        },
    }

    def __init__(self):
        """Initialize impact simulator"""
        self.gemini = GeminiService(temperature=0.5)  # Balanced for scenario analysis

    def simulate_impact(
        self,
        policy_data: Dict,
        scenarios: Optional[List[str]] = None,
        use_cache: bool = True
    ) -> Dict:
        """
        Simulate policy impact under different scenarios

        Args:
            policy_data: Policy recommendation dict or UUID
            scenarios: List of scenario names (default: all scenarios)
            use_cache: Whether to cache results (default: True)

        Returns:
            {
                'policy_id': '...',
                'policy_title': '...',
                'scenarios': {
                    'best_case': {...},
                    'realistic': {...},
                    'worst_case': {...},
                    'pilot': {...}
                },
                'comparison': {...},
                'recommendation': '...'
            }
        """
        # Handle both dict and UUID inputs
        if isinstance(policy_data, str):
            # UUID provided, fetch from database
            from recommendations.policy_tracking.models import PolicyRecommendation
            try:
                policy = PolicyRecommendation.objects.get(id=policy_data)
                policy_dict = {
                    'id': str(policy.id),
                    'title': policy.title,
                    'description': policy.description,
                    'proposed_solution': policy.proposed_solution,
                    'estimated_cost': float(policy.estimated_cost or 0),
                    'target_communities_count': policy.target_communities.count(),
                }
            except PolicyRecommendation.DoesNotExist:
                logger.error(f"Policy {policy_data} not found")
                return {'error': 'Policy not found'}
        else:
            policy_dict = policy_data

        logger.info(f"Simulating impact for: {policy_dict.get('title')}")

        # Check cache
        cache_key = f"policy_impact_{policy_dict.get('id')}_{'-'.join(scenarios or [])}"
        if use_cache:
            cached = cache.get(cache_key)
            if cached:
                logger.info("Returning cached impact simulation")
                return cached

        # Determine scenarios to simulate
        if scenarios is None:
            scenarios = ['best_case', 'realistic', 'worst_case', 'pilot']

        # Simulate each scenario
        scenario_results = {}
        for scenario_name in scenarios:
            if scenario_name in self.SCENARIOS:
                result = self._simulate_scenario(policy_dict, scenario_name)
                scenario_results[scenario_name] = result

        # Generate comparison and recommendation
        comparison = self._compare_scenarios(scenario_results)
        recommendation = self._generate_recommendation(scenario_results, comparison)

        # Compile final result
        final_result = {
            'policy_id': policy_dict.get('id'),
            'policy_title': policy_dict.get('title'),
            'scenarios': scenario_results,
            'comparison': comparison,
            'recommendation': recommendation,
            'simulated_at': str(timezone.now())
        }

        # Cache result
        if use_cache:
            cache.set(cache_key, final_result, timeout=86400)  # 24 hours

        logger.info("Impact simulation completed")
        return final_result

    def _simulate_scenario(
        self,
        policy_dict: Dict,
        scenario_name: str
    ) -> Dict:
        """
        Simulate a single scenario

        Returns:
            {
                'scenario_name': '...',
                'beneficiaries_reached': 5000,
                'cost_per_beneficiary': 250,
                'timeline_months': 12,
                'success_probability': 0.85,
                'risk_factors': [...],
                'critical_success_factors': [...],
                'impact_metrics': {...}
            }
        """
        scenario_config = self.SCENARIOS[scenario_name]

        # Build AI prompt for scenario simulation
        prompt = f"""
Simulate the impact of this policy recommendation under the {scenario_config['name']}:

POLICY INFORMATION:
Title: {policy_dict.get('title')}
Description: {policy_dict.get('description', 'N/A')}
Proposed Solution: {policy_dict.get('proposed_solution', 'N/A')}
Estimated Budget: PHP {policy_dict.get('estimated_cost', 0):,.2f}
Target Communities: {policy_dict.get('target_communities_count', 'Multiple')}

SCENARIO: {scenario_config['name']}
{scenario_config['description']}

Scenario Parameters:
- Funding Level: {scenario_config['funding_multiplier'] * 100:.0f}% of estimated budget
- Implementation Efficiency: {scenario_config['efficiency_multiplier'] * 100:.0f}%
- Base Success Probability: {scenario_config['success_probability'] * 100:.0f}%

TASK: Simulate the impact of implementing this policy under these conditions.

Provide realistic estimates for:
1. Beneficiaries Reached (number of people/families)
2. Cost per Beneficiary (PHP)
3. Implementation Timeline (months)
4. Success Probability (0-1, based on scenario)
5. Risk Factors (3-5 specific risks for this scenario)
6. Critical Success Factors (3-5 key factors for success)
7. Impact Metrics:
   - Economic impact (quantified)
   - Social impact (qualitative)
   - Community satisfaction (0-100)
   - Sustainability score (0-100)

Base estimates on:
- Similar policies in Bangsamoro region
- Typical implementation challenges
- Resource availability
- Community capacity

OUTPUT FORMAT: Valid JSON with structure:
{{
    "scenario_name": "{scenario_name}",
    "beneficiaries_reached": <number>,
    "cost_per_beneficiary": <number>,
    "timeline_months": <number>,
    "success_probability": <0-1>,
    "risk_factors": ["Risk 1", "Risk 2", ...],
    "critical_success_factors": ["CSF 1", "CSF 2", ...],
    "impact_metrics": {{
        "economic_impact_php": <number>,
        "social_impact_score": <0-100>,
        "community_satisfaction": <0-100>,
        "sustainability_score": <0-100>
    }}
}}
"""

        response = self.gemini.generate_text(
            prompt,
            use_cache=False,
            include_cultural_context=True
        )

        if response['success']:
            try:
                result = json.loads(response['text'])
                logger.info(f"Simulated {scenario_name}: {result.get('beneficiaries_reached')} beneficiaries")
                return result
            except json.JSONDecodeError:
                logger.error(f"Failed to parse scenario simulation for {scenario_name}")
                return self._generate_fallback_scenario(policy_dict, scenario_name, scenario_config)
        else:
            logger.error(f"Scenario simulation failed: {response.get('error')}")
            return self._generate_fallback_scenario(policy_dict, scenario_name, scenario_config)

    def _generate_fallback_scenario(
        self,
        policy_dict: Dict,
        scenario_name: str,
        scenario_config: Dict
    ) -> Dict:
        """Generate fallback estimates if AI simulation fails"""
        estimated_cost = policy_dict.get('estimated_cost', 1000000)
        target_communities = policy_dict.get('target_communities_count', 5)

        # Simple calculation-based estimates
        funding = estimated_cost * scenario_config['funding_multiplier']
        cost_per_beneficiary = 500  # Fallback estimate
        beneficiaries = int(funding / cost_per_beneficiary * scenario_config['efficiency_multiplier'])

        return {
            'scenario_name': scenario_name,
            'beneficiaries_reached': beneficiaries,
            'cost_per_beneficiary': cost_per_beneficiary,
            'timeline_months': 12 if scenario_name != 'pilot' else 6,
            'success_probability': scenario_config['success_probability'],
            'risk_factors': ['AI simulation unavailable - using fallback estimates'],
            'critical_success_factors': ['Adequate funding', 'Community engagement', 'Strong implementation team'],
            'impact_metrics': {
                'economic_impact_php': int(funding * 0.8),
                'social_impact_score': 70,
                'community_satisfaction': 65,
                'sustainability_score': 60
            },
            'fallback': True
        }

    def _compare_scenarios(self, scenario_results: Dict) -> Dict:
        """
        Compare scenarios and identify trade-offs

        Returns:
            {
                'best_reach': 'best_case',
                'best_efficiency': 'pilot',
                'best_risk_adjusted': 'realistic',
                'trade_offs': {...}
            }
        """
        if not scenario_results:
            return {}

        comparison = {
            'best_reach': None,
            'best_efficiency': None,
            'best_risk_adjusted': None,
            'trade_offs': {}
        }

        # Find best reach (most beneficiaries)
        max_beneficiaries = 0
        for scenario, result in scenario_results.items():
            beneficiaries = result.get('beneficiaries_reached', 0)
            if beneficiaries > max_beneficiaries:
                max_beneficiaries = beneficiaries
                comparison['best_reach'] = scenario

        # Find best efficiency (lowest cost per beneficiary)
        min_cost_per = float('inf')
        for scenario, result in scenario_results.items():
            cost_per = result.get('cost_per_beneficiary', float('inf'))
            if cost_per < min_cost_per:
                min_cost_per = cost_per
                comparison['best_efficiency'] = scenario

        # Find best risk-adjusted (probability × beneficiaries)
        max_risk_adjusted = 0
        for scenario, result in scenario_results.items():
            risk_adjusted = result.get('beneficiaries_reached', 0) * result.get('success_probability', 0)
            if risk_adjusted > max_risk_adjusted:
                max_risk_adjusted = risk_adjusted
                comparison['best_risk_adjusted'] = scenario

        return comparison

    def _generate_recommendation(
        self,
        scenario_results: Dict,
        comparison: Dict
    ) -> str:
        """Generate strategic recommendation based on scenarios"""
        prompt = f"""
Based on these policy impact simulations, provide a strategic recommendation:

SCENARIO RESULTS:
{json.dumps(scenario_results, indent=2)}

COMPARISON:
{json.dumps(comparison, indent=2)}

Provide a strategic recommendation (200-250 words) that:
1. Identifies the recommended implementation approach
2. Explains the trade-offs between scenarios
3. Suggests risk mitigation strategies
4. Provides a phased implementation recommendation if appropriate

Consider:
- Resource constraints in Bangsamoro region
- Community capacity and readiness
- Risk tolerance
- Long-term sustainability

Output as plain text (not JSON).
"""

        response = self.gemini.generate_text(
            prompt,
            use_cache=False,
            include_cultural_context=False
        )

        if response['success']:
            return response['text']
        else:
            return "Unable to generate recommendation due to AI service error."

    def compare_policies(
        self,
        policy_ids: List[str],
        scenario: str = 'realistic'
    ) -> Dict:
        """
        Compare multiple policies under the same scenario

        Args:
            policy_ids: List of policy UUIDs
            scenario: Scenario to compare under (default: 'realistic')

        Returns:
            {
                'policies': [...],
                'comparison_matrix': {...},
                'ranking': [...],
                'recommendation': '...'
            }
        """
        logger.info(f"Comparing {len(policy_ids)} policies under {scenario} scenario")

        policies_data = []
        simulations = []

        for policy_id in policy_ids:
            result = self.simulate_impact(policy_id, scenarios=[scenario])
            if 'error' not in result:
                policies_data.append({
                    'id': policy_id,
                    'title': result['policy_title'],
                    'simulation': result['scenarios'][scenario]
                })
                simulations.append(result['scenarios'][scenario])

        # Create comparison matrix
        comparison_matrix = self._create_comparison_matrix(policies_data)

        # Rank policies
        ranking = self._rank_policies(policies_data)

        return {
            'policies': policies_data,
            'scenario': scenario,
            'comparison_matrix': comparison_matrix,
            'ranking': ranking,
            'compared_at': str(timezone.now())
        }

    def _create_comparison_matrix(self, policies_data: List[Dict]) -> Dict:
        """Create comparison matrix for policies"""
        matrix = {
            'beneficiaries': [],
            'cost_efficiency': [],
            'timeline': [],
            'success_probability': []
        }

        for policy in policies_data:
            sim = policy['simulation']
            matrix['beneficiaries'].append({
                'policy': policy['title'],
                'value': sim.get('beneficiaries_reached', 0)
            })
            matrix['cost_efficiency'].append({
                'policy': policy['title'],
                'value': sim.get('cost_per_beneficiary', 0)
            })
            matrix['timeline'].append({
                'policy': policy['title'],
                'value': sim.get('timeline_months', 0)
            })
            matrix['success_probability'].append({
                'policy': policy['title'],
                'value': sim.get('success_probability', 0)
            })

        return matrix

    def _rank_policies(self, policies_data: List[Dict]) -> List[Dict]:
        """Rank policies by weighted score"""
        scores = []

        for policy in policies_data:
            sim = policy['simulation']

            # Weighted scoring
            score = (
                (sim.get('beneficiaries_reached', 0) / 1000) * 0.3 +  # Reach: 30%
                (1 / max(sim.get('cost_per_beneficiary', 1), 1)) * 1000 * 0.25 +  # Efficiency: 25%
                sim.get('success_probability', 0) * 100 * 0.25 +  # Success: 25%
                (sim.get('impact_metrics', {}).get('sustainability_score', 0)) * 0.20  # Sustainability: 20%
            )

            scores.append({
                'policy_id': policy['id'],
                'policy_title': policy['title'],
                'score': round(score, 2)
            })

        # Sort by score descending
        scores.sort(key=lambda x: x['score'], reverse=True)

        return scores


# Global singleton
_impact_simulator = None


def get_impact_simulator() -> PolicyImpactSimulator:
    """Get or create global impact simulator instance"""
    global _impact_simulator
    if _impact_simulator is None:
        _impact_simulator = PolicyImpactSimulator()
    return _impact_simulator


# Fix missing import
from django.utils import timezone
