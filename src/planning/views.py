# src/planning/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.http import JsonResponse

from .models import StrategicPlan, StrategicGoal, AnnualWorkPlan, WorkPlanObjective
from .forms import StrategicPlanForm, StrategicGoalForm, AnnualWorkPlanForm, WorkPlanObjectiveForm


# ============================================================================
# STRATEGIC PLAN VIEWS
# ============================================================================

@login_required
def strategic_plan_list(request):
    """
    List all strategic plans with filtering and statistics
    """
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')

    # Base queryset
    plans = StrategicPlan.objects.all()

    # Apply filters
    if status_filter != 'all':
        plans = plans.filter(status=status_filter)

    # Annotate with goal counts and progress
    plans = plans.annotate(
        goal_count=Count('goals'),
        avg_goal_progress=Avg('goals__completion_percentage')
    )

    # Calculate statistics for stat cards
    stats = {
        'total_plans': StrategicPlan.objects.count(),
        'active_plans': StrategicPlan.objects.filter(status='active').count(),
        'completed_goals': StrategicGoal.objects.filter(status='completed').count(),
        'total_goals': StrategicGoal.objects.count(),
    }

    context = {
        'plans': plans,
        'status_filter': status_filter,
        'stats': stats,
    }

    return render(request, 'planning/strategic/list.html', context)


@login_required
def strategic_plan_detail(request, pk):
    """
    Strategic plan detail with goals, timeline, and annual plans
    """
    plan = get_object_or_404(StrategicPlan, pk=pk)

    # Get goals grouped by priority
    goals_by_priority = {
        'critical': plan.goals.filter(priority='critical'),
        'high': plan.goals.filter(priority='high'),
        'medium': plan.goals.filter(priority='medium'),
        'low': plan.goals.filter(priority='low'),
    }

    # Get annual plans within this strategic plan
    annual_plans = plan.annual_plans.all().annotate(
        objective_count=Count('objectives'),
        avg_objective_progress=Avg('objectives__completion_percentage')
    )

    context = {
        'plan': plan,
        'goals_by_priority': goals_by_priority,
        'annual_plans': annual_plans,
    }

    return render(request, 'planning/strategic/detail.html', context)


@login_required
def strategic_plan_create(request):
    """
    Create new strategic plan
    """
    if request.method == 'POST':
        form = StrategicPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.created_by = request.user
            plan.save()

            messages.success(
                request,
                f'Strategic plan "{plan.title}" created successfully.'
            )
            return redirect('planning:strategic_detail', pk=plan.pk)
    else:
        form = StrategicPlanForm()

    context = {
        'form': form,
        'action': 'Create',
    }

    return render(request, 'planning/strategic/form.html', context)


@login_required
def strategic_plan_edit(request, pk):
    """
    Edit existing strategic plan
    """
    plan = get_object_or_404(StrategicPlan, pk=pk)

    if request.method == 'POST':
        form = StrategicPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()

            messages.success(
                request,
                f'Strategic plan "{plan.title}" updated successfully.'
            )
            return redirect('planning:strategic_detail', pk=plan.pk)
    else:
        form = StrategicPlanForm(instance=plan)

    context = {
        'form': form,
        'plan': plan,
        'action': 'Edit',
    }

    return render(request, 'planning/strategic/form.html', context)


@login_required
def strategic_plan_delete(request, pk):
    """
    Archive (soft delete) strategic plan
    """
    plan = get_object_or_404(StrategicPlan, pk=pk)

    if request.method == 'POST':
        # Soft delete by setting status to archived
        plan.status = 'archived'
        plan.save(update_fields=['status'])

        messages.success(
            request,
            f'Strategic plan "{plan.title}" archived successfully.'
        )
        return redirect('planning:strategic_list')

    context = {
        'plan': plan,
    }

    return render(request, 'planning/strategic/delete_confirm.html', context)


# ============================================================================
# STRATEGIC GOAL VIEWS
# ============================================================================

@login_required
def goal_create(request, plan_id):
    """
    Add goal to strategic plan
    """
    plan = get_object_or_404(StrategicPlan, pk=plan_id)

    if request.method == 'POST':
        form = StrategicGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.strategic_plan = plan
            goal.save()

            messages.success(
                request,
                f'Strategic goal "{goal.title}" added successfully.'
            )
            return redirect('planning:strategic_detail', pk=plan.pk)
    else:
        form = StrategicGoalForm()

    context = {
        'form': form,
        'plan': plan,
        'action': 'Add',
    }

    return render(request, 'planning/goals/form.html', context)


@login_required
def goal_edit(request, pk):
    """
    Update goal details
    """
    goal = get_object_or_404(StrategicGoal, pk=pk)

    if request.method == 'POST':
        form = StrategicGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()

            messages.success(
                request,
                f'Strategic goal "{goal.title}" updated successfully.'
            )
            return redirect('planning:strategic_detail', pk=goal.strategic_plan.pk)
    else:
        form = StrategicGoalForm(instance=goal)

    context = {
        'form': form,
        'goal': goal,
        'action': 'Edit',
    }

    return render(request, 'planning/goals/form.html', context)


@login_required
def goal_update_progress(request, pk):
    """
    HTMX endpoint to update goal completion percentage
    """
    if request.method == 'POST':
        goal = get_object_or_404(StrategicGoal, pk=pk)

        try:
            completion_percentage = float(request.POST.get('completion_percentage', 0))

            # Validate percentage is between 0 and 100
            if 0 <= completion_percentage <= 100:
                goal.completion_percentage = completion_percentage
                goal.save(update_fields=['completion_percentage'])

                return JsonResponse({
                    'success': True,
                    'message': 'Progress updated successfully',
                    'completion_percentage': goal.completion_percentage
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Completion percentage must be between 0 and 100'
                }, status=400)

        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'message': 'Invalid completion percentage value'
            }, status=400)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


@login_required
def goal_delete(request, pk):
    """
    Remove goal from strategic plan
    """
    goal = get_object_or_404(StrategicGoal, pk=pk)
    plan_pk = goal.strategic_plan.pk

    if request.method == 'POST':
        goal_title = goal.title
        goal.delete()

        messages.success(
            request,
            f'Strategic goal "{goal_title}" removed successfully.'
        )
        return redirect('planning:strategic_detail', pk=plan_pk)

    context = {
        'goal': goal,
    }

    return render(request, 'planning/goals/delete_confirm.html', context)


# ============================================================================
# ANNUAL WORK PLAN VIEWS
# ============================================================================

@login_required
def annual_plan_list(request):
    """
    List annual work plans with filtering by year
    """
    year_filter = request.GET.get('year', 'all')

    plans = AnnualWorkPlan.objects.all()

    if year_filter != 'all':
        plans = plans.filter(year=int(year_filter))

    # Annotate with objective counts
    plans = plans.annotate(
        objective_count=Count('objectives'),
        completed_objectives=Count(
            'objectives',
            filter=Q(objectives__status='completed')
        )
    )

    # Get available years for filter
    available_years = AnnualWorkPlan.objects.values_list(
        'year', flat=True
    ).distinct().order_by('-year')

    context = {
        'plans': plans,
        'year_filter': year_filter,
        'available_years': available_years,
    }

    return render(request, 'planning/annual/list.html', context)


@login_required
def annual_plan_detail(request, pk):
    """
    Annual work plan detail with objectives and M&E program links
    """
    plan = get_object_or_404(AnnualWorkPlan, pk=pk)

    # Get objectives grouped by status
    objectives_by_status = {
        'not_started': plan.objectives.filter(status='not_started'),
        'in_progress': plan.objectives.filter(status='in_progress'),
        'completed': plan.objectives.filter(status='completed'),
    }

    # Get linked M&E programs
    linked_programs = plan.linked_programs.all()

    context = {
        'plan': plan,
        'objectives_by_status': objectives_by_status,
        'linked_programs': linked_programs,
    }

    return render(request, 'planning/annual/detail.html', context)


@login_required
def annual_plan_create(request):
    """
    Create new annual plan
    """
    if request.method == 'POST':
        form = AnnualWorkPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.created_by = request.user
            plan.save()

            messages.success(
                request,
                f'Annual work plan "{plan.title}" created successfully.'
            )
            return redirect('planning:annual_detail', pk=plan.pk)
    else:
        form = AnnualWorkPlanForm()

    context = {
        'form': form,
        'action': 'Create',
    }

    return render(request, 'planning/annual/form.html', context)


@login_required
def annual_plan_edit(request, pk):
    """
    Update annual plan
    """
    plan = get_object_or_404(AnnualWorkPlan, pk=pk)

    if request.method == 'POST':
        form = AnnualWorkPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()

            messages.success(
                request,
                f'Annual work plan "{plan.title}" updated successfully.'
            )
            return redirect('planning:annual_detail', pk=plan.pk)
    else:
        form = AnnualWorkPlanForm(instance=plan)

    context = {
        'form': form,
        'plan': plan,
        'action': 'Edit',
    }

    return render(request, 'planning/annual/form.html', context)


@login_required
def annual_plan_delete(request, pk):
    """
    Archive annual plan
    """
    plan = get_object_or_404(AnnualWorkPlan, pk=pk)

    if request.method == 'POST':
        # Soft delete by setting status to archived
        plan.status = 'archived'
        plan.save(update_fields=['status'])

        messages.success(
            request,
            f'Annual work plan "{plan.title}" archived successfully.'
        )
        return redirect('planning:annual_list')

    context = {
        'plan': plan,
    }

    return render(request, 'planning/annual/delete_confirm.html', context)


# ============================================================================
# WORK PLAN OBJECTIVE VIEWS
# ============================================================================

@login_required
def objective_create(request, plan_id):
    """
    Add objective to annual plan
    """
    plan = get_object_or_404(AnnualWorkPlan, pk=plan_id)

    if request.method == 'POST':
        form = WorkPlanObjectiveForm(request.POST)
        if form.is_valid():
            objective = form.save(commit=False)
            objective.annual_work_plan = plan
            objective.save()

            messages.success(
                request,
                f'Objective "{objective.title}" added successfully.'
            )
            return redirect('planning:annual_detail', pk=plan.pk)
    else:
        form = WorkPlanObjectiveForm()

    context = {
        'form': form,
        'plan': plan,
        'action': 'Add',
    }

    return render(request, 'planning/objectives/form.html', context)


@login_required
def objective_edit(request, pk):
    """
    Update objective
    """
    objective = get_object_or_404(WorkPlanObjective, pk=pk)

    if request.method == 'POST':
        form = WorkPlanObjectiveForm(request.POST, instance=objective)
        if form.is_valid():
            form.save()

            messages.success(
                request,
                f'Objective "{objective.title}" updated successfully.'
            )
            return redirect('planning:annual_detail', pk=objective.annual_work_plan.pk)
    else:
        form = WorkPlanObjectiveForm(instance=objective)

    context = {
        'form': form,
        'objective': objective,
        'action': 'Edit',
    }

    return render(request, 'planning/objectives/form.html', context)


@login_required
def objective_update_progress(request, pk):
    """
    HTMX endpoint to update objective completion percentage
    """
    if request.method == 'POST':
        objective = get_object_or_404(WorkPlanObjective, pk=pk)

        try:
            completion_percentage = float(request.POST.get('completion_percentage', 0))

            # Validate percentage is between 0 and 100
            if 0 <= completion_percentage <= 100:
                objective.completion_percentage = completion_percentage
                objective.save(update_fields=['completion_percentage'])

                return JsonResponse({
                    'success': True,
                    'message': 'Progress updated successfully',
                    'completion_percentage': objective.completion_percentage
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Completion percentage must be between 0 and 100'
                }, status=400)

        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'message': 'Invalid completion percentage value'
            }, status=400)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


@login_required
def objective_delete(request, pk):
    """
    Remove objective
    """
    objective = get_object_or_404(WorkPlanObjective, pk=pk)
    plan_pk = objective.annual_work_plan.pk

    if request.method == 'POST':
        objective_title = objective.title
        objective.delete()

        messages.success(
            request,
            f'Objective "{objective_title}" removed successfully.'
        )
        return redirect('planning:annual_detail', pk=plan_pk)

    context = {
        'objective': objective,
    }

    return render(request, 'planning/objectives/delete_confirm.html', context)


# ============================================================================
# DASHBOARD VIEW
# ============================================================================

@login_required
def planning_dashboard(request):
    """
    Planning module dashboard with overview stats and quick actions
    """
    # Strategic planning metrics
    strategic_stats = {
        'total_plans': StrategicPlan.objects.count(),
        'active_plans': StrategicPlan.objects.filter(status='active').count(),
        'draft_plans': StrategicPlan.objects.filter(status='draft').count(),
    }

    # Strategic goals metrics
    goals_stats = {
        'total_goals': StrategicGoal.objects.count(),
        'completed_goals': StrategicGoal.objects.filter(status='completed').count(),
        'in_progress_goals': StrategicGoal.objects.filter(status='in_progress').count(),
        'not_started_goals': StrategicGoal.objects.filter(status='not_started').count(),
    }

    # Annual planning metrics
    annual_stats = {
        'total_annual_plans': AnnualWorkPlan.objects.count(),
        'active_annual_plans': AnnualWorkPlan.objects.filter(status='active').count(),
    }

    # Objectives metrics
    objectives_stats = {
        'total_objectives': WorkPlanObjective.objects.count(),
        'completed_objectives': WorkPlanObjective.objects.filter(status='completed').count(),
        'in_progress_objectives': WorkPlanObjective.objects.filter(status='in_progress').count(),
    }

    # Get active strategic plan
    active_plan = StrategicPlan.objects.filter(status='active').first()

    # Get recent strategic plans
    recent_plans = StrategicPlan.objects.all().order_by('-created_at')[:5]

    # Get recent annual plans
    recent_annual_plans = AnnualWorkPlan.objects.all().order_by('-created_at')[:5]

    context = {
        'strategic_stats': strategic_stats,
        'goals_stats': goals_stats,
        'annual_stats': annual_stats,
        'objectives_stats': objectives_stats,
        'active_plan': active_plan,
        'recent_plans': recent_plans,
        'recent_annual_plans': recent_annual_plans,
    }

    return render(request, 'planning/dashboard.html', context)
