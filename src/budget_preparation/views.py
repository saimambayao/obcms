"""
Budget Preparation Views

Web interface for budget proposal creation and management.
Implements Parliament Bill No. 325 budget preparation workflows.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator
from django.utils import timezone
from decimal import Decimal

from .models import BudgetProposal, ProgramBudget, BudgetLineItem, BudgetJustification
from .services.budget_builder import BudgetBuilderService
from .forms import (
    BudgetProposalForm,
    ProgramBudgetForm,
    BudgetLineItemFormSet,
    BudgetJustificationForm
)
from planning.models import WorkPlanObjective, AnnualWorkPlan
from coordination.models import Organization


@login_required
def budget_dashboard(request):
    """
    Budget preparation dashboard with overview statistics and recent proposals.
    """
    # Get user's organization (OOBC for now, will be user.organization in BMMS)
    organization = Organization.objects.filter(name__icontains='OOBC').first()

    # Statistics
    total_proposals = BudgetProposal.objects.filter(organization=organization).count()
    draft_proposals = BudgetProposal.objects.filter(
        organization=organization, status='draft'
    ).count()
    submitted_proposals = BudgetProposal.objects.filter(
        organization=organization, status='submitted'
    ).count()
    approved_proposals = BudgetProposal.objects.filter(
        organization=organization, status='approved'
    ).count()

    # Current fiscal year
    current_year = timezone.now().year

    # Recent proposals
    recent_proposals = BudgetProposal.objects.filter(
        organization=organization
    ).select_related('submitted_by', 'reviewed_by').order_by('-updated_at')[:5]

    # Total budget by fiscal year
    budget_by_year = BudgetProposal.objects.filter(
        organization=organization,
        status='approved'
    ).values('fiscal_year').annotate(
        total=Sum('total_proposed_budget')
    ).order_by('-fiscal_year')[:5]

    context = {
        'total_proposals': total_proposals,
        'draft_proposals': draft_proposals,
        'submitted_proposals': submitted_proposals,
        'approved_proposals': approved_proposals,
        'current_year': current_year,
        'recent_proposals': recent_proposals,
        'budget_by_year': budget_by_year,
    }

    return render(request, 'budget_preparation/dashboard.html', context)


@login_required
def proposal_list(request):
    """
    List all budget proposals with filtering and search.
    """
    # Get user's organization
    organization = Organization.objects.filter(name__icontains='OOBC').first()

    # Base queryset
    proposals = BudgetProposal.objects.filter(
        organization=organization
    ).select_related('submitted_by', 'reviewed_by').prefetch_related('program_budgets')

    # Filters
    status_filter = request.GET.get('status', '')
    year_filter = request.GET.get('year', '')
    search_query = request.GET.get('q', '')

    if status_filter:
        proposals = proposals.filter(status=status_filter)

    if year_filter:
        proposals = proposals.filter(fiscal_year=year_filter)

    if search_query:
        proposals = proposals.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Order by
    proposals = proposals.order_by('-fiscal_year', '-updated_at')

    # Pagination
    paginator = Paginator(proposals, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Available years for filter
    available_years = BudgetProposal.objects.filter(
        organization=organization
    ).values_list('fiscal_year', flat=True).distinct().order_by('-fiscal_year')

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'year_filter': year_filter,
        'search_query': search_query,
        'available_years': available_years,
        'status_choices': BudgetProposal.STATUS_CHOICES,
    }

    return render(request, 'budget_preparation/proposal_list.html', context)


@login_required
def proposal_detail(request, pk):
    """
    View detailed budget proposal with program budgets and line items.
    """
    organization = Organization.objects.filter(name__icontains='OOBC').first()

    proposal = get_object_or_404(
        BudgetProposal.objects.select_related('submitted_by', 'reviewed_by'),
        pk=pk,
        organization=organization
    )

    # Get program budgets with related data
    program_budgets = proposal.program_budgets.select_related(
        'program__annual_work_plan',
        'program__strategic_goal'
    ).prefetch_related('line_items').all()

    # Calculate statistics
    total_programs = program_budgets.count()
    total_line_items = BudgetLineItem.objects.filter(
        program_budget__budget_proposal=proposal
    ).count()

    # Category breakdown
    category_breakdown = BudgetLineItem.objects.filter(
        program_budget__budget_proposal=proposal
    ).values('category').annotate(
        total=Sum('total_cost')
    ).order_by('category')

    # Priority breakdown
    priority_breakdown = program_budgets.values('priority_level').annotate(
        count=Count('id'),
        total=Sum('allocated_amount')
    ).order_by('priority_level')

    context = {
        'proposal': proposal,
        'program_budgets': program_budgets,
        'total_programs': total_programs,
        'total_line_items': total_line_items,
        'category_breakdown': category_breakdown,
        'priority_breakdown': priority_breakdown,
    }

    return render(request, 'budget_preparation/proposal_detail.html', context)


@login_required
def proposal_create(request):
    """
    Create new budget proposal.
    """
    organization = Organization.objects.filter(name__icontains='OOBC').first()

    if request.method == 'POST':
        form = BudgetProposalForm(request.POST, organization=organization)

        if form.is_valid():
            try:
                service = BudgetBuilderService()
                proposal = service.create_proposal(
                    organization=organization,
                    fiscal_year=form.cleaned_data['fiscal_year'],
                    title=form.cleaned_data['title'],
                    description=form.cleaned_data['description'],
                    user=request.user
                )

                messages.success(
                    request,
                    f"Budget proposal for FY {proposal.fiscal_year} created successfully!"
                )
                return redirect('budget_preparation:proposal_edit', pk=proposal.pk)

            except Exception as e:
                messages.error(request, f"Error creating proposal: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BudgetProposalForm(organization=organization)

    context = {
        'form': form,
        'current_year': timezone.now().year,
    }

    return render(request, 'budget_preparation/proposal_form.html', context)


@login_required
def proposal_edit(request, pk):
    """
    Edit existing budget proposal (only if editable).
    """
    organization = Organization.objects.filter(name__icontains='OOBC').first()

    proposal = get_object_or_404(
        BudgetProposal,
        pk=pk,
        organization=organization
    )

    # Check if proposal is editable
    if not proposal.is_editable:
        messages.warning(
            request,
            "This proposal cannot be edited in its current status."
        )
        return redirect('budget_preparation:proposal_detail', pk=proposal.pk)

    if request.method == 'POST':
        form = BudgetProposalForm(
            request.POST,
            instance=proposal,
            organization=organization
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Budget proposal updated successfully!")
            return redirect('budget_preparation:proposal_detail', pk=proposal.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BudgetProposalForm(instance=proposal, organization=organization)

    # Get program budgets
    program_budgets = proposal.program_budgets.select_related(
        'program__annual_work_plan'
    ).prefetch_related('line_items').all()

    # Get available work plan objectives
    available_objectives = WorkPlanObjective.objects.filter(
        annual_work_plan__year=proposal.fiscal_year,
        status__in=['not_started', 'in_progress']
    ).select_related('annual_work_plan', 'strategic_goal')

    context = {
        'form': form,
        'proposal': proposal,
        'program_budgets': program_budgets,
        'available_objectives': available_objectives,
        'current_year': timezone.now().year,
    }

    return render(request, 'budget_preparation/proposal_form.html', context)


@login_required
def proposal_delete(request, pk):
    """
    Soft delete budget proposal (only if in draft status).
    """
    organization = Organization.objects.filter(name__icontains='OOBC').first()

    proposal = get_object_or_404(
        BudgetProposal,
        pk=pk,
        organization=organization
    )

    if proposal.status != 'draft':
        messages.error(
            request,
            "Only draft proposals can be deleted."
        )
        return redirect('budget_preparation:proposal_detail', pk=proposal.pk)

    if request.method == 'POST':
        fiscal_year = proposal.fiscal_year
        proposal.delete()
        messages.success(
            request,
            f"Budget proposal for FY {fiscal_year} has been deleted."
        )
        return redirect('budget_preparation:proposal_list')

    context = {
        'proposal': proposal,
    }

    return render(request, 'budget_preparation/proposal_confirm_delete.html', context)


@login_required
def proposal_submit(request, pk):
    """
    Submit budget proposal for review.
    """
    organization = Organization.objects.filter(name__icontains='OOBC').first()

    proposal = get_object_or_404(
        BudgetProposal,
        pk=pk,
        organization=organization
    )

    if request.method == 'POST':
        try:
            service = BudgetBuilderService()
            service.submit_proposal(proposal, request.user)

            messages.success(
                request,
                f"Budget proposal for FY {proposal.fiscal_year} submitted for review!"
            )
            return redirect('budget_preparation:proposal_detail', pk=proposal.pk)

        except Exception as e:
            messages.error(request, f"Error submitting proposal: {str(e)}")
            return redirect('budget_preparation:proposal_edit', pk=proposal.pk)

    # Show validation errors if any
    service = BudgetBuilderService()
    validation_errors = service.validate_proposal(proposal)

    context = {
        'proposal': proposal,
        'validation_errors': validation_errors,
    }

    return render(request, 'budget_preparation/proposal_submit_confirm.html', context)


@login_required
@permission_required('budget_preparation.can_approve_proposals', raise_exception=True)
def proposal_approve(request, pk):
    """
    Approve budget proposal (requires permission).
    """
    organization = Organization.objects.filter(name__icontains='OOBC').first()

    proposal = get_object_or_404(
        BudgetProposal,
        pk=pk,
        organization=organization
    )

    if proposal.status != 'under_review':
        messages.error(
            request,
            "Only proposals under review can be approved."
        )
        return redirect('budget_preparation:proposal_detail', pk=proposal.pk)

    if request.method == 'POST':
        approval_notes = request.POST.get('approval_notes', '')

        try:
            proposal.approve(request.user, approval_notes)
            messages.success(
                request,
                f"Budget proposal for FY {proposal.fiscal_year} approved!"
            )
        except Exception as e:
            messages.error(request, f"Error approving proposal: {str(e)}")

        return redirect('budget_preparation:proposal_detail', pk=proposal.pk)

    context = {
        'proposal': proposal,
    }

    return render(request, 'budget_preparation/proposal_approve.html', context)


@login_required
@permission_required('budget_preparation.can_approve_proposals', raise_exception=True)
def proposal_reject(request, pk):
    """
    Reject budget proposal with reason (requires permission).
    """
    organization = Organization.objects.filter(name__icontains='OOBC').first()

    proposal = get_object_or_404(
        BudgetProposal,
        pk=pk,
        organization=organization
    )

    if proposal.status != 'under_review':
        messages.error(
            request,
            "Only proposals under review can be rejected."
        )
        return redirect('budget_preparation:proposal_detail', pk=proposal.pk)

    if request.method == 'POST':
        rejection_notes = request.POST.get('rejection_notes', '')

        if not rejection_notes:
            messages.error(request, "Rejection reason is required.")
            return redirect('budget_preparation:proposal_reject', pk=proposal.pk)

        try:
            proposal.reject(request.user, rejection_notes)
            messages.success(
                request,
                f"Budget proposal for FY {proposal.fiscal_year} rejected."
            )
        except Exception as e:
            messages.error(request, f"Error rejecting proposal: {str(e)}")

        return redirect('budget_preparation:proposal_detail', pk=proposal.pk)

    context = {
        'proposal': proposal,
    }

    return render(request, 'budget_preparation/proposal_reject.html', context)


# ==================== Program Budget Views ====================

@login_required
def program_create(request, proposal_pk):
    """
    Add program budget to proposal (HTMX view).
    """
    organization = Organization.objects.filter(name__icontains='OOBC').first()

    proposal = get_object_or_404(
        BudgetProposal,
        pk=proposal_pk,
        organization=organization
    )

    if not proposal.is_editable:
        return JsonResponse({
            'error': 'Proposal is not editable'
        }, status=400)

    if request.method == 'POST':
        form = ProgramBudgetForm(request.POST, proposal=proposal)

        if form.is_valid():
            try:
                service = BudgetBuilderService()
                program_budget = service.add_program_budget(
                    proposal=proposal,
                    program=form.cleaned_data['program'],
                    allocated_amount=form.cleaned_data['allocated_amount'],
                    priority=form.cleaned_data['priority_level'],
                    justification=form.cleaned_data['justification'],
                    expected_outputs=form.cleaned_data['expected_outputs']
                )

                if request.headers.get('HX-Request'):
                    # Return HTMX partial
                    return render(
                        request,
                        'budget_preparation/partials/program_budget_item.html',
                        {'program_budget': program_budget}
                    )
                else:
                    messages.success(request, "Program budget added successfully!")
                    return redirect('budget_preparation:proposal_edit', pk=proposal.pk)

            except Exception as e:
                if request.headers.get('HX-Request'):
                    return JsonResponse({'error': str(e)}, status=400)
                else:
                    messages.error(request, f"Error adding program: {str(e)}")
        else:
            if request.headers.get('HX-Request'):
                return render(
                    request,
                    'budget_preparation/partials/program_form.html',
                    {'form': form, 'proposal': proposal}
                )
    else:
        form = ProgramBudgetForm(proposal=proposal)

    context = {
        'form': form,
        'proposal': proposal,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'budget_preparation/partials/program_form.html', context)
    else:
        return render(request, 'budget_preparation/program_form.html', context)


@login_required
def program_edit(request, pk):
    """
    Edit program budget (HTMX view).
    """
    organization = Organization.objects.filter(name__icontains='OOBC').first()

    program_budget = get_object_or_404(
        ProgramBudget.objects.select_related('budget_proposal'),
        pk=pk,
        budget_proposal__organization=organization
    )

    proposal = program_budget.budget_proposal

    if not proposal.is_editable:
        return JsonResponse({
            'error': 'Proposal is not editable'
        }, status=400)

    if request.method == 'POST':
        form = ProgramBudgetForm(request.POST, instance=program_budget, proposal=proposal)

        if form.is_valid():
            form.save()

            # Update proposal total
            service = BudgetBuilderService()
            service._update_proposal_total(proposal)

            if request.headers.get('HX-Request'):
                return render(
                    request,
                    'budget_preparation/partials/program_budget_item.html',
                    {'program_budget': program_budget}
                )
            else:
                messages.success(request, "Program budget updated successfully!")
                return redirect('budget_preparation:proposal_edit', pk=proposal.pk)
        else:
            if request.headers.get('HX-Request'):
                return render(
                    request,
                    'budget_preparation/partials/program_form.html',
                    {'form': form, 'proposal': proposal, 'program_budget': program_budget}
                )
    else:
        form = ProgramBudgetForm(instance=program_budget, proposal=proposal)

    context = {
        'form': form,
        'proposal': proposal,
        'program_budget': program_budget,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'budget_preparation/partials/program_form.html', context)
    else:
        return render(request, 'budget_preparation/program_form.html', context)


@login_required
def program_delete(request, pk):
    """
    Delete program budget.
    """
    organization = Organization.objects.filter(name__icontains='OOBC').first()

    program_budget = get_object_or_404(
        ProgramBudget.objects.select_related('budget_proposal'),
        pk=pk,
        budget_proposal__organization=organization
    )

    proposal = program_budget.budget_proposal

    if not proposal.is_editable:
        messages.error(request, "Cannot delete program from non-editable proposal.")
        return redirect('budget_preparation:proposal_edit', pk=proposal.pk)

    if request.method == 'POST':
        program_budget.delete()

        # Update proposal total
        service = BudgetBuilderService()
        service._update_proposal_total(proposal)

        messages.success(request, "Program budget removed successfully!")
        return redirect('budget_preparation:proposal_edit', pk=proposal.pk)

    context = {
        'program_budget': program_budget,
        'proposal': proposal,
    }

    return render(request, 'budget_preparation/program_confirm_delete.html', context)


# ==================== HTMX API Endpoints ====================

@login_required
def proposal_stats(request):
    """
    Return proposal statistics as JSON for dashboard updates.
    """
    organization = Organization.objects.filter(name__icontains='OOBC').first()

    stats = {
        'total_proposals': BudgetProposal.objects.filter(organization=organization).count(),
        'draft_proposals': BudgetProposal.objects.filter(
            organization=organization, status='draft'
        ).count(),
        'submitted_proposals': BudgetProposal.objects.filter(
            organization=organization, status='submitted'
        ).count(),
        'approved_proposals': BudgetProposal.objects.filter(
            organization=organization, status='approved'
        ).count(),
    }

    return JsonResponse(stats)


@login_required
def recent_proposals_partial(request):
    """
    HTMX partial for recent proposals list.
    """
    organization = Organization.objects.filter(name__icontains='OOBC').first()

    recent_proposals = BudgetProposal.objects.filter(
        organization=organization
    ).select_related('submitted_by').order_by('-updated_at')[:5]

    return render(
        request,
        'budget_preparation/partials/recent_proposals.html',
        {'recent_proposals': recent_proposals}
    )
