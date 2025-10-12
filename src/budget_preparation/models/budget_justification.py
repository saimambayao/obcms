"""
Budget Justification Model

Evidence-based budget justification linking to needs assessments and M&E data.
"""

from django.db import models


class BudgetJustification(models.Model):
    """
    Supporting evidence and rationale for program budget allocations.

    Integration Points:
    - Needs Assessment: Links to MANA module for evidence-based budgeting
    - Monitoring Entry: Links to M&E PPAs (CRITICAL: NOT Program FK)
    
    CRITICAL FIX: Uses MonitoringEntry FK (not Program FK) for M&E integration.
    This ensures budget justifications can reference actual PPAs being implemented.
    """

    program_budget = models.ForeignKey(
        'ProgramBudget',
        on_delete=models.CASCADE,
        related_name='justifications',
        help_text="Program budget being justified"
    )

    # Integration with MANA (Needs Assessment)
    needs_assessment_reference = models.ForeignKey(
        'mana.Assessment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='budget_justifications',
        help_text="Needs assessment supporting this budget request"
    )

    # Integration with M&E (Monitoring Entry - CRITICAL FIX)
    monitoring_entry_reference = models.ForeignKey(
        'monitoring.MonitoringEntry',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='budget_justifications',
        help_text="M&E PPA entry supporting this budget allocation"
    )

    rationale = models.TextField(
        blank=True,
        default='',
        help_text="Detailed rationale for budget allocation"
    )

    alignment_with_priorities = models.TextField(
        blank=True,
        default='',
        help_text="How this budget aligns with organizational priorities"
    )

    expected_impact = models.TextField(
        blank=True,
        default='',
        help_text="Expected impact and outcomes from this budget allocation"
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Budget Justification"
        verbose_name_plural = "Budget Justifications"

    def __str__(self):
        return f"Justification for {self.program_budget}"

    @property
    def has_evidence(self):
        """Check if justification has supporting evidence from MANA or M&E."""
        return bool(self.needs_assessment_reference or self.monitoring_entry_reference)
