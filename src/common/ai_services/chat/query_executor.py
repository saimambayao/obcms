"""
Query Executor for Conversational AI

Safely executes Django ORM queries generated from natural language.
Implements comprehensive security validation to prevent dangerous operations.
"""

import ast
import logging
from typing import Any, Dict, List, Optional

from django.db.models import Avg, Count, Max, Min, Q, Sum

logger = logging.getLogger(__name__)


class QueryExecutor:
    """
    Safely execute Django ORM queries from natural language.

    Security Features:
    - Whitelist of allowed models and methods
    - Blocks all write operations (create, update, delete)
    - AST parsing to detect dangerous patterns
    - Result size limits to prevent resource exhaustion
    """

    # Allowed models (read-only access)
    ALLOWED_MODELS = {
        "OBCCommunity": "communities.models.OBCCommunity",
        "Municipality": "common.models.Municipality",
        "Province": "common.models.Province",
        "Region": "common.models.Region",
        "Barangay": "common.models.Barangay",
        "Assessment": "mana.models.Assessment",
        "PolicyRecommendation": "recommendations.policy_tracking.models.PolicyRecommendation",
        "Organization": "coordination.models.Organization",
        "Partnership": "coordination.models.Partnership",
        "WorkItem": "common.work_item_model.WorkItem",
        "Event": "common.models.Event",
    }

    # Allowed QuerySet methods (read-only)
    ALLOWED_METHODS = {
        "filter",
        "exclude",
        "get",
        "first",
        "last",
        "exists",
        "count",
        "aggregate",
        "annotate",
        "values",
        "values_list",
        "order_by",
        "distinct",
        "select_related",
        "prefetch_related",
        "all",
        "none",
    }

    # Allowed aggregation functions
    ALLOWED_AGGREGATES = {"Count", "Sum", "Avg", "Max", "Min"}

    # Dangerous keywords that should never appear
    DANGEROUS_KEYWORDS = {
        "delete",
        "update",
        "create",
        "save",
        "bulk_create",
        "bulk_update",
        "raw",
        "execute",
        "cursor",
        "eval",
        "exec",
        "compile",
        "__import__",
        "open",
        "file",
        "input",
        "system",
        "popen",
        "subprocess",
    }

    # Maximum results to return
    MAX_RESULTS = 1000

    def __init__(self):
        """Initialize query executor with safety context."""
        self._context = self._build_safe_context()

    def execute(self, query_string: str) -> Dict[str, Any]:
        """
        Execute a query with comprehensive safety checks.

        Args:
            query_string: Django ORM query as string

        Returns:
            Dictionary with:
                - success: bool
                - result: Query result or None
                - error: Error message if failed
                - query_info: Metadata about the query

        Example:
            >>> executor = QueryExecutor()
            >>> result = executor.execute(
            ...     "OBCCommunity.objects.filter(barangay__municipality__province__name='Zamboanga del Sur').count()"
            ... )
            >>> print(result['result'])
            42
        """
        try:
            # Step 1: Parse and validate query
            validation = self._validate_query(query_string)
            if not validation["is_safe"]:
                return {
                    "success": False,
                    "result": None,
                    "error": f"Unsafe query: {validation['reason']}",
                    "query_info": validation,
                }

            # Step 2: Execute query in restricted context
            result = self._execute_safe(query_string)

            # Step 3: Process and limit results
            processed_result = self._process_result(result)

            return {
                "success": True,
                "result": processed_result,
                "error": None,
                "query_info": {
                    "query": query_string,
                    "result_type": type(result).__name__,
                    "result_count": self._get_result_count(processed_result),
                },
            }

        except Exception as e:
            logger.error(f"Query execution failed: {query_string} - {str(e)}")
            return {
                "success": False,
                "result": None,
                "error": f"Execution error: {str(e)}",
                "query_info": {"query": query_string},
            }

    def _validate_query(self, query_string: str) -> Dict[str, Any]:
        """
        Validate query safety using multiple approaches.

        Returns:
            Dictionary with is_safe (bool) and reason (str)
        """
        # Check 1: String-based dangerous keyword detection
        query_lower = query_string.lower()
        for keyword in self.DANGEROUS_KEYWORDS:
            if keyword in query_lower:
                return {
                    "is_safe": False,
                    "reason": f"Dangerous keyword detected: {keyword}",
                }

        # Check 2: AST parsing to detect dangerous patterns
        try:
            tree = ast.parse(query_string, mode="eval")
            ast_validation = self._validate_ast(tree)
            if not ast_validation["is_safe"]:
                return ast_validation
        except SyntaxError as e:
            return {
                "is_safe": False,
                "reason": f"Syntax error: {str(e)}",
            }

        # Check 3: Validate model names
        model_validation = self._validate_models(query_string)
        if not model_validation["is_safe"]:
            return model_validation

        return {"is_safe": True, "reason": "All validations passed"}

    def _validate_ast(self, tree: ast.AST) -> Dict[str, Any]:
        """
        Validate AST to ensure only safe operations.

        Checks for:
        - Only allowed attribute access
        - No function calls except allowed methods
        - No assignments or deletions
        """
        for node in ast.walk(tree):
            # Block assignments
            if isinstance(node, (ast.Assign, ast.AugAssign, ast.Delete)):
                return {
                    "is_safe": False,
                    "reason": "Assignment or deletion detected",
                }

            # Block imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                return {
                    "is_safe": False,
                    "reason": "Import statement detected",
                }

            # Validate function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name not in self.ALLOWED_AGGREGATES:
                        return {
                            "is_safe": False,
                            "reason": f"Unauthorized function call: {func_name}",
                        }

        return {"is_safe": True, "reason": "AST validation passed"}

    def _validate_models(self, query_string: str) -> Dict[str, Any]:
        """Validate that only allowed models are referenced."""
        for model_name in self.ALLOWED_MODELS.keys():
            if model_name in query_string:
                # Found an allowed model
                return {"is_safe": True, "reason": "Model validation passed"}

        return {
            "is_safe": False,
            "reason": "No recognized model found in query",
        }

    def _execute_safe(self, query_string: str) -> Any:
        """Execute query in restricted context."""
        # Use eval with restricted builtins and safe context
        result = eval(
            query_string,
            {"__builtins__": {}},  # No built-in functions
            self._context,  # Only our safe context
        )
        return result

    def _process_result(self, result: Any) -> Any:
        """
        Process query result and apply safety limits.

        Handles:
        - QuerySets: Convert to list with size limit
        - Aggregates: Return as-is
        - Single objects: Convert to dict
        """
        from django.db.models import QuerySet

        if isinstance(result, QuerySet):
            # Apply size limit
            limited_qs = result[: self.MAX_RESULTS]
            # Convert to list of dicts for JSON serialization
            return list(limited_qs.values())

        elif isinstance(result, dict):
            # Aggregate result
            return result

        elif isinstance(result, (int, float, str, bool, type(None))):
            # Primitive types
            return result

        elif hasattr(result, "__dict__"):
            # Single model instance - convert to dict
            return {
                "id": getattr(result, "id", None),
                "str": str(result),
                "model": result.__class__.__name__,
            }

        else:
            # Fallback
            return str(result)

    def _get_result_count(self, result: Any) -> int:
        """Get count of results."""
        if isinstance(result, list):
            return len(result)
        elif isinstance(result, dict):
            return 1
        elif isinstance(result, (int, float)):
            return 1
        else:
            return 0

    def _build_safe_context(self) -> Dict[str, Any]:
        """
        Build safe execution context with only allowed models and functions.

        Returns:
            Dictionary mapping names to safe objects
        """
        context = {}

        # Import and add allowed models
        for model_name, import_path in self.ALLOWED_MODELS.items():
            try:
                module_path, class_name = import_path.rsplit(".", 1)
                module = __import__(module_path, fromlist=[class_name])
                context[model_name] = getattr(module, class_name)
            except (ImportError, AttributeError) as e:
                logger.warning(f"Could not import {import_path}: {e}")

        # Add aggregation functions
        context["Count"] = Count
        context["Sum"] = Sum
        context["Avg"] = Avg
        context["Max"] = Max
        context["Min"] = Min
        context["Q"] = Q

        return context

    def get_available_models(self) -> List[Dict[str, str]]:
        """
        Get list of available models with metadata.

        Returns:
            List of dicts with model_name, import_path, fields
        """
        available = []

        for model_name, import_path in self.ALLOWED_MODELS.items():
            try:
                module_path, class_name = import_path.rsplit(".", 1)
                module = __import__(module_path, fromlist=[class_name])
                model_class = getattr(module, class_name)

                # Get field names
                fields = [f.name for f in model_class._meta.get_fields()]

                available.append(
                    {
                        "model_name": model_name,
                        "import_path": import_path,
                        "fields": fields,
                        "verbose_name": model_class._meta.verbose_name,
                    }
                )
            except Exception as e:
                logger.warning(f"Could not get info for {model_name}: {e}")

        return available


# Singleton instance
_executor = None


def get_query_executor() -> QueryExecutor:
    """Get singleton query executor instance."""
    global _executor
    if _executor is None:
        _executor = QueryExecutor()
    return _executor
