"""
Management command to seed or re-seed BARMM organizations.

This command is idempotent - it can be run multiple times safely.
It will create missing organizations and update existing ones.

Usage:
    python manage.py seed_organizations
    python manage.py seed_organizations --force  # Delete all and re-create
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from organizations.models import Organization


class Command(BaseCommand):
    help = 'Seed all 44 BARMM Ministries, Offices, and Agencies (MOAs)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Delete all existing organizations and re-seed (DANGEROUS!)',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)

        if force:
            self.stdout.write(self.style.WARNING(
                '\n⚠️  WARNING: --force flag will DELETE ALL existing organizations!'
            ))
            confirm = input('Type "yes" to confirm: ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('Operation cancelled.'))
                return

            with transaction.atomic():
                count = Organization.objects.count()
                Organization.objects.all().delete()
                self.stdout.write(self.style.WARNING(f'Deleted {count} organizations'))

        self.stdout.write(self.style.MIGRATE_HEADING('\nSeeding BARMM Organizations...'))

        # Track statistics
        created = 0
        updated = 0
        skipped = 0

        with transaction.atomic():
            # CRITICAL: Create OOBC first (will get ID=1)
            oobc, was_created = self._create_or_update_org(
                code='OOBC',
                name='Office for Other Bangsamoro Communities',
                org_type='office',
                is_pilot=False,
            )
            if was_created:
                created += 1
            else:
                updated += 1

            # MINISTRIES (16)
            ministries = [
                ('MAFAR', 'Ministry of Agriculture, Fisheries and Agrarian Reform', True),
                ('MBHTE', 'Ministry of Basic, Higher and Technical Education', False),
                ('MENRE', 'Ministry of Environment, Natural Resources and Energy', False),
                ('MFBM', 'Ministry of Finance, Budget and Management', False),
                ('MOH', 'Ministry of Health', True),
                ('MHSD', 'Ministry of Human Settlements and Development', False),
                ('MIPA', 'Ministry of Indigenous Peoples Affairs', False),
                ('MILG', 'Ministry of Interior and Local Government', False),
                ('MOLE', 'Ministry of Labor and Employment', True),
                ('MPWH', 'Ministry of Public Works and Highways', False),
                ('MSSD', 'Ministry of Social Services and Development', False),
                ('MTI', 'Ministry of Trade, Investments and Tourism', False),
                ('MTIT', 'Ministry of Transportation and Information Technology', False),
                ('MWDWA', 'Ministry of Women, Development and Welfare Affairs', False),
                ('MYNDA', 'Ministry of Youth and Nonprofit Development Affairs', False),
                ('MPOS', 'Ministry of Public Order and Safety', False),
            ]

            for code, name, is_pilot in ministries:
                org, was_created = self._create_or_update_org(
                    code=code,
                    name=name,
                    org_type='ministry',
                    is_pilot=is_pilot,
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

            # OFFICES (10, including OOBC which is already created)
            offices = [
                ('OCM', 'Office of the Chief Minister'),
                ('OMP', 'Office of the Majority Floor Leader (Parliament)'),
                ('OPARL', 'Office of the Bangsamoro Parliament'),
                ('OPMDA', 'Office of the Prime Minister on Disasters and Assistance'),
                ('OSM', 'Office of the Senior Minister'),
                ('OTAF', 'Office of Technical Assistance and Facilitation'),
                ('OADP', 'Office for Ancestral Domain Programs'),
                ('OBCE', 'Office of Business and Community Empowerment'),
                ('OCRE', 'Office of Cultural and Religious Endowments'),
                ('OMLA', 'Office of Muslim Legal Affairs'),
            ]

            for code, name in offices:
                org, was_created = self._create_or_update_org(
                    code=code,
                    name=name,
                    org_type='office',
                    is_pilot=False,
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

            # AGENCIES (8)
            agencies = [
                ('BAI', 'Bangsamoro Audit Institution'),
                ('BEDC', 'Bangsamoro Economic Development Council'),
                ('BTA', 'Bangsamoro Transition Authority'),
                ('BSWM', 'Bangsamoro Statistics and Water Management'),
                ('CAB', 'Commission on Appointments (Bangsamoro)'),
                ('CSC-BARMM', 'Civil Service Commission'),
                ('RLEA', 'Regional Law Enforcement Agency'),
                ('TESDA-BARMM', 'Technical Education and Skills Development Authority'),
            ]

            for code, name in agencies:
                org, was_created = self._create_or_update_org(
                    code=code,
                    name=name,
                    org_type='agency',
                    is_pilot=False,
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

            # SPECIAL BODIES (7)
            special_bodies = [
                ('BIDA', 'Bangsamoro Investment and Development Authority'),
                ('BIAF', 'Bangsamoro Islamic Affairs'),
                ('BRTA', 'Bangsamoro Radio and Television Authority'),
                ('BSBC', 'Bangsamoro Sustainable Blue Carbon'),
                ('BWPB', 'Bangsamoro Water and Power Board'),
                ('MUWASSCO', 'Mindanao Utilities Water and Sanitation Service Company'),
                ('SPBI', 'Special Program for Bangsamoro Innovation'),
            ]

            for code, name in special_bodies:
                org, was_created = self._create_or_update_org(
                    code=code,
                    name=name,
                    org_type='special',
                    is_pilot=False,
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

            # COMMISSIONS (3)
            commissions = [
                ('BCHRC', 'Bangsamoro Commission on Human Rights'),
                ('BWCRC', 'Bangsamoro Women\'s Commission on Rights and Concerns'),
                ('BYDC', 'Bangsamoro Youth Development Commission'),
            ]

            for code, name in commissions:
                org, was_created = self._create_or_update_org(
                    code=code,
                    name=name,
                    org_type='commission',
                    is_pilot=False,
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

        # Display results
        total = Organization.objects.count()
        pilot_count = Organization.objects.filter(is_pilot=True).count()

        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('✅ BARMM MOA Seeding Complete!'))
        self.stdout.write('='*70)
        self.stdout.write(f'Total Organizations: {total} (expected: 44)')
        self.stdout.write(f'Created: {created}')
        self.stdout.write(f'Updated: {updated}')
        self.stdout.write(f'Pilot MOAs: {pilot_count} (expected: 3)')

        # Verify OOBC is ID=1
        try:
            oobc = Organization.objects.get(code='OOBC')
            if oobc.id == 1:
                self.stdout.write(self.style.SUCCESS(
                    f'\n✅ OOBC Organization ID: {oobc.id} (correct - must be 1)'
                ))
            else:
                self.stdout.write(self.style.ERROR(
                    f'\n❌ ERROR: OOBC has ID={oobc.id}, expected ID=1!'
                ))
        except Organization.DoesNotExist:
            self.stdout.write(self.style.ERROR('\n❌ ERROR: OOBC organization not found!'))

        # List pilot MOAs
        pilot_moas = Organization.objects.filter(is_pilot=True).values_list('code', 'name')
        if pilot_moas:
            self.stdout.write('\nPilot MOAs:')
            for code, name in pilot_moas:
                self.stdout.write(f'  • {code}: {name}')

        self.stdout.write('='*70 + '\n')

    def _create_or_update_org(self, code, name, org_type, is_pilot):
        """
        Create or update an organization.

        Returns:
            tuple: (organization, was_created)
        """
        org, created = Organization.objects.update_or_create(
            code=code,
            defaults={
                'name': name,
                'org_type': org_type,
                'is_pilot': is_pilot,
                'is_active': True,
            }
        )

        status = 'Created' if created else 'Updated'
        pilot_flag = ' [PILOT]' if is_pilot else ''
        self.stdout.write(
            self.style.SUCCESS(f'  {status}: {code} - {name}{pilot_flag}')
        )

        return org, created
