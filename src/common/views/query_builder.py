"""
Query Builder Views

HTMX-powered endpoints for visual query builder.
"""

import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from common.ai_services.chat.query_builder import QueryBuilder


@login_required
@require_http_methods(["GET"])
def query_builder_entities(request):
    """
    GET /api/query-builder/entities/

    Returns list of available entity types
    """
    builder = QueryBuilder()
    entities = builder.get_available_entities()

    return JsonResponse(
        {
            "entities": entities,
        }
    )


@login_required
@require_http_methods(["GET"])
def query_builder_config(request, entity_type):
    """
    GET /api/query-builder/config/<entity_type>/

    Returns configuration for a specific entity type
    """
    builder = QueryBuilder()

    try:
        config = builder.get_builder_config(entity_type)
        return JsonResponse(config)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def query_builder_filters(request):
    """
    GET /api/query-builder/filters/?entity=<entity_type>

    Returns HTML for dynamic filters based on entity type
    """
    entity_type = request.GET.get("entity", "")

    if not entity_type:
        return HttpResponse("Entity type required", status=400)

    builder = QueryBuilder()

    try:
        config = builder.get_builder_config(entity_type)
        filters = config.get("filters", {})

        # Build filter HTML
        filter_html = _build_filter_html(filters)

        return HttpResponse(filter_html)

    except ValueError as e:
        return HttpResponse(f"Error: {str(e)}", status=400)


@login_required
@require_http_methods(["POST"])
def query_builder_preview(request):
    """
    POST /api/query-builder/preview/

    Returns preview of query results
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    builder = QueryBuilder()

    try:
        preview = builder.preview_query(data)
        return JsonResponse(preview)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def query_builder_execute(request):
    """
    POST /api/query-builder/execute/

    Executes the built query and returns results
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    builder = QueryBuilder()

    try:
        result = builder.execute_built_query(data)

        # Convert QueryResult to dict
        response_data = {
            "success": result.success,
            "query_text": result.query_text,
            "query_type": data.get("query_type", "count"),
            "count": result.count,
        }

        if result.success:
            # Handle different data types
            if data.get("query_type") == "list":
                # For list queries, serialize model instances
                response_data["data"] = _serialize_query_results(
                    result.data, data.get("entity_type")
                )
            else:
                # For count and aggregate, return raw value
                response_data["data"] = result.data
        else:
            response_data["error"] = result.error

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse(
            {"success": False, "error": str(e), "query_text": ""}, status=500
        )


def _build_filter_html(filters):
    """Build HTML for filters"""
    html_parts = []

    for key, config in filters.items():
        filter_type = config.get("type", "dropdown")
        label = config.get("label", key)
        required = config.get("required", False)

        if filter_type == "dropdown":
            options = config.get("options", ["All"])

            html = f"""
            <div class="space-y-2">
                <label for="filter-{key}" class="block text-sm font-medium text-gray-700">
                    {label}
                    {'<span class="text-red-500">*</span>' if required else ''}
                </label>
                <div class="relative">
                    <select id="filter-{key}" name="{key}"
                            class="block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white transition-all duration-200">
                        {''.join(f'<option value="{opt}" {"selected" if opt == "All" else ""}>{opt}</option>' for opt in options)}
                    </select>
                    <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-4">
                        <i class="fas fa-chevron-down text-gray-400 text-sm"></i>
                    </span>
                </div>
            </div>
            """
            html_parts.append(html)

        elif filter_type == "date":
            html = f"""
            <div class="space-y-2">
                <label for="filter-{key}" class="block text-sm font-medium text-gray-700">
                    {label}
                    {'<span class="text-red-500">*</span>' if required else ''}
                </label>
                <input type="date" id="filter-{key}" name="{key}"
                       class="block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] transition-all duration-200">
            </div>
            """
            html_parts.append(html)

    if not html_parts:
        return """
        <div class="text-center py-8">
            <i class="fas fa-filter text-gray-300 text-4xl mb-3"></i>
            <p class="text-gray-500">No filters available for this entity type</p>
            <p class="text-sm text-gray-400 mt-1">You can proceed to the next step</p>
        </div>
        """

    return "\n".join(html_parts)


def _serialize_query_results(data, entity_type):
    """Serialize query results for JSON response"""
    if not data:
        return []

    # For now, return simplified representation
    # In production, you'd want to use proper serializers
    serialized = []

    for item in data:
        if entity_type == "communities":
            serialized.append(
                {
                    "id": item.id,
                    "name": str(item),
                    "municipality": str(item.municipality) if item.municipality else "",
                }
            )
        elif entity_type == "workshops":
            serialized.append(
                {
                    "id": item.id,
                    "title": item.title,
                    "status": item.status,
                    "start_date": item.start_date.isoformat() if item.start_date else "",
                }
            )
        elif entity_type == "policies":
            serialized.append(
                {
                    "id": item.id,
                    "title": item.title,
                    "status": item.status,
                    "priority": item.priority_level,
                }
            )
        elif entity_type == "stakeholders":
            serialized.append(
                {
                    "id": item.id,
                    "name": item.name,
                    "organization": (
                        str(item.organization) if item.organization else ""
                    ),
                }
            )
        else:
            serialized.append({"id": item.id, "name": str(item)})

    return serialized
