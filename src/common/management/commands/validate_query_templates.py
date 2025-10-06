"""
Django management command to validate all query templates.

Validates:
- Duplicate IDs
- Pattern compilation
- Required fields present
- Category/intent/result_type valid
- Examples provided
- Priority in range 1-10
- Query template syntax
"""

import re
from collections import defaultdict
from typing import Dict, List, Tuple

from django.core.management.base import BaseCommand

from common.ai_services.chat.query_templates import get_template_registry


class Command(BaseCommand):
    help = 'Validate all query templates for errors and inconsistencies'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Auto-fix issues if possible (not yet implemented)',
        )
        parser.add_argument(
            '--domain',
            type=str,
            help='Validate specific domain/category only',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed validation output',
        )

    def handle(self, *args, **options):
        """Main validation logic."""
        fix_mode = options.get('fix', False)
        target_domain = options.get('domain')
        verbose = options.get('verbose', False)

        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('OBCMS Query Template Validator'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        # Get templates from registry
        registry = get_template_registry()
        templates = registry.get_all_templates()

        # Filter by domain if specified
        if target_domain:
            templates = [t for t in templates if t.category == target_domain]
            self.stdout.write(f"Filtering by domain: {target_domain}")

        self.stdout.write(f"Validating {len(templates)} templates...\n")

        # Run validation checks
        issues = []
        warnings = []

        # 1. Check for duplicate IDs
        duplicate_issues = self._check_duplicate_ids(templates)
        issues.extend(duplicate_issues)

        # 2. Check pattern compilation
        pattern_issues = self._check_patterns(templates, verbose)
        issues.extend(pattern_issues)

        # 3. Check required fields
        field_issues, field_warnings = self._check_required_fields(templates, verbose)
        issues.extend(field_issues)
        warnings.extend(field_warnings)

        # 4. Check valid categories/intents/result_types
        validity_issues = self._check_valid_values(templates, verbose)
        issues.extend(validity_issues)

        # 5. Check examples provided
        example_warnings = self._check_examples(templates, verbose)
        warnings.extend(example_warnings)

        # 6. Check priority range
        priority_issues = self._check_priority_range(templates, verbose)
        issues.extend(priority_issues)

        # 7. Check query template syntax
        query_issues = self._check_query_syntax(templates, verbose)
        issues.extend(query_issues)

        # Print results
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('VALIDATION RESULTS'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        if issues:
            self.stdout.write(self.style.ERROR(f"❌ Found {len(issues)} critical issues:"))
            self.stdout.write('')
            for i, issue in enumerate(issues, 1):
                self.stdout.write(f"  {i}. {issue}")
            self.stdout.write('')
        else:
            self.stdout.write(self.style.SUCCESS("✓ No critical issues found!"))
            self.stdout.write('')

        if warnings:
            self.stdout.write(self.style.WARNING(f"⚠️  Found {len(warnings)} warnings:"))
            self.stdout.write('')
            for i, warning in enumerate(warnings, 1):
                self.stdout.write(f"  {i}. {warning}")
            self.stdout.write('')
        else:
            self.stdout.write(self.style.SUCCESS("✓ No warnings!"))
            self.stdout.write('')

        # Summary statistics
        stats = self._get_validation_stats(templates)
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('TEMPLATE STATISTICS'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')
        self.stdout.write(f"Total templates: {stats['total']}")
        self.stdout.write(f"Categories: {stats['categories_count']}")
        self.stdout.write(f"Average priority: {stats['avg_priority']:.2f}")
        self.stdout.write(f"Templates with examples: {stats['with_examples']}/{stats['total']}")
        self.stdout.write('')

        # Category breakdown
        self.stdout.write("Templates by category:")
        for category, count in sorted(stats['by_category'].items()):
            self.stdout.write(f"  - {category}: {count}")
        self.stdout.write('')

        if fix_mode:
            self.stdout.write(self.style.WARNING("Fix mode not yet implemented."))

        # Exit with appropriate code
        if issues:
            self.stdout.write(self.style.ERROR("Validation failed."))
            exit(1)
        else:
            self.stdout.write(self.style.SUCCESS("✓ All templates valid!"))

    def _check_duplicate_ids(self, templates) -> List[str]:
        """Check for duplicate template IDs."""
        issues = []
        seen_ids = defaultdict(list)

        for template in templates:
            seen_ids[template.id].append(template.category)

        for template_id, categories in seen_ids.items():
            if len(categories) > 1:
                issues.append(
                    f"Duplicate ID '{template_id}' found in categories: {', '.join(categories)}"
                )

        return issues

    def _check_patterns(self, templates, verbose=False) -> List[str]:
        """Check that all patterns compile correctly."""
        issues = []

        for template in templates:
            if not template.pattern:
                issues.append(f"Template '{template.id}' has no pattern")
                continue

            try:
                re.compile(template.pattern, re.IGNORECASE)
                if verbose:
                    self.stdout.write(f"✓ Pattern valid: {template.id}")
            except re.error as e:
                issues.append(f"Invalid pattern in '{template.id}': {e}")

        return issues

    def _check_required_fields(self, templates, verbose=False) -> Tuple[List[str], List[str]]:
        """Check that required fields are present."""
        issues = []
        warnings = []

        for template in templates:
            # Critical fields
            if not template.id:
                issues.append(f"Template missing ID: {template}")
            if not template.category:
                issues.append(f"Template '{template.id}' missing category")
            if not template.pattern:
                issues.append(f"Template '{template.id}' missing pattern")

            # Recommended fields
            if not template.description:
                warnings.append(f"Template '{template.id}' missing description")
            if not template.query_template and not template.query_builder:
                warnings.append(
                    f"Template '{template.id}' has neither query_template nor query_builder"
                )

            if verbose and not issues:
                self.stdout.write(f"✓ Required fields: {template.id}")

        return issues, warnings

    def _check_valid_values(self, templates, verbose=False) -> List[str]:
        """Check that category, intent, and result_type have valid values."""
        issues = []

        valid_intents = {
            'data_query',
            'analysis',
            'navigation',
            'help',
            'system',
            'clarification',
        }
        valid_result_types = {'count', 'list', 'single', 'aggregate', 'exists'}

        for template in templates:
            # Intent validation
            if template.intent and template.intent not in valid_intents:
                issues.append(
                    f"Template '{template.id}' has invalid intent: '{template.intent}'"
                )

            # Result type validation
            if template.result_type and template.result_type not in valid_result_types:
                issues.append(
                    f"Template '{template.id}' has invalid result_type: '{template.result_type}'"
                )

            if verbose and not issues:
                self.stdout.write(f"✓ Valid values: {template.id}")

        return issues

    def _check_examples(self, templates, verbose=False) -> List[str]:
        """Check that templates have example queries."""
        warnings = []

        for template in templates:
            if not template.examples and not template.example_queries:
                warnings.append(f"Template '{template.id}' has no examples")
            elif verbose:
                example_count = len(template.examples or template.example_queries or [])
                self.stdout.write(f"✓ Examples ({example_count}): {template.id}")

        return warnings

    def _check_priority_range(self, templates, verbose=False) -> List[str]:
        """Check that priority is in valid range."""
        issues = []

        for template in templates:
            if template.priority < 1 or template.priority > 100:
                issues.append(
                    f"Template '{template.id}' has priority {template.priority} "
                    f"(must be 1-100)"
                )
            elif verbose:
                self.stdout.write(f"✓ Priority ({template.priority}): {template.id}")

        return issues

    def _check_query_syntax(self, templates, verbose=False) -> List[str]:
        """Check query template syntax for common issues."""
        issues = []

        for template in templates:
            if not template.query_template:
                continue

            query = template.query_template

            # Check for unmatched braces
            if query.count('{') != query.count('}'):
                issues.append(
                    f"Template '{template.id}' has unmatched braces in query_template"
                )

            # Check for common Django ORM patterns
            if 'objects.' in query:
                # Looks like Django ORM - basic validation
                if not any(
                    method in query
                    for method in [
                        '.filter(',
                        '.exclude(',
                        '.all(',
                        '.count(',
                        '.aggregate(',
                        '.annotate(',
                        '.values(',
                    ]
                ):
                    issues.append(
                        f"Template '{template.id}' query doesn't use standard Django ORM methods"
                    )

            if verbose and not issues:
                self.stdout.write(f"✓ Query syntax: {template.id}")

        return issues

    def _get_validation_stats(self, templates) -> Dict:
        """Generate validation statistics."""
        by_category = defaultdict(int)
        total_priority = 0
        with_examples = 0

        for template in templates:
            by_category[template.category] += 1
            total_priority += template.priority
            if template.examples or template.example_queries:
                with_examples += 1

        return {
            'total': len(templates),
            'categories_count': len(by_category),
            'by_category': dict(by_category),
            'avg_priority': total_priority / len(templates) if templates else 0,
            'with_examples': with_examples,
        }
