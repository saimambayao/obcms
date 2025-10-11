"""Forms for coordination module frontend interactions."""

import json

from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.forms import BaseInlineFormSet, inlineformset_factory

from communities.models import OBCCommunity
from mana.models import Assessment

from common.models import (
    Barangay,
    Municipality,
    Province,
    Region,
    RecurringEventPattern,
)
from common.work_item_model import WorkItem

from .models import (
    CoordinationNote,
    Organization,
    OrganizationContact,
    Partnership,
    PartnershipDocument,
    PartnershipMilestone,
    PartnershipSignatory,
    StakeholderEngagement,
)

# DEPRECATED: Event model removed - replaced by WorkItem
# See: docs/refactor/WORKITEM_MIGRATION_COMPLETE.md

INPUT_CLASS = (
    "block w-full px-4 py-3 text-base rounded-xl border border-gray-200 bg-white "
    "shadow-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 "
    "focus:border-emerald-500 min-h-[48px] transition-all duration-200"
)
TEXTAREA_CLASS = (
    "block w-full px-4 py-3 text-base rounded-xl border border-gray-200 bg-white "
    "shadow-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 "
    "focus:border-emerald-500 transition-all duration-200"
)
CHECKBOX_CLASS = (
    "h-4 w-4 text-emerald-600 border-gray-300 rounded focus:ring-emerald-500"
)

DATE_WIDGET = forms.DateInput(attrs={"type": "date", "class": INPUT_CLASS})
TIME_WIDGET = forms.TimeInput(attrs={"type": "time", "class": INPUT_CLASS})
DATETIME_WIDGET = forms.DateTimeInput(
    attrs={"type": "datetime-local", "class": INPUT_CLASS}
)

MULTISELECT_CLASS = (
    "block w-full px-4 py-3 text-base rounded-xl border border-gray-200 bg-white "
    "shadow-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 "
    "focus:border-emerald-500 min-h-[48px] transition-all duration-200"
)

User = get_user_model()

COORDINATION_INPUT_CLASS = (
    "block w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm "
    "focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] bg-white transition-all duration-200"
)
COORDINATION_TEXTAREA_CLASS = (
    "block w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm "
    "focus:ring-emerald-500 focus:border-emerald-500 bg-white transition-all duration-200 min-h-[120px]"
)
COORDINATION_MULTISELECT_CLASS = (
    "block w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm "
    "focus:ring-emerald-500 focus:border-emerald-500 bg-white transition-all duration-200 min-h-[200px]"
)
COORDINATION_SELECT_CLASS = (
    "block w-full px-4 py-3 text-base rounded-xl border border-gray-200 shadow-sm "
    "focus:ring-emerald-500 focus:border-emerald-500 min-h-[48px] appearance-none bg-white transition-all duration-200"
)


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

    region = forms.ModelChoiceField(
        queryset=Region.objects.filter(is_active=True).order_by("code", "name"),
        required=False,
        widget=forms.Select(attrs={"class": COORDINATION_SELECT_CLASS}),
        empty_label="Select region",
        label="Region",
    )
    province = forms.ModelChoiceField(
        queryset=Province.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": COORDINATION_SELECT_CLASS}),
        empty_label="Select province",
        label="Province",
    )
    municipality = forms.ModelChoiceField(
        queryset=Municipality.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": COORDINATION_SELECT_CLASS}),
        empty_label="Select municipality / city",
        label="Municipality / City",
    )
    barangay = forms.ModelChoiceField(
        queryset=Barangay.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": COORDINATION_SELECT_CLASS}),
        empty_label="Select barangay",
        label="Barangay",
    )

    social_media = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "facebook: https://facebook.com/OOBC\nx: https://x.com/OOBC",
            }
        ),
        help_text=(
            "Enter one platform per line using 'platform: url' (e.g., "
            "facebook: https://facebook.com/OOBC). JSON dictionaries are also accepted."
        ),
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_field_styles(self.fields)
        self._initialise_location_querysets()
        self._initialise_social_media()

    def _initialise_location_querysets(self):
        """Limit location dropdowns based on current selections."""
        region_field = self.fields["region"]
        region_field.queryset = Region.objects.filter(is_active=True).order_by(
            "code", "name"
        )

        selected_region_id = self._extract_id_from_data(
            "region", getattr(self.instance, "region_id", None)
        )
        province_qs = (
            Province.objects.filter(is_active=True)
            .select_related("region")
            .order_by("region__name", "name")
        )
        if selected_region_id:
            province_qs = province_qs.filter(region_id=selected_region_id)
        self.fields["province"].queryset = province_qs

        selected_province_id = self._extract_id_from_data(
            "province",
            getattr(self.instance, "province_id", None),
        )
        municipality_qs = (
            Municipality.objects.filter(is_active=True)
            .select_related("province__region")
            .order_by("province__name", "name")
        )
        if selected_province_id:
            municipality_qs = municipality_qs.filter(province_id=selected_province_id)
        elif selected_region_id:
            municipality_qs = municipality_qs.filter(
                province__region_id=selected_region_id
            )
        self.fields["municipality"].queryset = municipality_qs

        selected_municipality_id = self._extract_id_from_data(
            "municipality",
            getattr(self.instance, "municipality_id", None),
        )
        barangay_qs = (
            Barangay.objects.filter(is_active=True)
            .select_related("municipality__province__region")
            .order_by("municipality__name", "name")
        )
        if selected_municipality_id:
            barangay_qs = barangay_qs.filter(municipality_id=selected_municipality_id)
        elif selected_province_id:
            barangay_qs = barangay_qs.filter(
                municipality__province_id=selected_province_id
            )
        self.fields["barangay"].queryset = barangay_qs

    def _initialise_social_media(self):
        """Prepare social media field for editing."""
        if not self.instance or not self.instance.social_media:
            return
        existing = self.instance.social_media
        if isinstance(existing, dict):
            formatted_entries = [
                f"{platform}: {url}" for platform, url in existing.items() if url
            ]
            if formatted_entries:
                self.initial.setdefault("social_media", "\n".join(formatted_entries))
        else:
            self.initial.setdefault("social_media", json.dumps(existing, indent=2))

    def _extract_id_from_data(self, field_name, fallback):
        """Return an identifier from POST data or fallback instance value."""
        if self.data and field_name in self.data:
            value = self.data.get(field_name)
            if value in (None, "", "None"):
                return None
            return value
        return fallback

    def clean_social_media(self):
        social_media = self.cleaned_data.get("social_media")
        if not social_media:
            return None

        if isinstance(social_media, str):
            stripped = social_media.strip()
            if not stripped:
                return None

            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError:
                parsed = {}
                for line in stripped.splitlines():
                    if not line.strip():
                        continue
                    if ":" in line:
                        platform, url = line.split(":", 1)
                    elif "|" in line:
                        platform, url = line.split("|", 1)
                    else:
                        raise forms.ValidationError(
                            "Use 'platform: url' format for each social media entry."
                        )
                    platform = platform.strip().lower().replace(" ", "_")
                    url = url.strip()
                    if not platform or not url:
                        raise forms.ValidationError(
                            "Each social media entry must include both platform and URL."
                        )
                    parsed[platform] = url
            if isinstance(parsed, dict):
                return {key: value for key, value in parsed.items() if value}
            raise forms.ValidationError(
                "Enter a JSON object or use 'platform: url' per line."
            )

        if isinstance(social_media, dict):
            return {key: value for key, value in social_media.items() if value}

        raise forms.ValidationError(
            "Unsupported format for social media entries. Provide a JSON object or plain text list."
        )

    def clean(self):
        cleaned_data = super().clean()
        region = cleaned_data.get("region")
        province = cleaned_data.get("province")
        municipality = cleaned_data.get("municipality")
        barangay = cleaned_data.get("barangay")

        if barangay:
            barangay_municipality = barangay.municipality
            if municipality and municipality != barangay_municipality:
                self.add_error(
                    "barangay",
                    "Selected barangay does not belong to the chosen municipality.",
                )
            else:
                cleaned_data["municipality"] = barangay_municipality
                cleaned_data["province"] = barangay_municipality.province
                cleaned_data["region"] = barangay_municipality.province.region

        municipality = cleaned_data.get("municipality")
        if municipality:
            municipality_province = municipality.province
            if province and province != municipality_province:
                self.add_error(
                    "municipality",
                    "Selected municipality does not belong to the chosen province.",
                )
            else:
                cleaned_data["province"] = municipality_province
                cleaned_data["region"] = municipality_province.region

        province = cleaned_data.get("province")
        if province:
            province_region = province.region
            if region and region != province_region:
                self.add_error(
                    "province",
                    "Selected province does not belong to the chosen region.",
                )
            else:
                cleaned_data["region"] = province_region

        return cleaned_data


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
    coverage_region = forms.ModelChoiceField(
        queryset=Region.objects.filter(is_active=True).order_by("code", "name"),
        required=False,
        label="Region",
    )
    coverage_province = forms.ModelChoiceField(
        queryset=Province.objects.filter(is_active=True)
        .select_related("region")
        .order_by("region__name", "name"),
        required=False,
        label="Province",
    )
    coverage_municipality = forms.ModelChoiceField(
        queryset=Municipality.objects.filter(is_active=True)
        .select_related("province__region")
        .order_by("province__name", "name"),
        required=False,
        label="Municipality / City",
    )
    coverage_barangay = forms.ModelChoiceField(
        queryset=Barangay.objects.filter(is_active=True)
        .select_related("municipality__province__region")
        .order_by("municipality__name", "name"),
        required=False,
        label="Barangay",
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


class CoordinationNoteForm(forms.ModelForm):
    """Minutes capture form linked to WorkItem coordination activities."""

    work_item = forms.ModelChoiceField(
        queryset=WorkItem.objects.none(),
        label="Linked Coordination Activity",
        widget=forms.Select(
            attrs={
                "class": COORDINATION_SELECT_CLASS,
                "data-placeholder": "Select coordination activity...",
            }
        ),
        help_text="Only activities scheduled on the selected date are shown.",
    )
    note_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": COORDINATION_INPUT_CLASS,
            }
        ),
        help_text="Choose the date of the coordination activity.",
    )
    note_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(
            attrs={
                "type": "time",
                "class": COORDINATION_INPUT_CLASS,
            }
        ),
        help_text="Optional start time for reference.",
    )
    staff_participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True).order_by(
            "first_name", "last_name"
        ),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                "class": COORDINATION_MULTISELECT_CLASS,
            }
        ),
        help_text="OOBC staff present or contributing.",
    )
    partner_organizations = forms.ModelMultipleChoiceField(
        queryset=Organization.objects.filter(is_active=True).order_by("name"),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                "class": COORDINATION_MULTISELECT_CLASS,
            }
        ),
        help_text="Partner organizations present.",
    )
    partnership_agreements = forms.ModelMultipleChoiceField(
        queryset=Partnership.objects.select_related("lead_organization").order_by(
            "title"
        ),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                "class": COORDINATION_MULTISELECT_CLASS,
            }
        ),
        help_text="Link relevant partnership agreements discussed.",
    )
    coverage_region = forms.ModelChoiceField(
        queryset=Region.objects.filter(is_active=True).order_by("code", "name"),
        required=False,
        widget=forms.Select(
            attrs={
                "class": COORDINATION_SELECT_CLASS,
                "data-placeholder": "Select region...",
            }
        ),
    )
    coverage_province = forms.ModelChoiceField(
        queryset=Province.objects.filter(is_active=True)
        .select_related("region")
        .order_by("region__name", "name"),
        required=False,
        widget=forms.Select(
            attrs={
                "class": COORDINATION_SELECT_CLASS,
                "data-placeholder": "Select province...",
            }
        ),
    )
    coverage_municipality = forms.ModelChoiceField(
        queryset=Municipality.objects.filter(is_active=True)
        .select_related("province__region")
        .order_by("province__name", "name"),
        required=False,
        widget=forms.Select(
            attrs={
                "class": COORDINATION_SELECT_CLASS,
                "data-placeholder": "Select municipality / city...",
            }
        ),
    )
    coverage_barangay = forms.ModelChoiceField(
        queryset=Barangay.objects.filter(is_active=True)
        .select_related("municipality__province__region")
        .order_by("municipality__name", "name"),
        required=False,
        widget=forms.Select(
            attrs={
                "class": COORDINATION_SELECT_CLASS,
                "data-placeholder": "Select barangay...",
            }
        ),
    )
    coverage_map_data = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={"data-coverage-map-state": "true"}),
    )

    class Meta:
        model = CoordinationNote
        fields = [
            "title",
            "note_date",
            "note_time",
            "work_item",
            "location_description",
            "meeting_overview",
            "key_agenda",
            "discussion_highlights",
            "decisions",
            "action_items",
            "follow_up_items",
            "partnership_details",
            "attachments_links",
            "additional_notes",
            "staff_participants",
            "partner_organizations",
            "partnership_agreements",
            "coverage_region",
            "coverage_province",
            "coverage_municipality",
            "coverage_barangay",
            "coverage_map_data",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": COORDINATION_INPUT_CLASS,
                    "placeholder": "e.g., Minutes: Provincial Coordination Meeting",
                }
            ),
            "location_description": forms.TextInput(
                attrs={
                    "class": COORDINATION_INPUT_CLASS,
                    "placeholder": "Venue or platform (Zoom, Municipal Hall, etc.)",
                }
            ),
            "meeting_overview": forms.Textarea(
                attrs={
                    "class": COORDINATION_TEXTAREA_CLASS,
                    "rows": 3,
                    "placeholder": "Summarize the activity objectives and context...",
                }
            ),
            "key_agenda": forms.Textarea(
                attrs={
                    "class": COORDINATION_TEXTAREA_CLASS,
                    "rows": 3,
                    "placeholder": "List agenda items or talking points...",
                }
            ),
            "discussion_highlights": forms.Textarea(
                attrs={
                    "class": COORDINATION_TEXTAREA_CLASS,
                    "rows": 4,
                    "placeholder": "Capture main discussion highlights...",
                }
            ),
            "decisions": forms.Textarea(
                attrs={
                    "class": COORDINATION_TEXTAREA_CLASS,
                    "rows": 3,
                    "placeholder": "Document decisions and agreements...",
                }
            ),
            "action_items": forms.Textarea(
                attrs={
                    "class": COORDINATION_TEXTAREA_CLASS,
                    "rows": 4,
                    "placeholder": "List action items, responsible leads, and due dates...",
                }
            ),
            "follow_up_items": forms.Textarea(
                attrs={
                    "class": COORDINATION_TEXTAREA_CLASS,
                    "rows": 3,
                    "placeholder": "Capture follow-up needs, support requests, or upcoming deadlines...",
                }
            ),
            "partnership_details": forms.Textarea(
                attrs={
                    "class": COORDINATION_TEXTAREA_CLASS,
                    "rows": 3,
                    "placeholder": "Log partnership coordination notes, commitments, or risk flags...",
                }
            ),
            "attachments_links": forms.Textarea(
                attrs={
                    "class": COORDINATION_TEXTAREA_CLASS,
                    "rows": 2,
                    "placeholder": "Add shared folders, document links, or references...",
                }
            ),
            "additional_notes": forms.Textarea(
                attrs={
                    "class": COORDINATION_TEXTAREA_CLASS,
                    "rows": 3,
                    "placeholder": "Other remarks or reminders...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Prefilter work items using selected date if provided
        work_item_qs = WorkItem.objects.filter(
            work_type=WorkItem.WORK_TYPE_ACTIVITY
        ).order_by("start_date", "title")

        date_source = self.data.get("note_date") or self.initial.get("note_date")
        if date_source:
            try:
                parsed_date = forms.DateField().to_python(date_source)
            except (TypeError, ValueError):
                parsed_date = None
            if parsed_date:
                work_item_qs = work_item_qs.filter(
                    Q(start_date=parsed_date) | Q(due_date=parsed_date)
                )

        self.fields["work_item"].queryset = work_item_qs
        self.fields["staff_participants"].widget.attrs.setdefault(
            "data-searchable", "true"
        )
        self.fields["partner_organizations"].widget.attrs.setdefault(
            "data-searchable", "true"
        )
        self.fields["partnership_agreements"].widget.attrs.setdefault(
            "data-searchable", "true"
        )

    def clean_work_item(self):
        work_item = self.cleaned_data.get("work_item")
        if work_item and work_item.work_type != WorkItem.WORK_TYPE_ACTIVITY:
            raise forms.ValidationError(
                "Coordination notes can only be linked to coordination activities."
            )
        return work_item

    def clean_coverage_map_data(self):
        raw = self.cleaned_data.get("coverage_map_data")
        if not raw:
            return {}
        try:
            payload = json.loads(raw)
        except (TypeError, ValueError):
            raise forms.ValidationError("Invalid map data payload.")
        if not isinstance(payload, dict):
            raise forms.ValidationError("Coverage map data must be a JSON object.")
        return payload

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        work_item_qs = WorkItem.objects.filter(
            work_type=WorkItem.WORK_TYPE_ACTIVITY
        ).order_by("start_date", "title")

        date_source = self.data.get("note_date") or self.initial.get("note_date")
        if date_source:
            try:
                parsed_date = forms.DateField().to_python(date_source)
            except (TypeError, ValueError):
                parsed_date = None
            if parsed_date:
                work_item_qs = work_item_qs.filter(
                    Q(start_date=parsed_date) | Q(due_date=parsed_date)
                )

        self.fields["work_item"].queryset = work_item_qs
        self.fields["staff_participants"].widget.attrs.setdefault(
            "data-searchable", "true"
        )
        self.fields["partner_organizations"].widget.attrs.setdefault(
            "data-searchable", "true"
        )
        self.fields["partnership_agreements"].widget.attrs.setdefault(
            "data-searchable", "true"
        )


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


class EventForm(forms.Form):
    """
    DEPRECATED: Event model is now abstract. Use WorkItemForm instead.

    This form is kept ONLY to prevent import errors but CANNOT be used.
    All new code should use WorkItemForm from common.forms.work_items.

    See: WORKITEM_MIGRATION_COMPLETE.md
    """

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "EventForm is deprecated because Event model is abstract. "
            "Use WorkItemForm with work_type='activity' instead. "
            "See: docs/refactor/WORKITEM_MIGRATION_COMPLETE.md"
        )

        # Legacy Meta class preserved for reference only
        # class Meta:
        #     model = Event
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
            "is_project_activity",
            "related_project",
            "project_activity_type",
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


class EventQuickUpdateForm(forms.Form):
    """
    DEPRECATED: Event model is now abstract. Use WorkItemForm instead.

    This form is kept ONLY to prevent import errors but CANNOT be used.
    All new code should use WorkItemForm from common.forms.work_items.

    See: WORKITEM_MIGRATION_COMPLETE.md
    """

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "EventQuickUpdateForm is deprecated because Event model is abstract. "
            "Use WorkItemForm with work_type='activity' instead. "
            "See: docs/refactor/WORKITEM_MIGRATION_COMPLETE.md"
        )

    # Legacy Meta preserved for reference only
    # class Meta:
    #     model = Event
    #     fields = ["title", "status", "priority", ...]
    #     widgets = {...}


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
