"""
AI-powered views for MANA module
Handles AI analysis, report generation, and cultural validation
"""

import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from .ai_services.cultural_validator import BangsomoroCulturalValidator
from .ai_services.needs_extractor import NeedsExtractor
from .ai_services.report_generator import AssessmentReportGenerator
from .ai_services.response_analyzer import ResponseAnalyzer
from .ai_services.theme_extractor import ThemeExtractor
from .models import WorkshopActivity
from .tasks import analyze_workshop_responses, generate_assessment_report

logger = logging.getLogger(__name__)


@login_required
def workshop_ai_analysis(request, workshop_id):
    """
    Display AI analysis for a workshop

    Shows analysis results or triggers analysis if not yet performed
    """
    workshop = get_object_or_404(WorkshopActivity, id=workshop_id)

    # Check if analysis exists in cache
    cache_key = f"mana_workshop_analysis_{workshop_id}"
    analysis_data = cache.get(cache_key)

    if not analysis_data:
        # Trigger async analysis
        task = analyze_workshop_responses.delay(workshop_id)
        logger.info(f"Started AI analysis task {task.id} for workshop {workshop_id}")

        return render(
            request,
            "mana/ai_analysis_loading.html",
            {
                "workshop": workshop,
                "task_id": task.id,
                "message": "AI analysis in progress... This may take a few moments.",
            },
        )

    # Analysis exists, display results
    context = {
        "workshop": workshop,
        "insights": analysis_data.get("insights", {}),
        "themes": analysis_data.get("themes", []),
        "needs": analysis_data.get("needs", {}),
        "ranked_needs": analysis_data.get("ranked_needs", []),
        "response_count": analysis_data.get("response_count", 0),
        "analyzed_at": analysis_data.get("analyzed_at"),
    }

    return render(request, "mana/workshop_ai_analysis.html", context)


@login_required
@require_http_methods(["POST"])
def trigger_workshop_analysis(request, workshop_id):
    """
    HTMX endpoint: Trigger AI analysis for a workshop

    Returns: Loading indicator with hx-poll for status updates
    """
    workshop = get_object_or_404(WorkshopActivity, id=workshop_id)

    # Trigger async analysis
    task = analyze_workshop_responses.delay(workshop_id)

    logger.info(f"Triggered AI analysis for workshop {workshop_id}, task: {task.id}")

    # Return loading state with polling
    return HttpResponse(
        f"""
        <div id="analysis-status" hx-get="{request.build_absolute_uri()}/status/"
             hx-trigger="every 2s" hx-swap="outerHTML">
            <div class="flex items-center justify-center space-x-3 text-purple-600 py-8">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                <div>
                    <p class="font-semibold">AI Analysis in Progress...</p>
                    <p class="text-sm text-gray-500">Analyzing workshop responses</p>
                </div>
            </div>
        </div>
        """,
        status=200,
        headers={"HX-Trigger": json.dumps({"analysis-started": {"workshop_id": workshop_id}})},
    )


@login_required
def analysis_status(request, workshop_id):
    """
    HTMX endpoint: Check analysis status

    Returns: Updated status or complete analysis results
    """
    cache_key = f"mana_workshop_analysis_{workshop_id}"
    analysis_data = cache.get(cache_key)

    if analysis_data:
        # Analysis complete, return results widget
        context = {
            "workshop_id": workshop_id,
            "ai_insights": analysis_data.get("insights", {}).get("overall_summary", {}),
            "themes": analysis_data.get("themes", [])[:5],  # Top 5 themes
            "ranked_needs": analysis_data.get("ranked_needs", [])[:5],  # Top 5 needs
            "response_count": analysis_data.get("response_count", 0),
        }

        return render(request, "mana/widgets/ai_analysis.html", context)

    # Still processing
    return HttpResponse(
        """
        <div id="analysis-status" hx-get="" hx-trigger="every 2s" hx-swap="outerHTML">
            <div class="flex items-center justify-center space-x-3 text-purple-600 py-8">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                <div>
                    <p class="font-semibold">AI Analysis in Progress...</p>
                    <p class="text-sm text-gray-500">This may take a few moments</p>
                </div>
            </div>
        </div>
        """
    )


@login_required
@require_http_methods(["POST"])
def generate_report(request, workshop_id):
    """
    HTMX endpoint: Generate assessment report

    Triggers async report generation
    """
    workshop = get_object_or_404(WorkshopActivity, id=workshop_id)

    report_type = request.POST.get("report_type", "executive")

    # Trigger async report generation
    task = generate_assessment_report.delay(workshop_id, report_type)

    logger.info(
        f"Triggered {report_type} report generation for workshop {workshop_id}, task: {task.id}"
    )

    # Return loading state
    return HttpResponse(
        f"""
        <div id="report-status" hx-get="/mana/workshop/{workshop_id}/report/status/?type={report_type}"
             hx-trigger="every 3s" hx-swap="outerHTML">
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div class="flex items-center space-x-3">
                    <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                    <div>
                        <p class="font-semibold text-blue-900">Generating Report...</p>
                        <p class="text-sm text-blue-700">This may take a minute</p>
                    </div>
                </div>
            </div>
        </div>
        """
    )


@login_required
def report_status(request, workshop_id):
    """
    HTMX endpoint: Check report generation status
    """
    report_type = request.GET.get("type", "executive")
    cache_key = f"mana_report_{report_type}_{workshop_id}"

    report_data = cache.get(cache_key)

    if report_data:
        # Report complete
        context = {
            "workshop_id": workshop_id,
            "report_type": report_type,
            "report": report_data.get("report"),
            "cultural_validation": report_data.get("cultural_validation", {}),
            "generated_at": report_data.get("generated_at"),
        }

        return render(request, "mana/widgets/report_preview.html", context)

    # Still generating
    return HttpResponse(
        f"""
        <div id="report-status" hx-get="/mana/workshop/{workshop_id}/report/status/?type={report_type}"
             hx-trigger="every 3s" hx-swap="outerHTML">
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div class="flex items-center space-x-3">
                    <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                    <div>
                        <p class="font-semibold text-blue-900">Generating Report...</p>
                        <p class="text-sm text-blue-700">Please wait...</p>
                    </div>
                </div>
            </div>
        </div>
        """
    )


@login_required
def validate_content(request):
    """
    HTMX endpoint: Validate content for cultural appropriateness

    POST: content to validate
    Returns: Validation results
    """
    if request.method == "POST":
        content = request.POST.get("content", "")

        if not content:
            return JsonResponse({"error": "No content provided"}, status=400)

        # Run validation
        validator = BangsomoroCulturalValidator()
        validation = validator.validate_report_content(content)

        context = {
            "validation": validation,
            "content_preview": content[:200] + "..." if len(content) > 200 else content,
        }

        return render(request, "mana/widgets/cultural_validation_result.html", context)

    return JsonResponse({"error": "Method not allowed"}, status=405)


@login_required
def theme_analysis(request, workshop_id):
    """
    Display detailed theme analysis for a workshop
    """
    workshop = get_object_or_404(WorkshopActivity, id=workshop_id)

    # Get from cache or generate
    cache_key = f"mana_workshop_analysis_{workshop_id}"
    analysis_data = cache.get(cache_key)

    if not analysis_data:
        # Trigger analysis
        messages.info(request, "Analysis not yet complete. Starting analysis...")
        task = analyze_workshop_responses.delay(workshop_id)
        return render(
            request,
            "mana/ai_analysis_loading.html",
            {"workshop": workshop, "task_id": task.id},
        )

    themes = analysis_data.get("themes", [])

    context = {
        "workshop": workshop,
        "themes": themes,
        "theme_count": len(themes),
    }

    return render(request, "mana/theme_analysis.html", context)


@login_required
def needs_analysis(request, workshop_id):
    """
    Display detailed needs analysis for a workshop
    """
    workshop = get_object_or_404(WorkshopActivity, id=workshop_id)

    # Get from cache
    cache_key = f"mana_workshop_analysis_{workshop_id}"
    analysis_data = cache.get(cache_key)

    if not analysis_data:
        messages.info(request, "Analysis not yet complete. Starting analysis...")
        task = analyze_workshop_responses.delay(workshop_id)
        return render(
            request,
            "mana/ai_analysis_loading.html",
            {"workshop": workshop, "task_id": task.id},
        )

    needs = analysis_data.get("needs", {})
    ranked_needs = analysis_data.get("ranked_needs", [])

    # Generate prioritization matrix
    needs_extractor = NeedsExtractor()
    priority_matrix = needs_extractor.generate_needs_prioritization_matrix(needs)

    context = {
        "workshop": workshop,
        "needs": needs,
        "ranked_needs": ranked_needs,
        "priority_matrix": priority_matrix,
        "needs_count": len(needs),
    }

    return render(request, "mana/needs_analysis.html", context)


@login_required
def export_analysis_json(request, workshop_id):
    """
    Export complete analysis as JSON
    """
    workshop = get_object_or_404(WorkshopActivity, id=workshop_id)

    cache_key = f"mana_workshop_analysis_{workshop_id}"
    analysis_data = cache.get(cache_key)

    if not analysis_data:
        return JsonResponse(
            {"error": "Analysis not yet complete"}, status=404
        )

    # Return JSON response
    response = JsonResponse(analysis_data, safe=False)
    response["Content-Disposition"] = (
        f'attachment; filename="workshop_{workshop_id}_analysis.json"'
    )

    return response
