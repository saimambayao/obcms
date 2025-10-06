"""Celery tasks for MANA workflows (fallback to synchronous execution if Celery is absent)."""

from __future__ import annotations

try:
    from celery import shared_task
except ImportError:  # pragma: no cover

    def shared_task(*dargs, **dkwargs):  # type: ignore
        def decorator(func):
            setattr(func, "delay", func)
            return func

        if dargs and callable(dargs[0]):
            return decorator(dargs[0])
        return decorator


import logging

from django.contrib.auth import get_user_model
from django.core.cache import cache

from .models import Assessment, WorkshopActivity
from .services.workshop_access import WorkshopAccessManager
from .services.workshop_synthesis import AIWorkshopSynthesizer

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task
def auto_unlock_due_workshops(assessment_id: str) -> int:
    """Background task to unlock workshops that have reached their schedule."""
    assessment = Assessment.objects.get(id=assessment_id)
    manager = WorkshopAccessManager(assessment)
    return manager.auto_unlock_due_workshops()


@shared_task
def generate_workshop_synthesis(
    workshop_id: int,
    filters: dict | None,
    created_by_id: int | None,
    provider: str = "anthropic",
    custom_prompt: str | None = None,
) -> dict:
    """Queueable task to run AI workshop synthesis."""
    workshop = WorkshopActivity.objects.get(id=workshop_id)
    created_by = User.objects.filter(id=created_by_id).first()

    synthesizer = AIWorkshopSynthesizer(workshop, filters)
    synthesis = synthesizer.synthesize(
        created_by=created_by,
        provider=provider,
        custom_prompt=custom_prompt,
    )

    return {
        "synthesis_id": synthesis.id,
        "status": synthesis.status,
    }


@shared_task
def analyze_workshop_responses(workshop_id: int) -> dict:
    """
    Background task: Analyze all workshop responses using AI

    Runs comprehensive analysis including:
    - Response analysis
    - Theme extraction
    - Needs identification
    - Sentiment analysis
    """
    from .ai_services.needs_extractor import NeedsExtractor
    from .ai_services.response_analyzer import ResponseAnalyzer
    from .ai_services.theme_extractor import ThemeExtractor

    try:
        workshop = WorkshopActivity.objects.get(id=workshop_id)

        # Initialize AI services
        analyzer = ResponseAnalyzer()
        theme_extractor = ThemeExtractor()
        needs_extractor = NeedsExtractor()

        # Collect responses
        responses = []
        for response in workshop.structured_responses.filter(status="submitted"):
            if isinstance(response.response_data, dict):
                text = response.response_data.get("text") or response.response_data.get(
                    "answer"
                )
                if text:
                    responses.append(text)
            elif isinstance(response.response_data, str):
                responses.append(response.response_data)

        if not responses:
            logger.warning(f"No responses found for workshop {workshop_id}")
            return {"status": "no_data", "workshop_id": workshop_id}

        # Run analysis
        logger.info(f"Analyzing {len(responses)} responses for workshop {workshop_id}")

        insights = analyzer.aggregate_workshop_insights(workshop_id)
        themes = theme_extractor.extract_themes(
            responses, num_themes=8, context=workshop.workshop_type
        )
        needs = needs_extractor.extract_needs(
            responses, context=f"{workshop.workshop_type} - {workshop.barangay.name}"
        )
        ranked_needs = needs_extractor.rank_needs_by_priority(needs)

        # Store results in cache (30 days)
        analysis_data = {
            "workshop_id": workshop_id,
            "insights": insights,
            "themes": themes,
            "needs": needs,
            "ranked_needs": ranked_needs,
            "response_count": len(responses),
            "analyzed_at": str(workshop.updated_at),
        }

        cache_key = f"mana_workshop_analysis_{workshop_id}"
        cache.set(cache_key, analysis_data, timeout=86400 * 30)

        logger.info(f"Successfully analyzed workshop {workshop_id}")

        return {"status": "success", "workshop_id": workshop_id, "response_count": len(responses)}

    except WorkshopActivity.DoesNotExist:
        logger.error(f"Workshop {workshop_id} not found")
        return {"status": "error", "message": "Workshop not found"}

    except Exception as e:
        logger.error(f"Error analyzing workshop {workshop_id}: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@shared_task
def generate_assessment_report(workshop_id: int, report_type: str = "full") -> dict:
    """
    Background task: Generate comprehensive assessment report

    Args:
        workshop_id: Workshop activity ID
        report_type: 'executive' or 'full' report

    Returns:
        dict: Report generation status and cache key
    """
    from .ai_services.cultural_validator import BangsomoroCulturalValidator
    from .ai_services.report_generator import AssessmentReportGenerator

    try:
        workshop = WorkshopActivity.objects.get(id=workshop_id)

        # Initialize services
        generator = AssessmentReportGenerator()
        validator = BangsomoroCulturalValidator()

        logger.info(f"Generating {report_type} report for workshop {workshop_id}")

        if report_type == "executive":
            # Generate executive summary
            report = generator.generate_executive_summary(workshop_id)

            # Validate cultural appropriateness
            validation = validator.validate_report_content(report)

            result = {
                "workshop_id": workshop_id,
                "report_type": "executive",
                "report": report,
                "cultural_validation": validation,
                "generated_at": str(workshop.updated_at),
            }

        else:  # full report
            # Generate full report
            report = generator.generate_full_report(workshop_id)

            # Validate executive summary
            exec_summary = report.get("sections", {}).get("executive_summary", "")
            validation = validator.validate_report_content(exec_summary)

            result = {
                "workshop_id": workshop_id,
                "report_type": "full",
                "report": report,
                "cultural_validation": validation,
                "generated_at": str(workshop.updated_at),
            }

        # Cache report for 30 days
        cache_key = f"mana_report_{report_type}_{workshop_id}"
        cache.set(cache_key, result, timeout=86400 * 30)

        logger.info(
            f"Successfully generated {report_type} report for workshop {workshop_id}"
        )

        return {
            "status": "success",
            "workshop_id": workshop_id,
            "report_type": report_type,
            "cache_key": cache_key,
            "cultural_score": validation.get("score", 0),
        }

    except WorkshopActivity.DoesNotExist:
        logger.error(f"Workshop {workshop_id} not found")
        return {"status": "error", "message": "Workshop not found"}

    except Exception as e:
        logger.error(f"Error generating report for workshop {workshop_id}: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@shared_task
def validate_report_cultural_compliance(report_text: str, report_id: str = None) -> dict:
    """
    Background task: Validate report for cultural appropriateness

    Args:
        report_text: Report content to validate
        report_id: Optional identifier for caching

    Returns:
        dict: Validation results
    """
    from .ai_services.cultural_validator import BangsomoroCulturalValidator

    try:
        validator = BangsomoroCulturalValidator()

        logger.info(f"Validating cultural compliance for report {report_id or 'unnamed'}")

        validation = validator.validate_report_content(report_text)

        # Generate compliance report
        compliance_report = validator.generate_cultural_compliance_report(validation)

        result = {
            "validation": validation,
            "compliance_report": compliance_report,
            "validated_at": str(cache.get("now")),
        }

        # Cache if report_id provided
        if report_id:
            cache_key = f"mana_cultural_validation_{report_id}"
            cache.set(cache_key, result, timeout=86400 * 14)

        logger.info(
            f"Cultural validation completed. Score: {validation.get('score', 0):.2%}"
        )

        return {"status": "success", "validation": validation}

    except Exception as e:
        logger.error(f"Error validating cultural compliance: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
