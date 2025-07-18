from django.core.management.base import BaseCommand
from main.models import Broker, Invoice
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Create a test invoice for a broker user by email.'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email of the broker user')
        parser.add_argument('--amount', type=float, default=1000, help='Invoice amount (default: 1000)')

    def handle(self, *args, **options):
        email = options['email']
        amount = options['amount']
        try:
            broker = Broker.objects.get(email=email)
        except Broker.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'No broker found with email: {email}'))
            return

        start_date = broker.date_joined.date() if broker.date_joined else timezone.now().date()
        end_date = start_date + timedelta(days=365)
        invoice_number = f"INV-{broker.id}-{start_date.strftime('%Y%m%d')}"

        invoice, created = Invoice.objects.get_or_create(
            broker=broker,
            start_date=start_date,
            end_date=end_date,
            defaults={
                'amount': amount,
                'invoice_number': invoice_number,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Test invoice created for {email}: {invoice_number}'))
        else:
            self.stdout.write(self.style.WARNING(f'Invoice already exists for {email} for this period.')) 