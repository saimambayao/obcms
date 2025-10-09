"""
Management command to generate focal person users for all MOA organizations.

Usage:
    python manage.py generate_moa_focal_users                   # Create users
    python manage.py generate_moa_focal_users --dry-run         # Preview only
    python manage.py generate_moa_focal_users --overwrite       # Reset existing users
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from coordination.models import Organization

User = get_user_model()


class Command(BaseCommand):
    """Generate focal person users for all MOA organizations."""

    help = 'Generate focal person users for all MOA organizations with standard credentials'

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating users',
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing focal users (reset passwords)',
        )

    def handle(self, *args, **options):
        """Execute the command."""
        dry_run = options['dry_run']
        overwrite = options['overwrite']
        
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.HTTP_INFO("MOA Focal User Generation"))
        self.stdout.write("=" * 80)
        
        if dry_run:
            self.stdout.write(self.style.WARNING("\n[DRY RUN MODE] - No changes will be made\n"))
        
        # Get all BMOA organizations with acronyms
        moa_orgs = Organization.objects.filter(
            organization_type='bmoa',
            acronym__isnull=False
        ).exclude(acronym='')
        
        if not moa_orgs.exists():
            self.stdout.write(
                self.style.ERROR("No BMOA organizations with acronyms found!")
            )
            return
        
        self.stdout.write(f"Found {moa_orgs.count()} BMOA organizations with acronyms\n")
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for org in moa_orgs:
            acronym = org.acronym.strip()
            if not acronym:
                continue
            
            username = f"focal.{acronym}"
            password = f"{acronym}.focal123"
            
            # Check if user exists
            existing_user = User.objects.filter(username=username).first()
            
            if existing_user and not overwrite:
                self.stdout.write(
                    self.style.WARNING(
                        f"  [SKIP] User '{username}' already exists (use --overwrite to reset)"
                    )
                )
                skipped_count += 1
                continue
            
            if dry_run:
                action = "UPDATE" if existing_user else "CREATE"
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  [{action}] {username} | Password: {password} | Org: {org.name}"
                    )
                )
                if existing_user:
                    updated_count += 1
                else:
                    created_count += 1
                continue
            
            # Create or update user
            if existing_user:
                # Update existing user
                existing_user.set_password(password)
                existing_user.organization = org.name
                existing_user.user_type = 'bmoa'
                existing_user.is_approved = True
                existing_user.is_active = True
                existing_user.position = 'Focal Person'
                existing_user.first_name = acronym
                existing_user.last_name = 'Focal Person'
                existing_user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  [UPDATED] {username} | Password: {password} | Org: {org.name}"
                    )
                )
                updated_count += 1
            else:
                # Create new user
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    user_type='bmoa',
                    organization=org.name,
                    position='Focal Person',
                    is_approved=True,
                    is_active=True,
                    first_name=acronym,
                    last_name='Focal Person',
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  [CREATED] {username} | Password: {password} | Org: {org.name}"
                    )
                )
                created_count += 1
        
        # Summary
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.HTTP_INFO("Summary:"))
        self.stdout.write("=" * 80)
        self.stdout.write(f"  Created:  {self.style.SUCCESS(str(created_count))}")
        self.stdout.write(f"  Updated:  {self.style.SUCCESS(str(updated_count))}")
        self.stdout.write(f"  Skipped:  {self.style.WARNING(str(skipped_count))}")
        self.stdout.write(f"  Total:    {moa_orgs.count()} BMOA organizations processed")
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\n[DRY RUN MODE] - No users were actually created or updated"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nSuccessfully processed {created_count + updated_count} focal users!"
                )
            )
        
        self.stdout.write("=" * 80)
