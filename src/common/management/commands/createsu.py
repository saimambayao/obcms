"""
Custom management command to create a superuser non-interactively.
Usage: python manage.py createsu --username=<username> --email=<email> --password=<password>
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create a superuser non-interactively'

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True, help='Superuser username')
        parser.add_argument('--email', required=True, help='Superuser email')
        parser.add_argument('--password', required=True, help='Superuser password')

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        email = options['email']
        password = options['password']

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'User "{username}" already exists!')
            )
            return

        # Create the superuser
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Superuser "{username}" ({email}) created successfully!'
            )
        )
