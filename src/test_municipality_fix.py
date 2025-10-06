#!/usr/bin/env python
"""Test that 'How many municipalities' now matches the correct template."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings')
django.setup()

from common.ai_services.chat.template_matcher import TemplateMatcher

# Test the fix
matcher = TemplateMatcher()
result = matcher.match_and_generate(
    query="How many municipalities",
    entities={},
    intent='data_query'
)

print("=" * 70)
print("TEST: 'How many municipalities' query")
print("=" * 70)
print(f"Success: {result['success']}")
print(f"Template ID: {result['template'].id if result['template'] else 'None'}")
print(f"Template Category: {result['template'].category if result['template'] else 'None'}")
print(f"Template Priority: {result['template'].priority if result['template'] else 'None'}")
print(f"Query: {result['query']}")
print(f"Score: {result['score']:.3f}")
print("=" * 70)

# Verify it's the geographic template, not communities
if result['success']:
    if result['template'].category == 'geographic':
        print("✅ PASS: Matched geographic template (correct!)")
    elif result['template'].category == 'communities':
        print("❌ FAIL: Matched communities template (wrong!)")
    else:
        print(f"⚠️  UNEXPECTED: Matched {result['template'].category} template")

    # Check if query is for municipalities
    if 'Municipality' in result['query']:
        print("✅ PASS: Query references Municipality model (correct!)")
    elif 'OBCCommunity' in result['query']:
        print("❌ FAIL: Query references OBCCommunity model (wrong!)")
    else:
        print(f"⚠️  UNEXPECTED: Query is {result['query']}")
else:
    print(f"❌ FAIL: No template matched - {result['error']}")

print("=" * 70)
