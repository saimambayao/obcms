"""Forms for Monitoring & Evaluation operations."""

from django import forms

from common.forms.mixins import LocationSelectionMixin
from common.models import Barangay, Municipality, Province, Region
from communities.models import OBCCommunity

from .models import MonitoringEntry, MonitoringUpdate


class BaseMonitoringEntryForm(forms.ModelForm):
    """Base form helpers shared across entry quick-create forms."""

    class Meta:
        model = MonitoringEntry
        fields: list[str] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        queryset_fields = {
            "lead_organization",
            "supporting_organizations",
            "submitted_by_community",
            "communities",
            "submitted_to_organization",
            "implementing_moa",
            "coverage_region",
            "coverage_province",
            "coverage_municipality",
            "coverage_barangay",
        }

        goal_alignment_field = self.fields.get("goal_alignment")
        if goal_alignment_field:
            self.fields["goal_alignment"] = forms.CharField(
                required=False,
                help_text=goal_alignment_field.help_text,
            )

        for field_name in queryset_fields.intersection(self.fields.keys()):
            field = self.fields[field_name]
            field.queryset = field.queryset.order_by("name")

        tailwind_input = (
            "block w-full px-4 py-3 rounded-xl border border-neutral-200 "
            "bg-white shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 "
            "text-sm transition"
        )
        coverage_placeholders = {
            "coverage_region": "Select region...",
            "coverage_province": "Select province...",
            "coverage_municipality": "Select municipality / city...",
            "coverage_barangay": "Select barangay...",
        }

        for name, field in self.fields.items():
            widget = field.widget
            existing_classes = widget.attrs.get("class", "").strip()

            if isinstance(widget, forms.CheckboxInput):
                # Keep checkbox widgets lean so templates can apply custom styling
                widget.attrs["class"] = existing_classes
                widget.attrs.setdefault("data-component", "checkbox")
            else:
                widget.attrs["class"] = (
                    f"{existing_classes} {tailwind_input}".strip()
                )
                placeholder_source = field.help_text or field.label
                if placeholder_source and not isinstance(
                    widget, (forms.Select, forms.SelectMultiple)
                ):
                    widget.attrs.setdefault("placeholder", placeholder_source)
            widget_input_type = getattr(field.widget, "input_type", None)
            if widget_input_type == "select-multiple":
                field.widget.attrs.setdefault("size", 4)
            if name in coverage_placeholders:
                field.widget.attrs.setdefault(
                    "data-placeholder", coverage_placeholders[name]
                )
                initial_value = (
                    self.initial.get(name)
                    if name in self.initial
                    else (
                        getattr(self.instance, name + "_id", "")
                        if getattr(self.instance, "pk", None)
                        else ""
                    )
                )
                if isinstance(
                    initial_value, (Region, Province, Municipality, Barangay)
                ):
                    initial_value = initial_value.pk
                if initial_value:
                    field.widget.attrs.setdefault("data-initial", str(initial_value))

        goal_field = self.fields.get("goal_alignment")
        if goal_field:
            goal_field.widget.attrs.setdefault(
                "placeholder",
                "Comma-separated strategic tags (e.g., PDP 2023, SDG 1)",
            )
            goal_field.widget.attrs["class"] = goal_field.widget.attrs.get(
                "class",
                "",
            ).replace("block w-full", "block w-full")
            if getattr(self.instance, "pk", None) and not self.initial.get(
                "goal_alignment"
            ):
                existing = getattr(self.instance, "goal_alignment", []) or []
                if isinstance(existing, list):
                    self.initial["goal_alignment"] = ", ".join(existing)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance = self._apply_category_defaults(instance)
        if commit:
            instance.save()
            if hasattr(self, "save_m2m"):
                self.save_m2m()
            self._post_save(instance)
        return instance

    def clean(self):
        cleaned_data = super().clean()
        funding_source = cleaned_data.get("funding_source")
        funding_source_other = cleaned_data.get("funding_source_other")
        if (
            funding_source == MonitoringEntry.FUNDING_SOURCE_OTHERS
            and not funding_source_other
        ):
            self.add_error(
                "funding_source_other",
                "Specify the funding source when selecting Other Funding Sources.",
            )
        return cleaned_data

    def clean_goal_alignment(self):  # pragma: no cover - exercised via form processing
        field = self.cleaned_data.get("goal_alignment")
        if field in (None, ""):
            return []
        if isinstance(field, list):
            return [item for item in field if item]
        if isinstance(field, str):
            return [item.strip() for item in field.split(",") if item.strip()]
        return field

    def _apply_category_defaults(self, instance: MonitoringEntry) -> MonitoringEntry:
        """Allow subclasses to enforce category-specific defaults."""

        return instance

    def _post_save(
        self, instance: MonitoringEntry
    ) -> None:  # pragma: no cover - default no-op
        """Hook for subclasses to mutate m2m relations after save."""

        return None


class MonitoringMOAEntryForm(BaseMonitoringEntryForm):
    """Quick-create form for MOA PPAs accessible by OBCs."""

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        instance_exists = bool(getattr(self.instance, "pk", None))
        if instance_exists and getattr(self.user, "is_moa_staff", False):
            locked_fields = {
                "implementing_moa": {
                    "disabled": True,
                    "extra_classes": "cursor-not-allowed bg-gray-100 text-gray-600",
                    "attrs": {
                        "aria-disabled": "true",
                        "data-lock-reason": "moa-staff",
                    },
                },
                "title": {
                    "readonly": True,
                    "extra_classes": "cursor-not-allowed bg-gray-100 text-gray-600",
                    "attrs": {
                        "aria-readonly": "true",
                        "data-lock-reason": "moa-staff",
                    },
                },
            }

            for field_name, options in locked_fields.items():
                field = self.fields.get(field_name)
                if not field:
                    continue

                widget = field.widget
                if options.get("disabled"):
                    field.disabled = True
                if options.get("readonly"):
                    widget.attrs["readonly"] = True

                existing_class = widget.attrs.get("class", "").strip()
                if options.get("extra_classes"):
                    widget.attrs["class"] = (
                        f"{existing_class} {options['extra_classes']}".strip()
                    )

                for attr_name, attr_value in options.get("attrs", {}).items():
                    widget.attrs[attr_name] = attr_value

    class Meta(BaseMonitoringEntryForm.Meta):
        fields = [
            "implementing_moa",
            "title",
            "summary",
            "plan_year",
            "fiscal_year",
            "sector",
            "appropriation_class",
            "funding_source",
            "funding_source_other",
            "program_code",
            "plan_reference",
            "goal_alignment",
            "moral_governance_pillar",
            "compliance_gad",
            "compliance_ccet",
            "benefits_indigenous_peoples",
            "supports_peace_agenda",
            "supports_sdg",
            "budget_ceiling",
            "budget_allocation",
            "budget_obc_allocation",
            "total_slots",
            "obc_slots",
            "coverage_region",
            "coverage_province",
            "coverage_municipality",
            "coverage_barangay",
            "communities",
            "obcs_benefited",
            "status",
            "progress",
            "start_date",
            "target_end_date",
        ]
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 3}),
            "obcs_benefited": forms.Textarea(attrs={"rows": 3}),
            "goal_alignment": forms.TextInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        coverage_region = cleaned_data.get("coverage_region")
        coverage_province = cleaned_data.get("coverage_province")
        coverage_municipality = cleaned_data.get("coverage_municipality")
        coverage_barangay = cleaned_data.get("coverage_barangay")

        if not cleaned_data.get("implementing_moa"):
            self.add_error(
                "implementing_moa",
                "Select the implementing MOA for this PPA.",
            )
        if cleaned_data.get("progress") is None:
            cleaned_data["progress"] = 0

        if coverage_province and coverage_province.region_id != getattr(
            coverage_region, "id", None
        ):
            self.add_error(
                "coverage_province",
                "Selected province does not belong to the chosen region.",
            )
        if coverage_municipality and coverage_municipality.province_id != getattr(
            coverage_province, "id", None
        ):
            self.add_error(
                "coverage_municipality",
                "Municipality must belong to the selected province.",
            )
        if coverage_barangay and coverage_barangay.municipality_id != getattr(
            coverage_municipality, "id", None
        ):
            self.add_error(
                "coverage_barangay",
                "Barangay must belong to the selected municipality.",
            )
        return cleaned_data

    def _apply_category_defaults(self, instance: MonitoringEntry) -> MonitoringEntry:
        instance.category = "moa_ppa"
        instance.request_status = ""
        if instance.progress is None:
            instance.progress = 0
        return instance


class MonitoringOOBCEntryForm(BaseMonitoringEntryForm):
    """Quick-create form for OOBC-led initiatives."""

    class Meta(BaseMonitoringEntryForm.Meta):
        fields = [
            "title",
            "summary",
            "oobc_unit",
            "plan_year",
            "fiscal_year",
            "sector",
            "appropriation_class",
            "funding_source",
            "funding_source_other",
            "program_code",
            "plan_reference",
            "goal_alignment",
            "moral_governance_pillar",
            "compliance_gad",
            "compliance_ccet",
            "benefits_indigenous_peoples",
            "supports_peace_agenda",
            "supports_sdg",
            "budget_ceiling",
            "communities",
            "supporting_organizations",
            "status",
            "progress",
            "start_date",
            "target_end_date",
            "budget_allocation",
            "budget_currency",
        ]
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 3}),
            "goal_alignment": forms.TextInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("oobc_unit"):
            self.add_error(
                "oobc_unit",
                "Identify the OOBC unit responsible for this initiative.",
            )
        if cleaned_data.get("progress") is None:
            cleaned_data["progress"] = 0
        return cleaned_data

    def _apply_category_defaults(self, instance: MonitoringEntry) -> MonitoringEntry:
        instance.category = "oobc_ppa"
        instance.request_status = ""
        if instance.progress is None:
            instance.progress = 0
        return instance


class MonitoringRequestEntryForm(BaseMonitoringEntryForm):
    """Quick-create form for OBC requests and proposals."""

    class Meta(BaseMonitoringEntryForm.Meta):
        fields = [
            "title",
            "summary",
            "submitted_by_community",
            "submitted_to_organization",
            "lead_organization",
            "communities",
            "supporting_organizations",
            "priority",
            "support_required",
            "plan_year",
            "fiscal_year",
            "sector",
            "funding_source",
            "funding_source_other",
            "plan_reference",
            "goal_alignment",
            "moral_governance_pillar",
        ]
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 3}),
            "support_required": forms.Textarea(attrs={"rows": 3}),
            "goal_alignment": forms.TextInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("submitted_by_community"):
            self.add_error(
                "submitted_by_community",
                "Identify the requesting OBC community.",
            )
        if not cleaned_data.get("submitted_to_organization") and not cleaned_data.get(
            "lead_organization"
        ):
            self.add_error(
                "submitted_to_organization",
                "Provide the receiving OOBC unit or external MOA for the request.",
            )
        return cleaned_data

    def _apply_category_defaults(self, instance: MonitoringEntry) -> MonitoringEntry:
        instance.category = "obc_request"
        instance.status = "planning"
        instance.request_status = "submitted"
        instance.progress = 0
        return instance

    def _post_save(self, instance: MonitoringEntry) -> None:
        if (
            instance.submitted_by_community
            and not instance.communities.filter(
                pk=instance.submitted_by_community.pk
            ).exists()
        ):
            instance.communities.add(instance.submitted_by_community)


class MonitoringOBCQuickCreateForm(LocationSelectionMixin, forms.ModelForm):
    """Minimal form for inline creation of barangay-level OBC communities."""

    # Configure location fields - all levels including barangay
    location_fields_config = {
        "region": {"required": True, "level": "region", "zoom": 7},
        "province": {"required": True, "level": "province", "zoom": 9},
        "municipality": {"required": True, "level": "municipality", "zoom": 12},
        "barangay": {"required": True, "level": "barangay", "zoom": 15},
    }

    # Override default CSS classes for this form
    location_field_css_classes = "block w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition"

    region = forms.ModelChoiceField(
        queryset=Region.objects.filter(is_active=True).order_by("code", "name"),
        required=True,
        label="Region",
    )
    province = forms.ModelChoiceField(
        queryset=Province.objects.none(),
        required=True,
        label="Province",
    )
    municipality = forms.ModelChoiceField(
        queryset=Municipality.objects.none(),
        required=True,
        label="Municipality / City",
    )

    class Meta:
        model = OBCCommunity
        fields = [
            "barangay",
            "name",
            "community_names",
            "obc_id",
            "latitude",
            "longitude",
        ]
        labels = {
            "region": "Region",
            "province": "Province",
            "municipality": "Municipality / City",
            "barangay": "Barangay",
            "name": "OBC Name",
            "community_names": "Alternate Names (optional)",
            "obc_id": "OBC ID (optional)",
            "latitude": "Latitude",
            "longitude": "Longitude",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "block w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition",
                    "placeholder": "e.g., Purok Maharlika Muslim Community",
                }
            ),
            "community_names": forms.TextInput(
                attrs={
                    "class": "block w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition",
                    "placeholder": "Other known names (comma-separated)",
                }
            ),
            "obc_id": forms.TextInput(
                attrs={
                    "class": "block w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition",
                    "placeholder": "Registry identifier (optional)",
                }
            ),
            "latitude": forms.NumberInput(
                attrs={
                    "class": "block w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition",
                    "step": "any",
                    "placeholder": "Auto-filled latitude",
                    "data-placeholder": "Auto-filled latitude",
                }
            ),
            "longitude": forms.NumberInput(
                attrs={
                    "class": "block w-full px-4 py-3 rounded-xl border border-neutral-200 bg-white shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition",
                    "step": "any",
                    "placeholder": "Auto-filled longitude",
                    "data-placeholder": "Auto-filled longitude",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set field requirements
        name_field = self.fields.get("name")
        if name_field:
            name_field.required = True
        if self.fields.get("community_names"):
            self.fields["community_names"].required = False
        if self.fields.get("obc_id"):
            self.fields["obc_id"].required = False

        for coordinate_field in ("latitude", "longitude"):
            field = self.fields.get(coordinate_field)
            if field:
                field.required = False
                field.widget.attrs.setdefault("data-auto-filled", "true")

        # Add data-placeholder attributes to location fields
        location_placeholders = {
            "region": "Select region...",
            "province": "Select province...",
            "municipality": "Select municipality / city...",
            "barangay": "Select barangay...",
        }

        for field_name, placeholder in location_placeholders.items():
            field = self.fields.get(field_name)
            if field:
                field.widget.attrs.setdefault("data-placeholder", placeholder)


class MonitoringUpdateForm(forms.ModelForm):
    """Form for recording monitoring updates."""

    class Meta:
        model = MonitoringUpdate
        fields = [
            "update_type",
            "status",
            "request_status",
            "progress",
            "notes",
            "next_steps",
            "follow_up_date",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
            "next_steps": forms.Textarea(attrs={"rows": 3}),
            "follow_up_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        update_type = cleaned_data.get("update_type")

        if update_type == "status" and not cleaned_data.get("status"):
            self.add_error("status", "Provide the updated implementation status.")

        if update_type == "progress" and cleaned_data.get("progress") is None:
            self.add_error("progress", "Capture the new progress percentage.")

        if update_type == "milestone" and not cleaned_data.get("follow_up_date"):
            self.add_error(
                "follow_up_date", "Set the follow-up date for the milestone."
            )

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tailwind_input = (
            "block w-full px-4 py-3 text-sm rounded-xl border border-gray-200 "
            "bg-white shadow-sm transition-all duration-200 focus:ring-emerald-500 "
            "focus:border-emerald-500 min-h-[48px]"
        )
        def _set_empty_choice_label(django_field: forms.Field, label: str) -> None:
            if not getattr(django_field, "choices", None):
                return
            choices = list(django_field.choices)
            if choices and choices[0][0] == "":
                choices[0] = ("", label)
                django_field.choices = choices

        for name, field in self.fields.items():
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_classes} {tailwind_input}".strip()
            placeholder_source = field.help_text or field.label
            if placeholder_source and not isinstance(
                field.widget, (forms.Select, forms.SelectMultiple)
            ):
                field.widget.attrs.setdefault("placeholder", placeholder_source)
            widget_input_type = getattr(field.widget, "input_type", None)
            if widget_input_type == "select-multiple":
                field.widget.attrs.setdefault("size", 4)
            if name == "progress":
                field.widget.attrs.setdefault("min", 0)
                field.widget.attrs.setdefault("max", 100)
            if name == "status":
                _set_empty_choice_label(field, "Select status")
            if name == "request_status":
                _set_empty_choice_label(field, "Select request status")
