"""
Management command to check AI infrastructure health.

Usage:
    python manage.py ai_health_check
    python manage.py ai_health_check --verbose
"""

import sys
from decimal import Decimal

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.utils import timezone

from ai_assistant.cultural_context import BangsomoroCulturalContext
from ai_assistant.models import AIOperation
from ai_assistant.services.cache_service import CacheService
from ai_assistant.services.gemini_service import GeminiService
from ai_assistant.utils.cost_tracker import CostTracker


class Command(BaseCommand):
    help = 'Check AI infrastructure health and configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )

    def handle(self, *args, **options):
        verbose = options['verbose']

        self.stdout.write(self.style.HTTP_INFO("\n" + "=" * 60))
        self.stdout.write(self.style.HTTP_INFO("AI INFRASTRUCTURE HEALTH CHECK"))
        self.stdout.write(self.style.HTTP_INFO("=" * 60 + "\n"))

        # Track overall health
        all_healthy = True

        # 1. Check Google API Key
        self.stdout.write(self.style.HTTP_INFO("1. Checking Google API Key..."))
        api_key = getattr(settings, 'GOOGLE_API_KEY', None)
        if api_key:
            masked_key = f"{api_key[:10]}...{api_key[-4:]}" if len(api_key) > 14 else "***"
            self.stdout.write(
                self.style.SUCCESS(
                    f"   ✓ API Key configured: {masked_key}"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    "   ✗ API Key NOT configured"
                )
            )
            all_healthy = False

        # 2. Check Gemini Service
        self.stdout.write(self.style.HTTP_INFO("\n2. Checking Gemini Service..."))
        try:
            gemini = GeminiService()
            self.stdout.write(
                self.style.SUCCESS(
                    f"   ✓ Gemini service initialized (model: {gemini.model_name})"
                )
            )

            # Test API call (if API key exists)
            if api_key:
                try:
                    test_result = gemini.generate_text(
                        "Hello! Respond with 'OK' if you receive this.",
                        include_cultural_context=False
                    )
                    if test_result['success']:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"   ✓ API call successful "
                                f"({test_result['response_time']:.2f}s, "
                                f"{test_result['tokens_used']} tokens, "
                                f"${test_result['cost']:.6f})"
                            )
                        )
                        if verbose:
                            self.stdout.write(
                                f"      Response: {test_result['text'][:100]}"
                            )
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f"   ✗ API call failed: {test_result.get('error', 'Unknown error')}"
                            )
                        )
                        all_healthy = False
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"   ✗ API test failed: {str(e)}"
                        )
                    )
                    all_healthy = False
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"   ✗ Gemini service failed: {str(e)}"
                )
            )
            all_healthy = False

        # 3. Check Redis/Cache
        self.stdout.write(self.style.HTTP_INFO("\n3. Checking Cache (Redis)..."))
        try:
            # Test cache write
            test_key = "health_check_test"
            test_value = {"test": True, "timestamp": timezone.now().isoformat()}
            cache.set(test_key, test_value, 60)

            # Test cache read
            retrieved = cache.get(test_key)
            if retrieved == test_value:
                self.stdout.write(
                    self.style.SUCCESS(
                        "   ✓ Cache read/write successful"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "   ⚠ Cache read/write mismatch"
                    )
                )

            # Test cache service
            cache_service = CacheService()
            stats = cache_service.get_stats()
            self.stdout.write(
                self.style.SUCCESS(
                    f"   ✓ Cache service initialized"
                )
            )
            if verbose:
                self.stdout.write(
                    f"      Stats: {stats['hits']} hits, "
                    f"{stats['misses']} misses, "
                    f"{stats['hit_rate']:.1f}% hit rate"
                )

            # Clean up
            cache.delete(test_key)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"   ✗ Cache check failed: {str(e)}"
                )
            )
            all_healthy = False

        # 4. Check Cultural Context
        self.stdout.write(self.style.HTTP_INFO("\n4. Checking Cultural Context..."))
        try:
            cultural_context = BangsomoroCulturalContext()
            base_context = cultural_context.get_base_context()
            self.stdout.write(
                self.style.SUCCESS(
                    f"   ✓ Cultural context loaded ({len(base_context)} chars)"
                )
            )
            if verbose:
                guidelines = cultural_context.get_policy_guidelines()
                self.stdout.write(
                    f"      Ethnolinguistic groups: {len(cultural_context.ethnolinguistic_groups)}"
                )
                self.stdout.write(
                    f"      Policy guidelines: {len(guidelines)} categories"
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"   ✗ Cultural context failed: {str(e)}"
                )
            )
            all_healthy = False

        # 5. Check AIOperation Model
        self.stdout.write(self.style.HTTP_INFO("\n5. Checking AI Operation Logging..."))
        try:
            # Get today's stats
            today_stats = AIOperation.get_daily_stats()
            self.stdout.write(
                self.style.SUCCESS(
                    "   ✓ AIOperation model accessible"
                )
            )
            if verbose or today_stats['total_operations'] > 0:
                self.stdout.write(
                    f"      Today's operations: {today_stats['total_operations']}"
                )
                self.stdout.write(
                    f"      Successful: {today_stats['successful']}, "
                    f"Failed: {today_stats['failed']}, "
                    f"Cached: {today_stats['cached']}"
                )
                self.stdout.write(
                    f"      Total cost: ${today_stats['total_cost']:.4f}"
                )
                self.stdout.write(
                    f"      Total tokens: {today_stats['total_tokens']:,}"
                )
                self.stdout.write(
                    f"      Avg response time: {today_stats['avg_response_time']:.2f}s"
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"   ✗ AIOperation check failed: {str(e)}"
                )
            )
            all_healthy = False

        # 6. Check Cost Tracking
        self.stdout.write(self.style.HTTP_INFO("\n6. Checking Cost Tracking..."))
        try:
            cost_tracker = CostTracker()
            daily_cost = cost_tracker.get_daily_cost()
            monthly_cost = cost_tracker.get_monthly_cost()

            self.stdout.write(
                self.style.SUCCESS(
                    "   ✓ Cost tracker operational"
                )
            )
            self.stdout.write(
                f"      Today's cost: ${daily_cost:.4f}"
            )
            self.stdout.write(
                f"      This month's cost: ${monthly_cost:.4f}"
            )

            # Check budget alerts (example: $10/day, $100/month)
            daily_budget = Decimal('10.00')
            monthly_budget = Decimal('100.00')
            alert_info = cost_tracker.check_budget_alert(daily_budget, monthly_budget)

            if alert_info['has_alerts']:
                for alert in alert_info['alerts']:
                    if alert['severity'] == 'critical':
                        self.stdout.write(
                            self.style.ERROR(
                                f"      🚨 {alert['message']}"
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"      ⚠️  {alert['message']}"
                            )
                        )

            if verbose:
                suggestions = cost_tracker.get_optimization_suggestions()
                self.stdout.write("\n      Optimization Suggestions:")
                for i, suggestion in enumerate(suggestions[:3], 1):
                    self.stdout.write(f"      {i}. {suggestion}")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"   ✗ Cost tracking failed: {str(e)}"
                )
            )
            all_healthy = False

        # 7. Configuration Summary
        if verbose:
            self.stdout.write(self.style.HTTP_INFO("\n7. Configuration Summary:"))
            self.stdout.write(f"      Django version: {settings.VERSION if hasattr(settings, 'VERSION') else 'Unknown'}")
            self.stdout.write(f"      Debug mode: {settings.DEBUG}")
            self.stdout.write(f"      Time zone: {settings.TIME_ZONE}")
            self.stdout.write(f"      AI Assistant installed: {'ai_assistant' in settings.INSTALLED_APPS}")

        # Final Summary
        self.stdout.write(self.style.HTTP_INFO("\n" + "=" * 60))
        if all_healthy:
            self.stdout.write(
                self.style.SUCCESS(
                    "✓ ALL SYSTEMS HEALTHY"
                )
            )
            self.stdout.write(self.style.SUCCESS("=" * 60 + "\n"))
            sys.exit(0)
        else:
            self.stdout.write(
                self.style.ERROR(
                    "✗ SOME SYSTEMS REQUIRE ATTENTION"
                )
            )
            self.stdout.write(self.style.ERROR("=" * 60 + "\n"))
            sys.exit(1)
