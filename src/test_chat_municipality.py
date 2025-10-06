#!/usr/bin/env python
"""Test the full chat pipeline for municipality queries."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings')
django.setup()

from common.ai_services.chat.chat_engine import ConversationalAssistant
from communities.models import Municipality, OBCCommunity

# Get actual counts from database
municipality_count = Municipality.objects.all().count()
community_count = OBCCommunity.objects.count()

print("=" * 70)
print("DATABASE COUNTS")
print("=" * 70)
print(f"Total Municipalities: {municipality_count}")
print(f"Total OBC Communities: {community_count}")
print("=" * 70)

# Test the chat system
assistant = ConversationalAssistant()

# Test query
user_id = 1
query = "How many municipalities"

print("\nTESTING CHAT SYSTEM")
print("=" * 70)
print(f"Query: {query}")
print("-" * 70)

try:
    result = assistant.chat(user_id, query)

    print(f"Response: {result.get('response', 'No response')}")
    print(f"Intent: {result.get('intent', 'Unknown')}")
    print(f"Confidence: {result.get('confidence', 0):.2f}")

    if result.get('data'):
        print(f"Data: {result['data']}")

    # Check if response is correct
    response_text = str(result.get('response', ''))

    if str(municipality_count) in response_text:
        print(f"\n✅ PASS: Response contains correct municipality count ({municipality_count})")
    elif str(community_count) in response_text:
        print(f"\n❌ FAIL: Response contains community count ({community_count}) instead of municipality count")
    else:
        print(f"\n⚠️  WARNING: Response doesn't contain expected count")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("=" * 70)
