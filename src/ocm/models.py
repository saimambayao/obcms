"""
OCM Models

Defines OCMAccess model for managing Office of the Chief Minister access.
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class OCMAccessQuerySet(models.QuerySet):
    """Custom QuerySet for OCMAccess"""

    def active(self):
        """Return only active OCM access records"""
        return self.filter(is_active=True)

    def inactive(self):
        """Return only inactive OCM access records"""
        return self.filter(is_active=False)

    def by_level(self, level):
        """Filter by access level"""
        return self.filter(access_level=level)

    def viewers(self):
        """Return viewer level access"""
        return self.by_level('viewer')

    def analysts(self):
        """Return analyst level access"""
        return self.by_level('analyst')

    def executives(self):
        """Return executive level access"""
        return self.by_level('executive')


class OCMAccessManager(models.Manager):
    """Custom Manager for OCMAccess"""

    def get_queryset(self):
        """Return custom QuerySet"""
        return OCMAccessQuerySet(self.model, using=self._db)

    def active(self):
        """Return only active OCM access"""
        return self.get_queryset().active()

    def inactive(self):
        """Return only inactive OCM access"""
        return self.get_queryset().inactive()

    def by_level(self, level):
        """Filter by access level"""
        return self.get_queryset().by_level(level)


class OCMAccess(models.Model):
    """
    Model for managing OCM (Office of the Chief Minister) access.

    Provides read-only consolidated views across all MOAs for government oversight.
    """

    ACCESS_LEVELS = [
        ('viewer', 'Viewer'),
        ('analyst', 'Analyst'),
        ('executive', 'Executive'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ocm_access',
        verbose_name='User',
        help_text='User with OCM access'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Active',
        help_text='Whether OCM access is currently active'
    )

    access_level = models.CharField(
        max_length=50,
        choices=ACCESS_LEVELS,
        default='viewer',
        verbose_name='Access Level',
        help_text='Level of access: viewer (dashboard only), analyst (+ reports), executive (+ exports)'
    )

    granted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Granted At',
        help_text='When OCM access was granted'
    )

    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ocm_grants',
        verbose_name='Granted By',
        help_text='User who granted this access'
    )

    last_accessed = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Last Accessed',
        help_text='Last time user accessed OCM views'
    )

    notes = models.TextField(
        blank=True,
        verbose_name='Notes',
        help_text='Internal notes about this OCM access grant'
    )

    objects = OCMAccessManager()

    class Meta:
        verbose_name = 'OCM Access'
        verbose_name_plural = 'OCM Access'
        ordering = ['-granted_at']
        permissions = [
            ('view_ocm_dashboard', 'Can view OCM dashboard'),
            ('view_consolidated_budget', 'Can view consolidated budget'),
            ('view_planning_overview', 'Can view planning overview'),
            ('view_coordination_matrix', 'Can view coordination matrix'),
            ('generate_ocm_reports', 'Can generate OCM reports'),
            ('export_ocm_data', 'Can export OCM data'),
        ]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_access_level_display()}"

    def clean(self):
        """Validate OCM access"""
        super().clean()

        # Prevent MOA staff from getting OCM access
        if hasattr(self.user, 'organization') and self.user.organization:
            if self.user.organization.code.upper() not in ['OOBC', 'OCM']:
                raise ValidationError({
                    'user': 'MOA staff cannot have OCM access. OCM access is only for OOBC/OCM personnel.'
                })

    def save(self, *args, **kwargs):
        """Override save to run validation"""
        self.full_clean()
        super().save(*args, **kwargs)

    # Helper properties for access level checks

    @property
    def is_viewer(self):
        """Check if user has viewer level access"""
        return self.access_level == 'viewer'

    @property
    def is_analyst(self):
        """Check if user has analyst level access"""
        return self.access_level in ['analyst', 'executive']

    @property
    def is_executive(self):
        """Check if user has executive level access"""
        return self.access_level == 'executive'

    @property
    def can_generate_reports(self):
        """Check if user can generate reports"""
        return self.is_analyst

    @property
    def can_export_data(self):
        """Check if user can export data"""
        return self.is_executive

    # Helper methods

    def update_last_accessed(self):
        """Update last accessed timestamp"""
        self.last_accessed = timezone.now()
        self.save(update_fields=['last_accessed'])
