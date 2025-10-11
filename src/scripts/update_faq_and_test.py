#!/usr/bin/env python
"""Update FAQ cache and test municipality query."""

import os

import pytest

try:
    import django
except ImportError:  # pragma: no cover - handled via skip
    pytest.skip(
        "Django is required for FAQ update script",
        allow_module_level=True,
    )

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "obc_management.settings")
django.setup()

from common.ai_services.chat.chat_engine import ConversationalAssistant
from common.ai_services.chat.faq_handler import get_faq_handler
from communities.models import Municipality, OBCCommunity


def main() -> None:
    """Execute the diagnostic workflow when run as a script."""
    # Step 1: Update FAQ cache with the latest statistics
    print("=" * 70)
    print("STEP 1: Updating FAQ Cache")
    print("=" * 70)
    faq_handler = get_faq_handler()
    faq_handler.update_stats_cache()
    print("✅ FAQ cache updated")
    print()

    # Step 2: Show current database counts
    municipality_count = Municipality.objects.count()
    community_count = OBCCommunity.objects.count()
    print("=" * 70)
    print("DATABASE COUNTS")
    print("=" * 70)
    print(f"Total Municipalities: {municipality_count}")
    print(f"Total OBC Communities: {community_count}")
    print("=" * 70)
    print()

    # Step 3: Test the chat response for municipality counts
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

        response_text = str(result.get("response", ""))

        print("-" * 70)
        if str(municipality_count) in response_text:
            print(
                "✅ PASS: Response contains correct municipality count "
                f"({municipality_count})"
            )
        elif str(community_count) in response_text:
            print(
                "❌ FAIL: Response contains community count "
                f"({community_count}) instead!"
            )
            print(
                "   This means the FAQ is still matching 'communities' "
                "instead of 'municipalities'"
            )
        else:
            print("⚠️  WARNING: Response doesn't contain expected count")

    except Exception as exc:  # pragma: no cover - diagnostic helper
        print(f"❌ ERROR: {exc}")
        import traceback

        traceback.print_exc()

    print("=" * 70)


if __name__ == "__main__":
    main()
