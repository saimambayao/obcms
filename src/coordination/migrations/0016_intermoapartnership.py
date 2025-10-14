# Generated manually for InterMOAPartnership model
import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [
        ("coordination", "0015_organization_barangay_organization_municipality_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="InterMOAPartnership",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text="Title of the inter-MOA partnership",
                        max_length=255,
                    ),
                ),
                (
                    "partnership_type",
                    models.CharField(
                        choices=[
                            ("bilateral", "Bilateral Partnership (2 MOAs)"),
                            ("multilateral", "Multilateral Partnership (3+ MOAs)"),
                            ("joint_program", "Joint Program Implementation"),
                            ("resource_sharing", "Resource Sharing Agreement"),
                            ("capacity_building", "Capacity Building Initiative"),
                            ("policy_coordination", "Policy Coordination"),
                            ("service_delivery", "Joint Service Delivery"),
                            ("other", "Other"),
                        ],
                        help_text="Type of partnership between MOAs",
                        max_length=30,
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        help_text="Detailed description of the partnership objectives and scope"
                    ),
                ),
                (
                    "objectives",
                    models.TextField(
                        help_text="Specific objectives and goals of this partnership"
                    ),
                ),
                (
                    "lead_moa_code",
                    models.CharField(
                        help_text="Code of the lead MOA (e.g., 'OOBC', 'MOH', 'MAFAR')",
                        max_length=20,
                    ),
                ),
                (
                    "participating_moa_codes",
                    models.JSONField(
                        default=list,
                        help_text="List of participating MOA codes (e.g., ['MOH', 'MOLE'])",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("pending_approval", "Pending Approval"),
                            ("active", "Active"),
                            ("on_hold", "On Hold"),
                            ("completed", "Completed"),
                            ("terminated", "Terminated"),
                        ],
                        default="draft",
                        help_text="Current status of the partnership",
                        max_length=20,
                    ),
                ),
                (
                    "priority",
                    models.CharField(
                        choices=[
                            ("low", "Low"),
                            ("medium", "Medium"),
                            ("high", "High"),
                            ("critical", "Critical"),
                        ],
                        default="medium",
                        help_text="Priority level of this partnership",
                        max_length=10,
                    ),
                ),
                (
                    "progress_percentage",
                    models.IntegerField(
                        default=0,
                        help_text="Overall progress (0-100%)",
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(100),
                        ],
                    ),
                ),
                (
                    "start_date",
                    models.DateField(
                        blank=True,
                        help_text="Partnership start date",
                        null=True,
                    ),
                ),
                (
                    "end_date",
                    models.DateField(
                        blank=True,
                        help_text="Partnership end date (if applicable)",
                        null=True,
                    ),
                ),
                (
                    "focal_person_name",
                    models.CharField(
                        blank=True,
                        help_text="Name of the focal person managing this partnership",
                        max_length=255,
                    ),
                ),
                (
                    "focal_person_email",
                    models.EmailField(
                        blank=True,
                        help_text="Email of the focal person",
                        max_length=254,
                    ),
                ),
                (
                    "focal_person_phone",
                    models.CharField(
                        blank=True,
                        help_text="Phone number of the focal person",
                        max_length=50,
                    ),
                ),
                (
                    "expected_outcomes",
                    models.TextField(
                        blank=True,
                        help_text="Expected outcomes and impact of the partnership",
                    ),
                ),
                (
                    "deliverables",
                    models.TextField(
                        blank=True,
                        help_text="Key deliverables and milestones",
                    ),
                ),
                (
                    "total_budget",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Total budget for the partnership (in PHP)",
                        max_digits=15,
                        null=True,
                    ),
                ),
                (
                    "resource_commitments",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="Resource commitments by each MOA (JSON: {moa_code: resources})",
                    ),
                ),
                (
                    "is_public",
                    models.BooleanField(
                        default=False,
                        help_text="Whether this partnership is publicly visible (for OCM oversight)",
                    ),
                ),
                (
                    "requires_ocm_approval",
                    models.BooleanField(
                        default=False,
                        help_text="Whether this partnership requires OCM (Office of the Chief Minister) approval",
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        blank=True,
                        help_text="Additional notes and observations",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        help_text="User who created this partnership",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="created_inter_moa_partnerships",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Inter-MOA Partnership",
                "verbose_name_plural": "Inter-MOA Partnerships",
            },
        ),
        migrations.AddIndex(
            model_name="intermoapartnership",
            index=models.Index(
                fields=["lead_moa_code", "status"],
                name="coordination_intermoapartnership_lead_status_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="intermoapartnership",
            index=models.Index(
                fields=["status", "priority"],
                name="coordination_intermoapartnership_status_priority_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="intermoapartnership",
            index=models.Index(
                fields=["start_date", "end_date"],
                name="coordination_intermoapartnership_dates_idx",
            ),
        ),
    ]
