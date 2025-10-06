"""
Visual Query Builder for OBCMS Chat System

Provides step-by-step UI for building guaranteed-valid queries.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from django.db.models import Q, Count, Avg, Sum, Max, Min
from django.apps import apps


@dataclass
class QueryResult:
    """Result of a built query execution"""

    success: bool
    data: Any
    query_text: str
    count: Optional[int] = None
    error: Optional[str] = None


class QueryBuilder:
    """Visual query builder - guaranteed to work"""

    # Entity type configurations
    ENTITY_CONFIGS = {
        "communities": {
            "model": "common.Barangay",
            "display_name": "Communities",
            "query_types": ["count", "list", "aggregate"],
            "filters": {
                "region": {
                    "type": "dropdown",
                    "required": False,
                    "field": "municipality__province__region__name",
                    "label": "Region",
                    "dynamic": True,
                },
                "province": {
                    "type": "dropdown",
                    "required": False,
                    "field": "municipality__province__name",
                    "label": "Province",
                    "dynamic": True,
                },
                "municipality": {
                    "type": "dropdown",
                    "required": False,
                    "field": "municipality__name",
                    "label": "Municipality",
                    "dynamic": True,
                },
                "ethnolinguistic_group": {
                    "type": "dropdown",
                    "required": False,
                    "field": "obcprofile__dominant_ethnolinguistic_group",
                    "label": "Ethnolinguistic Group",
                    "options": [
                        "All",
                        "Maranao",
                        "Maguindanao",
                        "Tausug",
                        "Sama",
                        "Yakan",
                        "Iranun",
                        "Kalagan",
                        "Kolibugan",
                        "Mixed",
                        "Other",
                    ],
                },
                "livelihood": {
                    "type": "dropdown",
                    "required": False,
                    "field": "obcprofile__primary_livelihood",
                    "label": "Primary Livelihood",
                    "options": [
                        "All",
                        "Farming",
                        "Fishing",
                        "Trading",
                        "Services",
                        "Crafts",
                        "Other",
                    ],
                },
            },
            "aggregates": {
                "total_population": {
                    "field": "obcprofile__total_obc_population",
                    "operation": "sum",
                    "label": "Total OBC Population",
                },
                "total_households": {
                    "field": "obcprofile__total_obc_households",
                    "operation": "sum",
                    "label": "Total OBC Households",
                },
                "avg_population": {
                    "field": "obcprofile__total_obc_population",
                    "operation": "avg",
                    "label": "Average Population per Barangay",
                },
            },
        },
        "workshops": {
            "model": "coordination.Workshop",
            "display_name": "Workshops",
            "query_types": ["count", "list", "aggregate"],
            "filters": {
                "status": {
                    "type": "dropdown",
                    "required": False,
                    "field": "status",
                    "label": "Status",
                    "options": [
                        "All",
                        "draft",
                        "scheduled",
                        "ongoing",
                        "completed",
                        "cancelled",
                    ],
                },
                "date_from": {
                    "type": "date",
                    "required": False,
                    "field": "start_date__gte",
                    "label": "From Date",
                },
                "date_to": {
                    "type": "date",
                    "required": False,
                    "field": "end_date__lte",
                    "label": "To Date",
                },
            },
            "aggregates": {
                "total_participants": {
                    "field": "attendance_count",
                    "operation": "sum",
                    "label": "Total Participants",
                },
                "avg_participants": {
                    "field": "attendance_count",
                    "operation": "avg",
                    "label": "Average Participants per Workshop",
                },
            },
        },
        "policies": {
            "model": "policies.PolicyRecommendation",
            "display_name": "Policies",
            "query_types": ["count", "list", "aggregate"],
            "filters": {
                "status": {
                    "type": "dropdown",
                    "required": False,
                    "field": "status",
                    "label": "Status",
                    "options": [
                        "All",
                        "draft",
                        "under_review",
                        "approved",
                        "implemented",
                        "rejected",
                    ],
                },
                "priority": {
                    "type": "dropdown",
                    "required": False,
                    "field": "priority_level",
                    "label": "Priority Level",
                    "options": ["All", "critical", "high", "medium", "low"],
                },
            },
            "aggregates": {
                "total_policies": {
                    "field": "id",
                    "operation": "count",
                    "label": "Total Policies",
                }
            },
        },
        "stakeholders": {
            "model": "coordination.Stakeholder",
            "display_name": "Stakeholders",
            "query_types": ["count", "list"],
            "filters": {
                "type": {
                    "type": "dropdown",
                    "required": False,
                    "field": "organization__type",
                    "label": "Organization Type",
                    "options": [
                        "All",
                        "government",
                        "ngo",
                        "private_sector",
                        "academic",
                        "community",
                        "international",
                    ],
                },
                "region": {
                    "type": "dropdown",
                    "required": False,
                    "field": "region__name",
                    "label": "Region",
                    "dynamic": True,
                },
            },
            "aggregates": {},
        },
    }

    def __init__(self):
        """Initialize query builder"""
        pass

    def get_available_entities(self) -> List[Dict[str, str]]:
        """Get list of entities that can be queried"""
        return [
            {
                "value": key,
                "label": config["display_name"],
                "icon": self._get_entity_icon(key),
            }
            for key, config in self.ENTITY_CONFIGS.items()
        ]

    def get_builder_config(self, entity_type: str) -> Dict:
        """
        Get configuration for building query about entity_type

        Args:
            entity_type: Type of entity (e.g., 'communities', 'workshops')

        Returns:
            Configuration dict with filters, query types, etc.
        """
        if entity_type not in self.ENTITY_CONFIGS:
            raise ValueError(f"Unknown entity type: {entity_type}")

        config = self.ENTITY_CONFIGS[entity_type].copy()

        # Resolve dynamic filter options
        for filter_key, filter_config in config["filters"].items():
            if filter_config.get("dynamic"):
                config["filters"][filter_key]["options"] = self._get_dynamic_options(
                    entity_type, filter_key
                )

        return config

    def _get_dynamic_options(self, entity_type: str, filter_key: str) -> List[str]:
        """Get dynamic filter options from database"""
        config = self.ENTITY_CONFIGS[entity_type]
        filter_config = config["filters"][filter_key]

        # Get model
        model = apps.get_model(config["model"])

        # Get field path
        field_path = filter_config["field"]

        try:
            # Get distinct values
            values = (
                model.objects.values_list(field_path, flat=True)
                .distinct()
                .order_by(field_path)
            )
            return ["All"] + [str(v) for v in values if v]
        except Exception:
            return ["All"]

    def build_query(self, selections: Dict) -> str:
        """
        Build natural language query from selections

        Args:
            selections: User's filter selections

        Returns:
            Natural language query string
        """
        entity_type = selections.get("entity_type", "")
        query_type = selections.get("query_type", "count")
        filters = selections.get("filters", {})

        config = self.ENTITY_CONFIGS.get(entity_type, {})
        entity_name = config.get("display_name", entity_type)

        # Build query text
        parts = []

        if query_type == "count":
            parts.append(f"How many {entity_name.lower()}")
        elif query_type == "list":
            parts.append(f"List all {entity_name.lower()}")
        elif query_type == "aggregate":
            aggregate = selections.get("aggregate", "")
            if aggregate:
                aggregate_config = config.get("aggregates", {}).get(aggregate, {})
                parts.append(f"What is the {aggregate_config.get('label', aggregate)}")
        else:
            parts.append(f"Show {entity_name.lower()}")

        # Add filters
        filter_parts = []
        for key, value in filters.items():
            if value and value != "All":
                filter_config = config.get("filters", {}).get(key, {})
                label = filter_config.get("label", key)
                filter_parts.append(f"{label}: {value}")

        if filter_parts:
            parts.append("where " + " AND ".join(filter_parts))

        return " ".join(parts) + "?"

    def preview_query(self, selections: Dict) -> Dict:
        """
        Show preview of what query will return

        Args:
            selections: User's filter selections

        Returns:
            Preview info including expected result type and count estimate
        """
        entity_type = selections.get("entity_type", "")
        query_type = selections.get("query_type", "count")

        config = self.ENTITY_CONFIGS.get(entity_type, {})
        model = apps.get_model(config["model"])

        # Build queryset
        queryset = self._build_queryset(entity_type, selections)

        # Get count
        count = queryset.count()

        # Build preview
        preview = {
            "query_text": self.build_query(selections),
            "result_type": query_type,
            "estimated_count": count,
            "entity_type": entity_type,
        }

        if query_type == "aggregate":
            aggregate = selections.get("aggregate", "")
            if aggregate:
                aggregate_config = config.get("aggregates", {}).get(aggregate, {})
                preview["aggregate_label"] = aggregate_config.get("label", aggregate)

        return preview

    def execute_built_query(self, selections: Dict) -> QueryResult:
        """
        Execute the built query (guaranteed valid)

        Args:
            selections: User's filter selections

        Returns:
            QueryResult with data
        """
        try:
            entity_type = selections.get("entity_type", "")
            query_type = selections.get("query_type", "count")

            config = self.ENTITY_CONFIGS.get(entity_type, {})
            queryset = self._build_queryset(entity_type, selections)

            query_text = self.build_query(selections)

            if query_type == "count":
                count = queryset.count()
                return QueryResult(
                    success=True,
                    data=count,
                    query_text=query_text,
                    count=count,
                )

            elif query_type == "list":
                items = list(queryset[:50])  # Limit to 50 items
                return QueryResult(
                    success=True,
                    data=items,
                    query_text=query_text,
                    count=len(items),
                )

            elif query_type == "aggregate":
                aggregate = selections.get("aggregate", "")
                aggregate_config = config.get("aggregates", {}).get(aggregate, {})

                field = aggregate_config.get("field")
                operation = aggregate_config.get("operation", "sum")

                if operation == "sum":
                    result = queryset.aggregate(total=Sum(field))["total"]
                elif operation == "avg":
                    result = queryset.aggregate(average=Avg(field))["average"]
                elif operation == "max":
                    result = queryset.aggregate(maximum=Max(field))["maximum"]
                elif operation == "min":
                    result = queryset.aggregate(minimum=Min(field))["minimum"]
                elif operation == "count":
                    result = queryset.aggregate(total=Count(field))["total"]
                else:
                    result = None

                return QueryResult(
                    success=True,
                    data=result,
                    query_text=query_text,
                    count=queryset.count(),
                )

            else:
                return QueryResult(
                    success=False,
                    data=None,
                    query_text=query_text,
                    error=f"Unknown query type: {query_type}",
                )

        except Exception as e:
            return QueryResult(
                success=False,
                data=None,
                query_text=self.build_query(selections),
                error=str(e),
            )

    def _build_queryset(self, entity_type: str, selections: Dict):
        """Build Django queryset from selections"""
        config = self.ENTITY_CONFIGS[entity_type]
        model = apps.get_model(config["model"])

        queryset = model.objects.all()

        # Apply filters
        filters = selections.get("filters", {})
        for key, value in filters.items():
            if not value or value == "All":
                continue

            filter_config = config["filters"].get(key, {})
            field = filter_config.get("field", key)

            if filter_config.get("type") == "date":
                # Date filters use the field as-is (already includes __gte or __lte)
                queryset = queryset.filter(**{field: value})
            else:
                # For other filters, use exact match or icontains
                if "__" in field:
                    queryset = queryset.filter(**{field: value})
                else:
                    queryset = queryset.filter(**{f"{field}__icontains": value})

        return queryset

    def _get_entity_icon(self, entity_type: str) -> str:
        """Get FontAwesome icon for entity type"""
        icons = {
            "communities": "fa-users",
            "workshops": "fa-chalkboard-teacher",
            "policies": "fa-file-alt",
            "stakeholders": "fa-handshake",
        }
        return icons.get(entity_type, "fa-question")
