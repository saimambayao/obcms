"""
Planning Module Forms

This module provides form classes for strategic planning functionality.
All forms follow OBCMS UI standards with Tailwind CSS styling.

BMMS Note: Forms are organization-agnostic. Organization context will be
added through views/middleware in BMMS migration.
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import StrategicPlan, StrategicGoal, AnnualWorkPlan, WorkPlanObjective


class StrategicPlanForm(forms.ModelForm):
    """
    Form for creating/editing strategic plans

    Features:
    - Tailwind CSS styling following OBCMS standards
    - Year range validation (end_year > start_year)
    - Max 10-year duration validation
    - Overlapping plan detection
    - Accessibility-compliant min-h-[48px] inputs
    """

    class Meta:
        model = StrategicPlan
        fields = [
            'title',
            'start_year',
            'end_year',
            'vision',
            'mission',
            'status',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'placeholder': 'e.g., OOBC Strategic Plan 2024-2028'
            }),
            'start_year': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'min': 2020,
            }),
            'end_year': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'min': 2020,
            }),
            'vision': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 resize-vertical',
                'rows': 4,
                'placeholder': 'Describe the long-term vision...'
            }),
            'mission': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 resize-vertical',
                'rows': 4,
                'placeholder': 'Describe the mission statement...'
            }),
            'status': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white'
            }),
        }

    def clean(self):
        """
        Validate year range and check for overlapping plans
        """
        cleaned_data = super().clean()
        start_year = cleaned_data.get('start_year')
        end_year = cleaned_data.get('end_year')

        if start_year and end_year:
            # Validate year range
            if end_year <= start_year:
                raise ValidationError("End year must be after start year")

            if end_year - start_year > 10:
                raise ValidationError("Strategic plans should not exceed 10 years")

            # Check for overlapping plans (excluding current instance if editing)
            overlapping_plans = StrategicPlan.objects.filter(
                start_year__lte=end_year,
                end_year__gte=start_year
            )

            if self.instance.pk:
                overlapping_plans = overlapping_plans.exclude(pk=self.instance.pk)

            if overlapping_plans.exists():
                raise ValidationError(
                    f"A strategic plan already exists for this year range: "
                    f"{overlapping_plans.first()}"
                )

        return cleaned_data


class StrategicGoalForm(forms.ModelForm):
    """
    Form for creating/editing strategic goals

    Features:
    - Tailwind CSS styling following OBCMS standards
    - Target value validation (must be > 0)
    - Priority and status dropdowns
    - Accessibility-compliant inputs
    """

    class Meta:
        model = StrategicGoal
        fields = [
            'strategic_plan',
            'title',
            'description',
            'target_metric',
            'target_value',
            'current_value',
            'completion_percentage',
            'priority',
            'status',
        ]
        widgets = {
            'strategic_plan': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'placeholder': 'e.g., Improve education access in OBCs'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 resize-vertical',
                'rows': 3,
            }),
            'target_metric': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'placeholder': 'e.g., Number of schools built'
            }),
            'target_value': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'step': '0.01',
                'min': '0.01',
            }),
            'current_value': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'step': '0.01',
                'min': '0',
            }),
            'completion_percentage': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'step': '0.01',
                'min': '0',
                'max': '100',
            }),
            'priority': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white'
            }),
            'status': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white'
            }),
        }

    def clean_target_value(self):
        """Validate that target_value is greater than 0"""
        target_value = self.cleaned_data.get('target_value')

        if target_value is not None and target_value <= 0:
            raise ValidationError("Target value must be greater than 0")

        return target_value


class AnnualWorkPlanForm(forms.ModelForm):
    """
    Form for creating/editing annual work plans

    Features:
    - Tailwind CSS styling following OBCMS standards
    - Year validation (must be within strategic plan range)
    - Budget field support
    - Accessibility-compliant inputs
    """

    class Meta:
        model = AnnualWorkPlan
        fields = [
            'strategic_plan',
            'title',
            'year',
            'description',
            'budget_total',
            'status',
        ]
        widgets = {
            'strategic_plan': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'placeholder': 'e.g., OOBC Annual Work Plan 2025'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'min': 2020,
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 resize-vertical',
                'rows': 4,
                'placeholder': 'Overview of annual priorities and approach...'
            }),
            'budget_total': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'status': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white'
            }),
        }

    def clean(self):
        """Validate that year is within strategic plan range"""
        cleaned_data = super().clean()
        year = cleaned_data.get('year')
        strategic_plan = cleaned_data.get('strategic_plan')

        if year and strategic_plan:
            if year < strategic_plan.start_year or year > strategic_plan.end_year:
                raise ValidationError(
                    f"Annual plan year must be within strategic plan range "
                    f"({strategic_plan.start_year}-{strategic_plan.end_year})"
                )

        return cleaned_data


class WorkPlanObjectiveForm(forms.ModelForm):
    """
    Form for creating/editing work plan objectives

    Features:
    - Tailwind CSS styling following OBCMS standards
    - Validation: target_value > baseline_value
    - Date picker support for target_date
    - Indicator tracking fields
    - Accessibility-compliant inputs
    """

    class Meta:
        model = WorkPlanObjective
        fields = [
            'annual_work_plan',
            'strategic_goal',
            'title',
            'description',
            'target_date',
            'indicator',
            'baseline_value',
            'target_value',
            'current_value',
            'completion_percentage',
            'status',
        ]
        widgets = {
            'annual_work_plan': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white'
            }),
            'strategic_goal': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'placeholder': 'e.g., Build 5 new classrooms in Lanao del Sur OBCs'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 resize-vertical',
                'rows': 3,
            }),
            'target_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'type': 'date',
            }),
            'indicator': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'placeholder': 'e.g., Number of classrooms constructed'
            }),
            'baseline_value': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'step': '0.01',
                'min': '0',
            }),
            'target_value': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'step': '0.01',
                'min': '0',
            }),
            'current_value': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'step': '0.01',
                'min': '0',
            }),
            'completion_percentage': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'step': '0.01',
                'min': '0',
                'max': '100',
            }),
            'status': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white'
            }),
        }

    def clean(self):
        """Validate that target_value is greater than baseline_value"""
        cleaned_data = super().clean()
        baseline_value = cleaned_data.get('baseline_value')
        target_value = cleaned_data.get('target_value')

        if baseline_value is not None and target_value is not None:
            if target_value <= baseline_value:
                raise ValidationError(
                    "Target value must be greater than baseline value"
                )

        return cleaned_data
