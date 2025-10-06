#!/usr/bin/env python
"""Test municipalities and cities queries separately."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings')
django.setup()

from common.ai_services.chat.faq_handler import get_faq_handler
from common.ai_services.chat.chat_engine import ConversationalAssistant
from communities.models import Municipality

# Step 1: Update FAQ cache
print("=" * 70)
print("STEP 1: Updating FAQ Cache")
print("=" * 70)
faq_handler = get_faq_handler()
faq_handler.update_stats_cache()
print("✅ FAQ cache updated")
print()

# Step 2: Get actual counts from database
municipalities_count = Municipality.objects.filter(municipality_type="municipality").count()
cities_count = Municipality.objects.exclude(municipality_type="municipality").count()
total_count = Municipality.objects.count()

print("=" * 70)
print("DATABASE COUNTS")
print("=" * 70)
print(f"Municipalities only: {municipalities_count}")
print(f"Cities only: {cities_count}")
print(f"Total (both): {total_count}")
print("=" * 70)
print()

# Step 3: Test both queries
assistant = ConversationalAssistant()
user_id = 1

test_queries = [
    ("How many municipalities", municipalities_count),
    ("How many cities", cities_count),
]

for query, expected_count in test_queries:
    print(f"TESTING: '{query}'")
    print("-" * 70)

    try:
        result = assistant.chat(user_id, query)
        response = result.get('response', 'No response')

        print(f"Response: {response}")
        print(f"Intent: {result.get('intent', 'Unknown')}")
        print(f"Confidence: {result.get('confidence', 0):.2f}")
        print()

        # Verify correctness
        response_str = str(response)
        if str(expected_count) in response_str:
            print(f"✅ PASS: Contains correct count ({expected_count})")
        else:
            print(f"❌ FAIL: Expected count {expected_count} not found in response")

        # Check it doesn't contain wrong counts
        for wrong_count in [municipalities_count, cities_count, total_count]:
            if wrong_count != expected_count and str(wrong_count) in response_str:
                print(f"⚠️  WARNING: Response also contains {wrong_count} (should only show {expected_count})")

    except Exception as e:
        print(f"❌ ERROR: {e}")

    print("=" * 70)
    print()
