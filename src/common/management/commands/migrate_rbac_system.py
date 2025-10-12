"""
Management command to migrate and populate RBAC system.

This command:
1. Creates Features from navbar menu structure
2. Creates standard Permissions (view, create, edit, delete) for each feature
3. Creates initial Roles (OOBC Admin, Manager, Staff, Viewer, etc.)
4. Assigns existing user permissions to the new RBAC system

Usage:
    python manage.py migrate_rbac_system --create-features
    python manage.py migrate_rbac_system --create-roles
    python manage.py migrate_rbac_system --assign-users
    python manage.py migrate_rbac_system --all  # Run all steps

References:
- docs/improvements/NAVBAR_RBAC_ANALYSIS.md
- src/common/rbac_models.py
- src/common/services/rbac_service.py
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify
from django.contrib.auth import get_user_model


User = get_user_model()


class Command(BaseCommand):
    help = 'Migrate and populate RBAC system from navbar structure'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-features',
            action='store_true',
            help='Create features from navbar menu structure',
        )
        parser.add_argument(
            '--create-roles',
            action='store_true',
            help='Create initial roles',
        )
        parser.add_argument(
            '--assign-users',
            action='store_true',
            help='Assign existing users to roles',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all migration steps',
        )

    def handle(self, *args, **options):
        if options['all']:
            options['create_features'] = True
            options['create_roles'] = True
            options['assign_users'] = True

        if not any([options['create_features'], options['create_roles'], options['assign_users']]):
            raise CommandError(
                'You must specify at least one action: '
                '--create-features, --create-roles, --assign-users, or --all'
            )

        if options['create_features']:
            self.create_features()

        if options['create_roles']:
            self.create_roles()

        if options['assign_users']:
            self.assign_users()

        self.stdout.write(
            self.style.SUCCESS('RBAC migration completed successfully!')
        )

    @transaction.atomic
    def create_features(self):
        """Create features from navbar menu structure."""
        from common.rbac_models import Feature, Permission

        self.stdout.write('Creating features from navbar structure...')

        # Navbar structure based on NAVBAR_RBAC_ANALYSIS.md
        navbar_structure = [
            # Dashboard
            {
                'feature_key': 'dashboard',
                'name': 'Dashboard',
                'module': 'common',
                'category': 'navigation',
                'icon': 'fa-mosque',
                'url_pattern': '/dashboard/',
                'sort_order': 1,
            },

            # OBC Data (parent)
            {
                'feature_key': 'obc_data',
                'name': 'OBC Data',
                'module': 'communities',
                'category': 'navigation',
                'icon': 'fa-users',
                'url_pattern': '/communities/',
                'sort_order': 2,
            },
            {
                'feature_key': 'communities.barangay_obc',
                'name': 'Barangay OBCs',
                'module': 'communities',
                'category': 'data_management',
                'icon': 'fa-map-marker-alt',
                'url_pattern': '/communities/manage/',
                'sort_order': 1,
                'parent_key': 'obc_data',
            },
            {
                'feature_key': 'communities.municipal_obc',
                'name': 'Municipal OBCs',
                'module': 'communities',
                'category': 'data_management',
                'icon': 'fa-city',
                'url_pattern': '/communities/manage-municipal/',
                'sort_order': 2,
                'parent_key': 'obc_data',
            },
            {
                'feature_key': 'communities.provincial_obc',
                'name': 'Provincial OBCs',
                'module': 'communities',
                'category': 'data_management',
                'icon': 'fa-flag',
                'url_pattern': '/communities/manage-provincial/',
                'sort_order': 3,
                'parent_key': 'obc_data',
            },
            {
                'feature_key': 'mana.geographic_data',
                'name': 'Geographic Data',
                'module': 'mana',
                'category': 'data_management',
                'icon': 'fa-map',
                'url_pattern': '/mana/geographic-data/',
                'sort_order': 4,
                'parent_key': 'obc_data',
            },

            # MANA (parent)
            {
                'feature_key': 'mana',
                'name': 'MANA',
                'module': 'mana',
                'category': 'navigation',
                'icon': 'fa-map-marked-alt',
                'url_pattern': '/mana/',
                'sort_order': 3,
            },
            {
                'feature_key': 'mana.regional_overview',
                'name': 'Regional MANA',
                'module': 'mana',
                'category': 'assessment',
                'icon': 'fa-globe-asia',
                'url_pattern': '/mana/regional/',
                'sort_order': 1,
                'parent_key': 'mana',
            },
            {
                'feature_key': 'mana.provincial_overview',
                'name': 'Provincial MANA',
                'module': 'mana',
                'category': 'assessment',
                'icon': 'fa-map',
                'url_pattern': '/mana/provincial/',
                'sort_order': 2,
                'parent_key': 'mana',
            },
            {
                'feature_key': 'mana.desk_review',
                'name': 'Desk Review',
                'module': 'mana',
                'category': 'assessment',
                'icon': 'fa-book-open',
                'url_pattern': '/mana/desk-review/',
                'sort_order': 3,
                'parent_key': 'mana',
            },
            {
                'feature_key': 'mana.survey',
                'name': 'Survey',
                'module': 'mana',
                'category': 'assessment',
                'icon': 'fa-clipboard-list',
                'url_pattern': '/mana/survey/',
                'sort_order': 4,
                'parent_key': 'mana',
            },
            {
                'feature_key': 'mana.kii',
                'name': 'Key Informant Interview',
                'module': 'mana',
                'category': 'assessment',
                'icon': 'fa-comments',
                'url_pattern': '/mana/kii/',
                'sort_order': 5,
                'parent_key': 'mana',
            },

            # Coordination
            {
                'feature_key': 'coordination',
                'name': 'Coordination',
                'module': 'coordination',
                'category': 'navigation',
                'icon': 'fa-handshake',
                'url_pattern': '/coordination/',
                'sort_order': 4,
            },
            {
                'feature_key': 'coordination.mapped_partners',
                'name': 'Mapped Partners',
                'module': 'coordination',
                'category': 'partnership',
                'icon': 'fa-users-cog',
                'url_pattern': '/coordination/organizations/',
                'sort_order': 1,
                'parent_key': 'coordination',
            },
            {
                'feature_key': 'coordination.partnership_agreements',
                'name': 'Partnership Agreements',
                'module': 'coordination',
                'category': 'partnership',
                'icon': 'fa-file-contract',
                'url_pattern': '/coordination/partnerships/',
                'sort_order': 2,
                'parent_key': 'coordination',
            },
            {
                'feature_key': 'coordination.activities',
                'name': 'Coordination Activities',
                'module': 'coordination',
                'category': 'partnership',
                'icon': 'fa-calendar-check',
                'url_pattern': '/coordination/events/',
                'sort_order': 3,
                'parent_key': 'coordination',
            },

            # Recommendations
            {
                'feature_key': 'policies',
                'name': 'Recommendations',
                'module': 'policies',
                'category': 'navigation',
                'icon': 'fa-gavel',
                'url_pattern': '/recommendations/',
                'sort_order': 5,
            },
            {
                'feature_key': 'policies.policies',
                'name': 'Policies',
                'module': 'policies',
                'category': 'policy',
                'icon': 'fa-balance-scale',
                'url_pattern': '/recommendations/manage/',
                'sort_order': 1,
                'parent_key': 'policies',
            },
            {
                'feature_key': 'policies.programs',
                'name': 'Systematic Programs',
                'module': 'policies',
                'category': 'policy',
                'icon': 'fa-project-diagram',
                'url_pattern': '/recommendations/programs/',
                'sort_order': 2,
                'parent_key': 'policies',
            },
            {
                'feature_key': 'policies.services',
                'name': 'Services',
                'module': 'policies',
                'category': 'policy',
                'icon': 'fa-concierge-bell',
                'url_pattern': '/recommendations/services/',
                'sort_order': 3,
                'parent_key': 'policies',
            },

            # M&E
            {
                'feature_key': 'monitoring',
                'name': 'M&E',
                'module': 'monitoring',
                'category': 'navigation',
                'icon': 'fa-chart-pie',
                'url_pattern': '/monitoring/',
                'sort_order': 6,
            },
            {
                'feature_key': 'monitoring.moa_ppas',
                'name': 'MOA PPAs',
                'module': 'monitoring',
                'category': 'monitoring',
                'icon': 'fa-file-contract',
                'url_pattern': '/monitoring/moa-ppas/',
                'sort_order': 1,
                'parent_key': 'monitoring',
            },
            {
                'feature_key': 'monitoring.oobc_initiatives',
                'name': 'OOBC Initiatives',
                'module': 'monitoring',
                'category': 'monitoring',
                'icon': 'fa-hand-holding-heart',
                'url_pattern': '/monitoring/oobc-initiatives/',
                'sort_order': 2,
                'parent_key': 'monitoring',
            },
            {
                'feature_key': 'monitoring.obc_requests',
                'name': 'OBC Requests',
                'module': 'monitoring',
                'category': 'monitoring',
                'icon': 'fa-file-signature',
                'url_pattern': '/monitoring/obc-requests/',
                'sort_order': 3,
                'parent_key': 'monitoring',
            },
            {
                'feature_key': 'monitoring.me_analytics',
                'name': 'M&E Analytics',
                'module': 'monitoring',
                'category': 'monitoring',
                'icon': 'fa-chart-bar',
                'url_pattern': '/monitoring/analytics/',
                'sort_order': 4,
                'parent_key': 'monitoring',
            },

            # OOBC Management
            {
                'feature_key': 'oobc_management',
                'name': 'OOBC Management',
                'module': 'common',
                'category': 'navigation',
                'icon': 'fa-toolbox',
                'url_pattern': '/oobc-management/',
                'sort_order': 7,
            },
            {
                'feature_key': 'oobc_management.staff_management',
                'name': 'Staff Management',
                'module': 'common',
                'category': 'management',
                'icon': 'fa-user-cog',
                'url_pattern': '/common/staff-management/',
                'sort_order': 1,
                'parent_key': 'oobc_management',
            },
            {
                'feature_key': 'oobc_management.work_items',
                'name': 'Work Items',
                'module': 'common',
                'category': 'management',
                'icon': 'fa-tasks',
                'url_pattern': '/common/work-items/',
                'sort_order': 2,
                'parent_key': 'oobc_management',
            },
            {
                'feature_key': 'oobc_management.planning_budgeting',
                'name': 'Planning & Budgeting',
                'module': 'planning',
                'category': 'management',
                'icon': 'fa-file-signature',
                'url_pattern': '/planning/budgeting/',
                'sort_order': 3,
                'parent_key': 'oobc_management',
            },
            {
                'feature_key': 'oobc_management.calendar',
                'name': 'Calendar Management',
                'module': 'common',
                'category': 'management',
                'icon': 'fa-calendar-week',
                'url_pattern': '/common/calendar/',
                'sort_order': 4,
                'parent_key': 'oobc_management',
            },
            {
                'feature_key': 'oobc_management.project_management',
                'name': 'Project Management Portal',
                'module': 'project_central',
                'category': 'management',
                'icon': 'fa-project-diagram',
                'url_pattern': '/project-central/dashboard/',
                'sort_order': 5,
                'parent_key': 'oobc_management',
            },
            {
                'feature_key': 'oobc_management.user_approvals',
                'name': 'User Approvals',
                'module': 'common',
                'category': 'management',
                'icon': 'fa-user-check',
                'url_pattern': '/common/user-approvals/',
                'sort_order': 6,
                'parent_key': 'oobc_management',
            },
        ]

        # Create features with parent-child relationships
        feature_map = {}
        created_count = 0

        # First pass: Create all features without parent relationships
        for feature_data in navbar_structure:
            parent_key = feature_data.pop('parent_key', None)

            feature, created = Feature.objects.get_or_create(
                feature_key=feature_data['feature_key'],
                defaults=feature_data
            )

            feature_map[feature_data['feature_key']] = feature

            if created:
                created_count += 1
                self.stdout.write(f"  Created feature: {feature.name}")

                # Create standard permissions for this feature
                self.create_permissions_for_feature(feature)

        # Second pass: Set parent relationships
        for feature_data in navbar_structure:
            parent_key = feature_data.get('parent_key')
            if parent_key and parent_key in feature_map:
                feature = feature_map[feature_data['feature_key']]
                feature.parent = feature_map[parent_key]
                feature.save(update_fields=['parent'])

        self.stdout.write(
            self.style.SUCCESS(f'Created {created_count} features')
        )

    def create_permissions_for_feature(self, feature):
        """Create standard permissions for a feature."""
        from common.rbac_models import Permission

        # Standard permission types
        permission_types = [
            ('view', 'View/Read', 'Can view and access'),
            ('create', 'Create/Add', 'Can create new'),
            ('edit', 'Edit/Update', 'Can edit existing'),
            ('delete', 'Delete/Remove', 'Can delete'),
            ('export', 'Export Data', 'Can export data'),
        ]

        for codename, name, description in permission_types:
            Permission.objects.get_or_create(
                feature=feature,
                codename=codename,
                defaults={
                    'name': f"{name} {feature.name}",
                    'description': f"{description} {feature.name.lower()}",
                    'permission_type': codename if codename in ['view', 'create', 'edit', 'delete', 'export'] else 'custom',
                }
            )

    @transaction.atomic
    def create_roles(self):
        """Create initial roles."""
        from common.rbac_models import Role

        self.stdout.write('Creating initial roles...')

        # Standard BMMS roles
        roles = [
            # OOBC Roles
            {
                'name': 'OOBC Admin',
                'slug': 'oobc-admin',
                'description': 'Full system administrator with all permissions',
                'scope': 'system',
                'level': 5,
                'is_system_role': True,
            },
            {
                'name': 'OOBC Manager',
                'slug': 'oobc-manager',
                'description': 'Management-level access to all OOBC operations',
                'scope': 'system',
                'level': 4,
                'is_system_role': True,
            },
            {
                'name': 'OOBC Staff',
                'slug': 'oobc-staff',
                'description': 'Standard staff access to OOBC operations',
                'scope': 'system',
                'level': 3,
                'is_system_role': True,
            },
            {
                'name': 'OOBC Viewer',
                'slug': 'oobc-viewer',
                'description': 'Read-only access to OOBC data',
                'scope': 'system',
                'level': 2,
                'is_system_role': True,
            },

            # MOA Roles (organization-specific)
            {
                'name': 'MOA Admin',
                'slug': 'moa-admin',
                'description': 'Ministry/Agency administrator',
                'scope': 'organization',
                'level': 4,
                'is_system_role': True,
            },
            {
                'name': 'MOA Manager',
                'slug': 'moa-manager',
                'description': 'Ministry/Agency manager',
                'scope': 'organization',
                'level': 3,
                'is_system_role': True,
            },
            {
                'name': 'MOA Staff',
                'slug': 'moa-staff',
                'description': 'Ministry/Agency staff member',
                'scope': 'organization',
                'level': 2,
                'is_system_role': True,
            },
            {
                'name': 'MOA Viewer',
                'slug': 'moa-viewer',
                'description': 'Ministry/Agency read-only access',
                'scope': 'organization',
                'level': 1,
                'is_system_role': True,
            },

            # OCM Roles
            {
                'name': 'OCM Analyst',
                'slug': 'ocm-analyst',
                'description': 'Office of Chief Minister analyst (read-only aggregated access)',
                'scope': 'system',
                'level': 2,
                'is_system_role': True,
            },
        ]

        created_count = 0
        for role_data in roles:
            role, created = Role.objects.get_or_create(
                slug=role_data['slug'],
                organization=None,  # System roles have no organization
                defaults=role_data
            )
            if created:
                created_count += 1
                self.stdout.write(f"  Created role: {role.name}")

        self.stdout.write(
            self.style.SUCCESS(f'Created {created_count} roles')
        )

    @transaction.atomic
    def assign_users(self):
        """Assign existing users to roles based on their user_type."""
        from common.rbac_models import Role, UserRole

        self.stdout.write('Assigning existing users to roles...')

        # Mapping of user_type to role slug
        user_type_to_role = {
            'admin': 'oobc-admin',
            'oobc_executive': 'oobc-admin',
            'oobc_staff': 'oobc-staff',
            'cm_office': 'ocm-analyst',
            'bmoa': 'moa-staff',
            'lgu': 'moa-staff',
            'nga': 'moa-staff',
        }

        assigned_count = 0

        for user in User.objects.filter(is_active=True):
            role_slug = user_type_to_role.get(user.user_type)
            if not role_slug:
                continue

            role = Role.objects.filter(slug=role_slug, organization__isnull=True).first()
            if not role:
                self.stdout.write(
                    self.style.WARNING(f"Role not found: {role_slug}")
                )
                continue

            # Determine organization context
            organization = None
            if user.is_moa_staff and user.moa_organization:
                organization = user.moa_organization

            # Create user role assignment
            user_role, created = UserRole.objects.get_or_create(
                user=user,
                role=role,
                organization=organization,
                defaults={
                    'is_active': True,
                }
            )

            if created:
                assigned_count += 1
                org_name = organization.name if organization else "Global"
                self.stdout.write(
                    f"  Assigned {user.get_full_name()} to {role.name} ({org_name})"
                )

        self.stdout.write(
            self.style.SUCCESS(f'Assigned {assigned_count} users to roles')
        )
