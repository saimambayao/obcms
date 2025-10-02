"""Forms for coordination module frontend interactions."""

from django import forms
from django.contrib.auth import get_user_model
from django.forms import BaseInlineFormSet, inlineformset_factory

from communities.models import OBCCommunity
from mana.models import Assessment

from common.models import RecurringEventPattern

from .models import (
    Event,
    Organization,
    OrganizationContact,
    Partnership,
    PartnershipDocument,
    PartnershipMilestone,
    PartnershipSignatory,
    StakeholderEngagement,
)

INPUT_CLASS = (
    "block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm "
    "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
)
TEXTAREA_CLASS = (
    "block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm "
    "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
)
CHECKBOX_CLASS = "h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"

DATE_WIDGET = forms.DateInput(attrs={"type": "date", "class": INPUT_CLASS})
TIME_WIDGET = forms.TimeInput(attrs={"type": "time", "class": INPUT_CLASS})
DATETIME_WIDGET = forms.DateTimeInput(
    attrs={"type": "datetime-local", "class": INPUT_CLASS}
)

MULTISELECT_CLASS = (
    "block w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm "
    "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
)

User = get_user_model()


def _apply_field_styles(fields):
    for field in fields.values():
        widget = field.widget
        if isinstance(widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
            widget.attrs.setdefault("class", CHECKBOX_CLASS)
        elif isinstance(widget, forms.SelectMultiple):
            widget.attrs.setdefault("class", MULTISELECT_CLASS)
        elif isinstance(widget, (forms.Textarea,)):
            widget.attrs.setdefault("class", TEXTAREA_CLASS)
        else:
            widget.attrs.setdefault("class", INPUT_CLASS)


class OrganizationForm(forms.ModelForm):
    """Collect organization metadata outside the admin interface."""

    social_media = forms.JSONField(
        required=False, widget=forms.Textarea(attrs={"rows": 3})
    )

    class Meta:
        model = Organization
        exclude = [
            "id",
            "created_by",
            "created_at",
            "updated_at",
        ]
        widgets = {
            "partnership_start_date": DATE_WIDGET,
            "last_engagement_date": DATE_WIDGET,
        }

    def clean_social_media(self):
        social_media = self.cleaned_data.get("social_media")
        if not social_media:
            return None
        return social_media

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_field_styles(self.fields)
        if isinstance(self.fields.get("social_media").widget, forms.Textarea):
            self.fields["social_media"].widget.attrs.setdefault(
                "placeholder", '{"facebook": "https://facebook.com/..."}'
            )


class OrganizationContactForm(forms.ModelForm):
    """Inline form for creating organization contacts."""

    class Meta:
        model = OrganizationContact
        exclude = ["organization", "created_at", "updated_at"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_field_styles(self.fields)


class BaseOrganizationContactFormSet(BaseInlineFormSet):
    """Ensure only one primary contact is marked and ignore empty rows."""

    def clean(self):
        super().clean()
        primary_count = 0
        for form in self.forms:
            if form.cleaned_data.get("DELETE"):
                continue
            if not form.cleaned_data or not form.has_changed():
                continue
            if form.cleaned_data.get("is_primary"):
                primary_count += 1
        if primary_count > 1:
            raise forms.ValidationError("Please mark only one contact as primary.")


OrganizationContactFormSet = inlineformset_factory(
    Organization,
    OrganizationContact,
    form=OrganizationContactForm,
    formset=BaseOrganizationContactFormSet,
    extra=1,
    can_delete=True,
)


class PartnershipForm(forms.ModelForm):
    """Frontend form mirroring the admin partnership configuration."""

    organizations = forms.ModelMultipleChoiceField(
        queryset=Organization.objects.none(),
        widget=forms.SelectMultiple(attrs={"class": MULTISELECT_CLASS}),
    )
    communities = forms.ModelMultipleChoiceField(
        queryset=OBCCommunity.objects.none(),
        widget=forms.SelectMultiple(attrs={"class": MULTISELECT_CLASS}),
        required=False,
    )

    class Meta:
        model = Partnership
        exclude = [
            "id",
            "created_by",
            "created_at",
            "updated_at",
        ]
        widgets = {
            "concept_date": DATE_WIDGET,
            "negotiation_start_date": DATE_WIDGET,
            "signing_date": DATE_WIDGET,
            "start_date": DATE_WIDGET,
            "end_date": DATE_WIDGET,
            "renewal_date": DATE_WIDGET,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_field_styles(self.fields)
        self.fields["organizations"].queryset = Organization.objects.order_by("name")
        self.fields["communities"].queryset = OBCCommunity.objects.order_by("name")
        self.fields["focal_person"].queryset = User.objects.order_by(
            "first_name", "last_name"
        )
        self.fields["backup_focal_person"].queryset = User.objects.order_by(
            "first_name", "last_name"
        )
        self.fields["focal_person"].required = False
        self.fields["backup_focal_person"].required = False


class PartnershipSignatoryForm(forms.ModelForm):
    """Inline form for partnership signatories."""

    class Meta:
        model = PartnershipSignatory
        fields = ["organization", "name", "position", "signature_date"]
        widgets = {
            "signature_date": DATE_WIDGET,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_field_styles(self.fields)
        self.fields["organization"].queryset = Organization.objects.order_by("name")


class PartnershipMilestoneForm(forms.ModelForm):
    """Inline form for partnership milestones."""

    class Meta:
        model = PartnershipMilestone
        fields = ["title", "due_date", "status", "progress_percentage"]
        widgets = {
            "due_date": DATE_WIDGET,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_field_styles(self.fields)


class PartnershipDocumentForm(forms.ModelForm):
    """Inline form for partnership documents."""

    class Meta:
        model = PartnershipDocument
        fields = ["document_type", "title", "file", "is_confidential"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_field_styles(self.fields)


PartnershipSignatoryFormSet = inlineformset_factory(
    Partnership,
    PartnershipSignatory,
    form=PartnershipSignatoryForm,
    extra=1,
    can_delete=True,
)


PartnershipMilestoneFormSet = inlineformset_factory(
    Partnership,
    PartnershipMilestone,
    form=PartnershipMilestoneForm,
    extra=1,
    can_delete=True,
)


PartnershipDocumentFormSet = inlineformset_factory(
    Partnership,
    PartnershipDocument,
    form=PartnershipDocumentForm,
    extra=1,
    can_delete=True,
)


class EventForm(forms.ModelForm):
    """Frontend form for scheduling coordination events."""

    class Meta:
        model = Event
        fields = [
            "title",
            "event_type",
            "status",
            "priority",
            "description",
            "objectives",
            "community",
            "organizations",
            "related_engagement",
            "related_assessment",
            "start_date",
            "start_time",
            "end_date",
            "end_time",
            "duration_hours",
            "venue",
            "address",
            "is_virtual",
            "virtual_platform",
            "virtual_link",
            "virtual_meeting_id",
            "virtual_passcode",
            "organizer",
            "co_organizers",
            "facilitators",
            "expected_participants",
            "actual_participants",
            "target_audience",
            "agenda",
            "materials_needed",
            "minutes",
            "outcomes",
            "decisions_made",
            "key_discussions",
            "budget_allocated",
            "actual_cost",
            "feedback_summary",
            "satisfaction_rating",
            "lessons_learned",
            "follow_up_required",
            "follow_up_date",
            "follow_up_notes",
            "is_recurring",
            "recurrence_pattern",
            "recurrence_parent",
            "is_recurrence_exception",
            "parent_event",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "objectives": forms.Textarea(attrs={"rows": 3}),
            "agenda": forms.Textarea(attrs={"rows": 3}),
            "materials_needed": forms.Textarea(attrs={"rows": 3}),
            "minutes": forms.Textarea(attrs={"rows": 3}),
            "outcomes": forms.Textarea(attrs={"rows": 3}),
            "decisions_made": forms.Textarea(attrs={"rows": 3}),
            "key_discussions": forms.Textarea(attrs={"rows": 3}),
            "feedback_summary": forms.Textarea(attrs={"rows": 3}),
            "lessons_learned": forms.Textarea(attrs={"rows": 3}),
            "follow_up_notes": forms.Textarea(attrs={"rows": 3}),
            "address": forms.Textarea(attrs={"rows": 3}),
            "target_audience": forms.Textarea(attrs={"rows": 2}),
            "start_date": DATE_WIDGET,
            "end_date": DATE_WIDGET,
            "follow_up_date": DATE_WIDGET,
            "start_time": TIME_WIDGET,
            "end_time": TIME_WIDGET,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_field_styles(self.fields)
        self.fields["community"].queryset = OBCCommunity.objects.order_by("name")
        self.fields["organizations"].queryset = Organization.objects.order_by("name")
        self.fields["co_organizers"].queryset = User.objects.order_by(
            "first_name",
            "last_name",
        )
        self.fields["facilitators"].queryset = User.objects.order_by(
            "first_name",
            "last_name",
        )
        self.fields["organizer"].queryset = User.objects.order_by(
            "first_name",
            "last_name",
        )
        self.fields["related_engagement"].queryset = (
            StakeholderEngagement.objects.order_by("-planned_date")
        )
        self.fields["related_assessment"].queryset = Assessment.objects.order_by(
            "-created_at"
        )
        self.fields["parent_event"].queryset = Event.objects.order_by(
            "-start_date",
            "-start_time",
        )
        numeric_fields = [
            "duration_hours",
            "expected_participants",
            "actual_participants",
            "budget_allocated",
            "actual_cost",
        ]
        for field_name in numeric_fields:
            field = self.fields.get(field_name)
            if field and isinstance(field.widget, forms.NumberInput):
                field.widget.attrs.setdefault("min", "0")
                if field_name == "duration_hours":
                    field.widget.attrs.setdefault("step", "0.25")


class EventQuickUpdateForm(forms.ModelForm):
    """Streamlined update form rendered inside calendar modal."""

    class Meta:
        model = Event
        fields = [
            "title",
            "status",
            "priority",
            "start_date",
            "start_time",
            "end_date",
            "end_time",
            "duration_hours",
            "venue",
            "address",
            "is_virtual",
            "virtual_platform",
            "virtual_link",
            "follow_up_required",
            "follow_up_date",
            "follow_up_notes",
            "description",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "address": forms.Textarea(attrs={"rows": 3}),
            "follow_up_notes": forms.Textarea(attrs={"rows": 3}),
            "start_date": DATE_WIDGET,
            "end_date": DATE_WIDGET,
            "follow_up_date": DATE_WIDGET,
            "start_time": TIME_WIDGET,
            "end_time": TIME_WIDGET,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_field_styles(self.fields)
        numeric_fields = ["duration_hours"]
        for field_name in numeric_fields:
            field = self.fields.get(field_name)
            if field and isinstance(field.widget, forms.NumberInput):
                field.widget.attrs.setdefault("min", "0")
                field.widget.attrs.setdefault("step", "0.25")


class StakeholderEngagementForm(forms.ModelForm):
    """Frontend form for logging coordination activities."""

    class Meta:
        model = StakeholderEngagement
        fields = [
            "title",
            "engagement_type",
            "description",
            "objectives",
            "community",
            "related_assessment",
            "status",
            "priority",
            "participation_level",
            "planned_date",
            "duration_minutes",
            "venue",
            "address",
            "target_participants",
            "actual_participants",
            "stakeholder_groups",
            "methodology",
            "materials_needed",
            "budget_allocated",
            "actual_cost",
            "key_outcomes",
            "feedback_summary",
            "action_items",
            "satisfaction_rating",
            "meeting_minutes",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "objectives": forms.Textarea(attrs={"rows": 3}),
            "stakeholder_groups": forms.Textarea(attrs={"rows": 3}),
            "methodology": forms.Textarea(attrs={"rows": 3}),
            "materials_needed": forms.Textarea(attrs={"rows": 3}),
            "key_outcomes": forms.Textarea(attrs={"rows": 3}),
            "feedback_summary": forms.Textarea(attrs={"rows": 3}),
            "action_items": forms.Textarea(attrs={"rows": 3}),
            "meeting_minutes": forms.Textarea(attrs={"rows": 4}),
            "address": forms.Textarea(attrs={"rows": 3}),
            "planned_date": DATETIME_WIDGET,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_field_styles(self.fields)
        self.fields["community"].queryset = OBCCommunity.objects.order_by("name")
        self.fields["related_assessment"].queryset = Assessment.objects.order_by(
            "-created_at"
        )
        numeric_fields = [
            "target_participants",
            "actual_participants",
            "duration_minutes",
        ]
        for field_name in numeric_fields:
            field = self.fields.get(field_name)
            if field and isinstance(field.widget, forms.NumberInput):
                field.widget.attrs.setdefault("min", "0")
        if "duration_minutes" in self.fields:
            self.fields["duration_minutes"].widget.attrs.setdefault("step", "15")


class RecurringEventPatternForm(forms.ModelForm):
    """Form for creating and editing recurring event patterns (RFC 5545 compliant)."""

    class Meta:
        model = RecurringEventPattern
        fields = [
            "recurrence_type",
            "interval",
            "by_weekday",
            "by_monthday",
            "by_setpos",
            "count",
            "until_date",
            "exception_dates",
        ]
        widgets = {
            "until_date": DATE_WIDGET,
            "by_weekday": forms.CheckboxSelectMultiple,
        }
        help_texts = {
            "recurrence_type": "How often should this event repeat?",
            "interval": "Repeat every X days/weeks/months/years (e.g., '2' for every 2 weeks)",
            "by_weekday": "For weekly recurrence, select which days of the week",
            "by_monthday": "For monthly recurrence, specify day of month (1-31)",
            "by_setpos": "Relative position (1=first, -1=last)",
            "count": "Number of occurrences (leave empty for until_date or forever)",
            "until_date": "End date for recurrence (leave empty if using count)",
            "exception_dates": "Dates to exclude from recurrence",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_field_styles(self.fields)

        # Make interval default to 1
        if not self.instance.pk:
            self.fields["interval"].initial = 1

        # Set min value for interval
        if "interval" in self.fields and isinstance(
            self.fields["interval"].widget, forms.NumberInput
        ):
            self.fields["interval"].widget.attrs.setdefault("min", "1")

    def clean(self):
        cleaned_data = super().clean()
        recurrence_type = cleaned_data.get("recurrence_type")
        by_weekday = cleaned_data.get("by_weekday")
        by_monthday = cleaned_data.get("by_monthday")
        count = cleaned_data.get("count")
        until_date = cleaned_data.get("until_date")

        # Validate that weekly recurrence has weekdays selected
        if (
            recurrence_type == RecurringEventPattern.RECURRENCE_WEEKLY
            and not by_weekday
        ):
            self.add_error(
                "by_weekday",
                "Please select at least one day of the week for weekly recurrence.",
            )

        # Validate that monthly recurrence has monthday if not using weekday
        if (
            recurrence_type == RecurringEventPattern.RECURRENCE_MONTHLY
            and not by_monthday
            and not by_weekday
        ):
            self.add_error(
                "by_monthday",
                "Please specify a day of the month for monthly recurrence.",
            )

        # Validate that either count or until_date is provided, but not both
        if count and until_date:
            self.add_error(
                "count",
                "Please specify either a count or an end date, not both.",
            )
            self.add_error(
                "until_date",
                "Please specify either a count or an end date, not both.",
            )

        return cleaned_data
