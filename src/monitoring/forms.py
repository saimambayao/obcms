"""Forms for Monitoring & Evaluation operations."""

from django import forms
from django.urls import reverse
from django.utils.html import format_html

from common.forms.mixins import LocationSelectionMixin
from common.models import Barangay, Municipality, Province, Region
from communities.models import OBCCommunity

from .models import MonitoringEntry, MonitoringUpdate


class OBCRequestFilterForm(forms.Form):
    """Filter controls for the OBC requests dashboard."""

    status = forms.ChoiceField(required=False)
    priority = forms.ChoiceField(required=False)
    source = forms.ChoiceField(required=False)
    organization = forms.ChoiceField(required=False)
    disaster = forms.ChoiceField(required=False)
    query = forms.CharField(required=False, label="Search")

    def __init__(
        self,
        *args,
        status_choices=(),
        priority_choices=(),
        source_choices=(),
        organization_choices=(),
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.fields["status"].choices = [("", "All statuses"), *status_choices]
        self.fields["priority"].choices = [("", "All priorities"), *priority_choices]
        self.fields["source"].choices = [("", "All channels"), *source_choices]
        self.fields["organization"].choices = [
            ("", "All organizations"),
            *organization_choices,
        ]
        self.fields["disaster"].choices = [
            ("", "All requests"),
            ("yes", "Disaster-related"),
            ("no", "Non-disaster"),
        ]

        self.fields["query"].widget = forms.TextInput(
            attrs={
                "type": "search",
                "placeholder": "Search by title, summary, or requester…",
                "class": "pl-10",
            }
        )


class BaseMonitoringEntryForm(LocationSelectionMixin, forms.ModelForm):
    """Base form helpers shared across entry quick-create forms."""

    location_field_names = {
        "region": "coverage_region",
        "province": "coverage_province",
        "municipality": "coverage_municipality",
        "barangay": "coverage_barangay",
    }

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

        if self.is_bound and hasattr(self, "data") and "progress" in self.data:
            # Normalise blank progress submissions to zero before validation
            bound_progress = self.data.get("progress")
            if isinstance(bound_progress, (list, tuple)):
                bound_progress = bound_progress[0] if bound_progress else ""
            if bound_progress is not None and str(bound_progress).strip() == "":
                mutable_data = self.data.copy()
                mutable_data["progress"] = "0"
                self.data = mutable_data

        goal_alignment_field = self.fields.get("goal_alignment")
        if goal_alignment_field:
            self.fields["goal_alignment"] = forms.CharField(
                required=False,
                help_text=goal_alignment_field.help_text,
            )

        progress_field = self.fields.get("progress")
        if progress_field:
            progress_field.required = False
            progress_field.initial = (
                progress_field.initial
                if progress_field.initial not in (None, "")
                else 0
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
                widget.attrs["class"] = f"{existing_classes} {tailwind_input}".strip()
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

        if not cleaned_data.get("implementing_moa"):
            self.add_error(
                "implementing_moa",
                "Select the implementing MOA for this PPA.",
            )
        if cleaned_data.get("progress") is None:
            cleaned_data["progress"] = 0
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

    beneficiary_numeric_fields = [
        ("beneficiary_children_0_9", "Children (0-9 years)"),
        ("beneficiary_adolescents_10_14", "Adolescents (10-14 years)"),
        ("beneficiary_youth_15_30", "Youth (15-30 years)"),
        ("beneficiary_adults_31_59", "Adults (31-59 years)"),
        ("beneficiary_seniors_60_plus", "Seniors (60+ years)"),
        ("beneficiary_women", "Women"),
        ("beneficiary_solo_parents", "Solo parents"),
        ("beneficiary_pwds", "Persons with disabilities"),
        ("beneficiary_farmers", "Farmers"),
        ("beneficiary_fisherfolk", "Fisherfolk"),
        ("beneficiary_unemployed", "Unemployed"),
        ("beneficiary_indigenous_peoples", "Indigenous Peoples"),
        ("beneficiary_idps", "Internally Displaced Persons"),
        ("beneficiary_migrants_transients", "Migrants / Transients"),
    ]

    class Meta(BaseMonitoringEntryForm.Meta):
        fields = [
            "title",
            "summary",
            "request_objectives",
            "request_source",
            "requester_name",
            "requester_position",
            "requester_affiliation",
            "requester_contact_number",
            "requester_alternate_contact_number",
            "requester_email",
            "submitted_by_community",
            "submitted_to_organization",
            "lead_organization",
            "communities",
            "supporting_organizations",
            "related_ppas",
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
            "coverage_region",
            "coverage_province",
            "coverage_municipality",
            "coverage_barangay",
            "beneficiary_organizations_total",
            "beneficiary_individuals_total",
            "beneficiary_description",
            "estimated_total_amount",
            "request_notes",
            "is_disaster_related",
        ]
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 3}),
            "support_required": forms.Textarea(attrs={"rows": 3}),
            "goal_alignment": forms.TextInput(),
            "beneficiary_description": forms.Textarea(attrs={"rows": 3}),
            "request_notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["request_objectives"] = forms.CharField(
            label="Objectives / Purposes",
            required=True,
            widget=forms.Textarea(attrs={"rows": 4}),
            help_text="List each objective or purpose on a separate line.",
        )

        request_source_field = self.fields.get("request_source")
        if request_source_field:
            request_source_field.required = False
            request_source_field.widget.attrs.setdefault(
                "placeholder", "Select request source..."
            )

        related_ppas_field = self.fields.get("related_ppas")
        if related_ppas_field:
            related_ppas_field.queryset = (
                MonitoringEntry.objects.filter(category__in=["moa_ppa", "oobc_ppa"])
                .order_by("title")
                .select_related("implementing_moa")
            )
            related_ppas_field.help_text = (
                "Link existing PPAs (MOA or OOBC) connected to this request."
            )

        # Prefill requester details based on the authenticated user
        if self.user and not self.initial.get("request_source"):
            user_type = getattr(self.user, "user_type", "")
            default_source = {
                "community_leader": MonitoringEntry.REQUEST_SOURCE_COMMUNITY_USER,
                "oobc_staff": MonitoringEntry.REQUEST_SOURCE_OOBC_STAFF,
                "oobc_executive": MonitoringEntry.REQUEST_SOURCE_OOBC_STAFF,
                "bmoa": MonitoringEntry.REQUEST_SOURCE_MOA_FOCAL,
                "cm_office": MonitoringEntry.REQUEST_SOURCE_MOA_FOCAL,
                "lgu": MonitoringEntry.REQUEST_SOURCE_LGU_FOCAL,
                "nga": MonitoringEntry.REQUEST_SOURCE_NGA_FOCAL,
            }.get(user_type)
            if default_source:
                self.initial.setdefault("request_source", default_source)

        if self.user:
            self.initial.setdefault("requester_name", self.user.get_full_name())
            self.initial.setdefault(
                "requester_position", getattr(self.user, "position", "")
            )
            self.initial.setdefault(
                "requester_affiliation", getattr(self.user, "organization", "")
            )
            self.initial.setdefault(
                "requester_contact_number", getattr(self.user, "contact_number", "")
            )
            self.initial.setdefault("requester_email", getattr(self.user, "email", ""))

        # Additional demographic fields for beneficiary disaggregation
        self.beneficiary_numeric_keys = [
            key for key, _ in self.beneficiary_numeric_fields
        ]
        for field_name, label in self.beneficiary_numeric_fields:
            self.fields[field_name] = forms.IntegerField(
                required=False,
                min_value=0,
                label=label,
                help_text="Enter 0 if not applicable.",
            )

        self.fields["beneficiary_ethnolinguistic_groups"] = forms.CharField(
            required=False,
            label="Ethnolinguistic groups",
            help_text="Comma-separated list of ethnolinguistic groups represented.",
        )
        self.fields["beneficiary_other_vulnerable"] = forms.CharField(
            required=False,
            label="Other vulnerable sectors",
            help_text="Specify other vulnerable sectors included in the beneficiaries.",
        )

        demographics = getattr(self.instance, "beneficiary_demographics", {}) or {}
        for key in self.beneficiary_numeric_keys:
            if key in demographics and self.initial.get(key) is None:
                self.initial[key] = demographics.get(key)
        if (
            demographics
            and self.initial.get("beneficiary_ethnolinguistic_groups") is None
        ):
            ethnos = demographics.get("ethnolinguistic_groups", [])
            if isinstance(ethnos, list):
                self.initial["beneficiary_ethnolinguistic_groups"] = ", ".join(ethnos)
            elif ethnos:
                self.initial["beneficiary_ethnolinguistic_groups"] = str(ethnos)
        if demographics and self.initial.get("beneficiary_other_vulnerable") is None:
            other = demographics.get("other_vulnerable_sectors", "")
            if other:
                self.initial["beneficiary_other_vulnerable"] = other

    def clean_request_objectives(self):
        value = self.cleaned_data.get("request_objectives")
        if not value:
            raise forms.ValidationError("Provide at least one objective or purpose.")
        if isinstance(value, list):
            return [item for item in value if item]

        objectives = []
        for line in str(value).splitlines():
            item = line.strip().lstrip("-•").strip()
            if item:
                objectives.append(item)
        if not objectives:
            raise forms.ValidationError("List at least one objective for the request.")
        return objectives

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

        primary_contact = (cleaned_data.get("requester_contact_number") or "").strip()
        alternate_contact = (
            cleaned_data.get("requester_alternate_contact_number") or ""
        ).strip()
        if (
            primary_contact
            and alternate_contact
            and primary_contact == alternate_contact
        ):
            self.add_error(
                "requester_alternate_contact_number",
                "Alternate contact number must be different from the primary number.",
            )

        title = cleaned_data.get("title", "")
        requester_name = (cleaned_data.get("requester_name") or "").strip()
        submitted_by = cleaned_data.get("submitted_by_community")
        submitted_to = cleaned_data.get("submitted_to_organization")
        related_ppas = cleaned_data.get("related_ppas")
        communities = cleaned_data.get("communities")

        if title and (submitted_by or requester_name) and submitted_to:
            duplicate_qs = MonitoringEntry.objects.filter(
                category="obc_request"
            ).filter(title__iexact=title.strip())
            if submitted_by:
                duplicate_qs = duplicate_qs.filter(submitted_by_community=submitted_by)
            if requester_name:
                duplicate_qs = duplicate_qs.filter(
                    requester_name__iexact=requester_name
                )
            duplicate_qs = duplicate_qs.filter(submitted_to_organization=submitted_to)
            if related_ppas:
                duplicate_qs = duplicate_qs.filter(related_ppas__in=list(related_ppas))
            if communities:
                duplicate_qs = duplicate_qs.filter(communities__in=list(communities))

            duplicate_qs = duplicate_qs.distinct()
            if duplicate_qs.exists():
                existing_entry = duplicate_qs.first()
                detail_url = reverse(
                    "monitoring:detail", kwargs={"pk": existing_entry.pk}
                )
                self.add_error(
                    None,
                    forms.ValidationError(
                        format_html(
                            'A similar request already exists. <a href="{}" class="text-emerald-600 underline">View previous submission</a>.',
                            detail_url,
                        )
                    ),
                )

        return cleaned_data

    def _build_beneficiary_demographics(self) -> dict:
        demographics: dict[str, object] = {}
        for key in self.beneficiary_numeric_keys:
            value = self.cleaned_data.get(key)
            if value is not None:
                demographics[key] = int(value)

        ethnos = self.cleaned_data.get("beneficiary_ethnolinguistic_groups")
        if ethnos:
            groups = [item.strip() for item in str(ethnos).split(",") if item.strip()]
            demographics["ethnolinguistic_groups"] = groups

        other_vulnerable = self.cleaned_data.get("beneficiary_other_vulnerable")
        if other_vulnerable:
            demographics["other_vulnerable_sectors"] = other_vulnerable.strip()

        return demographics

    def save(self, commit: bool = True):
        instance = super().save(commit=False)

        instance.request_source = self.cleaned_data.get("request_source", "")
        instance.requester_name = self.cleaned_data.get("requester_name", "")
        instance.requester_position = self.cleaned_data.get("requester_position", "")
        instance.requester_affiliation = self.cleaned_data.get(
            "requester_affiliation", ""
        )
        instance.requester_contact_number = self.cleaned_data.get(
            "requester_contact_number", ""
        )
        instance.requester_alternate_contact_number = self.cleaned_data.get(
            "requester_alternate_contact_number", ""
        )
        instance.requester_email = self.cleaned_data.get("requester_email", "")
        instance.request_objectives = self.cleaned_data.get("request_objectives", [])
        instance.beneficiary_organizations_total = self.cleaned_data.get(
            "beneficiary_organizations_total"
        )
        instance.beneficiary_individuals_total = self.cleaned_data.get(
            "beneficiary_individuals_total"
        )
        instance.beneficiary_description = self.cleaned_data.get(
            "beneficiary_description", ""
        )
        instance.beneficiary_demographics = self._build_beneficiary_demographics()
        instance.is_disaster_related = bool(
            self.cleaned_data.get("is_disaster_related")
        )
        instance.estimated_total_amount = self.cleaned_data.get(
            "estimated_total_amount"
        )
        instance.request_notes = self.cleaned_data.get("request_notes", "")

        if commit:
            instance.save()
            self.save_m2m()
            self._post_save(instance)
        return instance

    def _apply_category_defaults(self, instance: MonitoringEntry) -> MonitoringEntry:
        instance.category = "obc_request"
        instance.status = "planning"
        instance.request_status = "submitted"
        instance.progress = 0
        return instance

    def _post_save(self, instance: MonitoringEntry) -> None:
        related_ppas = self.cleaned_data.get("related_ppas")
        if related_ppas is not None:
            instance.related_ppas.set(related_ppas)

        if (
            instance.submitted_by_community
            and not instance.communities.filter(
                pk=instance.submitted_by_community.pk
            ).exists()
        ):
            instance.communities.add(instance.submitted_by_community)

        super()._post_save(instance)


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
