"""
Chat Views for Conversational AI Assistant

Handles chat widget interactions and message processing.
"""

import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from common.ai_services.chat import get_conversational_assistant
from common.ai_services.chat.clarification import get_clarification_handler
from common.models import ChatMessage

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(['POST'])
def chat_message(request):
    """
    Handle incoming chat message from user.

    Returns HTMX-compatible HTML snippet for the chat interface.
    """
    message = request.POST.get('message', '').strip()

    if not message:
        return HttpResponse(
            '<div class="text-red-500 text-sm">Please enter a message</div>',
            status=400,
        )

    try:
        # Get conversational assistant
        assistant = get_conversational_assistant()

        # Process message
        result = assistant.chat(
            user_id=request.user.id,
            message=message,
        )

        # Check if clarification needed
        if result.get('type') == 'clarification':
            clarification = result.get('clarification', {})
            context = {
                'message': clarification.get('message', ''),
                'options': clarification.get('options', []),
                'original_query': clarification.get('original_query', message),
                'session_id': clarification.get('session_id', ''),
                'clarification_id': clarification.get('clarification_id', ''),
                'issue_type': clarification.get('issue_type', ''),
                'priority': clarification.get('priority', 'medium'),
            }
            return render(request, 'common/chat/clarification_dialog.html', context)

        # Render normal response
        context = {
            'user_message': message,
            'assistant_response': result.get('response', ''),
            'suggestions': result.get('suggestions', []),  # Pass as list, not JSON string
            'data': result.get('data', {}),
            'visualization': result.get('visualization'),
            'intent': result.get('intent'),
            'confidence': result.get('confidence', 0.0),
        }

        return render(request, 'common/chat/message_pair.html', context)

    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        return HttpResponse(
            f'<div class="text-red-500 text-sm">Error: {str(e)}</div>',
            status=500,
        )


@login_required
@require_http_methods(['GET'])
def chat_history(request):
    """
    Get chat history for current user.

    Returns JSON array of recent messages.
    """
    limit = int(request.GET.get('limit', 20))

    messages = ChatMessage.objects.filter(
        user=request.user
    ).order_by('-created_at')[:limit]

    history = [
        {
            'id': msg.id,
            'user_message': msg.user_message,
            'assistant_response': msg.assistant_response,
            'intent': msg.intent,
            'topic': msg.topic,
            'created_at': msg.created_at.isoformat(),
        }
        for msg in reversed(list(messages))
    ]

    return JsonResponse({'history': history})


@login_required
@require_http_methods(['DELETE'])
def clear_chat_history(request):
    """Clear chat history for current user."""
    try:
        ChatMessage.objects.filter(user=request.user).delete()

        # Clear conversation context
        from common.ai_services.chat import get_conversation_manager
        manager = get_conversation_manager()
        manager.clear_context(request.user.id)

        return JsonResponse({'success': True, 'message': 'Chat history cleared'})

    except Exception as e:
        logger.error(f"Error clearing chat history: {str(e)}", exc_info=True)
        return JsonResponse(
            {'success': False, 'error': str(e)},
            status=500,
        )


@login_required
@require_http_methods(['GET'])
def chat_stats(request):
    """Get conversation statistics for current user."""
    try:
        from common.ai_services.chat import get_conversation_manager
        manager = get_conversation_manager()

        stats = manager.get_conversation_stats(request.user.id)

        return JsonResponse({
            'success': True,
            'stats': {
                'total_messages': stats['total_messages'],
                'recent_messages_7d': stats['recent_messages_7d'],
                'top_topics': stats['top_topics'],
            }
        })

    except Exception as e:
        logger.error(f"Error getting chat stats: {str(e)}", exc_info=True)
        return JsonResponse(
            {'success': False, 'error': str(e)},
            status=500,
        )


@login_required
@require_http_methods(['GET'])
def chat_capabilities(request):
    """Get assistant capabilities and example queries."""
    try:
        assistant = get_conversational_assistant()
        capabilities = assistant.get_capabilities()

        return JsonResponse({
            'success': True,
            'capabilities': capabilities,
        })

    except Exception as e:
        logger.error(f"Error getting capabilities: {str(e)}", exc_info=True)
        return JsonResponse(
            {'success': False, 'error': str(e)},
            status=500,
        )


@login_required
@require_http_methods(['POST'])
def chat_suggestion(request):
    """
    Handle suggestion click.

    User clicked a suggestion - process it as a message.
    """
    suggestion = request.POST.get('suggestion', '').strip()

    if not suggestion:
        return HttpResponse(
            '<div class="text-red-500 text-sm">Invalid suggestion</div>',
            status=400,
        )

    # Process as regular message
    request.POST = request.POST.copy()
    request.POST['message'] = suggestion

    return chat_message(request)


@login_required
@require_http_methods(['POST'])
def chat_clarification_response(request):
    """
    Handle clarification response from user.

    User selected an option from clarification dialog.
    Refines the query and continues processing.
    """
    session_id = request.POST.get('session_id', '').strip()
    issue_type = request.POST.get('issue_type', '').strip()
    value = request.POST.get('value', '').strip()
    original_query = request.POST.get('original_query', '').strip()

    if not all([session_id, issue_type, value, original_query]):
        return HttpResponse(
            '<div class="text-red-500 text-sm">Invalid clarification response</div>',
            status=400,
        )

    try:
        # Get clarification handler
        clarification_handler = get_clarification_handler()

        # Apply clarification
        result = clarification_handler.apply_clarification(
            original_query=original_query,
            user_choice={'value': value, 'issue_type': issue_type},
            session_id=session_id,
        )

        refined_query = result['refined_query']
        entities = result['entities']
        needs_more = result.get('needs_more_clarification', False)

        # If more clarification needed, show next clarification dialog
        if needs_more:
            next_clarification = result.get('next_clarification')
            if next_clarification:
                context = {
                    'message': next_clarification['message'],
                    'options': next_clarification['options'],
                    'original_query': refined_query,
                    'session_id': next_clarification['session_id'],
                    'clarification_id': next_clarification['clarification_id'],
                    'issue_type': next_clarification['issue_type'],
                    'priority': next_clarification.get('priority', 'medium'),
                }
                return render(
                    request, 'common/chat/clarification_dialog.html', context
                )

        # No more clarification needed - process refined query
        assistant = get_conversational_assistant()

        # Process refined message with updated entities
        chat_result = assistant.chat(
            user_id=request.user.id,
            message=refined_query,
        )

        # Render response
        context = {
            'user_message': refined_query,
            'assistant_response': chat_result.get('response', ''),
            'suggestions': chat_result.get('suggestions', []),
            'data': chat_result.get('data', {}),
            'visualization': chat_result.get('visualization'),
            'intent': chat_result.get('intent'),
            'confidence': chat_result.get('confidence', 0.0),
        }

        return render(request, 'common/chat/message_pair.html', context)

    except Exception as e:
        logger.error(f"Clarification response error: {str(e)}", exc_info=True)
        return HttpResponse(
            f'<div class="text-red-500 text-sm">Error: {str(e)}</div>',
            status=500,
        )
