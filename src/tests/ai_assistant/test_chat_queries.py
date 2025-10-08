#!/usr/bin/env python
"""
Comprehensive AI Chat Query Testing Script

Tests the conversational AI assistant with various query types to ensure
proper understanding, execution, and response generation.

Usage:
    cd /path/to/obcms/src
    python test_ai_chat_queries.py
"""

import os
import sys
import django
import time
import json
from typing import List, Dict, Any
from datetime import datetime

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "obc_management.settings.development")
django.setup()

# Force reload of chat modules to get latest code
import importlib
if 'common.ai_services.chat.chat_engine' in sys.modules:
    importlib.reload(sys.modules['common.ai_services.chat.chat_engine'])

from common.ai_services.chat.chat_engine import get_conversational_assistant
from django.contrib.auth import get_user_model

User = get_user_model()


class AIQueryTester:
    """Test runner for AI chat queries."""

    def __init__(self):
        """Initialize tester."""
        self.assistant = get_conversational_assistant()
        self.test_user_id = 1  # Use admin user for testing
        self.results = []
        self.start_time = None
        self.end_time = None

    def run_all_tests(self):
        """Run all test categories."""
        print("\n" + "=" * 80)
        print("AI CHAT QUERY COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        self.start_time = time.time()

        # Test categories
        test_categories = [
            ("Data Queries - Geographic", self._test_geographic_queries),
            ("Data Queries - Counting", self._test_counting_queries),
            ("Data Queries - Status Filters", self._test_status_queries),
            ("Data Queries - Entity Listing", self._test_entity_listing),
            ("Help Queries", self._test_help_queries),
            ("Conversational Queries", self._test_conversational),
            ("Edge Cases", self._test_edge_cases),
        ]

        for category_name, test_function in test_categories:
            print(f"\n{'─' * 80}")
            print(f"Category: {category_name}")
            print(f"{'─' * 80}\n")
            test_function()

        self.end_time = time.time()

        # Print summary
        self._print_summary()

        # Save detailed results
        self._save_results()

    def _test_geographic_queries(self):
        """Test queries about specific geographic locations."""
        test_cases = [
            {
                "query": "Tell me about OBC communities in Davao City",
                "expected_intent": "data_query",
                "should_contain_data": True,
            },
            {
                "query": "How many communities are in Region IX?",
                "expected_intent": "data_query",
                "should_contain_data": True,
            },
            {
                "query": "Show me assessments in Zamboanga del Sur",
                "expected_intent": "data_query",
                "should_contain_data": True,
            },
            {
                "query": "List communities in Northern Mindanao",
                "expected_intent": "data_query",
                "should_contain_data": True,
            },
        ]

        for test_case in test_cases:
            self._run_test(test_case)

    def _test_counting_queries(self):
        """Test queries that request counts."""
        test_cases = [
            {
                "query": "How many communities are there?",
                "expected_intent": "data_query",
                "should_contain_data": True,
            },
            {
                "query": "Count workshops in the system",
                "expected_intent": "data_query",
                "should_contain_data": True,
            },
            {
                "query": "Total number of policy recommendations",
                "expected_intent": "data_query",
                "should_contain_data": True,
            },
            {
                "query": "How many projects do we have?",
                "expected_intent": "data_query",
                "should_contain_data": True,
            },
        ]

        for test_case in test_cases:
            self._run_test(test_case)

    def _test_status_queries(self):
        """Test queries with status filters."""
        test_cases = [
            {
                "query": "Show me approved policy recommendations",
                "expected_intent": "data_query",
                "should_contain_data": True,
            },
            {
                "query": "List active projects",
                "expected_intent": "data_query",
                "should_contain_data": True,
            },
            {
                "query": "Find completed workshops",
                "expected_intent": "data_query",
                "should_contain_data": True,
            },
        ]

        for test_case in test_cases:
            self._run_test(test_case)

    def _test_entity_listing(self):
        """Test queries that list entities."""
        test_cases = [
            {
                "query": "List all coordination activities",
                "expected_intent": "data_query",
                "should_contain_data": True,
            },
            {
                "query": "Show me all organizations",
                "expected_intent": "data_query",
                "should_contain_data": True,
            },
            {
                "query": "Display all regions",
                "expected_intent": "data_query",
                "should_contain_data": True,
            },
        ]

        for test_case in test_cases:
            self._run_test(test_case)

    def _test_help_queries(self):
        """Test help-related queries."""
        test_cases = [
            {
                "query": "What can you help me with?",
                "expected_intent": "help",
                "should_contain_data": False,
            },
            {
                "query": "What data do you have?",
                "expected_intent": "help",
                "should_contain_data": False,
            },
            {
                "query": "How do I use this?",
                "expected_intent": "help",
                "should_contain_data": False,
            },
            {
                "query": "Show me example queries",
                "expected_intent": "help",
                "should_contain_data": False,
            },
        ]

        for test_case in test_cases:
            self._run_test(test_case)

    def _test_conversational(self):
        """Test conversational queries."""
        test_cases = [
            {
                "query": "Hello",
                "expected_intent": "general",
                "should_contain_data": False,
            },
            {
                "query": "Good morning",
                "expected_intent": "general",
                "should_contain_data": False,
            },
            {
                "query": "Thank you",
                "expected_intent": "general",
                "should_contain_data": False,
            },
            {
                "query": "Thanks for your help",
                "expected_intent": "general",
                "should_contain_data": False,
            },
        ]

        for test_case in test_cases:
            self._run_test(test_case)

    def _test_edge_cases(self):
        """Test edge cases and potential failures."""
        test_cases = [
            {
                "query": "asdfghjkl",
                "expected_intent": None,  # Should handle gracefully
                "should_contain_data": False,
            },
            {
                "query": "",
                "expected_intent": None,
                "should_contain_data": False,
            },
            {
                "query": "Tell me everything about everything",
                "expected_intent": None,  # Too vague
                "should_contain_data": False,
            },
        ]

        for test_case in test_cases:
            self._run_test(test_case, allow_errors=True)

    def _run_test(self, test_case: Dict[str, Any], allow_errors: bool = False):
        """
        Run a single test case.

        Args:
            test_case: Test case configuration
            allow_errors: If True, don't fail on errors
        """
        query = test_case["query"]
        expected_intent = test_case.get("expected_intent")
        should_contain_data = test_case.get("should_contain_data", False)

        print(f"Query: '{query}'")

        # Execute query
        start = time.time()
        try:
            result = self.assistant.chat(
                user_id=self.test_user_id,
                message=query,
            )
            duration = (time.time() - start) * 1000  # Convert to ms

            # Add delay to avoid rate limiting (only for data queries)
            if test_case.get("expected_intent") == "data_query":
                time.sleep(1.5)  # 1.5 second delay between data queries

        except Exception as e:
            duration = (time.time() - start) * 1000
            result = {"error": str(e), "response": f"ERROR: {str(e)}"}
            if not allow_errors:
                print(f"  ❌ EXCEPTION: {str(e)}\n")
                self.results.append(
                    {
                        "query": query,
                        "status": "EXCEPTION",
                        "error": str(e),
                        "duration_ms": duration,
                    }
                )
                return

        # Analyze result
        status = "PASS"
        issues = []

        # Check 1: Response exists
        if not result.get("response"):
            status = "FAIL"
            issues.append("No response text")

        # Check 2: Intent matches (if specified)
        if expected_intent and result.get("intent") != expected_intent:
            if not allow_errors:
                status = "WARNING"
                issues.append(
                    f"Intent mismatch: expected {expected_intent}, got {result.get('intent')}"
                )

        # Check 3: Should not be error message
        response_text = result.get("response", "").lower()
        if not allow_errors and any(
            phrase in response_text
            for phrase in [
                "could not understand",
                "error occurred",
                "an issue",
                "i'm not sure",
            ]
        ):
            status = "FAIL"
            issues.append("Error message in response")

        # Check 4: Data presence
        if should_contain_data and not result.get("data"):
            status = "WARNING"
            issues.append("No data returned")

        # Check 5: Response time
        if duration > 3000:
            status = "WARNING"
            issues.append(f"Slow response ({duration:.0f}ms)")

        # Print result
        print(f"  Intent: {result.get('intent', 'N/A')} (confidence: {result.get('confidence', 0):.2f})")
        print(f"  Duration: {duration:.0f}ms")
        print(f"  Response: {result.get('response', 'N/A')[:150]}...")

        if status == "PASS":
            print(f"  ✅ {status}")
        elif status == "WARNING":
            print(f"  ⚠️  {status}: {', '.join(issues)}")
        else:
            print(f"  ❌ {status}: {', '.join(issues)}")

        # Show suggestions
        suggestions = result.get("suggestions", [])
        if suggestions:
            print(f"  Suggestions: {', '.join(suggestions[:2])}")

        print()

        # Record result
        self.results.append(
            {
                "query": query,
                "status": status,
                "intent": result.get("intent"),
                "confidence": result.get("confidence", 0),
                "response": result.get("response", ""),
                "data": result.get("data"),
                "suggestions": suggestions,
                "duration_ms": duration,
                "issues": issues,
            }
        )

    def _print_summary(self):
        """Print test summary."""
        total_time = self.end_time - self.start_time

        passed = sum(1 for r in self.results if r["status"] == "PASS")
        warnings = sum(1 for r in self.results if r["status"] == "WARNING")
        failed = sum(1 for r in self.results if r["status"] in ["FAIL", "EXCEPTION"])
        total = len(self.results)

        avg_duration = (
            sum(r["duration_ms"] for r in self.results) / total if total > 0 else 0
        )
        max_duration = max((r["duration_ms"] for r in self.results), default=0)

        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total}")
        print(f"  ✅ Passed:   {passed} ({passed/total*100:.1f}%)")
        print(f"  ⚠️  Warnings: {warnings} ({warnings/total*100:.1f}%)")
        print(f"  ❌ Failed:   {failed} ({failed/total*100:.1f}%)")
        print(f"\nPerformance:")
        print(f"  Average Response Time: {avg_duration:.0f}ms")
        print(f"  Max Response Time: {max_duration:.0f}ms")
        print(f"  Total Test Duration: {total_time:.2f}s")
        print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        # Show failed tests
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for r in self.results:
                if r["status"] in ["FAIL", "EXCEPTION"]:
                    print(f"  - {r['query']}")
                    print(f"    Issues: {', '.join(r.get('issues', []))}")
                    if r.get("error"):
                        print(f"    Error: {r['error']}")

        # Show warnings
        if warnings > 0:
            print("\n⚠️  WARNINGS:")
            for r in self.results:
                if r["status"] == "WARNING":
                    print(f"  - {r['query']}")
                    print(f"    Issues: {', '.join(r.get('issues', []))}")

    def _save_results(self):
        """Save detailed results to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_chat_test_results_{timestamp}.json"

        output = {
            "metadata": {
                "test_date": datetime.now().isoformat(),
                "total_tests": len(self.results),
                "passed": sum(1 for r in self.results if r["status"] == "PASS"),
                "warnings": sum(1 for r in self.results if r["status"] == "WARNING"),
                "failed": sum(1 for r in self.results if r["status"] in ["FAIL", "EXCEPTION"]),
                "total_duration_seconds": self.end_time - self.start_time,
                "average_response_ms": sum(r["duration_ms"] for r in self.results) / len(self.results),
                "has_gemini": self.assistant.has_gemini,
            },
            "results": self.results,
        }

        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, "w") as f:
            json.dump(output, f, indent=2, default=str)

        print(f"\n📄 Detailed results saved to: {filename}")


def main():
    """Main entry point."""
    tester = AIQueryTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
