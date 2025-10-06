"""
Management command to update FAQ cache with current statistics.

This command queries the database for current statistics and updates
the FAQ handler's cache. Should be run daily via cron job.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from common.ai_services.chat.faq_handler import FAQHandler
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Update FAQ handler statistics cache."""

    help = "Updates FAQ cache with current statistics from database"

    def add_arguments(self, parser):
        parser.add_argument(
            '--show-stats',
            action='store_true',
            help='Display FAQ statistics after update',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )

    def handle(self, *args, **options):
        show_stats = options['show_stats']
        verbose = options['verbose']

        self.stdout.write(
            self.style.NOTICE(
                f"\n{'='*70}\n"
                f"FAQ Cache Update - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"{'='*70}\n"
            )
        )

        try:
            # Initialize FAQ handler
            if verbose:
                self.stdout.write("Initializing FAQ handler...")

            faq_handler = FAQHandler()

            # Update statistics cache
            if verbose:
                self.stdout.write("Querying database for current statistics...")

            stats = faq_handler.update_stats_cache()

            # Display results
            if stats:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n✅ Successfully updated {len(stats)} FAQ statistics:\n"
                    )
                )

                if verbose:
                    for key, value in stats.items():
                        self.stdout.write(f"\n{key}:")
                        self.stdout.write(f"  {value}\n")
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "\n⚠️  No statistics were generated. Check database content."
                    )
                )

            # Show FAQ handler stats if requested
            if show_stats:
                self._display_faq_stats(faq_handler)

            self.stdout.write(
                self.style.SUCCESS(
                    f"\n{'='*70}\n"
                    f"✅ FAQ cache update complete!\n"
                    f"   Cache TTL: 24 hours\n"
                    f"   Next update recommended: {(timezone.now() + timezone.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"{'='*70}\n"
                )
            )

        except ImportError as e:
            self.stdout.write(
                self.style.ERROR(
                    f"\n❌ ERROR: Failed to import required modules.\n"
                    f"   {str(e)}\n"
                    f"   Make sure all apps are properly installed.\n"
                )
            )
            logger.error(f"FAQ cache update failed: {e}")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"\n❌ ERROR: Failed to update FAQ cache.\n"
                    f"   {str(e)}\n"
                )
            )
            logger.error(f"FAQ cache update failed: {e}", exc_info=True)

    def _display_faq_stats(self, faq_handler: FAQHandler):
        """
        Display FAQ handler statistics.

        Args:
            faq_handler: FAQHandler instance
        """
        self.stdout.write(
            self.style.NOTICE(
                f"\n{'='*70}\n"
                f"FAQ Handler Statistics\n"
                f"{'='*70}\n"
            )
        )

        stats = faq_handler.get_faq_stats()

        self.stdout.write(
            f"\nTotal FAQs: {stats['total_faqs']}\n"
            f"Total Hits: {stats['total_hits']}\n"
            f"FAQs with Hits: {stats['faqs_with_hits']}\n"
            f"Hit Rate: {stats['hit_rate']}%\n"
        )

        if stats['popular_faqs']:
            self.stdout.write("\nTop 5 Popular FAQs:")
            for i, faq in enumerate(stats['popular_faqs'], 1):
                self.stdout.write(
                    f"\n{i}. {faq['pattern']} "
                    f"({faq['hit_count']} hits, category: {faq['category']})"
                )
                if faq['answer']:
                    # Show first 100 chars of answer
                    answer_preview = faq['answer'][:100]
                    if len(faq['answer']) > 100:
                        answer_preview += '...'
                    self.stdout.write(f"   Answer: {answer_preview}")

        self.stdout.write(f"\n{'='*70}\n")
