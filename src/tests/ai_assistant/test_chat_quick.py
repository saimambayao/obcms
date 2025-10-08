#!/usr/bin/env python
"""
Quick AI Chat Test - Tests the specific fix for "tell me about OBC communities in Davao City"

Tests 5 critical queries to verify the AI chat query understanding works.
"""

import os
import sys
import django
import time

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "obc_management.settings.development")
django.setup()

from common.ai_services.chat.chat_engine import get_conversational_assistant


def test_query(assistant, query, test_num):
    """Test a single query."""
    print(f"\n{'='*80}")
    print(f"TEST {test_num}: {query}")
    print(f"{'='*80}")

    start = time.time()
    try:
        result = assistant.chat(user_id=1, message=query)
        duration = (time.time() - start) * 1000

        print(f"✅ SUCCESS")
        print(f"Intent: {result.get('intent', 'N/A')} (confidence: {result.get('confidence', 0):.2f})")
        print(f"Duration: {duration:.0f}ms")
        print(f"\nResponse:")
        print(result.get('response', 'N/A')[:300])

        if len(result.get('response', '')) > 300:
            print("...")

        suggestions = result.get('suggestions', [])
        if suggestions:
            print(f"\nSuggestions: {', '.join(suggestions)}")

        # Check if it's an error
        response_lower = result.get('response', '').lower()
        if any(phrase in response_lower for phrase in ['error occurred', 'could not understand', "i'm not sure"]):
            print("\n⚠️  WARNING: Response contains error message")
            return False

        return True

    except Exception as e:
        duration = (time.time() - start) * 1000
        print(f"❌ EXCEPTION after {duration:.0f}ms")
        print(f"Error: {str(e)}")
        return False


def main():
    """Run quick tests."""
    print("\n" + "="*80)
    print("AI CHAT QUICK TEST - Critical Queries")
    print("="*80)
    print("Testing the fix for 'tell me about OBC communities in Davao City'\n")

    assistant = get_conversational_assistant()

    # Critical test queries
    test_queries = [
        "Hello",  # Simple conversational
        "What can you help me with?",  # Help query
        "How many communities are there?",  # Basic count
        "Tell me about OBC communities in Davao City",  # The original failing query
        "Show me communities in Region IX",  # Geographic query
    ]

    results = []
    for i, query in enumerate(test_queries, 1):
        success = test_query(assistant, query, i)
        results.append((query, success))

        # Small delay between queries to avoid rate limits
        if i < len(test_queries):
            time.sleep(2)

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for query, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {query}")

    print(f"\nTotal: {passed}/{total} passed ({passed/total*100:.0f}%)")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
    elif passed >= total * 0.8:
        print("\n✅ MOST TESTS PASSED (80%+)")
    else:
        print("\n❌ MANY TESTS FAILED - needs investigation")


if __name__ == "__main__":
    main()
