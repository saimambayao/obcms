"""
Management command to index all policy recommendations into the vector store.

Usage:
    python manage.py index_policies
    python manage.py index_policies --limit 50
    python manage.py index_policies --rebuild
"""

import time

from django.core.management.base import BaseCommand

from ai_assistant.models import DocumentEmbedding
from ai_assistant.services.embedding_service import get_embedding_service
from ai_assistant.services.vector_store import VectorStore
from recommendations.policy_tracking.models import PolicyRecommendation


class Command(BaseCommand):
    help = 'Index all policy recommendations into the vector store for semantic search'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit the number of policies to index'
        )
        parser.add_argument(
            '--rebuild',
            action='store_true',
            help='Rebuild the entire index from scratch'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-indexing even if content hash matches'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        rebuild = options['rebuild']
        force = options['force']

        self.stdout.write(self.style.SUCCESS('Starting policy indexing...'))

        # Initialize services
        embedding_service = get_embedding_service()
        index_name = 'policies'

        # Load or create vector store
        if rebuild:
            self.stdout.write(self.style.WARNING('Rebuilding index from scratch...'))
            vector_store = VectorStore(
                index_name=index_name,
                dimension=embedding_service.get_dimension()
            )
            DocumentEmbedding.objects.filter(index_name=index_name).delete()
        else:
            vector_store = VectorStore.load_or_create(
                index_name=index_name,
                dimension=embedding_service.get_dimension()
            )

        # Get policies to index
        policies_qs = PolicyRecommendation.objects.all()

        if limit:
            policies_qs = policies_qs[:limit]

        total_policies = policies_qs.count()
        self.stdout.write(f'Found {total_policies} policies to index')

        # Index policies
        indexed_count = 0
        skipped_count = 0
        error_count = 0
        start_time = time.time()

        for i, policy in enumerate(policies_qs, 1):
            try:
                # Format policy as text
                text = self._format_policy_text(policy)

                # Compute content hash
                content_hash = embedding_service.compute_content_hash(text)

                # Check if already indexed and unchanged
                if not force:
                    existing = DocumentEmbedding.objects.filter(
                        content_type__model='policyrecommendation',
                        object_id=policy.id,
                        index_name=index_name,
                        embedding_hash=content_hash
                    ).first()

                    if existing:
                        skipped_count += 1
                        if i % 20 == 0:
                            self.stdout.write(
                                f'Progress: {i}/{total_policies} '
                                f'(indexed: {indexed_count}, skipped: {skipped_count})'
                            )
                        continue

                # Generate embedding
                embedding = embedding_service.generate_embedding(text)

                # Add to vector store
                position = vector_store.add_vector(
                    embedding,
                    metadata={
                        'id': policy.id,
                        'type': 'policy',
                        'module': 'recommendations',
                        'data': {
                            'title': policy.title,
                            'status': policy.status,
                            'sector': policy.sector if hasattr(policy, 'sector') else None,
                        }
                    }
                )

                # Save metadata to database
                doc_embedding, created = DocumentEmbedding.get_or_create_for_object(
                    policy,
                    index_name=index_name,
                    embedding_hash=content_hash
                )
                if not created:
                    doc_embedding.embedding_hash = content_hash
                doc_embedding.index_position = position
                doc_embedding.save()

                indexed_count += 1

                # Progress update
                if i % 20 == 0:
                    elapsed = time.time() - start_time
                    rate = i / elapsed if elapsed > 0 else 0
                    self.stdout.write(
                        f'Progress: {i}/{total_policies} '
                        f'(indexed: {indexed_count}, skipped: {skipped_count}, '
                        f'rate: {rate:.1f} docs/sec)'
                    )

            except Exception as e:
                error_count += 1
                self.stderr.write(
                    self.style.ERROR(
                        f'Error indexing policy {policy.id} ({policy.title}): {e}'
                    )
                )

        # Save vector store
        self.stdout.write('Saving vector store...')
        vector_store.save()

        # Final summary
        elapsed_time = time.time() - start_time
        self.stdout.write(self.style.SUCCESS(
            f'\n=== Indexing Complete ===\n'
            f'Total policies: {total_policies}\n'
            f'Indexed: {indexed_count}\n'
            f'Skipped (unchanged): {skipped_count}\n'
            f'Errors: {error_count}\n'
            f'Time: {elapsed_time:.2f} seconds\n'
            f'Rate: {total_policies / elapsed_time:.1f} docs/sec\n'
            f'Vector store size: {vector_store.vector_count} vectors'
        ))

    def _format_policy_text(self, policy) -> str:
        """Format policy data as text for embedding."""
        parts = [
            f"Title: {policy.title}",
            f"Status: {policy.get_status_display()}",
        ]

        if policy.description:
            parts.append(f"Description: {policy.description}")

        if hasattr(policy, 'sector') and policy.sector:
            parts.append(f"Sector: {policy.get_sector_display()}")

        if hasattr(policy, 'priority_level') and policy.priority_level:
            parts.append(f"Priority: {policy.get_priority_level_display()}")

        if hasattr(policy, 'target_communities') and policy.target_communities:
            parts.append(f"Target Communities: {policy.target_communities}")

        if hasattr(policy, 'expected_impact') and policy.expected_impact:
            parts.append(f"Expected Impact: {policy.expected_impact}")

        if hasattr(policy, 'evidence_summary') and policy.evidence_summary:
            parts.append(f"Evidence: {policy.evidence_summary}")

        return "\n".join(parts)
