"""
Management command to rebuild all vector indices from scratch.

Usage:
    python manage.py rebuild_vector_index
    python manage.py rebuild_vector_index --indices communities policies
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Rebuild all vector indices from scratch'

    def add_arguments(self, parser):
        parser.add_argument(
            '--indices',
            nargs='+',
            default=['communities', 'policies'],
            help='Space-separated list of indices to rebuild (default: communities policies)'
        )

    def handle(self, *args, **options):
        indices = options['indices']

        self.stdout.write(self.style.SUCCESS(
            f'Rebuilding vector indices: {", ".join(indices)}\n'
        ))

        # Rebuild each index
        for index_name in indices:
            self.stdout.write(self.style.WARNING(f'\n--- Rebuilding {index_name} index ---'))

            if index_name == 'communities':
                call_command('index_communities', rebuild=True)
            elif index_name == 'policies':
                call_command('index_policies', rebuild=True)
            elif index_name == 'assessments':
                # Will be implemented when MANA models are ready
                self.stdout.write(
                    self.style.WARNING(f'Assessments indexing not yet implemented')
                )
            else:
                self.stderr.write(
                    self.style.ERROR(f'Unknown index: {index_name}')
                )

        self.stdout.write(self.style.SUCCESS(
            f'\n=== All indices rebuilt successfully ===\n'
        ))
