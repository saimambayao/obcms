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

        # Render response
        import json as json_lib
        context = {
            'user_message': message,
            'assistant_response': result.get('response', ''),
            'suggestions': json_lib.dumps(result.get('suggestions', [])),
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
