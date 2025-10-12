"""
Budget Execution Signals for Audit Logging
Compliance: Parliament Bill No. 325 Section 78

Audit logging is handled by:
1. AuditMiddleware (common.middleware.AuditMiddleware) - Captures all budget changes
2. Django-auditlog - Built-in audit trail
3. These signals - Additional context-specific logging

All financial operations (allotments, obligations, disbursements) are automatically
logged by the middleware. These signals provide additional event hooks if needed.
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from decimal import Decimal
import logging

from .models import Allotment, Obligation, Disbursement, DisbursementLineItem

logger = logging.getLogger(__name__)


# ============================================================================
# ALLOTMENT SIGNALS
# ============================================================================

@receiver(pre_save, sender=Allotment)
def allotment_pre_save(sender, instance, **kwargs):
    """Track allotment changes before save for audit context."""
    if instance.pk:
        # Updating existing allotment
        try:
            old_instance = Allotment.objects.get(pk=instance.pk)
            instance._old_amount = old_instance.amount
            instance._old_status = old_instance.status
        except Allotment.DoesNotExist:
            pass


@receiver(post_save, sender=Allotment)
def allotment_post_save(sender, instance, created, **kwargs):
    """Log allotment creation/updates."""
    if created:
        logger.info(
            f"Allotment created: {instance.id} | "
            f"Program: {instance.program_budget} | "
            f"Quarter: Q{instance.quarter} | "
            f"Amount: ±{instance.amount:,.2f} | "
            f"Created by: {instance.created_by}"
        )
    else:
        # Check for amount changes
        old_amount = getattr(instance, '_old_amount', None)
        old_status = getattr(instance, '_old_status', None)

        if old_amount and old_amount != instance.amount:
            logger.warning(
                f"Allotment amount changed: {instance.id} | "
                f"From: ±{old_amount:,.2f}  To: ±{instance.amount:,.2f} | "
                f"Difference: ±{instance.amount - old_amount:,.2f}"
            )

        if old_status and old_status != instance.status:
            logger.info(
                f"Allotment status changed: {instance.id} | "
                f"From: {old_status}  To: {instance.status}"
            )


@receiver(post_delete, sender=Allotment)
def allotment_deleted(sender, instance, **kwargs):
    """Log allotment deletion (should be rare - cancelled instead)."""
    logger.warning(
        f"Allotment deleted: {instance.id} | "
        f"Program: {instance.program_budget} | "
        f"Amount: ±{instance.amount:,.2f}"
    )


# ============================================================================
# OBLIGATION SIGNALS
# ============================================================================

@receiver(pre_save, sender=Obligation)
def obligation_pre_save(sender, instance, **kwargs):
    """Track obligation changes before save."""
    if instance.pk:
        try:
            old_instance = Obligation.objects.get(pk=instance.pk)
            instance._old_amount = old_instance.amount
            instance._old_status = old_instance.status
        except Obligation.DoesNotExist:
            pass


@receiver(post_save, sender=Obligation)
def obligation_post_save(sender, instance, created, **kwargs):
    """Log obligation creation/updates."""
    if created:
        logger.info(
            f"Obligation created: {instance.id} | "
            f"Allotment: {instance.allotment.id} | "
            f"Description: {instance.description} | "
            f"Amount: ±{instance.amount:,.2f} | "
            f"Created by: {instance.created_by}"
        )
    else:
        old_amount = getattr(instance, '_old_amount', None)
        old_status = getattr(instance, '_old_status', None)

        if old_amount and old_amount != instance.amount:
            logger.warning(
                f"Obligation amount changed: {instance.id} | "
                f"From: ±{old_amount:,.2f}  To: ±{instance.amount:,.2f} | "
                f"Difference: ±{instance.amount - old_amount:,.2f}"
            )

        if old_status and old_status != instance.status:
            logger.info(
                f"Obligation status changed: {instance.id} | "
                f"From: {old_status}  To: {instance.status}"
            )


@receiver(post_delete, sender=Obligation)
def obligation_deleted(sender, instance, **kwargs):
    """Log obligation deletion."""
    logger.warning(
        f"Obligation deleted: {instance.id} | "
        f"Description: {instance.description} | "
        f"Amount: ±{instance.amount:,.2f}"
    )


# ============================================================================
# DISBURSEMENT SIGNALS
# ============================================================================

@receiver(pre_save, sender=Disbursement)
def disbursement_pre_save(sender, instance, **kwargs):
    """Track disbursement changes before save."""
    if instance.pk:
        try:
            old_instance = Disbursement.objects.get(pk=instance.pk)
            instance._old_amount = old_instance.amount
        except Disbursement.DoesNotExist:
            pass


@receiver(post_save, sender=Disbursement)
def disbursement_post_save(sender, instance, created, **kwargs):
    """Log disbursement creation/updates."""
    if created:
        logger.info(
            f"Disbursement created: {instance.id} | "
            f"Obligation: {instance.obligation.id} | "
            f"Payee: {instance.payee} | "
            f"Amount: ±{instance.amount:,.2f} | "
            f"Payment Method: {instance.payment_method} | "
            f"Created by: {instance.created_by}"
        )
    else:
        old_amount = getattr(instance, '_old_amount', None)

        if old_amount and old_amount != instance.amount:
            logger.warning(
                f"Disbursement amount changed: {instance.id} | "
                f"From: ±{old_amount:,.2f}  To: ±{instance.amount:,.2f} | "
                f"Difference: ±{instance.amount - old_amount:,.2f}"
            )


@receiver(post_delete, sender=Disbursement)
def disbursement_deleted(sender, instance, **kwargs):
    """Log disbursement deletion."""
    logger.warning(
        f"Disbursement deleted: {instance.id} | "
        f"Payee: {instance.payee} | "
        f"Amount: ±{instance.amount:,.2f}"
    )


# ============================================================================
# DISBURSEMENT LINE ITEM SIGNALS
# ============================================================================

@receiver(post_save, sender=DisbursementLineItem)
def line_item_post_save(sender, instance, created, **kwargs):
    """Log line item creation."""
    if created:
        logger.info(
            f"Disbursement Line Item created: {instance.id} | "
            f"Disbursement: {instance.disbursement.id} | "
            f"Description: {instance.description} | "
            f"Amount: ±{instance.amount:,.2f}"
        )


@receiver(post_delete, sender=DisbursementLineItem)
def line_item_deleted(sender, instance, **kwargs):
    """Log line item deletion."""
    logger.info(
        f"Disbursement Line Item deleted: {instance.id} | "
        f"Description: {instance.description} | "
        f"Amount: ±{instance.amount:,.2f}"
    )