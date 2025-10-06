"""
Django management command to auto-generate query template documentation.

Generates:
- Query reference by domain/category
- Example queries list
- Entity types reference
- Intent types reference
- Statistics and coverage analysis
"""

import os
from collections import defaultdict
from datetime import datetime
from typing import Dict, List

from django.core.management.base import BaseCommand

from common.ai_services.chat.query_templates import get_template_registry


class Command(BaseCommand):
    help = 'Generate comprehensive documentation from query templates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='docs/ai/queries/QUERY_REFERENCE.md',
            help='Output file path (default: docs/ai/queries/QUERY_REFERENCE.md)',
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['markdown', 'html'],
            default='markdown',
            help='Output format (default: markdown)',
        )
        parser.add_argument(
            '--include-stats',
            action='store_true',
            help='Include detailed statistics',
        )
        parser.add_argument(
            '--examples-only',
            action='store_true',
            help='Generate only example queries list',
        )

    def handle(self, *args, **options):
        """Main documentation generation."""
        output_file = options['output']
        output_format = options['format']
        include_stats = options.get('include_stats', False)
        examples_only = options.get('examples_only', False)

        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('OBCMS Query Documentation Generator'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        # Get all templates
        registry = get_template_registry()
        templates = registry.get_all_templates()

        self.stdout.write(f"Processing {len(templates)} templates...")
        self.stdout.write('')

        # Generate documentation
        if output_format == 'markdown':
            if examples_only:
                content = self._generate_examples_only(templates)
            else:
                content = self._generate_markdown_doc(templates, include_stats)
        else:
            content = self._generate_html_doc(templates, include_stats)

        # Ensure output directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            self.stdout.write(f"Created directory: {output_dir}")

        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        self.stdout.write(self.style.SUCCESS(f"✓ Documentation generated: {output_file}"))
        self.stdout.write(f"  Size: {len(content)} characters")
        self.stdout.write(f"  Lines: {content.count(chr(10))}")

    def _generate_markdown_doc(self, templates: List, include_stats: bool) -> str:
        """Generate markdown documentation."""
        lines = []

        # Header
        lines.append("# OBCMS AI Chat Query Reference")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Total Templates:** {len(templates)}")
        lines.append("")

        # Table of Contents
        lines.append("## Table of Contents")
        lines.append("")

        by_category = self._group_by_category(templates)

        for i, (category, category_templates) in enumerate(
            sorted(by_category.items()), 1
        ):
            lines.append(
                f"{i}. [{category.upper()}](#{category.lower().replace(' ', '-')}) "
                f"({len(category_templates)} templates)"
            )

        lines.append("")

        # Statistics (if requested)
        if include_stats:
            lines.append("## Statistics")
            lines.append("")
            stats = self._calculate_stats(templates)
            lines.extend(self._format_stats_markdown(stats))
            lines.append("")

        # Quick Reference: Common Queries
        lines.append("## Quick Reference: Common Queries")
        lines.append("")
        lines.append("Here are some example queries you can try:")
        lines.append("")

        common_examples = self._get_common_examples(templates)
        for category, examples in common_examples.items():
            lines.append(f"### {category}")
            lines.append("")
            for example in examples[:5]:  # Top 5 per category
                lines.append(f"- {example}")
            lines.append("")

        # Detailed Template Reference
        lines.append("---")
        lines.append("")
        lines.append("## Detailed Template Reference")
        lines.append("")

        for category, category_templates in sorted(by_category.items()):
            lines.append(f"## {category.upper()}")
            lines.append("")
            lines.append(f"**Total Templates:** {len(category_templates)}")
            lines.append("")

            # Sort by priority (highest first)
            sorted_templates = sorted(
                category_templates, key=lambda t: t.priority, reverse=True
            )

            for template in sorted_templates:
                lines.extend(self._format_template_markdown(template))
                lines.append("")

        # Entity Reference
        lines.append("---")
        lines.append("")
        lines.append("## Entity Types Reference")
        lines.append("")
        entity_ref = self._build_entity_reference(templates)
        lines.extend(self._format_entity_reference_markdown(entity_ref))
        lines.append("")

        # Intent Reference
        lines.append("---")
        lines.append("")
        lines.append("## Intent Types Reference")
        lines.append("")
        intent_ref = self._build_intent_reference(templates)
        lines.extend(self._format_intent_reference_markdown(intent_ref))

        return "\n".join(lines)

    def _generate_examples_only(self, templates: List) -> str:
        """Generate a simple list of all example queries."""
        lines = []

        lines.append("# OBCMS AI Chat - Example Queries")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        by_category = self._group_by_category(templates)

        for category, category_templates in sorted(by_category.items()):
            lines.append(f"## {category.upper()}")
            lines.append("")

            all_examples = []
            for template in category_templates:
                examples = template.examples or template.example_queries or []
                all_examples.extend(examples)

            # Remove duplicates while preserving order
            seen = set()
            unique_examples = []
            for example in all_examples:
                if example not in seen:
                    seen.add(example)
                    unique_examples.append(example)

            for example in unique_examples:
                lines.append(f"- {example}")

            lines.append("")

        return "\n".join(lines)

    def _generate_html_doc(self, templates: List, include_stats: bool) -> str:
        """Generate HTML documentation."""
        # Basic HTML structure
        html = []
        html.append("<!DOCTYPE html>")
        html.append("<html>")
        html.append("<head>")
        html.append("  <title>OBCMS Query Reference</title>")
        html.append("  <meta charset='utf-8'>")
        html.append("  <style>")
        html.append(self._get_html_styles())
        html.append("  </style>")
        html.append("</head>")
        html.append("<body>")
        html.append("  <div class='container'>")

        # Header
        html.append("    <h1>OBCMS AI Chat Query Reference</h1>")
        html.append(
            f"    <p class='meta'>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
        )
        html.append(f"    <p class='meta'>Total Templates: {len(templates)}</p>")

        # Categories
        by_category = self._group_by_category(templates)

        for category, category_templates in sorted(by_category.items()):
            html.append(f"    <h2>{category.upper()}</h2>")
            html.append(
                f"    <p>{len(category_templates)} templates in this category</p>"
            )

            for template in sorted(category_templates, key=lambda t: t.priority, reverse=True):
                html.append("    <div class='template'>")
                html.append(f"      <h3>{template.id}</h3>")
                html.append(f"      <p><strong>Description:</strong> {template.description}</p>")
                html.append(f"      <p><strong>Priority:</strong> {template.priority}</p>")

                examples = template.examples or template.example_queries or []
                if examples:
                    html.append("      <p><strong>Examples:</strong></p>")
                    html.append("      <ul>")
                    for example in examples[:3]:
                        html.append(f"        <li>{example}</li>")
                    html.append("      </ul>")

                html.append("    </div>")

        html.append("  </div>")
        html.append("</body>")
        html.append("</html>")

        return "\n".join(html)

    def _format_template_markdown(self, template) -> List[str]:
        """Format a single template as markdown."""
        lines = []

        lines.append(f"### {template.id}")
        lines.append("")

        if template.description:
            lines.append(f"**Description:** {template.description}")
            lines.append("")

        lines.append(f"**Priority:** {template.priority}/100")
        lines.append(f"**Intent:** {template.intent}")
        lines.append(f"**Result Type:** {template.result_type}")
        lines.append("")

        # Required entities
        if template.required_entities:
            lines.append(f"**Required Entities:** {', '.join(template.required_entities)}")
            lines.append("")

        # Optional entities
        if template.optional_entities:
            lines.append(f"**Optional Entities:** {', '.join(template.optional_entities)}")
            lines.append("")

        # Examples
        examples = template.examples or template.example_queries or []
        if examples:
            lines.append("**Example Queries:**")
            for example in examples[:5]:  # Show up to 5 examples
                lines.append(f"- `{example}`")
            lines.append("")

        # Query template (first 100 chars)
        if template.query_template:
            query_preview = template.query_template[:100]
            if len(template.query_template) > 100:
                query_preview += "..."
            lines.append(f"**Query Template:** `{query_preview}`")
            lines.append("")

        return lines

    def _group_by_category(self, templates: List) -> Dict:
        """Group templates by category."""
        by_category = defaultdict(list)
        for template in templates:
            by_category[template.category].append(template)
        return by_category

    def _calculate_stats(self, templates: List) -> Dict:
        """Calculate template statistics."""
        stats = {
            'total_templates': len(templates),
            'by_category': defaultdict(int),
            'by_intent': defaultdict(int),
            'by_result_type': defaultdict(int),
            'avg_priority': 0,
            'templates_with_examples': 0,
            'total_examples': 0,
            'avg_required_entities': 0,
        }

        total_priority = 0
        total_required_entities = 0

        for template in templates:
            stats['by_category'][template.category] += 1
            stats['by_intent'][template.intent] += 1
            stats['by_result_type'][template.result_type] += 1
            total_priority += template.priority
            total_required_entities += len(template.required_entities)

            examples = template.examples or template.example_queries or []
            if examples:
                stats['templates_with_examples'] += 1
                stats['total_examples'] += len(examples)

        stats['avg_priority'] = total_priority / len(templates) if templates else 0
        stats['avg_required_entities'] = (
            total_required_entities / len(templates) if templates else 0
        )

        return stats

    def _format_stats_markdown(self, stats: Dict) -> List[str]:
        """Format statistics as markdown."""
        lines = []

        lines.append(f"- **Total Templates:** {stats['total_templates']}")
        lines.append(f"- **Average Priority:** {stats['avg_priority']:.2f}")
        lines.append(
            f"- **Templates with Examples:** {stats['templates_with_examples']}/{stats['total_templates']}"
        )
        lines.append(f"- **Total Examples:** {stats['total_examples']}")
        lines.append("")

        lines.append("**By Category:**")
        for category, count in sorted(stats['by_category'].items()):
            lines.append(f"- {category}: {count}")
        lines.append("")

        lines.append("**By Intent:**")
        for intent, count in sorted(stats['by_intent'].items()):
            lines.append(f"- {intent}: {count}")
        lines.append("")

        lines.append("**By Result Type:**")
        for result_type, count in sorted(stats['by_result_type'].items()):
            lines.append(f"- {result_type}: {count}")

        return lines

    def _get_common_examples(self, templates: List) -> Dict[str, List[str]]:
        """Get common example queries by category."""
        by_category = self._group_by_category(templates)
        common_examples = {}

        for category, category_templates in by_category.items():
            examples = []
            # Get high-priority templates
            high_priority = sorted(
                category_templates, key=lambda t: t.priority, reverse=True
            )[:10]

            for template in high_priority:
                template_examples = template.examples or template.example_queries or []
                if template_examples:
                    examples.append(template_examples[0])  # First example

            common_examples[category] = examples

        return common_examples

    def _build_entity_reference(self, templates: List) -> Dict:
        """Build entity type reference."""
        entity_ref = defaultdict(lambda: {'count': 0, 'templates': []})

        for template in templates:
            for entity in template.required_entities + template.optional_entities:
                entity_ref[entity]['count'] += 1
                entity_ref[entity]['templates'].append(template.id)

        return dict(entity_ref)

    def _format_entity_reference_markdown(self, entity_ref: Dict) -> List[str]:
        """Format entity reference as markdown."""
        lines = []

        for entity, data in sorted(entity_ref.items(), key=lambda x: x[1]['count'], reverse=True):
            lines.append(f"### {entity}")
            lines.append("")
            lines.append(f"**Used in {data['count']} templates**")
            lines.append("")
            lines.append(f"Templates: {', '.join(data['templates'][:10])}")
            if len(data['templates']) > 10:
                lines.append(f"... and {len(data['templates']) - 10} more")
            lines.append("")

        return lines

    def _build_intent_reference(self, templates: List) -> Dict:
        """Build intent type reference."""
        intent_ref = defaultdict(lambda: {'count': 0, 'templates': []})

        for template in templates:
            intent_ref[template.intent]['count'] += 1
            intent_ref[template.intent]['templates'].append(template.id)

        return dict(intent_ref)

    def _format_intent_reference_markdown(self, intent_ref: Dict) -> List[str]:
        """Format intent reference as markdown."""
        lines = []

        for intent, data in sorted(intent_ref.items()):
            lines.append(f"### {intent}")
            lines.append("")
            lines.append(f"**{data['count']} templates use this intent**")
            lines.append("")

        return lines

    def _get_html_styles(self) -> str:
        """Get CSS styles for HTML output."""
        return """
body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
.container { max-width: 1200px; margin: 0 auto; background: white; padding: 40px; }
h1 { color: #2563eb; border-bottom: 3px solid #2563eb; padding-bottom: 10px; }
h2 { color: #059669; margin-top: 40px; }
h3 { color: #7c3aed; }
.meta { color: #666; font-style: italic; }
.template { border: 1px solid #e5e7eb; padding: 20px; margin: 20px 0; border-radius: 8px; }
ul { line-height: 1.8; }
code { background: #f3f4f6; padding: 2px 6px; border-radius: 3px; }
"""
