"""
Management command to index all communities into the vector store.

Usage:
    python manage.py index_communities
    python manage.py index_communities --limit 100
    python manage.py index_communities --rebuild
"""

import time
from typing import Optional

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from ai_assistant.models import DocumentEmbedding
from ai_assistant.services.embedding_service import get_embedding_service
from ai_assistant.services.vector_store import VectorStore
from communities.models import OBCCommunity


class Command(BaseCommand):
    help = "Index all OBC communities into the vector store for semantic search"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Limit the number of communities to index",
        )
        parser.add_argument(
            "--rebuild",
            action="store_true",
            help="Rebuild the entire index from scratch",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force re-indexing even if content hash matches",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        rebuild = options["rebuild"]
        force = options["force"]

        self.stdout.write(self.style.SUCCESS("Starting community indexing..."))

        # Initialize services
        embedding_service = get_embedding_service()
        index_name = "communities"

        # Load or create vector store
        if rebuild:
            self.stdout.write(self.style.WARNING("Rebuilding index from scratch..."))
            vector_store = VectorStore(
                index_name=index_name, dimension=embedding_service.get_dimension()
            )
            # Clear existing embeddings
            DocumentEmbedding.objects.filter(index_name=index_name).delete()
        else:
            vector_store = VectorStore.load_or_create(
                index_name=index_name, dimension=embedding_service.get_dimension()
            )

        # Get communities to index
        communities_qs = OBCCommunity.objects.select_related(
            "barangay",
            "barangay__municipality",
            "barangay__municipality__province",
            "barangay__municipality__province__region",
        ).all()

        if limit:
            communities_qs = communities_qs[:limit]

        total_communities = communities_qs.count()
        self.stdout.write(f"Found {total_communities} communities to index")

        # Index communities
        indexed_count = 0
        skipped_count = 0
        error_count = 0
        start_time = time.time()

        for i, community in enumerate(communities_qs, 1):
            try:
                # Format community as text
                text = self._format_community_text(community)

                # Compute content hash
                content_hash = embedding_service.compute_content_hash(text)

                # Check if already indexed and unchanged
                if not force:
                    existing = DocumentEmbedding.objects.filter(
                        content_type__model="obccommunity",
                        object_id=community.id,
                        index_name=index_name,
                        embedding_hash=content_hash,
                    ).first()

                    if existing:
                        skipped_count += 1
                        if i % 50 == 0:
                            self.stdout.write(
                                f"Progress: {i}/{total_communities} "
                                f"(indexed: {indexed_count}, skipped: {skipped_count})"
                            )
                        continue

                # Generate embedding
                embedding = embedding_service.generate_embedding(text)

                # Add to vector store
                position = vector_store.add_vector(
                    embedding,
                    metadata={
                        "id": community.id,
                        "type": "community",
                        "module": "communities",
                        "data": {
                            "community_names": community.community_names,
                            "barangay": community.barangay.name,
                            "municipality": community.barangay.municipality.name,
                            "province": community.barangay.municipality.province.name,
                            "region": community.barangay.municipality.province.region.name,
                        },
                    },
                )

                # Save metadata to database
                doc_embedding, created = DocumentEmbedding.get_or_create_for_object(
                    community, index_name=index_name, embedding_hash=content_hash
                )
                if not created:
                    doc_embedding.embedding_hash = content_hash
                    doc_embedding.updated_at = time.time()
                doc_embedding.index_position = position
                doc_embedding.save()

                indexed_count += 1

                # Progress update
                if i % 50 == 0:
                    elapsed = time.time() - start_time
                    rate = i / elapsed if elapsed > 0 else 0
                    self.stdout.write(
                        f"Progress: {i}/{total_communities} "
                        f"(indexed: {indexed_count}, skipped: {skipped_count}, "
                        f"rate: {rate:.1f} docs/sec)"
                    )

            except Exception as e:
                error_count += 1
                self.stderr.write(
                    self.style.ERROR(
                        f"Error indexing community {community.id} ({community.community_names}): {e}"
                    )
                )

        # Save vector store
        self.stdout.write("Saving vector store...")
        vector_store.save()

        # Final summary
        elapsed_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f"\n=== Indexing Complete ===\n"
                f"Total communities: {total_communities}\n"
                f"Indexed: {indexed_count}\n"
                f"Skipped (unchanged): {skipped_count}\n"
                f"Errors: {error_count}\n"
                f"Time: {elapsed_time:.2f} seconds\n"
                f"Rate: {total_communities / elapsed_time:.1f} docs/sec\n"
                f"Vector store size: {vector_store.vector_count} vectors"
            )
        )

    def _format_community_text(self, community) -> str:
        """Format community data as text for embedding."""
        parts = [
            f"Community Names: {community.community_names}",
            f"Barangay: {community.barangay.name}",
            f"Municipality: {community.barangay.municipality.name}",
            f"Province: {community.barangay.municipality.province.name}",
            f"Region: {community.barangay.municipality.province.region.name}",
        ]

        if community.estimated_obc_population:
            parts.append(f"Population: {community.estimated_obc_population}")

        if community.households:
            parts.append(f"Households: {community.households}")

        # Add additional fields if they exist
        if (
            hasattr(community, "ethnolinguistic_groups")
            and community.ethnolinguistic_groups
        ):
            parts.append(f"Ethnolinguistic Groups: {community.ethnolinguistic_groups}")

        if hasattr(community, "primary_livelihoods") and community.primary_livelihoods:
            parts.append(f"Primary Livelihoods: {community.primary_livelihoods}")

        if hasattr(community, "notes") and community.notes:
            parts.append(f"Notes: {community.notes}")

        return "\n".join(parts)
