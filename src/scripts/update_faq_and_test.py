#!/usr/bin/env python
"""Update FAQ cache and test municipality query."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings')
django.setup()

from common.ai_services.chat.faq_handler import get_faq_handler
from common.ai_services.chat.chat_engine import ConversationalAssistant
from communities.models import Municipality, OBCCommunity

# Step 1: Update FAQ cache
print("=" * 70)
print("STEP 1: Updating FAQ Cache")
print("=" * 70)
faq_handler = get_faq_handler()
faq_handler.update_stats_cache()
print("✅ FAQ cache updated")
print()

# Step 2: Get actual counts
municipality_count = Municipality.objects.all().count()
community_count = OBCCommunity.objects.count()
print("=" * 70)
print("DATABASE COUNTS")
print("=" * 70)
print(f"Total Municipalities: {municipality_count}")
print(f"Total OBC Communities: {community_count}")
print("=" * 70)
print()

# Step 3: Test the chat system
assistant = ConversationalAssistant()
user_id = 1
query = "How many municipalities"

print("STEP 2: Testing Chat System")
print("=" * 70)
print(f"Query: '{query}'")
print("-" * 70)

try:
    result = assistant.chat(user_id, query)

    print(f"Response: {result.get('response', 'No response')}")
    print(f"Intent: {result.get('intent', 'Unknown')}")
    print(f"Confidence: {result.get('confidence', 0):.2f}")

    # Check if response is correct
    response_text = str(result.get('response', ''))

    print("-" * 70)
    if str(municipality_count) in response_text:
        print(f"✅ PASS: Response contains correct municipality count ({municipality_count})")
    elif str(community_count) in response_text:
        print(f"❌ FAIL: Response contains community count ({community_count}) instead!")
        print(f"   This means the FAQ is still matching 'communities' instead of 'municipalities'")
    else:
        print(f"⚠️  WARNING: Response doesn't contain expected count")

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("=" * 70)
