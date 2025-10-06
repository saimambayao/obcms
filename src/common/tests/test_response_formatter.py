"""
Test suite for Response Formatter (Advanced Phase 2).

Tests the 5 new formatter methods:
- format_count_response
- format_list_response
- format_aggregate_response
- format_trend_response
- format_comparison_response

Target: Clear, readable output with proper formatting
"""

from django.test import TestCase

from common.ai_services.chat.response_formatter import ResponseFormatter


class FormatCountResponseTestCase(TestCase):
    """Test suite for format_count_response method."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = ResponseFormatter()

    def test_format_count_zero(self):
        """Test formatting zero count."""
        result = self.formatter.format_count_response(0, "communities")
        self.assertEqual(result, "No communities found")

    def test_format_count_one(self):
        """Test formatting count of one."""
        result = self.formatter.format_count_response(1, "communities")
        self.assertEqual(result, "Found 1 community")

    def test_format_count_multiple(self):
        """Test formatting multiple count."""
        result = self.formatter.format_count_response(15, "communities")
        self.assertEqual(result, "Found 15 communities")

    def test_format_count_with_filters(self):
        """Test formatting count with filters."""
        filters = {"region": "Region IX", "status": "active"}
        result = self.formatter.format_count_response(15, "communities", filters)

        self.assertIn("Found 15 communities", result)
        self.assertIn("region: Region IX", result)
        self.assertIn("status: active", result)

    def test_format_count_large_number(self):
        """Test formatting large count with thousands separator."""
        result = self.formatter.format_count_response(1500, "communities")
        self.assertIn("1,500", result)

    def test_format_count_singular_nonstandard(self):
        """Test singularization of non-standard plurals."""
        result = self.formatter.format_count_response(1, "assessments")
        self.assertEqual(result, "Found 1 assessment")


class FormatListResponseTestCase(TestCase):
    """Test suite for format_list_response method."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = ResponseFormatter()

    def test_format_list_empty(self):
        """Test formatting empty list."""
        result = self.formatter.format_list_response([], "communities")
        self.assertEqual(result, "No communities to display")

    def test_format_list_bulleted(self):
        """Test bulleted list formatting."""
        items = [
            {"name": "Community A"},
            {"name": "Community B"},
            {"name": "Community C"},
        ]
        result = self.formatter.format_list_response(items, "communities", "bulleted")

        self.assertIn("Communities (3):", result)
        self.assertIn("• Community A", result)
        self.assertIn("• Community B", result)
        self.assertIn("• Community C", result)

    def test_format_list_numbered(self):
        """Test numbered list formatting."""
        items = [
            {"name": "Item 1"},
            {"name": "Item 2"},
        ]
        result = self.formatter.format_list_response(items, "items", "numbered")

        self.assertIn("Items (2):", result)
        self.assertIn("1. Item 1", result)
        self.assertIn("2. Item 2", result)

    def test_format_list_truncation(self):
        """Test long item name truncation."""
        items = [
            {"name": "A" * 100},  # Very long name
        ]
        result = self.formatter.format_list_response(items, "items")

        # Should be truncated to 80 chars with ellipsis
        self.assertIn("...", result)
        self.assertLess(len(result.split('\n')[1]), 90)  # Line should be under 90 chars

    def test_format_list_title_fallback(self):
        """Test fallback to title field if name not present."""
        items = [
            {"title": "Assessment Title"},
        ]
        result = self.formatter.format_list_response(items, "assessments")

        self.assertIn("Assessment Title", result)

    def test_format_list_description_fallback(self):
        """Test fallback to description if name and title not present."""
        items = [
            {"description": "Some description"},
        ]
        result = self.formatter.format_list_response(items, "items")

        self.assertIn("Some description", result)


class FormatAggregateResponseTestCase(TestCase):
    """Test suite for format_aggregate_response method."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = ResponseFormatter()

    def test_format_aggregate_basic(self):
        """Test basic aggregate formatting."""
        data = {
            "total": 150,
            "average": 15,
            "min": 5,
            "max": 30,
        }
        result = self.formatter.format_aggregate_response(data, "population")

        self.assertIn("Population Statistics:", result)
        self.assertIn("Total: 150", result)
        self.assertIn("Average: 15", result)
        self.assertIn("Min: 5", result)
        self.assertIn("Max: 30", result)

    def test_format_aggregate_currency(self):
        """Test currency formatting for budget metrics."""
        data = {
            "total": 150000,
            "average": 5000,
        }
        result = self.formatter.format_aggregate_response(data, "budget")

        self.assertIn("Budget Statistics:", result)
        self.assertIn("₱150,000", result)
        self.assertIn("₱5,000", result)

    def test_format_aggregate_float_values(self):
        """Test float value formatting."""
        data = {
            "average": 123.456,
            "median": 100.5,
        }
        result = self.formatter.format_aggregate_response(data, "score")

        self.assertIn("123.46", result)  # Should round to 2 decimals
        self.assertIn("100.50", result)

    def test_format_aggregate_currency_float(self):
        """Test currency formatting with decimal values."""
        data = {
            "total": 123456.78,
        }
        result = self.formatter.format_aggregate_response(data, "funding")

        self.assertIn("₱123,456.78", result)

    def test_format_aggregate_underscore_keys(self):
        """Test formatting of keys with underscores."""
        data = {
            "total_population": 1000,
            "avg_household_size": 5,
        }
        result = self.formatter.format_aggregate_response(data, "demographics")

        self.assertIn("Total Population:", result)
        self.assertIn("Avg Household Size:", result)


class FormatTrendResponseTestCase(TestCase):
    """Test suite for format_trend_response method."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = ResponseFormatter()

    def test_format_trend_insufficient_data(self):
        """Test trend with insufficient data."""
        data = [{"month": "Jan", "value": 10}]
        result = self.formatter.format_trend_response(data, "monthly")

        self.assertIn("Insufficient data", result)

    def test_format_trend_basic(self):
        """Test basic trend formatting."""
        data = [
            {"month": "Jan", "value": 10},
            {"month": "Feb", "value": 15},
            {"month": "Mar", "value": 12},
        ]
        result = self.formatter.format_trend_response(data, "monthly")

        self.assertIn("Trend Analysis (Monthly):", result)
        self.assertIn("Jan: 10", result)
        self.assertIn("Feb: 15", result)
        self.assertIn("Mar: 12", result)

    def test_format_trend_with_percentage(self):
        """Test trend with percentage change calculation."""
        data = [
            {"month": "Jan", "value": 100},
            {"month": "Feb", "value": 150},  # 50% increase
        ]
        result = self.formatter.format_trend_response(data, "monthly")

        self.assertIn("Jan: 100", result)
        self.assertIn("Feb: 150", result)
        self.assertIn("↑50.0%", result)  # Should show increase arrow

    def test_format_trend_decrease(self):
        """Test trend with decrease."""
        data = [
            {"period": "Q1", "count": 100},
            {"period": "Q2", "count": 80},  # 20% decrease
        ]
        result = self.formatter.format_trend_response(data, "quarterly")

        self.assertIn("↓20.0%", result)  # Should show decrease arrow

    def test_format_trend_no_change(self):
        """Test trend with no change."""
        data = [
            {"month": "Jan", "value": 100},
            {"month": "Feb", "value": 100},  # No change
        ]
        result = self.formatter.format_trend_response(data, "monthly")

        self.assertIn("→0.0%", result)  # Should show no change arrow

    def test_format_trend_date_field_fallback(self):
        """Test trend with date field instead of month."""
        data = [
            {"date": "2024-01", "value": 10},
            {"date": "2024-02", "value": 15},
        ]
        result = self.formatter.format_trend_response(data, "monthly")

        self.assertIn("2024-01:", result)
        self.assertIn("2024-02:", result)

    def test_format_trend_large_numbers(self):
        """Test trend with large numbers using thousands separator."""
        data = [
            {"month": "Jan", "value": 1000},
            {"month": "Feb", "value": 1500},
        ]
        result = self.formatter.format_trend_response(data, "monthly")

        self.assertIn("1,000", result)
        self.assertIn("1,500", result)


class FormatComparisonResponseTestCase(TestCase):
    """Test suite for format_comparison_response method."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = ResponseFormatter()

    def test_format_comparison_basic(self):
        """Test basic comparison formatting."""
        data1 = {"communities": 15, "assessments": 8}
        data2 = {"communities": 20, "assessments": 5}

        result = self.formatter.format_comparison_response(
            data1, data2, "Region IX", "Region X"
        )

        self.assertIn("Comparison (Region IX vs Region X):", result)
        self.assertIn("Communities:", result)
        self.assertIn("15 vs 20", result)
        self.assertIn("Assessments:", result)
        self.assertIn("8 vs 5", result)

    def test_format_comparison_with_delta(self):
        """Test comparison with delta calculation."""
        data1 = {"total": 100}
        data2 = {"total": 150}

        result = self.formatter.format_comparison_response(data1, data2, "A", "B")

        self.assertIn("Δ+50", result)  # Should show positive delta

    def test_format_comparison_negative_delta(self):
        """Test comparison with negative delta."""
        data1 = {"value": 150}
        data2 = {"value": 100}

        result = self.formatter.format_comparison_response(data1, data2, "Before", "After")

        self.assertIn("Δ-50", result)  # Should show negative delta

    def test_format_comparison_no_change(self):
        """Test comparison with no change."""
        data1 = {"count": 50}
        data2 = {"count": 50}

        result = self.formatter.format_comparison_response(data1, data2, "A", "B")

        self.assertIn("=", result)  # Should show equals

    def test_format_comparison_float_values(self):
        """Test comparison with float values."""
        data1 = {"average": 123.45}
        data2 = {"average": 234.56}

        result = self.formatter.format_comparison_response(data1, data2, "X", "Y")

        self.assertIn("123.45", result)
        self.assertIn("234.56", result)

    def test_format_comparison_missing_keys(self):
        """Test comparison with missing keys in one dataset."""
        data1 = {"a": 10, "b": 20}
        data2 = {"b": 30, "c": 40}

        result = self.formatter.format_comparison_response(data1, data2, "Data1", "Data2")

        # Should handle missing keys gracefully (treat as 0)
        self.assertIn("A:", result)
        self.assertIn("B:", result)
        self.assertIn("C:", result)

    def test_format_comparison_underscore_keys(self):
        """Test comparison with underscore in keys."""
        data1 = {"total_count": 100}
        data2 = {"total_count": 150}

        result = self.formatter.format_comparison_response(data1, data2, "A", "B")

        self.assertIn("Total Count:", result)

    def test_format_comparison_large_numbers(self):
        """Test comparison with large numbers."""
        data1 = {"population": 1500000}
        data2 = {"population": 2000000}

        result = self.formatter.format_comparison_response(data1, data2, "City A", "City B")

        self.assertIn("1,500,000", result)
        self.assertIn("2,000,000", result)
        self.assertIn("Δ+500,000", result)


class ResponseFormatterIntegrationTestCase(TestCase):
    """Integration tests for response formatter."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = ResponseFormatter()

    def test_all_formatters_output_strings(self):
        """Test that all advanced formatters return strings."""
        # Count
        result1 = self.formatter.format_count_response(10, "items")
        self.assertIsInstance(result1, str)

        # List
        result2 = self.formatter.format_list_response([{"name": "A"}], "items")
        self.assertIsInstance(result2, str)

        # Aggregate
        result3 = self.formatter.format_aggregate_response({"total": 100}, "metric")
        self.assertIsInstance(result3, str)

        # Trend
        result4 = self.formatter.format_trend_response(
            [{"month": "A", "value": 1}, {"month": "B", "value": 2}], "period"
        )
        self.assertIsInstance(result4, str)

        # Comparison
        result5 = self.formatter.format_comparison_response({"a": 1}, {"a": 2})
        self.assertIsInstance(result5, str)

    def test_formatter_handles_edge_cases(self):
        """Test that formatters handle edge cases gracefully."""
        # Empty data
        self.formatter.format_list_response([], "items")
        self.formatter.format_aggregate_response({}, "metric")

        # None values
        self.formatter.format_count_response(0, "items")

        # Mixed data types
        data = {"int": 1, "float": 1.5, "str": "text"}
        result = self.formatter.format_aggregate_response(data, "mixed")
        self.assertIn("Int:", result)
        self.assertIn("Float:", result)
        self.assertIn("Str:", result)
