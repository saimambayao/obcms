#!/usr/bin/env python
"""Test 'Where is Cotabato province?' query."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings')
django.setup()

from common.ai_services.chat.chat_engine import ConversationalAssistant

# Test the query
assistant = ConversationalAssistant()
user_id = 1

test_queries = [
    "Where is Cotabato province?",
    "Where is Zamboanga?",
    "Where is Bukidnon?",
    "Where is Davao?",
]

print("=" * 70)
print("TESTING LOCATION QUERIES")
print("=" * 70)

for query in test_queries:
    print(f"\nQuery: '{query}'")
    print("-" * 70)

    try:
        result = assistant.chat(user_id, query)
        response = result.get('response', 'No response')

        print(f"Response: {response}")
        print(f"Intent: {result.get('intent', 'Unknown')}")
        print(f"Confidence: {result.get('confidence', 0):.2f}")

        # Check if response is helpful
        if "couldn't process" in response.lower() or "issue" in response.lower():
            print("❌ FAIL: Query not processed successfully")
        elif "region" in response.lower() or "province" in response.lower():
            print("✅ PASS: Query answered successfully")
        else:
            print("⚠️  UNKNOWN: Response unclear")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

    print("=" * 70)
