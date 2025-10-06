"""
Celery Tasks for Policy AI Services

Background tasks for:
- Policy generation from assessments
- Impact simulation
- Compliance checking
- Evidence indexing
"""

import logging
from typing import Dict, List

from celery import shared_task
from django.core.cache import cache

logger = logging.getLogger(__name__)


@shared_task(
    name='policy_tracking.generate_policy_from_assessments',
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def generate_policy_from_assessments(
    self,
    issue: str,
    assessment_ids: List[int],
    category: str = 'social_development',
    scope: str = 'regional'
) -> Dict:
    """
    Auto-generate policy recommendation from MANA assessments

    Args:
        issue: Policy issue description
        assessment_ids: List of MANA assessment IDs
        category: Policy category
        scope: Policy scope

    Returns:
        Dict with generated policy data
    """
    try:
        from recommendations.policies.ai_services import (
            get_evidence_gatherer,
            get_policy_generator
        )

        logger.info(f"Task {self.request.id}: Generating policy for '{issue}'")

        # Gather evidence
        gatherer = get_evidence_gatherer()
        evidence = gatherer.gather_evidence(issue, modules=['assessments', 'communities'])

        # Generate policy
        generator = get_policy_generator()
        policy_data = generator.generate_policy_recommendation(
            issue=issue,
            evidence=evidence,
            category=category,
            scope=scope
        )

        # Cache result
        cache_key = f"generated_policy_{self.request.id}"
        cache.set(cache_key, policy_data, timeout=3600)  # 1 hour

        logger.info(f"Task {self.request.id}: Policy generated successfully")

        return {
            'success': True,
            'policy_title': policy_data.get('title'),
            'cache_key': cache_key,
            'task_id': self.request.id
        }

    except Exception as e:
        logger.error(f"Task {self.request.id}: Policy generation failed: {e}")
        # Retry with exponential backoff
        raise self.retry(exc=e)


@shared_task(
    name='policy_tracking.simulate_policy_impact',
    bind=True
)
def simulate_policy_impact(
    self,
    policy_id: str,
    scenarios: List[str] = None
) -> Dict:
    """
    Simulate policy impact under different scenarios

    Args:
        policy_id: Policy UUID
        scenarios: List of scenarios to simulate

    Returns:
        Dict with simulation results
    """
    try:
        from recommendations.policies.ai_services import get_impact_simulator

        logger.info(f"Task {self.request.id}: Simulating impact for policy {policy_id}")

        simulator = get_impact_simulator()
        results = simulator.simulate_impact(
            policy_data=policy_id,
            scenarios=scenarios,
            use_cache=True
        )

        logger.info(f"Task {self.request.id}: Impact simulation completed")

        return {
            'success': True,
            'policy_id': policy_id,
            'scenarios_simulated': list(results.get('scenarios', {}).keys()),
            'task_id': self.request.id
        }

    except Exception as e:
        logger.error(f"Task {self.request.id}: Impact simulation failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'task_id': self.request.id
        }


@shared_task(
    name='policy_tracking.check_policy_compliance',
    bind=True
)
def check_policy_compliance(
    self,
    policy_id: str
) -> Dict:
    """
    Check policy compliance with BARMM regulations

    Args:
        policy_id: Policy UUID

    Returns:
        Dict with compliance check results
    """
    try:
        from recommendations.policy_tracking.models import PolicyRecommendation
        from recommendations.policies.ai_services import get_compliance_checker

        logger.info(f"Task {self.request.id}: Checking compliance for policy {policy_id}")

        # Get policy
        policy = PolicyRecommendation.objects.get(id=policy_id)

        # Build policy text
        policy_text = f"""
Title: {policy.title}
Category: {policy.category}
Description: {policy.description}
Rationale: {policy.rationale}
Proposed Solution: {policy.proposed_solution}
"""

        # Check compliance
        checker = get_compliance_checker()
        compliance_result = checker.check_compliance(
            policy_text=policy_text,
            policy_title=policy.title,
            category=policy.category
        )

        # Cache result
        cache_key = f"compliance_check_{policy_id}"
        cache.set(cache_key, compliance_result, timeout=86400)  # 24 hours

        logger.info(
            f"Task {self.request.id}: Compliance check completed - "
            f"{compliance_result.get('compliance_score', 0):.0%} compliant"
        )

        return {
            'success': True,
            'policy_id': str(policy_id),
            'compliant': compliance_result.get('compliant'),
            'compliance_score': compliance_result.get('compliance_score'),
            'risk_level': compliance_result.get('risk_level'),
            'cache_key': cache_key,
            'task_id': self.request.id
        }

    except PolicyRecommendation.DoesNotExist:
        logger.error(f"Task {self.request.id}: Policy {policy_id} not found")
        return {
            'success': False,
            'error': f'Policy {policy_id} not found',
            'task_id': self.request.id
        }
    except Exception as e:
        logger.error(f"Task {self.request.id}: Compliance check failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'task_id': self.request.id
        }


@shared_task(
    name='policy_tracking.simulate_all_active_policies',
    bind=True
)
def simulate_all_active_policies(self) -> Dict:
    """
    Nightly task: Simulate impact of all active policies

    Runs impact simulation for all policies in DRAFT or UNDER_REVIEW status
    and caches results for quick display.

    Returns:
        Dict with task summary
    """
    try:
        from recommendations.policy_tracking.models import PolicyRecommendation
        from recommendations.policies.ai_services import get_impact_simulator

        logger.info(f"Task {self.request.id}: Starting batch impact simulation")

        # Get active policies
        policies = PolicyRecommendation.objects.filter(
            status__in=['draft', 'under_review']
        )

        simulator = get_impact_simulator()
        results = {
            'total_policies': policies.count(),
            'simulated': 0,
            'failed': 0,
            'policy_ids': []
        }

        for policy in policies:
            try:
                simulation = simulator.simulate_impact(
                    policy_data=str(policy.id),
                    scenarios=['realistic', 'best_case', 'worst_case'],
                    use_cache=True
                )

                if 'error' not in simulation:
                    results['simulated'] += 1
                    results['policy_ids'].append(str(policy.id))
                else:
                    results['failed'] += 1

            except Exception as e:
                logger.error(f"Failed to simulate policy {policy.id}: {e}")
                results['failed'] += 1

        logger.info(
            f"Task {self.request.id}: Batch simulation completed - "
            f"{results['simulated']} success, {results['failed']} failed"
        )

        return {
            'success': True,
            'results': results,
            'task_id': self.request.id
        }

    except Exception as e:
        logger.error(f"Task {self.request.id}: Batch simulation failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'task_id': self.request.id
        }


@shared_task(
    name='policy_tracking.generate_evidence_synthesis',
    bind=True
)
def generate_evidence_synthesis(
    self,
    policy_topic: str,
    modules: List[str] = None
) -> Dict:
    """
    Generate evidence synthesis for a policy topic

    Args:
        policy_topic: Topic to gather evidence for
        modules: Modules to search

    Returns:
        Dict with evidence and synthesis
    """
    try:
        from recommendations.policies.ai_services import get_evidence_gatherer

        logger.info(f"Task {self.request.id}: Generating evidence synthesis for '{policy_topic}'")

        gatherer = get_evidence_gatherer()

        # Gather evidence
        evidence = gatherer.gather_evidence(
            policy_topic=policy_topic,
            modules=modules
        )

        # Synthesize evidence
        synthesis = gatherer.synthesize_evidence(evidence, policy_topic)

        # Cache result
        cache_key = f"evidence_synthesis_{self.request.id}"
        result = {
            'evidence': evidence,
            'synthesis': synthesis,
            'topic': policy_topic
        }
        cache.set(cache_key, result, timeout=3600)  # 1 hour

        logger.info(
            f"Task {self.request.id}: Evidence synthesis completed - "
            f"{evidence.get('total_citations', 0)} citations, "
            f"{synthesis.get('strength_of_evidence', 'unknown')} strength"
        )

        return {
            'success': True,
            'topic': policy_topic,
            'total_citations': evidence.get('total_citations', 0),
            'strength_of_evidence': synthesis.get('strength_of_evidence'),
            'cache_key': cache_key,
            'task_id': self.request.id
        }

    except Exception as e:
        logger.error(f"Task {self.request.id}: Evidence synthesis failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'task_id': self.request.id
        }


@shared_task(
    name='policy_tracking.refine_policy_with_feedback',
    bind=True,
    max_retries=2
)
def refine_policy_with_feedback(
    self,
    policy_id: str,
    feedback: str,
    focus_areas: List[str] = None
) -> Dict:
    """
    Refine policy based on stakeholder feedback

    Args:
        policy_id: Policy UUID
        feedback: Stakeholder feedback text
        focus_areas: Specific areas to refine

    Returns:
        Dict with refined policy data
    """
    try:
        from recommendations.policy_tracking.models import PolicyRecommendation
        from recommendations.policies.ai_services import get_policy_generator

        logger.info(f"Task {self.request.id}: Refining policy {policy_id}")

        # Get policy
        policy = PolicyRecommendation.objects.get(id=policy_id)

        # Build policy data dict
        policy_data = {
            'title': policy.title,
            'description': policy.description,
            'problem_statement': policy.problem_statement,
            'rationale': policy.rationale,
            'proposed_solution': policy.proposed_solution,
            'policy_objectives': policy.policy_objectives,
            'expected_outcomes': policy.expected_outcomes,
            'implementation_strategy': policy.implementation_strategy,
        }

        # Refine policy
        generator = get_policy_generator()
        refined_policy = generator.refine_policy(
            policy_data=policy_data,
            feedback=feedback,
            focus_areas=focus_areas
        )

        # Cache refined policy
        cache_key = f"refined_policy_{self.request.id}"
        cache.set(cache_key, refined_policy, timeout=3600)  # 1 hour

        logger.info(f"Task {self.request.id}: Policy refinement completed")

        return {
            'success': True,
            'policy_id': str(policy_id),
            'cache_key': cache_key,
            'task_id': self.request.id
        }

    except PolicyRecommendation.DoesNotExist:
        logger.error(f"Task {self.request.id}: Policy {policy_id} not found")
        return {
            'success': False,
            'error': f'Policy {policy_id} not found',
            'task_id': self.request.id
        }
    except Exception as e:
        logger.error(f"Task {self.request.id}: Policy refinement failed: {e}")
        # Retry
        raise self.retry(exc=e)
