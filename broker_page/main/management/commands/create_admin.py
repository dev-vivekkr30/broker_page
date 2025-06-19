from django.core.management.base import BaseCommand
from main.models import Broker
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'Create a superuser for admin access'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, default='admin@broker.page', help='Admin email')
        parser.add_argument('--password', type=str, default='admin123', help='Admin password')
        parser.add_argument('--full-name', type=str, default='Admin User', help='Admin full name')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        full_name = options['full_name']

        # Check if user already exists
        if Broker.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'User with email "{email}" already exists. Skipping creation.')
            )
            return

        # Create the user
        user = Broker.objects.create(
            email=email,
            password=make_password(password),
            full_name=full_name,
            company='Admin Company',
            mobile='1234567890',
            residence_colony='Admin Colony',
            office_address='Admin Office Address',
            is_staff=True,
            is_superuser=True,
            is_active=True
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created admin user:\n'
                f'Email: {email}\n'
                f'Password: {password}\n'
                f'Full Name: {full_name}'
            )
        ) 