"""
Budget Execution Views
Phase 2B: Budget Execution (Parliament Bill No. 325 Section 78)

Web interface for budget execution: Allotments, Obligations, Disbursements
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q, Count, F
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
import json

from .models import Allotment, Obligation, Disbursement, DisbursementLineItem
from .services.allotment_release import AllotmentReleaseService
from budget_preparation.models import ProgramBudget
from monitoring.models import MonitoringEntry


# ============================================================================
# DASHBOARD
# ============================================================================


@login_required
def budget_dashboard(request):
    """
    Main budget execution dashboard with financial summaries and charts.
    """
    # Get current fiscal year (default to 2025)
    fiscal_year = timezone.now().year

    # Calculate summary statistics
    approved_budget = ProgramBudget.objects.filter(
        budget_proposal__fiscal_year=fiscal_year,
        approved_amount__isnull=False
    ).aggregate(total=Sum('approved_amount'))['total'] or Decimal('0.00')

    allotted_amount = Allotment.objects.filter(
        program_budget__budget_proposal__fiscal_year=fiscal_year,
        status__in=['released', 'partially_utilized', 'fully_utilized']
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    obligated_amount = Obligation.objects.filter(
        allotment__program_budget__budget_proposal__fiscal_year=fiscal_year,
        status__in=['committed', 'partially_disbursed', 'fully_disbursed']
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    disbursed_amount = Disbursement.objects.filter(
        obligation__allotment__program_budget__budget_proposal__fiscal_year=fiscal_year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # Calculate percentages
    allotted_percentage = (allotted_amount / approved_budget * 100) if approved_budget > 0 else Decimal('0.00')
    obligated_percentage = (obligated_amount / allotted_amount * 100) if allotted_amount > 0 else Decimal('0.00')
    disbursed_percentage = (disbursed_amount / obligated_amount * 100) if obligated_amount > 0 else Decimal('0.00')

    # Get quarterly data for chart
    quarterly_allotted = []
    quarterly_obligated = []
    quarterly_disbursed = []

    for quarter in range(1, 5):
        q_allotted = Allotment.objects.filter(
            program_budget__budget_proposal__fiscal_year=fiscal_year,
            quarter=quarter,
            status__in=['released', 'partially_utilized', 'fully_utilized']
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        quarterly_allotted.append(float(q_allotted))

        q_obligated = Obligation.objects.filter(
            allotment__program_budget__budget_proposal__fiscal_year=fiscal_year,
            allotment__quarter=quarter,
            status__in=['committed', 'partially_disbursed', 'fully_disbursed']
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        quarterly_obligated.append(float(q_obligated))

        q_disbursed = Disbursement.objects.filter(
            obligation__allotment__program_budget__budget_proposal__fiscal_year=fiscal_year,
            obligation__allotment__quarter=quarter
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        quarterly_disbursed.append(float(q_disbursed))

    # Get program-wise utilization
    program_budgets = ProgramBudget.objects.filter(
        budget_proposal__fiscal_year=fiscal_year,
        approved_amount__isnull=False
    ).select_related('program', 'budget_proposal').annotate(
        allotted_amount=Sum('allotments__amount', filter=Q(
            allotments__status__in=['released', 'partially_utilized', 'fully_utilized']
        ))
    )

    # Add utilization percentage to each program
    for pb in program_budgets:
        pb.allotted_amount = pb.allotted_amount or Decimal('0.00')
        if pb.approved_amount > 0:
            pb.utilization_percentage = float((pb.allotted_amount / pb.approved_amount) * 100)
        else:
            pb.utilization_percentage = 0.0

    # Count pending approvals
    pending_approvals_count = Allotment.objects.filter(status='pending').count()
    alerts_count = Allotment.objects.filter(
        status__in=['released', 'partially_utilized']
    ).annotate(
        utilization=Sum('obligations__amount')
    ).filter(
        utilization__gte=F('amount') * Decimal('0.85')  # 85% threshold
    ).count()

    context = {
        'fiscal_year': fiscal_year,
        'approved_budget': float(approved_budget) / 1_000_000,  # Convert to millions
        'allotted_amount': float(allotted_amount) / 1_000_000,
        'obligated_amount': float(obligated_amount) / 1_000_000,
        'disbursed_amount': float(disbursed_amount) / 1_000_000,
        'allotted_percentage': float(allotted_percentage),
        'obligated_percentage': float(obligated_percentage),
        'disbursed_percentage': float(disbursed_percentage),
        'quarterly_allotted': json.dumps(quarterly_allotted),
        'quarterly_obligated': json.dumps(quarterly_obligated),
        'quarterly_disbursed': json.dumps(quarterly_disbursed),
        'program_budgets': program_budgets,
        'pending_approvals_count': pending_approvals_count,
        'alerts_count': alerts_count,
        'today': date.today(),
    }

    return render(request, 'budget_execution/budget_dashboard.html', context)


# ============================================================================
# ALLOTMENT VIEWS
# ============================================================================


@login_required
def allotment_list(request):
    """List all allotments with filtering."""
    allotments = Allotment.objects.select_related(
        'program_budget__program',
        'program_budget__budget_proposal',
        'created_by'
    ).order_by('-release_date', '-created_at')

    # Apply filters
    status = request.GET.get('status')
    quarter = request.GET.get('quarter')
    fiscal_year = request.GET.get('fiscal_year')

    if status:
        allotments = allotments.filter(status=status)
    if quarter:
        allotments = allotments.filter(quarter=quarter)
    if fiscal_year:
        allotments = allotments.filter(program_budget__budget_proposal__fiscal_year=fiscal_year)

    context = {
        'allotments': allotments,
        'status_choices': Allotment.STATUS_CHOICES,
        'quarter_choices': Allotment.QUARTER_CHOICES,
    }

    return render(request, 'budget_execution/allotment_list.html', context)


@login_required
def allotment_detail(request, pk):
    """View allotment details with obligations."""
    allotment = get_object_or_404(
        Allotment.objects.select_related(
            'program_budget__program',
            'program_budget__budget_proposal',
            'created_by'
        ).prefetch_related('obligations'),
        pk=pk
    )

    obligations = allotment.obligations.select_related('created_by').order_by('-obligated_date')

    context = {
        'allotment': allotment,
        'obligations': obligations,
        'remaining_balance': allotment.get_remaining_balance(),
        'utilization_rate': allotment.get_utilization_rate(),
    }

    return render(request, 'budget_execution/allotment_detail.html', context)


@login_required
def allotment_release(request):
    """Release quarterly allotment."""
    if request.method == 'POST':
        try:
            program_budget_id = request.POST.get('program_budget')
            quarter = int(request.POST.get('quarter'))
            amount = Decimal(request.POST.get('amount'))
            release_date_str = request.POST.get('release_date')
            status = request.POST.get('status', 'released')
            notes = request.POST.get('remarks', '')

            program_budget = get_object_or_404(ProgramBudget, pk=program_budget_id)
            release_date = date.fromisoformat(release_date_str) if release_date_str else date.today()

            # Use service layer
            service = AllotmentReleaseService()
            allotment = service.release_allotment(
                program_budget=program_budget,
                quarter=quarter,
                amount=amount,
                created_by=request.user,
                release_date=release_date,
                notes=notes
            )

            # Update status if not 'released'
            if status != 'released':
                allotment.status = status
                allotment.save()

            messages.success(
                request,
                f'Allotment released successfully: {allotment.get_quarter_display()} '
                f'for {program_budget.program.name} (₱{amount:,.2f})'
            )
            return redirect('budget_execution:allotment_detail', pk=allotment.pk)

        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error releasing allotment: {str(e)}')

    # GET request - show form
    program_budgets = ProgramBudget.objects.filter(
        approved_amount__isnull=False
    ).select_related('program', 'budget_proposal').order_by('-budget_proposal__fiscal_year')

    context = {
        'program_budgets': program_budgets,
        'today': date.today(),
    }

    return render(request, 'budget_execution/allotment_release.html', context)


@login_required
def allotment_approve(request, pk):
    """Approve pending allotment (finance director only)."""
    allotment = get_object_or_404(Allotment, pk=pk)

    if request.method == 'POST':
        try:
            service = AllotmentReleaseService()
            service.update_allotment_status(allotment, 'released')

            messages.success(request, f'Allotment approved: {allotment}')
            return redirect('budget_execution:allotment_detail', pk=allotment.pk)

        except Exception as e:
            messages.error(request, f'Error approving allotment: {str(e)}')

    return redirect('budget_execution:allotment_detail', pk=allotment.pk)


# ============================================================================
# OBLIGATION VIEWS
# ============================================================================


@login_required
def obligation_list(request):
    """List all obligations with filtering."""
    obligations = Obligation.objects.select_related(
        'allotment__program_budget__program',
        'created_by'
    ).order_by('-obligated_date')

    # Apply filters
    status = request.GET.get('status')
    if status:
        obligations = obligations.filter(status=status)

    context = {
        'obligations': obligations,
        'status_choices': Obligation.STATUS_CHOICES,
    }

    return render(request, 'budget_execution/obligation_list.html', context)


@login_required
def obligation_detail(request, pk):
    """View obligation details with disbursements."""
    obligation = get_object_or_404(
        Obligation.objects.select_related(
            'allotment__program_budget__program',
            'allotment__program_budget__budget_proposal',
            'created_by',
            'monitoring_entry'
        ).prefetch_related('disbursements'),
        pk=pk
    )

    disbursements = obligation.disbursements.select_related('created_by').order_by('-disbursed_date')

    context = {
        'obligation': obligation,
        'disbursements': disbursements,
        'remaining_balance': obligation.get_remaining_balance(),
    }

    return render(request, 'budget_execution/obligation_detail.html', context)


@login_required
def obligation_create(request):
    """Create new obligation."""
    if request.method == 'POST':
        try:
            allotment_id = request.POST.get('allotment')
            description = request.POST.get('description')
            amount = Decimal(request.POST.get('amount'))
            obligated_date_str = request.POST.get('obligated_date')
            document_ref = request.POST.get('document_reference', '')
            monitoring_entry_id = request.POST.get('activity')

            allotment = get_object_or_404(Allotment, pk=allotment_id)
            obligated_date = date.fromisoformat(obligated_date_str) if obligated_date_str else date.today()

            monitoring_entry = None
            if monitoring_entry_id:
                monitoring_entry = get_object_or_404(MonitoringEntry, pk=monitoring_entry_id)

            # Use service layer
            service = AllotmentReleaseService()
            obligation = service.create_obligation(
                allotment=allotment,
                description=description,
                amount=amount,
                obligated_date=obligated_date,
                created_by=request.user,
                document_ref=document_ref,
                monitoring_entry=monitoring_entry,
                notes=request.POST.get('remarks', '')
            )

            messages.success(
                request,
                f'Obligation recorded successfully: {description} (₱{amount:,.2f})'
            )
            return redirect('budget_execution:obligation_detail', pk=obligation.pk)

        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error recording obligation: {str(e)}')

    # GET request - show form
    allotments = Allotment.objects.filter(
        status__in=['released', 'partially_utilized']
    ).select_related(
        'program_budget__program',
        'program_budget__budget_proposal'
    ).order_by('-release_date')

    activities = MonitoringEntry.objects.filter(
        status__in=['planned', 'in_progress']
    ).order_by('-created_at')[:100]

    context = {
        'allotments': allotments,
        'activities': activities,
        'today': date.today(),
    }

    return render(request, 'budget_execution/obligation_form.html', context)


@login_required
def obligation_edit(request, pk):
    """Edit existing obligation."""
    obligation = get_object_or_404(Obligation, pk=pk)

    if request.method == 'POST':
        try:
            obligation.description = request.POST.get('description')
            obligation.amount = Decimal(request.POST.get('amount'))
            obligation.document_ref = request.POST.get('document_reference', '')
            obligation.notes = request.POST.get('remarks', '')

            obligated_date_str = request.POST.get('obligated_date')
            if obligated_date_str:
                obligation.obligated_date = date.fromisoformat(obligated_date_str)

            obligation.save()

            messages.success(request, 'Obligation updated successfully')
            return redirect('budget_execution:obligation_detail', pk=obligation.pk)

        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error updating obligation: {str(e)}')

    context = {
        'obligation': obligation,
        'edit_mode': True,
    }

    return render(request, 'budget_execution/obligation_form.html', context)


# ============================================================================
# DISBURSEMENT VIEWS
# ============================================================================


@login_required
def disbursement_list(request):
    """List all disbursements with filtering."""
    disbursements = Disbursement.objects.select_related(
        'obligation__allotment__program_budget__program',
        'created_by'
    ).order_by('-disbursed_date')

    # Apply filters
    payment_method = request.GET.get('payment_method')
    if payment_method:
        disbursements = disbursements.filter(payment_method=payment_method)

    context = {
        'disbursements': disbursements,
    }

    return render(request, 'budget_execution/disbursement_list.html', context)


@login_required
def disbursement_detail(request, pk):
    """View disbursement details with line items."""
    disbursement = get_object_or_404(
        Disbursement.objects.select_related(
            'obligation__allotment__program_budget__program',
            'obligation__allotment__program_budget__budget_proposal',
            'created_by'
        ).prefetch_related('line_items'),
        pk=pk
    )

    line_items = disbursement.line_items.select_related('monitoring_entry').all()

    context = {
        'disbursement': disbursement,
        'line_items': line_items,
    }

    return render(request, 'budget_execution/disbursement_detail.html', context)


@login_required
def disbursement_record(request):
    """Record new disbursement."""
    if request.method == 'POST':
        try:
            obligation_id = request.POST.get('obligation')
            amount = Decimal(request.POST.get('amount'))
            disbursed_date_str = request.POST.get('disbursed_date')
            payee = request.POST.get('payee')
            payment_method = request.POST.get('payment_method')
            check_number = request.POST.get('check_number', '')
            voucher_number = request.POST.get('voucher_number', '')

            obligation = get_object_or_404(Obligation, pk=obligation_id)
            disbursed_date = date.fromisoformat(disbursed_date_str) if disbursed_date_str else date.today()

            # Use service layer
            service = AllotmentReleaseService()
            disbursement = service.record_disbursement(
                obligation=obligation,
                amount=amount,
                disbursed_date=disbursed_date,
                payee=payee,
                payment_method=payment_method,
                created_by=request.user,
                check_number=check_number,
                voucher_number=voucher_number,
                notes=request.POST.get('remarks', '')
            )

            messages.success(
                request,
                f'Disbursement recorded successfully: {payee} (₱{amount:,.2f})'
            )
            return redirect('budget_execution:disbursement_detail', pk=disbursement.pk)

        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error recording disbursement: {str(e)}')

    # GET request - show form
    obligations = Obligation.objects.filter(
        status__in=['committed', 'partially_disbursed']
    ).select_related(
        'allotment__program_budget__program'
    ).order_by('-obligated_date')

    context = {
        'obligations': obligations,
        'today': date.today(),
    }

    return render(request, 'budget_execution/disbursement_form.html', context)


# ============================================================================
# HTMX PARTIALS & AJAX ENDPOINTS
# ============================================================================


@login_required
def recent_transactions(request):
    """HTMX partial: Recent transactions widget."""
    # Get recent allotments, obligations, and disbursements
    recent_allotments = Allotment.objects.filter(
        release_date__gte=timezone.now().date() - timedelta(days=30)
    ).select_related('program_budget__program')[:5]

    recent_obligations = Obligation.objects.filter(
        obligated_date__gte=timezone.now().date() - timedelta(days=30)
    ).select_related('allotment__program_budget__program')[:5]

    recent_disbursements = Disbursement.objects.filter(
        disbursed_date__gte=timezone.now().date() - timedelta(days=30)
    ).select_related('obligation__allotment__program_budget__program')[:5]

    # Combine and format transactions
    transactions = []

    for allotment in recent_allotments:
        transactions.append({
            'type': 'allotment',
            'description': f'Q{allotment.quarter} Allotment Released',
            'program_name': allotment.program_budget.program.name,
            'amount': allotment.amount,
            'date': allotment.release_date,
        })

    for obligation in recent_obligations:
        transactions.append({
            'type': 'obligation',
            'description': obligation.description,
            'program_name': obligation.allotment.program_budget.program.name,
            'amount': obligation.amount,
            'date': obligation.obligated_date,
        })

    for disbursement in recent_disbursements:
        transactions.append({
            'type': 'disbursement',
            'description': f'Payment to {disbursement.payee}',
            'program_name': disbursement.obligation.allotment.program_budget.program.name,
            'amount': disbursement.amount,
            'date': disbursement.disbursed_date,
        })

    # Sort by date (newest first)
    transactions.sort(key=lambda x: x['date'], reverse=True)
    transactions = transactions[:10]  # Limit to 10 most recent

    context = {
        'transactions': transactions,
    }

    return render(request, 'budget_execution/partials/recent_transactions.html', context)


@login_required
def pending_approvals(request):
    """HTMX partial: Pending approvals widget."""
    approvals = Allotment.objects.filter(
        status='pending'
    ).select_related(
        'program_budget__program',
        'created_by'
    ).order_by('-created_at')[:5]

    context = {
        'approvals': approvals,
    }

    return render(request, 'budget_execution/partials/pending_approvals.html', context)


@login_required
def budget_alerts(request):
    """HTMX partial: Budget alerts widget."""
    # Find allotments with high utilization (>85%)
    alerts = []

    high_utilization = Allotment.objects.filter(
        status__in=['released', 'partially_utilized']
    ).select_related('program_budget__program').annotate(
        utilization=Sum('obligations__amount')
    ).filter(
        utilization__gte=F('amount') * Decimal('0.85')
    )[:5]

    for allotment in high_utilization:
        utilization_pct = (allotment.utilization / allotment.amount * 100) if allotment.amount > 0 else 0
        alerts.append({
            'type': 'high_utilization',
            'severity': 'warning' if utilization_pct < 95 else 'critical',
            'message': f'{allotment.program_budget.program.name} Q{allotment.quarter} is {utilization_pct:.0f}% utilized',
            'allotment': allotment,
        })

    context = {
        'alerts': alerts,
    }

    return render(request, 'budget_execution/partials/budget_alerts.html', context)


@login_required
def get_budget_details(request):
    """AJAX: Get program budget details for allotment release form."""
    program_budget_id = request.GET.get('program_budget')
    if not program_budget_id:
        return JsonResponse({'error': 'No program budget ID provided'}, status=400)

    program_budget = get_object_or_404(
        ProgramBudget.objects.annotate(
            total_allotted=Sum('allotments__amount')
        ),
        pk=program_budget_id
    )

    total_allotted = program_budget.total_allotted or Decimal('0.00')
    remaining = program_budget.approved_amount - total_allotted

    data = {
        'approved_amount': float(program_budget.approved_amount),
        'total_allotted': float(total_allotted),
        'remaining': float(remaining),
        'program_name': program_budget.program.name,
        'fiscal_year': program_budget.budget_proposal.fiscal_year,
    }

    return JsonResponse(data)
