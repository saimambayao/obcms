"""
Forms for WorkItem model with dynamic field rendering.

Supports:
- Unified form for all work types (Project, Activity, Task)
- Dynamic field visibility based on work_type
- MPTT parent selection
- Type-specific data validation
"""

from decimal import Decimal, InvalidOperation

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Case, IntegerField, Value, When, Q

from coordination.models import Organization
from monitoring.models import MonitoringEntry

from common.constants import STAFF_DIRECTORY_PRIORITY
from common.work_item_model import WorkItem
from common.models import User, StaffTeam


class WorkItemForm(forms.ModelForm):
    """
    Unified form for creating/editing WorkItems.

    Features:
    - Type selector (Project/Activity/Task)
    - Dynamic field rendering based on selected type
    - Parent selection with hierarchy validation
    - Assignees and teams multi-select
    """

    related_ppa = forms.ModelChoiceField(
        queryset=MonitoringEntry.objects.none(),
        required=False,
        empty_label="No related PPA",
        help_text="Select the OOBC PPA that this work item supports.",
        widget=forms.Select(attrs={
            'class': ''
        })
    )

    # Override parent field for better UI
    parent = forms.ModelChoiceField(
        queryset=WorkItem.objects.all(),
        required=False,
        empty_label="(None - Top Level)",
        help_text="Select parent work item",
        widget=forms.Select(attrs={
            'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white transition-all duration-200',
        })
    )

    # Assignees multi-select
    assignees = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True).order_by('first_name', 'last_name'),
        required=False,
        help_text="Select assigned users",
        widget=forms.SelectMultiple(attrs={
            'class': 'searchable-multi-select block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[200px] transition-all duration-200',
            'size': '5'
        })
    )

    # Teams multi-select
    teams = forms.ModelMultipleChoiceField(
        queryset=StaffTeam.objects.filter(is_active=True).order_by('name'),
        required=False,
        help_text="Select assigned teams",
        widget=forms.SelectMultiple(attrs={
            'class': 'searchable-multi-select block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[180px] transition-all duration-200',
            'size': '4'
        })
    )

    allocated_budget = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'block w-full pl-10 pr-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
            'placeholder': '0.00',
            'data-currency-input': 'true',
            'inputmode': 'decimal',
            'oninput': 'calculateBudgetVariance()',
            'autocomplete': 'off',
        })
    )

    actual_expenditure = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'block w-full pl-10 pr-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
            'placeholder': '0.00',
            'data-currency-input': 'true',
            'inputmode': 'decimal',
            'oninput': 'calculateBudgetVariance()',
            'autocomplete': 'off',
        })
    )

    class Meta:
        model = WorkItem
        fields = [
            'work_type',
            'parent',
            'title',
            'description',
            'status',
            'priority',
            'related_ppa',
            'allocated_budget',
            'actual_expenditure',
            'start_date',
            'due_date',
            'start_time',
            'end_time',
            'progress',
            'auto_calculate_progress',
            'assignees',
            'teams',
            'is_calendar_visible',
            'calendar_color',
        ]
        widgets = {
            'work_type': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white transition-all duration-200',
                'onchange': 'updateFormFields(this.value)',
            }),
            'parent': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white transition-all duration-200',
            }),
            'title': forms.TextInput(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'placeholder': 'Enter work item title...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[120px]',
                'placeholder': 'Enter detailed description...',
                'rows': 4
            }),
            'status': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white transition-all duration-200',
            }),
            'priority': forms.Select(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none pr-12 bg-white transition-all duration-200',
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'type': 'date'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'type': 'date'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'type': 'time'
            }),
            'progress': forms.NumberInput(attrs={
                'class': 'block w-full py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'min': 0,
                'max': 100
            }),
            'auto_calculate_progress': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-emerald-600 focus:ring-emerald-500 border-gray-300 rounded',
            }),
            'is_calendar_visible': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-emerald-600 focus:ring-emerald-500 border-gray-300 rounded',
            }),
            'calendar_color': forms.TextInput(attrs={
                'class': 'block w-24 py-3 px-4 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
                'type': 'color'
            }),
        }

    def __init__(self, *args, **kwargs):
        """Initialize form with dynamic parent queryset."""
        super().__init__(*args, **kwargs)

        # Determine MOA vs OOBC context for filtering
        is_moa_ppa = False
        if self.instance and self.instance.pk:
            is_moa_ppa = self.instance.ppa_category == 'moa_ppa'

        # Filter assignees based on context
        if is_moa_ppa:
            # MOA PPAs: Only MOA staff (bmoa, lgu, nga)
            # Only show approved and active users
            self.fields['assignees'].queryset = (
                User.objects.filter(
                    is_active=True,
                    is_approved=True,
                    user_type__in=['bmoa', 'lgu', 'nga']
                )
                .order_by('organization', 'last_name', 'first_name')
            )

            # Teams: Empty for MOA (teams are OOBC-only)
            self.fields['teams'].queryset = StaffTeam.objects.none()
            self.fields['teams'].help_text = "Team assignment not available for MOA PPAs"
        else:
            # OOBC work items: Surface OOBC leaders ahead of broader staff roster
            self.fields['assignees'].queryset = (
                User.objects.filter(is_active=True)
                .annotate(
                    preferred_order=Case(
                        *[
                            When(username=username, then=Value(idx))
                            for idx, username in enumerate(STAFF_DIRECTORY_PRIORITY)
                        ],
                        default=Value(len(STAFF_DIRECTORY_PRIORITY)),
                        output_field=IntegerField(),
                    ),
                    user_type_order=Case(
                        When(user_type="oobc_executive", then=Value(0)),
                        When(user_type="oobc_staff", then=Value(1)),
                        When(user_type="admin", then=Value(2)),
                        default=Value(3),
                        output_field=IntegerField(),
                    ),
                    leadership_order=Case(
                        When(position__iexact="Executive Director", then=Value(0)),
                        When(
                            position__iexact="Deputy Executive Director",
                            then=Value(1),
                        ),
                        When(position__icontains="DMO IV", then=Value(2)),
                        When(position__icontains="DMO III", then=Value(3)),
                        default=Value(4),
                        output_field=IntegerField(),
                    ),
                )
                .order_by(
                    "preferred_order",
                    "user_type_order",
                    "leadership_order",
                    "last_name",
                    "first_name",
                    "username",
                )
            )

        # Filter parent queryset based on work_type
        if (
            self.instance
            and self.instance.pk
            and not self.instance._state.adding
        ):
            # Editing existing item - exclude self and descendants
            self.fields['parent'].queryset = WorkItem.objects.exclude(
                pk=self.instance.pk
            ).exclude(
                pk__in=self.instance.get_descendants().values_list('pk', flat=True)
            )

            # Filter by valid parent types
            work_type = self.instance.work_type
            valid_parent_types = self._get_valid_parent_types(work_type)
            if valid_parent_types:
                self.fields['parent'].queryset = self.fields['parent'].queryset.filter(
                    work_type__in=valid_parent_types
                )

        # Make parent select prettier with hierarchy display
        self.fields['parent'].label_from_instance = self._parent_label

        # Populate Related PPA options (OOBC-focused by default)
        related_ppa_filter = Q(category='oobc_ppa')

        oobc_org = (
            Organization.objects.filter(name__iexact="Office for Other Bangsamoro Communities (OOBC)").first()
            or Organization.objects.filter(acronym__iexact="OOBC").first()
        )
        if oobc_org:
            related_ppa_filter |= Q(category='moa_ppa', implementing_moa=oobc_org)

        current_related = None
        if self.instance and self.instance.related_ppa_id:
            current_related = self.instance.related_ppa_id
        elif isinstance(self.initial.get('related_ppa'), MonitoringEntry):
            current_related = self.initial['related_ppa'].pk
        elif self.initial.get('related_ppa'):
            current_related = self.initial['related_ppa']

        if current_related:
            related_ppa_filter |= Q(pk=current_related)

        related_queryset = (
            MonitoringEntry.objects.filter(related_ppa_filter)
            .select_related('implementing_moa')
            .order_by('title')
        )
        self.fields['related_ppa'].queryset = related_queryset
        if is_moa_ppa:
            self.fields['related_ppa'].widget.attrs['disabled'] = True
            self.fields['related_ppa'].help_text = (
                "MOA-linked work items manage PPAs from the MOA module."
            )

    def _parent_label(self, obj):
        """Custom label for parent select showing hierarchy."""
        indent = "  " * obj.level
        type_display = obj.get_work_type_display()
        return f"{indent}{type_display}: {obj.title}"

    def _get_valid_parent_types(self, child_type):
        """Get list of valid parent types for a given child type."""
        return WorkItem.get_valid_parent_types(child_type)

    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        work_type = cleaned_data.get('work_type')
        parent = cleaned_data.get('parent')

        # Validate parent-child relationship
        if parent and work_type:
            if not parent.can_have_child_type(work_type):
                raise ValidationError({
                    'parent': f"{parent.get_work_type_display()} cannot have "
                             f"{dict(WorkItem.WORK_TYPE_CHOICES)[work_type]} as child"
                })

        # Validate dates
        start_date = cleaned_data.get('start_date')
        due_date = cleaned_data.get('due_date')
        if start_date and due_date and start_date > due_date:
            raise ValidationError({
                'due_date': 'Due date must be after start date'
            })

        return cleaned_data

    def save(self, commit=True):
        """Save with proper MPTT handling."""
        instance = super().save(commit=False)

        # Set created_by if new instance
        if not instance.pk and hasattr(self, 'user'):
            instance.created_by = self.user

        if commit:
            instance.save()
            self.save_m2m()

        return instance

    def clean_allocated_budget(self):
        """Allow currency strings with grouping separators."""
        return self._clean_currency_value('allocated_budget')

    def clean_actual_expenditure(self):
        """Allow currency strings with grouping separators."""
        return self._clean_currency_value('actual_expenditure')

    def _clean_currency_value(self, field_name):
        """Normalize formatted currency strings to Decimal values."""
        value = self.cleaned_data.get(field_name)
        if value in (None, ''):
            return None

        if isinstance(value, Decimal):
            return value

        normalized = str(value).strip().replace(',', '')
        if normalized == '':
            return None

        try:
            decimal_value = Decimal(normalized)
        except (InvalidOperation, ValueError):
            raise forms.ValidationError('Enter a valid amount (e.g., 1,234.56).')

        return decimal_value


class WorkItemQuickEditForm(forms.ModelForm):
    """
    Simplified form for quick editing/creating in calendar sidebar.

    This form includes only the most commonly edited fields for inline editing
    in the calendar detail panel, providing a streamlined UX for quick updates
    and calendar-based creation.
    """

    # Add allocated_budget as CharField to handle formatted currency input
    allocated_budget = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'block w-full pl-10 pr-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px]',
            'placeholder': '0.00',
            'data-currency-input': 'true',
            'inputmode': 'decimal',
            'autocomplete': 'off',
        })
    )

    implementing_moa = forms.ModelChoiceField(
        queryset=Organization.objects.none(),
        required=False,
        empty_label="Select implementing MOA...",
        widget=forms.Select(attrs={
            'class': 'block w-full py-2 px-3 text-sm rounded-lg border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 appearance-none',
        })
    )

    related_ppa = forms.ModelChoiceField(
        queryset=MonitoringEntry.objects.none(),
        required=False,
        empty_label="Select a PPA (optional)",
        widget=forms.Select(attrs={
            'class': 'block w-full py-2 px-3 text-sm rounded-lg border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 appearance-none',
        })
    )

    def __init__(self, *args, **kwargs):
        """Initialize form with user for created_by field."""
        # Extract user for created_by field
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Populate dropdowns after initialization to avoid circular imports during app loading
        self.fields['implementing_moa'].queryset = Organization.objects.order_by('name')
        self.fields['related_ppa'].queryset = (
            MonitoringEntry.objects.filter(category__in=['moa_ppa', 'oobc_ppa'])
            .order_by('title')
        )

    class Meta:
        model = WorkItem
        fields = [
            'work_type',  # Added for calendar creation
            'title',
            'status',
            'priority',
            'start_date',
            'due_date',
            'description',
            'progress',
            'allocated_budget',  # Added for budget tracking
            'implementing_moa',
            'related_ppa',
        ]
        widgets = {
            'work_type': forms.Select(attrs={
                'class': 'block w-full py-2 px-3 text-sm rounded-lg border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 appearance-none'
            }),
            'title': forms.TextInput(attrs={
                'class': 'block w-full py-2 px-3 text-sm rounded-lg border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500',
                'placeholder': 'Work item title'
            }),
            'status': forms.Select(attrs={
                'class': 'block w-full py-2 px-3 text-sm rounded-lg border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 appearance-none'
            }),
            'priority': forms.Select(attrs={
                'class': 'block w-full py-2 px-3 text-sm rounded-lg border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500 appearance-none'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'block w-full py-2 px-3 text-sm rounded-lg border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500',
                'type': 'date'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'block w-full py-2 px-3 text-sm rounded-lg border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500',
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'block w-full py-2 px-3 text-sm rounded-lg border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500',
                'placeholder': 'Description...'
            }),
            'progress': forms.NumberInput(attrs={
                'class': 'block w-full py-2 px-3 text-sm rounded-lg border border-gray-200 shadow-sm focus:ring-emerald-500 focus:border-emerald-500',
                'min': 0,
                'max': 100,
                'step': 1  # Allow any integer 0-100
            }),
        }

    def clean_allocated_budget(self):
        """Allow currency strings with grouping separators."""
        value = self.cleaned_data.get('allocated_budget')
        if value in (None, ''):
            return None

        if isinstance(value, Decimal):
            return value

        normalized = str(value).strip().replace(',', '')
        if normalized == '':
            return None

        try:
            decimal_value = Decimal(normalized)
        except (InvalidOperation, ValueError):
            raise forms.ValidationError('Enter a valid amount (e.g., 1,234.56).')

        return decimal_value

    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()

        # Validate dates
        start_date = cleaned_data.get('start_date')
        due_date = cleaned_data.get('due_date')
        if start_date and due_date and start_date > due_date:
            raise ValidationError({
                'due_date': 'Due date must be after start date'
            })

        return cleaned_data

    def save(self, commit=True):
        """Save with created_by field populated."""
        instance = super().save(commit=False)

        # Set created_by for new instances
        if not instance.pk and self.user:
            instance.created_by = self.user

        if commit:
            instance.save()

        return instance
