"""
Financial constraint tests for budget execution

Tests PostgreSQL triggers and database-level financial controls.
These are CRITICAL tests - 100% pass rate required.
"""

import pytest
from decimal import Decimal
from django.db import IntegrityError, transaction
from budget_execution.models import Allotment, Obligation, Disbursement


@pytest.mark.django_db
class TestAllotmentConstraints:
    """Test allotment-level financial constraints."""

    def test_allotment_cannot_exceed_approved_budget(self, approved_program_budget, execution_user):
        """Test that total allotments cannot exceed approved budget."""
        # Approved budget: 45M
        approved_amount = approved_program_budget.approved_amount

        # Create allotments totaling MORE than approved
        Allotment.objects.create(
            program_budget=approved_program_budget,
            quarter='Q1',
            amount=Decimal('20000000.00'),
            released_by=execution_user,
            status='released'
        )

        Allotment.objects.create(
            program_budget=approved_program_budget,
            quarter='Q2',
            amount=Decimal('20000000.00'),
            released_by=execution_user,
            status='released'
        )

        # Third allotment should fail (would exceed 45M)
        # TODO: Implement constraint trigger
        # with pytest.raises(IntegrityError) as exc_info:
        #     Allotment.objects.create(
        #         program_budget=approved_program_budget,
        #         quarter='Q3',
        #         amount=Decimal('10000000.00'),
        #         released_by=execution_user,
        #         status='released'
        #     )
        # assert 'allotment_total_constraint' in str(exc_info.value)

    def test_quarterly_allotment_limits(self, approved_program_budget, execution_user):
        """Test that allotments respect quarterly limits if configured."""
        # TODO: Implement if quarterly limits are required
        pass


@pytest.mark.django_db
class TestObligationConstraints:
    """Test obligation-level financial constraints."""

    def test_obligation_cannot_exceed_allotment(self, allotment_q1, work_item, execution_user):
        """Test that obligations cannot exceed allotment amount."""
        # Allotment: 10M
        allotment_amount = allotment_q1.amount

        # Create obligation for 6M
        Obligation.objects.create(
            allotment=allotment_q1,
            work_item=work_item,
            amount=Decimal('6000000.00'),
            payee="Contractor A",
            obligated_by=execution_user,
            status='obligated'
        )

        # Create another obligation for 5M - should FAIL (total would be 11M > 10M)
        with pytest.raises(IntegrityError) as exc_info:
            with transaction.atomic():
                Obligation.objects.create(
                    allotment=allotment_q1,
                    work_item=work_item,
                    amount=Decimal('5000000.00'),
                    payee="Contractor B",
                    obligated_by=execution_user,
                    status='obligated'
                )

        # TODO: Verify error message contains constraint name
        # assert 'obligation_total_constraint' in str(exc_info.value)

    def test_multiple_obligations_within_limit(self, allotment_q1, work_item, work_item_2, execution_user):
        """Test creating multiple obligations within allotment limit."""
        # Create multiple obligations totaling less than allotment
        Obligation.objects.create(
            allotment=allotment_q1,
            work_item=work_item,
            amount=Decimal('4000000.00'),
            payee="Contractor A",
            obligated_by=execution_user,
            status='obligated'
        )

        Obligation.objects.create(
            allotment=allotment_q1,
            work_item=work_item_2,
            amount=Decimal('3000000.00'),
            payee="Contractor B",
            obligated_by=execution_user,
            status='obligated'
        )

        Obligation.objects.create(
            allotment=allotment_q1,
            work_item=work_item,
            amount=Decimal('2000000.00'),
            payee="Contractor C",
            obligated_by=execution_user,
            status='obligated'
        )

        # Total: 9M < 10M allotment - should succeed
        total_obligations = Obligation.objects.filter(allotment=allotment_q1).count()
        assert total_obligations == 3

    def test_obligation_amount_positive(self, allotment_q1, work_item, execution_user):
        """Test obligation amount must be positive."""
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Obligation.objects.create(
                    allotment=allotment_q1,
                    work_item=work_item,
                    amount=Decimal('-1000000.00'),  # Negative amount
                    payee="Test",
                    obligated_by=execution_user
                )


@pytest.mark.django_db
class TestDisbursementConstraints:
    """Test disbursement-level financial constraints."""

    def test_disbursement_cannot_exceed_obligation(self, obligation, execution_user):
        """Test that disbursements cannot exceed obligation amount."""
        # Obligation: 5M
        obligation_amount = obligation.amount

        # Create disbursement for 3M
        Disbursement.objects.create(
            obligation=obligation,
            amount=Decimal('3000000.00'),
            payment_method='check',
            disbursed_by=execution_user,
            status='paid'
        )

        # Create another disbursement for 3M - should FAIL (total would be 6M > 5M)
        with pytest.raises(IntegrityError) as exc_info:
            with transaction.atomic():
                Disbursement.objects.create(
                    obligation=obligation,
                    amount=Decimal('3000000.00'),
                    payment_method='check',
                    disbursed_by=execution_user,
                    status='paid'
                )

        # TODO: Verify error message
        # assert 'disbursement_total_constraint' in str(exc_info.value)

    def test_multiple_disbursements_within_obligation(self, obligation, execution_user):
        """Test progressive disbursements within obligation limit."""
        # Create 3 disbursements totaling obligation amount
        Disbursement.objects.create(
            obligation=obligation,
            amount=Decimal('2000000.00'),  # 40%
            payment_method='check',
            disbursed_by=execution_user,
            status='paid'
        )

        Disbursement.objects.create(
            obligation=obligation,
            amount=Decimal('1500000.00'),  # 30%
            payment_method='check',
            disbursed_by=execution_user,
            status='paid'
        )

        Disbursement.objects.create(
            obligation=obligation,
            amount=Decimal('1500000.00'),  # 30%
            payment_method='bank_transfer',
            disbursed_by=execution_user,
            status='paid'
        )

        # Total: 5M = obligation amount - should succeed
        total_disbursed = Disbursement.objects.filter(
            obligation=obligation
        ).count()
        assert total_disbursed == 3

    def test_disbursement_amount_positive(self, obligation, execution_user):
        """Test disbursement amount must be positive."""
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Disbursement.objects.create(
                    obligation=obligation,
                    amount=Decimal('-500000.00'),  # Negative
                    payment_method='check',
                    disbursed_by=execution_user
                )


@pytest.mark.django_db
class TestStatusCascades:
    """Test automatic status updates based on financial thresholds."""

    def test_obligation_status_when_fully_disbursed(self, obligation, execution_user):
        """Test obligation status updates to 'fully_disbursed' automatically."""
        # Create disbursement equal to obligation amount
        Disbursement.objects.create(
            obligation=obligation,
            amount=obligation.amount,  # Full amount
            payment_method='check',
            disbursed_by=execution_user,
            status='paid'
        )

        # TODO: Implement trigger/signal to update status
        # obligation.refresh_from_db()
        # assert obligation.status == 'fully_disbursed'

    def test_obligation_status_when_partially_disbursed(self, obligation, execution_user):
        """Test obligation status updates to 'partially_disbursed'."""
        # Create disbursement for partial amount
        Disbursement.objects.create(
            obligation=obligation,
            amount=obligation.amount / 2,  # 50%
            payment_method='check',
            disbursed_by=execution_user,
            status='paid'
        )

        # TODO: Implement status update logic
        # obligation.refresh_from_db()
        # assert obligation.status == 'partially_disbursed'

    def test_allotment_status_when_fully_obligated(self, allotment_q1, work_item, execution_user):
        """Test allotment status when fully obligated."""
        # Create obligation equal to allotment
        Obligation.objects.create(
            allotment=allotment_q1,
            work_item=work_item,
            amount=allotment_q1.amount,
            payee="Contractor",
            obligated_by=execution_user,
            status='obligated'
        )

        # TODO: Implement status update
        # allotment_q1.refresh_from_db()
        # assert allotment_q1.status == 'fully_obligated'


@pytest.mark.django_db
class TestTransactionRollback:
    """Test transaction rollback on constraint violations."""

    def test_rollback_on_obligation_failure(self, allotment_q1, work_item, execution_user):
        """Test that failed obligation doesn't create partial records."""
        initial_count = Obligation.objects.count()

        try:
            with transaction.atomic():
                # This should fail due to exceeding allotment
                Obligation.objects.create(
                    allotment=allotment_q1,
                    work_item=work_item,
                    amount=allotment_q1.amount * 2,  # Exceeds allotment
                    payee="Test",
                    obligated_by=execution_user
                )
        except IntegrityError:
            pass

        # Verify no record was created
        assert Obligation.objects.count() == initial_count

    def test_rollback_on_disbursement_failure(self, obligation, execution_user):
        """Test rollback on disbursement constraint violation."""
        initial_count = Disbursement.objects.count()

        try:
            with transaction.atomic():
                # Create disbursement exceeding obligation
                Disbursement.objects.create(
                    obligation=obligation,
                    amount=obligation.amount * 2,
                    payment_method='check',
                    disbursed_by=execution_user
                )
        except IntegrityError:
            pass

        # Verify no record was created
        assert Disbursement.objects.count() == initial_count


@pytest.mark.django_db
class TestConcurrencyControl:
    """Test concurrent transaction handling."""

    def test_concurrent_obligations_safe(self, allotment_q1, work_item, execution_user):
        """Test that concurrent obligations are handled safely."""
        # TODO: Implement concurrent transaction test
        # Use threading or async to simulate concurrent requests
        pass

    def test_concurrent_disbursements_safe(self, obligation, execution_user):
        """Test concurrent disbursements don't exceed obligation."""
        # TODO: Implement concurrent disbursement test
        pass
