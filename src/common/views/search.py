"""
Unified Search Views

Views for global semantic search across OBCMS.
"""

import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from common.ai_services import UnifiedSearchEngine, SearchAnalytics, HAS_UNIFIED_SEARCH

logger = logging.getLogger(__name__)


@login_required
@require_GET
def unified_search_view(request):
    """
    Global search page.

    GET /search/?q=query&modules=communities,mana&limit=20
    """
    if not HAS_UNIFIED_SEARCH:
        # Search not available
        return render(request, 'common/search_results.html', {
            'search_error': 'Unified search is currently unavailable. AI services are not installed.',
            'search_unavailable': True,
            'search_success': False,
        })

    query = request.GET.get('q', '').strip()
    modules_param = request.GET.get('modules', '')
    limit = int(request.GET.get('limit', 20))

    # Parse modules parameter
    modules = None
    if modules_param:
        modules = [m.strip() for m in modules_param.split(',') if m.strip()]

    context = {
        'query': query,
        'selected_modules': modules or [],
    }

    if not query:
        # Empty search page
        return render(request, 'common/search_results.html', context)

    try:
        # Perform search
        search_engine = UnifiedSearchEngine()
        results = search_engine.search(
            query=query,
            modules=modules,
            limit=limit
        )

        # Log search
        if SearchAnalytics:
            analytics = SearchAnalytics()
            analytics.log_search(
                query=query,
                results_count=results['total_results'],
                user_id=request.user.id,
                modules_searched=modules
            )

        context.update({
            'results': results,
            'search_success': True,
        })

    except Exception as e:
        logger.error(f"Search error: {e}")
        context.update({
            'results': None,
            'search_error': str(e),
            'search_success': False,
        })

    return render(request, 'common/search_results.html', context)


@login_required
@require_POST
def search_autocomplete(request):
    """
    Search autocomplete endpoint.

    POST /search/autocomplete/
    Body: {"query": "partial query"}
    """
    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()

        if len(query) < 3:
            return JsonResponse({'suggestions': []})

        # Get popular queries that match
        analytics = SearchAnalytics()
        popular = analytics.get_popular_queries(limit=50)

        # Filter by query prefix
        suggestions = [
            p['query']
            for p in popular
            if query.lower() in p['query'].lower()
        ][:10]

        return JsonResponse({'suggestions': suggestions})

    except Exception as e:
        logger.error(f"Autocomplete error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_GET
def search_stats(request):
    """
    Search analytics dashboard.

    GET /search/stats/
    """
    if not HAS_UNIFIED_SEARCH:
        return render(request, 'common/search_stats.html', {
            'error': 'Search analytics are currently unavailable. AI services are not installed.',
            'search_unavailable': True
        })

    try:
        if not SearchAnalytics:
            return render(request, 'common/search_stats.html', {
                'error': 'Search analytics service is not available.',
                'search_unavailable': True
            })

        analytics = SearchAnalytics()

        # Get analytics data
        patterns = analytics.identify_patterns()
        popular_queries = analytics.get_popular_queries(limit=20)
        zero_results = analytics.get_zero_result_queries(limit=20)
        suggestions = analytics.suggest_improvements()

        # Get index stats
        search_engine = UnifiedSearchEngine()
        index_stats = search_engine.get_index_stats()

        context = {
            'patterns': patterns,
            'popular_queries': popular_queries,
            'zero_results': zero_results,
            'suggestions': suggestions,
            'index_stats': index_stats,
        }

        return render(request, 'common/search_stats.html', context)

    except Exception as e:
        logger.error(f"Stats error: {e}")
        return render(request, 'common/search_stats.html', {
            'error': str(e)
        })


@login_required
@require_POST
def reindex_module(request, module):
    """
    Trigger reindexing of a specific module.

    POST /search/reindex/<module>/
    """
    if not HAS_UNIFIED_SEARCH:
        return JsonResponse({
            'success': False,
            'error': 'Reindexing is not available. AI services are not installed.'
        }, status=500)

    try:
        search_engine = UnifiedSearchEngine()
        stats = search_engine.reindex_module(module)

        return JsonResponse({
            'success': True,
            'stats': stats,
        })

    except Exception as e:
        logger.error(f"Reindex error for {module}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
