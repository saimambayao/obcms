class RegionalWorkshopSetupForm(forms.ModelForm):
    """Form to launch a regional-level workshop assessment using Region/Province selection."""

    # Region selection field
    region = forms.ModelChoiceField(
        queryset=Region.objects.filter(is_active=True).order_by("code", "name"),
        required=True,
        label="Region",
        widget=forms.Select(attrs={
            "class": "block w-full py-3 px-4 text-base rounded-lg border border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 min-h-[48px] transition-all duration-200",
            "data-level": "region"
        }),
        help_text="Region where the assessment will be conducted"
    )

    # Province selection field (will be populated via JavaScript)
    province = forms.ModelChoiceField(
        queryset=Province.objects.none(),  # Empty initially
        required=True,
        label="Province",
        widget=forms.Select(attrs={
            "class": "block w-full py-3 px-4 text-base rounded-lg border border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 min-h-[48px] transition-all duration-200",
            "data-level": "province"
        }),
        help_text="Province being assessed"
    )

    # Date fields
    planned_start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "block w-full rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"}),
        label="Planned Start Date",
        help_text="When the regional workshop will begin"
    )
    planned_end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "block w-full rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"}),
        label="Planned End Date",
        help_text="When the regional workshop will end"
    )

    # Optional target participants
    target_participants = forms.IntegerField(
        required=False,
        min_value=1,
        initial=30,
        label="Target Participants",
        widget=forms.NumberInput(
            attrs={
                "class": "block w-full rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                "placeholder": "Number of expected participants (default: 30)",
            }
        ),
        help_text="Expected number of participants for the workshops"
    )

    class Meta:
        model = Assessment
        fields = [
            "title",
            "planned_start_date",
            "planned_end_date",
            "objectives",
            "description",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "block w-full rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                    "placeholder": "e.g., Regional Workshop Cycle - SOCCSKSARGEN 2025",
                }
            ),
            "objectives": forms.Textarea(
                attrs={
                    "class": "block w-full rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                    "rows": 3,
                    "placeholder": "Key objectives for the regional workshop cycle",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "block w-full rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                    "rows": 3,
                    "placeholder": "Brief description of the regional MANA deployment and coverage",
                }
            ),
        }

    def __init__(self, *args, regions=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Set up region queryset (optionally filter by provided regions)
        region_qs = Region.objects.filter(is_active=True).order_by("code", "name")
        if regions is not None:
            region_qs = region_qs.filter(id__in=[r.id for r in regions])
        self.fields["region"].queryset = region_qs

        # If editing existing assessment, populate province choices
        if self.instance and self.instance.pk and self.instance.province:
            selected_region = self.instance.province.region
            self.fields["region"].initial = selected_region.id
            self.fields["province"].queryset = Province.objects.filter(
                region=selected_region, is_active=True
            ).order_by("name")
            self.fields["province"].initial = self.instance.province.id

        # Set default values
        today = timezone.now().date()
        self.fields["planned_start_date"].initial = self.fields["planned_start_date"].initial or today
        self.fields["planned_end_date"].initial = self.fields["planned_end_date"].initial or (today + timedelta(days=4))
        self.fields["target_participants"].initial = 30
        self.fields["title"].initial = (
            self.fields["title"].initial
            or f"Regional Workshop Cycle - {today.year}"
        )
        self.fields["objectives"].initial = self.fields["objectives"].initial or (
            "Coordinate the regional workshop cycle and document core outputs across the mandated sessions."
        )
        self.fields["description"].initial = self.fields["description"].initial or (
            "Regional-level facilitation of the five-day MANA workshop structure, covering context, aspirations, collaboration, feedback, and action planning."
        )

    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()

        # Validate dates
        start_date = cleaned_data.get('planned_start_date')
        end_date = cleaned_data.get('planned_end_date')

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError(
                "Planned end date cannot be earlier than start date."
            )

        # Validate that the province belongs to the selected region
        region = cleaned_data.get('region')
        province = cleaned_data.get('province')

        if region and province and province.region != region:
            raise forms.ValidationError(
                "The selected province does not belong to the selected region."
            )

        return cleaned_data

    def save(self, user=None, commit=True):
        """Save the assessment with proper defaults for regional workshop."""
        assessment = super().save(commit=False)

        # Create or get the assessment category
        from .models import AssessmentCategory
        category, _ = AssessmentCategory.objects.get_or_create(
            name="OBC-MANA Workshop",
            defaults={
                "category_type": "needs_assessment",
                "description": "Other Bangsamoro Communities Mapping and Needs Assessment",
                "icon": "fas fa-users",
                "color": "#3B82F6",
            },
        )

        # Set assessment properties for regional workshop
        assessment.category = category
        assessment.assessment_level = "regional"
        assessment.primary_methodology = "workshop"
        assessment.priority = assessment.priority or "medium"

        # Link to province instead of community
        assessment.province = self.cleaned_data['province']
        assessment.community = None  # Regional assessments don't link to specific communities

        # Set user as lead assessor if provided
        if user is not None:
            assessment.created_by = user
            if not assessment.lead_assessor_id:
                assessment.lead_assessor = user

        if commit:
            assessment.save()
            self.save_m2m()

        return assessment